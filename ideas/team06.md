# Frames Are Not Samples: The Exposure Gap in Event–Frame Consistency, and the Invariant That Survives It

## One-sentence thesis

A captured frame is a log-mean-exp functional of the intra-exposure log-intensity trajectory, not a point sample
of it, so the point-sample form of the event–frame identity carries a deterministic bias equal to half the
intra-exposure variance of log-intensity — worth 0.5–2.6 contrast thresholds, enough to collapse the standard
per-pixel contrast-threshold calibration to zero on a *perfect* sensor — and the fix is to supervise the exposure
functional of a trajectory whose *shape* is a threshold-invariant normalised event profile and whose *amplitude*
is identified by the blur itself.

## The assumption we kill

**The assumption.** The bridge between the two modalities is built from a pair of statements:

```
(E1)  event generation:  L(t) − L(t_ref) = c · E(t_ref → t)         [c constant, known, ideal]
(E2)  frame ≡ sample:    log B_k = L(t_k)                            [t_k = exposure midpoint]
```

whose composition gives the working identity `log B_{k+1} − log B_k = c·E(t_k → t_{k+1})`.

**Precision about who assumes what — this is the part we verified hardest, and it narrows the claim.** EDI and
mEDI do **not** make (E2). mEDI's Eq. (5) already reads `B̃ = L̃(f) + J̃(c)` with
`J(c) = (1/T)∫_{f−T/2}^{f+T/2} exp(c·E(t))dt` — the exact exposure functional. Time Lens and Time Lens++ carry no
photometric log identity at all (Time Lens++ never mentions a contrast threshold); TimeReplayer uses image-space
cycle consistency; E2VID and ET-Net are event-only; and EVDI, GEM, eSL-Net, LEDVDI, UEVD and the 2025
exposure-agnostic line all keep the exposure integral. **So "every method assumes (E2)" would be false, and we do
not write it.**

What is true, and is enough:

* The exact term exists but is **never expanded, named, bounded, or measured.** No paper in the event–frame
  literature states its second-order form. A full-text search over 44 downloaded PDFs returns zero hits for
  "Jensen", "log of the average", "average of the log".
* It is lost **in three distinguishable ways**, and naming them is what makes the claim precise:
  **(a) linear substitution** — EventAid (TPAMI) states EDI canonically as `L_clear = L_blur − c·∫∫E`, replacing
  the log-mean-exp by `c·mean(E)`.
  **(b) captured-frame anchoring with point samples** — REFID (CVPR 2023) Eq. (2) writes
  `Î_τ = I₀·exp(c∫_{t₀}^{t}p)` on the *captured* key frames, and itself observes that "because of the finite
  exposure times of the two frames, the timestamps t₀ and t₁ should be replaced by time ranges", then attributes
  the residual to "sensor noise and the varying contrast threshold"; TimeLens-XL (ECCV 2024) Eq. (2) writes
  `I_{t+Δt} ≈ I_t·exp(∫c·E)` — attributing it to "many works" — and discards it as "sub-optimal" **because the
  formation model is non-differentiable**, not because of exposure; AE2VID (CVPR 2026) Eq. (2) uses the same form;
  Wang et al. (ACRA 2019) Eq. (6) equates `Σc_pσ_i` to `ΔL_p` from two captured APS frames and uses it to
  **estimate the per-pixel threshold**, acknowledging that those frames "could be blurry in fast-motion" without
  correcting; Scheerlinck et al. (ACCV 2018) demote the exposure average to a zero-order-hold sample before
  taking its log.
  **(c) wholesale replacement by a network** — the entire Time Lens family drops the photometric identity
  altogether.
  **The exception, which we must state prominently: EVDI (CVPR 2022) gets it right.** Its Eq. (19)–(20) difference
  two *captured blurry frames* while preserving `Ẽ = log[(1/T)∫exp(cE)dt]`. Exactly one method in the lineage
  keeps the correct two-frame form, and no one has measured what the others lose by not keeping it.
* **A structural gap confirmed by two independent sweeps:** the identity is used everywhere as a *physical
  justification sentence*, but **never as an actual training loss in frame interpolation** — so no one has ever
  been forced to confront its bias. Where `c` is troublesome, the field removes it by *gauge fixing* rather than
  correcting the operator: EVDI min/max-normalises "to avoid the estimation of threshold `c`", GEM cancels it in a
  ratio, SSL-E2VID fixes `C = 1` with percentile normalisation, and E2VID deliberately randomises
  `C ~ N(0.18, 0.03)` in training data specifically, in its own words, to prevent "the network from learning to
  naively integrate events". And **no differentiable method exists that estimates `c` per sequence from paired
  events and frames** — the closest are a non-differentiable events/pixel/s proxy (E2VID+) and the least squares
  of Wang et al., which is the very estimator our P7 shows to be exposure-biased.

* The one place the effect was noticed, it was dismissed without evidence. Scheerlinck, Barnes & Mahony
  (ACCV 2018), §3.1, verbatim: *"Note that converting the zero-hold signal into the log domain is not the same as
  integrating the log intensity of the irradiance over the shutter time. We believe the difference will be
  insignificant in the scenarios considered and we do not consider this further in the present paper."* That belief
  has stood untested for eight years. **This paper tests it.**

**What breaks.** Exactly, with no approximation:

```
    B_k = (1/T) ∫_{W_k} exp(L(t)) dt = exp(L_ref) · (1/T) ∫_{W_k} exp(c·E(t)) dt
⇒   log B_k = L(t_k) + J_k,     J_k := LME_{W_k}(c·E) − c·E(t_k) ≥ 0
    where  LME_W(f) := log (1/|W|) ∫_W exp(f(t)) dt
```

`J_k` is the **exposure gap** — the same object as mEDI's `J̃(c)`, which is why we keep the symbol. To second
order `J_k = ½·Var_{W_k}(L) + O(κ₃)`: **the bias of the point-sample identity is half the intra-exposure variance
of log-intensity**, exactly zero iff the temporal support is a point, and growing with
(speed × log-gradient × exposure)². Verified numerically: for a soft step edge the measured `log B − L(t_mid)`
equals `Var_W(L)/2` to four significant figures across three decades of blur (s = 0.05–64 px), follows `(ωT)²/24`
in the small-blur limit (ratio 1.000 at s ≤ 0.2 px), and saturates at `log cosh(Δ/2) ≈ Δ²/8` for a step of
log-contrast Δ.

**The kill is not "sensors are noisy."** `J_k` exists for a *perfect* sensor: exact threshold, no refractory
period, no leak, no shot noise, infinite bandwidth. It is a property of the *observation operator*, not of the
silicon. Sensor non-idealities add a second, separable family of structured terms on top of it.

