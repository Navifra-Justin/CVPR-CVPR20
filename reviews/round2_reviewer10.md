# Round 2 — Reviewer 10 (hostile, reject-by-default) — Team 08 v2

*Re-review of `ideas/team08_v2.md` against `ideas/team08.md`, my round-one review
(`reviews/reviewer10.md`), the nine other round-one reviews, and the machine-verified records in
`experiments/e00`–`e04`. Round-one verdict: BORDERLINE (the strongest of the ten), on a single named
objection. I am the only reviewer who did not pass it.*

---

## Was my objection closed

**Yes. Both of them, and better than I asked.**

My round-one BORDERLINE rested on one sentence: *"a headline ranking flip whose primary candidate pair
is separated by 0.5 published mAP, i.e. inside the bootstrap."* I demanded three cheap things
(reviewer10.md, "SURVIVABLE WITH"): paired bootstrap CIs on the **ordering**; an errors-in-variables
correction for the velocity denominator; and that C3 be narrowed or demoted from "prediction" to
"reference point."

Verified in the revision, item by item:

1. **The flip is gone from the thesis and from the pre-registered table.** v1's P6 (`|ΔAP| < 1.5` and
   `|ΔAP^⟂| > 2.5`) is deleted, not softened — I diffed the prediction tables. The thesis sentence now
   carries an explicit paragraph, *"What this thesis no longer promises,"* naming my objection and
   conceding it. §4.5 specifies the procedure in full: sequence as the resampling unit (correct — it is
   the exchangeable unit, and no one else in this round got that right), `B = 10 000`, paired
   resampling with both methods scored on the same resample, the ordering probability
   `P(ΔAP^(b) > 0)` reported, a flip claimable only at `P(order|AP) ≥ 0.95` **and**
   `P(order|AP^sync) ≤ 0.05`, a pre-registered pair list capped at 12, and Holm–Bonferroni. Under that
   rule the RVT-B / S5-ViT-B pair I killed **cannot** produce a flip claim. They also retract v1's
   Death-1 mitigation "maximise the pool," which was the instinct that manufactured the multiplicity
   problem. That is the correct retraction and it was not forced by me.
2. **The EIV problem I named as "the fatal flaw the team has not named" is now named, and the fix is
   better than my prescription.** Three estimators printed side by side; `τ̂_naive` demoted to an
   explicit lower bound in magnitude; `λ_att` printed per dataset; the `‖v*‖·τ_max > 2 px` filter's
   retained fraction and the speed distribution of the *discarded* set published, which is the
   second-order bias I flagged and which they now report rather than mitigate silently; and C4 re-pointed
   at the denominator, which is exactly what I asked for. The instrument — velocity from a **disjoint
   earlier label pair** `(t−2Δ, t−Δ)` — is a valid IV: measurement noise is independent across disjoint
   differences while true speed is autocorrelated. That is the right instrument and I did not think of it.
   They also correct me, and they are right: on Gen1 the dominant term is **velocity smoothing bias**
   (a central difference at Δ = 250 ms returns the mean velocity over 500 ms), which is correlated with
   acceleration and which Deming does not fix. My diagnosis was directionally correct and mechanically
   imprecise, and the paper says so in print rather than in a rebuttal.
3. **C3 was not narrowed; it was rebuilt into the stronger thing.** It is now the Panel C regression of
   measured `τ̂` on measured `w_P`, with a slope, a CI and a pre-registered interval, plus E1b's per-bin
   occlusion converting `t − 25 ms` from arithmetic on a config into a measured influence centroid.
   That is a better answer than "demote it," and it is R3's own stated standard.

Also creditable, and I will say it once so it is on the record: LET-3D-AP is installed as first row,
named ancestor **and** precedent, with the novelty self-score cut 7 → 5.5 in the paper rather than in a
rebuttal; `AP^⟂` is met with *"we do not answer this; we comply with it"*; `τ_max` takes
`min(w_P^decl, w_P^meas)` so the correction can never flatter the authors; the simulator, the 1 Mpx arm,
the MultiFlow fallback and BS-ERGB are deleted rather than defended; and `experiments/e04` closes R4's
"fatal flaw" with a measurement, which the record supports.

I have no residual claim on the ranking flip or on the denominator. Anything else I say below is a new
objection, and I will mark it as such rather than pretend it was implied.

