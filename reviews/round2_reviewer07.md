# Round 2 — Reviewer 07 (robotics, deployed perception) on Team 08 v2

*Same axis as round one: suppose you are completely right — what changes, and by how many centimetres or
milliseconds? Round one I gave this STRONG ACCEPT and then wrote the objection the authors split the paper
on. This round I check whether the split rescues it.*

**Read:** `reviews/reviewer07.md` (my round one), `ideas/team08_v2.md` (887 lines), `experiments/e00`–`e04`
including E01's new night sequence.

**Standing assumptions, restated so every number below can be redone.** `f ≈ 550 px` for the DSEC event
camera (~60° HFOV over 640 px). Detector box-centre noise `σ_det = 3 px`, which is the scale at which these
detectors are matched at IoU 0.5. Steady-state 1-D constant-velocity filter with prior variance `P⁻ = R`.
2-D validation gate at 99 % (`χ²₂ = 9.21`). DSEC-Det density from the paper's own §8/E3 line: 390 118 boxes
over 70 379 frames = **5.543 boxes/frame** on 640×480 = 307 200 px².

---

## Is dispersion cancellable too

Short answer: **not cancellable, but not expensive either — at the magnitude the paper pre-registers.**
A filter does not need to cancel `σ_τ`. It needs to *afford* it, and at `σ_τ = 3 ms` it can.

### The magnitude, in the units I used in round one

`σ_τ = 3 ms` is the paper's own pre-registered threshold (P8, K5). World-frame position dispersion is
`σ_x = σ_τ·v_rel`:

| platform | `v_rel` | `σ_x` at `σ_τ = 3 ms` | for comparison: the conceded bias, 25 ms |
|---|---|---|---|
| warehouse forklift | 1.5 m/s | 0.45 cm | 3.8 cm |
| urban car | 13.9 m/s (50 km/h) | **4.17 cm** | **34.7 cm** |
| highway car | 27.8 m/s (100 km/h) | 8.34 cm | 69.5 cm |
| autobahn | 36.1 m/s (130 km/h) | 10.8 cm | 90.3 cm |
| obstacle-avoiding quadrotor | 5 m/s | 1.5 cm | 12.5 cm |
| racing quadrotor | 20 m/s | 6.0 cm | 50 cm |

**The decisive ratio, and it is arithmetic.** The paper conceded a 25 ms bias as free to fix and moved its
importance onto a 3 ms dispersion. `25/3 = 8.3`. Against the interval the system has already accepted by
choosing a 20 Hz camera, my round-one comparison was 25 ms against 50 ms — a factor of **two**. The new
headline is 3 ms against 50 ms — a factor of **16.7**. *The paper answered "your effect is half of what the
system already tolerates" by relocating onto an effect that is one-sixteenth of what the system already
tolerates.* That sentence will be written by some reviewer; better it is this one, in round two, where it
can still be acted on.

### What 3 ms costs a real association step

Image speeds at the geometry from my round-one table, and the resulting dispersion in pixels:

| target | image speed | `σ_τ·‖v‖` at 3 ms | `α = 1+(σ_t/σ_det)²` | excess RMS of a CV filter with `R` unmodelled | 99 % gate rejection (nominal 1 %) | IoU cost on a matched box |
|---|---|---|---|---|---|---|
| car 8.3 m/s @ 15 m (w = 165 px) | 0.304 px/ms | 0.91 px | 1.093 | **+0.10 %** | 1.5 % | 0.989 |
| ego-flow, 100 km/h, Z = 10 m, r = 200 px | 0.556 px/ms | 1.67 px | 1.309 | **+0.91 %** | 3.0 % | — |
| cyclist 6 m/s @ 5 m (w = 66 px) | 0.660 px/ms | 1.98 px | 1.436 | **+1.64 %** | 4.0 % | 0.942 |
| pedestrian 1.5 m/s @ 10 m (w = 40 px) | 0.083 px/ms | 0.25 px | 1.007 | +0.00 % | 1.0 % | 0.988 |

Three readings, all of which the paper needs to absorb.

