# Chronofields: Predicting *When* Instead of *What*, from Exact Events and Interval-Censored Frames

*Idea Team 7 — CVPR 2027 — Temporal-Support-Aligned Event–RGB Perception*
*Angle: invert the query. Time is the output; scene state is the index.*

---

## One-sentence thesis

Every perception head is a map `time -> state`; we invert it into a map `state -> time` — a *chronofield* that predicts, for a queried state (a contrast crossing, a spatial passage, a contact, a line crossing), a **distribution over when it held**, with events entering the likelihood as *exact* time observations and frames entering as *interval-censored* ones, because a frame does not have a timestamp and never did.

---

## The assumption we kill

> **A frame has a timestamp.**

Not "a frame has an approximate timestamp." The assumption is that a frame is annotated, associated, fused, supervised and evaluated as if it were an instantaneous observation at a single scalar time `t_c` — universally taken as the exposure midpoint or the shutter-open time.

**Why it is universal.** It is baked in below the level anyone argues about:

- **Data format.** Every event–RGB dataset (DSEC, MVSEC, DAVIS recordings, PKU-DAVIS-SOD, BS-ERGB) stores frames as `(image, t)`. There is no field for an interval. The exposure length is frequently not even recorded.
- **Association.** Every event–RGB method slices events into a window "around the frame timestamp." A window needs a center.
- **Annotation.** Boxes and masks are drawn on frames and inherit the frame's scalar `t`. Ground truth therefore lives on the same grid as the prediction.
- **Evaluation.** mAP, MOTA, EPE are all computed by matching predictions to annotations *at the annotation times*.

**What breaks.** A frame is `B(u) = (1/T) ∫_{a}^{a+T} I(u,t) dt` — a measure on the time axis, not a point on it. Stamping it with `a + T/2` is a maximum-likelihood point estimate under a **uniform dwell-time prior**, i.e. under the assumption that the scene moved at constant velocity through the exposure. That assumption fails precisely in the regime where events are supposed to help. Two consequences, both derived below and both measurable:

1. The frame's *effective* time is biased away from the midpoint by `Δt ≈ a·T² / (24·v̄)` (image-space acceleration `a`, mean image speed `v̄`). Quadratic in exposure, and it **diverges as `v̄ → 0`**.
2. For a target that reverses direction inside one exposure — a ball at impact, a wiper at its turn, a hand at the top of a gesture, a propeller blade — the effective time is not biased, it is **multi-valued**. The formulation has one slot. Physics needs two.

The second consequence is the one worth a paper: it is not an error term, it is a *type error*.

---

## The failure phenomenon

We report two curves. The first indicts the **metric**; the second indicts the **frame**.

### F1 — mAP has a null space in the time direction (headline)

**Measurement.** Take a strong event+frame detector (FAOD, RVT+DAGr-style). On a held-out sequence with 1 kHz ground truth, evaluate (i) standard mAP against grid-aligned annotations and (ii) **Crossing-Time Error (CTE)**: for each object and a fixed virtual tripwire, the absolute error in the predicted time at which the object's boundary crossed it, in milliseconds.

**Independent variable.** Object image-space acceleration `a` (px/ms²), swept by sequence stratification and, in simulation, directly. Secondary sweep: inter-frame interval `Δt_f ∈ {5, 11, 20, 33, 50} ms`.

**Axes.** x = `a·Δt_f²` (a single dimensionless-ish predictor, px); left y = mAP@0.5; right y = P95 CTE (ms), log scale.

**Expected curve.** mAP is **flat** across the sweep (it is already known to be: FAOD reports only a *3-point* mAP drop under an 80× event–RGB frequency mismatch — their own headline result is our evidence that mAP cannot see time). CTE rises **linearly in `Δt_f`** and picks up a super-linear term in `a`, spanning roughly 1 ms → 25 ms over the sweep. **The two curves diverge.** The benchmark says nothing is wrong while the answer degrades by an order of magnitude.

**Proposition (constructive, not empirical).** Let a detector's outputs be shifted uniformly in time by `δ`. If `δ·v_max < ε` where `ε` is the IoU-matching tolerance in pixels, mAP is *exactly unchanged*, while CTE changes by exactly `δ`. Therefore **mAP is invariant to a group of temporal shifts** and no existing event–RGB detection benchmark can distinguish a method that is right at the right time from one that is right at the wrong time. We will demonstrate this by construction: two systems, identical mAP to 3 decimals, 4× different CTE.