**Not to be confused with the other Jensen term in this literature.** AKF (Wang, Ng, Scheerlinck, Mahony,
ICCV 2021) notes that "the log function is not symmetric and mapping the noise from I_p will bias the log
intensity", with a Taylor correction `R̄_p/(2(I_p+I₀)²)`. That is a convexity bias over the **noise**
distribution. Ours is over the **exposure window**. They are orthogonal axes and we state the distinction
explicitly, because a reviewer who has read AKF will otherwise assume we are re-deriving it.

**Corollary we must attribute rather than claim.** That the *effective* contrast threshold moves with motion is
already published: Delbrück, Graca & Paluch (CVPRW 2021) give the refractory rate law `r = 1/(T₀ + Δ_refr)` and
validate it with a physical rotating-dot speed sweep; Gallego et al. (TPAMI 2020) state outright that "the larger
the refractory period the fewer events are produced by fast moving objects"; Scheerlinck et al. (ACCV 2018) and
Wang et al. (ACRA 2019) both assert the threshold varies "with illumination, event-rate and other factors", citing
Brandli et al. (ISCAS 2014); Robust e-NeRF (ICCV 2023) benchmarks a K× speed-up as a K× scaling of effective
refractory and threshold variance. We reproduce it in simulation (0.26 → 0.37 over 32 px of blur under a 300 µs
refractory) and cite all of it. **It matters for our framing in one favourable way:** the field's entire diagnostic
vocabulary for this residual is *sensor-side*, which is exactly why the *frame-side* operator went unexamined —
and, as §P7 shows, part of the reported speed-dependence is manufactured by the calibration procedure itself.

## The failure phenomenon

**Measurement.** Per pixel, per frame pair, compute the residual actually incurred by the working identity

```
    R = c·(E(t_{k+1}) − E(t_k))  −  (log B_{k+1} − log B_k)
```

and regress it against a **zero-free-parameter predictor computable from the events alone**

```
    P = [c·E(t_{k+1}) − LME_{W_{k+1}}(c·E)] − [c·E(t_k) − LME_{W_k}(c·E)]
```

`P` needs no ground truth, no intensity, and no unknown offset — the reference level cancels inside every LME. It
needs only the event stream and the two exposure windows. If the residual were sensor noise, the regression
`R ~ P` must return slope 0 and R² ≈ 0.

**Independent variable.** Blur length `s = |v|·T_exp` in pixels — the single scalar quantifying temporal-support
mismatch. Swept two ways: exposure duty at fixed motion, and motion at fixed exposure. The two sweeps must
collapse onto one curve; that collapse is the cleanest available evidence that the driver is *support*, not motion.
Secondary variable: which sensor non-ideality is switched on.

**Axes of the one plot.** x = `P` (event-predicted exposure gap, log units); y = `R` (measured residual, log
units); one scatter cloud per sensor configuration against the unit-slope line; inset = recovered slope and R² vs
`s`. Two nulls overlaid as flat references: residual vs a random regressor (noise hypothesis) and residual vs
`|ΔE|` (threshold-error hypothesis).

**Expected curve and quantitative prediction.** Monte-Carlo over 900 random moving-edge scenes per configuration
(speed 100–3200 px/s, log-contrast 0.2–1.4, edge width 0.5–3 px, 40 % of scenes carrying a second opposite-sign
edge so trajectories are non-monotone), `c = 0.2`, `T_exp = 10 ms`, frame period 10 ms:

| sensor configuration | slope of R~P | R² | Var(R) removed | fingerprint after correction |
|---|---|---|---|---|
| **ideal (all non-idealities OFF)** | **+0.955** | **0.779** | **77.8 %** | flat; remainder is ±c/2 event quantisation |
| per-pixel threshold bias ε = +0.10 | +0.928 | 0.634 | 63.0 % | remainder ∝ \|ΔE\|, slope −0.016 (predicted −εc = −0.020) |
| refractory 300 µs | +0.779 | 0.283 | 26.1 % | strongest \|ΔE\| coupling (R² = 0.19): a rate-dependent threshold |
| leak 20 ev/s | +0.978 | 0.780 | 77.9 % | motion-independent **intercept** +0.034 |
| shot noise 300 ev/s | +1.313 | 0.369 | 34.8 % | Var(R) inflated 2.7×; genuinely noise-like |
| *noise null (random regressor)* | +0.005 | **0.0015** | — | — |

**Robustness of the headline (independent check, three scene models × three seeds, ideal sensor throughout).**
The table above uses an adversarial mix in which 40 % of scenes carry a second opposite-sign edge, so trajectories
are non-monotone; that is the *hardest* case and gives the *lowest* number. Re-running on cleaner and on more
realistic scenes:

| scene model | slope (3 seeds) | R² | Var(R) removed | std(R) in contrast thresholds |
|---|---|---|---|---|
| mixed edges, 40 % non-monotone (headline) | +0.955 | 0.779 | 77.8 % | 0.71 |
| single soft edges | +0.980 … +0.996 | 0.875–0.879 | **87.5–87.9 %** | 0.64–0.66 |
| **band-limited translating texture** (the realistic case) | +0.997 … +0.999 | 0.991–0.993 | **99.1–99.3 %** | **2.61–2.65** |
| accelerating edges (non-constant velocity) | +0.922 … +0.941 | 0.827–0.837 | 82.3–83.1 % | 0.53–0.55 |

Two things follow. The slope is within 8 % of unity in every configuration with no fitted physics, and **on
textured content — which is what natural video is — the residual is 2.6 contrast thresholds and 99 % of it is the
exposure operator.** Texture raises intra-exposure variance, and `J = ½Var_W(L)`, so the effect is largest exactly
where the field's benchmarks live.

Headline predictions, each falsifiable:

1. **P1.** With a physically perfect sensor, ≥ 70 % of the variance of the event–frame consistency residual is
   removed by a one-line, parameter-free `LME` correction. Measured 77.8 %; noise null 0.15 %.
2. **P2.** The residual's standard deviation is **0.53–0.71 contrast thresholds on edge scenes and 2.6 on
   textured scenes** — the identity is typically wrong by one to several whole events, not by a fraction of one.
3. **P3.** The residual's *global signed mean is ≈ 0* while its spatial pattern is an antisymmetric **dipole
   straddling the motion trail**, peaking at 1.11 c for a 2× contrast edge at 16 px blur. This is why it has
   passed every zero-mean noise check ever run on it: the mean is the wrong statistic, and averaging along the
   trail — the natural thing to do — cancels it exactly.
4. **P4.** Methods trained with the uncorrected consistency term inherit a **motion-conditioned contrast bias**.
   Because `J ≥ 0` always, the frame reads systematically *brighter in the log domain* than the true mid-exposure
   log-intensity at swept pixels, so reconstructions are biased toward reduced contrast amplitude along motion
   trails, growing as `(vT)²` and saturating at `Δ²/8`. Predicted signature: a positive-biased band along the
   trail, and a *negative* slope of (predicted − GT) log-contrast against local blur length.
