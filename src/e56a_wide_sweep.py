"""E56a - how fast would Gen1's objects have to move before the metric could see 23.81 ms?

The manuscript's displacement intervention moves every ground-truth box by delta * v, where
v is that box's own centered label velocity. The intervention therefore depends on delta and
v only through their product:

    mAP(delta ; velocities v)  ==  mAP(k*delta ; velocities v/k)     exactly,

so sweeping delta past the measured interval is the same experiment as holding the interval
fixed and asking what the benchmark would report if its objects moved k = delta / tau times
faster, with tau = 23.81 ms the newest-window occlusion-sensitivity centroid. The detections
are held fixed, so this is a statement about what the metric can resolve at a given label
composition, not a prediction of how a detector trained on faster objects would score.

The sweep is run for all five released checkpoints in four speed strata, and the results feed
three questions E56b-E56d ask: where the displacement first exceeds the benchmark's own noise,
where it first exceeds the gap between two released checkpoints, and whether the four strata
collapse onto one curve once delta is scaled by each stratum's own speed.
"""
import numpy as np, json, os, sys
from multiprocessing import Pool
from e56_eval import Scorer, load_dump, model_paths

TAU_MS = 23.81
GRID = [0.0, 2.5, 5.0, 7.5, 10.0, 15.0, 20.0, 23.81, 30.0, 40.0, 50.0, 60.0, 80.0,
        100.0, 125.0, 150.0, 200.0, 250.0, 300.0, 400.0, 500.0]
DELTAS_MS = sorted(set([-d for d in GRID] + GRID))
STRATA = [('all moving', None, None), ('10-25 px/s', 10., 25.),
          ('25-50 px/s', 25., 50.), ('>50 px/s', 50., 1e9)]
OUT = 'experiments/e56_resolving/wide_sweep.json'

_S = {}


def _init(paths):
    for nm, p in paths:
        det, gt = load_dump(p)
        _S[nm] = Scorer(det, gt)


def _job(a):
    nm, sname, lo, hi, d = a
    return (nm, sname, d, _S[nm].evaluate(d * 1e-3, lo, hi))


if __name__ == '__main__':
    paths = model_paths()
    print(f"{len(paths)} checkpoints: {', '.join(n for n, _ in paths)}")
    gts = []
    for nm, p in paths:
        _, gt = load_dump(p); gts.append(gt)
    for g in gts[1:]:
        if g.shape != gts[0].shape or not np.allclose(g, gts[0], equal_nan=True):
            raise SystemExit("ground truth differs between dumps: not a comparison")
    print(f"ground truth identical across dumps: {gts[0].shape[0]} boxes")
    del gts

    jobs = [(nm, s, lo, hi, d) for nm, _ in paths for s, lo, hi in STRATA for d in DELTAS_MS]
    print(f"{len(jobs)} evaluations on {min(len(jobs), 64)} workers", flush=True)
    res = {}
    with Pool(processes=min(64, len(jobs)), initializer=_init, initargs=(paths,)) as pool:
        for i, (nm, sname, d, v) in enumerate(pool.imap_unordered(_job, jobs, chunksize=1)):
            res.setdefault(nm, {}).setdefault(sname, {})[f"{d:.2f}"] = v
            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{len(jobs)}", flush=True)

    out = {'tau_ms': TAU_MS, 'deltas_ms': DELTAS_MS,
           'strata': [s for s, _, _ in STRATA], 'curves': {}}
    for nm, _ in paths:
        out['curves'][nm] = {}
        for s, _, _ in STRATA:
            c = [res[nm][s][f"{d:.2f}"] for d in DELTAS_MS]
            out['curves'][nm][s] = dict(deltas_ms=DELTAS_MS, map=c,
                                        k=[d / TAU_MS for d in DELTAS_MS])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w'), indent=1)

    print("\nmAP at delta = k * 23.81 ms, all moving")
    print(f"{'k':>6} {'delta ms':>9} " + " ".join(f"{n:>12}" for n, _ in paths))
    for d in DELTAS_MS:
        if d < 0:
            continue
        row = " ".join(f"{out['curves'][n]['all moving']['map'][DELTAS_MS.index(d)]:12.5f}"
                       for n, _ in paths)
        print(f"{d/TAU_MS:6.2f} {d:9.2f} {row}")
    print(f"\nWROTE {OUT}")
