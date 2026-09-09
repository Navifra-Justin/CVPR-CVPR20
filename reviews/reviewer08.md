# Reviewer 08 — claim calibration and narrative architecture

Specialism: the strength of a sentence against the strength of the evidence that will exist when the
paper is written; and whether the paper has a spine or is an assembly of good parts.

Round: CVPR20 idea selection, ten ideas, domain Temporal-Support-Aligned Event–RGB Perception.

---

## Comparison set

Six papers, all confirmed accepted, fetched directly (arXiv API, `comment` field carries the venue).
For each I quote the abstract's central claim sentence verbatim and characterise its calibration.
This is the evidence for what the venue actually rewards, and it is the yardstick used in the
overclaim audit below.

**1. State Space Models for Event Cameras** — Zubić, Gehrig, Scaramuzza. CVPR 2024
(arXiv 2402.15584v3, comment: "18 pages, 5 figures, 6 tables, CVPR 2024 Camera Ready paper").

> "Our results demonstrate that SSM-based models train 33% faster and also exhibit minimal
> performance degradation when tested at higher frequencies than the training input."

Calibration: the verb is "demonstrate", and every strength word in the sentence is bolted to a number
produced in the same sentence ("33% faster", "minimal degradation" followed one sentence later by
"3.76 mAP" against ">20 mAP"). The failure of prior work is stated as a measured property — "they
exhibit poor generalizability when deployed at higher inference frequencies" — not as an
impossibility. Note what is absent: no "cannot", no "provably", no "the field has been optimizing the
wrong quantity". This is the closest published analogue to what several of these ten ideas want to
say, and it says it in the indicative measured mood.

**2. Ev-3DOD: Pushing the Temporal Boundaries of 3D Object Detection with Event Cameras** — Cho et al.
CVPR 2025 (arXiv 2502.19630v1, comment: "Accepted by CVPR2025").

> "To address this limitation, we introduce asynchronous event cameras into 3D object detection for
> the first time." … "Furthermore, we introduce the first event-based 3D object detection dataset,
> DSEC-3DOD, which includes ground-truth 3D bounding boxes at 100 FPS, establishing the first
> benchmark for event-based 3D detectors."

