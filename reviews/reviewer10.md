# Reviewer 10 — the hostile reviewer

*CVPR20 idea-selection round. Domain: Temporal-Support-Aligned Event–RGB Perception.
I reject by default. My job here is to write, for each of the ten, the single most damaging
review that could honestly be written, and then to judge which idea best survives its own worst
review. Attacks I know to be answerable are marked answerable, with the answer.*

---

## Comparison set

Seven accepted papers, fetched and verified this session (title, venue, and acceptance confirmed
from the arXiv record). For each: the strongest objection a reviewer could have raised, and how
the paper defused it. This is my calibration for what "survivable" means at this venue.

**1. LEOD: Label-Efficient Object Detection for Event Cameras — Wu, Gehrig, Lyu, Liu, Gilitschenski, CVPR 2024** (arXiv 2311.17286).
*Strongest objection:* "Self-training on your own pseudo-labels is confirmation bias. Your +8.6 mAP
at 1% labels measures the quality of your pseudo-label generator's prior, not information extracted
from unlabelled data."
*How it was defused:* the teacher uses **bi-directional (non-causal) inference plus tracking-based
post-processing** — information the student structurally cannot access at inference time. The gain
therefore cannot be reproduced by the student's own prior. Plus soft anchor assignment that models
label noise explicitly rather than assuming it away, and a sweep over label fractions with the
fully-supervised ceiling drawn on the same axes.
*Lesson for this round:* **if your correction can be reproduced by the prior you already assumed,
it is not a result.** You must show the correction uses information the baseline cannot reach.

**2. State Space Models for Event Cameras — Zubić, Gehrig, Scaramuzza, CVPR 2024** (arXiv 2402.15584).
*Strongest objection:* "You invented the failure. Nobody deploys at a different inference frequency
than they trained at, so the >20 mAP collapse you fix is self-inflicted."
*How it was defused:* the collapse is demonstrated on **standard RNN and Transformer baselines under
their own published protocol**, not on a constructed one; and the paper carries a **second,
regime-independent benefit** (33% faster training) so it is not worthless if a reviewer refuses the
frequency-generalisation premise. Degradation is reported as a curve, not a point.
*Lesson:* a paper whose only value is fixing a regime the field does not operate in **must carry a
second benefit that survives rejection of the premise.**

**3. Motion-prior Contrast Maximization for Dense Continuous-Time Motion Estimation — Hamann, Wang,
Asmanis, Chaney, Gallego, Daniilidis, ECCV 2024** (arXiv 2407.10802).
*Strongest objection:* "Contrast maximization has a documented degeneracy (event collapse). Your
motion prior suppresses it, so you have tuned a regulariser and called it a method."
*How it was defused:* the headline is a **zero-shot transfer** number (+29% on EVIMO2 for a
synthetically trained model) — a result a tuned prior cannot buy, because the prior never saw the
target — plus SOTA on the **DSEC benchmark server, whose test ground truth is withheld.**
*Lesson:* withheld-test-set numbers and zero-shot transfer are how "you tuned it" is killed. Nothing
else works.

**4. BeNeRF: Neural Radiance Fields from a Single Blurry Image and Event Stream — Li, Wan, Wang, Li,
Zhou, Liu, ECCV 2024** (arXiv 2407.02174).
*Strongest objection:* "Recovering the camera trajectory *inside a single exposure* from one blurred
image plus events is an unidentifiable inverse problem. What you recover is your spline prior."
*How it was defused:* they **shrank the parameterisation to a cubic B-spline** so the claim is
exactly what is identifiable, and removed an external prior (no SfM-precomputed poses) rather than
adding one. The scope of the claim was cut to match the scope of the identifiability.
*Lesson — directly relevant to Teams 01, 02, 04, 05:* when your latent is weakly identifiable, you
shrink the parameterisation until the claim matches what the data determines. You do not prove a
non-identifiability proposition and then estimate the thing anyway.

**5. Adaptive Bounding Box Uncertainties via Two-Step Conformal Prediction — Timans, Straehle,
Sakmann, Nalisnick, ECCV 2024** (arXiv 2403.07263).
*Strongest objection:* "Coverage is trivially purchasable by enlarging the sets. A conformal
guarantee is a tautology of the method, not a contribution."
*How it was defused:* coverage is never the headline; **adaptivity and efficiency are**, with the
genuinely hard part (propagating label uncertainty into box uncertainty in the multi-object setting)
carried as the actual contribution.
*Lesson — directly for Team 02:* a set-prediction paper is judged **only** on the efficiency
frontier at matched coverage. Reporting that coverage was achieved is reporting that the algorithm
ran.

**6. Ev-3DOD: Pushing the Temporal Boundaries of 3D Object Detection with Event Cameras — Cho, Kang,
Kim, Yoon, CVPR 2025** (arXiv 2502.19630).
*Strongest objection:* "Your advertised 100 FPS ground truth is linear interpolation of 10 FPS boxes,
seeded against sensor data synthesised by a video-frame-interpolation network. You are scoring
methods against an interpolation prior."
*How it was defused:* they **stated the construction in their own paper**, added expert human
refinement, and — decisively — published the conventional-detector **offline-vs-online gap
(53.6 → 33.3 mAP)** so a reader can see the size of the timing term separately from the method's
contribution. They shipped the caveat as a number instead of burying it.
*Lesson — directly for Team 08:* the interpolation objection has **already been conceded in print by
the paper Team 08 attacks.** Quoting a limitations section back at its authors is not a result;
measuring the size of the effect is. Team 08's E0 is exactly that measurement, and that is the only
reason it is not vacuous.

**7. Unleashing the Temporal Potential of Stereo Event Cameras for Continuous-Time 3D Object
Detection — Kang, Cho, Yoon, ICCV 2025** (arXiv 2508.02288).
*Strongest objection:* "Event-only 3D detection is a solution looking for a problem; frames are
available and better."
*How it was defused:* the regime is one where the competing modality is **structurally absent**
(between frames), not merely worse, and the method is built around that absence rather than around
fusion.
*Lesson:* "our regime is where the other modality does not exist" survives. "Our regime is where the
other modality is 3% worse" does not.

*(Also fetched and verified as context, but **not** counted in the set because acceptance is not
established: FAOD, arXiv 2412.04149, is a preprint, not an accepted paper — Teams 01, 04, 05, 07, 08
and 09 all treat it as a load-bearing antagonist and none of them says it is unrefereed. BRENet,
arXiv 2505.01548, is likewise a preprint; Team 09 credits it with "actually proving an irreducible
shift," a claim the abstract does not support. If either becomes the paper you are positioned
against, you are positioned against a preprint, and a reviewer will say so.)*

