# 12-step protocol ledger

Every negative result in this project, the passes run against it, and where each stopped.
Kept so that "we ran the protocol" is auditable rather than asserted.

| # | negative result | passes | steps taken | outcome |
|---|---|---|---|---|
| 1 | the dispersion converts to 0.007-0.066 px, below the label noise (E14) | 3 | 3 -> 10 -> 11 | stands; the pixel conversion is reported in the paper |
| 2 | mains flicker may produce the night dispersion | 5 | 2 -> 5 -> 6 -> 10 | **not resolved.** The step-10 route (E20, spatial gradient) was itself retracted on 2026-09-05, see row 6; the scalar dispersion stands as a bounded statement |
| 3 | E21 returned zero matches | 3 | 2 -> 5 -> 9 | resolved; Gen1 `track_id` is not persistent, rebuilt by IoU |
| 4 | E21's effective output time is ~0, not -25 ms | 3 | 3 -> 7/8 -> 11 | resolved; reported as a negative control the objective enforces |
| 5 | E23's acceleration term appears on the cross-track error too | 0 | none yet | recorded 2026-09-04, no pass run |

## 1 — pixel scale

- **Pass 1, step 3.** The product of medians is not the median of products; recomputed
  per object. Median 0.0058 px, correlation between deviation and speed **-0.125**, so fast
  objects deviate *less*. Failed.
- **Pass 2, step 10.** Dimension 1 -> 2: residual anisotropy `R = 1.939`, CI excluding 1.
  Positive but confounded by local-fit error, and closed on magnitude: the temporal term
  can account for 0.05 % of the excess variance.
- **Pass 3, step 11.** Cross-link the event-derived deviation against the label residual.
  `r = +0.0047`. **Retracted as a negative:** the power calculation showed the effect would
  produce `r = 0.0155` against a 2-SE threshold of 0.0254, so the test could not have
  detected it. Recorded as uninformative, not as a refutation.
- **Steps 7-9 were not run explicitly.** E20 was recorded as supplying them, on the
  argument that the gradient measurement avoids converting a temporal quantity through
  velocity into a spatial noise comparison. **E20 was retracted on 2026-09-05 (row 6), so
  those steps are again unrun.** Row 1 itself is unaffected: the pixel conversion of E14 is
  a multiplication of two independently measured quantities and does not depend on E20.

## 2 — mains flicker

- **E11, step 5.** Exclude individually phase-locked pixels. Excess 183.6 -> 180.6 us
  against 182.9 for a matched random exclusion. Insufficient: a weakly modulated majority
  remains (E10 median Rayleigh Z 2.935 against a null of 0.693).
- **E12, step 9.** Integer-period windows. **Mathematically wrong and retracted:** an
  integer window cancels the zeroth moment, not the first. Verified numerically.
- **E18, step 9 again.** Subtract each box's own contribution. **Repeated the same error**
  by applying an integer-period formula to a 1.4996-period window.
- **E19, step 6.** Stratify by each box's modulation. Dose-response 93.1 -> 208.0 us across
  quartiles, and no unmodulated stratum exists (p10 modulation 0.355 against a 0.125 noise
  floor). The scalar dispersion is **abandoned**.
- **E20, step 10.** Change the dimension: the spatial gradient of evidence time inside a
  box, which flicker cannot reach because it is spatially uniform. Alignment with the
  label velocity `cos = +0.152`, **12.4 SE**, against nulls of +0.028 (shuffled velocity)
  and +0.020 (shuffled times). **Retracted 2026-09-05 by E25 and E26 (row 6 below): the
  alignment is ego-motion, not per-object evidence time.** The flicker confound is
  therefore not resolved by this route either, and no route to resolving it stands.

## 3 — E21 zero matches

- **Pass 1, step 2.** The model and detections are fine: at conf 0.1 there are four
  detections and the sample box overlaps its ground truth closely.
- **Pass 2, step 5.** The data, not the code: **Gen1's `track_id` is a per-frame index**,
  145 labels carrying 145 distinct ids, so no velocity can be taken from track continuity.
- **Pass 3, step 9.** Rebuild association by same-class IoU matching between adjacent label
  times; 81.5 % of boxes link at IoU >= 0.3. **Resolved.**

## 4 — the effective output time is not -25 ms

