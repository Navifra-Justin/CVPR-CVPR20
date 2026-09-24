"""E60 - the paired chunk-position experiment.

E58 compared frames sitting at different positions in the release's streaming chunk and
controlled for scene content with RVT. That control rests on parallel trends: it assumes
the frames that happen to land early in a chunk would, absent the support difference,
have scored like the frames that land late, up to a model-independent offset.

This removes the assumption. The same SSM checkpoints are re-run with every chunk boundary
moved SHIFT windows LATER, so a frame the release gave position p now sits at (p - SHIFT)
mod 21. SHIFT = 5 is the value that carries the release's starved block, positions 0-3, onto
16-19: the frames the protocol gave one to four windows of history are scored again with
seventeen to twenty. The comparison is then within model and within frame: the identical
frame, the identical ground truth, the identical weights, differing only in how much
history the streaming protocol handed it. No control model is needed and no parallel-trends
assumption is made.

Two paired quantities are reported, each with the same 406-sequence cluster bootstrap that
E56 and E58 use:

  1. delta mAP, on the velocity-evaluable subset that E58's headline is computed over, and
     again over every labelled box;
  2. delta mean detection confidence, over every dumped detection on the paired frames and
     again over only those matched to a label at IoU 0.5, with detections per frame
     alongside so a confidence move cannot be read without its count.

Confidence is additive over frames, so its bootstrap is exact from per-frame sums rather
than re-derived per replicate; mAP is not, and is re-evaluated in each replicate.
"""
import json, os, sys, numpy as np
sys.path.insert(0, 'src')
from e56_eval import Scorer, iou_mat
from multiprocessing import Pool

SHIFT = 5
B = 300
NPROC = 8
IOU_TP = 0.5
OUT = 'experiments/e60_shift/paired.json'
BOUNDS = json.load(open('experiments/e56_resolving/seqmap.json'))
SHORT, FULL = (0, 4), (16, 21)


def frames_at(pos, lo, hi):
    return np.flatnonzero((pos >= lo) & (pos < hi))


def load(tag):
    """Released-protocol dump and the shifted dump, with the position each frame got."""
    a = np.load(f'experiments/e51_ranking/dets-s5vit-{tag}.npz')
    b = np.load(f'experiments/e60_shift/dets-s5vit-{tag}-shift{SHIFT}.npz')
    pa = np.load('experiments/e58_chunkpos/positions.npy')
    pb = b['pos']
    # equal_nan: the velocity columns are NaN for boxes with no finite-difference
    # neighbour, and NaN != NaN would make an identical label set compare unequal.
    assert np.array_equal(a['gt'], b['gt'], equal_nan=True), \
        f'{tag}: ground truth differs between dumps'
    assert len(pa) == len(pb), f'{tag}: frame count differs between dumps'
    return a, b, pa, pb


def perframe_conf(S):
    """Per-frame detection-confidence sums for one arm, from a Scorer's own buckets.

    Returns four arrays indexed by frame: the sum and the count of all dumped detection
    scores, and the sum and the count over detections matched to a label of the same class
    at IoU >= IOU_TP. Matching is greedy by descending score, one label per detection, which
    is the convention the evaluator uses. Sums are additive over frames, so the cluster
    bootstrap reads any frame subset off these arrays exactly.
    """
    n = S.NF
    s_sum = np.zeros(n); s_cnt = np.zeros(n)
    t_sum = np.zeros(n); t_cnt = np.zeros(n)
    for f in range(n):
        D = S.det_by[f]
        if not D:
            continue
        D = np.asarray(D, dtype=np.float64)
        s_sum[f] = D[:, 5].sum(); s_cnt[f] = len(D)
        G = S.gt_by[f]
        if not G:
            continue
        Garr = np.asarray([g[0] for g in G], dtype=np.float64)
        order = np.argsort(-D[:, 5])
        taken = np.zeros(len(Garr), dtype=bool)
        # iou_mat reads columns 0..3 as the box, so both sides are sliced to x1,y1,x2,y2.
        M = iou_mat(D[order][:, 1:5], Garr[:, 1:5])
        for k in range(len(order)):
            ok = (~taken) & (Garr[:, 5] == D[order[k], 6]) & (M[k] >= IOU_TP)
            if ok.any():
                j = int(np.flatnonzero(ok)[np.argmax(M[k][ok])])
                taken[j] = True
                t_sum[f] += D[order[k], 5]; t_cnt[f] += 1
    return s_sum, s_cnt, t_sum, t_cnt


def conf_of(arrs, frames):
    s_sum, s_cnt, t_sum, t_cnt = arrs
    S, C, T, N = s_sum[frames].sum(), s_cnt[frames].sum(), t_sum[frames].sum(), t_cnt[frames].sum()
    return (S / C if C else np.nan, T / N if N else np.nan,
            C / len(frames) if len(frames) else np.nan, N)


