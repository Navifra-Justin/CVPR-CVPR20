"""E56 shared evaluator.

The mAP-vs-displacement evaluator of E52, unchanged in semantics, factored out so that
E56's wide sweep, its cluster bootstrap and its self-test all score with one function.
`src/e52_selftest.py` pins four values this must reproduce; `src/e56_selftest.py` re-runs
that pin against this copy before any E56 number is used.
"""
import numpy as np, os, glob

THRS = np.arange(0.5, 0.96, 0.05)


def load_dump(path):
    Z = np.load(path)
    return Z['det'].astype(np.float64), Z['gt'].astype(np.float64)


def iou_mat(D, G):
    if len(D) == 0 or len(G) == 0:
        return np.zeros((len(D), len(G)))
    x1 = np.maximum(D[:, None, 0], G[None, :, 0]); y1 = np.maximum(D[:, None, 1], G[None, :, 1])
    x2 = np.minimum(D[:, None, 2], G[None, :, 2]); y2 = np.minimum(D[:, None, 3], G[None, :, 3])
    w = np.clip(x2 - x1, 0, None); h = np.clip(y2 - y1, 0, None); it = w * h
    ad = ((D[:, 2] - D[:, 0]) * (D[:, 3] - D[:, 1]))[:, None]
    ag = ((G[:, 2] - G[:, 0]) * (G[:, 3] - G[:, 1]))[None, :]
    return it / np.maximum(ad + ag - it, 1e-9)


class Scorer:
    """Holds one model's detections and the shared ground truth, pre-bucketed by frame."""

    def __init__(self, det, gt):
        self.GT = gt
        self.NF = int(gt[:, 0].max()) + 1
        self.CLASSES = sorted(set(gt[:, 5].astype(int)))
        hasv = np.isfinite(gt[:, 6]) & np.isfinite(gt[:, 7])
        spd = np.hypot(np.nan_to_num(gt[:, 6]), np.nan_to_num(gt[:, 7]))
        self.gt_by = [[] for _ in range(self.NF)]
        for i, r in enumerate(gt):
            self.gt_by[int(r[0])].append((r, hasv[i], spd[i]))
        self.det_by = [[] for _ in range(self.NF)]
        for r in det:
            self.det_by[int(r[0])].append(r)

    def evaluate(self, delta, lo=None, hi=None, frames=None, per_class=False,
                 require_velocity=True):
        """mAP over ground truth with a centered velocity; boxes outside [lo,hi) are ignored.

        `frames` restricts the evaluation to a subset of frame indices, which is what the
        cluster bootstrap resamples over. Frames may repeat; each copy is scored once.

        `require_velocity=False` scores every labelled box instead of only the velocity-
        evaluable ones, which is the population the released Gen1 number is computed over.
        It is only meaningful at delta = 0, since a box without a velocity cannot be
        displaced; the default is the paper's moving-object subset and the four pinned
        values in `e56_selftest.py` are values of that default.
        """
        idx = range(self.NF) if frames is None else frames
        out = {}
        for c in self.CLASSES:
            scores = []; tp = {t: [] for t in THRS}; npos = 0
            for fi in idx:
                G = []; ign = []
                for r, hv, sp in self.gt_by[fi]:
                    if int(r[5]) != c:
                        continue
                    b = r[1:5].copy()
                    keep = (hv or not require_velocity) and \
                        (lo is None or (hv and sp >= lo and sp < hi))
                    if hv:
                        b[0] += delta * r[6]; b[2] += delta * r[6]
                        b[1] += delta * r[7]; b[3] += delta * r[7]
                    G.append(b); ign.append(not keep)
                D = [r for r in self.det_by[fi] if int(r[6]) == c]
                G = np.array(G).reshape(-1, 4); ign = np.array(ign, dtype=bool)
                npos += int((~ign).sum())
                if not len(D):
                    continue
                D = np.array(D); D = D[np.argsort(-D[:, 5])]
                IM = iou_mat(D[:, 1:5], G); scores.append(D[:, 5])
                for t in THRS:
                    used = np.zeros(len(G), dtype=bool); flag = np.zeros(len(D))
                    for di in range(len(D)):
                        r = IM[di]
                        cand = (~used) & (r >= t)
                        if not cand.any():
                            continue
                        j = int(np.flatnonzero(cand)[np.argmax(r[cand])])
                        used[j] = True; flag[di] = -1.0 if ign[j] else 1.0
                    tp[t].append(flag)
            if not scores:
                continue
            S = np.concatenate(scores); o = np.argsort(-S); aps = []
            for t in THRS:
                f = np.concatenate(tp[t])[o]; f = f[f >= 0]
                ctp = np.cumsum(f == 1); cfp = np.cumsum(f == 0)
                rec = ctp / max(npos, 1); prec = ctp / np.maximum(ctp + cfp, 1e-9)
                mp = np.concatenate([[0], prec, [0]]); mr = np.concatenate([[0], rec, [1]])
                for i in range(len(mp) - 2, -1, -1):
                    mp[i] = max(mp[i], mp[i + 1])
                k = np.where(mr[1:] != mr[:-1])[0]
                aps.append(float(((mr[k + 1] - mr[k]) * mp[k + 1]).sum()))
            out[c] = float(np.mean(aps))
        if per_class:
            return out
        return float(np.mean(list(out.values()))) if out else 0.0


def model_paths(root='experiments/e51_ranking'):
    order = {'rvt-t': 0, 'rvt-s': 1, 'rvt-b': 2, 's5vit-small': 3, 's5vit-base': 4}
    fs = sorted(glob.glob(os.path.join(root, 'dets-*.npz')))
    named = [(os.path.basename(f)[5:-4], f) for f in fs]
    named.sort(key=lambda r: order.get(r[0], 9))
    return named
