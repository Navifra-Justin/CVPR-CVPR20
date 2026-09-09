# Reviewer 09 — Area Chair report

**Round:** CVPR20 idea selection, Temporal-Support-Aligned Event–RGB Perception.
**Role:** Area Chair. I am not checking correctness; nine other reviewers do that. I decide which of
these becomes a paper the community remembers, and I am accountable for the choice.

A note on the verdict scale. This is a selection round with ten candidates and one slot. My verdicts
are relative rankings, not accept/reject decisions on a submission. BORDERLINE here means "not the
one to build, and here is the single structural reason", not "this could never be a paper".

---

## Comparison set

Fetched and verified this session from the CVF awards listing and from arXiv. These are the standard
I am holding the ten ideas to.

| Paper | Venue | Standing | What made it land |
|---|---|---|---|
| **VGGT: Visual Geometry Grounded Transformer** (J. Wang et al.) | CVPR 2025 | **Best Paper** | One feed-forward network replaced an entire optimisation pipeline that everyone had accepted as necessary. It landed because it deleted a stage, not because it improved one. |
| **Neural Inverse Rendering from Propagating Light** (A. Malik et al.) | CVPR 2025 | **Best Student Paper** | It took the *measurement operator* of a transient sensor seriously — light in flight, not light at an instant — and built the estimator that operator actually licenses. This is the closest structural analogue to what these ten teams are attempting, and it is the model to imitate. |
| **EventPS: Real-Time Photometric Stereo Using an Event Camera** (B. Yu et al.) | CVPR 2024 | **Best Paper Honorable Mention** | The only event-camera paper in recent award lists. It landed by finding the task for which the sensor's continuous per-pixel output is *the natural observation*, rather than by fusing events into an existing frame pipeline. Note what it is not: it is not a fusion module and it is not a benchmark critique. |
| **Spatially-Varying Autofocus** (Y. Qin et al.) | ICCV 2025 | **Best Paper Honorable Mention** | It made a scalar capture parameter into a *field over the image* and showed the field was the right object. This is the exact move Teams 3, 4, 9 and 10 are proposing on the time axis, and its acceptance is the precedent they should cite. |
| **Rich Human Feedback for Text-to-Image Generation** (Y. Liang et al.) | CVPR 2024 | **Best Paper** | A dataset-and-measurement paper with no new architecture. Proof that the "contribution to the field, not the leaderboard" genre wins at CVPR when the artifact is reusable by everyone. |
| **State Space Models for Event Cameras** (Zubić, Gehrig, Scaramuzza) | CVPR 2024 | Highly cited within a year; the reference event backbone since | It landed by identifying a *specific brittleness* — event models break when the inference-time window differs from training — naming it, and removing it. A narrow, measurable, architecture-level claim, cleanly falsifiable. |
| **Ev-3DOD: Pushing the Temporal Boundaries of 3D Object Detection with Event Cameras** (Cho, Kang, Kim, Yoon) | CVPR 2025 | Highlight | It landed by *creating the evaluation regime* (100 FPS "blind time" GT) in which its sensor could be shown to matter. Directly relevant: it is also the paper whose 53.6 → 33.3 mAP online/offline gap Team 8 proposes to rename. |
| **MegaSaM** (Z. Li et al.) | CVPR 2025 | Best Paper Honorable Mention | Robustness on casual, uncontrolled video — it won on the regime nobody could handle, not on the benchmark everyone reports. |

Two calibrations I draw from this set, and apply below.

1. **Every one of these is believed from its first figure.** Not one requires the reader to accept an
   invented axis before the plot means anything.
2. **The two measurement-operator papers (Neural Inverse Rendering, Spatially-Varying Autofocus) both
   deliver a working estimator, not only a diagnosis.** A pure critique paper can win here (Rich Human
   Feedback did) but only when it ships an artifact other people will use.

---

## Per-idea verdicts

| # | Title (short) | Verdict | One-sentence reason |
|---|---|---|---|
| **01** | A Frame Is Not a Timestamp | **ACCEPT** | The best-argued framing in the set and a free Figure 1a from DSEC metadata, but its money plot depends on FE240hz, which one other team reports as an unreachable host. |
| **02** | Exposure-Occupancy Measures as the Prediction Target | **BORDERLINE** | The whole paper is conditional on annotation-convention spread being large on real data, and its only vehicle for measuring that is the same contested dataset. |
| **03** | Temporal Support Fields | **BORDERLINE** | The headline x-axis (support overlap `O*`) exists only inside the authors' simulator, and the matched-pair construction does not actually match event counts under any non-ideal sensor. |
| **04** | When Is Your Prediction? | **ACCEPT** | `σ_τ > 0` — the prediction has no single timestamp — is the sharpest single claim anyone made, and it is the one thing that defeats "just recalibrate"; but this is Team 1's paper with a better kill shot and a worse real-data plan. |
| **05** | No Offset Can Fix a Width | **ACCEPT** | The cheapest theory tier in the set and a phenomenon guaranteed by the Fourier transform of a box, but it will be read as deblurring and its real-data regime is exactly where the brief warns displacement is unestablished. |
| **06** | Frames Are Not Samples (the exposure gap) | **STRONG ACCEPT** | The only team that has already run its experiment, verified its data and checkpoints at the file level, and can put a measured scatter plot about `y=x` on page one. |
| **07** | Chronofields (predict *when*) | **BORDERLINE** | The team states its own falsification criterion honestly and it is a criterion the paper may fail: reconstruct-to-1000fps-then-detect might simply match it. |
| **08** | Right Place, Wrong Time | **STRONG ACCEPT** | It produces a number in milliseconds, on other people's released checkpoints and other people's benchmarks, from a 4.7 MB label file and no training — the highest leverage per unit of risk in the round. |
| **09** | Change-Time (per-pixel clocks) | **BORDERLINE** | Its make-or-break experiment is defined entirely against the hyperparameter table of a CVPR 2026 paper that nobody in this round could verify. |
| **10** | Fusion Is Ill-Typed | **BORDERLINE** | The diagnostic instrument — zeroing the event branch — measures out-of-distribution brittleness, not information contribution, so the headline curve does not mean what the paper needs it to mean. |

---

## Detailed review

Rubric's eight items. Deepest on 08, 06, and the 01/04 pair.

---

### Idea 08 — *Right Place, Wrong Time* — **STRONG ACCEPT**

**Summary (proving I read it).** The claim is not about frames; it is about the *unit of error*. The
team observes that every event benchmark scores in pixels and that a pixel cannot express a time, so
the field's dominant fast-motion failure — being at the right point on the object's path at the wrong
instant — is structurally forced into the `loc` bucket. They then note that the fix is one line of
geometry borrowed from air-traffic surveillance: project the box-centre error onto the GT track
tangent, divide by speed, and the residual has units of milliseconds. The instrument set is what
convinced me: RVT and S5-ViT consume the *identical* preprocessed tarballs (removing every
preprocessing degree of freedom a reviewer could attack), BFlow ships event-only and event+image
checkpoints of the same architecture and training recipe (a genuine single-variable manipulation of
temporal support width, released by someone else), and DAGr's repo already contains
`run_test_interframe.py`, which writes exactly the artifact the re-scorer consumes.