- **Pass 1, step 3.** Mean +25.92 ms against median +0.43 ms is a 60-fold gap, the
  signature of a ratio estimator with a small denominator. Replaced `e_par/|v|` with a
  regression of `e_par` on `|v|` through the origin, whose slope is the same quantity
  without the division. Running.
- **Pass 2, steps 7 and 8.** The evaluation was asymmetric in a way that made it
  uninformative: **RVT is trained with ground truth at the label time on a window ending at
  that time**, so the loss forces the output to align with it. An offset of zero is what
  training enforces, not a finding. The question was wrong.
- **Pass 3, step 11.** The quantity that is not forced by training: the network's evidence
  is centred 24.94 ms before the label (E17) while its output is at the label (E21), so it
  **extrapolates about 25 ms**. Extrapolation is free under constant velocity and costs
  `~a tau^2 / 2` under acceleration — 0.31 px at 1000 px/s^2, the same order as the label
  noise. Stratifying detector error by object acceleration tests this, and nothing in the
  training objective forces its outcome.

## 5 - E23, the cost of extrapolating

Measured 2026-09-04, 4332 matches. `|along-track error|` regressed on label speed, box
side and acceleration gives an acceleration coefficient of **+0.0198 s^2 at 10.0 SE**.
The cross-track control, which no extrapolation can produce, gives **+0.0117 s^2 at
13.4 SE**, and the along-track coefficient is about **64x** the `tau^2/2 = 3.11e-4 s^2`
the extrapolation account predicts at `tau = 24.94 ms`. Acceleration correlates with
label speed at +0.360 and with box side at +0.327, and the median along/cross error
ratio rises 1.42 -> 1.42 -> 1.66 -> 2.59 across acceleration quartiles.

**No pass of the protocol has been run against this.** The paper reports the two
coefficients and states that no extrapolation cost is established; it claims no
refutation of the extrapolation account, because a term this much larger than the
predicted one, present in both directions, is most simply read as object difficulty
rather than as timing, and that reading has not itself been tested. Pass 1 is step 3:
the acceleration is a forward difference of a forward difference of label centres, so
it carries the label noise of E13 squared over a 50 ms base, and the first check is
whether the term survives an acceleration estimated over a wider base.

## Standing rule

Three passes is the floor, not the target. A pass that fails for a reason internal to the
measurement (a wrong formula, an underpowered test, a ratio estimator) does not count as
evidence about the world and the ledger says so.

## 6 — the gradient alignment is ego-motion (2026-09-05)

- **Pass 1, step 2.** The code is not at fault: the same procedure returns 8 to 12.6 SE in
  four sequences and the time-shuffled null returns +0.020 everywhere.
- **Pass 2, step 3.** Is the two-sequence exception sampling noise? No. Cochran Q = 56.01 on
  5 df, I^2 = 91 %, and a uniform effect would have shown 3.8 SE in the sequence that
  measured 0.0. The sequences genuinely differ.
- **Pass 3, steps 5 and 6.** What differs: the alignment is **stronger where objects move
  slower** (r = -0.907 against the fraction above 20 px/s). A motion-driven per-object
  gradient cannot behave that way, which pointed at a scene-level cause.
- **Pass 4, steps 7 and 8.** The evaluation was measuring the wrong thing. Comparing a box's
  gradient against a background annulus showed the background aligning as well or better in
  half the sequences.
- **Pass 5, step 9.** Change the estimator to a **paired** difference: each box minus its own
  surrounding annulus, which cancels ego-motion because it is locally common. Four of six
  sequences go negative; the eroded object core goes negative in five of six.
  **E20 is retracted.**

Five passes, and the result did not survive. The protocol says a favourable route must
exist; it does not say every quantity is the favourable one. What survived this round is
the flicker finding, reproduced in six of six sequences, and the predictor-side
measurements, which never depended on the night arm.

---

## Case 7 — the output-time estimate that disagreed with itself (2026-09-07)

**The negative-looking result.** The signed refit demanded by the checklist audit returned
`tau = +52.7 ms` at 8.1 SE, against E21's `+11.9 ms` at 1.3 SE for the same quantity on
the same checkpoint. A four-fold disagreement between two estimates of one number is worse
than either being null: it says at least one is measuring the estimator.

