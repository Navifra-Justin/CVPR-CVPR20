# Round 2 — Reviewer 05 (prior art) — Team 08, *Right Place, Wrong Time* (v2)

**Standing position from round one.** I found LET-3D-AP (arXiv 2206.07705, Waymo Open Dataset's
official 2022 camera-only 3D metric), cut Team 08's novelty from 7 to 5, and kept ACCEPT. The main
session verified the LET abstract verbatim. That finding stands and I do not re-litigate it.

**What this round did.** I took the four surviving deltas adversarially, settled sAP, and prior-art
checked the four things v2 introduces that have never been checked. I found **one new collision**
(on `AP^sync`) and **one new uncited ancestor** (on the millisecond conversion itself), both quoted
below from PDFs I downloaded and extracted myself. Neither is fatal. I also closed three of round
one's open sweeps and I list what is still open.

Everything marked as a collision carries a sentence from the source. Everything I checked and found
empty is listed, because a prior-art review that reports only hits is useless to the next reader.

---

## Do the four deltas survive

### Delta 1 — "the axis is time, not the line of sight" — **WOUNDED**

The adversarial question the brief posed is the right one, and the answer is that
along-the-viewing-ray and along-the-motion-path **are the same device**. Both are a rank-one
projection of a localisation error onto a privileged unit vector, followed by an AP that is
permissive along that vector and a control that shows the permissiveness is directional. LET's
construction, from the PDF (§III):

> "The **longitudinal error `e_lon` is the error along the line of sight** of the ground truth box,
> giving `e_lon = (e_loc · u_G) · u_G`"