**Strongest reason to accept.** E0. Two days, no GPU, a 4.7 MB label file: measure how much of DSEC-Det's
and DSEC-3DOD's advertised high-rate ground truth is recoverable from its own linear-interpolation
prior. If that number is high — and the authors of both datasets state in print that their inter-frame
labels *are* linear interpolations — then the two flagship low-latency event benchmarks are partly
scoring agreement with a constant-velocity assumption, and every inter-frame mAP in the literature
inherits it. That is a publishable result on its own, obtainable before anyone downloads a single
event file, and it is independent of whether the rest of the paper works. No other idea in this round
has a first experiment with that risk/reward shape.

**Strongest reason to reject.** The algebra is borrowed and the team says so. A reviewer who knows the
tracking-metric literature writes "this is along-track/cross-track error" in one sentence, and they are
half right. The defence has to be that the *setting* is what makes it decisive, and that defence is
carried entirely by the anisotropy control `R`.

**Factual errors.**
- §4 P1 predicts `τ̂ ∈ [−35, −10] ms` and glosses the RVT window centroid as a prediction of network
  behaviour. The brief is explicit: `t−25 ms` is the uniform-weight centroid, and "whether the trained
  network weights the ten bins uniformly is unmeasured, so 25 ms is a reference point, not a prediction
  of network behaviour." Correction: state C3 as *"the measured `τ̂` is consistent with / departs from
  the uniform-weight centroid of the declared window by X ms"*, and report the departure as a finding
  about learned bin weighting rather than as a confirmation of an architectural prediction. The wide
  [−35, −10] interval already anticipates this; the prose does not.
- §2, DSEC-Flow row: "MVSEC is documented in the flow literature as lacking temporal synchronization
  with the ground truth" is second-hand and needs a citation at source before it appears in a paper.

**Claims whose strength exceeds their evidence.**
- Thesis: *"the ranking is not the ranking mAP reports."* P6 requires only that **at least one pair**
  swaps, under stated magnitude conditions, and Death 1 concedes no flip may survive. The thesis
  sentence promises a general reordering the pre-registration does not.
- P5: *"≥ 5 % of `M` values exceed 0.3 … i.e. the failure exists but is diluted."* This sits badly
  against the abstract's *"the dominant error mode under fast motion."* Dominant on 5 % of the data is
  not dominant; say "dominant on the top-`M` decile" everywhere, including the abstract.
- §Death 3: *"a shared `τ̂` is itself a publishable finding."* Probably true, but it is a much smaller
  paper than the one the abstract sells, and the abstract should not be written as if the method-level
  component is assured.

**The experiment a hostile reviewer demands.** The isotropic null. `AP^iso` at equal relaxation budget,
and the per-pair distribution of `cos²θ` between the error vector and the motion tangent, with bootstrap
CIs. Under isotropic error `E[cos²θ] = 0.5`. **Its absence is fatal** — without it, `AP^⟂ ≥ AP` is
tautological and the entire metric family is loosened IoU wearing a lab coat. To the team's credit it
is already designed in as C1. My instruction is to promote it from "control" to **week-1 go/no-go gate**,
run on Gen1 alone before the 190 GB gen4 download starts.

**Ranked fixes.**
1. Run C1 (anisotropy `R`) on Gen1 in week 1 and treat `R ≈ 0.5` as a kill. Nothing else is worth
   starting until that number exists.
2. Run E0 in parallel; it needs no GPU and no event data and it de-risks the paper independently.
3. Rewrite the thesis and abstract to promise what the pre-registration promises (a measured latency in
   ms per method, plus a flip on the high-`M` slice), not a general reordering.
4. Re-state C3 per the brief's caveat on RVT bin weighting.
5. Finish the prior-art sweep on event-vision streaming/latency metrics *before* E1 — this is the one
   idea whose contribution could be wholly pre-empted by a single paper, and the team says its search
   budget ran out mid-survey.
6. Add Team 4's within-frame dispersion `σ_τ` as a second panel (see Merge analysis).

---

### Idea 06 — *Frames Are Not Samples: The Exposure Gap* — **STRONG ACCEPT** (runner-up)

**Summary.** The bridge identity the whole event–frame literature stands on, `∫events = Δ log I`, is not
noisy — it is misspecified, because a frame is `log` of a time-average and the identity treats it as the
time-average of a `log`. The gap has a closed form, `J = ½·Var_W(L)`, it is zero only for a point support,
and it is the *same object* mEDI already writes as `J̃(c)` and everyone downstream drops. The team is
unusually precise about who assumes what: it explicitly refuses the sentence "every method assumes this"
after checking that Time Lens++, TimeReplayer, E2VID and the EVDI line do not, and it names the exact
place the effect was seen and dismissed — Scheerlinck, Barnes & Mahony, ACCV 2018, §3.1, *"we believe the
difference will be insignificant … and we do not consider this further"* — a belief that has stood eight
years untested.

**Strongest reason to accept.** The experiment has already been run. Slope of the residual against a
**zero-free-parameter, events-only** predictor is 0.955 with `R² = 0.779` on a physically *perfect*
sensor, against a noise null of `R² = 0.0015`; on band-limited translating texture it is 0.997 and
`R² = 0.99`. And P7 is a table I would remember: run the field's standard contrast-threshold calibration
recipe on an ideal sensor and `ĉ` collapses from 0.189 to **−0.004** as blur grows — the calibrated
threshold changes sign purely as a function of how fast the calibration target moved. Every other team in
this round is projecting numbers. This one is reporting them.

Second, and I weight this heavily given the operational brief: Team 6 is the only team that checked
whether the baselines will *build*. It correctly identifies that the binding sm_120 question is not the
README's torch pin but whether a repo compiles custom CUDA, verifies that EFNet/REFID/EVDI/E2VID/ELEDNet
do not and that GEM and CBMNet do, and deprioritises the latter. It also found that BS-ERGB is dark and
said so instead of planning around it. That is the operational competence that survives ten weeks on a
shared 9 GB card.

**Strongest reason to reject.** The delta over EDI/mEDI is genuinely small and the team's own novelty
self-score of 7/10 is the honest one. mEDI Eq. (5) already contains the exposure functional. The
contribution reduces to: the second-order form of a term someone else wrote, plus the demonstration that
the field drops it, plus a one-line fix. A reviewer who reads only the method section sees a corrected
loss term. This is a paper that will be accepted and cited by the few hundred people who compute contrast
thresholds; it is not a paper that changes what everyone else does.

**Factual errors.** None found that I can check against the brief. The DSEC claim — that it is the only
public event–frame dataset shipping real per-frame exposure intervals — is consistent with the brief's
independent verification of `<seq>_image_exposure_timestamps_left.txt`. Two verification gates are
flagged by the team itself as open (Brandli et al. ISCAS 2014, paywalled; *Electronics* 15(7):1420 (2026)
"Movement-Aware Polarity Integration", 403) and both must close before an introduction is written. The
second title is, as they say, uncomfortably close.

**Claims whose strength exceeds their evidence.**
- Thesis-position sentence: *"on textured content — which is what natural video is — the residual is 2.6
  contrast thresholds and 99 % of it is the exposure operator."* This is a v2e simulation on a
  band-limited translating texture, presented in the position where readers take it as a property of
  natural video. Restate as measured-in-simulation until DSEC confirms it.
