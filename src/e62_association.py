"""E62 - is the fitted output time an artifact of the association that produced its rows?

E27 fitted the vector lag model

    p - g  =  -tau * v  +  eps

on detections matched to ground truth AT THE NOMINAL LABEL TIME with a class-conditioned
greedy IoU gate of 0.3. External review #11 named the selection this can create: a detection
whose center is displaced along travel by a large tau has LESS nominal-time overlap with its
label, so the gate removes the very rows that would carry a large tau and pulls the estimate
toward zero. E27's own robustness sweep raised the gate to 0.5 and 0.7, which tightens the
same selection instead of relaxing it, so it cannot answer the objection.

This answers it three ways, all on CPU, from the detection dumps E51 already wrote:

  1. LOWER the gate, to 0.05 and 0.1 and 0.2, which admits exactly the displaced rows the
     objection says are missing.
  2. Replace greedy matching with a class-conditioned Hungarian assignment, which removes
     the order dependence of the greedy rule at every gate.
  3. Associate WITHOUT using nominal-time overlap at all: a class-conditioned Hungarian
     assignment on center distance, admitted out to a radius of RADIUS * sqrt(w*h). At
     RADIUS = 1.5 a box displaced by one and a half of its own widths still matches, so a
     row survives at any overlap including zero.

If tau is a selection artifact its estimate must move as the gate opens and as the
overlap requirement is dropped. The same regression, the same cluster-robust standard
errors clustered by sequence, and the same 90-degree-rotated velocity placebo are used
throughout, so only the association differs.

Reads experiments/e51_ranking/dets-rvt-t.npz (the same released checkpoint E27 used) and
experiments/e56_resolving/seqmap.json for the sequence of each frame. No GPU.
"""
import json, os, sys, numpy as np
from scipy.optimize import linear_sum_assignment

DUMP = os.environ.get('DUMP', 'experiments/e51_ranking/dets-rvt-t.npz')
OUT  = os.environ.get('OUT',  'experiments/e27_rows/association.json')
CONF = float(os.environ.get('CONF', '0.1'))      # E27's confidence threshold
RADIUS = 1.5                                      # box-widths, for the overlap-free rule

Z  = np.load(DUMP)
DET, GT = Z['det'].astype(np.float64), Z['gt'].astype(np.float64)
SEQ = np.zeros(int(GT[:, 0].max()) + 1, dtype=np.int32)
for i, s in enumerate(json.load(open('experiments/e56_resolving/seqmap.json'))):
    SEQ[s['start']:s['start'] + s['n']] = i


def iou_mat(A, B):
    x1 = np.maximum(A[:, None, 0], B[None, :, 0]); y1 = np.maximum(A[:, None, 1], B[None, :, 1])
    x2 = np.minimum(A[:, None, 2], B[None, :, 2]); y2 = np.minimum(A[:, None, 3], B[None, :, 3])
    it = np.clip(x2 - x1, 0, None) * np.clip(y2 - y1, 0, None)
    aa = (A[:, 2] - A[:, 0]) * (A[:, 3] - A[:, 1]); bb = (B[:, 2] - B[:, 0]) * (B[:, 3] - B[:, 1])
    return it / np.maximum(aa[:, None] + bb[None, :] - it, 1e-9)


