"""E56c - the timing difference Gen1's ordering can resolve, and the composition that changes it.

Two detectors that differ only in effective output time differ in their boxes by
(tau_i - tau_j) * v pixels. The metric registers that as a loss, so the ordering of a
leaderboard responds to a timing difference only once that loss exceeds the gap between the
two entries. Everything needed is in the measured sweep:

    L_i(D)  =  mAP_i(peak_i) - mAP_i(peak_i + D)     the AP cost of being off by D
    G_ij    =  mAP_i(0) - mAP_j(0)                   the published gap
    D*_ij   =  min { |D| : L_j(D) >= G_ij }          the timing difference that flips the pair

D* over adjacent pairs is the benchmark's rank-resolving timing difference. It is compared
against three fixed quantities: the 23.81 ms newest-window occlusion-sensitivity centroid,
the 50 ms input window, and the 1 ms spread of that centroid across the five released
checkpoints.

Because a timing error of D displaces a box by D * r box-widths, with r the motion-to-scale
ratio of E57, D* scales as 1/r: the same five checkpoints on a benchmark whose labels carry
c times Gen1's r resolve a timing difference c times smaller. The last block turns D* into the
composition a benchmark would need for the measured interval to reorder it, and reads off
where DSEC-Det's released labels sit against that requirement.
"""
import numpy as np, json, os, sys

SW = json.load(open('experiments/e56_resolving/wide_sweep.json'))
COMP = {d['name']: d for d in json.load(open('experiments/e56_resolving/composition.json'))}
BOOT = None
if os.path.exists('experiments/e56_resolving/bootstrap.json'):
    BOOT = json.load(open('experiments/e56_resolving/bootstrap.json'))
TAU = SW['tau_ms']
WINDOW_MS = 50.0
CENTROID_SPREAD_MS = 0.96          # E48: -23.76 to -24.72 ms over the five released checkpoints
OUT = 'experiments/e56_resolving/resolving.json'
MODELS = list(SW['curves'].keys())
STRATA = SW['strata']
R_OF = {'all moving': 'Gen1 (all moving)', '25-50 px/s': 'Gen1 (25-50 px/s)',
        '>50 px/s': 'Gen1 (>50 px/s)'}


def curve(m, s):
    c = SW['curves'][m][s]
    return np.array(c['deltas_ms'], float), np.array(c['map'], float) * 100.0


def peak(d, y):
    """Grid argmax, refined by the parabola through it and its two neighbours."""
    i = int(np.argmax(y))
    if 0 < i < len(y) - 1:
        a, b, c = y[i - 1], y[i], y[i + 1]
        den = a - 2 * b + c
        if den < 0:
            h = 0.5 * (a - c) / den
            if abs(h) <= 1:
                x = d[i] + h * (d[i + 1] - d[i] if h > 0 else d[i] - d[i - 1])
                return float(x), float(b - 0.25 * (a - c) * h)
    return float(d[i]), float(y[i])


def invert_loss(d, y, x0, y0, target):
    """Smallest |D| with mAP(x0+D) <= y0-target, linearly interpolated, each side separately."""
    out = {}
    for side, sel in (('late', d >= x0), ('early', d <= x0)):
        xs = d[sel]; ys = y[sel]
        o = np.argsort(np.abs(xs - x0)); xs = xs[o]; ys = ys[o]
        loss = y0 - ys
        hit = np.flatnonzero(loss >= target)
        if len(hit) == 0:
            out[side] = float('inf'); continue
        k = hit[0]
        if k == 0:
            out[side] = 0.0; continue
        l0, l1 = loss[k - 1], loss[k]
        f = 0.0 if l1 == l0 else (target - l0) / (l1 - l0)
        out[side] = float(abs(xs[k - 1] - x0) + f * (abs(xs[k] - x0) - abs(xs[k - 1] - x0)))
    out['min'] = min(out['late'], out['early'])
    return out


res = {'tau_ms': TAU, 'window_ms': WINDOW_MS, 'centroid_spread_ms': CENTROID_SPREAD_MS,
       'strata': {}}
