# Where the novelty is, and the case for it

Written 2026-09-02 against `paper/main.tex`, `ideas/team08_v2.md`, `ideas/team04.md`, the
fifteen files in `reviews/`, and `experiments/E00`–`E07`.

Two things changed during this analysis and both are load-bearing:

1. **A new experiment, E09** (numbered E08 when run; renumbered by a parallel agent), was run and recorded in
   `experiments/e09_per_object_evidence_time/`. It measures `σ_τ` — the paper's central
   unmeasured quantity — from the sensor alone, with an analytic null, and it returns a
   positive result that survives three controls.
2. **A prior-art collision was found that kills the broad form of the novelty claim.**
   Waymo's `label.proto` already solves a per-object capture time that varies within one
   frame, and made it the ground-truth convention of the 2022 camera-only challenge. Verified
   verbatim at source, below. The claim survives in a narrowed form, and the narrowing is
   specific.

3. **E09's night result is then confounded by mains flicker, and cannot be claimed as
   written.** I ran a flicker check and cleared it; **my check was underpowered and my
   clearance was wrong.** A parallel agent's E10 settled it properly: 24.1 % of active night
   pixels are phase-locked to the mains at 100 Hz. The correction is recorded in full below,
   because the error is instructive — a 60-bin FFT inside one 14 996 µs exposure has 66.7 Hz
   bin spacing and cannot resolve a 100 Hz line at all.

Sections below were written before item 3 and have been corrected in place. Where a
conclusion changed, both the original and the correction are kept, because a reader needs to
know which claims in this repository were once believed and are no longer.

`main.tex` was not edited.

Standing constraint applied throughout: scope may be narrowed, the central claim may not be
weakened. Every recommendation below narrows scope or moves emphasis. None deletes evidence.

---

## What is imported

The paper's related-work section is already honest about three ancestors. This section states
the inventory more precisely, adds **six** ancestors the paper does not cite — one of which is
severe — and marks one sentence in the introduction that is factually wrong in a way that
costs the paper something.

### LET-3D-AP — Hung, Casser, Kretzschmar, Hwang, Anguelov, arXiv 2206.07705, 2022

Primary metric of the Waymo Open Dataset 2022 3D camera-only detection challenge. Quoted from
the PDF extraction in `reviews/reviewer05.md`.

> "We **decompose the localization error into a lateral error and a longitudinal error**. We
> find that the longitudinal error is more prominent in camera-only 3D detection. We
> therefore propose **longitudinal error tolerant (LET) metrics that are more permissive with
> respect to the longitudinal localization error**."

> "the **longitudinal error `e_lon` is the error along the line of sight** of the ground truth
> box, giving `e_lon = (e_loc · u_G) · u_G`"

> "state-of-the-art camera-based detectors can outperform popular LiDAR-based detectors with
> our new metrics past at 10% depth error tolerance"

**Taken:** the rank-one projection of a localisation error onto a privileged unit vector; the
tolerance-parameterised average precision; the affinity-weighted variant (LET-3D-APL →
`AP^⊥L`); the re-scoring of published detectors; and the ranking-flip framing.

**Not taken:** the tolerance is derived rather than swept. LET's own text is explicit that its
tolerance is chosen — *"a longitudinal tolerance value must be chosen … Users can also sweep
the tolerance values"* — while `τ_max = (w_G + min(w_P^decl, w_P^meas))/2` is read off a
declared and a measured support, and the `min(·)` rule means a wider measured support can
never buy a more permissive score. R5 tested this delta in round two and passed it.