def rows(rule, thr):
    """One row per matched (detection, labelled box) pair: residual, velocity, size, sequence."""
    d = DET[DET[:, 5] >= CONF]
    g = GT[np.isfinite(GT[:, 6])]                       # centered velocity required, as in E27
    out = []
    order_d = np.argsort(d[:, 0], kind='stable'); d = d[order_d]
    bd = np.searchsorted(d[:, 0], np.arange(SEQ.size + 1))
    order_g = np.argsort(g[:, 0], kind='stable'); g = g[order_g]
    bg = np.searchsorted(g[:, 0], np.arange(SEQ.size + 1))
    for f in range(SEQ.size):
        D = d[bd[f]:bd[f + 1]]; G = g[bg[f]:bg[f + 1]]
        if not len(D) or not len(G): continue
        for c in np.unique(G[:, 5]):
            Dc = D[D[:, 6] == c]; Gc = G[G[:, 5] == c]
            if not len(Dc) or not len(Gc): continue
            gw = Gc[:, 3] - Gc[:, 1]; gh = Gc[:, 4] - Gc[:, 2]
            if rule == 'center':
                pc = np.column_stack([(Dc[:, 1] + Dc[:, 3]) / 2, (Dc[:, 2] + Dc[:, 4]) / 2])
                gc = np.column_stack([(Gc[:, 1] + Gc[:, 3]) / 2, (Gc[:, 2] + Gc[:, 4]) / 2])
                dist = np.linalg.norm(pc[:, None] - gc[None], axis=2)
                lim = thr * np.sqrt(gw * gh)[None, :]
                Q = np.where(dist <= lim, 1.0 - dist / np.maximum(lim, 1e-9), -1.0)
            else:
                Q = np.where((M := iou_mat(Dc[:, 1:5], Gc[:, 1:5])) >= thr, M, -1.0)
            if rule == 'greedy':
                pairs = []; used_d = set(); used_g = set()
                for k in np.argsort(-Q, axis=None):
                    i, j = divmod(int(k), Q.shape[1])
                    if Q[i, j] < 0: break
                    if i in used_d or j in used_g: continue
                    used_d.add(i); used_g.add(j); pairs.append((i, j))
            else:
                ri, cj = linear_sum_assignment(-Q)
                pairs = [(i, j) for i, j in zip(ri, cj) if Q[i, j] >= 0]
            for i, j in pairs:
                px = (Dc[i, 1] + Dc[i, 3]) / 2; py = (Dc[i, 2] + Dc[i, 4]) / 2
                cx = (Gc[j, 1] + Gc[j, 3]) / 2; cy = (Gc[j, 2] + Gc[j, 4]) / 2
                out.append((px - cx, py - cy, Gc[j, 6], Gc[j, 7],
                            np.sqrt(gw[j] * gh[j]), SEQ[f],
                            gw[j], gh[j], cx, cy))
    return np.array(out) if out else np.zeros((0, 10))


def cluster_ols(X, y, gg):
    XtXi = np.linalg.inv(X.T @ X); b = XtXi @ (X.T @ y); r = y - X @ b
    meat = np.zeros((X.shape[1], X.shape[1]))
    for c in np.unique(gg):
        m = gg == c; u = X[m].T @ r[m]; meat += np.outer(u, u)
    G = len(np.unique(gg)); n, k = X.shape
    cov = XtXi @ meat @ XtXi * (G / max(G - 1, 1) * (n - 1) / max(n - k, 1))
    return b, np.sqrt(np.diag(cov))


def fit(R, use_size=True):
    """E27's stacked vector regression, verbatim in form: dx = -tau*vx - beta*(-vy) + ..."""
    dx, dy, vx, vy, s, gg = R[:, :6].T
    sp = np.hypot(vx, vy); m = sp > 0
    dx, dy, vx, vy, s, gg, sp = (a[m] for a in (dx, dy, vx, vy, s, gg, sp))
    ux, uy = vx / sp, vy / sp
    one = np.ones_like(vx); zero = np.zeros_like(vx)
    cx = [one, zero, vx, -vy]; cy = [zero, one, vy, vx]
    if use_size: cx.append(s * ux); cy.append(s * uy)
    X = np.vstack([np.column_stack(cx), np.column_stack(cy)])
    y = np.concatenate([dx, dy]); g2 = np.concatenate([gg, gg])
    b, se = cluster_ols(X, y, g2)
    return dict(n=int(m.sum()), tau_ms=-b[2] * 1e3, tau_se_ms=se[2] * 1e3,
                placebo_ms=-b[3] * 1e3, placebo_se_ms=se[3] * 1e3,
                med_speed=float(np.median(sp)))


def fit_full(R):
    """The REPORTED specification (E30 `perseq4`): per-sequence bias vectors plus the four
    geometric regressors, which is where the manuscript's tau comes from. Reproduced here so
    the association sweep is compared against the number the paper actually reports, not
    against the minimal fit."""
    dx, dy, vx, vy, s, gg, gw, gh, gcx, gcy = R.T
    sp = np.hypot(vx, vy); m = sp > 0
    dx, dy, vx, vy, s, gg, gw, gh, gcx, gcy, sp = (a[m] for a in
        (dx, dy, vx, vy, s, gg, gw, gh, gcx, gcy, sp))
    ux, uy = vx / sp, vy / sp; zero = np.zeros_like(vx)
    cx = [vx, -vy, s * ux, zero, zero, gcx, gw]
    cy = [vy,  vx, s * uy, gh,  gcy, zero, zero]
    u = np.unique(gg); Dm = (gg[:, None] == u[None, :]).astype(float)
    X = np.vstack([np.hstack([np.column_stack(cx), Dm, np.zeros_like(Dm)]),
                   np.hstack([np.column_stack(cy), np.zeros_like(Dm), Dm])])
    y = np.concatenate([dx, dy]); g2 = np.concatenate([gg, gg])
    b, se = cluster_ols(X, y, g2)
    return dict(n=int(m.sum()), tau_ms=-b[0] * 1e3, tau_se_ms=se[0] * 1e3,
                placebo_ms=-b[1] * 1e3, placebo_se_ms=se[1] * 1e3,
                med_speed=float(np.median(sp)))