Substituting `û = v*/‖v*‖` for `u_G` changes the vector and nothing else in the algebra. A reviewer
who has used the Waymo devkit will write exactly that sentence, and Team 08's v2 says so itself
("a hostile reviewer can still say — correctly — that this is LET-3D-AP with the velocity vector
substituted for the range vector"). Good; that concession is honest and it is in the paper.

**What genuinely differs, and it is not nothing.** LET's axis is fixed by *sensor geometry* and is
computable from a single ground-truth box with no dynamics at all. Team 08's axis is fixed by the
*scene* and requires a tracked GT trajectory and a finite-differenced velocity — which is why the
whole errors-in-variables apparatus in §4.3 exists, and LET needs no such apparatus. The two axes
are also justified by different physics: LET's is the direction in which a monocular *sensor* is
epistemically weak; Team 08's is the direction in which a *clock* error must manifest. That is a
real difference of kind.

**Why I mark it WOUNDED rather than SURVIVES.** Two reasons.

1. **It is not an independent delta.** Delta 1 and Delta 3 are the same claim stated twice. The axis
   being the velocity is *precisely what makes* division by `‖v*‖` meaningful; there is no version
   of this paper in which the axis is the motion path and the unit is not milliseconds, or in which
   the unit is milliseconds and the axis is not the motion path. Counting them separately inflates a
   four-item list that is honestly a three-item list. I recommend the paper say "three deltas", not
   four — a reviewer who notices the padding will discount the rest of the list.
2. **The support for "nobody has done the motion-tangent version" is vocabulary evidence only.** My
   queries this round: `all:"direction of motion" AND all:"localization error"` → **0**;
   `all:"along-track" AND all:"cross-track" AND all:"tracking"` → 8, all orbital mechanics,
   satellite altimetry, gyroscope Allan deviation and tropical-cyclone assimilation, none in vision;
   `all:"error tolerant" AND all:"average precision"` → **2**, one of which is LET-3D-AP itself and
   the other an edge-detection benchmark paper. That is genuinely empty, and it is also exactly the
   kind of zero-hit conjunction I warned against in round one — LET-3D-AP contains neither
   "along-track" nor "event camera" and it is the paper that wounded this submission.

### Delta 2 — "the tolerance is derived from declared supports, not swept" — **SURVIVES**

This one holds, and I can now prove the contrast at source rather than by inference. LET's own
discussion section, from the PDF:

> "To compute LET metrics, a longitudinal tolerance value **must be chosen**, and the choice of the
> longitudinal tolerance **depends on the requirements of the downstream modules**, e.g. tracking or
> behavior prediction, especially for an autonomous driving system. **Users can also sweep the
> tolerance values** to gain more understanding of the error patterns."

and its parameter definition:

> "**longitudinal tolerance percentage `T_l^p`**: The maximum longitudinal error `e_lon` is expressed
> as a percentage `T_l^p` of the range to the ground truth `G`. For example, `T_l^p = 0.1` provides a
> 10% tolerance, and for a ground truth object that is 50 meters away (`|g| = 50`), the longitudinal
> tolerance is 5 meters."

So LET's tolerance is (i) a chosen hyperparameter, (ii) anchored to a *downstream consumer's*
requirement rather than to any property of the predictor or the annotation, and (iii) explicitly
sweepable, with Figure 6 ("LET metrics with different longitudinal error tolerance values") drawing
the curve. Team 08's `τ_max = (w_G + min(w_P^decl, w_P^meas))/2` is anchored to the *benchmark's own
stated interpolation half-width* and the *method's measured support*, which is a different and
better-motivated object. The `min(·)` rule — deliberately taking the smaller so a wider measured
support can never buy a more flattering permissive score — is a genuine anti-self-serving device
that LET does not have. I said this in round one and v2 now says it in the paper. Credit where due.

**I checked the brief's specific suspicion and it does not apply to v2.** I grepped every occurrence
of `τ_max` in `team08_v2.md`: there is **no sweep of `τ_max` anywhere and no AP-versus-tolerance
curve**. The brief's premise ("when the paper still reports curves over it") was true of a paper
that v2 is not.

**Two caveats that keep this from being a strong survival.**

- The team concedes the Gen1 half itself: "on Gen1 `τ_max` **is** a free parameter under another
  name, and we say so in the table caption." Half the primary testbeds do not get the delta.
- Sharper: Panel C varies `w_P^meas` over ≥ 12 configurations, and `τ_max` is a function of
  `w_P^meas`. So the tolerance *does* vary across the paper's central figure — not as an AP curve,
  but the quantity is not a single derived constant either. The distinction from LET is that the
  variation is driven by a measured property of each configuration rather than chosen; that is a
  defensible distinction and the paper should state it explicitly before a reviewer states it first.
- Sharpest: **the delta's carrier was demoted in the same revision.** `τ_max` parameterises `AP^⟂`,
  and §4.3 now marks `AP^⟂` **"DIAGNOSTIC ONLY"**, out of the abstract, out of every headline number,
  and disqualified as a ranking instrument. A methodological improvement to a quantity you have just
  removed from the headline is worth less than it was in v1. It is still worth something — `R`'s
  numerator has to come from somewhere — but the paper should not lead with it.

### Delta 3 — "the unit is milliseconds" — **WOUNDED (new finding)**

This is where round two found something. Two independent dents.

**(a) A tolerance-parameterised AP whose privileged axis is time and whose unit is a time already
exists, and it is the standard metric of an entire subfield.** Temporal action localisation has
scored detections by temporal IoU against a swept threshold since ActivityNet. From *Diagnosing
Error in Temporal Action Detectors* (Alwassel et al., **ECCV 2018**, arXiv 1807.10706 — PDF
downloaded and extracted):

> "Given the continuous nature of the problem, **a prediction segment is considered a true positive
> if its temporal Intersection over Union (tIoU) with a ground truth segment meets a given
> threshold**."
> "tIoU thresholds between 0.5 and 0.95 (inclusive) with a step size of 0.05."

This does not collide with Team 08's construction — in temporal action localisation *time is the
coordinate of the prediction itself*, so a temporal tolerance is just IoU in a one-dimensional space,
and nothing there converts a **spatial** error into a time. But it means the sentence "the unit is
milliseconds" will not by itself impress a reviewer who works on video. The claim must be stated as
*"we convert a spatial localisation error into a time"*, never as *"we are the first to put a time
unit in an AP"*, which is false. DETAD is also the temporal-axis analogue of TIDE and the paper cites
TIDE without it; it should cite both.

**(b) The conversion itself — displacement divided by finite-differenced image-plane speed to
recover a time offset — is standard, deployed, in-vision, and uncited.** Qin & Shen, *Online Temporal
Calibration for Monocular Visual-Inertial Systems*, **IROS 2018** (arXiv 1808.00692; PDF downloaded
and extracted; this is the temporal calibration shipped in VINS-Mono). Their model, verbatim:

> "`z^k_l(t_d) = [u^k_l  v^k_l]^T + t_d · V^k_l`.
> **`V^k_l` is feature's speed on the image plane**, got from eq. 2. **`t_d` is the unknown variable
> of time offset, which shifts feature's observation in time domain.**"

and the speed is obtained exactly as Team 08 obtains `v*`:

> "The velocity `V^k_l` is calculated as follows: `([u^{k+1}_l − u^k_l], [v^{k+1}_l − v^k_l]) /
> (t^{k+1} − t^k)`"

with the modelling assumption Team 08 also makes:

> "In a very short time period (several milliseconds), the camera's movement can be treated as
> constant speed motion. Hence, **a feature moves at an approximately constant velocity on the image
> plane in short time period.**"

That is `δ̂ = e_∥/‖v*‖` — an image-plane displacement converted to a millisecond time offset by
dividing by a finite-differenced image-plane speed — published in vision in 2018, four years before
LET-3D-AP, and running today inside one of the most-used VIO systems in robotics. Team 08 currently
credits this device to air-traffic surveillance (arXiv 2008.06352) and to trajectory prediction. The
closer and far more famous vision ancestor is missing from both v1 and v2.

**What survives, and it is still a paper.** Nobody has pointed this estimator at a *benchmark's
labels* or at a *learned predictor's effective clock*. My checks:
`all:"time offset" AND all:"annotation" AND all:"dataset" AND all:"detection"` → **0**;
`all:"synchronization error" AND all:"ground truth" AND all:"detection"` → **0**;
`all:"effective latency" AND all:"object detection"` → **0**;
`all:"temporal bias" AND all:"object detection"` → **0**;
`all:"aggregation window" AND all:"latency" AND all:"event"` → **0**.
VINS estimates the offset between two *sensor clocks* on a static scene, jointly inside a bundle
adjustment, as a nuisance parameter to be removed. Team 08 estimates the offset between a *trained
network's* effective clock and a *benchmark's label clock*, per released checkpoint, and publishes it
as a number about that checkpoint. That is a different object and it is unclaimed. But the algebra is
borrowed twice over now — from LET (the projection) and from temporal calibration (the division) —
and the paper must say so in the first submitted version, exactly as it now does for LET.

### Delta 4 — "the claim is over-identified across two channels" — **SURVIVES**

I tried hardest to break this one because reviewer02 and I both called it the strongest structural
asset, and it mostly holds.

LET has one channel and therefore no falsification test — that part of Team 08's claim is correct and
I verified it against the full PDF: there is no second observable in LET that `e_lon` must
simultaneously explain. TIDE and DETAD are taxonomies with no cross-channel consistency statistic at
all. In the *metric* literature the move is unclaimed.

**Two honest deflations the paper should absorb before a reviewer supplies them.**

- **The structure is generic estimation practice, not an invention.** "One scalar must explain more
  residual channels than it has degrees of freedom, and the surplus is a specification test" is
  over-identification in the econometric sense; `κ = |δ̂ − δ̂_s|/(σ_δ̂ + σ_δ̂_s)` is a normalised
  two-moment J-statistic. Calling it "the strongest piece of mathematics in the round" (R2) is
  generous. Its value here is that it is the *right* test to run on a metric, not that it is new.
- **Temporal calibration already runs the same structure.** Qin & Shen again:

  > "if there exists time misalignment between IMU and camera, **the IMU constraint is inconsistent
  > with vision constraint in the time domain** … **By optimizing `t_d`, we can find the optimal
  > camera pose and feature's observation in the time domain which matches IMU constraints.**"

  One scalar time offset, required to reconcile two independent measurement channels, with the
  reconciliation being what makes it observable. Team 08's second channel (box scale rate under
  approach) is different and its use as a *falsification test of a metric's own hypothesis* — rather
  than as an estimator to be optimised — is not something the calibration literature does. That is
  the surviving delta, and it is narrower than "we have a falsification test nobody has".

**Net on the four deltas: one survives clean (2), one survives narrowed (4), two are wounded and are
in any case one delta (1 and 3).**

---

## sAP and the temporal-tolerance line

**Ruling: sAP does not take the paper. It takes two of the paper's instruments, and one of them is
new in v2.**

I swept the line properly this round rather than through the single narrow conjunction I used in
round one. `all:"streaming perception"` returns **36 records** (round one's
`abs:"streaming perception" AND abs:"metric"` returned 6 and was too narrow). The line, as it stands:
*Towards Streaming Perception* (ECCV 2020 Oral, 2005.10420), *Real-time Object Detection for
Streaming Perception* / StreamYOLO (CVPR 2022 Oral), LongShortNet (ICASSP 2023), DAMO-StreamNet
(IJCAI 2023), *Context-Aware Streaming Perception* (ECCV 2022), DaDe (VISAPP 2023), MTD (PRCV 2023),
Transtreaming (2409.06584), CorrDiff (2501.05132), DyRoNet (WACV 2025), ASAP (2212.08914), *Real-time
Stereo-based 3D Object Detection for Streaming Perception* (NeurIPS 2024), LASP (2504.19115),
*Rethink 3D Object Detection from Physical World* (2507.00190, L-AP / P-AP, unrefereed).

**What the whole line is about, and why it is not Team 08's phenomenon.** Every one of these
quantifies **wall-clock compute latency**. None of them decomposes a localisation error by direction,
none converts a residual into a time, none reports a per-method time as an error unit, and none can
see a latency that exists at *zero* compute time — which is what a 50 ms event window's information
centroid is. Team 08's differentiation in the related-work row is correct as written. The three
"delay-adaptive" descendants (DaDe, MTD, Transtreaming) all *sense* the runtime delay and predict
forward to compensate; they never measure a representational one.

**sAP has still never been applied to event cameras.** `all:"streaming perception" AND all:"event
camera"` returns exactly **1** record — EHGCN (2504.16616), an unrefereed event-GNN *method* paper
that uses the phrase in passing and does not use the sAP metric. Team 08's claim reproduces.

**Where sAP does land: `AP^sync` and §6's re-anchoring.** See the next section — this is a genuine
collision and it is on material that is new in v2.

**The other branch of "temporal tolerance" — action detection and time-series event detection — is
adjacent, not colliding.** tIoU-thresholded mAP (above) is a swept temporal tolerance but the
prediction is itself an interval. `all:"temporal tolerance" AND all:"detection"` returns 5 records,
all time-series/physiological (SoftED, *Computers & Industrial Engineering* 2024: "There is a demand
for metrics that incorporate both the concept of time and **temporal tolerance** for neighboring
detections") — the right instinct, the wrong field, no spatial error, no vision. I would cite SoftED
in one line as evidence that the tolerance move is recognised as necessary elsewhere; it costs
nothing and pre-empts a reviewer.

**One supporting citation the paper is missing, found in the CVPRW sweep.** Kugele et al., *How Many
Events Make an Object? Improving Single-Frame Object Detection on the 1 Mpx Dataset*, **CVPRW 2023
(EventVision)**:

> "We analyze the distribution of event counts in the 2D bounding boxes in the 1 Mpx Dataset to find
> that the distribution is **skewed towards few events, rendering it impossible to detect objects
> based only on current information**."

That is a published, accepted, event-vision demonstration that the 1 Mpx label at time `t` frequently
has almost no event evidence at `t` — the label-versus-evidence mismatch that Team 08's ISA argument
asserts. It is a gift, not a threat, and no team in the round cites it.

---

## New material, newly checked

### `AP^sync` — **WOUNDED, and close to SCOOPED**

`AP^sync` is defined in v2 §4.4 as: re-anchor every prediction by `ĉ ← ĉ − τ̂_P·v̂_pred` where
`v̂_pred` comes from **the method's own consecutive outputs, never ground truth**, then score on the
**unmodified standard metric**; and its selling sentence is *"Because the post-processing is legal,
cheap, and GT-free, **anyone can apply it to their own detector and get the same benefit**."*

That is the sAP paper's Streamer. From the *Towards Streaming Perception* PDF (§4.3, Appendix B.2):

> "Note that our dynamic scheduler (Alg. 1) and **asynchronous Kalman forecaster can be applied to
> any off-the-shelf detector, regardless of its underlying latency (or accuracy)**. This means that
> we can assemble these modules into a meta-detector — which we call **Streamer** — that converts any
> detector into a streaming detection system that reports real-time detections at an arbitrary
> framerate."

> "**Association for bounding boxes across frames is required to update the Kalman filter**, and we
> apply IoU-based greedy matching. For association and forecasting, **the computation involves only
> bounding box coordinates** and therefore is very lightweight (< 2ms on CPU)."

> "For scalable evaluation, we assume zero runtime for the association and forecasting module, and
> **implement forecasting as post-processing of the detection outputs**."

And the ranking consequence, from the Table 2 caption:

> "First, we observe that **forecasting greatly boosts the performance** (from Table 1 row 7's 13.0
> to row 1's 16.7). Also, **with forecasting compensating for algorithm latency, it is now desirable
> to run a more expensive detector** (row 2). Searching again over a large suite of detectors after
> adding forecasting, we find that **the optimal detector is still Mask R-CNN (ResNet 50), but at
> input scale 0.75 instead of 0.5**."

> "Appendix B.4 evaluates the improvement in streaming AP **across 80 different settings** (8
> detectors × 5 image scales × 2 compute models), which vary from 4% to 80% with an **average
> improvement of 33%**."

So: a training-free, GT-free, bounding-box-only post-processing step that temporally re-anchors a
detector's outputs using velocity estimated from the detector's own consecutive detections, applied
to any off-the-shelf detector, re-scored across 80 published configurations, and shown to **change
which detector is best**. Every clause of Team 08's `AP^sync` pitch — legal, cheap, GT-free, anyone
can apply it, and a change of order is the legitimate flip — is a clause of the Streamer result.

**What survives, and I want to be precise rather than punitive.** Three real differences:

1. **The offset is measured, not known.** sAP forecasts forward by a latency the harness *knows*
   because it timed the GPU. Team 08 forecasts by `τ̂`, a quantity it *estimates* from the data and
   whose existence is the paper's claim. sAP could not have run `AP^sync` because it has no `τ̂`.
2. **The latency is representational, not computational.** sAP's compensation is for time the
   detector spent computing; Team 08's is for time the detector's *input window* is centred behind
   the query. sAP's compensation goes to zero on an infinitely fast GPU; Team 08's does not.
3. **The scoring metric is the offline standard AP, not sAP.** Team 08's whole point is that the
   correction shows up in the metric the field already publishes.

**But `AP^sync` is no longer a novel instrument, and the v2 text presents it as one** — it is
introduced as "the one legitimate ranking instrument" with no acknowledgement that the identical
post-processing was published, evaluated at scale, and already produced a "cheap post-hoc beats
train-time choice" result in 2020. The paper cites sAP once, in the *metric* row, for the thing sAP
does that Team 08 does not do. It must also cite sAP in §4.4 and §6, for the thing Team 08 does that
sAP already did. Note too that Team 08 justifies `AP^sync`'s shape by analogy to *On Calibration of
Object Detectors* (ECCV 2024); the far better precedent is sAP's own Table 2, in the same task, on
the same kind of artefact.

### The regression of measured `τ̂` on measured `w_P` (Panel C, P6, C3) — **CLEAR**

Nothing. `all:"aggregation window" AND all:"latency" AND all:"event"` → 0;
`all:"effective latency" AND all:"object detection"` → 0; `all:"per-object latency"` → 0;
`all:"temporal receptive field" AND all:"video"` → 12 records, none of which regresses a *measured
output bias* on a *measured input support* (they are architecture papers: Video BagNet, TDViT,
recurrent video SR stability). The streaming line plots AP against latency; nobody plots an estimated
temporal bias against a manipulated temporal support.

This is, in my judgement, **the single most valuable thing the revision added**, and more valuable
than any of the four deltas. It is also the one part of the paper that cannot come back empty in an
uninformative way — a slope says "property of the predictor", a null slope says "property of the
dataset", and the team has pre-registered both branches (K4). Its novelty is a *design* novelty
rather than an idea novelty, which is the correct kind for an evaluation paper. I would move it to
the front of the novelty list, ahead of everything inherited from LET.

### Per-bin occlusion (E1b, the influence profile `ω_k`) — **CLEAR as used, but say what it is**

**What it is.** Occlusion sensitivity analysis — Zeiler & Fergus's 2014 device of occluding part of
the input and measuring the change in the output. Its temporal extension already exists: *Adaptive
Occlusion Sensitivity Analysis for visually explaining video recognition networks* (AOSA, arXiv
2207.12859, **unrefereed** — no journal_ref, no acceptance comment):

> "a method for visually explaining the decision-making process of video recognition networks with a
> **temporal extension of occlusion sensitivity analysis** … The key idea here is to **occlude a
> specific volume of data by a 3D mask in an input 3D temporal-spatial data space and then measure
> the change degree in the output score**."

**What is not standard, and is Team 08's.** The readout. AOSA and every occlusion-sensitivity paper
I found measures a *class-score drop*. Team 08 measures **the induced shift of the predicted box
centre along the motion tangent**, converts the per-bin weights to an **influence centroid in
milliseconds**, and uses that number as the *predictor* in a pre-registered regression. I could find
no instance of an occlusion profile read out as a signed displacement in a physical unit.
`all:"occlusion sensitivity" AND all:"temporal"` → 6, one relevant (AOSA);
`all:"frame masking" AND all:"attribution" AND all:"video"` → 1, irrelevant;
`all:"time bin" AND all:"event camera"` → 3, all representation papers.

**What it is not, and the paper must not say otherwise.** It is not a measurement of "the network's
information centroid". It is a counterfactual influence profile under an intervention the network was
never trained to see, and an influence centroid is not the same object as an information centroid.
Team 08's controls are the right ones (mean-imputation arm, symmetric trailing-bin masking, mAP
reported at every mask) and are more careful than most attribution papers — keep them, and keep the
"assumption about the input → measured property of the model" phrasing away from the word
"information". **One technical hazard nobody in the round has flagged:** `ω_k` is defined as a
*signed* induced shift, so individual `ω_k` can be negative, and `Σω_k c_k` is not a centroid unless
the weights are non-negative and normalised. Define `ω_k = |Δc_∥|` or state the normalisation, or P1's
"agrees within ±8 ms" test is not well-posed. Team 08 does **not** claim per-bin occlusion as a
contribution anywhere in v2, which is the correct posture and which is why this is CLEAR rather than
WOUNDED.

