"""E71 evaluation: Support-Conditioned AP on 3000 stratified frames at H = 1, 5, 10, 21, 40, 80 (+ pooled).

Inputs : experiments/e66_fixedH/dets-<m>.npz (H=1,5,10,21), experiments/e51_ranking/dets-<m>.npz (pooled, released protocol),
         experiments/e71_h4080/dets-<m>.npz (H=21 regression, 40, 80), experiments/e71_h4080/frames.npz
Outputs: experiments/e71_h4080/results.json, tables.md
Same instrument as src/e66_eval.py (Cell/Scorer: all labelled boxes, delta=0), same bootstrap (sequence clusters, one draw for
every model and column).  Step 0 inside the script: the e66 numbers on the full common set are reproduced with this code path
(--selfcheck models), then the subset is scored.
Env: B (default 200), SEED, ONLY (comma list), HX (extra e71 columns, default 40,80), SELFCHECK=1
"""
import numpy as np, json, os, sys, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e66_eval import Cell, kendall
from e56_eval import Scorer
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E66 = f'{ROOT}/experiments/e66_fixedH'; E51 = f'{ROOT}/experiments/e51_ranking'; E71 = f'{ROOT}/experiments/e71_h4080'
MODELS = ['rvt-t', 'rvt-s', 'rvt-b', 's5vit-small', 's5vit-base']
if os.environ.get('ONLY'): MODELS = os.environ['ONLY'].split(',')
B = int(os.environ.get('B', '200')); SEED = int(os.environ.get('SEED', '20261002'))
HX = [int(h) for h in os.environ.get('HX', '40,80').split(',')]
FR = np.load(f'{E71}/frames.npz'); GID = FR['gid']; N = len(GID)
new_of = -np.ones(int(GID.max()) + 1, int); new_of[GID] = np.arange(N)
Z0 = np.load(f'{E66}/dets-{MODELS[0]}.npz'); SEQ66 = Z0['seq']; seq = SEQ66[GID]
key66 = {}
for s in np.unique(SEQ66):
    for jj, g in enumerate(np.flatnonzero(SEQ66 == s)): key66[(int(s), jj)] = int(g)

def remap(det, gid_of_frame=None):
    """keep rows of the selected frames, relabel frame id to 0..N-1"""
    f = det[:, 0].astype(int)
    if gid_of_frame is not None: f = gid_of_frame[f]
    ok = (f < len(new_of)) & (new_of[np.minimum(f, len(new_of) - 1)] >= 0)
    d = det[ok].copy(); d[:, 0] = new_of[f[ok]]; return d

gt66 = Z0['gt'].astype(np.float64); gtN = remap(gt66)
assert len(np.unique(gtN[:, 0])) <= N
cells = {}; M = {}; cols = None
for m in MODELS:
    Z = np.load(f'{E66}/dets-{m}.npz'); Y = np.load(f'{E51}/dets-{m}.npz'); X = np.load(f'{E71}/dets-{m}.npz')
    assert np.allclose(Y['gt'].astype(np.float64), gt66, equal_nan=True) and np.allclose(Z['gt'], gt66, equal_nan=True)
    sx = X['seq']; lx = np.zeros(len(sx), int)
    for s in np.unique(sx): k = np.flatnonzero(sx == s); lx[k] = np.arange(len(k))
    g_of_x = np.array([key66[(int(a), int(b))] for a, b in zip(sx, lx)])
    D = {'pooled': remap(Y['det'].astype(np.float64))}
    for h in [int(h) for h in Z['hnominal']]: D[f'H{h}'] = remap(Z[f'det_h{h}'].astype(np.float64))
    D['H21x'] = remap(X['det_h21'].astype(np.float64), g_of_x)      # E71 recomputation of H=21 (regression column)
    for h in HX: D[f'H{h}'] = remap(X[f'det_h{h}'].astype(np.float64), g_of_x)
    order_cols = ['pooled'] + [f'H{h}' for h in sorted(int(c[1:]) for c in D if c not in ('pooled', 'H21x'))] + ['H21x']
    cols = order_cols; M[m] = {}
    for c in cols:
        cells[(m, c)] = Cell(Scorer(D[c], gtN)); M[m][c] = cells[(m, c)].ap(np.ones(N))
    print('built', m, {c: round(M[m][c], 2) for c in cols}, flush=True)
