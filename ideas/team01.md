# A Frame Is Not a Timestamp: Latent Exposure Support as a First-Class Variable in Event–RGB Perception

## One-sentence thesis

A motion-blurred frame carries **no information whatsoever** about the absolute time interval it integrated, so every timestamp-aligned event–RGB system silently fixes that interval by dataloader convention; we prove this non-identifiability, measure the signed, motion-dependent localization bias it produces on real benchmarks, and replace the "state at time *t*" formulation with a **support-parameterized trajectory** whose exposure interval is inferred jointly from events and blur.

---

## The assumption we kill

**The assumption.** *A frame is an observation of the scene state at a single instant `t_i`, and that instant is known.*

It is encoded everywhere:

- **Dataloaders.** `image_timestamps.txt` holds one number per frame. DSEC's own documentation is explicit that this number is *derived*: image timestamps are "computed as the average of the middle exposures from the left and right cameras." Two physically different integration windows are collapsed into one shared scalar before any model ever sees the data. DSEC also ships `exposure_timestamps.txt` with the true start and end in microseconds — and essentially no downstream method reads it.
- **Ground truth association.** FE108/FE240hz has 240 Hz Vicon annotation but 20/40 FPS APS frames; the "frame label" is whichever mocap sample is nearest the frame's scalar timestamp. Prophesee GEN1/1Mpx, DSEC-Det and PKU-DAVIS-SOD all attach boxes to frame indices.
- **Event chunking.** Events are sliced into `[t_{i-1}, t_i)` — half-open intervals between *point* timestamps, which is only coherent if frames are points.
- **Fusion modules.** Every event–RGB fusion block concatenates an event tensor "at t" with an image "at t."
- **Metrics.** mAP and success-AUC are evaluated *at the label times*, i.e. at the very convention under test.

**Why it is universal.** It is inherited from frame-based vision, where it is harmless: if `v·T` is well under a pixel, the integral and the point sample agree, and the exposure is a nuisance for photometry only. Event vision then imported the frame pipeline wholesale. It is also convenient: a scalar timestamp makes the observation model a function `z = h(x_t)` rather than a functional of a trajectory, which is what makes standard supervised learning and standard benchmarks work at all.

**What breaks when it is false.** Write the image formation with the exposure normalized out:

```
B(x) = (1/T) ∫_{t0}^{t0+T} L(x ; p(τ)) dτ ,   substitute u = (τ - t0)/T
     =         ∫_0^1        L(x ; γ(u))  du ,   γ(u) := p(t0 + uT)
```

After the substitution **`t0` and `T` are gone from the equation.** The blurry frame depends on the motion only through the pushforward measure `μ = γ_# Unif[0,1]` — the path in the image plane together with its dwell-time density. Therefore:

1. The frame determines the *path* and the *dwell density*, and nothing else.
2. The frame does not determine `t0` or `T`. Not approximately — **not at all**; they do not appear.
3. The frame does not even determine the *direction of traversal* along the path (`u → 1-u` leaves `B` invariant).

So the timestamp a dataloader hands you is not a measurement. It is a **convention**, and because the frame carries zero information about it, that convention is an **unfalsifiable prior baked into the dataloader.** Under fast motion `α ∈ [0,1]` (start / mid / end) selects different scene states separated by `v·T` pixels, and no amount of data, capacity, or fusion architecture can recover which one the label meant.

---

## The failure phenomenon

**Name: Temporal Support Bias (TSB) — a signed, motion-direction-conditioned localization error that grows linearly with intra-exposure displacement, that all standard metrics average to zero, and that is therefore currently mis-attributed to "motion blur is hard" and to "cross-dataset domain gap."**

This is a failure of the *formulation*, not of accuracy: the supervision target itself is ill-posed, so the error is present at the optimum and cannot be trained away.

### The prediction

Let `d_i = ‖p(t0+T) - p(t0)‖` be an object's intra-exposure displacement in pixels, and let `e_∥` be the localization error **projected onto the object's motion direction** (signed, not absolute). Then for any timestamp-aligned method,

```
E[ e_∥ | d ]  =  (α_model − α_label) · d  +  O(d²)      ... (TSB law)
```

