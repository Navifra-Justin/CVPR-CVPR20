"""E56e - do the four speed strata collapse onto one curve once delta is scaled by speed?

E56a's docstring names three questions the wide sweep feeds. E56b and E56c answered the first
two. This is the third, and the answer is more interesting than the question: the obvious
rescaling fails, and understanding why it fails removes an escape hatch from the paper's
central claim.

THE OBVIOUS RESCALING, AND WHY ONE WOULD EXPECT IT TO WORK

The displacement intervention depends on delta and v only through their product, so

    mAP(delta ; v)  ==  mAP(k*delta ; v/k)       exactly.

The scale-free per-box quantity is r = |v| / sqrt(w*h), box-widths of motion per second
(E57); a delta-second timing error moves a box delta*r box-widths, and an IoU matcher sees
box-widths and nothing else. So if a stratum's loss curve

    L(delta) = 1 - mAP(delta) / mAP(0)

were a consequence of its composition, plotting L against delta * r_median(stratum) would put
all four strata on one curve. Gen1's strata span a factor of 9 in r_median, which is a lot of
lever arm for a test.

WHAT HAPPENS

It does not collapse. It anti-collapses: rescaling by the median makes the strata three times
MORE dispersed than leaving delta in milliseconds. No fixed quantile of r fixes it either -
the best single quantile is the 85th, and it is still worse than not rescaling at all. The
raw fact underneath is that D, the delta at which a stratum loses 5 % of its mAP, is 95, 85,
61 and 67 ms across strata whose median displacement rates differ by 9x, and is not even
monotone in speed.

WHY, AND THE MODEL THAT DOES COLLAPSE

Because mAP is not an average over boxes; it is a threshold on each box. Take the crudest
possible model: a box drops its match once it is displaced past some fixed number of
box-widths d*, and is unaffected before that. Then

    L(delta) = P(r > d*/delta)     =>     D(L=p) = d* / Q_{1-p}(r),

and the scale-setter is the (1-p) QUANTILE of r, not its median. The quantile must match the
loss level being read off. That is the one-parameter prediction this script tests, and with
it the strata do collapse: at the 5 % level, D * Q_95(r) = 0.063 +- 0.003 box-widths across
three strata and five checkpoints, a coefficient of variation of 0.042 against 0.209 for no
rescaling and 0.599 for the median.

d* = 0.063 box-widths is also the right number on its own terms. Displacing a square box by a
fraction d of its width along an axis gives IoU = (1-d)/(1+d), so d* = 0.063 is the
displacement that breaks a match at IoU 0.88 - inside the 0.5:0.05:0.95 range this mAP
averages over, near its upper end, which is exactly where a 5 % loss should first bite.

WHAT IT MEANS FOR THE PAPER

The escape hatch it closes: a reader can grant that the 23.81 ms correction moves Gen1's mAP
by 0.0004 and still say that this is a fact about Gen1's slow objects rather than about
benchmarks, so a faster benchmark would resolve timing fine. The measurement says otherwise.
Timing resolution is bought from the UPPER TAIL of the displacement-rate distribution, and a
tail is the most expensive thing in a dataset to buy: restricting Gen1 to its fastest stratum
multiplies Q_95(r) by 2.5 and so improves the resolvable timing by 2.5x, while costing a
factor of 83 in sample size (27943 boxes -> 337). Resolution improves as the quantile, the
standard error as 1/sqrt(n). Stratifying for speed loses that race, which is why the paper's
argument does not depend on finding a faster benchmark.
"""
import json, numpy as np

SWEEP = 'experiments/e56_resolving/wide_sweep.json'
DUMP = 'experiments/e51_ranking/dets-rvt-t.npz'
OUT = 'experiments/e56_resolving/collapse.json'
LEVELS = [0.05, 0.10, 0.25]
STRATA = [('all moving', None, None), ('10-25 px/s', 10., 25.),
          ('25-50 px/s', 25., 50.), ('>50 px/s', 50., 1e9)]
NAMES = [n for n, _, _ in STRATA]
FIXEDQ = [50, 60, 70, 75, 80, 85, 90, 95, 97, 99]