if __name__ == '__main__':
    print(f"dump {DUMP}  conf>={CONF}  {len(DET)} detections  {len(GT)} labelled boxes\n")
    grid = ([('greedy', t) for t in (0.05, 0.1, 0.2, 0.3, 0.5)]
            + [('hungarian', t) for t in (0.05, 0.1, 0.2, 0.3, 0.5)]
            + [('center', r) for r in (0.5, 1.0, 1.5, 2.0)])
    res = {}
    print(f"{'association':<46}{'rows':>7}{'tau minimal':>17}{'tau reported spec':>21}")
    for rule, thr in grid:
        R = rows(rule, thr)
        if len(R) < 100: continue
        f = fit(R); ff = fit_full(R)
        lab = (f"IoU >= {thr:.2f}, {rule}" if rule != 'center'
               else f"center within {thr:.1f} box-widths, no overlap test")
        res[f'{rule}_{thr}'] = dict(rule=rule, thr=thr, label=lab, minimal=f, reported=ff)
        print(f"  {lab:<44}{f['n']:>7}{f['tau_ms']:>+9.2f} +-{f['tau_se_ms']:>4.2f}"
              f"{ff['tau_ms']:>+13.2f} +-{ff['tau_se_ms']:>4.2f}")
    t = np.array([v['reported']['tau_ms'] for v in res.values()])
    se = np.array([v['reported']['tau_se_ms'] for v in res.values()])
    tmin = np.array([v['minimal']['tau_ms'] for v in res.values()])
    span = [float(t.min()), float(t.max())]
    # An estimate that survives the objection is one whose spread across association rules is
    # small against its own standard error, and whose loosest rule is not systematically larger.
    lo = res['center_1.5']['reported']; base = res['greedy_0.3']['reported']
    print(f"\n  reported specification, across all {len(t)} association rules:"
          f" {span[0]:+.2f} to {span[1]:+.2f} ms"
          f"  (spread {span[1]-span[0]:.2f} ms, median SE {np.median(se):.2f} ms)")
    print(f"  minimal specification, same sweep:                {tmin.min():+.2f} to {tmin.max():+.2f} ms")
    print(f"  the gate the row table used, greedy IoU >= 0.3:   {base['tau_ms']:+.2f} +- {base['tau_se_ms']:.2f} ms"
          f"  on {base['n']} rows")
    print(f"  the rule that never tests overlap, r <= 1.5 w:    {lo['tau_ms']:+.2f} +- {lo['tau_se_ms']:.2f} ms"
          f"  on {lo['n']} rows ({lo['n']/base['n']:.2f}x)")
    print(f"  difference {lo['tau_ms']-base['tau_ms']:+.2f} ms, "
          f"{abs(lo['tau_ms']-base['tau_ms'])/max(base['tau_se_ms'],1e-9):.2f} of that gate's SE")
    every = all(abs(v['reported']['tau_ms']) < 2 * v['reported']['tau_se_ms'] for v in res.values())
    print(f"  consistent with zero under every rule (reported spec): {every}")
    cen = float(os.environ.get('CENTROID_MS', '23.81'))
    clears = sum(1 for v in res.values()
                 if cen - v['reported']['tau_ms'] > 2 * v['reported']['tau_se_ms'])
    print(f"  the {cen:.2f} ms ablation-sensitivity centroid stays more than 2 SE away from tau"
          f" under {clears} of {len(res)} rules")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(dict(conf=CONF, radius_rule='center distance <= thr * sqrt(w*h)',
                   span_ms=span, spread_ms=span[1] - span[0],
                   span_minimal_ms=[float(tmin.min()), float(tmin.max())],
                   median_se_ms=float(np.median(se)), all_within_2se=bool(every),
                   centroid_ms=cen, centroid_clears=int(clears), n_rules=len(res),
                   rows=res), open(OUT, 'w'), indent=1)
    print(f"\nWROTE {OUT}")
