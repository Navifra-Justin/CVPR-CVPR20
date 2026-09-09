# When Is Your Prediction? Event–RGB Fusion Silently Invents a Timestamp

*Team 4 — the failure-phenomenon team. Domain: Temporal-Support-Aligned Event–RGB Perception. Plain fusion is not the contribution; the diagnosed failure and the change-of-support reformulation are.*

---

## One-sentence thesis

A frame is not a measurement of the scene *at* a time, it is an integral of the scene *over* a time interval, so a fused event–RGB predictor trained to output a state "at time `t`" does not output the state at `t` — it outputs the state at the **evidence-weighted time centroid**, a quantity that moves with exposure length, event-window offset, object speed, and scene texture, and that differs **between regions of a single frame**, so the prediction has no single timestamp at all.

---

## The assumption we kill

**The instantaneity assumption** (equivalently: the *point-observation* assumption).

Every event–RGB pipeline we could find writes, explicitly or in its dataloader, some version of

```
x_t = [ Frame(t) , EventVoxel(t-W, t) ]   →   f_theta(x_t)  →   y_hat  ≈  y*(t)
```

and then treats the residual `y_hat - y*(t)` as *localization error*. Three sub-assumptions are hidden in that line, and all three are false under fast motion:

1. **The frame is a point sample.** It is not. With exposure `[a,b]`, the frame is the linear functional `F = (1/(b-a)) ∫_a^b L(s) ds` of the radiance path. It constrains a *time-average* of the state, not the state at any instant. Fusing it with events therefore equates an integral measurement with a family of point measurements — a **type error**, not a synchronization error.
2. **The two modalities have the same support.** They do not. The frame's support is `[a,b]` (an interval whose *weighting* is the per-instant contrast energy of the moving object, not the uniform density); the event stream's support is `[t-W, t]` with a genuinely point-wise weight per event. Their time centroids differ by milliseconds even when the *hardware is perfectly synchronized*. Beam-splitter rigs (PEOD, EventAid, spacecraft-pose work) remove parallax and clock skew and do **not** remove this.
3. **The label has no support either.** Boxes drawn on a blurred frame, or mocap poses sampled at 240 Hz and assigned to a frame index, inherit their own support. The "ground-truth clock" is itself a convention.

The field's current best answer to (2) is to enforce **invariance** to temporal shift. FAOD's *Time Shift* strategy explicitly trains the model to produce the *same* prediction from temporally shifted Event–RGB pairs, and reports success as a *flat* accuracy curve under an 80× frequency mismatch (1.2 mAP drop where baselines drop ~10). We claim this is the disease presented as the cure: **a detector whose output does not change when you shift the temporal support is a detector that has thrown time away.** Under fast motion the correct answer *must* change with the support, because the scene changed. Invariance is not correctness; here it is a certificate that the model is emitting an untimed object.

We name the correct framing: event–RGB perception is a **change-of-support problem** (in the spatial-statistics sense: combining observations whose measurement supports differ), not an alignment problem. To our knowledge that name has never been applied in this literature.

---

## The failure phenomenon

### 4.0 The primitive we introduce: the effective timestamp `τ̂`

Everything below rests on one measurement primitive. Standard evaluation asks *"how wrong is the prediction at the time we asked for?"* We instead ask *"at what time would this prediction have been right?"*

Given a continuous ground-truth trajectory `y*(·)` (available only when GT rate ≫ prediction rate — this is why the phenomenon has never been measured) and a prediction `ŷ` nominally for query time `t_q`, define

```
τ̂  =  argmin_{t ∈ S}  d( ŷ , y*(t) )            (effective timestamp / time-of-agreement)
r_min = min_{t ∈ S} d( ŷ , y*(t) )              (irreducible, non-temporal residual)
r_q   = d( ŷ , y*(t_q) )                        (what the field currently reports as "error")
TEF   = 1 - r_min / r_q                          (Time-Explained Error Fraction ∈ [0,1])
```

with `S` the joint support `[min(a, t_q-W), max(b, t_q)]`, `d` = box-center L2 (or 6-DoF geodesic for pose). `TEF = 0.9` means 90% of what the community reports as a fast-motion localization failure is a **clock** failure: the model is *right*, at the wrong time.

Two derived statistics carry the argument:

```
Temporal bias        b   = E[ τ̂ - t_q ]                        (over a condition)
Temporal dispersion  σ_τ = std of τ̂ over objects/regions WITHIN one frame
```

`b ≠ 0` alone is only a calibration offset — a reviewer will say "subtract it." `σ_τ > 0` is the kill shot: **no scalar clock correction exists**, because different parts of the same output live at different times.

### 4.1 The law we predict (and it is derivable, which is why the experiment is sharp)