**Quantitative prediction.** At 30 fps with `σ_x ≈ 3 px` detector spatial error, the conventional route's time error is dominated by interpolation, `≈ a·Δt_f²/8`. The inverted route is bounded by event jitter + temporal bin width, `≈ 0.5–1 ms`. **Crossover at `a > 8σ_x/(Δt_f²·v̄) ≈ 0.2 px/ms²`** — a regime that covers essentially all near-field looming, all rotation about a near axis, and all contact. We predict WHEN beats WHAT above this line and *does not* below it, and we will plot the crossing.

### F2 — the frame's effective timestamp, measured with events (mechanism)

**Derivation.** For a 1-D edge at `x(t) = x₀ + v₀t + ½at²` over exposure `[0,T]`, the blurred image's intensity profile is the dwell-time density `∝ 1/|ẋ|`. Its spatial centroid is `x̄ = ∫x(t)dt/T = x₀ + v₀T/2 + aT²/6`, while the position at the midpoint time is `x(T/2) = x₀ + v₀T/2 + aT²/8`. The mismatch `aT²/24` converts to a time bias

```
Δt  ≈  a·T² / (24·v̄),        v̄ = v₀ + aT/2
```

**Measurement.** From 1 kHz ground-truth video, define per-pixel `t*(u) = argmin_t ‖B(N(u)) − I(N(u), t)‖` (best-matching sharp latent time) and measure `t*(u) − (a+T/2)`. Independent variable: `a·T²/v̄`. **Expected curve: a straight line through the origin with slope 1/24**, plus a divergence branch as `v̄ → 0`.

**Quantitative prediction.** At `T = 20 ms`, `a = −2 px/ms²`, `v̄ = 4 px/ms`: `Δt ≈ −8.3 ms`, i.e. **42% of the exposure** — larger than a whole inter-frame interval at 50 fps. At `T = 10 ms`, `a = −1`, `v̄ = 5`: `−0.83 ms`, small. The bias is negligible in the benign regime and dominant in the interesting one, which is exactly why nobody has noticed it.

**The role reversal.** Local event rate is `∝ |∂_t log I|`. So the *events themselves measure the frame's own effective timestamp* — no simulator needed at test time. The contrast-weighted barycenter `t̂(u) = (Σ_k t_k)/N_u` over events at pixel `u` inside the exposure is a computable, per-pixel timestamp for a frame. Standard practice aligns events *to* the frame's time. We use events to tell the frame *what time it is*, and then refuse to collapse it to a scalar anyway.

---

## The reformulation

### State space

Fix an observation window `W = [0, T_w]`. A **state index** `s ∈ S` names a scene condition; the predicate `P_s(t) ∈ {0,1}` says whether it holds at time `t`. We instantiate three:

| | index `s` | predicate | ground truth source |
|---|---|---|---|
| **C1 Photometric** | `(u, k)` — pixel, contrast level | log-intensity at `u` crosses level `k` | **the event stream itself** (µs-exact, real, free) |
| **C2 Passage** | `(u, o)` — pixel, object | object `o`'s support covers pixel `u` | 1 kHz video / VICON |
| **C3 Relational** | `(i, j)` — object pair, or object×gate | supports of `i` and `j` overlap / `i` crosses gate `j` | geometry from 1 kHz video, LiDAR, GNSS/INS |

C3 is the case that is **well-posed only in the inverted form**: a contact between a bat and a ball lasts ~2 ms. At 30 fps, ~94% of contacts fall strictly between frames. The conventional formulation has *no output slot* into which the answer could be written.

### What is predicted

A **chronofield**

```
τ :  S  ->  Δ(W ∪ {∅})
```

a distribution over *when*, with an explicit atom `∅` = "never within `W`". Parameterization: `B+1` logits per state index over `B` uniform time bins plus a `∅` bin, softmax to `p`, with a per-bin sub-bin offset `δ_b ∈ [−Δ/2, Δ/2]`. `B = 128` over a 100 ms window gives 0.78 ms bins; the offset head recovers ~0.1 ms. The `∅` atom and the multi-bin support are load-bearing — they are the two things a scalar regression head cannot have.