where `α_label ∈ [0,1]` is the annotation convention's position in the support and `α_model` is the model's *learned* implicit convention (a frame-dominant model drifts toward the blur centroid, `α ≈ 0.5`; an event-dominant model drifts toward the end of its event window, `α → 1`). The slope `β = dE[e_∥]/dd` is the metric; ideally `β = 0`.

Committed quantitative predictions:

- **Sim (exact control).** Sweeping exposure `T` at fixed velocity and velocity at fixed `T`, `e_∥` is a function of the *product* `d = v·T` alone, linear with `R² > 0.9` up to `d ≈ 40 px`, and `|β| ≥ 0.3` when label and model conventions differ by 0.5. **The slope is essentially independent of the network** (YOLOX-S vs. a transformer detector vs. a tracker) — this is the signature that it is a property of the formulation, not of any model.
- **Bias dominates variance.** Decompose the squared localization error into `bias²_∥ + var`. Prediction: for `d > 15 px` on FE240hz's low-light / high-speed subsets, `bias²_∥ > 50%` of total squared error. Read plainly: *most of what the field calls "blur difficulty" is a coordinate-system offset.*
- **The free-lunch test.** Estimate a single scalar `α̂` per dataset from our support estimator and shift every baseline's prediction by `(α̂ − α_model)·d̂` along the event-estimated motion direction — **zero learned parameters, one number per dataset.** Prediction: this removes **≥ 40%** of the excess error at `d > 15 px`. If a single scalar recovers 40% of the error an entire architecture paper is fighting for, the formulation, not the architecture, is the bug.
- **The "domain gap" that is not one.** Train on dataset A (convention `α_A`), test on dataset B (`α_B`). Prediction: the transfer degradation, conditioned on `d`, is predicted by `(α_A − α_B)·d` to within 25%, and largely disappears after the free-lunch shift. A gap that looks like appearance/sensor domain shift is a **clock-convention shift**.

### The exact experiment (Figure 1, costs almost no compute)

**Fig 1a — the phenomenon exists in public data, no training required.** DSEC ships true per-frame exposure start/end. Take DSEC train sequences; for each frame compute `T` (published) and per-pixel displacement during the support as `|flow_GT| · T/Δt_frame` using DSEC's optical-flow GT. Plot the distribution of `d` per sequence, day vs. night/tunnel. Prediction: `T` spans more than an order of magnitude within a single sequence under auto-exposure (~1 ms daylight to >15 ms night), and in night/tunnel sequences a non-trivial fraction of moving-object pixels exceed 5 px of intra-exposure displacement. Also plot the **left–right exposure-midpoint difference**: prediction ≥ 1 ms on a substantial fraction of frames, meaning the stereo pair — and hence disparity GT — is *support-inconsistent* under motion while sharing one nominal timestamp.

**Fig 1b — the money plot.** FE240hz: DAVIS346, 240 Hz Vicon GT, 20/40 FPS APS. For each APS frame, recover the exposure window from the AEDAT APS exposure-start/end signals, take the true GT sub-trajectory over that window at 240 Hz, compute `d_i`. Run released checkpoints of frame–event trackers (FENet/ICCV'21, AFNet/CVPR'23, ISTASTrack) **inference only**. x-axis `d_i` (0–40 px, binned); y-axis signed along-motion error `e_∥`. Expected: straight lines with distinct nonzero slopes per method, while the conventional unsigned success-AUC curves of the same runs look like ordinary smooth degradation. Overlay both panels — that single figure is the paper's argument.

**Fig 1c — why nobody noticed.** Same data, plot `E[e_∥]` *unconditioned on motion direction*: it sits at ≈ 0. The dataset contains motion in all directions, so the signed bias cancels in the mean and reappears only as inflated variance, which mAP/AUC reports as "harder." Standard metrics are blind for three compounding reasons: (i) IoU is unsigned; (ii) evaluation times *are* the convention under test, so the bias is invisible within a dataset by construction; (iii) nobody conditions on motion direction.

---

## The reformulation

### New problem statement

> Given a set of observations with **heterogeneous temporal supports** — a frame is a measurement functional `∫` over an interval, an event is a `δ` at a microsecond instant — infer a **continuous-time scene state function**, jointly with the **latent support of each frame**.

The state stops being a vector at a time and becomes a function of time; the *time* stops being metadata and becomes a latent variable.

### New representation unit

