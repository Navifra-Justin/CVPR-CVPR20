# E34 — is the −24.94 ms influence centroid an artefact of the occlusion? (2026-09-07)

## Why this exists

E17 occludes a bin by writing zeros into it and finds a nearly flat influence profile
(CV = 0.034) whose centroid is −24.94 ms. A checklist audit raised the right objection: a
flat profile is also what an intervention pushing the input off the data manifold would
produce, for reasons having nothing to do with temporal weighting. Zero is a legal value
for this representation — it means "no events in this bin" — but it is still an
intervention.

Two arms of that objection can be separated. **State perturbation is already excluded by
construction**: the reference pass and the occluded pass are given the same recurrent
`states`, and the states the occluded pass returns are discarded, so the profile is a
property of the current window. **The fill remains**, and it is tested.

## Construction

Three fills and one instrument that does not occlude at all, over the same 480 samples of
12 Gen1 validation sequences with the recurrent state warmed 8 steps:

- **zero** — what E17 did.
- **mean** — the bin set to its per-channel dataset mean, keeping the input in range.
- **swap** — the bin taken from the same bin of an unrelated sample, keeping both the
  marginal statistics and the spatial structure of a real bin.
- **gradient** — `d‖out‖ / d(bin)` summed over the bin's channels. No occlusion, no
  off-manifold step, and a different definition of influence.

## Result

| instrument | centroid (ms) | CV over bins | bootstrap SE | 95 % CI |
|---|---|---|---|---|
| zero (E17) | **−24.944** | 0.0337 | 0.022 | [−24.99, −24.90] |
| mean | −26.272 | 0.1371 | 0.025 | [−26.32, −26.22] |
| swap | −25.133 | 0.0435 | 0.081 | [−25.29, −24.98] |
| gradient | −22.359 | 0.1902 | 0.005 | [−22.37, −22.35] |

Uniform-weight reference: −25.00 ms. The four centroids span **2.6 ms**, against bootstrap
standard errors of 0.005–0.081 ms on any one of them, so the spread is the choice of
instrument and not sampling. An instrument that performs no occlusion at all still places
the centroid at −22.4 ms, so the flat profile is not an artefact of intervening.

This also supplies the number the manuscript needs for honesty about the interval: the
centroid's own sampling error is 0.02 ms and its instrument-dependence is 2.6 ms, both
small beside the output-time term's 7.18 ms, so the evidence-to-output interval's stated
uncertainty is dominated by the regression.

## What this does NOT establish

That occlusion equals a linear influence weight. It does not, except for a predictor linear
in its bins, and that limitation stands unchanged. It also does not extend to another
checkpoint, architecture or dataset. What it establishes is narrower: within this
checkpoint, the centroid is not a property of how a bin is removed.