### Objective

The whole point is that the two modalities are **different kinds of observation of the same latent time**, so they enter the *same* likelihood with different censoring, not through feature concatenation. (This is explicitly not event+RGB fusion: there is one predicted variable and two observation models.)

**(L1) Exact — from events.** An event `(u, t*, p)` is an uncensored observation of a crossing time.
```
L_exact = −log p_{b*}  +  λ_δ · |δ_{b*} − (t* − c_{b*})|,    b* = bin(t*)
```

**(L2) Interval-censored — from frames.** A frame with exposure `[a, a+T]` says the transition happened *somewhere inside*, not when. This is textbook interval censoring:
```
L_int = −log ( F(a+T) − F(a) ) = −log Σ_{b : c_b ∈ [a, a+T]} p_b
```

**(L3) Right-censored — "it never happened."**
```
L_cens = −log p_∅ = −log (1 − F(T_w))
```
Needed for state indices that genuinely do not occur, and for pixels below contrast threshold where the event branch is *itself* censored.

**(L4) Dwell-time measure constraint — the frame as more than an interval.** Change of variables on the blur integral. For a monotone segment,
```
B(u) = (1/T) ∫_a^{a+T} I(u,t) dt  =  (1/T) ∫ L · (∂τ/∂L)(u,L) dL
```
so the blurred pixel value is a **dwell-time-weighted average over intensity levels**, and `∂τ/∂L` — the *spacing of crossing times*, a first-class quantity in the inverted domain — is directly observed. Discretized:
```
L_blur = | B(u) − (1/T) Σ_k L_k · ( τ̂(u,k+1) − τ̂(u,k) ) |
```
This is the EDI double-integral model re-expressed with the variables swapped. Same physics; the frame becomes a *quantitative* constraint on the chronofield rather than a weak bracket. It carries real information exactly where events carry none: low-contrast regions.

**(L5) Temporal eikonal — the SDF analogue.** Differentiating `I(u, τ(u)) = L` in `u` gives `∇_u I + I_t ∇_u τ = 0`; brightness constancy gives `I_t = −∇_u I · v`; substituting,
```
∇_u τ(u) · v(u)  =  1                    [exact]
        ⇒  ‖∇_u τ‖ = 1 / v_⊥             [normal-flow form]
```
**The spatial gradient of the crossing-time field is the slowness (inverse-velocity) field.** This is the precise temporal analogue of the eikonal constraint `‖∇d‖ = 1` that makes signed-distance fields well-behaved, and it exists *only* when time is the output. Regularizer, with `v̂` from a joint flow head or from contrast maximization:
```
L_eik = Σ_u ρ( ∇_u τ(u) · v̂(u) − 1 ),   ρ = Huber,  masked at motion boundaries
```

**Total.** `L = L_exact + λ₁L_int + λ₂L_cens + λ₃L_blur + λ₄L_eik`.

### What this forces us to admit about frames

A frame can contribute to L2, L3 and L4. **It can never contribute to L1.** No amount of deblurring, interpolation or alignment converts an integral into an instant; it only narrows the interval. Frames are *irreducibly censored observations of time*, and the universal midpoint stamp is a hidden, wrong prior — not a convention.

---

## What existing methods cannot express

Five things, in increasing order of severity.

1. **A crossing strictly between output timestamps.** There is no variable for it. The answer must be interpolated, and — the sharp part — *the ground truth is on the same grid*, so the benchmark cannot penalize getting it wrong.
2. **"This never happened."** A `time -> state` head must emit a state at every queried `t`; it cannot decline. Right-censoring (`p_∅`) is a first-class output here and has no counterpart there.
3. **A frame's per-pixel effective time.** Every format, method and annotation carries one scalar `t` per frame. There is no field in which a per-pixel time could be written down.
4. **Temporal uncertainty, as distinct from spatial uncertainty.** A detector under fast motion knows the object is *on the trajectory*; its ignorance is about *where along it*, i.e. about *when*. Forced into a `time -> state` head, this must be re-encoded as a large 2-D spatial covariance, which asserts something false: that the object might be off-track. **Prediction, one plot:** the true error cloud of a fast-object tracker is a 1-D curve along the trajectory (participation ratio ≈ 1), while its predicted covariance is 2-D (≈ 2). The mismatch is not miscalibration — it is the wrong variable.
5. **A state that held at several times.** A direction reversal inside one exposure makes the effective time multi-valued. A regression head returns the mean of the two — a time at which the state did *not* hold. A distribution over time returns both modes. This is the sentence we can earn: **there is no variable for "when" in the current formulation, only for "what, at a time we chose."**

