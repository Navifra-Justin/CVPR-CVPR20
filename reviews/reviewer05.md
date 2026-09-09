# Reviewer 05 — CVPR20 idea-selection round

**Assigned specialism: prior art. My job was to find the paper that already did it.**

Everything I mark as a collision is backed by a sentence I pulled from the actual abstract, the
actual PDF, or the actual source file — never from a team's summary of it. Everything I checked
and found *empty* is listed too, because a prior-art reviewer who reports only the hits is
useless to whoever reads this next.

Three findings in this review appear in none of the other nine reviews on disk (checked by grep
over `reviewer01..10.md`): **Mueggler et al., ICRA 2015** (event lifetime), **LET-3D-AP**
(Waymo's longitudinal-error-tolerant AP), and **Binary TTC** (CVPR 2021). They land on Teams 03,
08 and 07 respectively. The first and third are kills. The second is the adversarial check the
brief asked me to run on the consensus winner, and it lands.

---

## Comparison set

Twelve accepted papers, each verified by finding its title in a proceedings listing I downloaded
myself (`openaccess.thecvf.com/CVPR20{24,25,26}?day=all`, `.../ICCV2025?day=all`, `ecva.net`),
then fetching its own abstract page or PDF. No title here is taken from a team's table.

| # | Title | Venue / Year | Novelty it claims | How verified |
|---|---|---|---|---|
| C1 | **Adaptive Spatial-Temporal Window: Unlocking the Potential of Event Cameras in Heterogeneous Velocity Scenarios** (ASTW) | CVPR 2026 | Patch-level time-window length from a max-entropy criterion on event density; "simultaneously achieves temporal adaptivity and spatial locality in event partitioning"; contributes HetVel, "the first RGB-event dual-modality dataset for HVS" | CVF listing + abstract fetched + PDF |
| C2 | **Time-Specialized Event-Image Alignment for Blur-to-Video Decomposition** (TSANet) | CVPR 2026 | Relative Time-Encoded Attention + Timesurface Dynamic Warping to time-specialize *both* event and image features at an arbitrary query time | CVF listing + full PDF text |
| C3 | **Ev-3DOD: Pushing the Temporal Boundaries of 3D Object Detection with Event Cameras** | CVPR 2025 | First event-based 3D detection; detection "during inter-frame intervals when synchronized data is unavailable"; Ev-Waymo + DSEC-3DOD with 100 FPS GT boxes | CVF listing + abstract |
| C4 | **Unleashing the Temporal Potential of Stereo Event Cameras for Continuous-Time 3D Object Detection** | ICCV 2025 | Stereo-event-only continuous-time 3D detection, explicitly because "dependency on synchronized sensors" breaks in fast motion | CVF listing + abstract |
| C5 | **Bridge Frame and Event: Common Spatiotemporal Fusion for High-Dynamic Scene Optical Flow** | CVPR 2025 | A common-latent bridge; "frame-based motion possesses spatially dense but temporally discontinuous correlation, while the event-based motion has spatially sparse but temporally continuous correlation" | CVF listing + abstract |
| C6 | **State Space Models for Event Cameras** | CVPR 2024 | Learnable timescales; robustness to inference-time window duration | CVF listing |
| C7 | **Latency Correction for Event-guided Deblurring and Frame Interpolation** | CVPR 2024 | Parameterized *event* latency model; EDI made differentiable w.r.t. latency; "the temporal discrepancy between the actual occurrence of changes in the corresponding timestamp assigned by the sensor" | CVF listing + abstract |
| C8 | **TTAPFormer: Robust Arbitrary Point Tracking via Transient Asynchronous Fusion of Frames and Events** | CVPR 2026 | Transient Asynchronous Fusion: "explicitly models the temporal evolution between discrete frames through continuous event updates"; names that prior frame+event fusion is "synchronous or non-adaptive... leading to temporal misalignment" | CVF listing + abstract |
| C9 | **Beyond Duality: A Hybrid Framework of Leveraging Shared and Private Features for RGB-Event Object Detection** (SPFD) | CVPR 2026 | Frequency-domain decoupling of shared vs. private RGB/event features; "selectively emphasizing texture-rich RGB features in static regions and motion-sensitive event features in dynamic regions" | CVF listing + abstract |
| C10 | **CMTA: Cross-Modal Temporal Alignment for Event-guided Video Deblurring** | ECCV 2024 | Intra-exposure enhancement + inter-frame alignment as separate modules | ECVA listing |
| C11 | **UniINR: Event-guided Unified Rolling Shutter Correction, Deblurring, and Interpolation** | ECCV 2024 | Spatio-temporal INR with exposure time embedded in the query | ECVA listing |
| C12 | **BeNeRF: Neural Radiance Fields from a Single Blurry Image and Event Stream** | ECCV 2024 | Recovers the camera trajectory *within* the exposure jointly with a radiance field | ECVA listing |

**What this set says about the frontier.** In 2024–2026 the accepted work treats intra-exposure
time as (i) a *query coordinate* for a reconstruction (C2, C11, C12), (ii) an *aggregation
hyper-parameter* to be adapted (C1, C6), or (iii) a *misalignment to be registered away*
(C5, C8, C9). Nobody in this set treats temporal support as a *predicted output with units*, and
nobody scores anything in milliseconds. That gap is real, and it is the gap the whole CVPR20
domain is aimed at. It is narrower than most of these ten teams believe, for the reasons below.

---

## Per-idea verdicts

| Team | Verdict | One-sentence reason |
|---|---|---|
| **01** — Latent exposure support | **BORDERLINE** | EBFI-BE (CVPR 2023) already estimates the lost exposure prior from events and states that this makes blind exposure *well-posed*, so Team 01's headline proposition formalizes a premise the field accepted three years ago; the TSB law and the benchmark-bias measurement survive, and are the paper. |
| **02** — Exposure-occupancy measures as the label | **REJECT** | Two independent kills: TSANet's Figure 1 (CVPR 2026) *is* its Figure 2 construction, and Sayed & Brostow (CVPR 2021) not only made the "choose one convention more carefully" move Team 02 declares unavailable, they report it beat four other remedies. Fatal to this framing, not to the idea. |
| **03** — Temporal support fields | **REJECT** | "We found no work that predicts a temporal support measure as its output" is defeated by Mueggler et al., ICRA 2015, which assigns every event a *lifetime* — an explicit, content-dependent, per-pixel validity interval emitted as output precisely to replace fixed windows. Fatal to the "first-to", not to the abstention idea. |
| **04** — Effective timestamp `τ̂` | **ACCEPT** | The cleanest prior-art record in the round on my instrument: `"effective timestamp"` returns **0** arXiv records and no paper in my comparison set measures the clock of a fused prediction — the "no one has done this" claim is the only one of the ten I could not dent. |
| **05** — No offset fixes a width | **BORDERLINE** | Prior art is clear and honestly conceded (Raskar 2006, Yang CVPR 2024 verified to be a *first-moment* correction exactly as claimed), but the theory tier is a textbook Fourier fact and the novelty reduces to one measurement (OBD) in a regime DSEC daytime may not reach. |
| **06** — The exposure gap `J` | **ACCEPT** | It concedes the operator to EVDI and the observation to Scheerlinck before anyone can take them, which is the correct posture and leaves a measurement nobody has made — but its one exclusivity claim ("DSEC is the only public event–frame dataset with real per-frame exposure intervals") is false and I refute it at source. |
| **07** — Chronofields | **REJECT** | Binary TTC (CVPR 2021) already predicts a **dense, per-pixel** map of *when*, built as a sequence of binary "within time `t`?" classifications — the discrete-hazard parameterization Team 07 imports from DeepHit — so "nobody has put a dense, state-indexed distribution over time on the output side" is false. |
| **08** — Right place, wrong time | **ACCEPT** | Survives my adversarial check, but not intact: **LET-3D-AP** (Waymo Open Dataset's official 2022 camera-only 3D metric) already decomposes detection localization error along a privileged axis, defines a tolerance-parameterized AP permissive along it, re-scores published detectors, and reports the ranking flip — in vision, on a detection benchmark, four years ago. |
| **09** — Change-time / per-pixel clocks | **BORDERLINE** | Best prior-art scholarship in the round by a distance — I verified five of its "zero hits" conjunctions and all five are genuinely zero, and its SECNet "ICML2026 Oral" attribution is correct at source — but its own catch-all row buries Mueggler 2015, which is the per-pixel content-derived clock it says nobody built. |
| **10** — Fusion is ill-typed | **BORDERLINE** | The type discipline itself is unclaimed (`"change of support"` + vision returns nothing relevant), but two of the three works it audits as exemplars of the disease — FAOD and BRENet — are **unrefereed preprints with no journal_ref and no acceptance note**, which the team never says, and C9 (CVPR 2026) already decouples shared vs. private RGB-event features. |

---

## Collision report

The heart of this review. Format per team: the closest work I actually found, the sentence that
establishes it, and a marking of SCOOPED / WOUNDED (with what survives) / CLEAR.

### Team 01 — WOUNDED

**Closest work found: Weng et al., *Event-Based Blurry Frame Interpolation Under Blind Exposure*,
CVPR 2023.** Verified in the CVPR 2023 CVF listing; abstract fetched from
`openaccess.thecvf.com/content/CVPR2023/html/Weng_...`.

> "Existing blurry frame interpolation methods assume a predefined and known exposure time, which
> suffer from severe performance drop when applied to videos captured in the wild. ... we first
> propose an exposure estimation strategy guided by event streams to estimate the lost exposure
> prior, **transforming the blind exposure problem well-posed**."

That sentence is Team 01's Proposition (a) — the frame does not determine its own support, and
the events do — stated as a solved premise in 2023. Team 01 cites EBFI-BE and calls it "closest
work on latent support", which is honest, but then says the missing thing is "(a) the
non-identifiability proposition stated and used". It has been stated and used; EBFI-BE's entire
method exists because of it.

**What survives, and it is enough for a paper:** the TSB *law* (a signed, motion-dependent
localization bias with units), its measurement on public detection/tracking benchmarks, and
support as an input-side latent for **discriminative** perception with time-queried evaluation.
No restoration paper contains any of those. The paper must lead with the measurement, not the
proposition — Team 01 says this itself ("If it leads with the architecture, it is an application
paper"), and it is one notch more true than they think.

**Secondary check.** Team 01's characterization of ETES (ECCV 2022) as handling unknown exposure
"implicitly in features" is **correct** and Team 03's contradicting characterization is not; see
Team 03 below.

### Team 02 — SCOOPED (twice)

**Collision 1 — reviewer01's TSANet finding: VERIFIED, exactly as reported.** I downloaded the
CVPR 2026 PDF (`Sun_Time-Specialized_Event-Image_Alignment_..._CVPR_2026_paper.pdf`, 2.19 MB) and
read the Figure 1 caption:

> "**Figure 1.** Illustration of motion ambiguity in a toy hand–ball example. The top row in (a)
> shows **four possible motion patterns during exposure**: hand moving up while ball moves down,
> both moving up, both moving down, and hand moving down while ball moves up. After temporal
> averaging, **all of them produce the same blurred image** in (b). Relying only on the blurred
> image therefore leads to intrinsic motion ambiguity. The bottom row in (a) shows the
> corresponding **event data, which encodes the underlying motion process and provides strong cues
> to disambiguate the blur**."

Four intra-exposure motion patterns, one identical blurred frame, events disambiguate — the
construction Teams 02 and 10 claim, as the opening figure of an accepted CVPR 2026 paper.
reviewer01 is right and I am confirming it, not repeating it. The body text repeats it:
"different motion trajectories can integrate over the exposure to produce the same blurred image.
This phenomenon is known as the motion ambiguity of motion-blurred frames."

**Collision 2 — and this one is worse, and no other review has drawn it out.** Sayed & Brostow,
*Improved Handling of Motion Blur in Online Object Detection*, CVPR 2021 (verified in the CVPR
2021 CVF listing; abstract fetched):

> "We explore five classes of remedies ... The other four classes of remedies address multi-scale
> texture, out-of-distribution testing, **label generation**, and conditioning by blur-type.
> **Surprisingly, we discover that custom label generation aimed at resolving spatial ambiguity,
> ahead of all others, markedly improves object detection.**"

Team 02's thesis requires that resolving the ambiguity by legislating a better single label is
*unavailable*: "They resolve the ambiguity by *choosing one convention more carefully* — which is
exactly the move we argue is unavailable." But Sayed & Brostow ran that move against four
alternatives and it won. Team 02 is not merely preceded; its central premise has a published
empirical counterexample it cites and does not answer.

**What survives:** convention-marginal conformal coverage as a scoring protocol, and the
frame-mass/event-order identifiability pair. Both are second-order relative to the thesis, and
the thesis is where the paper lives.

### Team 03 — SCOOPED on the headline claim

**The lead from the crashed session is correct. Mueggler, Forster, Baumli, Gallego & Scaramuzza,
*Lifetime Estimation of Events from Dynamic Vision Sensors*, ICRA 2015.** PDF fetched from
`rpg.ifi.uzh.ch/docs/ICRA15_Mueggler.pdf` (743 KB, HTTP 200) and read in full.

Team 03's closing claim is:

> "**Honest verdict after search:** we found no work that predicts a temporal support measure as
> its output, and no work that computes attention as an overlap of supports."

The first half is false. From the abstract:

> "We develop an algorithm that **augments each event with its lifetime**, which is computed from
> the event's velocity on the image plane. The generated stream of augmented events gives a
> continuous representation of events in time, hence enabling the design of new algorithms that
> **outperform those based on the accumulation of events over fixed, artificially-chosen time
> intervals**."

From §III:

> "**The lifetime τ indicates how long it will take for the brightness gradient at the current
> event location to trigger a new event in a neighboring pixel. We assign zero lifetime to noise
> events, τ = 0.**"

And from §I:

> "We consider an event **active** as long as the brightness gradient causing this event is visible
> by the pixel."
> "In contrast to previous algorithms, our method **does not depend on a temporal window
> `[t−Δt, t+Δt]`** around the event time `t`. Thus, we eliminate both a tuning parameter (Δt) and
> its corresponding latency."
> "In a general configuration, however, such a time interval does not exist."

This is, in Team 03's own vocabulary: a per-pixel, content-dependent, scene-driven measure on the
time axis stating **over which instants an observation is a statement about the scene**, emitted
as an output, with an explicit **zero-mass** state for observations that carry no evidence, used
to replace fixed-window aggregation. That is the definition Team 03 gives for `ŝ^E`. It is 2015,
it is from the same lab as half the comparison set, and Team 03's thirteen-row table does not
contain it.

**What survives — and I want to be fair, because it is not nothing:** Mueggler's τ is (i)
*computed* from a plane fit, not learned or supervised; (ii) a scalar duration, not a measure with
shape and mass over the exposure; (iii) event-side only — there is no frame counterpart, no
exposure, no blur constraint; (iv) used for rendering sharp gradient images, never for fusion,
never for abstention. The **support-overlap fusion operator** and the **abstention output** are
still, as far as I can find, unclaimed (`"support overlap" AND "attention"` → 0 relevant;
`"abstain" AND "event camera"` → 0). Team 07 of this round independently rates abstention the
most operationally valuable output of the ten, and I agree.

But the paper cannot be sold as "we predict temporal support and nobody has". It must be sold as
"we make temporal support *bi-modal, learned, and comparable across modalities*, which lifetime
estimation is not". That is a real but much smaller claim, and a CVPR reviewer with a
neuromorphic background will find Mueggler in five minutes.

**Factual error found while checking:** Team 03's row 3 says of Kim et al., ECCV 2022 —

> "Estimates the *unknown exposure/readout time*; ETES selects events by cross-modal correlation
> ... **the estimated quantity is a frame-level scalar (an exposure duration)** used for event
> selection"

The paper's own abstract (fetched from `ecva.net/papers/eccv_2022/.../3601_ECCV_2022_paper.php`)
says otherwise:

> "we first **derive a new formulation** for event-guided motion deblurring by considering the
> exposure and readout time in the video frame acquisition process. ... we design a novel
> **Exposure Time-based Event Selection (ETES) module to selectively use event features by
> estimating the cross-modal correlation** between the features from blurred frames and the events."

There is no scalar exposure duration estimated anywhere. The exposure enters the *formulation*;
the module selects features by correlation. Team 03 has upgraded a feature-selection module into
a support estimator in order to have something to be a degenerate ablation of. Team 01 and Team 05
both describe this paper correctly; Team 03 does not.

### Team 04 — CLEAR

This is the only team whose central novelty claim I could not dent, and I tried hardest here
because it is cheap to check.

Searches run, all against the arXiv API over title+abstract+comments:

- `all:"effective timestamp"` → **0 records.**
- `all:"along-track error"` → 4 records, **none in vision** (visual place recognition adversarial
  attacks, tropical-cyclone assimilation, symplectic integrators, gyroscope Allan deviation).
- `all:"localization error" AND all:"direction of motion"` → **0.**
- `all:"time offset" AND all:"object detection" AND all:"evaluation"` → 1, automotive radar
  interference, irrelevant.
- `all:"event camera" AND all:"label" AND all:"temporal misalignment"` → **0.**
- `all:"event-based" AND all:"object detection" AND all:"evaluation protocol"` → **0.**

And the comparison set: C8 (TTAPFormer, CVPR 2026) names temporal misalignment in frame-event
fusion and fixes it architecturally; C9 (SPFD, CVPR 2026) routes static/dynamic regions to
different modalities; neither reports what time its output is about. **Nobody measures the
effective timestamp of a fused event–RGB task prediction.** Team 04's claim stands.

**One correction Team 04 needs.** Its table cites "TAPFormer (arXiv 2603.04989)" as a preprint.
It is now **TTAPFormer, CVPR 2026** (verified in the CVF CVPR 2026 listing:
`Liu_TTAPFormer_Robust_Arbitrary_Point_Tracking_via_Transient_Asynchronous_Fusion_of_CVPR_2026_paper.html`),
and its abstract explicitly says prior frame-event fusion is "synchronous or non-adaptive, leading
to **temporal misalignment** and severe degradation when one modality fails." That upgrades it
from a preprint footnote to an accepted CVPR paper that names Team 04's phenomenon and then does
*not* measure it — which is a much better citation for Team 04 than the one they have.

**Shared exposure with Team 08:** see LET-3D-AP below. Team 04's `δ̂ = e_∥/‖v‖` uses the same
along/cross decomposition. Team 04 does not claim to invent it; it should still cite LET-3D-AP.

### Team 05 — CLEAR (thin)

**Closest work: Yang et al., *Latency Correction for Event-guided Deblurring and Frame
Interpolation*, CVPR 2024.** Verified in the CVPR 2024 CVF listing; abstract fetched:

> "This paper addresses the challenge of latency in event cameras — **the temporal discrepancy
> between the actual occurrence of changes in the corresponding timestamp assigned by the
> sensor**. ... we propose a latency correction method based on a **parameterized latency model**
> ... and reformulate the event-based double integral model differentiable to latency."

Team 05's characterization — a per-event *location* shift, i.e. a first moment, with the frame's
kernel still assumed a known box — is accurate. Their delta (the *width*, the second moment, and
the impossibility that no offset can substitute for it) is not in that paper.

Searches that came back empty and support them: `all:"temporal support" AND all:"event camera"`
→ **0**; nothing in my twelve-paper comparison set estimates a temporal *kernel* on either branch.

**But** I record the reviewer's real objection, which is not prior art: the theory tier is the
Fourier transform of a box, conceded by the team ("Our theory's true ancestor, and we say so"),
and what is left that is genuinely theirs is one measurement, OBD. A paper whose novelty is one
measurement in a regime that may be sub-pixel on every reachable dataset is a BORDERLINE paper,
and reviewers 03, 06, 09 and 10 independently converged on that. I do not overturn them.

### Team 06 — CLEAR on the science, one exclusivity claim REFUTED

Prior-art posture is the best in the round: it concedes mEDI's `J` (keeping their symbol), concedes
EVDI Eq. (19)–(20) gets the two-frame form right, and elevates Scheerlinck et al. (ACCV 2018) —
who saw the effect and dismissed it by assertion — to its most important citation. There is
nothing left for me to take.

**Factual error, `team06.md` line ~374.** The claim:

> "DSEC ships `image_exposure_timestamps_left/right.txt` per sequence and is **the only public
> event–frame dataset with real per-frame exposure intervals**."

Refuted at source, in two steps.

**Step 1 — the AEDAT4 file format itself carries per-frame exposure.** From the iniVation
`dv-processing` frame definition (`gitlab.com/inivation/dv/dv-processing`,
`include/dv-processing/data/frame_base.hpp`, HTTP 200):

> `// Timestamp represents start of exposure, or closest possible moment to it.`
> `dv::Duration exposure;`
> `Frame(int64_t _timestamp, int64_t _timestampStartOfFrame, int64_t _timestampEndOfFrame,`
> `      int64_t _timestampStartOfExposure, int64_t _timestampEndOfExposure, ...)`
> `      exposure{_timestampEndOfExposure - _timestampStartOfExposure},`
> `VT_TIMESTAMPSTARTOFEXPOSURE = 10,`

Exposure start and end are first-class flatbuffer fields of every AEDAT4 frame.

**Step 2 — a public event–frame dataset ships in that format.** FE108's own dataset page
(`zhangjiqing.com/dataset/`, HTTP 200):

> "**To load the aedat4 file**, you should install the required toolkit dv-gui."

So FE108/FE240hz (ICCV 2021) carries real per-frame exposure start/end, as does any other DAVIS
dataset distributed as `.aedat4`. This independently confirms what reviewer01 reported.

**Does it hurt Team 06?** Barely, and I want to be precise rather than punitive. DSEC remains
the right anchor: it publishes the intervals as a plain text file, its exposures span 118–14996 µs
(a factor of 127, per the verified brief), and reviewer04 reports the FE108 access portal is
currently dead. The *plan* is unaffected. What must go is the word "only" — it is an exclusivity
claim of exactly the kind the rubric flags ("a 'first to' claim that a fifteen-minute search
defeats"), and it took me under fifteen minutes.

### Team 07 — SCOOPED on the headline claim

Team 07's one-line positioning is:

> "Time surfaces put time on the input side; INRs put time on the query side; TTC puts one time on
> the output side. **Nobody has put a dense, state-indexed, censored distribution over time on the
> output side**, and nobody has noticed that this is the natural home for a frame's exposure
> interval."

Their table concedes only *scalar* TTC ("one scalar per object under a looming model, vs. a dense
state-indexed field; a point estimate, vs. a distribution").

**Badki, Gallo, Kautz & Sen, *Binary TTC: A Temporal Geofence for Autonomous Navigation*,
CVPR 2021.** Verified in the CVPR 2021 CVF listing; abstract fetched:

> "However, **regressing TTC for each pixel** is not straightforward, and most existing methods
> make over-simplifying assumptions about the scene. We address this challenge by **estimating TTC
> via a series of simpler, binary classifications. We predict with low latency whether the observer
> will collide with an obstacle within a certain time** ... Our approach can also **estimate
> per-pixel TTC with arbitrarily fine quantization (including continuous values)**, when the
> computational budget allows for it."

This is dense (per-pixel, not per-object), it is state-indexed (the query is a *state* — "will the
observer's plane be reached" — and the answer is a time), and the estimator is a **sequence of
thresholded binary decisions over the time axis**, which is precisely the discrete-time hazard
parameterization Team 07 imports from DeepHit. "Arbitrarily fine quantization" is a discretized
distribution over `t`. Team 07's sentence is false in three of its four qualifiers.

**What survives:** (i) the *censoring* identification — an event as an exact observation, a frame
as interval-censored, a non-crossing as right-censored — which Binary TTC has nothing
corresponding to, since it is supervised with dense TTC ground truth; (ii) the `∅` atom ("never");
(iii) frames entering the likelihood at all. Note that reviewer01 argues (i) is physically false
because event timestamps carry illumination-dependent photoreceptor latency — and C7 (Yang,
CVPR 2024) is exactly the accepted paper that establishes that latency exists and is worth
correcting. If reviewer01 is right, then after Binary TTC removes the "first dense time field"
claim, what is left is (ii) and (iii) resting on a misspecified likelihood. That is why my verdict
is REJECT rather than BORDERLINE.

Empty searches that Team 07 ran and I **confirm** are genuinely empty:
`all:"event camera" AND all:"censored"` → **0**; `all:"crossing time" AND all:"event camera"` →
**0**; `all:"event camera" AND all:"temporal uncertainty"` → **0**. All three reproduce. See the
methodological warning at the end of this section about what that does and does not prove.

### Team 08 — WOUNDED (the adversarial check the brief asked for)

The brief asked me specifically whether an along-track/cross-track error decomposition has already
been applied to event or video object detection, and whether anyone has already re-scored event
detectors for temporal bias. The answers are **yes, in vision, as a deployed benchmark metric**,
and **no**, respectively.

**Hung, Casser, Kretzschmar, Hwang & Anguelov (Waymo LLC), *LET-3D-AP: Longitudinal Error
Tolerant 3D Average Precision for Camera-Only 3D Detection*, arXiv 2206.07705v2.** This is not an obscure preprint: its
own arXiv comment field reads *"Find the primary metrics for the **2022 Waymo Open Dataset 3D
Camera-Only Detection Challenge** at waymo.com/open/challenges/2022/3d-camera-only-detection/.
Find the code at github.com/waymo-research/waymo-open-dataset."* It is the official metric of a
major benchmark. I fetched and extracted the full PDF.

From §II (Related Work):

> "We **decompose the localization error into a lateral error and a longitudinal error**. We find
> that the longitudinal error is more prominent in camera-only 3D detection. We therefore propose
> **longitudinal error tolerant (LET) metrics that are more permissive with respect to the
> longitudinal localization error**."

From §III:

> "The **longitudinal error `e_lon` is the error along the line of sight** of the ground truth box,
> giving `e_lon = (e_loc · u_G) · u_G`"
> "The **lateral error `e_lat`** is the distance between the predicted [box and the line of sight]"

From the abstract:

> "our novel longitudinal error tolerant metrics, LET-3D-AP and LET-3D-APL, **allow longitudinal
> localization errors of the prediction boxes up to a given tolerance** ... **Surprisingly, we find
> that state-of-the-art camera-based detectors can outperform popular LiDAR-based detectors with
> our new metrics past at 10% depth error tolerance**"

Compare Team 08's thesis sentence:

> "we give an identifiable decomposition of published error into a spatial part (pixels ⟂ to the
> motion) and a temporal-support part (milliseconds ∥ to the motion), **re-score released
> checkpoints with it, and show the ranking is not the ranking mAP reports**."

Structurally these are the same paper: decompose localization error along a physically privileged
unit vector; define an AP that is permissive along that axis, parameterized by a tolerance;
penalize residual error along it with an affinity term (LET-3D-**APL**); re-score published
detectors; report that the ranking changes. Team 08's `AP^⊥`, `AP`, `R` and `τ_max` map one-to-one
onto LET-3D-AP, 3D-AP, and the tolerance parameter. And the ranking-flip result — "camera
detectors beat LiDAR detectors past 10% tolerance" — is the same *kind* of finding, already
delivered.

**Team 08's escape clause holds, narrowly.** Its Death-4 section says: "If someone has applied it
as an *evaluation* metric **in event vision**, our contribution collapses to the protocol and the
ranking evidence." LET-3D-AP is camera/LiDAR 3D detection, not event vision. So the escape clause
is technically satisfied. But the table row that concedes the borrowing cites only air-traffic
surveillance (arXiv 2008.06352) and "trajectory prediction", and claims the novelty is
"(a) recognising that event–RGB benchmarks are the setting where the borrowed device is decisive".
That claim is now weaker: the device was already recognized as decisive **in a vision detection
benchmark**, and was adopted as an official challenge metric on that basis.

**What genuinely survives, and it is a paper:**

1. **The axis is the object's velocity, not the sensor's line of sight.** LET's privileged axis is
   fixed by geometry (range); Team 08's is fixed by the scene (motion), which is what makes the
   division by `‖v‖` meaningful.
2. **The unit is milliseconds.** LET-3D-AP tolerates longitudinal error and reports it as a
   fraction of range. Nothing in LET converts the tolerated component into a *time*. Team 08's
   `δ̂ = e_∥/‖v*‖` is the step LET does not take, and it is the step that makes the quantity
   comparable to a declared temporal support.
3. **`τ_max` is not a free parameter.** LET's tolerance is a swept percentage of range. Team 08
   derives `τ_max = (w_G + w_P)/2` from the benchmark's and the method's own published
   specifications. That is a real methodological improvement over LET and Team 08 should say so.
4. **The over-identification test.** One scalar `δ` must explain the translation channel *and* the
   scale channel. LET has no second channel and therefore no falsification test. Reviewer02
   correctly identifies this as Team 08's strongest structural asset; it survives untouched.
5. **C3, the pre-registered architecture prediction.** Predicting `τ̂ ∈ [−35, −10] ms` from RVT's
   declared 50 ms backward window *before* measuring is something no metric paper in vision has
   done, and it is what separates "a physical quantity" from "a metric I invented".
6. **E0, the label forensics, is completely untouched.** Nothing in LET-3D-AP, and nothing I found
   anywhere, asks whether a benchmark's high-rate ground truth is recoverable from its own
   interpolation prior. `all:"ground truth" AND all:"interpolation" AND all:"event camera" AND
   all:"benchmark"` → **0**. This is the strongest single deliverable in the entire round and it
   costs a 4.7 MB label file.

**Second half of the adversarial check — has anyone re-scored event detectors for temporal bias?**
No. Searches, all empty or irrelevant: `all:"event camera" AND all:"label" AND all:"temporal
misalignment"` → 0; `all:"event-based" AND all:"object detection" AND all:"evaluation protocol"`
→ 0; `all:"annotation" AND all:"time offset" AND all:"event camera"` → 0; `abs:"error
decomposition" AND abs:"object detection"` → 1 (a small-object frequency-representation paper,
irrelevant); `abs:"streaming perception" AND abs:"metric"` → 6, all compute-latency work
(Towards Streaming Perception ECCV 2020, StreamYOLO CVPR 2022, a NeurIPS 2024 stereo streaming
detector, CorrDiff, SPOT-Bench 2026) with **zero** event-camera entries — Team 08's claim "we
found no event-camera sAP work" reproduces. I also swept the full CVPR 2026 event listing (38
event papers extracted from the CVF index) and there is no benchmark-integrity or
temporal-metric paper among them.

**Net.** Team 08 remains the strongest idea in the round on execution certainty, and my check did
not kill it. But its self-scored **Novelty 7/10 is now 5/10**, and it must cite LET-3D-AP in the
first version of the related-work table, not the rebuttal. See "My winner and its fatal flaw".

### Team 09 — CLEAR (and the best-verified document in the round)

I ran Team 09's own empty-conjunction claims as literal queries. All reproduce:

- `all:"temporal support" AND all:"event camera"` → **0**
- `all:"reparameterization invariance" AND all:"event"` → **0**
- `all:"change of support" AND all:"vision"` → 14 records, **none** in the geostatistical sense
  (agility definitions, DreamPose, sign-language pose stitching, …)

I also spot-checked three of its attributions at source and all three are correct:

- **SECNet.** Team 09 cites "ICML 2026 (Oral)". arXiv 2412.20803v2, *Scalable Event Cloud Network
  for Event-based Classification*, comment field: `ICML2026 Oral`. Correct.
- **Neural Events, arXiv 2606.19835.** Team 09 calls it "a *tokenizer* — it decides *when to
  emit*". The abstract: "a framework to **re-tokenize** event streams into a small set of highly
  informative *neural events*, each representing a local spatio-temporal context window with a
  discrete learnable code. **Every time this code flips, a neural event is triggered**, yielding a
  highly compressed data stream." Correct, and its "strategic risk, not conceptual overlap"
  reading is right.
- **ASTW, CVPR 2026.** Verified accepted (CVF listing), abstract confirms the max-entropy
  patch-level window criterion and the HetVel dataset. Correct.

**The one thing Team 09 buried.** Its table has a catch-all final row — "Event Lifetime; VK-SITS;
ATSLTD; Adaptive Temporal Sampling; …" — dismissed with "each emits a duration or decay constant
in seconds from an *estimated* velocity or density". That dismissal is *correct* for Mueggler 2015
(τ comes from a plane fit to the Surface of Active Events, i.e. an estimated velocity, and is a
duration in seconds — exactly Team 09's own critique). So Team 09 is defended on the merits. But
lumping the 2015 paper that first said "**In a general configuration, however, such a time interval
does not exist**" into an eight-item catch-all row is a presentation error: that sentence is
Team 09's thesis, twelve years early, and a reviewer who spots it in the catch-all row will read
the whole table as evasive. Promote it to its own row and answer it directly.

### Team 10 — WOUNDED (by the status of its own subjects)

**reviewer10's finding, confirmed at source.** I queried the arXiv API for both:

- **FAOD**, arXiv **2412.04149v2**, *Frequency-Adaptive Low-Latency Object Detection Using Events
  and Frames*: `journal_ref` = **none**, `comment` = **none**. Two versions, Dec 2024, no
  acceptance note twenty-one months later.
- **BRENet**, arXiv **2505.01548v2**, *Learning Flow-Guided Registration for RGB-Event Semantic
  Segmentation*: `journal_ref` = **none**, `comment` = `"20 pages, 14 figures"`. No venue.

Neither appears in the CVPR 2024/2025/2026, ICCV 2025, ECCV 2024 or NeurIPS 2024 title listings I
grepped (19,210 titles). Both are unrefereed preprints. **No team says this.** Team 10 calls
BRENet "the strongest statement of the assumption we kill" and Team 09 calls it "the most
dangerous competitor for 'we formalize it'"; Teams 01, 04, 05, 07, 08 and 09 all treat FAOD as the
antagonist. Building an indictment of "the field" on two preprints is a rebuttal liability: a
reviewer can say the assumption you kill was never accepted anywhere.

**Also note the title drift.** Team 10's table and Team 04's table both call 2505.01548
"*Rethinking RGB-Event Semantic Segmentation with a Bidirectional Motion-enhanced Event
Representation*". The v2 title is "*Learning Flow-Guided Registration for RGB-Event Semantic
Segmentation*". `ti:"Bidirectional Motion-enhanced Event Representation"` returns **0**. Minor,
but it means both teams are quoting a superseded version.

**Closest *accepted* neighbour I found: C9, *Beyond Duality* (SPFD), CVPR 2026.**

> "The existing RGB-Event object detectors all struggle to fully utilize the fusion features of two
> modalities, but **do not explicitly disentangle shared vs. private features to dedicated
> branches**. ... a **frequency-domain coherence-based Shared and Private Features Decoupling**
> method ... selectively emphasizing texture-rich RGB features in **static** regions and
> motion-sensitive event features in **dynamic** regions."

This is not Team 10's type system, and I will not overstate it: SPFD decouples by spectral energy,
not by measurement order, and it states no legality rule. But it is an accepted CVPR 2026 paper
that (a) says fusing the two modalities undifferentiated is the problem and (b) routes static and
dynamic regions to different modalities — which is a coarse, empirical version of Team 10's
`EU(s)` claim that event utility is regime-dependent. Team 10 must cite it, and it slightly
deflates "no work we found claims a support/type discipline".

**What survives:** the type discipline itself is genuinely unclaimed. My searches for
change-of-support in vision, support-overlap attention, and legality rules for cross-modal mixing
all came back empty. The novelty is real; it is the *indictment* that is built on sand.

---

### Searches and fetches run — including the empty ones

So a later reader knows exactly what was and was not checked.

**Proceedings listings downloaded and grepped locally (19,210 titles).**
`openaccess.thecvf.com/CVPR2024?day=all` (2,716 titles), `CVPR2025` (2,871), `CVPR2026` (4,042),
`ICCV2025` (2,701), `ecva.net` ECCV 2022+2024 (2,387 for 2024; 6,165 rows total),
`papers.nips.cc` NeurIPS 2024 Main (4,034) + Datasets&Benchmarks (459). Also downloaded
`CVPR2021` and `CVPR2023` listings for the older targets. `openaccess.thecvf.com/ECCV2024` is a
404 — ECCV lives at ecva.net, noted in case a later reviewer wastes a fetch on it.

**Full PDFs downloaded and text-extracted (4).** TSANet CVPR 2026 (2.19 MB), ASTW CVPR 2026
(3.14 MB), Mueggler ICRA 2015 (743 KB), LET-3D-AP (arXiv 2206.07705v2).

**Abstract pages fetched individually (11).** TSANet, ASTW, Ev-3DOD, Unleashing the Temporal
Potential (ICCV 2025), Bridge Frame and Event, TTAPFormer, Beyond Duality, EBFI-BE (CVPR 2023),
Sayed & Brostow (CVPR 2021), Latency Correction (CVPR 2024), AFNet (CVPR 2023), Binary TTC
(CVPR 2021), ETES (ECCV 2022, via ecva.net).

**Source-file fetches (2).** `gitlab.com/inivation/dv/dv-processing` →
`include/dv-processing/data/frame_base.hpp` (AEDAT4 exposure fields). `zhangjiqing.com/dataset/`
(FE108 format statement).

**arXiv API queries — HITS.**

| Query | Result |
|---|---|
| `all:"longitudinal error" AND all:"detection"` | **LET-3D-AP (2206.07705)** — the Team 08 wound |
| `all:"event camera" AND all:"lifetime"` | 6 — incl. *Stereo Event Lifetime and Disparity Estimation* (ECMR 2019), confirming lifetime is a live line |
| `ti:"Frequency-Adaptive Low-Latency Object Detection"` | 1 — FAOD 2412.04149v2, no journal_ref, no comment |
| `ti:"Spiking Patches"` | 1 — 2510.26614v1, no venue: **preprint** |
| `all:"SECNet" AND all:"event"` | 1 — 2412.20803v2, comment `ICML2026 Oral`: **verified accepted** |
| `abs:"streaming perception" AND abs:"metric"` | 6 — all compute-latency, **zero event-camera** |
| `id_list` lookups | 2606.19835 (Neural Events), 2412.04149 (FAOD), 2505.01548 (BRENet), 2206.07705, 2604.24317 |

**arXiv API queries — EMPTY (this is the part other reviewers omit).**

| Query | Records |
|---|---|
| `all:"temporal support" AND all:"event camera"` | 0 |
| `all:"reparameterization invariance" AND all:"event"` | 0 |
| `all:"event camera" AND all:"censored"` | 0 |
| `all:"crossing time" AND all:"event camera"` | 0 |
| `all:"event camera" AND all:"temporal uncertainty"` | 0 |
| `all:"effective timestamp"` | 0 |
| `all:"along-track" AND all:"object detection"` | 0 |
| `all:"localization error" AND all:"direction of motion"` | 0 |
| `all:"temporal error" AND all:"object detection" AND all:"benchmark"` | 0 |
| `all:"latency" AND all:"mean average precision" AND all:"event camera"` | 0 |
| `all:"event camera" AND all:"label" AND all:"temporal misalignment"` | 0 |
| `all:"event-based" AND all:"object detection" AND all:"evaluation protocol"` | 0 |
| `all:"annotation" AND all:"time offset" AND all:"event camera"` | 0 |
| `all:"ground truth" AND all:"interpolation" AND all:"event camera" AND all:"benchmark"` | 0 |
| `all:"abstain" AND all:"event camera"` | 0 |
| `all:"support overlap" AND all:"attention"` | 2, both OOD-generalization, irrelevant |
| `ti:"Bidirectional Motion-enhanced Event Representation"` | 0 (superseded title) |
| `all:"lateral" AND all:"longitudinal" AND all:"miss rate" AND all:"motion forecasting"` | 0 |

**NOT checked, and a later reader should treat these as open.** IEEE Xplore, TPAMI/TIP/RA-L (no
open listing grepped — so ICRA/IROS/RA-L collisions beyond Mueggler are unswept, and Mueggler is
itself an ICRA paper, which tells you where the risk lives); ICLR/ICML/AAAI proceedings listings;
CVPR/ICCV/ECCV **workshop** proceedings; NeurIPS 2025; the 2026 ECCV cycle; Google Scholar
citation graphs.

**A methodological warning that applies to five of these ten submissions.** Teams 07 and 09 both
rest novelty arguments on zero-hit arXiv conjunctions, and Team 09's document is explicit that
`reparameterization invariance ∧ event` = "zero hits". Every one of those conjunctions reproduces
— and they are worth almost nothing. arXiv's `all:` field indexes title, abstract, authors and
comments, **not full text**. Mueggler et al. contains none of the strings "temporal support",
"validity measure" or "sub-probability measure", and it is the paper that kills Team 03. Binary
TTC contains none of "censored", "chronofield" or "state-indexed", and it is the paper that kills
Team 07. LET-3D-AP contains neither "along-track" nor "event camera", and it is the paper that
wounds Team 08. **A zero-hit keyword conjunction is evidence about vocabulary, not about ideas**,
and any submission that offers one as a novelty argument is handing a reviewer a free rebuttal.
Every team in this round that has a "we searched and found nothing" paragraph should replace it
with "here is the closest work in each adjacent field and here is the sentence".

---

## Detailed review

Rubric items 1–8 per idea, tight. Items 5 and 6 are where my specialism earns its place.

### Team 01 — A Frame Is Not a Timestamp

1. **Verdict: BORDERLINE.**
2. **Summary.** Argues that `(t₀, T)` is unrecoverable from a blurred frame alone by a
   reparameterization argument, that every dataloader therefore fixes it by convention, and that
   this produces a signed, speed-dependent localization bias (the "TSB law") which it proposes to
   measure on DSEC/FE240hz and remove by jointly inferring the support from events and blur. The
   document is unusually clear that the architecture is not the contribution and that leading with
   it means rejection. Its validation instrument — SIE, `|T̂ − T|` in ms against DSEC's shipped
   exposure timestamps, a file never seen in training — is the single best-designed check in the
   round, and I agree with reviewer03 on that.
3. **Strongest reason to accept.** SIE is falsifiable against a published ground truth that the
   model never sees, on a dataset the brief has already verified byte-for-byte (118–14996 µs across
   18 sequences). Very few ideas here can be checked against a number someone else recorded.
4. **Strongest reason to reject.** Its Proposition (a) is the operating premise of EBFI-BE
   (CVPR 2023), which says in its abstract that estimating the exposure prior from events
   "transform[s] the blind exposure problem well-posed". Formalizing an accepted premise is a
   preliminaries section, not a contribution, and the paper allocates it a contribution slot.
5. **Factual errors.** (i) Its characterization of ETES/Kim et al. as ECCV 2022 is correct
   (verified in ecva.net); good. (ii) reviewer01 reports its Fig-1a prediction (left/right
   exposure-midpoint difference ≥ 1 ms on a substantial fraction of frames) is falsified by
   measurement — median 8–72 µs, 0.00% above 1 ms. I did not re-measure but the brief independently
   states left/right divergence is "two orders of magnitude smaller than the window width itself"
   and that "an argument resting on left/right divergence rests on the smaller effect and should be
   marked down". Consistent. Delete Fig-1a.
6. **Claim exceeding evidence.** "A motion-blurred frame carries **no information whatsoever**
   about the absolute time interval it integrated" — "no information whatsoever" is an
   information-theoretic claim the document does not prove; blur *extent* bounds `T` given a speed
   prior, and vignetting/noise level correlate with exposure in practice. Soften to
   "does not identify".
7. **Experiment a hostile reviewer demands.** Detection/tracking mAP with the estimated support
   fed in, versus the same model with the *published* DSEC exposure interval fed in as an oracle.
   If the oracle does not beat the convention baseline, the whole latent-variable apparatus is
   unnecessary. Its absence is **fatal** — this is a one-day experiment and it decides the paper.
8. **Fixes, ranked.** (1) Cite EBFI-BE as the source of the premise and re-scope contribution (a)
   to "stated for discriminative perception". (2) Delete the left/right-divergence figure.
   (3) Run the oracle-support upper bound before anything else. (4) Replace FE240hz-dependent
   plots — reviewer04 reports the portal returns a zero-byte 416 — with DSEC-Det, which has track
   IDs. (5) Soften "no information whatsoever" and "we prove".

### Team 02 — No State at *t*

1. **Verdict: REJECT** (fatal to this framing; the conformal-coverage protocol is salvageable
   inside another paper).
2. **Summary.** Claims the label attached to a blurred frame is an unspecified functional of the
   state's occupancy measure over the exposure, so the prediction target should be the measure —
   frame supplies mass, events supply order — scored by convention-marginal coverage rather than
   point IoU. Its Figure 2 is a time-reversal pair: two intra-exposure motions producing an
   identical blurred frame, disambiguated only by events. It is metric-literate (CI-AP degenerates
   to AP, so every published number remains locatable) and it is honest that the physics is 2010.
3. **Strongest reason to accept.** Moving the recovered quantity out of image space into
   *supervision and evaluation* space is a genuinely different move from every restoration paper,
   and reviewer06 is right that no restoration paper can contain it.
4. **Strongest reason to reject.** Both of its two most vivid assets are taken. Figure 2 is
   TSANet's Figure 1 (CVPR 2026), quoted in full above. And its premise that legislating a single
   better label is unavailable is contradicted by Sayed & Brostow (CVPR 2021), who tried exactly
   that against four alternatives and report it "**ahead of all others, markedly improves object
   detection**".
5. **Factual errors.** Its Sayed & Brostow row describes the paper as fixing the problem by
   "re-generating a better single label" — accurate — but omits that this was the *winning* remedy
   of five, which is the fact that damages Team 02. Selective description of a cited paper is worse
   than not citing it.
6. **Claim exceeding evidence.** "Searches covering CVPR/ICCV/ECCV/NeurIPS/ICLR 2023–2026 and
   arXiv returned no combination of these." CVPR 2026 contains TSANet. The search did not cover
   what it says it covered.
7. **Experiment a hostile reviewer demands.** Show that the convention spread is large on real
   data — i.e. that the choice among {start, midpoint, end, union} moves mAP by more than bootstrap
   noise on a public benchmark. Its own indictment currently rests on a Kendall τ over **five**
   trackers (reviewer03's finding), which is one or two swaps. Absence is **fatal**: without a
   large measured spread there is no problem.
8. **Fixes, ranked.** (1) Cite TSANet and replace Figure 2 with something it does not contain.
   (2) Answer Sayed & Brostow head-on with a measurement, not an assertion. (3) Widen the tracker
   pool past five. (4) Fix the `ν=0, β=3` arithmetic that reviewers 02, 07 and 08 independently
   report evaluates to `D = 1.0`, not `< 0.05`. (5) Split the conformal half out; it is a second
   paper.

### Team 03 — Temporal Support Fields

1. **Verdict: REJECT** (fatal to the "first-to" framing and to the frame-branch identifiability;
   the abstention output deserves to be rescued into another submission).
2. **Summary.** Inverts the representation unit: predict, per pixel and per modality branch, a
   sub-probability measure on the time axis stating over which instants an observation speaks and
   with how much evidence; then make fusion an *overlap* of supports rather than a feature
   similarity, so that non-overlap becomes an explicit, abstainable output. Its thirteen-row prior
   art table is the longest in the round. It plots performance against ground-truth support overlap
   `O*` and predicts a cliff.
3. **Strongest reason to accept.** Abstention — "I hold no observation of this pixel at the
   requested instant" — is the most operationally valuable output any of the ten proposes, and
   `all:"abstain" AND all:"event camera"` returns **0**. Team 07 of this round independently
   reached the same conclusion about its value.
4. **Strongest reason to reject.** The load-bearing novelty sentence is false. Mueggler et al.
   (ICRA 2015) augments every event with a lifetime — "**how long it will take for the brightness
   gradient at the current event location to trigger a new event in a neighboring pixel**", with
   `τ = 0` for noise — explicitly to escape "fixed, artificially-chosen time intervals". That is a
   per-pixel content-dependent temporal support emitted as output, with a zero-mass state, eleven
   years old, absent from a thirteen-row table.
5. **Factual errors.** (i) Row 3 attributes to Kim et al. (ECCV 2022) the estimation of "a
   frame-level scalar (an exposure duration)"; the paper's abstract describes a *formulation* that
   considers exposure and readout time plus a module that "selectively use[s] event features by
   estimating the cross-modal correlation". No duration is estimated. Correct the row or drop the
   "degenerate ablation" framing that depends on it. (ii) Row 3 labels that ECCV 2022 paper
   "REFID"; REFID is Sun et al., *Event-based Frame Interpolation with Ad-hoc Deblurring*,
   CVPR 2023. Two different papers merged into one row. Team 05 gets this right and Team 03 does
   not.
6. **Claim exceeding evidence.** "**we found no work that predicts a temporal support measure as
   its output**" — refuted above. Also "The idea appears open", which follows from it.
7. **Experiment a hostile reviewer demands.** The `O*` cliff plot on *real* data. Reviewer03's
   objection is decisive and I concur: `O*` is a simulator bookkeeping variable. A hostile reviewer
   will ask for the x-axis to exist outside the authors' renderer. Its absence is **fatal**.
8. **Fixes, ranked.** (1) Add Mueggler 2015 as row 1 and restate the claim as "bi-modal, learned,
   comparable supports", which is defensible. (2) Fix the ECCV 2022 / CVPR 2023 conflation.
   (3) Find a real-data proxy for `O*` or drop the cliff plot. (4) Answer reviewer02's counting
   argument: `B(x) = Σ_k ŝ^F_k Î(x, τ_k)` is one equation in `K` unknowns per pixel. (5) Consider
   resubmitting as an *abstention* paper, where the novelty is intact.

### Team 04 — When Is Your Prediction?

1. **Verdict: ACCEPT.**
2. **Summary.** Claims a fused event–RGB predictor trained to output the state "at `t`" actually
   outputs the state at an evidence-weighted time centroid `τ̂` that moves with exposure length,
   event-window offset, speed and texture — and, critically, differs between regions of a single
   frame, so `σ_τ > 0` and the prediction has no single timestamp. Proposes to measure `τ̂` by
   argmin over a continuous GT trajectory, with a frame-only/event-only control. The pilot is three
   days, ~3 GPU-h and zero downloads.
3. **Strongest reason to accept.** On my instrument this is the cleanest novelty in the round.
   `all:"effective timestamp"` → **0 records**. No paper in my twelve-paper comparison set reports
   what time its output refers to, including the two CVPR 2026 papers (C8, C9) that name temporal
   misalignment in frame-event fusion and then fix it architecturally without measuring it. And
   `σ_τ > 0` — within-frame dispersion — is a quantity no restoration formulation can produce even
   in principle.
4. **Strongest reason to reject.** `σ_τ > 0` has no null model. Reviewer03 and reviewer10 both make
   this point and they are right: GT interpolation noise, a flat argmin, or ordinary spatial error
   all yield `σ_τ > 0` for free. The paper's declared kill shot currently cannot fail, which means
   it also cannot succeed.
5. **Factual errors.** (i) "TAPFormer (arXiv 2603.04989)" is now **TTAPFormer, CVPR 2026**
   (verified in the CVF listing). Upgrade the citation — its abstract names "temporal
   misalignment" in frame-event fusion, which strengthens Team 04's framing. (ii) It cites BRENet
   as "arXiv 2505.01548, 2025" under the title *Flow-Guided Registration for RGB–Event Semantic
   Segmentation*; the current title is *Learning Flow-Guided Registration for...* and the paper is
   an **unrefereed preprint** — say so, since Team 04 leans on it as "the strongest competing
   framing". (iii) FAOD likewise: still a preprint, no journal_ref, no acceptance comment.
6. **Claim exceeding evidence.** "no paper measures the effective timestamp of a fused event–RGB
   task prediction, **none reports that it varies within a frame**, and none frames event–RGB
   fusion as a change-of-support problem." The first and third I verified. The second is not a
   search result, it is a consequence of the first, and stating it as a separate finding
   overstates the sweep.
7. **Experiment a hostile reviewer demands.** A synthetic null: inject known `τ` and known
   isotropic spatial noise with *no* temporal structure, and show the estimator returns
   `σ_τ ≈ σ_noise/‖v‖` and not more. Absence is **not fatal** — it is a half-day of CPU and it is
   already implicitly in their C4-equivalent — but it must be in the paper, first figure of the
   supplement.
8. **Fixes, ranked.** (1) Build the `σ_τ` null before measuring anything. (2) Resolve the internal
   contradiction reviewer01 found: §4.1 makes `w(t)` content-dependent *within* one exposure, §8.3
   then asserts the frame-only control gives `σ_τ ≈ 0`. One of the two is wrong and it is the
   paper's most important control. (3) Cite LET-3D-AP for `e_∥/‖v‖`. (4) Re-found the data plan on
   DSEC-Det + EVIMO2 (reviewer04 reports three of four named sources dead). (5) Update TTAPFormer
   and flag FAOD/BRENet as preprints.

### Team 05 — No Offset Can Fix a Width

1. **Verdict: BORDERLINE.** One unfixed structural problem: the novelty reduces to a single
   measurement in a regime the only reachable real dataset may not enter.
2. **Summary.** Recasts event–frame temporal calibration as identification of a *pair* of temporal
   support kernels rather than a scalar delay, proves (T1) that a unit-modulus phase shift cannot
   correct a modulus mismatch with spectral zeros, predicts (T2) a speed-dependent residual with
   nulls at `k/(vT)`, and proposes to measure that the best-fit offset on a hardware-synced rig is
   not a rig constant (OBD, `dδ̂/db`). It correctly identifies Raskar's coded exposure as its
   ancestor and says so.
3. **Strongest reason to accept.** The theory tier is a CPU FFT experiment that cannot fail to
   produce a figure, and OBD is the rare invented metric that needs **no labels at all** and has a
   principled null (a rig constant must have zero drift). On a 9 GB contended GPU that matters.
4. **Strongest reason to reject.** After conceding Raskar (spectral nulls) and EDI (forward model),
   what remains is one Fourier identity plus one measurement, and reviewer07 recomputed DSEC and
   reports daytime `b = vT < 1 px`, below the effect's own stated onset of 2 px. A correct and
   irrelevant theorem is a BORDERLINE paper.
5. **Factual errors.** Its Yang et al. (CVPR 2024) row is **accurate** — I fetched the abstract and
   it is indeed a per-event latency model, a first moment, with the frame kernel assumed known.
   Its TSANet row (CVPR 2026, "Sun et al.") is **accurate** on venue and mechanism; verified in the
   CVF listing and PDF. Its EGER row (Zhang et al., ICCV 2023) I did not verify. Reviewer02 reports
   a sign error in T2's closed form; not my lane, but if correct it inverts the headline.
6. **Claim exceeding evidence.** "The CVPR 2026 proceedings contain 60+ event papers and none is
   about event–frame temporal support or exposure-aware calibration." I extracted 38 event papers
   from the CVPR 2026 CVF index by keyword; the count "60+" is not reproducible from the public
   listing without saying how it was made. The *conclusion* is right — I found none either — but
   stating an unverifiable count next to a novelty claim is exactly the pattern the rubric flags.
7. **Experiment a hostile reviewer demands.** Show `b ≥ 2 px` on real hardware-synced data before
   the theory section. Absence is **fatal to the real-data half** and the team knows it — they
   scheduled a day-one check, which is to their credit.
8. **Fixes, ranked.** (1) Run the `b ≥ 2 px` check on day one and be willing to pivot to the
   night-time DSEC sequences (10.1× wider windows, per the verified brief). (2) Have someone
   re-derive T2 independently given reviewer02's sign-error report. (3) Replace "60+ event papers"
   with a reproducible count or delete it. (4) Lead with OBD, not with the Fourier identity.
   (5) Keep the fallback (design the exposure schedule) visible — it is the best contingency plan
   in the round.

### Team 06 — Frames Are Not Samples

1. **Verdict: ACCEPT.**
2. **Summary.** Observes that a captured frame is a log-mean-exp functional of the intra-exposure
   log-intensity trajectory rather than a point sample, so the point-sample form of the
   event–frame identity carries a deterministic bias equal to half the intra-exposure variance of
   log-intensity, worth 0.5–2.6 contrast thresholds — enough to collapse standard per-pixel
   contrast-threshold calibration to zero on a *perfect* sensor. It has already run the
   measurement (slope 0.955, R² 0.78, noise null R² 0.0015) before writing the document, which no
   other team did. Its sixteen-row prior-art table concedes the operator to mEDI and EVDI and
   elevates Scheerlinck et al. (ACCV 2018) — who saw the effect and dismissed it by assertion — to
   its most important citation.
3. **Strongest reason to accept.** It concedes everything a reviewer could take before the reviewer
   arrives, and what is left is a *measurement* of something the field wrote down and dropped. That
   is the correct structure for a paper whose physics is not new, and it is the only submission
   here whose headline plot exists on disk today.
4. **Strongest reason to reject.** Reviewer06's objection — that it collapses into mEDI by the
   team's own admission, since they keep mEDI's symbol `J` — is the one a hostile AC will repeat.
   The delta is "we measured what everyone drops", and that is a workshop-sized delta unless P7
   (the calibration collapse) lands.
5. **Factual errors.** **One, and it is an exclusivity claim.** "DSEC ... is **the only public
   event–frame dataset with real per-frame exposure intervals**" (§Experimental plan, Stage 1).
   Refuted at source: the AEDAT4 `Frame` type carries `timestampStartOfExposure` /
   `timestampEndOfExposure` as flatbuffer fields (`frame_base.hpp`, quoted in the collision report),
   and FE108's own dataset page instructs users to "load the aedat4 file" with dv-gui. Any DAVIS
   dataset shipped as `.aedat4` carries real per-frame exposure intervals. **Correction:** DSEC is
   the only public event–frame dataset that publishes exposure intervals as a *documented,
   directly readable text file*, which is the property the plan actually needs.
6. **Claim exceeding evidence.** "the fix is to supervise the exposure functional of a trajectory
   whose *shape* is a **threshold-invariant** normalised event profile" — reviewers 01 and 02 both
   report `c` is per-pixel, illumination-dependent and polarity-asymmetric, so the invariance is
   approximate. Say approximate.
7. **Experiment a hostile reviewer demands.** P7 on **real** DVS data, not simulation: show that a
   published per-pixel contrast-threshold calibration procedure, run on real blurred APS frames,
   returns a systematically biased `c`, and that the closed-form correction fixes it. Absence is
   **fatal** to the practical claim, which is the claim that makes this more than a re-derivation.
8. **Fixes, ranked.** (1) Delete "only" and restate as "only one shipping a documented text file".
   (2) Get P7 onto real data. (3) State the threshold-invariance as approximate with a measured
   residual. (4) Front-load the Scheerlinck quote — "we believe the difference will be
   insignificant… we do not consider this further" — because that sentence is the paper's
   justification for existing. (5) Keep the honest EVDI concession in the intro, not a footnote;
   it is the difference between ACCEPT and REJECT for me.

### Team 07 — Chronofields

1. **Verdict: REJECT** (fatal to the "first dense time field" claim; the censoring formalism could
   survive inside a different paper if its physics is repaired).
2. **Summary.** Inverts the perception map from `time → state` to `state → time`: for a queried
   state (a contrast crossing, a spatial passage, a contact), predict a distribution over *when* it
   held, with events entering the likelihood as exact observations and frames as interval-censored
   ones. Imports the survival-analysis loss family (DeepSurv/DeepHit). Derives a temporal eikonal
   `∇_u τ · v = 1`. Reports three zero-hit arXiv conjunctions and a 29-paper time-surface sweep as
   its novelty evidence.
3. **Strongest reason to accept.** It is the only team that states its stake in units an AEB
   specification is written in (ms of time-to-contact, warning lead time at fixed false-alarm
   rate), and reviewer07 is right that this matters.
4. **Strongest reason to reject.** Binary TTC (CVPR 2021) already predicts a dense per-pixel field
   of *when*, via "a series of simpler, binary classifications" — "we predict ... whether the
   observer will collide with an obstacle within a certain time" — with "arbitrarily fine
   quantization (including continuous values)". That is a dense, state-indexed, discretized
   distribution over time on the output side, five years old, in RGB. The positioning paragraph is
   false.
5. **Factual errors.** (i) "**TTC puts one time on the output side**" and the table's
   characterization of the TTC line as "one scalar per object under a looming model" — Binary TTC
   is per-pixel and dense. (ii) The 29-paper time-surface sweep's conclusion, "every one uses time
   surfaces as an INPUT representation; none regresses a timestamp map as an output", is true of
   time-surface papers and false of the adjacent lifetime line: Mueggler et al. (ICRA 2015) emits a
   per-event *duration*. The sweep was scoped to a term, not to an idea.
6. **Claim exceeding evidence.** "Verified against arXiv full text and abstracts (Sept 2026).
   Notable empty conjunctions, checked directly: `"event camera" ∧ "censored"` → **0 results**."
   The three conjunctions reproduce exactly, but the arXiv API `all:` field does **not** search
   full text; claiming "arXiv full text" is a factual misstatement of the instrument, and it is the
   instrument the novelty argument rests on.
7. **Experiment a hostile reviewer demands.** The team names it themselves: reconstruct to 1000 fps
   with Time Lens, then run a standard detector, and show the chronofield beats it. Reviewer09 and
   reviewer08 both predict a tie. Its absence is **fatal**; a tie is a rejection.
8. **Fixes, ranked.** (1) Cite Binary TTC and restate the novelty as the *censored likelihood* and
   the `∅` atom, not as "the first dense time field". (2) Answer reviewer01's physics objection —
   photoreceptor latency (C7, CVPR 2024) means events are not exact observations either — because
   the whole likelihood is built on that asymmetry. (3) Fix the headline `Δt = −8.3 ms` number,
   which reviewer02 reports is computed in a regime where the object reverses direction
   mid-exposure, outside its own derivation. (4) Cut the six-dataset plan to two. (5) Delete the
   "arXiv full text" claim.

### Team 08 — Right Place, Wrong Time

1. **Verdict: ACCEPT.** (The round's consensus is STRONG ACCEPT; I am one notch below, and the
   reason is in item 4.)
2. **Summary.** Argues every event/event–RGB benchmark scores against ground truth on a different
   clock with a different temporal support, so the dominant fast-motion error mode — right place
   along the path, wrong time — is silently booked as spatial error; proposes to decompose
   published error into pixels perpendicular to motion and milliseconds parallel to it, re-score
   ~15 released checkpoints across four datasets, and show the ranking changes. It proposes **no
   method**, which structurally defeats "you invented a metric you win on". It verified every
   checkpoint URL and tarball size by HTTP HEAD, and its first experiment (E0, label forensics) is
   a 4.7 MB label file and zero GPU. Its risk section names, in advance, the exact prior-art
   scenario that would collapse it.
3. **Strongest reason to accept.** E0 alone. "The inter-frame ground truth of the two flagship
   low-latency event benchmarks is, to within X% IoU, its own interpolation prior" is a
   benchmark-integrity result that needs no GPU, no training, no download beyond a label file, and
   cannot be taken away by a dataset going offline. I searched specifically for prior work asking
   this — `all:"ground truth" AND all:"interpolation" AND all:"event camera" AND all:"benchmark"`
   → **0** — and Ev-3DOD (C3, CVPR 2025) is the paper that ships the 100 FPS GT without ever asking.
   Nothing in my sweep touches it.
4. **Strongest reason to reject — and the adversarial finding this review was commissioned for.**
   Its central algebraic device already exists **in vision, on a detection benchmark, as an
   official challenge metric**, and Team 08 does not know it. LET-3D-AP (Waymo Open Dataset 2022
   camera-only 3D detection challenge metric): "We **decompose the localization error into a
   lateral error and a longitudinal error** ... We therefore propose **longitudinal error tolerant
   (LET) metrics that are more permissive with respect to the longitudinal localization error**",
   and its headline is a ranking flip — "**camera-based detectors can outperform popular
   LiDAR-based detectors with our new metrics past at 10% depth error tolerance**". Team 08's
   novelty statement, "(a) recognising that event–RGB benchmarks are the setting where the borrowed
   device is decisive", is exactly what LET-3D-AP already did for camera-only 3D detection.
5. **Factual errors.** (i) The along-track/cross-track row cites only air-traffic surveillance and
   trajectory prediction as the prior settings. **Correction: add LET-3D-AP / LET-3D-APL
   (arXiv 2206.07705; Waymo Open Dataset 2022 challenge metric), which is the same device in
   vision, on detection, with a ranking flip.** (ii) It cites FAOD as the closest work on naming
   the problem without stating that FAOD is an unrefereed preprint (arXiv 2412.04149v2, no
   journal_ref, no acceptance comment, verified). (iii) Ev-3DOD is correctly attributed to
   CVPR 2025 (verified in the CVF listing); Towards Streaming Perception to ECCV 2020 (verified via
   arXiv comment "ECCV 2020 (Oral)"); TIDE to ECCV 2020. Attribution hygiene is otherwise the best
   in the round.
6. **Claim exceeding evidence.** Two. (i) The thesis sentence promises "**show the ranking is not
   the ranking mAP reports**", while §Death-1 concedes the flip may not happen and provides a
   fallback. Reviewer03 flags this and is right: a thesis sentence must not promise a result the
   risk section disclaims. (ii) "We confirmed no *event-camera* streaming/latency-aware metric and
   no along-motion error decomposition used as an evaluation metric in event vision" — the first
   half reproduces (my `abs:"streaming perception" AND abs:"metric"` returned six papers, zero
   event); the second half is true only because of the words "in event vision", and the document
   does not tell the reader how much work those words are doing. After LET-3D-AP they are doing all
   of it.
7. **Experiment a hostile reviewer demands.** C1, the isotropic null (`R`, `E[cos²θ]`), on real
   data, before the leaderboard. If `R ≈ 0.5` the metric is loosened IoU and the paper is vacuous.
   Team 08 already designed it and says as much. Its absence would be **fatal**; its presence is
   the single reason I can accept a paper whose device is borrowed twice over.
8. **Fixes, ranked.** (1) **Cite LET-3D-AP in the related-work table of the first submitted
   version**, and reframe the novelty as (velocity axis, not line of sight) + (milliseconds, not
   percent of range) + (`τ_max` derived from declared supports, not swept) + (two-channel
   over-identification) + (E0). (2) **Adopt LET-3D-APL's affinity-weighted penalty form.** It is
   the published answer to the "`AP^⊥ ≥ AP` makes the comparison unfair" objection that reviewers
   03 and 08 both raise, and it comes with a reference implementation in
   `waymo-research/waymo-open-dataset`. This turns my strongest criticism into an asset. (3) Rewrite
   the thesis sentence to promise what §Death-1 will deliver. (4) Run C1 and C3 before E1.
   (5) Mark FAOD as a preprint. (6) Lower the self-scored Novelty from 7 to 5 and say why —
   pre-empting is this team's demonstrated strength and it should use it here.

### Team 09 — Change-Time

1. **Verdict: BORDERLINE.** One unfixed structural problem, and it is not prior art: the invariance
   is claimed as exact for a sensor that deletes events, and deleting events is not a monotone time
   warp.
2. **Summary.** Argues every event pipeline *partitions* the stream by wall-clock duration and that
   no partitioning rule escapes a ceiling; replaces the global timeline with a per-pixel clock
   field `τ(x,t) = C·N(x,t)` in which the event stream is a complete observation, the RGB frame's
   support becomes a measured spatially varying width `W(x)`, and the representation is exactly
   invariant to monotone reparameterizations of time. Its prior-art survey is 25 rows across two
   families and reads competitor *source code* — DAGr's `normalizer`, AEGNN's `normalize_time`,
   EFGCN's `t*_i = ⌊β·t_i/T⌋` — to show that `β` is the reciprocal of a window length.
3. **Strongest reason to accept.** The scholarship. It is the only document in the round that
   distinguishes what a competitor *claims* from what a competitor's released code *does*, it
   pre-empts SITS ("a reviewer will say 'SITS with a theorem', so we pre-empt it"), and it
   explicitly forbids itself the false claim ("**Do not claim 'reference time is arbitrary'** —
   Shiba and Hamann already say and fix that"). I verified three of its attributions at source and
   all three hold, including the SECNet "ICML 2026 Oral" claim, which is correct in the arXiv
   comment field of 2412.20803v2.
4. **Strongest reason to reject.** Four other reviewers independently report the same physics
   failure: `N` is rate-dependently under-counted by the refractory period and inflated by leak and
   shot events, so "exact, bit-for-bit invariance" holds for an ideal DVS and fails hardest in the
   fast/low-light regime the paper targets. The invariance group (monotone warps) does not contain
   event deletion. I am not the physics reviewer, but the convergence is total and I will not
   overturn it.
5. **Factual errors.** None that I found in the prior-art tables — a first for this round. One
   **presentation** error: Mueggler et al. (ICRA 2015) is buried in an eight-item catch-all row
   ("Event Lifetime; VK-SITS; ATSLTD; …"). That paper's §I contains the sentence "In a general
   configuration, however, such a time interval does not exist", which is Team 09's own thesis
   about global durations, and its `τ` is a per-pixel content-derived clock. The team's dismissal
   is *substantively correct* — Mueggler emits a duration in seconds from an estimated velocity,
   which is exactly what Team 09 argues against — but hiding the ancestor in a list reads as
   evasion. Promote it.
6. **Claim exceeding evidence.** "Verified against the June 2026 survey (arXiv:2606.23078), which
   has **no category, no method, and no open-problem entry** for reparameterization invariance or
   timeline-free representations." A survey's omission is weak evidence, and the whole novelty
   argument leans on it plus zero-hit conjunctions. See my methodological warning: these
   conjunctions all reproduce and they are nearly worthless.
7. **Experiment a hostile reviewer demands.** Measure the invariance violation on *real* DVS data
   under a controlled speed sweep — i.e. show how far from exact the "exact" invariance is when
   refractory and leak are active. Absence is **fatal**, because the claim is stated as an equality.
8. **Fixes, ranked.** (1) Restate the invariance as approximate with a measured violation, or
   restrict the claim to a stated sensor regime. (2) Promote Mueggler 2015 to its own table row and
   answer it in one sentence. (3) Replace zero-hit conjunctions with closest-work-plus-quote.
   (4) Re-found P3, which depends on ASTW's hyper-parameter table and, per reviewer04, on ASTW code
   nobody could locate. (5) Note that Spiking Patches (2510.26614) is an unrefereed preprint when
   citing it as evidence "the structure is reachable and unrecognized".

### Team 10 — Fusion Is Ill-Typed

1. **Verdict: BORDERLINE.** One unfixed structural problem: the indictment's exemplars are
   preprints and Proposition 1 is asked to carry more than it can.
2. **Summary.** Argues a frame is a positive interval-mean of irradiance and an event bin is a
   zero-mass signed boundary difference of log-irradiance, so every concatenation, gate,
   cross-attention and contrastive loss in the RGB–event literature mixes measurements of different
   *type*; supplies a legality rule for mixing, an audit (OSAM) of published architectures, and the
   falsifiable field-level prediction that existing fusion models extract *less* from events as
   scene speed rises. It names its subjects — RENet, FRN, CEUTrack, SODFormer, EFNet — and audits
   them rather than beating them.
3. **Strongest reason to accept.** `EU(s)` — "event utility inverts exactly in the regime events
   exist for" — is the most consequential checkable claim in the round for anyone choosing a
   perception stack, and the audit is inference-only on released checkpoints. Reviewer07 and
   reviewer08 independently rate it the best falsifiable field-level claim here, and my prior-art
   sweep found nothing that has asked the question.
4. **Strongest reason to reject.** Its two headline antagonists, FAOD and BRENet, are unrefereed
   preprints (verified: no journal_ref, no acceptance comment, absent from 19,210 accepted titles),
   which the document never says. An indictment of "the field" whose strongest exemplar of the
   disease has not passed review is a rebuttal liability. And Proposition 1 is, as four reviewers
   note, close to a tautology — mass 1 ≠ mass 0 — which does not by itself make a mixer illegal.
5. **Factual errors.** (i) BRENet is cited under its superseded title *Rethinking RGB-Event
   Semantic Segmentation with a Bidirectional Motion-enhanced Event Representation*; the v2 title
   is *Learning Flow-Guided Registration for RGB-Event Semantic Segmentation*, and
   `ti:"Bidirectional Motion-enhanced Event Representation"` returns 0. (ii) Neither BRENet nor
   FAOD is labelled a preprint. (iii) Missing: *Beyond Duality* (SPFD), **CVPR 2026** (verified),
   which decouples shared vs. private RGB-event features and routes static regions to RGB and
   dynamic regions to events — an accepted, empirical, coarse version of the regime-dependence
   Team 10 predicts. It should be in the table and it is a better antagonist than either preprint.
6. **Claim exceeding evidence.** "**No work we found claims** a support/type discipline for
   asynchronous perception, a support-identifiability theorem for the (frame, event-bin) pair, a
   null-space regularizer, or an audit of published RGB–event models." The type discipline and the
   audit I verified as unclaimed. But the sentence's force comes from listing four things at once,
   and SPFD is a partial counterexample to the framing that nobody has noticed the modalities are
   not interchangeable.
7. **Experiment a hostile reviewer demands.** A control separating "the model extracts less from
   events at speed" from "the model is out-of-distribution at speed". Reviewer09's objection —
   zeroing the event branch measures brittleness, not information contribution — is correct and
   decisive. Absence is **fatal** to the headline curve, which is the paper's best asset.
8. **Fixes, ranked.** (1) Build the OOD control for `EU(s)`. (2) Label FAOD and BRENet as preprints
   and re-anchor the indictment on accepted work (RENet ICRA 2023, FRN ECCV 2024, CEUTrack
   CVPR 2023, EFNet ECCV 2022 — all of which it already has). (3) Add SPFD (CVPR 2026). (4) Fix the
   BRENet title. (5) Demote Proposition 1 from load-bearing to motivating, and let the audit carry
   the paper.

---

## Ranking

By **surviving novelty** — what is left of each idea's novelty claim after my sweep, not by
overall quality. Execution risk is noted but does not drive this ordering.

| Rank | Team | Surviving novelty | What took the rest |
|---|---|---|---|
| **1** | **04** — Effective timestamp `τ̂` | **Intact.** `"effective timestamp"` → 0; no accepted paper reports what time a fused prediction refers to; `σ_τ` (within-frame dispersion) is unclaimed anywhere I looked. | Nothing. Its problems are methodological (no null for `σ_τ`), not priority. |
| **2** | **08** — Right place, wrong time | **Most of it.** The ms unit, `τ_max` from declared supports, the two-channel over-identification, C3, and all of E0 survive. | LET-3D-AP takes the decomposition, the tolerance-parameterized AP, and the ranking-flip framing. |
| **3** | **09** — Change-time | **Intact on the literature.** Five empty conjunctions reproduce; SECNet, Neural Events and ASTW attributions verified correct; nothing predicts a per-pixel clock *field* with a stated equivariance. | Mueggler 2015 is a partial ancestor it already (correctly) dismisses but hides. The physics, not the priority, is what sinks it elsewhere. |
| **4** | **06** — The exposure gap | **A measurement.** It concedes the operator to mEDI/EVDI and the observation to Scheerlinck up front, leaving "we measured what the field drops" plus P7. | Its own concessions, honestly made — plus one false exclusivity claim about DSEC. |
| **5** | **10** — Fusion is ill-typed | **The discipline.** Type rules, the audit, the null-space regularizer and change-of-support for event–RGB are all unclaimed. | SPFD (CVPR 2026) partially occupies the framing; the indictment rests on two preprints. |
| **6** | **05** — No offset fixes a width | **One measurement (OBD).** | Raskar 2006 and Yang CVPR 2024, both conceded; the theorem is the Fourier transform of a box. |
| **7** | **01** — Latent exposure support | **The TSB law and its benchmark measurement.** | EBFI-BE (CVPR 2023) holds the premise and says in its abstract that events make blind exposure well-posed. |
| **8** | **03** — Temporal support fields | **Abstention, and bi-modal comparable supports.** | Mueggler ICRA 2015 takes "predicts a temporal support measure as its output" outright. |
| **9** | **07** — Chronofields | **The censored likelihood and the `∅` atom** — resting on an asymmetry CVPR 2024 evidence contradicts. | Binary TTC (CVPR 2021) takes the dense state-indexed time field. |
| **10** | **02** — Occupancy measures as label | **Convention-marginal conformal coverage.** | TSANet Figure 1 takes the construction; Sayed & Brostow takes the premise *and* reports the forbidden move winning. |

---

## My winner and its fatal flaw

**Winner: Team 08 — *Right Place, Wrong Time*.**

I was asked to give Team 08 the most adversarial check in the round because my review is the one
that could overturn a nine-reviewer consensus. I ran it, I found the strongest thing that exists,
and it wounded the paper without killing it. I am not overturning the consensus, but I am moving
Team 08 from STRONG ACCEPT to ACCEPT, and the reason is a citation the team must add before it
writes a single line of code.

Why it still wins, on my axis rather than on execution: it is the only submission whose *primary*
deliverable is untouched by anything I found. E0 — measure how much of DSEC-Det's and
DSEC-3DOD's high-rate ground truth is recoverable from a linear interpolation of its own anchors,
then score a causal constant-velocity extrapolator with no sensor data under each benchmark's own
protocol — has no prior art anywhere in my sweep, needs a 4.7 MB label file and zero GPU, and
produces a publishable sentence whether or not the rest of the paper works. Every other team's
primary deliverable is either scooped (02, 03, 07), conceded (05, 06), contested on physics
(09, 10), or dependent on a dataset portal that other reviewers report is dead (01). Team 04 has
the cleaner novelty record and I ranked it first for that reason, but its kill shot has no null
model and three of its four named data sources are unreachable; Team 08's kill shot is a text file.

**The fatal flaw: Team 08 believes it is importing its central device from air-traffic surveillance
into vision, and it is not. The device is already an official vision benchmark metric, and it
already produced Team 08's headline result.**

LET-3D-AP and LET-3D-APL are the primary metrics of the Waymo Open Dataset 2022 3D Camera-Only
Detection Challenge. They decompose detection localization error along a privileged unit vector
into a tolerated component and a penalized component; they define a tolerance-parameterized
average precision permissive along that axis; they add an affinity term so the permissive metric
does not simply dominate the strict one; they re-score published detectors; and their headline
finding is that **the ranking changes** — camera detectors overtake LiDAR detectors past 10%
tolerance. Team 08's `AP^⊥`, `R`, `τ_max` and "the ranking is not the ranking mAP reports" are the
same four objects, with the axis swapped from line-of-sight to velocity.

This is fatal to Team 08's *novelty framing*, not to Team 08's paper, and the distinction matters:

- **If Team 08 submits as written**, a reviewer who has ever touched the Waymo devkit will write
  "this is LET-3D-AP with the velocity vector substituted for the range vector, and LET-3D-AP
  already showed the ranking flips." The paper's self-declared 7/10 novelty becomes a 3, and the
  concession paragraph about air-traffic surveillance reads as a team that surveyed an unrelated
  field carefully and its own field carelessly. That is the worst possible impression for a paper
  whose entire thesis is *"the community is not measuring what it thinks it is measuring."*
- **If Team 08 cites it in the first version**, LET-3D-AP becomes the best thing that could have
  happened to this paper. It is precedent that a major benchmark accepted an axis-tolerant AP as
  an *official* metric — which is the hardest sell in Team 08's whole argument. It supplies a
  reference implementation of the affinity-weighted penalty (LET-3D-**APL**) that answers, with
  code, the "`AP^⊥ ≥ AP` is unfair" objection that reviewers 03 and 08 both raised and that
  Team 08 currently answers only with an isotropic null. And the residual novelty — that the
  privileged axis is the *scene's* velocity rather than the *sensor's* geometry, so the tolerated
  component divides by speed and comes out in **milliseconds**, comparable against a method's own
  declared temporal support — is a clean, defensible, one-sentence delta that LET-3D-AP cannot
  claim, because a range tolerance has no clock in it.

Team 08's single greatest demonstrated strength is pre-emption: it concedes the borrowed algebra
before a reviewer can raise it, it derives `τ_max` from published specifications so it is not a
tuned parameter, and it proposes no method so it cannot be accused of inventing a metric it wins
on. It should use that strength here. The fix is one table row, one paragraph, one lowered
self-score, and one adopted penalty term. It costs a day. Not doing it costs the paper.