**What the paper over-claims:** deltas 1 and 3 ("the axis is time", "the unit is
milliseconds") are one delta stated twice. R5:

> "along-the-viewing-ray and along-the-motion-path **are the same device**. Both are a
> rank-one projection of a localisation error onto a privileged unit vector … Substituting
> `û = v*/‖v*‖` for `u_G` changes the vector and nothing else in the algebra."

Say three deltas, not four.

**What nobody in this project had noticed — LET-3D-AP also has a per-object temporal
quantity.** Its Table I reports a per-dataset "Sync Gap [ms] Cam↔Label Center" as an interval,
with the footnote:

> "The sync gaps of other datasets **depend on the horizontal object position in the image
> plane** and falls within the given range."

> "Datasets such as Lyft and nuScenes offer multiple camera views but can experience **a
> synchronization gap of roughly 5−10 ms, depending on the object location on the image
> plane**."

This is discussed in the next ancestor, because it is where the real damage is.

### Waymo `camera_synced_box` — the severe collision, uncited anywhere in this project

I fetched and verified `label.proto` at source
(`raw.githubusercontent.com/waymo-research/waymo-open-dataset/master/src/waymo_open_dataset/label.proto`,
lines 106–133). Verbatim:

> "Used by Lidar labels to store a camera-synchronized box corresponding to the camera
> indicated by `most_visible_camera_name`. Currently, the boxes are shifted to **the time when
> the most visible camera captures the center of the box, taking into account the rolling
> shutter of that camera**. Specifically, given the object box living at the start of the Open
> Dataset frame (t_frame) with center position (c) and velocity (v), **we aim to find the
> camera capture time (t_capture), when the camera indicated by `most_visible_camera_name`
> captures the center of the object.** To this end, we solve the rolling shutter optimization
> considering both ego and object motion:
>   `t_capture = image_column_to_time(camera_projection(c + v * (t_capture - t_frame), …))`
> … We then move the label box to t_capture by updating the center of the box as follows:
>   `c_camera_synced = c + v * (t_capture - t_frame)`
> … **We use the camera_synced_box as the ground truth box for the 3D Camera-Only Detection
> Challenge. This makes the assumption that the users provide the detection at the same time
> as the most visible camera captures the object center.**"

**This defeats the broad claim.** "Existing formulations attribute one time to one output" is
false: a major benchmark solves a per-object capture time, acknowledges that it differs
between objects in one frame, and made "each detection carries its own effective timestamp"
the ground-truth convention of a public challenge in 2022. The paper cannot say the field
cannot state this. **It must cite `camera_synced_box` and concede the observation.**

**The three escape hatches, each verified rather than assumed:**

1. **The time is solved and then thrown away.** I grepped the whole `Label` message for
   `timestamp` and `time_`: **there is no timestamp field.** `t_capture` is absorbed into a
   spatial shift `c + v·(t_capture − t_frame)` and discarded. The per-object time exists in
   the construction and not in the release.
2. **It is a geometric construction, not a measurement.** `t_capture` is solved from rolling
   shutter geometry plus LiDAR-derived object velocity. It is where the readout row *would*
   have been, not where the evidence *was*. The reported statistic (their Fig. 5) is the
   **spatial** shift in metres; the millisecond figures are a dataset-level geometric bound,
   not a measured per-frame dispersion.
3. **No detector predicts it.** The challenge winner, MV-FCOS3D++ (arXiv 2207.12716), uses the
   synced labels and states that its projection is computed *"without considering rolling
   shutter for simplicity."*

**And the mechanism is absent here.** Waymo's per-object time exists *because of rolling
shutter*. R1 measured that DSEC's FLIR Blackfly S frame cameras are **global shutter**, so
the readout-row mechanism cannot operate on this paper's data. E08's dispersion has a
different cause — where the evidence falls inside a global-shutter integration window — and
is therefore a different phenomenon, not the same one on new data.

**The upside, and it is real.** This is the same rhetorical gift LET-3D-AP was. The standing
charge against an evaluation paper is "you invented a quantity nobody wants." The answer is
that a major benchmark considered per-object capture time important enough to **change its
ground-truth convention** over it. Waymo is precedent, not only ancestor.

### Nuñez et al., arXiv 2601.14038, January 2026 — states the idea and declines it

*Correcting and Quantifying Systematic Errors in 3D Box Annotations for Autonomous Driving.*

> "3D box annotation … is challenging in dynamic scenarios, **where objects are observed at
> different timestamps, hence different positions**."

> "An accurate annotation would either place the boxes where the objects were at the
> annotation timestamp **or should have indicated the exact timestamp when each object's
> position was annotated**. We focus on the former, as annotating multiple boxes at a common,
> pre-defined sample timestamp has been the standard in the autonomous driving field. However,
> the latter, i.e. **annotating each individual box at the exact location and timestamp that
> matches the sensor data**, has the potential to be more accurate and lead to better
> performance in downstream tasks."

They measure per-object offsets within single frames (+30 ms on Argoverse 2, −35 ms on MAN
TruckScenes) and define a dispersion metric, SDEDE — but of the **spatial** error, not of the
time. **This paper writes the idea in one sentence, declines to pursue it, and confirms it is
not the standard.** It must be cited as the motivating gap. Pretending it does not exist is
the single largest rejection risk in the whole submission.

### Qin & Shen, IROS 2018 — online temporal calibration for monocular VINS

The estimator, four years earlier, in vision. Quoted in `reviews/round2_reviewer05.md`:

> "`z^k_l(t_d) = [u^k_l  v^k_l]^T + t_d · V^k_l`. **`V^k_l` is feature's speed on the image
> plane** … **`t_d` is the unknown variable of time offset**"

> "The velocity `V^k_l` is calculated as follows: `([u^{k+1}_l − u^k_l], [v^{k+1}_l − v^k_l])
> / (t^{k+1} − t^k)`"

**Taken:** `δ̂ = e_∥/‖v*‖` in its entirety, and the over-identification structure (one scalar
required to reconcile two channels). **Not taken:** what the offset lies between — two
*sensor* clocks there, a predictor's clock and a *benchmark's label clock* here.

### sAP / Streamer — Li, Wang, Ramanan, ECCV 2020

`AP^sync` is Streamer:

> "our dynamic scheduler … and **asynchronous Kalman forecaster can be applied to any
> off-the-shelf detector** … we call **Streamer**" · "**the computation involves only bounding
> box coordinates**" · "**implement forecasting as post-processing of the detection outputs**"
> · "the improvement … **across 80 different settings**"

**Taken:** every clause of the `AP^sync` pitch. **Not taken:** the offset is estimated rather
than timed; it is representational and survives an infinitely fast GPU; scoring is on the
unmodified offline metric.

**Assessment:** `AP^sync` is the paper's weakest asset. R3: *"LET's tolerance is swept and
declared, not fitted to the evaluation set, and that is the one axis on which this paper is
currently **behind** its ancestor."*

### Four further uncited ancestors

**1. `Rethink 3D Object Detection from Physical World`, arXiv 2507.00190 (2025).** This was
E07's one unread paper — the one whose framing "could plausibly concern latency." I fetched
it. It does:

> "we introduce **latency-aware AP (L-AP)** and planning-aware AP (P-AP) as new metrics,
> **which consider the physical world such as the concept of time**"

A 2025 latency-aware AP inside LET-3D-AP's own citation graph. It does not collide with the
per-object claim — L-AP's latency is device latency in the sAP tradition — but E07's clean
verdict must be restated as *40 citing papers, one of which introduces a latency-aware AP,
none applying the decomposition to a per-object temporal axis or to an event camera.*
Unrefereed; mark it so, as FAOD is.

**2. REFID, Sun et al., CVPR 2023** (arXiv 2301.05191), found by grepping its LaTeX source:

> "compared to the temporal resolution of events, the length of the exposure time of frames is
> large and **not negligible**, so simple accumulation from a single timestamp in the above
> works loses information and **is not reasonable**."

The most damaging sentence found against the intra-exposure framing. The observation that a
frame's single timestamp does not represent its exposure is already in a CVPR paper. REFID
does not measure it. Any claim built on E01 must live entirely in the measurement.

**3. Kim et al., ECCV 2022, *Event-guided Deblurring of Unknown Exposure Time Videos***
(arXiv 2112.06988). Names the variability E00 measures: *"the exposure time is not always
known, and furthermore, it **can dynamically vary depending on the imaging environments when
the auto-exposure function turns on**."* Their exposures are ones they set themselves; they
never read a released dataset's metadata.

**4. RENet, Zhou et al., ICRA 2022** (arXiv 2209.08323). Already uses **DSEC's exposure
interval as an event window** — *"the events obtained from the RGB frame exposure time (ε₁)"*
— and never reports what is inside it. Its stated premise is the one E00 refutes: *"RGB frames
are obtained during a **short exposure time**."* At 14 996 µs against a 50 ms period that is a
30 % duty cycle. A citable target, not only an ancestor.

Also to cite: **DETAD (ECCV 2018)** beside TIDE, so the claim is always phrased as "we convert
a spatial localisation error into a time" and never as "we put a time unit in an AP", which is
false; and **Northcutt et al., NeurIPS 2021 D&B** as the standard the dataset-audit genre is
held to — *"We identify label errors … **and subsequently study the potential for these label
errors to affect benchmark results**."* The second clause is the bar.

### One sentence in the introduction that is wrong, and costs the paper

`main.tex` line 91: *"the released label formats have no field in which one could be
recorded."* Repeated at line 52 and in `ideas/team08_v2.md`.

Measured, on the release on disk. The DSEC-Det label dtype is

```
('t','<u8') ('x','<f4') ('y','<f4') ('w','<f4') ('h','<f4')
('class_id','u1') ('class_confidence','<f4') ('track_id','<u4')
```

`t` is a **per-box** unsigned 64-bit microsecond timestamp. Across the 60 released sequences,
**390 118 boxes carry only 70 379 distinct values of `t`** — 5.54 boxes per value — and E06
established those values are the 20 Hz frame clock. The same Prophesee dtype is the label
format of Gen1 and the 1 Mpx dataset.

The field exists. Every release fills it with one number per frame.

**And this is now a sharper point than before**, because the automotive formats genuinely
lack it: I inspected Waymo `Label` (no timestamp field at all), Argoverse 2 `Cuboid`
(`timestamp_ns: "Corresponds 1-to-1 with a lidar sweep"`, i.e. per-frame), and nuScenes
`sample_annotation` (no timestamp field). **The event-vision label format is the one that
already has the slot, and it is the one nobody fills.** Corrected, the claim is stronger than
the false version: reporting a per-object time is not a format change here, only a reporting
change.

---

## What is not in any ancestor

Four candidates, tested adversarially. One survives in a narrowed and specific form, one
survives conditionally, one survives only as a restated statistic, one does not survive.

### Candidate 1 — `σ_τ`, the within-output dispersion. **SURVIVES NARROWED, BUT ITS MEASUREMENT IS CURRENTLY CONFOUNDED.**

**The searches run.** R5 ran two adversarial rounds and came back empty:

> "`all:"effective timestamp"` → **0 arXiv records**, and it is still 0 … `all:"per-object
> latency"` → 0; `all:"temporal bias" AND all:"object detection"` → 0 … Nothing in the
> 36-paper streaming line, nothing in the 69 CVPRW EventVision papers I listed, nothing in
> NeurIPS 2025's 5,823 titles."

I re-ran those and added ~50 more across three sweeps: `abs:"per-object latency"`,
`abs:"object-level latency" AND abs:perception`, `abs:"each object" AND abs:"its own
timestamp"`, `abs:"object-specific" AND abs:"time offset"`, `abs:"per-feature time offset"`,
`abs:"streaming perception" AND abs:"per-object"`, `abs:"temporal support" AND abs:"object
detection"`, `all:"time centroid" AND all:"event camera"` — **all zero**. Plus the full CVF
listings for CVPR 2021–2025, ICCV 2021/2023/2025 and WACV 2024/2025 (19 918 titles):
`rolling shutter` → 27 papers, all correction/pose/NeRF/GS, **zero detection**; `streaming
perception` → 6, all frame-level.

**But the broad claim died anyway, and it died to full text, not abstracts.** Both decisive
hits — LET-3D-AP's Table I footnote and Waymo's `label.proto` comment — are invisible to every
abstract-level search engine. That is a methodological lesson worth carrying: R5's standing
warning that *"a zero-hit keyword conjunction is evidence about vocabulary, not about ideas"*
was exactly right, and this is the instance.

**The form that survives, with every clause load-bearing:**

> Prior work has recognised that objects within a single frame are captured at different
> times. Waymo solves a per-object rolling-shutter capture time `t_capture` and immediately
> absorbs it into a spatial correction to the ground-truth box; Nuñez et al. (2026) identify
> the same effect as an annotation error to be removed. **In both cases the per-object time is
> a nuisance eliminated offline from labels, using LiDAR and known object velocity, and is
> never retained** — no released label schema inspected (Waymo, Argoverse 2, nuScenes) carries
> a per-instance timestamp, the event-vision schemas carry the slot and fill it with the frame
> clock, and no detector predicts one. What is new here is (i) measuring the per-object
> effective time **from the sensor data**, on a **global-shutter** benchmark where the
> rolling-shutter mechanism is absent and no LiDAR or known velocity is available, and
> (ii) reporting its **within-frame dispersion, in units of time, against an analytic null**.

**Why the structural argument matters more than the keyword argument.** Each remaining
ancestor is constructed so that the dispersion is the thing to be removed.

- **Waymo/LET-3D-AP** compute it in order to *cancel* it into a box shift, and do not keep it.
- **Qin & Shen** estimate one `t_d` per rigid sensor pair by pooling over features. The spread
  of per-feature time estimates is *the estimator's error bar* — pooling it away is how a good
  `t_d` is obtained.
- **sAP** measures wall-clock compute latency, one number per frame, timed by the harness. It
  cannot differ between two objects of one forward pass.

The move is an inversion: **every ancestor treats the spread as nuisance to be eliminated;
this paper makes it the estimand.** That is a claim about the structure of the problem, so it
does not rest on a keyword search — which is fortunate, because the keyword searches missed
the collisions.

**Why the paper cannot currently claim any of this.** `σ_τ` is `\TODOnum` in `numbers.tex`.
It has never been measured, and the planned route to it is the most fragile quantity in the
draft. Three reviewers showed why: R7 — *"a ±20 % error in `σ_c` takes the headline from 'no
effect' to '40 % above the pre-registered threshold'"*; R2 — `δ̂_i` is a ratio estimator whose
population variance may not exist, so *"P8's pre-registered `σ_τ,excess ≥ 3 ms` is a statement
about the filter, not about the data"*; R2, R7 and R10 independently — the permutation null
tests the wrong direction, and R10: *"The instrument, when it fires, refutes the thesis it was
imported to save."*

I priced this on the data, and a parallel agent's E08 (`experiments/e08_label_noise/`) has
since measured the input my estimate had to assume. Median per-object image speed on DSEC-Det
is **40 px/s** (independently reproduced by both of us: median 40.0, p90 150 against my 143,
p99 360 against my 351). E08 estimates the label noise properly, from the third difference on
a uniform grid where the constant-acceleration term vanishes: **`σ_c` ≤ 0.497 px**, an upper
bound, against 0.605 px from the second difference. So label noise alone produces
**12.4 ms of apparent per-object offset at the median object** — I had said 17.5 ms, using
E06's raw median residual of 0.707 px in place of a noise estimate, which overstated it by
40 %. The conclusion does not change: only **3.6 %** of objects exceed 233 px/s, and frames
carrying three such objects number **690 of 70 379**. The `δ̂` route remains a search for a
3 ms signal in a 12 ms noise floor.

**Two further results from that E08 bear directly on this document.** First, in the paper's
favour: `σ_c` no longer has to be assumed, so R7's *"±20 % error in `σ_c`"* objection is
answerable with a measurement, and the excess-dispersion quantity can be reported against a
measured floor. That removes one of the advantages I had claimed was exclusive to E09.
Second, against the paper: **the label errors are not white.** The third-difference
autocorrelation is −0.357 at lag 1 where white noise forces −0.750, and three competing
explanations (pooled-ratio bias, heteroscedastic segments, heavy tails) were each pushed
through the identical code and each returned −0.74. The IV estimator's justification —
*"the two velocity estimates share no label, therefore their errors are uncorrelated"* —
**does not hold as written**, because disjointness does not deliver independence when the
errors are correlated. That is a correctness problem in the paper's headline estimator and it
reinforces the recommendation to demote it.

**E09 — so I measured `σ_τ` another way.** Full record in
`experiments/e09_per_object_evidence_time/README.md`. DSEC publishes each frame's own exposure
window; events and frames share one clock with no calibration step (E00 `PIPELINE_CHECK`); and
DSEC-Det's boxes are in the event camera's 640×480 frame. So for each labelled box, compute
the evidence-weighted time centroid of the events inside it during that frame's own exposure:

```
tbar_i = mean( t of events in box i during [exposure_start, exposure_end] ) − mid_exposure
```

**The null is analytic.** Uniform evidence over the exposure gives `tbar_i` variance
`w²/(12 N_i)`, so the excess is `Var_i(tbar_i) − mean_i(w²/(12 N_i))` and the subtrahend
contains no assumed quantity. No detector, no checkpoint, no velocity denominator, no `σ_c`,
no ratio estimator, no permutation null.

*Night, `zurich_city_09_a`, exposure pinned at 14 996 µs, 1133 frames, median 6 objects:*

| quantity | value |
|---|---|
| within-frame sd of `tbar_i` | **229.5 µs** (p90 333.5) |
| analytic uniform null | 93.4 µs |
| **excess** | **209.7 µs** |
| frames with positive excess | **91.8 %** |
| within-frame peak-to-peak spread | **601.6 µs** (p90 956.0) |
| frame-level common offset from mid-exposure | **−862 µs** |

*Day, `interlaken_00_c`, exposure 1523 µs:* sd 18.7 µs against a null of 23.9 µs, **excess
zero**, 33 % of frames positive. **The dispersion scales with the temporal support and
vanishes when the support is narrow** — the paper's thesis, across E00's two-level exposure
factor, with nothing trained.

*Control (a), random boxes — NEGATIVE, and reported as such.* Same box shapes, random
positions: sd 338.4 µs, null 134.4 µs, excess **310.5 µs** — larger than the labelled boxes'.
**The raw within-frame dispersion is not a property of objecthood.** Any claim that it is, is
refuted by this control.

*Control (b), per-track persistence — POSITIVE.* Remove the frame-level common component first
(that is precisely what a declared per-output scalar cancels), then ask whether the residual
is a persistent property of the object. 102 tracks with ≥ 5 observations:

| quantity | value |
|---|---|
| between-track sd of the centred residual | **170.3 µs** |
| between-track sd expected if there were no track effect | 37.6 µs |
| **variance ratio** | **20.56×** |
| lag-1 autocorrelation along the track | **0.471** |

*Control (c), position — POSITIVE, and it closes the obvious hole.* The persistence in (b)
could be *positional*: a region of the image with a persistent offset, inherited by any track
in it. Two tests say otherwise. Removing each image cell's mean residual before repeating the
track test leaves most of the effect: 20.56× → 17.64× → 16.13× → **13.45×** at 8×8, 16×16 and
32×32 granularity, so at most a third of the variance is positional. And tracks that move
*further* have *higher* autocorrelation (**0.567** for displacement ≥ 235 px against **0.152**
below), the opposite of what a positional offset predicts — the object carries its offset with
it. The obvious confound, that a moving track is simply a larger event-richer object whose
`tbar` is better estimated, is refuted: displacement and event count are *negatively*
correlated (r = −0.195) and the effect holds inside both event-count strata (−0.040 → 0.479
below the median count, 0.437 → 0.572 above).

**The per-object evidence-time offset survives removal of the frame-level component, survives
removal of image position, and travels with the object.**

**Why this form is not reached by the review record's three hardest objections.** It needs no
`σ_c`, so R7's ±20 % sensitivity does not apply. It is not a ratio estimator, so R2's divergent
variance does not apply. And it is not the permutation null whose direction R2, R7 and R10 all
showed points the wrong way — the frame-level component is *removed by construction* rather
than tested for. That is exactly the instrument R2 asked for:

> "The right instrument is a two-level variance decomposition — per-method constant, per-frame
> random effect, per-object residual … The per-frame term is what the reporting contract can
> cancel; the per-object residual is Death 4's escape."

E08 is that decomposition, computed on the sensor rather than on a detector.

**The confound that closed, against the result — and my first check of it was wrong.**
DSEC's own paper attributes high night event rates near street lamps to **flashing lights**,
and Graça & Delbrück (arXiv 2109.08640) show DVS noise rises in dim light. I ran a check and
concluded the night data was clean. **That conclusion was wrong and the check was
underpowered.** I took a 60-bin FFT of the event-rate profile *inside a single 14 996 µs
exposure*; that window has 66.7 Hz bin spacing, so a 100 Hz line falls between bins and
cannot be resolved at all. What I read as "a ladder of window harmonics present in daytime
too" was the window function, and I mistook the absence of a resolvable line for the absence
of flicker.

E10 (`experiments/e10_flicker/`, run in parallel) settled it correctly, with a long window
and the right per-pixel statistic:

| test | night `zurich_city_09_a` | day `interlaken_00_c` |
|---|---|---|
| strongest line, 90–110 Hz | **100.00 Hz** | — |
| peak over continuum (60–160 Hz) | **10 841** | 6.4 |
| 100 Hz line ratio, 20 s window | **48 694** | 6.4 |
| **active pixels with Rayleigh `p < 1e-3` at 100 Hz** | **24.07 %** | 0.08 % |
| same at `p < 1e-6` | 7.50 % | 0.00 % |
| off-frequency control, 137 Hz | 0.04 % | 0.11 % |

The Rayleigh statistic `Z = R²/N` is `Exp(1)` under the null, so the null `p < 1e-3` rate is
0.001. Two independent nulls land on the analytic value — the same code at 137 Hz on the same
night events, and at 100 Hz on daytime events — so the estimator is not manufacturing the
effect. Swiss mains is 50 Hz; lamp intensity flickers at 100 Hz.

**Why this defeats the night measurement.** A 100 Hz period is 10 ms and the night exposure
is 14 996 µs, so flicker completes one and a half cycles inside a single exposure. Objects at
different image positions see different lamps at different phases, which **displaces their
event-time centroids with no motion at all** — precisely the signature E09 measured. And the
correlation is worse than that: the excess dispersion appears at night and is zero in
daylight, and flicker is present at night and absent in daylight. A reviewer reaches for that
in one sentence.

**My controls do not rescue it, and I should not have thought they did.** Control (c) removed
*image-cell* means, but street lamps are static in the world and therefore **move through the
image** as the ego-vehicle drives, so an image-cell mean cannot remove a lamp-phase effect.
And the frame period is 50 001 µs against a 10 000 µs flicker period — 5.0001 cycles — so
consecutive exposures sample almost the same flicker phase, which manufactures exactly the
lag-1 autocorrelation that control (b) reported as evidence of persistence. Flicker plausibly
explains (b) and (c) together.

**What survives, and it is not nothing.**

- **The daytime data is clean.** Day matches the null at both frequencies, so the daytime
  arm of E09 carries no flicker confound. Its result is that the excess is **zero** at a
  1523 µs exposure — a valid negative, and now a validated calibration of the method rather
  than a mere contrast.
- **The route forward is prescribed and cheap.** 76 % of active night pixels are *not*
  significantly modulated, so the dispersion can be re-measured on the flicker-free majority
  with locked pixels excluded. **Until that is run, the night number is unusable.**
- **The estimator now has two validated nulls**, which is worth more than the number it was
  built to produce.

**And E10 is itself a finding.** "A quarter of the active pixels of DSEC's night sequences are
phase-locked to the mains at 100 Hz" is a fact about a widely used benchmark that its users
are not told, established with a proper null and an off-frequency control. It is cleaner than
E00's exposure structure, it needs no new machinery, and every event-vision method evaluated
on DSEC night sequences is consuming it. See Candidate 2b.

### Candidate 2 — E00's structure. **SURVIVES, and the paper states it as the wrong thing.**

The paper reports "a factor of 127". A range is not a finding. I recomputed over all 21 142
frames:

| | |
|---|---|
| frames strictly between 4207 and 14 996 µs | **0** |
| largest non-ceiling exposure anywhere | **4207 µs** |
| frames at exactly 14 996 µs | 6866 = **32.48 %** |
| 67th → 68th percentile | 3512 µs → **14 996 µs** |

Not a bimodal distribution — a **two-point distribution**: a continuous daytime mode that
stops dead at 4207 µs, and an atom at exactly 14 996 µs holding a third of the split, with
literally zero frames between. Two adjacent percentiles differ by a factor of 4.3.

Two facts make it a finding, both already in the repository from R1 and R7. The atom is the
night sequences, and inside it the exposure never varies (R1: *"long exposure and exposure
*variation* are anti-correlated in DSEC"*). Therefore **exposure width in DSEC is a binary
latent perfectly confounded with the illumination condition the field already reports**: every
published DSEC day/night breakdown is also an unreported 10× temporal-support breakdown.

R7 computed the shape, used it as a criticism in round one, then inverted it:

> "a covariate with no mass between 5 ms and 15 ms is a bad continuous regressor and an
> **excellent two-level treatment factor** … **Stratify `σ_τ` day vs night and the paper gets
> a mechanism test for free.**"

E08 is that test, run, and it returned the predicted sign.

**Prior-art status — checked hard, and it holds.** `all:"auto-exposure" AND all:dataset`
(9 hits, all AE algorithms), `abs:"auto-exposure" AND abs:"night"` (0), `abs:"capture
parameters" AND abs:"dataset" AND cat:cs.CV` (0), plus a title sweep of CVPR 2021–2025, ICCV
2021/2023/2025, WACV 2024/2025 for "exposure" — **31 unique titles, every one an
exposure-correction, fusion, HDR or AE-control method.** Decisively: **DSEC's own LaTeX source
contains the word "exposure" exactly once**, qualitatively, with no exposure number anywhere;
and a keyword scan of **all 572 papers citing DSEC** found not one reporting exposure-time
distributions or day/night exposure statistics. Every CV paper touching camera metadata
*consumes* it (*EXIF as Language*, CVPR 2023); **nobody audits it.** The cleanest gap is
exposure width as a *hidden stratification variable* — `abs:"hidden stratification"` returns
10 hits, all medical imaging and subgroup fairness, never a capture parameter.

**The objection that must be answered.** Not "already published" — *"the camera did what a
capped auto-exposure controller does under two illumination regimes."* Ceiling-pinning and a
two-point distribution are the expected signature of a capped controller, and 127× is a
description of day against night. Per the Northcutt standard this becomes a finding only when
paired with a measured consequence: **a published DSEC benchmark number that moves, or
reorders, when frames are stratified by exposure width.** That is item 2 below, and without it
E00 is a figure, not a section.

### Candidate 2b — DSEC's night sequences are mains-locked. **SURVIVES, and it is the cleanest finding in the repository.**

This did not exist as a candidate when this document was first written. It is a by-product of
trying to defend E09's night result, and it is worth more than the result it failed to save.

**The measurement (E10).** In `zurich_city_09_a`, **24.07 % of active pixels are phase-locked
to 100 Hz at `p < 1e-3`** — 240× the null rate — and 7.50 % reach `p < 1e-6`. The global
spectrum puts the strongest line at exactly 100.00 Hz with a 48 694 line ratio over the
continuum. Two nulls validate the estimator: 137 Hz on the same night events returns 0.04 %,
and 100 Hz on daytime events returns 0.08 %, both at the analytic null of 0.1 %.

**Why it is a finding and not a curiosity.** DSEC is a widely used benchmark and its night
sequences are the hard split that event-vision papers cite as their motivating case. A quarter
of the active sensor carrying a deterministic 100 Hz component means: the "events" that
methods consume in these sequences are substantially not scene motion; any event-count or
event-density statistic on DSEC night is inflated by a source unrelated to the scene; and any
representation with a temporal window shorter than ~10 ms is sampling flicker phase. **None of
this is stated anywhere in DSEC's documentation** — recall from Candidate 2 that DSEC's own
LaTeX source contains the word "exposure" exactly once, and the flicker attribution in its
paper is a qualitative remark, not a measurement.

**Prior-art status.** DSEC's own paper *attributes* high night event rates to flashing lights,
so the observation is not new — but as with Waymo, the observation is stated and not measured.
No quantification of the phase-locked fraction, with a null, on this or any driving event
benchmark was found. The genre precedent is Northcutt et al., and it applies here with unusual
force: the finding pairs naturally with a measured consequence, because the same 76 %
flicker-free mask that rescues E09 also defines a re-scoring experiment.

**Its risk.** It is one sequence. The other four ceiling sequences are unmeasured, and if they
differ the claim narrows to "some DSEC night sequences". That check is ~2 h of CPU and is
item 1 below.

### Candidate 3 — E01's night measurement. **SURVIVES ONLY AS A RESTATED STATISTIC. Not a novelty pillar.**

Is 2.60 threshold crossings per firing pixel on 38 % of the array a phenomenon existing
formulations cannot express, or motion blur restated?

**Very largely motion blur restated, and the paper should concede it.** Repeated threshold
crossing during integration is precisely the premise of the event-guided deblurring line.
`abs:"intra-exposure"` returns two papers and one states the framing outright — *"Motion blur
arises when rapid scene changes occur during the exposure period, collapsing rich
intra-exposure motion into a single RGB frame"* (arXiv 2604.10554). `reviews/PROCESS_DEFECTS.md`
records that a claim of this shape was already retracted once in this project, because *"EVDI
Eq. (19)-(20) already implements the exposure-correct two-frame loss."*

**And the interpretation is explicitly stated, not merely implicit** — REFID, above. Events
have also already been used as an instrument on the exposure: Weng et al., CVPR 2023, recover
exposure duration from events (*"an exposure estimation strategy guided by event streams"*);
Nakabayashi et al., CVPRW 2023, recover intra-exposure 2D motion (*"the proposed method
estimates the 2D motion of the blurred image at short intervals during the exposure time"*).

R7 also priced E01 inside this paper and was right: *"it measures activity inside the exposure
(1.5–15 ms). The paper's lever is the 50 ms event window … **E01 is decoration in this paper,
not evidence.**"*

**What survives, and it is worth keeping — three narrow things.**

1. **The statistic is unpublished.** Events per exposure, crossings per firing pixel, day
   against night, on a released benchmark: not found across ~30 arXiv queries, the 572-paper
   DSEC citation sweep, or source greps of seven likely papers. And the deblurring literature's
   own blur-magnitude convention is *not* a measurement of the scene — it is the count of
   averaged synthetic sub-frames (EDI: *"the frame number is fixed at 7"*; Kim et al.: *"m =
   {9,11,13,15}"*), a property of how the researcher built the data. Present E01 as **a
   blur-magnitude statistic that is measured rather than constructed**, and own that framing
   rather than denying it.
2. **Deblurring recovers appearance, not time.** A perfectly deblurred frame still carries one
   timestamp, and which instant its label should be indexed to is untouched by any restoration
   method. R6: *"A generative reconstruction must be indexed by a time … A discriminative task
   head is not indexed at all."*
3. **E01 converts `w_G` from declared to measured for the night stratum**, upgrading Eq. (2).

E01's proper role is to *license* E08 — it is the reason a night exposure contains enough
events for a per-box centroid to be estimable at all — not to be a novelty pillar.

### Candidate 4 — the decomposition, the estimator, the re-scoring device. **DOES NOT SURVIVE.**

All three imported, the paper says so, no reframing recovers them. R5 held novelty at 5/10
across two rounds on this basis and the assessment is correct.

---

## The strongest available novelty claim

**Written twice, because the flicker result forces a conditional.**

### If the flicker-free re-measurement succeeds (item 1 below), this is the claim:

> A benchmark frame does not have one time: measured from the event stream inside a single
> published DSEC exposure and restricted to the 76 % of pixels not phase-locked to the mains,
> the annotated objects of one frame have evidence-time centroids that differ by hundreds of
> microseconds against an analytic null, persist along each track after the frame-level
> component is removed, and grow with the exposure width — and the per-object timestamp field
> that the released label format already carries records none of it.

**The three sentences that defend it.**

1. *Where the field has met this quantity, it has eliminated it rather than reported it.*
   Waymo solves a per-object rolling-shutter capture time and absorbs it into a spatial
   correction to the ground truth, keeping no timestamp field; Nuñez et al. name per-object
   annotation timestamps in one sentence and decline them; temporal calibration pools the
   per-feature spread away as estimator variance; sAP's latency is one number per frame that
   cannot differ between two objects of one forward pass. We retain it and report its
   dispersion.

2. *It is measured on a sensor where the known mechanism is absent, and against a null that
   is analytic.* DSEC's frame cameras are global shutter, so Waymo's readout-row mechanism
   cannot operate, and there is no LiDAR and no known object velocity to construct a capture
   time from. E09 measures where the evidence fell; its null is `w²/12N`, so it needs no
   assumed centre noise, no velocity denominator, no ratio estimator and no permutation test.

3. *It moves with the mechanism the paper predicts.* The excess is zero at a 1523 µs exposure
   on data measured to be flicker-free, and the prediction under test is that it is non-zero
   at 14 996 µs once the mains-locked quarter of the sensor is excluded.

### If the re-measurement fails, this is the claim — and it is still a paper:

> A quarter of the active pixels in DSEC's night sequences are phase-locked to the mains at
> 100 Hz, the exposure that produces one indexed frame is a two-point distribution with a
> third of frames pinned at a ceiling and no frames at all in between, and the per-object
> timestamp field the released event-detection label format carries is filled with one number
> per frame across all 390 118 boxes — three properties of a widely used benchmark that its
> documentation does not state and its consumers do not know.

That is a benchmark-integrity paper with no invented quantity in it, and every number in it is
already measured.

**What neither version says.** Neither claims first observation of per-object capture time;
Waymo has that, and the paper must concede it in its own words before a reviewer does. Neither
says the dispersion is large enough to matter downstream. Neither claims the decomposition,
the estimator or the re-scoring device.

## What would have to change in the paper

Reordering only. No evidence is cut.

### The title

Current: *Temporal Support Error in Event–RGB Detection Benchmarks.* This names the imported
thing — "error along a privileged axis" is LET-3D-AP's contribution and the title advertises
it. If the centre of gravity moves to the dispersion:

**`Per-Object Temporal Support in Event–RGB Detection Benchmarks`**

R7's note that *"the title of the paper is currently about the metric; the result is about the
ground truth"* points the same way.

### What moves to the front

1. **E09 becomes the first result section**, ahead of the exposure survey — *conditional on
   item 1 clearing*. It is the only measurement that directly instantiates the central claim
   and the only one that does so without a checkpoint. All four controls go in the same table,
   the negative random-box control included and labelled negative. **If item 1 does not clear,
   E09's daytime null leads instead, as a calibration of the method, and E10 takes the front.**

1b. **E10 becomes a result section either way.** The phase-locked fraction with its Rayleigh
   null and its 137 Hz off-frequency control is a self-contained benchmark-integrity result,
   it is the reason the night numbers are treated as they are, and presenting it as a found
   and quantified confound is stronger than presenting a clean result that never looked.

2. **E00 is restated as the two-point distribution and the day/night confound**, not as "a
   factor of 127". Print: zero frames between 4207 and 14 996 µs; 32.48 % at the ceiling; 67th
   percentile 3512 µs against 68th percentile 14 996 µs; and the width/variability
   anti-correlation. The consequence sentence — that every published DSEC day/night breakdown
   is an unreported 10× temporal-support breakdown — is the finding and is currently absent.

3. **The label-format correction goes into the introduction**, replacing the false sentence at
   line 91, and now carries the cross-format comparison: Waymo `Label` and nuScenes
   `sample_annotation` have no per-instance time at all, Argoverse 2's is per-sweep, and the
   Prophesee event-detection dtype has the slot and fills it with the frame clock.

4. **`σ_τ`'s definition moves ahead of the estimator**, stated first as the two-level
   decomposition E08 computes, with the `δ̂`-based version second as predictor-side
   corroboration.

### What moves back

1. **`AP^sync` and `AP^bias` become a short subsection or supplement.** It is Streamer's
   operation and its constant is fitted on the data it scores. `AP^bias` stays — R3 called it
   *"the single highest-value experiment I can name in this revision"* — as a control, not a
   headline.

2. **The errors-in-variables apparatus becomes supplementary machinery.** Careful and correct,
   but it defends an estimator that is Qin & Shen's, on a benchmark where I measured its noise
   floor at 12.4 ms against a 3 ms target, and whose independence assumption E08 refutes. It
cannot lead.

3. **E01 moves out of the motivation into §Temporal support**, in two roles only: it measures
   `w_G` for the ceiling stratum, and it licenses E08. Follow R7's instruction to re-scope the
   citation.

### What must be added — required, not optional

- **Cite Waymo `camera_synced_box` and LET-3D-AP's sync-gap table**, and state the distinction
  in the authors' own words, in related work, before a reviewer states it for them: label-side
  and eliminated versus prediction-side and exposed; rolling-shutter geometry with LiDAR and
  known velocity versus a measurement of the evidence on a global-shutter sensor. Concede the
  observation, claim the formulation.
- **Cite Nuñez et al., arXiv 2601.14038**, as the motivating gap.
- **Never use "first" around *observing* per-object time.** "First to report it in units of
  time as a per-frame statistic measured from sensor data" is defensible; "first to report a
  per-object temporal offset" is not.
- Cite **arXiv 2507.00190 (L-AP)** as an unrefereed preprint and restate E07's verdict.
- Cite **REFID**, **Kim et al. ECCV 2022**, **RENet**, and **DETAD** beside TIDE.
- One sentence distinguishing `σ_τ` from **rolling-shutter** dispersion — declarable as a
  function of image row, therefore inside the reporting contract — plus R1's measurement that
  DSEC's cameras are global shutter.
- Say **three deltas, not four**.

### The novelty paragraph, rewritten

> The decomposition is LET-3D-AP's. The conversion of a displacement to a time is temporal
> calibration's. The ground-truth-free re-anchoring is Streamer's. And the observation that
> objects in one frame are captured at different instants is Waymo's, which solves a per-object
> capture time and absorbs it into a spatial correction to the ground-truth box. What is ours:
> we retain that time instead of eliminating it; we measure it from the event stream on a
> global-shutter benchmark where no rolling shutter, no LiDAR and no known object velocity are
> available to construct it; we report its within-frame dispersion in units of time against an
> analytic null; and we show it is a persistent property of the object that rises with the
> exposure and vanishes without it.

---

## What would raise novelty further, and what it would cost

One shared RTX 5090, ~7 GB usable and not guaranteed, Docker only. Ranked by novelty per unit
of risk.

### 1. Re-measure the night dispersion on flicker-free pixels. **Cost: ~3 h CPU. Risk: it may not survive, and that is the point.**

**This outranks everything else, because the paper's strongest claim is currently confounded
and this is the experiment that decides which of the two claims above the paper makes.** E10
supplies the instrument: the Rayleigh test at 100 Hz gives a principled per-pixel mask, and
**76 % of active night pixels are not significantly modulated**. Recompute `tbar_i` using only
unmasked pixels, and report the excess against the same analytic null.

Three outcomes, all publishable, and the paper should say now which it will write:
- *Excess survives at a similar magnitude* — the claim stands as the first version above, and
  it stands much more strongly than before, because it now has a named and defeated confound.
- *Excess collapses to zero* — the phenomenon was flicker; report that as a measured negative,
  and the paper becomes the second version. This is the honest and likely-enough outcome that
  it must be written into the plan before the run, not after.
- *Excess survives but shrinks* — report the flicker-attributable fraction as a quantity. That
  is arguably the most interesting result of the three.

Two supporting runs at the same cost: extend the Rayleigh test to the **other four ceiling
sequences**, so Candidate 2b is not one sequence; and add a stopped-vehicle or static segment
as a motion-free control. No GPU for any of it.

### 2. Stratify a published DSEC benchmark number by exposure width. **Cost: one CPU re-score once predictions exist. Risk: low.**

This is what converts E00 from a figure into a section, per the Northcutt standard. Report a
published detector's AP separately for the 14 996 µs stratum and the sub-5 ms stratum, with
sequence-level intervals. If the gap that the field reads as "night is harder" is partly a
10× temporal-support difference, that is a benchmark-integrity result with an immediate
consequence, and it needs none of the paper's invented quantities.

### 3. Extend E08 to the full exposure-width curve. **Cost: ~18 GB download + ~6 h CPU. Risk: low.**

E08 has two points because only two sequences' events are on disk. Five more ceiling sequences
(`zurich_city_00_a`, `01_a`, `02_a`, `03_a`, `10_a`) and four daytime ones turn a two-point
contrast into a regression of excess dispersion on exposure width with the frame period fixed
at 50 ms. Events are ~3 GB per sequence against 990 GB free. **A dose-response curve is a
categorically stronger object than a two-point contrast**, and it is the form in which a
reviewer will accept a support effect rather than a night/day effect. No GPU.

### 4. Content dependence of the evidence centroid. **Cost: ~2 h CPU on data already held. Risk: low.**

Team 04's consequence C2 — *"a timestamp that depends on texture is not a timestamp"* — is
testable inside E08 with no new data: regress each object's `tbar_i` on its event count, box
area, event density and class. If the evidence centroid is predictable from scene content, the
offset is content-driven, which is a property no clock has and which none of the ancestors can
express — Waymo's `t_capture` is a function of geometry and velocity only. Team 04 needed
240 Hz Vicon ground truth from the application-gated FE108 to attempt this; E08 needs none.
**This is the cheapest route to a claim Waymo structurally cannot make.**

### 5. Link the sensor-side dispersion to a detector-side one. **Cost: DSEC-Det images (81.9 GB) + ~9 GPU-h. Risk: medium-high.**

Does a released detector's per-object `δ̂_i` correlate with E08's `tbar_i` on the same objects?
A positive correlation links a sensor quantity to a network quantity and makes the chain one
argument — and it is the only route to "the detector *predicts* a per-object time", which is
the clause the narrowed novelty statement rests hardest on. Risk is real: the checkpoint must
reproduce its published score, and it inherits the 12.4 ms `δ̂` noise floor, so restrict to the
≥ 140 px/s stratum where I measured 3464 usable frames. **Attempt it; do not stake the paper on
it.** E08 stands without it; this does not stand without E08.

### 6. R7's cross-branch mechanism test. **Cost: one CPU pass on budgeted runs. Risk: low, contingent on 5.**

`σ_τ`(fused) against `σ_τ`(event-only). E00 fixes the frame branch's centroid at the label time
and E02 the event branch's at −25 ms, so a per-object mixing weight over [0,1] predicts
`25/√12 = 7.2 ms` — which R7 priced at +20 % RMS, decisive where 3 ms is not.
`GATE_RECORD.md` records this as *"the rescue the paper is not using."*

### 7. R3's ordering-probability matrix under the plain metric. **Cost: one CPU pass. Risk: none.**

Not a novelty item for the dispersion claim, but the cheapest independent contribution
available, and it cannot come back empty:

> "If the published gaps on Gen1 and DSEC-Det sit inside their own sequence-level CIs, then
> **the field's ordering of its flagship event detectors is not resolved by the field's own
> data** … the first of its kind at these venues on my round-one sweep."

### 8. Close the full-text search gap. **Cost: a few hours of a human with Scholar access. Risk: none, and it is required.**

Both fatal collisions came from **full text**, invisible to every abstract-level engine. Before
the novelty statement is finalised, someone must full-text search `"camera_synced_box"`,
`"sync gap"` + `"object position in the image plane"`, and `"timestamp"` + `"each object"` +
`"annotation"`. WebSearch was unavailable and OpenAlex/Semantic Scholar were rate-limited to
near-zero throughout this analysis. R5's two rounds also never swept IEEE Xplore, T-PAMI, RA-L,
ICRA or IROS — and Qin & Shen, the closest estimator ancestor, is an IROS paper found by hand.

### What is not worth doing

- **Retraining at several supports from scratch.** Unaffordable, and E05 shows the frozen
  masking lever saturates past 25 ms so the achievable range is far below the nominal 30×.
  R2's nine-GPU-hour fine-tune at five mask levels is the right compromise and is planned.
- **Pursuing the `δ̂`-based `σ_τ` as the headline.** Noise floor 12.4 ms against a 3 ms target
  at the median object. Report it as corroboration of E08, restricted to the ≥ 140 px/s
  stratum, with the noise floor printed as a function of speed.

---

## Honest ceiling

**Conditional, and the condition is item 1.**

| branch | ceiling | what the paper is |
|---|---|---|
| flicker-free night excess **survives** | **6/10** | a formulation claim supported by a measurement with a defeated confound |
| night excess **collapses** | **4.5–5/10** | a benchmark-integrity paper: flicker, exposure structure, label-format, label-noise |
| night excess **shrinks but persists** | **5.5–6/10** | as the first row, with a flicker-attributable fraction reported |

It is not 7 on any branch, and the paper should not claim 7.

**Why the ceiling did not rise further even though `σ_τ` got measured.** Three movements
nearly cancel. E09 converted the central claim from unmeasured to measured, worth more than a
point. Waymo's `camera_synced_box` removed the *observation* from the claim entirely, costing
about as much. E10 then removed the *measurement* on the branch where it was largest, pending
item 1. What is left is a formulation claim whose supporting measurement is currently valid
only where it returns zero.

**What a reviewer must concede for 6.**

1. *That retaining and reporting the quantity is a different contribution from eliminating
   it.* This is the load-bearing concession and it is narrower than the one the paper
   currently asks for. Waymo computes a per-object time to cancel it and keeps no timestamp
   field; this paper measures one and reports its dispersion. A reviewer who grants that the
   difference between a nuisance parameter and an estimand is a real difference grants the 6.
2. *That the analytic null is the right instrument.* The excess subtracts `w²/12N`, not an
   assumed `σ_c`. This mattered more before the parallel E08 measured `σ_c` at ≤ 0.497 px;
   it is now an advantage of convenience rather than of necessity.
3. *That a defeated confound is stronger than an absent one.* If item 1 succeeds, the paper
   can say it found the flicker, quantified it, masked it and the effect survived. That is a
   better position than never having looked, and it should be presented that way.

**What a reviewer will not concede, and the paper must not ask.**

- *That the effect is large.* It is not. On the night branch the dispersion was 210 µs and the
  frame-level bias 862 µs, and both are now sub-judice. R7's arithmetic on the 3 ms version
  already gave 0.10–1.64 % of filter RMS, and R10's *"if the large effect does not matter, the
  effect one-eighth its size does not matter more"* applies with more force, not less. The
  paper already disclaims downstream accuracy gain and must keep disclaiming it. Its magnitude
  test is "is it measurable and is it currently mis-stated", not "does it change a filter".
- *That the observation is new.* Waymo, and Nuñez et al. in one sentence.
- *That the metric family is new.* Five ancestors, with L-AP and DETAD.
- *That the IV estimator is justified as written.* The parallel E08 measured the label errors
  to be non-white (third-difference ACF −0.357 against −0.750), so disjointness does not
  deliver independence. This is a correctness defect, not a presentational one, and it must be
  fixed or the estimator demoted.
- *That the search was complete.* Both fatal collisions came from **full text** and every
  abstract-level sweep missed them; IEEE Xplore, T-PAMI, RA-L, ICRA and IROS remain unswept.

**The methodological lesson this document should carry into the paper.** Two of the three
conclusions written here were overturned within the same session — once by prior art found in
a `.proto` comment, once by my own confound check being underpowered enough to return a false
clearance. The paper's §Prior-art coverage already reports coverage rather than asserting
completeness; the same posture should be extended to its confound checks, which should state
their power, not only their outcome. A check that cannot resolve the frequency it is testing
for is not evidence of absence, and this repository now has a worked example of that.

**One structural warning, from R10, that this recommendation still does not escape.** R10's
round-two finding was that the thesis reads the same whatever the instrument says, because
every kill criterion falls back to a surviving paper. The conditional above is an attempt to
answer it honestly: the two claims are written out in advance, they are materially different
papers, and item 1 chooses between them. That commitment belongs in the paper now, while the
control is outstanding — not in a rebuttal after it returns.

### 한 줄 요약

**세션 중 결론이 세 번 바뀌었습니다. 두 번은 제 판단이 틀려서입니다.**

1. **σ_τ가 진짜 새로움**이라는 판단은 유지됩니다. 논문의 분해·추정기·재채점 장치는 모두
   수입품이고, 세 선행연구 모두 물체 간 산포를 *제거 대상*으로 설계했는데 이 논문은 그것을
   *추정 대상*으로 뒤집습니다. 측정이 없었으므로 **E09를 새로 실행**했습니다(검출기·체크포인트
   ·속도 분모·`σ_c` 불필요, 널이 해석적).

2. **광범위한 주장은 죽었습니다.** Waymo `label.proto`가 이미 물체별 촬영 시각 `t_capture`를
   풀어 2022 챌린지 정답 규약으로 삼았습니다(원문 직접 확인). 다만 그 시각은 공간 보정으로
   흡수되어 **버려지고**, `Label`에 타임스탬프 필드가 없으며, DSEC은 글로벌 셔터라 그
   메커니즘 자체가 없습니다. **Waymo와 arXiv 2601.14038은 반드시 인용해야 합니다.**

3. **E09의 야간 결과는 현재 교란되어 있고, 제 플리커 검사가 틀렸습니다.** 저는 노출 하나
   안에서 60-bin FFT를 돌려 "플리커 없음"으로 판정했지만, 그 창은 bin 간격이 66.7 Hz라
   100 Hz 선을 **애초에 분해할 수 없습니다**. 병렬 에이전트의 E10이 제대로 측정했습니다:
   야간 활성 픽셀의 **24.1 %가 100 Hz 상용전원에 위상 고정**(널의 240배), 널 검증 2개 통과.
   가로등은 세계 좌표에서 고정이지만 **이미지에서는 움직이므로** 제 위치 대조군도 이를
   제거하지 못했고, 프레임 주기 50 001 µs가 플리커 주기 10 000 µs의 정확히 5배라 제
   시간 자기상관도 설명됩니다.

**지금 해야 할 단 하나의 실험:** 위상 고정되지 않은 **76 %의 픽셀만으로 야간 산포를 재측정**
(CPU 약 3시간, GPU 불필요). 세 가지 결과 모두 발표 가능하며, **어느 쪽을 쓸지 지금 미리
문서에 적어두어야 합니다** — 그것이 R10의 "어떤 결과가 나와도 논문은 같은 말을 한다"는
지적에 대한 유일한 정직한 답입니다.

**정직한 상한:** 재측정 성공 시 **6/10**, 붕괴 시 4.5–5/10, 축소 시 5.5–6/10. 어느 경우에도
7은 아닙니다.

**부수적으로:** 병렬 E08이 `σ_c`를 0.497 px로 실측해 제 "17.5 ms"를 **12.4 ms**로 정정했고,
동시에 **라벨 오차가 백색이 아님**(3차 차분 ACF −0.357 대 이론 −0.750)을 보여 논문의 IV
추정기 정당화가 **성립하지 않음**을 밝혔습니다. 이건 표현 문제가 아니라 정확성 결함입니다.
