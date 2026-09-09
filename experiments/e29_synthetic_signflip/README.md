# E29 — the forward-difference velocity manufactures a lag (2026-09-07)

## Why this exists

E21 and E24 both estimated the detector's output time by taking a track velocity from the
**forward** inter-label displacement and regressing the detection residual on it. E21
reported `+11.9 ms` (1.3 SE) and E24, on a wider row set with an acceleration regressor,
`+52.7 ms` (8.1 SE). Two estimates of one quantity that disagree by four times cannot both
be measurements of the detector.

The suspicion was that the estimator, not the detector, produces the number. A forward
difference

    v_f = (c_{k+1} - c_k) / dt

contains the label-centre noise `delta_k` with weight `-1/dt`. The residual being
regressed,

    dx = p_x - c_{k,x},

contains the same `delta_k` with weight `-1`. Their covariance is `+var(delta)/dt` **even
when the detector has no lag at all**. A backward difference carries `delta_k` with the
opposite sign and must produce the opposite artefact. A centered difference

    v_c = (c_{k+1} - c_{k-1}) / (dt_f + dt_b)

does not use `c_k` and is free of it.

That claim is about the estimator, so it can be tested without a detector.

## Construction

2000 synthetic tracks, 14 labels each on a 50 ms grid, quadratic motion. The simulated
detector reports the true position at `t - tau_true` plus its own 0.3 px error. The label
centres are corrupted with the noise **E28** measured on Gen1 itself, `sigma = 0.6515 px`.
The fit is the same stacked vector regression E27 uses, including the rotated-velocity
placebo.

## Result — arm A, `tau_true = 0`

| velocity | tau_hat | placebo |
|---|---|---|
| forward | **−5.64 ms** | −0.00 ms |
| backward | **+5.84 ms** | +0.03 ms |
| centered | **+0.00 ms** | +0.02 ms |

The detector in this arm has no lag whatsoever, so every non-zero entry is estimator
artefact. Three things have to hold if the mechanism is the shared `delta_k` term, and all
three do:

1. forward and backward are equal and opposite — their sum is `+0.20 ms`;
2. the closed form `-var(delta)/dt / var(v)` predicts `−5.63 ms` against a simulated
   `−5.64 ms`;
3. setting the label noise to zero collapses all three estimators to `+0.02 ms`.

The placebo — the velocity rotated by 90 degrees — stays at zero throughout, so it does
not absorb the artefact and remains a usable null in the real fit.

## Result — arm B, recovery and attenuation

| tau_true | tau_hat (centered) | ratio |
|---|---|---|
| +10.0 ms | +9.15 ms | 0.915 |
| +25.0 ms | +23.12 ms | 0.925 |
| +50.0 ms | +46.00 ms | 0.920 |

The classical errors-in-variables prediction `lambda = 1 - Var(noise)/Var(observed)` gives
`0.933` against a measured `0.915–0.925`, and with the label noise removed the recovery is
exact (`+24.87` for `+25.0`). So the centered estimator is unbiased up to a known
attenuation that can be divided out, and the attenuation always biases **toward zero**.

## Sign convention

E21's docstring states that a lag `tau` gives `e_par = -tau |v|`, and then prints the
fitted coefficient itself as `tau`. The two disagree by a sign. Everything from E27 onward
uses one convention, stated once: `p - g = -tau v`, so `tau > 0` means the detector
reports an **earlier** state. Under that convention E24's `+52.7 ms` is a lead of
`-52.7 ms`, which is the same direction the forward-difference artefact pushes.

## What this does NOT establish

It does not measure the real detector. It establishes that the estimator used in E21 and
E24 is biased by an amount set by the label noise and the observed velocity variance, and
that the centered form is not. The size of the artefact in the real rows depends on the
real `var(v)` and is computed in E27, not here.
