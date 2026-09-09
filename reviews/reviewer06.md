# Reviewer 06 — motion deblurring, frame interpolation, event-guided restoration

*Specialism: EDI/mEDI, Time Lens / Time Lens++, REFID / unknown-exposure deblurring, EBFI-BE,
E-CIR, EVDI, UniINR, EvShutter/EvUnroll, TbD / TbD-3D / DeFMO / Motion-from-Blur, Exposure
Trajectory Recovery, and the blur formation model in every published variant.*

I am the reviewer who says **"this is deblurring with new words."** Below I press that objection
on all ten, and where a team has genuinely answered it I say so and defend them.

---

## Comparison set

Fetched and checked this session (arXiv metadata; venue strings taken verbatim from each entry's
`comment` / `journal_ref`). WebSearch was unavailable — the session's 200-call budget was already
exhausted by the idea teams — so everything below was retrieved through the arXiv API and is
reported with its stated venue.

**Accepted CVPR / ICCV / ECCV / NeurIPS 2024–2026 (the required set):**

| # | Title | Venue / Year | arXiv | Contribution |
|---|---|---|---|---|
| 1 | **Mitigating Motion Blur in Neural Radiance Fields with Events and Frames** (Ev-DeblurNeRF) — Cannici & Scaramuzza | **CVPR 2024** | 2403.19780 | Explicit blur-formation model (exposure integral) combined with a *learned adaptive event-pixel response*, i.e. the contrast threshold and per-pixel response are estimated rather than assumed, inside a NeRF. Directly relevant: this is a 2024 paper that already treats the frame as an exposure integral **and** the event threshold as an unknown to be fit. |
| 2 | **UniINR: Event-guided Unified Rolling Shutter Correction, Deblurring, and Interpolation** — Lu, Liang, Wang, Wang, Xiong | **ECCV 2024** | 2305.15078 | Single spatio-temporal implicit representation queried by `(x,y,t)`, with **the exposure interval embedded into the query**, solving RS correction + deblur + VFI jointly with a small parameter count. This is the strongest existing precedent that "exposure is an input variable, and temporal support varies spatially." |
| 3 | **Deblur e-NeRF: NeRF from Motion-Blurred Events under High-speed or Low-light Conditions** — Low & Lee | **ECCV 2024** | 2409.17988 | Physically grounded **pixel-bandwidth** model of *event* motion blur (the photoreceptor low-pass), plus a regularizer, showing that the event stream itself has a finite temporal support that matters at speed. |
| 4 | **Towards Real-world Event-guided Low-light Video Enhancement and Deblurring** (ELEDNet) — Kim, Jeong, Cho, Jeong, Yoon | **ECCV 2024** | 2408.14916 | End-to-end joint low-light enhancement + deblurring with a real-captured beam-splitter dataset; cross-modal modules with explicit event-noise suppression. The reference point for "events help most exactly where the frame is worst." |
| 5 | **PPLNs: Parametric Piecewise Linear Networks for Event-Based Temporal Modeling and Beyond** — Song, Liang, Sun, Huang | **NeurIPS 2024** | 2409.19772 | Neuromorphically motivated piecewise-linear temporal parameterization, SOTA across steering, pose and **motion deblurring** — i.e. a learned continuous-time intensity trajectory, which is the direct competitor to any "predict a trajectory over the exposure" head. |
| 6 | **ClearSight: Human Vision-Inspired Solutions for Event-Based Motion Deblurring** — Lin, Huang, Ren, Liu, Zhou, Fu, Cheng | **ICCV 2025** | 2501.15808 | SNN+ANN hybrid with dynamic neuron configuration and *unsupervised blurry-mask generation* — a per-pixel estimate of where and how much blur exists, produced without supervision. This is the closest published thing to several teams' "per-pixel support width." |
| 7 | **CMTA: Cross-Modal Temporal Alignment for Event-guided Video Deblurring** | **ECCV 2024** | (2408.14930) | Splits processing into **intra-exposure** enhancement and **inter-frame** alignment — an architectural acknowledgement that the exposure window is a distinct temporal regime. Cited by Teams 03 and 09. |

**Pre-2024 anchors I rely on and know from the field (not part of the required five, listed so my
reasoning is auditable):** EDI / mEDI (Pan et al., CVPR 2019 / TPAMI 2020) — `B = (1/T)∫exp(L)`,
with mEDI Eq. 5 written as `B̃ = L̃(f) + J̃(c)`; Time Lens (CVPR 2021) and Time Lens++ (CVPR 2022)
with HS-ERGB / BS-ERGB; EFNet + SCER (ECCV 2022); REFID / event-guided deblurring of unknown
exposure time (ECCV 2022, CVPR 2023); EVDI's learnable double integral (CVPR 2022); E-CIR (CVPR
2022); EBFI-BE blind exposure (CVPR 2023); TbD / TbD-3D (ICCVW 2019 / IJCV 2021, which introduced
Trajectory-IoU), DeFMO (CVPR 2021), Motion-from-Blur (CVPR 2022); Exposure Trajectory Recovery
(TPAMI); Gupta et al.'s Motion Density Function (ECCV 2010); Raskar et al., coded exposure
(SIGGRAPH 2006).

**Verification I could not complete.** Several teams' *closest competitors* are CVPR 2026 / ICML
2026 papers — ASTW, RTEA/TSANet, AE2VID, SECNet, Neural Events. I could not reach CVF openaccess
(403) or Semantic Scholar (429) and could not verify any of them. Teams 03, 05 and 09 each build
their central differentiation argument on one of these. **Their novelty claims are therefore
unaudited by me and should be treated as liabilities, per the brief.**

---

## Per-idea verdicts

| Team | Verdict | One-sentence reason |
|---|---|---|
| **01** Latent exposure support | **BORDERLINE** | The non-identifiability proposition is EDI + Gupta's MDF + TbD's known reversal ambiguity reassembled, and one of its Figure-1 predictions is already falsified by the machine-verified DSEC numbers; the TSB law and the "domain gap is a clock-convention gap" result do survive, but they rest on a dataset another team measured as offline. |
| **02** Exposure-occupancy measure as label | **ACCEPT** | This is the one idea that genuinely moves the recovered quantity out of image space into *supervision and evaluation* space, and its time-reversal identifiability pair plus convention-marginal conformal coverage are things no restoration paper contains or can contain. |
| **03** Temporal support fields | **REJECT** | The headline "matched blur, different support" pair is physically confounded — matched blur *extent* is not matched blur, the dwell density *is* the PSF, so the two frames differ visibly and the inexpressibility prediction is very likely false. |
| **04** Effective timestamp of a fused prediction | **ACCEPT** | `τ̂` and especially within-frame `σ_τ` are quantities no restoration formulation can produce even in principle, the 3-day zero-download pilot is the best de-risking in the batch, and the frame-only/event-only control is the single best control here. |
| **05** No offset fixes a width | **BORDERLINE** | T1/T2 are Raskar 2006 plus EDI's forward model plus a one-line Fourier fact, and the only deliverable that survives my objection is a single measurement (OBD) whose real-data onset condition DSEC daytime cannot reach. |
| **06** The exposure gap `J = ½Var_W(L)` | **REJECT** | It collapses into mEDI by the team's own admission — they keep mEDI's symbol `J` — and its headline P4 indicts a training term the team itself verified essentially nobody uses. |
| **07** Chronofields | **BORDERLINE** | The censored-likelihood output type is a real reformulation, but the headline bias number is computed outside the validity regime of its own derivation, and its killer baseline (Time Lens → detector) is genuinely live. |
| **08** Right place, wrong time | **ACCEPT** | It is the only idea my objection cannot touch — it never enters image space — and it is the only one whose central result cannot be taken away by a dataset going offline. |
| **09** Change-time / per-pixel clocks | **REJECT** | Pillar 2, the half in my domain, renames EDI's exponent as a "support width" and rests on the false claim that zero events during the exposure implies a sharp instantaneous frame observation. |
| **10** Fusion is ill-typed | **BORDERLINE** | The audit is a good, cheap design, but its headline prediction (event utility inverts with speed) is one I expect to be *falsified* on the deblurring models it names, and its support-blind-pair claim is false for any `B ≥ 2` bin configuration, i.e. for essentially every published model. |

---

## Detailed review

### Team 08 — *Right Place, Wrong Time* (my top-ranked)

**1. Verdict.** ACCEPT.

**2. Summary.** The claim is that every event and event–RGB benchmark evaluates a prediction with
temporal support `k_P` against a ground truth with a different support `k_G`, that neither is
stated anywhere, and that the resulting "right place, wrong time" error is charged to the `loc`
bucket in pixels because no metric in the field has a millisecond slot. The instrument is
along-track/cross-track decomposition — borrowed openly from air-traffic surveillance — with the
key twist that a *timing* error is a one-parameter perturbation that must simultaneously explain
box translation, box scale rate and yaw, which makes the temporal hypothesis testable rather than
assumed. Everything is inference-only on released checkpoints, plus E0, a label-forensics
experiment on a 4.7 MB label file that asks whether DSEC-Det's and DSEC-3DOD's inter-frame ground
truth is anything more than its own linear-interpolation prior.

**3. Strongest reason to accept.** E0 costs zero GPU hours and, if it lands, is a result that
belongs to the field rather than to the authors: *the high-rate ground truth of the two flagship
low-latency event benchmarks is, to within X% IoU, the interpolation prior used to make it.* No
dataset can go offline and take that away — the label files are 4.7 MB. Under the brief's own
criterion ("certain to produce a real figure"), nothing else here is close. Second: the pre-
registered architecture prediction (C3) — predicting `τ̂` from a method's declared window *before*
measuring it — is the strongest available evidence that a metric measures a physical quantity, and
it is the discipline this batch mostly lacks.

**4. Strongest reason to reject.** The algebra is borrowed and conceded, so the whole paper hangs
on the ranking flip (P6). If no pair flips, the fallback is a table of `τ̂` values, which is a
workshop paper.