---

## Why this is not <closest work>

Verified against arXiv full text and abstracts (Sept 2026). Notable empty conjunctions, checked directly: `"event camera" ∧ "censored"` → **0 results**; `"crossing time" ∧ "event camera"` → **0**; `"event camera" ∧ "temporal uncertainty"` → **0**. A 29-paper sweep of event-camera "time surface" papers (2019–2026) found **every one uses time surfaces as an INPUT representation; none regresses a timestamp map as an output**.

| Work (venue, year) | What it does | Direction of the map | Why we differ |
|---|---|---|---|
| **HOTS — Lagorce et al., TPAMI 2017**; **HATS — Sironi et al., CVPR 2018** | Decayed last-event-timestamp surfaces as a feature | time is an **input feature** | *Directly addressing time surfaces:* a time surface **encodes** when the last event fired so a downstream head can predict *what*. It is never supervised, never a distribution, never has a "never" state, and is not compared against a ground-truth time. We predict a *future/other* crossing time, supervised by held-out events, with a likelihood. Time surface : chronofield :: input image : depth map. |
| **Labits (arXiv 2412.08849, 2025)** | Layered bidirectional time surfaces; SOTA continuous **dense trajectory** estimation, 49% TEPE reduction | `t -> position` | Closest work on "continuous time," and it is the *opposite* map: query a time, get a position. TEPE is a spatial error. It cannot answer "when was it here," cannot say "never," and its supervision has no censored term. |
| **EDI — Pan et al., CVPR 2019** (+ event-deblur successors) | `B = (1/T)∫I(t)dt` with events; recover sharp `I` at a chosen `t` | `t -> intensity` | We use *the same integral*, change variables, and read it as a constraint on `∂τ/∂L` (our L4). EDI treats the exposure as an obstacle to recovering an instant; we treat it as a measurement of a measure. Same physics, swapped unknown. |
| **Time Lens / Time Lens++ (CVPR 2021/2022)** | Event-guided frame interpolation at query time | `t -> image` | Our strongest *baseline*, not our neighbor: "reconstruct at 1000 fps then run a WHAT head." Costs N forward passes, compounds reconstruction error, and produces no temporal uncertainty. |
| **UniINR (ECCV 2024, arXiv 2305.15078)** | Spatio-temporal INR `(x,y,t) -> color`; explicitly embeds **exposure time** for RS correction + deblur + interpolation | `(space, time) -> value` | The one work that takes the exposure *interval* seriously. It still uses the interval to produce values at chosen times. We invert the field: `(space, value) -> time`. Nothing in UniINR predicts a time or represents temporal ambiguity. |
| **Event-Aided TTC (ECCV 2024, arXiv 2407.07324)** | Two-step geometric fit of event normal flow → **scalar TTC** per object | `observations -> a time` ✅ | The closest existing "predict a time." Differences: one scalar per object under a looming model, vs. a dense state-indexed field; a point estimate, vs. a distribution with a `∅` atom; geometric fitting, vs. a censored likelihood; **no frames at all**, so the temporal-support question never arises. |
| **EV-TTC (Bisulco et al.)**; **EvTTC dataset (arXiv 2412.05053)** | Learned TTC from multi-scale event representations; LiDAR+GNSS/INS ground-truth TTC benchmark | scalar time / benchmark | Same scalar-vs-field, point-vs-distribution gap. EvTTC is a resource we *use*, not a formulation we restate. |
| **RVT (CVPR 2023)**; **DAGr / low-latency automotive vision (Nature 2024)** | High-rate event(+frame) detection | `t -> boxes` | Evaluated by mAP. "Low latency" means *the system answers quickly*, not *the answer is a time*. Subject to the null-space proposition in F1. |
| **FAOD (arXiv 2412.04149)** | Frames+events with an Align module and a Time-Shift training strategy for the Event–RGB Mismatch | `t -> boxes` | **The closest work on the seed itself** — and the cleanest illustration of our point. It treats temporal mismatch as a nuisance to *align away* and validates with mAP. Its headline — *80× frequency mismatch, only 3 mAP drop* — is not evidence that alignment works; it is evidence that **mAP cannot see time**. We keep the mismatch as the signal and change the output variable. |
| **Deep time-to-event / survival models (DeepSurv, DeepHit, Kvamme & Borgan arXiv 1907.00825)** | Censored likelihoods over time-to-event | `covariates -> time distribution` | The loss family we import. Never applied to event-camera perception (0 arXiv hits for the conjunction). Our contribution is the *identification*: an event is uncensored, a frame is interval-censored, a non-crossing is right-censored. |

