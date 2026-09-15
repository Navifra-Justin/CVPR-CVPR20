"""E55 - the fast-motion consequence table, at the corrected centroid.

E37c stratified the ground-truth displacement sweep by object speed and reported each
stratum's cost at -24.94 ms, the centroid E45 later corrected to -23.81 ms, and read that
cost off the 5 ms sweep grid. This run evaluates each stratum exactly at delta = -23.81 ms
with the same evaluator, and adds what the table needs to say why the pooled curve is
flat: each stratum's share of the moving boxes, its median speed, and what 23.81 ms of
that speed is in pixels. The sweep span per stratum is copied from strata.json, whose
grid did not change.

Cross-checks: the "all moving" row must reproduce at_centroid.json's moving numbers
(mAP 0.33458 at zero, 0.33419 at -23.81), and each stratum's mAP(0) must reproduce
strata.json's map_zero.
"""
import numpy as np, json

CENTROID_S = -0.02381                       # E45's corrected centroid, in seconds

Z = np.load('experiments/e37_map/dets.npz')
DET = Z['det'].astype(np.float64); GT = Z['gt'].astype(np.float64)
hasv = np.isfinite(GT[:, 6]) & np.isfinite(GT[:, 7])
SPD = np.hypot(GT[:, 6], GT[:, 7])
NF = int(max(DET[:, 0].max(), GT[:, 0].max())) + 1
det_by = [[] for _ in range(NF)]
for r in DET: det_by[int(r[0])].append(r)
gt_by = [[] for _ in range(NF)]
for i, r in enumerate(GT): gt_by[int(r[0])].append((r, bool(hasv[i]), float(SPD[i])))
CLASSES = sorted(set(GT[:, 5].astype(int)))
THRS = np.arange(0.5, 0.96, 0.05)

def iou_mat(D, G):
    if len(D) == 0 or len(G) == 0: return np.zeros((len(D), len(G)))
    x1 = np.maximum(D[:, None, 0], G[None, :, 0]); y1 = np.maximum(D[:, None, 1], G[None, :, 1])
    x2 = np.minimum(D[:, None, 2], G[None, :, 2]); y2 = np.minimum(D[:, None, 3], G[None, :, 3])
    w = np.clip(x2 - x1, 0, None); h = np.clip(y2 - y1, 0, None); it = w * h
    ad = ((D[:, 2] - D[:, 0]) * (D[:, 3] - D[:, 1]))[:, None]
    ag = ((G[:, 2] - G[:, 0]) * (G[:, 3] - G[:, 1]))[None, :]
    return it / np.maximum(ad + ag - it, 1e-9)

def evaluate(delta, lo, hi):
    out = {}
    for c in CLASSES:
        scores = []; tp = {t: [] for t in THRS}; npos = 0
        for fi in range(NF):
            G = []; ign = []
            for r, hv, sp in gt_by[fi]:
                if int(r[5]) != c: continue
                b = r[1:5].copy()
                if hv:
                    b[0] += delta * r[6]; b[2] += delta * r[6]
                    b[1] += delta * r[7]; b[3] += delta * r[7]
                G.append(b); ign.append((not hv) or not (lo <= sp < hi))
            D = [r for r in det_by[fi] if int(r[6]) == c]
            G = np.array(G).reshape(-1, 4); ign = np.array(ign, dtype=bool)
            npos += int((~ign).sum())
            if not len(D): continue
            D = np.array(D); D = D[np.argsort(-D[:, 5])]
            M = iou_mat(D[:, 1:5], G); scores.append(D[:, 5])
            for t in THRS:
                used = np.zeros(len(G), dtype=bool); flag = np.zeros(len(D))
                for di in range(len(D)):
                    j = -1; best = t
                    for gj in range(len(G)):
                        if used[gj] or M[di, gj] < best: continue
                        best = M[di, gj]; j = gj
                    if j >= 0:
                        used[j] = True; flag[di] = -1.0 if ign[j] else 1.0
                tp[t].append(flag)
        if not scores or npos == 0: continue
        S = np.concatenate(scores); o = np.argsort(-S); aps = []
        for t in THRS:
            f = np.concatenate(tp[t])[o]; f = f[f >= 0]
            ctp = np.cumsum(f == 1); cfp = np.cumsum(f == 0)
            rec = ctp / npos; prec = ctp / np.maximum(ctp + cfp, 1e-9)
            mp = np.concatenate([[0], prec, [0]]); mr = np.concatenate([[0], rec, [1]])
            for i in range(len(mp) - 2, -1, -1): mp[i] = max(mp[i], mp[i + 1])
            idx = np.where(mr[1:] != mr[:-1])[0]
            aps.append(float(((mr[idx + 1] - mr[idx]) * mp[idx + 1]).sum()))
        out[c] = float(np.mean(aps))
    return float(np.mean(list(out.values()))) if out else float('nan')

SPANS = json.load(open('experiments/e37_map/strata.json'))
SPAN_KEY = {"all moving": "all moving", "slow, |v| < 10": "slow, |v| < 10",
            "10 <= |v| < 25": "10 <= |v| < 25", "25 <= |v| < 50": "25 <= |v| < 50",
            "fast, |v| >= 50": "fast, |v| >= 50"}
STRATA = [("all moving", 0.0, 1e9), ("slow, |v| < 10", 0.0, 10.0),
          ("10 <= |v| < 25", 10.0, 25.0), ("25 <= |v| < 50", 25.0, 50.0),
          ("fast, |v| >= 50", 50.0, 1e9)]

n_moving = int(hasv.sum())
rows = {}
for name, lo, hi in STRATA:
    sel = (SPD >= lo) & (SPD < hi) & hasv
    n = int(sel.sum())
    med_spd = float(np.median(SPD[sel]))
    disp_med = med_spd * abs(CENTROID_S)
    m0 = evaluate(0.0, lo, hi)
    mc = evaluate(CENTROID_S, lo, hi)
    prev0 = SPANS[SPAN_KEY[name]]['map_zero']
    assert abs(m0 - prev0) < 5e-5, (name, m0, prev0)   # same evaluator, same stratum
    rows[name] = dict(n=n, share_pct=float(100.0 * n / n_moving), speed_median=med_spd,
                      disp_px_median=float(disp_med), map_zero=m0, map_centroid=mc,
                      cost_points=float(100.0 * (m0 - mc)),
                      span_points=SPANS[SPAN_KEY[name]]['span_points'])
    print(f"{name:18s} n {n:6d} ({rows[name]['share_pct']:5.1f} %)  med |v| {med_spd:6.2f} px/s"
          f"  23.81 ms = {disp_med:5.3f} px  mAP(0) {m0:.4f}  mAP(-23.81) {mc:.4f}"
          f"  cost {rows[name]['cost_points']:.2f}  span {rows[name]['span_points']:.2f}", flush=True)

ac = json.load(open('experiments/e37_map/at_centroid.json'))['moving']
assert abs(rows['all moving']['map_zero'] - ac['zero']['map']) < 5e-5
assert abs(rows['all moving']['map_centroid'] - ac['centroid_new']['map']) < 5e-5
print("cross-check against at_centroid.json: agree")

json.dump(rows, open('experiments/e37_map/stratum_table.json', 'w'), indent=1)
print("WROTE experiments/e37_map/stratum_table.json")