**5. Factual errors.**
- **§4, `τ_max := (w_G + w_P)/2`, and C3.** `w_P` is taken to be the *representation* window — 50 ms
  for RVT's `stacked_histogram_dt=50_nbins=10`. But RVT, S5-ViT and DAGr are all **recurrent /
  stateful**: RVT carries LSTM state across the whole sequence, S5-ViT carries SSM state. Their
  actual temporal support is not 50 ms; it is unbounded, with an unknown decay. The paper's single
  proudest structural safeguard — "`τ_max` is not a free parameter" — is mis-specified for exactly
  the models under test. *Correction:* measure `w_P` empirically (truncate the recurrent state at
  `k` steps and measure the change in `τ̂`) and report the measured support, or restrict `τ_max` to
  feed-forward configurations.
- **§3, Ev-3DOD Table 1 read.** VoxelNeXt 53.61 → 33.32 is cited as "purely a timing gap." It is a
  timing gap *plus* the fact that the online setting withholds the LiDAR sweep entirely. The
  decomposition is exactly the right tool to separate those two, but the sentence as written
  asserts the conclusion before the measurement.
- **§2, the BS-ERGB / HS-ERGB row.** The claim that PSNR against a finite-exposure reference
  *strictly prefers* a blurred prediction is correct and is, in my judgement, the sharpest
  event-VFI observation anywhere in these ten documents. But its magnitude depends on the reference
  camera's duty cycle, and HS-ERGB's high-speed strand was captured with short exposures precisely
  to reduce it. State the duty cycle or the claim is unquantified.

**6. Claims exceeding evidence.**
- *"for a uniform event rate the information centroid of the input is `t − 25 ms`. That is a
  prediction, not a hypothesis."* The machine-verified brief says explicitly: "Whether the trained
  network weights the ten bins uniformly is unmeasured, so 25 ms is a reference point, not a
  prediction of network behaviour." Soften, or measure the bin weighting.
- *"P1: `τ̂` for RVT-{T,S,B} on 1 Mpx lies in [−35, −10] ms."* A 25 ms-wide interval on a 50 ms
  window is close to unfalsifiable. Tighten it or drop the pre-registration framing for P1.

**7. The hostile experiment.** "Show me that `AP^⟂ ≥ AP` is not simply because you gave every
prediction a free translation." Answered by `AP^iso` and `R` — but only if `R` comes out well above
0.5. Its absence would be fatal; its presence is designed in. **Not fatal.**

**8. Ranked fixes.**
1. Measure `w_P` for recurrent backbones instead of reading it off the representation config.
2. Run E0 first and report it as a standalone result before touching a GPU.
3. Report `R` with a bootstrap CI as the *first* number in the results section, not the fourth.
4. Add the beam-splitter / event-VFI PSNR-prefers-blur measurement with a stated duty cycle — it is
   your cheapest additional finding and it is in a literature (event VFI) you otherwise skip.
5. Drop the sawtooth prediction in E3 to a secondary claim; it assumes the frame branch dominates
   `τ̂`, which is what you are trying to measure.

---

### Team 04 — *When Is Your Prediction?*

**1. Verdict.** ACCEPT.

**2. Summary.** The claim is that a fused event–RGB predictor trained to emit "the state at `t`"
actually emits the state at the *evidence-weighted time centroid* `t̄`, a content-driven quantity;
the paper measures it as `τ̂ = argmin_t d(ŷ, y*(t))` against a continuous ground-truth trajectory,
and reports two derived statistics — the bias `b` and, crucially, the *within-frame* dispersion
`σ_τ`, which is what makes a scalar clock correction impossible. It correctly identifies FAOD's
Time-Shift invariance training as the antagonist rather than the ancestor: a detector whose output
does not change when you shift the support has thrown time away. The pilot is three days, three GPU
hours, and zero downloads, with a pre-registered null.

**3. Strongest reason to accept.** `σ_τ` — a *spatially varying effective timestamp induced by
fusion on global-shutter data* — is a quantity that no deblurring, interpolation or restoration
paper can produce, because restoration always emits an image indexed by a chosen instant and has no
task head whose implicit clock could disperse. The rolling-shutter line (EvUnroll, EvShutter,
UniINR) has already made the field accept that a spatially varying timestamp is a real defect worth
a CVPR paper; Team 04 proposes one nobody has looked for. And control 8.3(5) — frame-only and
event-only must give `σ_τ ≈ 0` — is the single best-designed control in this batch, because it can
kill the paper's own framing.

**4. Strongest reason to reject.** The instrument's resolution is the same order as the signal.
`τ̂` is estimated by an argmin over a GT trajectory; on FE240hz the GT is 240 Hz (4.17 ms sampling)
and the predicted effect is 2–5 ms. Worse, the argmin is flat under constant-velocity motion — the
team says so — and near-linear motion is the overwhelming majority of every real sequence. The
paper needs high-curvature, high-speed segments on real data, and it has not shown that enough of
them exist.

**5. Factual errors.**
- **§4.3, `b ≥ 0.25·T_exp`, falsified if `|b| < 0.5 ms`.** Against the machine-verified DSEC
  numbers this auto-falsifies on daytime data: the median daytime exposure in `interlaken_00_c` is
  1478 µs, giving a predicted `b ≈ 0.37 ms`, below the team's own falsification threshold. The
  prediction is only testable on the **six DSEC sequences pinned at 14996 µs**, where it gives
  `b ≈ 3.75 ms`. The paper does not identify those six sequences and must.
- **§8.2, FE240hz "Medium risk — author-hosted (zhangjiqing.com)".** Team 09 reports the FE108/
  FE240hz host `fe108.dluticcd.com` **refused connection**. Under the brief's rule that measurement
  supersedes guess, this row should read *dead*, and it is the primary loop-closer.
- **§8.2, BS-ERGB "Low — uzh-rpg download page".** Team 06 verified that both the Time Lens and
  Time Lens++ download pages now render navigation only, with no links or forms, and that no mirror
  exists. This row should also read *dead*. That removes the content-control (Fig. 4) closure.
- **§4.1 (C1), "`τ̂ − t_q` is to first order independent of speed `v`."** This is in tension with
  the paper's own definition of `w(t)` as the object's contrast-energy density over the exposure.
  Contrast energy deposition per instant is speed-dependent, and — from Deblrück's refractory rate
  law `r = 1/(T₀ + Δ_refr)`, which Team 06 documents — the *event-branch* weight is explicitly
  speed-dependent. The claim needs the refractory term modelled or the prediction weakened.

**6. Claims exceeding evidence.**
- *"the network was told the right time and still cannot deliver it, because the evidence does not
  contain a separable point-evaluation at `t_q`."* True for the frame branch. False for the event
  branch: an event at `t_i` *is* a point evaluation. The correct statement is that the *fused*
  evidence has no separable point evaluation because the frame branch dominates in the low-event
  regime — which is a measurement, not a derivation.