**One-line positioning.** Time surfaces put time on the input side; INRs put time on the query side; TTC puts one time on the output side. Nobody has put a **dense, state-indexed, censored distribution over time** on the output side, and nobody has noticed that this is the natural home for a frame's exposure interval.

---

## Experimental plan

### The task where WHEN beats WHAT

**Primary: sub-frame crossing-time and time-to-contact regression for collision warning.** Metric a reviewer already respects: **time-to-collision error in milliseconds**, and — the deployment-facing version — **warning lead-time achieved at a fixed false-alarm rate**. AEB is specified in milliseconds; this is not an invented stake.

**Secondary (the well-posedness case): contact-time estimation.** Ball–paddle, foot–ground, tool–surface. Contact duration ~2–5 ms; at 30 fps, >90% of contacts fall strictly between frames. Here WHEN is not better, it is the *only* well-posed form — the conventional pipeline has no slot for the answer.

**Anchor (zero-annotation, real data, µs ground truth): next-crossing-time prediction (C1).** Hold out a temporal slice of a *real* event stream; from the preceding events + the last RGB frame (with its exposure), predict when each pixel next crosses a contrast threshold; supervise with the held-out real events. Real sensor, microsecond ground truth, no simulator, no labels. This is our insurance against every ground-truth objection and should be run first.

### Datasets and sizes

| Tier | Data | Role | Size | Risk |
|---|---|---|---|---|
| 0 | Synthetic 2-D rendered scenes (analytic `τ`) + **DVS-Voltmeter** / **ESIM** | Exact GT for F2, the eikonal, reversals | <5 GB | none |
| 1 | **X4K1000FPS** (1000 fps) and/or **GoPro/Adobe240** → ESIM events + synthesized exposure blur | Exposure sweep, `a·T²/v̄` law, controlled F1 | 40–80 GB | simulator throughput (see Risks) |
| 2 | **HS-ERGB / BS-ERGB** (Time Lens / Time Lens++) — *real* Prophesee events + real high-frame-rate color | Real-event validation with ~1–6 ms GT | ~30–60 GB *(size unverified — rate-limited; confirm at download)* | availability |
| 2 | **EVIMO2** — real events + ~200 Hz VICON object poses + masks | C2/C3 passage and contact GT | subset 20–40 GB (full ~250 GB) | 200 Hz GT is only 5 ms — supporting, not primary |
| 3 | **DSEC** subset, 6–10 sequences (**verified**: events 1.6–9.2 GB/seq, images 2.4–13.1 GB/seq; bulk is 125 GB + 216 GB — *do not* bulk-download) + `lidar_imu.zip` (26 GB) | Real driving; the mAP-vs-CTE divergence plot with real baselines | 60–100 GB | none |
| 3 | **EvTTC** (LiDAR + GNSS/INS ground-truth TTC) | The most directly respected TTC number | small *(unverified)* | small dataset |

Total ≈ 250 GB of 990 GB free. Comfortable. Everything runs in Docker; no host installs.

### Baselines (real, named, and one that could kill us)

1. **RVT (CVPR 2023)** + constant-velocity / Kalman extrapolation to the crossing time. The honest "what everyone actually does."
2. **FAOD (arXiv 2412.04149)** + the same extrapolation. The strongest event+frame detector that explicitly models the mismatch.
3. **Event-Aided TTC (ECCV 2024)** and **EV-TTC**. Geometric and learned scalar-TTC, on the TTC task.
4. **Reconstruct-then-detect: Time Lens / UniINR → 1000 fps → RVT at every virtual frame.** *This is the baseline that can kill the paper.* It must be run at matched and at unmatched compute, and reported either way.
5. **Ours-degraded**: identical network, point regression on time, frames stamped at the midpoint. Isolates the formulation from the architecture.