**Point → support-parameterized trajectory.** For object `o`, predict a curve on the *normalized* support in Bernstein (Bézier) basis:

```
γ_o(u) = Σ_{k=0..K} B_k^K(u) · c_{o,k},    u ∈ [0,1],    c_{o,k} ∈ R^4 = (cx, cy, log w, log h)
```

`K = 3` (cubic) → 16 numbers per object instead of 4. **`K = 0` is exactly the current formulation**, which makes the order ablation a direct comparison against the state of the art rather than a side experiment.

**Support field.** The support is a property of the observation, and under rolling shutter it varies across the image, so predict per frame three physical scalars — offset, line delay, duration:

```
S(y) = [ t̂0 + ρ̂·y ,  t̂0 + ρ̂·y + T̂ ]        (ρ̂ = 0 for global shutter)
```

**Time-queried readout.** For any query time τ (not just frame times):

```
u = ( τ − t̂0 − ρ̂·y_o ) / T̂ ,     b̂_o(τ) = γ_o(u),     flag EXTRAPOLATION if u ∉ [−ε, 1+ε]
```

The network *takes τ as an input*. No current detector or tracker does.

### Objective

**(1) Support-distributed supervision.** With high-rate GT (240 Hz Vicon on FE240hz; 1 kHz in sim), sample `M` times `τ_m` inside the support:

```
L_traj = (1/M) Σ_m  L_box( γ_o((τ_m − t̂0 − ρ̂ y_o)/T̂),  b*_o(τ_m) )
```

There is no single label time, so there is no convention to be biased by. This term alone drives TSB toward zero.

**(2) Event–trajectory consistency (self-supervised; needed where GT is frame-rate only).** For events inside the object's swept region, warp to `u = 0` along the predicted curve and maximize contrast:

```
u_e = (τ_e − t̂0 − ρ̂ y_e)/T̂ ,   x'_e = x_e − ( γ_xy(u_e) − γ_xy(0) )
L_cm = − Var_{Ω_o} [ IWE(γ_o, ŝ) ]
```

`t̂0` and `T̂` enter as an **affine reparameterization of event time**, and image-of-warped-events contrast is sensitive to it — this is precisely the term that makes the support identifiable.

**(3) Frame–support consistency (blur as integral).** The object's appearance in the frame must equal its template swept along `γ` and averaged over the support:

```
L_blur = ‖ I_i ⊙ M_o  −  ∫_0^1 W_{γ_o(u)}[ Ŝ_o ] du ‖_1
```

with a cheap surrogate for detection: integrate the predicted soft occupancy mask along `γ` and match the frame's directional gradient-energy profile.

**(4) Weak metadata prior** where available: `L_meta = |T̂ − T_exif|` (DSEC publishes it; DAVIS APS emits exposure start/end).

```
L = L_traj + λ1 L_cm + λ2 L_blur + λ3 L_meta
```

### The identifiability proposition (the spine of the paper)

> **Proposition (informal).** A single motion-blurred frame determines the intra-exposure path and its dwell-time density (the occupancy measure `μ`), and determines **neither** the affine time reparameterization `(t0, T)` **nor** the direction of traversal. An event stream over a superset interval determines relative timing to microsecond resolution and the direction of motion, but not which sub-interval the frame integrated, absent a photometric anchor. **Jointly**, `(γ, t0, T)` is identifiable up to the standard contrast-maximization degeneracies whenever the object emits events during the support.

Proof sketch: the `u`-substitution above removes `(t0,T)` from `B` exactly; invariance of `B` under `u → 1−u` gives the reversal ambiguity; the event term is a strictly monotone function of the time affine map through the warp, so it breaks both.

This is why the paper is **not** event+RGB fusion for accuracy. It is event+RGB **for identifiability**: neither modality alone can express the quantity, and the combination is *necessary*, not merely helpful.

---

## What existing methods cannot express