Calibration: three "first" claims — and all three are **artifact-firsts** (first to apply sensor X to
task Y; first dataset; first benchmark). An artifact-first is settled by a reviewer in fifteen
minutes and is either true or false. None of them is a *phenomenon-first* ("no one has noticed
that…"), which is the unfalsifiable kind that several of these ten ideas reach for. The mechanism
sentence is separately hedged: "Our method **enables** detection even during inter-frame intervals" —
enables, not solves.

**3. Unleashing the Temporal Potential of Stereo Event Cameras for Continuous-Time 3D Object
Detection** — ICCV 2025 (arXiv 2508.02288v1, comment: "Accepted to ICCV 2025").

> "Experiments show that our method outperforms prior approaches in dynamic environments,
> demonstrating the potential of event cameras for robust, continuous-time 3D perception."

Calibration: the strongest word in the paper's closing claim is "potential". The criticism of the
nearest competitor is scoped to a named mechanism — "struggles in fast-motion scenarios **due to its
dependency on synchronized sensors**" — rather than to an expressive incapacity. This is exactly the
"condition → mechanism → observation" register that checklist item 196 asks for, executed by an
accepted ICCV paper on this precise topic.

**4. BeNeRF: Neural Radiance Fields from a Single Blurry Image and Event Stream** — ECCV 2024
(arXiv 2407.02174v3, comment: "Accepted to ECCV 2024").

> "In this work, we demonstrate the possibility to recover the neural radiance fields (NeRF) from a
> single blurry image and its corresponding event stream."

Calibration: "demonstrate the possibility" is the weakest available existence claim, attached to a
genuinely strong existence result. This is the single most instructive sentence in the comparison
set for the present round: a blur-plus-events paper that recovers an intra-exposure camera trajectory
with a cubic B-spline — i.e. mechanically almost identical to what Teams 01, 02 and 04 propose —
publishes it at ECCV with the verb "demonstrate the possibility". Team 01's corresponding sentence is
"we prove this non-identifiability". The venue does not require the stronger verb, and the stronger
verb is what a hostile reviewer attacks first.

**5. Adaptive Bounding Box Uncertainties via Two-Step Conformal Prediction** — Timans et al. ECCV 2024
(arXiv 2403.07263v2, comment: "European Conference on Computer Vision (ECCV) 2024").

> "Validating our two-step approach on real-world datasets for 2D bounding box localization, we find
> that desired coverage levels are satisfied with practically tight predictive uncertainty intervals."

Calibration: this paper has an actual mathematical guarantee — split-conformal coverage — and it
still reports its empirical outcome with "we find that" and "practically tight". It does not say
"we prove tight intervals". Directly relevant to Team 02, which imports this exact machinery and then
writes "This is an un-arguable experiment: it is a proof, not a benchmark delta."

**6. Seeing Motion at Nighttime with an Event Camera (NER-Net)** — CVPR 2024 (arXiv 2404.11884v1,
comment: "Accepted by CVPR 2024").

> "Specifically, we discover that the event at nighttime exhibits temporal trailing characteristics
> and spatial non-stationary distribution." … "Extensive experiments demonstrate that the proposed
> method outperforms state-of-the-art methods in terms of visual quality and generalization ability
> on real-world nighttime datasets."

Calibration: a phenomenon paper. Its phenomenon sentence is "we discover that X **exhibits** Y" — an
observed property of the data. It does not say "no existing representation can express nighttime
trailing", although it easily could have. Eight of the ten ideas here would have written the stronger
sentence.

**What the comparison set establishes.** Across six accepted CVPR/ICCV/ECCV 2024–2025 papers in and
adjacent to this exact topic, the main-claim verbs are: *demonstrate, show, find, discover,
outperform, enable*. The count of "prove", "provably", "cannot", "no work", "carries no information
whatsoever", "the field has been optimizing the wrong quantity" in the six central claim sentences
is **zero**. The only categorical claims present are artifact-firsts. That is the register these ten
ideas must be written in, and it is not a style preference: it is what survives rebuttal.

---

## Per-idea verdicts

| # | Idea | Verdict | One-sentence reason |
|---|---|---|---|
| 08 | Right Place, Wrong Time (evaluation decomposition) | **STRONG ACCEPT** | The only idea whose deliverable is inference-only on verified checkpoints, that proposes no method (structurally killing "you invented a metric you win on"), and that concedes its own borrowed algebra before a reviewer can. |
| 04 | When Is Your Prediction? (effective timestamp) | **ACCEPT** | Best-designed measurement in the set — a 3-day, zero-download pilot, a pre-registered null result, and the one decisive control (frame-only `σ_τ`) that can falsify its own framing. |
| 05 | No Offset Can Fix a Width (support kernels) | **ACCEPT** | The failure phenomenon is a consequence of the Fourier transform of a box rather than an empirical hope, the killing ablation runs first, and 96 GPU-h is the cheapest credible plan here. |
| 01 | A Frame Is Not a Timestamp (latent exposure support) | **BORDERLINE** | Best formulation and the cleanest `K=0`-is-the-baseline design, but the thesis sentence is false as written ("no information whatsoever" plus "we prove") and the real-data figure hangs on FE240hz, which Team 09 reports is dead. |
| 06 | Frames Are Not Samples (the exposure gap) | **ACCEPT** | The most honestly calibrated document in the round, with its headline numbers already measured — accepted despite a narrow delta over EVDI/mEDI, which it declares itself. |
| 02 | No State at t (occupancy measures) | **BORDERLINE** | Its headline prediction ("severe blur with zero acceleration produces a perfectly well-posed label") is contradicted by its own convention table two pages earlier, and the conformal half is a second paper. |
| 10 | Fusion Is Ill-Typed (support types) | **BORDERLINE** | The `EU(s)` inversion is the best falsifiable field-level claim in the round, but Proposition 1 is close to a tautology and is asked to carry the entire indictment. |
| 03 | Temporal Support Fields (predicted support measures) | **BORDERLINE** | Uses "provably" for a measured 3% relative difference, and the load-bearing frame-branch ground truth exists only where the authors generated it. |
| 07 | Chronofields (invert the query) | **REJECT** (fatal to this execution, not to the idea) | The formulation change does not follow from the diagnosed failure — it is one of several available fixes — and the baseline the team itself names as lethal is likely to tie. |
| 09 | Change-Time (per-pixel clocks) | **REJECT** (fatal to the idea as stated) | The invariance claim is destroyed by the very sensor mechanism the document uses to motivate it, and the novelty rests on zero-hit keyword conjunctions plus a fabricated "<5%" residual-risk figure. |

---

## Detailed review

Eight items per the rubric, tight.

### Team 01 — A Frame Is Not a Timestamp

1. **Verdict.** BORDERLINE.
2. **Summary.** The document argues that a blurred frame constrains the intra-exposure path and its
dwell density but not the affine time map `(t0,T)`, so the scalar timestamp every dataloader hands
downstream is a convention rather than a measurement; it predicts a signed, motion-direction-
conditioned localisation bias `E[e_∥|d] = (α_model − α_label)·d` that standard metrics average to
zero, and replaces the point state with a Bézier trajectory on a normalised support plus an estimated
support field `(t̂0, ρ̂, T̂)`. Its cheapest asset is real: DSEC publishes per-frame exposure
start/end, so `|T̂ − T|` can be validated in milliseconds on public data with no training. Its
`K = 0` ablation *is* the current formulation, which is the cleanest ablation-as-SOTA-comparison
design anywhere in this round.
3. **Strongest reason to accept.** Item 5 of the checklist — contribution as problem structure rather
than method trick — is satisfied better here than anywhere else: the free-lunch experiment (one
scalar per dataset, zero learned parameters, applied to *other people's checkpoints*) produces a
result that belongs to the field rather than to the authors' model.
4. **Strongest reason to reject.** The identity of the paper is carried by a sentence that is false
as written, and the document then contradicts it three pages later by adding `L_meta = |T̂ − T_exif|`
and a blur-as-integral constraint — both of which are ways of extracting information about the
exposure that the thesis says does not exist.
5. **Factual errors.** (a) Fig 1a predicts "the left–right exposure-midpoint difference: prediction
≥ 1 ms on a substantial fraction of frames". The brief's verified measurement is median 16–144 µs and
max 380 µs — the prediction is wrong by roughly an order of magnitude, and the brief explicitly says
an argument resting on left/right divergence rests on the smaller effect. Delete this panel.
(b) The dataset table gives FE108/FE240hz "Medium-high" availability risk; Team 09 reports the host
`fe108.dluticcd.com` refused connection outright. If that is right, risk is not medium-high, it is
realised, and Fig 1b has no data source. Verify on day 1, not day 14.
6. **Claims exceeding evidence.** See the overclaim audit — items O1.1 through O1.8. The critical
ones are the thesis sentence and "we prove this non-identifiability" against a proposition the
document itself labels "(informal)" with a "proof sketch".
7. **Experiment a hostile reviewer demands.** Show that deblur-then-detect (EDI, EBFI-BE → detector)
does **not** reduce TSB. The document already plans it. Its absence would be fatal, because without
it the whole paper compresses to "blind exposure estimation exists; you applied it to boxes".
8. **Ranked fixes.** (i) Rewrite the thesis sentence to the identifiability statement that is
actually provable and actually needed (see O1.1). (ii) Resolve FE240hz access in week 1 with a
declared no-go. (iii) Delete the left/right divergence panel. (iv) Reduce four invented metrics to
two (TSB and SIE); TQ-AUC and SCR measure the same thing twice and quadruple the "you invented your
own metric" surface. (v) Move the free-lunch cross-dataset result to Figure 1, since it is the only
result that cannot be produced by an incremental paper.

### Team 02 — No State at t

1. **Verdict.** BORDERLINE.
2. **Summary.** The label attached to a frame is modelled as an unnamed functional `A` of the state's
occupancy measure `μ = y_#Unif(W)`, with six defensible candidate conventions in active use and no
benchmark declaring which it used; the document predicts that label ill-posedness is governed by
intra-exposure *acceleration* rather than blur magnitude, that switching `A_mid → A_mean` moves a
fixed model's RSR by more than the spread between five published trackers, and that Kendall τ over
the FE240hz leaderboard falls below 0.6 in the top acceleration decile. The reformulation predicts
`μ` itself via a support spline plus a dwell density, learns the convention `π` as a latent by EM so
it trains on ordinary point-labelled data, and evaluates by split-conformal convention-marginal
coverage.
3. **Strongest reason to accept.** The `π`-recovery result — reading a benchmark's unwritten
annotation habit off its own labels — is a quotable, checkable, field-level finding that no
uncertainty method has anywhere to put, and it is cheap.
4. **Strongest reason to reject.** Prediction 1 is contradicted by the document's own table. At
constant velocity `A_mid = A_mean = A_mode` holds, but `A_hull` (tightest box containing the streak)
and `A_core` (the sharp part) are listed in the same table and diverge from all three under
arbitrarily severe *uniform* blur. So "severe blur with zero acceleration produces a perfectly
well-posed label" is false against the document's own convention set, and `D = 1 − min_{A,A'} IoU`
computed over that set cannot be `< 0.05` at `β = 3`. Either the convention set or the prediction has
to go, and either choice weakens the headline.
5. **Factual errors.** The internal contradiction above is the substantive one. Also: "*no benchmark
in computer vision states which A it used*" is a universal over a set nobody can enumerate, made by a
team the brief lists as unable to finish its prior-art sweep.
6. **Claims exceeding evidence.** Audit items O2.1–O2.6; the worst is "This is an un-arguable
experiment: it is a proof, not a benchmark delta", applied to a trained model's ~100% accuracy on
time-reversal pairs.
7. **Experiment a hostile reviewer demands.** The KL-Loss / Gaussian aleatoric head at matched
capacity, on the *same* time-reversal pairs. The document plans it. Its absence is fatal: without it
the entire paper reads as aleatoric uncertainty with a spline.
8. **Ranked fixes.** (i) Repair prediction 1 by restricting the convention set to the functionals of
`μ` alone and stating that restriction, or by re-deriving `D` with `A_hull`/`A_core` included and
accepting a smaller effect. (ii) Split the paper: the acceleration-vs-blur measurement plus `π`
recovery is one paper; conformal set prediction is another. (iii) Replace "un-arguable" and "proof"
with the measured accuracy. (iv) Honour the stated day-7 kill criterion literally.

### Team 03 — Temporal Support Fields

1. **Verdict.** BORDERLINE.
2. **Summary.** Every observation is recast as a pairing of the latent log-intensity trajectory with
a non-negative measure on the time axis; the network predicts, per pixel and per branch, a
sub-probability measure (shape plus mass), and cross-modal attention is gated by the *overlap* of the
two branches' supports rather than by feature similarity. The failure phenomenon is a matched-pair
construction — constant-velocity versus dwell-then-dash at identical blur extent, identical event
count, identical mean flow — that varies only the ground-truth support overlap `O*`, predicting a
≥3.5 dB PSNR cliff that no covariate in current use can explain. The sub-probability mass is what
makes abstention ("no valid observation of this pixel at this time") a representable output.
3. **Strongest reason to accept.** The event-branch support has exact ground truth on real data for
free — it is the inter-event interval, present in the raw stream. Half the supervision is real by
construction, which is an unusually strong answer to "you invented your ground truth".
4. **Strongest reason to reject.** The frame-branch support, which is the half that matters for this
round's seed, has no real ground truth anywhere; it is supervised by a simulator or self-supervised
by an EDI rendering loss whose null space the document itself flags as a live risk (Death 3). The
load-bearing quantity is the one with the weakest evidence.
5. **Factual errors.** None found in the physics. Two verification hazards: the two named nearest
competitors (ASTW and RTEA, both "CVPR 2026") could not be checked in this review, and the entire
"why this is not closest work" table rests on them. Team 03 is on the brief's list of teams that
could not finish the prior-art sweep, so "we found no work that predicts a temporal support measure
as its output" is provisional in a way the document does not mark clearly enough.
6. **Claims exceeding evidence.** Audit items O3.1–O3.4; the worst by a distance is "The
representation is *provably* unable to separate two inputs whose correct answers differ", quantified
one clause later as `< 3%` relative difference — which is a measurement, is not zero, and is not a
proof of inability.
7. **Experiment a hostile reviewer demands.** Ablation (viii) — replace the overlap term with a
learned per-pixel scalar modality reliability at matched parameter count. Its absence is fatal;
"isn't this uncertainty-gated fusion" is the first thing every reviewer will write.
8. **Ranked fixes.** (i) Delete "provably" and report the SID number as a measurement. (ii) Promote
the zero-simulator-label ablation (vi) into the main paper, since it is the only defence against the
synthetic-GT charge. (iii) Cut the six invented metrics to three. (iv) Re-verify ASTW and RTEA at
source before any framing sentence depends on them.

### Team 04 — When Is Your Prediction?

1. **Verdict.** ACCEPT.
2. **Summary.** The document introduces one measurement primitive — the effective timestamp
`τ̂ = argmin_t d(ŷ, y*(t))`, the time at which a prediction *would* have been right — and from it
derives a temporal bias `b` and a within-frame temporal dispersion `σ_τ`. It argues that a fused
predictor returns the state at the evidence-weighted time centroid `t̄` rather than at the queried
time, so `τ̂` is a function of exposure, event-window offset and *scene texture*, and varies between
regions of a single output tensor. `σ_τ > 0` is the load-bearing claim, because it is what makes a
scalar clock correction impossible. The pilot is three days, three GPU-hours and zero downloads.
3. **Strongest reason to accept.** Section 4.4 — "What a NULL result looks like (and we will report
it)" — is written before the experiment, names the exact numbers that would falsify each figure,
identifies the confound (blur magnitude correlates with temporal displacement by construction) and
specifies the anti-diagonal control that separates them. This is checklist items 71, 74 and 77
satisfied at idea stage. No other document in this round does it this completely.
4. **Strongest reason to reject.** The effect it needs to resolve on real data is 2–5 ms, and the
best available real ground truth (FE240hz Vicon at 240 Hz) has a 4.17 ms sampling interval. The
document concedes this. If the real-data `σ_τ` is marginal, this becomes a paper about a 2 ms bias
measured in a simulator, and small effects are punished regardless of conceptual weight.
5. **Factual errors.** None found. One scoping error: "no paper measures the effective timestamp of
a fused event–RGB task prediction, none reports that it varies within a frame, and none frames
event–RGB fusion as a change-of-support problem" is stated categorically and only then hedged in the
next sentence ("We found no prior report"). Reverse the order.
6. **Claims exceeding evidence.** Audit O4.1–O4.5. All are framing sentences rather than results,
which is the good case: they are removable without touching the science. But they must be removed
now, because a slogan that survives to the introduction becomes a claim.
7. **Experiment a hostile reviewer demands.** Ablation 8.5(a) — frame-only versus event-only versus
fused. If `σ_τ` is as large for the frame-only model, the phenomenon is not about fusion and the
paper's framing is wrong. The document names this itself as the single most important control. Its
absence is fatal.
8. **Ranked fixes.** (i) Strike the four slogan sentences (O4.1–O4.4) before they reach a draft.
(ii) Run 8.5(a) in the pilot, not after it. (iii) State the FE240hz GT resolution limit (4.17 ms) in
the same paragraph as every real-data `σ_τ` number. (iv) Report the strongest calibration baseline —
per-speed-bucket lookup table — as a main-paper row, not a rebuttal.

### Team 05 — No Offset Can Fix a Width

1. **Verdict.** ACCEPT.
2. **Summary.** Frame and event channels are integrals of one latent log-radiance against two
different measures on the time axis; a temporal shift is a unit-modulus linear-phase multiplier in
Fourier, whereas support mismatch is a modulus mismatch with exact zeros and π phase jumps, so the
shift group cannot contain the operator relating the two channels. Three results follow: an
impossibility floor `SMF`, a proof that the best-fit offset is a spectrum-weighted group delay and
therefore depends on scene and speed rather than on the rig, and a speed-sweep identifiability
theorem recovering the kernel pair from `J ≥ 2` known speeds. The decisive experiment gives the
opposing formulation every advantage — synthetic data where the shift model is exact, an ideal
sensor, an oracle grid search over δ — and shows the residual survives anyway.
3. **Strongest reason to accept.** The failure phenomenon is guaranteed to exist before any
experiment is run, because it is a property of the Fourier transform of a box. Nothing else in this
round has that. And the load-bearing tier is CPU-FFT-bound: the central claim can be produced without
a GPU at all, which is exactly the de-risking the brief asks for.
4. **Strongest reason to reject.** "Isn't this deblurring, and isn't the sinc null from Raskar 2006?"
takes a paragraph to answer rather than a sentence, and a reviewer who reads only the figures sees
blur curves. The document knows this and scores itself 6/10 on reviewer-proofness for it.
5. **Factual errors.** None. The DSEC exposure estimate ("0.1–1 ms" daytime) is consistent with the
brief's verified 118 µs minimum. The document's Death 2 correctly identifies that if daytime `b < 1`
px the theory is "correct and irrelevant", and schedules the `(T, v)` distribution measurement as a
one-day gate before committing. That is the right posture and it matches the brief's measured
14996 µs night ceiling, where the effect should live.
6. **Claims exceeding evidence.** Audit O5.1–O5.4. The pattern here is narrow and fixable: the
theorems are correctly conditioned in their own statements (T3 is explicitly restricted to the
log-linearised model, and the document says so in a parenthetical risk note), but the thesis sentence
and the title drop the conditions.
7. **Experiment a hostile reviewer demands.** Ablation 1 — global shutter, `τ → 0`, noiseless,
`δ* = 0`, ideal thresholding. If SMF and OBD survive with every mundane cause removed by
construction, the "just model latency like Yang et al." objection dies in one table row. The document
schedules it first. Its absence would be fatal.
8. **Ranked fixes.** (i) Carry the linearisation and constant-velocity conditions into the thesis
sentence, not only into the theorem statements. (ii) Move the `(T, v)` distribution measurement to
day 1 as a declared go/no-go. (iii) Drop "Calibrating faster makes your calibration worse" from
anything that becomes prose; report `OBD` in ms/px instead. (iv) Reduce the five invented metrics to
SMF, OBD and NDE.

### Team 06 — Frames Are Not Samples

1. **Verdict.** ACCEPT.
2. **Summary.** The working identity `∫events = Δ log I` is misspecified rather than noisy, because a
frame is a log-mean-exp functional of the intra-exposure log-intensity trajectory; the resulting
exposure gap has the closed form `J = ½·Var_W(L)`, exists for a physically perfect sensor, and is
predicted with **zero fitted parameters** from the event stream alone. The measurements already
exist: slope 0.955 and R² 0.779 with every non-ideality off, against a noise null of R² 0.0015, and
99% of the residual explained on textured content. The sharpest consequence (P7) is that the field's
standard per-pixel contrast-threshold calibration collapses from 0.189 to −0.004 as a function of how
fast the calibration sequence moved, with no sensor non-ideality present at all.
3. **Strongest reason to accept.** This is the best-calibrated document in the round and it is not
close. It refuses a universal claim in writing — "So 'every method assumes (E2)' would be false, and
we do not write it" — names the one method in the lineage that gets the operator right (EVDI) and
promotes it to *positive control*, distinguishes its own Jensen term from AKF's on an orthogonal
axis so a reader cannot conflate them, and states P7's scope precisely: "We do not claim that *all*
the reported speed-dependence of the contrast threshold is this artefact… We claim that a component
of it is a measurement artefact, that the component is large, and that it is removable in closed
form." That is checklist item 23 executed at idea stage.
4. **Strongest reason to reject.** The headline fix is one line of code and its operator is already
in print (mEDI Eq. 5, EVDI Eq. 19–20). The delta is measurement plus re-attribution plus an
identifiability argument — real, but narrow, and the document's own novelty score of 6.5 is the
lowest self-assessment in the round.
5. **Factual errors.** None found; this file is the most carefully sourced. Two open verification
gates are declared honestly (Brandli ISCAS 2014 behind IEEE; an MDPI 2026 title "uncomfortably close
to our framing" that returned 403). Both must close before an introduction is written, and the
document says so.
6. **Claims exceeding evidence.** Audit O6.1–O6.3. Only three, all minor, and one of them
("no differentiable method exists that estimates `c` per sequence") is a null claim the brief tells
me to treat as provisional.
7. **Experiment a hostile reviewer demands.** The cross-support generalisation experiment at network
scale — train on short exposure and slow motion, test on long and fast, with MCB as the readout. P6
has this at the level of a fitted correction (0.0% for a constant, 51% for a learned linear model,
91.2% for the closed form); a reviewer will demand it for a trained network. Its absence is fatal to
the "capacity cannot absorb it" claim, which is the paper's only defence against "your PSNR gain is
0.1 dB".
8. **Ranked fixes.** (i) Close the two verification gates. (ii) Lead with P7, not with the LME
correction — the calibration re-attribution is the result that cannot be compressed to one line.
(iii) Run the EVDI positive control early; if EVDI does not separate from REFID/EFNet, the causal
story is wrong and the document already commits to saying so. (iv) Strike "That belief has stood
untested for eight years. This paper tests it." — checklist item 64 (meta-explanatory sentence) and
189.

### Team 07 — Chronofields

1. **Verdict.** REJECT. Fatal to this execution, not to the idea.
2. **Summary.** The document inverts every perception head from `time → state` to `state → time`: a
chronofield predicts, for a queried state (a contrast crossing, a passage, a contact), a distribution
over when it held, with an explicit `∅` atom for "never". Events enter the likelihood as uncensored
observations, frames as interval-censored ones, and the blur integral is re-read as a constraint on
the spacing of crossing times. It derives a frame-timestamp bias `Δt ≈ a·T²/(24·v̄)` that diverges as
`v̄ → 0`, and a proposition that mAP is exactly invariant to any temporal shift smaller than the IoU
matching tolerance.
3. **Strongest reason to accept.** The C1 anchor — predict the next contrast-crossing time per pixel
from preceding real events plus one RGB frame, supervised by held-out real events — is real-sensor,
microsecond-exact, annotation-free ground truth for a genuine "when" task. It is the best insurance
against a ground-truth objection in this entire round.
4. **Strongest reason to reject.** The formulation change does not follow from the diagnosed failure.
The failure is "a frame's effective time is biased and sometimes multi-valued". Inverting the whole
query from `time → state` to `state → time` is one of at least four available responses (predict the
support; predict a trajectory; predict a distribution over the state at `t`; invert the map), and the
document gives no argument for why the inversion is the one the failure implies. That is a spine
break at exactly the joint the checklist's item 102 (Problem–Mechanism Correspondence) tests. The
document's own reviewer-proofness self-score of 5/10 — the lowest in the round — is the authors
noticing the same thing.
5. **Factual errors.** None found. One reinterpretation risk shared with Teams 04, 08 and 09: FAOD's
"80× frequency mismatch, ~3 mAP drop" is read here as "evidence that mAP cannot see time". It is
equally consistent with the alignment module working. No alternative-explanation kill test is offered
(checklist 74), and four of the ten ideas lean on this same reinterpretation, so if it is wrong four
papers move at once.
6. **Claims exceeding evidence.** Audit O7.1–O7.4.
7. **Experiment a hostile reviewer demands.** Time Lens → 1000 fps → RVT at every virtual frame, at
matched and unmatched compute. The document names this as the baseline that can kill the paper and
pre-registers a falsification threshold (within 15% of P95 CTE). Its absence is fatal, and its
*presence* is a coin flip.
8. **Ranked fixes.** (i) Run the C1 anchor and the reconstruct-then-detect head-to-head before
writing anything. (ii) Supply the missing argument for why inversion, specifically, is what the
failure implies — or drop the inversion and keep the censored-likelihood treatment of frames, which
is the part that actually follows. (iii) Cut six named datasets to two. (iv) Reduce five invented
metrics (CTE, SFR, TCE, CMR, FTB) to two; the document itself observes that its metric story "reads
from a distance exactly like inventing a metric you win on".

### Team 08 — Right Place, Wrong Time

1. **Verdict.** STRONG ACCEPT.
2. **Summary.** Every event and event–RGB benchmark scores a prediction against ground truth on a
different clock with a different temporal support, so the dominant fast-motion error — right place
along the path, wrong time — is booked as spatial error. The document decomposes matched (prediction,
GT) pairs into `e_⟂` in pixels and `e_∥/‖v*‖` in milliseconds, tests the temporal hypothesis for
identifiability by requiring one scalar `δ` to explain translation *and* box scale *and* yaw
simultaneously, derives the relaxation budget `τ_max = (w_G + w_P)/2` from the benchmark's and the
method's own published specifications rather than tuning it, and re-scores released checkpoints. It
proposes no architecture and no loss.
3. **Strongest reason to accept.** Its defence against the standing failure mode "a metric invented
by the authors on which, unsurprisingly, the authors win" is structural rather than rhetorical: there
is no author method to win. On top of that it stacks five named controls — an isotropic null with a
falsifiable threshold (`R ≈ 0.5` means the metric is vacuous and they report it as such), a coherence
test, a **pre-registered architecture prediction** registered before measurement, an
injection–recovery calibration, and a falsification method whose only job is to fail if the
decomposition is measuring an artifact. And it concedes its own borrowed algebra in writing:
"We are importing it, not inventing it — and we say so… Claiming to invent along-track error would be
the fastest way to get desk-rejected."
4. **Strongest reason to reject.** The paper has no positive result of its own. If P6 (the ranking
flip) does not land, what remains is a table of milliseconds about other people's models, and the
declared fallback (E0 label forensics) is a different paper with a different thesis.
5. **Factual errors.** One, and it matters. Section 2 states: "for a uniform event rate the
information centroid of the input is `t − 25 ms`. That is a *prediction*, not a hypothesis". The
brief's verification of RVT source confirms the window `[t−50 ms, t]` and the uniform-weight centroid
`t − 25 ms`, but then states explicitly: "Whether the trained network weights the ten bins uniformly
is unmeasured, so 25 ms is a reference point, not a prediction of network behaviour." The document's
input-side arithmetic is correct; the slide from input centroid to P1's predicted *output* latency
`τ̂ ∈ [−35, −10] ms` is not licensed, because it requires the untested assumption that the network
weights its bins uniformly. Correction: state `t − 25 ms` as the input representation's centroid and
present P1 as a hypothesis about network behaviour that C3 tests.
6. **Claims exceeding evidence.** Audit O8.1–O8.4. The pattern is characteristic and easily fixed:
several sentences state categorically what the immediately following sentence correctly scopes.
7. **Experiment a hostile reviewer demands.** The isotropic null `AP^iso` and the anisotropy ratio
`R`. Already control C1, with a pre-declared vacuity threshold. Its absence would be fatal; its
presence is the reason this idea ranks first.
8. **Ranked fixes.** (i) Correct the input-centroid / output-latency slide (item 5). (ii) Scope
"No published event benchmark states, enforces, or checks this" to "of the six we examined", matching
the scoping the very next clause already uses. (iii) Remove "purely" from "A ~20 mAP gap that is
purely a timing gap" — that is the conclusion of the experiment, not its premise. (iv) Run E0 first;
it is a 4.7 MB label file, zero GPU, and it is the fallback paper's core result.

### Team 09 — Change-Time

1. **Verdict.** REJECT. Fatal to the idea as stated, recoverable only if the second pillar is
separated out and the invariance claim is abandoned or re-scoped.
2. **Summary.** The document kills the assumption that a single global second-valued timeline exists,
replacing it with a per-pixel clock field `τ(x,t) = C·N(x,t)` — accumulated change, not duration —
in which the event stream is a complete observation of the intensity path to `O(C)` and any function
of the representation is exactly invariant to monotone time reparameterisation. The frame's temporal
support becomes a measured per-pixel width `W(x) = C·N_exp(x)`, zero on static pixels, and the fusion
weight `1/W(x)` is derived from the sensor model rather than learned. Two make-or-break predictions
are pre-registered: ASTW's clamp elbow at `ρ ≈ 25` (computed from the competitor's own hyperparameter
table), and hyperbolic `k·T` iso-error contours on a speed × exposure grid.
3. **Strongest reason to accept.** The `β`-is-the-window identity is genuinely strong evidence,
verifiable from released code (DAGr `time_window = 1e6` µs, AEGNN `beta=0.5e-5` with `torch.min(ts)`
as a window origin, EFGCN's `t*_i = ⌊β·t_i/T⌋`), and it converts "grid-free is not timeline-free"
from an assertion into a citation. P3's elbow, predicted in advance from a competitor's published
table rather than fitted, is exactly the kind of pre-registration this round should reward.
4. **Strongest reason to reject.** The invariance claim is destroyed by the mechanism used to
motivate it, in the same document. The motivation is: recorded timestamps are already corrupted by an
unknown monotone `φ`, because the AER bus saturates and — quoting the document's own citation —
"the larger the refractory period the fewer events are produced by fast moving objects". But
`τ(x,t) = C·N(x,t)` is a function of the *event count*, and refractory dead-time changes the count,
not merely the stamps. A mechanism that destroys events is not a monotone reparameterisation of time;
it changes `N`, and therefore changes `τ`, and therefore breaks the "identical bit-for-bit"
invariance. The paper's motivation and its central theorem cannot both stand. This is not a
presentation problem; the claim itself has to change.
5. **Factual errors.** (a) The contradiction above. (b) "**The sensor is not lossy; the coordinate
is.**" is false as written, and false by the document's own citations two paragraphs earlier —
refractory dead-time genuinely destroys brightness change. (c) "Estimated residual risk of a missed
direct hit: **<5%**" is a fabricated precision on an unmeasurable quantity, asserted by a team whose
own next sentence says the WebSearch quota was exhausted and CVF/Semantic Scholar were rate-limited.
6. **Claims exceeding evidence.** Audit O9.1–O9.6. This is the largest cluster in the round and the
only one where the overclaims are load-bearing rather than decorative.
7. **Experiment a hostile reviewer demands.** P3, against ASTW with its six hyperparameters re-tuned
by the reviewer's choice rather than the authors'. The document commits to sweeping
`(Δt_min, Δt_max)`, which is right, but a reviewer will ask for patch size, `γ` and `Δt_ref` too. Its
absence is fatal to pillar 1.
8. **Ranked fixes.** (i) Resolve the invariance/refractory contradiction — most likely by restating
invariance for the idealised model and *measuring* the departure on real data, which turns the
contradiction into a result. (ii) Delete the "<5%" figure and every zero-hit keyword conjunction used
as a novelty argument; replace with "we searched X, Y, Z and did not find". (iii) Separate pillar 2
(`W(x)` as a measured per-pixel frame support) into its own document — it is the part that answers
this round's seed and it does not depend on the broken invariance claim. (iv) Cut the eight invented
metrics to three. (v) Cut the related-work table by half; at 409 lines with four competing arguments
this is a survey, not an idea.

### Team 10 — Fusion Is Ill-Typed

1. **Verdict.** BORDERLINE.
2. **Summary.** A frame is a mass-one probability measure applied in the linear domain; an event bin
is a mass-zero signed measure on two instants applied in the log domain. The document shows the two
sets are disjoint, so no shift, scale or warp maps one to the other, and concludes that alignment is
orthogonal to the defect. It builds a type system (photometric domain, temporal measure, spatial
trajectory, per-pixel offset) with five typing rules, a static checker, and a diagnostic that audits
published architectures via Jacobian influence so it applies to gates and AdaIN and not only to
attention. The headline prediction is that event utility — measured by modality dropout at inference
— *inverts* with scene speed.
3. **Strongest reason to accept.** `EU(s)` is the best single falsifiable field-level claim in this
round and it degrades gracefully: if the curve merely flattens instead of falling, the finding is
smaller but still a finding, and the paper is not false. That is precisely the property this round
should be selecting for, and most of the other nine ideas lack it.
4. **Strongest reason to reject.** Proposition 1 is close to a tautology — an interval mean and a
boundary difference are different functionals, which nobody disputes — and it is asked to carry the
entire indictment of the field's architectures. The inference "the observables differ in type,
therefore mixing them is undefined as measurement" does not hold: RGB-D fusion mixes radiance and
depth, which differ in type by any reasonable definition, and works. A learned feature mixture is not
required to be an estimate of any single observable. The document's Death 3 anticipates exactly this
("a hostile reviewer calls Prop. 1 a two-line triviality") and its mitigation — show the violation in
published code with numbers — is right but does not repair the logical gap.
5. **Factual errors.** None found. One scoping problem: the thesis says "every concatenation, gate,
cross-attention and contrastive loss in the RGB–event literature", whereas the body correctly says
"Every RGB–event paper **we surveyed** adopts it verbatim". The body's scoping is the honest one and
should be promoted to the thesis.
6. **Claims exceeding evidence.** Audit O10.1–O10.5. The worst is "the **support-blind pair** result
cannot fail" — a sentence a reviewer will quote back verbatim, and one that is not even true: the
construction requires a single polarity-sum bin spanning the reversal, and a model consuming
per-event timestamps within the bin can separate the pair.
7. **Experiment a hostile reviewer demands.** The high-`s` fine-tuning experiment: if OSAM falls by
more than 0.08 after fine-tuning, the "training cannot fix it" claim — the sentence that makes this a
formulation paper rather than a training paper — is dead. Its absence is fatal.
8. **Ranked fixes.** (i) Demote Proposition 1 from load-bearing to explanatory, and make `EU(s)` the
title claim; the document's own Death-3 fallback already says this. (ii) Scope the support-blind pair
construction to the representations for which it holds. (iii) Delete "cannot fail". (iv) Import the
body's "we surveyed" scoping into the thesis sentence.

---

## Overclaim audit

Every sentence across the ten documents whose claim strength exceeds the evidence that will exist.
Quoted verbatim, with location, why it overclaims, and a calibrated rewrite. Ordered by team.

### Team 01

**O1.1** — thesis, line 5.
> "A motion-blurred frame carries **no information whatsoever** about the absolute time interval it
> integrated"

Why it overclaims: true only for a noiseless, unsaturated, scene-agnostic idealisation. A real frame
carries information about `T` through photon-noise variance, through saturation, through blur extent
combined with any motion prior, and — decisively — the document itself adds `L_meta = |T̂ − T_exif|`
and a blur-as-integral term precisely to extract exposure information. The thesis is contradicted by
the method section of the same document. It is also written so that a real-but-small residual
identifiability makes the paper *false* rather than modest.
Calibrated rewrite: "Under the normalised image-formation model, a motion-blurred frame determines
the intra-exposure path and its dwell density but not the affine time map `(t0, T)`; any residual
information about the exposure comes from photometric side channels, not from the blur geometry."

**O1.2** — thesis, line 5.
> "we prove this non-identifiability"

Why it overclaims: the document's own statement of the result is "**Proposition (informal)**" with a
"Proof sketch". Compare BeNeRF (ECCV 2024), which recovers an intra-exposure trajectory from blur
plus events and says "we demonstrate the possibility". "Prove" invites a reviewer to check a proof
that does not exist in the required form.
Rewrite: "we state and verify the non-identifiability of `(t0, T)` under the normalised model".

**O1.3** — line 33.
> "The frame does not determine `t0` or `T`. Not approximately — **not at all**; they do not appear."

Why: rhetorical intensification of O1.1 (checklist 188, S1). The parenthetical "they do not appear"
is the substantive claim and it is correct about the *equation*; the intensifier is what fails.
Rewrite: "`t0` and `T` do not appear in the substituted integral, so the blur geometry alone does not
constrain them."

**O1.4** — line 36.
> "no amount of data, capacity, or fusion architecture can recover which one the label meant."

Why: an impossibility claim about all future architectures, derived from a property of one forward
model. Also false for architectures that read the exposure metadata, which the document's own
`L_meta` does.
Rewrite: "a model that observes only the frame and a scalar timestamp has no input from which `α`
could be recovered."

**O1.5** — line 42.
> "…that all standard metrics average to zero"

Why: "all" over an unenumerated set (checklist 24). The document then names three metrics.
Rewrite: "that mAP, IoU-based success-AUC and EPE average to zero, for the three structural reasons
given below."

**O1.6** — line 59.
> "Read plainly: *most of what the field calls 'blur difficulty' is a coordinate-system offset.*"

Why: a prediction (`bias²_∥ > 50%` of squared error at `d > 15` px on one subset of one dataset)
restated as an established reading of the field. If the measured fraction comes back at 30%, this
sentence is false while the science is intact — the definition of a fragile claim (checklist 77).
Rewrite: delete. The prediction one line above already carries the content.

**O1.7** — line 61.
> "A gap that looks like appearance/sensor domain shift is a **clock-convention shift**."

Why: declarative before measurement, and the prediction it summarises is itself hedged ("to within
25%"). Rewrite: "we predict that the `d`-conditioned transfer degradation is largely accounted for by
`(α_A − α_B)·d`, and test whether the free-lunch shift removes it."

**O1.8** — line 153.
> "so all estimates are reported with false temporal precision."

Why: "all", plus "false", applied to the entire literature's reporting practice.
Rewrite: "so the temporal resolution of a state estimate is not currently reported."

### Team 02

**O2.1** — line 80, prediction 1.
> "**Severe blur with zero acceleration produces a perfectly well-posed label.**"

Why: contradicted by the document's own convention table on the same page. `A_hull` (tightest box
containing the whole streak) and `A_core` (the sharp part) diverge under uniform blur of any
magnitude, so `D = 1 − min_{A,A'} IoU` cannot be `< 0.05` at `β = 3` over the stated set 𝒜. This is
the round's clearest internal contradiction between a headline prediction and its own definitions.
Rewrite: either restrict 𝒜 to functionals of the dwell density alone and say so, giving "under
constant velocity the mid-, mean- and mode-conventions coincide exactly, so ill-posedness among them
is governed by intra-exposure acceleration rather than blur magnitude"; or keep 𝒜 and predict a
smaller, `β`-dependent floor.

**O2.2** — line 24.
> "and *no benchmark in computer vision states which A it used.*"

Why: a universal over an unenumerable set, from a team the brief lists as unable to finish its
prior-art sweep. This is the "no work does X" versus "we searched and did not find X" distinction in
its purest form.
Rewrite: "we checked COCO, KITTI, Prophesee GEN1/1Mpx, DSEC-Det, FE108 and EVIMO2 and none states
which `A` it used."

**O2.3** — line 84.
> "**A quarter of the remaining headroom on this benchmark is definitional, not learnable.**"

Why: a pre-registered prediction ("≈25% of FE108's fast-motion frames") typeset as an established
fact, in bold, with the qualifier "fast-motion" silently dropped.
Rewrite: "we predict that on the ≈25% of FE108 fast-motion frames with `ν > 0.3`, the oracle point
predictor's floor `e*` exceeds the current SOTA-to-runner-up gap."

**O2.4** — line 82.
> "**The indictment.** … The convention moves the score more than the method does."

Why: prediction 3 has not been run. "Indictment" is courtroom rhetoric (checklist 63, 191).
Rewrite: "Prediction 3: on the top-20% `ν` subset, a convention switch changes a fixed model's RSR by
10–20 points, against a 3–8 point spread between the five published trackers."

**O2.5** — line 165.
> "This is an un-arguable experiment: it is a proof, not a benchmark delta."

Why: the experiment is a trained model achieving "~100%" on time-reversal pairs. That is an empirical
result with a seed, a training set and a failure rate. Compare the ECCV 2024 conformal paper, which
has an actual theorem and still writes "we find that". "Un-arguable" is the adjective that guarantees
a reviewer will argue.
Rewrite: "Frame-only methods are at chance on this construction by Proposition 1; we measure whether
the event term recovers the ordering, and report the accuracy."

**O2.6** — line 110, Proposition 1 heading.
> "Proposition 1 (frames measure mass, and *only* mass)."

Why: "only" holds for the locally rigid, noise-free linearisation stated; the proposition text carries
the conditions but the heading does not, and the heading is what gets quoted.
Rewrite: "Proposition 1 (for a locally rigid patch, the frame is a linear functional of `Π_#μ`)."

### Team 03

**O3.1** — line 66, prediction 4.
> "The representation is *provably* unable to separate two inputs whose correct answers differ."

Why: the same sentence quantifies the claim as `‖φ(A)−φ(B)‖/‖φ(A)‖ < 3%`. Three percent is not zero,
a measured ratio is not a proof, and "unable" is an impossibility claim resting on a threshold the
authors chose. This is the single sharpest claim/evidence mismatch in the round: the strength word
and its own refutation sit in the same sentence.
Rewrite: "For matched pairs, the fused code changes by less than 3% of its norm while the correct
targets differ by more than the inter-class spread; our support-augmented encoder changes by more
than 30%."

**O3.2** — line 129.
> "The first four are *inexpressibility*, not *inaccuracy* — no retraining fixes them."

Why: items 1 and 2 (abstention; measured-quiet versus never-measured) are genuinely representational.
Item 4 is the empirical 3% result above, and item 3 depends on the architecture. A blanket "no
retraining fixes them" over all four inherits the weakest member's evidence.
Rewrite: apply the inexpressibility label to items 1–3 and label item 4 as a measurement.

**O3.3** — line 159.
> "we found no work that predicts a temporal support measure as its output, and no work that computes
> attention as an overlap of supports."

Why: correctly phrased as a search outcome — this one is fine and should be the template for the
other nine documents. Flagged here only to note that the *self-score* then converts it into
"does not exist in the literature we searched", which is also acceptable, whereas the novelty
argument later leans on it as if it were established. Keep the search-outcome phrasing everywhere.

**O3.4** — line 104.
> "when it vanishes the logit goes to `−∞` and the pair is refused aggregation no matter how similar
> the features look."

Why: `log(⟨s^F, s^E⟩ + ε)` with `ε > 0` does not go to `−∞`; it goes to `log ε`, scaled by `λ`. The
mechanism claim as written is stronger than the equation printed one line above it.
Rewrite: "as the overlap vanishes the logit falls to `λ log ε`, which suppresses the pair regardless
of feature similarity for a suitable `λ`."

### Team 04

**O4.1** — line 29.
> "**a detector whose output does not change when you shift the temporal support is a detector that
> has thrown time away.**"

Why: a slogan and a definitional assertion (checklist 188, S1). It is also not necessarily true —
invariance could arise from correct compensation, which is the FAOD authors' own claim. The document
gives no alternative-explanation kill test for this reading.
Rewrite: "Under fast motion the correct output changes with the temporal support, so shift-invariance
is only correct if the model compensates rather than marginalises; we test which, by measuring `τ̂`
on FAOD."

**O4.2** — line 29.
> "We claim this is the disease presented as the cure"

Why: metaphor (checklist 191, S4). Delete; the sentence after it carries the argument.

**O4.3** — line 74.
> "A timestamp that depends on texture is not a timestamp."

and line 101:
> "A timestamp that is a function of scene content is not a property of the sensor system; it is an
> artifact of the formulation."

Why: definitional assertions dressed as findings. The measurable content is `dτ̂/dA ≠ 0`.
Rewrite: "`τ̂` varies with the texture-asymmetry index `A` at fixed clock, exposure and speed, so it
is not a property of the sensor configuration."

**O4.4** — line 96.
> "*This is the exact analogue of 'you measure the occluder's depth, not the target's': you ask for
> the state at `t`, you get a mosaic of states at times you never asked for.*"

Why: metaphor plus anthropomorphism ("you ask", "never asked for"), checklist 190/191.
Rewrite: delete; the histogram and the heat map are the evidence.

**O4.5** — line 69.
> "The network was **told** the right time and still cannot deliver it"

Why: anthropomorphism (checklist 190, S3), and it states the outcome of ablation 8.5(c) — which is
designed to test whether `τ̂` follows the label clock or the evidence centroid — before that ablation
has been run.
Rewrite: "Training with labels at `t_q` does not, to first order, move `τ̂` to `t_q`; ablation (c)
measures how far the label clock pulls it."

### Team 05

**O5.1** — thesis, line 7.
> "we prove and measure that the best possible time offset leaves a structured, speed-dependent
> residual … that no offset, learned or hardware, can remove."

Why: T1 is a genuine theorem, but it holds for the shift group acting on the log-linearised,
locally-translating model. "No offset, learned or hardware" reads as a claim about deployed systems,
where a learned per-pixel module combines a shift with a spatial resampling and is therefore not in
the shift group at all. The document knows the conditions — it restricts T3 explicitly to the
log-linearised model in a parenthetical risk note — but the thesis drops them.
Rewrite: "under the log-linearised translating-scene model we prove that the shift group cannot
remove the modulus mismatch between the two channels, and we measure that the residual floor is
approached within a few percent for `b > 2` px."

**O5.2** — line 27.
> "So no `δ` — not per-frame, not per-pixel, not per-event, not learned — reduces the disagreement to
> zero"

Why: same scope problem, stated as an enumeration that sounds exhaustive.
Rewrite: "no element of the shift group — however finely parameterised — reduces the disagreement to
zero."

**O5.3** — line 62.
> "**Calibrating faster makes your calibration worse**, which is the opposite of every calibration
> protocol's assumption"

Why: slogan (S1) plus "every calibration protocol" (checklist 24). The measurable statement is
prediction 4's OBD in ms/px.
Rewrite: "`|dδ̂/db| ≳ 0.05 T` per pixel of blur, so a faster calibration motion increases the offset
bias; the protocols we checked (EF-Calib, eKalibr) assume the opposite."

**O5.4** — line 160.
> "The CVPR 2026 proceedings contain 60+ event papers and none is about event–frame temporal support
> or exposure-aware calibration."

Why: a "none" claim over a full proceedings, from a team the brief lists as unable to finish its
sweep, with a suspiciously precise "60+".
Rewrite: "We scanned the CVPR 2026 event-camera papers we could retrieve and found none addressing
event–frame temporal support or exposure-aware calibration; the sweep was not exhaustive."

### Team 06

This is the lightest cluster in the round, which is the point of the ranking.

**O6.1** — line 161.
> "**on textured content — which is what natural video is — the residual is 2.6 contrast thresholds
> and 99 % of it is the exposure operator.**"

Why: the measurement is on a band-limited *translating texture* model. "Which is what natural video
is" generalises from one synthetic scene class to all natural video, in a parenthetical, in bold.
Rewrite: "on band-limited translating texture the residual is 2.6 contrast thresholds and 99% of it
is explained by the exposure operator; whether natural video sits closer to this regime or to the
edge regime is measured on GoPro and DSEC in Stage 1."

**O6.2** — line 264.
> "the blur everyone treats as the problem is what makes `c_p` identifiable"

Why: "everyone" (checklist 24), and it is false of the very papers the document cites approvingly
(EVDI, mEDI), which treat blur as an integral to be modelled.
Rewrite: "blur, ordinarily treated as the degradation to be removed, is what makes `c_p`
identifiable."

**O6.3** — line 61.
> "**no differentiable method exists that estimates `c` per sequence from paired events and frames**"

Why: a null existence claim; the brief instructs that all such claims are provisional.
Rewrite: "two independent sweeps found no differentiable per-sequence estimator of `c` from paired
events and frames; the closest are a non-differentiable events/pixel/s proxy and the least squares of
Wang et al."

Also flagged, not as an overclaim but as checklist 64/189: "That belief has stood untested for eight
years. **This paper tests it.**" — a meta-explanatory sentence about the paper rather than about the
science. Remove.

### Team 07

**O7.1** — line 10.
> "because a frame does not have a timestamp and never did."

Why: rhetorical flourish (S1). A frame has a recorded timestamp; the claim is that the recorded
timestamp is a convention with no unique physical referent under acceleration.
Rewrite: "because the scalar timestamp attached to a frame is a maximum-likelihood point estimate
under a uniform-dwell prior, not a measurement."

**O7.2** — line 50.
> "**mAP is invariant to a group of temporal shifts** and no existing event–RGB detection benchmark
> can distinguish a method that is right at the right time from one that is right at the wrong time."

Why: the proposition immediately above it is conditional — "If `δ·v_max < ε`". The sentence drops the
condition and becomes a universal about all benchmarks and all timing errors. As written it is false
for any timing error large enough to exceed the matching tolerance, which is exactly the regime the
paper cares about.
Rewrite: "mAP is exactly invariant to temporal shifts smaller than `ε/v_max`; within that band no
current event–RGB benchmark can distinguish right-time from wrong-time predictions."

**O7.3** — line 48 (and the same move in Teams 04, 08, 09).
> "their own headline result is our evidence that mAP cannot see time"

Why: FAOD's 3-point drop under 80× mismatch is equally consistent with the alignment module working
as intended. No alternative-explanation kill test is offered (checklist 74). Four of the ten ideas
lean on this single reinterpretation, so the shared exposure is a round-level risk.
Rewrite: "FAOD reports a 3-point mAP drop under an 80× frequency mismatch. Two readings are
available — the alignment succeeds, or mAP is insensitive to the residual timing error. We
discriminate them by measuring CTE on the same checkpoints."

**O7.4** — line 138.
> "Frames are *irreducibly censored observations of time*, and the universal midpoint stamp is a
> hidden, wrong prior — not a convention."

Why: "irreducibly" and "universal" are both stronger than the evidence, and the last clause is a
definitional dispute rather than a finding.
Rewrite: "A frame constrains the transition time to an interval and cannot constrain it further; the
midpoint stamp is the MAP estimate under a uniform-dwell prior, which fails under intra-exposure
acceleration."

### Team 08

**O8.1** — section 2, line 19.
> "**No published event benchmark states, enforces, or checks this. It is false in every case we
> examined, and the violation is on the order of 25–50 ms**"

Why: the first sentence is a universal; the second, in the same breath, applies the correct scope
("in every case we examined"). The document already knows how to scope and does not do it
consistently.
Rewrite: "Of the six benchmarks we examined, none states, enforces or checks this, and in all six it
is false, with violations of order 25–50 ms."

**O8.2** — section 2, line 37.
> "**for a uniform event rate the information centroid of the input is `t − 25 ms`.** That is a
> *prediction*, not a hypothesis"

Why: correct about the input representation, not licensed about the network's output. The brief's
verification says explicitly that whether the trained network weights the ten bins uniformly is
unmeasured, so `t − 25 ms` is a reference point, not a prediction of behaviour. P1 then predicts an
*output* latency in `[−35, −10] ms` on this basis. The arithmetic is right; the inference is a step
the evidence does not support.
Rewrite: "the input representation's uniform-weight information centroid is `t − 25 ms`. Whether the
trained network weights its ten bins uniformly is unmeasured, so we register `τ̂ ∈ [−35, −10] ms` as
a hypothesis that control C3 tests, and we report a miss as a miss."

**O8.3** — line 34.
> "**The high-rate ground truth of the two flagship 'low-latency' event benchmarks is a linear motion
> model.**"

Why: the document's own quotation of DSEC-3DOD includes "Data annotation experts refined interpolated
bounding boxes", so the GT is linear interpolation *plus expert refinement plus VFI-synthesised
sensor data*. The bold sentence is stronger than the evidence quoted two lines above it — and P7 is
precisely the experiment that would measure how much of it survives refinement. Stating the answer
before the measurement is the error.
Rewrite: "The high-rate ground truth of both flagship benchmarks is seeded by linear interpolation
and then refined. P7 measures how much information the released labels carry beyond that prior."

**O8.4** — line 72.
> "**A ~20 mAP gap that is purely a timing gap is currently reported in mAP units and has no name.**"

Why: "purely" is the conclusion of the decomposition, used as its premise. Some of the 53.61 → 33.32
drop could be genuine degradation.
Rewrite: "A ~20 mAP gap that we hypothesise is largely a timing gap is currently reported in mAP
units; our decomposition tests what fraction of it is temporal."

### Team 09

**O9.1** — line 136.
> "**The sensor is not lossy; the coordinate is.**"

Why: false by the document's own citations. Two paragraphs earlier it quotes Gallego et al. that "the
larger the refractory period the fewer events are produced by fast moving objects" — a genuine
destruction of information by the sensor, not by the coordinate. Slogan (S1) carrying a false claim.
Rewrite: "Under the ideal DVS model, the information loss usually attributed to event sparsity lives
in the map `t ↦ τ` rather than in `L̃`; refractory dead-time is a separate, genuine sensor-side loss
that we model explicitly."

**O9.2** — line 138.
> "so `S` is **unchanged**. Any function of `S` is *exactly* invariant to monotone time
> reparameterization — not robust, not approximately: identical bit-for-bit."

Why: this is the round's most consequential overclaim, because it is load-bearing rather than
decorative. `τ(x,t) = C·N(x,t)` depends on the event *count*. The physical mechanism the document
uses to motivate the whole idea — refractory dead-time and AER bus saturation — changes `N`, not just
the stamps. Motivation and theorem cannot both stand as written.
Rewrite: "Under the ideal DVS model, warping every timestamp by a strictly increasing `φ` leaves `S`
bit-identical. Real rate-dependent effects (refractory dead-time, bus saturation) change the event
count itself and therefore change `S`; we measure the resulting departure from exact invariance as a
function of event rate and report it as the operating envelope."

**O9.3** — line 32.
> "**A representation that reads absolute seconds is reading a corrupted coordinate, and the
> corruption is worst where the task is hardest.**"

Why: slogan; also assumes the corruption is monotone-and-only-monotone, which the refractory citation
in the same paragraph contradicts.
Rewrite: state the two mechanisms and their measured magnitudes separately.

**O9.4** — line 12.
> "**Two pillars, both verified unclaimed.** (i) `"temporal support"` + `"event camera"` returns
> **zero** arXiv abstracts."

Why: a zero-hit keyword conjunction over arXiv *abstracts* is evidence about phrasing, not about
concepts. The document then treats it as verification of unclaimedness and builds the novelty case on
it. This is precisely the "no work does X" versus "we searched and did not find X" substitution the
brief asks me to police, and here it carries a pillar.
Rewrite: "We did not find the phrase `temporal support` co-occurring with `event camera` in arXiv
abstracts. That is weak evidence about terminology, not about prior art; the substantive novelty
claim rests on the two mechanisms below."

**O9.5** — line 368.
> "Estimated residual risk of a missed direct hit: **<5%**."

Why: a fabricated precision on an unmeasurable quantity, asserted in the same paragraph that admits
the WebSearch quota was exhausted and that CVF and Semantic Scholar were rate-limited.
Rewrite: "The sweep is incomplete: WebSearch quota exhausted, CVF and Semantic Scholar rate-limited.
Treat the novelty claim as unverified until the named Google Scholar passes are done."

**O9.6** — line 254.
> "We show no global schedule can work when `∇L·v` is spatially non-uniform"

Why: "no … can work" over all schedules, from an argument about one error term.
Rewrite: "We show that under a global schedule the per-pixel quantisation error scales as
`C·n·r(x)/R`, so no single global `n` bounds it uniformly across pixels."

### Team 10

**O10.1** — thesis, line 5.
> "every concatenation, gate, cross-attention and contrastive loss in the RGB–event literature mixes
> measurements of different *type*"

Why: universal over a literature; the body scopes it correctly ("Every RGB–event paper **we
surveyed**"). Promote the body's scoping.
Rewrite: "every fusion operator in the six RGB–event architectures we surveyed mixes measurements of
different type".

**O10.2** — line 22.
> "**Perfect temporal and spatial registration leaves the two quantities as different observables.**
> Alignment is orthogonal to the defect."

Why: the first sentence is true and near-tautological; the second does not follow. Two different
observables of the same latent can be fused correctly — this is what RGB-D does. The document needs
the extra step showing that the *specific* difference (mass 1 versus mass 0; linear versus log) is
what causes the measured `EU(s)` inversion, and that step is exactly what Panel A is for.
Rewrite: "Registration changes `κ` and `t̄` but not `φ` or `o`; whether that residual type difference
is what degrades event utility with speed is the question Panel A answers."

**O10.3** — line 24.
> "It is not an estimate of the frame's observable, not an estimate of the event's observable, and
> not an estimate of any scene quantity at all."

Why: a learned intermediate feature is not required to be an estimate of anything, so "undefined as
measurement" is a category claim about representation learning, not a defect.
Rewrite: "The mixture has a well-defined temporal measure `Σα_jμ_j` that no current framework
records, so downstream layers cannot condition on what they are mixing."

**O10.4** — line 99.
> "**Every published model maps this pair to one input point and emits one confident answer for two
> different worlds.**"

Why: conditional on a polarity-sum bin spanning the whole reversal. A model consuming per-event
timestamps, or a finer bin partition, separates the pair. "Every published model" is false as stated
and the document's own `B`-sweep ablation is what determines the boundary.
Rewrite: "Any model whose event representation reduces the reversal interval to a single polarity-sum
bin maps this pair to one input point; the `B`-sweep locates the bin count at which the pair becomes
separable."

**O10.5** — line 215.
> "the **support-blind pair** result cannot fail."

Why: "cannot fail" is the sentence a hostile reviewer quotes back, and it is untrue for the reason in
O10.4. It also removes the paper's own falsifiability, which is the opposite of what the risk section
is for.
Rewrite: "the support-blind pair result depends only on the construction and on models being
deterministic, so it is the least likely of our results to fail."

---

## Spine test

A spine is: a failure a reader believes → an explanation that follows from it → a formulation that
follows from the explanation. Stated in one sentence each, or declared absent.

**Team 04.** *The prediction's effective timestamp is not the time you asked for, it is set by the
evidence centroid, and it differs between regions of one output — therefore the output must carry a
trajectory and a declared, calibrated time.* Complete, single-variable, and the null case is written
in advance. **Strongest spine in the round.**

**Team 05.** *An oracle time offset cannot remove the residual between a box-integral channel and a
near-instantaneous one, because a shift cannot change a modulus — therefore calibration must return a
pair of measures and a validity mask instead of a number.* Complete, and the failure is a theorem
rather than a hope, which is why it needs no dataset to exist.

**Team 08.** *Benchmarks score predictions against ground truth on a different clock, so the dominant
fast-motion error is booked as pixels when it is milliseconds — therefore the unit of error must be
(px⟂, ms∥) and the leaderboard must be re-scored.* Complete, and unusually disciplined because it
proposes no method, so the spine has nothing bolted onto it.

**Team 01.** *The exposure interval is a latent nobody estimates, so the supervision target is a
convention rather than a measurement — therefore predict a trajectory on a normalised support with
the support inferred jointly.* Complete. Docked because the thesis sentence overshoots the spine: the
paper's argument needs "the blur geometry does not constrain `(t0,T)`", and the document claims "no
information whatsoever", which the method section then contradicts.

**Team 06.** *The event–frame identity is misspecified, not noisy, its bias has a closed form, and the
bias propagates into the field's threshold calibration — therefore supervise the exposure functional
and a threshold-invariant profile.* Complete and unusually well-attributed. Docked only because the
first link (misspecification) was already correct in EVDI, so the failure is half-known.

**Team 03.** *Two branches carry per-pixel supports that are frequently disjoint, and error tracks
support overlap rather than blur — therefore predict the support and fuse by overlap.* Complete. The
weak vertebra is the middle: the frame-branch support has no real ground truth, so the explanation is
demonstrated where it was constructed.

**Team 10.** *Event utility inverts with speed — because the two observables differ in type, not
timing — therefore type every tensor and only mix within a type.* The spine exists but the middle
vertebra does not bear load: type difference is not the only available explanation of the inversion
(receptive field, misregistration, and event-branch saturation all predict it too), and no
discriminating test is proposed.

**Team 02.** Two spines, not one. Spine A: *label ill-posedness is governed by acceleration, not blur,
so leaderboards rank agreement with an unwritten habit.* Spine B: *the prediction target should be a
measure, auditable on point-labelled benchmarks by convention-marginal conformal coverage.* Each is
good; joined, the reader must hold two theses, which checklist 152 forbids.

**Team 07.** Spine broken at one joint. The failure (frames have no unique effective time; mAP cannot
see time) is well-argued. The formulation (invert `time → state` into `state → time`) is *a* response
to it, not *the* response, and no argument is given for the choice. Everything downstream — the
censored likelihood, the eikonal, the `∅` atom — hangs from a joint that is asserted.

**Team 09.** **No spine.** Two declared pillars that "fail separately", plus a third argument (partial
order versus total order), plus a fourth (the `β`-is-the-window code evidence), plus a fifth (`W(x)`
as measured support). Four hundred and nine lines, a thirty-row related-work table, eight invented
metrics, eight ablations. The document is explicit that the pillars are independent, which is exactly
the property that makes it an assembly: a reader who loses pillar 1 does not lose their place, because
there was no single place to be.

**Ranking by spine strength:** 04 > 05 > 08 > 01 > 06 > 03 > 10 > 02 > 07 > 09.

**Titles that promise more than the paper can deliver:** Team 01 ("A Frame Is Not a Timestamp" is
fine; the *subtitle* claim of proof is not), Team 09 (a title promising a replacement for event
slicing, delivered as two independent pillars either of which may fail), Team 10 ("Fusion Is
Ill-Typed" promises a verdict on the whole literature from a proposition about two measures).
**Titles that are honest:** Team 05 ("No Offset Can Fix a Width" is a literal statement of T1), Team
08 ("Right Place, Wrong Time" is exactly what it measures), Team 06 (states the misspecification and
names the invariant that survives it).

**Contribution lists that are method-trick lists rather than problem-structure lists (checklist 5):**
Team 09 (a coordinate, plus a two-cut architecture, plus eight metrics, plus a code-forensics result),
Team 03 (a head, an attention modification, six metrics), and the operator half of Team 10. **Cleanest
problem-structure contributions:** Team 08 (a unit of error and a reporting contract), Team 04 (a
measurement primitive from which everything else is derived), Team 01 (`K = 0` is literally the
current formulation, so the contribution is defined as a superset rather than a module).

---

## Ranking

1. **Team 08 — Right Place, Wrong Time.** Inference-only on verified live checkpoints, ~35 GPU-h, no
   training, and a relaxation budget derived from published specifications rather than tuned; the only
   idea that defeats "you invented a metric you win on" by construction rather than by argument, and
   the only one that concedes its borrowed algebra before a reviewer can.
2. **Team 04 — When Is Your Prediction?** One measurement primitive, a three-day zero-download pilot,
   a pre-registered null result, and the decisive frame-only control named by the authors themselves;
   its rhetoric is heavy but confined to framing sentences that can be deleted without touching a
   result.
3. **Team 05 — No Offset Can Fix a Width.** The failure exists before the experiment because it is a
   property of the Fourier transform of a box; the ablation that would kill it runs first, and the
   load-bearing tier needs no GPU at all.
4. **Team 01 — A Frame Is Not a Timestamp.** The best formulation and the cleanest ablation-as-SOTA
   design in the round, held back by a thesis sentence the method section contradicts and by a real-
   data figure that depends on a dataset another team reports as dead.
5. **Team 06 — Frames Are Not Samples.** The most honestly calibrated document here, with headline
   numbers already measured and a re-attribution result (P7) that no restoration paper can produce —
   ranked fifth only because the fix is one line and the operator is already in print.
6. **Team 02 — No State at t.** A genuine change of prediction target and a quotable `π`-recovery
   result, blocked by an internal contradiction between its headline prediction and its own convention
   table, and by carrying two theses at once.
7. **Team 10 — Fusion Is Ill-Typed.** `EU(s)` is the best falsifiable field-level claim in the round
   and degrades gracefully, but the proposition asked to explain it is near-tautological and no test
   discriminates it from three ordinary alternatives.
8. **Team 03 — Temporal Support Fields.** A clean matched-pair construction and free real event-side
   ground truth, undercut by "provably" attached to a measured 3% and by a frame-branch supervision
   signal that exists only where the authors generate it.
9. **Team 07 — Chronofields.** Elegant and the C1 anchor is genuinely clever, but the formulation does
   not follow from the failure, the lethal baseline is likely to tie, and the authors' own reviewer-
   proofness score of 5/10 is the round's lowest.
10. **Team 09 — Change-Time.** The `β`-is-the-window code evidence is the single best-sourced fact
    produced by any team, and it is stranded in a document with no spine, whose central invariance
    theorem is falsified by the sensor mechanism used to motivate it.

---

## My winner and its fatal flaw

**Winner: Team 08, "Right Place, Wrong Time: Temporal-Support Error Is the Unmeasured Half of
Event–RGB Benchmarks."**

It wins on my axis and on the brief's. On mine: it is the only document whose strength words are
already matched to the evidence that will exist. It writes "We are importing it, not inventing it —
and we say so", "We never claim `AP^⟂` is 'the true score'", and "if `R ≈ 0.5`, our relaxation is just
loosened IoU and we report the metric as vacuous" — three sentences that pre-emptively surrender the
ground a hostile reviewer would otherwise take. Its register is the register of the six accepted
papers in my comparison set. On the brief's: it is inference-only on checkpoints verified live by HTTP
HEAD, ~35 GPU-h, nothing over 9 GB, no training, and its highest-yield experiment (E0 label forensics)
needs a 4.7 MB label file and no GPU at all. Under the brief's instruction that a merely good idea
certain to produce a real figure beats a beautiful one that is unfinishable, E0 alone clears the bar
by early October.

**Its fatal flaw: the quantity it measures is not attributable, and its headline unit is only
meaningful if the attribution goes the way it assumes.**

`τ̂` is a single number that absorbs at least three distinct sources: (a) the temporal centroid of
the input representation, which is arithmetic and known; (b) the trained network's actual weighting of
that representation, which is *unmeasured* — the brief says so explicitly about RVT's ten bins; and
(c) the annotation pipeline's own offset (GoPro exposure, QDTrack latency, ATIS integration,
homography warp), which is a property of the dataset and not of any method. The paper's pre-registered
prediction C3 — "`τ̂ ∈ [−35, −10] ms`, predicted from the declared 50 ms window" — is presented as the
strongest available evidence that the metric measures a physical quantity. But it is confirmable for
the wrong reason: if (c) happens to land in the same range, C3 passes while measuring the dataset. And
it is falsifiable without falsifying the thesis: if the network weights its bins non-uniformly, `τ̂`
lands outside `[−35, −10]` while the temporal-support error is exactly as real and as large as
claimed. A pre-registered prediction that can pass for the wrong reason and fail for the wrong reason
is not the control the paper needs it to be, and it is the load-bearing one.

The document does see the third component — Death 3 proposes a variance decomposition across (dataset,
method) and argues that a shared `τ̂` is itself publishable. That is a good answer to (c). It has no
answer to (b), and (b) is the component that decides whether "milliseconds" is a property of the model
or a restatement of the window length the authors already knew.

**What would fix it, in one experiment.** Measure the network's actual bin weighting directly —
occlude or zero each of RVT's ten histogram bins in turn at inference and record the induced shift in
`τ̂`. That yields an empirical input-weighting profile, converts `t − 25 ms` from an assumption into a
measurement, and turns C3 from a prediction that can pass for the wrong reason into a two-sided
attribution test. It costs one extra inference pass per checkpoint on data already downloaded, and
without it the paper's central unit is borrowed from a configuration file rather than measured.