5. **P5.** Each non-ideality has a distinct fingerprint in the triple (variance removed, intercept, `|ΔE|` slope),
   so the toggle ablation is *identifying*, not merely descriptive.
6. **P6 — the bias is not absorbable by capacity.** Fitting a correction on slow motion (blur 1–6 px) and applying
   it to fast motion (16–32 px): a learned **constant** offset removes **0.0 %** of the fast-motion residual
   variance; a learned **linear model in generic event features** (`|ΔE|`, event-rate spread, bias) removes
   **51.0 %** and its RMSE degrades 0.059 → 0.105 across the support shift; the parameter-free `LME` correction
   removes **91.2 %** and degrades only 0.044 → 0.055. A network can memorise this bias inside its training
   support and cannot extrapolate it outside.
7. **P7 — the published contrast-threshold calibration is contaminated by the gap, and this is the sharpest
   consequence.** The standard recipe estimates `c` by least squares of `Δlog B = c·ΔE` over two *captured* frames
   (Wang et al., ACRA 2019, Eq. 6). Running that recipe on **a physically perfect sensor**, with `c_true = 0.200`:

   | blur s = vT (px) | 1 | 2 | 4 | 8 | 16 | 32 |
   |---|---|---|---|---|---|---|
   | published recipe `ĉ` | 0.189 | 0.162 | 0.130 | 0.049 | 0.018 | **−0.004** |
   | error | −5.5 % | −19.1 % | −34.9 % | −75.4 % | −91.2 % | **−101.8 %** |
   | support-aligned `ĉ` | 0.204 | 0.210 | 0.206 | 0.202 | 0.198 | 0.196 |

   The calibrated threshold collapses by an order of magnitude and changes sign, purely as a function of how fast
   the calibration sequence moved — **with no sensor non-ideality present at all** — while the support-aligned
   estimator stays within ±5 % of truth at every blur level. We do not claim that *all* the reported
   speed-dependence of the contrast threshold is this artefact; refractory dead-time genuinely destroys events, and
   note the two effects have **opposite signs** (refractory inflates the effective threshold, the exposure gap
   deflates the calibrated one), which is itself a discriminating test. We claim that a component of it is a
   measurement artefact of the calibration procedure, that the component is large, and that it is removable in
   closed form.

**Why nobody has plotted this.** At a single pixel the sensor term is dominated by event quantisation (±c/2), so
the residual looks like noise and is discarded. The exposure term only becomes visible when the residual is
regressed against a *structural* predictor rather than averaged — and averaging is exactly the check the field
has been running.

## The reformulation

### Corrected forward model

Drop (E2). Model the per-pixel intra-window log-intensity **trajectory**, and two observation operators with
*different temporal supports*:

```
  latent:   L_p(t) = L_p^0 + a_p · φ_p(t),   t ∈ [t_k, t_{k+1}],   φ_p(t_k)=0, φ_p(t_{k+1})=1
  frame:    B_k = (1/T) ∫_{W_k} exp(L_p(t)) dt                     (support = exposure window W_k)
  events:   level-crossing sampling of (h ⊛ L_p) on a grid of spacing c_p,
            with dead time ρ after each event, leak rate λ, and an additive noise process
```

`h` is the photoreceptor low-pass, `c_p` the per-pixel threshold, `a_p := c_p·E_p(t_k → t_{k+1})` the total log
amplitude. The event stream determines the trajectory **only up to an affine map in the log domain**: the offset
`L_p^0` and the scale `a_p` are unobservable from events; the *shape* is observable.

### The invariant

```
  φ_p(t) := E_p(t_k → t) / E_p(t_k → t_{k+1})        — the normalised cumulative event profile
```

`φ` is invariant to (i) any per-pixel scaling of the contrast threshold, (ii) the absolute intensity level,
(iii) any global gain or exposure change, and (iv) the exposure gap itself — because `J` is a functional of the
trajectory's *values* while `φ` describes its *argument*. This is the quantity that survives support mismatch.

Verified sensitivity (400 random moving edges; drift measured as mean absolute quantile-time shift at 7 deciles):

| perturbation | drift of φ (% of window) | error in log-intensity from the same perturbation |
|---|---|---|
| threshold scale ε = 0.05 | 2.37 % | 0.039 log units (0.20 c) |
| ε = 0.10 | 3.26 % | 0.071 (0.36 c) |
| ε = 0.20 | 4.69 % | 0.127 (0.64 c) |
| ε = 0.40 | 6.00 % | 0.225 (1.12 c) |

Intensity error is **linear** in ε; φ's drift is quantisation-limited and grows only 2.5× for an 8× change in ε.
φ is first-order invariant to the threshold; intensity is not. Refractory period is the one non-ideality that
*does* warp φ (0.84 % at 50 µs → 3.29 % at 600 µs), because dead time is rate-dependent; this makes ρ the single
parameter the model must carry explicitly, and gives the sharpest ablation.

### Identification: blur is the signal, not only the nuisance

With `φ` known from events, two exposure windows give two equations in the two unknowns `(L_p^0, a_p)`:

```
  log B_k = L_p^0 + log M_k(a_p),         M_k(a) := (1/T) ∫_{W_k} exp(a·φ_p(t)) dt
  log(B_{k+1}/B_k) = G(a_p) := log M_{k+1}(a_p) − log M_k(a_p)
```

`G` is monotone in `a` with `dG/da = 0.86–0.91` at the true value in our tests, and inverting it recovers `a_p`
to **0.18–0.22 % relative error**. Since `a_p = c_p·E_p`, this **recovers the per-pixel contrast threshold from
the exposure integrals**: the blur everyone treats as the problem is what makes `c_p` identifiable, and the
conditioning *improves* as motion increases. No calibration rig, no assumed constant.

This is the point at which our work and the sensor-side literature meet productively rather than collide. That
literature has established *that* the effective threshold moves with rate and speed (§ above) and has responded
either by calibrating a per-pixel constant offline (Wang et al., ACRA 2019), by jointly estimating a global
refractory constant (Robust e-NeRF, ICCV 2023), or by rescaling the threshold per frame to fit the deblurred
data (Wang et al., *Asynchronous Linear Filter Architecture*, arXiv:2309.01159 — in substance, absorbing
rate-dependent event loss into an adjusted threshold as an engineering fix). What none of them has is an
*identifiability argument*: a statement of which quantities the two observation operators jointly determine, and
under what conditioning. `G` supplies it, and it says something counterintuitive — the harder the motion, the
better the threshold is determined.

### Objective (PACE — Profile–Amplitude Consistency for Events)

The network predicts, per pixel, a corrected profile `φ̂_p` (K = 8 knots, initialised from the raw event profile)
and an amplitude `â_p`; a small head predicts the global non-ideality scalars `(ρ, λ, σ_c)`.