1. **The frame's clock `(t0, T)` — the affine time reparameterization of the exposure.** No detector, tracker, flow model, or fusion module has a variable for it. It is fixed by a text file.
2. **Intra-exposure motion.** Existing event–RGB models have a variable for motion *between* frames (optical flow, event volumes, temporal attention) and **no variable at all for what the object did during a single frame's exposure.** The blur is treated as a corrupted appearance, never as a measurement of a trajectory.
3. **Query time as an input.** Current models answer exactly one question per frame: "where at `t_i`?" They cannot be asked "where at `t_i − 4 ms`?", and there is no way to even pose the question in their interface.
4. **Temporal bandwidth of the estimate.** With support width `T`, trajectory content above ~`1/T` is unobservable from the frame; only events resolve it. The *time resolution of a state estimate* is a computable quantity that no formulation currently carries, so all estimates are reported with false temporal precision.
5. **Per-observation, per-row support heterogeneity.** Stereo pairs with different auto-exposure windows, rolling shutter rows with different `t0`, and multi-camera rigs are all currently forced into one scalar. DSEC literally averages two different exposure midpoints into one number.
6. **Signed, direction-conditioned error.** Not expressible in mAP/IoU-based metrics at all.

---

## Why this is not <closest work>

| Title | Venue / Year | What it does | Why we are not it |
|---|---|---|---|
| Bringing a Blurry Frame Alive at High Frame-Rate with an Event Camera (EDI) | CVPR 2019 | Event Double Integral: models the frame as `B = (1/T)∫L(t)dt` and inverts it with events to restore sharp frames | Same image-formation insight, opposite use. EDI **assumes `T` and the window are known**, targets pixel restoration, and still outputs images at chosen instants. We prove `(t0,T)` is *not* recoverable from the frame, make it a latent, and change the *task/label/metric*, not the pixels. |
| Event-guided Deblurring of Unknown Exposure Time Videos | ECCV 2022 | Handles unknown, auto-exposure-varying exposure via exposure-time-based feature selection | Restoration only; "unknown exposure" is a robustness nuisance handled implicitly in features. We estimate the support explicitly as a physical quantity with units, validate it in ms against DSEC's published exposure timestamps, and expose it to downstream tasks. |
| Event-based Blurry Frame Interpolation under Blind Exposure (EBFI-BE) | CVPR 2023 | Estimates the "lost exposure prior" from blurry frame + events; temporal-exposure-aware control for interpolation | **Closest work on latent support.** But it is a video-restoration method: it never touches labels, association, detection/tracking, or evaluation, and it does not identify the bias phenomenon. Our claim is that latent support is a *perception-level* variable and that current benchmarks are measuring an artifact. We use EBFI-BE-style restoration as a **baseline that inherits the bug** (deblur-then-detect still picks one `α`). |
| Latency Correction for Event-guided Deblurring and Frame Interpolation | CVPR 2024 | Parameterized model of *event* latency; makes EDI differentiable w.r.t. latency | Corrects the **event** clock (timestamp error per event). We are about the **frame's** clock (the integration window). Orthogonal and composable; also restoration, not perception. |
| Intra-frame Object Tracking by Deblatting / Tracking by Deblatting | CVPR-W 2019 / IJCV 2021 | Recovers an object's intra-frame trajectory from blur via blind deblurring + matting; proposes Trajectory-IoU | Closest on *representation unit*, and we adopt TIoU rather than reinvent it. But: frame-only, no events, restricted to fast-moving-objects that appear as isolated blur streaks on simple backgrounds, non-learned, and **assumes the exposure fraction / duty cycle is known** — exactly the quantity we prove is unidentifiable from frames and recover from events. It also makes no claim about labels, conventions, or benchmark bias. |
| DeFMO: Deblurring and Shape Recovery of Fast Moving Objects | CVPR 2021 | Learned sub-frame appearance and trajectory of a single fast moving object | Frame-only, single-object, assumes exposure fraction, and evaluated as restoration/shape. No support estimation, no events, no general detection/tracking reformulation. |
| Exposure Trajectory Recovery from Motion Blur | TPAMI 2022 | Dense pixel-wise "exposure trajectories" from a single blurry image | Image-only, so by our proposition it recovers only the path/dwell density — no absolute clock, no direction. Aimed at deblurring/warping, not at task labels or metrics. |
| Dense Continuous-Time Optical Flow from Event Cameras | TPAMI 2024 (ECCV 2022) | Bézier-parameterized continuous-time per-pixel trajectories from events, queryable at any time | Closest on *continuous-time output*. **Event-only**, so the frame-support problem never arises and there is no exposure variable anywhere. We inherit the Bézier machinery and add the thing they do not have: the frame's latent support and the blur-as-integral constraint that ties a frame to a sub-interval. |
| Motion-prior Contrast Maximization for Dense Continuous-Time Motion Estimation | ECCV 2024 | Contrast maximization with motion priors for continuous-time event flow | Event-only self-supervision. Our `L_cm` is the same family, but our contrast term is parameterized by `(t̂0, T̂)` and *anchored to a frame's integral*, which is what makes the support identifiable. |
| Frequency-Adaptive Low-Latency Object Detection Using Events and Frames (FAOD) | arXiv 2024 / 2025 | Handles low-latency-event vs. high-latency-RGB mismatch; "Time Shift" training aligns predictions from temporally shifted Event–RGB pairs | **The most dangerous neighbor at the task level, and it makes our case.** FAOD treats frames as point samples and trains the model to be *invariant* to a temporal shift. We argue the shift is not a nuisance to be averaged out — it is the object's intra-exposure trajectory, i.e. **information**. Invariance destroys exactly the quantity we recover; FAOD still outputs a box at one time and still cannot be queried off-frame. |
| SODFormer | TPAMI 2023 | Streaming event+frame detection transformer (PKU-DAVIS-SOD) | Timestamp-aligned throughout; box at frame time; a baseline. |
| Frame-Event Alignment and Fusion Network (AFNet) | CVPR 2023 | High-frame-rate tracking on FE240hz with cross-modal alignment | Aligns *features* spatially/temporally; the frame is still an observation at one time and the alignment has no physical support variable. A primary baseline for the Fig-1b bias measurement. |
| Unleashing the Temporal Potential of Stereo Event Cameras for Continuous-Time 3D Object Detection | ICCV 2025 | Fully asynchronous 3D detection at arbitrary timestamps | **Event-only stereo** — no frames, therefore no exposure support and no blur constraint. Confirms the community wants arbitrary-time queries; we are the frame-side half of that problem, which is the hard half. |
| EvUnroll / EvShutter | CVPR 2022 / CVPR 2023 | Event-guided rolling-shutter correction using per-row exposure timing | Per-row time as **known sensor geometry** for image rectification. We treat the support as an *inferred latent field* `(t̂0, ρ̂, T̂)`, including duration, and use it for perception rather than to produce a rectified image. |
| MTevent | CVPR-W 2025 | Multi-task event dataset; observes that 25 ms RGB exposure yields "faulty annotations" under fast motion | **Our phenomenon, noticed in passing by a dataset paper, and then discarded** ("event annotations remain accurate"). No formulation, no law, no metric, no method, no measurement of the bias. We cite it as independent evidence that the phenomenon is real. |

