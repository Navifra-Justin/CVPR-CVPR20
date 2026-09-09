# E37 — what the interval is worth on the benchmark's own metric (2026-09-07)

## Why this exists

A live search of accepted CVPR 2024–2026 work returned the objection this paper had no
answer to: every comparable audit — dataset leakage, metric bias, evaluation protocol —
ends on a score that changes, and this one computed no detection score anywhere. A
property that costs nothing invites "so what".

## The question, asked the benchmark's way

If the detector's output describes the state at `t + delta` rather than at the label
instant `t`, then scoring it against ground truth displaced to `t + delta` should score
better, and the `delta` that maximises average precision estimates the output time from
the metric itself — by an argmax rather than by a regression slope.

**The ground truth is displaced, not the detections.** Every ground-truth box carries a
track velocity from its own labels; detections do not, and moving a detection by the
velocity of the box it happens to match would be circular. Displacing the ground truth by
`delta * v` scores the released predictions against the state each object occupied `delta`
later and leaves the detector untouched.

One GPU pass dumps every detection and every ground-truth box: **20 296 frames, 86 788
detections, 40 698 ground-truth boxes**, of which 27 943 (68.7 %) have a centered
velocity. The rest are marked ignore in the COCO sense. mAP is the standard average over
IoU 0.5 to 0.95.

## The curve (`sweep.log`)

| delta (ms) | −60 | −25 | **−10** | 0 | +25 | +60 |
|---|---|---|---|---|---|---|
| mAP, moving objects | 0.3288 | 0.3340 | **0.3346** | 0.3346 | 0.3329 | 0.3260 |

Smooth, unimodal, **maximum at −10 ms**. Read as an output time this is `tau = +10 ms`,
against the regression's `tau = -2.40 +- 7.18 ms` (E27) — the two instruments agree within
1.7 standard errors, and neither reaches the influence centroid of +24.94 ms, which sits
below the peak on this curve as well.

**The curve is very flat**: the whole ±60 ms sweep moves mAP by 0.9 points, and the
24.94 ms interval costs **0.06 mAP points, 0.18 %**.

## That flatness is the result, and it was predicted

A displacement of `tau` costs IoU in proportion to `tau*|v|` against the box size. On this
split the median label speed is 4.00 px/s and the median box side 41.5 px, so 24.94 ms is
**0.10 px on a 41.5 px box**. The metric cannot see it. The prediction is that the curve
deepens with speed, and stratifying tests it (`strata.log`):

| stratum | n | span over ±50 ms | cost of 24.94 ms | argmax |
|---|---|---|---|---|
| \|v\| < 10 px/s | 20 154 | 0.11 points | 0.02 | −10 ms |
| 10 ≤ \|v\| < 25 | 5 356 | 0.33 points | 0.04 | −10 ms |
| 25 ≤ \|v\| < 50 | 2 096 | **0.78 points** | 0.09 | −10 ms |
| \|v\| ≥ 50 | 337 | 0.37 points | 0.01 | −5 ms |

Across the three well-populated strata the sensitivity rises by a factor of seven with
speed, as the arithmetic predicts. **The fastest stratum breaks the trend and is reported
as it came out**: it holds 337 boxes and its mAP is 0.139 against 0.286 for the stratum
below, so fast objects are lost to detection failure rather than to localisation, and the
stratum has neither the count nor the headroom to show a displacement effect.

## What this establishes, and what it does not

It establishes that the interval measured in this paper is worth 0.06 mAP on Gen1 and that
this number rises with object speed in the way the geometry requires. It is a statement
about **the benchmark's temporal sensitivity**, not about the detector being wrong: an
event-camera benchmark whose metric moves by a fifth of a percent under a 25 ms
misalignment cannot be used to detect one.

It does not establish a cost on any other dataset, and it does not establish that closing
the interval would raise anyone's score. The argmax carries no interval here — a cluster
bootstrap of it over sequences was not run — so `−10 ms` is reported as an agreement in
sign and magnitude with E27, not as an independent significant estimate.
