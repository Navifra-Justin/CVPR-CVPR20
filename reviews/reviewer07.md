# Reviewer 07 — robotics, deployed perception, and whether any of this matters outside a plot

*Specialism: cameras on moving platforms. I care about event cameras because of latency and
dynamic range. My question for every idea is: suppose you are completely right — what changes,
and by how many centimetres or milliseconds?*

**Round summary.** Two STRONG ACCEPT (08, 06), five ACCEPT (05, 03, 10, 04, 07), two BORDERLINE
(01, 09), one REJECT (02). One cross-cutting finding that outranks any single verdict is in
§0 and affects four of the ten.

---

## 0. Finding that applies to four ideas at once — FE108/FE240hz is unobtainable

Teams **01, 02, 04 and 07** each name **FE108 / FE240hz** as the primary and in three cases the
*only* real source of ground truth above the frame rate. Team 09, in the same round, reports the
host dead. I verified it independently today rather than take either side on trust:

```
WebFetch http://fe108.dluticcd.com   ->  connect ECONNREFUSED 38.6.135.80:443
WebFetch https://zhangjiqing.com/dataset/  ->  "you must apply for access through
                                               http://fe108.dluticcd.com/"
```

The authors' own dataset page routes every request through the refused host. There is no mirror.
So the situation is not "medium-high access risk pending an application" (team 01's wording) or
"gated by an application form, apply in week 1" (team 02's wording) — the application endpoint
does not answer TCP.

Consequences, stated as a reviewer and not as a scheduling note:

- **Team 01** loses Fig 1b, which the team itself calls "the money plot," and its own self-score
  says "the dominant risk is ... access to FE240hz."
- **Team 02** loses its week-1 kill criterion, which is defined on FE108 or EVIMO2. EVIMO2 at
  200 Hz survives; the 240 Hz box GT does not.
- **Team 04** loses its "primary loop-closer" and is left with EVIMO2 at 200 Hz (5 ms sampling)
  to resolve a predicted effect of 2.5 ms. That is under-sampled by construction.
- **Team 07** loses one of its two real sub-frame GT sources.

Teams 05, 06, 08, 09 and 10 do not depend on it. That is a real ranking signal, not a technicality:
under a November 2026 deadline, an idea whose headline real-data figure requires a dataset that
cannot be downloaded is not a good bet, however good the theory is.

---

## 1. What the DSEC exposure numbers actually mean for a vehicle

The brief gives 118–14996 us and a 127x range. I recomputed the distribution from
`experiments/e00_exposure_survey/` over all 21,142 frames in the 18 sequences, because the shape
of the distribution decides several of these ideas and nobody in the ten reports it:

| statistic | value |
|---|---|
| total frames | 21,142 |
| frames at exactly 14996 us (the AE ceiling) | **6,866 = 32.5 %** |
| frames with exposure >= 5000 us | 6,866 = 32.5 % |
| frames with exposure >= 10000 us | 6,866 = 32.5 % |
| median over all frames | **1,181 us** |
| frames >= 1000 us | 63.9 % |
| frames >= 2000 us | 38.3 % |

**The distribution is bimodal with an empty gap between 5 ms and 15 ms.** Every frame above 5 ms
is a frame pinned at the ceiling. There is no continuum. Three consequences the ideas need to
absorb:

1. **In the regime where the effect is largest, the exposure is a constant.** All six pinned
   sequences sit at 14996 us for every frame, and the survey's follow-up measurement shows left
   and right windows coincide exactly there (`|w_L - w_R| = 0`, max 0). So for a third of DSEC,
   `T` is a known, published, per-sequence scalar. **Team 01's central latent is a header field
   in exactly the 32.5 % of frames where it would matter most**, and a one-line AE-ceiling
   detector recovers it. This is fatal to the *motivation* for latent-support estimation on
   automotive data, not to the mathematics.
2. **In the regime where the exposure genuinely varies frame-to-frame (interlaken_00_d, 337 ->
   4207 us, 12.5x), the absolute width is 0.34–4.2 ms.** At 50 km/h (13.9 m/s) that is
   **0.47 cm to 5.8 cm of ego translation inside one frame.** With the DSEC event camera
   (640x480, f ~ 550 px assumed from a ~60 deg HFOV), a pedestrian crossing at 1.5 m/s at 10 m
   moves **0.10 px** during the median 1.18 ms exposure. There is no measurable phenomenon in
   daytime DSEC. Teams 05 and 10 both flagged this in advance and were right to.
3. **Team 10's Panel C has a confound its authors have not noticed.** Panel C proposes
   correlating per-frame error with `T * |v|` across DSEC. But `T` is essentially constant
   *within* a sequence and switches between two clusters *across* sequences, so a cross-sequence
   correlation with `T` is a correlation with illumination, sensor gain, night-vs-day scene
   content and pedestrian density. The only valid version of Panel C is within-sequence, on
   interlaken_00_d / zurich_city_05_a, where the lever arm is 3.9 ms and 3.3 ms respectively,
   not 14.9 ms. This must be fixed or the panel is uninterpretable.

### The number the round needs: what 25 ms costs

The brief's verified reference point is that a `dt=50 ms` RVT representation attached to a label
at `t` has a uniform-weight centroid at `t-25 ms`. Here is that in units a vehicle uses.

| platform | speed | 15 ms (AE ceiling) | 25 ms (RVT centroid) | 50 ms (DSEC frame period) |
|---|---|---|---|---|
| warehouse forklift | 1.5 m/s | 2.3 cm | **3.8 cm** | 7.5 cm |
| urban car | 13.9 m/s (50 km/h) | 20.8 cm | **34.7 cm** | 69.5 cm |
| highway car | 27.8 m/s (100 km/h) | 41.7 cm | **69.5 cm** | 1.39 m |
| autobahn | 36.1 m/s (130 km/h) | 54.2 cm | **90.3 cm** | 1.81 m |
| obstacle-avoiding quadrotor (CoRL'24 setting) | 5 m/s | 7.5 cm | **12.5 cm** | 25 cm |
| racing quadrotor | 20 m/s | 30 cm | **50 cm** | 1.0 m |

And in image space, at f ~ 550 px on the DSEC event camera, for a car crossing at 8.3 m/s at 15 m
(box ~165 px wide) and a cyclist at 6 m/s at 5 m (box ~66 px wide):

| offset | crossing car @15 m (box ~165 px) | IoU | cyclist @5 m (box ~66 px) | IoU |
|---|---|---|---|---|
| 1.18 ms (median exposure) | 0.36 px | 1.00 | 0.78 px | 0.98 |
| 14.996 ms (AE ceiling) | 4.6 px | 0.95 | 9.9 px | 0.74 |
| 25 ms (RVT centroid) | 7.6 px | 0.91 | 16.5 px | **0.60** |

*(IoU for equal boxes translated by `s` along width `w` is `(w-s)/(w+s)`; `f ~ 550 px` assumed
for the DSEC event camera from a ~60 deg HFOV over 640 px — stated so a reader can redo it with
the true intrinsics.)*

**The decisive comparison.** 25 ms is *half of the 50 ms sampling interval the same system has
already accepted by choosing a 20 Hz camera*. A pipeline that tolerates 69.5 cm of aliasing at
100 km/h between consecutive frames cannot honestly call 34.7 cm of representational centroid
offset a crisis. Worse for the ambitious framings here: the offset is a **bias**, not jitter, and
a bias with a known sign is the single easiest error a downstream estimator removes — a constant-
velocity Kalman step cancels it *exactly*, for free, **provided somebody declares the timestamp**.
That is not a research problem. It is a reporting problem. Which is why the idea that wins this
round is the one that says exactly that (team 08) and not the nine that build machinery.

Where 25 ms is genuinely decisive: the quadrotor. 12.5 cm at 5 m/s is 0.64 airframe lengths for
a 19.5 cm tip-to-tip quadrotor (Bauersfeld's spec, below), and the flow-feedback control loops
in the deployed literature run at 500 Hz–1 kHz, i.e. 12–25 control periods per 25 ms. **But the
deployed drone systems that achieve those rates use no RGB frame at all.** The regime where
temporal support is decisive is the regime from which the frame has already been deleted. Every
team in this round should read that sentence before writing an introduction.

---

## Comparison set

Verified accepted, event vision on a real robotic or automotive system, 2024–2026. Acceptance was
confirmed for every entry this session (PDF header, PMLR proceedings page, arXiv acceptance
comment, publisher metadata, or the authors' publication list). Numbers are read out of the paper
body except where I say otherwise; entry 1 is the one exception and it is flagged in place.

1. **Low-latency automotive vision with event cameras** — Daniel Gehrig & Davide Scaramuzza,
   **Nature 629, 1034-1040 (30 May 2024)**, doi:10.1038/s41586-024-07409-w. Bibliographic record
   confirmed against the CrossRef API; DSEC-Det and DAGr code at `uzh-rpg/dagr`.
   *Measured practical benefit:* a 20 Hz RGB camera paired with an event camera reaches the
   detection latency of a **5,000 Hz** camera while consuming the bandwidth of a **45 Hz** camera.
   **Sourcing caveat, stated because it matters:** the full text sits behind Nature's auth
   redirect and I could not open it through five independent routes (nature.com HTML and PDF, the
   UZH ZORA mirror, the ETH Research Collection, and the RPG docs path). These three figures are
   therefore quoted from the authors' own project-page summary, not read out of the paper body,
   and anyone citing them in the submission must open the PDF first. The venue, volume, pages and
   date above are publisher metadata and are solid.
   The benefit is stated in **bandwidth and latency**, not in temporal-support correctness, and
   the frame is retained as a low-rate anchor.
2. **Low-Latency Event-Based Velocimetry for Quadrotor Control in a Narrow Pipe** — Bauersfeld &
   Scaramuzza, **IEEE T-RO**, 2026 (PDF header: "accepted for publication in the IEEE Transactions
   on Robotics (T-RO), 2026").
   *Measured:* first closed-loop quadrotor control from real-time flow-field measurement;
   **sub-millisecond processing latency**; smoke-velocimetry mean error **0.35 m/s** vs offline
   PIVLab; flow estimator at **500 Hz** on a workstation and **~1 kHz** on Jetson Thor
   (measured runtimes: Raspberry Pi 4B 3.22 ms, Jetson Orin NX 1.29 ms, Jetson Thor 0.61 ms,
   i9-12900K 0.17 ms); monocular event motion capture at **273 us** latency with millimetre
   accuracy; closed-loop result **29 % reduction in hovering position deviation and 71 %
   reduction in overshoot during lateral moves**, in a 380 mm pipe where the prior art showed
   tracking errors up to 6 cm. **No RGB frame anywhere in the loop.**
3. **Monocular Event-Based Vision for Obstacle Avoidance with a Quadrotor** — Bhattacharya,
   Cannici, Rao, Tao, Kumar, Matni, Scaramuzza, **CoRL** 2024 (PMLR v270, pp. 4826–4843).
   *Measured:* first static-obstacle avoidance on a quadrotor from a **monocular event camera
   only**. The load-bearing finding for this round: **1 m/s flight is more collision-prone than
   5 m/s**, because faster motion yields better event-based depth. Speed is the *enabling*
   variable, not the failure variable. Any idea in this round that treats fast motion purely as a
   degradation axis is arguing against a measured robotic result.
4. **Deep Visual Odometry with Events and Frames (RAMP-VO)** — Pellerito, Cannici, Gehrig,
   Belhadj, Dubois-Matra, Casasco, Scaramuzza, **IROS** 2024.
   *Measured:* **8x faster inference** and **33 % more accurate** predictions than prior
   event+frame solutions; **58.8 %** improvement over previous image- and event-based methods and
   **30.6 %** on existing benchmarks; targeted at planetary-landing / GPS-denied navigation.
   This is the strongest *deployed* event+frame fusion result in the window, and note what it
   optimises: inference latency and trajectory error, not temporal alignment.
5. **Ev-3DOD: Pushing the Temporal Boundaries of 3D Object Detection with Event Cameras** — Cho,
   Kang, Kim, Yoon, **CVPR** 2025 (Highlight; arXiv 2502.19630 comment confirms acceptance).
   *Measured:* first event-based 3D detection for driving; DSEC-3DOD with **100 FPS** 3D box GT;
   detection during the LiDAR blind time. Team 08 correctly identifies the number that matters
   here: conventional detectors drop **53.61 -> 33.32 mAP** (VoxelNeXt) and **53.29 -> 33.27**
   (LoGoNet) when scored online against the 100 FPS GT — a ~20 mAP gap that is purely timing and
   currently has no name and no unit.
6. **Event-Based De-Snowing for Autonomous Driving** — Muglikar, Messikommer, Cannici,
   Scaramuzza, **IEEE T-RO**, 2026.
   *Measured:* **+3 dB PSNR** over SOTA de-snowing for image reconstruction on real driving data.
   The practical benefit is dynamic range and occlusion rejection in adverse weather — again, not
   temporal support.
7. **Event-Aided Sharp Radiance Field Reconstruction for Fast-Flying Drones** — Zou, Cannici,
   Scaramuzza, **IEEE T-RO**, 2026.
   *Measured:* **>50 % performance gain on real-world data** over SOTA, for scene reconstruction
   from a fast-moving drone where frames are motion-blurred. This is the closest deployed
   analogue to the intra-exposure story these ten ideas are chasing, and it treats blur as a
   *reconstruction* nuisance, not as a label-convention problem.

*(Additionally located but not counted, because acceptance is not yet confirmable: Messikommer et
al., "Approximate Imitation Learning for Event-based Quadrotor Flight", arXiv 2026, reporting
**28x training speed-up** and cluttered flight **up to 9.8 m/s**.)*

**What the comparison set establishes, and it is uncomfortable for this whole round.** Across
seven accepted deployed results, the measured practical benefit of an event camera is one of:
bandwidth (Nature'24), latency in the *control loop* (T-RO'26 velocimetry, 273 us / 0.61 ms),
dynamic range and weather (T-RO'26 de-snowing), or blur-free geometry (T-RO'26 radiance fields,
CoRL'24 depth). **Not one of them reports a benefit that came from getting the temporal support
of a frame right.** Two of them — the two with hard closed-loop numbers — do not use a frame at
all. The honest position for this round is therefore: the temporal-support problem is a
*benchmark-integrity* problem and an *evaluation-protocol* problem, and the ideas that own it as
such (08, 06, 05) are on firmer ground than the ideas that promise downstream task gains (01, 02,
07, 09).

---

## Per-idea verdicts

| # | Title (short) | Verdict | One-sentence reason |
|---|---|---|---|
| 08 | Right Place, Wrong Time — support error as the unmeasured half of benchmarks | **STRONG ACCEPT** | The only idea whose output changes a deployed system this week (declare `tau_hat`, shift by `-25 ms`, let the tracker cancel it), it trains nothing, and every checkpoint and byte-size is verified. |
| 06 | The exposure gap `J = 1/2 Var_W(L)` and profile/amplitude identification | **STRONG ACCEPT** | Its headline number is already measured rather than predicted (slope 0.955, R2 0.779, noise null 0.0015), and its practical payoff — contrast-threshold calibration collapsing from 0.200 to -0.004 with blur — is a defect in every DVS deployment pipeline. |
| 05 | No offset can fix a width — temporal support calibration | **ACCEPT** | The impossibility bound is a consequence of the Fourier transform of a box, so it cannot fail; it delivers a usable artifact (a per-pixel blind-band mask); and it pre-identified the exact real-data risk that my DSEC recomputation confirms. |
| 03 | Temporal support fields; fusion as support overlap; abstention | **ACCEPT** | Abstention — "I hold no observation of this pixel at the requested instant" — is the single most valuable output in the ten for a real vehicle, and half the supervision (the event branch) is free and real. |
| 10 | Fusion is ill-typed; event utility inverts with speed | **ACCEPT** | "Fusion models extract less from events as speed rises" is the most consequential checkable claim in the round for anyone choosing a perception stack, and it is inference-only on released checkpoints — but Panel C has a sequence-level confound (see §1.3). |
| 04 | Effective timestamp `tau_hat`, within-frame dispersion `sigma_tau` | **ACCEPT** | Best-engineered pilot in the set (3 days, 3 GPU-h, zero downloads) and honest pre-registered nulls; the predicted 2.5 ms bias is 3.5 cm at 50 km/h, so it is a good paper about a small number. |
| 07 | Chronofields — predict *when*, with censored likelihoods | **ACCEPT** | The only team that states its stake in the units an AEB specification is written in (ms of TTC, warning lead-time at fixed false-alarm rate), but its two real sub-frame GT sources are FE108 (dead) and 200 Hz EVIMO2 (5 ms, too coarse). |
| 01 | Latent exposure support as a first-class variable; the TSB law | **BORDERLINE** | The non-identifiability proposition is correct and its consequence is void: in the 32.5 % of DSEC frames where the window is 15 ms wide the exposure is a pinned constant published in a text file, and the FE240hz plot the paper is built on cannot be downloaded. |
| 09 | Change-time — per-pixel clocks, reparameterization invariance | **BORDERLINE** | Best scholarship in the round and the weakest operational stake: its own make-or-break prediction (P3) says the competitor ASTW survives to a 25:1 speed ratio, and a car-plus-pedestrian scene is 20:1, so ASTW is predicted *not to break* anywhere real. |
| 02 | Exposure-occupancy measures as the prediction target | **REJECT** | Its load-bearing prediction ("at nu=0, beta=3, D<0.05") is contradicted by arithmetic on its own convention table, and the controlled variable `nu` requires an intra-exposure velocity change that no vehicle, drone or manipulator produces. |

---

## Detailed review

Rubric items 1–8 per idea. Deepest on 08, 06, 05 and on the REJECT.

### Team 08 — Right Place, Wrong Time — **STRONG ACCEPT**

1. **Verdict.** STRONG ACCEPT.
2. **Summary proving I read it.** The paper does not train anything: it dumps predictions from
   fifteen released checkpoints, projects each box-centre error onto the GT track tangent, divides
   the along-track component by ground-truth image speed, and reports the quotient in
   milliseconds. It then pre-registers `tau_hat in [-35, -10] ms` for RVT from RVT's *own* config
   (`stacked_histogram_dt=50_nbins=10`, window ending at the label) before measuring it, ties the
   relaxation budget `tau_max = (w_G + w_P)/2` to the benchmark's and the method's published
   specifications so it is not a tunable knob, and uses an isotropic free-direction relaxation
   `AP^iso` as the null. E0 — the cheapest experiment in the round, a 4.7 MB label file and no
   GPU — asks whether the inter-frame ground truth of DSEC-Det and DSEC-3DOD carries information
   beyond the linear interpolation that produced it.
3. **Strongest reason to accept.** It is the only idea in the ten that produces an artifact a
   deployment engineer uses on Monday. If `tau_hat(RVT) = -25 ms` and is predictable from the
   declared window, then anyone running RVT on a vehicle should stamp its output at `t - 25 ms`
   and let the existing EKF cancel 34.7 cm of lag at 50 km/h at zero cost. Nobody does this today
   because nobody has ever published the number. That is a real, cheap, immediately actionable
   change, and it is the *correct* answer to the seed observation — the fix for a known constant
   bias is to declare it, not to build a trajectory head.
4. **Strongest reason to reject.** P6 (the ranking flip) may not land, and the team knows it. If
   every method on a dataset uses the same 50 ms window, they share `tau_hat` and the correction
   is order-preserving. The paper then degrades to "here is a number for every published method,"
   which is a benchmark note. Mitigated, but only partly, by E0 running independently first.
5. **Factual errors.** None found that survive checking. The RVT claim (`preprocess_dataset.py`
   counting backwards from label timestamps) matches the brief's independent verification. The
   Ev-3DOD 53.61 -> 33.32 / 53.29 -> 33.27 figures are consistent with the CVPR 2025 paper as I
   verified its acceptance and framing. The 1 Mpx label-provenance quote (GoPro Hero6 at 60 fps +
   homography) is accurate to Perot et al., NeurIPS 2020.
6. **Overclaim.** "for a uniform event rate the information centroid of the input is `t - 25 ms`.
   That is a *prediction*, not a hypothesis" — no. It is a hypothesis about the *network*, and
   the brief says so explicitly: "Whether the trained network weights the ten bins uniformly is
   unmeasured, so 25 ms is a reference point, not a prediction of network behaviour." The paper
   must not write "prediction" where it means "uniform-weight reference." Also P3's threshold
   (`R >= 0.75`) is asserted without derivation; state it as a pre-registered bet, which is what
   it is.
7. **Experiment a hostile reviewer demands.** "Your `tau_hat` is the dataset's annotation offset,
   not the model's." The team's own C3 (predict `tau_hat` from each method's declared window
   *before* measuring, then compare across methods with different windows) is exactly the right
   answer, and the E-RAFT MVSEC 20 Hz vs 45 Hz pair is the cleanest instrument in the round for
   it. Its absence would be fatal; its presence is why I am voting STRONG ACCEPT. What I would
   add: **run it on a sequence where ego-speed is logged.** DSEC ships `lidar_imu.zip`; regressing
   `tau_hat` against measured ego-speed rather than image speed would let the paper report the
   result in centimetres, which is the unit the robotics half of the audience reads.
8. **Ranked fixes.** (i) Run E0 first and publish it standalone-capable. (ii) Report `tau_hat`
   in both ms and cm using DSEC IMU speed. (iii) Replace "prediction" with "uniform-weight
   reference" for the 25 ms figure. (iv) Add the deployment recommendation explicitly — a
   one-sentence reporting contract, "declare `(c_P, w_P)`" — since that is the paper's real
   product. (v) Drop the ambition of a flip on Gen1 and target BFlow `E` vs `E+I`, the only pair
   where the mechanism is single-variable.

### Team 06 — The exposure gap — **STRONG ACCEPT**

1. **Verdict.** STRONG ACCEPT.
2. **Summary proving I read it.** The paper refuses the easy overclaim: it explicitly states that
   EDI/mEDI already carry the exposure functional and that "every method assumes (E2)" would be
   false, then narrows to the true and sufficient claim — the term is never expanded, named,
   bounded or measured, and it is silently dropped whenever the identity is anchored on two
   *captured* frames. It gives the closed form `J = 1/2 Var_W(L) + O(k3)`, verifies it to four
   significant figures across three decades of blur, and then produces the number that matters:
   run the standard contrast-threshold calibration recipe (Wang et al., ACRA 2019, Eq. 6) on a
   *physically perfect* sensor and `c_hat` falls from 0.189 at 1 px of blur to **-0.004 at 32 px**
   — a sign flip — while the support-aligned estimator stays within 5 % at every blur level.
3. **Strongest reason to accept.** It is the only idea in the round whose headline is *already
   measured* rather than predicted, with the noise null run (R2 = 0.0015 against 0.779) and the
   robustness check across three scene models and three seeds. And its practical consequence is
   the one thing in this entire round that touches every robotics group that owns a DVS: **your
   contrast threshold is miscalibrated as a function of how fast you moved the calibration
   target, by up to 100 %, with no sensor non-ideality present.** That is a deployment defect,
   it is closed-form removable, and it is verifiable in an afternoon.
4. **Strongest reason to reject.** "Networks absorb it; your PSNR gain is 0.1 dB." The team names
   this as Death 2 and answers with P6 — a learned constant removes 0.0 % of the fast-motion
   residual, a learned linear model in generic event features removes 51 % and degrades 0.059 ->
   0.105 across the support shift, the parameter-free LME correction removes 91.2 % and degrades
   0.044 -> 0.055. That answer is measured at toy scale and must be reproduced at network scale;
   if it returns a null, the paper shrinks to a measurement.
5. **Factual errors.** None found. The BS-ERGB death is independently confirmed by team 09 and by
   my own check pattern (form-gated, links removed). The claim that ESIM models only a Gaussian
   contrast threshold and that DVS-Voltmeter has no refractory period is correct and is stated
   *against* the paper's own interest, which is the mark of a document I can trust.
6. **Overclaim.** "on textured content ... the residual is 2.6 contrast thresholds and 99 % of it
   is the exposure operator." True in the Monte-Carlo, but "which is what natural video is" is
   doing unearned work: DSEC daytime driving at a median 1.18 ms exposure has almost no
   intra-exposure variance at all (see §1). The sentence must be scoped to the blur regime that
   the sequence actually occupies, or a reviewer with a DSEC checkout will kill it in one plot.
   Second: "the harder the motion, the better the threshold is determined" is stated as
   counterintuitive fact from `dG/da = 0.86-0.91`; it is a conditioning statement in the
   log-linearised model and must be labelled as such.
7. **Experiment a hostile reviewer demands.** Run the `R ~ P` regression on **real DSEC**, using
   the published exposure windows and no ground truth at all — which the team already plans as
   Stage 1. Its absence would be fatal, because the entire diagnosis is otherwise a simulator
   result. I would additionally demand it be run **separately on the pinned-15 ms sequences and
   the sub-2 ms sequences**, since §1 shows those are two different physical regimes and a
   pooled regression would mix them.
8. **Ranked fixes.** (i) Split every real-data regression by exposure regime (>= 14996 us vs
   < 5000 us) — pooling is not defensible given the bimodality. (ii) Close the two open
   verification gates (Brandli ISCAS 2014; Electronics 15(7):1420) before writing an
   introduction; the team already says so. (iii) Lead with P7, the calibration collapse, not with
   the LME identity — P7 is the sentence a robotics reader remembers. (iv) Scope the "natural
   video" claim to measured blur regimes.

### Team 05 — No offset can fix a width — **ACCEPT**

1. **Verdict.** ACCEPT.
2. **Summary proving I read it.** The argument is Fourier and it cannot fail: a shift is a
   unit-modulus linear-phase multiplier, support mismatch is a modulus mismatch with exact zeros
   and pi phase jumps, so the shift group cannot contain the operator relating the two channels.
   T1 gives the impossibility floor SMF, T2 says the best-fit offset is a spectrum-weighted group
   delay and therefore depends on the *scene*, and T3 gives multichannel-blind-deconvolution-style
   identifiability from `J >= 2` speeds. The failure experiment is run with an *oracle* offset
   search on data where the shift model is exact and the true offset is zero — there is no
   estimator, no noise and no hardware to blame.
3. **Strongest reason to accept.** The deliverable is an artifact I would ship: a per-pixel
   blind-band mask that tells a fusion stack which spatial frequencies of the frame carry zero
   information at the current local speed, plus a contrast-sign-inversion flag. That is directly
   consumable by a downstream weighting scheme, and it is the only output in the round besides
   team 03's abstention mass that a systems engineer can act on without retraining anything.
   Compute profile is also the best in the set: ~96 GPU-h, <8 GB, theory tier runs on CPU.
4. **Strongest reason to reject.** "This is deblurring with new vocabulary; the sinc null is
   Raskar 2006." The answer takes a paragraph rather than a sentence, and a reviewer who reads
   only the figures sees blur curves. The team says this itself.
5. **Factual errors.** One correction. Death 2 says "DSEC daytime driving may run exposures of
   0.1-1 ms, giving b < 1 px." My recomputation makes this sharper and slightly worse for the
   paper: the **median over all 21,142 train frames is 1.18 ms**, and 63.9 % exceed 1 ms — but
   38.3 % exceed 2 ms and *all* of those above 5 ms are the pinned-15 ms night frames. So the
   real-data story is: daytime is entirely below onset (b ~ 0.1–1.3 px for realistic crossing
   speeds), and the effect lives exclusively in the six night sequences, where b ~ 4.6–9.9 px for
   the cases I tabulated in §1 — comfortably above the b >= 2 px onset. The paper's plan should
   say this, not hedge it.
6. **Overclaim.** "at T=10 ms that is >= 3 ms of drift on a rig whose true offset is exactly 0 —
   an order of magnitude above the sub-ms precision EF-Calib/eKalibr-class methods report."
   `|d delta_hat / db| >~ 0.05 T` per pixel over `b in [1,8]` is an assumption, not a result,
   until Panel A is run; it is currently presented in the same register as T1, which *is* a
   theorem. Separate them typographically.
7. **Experiment a hostile reviewer demands.** Measure the joint `(T, v)` distribution on DSEC
   *first*, before committing, which the team already schedules as step (ii) of Death 2. Its
   absence would be fatal, because without it the paper cannot say whether it is describing
   reality or a corner. I would demand one addition: since the effect is confined to night
   sequences, report the fraction of DSEC *frames* — not sequences — above onset. From my
   numbers that is at most 32.5 %, and probably less once local speed is folded in. A paper that
   says "the effect is present in a third of a public benchmark's frames" is strong; a paper that
   implies it is everywhere is refutable.
8. **Ranked fixes.** (i) Run the `(T, v)` measurement in week one and report the above-onset
   frame fraction as a headline statistic. (ii) Separate theorem from conjecture in the
   presentation of T1 vs prediction 4. (iii) Pivot the headline downstream task to event-RGB
   correspondence/flow as the team's own fallback suggests — no deblurring baseline exists there,
   so the "isn't this deblurring" attack has no purchase. (iv) Keep Ablation 1 first, as planned.

### Team 03 — Temporal support fields — **ACCEPT**

1. ACCEPT.
2. **Summary.** Predicts, per pixel and per branch, a **sub-probability** measure on the time
   axis — mass separate from shape, so "there is no valid observation here" is representable —
   and replaces similarity fusion with a support-overlap gate `log <s_F, s_E>` added to the
   attention logit. The event-branch support is read for free from the raw stream (inter-event
   intervals), the frame-branch support is self-supervised via an EDI rendering loss with no
   labels, and the go/no-go phenomenon plot costs ~18 GPU-h.
3. **Strongest reason to accept.** The abstention output. A perception module that can say
   *"I hold no measurement of this region at the requested instant"* is a safety primitive, not a
   metric. It maps directly onto an operational-design-domain monitor on a vehicle and onto a
   collision-check gate on a drone, and no existing event-RGB model can emit it. Everything else
   in this round outputs a better number; this outputs a refusal, and refusals are what keep
   robots from driving into things they cannot see.
4. **Strongest reason to reject.** "This is uncertainty estimation with extra steps." The
   scalar-reliability ablation (viii) is the right answer and it must be in the main paper. The
   deeper worry is that the frame-branch support is supervised only in simulation, so the
   headline is a simulator claim with a real-data fallback.
5. **Factual errors.** None material. One scoping error: prediction 1 (>= 3.5 dB PSNR drop between
   high and low overlap terciles) is stated for EFNet/CMTA/REFID/Time Lens++ on data the team
   generates; it cannot be asserted for real DSEC, where §1 shows daytime overlap barely varies.
6. **Overclaim.** "supports vary smoothly on an object" is a regulariser justified by assertion,
   and it is exactly wrong at a motion boundary or an occlusion edge — which is where abstention
   matters most. Either mask it at boundaries (as done for `L_eik` in team 07) or drop it.
7. **Experiment a hostile reviewer demands.** Ablation (vi): a model trained with **zero
   simulator labels**, real self-supervision only, recovering most of the gain. Its absence is
   fatal, because otherwise the invented ground truth is the whole paper.
8. **Fixes.** (i) (vi) and (viii) into the main paper. (ii) Report the abstention result as a
   risk-coverage curve against a real downstream consumer, not as an AUC. (iii) Drop the
   dwell-then-dash matched pair from the headline and demote it to the mechanism section — it is
   a constructed stimulus and a reviewer will say so. (iv) Cut the dataset list from eight to
   three.

### Team 10 — Fusion is ill-typed — **ACCEPT**

1. ACCEPT.
2. **Summary.** Proposition 1 is two lines: the frame's temporal measure has mass 1 and lives in
   the linear domain, the event bin's has mass 0 and lives in the log domain, the two sets are
   disjoint, so no shift, scale or warp maps one to the other — registration is orthogonal to the
   defect. The diagnostic is Panel A: event utility `EU = metric(M(F,E)) - metric(M(F,0))`
   measured by modality dropout on released checkpoints and plotted against intra-exposure
   displacement `s = |v| T`, predicted to **peak and then fall**. Panel B instruments every mixing
   site with Jacobian influence, so gates and AdaIN are auditable, not just attention.
3. **Strongest reason to accept.** If `EU(s)` inverts across four published architectures, that is
   the most consequential sentence anyone in this round could write for a systems audience:
   *event-RGB fusion stops using the event branch precisely in the regime the event branch was
   bought for.* It is inference-only, it costs an afternoon per model, and it would change
   procurement decisions. The fine-tuning control (metric improves 2–4 points, OSAM falls < 0.08,
   EU does not recover) is the right way to show the defect is formulational rather than a
   weights problem.
4. **Strongest reason to reject.** It is a claim about other people's models, and if `EU(s)`
   merely flattens rather than inverting, the paper becomes a formalism paper with a synthetic
   witness. The team says this.
5. **Factual errors — one that must be fixed.** Panel C as specified is confounded. It proposes
   correlating per-frame error with `T |v|` across DSEC "even after controlling for `|v|` alone."
   Per §1, `T` is constant within a sequence and switches between two clusters across sequences,
   so cross-sequence variation in `T` is variation in *illumination and scene*. The valid design
   is within-sequence, on interlaken_00_d (337 -> 4207 us) or zurich_city_05_a (658 -> 3988 us),
   with a lever arm of 3.9 ms and 3.3 ms — not the 14.9 ms the "118 to 14996 us" framing implies.
   As written, `rho > 0.5` would be trivially achievable and meaningless.
6. **Overclaim.** "`OSAM(s) ~ 1 - r/(r+s)`, from 0.12 +- 0.03 at s=0.5 px to 0.83 +- 0.05 at
   s=12 px" — error bars on an unrun experiment. Delete the +- or label it a target.
7. **Experiment a hostile reviewer demands.** The support-blind pair (time-reversal) evaluation on
   released checkpoints. The team is right that it cannot fail: it is a construction plus a
   theorem. Keep it as the insurance policy it is.
8. **Fixes.** (i) Rewrite Panel C as within-sequence. (ii) Present the Jacobian-influence OSAM as
   the primary definition from the first mention, since two of the four target models have no
   softmax. (iii) Cut the operator to 1.5 pages as planned and never show a leaderboard.
   (iv) Report `s` in centimetres of scene motion as well as pixels — the audience that cares
   about this result reads metres.

### Team 04 — Effective timestamp and within-frame dispersion — **ACCEPT**

1. ACCEPT.
2. **Summary.** Introduces one primitive — `tau_hat = argmin_t d(y_hat, y*(t))`, the time at which
   the prediction *would have been right* — and two statistics: bias `b` and, the kill shot,
   within-frame dispersion `sigma_tau`. If `sigma_tau > 0`, no scalar clock correction exists
   because different regions of one output tensor live at different times. The pilot is 3 days, 3
   GPU-hours, zero external downloads, rendering natively at 10 kHz to remove the v2e/SuperSloMo
   dependency, and the null result is written out in advance (Fig 1 vertices at 0, no collapse,
   `sigma_tau ~ 0` ⇒ "this is calibration, we pivot").
3. **Strongest reason to accept.** The frame-only / event-only / fused control (8.3.5a) is the
   single most important control in the round and the team names it as such: if `sigma_tau` is as
   large for a frame-only model, the fusion framing is wrong and they will say so. That is how a
   diagnosis paper should be built.
4. **Strongest reason to reject.** The predicted magnitudes are small: `b >= 2.5 ms`,
   `sigma_tau >= 1.5 ms` at `T_exp = 10 ms`. At 50 km/h that is 3.5 cm and 2.1 cm of ego motion,
   against a brake actuator that needs hundreds of milliseconds to build pressure. A hostile
   reviewer will not dispute the measurement; they will ask why it matters, and the paper's
   current answer ("time-to-collision or closed-loop reaching") is a fallback in the risk section
   rather than an experiment.
5. **Factual errors.** The FE240hz risk is rated "medium — author-hosted; Baidu-only mirrors would
   hurt." It is not medium; it is realised (§0). Also, `T_exp = 10 ms` as the default operating
   point is not a DSEC value — DSEC has essentially no mass between 5 and 15 ms. Pick 1.2 ms
   (daytime median) and 15 ms (AE ceiling) as the two real settings and say why.
6. **Overclaim.** "the field's 'fast motion is hard' curves are a speed-scaled projection of a
   single latent timing variable" (C1). That is the thesis, asserted in the failure-phenomenon
   section as though established. Mark it as the hypothesis Figure 2 tests.
7. **Experiment a hostile reviewer demands.** The strongest possible calibration baseline, run by
   the authors: best global `delta` per dataset, then per-speed-bucket, and report the residual
   `sigma_tau` that survives. The team schedules exactly this and pre-commits to downgrading to a
   workshop note if a lookup table removes >= 80 %. That is the right posture and it is why this
   is an ACCEPT despite the small effect.
8. **Fixes.** (i) Replace FE240hz with BS-ERGB/HS-ERGB or EVIMO2 in the plan and re-cost.
   (ii) Move the closed-loop consequence (Death 3 fallback ii) into the main experimental plan —
   it is the only thing that answers "so what." (iii) Use DSEC's real bimodal exposure settings.
   (iv) Report `b` and `sigma_tau` in cm at a stated platform speed alongside ms.

### Team 07 — Chronofields — **ACCEPT**

1. ACCEPT.
2. **Summary.** Inverts the map: instead of `time -> state`, predict `state -> distribution over
   time`, with an explicit `null` atom for "never within the window." Events enter as
   *uncensored* observations of a crossing time, frames as *interval-censored* ones — a frame
   says the transition happened somewhere inside the exposure and refuses to say when — and
   non-crossings as right-censored. The dwell-time change of variables turns the EDI integral
   into a constraint on `d tau / d L`, and the temporal eikonal `grad_u tau . v = 1` falls out
   because the spatial gradient of a crossing-time field is the slowness field.
3. **Strongest reason to accept.** It is the only team that states its stake in units an AEB
   specification uses: **time-to-collision error in milliseconds, and warning lead-time achieved
   at a fixed false-alarm rate.** That is not an invented metric; that is how the function is
   certified. And the C1 anchor — predict the next contrast crossing, supervise with held-out
   *real* events at microsecond precision, no simulator, no annotator — is the cleanest
   zero-annotation real-data experiment proposed anywhere in this round.
4. **Strongest reason to reject.** Reconstruct-to-1000-fps then detect. The team pre-registers the
   falsification criterion (within 15 % P95 CTE at equal compute ⇒ the accuracy claim is dead),
   which is admirable, but a live risk is still a live risk.
5. **Factual errors.** The `Delta t ~ a T^2 / (24 v_bar)` example — `T=20 ms, a=-2 px/ms^2,
   v_bar=4 px/ms` giving 8.3 ms — has no counterpart in DSEC: no DSEC frame has a 20 ms exposure
   (max is 14996 us), and an image acceleration of 2 px/ms^2 = 2,000,000 px/s^2 is not a vehicle.
   Rework the example on the 15 ms AE-ceiling regime with an attainable acceleration, or concede
   it is a manipulation/sports number.
6. **Overclaim.** "FAOD's headline — 80x frequency mismatch, only 3 mAP drop — is not evidence
   that alignment works; it is evidence that mAP cannot see time." The rhetorical inversion is
   good but the paper states it three times in three sections. Once, with the null-space
   proposition attached, is enough; repeated, it reads as a slogan.
7. **Experiment a hostile reviewer demands.** Time Lens -> RVT head-to-head at matched *and*
   unmatched compute, reported either way. Its absence is fatal.
8. **Fixes.** (i) Replace FE108-dependent plans (§0). (ii) Run C1 and the head-to-head before
   writing. (iii) Cut the six-dataset plan to two, as the team's own self-score demands.
   (iv) Re-derive the `Delta t` worked example at a physically attainable acceleration.

### Team 01 — Latent exposure support — **BORDERLINE**

1. **Verdict.** BORDERLINE. The single unfixed structural problem: **the paper's central latent
   is a published constant in the only DSEC regime where its effect is measurable, and its
   headline real-data figure depends on a dataset that cannot be downloaded.**
2. **Summary.** The `u = (tau - t0)/T` substitution removes `(t0, T)` from the blur integral
   exactly, so a blurred frame determines the path and dwell density and *nothing* about the
   absolute window or even the direction of traversal. From this the paper derives the TSB law
   `E[e_par | d] = (alpha_model - alpha_label) d`, predicts that a documented cross-dataset
   "domain gap" is a clock-convention gap removable by one scalar per dataset, and replaces the
   point state with a Bezier trajectory on the normalised support where `K=0` reproduces the
   current formulation exactly.
3. **Strongest reason to accept.** The `K=0` ablation *is* the state-of-the-art comparison, and
   the free-lunch test (one scalar per dataset, zero learned parameters, predicted to remove
   >= 40 % of excess error at `d > 15 px`) is falsifiable, cheap and genuinely surprising if true.
   The headline claim costs ~10 GPU-hours of pure inference.
4. **Strongest reason to reject.** The proposition is true and its consequence is void on the data
   that exists. In 32.5 % of DSEC train frames — the ones with a 15 ms window, where `v T` is
   large enough to see — the exposure is **pinned at exactly 14996 us for every frame of every
   one of the six sequences**, both cameras identical. `T` is not latent; it is a constant that
   the AE loop saturated and the dataset published. In the frames where `T` genuinely varies
   frame-to-frame by 12.5x, its absolute value is 337–4207 us, giving 0.5–5.8 cm of ego motion
   and ~0.1–1.3 px of object displacement. So the estimator has nothing to estimate where the
   effect is large, and nothing to see where the estimation would be interesting. On deployed
   hardware the position is worse: production automotive and robotic cameras run fixed exposure
   or hardware-triggered global shutter precisely so that this quantity is known.
5. **Factual errors.** (a) "essentially no downstream method reads it [the exposure file]" — true
   and fine. (b) "Prediction: `T` spans more than an order of magnitude within a single sequence
   under auto-exposure (~1 ms daylight to >15 ms night)" — measured: the largest *within-sequence*
   span is 12.5x in interlaken_00_d (337 -> 4207 us), and no single sequence spans 1 ms to 15 ms.
   The order-of-magnitude span is *between* sequences. This matters because the paper's Fig 1a is
   built on the within-sequence claim. (c) "prediction >= 1 ms on a substantial fraction of frames"
   for the left-right exposure-midpoint difference — measured at median 8–72 us and **max 190 us**,
   i.e. five times smaller than predicted at the extreme and two orders below the window width.
   The brief already flags that an argument resting on left/right divergence rests on the smaller
   effect; this specific prediction is falsified by the data already on disk. (d) FE240hz access
   risk is "medium-high"; it is realised (§0).
6. **Overclaim.** "no amount of data, capacity, or fusion architecture can recover which one the
   label meant." True for a *single* frame in isolation; false for a *sequence*, where the frame
   rate, the AE ceiling and the events jointly pin the window to within microseconds — which is
   what the paper's own `L_cm` term does. The abstract must not assert the single-frame result as
   a system-level impossibility.
7. **Experiment a hostile reviewer demands.** SIE (`|T_hat - T|` in ms) validated against DSEC's
   published exposures, which the paper proposes. Its absence would be fatal. But note the trap:
   validating on the 32.5 % pinned frames is trivial (predict 14996), and validating on the
   daytime frames measures sub-millisecond estimation against sub-pixel effects. The paper must
   report SIE **stratified by regime** or the number is meaningless.
8. **Fixes.** (i) Replace FE240hz (§0). (ii) Correct predictions (b) and (c) against the measured
   data before writing. (iii) Report SIE stratified by exposure regime. (iv) State plainly, in
   the introduction, that for a third of DSEC the exposure is a known constant, and re-scope the
   contribution to `alpha` (which convention the label used) rather than `T` — the paper's own
   Risk-3 fallback (d) already says this and it should be the main line, not the fallback.

### Team 09 — Change-time — **BORDERLINE**

1. **Verdict.** BORDERLINE. Single unfixed structural problem: **its own make-or-break prediction
   places the competitor's failure at a speed ratio of 25:1, which is above the ratio that occurs
   in the scenes it targets.**
2. **Summary.** Replaces the second with the contrast threshold: `tau(x,t) = C N(x,t)`, a per-pixel
   counting clock with no free parameter, exactly invariant to any monotone time warp. The frame
   then acquires a *measured* per-pixel support width `W(x) = C N_exp(x)`, which is exactly zero
   where the scene was static — so the alignment cost provably vanishes there — and the fusion
   weight `1/W(x)` is derived from the sensor model rather than learned. The scholarship is
   outstanding: the `beta`-is-the-window identity read out of DAGr's and AEGNN's released code is
   the strongest single piece of evidence anywhere in this round.
3. **Strongest reason to accept.** `W(x) = 0` ⇒ nothing to align, cost exactly zero, is the
   cleanest statement of the seed observation produced by any team, and it is checkable
   (SWC: correlation of `W(x)` with per-pixel blur severity). The invariance is a *unit test*
   (RIG = 0 to float precision), not a benchmark delta, which is rare and valuable.
4. **Strongest reason to reject.** P3 is the decisive experiment and it predicts that ASTW —
   the CVPR 2026 competitor — is flat to `rho ~ 25` and only then breaks. A car at 20 m/s and a
   pedestrian at 1 m/s is `rho = 20`. A car at 14 m/s and a cyclist at 5 m/s is `rho = 2.8`.
   Ego-motion-dominated driving scenes have most flow within a factor of ~5. **The team has
   pre-registered a prediction that its competitor survives the operational regime and fails only
   in a constructed one.** Winning P3 at `rho = 64` at fixed global event rate is a lab result
   about a lab stimulus. Pillar 2 is stronger but depends on BS-ERGB/HS-ERGB (form-gated,
   emailed links) and HetVel (release unconfirmed).
5. **Factual errors.** None found; the verification standard here is the highest in the round,
   including the correct identification that FE108's host is dead and that EventVOT has no RGB.
   One scoping issue: the AER-bus-saturation argument ("recorded timestamps are already
   `phi(t)`") is real but is a *high-event-rate* phenomenon; at DSEC driving rates on a Gen3.1
   the bus is not saturated, so the motivation does not transfer to the automotive setting it
   uses for pillar 2.
6. **Overclaim.** "a car at 20 m/s and a pedestrian at 1 m/s run two clocks at a 20:1 ratio in one
   image." Image-space event rate is driven by `|grad L . v|`, not by metric speed: a pedestrian
   at 3 m distance and a car at 40 m can have comparable angular rates. The 20:1 figure is a
   metric-space ratio presented as an image-space one, and it is the number the whole `rho` sweep
   is calibrated against.
7. **Experiment a hostile reviewer demands.** Measure the *empirical* distribution of per-pixel
   event-rate ratio `rho` in DSEC and HetVel before running the sweep. If the 99th percentile is
   below 25, P3 is unwinnable in any operational sense and pillar 1 should be dropped in favour
   of pillar 2 immediately. This is one day of work on data already budgeted and it is not in the
   plan.
8. **Fixes.** (i) Measure the real `rho` distribution first and re-target P3 to it. (ii) Convert
   the metric-speed ratio to an angular-rate ratio throughout. (iii) Start the BS-ERGB and
   HS-ERGB forms today; pillar 2 has no fallback without them. (iv) Cut the 409-line document to
   the two pillars and their two decisive experiments.

### Team 02 — Exposure-occupancy measures — **REJECT**

1. **Verdict.** REJECT. Fatal to *this execution*, not to the idea. Two independent reasons, either
   of which is sufficient.

2. **Fatal reason A — the load-bearing prediction is contradicted by the paper's own definitions.**
   Prediction 1 reads: *"At `nu = 0` and `beta = 3` (a streak three object-diagonals long — severe
   blur), `D < 0.05`. Severe blur with zero acceleration produces a perfectly well-posed label."*
   And the paper says of it: *"Prediction 1 is the one that indicts the formulation."*
   But `D` is defined as `1 - min_{A,A' in 𝒜} IoU(A[y], A'[y])`, and the paper's own table of `𝒜`
   contains `A_start`, `A_end` and `A_hull`. At constant velocity with `beta = 3`, the start box
   and the end box are separated by three object diagonals and **do not overlap at all**, so
   `IoU(A_start, A_end) = 0` and `D = 1`. Even excluding the endpoints, `IoU(A_mid, A_hull) ~ 1/4`
   gives `D ~ 0.75`. The predicted value is `< 0.05`. The prediction is off by a factor of
   fifteen to twenty *by arithmetic on the paper's own page*, before any experiment is run.
   The only repair is to restrict `𝒜` to `{A_mid, A_mean, A_mode}` — but those three coincide
   *exactly* at constant velocity by the paper's own argument, so `D ≡ 0` identically, the
   prediction becomes a tautology rather than a measurement, and the "conventions are all
   defensible, all in active use, all different" framing that motivates the entire paper
   collapses to three functionals that agree whenever the label is well posed. The paper is
   caught between a false prediction and a vacuous one. This is not a typo; it is the axis the
   thesis rests on.

3. **Fatal reason B — the controlled variable is unattainable on any real platform.**
   `nu = ||v(t0+T) - v(t0)|| T / diag(box)`. Take the paper's own headline target, `nu = 1`,
   which it predicts gives `D > 0.5`. On DSEC's median 1.18 ms exposure with a 50 px box, `nu = 1`
   requires an intra-exposure velocity change of `50 / 0.00118 = 42,000 px/s` — a change of
   image velocity, inside 1.18 ms, of about 76 m/s at 10 m range. On the 15 ms AE-ceiling frames
   with a 165 px box it requires `11,000 px/s` of change in 15 ms, i.e. an image acceleration of
   `733,000 px/s^2`. Neither vehicle, drone, pedestrian, cyclist, nor manipulator produces this.
   The paper's own escape hatch — in-exposure *rotation*, where `A_mean != A_mid` on SO(3) even
   at constant angular velocity — is legitimate physics but it abandons the bounding-box
   detection framing that the FE240hz leaderboard-flip experiment (the paper's "indictment")
   requires, and it moves the work to EVIMO2 pose, which is a different and much smaller paper.
   Verdict on regime: **constructed corner case**, and one the paper cannot reach from any dataset
   it names.

4. **Summary proving I read it (rubric item 2).** The paper defines the exposure-occupancy measure
   `mu = y_# Unif(W)`, proves that a frame is a linear functional of `Pi_# mu` alone (hence
   invariant to every time reparameterisation including reversal) while events determine the
   parametrisation but not the mass, and concludes that neither modality alone identifies the
   intra-exposure state process. It predicts the exposure-occupancy measure with a spline support
   curve plus a 16-bin dwell density, learns the annotation convention `pi` by EM as a latent, and
   supplies split-conformal coverage that is valid *marginally over the benchmark's own unknown
   convention*, which is a genuinely clever move.

5. **Strongest reason to accept, stated fairly.** Two things here are excellent and should survive
   into whatever replaces this. The **time-reversal pair** experiment is a proof, not a benchmark:
   two clips traversing A->B and B->A over one exposure give bit-identical frames and identical
   point labels, every frame-only method and every uncertainty head is at chance, and the event
   term separates them at ~100 %. And **convention-marginal conformal coverage** is the right way
   to audit a set-valued prediction against a point-labelled benchmark without knowing the
   convention. Both are reusable regardless of this paper's fate. For a robot, the support *width*
   is also the quantity a controller most wants — a planner that knows a box is "one arbitrary
   pick from a 40 px set" behaves differently from one that thinks the box is a fact. The idea is
   not wrong; this execution of it is.

6. **Strongest reason to reject (rubric item 4).** Reason A above: the paper's indictment
   prediction is arithmetically false against its own convention set.

7. **Other factual errors.** (a) FE108 is "gated by an application form ... apply in week 1" —
   the endpoint refuses TCP (§0), so the "primary real validation" does not exist, and the paper's
   own kill criterion (day 7, on FE108 or EVIMO2) can only be run on EVIMO2, where the task is
   6-DoF pose, not boxes, and the leaderboard-flip experiment is impossible. (b) "at 20 FPS there
   are up to 12 Vicon labels inside one frame period" — 240 Hz over a 50 ms period is 12 labels
   per *frame period*, but the paper needs labels inside the *exposure*, which on a DAVIS346 in
   the sequences it targets is a small fraction of the period; the number of GT samples inside the
   support is what the method needs and it is not 12.
8. **Overclaim.** "the RSR change of a single fixed model under a convention switch is 10–20
   points, whereas the RSR spread between the five published trackers is 3–8 points. The
   convention moves the score more than the method does." This is the paper's most quotable
   sentence and it is a prediction dressed as a finding, on a dataset that cannot be downloaded.
9. **Experiment a hostile reviewer demands.** Ablation A1 (frame-only / event-only / both on the
   time-reversal pairs). Its absence is fatal. Its presence does not rescue the paper, because A1
   proves identifiability, not that the phenomenon has a regime.
10. **Ranked fixes, i.e. what a resubmission must do.** (i) Fix or delete Prediction 1 and rebuild
    the difficulty-axis argument on a `nu` range that is attainable — most plausibly in-exposure
    *rotation* on EVIMO2, which the paper already identifies as its Risk-1 fallback and which
    should be the main line. (ii) Drop every FE108 dependency (§0). (iii) Re-target the
    contribution to what survives: the time-reversal identifiability proof and convention-marginal
    conformal coverage, which do not need the acceleration story at all. (iv) State the operational
    regime up front — this is a manipulation, sports and machinery paper, not a driving paper — and
    stop borrowing automotive framing it cannot support.

---

## "So what?" audit

For each idea: the concrete downstream consequence **if the idea is entirely correct**, quantified,
marked DECISIVE / REAL BUT SMALL / IGNORABLE; then, separately, whether the regime it needs is
OPERATIONAL or a CONSTRUCTED CORNER CASE.

**Team 01 — latent exposure support.**
*If entirely correct:* dataloaders read `image_exposure_timestamps_*.txt`, and every published
event-RGB box shifts by `(alpha_hat - alpha_model) * d_hat` along the motion direction. On DSEC
daytime (median `T = 1.18 ms`) that shift is **0.1–1.3 px**, below annotation noise. On the 15 ms
night sequences it is **4.6 px** for a car crossing at 15 m and **9.9 px** for a cyclist at 5 m,
i.e. 3 % and 15 % of box width. In metres of world error: `alpha` mis-set by 0.5 on a 15 ms window
at 50 km/h is **10.4 cm** of ego-relative position. Against a brake system that needs 200+ ms of
pressure build-up, and a 20 Hz camera that has already conceded 69.5 cm of inter-frame aliasing at
100 km/h, this is not a control error and not a collision. **REAL BUT SMALL**, and only in the
night third of the benchmark.
*Regime:* **OPERATIONAL but narrow** — night urban driving is operational, and 32.5 % of DSEC
frames sit there. What is *not* operational is the latency of the claim: production cameras on
vehicles run fixed exposure or hardware trigger precisely so that `T` is known. The paper's
premise is a property of a research dataset's auto-exposure loop, not of a deployed rig.

**Team 02 — exposure-occupancy measures.**
*If entirely correct:* benchmarks would publish set-valued labels and report a coverage-efficiency
frontier instead of a point mAP, and a quarter of the remaining headroom on FE108 would be shown
to be definitional. For a robot, the useful half is the support width as a first-class output: a
planner that receives "40 px set" instead of "box" can inflate its safety envelope correctly
instead of guessing. That is worth something. But the effect requires `nu ~ 1`, which needs
`~10^5–10^6 px/s^2` of image acceleration (§Team 02 reason B). **IGNORABLE** for any vehicle,
drone or AMR. Genuinely DECISIVE for bat-ball contact, propeller and fan-blade imaging, and
impact events in manipulation — all real, none automotive.
*Regime:* **CONSTRUCTED CORNER CASE** for the domain the paper argues in; operational for a
different domain it does not target.

**Team 03 — temporal support fields with abstention.**
*If entirely correct:* a perception module emits, per pixel and per query instant, an answerable
mass `alpha`, and the vehicle refuses to plan through regions where `alpha < tau_abstain`. This is
the one output in the round that a safety case can consume: it converts "the detector was
confidently wrong about an occluded region" into "the detector declared no coverage," which is
the difference between a silent failure and a handover. The measured stake, using the team's own
prediction 5: the lowest-mass 10 % of pixels carry ~4x mean error and are **not identified by any
existing confidence score** — so today that 10 % is being planned through blind. On a 100 km/h
highway, correctly flagging even one frame's worth of no-coverage region is a 1.4 m difference in
where the planner will commit. **DECISIVE**, conditional on the abstention being calibrated
(their SCE metric) rather than merely present.
*Regime:* **OPERATIONAL for the mass/staleness axis, CONSTRUCTED for the overlap axis.** Pixels
with stale event support and saturated frame support genuinely exist at every tunnel entrance and
every night scene — that is real and does not need fast motion. The dwell-then-dash matched-pair
construction that produces the headline `O*` cliff is a laboratory stimulus. The team should lead
with mass, not overlap; its own Death-1 fallback says exactly that and it should be promoted to
the main line.

**Team 04 — effective timestamp and dispersion.**
*If entirely correct:* every fused event-RGB predictor's output is stamped with `tau_hat` and a
dispersion `sigma_tau`, and downstream consumers stop treating a spatially-varying timestamp as a
single one. Predicted magnitudes: `b ~ 2.5 ms`, `sigma_tau ~ 1.5 ms` at `T_exp = 10 ms`. At
50 km/h: **3.5 cm and 2.1 cm**. At 130 km/h: 9.0 cm and 5.4 cm. On a 19.5 cm quadrotor at 5 m/s:
1.25 cm and 0.75 cm. Every one of these is smaller than the localisation error of the detectors
being measured and far smaller than the actuation delay downstream. The *scientific* claim
(`sigma_tau > 0` ⇒ no scalar correction exists) is important; the *magnitude* is not.
**REAL BUT SMALL**, verging on IGNORABLE for actuation, DECISIVE only as a statement about what
benchmarks can see.
*Regime:* **OPERATIONAL.** `T_exp` in the 1–15 ms range and speeds of 250–4000 px/s are ordinary
driving and ordinary drone numbers. Nothing here needs a constructed stimulus, which is a real
credit to this team — it is a small effect in a real regime, not a large effect in a fake one.

**Team 05 — support kernels and spectral nulls.**
*If entirely correct:* a fusion stack receives a per-pixel mask saying "the frame carries no
information at spatial frequencies near `k/(vT)`, and reports contrast with the *wrong sign*
between the first and second null." That second part is the operationally interesting one: an
L1/L2 fusion objective averaging a sign-flipped observation with a correct one produces a
*systematic bias*, not extra variance, and PSNR/SSIM/EPE cannot see it. Onset at `b >= 2 px`.
Using §1: DSEC daytime gives `b ~ 0.1–1.3 px` (below onset); the 15 ms night frames give
`b ~ 4.6–9.9 px` (2–5x above onset, so the first two nulls are inside the passband). So the
effect is off in two-thirds of the benchmark and on in one-third. Second consequence: every
event-frame temporal calibration in the field returns a number that drifts with how fast the
calibration target moved — predicted `>= 3 ms` of drift at `T = 10 ms`, against sub-millisecond
claimed precision. **That** is decisive for anyone who calibrates a rig: it means published
sub-millisecond sync figures are precise about the wrong quantity. **DECISIVE for calibration
practice, REAL BUT SMALL for task accuracy.**
*Regime:* **OPERATIONAL, in the night third.** The team correctly predicted this would be the
answer and built the go/no-go around it.

**Team 06 — the exposure gap.**
*If entirely correct:* (a) every two-frame event-frame consistency term in the field carries a
deterministic, motion-conditioned bias of 0.5–2.6 contrast thresholds, currently charged to noise;
(b) more importantly, the standard per-pixel contrast-threshold calibration recipe returns
`c_hat = 0.049` at 8 px of blur and `-0.004` at 32 px when the truth is 0.200 — a **75 % to 102 %
error, with a sign flip, on a physically perfect sensor**. Anyone who calibrated a DVS by moving a
target in front of it has a wrong number in their config file, and the error scales with how
enthusiastically they moved the target. That number propagates into every event-based
reconstruction, every EDI-style deblur, every simulator calibration, and every contrast-threshold
assumption in a robotics stack. It is removable in closed form, one line. **DECISIVE** — the
single largest, most concrete, most immediately fixable practical defect identified anywhere in
this round.
*Regime:* **OPERATIONAL.** Blur of 8–32 px is exactly what you get when you wave a calibration
target, which is exactly how people calibrate. This is not a corner case; it is standard practice
producing a wrong answer.

**Team 07 — chronofields.**
*If entirely correct:* time-to-contact and crossing times are predicted directly, with a
calibrated distribution and a "never" atom, at P95 error of **0.5–1 ms** instead of the
detect-then-extrapolate route's **8–25 ms**. Convert: at 100 km/h closing on a stationary
obstacle, a 25 ms TTC error is **69 cm** of range; a 1 ms error is **2.8 cm**. Sounds decisive
until you put it against the specification: forward-collision-warning thresholds are set at
TTC of order 1.4–2.7 s, so 25 ms is **1–2 % of the trigger threshold**, and the brake actuator
itself contributes 100–300 ms. The honest statement is that the chronofield buys 24 ms of a
budget where 200+ ms is spent downstream. **REAL BUT SMALL for AEB.** But **DECISIVE for
contact-timing**: a bat-ball or foot-ground contact lasts 2–5 ms, and at 30 fps more than 90 % of
contacts fall strictly between frames — there the conventional formulation has no output slot at
all, so the comparison is not "better" but "possible versus impossible."
*Regime:* **CONSTRUCTED CORNER CASE for driving, OPERATIONAL for manipulation, sports and impact
sensing.** The team should stop marketing this as an AEB paper and market it as a contact-timing
paper, where its claim is unanswerable.

**Team 08 — support error decomposition.**
*If entirely correct:* every event and event-RGB benchmark reports a triple `(AP, tau_hat, AP^perp)`
instead of a scalar; every method declares `(c_P, w_P)`; and every deployed detector's output
carries a corrected timestamp. Concrete: `tau_hat(RVT) ~ -25 ms` means an RVT box on a vehicle at
50 km/h describes the world **34.7 cm ago**, and at 130 km/h **90.3 cm ago**. Because it is a
constant bias with a known sign, a downstream constant-velocity update removes it **exactly and
for free** — but only if it is declared, and today it is not. Second consequence, P7: if a
sensor-free constant-velocity propagator reproduces DSEC-Det's and DSEC-3DOD's inter-frame ground
truth to median IoU > 0.9, then the headline "low-latency inter-frame detection" results of two
flagship benchmarks are, in part, measurements of agreement with an interpolation prior. That
would change what those benchmarks are used for. **DECISIVE** — not because 25 ms is large, but
because it is free to fix and nobody is fixing it.
*Regime:* **OPERATIONAL, unconditionally.** It requires no fast motion, no special exposure, no
constructed stimulus. It requires only that a method have a temporal aggregation window, which
every event method does. This is the only idea in the ten whose effect exists at every speed
including zero relative motion — the bias is set by the window, not the scene.

**Team 09 — change-time.**
*If entirely correct:* event representations stop emitting durations, so there is no clamp, no
rate-estimation lag, and no speed dynamic-range ceiling; and the frame acquires a measured
per-pixel support `W(x)` that is exactly zero on static pixels. Practical consequence: onset
response latency drops from `~100 ms` (ASTW's EMA over a 250 ms reference window) to **0** — that
one is genuinely decisive, because a pedestrian stepping off a kerb is exactly a 4x acceleration
step and 100 ms at 50 km/h is 1.39 m of ego travel before the representation adapts. But that
consequence belongs to the *onset-latency* argument (P5), not to the `rho`-sweep argument (P3)
that the team makes central. The `rho = 64` clamp-limit result requires a scene with a 64:1
per-pixel event-rate ratio at fixed total rate; real driving scenes are dominated by ego-motion
flow within a factor of ~5, and the sharpest realistic case (car 20 m/s, pedestrian 1 m/s in
metric terms — less in angular terms) sits at or below ASTW's 25:1 clamp. **REAL BUT SMALL for
P3, DECISIVE for P5**, and the team has ranked them the wrong way round.
*Regime:* **P3 CONSTRUCTED CORNER CASE; P5 and pillar 2 OPERATIONAL.** Recommend inverting the
paper's emphasis.

**Team 10 — fusion is ill-typed.**
*If entirely correct:* the event branch of every published RGB-event fusion model contributes less
as scene speed rises, with event utility at the top flow decile at most 60 % of its value at the
median and below 0.3 mAP for at least two models. Consequence for a buyer: **you are paying for a
second sensor whose contribution decays exactly in the regime you bought it for.** That is a
procurement-grade finding — it says the correct engineering response to fast motion is not "fuse
harder" but "route by support or drop the frame," which is precisely what the deployed literature
already did (Bhattacharya CoRL 2024 uses events only; Bauersfeld T-RO 2026 uses events only).
Quantified: a fusion model that loses 1.5 mAP of event contribution in the top flow decile has,
at DSEC-Det scale, given up the entire margin that motivated adding the sensor.
**DECISIVE if the inversion is real; IGNORABLE if the curve merely flattens** — and the paper's
own fallback (support-blind pairs) is a theorem, so it cannot come back empty-handed.
*Regime:* **OPERATIONAL.** `s = |v| T` in the 0.25–16 px range covers DSEC night and every
manipulation and drone setting; the fine-tune control needs no constructed stimulus. Panel C's
design, however, is currently invalid (§1.3) and must be made within-sequence.

---

## Ranking

1. **Team 08 — Right Place, Wrong Time.** The only idea whose correctness changes a number in a
   deployed config file this week, at 35 GPU-hours with nothing trained and every artifact
   verified by HTTP HEAD; its effect exists at every speed because it is set by the aggregation
   window, not by the scene.
2. **Team 06 — The exposure gap.** The only idea whose headline is already measured rather than
   predicted, and its calibration corollary (`c_hat` 0.200 -> -0.004 with blur, perfect sensor) is
   a live defect in every lab that owns an event camera.
3. **Team 05 — No offset can fix a width.** An impossibility bound that cannot fail because it is
   the Fourier transform of a box; produces a usable per-pixel blind-band mask; best compute
   profile in the round; and it predicted in advance the exact DSEC regime split that my
   recomputation confirms.
4. **Team 03 — Temporal support fields.** Abstention is the most valuable output in the ten for a
   safety case, and half the supervision is real and free; lead with mass, not overlap.
5. **Team 10 — Fusion is ill-typed.** The most consequential checkable claim in the round for a
   systems audience, inference-only, with a theorem as its floor — held back by an invalid
   Panel C design that is fixable in a paragraph.
6. **Team 04 — Effective timestamp.** The best-engineered pilot and the most honest pre-registered
   null in the set, measuring an effect (2.5 ms, 3.5 cm at 50 km/h) that is real, operational,
   and too small to matter downstream.
7. **Team 07 — Chronofields.** The only team that speaks in AEB units, undermined by losing both
   of its real sub-frame ground-truth sources and by an inverted-map framing whose strongest case
   (contact timing) is not the case it argues.
8. **Team 01 — Latent exposure support.** A correct theorem about a quantity that is a published
   constant in the 32.5 % of frames where it would matter, with its money plot on a host that
   refuses TCP.
9. **Team 09 — Change-time.** Best literature verification in the round and the weakest
   operational stake; its own decisive prediction says the competitor survives every real scene,
   and the sub-argument that *is* decisive (zero onset latency) has been demoted to P5.
10. **Team 02 — Exposure-occupancy measures.** Excellent identifiability machinery attached to a
    difficulty axis that requires an intra-exposure acceleration no platform produces, and a
    load-bearing prediction that its own convention table contradicts by a factor of fifteen.

---

## My winner and its fatal flaw

**Winner: Team 08 — "Right Place, Wrong Time: Temporal-Support Error Is the Unmeasured Half of
Event-RGB Benchmarks."**

Why it wins on my axis and not merely on mine. It is the only submission in the ten that answers
"suppose you are completely right — what changes?" with something a person does rather than
something a person knows. If `tau_hat(RVT) = -25 ms` and is predictable from the declared
aggregation window, then the correct engineering response is one line: stamp the detector's output
at `t - 25 ms` and let the existing motion model cancel 34.7 cm at 50 km/h and 90.3 cm at
130 km/h. Nobody does that today, not because it is hard but because the number has never been
published. The paper also proposes no method, trains nothing, invents no architecture, derives its
one free parameter (`tau_max`) from the benchmark's and the method's own published specifications,
pre-registers `tau_hat` from architecture before measuring it, and ships an isotropic null that
can falsify its own metric. Under a November 2026 deadline on 9 GB of a shared card, that
combination — 35 GPU-hours, no training, checkpoints and tarball sizes verified by HTTP HEAD, and
a zero-GPU experiment (E0) that stands alone — is worth more than any of the beautiful
formulations above it in conceptual ambition. And it does not touch FE108, which four of its
competitors do.

**Its fatal flaw: the paper's central quantity is almost certainly a property of the benchmarks
rather than of the methods, and the paper's own defence against that concedes the point.**

Death 3 in team 08's risk section names it — "you are measuring the labels, not the models" — and
answers that a shared `tau_hat` is itself publishable and that C3 discriminates: if `tau_hat`
tracks each method's declared window, it is the method; if it is constant across methods with
different windows, it is the dataset. That answer is correct and it is not enough, because of a
fact team 08 itself verified: **every event detector on Gen1 and 1 Mpx uses the same 50 ms
`stacked_histogram_dt=50_nbins=10` representation.** RVT-{T,S,B} and S5-ViT-{B,S} share it — that
sharing is exactly why team 08 chose the pair as its "fair-comparison guarantee." So on the two
datasets carrying most of the measurement, `w_P` does not vary across methods, C3 cannot
discriminate, and `tau_hat` will come back near-identical for all five. The correction is then a
uniform shift, P6's ranking flip does not occur, and the paper falls back to "here is a number
for every published method" plus E0. That is a benchmark note, not a CVPR paper.

The escape exists but it is thin and it is the whole bet: **the only genuinely single-variable
instruments in the plan are BFlow `E` vs `E+I` on DSEC-Flow (same authors, same architecture, same
training, differing only by an image branch whose support is ~100x wider) and E-RAFT on MVSEC at
20 Hz vs 45 Hz.** Two checkpoint pairs, 156 MB and 64 MB, roughly two GPU-hours, and the entire
distinction between "we measured the methods" and "we measured the datasets" rests on them. If
`E+I` wins on EPE and loses on `EPE_perp` with `|tau_hat(E+I)| > |tau_hat(E)|`, the paper has a
published, author-released, single-variable demonstration that adding frames buys spatial accuracy
by paying temporal-support error — and then it is a very good paper. If that pair comes back flat,
nothing else in the plan can substitute for it, because nothing else varies `w_P` while holding
architecture and training fixed.

My recommendation to the AC: run E0 and E2 in week one, in that order, before touching Gen1 or
1 Mpx. E0 is a 4.7 MB label file and no GPU. E2 is two checkpoints and two GPU-hours. Together
they decide whether this is a paper or a note, and they cost less than a day.
