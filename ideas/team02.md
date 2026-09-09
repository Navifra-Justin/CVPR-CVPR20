# No State at *t*: Exposure-Occupancy Measures as the Prediction Target for Event–RGB Perception

*Idea Team 02 — CVPR 2027 — domain: Temporal-Support-Aligned Event–RGB Perception*
*Attack angle: kill the assumption that the ground truth at time t is a single value.*

---

## One-sentence thesis

Under fast motion the label attached to a frame is not the scene state but an *unspecified functional of the state's occupancy measure over the exposure window*; we therefore predict the measure itself — the frame supplies its **mass**, the event stream supplies its **order**, and neither modality alone identifies it — and we evaluate it by convention-marginal coverage instead of point IoU.

---

## The assumption we kill

**The assumption.** *An annotation attached to a frame denotes the value of a scene quantity at a single instant, and any disagreement about that value is annotation noise.*

Write it formally. A frame is captured over an exposure window `W = [t0, t0+T]`. The scene quantity of interest (box, 6-DoF pose, disparity, flow, joint angles) is a *process* `y : W → Y ⊆ R^d`. Every dataset in vision stores one vector `ŷ ∈ Y` per frame. So every dataset silently applies an **annotation operator**

```
A : C(W, Y) → Y ,    ŷ = A[y] ,
```

and *no benchmark in computer vision states which A it used.* Candidates all in active use, all defensible, all different:

| Convention | Definition |
|---|---|
| `A_mid` | `y(t0 + T/2)` — "the middle of the exposure" |
| `A_mean` | `(1/T)∫_W y(t) dt` — the barycenter, what a least-squares annotator converges to |
| `A_mode` | `argmax` of the dwell density — where the streak is *darkest*, what a human eye actually locks onto |
| `A_start`, `A_end` | `y(t0)`, `y(t0+T)` — what trigger-synchronised mocap pipelines export |
| `A_hull` | tightest box containing the whole streak — the COCO/VOC instruction "box the visible object" taken literally |
| `A_core` | intersection over the exposure — what annotators do when told "box the sharp part" |

**Why the assumption is universal.** It is baked in three layers deep and is never argued for:
1. *Storage.* Annotation formats (COCO JSON, KITTI txt, Prophesee `.npy` box records, VOT rectangles) have one row per (frame, object). There is no slot for a set.
2. *Loss.* `L1`/`GIoU`/`EPE`/`ADE` are metrics on `Y`, so the target must be a point of `Y`.
3. *Metric.* AP, IoU, PCK, RSR/RPR compare a point to a point. A model that correctly reports "the state is this 40-px-wide set" gets scored as if it had guessed the set's centre and is punished for its width.

**What breaks.** Three things, in increasing severity.

- **(b1) The conventions disagree, and the disagreement is not noise.** `A_mid ≠ A_mean ≠ A_mode` whenever the motion inside the exposure is not uniform. The gap is a *systematic, sign-carrying, scene-dependent bias*, not zero-mean jitter. Every noise-robust-training paper (bootstrapping, co-teaching, label smoothing, LEOD-style label refinement) assumes zero-mean; the assumption is wrong here by construction.
- **(b2) The field indexes difficulty by the wrong variable.** Everyone reports robustness against *blur magnitude* (`β` = streak length / object size). But at constant velocity, `A_mid = A_mean = A_mode` **exactly**, no matter how large `β` is — the label is perfectly well-posed under arbitrarily severe uniform blur. What destroys the label is **intra-exposure acceleration**. Blur magnitude and label ill-posedness are *orthogonal axes*, and the community has only ever plotted the first one.
- **(b3) The benchmark measures the convention, not the physics.** If switching from `A_mid` to `A_mean` reorders the leaderboard, then what the leaderboard ranks is *"which model best guessed an unwritten annotation habit"*. That is a statement about the task definition, not about the models — and it caps the headroom of every future method by an amount nobody has measured.

**The reframe.** The physics supplies a *set with a mass distribution on it*; the benchmark supplies a point drawn from it by an unknown rule. We should predict the object the physics supplies and treat the rule as a latent nuisance.

---

## The failure phenomenon

> Everyone believes: *label ambiguity under motion grows with blur.*
> The measurement says: *it does not — it grows with intra-exposure acceleration, and blur magnitude is a confound.*

### Data

