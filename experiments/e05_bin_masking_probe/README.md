# E05 — Does bin masking actually vary a network's temporal support? (2026-09-01)

The revised idea's central repair replaces "retrain RVT at four window widths" with three
no-training levers on the stored `dt=50ms nbins=10` tensor, claiming a **30x
within-checkpoint support range**. Reviewer 2 was asked to settle whether that varies
temporal support or merely ablates input. This is a first, cheap probe of the mechanism,
run before that review lands.

Setup: real pretrained `rvt-t` gen1 weights, loaded strict (E04), `previous_states=None`,
synthetic sparse input (2 % of pixels active, 1-3 counts), measuring the relative L2 change
of the **backbone feature maps**. Bin 0 is the oldest of the ten 5 ms bins.

## Cumulative leading-bin masking — the response saturates

| bins masked | nominal w_P | rel. L2 change |
|---|---|---|
| 0 | 50 ms | 0.0000 |
| 1 | 45 ms | 0.0145 |
| 2 | 40 ms | 0.0323 |
| 3 | 35 ms | 0.0605 |
| 4 | 30 ms | 0.0979 |
| 5 | 25 ms | 0.1248 |
| 6 | 20 ms | 0.1269 |
| 7 | 15 ms | 0.1256 |
| 8 | 10 ms | 0.1365 |
| 9 | 5 ms | 0.1538 |

The response grows steeply to 25 ms and then **flattens**: masking bins 5 through 9 moves
the features by almost nothing (0.1248 -> 0.1538, and non-monotone in between).

## Single-bin occlusion — the influence profile is nearly flat

| bin centre relative to label | rel. L2 change |
|---|---|
| -47.5 ms | 0.0145 |
| -42.5 ms | 0.0182 |
| -37.5 ms | 0.0225 |
| -32.5 ms | 0.0195 |
| -27.5 ms | 0.0201 |
| -22.5 ms | 0.0244 |
| -17.5 ms | 0.0254 |
| -12.5 ms | 0.0248 |
| -7.5 ms | 0.0284 |
| -2.5 ms | 0.0243 |

Oldest to most influential is a factor of about 2. There is a mild recency preference
peaking at -7.5 ms, not a sharp one, and the most recent bin is not the most influential.

## What this does and does not establish

**Does:** masking is not inert — it moves the network's features, so the lever exists.
And the flat-ish occlusion profile is the shape the "uniform-weight centroid at t - 25 ms"
reference point (E02) assumes; this is weak early support for that assumption rather than
against it.

**Does not — and these caveats are load-bearing:**
1. The input is **synthetic random sparse noise, not event data**. A real scene has spatial
   and temporal structure that this does not have, and the influence profile could differ
   substantially.
2. The measurement is **backbone feature displacement, not detections and not `tau_hat`**.
   Feature change of 0.13 says nothing yet about how far the predicted box moves in time.
3. `previous_states=None`, so this is a **first frame with no recurrence**. Reviewer 6's
   objection — that a recurrent model's true support is the whole sequence — is untouched
   here and remains open.
4. Saturation past 25 ms means the achievable *effective* support range is plausibly much
   narrower than the claimed 30x, even though the nominal range is 30x. **The revision's
   claim should be restated in terms of measured effective support, not nominal bin count,
   until this is redone on real data with detections.**

This probe cost minutes. Redoing it properly needs `gen1.tar` (98.6 GB) and the evaluation
pipeline, and it should be the first GPU work of the project, because if the effective
range collapses to 2x the `tau_hat`-vs-`w_P` regression loses most of its leverage.
