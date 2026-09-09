# E08 — The DSEC-Det label noise floor, and whether label errors are white (2026-09-02)

An external review raised two of its three Major issues against quantities that had never
been measured: the estimator's independence assumption (Major 2) and the fragility of the
dispersion estimate to the assumed label noise `sigma_c` (Major 3). Both are properties of
the labels, and the labels are 23 MB on disk, so both were measured directly.

Data: all 60 `tracks.npy` files of DSEC-Det, 5250 tracks with at least six detections on a
regular 20 Hz grid, 639 942 second differences and 629 442 third differences of the box
centre in x and y.

## Estimator

For `x_i = f(t_i) + e_i` on a uniform grid,

    Var(2nd difference) = 6 s^2 + (f'' h^2)^2
    Var(3rd difference) = 20 s^2 + (f''' h^3)^2

Under locally constant acceleration `f''' = 0`, so the third difference is pure noise and
`s = sqrt(Var(D3)/20)`. Variances are taken robustly (MAD x 1.4826) so a few gross outliers
cannot set the answer.

## Result 1 — the label noise floor

| estimator | value |
|---|---|
| `sigma_c` from the 2nd difference | **0.605 px** |
| `sigma_c` from the 3rd difference | **0.497 px** |
| ratio | 1.217 |

The second-difference estimate is larger, as it must be, because it still contains the
curvature term. **`sigma_c` is at most 0.50 px**, and this is an upper bound: any real jerk
in the object's motion also enters the third difference.

## Result 2 — the label errors are not white, and the estimator is not at fault

Autocorrelation of the third-difference series. For white noise the third-difference kernel
`(1, -3, 3, -1)` forces `rho(1) = -0.75`, `rho(2) = 0.30`, `rho(3) = -0.05`.

| series | lag 1 | lag 2 | lag 3 |
|---|---|---|---|
| white-noise theory | -0.75 | 0.30 | -0.05 |
| **control: white noise through this exact code** | **-0.740** | 0.293 | -0.049 |
| control: heteroscedastic segments | -0.741 | 0.297 | -0.055 |
| control: heavy tails, Student-t df 2.5 | -0.737 | 0.287 | -0.046 |
| control: AR(1) noise, rho = 0.6 | -0.667 | 0.173 | 0.000 |
| **measured on DSEC-Det labels** | **-0.357** | **0.091** | -0.013 |

Three competing explanations for the departure were tested before it was accepted as real,
each pushed through the identical pooling code:

- *the pooled ratio estimator is biased toward zero* — refuted; white noise returns -0.740.
- *pooling segments of different variance biases it* — refuted; returns -0.741.
- *heavy-tailed outliers inflate the denominator* — refuted; returns -0.737.

The measured value is roughly half the white-noise magnitude at every lag, and an AR(1)
model cannot reproduce it even at `rho = 0.95` (which predicts -0.667). So the departure is
a property of the labels, not of the estimator, and the noise is more strongly structured
than a first-order process.

## Result 3 — object speed, and where a temporal offset is detectable

| quantity | p10 | median | p90 | p99 |
|---|---|---|---|---|
| box-centre speed (px/s) | 0.0 | 40.0 | 150.0 | 360.2 |
| speed change (px/s^2) | — | 384.5 | 1012.6 | 3336.0 |

A temporal offset `tau` appears as a displacement `tau * v` along the track:

| tau | at median speed | at p90 | at p99 |
|---|---|---|---|
| 5 ms | 0.20 px = 0.40 `sigma_c` | 0.75 px = 1.51 `sigma_c` | 1.80 px = 3.62 `sigma_c` |
| 10 ms | 0.40 px = 0.80 `sigma_c` | 1.50 px = 3.02 `sigma_c` | 3.60 px = 7.24 `sigma_c` |
| 25 ms | 1.00 px = 2.01 `sigma_c` | 3.75 px = 7.54 `sigma_c` | 9.00 px = 18.11 `sigma_c` |

## What this settles

**Major 2 is confirmed, against the paper.** The instrumental-variable argument rests on
"the two velocity estimates share no label, therefore their errors are uncorrelated." The
labels' errors are measurably not white, so disjointness does not deliver independence, and
the paper's justification of its headline estimator does not hold as written. The estimator
needs either a correlation-aware treatment or a different instrument.

**Major 3 is answered, in the paper's favour.** `sigma_c` no longer has to be assumed: it is
at most 0.50 px, measured. The excess-dispersion quantity can be reported against a measured
noise floor rather than a guessed one.

**A design consequence the paper does not currently state.** At the median object speed a
25 ms offset is 1.0 px, only twice the label noise. The measurement is only comfortable in
the fast tail: at the 99th percentile of speed the same offset is 9.0 px, eighteen times the
noise floor. Any estimate pooled over all objects is dominated by objects that carry almost
no information about it, and the analysis should be stratified by speed rather than pooled.

## Limits

- `sigma_c = 0.497 px` is an **upper bound**. Real jerk enters the third difference and cannot
  be separated from noise without an independent reference. A decomposition assuming the
  motion component has a smooth autocorrelation puts the noise part near 0.39 px, but that
  depends on the assumed jerk spectrum and is not reported as a measurement.
- The autocorrelation result shows the errors are *not white*; it does not identify what they
  are. The specific structure is not AR(1) and is not identified here.
- Speeds are box-centre image speeds from the labels themselves, so they inherit the same
  noise; at the low end they are not distinguishable from zero.