---

## The new killing review

> The revision solved my problem by moving the paper's primary `τ̂` testbed from Gen1 to DSEC-Det,
> because DSEC-Det has 20 Hz labels with track IDs and therefore the smallest errors-in-variables
> problem in the plan. That move is correct as statistics and it is fatal as physics, because
> **DSEC-Det's inter-frame ground truth is, by the authors' own sentence and by this paper's own E0,
> linear interpolation.** The paper now measures its headline quantity against the labels its floor
> experiment exists to discredit, and it does not notice.
>
> Work the sign out. Between two 20 Hz anchors the released label `c*_lin(t)` is the chord of the true
> image trajectory. DSEC is a driving dataset; image trajectories under approach are **convex**, so the
> chord runs ahead of the truth in the direction of motion for the whole interior of the interval, and
> meets it exactly at the anchors. A *perfect* detector — zero latency, zero spatial error — therefore
> produces `e_∥ < 0` everywhere inside the interval and `e_∥ = 0` at the anchors. Divide by `‖v*‖` and
> you have a systematically negative `δ̂` that is zero at each RGB frame, grows across the interval, and
> resets. **That is the sawtooth.** E3 pre-registers the sawtooth as the paper's mechanistic signature
> and says *"a sawtooth synchronised to the frame clock is a signature no spatial explanation can
> produce."* It is not a spatial explanation. It is the label construction, it has the right period, the
> right phase, the right reset, and the right sign, and the paper documents its existence three sections
> earlier as the reason E0 is worth running. One artifact forges the paper's one unforgeable signature.
>
> It does not stop there, and this is why it is the killing review rather than a caveat. The same
> interpolation term feeds all three surviving headline results:
> (i) it enters `τ̂` on the primary testbed with a systematic sign that agrees with the hypothesis;
> (ii) it is **frame-phase-coherent** — every object in one inter-frame query shares the phase and
> scales it by its own trajectory curvature — so it inflates within-output dispersion **and passes the
> permutation null of §4.6**, which permutes objects across frames and therefore across phases;
> (iii) it is speed- and curvature-correlated, so it concentrates in the top-`M` decile, which is the
> headline slice. On my arithmetic it is worth a few tenths of a millisecond on a distant static object
> and of order 3–5 ms on a near, fast, laterally-crossing one. That is small against the 25 ms
> hypothesis and it is the **same size as the entire quantity the paper has just moved its importance
> onto.**
>
> Which brings the second barrel. The revision concedes the bias half outright — *"a reporting problem,
> not a research problem"* — because R7 showed 25 ms is 34.7 cm at 50 km/h and is cancelled for free by
> a Kalman step once declared. The paper's importance now rests on `σ_τ`, pre-registered at
> `σ_τ,excess ≥ 3 ms`. Run the paper's own conversion, which it adopted from R7 and promises to print in
> centimetres: **3 ms is 4.2 cm at 50 km/h and 10.8 cm at 130 km/h.** The paper has conceded 34.7 cm as
> a reporting problem and relocated its claim to importance onto 4.2 cm. If the large effect does not
> matter, the effect one-eighth its size does not matter more. This is not a framing complaint; it is
> the paper's own two numbers on the same axis, and it is the first question an AC will ask.
>
> And `σ_τ`, the quantity now carrying the paper, has its null specified backwards — in one of the two
> places it is specified. §4.6: *"If within-frame dispersion is not detectably smaller than this
> across-frame dispersion, there is no frame-level clock coherence, `σ_τ` carries nothing, and we drop
> it (K5)."* P8 and K5 say the opposite: `σ_τ,excess` must **exceed** the permutation null. Those are
> contradictory inequalities on the same criterion, and the §4.6 direction — the one with the reasoning
> attached — is worse than a typo, because in that direction **the test passes exactly when the claim is
> false.** Within-frame dispersion being significantly *smaller* than across-frame dispersion is the
> statement that objects in one output tensor **do** share a clock — which is precisely R7's position,
> which the paper has already conceded, and which makes a declared scalar `(c_P, w_P)` sufficient. The
> instrument, when it fires, refutes the thesis it was imported to save. Team 04's `σ_τ` had no null and
> I killed it for that; this one has a null pointing at its own foot.
>
> Then the estimator that survived as the ranking instrument. `AP^sync` re-anchors by `−τ̂_P · v̂_pred`
> and is scored on the unmodified standard metric — the right shape, and R2's correction that it can go
> down is correctly absorbed. But `τ̂_P` is the least-squares minimiser of the along-track residual
> **fitted on the evaluation set, using ground-truth velocity**, and there is no held-out split anywhere
> in v1 or v2; I grepped for one. Worse, §4.5 states that `τ̂` *"is re-estimated inside each resample."*
> Refitting the correction inside every bootstrap replicate does not price the optimism of in-sample
> fitting — it **reproduces** it 10 000 times, so the CI is centred on the optimistic value and cannot
> detect it. `Δ_clock > 0` is then arithmetic: one scalar per method, fitted to reduce the mean signed
> along-track error, evaluated by the reduction in the mean signed along-track error. That is verbatim
> the sentence I used to kill Team 01's free-lunch scalar in round one, and it now applies here.
> The consequence for the ranking claim is specific: every method gains monotonically in its own fitted
> `|τ̂_P|` and its own along-track error fraction, so the `AP^sync` ordering is a deterministic
> re-ranking by the quantity the authors fit on the test set. The ECCV-2024 calibration precedent the
> paper invokes does not cover this, because there the correction is a published, uniform post-hoc
> method; here its magnitude is tuned per method, on the data it is scored on.
>
> C5, the paper's designated falsification method, is void for the same reason and for a simpler one.
> §6: *"shift every box by `−τ̂_P·v̂_pred` … this must recover most of `Δ_clock` on the unmodified
> standard metric."* §4.4 defines `AP^sync` as that operation and `Δ_clock := AP^sync − AP`. C5 therefore
> requires `AP^sync` to recover `AP^sync − AP`. It is an identity, carried unchanged from v1, and it is
> the control the paper names as the one that could show *"our metric failed its own test."* It cannot.
>
> Panel C, the new headline. Twelve configurations is a headcount, not a design. Six leading-bin masks ×
> three checkpoints, two re-binnings, three query-step subsamplings and seven state truncations are all
> **input ablations of three models trained at a single support**. §4.5 argues, correctly, that
> detections within a recording are not exchangeable and the unit must be the sequence; by exactly that
> logic, nine masked variants of one checkpoint are not nine predictors, and Panel C's effective `n` is
> three trained models plus five heterogeneous cross-family points. The CI quoted from twelve points will
> be anti-conservative by roughly the factor the paper's own bootstrap section exists to avoid.
> And the levers are not neutral. Query-step subsampling from 20 Hz to 6.7 Hz is not a support
> manipulation: it is the inference-frequency change that **Zubić et al., CVPR 2024** — item 2 of my own
> round-one comparison set, and one of this paper's own checkpoints — demonstrated collapses RNN and
> Transformer event detectors by more than 20 mAP. Re-binning two stored 50 ms windows into ten 10 ms
> bins hands the network a tensor with different per-bin statistics and different bin semantics. Masking
> nine of ten bins does not produce a detector with a 5 ms support; it produces a broken detector, and
> `τ̂` estimated from a broken detector's boxes is `τ̂` of a different predictor. The paper's own control
> — *"report mAP at every mask so the reader sees the damage"* — guarantees the reader sees it. The
> declared fallback if the OOD confound bites is *"restrict the axis to the cross-family points from
> E2/E3"*: that is five points spanning optical flow and detection across DSEC-Flow, MVSEC and DSEC-Det,
> whose dominant variance is dataset identity — which is Death 3, the confound Panel C exists to
> resolve. The fallback is the objection.
>
> §8.6 argues the within-checkpoint design is *"the better experiment, not merely the cheaper one."*
> It is not. The reporting contract the paper proposes to the community is a **between-subject** claim:
> declare your `(c_P, w_P)` and a reader can predict your `τ̂`. Only predictors actually trained at those
> supports test it. A 50 ms-trained network fed a 10 ms window cannot compensate; a 10 ms-trained one
> learns to. The paper's reasons for not retraining (raw GEN1 is form-gated, RVT's own budget is ~2 days
> on an A100) are correct, well-evidenced and decisive — but they establish that the between-subject
> experiment is **unaffordable**, not that the within-subject one answers the question.
>
> Finally, two things the revision made worse, which a hostile reviewer is obliged to check. v1's P7 read
> *"median IoU > 0.9"* and *"recovers ≥ 60 %"*; v2 reads *"> 0.85"* and *"≥ 50 %"*. Both pre-registered
> thresholds moved in the direction that makes the prediction easier to satisfy, between rounds, with no
> stated reason, on the one prediction that carries the paper's floor. Pre-registration whose numbers
> relax under review is not pre-registration. And v2's falsification clause for P7 is a **conjunction**
> of three failures (`IoU < 0.75` **and** causal recovery `< 25 %` **and** the DSEC-Det identity check
> inverting), leaving a wide band — IoU 0.75–0.85, recovery 25–50 % — in which P7 is neither confirmed
> nor falsified. Second: v1's E0 on DSEC-Det was a measurement (*"median IoU between released GT and the
> linear oracle"*); v2 converts it into *"an identity check, not a statistic"* — verifying that a file
> matches a sentence its own authors published about it. In round one I wrote that *"quoting a
> limitations section back at its authors is not a result; measuring the size of the effect is. Team 08's
> E0 is exactly that measurement, and that is the only reason it is not vacuous."* On DSEC-Det, the
> revision has moved E0 in the direction I named as vacuous. The real measurement now lives entirely on
> DSEC-3DOD, where refinement actually occurred — one dataset, one 40 GB download.
>
> **The structural finding.** Audit the eight kill criteria against the outcome space. K1 vacuous
> anisotropy → E0 + reporting contract. K3 `τ̂` indistinguishable from zero → E0 + `σ_τ`. K4 null slope →
> retitle to the dataset branch. K5 `σ_τ` inside its null → drop it, the paper survives. K6 E0 inverts →
> *"a real positive control and worth a paragraph."* K7 prior art → collapse to E0 + contract + `σ_τ`.
> K8 fires only if fewer than three of four items *"exist as finished figures"* — and a null `τ̂` with a
> CI is a finished figure, as is a flat Panel C. **There is no scientific outcome that stops this paper.**
> For a measurement I would defend that; I defended exactly that in round one when I wrote that E0 cannot
> fail. But the thesis sentence still makes three claims — that `τ̂` is (i) large, (ii) predictable from
> measured `w_P`, (iii) not a single number per output — and K3, K4 and K5 negate them one each while the
> paper survives all three. A measurement is allowed to read zero. A *thesis* that reads the same whatever
> the instrument says is not robust; it is unfalsifiable, and the difference is the whole of my job.