- *"no paper measures the effective timestamp of a fused event–RGB task prediction."* Unverified;
  the search budget ran out. Given that the closest neighbour (FAOD's Time Shift sweep) is one
  small step away, treat this as provisional.

**7. The hostile experiment.** "Fit the best per-speed-bucket lookup table of temporal offsets and
show me the residual `σ_τ`." The team already schedules this (Death 2) and pre-commits to
downgrading if the table removes ≥80%. That is the right posture. **Its absence would be fatal;
its presence is planned.**

**8. Ranked fixes.**
1. Replace FE240hz and BS-ERGB — both appear offline — with **EVIMO2 (200 Hz Vicon, direct
   download)** plus the six 14996 µs DSEC sequences. Do this before writing anything.
2. Restrict all `b` predictions to the long-exposure subset and state the daytime prediction is
   below your own falsification floor.
3. Add the refractory/bandwidth term to `w(t)` for the event branch, or state C1 as an empirical
   hypothesis rather than a first-order claim.
4. Report the identifiability margin (argmin curvature) as a *distribution over the test set*, not
   a per-measurement caveat — the fraction of frames where `τ̂` is identifiable at all is the number
   that decides whether the paper exists.
5. Run 8.3(5), the frame-only/event-only control, in the pilot week, not after.

---

### Team 02 — *No State at t: Exposure-Occupancy Measures*

**1. Verdict.** ACCEPT.

**2. Summary.** The claim is that a frame-level label is not a scene state but an unstated
functional `A` of the state's occupancy measure `μ` over the exposure, that no benchmark says which
`A` it used, and that the disagreement between defensible conventions is systematic and
sign-carrying rather than zero-mean noise. The formal core is a complementary-identifiability pair:
Proposition 1 says the frame is a linear functional of the pushforward measure alone and is
therefore invariant to every time reparametrization including reversal (this is Gupta's Motion
Density Function lifted from image formation to supervision, and the team says so); Proposition 2
says events determine the parametrization but not the mass. The predicted object is `μ̂` = a support
curve pushed forward by a learned dwell density, trained on point-labelled benchmarks with the
convention as a latent fitted by EM, and audited by split-conformal *convention-marginal* coverage.

**3. Strongest reason to accept.** This is the one idea in the batch that genuinely answers my
objection, and it answers it in the way the brief says deserves credit: the recovered quantity moves
out of image space into **label, supervision and evaluation space**. Exposure Trajectory Recovery
and TbD-3D recover a trajectory and a dwell density *of pixels*, for the purpose of producing a
sharper image. Nobody has proposed the occupancy measure as the *supervision target of a semantic
state*, nobody has learned a set-valued output from point labels with the annotation habit as a
latent, and nobody has scored a set prediction on a point-labelled benchmark with a coverage
guarantee that marginalizes over the benchmark's own unknown convention. Those four are real.

The second reason is the observation in (b2), which I think is the best single scientific insight
in these ten documents: **at constant velocity `A_mid = A_mean` exactly, no matter how severe the
blur; what destroys the label is intra-exposure acceleration, and the field has only ever plotted
blur magnitude.** That is correct — a linear motion blur kernel is symmetric, which is exactly why
the deblurring literature's difficulty axis is the wrong axis for label well-posedness — and it is a
falsifiable, cheap, orthogonalizing experimental design (`β` matched, `ν` swept).

The third is the time-reversal pair. Two clips traversing A→B and B→A over one exposure produce
bit-identical blurred frames and identical labels under mid/mean/mode/hull. That is a theorem, not
a benchmark delta, and it establishes that events are *necessary* rather than helpful — which is
precisely what the domain's "no plain fusion" constraint requires. Team 10 uses the same
construction and, as I note below, misuses it; Team 02 uses it correctly.

**4. Strongest reason to reject.** The paper's whole real-data story is FE108/FE240hz, which Team
09 measured as offline, and the fallback (EVIMO2, 200 Hz) is in 6-DoF pose space where the
convention-spread argument is different and weaker. The kill criterion is stated honestly, but the
instrument to run it against may not exist.

**5. Factual errors.**
- **Table of conventions.** `A_mode` = "argmax of the dwell density" is undefined at constant
  velocity, where the dwell density is uniform over the path — so the claim "at constant velocity
  `A_mid = A_mean = A_mode` exactly" is true for the first two and vacuous for the third. Restate
  as the barycentre of the argmax set, or drop `A_mode` from the equality.
- **Venue.** *Exposure Trajectory Recovery from Motion Blur* is cited here as **TPAMI 2021**, by
  Team 01 as **TPAMI 2022**, and by Team 03 as **TIP 2021**. Three teams, three venues, one paper.
  Resolve before submission; a wrong venue on your nearest pixel-space neighbour is the kind of
  thing my kind of reviewer notices immediately.
- **"no benchmark in computer vision states which A it used."** COCO/VOC annotation instructions
  ("box the visible extent of the object") do effectively specify `A_hull`. The claim should be
  narrowed to *event–RGB* benchmarks and to whether the convention is *enforced under motion*.
- **§Datasets, FE108 "Medium — gated by an application form."** See above: Team 09 measured the host
  as refusing connections. Reclassify.

**6. Claims exceeding evidence.**
- *"Prediction 3, the indictment: RSR change under a convention switch is 10–20 points, whereas the
  spread between the five published trackers is 3–8 points."* This is the paper's headline and it is
  a pure guess — the team has not measured the convention spread on any real data. If it comes in at
  2 points the paper is a simulation exercise. The team says so in the kill criterion, which is to
  their credit, but the abstract must not lead with 10–20 until it is measured.
- *"L_point ... is identifiable because different frames have differently shaped `μ̂`, so the
  functionals separate."* Asserted, not argued. With `|𝒜| = 6` conventions, one global `π`, and
  `σ²` also free, this EM is very likely weakly identified. Show identifiability on simulation with
  an imposed `π` before claiming "we read a benchmark's unwritten annotation convention off its
  labels."

**7. The hostile experiment (from my side of the field).** "Take EFNet or REFID, deblur the frame,
run the detector, and show me the convention spread does not collapse." My prediction is that it
does *not* collapse — a deblurring method restores a latent at one chosen instant, so
deblur-then-detect silently picks one `A` and inherits its bias rather than removing it. The team
schedules exactly this baseline ("EFNet / event-based deblur → off-the-shelf detector"). Keep it in
the main paper, not the supplement; it is the experiment that converts my objection into evidence
*for* the paper. **Absence would be fatal.**

**8. Ranked fixes.**
1. Substitute EVIMO2 as the *primary* real-data vehicle and re-derive the convention-spread argument
   in SO(3), where — as the team notes — `A_mean ≠ A_mid` even at constant angular velocity. That
   argument is stronger than the FE108 one and does not depend on a dead host.
2. Measure the convention spread `CS` in week 1, before any model, and honour the kill criterion.
3. Demonstrate `π` identifiability on simulation with an imposed convention before making the
   "we read the benchmark's habit" claim.
4. Promote the deblur-then-detect baseline into Figure 3.
5. Fix the ETR venue, and drop `A_mode` from the constant-velocity equality.

---

### Team 01 — *A Frame Is Not a Timestamp*

**1. Verdict.** BORDERLINE. *(Structural problem: the load-bearing proposition is an assembly of
published parts, and the real-data figure depends on a host that another team measured as dead.)*

**2. Summary.** The claim is that a blurred frame carries no information about `(t0, T)` — the
`u`-substitution removes them exactly — so the timestamp a dataloader supplies is an unfalsifiable
prior, and the resulting Temporal Support Bias is a signed, motion-direction-conditioned
localization error that all standard metrics average to zero. The reformulation predicts a
Bernstein-basis trajectory over the *normalized* support plus a support field `(t̂0, ρ̂, T̂)`, with
`K = 0` reproducing the current formulation exactly, so the order ablation is the SOTA comparison.
The validation asset the team correctly identifies is that DSEC publishes true per-frame exposure
start/end in µs, so `|T̂ − T|` in milliseconds is free real-data supervision.

**3. Strongest reason to accept.** The "free lunch" experiment — estimate one scalar `α̂` per
dataset, shift every baseline's predictions along the event-estimated motion direction, zero learned
parameters — and the prediction that this removes ≥40% of a published cross-dataset "domain gap."
If that holds, it is not something an incremental paper can produce, and it is a claim about the
field's data rather than about the authors' model. Second: SIE validated against DSEC's published
exposure timestamps is the cheapest possible real-data check on the central latent, and it exists
today for free.

**4. Strongest reason to reject.** Every component is published and the team names them all: the
exposure integral is EDI 2019; blind exposure is EBFI-BE 2023; unknown-exposure-time deblurring is
REFID/ECCV 2022; intra-frame Bézier trajectories with Trajectory-IoU are TbD 2019/IJCV 2021;
continuous-time Bézier queries are Gehrig et al. The proposition's three parts are also all known
in my literature: that the frame determines the dwell measure is Gupta 2010; that the blur kernel is
reversal-invariant is folklore in blind deconvolution and explicit in TbD; that `(t0,T)` drop out of
a normalized integral is a change of variables. The self-score's own phrase — "assembly novelty" —
is the right one, and under the brief's rule an unverified novelty claim as the sole asset is a
liability.

**5. Factual errors.**
- **§Fig 1a.** *"prediction: left–right exposure-midpoint difference ≥ 1 ms on a substantial
  fraction of frames."* **Falsified in advance.** The machine-verified measurement is median
  16–144 µs, max 380 µs — a factor of 3 to 60 below the prediction — and the brief explicitly says
  an argument resting on left/right divergence rests on the smaller effect and should be marked
  down. This propagates: the "stereo pair is support-inconsistent, and hence disparity GT is
  support-inconsistent" claim, and item 5 of "what existing methods cannot express," both rest on
  it. Remove or restate with the measured numbers.
- **§Datasets, FE108/FE240hz "Medium-high, access is by application."** Team 09 measured the host as
  refusing connections. This is the *only* real source of intra-exposure GT in the plan, and the
  self-score already names it as the dominant risk; it should now be treated as realized.
- **§Fig 1b.** Recovering the APS exposure window from AEDAT exposure-start/end signals on DAVIS346
  is stated as routine. It is not: the exposure-start/end special events are present in some AEDAT
  recordings and absent in others depending on the capture tool and firmware. Verify on an actual
  FE240hz file before the plan depends on it — and the file may not be obtainable.

**6. Claims exceeding evidence.**
- *"A motion-blurred frame carries **no information whatsoever** about the absolute time interval it
  integrated."* Not quite: the *blur extent* bounds `v·T`, and if `v` is known from events the frame
  constrains `T`. The correct statement — which the team's own Proposition makes — is that the frame
  alone does not determine `(t0, T)` *given an unknown trajectory*. As written the sentence is
  stronger than the proposition it is derived from.
- *"the resulting `α̂` shift removes ≥40% of the excess error"* and *"transfer degradation is
  predicted to within 25%."* Two pre-registered numbers with no pilot behind them.
- *"essentially no downstream method reads `exposure_timestamps.txt`."* Plausible and probably true,
  but unverified.

**7. The hostile experiment.** "Run EDI and EBFI-BE, deblur, then detect, and show me TSB is not
reduced." The team schedules it, correctly predicts it will not reduce TSB, and is right — a
restoration method commits to one instant. **Absence would be fatal**; presence is the single best
answer to me in this document.

**8. Ranked fixes.**
1. Delete the left/right divergence argument. It is falsified and it is the weaker effect.
2. Replace FE240hz with EVIMO2 + the six 14996 µs DSEC sequences, and reduce the paper's claims to
   what those support.
3. Lead with the free-lunch scalar and the SIE validation, not with the proposition. The proposition
   is a half-page of change-of-variables and every part of it is citable to 2010–2021.
4. Make `K = 0` the *first* table, so the reviewer sees the formulation change isolated from the
   architecture before seeing any architecture at all.
5. Fix the ETR venue and cross-check it against Teams 02 and 03.

---

### Team 10 — *Fusion Is Ill-Typed*

**1. Verdict.** BORDERLINE. *(Structural problem: the headline empirical prediction is one I expect
to be falsified on the very models it names.)*

**2. Summary.** Proposition 1 observes that a frame is an order-0 positive interval mean in the
linear domain while an event bin is an order-1 zero-mass signed difference in the log domain, so
these are different observables, not misaligned copies of one observable, and no shift, scale or
warp can reconcile them. From this comes a type system (mix / compare / lift / render / causal
tube), a diagnostic suite for published RGB–event models (event utility vs speed, off-support
attention mass via Jacobian influence so it applies to gates and AdaIN too), and a minimal operator.

**3. Strongest reason to accept.** The Jacobian-influence formulation of OSAM is the right
engineering call — it makes the diagnostic apply to FRN's AdaIN and RENet's gates, not just to
attention — and the "fine-tune on the high-`s` regime and watch OSAM *not* fall while the task
metric improves" experiment is a genuinely well-designed formulation-vs-weights discriminator. And
the team is honest that the operator is not the contribution and will not top the leaderboard.

**4. Strongest reason to reject.** Panel A. `EU(s)` is predicted to *rise then fall*, with the event
branch contributing least where the frame is worst. In event-guided restoration the documented
behaviour is the opposite: EFNet, REFID, CMTA (ECCV 2024) and ClearSight (ICCV 2025) all show the
event branch's contribution growing with blur severity — that is the entire premise of the NTIRE
event-deblurring benchmark. **EFNet is on the team's own diagnostic list.** My prediction is that
`EU(s)` inverts for the detection/segmentation models (RENet, FRN, CEUTrack), whose fusion is
pixel-aligned at high stride, and does *not* invert for EFNet, whose SCER is already
exposure-referenced — i.e. already a hand-built `render`-to-frame-type, which the team credits.
That split would be a *better* paper than the one proposed, but as written the headline is at risk
of contradicting itself in its own Table 1.

**5. Factual errors.**
- **§Support-blind pairs.** *"identical endpoints ⇒ identical polarity-sum voxel grids."* Only for
  `B = 1`. The construction as stated indicts a straw configuration: every model in the diagnostic
  list uses `B = 5–15` bins, and with `B ≥ 2` a time-reversed trajectory produces a *different*
  voxel grid. The claim *"every published model maps this pair to one input point"* is therefore
  false as written. The `dim 𝒩 = d − B − 1` sweep partially covers this, but the headline must be
  restated as a statement about temporal resolution (`d > B + 1`), not about reversal.
- **§Panel C, DSEC.** The plan regresses per-frame error on `T·‖v̄‖` using DSEC's exposure
  timestamps. The verified daytime exposure is ~1478 µs and `T` varies 337 → 4207 µs within a single
  sequence, so the `T` axis has real dynamic range — good. But the six sequences pinned at exactly
  14996 µs have *zero* `T` variance and will contribute nothing to the correlation. Stratify.
- **§Data, "GoPro+events / REBlur (~25 GB) for EFNet."** REBlur is ~0.66 GB with SCER and ~0.47 GB
  raw (Team 06 verified this). The 25 GB figure appears to be GoPro-events only.

**6. Claims exceeding evidence.**
- *"$\mathrm{OSAM}(s)\approx 1-\tfrac{r}{r+s}$: from $0.12\pm0.03$ at $s{=}0.5$ px to
  $0.83\pm0.05$ at $s{=}12$ px."* Error bars on a quantity never measured.
- *"Perfect temporal and spatial registration leaves the two quantities as different observables."*
  True and trivial — and the restoration field has acted on it for years. EFNet's SCER, EDI's
  forward model and AKF are all `render ∘ lift`, and the team concedes each. The proposition is a
  two-line observation; its value is entirely in whether the audit shows the field violating it, so
  the audit must carry the paper and the abstract must say so.

**7. The hostile experiment.** "Show me `EU(s)` for EFNet." Run it first. If it rises monotonically,
restructure the paper around the *split* between exposure-referenced restoration fusion and
pixel-aligned task fusion — that is a defensible and more interesting claim.

**8. Ranked fixes.**
1. Run EFNet's `EU(s)` before anything else; be prepared to restructure.
2. Restate the support-blind-pair claim for `B ≥ 2` (a temporal-resolution statement, not a reversal
   statement), or drop the "every published model" phrasing.
3. Credit SCER earlier and harder; it is the strongest evidence that the field already half-knows
   Prop. 1, and burying it invites the charge that you didn't know.
4. Force the high-`s` regime on REBlur / EVIMO2 rather than DSEC, per your own Death 2.
5. Cut the operator to one page.

---

### Team 05 — *No Offset Can Fix a Width*

**1. Verdict.** BORDERLINE. *(Structural problem: the surviving deliverable is a single
measurement, and its onset condition is out of reach on the only real dataset that is certainly
available.)*

**2. Summary.** Frames and events integrate one latent log-radiance against two different temporal
measures, so alignment is not a scalar-delay problem; a shift is a unit-modulus linear-phase
multiplier in Fourier and cannot fix a modulus mismatch with zeros, so a Support Mismatch Floor
exists that no offset removes (T1), the best-fit offset is a spectrum-weighted group delay and
therefore scene- and speed-dependent (T2), and a sweep over `J ≥ 2` known speeds identifies the
kernel pair by dilation (T3). The deliverable is a calibration protocol whose output is a pair of
measures plus a per-pixel blind-band mask, plus the measurement OBD = `dδ̂/db` on a hardware-synced
rig.

**3. Strongest reason to accept.** OBD is a real deliverable that no restoration paper has or could
have: "on a rig whose true offset is exactly zero, the estimated offset drifts by ≥3 ms as the
calibration motion gets faster — i.e. calibrating faster makes your calibration worse." EF-Calib and
eKalibr report sub-millisecond `t_d ± σ`; a demonstration that their estimand is not a rig constant
is a genuine finding aimed at a literature (event–frame extrinsic temporal calibration) that my
objection does not reach. T3 is also nice: the multi-speed dilation argument is the event–frame
analogue of multichannel blind deconvolution identifiability, transplanted competently.

**4. Strongest reason to reject.** Everything else is textbook and the team says so. The box-⇒-sinc-
nulls argument is Raskar 2006; the photoreceptor low-pass is standard and is modelled by v2e, IEBCS
and — as of 2024 — by **Deblur e-NeRF (ECCV 2024)**, which the team does not cite and which
explicitly models event pixel bandwidth as the source of *event* motion blur. And the "support-
matched comparison" whose residual stays at the noise floor in Panel B **is EDI's forward model**:
rendering the event-derived latent through the frame's exposure integral and comparing is precisely
what EDI does. Panel B therefore re-derives, under a new name, the fact that EDI's forward model is
correct. What is new is only that nobody applied it to *offset estimation*.

**5. Factual errors.**
- **§Datasets / Risks, DSEC onset.** Prediction 1 says nothing happens below `b = vT ≈ 2 px`. With
  the verified daytime median exposure `T = 1478 µs`, the onset requires `v ≥ 1353 px/s`. On the
  night/tunnel sequences at `T = 14996 µs`, it requires only `v ≥ 133 px/s`. **The entire real-data
  story lives on the six sequences pinned at 14996 µs**, and the paper should say so and name them
  rather than saying "night/tunnel."
- **Missing prior art.** Deblur e-NeRF (ECCV 2024) models the event pixel bandwidth as a physical
  low-pass causing event motion blur under high speed — i.e. it keeps more than the first moment of
  `w_E`, which is the paper's stated delta against Yang et al. (CVPR 2024). Engage it.
- **§Baselines.** "EGER / Zhang et al., *Generalizing Event-Based Motion Deblurring*, ICCV 2023" is
  described as "exposure as an index range." I could not verify this title/venue and the description
  reads closer to REFID's ETES. Verify.

**6. Claims exceeding evidence.**
- *"the CVPR 2026 proceedings contain 60+ event papers and none is about event–frame temporal
  support or exposure-aware calibration."* An exhaustive-proceedings claim made with an exhausted
  search budget. I could not verify a single CVPR 2026 citation in this batch.
- *"|dδ̂/db| ≳ 0.05 T per pixel of blur"* and *"the gap between empirical `R(δ̂)` and computed SMF is
  <5% of SMF for b > 2 px."* Two precise numbers with no pilot.

**7. The hostile experiment.** "Run EDI's forward model as your 'support-matched comparison' and
show me your Panel B curve is not just a restatement that EDI works." Ablation 1 (global shutter,
`τ = 0`, noiseless, `δ* = 0`, ideal thresholding) is the right test and is scheduled first, which is
the correct posture. **Absence would be fatal.**

