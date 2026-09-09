# E42 — the temporal support of a *recurrent* detector (2026-09-07)

## Why this exists

E17 and E34 occlude the bins of the current 50 ms window while holding the recurrent state
fixed. An external review pointed out, correctly, that this measures the influence of the
current window **conditional on an intact recurrent state**, not the temporal support of
the emitted state as Sec. 3.1 defines it. RVT carries an LSTM state between timesteps, so
the prediction at `t` depends on windows before `t` as well.

The paper's own sentence — *"the profile is a property of the current window and not of a
perturbed history"* — states what was measured. The abstract and conclusion then generalised
it to "the detector's evidence". That was my error, and the right response is to measure
the part that was missing rather than to narrow the wording around it.

## Construction

For each lag `L`, restore the recurrent state saved *before* step `t − 50L`, occlude that
whole window, and let the state propagate forward normally to `t`. The relative `L2` change
in the emitted state at `t` is that window's influence. Saving states per step makes lag `L`
cost `L+1` forwards instead of a full re-run. 576 samples over 12 Gen1 validation
sequences, recurrent state warmed 8 steps.

Because E17 measured the within-window profile to be flat (CV 0.034), a window at lag `L`
contributes at a centroid of `−(25 + 50L)` ms, and the support centroid is the
influence-weighted mean over lags.

## Result

| lag | window centre | influence | share (20-window horizon) |
|---|---|---|---|
| 0 | −25 ms | 0.02309 | **22.75 %** |
| 1 | −75 ms | 0.01260 | 12.41 % |
| 2 | −125 ms | 0.00883 | 8.70 % |
| 3 | −175 ms | 0.00688 | 6.78 % |
| 9 | −475 ms | 0.00327 | 3.22 % |
| 14 | −725 ms | 0.00238 | 2.35 % |
| 18 | −925 ms | 0.00217 | 2.14 % |
| 19 | −975 ms | 0.00224 | 2.20 % |

**The current window carries under a quarter of the influence.** Half the influence is
reached only by lag 3, at −175 ms.

**The tail does not decay to zero within the second measured.** Influence at lag 19 (0.00224)
is no lower than at lag 18 (0.00217). The consequence is that the influence-weighted
centroid moves with the horizon rather than converging:

| horizon | centroid | current-window share |
|---|---|---|
| 500 ms (10 windows) | **−165.9 ms** | 29.1 % |
| 1000 ms (20 windows) | **−299.4 ms** | 22.7 % |

Doubling the horizon roughly doubles the centroid. **This detector's temporal support has
no finite centroid over the horizon measured.**

## The history matters more than the current window

Running the target step with the recurrent state zeroed, same input window, changes the
emitted state by **0.0867** of its norm. Occluding the entire current window changes it by
**0.0231**. The history is worth **3.8 times** the current window.

## A note on the two runs

`run.log` (10 lags) and `run_k19.log` (20 lags) both report 576 samples over the same 12
sequences, and they disagree by up to 13 % at shared lags. That is not irreproducibility:
the sample loop starts at `max(WARM, KLAG)`, so the two runs scored **different frames** —
the k=9 run began at index 9 and the k=19 run at index 19. Everything the manuscript quotes
comes from `run_k19.log` alone, including the 500 ms horizon, whose centroid on that run is
**−161 ms** rather than the −166 ms of the shorter run.

## The fill control (`fill_control.log`)

Zero-filling a past window pushes the recurrent state off the manifold it was trained on,
so the plateau had to be separated from its instrument. Replacing the window with the
same-index window of an unrelated sample keeps a real window's statistics and structure
while removing that window's own content.

| lag | centre | zero fill | swap fill | swap / zero |
|---|---|---|---|---|
| 0 | −25 ms | 0.02309 | 0.05620 | 2.43 |
| 1 | −75 ms | 0.01260 | 0.04083 | 3.24 |
| 3 | −175 ms | 0.00688 | 0.03378 | 4.91 |
| 9 | −475 ms | 0.00327 | 0.02691 | 8.24 |
| 19 | −975 ms | 0.00224 | 0.02565 | 11.47 |
| **decay, lag 0 to 19** | | **10.3x** | **2.2x** | |

The plateau does not collapse under the swap — it deepens. Under the swap fill a window a
second back still carries **46 %** of the influence of the window immediately before, and
the whole decay across a second is a factor of 2.2. The zero fill was *understating* the
long dependence, not manufacturing it.

Neither fill is the truth; both are interventions, and the swap injects content from a
different scene while the zero removes content. What they agree on is the conclusion that
matters: the current window is a minority of the temporal support, and the support does not
decay away within the second measured. The centroid itself is therefore not identified —
it depends on the horizon and on the intervention — and the paper reports it as such.

## What this changes in the manuscript

`−24.94 ms` is not the detector's evidence centroid and must not be called one. It is the
influence centroid of the **current input window, conditional on the recurrent state**, and
it is a well-measured quantity — four instruments place it within 3.9 ms (E34), and the
released configuration that puts it there is read from source (E02).

The paper's argument does not weaken; it grows. The interval between where the detector's
evidence lives and the instant its output is scored at is **at least** 24.94 ms and, once
the recurrent history is counted, larger by an amount the measured horizon does not bound.

## What this does NOT establish

The influences are norms of differences and do not add linearly, so the "share of total"
column and the centroid built from it are a weighting, not a decomposition. Occluding a
whole past window is a larger perturbation than occluding one bin, but every lag receives
the identical treatment, so the comparison across lags is fair while the comparison against
E17's per-bin numbers is not. Whether the non-decaying tail is dependence or an artefact of
the zero fill is a separate question, answered by the fill control in
`fill_control.log`. One checkpoint, one architecture, one dataset.
