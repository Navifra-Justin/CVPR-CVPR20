# Reviewer 01 — event-camera sensor physics and event representations

*CVPR 2027 idea-selection round. Ten ideas judged on one question: **are the physical premises true of a real
event camera, and would the proposed measurement survive contact with a real sensor rather than a simulator?***

**Note on grounding method.** The shared WebSearch budget was already exhausted before this review began
(200/200). I therefore grounded against the **CVF open-access proceedings listings and paper PDFs already
resident on this machine** (`CVPR2024.html`, `CVPR2025.html`, `ICCV2025.html`, `titles26.txt` = the CVPR 2026
accepted list, plus full PDFs), which is stronger evidence than a search snippet: every title below was
extracted programmatically from the official CVF listing for its venue, and for six of them I read the paper.
Where I claim a number from DSEC I computed it myself from the exposure-timestamp files on disk; those
computations are reproduced inline.

---

## Comparison set

Ten actually-accepted papers, all verified present in the official CVF proceedings listing for the stated venue.

| # | Title | Venue | Year | What it did |
|---|---|---|---|---|
| C1 | **Latency Correction for Event-guided Deblurring and Frame Interpolation** (Yang, Liang, Yu, Chen, Ren, Shi) | CVPR | 2024 | Models the **event timestamp itself as wrong** — a per-pixel, illumination-dependent latency between the physical brightness change and the timestamp the sensor assigns — parameterises it, makes the EDI double integral differentiable w.r.t. latency, and validates on synthetic and real data across lighting conditions. *This is the field's own admission that "microsecond timestamps" are not exact times.* |
| C2 | **State Space Models for Event Cameras** (Zubić, Gehrig, Scaramuzza) | CVPR | 2024 | Replaces the RNN in RVT-style detectors with S4/S5 SSMs carrying a **learnable timescale**, so a model trained at one event-window duration deploys at another; average mAP drop across train/test frequency of 3.31 vs 21.25 (RVT) and 24.53 (GET). Establishes that window duration is a first-class nuisance variable, and that robustness to it is already a solved-ish, published axis. |
| C3 | **TTA-EVF: Test-Time Adaptation for Event-based Video Frame Interpolation** (Cho, Kim, Jeong, Yoon) | CVPR | 2024 | Online test-time adaptation for event VFI, motivated explicitly by the fact that **"event camera data distribution undergoes substantial variations based on camera settings and scene conditions"** — i.e. bias settings and illumination move the event statistics enough to break a trained model. |
| C4 | **Ev-3DOD: Pushing the Temporal Boundaries of 3D Object Detection with Event Cameras** | CVPR | 2025 | First event-based 3D detection with "blind-time" evaluation between LiDAR sweeps; releases DSEC-3DOD / Ev-Waymo with 100 FPS GT built by **linear interpolation of 10 FPS labels plus expert refinement on VFI-synthesised sensor data**. |
| C5 | **TimeTracker: Event-based Continuous Point Tracking for VFI with Non-linear Motion** (Liu et al.) | CVPR | 2025 | Tracks continuous per-patch trajectories through events to handle non-linear intra-interval motion, explicitly because "continuous motion cues from events do not align with the dense spatial information of images in the temporal dimension." The closest published thing to "the two modalities do not share a temporal support," solved as a tracking problem. |
| C6 | **Unleashing the Temporal Potential of Stereo Event Cameras for Continuous-Time 3D Object Detection** | ICCV | 2025 | Fully asynchronous stereo-event 3D detection queryable at arbitrary timestamps — event-only, so the frame-exposure question never arises. |
| C7 | **Simultaneous Motion And Noise Estimation with Event Cameras** | ICCV | 2025 | Joint estimation of motion and of the noise process, i.e. treats event noise as a structured, estimable quantity rather than as i.i.d. corruption. |
| C8 | **Adaptive Spatial-Temporal Window (ASTW): Unlocking the Potential of Event Cameras** (Sui et al.) | CVPR | 2026 | Per-patch adaptive time window `Δt_ij = clamp(γ/(D̄_ij+ε), Δt_min, Δt_max)` from a max-entropy criterion on patch event density; **re-imposes a global timestamp** via a minimum-time-step rule "to prevent violating the causal consistency of the scene"; introduces **HetVel**, an RGB-event heterogeneous-velocity dataset. Ablations: removing patch division −4.0 mAP, removing causal consistency −1.2 mAP. *(Read from PDF.)* |
| C9 | **Time-Specialized Event-Image Alignment for Blur-to-Video Decomposition (TSANet)** (Sun, Xu, Jiang, Liu, Tian, Fu, Zha) | CVPR | 2026 | Blur-to-video decomposition with Relative Time-Encoded Attention + Timesurface Dynamic Warping, queryable at arbitrary target times. **Its Figure 1 is the "four different intra-exposure motion patterns produce the identical blurred frame, and the events disambiguate them" construction.** *(Read from PDF.)* |
| C10 | **Event Stream Filtering via Probability Flux Estimation (EDFilter)** (Chen, Zhai, Cao, Li, Zha) | CVPR | 2026 | Models event generation as **threshold-crossing probability flux of a stochastic irradiance diffusion**, and explicitly uses both the state information `I_{t_i} − I_{t_{i-1}} = p_i C` **and the process information `sup_{t∈[t_{i-1},t_i)} \|I_t − I_{t_{i-1}}\| < C`** — the inter-event interval as an interval-valued constraint on the latent path. Releases the Rotary Event Dataset with microsecond GT irradiance flow. *(Read from PDF.)* |

Bonus, because it is directly load-bearing for one physical premise below: **Event Structural Valley (ESVA)**,
CVPR 2026 — event-based autofocus, which derives from event-generation physics that **event rate is
non-monotone in blur** (it rises, then *falls*, forming a dual-peak/valley structure). Any idea that uses
"event count" as a monotone proxy for motion or blur is contradicted by an accepted CVPR 2026 result.

---

## Per-idea verdicts

| Team | Verdict | One-sentence reason |
|---|---|---|
| **01** | BORDERLINE | The non-identifiability proposition is correct and the headline figure is cheap, but its Fig-1a prediction ("left–right exposure-midpoint difference ≥ 1 ms on a substantial fraction of frames") is **falsified by the data**: I measure median 8–72 µs, max 190 µs, **0.00 % of frames above 1 ms**, and identical exposure *start* on 100 % of frames. |
| **02** | BORDERLINE | Propositions 1–2 are right, but the "un-arguable" time-reversal-pair experiment it puts in Figure 2 is the opening figure of TSANet (CVPR 2026, C9), so its single strongest novelty asset is defeated by a fifteen-minute check. |
| **03** | **REJECT** | Its matched-pair design assumes "event counts are matched by construction" for constant-velocity vs dwell-then-dash — false under refractory dead time, which is maximal in the dash — and its predicted object (a 16-bin per-pixel sub-probability measure inside one exposure) is unidentifiable at the real density of **~1.1 threshold crossings per firing pixel**. |
| **04** | BORDERLINE | Best-de-risked pilot in the set (3 days, 3 GPU-h, zero downloads), but §4.1 defines the frame's evidence weight `w(t)` as content-dependent *within* one exposure, and §8.3 then asserts the frame-only control must give `σ_τ ≈ 0` — the paper's most important control is predicted wrong by the paper's own theory. |
| **05** | ACCEPT | The load-bearing claim (a unit-modulus linear-phase shift cannot correct a modulus mismatch with zeros) is a theorem plus a CPU numerical experiment that cannot fail to produce a figure; the real-data half is thin because DSEC daytime `b = vT < 1 px`, which they alone predicted and scheduled a day-one check for. |
| **06** | ACCEPT | The only team that actually ran its measurement before writing (slope 0.955, R² 0.78 with every non-ideality off, noise null R² 0.0015), and `J = ½Var_W(L)` is exactly the Jensen gap — but the "zero-free-parameter" predictor is not free of `c`, and `c` is per-pixel, illumination-dependent and polarity-asymmetric. |
| **07** | **REJECT** | The load-bearing type distinction — "an event is an **exact**, uncensored observation of a crossing time; a frame is interval-censored" — is false: event timestamps carry illumination-dependent photoreceptor latency (CVPR 2024, C1), rate-dependent AER arbitration delay, and refractory right-censoring, so both modalities are censored and the likelihood is misspecified. |
| **08** | ACCEPT | Makes almost no sensor-physics claims and therefore gets none of them wrong; every experiment is inference-only on checkpoints whose URLs and sizes it verified, and its most damaging result (E0, the linear-oracle reductio on DSEC-Det/DSEC-3DOD labels) needs a 4.7 MB label file and zero GPU. |
| **09** | **REJECT** | `τ(x,t) = C·N(x,t)` is claimed to be the total variation of the log-intensity path with "zero free parameters," but `N` is rate-dependently under-counted by refractory and inflated by leak/shot events, and `C` is an unknown per-pixel gain — so the "exact, bit-for-bit" invariance holds for an ideal DVS and fails worst in the fast/low-light regime it targets; its pre-registered make-or-break number is also verifiably wrong (see below). |
| **10** | BORDERLINE | Proposition 1 is algebraically true but physically vacuous — the "mass-zero" property of an event bin is a property of the *ideal* polarity-sum model, not of a real voxel grid — and the headline `EU(s)` inversion is confounded by refractory-driven event-rate saturation, for which no control is proposed. |

---

## Detailed review

### Team 01 — *A Frame Is Not a Timestamp*

**1. Verdict.** BORDERLINE.

**2. Summary.** The paper's spine is a substitution argument: writing `B = ∫₀¹ L(γ(u)) du` after `u = (τ−t₀)/T`
removes `t₀` and `T` from the image-formation equation exactly, so a blurred frame carries zero information
about its own integration window and the dataloader's scalar timestamp is an unfalsifiable prior. From this it
predicts a signed, motion-direction-conditioned localisation bias `E[e_∥|d] = (α_model − α_label)·d`, argues
that a documented cross-dataset "domain gap" is really a clock-convention gap removable by one scalar per
dataset, and replaces the point state with a Bernstein-basis trajectory over a *normalised* support plus an
estimated support field `(t̂₀, ρ̂, T̂)`. It is honest that `K = 0` reproduces the current formulation exactly,
and it correctly notes that DAVIS APS and DSEC RGB are global shutter so the rolling-shutter term is sim-only.

**3. Strongest reason to accept.** The headline result costs ~10 GPU-hours of pure inference on other people's
checkpoints, and the central latent has a free real-data validation signal (`SIE = |T̂ − T|` against DSEC's
published exposure timestamps, never shown in training). A paper whose main claim is a property of the field's
own benchmarks, not of the authors' model, is the right shape for this venue.

**4. Strongest reason to reject.** The real-data money plot (Fig 1b) requires **intra-exposure event timing on a
DAVIS346** (FE240hz). That is the one sensor where measuring events *inside* an APS exposure is worst-posed:
the APS and DVS share a photodiode, and APS reset/readout injects frame-synchronous artefact events. A slope
measured on events acquired during the exposure of the same pixel's APS integration is contaminated by exactly
the mechanism the plot is about, and nothing in the plan controls for it.