---

## What I verified vs took on trust

**Verified directly.**
- Old P6 is absent from v2's prediction table (diffed `team08.md:66` region against `team08_v2.md`
  §"Quantitative predictions"). The flip appears only in §4.4 and only under `AP^sync`.
- §4.5's bootstrap specification is present in full and its flip rule is arithmetically incompatible with
  a 0.5 mAP separation.
- No held-out or disjoint split for fitting `τ̂_P` exists anywhere in v1 or v2. The only occurrence of
  "disjoint" is the IV instrument. §4.5 explicitly refits the EIV estimate inside each resample.
- C5's text is byte-identical in v1 (`team08.md:244`) and v2, and `Δ_clock` is defined as
  `AP^sync − AP`, making C5 self-referential.
- The §4.6 permutation-null direction ("not detectably smaller") contradicts P8 and K5 ("exceeding its
  permutation null"). All three describe K5.
- P7 thresholds moved 0.9 → 0.85 and 60 % → 50 % between v1 and v2; v2's E0 step 1 is restated as an
  identity check.
- `experiments/e04` supports the toolchain correction: zero missing / zero unexpected keys, forward pass
  runs, `pytorch-lightning` never installed. Their "reviewer corrected" entry against R4 is legitimate.
  So is the pointed caveat they keep: reproduction of published mAP is **not** established, and they
  make it a gate (K2) rather than a step.
- `experiments/e03` supports the `σ_τ` provenance argument: the full FE108/FE240hz release with 240 Hz
  Vicon GT is application-gated, and Team 04's version of `σ_τ` needed exactly that. Their attribution of
  the zero-byte HTTP 416 on `fe108.dluticcd.com` to R4 is correct (`reviewer04.md:533`).
- `experiments/e00`/`e01` support their objection-D answer: their `w_P` lever is the event window, not the
  exposure, so the "wide support and varying support do not co-occur in DSEC" constraint does not bind
  them. They carry E01's caveat verbatim and make no displacement claim. Correct.
- Nine other round-one reviews checked for objections I did not raise. R6's recurrent-support objection is
  answered by E1c as a first-class experiment; R8's three-way `τ̂` attribution by E1b's occlusion profile
  plus the (dataset, method) variance decomposition; R2's `AP^sync` monotonicity error, R2's Gen1 `w_G`
  free-parameter point, R1's non-monotone constant-count support, R9's "dominant on 5 %", R8's scoping
  and "purely a timing gap", the unsourced MVSEC claim, and R5's FAOD-is-a-preprint point are all
  corrected in place and verifiable in the text.
- **R3's objection that the GT for `τ̂` is a zero-acceleration interpolation is the one residual
  objection from the round-one set that the revision does not answer.** v2 cites that finding only to
  argue `σ_τ` survives on interpolated tracks; it never applies it to `τ̂` itself — and the revision made
  it worse by promoting the interpolated dataset to primary. That is the spine of my killing review above.

**Taken on trust.**
- That E1b's stacked histogram is additive in bins (they schedule a week-1 check; if it fails, two Panel C
  levers vanish).
