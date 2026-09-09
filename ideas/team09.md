# Change-Time: Replacing Event Slicing with Per-Pixel Clocks for Event–RGB Perception

*Idea Team 9 / CVPR 2027 / Domain: Temporal-Support-Aligned Event–RGB Perception*
*Attack angle: kill the assumption that a canonical global timeline exists.*

---

## One-sentence thesis

Every event pipeline, including the newest adaptive ones, *partitions* the stream — it selects events by wall-clock duration and hands a flat tensor to a network — and we show this framework has a ceiling no partitioning rule can pass; so we stop cutting and re-coordinate, indexing each pixel by its own accumulated change `τ(x,t) = C·N(x,t)`, a clock **field** in which the event stream is a complete observation, the RGB frame's temporal support becomes a *measured, spatially varying* width `W(x)`, and the representation is *exactly* invariant to any monotone reparameterization of time.

**Two pillars, both verified unclaimed.** (i) `"temporal support"` + `"event camera"` returns **zero** arXiv abstracts. (ii) Reparameterization invariance as a stated formal property for event data returns **zero** across ten independent probes (arXiv API, arXiv search, dblp).

---

## The assumption we kill

**The assumption:** *there exists one time axis, shared by every pixel and every modality, on which all observations can be resampled without loss, and the correct unit of that axis is the second.*

Embedded at three levels:

1. **Representation.** A voxel grid allocates `B` bins uniformly over `T` seconds. A time surface stores `t − t_last(x)` in seconds. An event frame accumulates over `[t0, t0+T]`.
2. **Architecture.** A 3D conv over `(b,x,y)` assumes bin index `b` means the same thing at every `(x,y)`. A transformer adds a temporal positional encoding keyed to the *global* timestamp. An RNN or SSM steps on a globally shared tick.
3. **Cross-modal.** The RGB frame gets one timestamp (usually exposure midpoint) and events are gathered relative to it. The 2026 representation-learning survey states the field's default in one sentence: **"the exposure duration can be treated as a constant hyperparameter when the actual exposure time is unavailable."**

**Why it is universal.** It is inherited, not chosen — from frame cameras, where a global exposure clock is a physical fact of the sensor, and from the fact that every mature spatial operator (convolution, attention over a grid, cost volumes) needs a *flat cut* `t = const` to have a tensor to act on. Nobody defends the assumption because nobody notices making it: it is filed under "preprocessing," or, in the literature's own word, **"partitioning."**

### What breaks

- **The unit is wrong.** The second measures duration. An event stream carries information in units of *change*: an event fires when log-intensity moves by the contrast threshold `C`, however long that took. A `B`-bin voxel grid over `T` seconds has temporal quantization error `C·R·T/B` in change units — **linear in the scene's event rate**, i.e. in speed. That term is in the representation, not the estimator; training cannot remove it.
- **The clock is not shared.** Events are produced by `∂L/∂t = −∇L·v`, a *field*. A car at 20 m/s and a pedestrian at 1 m/s run two clocks at a 20:1 ratio in one image. The literature now names this — *heterogeneous velocity scenarios* (HVS) — which helps us: the phenomenon no longer has to be argued, only explained.
- **The recorded timestamp is not the true one, and the corruption is monotone and scene-dependent.** This is the strongest and least-known point, and it comes from the field's own reference survey (Gallego et al., §II, Principle of Operation): the AER readout bus **"can become saturated, which perturbs the times that events are sent."** Bus saturation is event-rate dependent, i.e. worst exactly under fast motion. Second mechanism, §II-D: the refractory period means **"the larger the refractory period the fewer events are produced by fast moving objects."** So the stream we record is already `φ(t)` for an unknown, monotone, scene-dependent `φ`. **A representation that reads absolute seconds is reading a corrupted coordinate, and the corruption is worst where the task is hardest.** This preempts the obvious rebuttal — "sensor time is a real physical measurement, not a gauge" — on the field's own evidence.
- **For a static region, time is not merely unobserved — it is undefined.** If pixel `x` emits no events on `[a,b]`, `τ(x,·)` is constant there and `τ(x,·)^{-1}` is set-valued: **no measurement at `x` distinguishes any two instants in `[a,b]`.** Yet a voxel grid writes `B` entries for that pixel, a time surface returns a value keyed to seconds since an irrelevant past event, and a transformer assigns `B` distinct positional encodings. The representation manufactures a coordinate the sensor never measured, and the network must then learn to ignore a nuisance we invented.

### The template, borrowed from 4D reconstruction

HyperNeRF's critique of canonical space is an *impossibility* argument, not an empirical complaint:

> "Topological changes require a discontinuity in the deformation field, but these deformation fields are necessarily continuous."

The time-axis transplant writes itself: a single global timeline requires that all pixels' streams be sections of one shared, continuous, monotone clock, and event-rate-dependent readout delay breaks the shared-clock assumption exactly as topology change breaks the shared-template assumption. Both are identifiability failures, not accuracy failures. *(Note for related work: Shape of Motion (ICCV 2025) and Dynamic 3D Gaussians (3DV 2024) are genuinely canonical-free and can be cited as such; MoSca is **not** canonical-free, and "Reality Check" (NeurIPS 2022) critiques benchmark protocols, not canonical spaces — citing either as anti-canonical would be a factual error.)*

### The specific thing we kill: *partitioning* as a framework

The strongest current work states the framework outright. Sui et al., **ASTW (CVPR 2026)**, open by dividing event processing into "(i) partitioning the event stream into different groups, and (ii) transforming them into representations," then compare nine partitioning strategies (Fixed Time Window, Fixed Number of Events, ATSLTD, Adaptive Temporal Sampling, Adaptive Event Conversion, Adaptive Global Decay, SpikeSlicer, TORE, Event Lifetime) on two axes: *temporal adaptivity* and *spatial locality*. ASTW is the first to get both, at patch granularity, and wins (+2.6 mAP Gen1).

**We add their missing third column — *no global temporal reference* — and every row, ASTW included, gets ✗.** Their own algorithm says why:

> "To prevent patch-level time window partitioning from violating the causal consistency of the scene, we propose a minimum time-step strategy that **unifies the temporal reference across all patches** … **all patches share the same ending timestamp** … The global timestamp is updated based on the smallest window among all patches. This can result in overlapping time windows for some patches. This was found acceptable through experiments."

They broke the global clock, called the result a violation of causal consistency, and glued it back: a flat right edge, ragged left edges, and a global tick set by the *fastest* patch. Their ablation shows the glue is load-bearing (−1.2 mAP without it). That is the assumption, stated and defended by the people closest to the problem.

---

## The failure phenomenon

Two measurements, one per pillar. Both indict the formulation; neither is a tuning result.

### 4.1 Decisive plot — clamp-limited dynamic range

**Claim:** any partitioning rule whose output is a window measured in seconds has a bounded speed dynamic range, and past that bound it degrades to a fixed-time window. Not a tuning failure — a property of emitting a duration at all.

**Why it must happen, before the experiment.** A partitioning rule emits `Δt(x)` in seconds and must clamp it: ASTW uses `Δt = clamp(γ/D̄, Δt_min, Δt_max)` with tuned `Δt_min = 10 ms`, `Δt_max = 250 ms` — a **hard dynamic range of 25:1**. The clamp is not incidental: remove `Δt_max` and a static patch demands an infinite window; remove `Δt_min` and a fast patch demands a window shorter than sensor latency, yielding an empty frame. Every member of the family carries this pair, in milliseconds, tuned. A counting clock has no such range: `τ(x,t) = C·N(x,t)` is defined at every rate including zero, because **there is no duration in the formula to clamp**.

**Measurement.** Two textured objects A and B translate at `v_A`, `v_B`. Task: per-object 8-way motion-direction classification and per-object flow, scored **separately on A and B**.

- **Independent variable:** speed ratio `ρ = v_A/v_B`, swept `1 → 64`, **at fixed global event rate `R`** (both speeds rescaled to hold `R` constant). Fixing `R` is the whole point: it removes the absolute-speed confound adaptive slicing already handles and isolates *spatial heterogeneity of the clock*.
- **Axes:** x = `log2 ρ` (0→6); y = `err_B` (%), the **slow** object's error.
- **Curves:** fixed-time; fixed-count (swept `n`); Adaptive Temporal Sampling; Adaptive Global Decay; SpikeSlicer; TORE; SITS; **ASTW**; **ours**.

**Expected curve.** Second-valued rules are flat while the clamp is slack and rise once it binds:

> **ASTW tracks us to `ρ ≈ 25`, then turns upward toward the fixed-time baseline. Ours is flat across the whole sweep.**

The elbow is **predicted from their published hyperparameter table, not fitted**. That is what makes this a formulation indictment rather than a benchmark win: we say in advance where the strongest competitor breaks and why, and widening the clamp does not help — we sweep `(Δt_min, Δt_max)` and show the elbow moves while the ceiling remains, because widening `Δt_max` starves the fast object and widening `Δt_min` blurs it. Their own Table 8 already half-shows this: every non-default clamp pair loses mAP.