**5. Factual errors.**
- *Fig 1a, "prediction ≥ 1 ms [left–right exposure-midpoint difference] on a substantial fraction of frames."*
  **Wrong by an order of magnitude.** Computed from the on-disk DSEC exposure files: `interlaken_00_d` median
  27 µs / max 152 µs; `zurich_city_05_a` median 72 µs / max 190 µs; `zurich_city_06_a` median 8 µs / max 51 µs.
  Fraction of frames above 1 ms: **0.0000** in all three. Correction: the divergence is 8–190 µs.
- *"DSEC literally averages two different exposure midpoints into one number"* — technically true but
  misleading. **The exposure START timestamp is bit-identical between left and right on 100 % of frames**
  (verified: `L[:,0] − R[:,0] == 0` for 1991/1991, 1753/1753, 1523/1523 frames). The two windows are
  co-triggered and differ only in duration; there is no offset at all. Correct the claim to "different widths,
  same start."
- *"~1 ms daylight to >15 ms night"* under-states the structure. My measurement over 18 sequences: min 118 µs,
  median 1181 µs, max 14996 µs — and **six sequences sit pinned at exactly 14996 µs for every frame**, i.e.
  auto-exposure saturated at its cap. Consequence the paper must absorb: **long exposure and exposure
  *variation* are anti-correlated in DSEC.** The sequences with wide windows have zero within-sequence variance,
  and the sequences with variance have windows of 0.3–4 ms.