**Pass 1 — steps 1 to 3 (code, arithmetic, data).**
- Step 1, code: E24 fitted `np.abs(epar)`, not `epar`. Confirmed by reading
  `src/e24_order.py:119` and by the run log carrying both blocks with identical
  magnitude numbers. **Defect found.**
- Step 2, arithmetic: `E|eps + tau v| != E|eps| + tau v`. Verified symbolically; for
  symmetric zero-mean `eps` the derivative at `d = 0` vanishes. **Defect confirmed.**
- Step 3, data: Gen1 `track_id` is a per-frame index; association is rebuilt by IoU.
  Already known from E21 and unchanged. No new defect.

**Pass 2 — steps 4 to 7 (specification, regressors, dimensions).**
- The acceleration regressor was `|dv|/dt`, a magnitude, entered where a signed `a_par` is
  required. `corr(acc, |v|) = +0.36`, and omitted-variable arithmetic reproduces the whole
  `11.9 -> 52.7` gap. **Defect found**, and it is the same class of error as step 1: a
  magnitude standing in for a signed quantity.
- Sign conventions differ between E21 and E24 by a sign. **Defect found.**

**Pass 3 — steps 8 to 12 (change the dimension, change the estimator).**
- Step 9, change what is measured: the residual is a vector and the lag model is linear in
  the velocity *vector*. Projecting onto `u = v/|v|` estimates a direction from the same
  noisy velocity and then regresses on `|v|`, a nonlinear function of it. Replacing the
  projection with a stacked vector regression removes both steps.
- Step 10, find the mechanism that makes the number appear without the effect: a forward
  difference shares the label-centre noise `delta_k` with the residual, covariance
  `+var(delta)/dt`, present at `tau_true = 0`. **This is the largest defect and neither
  external review found it.**
- Step 11, test the test: E29 simulates `tau_true = 0` with E28's measured Gen1 noise. The
  forward estimator returns `-5.64 ms` against a closed-form `-5.63 ms`; backward returns
  `+5.84 ms`; their sum is `+0.20 ms`; zero noise collapses all three to `+0.02 ms`.
- Step 12, the favourable method that must exist: the centered-difference vector estimator
  with a rotated-velocity placebo, clustered errors and a measured attenuation correction.
  It is not a weaker claim than the one withdrawn — it is an identified one, and it comes
  with two controls the withdrawn estimator could not carry.

**Outcome.** Six defects, all mine, none in the data, and the corrected estimator returns
`tau = -2.40 +- 7.18 ms` — a null, but a null with a use: it is 3.81 SE from the influence
centroid, so the hypothesis that the detector's output describes the instant its own
evidence is centred on is excluded, and the evidence-to-output interval is 27.3 ms. The
step-12 promise held in an unexpected form. The favourable method was not a larger lag but
an identified interval, and it arrived with three controls the withdrawn estimator could
not carry: a placebo that selected the specification without seeing tau, an injection test
showing the controls do not absorb a lag, and a saturation sweep bounding the answer at
-20.2 to +11.1 ms across every specification.

A seventh defect surfaced during the write-up and is recorded because it nearly reached
the manuscript: two numbers, `+0.349` for corr(speed, box side) and `81.5 %` for the track
linking rate, were carried over from retracted E21 and attached in prose to E27's sample.
Re-measured on the sample actually reported (E36) they are **+0.139** and **79.0 %**. A
retracted experiment's numbers do not become correct by being plausible.

Consistent with Case 2 and Case 5, and with the standing rule that a bad result is a bug
until three independent checks say otherwise.


---

## Case 8 — the per-box significance that rested on a null the data rejects (2026-09-07)

**The claim under test.** "Between 99.0 % and 100.0 % of labelled boxes are phase-locked to
the 100 Hz mains at p < 1e-3." It appeared in the abstract, the introduction, Sec. 4.3 and
the conclusion.

**Pass 1 — the checker was not tested.** A checklist audit pointed at the paper's own
table: the 137 Hz off-frequency arm has a per-box median of 4.01 against the analytic
0.693, so the text's "the test returns its null" is contradicted by the numbers printed
four lines above it. **Defect confirmed by reading, before any new run.**