**8. Ranked fixes.**
1. Measure the joint `(T, v)` distribution over all DSEC sequences in week 1, name the six
   long-exposure sequences, and decide the real-data story from that measurement — the team already
   plans this and it should be the go/no-go.
2. Move the deliverable decisively to calibration: the headline result should be OBD measured
   against EF-Calib/eKalibr's own protocol, not the notch spectrum.
3. Cite and engage Deblur e-NeRF (ECCV 2024) and Ev-DeblurNeRF (CVPR 2024) — both fit event-pixel
   response parameters that your framing says nobody estimates.
4. State explicitly, in the introduction, that Panel B's support-matched curve is EDI's forward
   model. A reviewer of my kind will notice; saying it first is worth more than being caught.
5. Verify the ICCV 2023 EGER citation.

---

### Team 07 — *Chronofields*

**1. Verdict.** BORDERLINE. *(Structural problem: the headline quantitative example is computed
outside the validity regime of its own derivation.)*

**2. Summary.** Invert the map: instead of `time → state`, predict for a queried state a
distribution over *when* it held, with events entering as exact (uncensored) time observations,
frames as interval-censored ones, and non-occurrence as right-censored, plus an explicit `∅` atom.
The frame's dwell integral is re-expressed as a constraint on `∂τ/∂L` (EDI with the variables
swapped, and the team says so), and a temporal eikonal `∇_u τ · v = 1` falls out as the analogue of
`‖∇d‖ = 1` for SDFs.

**3. Strongest reason to accept.** The censored-likelihood type assignment is a real reformulation
imported from survival analysis, and the `∅` atom and calibrated temporal intervals (TCE) are
outputs that a reconstruct-then-detect pipeline structurally cannot produce. The C1 anchor — predict
the next contrast-crossing time from prior events plus the last frame, supervise with *held-out real
events at microsecond resolution* — is the best zero-annotation real-data experiment in this batch.
No simulator, no labels, no gated dataset.