def r_by_stratum():
    """r = |v|/sqrt(w*h) on exactly the boxes Scorer.evaluate keeps for each stratum."""
    G = np.load(DUMP)['gt'].astype(np.float64)
    w = G[:, 3] - G[:, 1]; h = G[:, 4] - G[:, 2]
    sp = np.hypot(G[:, 6], G[:, 7])
    hv = np.isfinite(sp) & (w > 0) & (h > 0)
    r = np.where(hv, sp / np.sqrt(np.maximum(w * h, 1e-9)), np.nan)
    out = {}
    for nm, lo, hi in STRATA:
        m = hv if lo is None else (hv & (sp >= lo) & (sp < hi))
        out[nm] = r[m]
    return out


def cross(d, L, p):
    """|delta| where L first reaches p, interpolated, averaged over the two signs.

    nan on a side that never reaches p inside the swept range, so an unattained level is
    visibly absent rather than silently extrapolated off the end of the sweep.
    """
    got = []
    for sgn in (-1, +1):
        m = (np.sign(d) == sgn) | (d == 0)
        x = np.abs(d[m]); y = L[m]
        o = np.argsort(x); x, y = x[o], y[o]
        hit = np.flatnonzero(y >= p)
        if not len(hit) or hit[0] == 0:
            got.append(np.nan); continue
        i = hit[0]
        got.append(x[i - 1] + (p - y[i - 1]) * (x[i] - x[i - 1]) / (y[i] - y[i - 1])
                   if y[i] > y[i - 1] else x[i])
    return float(np.nanmean(got)) if np.isfinite(got).any() else float('nan')


def cv(v):
    v = np.asarray([x for x in v if np.isfinite(x)], dtype=float)
    return float(v.std(ddof=1) / v.mean()) if len(v) > 1 else float('nan')


