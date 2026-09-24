"""E58e - the chunk-position contrast resolved position by position.

E58d reports the contrast as two aggregates, short against full. The same quantity
measured at each of the \\ssmEvalChunk{} positions separately shows whether the effect is a
monotone consequence of accumulated history or a step at the aggregation boundary, and it
puts the placebo checkpoints on the same axis. Every labelled box is scored, so the level
matches a published table, and displacement is not applied: the only variable is how many
windows of history the released protocol gave each detection.
"""
import numpy as np, json, os
from multiprocessing import Pool
from e56_eval import Scorer, load_dump, model_paths

NW = int(os.environ.get('NW', '40'))
CHUNK = 21
P = np.load('experiments/e58_chunkpos/positions.npy')
_S, _D = {}, {}


def _init(paths):
    for nm, q in paths:
        det, gt = load_dump(q)
        _S[nm] = Scorer(det, gt)
        _D[nm] = det


def _point(a):
    nm, p = a
    fr = np.flatnonzero(P == p)
    m = _S[nm].evaluate(0.0, frames=fr, require_velocity=False)
    d = _D[nm]
    sel = np.isin(d[:, 0].astype(int), fr)
    return nm, p, m, float(d[sel, 5].mean()) if sel.any() else float('nan'), len(fr)


if __name__ == '__main__':
    paths = model_paths(); names = [n for n, _ in paths]
    jobs = [(n, p) for n in names for p in range(CHUNK)]
    M = {n: [0.0] * CHUNK for n in names}; C = {n: [0.0] * CHUNK for n in names}
    NF = [0] * CHUNK
    print(f"{len(jobs)} evaluations on {NW} workers", flush=True)
    with Pool(NW, initializer=_init, initargs=(paths,)) as pool:
        for nm, p, m, c, nf in pool.imap_unordered(_point, jobs, chunksize=1):
            M[nm][p] = m; C[nm][p] = c; NF[p] = nf
    print("\nmAP by chunk position, every labelled box, delta = 0")
    print("windows  " + "".join(f"{n:>13}" for n in names))
    for p in range(CHUNK):
        print(f"{p+1:7d}  " + "".join(f"{M[n][p]*100:13.3f}" for n in names))
    print(f"{'n':>7}  " + "".join(f"{NF[p]:13d}" for p in range(0, 1)))
    print("\nmean detection confidence by chunk position")
    print("windows  " + "".join(f"{n:>13}" for n in names))
    for p in range(CHUNK):
        print(f"{p+1:7d}  " + "".join(f"{C[n][p]:13.4f}" for n in names))
    json.dump({'map': M, 'conf': C, 'n_frames': NF},
              open('experiments/e58_chunkpos/curve.json', 'w'), indent=1)
    print("\nWROTE experiments/e58_chunkpos/curve.json")