for s in STRATA:
    peaks = {}; at0 = {}
    for m in MODELS:
        d, y = curve(m, s)
        px, py = peak(d, y)
        peaks[m] = (px, py)
        at0[m] = float(np.interp(0.0, d, y))
    order = sorted(MODELS, key=lambda m: -at0[m])
    pairs = []
    for a, b in zip(order[:-1], order[1:]):
        G = at0[a] - at0[b]
        d, y = curve(b, s)
        inv = invert_loss(d, y, peaks[b][0], peaks[b][1], G)
        pairs.append(dict(above=a, below=b, gap_pt=G, dstar_ms=inv['min'],
                          dstar_late_ms=inv['late'], dstar_early_ms=inv['early']))
    tight = min(pairs, key=lambda p: p['dstar_ms'])
    row = dict(order=order, map_at_zero_pt={m: at0[m] for m in MODELS},
               peak_ms={m: peaks[m][0] for m in MODELS},
               peak_pt={m: peaks[m][1] for m in MODELS},
               adjacent=pairs, dstar_ms=tight['dstar_ms'], tightest_pair=[tight['above'], tight['below']],
               dstar_over_tau=tight['dstar_ms'] / TAU,
               dstar_over_window=tight['dstar_ms'] / WINDOW_MS,
               dstar_over_spread=tight['dstar_ms'] / CENTROID_SPREAD_MS)
    if s in R_OF:
        row['r_median'] = COMP[R_OF[s]]['r_median']
        row['composition_needed_x'] = tight['dstar_ms'] / TAU
    res['strata'][s] = row

    print(f"\n=== {s} ===")
    print(f"  published order: {' > '.join(order)}")
    for p in pairs:
        print(f"    {p['above']:<12} > {p['below']:<12} gap {p['gap_pt']:6.3f} pt   "
              f"flips at a timing difference of {p['dstar_ms']:8.1f} ms "
              f"(early {p['dstar_early_ms']:.1f} / late {p['dstar_late_ms']:.1f})")
    print(f"  rank-resolving timing difference D* = {tight['dstar_ms']:.1f} ms"
          f"   = {tight['dstar_ms']/TAU:.1f} x the 23.81 ms centroid"
          f"   = {tight['dstar_ms']/WINDOW_MS:.1f} x the 50 ms window"
          f"   = {tight['dstar_ms']/CENTROID_SPREAD_MS:.0f} x the measured inter-checkpoint spread")

if BOOT is not None:
    print("\n=== against the benchmark's own noise ===")
    res['noise'] = {}
    for s in ['all moving', '25-50 px/s']:
        for m in MODELS:
            b = BOOT['per_model'][m][s]
            j = BOOT['deltas_ms'].index(-23.81)
            se_abs = b['se_map_pt'][0]; se_pair = b['se_dmap_pt'][j]; eff = abs(b['mean_dmap_pt'][j])
            d, y = curve(m, s); px, py = peak(d, y)
            r_pair = invert_loss(d, y, px, py, 2 * se_pair)['min']
            r_abs = invert_loss(d, y, px, py, 2 * se_abs)['min']
            res['noise'].setdefault(s, {})[m] = dict(
                se_map_pt=se_abs, se_dmap_pt=se_pair, effect_at_tau_pt=eff,
                resolve_paired_ms=r_pair, resolve_absolute_ms=r_abs)
            print(f"  {m:<13}{s:<12} SE(mAP) {se_abs:.3f} pt  SE(dmAP) {se_pair:.4f} pt  "
                  f"effect at 23.81 ms {eff:.4f} pt  ->  paired-resolvable from "
                  f"{r_pair:7.1f} ms, comparison-resolvable from {r_abs:8.1f} ms")

print("\n=== composition ===")
base = COMP['Gen1 (all moving)']['r_median']
need = res['strata']['all moving']['dstar_ms'] / TAU
print(f"  Gen1's ordering responds to 23.81 ms only at {need:.1f}x its own motion-to-scale ratio")
for k in ['Gen1 (25-50 px/s)', 'Gen1 (>50 px/s)', 'DSEC-Det (train)', 'DSEC-Det (test)']:
    c = COMP[k]['r_median'] / base
    print(f"    {k:<22} r = {COMP[k]['r_median']:.3f}/s = {c:6.2f}x Gen1   "
          f"{'reaches' if c >= need else 'short of'} the requirement ({c/need:.2f} of it)")
res['composition'] = {k: COMP[k]['r_median'] / base for k in COMP}
res['composition_needed_x'] = need
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(res, open(OUT, 'w'), indent=1)
print(f"\nWROTE {OUT}")