### `σ_τ` (within-output temporal dispersion, absorbed from Team 04) — **CLEAR**

Round one's finding stands: `all:"effective timestamp"` → **0 arXiv records**, and it is still 0.
New this round, all empty: `all:"per-object latency"` → 0; `all:"temporal bias" AND all:"object
detection"` → 0; `all:"tracking metric" AND all:"latency"` → 0; `all:"rolling shutter" AND all:"object
detection" AND all:"bounding box"` → 0. Nothing in the 36-paper streaming line, nothing in the 69
CVPRW EventVision papers I listed, nothing in NeurIPS 2025's 5,823 titles.

**The one rebuttal risk, which is conceptual rather than bibliographic.** "Different objects in one
output tensor live at different instants" is, in a rolling-shutter camera, simply true of the *sensor*
and has been known for as long as CMOS readout has existed. A reviewer may say the phenomenon is old.
The answer — which the paper should pre-empt in one sentence — is that rolling-shutter dispersion is
*declarable as a function of image row* and therefore falls under the reporting contract, whereas
`σ_τ` is dispersion driven by per-object motion and texture and has no declarable functional form.
That is precisely the argument v2 already makes about the DAGr sawtooth ("this *is* still declarable
— as a function rather than a scalar — so it strengthens the reporting contract rather than defeating
it"), and it needs to be made about rolling shutter too or the `σ_τ` "so what" is exposed.

The permutation null is a genuine repair of Team 04's fatal gap and I have nothing to take from it.

---

## Still unverified

So a later reader knows the boundary of what has been checked across both rounds.

**Closed this round (previously open):**
- **NeurIPS 2025 main conference** — full title list pulled from `papers.nips.cc` (**5,823 titles**)
  and grepped for streaming / latency / average precision / evaluation metric / temporal metric /
  event camera / error decomposition / detector diagnosis. **Nothing relevant.**
- **CVPR Workshops, event-vision track** — `CVPR2023_workshops/EventVision` (33 papers) and
  `CVPR2025_workshops/EventVision` (36 papers) enumerated in full and read by title. No metric,
  benchmark-integrity or temporal-support paper. One useful supporting citation found (Kugele et al.,
  quoted above). Note for the record: **CVPR 2024 has no EventVision entry in the CVF workshop
  index**, so that year is unchecked and is not checkable from the open-access listing.
- **CVPR 2026 workshops** — full workshop menu pulled; **there is no event-vision or neuromorphic
  workshop in the CVPR 2026 open-access index**, so there is no 2026 workshop event-vision listing to
  sweep.

**Still open, in descending order of risk:**

1. **IEEE Xplore / TPAMI / TIP / RA-L / ICRA / IROS.** Still unswept, and this round is the argument
   for why it matters most: my one new ancestor (Qin & Shen) is an **IROS** paper, and round one's
   Team 03 kill (Mueggler) was an **ICRA** paper. Two of the three hardest findings I have produced
   across both rounds come from robotics venues with no open listing to grep, found only because I
   guessed the right vocabulary. Team 08's K7 week-1 sweep should be pointed here first.
2. **The citation graph of LET-3D-AP.** Not pulled — Google Scholar is unavailable to me and the
   Semantic Scholar route was not attempted this round. **This is the highest-yield remaining check
   in the whole review.** Anyone who cited LET-3D-AP and generalised the privileged axis away from
   the line of sight is the paper that kills this submission, and they would not necessarily use any
   of Team 08's vocabulary. Two hours of work; do it before writing the related-work table.
3. **ICLR / ICML / AAAI proceedings listings.** Unswept in both rounds.
4. **ECCV 2026.** `ecva.net` carries ECCV 2018–2024 only (6,166 titles pulled and grepped this
   round); there is no 2026 listing in existence to sweep.
5. **ICCV workshops, ECCV workshops, NeurIPS Datasets & Benchmarks 2025.** Unswept.
6. **Full-text search anywhere.** arXiv's `all:` field indexes title, abstract, authors and comments,
   **not full text**. Every empty conjunction above is evidence about vocabulary, not about ideas.
   This warning applied to five submissions in round one and it applies to this one.

**Claims from round one I could not close, restated as still-open:** (i) whether any *event-vision*
paper converts along-motion detection error into a time — I have now run eight further conjunctions,
all empty, and I regard this as strongly supported but not proven, for the full-text reason above;
(ii) whether the DSEC-Det / DSEC-3DOD label-forensics result (E0) has any prior art anywhere — round
one's `all:"ground truth" AND all:"interpolation" AND all:"event camera" AND all:"benchmark"` → 0
still stands and I found nothing this round to dent it. **E0 remains the strongest single deliverable
in the round and remains completely untouched by prior art after two rounds of adversarial search.**

---

## Revised novelty score with justification

**Round one: 5 / 10 (down from the team's self-scored 7). Round two: 5 / 10. The team self-scores
5.5; I hold at 5, and the composition of the 5 has changed.**

The repositioning is **honest and, as scholarship, exemplary**. Installing LET-3D-AP as first row,
naming it both ancestor and precedent, adopting LET-3D-APL's affinity-weighted form as `AP^⟂L`,
demoting the air-traffic credit, and lowering the self-score in the paper rather than in a rebuttal is
exactly the response I asked for and it is better than most published related-work sections. It also
converts my round-one finding from a liability into an asset, correctly: the hardest sell in this
paper is "a benchmark should adopt an axis-tolerant AP", and the answer is now "one did, officially,
in 2022".

**Why the score does not go up despite a better paper.** Round two removed roughly as much novelty as
the revision added:

- `AP^sync`, the new ranking instrument that replaced the flip, is largely the sAP Streamer — the
  same GT-free bounding-box-only post-processing, applied to off-the-shelf detectors, already shown
  to reorder which detector is best.
- The millisecond conversion, delta 3, has a closer and more famous in-vision ancestor than the one
  cited (VINS-Mono's online temporal calibration, IROS 2018), and a time-unit tolerance in an AP is
  the standard metric of temporal action localisation.
- Deltas 1 and 3 are one delta. The list is three, not four.
- Delta 2's carrier (`AP^⟂`) was demoted to "DIAGNOSTIC ONLY" in the same revision, which reduces
  what the improved tolerance buys.

**Against that, the revision added one genuinely unclaimed thing of real value** — Panel C, the
regression of measured `τ̂` on measured `w_P` over ≥ 12 free configurations — and preserved two more
(`σ_τ` with the permutation null Team 04 never had, and E0). Those three are what the 5 now rests on.
The decomposition, the tolerance-parameterised AP, the ranking-flip framing, the post-hoc re-anchoring
and the ms conversion are all borrowed, and the paper now concedes four of those five.

**The half-point I am withholding from the team's 5.5 has a name:** two of the four deltas they claim
are one delta, and that one delta has an uncited ancestor closer than the one they credit. Fix both —
say "three deltas", cite Qin & Shen and sAP-as-Streamer — and I would sign 5.5 without argument. The
number is not the point; the honesty of the list is.

**What the novelty sentence should be**, after two rounds:

> The decomposition is LET-3D-AP's. The conversion to a time is temporal calibration's. The GT-free
> re-anchoring is sAP's. What is ours: we point all three at a *benchmark's own clock* rather than at
> a sensor's; we show a released detector's effective timestamp is a measurable function of its
> temporal support; we show one output tensor carries several of them; and we show the flagship
> high-rate ground truths are their own interpolation prior.

Every clause of that is defensible after everything I have thrown at it.

---

## Verdict

**ACCEPT — unchanged from round one. Novelty 5 / 10. This remains the strongest idea in the round on
execution certainty, and two rounds of adversarial prior-art search have not killed it.**

The revision does the two things that matter most: it concedes the collision at full strength in the
paper rather than in a rebuttal, and it moves the headline onto three results (E0, the EIV-corrected
`τ̂`, Panel C) that cannot come back empty in an uninformative way. That is the correct architecture
for an evaluation paper and it is rarer than it should be.

**Required before submission, in order:**

1. **Cite *Towards Streaming Perception* a second time, in §4.4 and §6**, for the Streamer /
   asynchronous Kalman forecaster — the GT-free bounding-box-only post-processing that re-anchors any
   off-the-shelf detector and already reordered detector choice. Presenting `AP^sync` as a new
   instrument without it is the same mistake v1 made with LET-3D-AP, on smaller stakes.
2. **Cite Qin & Shen, IROS 2018** (and Furgale-line temporal calibration generally) for
   `δ̂ = e_∥/‖v*‖`. Their equation `z(t_d) = [u, v]^T + t_d·V` with `V` finite-differenced from
   consecutive observations *is* the estimator. Retire the air-traffic-surveillance citation to a
   footnote; it is the weakest of the three ancestors and the only one currently in the lead position.
3. **Say "three deltas", not four**, and lead the novelty list with Panel C rather than with the axis.
4. **Cite DETAD (ECCV 2018)** beside TIDE, and state the claim as "we convert a spatial error into a
   time", never as "we put a time unit in an AP".
5. **Pull the LET-3D-AP citation graph in week 1**, ahead of everything else in K7. It is the only
   remaining check with a realistic chance of producing a fatal collision, and it is two hours.
6. Minor: define `ω_k`'s sign convention so the influence centroid is well-posed; add one sentence
   distinguishing `σ_τ` from rolling-shutter dispersion; add Kugele et al. (CVPRW 2023) as supporting
   evidence that 1 Mpx labels frequently lack event evidence at their own timestamp.

**What I did not find, after two rounds:** anything that measures a benchmark's label clock, anything
that reports a detector's effective timestamp as a published number, anything that measures the
dispersion of that timestamp within one output, and anything that asks whether a high-rate ground
truth is recoverable from its own interpolation prior. Those four are the paper. They are worth a 5,
and a 5 that survives this much searching is worth accepting.

---

### Sources fetched and extracted this round

**Full PDFs downloaded and text-extracted (4).** *Towards Streaming Perception* (arXiv 2005.10420v2,
3.7 MB); LET-3D-AP (arXiv 2206.07705v2, re-pulled for the tolerance discussion); *Diagnosing Error in
Temporal Action Detectors* (arXiv 1807.10706v1); *Online Temporal Calibration for Monocular
Visual-Inertial Systems* (arXiv 1808.00692v1).

**Abstracts pulled via the arXiv API (12).** sAP, ASAP, LASP, DaDe, MTD, Transtreaming, EHGCN, AOSA,
SoftED, DETAD, *Rethink 3D Object Detection from Physical World*, Qin & Shen.

**Proceedings listings downloaded and grepped locally (5).** `papers.nips.cc` NeurIPS 2025 main
(5,823 titles); `ecva.net/papers.php` (6,166 titles, ECCV 2018–2024);
`openaccess.thecvf.com/CVPR2026_workshops/menu`; `CVPR2023_workshops/EventVision` (33 papers);
`CVPR2025_workshops/EventVision` (36 papers). One abstract page fetched individually (Kugele et al.,
CVPRW 2023).

**arXiv API queries — HITS.**

| Query | Result |
|---|---|
| `all:"streaming perception"` | **36** — the full sAP line; all compute-latency; **1** event-camera record (EHGCN, unrefereed method paper) |
| `all:"error tolerant" AND all:"average precision"` | 2 — LET-3D-AP itself + an edge-detection benchmark |
| `all:"temporal tolerance" AND all:"detection"` | 5 — all time-series/physiological (SoftED et al.), none in vision |
| `all:"occlusion sensitivity" AND all:"temporal"` | 6 — 1 relevant (AOSA, unrefereed) |
| `all:"temporal receptive field" AND all:"video"` | 12 — architecture papers, none regressing bias on support |
| `all:"temporal calibration" AND all:"time offset" AND all:"camera"` | 5 — **Qin & Shen IROS 2018**, the new ancestor |
| `all:"latency-aware" AND all:"average precision"` | 2 — L-AP (unrefereed), video-anomaly metrics |
| `ti:"Diagnosing Error in Temporal Action Detectors"` | 1 — DETAD, ECCV 2018 |

**arXiv API queries — EMPTY.**

| Query | Records |
|---|---|
| `all:"direction of motion" AND all:"localization error"` | 0 |
| `all:"temporal average precision"` | 1, irrelevant (visual query localisation) |
| `all:"per-object latency"` | 0 |
| `all:"effective latency" AND all:"object detection"` | 0 |
| `all:"aggregation window" AND all:"latency" AND all:"event"` | 0 |
| `all:"temporal bias" AND all:"object detection"` | 0 |
| `all:"time offset" AND all:"estimation" AND all:"bounding box"` | 0 |
| `all:"time offset" AND all:"annotation" AND all:"dataset" AND all:"detection"` | 0 |
| `all:"synchronization error" AND all:"ground truth" AND all:"detection"` | 0 |
| `all:"tracking metric" AND all:"latency"` | 0 |
| `all:"rolling shutter" AND all:"object detection" AND all:"bounding box"` | 0 |
| `all:"temporal localization error" AND all:"action"` | 0 |
| `all:"frame masking" AND all:"attribution" AND all:"video"` | 1, irrelevant |
| `all:"along-track" AND all:"cross-track" AND all:"tracking"` | 8, none in vision |
| `all:"latency compensation" AND all:"detection" AND all:"benchmark"` | 1, particle physics |
| `all:"effective timestamp"` (re-run from round one) | **0**, still |