- *"a component of it is a measurement artefact"* (P7) is correctly hedged in §Failure, but the one-line
  thesis and the Korean summary both read as if the published speed-dependence of `c` is the artefact.
  Keep the hedge everywhere; it is the difference between a strong result and an unsupportable one.

**The experiment a hostile reviewer demands.** P6 at network scale: train on short-exposure/slow motion,
test on long-exposure/fast, and show the bias is *not* absorbed by capacity, with MCB as the readout.
The team has this at the level of a fitted linear model (0 % / 51 % / 91.2 %); a reviewer will demand it
for an actual trained network. **Its absence is not fatal** — the paper degrades to a measurement plus a
free correction, which is defensible — but it is the difference between "diagnosis" and "indictment".

**Ranked fixes.**
1. Close the two verification gates before writing. The *Electronics* 2026 title is a live scoop risk.
2. Move the DSEC real-data regression `R ~ P` to week 1. It needs only events, two frames and the
   shipped exposure windows — no ground truth at all — and it is the single cheapest way to convert
   "simulation result" into "property of real data."
3. Run the cross-support generalisation experiment at network scale; it is the paper's spine as an
   indictment rather than a note.
4. Import Team 5's impossibility bound as a half-page proposition (see Merge analysis) and drop the
   restoration framing from the title.

---

### Ideas 01 and 04 — the same paper — **ACCEPT** (jointly)

I review these together because they are the same paper. Team 1's `α_model` (the model's learned implicit
position in the support) and Team 4's `τ̂` (the time at which the prediction would have been right) are
the same quantity under the change of variables `τ̂ = t₀ + α_model·T`. Both propose a trajectory head in
which `K = 0` recovers the current formulation exactly. Both make the frame's integral a loss term. Both
name the invariance-training line (FAOD's Time Shift) as the antagonist and give the same argument
against it.

**Summary.** After substituting `u = (τ−t₀)/T`, the exposure start and duration vanish from the image
formation equation exactly — the blurred frame determines the path and the dwell density and *nothing
else*, not even the direction of traversal. So the scalar in `image_timestamps.txt` is not a measurement,
it is an unfalsifiable prior baked into the dataloader, and the resulting localisation error is signed,
motion-direction-conditioned, present at the optimum, and averaged to zero by every metric the field
uses. Team 4 adds the part that matters most: because the evidence-weighted centroid is a function of
scene content, the effective timestamp is a **field over the image**, so two objects at different speeds
in one frame produce two different timestamps in one prediction tensor.

**Strongest reason to accept.** `σ_τ > 0`. Team 4 is right that `b ≠ 0` alone invites "subtract the
constant and go home", and that within-frame dispersion is the only observation that closes that exit.
A spatial heat map of the effective timestamp over a single frame, showing that one output tensor carries
several clocks, is the most memorable image anybody proposed in this round. Separately, Team 1's Figure
1a costs nothing and is already half-verified by the brief: DSEC's own exposure widths span 118 µs to
14 996 µs, a factor of 127, and vary 337 → 4207 µs frame-to-frame *within a single sequence*, while every
downstream method treats the frame period as 50 ms and constant.

**Strongest reason to reject.** Both papers' load-bearing real-data figure requires ground truth at
roughly ten times the frame rate, and the only public source is FE240hz/FE108. **Team 9 reports the host
`fe108.dluticcd.com` refused connection and marks it DEAD.** Teams 1, 2, 4 and 7 all plan on it; Team 1
calls it "the only real source of intra-exposure GT"; Team 4 calls it the "primary loop-closer." Exactly
one team checked, and the answer was bad. On a ten-week clock with no event data on disk, staking the
headline figure on an application-gated dataset that one reviewer reports as unreachable is the wrong bet
regardless of how good the framing is.

**Factual errors.**
- **Team 1, Fig 1a:** *"plot the left–right exposure-midpoint difference: prediction ≥ 1 ms on a
  substantial fraction of frames."* The brief measured this directly: the published `image_timestamp`
  equals the average of the left and right mid-exposures to within 1 µs, and the left/right divergence is
  a median of 16–144 µs with a maximum of 380 µs — **two orders of magnitude below the window width, and
  roughly an order of magnitude below Team 1's prediction.** This prediction is falsified before the
  experiment runs. The brief also instructs that an argument resting on left/right divergence be marked
  down. Delete the sub-claim; it is not needed and it is the kind of error that costs a reviewer's trust
  on page 3.
- **Team 4, §4.0:** `TEF = 1 − r_min/r_q` is defined by an argmin over the joint support, so it is
  inflated by construction whenever the GT trajectory passes near the prediction for any reason. The team
  partly guards this with the identifiability margin, which is the right instinct, but the headline gloss
  *"90 % of what the community reports as a fast-motion localization failure is a clock failure"* does not
  survive the definition. Report TEF only on segments above a stated curvature threshold, and report the
  retained fraction.

**Claims whose strength exceeds their evidence.**
- **Team 1:** *"this removes ≥ 40 % of the excess error at `d > 15 px` … zero learned parameters, one
  number per dataset."* The free-lunch shift needs `d̂`, an estimated intra-exposure displacement. The
  brief is explicit that crossings-per-firing-pixel near 1.10 "is not a displacement measurement, and no
  team may claim displacement from it without measuring flow or IMU." The shift is therefore not free;
  it costs a flow estimate. Say so.
- **Team 1:** *"the transfer degradation … is predicted by `(α_A − α_B)·d` to within 25 %."* A quantitative
  prediction about cross-dataset transfer, with no pilot behind it, on datasets not yet downloaded.
- **Team 4:** *"a detector whose output does not change when you shift the temporal support is a detector
  that has thrown time away."* Rhetorically excellent, and I believe it, but as written it asserts that
  FAOD's reported robustness is a pathology without having measured FAOD.

**The experiment a hostile reviewer demands.** Team 4 already names it and it is the right one: the
frame-only and event-only controls. A single modality has a single support, so the theory predicts
`σ_τ ≈ 0` for both and `σ_τ > 0` only under fusion. **If `σ_τ` is as large for the frame-only model, the
framing is wrong and the paper is about blur.** Absence is fatal. Team 1 has no equivalent control.

**Ranked fixes.**
1. **Establish FE240hz access, or a substitute, in week 1.** Team 9's report must be independently
   checked. If it is dead, the fallback is EVIMO2 (200 Hz Vicon, ~40 GB, direct download, named by Team 2
   and Team 4) in pose space — and the paper's real-data claim changes from detection to 6-DoF pose,
   which is a different paper and should be planned as one now rather than in week 6.
2. Delete Team 1's left/right divergence sub-claim.
3. Run Team 4's frame-only / event-only `σ_τ` control before anything else; it is three days.
4. Merge. See below. Two teams should not spend ten weeks writing the same paper.
5. Cut the invented metrics from four (Team 1: TSB, TQ-AUC, SCR, SIE) to two. "You invented four metrics
   and won on all of them" is a review that writes itself.

---

### Idea 02 — *Exposure-Occupancy Measures* — **BORDERLINE**

**Structural problem, one sentence:** the paper's existence is conditional on annotation-convention spread
being large on real data, and its only vehicle for measuring that is the same possibly-dead FE108.

**Summary.** The label attached to a frame is an unstated functional `A` of the state's occupancy measure
over the exposure — mid, mean, mode, hull, core — and no benchmark in vision states which `A` it used. The
sharp consequence, and the best idea in the write-up, is that label ill-posedness is governed by
intra-exposure **acceleration**, not blur magnitude: at constant velocity every convention agrees exactly,
no matter how severe the blur. The reformulation predicts the measure, recovers the convention `π` by EM
as a latent, and certifies with convention-marginal conformal coverage.

**Strongest reason to accept.** The `β`-matched `ν` sweep is a genuinely clean experimental design, and
the predicted null at `ν = 0` (severe blur, perfectly well-posed label) is good science: a paper that
pre-registers where its effect must *vanish* is more credible than one that only predicts where it
appears. And prediction 3 — that a convention switch moves a single model's RSR by 10–20 points while the
spread between five published trackers is 3–8 — is the single most quotable sentence anyone wrote.

**Strongest reason to reject.** Two hard reviews are pre-loaded and the team knows it: "this is aleatoric
uncertainty with extra steps" and "AFNet already tracks at 240 Hz." The counter is Propositions 1–2 and
the time-reversal pair, which require the reviewer to engage with theory before the figure means anything.
Against my comparison set, that is the wrong shape.

**Overclaim.** *"A quarter of the remaining headroom on this benchmark is definitional, not learnable"* —
derived from an oracle floor `e*` computed on a dataset that has not been downloaded.

**Hostile experiment.** A1: frame-only ≈ 50 % on time-reversal order accuracy, both ≈ 100 %. Not fatal
if absent, because it is a construction, not a benchmark — but it must be Figure 2, not an appendix.

**Fixes.** (1) Move to EVIMO2 as primary now, not as fallback — the team's own observation that
in-exposure rotation makes `A_mean ≠ A_mid` geometrically unavoidable even at zero linear acceleration is
the strongest real-data argument in the document and it lives in pose space. (2) Honour the day-7 kill
criterion literally. (3) A7 (the drop-in loss reweighting) is not optional; it is what converts "your
benchmark is broken" into something a reviewer can use.

---

### Idea 03 — *Temporal Support Fields* — **BORDERLINE**

**Structural problem:** the headline axis exists only inside the authors' simulator.

**Summary.** Predict, per pixel and per branch, a sub-probability measure on the time axis — mass for
"is there any evidence at all", shape for "when is it from" — and replace similarity-based cross-attention
with an overlap of supports, so that non-overlapping observations are refused aggregation regardless of
feature similarity. The sub-probability (mass ≤ 1, not = 1) is genuinely load-bearing: it is what makes
abstention representable.

**Strongest reason to accept.** The event-branch support has exact ground truth on real data for free —
it is the inter-event interval, present in the raw stream, no annotation, no simulator. Half the
supervision is real by construction. That is a better answer to "you invented your ground truth" than any
other measure-valued proposal in this round.

**Strongest reason to reject, and it is a technical error not a taste judgement.** The matched-pair
construction claims *"Event counts are matched by construction (same `d`, same contrast, same threshold
⇒ same number of threshold crossings)"*. This is false for any sensor with a refractory period. The
dwell-then-dash condition concentrates every crossing into 0.2T, which raises the instantaneous rate
five-fold and destroys events through dead time — a mechanism this very idea set documents elsewhere
(Team 6 measures effective threshold moving 0.26 → 0.37 under a 300 µs refractory). So the pairs are
matched on blur but **not** on event count under any realistic sensor, and the entire "every covariate the
field regresses against is held fixed" argument fails. Prediction 2 (partial correlation) is the paper,
and this defect attacks it directly.