_S = {}
TARGET = {}
CONF = {}


def _job(seed):
    rng = np.random.default_rng(seed)
    units = [np.arange(x['start'], x['start'] + x['n']) for x in BOUNDS]
    pick = rng.integers(0, len(units), len(units))
    fr = np.concatenate([units[i] for i in pick])
    out = {}
    for tag, (sa, sb, pa, pb) in _S.items():
        keep = fr[np.isin(fr, TARGET[tag])]
        if len(keep) == 0:
            continue
        ca, cb = conf_of(CONF[tag][0], keep), conf_of(CONF[tag][1], keep)
        out[tag] = dict(
            map_vel=(sa.evaluate(0.0, frames=keep) * 100, sb.evaluate(0.0, frames=keep) * 100),
            map_all=(sa.evaluate(0.0, frames=keep, require_velocity=False) * 100,
                     sb.evaluate(0.0, frames=keep, require_velocity=False) * 100),
            conf=(ca[0], cb[0]), conf_tp=(ca[1], cb[1]), dpf=(ca[2], cb[2]))
    return out


def ci(v):
    v = np.asarray([x for x in v if np.isfinite(x)])
    return dict(se=float(v.std(ddof=1)),
                ci=[float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))])


if __name__ == '__main__':
    tags = [t for t in ('small', 'base')
            if os.path.exists(f'experiments/e60_shift/dets-s5vit-{t}-shift{SHIFT}.npz')]
    assert tags, 'no shifted dump present yet'
    print(f'arms present: {tags}', flush=True)
    rows = {}
    for tag in tags:
        a, b, pa, pb = load(tag)
        # The frames the RELEASE starved: positions 0..3. Under SHIFT they sit at 16..19.
        f = frames_at(pa, *SHORT)
        # A start moved later than a sequence's first label leaves that label before the
        # first chunk; the dump records -1 for it. Requiring FULL in the shifted arm already
        # excludes those, so the pairing is on frames covered in both arms by construction.
        gained = f[(pb[f] >= FULL[0]) & (pb[f] < FULL[1])]
        TARGET[tag] = gained
        sa = Scorer(a['det'].astype(np.float64), a['gt'].astype(np.float64))
        sb = Scorer(b['det'].astype(np.float64), b['gt'].astype(np.float64))
        _S[tag] = (sa, sb, pa, pb)
        CONF[tag] = (perframe_conf(sa), perframe_conf(sb))
        ca, cb = conf_of(CONF[tag][0], gained), conf_of(CONF[tag][1], gained)
        r = dict(tag=tag, n=int(len(gained)),
                 map_vel=[sa.evaluate(0.0, frames=gained) * 100,
                          sb.evaluate(0.0, frames=gained) * 100],
                 map_all=[sa.evaluate(0.0, frames=gained, require_velocity=False) * 100,
                          sb.evaluate(0.0, frames=gained, require_velocity=False) * 100],
                 conf=[ca[0], cb[0]], conf_tp=[ca[1], cb[1]], dpf=[ca[2], cb[2]],
                 n_tp=[int(ca[3]), int(cb[3])])
        rows[tag] = r
        print(f"  s5vit-{tag}: n={r['n']} paired frames", flush=True)
        for k, unit in (('map_vel', 'pt mAP, velocity-evaluable'), ('map_all', 'pt mAP, all boxes'),
                        ('conf', 'mean confidence'), ('conf_tp', 'mean confidence, IoU>=0.5 matched'),
                        ('dpf', 'detections per frame')):
            lo, hi = r[k]
            print(f'      {unit:38s} 1-4 win {lo:8.4f}   17-20 win {hi:8.4f}   paired {hi - lo:+8.4f}',
                  flush=True)

    print(f'cluster bootstrap B={B} over {len(BOUNDS)} sequences', flush=True)
    with Pool(NPROC) as p:
        reps = p.map(_job, range(B))
    res = {}
    for tag, r in rows.items():
        d = dict(r)
        for k in ('map_vel', 'map_all', 'conf', 'conf_tp', 'dpf'):
            g = [x[tag][k][1] - x[tag][k][0] for x in reps if tag in x]
            st = ci(g)
            obs = r[k][1] - r[k][0]
            d[k + '_boot'] = dict(obs=obs, **st, z=obs / st['se'] if st['se'] else float('nan'))
            print(f"  s5vit-{tag} {k:8s}: {obs:+8.4f} +- {st['se']:.4f}"
                  f"  95% CI [{st['ci'][0]:+8.4f}, {st['ci'][1]:+8.4f}]"
                  f"  z={d[k + '_boot']['z']:+6.2f}", flush=True)
        res[tag] = d
    json.dump(dict(shift=SHIFT, B=B, short=SHORT, full=FULL, iou_tp=IOU_TP, models=res),
              open(OUT, 'w'), indent=1)
    print('WROTE', OUT)