**Brutal honesty about the residual gap.** Latent-exposure estimation from events exists (EBFI-BE). Intra-frame trajectories as an output exist (TbD/DeFMO). Bézier continuous-time queries exist (Gehrig et al.). What does **not** exist anywhere we can find: (a) the non-identifiability proposition stated and used, (b) the TSB law and its measurement on public benchmarks, (c) the demonstration that a documented "domain gap" is a clock-convention gap removable by one scalar, (d) support as an input-side latent for *detection/tracking* with time-queried evaluation. The paper must lead with (a)–(c). If it leads with the architecture, it is an application paper and it will be rejected as one.

---

## Experimental plan

### Datasets

| Data | What it gives us | Size | Availability risk |
|---|---|---|---|
| **FE108 / FE240hz** (ICCV 2021) | The only real set with **GT at ~10× the frame rate**: DAVIS346 346×260, APS 20/40 FPS + events, 240 Hz Vicon boxes, 108 sequences / 143 K frames. Enables real intra-exposure GT and time-queried evaluation. | est. 40–90 GB (not published; must be measured on download) | **Medium-high.** Access is by application for non-commercial use via the authors' portal — turnaround is unknown and could take weeks. *Mitigation: apply on day 1.* |
| **DSEC** (RA-L 2021) + **DSEC-Det** | **Publishes true per-frame exposure start/end in µs** — free ground truth for the support estimator on real data — plus optical-flow GT for computing `d`, and documented midpoint-averaging convention. | 356 GB full; per-sequence 2.4–13 GB → download a **60–90 GB** subset (day + night/tunnel) | **Low.** Public HTTP, no gate. |
| **PKU-DAVIS-SOD** (SODFormer, TPAMI 2023) | Real RGB+event detection, DAVIS346, driving/campus; second real detection domain for the cross-dataset convention experiment. | est. ~80–120 GB (unverified) | **Medium.** Hosted on OpenI (git.openi.org.cn); mirror availability unverified. |
| **SupportBench (ours, synthetic)** | The controlled proof. A textured-sprite / Blender renderer at 10 kHz → exact `(t0, T)`, exact 1 kHz GT trajectories, exposure formed by averaging `N` sub-frames, events via **v2e** (CVPR-W 2021) or **DVS-Voltmeter** (ECCV 2022). Exposure, velocity, and label convention `α` are all independent variables. | ~20–40 GB generated on disk, no download | **Low** — this is why it is the primary vehicle for the law. |
| **BS-ERGB / HS-ERGB** (Time Lens / Time Lens++) | Optional photorealistic sim source (real high-FPS + real events) for a realism check on the sim→real transfer of the TSB slope. | ~30–60 GB | Medium. |
| Local rosbags (`/media/hdd8/justin/navifra/wingbody/*.bag`) | Weak fallback only: existing multi-camera/robot bags for a v2e-simulated in-house sequence if all gated datasets fail. Not high-FPS vision; would need new capture. | on disk | Fallback of last resort. |

