# Round 2 — Reviewer 03 (evaluation, benchmarks, metric design)

*Target: Team 08, `ideas/team08_v2.md`. Round-one verdict: **ACCEPT**, ranked 2nd of 10 behind Team 06.*

**Standing question, unchanged:** is the proposed evaluation a measuring instrument, or a scoreboard the
authors built to stand on? In round one I set one test and I will apply the same one here: *does the quantity
disagree with something the authors did not define?* Four of roughly sixty invented metrics in this round
passed it. The revision has to be judged against that base rate, not against how much work went into it.

**Preliminary, and I will say it before I start grading.** In my round-one metric audit I scored `AP^sync`
**SOUND**, with the note *"Never uses GT velocity at inference; that restriction is load-bearing and correctly
imposed."* That grade was given when `AP^sync` was a middle term in a decomposition chain. The revision
promotes it to the paper's only ranking instrument. A quantity that is adequate as a diagnostic is not
automatically adequate as a ranking instrument, and my round-one pass was on a narrow reading — I checked
what happens at inference and did not check where the correction's *calibration constant* comes from. That is
the gap this review is mostly about, and the authors should read the section below as me auditing my own
round-one grade as much as their revision.

---

## Is `AP^sync` an instrument or a rigged axis

The brief asks me to verify three properties adversarially: that the transformation is one the original
authors would accept, that it uses no privileged information, and that it can lower the score. I take them in
the order of how badly they fail.

### Test 1 — would the original authors accept the transformation? **PASS.**

The transformation is `ĉ ← ĉ − τ̂_P · v̂_pred`, followed by the *unmodified* COCO AP against the *unmodified*
ground truth at the *unmodified* query time. Nothing in the metric's definition changes: not the matching
rule, not the IoU threshold, not the tolerance, not the GT. The prediction file changes. RVT's authors declare
that their output is the state at `t`; re-anchoring produces a (differently estimated) state at `t`. An author
who objected would have to argue that a legal, training-free, GT-free post-process on their own outputs is
somehow off-limits, which nobody will argue. This is genuinely a different animal from `AP^⊥`, and the
distinction the revision draws in §4.4 is the correct distinction. **This is the part of the repair that
works, and the authors deserve to be told so plainly.**

Two loose ends that must be closed before this stays a PASS:

- **`v̂_pred` must be declared causal.** §4.4 and §6 both say only "the method's own *consecutive* outputs."
  If `v̂` is finite-differenced from outputs at `t` and `t+Δ`, the correction is non-causal, is not shippable,
  and — worse — leaks the object's realised future path, which is correlated with the GT at `t` in exactly
  the direction that raises AP. Estimate `v̂` from `(t−Δ, t)` only, and say so in the definition line.
- **The re-anchoring needs an association rule across the method's own outputs, and an association rule has
  parameters.** "Five lines" understates it: detections have no track IDs, so `v̂_pred` requires
  detection-to-detection matching, whose gate radius, score threshold and lifetime are all free. Freeze one
  rule, use it identically for every method, publish it, and report sensitivity to the gate radius. Otherwise
  the "five lines anyone can apply" is five lines plus a tracker the authors tuned.

### Test 2 — does it use privileged information? **FAIL, and this is the ruling.**

`v̂_pred` is GT-free. **`τ̂_P` is not.** By §4.3, `τ̂_P` is the slope of `e_∥ = ⟨ĉ − c*(t), û⟩` regressed on
`‖v*(t)‖`, and `c*`, `û` and `v*` are all ground truth. E1d then computes `τ̂` and the decomposition table —
`(AP, AP^sync, AP^⊥, …)` — in the same pass, on the same data.

So `AP^sync` is: *the standard metric, applied to a prediction file transformed by a one-parameter correction
fitted to the ground truth of the evaluation set, and then scored against that same ground truth.* The
inference-time step is GT-free; the calibration is not. The word "never from ground truth" in §4.4 attaches
to `v̂_pred` and the reader is invited to carry it to the whole transformation. It does not carry.

Three consequences, in increasing order of seriousness.

1. **The optimism is not bounded and is not bootstrapped away.** §4.5 says `τ̂` is refit inside each bootstrap
   resample. That covers sampling and estimator variance; it does **not** cover in-sample optimism, because
   the refit inside each resample is fitted and applied on the *same* resample. Every draw reproduces the
   leak. The bootstrap CI on `Δ_clock` is therefore centred on the wrong quantity, not merely wide.
2. **The monotonicity I objected to in `AP^⊥` reappears, one layer down.** The whole force of my round-one
   objection was that `AP^⊥`'s gain is monotone in `|τ̂|`, so a method that is later gains more, so a flip is
   mechanically available for any narrow pair. A one-parameter GT-fitted shift has the same property in
   expectation: the larger `|τ̂_P|`, the more along-track residual there is for the fitted shift to remove, and
   the larger the expected AP gain. The mechanism is different — a fit rather than a definition — but the
   *shape of the advantage* is the same, and the shape is what makes a flip mechanically available. **The
   self-serving charge is not dissolved. It is relocated from the metric's definition to the metric's
   calibration.**