```
L = Σ_k ‖ (1/M) Σ_{m=1..M} exp(L̂_p^0 + â_p·φ̂_p(t_m^{(k)})) − B_k ‖₁        (support-aligned data term)
  + λ₁ Σ_q | τ̂_q − τ_q^{events} |                                          (threshold-free profile term)
  + λ₂ Σ_{(i,j)} max(0, −sign(L_i−L_j)·(L̂_i−L̂_j) + m)                      (ordinal, monotone-invariant)
  + λ₃ ‖ρ̂ − ρ_prior‖² + …                                                  (non-ideality prior)
```

* Term 1 is the **corrected** photometric loss: quadrature over the exposure window (M = 16 Gauss–Legendre nodes)
  *inside* the exponential. It has no exposure gap by construction. This single change is the parameter-free fix
  and drops into any existing method.
* Term 2 is a 1-Wasserstein distance between predicted and observed normalised event-time measures, written as an
  L1 on quantile times `τ_q = φ^{-1}(q)`. Invariant to `c_p`, to `L^0`, and to any global gain.
* Term 3 is invariant to *any* monotone transform of intensity — gamma, tone curve, saturation — the weakest and
  most robust constraint available.

Training-free variant, usable immediately as a baseline fix: replace every `c·E(t_k)` in an existing consistency
term with `LME_{W_k}(c·E)`. One line.

## What existing methods cannot express

1. **Zero-net-event blur.** When log-intensity rises and falls within one exposure — a thin bar, a fan blade, a
   specular highlight sweeping past — the net event count is ≈ 0 while the excursion is large. In a bar-sweep
   Monte-Carlo, **24.6 % of active pixels** are zero-net-event (|net| ≤ 1, excursion ≥ 2 events), and on those the
   identity `Δlog I = c·E ≈ 0` mispredicts the frame by **1.62 contrast thresholds on average, 3.14 at the 90th
   percentile**. Any representation that summarises inter-frame events into a count image, a net-polarity map, or
   a voxel grid reduced to a `Δlog I` cannot represent that such a pixel was blurred at all: it predicts a sharp
   pixel and the error is charged to noise. `φ` represents it exactly — a non-monotone profile with identical
   endpoints.
2. **A motion-dependent threshold.** Representations that convert events to a fixed-scale tensor bake `c` in
   before the network sees the data. That the effective threshold moves with scene speed is established in the
   sensor literature (Delbrück et al. 2021; Gallego et al. 2020); the representational consequence — that a
   quantity varying 40 % with speed cannot be a preprocessing constant — is what has not been acted on.
3. **"Shape known, amplitude unknown."** Existing outputs are intensity maps: a single estimate fusing an
   observable quantity (timing) with an unobservable one (scale). There is no slot in the representation to say
   *I know when, not how much* — which is precisely the information content of an event stream.
4. **An observation that has a support.** Nothing in the standard formulation distinguishes "the frame constrains
   `L` at `t_k`" from "the frame constrains a log-mean-exp functional of `L` over `W_k`." A representation whose
   output space is *intensity at a time* cannot express a constraint that is a functional of a trajectory.

## Why this is not <closest work>