**Overclaim.** *"mean PSNR drops by ≥ 3.5 dB between `O* ∈ [0.7,1.0]` and `O* ∈ [0.0,0.3]`"* — every
number on that axis is an authors' construction evaluated on authors' data.

**Hostile experiment.** Ablation (vi): a model trained with **zero simulator labels**, real
self-supervision only. If it recovers most of the gain, the simulator is an instrument rather than a
crutch. Absence is fatal.

**Fixes.** (1) Fix or drop the event-count matching claim; re-derive the matched pairs under an explicit
refractory model and report the residual count mismatch. (2) Promote the free real event-side GT from a
risk mitigation to the paper's opening move. (3) Verify ASTW and RTEA exist as described before building
the related-work spine on them.

---

### Idea 05 — *No Offset Can Fix a Width* — **ACCEPT**

**Summary.** Temporal calibration in this field estimates a scalar — DSEC's `t_offset`, EF-Calib's `t_d`,
eKalibr's `t_d`, and even the CVPR 2024 latency work, which cites a photoreceptor low-pass and then keeps
only its first moment. But a shift is a unit-modulus linear-phase multiplier in Fourier and a support
mismatch has non-unit modulus with exact zeros; the shift group simply does not contain the operator that
relates the two channels. Hence T1 (an impossibility bound), T2 (the best-fit offset is a function of the
scene and the speed, not a rig constant), and T3 (a speed-sweep identifiability result — the event–frame
analogue of multichannel blind deconvolution).

**Strongest reason to accept.** The failure phenomenon is guaranteed to exist. It is a consequence of the
Fourier transform of a box, not an empirical hope, and it is demonstrated on data where the opposing
formulation is given every advantage: an ideal sensor, a true offset of exactly zero, and an oracle grid
search over the shift. The theory tier runs on CPU. Ablation 1 — global shutter, `τ = 0`, noiseless,
`δ* = 0` — kills every mundane explanation in a single table row and is scheduled first. Four days to a
thesis-level go/no-go is the second-best risk profile in the round.

**Strongest reason to reject.** "Isn't this deblurring?" and "the sinc null is Raskar 2006" are both
available in one sentence each, and each answer takes a paragraph. Against my comparison set, a paper
whose defence needs a paragraph loses to a paper whose figure needs none.

**Overclaims.** *"the CVPR 2026 proceedings contain 60+ event papers and none is about event–frame
temporal support or exposure-aware calibration"* — asserted after the search budget was exhausted; per
the brief, treat as provisional and do not put it in a paper. Also *"an order of magnitude above the
sub-ms precision EF-Calib/eKalibr-class methods report"* compares a simulated drift against published
real-rig precision, which is not a like-for-like comparison.

**Hostile experiment.** Death 2's own item (ii): measure the actual joint distribution of `(T, v)` across
all DSEC sequences *before* committing. This is a one-day check and it decides whether the theory is
correct-and-relevant or correct-and-irrelevant. Given that the brief measured daytime exposures as low as
118 µs, the risk of `b < 1 px` is real. Absence is fatal.

**Fixes.** (1) Run the `(T, v)` distribution measurement in week 1. (2) Move the deliverable decisively
out of restoration: the product is a calibration protocol whose output is a pair of measures plus a
per-pixel blind-band mask. (3) See Merge analysis — T1 belongs inside Idea 06.

---

### Idea 07 — *Chronofields* — **BORDERLINE**

**Structural problem:** the team names a falsification criterion it may well fail — if Time Lens →
1000 fps → RVT lands within 15 % of its CTE at equal compute, the accuracy claim is dead — and I cannot
in good conscience advance a ten-week project whose central experiment is a coin flip the authors
themselves priced.

