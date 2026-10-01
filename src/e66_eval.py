"""E66 evaluation: Support-Conditioned AP.

Inputs : experiments/e66_fixedH/dets-<model>.npz  (src/e66_fixedH_dump.py, all five checkpoints)
         experiments/e51_ranking/dets-<model>.npz (released protocol, "pooled")
Outputs: experiments/e66_fixedH/results.json, tables.md

 1. common frames  = frames whose H_forced equals H_nominal for every H (21 windows of
    history exist); every model is scored on exactly these frames for every condition.
 2. mAP (all labelled boxes, delta = 0, the E58e instrument) per model x {released-pooled,
    H=1,5,10,21}; the released-pooled column is scored on the same common frames, and on all
    frames as a side column.
 3. rankings by column, Kendall tau of each H ranking against the pooled ranking.
 4. sequence-cluster bootstrap (resample validation sequences, same draw for every model and
    column -> paired): CI of every mAP, CI of every pairwise gap, and the rank reproduction
    rate = share of draws whose full ordering equals the point ordering, plus the share of
    draws in which each pair keeps its point-estimate sign.

Env: B (bootstrap draws, default 200), SEED, ONLY (comma list of model names)
"""
import numpy as np, json, os, sys, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e56_eval import Scorer

ROOT = os.environ.get('E66_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E66 = os.path.join(ROOT, 'experiments/e66_fixedH'); E51 = os.path.join(ROOT, 'experiments/e51_ranking')
MODELS = ['rvt-t', 'rvt-s', 'rvt-b', 's5vit-small', 's5vit-base']
if os.environ.get('ONLY'): MODELS = os.environ['ONLY'].split(',')
B = int(os.environ.get('B', '200')); NW = int(os.environ.get('NW', '1'))
SEED = int(os.environ.get('SEED', '20261001'))
OUT = os.environ.get('OUTDIR', E66)

THRS = np.arange(0.5, 0.96, 0.05)
_S = {}


class Cell:
    """One (model, column): per-frame matching done once with the E56 matching rules at delta=0 and
    every labelled box (require_velocity=False), stored flat so that any frame multiset (a bootstrap
    draw) is a weight vector. ap(w) equals Scorer.evaluate(frames with multiplicities w); the point
    estimate is checked against Scorer.evaluate in main()."""

    def __init__(self, sc):
        from e56_eval import iou_mat
        self.cls = {}
        for c in sc.CLASSES:
            fr = []; scr = []; fl = []; npos = np.zeros(sc.NF)
            for fi in range(sc.NF):
                G = np.array([r[1:5] for r, hv, sp in sc.gt_by[fi] if int(r[5]) == c]).reshape(-1, 4)
                npos[fi] = len(G)
                D = [r for r in sc.det_by[fi] if int(r[6]) == c]
                if not D: continue
                D = np.array(D); D = D[np.argsort(-D[:, 5])]
                IM = iou_mat(D[:, 1:5], G); f = np.zeros((len(THRS), len(D)))
                for ti, t in enumerate(THRS):
                    used = np.zeros(len(G), dtype=bool)
                    for di in range(len(D)):
                        r = IM[di]; cand = (~used) & (r >= t)
                        if not cand.any(): continue
                        j = int(np.flatnonzero(cand)[np.argmax(r[cand])]); used[j] = True; f[ti, di] = 1.0
                fr.append(np.full(len(D), fi)); scr.append(D[:, 5]); fl.append(f)
            if not scr: continue
            S = np.concatenate(scr); o = np.argsort(-S, kind='stable')
            self.cls[c] = (np.concatenate(fr)[o], S[o], np.concatenate(fl, axis=1)[:, o], npos)

    def ap(self, w):
        """w: per-frame multiplicity (length NF)."""
        out = []
        for c, (fr, S, F, npos) in self.cls.items():
            ww = w[fr]; np_ = float((w * npos).sum())
            ctp = np.cumsum(F * ww, axis=1); cfp = np.cumsum((1 - F) * ww, axis=1)
            rec = ctp / max(np_, 1); prec = ctp / np.maximum(ctp + cfp, 1e-9)
            aps = []
            for ti in range(len(THRS)):
                mp = np.concatenate([[0], prec[ti], [0]]); mr = np.concatenate([[0], rec[ti], [1]])
                mp = np.maximum.accumulate(mp[::-1])[::-1]
                k = np.where(mr[1:] != mr[:-1])[0]
                aps.append(float(((mr[k + 1] - mr[k]) * mp[k + 1]).sum()))
            out.append(np.mean(aps))
        return float(np.mean(out)) * 100


def build(path_e66, path_e51):
    Z = np.load(path_e66); HS = [int(h) for h in Z['hnominal']]
    hf = Z['hforced']; common = np.flatnonzero((hf == np.array(HS)[None]).all(1) & Z['done'])
    gt = Z['gt'].astype(np.float64)
    sc = {}
    for h in HS: sc[f'H{h}'] = Scorer(Z[f'det_h{h}'].astype(np.float64), gt)
    if path_e51:
        Y = np.load(path_e51); g51 = Y['gt'].astype(np.float64)
        assert g51.shape == gt.shape and np.allclose(g51, gt, equal_nan=True), 'GT differs from e51'
        sc['pooled'] = Scorer(Y['det'].astype(np.float64), g51)
    return sc, common, Z['seq'], HS, gt


def kendall(a, b):
    n = len(a); s = 0
    if n < 2: return float("nan")
    for i, j in itertools.combinations(range(n), 2):
        s += np.sign(a[i] - a[j]) * np.sign(b[i] - b[j])
    return s / (n * (n - 1) / 2)


def main():
    sc0, common, seq, HS, gt = build(f'{E66}/dets-{MODELS[0]}.npz', f'{E51}/dets-{MODELS[0]}.npz')
    cols = ['pooled'] + [f'H{h}' for h in HS]
    # every model must share frame set, sequence ids and ground truth
    for m in MODELS[1:]:
        Z = np.load(f'{E66}/dets-{m}.npz')
        assert np.array_equal(Z['seq'], seq) and np.array_equal(Z['ri'], np.load(f'{E66}/dets-{MODELS[0]}.npz')['ri']), m
        assert np.allclose(Z['gt'], gt, equal_nan=True), m
    nF = len(seq); allfr = np.flatnonzero(np.load(f'{E66}/dets-{MODELS[0]}.npz')['done'])
    print(f'{nF} frames, {len(common)} common (H_forced == H_nominal for all H={HS}), '
          f'{len(allfr)-len(common)} excluded', flush=True)
    from e56_eval import Scorer
    cells = {}; M = {}
    for m in MODELS:
        sc, _, _, _, _ = build(f'{E66}/dets-{m}.npz', f'{E51}/dets-{m}.npz')
        wc = np.zeros(nF); wc[common] = 1; wa = np.zeros(nF); wa[allfr] = 1
        M[m] = {}
        for c in cols:
            cells[(m, c)] = Cell(sc[c]); M[m][c] = cells[(m, c)].ap(wc)
            ref = sc[c].evaluate(0.0, frames=common, require_velocity=False) * 100
            # fast path == E56 Scorer up to tie-breaking.  The detection scores are float32 and many are
            # exactly equal across frames; the fast path orders ties by a stable global sort, so a few
            # tied detections can swap places in the cumulative curves.  Observed differences are 3e-8
            # (rvt-s pooled) to 5e-6 (rvt-b H10) on the 0-100 scale; a real disagreement in matching
            # or in the frame set moves AP by 1e-2 or more.  The tolerance is 1e-4 and the largest
            # difference is printed after the loop.
            maxdiff = max(globals().get('_MAXDIFF', 0.0), abs(M[m][c] - ref)); globals()['_MAXDIFF'] = maxdiff
            assert abs(M[m][c] - ref) < 1e-4, (m, c, M[m][c], ref)
        pooled_all_m = cells[(m, 'pooled')].ap(wa)
        M[m]['_pooled_all'] = pooled_all_m
        print(f'  built {m}  (max |fast - Scorer| so far {globals().get("_MAXDIFF", 0.0):.2e})', flush=True)
    pooled_all = {m: M[m].pop('_pooled_all') for m in MODELS}
    order = {c: [MODELS[i] for i in np.argsort([-M[m][c] for m in MODELS])] for c in cols}
    tau = {c: kendall([M[m]['pooled'] for m in MODELS], [M[m][c] for m in MODELS]) for c in cols}
    # bootstrap over sequences (paired: one draw serves every model and column)
    rng = np.random.default_rng(SEED); useq = np.unique(seq[common])
    sid = {s_: i for i, s_ in enumerate(useq)}
    cnt = np.zeros((len(useq), nF))
    draws = np.zeros((B, len(MODELS), len(cols)))
    inseq = {s_: common[seq[common] == s_] for s_ in useq}
    for b in range(B):
        pick = rng.integers(0, len(useq), len(useq))
        w = np.zeros(nF)
        for i in pick: w[inseq[useq[i]]] += 1
        for i, m in enumerate(MODELS):
            for j, c in enumerate(cols): draws[b, i, j] = cells[(m, c)].ap(w)
        if (b + 1) % 10 == 0: print(f'  boot {b+1}/{B}', flush=True)
    out = dict(models=MODELS, cols=cols, hs=HS, n_frames=int(nF), n_common=int(len(common)),
               n_excluded=int(len(allfr) - len(common)), n_seq_common=int(len(useq)), B=B,
               map={m: M[m] for m in MODELS}, pooled_all_frames=pooled_all, order=order,
               kendall_vs_pooled=tau, ci={}, gap={}, rank_repro={}, pair_sign={})
    for j, c in enumerate(cols):
        for i, m in enumerate(MODELS):
            lo, hi = np.percentile(draws[:, i, j], [2.5, 97.5])
            out['ci'].setdefault(m, {})[c] = [float(lo), float(hi), float(draws[:, i, j].std(ddof=1))]
        pt = np.array([M[m][c] for m in MODELS]); ptord = tuple(np.argsort(-pt))
        out['rank_repro'][c] = float(np.mean([tuple(np.argsort(-draws[b, :, j])) == ptord for b in range(B)]))
        for a, bb in itertools.combinations(range(len(MODELS)), 2):
            g = draws[:, a, j] - draws[:, bb, j]; pg = pt[a] - pt[bb]
            lo, hi = np.percentile(g, [2.5, 97.5])
            out['gap'].setdefault(f'{MODELS[a]}-{MODELS[bb]}', {})[c] = [float(pg), float(lo), float(hi)]
            out['pair_sign'].setdefault(f'{MODELS[a]}-{MODELS[bb]}', {})[c] = float(np.mean(np.sign(g) == np.sign(pg)))
    # does the ORDERING change between columns, beyond bootstrap noise: P(ordering at H equals pooled ordering)
    pj = cols.index('pooled'); pord = tuple(np.argsort(-np.array([M[m]['pooled'] for m in MODELS])))
    out['share_draws_ordering_equals_pooled_point_ordering'] = {
        c: float(np.mean([tuple(np.argsort(-draws[b, :, j])) == pord for b in range(B)])) for j, c in enumerate(cols)}
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(f'{OUT}/results.json', 'w'), indent=1)
    np.save(f'{OUT}/boot_draws.npy', draws)
    L = ['# E66 Support-Conditioned AP (mAP x100, all labelled boxes, delta=0)', '',
         f'common frames {len(common)} of {nF} ({len(allfr)-len(common)} excluded: fewer than {max(HS)} windows of history), '
         f'{len(useq)} sequences, bootstrap B={B} over sequences', '',
         '| model | ' + ' | '.join(cols) + ' | pooled (all frames) |', '|---|' + '--:|' * (len(cols) + 1)]
    for m in MODELS:
        L.append(f'| {m} | ' + ' | '.join(f"{M[m][c]:.2f} [{out['ci'][m][c][0]:.2f}, {out['ci'][m][c][1]:.2f}]" for c in cols)
                 + f' | {pooled_all[m]:.2f} |')
    L += ['', '| column | ordering (best to worst) | Kendall tau vs pooled | P(ordering reproduces its own point ordering) |',
          '|---|---|--:|--:|']
    for c in cols:
        L.append(f"| {c} | {' > '.join(order[c])} | {tau[c]:+.2f} | {out['rank_repro'][c]:.2f} |")
    L += ['', '| pair (a-b) | ' + ' | '.join(cols) + ' |', '|---|' + '--:|' * len(cols)]
    for k, v in out['gap'].items():
        L.append(f'| {k} | ' + ' | '.join(f"{v[c][0]:+.2f} [{v[c][1]:+.2f}, {v[c][2]:+.2f}] ({out['pair_sign'][k][c]:.2f})" for c in cols) + ' |')
    L.append('\nCells: point gap [95% cluster-bootstrap CI] (share of draws keeping the point sign).')
    open(f'{OUT}/tables.md', 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
