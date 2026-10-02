"""E66 prelim: mAP by H=pos+1 for RVT reset-shift0 vs carry; same Scorer path as src/e58e_curve.py.
Single process, CPU only. Sources scored: e51 dump (reproduces curve.json), e65 carry, e65 reset."""
import sys, json, numpy as np
sys.path.insert(0, 'src')
from e56_eval import Scorer, load_dump
P = np.load('experiments/e58_chunkpos/positions.npy')
E65 = 'experiments/e65_rvt_boundary/dets-rvt-%s-%s-shift0.npz'
srcs = {}
for t in 'sb':
    srcs[f'rvt-{t}:e51'] = f'experiments/e51_ranking/dets-rvt-{t}.npz'
    srcs[f'rvt-{t}:e65carry'] = E65 % (t, 'carry')
    srcs[f'rvt-{t}:e65reset'] = E65 % (t, 'reset')
out = {}
for k, q in srcs.items():
    det, gt = load_dump(q)
    z = np.load(q)
    pos_ok = bool((np.load(q)['pos'] == P).all()) if 'pos' in z.files else None
    S = Scorer(det, gt)
    out[k] = {'pos_equal_e58': pos_ok,
              'map': [S.evaluate(0.0, frames=np.flatnonzero(P == p), require_velocity=False) for p in range(21)]}
    print(k, pos_ok, flush=True)
json.dump(out, open('experiments/e66_fixedH_prelim/curve_raw.json', 'w'), indent=1)