**Summary.** Invert the map. Every perception head is `time → state`; predict `state → time` instead, a
distribution over *when* a queried condition held, with an explicit `∅` atom for "never". Events enter as
exact (uncensored) observations, frames as **interval-censored** ones, in the same likelihood — which is
the cleanest formal statement in the entire round of what a frame actually is. The censoring identification
is genuinely elegant and the survival-analysis loss family is imported correctly.

**Strongest reason to accept.** The C1 anchor: hold out a temporal slice of a *real* event stream and
predict when each pixel next crosses a contrast threshold, supervised by the held-out real events. Real
sensor, microsecond ground truth, no simulator, no annotator, no gated dataset. Every other team in this
round is negotiating for ground truth; this team found some lying on the floor.

**Strongest reason to reject.** The team's own reviewer-proof-ness self-score of 5/10 is the honest one,
and for the right reason: "the metric story reads from a distance exactly like inventing a metric you win
on." Four invented metrics (CTE, SFR, TCE, CMR) against one reported-to-be-flat borrowed one.

**Overclaim.** *"mAP is invariant to a group of temporal shifts"* — the proposition as stated requires
`δ·v_max < ε`, i.e. it holds for shifts *smaller than the matching tolerance*. The interesting regime
(large shifts) is not covered, and the sentence as written claims more than the proof.

**Hostile experiment.** Reconstruct-then-detect at matched and unmatched compute. Absence is fatal, and
the team says so.

**Fixes.** (1) Run C1 and the Time Lens → RVT head-to-head before writing a line. (2) Cut the dataset
list from six to two; the plan as written is not executable in ten weeks. (3) Drop SFR or CMR — four
invented metrics is one more than the traffic will bear.

---

### Idea 09 — *Change-Time* — **BORDERLINE**

**Structural problem:** pillar 1's make-or-break prediction (P3, the elbow at `ρ ≈ 25`) is derived
entirely from the published hyperparameter table of ASTW (CVPR 2026), a paper nobody in this round could
verify, on a search budget that was exhausted.

**Summary.** Stop partitioning. Index each pixel by its own accumulated change `τ(x,t) = C·N(x,t)` — the
total variation of the quantised log-intensity path, with zero free parameters — in which the event stream
is a *complete* observation up to one unknown scalar per pixel and a uniform `O(C)` bound independent of
speed. The representation is exactly invariant to any monotone reparameterisation of time, and the RGB
frame's temporal support becomes a measured per-pixel width `W(x) = C·N_exp(x)`, exactly zero on static
pixels.

