"""E70 - paired chunk-boundary move on 1 Mpx. Port of src/e60_paired.py / e65_paired.py to the dumps
written by src/e70_1mpx_dump.py (CHUNK=10). Original files are untouched.

Frames the release (SHIFT=0) places at chunk positions SHORT=[0,2) (one or two windows of history)
are the target set. Under SHIFT=s they sit at (p - s) mod CHUNK. The same frames, weights, labels
and evaluator are scored in both arms; only the boundary moves.

usage: ARMS="s5vit-base:0,5 rvt-s:carry0,carry5,reset0,reset5" python3 src/e70_1mpx_paired.py
Each arm name maps to experiments/e70_1mpx/dets-<model>[-<regime>]-shift<k>.npz (regime tag in file name).
Cluster bootstrap over sequences (dump `seq` array), B from env.
"""
import json, os, sys, numpy as np
sys.path.insert(0, 'src')
from e56_eval import Scorer
from multiprocessing import Pool

CHUNK = int(os.environ.get('CHUNK', '10')); SHORT = (0, int(os.environ.get('SHORTN', '2')))
S = int(os.environ.get('SHIFT', '2')); B = int(os.environ.get('B', '300')); NPROC = int(os.environ.get('NPROC', '4'))
ROOT = os.environ.get('ROOT', 'experiments/e70_1mpx'); OUT = os.environ.get('OUT', f'{ROOT}/paired-shift{S}.json')
GAIN = sorted((p - S) % CHUNK for p in range(*SHORT))
DATA = {}


def paths(model, regime):
    mid = '' if regime is None else f'-{regime}'
    return (f'{ROOT}/dets-{model}{mid}-shift0.npz', f'{ROOT}/dets-{model}{mid}-shift{S}.npz')


def load_pair(model, regime):
    pa, pb = paths(model, regime); a = np.load(pa); b = np.load(pb)
    assert np.array_equal(a['gt'], b['gt'], equal_nan=True), 'ground truth differs between arms'
    assert np.array_equal(a['seq'], b['seq'])
    fa, fb = a['pos'], b['pos']
    tgt = np.flatnonzero((fa >= SHORT[0]) & (fa < SHORT[1]) & np.isin(fb, GAIN))
    # every target frame must rotate by exactly S (checked, not assumed)
    assert np.all(((fa[tgt] - fb[tgt]) % CHUNK) == S % CHUNK), 'rotation is not S for some target frame'
    sa = Scorer(a['det'].astype(np.float64), a['gt'].astype(np.float64))
    sb = Scorer(b['det'].astype(np.float64), b['gt'].astype(np.float64))
    return sa, sb, tgt, a['seq'], len(fa)


def measure(sa, sb, fr):
    return dict(map_vel=[sa.evaluate(0.0, frames=fr) * 100, sb.evaluate(0.0, frames=fr) * 100],
                map_all=[sa.evaluate(0.0, frames=fr, require_velocity=False) * 100,
                         sb.evaluate(0.0, frames=fr, require_velocity=False) * 100])


def _job(args):
    key, seed = args
    sa, sb, tgt, seq = DATA[key]
    rng = np.random.default_rng(seed)
    us = np.unique(seq); pick = rng.integers(0, len(us), len(us))
    by = {u: np.flatnonzero(seq == u) for u in us}
    fr = np.concatenate([by[us[i]] for i in pick]); fr = fr[np.isin(fr, tgt)]
    return measure(sa, sb, fr) if len(fr) else None


if __name__ == '__main__':
    arms = []
    for tok in os.environ['ARMS'].split():
        m, regs = tok.split(':'); 
        for r in regs.split(','): arms.append((m, None if r == '-' else r))
    res = {}
    for m, r in arms:
        key = f'{m}{"" if r is None else "-" + r}'
        sa, sb, tgt, seq, nfr = load_pair(m, r); DATA[key] = (sa, sb, tgt, seq)
        obs = measure(sa, sb, tgt); res[key] = dict(n_target=int(len(tgt)), n_frames=nfr, n_seq=int(len(np.unique(seq))), **obs)
        print(key, 'n_target', len(tgt), {k: [round(x, 3) for x in v] for k, v in obs.items()}, flush=True)
    with Pool(NPROC) as p:
        for key in list(res):
            reps = [x for x in p.map(_job, [(key, s) for s in range(B)]) if x]
            for k in ('map_vel', 'map_all'):
                g = np.array([x[k][1] - x[k][0] for x in reps]); o = res[key][k][1] - res[key][k][0]
                res[key][k + '_boot'] = dict(obs=o, se=float(g.std(ddof=1)), ci=[float(np.percentile(g, 2.5)), float(np.percentile(g, 97.5))],
                                              z=o / float(g.std(ddof=1)) if g.std(ddof=1) else float('nan'))
                print(f"  {key:22s} {k:8s} {o:+8.3f} +- {g.std(ddof=1):.3f}  CI [{res[key][k+'_boot']['ci'][0]:+.3f},{res[key][k+'_boot']['ci'][1]:+.3f}]", flush=True)
    json.dump(dict(shift=S, chunk=CHUNK, short=SHORT, gain=GAIN, B=B, arms=res), open(OUT, 'w'), indent=1)
    print('WROTE', OUT)