Disk budget: 990 GB free; the plan uses ~250 GB.

### Controlled variable

**Primary: normalized intra-exposure displacement `d = v·T` (px).** Swept two ways to prove it is the *product* that matters: (i) vary exposure `N ∈ {1,2,4,8,16,32}` sub-frames at fixed velocity; (ii) vary velocity at fixed `N`. Both must collapse onto one curve.
**Secondary: the label convention `α ∈ {0, 0.25, 0.5, 0.75, 1}`** — the variable that does not exist in any current pipeline.
**Tertiary: support heterogeneity** — per-frame jittered `T` (auto-exposure emulation), and rolling-shutter line delay `ρ`.

### Baselines (all real, released methods)

- **Trackers on FE240hz:** FENet (ICCV 2021, the FE240 baseline), **AFNet** (CVPR 2023), ISTASTrack (2025), plus an RGB-only tracker for reference.
- **Detectors:** **SODFormer** (TPAMI 2023), **FAOD** (2024/25), **RVT** (CVPR 2023, event-only), **DAGr** (Nature 2024, DSEC-Det).
- **Restore-then-perceive:** **EDI** (CVPR 2019) and **EBFI-BE** (CVPR 2023) → detector. This is the baseline that must be beaten *conceptually*: prediction is that deblur-then-detect does **not** reduce TSB, because restoration also picks one instant.
- **Continuous-time references:** Dense Continuous-Time Optical Flow (TPAMI 2024) as the event-only trajectory upper bound; **TbD-NC** (IJCV 2021) as the frame-only intra-frame trajectory reference.
- **Ablation-as-baseline:** our own model at `K = 0`, which *is* the current formulation with our backbone — the honest apples-to-apples comparison.

### Metrics

**Existing, reused:** success-AUC / precision (tracking), mAP (detection), **TIoU** (Trajectory-IoU, from TbD, IJCV 2021 — reused, not invented).

**Invented, with justification for why existing ones are blind:**

1. **TSB — Temporal Support Bias.** The slope `β = dE[e_∥]/dd` (px per px), estimated by robust regression over `d`-bins, reported with CI. *Existing metrics are blind because IoU is unsigned and because averaging over motion directions cancels a direction-conditioned bias in the mean while inflating variance, which mAP then reports as "hard."*
2. **TQ-AUC / TQ-mAP — Time-Queried accuracy as a function of query offset `τ`** over `[t0 − Δ, t0 + T + Δ]`, evaluated against 240 Hz (real) / 1 kHz (sim) GT. *Existing metrics evaluate only at label times, i.e. at the convention under test — a self-confirming measurement.* Baselines can only emit a constant across `τ`, so their curve is a V with a minimum at their implicit `α`; ours should be flat. Report both the curve and its AUC. **Prediction: baseline accuracy at `τ = t0` or `t0+T` drops ≥ 30% relative to the midpoint; our variation across the support is < 15% of peak.**
3. **SCR — Support Coverage Ratio.** Fraction of `τ` inside the support at which error is below threshold. One number summarizing (2).
4. **SIE — Support Identification Error.** `|T̂ − T|` and `|t̂0 − t0|` **in milliseconds**, against DSEC's published exposure timestamps (never shown in training) and against exact sim GT. **Prediction: `T̂` within 15% of DSEC's reported exposure.** This is the cheapest possible real-data validation of the central latent variable and it exists today, for free, in a public dataset.