**Strongest reason to accept.** Two things. First, the argument that the *recorded* timestamp is already
corrupted — AER bus saturation perturbs event send times, rate-dependently, worst under fast motion, per
the field's own reference survey — converts the idea's weakest point ("sensor time is a real measurement,
not a gauge") into its motivation. That is a genuinely good save. Second, the `β`-is-the-window identity,
demonstrated from released code (DAGr's `time_window = 1e6` µs ⇒ `β = 10⁻⁶`; AEGNN's `beta=0.5e-5` with
`torch.min(ts)` as a window origin), converts "graph methods are grid-free but not timeline-free" from
assertion into citation. Code-level evidence beats rhetoric.

**Strongest reason to reject.** Two novelty pillars are both **negative search results** — `"temporal
support"` + `"event camera"` = 0 abstracts; reparameterisation invariance for events = 0 across ten
probes — declared on an exhausted budget with CVF and Semantic Scholar rate-limited. Per the brief: if an
idea's novelty is its only real asset, that is a reason to rank it lower. And the team itself names two
unclaimed near-misses (SITS reaches monotone invariance by accident via ranks; Spiking Patches builds an
unnamed product order) plus an active scoop threat three months old from the DAGr lab. "SITS with a
theorem" is a review someone will write.

**Overclaim.** *"RIG for our invariant branch: exactly 0, to float precision."* True, and the team
correctly calls it "a unit test, not a result" — but the self-score then counts it as a headline metric.
Pick one.

**Hostile experiment.** P3 with ASTW's clamp swept. If *any* clamp setting flattens the `ρ` curve, the
hyperparameter objection stands and pillar 1 is gone. Absence is fatal.

**Fixes.** (1) Verify ASTW at source before building anything. (2) Run Stage 0 and 0b — one day each, no
downloads — before another word. (3) If P3 falls, the honest retreat is pillar 2 alone, and the team
should decide now whether that is a paper worth ten weeks.

---

### Idea 10 — *Fusion Is Ill-Typed* — **BORDERLINE**

**Structural problem:** the headline diagnostic does not measure what the paper needs it to measure.

**Summary.** A frame is a mass-one probability measure applied in the linear domain; an event bin is a
mass-zero signed measure supported on two instants, applied in the log domain. These sets are disjoint, so
no shift, scale or warp maps one to the other — registration is orthogonal to the defect. The paper types
every tensor with its support and gives legality rules for mixing, comparison, `lift` and `render`, plus a
support-blind pair construction (a bar going right-then-left vs left-then-right within one bin) on which
every published model is provably guessing and confidently wrong.

**Strongest reason to accept.** The support-blind pair cannot fail. It is a construction plus a theorem,
renderable procedurally in an afternoon, and it only requires published models to be deterministic and
confident, which they are by definition. That is a guaranteed result, and the fallback paper — "event–RGB
fusion is provably non-identifiable on a constructible family, and every published model answers it
confidently" — is a real field-level statement.

**Strongest reason to reject.** Event Utility is defined by **modality dropout**: zero the event branch at
inference and measure the metric drop. That measures how brittle a network is to an out-of-distribution
input, not how much information it extracted from events. A network that has learned a strong event prior
will degrade badly on an all-zeros tensor for reasons that have nothing to do with support. The headline
claim — "event utility inverts with speed" — cannot be established this way. The correct instrument is a
matched-capacity frame-only model trained from scratch, which is expensive, or a well-constructed
counterfactual event input, which is subtle. Panel A is the paper, and Panel A's instrument is wrong.

**Overclaim.** *"existing fusion models extract less from events as scene speed increases, i.e. event
utility inverts exactly in the regime events exist for"* — the strongest sentence in the round, resting on
the weakest instrument in the round.

**Hostile experiment.** The fine-tuning control the team already designed: fine-tune on high-`s`, show the
task metric improves 2–4 points while OSAM falls by < 0.08. That is what separates "the formulation is
broken" from "the weights were undertrained." Absence is fatal.

**Fixes.** (1) Replace or supplement modality dropout with a matched-capacity frame-only baseline. (2) Cut
the operator to ≤ 1.5 pages as planned and mean it. (3) Six repos and six Dockerfiles in ten weeks on a
shared box is optimistic; pick four and say which.

---

## Figure 1 test

The single fact that decides more CVPR outcomes than any other: does a reviewer believe the first figure
before reading the caption? I describe the Figure 1 each idea would actually produce, and mark it.

**01 — A Frame Is Not a Timestamp.** Two stacked panels. Top: per-sequence distributions of DSEC exposure
width, day versus night, spanning two orders of magnitude, with the constant 50 ms frame period drawn as
a single vertical line for reference. Bottom: signed along-motion error `e_∥` versus intra-exposure
displacement `d`, one straight line per released tracker, each with a different nonzero slope, and beside
it the same runs' conventional success-AUC curves looking like ordinary smooth degradation.
→ **BELIEVABLE ON SIGHT (top panel).** The top panel is a histogram of numbers that are already in a public
text file; the brief has independently confirmed the 127× spread. Nobody argues with a histogram of
published metadata. The bottom panel is the paper, and it is **NEEDS THE CAPTION** — the reader must accept
`d` and the sign convention first — and it is contingent on a dataset that may not be reachable.

**02 — Exposure-Occupancy Measures.** Two curves of `D` (one minus the minimum IoU over annotation
conventions) against `β` (blur magnitude), stratified into a low-`ν` and a high-`ν` stratum. The low-`ν`
curve is flat near zero across the whole blur range; the high-`ν` curve climbs steeply. The separation is
the plot.
→ **NEEDS THE CAPTION.** The message — "severe blur with zero acceleration produces a perfectly well-posed
label" — is excellent, but the reader must first accept two invented quantities on two axes before the
separation means anything. Two unfamiliar axes is one too many for a Figure 1.

**03 — Temporal Support Fields.** Task error against ground-truth support overlap `O*` in ten bins, one
curve per baseline, each point coloured by blur extent. The intended visual claim is that the colours are
shuffled while the curve falls off a cliff.
→ **NEEDS THE CAPTION.** The shuffled-colour device is genuinely good and would be instantly readable *if
the x-axis were a quantity the reader already believed in.* It is not: `O*` is computed by the authors'
simulator and is defined nowhere else in the literature. The reviewer's first question is about the axis,
not the curve, and that is a losing position.

**04 — When Is Your Prediction?** A spatial heat map of the effective timestamp `τ̂` over a single frame
containing objects at different speeds, showing patches of the image living at times milliseconds apart,
with a violin plot of `τ̂ − t_q` per speed group beside it — multi-modal, modes separated by ≥ 2 ms.
→ **NEEDS THE CAPTION**, but it is the *best* needs-the-caption figure in the round, and with the right
caption it is the most memorable image anyone proposed. "This is one prediction. These are its
timestamps." The problem is that `τ̂` is defined by an argmin the reader has not seen, and the map is
rendered from simulation. Team 4's alternative Figure 1 — the V-curves with vertices off zero, fanning
with speed — is weaker as an image but stronger as evidence; the collapse plot (all ~2000 condition cells
on one line of slope 1, R² > 0.9) is the one a physicist believes on sight and a CVPR reviewer skims.

**05 — No Offset Can Fix a Width.** Three panels: the oracle-estimated offset drifting with blur extent on
a rig whose true offset is exactly zero; the residual at the argmin rising and tracking a theoretical
floor instead of returning to noise; and a residual power spectrum with a comb of notches migrating
leftward as `1/b`.
→ **NEEDS THE CAPTION.** Panel C is the strongest scientific content in this section — notches at predicted
positions with no free parameters is how physics figures work — and it is the panel a CVPR audience is
least equipped to read at a glance. Panel A is the one to lead with: "the calibrated offset of a
perfectly synchronised rig drifts by 3 ms depending on how fast you moved" is a sentence that lands.
Reorder.

**06 — Frames Are Not Samples.** A scatter of the measured residual `R` against the parameter-free,
events-only predictor `P`, hugging the unit-slope line, with a second cloud overlaid flat at zero (the
noise null). Inset: recovered slope and R² against blur length. Beside it, the six-column calibration
table: `ĉ` = 0.189, 0.162, 0.130, 0.049, 0.018, **−0.004**.
→ **BELIEVABLE ON SIGHT.** This is the only Figure 1 in the round that requires the reader to accept
nothing. It is a scatter about `y = x` with a null. Both axes are in log-intensity units the field already
uses. The predictor has zero fitted parameters, which the reader can verify from the equation. And the
sensor is *ideal* — every mundane explanation is switched off by construction, which the figure states in
its own panel titles rather than in a caption. The calibration table is the memorable half: a published
recipe returning a negative contrast threshold on a perfect sensor is an image people repeat at coffee.

**07 — Chronofields.** A dual-axis plot: mAP@0.5 flat across the sweep on the left axis, P95 crossing-time
error rising an order of magnitude on the right axis, log scale, against `a·Δt_f²`.
→ **BELIEVABLE ON SIGHT.** Two curves diverging, one flat and one climbing, is the single most legible
figure form in the discipline, and the message is instant: the benchmark says nothing is wrong while the
answer degrades tenfold. It has one weakness — dual axes with different units invite the "you invented the
right-hand axis" reflex — but the left-hand axis is mAP, which nobody disputes, and that carries it.

**08 — Right Place, Wrong Time.** Panel A: signed along-motion error against ground-truth image speed, one
straight line per method, each passing through the origin, each slope annotated in milliseconds. Panel B:
the same x-axis, perpendicular error, roughly flat. Panel C: the distribution of the support-mismatch
number over each test set.
→ **BELIEVABLE ON SIGHT.** This is the strongest Figure 1 in the round and it is not close. Every element
does work: (i) it is computed from **released checkpoints on public benchmarks**, no training, no
simulator, no gated data — the reviewer knows the authors did not manufacture the inputs; (ii) a line
through the origin whose slope has units of *milliseconds* is a physical measurement, not a score; (iii)
Panel B is the control, in the same figure, so the "that's just error growing with speed" objection is
answered before it is raised; (iv) the slopes can be compared against each method's *declared* aggregation
window, so the figure carries its own sanity check. A reviewer who looks at nothing else understands the
paper and believes it.

**09 — Change-Time.** Slow-object error against `log₂` speed ratio at fixed global event rate, nine
partitioning baselines plus the proposed method. ASTW tracks the proposal to `ρ ≈ 25` then turns upward;
the proposal stays flat.
→ **NEEDS THE CAPTION.** The rhetorical move is excellent — predicting a competitor's elbow from their own
published hyperparameter table, in advance — but the figure is nine curves on a synthetic axis
(speed ratio at fixed event rate) that exists in no dataset, and its meaning depends on the reader
accepting a hyperparameter claim about a paper they have not read. Nine curves is also two too many;
plot three (fixed-time, ASTW, ours) and put the rest in the supplement.

**10 — Fusion Is Ill-Typed.** Event utility (mAP points gained by supplying events) against displacement
during the exposure, log x-axis, one hump per published model, each rising and then falling toward zero.
→ **NOT A FIGURE.** Not because it would be ugly — a set of humps is legible — but because the y-axis is
produced by zeroing an input branch, and the first reviewer who notices will say so, correctly, and the
figure stops meaning anything. A Figure 1 whose axis definition is the paper's weakest point is worse than
no Figure 1. Team 10's *actual* Figure 1 is elsewhere in their own document and they have not recognised
it: two rendered scenes producing bit-identical frames and bit-identical voxel grids with different
correct answers, side by side, with each published model's confident and identical output printed
underneath. That is a construction, not a measurement, it cannot fail, and it is believable on sight.

**Scoreboard.** Believable on sight: **08**, **06**, **07**, and Team 1's top panel. Everything else needs
the reader to accept an invented axis first. That distribution is, by itself, most of my decision.

---

## The convergence question

Teams 1, 4 and 7 converged explicitly on "a frame has no timestamp, only an exposure interval." Teams 2,
5, 9 and 10 converged on it implicitly (an unstated annotation functional over a window; a kernel with a
width rather than a location; a per-pixel measured support width; a mass-one measure over an interval).
Seven of ten, given seven different assumptions to attack.

**My ruling: the convergence is evidence that the observation is obvious once you look, and therefore it
is a premise, not a contribution. Any team that leads with it will be scooped or dismissed. It is worth
one sentence in an introduction and zero pages of contribution.**

The reasoning, in three parts.

**First, it is already in print, repeatedly, as an aside.** Not one of these teams found it; they found
the places where other people already wrote it down and moved on. Sayed & Brostow (CVPR 2021) named
exposure-time label ambiguity — start, midpoint, end, or union — and resolved it by legislating a
convention. REFID (CVPR 2023) states outright that "because of the finite exposure times of the two
frames, the timestamps `t₀` and `t₁` should be replaced by time ranges", and then attributes the residual
to sensor noise. MTevent (CVPR-W 2025) observes that a 25 ms RGB exposure yields faulty annotations under
fast motion, and discards the observation in the next sentence. Scheerlinck, Barnes & Mahony (ACCV 2018)
saw the log/average mismatch, wrote "we believe the difference will be insignificant", and did not return.
DSEC ships the exposure file and documents the midpoint-averaging convention in its own paper. An
observation that five published groups have already made in passing is not a finding. It is common
knowledge that nobody has bothered to price.

**Second, convergence under a shared seed measures the seed, not the world.** All ten teams were handed
one sentence: frame and event observations do not share the same temporal support under fast motion.
"A frame is an interval, not an instant" is *one* inferential step from that sentence. Seven teams taking
the same single step is a measurement of the seed's diameter, not independent replication. Independent
replication would look like seven teams arriving here from seven unrelated starting points. They did not.

**Third — and this is the part that decides the round — the scoop risk is not uniform, and the teams have
it backwards.** The *observation* carries low scoop risk precisely because it is already half-published;
nobody will write a CVPR paper whose contribution is a restatement of REFID's parenthetical. The high
scoop risk is on the two moves the teams think are safe:

- **"Estimate the latent exposure from events."** This is occupied territory and the teams' own related-
  work tables prove it: EBFI-BE (CVPR 2023) estimates the lost exposure prior under blind exposure; ETES /
  REFID (ECCV 2022) handle unknown exposure time; exposure-agnostic VFI (BMVC 2025) handles unknown and
  *dynamic* exposure. Any paper whose method is "make `T` a latent" is one search away from a compression
  into "they applied EBFI-BE to detection." Team 1 names this as its Risk 2 and is right to.
- **"Predict a measure instead of a point."** Three of these ten teams proposed it independently in the
  same week on the same seed. If three teams in one room converge on it, three labs elsewhere will too.

What has **low** scoop risk is what nobody else is positioned to do cheaply: **measuring, in physical
units, on other people's released checkpoints and other people's published benchmarks, what the
convention costs.** That measurement requires no new dataset, no gated access, and no simulator — and,
critically, it requires *wanting to indict the field rather than beat it*, which most groups do not.
Team 8 is the only idea in this round whose contribution is entirely in that territory. Team 6 is the only
other one that has actually produced such a number.

**Commitment.** I rule the shared observation a premise. I will not advance any idea whose contribution
is the observation, or the observation plus a head. I advance the idea whose contribution is the *price*.

---

## Merge analysis

### Merge A — Ideas 01 + 04. **One paper. Merge, and it strengthens.**

These are the same paper and I will not fund both. `α_model` and `τ̂` are the same quantity; both
reformulate to a trajectory head in which `K = 0` recovers the current model exactly; both use the frame's
integral as a loss; both name FAOD's Time Shift as the antagonist with the same argument.

Team 4 supplies what Team 1 lacks: `σ_τ`, the within-frame dispersion, and the frame-only/event-only
control that makes it mean something. Team 1 supplies what Team 4 lacks: the exact non-identifiability
proposition (the `u`-substitution removing `t₀` and `T` from the image formation equation, and the
`u → 1−u` reversal ambiguity), which is a half-page proof that gives the diagnosis a spine, and the free
DSEC exposure-statistics panel.

**What gets cut in the merge, and it must be cut, not merged:** Team 1's Bézier support-field machinery
(the `S(y) = [t̂₀ + ρ̂y, …]` rolling-shutter field is sim-only by their own admission, on global-shutter
data); Team 1's SupportBench as a *primary* vehicle (demote to a controlled instrument); two of Team 1's
four invented metrics; three of Team 4's four simulator figures (keep the collapse plot and the dispersion
map). The merged paper is a diagnosis with a 1.5-page method, not a method with a motivating diagnosis.

