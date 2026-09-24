"""E56b - the benchmark's own noise floor, and the displacement that clears it.

A displacement cost is only a cost if it is larger than the uncertainty of the number it is
subtracted from. Gen1's validation split is 406 sequences; frames inside one sequence are not
independent, so the resampling unit is the sequence.

Two standard errors are produced, and they answer different questions:

  SE(mAP)        - resampling sequences and scoring at one displacement. This is the error
                   bar on a published number, and it is what a *comparison between two
                   papers* has to clear.
  SE(dmAP)       - resampling sequences and scoring the same resample at two displacements,
                   then differencing. The sequence effect cancels, so this is much smaller,
                   and it is what a *within-paper claim that a displacement matters* has to
                   clear.

The gap between the two is the result: the displacement effect is resolvable within one
evaluation and invisible between two.
"""
import numpy as np, json, os, sys
from multiprocessing import Pool
from e56_eval import Scorer, load_dump, model_paths

B = int(os.environ.get('B', '200'))
SEED = 20260916
TAU_MS = 23.81
DELTAS_MS = [0.0, -10.0, -23.81, -50.0, -100.0, -200.0]
STRATA = [('all moving', None, None), ('25-50 px/s', 25., 50.)]
OUT = 'experiments/e56_resolving/bootstrap.json'

_S = {}
_SEQ = None


def _init(paths, seq):
    global _SEQ
    _SEQ = seq
    for nm, p in paths:
        det, gt = load_dump(p)
        _S[nm] = Scorer(det, gt)


def _job(a):
    nm, sname, lo, hi, b = a
    rng = np.random.default_rng(SEED + 1000 * b)
    pick = rng.integers(0, len(_SEQ), len(_SEQ))
    frames = np.concatenate([np.arange(_SEQ[i]['start'], _SEQ[i]['start'] + _SEQ[i]['n'])
                             for i in pick if _SEQ[i]['n'] > 0])
    return (nm, sname, b, [_S[nm].evaluate(d * 1e-3, lo, hi, frames=frames) for d in DELTAS_MS])


if __name__ == '__main__':
    paths = model_paths()
    seq = json.load(open('experiments/e56_resolving/seqmap.json'))
    print(f"{len(paths)} checkpoints, {len(seq)} resampling units, B={B}", flush=True)
    jobs = [(nm, s, lo, hi, b) for nm, _ in paths for s, lo, hi in STRATA for b in range(B)]
    acc = {}
    with Pool(processes=64, initializer=_init, initargs=(paths, seq)) as pool:
        for i, (nm, sname, b, vals) in enumerate(pool.imap_unordered(_job, jobs, chunksize=1)):
            acc.setdefault(nm, {}).setdefault(sname, []).append(vals)
            if (i + 1) % 100 == 0:
                print(f"  {i+1}/{len(jobs)}", flush=True)

    out = {'B': B, 'deltas_ms': DELTAS_MS, 'n_units': len(seq), 'per_model': {}}
    print(f"\n{'model':<13}{'stratum':<12}{'delta':>9}  {'SE(mAP) pt':>11}  {'SE(dmAP) pt':>12}"
          f"  {'dmAP pt':>9}  {'|d|/SE':>7}")
    for nm, _ in paths:
        out['per_model'][nm] = {}
        for sname, _, _ in STRATA:
            A = np.array(acc[nm][sname])                       # (B, len(DELTAS))
            se_abs = A.std(axis=0, ddof=1) * 100
            d = (A - A[:, [0]]) * 100                          # paired difference vs delta=0
            se_pair = d.std(axis=0, ddof=1)
            mean_d = d.mean(axis=0)
            out['per_model'][nm][sname] = dict(
                se_map_pt=[float(v) for v in se_abs],
                se_dmap_pt=[float(v) for v in se_pair],
                mean_dmap_pt=[float(v) for v in mean_d])
            for j, dm in enumerate(DELTAS_MS):
                z = abs(mean_d[j]) / se_pair[j] if se_pair[j] > 0 else float('nan')
                print(f"{nm:<13}{sname:<12}{dm:9.2f}  {se_abs[j]:11.4f}  {se_pair[j]:12.4f}"
                      f"  {mean_d[j]:9.4f}  {z:7.1f}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w'), indent=1)
    print(f"\nWROTE {OUT}")