1. **The state estimate barely moves.** Leaving `σ_τ = 3 ms` entirely unmodelled costs a constant-velocity
   filter between **0.10 % and 1.64 % of RMS position error** across the whole realistic geometry range. The
   reason is second-order: the Kalman gain sits at a minimum of the MSE, so a gain error of a few percent
   costs a fraction of a percent of variance. This is not a tuning accident; it is why filters are robust to
   mis-specified `R` in the first place.
2. **The gate *is* the visible cost, and it is the cheap one.** Gate rejection triples in the worst geometry
   (1 % → 4 % for the close cyclist). That is a real, measurable tracker degradation and I will credit the
   paper for it. But it is fixed by *widening the gate* — no knowledge of `σ_τ` required, a blanket factor
   of 1.5 on `R` suffices — and at DSEC-Det object density the cost of that widening is: mean object spacing
   118 px, a 99 % gate of area 260 px², expected competing objects **0.0047 → 0.0067**, i.e.
   **two extra ambiguous associations per thousand.** That is the AC's question answered exactly: the
   tracker widens its gates and carries on, and the bill is 0.2 %.
3. **No match flips.** For equal boxes displaced by `s` along width `w`, IoU = `(w−s)/(w+s)`. Falling below
   IoU 0.5 needs `s = w/3`: 22 px on the cyclist (**33 ms**, 11σ) and 55 px on the car (**181 ms**, 60σ).
   Even at the 3σ tail (9 ms) the cyclist sits at IoU 0.835 and the car at 0.967 — above every threshold in
   use. **`σ_τ = 3 ms` cannot flip a single IoU-0.5 match at any tail worth naming.** I checked the tail
   before dismissing a variance claim on its mean, which is the minimum owed to a dispersion argument.

### The threshold the paper should have pre-registered

Inverting the filter arithmetic: unmodelled dispersion costs **10 % of RMS position error** at `α = 2.43`,
i.e. `σ_τ·‖v‖ = 3.59 px`. In milliseconds that is **5.4 ms on a close cyclist, 6.5 ms on peripheral ego-flow
at 100 km/h, and 11.8 ms on a crossing car**. The paper pre-registers 3 ms. It is pre-registering an effect
**two to four times below the level at which a downstream filter would notice it**, and K5 therefore has a
pass condition that a robotics reader will read as a null.

### The dilemma the paper has not posed

My bias argument was that a *declared constant* is free. The authors' reply is that a dispersion is not a
constant. True, and insufficient, because dispersion splits:

