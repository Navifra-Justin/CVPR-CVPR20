"""E71 sensitivity: Support-Conditioned AP at H = 1, 5, 10, 21 and pooled on ALL frames with r+1 >= 80 (the population the
3,000-frame sample of E71 is drawn from), from the full fixed-H dumps of E66.  No new model run: same detections, same Cell/Scorer,
same bootstrap scheme (sequence clusters, one draw for every model and column) as src/e66_eval.py and src/e71_eval.py.
Writes experiments/e71_h4080/population.json and population.md."""
import numpy as np, json, os, sys, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e66_eval import Cell, build, kendall
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E66 = f'{ROOT}/experiments/e66_fixedH'; E51 = f'{ROOT}/experiments/e51_ranking'; OUT = f'{ROOT}/experiments/e71_h4080'
MODELS = ['rvt-t', 'rvt-s', 'rvt-b', 's5vit-small', 's5vit-base']
B = 200; SEED = 20261002
sc0, common, seq, HS, gt = build(f'{E66}/dets-{MODELS[0]}.npz', f'{E51}/dets-{MODELS[0]}.npz')
Z0 = np.load(f'{E66}/dets-{MODELS[0]}.npz'); ri = Z0['ri']
pop = np.array([g for g in common if ri[g] + 1 >= 80]); nF = len(seq)
cols = ['pooled'] + [f'H{h}' for h in HS]
print(len(common), 'common;', len(pop), 'with r+1>=80;', len(np.unique(seq[pop])), 'sequences', flush=True)
cells = {}; M = {}
w = np.zeros(nF); w[pop] = 1
for m in MODELS:
    sc, _, _, _, _ = build(f'{E66}/dets-{m}.npz', f'{E51}/dets-{m}.npz'); M[m] = {}
    for c in cols:
        cells[(m, c)] = Cell(sc[c]); M[m][c] = cells[(m, c)].ap(w)
    print(m, {c: round(M[m][c], 2) for c in cols}, flush=True)
rng = np.random.default_rng(SEED); useq = np.unique(seq[pop]); inseq = {s: pop[seq[pop] == s] for s in useq}
draws = np.zeros((B, len(MODELS), len(cols)))
for b in range(B):
    ww = np.zeros(nF)
    for i in rng.integers(0, len(useq), len(useq)): ww[inseq[useq[i]]] += 1
    for i, m in enumerate(MODELS):
        for j, c in enumerate(cols): draws[b, i, j] = cells[(m, c)].ap(ww)
out = dict(models=MODELS, cols=cols, n_frames=int(len(pop)), n_seq=int(len(useq)), B=B, seed=SEED, map=M, ci={}, order={}, gap={}, pair_sign={},
           kendall_vs_pooled={}, rank_repro={})
for j, c in enumerate(cols):
    pt = np.array([M[m][c] for m in MODELS]); ptord = tuple(np.argsort(-pt))
    out['order'][c] = [MODELS[i] for i in ptord]
    out['kendall_vs_pooled'][c] = kendall([M[m]['pooled'] for m in MODELS], list(pt))
    out['rank_repro'][c] = float(np.mean([tuple(np.argsort(-draws[b, :, j])) == ptord for b in range(B)]))
    for i, m in enumerate(MODELS):
        out['ci'].setdefault(m, {})[c] = [float(x) for x in np.percentile(draws[:, i, j], [2.5, 97.5])]
    for a, bb in itertools.combinations(range(len(MODELS)), 2):
        g = draws[:, a, j] - draws[:, bb, j]; pg = pt[a] - pt[bb]; lo, hi = np.percentile(g, [2.5, 97.5])
        k = f'{MODELS[a]}-{MODELS[bb]}'
        out['gap'].setdefault(k, {})[c] = [float(pg), float(lo), float(hi)]
        out['pair_sign'].setdefault(k, {})[c] = float(np.mean(np.sign(g) == np.sign(pg)))
json.dump(out, open(f'{OUT}/population.json', 'w'), indent=1)
L = [f'# E71 sensitivity: all {len(pop)} frames with r+1 >= 80 in {len(useq)} sequences, H <= 21, B={B}', '',
     '| model | ' + ' | '.join(cols) + ' |', '|---|' + '--:|' * len(cols)]
for m in MODELS: L.append(f'| {m} | ' + ' | '.join(f"{M[m][c]:.2f} [{out['ci'][m][c][0]:.2f}, {out['ci'][m][c][1]:.2f}]" for c in cols) + ' |')
L += ['', '| column | ordering | tau vs pooled | repro |', '|---|---|--:|--:|']
for c in cols: L.append(f"| {c} | {' > '.join(out['order'][c])} | {out['kendall_vs_pooled'][c]:+.2f} | {out['rank_repro'][c]:.2f} |")
L += ['', '| pair | ' + ' | '.join(cols) + ' |', '|---|' + '--:|' * len(cols)]
for k, v in out['gap'].items(): L.append(f'| {k} | ' + ' | '.join(f"{v[c][0]:+.2f} [{v[c][1]:+.2f}, {v[c][2]:+.2f}]" for c in cols) + ' |')
open(f'{OUT}/population.md', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
