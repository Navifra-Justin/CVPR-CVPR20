"""E58b - how much of a released benchmark number is the unnamed support variable worth?

E58 reconstructed, from the release's own indexing rule, how many windows of history each
released SSM-ViT detection actually had: one at position 0 of a streaming chunk, twenty-one
at position 20. The reported Gen1 number averages over all twenty-one without naming the
variable it averages over.

Position groups hold different frames, so a raw mAP difference across positions mixes the
support effect with scene content. RVT is the control: it is driven one window per call with
its state carried across the whole sequence after a 20-window warm-up, so it never has short
history and chunk position is, for it, an arbitrary label on the same frames. The estimand is
therefore the difference-in-differences

    DiD_j = [mAP_j(short) - mAP_j(full)] - mean_over_RVT [mAP_r(short) - mAP_r(full)] ,

read in mAP points. A leave-one-out placebo re-runs the same contrast with each RVT model in
the treated slot and the remaining two as its control; those must come out near zero, since
no RVT detection's support depends on the label.

Uncertainty is a cluster bootstrap over the 406 admitted sequences, the same resampling unit
E56 uses, because frames inside a sequence are dependent.
"""
import numpy as np, json, os, sys
from multiprocessing import Pool
from e56_eval import Scorer, load_dump, model_paths

CHUNK = 21
SHORT = (0, 4)      # positions 0..3   : 1 to 4 windows of history
FULL = (16, 21)     # positions 16..20 : 17 to 21 windows
RVT = ['rvt-t', 'rvt-s', 'rvt-b']
SSM = ['s5vit-small', 's5vit-base']
B = int(os.environ.get('B', '300'))
NW = int(os.environ.get('NW', '24'))

P = np.load('experiments/e58_chunkpos/positions.npy')
# E56's resampling units: a list of {seq, start, n}, frames [start, start+n) per sequence.
BOUNDS = json.load(open('experiments/e56_resolving/seqmap.json'))
UNITS = [np.arange(b['start'], b['start'] + b['n']) for b in BOUNDS]
assert sum(len(u) for u in UNITS) == len(P), "seqmap and the position array disagree on frame count"

_S = {}


def _init(paths):
    for nm, q in paths:
        det, gt = load_dump(q)
        _S[nm] = Scorer(det, gt)


def _point(a):
    nm, kind, lo, hi = a
    fr = np.flatnonzero((P >= lo) & (P < hi))
    return (nm, kind, _S[nm].evaluate(0.0, frames=fr), len(fr))


def _boot(b):
    """One bootstrap replicate: resample sequences, return every model's short/full mAP."""
    rng = np.random.default_rng(20260916 + b)
    pick = rng.integers(0, len(UNITS), len(UNITS))
    fr = np.concatenate([UNITS[u] for u in pick])
    p = P[fr]
    fs = fr[(p >= SHORT[0]) & (p < SHORT[1])]
    ff = fr[(p >= FULL[0]) & (p < FULL[1])]
    out = {}
    for nm in _S:
        out[nm] = (_S[nm].evaluate(0.0, frames=fs), _S[nm].evaluate(0.0, frames=ff))
    return b, out


def did(d, treated, controls):
    return d[treated] - float(np.mean([d[c] for c in controls]))