- **If `δ̂_i` is predictable from something the deployer observes** — the object's own speed, size, branch
  visibility — then it is a per-object offset that is a *function of an observable*, and the paper's own §6
  re-anchoring (`ĉ ← ĉ − τ̂_P·v̂_pred`, using the method's own per-track velocity) already removes part of
  it. That is the bias fix with a vector where there used to be a scalar. Still declarable, still free.
- **If `δ̂_i` is not predictable from any observable**, it is zero-mean noise, and inflating `R` is the
  textbook response, priced above at 0.2 %.

The interesting middle — predictable, but only from something the deployer cannot see — has to be
*demonstrated*, not assumed. §4.6 does not attempt it. This is the load-bearing gap in the variance half.

### Two technical faults in the `σ_τ` machinery

**(a) The permutation null tests the wrong direction.** §4.6: "*If within-frame dispersion is not detectably
smaller than this across-frame dispersion, there is no frame-level clock coherence, `σ_τ` carries nothing.*"
Passing that test establishes that a **per-frame common component exists** — which is the *declarable*
quantity, one scalar per output tensor, exactly the reporting contract. The claim `σ_τ` is supposed to
support is the opposite: that within-frame spread is large enough to defeat a declared scalar. The
permutation null is a sound estimator sanity check (it shows `δ̂_i` is not pure noise) and it is *necessary*;
it is nowhere near *sufficient* for the "so what", because it says nothing about magnitude in filter units.
K5 as written can pass while the paper's importance argument fails. Both tests must be run and reported
separately.

**(b) `σ_τ,excess` is a difference of two comparable quantities and the subtrahend is estimated the wrong
way.** `δ̂_i = e_∥,i/‖v*_i‖`, so per-object estimator noise is `σ_c/‖v*_i‖`. At `σ_c = 1.5 px`:
2.3 ms on the cyclist, **4.9 ms on the crossing car**, 18.2 ms on the pedestrian. For the crossing-car
population — the bulk of DSEC-Det — the estimator noise **exceeds the 3 ms effect being sought.** The
sensitivity, with the car geometry and a true `σ_τ = 3 ms`:

| assumed `σ_c` | measured var | subtracted | `σ_τ,excess` reported |
|---|---|---|---|
| 1.2 px | 33.3 ms² | 15.5 | **4.21 ms** (40 % above truth) |
| 1.5 px | 33.3 ms² | 24.3 | 3.00 ms (truth) |
| 1.8 px | 33.3 ms² | 35.0 | **0 ms** (no effect) |

**A ±20 % error in `σ_c` takes the headline from "no effect" to "40 % above the pre-registered threshold."**
And the paper's plan for `σ_c` — "*to be measured in week 3 from track residuals*" — is the one estimator
that is guaranteed biased: residuals of an anchor against the interpolated track that *that anchor defines*
are shrunk, `σ_c` comes out low, and the bias runs **in the paper's favour**. `σ_c` needs an independent
estimate (left/right reprojection, or a held-out anchor excluded from the interpolation).

Relatedly, the `‖v*‖·τ_max > 2 px` filter does not protect this. On DSEC-Det `τ_max = (50+50)/2 = 50 ms`,
so the filter is `‖v*‖ > 0.04 px/ms` — it retains the pedestrian at 0.083 px/ms, whose `σ_δ̂` is 18 ms. The
speed floor must be stated in `σ_δ̂` units (keep objects with `σ_c/‖v*‖ < 3 ms`, i.e. `‖v*‖ > 0.5 px/ms`),
with the retained fraction of DSEC-Det published.

### The mechanism that would make me wrong, which the paper has not claimed

There is a version of the variance argument that survives everything above, and Team 08 has the two
measurements that pin it and has not connected them:

- **E00 measured** that DSEC's published image timestamp is the average of the left/right mid-exposures
  **to within 1 µs**. So the *frame* branch's information centroid sits at the label time: `c_frame ≈ 0 ms`.
- **E02 measured** that RVT's window is `[t−50, t]`, so the *event* branch's uniform-weight centroid is
  `c_event = −25 ms`.

For a genuinely fused predictor (DAGr), an object resolved mainly by the frame branch has `δ̂ ≈ 0` and one
resolved mainly by events has `δ̂ ≈ −25 ms`. If the per-object mixing weight `p` varies across a frame's
objects — which is what a night scene with some well-lit large objects and some fast dark ones *is* — then
`σ_τ`'s natural scale is not 3 ms. For `p` spread over [0,1] it is `25/√12 = **7.2 ms**`. Priced in my
table above: at 7.2 ms the close cyclist costs **+20.5 % RMS and a 27 % gate rejection rate**. That is
unmistakably measurable, unambiguously not cancellable by a scalar, and it is a real fused-stack regime.

**The paper's variance claim is worth a CVPR paper at 7.2 ms and is not worth a paragraph at 3 ms, and the
difference is which mechanism produces it.** §4.6 names no mechanism at all.

---

## Does conceding the bias half gut the paper

**The concession itself is correct, honest, and not fatal.** Conceding a phenomenon's *fix* is not conceding
the phenomenon, and the fix requires a number nobody has published. That is a legitimate paper shape with
in-venue precedent the authors already cite: TIDE concedes every error type it names is fixable; EVREAL
concedes every metric it re-runs is standard. Both are cited work. And putting my 25-vs-50 ms comparison in
the *introduction* rather than burying it is the correct handling of a reviewer objection you accept.

**What is damaged is not the honesty; it is the sequencing.** A CVPR reader who reads "this is a reporting
problem, not a research problem" in §1 asks immediately what the research problem is, and the answer arrives
as `σ_τ`, which by the section above is 8.3× smaller in the same units on the same platform. The paper
concedes the large effect and offers a smaller one in its place. The direction of that trade is visible from
the abstract.

**But the paper's best result is on neither side of my bias/variance split, and it is filed as the floor.**

E0. The claim that DSEC-Det's inter-frame ground truth *is* the linear interpolation of its 20 Hz anchors,
that DSEC-3DOD's is mostly so, and that a **causal, sensor-free constant-velocity extrapolator recovers
≥ 50 % of the published event method's inter-frame advantage** (P7). Properties, all of which I checked
against the plan:

- Not conceded, and not touched by my round-one objection at all.
- Not small. If it lands, half the advertised inter-frame benefit of the *Nature* 2024 low-latency result —
  the single strongest deployed event-vision result in my round-one comparison set — is available from a
  motion model with no event camera, measured on that benchmark's own protocol. My round-one comparison-set
  finding was that the Nature benefit is stated in **bandwidth and latency**, not temporal-support
  correctness. E0 is the first measurement that puts a denominator under the headline. That is
  procurement-grade, which is the same standard on which I called Team 10's `EU(s)` inversion consequential.
- Zero prior art in R5's targeted sweep (`all:"ground truth" AND all:"interpolation" AND all:"event camera"
  AND all:"benchmark"` → 0).
- Costs a 4.7 MB label file and zero GPU, and is decidable **2026-09-07**, in week one.
- The paper's own §Death-5 "next idea if the decomposition is taken" *is* E0 promoted; K1, K3 and K8 all
  fall back to it. The authors already know where their floor is. They have not noticed it is their ceiling.

**Two kinematic facts I can supply for free that the paper should be using and is not.** Over the anchor
interval Δ = 50 ms, the constant-velocity prior's own error is `(1/8)aΔ²`: at a = 8 m/s² (hard braking) that
is **2.5 mm, or 0.14 px at 10 m**, and for the causal forward extrapolation `(1/2)aΔ²` it is **10 mm,
0.55 px**. So (i) DSEC-Det's inter-frame labels *cannot* carry meaningful information beyond a
constant-velocity prior at 50 ms for rigid vehicles — P7's first clause is near-certain by kinematics, not
by luck; and (ii) P7's ≥ 50 % threshold on the causal test is **conservative** — the extrapolator should
recover nearly all of the frozen-at-`t=0` gap on rigid objects, and only articulated pedestrians and
cyclists can break it. Argue P7 as physics with a measurement attached rather than as a hope, predict
higher, and be judged on it.

**Verdict on this question:** the concession does not gut the paper. It reveals that the paper's headline is
on the wrong experiment. The importance argument was moved from bias to variance when it should have been
moved from bias to E0.

---

## Where the effect actually lives on real hardware

### The bias half: unconditionally operational, and the paper's re-anchoring of it is the right call

§Response-D states that the paper's `w_P` lever is the **event window, not the exposure**. That is correct
and it is the most consequential single sentence in the revision for my axis. The 50 ms stacked histogram is
a *method configuration*, chosen by the deployer, present on any hardware, and — as I wrote in round one —
producing an offset at every speed including zero relative motion. It is entirely untouched by DSEC's
exposure bimodality, by the AE ceiling, and by my round-one criticism of Teams 01/05/10. My round-one
"OPERATIONAL, unconditionally" stands.

It also means my E00 finding cannot be used against this paper the way it was used against Team 01, and I
say so explicitly so the AC does not double-count it.

### The variance half: regime unstated, and the two candidate mechanisms land in opposite places

`σ_τ` can arise three ways, and the paper distinguishes none of them.

**(a) Exposure-driven (the RGB branch of DAGr).** This one E00 kills, and it kills it in exactly the shape I
found in round one. In the six ceiling sequences the exposure is **14996 µs on every frame, both cameras
identical, exposure starts identical to the microsecond in 7080/7080 frames** — so the exposure contributes
a per-sequence **constant**, which DSEC already publishes in a text file, and which is declarable and free.
In the daytime sequences the exposure genuinely varies 12.5× but its absolute width is 337–4207 µs, giving
**0.1–1.3 px** of object displacement, below `σ_det = 3 px`. **There is no DSEC regime in which the
exposure-driven component of `σ_τ` is both varying and large.** That is E00's recorded tension applied to
this paper's new headline, and §Response-D sidesteps it by pointing at the event window — which is a valid
answer for the bias half and *not* an answer for `σ_τ` if `σ_τ`'s mechanism is the exposure.

**(b) Event-window-driven (per-object information centroid inside the 50 ms window).** Regime-independent,
exists at all speeds — and this is the branch I priced above at 0.25–2.0 px and under 1.7 % RMS.

**(c) Cross-branch (per-object variation in which branch dominates).** Operational — this *is* what a
deployed event+RGB stack looks like — and the only branch with a magnitude worth the paper's weight
(7.2 ms, +20 % RMS, 27 % gate rejection). E00 and E02 have already measured the two centroids that set its
scale.

**A note on E01, since the AC flagged it.** E01's night measurement — 310 320 events inside one exposure on
38.2 % of pixels at 2.60 crossings per firing pixel, against 20 616 / 6.0 % / 1.10 in daytime — is a real
and well-run measurement, and E01's own carried-forward caveat is correct and correctly repeated in the
paper: *crossings per firing pixel is not a displacement measurement.* But note what it measures: activity
inside the **exposure** (1.5–15 ms). The paper's lever is the **50 ms event window**. In §Response-D, E01 is
therefore cited in support of a quantity it does not measure. The paper says it cites E01 "only to establish
that intra-exposure evidence is substantial," which is honest, and the correct conclusion is that **E01 is
decoration in this paper, not evidence.** It is evidence for Teams 05 and 06.

**The inversion the paper is missing.** In round one I used DSEC's bimodality as a *criticism* — a bimodal
covariate makes Team 10's Panel C uninterpretable and makes Team 01's latent a published constant. For
*this* paper the same bimodality is a gift: a covariate with no mass between 5 ms and 15 ms is a bad
continuous regressor and an excellent **two-level treatment factor**. 32.5 % of DSEC train frames sit at
14996 µs, the rest below 5 ms, nothing between. `σ_τ` under mechanism (c) should be *largest* in the night
stratum, where a 15 ms exposure blurs the frame branch most and per-object branch dominance therefore varies
most. **Stratify `σ_τ` day vs night and the paper gets a mechanism test for free, on data it is already
downloading.** §Response-D currently treats E00 purely as a constraint to avoid. One check required first:
which of DSEC-Det's 60 sequences sit at the AE ceiling — E00 covers 18 DSEC train sequences and finds 6, but
DSEC-Det adds new sequences and that composition has not been measured.

### On deployed hardware, restated

Production automotive cameras run fixed exposure or hardware-triggered global shutter precisely so the
integration window is known. So mechanism (a) is a property of a research dataset's auto-exposure loop, not
of a deployed rig — the same judgement I passed on Team 01, and it applies here for whichever fraction of
`σ_τ` turns out to be exposure-driven. Mechanisms (b) and (c) are properties of the *method*, survive on any
hardware, and are the ones worth measuring.

---

## Was my objection closed

**On the bias half: closed by concession, and the concession is complete and correctly placed.** Death 4
quotes my argument accurately, including the 25-vs-50 ms comparison and the Kalman-cancellation point, and
the paper states in its own introduction that this half is a reporting problem. `τ̂` in cm via DSEC's
`lidar_imu` is adopted (E3). My round-one fix (ii) is done. Nothing further is owed.

**On my round-one *fatal flaw*: genuinely closed, and better than I asked for.** I wrote that `w_P` has zero
variance across the method set because RVT-{T,S,B} and S5-ViT-{B,S} all consume `stacked_histogram_dt=50_
nbins=10`, that C3 therefore cannot discriminate, and that the escape rested entirely on two checkpoint
pairs (BFlow `E`/`E+I`, E-RAFT 20/45 Hz) — "thin and it is the whole bet." E1b's leading-bin masking gives
`w_P ∈ {5,…,50} ms` on a single fixed checkpoint, re-binning extends to 100–150 ms, and query subsampling
adds the downward frequency arm: **a 30× within-subject range with zero training.** That is a better
instrument than the between-subject pair I recommended, because it is not confounded by three retrainings'
worth of optimisation noise and it cannot come back empty for want of two checkpoints agreeing. The
OOD confound is real and the trailing-bin symmetry control is the right one: masking leading bins moves the
retained-mass centroid later, masking trailing bins moves it earlier, and slope ≈ 1 in **both** directions
with comparable mAP damage separates support from OOD damage. My fatal flaw is retired.

**On my §0 finding (FE108/FE240hz):** E03 corrects the review record — the host answers, the *full* release
with 240 Hz Vicon GT is application-gated, and a preprocessed val/test split is open. My round-one §0 was
too strong in mechanism and right in consequence for the four teams that staked their primary figure on the
240 Hz GT. This paper never depended on it, which was part of why it won round one, and `σ_τ` migrating from
Team 04 to Team 08 is a genuine rescue of a quantity from a dataset death.

**On my seven-paper finding — none of seven deployed event-vision results reports a benefit from getting
temporal support right: the revision confirms it, and says so.** Death 4 reproduces the finding, names all
seven, and concedes that the paper's product for the bias half is "a declared number and a reporting
contract, not a downstream accuracy gain." I checked whether anything *new* in v2 changes the count:

- `τ̂` + declaration + re-anchoring: by construction produces no accuracy gain (the paper says so). It
  removes a defect from a benchmark. It is not a benefit from temporal support.
- `σ_τ`: at 3 ms, priced above at 0.1–1.6 % RMS and 2 ambiguous associations per thousand. Not a benefit.
- E0: the one item that could change a deployment decision — and it is not a temporal-support benefit
  either. It is the *reverse*: a measurement of how much of a published inter-frame benefit is agreement
  with an interpolation prior rather than with the sensor.

So the count stands at **zero of seven, and v2 does not add an eighth.** That is not a fault of the
revision; it is the true state of the field, and the paper is now the only one of the ten that says so in
its own risk section rather than in a rebuttal. Positioning itself as benchmark-integrity and reporting is
the correct response, and it is the ground I said in round one that 08, 06 and 05 stand on more firmly than
the teams promising downstream gains. The paper took that advice literally and completely.

---

## Verdict

**ACCEPT** (round one: STRONG ACCEPT). **Still my #1 of the ten; still my winner for the round.**

The downgrade is one step and I want the AC to read the reason precisely, because it is not a demerit to the
authors. It is *my own round-one finding turning out to be right*. My STRONG ACCEPT was justified in one
sentence — "the only idea in the ten that produces an artifact a deployment engineer uses on Monday" — and
that artifact was the bias half, which I then demolished myself and which the paper now concedes in its
introduction at my insistence. Holding STRONG ACCEPT on a paper whose reason-for-STRONG-ACCEPT I personally
removed would be incoherent. Lowering it because the authors were honest would be worse. The consistent
position is: the verdict is absolute and it moves; the ranking is comparative and it does not.

What earns the ACCEPT, on the record:

- Nine objections answered with measured evidence, three structural changes made (flip demoted, `AP^⊥`
  demoted, LET-3D-AP installed as ancestor and precedent), the novelty self-score lowered 7 → 5.5 **in the
  paper rather than in a rebuttal**, and one reviewer (R4) corrected with an experiment (E04: released RVT
  checkpoint loads under `torch 2.7.1+cu128`, zero missing and zero unexpected keys, no Lightning, one
  working session). This is the best revision behaviour I have seen in ten documents.
- My fatal flaw is closed by a better experiment than the one I proposed.
- Feasibility is still the best in the round: ~40 GPU-h, nothing trained, every checkpoint and byte size
  verified, 405 GB of 990 GB, no dependency that can go dark.
- E0 is a week-one, zero-GPU, no-prior-art result that stands alone and is the paper's real contribution.

What holds it below STRONG ACCEPT:

- The importance argument now leads with a quantity 8.3× smaller than the one it conceded, priced at
  0.1–1.6 % of filter RMS and 2 ambiguous associations per thousand at DSEC-Det density, unable to flip an
  IoU-0.5 match at 11σ.
- `σ_τ`'s physical mechanism is unstated, and its two candidate mechanisms differ by a factor of ~2.4 in
  magnitude and land in opposite regimes.
- The permutation null tests coherence, which is the declarable direction; and `σ_τ,excess` is the
  difference of two comparable variances whose subtrahend is currently planned to be estimated by a method
  that biases it in the paper's favour.
- The headline sits on the metric family; the result sits on E0.

---

## Minimum change to reach ACCEPT

**Not triggered — the paper is at ACCEPT.** What follows is the path back to STRONG ACCEPT, in the order I
would run it. All four are cheap and three are already in the plan under a different name.

1. **Promote E0 to the headline; demote the metric family to the instrument.** The title of the paper is
   currently about the metric; the result is about the ground truth. Death 5's "next idea" — *the ground
   truth is a model* — is the paper. Argue P7 as kinematics with a measurement attached: `(1/8)aΔ² = 2.5 mm
   = 0.14 px` at 50 ms and 8 m/s², `(1/2)aΔ² = 10 mm = 0.55 px` for the causal version, so a
   constant-velocity prior is near-exact at the anchor interval and the ≥ 50 % threshold is conservative.
   Predict higher. Cost: zero, week one, already scheduled for 2026-09-07.

2. **Name `σ_τ`'s mechanism and re-derive its predicted magnitude from the two centroids you have already
   measured.** `c_frame ≈ 0 ms` (E00, mid-exposure average to 1 µs) and `c_event = −25 ms` (E02). For a
   per-object mixing weight spread over [0,1] the predicted dispersion is **7.2 ms**, not 3 ms. Re-register
   P8 at `σ_τ ≥ 5 ms` — the level at which a constant-velocity filter loses 10 % of RMS on a close cyclist —
   and report `σ_τ` in **gate-rejection percentage** as well as ms, because that is the unit in which a
   tracker engineer decides whether to care. Then run the mechanism test: **`σ_τ`(DAGr, fused) vs
   `σ_τ`(RVT, event-only)**. If fused ≫ event-only, mechanism (c) is identified and the variance half is
   decisive. If they are equal, `σ_τ` is estimator noise, K5 fires, and the paper is E0 plus the reporting
   contract — which is the paper anyway under item 1. Either outcome is publishable and it costs one CPU
   pass on runs already budgeted.

3. **Fix the two `σ_τ` statistics faults.** (a) Report the permutation null *and* a separate magnitude test,
   and state in the caption that the permutation result establishes frame-level coherence — the declarable
   direction — and is a sanity check on the estimator, not evidence of un-cancellability. (b) Estimate
   `σ_c` independently of the interpolated track (left/right reprojection, or a held-out anchor excluded
   from the interpolation), publish the sensitivity band, and replace the `‖v*‖·τ_max > 2 px` filter with a
   floor stated in estimator units (`σ_c/‖v*‖ < 3 ms`, i.e. `‖v*‖ > 0.5 px/ms` at `σ_c = 1.5 px`) with the
   retained fraction of DSEC-Det printed. Without (b) a ±20 % error in `σ_c` moves the headline from
   0 ms to 4.2 ms.

4. **Use the bimodality instead of avoiding it.** E00 gives a free two-level treatment factor: 32.5 % of
   DSEC train frames pinned at 14996 µs, the rest below 5 ms, nothing between. Stratify `τ̂` and `σ_τ` by
   that factor. Under mechanism (c), `σ_τ` should be larger in the night stratum; under mechanism (b) it
   should not move. First measure which DSEC-Det sequences sit at the ceiling — E00 covers 18 DSEC train
   sequences and finds 6, and DSEC-Det's added sequences have not been surveyed. One afternoon on files
   already on the download list.

**One thing to stop doing.** Delete E01 from §Response-D or re-scope the citation. It measures activity
inside the *exposure*; the paper's lever is the 50 ms *event window*. A reviewer who follows the reference
will find a measurement of a different quantity supporting a design decision, and the paper's credibility on
measured evidence — which is currently its strongest asset — is worth more than that paragraph.