**Pass 2 — measure the null instead of assuming it (E38 arm 1).** Sweeping sixteen off
frequencies over all six ceiling sequences: the pooled per-box median is 38.39, an
inflation of 55, and the empirical p < 1e-3 threshold is 7181 rather than 6.91. Against
that threshold the locked fraction is **0.20 %**, not 99.65 %. The p-values are withdrawn.

**Pass 3 — test the new checker too.** Arm 1's own sweep reached to 63 Hz, where a 15 ms
window holds less than one cycle and the statistic measures the burst envelope rather than
an oscillation. So arm 1 cannot be the replacement either.

**Step 12, the favourable method that must exist.** A ratio needs no null. Dividing each
box's `Z` at the line by the median of `Z(f)` over that same box's neighbouring frequencies
removes the burst inflation whatever its size: 1.87 over 16 516 boxes (p10 1.62) against
0.11 for the identical construction at 137 Hz, and **99.63 %** of boxes above the
off-frequency arm's 99th percentile. The headline number barely moved; what it rests on
changed completely.

**And a limit the new statistic exposes.** The pooled median spectrum has one peak, at
96 Hz, 8.5x the 200-300 Hz level. One 14996 us window is transform-limited to 67 Hz, so a
box cannot separate 96 from 100 Hz. The line's *position* comes from the per-pixel arm,
which pools a whole recording and puts it at 100.00 Hz with a ratio of 10841 over the
continuum. The per-pixel arm was never in doubt: there the 137 Hz control returns 0.581
against 0.693, so the analytic null holds exactly where it was verified.

**Outcome.** A claim was weakened, a statistic was replaced, and the paper is stronger for
it: a distribution-free rank statement over the same events, and an explicit statement of
what one exposure window can and cannot resolve. Consistent with [[test-the-checkers]] —
the null had never been tested against the data it was applied to.

---

## Case 9 — the recurrent state handed to the occluded pass (2026-09-07)

**The claim under test.** "The influence-weighted centroid of the newest window is
−24.94 ms, and the profile is close to flat (CV 0.034)." It is the paper's most-quoted
predictor-side number: the interval to the measured output time, that interval in standard
errors, the ratio to the label dispersion, the pixel displacements and the mAP cost are all
functions of it.

**Pass 1 — a disagreement between two of my own runs.** E44 measured the same quantity on
`rvt-t` while sweeping three capacities and returned −23.84 ms, not −24.94 ms. Same
checkpoint, same representation, same bins. A 1.1 ms disagreement between two runs of one
measurement is a defect in one of them, and neither had been shown correct.

**Pass 2 — read both implementations rather than re-run either.** E17 and E34 advance the
recurrence with

    out,_,states = mdl.forward(x, previous_states=states)

and then call the occluded pass with `previous_states=states`, which by then holds the state
the reference pass **returned**. E42 and E44 save `pre[i]` before the step and pass that.
The occluded pass in E17/E34 therefore ran one step out of phase with the pass it is
differenced against, so part of what was attributed to occluding a bin is the mismatch
between two different histories. **Defect confirmed by reading, before any new run.**

**Pass 3 — repeat all four instruments with the entering state (E45).** 480 samples:
zero-fill −23.810, mean-fill −26.354, swap-fill −25.007, gradient −22.346; spread 4.008 ms,
bootstrap SE 0.054 ms on the zero-fill arm. The corrected value agrees with E44's
independent −23.84 ms. E17 and E34 are superseded, not amended.

**What it cost the paper, honestly.** The centroid moves +1.13 ms and every downstream
number with it: the interval to the output time 27.3 → 26.2 ms, its separation 3.81 → 3.65
standard errors, the ratio to the label dispersion 136 → 130, the displacement at the 99th
percentile speed 1.35 → 1.29 px, the mAP cost 0.06 → 0.04 points. No claim reverses. The
separation stays above three standard errors and the mAP cost stays below a tenth of a
point, so both halves of the result survive at slightly reduced magnitude.

**What it cost that is not a number.** "The profile is close to flat" does not survive. The
corrected CV is 0.131, four times the reported value, and the heaviest bin carries 1.52x the
lightest. The centroid is near the uniform value for a different reason than flatness: the
five older bins hold 48.6 % of the influence against 51.4 % for the five newer, so the
imbalance is between neighbouring bins and largely cancels in the first moment. The
manuscript now says that instead, which is a weaker premise supporting the same conclusion.