**Companion plot — estimation latency.** ASTW derives `Δt` from a density estimated over `Δt_ref = 250 ms` and EMA-smoothed, so at motion onset the window is set from stale statistics. Independent variable: time since a 4× acceleration step. Prediction: a transient with time constant of order `α·Δt_ref`; ours has **zero** onset latency, because counting updates on the event itself. Structural: *estimating a rate requires a window; counting does not.* This attacks ASTW's own showcase scenario (a pedestrian suddenly entering the field of view).

### 4.2 Second plot — the (k, T) grid: speed and exposure, decoupled

This is the frame-side measurement, and it is in our assigned domain. Playing a scene back k× faster simultaneously multiplies event rate by k **and** multiplies intra-exposure blur by k. Every existing study confounds them. We separate them:

- **`k` (speed knob):** rescale the source timestamps only. Pixels are byte-identical across `k`, so scene content is provably held fixed.
- **`T` (exposure knob):** synthesize the RGB frame by averaging `N` consecutive source frames. `N` sets support width; `k` sets event rate.

The result is a **2-D grid `(k, T)`** instead of one confounded axis. Prediction: for every fusion baseline, error is a function of the *product* `k·T` — because that product is the blur magnitude, and their fixed exposure hyperparameter cannot see it. For us, error is a function of `T` alone at fixed `W`, because `W(x) = C·N_exp(x)` measures `k·T` directly and divides it out. **The diagnostic signature is that baseline iso-error contours run along hyperbolas `k·T = const`, and ours run along horizontal lines.** Nobody has run this grid; the field's flagship benchmark (NTIRE 2025 event deblurring) states inputs are *spatially* aligned and gives no treatment of temporal alignment at all.

### Quantitative predictions (registered in advance)