**4. Strongest reason to reject (and it is a hard error).** §F2's headline: "`T = 20 ms`,
`a = −2 px/ms²`, `v̄ = 4 px/ms` ⇒ `Δt ≈ −8.3 ms`, i.e. 42% of the exposure." The arithmetic is
right — `aT²/(24 v̄) = −800/96 = −8.33` — but the *regime* is not. `v̄ = v₀ + aT/2` gives
`v₀ = 24 px/ms` and `v(T) = −16 px/ms`: **the object reverses direction at `t = 12 ms`, inside the
exposure.** The dwell density `∝ 1/|ẋ|` is singular there, and the paper's own second consequence
says a reversal makes the effective time *multi-valued*, not biased. The first-order expansion needs
`|aT| ≪ v̄` — here `40 ≪ 4`, false by an order of magnitude. The headline number for the bias
formula is drawn from a case the paper elsewhere says the bias formula does not describe. The second
example (`T = 10`, `a = −1`, `v̄ = 5` ⇒ `−0.83 ms`) is marginal but valid; that is the number the
paper actually has, and it is small.

**5. Other factual errors.**
- **§Datasets.** HS-ERGB / BS-ERGB "availability" — Team 06 verified the Time Lens and Time Lens++
  download pages now render navigation only, with no links or forms and no mirror; HS-ERGB survives
  on a HuggingFace mirror at 2.61 GB. Update, and note that BS-ERGB is where the killer baseline
  comparison (Time Lens → RVT) was to be run.
- **§F1.** "FAOD reports only a 3-point mAP drop under an 80× mismatch" is used as evidence that
  mAP cannot see time. It is equally consistent with the Align Module working. The claim needs the
  null-space construction (two systems, identical mAP, 4× different CTE) to carry it, and that
  construction should therefore be Figure 1, not a proposition in the text.