**Step 12, the favourable method that must exist.** It was not needed here — the corrected
measurement is favourable on its own, because it agrees with an independent run made for a
different purpose. That agreement is the reason to trust it, and it is the reason the defect
was found at all. Consistent with [[trust-validated-results-suspect-new-runs]]: E44's
disagreement was treated as my bug, and it was.

**Did it spread?** Every script that calls `mdl.forward(..., previous_states=...)` was checked.
Only a script that runs a *second, counterfactual* pass can carry this defect, and there are
six: E17, E34, E42, E42b, E44, E45. E42, E42b, E44 and E45 save the entering state and pass
it; E17 and E34 do not, and both are superseded. E21, E23, E24, E27 and E37 advance the
recurrence without a counterfactual pass, so the detection dump the mAP sweep and the
output-time regression are built on is unaffected. The defect is contained to the two runs
already withdrawn.

---

## Case 10 — a second architecture that turned out to be running stateless (2026-09-08)

**The claim under test.** "The newest window's influence centroid is a property of the
released configuration rather than of the recurrent operator." The evidence was to be
SSM-ViT (Zubic et al., CVPR 2024), a fork of the RVT repository in which each stage's
ConvLSTM is replaced by an S5 state space layer, run through E45's occlusion instrument.

**Pass 1 — the instrument reported an impossible model.** The first bin arm gave
−23.91 ms and −24.97 ms, close to RVT's, and the support arm that followed said that
zeroing the recurrent state changed the emitted detection tensor by **0.0000** of its norm
and that every past window carried zero influence against 0.1401 for the newest. A recurrent
detector unaffected by its own history is not a result; it is a symptom, and the bin numbers
that came from the same calls are then also suspect.

**Pass 2 — read the released implementation.** In `models/layers/s5/s5_model.py`,
`apply_ssm` injects the carried state as

    Lambda_bars[0] = Lambda_bars[0] * prev_state
    _, xs = associative_scan(binary_operator, (Lambda_bars, Bu_elements))

The first reading said the state reaches positions 1, 2, … of a chunk and never position 0,
which would make a one-window call stateless by construction. That reading was wrong, and the
next pass caught it.

**Pass 2b — call it the way the release calls it.** `modules/detection.py` passes the whole
sequence at once as `(L, B, C, H, W)` and applies the detection head per position. E47b does
the same: chunks of eight windows with the state entering the chunk, occlusion applied to one
window, the output read at that window's position, and only positions with at least four
preceding windows inside the chunk used, so each sample carries real in-chunk history. Its
centroids are −23.76 and −24.72 ms, and they are what the paper reports.

**Pass 3 — measure it by position, with a control (E47c).** Driving each model as its own
release drives it and zeroing the state entering a chunk of eight windows: SSM-ViT returns
**0.00000 at every position**, `rvt-t` returns 0.0616 at position one falling to 0.0304 at
the last. A model that ignored its history entirely would return zero to that arm too, so a
second arm occludes the window one position earlier inside the same chunk: SSM-ViT answers
0.0276 there, falling to 0.0106. It is recurrent within a chunk and only across chunks is the
state lost. Re-deriving the scan explains why, and it is not what Pass 2 said: with
`(a_i,b_i)∘(a_j,b_j)=(a_j a_i, a_j b_i + b_j)`, the outputs are the `b` components and `b_p`
is built from `a_1…a_p`, so `Lambda_bars[0]` enters no output at any position. **The
measurement corrected the reading, not the other way round.**

**What the release does, stated as a measurement.** Its streaming evaluation steps through
the split in non-overlapping chunks of 21 windows, so a released detection's temporal support
runs from the current window alone at the first position of a chunk to 21 windows at the
last. That is the same class of undeclared quantity this paper measures elsewhere, and it is
reported as such rather than as a claim about what the architecture could support.

**What this cost, and what it bought.** The first S5 numbers are withdrawn, not corrected:
they describe a model run without history, which is neither the released evaluation regime
nor the instrument applied to RVT. The record is in
`experiments/e47_ssm/withdrawn_L1/WHY.md`. What it bought is a sharper instrument — the state
check now runs before the profile in every architecture port — and a fact about the release
that a reader porting it would otherwise hit silently.