### Ablations

1. **Bézier order `K ∈ {0,1,2,3}`.** `K=0` reproduces the current formulation → the ablation *is* the SOTA comparison.
2. **Support: metadata-only / frozen-convention / estimated.** Isolates the contribution of making it latent.
3. **Drop `L_cm` (no events in the support term).** *Direct empirical test of the proposition:* prediction is that the **path** stays accurate while `T̂` becomes unidentifiable and SIE blows up — the proposition rendered as a bar chart.
4. **Drop `L_blur` (no frame).** Path accuracy degrades (events give edges, not extent), confirming necessity in the other direction.
5. **Label convention sweep** (train `α=0`, test `α=1`, etc.) with and without the free-lunch shift.
6. **Rolling-shutter term `ρ̂` on/off** (sim + any RS source; DAVIS APS and DSEC RGB are global shutter, so this ablation is sim-primary — stated honestly).
7. **Sim → real transfer of the TSB slope**: does the law measured in sim predict the slope measured on FE240hz?

### Compute budget (single shared RTX 5090, ~9 GB usable, Docker only)

Backbone deliberately small: ResNet-18/YOLOX-S image branch + event-voxel branch, 346×260 (FE240) or 640×440 crops (DSEC), batch 8, AMP → **~5–7 GB peak**. Bézier head adds 12 scalars per object: negligible.

| Item | GPU-h |
|---|---|
| **Fig 1 (the whole argument): inference-only with released checkpoints + DSEC metadata analysis** | **~10** |
| SupportBench generation (v2e is GPU-assisted) | 15 |
| Sim pretraining + the `d`-sweep law (6 exposure settings) | 30 |
| FE240hz training, 3 seeds | 36 |
| DSEC-Det training, 2 runs | 40 |
| Ablations (7 configs × ~8 h) | 56 |
| Baseline re-runs / evaluation harness | 30 |
| **Total** | **≈ 217 GPU-h ≈ 9 days of pure GPU** |

Comfortable inside Sep→Nov 2026 on a shared GPU. Crucially, **the paper's central claim costs ~10 GPU-hours** and depends on no training at all; everything else is the method that follows from it. That ordering is the de-risking.

---

## Risks

**Risk 1 — the bias is small on real data.** Public event–RGB datasets are largely captured in decent light with short exposures, so `v·T` may be a couple of pixels and the phenomenon invisible outside simulation. A sim-only failure phenomenon is a weak paper.
*Fallback:* (a) Target the regimes where it must be large — FE240hz explicitly contains low-light, HDR, motion-blur and fast-motion sequences with long APS exposure; DSEC night/tunnel sequences with auto-exposure over 10 ms. (b) Even if the *magnitude* is modest, the **bias/variance decomposition** stands: showing that a signed component dominates at large `d` is a formulation result independent of absolute magnitude. (c) If real magnitude collapses entirely, the paper degrades gracefully into "the regime map + the protocol + SupportBench + the SIE validation on DSEC's published exposures" — a weaker but still publishable analysis/benchmark paper. (d) Last resort: v2e over in-house high-FPS capture.

**Risk 2 — "this is EBFI-BE (or EDI) applied to detection."** The single most likely rejection. Latent exposure estimation from events is published; a reviewer can compress our contribution into "they used it for boxes."
*Fallback:* Structural, not rhetorical. Lead the paper with the **non-identifiability proposition** and the **TSB measurement on existing benchmarks with existing checkpoints** — neither of which any restoration paper contains, and both of which are results about *the field's data and metrics*, not about our model. Make deblur-then-detect (EDI, EBFI-BE) a headline baseline and show it **does not reduce TSB**, because restoration also commits to one instant. Make `K=0` the ablation so the reviewer sees the formulation change isolated from the architecture. If reviewers still read it as an application paper, the fallback framing is "benchmark-and-analysis paper with a corrective method," which is a legitimate CVPR category and survives on Fig 1 alone.

