"""E59 - the recurrent support centroid is not unidentified. It does not exist.

E42 occluded one 50 ms window at lag L, let the state propagate, and measured the relative
L2 change in the emitted state at the target step, for L = 0..19 over 576 samples. Its
reported consequence was that the influence-weighted centroid moved with the horizon instead
of converging: -161 ms at a 500 ms horizon, -299 ms at 1000 ms. The manuscript recorded that
as a limit of what had been measured.

It is not a limit of measurement. If the tail obeys I(L) = A L^-a with a < 1, then

    sum_L I(L)      ~ H^(1-a) / (1-a)          diverges
    sum_L L I(L)    ~ H^(2-a) / (2-a)          diverges faster

so the centroid over a horizon of H windows of width w is, to leading order,

    c(H) = -w H (1-a) / (2-a)                                             (*)

which is linear in H and has no limit. The centroid is then not an unmeasured quantity but
an undefined one, and no longer horizon suffices to pin it down. Any published "effective
temporal support" for such a detector is a statement about the horizon its author chose.

Three things are checked before that is claimed.

1. a is fitted on lags 1..9 only and used to *predict* lags 10..19, which the fit never saw.
   An exponential tail I(L) = A exp(-L/s), the hypothesis under which the centroid does
   converge, is fitted on the same lags by the same weighted criterion and predicts the same
   held-out points. The comparison is out-of-sample for both.
2. The closed form (*) is compared against the horizon centroids computed directly from the
   measured influences, with no fitted quantity in them.
3. a < 1 is tested against its own uncertainty, propagated from E42's per-lag standard errors
   by a parametric bootstrap, since a >= 1 is exactly the hypothesis under which the paper's
   present wording would be right and this result would be wrong.
"""
import numpy as np, json

W = 50.0          # window width, ms
FIT = (1, 10)     # lags used for fitting: 1..9
HELD = (10, 20)   # lags held out: 10..19
NB = 20000

D = json.load(open('experiments/e42_recurrent_support/result_k19.json'))
I = np.array(D['influence']); S = np.array(D['sem']); L = np.arange(len(I))


def wls_power(y, e, lags):
    """log y = log A - a log L, weighted by the inverse variance of log y."""
    x = np.log(lags); ly = np.log(y); w = (y / e) ** 2
    X = np.vstack([np.ones_like(x), -x]).T
    Wm = np.diag(w)
    C = np.linalg.inv(X.T @ Wm @ X)
    b = C @ (X.T @ Wm @ ly)
    return float(b[0]), float(b[1]), C          # logA, a, cov


def wls_exp(y, e, lags):
    x = lags.astype(float); ly = np.log(y); w = (y / e) ** 2
    X = np.vstack([np.ones_like(x), -x]).T
    Wm = np.diag(w)
    b = np.linalg.inv(X.T @ Wm @ X) @ (X.T @ Wm @ ly)
    return float(b[0]), float(b[1])             # logA, 1/s


def centroid(inf, H):
    """Influence-weighted centre of the support over the newest H windows, in ms."""
    k = np.arange(H); c = -(W / 2 + W * k)
    return float((inf[:H] * c).sum() / inf[:H].sum())