**And a hole in the checker.** `src/audit_numbers.py` verified every macro against its
artifact, but when the withdrawn artifacts were moved aside it simply stopped checking the
eleven macros that depended on them, while the manuscript went on quoting them. Silence read
as success. It now fails on a macro it knows how to derive whose artifact is absent, which is
the same lesson as [[test-the-checkers]] one level up: a checker that can go quiet has not
been tested against the case where it should shout.

---

## Case 11 — the cross-model dump that quietly changed the ground truth (2026-09-08)

**Why the run exists.** External review #7 accepts the paper's measurements and rejects
nothing technical, but names one gap: the temporal support is shown to exist and never shown
to change a benchmark *conclusion*. That question is comparative, so E51 dumps detections for
all five released checkpoints under one protocol and E52 asks whether the ordering survives
scoring each detector at its own output time.

**Pass 1 — check the rewrite against the run it replaces.** E51 generalises E37's dump to a
family and a tag. Before trusting any comparison built on it, its `rvt-t` output was compared
with E37's `dets.npz`. The **detections were byte-identical**, 86 788 rows, and the **ground
truth was not**: 193 of 40 698 boxes differed in their centered velocity, up to 96.5 px/s.

**Pass 2 — find which construction moved.** Boxes, frames and classes matched exactly; only
the velocities differed, and only where a track link was ambiguous. E37 builds greedy
*forward* links at IoU ≥ 0.3 and then inverts them to get each box's predecessor. The rewrite
built the predecessor independently by a backward greedy match. The two disagree whenever the
forward and backward argmax disagree. **The rewrite was the deviant**: every number the paper
reports — the mAP sweep, the speed strata, the 68.7 % of boxes carrying a centered velocity —
rests on E37's construction, so a comparison built on the other one would not be commensurable
with the paper it is meant to defend. E37's block was copied in verbatim and the dumps redone.

**And the checker again reported a pass while printing the failure.** `e51_check.py` compared
shapes, exited non-zero only on a shape mismatch, and printed "E51 reproduces E37's dump"
underneath a line that said `identical: False   max abs diff 9.650e+01`. It now reports the
differing columns and exits non-zero on any difference. This is the third time in two days
that a checker's silence, or its cheerful summary line, has been the actual defect; see case 9
and case 10 and [[test-the-checkers]]. The rule that keeps working is not "write a checker" but
"make the checker fail on the case you have not seen yet, and read what it prints, not what it
concludes".

**Two operational notes, since both cost real GPU time.** A shell re-reads a running script by
byte offset, so editing `run_e51b.sh` while a shell was executing it produced a syntax error
mid-queue; new files, not edits, for anything already running. And an OOM on a shared card is
a scheduling fact before it is a configuration fact: the SSM dump needs room for the 21-window
chunk its release evaluates with, and the queue now waits for a card with that room rather than
taking one from whoever is already on it.

---

## Case 12 — the negative result that review #7 asked for (2026-09-08)

**The question.** External review #7 found no technical flaw and named one gap: does the
measured temporal support change a benchmark *conclusion*? Its experiment: score several
released detectors at the instant each one's output describes and see whether the ordering
changes.

**The answer is no, in all four speed strata, with no pair reversing.** Under the 12-step
protocol that is where the work starts, not where it stops, so the question became whether
the null is a property of the data or of the grid.

**It is a property of the data, and the proof is arithmetic.** In every stratum the largest
gain any model draws from alignment is at most 52 % of the smallest gap between adjacent
models — 0.058 against 0.112 points in the tightest case. No refinement of the δ grid, and no
continuous optimum, can reorder them. That converts "we looked and did not see it" into "it
cannot happen at this scale", which is a stronger statement and the one the paper makes.

**Step 12 says a favourable framing must exist, and here it did not require one.** The result
this produces is not a win dressed as a loss: the paper already claimed the metric cannot
resolve the interval on one checkpoint, and this bounds that claim over five checkpoints, two
architectures and four strata. The honest gain is that an assertion about one model became a
quantitative limit over a family.

**What the search turned up instead.** The ordering is unstable across speed strata:
`s5vit-base` is first in both middle strata and last above 50 px/s, and `rvt-t` is third
overall, last between 25 and 50 px/s, second above 50. That reordering is more than ten times
the largest alignment effect. It is reported, and it is attributed to object speed rather than
to temporal support, because that is what it is. Presenting it as a consequence of this
paper's mechanism would have been the easy overclaim and it is not made.

