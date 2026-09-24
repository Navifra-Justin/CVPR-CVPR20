"""E58d - the same contrast on the population the released Gen1 number is computed over.

E58b measured the chunk-position effect on this paper's velocity-evaluable moving-object
subset, which is the right population for a displacement analysis but is not the population
a released Gen1 mAP is reported over. This repeats the contrast with every labelled box
scored, so the level is comparable to a published table and the effect can be quoted in the
units a leaderboard uses. Displacement is not applied here; the only variable is how many
windows of history the protocol gave each detection.
"""
import numpy as np, json, os
from multiprocessing import Pool
from e56_eval import Scorer, load_dump, model_paths

SHORT, FULL = (0, 4), (16, 21)
RVT = ['rvt-t', 'rvt-s', 'rvt-b']
SSM = ['s5vit-small', 's5vit-base']
B = int(os.environ.get('B', '300'))
NW = int(os.environ.get('NW', '40'))

P = np.load('experiments/e58_chunkpos/positions.npy')
BOUNDS = json.load(open('experiments/e56_resolving/seqmap.json'))
UNITS = [np.arange(b['start'], b['start'] + b['n']) for b in BOUNDS]
_S = {}


def _init(paths):
    for nm, q in paths:
        det, gt = load_dump(q)
        _S[nm] = Scorer(det, gt)


def _point(a):
    nm, k, lo, hi = a
    fr = np.flatnonzero((P >= lo) & (P < hi))
    return nm, k, _S[nm].evaluate(0.0, frames=fr, require_velocity=False), len(fr)


def _boot(b):
    rng = np.random.default_rng(90260916 + b)
    fr = np.concatenate([UNITS[u] for u in rng.integers(0, len(UNITS), len(UNITS))])
    p = P[fr]
    fs = fr[(p >= SHORT[0]) & (p < SHORT[1])]; ff = fr[(p >= FULL[0]) & (p < FULL[1])]
    return b, {n: (_S[n].evaluate(0.0, frames=fs, require_velocity=False),
                   _S[n].evaluate(0.0, frames=ff, require_velocity=False)) for n in _S}


def did(d, t, ctl):
    return d[t] - float(np.mean([d[c] for c in ctl]))


if __name__ == '__main__':
    paths = model_paths(); names = [n for n, _ in paths]
    jobs = [(n, k, lo, hi) for n in names
            for k, (lo, hi) in [('short', SHORT), ('full', FULL), ('pooled', (-1, 22))]]
    A = {}
    with Pool(NW, initializer=_init, initargs=(paths,)) as pool:
        for n, k, v, c in pool.imap_unordered(_point, jobs, chunksize=1):
            A.setdefault(n, {})[k] = v
    print("every labelled box scored, delta = 0\n")
    print(f"{'model':<14}{'pooled':>9}{'short':>9}{'full':>9}{'raw':>8}{'ctl':>8}{'DiD pt':>9}")
    d = {n: (A[n]['short'] - A[n]['full']) * 100 for n in names}
    dp = {n: (A[n]['pooled'] - A[n]['full']) * 100 for n in names}
    res = {'point': {n: A[n] for n in names}, 'did': {}, 'pooled_gap': {}}
    for n in names:
        ctl = [c for c in RVT if c != n]
        res['did'][n] = did(d, n, ctl); res['pooled_gap'][n] = did(dp, n, ctl)
        print(f"{n:<14}{A[n]['pooled']*100:9.3f}{A[n]['short']*100:9.3f}{A[n]['full']*100:9.3f}"
              f"{d[n]:8.3f}{float(np.mean([d[c] for c in ctl])):8.3f}{res['did'][n]:9.3f}"
              f"{'' if n in SSM else '   <- placebo'}")
    print(f"\n{'model':<14}{'released':>10}{'full-sup':>10}{'gap pt':>9}{'net of ctl':>12}")
    for n in names:
        print(f"{n:<14}{A[n]['pooled']*100:10.3f}{A[n]['full']*100:10.3f}"
              f"{dp[n]:9.3f}{res['pooled_gap'][n]:12.3f}")

    print(f"\ncluster bootstrap B={B} over {len(UNITS)} sequences", flush=True)
    acc = {n: [] for n in names}
    with Pool(NW, initializer=_init, initargs=(paths,)) as pool:
        for i, (b, o) in enumerate(pool.imap_unordered(_boot, range(B), chunksize=1)):
            for n in names:
                acc[n].append(o[n])
            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{B}", flush=True)
    print(f"\n{'model':<14}{'DiD pt':>9}{'SE':>8}{'95% CI':>20}{'z':>8}")
    res['boot'] = {}
    for n in names:
        rep = np.array([did({m: (acc[m][k][0] - acc[m][k][1]) * 100 for m in names},
                            n, [c for c in RVT if c != n]) for k in range(B)])
        se = float(rep.std(ddof=1)); lo, hi = np.percentile(rep, [2.5, 97.5])
        res['boot'][n] = {'se': se, 'lo': float(lo), 'hi': float(hi)}
        print(f"{n:<14}{res['did'][n]:9.3f}{se:8.3f}{f'[{lo:+.3f}, {hi:+.3f}]':>20}"
              f"{res['did'][n]/max(se,1e-9):8.2f}{'' if n in SSM else '   <- placebo'}")
    json.dump(res, open('experiments/e58_chunkpos/allbox.json', 'w'), indent=1)
    print("\nWROTE experiments/e58_chunkpos/allbox.json")