---

## Per-idea verdicts

| # | Idea | Verdict | One-sentence reason |
|---|---|---|---|
| 01 | Latent exposure support / TSB law | **REJECT** | Proves a number recorded in the dataset file is unrecoverable from the pixels, validates its estimator against that recorded number, fixes the residual with one scalar per dataset, and stakes its money plot on a dataset another team reports is offline. |
| 02 | Exposure-occupancy measures | **REJECT** | The controlling variable (intra-exposure velocity change, normalised by box size) needs accelerations of order 10⁵–10⁶ px/s² to reach the predicted regime; that regime is an impact, not a benchmark. |
| 03 | Temporal support fields | **BORDERLINE** | The matched-blur/matched-event-count pair is matched only for an ideal sensor — refractory period and photoreceptor bandwidth unmatch it — so the covariate control fails on the exact axis being claimed. |
| 04 | Effective timestamp τ̂ / σ_τ | **REJECT** | The centrepiece collapse plot is an algebraic identity (along-track error divided by speed, multiplied by speed) and the pre-registered σ_τ signal is smaller than the noise its own spatial-error assumption implies. |
| 05 | No offset fixes a width | **BORDERLINE** | Theorem T1 is one line of Fourier analysis that forbids nothing anyone does, and the effect's own onset condition (blur ≥ 2 px) is not met by daytime DSEC's verified exposures. |
| 06 | Exposure gap / LME correction | **BORDERLINE** | The headline regression is a change of variables verified against itself; the fix is one line that CVPR 2022 already implements; the real-data version is circular in the unknown contrast threshold. |
| 07 | Chronofields | **REJECT** | The frame's entire contribution reduces to an interval-censoring bracket of ~1.5 ms inside a 100 ms window, i.e. numerically the midpoint stamp — the assigned seed is not answered. |
| 08 | Right Place, Wrong Time | **BORDERLINE (the strongest of the ten)** | Imported decomposition and a headline ranking flip whose primary candidate pair is separated by 0.5 published mAP, i.e. inside the bootstrap — but E0 cannot fail and costs nothing. |
| 09 | Change-time / per-pixel clocks | **REJECT** | Pillar 2 is refuted by the machine-verified event statistics (≈1.1 crossings per firing pixel, 6% of pixels); pillar 1's exact invariance is trivially true and is destroyed at the head by the team's own design. |
| 10 | Fusion is ill-typed | **REJECT** | Proposition 1 proves too much — by its rule every multimodal network ever trained is a type error — and both diagnostics (modality dropout, off-support attention mass) are known-invalid or tautological. |

---

## The killing review

### The attack that applies to all ten, first

Before the individual reviews, the one that every author here needs to read, because it is the
review the AC will remember.

The brief's verified facts say: DSEC frame period is **50 ms everywhere**; daytime exposure inside
`interlaken_00_c` is **1478 µs**; RVT's event representation is **50 ms wide, ending at the label
time**, with a uniform-weight centroid at t−25 ms. So on the field's flagship benchmark, with the
field's flagship detector, the frame's temporal support is **1.5 ms** and the event tensor's is
**50 ms**, and the gap between their centroids is **~25 ms**.

Therefore: *the temporal-support mismatch this entire round is organised around is, to a first
approximation, **97% a windowing convention that any implementer changes with one line of YAML**,
and **3% physics**.* The exposure term — the term Teams 01, 02, 05, 06, 07, 09 and 10 all build on —
is the second-order term. It is roughly 1.5 ms wide against a 50 ms window and a 50 ms frame period.
Even at night, where the brief confirms the windows are 10.1× wider, the exposure is 15 ms against a
50 ms window, and **six sequences sit pinned at exactly 14996 µs**, which is not a distribution — it
is a rail, i.e. auto-exposure saturating, in scenes that are dark and therefore slow.

Any paper in this domain must answer, in the abstract, the question *"is the effect you are
measuring larger than the effect of the event-window choice you made yourself?"* Nine of the ten do
not ask it. Team 08 is the only one whose formalism (declare `(c_P, w_P)` for both branches; measure
τ̂ for each) can even express the comparison, and it is the only one that would come out of the
comparison with a number rather than an excuse.

Second cross-cutting fact: **Teams 01, 02, 04 and 07 all stake their primary real-data figure on
FE108/FE240hz, and Team 09 reports that the host `fe108.dluticcd.com` refuses connection.** Four of
ten ideas share a single point of failure that a fifth team already tested and found dead. None of
the four checked. That is not a research risk; that is a planning failure, and it is why four of my
rejections below are partly logistical.

Third: **all ten invent a metric suite.** Team 01 invents four (TSB, TQ-AUC, SCR, SIE) and says so.
Team 03 invents six. Team 07 invents five. Team 09 invents eight. "You invented N metrics and won on
all N" is not a caricature here; it is a headcount. Only Team 08 escapes, and only because it
proposes no method to win with.

---

### Team 01 — *A Frame Is Not a Timestamp*

> The paper's spine is a non-identifiability proposition: a blurred frame carries no information
> about the absolute interval it integrated. This is true, it is proved in three lines by a change
> of variables, and it does no work whatsoever, because the quantity it declares unrecoverable is
> **printed in the dataset**. DSEC publishes per-frame exposure start and end in microseconds; DAVIS
> APS emits exposure start and end; the authors' own SIE experiment validates T̂ against DSEC's
> published exposures, and their own loss carries a term `L_meta = |T̂ − T_exif|` pulling the
> estimate toward the recorded value. So the paper proves that a number cannot be recovered from the
> pixels, estimates it anyway, and grades the estimate against the recorded number it just proved
> was unavailable to the pixels. That is not a proposition doing work; that is a proposition
> decorating an estimator that is being supervised by the answer.
>
> What is left once the proposition is set aside is the TSB law, `E[e_∥ | d] = (α_model − α_label)·d`,
> and the "free-lunch" correction. But α_label is an *annotation convention* — a property of a
> human, not of the world — and α_model is fitted. The law therefore reads: *the signed along-motion
> error is proportional to displacement, with a fitted constant of proportionality.* Every monotone
> bias satisfies this. And the free-lunch test — "estimate a single scalar α̂ per dataset and shift
> every baseline's prediction, zero learned parameters, one number per dataset, predicted to remove
> ≥40% of the excess error" — is the authors writing my review for me. **A one-scalar-per-dataset
> correction fitted to reduce the mean signed error, evaluated by the reduction in mean signed
> error, is not a finding; it is a residual with the mean taken out.** Unless α̂ is fitted on a
> disjoint split and reported with a confidence interval, the 40% is arithmetic.
>
> The pre-registered Figure 1a prediction is already falsified. The authors predict the left–right
> exposure-midpoint difference is "≥ 1 ms on a substantial fraction of frames, meaning the stereo
> pair — and hence disparity GT — is support-inconsistent." The verified measurement on the target
> machine is a **median of 16–144 µs and a maximum of 380 µs**. The prediction is wrong by a factor
> of ~2.6 at the extreme and roughly an order of magnitude at the median, and the disparity-GT
> corollary drawn from it does not exist. A pre-registered prediction that is false before the paper
> is written is the worst possible advertisement for the other pre-registered predictions.
>
> Finally, the money plot (Fig 1b, real intra-exposure GT on FE240hz) depends on a dataset whose
> host another team in this round reports as refusing connection, and the authors' own self-score
> concedes "if that access does not arrive, the strongest real-data plot is gone."

