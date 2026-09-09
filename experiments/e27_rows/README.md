# E27 — the output time of the released checkpoint, re-measured (2026-09-07)

## Why this replaces E21, E23 and E24

E21 estimated the detector's output-time offset at `+11.9 ms` (1.3 SE). E24, on a wider
row set with an acceleration regressor, estimated the same quantity at `+52.7 ms` (8.1 SE)
once refitted on the signed residual. Two estimates of one number differing by four times
means at least one is measuring the estimator. Six defects were found, all in the
estimator, none in the data (`docs/PROTOCOL_LEDGER.md`, case 7):

1. **E24 fitted `|e|`.** `E|eps + tau v|` is not `E|eps| + tau v`; for symmetric zero-mean
   noise the derivative at `d = 0` vanishes. External review #3's Critical 1 and the
   internal checklist audit reached this independently on the same day.
2. **The acceleration regressor was `|dv|/dt`**, a magnitude entered where a first-order
   extrapolation cost needs a signed `a_par`. It correlates with speed at `+0.36`, and
   omitted-variable arithmetic accounts for the whole `11.9 -> 52.7 ms` gap.
3. **The velocity was a forward difference**, which shares the label-centre noise with the
   residual and manufactures a lag when none exists (E29 measures the size of this).
4. **E21 and E24 used opposite sign conventions.**
5. **Standard errors assumed independence** across thousands of rows from a few hundred
   sequences and repeated tracks.
6. **Neither saved its rows**, so the disagreement could not be diagnosed without another
   GPU pass.

## What this experiment is

One GPU pass over the whole Gen1 validation split that saves the **raw per-match row
table** and fits nothing: `rows.npz`, 35 523 matches over 406 sequences, columns
`seq, t_us, k, gi, cls, iou, dx, dy, fx, fy, dt_f, bx, by, dt_b, gw, gh, gcx, gcy`.
Every number below is a CPU re-analysis of that one table and can be re-run in seconds.

Requiring both label neighbours, so that a centered velocity exists, leaves **22 534
matches over 376 sequences**, median overlap 0.873, median box side 41.7 px, median label
speed 5.4 px/s. No speed floor.

## The estimator

A detector reporting the state an object occupied `tau` earlier displaces its prediction
by `-tau v`. That is a vector statement and it is fitted as one, stacking both components
of every match:

    c_hat - c*  =  b  -  tau v*  +  rho R90 v*  +  gamma sqrt(A) u  +  eps

`tau` is identified by construction under the model: no magnitude is taken and no direction
is estimated from the same noisy velocity the regression is on. `rho` is a **placebo** —
the velocity rotated a quarter turn, same magnitude, same noise, unreachable by any
temporal offset. Standard errors are clustered by sequence.

## The specification ladder (`fit.log`, `placebo_diag.log`)

| Specification | tau (ms) | placebo (ms) |
|---|---|---|
| forward difference, no geometric controls | −14.68 ± 4.99 | −6.53 ± 1.68 |
| backward difference | +45.65 ± 5.59 | −6.15 ± 1.71 |
| centered difference | +17.51 ± 5.06 | −7.76 ± 1.92 |
| + box side along travel | +14.62 ± 5.47 | −7.75 ± 1.91 |
| + four geometric terms | −7.62 ± 7.01 | −4.12 ± 1.90 |
| + per-sequence bias vectors | **−2.40 ± 7.18** | **−2.66 ± 1.71** |

**The specification was chosen by the placebo, not by tau.** At the minimal specification
the placebo is 4.0 SE from zero, and a placebo that large means the model is missing
something the rotated velocity stands in for. Splitting by the sign of the horizontal
velocity says what it is: `rho` is −27.99 (7.3 SE) for objects moving right and **+21.84**
(4.0 SE) for objects moving left. A rotational term survives that split; a vertical-bias
alias flips sign, and this flips. Most label motion in driving footage is horizontal, so
`R90 v` maps a horizontal speed onto a vertical residual, and a vertical bias that differs
between oncoming and same-direction traffic lands there with nothing rotational present.
Entering box height and image row along `y_hat`, box width and image column along `x_hat`,
and a constant vector per sequence returns the placebo to 1.6 SE. That criterion carries no
information about `tau`.

## The sign-flip control (`fit.log` arm 1, `injection.log` arm 3)

Under the full control set the forward estimator gives −20.60 ± 6.36 and the backward one
+14.38 ± 5.97, straddling the centered −2.40 at a midpoint of −3.11. The spread is 35 ms —
larger than any offset being looked for. E29 calibrates this on synthetic tracks with
`tau_true = 0` and shows it is the shared label-noise term, not the network.

## Do the controls eat the lag? (`injection.log` arms 1 and 2)

Adding `-tau_inj v` to the observed residual builds a dataset with a known extra lag and
every real confound left in place. Recovery under the full control set is **1.000** at 10,
25, 50 and 100 ms, which also shows `v` is not in the span of the controls. Injecting a
purely geometric displacement of 0.05 px per px of box height moves the minimal
specification's `tau` by +0.63 ms and the full specification's by less than 0.01 ms.

