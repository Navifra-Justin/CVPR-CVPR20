"""E56d - does the published ordering survive the benchmark's own resampling noise?

E56b reported SE(mAP) around 2.2-2.8 points over a cluster bootstrap of the 406 validation
sequences. That is the right floor for a number computed on a different sample, but it is the
wrong floor for comparing two checkpoints, because the five checkpoints are scored on the
same sequences and scene difficulty cancels in their difference. The honest quantity is
SE(mAP_i - mAP_j), formed inside each replicate.

This stores the per-replicate scores themselves rather than a summary, so the paired
difference can be formed afterwards, and reports for every adjacent published pair how often
the resampled ordering disagrees with the published one. Both populations are scored: this
paper's velocity-evaluable moving subset, and every labelled box, which is the population a
released Gen1 number is reported over.
"""
import numpy as np, json, os
from multiprocessing import Pool
from e56_eval import Scorer, load_dump, model_paths

B = int(os.environ.get('B', '200'))
NW = int(os.environ.get('NW', '40'))
BOUNDS = json.load(open('experiments/e56_resolving/seqmap.json'))
UNITS = [np.arange(b['start'], b['start'] + b['n']) for b in BOUNDS]
_S = {}


def _init(paths):
    for nm, q in paths:
        det, gt = load_dump(q)
        _S[nm] = Scorer(det, gt)


def _boot(b):
    rng = np.random.default_rng(560916 + b)
    fr = np.concatenate([UNITS[u] for u in rng.integers(0, len(UNITS), len(UNITS))])
    return b, {n: (_S[n].evaluate(0.0, frames=fr),
                   _S[n].evaluate(0.0, frames=fr, require_velocity=False)) for n in _S}


if __name__ == '__main__':
    paths = model_paths(); names = [n for n, _ in paths]
    with Pool(NW, initializer=_init, initargs=(paths,)) as pool:
        M = {n: np.zeros((B, 2)) for n in names}
        for i, (b, o) in enumerate(pool.imap_unordered(_boot, range(B), chunksize=1)):
            for n in names:
                M[n][b] = o[n]
            if (i + 1) % 25 == 0:
                print(f"  {i+1}/{B}", flush=True)
    _init(paths)
    point = {n: (_S[n].evaluate(0.0), _S[n].evaluate(0.0, require_velocity=False)) for n in names}

    res = {'B': B, 'point': point, 'pairs': {}}
    for j, lab in enumerate(['moving subset', 'every labelled box']):
        v = {n: M[n][:, j] * 100 for n in names}
        pt = {n: point[n][j] * 100 for n in names}
        order = sorted(names, key=lambda n: -pt[n])
        print(f"\n=== {lab} ===")
        print("  published order: " + " > ".join(order))
        print(f"  {'pair':<28}{'gap pt':>9}{'SE(gap)':>10}{'z':>7}{'P(flip)':>10}"
              f"{'SE(mAP)':>10}")
        for a, c in zip(order, order[1:]):
            d = v[a] - v[c]; g = pt[a] - pt[c]
            se = float(d.std(ddof=1)); pf = float((d <= 0).mean())
            print(f"  {a+' > '+c:<28}{g:9.3f}{se:10.3f}{g/max(se,1e-9):7.2f}{pf:10.3f}"
                  f"{float(v[a].std(ddof=1)):10.3f}")
            res['pairs'].setdefault(lab, []).append(
                {'hi': a, 'lo': c, 'gap': g, 'se': se, 'p_flip': pf,
                 'se_abs': float(v[a].std(ddof=1))})
        allc = np.ones(B, dtype=bool)
        for a, c in zip(order, order[1:]):
            allc &= (v[a] - v[c]) > 0
        print(f"  the full published ordering is reproduced in {allc.mean()*100:.1f} % of "
              f"{B} resamples")
        res.setdefault('order_preserved', {})[lab] = float(allc.mean())
    json.dump(res, open('experiments/e56_resolving/rankse.json', 'w'), indent=1)
    print("\nWROTE experiments/e56_resolving/rankse.json")
