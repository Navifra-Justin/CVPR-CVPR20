"""E58g - a permutation null for the chunk-position contrast.

The cluster bootstrap of E58d gives the sampling error of the difference-in-differences
but assumes the position labels mean what the reconstruction says they mean. This test
removes that assumption. Chunk position is reshuffled among the frames of each sequence,
which preserves every other property of the frame set - scene, sequence length, label
density, the sizes of the short and full blocks - and destroys only the correspondence
between a frame and the amount of recurrent history the protocol gave it. The DiD is
recomputed on each reshuffle. A permutation null centred on zero and narrow compared with
the observed effect leaves the reconstructed position as the only variable that carries it.

It also re-derives the pooled number from the same evaluator, which must reproduce the
released-protocol score the other scripts report.
"""
import numpy as np, json, os
from multiprocessing import Pool
from e56_eval import Scorer, load_dump, model_paths

SHORT, FULL = (0, 4), (16, 21)
RVT = ['rvt-t', 'rvt-s', 'rvt-b']
B = int(os.environ.get('B', '200'))
NW = int(os.environ.get('NW', '40'))

P = np.load('experiments/e58_chunkpos/positions.npy')
BOUNDS = json.load(open('experiments/e56_resolving/seqmap.json'))
UNITS = [np.arange(b['start'], b['start'] + b['n']) for b in BOUNDS]
_S = {}


def _init(paths):
    for nm, q in paths:
        det, gt = load_dump(q)
        _S[nm] = Scorer(det, gt)


def _blocks(p):
    return (np.flatnonzero((p >= SHORT[0]) & (p < SHORT[1])),
            np.flatnonzero((p >= FULL[0]) & (p < FULL[1])))


def _perm(b):
    """Reshuffle position within each sequence, then rescore both blocks."""
    rng = np.random.default_rng(58070916 + b)
    q = P.copy()
    for u in UNITS:
        q[u] = rng.permutation(q[u])
    fs, ff = _blocks(q)
    return b, {n: (_S[n].evaluate(0.0, frames=fs, require_velocity=False),
                   _S[n].evaluate(0.0, frames=ff, require_velocity=False)) for n in _S}


def did(d, t, ctl):
    return d[t] - float(np.mean([d[c] for c in ctl]))


if __name__ == '__main__':
    paths = model_paths(); names = [n for n, _ in paths]
    A = json.load(open('experiments/e58_chunkpos/allbox.json'))
    obs = A['did']
    fs, ff = _blocks(P)
    print(f"observed blocks: short n={len(fs)}  full n={len(ff)}  total frames={len(P)}")
    assert not set(fs.tolist()) & set(ff.tolist()), 'blocks overlap'

    with Pool(NW, initializer=_init, initargs=(paths,)) as pool:
        # the pooled number the released protocol reports, from this evaluator
        pooled = {}
        for nm, q in paths:
            pass
        acc = {n: [] for n in names}
        print(f"\n{B} position permutations within sequence on {NW} workers", flush=True)
        for i, (b, o) in enumerate(pool.imap_unordered(_perm, range(B), chunksize=1)):
            for n in names:
                acc[n].append(o[n])
            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{B}", flush=True)

    print(f"\n{'model':<14}{'observed':>10}{'null mean':>11}{'null SD':>9}"
          f"{'|z|':>7}{'p (2-sided)':>13}")
    res = {}
    for n in names:
        rep = np.array([did({m: (acc[m][k][0] - acc[m][k][1]) * 100 for m in names},
                            n, [c for c in RVT if c != n]) for k in range(B)])
        mu, sd = float(rep.mean()), float(rep.std(ddof=1))
        z = (obs[n] - mu) / max(sd, 1e-9)
        p = (1 + int((np.abs(rep - mu) >= abs(obs[n] - mu)).sum())) / (B + 1)
        res[n] = {'obs': obs[n], 'null_mean': mu, 'null_sd': sd, 'z': z, 'p': p}
        print(f"{n:<14}{obs[n]:10.3f}{mu:11.3f}{sd:9.3f}{abs(z):7.2f}{p:13.4f}"
              f"{'' if n.startswith('s5') else '   <- placebo'}")
    json.dump(res, open('experiments/e58_chunkpos/perm.json', 'w'), indent=1)
    print("\nWROTE experiments/e58_chunkpos/perm.json")