**And the run found a defect in itself first.** The rewritten dump disagreed with E37 on 193
ground-truth velocities before any of the above was computed; had that not been checked, five
models would have been compared against a ground truth the paper does not use. Case 11.

---

## Case 13 — the experiment that ran to completion without applying its treatment (2026-09-16)

**What E60 is for.** E58 found that the chunk position of a released SSM-ViT detection — one
window of recurrent history at position 0, twenty-one at position 20 — is worth 4.4 and 5.3 mAP
points on the population a released Gen1 number is reported over. Position groups hold different
frames, so that estimate leans on RVT as a scene-content control and on parallel trends. E60
removes the assumption by re-running the same checkpoints with the chunk boundaries moved, so
the *same frames* are scored with and without their history.

**The defect.** The shift was implemented as `start = max(o2r[0] - 21 + 1 - SHIFT, 0)` — every
boundary moved SHIFT windows *earlier*. The release's own start is `max(o2r[0] - 20, 0)`, and
Gen1 labels begin early enough in most sequences that this is **already clamped at 0**.
Subtracting from a clamped value changes nothing. The treatment was applied only to the
minority of sequences whose first label sits past index 20.

**Everything an exit-code check would look at was correct.** The run exited 0. It wrote 20 296
frames, exactly matching E58. Its ground truth was byte-identical to the baseline dump, which is
the precondition `e60_paired.py` asserts. It printed plausible progress the whole way. What was
wrong was the only thing nobody had looked at: whether the positions actually moved.

| | old-short → new-full | old-full → new-short | position unchanged |
|---|---:|---:|---:|
| boundaries 16 earlier (ran, ~45 min of GPU 1) | 774 / 3672 | **18 / 5069** | 14 927 / 20 296 |
| boundaries 5 later (the design) | **3574 / 3672** | 0 / 5069 | 0 / 20 296 |

**The tell was the asymmetry, not the totals.** 774 frames moved one way and 18 the other. A
rotation is a bijection; it cannot move 21 % of a block in one direction and 0.4 % in the other.
The `(old - new) mod 21` histogram said the same thing more directly: five bars where a fixed
shift permits one.

**The second attempt was also wrong, and cost nothing.** The repair clamped the start at the
first labelled frame so that no frame could fall outside a chunk:
`start = min(max(o2r[0]-20, 0) + SHIFT, o2r[0])`. **216 of the 406 validation sequences** have
their first label below index 16, so the clamp pinned their start at the label itself and gave
them a rotation of `o2r[0]`, not `SHIFT`. Six bars in the histogram instead of one. This one was
caught by `src/e60_verify_shift.py` in ninety seconds on a CPU, before any card was claimed.

**What the check is.** Chunk positions depend only on `objframe_idx_2_repr_idx`, the label
timestamps and the number of representation frames. None of that needs a model, CUDA, or the
event data. So the dumper's frame enumeration is replayed from the index files alone and four
things are asserted: that the replay reproduces `positions.npy` exactly at SHIFT = 0, which is
what licenses the rest; that the modified start expression is inert at SHIFT = 0; that every
covered frame's new position is `(old - SHIFT) mod 21`; and that the block the paired analysis
scores is actually populated. It also reads the dumper's own `start = ...` line and fails if it
is not the expression the replay assumes, so the two cannot drift apart by hand.
`run_e60.sh` now runs it first and refuses to claim GPU 1 unless it exits 0.

**Two things this changed in the design, both for the better.** The shift is now **5 later**
rather than 16 earlier. Later is never clamped from below. And 5 is the rotation that carries
positions 0–3 onto 16–19, so the experiment takes the frames the released protocol *starved*
and hands them the history the release already intends to carry — a gain, on the frames that
lost the most, rather than a loss on the frames that lost the least. A single shift cannot do
both directions: a rotation by S swaps two blocks only if `S ≡ -S (mod 21)`, which holds only
for S = 0.

**The rule this adds.** Case 11 established that a checker's cheerful summary line is not
evidence. This adds the case where there is no checker at all because the job's own exit code
looks like one: *verify that the intervention happened, not that the run finished.* An
experiment whose treatment is a change of indexing can be checked on indices, and indexing is
free. The check belongs before the GPU, not after it.