Train with an L2/L1 objective and labels at the conventional clock `t_q` (the exposure midpoint). The Bayes-optimal deterministic predictor is `ŷ = E[y*(t_q) | F, E]`. Write the *evidence weight density* `w(t)` over `S`: the instantaneous informativeness of the observations about the state at time `t` (for the frame branch, `w` is proportional to the moving object's contrast energy deposited at instant `t` in the exposure; for the event branch, `w` is proportional to local event rate). Let

```
t̄ = ∫_S t w(t) dt / ∫_S w(t) dt        (evidence-weighted time centroid)
```

**Claim (first-order).** For locally linear motion, `ŷ ≈ y*(t̄)`, hence `τ̂ ≈ t̄`, *regardless of the label clock used in training.* The network was **told** the right time and still cannot deliver it, because the evidence does not contain a separable point-evaluation at `t_q`.

Three consequences, each an experiment:

- **(C1)** `τ̂ - t_q` grows with exposure length `T_exp` and with event-window offset `Δ`, and is (to first order) **independent of speed `v`** — while the resulting *position* error grows as `|τ̂ - t_q| · v`. So the field's "fast motion is hard" curves are a speed-scaled projection of a single latent timing variable.
- **(C2)** `τ̂` is set by *w(t)*, i.e. by **scene content**, not by the clock. Hold the clock, the exposure, and the speed fixed; move the object's contrast energy to the first half of the exposure; `τ̂` moves earlier. A timestamp that depends on texture is not a timestamp.
- **(C3)** `w(t)` is *local* (per-object, per-region), so `τ̂` is a **field over the image**, not a scalar. Two objects at different speeds in one frame ⇒ two different effective timestamps in one prediction.

### 4.2 Measurement design — four figures

All four use the same probe (§4.0). Independent variables are swept *independently*, which is only possible in a controlled simulator; §8 says how each is closed on real data.

**Figure 1 — the failure diagram (support-offset sweep).**
- Independent variable: nominal event-window offset `Δ ∈ [-20, +20] ms` in 1 ms steps (the event window is `[t_q + Δ - W, t_q + Δ]`), one curve per object speed `v ∈ {250, 500, 1000, 2000, 4000} px/s`, at fixed `T_exp = 10 ms`.
- Axes: **x = Δ (ms)**, **y = center error at the declared time `t_q` (px)**.
- Expected curve: each curve is a **V** whose vertex sits at `Δ* ≠ 0`, and `Δ*` **shifts with `v`** — the network has silently learned a speed-dependent temporal calibration that the formulation says cannot exist. The V's slope is `∝ v`, so the curves fan out; the vertex locus `Δ*(v)` is the new object.
- *What proves the formulation is wrong rather than merely inaccurate:* an inaccurate model gives a V with its vertex at `Δ* = 0` and a nonzero floor. A **mis-formulated** model gives `Δ* ≠ 0` with a floor near the noise level — it is not failing to see, it is seeing a different instant.

**Figure 2 — the collapse plot (the centerpiece).**
- Pool every condition: `T_exp ∈ {0.5, 2, 5, 10, 20} ms` × `v ∈ {250…4000} px/s` × `W ∈ {1, 5, 10, 20} ms` × `Δ ∈ [-20,+20] ms` (≈2000 condition cells, 3 seeds).
- Axes: **x = predicted temporal displacement `(τ̂ - t_q) · v` (px)**, **y = observed error `r_q` (px)**.
- Expected: **all conditions collapse onto a single line of slope 1**, R² > 0.9. A collapse across four independent variables is the strongest available evidence that one latent variable — the timestamp — generates the error. It converts a scatter of "hard conditions" into a law.
- Companion panel: **x = `T_exp` (ms)**, **y = `b = E[τ̂ - t_q]` (ms)**, one line per `v`. Expected: lines lie on top of each other (bias is speed-independent), slope ≈ 0.2–0.4 (i.e. `b ≈ 0.25·T_exp`).

**Figure 3 — within-frame temporal dispersion (kills "just recalibrate").**
- Scenes contain 2–5 objects with *different* speeds and textures in the same frame.
- Axes: **x = τ̂ - t_q (ms)** as a histogram / violin per object-speed group; and a spatial heat map of `τ̂` over the image.
- Expected: **multi-modal**, with modes separated by ≥ 2 ms at `T_exp = 10 ms`; `σ_τ` grows with the spread of per-object evidence quality. A single prediction tensor thus carries several timestamps at once. *This is the exact analogue of "you measure the occluder's depth, not the target's": you ask for the state at `t`, you get a mosaic of states at times you never asked for.*

**Figure 4 — content control (kills "just synchronize better").**
- The clock, exposure, speed, event rate, and trajectory are **held fixed**. The only manipulation is the *texture asymmetry index* `A = (contrast energy in [a, (a+b)/2]) / (total contrast energy in [a,b])`, swept over `A ∈ [0.1, 0.9]` by making the object traverse a background/illumination gradient, or by modulating its own albedo pattern over the exposure.
- Axes: **x = A**, **y = τ̂ - t_q (ms)**.
- Expected: **monotone decreasing**, spanning ≥ 0.3·`T_exp` (≥ 3 ms at `T_exp = 10 ms`), with the clock provably untouched. A timestamp that is a function of scene content is not a property of the sensor system; it is an artifact of the formulation.

### 4.3 Quantitative prediction (falsifiable, pre-registered)

At `T_exp = 10 ms`, `W = 10 ms` ending at `t_q` (a standard configuration; the two support centroids are ~5 ms apart):

| Quantity | Predicted | Falsified if |
|---|---|---|
| `b = E[τ̂ - t_q]` | `≥ 0.25 · T_exp` for `T_exp ≥ 5 ms`, i.e. `≥ 2.5 ms` | `\|b\| < 0.5 ms` |
| Speed-dependence of `b` | `\|∂b/∂v\| · v_range < 0.3·b` (bias ~speed-independent) | `b` scales with `v` (⇒ it is a latency, not a support effect) |
| `σ_τ` within one frame | `≥ 0.15 · T_exp` (≥ 1.5 ms) | `σ_τ < 0.3 ms` |
| `TEF` at `v ≥ 1500 px/s` | `≥ 0.5` | `TEF < 0.15` |
| Collapse (Fig. 2) | slope `1.0 ± 0.15`, R² `> 0.9` | R² `< 0.5` |
| Content effect (Fig. 4) | `\|dτ̂/dA\| · 0.8 ≥ 0.3·T_exp` | slope indistinguishable from 0 |

Why these magnitudes matter for the metrics the field actually reports: a `b = 5 ms` bias at `v = 1000 px/s` is a 5 px shift; on a 50 px box that is IoU `45/55 = 0.82` — invisible at AP50, fatal at AP90. At `v = 4000 px/s` it is 20 px, IoU `30/70 = 0.43` — the detection is a **false positive at AP50 caused entirely by a timing error**, while the model's picture of the world is correct. That is the fourth candidate from the brief made concrete: benchmark accuracy and temporal correctness have been decoupled, and point-labeled GT cannot see it.

### 4.4 What a NULL result looks like (and we will report it)

Null = **the instantaneity assumption is fine and the residual is genuine perception error**:
- Fig. 1 vertices at `Δ* = 0 ± 1 ms` for every speed, with the V floor equal to the error at `Δ=0`.
- Fig. 2 no collapse (R² < 0.5); error better explained by blur magnitude `v·T_exp` alone than by `(τ̂-t_q)·v`. **Critical control:** blur magnitude and temporal displacement are correlated by construction, so we must sweep `T_exp` and `v` on a grid and show the collapse holds along the anti-diagonal (constant `v·T_exp`, varying `τ̂`). If the collapse only works when it is a proxy for blur, the finding is dead.
- `σ_τ ≈ 0` ⇒ the phenomenon is a global constant offset ⇒ this is *temporal calibration*, a solved and boring problem; we would say so and pivot.
- Fig. 4 flat ⇒ no content dependence ⇒ again just calibration.
- Additional null-check: `τ̂` is unidentifiable (the argmin is flat) whenever the local trajectory is a straight line at constant speed, because then a spatial shift and a temporal shift are the same thing. We therefore **only** claim `τ̂` on segments with measurable curvature/acceleration, and we report the identifiability margin (curvature of `d(ŷ, y*(t))` at the argmin) for every measurement. A paper that skips this is refutable in one reviewer sentence.

---

## The reformulation

The failure says: the output state space has no time coordinate, and the observation model has the wrong type. Fix both.

**State space.** Replace the point state `y ∈ R^k` with a **time-parameterized trajectory segment plus its own support density**, both defined on the joint support `S = [t_0, t_1]`:

```
ŷ(t) = Σ_{k=0}^{K} c_k B_k(t)          # cubic B-spline, K=3, or  p + v·(t-t_q) + ½a·(t-t_q)²
ŵ(t) = softmax over M bins of S        # ŵ ≥ 0, ∫_S ŵ(t) dt = 1
τ̂ = ∫_S t·ŵ(t) dt ,  σ̂_τ² = ∫_S (t-τ̂)²·ŵ(t) dt
```

The head therefore emits `(c_0..c_K, ŵ)` per object: **where**, **how it is moving**, **when the answer is valid**, and **how tightly**. `σ̂_τ` is a first-class output: "I know where but not when" becomes expressible.

**Observation model — the type error is repaired by making the frame an integral.**

```
L = L_pt + λ1·L_frame + λ2·L_event + λ3·L_time
```

1. `L_pt = Σ_k ρ( ŷ(t_k) − y*(t_k) )` — supervision evaluated at **the label's own clock** `t_k`, which is now representable.
2. `L_frame = || (1/(b−a)) ∫_a^b R(ŷ(s)) ds − F ||₁` where `R(·)` renders the object's soft footprint. Discretize with `M = 16` sub-times. This says: *the blurred frame is the time-average of the state along the predicted path.* It is the only term that gives the frame its correct type, and it is what makes `T_exp` an input rather than a nuisance.
3. `L_event = −(1/N) Σ_i log σ( s(x_i, y_i ; ŷ(t_i)) )` — **each event supervises at its own timestamp `t_i`**, with no accumulation into a voxel grid. Events become point evaluations of the trajectory; the representation unit changes from "a tensor at a time" to "a constraint on a path."
4. `L_time = (τ̂ − t*)² / (2σ̂_τ²) + log σ̂_τ`, with `t* = argmin_t d(ŷ(t), y*(t))`, a heteroscedastic NLL that **calibrates the declared timestamp**. Without this the model can emit a trajectory and lie about which part of it it believes.

**Identifiability.** Events alone identify `ŷ(·)` up to the contrast threshold and up to a global spatial offset; the frame contributes exactly one integral moment, which pins the offset. Curvature `a ≠ 0` is what separates a temporal shift from a spatial shift — hence §4.4's identifiability margin is not a caveat bolted on, it is the same quantity that makes the reformulation well-posed. We can state a small proposition: *for constant-velocity motion the pair (spatial offset, temporal offset) is unidentifiable from any support-averaged observation; identifiability is restored at order `‖a‖·(Δt)²`.* That proposition simultaneously explains the failure and licenses the fix.

**Evaluation must change too — `sAP-τ` (support-aware AP).** A detection `(ŷ, τ̂)` is a true positive iff `IoU(ŷ(τ̂), y*(τ̂)) > θ` **and** `|τ̂ − t_q| < δ`. Sweep `(θ, δ)`. Under `sAP-τ`, being right at the wrong time is a false positive — the failure now costs something, which is the whole point of the fourth candidate in the brief. Legacy mAP is reported alongside, and we predict the two disagree most exactly where `TEF` is highest.

---

## What existing methods cannot express

| Cannot express | Why | Consequence today |
|---|---|---|
| **The time of its own output.** | The output space is `R^k`; no time coordinate exists. | A timing error is silently re-reported as a localization error. |
| **A per-region timestamp field.** | One output tensor, one implicit clock. | `σ_τ > 0` is invisible; global sync/calibration fixes are applied to a spatially varying problem. |
| **An integral observation.** | Frames and event voxel grids are both cast into "a tensor indexed by `t`". | Fusion equates `∫w(s)y(s)ds` with `y(t)`. |
| **Temporal uncertainty separate from spatial uncertainty.** | Confidence is a class score. | "Sharp box, unknown instant" and "blurry box, known instant" get identical confidences. |
| **That the label has a support.** | GT is a point tuple `(t, box)`. | Point-labeled benchmarks are structurally blind to the failure — the metric cannot see the error. |
| **A prediction *between* two labels that is checked against the truth there.** | Interpolated GT is used for evaluation but the model still emits one untimed answer per interval. | High-frame-rate claims (240 Hz tracking) are evaluated against interpolated GT with no check that the output's own timestamp is what was asked. |
| **Exposure length as an input.** | `T_exp` is not in the interface of any fused detector we found. | The same model applied to a 1 ms and a 20 ms exposure has two different effective clocks and no way to know it. |

---

## Why this is not <closest work>

| Work (venue, year) | What it does | Why ours is different |
|---|---|---|
| **FAOD — Frequency-Adaptive Low-Latency Object Detection Using Events and Frames** (arXiv 2412.04149; PKU-DAVIS-SOD, DSEC-Det) | Names "Event–RGB Mismatch"; Align Module + **Time Shift** training that forces the prediction from temporally *shifted* pairs to match the unshifted one; success = flat accuracy under 80× frequency mismatch (1.2 vs ~10 mAP drop). | **This is our antagonist, not our ancestor.** They sweep temporal shift as a *nuisance to be made invariant*. We show the flat curve is the pathology: under fast motion the correct answer must change with the support. We never enforce invariance; we *measure* `τ̂` and make the model declare it. They never measure the effective timestamp, never sweep `T_exp`, never report `σ_τ`. |
| **AFNet — Frame-Event Alignment and Fusion Network for High Frame Rate Tracking** (CVPR 2023; FE240hz, 240 Hz) | Event-guided cross-modal alignment (ECA) + cross-correlation fusion; tracks at 240 Hz between frames. | Aligns *features* spatially to a single implicit instant, then emits an **untimed** box. We show that box's `τ̂` is not the queried time, is speed- and content-dependent, and disperses within a frame. AFNet is one of our probe subjects, not a baseline we beat on their metric. |
| **Flow-Guided Registration for RGB–Event Semantic Segmentation** (arXiv 2505.01548, 2025) | Names fusion "ill-posed" under spatiotemporal + modal misalignment; "registers first, then fuses" using temporally aligned flow. | Closest in *spirit*, and the strongest competing framing. But registration presupposes **a single target time to register to**. Our finding is that no such time exists per-frame (`σ_τ > 0`), and that the frame is an integral that cannot be registered to an instant without discarding information. Registration is a special case of our formulation with `ŵ(t) = δ(t − t_q)`. |
| **Sayed & Brostow, Improved Handling of Motion Blur in Online Object Detection** (CVPR 2021) | Identifies spatial ambiguity from blur — is the box the object at the exposure start, midpoint, end, or the union? Fixes it with bespoke label generation + blur-category conditioning; RGB only, blurred COCO. | Same intuition, five years earlier, in a world with **no second clock**. They resolve the ambiguity by *legislating a label convention*. We show that with events present the model resolves it by itself, differently in different regions, and that the resulting clock is measurable, content-driven, and wrong. They also never measure the effective timestamp of the detector's output. |
| **REFID / A Unified Framework for Event-based Frame Interpolation with Ad-hoc Deblurring** (CVPR 2023 / T-PAMI 2025); **EVDI** (CVPR 2022) | Restore latent *sharp images* at arbitrary times inside the exposure; explicitly note that "the timestamp of the deblurred image is traditionally assumed to be the exposure midpoint"; EVDI needs exposure known exactly. | Generative reconstruction already has a time coordinate — because a rendered image *must* be indexed. We show that **discriminative** fused perception (detection / tracking / pose / segmentation) dropped that coordinate and never noticed, and we quantify the price in task space. Our `L_frame` borrows the double-integral image formation from this line and imports it into a *task* head. |
| **UniINR** (ECCV 2024), **EvShutter** (CVPR 2023), **EvUnroll** | Event-guided rolling-shutter correction: per-row timestamps, spatial-temporal INR queried by `(x, y, t)`. | Rolling shutter is the one accepted case of a spatially varying timestamp — but it is a **known, deterministic sensor property with a closed-form row→time map**, and these papers *correct* it. Ours is a spatially varying timestamp **induced by the fusion**, present in global-shutter data, with no closed form, driven by scene content. Their existence is our best rhetorical asset: the field already accepts that a spatially varying timestamp is a real defect worth a CVPR paper; we show one nobody knew existed. |
| **FE-TAP — Tracking Any Point with Frame-Event Fusion at High Frame Rate** (arXiv 2409.11953) | EvoFusion models image generation guided by events across frequencies; reports **expected feature age** (+24% on EDS). | "Feature age" = how long a track survives. It is a *duration*, not a *timestamp*; it says nothing about whether a point's reported position corresponds to the requested instant. Orthogonal metric, orthogonal claim. |
| **SODFormer** (T-PAMI 2023), **TAPFormer** (arXiv 2603.04989), **MambaTrack / Event-Adaptive State Transition** (arXiv 2604.13426) | Asynchronous / streaming fusion; unified "transient" representation continuously updated; event-density-adaptive temporal modeling. | All improve *when the model can answer*. None change *what time the answer is about*: the output is still a point state with an implicit clock. Density-adaptive temporal modeling in fact makes `ŵ(t)` more content-dependent, so by our theory it should make `σ_τ` **worse** — a prediction we will test on MambaTrack-style density adaptation. |
| **DejaVu / Temporal Misalignment Attacks against Multimodal Perception** (arXiv 2507.09095, 2025) | Adversarial clock manipulation on camera–LiDAR; up to 88.5% mAP loss from one-frame LiDAR delay; AION defense via contrastive smoothing + DTW. | An **attack** requires a broken clock. Our failure occurs with perfect hardware synchronization, on beam-splitter data, with no adversary — it is intrinsic to fusing an integral with a point process. Their defense (smooth the representation across time) is another invariance fix and would, by our theory, increase `b` and `σ_τ`. |
| **PEOD** (AAAI 2026), **EventAid**, beam-splitter Event–RGB rigs | Pixel- and time-aligned Event–RGB benchmarks via beam splitters; sync at microsecond level. | These datasets are the ideal *proof* that the community believes hardware sync closes the issue. We use PEOD-class data to show the residual survives perfect sync, because sync equalizes clocks, not supports. |

**Verdict of the search:** the ingredients exist separately — exposure-midpoint ambiguity (RGB-only, 2021), arbitrary-time latent reconstruction (generative), shift-robustness training (FAOD), spatial+temporal registration (2025), rolling-shutter timestamp fields — but **no paper measures the effective timestamp of a fused event–RGB task prediction, none reports that it varies within a frame, and none frames event–RGB fusion as a change-of-support problem.** We found no prior report of the specific failure. Proceeding, not pivoting.

---

## Experimental plan

### 8.1 Pilot — runnable this week (target: 3 days, ~3 GPU-hours, < 7 GB VRAM)

The pilot must establish Fig. 1 and Fig. 2 with the **simplest possible fusion model**, because a failure demonstrated on an exotic architecture is an architecture bug, while a failure demonstrated on the most trivial fusion is a formulation bug.

**Day 1 — controlled generator (no external download, zero availability risk).**
- Analytic scene: 2–5 textured sprites (CIFAR/DTD crops) on a textured background, moving on quadratic paths `p(t) = p0 + v·t + ½a·t²` with controlled `‖a‖ > 0` (needed for `τ̂` identifiability). Resolution 346×260 (DAVIS346-matched). Render **10 kHz** sub-frames by GPU affine warping — this is a batched `grid_sample`, so 500 sequences × 1000 sub-frames renders in ~10 min on one GPU.
- **Frame** = mean of sub-frames over `[a,b]`, `T_exp` swept. **Events** = threshold the log-intensity of the same 10 kHz stack (ESIM-style) plus a v2e-style noise model (per-pixel threshold mismatch `σ=0.03`, refractory period, leak). *Crucially, rendering natively at 10 kHz removes v2e's SuperSloMo dependency* (a Google-Drive checkpoint = the single biggest availability risk in the standard v2e pipeline). We cross-validate a subset against real `v2e` and `DVS-Voltmeter` in a second Docker image.
- Ground truth `y*(t)` is **analytic and exact at any `t`** — `τ̂` is measured with zero GT interpolation error. No real dataset can do this; this is why the simulator is not a convenience but the instrument.

**Day 2 — baseline and training.**
- Model: two-branch ResNet-18 (RGB frame; 5-bin event voxel grid), concat at stride 8, CenterNet-style head → box center + size. ~11 M params. 10 k samples, 30 epochs, batch 16, AMP, `T_exp=10 ms`, `W=10 ms`, `Δ=0` at training, labels at the exposure midpoint. **≈ 1 GPU-hour, ~5 GB.** One Docker image (`pytorch:2.x-cuda12.x` + torchvision + numpy/scipy/matplotlib), no host installs.
- Deliberately train at a *single* configuration and probe at many — the point is that the network cannot generalize its clock, and cannot even hold it fixed.

**Day 3 — the probe and the four figures.**
- Sweep `Δ ∈ [-20,+20] ms` × `v ∈ {250…4000}` × `T_exp ∈ {0.5,2,5,10,20}` at inference (no retraining) → Fig. 1, Fig. 2, Fig. 3.
- Content control (Fig. 4): re-render the *same* trajectories with albedo modulated over the exposure to set `A ∈ [0.1,0.9]`; probe. ~30 min.
- Report `b`, `σ_τ`, `TEF`, collapse slope/R², identifiability margins, and the anti-diagonal blur control from §4.4.

**Pilot go/no-go:** the idea lives iff Fig. 1 vertices are at `|Δ*| > 1 ms` with the speed-dependent locus, AND `σ_τ > 0.3 ms`, AND the collapse survives the constant-`v·T_exp` anti-diagonal control. If not, §9 fallback.

### 8.2 Real-data closure — which dataset closes which loop

The plan is: **simulation establishes the law; real data shows it survives outside the simulator.** `τ̂` requires GT at a rate far above the frame rate, which eliminates most event–RGB benchmarks immediately.

| Dataset | Why / what it closes | Approx. size | Availability risk |
|---|---|---|---|
| **FE240hz / FE108** (DAVIS346, 82 seq, ~143 k frames, **240 Hz Vicon boxes**, HDR + low-light + blur + fast motion) | **Primary loop-closer.** The only public event+frame set with box GT far above the frame rate → `τ̂` measurable to ~1 ms after spline interpolation. AFNet's own benchmark, so probing AFNet checkpoints here is maximally pointed. | est. 50–100 GB (unconfirmed) | **Medium** — author-hosted (zhangjiqing.com); Baidu-only mirrors would hurt. Mitigate by starting the download on day 1. |
| **EVIMO2** (3× 640×480 event cams + 2080×1552 color cam, 173 seq, 41 min, **200 Hz Vicon object poses**, regenerable masks to 200 Hz) | Second loop-closer, different task (6-DoF pose / segmentation) and different `d(·,·)`. Shows the failure is not detection-specific. | full set large (hundreds of GB); use the npz subsets (~tens of GB) | **Medium** — well hosted, but the full set is big; take the "independently moving objects" subset (3.75 min) first. |
| **BS-ERGB / HS-ERGB** (beam-splitter Prophesee Gen4M + Flir; high-speed RGB) | Closes the **content-control** loop (Fig. 4) on real optics with **no parallax and hardware sync** — proving the effect is not a sync artifact. High-FPS RGB provides sub-frame appearance GT. | tens of GB | **Low** — uzh-rpg download page. |
| **DSEC / DSEC-Detection** (20 Hz RGB + Prophesee Gen3.1, µs sync) | Not usable for `τ̂` (labels at frame rate) — used instead to demonstrate the **consequence**: `sAP-τ` vs mAP disagreement, and to train the reformulated model at scale. | ~150 GB full; Detection subset far smaller | **Low** — ETH/UZH. |
| **PKU-DAVIS-SOD** | FAOD's benchmark; needed only to compare against FAOD on its home turf. | unknown | **Medium-high** — China-hosted. Optional. |
| **PEOD** (AAAI 2026, 1280×720 EVK4 + RGB beam-splitter) | Ideal "perfect sync still fails" demonstration if released in time. | unknown | **High** — very new. Treat as bonus. |
| **MVSEC / N-Caltech101 / Gen1 / 1Mpx** | Not applicable — no high-rate GT, or no paired RGB. | — | — |

**Simulator cross-check:** `v2e` and `DVS-Voltmeter` (both pip/GitHub installable in Docker) applied to the same 10 kHz renders, to prove the phenomenon is not an artifact of our event model. Also re-render a subset with **Blender/Cycles** with true motion blur to prove it is not an artifact of our compositing.

### 8.3 Baselines to probe (we do not need to beat them; we need to indict them)

1. Our trivial two-branch CenterNet fusion (formulation-level evidence).
2. **AFNet** (CVPR'23) checkpoint on FE240hz — the strongest "high-frame-rate frame-event" claim.
3. **FAOD** (if weights release) — the invariance-trained model; our theory predicts it has the **largest** `σ_τ` and the flattest, least meaningful Fig. 1, because it was trained to be blind to the support.
4. **CEUTrack** (COESOT) — a plain unified transformer, for a no-alignment control.
5. **Events-only** and **frame-only** ablations — these are the two crucial controls, because a single modality has a *single* support, so our theory predicts `σ_τ ≈ 0` for both and `σ_τ > 0` only under fusion. **If `σ_τ` is just as large for the frame-only model, the phenomenon is not about fusion and the paper's framing is wrong.** This is the single most important control in the paper.

### 8.4 Metrics

Existing: mAP / AP50 / AP90, tracking success/precision, EPE.
Invented: **`τ̂`** (effective timestamp), **`b`** (temporal bias), **`σ_τ`** (within-frame temporal dispersion / *temporal incoherence*), **`TEF`** (time-explained error fraction), **`sAP-τ`** (support-aware AP over `(θ, δ)`), **identifiability margin** (curvature of the agreement curve at `τ̂`), **collapse slope/R²**.

### 8.5 Ablations

(a) frame-only / event-only / fused → is `σ_τ` fusion-specific? (b) `T_exp` sweep with `v·T_exp` held constant (blur control). (c) label-clock ablation: train with labels at exposure start / midpoint / end / event-window end — does `τ̂` follow the label clock or the evidence centroid? (Theory: the evidence centroid, weakly pulled by the label.) (d) invariance ablation: add FAOD-style Time Shift to our own baseline and measure `σ_τ` — does enforcing invariance make the timestamp *worse*? (e) reformulation ablations: drop `L_frame`, drop per-event `L_event` (revert to voxel grid), drop `L_time`, reduce trajectory order K=0 (recovers the standard model exactly). (f) architecture control: swap ResNet-18 → RVT-style recurrent backbone; the phenomenon must survive.

### 8.6 Compute budget (one GPU, ≤ 9 GB, Docker)

| Stage | GPU-h | Peak VRAM |
|---|---|---|
| Pilot (generation + 1 training + probes + 4 figures) | ~3 | ~5 GB |
| Full sim sweep: ~60 condition-specific trainings × 1.5 h | ~90 | ~6 GB |
| Real-data probing of released checkpoints (inference only) | ~20 | ~6 GB |
| Reformulated model: sim + FE240hz + DSEC-Det, 3 seeds | ~80 | ~8.5 GB (346×260/640×480, batch 8–16, AMP, grad-ckpt) |
| Ablations | ~40 | ≤ 8.5 GB |
| **Total** | **≈ 230 GPU-h ≈ 10 days wall on one shared GPU** | **≤ 9 GB throughout** |

Everything at DAVIS346 (346×260) or DSEC-crop (640×480) resolution keeps us far under 9 GB; nothing here needs a large backbone, which is itself an argument that the finding is about formulation, not capacity.

---

## Risks

**Death 1 — The phenomenon does not reproduce on real data.** `b` and `σ_τ` are clean in simulation and vanish on FE240hz/EVIMO2, because our event model's timing is unrealistically clean, or because real GT at 240 Hz is too coarse and too noisy to resolve a 2–5 ms `τ̂`.
*Fallbacks, in order:* (i) Report the identifiability margin and restrict real-data claims to high-curvature, high-speed segments where the argmin is sharp — quantify how many such segments exist rather than hiding the restriction. (ii) Move to BS-ERGB/HS-ERGB, where the high-speed RGB stream provides sub-millisecond appearance GT far denser than 240 Hz mocap. (iii) Build a small **hardware-free real loop**: take any high-FPS video dataset (e.g. 960–1000 fps phone/slow-mo), synthesize the blurred frame by averaging *real* frames — so blur, texture, and noise are real — and simulate only the events. This isolates the risk to the event model alone. (iv) If only the *magnitude* shrinks but the *sign and ordering* survive (`τ̂` still moves with `T_exp` and `A`), the paper stands as a smaller but still valid law; we must pre-commit to reporting the shrunken effect honestly rather than cherry-picking sequences.

**Death 2 — "This is just temporal calibration / latency. Subtract a constant and go home."** The most likely reviewer-2 sentence, and it kills the paper if `σ_τ ≈ 0`.
*Fallback:* the entire defense is designed in, not bolted on — Fig. 3 (`σ_τ > 0` ⇒ no scalar fix exists), Fig. 4 (content-driven ⇒ not a clock property), and ablation 8.5(a) (fusion-specific ⇒ not a sensor latency). We should also run the *strongest possible* calibration baseline ourselves — fit the single best global `Δ` per dataset, and per-speed-bucket, and show the residual `σ_τ` that survives it. If a per-speed lookup table removes ≥ 80% of the effect, the honest conclusion is "this is calibration," and we downgrade to a workshop diagnostic paper rather than pretending otherwise.

**Death 3 — The reformulation does not pay.** The trajectory + support head wins on `sAP-τ` (our own metric) and ties or loses on mAP, and reviewers read invented-metric-only wins as circular.
*Fallbacks:* (i) Predict and demonstrate a *legacy-metric* win where the theory says it must exist — highest-speed / longest-exposure / strict-IoU (AP90) buckets, where `TEF` is highest; a win confined exactly where the theory predicts is far more convincing than a uniform win. (ii) Show a downstream consequence in a task with an external clock: time-to-collision or closed-loop reaching, where a 5 ms state error is a real distance. (iii) Worst case, land the paper as *diagnosis + protocol + dataset-tooling* — a reproducible failure diagram, `sAP-τ`, and a public probe that any existing checkpoint can be run through. That is a defensible CVPR contribution on its own, and it is the contribution we actually believe in.

**Death 4 (secondary) — Prior art surfaces.** The nearest live threats are FAOD's Time Shift (shift as nuisance) and the 2025 registration paper (spatiotemporal misalignment named). A 2026 paper that measures effective timestamps would sink us.
*Fallback:* our second, unclaimed asset is the **change-of-support formalization plus `σ_τ`**; even if someone reports a global bias `b`, the *spatially varying* and *content-driven* results, and the integral-observation loss `L_frame` in a discriminative head, remain unclaimed. Re-verify the literature at pilot completion and again in October.

---

## Self-score

| Axis | Score | Harsh justification |
|---|---|---|
| **Novelty** | **8 / 10** | The primitive (`τ̂` as argmin over a continuous GT trajectory) is embarrassingly simple and, as far as 15+ targeted searches across CVPR/ICCV/ECCV/T-PAMI/arXiv 2021–2026 show, nobody has run it on an event–RGB task head. The change-of-support framing is a genuine renaming of the problem, and `σ_τ > 0` — "the prediction has no single time" — is a claim the field currently cannot even state. Docked 2 because the *intuition* is not virgin: Sayed & Brostow named exposure-time ambiguity in 2021, the deblurring line knows the midpoint convention is arbitrary, and FAOD already sweeps temporal shift. We are the first to *measure* it in task space, which is a real but not unimaginable step. |
| **Feasibility** | **7 / 10** | Pilot is 3 days and 3 GPU-hours with zero external downloads — that is unusually strong. Rendering natively at 10 kHz removes the v2e/SuperSloMo dependency, the worst practical risk. Docked 3 for two real hazards: FE240hz availability (author-hosted, possible Baidu-only mirrors) is a single point of failure for the real-data loop, and `τ̂` identifiability on real 240 Hz GT under near-linear motion may be marginal — the effect we need to resolve (2–5 ms) is comparable to the GT sampling interval (4.17 ms). |
| **Reviewer-proof-ness** | **6 / 10** | The collapse plot and the fusion-specific `σ_τ` control are strong, and pre-registering the null result is the right posture. But three attacks are live: "just calibration" (answered only if `σ_τ` is convincingly nonzero on *real* data), "your simulator made this" (answered only by BS-ERGB), and "the invented metric is circular" (answered only if AP90 at high speed also improves). If the real-data effect is small, this becomes a well-argued paper about a 2 ms bias, and reviewers punish small effects regardless of their conceptual weight. |
| **Incrementality** *(lower = better)* | **2 / 10** | It changes the type signature of the output, not the architecture — the standard model is literally the `K=0, ŵ=δ` special case of ours, which is the cleanest possible demonstration that this is a superset rather than a tweak. Not 1/10 because the fix (trajectory head + calibrated time) is an unsurprising engineering answer once the diagnosis is accepted; the diagnosis carries the paper, and the method is honestly the smaller half. |

**Overall verdict:** the diagnosis is the paper. If the pilot's Fig. 1 vertices are off zero and `σ_τ` survives the frame-only control, this is a top-quartile CVPR submission; if `σ_τ` collapses to a global offset, it is a calibration note and we should pivot to another team's angle rather than dress it up.