**FATAL** — not to the topic, but to this execution. Three independent load-bearing elements
(proposition, free-lunch scalar, Fig 1b) each fail for a different reason, and the falsified Fig 1a
prediction shows the pre-registration was not checked against data the team could have measured in
an afternoon. *Answerable part:* the "restoration also picks one instant, so deblur-then-detect does
not reduce TSB" argument is genuinely good and no restoration paper contains it; keep it. *Not
answerable:* the proposition. Delete it or relegate it to a remark.

---

### Team 02 — *No State at t: Exposure-Occupancy Measures*

> The paper's central and genuinely novel claim is that label ill-posedness is governed not by blur
> magnitude but by **intra-exposure acceleration**, formalised as
> `ν = ‖v(t0+T) − v(t0)‖·T / diag(box)`. It is a good idea. It is also, on any benchmark that exists,
> approximately zero.
>
> Do the arithmetic the paper does not do. The headline prediction is `D > 0.5` at `ν = 1`. Take
> FE240hz's DAVIS346 at 346×260 with a 60-px-diagonal box and a generous 10 ms exposure. `ν = 1`
> requires the object's velocity to change by **6000 px/s within 10 ms**, i.e. an image-plane
> acceleration of **6×10⁵ px/s²** — about 1700 image-widths per second squared. Even the weaker
> claim, "≈25% of FE108's fast-motion frames have ν > 0.3," requires 1.8×10⁵ px/s² on a quarter of
> frames. On DSEC, where the verified daytime exposure is 1478 µs, the same `ν = 1` needs
> **2.7×10⁷ px/s²**. These are not fast-motion numbers. They are collision numbers. The regime in
> which the paper's entire thesis has teeth is a regime the paper must construct, and the paper's
> own risk section concedes this in the mildest possible language ("the convention spread is small
> on real data").
>
> The paper's escape hatch — simulation, where `β` can be held fixed while `ν` is swept — is exactly
> the escape hatch that converts the contribution into an artifact of the generator. You are
> imposing an annotation operator `A` on synthetic data, then measuring that different `A`s disagree.
> They disagree by construction. `A_mid ≠ A_mean` under non-uniform motion is a fact about the
> definitions, provable on a napkin, and Prediction 1 ("at ν=0 all conventions coincide exactly") is
> a *theorem*, not a measurement. Two of the five pre-registered predictions are algebra.
>
> The one prediction that would indict the field — "the convention moves the score more than the
> method does," a 10–20 point RSR swing against a 3–8 point spread between five published trackers
> — cannot be produced without sub-exposure GT on a real benchmark. That means FE108, whose host is
> reported offline, or EVIMO2, whose 200 Hz mocap has a **5 ms** sampling interval against exposures
> the paper itself wants to be 1–16 ms. You cannot resolve intra-exposure acceleration with a GT
> sampler whose period is comparable to the exposure.
>
> And the conformal half is scored the wrong way round. Per the ECCV 2024 conformal-detection
> literature, coverage is purchasable and is not the contribution; the frontier is. The paper does
> say it will report the CMC–SetEff frontier — good — but the honest baseline is not "KL-loss
> Gaussian head" as a straw man, it is an **anisotropic** Gaussian head oriented along the motion
> direction, which is precisely the shape the occupancy support has. At `ν ≈ 0` (the real-world
> case) the support *is* a line segment along the motion, and an oriented Gaussian covers it at
> comparable efficiency. The paper's own A2 ablation predicts "near-zero gap at ν = 0" and calls it
> "a predicted null — good science." It is good science and it is also the whole real world.

**FATAL as posed.** The kill criterion the team pre-registered (median CS < 0.08 and Kendall τ > 0.85
by day 7) is the right instrument and I expect it to fire. *Answerable:* the time-reversal-pair
identifiability argument is correct and cheap. But it is a proof about a family that requires the
reversal to occur within one exposure — again, an impact — and no downstream consumer needs it.
"You proved a theorem that does no work in the paper" applies here as squarely as anywhere in the set.

---

### Team 03 — *Temporal Support Fields*

> The paper stands entirely on one experimental construction: matched pairs (A) constant velocity and
> (B) dwell-then-dash, "matched on every covariate the field currently uses" — same blur extent, same
> event count, same mean speed — differing only in support overlap `O*`. If the pairs are matched,
> the resulting error cliff indicts the formulation. If they are not matched, the cliff is an
> ordinary covariate effect.
>
> **They are not matched on any real sensor, and the paper asserts that they are.** Verbatim: "Event
> counts are matched by construction (same d, same contrast, same threshold ⇒ same number of
> threshold crossings)." That is true only for an ideal event pixel with infinite bandwidth and zero
> refractory period. In (B) the object covers the same displacement in 0.2T, i.e. at **5× the
> instantaneous speed**, and both of the sensor's established rate-limiting mechanisms bite exactly
> there: the photoreceptor low-pass attenuates the faster transient, and the refractory dead-time
> discards crossings at the higher rate — Gallego et al.'s survey states outright that a larger
> refractory period yields fewer events from fast-moving objects, and Delbrück et al. give the rate
> law. Team 06 in this very round measured a 0.26 → 0.37 shift in the *effective* threshold from
> motion alone at a 300 µs refractory. So the dwell-then-dash pair produces **fewer** events than the
> constant-velocity pair on any sensor model that is not the authors' own idealisation. The authors
> then face a dilemma with no good horn: run the simulator with refractory off, and the covariate
> match holds but the simulator's event model is precisely the thing under measurement; run it on,
> and the headline claim "event count within ±5%" fails and the cliff is confounded with event count.
> This is the canonical objection — *it only exists in your simulator, and your simulator's model is
> the thing you claim to be measuring* — and it is not answered anywhere in the document.
>
> Second: half the supervision is advertised as free real ground truth — "the event-branch support
> has exact ground truth on real data, it is the inter-event interval, present in the raw stream."
> Read that again. The network is given the event stream as input and supervised to predict the
> inter-event intervals of that same event stream. It is being taught to reproduce a deterministic
> function of its own input. That is not free supervision; it is an identity map with a loss on it,
> and it will train to near-zero error while teaching the network nothing about anything.
>
> Third: `Real-1` is BS-ERGB/HS-ERGB, described here as "medium (host availability)." Team 06 in this
> round reports, from an actual check, that **both Time Lens and Time Lens++ download pages now
> render navigation only, with no links or forms, and no mirror exists.** The one real dataset with
> pixel-aligned beam-splitter data and a high-speed strand — the only source of *measured* occupancy
> windows in the plan — is gone.

**SURVIVABLE WITH** exactly two things: (i) the matched-pair construction re-verified with refractory
period and photoreceptor bandwidth **on**, with the residual event-count mismatch reported as a
number and the cliff shown to survive after regressing it out; and (ii) a real dataset that is not
BS-ERGB. *Answerable:* "isn't this uncertainty estimation?" is genuinely answered by ablation (viii)
— a scalar per-pixel reliability has no time axis and cannot compute an overlap — and that answer
should be in the main paper, as the team already plans. The sub-probability mass channel is a real
representational addition.

---

### Team 04 — *When Is Your Prediction?*

> The paper's centrepiece is Figure 2, the collapse plot: pool ~2000 condition cells over four
> independent variables, plot observed error `r_q` against predicted temporal displacement
> `(τ̂ − t_q)·v`, and predict a single line of slope 1 with R² > 0.9. The authors call a collapse
> across four variables "the strongest available evidence that one latent variable generates the
> error."
>
> It is not evidence at all. `τ̂` is **defined** as `argmin_t d(ŷ, y*(t))`. For an object on a smooth
> path, the time whose ground-truth position is closest to the prediction differs from `t_q` by
> approximately the along-track component of the error divided by the speed. So
> `(τ̂ − t_q)·v ≈ e_∥`, the along-track error, and `r_q` is the total error — which, in a regime where
> the along-track component dominates, *is* `e_∥`. Figure 2 plots `e_∥` against `‖e‖` and discovers
> that they lie on a line of slope 1. **The collapse is a definition, not a law, and R² > 0.9 is a
> statement about how much of the error is along-track — which is Team 08's decomposition, measured
> with more steps and reported as a discovery.** Any reviewer who writes out the two definitions on
> the same line kills the paper's centrepiece in one sentence, and the paper has no second
> centrepiece.
>
> The kill-shot statistic, `σ_τ` (within-frame temporal dispersion, "no scalar clock correction
> exists"), inherits the problem and adds a worse one. Since `τ̂ − t_q ≈ e_∥/v`, two objects with the
> same spatial error and different speeds get different `τ̂` — automatically. `σ_τ > 0` is guaranteed
> by heterogeneous speeds plus ordinary spatial noise, with no timing phenomenon required. Worse, the
> paper's own numbers make the artifact **larger than the signal**: §4.3 pre-registers
> `σ_τ ≥ 0.15·T_exp ≥ 1.5 ms`, while §F1's own assumption of `σ_x ≈ 3 px` detector spatial error at
> `v = 1000 px/s = 1 px/ms` implies a per-object `τ̂` noise of **3 ms**. The pre-registered effect is
> half the noise floor implied by the paper's own error model. There is no noise null anywhere in the
> plan — no prediction of what `σ_τ` should be under i.i.d. isotropic spatial error at the observed
> speed distribution — so the paper cannot distinguish its phenomenon from its own residuals.
>
> Ablation 8.3.5 (frame-only / event-only / fused) is correctly identified by the authors as "the
> single most important control in the paper," and my prediction is that it fails: frame-only will
> show `σ_τ > 0` too, because spatial error divided by heterogeneous speed is not a fusion effect.

**FATAL** as currently framed. The diagnosis genuinely is the paper, and the diagnosis is circular.
*Answerable:* Figure 4 (content control — hold clock, exposure, speed and event rate fixed, sweep
texture asymmetry, watch τ̂ move) is the **one experiment here that is not definitional**, because it
varies nothing that enters the τ̂ definition. If the paper were rebuilt around Figure 4 alone, with a
noise null for σ_τ and the collapse plot deleted, there is a real, small paper. As written, the
strongest figure is buried behind two tautologies.

---

### Team 05 — *No Offset Can Fix a Width*

> Theorem T1 states that a temporal shift is a unit-modulus, linear-phase multiplier and therefore
> cannot correct a modulus mismatch with zeros. This is correct, it is one line, and it forbids
> nothing that anyone does. **No one in the event–frame literature believes that shifting a blurred
> frame in time makes it equal to a sharp one.** The theorem's content, stated plainly, is that
> deblurring is not translation — which is why deblurring exists. Raskar's coded-exposure argument
> (2006) is the acknowledged ancestor and the authors concede it; what they do not concede is that
> the addition — "and there is a second sensor that sees the nulled band" — is the standard
> motivation sentence of every event-guided deblurring paper since EDI in 2019.
>
> The live claim is T2/OBD: the best-fit offset is not a rig constant but drifts with blur extent,
> so "calibrating faster makes your calibration worse." That is a real and checkable claim. It is
> also a claim about the **event–frame calibration literature (RA-L: EF-Calib, eKalibr)**, not about
> CVPR perception, and it needs to be measured on a rig where somebody actually estimates an offset.
> On DSEC, the brief's verified facts say **events and frames share one clock with no calibration
> step** — in `interlaken_00_c` the first event lands 689 µs after the first exposure opened and 781
> µs before it closed. There is no offset there to drift. The paper's own table frames DSEC's
> `t_offset` as the field "reconciling the modalities with one number"; that is a file-format origin,
> not a calibration, and stating otherwise in a CVPR paper is a factual error a reviewer from the
> event community will catch immediately.
>
> Then the magnitude. The paper's Prediction 1 sets the onset at `b = vT ≥ 2 px` and states
> explicitly that "below b ≈ 1 px nothing happens and the scalar-offset formulation is *correct*."
> Verified daytime DSEC exposure is ~1.5 ms. For a typical driving-scene image speed of 200–400 px/s
> that gives `b = 0.3–0.6 px`, and Prediction 2 puts the mismatch floor there at **below 10⁻³ of
> signal energy**. The regime where the theory bites is DSEC at night — where the verified exposure
> is pinned at exactly 14996 µs on six sequences, which is auto-exposure hitting a rail in scenes
> dark enough to be slow. The paper's honest Death 2 says this. My review says it louder: **the
> theory is guaranteed true and, on the only ungated dataset in the plan, guaranteed to be worth one
> part in a thousand.**
>
> The downstream deliverable — "existing method, unchanged weights, alignment operator swapped,
> stratified by b" — is a per-pixel preprocessing mask. That is the honest description, and it is a
> workshop-scale deliverable with an impossibility bound glued to the front.

**SURVIVABLE WITH** a hard reframing: drop the CVPR perception framing entirely and submit the
calibration result where a scalar `t_d` is actually estimated and where a demonstration that it
drifts with the calibration motion's speed is a genuine finding. As a CVPR submission, the theorem
is a triviality and the effect is 10⁻³. *Answerable:* Ablation 1 (global shutter, τ=0, noiseless,
δ*=0, ideal thresholding — does OBD survive?) is exactly the right first experiment and it is
scheduled first. That is the best experimental hygiene in the round. It just cannot make a 0.6 px
effect matter.

---

### Team 06 — *Frames Are Not Samples: The Exposure Gap*

> This is the most carefully verified document in the round, and it verifies a change of variables
> against itself.
>
> The headline is that the residual `R = c·ΔE − Δlog B` is predicted by a parameter-free,
> event-only quantity `P = [c·E − LME(cE)]_{k+1} − [·]_k`, with slope 0.955 and R² 0.779 on an ideal
> sensor. But in an ideal-sensor simulation, `log B_k = L(t_k) + J_k` holds **exactly** — the authors
> derive it themselves, with no approximation — and `P` is the discrete estimate of `ΔJ` computed
> from the same simulated event stream that generated `B` under the same forward model. Therefore
> `R = P` identically up to event quantisation, and the reported R² of 0.779 is not a discovery; **it
> is the ±c/2 quantisation noise floor, and the authors say so in the same table ("remainder is ±c/2
> event quantisation").** A slope of 0.955 with no fitted physics is what algebra predicts, not what
> an experiment finds. The "noise null returns R² = 0.0015" is a null against a *random regressor*,
> which is the wrong null: the informative null is "does `P` predict `R` better than any smooth
> function of `|ΔE|` and blur extent does," and that is not run.
>
> On real data the regression is circular. Both `R` and `P` are functions of the per-pixel contrast
> threshold `c`, which is unknown — and the paper's own P7 is the finding that **the standard
> estimator of `c` is destroyed by the very effect being measured.** So on DSEC you must either
> assume a `c` (and the "parameter-free" claim dies, because the slope becomes a function of the
> assumed `c`) or fit `c` jointly (and the slope-1 result becomes a fit). There is no third option
> and the plan does not name one.
>
> Then the double bind that decides the paper. The authors state, correctly and to their credit, that
> **EVDI (CVPR 2022) Eq. (19)–(20) already implements the exposure-correct two-frame loss.** Their
> Stage-2 control asks whether EVDI shows less motion-conditioned contrast bias than REFID and EFNet.
> Both branches are bad. If EVDI *does* separate, the paper's conclusion is "use the loss CVPR 2022
> already published," and the contribution is a measurement of how much three other methods lose by
> not using it — a benchmarking note. If EVDI does *not* separate, the causal story is falsified and
> the authors have committed, honourably, to saying so. There is no branch on which this becomes a
> CVPR paper about a new idea.
>
> And P7, the strongest single result, is: *if you calibrate a contrast threshold using motion-blurred
> frames, you get the wrong threshold, and the fix is one line.* That is a real, useful, correct
> finding about a 2019 robotics-conference calibration recipe. It is a **bug report**, and the field
> it corrects is not this venue's.

**SURVIVABLE WITH** a change of product: not "the exposure gap exists" (algebra) and not "the fix is
LME" (published), but **P6 — that the bias is not absorbable by capacity across a support shift**
(learned constant removes 0.0%, learned linear model 51%, closed form 91.2%), reproduced at network
scale on real data with MCB as the readout. That single generalisation result is the only thing here
a reviewer cannot derive on a napkin or find in EVDI. Everything else is diagnosis. *Fully answerable
attack:* "this is EDI" — no, EDI's `J` is theirs and they say so; the honesty is exemplary and should
be kept. *Unanswerable attack:* "this is a workshop paper with a closed form glued to the front" —
that is very close to true, and their own 6.5/10 novelty self-score is the most accurate number in
the round.

---

### Team 07 — *Chronofields*

> The reformulation is elegant: invert `time → state` into `state → time`, let events enter as exact
> observations and frames as interval-censored ones. The censoring identification is correct and, as
> far as the searches go, unclaimed.
>
> Now compute what the frame's censored observation actually contributes. On DSEC the verified
> exposure is **~1.5 ms** and the observation window `W` in the plan is 100 ms with `B = 128` bins of
> 0.78 ms. The frame's interval-censoring term `L_int = −log Σ_{b: c_b ∈ [a, a+T]} p_b` therefore
> sums over **two bins**. The paper's entire reformulation of the frame — from a lying point stamp
> to an honest interval — is, numerically, the difference between a delta and a two-bin box in a
> 128-bin distribution. It is the midpoint stamp with a 1.5% smear. On the night sequences it is
> nineteen bins out of 128, and those sequences are the dark, slow ones.
>
> So the paper answers the assigned seed only in the sense that it writes down the right type. The
> seed's *phenomenon* — that the difference in temporal support matters under fast motion — is
> quantitatively absent from the frame branch, and the paper's own Death 4 admits it: "the frame
> branch contributes nothing measurable, which would gut the temporal-support seed and leave an
> events-only paper." Ablation A7 is the test, and I predict it comes back flat outside the
> sub-contrast-threshold refuge, which is a small pixel population.
>
> The headline number is computed outside its own validity. `Δt ≈ a·T²/(24·v̄)` is quoted as
> "8.3 ms, 42% of the exposure" at `T = 20 ms`, `a = −2 px/ms²`, `v̄ = 4 px/ms`. `T = 20 ms` exceeds
> DSEC's verified maximum exposure of 14996 µs; `a = 2 px/ms² = 2×10⁶ px/s²` is, again, an impact.
> And the expression **diverges as v̄ → 0**, which is not a physical effect but the signature of an
> expansion breaking down — as `v̄ → 0` there is no blur, the argmin is flat, and the effective
> timestamp is undefined. The paper notes the identifiability issue but still leads with the number
> from the invalid corner.
>
> Finally the objection the authors themselves name as live and unpre-emptable: reconstruct to
> 1000 fps with Time Lens, then run a detector. They pre-register a falsification criterion (within
> 15% P95 CTE = dead), which is admirable, and then plan to run that head-to-head on **BS-ERGB**,
> which Team 06 verified is no longer downloadable.

**FATAL for the assigned domain.** The idea is real; it is an events-only idea wearing a frame branch
that contributes 1.5% of a window. *Answerable:* the C1 anchor (predict next contrast-crossing time
from real events, supervised by held-out real events) is a genuinely clean, simulator-free, label-free
experiment — and it is also next-event-time prediction, which is folklore, has no consumer, and needs
no frame at all.

---

### Team 08 — *Right Place, Wrong Time*

> The decomposition is imported. The authors concede this in the paper — along-track/cross-track
> error divided by speed to recover latency is standard in air-traffic surveillance, and they cite
> arXiv 2008.06352 for it. So the first review sentence writes itself: *"this is along-track error,
> plus sAP for event cameras, applied to other people's checkpoints."* That sentence is half right,
> the authors know it is half right, and it caps the paper's ceiling. This will not be a
> STRONG ACCEPT at any venue.
>
> The headline deliverable is the ranking flip (P6), and **the flip is inside the noise.** The
> authors' own primary flip candidates are RVT-B vs S5-ViT-B on Gen1 at a **published gap of ≈0.5
> mAP**, and RVT-B vs RVT-S at 1–2 mAP. A 0.5 mAP gap on Gen1 is not separated by a bootstrap over
> the test set; a flip between two methods whose difference is smaller than the resampling interval
> of either is a coin landing. The paper pre-registers `|ΔAP| < 1.5` and `|ΔAP^⟂| > 2.5` as the flip
> signature, which is a sensible design, but it does not commit to reporting paired bootstrap CIs on
> the *ordering*, and without that the flip is unreportable. I would demand, in review, a paired
> bootstrap over sequences with the ordering probability stated, and I expect it to come back near
> 0.5.
>
> The estimator has an error-in-variables problem the plan never names. `δ̂ = e_∥ / ‖v*‖`, and `‖v*‖`
> is finite-differenced from **4 Hz labels on Gen1** and 10 Hz on 1 Mpx. A noisy denominator produces
> classical regression dilution: `τ̂` is attenuated toward zero and its variance inflated, and the
> attenuation is *speed-dependent*, which is the exact axis the paper's Panel A regresses on. The
> filter `‖v*‖·τ_max > 2 px` limits but does not remove it. The two-channel consistency test (P4,
> translation vs scale) is a good idea and is the right partial answer, but the paper needs a
> Deming/total-least-squares treatment or a simulation-calibrated attenuation factor, and it has
> neither.
>
> The pre-registered architecture prediction (C3) — τ̂ ∈ [−35, −10] ms for RVT — is weaker than it
> looks. The band is **25 ms wide and centred on the only physically sensible value**, and the brief's
> own verification is explicit that "whether the trained network weights the ten bins uniformly is
> unmeasured, so 25 ms is a reference point, not a prediction of network behaviour." A prediction
> that spans from "half the window" to "one fifth of the window" and is confirmed by any negative
> number in that range is not a strong pre-registration; it is a plausible interval. Narrow it, or
> stop calling it a prediction.
>
> And Death 3 is sharper than the authors allow. If `τ̂` is dominated by the **label** pipeline — the
> 1 Mpx boxes come from a commercial detector on a 60 fps side-mounted GoPro, warped by homography —
> then every method on that dataset shares one τ̂ and the paper has measured a dataset. The authors'
> answer (a shared τ̂ is itself publishable; decompose the variance across (dataset, method)) is a
> good answer, and C3 discriminates. I accept it.

**SURVIVABLE WITH** three things, all cheap: (i) paired bootstrap CIs on the *ordering*, not on the
scores, with the flip probability reported and the honest possibility that it is 0.5; (ii) an
errors-in-variables correction for the velocity denominator, calibrated on TSB-Sim where `v*` is
exact; (iii) narrowing C3 or demoting it from "prediction" to "reference point."

The reason this survives where nine others do not: **E0 cannot fail.** It needs a 4.7 MB label file,
zero GPU, and two days, and it answers a question with only two possible outcomes, both publishable.
Either the released high-rate ground truth of the two flagship low-latency event benchmarks is
recoverable from its own interpolation prior to >0.9 median IoU — in which case a large fraction of
every inter-frame number in that literature is agreement with a constant-velocity assumption — or it
is not, and the benchmarks are cleaner than their own descriptions suggest, which is also worth
knowing. Ev-3DOD (CVPR 2025 Highlight) already publishes the construction in its own words and
already publishes a 53.6 → 33.3 mAP online-vs-offline gap; Team 08's contribution is to put a unit
(milliseconds) and a control (anisotropy R) on a number the field is currently reporting in mAP with
no name. That is a modest contribution that is **certain to exist**, which is exactly what the brief
says to value.

---

### Team 09 — *Change-Time: Per-Pixel Clocks*

> Pillar 1's central formal claim is Property (2): the representation `τ(x,t) = C·N(x,t)` is
> **exactly** invariant to any strictly increasing reparameterisation of time, bit for bit. This is
> true. It is also trivial, and the triviality is the review: **counting events is invariant to
> relabelling their timestamps because it does not read the timestamps.** A representation that
> discards a quantity is invariant to that quantity. The paper has proved that throwing away the
> clock makes you independent of the clock.
>
> Whether the invariance is *useful* is decided in the paper's own Secondary Risks, and the authors
> decide against themselves: "Flow in px/s, time-to-collision, and physical velocity are genuinely
> rate-valued. Already designed for: `v = (dx/dτ)·(dτ/dt)` keeps an invariant backbone and reinjects
> the counted rate at the head via FiLM." So the timestamp is deleted at the input and put back at
> the output, for every task that anyone cares about. The invariance is a gauge the authors fix
> themselves wherever it would have consequences. RIG = 0 is described in the paper as "a unit test,
> not a result," and that is the correct description.
>
> **Pillar 2 is refuted by the round's own verified measurements, and this is the part I would put in
> the review verbatim.** The paper defines the frame's per-pixel temporal support width as
> `W(x) = C·N_exp(x)`, the count of events at pixel x during the exposure, and stakes a metric on it
> (SWC: correlation of `W(x)` with true blur severity, "target r > 0.9"). The brief's verified
> measurement over 536 frames of `interlaken_00_c` is that inside one 1478 µs daytime exposure there
> are a median of 20,616 events touching **6% of pixels**, at **≈1.10 threshold crossings per firing
> pixel.** So `W(x) = 0` on 94% of pixels, and on the remaining 6% `N_exp` takes values in {1, 2}.
> The advertised "measured, spatially varying, per-pixel support field" is, on real daytime data, a
> **sparse binary mask**, and no quantity that is zero on 94% of pixels and one on most of the rest
> can correlate with a continuous blur severity at r > 0.9. The brief also states explicitly that
> 1.10 crossings per firing pixel "is not a displacement measurement, and no team may claim
> displacement from it" — which forecloses the fallback of reinterpreting `W` as intra-exposure
> motion. Pillar 2 survives only on the night sequences (10.1× wider windows, so `N_exp` of order 11),
> which are the slow, dark ones, and on BS-ERGB, which Team 06 verified is no longer downloadable.
>
> Pillar 1's decisive experiment, P3, is a prediction about **one competitor's clamp
> hyperparameters** (ASTW's Δt_min = 10 ms, Δt_max = 250 ms ⇒ elbow at ρ ≈ 25). Predicting an
> opponent's failure point from their own hyperparameter table is genuinely good practice. It is also
> a two-degree-of-freedom target that a reviewer will simply ask you to re-tune, and the authors
> concede: "if any clamp setting flattens the ρ curve, the hyperparameter objection stands."
>
> Finally, the authors themselves list two unnamed near-misses (SITS 2019 is already monotone-invariant
> via ranks; Spiking Patches already builds an unnamed product order) and one live scooping threat
> from the same lab that owns the datasets (Neural Events, June 2026, change-triggered emission).
> "It was already reached and not named" is not a defence; it is a reviewer's sentence.

**FATAL for pillar 2** on the verified data; **SURVIVABLE WITH** a total reframe of pillar 1 as the
authors' own better idea — *disentangling what is speed-dependent from what is not*, showing `dx/dτ`
transfers to unseen speeds where an end-to-end `t`-based model does not. That is a real result and
it does not need the invariance theorem to be interesting. But it is then a representation paper with
no cross-modal claim, which does not answer the seed.

---

### Team 10 — *Fusion Is Ill-Typed*

> Proposition 1 says a probability measure and a zero-mass signed measure are different objects, and
> that no shift, scale or warp maps one to the other. True, two lines, and it **proves far too much.**
> By this rule, every RGB-D network that concatenates a depth channel with an intensity channel is a
> type error; every model that mixes a log-scaled feature with a linear one is a type error; CLIP is
> a type error; a ResNet's first layer is a type error the moment the input channels have different
> units. Nobody in deep learning claims a fused feature is an unbiased estimator of a scene
> observable — the claim is that a learned map of two inputs predicts a target. A discipline that
> condemns every method that works, including the ones the paper's own diagnostics rank as good,
> condemns nothing. The authors half-see this (Death 3, "the type system is bookkeeping") and answer
> that triviality is a feature "only if the field visibly violates it." The field visibly violates it
> and the field visibly works. That is the problem.
>
> Both diagnostics are broken, in different ways, and each in one sentence.
>
> **EU(s) is modality dropout.** Zeroing the event branch at inference on a model whose
> normalisation statistics, residual scales and feature magnitudes were co-adapted with a live event
> branch puts the network far off its training distribution. The resulting drop measures *fragility
> to input ablation*, not *information contributed*. This is well understood in the attribution
> literature and any reviewer who has read it writes one line. Worse for the paper's thesis: an
> off-distribution ablation gets **more** damaging as inputs get more unusual, so `EU` measured this
> way could rise with speed for reasons that have nothing to do with the event branch's utility. The
> headline curve is not interpretable in either direction.
>
> **OSAM is a geometric identity.** The paper predicts `OSAM(s) ≈ 1 − r/(r+s)` where `r` is the
> block's mixing radius and `s` is displacement during the exposure. That expression is what you get
> for *any* fixed-radius aggregation against a tube that grows with `s` — it is a statement about the
> tube definition, not about the model. Confirming it is confirming arithmetic. And the "causal tube"
> is built from GT flow "dilated by the calibration/flow error budget," so the one free parameter in
> the diagnostic is the dilation, and it sets the answer.
>
> The support-blind pair (time reversal within one bin ⇒ identical frame, identical polarity-sum
> voxel grid, different correct answer) is the paper's only unfalsifiable-by-construction asset, and
> it is shared: **Team 02 in this same round constructs the identical family independently.** Two
> teams converging on it is evidence it is the obvious move from the physics, not evidence it is
> novel. It also requires the reversal to be contained inside one temporal bin — 5 ms for RVT's
> `nbins=10` over 50 ms — which is again an impact-scale event, and it fails against any
> representation with enough bins, which is a hyperparameter.
>
> Operationally: six repos, six Docker images, Baidu-hosted weights for two of them, ~140 GPU-h of
> fine-tuning from released checkpoints. The paper's value is a claim about other people's models and
> the plan's critical path is other people's dependency stacks.

**FATAL.** The theory proves too much, and both empirical instruments are invalid. *Answerable:*
Panel C — that DSEC's auto-exposure varies frame to frame and no published model reads `T`, so
per-frame error should correlate with `T·‖v̄‖` after controlling for `‖v̄‖` — is honest, cheap, uses a
verified dataset field, and is the one thing here I would want to see. It is an afternoon of
inference and it is a paragraph, not a paper.

---

## Which survives its own worst review

Ranked by survivability — how much of the idea is standing after the review above is published.

**1. Team 08.** Worst review: *"imported decomposition; the flip is inside the bootstrap."* Both true;
neither fatal. Survivability comes from structure, not from cleverness: the load-bearing experiment
(E0) needs a 4.7 MB label file, no GPU, no simulator, no gated dataset and no cooperation from
anyone, and it has two outcomes that are both worth reporting. Every other idea in this round has at
least one load-bearing element that can be removed by a fact outside the team's control — a dead
host, an unmet onset condition, an acceleration that does not occur, a simulator artifact. Team 08
has none. It also proposes no method, which retires "you invented a metric and won on it" — the
single most-used attack against the other nine — at the cost of the paper's ceiling.

**2. Team 06.** Worst review: *"you verified a change of variables; the fix is one line CVPR 2022
already published."* Severe, but the work completes with certainty, every headline number is already
computed rather than guessed, and the P6 generalisation-across-support result is the one claim a
reviewer cannot derive on a napkin. The document's honesty (naming EVDI as the positive control that
could falsify the paper, and scheduling it early) is the best scientific behaviour in the round. It
survives as a diagnosis paper; it does not survive as a novelty paper.

**3. Team 03.** Worst review: *"your matched pair is not matched on a real sensor."* This is repairable
— re-run with refractory and bandwidth on, report the residual mismatch, regress it out — and the
fallback axis (support mass / staleness / abstention) is genuinely independent of the overlap axis.
The representational addition (sub-probability mass, so "no valid observation here" is a
representable output) is real and is the only place in the round where an *inexpressibility* claim is
both true and consequential for a downstream user. Loses two places for the BS-ERGB dependency and
for a supervision term that is an identity map.

**4. Team 05.** Worst review: *"the theorem is a triviality and the effect is one part in a thousand."*
The theory cannot fail, which is worth something; the ablation discipline (kill the mundane
explanations first, in week one, at almost no cost) is the best in the round. It ranks here and not
higher because the honest destination is a calibration venue, and because a CVPR reviewer's first
sight of the figures is blur curves.

**5. Team 09.** Worst review: *"the invariance is trivial and you destroy it at the head; pillar 2 is
zero on 94% of pixels."* Pillar 2 is dead on the verified data. Pillar 1 has a real, one-day,
no-download decisive experiment and a reframing (speed-invariant vs speed-dependent factorisation)
that the authors have already identified as "arguably the better paper." Survivable only by
abandoning the assigned seed. High scooping risk on top.

**6. Team 01.** Worst review: *"the proposition does no work, the fix is one scalar, and Fig 1a is
already false."* The best-written document in the round and the one whose load-bearing elements fail
most independently of each other. What survives is the deblur-then-detect argument, which is a good
section, not a paper.

**7. Team 04.** Worst review: *"the collapse plot is a definition and σ_τ is below your own noise
floor."* One genuinely non-circular experiment (Figure 4, content control) buried behind two
tautologies. Rebuildable, but only by discarding the two figures the authors call the centrepiece and
the kill shot.

**8. Team 10.** Worst review: *"the type system condemns everything that works, and both diagnostics
are invalid."* Little survives except Panel C, which is a paragraph.

**9. Team 02.** Worst review: *"you need 10⁵–10⁶ px/s² and no benchmark contains it."* The idea is
correct and the world does not instantiate it. Its own kill criterion is well designed and I expect it
to fire in week one, which is the best thing I can say.

**10. Team 07.** Worst review: *"the frame contributes a 1.5 ms bracket in a 100 ms window."* The
reformulation is the most elegant in the round and it does not answer the seed it was assigned. As an
events-only paper it is a different submission with a different domain.

---

## My winner and its fatal flaw

**Winner: Team 08 — *Right Place, Wrong Time*.** Not because it is the best idea. It is, on novelty,
the weakest of the ten and the team scores itself accordingly (7/10, honestly 6). It wins because it
is the only one of the ten that is standing after I finish writing about it, and because it is the
only one whose central figure cannot be taken away from it by a dead download link, an
acceleration that does not occur in nature, a simulator whose event model is the object of study, or
an exposure that turns out to be 1.5 ms wide.

The brief's own criterion decides this: *"an idea that is beautiful and unfinishable by November 2026
on 9 GB is worth less than one that is merely good and certain to produce a real figure."* Nine ideas
here are beautiful. One is certain.

**Its fatal flaw — the one the team has not named.** Not the imported algebra, which they concede;
not the ranking flip, which they have hedged; not Death 3, which they answer well. It is this:
**`δ̂ = e_∥/‖v*‖` divides by a quantity estimated by finite-differencing box centres from 4 Hz labels
on Gen1 and 10 Hz on 1 Mpx.** A noisy denominator produces classical regression dilution — `τ̂` is
attenuated toward zero, its variance inflated, and, fatally, the attenuation is itself a function of
speed, which is the exact axis Panel A regresses on. The paper's headline object is a slope, and the
slope is measured through a noisy divisor with no errors-in-variables treatment anywhere in the plan.
The mitigation on offer (`‖v*‖·τ_max > 2 px`, retained-fraction reporting) reduces the problem and
truncates the sample in a speed-correlated way, which is a second bias in the same direction. A
reviewer with a statistics background — and there is one on every CVPR panel — will find this in the
supplement and it attacks the headline number directly, not a side claim. The fix is cheap and must
be in the plan from day one: total-least-squares or Deming regression for the slope, and an
attenuation factor calibrated on TSB-Sim where `v*` is exact (their control C4 is already the right
instrument; it just has to be pointed at the denominator instead of only at the injected offset).

**Would I reject all ten?** As submitted, yes — nine on the reviews above and Team 08 at BORDERLINE.
There is no STRONG ACCEPT here and I would not fight for any of them in an AC discussion in their
current form.

**What would have to be true for any of them to work.** Three things, and they are all measurable
before a single model is trained:

1. **The exposure-side effect must be shown to be larger than the event-window effect the authors
   choose themselves.** On the verified numbers it is not: 1.5 ms of exposure against a 50 ms
   self-selected window. Any paper here must open by measuring both supports on the same axis and
   showing which one dominates. If the answer is the window, the honest paper is about the window —
   which is Team 08's paper, and only Team 08's.

2. **The regime must be found before it is theorised.** Four separate ideas require
   intra-exposure displacement, intra-exposure acceleration, or intra-exposure reversal at
   magnitudes that, on the arithmetic above, correspond to impacts rather than to fast motion. The
   joint distribution of (exposure width, image-plane speed, image-plane acceleration) over every
   candidate dataset is a one-day, zero-GPU measurement that decides five of these ten ideas, and
   **not one team ran it.** Run it first. If the regime is empty, the paper is a simulator study, and
   simulator studies of exposure effects are refereed by people who know that the simulator's
   exposure model is the thing being measured.

3. **The real-data plan must not route through a dead host.** FE108/FE240hz is reported offline by
   Team 09 and is the primary real-data source for Teams 01, 02, 04 and 07. BS-ERGB is reported
   unobtainable by Team 06 and is load-bearing for Teams 03 and 07. Between them these two facts
   remove the primary real figure from five of the ten ideas. Verify every download link this week.
   The teams that did this (06, 08, 09) are, not coincidentally, the top three in my ranking, and
   that is not a coincidence about their ideas — it is a coincidence about their character, which is
   what predicts whether a paper exists in November.