- **Real, primary:** **FE108 / FE240hz** (Zhang et al., ICCV 2021). DAVIS346, grayscale APS frames at **20/40 FPS**, real events, and **240 Hz Vicon bounding-box ground truth**. This is the only public event+frame benchmark whose label rate is an order of magnitude above its frame rate, so **the intra-exposure state continuum is directly observable on real data**: at 20 FPS there are up to 12 Vicon labels inside one frame period. It has explicit `motion blur`, `HDR` and `low light` attribute splits.
- **Real, backup:** **EVIMO2** (~40 GB, direct download). 200 Hz Vicon 6-DoF object poses + real events + a classical colour camera. Same construction in pose space.
- **Controlled:** procedurally rendered clips at 10 kHz with analytic motion laws, blur = sub-frame average, events = **v2e**. This is the only source that lets us hold `β` fixed while sweeping acceleration — which is the entire point.

### Construction

For each frame with exposure `W`, take the sub-exposure GT samples `{y_k}` inside `W` and form the empirical occupancy measure `μ`. Then compute two axes and two responses.

- **Axis 1 (the field's axis):** `β = ‖path length over W‖ / diag(box)` — blur magnitude.
- **Axis 2 (ours):** `ν = ‖v(t0+T) − v(t0)‖·T / diag(box)` — normalised intra-exposure velocity change. (Equivalently, the non-uniformity `κ = W₁(μ, arc-uniform) / diag(box)`.)
- **Response 1 (label irreducibility):** `D = 1 − min_{A,A' ∈ 𝒜} IoU(A[y], A'[y])` — how much the label changes if you change nothing but the unwritten convention.
- **Response 2 (benchmark validity):** Kendall `τ` between the FE240hz leaderboards of five real trackers (**FENet**, **AFNet**, **ToMP-MF**, **DeT**, **HMFT**) scored under `A_mid` vs. under `A_mean`.

### Expected curves

**Panel A — `D` vs `β`, stratified by `ν`.** The low-`ν` stratum is a **flat line near zero across the whole blur range**. The high-`ν` stratum rises steeply. *The two strata separate, which means `β` alone does not predict `D` — that separation is the plot.*

**Panel B — `D` vs `ν`, with `β` held fixed (simulation).** Monotone, near-linear rise from `D ≈ 0` to `D > 0.5`. Held-fixed `β` removes the standard explanation entirely.

**Panel C — leaderboard `τ` vs `ν` decile.** Flat and near 1.0 on the slow deciles; falls off in the top deciles.

### Quantitative predictions (falsifiable, stated in advance)

1. At `ν = 0` and `β = 3` (a streak three object-diagonals long — severe blur), `D < 0.05`. **Severe blur with zero acceleration produces a perfectly well-posed label.**
2. At `ν = 1` and `β = 1`, `D > 0.5`: the mid-exposure box and the time-average box overlap by **less than half**.
3. **The indictment.** On the top-20 % `ν` subset of FE108, the RSR change of a *single fixed model* under a convention switch (`A_mid → A_mean`) is **10–20 points**, whereas the RSR spread *between* the five published trackers is **3–8 points**. The convention moves the score more than the method does.
4. Kendall `τ` over the five-method ranking drops **below 0.6** on the top `ν` decile — i.e. the published ordering is not stable to an unwritten choice.
5. **Oracle floor.** Define `e*(x) = min_p max_{A ∈ 𝒜} d(p, A[y])`: the error of the best possible *point* predictor that knows the physics exactly. `e*` grows linearly in `ν` and exceeds the current SOTA-to-runner-up gap for `ν > 0.3`, a regime covering **≈25 %** of FE108's fast-motion frames. **A quarter of the remaining headroom on this benchmark is definitional, not learnable.**

Prediction 1 is the one that indicts the *formulation* rather than the accuracy: it shows the community's chosen difficulty axis is the wrong one, and that a well-posedness property — not a performance property — is what actually varies.

---

## The reformulation

### State space

Exposure `W = [t0, t0+T]`. Latent state process `y : W → Y ⊆ R^d`. Define the **exposure-occupancy measure** (the dwell measure)

```
μ = y_# Unif(W) ,     μ(B) = (1/T) · |{ t ∈ W : y(t) ∈ B }| ,     μ ∈ P(Y).
```

`supp μ = S` is the **support set** — *what* states occurred. The density of `μ` on `S` is the **dwell** — *how long* each was occupied. A conventional label is a functional `A[y]`, and every convention in the table above is a functional of `μ` alone except `A_start`/`A_end`, which additionally need the time order.

### What each modality actually observes (this is the theory, and it is not fusion)

Let `Π : Y → R²` be the map from state to image-plane displacement.

**Proposition 1 (frames measure mass, and *only* mass).** For a locally rigid patch, the captured frame is
```
B(x) = (1/T) ∫_W I(x − Π(y(t))) dt = (I ⊛ Π_# μ)(x).
```
The frame is a **linear functional of `Π_# μ` alone**. It is therefore invariant to *every* time-reparametrisation of `y`, including time reversal. From `B`, `y` is identifiable only up to the equivalence class `{ y' : y'_# Unif(W) = μ }`, which is an infinite-dimensional group orbit. (The classical special case — that a uniform-motion blur kernel *is* a dwell histogram — is Gupta et al.'s Motion Density Function, ECCV 2010; we are lifting it from image formation to the supervision of a semantic state.)

**Proposition 2 (events measure order, and *only* order).** An event at pixel `x` with timestamp `t_e` asserts that a log-intensity edge crossed `x` at `t_e`; the timestamp field `t(x)` is the inverse of the trajectory `t ↦ Π(y(t))`. Events therefore determine the **parametrisation** up to per-pixel contrast-threshold gain — but the unknown, per-pixel, polarity-asymmetric contrast threshold means the *mass* (how much irradiance accumulated) is not recoverable from events alone.

**Corollary (complementary identifiability).** `Π_# μ` from the frame + the time-ordering from the events **jointly identify the image-space intra-exposure state process**, and neither modality alone does. This is the temporal-support statement in its sharpest form: **the frame and the events are two different measurements of the same measure — the frame integrates it, the events index it — and the "state at `t`" that both are conventionally asked to report is not a quantity either of them observes.**

### What is predicted

Represent `μ̂` as a pushforward of a 1-D dwell density along a learned support curve:

```
γ_θ : [0,1] → Y      cubic B-spline, M = 4 control points   (the support / "where")
p_φ  ∈ P([0,1])      K = 16 softmax bins, or a monotone quantile net   (the dwell / "how long")
μ̂ = (γ_θ)_# p_φ ,    Ŝ = γ_θ([0,1]) ,    plus a conformal radius r̂.
```

Two heads, `d·M + K` numbers. Note what this makes explicit: **every existing intra-exposure trajectory method is the special case `p_φ ≡ Unif`, and every conventional detector is the special case `M = 1, K = 1`.** The representation is a strict generalisation with a two-parameter reduction to each.

### Objective

**(L1) Measure loss** where sub-exposure GT exists (simulation; FE108/EVIMO2 mocap):
```
L_meas = SW₁(μ̂, μ) + λ_S · Hausdorff(Ŝ, S)
```
with `SW₁` the sliced 1-Wasserstein over `d` dims (32 random projections; cheap, differentiable).

**(L2) Point-label likelihood with the convention as a latent variable** — the contribution that makes this trainable on *every existing benchmark*:
```
L_point = − log Σ_{A ∈ 𝒜} π_A · N( ŷ ; A[μ̂] , σ² )
```
`π ∈ Δ^{|𝒜|−1}` is a **single global vector per dataset**, fit by EM alongside the network. It is identifiable because different frames have differently shaped `μ̂`, so the functionals separate. Recovering `π` is itself a quotable result: *"we read a benchmark's unwritten annotation convention off its labels."*

**(L3) Photometric consistency — the frame as mass, label-free:**
```
L_blur = ‖ B − Â ⊛ Π_# μ̂ ‖₁      (Â = predicted sharp appearance of the crop)
```

**(L4) Event-order consistency — the events as order, label-free:** contrast-maximisation. Warp each event by the intra-exposure displacement the model predicts at its own timestamp and maximise the variance of the warped image:
```
L_evt = − Var_x [ Σ_e δ( x − x_e + Π(γ_θ(P_φ^{-1}((t_e − t0)/T))) ) ]
```
`P_φ^{-1}` is the dwell quantile function: **this term is exactly where the dwell density gets its time-parametrisation from the events**, and it is zero-gradient if `p_φ` is clamped uniform — which is why the `p ≡ Unif` ablation must fail.

**(L5) Conformal calibration — post hoc, no sub-exposure GT required.** On a held-out calibration split with only ordinary point labels, compute `s_i = inf{ r : ŷ_i ∈ Ŝ_i ⊕ r }`, set `r̂` to the `⌈(n+1)(1−α)⌉`-th order statistic. Then
```
P( ŷ_new ∈ Ŝ_new ⊕ r̂ ) ≥ 1 − α ,
```
**marginally over the benchmark's own (unknown) convention distribution**, by split-conformal exchangeability — the convention is part of the data-generating process, so we never need to know it. This is what makes a set-valued prediction *auditable against a point-labeled benchmark*, which is the evaluation half of the contribution.

Total: `L = L_meas + λ₂L_point + λ₃L_blur + λ₄L_evt`, with `L_meas` dropped on datasets lacking sub-exposure GT.

---

## What existing methods cannot express

1. **Time-reversal pairs.** Two clips in which an object traverses A→B and B→A over one exposure produce **bit-identical blurred frames** (Prop. 1) and identical point labels under `A_mid`, `A_mean`, `A_mode`, `A_hull`. No frame-only method — deblurring, trajectory recovery, or detection — and no uncertainty head can separate them, *even in principle*. Our `(γ, p)` with `L_evt` separates them at ~100 %. This is an un-arguable experiment: it is a proof, not a benchmark delta.
2. **Dwell concentration (stop-and-go inside the exposure).** An object that decelerates to rest mid-exposure has `A_mode` far from `A_mid`. A point label cannot express it; a *uniform-dwell trajectory* (`p ≡ Unif`) — which is what intra-frame trajectory methods effectively assume for a semantic state — cannot express it either. Only the dwell density can.
3. **Disconnected support (mid-exposure occlusion).** The object passes behind a pole during the exposure: `S` is two components. There is no single box, and no connected tube, that is correct. A measure with disconnected support is.
4. **Zero-width vs. finite-width labels.** A static object and a fast one both receive one box. Nothing in the current formulation distinguishes *"this label is a fact"* from *"this label is one arbitrary pick from a 40-px set"*. The support width is exactly that distinction, and it is the quantity a downstream consumer (a controller, a tracker's motion model, a training loss) most needs.
5. **The annotation convention itself.** No existing method has any place to put `π`. Ours reads it off the data.

Points 1 and 3 are phenomena that existing *representations* cannot encode, not merely tasks existing methods perform badly.

---

## Why this is not <closest work>

| Title | Venue, Year | What it does | Why we differ |
|---|---|---|---|
| Improved Handling of Motion Blur in Online Object Detection (Sayed & Brostow) | CVPR 2021 | Names the problem: "when an image is motion blurred, objects are no longer confined to the bounding boxes they had occupied in the sharp image", introducing label ambiguity. Fixes it by **re-generating a better single label** for blurred COCO. | They resolve the ambiguity by *choosing one convention more carefully* — which is exactly the move we argue is unavailable. We keep the ambiguity as the signal, measure that the choice reorders leaderboards, and predict a set. No events, no exposure-support theory, no coverage guarantee. |
| Motion-from-Blur: 3D Shape and Motion of Motion-Blurred Objects (Rozumnyi et al.) | CVPR 2022 | Recovers 3D shape + start/end pose + offsets of a fast object from a blurred frame. | Frame-only, hence subject to Prop. 1's reparametrisation orbit; predicts one deterministic trajectory with no dwell density and no guarantee; needs an isolable FMO on a clean background. We predict a *measure*, use events to break the orbit, and train from point labels. |
| Tracking by Deblatting / TbD-3D (Kotera, Rozumnyi, Šroubek, Matas) | ICCVW 2019 / IJCV 2021 | Intra-frame trajectory of fast moving objects via joint deblurring+matting; introduces Trajectory-IoU. | Closest *evaluation* relative: TIoU compares a predicted curve to a GT curve. It still presumes a unique GT curve and requires a high-speed-camera GT trajectory. We compare a *set/measure* to a *point label* — the mismatch is the contribution — and we quantify convention-dependence, which TIoU cannot see. |
| Exposure Trajectory Recovery from Motion Blur (Zhang et al.) | TPAMI 2021 | Dense pixel-wise displacement at multiple timepoints inside the exposure, for blur synthesis/removal. | Pixel-level and restoration-oriented; never proposed as the supervision target for a *semantic* state, and frame-only so the time order is unidentifiable. |
| Single Image Deblurring Using Motion Density Functions (Gupta et al.) | ECCV 2010 | Camera motion as an MDF — "the fraction of time spent in each discretised camera pose". | The honest ancestor of our `μ`. But it is (a) *camera* ego-pose, (b) an intermediate latent for deblurring, never a prediction target, (c) frame-only, (d) has no notion of annotation convention, sets, or coverage. We lift MDF from image formation to supervision and add the event-order half. |
| Recovering Continuous Scene Dynamics from a Single Blurry Image with Events (Cheng et al.) | ICCV 2023 (arXiv 2304.02695) | Implicit Video Function: restores latent sharp images at arbitrary timestamps within the exposure, from blur + events. | Same physical setting, opposite conclusion: they *restore the single sharp state at each t* and hand the point-label formulation back intact. We argue the frame-level label has no such single value and must be reported as a set. Restoration, not supervision/evaluation. |
| BeNeRF: NeRF from a Single Blurry Image and Event Stream | ECCV 2024 | Recovers the camera trajectory *within the exposure* + a radiance field, from one blurred image + events. | Confirms our physics but for ego-pose and rendering; one deterministic trajectory, per-scene optimisation, no dwell measure, no label/benchmark claim, no generalisable predictor. |
| Frame-Event Alignment and Fusion Network (AFNet, Zhang et al.) | CVPR 2023 | High-frame-rate tracking to 240 Hz on FE240hz by aligning low-rate frames with high-rate events. | The strongest "why do you need sets?" objection, and our main baseline. AFNet turns one point into *many points* — and needs 240 Hz mocap labels to do it, which 99 % of benchmarks lack. We produce a calibrated *set for the frame's own window* from a single blurred frame + its events, trainable from point labels alone, with coverage guarantees. Also: AFNet is still scored by point IoU, so our Panel-C result applies to it. |
| Object Tracking by Jointly Exploiting Frame and Event Domain (FENet; FE240hz dataset) | ICCV 2021 | Frame–event tracking; contributes the 240 Hz-annotated dataset. | Provides our data. Plain frame+event fusion for a point estimate — precisely the contribution class our domain forbids and our thesis contradicts. |
| Adaptive Bounding Box Uncertainties via Two-Step Conformal Prediction (Timans et al.) | ECCV 2024 | Conformal, size-adaptive coordinate intervals for detection boxes. | Our conformal baseline. It inflates a *point* estimate isotropically to hit marginal coverage; it has no support model, no dwell, no notion that the label's variability is a physical set width, and it is uninformative about *why* a box is uncertain. We predict the set's shape and orientation from physics, so at equal coverage our sets should be substantially tighter. |
| Towards Streaming Perception (Li et al.) / STARE continuous-stream evaluation | ECCV 2020 / Nat. Commun. 2026 | Argues the benchmark's temporal protocol is wrong — because of *processing latency* — and redefines the metric (sAP). | Same *genre* of contribution (the protocol, not the model), which is a precedent in our favour. Different mechanism entirely: latency is about *when the answer is delivered*; support width is about *whether the question has a unique answer*. Their fix (score against the state at the delivery time) still assumes a single state at each instant. |

**Honest verdict on novelty.** The physics (blur kernel = dwell measure) is 2010. Intra-exposure trajectory recovery is 2019–2025. Conformal boxes are 2024. What we could not find anywhere: (i) the exposure occupancy measure as the **supervision and evaluation target of a semantic state**, (ii) the **frame-mass / event-order complementary-identifiability** pair stated and tested, (iii) **learning a set-valued output from point labels with the annotation convention as a latent variable**, (iv) **convention-marginal conformal coverage** as a way to score set predictions on point-labeled benchmarks, and (v) the measurement that **acceleration, not blur magnitude, governs label well-posedness**. Searches covering CVPR/ICCV/ECCV/NeurIPS/ICLR 2023–2026 and arXiv returned no combination of these.

---

## Experimental plan

### Datasets

| Dataset | Role | Size | Availability risk |
|---|---|---|---|
| **Controlled simulation** (10 kHz analytic renders + sub-frame averaging + **v2e**) | Primary training + the only source of exact `μ` GT and of `β`-matched / `ν`-varying pairs | ~30 GB generated locally | **None.** v2e is pip-installable. This is why simulation is the right call here: no real benchmark contains set-valued GT, and only a simulator can hold blur fixed while varying acceleration. |
| **FE108 / FE240hz** (DAVIS346, 20/40 FPS APS + real events + **240 Hz Vicon boxes**) | Primary real validation; the only public event+frame set with sub-exposure GT | 143 K frames + events; est. 50–100 GB; a 20-sequence subset suffices | **Medium.** Gated by an application form (fe108.dluticcd.com), not a direct download. Apply in week 1. |
| **EVIMO2** | Fallback real validation in 6-DoF pose space; 200 Hz Vicon object poses | **~40 GB, direct download** | **Low.** |
| **BS-ERGB** (TimeLens++) | Real events+frames with fast object motion; used only for `L_blur`/`L_evt` self-supervision and for the `π` EM | ~30–60 GB | **Low.** |
| **DSEC-Det** *(stretch)* | Convention-marginal conformal audit on a point-labeled event benchmark we did not design | subset only; full DSEC is >100 GB | **Medium** (size). Optional; FE108 with its 240 Hz labels *withheld* gives the same audit at zero extra download and is the primary plan. |

We deliberately **do not** use Prophesee GEN1/1Mpx as a primary: 1–4 Hz labels and ~120 GB+ make the intra-exposure question unobservable there.

### Controlled variable

`ν` (normalised intra-exposure velocity change), **with `β` (blur magnitude) matched pairwise**. This pairing is the experimental design: without it every result is attributable to "more blur is harder", and with it that explanation is closed off. Secondary sweep: exposure `T ∈ {1, 2, 4, 8, 16} ms`.

### Baselines (all real, all named)

- **FENet** (ICCV 2021) and **AFNet** (CVPR 2023) — SOTA frame+event point trackers on FE240hz; re-scored under both conventions.
- **ToMP-MF, DeT, HMFT** — the three further trackers reported on FE240hz, used for the leaderboard-`τ` experiment.
- **Motion-from-Blur** (CVPR 2022) and **TbD-3D** (IJCV 2021) — frame-only intra-exposure trajectory; our `p ≡ Unif`, no-events reduction.
- **Exposure Trajectory Recovery** (TPAMI 2021) — adapted from pixel offsets to box space.
- **KL-Loss bounding-box regression** (He et al., CVPR 2019) / a Gaussian aleatoric head — the "uncertainty already covers this" straw man. Must be knocked down explicitly: a symmetric unimodal variance cannot represent an anisotropic, possibly disconnected, non-uniformly-weighted support.
- **Two-step conformal boxes** (Timans et al., ECCV 2024) — conformal baseline at matched coverage.
- **EFNet / event-based deblur → off-the-shelf detector** — shows that deblurring silently *picks one convention* (whichever timestamp it restores) and inherits its bias.

### Metrics

Existing metrics (IoU, AP, RSR/RPR, EPE, ADE, TIoU) are blind for a structural reason: **they compare a point to a point.** They give zero credit for correctly reporting that the state occupies a set of width `w`; they give full credit to a model that happened to match the annotator's habit; and they cannot detect that the label itself moved when the habit changed. So:

- **CS — Convention Spread** *(a dataset statistic, not a model score)*: `1 − min_{A,A'} IoU(A[y], A'[y])`. Reported per attribute split. This is the diagnostic and it is new.
- **CMC@α — Convention-Marginal Coverage**: fraction of the benchmark's own point labels contained in `Ŝ ⊕ r̂`. Target `1−α`. **Computable on any point-labeled dataset with no sub-exposure GT** — this is what makes the formulation adoptable.
- **SetEff — Set Efficiency**: `E[|Ŝ ⊕ r̂|]` in state-space measure. Coverage is trivial to buy; efficiency is the real score. Always reported as the **CMC–SetEff frontier**, never a single number.
- **CI-AP — Convention-Invariant AP**: AP in which a detection is a TP iff the GT label lies in the predicted set, reported *as a curve against SetEff*. Degenerates to standard AP as `|Ŝ| → 0`, so it is backward-compatible and a reviewer can locate every existing number on it.
- **dW₁** (dwell Wasserstein, `W₁(μ̂, μ)`) and **sJ** (support Jaccard) — only where sub-exposure GT exists. `dW₁` is the metric that separates us from uniform-dwell trajectory methods; `sJ` alone would not.
- **Order accuracy** on time-reversal pairs — a binary, chance = 50 %.
- **`π` recovery error** — on simulation where the true convention is imposed.

### Ablations

| # | Ablation | Purpose | Prediction |
|---|---|---|---|
| A1 | frame-only / event-only / both | **The identifiability test — the most important experiment in the paper** | frame-only ≈ 50 % on order accuracy (chance, per Prop. 1); event-only degrades `dW₁` badly (no mass); both ≈ 100 % / best `dW₁` |
| A2 | `p_φ ≡ Unif` vs. learned dwell | isolates the dwell contribution vs. trajectory methods | `dW₁` gap widens monotonically with `ν`; near-zero gap at `ν=0` (a *predicted null* — good science) |
| A3 | spline control points `M ∈ {2,3,4,6}`, dwell bins `K ∈ {4,8,16,32}` | capacity | `M=4, K=16` saturates |
| A4 | latent-convention EM on/off; report recovered `π` per dataset | the headline interpretability result | `π` concentrates differently on FE108 vs. BS-ERGB vs. simulation |
| A5 | exposure `T` sweep | shows the effect is exposure-driven, not sensor-driven | `CS`, `dW₁` gap grow ~linearly in `T` at fixed `ν/T` |
| A6 | conformal `α` sweep and calibration-set size | validity check | empirical CMC tracks `1−α` within ±2 % for `n ≥ 500` |
| A7 | **downstream payoff**: reweight a *standard* point detector's training loss by `1/(predicted support width)` | practical win for reviewers who want a number | +1.5–3 mAP on the fast-motion subset, ~0 on the slow subset |

A7 matters strategically: it converts the paper from "your benchmark is broken" into "…and here is a drop-in fix that improves your existing numbers."

### Compute (must fit 9 GB, days not weeks)

- Backbone ConvNeXt-Tiny or ResNet-18; input = 256×256 crop + 5-bin event voxel grid; batch 24; AMP fp16 → **≈5.5–7 GB peak**, verified before any long run.
- Heads are `d·M + K ≈ 80` outputs. Negligible.
- One training run ≈ **5–6 h** on a half-shared RTX 5090.
- 4 main runs + 7 ablation groups (~16 runs) ≈ **110–130 GPU-hours**, ~6–8 wall-clock days at 50 % GPU share. Conformal calibration and all metric computation are CPU-only.
- v2e simulation is CPU-bound: ~2 days, run concurrently with GPU training, zero VRAM.
- Everything in Docker. **Flagged infra risk:** RTX 5090 is `sm_120`; the container must be CUDA ≥12.8 / PyTorch ≥2.7. Verify on day 1 with a one-line `torch.zeros(1).cuda()` before committing to the schedule.

---

## Risks

**Risk 1 — The convention spread is small on real data.** Real annotators may be consistent enough, and real FE108 exposures short enough, that `D` stays under 0.1 and no leaderboard ever reorders. The failure phenomenon then has no teeth and the paper is a simulation exercise.
*Fallback:* pivot the knob from `ν` to `T`. Use FE108's `low light` and `HDR` splits, where APS exposure is longest and blur is worst, and add EVIMO2 6-DoF pose where **in-exposure rotation makes the mean/mid gap geometrically unavoidable** (rotation averages non-linearly on SO(3), so `A_mean ≠ A_mid` even at constant angular velocity — a case where our effect survives even zero linear acceleration). If it still does not appear, the paper reframes as a *measurement* paper: "we bound the definitional share of remaining benchmark headroom via the oracle floor `e*`", which is publishable on its own and is a genuine negative-result-with-a-number rather than a null.

**Risk 2 — "This is just aleatoric uncertainty / trajectory estimation with extra steps."** The single most likely reviewer response, and the one that kills the paper if unanswered.
*Fallback:* do not defend it with benchmark deltas; defend it with the two things a variance head and a frame-only trajectory *provably* cannot do. (a) The **time-reversal pair** experiment — identical frames, opposite motion, chance-level for every frame-only and every uncertainty method, ~100 % for ours. That is a proof, and it goes in Figure 2, not the appendix. (b) The **recovered annotation convention `π`** — no uncertainty method has anywhere to put it. Lead the paper with Propositions 1–2 and ablation A1 so the identifiability claim, not the accuracy claim, is what the reviewer is asked to evaluate.

**Risk 3 — Data access and the sim-to-real gap.** FE108 is application-gated and may be slow or refused; we have no event camera on site, so there is no capture fallback; and a reviewer will discount a v2e-only result as "you validated your assumption on data generated under your assumption."
*Fallback (three layers).* (i) Apply to FE108 in week 1 and start immediately on **EVIMO2 (40 GB, direct, 200 Hz Vicon)**, which supports the entire real-data story in pose space. (ii) Use **BS-ERGB** for real-event self-supervised terms even without sub-exposure GT. (iii) Validate the simulator explicitly: match v2e event-rate, polarity-ratio and inter-event-interval statistics against a real EVIMO2/BS-ERGB clip and report the discrepancy in the main paper. If the sim-real gap is large, restrict all *quantitative* claims to real data and demote simulation to the role it is uniquely good for — the `β`-matched `ν` sweep, which is a *controlled contrast*, not an absolute number, and is therefore far more robust to the gap.

---

## Self-score

| Axis | Score | Harsh justification |
|---|---|---|
| **Novelty** | **8 / 10** | The representation unit genuinely changes (point → measure on the exposure support), and three sub-claims appear unpublished: frame-mass/event-order complementary identifiability, set-valued learning from point labels with the convention latent, and convention-marginal conformal evaluation. Docked two points because the *physics* is Gupta 2010 and the *trajectory* half is well-trodden (TbD, Motion-from-Blur, BeNeRF, IVF). If a reviewer reads only the method figure, it looks like "trajectory + a density". The novelty lives in the problem statement and the evaluation, which is a riskier place for it to live. |
| **Feasibility here** | **7 / 10** | Model is tiny and fits 9 GB with room to spare; simulation is CPU-side and free; EVIMO2 is 40 GB and directly downloadable. Real risks are FE108's application gate and v2e CPU throughput, not compute. The `sm_120` container issue is a day-one nuisance, not a threat. Docked for depending on a gated dataset for the single most important real-data figure. |
| **Reviewer-proof-ness** | **6 / 10** | The weakest axis, honestly. "This is aleatoric uncertainty" and "just predict the trajectory at 240 Hz like AFNet" are both fast, cheap reviewer rejections, and the counter-arguments (Props. 1–2, reversal pairs) require the reviewer to engage with the theory. Protocol-criticism papers also draw "so what does this change?" — mitigated by A7's drop-in mAP gain, which is why A7 is non-optional. And everything rests on the failure plot landing on **real** data; if only simulation shows the effect, this is a 3/10. |
| **Is this incremental?** | **No — conditionally.** | Not incremental *if* Panel A separates on FE108/EVIMO2 and the leaderboard `τ` actually drops: then the paper says a benchmark's ranking is decided by an unwritten convention, which is a formulation result. It **becomes incremental** in exactly one failure mode: if the convention spread is negligible on real data, then `μ̂` collapses to a trajectory, `L_point` collapses to an L1 loss, and what remains is "event-guided intra-exposure trajectory estimation with a conformal wrapper" — a solid workshop paper and a CVPR reject. **The whole bet is on the failure phenomenon, and it must be measured in week 1, before a single model is trained.** |

**Kill criterion (decide by day 7).** If, on FE108 or EVIMO2, `median CS < 0.08` on the fast-motion split *and* the leaderboard Kendall `τ` stays above 0.85 in the top `ν` decile, abandon this angle and report it as a negative result rather than pivoting the story to save it.

---

**한국어 요약.** 핵심 주장은 "노출 시간 동안 상태는 하나가 아니다"이다. 프레임 라벨은 노출 구간 `W` 위 상태 궤적 `y(·)`의 *점유측도* `μ = y_#Unif(W)`에 어떤 미지의 범함수 `A`(중앙시각/시간평균/최빈체류/합집합박스 등)를 적용한 값이며, 어떤 벤치마크도 그 `A`를 명시하지 않는다. 따라서 (1) 라벨 불량성은 통념과 달리 **블러 크기가 아니라 노출 내 가속도**에 의해 결정되고(등속이면 아무리 블러가 커도 모든 관례가 일치), (2) 관례를 바꾸면 FE240hz 리더보드 순위가 뒤집힐 것으로 예측한다. 재정식화는 상태 대신 `μ`를 예측하는 것이며, 이론적 핵심은 **프레임은 `μ`의 질량만, 이벤트는 그 시간 순서만 관측하므로 어느 한쪽만으로는 식별 불가능**하다는 명제 1–2다(단순 융합이 아니라 식별가능성 논증이라 도메인 제약을 충족). 표현은 지지곡선 `γ_θ` + 체류밀도 `p_φ`이고, 기존 궤적 방법은 `p ≡ Unif`, 기존 검출기는 `M=K=1`인 특수 경우다. 점 라벨만 있는 데이터셋에서도 관례를 잠재변수로 두는 EM(`L_point`)으로 학습 가능하고, 분할 컨포멀로 **관례-주변 커버리지 보장**을 부여해 점 라벨 벤치마크 위에서 집합 예측을 감사할 수 있다. 데이터는 시뮬레이션(v2e, 정확한 집합 GT + 블러 고정/가속도 스윕) + 실측 FE108(240Hz Vicon, 신청 필요) / EVIMO2(40GB 직접 다운로드) / BS-ERGB. 9GB VRAM 내 ConvNeXt-T 기준 총 110–130 GPU-시간. 최대 위험은 실데이터에서 관례 간 차이가 작을 경우이며, 이때 논문은 궤적 추정 + 컨포멀 래퍼로 축소되어 증분 연구가 된다 — **따라서 실패 현상 측정을 학습보다 먼저, 1주차에 끝내야 한다.**
