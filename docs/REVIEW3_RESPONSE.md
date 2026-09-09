# Response to external review #3 (2026-09-07)

Verdict received: **Reject**. Critical 1, Major 1, three submission-critical revisions.
Novelty, distinct contribution and significance were not the objection — the review states
the contribution is "clearly distinct" and that no CVPR 2022–2026 accepted paper performs
this measurement. The objection is technical soundness on one claim.

## Critical 1 — the magnitude regression does not identify a lag

> `beta_{|e_par|} - beta_{|e_perp|} = 0.0166 s` does not imply `tau = 16.6 ms`, because
> `E|eps + tau v|` is not `E|eps| + tau v`; for zero-mean symmetric noise the leading
> response near `d = 0` is even in `d`, so its first derivative vanishes.

**Accepted in full.** This is correct and it was reached independently by the internal
checklist audit on the same day, which flagged that `src/e24_order.py` fits `np.abs(epar)`
and `np.abs(eperp)` while `supplement.tex:145` calibrates for the signed residual. The
`+16.6 ms` figure is withdrawn from every position in the manuscript.

Refitting the same rows on the signed residual was the first response, and it produced a
*larger* number, `+52.7 ms` at 8.1 SE, against E21's `+11.9 ms` at 1.3 SE on the same
quantity. Two estimates of one quantity differing by four times is not a result, so the
disagreement was treated as a defect to be located rather than a finding. Three further
defects were found, all in the estimator, none of them raised by the review:

**(i) The acceleration regressor was a magnitude.** `|dv|/dt` is non-negative and
correlates with speed at `r = +0.36`. A first-order extrapolation cost is
`(1/2) a tau^2` *along travel* and requires a signed `a_par`. Entering a non-negative
proxy instead moves the speed coefficient, and the omitted-variable arithmetic accounts
for the whole `11.9 -> 52.7 ms` gap.

**(ii) The velocity was a forward difference, which shares label noise with the
residual.** `v_f = (c_{k+1} - c_k)/dt` carries the label-centre noise `delta_k` with
weight `-1/dt`; the residual `dx = p_x - c_{k,x}` carries the same `delta_k` with weight
`-1`. Their covariance is `+var(delta)/dt` **when the detector has no lag at all**. E29
simulates this with `tau_true = 0` and the label noise E28 measures on Gen1: the forward
estimator returns `-5.64 ms`, the backward estimator `+5.84 ms`, their sum `+0.20 ms`, the
closed form predicts `-5.63 ms`, and removing the label noise collapses all three to zero.
Both E21 and E24 used forward differences.

**(iii) The two experiments used opposite sign conventions.** E21's docstring defines a lag
by `e_par = -tau |v|` and then prints the fitted coefficient itself as `tau`.

**(iv) Standard errors assumed independence** across thousands of rows drawn from a few
hundred sequences and from repeated tracks. This is the review's Major 1, in a stronger
form than stated: the problem is not only the along/cross pairing but clustering.

The replacement estimator (E27) is a signed **vector** regression,

    p - g  =  b  -  tau * v  +  rho * R90 v  +  gamma * sqrt(A) * u  +  eps,

fitted as one stacked least squares on the velocity components. `tau` is identified by
construction under the stated model, with no magnitude step and no direction estimated
from the same noisy velocity. It carries:

- a **placebo**, `R90 v`: the velocity rotated a quarter turn, same magnitude, same noise,
  unreachable by any temporal offset.
- a **sign-flip control**: the identical fit under forward, backward and centered
  velocities.
- **sequence-clustered standard errors** and a cluster bootstrap over sequences.
- an **errors-in-variables** treatment using `sigma = 0.6515 px`, measured on Gen1 itself
  (E28) rather than imported from DSEC-Det's `0.4974 px` (E13). On these rows the
  attenuation is 0.5 %, so it does not carry the result either way.

## What the corrected estimator actually returns

Not `+16.6 ms`, and not `+52.7 ms`. **`tau = -2.40 +- 7.18 ms`**, which is 0.33 SE from the
label instant and **3.81 SE from the influence centroid**, with a cluster-bootstrap 95 %
interval of [-17.0, +11.5] ms and 3 of 4000 draws reaching the centroid.

The route there matters, because the placebo failed first. At the minimal specification
`rho` was -7.75 ms at 4.0 SE, and a placebo that large means a missing regressor. Splitting
by the sign of the horizontal velocity flipped its sign (-27.99 for objects moving right,
+21.84 for objects moving left), which a rotational term cannot do and a vertical bias
aliased onto `R90 v` must. Adding four directed geometric regressors and a per-sequence
bias vector returned the placebo to 1.6 SE — and moved `tau` from +14.62 to -2.40.
**The specification was selected by the placebo, a criterion that does not see `tau`.**

Three further checks, all on the same rows:

- **the controls do not eat a lag.** Injecting `-tau_inj v` into the observed residual is
  recovered at 1.000 of its size at 10, 25, 50 and 100 ms under the full control set, while
  injecting a purely geometric displacement leaves the full-control `tau` unchanged.
- **the axis pairing does not make the answer.** Entering all four geometric variables on
  both axes gives -3.62 +- 7.41 ms, and across every specification carrying geometric
  controls `tau` spans -20.2 to +11.1 ms. None reaches +24.94.
- **the nearest prior estimator, fitted here** (E35). The per-object ratio has an
  interquartile range of 430 ms and a sample standard deviation of 4170 ms; its mean over
  all rows is +24.22 ms, which would have "confirmed" the centroid hypothesis outright, and
  above a 15 px/s floor it gives +13.34 +- 6.17 ms. That is a fixed spatial bias divided by
  a speed, because the ratio has no intercept.

So the paper's temporal claim is no longer a point estimate of a lag. It is an interval:
the evidence is centred 24.94 ms before the instant the output is scored at, the output
carries no offset from that instant, and the two are 27.3 ms apart. The benchmark scores a
prediction at an instant its own evidence does not cover.

## The headline centroid, re-measured four ways (E34)

The remaining route to falsifying claim 1 is that zero-fill occlusion pushes the input off
the data manifold, and a flat profile is what that would produce. Answered rather than
conceded: setting a bin to its dataset mean gives -26.27 ms, taking it from an unrelated
sample -25.13 ms, and a gradient sensitivity that occludes nothing gives -22.36 ms, against
E17's -24.94 ms. The four span 3.9 ms, and the bootstrap standard error on the zero-fill centroid is
0.02 ms. The recurrent state was already held fixed within each sample, so no arm of this
measures state perturbation.

## Major 1 — optimistic standard errors

**Accepted.** Addressed above by clustering rather than by the paired-difference
construction, because the difference construction is itself withdrawn along with the
magnitude fit.

## Must-fix 2 — "two routes to output time"

**Accepted.** The magnitude decomposition is withdrawn, so there is one route, and
Sec. 3.5 and Sec. 3.6 collapse into Sec. 3.4. This frees a table and a subsection, which
is what pays for the new control table on a manuscript with no page slack.

## Must-fix 3 — the conclusion's temporal interpretation

**Accepted**, by the same deletion.

## What is not changed

Claim 1 (the influence centroid) and Claim 3 (the mains signature) are untouched. The
review grades them "mostly supported" and "fully supported" respectively, and no defect
found in the output-time estimator touches either: the centroid comes from bin occlusion
and carries no velocity, and the flicker analysis regresses nothing.

## Terminology

The review asks for "influence/sensitivity centroid" rather than "information centroid".
The manuscript already says *influence profile* and *influence-weighted centroid*
throughout; no instance of "information centroid" is present. No change required.


---

## What was added after the response was first written (2026-09-07, later)

**The benchmark number the paper had none of (E37).** A live search of accepted CVPR
2024-2026 work returned one objection this manuscript could not answer: every comparable
audit ends on a score that changes, and this one computed no detection score. It does now.
Displacing the ground truth of every labelled frame by `delta*v` and recomputing mAP over
20 296 frames and 40 698 boxes gives a smooth unimodal curve with its maximum at **-10 ms**
— a second estimate of the output time, from an argmax rather than a slope, agreeing with
the regression's `-2.40 +- 7.18 ms` and again short of the influence centroid.

The curve is nearly flat, and that is reported as the result rather than buried: the whole
+/-60 ms sweep moves mAP by 0.9 points and the interval costs **0.06 points, 0.18 %**. The
reason is arithmetic and it predicts its own test — at Gen1's median label speed of
4.0 px/s, 24.94 ms is 0.10 px on a 41.5 px box. Stratified by speed the sweep deepens as
required, 0.11 -> 0.33 -> 0.78 points across the three well-populated strata. The fastest
stratum breaks the trend on 337 boxes whose mAP is 0.139, and is reported as it came out.

The resulting claim is about the benchmark, not the detector: **a metric that moves by a
fifth of a percent under a 24.94 ms misalignment cannot be used to detect one.**

**Four prior works that were missing.** LEOD (CVPR 2024) states in print that event
detectors take only events triggered before the query time and builds a time-flip
augmentation on the receding/approaching asymmetry that follows; it does not measure where
inside the window the evidence sits. Adaptive spatial-temporal windows (CVPR 2026) retrain
per partitioning strategy. Sensor-latency correction (CVPR 2024) measures an
illumination-dependent microsecond offset at the photoreceptor. A continuous-stream
evaluation framework (Nature Communications 2026) penalises stale outputs and reorders
rankings; its latency is compute latency. All four were verified against their published
pages before citation, which corrected the fourth's first author.