### Merge B — Idea 08 + the merged 01/04. **Merge, and it is the paper I would build.** See My decision.

### Merge C — Ideas 05 + 06. **Partial merge only. Full merge produces two products and no paper.**

These are closer than either admits. Team 5's own log-linearisation writes
`log F ≈ (w_F * ℓ) + ½Var_{w_F}[ℓ]` — that second term **is** Team 6's exposure gap `J = ½Var_W(L)`.
They have derived the same object in two bases: Team 5 in Fourier (a box's sinc nulls; a shift cannot
change a modulus), Team 6 in Jensen (log of a mean is not the mean of a log). The physical content
overlaps substantially and neither related-work table notices.

But their *deliverables* do not merge. Team 5 ships a calibration protocol whose output is a pair of
measures and a per-pixel blind-band mask. Team 6 ships a one-line correction to a consistency loss and an
identifiability result for the per-pixel contrast threshold. A paper with both has two products and no
thesis. **Correct merge: import Team 5's T1 (no shift can fix a width) into Idea 06 as a half-page
proposition, cite Raskar for the spectral fact, and drop Team 5's calibration framing entirely.** Team 6
gains an impossibility bound where it currently has only a measurement; Team 5's independent contribution
survives as one proposition inside a paper that has data.

### Non-merges — these produce mush

- **02 + 03 + 10** ("predict a measure/set instead of a point"). Three measure-valued proposals, three
  different theories of *what the measure is of* — occupancy of the scene state (02), validity of the
  observation (03), the photometric latent with a null space (10) — and three incompatible evaluation
  stories (conformal coverage / support-overlap accuracy / certified ambiguity intervals). A merged paper
  carries four propositions, three invented metric families and no Figure 1. **Do not merge.** If any of
  these is built, build exactly one.
- **07 + anything.** Chronofields inverts the map. Nothing else in the set does, and bolting a
  `state → time` head onto a `time → state` diagnosis produces a paper with two output types. Its
  censored-likelihood identification (event = exact, frame = interval-censored, non-crossing = right-
  censored) is a genuinely nice formal statement and it should be **cited by whoever wins**, in one
  sentence, as the correct way to write down what a frame is. That is the right size for it in this round.
- **09 + anything.** Change-time replaces the coordinate. Everything else keeps seconds and argues about
  what happens on them. There is no partial adoption: you either have a global timeline or you do not.