3. **There is no null model for `AP^sync`, and `AP^⊥` has one.** This is the structural gap. `AP^iso` is the
   equal-budget free-direction null for `AP^⊥` — a control that answers "would *any* relaxation of this size
   have produced this?" Nothing in §4.3–4.5 answers the analogous question for `AP^sync`: *would any
   one-parameter shift fitted on the evaluation set have raised AP by this much?*

### Test 3 — can it go down? **TRUE BUT UNAUDITED, and the authors are over-claiming what it buys.**

R2's correction is right and I accept it: `AP ≤ AP^sync` is false. It can go down, for two real reasons —
`v̂_pred ≠ v*`, so the applied shift is misdirected and noisy; and AP is a thresholded, non-monotone functional
of box position, so a shift can push a marginal detection below the IoU threshold. Good.

But "can go down" is a far weaker property than the revision leans on. What matters is whether it *does* go
down when it should. The paper currently has no case in which `Δ_clock < 0` is predicted in advance. Two free
checks turn "can go down" from a theoretical possibility into an audited property:

- **A clock-clean predictor.** Take any method whose EIV-corrected `τ̂` CI contains 0 (or synthesise one by
  time-shifting a method's outputs to zero its measured `τ̂`) and report `Δ_clock` for it. It must be ≤ 0,
  and its magnitude is the **noise floor of the re-anchoring** — the amount of AP that the `v̂` noise costs
  for free. Every reported `Δ_clock` must then be read against that floor, not against zero.
- **Print the sign for all of them.** If `Δ_clock > 0` for all 15 checkpoints, the "it can go down" defence is
  never exercised, and a reviewer is entitled to say so. Report the distribution.

### The missing control, and it is free: **`b` is the null model for `AP^sync`**

The same regression that yields `τ̂_P` yields `b`, the speed-independent spatial intercept. `AP^sync` applies
`τ̂_P` and does **not** apply `b`. That asymmetry is defensible — correcting `b` is pure test-set fitting with
no physical story — but it is also exactly the control the paper needs and does not have. Define

```
AP^bias   : ĉ ← ĉ − b̂_P          (the SAME regression's other fitted parameter, a constant vector)
Δ_bias    = AP^bias − AP
```

and report `Δ_bias` beside `Δ_clock` in every table. `Δ_bias` is the answer to *"would any one-parameter
test-set fit have raised AP by this much?"* If `Δ_bias ≈ Δ_clock`, the gain is fitting, not clock correction,
and `AP^sync` is a rigged axis after all. If `Δ_clock ≫ Δ_bias`, the gain is directional and speed-coupled in
the way the thesis requires, and `AP^sync` is an instrument. **This costs one CPU re-score and it is the
single highest-value experiment I can name in this revision.** It is to `AP^sync` what `AP^iso` is to `AP^⊥`,
and its absence is the reason my ruling is not a clean PASS.

### Ruling

`AP^sync` is **structurally the right object and is not yet a legitimate ranking instrument.** The
transformation is legal, the metric is unmodified, the "anyone can apply it" claim is true, and the
C10 shape — same quantity, corrected protocol, cheap post-hoc method overtakes train-time SOTA — is
correctly identified and correctly targeted. That is real progress and it is the compliance I asked for.
But the correction is *calibrated on the test ground truth*, which is privileged information, and the paper
neither discloses this nor controls for it. **The self-serving charge is relocated, not dissolved**, and the
relocation is to a place where it can actually be fixed — which `AP^⊥` never could be. Two changes make it an
instrument, both cheap:

- **Cross-fit `τ̂_P`.** Partition the evaluation sequences into folds; estimate `τ̂_P` on the complement of
  each fold and apply it inside the fold. Report the cross-fitted `AP^sync` as the headline and the in-sample
  one beside it, exactly as you already do for `τ̂_IV` vs `τ̂_naive`. Better still: **publish one `τ̂` per
  checkpoint, estimated on a declared split, and apply that published constant everywhere.** That is a
  transferable correction a third party can use without refitting, it makes the reporting contract concrete,
  and it removes the leak in one move.
- **Add `AP^bias` as the null.**

With those two, `AP^sync` is a legitimate leaderboard instrument and I would defend it against any reviewer.
Without them, the first hostile question in review is "where did `τ̂` come from?" and the paper has no answer
in its own text.

---

## The null-result escape hatch

The claim under audit: a null slope in the `τ̂`-vs-`w_P` regression (P6 / K4 / Panel C) is publishable, because
"a slope means `τ̂` is a property of the predictor; a null slope means it is a property of the dataset."

**As designed, this is 70 % honest pre-registration and 30 % escape hatch, and the 30 % is fixable.**

**What is genuinely honest, and I want it on the record.** The branch is pre-registered with a date
(2026-10-19), a stated abstract change, a retitle, and an explicit concession that the fallback is *smaller*
("honestly smaller"). Death 3 states the branch in advance rather than reaching for it in a rebuttal, and K8
caps the whole thing with a hard stop that sends the work to a workshop rather than padding a main-track
submission. Almost nothing else in the ten-idea pool does this. Compared with v1 — where the headline was a
flip that could simply fail to occur, leaving nothing — this is a large structural improvement and it is the
correct response to R10.

**What makes it an escape hatch as written.**

1. **The branch triggers on an absence, not on a presence.** K4 fires when "the slope CI contains 0". A CI
   containing zero is not evidence of a common dataset offset; it is evidence of nothing. There are at least
   four routes to a null slope and only one of them is the finding: (a) a genuine dataset-level offset;
   (b) attenuation — the same EIV problem the paper documents on the y-axis also applies to the *x*-axis,
   because `w_P^meas` is itself estimated (E1b/E1c) with error, which attenuates the slope toward zero;
   (c) the `w_P` axis is manufactured by bin-masking, an OOD manipulation whose effect on `τ̂` may be dominated
   by damage rather than by support; (d) no power — 12 heterogeneous points, several of which are correlated
   because they come from the same checkpoint. Routes (b), (c) and (d) all produce "we measured the dataset"
   as an artefact of a weak experiment.
2. **The decision rule does not partition the outcome space.** P6 predicts a slope in `[0.3, 0.7]`. K4 fires
   on a CI containing 0. With 12 points, a plausible CI is something like `[0.05, 0.85]` — which neither
   excludes 0 nor excludes the predicted band. In that case P6 is not falsified, K4 does not fire, and the
   paper is free to report P6 as confirmed on an interval that is consistent with no effect at all. That gap
   between the two criteria is where a pre-registration quietly becomes unfalsifiable. **Fix: make the rules
   complementary.** Declare the slope branch only if the CI excludes 0 *and* overlaps `[0.3, 0.7]`; declare
   the dataset branch only under an equivalence test (TOST) in which the CI excludes the whole of
   `[0.3, 0.7]`; declare "underpowered, no branch" otherwise, and pre-register that this third outcome is
   reported as underpowered rather than as either finding.
3. **The dataset branch converts the sharpest referee objection into the paper's fallback contribution.**
   Death 3's own title is *"You are measuring the labels, not the models."* The null branch is that objection
   with the sign flipped and the word "finding" attached. That move is legitimate *only* if the finding is
   positively identified — otherwise the design has the property that no reviewer objection can hurt it,
   which is the definition of unfalsifiable.

**How to make the dataset branch a real result — and it can be one, cheaply.** The claim *"every published
number on this benchmark is scored against labels offset by X ms"* is quantitative, falsifiable, and would be
a genuine benchmark-integrity finding. But it must be earned positively, and there are two free external
referents available for exactly that:

- **The common-component test.** The variance decomposition sketched in Death 3 is the right instrument and
  must be promoted into K4: estimate the dataset-level offset as the common component of `τ̂` across ≥ 3
  methods, require its CI to **exclude 0**, and report an upper bound on the method-level component. "There
  is a common offset of X ± Y ms and the between-method spread is bounded by Z ms" is a finding. "The slope
  CI contains zero" is not.
- **An independent prediction of X.** The annotation pipeline's own clock is knowable. DSEC ships per-frame
  exposure timestamps; DSEC-Det's labels are QDTrack on those 20 Hz frames; the interpolation half-width is
  published as 50 ms. That gives an *a priori* expectation for the annotator offset that the authors did not
  define. If the measured common offset agrees with it, the null branch has an external referent and is worth
  a paper on its own. And the calibration is free: run a **frame-only detector on the RGB frames at the anchor
  timestamps** and measure its `τ̂`. Its support centroid is near zero, so whatever `τ̂` it shows *is* the
  annotator offset. That single number turns the dataset branch from a shrug into a measurement, and it also
  gives Panel C a point at `w_P ≈ 0` — the anchor of the regression the paper does not currently have.

With the complementary decision rule, the common-component requirement, and the frame-only anchor point, the
null branch is honest pre-registration. Without them, "we measured the dataset, not the method" is a sentence
the paper can always say.

---

## Statistics audit

§4.5 is the most completely specified statistical procedure in the ten-idea pool, and it is specified in the
main paper rather than assumed — which is what I asked for and did not expect to get. Sequence-level
resampling, pairing, `B = 10000`, refitting the estimator inside the resample, a pre-registered capped pair
list, Holm, and the explicit retraction of "maximise the pool" are all correct. Below are the holes, in the
order a statistically literate reviewer will find them.

### 1. Sequence-level resampling is the right unit, and `n_seq` is the wrong `n`

Resampling the recording is correct: detections within one sequence share scene, illumination, tracks and
ego-motion, and are not exchangeable. But the brief's question — sequences differ wildly in length and content
— is a real defect and the revision does not address it.

- **Report effective `n`, not `n_seq`.** With unequal cluster sizes the bootstrap's effective independent
  sample size is closer to `(Σ n_i)² / Σ n_i²` than to the sequence count. For a driving benchmark where a
  handful of long, object-dense sequences dominate the detection pool, that can be half the nominal `n_seq`.
  Print it in every CI caption. A CI labelled `n = 60` that behaves like `n = 25` is the most common way a
  bootstrap misleads.
- **AP is not a mean, and the resample changes the estimand.** COCO AP is computed by pooling detections
  across the resample. Resampling sequences with replacement duplicates whole clusters, which inflates the
  PR curve's sample count without adding diversity, and rare classes can be absent from a resample entirely,
  leaving mAP averaged over a different class set draw to draw. Pin the class set for all resamples, and state
  what happens to a class with zero instances. This is not pedantry: it is the mechanism by which a bootstrap
  on a pooled ranking metric produces a distribution that is not the sampling distribution of the reported
  number.
- **The percentile bootstrap is the wrong interval here.** `ΔAP` is a difference of ratio-type functionals
  and its bootstrap distribution is skewed. The stated rule reads a one-sided tail probability at 0.95/0.05,
  which is precisely where percentile intervals are least accurate. Use BCa, or report the bias-correction
  and acceleration constants, and cross-check with a delete-`d` jackknife over sequences. At `B = 10000` this
  costs nothing.

### 2. The 10 s block bootstrap is currently a power knob

Where `n_seq < 20`, the plan additionally reports a 10 s block bootstrap "which raises the effective `n`".
That is exactly the problem. For driving data, the scene, illumination, object population and ego-speed regime
are approximately constant over an entire 60 s recording; blocks within a sequence are far more alike than
blocks across sequences, so a 10 s block bootstrap under-states dependence and narrows the CI — in the
direction that makes flips *easier* to declare. Printing both intervals does not fix this if the reader is
left to choose.

**Fix, one line:** pre-register that every *decision* (flip claims, CI-excludes-zero claims) is taken on the
**sequence-level** interval, and that the block bootstrap is reported as a robustness check only. And note the
uncomfortable tension the revision has created for itself: **every reason DSEC-Det was promoted to primary
testbed (20 Hz labels, track IDs, a published `w_G`, small EIV) is orthogonal to sequence count, and DSEC-Det
is precisely where `n_seq` is small enough to trigger the block bootstrap.** Gen1, with far more recordings, is
where the sequence bootstrap is comfortable and where `τ_max` is an admitted free parameter. Say this
explicitly in the paper rather than letting a reviewer discover it: the dataset with the best estimator has the
worst `n`, and vice versa.

### 3. Holm over 12 pairs — the correction is well chosen and mis-targeted

- **The per-pair p-value is undefined.** The flip rule is a *conjunction* of two one-sided bootstrap
  probabilities. Holm requires one p-value per hypothesis. Define it — the natural construction is
  `p_pair = max(1 − P(order | AP), P(order | AP^sync))` — and state it, or "Holm across the tested pairs" is
  not implementable as written.
- **Holm is applied to the one family the paper has already declared non-load-bearing.** The flip is now a
  supporting result that is allowed to come back null. Meanwhile P1–P8, `R`, `E[cos²θ]`, `σ_τ`, the slope, and
  the three estimators are all confirmatory tests with no multiplicity control at all. That is a
  mis-targeted correction. The defensible position — and I think it is defensible — is that P1–P8 are
  directional point predictions pre-registered with explicit falsification conditions, and are therefore
  reported without correction *as pre-registered predictions, not as discoveries*. Write that sentence in the
  paper. A reviewer who sees Holm on the unimportant family and nothing on the important one will assume the
  authors do not know the difference.
- **Pre-registration must be verifiable.** "Pre-registered in the supplement before any prediction file is
  scored" is unverifiable at review time. A timestamped public commit hash of the pair list, cited in the
  paper, is the only form that means anything.

### 4. Does the 0.95/0.05 two-way rule leave any power? Do the arithmetic and publish it

Take the rule at face value. Per pair you need `P(order | AP) ≥ 0.95` **and** `P(order | AP^sync) ≤ 0.05` —
that is roughly 1.65 paired standard errors in each direction, so the *differential* clock effect must satisfy

```
| (Δ_clock,A − Δ_clock,B) |  ≳  3.3 · SE_paired(ΔAP)    (before Holm)
```

and under Holm at 12 pairs the smallest-p test runs at α = 0.05/12 = 0.0042, i.e. ≈ 2.6 SE each way:

```
| (Δ_clock,A − Δ_clock,B) |  ≳  5.2 · SE_paired(ΔAP)    (Holm-corrected, first rejection)
```

Pairing helps a great deal here — the paired difference for two detectors on the same sequences is strongly
correlated and its SE is much smaller than the difference of two marginal SEs — and the revision is right to
insist on it. But the rule still demands a differential clock correction of several paired SEs. For the pair
the plan actually has (RVT-B vs S5-ViT-B, published gap ≈ 0.5 mAP, both consuming the *same* preprocessed
tarballs at `dt=50 nbins=10`, hence near-identical `w_P` and probably near-identical `τ̂`), the differential
clock effect is close to zero by construction. The cross-family manipulations that *would* produce a large
differential — BFlow `E` vs `E+I`, E-RAFT MVSEC 20 vs 45 Hz — are flow, not AP, and §E2 correctly forbids any
ranking claim on them because the split is contaminated. **So on the current plan there is no live flip
candidate at all.**

Is that dishonest conservatism? **No — but the paper must say it, and the way to say it is a power analysis.**
Required, before unblinding: for each of the ≤ 12 pre-registered pairs, compute the paired `SE(ΔAP)` from a
pilot on one dataset and publish the **minimum detectable differential clock effect** under the stated rule.
Any pair whose MDE exceeds the largest `Δ_clock` physically available should be dropped from the list rather
than tested — testing a pair you have shown you cannot resolve is what turns conservatism into a guaranteed
null with a rigour costume.

### 5. The result the statistics will actually produce, which the paper should promote

I set this out because I think the team is about to under-sell its own best statistical finding. In round one
I reported that **no in-window paper at CVPR/ICCV/ECCV/NeurIPS puts confidence intervals on a leaderboard
ranking at all.** If the paired sequence bootstrap shows that the published Gen1 top-of-leaderboard gaps —
0.5 mAP between RVT-B and S5-ViT-B, and comparable gaps elsewhere — sit inside their own CIs, then *the
field's ordering of its flagship event detectors is not resolved by the field's own data*. That is a C10 /
C13-class result: it does not need a flip, it does not need `AP^sync`, it does not need `τ̂`, it cannot come
back empty, and it costs one CPU pass over prediction files the paper is dumping anyway. It is also entirely
robust to every objection in this review, because it uses only the standard metric.

Report the full ordering-probability matrix over all methods under plain `AP`, with the effective `n`, as a
main-paper table. Then `AP^sync` becomes the second column of a table whose first column is already a finding.
**This is the strongest thing in the revision's statistics section and it is currently not stated as a
contribution at all.**

---

## Surviving metrics, re-scored against the external-referent test

The test: does the quantity disagree with something the authors did not define? Round-one base rate: four of
about sixty.

| Quantity | External referent? | Verdict |
|---|---|---|
| **`τ̂`** (EIV-corrected latency, ms) | **YES, and this is new in v2.** E1b's per-bin occlusion measures the network's influence centroid by a *different procedure* (input-bin ablation on a released checkpoint) than `τ̂` (regression against GT tracks). P1 requires them to agree to ±8 ms. Two independent estimates of one latent, one of which is a property of someone else's trained weights. | **SOUND, and upgraded.** This is the repair that closes my round-one objection. "Recovering −25 ms once is arithmetic; a slope-1 line across architectures is evidence" — the revision does better than I asked, because the influence centroid is a *measured* predictor, not a declared one. Two caveats: measure the occlusion-induced shift along a tangent taken from the method's own outputs, not from GT, or the two "independent" measurements share an input; and the mean-imputation and symmetric-trailing-mask controls (already planned) must be reported even when they are boring, since they are what separate support from OOD damage. |
| **`b`** (speed-independent intercept) | Weakly — it is defined against `τ̂` in the same regression. | **SOUND** as a diagnostic, and now doubly valuable because it supplies the missing null for `AP^sync` (see above). Promote it from a by-product to a control. |
| **`w_P^meas`** | **YES.** Its referent is `w_P^decl`, which is a number in someone else's config file. Measured-vs-declared is exactly the C4 shape. | **SOUND.** And the `min(w_P^decl, w_P^meas)` rule is the one design choice in this entire round where the authors deliberately took the value that can only hurt them. Say so in the paper in one sentence; reviewers notice self-denying ordinances and there are almost none in this batch. |
| **`R = (AP^⊥ − AP)/(AP^iso − AP)`** | Weakly. All three terms are the authors' constructions and the null is now simulated on the authors' own score distribution. | **SOUND-BUT-MARGINAL, saved by K1.** It survives only because it is demoted to a diagnostic that is allowed to come back vacuous, with a dated kill criterion. Two technical requirements: `R` is a ratio whose denominator `(AP^iso − AP)` can be near zero, making it explosive and its CI meaningless — pre-register a minimum denominator magnitude below which `R` is not reported, and print numerator and denominator separately with CIs. And you are right to make `E[cos²θ]` primary: it is the only anisotropy statistic here with a *derivable* null (0.5 in 2D), i.e. a fact the authors did not choose. Lead with it. |
| **`AP^⊥`, `AP^⊥L`** | No. | **Correctly demoted.** `AP^⊥` as the numerator of `R` and `AP^⊥L` as a sensitivity check is the right place for them. `AP^⊥L` is a genuine improvement — adopting LET-3D-APL's affinity weighting is the *published* answer to "your permissive metric dominates," and citing the ancestor's own remedy is better than inventing one. |
| **`AP^sync`, `Δ_clock`** | **Not yet.** The transformation has an external referent (the standard metric, unmodified); the calibration constant does not. | **PENDING.** Cross-fit `τ̂_P` and add `AP^bias`, and this becomes SOUND. See the ruling above. |
| **`σ_τ`, `σ_τ,excess`** | **NO — and the null that was added tests the wrong hypothesis.** See below. | **NOT SOUND as posed.** This is the one place the revision went backwards relative to its own standard. |
| **E0's linear oracle** | **YES.** The benchmark's own generative process, stated in the benchmark's own sentence. | **SOUND**, unchanged, and still the best-designed measurement in the ten-idea pool. The v2 sharpening — from "median IoU > 0.9" to *"an identity check, not a statistic"* on DSEC-Det — is strictly better: it is a one-line result in either direction and it cannot be argued with. |
| **`M` / TS-Split / `AP@HiM`** | Yes — computable from GT and declared specs before any model runs. | **SOUND**, unchanged. Still the only structurally correct stratification in the round. |
| **`TEF`** | — | **Does not appear in v2.** Confirmed by grep. Nothing to score; it stayed with Team 04. Good — the revision resisted the temptation to absorb it along with `σ_τ`. |

### `σ_τ` — the null tests the opposite of the claim

I killed Team 04's `σ_τ` for having no null model, and the revision imports it *with* a null, explicitly citing
my objection. I have to report that the null it imports does not test the hypothesis the paper needs.

**The claim (Death 4, §4.6, and the whole variance-half escape from R7's "so what"):** *different objects in
one prediction tensor have different effective timestamps*, so a declared scalar timestamp cancels a constant
and cannot cancel a dispersion.

**The null as stated:** resample each "frame's" object set from *different* frames within the same sequence
and speed stratum; if within-frame dispersion is not detectably smaller than this across-frame dispersion,
drop `σ_τ`.

That test detects a **per-frame common clock offset** — a component shared by objects within a frame and
varying between frames. Within-frame dispersion falls below across-frame dispersion precisely when each frame
has its own offset. But **a per-frame offset is exactly the thing a declared per-frame timestamp cancels.**
So the branches are:

- Test passes (within < across): you have evidence of a frame-level clock component, which *is* declarable and
  therefore does **not** support Death 4's "the reporting-contract answer runs out here."
- Test fails (within ≈ across): you drop `σ_τ` under K5.

**Under the stated null, the variance escape from R7's objection cannot be earned in either branch.** The
right null for "per-object dispersion within one tensor exceeds estimator noise" is the estimator's own
per-object variance, calibrated where the true per-object timestamps are known — which is E4(iv), already in
the plan. Make E4(iv) the primary null for `σ_τ`, and either repair the permutation test or restate what it
shows (a frame-level offset, declarable) and stop counting it as the escape.

### `σ_τ` is also confounded by the interpolated GT, contrary to §4.6

§4.6 argues that `σ_τ` survives the zero-acceleration GT because it is "dispersion of a first-order quantity
across *objects*, not across time." That argument does not hold, and it matters because it is the load-bearing
reason `σ_τ` was chosen over the acceleration-driven quantities my round-one cross-cutting finding killed.

On DSEC-Det, an object's inter-frame GT position lies exactly on the line between its 20 Hz anchors. For an
object with true acceleration `a_i`, the GT position error at inter-frame time `t` is
`≈ ½ a_i (t − t_0)(t − t_1)` — nonzero, **object-specific**, and varying within a single frame across objects
with different accelerations. It enters `e_∥` directly and hence `δ̂_i` directly. So the interpolation prior
injects a per-object, within-frame dispersion that is indistinguishable from `σ_τ` by construction, and it
injects *more* of it for objects with more acceleration, which correlates with speed, which is the paper's own
stratification variable. The confusion in §4.6 is between "we do not need acceleration in the GT to measure
this" (true) and "GT acceleration error does not contaminate this" (false).

**Three fixes, all free, and any one of them rescues the quantity:**

1. **Measure `σ_τ` at the anchor frames only.** At the 20 Hz anchor timestamps the GT is a real annotation,
   not an interpolant, so the interpolation confound is zero by construction. If `σ_τ,excess` survives at the
   anchors, it is real. This is the clean version and it should be the headline form.
2. **Stratify by anchor-estimated acceleration** (three consecutive anchors give `a_i` for free). The confound
   predicts `σ_τ,excess ∝ |a_i|`; a genuine per-object clock dispersion predicts it flat. That is a
   *discriminative* prediction with an external referent, and it is the shape I asked Team 08 for in round one.
3. **The cross-method correlation test.** Compute per-object `δ̂_i` residuals for two different methods on the
   same frames. If `σ_τ` is annotator- or interpolation-driven, the residuals are **correlated across
   methods**; if it is a property of each predictor's internal clock, they are not. One CPU pass, two
   checkpoints already in the plan, and it is the strongest external referent available for `σ_τ` — it
   disagrees with something no one defined.

### Invented-quantity count

For the record, since I told this pool that reviewers count: v2 has more invented quantities than v1, not
fewer — `τ̂`, `b`, `σ_τ`, `σ_τ,excess`, `w_P^meas`, `λ_att`, `κ`, `δ̂_s`, `R`, `E[cos²θ]`, `AP^⊥`, `AP^⊥L`,
`AP^iso`, `AP^sync`, `Δ_clock`, `Δ_TS`, `M`, `AP@HiM`. That is not fatal, because §4.2's *headline* table is
disciplined to five rows of which one is standard AP, and headline discipline is what matters. But E1d's
decomposition table has ten columns, and a ten-column table reads as axis-shopping regardless of how it was
derived. Cap the main-paper per-method table at five numbers and put the rest in the supplement.

---

## Was my objection closed

My round-one objection, in its exact form: *pre-registering a prediction from someone else's released config
defuses estimator validity only; the self-serving charge attaches to `AP^⊥`, whose definition forgives the
error the authors want forgiven, and you cannot pre-register your way out of a metric that forgives your
error.*

**Closed, on the part that was closable, and closed by the method I named.** I said the fix was to drop
`AP^⊥` from the headline or defend it as a corrected score. They dropped it — from the abstract, from the
headline table, and from the ranking role — and kept it only as `R`'s numerator with a dated vacuity kill
criterion. They also adopted the ancestor's own remedy (`AP^⊥L`, LET-3D-APL's affinity weighting) rather than
inventing a defence. §7 of the response table says *"We do not answer this; we comply with it."* That is the
correct response to an unanswerable objection and I have no complaint about it.

**Partly re-opened in a new place.** The self-serving structure has moved from `AP^⊥`'s *definition* to
`AP^sync`'s *calibration*. That is progress — a leak in a calibration is fixable by cross-fitting; a
definition that forgives your error is not fixable at all — but it is not closure, and the paper does not
currently know the problem exists. The 30-second version for the authors: **you removed the metric that
forgives your error and replaced it with the standard metric plus a correction fitted to the test set's
ground truth. Cross-fit it and add the `b` null, and you are done.**

**Three related items, scored.**

- **The RVT pre-registration.** My round-one complaint was that the `t − 25 ms` prediction was arithmetic on a
  config with an escape hatch on both sides, and that `experiments/e02` says so explicitly ("*the 25 ms figure
  is the uniform-weight reference point, not a prediction of the network's behaviour*"). The revision corrects
  the sentence everywhere *and* — better — adds E1b's per-bin occlusion, which measures the thing the 25 ms was
  standing in for. That converts C3 from confirmatory to discriminative, which is precisely the fix I asked
  for, executed more cheaply and more convincingly than my own suggestion. **Fully closed.**
- **The statistics.** I said there is no in-window precedent for bootstrapping a leaderboard ranking, so the
  statistics could not be omitted. They are no longer omitted; they are the most fully specified in the pool.
  **Closed in substance**, with the four technical holes above outstanding — and with the observation that
  the paper has not noticed that its own bootstrap is a headline result.
- **LET-3D-AP as precedent.** The authors are right and I should be explicit about it, because it bears on my
  round-one claim. I said no *in-window* paper bootstraps a leaderboard ranking; that is unchanged and
  LET-3D-AP does not contradict it — LET reports a flip, not confidence intervals on one. But on the separate
  question of whether the *device* is legitimate, LET-3D-AP is a real and strong precedent: decompose along a
  privileged axis, define a tolerance-parameterised AP, re-score published detectors, report a flip — and it
  became an official Waymo challenge metric. It is one of the four metrics the community adopted rather than
  one of the four hundred it ignored, and it is the closest analogue to what this paper proposes. Installing
  it as the ancestor, lowering the novelty self-score to 5.5 in the paper rather than in a rebuttal, and
  adopting APL's affinity weighting is the correct handling of a collision. It does not, however, license
  `AP^sync`'s calibration leak — LET's tolerance is swept and declared, not fitted to the evaluation set, and
  that is the one axis on which this paper is currently *behind* its ancestor.

---

## Verdict

**ACCEPT** (unchanged in letter, materially stronger in substance).

The revision is the most responsive I have seen in this round. It complied with an objection it could not
answer rather than arguing; it accepted a novelty collision and lowered its own score in the paper; it
retracted "maximise the pool" and capped the pair list; it turned a sentence I flagged as an overclaim into a
measurement (E1b); it converted the ranking flip from the headline into a supporting result with a
pre-registered rule that can and probably will return null; and it imported Team 04's `σ_τ` while explicitly
supplying the null I said Team 04 lacked. That last one is executed wrongly, but the instinct was right.

Against that: `AP^sync`'s calibration constant is fitted on the evaluation ground truth and the paper does not
say so; it has no null model where `AP^⊥` had one; `σ_τ`'s permutation null tests a frame-level offset rather
than a per-object dispersion, and `σ_τ` is confounded by the interpolated GT in exactly the way my round-one
cross-cutting finding predicts; and the flip machinery, as designed, has no live candidate at this sample
size — a fact the paper should compute and publish rather than discover in review.

Ranking: Team 08 remains second behind Team 06, but the gap has closed to almost nothing, and it closes the
rest of the way if two things land. Team 06's headline (99 % of the residual explained) is still measured on
synthetic band-limited texture with an ideal sensor and will fall on real DSEC. Team 08's floor — E0 — is
real, free, third-party-computable, and publishable in either direction, and its best new instrument (the
agreement between the occlusion-measured influence centroid and the regression-measured `τ̂`) is two
independent measurements of one physical quantity on someone else's released weights. **If E0 lands and P1's
±8 ms agreement holds, Team 08 is the stronger paper and should be ranked first.**

---

## Minimum change to reach ACCEPT

**Not applicable — I am at ACCEPT.** What follows is the minimum change to reach **STRONG ACCEPT**, which is
where I would like this to end up. Six items; none needs a GPU, and all six together are under two CPU-days.

1. **Cross-fit `τ̂_P` for `AP^sync`, and publish one `τ̂` per checkpoint.** Estimate on the complement of each
   fold, apply inside the fold; report the cross-fitted number as headline and the in-sample number beside it.
   Disclose in the text that `τ̂_P` is GT-fitted, in the same sentence that says `v̂_pred` is not. *This is the
   single change that decides whether `AP^sync` is an instrument.*
2. **Add `AP^bias` as `AP^sync`'s null**, using `b̂` from the same regression, and report `Δ_bias` beside
   `Δ_clock` in every table. Add the clock-clean predictor whose `Δ_clock` defines the re-anchoring noise
   floor, and print the sign of `Δ_clock` for every checkpoint. Declare `v̂_pred` causal, and freeze and
   publish the association rule.
3. **Make P6 and K4 complementary**, with a TOST for the dataset branch, an explicit "underpowered, no
   branch" outcome, a common-component test whose CI must exclude 0 before the dataset branch may be claimed,
   and the frame-only-detector anchor point at `w_P ≈ 0` that calibrates the annotator offset against DSEC's
   own published exposure timestamps.
4. **Repair `σ_τ`:** measure it at the anchor frames as the headline form; make E4(iv) the primary null;
   stratify by anchor-estimated acceleration; and add the cross-method residual-correlation test. Restate what
   the permutation test actually shows (a declarable frame-level offset) and stop counting it as the answer to
   R7's "so what" until one of these lands.
5. **Fix the four statistical holes:** report effective `n` rather than `n_seq`; pin the class set across
   resamples; use BCa or report the bias/acceleration constants; pre-register that all decisions are taken on
   the sequence-level interval with the block bootstrap as robustness only; define the per-pair p-value for
   Holm; publish the minimum detectable differential clock effect for each of the ≤ 12 pairs *before*
   unblinding, and drop the pairs you have shown you cannot resolve.
6. **Promote the bootstrap itself to a contribution.** Publish the ordering-probability matrix over all
   methods under plain, unmodified `AP`, with effective `n`. If the published gaps on Gen1 and DSEC-Det sit
   inside their own sequence-level CIs, then the field's ordering of its flagship event detectors is not
   resolved by the field's own data — a result that needs none of this paper's invented quantities, cannot
   come back empty, is immune to every objection in this review, and is the first of its kind at these venues
   on my round-one sweep. Right now it is buried in §4.5 as machinery. It should be Table 1.