if __name__ == '__main__':
    fl = np.arange(*FIT); hl = np.arange(*HELD)
    lA, a, C = wls_power(I[fl], S[fl], fl)
    lB, r = wls_exp(I[fl], S[fl], fl)
    print(f"fitted on lags {fl[0]}..{fl[-1]} ({len(fl)} points), held out {hl[0]}..{hl[-1]}\n")
    print(f"  power law    I(L) = {np.exp(lA):.5f} * L^-{a:.4f}")
    print(f"  exponential  I(L) = {np.exp(lB):.5f} * exp(-L/{1/r:.3f})   (tail scale {1/r*W:.1f} ms)\n")

    pp = np.exp(lA) * hl.astype(float) ** (-a)
    pe = np.exp(lB) * np.exp(-r * hl)
    print(f"{'lag':>4}{'centre ms':>11}{'measured':>11}{'+-sem':>9}{'power':>10}{'exp':>10}"
          f"{'pow z':>8}{'exp z':>8}")
    for j, k in enumerate(hl):
        zp = (pp[j] - I[k]) / S[k]; ze = (pe[j] - I[k]) / S[k]
        print(f"{k:>4}{-(W/2+W*k):>11.0f}{I[k]:>11.5f}{S[k]:>9.5f}{pp[j]:>10.5f}{pe[j]:>10.5f}"
              f"{zp:>8.2f}{ze:>8.2f}")
    cp = float(np.sqrt(np.mean(((pp - I[hl]) / S[hl]) ** 2)))
    ce = float(np.sqrt(np.mean(((pe - I[hl]) / S[hl]) ** 2)))
    print(f"\n  held-out RMS z:  power law {cp:.2f}   exponential {ce:.2f}"
          f"   ({ce/cp:.1f}x worse)")
    print(f"  the exponential fit predicts the lag-19 influence as {pe[-1]:.2e}, "
          f"{I[19]/pe[-1]:.0f}x below the measured {I[19]:.5f}")

    lA2, a2, C2 = wls_power(I[1:], S[1:], L[1:])
    print(f"\nall lags 1..19:  a = {a2:.4f}")

    rng = np.random.default_rng(20260916)
    Y = I[None, 1:] + rng.standard_normal((NB, len(I) - 1)) * S[None, 1:]
    ok = (Y > 0).all(axis=1)
    A_ = np.array([wls_power(y, S[1:], L[1:])[1] for y in Y[ok][:NB]])
    lo, hi = np.percentile(A_, [2.5, 97.5])
    print(f"  parametric bootstrap ({ok.sum()} draws): a = {A_.mean():.4f} "
          f"[{lo:.4f}, {hi:.4f}], SE {A_.std(ddof=1):.4f}")
    print(f"  P(a >= 1) = {float((A_ >= 1).mean()):.5f}   "
          f"-> a < 1 at {(1 - a2) / A_.std(ddof=1):.1f} sigma")

    print(f"\ncentroid: closed form (*) against the measured influences")
    print(f"{'horizon ms':>11}{'windows':>9}{'measured':>11}{'predicted':>11}{'ratio':>8}")
    pr = []
    for H in (5, 10, 15, 20):
        cm = centroid(I, H)
        cf = -W * H * (1 - a2) / (2 - a2)
        pr.append((H * W, cm, cf))
        print(f"{H*W:>11.0f}{H:>9}{cm:>11.1f}{cf:>11.1f}{cm/cf:>8.3f}")
    g = (centroid(I, 20) / centroid(I, 10))
    # The assumption-free form of the claim: no fitted quantity enters this ratio. Under any
    # support with a finite centroid, c(2H)/c(H) -> 1 as H grows; it cannot sit near 2.
    Yr = I[None, :] + rng.standard_normal((NB, len(I))) * S[None, :]
    Yr = Yr[(Yr > 0).all(axis=1)]
    G = np.array([centroid(y, 20) / centroid(y, 10) for y in Yr])
    glo, ghi = np.percentile(G, [2.5, 97.5])
    print(f"\n  doubling the horizon multiplies the measured centroid by {g:.3f} "
          f"[{glo:.3f}, {ghi:.3f}] (a convergent support would give 1.000)")
    print(f"    that is {(g - 1) / G.std(ddof=1):.0f} sigma from 1, and no fitted quantity "
          f"enters it")
    print(f"  extrapolating (*): a 2 s horizon gives {-W*40*(1-a2)/(2-a2):.0f} ms, "
          f"a 5 s horizon {-W*100*(1-a2)/(2-a2):.0f} ms")

    frac = I[1:].sum() / I.sum()
    print(f"\n  share of measured influence outside the current window: {frac*100:.1f} %")
    json.dump({'ratio': float(g), 'ratio_lo': float(glo), 'ratio_hi': float(ghi),
               'ratio_se': float(G.std(ddof=1)), 'a_fit_1_9': a, 'a_all': a2, 'a_se': float(A_.std(ddof=1)),
               'a_lo': float(lo), 'a_hi': float(hi), 'p_ge_1': float((A_ >= 1).mean()),
               'rmsz_power': cp, 'rmsz_exp': ce, 'exp_scale_ms': float(W / r),
               'centroids': [{'horizon_ms': h, 'measured': m, 'predicted': p} for h, m, p in pr],
               'outside_current_window': float(frac)},
              open('experiments/e42_recurrent_support/tail.json', 'w'), indent=1)
    print("\nWROTE experiments/e42_recurrent_support/tail.json")