| Work (venue, year) | What it does | Why we differ |
|---|---|---|
| **EDI / mEDI** — Pan et al., *Bringing a Blurry Frame Alive at High Frame-Rate with an Event Camera* (CVPR 2019; arXiv:1903.06531 for mEDI) | Single-frame blur as an exposure integral; mEDI Eq. (5) is `B̃ = L̃(f) + J̃(c)` with `J(c) = (1/T)∫exp(c·E(t))dt` | **The exact term is already theirs, and we say so — we keep their symbol `J`.** What is unclaimed is its second-order form `J = ½Var_W(L)`, any bound or measurement of it, and the demonstration that the field drops it downstream. We are not correcting EDI; we are measuring what it costs when EDI's own term is discarded |
| **EVDI / Learnable Double Integral** — Zhang & Yu, *Unifying Motion Deblurring and Frame Interpolation with Events* (CVPR 2022, arXiv:2203.12178; ext. arXiv:2509.08260) | Eq. (9) `LDI(E) ≈ (1/T)∫₀^T exp(c∫₀^t e(s)ds)dt` learns the exposure functional; **Eq. (19)–(20) is the exposure-correct two-frame loss**: it differences two *captured blurry frames* while preserving `Ẽ = log[(1/T)∫exp(cE)dt]`; sidesteps `c` by min/max normalisation "to avoid the estimation of threshold c" | **The closest work by a wide margin, and the one method in the lineage that gets the two-frame form right — we say so first, not in a footnote.** Our delta is therefore not the operator but everything around it: naming and bounding the bias (`J = ½Var_W(L)`), *measuring* what the methods that drop it lose (0.5–2.6 contrast thresholds; 78–99 % of the residual), propagating it into contrast-threshold estimation (P7), replacing gauge-fixing-by-normalisation with an explicit per-pixel invariant `φ`, and showing a learned functional does not extrapolate across the support axis while the closed form does (P6: 51 % vs 91 %) |
| **REFID** — Sun et al., *Event-Based Frame Interpolation with Ad-hoc Deblurring* (CVPR 2023, arXiv:2301.05191) | Eq. (2) anchors `Î_τ = I₀·exp(c∫p)` on the **captured** key frames; notes that finite exposure means `t₀,t₁` "should be replaced by time ranges" | It sees the problem and routes around it architecturally, then attributes the leftover error to "sensor noise and the varying contrast threshold" — the exact misattribution we measure. We quantify what that leftover is (0.5–2.6 contrast thresholds) and show 78–99 % of it is the exposure operator |
| **E-CIR** — Song, Huang, Bajaj, *Event-Enhanced Continuous Intensity Recovery* (CVPR 2022, arXiv:2203.01935) | Eq. (4): per-pixel degree-n **polynomial** `L_xy(t) = α₀+α₁t+…+α_n tⁿ`, with event timestamps as derivative constraints | Predicts an *intensity* trajectory; its coefficients carry the threshold, so they are not invariant to `c_p`. We predict a normalised profile (invariant) plus a separately identified amplitude, which is a different factorisation of the same object |
| **LEDVDI** — Lin et al., *Learning Event-Driven Video Deblurring and Interpolation* (ECCV 2020; no arXiv preprint) | Handles a per-event threshold described as spatially **and temporally** variant, via learned dynamic filters | The closest prior acknowledgement that `c` is not a constant, answered with capacity. We give the temporal variation a source — part of it is the calibration artefact of P7, present with a perfect sensor — and an identifiability argument instead of a filter bank |
| **Continuous-time Intensity Estimation** — Scheerlinck, Barnes, Mahony (ACCV 2018, arXiv:1811.00386) | Complementary filter; §3.1 explicitly notes that log-of-exposure-average ≠ exposure-average-of-log and states "we believe the difference will be insignificant… we do not consider this further" | **The single most important citation for this paper.** The effect was seen, judged negligible by assertion, and never revisited in eight years. Our contribution is in the first instance simply to test that belief — and it is false by 0.5–2.6 contrast thresholds |
| **AKF** — Wang, Ng, Scheerlinck, Mahony (ICCV 2021, arXiv:2012.05590) | Notes "the log function is not symmetric and mapping the noise from I_p will bias the log intensity", with Taylor term `R̄_p/(2(I_p+I₀)²)` | A convexity bias over the **noise** distribution; ours is over the **exposure window**. Orthogonal, and we flag it explicitly so readers do not conflate the two |
| **EventAid** — Duan et al. (TPAMI, arXiv:2312.08220) | Benchmark; §2.1 states EDI canonically as `L_clear = L_blur − c·∫∫E` | A TPAMI-level benchmark publishing the first-order, point-sample form as *the* statement of EDI. Evidence that the term is dropped in the field's reference material, not just in individual methods |
| **Per-pixel biased contrast-threshold calibration** — Wang et al. (ACRA 2019, arXiv:2012.09378) | Eq. (6) equates `Σ c_pσ_i + b_p|σ_i|` to `ΔL_p` from two captured APS frames; measures `c ∈ [0,0.4]`, 10–15 % effective variation; acknowledges APS frames "could be blurry in fast-motion" | **This is where our result bites hardest (P7).** Their estimator, run on a *perfect* sensor, collapses from 0.189 to −0.004 as blur grows. We do not claim their sensor findings are wrong; we claim their procedure has a motion-dependent bias with a closed-form correction |
| **Asynchronous Linear Filter Architecture** — Wang, Ng, Scheerlinck, Mahony (arXiv:2309.01159) | "Refractory period noise" covariance term; rescales the contrast threshold per frame to "stretch or shrink the interpolation to fit the deblurred frame data" | In substance *absorbs* the residual into an adjusted threshold — the right instinct as an engineering fix. We give the frame-side term a closed form, show it survives a perfect sensor, and supply the identifiability argument the per-frame rescaling lacks |
| **Feedback control of event cameras** — Delbrück, Graca, Paluch (CVPRW 2021); **Robust e-NeRF** — Low & Lee (ICCV 2023) | The refractory rate law `r = 1/(T₀+Δ_refr)` with a physical speed sweep; and a σ_C × τ × speed factorial reporting 5.84×/11.37× event sparsity at τ = 8/25 ms | The strongest sensor-side pre-emption of our corollary, cited as such. Both explain why *events* are lost at speed; neither examines the frame-side operator, and both mechanisms are absent when the sensor is ideal — where our headline residual lives. Robust e-NeRF additionally *assumes* the threshold constant, which P7 shows is unsafe when it was calibrated from exposed frames |
| **TimeLens-XL** (ECCV 2024), **AE2VID** (CVPR 2026) | Both write the instantaneous identity `I_{t+Δt} ≈ I_t·exp(∫c·E)`; TimeLens-XL attributes it to "many works" and then discards it as "sub-optimal" **because the image formation model is non-differentiable** | The clearest evidence of the gap we occupy: the identity is rejected for the *wrong reason*. Nobody rejects it because the frame is not an instantaneous sample, and nobody has measured the resulting bias. AE2VID is additionally instructive — it avoids captured frames entirely because "none of the reference irradiance I(r,t₀) is known", which is our identifiability question asked and then routed around |
| **Gauge-fixing family** — EVDI (min/max normalisation), GEM (ratio cancellation), SSL-E2VID (`C = 1` + percentile normalisation), E2VID (`C ~ N(0.18,0.03)` randomised in training data, explicitly to stop "the network from learning to naively integrate events") | Remove the contrast threshold by fixing a gauge or randomising it away, rather than estimating or correcting it | **The nearest existing relatives of our invariant, and the honest comparison point.** All of these are *global* or *per-image* normalisations that discard the threshold along with the amplitude. `φ` is a *per-pixel temporal* normalisation that discards only the amplitude and keeps the shape — and the amplitude is then recovered, not discarded, from the exposure functionals. That two independent sweeps found **no differentiable per-sequence estimator of `c` from paired events and frames** is what makes the identification result a contribution rather than a re-derivation |
| **Time Lens** (CVPR 2021), **Time Lens++** (CVPR 2022), **TimeReplayer**, **E2VID / ET-Net** | Warp-and-synthesise interpolation; image-space cycle consistency; event-only reconstruction | **Negative controls, and we present them as such.** Verified: these carry no photometric log identity anchored on captured frames at all (Time Lens++ never mentions a contrast threshold; TimeReplayer's loss is `‖Î_t0−I_t0‖₁+‖Î_t1−I_t1‖₁`). Any claim that "every method assumes this" would be false, and we do not make it. Their existence bounds the scope of our indictment honestly |
| **v2e** (CVPRW 2021), **DVS-Voltmeter** (ECCV 2022), **ESIM** (CoRL 2018), **ADV2E**, **SENPI**, **FracEvent**, **IEBCS** | Sensor simulators with unequal coverage (verified): v2e models threshold scatter, refractory, leak, shot noise, intensity-dependent bandwidth; DVS-Voltmeter is a Brownian-drift model with **no refractory**; **ESIM models only a Gaussian threshold**, its paper stating that bandwidth is open and refractory loss at speed "is not modelled by our implementation" | Our *instruments*, not competitors. In every one the threshold is a static per-pixel constant and rate effects are emergent from low-pass plus dead time; none models the frame's exposure operator, because none is asking about frames. Their coverage gaps also constrain our cross-checks, which we state rather than paper over |
| **Contrast maximisation** — Gallego et al. (CVPR 2018) and successors | Threshold-free objective: maximise sharpness of warped event images | The one genuinely threshold-invariant family in the field — but invariance is a *by-product* of using event geometry only, and it discards frames entirely. We keep the frame and make invariance the design principle of the *cross-modal* term |

## Experimental plan

**Stage 0 — the controlled measurement (simulation; the paper's spine).**
Source: **GoPro `GOPRO_Large_all`, 35.3 GB**, CC BY 4.0, no registration (HF mirror `snah/GOPRO_Large`). It is
**already 240 fps**, so frame upsampling is skipped entirely — the single decision that keeps this study cheap
(re-running SuperSloMo per non-ideality setting would cost ≈ 40 GPU-h *per setting*; the DVS stage runs *after*
upsampling, so upsampling is cacheable and, here, unnecessary). Synthesise frames as *linear-domain* exposure
averages at duty ∈ {0.125, 0.25, 0.5, 1.0}; synthesise events with **v2e** at fixed nominal `c`.
Controlled variable: blur length `s = |v|·T_exp`, swept via duty at fixed motion and via motion at fixed duty; the
two sweeps must collapse.
**Non-ideality toggle (only simulation permits this).** **v2e is the only simulator with the full toggle set**,
and this is a verified constraint, not a preference: `--sigma_thres` (per-pixel threshold scatter; the paper uses
σ_θ = 0.03), `--refractory_period` (default 0.5 ms), `--leak_rate_hz`, `--shot_noise_rate_hz`, `--cutoff_hz`
(photoreceptor bandwidth, modelled as increasing monotonically with intensity), `--photoreceptor_noise`,
`--leak_jitter_fraction`, `--noise_rate_cov_decades`, `--pos_thres/--neg_thres`, and the `clean`/`noisy` presets.
Run one at a time from an all-off configuration. **The all-off run is the headline.**
*Honest limits of the cross-checks:* **ESIM models only a Gaussian contrast threshold** — its own paper states
that bandwidth is an open question and that refractory-induced event loss at high speed "is not modelled by our
implementation" — so it cannot serve as a refractory cross-check. **DVS-Voltmeter has no refractory period
either** (its conclusion names refractory as future work); it is a *stochastic-process* noise model with a
different formalism, so it cross-checks the shot-noise/leak axis only, which is still worth having because it is
independently derived. For an independent refractory cross-check the candidates are **IEBCS/ICNS**
(second-order low-pass, explicit refractory, and uniquely an arbiter-congestion model) and **SENPI**
(arXiv:2503.09754, a differentiable PyTorch digital twin with per-pixel maps for refractory, hot pixels, shot,
dark and leak noise, latency and contrast deviation). `esim_py` (pure C++/pybind11, no CUDA) is the CPU-only
fallback when the shared GPU is contended.
*Cost: 3–6 GPU-h across six settings with upsampling disabled; < 2 GB VRAM. Disk: budget ~200 GB for simulated
event output (one setting of GoPro raw events is ≈ 28 GB).*

**Stage 1 — real-data confirmation.**
**DSEC is the anchor, and this is a change of plan forced by verification:** DSEC ships
`image_exposure_timestamps_left/right.txt` per sequence and is **the only public event–frame dataset with real
per-frame exposure intervals**. That makes the parameter-free regression `R ~ P` runnable on real data with *no
ground truth at all* — only events, two frames, and the true exposure windows. DSEC is fully à-la-carte
(e.g. `interlaken_00_c`: `events_left.zip` 816 MB + `images_rectified_left.zip` 1.2 GB), so a handful of sequences
is a few GB out of 445 GB total.
Secondary real sets: **REBlur** (0.66 GB with SCER, 0.47 GB raw events; direct ETH HTTP, no form — the smallest
usable real blur+event set in existence), **HS-ERGB** (2.61 GB via the verified HuggingFace mirror
`RuixuanJiang/Low_Level_Datasets`), and **HighREV**, the NTIRE 2025/2026 event-deblurring challenge dataset, which
is becoming the field's expected high-resolution benchmark.
*Availability finding, verified:* **BS-ERGB is currently unobtainable** — it belongs to **Time Lens++ (CVPR 2022)**,
not to EVDI, and both `rpg.ifi.uzh.ch/timelens++download.html` and the Time Lens download page now render
navigation only, with no links or forms, and no mirror exists. We therefore do not build any claim on it and say
so in the paper. GoPro alone suffices for Stage 0, so this constrains breadth, not the core result.

**Stage 2 — indictment of published baselines.**
Inference only, on checkpoints verified live: **EFNet** (~8.5 M params; GoPro + REBlur weights; installs with
`setup.py develop --no_cuda_ext`, and its `requirements.txt` carries *no* torch pin), **REFID** (63.8 MB, ten
checkpoints hosted as **GitHub release assets** — the only rot-proof hosting in this field, with GoPro and
HighREV weights), **EVDI** (pure PyTorch, GoPro/HQF/RBE weights), **E2VID** (40.9 MB, plain HTTP, the easiest
thing to run), **ELEDNet** (ECCV 2024, weights live), and **EDI** as the analytic control — an optimisation, not a
learned model, hence immune to the toolchain problem entirely.
*Blackwell (sm_120) reality check:* the decisive question is not the README's torch pin but whether a repo compiles
custom CUDA. EFNet/REFID/EVDI/E2VID/ELEDNet do not, and their pins are floors, not ceilings. **GEM** (DCNv2) and
**CBMNet** (arXiv:2502.13716) (custom correlation kernel) do, and are deprioritised. Docker with the nvidia
runtime is already
available on this host; base image CUDA 12.8 + torch 2.7 + py3.11. Repos that will not port fall back to CPU
inference, which is slow but sufficient for a bias measurement over a few hundred frames.

**Stage 2b — the calibration experiment (new, and the cheapest high-value result in the plan).**
Re-run the published per-pixel threshold estimator (least squares of `Δlog B = c·ΔE`, Wang et al. ACRA 2019
Eq. 6) and our support-aligned estimator side by side, on (i) simulated sequences with an **ideal** sensor swept
over blur length — where the ground-truth `c` is known exactly and the published estimator is predicted to
collapse from 0.189 to −0.004 while ours holds 0.196–0.210 — and (ii) real DSEC sequences binned by ego-motion
magnitude, where the prediction is that the two estimators *diverge* as a function of speed, with the published
one trending down and the refractory-driven effect trending up. Because the two mechanisms have opposite signs,
this is a genuinely discriminating experiment, not a confirmation exercise. *Cost: CPU-only, ≈ 2 h.*

**Control that must be run and reported: EVDI.** EVDI's Eq. (19)–(20) is the exposure-correct two-frame loss, so
it is the *positive control* for our whole thesis: it should show markedly less motion-conditioned contrast bias
(MCB) than REFID, EFNet or an EDI restated in the linear form. If EVDI does **not** separate from the others, our
causal story is wrong and we must say so — this is the experiment most able to falsify the paper, and we run it
early rather than last.

**Stage 3 — the fix.**
(a) *Training-free:* substitute `LME_W(cE)` for `c·E(t_k)` in EDI and in each baseline's consistency term at
inference; report PSNR/SSIM and, more importantly, the change in motion-conditioned bias. Zero training cost.
(b) *Trained:* PACE-small, ≈ 8–15 M params, on REBlur or a HighREV subset, 128–192² crops, batch 8, AMP,
~50 k iterations.

**Metrics.**

* Standard: PSNR / SSIM / LPIPS on deblurring and ×8 interpolation; HighREV for the community-expected number.
* **EGR — Exposure-Gap Ratio**: `|J|/c`, the exposure gap in units of contrast thresholds, reported as a
  per-dataset distribution. It tells a reader in one number how wrong the identity is on their data.
* **SFR — Structured Fraction of the Residual**: fraction of `Var(R)` removed by the parameter-free `LME`
  correction. Predicted ≥ 0.70 with an ideal sensor; a noise hypothesis predicts 0.
* **TWD — Time-Warp Distance**: mean absolute quantile-time error between predicted and GT normalised profiles,
  in % of the window. Threshold-free, so a method can be scored even when its intensity scale is wrong.
* **MCB — Motion-Conditioned Contrast Bias**: slope of (predicted − GT) log-contrast regressed on local blur
  length `s`. Prediction: consistency-trained baselines have a significantly negative slope; PACE ≈ 0. This is
  the number that converts a diagnosis into an indictment.
* **ZNE-recall**: reconstruction accuracy restricted to zero-net-event pixels (|net E| ≤ 1, excursion ≥ 2).

**Ablations.** (i) non-ideality toggle, one at a time from all-off, in both v2e and DVS-Voltmeter; (ii) `LME`
correction on/off in the loss; (iii) profile term vs ordinal term vs both; (iv) `a_p` from two-window
identification vs `a_p` from an assumed global `c`; (v) K (profile knots) ∈ {2, 4, 8, 16} — **K = 2 collapses PACE
back to the standard identity and must reproduce the baseline's bias**, which is the internal consistency check;
(vi) quadrature nodes M ∈ {1, 4, 16, 64}, where M = 1 is again the uncorrected identity.

**GPU budget, honestly stated.** Stage 0 ≈ 3–6 h (mostly CPU, < 2 GB VRAM, given upsampling is disabled).
Stage 1 ≈ 6 h. Stage 2 ≈ 5–15 h across five checkpoints × six event variants. Stage 3(a) ≈ 2 h.
Stage 3(b) ≈ 4–8 h per run × 3 runs. **Core measurement (Stages 0–2) ≈ 1–2 days and is already a complete
publishable contribution.** With the trained model, hyperparameter search and the usual failed runs, the realistic
total is **70–120 GPU-hours**, i.e. 1–2 weeks on a card shared at ~8–12 usable hours/day. **VRAM is not the binding
constraint anywhere** — EFNet/REFID inference at 720p is 4–8 GB, PACE training at 192² batch 8 is 6–9 GB. Wall-clock
on a contended GPU is the constraint.

## Risks

**Death 1 — "This residual is already known and is attributed to sensor noise / threshold mismatch."**
This is the risk we spent the most verification effort on, and the honest answer is: *the sensor half is
thoroughly known, the frame half appears not to be.* Established and **not** claimed by us: threshold scatter
σ ≈ 2.5–4 % across pixels (Lichtsteiner et al. 2008; Posch & Matolin 2011); threshold dependence on illumination
and temperature (Nozaki & Delbrück 2017); light-dependent photoreceptor bandwidth low-passing fast transients
(Gallego et al., TPAMI 2020; modelled by v2e, IEBCS, ADV2E); refractory dead-time discarding brightness change
with the rate law `r = 1/(T₀+Δ_refr)`, measured against a physical speed sweep (Delbrück et al., CVPRW 2021);
"the larger the refractory period the fewer events are produced by fast moving objects" (TPAMI 2020, stated
outright); "the threshold varies with illumination, event-rate and other factors" (Scheerlinck et al., ACCV 2018;
Wang et al., ACRA 2019, both citing Brandli et al., ISCAS 2014); and speed × refractory × threshold-variance
benchmarked as a K× scaling (Robust e-NeRF, ICCV 2023). We cite all of it and claim none of it.
What two independent literature sweeps could not find — including a full-text search over 44 downloaded PDFs
returning zero hits for "Jensen", "log of the average" and "average of the log" — is any statement of the exposure
gap's second-order form `J = ½Var_W(L)`, any bound or measurement of it, or any calibrated curve of the
integration residual against ground truth as a function of speed. The one recorded observation of the effect is
Scheerlinck et al.'s (ACCV 2018) assertion that "the difference will be insignificant", made without evidence and
never revisited. **A related risk we surface ourselves:** EVDI (CVPR 2022) Eq. (19)–(20) already implements the
exposure-correct two-frame loss, so a reviewer may say the fix is published. It is — as an implementation choice,
without the closed form, the bound, the measurement, or the propagation into threshold estimation, and alongside a
gauge-fixing normalisation that discards `c` rather than identifying it. We position EVDI as the positive control
and are explicit that we are not the first to write the correct operator. The defence is therefore structural:
our headline residual is measured with
**every** sensor non-ideality switched off, its predictor is derived from the frame-side operator alone with no
fitted parameters, and the noise null returns R² = 0.0015 against our 0.78. The standing explanations of drift —
integration amplifying low-frequency disturbance, plus static threshold mismatch — cannot produce a residual that
survives a perfect sensor.
**Two verification gates that must be closed before writing an introduction**, both blocked by paywalls during
this review: (a) **Brandli, Muller & Delbrück, ISCAS 2014** — the paper two later works cite for speed-dependent
thresholds, and which TPAMI 2020 credits with per-pixel threshold measurement by APS-vs-event differencing; it is
four pages behind IEEE and must be read through institutional access. (b) **Electronics 15(7):1420 (2026),
"Spiking Feature-Driven Event Simulation with Movement-Aware Polarity Integration"** — MDPI returned 403; the
title is uncomfortably close to our framing.
*Fallback:* if either turns out to report the exposure/LME gap, pivot to the **invariant** (`φ`) and the
**identifiability** result (per-pixel `c_p` recovered from two exposure functionals, better conditioned under
faster motion), which stand independently of the diagnosis.

**Death 2 — "Real, but learned networks absorb it; your PSNR gain is 0.1 dB."**
The most likely reviewer attack and the most dangerous. A static bias *is* absorbable by capacity. Our answer is
P6, already measured: fit on slow motion, test on fast, and a learned constant removes 0.0 % of the residual
variance while a learned linear model in generic event features removes 51 % and degrades sharply across the
support shift, against 91.2 % for the parameter-free correction. The decisive paper experiment is therefore
**generalisation along the support axis** — train on short exposure / slow motion, test on long / fast — with MCB
as the readout. *Fallback:* reposition as a **benchmark and diagnosis** contribution: a support-controlled protocol
(duty × speed grid) on which every published method's motion-conditioned bias is exposed, plus the free `LME` fix.
Weaker, but still a defensible CVPR paper.

**Death 3 — "The invariant is too weak: discarding the amplitude costs more than the bias did."**
Genuine. Our own measurement shows `φ` is quantisation-limited (2.4–6.0 % quantile drift), at low event counts
per pixel it is nearly uninformative, and refractory dead time warps it. *Fallbacks, in order:* (i) use the profile
term as an auxiliary regulariser rather than the sole target — the support-aligned data term alone is provably
correct and needs no invariant; (ii) gate `φ` on a per-pixel event-count threshold and fall back to the standard
term elsewhere, reporting coverage; (iii) if `φ` never helps, publish the corrected forward model plus the
identifiability result and report the invariant as a negative result with its measured breakdown curve, which is
itself informative.

**Secondary risks.** BS-ERGB is verified unobtainable, so a reviewer asking for that comparison cannot be
satisfied — pre-empt this in the paper (mitigated: DSEC + REBlur + HS-ERGB mirror + HighREV cover the ground).
Repos with custom CUDA (GEM, CBMNet) may not build on sm_120 (mitigated: they are not needed; five
non-CUDA-extension baselines suffice). v2e's specific non-ideality model being unrepresentative — and note the
cross-check is
weaker than it first appears, since neither ESIM nor DVS-Voltmeter models a refractory period at all (mitigated:
DVS-Voltmeter covers the shot/leak axis, IEBCS or SENPI covers refractory, then real DSEC data). Disk pressure
from simulated events (~200 GB of 990 GB free).

## Self-score

Scale: 1 = worst, 10 = best, except **incrementality**, where **10 = maximally incremental (bad)**.

* **Novelty — 6.5/10.** Down from an initial 7 after verification. The correct operator is *not* new: mEDI's
  Eq. (5) carries the exact term `J̃(c)` and EVDI's Eq. (19)–(20) already uses the exposure-correct two-frame
  form. What two independent sweeps confirm is unclaimed: the closed form `J = ½Var_W(L)`; any measurement of what
  the methods that drop it lose; the propagation of the bias into per-pixel contrast-threshold *calibration*
  (P7 — the strongest single result, and a genuine re-attribution of a phenomenon currently charged to the
  sensor); the identifiability of `(L⁰, a_p)` from two exposure functionals, in a field where no differentiable
  per-sequence estimator of `c` from paired events and frames exists at all; and the threshold-invariant `φ`,
  whose nearest relatives are global gauge-fixing normalisations rather than a per-pixel temporal invariant.
  Not higher, because the headline fix is one line and its operator is already in print.
* **Feasibility — 8/10.** Every core claim above was verified numerically on CPU in minutes; the study is
  70–120 GPU-hours under 9 GB, with Docker and an nvidia runtime already on this host, and the core measurement
  is 1–2 days. Not 9 because real-data confirmation needs downloads not yet on disk and because one canonical
  dataset (BS-ERGB) has gone dark.
* **Reviewer-proof-ness — 6/10.** Two attacks must be answered on page one, not in rebuttal: "EDI already models
  exposure" and "networks absorb static biases." The first has a clean answer (two-frame use; `ĉ` drift). The
  second rests on the cross-support generalisation experiment actually reproducing P6 at network scale; if it
  returns a null, the paper shrinks to a measurement. The parameter-free-predictor design is the main defence —
  a slope of 0.955 with zero fitted parameters is hard to argue with.
* **Incrementality — 4/10 (moderately non-incremental).** It changes the problem definition (frames are
  functionals with support, not samples) and the supervised unit (profile + amplitude, not intensity), which is
  more than an architecture delta. Not a 2 or 3 because the deliverable still lands on the same tasks with the
  same metrics as the field, and the most defensible contribution — the `LME` fix — is literally one line of code,
  which reviewers will notice and weigh.

---

### 한국어 요약

**주장.** 캡처된 프레임은 노출 구간 로그휘도 궤적의 **로그–평균–지수(log-mean-exp) 범함수**이지 순간 표본이
아니다. 따라서 순간표본 형태의 이벤트–프레임 항등식은 **노출 구간 로그휘도 분산의 절반**(`J = ½·Var_W(log I)`)
이라는 결정론적 편향을 갖는다.

**수치 검증(전부 자체 재현).** (1) 센서 비이상성을 **전부 끈** 완벽한 센서에서도 잔차의 **77.8 %**(엣지 혼합
장면)~**99.1 %**(질감 장면)가 자유 파라미터 0개인 이벤트-only 예측자로 설명된다(기울기 0.92–1.00, 장면 모델
3종 × 시드 3개; 노이즈 귀무가설 R² = 0.0015). (2) 잔차 표준편차는 컨트라스트 임계값의 **0.53–0.71배(엣지),
2.6배(질감)**. (3) 잔차는 전역 평균이 0인 **쌍극자** 패턴이라 지금까지 노이즈로 오인되어 왔다. (4) 느린 모션에서
학습한 보정은 빠른 모션 잔차 분산을 0 %(상수)/51 %(선형)만 제거하나, 물리적 LME 보정은 파라미터 없이 91.2 %
제거 — 네트워크 용량으로 흡수되지 않는다. (5) **가장 강력한 결과**: 표준 화소별 컨트라스트 임계값 캘리브레이션
(Wang ACRA 2019 Eq. 6)을 **완벽한 센서**에 돌리면 블러 증가에 따라 ĉ 가 0.189 → −0.004 로 붕괴(오차 −102 %,
부호 반전)하는 반면, 노출 정합 추정기는 전 구간 0.196–0.210 을 유지한다.

**선행연구 확인(독립 스윕 2회).** EDI/mEDI 는 정확항 `J̃(c)` 를 **정확히 보존**하므로 "EDI가 틀렸다"고 쓰면
안 된다. EVDI(CVPR 2022) Eq. (19)–(20) 은 두 장의 블러 프레임을 노출 정합 형태로 올바르게 다루는 **유일한**
방법이며, 우리 논문의 **양성 대조군**으로 명시해야 한다. PDF 44편 전문 검색에서 "Jensen"·"log of the average"
0건. 유일한 근접 언급은 Scheerlinck ACCV 2018 §3.1 의 *"차이는 미미할 것으로 믿으며 더 다루지 않는다"* 라는
근거 없는 기각이며, 8년간 검증되지 않았다. AKF(ICCV 2021)의 Jensen 항은 **노이즈 분포**에 대한 것으로 축이 다르니
명시적으로 구분할 것. 임계값의 속도 의존성 자체는 이미 알려져 있으므로(Delbrück CVPRW 2021 등) 인용만 한다 —
다만 P7 은 그 일부가 **캘리브레이션 절차가 만들어낸 인공물**임을 보인다.

**실험 가능성(실측 확인).** GoPro 240fps `GOPRO_Large_all`(35.3 GB, 폼 없음, 이미 240fps 라 업샘플링 불필요 —
비용을 좌우하는 결정) + **DSEC**(유일하게 실제 프레임별 노출 구간 메타데이터 보유 → GT 없이 실데이터 검증 가능)
+ REBlur(0.66 GB) + HighREV(NTIRE 2025/2026). **BS-ERGB 는 공개 경로 소실로 사용 불가**(Time Lens++ 소속).
EFNet·REFID·EVDI·E2VID·ELEDNet 체크포인트 생존 확인, 커스텀 CUDA 없어 sm_120(5090) 구동 가능. 시뮬레이터는
v2e 만이 전 항목 토글 제공(ESIM 은 임계값 산포만, DVS-Voltmeter 는 불응기 없음 — 교차검증 한계를 명시).
핵심 측정(Stage 0–2)만으로 1–2일, 전체 70–120 GPU-시간, VRAM 9 GB 이내.

**제출 전 미해결 검증 2건.** Brandli et al. ISCAS 2014(IEEE 유료), Electronics 15(7):1420 (2026)
"Movement-Aware Polarity Integration"(MDPI 403).