A speed floor changes only the precision: −2.92 ± 9.05 ms above 5 px/s, −4.95 ± 11.01
above 10, −7.85 ± 13.34 above 15, −20.24 ± 14.78 above 20.

## The result (`injection.log` arm 4, `bootstrap.log`)

    tau = -2.40 +- 7.18 ms
      H: tau = 0      (the label instant)     0.33 SE
      H: tau = 24.94  (the influence centroid) 3.81 SE
    cluster bootstrap, 4000 sequence resamples: 95 % CI [-16.98, +11.47] ms
      draws reaching 24.94 ms: 3 in 4000

The output is anchored at the label instant. The evidence is centred 24.94 ms before it
(E17). The interval between them is **27.3 ± 7.2 ms**, which at the 90th percentile label
speed of this split is 0.64 px of displacement and at the 99th, 1.35 px.

## Did the choice of geometric controls make the answer? (`saturate.log`)

The reported specification pairs each geometric variable with one image axis. Those are the
pairings perspective suggests, but they are choices, so every alternative is reported.

| Specification | tau (ms) | placebo (ms) |
|---|---|---|
| per-sequence bias only | +9.91 ± 5.73 | −6.43 ± 1.73 |
| reported: height and row on y, column and width on x | −2.40 ± 7.12 | −2.66 ± 1.70 |
| saturated: all four on **both** axes | −3.62 ± 7.41 | −1.59 ± 1.62 |
| all four projected on the travel direction | +8.64 ± 6.05 | −6.24 ± 1.73 |
| saturated + all four along travel | −1.47 ± 7.30 | −1.61 ± 1.62 |
| saturated, overlap ≥ 0.7 (n = 19 629) | +0.49 ± 4.67 | −1.79 ± 1.34 |
| saturated, \|v\| ≥ 15 px/s (n = 5 005) | −9.78 ± 12.34 | +0.35 ± 1.55 |

Dropping each reported control in turn moves `tau` by less than 0.3 ms except for the image
column on `x_hat`, whose removal returns `tau` to +11.10 and the placebo to −6.42 — that
one term carries the horizontal bias the placebo was standing in for.

Across every specification carrying geometric controls, `tau` spans **−9.78 to +11.10 ms**.
None of them reaches +24.94 ms.

## The nearest prior estimator, fitted on the same rows (E35, `ratio.log`)

Sec. 3.4 argues against the per-object ratio `-<p-g, u>/|v|` because its variance diverges
as its denominator approaches zero. An argument is not a comparison, so it is fitted.

| estimator | value (ms) |
|---|---|
| ratio, mean over all rows | **+24.22 ± 27.73** |
| ratio, median | +12.32 |
| ratio, interquartile range | 429.53 |
| ratio, mean above 15 px/s (n = 5 005) | +13.34 ± 6.17 |
| reported vector regression, no floor | **−2.40 ± 7.18** |

Its sample standard deviation over all rows is **4170 ms**. Two things follow. The mean over
all rows, +24.22 ms, sits almost exactly on the influence centroid of 24.94 ms, so the
naive estimator would have "confirmed" the hypothesis this paper reports as excluded. And
the floored arm, +13.34 ± 6.17 ms, is significant at more than two standard errors — it is
a fixed spatial bias divided by a speed, because the ratio has no intercept and
Eq. 1 does.

## Descriptive statistics, measured on the sample actually reported (E36, `split_stats.log`)

Two numbers reached a manuscript draft from retracted E21, whose sample was 2 235 rows
under a 15 px/s floor:

| quantity | E21 (retracted) | E27 fit sample |
|---|---|---|
| corr(\|v\|, sqrt(A)) | +0.349 | **+0.139** |
| boxes with a successor at IoU ≥ 0.3 | 81.5 % | **79.0 %** (31 683 / 40 084) |

The correlation above a 15 px/s floor is +0.287, which is where E21's larger figure came
from. A retracted experiment's numbers do not become correct by being plausible.

## Files

| file | what it is |
|---|---|
| `rows.npz` | the raw row table, 35 523 × 18, one GPU pass |
| `run.log` | that pass |
| `fit.log` | the specification ladder and the sign-flip control |
| `placebo_diag.log` | what the rotated-velocity coefficient is (E30) |
| `injection.log` | recovery of an injected lag, and the hypothesis tests (E31) |
| `bootstrap.log` | the cluster bootstrap, by Frisch-Waugh-Lovell (E32b) |
| `saturate.log` | the specification sweep (E33) |
| `ratio.log` | the per-object ratio, for comparison (E35) |
| `split_stats.log` | descriptive statistics of the fit sample (E36) |

## What this does NOT establish

That a zero offset is a discovery: training against the ground truth at the label time on a
window ending there is what places the output at that instant, so `tau ~ 0` reports the
objective. What is not enforced by the objective is that the interval exists, and a null is
bounded by its precision — this one excludes an offset as large as the influence centroid
and says nothing about one of a few milliseconds. It is one checkpoint, one architecture,
one dataset. The specification, though selected by a criterion independent of `tau`, is
still a selected specification, and a different set of geometric controls could leave a
different residual bias behind.