**Risk 3 — the support is not identifiable in practice.** Contrast maximization on small, weakly-textured objects with few events is noisy; `T̂` may collapse to the metadata prior, making the whole latent decorative. Related: FE240hz's Vicon-to-camera temporal calibration may itself carry an unknown offset, which would confound the very measurement in Fig 1b.
*Fallback:* (a) **Two-tier estimation** — a robust per-sequence global `(t̂0, T̂)` aggregated over thousands of objects/frames as the headline result, with per-object/per-row refinement as a bonus rather than a load-bearing claim. (b) **Validate on DSEC first**, where the true exposure is published, before ever trusting it on FE240hz. (c) Turn the confound into a result: the mocap-to-camera offset is the *same* affine-time estimation problem, so estimate it and report it — "our support estimator recovers an `X ms` mocap-to-camera timing offset in a widely used benchmark" is exactly the kind of finding that makes reviewers believe the machinery. (d) If per-frame `T̂` is hopeless, fall back to `T` from metadata (DSEC publishes it, DAVIS emits it) and keep `t̂0`/`α` as the estimated latent — the TSB argument only needs `α`.

---

## Self-score

| Axis | Score | Justification (harsh) |
|---|---|---|
| **Novelty** | **8 / 10** | The non-identifiability proposition, the TSB law, and "the domain gap is a clock-convention gap" are, as far as ~20 searched neighbors go, unpublished, and they are the kind of claim that changes how people build dataloaders. Docked two points because none of the *components* are new: exposure-as-integral is EDI 2019, blind exposure is EBFI-BE 2023, intra-frame trajectories are TbD 2019/DeFMO 2021, Bézier continuous-time queries are Gehrig 2024. The novelty is entirely in the recombination and in the target (task/label/metric instead of pixels). That is real novelty, but it is *assembly* novelty, and a hostile reviewer can name every part. |
| **Feasibility here** | **7 / 10** | ~217 GPU-h at 5–7 GB fits the 9 GB shared budget with room to spare, and the headline figure costs ~10 GPU-h of pure inference. DSEC's published per-frame exposure timestamps are an unexpectedly strong free validation signal. Docked for: FE240hz is **application-gated** and is the only real source of intra-exposure GT — if that access does not arrive, the strongest real-data plot is gone and PKU-DAVIS-SOD (frame-rate GT only) cannot replace it. Also ~250 GB of downloads and a simulator to build from scratch, starting from zero event data on disk. |
| **Reviewer-proof-ness** | **6 / 10** | The proposition is provable in half a page and the free-lunch experiment is falsifiable and cheap, which is strong. But the paper stands or falls on Fig 1b actually showing a clean line on real data, and that plot depends on a gated dataset, on correctly recovering DAVIS APS exposure windows, and on a mocap calibration we do not control. A noisy Fig 1b turns the whole paper into a simulator study. Also: "you changed the metric and then won on your metric" is a standing charge against any paper that invents an evaluation, and we invent four. Mitigated only partly by reusing TIoU and by reporting standard mAP/AUC alongside. |
| **Could a reviewer say this is incremental?** | **5 / 10 risk (moderate)** | Yes, along one specific line: *"blind exposure estimation exists; you applied it to detection and made a metric."* That review is writable today. It is defeated only if the paper's first four pages are the proposition and the measurement on **other people's checkpoints and other people's benchmarks** — results that belong to the field rather than to our model. If the paper is instead organized around the architecture, the incremental charge sticks and the paper dies. Risk is moderate rather than high because the "one scalar removes 40% of a published domain gap" result, if it holds, is not something an incremental paper can produce. |

**Overall verdict.** The idea is not taken, the closest neighbors are all restoration-side or event-only, the central claim is provable and cheaply measurable, and the compute fits. The dominant risk is not novelty and not compute — it is **access to FE240hz** and whether the real-data slope is clean. Both are resolvable within the first two weeks, so this idea should be prosecuted with a hard go/no-go gate at day 14: apply for FE240hz on day 1, download the DSEC subset immediately, and produce Fig 1a (DSEC exposure statistics — zero training, zero gating) before writing a single line of the model.