### Metrics

- **CTE** — crossing-time error, ms; median, P95, and fraction under `Δt_f/2`.
- **SFR (Sub-Frame Resolution ratio)** = `Δt_f / P95(CTE)`. *Invented.* Reads "how many times finer than the frame grid is the answer." **SFR ≤ 1 means the method has learned nothing the frame grid did not already give it** — it exposes methods that secretly snap to frames. Existing metrics have no null of this kind.
- **TCE (Temporal Calibration Error)** — coverage of predicted `(1−α)` time intervals vs `α`, plus reliability diagram over the time axis. *Invented, and no existing method can even be scored on it*: they emit no distribution over time.
- **CMR (Censoring-Mass Recall)** — AUC of `p_∅` against the never/occurred label. Existing methods must hallucinate a state at every `t` and cannot compete by construction; we report it as an ability, not a win.
- **FTB (Frame Timestamp Bias)** — measured per-pixel effective-time deviation, ms; validates the `a·T²/(24 v̄)` law. An analysis result, not a leaderboard number.
- **mAP** — reported *in order to show it is flat*, together with the null-space construction from F1.

**Why existing metrics are blind, stated once:** mAP, MOTA and EPE are all defined by matching to annotations at annotation times. They are invariant to any uniform temporal shift smaller than the spatial matching tolerance. A method can therefore be right at the wrong time and score identically. FAOD's 80×-mismatch/3-mAP-drop result is the field's own demonstration of this.

### Ablations

- **A1 (the decisive one): frame branch treatment** — none / midpoint-as-exact-time (universal practice) / interval-censored L2 / +dwell-measure L4. **Report split by acceleration bin.** Prediction: the midpoint hack is fine at low `a` and fails above the F1 crossover. If it does not fail, we say so; that is a finding.
- **A2:** temporal eikonal L5 on/off, and with/without motion-boundary masking.
- **A3:** output parameterization — L1 point / Gaussian NLL / discretized softmax+offset / mixture-of-logistics. Prediction: point regression collapses at direction reversals (returns the mean of two modes, a time at which nothing happened). Direct evidence that a distribution is required.
- **A4:** bin count `B ∈ {32, 64, 128, 256}` — temporal resolution vs. data efficiency.
- **A5:** exposure sweep `T ∈ {2, 5, 10, 20, 40} ms` (simulation) — the F2 curve.
- **A6:** simulated vs. real events (sim-to-real gap on the C1 anchor).
- **A7:** event-only / frame-only / both, **stratified by local contrast.** Prediction: frames matter most below the event contrast threshold, where the event branch is itself censored and the blur integral is the only evidence. If frames add nothing anywhere, the temporal-support seed is dead and we must say so.

### Compute, under 9 GB

Backbone: recurrent U-Net, ResNet-18-class encoder (~11 M params), input = 10-bin event voxel grid + one RGB frame + its exposure interval as scalar conditioning, at 320×240 crops. Head: `B+1 = 129` logits per pixel (C1 predicts the *next* crossing only, so one level, not `K`); C2/C3 use cheap per-query heads.

Memory: `320×240×129×8×4 B ≈ 0.32 GB` per activation map; with decoder activations, AMP, and optimizer state, ≈ **5–6 GB**. Fallbacks if tight: batch 4, 256×192, `B = 64`.

Throughput: ~5 it/s → **~3 GPU-h per run** at 50 k iterations.
- Core: 3 tasks × 4 configurations = 12 runs ≈ 36 h
- Ablations A2–A7 ≈ 30 h
- Baselines: use released checkpoints for RVT / FAOD / Time Lens (inference only); train only the extrapolation heads ≈ 10 h
- **Total ≈ 75–90 GPU-hours ≈ 4–6 days** on a shared 9 GB slice. Feasible if data generation starts immediately and runs on CPU in parallel.

---

## Risks