mcols = [c for c in cols if c != 'H21x']
rng = np.random.default_rng(SEED); useq = np.unique(seq); inseq = {s: np.flatnonzero(seq == s) for s in useq}
draws = np.zeros((B, len(MODELS), len(cols)))
for b in range(B):
    w = np.zeros(N)
    for i in rng.integers(0, len(useq), len(useq)): w[inseq[useq[i]]] += 1
    for i, m in enumerate(MODELS):
        for j, c in enumerate(cols): draws[b, i, j] = cells[(m, c)].ap(w)
out = dict(models=MODELS, cols=cols, n_frames=int(N), n_seq=int(len(useq)), B=B, seed=SEED, map=M, ci={}, order={}, gap={}, pair_sign={},
           kendall_vs_pooled={}, rank_repro={}, h21_recompute_diff={m: M[m]['H21x'] - M[m]['H21'] for m in MODELS})
for j, c in enumerate(cols):
    pt = np.array([M[m][c] for m in MODELS]); ptord = tuple(np.argsort(-pt))
    out['order'][c] = [MODELS[i] for i in ptord]
    out['kendall_vs_pooled'][c] = kendall([M[m]['pooled'] for m in MODELS], list(pt))
    out['rank_repro'][c] = float(np.mean([tuple(np.argsort(-draws[b, :, j])) == ptord for b in range(B)]))
    for i, m in enumerate(MODELS):
        lo, hi = np.percentile(draws[:, i, j], [2.5, 97.5]); out['ci'].setdefault(m, {})[c] = [float(lo), float(hi)]
    for a, bb in itertools.combinations(range(len(MODELS)), 2):
        g = draws[:, a, j] - draws[:, bb, j]; pg = pt[a] - pt[bb]; lo, hi = np.percentile(g, [2.5, 97.5])
        k = f'{MODELS[a]}-{MODELS[bb]}'
        out['gap'].setdefault(k, {})[c] = [float(pg), float(lo), float(hi)]
        out['pair_sign'].setdefault(k, {})[c] = float(np.mean(np.sign(g) == np.sign(pg)))
# crossing: RVT-b minus S5-B (if both present)
if 'rvt-b' in MODELS and 's5vit-base' in MODELS:
    k = 'rvt-b-s5vit-base'; hs = [int(c[1:]) for c in mcols if c != 'pooled']
    gaps = [out['gap'][k][f'H{h}'][0] for h in hs]; sgn = [np.sign(g) for g in gaps]
    cross = None
    for a in range(len(hs) - 1):
        if gaps[a] < 0 <= gaps[a + 1]: cross = (hs[a], hs[a + 1], hs[a] + (hs[a + 1] - hs[a]) * (-gaps[a]) / (gaps[a + 1] - gaps[a]))
    out['crossing_rvt_b_over_s5_base'] = dict(H=hs, gap=gaps, first_sign_change=cross)
os.makedirs(E71, exist_ok=True)
json.dump(out, open(f'{E71}/results.json', 'w'), indent=1); np.save(f'{E71}/boot_draws.npy', draws)
L = ['# E71 Support-Conditioned AP at H = 1..80 (mAP x100, all labelled boxes, delta=0)', '',
     f'{N} stratified frames (r+1 >= 80) from {len(useq)} sequences, bootstrap B={B} over sequences; H21x = E71 recomputation of H=21', '',
     '| model | ' + ' | '.join(cols) + ' |', '|---|' + '--:|' * len(cols)]
for m in MODELS: L.append(f'| {m} | ' + ' | '.join(f"{M[m][c]:.2f} [{out['ci'][m][c][0]:.2f}, {out['ci'][m][c][1]:.2f}]" for c in cols) + ' |')
L += ['', '| column | ordering (best to worst) | Kendall tau vs pooled | P(ordering reproduces) |', '|---|---|--:|--:|']
for c in cols: L.append(f"| {c} | {' > '.join(out['order'][c])} | {out['kendall_vs_pooled'][c]:+.2f} | {out['rank_repro'][c]:.2f} |")
L += ['', '| pair (a-b) | ' + ' | '.join(cols) + ' |', '|---|' + '--:|' * len(cols)]
for k, v in out['gap'].items(): L.append(f'| {k} | ' + ' | '.join(f"{v[c][0]:+.2f} [{v[c][1]:+.2f}, {v[c][2]:+.2f}] ({out['pair_sign'][k][c]:.2f})" for c in cols) + ' |')
if 'crossing_rvt_b_over_s5_base' in out: L += ['', 'crossing RVT-b over S5-B: ' + json.dumps(out['crossing_rvt_b_over_s5_base'])]
open(f'{E71}/tables.md', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