if __name__ == '__main__':
    paths = model_paths()
    names = [n for n, _ in paths]

    jobs = [(nm, 'pos%02d' % p, p, p + 1) for nm in names for p in range(CHUNK)]
    jobs += [(nm, k, lo, hi) for nm in names for k, (lo, hi) in [('short', SHORT), ('full', FULL)]]
    jobs += [(nm, 'pooled', -1, CHUNK + 1) for nm in names]
    print(f"{len(jobs)} point evaluations on {NW} workers", flush=True)
    A = {}
    with Pool(processes=NW, initializer=_init, initargs=(paths,)) as pool:
        for nm, k, v, n in pool.imap_unordered(_point, jobs, chunksize=1):
            A.setdefault(nm, {})[k] = v
            A[nm].setdefault('n', {})[k] = n

    print("\nmAP by number of windows of history actually available (delta = 0)")
    print(f"{'windows':>8}" + "".join(f"{n:>13}" for n in names))
    for p in range(CHUNK):
        print(f"{p+1:>8}" + "".join(f"{A[n]['pos%02d' % p]*100:13.3f}" for n in names))
    print(f"{'n':>8}" + "".join(f"{A[names[0]]['n']['pos%02d' % 0]:13d}" for _ in names))

    print(f"\ncontrast: positions {SHORT[0]}-{SHORT[1]-1} (short) vs {FULL[0]}-{FULL[1]-1} (full)")
    print(f"  n(short) = {A[names[0]]['n']['short']}   n(full) = {A[names[0]]['n']['full']}"
          f"   n(pooled) = {A[names[0]]['n']['pooled']}")
    d = {n: (A[n]['short'] - A[n]['full']) * 100 for n in names}
    print(f"\n{'model':<14}{'short':>10}{'full':>10}{'raw diff':>10}{'control':>10}{'DiD pt':>10}")
    res = {'per_position': {n: [A[n]['pos%02d' % p] for p in range(CHUNK)] for n in names},
           'n_per_position': [A[names[0]]['n']['pos%02d' % p] for p in range(CHUNK)],
           'short': {n: A[n]['short'] for n in names}, 'full': {n: A[n]['full'] for n in names},
           'pooled': {n: A[n]['pooled'] for n in names}, 'did': {}}
    for n in names:
        ctl = [c for c in RVT if c != n]
        v = did(d, n, ctl)
        tag = '' if n in SSM else '   <- placebo'
        print(f"{n:<14}{A[n]['short']*100:10.3f}{A[n]['full']*100:10.3f}"
              f"{d[n]:10.3f}{float(np.mean([d[c] for c in ctl])):10.3f}{v:10.3f}{tag}")
        res['did'][n] = v

    print("\nthe released number against the number its own full support delivers")
    print(f"{'model':<14}{'released':>10}{'full-sup':>10}{'gap pt':>10}{'net of ctl':>12}")
    dp = {n: (A[n]['pooled'] - A[n]['full']) * 100 for n in names}
    res['pooled_gap'] = {}
    for n in names:
        ctl = [c for c in RVT if c != n]
        v = did(dp, n, ctl)
        print(f"{n:<14}{A[n]['pooled']*100:10.3f}{A[n]['full']*100:10.3f}{dp[n]:10.3f}{v:12.3f}")
        res['pooled_gap'][n] = v

    print(f"\ncluster bootstrap: B={B} over {len(UNITS)} sequences", flush=True)
    acc = {n: [] for n in names}
    with Pool(processes=NW, initializer=_init, initargs=(paths,)) as pool:
        for i, (b, out) in enumerate(pool.imap_unordered(
                _boot, range(B), chunksize=1)):
            for n in names:
                acc[n].append(out[n])
            if (i + 1) % 25 == 0:
                print(f"  {i+1}/{B}", flush=True)

    print(f"\n{'model':<14}{'DiD pt':>10}{'SE':>8}{'95% CI':>20}{'z':>8}")
    res['boot'] = {}
    for n in names:
        rep = []
        for k in range(B):
            dd = {m: (acc[m][k][0] - acc[m][k][1]) * 100 for m in names}
            rep.append(did(dd, n, [c for c in RVT if c != n]))
        rep = np.array(rep); se = float(rep.std(ddof=1))
        lo, hi = np.percentile(rep, [2.5, 97.5])
        tag = '' if n in SSM else '   <- placebo'
        print(f"{n:<14}{res['did'][n]:10.3f}{se:8.3f}"
              f"{f'[{lo:+.3f}, {hi:+.3f}]':>20}{res['did'][n]/max(se,1e-9):8.2f}{tag}")
        res['boot'][n] = {'se': se, 'lo': float(lo), 'hi': float(hi)}

    json.dump(res, open('experiments/e58_chunkpos/did.json', 'w'), indent=1)
    print("\nWROTE experiments/e58_chunkpos/did.json")