| # | Quantity | Prediction |
|---|---|---|
| P1 | `err_B` at `ρ=64` vs `ρ=1`, fixed-time window | ≥ **+45%** relative |
| P2 | `err_B` at `ρ=64` vs `ρ=1`, global fixed-count | ≥ **+30%** — adaptive slicing does *not* rescue it |
| **P3** | `err_B` at `ρ=64` vs `ρ=1`, **ASTW** | ≤ +5% for `ρ ≤ 16`; ≥ **+20%** at `ρ ≥ 32`, elbow within a factor 2 of `Δt_max/Δt_min = 25` |
| P4 | `err_B` at `ρ=64` vs `ρ=1`, ours | ≤ **+5%** throughout |
| P5 | Onset transient after a 4× acceleration step: ASTW settling | ≥ 100 ms (order `Δt_ref`); ours **0** |
| **P6** | `(k,T)` grid: baseline iso-error contours fit `k·T = const` | `R² ≥ 0.9` for baselines; ours **`R² ≤ 0.3`** against `k·T`, `≥ 0.9` against `T` alone |
| P7 | **RIG** for our invariant branch | **exactly 0**, to float precision |
| P8 | RIG for voxel grid, time surface, ASTW under a monotone warp of rate ratio ≤ 4 | ≥ 4 points (ASTW's ms-valued clamp is not scale-invariant) |
| P9 | SSD (slope of error vs `log2 R`), ours | ≤ 0.3 points/octave; fixed-bin ≥ 2 |

**P3 is make-or-break.** If ASTW is flat to `ρ = 64`, the "just adaptive slicing" objection stands and pillar 1 dies (see Death 1). **P6 is the frame-side make-or-break** and is independent of P3 — the two pillars fail separately, which is the plan.

---

## The reformulation

### State space

Ideal DVS model: with `L(x,t)` the log-intensity, pixel `x` emits event `k` with polarity `p_k ∈ {−1,+1}` at `t_k(x)` when `L(x,t_k) − L(x,t_{k−1}) = p_k·C`.

**Definition (change-time; the clock field).** Per pixel, independently,

```
τ(x, t) = C · N(x, t) ,     N(x,t) = #{ k : t_k(x) ≤ t } .
```

`τ(x,·)` is non-decreasing, right-continuous, piecewise constant with jumps of size `C`, and equals the **total variation of the quantized log-intensity path at `x` on `[0,t]`** — arc length of a 1-D path, i.e. the canonical reparameterization-invariant parameterization. It has **no free parameter**; `C` is the sensor's own contrast threshold and only sets a scale.

The state space is the **per-pixel change-indexed path bundle**

```
S = { (x, k, p_k(x)) }_{x,k}   together with the ragged index field  N(x,·) .
```

There is no `t` axis in `S`. No window, no boundary, no clamp, no reference interval, no EMA.

### Three properties — elementary, provable, and that is the point

**(1) Exactness in change-time.** With `L̃(x,kC) := L(x,t_k(x))`,

```
L̃(x, kC) = L(x,0) + C · Σ_{j≤k} p_j(x) ,      |L̃(x,τ) − L̃(x,kC)| ≤ C  for τ ∈ [kC,(k+1)C).
```

**In change-time the event stream is a *complete* observation of the intensity path**, up to one unknown scalar `L(x,0)` per pixel and a uniform `O(C)` bound independent of speed. Everything normally attributed to "event data is sparse and lossy" lives entirely in the map `t ↦ τ`, not in `L̃`. The sensor is not lossy; the coordinate is.

**(2) Exact invariance.** For any strictly increasing `φ`, warping every timestamp `t_k ↦ φ(t_k)` leaves `N(x,φ(t)) = N(x,t)` and the polarity sequences unchanged, so `S` is **unchanged**. Any function of `S` is *exactly* invariant to monotone time reparameterization — not robust, not approximately: identical bit-for-bit.

This is not an exotic property; it is a known one that machine learning **deliberately throws away**. Neural CDEs (Kidger et al., NeurIPS 2020) have *tree-like invariance* — "a CDE is blind to the speed at which `X` is traversed" — and the paper's Appendix C explains that time must be re-added as an explicit channel precisely to destroy it, because their tasks need absolute time. Path signatures (Chevyrev & Kormilitzin 2016) are exactly invariant under time reparameterization, uniquely so up to tree-like equivalence (Chen 1958; Hambly & Lyons 2010). **Event vision is the domain where this invariance should be kept rather than destroyed, and nobody has said so:** zero arXiv hits for path signatures, signature kernels, rough-path theory, or Neural CDEs on event-camera data.

Non-invariant by contrast: voxel grids; time surfaces; TORE (a *fixed* `log(t − t_k + 1)` warp of timestamps); learnable-timescale SSMs; ASTW (clamp in milliseconds). Global fixed-count is invariant only to *global* `φ` — precisely the gap P3 exploits.

**(3) Undefined time, represented as undefined.** If `x` emits no events on `[a,b]`, `τ(x,·)` is constant and `τ(x,·)^{-1}(c) = [a,b]`. In `S` the interval collapses to **one entry**, not `B`. The representation says "there is no time here," because there is no measurement that could distinguish two instants. Storage and compute follow the measurement, not the wall clock.

### The frame: temporal support as a measured, spatially varying width

An RGB frame with exposure `[t0, t0+T]` is `B(x) = (1/T)∫ I(x,t) dt`. Push it through the (non-invertible) local clock via the **occupation measure**:

```
μ_x = (1/T) · τ(x,·)_# ( Leb|[t0,t0+T] ) ,   supported on [0, W(x)] ,
W(x) = C · N_exp(x) ,     N_exp(x) = # events at x during exposure ,

B(x) = ∫_{[0,W(x)]} exp( L̃(x,τ) ) dμ_x(τ) .
```

Two statements no existing fusion formulation makes:

- **`W(x)` is the frame's temporal support width at pixel `x`, in change units, obtained by counting.** Not a hyperparameter, not learned, not an attention weight. Blur *is* temporal support width; the event count *is* the blur severity, because both are driven by the same `|∇L·v|`. This is exactly the quantity ASTW's `D_ij = c·L_ij·v_ij/s²` estimates by patch-smoothing — we read it exactly, per pixel, with no lag.
- **Where `W(x) = 0`, `μ_x = δ_0` and `B(x) = exp(L̃(x,0))` exactly.** The frame is a *sharp, instantaneous, exact* observation there, simultaneous with the entire window in change-time. There is nothing to align, and the alignment cost must be exactly zero — while every current method still pays it and still assigns that pixel a fictitious "frame timestamp."

This is the seed made precise: frame and events do not share a temporal support, and **the mismatch is a per-pixel scalar we measure, not a global nuisance we model.**

### What is predicted, and the objective

Let `f_θ` be the invariant backbone reading only `S`. Two cross-pixel mixing operators exist, and they are different surfaces in `(x,y,t)`:

- **`t`-cut (ragged gather).** For an anchor `t_b`, gather `h(x, N(x,t_b))`. Flat in wall clock, ragged in local index. Anchors must be chosen `φ`-equivariantly (global count quantiles, or the physically given exposure boundaries) or invariance is lost. *This is the generalization of ASTW's "shared ending timestamp" — kept as one available operator instead of as mandatory glue.*
- **`τ`-cut (iso-change surface).** Slice at fixed local index `k` for all `x`: `h(x,k)`. A **curved hypersurface** in `(x,y,t)` — "every pixel after it has changed by the same amount." No voxel grid, no partitioning rule, and no shared positional encoding can express this.

The two cuts do not commute and neither is canonical: together they are the concrete form of "a partial order rather than a total order." Per-pixel chains give a total order *within* a pixel; the two cut families give the only legal cross-pixel relations. The network gets both and is never asked to reconcile them into one axis.

Joint objective (reconstruction form; specializes to any downstream head):

```
min_{L̃, L0}  Σ_x || ∫ exp(L̃(x,τ)) dμ_x(τ) − B(x) ||²           (frame, correctly supported)
            + λ_e Σ_{x,k} | L̃(x,kC) − L̃(x,(k−1)C) − C p_k |²    (events, exact in τ)
            + λ_u Σ_x ∫ ( |∂L̃/∂τ| − 1 )² dτ                     (unit-speed prior: τ is arc length)
            + λ_s Σ_b || ∇_x h(x, N(x,t_b)) ||_δ                 (spatial smoothness, on t-cuts only)
```

The frame term carries weight `∝ 1/W(x)`: decisive where the frame is sharp, discounted where it is a broad average. **The fusion weighting is derived from the sensor model, not learned.**

For rate-valued tasks the model factorizes speed out and back in:

```
v(x) = (dx/dτ) · (dτ/dt)
       └ invariant ┘   └ counted ┘
```

The backbone predicts `dx/dτ` (displacement per unit change, invariant under `φ`); the scalar `dτ/dt = C·r(x)` is read by counting. Directly testable: `dx/dτ` must be constant under a speed sweep while `v` is not.

---

## What existing methods cannot express

1. **A non-flat temporal cut.** Observations simultaneous *in change* but spanning different wall-clock instants across the image. ASTW comes closest and explicitly refuses it ("violating the causal consistency of the scene") by forcing a shared ending timestamp.
2. **A pixel with no time coordinate — the distinction between *measured-and-quiet* and *never-measured*.** No data structure in the field encodes it. Every representation returns a value for a static pixel in every bin. Time surfaces come closest and still fail: their value is `t − t_last` in *seconds*, so a static pixel's descriptor drifts as the clock runs — the manufactured nuisance in its purest form. DAGr's dataloader is the sharpest instance: it re-bases each sample so the newest event sits at `t = 1.0`, so **a static pixel is assigned a "now" determined by whichever pixel elsewhere in the image happened to fire last**. EV-SpSegNet's spatio-temporal-consistency loss assumes targets "form continuous curves in spatiotemporal point clouds" — an assumption that fails precisely at a stationary target, undiscussed.
3. **An unbounded clock dynamic range.** Any rule emitting a duration must clamp it. `τ` is defined at every rate including zero.
4. **A frame whose temporal support is *content-driven* and spatially varying.** Rolling-shutter work (EvUnroll, EvShutter, SelfUnroll, UniINR) already handles spatially varying support — but per *row*, from a *known readout geometry*. Nobody represents support that varies per *pixel* because of what the *scene* did, measured from the events themselves.
5. **An intensity error bound independent of speed.** Property (1): `O(C)` uniformly.
6. **Exact, checkable invariance.** `f(S) = f(φ·S)` to float precision, rather than a mAP drop that happens to be small — and rather than Monte-Carlo averaging over a gauge.
7. **Zero-latency rate response.** Everything that adapts a window must first estimate a rate over a window, hence lags. Counting does not.
8. **Robustness to the corruption the sensor actually applies.** Recorded timestamps are perturbed by rate-dependent AER bus saturation — an unknown monotone `φ`. A `φ`-invariant representation is immune by construction; every second-valued representation inherits the corruption, worst under fast motion.
9. **A genuine partial order.** The "causal" event DAGs (DAGr, EvGNN, HUGNet) reach a partial order only by *deleting edges from a total order*: DAGr's edge predicate is `||·||_∞ < R **and** t_i < t_j`, and that scalar comparison presupposes one shared number line. PEPNet states the opposite design choice outright — "the ordering of all points in the grouping and sampling process strictly adheres to the timestamp (T)" — sacrificing permutation invariance to impose a total order, as every Mamba/SSM event method must. Our per-pixel chains are incomparable by construction; no deletion step is needed because no total order was ever built.

---

## Why this is not <closest work>

Verified against the June 2026 survey *A Systematic Survey on Event Camera Representation Learning* (arXiv:2606.23078), which has **no category, no method, and no open-problem entry** for reparameterization invariance or timeline-free representations; its time normalization discussion is explicitly affine (min–max / window rescaling), never monotone-general.

### A. The time-axis / partitioning family

| Closest work | Venue/Year | What it does | Why we differ |
|---|---|---|---|
| **ASTW — Adaptive Spatial-Temporal Window**, Sui et al. | **CVPR 2026** | Per-patch windows from a max-entropy criterion: `Δt_ij = clamp(γ/D̄_ij, Δt_min, Δt_max)`, `D̄` an EMA- and spatially-smoothed density. Patch 4, `γ`=1.7, `Δt_ref`=250 ms, `Δt_min`=10 ms, `Δt_max`=250 ms. +2.6 mAP Gen1. Introduces **HetVel**, the first RGB-event HVS dataset. | **The most dangerous prior, and it hands us our argument.** (i) It re-imposes a global reference by its own admission, to avoid "violating causal consistency," and needs it (−1.2 mAP without). (ii) Output is a duration in ms, so **hard 25:1 dynamic range**, not scale-invariant — P3 predicts its elbow from its own table. (iii) It *estimates* a rate over 250 ms with an EMA, so it lags at onset — P5. (iv) Six tuned constants; we have none. (v) **Their own Table 5 shows patch size 1 is worse than 4 (49.9 vs 50.6)** — because per-pixel *density estimation* is noisy. We never estimate density and never convert a count to a duration. (vi) Representation is a binary event frame: order and polarity inside the window are discarded. (vii) It never touches the RGB frame's temporal support, despite building an RGB-event dataset. |
| **Speed-Invariant Time Surface (SITS)**, Manderscheid et al. | CVPR 2019 | Per-pixel surface: on an event set `S(x,p)=(2r+1)²` and decrement every neighbour above it. The stored value is the **rank** of the event among recent neighbourhood events. | **The most dangerous conceptual prior.** Ranks depend on ordering only, so SITS is *de facto* invariant to any increasing `φ` — but the authors never noticed: they claim only invariance to constant object speed, give no theorem, and characterize no invariance class. A reviewer will say "SITS with a theorem," so we pre-empt it: SITS (a) is a single handcrafted surface queried at a global time, hence still a flat cut; (b) discards magnitude and cannot reconstruct intensity; (c) is not a differentiable coordinate; (d) says nothing about static regions, frames, or spatial heterogeneity. We take its one true insight — order, not seconds — and make it a coordinate system with a stated equivariance, an `O(C)` bound, and a cross-modal consequence. |
| **TORE volumes**, Baldwin et al. | TPAMI 2022 | Per-pixel per-polarity FIFO of the `K` most recent timestamps; `TORE = log(t − FIFO + 1)`. | Closest *structure* to ours: per-pixel queues. But it stores **timestamps** under a **fixed** log warp, so it is not invariant (rescale time and every entry changes), and ASTW's Table 1 marks it "no temporal adaptivity." A fixed nonlinear warp of seconds is not a data-derived clock. |
| **Global fixed-count windows** (standard practice) | 2018–2026 | Cut a slice every `n` events so slice density is stable under changing motion. | Defeated by computation, not benchmark. Fixed-count applies a **single global** monotone reparameterization. Per-pixel quantization error under it is `C·n·r(x)/R`, and bin-starvation probability `≈exp(−n·r(x)/R)`: both depend on `r(x)/R`. It trades an absolute-speed failure for a relative-speed failure. Our clock is a **field** `τ(x,t)`, not a scalar `τ(t)` — a difference in the dimension of the object, not the value of a hyperparameter. |
| **SpikeSlicer**, Cao et al. | NeurIPS 2024 | An SNN emits spikes triggering slice boundaries, trained with a membrane-potential loss plus downstream-task feedback. | State of the art in *learned* window prediction — still a global scalar schedule with no spatial locality. Learning where to cut cannot escape the cutting framework: the output is a duration, clamped, producing a flat cut. |
| **State Space Models for Event Cameras**, Zubić et al. | CVPR 2024 | SSMs with learnable timescales; 3.76 mAP drop at higher inference frequency vs >20 for RNN/Transformer. | Solves robustness to **our own sampling choice** (window duration at inference), not to the **scene's** speed, and not to spatial heterogeneity: one learnable timescale is still one global clock. Empirical robustness vs our equality. Inputs remain voxel grids, so `C·R·T/B` is untouched. Strongest architectural baseline; co-plot on `R` and `ρ`. |
| **PASS — Path-selective State Space Model** | NeurIPS 2025 | Claims generalization across inference frequencies (−8.62% vs −20.69% baseline) over event lengths spanning 1–10⁹. | Same critique as above and the same axis (our sampling frequency, globally). "Path" here is unrelated to path signatures. Must be a baseline; must not be confused with our claim. |
| **Matrix-LSTM**, Cannici et al. | ECCV 2020 | A grid of per-pixel LSTM cells, each consuming that pixel's own stream. | Nearest architectural relative. But the window is cut *globally* (`[t0,t1]` for every pixel), `Δt` enters as a raw feature, output collapses to one flat 2-D surface, and no invariance holds. A learned aggregator *inside* the global-timeline formulation. |
| **EST / ERGO-12 / EvRepSL** | ICCV 2019 / ICCV 2023 / TIP 2024 | Learn or search the events→tensor map: learnable kernels over `Δt`; ranking representations by Gromov–Wasserstein discrepancy; self-supervised representation generators. | All output a tensor on a *global* bin axis. They optimize *what goes in the bins*, never *what the bin axis means*. |
| **AEGNN / DAGr / EvGNN / SlideGCN / HUGNet / EFGCN — graph-based nets** | CVPR 2022 / Nature 2024 / 2024–26 / ICCV 2021 | Events as a spatio-temporal graph; never voxelize. Neighbourhoods from a space-time radius with a scale constant `β` converting µs to pixels. | **Grid-free, not timeline-free — and we can prove it from their released code, which is the strongest single piece of evidence in the paper.** `β` is not a free design constant; it is *literally the reciprocal of the window length*. DAGr `utils/buffers.py`: `normalizer = stack([width, height, time_window])` with `time_window = 1e6` µs, i.e. **β = 10⁻⁶ = 1/(1 s)**. AEGNN `normalization.py`: `normalize_time(ts, beta=0.5e-5)` — and `torch.min(ts)` is a **window origin**, so the graph cannot be built until you know when the sample started. EFGCN writes it outright: `t*_i = ⌊β·t_i/T⌋`. PEPNet/EventMamba normalize by `(T_i − t_j)/(t_l − t_j)`, denominator = window length. **The one published objection is EvGNN's** (§III-B): choosing `r` "involves the definition of a proper scaling factor between time and space dimensions… β can compensate for a scale difference of several orders of magnitude, [so] this approach is only practical when high-precision arithmetic is available." Their fix swaps one global constant for two, and `r_t` is still an absolute duration. *Verify HUGNet's β at source before quoting — ours is second-hand via EvGNN.* |
| **DAGr — Low-latency automotive vision with event cameras**, Gehrig & Scaramuzza | **Nature 2024** | Asynchronous graph neural network fusing events and frames; the flagship "async, no grid" result. | Two facts from its code and ablations do our work for us. (i) `dsec_data.py` re-bases every sample so the newest event sits at `t = 1.0`: **a static pixel inherits a "now" defined by whichever pixel elsewhere in the image happened to fire last** — our undefined-time point, instantiated. (ii) Their ablation shows early temporal aggregation with `g_t = 1` — pooling the *entire* time axis at layer one — is worth **+10.6 mAP**. Their best configuration is the one that destroys the time coordinate. We propose replacing it rather than pooling it away. |
| **SECNet**, Ren et al. | **ICML 2026 (Oral)** | **EF-KNN** builds neighbourhoods from *feature* distance, "different from previous work utilizing coordinates to find the neighbors"; **D-FPS** makes `β` **learnable** rather than preset. | **The nearest escape attempt in the literature and the one we must engage directly.** It is simultaneously the best evidence that nobody escaped the clock and that someone nearly did. But a learnable `β` is still a scalar exchange rate between pixels and seconds — one number for the whole image, fitted rather than tuned — and absolute `t` still enters as an input feature, so nothing is invariant. Feature-space neighbourhoods remove the *metric*, not the *coordinate*. |
| **Neural Events**, Pellerito, Gehrig, Shiba, Scaramuzza | **arXiv 2606.19835 (Jun 2026)** | VQ-style codes over local context windows; emits a "neural event" **only when the code changes** — change-driven emission rather than time-driven. | **The most dangerous new arrival: three months old, from the DAGr lab, and change-triggered.** But it is a *tokenizer* — it decides *when to emit*, producing a sparser stream on the same timeline, and addresses redundancy and compute. It defines no coordinate, states no invariance, says nothing about static regions being *undefined* rather than quiet, and never touches the frame's temporal support. Strategic risk, not conceptual overlap; see Risks. |
| **Spiking Patches** (event tokenizer) | 2025–26 | Per-patch tokenization: each patch's counter advances on **local event count**, with **no timestamp comparison anywhere** in the tokenizer. | **A second unclaimed near-miss, structurally identical to SITS.** Its patches are mutually incomparable — a genuine product order, i.e. exactly the partial order we argue for — and the authors never name it: they immediately stamp absolute `t` on every token, scale by `1/50000`, apply a 3-way sinusoidal positional encoding, and evaluate in 50 ms windows, reimposing the total order downstream. We cite it as evidence the structure is reachable and unrecognized. |
| **PEPNet** (point-based, CVPR 2024) | CVPR 2024 | Point-based event backbone with grouping and sampling. | The quotable anti-example: **"the ordering of all points in the grouping and sampling process strictly adheres to the timestamp (T)"** — permutation invariance deliberately sacrificed to impose a total order. Every Mamba/SSM event method needs this structurally. |
| **AW-GATCN** | IJCNN 2025 | Segmentation length set from *local event density* rather than a fixed `Δt`. | Closest published relative of a locally-defined clock — and still emits a duration in seconds from an *estimated* density, so the clamp and lag arguments of §4.1 apply unchanged. |
| **AsyNet**, Messikommer et al. | ECCV 2020 | Converts a synchronous net to an asynchronous one with *identical output*. | Explicitly preserves global-timeline semantics. An efficiency result about *when* computation happens. Orthogonal, composable. |
| **Contrast maximization**: Gallego et al.; **Secrets of Event-based Optical Flow**, Shiba et al.; **Motion-prior CM**, Hamann et al. | CVPR 2018 / ECCV 2022+TPAMI / ECCV 2024 | Warp events to a reference time `t_ref` and maximize sharpness. Shiba adds a **multi-reference** focus loss over three `t_ref` "so that contrast is high at any reference time"; Hamann samples `t_ref` **uniformly per batch**. | **Do not claim "reference time is arbitrary" — Shiba and Hamann already say and fix that.** The community has independently rediscovered that `t_ref` is a gauge and marginalizes it away by Monte Carlo. Our claim is the strictly stronger one: the CM objective is invariant only under the **2-parameter affine group** `t → at+b` (`b` absorbed by re-choosing `t_ref`, `a` by rescaling `v`), and **not** under the infinite-dimensional monotone group. We get invariance *by construction*, not by averaging over an origin; and CM needs a motion model to define the warp, whereas our clock needs only counting. Event collapse is what happens when the canonical instant is over-trusted. |
| **From Contrast to Consistency**, Rethinking Event-based Continuous-Time Optical Flow | CVPR 2026 | Argues CM "neglects temporal continuity and structural coherence, leading to distorted trajectories under complex motion"; adds spatio-temporal structural consistency. | The most recent paper occupying "CM mishandles the time axis." Read in full; it fixes *trajectory* regularity within a global clock, whereas we remove the global clock. Framing must be visibly distinct. |
| **Neural CDEs**, Kidger et al.; **path signatures**, Chevyrev & Kormilitzin | NeurIPS 2020 / 2016 | CDEs possess *tree-like invariance* — "blind to the speed at which `X` is traversed"; signatures are exactly invariant under reparameterization. Both **add time back as a channel** to destroy it. | The mathematics we need, never applied to events (zero hits). We invert their design choice: the property they discard is the one event vision needs, because the recorded timestamp is corrupted. **Flag:** *From Jumps to Signatures* (2607.06652) applies signatures to temporal point processes — the nearest conceptual neighbour; expect a reviewer to raise it, and distinguish (unmarked 1-D point processes vs a spatially indexed marked process with a cross-modal partner). |
| **Event Lifetime; VK-SITS; ATSLTD; Adaptive Temporal Sampling (ASTMNet); Adaptive Event Conversion; Adaptive Global Decay** | 2015–2023 | Per-event lifetime from estimated velocity; robust time-surface variants; information- and threshold-triggered partitioning; scene-adaptive decay. | The rest of the partitioning family. Each emits a duration or decay constant in seconds from an *estimated* velocity or density, and each is dominated by ASTW in ASTW's own Table 2. Our argument against ASTW subsumes them. |

### B. The event–RGB temporal-support family

| Closest work | Venue/Year | What it does | Why we differ |
|---|---|---|---|
| **EDI**, Pan et al.; **EVDI/EVDI++**; **EFNet** (SCER) | CVPR 2019 / CVPR 2022, 2025 / ECCV 2022 | `B = (1/T)∫ I(f)·exp(c·E(t)) dt` and its learned successors (Learnable Double Integral); SCER bins events symmetrically about the target time within the exposure window. | **Honest overlap: EDI's integral and our `μ_x` integral are the same number** — a change of variables is exact, so we claim no new *value*. We claim a new *coordinate* and what it buys: `W(x)` as a per-pixel measured support, alignment vanishing exactly where `W=0`, downstream invariance, and a representation for perception rather than a reconstruction. All of these treat the exposure window as a globally uniform interval. |
| **BRENet — Flow-Guided Registration for RGB-Event Semantic Segmentation** | arXiv 2505.01548 (2025) | **Actually formalizes the mismatch**: RGB captured at `t_k` while events accumulate over `[t_{k−1},t_k]`; proves fusion weights cannot eliminate the **irreducible spatial shift** under positive lag + motion; re-casts misalignment as flow-estimation error. | **The most dangerous competitor for "we formalize it."** They formalize the **lag** (a scalar offset), we formalize the **support width** (a per-pixel measure). Their conclusion is "convert it to flow error and optimize"; ours is "the support is measurable and vanishes where the scene is static." They never sweep lag magnitude or speed, so P6 is untouched. Must be cited as the closest formalization and clearly separated. |
| **Exposure-agnostic VFI via Adaptive Feature Blending** | BMVC 2025 | Recovers sharp high-FPS video from blurry input under **unknown and dynamic exposure**; target-adaptive event sampling around the target timestamp *and* the unknown exposure window. | **The paper a reviewer will cite against us.** It treats exposure as an unknown *interval in seconds* to be estimated and sampled around. We do not estimate an interval: we count events inside it and obtain a *width in change units per pixel*. Their "agnostic" means robust to the unknown; ours means the quantity is directly observed. |
| **EBFI-BE (blind exposure)**; **ETES (unknown exposure time)** | CVPR 2023 / ECCV 2022 | Estimate or select the exposure window from the event stream before interpolating/deblurring. | The "unknown exposure" line. All treat the window as a global scalar to be recovered, then proceed as usual. None makes it per-pixel, none makes it a *change*-valued quantity, none observes that it is exactly zero where the scene is static. |
| **CMTA — Cross-Modal Temporal Alignment for Event-guided Video Deblurring** | ECCV 2024 | Intra-frame enhancement operating strictly **within the exposure time**, plus inter-frame alignment. | The clearest existing architectural split between "inside the exposure window" and "between windows" — our decomposition, but as modules rather than as a support model, and with the window's extent fixed and uniform. |
| **SelfUnroll** (IJCV 2025); **EvUnroll** (CVPR 2022); **EvShutter** (CVPR 2023); **UniINR** (ECCV 2024) | 2022–2025 | Rolling-shutter correction with events. SelfUnroll targets "the absence of temporal dynamic information *within* intra-frame scanlines and *between* inter-frame exposures." UniINR embeds **exposure time into the INR query**. | **The strongest precedent that spatially varying temporal support is a legitimate object — and the sharpest available contrast.** RS support varies per *row*, from *known readout geometry*, and is scene-independent. Ours varies per *pixel*, from *what the scene did*, and is measured. UniINR makes exposure a query variable; we make it a measured field. Cite as precedent, not as competitor. |
| **FAOD — Frequency-Adaptive Low-Latency Object Detection** | arXiv 2412.04149 (2024) | Names the "Event-RGB Mismatch"; Align Module + Time Shift Training; **reports mAP under up to 80× frequency mismatch, degrading only ~3 points**. | The best existing mismatch-magnitude sweep, and it is about *our sampling frequency*, not scene speed, and is used as a *robustness* claim rather than a failure diagnosis. Their `k` is our `k` with `T` held fixed — the 1-D slice of our 2-D grid. |
| **Time Lens / Time Lens++ / TimeLens-XL** | CVPR 2021 / 2022 / ECCV 2024 | Event-based VFI; XL decomposes large inter-frame motion recursively; motion magnitude is its explicit difficulty axis. | Synthesize at a queried global `t`, re-asserting the canonical timeline at the output. XL's motion-magnitude axis is the nearest thing to a speed curve in VFI, reported via skip-count rather than event rate. Releases BS-ERGB and HQ-EVFI, which we use. |
| **NTIRE 2025 Challenge on Event-Based Image Deblurring** | CVPRW 2025 | 15 teams, HighREV benchmark. | **Useful negative evidence:** the report states inputs are *spatially* aligned and gives no treatment of temporal alignment to the exposure window. The flagship benchmark assumes the problem away. |

**The one-paragraph answer to "this is just adaptive slicing."**
Adaptive slicing chooses a better duration and keeps the assumption that a duration is the right output. Every member of the family — including per-patch ASTW — must (a) emit a number in seconds, hence clamp it, hence have bounded dynamic range; (b) *estimate* a rate over some reference window, hence lag; (c) restore a shared timestamp so a convolution has a tensor to act on, hence give up the locality it just bought. We show no global schedule can work when `∇L·v` is spatially non-uniform (per-pixel error `C·n·r(x)/R`), and that no *local* schedule escapes either, because the failure has moved from the choice of duration to the existence of a duration. The correct object is a scalar **field** `τ(x,t)` with no duration in it at all. The price is that flat cuts no longer exist — which is why nobody has taken this step, and what our two-cut architecture is for.

---

## Experimental plan

### Stage 0 — Controlled proof (analytic simulator; ~2 GB; ~5 GPU-h; no downloads)

Two-object translating-texture scenes. Events generated **analytically** from ground-truth `L(x,t)` and `v(x)` (exact `t_k` by integrating `|∇L·v|`) — no simulator dependency, minutes to generate.
Sweeps: `ρ ∈ {1,2,4,8,16,32,64}` at fixed `R` (decisive, P3); `R ∈ {0.5,…,8}×R0` at `ρ=1` (setup, P9); acceleration-step onsets (P5); ASTW `(Δt_min,Δt_max)` sweep to show the elbow moves but the ceiling does not.
**Requires no dataset and about one day. Settles P3 and P5.**

### Stage 0b — The (k, T) grid (P6)

Source: one fixed high-FPS capture (GoPro 240 fps, or a Blender/Isaac scene where we own the trajectory).
- **`k`** = timestamp rescaling only, so pixels are byte-identical across `k`. In **DVS-Voltmeter**, divide the `info.txt` microsecond column by `k`. In **v2e**, set `--input_frame_rate` / `--input_slowmotion_factor`.
- **`T`** = average `N` consecutive source frames to synthesize the RGB frame. (HighREV uses the same recipe — 11 sharp frames → 1 blurry, ×4 RIFE upsampled — which gives us a citation for it.)
- v2e uniquely separates `--dvs_exposure {duration|count|area_count|source}` from the speed knob, so the exposure and rate axes can be crossed independently.

**Simulator-artifact control (mandatory).** TIDES (arXiv:2606.02058) documents that frame-derived simulators suffer *timestamp batching* that **intensifies during rapid motion and occlusion** — so any error-vs-speed curve produced on v2e or ESIM is attackable as a simulator artifact. We therefore (i) run the primary sweep on **DVS-Voltmeter** (stochastic voltage model, MIT, five pure-Python deps, trivially containerized) and cross-check on **v2e**; (ii) verify that the analytic simulator, which has no upsampling stage and therefore no batching, reproduces the curve; (iii) cite **EventAid**, the only benchmark that scores simulators against real captures. Reporting the same curve from three generators with disjoint failure modes is the defense.

### Stage 1 — Real data, zero-cost speed perturbation

For the ideal model, *the same scene at a different speed is exactly a monotone warp of the timestamps.* So speed can be perturbed on **recorded** data with no simulator and no label ambiguity: apply `t ↦ φ(t)` and map labels through `φ`. We use uniform scalings and random smooth monotone warps (integrated positive splines, rate ratio ≤ 4).
*Honest caveat, stated in the paper:* a warp does not reproduce sensor-level rate effects (refractory saturation, AER bandwidth, noise fixed in seconds). Stage 0b supplies that control, and we report the warped-real vs resimulated-real gap as a first-class number. Note this cuts both ways and in our favour: those very effects are the physical `φ` that motivates the invariance in the first place.

| Dataset | Use | Size (verified where stated) | Risk |
|---|---|---|---|
| **DSEC** per-sequence (~10 seqs) | real event+RGB, flow, `dx/dτ` factorization | full **452 GB verified**; train events **125 GB**, train images **216 GB**, DSEC-Flow train **3.7 GB**; per-sequence **250 MB–9 GB** → budget **~60 GB** | **lowest — no registration, direct HTTP, CC-BY-NC-SA** |
| **N-Caltech101 / N-Cars** | fast invariance sweeps, many seeds | ~6 GB / ~1–2 GB (est.) | N-Caltech **CC-BY-4.0**, cleanest license; N-Cars form-gated |
| **BS-ERGB** (Time Lens++) | beam-splitter aligned event+RGB → residual mismatch is *purely temporal*. Ideal for `W(x)` | not published; est. 50–150 GB | **form-gated + non-standard "evaluation license" — read it before building on it. Start the form today.** |
| **HS-ERGB** (Time Lens) | high-speed event+RGB | est. 30–100 GB | form-gated, link emailed. **Start today.** |
| **HQ-EVFI** (TimeLens-XL) | newest synchronized RGB+EVS, large-motion emphasis | not published | Google Drive quota risk |
| **HighREV** (REFID/NTIRE25) | exposure window is *constructed* from 11 sharp frames → re-synthesizable at different `T` | not published | Kaggle/CodaLab |
| **Prophesee GEN1** | ASTW / RVT / SSM-ViT head-to-head on their benchmark | not published; est. **≥250 GB** | medium; form-gated; **event-only, no RGB** |
| **HetVel** (ASTW) | the real HVS benchmark, RGB+event, 33 videos | small | **release not yet confirmed — check first** |
| MVSEC `indoor_flying` (+`outdoor_day1`) | secondary flow check; built-in speed axis | **~15 GB** (+19 GB) | link-rot warning on the host page |
| EVIMO2 v2 | per-object motion GT → bin evaluation by true object speed | **525 GB npz**; **~254 GB dropping the flea3 RGB cam** | large |
| ~~FE240hz / FE108~~ | — | — | **DEAD: host `fe108.dluticcd.com` refused connection. Do not plan on it.** |
| ~~EventVOT~~ for fusion | — | 38.8 GB event-image | **event-only, no RGB** — unusable for our fusion arm |

Disk budget ≤ 400 GB of 990 GB free. Order: analytic + DVS-Voltmeter (day 1, no downloads) → N-Caltech → DSEC per-sequence → GEN1 → BS-ERGB when the form clears.

### Baselines (named, re-run, not quoted)

*Partitioning axis:* fixed-time; fixed-count (swept `n`); Adaptive Temporal Sampling (ASTMNet); Adaptive Global Decay; SpikeSlicer; TORE; SITS; Event Lifetime; **ASTW** (critical — swept over patch size and `(Δt_min,Δt_max)`); Matrix-LSTM; EST; RVT; **SSM-ViT / S5**; **PASS**.
*Grid-free axis (to show grid-free ≠ timeline-free):* AEGNN; **DAGr**; EvGNN; SlideGCN; PEPNet; EventMamba; **SECNet**. For each, the `β`-sensitivity test is one line and free: rescale all timestamps by `s` and re-evaluate without retraining. Every one of them must move; ours cannot.
*Fusion axis:* EDI/mEDI; EFNet (SCER); EVDI/EVDI++; REFID; CMTA; **BRENet**; **exposure-agnostic VFI (BMVC 2025)**; UniINR; FAOD.
Backbone, representation and training config held identical across partitioning strategies, exactly as ASTW does, so the comparison is on their terms.

Sweeping ASTW's clamp is mandatory: if any clamp setting flattens the `ρ` curve, the hyperparameter objection stands.

### Metrics

Standard: accuracy (N-Cars/N-Caltech); mAP/AP50 (GEN1); SR/PR/NPR (HetVel/EventVOT); EPE and outlier-% (DSEC-Flow); PSNR/SSIM (deblur arm).

Invented — each measures something the field has no number for:

- **RIG — Reparameterization Invariance Gap.** `RIG = E_φ |m(f(φ·S)) − m(f(S))|` plus worst case over a warp family. Ours: exactly 0 on the invariant branch — a unit test, not a result. Proposed as a standard reporting column.
- **CDR — Clock Dynamic Range.** Largest `ρ` at which slow-object error stays within 5% of its `ρ=1` value. For any clamped rule this should equal `Δt_max/Δt_min`; for ours, unbounded. **The number that separates us from ASTW, and predictable a priori.**
- **SSI — Support-Separability Index.** From the `(k,T)` grid: `R²` of iso-error contours against `k·T` versus against `T` alone. A method that confuses rate with support scores high on the former. **The frame-side headline metric.**
- **HSP — Heterogeneous-Speed Penalty.** Slow-object degradation per octave of `ρ` at fixed `R`.
- **ORL — Onset Response Latency.** Time from an acceleration step to within 5% of steady-state error. Ours: 0 by construction.
- **USW — Undefined-Support Waste.** Fraction of representation entries in a pixel-window with zero events. Reported with FLOPs, since it is wasted compute.
- **SWC — Support-Width Calibration.** Correlation of measured `W(x)` with true per-pixel blur severity (GT on synthetic; sharp reference on BS-ERGB/HighREV). Validates that `W` is what we claim.
- **SSD — Speed-Slope Dependence.** Slope of the metric vs `log2 R`, points/octave.

### Ablations

(a) per-pixel `τ` → per-patch `τ` → global `τ` — a **continuum from ASTW to us**, the cleanest possible ablation: the last must reproduce fixed-count's failure, the middle must reproduce ASTW's elbow;
(b) drop `τ`-cuts, keep `t`-cuts (should recover ASTW-like behaviour);
(c) drop `t`-cuts, keep `τ`-cuts (are flat cuts needed at all?);
(d) re-inject `Δt` as a feature — **must destroy RIG=0**, confirming invariance comes from the coordinate, not the architecture (this is exactly the move Neural CDEs make deliberately);
(e) frame weight `1/W(x)` → learned attention;
(f) counting vs density-estimation at pixel granularity — the direct test of our explanation for ASTW's patch-size-1 result;
(g) `t`-cut anchor rule: uniform-in-seconds (must break invariance) vs count-quantile;
(h) three simulators (analytic / DVS-Voltmeter / v2e) on the identical sweep — the artifact control.

### Compute

One RTX 5090 (GPU 1, ~9 GB; GPU 0 currently free as headroom), Docker only, AMP, `320×240` crops, batch 4–8, gradient checkpointing on the per-pixel recurrence.
Stage 0 ≈ 5 h · Stage 0b `(k,T)` grid ≈ 25 h (v2e is 50–200× slower than real time, so keep clips short and lean on DVS-Voltmeter) · N-Caltech/N-Cars invariance sweeps ≈ 25 h · GEN1 head-to-head vs ASTW ≈ 80 h · DSEC-Flow ≈ 60 h (optional) · BS-ERGB frame-support arm ≈ 20 h.
**Core (Stage 0 + 0b + N-Caltech + GEN1) ≈ 135 GPU-h ≈ 6 days. Full ≈ 215 GPU-h.**
Memory risk is the ragged per-pixel stack: `640×480` with cap `K=16` is ~5 M entries — fine with a fixed-`K` packed buffer and a gather; no custom CUDA needed.
**No simulator ships a Dockerfile.** DVS-Voltmeter is a five-dependency MIT Python package and is a one-evening container; v2e's pinned CUDA + SuperSloMo stack is the real friction. Budget a day for containers.

---

## Risks

**Death 1 — ASTW (or a swept fixed-count) stays flat to `ρ = 64`.**
If P3 fails, "this is adaptive slicing at finer granularity" stands and pillar 1 dies. Sharpest risk: ASTW is CVPR 2026, built for heterogeneous velocity, and already reports gains across low/medium/high speed strata.
*Fallback:* pillar 2 is independent and untouched by ASTW — `W(x)` as a measured per-pixel temporal support, alignment vanishing where `W=0`, the derived `1/W` weighting, and the `(k,T)` grid. Re-pitch as "the frame's temporal support is a field, not an interval," on BS-ERGB/HighREV. Weaker, but publishable, and still not plain fusion.

**Death 2 — the error-vs-speed curve is a simulator artifact.**
TIDES (2026) documents that frame-derived simulators suffer timestamp batching that *worsens with rapid motion* — i.e. the exact regime we measure. A reviewer can attribute the entire curve to v2e's SuperSloMo interpolation rather than to the formulation. This risk applies to *both* pillars simultaneously and is the one most likely to be raised by an expert reviewer.
*Fallback:* designed for — three generators with disjoint failure modes (analytic, which has no upsampling stage at all; DVS-Voltmeter, stochastic; v2e, deterministic-threshold), plus the *zero-simulator* real-data path (monotone time-warping of recorded DSEC/GEN1, where the underlying capture is untouched by construction), plus the real high-speed captures in BS-ERGB/HQ-EVFI. If the curve survives all four it is not an artifact. If it survives only in simulation, we report that honestly and the paper becomes a much weaker analysis piece.

**Death 3 — pillar 2 is already occupied by the "unknown exposure" line.**
ETES (ECCV 2022), EBFI-BE (CVPR 2023), exposure-agnostic VFI (BMVC 2025), and BRENet (2025, which actually *proves* an irreducible shift under lag) have collectively taken "the exposure window is unknown and this hurts." A reviewer can say the support story is a re-description.
*Fallback:* the distinction must be made load-bearing rather than rhetorical, and it is testable: they recover an *interval in seconds, globally*; we measure a *width in change units, per pixel*, and predict it is exactly zero on static pixels. The falsifiable difference is **SWC** — if `W(x)` correlates with per-pixel blur severity at `r > 0.9` while any global exposure estimate cannot, by construction, produce a per-pixel number, the contribution stands. If SWC is weak, the honest retreat is to the invariance result alone (pillar 1) and the paper becomes a pure representation paper with no cross-modal claim.

**Secondary risks.**
*Discarding seconds discards the task.* Flow in px/s, time-to-collision, and physical velocity are genuinely rate-valued. Already designed for: `v = (dx/dτ)·(dτ/dt)` keeps an invariant backbone and reinjects the counted rate at the head via FiLM. Reframe as **disentangling what is speed-dependent from what is not**, and show `dx/dτ` transfers to unseen speeds while an end-to-end `t`-based model does not — arguably the better paper, and we should be ready to lead with it.
*Per-pixel counting is noisier than per-patch density.* ASTW's Table 5 shows patch size 1 underperforms patch 4; our explanation (they *estimate*, we *count*) must be demonstrated in ablation (f), not asserted. If it fails, fall back to a learned pooling over `τ` rather than over `t`, which preserves invariance.
*"Reference time is arbitrary" is taken.* Shiba (ECCV 2022) and Hamann (ECCV 2024) already marginalize over `t_ref`. We must never phrase the contribution that way; the claim is monotone-group invariance by construction versus affine-group invariance by Monte Carlo.
*Dataset access.* BS-ERGB and HS-ERGB are form-gated with emailed links and are the long pole — start both forms on day 1. FE108/FE240 is dead. HetVel's release is unconfirmed. GEN1's size is unpublished and possibly ≥250 GB.
*Absolute mAP.* We may not beat ASTW's 50.6 on GEN1. We must win on CDR/HSP/ORL/RIG/SSI at *matched* mAP and say so in the abstract rather than be caught.
*Scooping risk — Neural Events (Jun 2026).* Pellerito, Gehrig, Shiba & Scaramuzza emit a token **only when a learned code changes**: change-triggered rather than time-triggered, three months old, from the lab that produced DAGr and the CM line. They currently define no coordinate, claim no invariance, and never touch the frame — but they are one paper away from `τ`, and they have the datasets, the compute, and the priority. This is a schedule risk, not a correctness risk, and it argues for publishing the *coordinate and the theorem* early rather than waiting on a large benchmark sweep. Monitor arXiv for successors monthly.

*Two unclaimed near-misses cut both ways.* SITS (ranks) and Spiking Patches (a per-patch counter with no timestamp comparison anywhere in the tokenizer, hence a genuine product order the authors never name) both reach our structure and fail to recognize it. That is evidence the idea is reachable — and evidence a reviewer can say it was already reached. Our defense is that neither states a property, neither survives its own downstream stage (Spiking Patches immediately stamps absolute `t`, scales by 1/50000, applies a 3-way sinusoidal PE, and evaluates in 50 ms windows), and neither says anything about the frame.

*Citation hygiene.* Cite the ICCV 2021 method as **SlideGCN**, its own name — "EvS-S" is only a comparison-table label and using it will draw a flag. **EvT is not a graph/point method**: it voxelizes with `Δt` = 24/48 ms, `B` = 2–3 bins and a **2-D-only** positional encoding, so cite it as a counterexample, not an ally. HUGNet's `β` reached us second-hand through EvGNN's description — verify at source before quoting a number. DAGr's Nature version is paywalled; our code-level claims come from the arXiv twin and the public repository, which is what we should cite.

*Residual literature risk.* All negative searches ran on the arXiv API, arXiv search, ar5iv and dblp; the WebSearch quota was exhausted and CVF/Semantic Scholar rate-limited. Do one Google Scholar pass on `"signature transform" DVS`, `"signature kernel" spiking`, `Lyons event camera`, and `"temporal support" event camera` before committing. Estimated residual risk of a missed direct hit: **<5%**.

---

## Self-score

| Axis | Score | Justification (harsh) |
|---|---|---|
| **Novelty** | **7 / 10** | Two independently verified empty intersections: `"temporal support"` + `"event camera"` = 0 arXiv abstracts, and reparameterization invariance for event data = 0 across ten probes. The clock as a *field* with no duration in it, `W(x)` as a measured per-pixel frame support, and the import of tree-like/signature invariance into event vision are ours. Docked hard for three reasons. SITS (2019) already achieves monotone invariance *by accident* via ranks, so "SITS with a theorem" is a live jab. ASTW (CVPR 2026) already named heterogeneous velocity, localized the clock to patches, and built the RGB-event benchmark — the *observation* is taken and only the *formulation* is left. And the unknown-exposure line (ETES, EBFI-BE, BMVC 2025, BRENet) has already circled pillar 2. Originality now rests on "stop emitting durations" plus "support is a measured per-pixel width" — real conceptual moves, but narrower than they looked before the sweep. Partially offset by one asset acquired late and cheaply: the **`β`-is-the-window identity**, verifiable from released code (DAGr `time_window = 1e6` µs → `β = 10⁻⁶`; AEGNN `beta=0.5e-5` with `torch.min(ts)` as a window origin; EFGCN's `t*_i = ⌊β·t_i/T⌋`), which converts "graph methods are grid-free but not timeline-free" from an assertion into a citation. Counterweighted by two near-misses that a reviewer can wield — Spiking Patches already builds an unnamed product order, and Neural Events (Jun 2026) already triggers on change rather than time. |
| **Feasibility** | **8 / 10** | Stage 0 is an analytic simulator plus a small classifier: one day, no downloads, and it settles the make-or-break prediction. The invariance test needs no training at all. DSEC is registration-free with per-sequence downloads, N-Caltech is 6 GB and CC-BY, DVS-Voltmeter containerizes in an evening, and ASTW's protocol (hold backbone fixed, vary only partitioning) is exactly the cheap comparison we want. Docked for v2e's 50–200× real-time cost on the `(k,T)` grid, GEN1's unpublished and possibly ≥250 GB footprint, and two form-gated datasets on the critical path for pillar 2. |
| **Reviewer-proof-ness** | **6 / 10** | Better than it was: the "sensor time is a real measurement, not a gauge" rebuttal is now answered from the field's own survey (AER bus saturation perturbs recorded event times, rate-dependently), which converts the weakest point into motivation. But three hazards remain and none is fully closable. P3 is one experiment against a well-tuned CVPR 2026 method with six knobs a reviewer can ask us to re-tune. The TIDES simulator-artifact objection attacks both pillars at once and can only be answered by triangulation, not by proof. And Shiba/Hamann have already claimed the adjacent territory in CM, so a careless sentence in the intro is a desk-reject. A fourth hazard arrived with the graph sweep: SECNet (ICML 2026 Oral) makes `β` learnable and builds neighbourhoods in feature space, so "nobody escaped the coordinate" now needs a careful sentence rather than a blanket one. Held at 6 because every claim is falsifiable and pre-registered, which reviewers reward, and because the `β` evidence is code-level rather than rhetorical. |
| **Incrementality** (lower = better) | **3 / 10** | It changes the coordinate rather than the architecture, and the failure it names cannot be tuned away inside the partitioning framework — the opposite of incremental. Not a 2, because it lives inside an active and now-crowded sub-literature, reuses standard backbones and benchmarks, and its headline experiment is defined relative to one competitor's hyperparameters. It reframes a problem the field has just started naming; it does not open a field. |

**Verdict: pursue, conditionally and cheaply.** Two independent pillars, each with one make-or-break prediction, each settleable in about a day without downloading anything: **P3** (ASTW's `ρ` elbow at 25) and **P6** (`k·T` collapse on the exposure grid). **Run Stage 0 and Stage 0b before writing another word.** If P3 fails, fall back to pillar 2 alone. If P6 fails, fall back to pillar 1 alone. If both fail, drop the idea — do not try to rescue the slicing argument.

---

## 한국어 요약

- **죽이는 가정:** "모든 픽셀·모든 센서가 공유하는 단 하나의 시간축(초 단위)이 존재하고, 거기 리샘플링해도 손실이 없다." 복셀 그리드·타임 서피스·공유 positional encoding·프레임 타임스탬프가 전부 이 위에 있다. 2026년 서베이가 이 관행을 한 문장으로 자백한다 — *"노출 시간을 알 수 없으면 상수 하이퍼파라미터로 두면 된다."*
- **더 정확히는 "partitioning(분할)" 프레임워크 자체를 죽인다.** 최신 최강자 **ASTW (CVPR 2026, 칭화대)** 조차 패치별 시간창을 **초 단위**로 내놓고, "인과 일관성이 깨진다"며 **전역 타임스탬프를 다시 붙인다**(모든 패치가 같은 종료 시각 공유). 본인들 ablation에서 그 접착제가 −1.2 mAP만큼 필수라고 나온다.
- **핵심 재정의:** 시간을 초가 아니라 **변화량**으로. 픽셀별 국소 시계 `τ(x,t)=C·N(x,t)`. 로그 강도 경로의 arc length이며 **자유 파라미터가 0개**(ASTW는 6개). 단조 증가 변환 `φ`에 **정확히 불변**(근사 아님, 비트 단위 동일).
- **물리적 근거를 찾았다(중요).** Gallego 서베이 본문: AER 버스가 포화되면 **"이벤트가 전송되는 시각이 교란된다"** — 이벤트율 의존, 즉 빠른 움직임에서 가장 심하다. 게다가 refractory period 때문에 빠른 물체일수록 이벤트가 덜 나온다. **즉 우리가 기록하는 타임스탬프 자체가 이미 미지의 단조 `φ(t)`로 오염돼 있다.** "센서 시간은 실측값이지 게이지가 아니다"라는 리뷰어 반박을 이 분야 표준 서베이로 막을 수 있다. 원래 가장 약한 고리였던 부분이 오히려 동기가 됐다.
- **두 기둥, 각각 독립적으로 검증됨(둘 다 비어 있음):** ① `"temporal support"` + `"event camera"` arXiv 초록 검색 **0건**. ② 이벤트 데이터에 대한 reparameterization 불변성 = **10회 독립 검색 전부 0건**(잔여 위험 <5%). path signature / Neural CDE도 이벤트 카메라에 적용된 적 **없음**.
- **수학적 근거:** Neural CDE는 tree-like invariance("경로를 얼마나 빨리 지나는지에 무감각")를 갖는데, 그들은 시간을 채널로 다시 넣어 **일부러 그 성질을 파괴한다**. 이벤트 비전은 그 성질을 **지켜야 하는** 유일한 도메인이고, 아무도 그 말을 한 적이 없다.
- **프레임 쪽(우리 도메인, ASTW가 안 건드린 곳):** RGB 프레임의 시간적 지지는 구간이 아니라 **픽셀마다 다른 폭 `W(x)=C·N_exp(x)`**, 노출 중 이벤트를 세면 측정된다. `W(x)=0`이면 프레임은 정확한 순간 관측 → 정렬 비용 **정확히 0**. 융합 가중치 `1/W(x)`가 학습이 아니라 센서 모델에서 유도된다.
- **"그냥 adaptive slicing 아니냐"의 정량적 답:** 초 단위 창을 내놓는 규칙은 반드시 **clamp** 해야 하고 → **속도 동적 범위가 유한**. ASTW는 `Δt_min=10ms, Δt_max=250ms` → **25:1이 한계**. 또 창 길이를 정하려면 rate를 **추정**해야 하므로(250ms 기준창+EMA) 가속 시 **지연**. 세는 시계는 둘 다 없다.
- **결정적 실험 P3:** 전역 이벤트율 `R` 고정, 속도비 `ρ`를 1→64로 쓸고 느린 물체 오차. **예측: ASTW는 ρ≈25까지 평평하다 꺾인다.** 꺾이는 지점을 **상대 논문 하이퍼파라미터 표에서 미리 계산해 선언**하는 것이 핵심.
- **결정적 실험 P6 (프레임 쪽, 독립):** 속도 `k`(타임스탬프만 재스케일 → 픽셀은 바이트 동일)와 노출폭 `T`(원본 프레임 N장 평균)를 **분리한 2차원 격자**. 예측: 기존 방법의 등오차선은 쌍곡선 `k·T=const`, 우리는 수평선. 아무도 이 격자를 돌린 적이 없다.
- **새 위험(중요):** TIDES(2026)가 프레임 기반 시뮬레이터의 timestamp batching이 **고속 운동에서 심해진다**고 지적 → 우리 속도-오차 곡선이 시뮬레이터 아티팩트로 공격당할 수 있다. 방어: 해석적 시뮬레이터 + DVS-Voltmeter + v2e + **시뮬레이터 없는 실데이터 시간왜곡** 4중 삼각측량.
- **데이터셋 실무:** DSEC 전체 452GB(검증), 시퀀스별 250MB–9GB → 60GB만 받으면 됨, **등록 불필요**. N-Caltech101 ~6GB, CC-BY-4.0. **FE108/FE240 호스트는 죽었다**(연결 거부). EventVOT는 **RGB 없음** → 융합에 못 씀. BS-ERGB/HS-ERGB는 폼 승인 후 메일 발송이라 **1일차에 신청**해야 함. 시뮬레이터는 **DVS-Voltmeter**가 MIT + 파이썬 5개 의존성으로 도커화 가장 쉽고 속도 knob(info.txt μs 열 나누기)도 가장 깔끔.
- **그래프/포인트 계열도 timeline-free가 아니다 — 코드로 증명됨(늦게 얻은 가장 단단한 근거).** 그래프 방법들의 시공간 스케일 상수 `β`는 자유 설계 상수가 아니라 **윈도우 길이의 역수 그 자체**다. DAGr `buffers.py`의 `time_window = 1e6` µs → **β = 10⁻⁶ = 1/(1초)**; AEGNN `normalization.py`의 `beta=0.5e-5`이고 `torch.min(ts)`가 **윈도우 원점**이라 샘플 시작 시각을 모르면 그래프를 만들 수도 없다; EFGCN은 아예 `t*_i = ⌊β·t_i/T⌋`라고 쓴다. 즉 "격자를 안 쓴다"는 방법들도 전부 전역 윈도우에 묶여 있다. 유일한 공개 반론인 EvGNN도 상수 하나를 둘로 늘렸을 뿐 `r_t`는 여전히 절대 시간.
- **DAGr(Nature 2024)가 우리 논지를 대신 증명해 준다.** (i) 데이터로더가 매 샘플을 재기준화해 최신 이벤트를 `t=1.0`에 둔다 → **정지 픽셀의 "지금"이 화면 어딘가 다른 픽셀이 마지막으로 발화한 시각으로 정해진다.** 우리가 말한 "정의되지 않은 시간"의 실물. (ii) ablation에서 **1층에서 시간축 전체를 pooling(`g_t=1`)하면 +10.6 mAP** — 최고 성능 설정이 시간 좌표를 파괴하는 설정이다.
- **부분순서(partial order)도 여전히 공백.** 소위 "causal" DAG들은 **전순서에서 간선을 지워** 부분순서를 만든다(DAGr 조건: `||·||_∞ < R **and** t_i < t_j` — 이 비교 자체가 공유 수직선을 전제). PEPNet은 반대로 못을 박는다: *"grouping·sampling의 모든 점 순서는 타임스탬프 T를 엄격히 따른다."* 순열불변성을 일부러 버린 것.
- **아깝게 놓친 선행 2건(양날).** ① SITS(2019)는 rank라서 이미 단조불변인데 저자들이 몰랐다. ② **Spiking Patches**의 토크나이저에는 **타임스탬프 비교가 아예 없고** 패치끼리 비교 불가 — 진짜 곱순서(product order)인데 이름을 안 붙였고, 곧바로 절대 `t`를 찍고 1/50000로 스케일, 3-way sinusoidal PE, 50ms 윈도우로 평가하며 전순서를 되돌린다. "도달 가능하다"는 증거이자 "이미 도달했다"는 반박거리.
- **선점 위험(일정 리스크):** **Neural Events** (2606.19835, 2026-06, Scaramuzza 랩) — 학습된 코드가 **바뀔 때만** 토큰을 낸다. 시간 기반이 아니라 **변화 기반 트리거**. 좌표를 정의하지도, 불변성을 주장하지도, 프레임을 건드리지도 않지만 `τ`까지 한 편 거리다. **좌표와 정리를 먼저 빨리 내고 대규모 벤치마크는 뒤로 미루는 편이 낫다.** 매달 arXiv 확인.
- **새 경쟁자:** **SECNet** (ICML 2026 Oral) — 좌표가 아니라 **특징 거리**로 이웃을 만들고 `β`를 **학습 가능**하게 한다. 가장 근접한 탈출 시도. 그래도 학습된 `β`도 결국 픽셀↔초 환산 스칼라 하나이고 절대 `t`가 입력 특징으로 남아 불변성은 없다.
- **인용 위생:** ICCV 2021 방법은 **SlideGCN**이 정식 명칭(EvS-S는 비교표 라벨). **EvT는 그래프/포인트 계열이 아님**(Δt 24/48ms, B=2~3 bin, PE는 2D 전용) → 반례로 인용할 것. HUGNet의 β는 EvGNN 경유 2차 정보이므로 원문 확인 후 인용. DAGr는 Nature판이 유료라 arXiv 쌍둥이 + 공개 저장소를 인용.
- **비용:** Stage 0는 다운로드 0, 하루면 P3·P5 결판. 코어 약 135 GPU-h(6일), 9GB 이내, Docker.
- **자체 점수:** 독창성 7, 실현가능성 8, 리뷰어 방어력 6, 점진성 3(낮을수록 좋음).
- **판정: 조건부 추진.** 기둥이 둘이고 각각 하루짜리 판정 실험(P3, P6)이 있다. **다른 작업 전에 Stage 0·0b부터.** 둘 다 실패하면 미련 없이 버릴 것.