**6. Claims exceeding evidence.**
- *"`event camera ∧ censored` → 0 results; `crossing time ∧ event camera` → 0; `event camera ∧
  temporal uncertainty` → 0."* Three empty conjunctions on specific phrasings are weak evidence of
  an empty field; time-to-contact, event-based TTC and next-event-time prediction all occupy
  adjacent ground under different words, and the team concedes the last.
- *"Crossover at `a > 0.2 px/ms²` — a regime that covers essentially all near-field looming, all
  rotation about a near axis, and all contact."* Asserted with no measurement of how much of any real
  dataset that is.

**7. The hostile experiment.** Time Lens → 1000 fps → RVT, at matched and unmatched compute. The
team names it as the paper-killer and pre-registers a falsification criterion (P95 CTE within 15%),
which is exactly right. From my side of the field: on BS-ERGB-class data Time Lens-family
interpolation is *very* good, and I would bet on the baseline at unmatched compute. **Absence is
fatal.** And the dataset it must be run on may be gone.

**8. Ranked fixes.**
1. Recompute the F2 headline inside its validity regime, or reframe it as the *reversal* case and
   drop the bias formula for it. As written it is a reviewer-2 kill in one sentence.
2. Run the C1 anchor first — it is real, cheap, and unblocked by any dataset going offline.
3. Find a replacement for BS-ERGB for the head-to-head (HS-ERGB mirror, or EVIMO2), or state that
   the head-to-head cannot be run and accept the consequences.
4. Promote the two-systems/identical-mAP construction to Figure 1.
5. Cut the dataset list from six to two, as the team's own self-score says.

---

### Team 03 — *Temporal Support Fields* — REJECT

**1. Verdict.** REJECT. **Fatal to this execution, not to the idea.** The event-branch support,
the sub-probability mass channel and the abstention output are worth keeping; the experiment that
is supposed to establish the phenomenon is confounded.

**2. Summary.** Predict, per pixel and per modality branch, a sub-probability measure on the time
axis — mass (how much evidence exists) and shape (when it is from) — and replace similarity-based
cross-modal attention with an *overlap of supports*, so "the two modalities were not looking at the
same time" becomes a first-class, abstainable output. The frame-branch support is self-supervised on
real data by re-rendering the blurred frame through the predicted measure (EDI with `Unif(T)`
replaced by a learned per-pixel `μ̂_F`), and the event-branch support has free ground truth in the
raw stream (inter-event intervals).

**3. Strongest reason to accept.** The event-branch half is genuinely good and genuinely free: the
inter-event interval *is* that pixel's information support, it is present in the raw stream on real
data with no annotation, and the distinction between "I checked and nothing changed for 40 ms"
(full mass, coarse value) and "I have no idea" (zero mass) is one no voxel grid can make. The
abstention output — "there is no valid observation of this pixel at the requested time" — is a
representable-output claim, not an accuracy claim, and it is the right kind of contribution.

**4. Strongest reason to reject — the fatal flaw.** The entire failure phenomenon rests on
"matched blur, different support" pairs: (A) constant velocity across the exposure, (B)
dwell-then-dash — same total displacement `d`, same exposure `T`, same event count. The paper
asserts these give "a blurred frame with the *same spatial blur extent* `d` (the PSF's support
length is identical; only its intensity profile differs)."

**The PSF's intensity profile *is* the dwell density, and the dwell density is what the frame
measures.** This is Gupta's Motion Density Function and it is the first thing my literature
established: the blur kernel is a dwell-time histogram. Case (A) produces a uniform streak. Case (B)
produces a bright, near-sharp image of the object at the dwell position plus a faint 20%-weight
streak. These are *visibly different images*, and a frame encoder sees the difference immediately.

Therefore Prediction 4 — the paper's "sharpest number," that a voxel-grid + frame-encoder pipeline
satisfies `‖φ(A) − φ(B)‖/‖φ(A)‖ < 3%` — is very likely false, and it is false for a reason
internal to the construction rather than an empirical accident. Prediction 1 (a ≥3.5 dB PSNR cliff
for EFNet/CMTA/REFID/Time Lens++ between overlap terciles) is confounded in the other direction:
dwell-then-dash blur is *easier* to deblur in the dwell band (most of the energy is at one position)
and harder in the dash band, so any PSNR difference between (A) and (B) is attributable to PSF shape
— a blur property — rather than to support overlap. Prediction 2, the partial-correlation control
`|ρ(err, O* | d, N_ev)| ≥ 0.6` vs `|ρ(err, d | O*, N_ev)| ≤ 0.25`, is supposed to close this off,
but it conditions on blur *extent* `d`, not on the PSF, so it does not.

The phenomenon may still exist. But the construction that is supposed to isolate it does not isolate
it, and the go/no-go gate (2–3 days) will produce a curve that a deblurring reviewer will attribute
entirely to PSF shape.

**5. Other factual errors.**
- **§What existing methods cannot express, item 1.** "Every existing model always outputs a value."
  Restoration models with an explicit confidence/occlusion mask, and ClearSight (ICCV 2025), which
  generates an unsupervised *blurry mask* per pixel, weaken this. ClearSight is the closest published
  thing to a per-pixel "how much of this pixel is valid" output and must be engaged.
- **Venue.** *Exposure Trajectory Recovery* is cited here as **TIP 2021**; Teams 01 and 02 say TPAMI
  2022 and TPAMI 2021 respectively. Resolve.
- **§Data, BS-ERGB / HS-ERGB "medium (host availability)."** Verified dead / mirror-only by Team 06.
  This removes the "real RGB-E with a high-speed strand ⇒ *measured* occupancy windows" row, which is
  the only source of measured frame-branch support ground truth on real data. Without it, `L_supp`
  is simulator-only and Death 2 is realized.

**6. Claims exceeding evidence.**
- *"EFNet, CMTA, REFID and Time Lens++ mean PSNR drops by ≥ 3.5 dB between `O* ∈ [0.7,1.0]` and
  `O* ∈ [0.0,0.3]`, with blur extent matched to within ±5% and event count within ±5%."* Blur extent
  and event count matched; blur *shape* not matched, and blur shape is the frame's whole content.
- *"we found no work that predicts a temporal support measure as its output."* Exposure Trajectory
  Recovery predicts per-pixel displacement at multiple timepoints inside the exposure; UniINR (ECCV
  2024) embeds the exposure interval in the query; ClearSight (ICCV 2025) predicts a per-pixel blur
  mask. The claim needs narrowing to "as a sub-probability measure with an explicit mass channel,
  on both branches."

**7. The hostile experiment.** "Render (A) and (B), show me the two blurred frames side by side, and
show me the frame encoder's codes." That is a five-minute experiment and it decides the paper. Run
it before anything else. **Its absence is fatal.**

**8. Ranked fixes.**
1. Match the *PSF*, not the blur extent. Construct pairs with the same dwell density but different
   event-branch supports — e.g. same frame-side motion profile, different illumination so the event
   rate profile differs. That isolates cross-modal support mismatch from PSF shape. Whether such
   pairs can be built at all is the real question, and answering it honestly may kill or save the
   idea.
2. If they cannot, pivot to the mass/staleness axis, which the team already names as the fallback
   and which does not depend on the matched-pair construction at all. "Temporal abstention for
   asynchronous perception" is a smaller but intact and defensible contribution.
3. Replace BS-ERGB with something obtainable, or accept that frame-branch support supervision is
   simulator-only and lead with the event-branch (free, real) half.
4. Engage ClearSight (ICCV 2025) directly.
5. Verify every CVPR 2026 citation (ASTW, RTEA) before building the differentiation argument on it.

---

### Team 06 — *The Exposure Gap* — REJECT

**1. Verdict.** REJECT. **Fatal to this framing; not fatal to the P7 result, which is a different,
smaller, real paper.**

I want to be clear that this is the most technically careful document in the batch. It read 44 PDFs,
it refuses to make the "everyone assumes this" claim, it names EVDI as the one method that gets the
two-frame form right, and it flags two unclosed verification gates. That honesty is exactly what
good work looks like. It is also what makes the rejection easy: the document tells me the answer.

**2. Summary.** The identity `∫events = Δ log I` is misspecified rather than noisy, because
`log B = L(t_k) + J` with `J = LME_W(cE) − cE(t_k) ≥ 0`, and to second order `J = ½Var_W(L)` — the
bias of the point-sample identity is half the intra-exposure variance of log-intensity. The
reformulation supervises a threshold-invariant normalized cumulative event profile `φ` plus an
amplitude `a_p` identified from two exposure functionals, which recovers the per-pixel contrast
threshold — better the faster the motion.

**3. Strongest reason to accept.** P7. Running the standard two-frame least-squares contrast-
threshold estimator (Wang et al., ACRA 2019, Eq. 6) on a *physically perfect* sensor, `ĉ` collapses
from 0.189 at 1 px of blur to −0.004 at 32 px — a sign flip, with no sensor non-ideality present —
while the support-aligned estimator stays within ±5% at every blur level. That is a real, checkable
finding about a procedure the field uses, and the discriminating test the team proposes (refractory
inflates the effective threshold, the exposure gap deflates the calibrated one — opposite signs) is
good science. The identifiability result (`G` monotone in `a`, `dG/da = 0.86–0.91`, `a_p` recovered
to 0.2%) is the honest inversion of the field's instinct: blur identifies the threshold, and the
conditioning improves with motion.

**4. Strongest reason to reject.** Two things, and either alone would do it.

*(a) It collapses into mEDI, by the team's own account.* The document states that mEDI Eq. 5 already
reads `B̃ = L̃(f) + J̃(c)` with `J(c) = (1/T)∫exp(c·E(t))dt` — "the exact exposure functional" — and
that they keep mEDI's symbol `J`. So the residual is not unmodelled; it is EDI's own term. What is
offered as new is the second-order form `J = ½Var_W(L)`. That is the standard cumulant expansion of
a log-mean-exp: `log⟨e^X⟩ = ⟨X⟩ + ½Var(X) + κ₃/6 + …`. Presenting it as "a new closed form for a
residual the field treats as noise" is a footnote presented as a contribution, and it is precisely
"deblurring with new words."

*(b) Its headline P4 indicts a training term the team verified nobody uses.* The document says, in
its own words, that the identity is used everywhere as "a *physical justification sentence*, but
**never as an actual training loss in frame interpolation** — so no one has ever been forced to
confront its bias." P4 then claims "methods trained with the uncorrected consistency term inherit a
motion-conditioned contrast bias." If nobody trains on it, there is nothing to inherit and nothing
to indict. This is an internal contradiction between the assumption section and the prediction
section, and it is the sharpest one in these ten documents.

**5. Factual errors — and a computation the team should run.**

**The exposure gap on real DSEC daytime data is ~0.01 contrast thresholds, not 0.53–2.6.** From the
machine-verified numbers: inside one 1478 µs daytime exposure, firing pixels average ~1.10 threshold
crossings. So the total log-intensity excursion at a firing pixel is `A ≈ 1.10c`. For a monotone ramp
over the window, `Var_W(L) = A²/12`, so `J = A²/24`. With `c = 0.2`: `A = 0.22`, `J = 0.0020` log
units `= 0.010 c`. That is **1% of a contrast threshold — two orders of magnitude below the ±c/2
event quantization noise** that the team itself says masks the effect. The paper's claimed
0.53–0.71 c (edges) and 2.6 c (texture) are simulation numbers at excursions ~10–20× larger than
DSEC daytime supplies.

On the night sequences the picture changes: the windows are 10.1× wider, so if the crossing count
scales comparably, `A ≈ 11c = 2.2`, `J = 0.202` log units `= 1.0 c` — squarely in the claimed range.
**So the entire real-data story lives on the long-exposure / night sequences**, and the daytime data
that constitutes most of DSEC will return a null. Compute this before writing.

Two further real-data problems specific to my field, neither of which the document addresses:

- **DSEC's RGB is a separate FLIR camera with an ISP.** `log B` is not log irradiance: there is a
  camera response function, a tone curve, white balance and gamma between the sensor and the stored
  pixel. The event camera measures log irradiance at a *different* sensor with different optics and
  spectral response. On DSEC, the residual of `R = c·ΔE − Δ log B` will be dominated by CRF and
  spectral mismatch, not by `J ≈ 0.01c`. This is exactly why EDI, EFNet, REFID and EVDI work on
  DAVIS (shared photodiode) or on beam-splitter rigs. Running the identity on DSEC's stereo
  event/RGB pair is a category error for a per-pixel photometric claim.
- **DSEC events and images are stereo, with a baseline.** Per-pixel regression requires pixel
  correspondence, and DSEC's rectified/remapped images still carry depth-dependent parallax. The
  document's `R ~ P` regression is per pixel, per frame pair.

Together these mean the plan's Stage 1 ("DSEC is the anchor, and this is a change of plan forced by
verification") is anchored on the wrong dataset. REBlur (0.66 GB, DAVIS, direct HTTP) and HighREV
are the right anchors and the team already has them on the list as secondary.

Also: **the "zero-free-parameter predictor" claim does not survive to real data.** Both `R` and `P`
contain `c`. In simulation `c` is known. On real data it is not — and P7 says the standard estimator
for it is contaminated by the very effect being measured. The regression on real data must fit `c`
jointly, at which point it has one free parameter and the "slope 0.955 with zero fitted parameters"
rhetoric no longer applies.

**6. Claims exceeding evidence.**
- *"`J = ½·Var_W(L)` is a new closed form for a residual the field treats as noise."* It is the
  second-order term of an expansion of a published quantity.
- *"on textured content — which is what natural video is — the residual is 2.6 contrast thresholds
  and 99% of it is the exposure operator."* True in the team's simulator with band-limited
  translating texture; ~0.01 c on verified DSEC daytime statistics.
- *"the published contrast-threshold calibration is contaminated by the gap."* This one I believe,
  and it is the paper's best result — but it is a claim about one 2019 robotics-conference estimator,
  not about "the field."

**7. The hostile experiment.** "Show me the exposure gap on real data, in contrast-threshold units,
on a sensor where events and frames share a photodiode." That is REBlur or a DAVIS recording, it is
cheap, and it decides the paper. **Absence is fatal.**

**8. Ranked fixes (i.e. what to write instead).**
1. **Rewrite the paper around P7 and the identifiability result** — "the standard contrast-threshold
   calibration has a motion-dependent bias with a closed-form correction, and blur identifies the
   per-pixel threshold better the faster the motion." That is a real, self-contained contribution
   with a clean experiment. Drop the exposure-gap framing to a section.
2. Move the real-data anchor from DSEC to REBlur / HighREV / a DAVIS recording. The DSEC plan cannot
   work for a per-pixel log-photometric identity across a stereo pair with an ISP in between.
3. Compute `J` in contrast-threshold units from the verified DSEC statistics before committing, and
   report the daytime/night split honestly.
4. Resolve the P4 / "never used as a training loss" contradiction explicitly, in the introduction.
5. Close the two flagged verification gates (Brandli ISCAS 2014; Electronics 15(7):1420) before
   writing an introduction, as the team already says.

---

### Team 09 — *Change-Time* — REJECT

**1. Verdict.** REJECT. The rejection is of **pillar 2**, the half assigned to our domain. Pillar 1
(monotone-reparameterization invariance of a counting clock) is a representation-learning argument
outside my competence and may well be a good paper; it needs a different reviewer. But pillar 2 as
written is not salvageable, and the document itself makes pillar 2 the answer to the assigned seed.

**2. Summary.** Stop cutting the event stream into windows measured in seconds; index each pixel by
its own accumulated change `τ(x,t) = C·N(x,t)`, a clock *field* with no duration in it, exactly
invariant to any monotone time reparametrization. On the frame side, the RGB frame's temporal
support becomes a *measured, spatially varying width* `W(x) = C·N_exp(x)` — the contrast threshold
times the number of events at that pixel during the exposure — obtained by counting, with a fusion
weight `1/W(x)` derived from the sensor model rather than learned.

**3. Strongest reason to accept.** Two verified-empty search intersections and a physically grounded
motivation (AER bus saturation perturbs recorded event times in a rate-dependent way, so the
recorded timestamp is already an unknown monotone `φ(t)`) that converts the framework's weakest
point into its motivation. The `β`-is-the-window-reciprocal identity, verified from released code
(DAGr `time_window = 1e6` µs; AEGNN `beta=0.5e-5` with `torch.min(ts)` as window origin; EFGCN's
`t*_i = ⌊β·t_i/T⌋`), is the hardest piece of evidence in this entire batch — a code-level citation
rather than a rhetorical claim. And the report that **`fe108.dluticcd.com` refuses connection** is
the single most valuable fact any team produced for the others.

**4. Strongest reason to reject — pillar 2.**

*(a) `W(x)` is EDI's exponent with a new name.* `W(x) = C·N_exp(x)` is the total log-intensity
variation at pixel `x` during the exposure. EDI writes `B = I₀·(1/T)∫exp(c·E(t))dt`; `c·E` over the
exposure *is* `W(x)`, up to sign bookkeeping. It is measured in log-intensity units, not time units.
Calling it "the frame's temporal support width, in change units" is a rename of a photometric
excursion as a temporal quantity. Note that **Team 06 independently derived the same scalar** and
called it the amplitude `a_p = c_p·E_p` — two teams, one quantity, two claims of novelty, and the
quantity is in EDI.

*(b) The load-bearing claim is false.* "Where `W(x) = 0`, `μ_x = δ₀` and `B(x) = exp(L̃(x,0))`
exactly. The frame is a *sharp, instantaneous, exact* observation there... the alignment cost must be
exactly zero." Zero events at a pixel during the exposure does **not** mean the intensity was
constant. It means `|ΔL| < C` — a *bound*, not a zero. Team 03, on the same seed, states this
correctly ("the absence of an event is an interval-valued constraint, not a zero"). A low-contrast
edge sweeping through a pixel produces genuine blur and no events. This is not a corner case: it is
the entire sub-threshold regime, which is where the frame is supposed to carry the information the
events cannot. The claim is load-bearing for the `1/W(x)` fusion weight, for the SWC metric, and for
the "alignment cost is exactly zero" result.

*(c) Refractory undercounting kills SWC in exactly the regime it is claimed for.* SWC predicts that
`W(x)` correlates with true per-pixel blur severity at `r > 0.9`. But the document itself cites
Delbrück's refractory rate law `r = 1/(T₀ + Δ_refr)` and Gallego et al.'s "the larger the refractory
period the fewer events are produced by fast moving objects" — and Team 06 measured the effective
threshold moving 0.26 → 0.37 over 32 px of blur under a 300 µs refractory. So `N_exp(x)`
systematically *under*counts as blur grows, and `W(x)` systematically underestimates blur severity
exactly where blur is largest. Add AER bus saturation — which this team cites as its own motivation
— and the undercount worsens further under fast motion. Pillar 2's headline metric is predicted to
fail by pillar 1's own physical argument.

**5. Other factual errors.**
- **Prediction P6 / SSI.** The `(k, T)` grid is a genuinely good design — separating the speed knob
  (timestamp rescaling, pixels byte-identical) from the exposure knob (averaging `N` source frames)
  is clean and, as far as I know, has not been run. But the prediction that "ours: iso-error contours
  fit `T` alone with `R² ≥ 0.9`" requires `W(x)` to measure `k·T` correctly, which (c) above says it
  does not at high `k`.
- **§Data.** The BS-ERGB row is marked "form-gated." Team 06 verified the pages render navigation
  only, with no links or forms. The row should read *unobtainable*. Since BS-ERGB is listed as the
  ideal vehicle for `W(x)` ("beam-splitter aligned ⇒ residual mismatch is purely temporal"), pillar
  2's real-data validation has no home.

**6. Claims exceeding evidence.**
- *"`W(x)` is the frame's temporal support width at pixel `x`, in change units, obtained by
  counting. Not a hyperparameter, not learned, not an attention weight."* It is a photometric
  excursion, it is biased low by refractory and bus saturation, and it is EDI's exponent.
- *"Blur *is* temporal support width; the event count *is* the blur severity."* Only where the
  contrast gradient is above threshold. In flat or low-contrast regions blur exists and events do
  not, which is the case the frame branch is there for.
- The document's own self-score is honest about pillar 1 ("SITS with a theorem" is a live jab; the
  observation is taken by ASTW and only the formulation is left). I would go further: I could not
  verify ASTW, SECNet or Neural Events at all, so the differentiation argument on which pillar 1's
  novelty rests is entirely unaudited.

**7. The hostile experiment.** "Take a low-contrast edge sweeping across a pixel during the exposure,
show me `W(x) = 0`, and show me the frame is blurred." Five minutes in the analytic simulator, and it
decides whether the `1/W` weighting and the SWC metric mean anything.

**8. Ranked fixes.**
1. Restate `W(x) = 0` as `|ΔL| < C` — a bound with an associated uncertainty — and rebuild the
   fusion weight from that bound rather than from an assumed zero.
2. Model the refractory/saturation undercount explicitly in `W(x)`, or restrict SWC claims to the
   low-blur regime where the undercount is negligible — which is the regime where the phenomenon
   does not matter.
3. Cite EDI's exponent explicitly as the same quantity, and Team 06's `a_p` if these two ideas ever
   meet.
4. Publish the *coordinate and the theorem* (pillar 1) alone and early, as the document's own verdict
   recommends, and drop pillar 2 rather than defending it.
5. Circulate the FE108 host-dead finding to Teams 01, 02, 04 and 07 today.

---

## "This is just deblurring" audit

For each idea: the strongest form of my objection, then the verdict.

### 01 — Latent exposure support
**Strongest objection.** *EDI (CVPR 2019) wrote `B = (1/T)∫L dt`. REFID/ECCV 2022 handled unknown,
auto-exposure-varying exposure. EBFI-BE (CVPR 2023) estimated the lost exposure prior from blur +
events. TbD (2019) and TbD-3D/DeFMO/Motion-from-Blur recovered intra-exposure Bézier trajectories
and invented Trajectory-IoU, which you adopt. Gupta 2010 established that the frame determines the
dwell measure. Blur-kernel reversal invariance is textbook blind deconvolution. Your Proposition is
those four facts and a change of variables. You applied blind exposure estimation to boxes.*

**Verdict: SURVIVES ONLY IN TASK SPACE.** The proposition collapses; every clause of it is citable
to 2006–2021. What survives, and survives cleanly: (i) the **TSB law measured on other people's
checkpoints and other people's benchmarks** — a signed, motion-direction-conditioned localization
bias in a *task* metric, which no restoration paper contains because restoration has no task head
whose implicit convention could be biased; (ii) the **free-lunch scalar** — one number per dataset,
zero learned parameters, removing a chunk of a published cross-dataset gap; (iii) **SIE in
milliseconds against DSEC's published exposure timestamps**, which is a real-data validation of the
central latent that no deblurring paper has run because deblurring papers do not need `T` in
absolute units. Lead with (i)–(iii). If the paper leads with the proposition or the architecture, it
collapses into EBFI-BE + TbD and I would reject it.

### 02 — Exposure-occupancy measures as the label
**Strongest objection.** *The occupancy measure is Gupta's Motion Density Function (2010) and you
say so. Predicting a support curve plus a dwell density from blur is Exposure Trajectory Recovery
and TbD-3D. Frame-gives-mass / events-give-order is the EDI decomposition restated. So: you renamed
the blur kernel and put a conformal wrapper on it.*

**Verdict: SURVIVES.** This is the case the brief told me to defend, and it earns the defence. The
*object* is old; the *place it lives* is new. ETR and TbD-3D recover a dwell density **of pixels, to
make a sharper image**. Team 02 makes the occupancy measure the **supervision target of a semantic
state**, treats the annotation functional `A` as a latent to be fitted by EM from point labels, and
scores set-valued predictions on point-labelled benchmarks with coverage that marginalizes over the
benchmark's own unknown convention. None of those four has a counterpart in restoration, and none
could have: restoration has no labels, no annotation convention, and no leaderboard whose ordering
could be shown to depend on an unwritten habit. The acceleration-vs-blur-magnitude result is a
finding about *label well-posedness*, which is a property of a benchmark, not of an image. And the
time-reversal pair is used correctly — to prove that events are *necessary*, not merely helpful,
which is exactly what the domain's "no plain fusion" constraint demands.

### 03 — Temporal support fields
**Strongest objection.** *Your frame-branch support `μ̂_F` is a per-pixel dwell density — that is
Exposure Trajectory Recovery, and your `L_ren` is EDI with `Unif(T)` replaced by a learned kernel,
which is what a coded-exposure deblurring formulation already is. Your "effective support is
narrower than the exposure and content-dependent" is the occupancy window that ETR models per pixel.
And your matched-blur pairs are not matched: the PSF shape is the dwell density, so your (A) and (B)
frames look different and your inexpressibility number is wrong.*

**Verdict: SURVIVES ONLY IN TASK SPACE — and the surviving part is not what the paper leads with.**
The frame branch collapses into ETR + EDI-with-a-learned-kernel. What survives is genuinely
non-restoration: the **event-branch support** (the inter-event interval as a measure with mass, with
free real-data ground truth), the **sub-probability mass channel** that makes "no observation here"
a representable output, the **overlap operator** as the fusion kernel, and **abstention at a queried
instant**. Those are worth a paper. The paper as written leads with the frame branch and with a
confounded experiment, so as submitted it does not survive.

### 04 — Effective timestamp of a fused prediction
**Strongest objection.** *REFID says the deblurred image's timestamp is conventionally the exposure
midpoint. EVDI needs the exposure known exactly. E-CIR and UniINR emit a latent at a queried instant.
You are re-observing that a restored frame has a chosen timestamp.*

**Verdict: SURVIVES.** This is the cleanest survival in the batch, and the reason is structural. A
generative reconstruction *must* be indexed by a time, because you cannot render an image without
choosing when. A discriminative task head is not indexed at all — it emits a box, and the box has no
time coordinate anywhere in its type. So the question "what time is this box about?" cannot be asked
of any restoration method and cannot be answered by importing one. `τ̂` and, decisively, **within-
frame `σ_τ`** — the claim that one output tensor carries several timestamps at once — are quantities
that do not exist in image space at all. `L_frame` is EDI's integral imported into a task head, and
the team says so; that is the small half. The diagnosis is the paper and the diagnosis is not
deblurring.

### 05 — No offset can fix a width
**Strongest objection.** *A box has sinc nulls: Raskar, coded exposure, SIGGRAPH 2006, and the whole
flutter-shutter line exists because of it. The photoreceptor low-pass is standard and is modelled by
v2e, IEBCS and, in 2024, by Deblur e-NeRF (ECCV 2024). Your "support-matched comparison," which
stays at the noise floor in Panel B, is EDI's forward model — rendering the event-derived latent
through the frame's exposure integral. Your T1 is one line of Fourier analysis. You have re-derived
that EDI's forward model is correct and given the residual four acronyms.*

**Verdict: SURVIVES ONLY IN CALIBRATION SPACE, and thinly.** T1, T2 and Panel B collapse. T3 is
multichannel blind deconvolution identifiability, transplanted competently but transplanted. What
survives is one measurement in a literature my objection does not reach: **OBD** — that on a rig
whose true offset is exactly zero, the best-fit offset drifts by ≥3 ms as the calibration motion gets
faster, so EF-Calib's and eKalibr's sub-millisecond `t_d ± σ` is estimating a quantity that is not a
rig constant. That is a real finding aimed at event–frame temporal calibration, not at restoration.
It is one number, and the paper must be built on it rather than on the notch spectrum.

### 06 — The exposure gap
**Strongest objection, and it is the team's own.** *mEDI Eq. 5 is `B̃ = L̃(f) + J̃(c)` with
`J(c) = (1/T)∫exp(c·E(t))dt`. You keep their symbol. So the residual is not unmodelled — it is
EDI's own term, published in 2019/2020. `J = ½Var_W(L)` is the second-order cumulant expansion of
a log-mean-exp, which is a footnote. And you verified yourself that the identity is "never used as
an actual training loss," so there is no trained bias to indict.*

**Verdict: COLLAPSES — into mEDI (Pan et al., TPAMI 2020).** This is the clearest collapse in the
batch and the document establishes it against itself. The residual the paper says is genuinely
unmodelled is exactly what EDI's exposure integral already accounts for; the paper's own related-work
table says so in the first row.

What does *not* collapse is P7 — the demonstration that the standard two-frame least-squares
contrast-threshold estimator has a motion-dependent bias that flips its sign, on a physically
perfect sensor, with a closed-form correction — together with the identifiability result that two
exposure functionals recover the per-pixel threshold, better the faster the motion. That is a real
contribution to *event-camera characterization*, not to deblurring, and it should be the paper.

### 07 — Chronofields
**Strongest objection.** *Your L4 is EDI with the variables swapped and you say so. The dwell-time
change of variables `B = (1/T)∫L·(∂τ/∂L)dL` is "the blur kernel is a dwell histogram" — Gupta 2010.
Your F2 bias `aT²/(24 v̄)` is a statement about where the centroid of a blur streak sits relative to
the mid-exposure position, which is a fact about blur kernels. Time surfaces put time on the input
side; UniINR (ECCV 2024) puts the exposure interval on the query side. You moved it to the output
and called it a chronofield.*

**Verdict: SURVIVES ONLY IN TASK SPACE.** L4 and F2 collapse into EDI + Gupta. What survives is the
*statistical type assignment*: an event is an uncensored time observation, a frame is an
interval-censored one, a non-occurrence is right-censored, and the `∅` atom makes "this never
happened" a representable output. Survival analysis has never been applied to event-camera
perception, and no restoration method can produce a calibrated distribution over *when*, because
restoration's output is indexed by a time the user chose rather than a time the model infers. The
temporal eikonal `∇_u τ · v = 1` is also genuinely new as a *stated constraint*, though the team is
right that it is optical flow's slowness field and that this is the dangerous version of the
objection. The C1 anchor — supervising next-crossing-time with held-out real events — is the one
experiment here that is unambiguously not deblurring.

### 08 — Right place, wrong time
**Strongest objection.** *You do not touch pixels, so I have almost nothing. The one place you enter
my field is the claim that PSNR against a finite-exposure reference prefers a blurred prediction —
and that is a known irritation in event VFI, which is why Time Lens's HS-ERGB used a high-speed
strand with short exposures.*

**Verdict: SURVIVES.** My objection does not reach it. The entire deliverable is in metric and
ground-truth space: an error unit of (pixels ⊥ to motion, milliseconds ∥ to motion), `τ̂` per
published checkpoint, and the label-forensics result that the flagship high-rate ground truths are
their own interpolation priors. There is no restoration formulation into which any of that could
collapse. The event-VFI observation is correct and, in fact, the team should press it harder: it is a
statement about how the interpolation literature scores itself that the interpolation literature has
not made.

### 09 — Change-time
**Strongest objection.** *`W(x) = C·N_exp(x)` is `c·E` over the exposure — EDI's exponent. You have
renamed a photometric excursion as a temporal support width, and Team 06 derived the same scalar
independently under the name `a_p`. Your claim that `W(x) = 0` means the frame is a sharp
instantaneous observation is false: zero events means `|ΔL| < C`, a bound. And refractory dead time
makes `N_exp` undercount exactly under fast motion, so your measured "support width" is biased low
precisely where blur is largest.*

**Verdict: pillar 2 COLLAPSES — into EDI (Pan et al., CVPR 2019).** The frame-side half, which is
the half that answers the assigned seed, is EDI's exponent with a new name and a false corollary
attached. Pillar 1 (the counting clock and its exact monotone-reparameterization invariance) is a
representation-learning claim my specialism does not govern; it neither survives nor collapses under
my objection, and it needs the reviewer who owns event representations.

### 10 — Fusion is ill-typed
**Strongest objection.** *Proposition 1 is true, two lines long, and the restoration field has been
acting on it since at least EFNet's SCER (ECCV 2022), which is exactly a `render`-to-frame-type of
the event stream referenced to the exposure — and you credit it. EDI's forward model is
`render ∘ lift`. EVDI's learnable double integral is a learned `lift` + `render`. AKF is `lift` +
`render` as a filter. E-CIR, UniINR and Neural Image Re-Exposure all route both modalities through a
continuous-time latent. So your mechanism is fully occupied, and what is left is bookkeeping.*

**Verdict: SURVIVES ONLY IN AUDIT SPACE.** The type system, the operator and Prop. 1 all collapse
into EFNet-SCER / EDI / EVDI / AKF, and the team concedes each. What survives is the **audit**: a
cross-model measurement, on published checkpoints, of what fusion blocks are actually mixing, with a
Jacobian-influence diagnostic that works on gates and AdaIN and not only attention. That is a
statement about other people's models and no restoration paper contains it. But I must flag that the
audit's headline prediction — event utility *falls* with speed — is one I expect to be falsified on
the deblurring models in its own list, where the documented behaviour is the opposite. Run EFNet
first.

---

## Ranking

1. **Team 08 — Right place, wrong time.** The only idea my objection cannot touch, the only one
   whose central result (label forensics on a 4.7 MB file, zero GPU) cannot be taken away by a host
   going offline, and the only one that pre-registers a prediction from architecture and commits to
   reporting misses.
2. **Team 04 — When is your prediction?** `σ_τ` is a quantity no restoration formulation can produce
   even in principle, the three-day zero-download pilot is the best de-risking here, and the
   frame-only/event-only control can kill the paper's own framing — which is why I trust it.
3. **Team 02 — Exposure-occupancy measures.** The best reframing in the batch: the occupancy measure
   moved out of image space into supervision and evaluation space, with a latent annotation
   convention and convention-marginal conformal coverage. Ranked third only because its primary real
   instrument (FE108) appears to be offline.
4. **Team 01 — Latent exposure support.** Real assets (the free-lunch scalar, SIE against DSEC's
   published exposures) attached to a proposition that is an assembly of published parts, one
   falsified sub-prediction, and a dead primary dataset.
5. **Team 10 — Fusion is ill-typed.** Good, cheap audit design with an honest self-assessment;
   ranked here because its headline empirical prediction is at serious risk of inverting on the
   deblurring models it names.
6. **Team 05 — No offset can fix a width.** Sound physics, competent transplant, but the surviving
   deliverable is one number and the real-data onset requires exposures DSEC only supplies on six
   sequences.
7. **Team 07 — Chronofields.** The most interesting output type in the batch, undermined by a
   headline number computed outside its own derivation's validity regime and by a live killer
   baseline that must be run on a dataset that has gone dark.
8. **Team 03 — Temporal support fields.** Good event-side idea, fatal frame-side experiment: matched
   blur extent is not matched blur, because the dwell density is the PSF.
9. **Team 09 — Change-time.** Pillar 1 may be a fine paper for another reviewer; pillar 2, the half
   that answers the seed, renames EDI's exponent and rests on a false corollary that refractory
   undercounting would break anyway.
10. **Team 06 — The exposure gap.** The most careful document here, and it establishes its own
    collapse into mEDI on page one while indicting a training term it verified nobody uses.

---

## My winner and its fatal flaw

**Winner: Team 08, *Right Place, Wrong Time*.**

I would fight for it in the AC discussion, and I want to be explicit that I am not choosing it
because it is the most novel — Team 02's is — but because of what the brief asked me to weigh. Of
the ten, it is the only one whose central result survives every dataset failure this batch has
discovered. FE108/FE240hz refuses connections; BS-ERGB and Time Lens++ have gone dark; four ideas
lose their primary real-data figure to those two facts alone. Team 08's E0 needs a 4.7 MB label
file and no GPU, and its E1–E3 checkpoints and preprocessed tarballs were verified live by HTTP HEAD
on 2026-09-01. It trains nothing. It proposes no method — which is the strongest possible answer to
"you invented a metric your own method wins on," and it is the only team that can make that answer.
And it is the only idea in the batch against which my specialism has no purchase at all: there is no
restoration formulation into which "the unit of detection error should be (pixels ⊥, milliseconds ∥)"
can collapse, because restoration has no detection error.

Its second result is independent of its first, which is the risk structure I want: even if no ranking
flips, the finding that the inter-frame ground truth of DSEC-Det and DSEC-3DOD is, to within a
measured IoU, its own linear-interpolation prior, is a benchmark-integrity result that stands alone.

**Its fatal flaw: the one parameter the paper insists is not free is mis-specified for every model it
tests.**

The whole defence against "you gave every prediction a free translation" is that
`τ_max = (w_G + w_P)/2` is read off the benchmark's and the method's own published specifications
rather than tuned. `w_P` is taken to be the representation window — 50 ms, from RVT's
`stacked_histogram_dt=50_nbins=10`, which the brief confirms is built backwards from the label
timestamp. But **RVT is recurrent.** It carries LSTM state across the sequence; S5-ViT carries SSM
state; DAGr carries a graph-structured memory. The temporal support of a recurrent detector's output
is not the width of its input representation — it is the whole sequence, with an unknown decay
profile. So `w_P = 50 ms` is the support of the *tensor*, not of the *prediction*, and the paper is
about exactly that distinction.

This is not a detail. If `w_P` is understated, `τ_max` is understated, `AP^⟂` is an arbitrary
relaxation rather than a principled one, `Δ_TS` is not interpretable, and the C3 pre-registered
prediction (`τ̂ ∈ [−35, −10] ms` from a `t − 25 ms` centroid) is a prediction from a quantity that
does not describe the model. Worse, the failure mode is silent and self-confirming: a recurrent model
whose true centroid is at, say, `t − 60 ms` would produce a `τ̂` outside the registered interval, and
the natural reading — "C3 missed" — would be recorded as a failure of the *metric* when it is a
failure of the *specification*.

The fix is one experiment and it should be the first GPU job in the plan: truncate the recurrent
state at `k` steps, re-run inference, and measure `dτ̂/dk`. The value of `k` at which `τ̂` stops
moving is the measured `w_P`. That turns the paper's weakest assumption into one more measured
quantity — which is, after all, what the paper is for.