- *"FE108 host … turnaround unknown"* — the page is live (`zhangjiqing.com/dataset/`, HTTP 200) and is
  application-gated. **Favourable correction the team should know: FE108 ships `.aedat4`** ("To load the aedat4
  file, you should install … dv-gui"), and AEDAT4 frames carry `timestampStartOfExposure` /
  `timestampEndOfExposure`. So the APS exposure window *is* recoverable, contrary to the team's own hedging.
  This also falsifies Team 06's claim that DSEC is "the only public event–frame dataset with real per-frame
  exposure intervals."

**6. Claims stronger than the evidence.**
- *"The frame does not determine `t₀` or `T`. Not approximately — **not at all**."* True for the idealised
  normalised-integral model, false for the sensor: photon shot noise scales as `√(T·Φ)` and read noise does
  not, so frame SNR is a (weak, scene-dependent) function of `T`. The absolute statement will be attacked.
- *"Prediction: `T̂` within 15 % of DSEC's reported exposure."* On the sequences where `T` is pinned at 14996 µs
  a constant predictor achieves this trivially; on the sequences where `T` varies, `T` is 0.3–4 ms and the
  events available inside it are ~1.1 crossings per firing pixel. The prediction is either trivial or
  unsupported, dataset by dataset. Report it stratified.
- *"crossings per firing pixel near 1.1 is not a displacement measurement"* — the brief already says this; the
  paper must not slide from event density to displacement anywhere, and §Fig-1a currently does via
  `|flow_GT|·T/Δt`, which is a *frame-rate* flow rescaled, not an intra-exposure measurement.

**7. Experiment a hostile reviewer demands.** Repeat Fig 1b with the DAVIS APS **disabled** on a subset (or on
a beam-splitter rig where the event camera never sees an APS readout), and show the TSB slope is unchanged.
Absence is not fatal, but it moves the paper from "measured" to "plausible."

**8. Ranked fixes.** (i) Delete the left/right-divergence panel or restate it at 8–190 µs and drop it from the
argument. (ii) Move the primary real-data slope to a sensor without APS/DVS crosstalk. (iii) Report `T̂`
accuracy separately for exposure-saturated and exposure-varying DSEC sequences. (iv) State the shot-noise
caveat to "not at all." (v) Apply for FE108 on day 1 and confirm aedat4 exposure fields are populated.

---

### Team 02 — *No State at t: Exposure-Occupancy Measures*

**1. Verdict.** BORDERLINE.

**2. Summary.** Argues that every dataset silently applies an unnamed annotation operator `A` to a state
*process* over the exposure, that the candidate operators (`A_mid`, `A_mean`, `A_mode`, `A_hull`, …) disagree
by a signed scene-dependent amount, and therefore that a benchmark's ranking partly measures which model best
guessed an unwritten habit. It replaces the point target with the exposure-occupancy measure
`μ = y_# Unif(W)` parameterised as a support spline `γ_θ` pushed forward by a learned dwell density `p_φ`,
trains on ordinary point labels by treating the convention as a latent categorical fitted by EM, and audits
set-valued predictions on point-labelled benchmarks via split-conformal coverage. Its sharpest claimed result
is that label ill-posedness is governed by intra-exposure **acceleration**, not blur magnitude — at constant
velocity `A_mid = A_mean = A_mode` exactly, no matter how severe the blur.

**3. Strongest reason to accept.** The acceleration-vs-blur decoupling is a genuinely non-obvious, correctly
derived, and cheaply falsifiable claim about the field's chosen difficulty axis, and the conformal coverage
device makes a set-valued output auditable against benchmarks that only have point labels — which is the thing
that would let anyone else adopt it.

**4. Strongest reason to reject.** The paper's designated "proof, not a benchmark delta" — the time-reversal
pair, promised for Figure 2 — is **the opening figure of an accepted CVPR 2026 paper**. TSANet (C9) Figure 1
shows four intra-exposure motion patterns of a hand-and-ball that "after temporal averaging, all of them
produce the same blurred image," with the events shown as the disambiguating cue. The construction is
published, illustrated, and used for the same purpose (events break the blur's motion ambiguity). Team 02's
strongest asset is therefore not novel, and the team did not find it.

**5. Factual errors.**
- *Proposition 2's stated reason is wrong.* "The unknown, per-pixel, polarity-asymmetric contrast threshold
  means the *mass* … is not recoverable from events alone." The threshold is a gain; it scales the recovered
  log-intensity, it does not remove the mass. The actual reason events cannot supply mass is the **unknown
  initial condition `L(x,0)` per pixel** — the DC null of a differencing sensor. Fix the proof or a physics
  reviewer will read the whole propositional apparatus as decorative.
- *"the only public event+frame benchmark whose label rate is an order of magnitude above its frame rate"* —
  EVIMO2's 200 Hz Vicon against its colour camera is in the same class, and the team lists it two lines later
  as a fallback. Soften.
- *"v2e is pip-installable … availability risk: None."* v2e's standard pipeline pulls a SuperSloMo checkpoint
  from Google Drive. Team 04 identified this correctly and engineered around it; Team 02 has not.

**6. Claims stronger than the evidence.**
- *"Our `(γ, p)` with `L_evt` separates them at ~100 %."* Time-reversal separation from events requires that
  the event polarity/timing asymmetry survives the sensor. Under a refractory period the dash half of a
  dwell-then-dash trajectory loses events preferentially, and under low light the photoreceptor low-pass
  smears the ordering. "~100 %" is a simulator number stated as a physical one.
- *"On the top-20 % ν subset of FE108, the RSR change … is 10–20 points, whereas the spread between the five
  published trackers is 3–8 points."* This is the indictment, and it is a pure guess. It must be flagged as
  such or measured in week 1 as their own kill criterion says.

**7. Experiment a hostile reviewer demands.** Run the time-reversal pair through **TSANet** and through a
contrast-maximisation baseline. If either separates the pair, the "existing methods cannot express this"
column collapses. Absence is close to fatal now that C9 exists.

**8. Ranked fixes.** (i) Cite TSANet (CVPR 2026) as prior art on the reversal construction and re-lead with
the *convention latent `π`* and *conformal convention-marginal coverage*, which TSANet does not have. (ii) Fix
Proposition 2's mechanism (DC null, not threshold). (iii) Run the day-7 kill criterion on EVIMO2, which is
ungated, before touching FE108. (iv) Add a refractory ablation to the reversal experiment. (v) Drop "None" as
an availability risk for v2e.

---

### Team 03 — *Temporal Support Fields*

**1. Verdict.** **REJECT.** Fatal to this execution, not to the underlying intuition.

**2. Summary.** Proposes that each observation be assigned, per pixel and per modality branch, a
**sub-probability measure on the time axis** — mass `m` ("is there evidence at all") times shape `s̄` ("from
when") — and that cross-modal fusion be an *overlap* of those measures rather than a feature similarity, with
`a_xy = softmax(q·k/√d + λ log⟨ŝ^F_x, ŝ^E_y⟩)`. The event branch's support is claimed free on real data (the
inter-event interval, read from the raw stream), and the frame branch's is self-supervised by re-rendering the
blurred frame under the predicted support via the EDI double integral. The failure phenomenon is a matched-pair
construction: constant-velocity vs dwell-then-dash at identical blur extent and identical event count, giving
ground-truth support overlap `O*` of 0.8 vs 0.15.

**3. Strongest reason to accept.** The sub-probability (mass ≤ 1) is genuinely load-bearing and correctly
motivated: a probability distribution must put its mass somewhere and therefore cannot express "there is no
valid observation of this pixel at this time." Temporal abstention as a first-class output is a real gap, and
the risk-coverage comparison against softmax confidence is a fair, falsifiable way to show it.

**4. Strongest reason to reject.** Two independent physics failures, either of which sinks the plan.

*(a) The matched-pair construction is false on a real sensor.* The paper writes: "Event counts are matched by
construction (same `d`, same contrast, same threshold ⇒ same number of threshold crossings)." This holds only
for a sensor with no dead time. Under a refractory period, the number of *emitted* events is
`r = 1/(T₀ + Δ_refr)`-limited, so the dash — which covers displacement `d` in `0.2T`, i.e. at 5× the
instantaneous rate — loses events that the constant-velocity twin does not. The pairs are therefore matched on
`O*` **and** unmatched on event count in exactly the configuration that makes `O*` differ, which is the
confound the whole design exists to eliminate. Worse, this cuts the same way in the direction of the claimed
result: the low-`O*` arm has fewer real events, so a PSNR cliff would be produced by event starvation rather
than by support mismatch. The paper's own headline partial-correlation test (`|ρ(err, O*|d, N_ev)| ≥ 0.6`) is
built on conditioning on an `N_ev` that its generator cannot hold fixed once refractory is on.

*(b) The predicted object is unidentifiable at real event densities.* The model emits `K = 16` bins per pixel
per branch. The brief's verified DSEC measurement gives a median of **20 616 events inside one 1478 µs daytime
exposure, touching 6 % of pixels — 20616/(0.06·640·480) = 1.12 threshold crossings per firing pixel.** One
crossing cannot determine a 16-bin sub-probability measure; it cannot determine a 4-bin one. The paper's own
Death-3 fallback ("predict only a 2-parameter (centre, width) support … retreat to the first moment and the
mass") is not a fallback, it is the only regime that exists on real data, and at that point the contribution
reduces to a per-pixel scalar reliability plus a scalar time — which is precisely the "uncertainty foil" the
paper sets up as its straw man in ablation (viii).

**5. Factual errors.**
- *"An event pixel's support is the inter-event interval … this branch's ground truth is readable from the raw
  stream on real data, for free."* The recorded inter-event interval is **not** the information support. It is
  bounded below by the refractory dead time (so short intervals are censored and piled at `Δ_refr`), inflated
  by leak events (a monotone bias generator that fires with no scene change), corrupted by shot noise in low
  light (spurious short intervals), and perturbed at the top end by AER arbitration when the bus loads. The
  "free real ground truth" is a distorted measurement of the thing being supervised, and the distortion is
  worst under the fast motion the paper targets.
- *"We found no work that predicts a temporal support measure as its output."* **EDFilter, CVPR 2026 (C10)**
  reconstructs a continuous per-pixel *event density flow* from threshold-crossing probability fluxes, and
  states the inter-event interval as an interval-valued constraint on the latent path in exactly the form this
  paper claims as unclaimed (`sup_{t∈[t_{i-1},t_i)} |I_t − I_{t_{i-1}}| < C`). That is a published, accepted
  CVPR 2026 instance of a per-pixel temporal measure as output, with a microsecond-GT dataset (RED) to
  validate it. The novelty statement must be rewritten.
- *"RTEA module (CVPR 2026)"* — the module belongs to **TSANet** (Sun et al., CVPR 2026, C9); RTEA is the
  module name, not the paper name. Cite it correctly.
- *"BS-ERGB / HS-ERGB … medium (host availability)"* — Team 06 verified the Time Lens++ download page is dead
  with no mirror. Do not plan the "measured occupancy windows" strand on it.

**6. Claims stronger than the evidence.** *"For a matched pair (A,B) the fused representation … satisfies
‖φ(A)−φ(B)‖/‖φ(A)‖ < 3 % while the ground-truth targets differ by more than the inter-class spread."* Given
(a) above, `φ(A)` and `φ(B)` will differ by more than 3 % on any real sensor for the wrong reason — different
event counts — and the "inexpressibility number" will be an artefact.

**7. Experiment a hostile reviewer demands.** Regenerate the matched pairs with `--refractory_period` swept
{0, 100, 300, 1000} µs in v2e and re-plot the `O*` cliff with the *measured* (not designed) event count as a
covariate. Absence is fatal: this is the experiment that decides whether the phenomenon is support or
starvation.

**8. Ranked fixes.** (i) Re-derive the matched-pair construction under a dead-time model, or match on *emitted*
event count post hoc rather than by construction. (ii) Re-scope `K` from 16 to 2 (centre, width) and state the
identifiability regime as a function of events-per-exposure *before* claiming the representation. (iii) Cite
EDFilter and restate novelty around the cross-branch overlap operator, which EDFilter does not have. (iv)
Replace "free real event-side GT" with "a censored, biased estimator of the event-side support," and model the
censoring. (v) Fix the RTEA/TSANet attribution.

---

### Team 04 — *When Is Your Prediction?*

**1. Verdict.** BORDERLINE.

**2. Summary.** Introduces one measurement primitive — the **effective timestamp** `τ̂ = argmin_t d(ŷ, y*(t))`
against a continuous GT trajectory, with `TEF = 1 − r_min/r_q` reporting what fraction of a reported
localisation error is actually a clock error — and derives that a squared-loss-optimal predictor lands at the
evidence-weighted time centroid `t̄` regardless of the label clock it was trained on. The kill shot is not the
bias `b = E[τ̂ − t_q]` (a reviewer would say "subtract it") but the **within-frame dispersion `σ_τ`**: different
objects and regions in one output tensor live at different times, so no scalar clock correction exists. It
names the setting a *change-of-support* problem, correctly identifies FAOD's shift-invariance training as the
antagonist rather than the ancestor, and pre-registers a full null result.

**3. Strongest reason to accept.** The pilot is the best-engineered de-risking in the ten: three days, ~3
GPU-hours, zero downloads, and — the detail that matters — **rendering natively at 10 kHz removes v2e's
SuperSloMo dependency**, which is the single most common way an event-simulation plan dies. `τ̂` is also
embarrassingly simple and, as far as I can tell, genuinely unrun on a fused event–RGB task head.

**4. Strongest reason to reject.** The paper contradicts itself on its own most important control. §4.1 defines
the frame branch's evidence weight `w(t)` as "proportional to the moving object's contrast energy deposited at
instant `t` **in the exposure**" — i.e. content-dependent *within a single frame's support*, and §4.2's Figure
4 sweeps exactly that (texture asymmetry `A` at fixed clock and speed). §8.3 then declares: "a single modality
has a *single* support, so our theory predicts `σ_τ ≈ 0` for both [frame-only and event-only]. **If `σ_τ` is
just as large for the frame-only model, the phenomenon is not about fusion and the paper's framing is wrong.**"
By the paper's own §4.1, a frame-only model has a per-object, content-weighted `w(t)` and therefore
`σ_τ > 0`. The paper has pre-registered a control whose failure it has already derived, and has committed in
advance to reading that failure as a refutation of its framing.

**5. Factual errors.**
- The dimensional claim in C1 — "`τ̂ − t_q` … is (to first order) **independent of speed `v`**" — is false once
  the event branch is real. `w(t)` for the event branch is "proportional to local event rate," and event rate
  is not proportional to speed: it saturates and then declines with speed under refractory dead time (the
  `r = 1/(T₀ + Δ_refr)` law), a fact now underwritten by an accepted CVPR 2026 result showing event rate is
  non-monotone in blur (ESVA's dual-peak-valley). So `t̄` is speed-dependent through the sensor, and the paper's
  own falsification row ("`b` scales with `v` ⇒ it is a latency, not a support effect") would fire on pure
  sensor physics and be misread as a refutation.
- *"τ̂ requires GT at a rate far above the frame rate … FE240hz → τ̂ measurable to ~1 ms after spline
  interpolation."* The effect sought is 2–5 ms and the Vicon sampling interval is 4.17 ms; spline interpolation
  does not create temporal bandwidth, it assumes it. The team concedes this in the self-score; it should be in
  the plan, not the self-score.
- *"PEOD (AAAI 2026)"* and *"MambaTrack / Event-Adaptive State Transition (arXiv 2604.13426)"*,
  *"TAPFormer (arXiv 2603.04989)"* — I could not verify these against any proceedings list on hand. Treat as
  unverified and check before they appear in a related-work table.

**6. Claims stronger than the evidence.** *"a `b = 5 ms` bias at `v = 1000 px/s` is a 5 px shift … the
detection is a **false positive at AP50 caused entirely by a timing error**."* 4000 px/s on a 346×260 DAVIS346
is 11 sensor-widths per second. State the speed regime in object-diameters-per-exposure and show what fraction
of any real dataset reaches it, before asserting benchmark consequences.

**7. Experiment a hostile reviewer demands.** Fit the strongest possible calibration baseline — a per-speed-bucket,
per-object-class lookup table of `Δ` — and report the residual `σ_τ` that survives it. The team proposes this;
it must be in the main paper, because "just recalibrate" is the whole review.

**8. Ranked fixes.** (i) Resolve the §4.1/§8.3 contradiction: predict `σ_τ^frame-only > 0` and make the *fusion
increment* `σ_τ^fused − max(σ_τ^F, σ_τ^E)` the claim. (ii) Add refractory to the event model in the pilot and
re-check the speed-independence of `b`. (iii) Replace FE240hz as the primary real closure with a beam-splitter
set whose high-speed RGB strand exceeds 240 Hz. (iv) Report the identifiability margin for every real-data
point, as promised. (v) Drop unverifiable citations.

---

### Team 05 — *No Offset Can Fix a Width*

**1. Verdict.** ACCEPT.

**2. Summary.** Reframes event–frame temporal calibration from estimating a scalar delay to identifying a
**pair of measures on the time axis** — the frame's exposure kernel `w_F` (width `T`) and the event channel's
causal photoreceptor kernel `w_E` (time constant `τ(Ī)`) — and proves that no shift can close the gap, because
in Fourier a shift is a unit-modulus linear-phase multiplier while a support mismatch is a modulus mismatch
with exact zeros and π phase jumps (T1). It shows the best-fit offset is the spectrum-weighted group delay and
is therefore a function of scene texture and speed rather than a rig constant (T2), and gives a multichannel
identifiability result: from `J ≥ 2` known speeds sharing one texture the kernels are recoverable because the
dilation `ŵ(vξ)` breaks the kernel/texture confound (T3). The failure demonstration is run with an *oracle*
offset search on data where the shift model is nominally exact and the true offset is exactly zero.

**3. Strongest reason to accept.** This is the only idea in the set whose load-bearing claim is guaranteed to
produce a figure, because it is a consequence of the Fourier transform of a box rather than an empirical hope,
and it can be produced on CPU in days with the opponent given every advantage (oracle search, ideal sensor,
zero true offset). Judged by the brief's own criterion — "an idea that is beautiful and unfinishable is worth
less than one that is merely good and certain to produce a real figure" — this scores highest on certainty
among the physics-heavy ideas. It is also the only team that treats the event channel's own kernel as a kernel
rather than as its first moment, which is the correct reading of the photoreceptor front end and is exactly
the gap left open by Latency Correction (C1), whose per-event polynomial is a location model.

**4. Strongest reason to reject.** The real-data half is thin, and the team knows it. The onset condition is
`b = vT ≥ 2 px`. I measured DSEC's exposures: daytime medians are 0.3–1.9 ms, so `b ≥ 2 px` requires
`v ≥ 1.05–6.7 px/ms`, i.e. 1000–6700 px/s of image-plane motion, which is far above typical DSEC driving flow
outside the immediate foreground. The sequences that *do* have wide exposures are the six pinned at exactly
14996 µs — and those are the low-light sequences, where the photoreceptor bandwidth (which scales with
photocurrent) collapses, `τ(Ī)` becomes large, and the paper's own `w_E` widens toward `w_F`. That is not fatal
to T1 — it is the regime where the two kernels become *comparable*, which the framework handles — but it means
the clean "one channel is a δ, the other is a box" story does not describe the only DSEC data where the effect
is large. And T3's identifiability needs `J ≥ 2` known speeds sharing one texture, which DSEC cannot supply.

**5. Factual errors.**
- *"DSEC ships `image_exposure_timestamps_left.txt` … and then defines the canonical `image_timestamps.txt` as
  the average of the middle exposures"* — correct, and I verified the convention holds to within 1 µs. But the
  implicit suggestion that the two windows are meaningfully different is wrong in the offset sense: the
  **exposure start is bit-identical between left and right on 100 % of frames** and the midpoints differ by
  8–190 µs. Use this as *support* for the argument (the divergence is a width difference, not an offset), not
  as an example of collapsed offsets.
- *"DSEC daytime driving may run exposures of 0.1–1 ms"* — measured range is 118 µs to 4207 µs in the
  non-saturated sequences, median 1181 µs overall. Use the measured numbers.
- *"The CVPR 2026 proceedings contain 60+ event papers and none is about event–frame temporal support or
  exposure-aware calibration."* I counted the CVPR 2026 accepted list independently: the event/spiking/blur/
  exposure slice is consistent with that order of magnitude, and I found no exposure-aware *calibration* paper.
  But **TSANet (C9)** is an event–image *temporal alignment* paper and **ASTW (C8)** is an event temporal-window
  paper, both CVPR 2026 — the sentence as written will be read as sloppy. Narrow it to "calibration."
- *"TSANet (CVPR 2026) … alignment = get features to the right instant"* — accurate, and the team is the only
  one that reads TSANet correctly as a *consumer* of a blind-band mask rather than a competitor. Good.

**6. Claims stronger than the evidence.**
- *"$\hat H_E(\xi) = (1+i2\pi v\tau\xi)^{-1}$"* — a first-order low-pass with a **single** `τ`. The DVS front
  end is a source-follower-buffered logarithmic photoreceptor whose small-signal response is closer to a
  cascade with an intensity-dependent dominant pole, and the effective bandwidth varies by orders of magnitude
  across the image in an HDR scene. The paper lists second-order `w_E` as an ablation; it must be the default
  for any low-light claim, or the night-sequence result is built on a model the sensor does not obey.
- *"At `T = 10 ms` that is **≥ 3 ms of drift** on a rig whose true offset is exactly 0 — an order of magnitude
  above the sub-ms precision EF-Calib/eKalibr-class methods report."* This is a simulation prediction being
  used as an indictment of published calibration numbers. Keep the two separate until OBD is measured on DSEC.
- *"Calibrating faster makes your calibration worse."* Quotable and probably true, but it is currently a
  prediction, not a result. Do not put it in an abstract until Panel A exists.

**7. Experiment a hostile reviewer demands.** Ablation 1 — global shutter, `τ → 0`, noiseless, `δ* = 0`, ideal
thresholding — with SMF and OBD shown to survive. The team schedules it first, which is correct. A second
demand: measure the joint distribution of `(T, v)` across all DSEC sequences *before* committing, which the
team also schedules. Absence of either would be fatal; their presence is why this gets an ACCEPT.

**8. Ranked fixes.** (i) Run the `(T, v)` census in week 1 using the exposure files (they are ~50 KB per
sequence; this is an afternoon, not a day). (ii) Make second-order/intensity-dependent `w_E` the default, not
an ablation, for anything on the 14996 µs sequences. (iii) Restate the left/right divergence as a width
difference with the measured 8–190 µs. (iv) Narrow the "no CVPR 2026 paper" sentence to calibration and cite
ASTW and TSANet explicitly. (v) Pre-commit the fallback (OBD only, notch evidence in sim) in the plan rather
than in the risk section, so the reviewer sees the paper's floor.

---

### Team 06 — *Frames Are Not Samples: The Exposure Gap*

**1. Verdict.** ACCEPT.

**2. Summary.** Observes that the identity underwriting every event–frame consistency loss, `∫events = Δ log I`,
composes two statements, and that the second — `log B_k = L(t_k)` — is exactly false whenever the exposure has
width, because `B` is a linear-domain mean and its log is a **log-mean-exp** functional: `log B_k = L(t_k) + J_k`
with `J_k = ½·Var_{W_k}(L) + O(κ₃)`. It then argues the residual is deterministic and predictable from the
events alone, proposes a threshold-invariant normalised cumulative event profile `φ` as the supervised object,
and shows that the two exposure functionals jointly identify the per-pixel amplitude `a_p = c_p·E_p`, so blur
*identifies* the contrast threshold rather than obscuring it. Unlike every other team, it ran the measurement:
slope 0.955, R² 0.779, 77.8 % of residual variance removed with **every** sensor non-ideality switched off, and
a noise null at R² = 0.0015.

**3. Strongest reason to accept.** It is the only submission whose central empirical claim already exists as a
number rather than a prediction, and the number is the right shape: a parameter-free structural predictor
achieving slope ≈ 1 against a noise null at ~0 is very hard for a reviewer to argue with. Its P6 result — fit
on slow motion, test on fast: a learned constant removes 0.0 % of the residual variance, a learned linear model
in generic event features removes 51 % and degrades 0.059 → 0.105 across the support shift, while the
parameter-free LME correction removes 91.2 % and degrades only 0.044 → 0.055 — is precisely the answer to the
"networks absorb static biases" attack, and it is measured, not asserted. Its simulator survey is also the only
honest one in the set: it states, correctly, that **ESIM models only a Gaussian contrast threshold and does not
model refractory-induced loss at high speed, and that DVS-Voltmeter has no refractory period at all**, so its
cross-checks are constrained rather than free. That is the level of instrument literacy this topic requires.

**4. Strongest reason to reject.** **The predictor is not parameter-free.** The paper writes:
`P = [c·E(t_{k+1}) − LME_{W_{k+1}}(c·E)] − [c·E(t_k) − LME_{W_k}(c·E)]`, and then: "`P` needs no ground truth,
no intensity, and no unknown offset — the reference level cancels inside every LME. It needs only the event
stream and the two exposure windows." The *reference level* cancels. **`c` does not.** LME is nonlinear, so
`LME(c·E) ≠ c·LME(E)`; the predictor is a function of `c` and the whole result is conditional on knowing it. On
a real sensor `c` is (i) per-pixel, with fixed-pattern threshold mismatch of a few percent contrast at the
transistor level and 10–15 % effective spread reported by later per-pixel calibration work, (ii) a function of
illumination and of bias currents and temperature, (iii) **polarity-asymmetric** — ON and OFF thresholds are
set by independent bias currents and are routinely unequal by tens of percent — and (iv) rate-dependent in its
*effective* value, which the paper itself measures (0.26 → 0.37 under a 300 µs refractory across 32 px of
blur). So the headline "zero free parameters" is false, and the one free parameter it has is the single
worst-behaved quantity in the sensor. In simulation, where `c` is set, this is invisible; on DSEC or REBlur it
is the dominant error term in `P`.

Second, subordinate but sharp: the paper's identifiability claim inverts under real physics. It writes: "the
harder the motion, the better the threshold is determined," because `dG/da = 0.86–0.91` and inverting `G`
recovers `a_p` to 0.18–0.22 % relative. But `a_p = c_p·E_p`, and `E_p` is the *emitted* event count, which
refractory and photoreceptor bandwidth cause to under-count precisely in proportion to speed. Faster motion
improves the numerical conditioning of `G` while degrading the physical validity of `E_p`. The two effects run
opposite, and the paper reports only the first. An accepted CVPR 2026 result now makes this concrete: ESVA
shows event rate is non-monotone in defocus blur, rising and then falling — event count is not a monotone
proxy for excursion.

**5. Factual errors.**
- *"DSEC … is **the only public event–frame dataset with real per-frame exposure intervals**."* False. Any
  DAVIS recording distributed as AEDAT4 carries `timestampStartOfExposure`/`timestampEndOfExposure` per frame,
  and **FE108/FE240hz is distributed as `.aedat4`** — verified from the dataset page ("To load the aedat4 file,
  you should install the required toolkit dv-gui"). This is good news for the plan, not bad: it supplies a
  second real anchor on a *co-located* sensor.
- **The DSEC anchor has a parallax problem the plan does not mention.** DSEC's frames come from FLIR Blackfly S
  cameras and its events from Prophesee Gen3.1 units on a stereo rig — the frame and the event stream are
  **different apertures with a baseline**. The regression `R ~ P` is per-pixel and requires the events at pixel
  `x` to be the events of the scene point imaged at `x` during the exposure; on DSEC that mapping is
  depth-dependent and is not available without disparity. The residual will be dominated by warping error, not
  by `J`. REBlur (DAVIS-class) and HighREV are the correct real anchors; DSEC is the wrong one for this
  particular regression, notwithstanding its exposure metadata.
- *"Exposure width swings with illumination frame to frame"* on DSEC — true for 12 of 18 sequences; **six are
  pinned at exactly 14996 µs for every frame** (auto-exposure at its ceiling), so the exposure-sweep story is
  only available in the short-exposure daytime sequences, where `J = ½Var_W(L)` is small. That anticorrelation
  should be stated, because it bounds the real-data effect size.
- *"under a 300 µs refractory the implied threshold rises from 0.26 at 1 px of blur to 0.37 at 32 px, true
  c = 0.20"* — this is v2e's model reproducing v2e's own refractory model. It is a consistency check, not a
  measurement. Label it as such.

**6. Claims stronger than the evidence.**
- *"a one-line, parameter-free `LME` correction"* — see above; it is one line and it takes `c`.
- *"the blur everyone treats as the problem is what makes `c_p` identifiable, and the conditioning *improves* as
  motion increases. No calibration rig, no assumed constant."* Overstated in exactly the direction a
  sensor-physics reviewer will attack.
- *"on textured content … the residual is 2.6 contrast thresholds and 99 % of it is the exposure operator"* —
  measured on a band-limited translating texture with an ideal sensor. The 99 % is a statement about the
  simulator's residual budget, not about DSEC's.

**7. Experiment a hostile reviewer demands.** Re-run the `R ~ P` regression on a real DAVIS recording (REBlur,
or an FE108 aedat4 sequence with its APS exposure fields) with `c` treated as an **unknown per-pixel nuisance**
— e.g. profile it out, or report the slope as a function of assumed `c` over the plausible range — and show
the slope stays within, say, 15 % of unity across that range. Absence is not fatal to the idea but is fatal to
the "parameter-free" framing, which is the paper's rhetorical spine.

**8. Ranked fixes.** (i) Delete "zero free parameters"; replace with "one parameter, `c`, and here is the
sensitivity of the slope to it." (ii) Move the real anchor from DSEC to REBlur/HighREV/FE108-aedat4 and state
the DSEC parallax reason. (iii) Add a refractory-vs-conditioning panel to the `G(a)` identifiability result, so
the "faster is better" claim is bounded rather than asserted. (iv) Handle polarity-asymmetric thresholds
(`c⁺ ≠ c⁻`) explicitly — the LME is computed on a signed integral and an asymmetry is a first-order bias.
(v) Close the two flagged verification gates (Brandli et al. ISCAS 2014; Electronics 15(7):1420) before
writing an introduction, as the team already plans.

---

### Team 07 — *Chronofields*

**1. Verdict.** **REJECT.** Fatal to this execution of the idea; the inverted-query framing itself survives.

**2. Summary.** Inverts every perception head from `time → state` to `state → time`: for a queried state
(a contrast crossing, a spatial passage, a contact, a tripwire crossing) predict a distribution over *when* it
held, including an explicit `∅` atom for "never in this window." The two modalities enter one likelihood with
different censoring — **an event is an exact (uncensored) time observation; a frame with exposure `[a, a+T]` is
interval-censored** — plus a dwell-time change of variables on the blur integral (L4, EDI with the variables
swapped) and a temporal eikonal regulariser `∇_u τ · v = 1` whose gradient is the slowness field. The headline
indictment is that mAP is invariant to any uniform temporal shift smaller than the IoU matching tolerance, so
no event–RGB detection benchmark can distinguish being right at the right time from being right at the wrong
time.

**3. Strongest reason to accept.** The mAP null-space proposition is correct, constructive, and cheap: two
systems with identical mAP to three decimals and 4× different crossing-time error is a real demonstration, and
"the answer is a time" is a genuinely under-occupied output type. The C1 anchor is also the right instinct —
find a task whose ground truth is the raw sensor stream, so no annotator and no simulator is in the loop.

**4. Strongest reason to reject.** The load-bearing premise is false, and it is false in the way this
specialism exists to catch. The paper's entire likelihood family rests on the assertion that
**"an event `(u, t*, p)` is an uncensored observation of a crossing time"** and that the C1 anchor supplies
"real sensor, microsecond ground truth." Neither holds:

- *Latency.* The timestamp a DVS assigns is separated from the physical log-intensity crossing by the
  photoreceptor's response, whose bandwidth scales with photocurrent; in low light the front end low-passes at
  the order of 10² Hz, not 10⁵ Hz, and the delay is scene- and illumination-dependent. This is not my opinion:
  it is the entire premise of **Latency Correction for Event-guided Deblurring and Frame Interpolation, CVPR
  2024 (C1)**, which defines the problem as "the temporal discrepancy between the actual occurrence of changes
  in the corresponding timestamp assigned by the sensor" and models it as a per-pixel polynomial in
  illuminance. An accepted CVPR paper says the exact opposite of Team 07's premise.
- *Right-censoring by refractory.* After each event the pixel is dead for `Δ_refr`. A crossing that occurs
  during dead time is **not observed at all** — that is right-censoring, in the paper's own vocabulary, on the
  branch it declares uncensored. Under fast motion this is the dominant loss mechanism.
- *Readout, not generation.* Under AER arbitration and bus load, events are timestamped at readout; at high
  rates timestamps are batched and perturbed. So the "µs-exact GT" of the C1 anchor is the sensor's readout
  schedule under load, which is itself a function of the scene activity being predicted.

The consequence is not a caveat, it is a misspecification: `L_exact` is a delta likelihood at a time the sensor
does not report, and the paper's central *type* distinction — the thing that makes the frame/event asymmetry
interesting — dissolves, because both modalities are censored and the event branch's censoring is
rate-dependent and correlated with the target. And the C1 anchor, explicitly designated as "our insurance
against every ground-truth objection," is the part that fails hardest, because it supervises against exactly
those readout times.

**5. Factual errors.**
- *"the events themselves measure the frame's own effective timestamp … the contrast-weighted barycenter
  `t̂(u) = (Σ_k t_k)/N_u` over events at pixel `u` inside the exposure is a computable, per-pixel timestamp."*
  With ~1.1 crossings per firing pixel inside a real daytime exposure (verified DSEC number), `N_u ≈ 1` and the
  "barycenter" is a single event's timestamp. It is not a barycenter; it is a sample of size one, and its
  distribution is shaped by the refractory state at exposure open.
- *The headline numerical example is physically unreachable.* "At `T = 20 ms`, `a = −2 px/ms²`, `v̄ = 4 px/ms`:
  `Δt ≈ −8.3 ms`, i.e. **42 % of the exposure**." The arithmetic is right (`aT²/24/v̄ = −2·400/24/4`), but
  `v̄ = v₀ + aT/2` forces `v₀ = 24 px/ms = 24 000 px/s`, with the object reversing to `−16 px/ms` inside the
  exposure and sweeping several hundred pixels. On a DAVIS346 (346 px wide) that object crosses the entire
  sensor in ~14 ms. The paper's flagship "42 % of the exposure" number comes from a configuration no
  event–RGB dataset contains. The second example (`T = 10 ms, a = −1, v̄ = 5 → −0.83 ms`) is the realistic one,
  and it is sub-millisecond — below the resolution of every ground truth the paper proposes to measure against.
- *"Every event–RGB dataset (DSEC, MVSEC, DAVIS recordings, PKU-DAVIS-SOD, BS-ERGB) stores frames as
  `(image, t)`. There is no field for an interval. The exposure length is frequently not even recorded."*
  False for two of the five named: **DSEC ships `image_exposure_timestamps_left/right.txt` with start and end
  in µs** (the brief says so; I verified the files), and **DAVIS recordings in AEDAT4 carry exposure start and
  end per frame**. The paper's motivating claim about data formats is wrong about the two most relevant formats.
- *"`event camera` ∧ `censored` → 0 results"* as evidence of novelty. Absence of a keyword conjunction is weak,
  and in this case actively misleading: **EDFilter (CVPR 2026, C10)** encodes precisely an interval constraint
  between events (`sup |I_t − I_{t_{i-1}}| < C`), which is interval-censoring of the latent path by another
  name.

**6. Claims stronger than the evidence.** *"Real sensor, microsecond ground truth, no simulator, no labels. This
is our insurance against every ground-truth objection and should be run first."* It is microsecond-*resolution*
readout, not microsecond-accurate ground truth about the world. The distinction is the whole paper.

**7. Experiment a hostile reviewer demands.** Take one real sequence, sweep the DVS bias settings (or, failing
hardware, sweep v2e's `--cutoff_hz` and `--refractory_period`), and show that the C1 crossing-time predictions
and the fitted temporal calibration are stable. If the "ground truth" moves when you change a bias current, it
is not ground truth. Absence is fatal.

**8. Ranked fixes.** (i) Rewrite the censoring taxonomy so events are *delayed and right-censored*, not exact;
this actually strengthens the survival-analysis framing, because the machinery handles it. (ii) Replace the
physically unreachable `Δt` example with one drawn from a real dataset's measured `(a, T, v̄)` distribution.
(iii) Correct the data-format claim — DSEC and AEDAT4 both record exposure intervals. (iv) Drop keyword-count
novelty arguments and engage EDFilter and C1 directly. (v) Run the Time Lens → RVT head-to-head first, as the
team's own verdict says.

---

### Team 08 — *Right Place, Wrong Time*

**1. Verdict.** ACCEPT. This is my winner; see below.

**2. Summary.** Names the *Instantaneous-State Assumption* — that both prediction and ground truth are states
at a single instant — and shows it is false in every event benchmark examined, with the ground-truth clock
documented case by case (1 Mpx: a commercial detector on a 60 fps GoPro warped by homography; GEN1: humans
annotating ATIS grey-level images whose pixels integrate over intensity-dependent intervals; DSEC-Det: QDTrack
on 20 Hz RGB with **linearly interpolated** inter-frame labels; DSEC-3DOD: linear interpolation of 10 FPS
LiDAR boxes refined against VFI-synthesised sensor data). It then decomposes matched-pair localisation error
into a component perpendicular to the GT track's tangent (pixels, genuine spatial error) and one parallel to
it, converted to milliseconds by dividing by GT speed, and reports the triple `(AP, τ̂, AP^⟂)` plus the
anisotropy control `R = (AP^⟂ − AP)/(AP^iso − AP)`. It proposes no method, trains nothing, and derives its
relaxation budget `τ_max = (w_G + w_P)/2` from the benchmark's and method's own declared supports rather than
tuning it.

**3. Strongest reason to accept.** Judged by the brief's stated criterion, this is the only idea that is
*certain* to produce real figures. E0 — the label forensics — needs a 4.7 MB label file, zero GPU, and two days,
and it produces a quotable sentence either way: "the inter-frame ground truth of the two flagship low-latency
event benchmarks is, to within X % IoU, its own interpolation prior." The rest is inference-only on checkpoints
whose URLs and byte sizes were verified by HTTP HEAD, on preprocessed tarballs shared by two model families
(RVT and S5-ViT-B, which is C2 in my comparison set — it links the identical `gen1.tar`/`gen4.tar`), so there
is no preprocessing degree of freedom for a reviewer to attack. And its diagnosis of the ground truth is
independently confirmed by my comparison set: C4 (Ev-3DOD, CVPR 2025) states in its own text that the
advertised 100 FPS GT is linear interpolation plus expert refinement on VFI-synthesised data. The paper is not
speculating about the label pipeline; it is quoting it.

From my specialism, the decisive point in its favour is a negative one: **it makes almost no sensor-physics
claims and therefore gets almost none of them wrong.** In a set where six of ten ideas rest on a premise about
the DVS front end that is false or over-idealised, that is not a small thing.

**4. Strongest reason to reject.** Its own fairness guarantee destroys its headline result. §E1's argument for
using RVT and S5-ViT together is that "`uzh-rpg/ssms_event_cameras` **consumes the identical preprocessed
tarballs as RVT** … one data pipeline, zero re-implementation." But the temporal support `w_P` is a property of
that preprocessing: `stacked_histogram_dt=50_nbins=10`, with the window ending at the label time (verified in
the brief from `preprocess_dataset.py:405`). If every method on Gen1 and 1 Mpx consumes the same 50 ms
representation, then `w_P` is **identical across all five model configurations by construction**, and `c_P` is
identical too. The method-level component of `τ̂` — the thing the paper needs for its pre-registered ranking
flip (P6) and for its C3 discriminator between "we measured the dataset" and "we measured the models" — is
therefore designed out of the primary experiment. The paper's Death 3 identifies the risk and its proposed
discriminator is "if `τ̂` tracks each method's declared window width, it is the method" — but on its own
primary datasets, no two methods have different declared window widths.

**5. Factual errors.** I found no outright factual error, which is itself notable. Three items to correct:
- *"for a uniform event rate the information centroid of the input is `t − 25 ms`."* The premise "uniform event
  rate" is false: event rate within a 50 ms window is driven by `|∇L·v|` and is bursty in both time and space,
  and it saturates under refractory. The brief already warns that the network's bin weighting is unmeasured.
  Keep 25 ms as a reference point, as the team does, but the *uniformity* assumption should be checked directly
  by histogramming events per bin over the test set — a five-minute computation on the preprocessed tarballs.
- *"Representations with a constant event count have a temporal support whose width is a function of scene
  activity. Faster motion → more events → shorter window."* The first clause is right; the second is only
  monotone up to the rate ceiling. ESVA (CVPR 2026) derives and measures that event rate is **non-monotone**
  in blur, and the refractory rate law caps it. Past the ceiling, faster motion does *not* shorten the window,
  and `w_P(v)` turns around. That makes the confound the team names *worse*, not weaker — it should be stated
  as non-monotone.
- *"MVSEC is documented in the flow literature as lacking temporal synchronization with the ground truth"* —
  attribute it to a specific source or drop it.

**6. Claims stronger than the evidence.**
- *"P1: `τ̂` for RVT-{T,S,B} on 1 Mpx lies in **[−35, −10] ms**."* Pre-registered, which is the right posture,
  but derived from the uniform-rate assumption above. If the true bin weighting is end-loaded (which burstiness
  under ego-motion makes likely), the prediction is wrong in a way the paper would have to report as a miss.
- *"P6: at least one pair … swaps order."* See the fairness-guarantee objection: on the primary datasets, the
  most likely outcome is that all methods share `τ̂` and nothing flips.
- *"25–50 ms — one to three object diameters at automotive speeds."* An object diameter at 50 ms requires
  ~1 px/ms of image motion for a 50 px box; state the speed distribution rather than asserting the ratio.

**7. Experiment a hostile reviewer demands.** The isotropic null. If `R ≈ 0.5`, `AP^⟂` is just loosened IoU and
the whole decomposition is vacuous. The team specifies it as control C1 and commits to reporting the metric as
vacuous if it fails. That is exactly right, and its presence is why this idea gets an ACCEPT rather than a
BORDERLINE. Absence would be fatal.

**8. Ranked fixes.** (i) Fix the `w_P` collapse: add at least one method family with a *genuinely different*
declared support — a constant-event-count representation, or S5-ViT evaluated at a different inference frequency
(C2's whole selling point is that it can be, which makes it a free within-checkpoint support manipulation), or
DAGr's inter-frame sawtooth (E3), which is the one place a method-level `τ̂` signature actually exists. (ii)
Histogram events per bin to replace the uniform-rate assumption with a measured centroid. (iii) Restate the
constant-count support-width claim as non-monotone in speed, citing the rate ceiling. (iv) Run E0 first and
independently, as planned; it is the paper's floor. (v) Re-run the prior-art survey on the along-track/latency
literature before anything else, since the search budget died mid-survey and the algebra is admittedly borrowed.

---

### Team 09 — *Change-Time: Per-Pixel Clocks*

**1. Verdict.** **REJECT.** Fatal to the headline claim as stated; pillar 2 is salvageable.

**2. Summary.** Argues the second is the wrong unit for an event stream and replaces the global time axis with
a per-pixel counting clock `τ(x,t) = C·N(x,t)`, claimed to be the total variation of the quantised log-intensity
path — an arc-length parameterisation with no free parameters, **exactly** invariant (bit-for-bit) to any
strictly increasing reparameterisation `φ` of time. From this it derives that the event stream is a *complete*
observation with an `O(C)` error bound independent of speed, that a static pixel's time is *undefined* rather
than merely unobserved, and that the RGB frame's temporal support is a measured per-pixel width
`W(x) = C·N_exp(x)` which is exactly zero on static pixels, yielding a fusion weight `1/W(x)` derived from the
sensor model rather than learned. Its make-or-break experiment is a speed-ratio sweep predicting that ASTW
(CVPR 2026) tracks it to `ρ ≈ 25` and then breaks, the elbow computed in advance from ASTW's own clamp
hyperparameters.

**3. Strongest reason to accept.** This is by a distance the best sensor-physics *reading* in the set. It is the
only team that notices that recorded event timestamps are already corrupted — AER bus saturation perturbing
send times, rate-dependently, worst under fast motion — and it correctly turns what would be the fatal
objection ("sensor time is a measurement, not a gauge") into motivation. Its `β`-is-the-window identity, read
from released code (DAGr `time_window = 1e6` µs ⇒ `β = 10⁻⁶`; AEGNN `beta=0.5e-5` with `torch.min(ts)` as
window origin; EFGCN's `t*_i = ⌊β·t_i/T⌋`) is code-level evidence rather than rhetoric, and it correctly
identifies that "grid-free" graph methods are not "timeline-free."

**4. Strongest reason to reject.** The reformulation contradicts the physics that motivates it, and the
contradiction is load-bearing.

- **`τ = C·N` is not arc length on a real sensor.** (i) *Refractory:* crossings occurring during dead time are
  never emitted, so `N` under-counts the true excursion, and the under-count is rate-dependent — the exact
  effect the paper quotes from the field survey ("the larger the refractory period the fewer events are
  produced by fast moving objects") as motivation. (ii) *Threshold:* `C` is per-pixel, illumination-dependent,
  polarity-asymmetric and bias-dependent. `τ(x,·)` therefore carries an unknown per-pixel gain, so the "τ-cut"
  — the iso-change surface that is the paper's genuinely new operator, "every pixel after it has changed by the
  same amount" — compares `C_x·N_x` to `C_y·N_y` with `C_x ≠ C_y`. It is not an iso-change surface; it is an
  iso-*count* surface with a spatially varying, unknown conversion to change. (iii) *Leak and shot noise:*
  both increment `N` with no corresponding log-intensity change, and in low light shot noise dominates — so
  `W(x) = C·N_exp(x)` is not zero on a static pixel in the dark, which destroys the paper's cleanest claim
  ("`W = 0` ⇒ the frame is a sharp, exact, instantaneous observation and the alignment cost is exactly zero")
  in precisely the regime (long exposure = low light) where long exposures exist. On DSEC, the six sequences
  with 14996 µs exposures are the dark ones.
- **The invariance is invariance to a transformation the world does not apply.** Playing a scene `k×` faster
  does *not* produce `φ`-warped timestamps, because refractory dead time, photoreceptor bandwidth, and noise
  rates are fixed in seconds, not in scene time. The paper concedes this in one sentence ("a warp does not
  reproduce sensor-level rate effects") — but Stage 1, its entire "real data, zero-cost speed perturbation"
  strand, is built on it, and `RIG = 0` then becomes a tautology about the team's own preprocessing rather
  than a property of anything physical. A reviewer will phrase this as: *you proved your representation is
  invariant to an operation you defined.*

**5. Factual errors.**
- **The make-or-break number is wrong.** P3's elbow at `ρ ≈ 25` is derived from "ASTW uses
  `Δt = clamp(γ/D̄, Δt_min, Δt_max)` with tuned `Δt_min = 10 ms`, `Δt_max = 250 ms` — a hard dynamic range of
  25:1." I read the ASTW PDF (C8). Its clamp-sensitivity table tests `(Δt_min, Δt_max)` ∈
  **{(25, 200), (50, 150), (50, 200), (75, 150)}** with mAP {49.6, 47.8, 48.7, 48.8} — ratios of **8, 3, 4 and
  2**, not 25. The 250 ms figure in the ASTW paper is `Δt_ref`, the *reference* window used for density
  estimation (its own sensitivity table sweeps 50/100/250/500/750), not `Δt_max`. Team 09 has conflated
  `Δt_ref` with `Δt_max`. The pre-registered elbow is therefore off by roughly a factor of 3–12, and it lands
  inside the range where the same paper predicts ASTW is flat (`≤ +5 % for ρ ≤ 16`). Their single decisive
  prediction, and the thing they present as its greatest virtue ("predicted from their published
  hyperparameter table, not fitted"), is wrong at the source.
- **A second misread of the same paper.** "Their own Table 5 shows patch size 1 is worse than 4 (49.9 vs
  50.6)." Table 5 is the patch-size table (sizes 1/2/4/8/16/32/64); the numbers 49.6/47.8/48.7/48.8 belong to
  the clamp table. Quote the right cells. (The `−1.2 mAP` for removing causal consistency and `−4.0` for
  removing patch division **are** correct — verified.)
- **FE108 is not dead.** "~~FE240hz / FE108~~ … **DEAD: host `fe108.dluticcd.com` refused connection.**" The
  dataset lives at `zhangjiqing.com/dataset/`, which returns HTTP 200 and carries the download link
  ("Application for Access for Non-Commercial Use"), the aedat4 loading instructions, and the FE240hz
  announcement (143,181 frames). One dead vanity domain is not a dead dataset, and this error, if propagated,
  would have removed the set's only intra-exposure-GT resource from three other teams' plans.
- *"`temporal support` + `event camera` returns zero arXiv abstracts"* as pillar-1 evidence. Keyword absence is
  not conceptual absence: EDFilter (C10) and TimeTracker (C5) both address the substance.

**6. Claims stronger than the evidence.**
- *"exactly invariant … not robust, not approximately: identical bit-for-bit"* and *"`P7`: RIG for our invariant
  branch **exactly 0**, to float precision."* True of the representation, uninformative about the sensor.
- *"`W(x) = 0` ⇒ … the alignment cost must be exactly zero — while every current method still pays it."* False
  in the dark, where leak and shot noise make `N_exp > 0` on genuinely static pixels.
- *"the sensor is not lossy; the coordinate is."* This is the paper's most quotable line and it is the one
  refractory falsifies most directly.

**7. Experiment a hostile reviewer demands.** Take a real recording, sweep the DVS refractory bias, and show
`N(x, t)` and hence `τ(x, ·)` is stable. It will not be — that is the point of the bias — and the honest
version of this paper reports the *sensitivity of `τ` to bias settings* as a first-class result rather than
claiming zero free parameters. Absence is fatal to "zero free parameters."

**8. Ranked fixes.** (i) Re-derive the P3 elbow from ASTW's actual clamp table (ratios 2–8) and re-plan the
sweep; the prediction may still hold, but the number must be right. (ii) Replace "zero free parameters" with an
explicit per-pixel `C_x` nuisance and show what the τ-cut means when `C_x` varies. (iii) Model refractory
explicitly in `N`, or restrict the arc-length claim to a stated rate regime. (iv) Drop the Stage-1 warp as
evidence for invariance and keep it only as an ablation instrument. (v) Correct the FE108 status, and tell the
other teams.

---

### Team 10 — *Fusion Is Ill-Typed*

**1. Verdict.** BORDERLINE.

**2. Summary.** Types every measurement as `(φ, μ, κ, π)` — photometric domain, signed temporal measure,
spatial trajectory reference, per-pixel offset — and observes that a frame is `∫ e^L dμ_F` with `μ_F` a
probability measure applied in the linear domain, while an event bin is `∫ L dμ_b` with `μ_b` a **mass-zero**
signed measure on two instants applied in the log domain; hence no shift, scale or warp maps one to the other
(Prop. 1) and every concat/gate/cross-attention mixes different observables rather than misaligned ones. It
proposes typing rules (mixing legal only within equal `φ` and equal order; all cross-type interaction must
factor as `render ∘ lift`), a diagnostic suite (event utility vs speed; off-support attention mass computed via
Jacobian influence so it applies to non-attention mixers; a support-inconsistency index), a support-identifiability
null space `N` with `dim N = max(0, d − B − 1)`, and a null-space regulariser forbidding decisions along
directions the measurements cannot see.

**3. Strongest reason to accept.** The Jacobian-influence form of OSAM is the right engineering call — it makes
the diagnostic applicable to AdaIN and gated mixers, not just attention — and the cross-model audit posture
("we propose no method; the operator gets ≤1.5 pages and does not win on average") is the correct answer to the
"this is a new fusion module" prohibition. `dim N = d − B − 1` as a *design rule* ("this task at this speed
needs ≥ B* bins, and shipped configurations under-provision") is a genuinely actionable output.

**4. Strongest reason to reject.** Proposition 1 is a statement about the *ideal* event model, and the paper
treats it as a statement about the measurement. The mass-zero property comes from
`V_b ≈ (1/C)(L(a_{b+1}) − L(a_b))` — the telescoping polarity sum. On a real sensor the polarity sum over a bin
is *not* a boundary difference: refractory dead time drops crossings inside the bin (so the sum under-counts,
rate-dependently), `C` differs per pixel and between polarities (so the sum is a weighted, asymmetric count),
leak events add a monotone drift, and shot noise adds a zero-mean but heavy-tailed term. The measured `V_b` is
a biased, lossy functional of the whole interval — not a mass-zero boundary difference. So the "orders differ
(0 vs 1)" claim, which is the load-bearing distinction between this paper and the change-of-support literature
it imports from, is an artefact of the idealisation.

Second, the headline diagnostic is confounded and no control is proposed. `EU(s)` — event utility falling at
high `s` — is exactly what refractory-limited event generation predicts *without any architectural type error*:
at high speed the event branch delivers fewer crossings per moving edge, so dropping it costs less. ESVA
(CVPR 2026) makes this concrete by deriving and measuring a non-monotone event-rate curve. To attribute the
`EU` inversion to ill-typed mixing rather than to event starvation, the paper must hold *emitted event count
per moving edge* fixed while varying `s`, and it currently does not.

**5. Factual errors.**
- *"x: `s ∈ [0.25, 16]` px (log)"* on DSEC, with `s = ‖v̄‖·T` and `T` from the exposure files. I measured `T`:
  medians 0.30–1.87 ms in the twelve non-saturated sequences. `s = 16 px` there needs `v̄ ≈ 8.5–53 px/ms`, i.e.
  8500–53 000 px/s. The upper half of the stated `s` range is unreachable on DSEC daytime; the only way to get
  it is the six sequences pinned at 14996 µs, which are dark and where the event branch is bandwidth-limited.
  The axis must be re-derived from the measured `(T, v)` joint distribution.
- *"DSEC's exposure timestamps show `T` varying frame to frame (auto-exposure across tunnels, shade, sun)."*
  True for 12 of 18 sequences. In six, `T` is **constant at 14996 µs for every frame** — auto-exposure pinned
  at its ceiling. Panel C ("per-frame error correlates with `T·‖v̄‖` after controlling for `‖v̄‖`") has no `T`
  variance to exploit in exactly the sequences where `T` is large. State the split.
- *"a rolling-shutter frame is a field of types `π(x)` spanning 10–30 ms across rows."* None of the datasets in
  the plan has rolling shutter: DAVIS APS is global shutter, and DSEC's FLIR Blackfly S frame cameras are
  global shutter. The `π` component of the type is sim-only or Gev-RS-only, and the paper should say so as
  plainly as Team 01 does.
- *"Support-blind pairs (constructive witness) … a bar that goes right-then-left versus left-then-right within
  the bin. **Every published model maps this pair to one input point and emits one confident answer for two
  different worlds.**"* This construction is the opening figure of **TSANet, CVPR 2026 (C9)** — four
  intra-exposure motion patterns producing an identical blurred frame, with the events shown as the
  disambiguating cue — published, illustrated, and used for the same purpose. The team's "cannot fail" fallback
  (Death 2) is therefore a re-demonstration of an accepted CVPR 2026 figure.

**6. Claims stronger than the evidence.**
- *"Perfect temporal and spatial registration leaves the two quantities as different observables. Alignment is
  orthogonal to the defect."* True of the measures; a non sequitur about the *features*. No fusion paper claims
  its two feature tensors are the same measure; the claim is that both are informative about a shared latent.
  Prop. 1 does not indict that, and a reviewer will say so in one sentence.
- *"OSAM(s) ≈ 1 − r/(r+s): from 0.12 ± 0.03 at s = 0.5 px to 0.83 ± 0.05 at s = 12 px"* — quoted to two decimal
  places with error bars, entirely un-run.
- *"Fine-tune each model on the high-`s` regime … **OSAM falls by < 0.08 absolute**."* Same.

**7. Experiment a hostile reviewer demands.** The event-starvation control: hold emitted events per moving edge
fixed (by adjusting contrast or threshold as speed rises) and re-measure `EU(s)`. If the inversion survives, the
paper stands. If it does not, the headline is a sensor curve. Absence is fatal to Panel A.

**8. Ranked fixes.** (i) Add the event-starvation control to Panel A. (ii) Re-derive the `s` axis from the
measured DSEC `(T, v)` joint distribution and stop claiming 16 px. (iii) Restate Prop. 1 as an algebraic
property of the ideal model and add the real-sensor corrections that break "order 0 vs 1." (iv) Cite TSANet for
the support-blind construction and re-lead with the null-space *certificate*, which TSANet does not produce.
(v) Mark `π` (rolling shutter) as sim-only, as Team 01 does.

---

## Physical-premise audit

*The section only I can write. For each idea, the sensor-physics assumptions it makes, marked
**TRUE / APPROXIMATELY TRUE / FALSE**, with the mechanism.*

### Premises shared across several ideas (audited once)

| Premise | Who relies on it | Verdict | Mechanism |
|---|---|---|---|
| A blurred frame is `(1/T)∫ I dt`, a linear-domain integral over the exposure | 01, 02, 03, 04, 05, 06, 07, 09, 10 | **TRUE** | This is what a photodiode does. Global-shutter CMOS and DAVIS APS both integrate photocurrent over the exposure. Safe for all ten. |
| `log B = L(t_mid)` (frame as a log-domain point sample) | assumed by the *baselines* under attack; **denied** by 06, 07, 10 | **FALSE**, and 06/07/10 are right to deny it | Jensen: `log(mean of exp) ≥ mean of log`, gap `= ½Var_W(L) + O(κ₃)` exactly. Team 06's closed form is correct. |
| Events are the derivative of log intensity: `ΔL = c·E` | 01 (`L_cm`), 03 (`L_ren`), 06 (the object of attack), 07 (L1), 09 (`τ = C·N`), 10 (`V_b`) | **APPROXIMATELY TRUE, and it degrades exactly where these papers work** | Valid only (i) within the photoreceptor's flat band, (ii) above threshold, (iii) with dead time short vs the crossing interval, (iv) with `c` known. All four fail under fast motion or low light. |
| The contrast threshold `C` is a known constant | 06 ("parameter-free" predictor), 09 (`τ = C·N`, "zero free parameters"), 10 (`V_b = (1/C)ΔL`) | **FALSE** | `C` has per-pixel fixed-pattern mismatch (a few percent contrast at the device level; 10–15 % effective spread reported in per-pixel calibration work), varies with illumination, bias currents and temperature, is **polarity-asymmetric** (ON/OFF biases are independent), and its *effective* value rises with event rate under refractory. It is the single worst-behaved parameter in the sensor and three ideas assume it away. C3 (TTA-EVF, CVPR 2024) is accepted partly *because* "event data distribution undergoes substantial variations based on camera settings." |
| Event timestamps are exact (µs) times of the physical change | **07 (load-bearing)**, 01, 04, 08 (mildly) | **FALSE** | Three mechanisms: photoreceptor latency scaling inversely with photocurrent (illumination-dependent, and the entire subject of C1, CVPR 2024); refractory dead time censoring crossings; AER arbitration timestamping at readout under bus load. Team 09 is the only team that says so. |
| Event count is monotone in speed / in blur | 03 ("event counts matched by construction"), 09 (`N` as arc length), 10 (`EU(s)`), 08 (constant-count support width) | **FALSE** | Rate compression `r = 1/(T₀ + Δ_refr)` caps and then reverses the relation; ESVA (CVPR 2026) derives and measures a rise-then-fall event-rate curve vs blur. |
| The inter-event interval is a clean measurement of the information support | **03 (load-bearing: "free real GT")** | **APPROXIMATELY TRUE at best** | Censored below by `Δ_refr`, inflated by leak events (which fire with no scene change), corrupted by shot noise in low light, and perturbed at the top by arbitration. EDFilter (C10, CVPR 2026) treats the same interval correctly, as a *constraint* (`sup|ΔI| < C`) inside a stochastic model, not as a label. |
| A speed change is a monotone warp of the recorded timestamps | **09 (Stage 1, load-bearing)**, 08 (mildly) | **FALSE** | Refractory, bandwidth, leak rate and noise rate are fixed in seconds, not in scene time. Warping recorded timestamps changes the *representation's* input without changing any sensor effect, so invariance to it is a statement about preprocessing. |
| Frames and events are co-located (same aperture) | **06 (DSEC anchor)**, 05 (DSEC), 10 (DSEC), 01 (DSEC) | **FALSE on DSEC, TRUE on DAVIS** | DSEC pairs FLIR frame cameras with Prophesee Gen3.1 event cameras on a stereo rig; per-pixel event/frame correspondence is depth-dependent. Any *per-pixel* regression between a DSEC frame and DSEC events is confounded by disparity. DAVIS (FE108, REBlur) is co-located and is the right instrument for per-pixel claims. |
| Events can be measured *inside* an APS exposure without artefact | **01, 02, 04 (all rest on FE240hz/DAVIS346)** | **APPROXIMATELY TRUE at best** | On DAVIS the APS and DVS share a photodiode; APS reset/readout is a known source of frame-synchronous artefact events. The three ideas that most need intra-exposure event timing all plan to get it from the one sensor where that measurement is contaminated by the frame it is being compared to. None of them controls for it. |
| APS / DSEC frames are global shutter | 01 (states it), 10 (denies it implicitly via `π`), 04 | **TRUE** | DAVIS is a global-shutter APS by design (Brandli et al.'s DAVIS sensor is titled a global-shutter spatiotemporal vision sensor); DSEC uses global-shutter FLIR Blackfly S cameras. Consequence: **every rolling-shutter term in this idea set (01's `ρ̂`, 10's `π(x)`) is simulation-only.** Team 01 says so; Team 10 does not. |
| v2e / ESIM / DVS-Voltmeter reproduce the relevant non-idealities | 01, 02, 03, 04, 07, 08, 09, 10 | **06 is the only team that audited this, and its audit is correct** | v2e models threshold scatter, refractory, leak, shot noise and intensity-dependent bandwidth; **ESIM models only a Gaussian contrast threshold and explicitly does not model refractory-induced loss at high speed; DVS-Voltmeter has no refractory period.** So "cross-check on DVS-Voltmeter/ESIM" (03, 07, 09) is *not* a refractory control, and any speed-dependent claim validated only that way is unvalidated. |

### Per-idea premise ledger

**Team 01.** `B` determines path and dwell density only — **TRUE**. `(t₀, T)` absent from the normalised
integral — **TRUE** exactly. "The frame carries *no* information about `T`" — **APPROXIMATELY TRUE**;
photon-shot-noise scaling with `T` leaks a weak, scene-dependent signal. Left/right exposure windows are
"physically different integration windows" — **FALSE as an offset claim**: starts are bit-identical on 100 % of
frames, widths differ by 8–190 µs. DAVIS/DSEC global shutter, RS ablation sim-only — **TRUE**, and honestly
stated. Contrast maximisation identifies `(t̂₀, T̂)` within a 0.3–4 ms daytime exposure — **FALSE at real
densities**: ~1.1 crossings per firing pixel supports a per-sequence aggregate, not the per-frame estimate the
method needs.

**Team 02.** Prop 1, frames measure `Π_#μ` only — **TRUE**. Prop 2, events determine parametrisation only —
**TRUE in conclusion, FALSE in stated mechanism** (the obstruction to mass is the unknown `L(x,0)` / DC null,
not the threshold, which is a gain). Constant velocity ⇒ `A_mid = A_mean = A_mode` exactly — **TRUE** in the
image plane; note it is **FALSE on SO(3)**, which the team spots and uses as a fallback. Time-reversal
separation "at ~100 %" — **APPROXIMATELY TRUE in an ideal simulator, unquantified on a real sensor**: refractory
preferentially deletes the fast half of an asymmetric trajectory and the low-light bandwidth smears order.

**Team 03.** Frame pixel's effective support is narrower than the exposure and content-dependent — **TRUE**, and
the sharpest observation in the paper. Event pixel's support is the inter-event interval — **APPROXIMATELY
TRUE**, degraded as above. "No event ⇒ verifiably static for 40 ms" — **FALSE in low light**, where leak and
shot noise mean the absence of a signal event is not the absence of events, and **FALSE at low contrast**,
where `|ΔL| < C` is the only statement available and `C` is unknown. "Event counts matched by construction
between constant-velocity and dwell-then-dash" — **FALSE**; refractory dead time deletes events preferentially
in the dash. `K = 16` bins per pixel per branch identifiable — **FALSE**; 1.12 crossings per firing pixel.

**Team 04.** Frame is an integral, events are point evaluations — first half **TRUE**, second **FALSE** (see the
shared ledger). Evidence weight `w(t)` for the event branch ∝ local event rate — **TRUE**, and this is what
makes the *speed-independence* of `b` **FALSE**: event rate is not proportional to speed. `w(t)` for the frame
branch is content-dependent within the exposure — **TRUE**, and it contradicts the paper's own frame-only
control. 240 Hz Vicon can resolve a 2–5 ms `τ̂` — **FALSE**; 4.17 ms sampling.

**Team 05.** Box exposure ⇒ `sinc(πvTξ)` ⇒ exact zeros at `ξ = k/(vT)` — **TRUE**. Shift = unit-modulus
linear-phase multiplier, cannot fix a modulus mismatch — **TRUE**. Event channel is a first-order low-pass with
`τ = τ(Ī)` — **APPROXIMATELY TRUE**; the real front end is closer to a cascade with an intensity-dependent
dominant pole, and in the HDR scenes DSEC contains, `τ` varies by orders of magnitude across the image within
one frame. "The existing latency literature keeps only the first moment of the kernel" — **TRUE** and correctly
attributed to C1. Contrast inversion past the first null is a signed systematic error invisible to PSNR —
**TRUE**. `b = vT ≥ 2 px` reachable on DSEC — **FALSE for the daytime sequences** (median `T` 0.3–1.9 ms), and
the sequences with wide `T` are dark, where `w_E` is no longer narrow.

**Team 06.** `log B = LME_W(L)`, `J = ½Var_W(L) + O(κ₃)` — **TRUE**, exactly. `J` exists for a perfect sensor —
**TRUE**, and this is the paper's real contribution. The residual is a spatial dipole with zero global mean —
**TRUE** in their simulation and a plausible explanation for why nobody plotted it. The predictor `P` is
parameter-free — **FALSE**; it is a function of `c`, and LME's nonlinearity prevents `c` from cancelling.
`φ` (normalised cumulative event profile) is first-order invariant to threshold scale — **TRUE** for a scale
perturbation, **FALSE for a polarity-asymmetric one** (a differential ON/OFF shift changes the cumulative
profile's shape, not just its gain), which is the common case and is not in their perturbation table. "Blur
identifies `c_p`, and conditioning improves with motion" — **FALSE on a real sensor**: `G` recovers
`a_p = c_p·E_p`, and `E_p` degrades with motion faster than `G`'s conditioning improves.

**Team 07.** "An event is an **exact**, uncensored observation of a crossing time" — **FALSE**, three
independent mechanisms, and it is load-bearing for `L_exact`, for the C1 anchor, and for the entire
censoring taxonomy. "Held-out real events are microsecond ground truth" — **FALSE**; they are the sensor's
readout schedule under load. "A frame is interval-censored on `[a, a+T]`" — **TRUE**. `L4` (blurred pixel is a
dwell-weighted average over intensity levels, so `∂τ/∂L` is observed) — **TRUE** for a monotone segment; the
non-monotone case, which is the paper's own motivating example (direction reversal), breaks the change of
variables. `∇_u τ · v = 1` — **TRUE** where brightness constancy holds; **FALSE at occlusion boundaries and
under illumination change**, which the paper masks for. Exposure length "frequently not even recorded" —
**FALSE** for DSEC and for AEDAT4 DAVIS recordings.

**Team 08.** Constant-count representations have activity-dependent support width — **TRUE**; monotone in speed
— **FALSE** (rate ceiling). Uniform event rate within a 50 ms window ⇒ centroid at `t − 25 ms` — **FALSE as a
premise, and the team labels it a reference point** rather than a prediction, which is the correct handling.
GEN1's grey-level images have per-pixel intensity-dependent integration windows — **TRUE**, and it is the
sharpest sensor observation in the paper: the ATIS exposure-measurement pixel integrates to a fixed charge, so
the "image" an annotator saw genuinely has no single timestamp and its per-pixel support is illumination
dependent. Everything else in the paper is about labels and metrics, where there is no sensor premise to get
wrong. **This idea has the smallest physical attack surface in the set.**

**Team 09.** AER bus saturation perturbs recorded timestamps, rate-dependently — **TRUE**, and no other team
notices. Refractory reduces events from fast objects — **TRUE**. `τ(x,t) = C·N(x,t)` is the total variation of
the quantised log-intensity path — **FALSE**, by refractory (under-count), leak/shot (over-count), and per-pixel
`C` (unknown gain). Zero free parameters — **FALSE**; `C` is per-pixel and bias-dependent. `W(x) = 0` on static
pixels ⇒ frame is an exact instantaneous observation there — **FALSE in low light**, where leak and shot noise
give `N_exp > 0` on static pixels, and low light is where wide exposures live. A `k×` speed change is a monotone
warp — **FALSE**. Exact bit-for-bit invariance to `φ` — **TRUE of the representation, vacuous about the world.**

**Team 10.** `μ_F` is a probability measure in the linear domain; `μ_b` is a mass-zero signed measure in the log
domain — **TRUE of the ideal models, FALSE of the measurements**: a real polarity sum over a bin is a biased,
lossy, per-pixel-scaled, polarity-asymmetric count, not a boundary difference, so the "order 0 vs order 1"
distinction that carries the paper is an artefact of idealisation. No shift/scale/warp maps one to the other —
**TRUE**, trivially, and about measures rather than features. Event support is "itself uncertain and biased"
(their §*What existing methods cannot express*, item 2) — **TRUE**, and it is the one place the paper
acknowledges the sensor; it should be promoted, because it is precisely what undermines Prop. 1's use.
`s = ‖v̄‖·T ∈ [0.25, 16] px` reachable on DSEC — **FALSE** above ~2–4 px in the daytime sequences. Rolling
shutter present in the plan's data — **FALSE** (all global shutter except Gev-RS).

---

## Ranking

1. **Team 08 — Right Place, Wrong Time.** The only idea whose figures are guaranteed: zero training, verified
   checkpoints, and a zero-GPU label-forensics experiment that produces a quotable number either way. It also
   makes the fewest physical claims and therefore gets the fewest wrong.
2. **Team 06 — The Exposure Gap.** The only team that ran its own measurement before writing, with a correct
   closed form (`J = ½Var_W(L)`), a noise null, and the field's only honest simulator-capability audit. Loses
   the top spot on the `c`-dependence of its "parameter-free" predictor and a real-data anchor (DSEC) that is
   the wrong instrument for a per-pixel regression.
3. **Team 05 — No Offset Can Fix a Width.** Textbook-correct physics, an impossibility bound rather than an
   empirical hope, and a load-bearing experiment that runs on CPU in days with the opponent given every
   advantage. Third because the real-data half is genuinely thin: `b < 1 px` on DSEC daytime, and the wide-`T`
   sequences are dark, where its own `w_E` model weakens.
4. **Team 01 — A Frame Is Not a Timestamp.** Correct central proposition, cheapest possible headline figure
   (~10 GPU-h of inference on other people's checkpoints), and a free real validation signal. Fourth because
   one of its Fig-1a predictions is falsified by the data by an order of magnitude, and its money plot needs
   intra-exposure event timing on the one sensor where that measurement is self-contaminated.
5. **Team 04 — When Is Your Prediction?** Best-engineered pilot in the set (3 days, no downloads, no SuperSloMo
   dependency) and a genuinely simple, apparently unrun primitive. Fifth because the paper's own most important
   control is predicted wrong by the paper's own theory, and its key law (`b` independent of `v`) is false once
   the event branch obeys a rate ceiling.
6. **Team 02 — Exposure-Occupancy Measures.** Correct propositions and a real evaluation contribution
   (convention latent + conformal coverage), but its designated proof-not-a-benchmark-delta is the opening
   figure of an accepted CVPR 2026 paper, and its Prop. 2 mechanism is wrong.
7. **Team 10 — Fusion Is Ill-Typed.** Good diagnostic engineering and the right posture on the no-new-fusion
   constraint, but its central proposition is true of an idealisation the sensor does not obey, its headline
   curve has an uncontrolled sensor confound, and its `s` axis is unreachable on the data it names.
8. **Team 03 — Temporal Support Fields.** The most appealing *idea* of the rejected three — sub-probability mass
   as a licence to abstain is a real gap — but its matched-pair design is falsified by refractory and its
   predicted object needs 16 bins where the sensor delivers 1.1 crossings.
9. **Team 09 — Change-Time.** The best sensor-physics reading in the set, deployed in service of a
   reformulation that the same physics falsifies, with a make-or-break number I verified wrong at the source
   and a dataset declared dead that is alive.
10. **Team 07 — Chronofields.** Last because the single premise this specialism exists to test — that an event
    is an exact time observation — is false, load-bearing, contradicted by an accepted CVPR 2024 paper, and
    fatal to the very experiment designated as insurance against all other objections; and its flagship
    numerical example is drawn from a physically unreachable configuration.

---

## My winner and its fatal flaw

**Winner: Team 08 — *Right Place, Wrong Time*.**

I would advance it, and I am aware that from a sensor-physics chair this is a slightly perverse choice: it is
the idea with the least event-camera physics in it. That is exactly why. Six of the other nine rest on a
premise about the DVS front end that is false or over-idealised — a known constant threshold, an exact
timestamp, an event count monotone in speed, a clean inter-event interval, an invariance to a warp the world
does not apply. Team 08 makes almost none of those claims. It re-scores other people's checkpoints against
other people's labels, with an anisotropy null that it commits in advance to reporting as vacuous if it fails,
a relaxation budget derived from the benchmark's and method's own published specifications rather than tuned,
and a pre-registered prediction of `τ̂` from declared architecture. It trains nothing, needs ~35 GPU-hours
under 9 GB, and its most damaging experiment — E0, showing that the inter-frame ground truth of the two
flagship low-latency event benchmarks is, to within some measured IoU, its own linear-interpolation prior —
needs a 4.7 MB label file and no GPU at all. Under the brief's own criterion ("an idea that is beautiful and
unfinishable is worth less than one that is merely good and certain to produce a real figure"), nothing else
is close. Its diagnosis is also independently corroborated by my comparison set: Ev-3DOD (C4, CVPR 2025
Highlight) states in its own text that its 100 FPS ground truth is linear interpolation plus expert refinement
on video-frame-interpolated sensor data.

**The one thing most likely to kill it: its fairness guarantee and its headline result are the same design
decision, and they cancel.**

§E1 justifies pairing RVT with S5-ViT-B on the grounds that `ssms_event_cameras` "consumes the identical
preprocessed tarballs as RVT … one data pipeline, zero re-implementation. There is no preprocessing degree of
freedom for a reviewer to attack." True — and the temporal support `w_P` *is* that preprocessing:
`stacked_histogram_dt=50_nbins=10`, window ending at the label time. If every model on Gen1 and 1 Mpx consumes
the same 50 ms representation, then `w_P`, and hence `c_P`, and hence the architecture-predicted `τ̂`, are
**identical across all five model configurations by construction.** The method-level component of `τ̂` — which
the paper needs for its pre-registered ranking flip (P6) and for control C3, its only discriminator between
"we measured the models" and "we measured the dataset" — has been designed out of the primary experiment. The
paper's own Death 3 anticipates the outcome but not the cause: it proposes to discriminate by checking whether
`τ̂` tracks each method's declared window width, and on its primary datasets no two methods have different
declared window widths. The most likely result is a single shared `τ̂ ≈ −25 ms` on Gen1 and 1 Mpx, no flip, and
a paper that has measured two datasets rather than eight methods.

It is fixable, and cheaply, which is why I still advance it: the paper needs at least one axis along which
`w_P` genuinely varies. Three are already sitting in its own materials. **S5-ViT is the obvious one** — the
entire selling point of C2 (State Space Models for Event Cameras, CVPR 2024) is that its learnable timescale
lets one checkpoint be deployed at inference frequencies it was not trained at, with a 3.31 mAP average drop
where RVT drops 21.25. Evaluating the *same* S5 checkpoint at 20/40/80/100/200 Hz is a free, within-checkpoint
support manipulation with a published robustness curve to compare against, and `τ̂` must move with it or the
estimator is not measuring what the paper says it measures. **DAGr's inter-frame sawtooth (E3)** is the second:
`τ̂(t)` rising across the 50 ms inter-frame interval and resetting at each RGB frame is a signature no spatial
explanation can produce, and DAGr already ships the script that dumps those detections. **BFlow `E` vs `E+I`
(E2)** is the third and the most on-topic for the seed. Those three, not the Gen1 leaderboard, are where this
paper's result lives — and E2 and E3 are jointly about seven GPU-hours.