- **10's type system + 08's metric.** Superficially attractive — one says which operations are legal, the
  other measures the cost — but 10's types are a compile-time discipline over network internals and 08's
  measurement is a post-hoc re-scoring of dumped prediction files. They share a motivation and no
  machinery. The merge would be an introduction, not a paper.

---

## Ranking

1. **08 — Right Place, Wrong Time.** The only idea whose Figure 1 is computed from other people's
   checkpoints, whose first experiment needs a 4.7 MB file and no GPU, and whose output is a number in
   milliseconds that every future event benchmark would have to report.
2. **06 — Frames Are Not Samples.** The only team with results in hand, verified infrastructure, and a
   scatter plot about `y = x` that requires the reader to accept nothing; docked one place because the
   fix is one line and the blast radius is the sensor community, not the field.
3. **04 — When Is Your Prediction?** `σ_τ > 0` is the sharpest claim anyone made and the frame-only
   control is the sharpest test anyone designed; docked for a real-data plan that depends on a dataset one
   team reports as dead.
4. **01 — A Frame Is Not a Timestamp.** The best-written framing in the round and a free opening panel,
   but it is Idea 4 without the kill shot, and it contains a prediction the brief has already falsified.
5. **05 — No Offset Can Fix a Width.** A phenomenon guaranteed by the Fourier transform of a box,
   settleable in four days on CPU, with an ablation that kills every mundane explanation in one table row;
   docked because it will be read as deblurring and because DSEC daytime may sit below its onset.
6. **02 — Exposure-Occupancy Measures.** The best single sentence in the round ("the convention moves the
   score more than the method does") attached to a paper that is entirely conditional on a dataset that
   may not exist and a theory a reviewer must read before the figure means anything.
7. **07 — Chronofields.** The most elegant formalisation of what a frame is, and the most honest risk
   assessment; it is a bet on one head-to-head the authors priced as a coin flip.
8. **10 — Fusion Is Ill-Typed.** A guaranteed result (support-blind pairs) buried under a headline
   instrument that measures the wrong thing; promote the construction, demote the curve, and it moves up
   three places.
9. **09 — Change-Time.** The most conceptually ambitious idea here and the one most exposed to the round's
   process defect: two novelty pillars that are negative search results, a decisive experiment defined
   against an unverified competitor, and an active scoop threat from the lab that owns the datasets.
10. **03 — Temporal Support Fields.** A good operator (overlap-gated attention, sub-probability mass for
    abstention) resting on a matched-pair construction that does not match under any real sensor, with an
    x-axis that exists only in the authors' simulator.

---

## My decision

**I advance Idea 08, *Right Place, Wrong Time*, absorbing Idea 04's within-frame dispersion and Idea 01's
DSEC exposure panel.**

### Why this one

It is the only idea in the round that is a contribution to the field rather than to a leaderboard *and*
can be carried by the team that proposed it. Those two conditions rarely coincide, and the AC prompt is
right that the field-level form is simultaneously the highest-leverage and the most dangerous. What
convinces me that Team 8 can carry it is not the argument — several teams argued well — but the evidence
that they opened the repositories. They found that `ssms_event_cameras` consumes the *identical*
preprocessed tarballs as RVT, which removes the single degree of freedom a hostile reviewer would attack
in a cross-method comparison. They found that DAGr already ships `run_test_interframe.py`, which writes
exactly the artifact their re-scorer eats. They found that BFlow releases event-only and event+image
checkpoints of one architecture under one training recipe — a single-variable manipulation of temporal
support width, released by someone else, for free. And they sized every download by HTTP HEAD on the day
they wrote. Against the operational reality in the brief — 9 GB shared, ten weeks, nothing on disk — that
is the difference between a plan and a wish.

It also has, by a wide margin, the best risk profile. Total ≈ 35 GPU-hours, no training, nothing over
9 GB. The critical path is bandwidth, not compute, which is the one resource this project actually has.
And the first experiment (E0) needs no GPU and no event data at all.

### The shape of the paper I would want built

**Title claim:** the unit of error in event vision should be an ordered pair — pixels perpendicular to
motion, milliseconds parallel to it — and when you measure the second component on released checkpoints,
it is large, systematic, predictable from each method's declared aggregation window, and invisible to
every metric in use.

**Figure 1:** Team 8's Panel A and B, unchanged. Signed along-motion error against ground-truth speed,
one line through the origin per method, slopes annotated in milliseconds; perpendicular error flat beside
it. Released checkpoints, public benchmarks, no simulator.

**Figure 2:** Team 4's contribution, and this is why the merge matters. The within-frame dispersion
`σ_τ` — a spatial map showing that one prediction tensor carries several timestamps, with the frame-only
and event-only controls beside it. Panel A alone invites "subtract the constant and go home." Figure 2 is
what makes that exit unavailable, and Team 8 does not currently have it.

**Figure 3:** E0's label forensics. How much of DSEC-Det's and DSEC-3DOD's advertised high-rate ground
truth is recoverable from its own linear-interpolation prior, and how far a *causal* constant-velocity
extrapolator with no sensor data at all gets under each benchmark's own published protocol. This is the
most damaging experiment in the round and the cheapest.

**Section 2 opener:** Team 1's DSEC exposure histogram. Exposure width spanning 118 µs to 14 996 µs, a
factor of 127, varying 337 → 4207 µs within a single sequence, against a frame period of 50 ms that every
downstream method treats as the whole story. One panel, already verified, establishes that the premise is
real without spending a page arguing it.

**The deliverable that outlives the paper** — and this is the part that decides whether anyone remembers
it — is the reporting contract: a submission declares `(c_P, w_P)`, the centroid and width of its temporal
support, the way it currently declares FLOPs and latency. Plus the three-GT release (`GT_inst`, `GT_exp`,
`GT_lin`) so any future author can measure how much of their score is agreement with an annotation prior.
A paper that adds a column to everyone else's tables outlives a paper that adds two points to one.

**What must not be in it.** No method. Team 8's instinct to propose only a five-line training-free
re-anchoring *as a falsification test of its own metric* is exactly right and must survive contact with
the temptation to win something. The moment this paper proposes an architecture, it becomes an
architecture paper with an unusual motivation section, and it dies as one.

### The one thing most likely to kill it

**The anisotropy control comes back at `R ≈ 0.5`.**

If relaxing predictions along the motion tangent recovers no more than an equal-budget relaxation in a
free direction, then `AP^⟂` is loosened IoU with a story attached, the decomposition measures nothing
physical, and the paper has no content. Everything — the ranking flips, the milliseconds, the reporting
contract — hangs off that one number, and no amount of writing rescues it.

It is also, fortunately, a number that can be had in week 1 on Gen1 alone, from one inference pass over a
98.6 GB tarball, before the 190 GB gen4 download starts and before anyone writes an introduction.

**My instruction to the team:** run E0 and the anisotropy control in the first ten days, in parallel, and
nothing else. If `R ≥ 0.75` on any dataset, build the paper above. If `R ≈ 0.5`, stop, publish E0's label
forensics as the standalone benchmark-integrity result it already is, and hand the remaining eight weeks
to **Idea 06**, which is my runner-up, which already has its numbers, and which is the only other idea
here that can put a believable figure on page one.