**Death 1 — clever but not useful.** Reconstruct-to-1000 fps + a strong detector matches our CTE. This is the first objection any reviewer will make and it is live.
*Falsification criterion, stated before we run:* if Time Lens → RVT reaches P95 CTE within 15% of ours at equal-or-lower compute on BS-ERGB, the accuracy claim is dead. *Fallbacks in order:* (a) compute — one forward pass vs. `N`, quantified; (b) **calibrated temporal uncertainty (TCE)**, which the reconstruct-then-detect pipeline structurally cannot produce; (c) the censoring/`∅` capability; (d) the regimes where reconstruction itself fails — low light, HDR, and speeds above the interpolator's training distribution. If none of (a)–(d) survives, the idea is dead and we should say so rather than dress it up.

**Death 2 — no real sub-frame ground truth, so the whole evaluation is simulation.** EVIMO2's 200 Hz VICON is only 5 ms — barely better than the problem. *Fallbacks:* (a) the **C1 anchor** — held-out *real* events are microsecond-exact ground truth for a real WHEN task, with no simulator and no annotator in the loop; run it first and lead with it; (b) HS-ERGB/BS-ERGB real high-frame-rate color as GT with real events as input; (c) EvTTC's LiDAR+GNSS/INS TTC for the driving number. We do not have an event camera on hand, so a custom rig is not a fallback we can promise.

**Death 3 — it reduces to something known.** "This is a time surface." / "This is TTC." / "This is optical flow with the variables shuffled — `∇τ` *is* slowness, you said so yourself." The last version is the dangerous one, because we derive it.
*Answer, which must be demonstrated, not asserted:* flow-and-extrapolate is a local first-order model. At a **direction reversal** it is not merely less accurate — extrapolation is ill-posed, while the chronofield's bimodal posterior is correct and calibrated. At a **contact**, flow has no notion of the event at all. And neither flow nor a time surface has a `∅` atom or a censored likelihood, so neither can consume a frame as an interval. If the reversal and contact experiments do not separate us from flow-and-extrapolate, this risk stands and the paper is a reparameterization.

**Death 4 (secondary) — the frame branch contributes nothing measurable**, which would gut the temporal-support seed and leave an events-only paper. Covered by A7's contrast stratification; the predicted refuge is the sub-threshold regime where the blur integral is the only evidence. If A7 comes back flat, the honest paper is "events-only chronofields," a smaller contribution that no longer answers the assigned seed.

**Operational risk (not a death):** v2e is far too slow for this volume. Use **DVS-Voltmeter (ECCV 2022)** or **ESIM**, and downsample 4K sources to 480p *before* simulation. Budget simulation as CPU-days running in parallel with training, not as a blocking step.

---

## Self-score

*Conventions stated explicitly: novelty, feasibility and reviewer-proof-ness are 1 = bad, 10 = good. **Incrementality is scored 10 = maximally incremental/derivative (bad), 1 = genuinely changes what is computed (good).***

| Axis | Score | Harsh justification |
|---|---|---|
| **Novelty** | **8 / 10** | The key arXiv conjunctions come back empty (`event camera ∧ censored` = 0; `crossing time ∧ event camera` = 0; `event camera ∧ temporal uncertainty` = 0), and 29 time-surface papers all use time as input, none as target. The specific combination — dense state-indexed time field + exact/interval/right-censored likelihood + dwell-time change of variables + temporal eikonal `∇τ·v = 1` — appears unoccupied. **Docked two points:** "invert the query" is the kind of framing a hostile reviewer calls rhetorical, scalar TTC already predicts a time, and the C1 photometric instantiation is uncomfortably adjacent to next-event-time prediction, which is folklore even if unpublished under that name. |
| **Feasibility** | **7 / 10** | 9 GB is genuinely ample for this network; the training budget (~80 GPU-h) fits in a week. The C1 anchor needs no simulator, no labels, no annotation. **Docked:** the plan as written names six datasets and must be cut to two before anyone starts; simulator throughput is the real schedule risk, not the GPU; and reproducing FAOD/RVT baselines faithfully enough that a reviewer believes the comparison is a week of unglamorous work not counted above. |
| **Reviewer-proof-ness** | **5 / 10** | The weakest axis, and honestly so. "Clever but not useful" is a live, reasonable objection that we cannot pre-empt with argument — only with the reconstruct-then-detect experiment, which might lose. Worse, the metric story ("mAP is blind, so we invented CTE, SFR and TCE") reads from a distance exactly like *inventing a metric you win on*. The null-space proposition and the two-systems-identical-mAP construction are the only defense, and they are a defense against the *form* of the objection, not its substance. Everything rests on the F1 crossover verifying and on beating Time Lens→RVT. |
| **Incrementality** | **3 / 10** *(low = good)* | It changes the output type, the loss family, and the evaluation protocol — not the architecture. That is a formulation change, not a module. **Not lower because:** the backbone is entirely standard, the gains are predicted to be confined to a high-acceleration regime that a reviewer may call a corner case, and one component (L4) is admittedly EDI with the variables renamed. |