- The numeric magnitudes in my convexity argument: the *sign*, *phase* and *frame-locking* of the
  interpolation-induced `δ̂` follow from convexity and the chord construction and I stand behind them; the
  0.3–5 ms range is my estimate from plausible curvatures, not a measurement, and the authors can and
  should measure it directly.
- Every published number quoted from LET-3D-AP, Ev-3DOD, DSEC-Det and 1 Mpx. R5's sweep is the record for
  the prior-art claim and I did not re-run it.
- The 40 GPU-h budget and the `< 7 GB` VRAM ceilings.

---

## Verdict

**ACCEPT.**

My round-one objection is closed in full, and the two additional fixes I demanded were delivered better
than specified. If I held BORDERLINE now, it would be on grounds I did not raise in round one, against a
team that converted my stated objection completely — that is goalpost-moving, and I would condemn it in
any other reviewer. The revision is also, on the round's own criterion, more certain than it was: the
toolchain risk is closed by a measurement, the gated and dead datasets are off the critical path, the
budget fits, and the critical path is now honestly named as the reproduction gate rather than as
bandwidth.

I accept it as an **evaluation and reporting paper whose figures will exist**, not as a paper with a
result. It is a poster, not a highlight, and the authors' own 5.5/10 novelty score is the honest number.

Four things are conditions, not suggestions, and three of them are one-liners:

1. **Estimate `τ̂` at the 20 Hz anchor times, where the DSEC-Det labels are real annotations, and report
   the inter-frame `τ̂` separately with the chord-interpolation term modelled.** Until that split exists,
   the sawtooth is not evidence and the primary `τ̂` is measured against a constant-velocity model. This
   is the one I would escalate to REJECT on if it is unaddressed at submission.
2. **Fit `τ̂_P` on a disjoint split and apply it to the scored split**, and stop refitting it inside the
   bootstrap. Then `Δ_clock` is a result rather than a residual with its mean removed, and C5 becomes a
   test that can fail. Rewrite C5 so it is not `AP^sync` recovering `AP^sync`.
3. **Fix the direction of `σ_τ`'s permutation null and reconcile §4.6 with P8/K5**, and state which
   inequality corresponds to the claim — because as written, the version with the reasoning attached
   passes only when a declared scalar timestamp is sufficient, which is the position the paper concedes.
   While you are there: state the `σ_τ` number in centimetres next to the `τ̂` number in centimetres, in
   the same table, and defend the ratio in the introduction rather than letting a reviewer compute it.
4. **Report Panel C's regression with the trained model, not the masked variant, as the unit** — an
   effective `n` of three, plus five cross-family points, with a CI that says so. Twelve points from
   three checkpoints is the same anti-conservatism §4.5 exists to prevent.

None of these costs GPU time. All of them are rebuttal-fixable, which is precisely why this is ACCEPT and
not BORDERLINE.