if __name__ == '__main__':
    S = json.load(open(SWEEP))
    R = r_by_stratum()
    models = list(S['curves'])

    # D(model, stratum, level), the raw material for everything below
    D = {m: {nm: {p: cross(np.array(S['curves'][m][nm]['deltas_ms'], dtype=float),
                           1 - np.array(S['curves'][m][nm]['map'], dtype=float) /
                           np.array(S['curves'][m][nm]['map'], dtype=float)[
                               int(np.argmin(np.abs(np.array(S['curves'][m][nm]['deltas_ms']))))],
                           p) for p in LEVELS} for nm in NAMES} for m in models}

    print('the r distribution per stratum (E51 ground truth, the boxes the scorer keeps)')
    print(f"{'stratum':<12s} {'n':>6s} {'median':>8s} {'Q75':>7s} {'Q90':>7s} {'Q95':>7s} "
          f"{'SD(ln r)':>9s}")
    for nm in NAMES:
        x = R[nm]; xp = x[x > 0]
        print(f"{nm:<12s} {len(x):6d} {np.median(x):8.4f} {np.percentile(x, 75):7.4f} "
              f"{np.percentile(x, 90):7.4f} {np.percentile(x, 95):7.4f} "
              f"{np.std(np.log(xp)):9.3f}")

    print('\n1. D, the |delta| at which each stratum loses p of its mAP (ms)')
    print(f"   {'model':<12s} {'level':>6s} " + " ".join(f'{nm:>12s}' for nm in NAMES) + '   CV')
    for m in models:
        for p in LEVELS:
            v = [D[m][nm][p] for nm in NAMES]
            print(f"   {m:<12s} {p:6.2f} " + " ".join(f'{x:12.1f}' for x in v)
                  + f"  {cv(v):.3f}")

    print('\n2. does any FIXED quantile of r collapse them?  (mean CV over 5 checkpoints)')
    print(f"   {'scale-setter':<16s} " + " ".join(f'L={p:<6.2f}' for p in LEVELS))
    fixed = {}
    for q in FIXEDQ:
        qs = {nm: float(np.percentile(R[nm], q)) for nm in NAMES}
        row = [float(np.mean([cv([D[m][nm][p] * qs[nm] for nm in NAMES]) for m in models]))
               for p in LEVELS]
        fixed[q] = row
        print(f"   {'x Q_%d(r)' % q:<16s} " + " ".join(f'{v:8.3f}' for v in row))
    raw = [float(np.mean([cv([D[m][nm][p] for nm in NAMES]) for m in models])) for p in LEVELS]
    print(f"   {'no rescaling':<16s} " + " ".join(f'{v:8.3f}' for v in raw)
          + '   <- every fixed quantile is worse than this')

    print('\n3. the LEVEL-MATCHED quantile: D(L=p) x Q_{1-p}(r), which the threshold model')
    print('   predicts is the constant d*, the box-widths of displacement that break a match')
    print(f"   {'model':<12s} {'level':>6s} " + " ".join(f'{nm:>12s}' for nm in NAMES)
          + f"  {'CV4':>6s} {'CV3':>6s}")
    matched = {}
    for p in LEVELS:
        qs = {nm: float(np.percentile(R[nm], 100 * (1 - p))) for nm in NAMES}
        c4, c3, allv = [], [], []
        for m in models:
            prod = [D[m][nm][p] * qs[nm] * 1e-3 for nm in NAMES]
            c4.append(cv(prod)); c3.append(cv(prod[:3])); allv += prod[:3]
            print(f"   {m:<12s} {p:6.2f} " + " ".join(f'{x:12.4f}' for x in prod)
                  + f"  {c4[-1]:6.3f} {c3[-1]:6.3f}")
        d_star = float(np.mean(allv)); d_sd = float(np.std(allv, ddof=1))
        iou = (1 - d_star) / (1 + d_star)
        matched[p] = dict(q={k: qs[k] for k in qs}, cv4=float(np.mean(c4)),
                          cv3=float(np.mean(c3)), d_star=d_star, d_sd=d_sd, iou_at_d=iou)
        print(f"   {'':<12s} {'mean':>6s} " + ' ' * 52
              + f"  {np.mean(c4):6.3f} {np.mean(c3):6.3f}")
        print(f"     -> d* = {d_star:.4f} +- {d_sd:.4f} box-widths, which for a square box "
              f"breaks a match at IoU {iou:.3f}")

    print('\n4. the cost of buying resolution from the tail')
    q95 = {nm: float(np.percentile(R[nm], 95)) for nm in NAMES}
    base = NAMES[0]
    print(f"   {'stratum':<12s} {'n':>6s} {'Q95(r)':>8s} {'resolution':>11s} {'1/sqrt(n)':>10s}"
          f" {'net':>7s}")
    cost = {}
    for nm in NAMES:
        gain = q95[nm] / q95[base]
        noise = np.sqrt(len(R[base]) / len(R[nm]))
        cost[nm] = dict(n=len(R[nm]), q95=q95[nm], resolution_gain=float(gain),
                        se_inflation=float(noise), net=float(gain / noise))
        print(f"   {nm:<12s} {len(R[nm]):6d} {q95[nm]:8.4f} {gain:10.2f}x {noise:9.2f}x"
              f" {gain / noise:6.2f}x")
    print('   resolution improves as the quantile, the standard error as 1/sqrt(n);')
    print('   every stratification of Gen1 loses that race.')

    json.dump(dict(r_summary={nm: dict(n=len(R[nm]), median=float(np.median(R[nm])),
                                       q75=float(np.percentile(R[nm], 75)),
                                       q90=float(np.percentile(R[nm], 90)),
                                       q95=float(np.percentile(R[nm], 95)),
                                       sd_log=float(np.std(np.log(R[nm][R[nm] > 0]))))
                              for nm in NAMES},
                   levels=LEVELS,
                   D_ms={m: {nm: {f'{p:.2f}': D[m][nm][p] for p in LEVELS} for nm in NAMES}
                         for m in models},
                   cv_no_rescaling={f'{p:.2f}': raw[i] for i, p in enumerate(LEVELS)},
                   cv_fixed_quantile={str(q): {f'{p:.2f}': fixed[q][i]
                                               for i, p in enumerate(LEVELS)} for q in FIXEDQ},
                   matched_quantile={f'{p:.2f}': matched[p] for p in LEVELS},
                   tail_cost=cost), open(OUT, 'w'), indent=1)
    print('\nWROTE', OUT)