**Overall verdict.** The idea is alive and worth building, but it lives or dies on a single experiment: reconstruct-then-detect versus the chronofield on real events. Run the C1 anchor and that head-to-head **first**, before writing a line of the paper. If the head-to-head is a tie, retreat to calibrated temporal uncertainty and censoring — a smaller but honest paper — and if that will not carry, kill it.

---

## 한국어 요약

**핵심 주장.** 모든 인지 헤드는 `시간 -> 상태` 사상이다. 이를 `상태 -> 시간`으로 뒤집어, 질의된 상태(명암 교차, 공간 통과, 접촉, 선 횡단)에 대해 **"언제 성립했는가"의 분포**를 예측하는 *크로노필드*를 제안한다. 이벤트는 **정확한(uncensored)** 시각 관측으로, 프레임은 **구간 절단된(interval-censored)** 관측으로 동일한 가능도에 들어간다. 특징 결합이 아니라 관측 모델이 둘인 하나의 잠재 변수다.

**죽이는 가정.** "프레임에는 타임스탬프가 있다." 프레임은 노출 구간 위의 적분, 즉 시간축 위의 *측도*이지 점이 아니다. 노출 중점을 찍는 관행은 등속 운동을 가정한 최대가능도 점추정이며, 이벤트가 필요한 바로 그 상황에서 틀린다. 유효 시각 편향 `Δt ≈ aT²/(24 v̄)`(노출 20 ms, 강한 감속에서 8.3 ms = 노출의 42%)이며, 노출 중 방향 전환이 일어나면 **다치(multi-valued)** 가 된다 — 오차가 아니라 타입 오류다.

**실패 현상.** mAP는 평평한데 횡단시각 오차(CTE)는 선형으로 증가한다. 더 강하게, mAP는 정합 허용오차보다 작은 균일 시간 이동에 대해 **불변**이므로 "맞는 시각에 맞춘 방법"과 "틀린 시각에 맞춘 방법"을 구분할 수 없다. FAOD가 보고한 "80배 주파수 불일치에서 mAP 3점 하락"은 정렬이 잘 된 증거가 아니라 **mAP가 시간을 보지 못한다는 증거**다.

**검증 결과.** arXiv 전문 검색에서 `event camera ∧ censored` 0건, `crossing time ∧ event camera` 0건, `event camera ∧ temporal uncertainty` 0건. 타임서피스 논문 29편 전수 확인 결과 **전부 입력 표현이며 출력으로 회귀하는 사례 없음**. 가장 가까운 연구는 Labits(시간->위치, 반대 방향), UniINR(노출 구간을 다루지만 시간이 질의), 이벤트 기반 TTC(객체당 스칼라 하나).

**최대 위험.** "영리하지만 쓸모없다." Time Lens로 1000 fps 복원 후 검출하는 베이스라인이 CTE에서 비기면 정확도 주장은 죽는다. 반증 기준을 미리 명시했고(P95 CTE 15% 이내면 사망), 후퇴선은 연산량·시간 불확실성 보정(TCE)·절단(`∅`) 능력이다. 셋 다 무너지면 아이디어를 접는 것이 정직하다.

**점수(엄격).** 독창성 8 / 실현가능성 7 / 리뷰어 방어력 5 / 증분성 3(낮을수록 좋음). **먼저 할 일:** 시뮬레이터 없이 실제 이벤트만으로 되는 C1 앵커 실험과, Time Lens→RVT 정면 대결. 논문은 그 뒤에 쓴다.
