# Reviewer 03 — evaluation, benchmarks, and metric design

*CVPR20 idea-selection round. Specialism: is the proposed evaluation a measuring instrument
or a scoreboard the authors built to stand on?*

Ten ideas. Between them they invent **roughly sixty new metrics**. For calibration: in the
decade the community actually adopted maybe five (sAP, HOTA, LPIPS, TIDE's error buckets,
and — provisionally — CMMD). The base rate for an invented metric surviving contact with
the field is therefore under 10 %, and every idea below is asking me to bet against that.

**Procedural note on grounding.** This session's WebSearch budget (200 calls) was already
exhausted when I began — the same defect the brief records for the idea teams. Acceptance was
therefore verified two ways, neither of which is a search engine. (a) I pulled the **official
proceedings listings** and grepped them locally: `openaccess.thecvf.com` for CVPR 2024 (2,716
titles), CVPR 2025 (2,871), CVPR 2026 (4,042) and ICCV 2025 (2,701); `ecva.net` for ECCV 2024
(2,387); `papers.nips.cc` for NeurIPS 2024 (4,034 main + 459 Datasets & Benchmarks). A title
present in an official listing is *confirmed accepted*, not inferred. (b) Cross-checked against
the arXiv `comment` field and the OpenAlex works API (DOI prefixes `10.1109/cvpr52733.2024.*`
= CVPR 2024, `10.1109/cvpr52734.2025.*` = CVPR 2025, `10.1007/978-3-031-7*` = ECCV 2024 LNCS).

Three negative results from that sweep matter for this round and are stated here because they
constrain what the ideas below may claim:

- **DSEC-Det does not appear in any of those six listings.** Its labels came with a
  Nature-family journal paper. Teams 01, 04, 07 and 08 should not cite it as a
  CVPR/ICCV/ECCV/NeurIPS paper.
- **"Beyond mAP: Towards Better Evaluation of Instance Segmentation" is not in any of the
  19,210 titles grepped.** If any team is carrying it as a CVPR precedent, that is wrong.
- **No paper at these six venues, in window, performs bootstrap confidence intervals on
  leaderboard *rankings*.** The nearest thing is C10 below, which estimates the precision of an
  accuracy *estimate*, not the significance of a ranking *flip*. This cuts both ways for team
  08: there is no established methodology it can lean on, and there is genuinely open ground
  if it does the statistics properly.

---

## Comparison set

Twelve papers whose primary contribution was a benchmark, a metric, or an evaluation
critique — every one located in an official proceedings listing, all 2024–2026. This is the bar.

| # | Paper | Venue | What it did | Why it was accepted |
|---|---|---|---|---|
| C1 | **Rethinking FID: Towards a Better Evaluation Metric for Image Generation** (Jayasumana et al.) | **CVPR 2024** — DOI `10.1109/cvpr52733.2024.00889` | Shows FID contradicts human raters, fails to reflect iterative text-to-image improvement, is biased by sample size and by a false Gaussianity assumption; proposes CMMD. | It attacked the field's *most used* number and produced a **disagreement with an external referent (human raters)** rather than with another metric. A metric critique earns its place by exhibiting a case where the incumbent metric ranks two systems the opposite way from a ground truth nobody disputes. |
| C2 | **Benchmarking Object Detectors with COCO: A New Path Forward** (COCO-ReM; Singh, Yadav, Jain, Shi, Johnson, Desai) | **ECCV 2024** — DOI `10.1007/978-3-031-72658-3` series (LNCS) | Re-annotates COCO masks (imprecise boundaries, non-exhaustive instances, mislabeled masks), re-scores **fifty** detectors, and shows the corrected labels change which models win. | The archetype of the paper the brief's "interpolated GT" question points at: it proved the *labels*, not the models, were producing part of the leaderboard, and it shipped the corrected labels so anyone could re-run it. **Fifty models, released artifact, ranking change.** That is the standard. |
| C3 | **VBench: Comprehensive Benchmark Suite for Video Generative Models** (Huang et al.) | **CVPR 2024** — DOI `10.1109/cvpr52733.2024.02060` | Decomposes video-generation quality into 16 dimensions, each with its own metric, **each validated against human preference annotations**. | It did not just assert its dimensions were meaningful — it measured per-dimension agreement with humans. An invented metric with a human-agreement column is very hard to call self-serving. |
| C4 | **MMBench: Is Your Multi-modal Model an All-Around Player?** (Liu et al.) | **ECCV 2024** — DOI `10.1007/978-3-031-72658-3_13` | Shows single-pass multiple-choice scoring is unstable to option order; introduces CircularEval plus LLM-based choice extraction as the protocol. | Pure **protocol** contribution. Accepted because it demonstrated that reported numbers moved under a change nobody thought was a degree of freedom. |
| C5 | **Ev-3DOD: Pushing the Temporal Boundaries of 3D Object Detection with Event Cameras** (Cho et al.) | **CVPR 2025 (Highlight)** — DOI `10.1109/cvpr52734.2025.02533`, arXiv 2502.19630 | DSEC-3DOD / Ev-Waymo, with 100 FPS "blind-time" GT built by **linear interpolation of 10 FPS boxes plus expert refinement over VFI-synthesised sensor data**. | The most directly relevant precedent and, for this round, a *cautionary* one: a Highlight paper's headline GT is partly a motion prior and a VFI network's output. Any idea here that evaluates against DSEC-3DOD inherits that. |
| C6 | **eTraM: Event-based Traffic Monitoring Dataset** (Verma, Chakravarthi, Vaghela, Wei, Yang) | **CVPR 2024** — DOI `10.1109/cvpr52733.2024.02136` | 10 h of static-camera event data, 2 M boxes, 8 classes, day/night/weather, with cross-condition generalisation evaluation. | A dataset paper clears CVPR when it opens a *regime* existing benchmarks cannot address (here: night and unseen environments) and reports baselines under a stratification the field could not previously do. |
| C7 | **LEOD: Label-Efficient Object Detection for Event Cameras** (Wu et al.) | **CVPR 2024** — DOI `10.1109/cvpr52733.2024.01602` | Self-training / label refinement for sparsely-annotated event detection on Gen1 and 1 Mpx. | Directly relevant: it treats event-detection labels as *incomplete and noisy* and is accepted on that premise. Anyone claiming "nobody has questioned these labels" must engage it. |
| C8 | **State Space Models for Event Cameras** (Zubić et al.) | **CVPR 2024** — arXiv 2402.15584, comment: "CVPR 2024 Camera Ready" | SSM backbone whose headline result is robustness when the *inference-time* event window differs from training (3.76 mAP drop vs >20 for RNN/Transformer). | Shows the field already accepts "your score depends on a temporal hyper-parameter nobody reports" as a publishable finding — and that the accepted framing is a **method that is robust**, not a metric that reveals the sensitivity. Ideas here that only reveal the sensitivity are fighting an established alternative framing. |
| C9 | **Adaptive Bounding Box Uncertainties via Two-Step Conformal Prediction** (Timans et al.) | **ECCV 2024** — DOI `10.1007/978-3-031-73223-2_21` | Size-adaptive conformal coordinate intervals for detection boxes with marginal coverage guarantees. | The live baseline for any set-valued box prediction here (team 02 correctly names it). Accepted because coverage is *guaranteed*, not measured on a metric of the authors' choosing. |
| C10 | **On Calibration of Object Detectors: Pitfalls, Evaluation and Baselines** | **ECCV 2024** (ecva.net listing) | Shows the standard D-ECE + AP framework for detector calibration, and the use of Temperature Scaling, "lead to incorrect conclusions"; proposes a joint calibration-and-accuracy protocol. | **The purest ranking-flip-by-broken-protocol precedent in window.** Re-evaluating under the fixed protocol *reversed the field's conclusion*: cheap post-hoc calibrators (Platt, isotonic) beat the recent train-time SOTA. This is what a legitimate flip looks like — the *same* quantity, measured correctly, reverses an order. Team 08 should be held to this standard, not below it. |
| C11 | **Quality Assured: Rethinking Annotation Strategies in Imaging AI** | **ECCV 2024** (ecva.net listing) | 57,648 instance masks from 924 annotators + 34 QA workers across four companies and MTurk, measuring how internal QA affects reference-annotation quality. | The paper **states outright that it "does not describe a novel method"** and was accepted anyway, on the grounds that it establishes the foundation for reliable benchmarking. The existence proof that a pure measurement paper with no model clears a top CV venue — which is the bet teams 06, 08 and 10 are making. |
| C12 | **A Framework for Efficient Model Evaluation through Stratification, Sampling, and Estimation** | **ECCV 2024** (ecva.net listing) | Stratification by clustering on predicted performance plus model-assisted estimators, to estimate accuracy from a labelled subsample with explicitly analysed estimator precision. | The closest CV-venue precedent for treating a reported number as **an estimate with variance rather than a value**, and for *principled* stratification. Every idea below that stratifies ("the fast-motion decile") is competing against this standard and none of them cites it. |
| C13 | **The Elephant in the Room: Towards A Reliable Time-Series Anomaly Detection Benchmark** (TSB-AD) | **NeurIPS 2024, Datasets & Benchmarks Track** | Attacks flawed data, biased evaluation measures and inconsistent protocol simultaneously: 1,070 curated series, an analysis of measure bias identifying the reliable one, 40 algorithms re-run under unified tuning. | Accepted for doing all three legs at once and producing a reversal — simpler statistical methods often beat the neural architectures once the biased measures are removed. Directly analogous to what team 08's E0 could produce for event benchmarks. |
| C14 | **Streaming Detection of Queried Event Start (SDQES)** | **NeurIPS 2024, Datasets & Benchmarks Track** | Defines onset-detection in streaming egocentric video, with an Ego4D-based benchmark and **new task-specific accuracy/latency-tradeoff metrics**. | The in-window analogue of sAP: accepted because offline temporal-localisation scores structurally cannot express "how late were you," so the task needed its own latency-aware measures. The precedent teams 04, 07 and 08 should be citing and none of them does. |

Ancestors outside the 2024–2026 window that every one of these ideas must position against,
and which several do not: **TIDE** (ECCV 2020, DOI `10.1007/978-3-030-58580-8_33`) — the
error-decomposition template, entirely atemporal; **Towards Streaming Perception / sAP**
(ECCV 2020, DOI `10.1007/978-3-030-58536-5_28`) — latency folded into AP; **Spring** (CVPR
2023, DOI `10.1109/cvpr52729.2023.00482`) — a benchmark whose argument is that existing GT
is too coarse to discriminate methods; **Pervasive Label Errors in Test Sets Destabilize ML
Benchmarks** (Northcutt et al., NeurIPS 2021 D&B) — the original "the labels decide the
ranking" result.

One more, verified and directly on-topic, that the round should note: **"What Is the Optimal
Ranking Score Between Precision and Recall? We Can Always Find It and It Is Rarely F1"**
(CVPR 2026, in the openaccess CVPR2026 listing) — a pure theory-of-ranking paper with no model
at all, proving that F-beta-induced rankings trace a shortest path between the precision- and
recall-induced rankings and that the right tradeoff is usually not F1. Recent, in-domain proof
that "your headline score induces the wrong ordering" is a CVPR-grade claim on its own.

**What this comparison set teaches, and what I score against.** C1–C4, C10 and C13 all share
one structure: *the new measurement disagrees with an external referent the community already
trusts* — human raters (C1, C3), re-annotated ground truth (C2), a permutation the protocol
should have been invariant to (C4), or the same quantity measured under a corrected protocol
(C10, C13). None of them is accepted for defining a new axis and winning on it. C11 proves a
paper with **no method at all** clears the bar if the measurement is the contribution; C12 and
C14 set the standard for stratification and for latency-aware metric design respectively.
Every idea below is graded on whether it has such an external referent, or whether its
metric's verdict is determined by its own construction.

---

## Per-idea verdicts

| Team | Verdict | One-sentence reason |
|---|---|---|
| **06** | **STRONG ACCEPT** | Its headline number (fraction of the event–frame consistency residual removed by a zero-parameter, events-only predictor) needs no ground truth, no simulator and no labels, is computable by any third party from DSEC's shipped `events`, `images` and `image_exposure_timestamps` files, and ships with a real null (R² = 0.0015 against 0.78). |
| **08** | **ACCEPT** | The best-engineered anti-rigging design in the batch — relaxation budget `τ_max` derived from the benchmark's and the method's own published specs rather than tuned, an isotropic null, injection–recovery, and no proposed method — but its thesis sentence claims a ranking flip its own §4 disclaims, and every number is measured against interpolated labels. |
| **01** | **ACCEPT** | SIE (`\|T̂ − T\|` in ms against DSEC's published exposure timestamps, never seen in training) is the single best-designed validation across all ten ideas; the other three invented metrics require an intra-exposure ground truth that team 09 reports is no longer downloadable. |
| **02** | **BORDERLINE** | Genuinely metric-literate (CMC is computable on any point-labelled set, CI-AP degenerates to AP so every existing number is locatable on it), but the indictment rests on a Kendall τ over **five** trackers, where τ = 0.6 is one or two swaps and is not distinguishable from bootstrap noise. |
| **05** | **BORDERLINE** | OBD (`dδ̂/db`) is the rare invented metric needing *no labels at all* and with a principled null (a rig constant must have zero drift), but the whole edifice may be sub-pixel on every real dataset it can reach, in which case the paper is a correct and irrelevant Fourier identity. |
| **10** | **BORDERLINE** | The support-blind pair is a real impossibility construction that cannot fail, but OSAM's predicted curve `1 − r/(r+s)` is a geometric identity given a local mixing radius, so it will "confirm" for any spatially local architecture whether or not anything is wrong. |
| **04** | **BORDERLINE** | `τ̂` as argmin over a continuous GT trajectory is a good primitive, but `σ_τ > 0` — the paper's declared kill shot — has **no null model**, and any GT interpolation noise or flat argmin produces it for free. |
| **09** | **REJECT** | Two of its three headline metrics (RIG, SSI) are analytically determined by the construction and cannot come out any other way; the third (CDR) is read off a competitor's hyper-parameter table. |
| **07** | **REJECT** | Invents five metrics of which three (TCE, CMR, and CTE's distributional form) are unscorable for any existing method by construction, so the comparison table is against a strawman the authors defined into existence. |
| **03** | **REJECT** | The x-axis of the paper's one plot — ground-truth support overlap `O*` — does not exist on real data, so the headline claim is a statement about a simulator's own bookkeeping. |

---

## Detailed review

### Team 06 — *Frames Are Not Samples: The Exposure Gap* — **STRONG ACCEPT**

**Summary.** The claim is that the field's bridging identity `Δ log I = c·E` is not noisy but
misspecified: a frame is a log-mean-exp functional of the intra-exposure log-intensity
trajectory, and the bias has the closed form `J = ½·Var_W(L)`. The team then does the thing
almost nobody in this batch does — it regresses the *measured* residual `R` against a
predictor `P` that is computable from the event stream and the exposure windows alone, with
zero fitted parameters, and reports slope 0.955, R² 0.78 with all sensor non-idealities
switched off, against a random-regressor null of R² 0.0015. The residual is a dipole
straddling the motion trail whose global signed mean is ≈ 0, which is offered as the reason
every zero-mean noise check the field has run has passed.

**Strongest reason to accept.** `SFR` — the fraction of `Var(R)` removed by the
parameter-free LME correction — is the only invented metric in these ten ideas that a
hostile reviewer can compute themselves, on public data, without the authors' code, without
labels, without a simulator, and without ground truth of any kind. It needs two frames, the
events between them, and `image_exposure_timestamps_left.txt`. The machine record
(`experiments/e00`) confirms DSEC ships that file for 19 of 23 probed train sequences. A
metric a reviewer can falsify over lunch is a different object from a metric that requires
the authors' 240 Hz mocap pipeline, and the community has repeatedly rewarded the former
(C1's CMMD is a five-line function; C2's contribution is a downloadable label file).

**Strongest reason to reject.** The 99.1–99.3 % figure — the one that makes the paper sound
decisive — is measured on a synthetic band-limited translating texture with an ideal sensor.
On real DSEC it will fall, possibly a lot, because refractory dead time alone drops the
slope to 0.779 / R² 0.283 in their own table, and the real sensor has refractory *and* shot
noise *and* leak simultaneously. The paper's honest number on real data may be closer to
25–40 % than to 99 %, and "we explain a third of a residual the field calls noise" is a much
weaker abstract.

**Factual errors.**
- *§Stage 1:* "**DSEC** … is **the only public event–frame dataset with real per-frame
  exposure intervals**." Unverified universal claim, and it conflicts with team 01's
  assertion (§Risks 3d) that "DAVIS APS emits exposure start/end", which if true makes every
  DAVIS-based set (FE240hz, PKU-DAVIS-SOD) a counterexample. At most one of the two teams is
  right. Correction: soften to "the only public event–frame dataset we verified to ship
  per-frame exposure intervals as a file", or verify the DAVIS AEDAT claim and drop the
  "only".
- *§Why this is not closest work, EDI row:* the same paper is dated "CVPR 2019; TPAMI" here,
  "CVPR 2019" by teams 01/02/03/05/07/09, and "CVPR'19, TPAMI'20" by team 05. Harmless, but
  the batch as a whole has a citation-hygiene problem (see the cross-cutting list below).
- *§Risks Death 1:* two verification gates are declared open (Brandli ISCAS 2014 behind
  IEEE; *Electronics* 15(7):1420 (2026) returning 403). Declaring an unclosed gate is
  correct practice and I credit it, but it means the novelty claim is **provisional** and
  the brief instructs me to score that down. It does not change the verdict here only
  because the novelty claim is not what carries the paper — the measurement is.

**Claims exceeding evidence.**
- "on textured content — which is what natural video is — the residual is 2.6 contrast
  thresholds and **99 % of it is the exposure operator**." Measured on `band-limited
  translating texture`, ideal sensor, three seeds. That is not natural video; it is the
  best case for the predictor, and calling it "what natural video is" is the sentence a
  hostile reviewer will quote back.
- "**P6 — the bias is not absorbable by capacity.**" P6 was measured with a *linear model in
  generic event features*, not with a network. The paper's own Death-2 text concedes the
  network-scale version is unrun. The claim as stated is stronger than the experiment.

**Experiment a hostile reviewer will demand.** Run the `R ~ P` regression on **real DSEC**,
stratified by the measured exposure width, and report the slope and R² per sequence —
including the six night sequences pinned at 14 996 µs and the daytime sequences at 299 µs
median. If the slope stays near unity across a 50× change in exposure width on real data,
the paper is made. **Its absence is fatal**, because everything else is simulation, and the
brief's standing failure mode #1 is exactly a result that only exists in simulation. The
good news is that this experiment costs zero GPU-hours and no ground truth, so there is no
excuse for it not being Figure 2.

**Required fixes, ranked.**
1. Real-DSEC `R ~ P` stratified by measured exposure width, in the main paper, before any
   trained model. Report the slope's bootstrap CI per sequence, not pooled.
2. Report `SFR` on real data as the headline number and demote the 99 % synthetic figure to
   a controlled-condition row. Do not let a synthetic-best-case number into the abstract.
3. Close the two verification gates (Brandli 2014; *Electronics* 2026) or state in the paper
   that the exposure-gap identity may be known and reposition on the identifiability result
   (`G(a)` recovering per-pixel `c_p`, better conditioned under faster motion), which is the
   genuinely unclaimed piece.
4. Rename `SFR` — team 07 uses the same acronym for a different quantity, and both ideas
   are in this pool.
5. Add the network-scale version of P6 (train on short exposure / slow motion, test on long
   / fast, read out MCB) or drop the "not absorbable by capacity" phrasing.

---

### Team 08 — *Right Place, Wrong Time* — **ACCEPT**

**Summary.** The claim is that every event benchmark scores a prediction against ground
truth on a different clock with a different temporal support, so the dominant fast-motion
error — right place along the path, wrong time — is booked as spatial error. The proposal is
to decompose box-centre error into a component perpendicular to the GT track (pixels) and a
component along it converted to milliseconds by dividing by GT speed, fit one latency `τ̂`
per method by weighted least squares through the origin, and re-score released checkpoints.
The identifiability argument is that a timing error is a *one-parameter* perturbation that
must simultaneously explain translation, scale change and (in 3D) yaw, whereas a spatial
error is unconstrained — so the temporal hypothesis is testable rather than assumed.

**Strongest reason to accept.** E0 — the label forensics — is the highest-value experiment
in the entire ten-idea pool, and it costs a 4.7 MB label file and no GPU. It asks: does
DSEC-Det's inter-frame ground truth carry information beyond the linear-interpolation prior
that generated it, and can a *sensor-free* constant-velocity propagator reproduce it to
> 0.9 median IoU? This is C2's move (the labels, not the models, are producing part of the
score) applied to a benchmark that C5 made a CVPR Highlight. It is a genuine external
referent — the "no-sensor oracle" is not the authors' invention, it is the benchmark's own
generative process — and the answer is publishable in either direction. The design controls
around the decomposition are also the best in the batch: `τ_max` is **derived** from the
declared supports rather than swept, `AP^iso` is an equal-budget free-direction null with a
stated chance value, C4 is an injection–recovery calibration, and C5 is a falsification test
in which their own metric must fail if the training-free re-anchoring does not recover
`Δ_clock` **on the unmodified standard metric**. Most importantly: **they propose no method**,
which structurally removes the "you invented the axis you win on" charge for the ranking
claim's *author*, if not for its *shape*.

**Strongest reason to reject.** `AP^⊥` forgives, up to `τ_max`, exactly the error component
the authors argue is large — and it does so *more* for methods that are later. So
`AP^⊥ ≥ AP` always, and the gain is monotone in `|τ̂|`. A "ranking flip" between `AP` and
`AP^⊥` is therefore mechanically guaranteed for any pair whose AP gap is smaller than the
difference in their latencies, which is precisely the pair the paper says it will target
(P6: `|ΔAP| < 1.5` and `|ΔAP^⊥| > 2.5`). That is not a ranking flip in the sense C2
established — a *corrected* measurement of the same quantity reversing an order — it is two
different metrics disagreeing, which is the null hypothesis, not the finding. The paper's own
§4 says "We never claim `AP^⊥` is 'the true score'", and its thesis sentence says "the
ranking is not the ranking mAP reports." Those two sentences cannot both stand.

The standard to be held to here is **C10** (On Calibration of Object Detectors, ECCV 2024),
which produced a genuine flip: it fixed a broken protocol, re-measured **the same quantity**,
and cheap post-hoc calibrators overtook the train-time SOTA. That is a flip. Two different
metrics disagreeing is not. And the proceedings sweep found **no paper at CVPR/ICCV/ECCV/
NeurIPS in window that puts confidence intervals on a leaderboard ranking at all** — so team 08
has no methodological precedent to hide behind and no excuse for omitting one. C12 (ECCV 2024)
is the nearest in-venue template for the statistics and should be cited.

Compounding this: every `τ̂` is measured against **interpolated** ground truth. DSEC-Det's
inter-frame boxes are linear interpolation of QDTrack outputs on 20 Hz RGB; a linearly
interpolated track has **zero acceleration by construction**, so the tangent `û` is exact
but the GT *position* is systematically wrong precisely when acceleration matters, which is
the fast-motion regime the paper is about. `τ̂` is therefore an estimate of (method latency −
annotator latency) taken against a constant-velocity model. The paper acknowledges this as
Death 3 and proposes a (dataset, method) variance decomposition, which is the right
instrument — but the decomposition is only identifiable if methods on the same dataset have
*different* declared windows, and RVT and S5-ViT both use `dt=50 ms` on the same
preprocessed tarballs. On Gen1 and 1 Mpx, the method-level component may be unidentifiable
by construction.

**On the RVT pre-registration question, which the brief asks me to settle.** Team 08's C3
predicts `τ̂ ∈ [−35, −10] ms` for RVT from the released config before measuring, and the
machine record (`experiments/e02`) confirms the config: `stacked_histogram_dt=50_nbins=10`,
`ev_repr_timestamps_us_end` counted backwards from label timestamps, hence a uniform-weight
centroid at `t − 25 ms`.

*It defuses one charge and not the other, and the team should be told which.*

- **What it genuinely defuses: estimator validity.** Predicting a number from someone else's
  config and then recovering it is an injection–recovery test with a real injector. It shows
  `δ̂ = e_∥/‖v*‖` is measuring a physical quantity rather than fitting label noise. That is
  worth having and it is the same logic as C4. Keep it.
- **What it does not defuse, and this is decisive.** (i) The prediction is *arithmetic on a
  config*, not a claim about the world — the brief states it is derivable "before any
  measurement", and `experiments/e02` explicitly warns that "'information centroid at
  `t − 25 ms`' assumes the ten bins contribute equally. Whether the trained network actually
  weights them uniformly is exactly the empirical question, and this note does not answer
  it. The 25 ms figure is the uniform-weight reference point, **not a prediction of the
  network's behaviour**." Team 08's §"Why it is universal" states the opposite — "That is a
  **prediction**, not a hypothesis" — which overstates the verified record on this machine.
  (ii) The prediction has an escape hatch on **both** sides: a hit is explained by uniform
  bin weighting, a miss ("τ̂ = −8 ms") is explained by the network weighting late bins more.
  A prediction that cannot be wrong is not a pre-registration. (iii) Most importantly, the
  self-serving charge does not attach to `τ̂` at all — it attaches to `AP^⊥` and the flip.
  You cannot pre-register your way out of a metric whose *definition* forgives the error you
  want forgiven. Pre-registering `τ̂` and then claiming it licenses `AP^⊥` is a bait-and-switch
  a good reviewer will catch.

The fix is to make the pre-registration *discriminative* rather than confirmatory: predict
`τ̂` for methods with **different** declared windows (RVT `dt=50 ms` vs an E-RAFT MVSEC 20 Hz
vs 45 Hz pair vs a constant-count representation whose `w_P` is a random variable) and show
`τ̂` tracks the declared width across methods. A slope-1 line of measured-vs-declared latency
across five architectures is evidence; recovering −25 ms once is arithmetic.

**Factual errors.**
- *§"Why it is universal", last paragraph:* "That is a **prediction**, not a hypothesis."
  Correction per `experiments/e02`: it is a uniform-weight reference point; the bin weighting
  of the trained network is unmeasured.
- *§E2:* "contamination would *reduce* systematic timing bias, so our estimates are
  conservative." Asserted, not argued. Training on the sequences you then measure latency on
  lets the model absorb the interpolation prior, which shrinks `e_∥` and biases `τ̂` toward
  zero — conservative for the *magnitude* claim, but **not** for the ranking-flip claim,
  which is the one they actually make. Correction: restrict the flip claim to data with
  held-out GT, or state the direction of the bias on the flip explicitly.
- *§"Why it is universal" table and §E3:* DSEC-Detection is presented alongside the
  conference-published benchmarks, sourced to "Gehrig & Scaramuzza, *Nature* 2024." That is
  correct as written, but the proceedings sweep confirms **DSEC-Det has no CVPR/ICCV/ECCV/
  NeurIPS paper**; teams 01, 04 and 07 who refer to "DSEC-Det" as a CVPR-line benchmark should
  correct the attribution. Team 08 gets this right and should keep it right.
- *§P3 / C1:* the isotropic null is stated as `R ≈ 0.5` under isotropic error, which is right
  for `E[cos²θ]` in 2D, but `R = (AP^⊥ − AP)/(AP^iso − AP)` is a ratio of AP *differences*,
  not of squared error components, and does not inherit the 0.5 chance value analytically.
  The chance value of `R` must be simulated, not asserted.

**Claims exceeding evidence.**
- Thesis: "**the ranking is not the ranking mAP reports**" — contradicted by their own §4
  ("We never claim `AP^⊥` is 'the true score'").
- P3: "**Anisotropy R ≥ 0.75 for every method**" — "every method" over a pool that does not
  yet exist.
- §"The already-published table that proves the point exists": "A ~20 mAP gap that is purely
  a timing gap". The Ev-3DOD online/offline gap (53.61 → 33.32) is consistent with a timing
  gap but is not shown to be *purely* one; that is the paper's hypothesis, quoted as a fact
  in its own motivation.

**Experiment a hostile reviewer will demand.** Bootstrap. Every flip claim needs a
sequence-level bootstrap CI on `ΔAP` and `ΔAP^⊥` and an explicit statement of how many
resamples reverse the order. With 15 checkpoints across 4 datasets there are ~100 orderable
pairs and a multiple-comparisons problem the paper does not mention: at α = 0.05 you expect
five spurious flips by chance. **Absence is fatal** — a ranking flip reported without a CI
and without a correction for the number of pairs examined is the single most reliable way to
get an evaluation paper rejected, and the brief's standing failure mode list names it.

**Required fixes, ranked.**
1. Run E0 first and independently, and be prepared for the paper to *be* E0. If the
   inter-frame GT of DSEC-Det and DSEC-3DOD reproduces from its own interpolation prior to
   > 0.9 IoU, that is the paper — a C2-class benchmark-integrity result on two flagship
   low-latency benchmarks — and the decomposition becomes the supporting act.
2. Bootstrap CIs on every flip, plus a Holm or Benjamini–Hochberg correction over the number
   of pairs tested, plus pre-registration of *which* pairs will be tested before looking.
3. Reconcile the thesis sentence with §4. Either `AP^⊥` is a corrected score (and must be
   defended as one) or the contribution is the triple `(AP, τ̂, AP^⊥)` and the abstract must
   not say the ranking is wrong.
4. Make C3 discriminative: measured `τ̂` vs declared `w_P` across ≥4 methods with genuinely
   different windows, reported as a regression with a slope.
5. Simulate the chance value of `R` rather than asserting 0.5.
6. State, in the main paper, that `τ̂` on DSEC-Det is measured against a zero-acceleration GT
   and bound the resulting bias.

---

### Team 01 — *A Frame Is Not a Timestamp* — **ACCEPT**

**Summary.** The argument is an identifiability proposition: substituting `u = (τ − t0)/T`
into the blur integral removes `t0` and `T` exactly, so a blurred frame determines the path
and the dwell density and *nothing* about the absolute exposure interval or even the
direction of traversal; the dataloader's scalar timestamp is therefore an unfalsifiable
prior. From this they predict a signed, motion-direction-conditioned localisation bias (TSB)
with slope `β = (α_model − α_label)`, claim that a documented cross-dataset "domain gap" is
really a clock-convention gap removable by one scalar, and replace the point state with a
Bézier trajectory on the normalised support plus an estimated support field.

**Strongest reason to accept.** **SIE**. The team proposes to estimate `T̂` from events and
blur, and validate it in milliseconds against DSEC's *published* per-frame exposure
timestamps, which are never shown in training. That is an external referent in exactly the
sense C1–C4 require: a number the community already trusts, produced by the sensor, that the
authors did not define. It is the only metric in these ten ideas that scores a latent
variable against a physical measurement rather than against a convention. It also costs
almost nothing — the machine record shows the files are already downloaded for 18 sequences,
with exposure widths spanning 118 µs to 14 996 µs, a factor of 127. A predicted `T̂` within
15 % across a 127× range would be a genuinely convincing result and it needs no training-set
label of any kind.

Secondarily: `K = 0` **is** the current formulation, so the order ablation is the SOTA
comparison rather than a side experiment. That is the cleanest reduction-to-existing design
in the batch, and it is what C9-style work does when it claims backward compatibility.

**Strongest reason to reject.** Four invented metrics, and three of them (TQ-AUC, SCR, and
the money-plot form of TSB) require ground truth at ~10× the frame rate, which on real data
means FE240hz and nothing else. **Team 09 reports, as a verified finding, that
`fe108.dluticcd.com` refuses connection — "DEAD: do not plan on it."** Team 01 scores that
access risk as "Medium-high … turnaround is unknown and could take weeks"; team 04 names a
different host (`zhangjiqing.com`) and scores it "Medium"; team 02 names the same dead host
and scores it "Medium". Four of the ten teams built their real-data instrument on a dataset
a fifth team reports is unreachable, and none of the four checked. If team 09 is right, team
01's Figure 1b — the paper's declared "money plot" — has no real-data substrate, and the
paper degrades to what the team's own Risk 1 fallback describes: "the regime map + the
protocol + SupportBench + the SIE validation", i.e. a simulator study with one real
validation number. That is a workshop paper.

**Factual errors.**
- *§Fig 1a:* "plot the **left–right exposure-midpoint difference**: prediction ≥ 1 ms on a
  substantial fraction of frames." **Contradicted by data already on this machine.**
  `experiments/e00` measures the left–right mid-exposure difference at a median of 0–72 µs
  with a **maximum of 190 µs** across four sequences, and finds the published
  `image_timestamp` equals the average of the two mid-exposures **to within 1 µs**. The
  prediction is wrong by more than a factor of five at the maximum and by two orders of
  magnitude at the median. The brief also warns explicitly that "an argument resting on
  left/right divergence rests on the smaller effect and should be marked down." Correction:
  delete this panel; the argument must rest on the *width* of the window (118 µs → 14 996 µs,
  a factor of 127), which is the larger effect by two orders of magnitude.
- *§Fig 1a:* "`T` spans more than an order of magnitude within a single sequence under
  auto-exposure (~1 ms daylight to **>15 ms** night)." Measured: the night sequences are
  pinned at exactly 14 996 µs, the auto-exposure ceiling. `> 15 ms` never occurs. The
  within-sequence span is 12.5× (interlaken_00_d, 337 → 4207 µs), which does support "more
  than an order of magnitude" — but the stated endpoint is wrong and a reviewer checking the
  file will find it.
- *§Why this is not closest work:* "Dense Continuous-Time Optical Flow from Event Cameras |
  TPAMI 2024 (ECCV 2022) | … **Event-only**, so the frame-support problem never arises." This
  is wrong. Team 08 documents (§E2) that the same work releases both an event-only checkpoint
  `E_LU4_BD2.ckpt` and an **event+image** checkpoint `E_I_LU4_BD2.ckpt` from the identical
  architecture and recipe, and the ECCV 2022 title is "Dense Continuous-Time Optical Flow
  from Events **and Frames**." The row's entire differentiator ("we are the frame-side half
  of that problem") rests on a false premise. Correction: reposition against the E+I variant,
  which is a much harder neighbour.
- *§Metrics:* `SCR` (Support Coverage Ratio) collides with team 03's `SCR` (Support-Conditioned
  Risk spread) in this same pool.

**Claims exceeding evidence.**
- "**The slope is essentially independent of the network** (YOLOX-S vs. a transformer detector
  vs. a tracker) — this is the signature that it is a property of the formulation." Stated as
  a committed prediction over three unrun architectures. If it fails for one, the "property
  of the formulation" framing collapses to "property of these two backbones."
- "this removes **≥ 40 %** of the excess error at `d > 15 px`" — the free-lunch test, with a
  number attached, for an experiment on a dataset that may not be obtainable.
- "the transfer degradation, conditioned on `d`, is predicted by `(α_A − α_B)·d` **to within
  25 %**, and largely disappears after the free-lunch shift." This is the paper's most
  quotable claim ("a documented domain gap is a clock-convention gap") and it is entirely
  unmeasured.

**Experiment a hostile reviewer will demand.** The null: measure `β` for a *frame-only*
detector and an *event-only* detector separately. If a frame-only model shows the same signed
along-motion slope, the phenomenon is motion blur, not temporal support, and the entire
event–RGB framing is decorative. Team 04 identifies exactly this control as "the single most
important control in the paper" and team 01 does not have it. **Absence is fatal.**

**Required fixes, ranked.**
1. **Verify FE240hz availability on day zero**, before any other work, and if team 09 is
   right, restructure the paper around SIE + DSEC + a simulator and say so in the abstract
   rather than being discovered in review.
2. Delete the left–right divergence panel and rebuild Fig 1a on exposure *width*, citing the
   measured 118–14 996 µs range.
3. Add the frame-only / event-only null for `β`.
4. Correct the BFlow row (E+I checkpoint exists) and reposition.
5. Cut the invented metric count from four to two. TSB and SIE carry the paper; TQ-AUC and
   SCR are the same quantity twice and both are simulator-bound. Reviewers count invented
   metrics, and four is where it starts to read as axis-shopping.
6. Fix the "> 15 ms" figure to the measured 14 996 µs ceiling.

---

### Team 02 — *Exposure-Occupancy Measures as the Prediction Target* — **BORDERLINE**

*Structural problem, one sentence: the paper's indictment is a leaderboard reordering
measured over five trackers, which is too few methods for any statement about ranking
stability to survive a bootstrap.*

**Summary.** The claim is that a frame label is an unstated functional `A` of the state's
occupancy measure over the exposure, that the conventions in active use (`A_mid`, `A_mean`,
`A_mode`, `A_hull`, `A_core`) disagree systematically, and that the field indexes difficulty
by the wrong variable — label ill-posedness is driven by intra-exposure *acceleration*, not
blur magnitude, so that at constant velocity all conventions agree exactly no matter how
severe the blur. The prediction target becomes the measure itself: a support curve plus a
dwell density, with the annotation convention as a latent fitted by EM and split-conformal
calibration giving convention-marginal coverage on point-labelled benchmarks.

**Strongest reason to accept.** This is the most metric-literate submission in the batch and
the only one that designs for *adoptability*. `CMC@α` is computable on any point-labelled
dataset with no sub-exposure GT, which is what would let other people use it. `CI-AP` is
reported as a curve against SetEff and **degenerates to standard AP as `|Ŝ| → 0`**, so every
existing published number is locatable on the new axis — the reduction-to-existing property
the brief asks about, designed in rather than retrofitted. And `SetEff` is reported as a
frontier with `CMC` rather than as a number, which is the correct answer to "coverage is
trivial to buy." Prediction 1 (severe blur with zero acceleration ⇒ well-posed label,
`D < 0.05`) is a **predicted null**, and predicted nulls are the strongest evidence a
measurement is not fishing.

**Strongest reason to reject.** Prediction 4: "Kendall `τ` over the five-method ranking drops
below 0.6 on the top `ν` decile." With n = 5 there are 10 pairs; τ = 0.6 means two discordant
pairs, i.e. one or two swaps. Under a random permutation of five items, `P(τ ≤ 0.6)` is large
— this is not a rare event. Worse, it is being computed on a *decile* of one dataset, so the
effective sample is a few hundred frames, and no bootstrap is proposed anywhere. Prediction 3
compounds it: "the RSR change of a single fixed model under a convention switch is 10–20
points, whereas the RSR spread *between* the five published trackers is 3–8 points." Those are
two different quantities (a within-model perturbation vs a between-model spread) presented as
comparable, and the comparison is the paper's headline indictment.

**Factual errors.**
- *§Why this is not closest work:* "Exposure Trajectory Recovery from Motion Blur (Zhang et
  al.) | **TPAMI 2021**." Team 01 lists the same paper as **TPAMI 2022**; team 03 lists it as
  **TIP 2021**. Three teams, three venues, one paper. At most one is right; all three should
  verify before submission.
- *§Datasets:* FE108 access is scored "**Medium.** Gated by an application form
  (fe108.dluticcd.com)". Team 09 reports that host refuses connection. If so, "Medium" is
  wrong and EVIMO2 (200 Hz, i.e. 5 ms sampling) becomes the only real substrate — which for a
  paper about intra-exposure structure at the millisecond scale is marginal, as team 07
  concedes for the same dataset ("200 Hz GT is only 5 ms — barely better than the problem").

**Claims exceeding evidence.**
- "**The convention moves the score more than the method does.**" The paper's thesis sentence,
  resting on n = 5 and no CI.
- "**A quarter of the remaining headroom on this benchmark is definitional, not learnable.**"
  From an oracle floor `e*` computed under an assumed convention set `𝒜` that the authors
  chose. Enlarge `𝒜` and the floor rises; shrink it and the floor vanishes. The result is a
  function of a design choice presented as a property of the benchmark.

**Experiment a hostile reviewer will demand.** Sensitivity of every headline number to the
choice of `𝒜`. `CS = 1 − min_{A,A'} IoU(A[y], A'[y])` is a minimum over a set the authors
define; adding `A_hull` (the union box) to `𝒜` can make `CS` arbitrarily large on any fast
object, and dropping it can make it near-zero. Without a `𝒜`-sensitivity table, `CS` is a
knob, not a measurement. **Absence is fatal** for `CS`; the conformal half survives it.

**Required fixes, ranked.** (1) Bootstrap everything and drop the n = 5 Kendall τ as an
indictment — use it as a descriptive statistic only. (2) `𝒜`-sensitivity table for `CS` and
`e*`. (3) Verify FE108 host; plan on EVIMO2 and state the 5 ms sampling limit up front.
(4) Keep the `CMC`–`SetEff` frontier and `CI-AP` as the contribution — they are adoptable and
they reduce to existing practice, which is the strongest thing here. (5) Report the recovered
`π` with a CI; "we read a benchmark's unwritten annotation convention off its labels" is a
wonderful sentence and needs an uncertainty attached or it will be dismissed as overfitting.

---

### Team 05 — *No Offset Can Fix a Width* — **BORDERLINE**

*Structural problem, one sentence: the theory is certainly true and may be entirely
irrelevant, because on every real dataset it can reach, the blur extent `b = vT` may sit
below the onset threshold the theory itself derives.*

**Summary.** Frame and event channels are integrals of one latent against two different
temporal measures; a time shift is a unit-modulus linear-phase multiplier in Fourier and
therefore cannot correct a modulus mismatch with exact zeros. Hence no offset — learned,
per-pixel, or hardware — reduces the cross-modal residual below a floor (SMF), the best-fit
offset is a scene- and speed-dependent quantity masquerading as a rig constant (T2), and a
speed sweep makes the kernel pair identifiable (T3).

**Strongest reason to accept.** `OBD = dδ̂/db` is the cleanest invented metric in the batch
after team 06's `SFR`, for one reason: **it has an analytic null that the field itself
supplies.** A rig constant must have zero drift. That is not the authors' definition; it is
the definition every calibration paper in the field uses when it reports `t_d ± σ`. So the
measurement "on a hardware-synchronised rig, the best-fit offset drifts by ≥ 3 ms as the
motion speeds up" is falsifiable against a standard the community already holds, and it
requires **no labels, no GT, and no simulator** on the real-data half. The load-bearing claim
also runs on CPU with no training, which is the correct place to put a load-bearing claim.

**Strongest reason to reject.** Prediction 1 states the onset condition: nothing happens
below `b ≈ 1 px`. `experiments/e00` gives measured DSEC daytime exposures with medians of
299–1871 µs. At 50 km/h and typical DSEC image scales, intra-exposure ego-displacement in
those sequences is well under a pixel for most of the image, and `experiments/e01` explicitly
warns that its own measurement — 1.10 threshold crossings per firing pixel — "is **not** a
statement about pixel displacement" and that "displacement in pixels needs either the DSEC
optical-flow ground truth or ego-motion from `lidar_imu.zip`, and neither has been
downloaded." So the paper's real-data relevance is currently **unmeasured on this machine**,
and the team's own Death-2 fallback ("measure the actual joint distribution of `(T, v)`
across all DSEC sequences *first*") is the right instinct. The six night sequences at
14 996 µs are the only regime where the theory bites, and they are night driving, where flow
GT is worst.

**Factual errors.** None found that contradict the machine record. The claim "DSEC's
documented `t_offset` … must be added to the timestamps of the events" is consistent with the
verified finding that events and frames share one clock with no calibration step. Note the
team writes "DSEC daytime driving may run exposures of 0.1–1 ms"; the measured range is
118–4207 µs across daytime sequences, so 0.1–1 ms understates the upper end by ~4×, in the
team's own favour — flag it and correct it rather than leave a reviewer to find that the
honest number helps them.

**Claims exceeding evidence.** "**Calibrating faster makes your calibration worse**, which is
the opposite of every calibration protocol's assumption." A strong, quotable, entirely
unmeasured claim about a literature (EF-Calib, eKalibr) whose protocols the team has not run.
Also: "The CVPR 2026 proceedings contain 60+ event papers and **none** is about event–frame
temporal support or exposure-aware calibration" — an exhaustive negative over a full
proceedings, made by a team that reported its search budget exhausted.

**Experiment a hostile reviewer will demand.** The `(T, v)` joint distribution over all DSEC
sequences, with `v` from the shipped optical-flow GT or from `lidar_imu.zip` ego-motion,
producing a histogram of `b = vT` in pixels, with the theory's `b ≥ 2 px` onset drawn on it.
**Absence is fatal** — it is the single number that decides whether this is a CVPR paper or a
correct footnote, it needs no GPU, and the team has already scheduled it. It should be
Figure 1.

**Required fixes, ranked.** (1) The `b` histogram on real DSEC, first, before anything else.
(2) Run ablation 1 (global shutter, τ = 0, noiseless, ideal thresholding) as scheduled — it is
the one row that answers "mundane cause" in a single line. (3) Withdraw the exhaustive
negative over CVPR 2026 or cite the enumeration. (4) Correct the daytime exposure range to
the measured 118–4207 µs. (5) If the histogram says `b < 1 px` everywhere reachable, take the
team's own step (iv) — retreat to OBD on the night sequences and carry the notch evidence in
simulation, explicitly labelled — rather than stretching the claim.

---

### Team 10 — *Fusion Is Ill-Typed* — **BORDERLINE**

*Structural problem, one sentence: the headline diagnostic OSAM has a predicted curve that
is a geometric identity, so it will confirm on every spatially local architecture regardless
of whether that architecture is doing anything wrong.*

**Summary.** A frame is a positive interval-mean of irradiance (mass 1, linear domain); an
event bin is a zero-mass signed boundary difference of log-irradiance. These live in disjoint
sets of measures, so no shift, scale or warp maps one to the other — alignment is orthogonal
to the defect. From this: a support type system with legality rules for mixing, an
identifiability null space, and the prediction that existing fusion models extract *less*
from events as scene speed rises.

**Strongest reason to accept.** The support-blind pair. Take a per-pixel path and its time
reversal on one bin: identical endpoints ⇒ identical polarity-sum voxel grids; identical
integral ⇒ identical blurred frames; different answer at any asymmetric `t*`. Every published
model maps the pair to one input and emits one confident answer for two different worlds.
This is a **construction plus a theorem, not a benchmark hope** — it cannot fail, it needs no
download, and it produces an honest calibration result (a well-typed model should be at
chance *and say so*). Team 02 independently proposes the same construction, which is
corroboration rather than collision. It is the only experiment in the ten ideas that is
guaranteed to produce a publishable figure.

**Strongest reason to reject.** `OSAM(s) ≈ 1 − r/(r+s)`, where `r` is the fusion block's
spatial mixing radius and `s` is displacement during exposure. That is not a prediction about
whether the model is misrouting — it is arithmetic about how much of a displacement-`s`
trajectory falls outside a radius-`r` neighbourhood. Any architecture with a local mixing
radius, correct or not, satisfies it. So the "expected curve" is confirmed by construction,
and the paper's mechanism panel measures the ratio `s/r`, which is fixed by the architecture
and the scene, not by whether anything is broken. Worse, the causal tube is "dilated by the
calibration/flow error budget", which is a free parameter that sets OSAM's absolute level.

And then the statistics. `SII`'s "scientific claim is the *cross-model correlation*: models
with larger type distance at their first mixing site degrade faster with `s` (target
`ρ > 0.7` over **≥ 5 models**)." With n = 5, a Pearson r of 0.7 gives t ≈ 1.70 on 3 df,
**p ≈ 0.19**. That is not a result at any conventional threshold, and the paper's target
value is *already* below significance before any noise is added. The Panel-A peak-location
correlation (`ρ > 0.7` over four models) is worse.

**Factual errors.** *§Panel B:* "from `0.12 ± 0.03` at `s = 0.5 px` to `0.83 ± 0.05` at
`s = 12 px`" — error bars are quoted on quantities from an experiment that has not been run.
Whatever the intent, this reads as fabricated precision and a reviewer will say so.
Correction: state predictions as inequalities or ranges, never as mean ± SD.

**Claims exceeding evidence.** "Across ≥ 4 published models: EU at the top flow decile is at
most **60 %** of EU at the median decile"; "Peak location correlates with the block's mixing
radius, `ρ > 0.7` over models"; "OSAM falls by `< 0.08` absolute" after fine-tuning. All
point predictions with two significant figures, none measured, all over n ≤ 6.

**Experiment a hostile reviewer will demand.** A tube-dilation sensitivity sweep for OSAM,
plus a *null architecture*: a fusion block that is provably well-typed by construction (e.g.
render both branches to the frame's type before mixing, per their own R3/R4) must show OSAM
at the tube-error floor. Without a model that scores *well* on OSAM by construction, the
metric has no calibrated zero. **Absence is fatal for Panel B**; Panel A and the support-blind
pairs survive.

**Required fixes, ranked.** (1) Lead with the support-blind pair, not with OSAM — it is the
part that cannot fail. (2) Replace `SII`'s cross-model correlation with a within-model
manipulation (change one block's type distance, hold everything else) so n is the number of
*ablations*, not the number of *papers*. (3) OSAM tube-dilation sensitivity plus a well-typed
null. (4) Delete all `± σ` from unmeasured predictions. (5) Report EU(s) with per-sequence
bootstrap CIs; modality-dropout deltas of 0.3 mAP are inside the noise of most detection
evaluations.

---

### Team 04 — *When Is Your Prediction?* — **BORDERLINE**

*Structural problem, one sentence: `σ_τ > 0` is declared the kill shot but has no null
model, and it is produced for free by GT interpolation noise or by a flat argmin.*

**Summary.** A fused predictor trained to output the state "at `t`" actually outputs the
state at the evidence-weighted time centroid, a quantity that moves with exposure, event
window, speed and texture and that **differs between regions of one frame**. The primitive is
`τ̂ = argmin_t d(ŷ, y*(t))` — "at what time would this prediction have been right?" — with
derived statistics `b` (temporal bias) and `σ_τ` (within-frame dispersion), and `TEF`, the
fraction of reported error explained by timing.

**Strongest reason to accept.** `τ̂` is embarrassingly simple, requires only a continuous GT
trajectory and released checkpoints, and asks a question the field's metrics cannot pose.
The collapse plot — pool ~2000 condition cells across four independent variables and show
they fall on one line of slope 1 — is the right shape of evidence: a collapse across
independent sweeps is much harder to fake than a single curve. And the team pre-specifies the
null result in §4.4, including the anti-diagonal blur control (constant `v·T_exp`, varying
`τ̂`), which is the correct way to separate the new axis from the field's existing confound.
That §4.4 exists at all puts this above most of the batch.

**Strongest reason to reject.** `σ_τ` is a standard deviation of an argmin. It is positive
whenever the argmin is noisy, and the paper's own §4.4 admits the argmin is *flat* — hence
unidentifiable — under constant-velocity motion, which is most of most datasets. So a nonzero
`σ_τ` is the expected outcome under the null hypothesis "there is one global clock plus
estimation noise", and the paper offers no null distribution for it. The proposed real-data
substrate makes this worse: at 240 Hz the GT sampling interval is 4.17 ms, and the effect to
be resolved is 2–5 ms. The team concedes this ("the effect we need to resolve … is comparable
to the GT sampling interval"). Resolving a 2 ms dispersion against a 4.17 ms sampling grid,
after spline interpolation, on a dataset that team 09 reports is offline, is not a measurement
— it is a hope. `σ_τ` needs a permutation null: shuffle predictions across objects within a
frame and recompute `σ_τ`; if the shuffled value is comparable, there is nothing there.

**Factual errors.** *§Why this is not closest work, FAOD row:* "reports success as a *flat*
accuracy curve under an 80× frequency mismatch (**1.2 mAP** drop where baselines drop ~10)."
Team 07 reports the same result as "**a 3-point mAP drop**" and team 09 as "degrading only
**~3 points**." Two of the three are wrong about a number all three use as load-bearing
evidence. Correction: read it from the paper; whichever team is right, this pool currently
contains a factual contradiction about its most-cited neighbour.
*§Datasets:* FE240hz hosted at `zhangjiqing.com`, risk "Medium" — team 09 reports the FE108
host dead; the two claims name different hosts and cannot both be checked against each other
as written.

**Claims exceeding evidence.** "`TEF = 0.9` means **90 % of what the community reports as a
fast-motion localization failure is a clock failure**" — offered as an interpretation of a
number not yet measured, in the section that defines the number. "the network was **told** the
right time and still cannot deliver it" — asserted from a first-order argument about the Bayes
predictor under an assumed evidence-weight density `w(t)` that is never estimated.

**Experiment a hostile reviewer will demand.** The frame-only / event-only control for `σ_τ`,
which the team correctly identifies as "the single most important control in the paper", plus
a permutation null for `σ_τ`. **Absence of either is fatal.**

**Required fixes, ranked.** (1) Permutation and shuffle nulls for `σ_τ`, reported alongside
every measured value. (2) The single-modality control, in the main paper. (3) Verify FE240hz
availability; if dead, the paper is a simulator study and must say so in the abstract.
(4) Reconcile the FAOD number with teams 07 and 09. (5) Cut the invented-metric count —
`τ̂`, `b`, `σ_τ`, `TEF`, `sAP-τ`, identifiability margin, collapse slope: seven is too many,
and `sAP-τ` in particular is the one that reads as circular ("being right at the wrong time
is a false positive" is true by the definition they just wrote).

---

### Team 09 — *Change-Time: Per-Pixel Clocks* — **REJECT**

**Summary.** The assumption killed is that one global time axis in seconds exists; the
replacement is a per-pixel clock `τ(x,t) = C·N(x,t)` counting accumulated change, in which
the event stream is a complete observation up to `O(C)` and any function of the representation
is *exactly* invariant to monotone time reparameterisation. The frame's temporal support
becomes a measured per-pixel width `W(x) = C·N_exp(x)`, zero on static pixels. The failure
phenomenon is that any partitioning rule emitting a duration in seconds must clamp it and
therefore has bounded speed dynamic range — predicted at 25:1 for ASTW from its published
`Δt_min = 10 ms`, `Δt_max = 250 ms`.

**The fatal flaw, named.** Two of the three headline metrics are **analytically determined by
the construction and cannot come out any other way.**

- `RIG` (Reparameterisation Invariance Gap): "Ours: exactly 0 on the invariant branch." The
  representation is *defined* as a function of `N(x,t)` and polarity sequences, both invariant
  to monotone warps by Proposition (2). `RIG = 0` is a restatement of the definition. The team
  concedes this — "a unit test, not a result" — and then lists it as invented metric #1 and
  as prediction P7.
- `SSI` (Support-Separability Index): `R²` of iso-error contours against `k·T` versus against
  `T` alone, with the prediction "ours `R² ≤ 0.3` against `k·T`, `≥ 0.9` against `T` alone."
  But `W(x) = C·N_exp(x)` measures `k·T` and the model divides it out by construction. The
  metric asks whether the method is invariant to a quantity the method is built to divide out.
  It is presented as "**the frame-side headline metric**" and it is a tautology.
- `CDR` (Clock Dynamic Range): "For any clamped rule this should equal `Δt_max/Δt_min`; for
  ours, unbounded." The competitor's value is read off the competitor's hyper-parameter table
  and the authors' value is infinite by definition. There is no measurement here either.
- `ORL` (Onset Response Latency): "Ours: **0 by construction**." Stated as such.

Four invented metrics whose values for the proposed method are known before any experiment.
That is the textbook form of the brief's standing failure mode: *a metric invented by the
authors on which, unsurprisingly, the authors win.* The team's own hedge — "We may not beat
ASTW's 50.6 on GEN1. We must win on CDR/HSP/ORL/RIG/SSI at *matched* mAP" — states the problem
precisely: the paper plans to tie on the community's metric and win on five metrics whose
outcome is fixed by the construction. No AC discussion survives that.

Is it fatal to the idea or to this execution? **To this execution.** The idea has one
measurement that is not tautological: `SWC` (Support-Width Calibration — correlation of the
measured `W(x)` with true per-pixel blur severity against a sharp reference), which has an
external referent and could fail. And `HSP`/P3 (does ASTW's slow-object error rise past
`ρ ≈ 25`?) is a genuine falsifiable prediction about *someone else's* method, derived from
their published constants. A paper built on `SWC` + P3, with `RIG` demoted to a footnote and
`SSI` deleted, would be reviewable. As written it is not.

**Factual errors.** None found against the machine record; the team's dataset verification is
the most careful in the batch (per-sequence DSEC sizes, N-Caltech licence, DVS-Voltmeter
dependency count) and its report that `fe108.dluticcd.com` refuses connection is, if correct,
the single most consequential piece of information in the whole round — it invalidates the
real-data plan of teams 01, 02, 04 and 07. It also correctly flags TIDES's finding that
frame-derived simulators suffer timestamp batching that *worsens under rapid motion*, which is
the regime every team here measures; that objection applies to teams 01, 02, 03, 04, 05, 07
and 10 as well and none of them names it.

**Claims exceeding evidence.** "Ours is **flat across the whole sweep**" (P4, `≤ +5 %`
throughout). "`RIG` … **exactly 0**, to float precision." "two independently verified empty
intersections: `"temporal support"` + `"event camera"` returns **zero** arXiv abstracts" — an
abstract-field keyword search returning zero is very weak evidence of novelty for a concept
the field expresses in other words (ASTW, REFID, EBFI-BE, BRENet all address it), and the team
half-concedes this.

**Experiment a hostile reviewer will demand.** `SWC` on real data with a sharp reference, and
P3 with ASTW's clamp swept — which the team schedules. **Absence of `SWC` is fatal**, because
it is the only proposed number that could come out badly.

**Required fixes.** (1) Delete `SSI`; it cannot fail. (2) Demote `RIG` and `ORL` to stated
properties of the construction in the method section, not to the metrics table. (3) Rebuild
the evaluation around `SWC` and around P3-on-ASTW, both of which are falsifiable.
(4) Report matched-mAP comparisons as the headline, since that is the honest position.
(5) Publish the FE108 host finding somewhere the other teams can see it.

---

### Team 07 — *Chronofields: Predicting When Instead of What* — **REJECT**

**Summary.** Invert the map: instead of `time → state`, predict `state → time` — a
distribution over when a queried condition held, with an explicit `∅` atom for "never within
the window." Events enter the likelihood as exact (uncensored) time observations, frames as
interval-censored ones, which is textbook survival analysis imported into event vision. The
frame's effective time is biased from the midpoint by `Δt ≈ a·T²/(24·v̄)` and becomes
multi-valued under an intra-exposure direction reversal.

**The fatal flaw, named.** Of five invented metrics, **three cannot be scored for any existing
method by construction**, and the paper says so.

- `TCE` (Temporal Calibration Error): "*Invented, and **no existing method can even be scored
  on it***: they emit no distribution over time."
- `CMR` (Censoring-Mass Recall): "Existing methods must hallucinate a state at every `t` and
  **cannot compete by construction**; we report it as an ability, not a win."
- `CTE` in its distributional form: baselines can only be scored after being wrapped in an
  extrapolator the authors write.

So the comparison table has three columns where the baselines are the authors' own
constructions, one column (`mAP`) reported "*in order to show it is flat*", and one genuine
column (`SFR`, the sub-frame resolution ratio, which does have a real null at `SFR ≤ 1`). A
reviewer reading that table sees a method compared against strawmen the method's authors
defined. The team's self-score names this exactly — "the metric story reads from a distance
exactly like *inventing a metric you win on*" — and scores its own reviewer-proofness at 5/10,
the lowest in the batch. I agree with the team's own assessment and I am acting on it.

Two aggravating factors. First, the paper's own declared kill condition is the
reconstruct-then-detect baseline (Time Lens → 1000 fps → RVT), and the team pre-commits that
"if Time Lens → RVT reaches P95 CTE within 15 % of ours at equal-or-lower compute … the
accuracy claim is dead." That baseline is strong, cheap for the community to run, and the
fallbacks if it wins are precisely the three unscorable metrics. Second, the F1 proposition is
overstated: "mAP is **invariant to a group of temporal shifts**" holds only for
`δ·v_max < ε` where `ε` is the IoU matching tolerance — i.e. for shifts small enough not to
move a box out of tolerance. That is a bounded, quantified insensitivity, not a null space,
and the paper then uses it as though mAP were blind to time in general.

Fatal to the idea or to this execution? **To this execution.** The C1 anchor — predict when
each pixel next crosses a contrast threshold, supervised by held-out *real* events at
microsecond resolution, no labels, no simulator, no annotator — is genuinely clever and is
real ground truth by construction. A paper built on C1 plus the reconstruct-then-detect
head-to-head, with `TCE`/`CMR` reported as *capabilities* in a separate section rather than as
comparison columns, is reviewable. But then it needs a strong trivial baseline for C1 (next
crossing time is largely predictable from the local event rate), and the paper does not
propose one.

**Factual errors.** *§F1:* "FAOD reports only a **3-point** mAP drop under an 80×
event–RGB frequency mismatch" — team 04 reports the same number as **1.2 mAP**. See the
cross-cutting list. *§Datasets:* HS-ERGB/BS-ERGB size "unverified — rate-limited"; team 06
reports, with specifics, that BS-ERGB's download page now renders navigation only, with no
links or forms and no mirror, and that it belongs to Time Lens++ (CVPR 2022), not EVDI. Team 07
lists BS-ERGB as tier-2 real-event validation and as the arbiter of its own kill criterion.

**Claims exceeding evidence.** "`Δt ≈ −8.3 ms`, i.e. **42 % of the exposure** — larger than a
whole inter-frame interval at 50 fps" — computed at `a = −2 px/ms²`, `T = 20 ms`, `v̄ = 4 px/ms`,
a hand-picked operating point, and the very formula diverges as `v̄ → 0`, so the number can be
made arbitrarily large by choosing the denominator. "**94 % of contacts fall strictly between
frames**" at 30 fps for a 2 ms contact — arithmetically fine, but stated as a dataset fact
without a dataset.

**Experiment a hostile reviewer will demand.** The reconstruct-then-detect head-to-head at
matched compute, which the team already names as the kill test, **and** a rate-only baseline
for C1. **Absence of either is fatal.**

**Required fixes.** (1) Run the kill test first, as planned, and abide by the pre-committed
criterion. (2) Move `TCE`/`CMR` out of the comparison table into a capability section.
(3) Add a local-event-rate baseline for C1. (4) Quantify the mAP-invariance proposition
rather than stating it as a group property. (5) Reconcile the FAOD number. (6) Drop BS-ERGB
from the plan per team 06's finding.

---

### Team 03 — *Temporal Support Fields* — **REJECT**

**Summary.** Predict, per pixel and per modality branch, a sub-probability measure on the
time axis stating over which instants and with how much total evidence the observation is a
statement about the scene, then make fusion an *overlap of supports* rather than a similarity
of features. The mass channel (sub-probability, not probability) is load-bearing because it
makes abstention — "there is no valid observation of this pixel at the requested time" — a
representable output.

**The fatal flaw, named.** The independent variable of the paper's one plot does not exist on
real data. `O*(x) = Σ_k min(s^{F*}_{x,k}, s^{E*}_{x,k})` is defined as the total-variation
intersection between the frame pixel's *occupancy measure* and the event pixel's inter-event
measure, "both computed exactly by the simulator." The event side is genuinely free on real
data — inter-event intervals are in the raw stream, and the team is right to lean on that.
The **frame side is not**: the occupancy-weighted measure on the exposure, i.e. the
sub-interval during which the scene point that dominates pixel `x` actually projected into
`x`, has no ground truth in any public event–frame dataset. It is definable only where you
control the renderer.

So the paper's argument — "the colours are shuffled, blur extent does not order the points,
while the curve falls off a cliff in `O*`" — is a statement about how a simulator's own
bookkeeping correlates with error in that simulator. The matched-pair construction (constant
velocity vs dwell-then-dash, matched blur extent, matched event count, `O*` = 0.8 vs 0.15) is
elegant and it is entirely a construction: the two conditions differ in exactly the variable
the authors defined, so of course they differ in it. Prediction 2 — the partial-correlation
result `|ρ(err, O* | d, N_ev)| ≥ 0.6` while `|ρ(err, d | O*, N_ev)| ≤ 0.25` — is the paper's
strongest form and it is computable **only** where `O*` is known, i.e. never on real data.
The BS-ERGB "measured occupancy windows from the high-speed strand" is the one proposed
escape, and team 06 reports BS-ERGB's download path has gone dark.

Of the six invented metrics, `SOA` and `RSE` require simulator GT; `SID` requires matched
pairs, i.e. a simulator; `SCR-spread` and the whole risk-vs-`O*` curve require `O*`; only
`TAB` (risk–coverage AUC ordered by answerable mass, minus the same ordered by softmax
confidence) and `SCE` are computable on real data — and those two are, respectively, an
uncertainty-estimation result and a calibration result, which is exactly the reading
("this is uncertainty estimation with extra steps") the team lists as a certain attack.

Fatal to the idea or to this execution? **To this execution.** The team's own Death-1 fallback
— pivot the axis from *overlap* to *mass*, and make the paper about temporal abstention — is
the right move and is real-data-computable, because staleness (time since last event, exposure
saturation) is readable from the raw stream. That paper is smaller and honest. The paper as
written cannot state its own x-axis on any benchmark.

**Factual errors.** *§Why this is not closest work:* "Exposure Trajectory Recovery from Motion
Blur, Zhang et al., **TIP 2021**" — teams 01 and 02 give TPAMI 2022 and TPAMI 2021 for the same
paper. *§13, ASTW / RTEA cited as CVPR 2026:* I could not verify either (search budget
exhausted, CVF returns 403); team 09 independently cites ASTW as CVPR 2026 with detailed
hyper-parameters, which is corroboration but not verification. Both teams should confirm before
building an argument on a competitor's clamp constants.

**Claims exceeding evidence.** "mean PSNR drops by **≥ 3.5 dB**" between `O*` terciles;
"**≥ 8 mAP** gap between the top and bottom `O*` terciles at matched blur and event count";
"`‖φ(A) − φ(B)‖/‖φ(A)‖ < 3 %` while … **Our support-augmented encoder gives > 30 %**." Every
one is a two-significant-figure prediction on an unrun experiment, and the last is a claim
about a model that does not exist.

**Experiment a hostile reviewer will demand.** Demonstrate `O*` — or any monotone proxy for it
— on a real dataset with no simulator. **Absence is fatal**, and there is currently no proposed
route to it.

**Required fixes.** (1) Either find a real-data estimator for the frame-branch occupancy
support with an external referent, or pivot to the mass/abstention paper now. (2) If pivoting,
lead with `TAB` against a softmax-confidence baseline on real DSEC, which is a real
risk–coverage comparison against a real incumbent. (3) Rename `SCR` (collides with team 01).
(4) Verify ASTW/RTEA venues.

---

## Metric audit

Every invented metric across the ten ideas. **SOUND** = computable by a third party on public
data, with a referent or null the authors did not define. **SOUND BUT UNCOMPUTABLE ON PUBLIC
DATA** = well posed, but requires ground truth no public benchmark has, so it is
simulation-only or authors-only. **RIGGED** = its value for the proposed method is fixed by
its construction, or its null is a free parameter of the authors.

### Team 01

| Metric | Measures | GT needed | Third party? | Verdict |
|---|---|---|---|---|
| **SIE** `\|T̂ − T\|`, `\|t̂0 − t0\|` (ms) | Support-identification error | DSEC's **published** exposure timestamps (already on disk) | **Yes** — files are public, never used in training | **SOUND.** The best-designed metric in the round. External physical referent, 127× dynamic range, zero training cost. |
| **TSB** `β = dE[e_∥]/dd` | Signed along-motion bias per pixel of intra-exposure displacement | GT motion direction + intra-exposure displacement `d` | Partly — needs flow GT for `d`; on DSEC, `d` is not yet measured (see `experiments/e01` caveat) | **SOUND**, conditionally: it has a real null (`β = 0`) and a real control (frame-only vs event-only), but neither is currently in the plan. Add the single-modality null and it is sound. |
| **TQ-AUC / TQ-mAP** | Accuracy vs query offset across the support | GT at 240 Hz–1 kHz | No — FE240hz only, reported dead | **SOUND BUT UNCOMPUTABLE ON PUBLIC DATA.** Also structurally self-favouring: "Baselines can only emit a constant across `τ`, so their curve is a V … ours should be flat." A metric on which the incumbent is a constant function is not a comparison. |
| **SCR** (Support Coverage Ratio) | One-number summary of TQ-AUC | same | No | **SOUND BUT UNCOMPUTABLE.** Redundant with TQ-AUC; cut it. |

### Team 02

| Metric | Measures | GT needed | Third party? | Verdict |
|---|---|---|---|---|
| **CMC@α** | Coverage of the benchmark's own point labels by the predicted set | **None beyond existing point labels** | **Yes**, on any point-labelled dataset | **SOUND.** Split-conformal exchangeability gives the guarantee without knowing the convention. This is the one metric here that another lab could adopt tomorrow. |
| **SetEff** + the CMC–SetEff frontier | Set size at matched coverage | none | Yes | **SOUND.** Reporting the frontier rather than a point is the correct answer to "coverage is trivially bought". |
| **CI-AP** | AP where a TP is "GT lies in the predicted set", as a curve vs SetEff | existing labels | Yes | **SOUND.** Degenerates to standard AP as `\|Ŝ\| → 0`, so every published number is locatable on it — the reduction property the brief asks about, and the only team that designed it in. |
| **CS** (Convention Spread) `1 − min_{A,A'} IoU` | Dataset-level label irreducibility | sub-exposure GT + an author-chosen convention set `𝒜` | No | **RIGGED**, as specified. `CS` is a minimum over `𝒜`; adding `A_hull` inflates it without limit on fast objects, removing it collapses it. Without an `𝒜`-sensitivity table the number is a design choice. |
| **dW₁**, **sJ** | Dwell Wasserstein, support Jaccard | exact `μ` | No | **SOUND BUT UNCOMPUTABLE ON PUBLIC DATA** (simulator / FE108 only). |
| **Order accuracy** on time-reversal pairs | Can the model tell A→B from B→A | constructed pairs | Yes (constructible) | **SOUND.** Binary, chance = 50 %, and frame-only methods are at chance *provably*. A real null. |
| **π recovery error** | Recovered annotation convention vs imposed one | simulation | No | **SOUND BUT UNCOMPUTABLE** on real data. Needs a CI on real data or it is unfalsifiable. |

### Team 03

| Metric | Measures | GT needed | Third party? | Verdict |
|---|---|---|---|---|
| **SOA** (Support Overlap Accuracy) | W₁(ms) between predicted and GT support + mass AUC | GT support measures | No | **SOUND BUT UNCOMPUTABLE ON PUBLIC DATA.** |
| **SCR-spread** (Support-Conditioned Risk) | `err(O* < 0.3) − err(O* > 0.7)` | `O*`, i.e. frame-branch occupancy GT | No | **SOUND BUT UNCOMPUTABLE.** Presented as "the headline table column and every baseline can be scored on it without modification" — true only where `O*` exists, which is the simulator. |
| **TAB** (Temporal Abstention Benefit) | Risk–coverage AUC ordered by answerable mass minus by softmax confidence | none | **Yes** | **SOUND.** The one metric here with a real incumbent baseline (softmax confidence) and a real referent (task error). Should be the paper's headline. |
| **SCE** (Support Calibration Error) | ECE over answerable-mass bins | none | Yes, for their model | **SOUND** but unscorable for baselines (they emit no `α`), so it is a capability, not a comparison. |
| **SID** (Support Identifiability Distance) | `‖φ(A) − φ(B)‖/‖φ(A)‖` on matched pairs | constructed pairs | Constructible, but the pairs are simulator-generated | **RIGGED as a comparison.** SID is small for baselines *by the construction of the pair* (the pair is chosen so their inputs coincide) and large for the proposed encoder *by the construction of the encoder* (it consumes the differing quantity). Fine as an existence proof of inexpressibility; not a score. |
| **RSE** (Re-Exposure Error) | Error against a GT `ν`-exposure image the sensor never took | simulator | No | **SOUND BUT UNCOMPUTABLE**, and "existing methods cannot accept `ν` as an input at all" makes it a capability, not a comparison. |

### Team 04

| Metric | Measures | GT needed | Third party? | Verdict |
|---|---|---|---|---|
| **τ̂** (effective timestamp) | The time at which the prediction would have been right | continuous GT trajectory | With released checkpoints + high-rate GT — currently unobtainable | **SOUND BUT UNCOMPUTABLE ON PUBLIC DATA**, pending FE240hz. Well posed and honest about its own identifiability margin. |
| **b** (temporal bias) | `E[τ̂ − t_q]` | same | same | **SOUND.** Has a real null (`b = 0`) and a real alternative explanation (calibration) that the paper commits to testing. |
| **σ_τ** (within-frame dispersion) | Spread of `τ̂` across regions of one frame | same | same | **RIGGED as specified** — not by intent, but by omission. `σ_τ > 0` is the expected outcome under the null (one global clock + argmin noise), the argmin is admitted to be flat under constant velocity, and **no null distribution is proposed**. Becomes SOUND the moment a permutation null is added. |
| **TEF** | `1 − r_min/r_q` | continuous GT | same | **SOUND BUT UNCOMPUTABLE.** Note `r_min` is a minimum over a free interval `S`, so TEF rises monotonically with `\|S\|`; `S` must be fixed by the declared supports (as team 08 does with `τ_max`) or it is a knob. |
| **sAP-τ** | TP requires IoU > θ **and** `\|τ̂ − t_q\| < δ` | continuous GT | No | **RIGGED.** A metric that penalises the exact failure the proposed model is built to remove, with a free threshold `δ`, evaluated only by the authors. Legacy mAP is reported alongside, which helps, but this is the column a reviewer will strike. |
| **identifiability margin**, **collapse slope/R²** | Curvature of the agreement curve; goodness of the collapse | simulator | Partly | **SOUND.** Reporting an identifiability margin per measurement is unusually rigorous and I credit it. |

### Team 05

| Metric | Measures | GT needed | Third party? | Verdict |
|---|---|---|---|---|
| **OBD** `dδ̂/db` [ms/px] | Drift of the best-fit offset with blur extent | **None** — needs only an offset estimator and a speed estimate | **Yes**, on DSEC, with no labels | **SOUND.** Best null in the batch after team 01's SIE: *a rig constant must have zero drift*, a standard the calibration literature already holds itself to. |
| **SMF** (Support Mismatch Floor) | `min_δ` cross-modal residual vs the theoretical floor | none | Yes | **SOUND.** It is an impossibility bound checked against an oracle grid search, i.e. the strongest possible opponent. |
| **NDE** (Notch Depth/Location Error) | Distance from measured residual-spectrum nulls to predicted `k/b` | none | Yes | **SOUND.** Frequency-resolved and predicted analytically before measurement — a genuine pre-registration, unlike team 08's config arithmetic. |
| **SFA** (Sign-Flip Agreement) | Fraction of pixels where frame and event contrast signs disagree | none | Yes | **SOUND.** |
| **SOR** (Support Overlap Ratio) | Per-pixel overlap of observable bands, used as the reporting axis | needs a local speed estimate | Yes (contrast maximisation) | **SOUND**, with the caveat that using it as the *stratification axis* for all downstream results makes the strata author-defined; report the standard aggregate too. |

Team 05 has the cleanest metric suite in the round on hygiene grounds — every one is
label-free and every one has an analytic null. Its problem is entirely whether the effect
exists at reachable `b`.

### Team 06

| Metric | Measures | GT needed | Third party? | Verdict |
|---|---|---|---|---|
| **SFR** (Structured Fraction of the Residual) | Fraction of `Var(R)` removed by the parameter-free LME correction | **None.** Two frames, the events between them, and the exposure windows | **Yes** — DSEC ships all three | **SOUND**, and the strongest instrument in the round. Zero fitted parameters, an explicit noise null (R² = 0.0015), and two competing hypotheses pre-registered as overlaid flat references (random regressor; `\|ΔE\|`). |
| **EGR** (Exposure-Gap Ratio) `\|J\|/c` | The exposure gap in units of contrast thresholds, per dataset | none | Yes | **SOUND.** A per-dataset descriptive statistic, not a score — which is the right shape for a diagnostic. |
| **MCB** (Motion-Conditioned Contrast Bias) | Slope of (predicted − GT) log-contrast vs local blur length | sharp GT frames | Yes, on REBlur / HighREV / GoPro | **SOUND.** Real null at slope 0, and it scores *existing* methods, which is what converts diagnosis into indictment. |
| **TWD** (Time-Warp Distance) | Quantile-time error of the normalised profile, threshold-free | GT profile | Simulator / high-FPS source | **SOUND BUT UNCOMPUTABLE ON PUBLIC DATA** in its strict form; usable on high-FPS-derived data. |
| **ZNE-recall** | Reconstruction accuracy on zero-net-event pixels | sharp GT | Yes on REBlur/HighREV | **SOUND**, and the subset is defined by an event-stream criterion (`\|net E\| ≤ 1`, excursion ≥ 2) rather than by results — i.e. it is **not** a post-hoc stratification. That distinction matters and this team got it right. |

### Team 07

| Metric | Measures | GT needed | Third party? | Verdict |
|---|---|---|---|---|
| **CTE** (Crossing-Time Error) | Error in the predicted time of a state crossing | 1 kHz GT, or held-out real events (C1) | For C1: **yes**, and it is µs-exact real GT | **SOUND** for the C1 instantiation; **UNCOMPUTABLE ON PUBLIC DATA** for C2/C3 (passage, contact), where 200 Hz Vicon gives 5 ms sampling against a 1–2 ms effect. |
| **SFR** (Sub-Frame Resolution ratio) `Δt_f / P95(CTE)` | How many times finer than the frame grid the answer is | same as CTE | Yes for C1 | **SOUND.** The `SFR ≤ 1` null — "the method has learned nothing the frame grid did not already give it" — is a genuine, well-designed null that exposes frame-snapping. Best idea in this submission. (Acronym collides with team 06.) |
| **TCE** (Temporal Calibration Error) | Coverage of predicted time intervals | own predictions | Only for methods that emit a time distribution | **RIGGED as a comparison column.** The submission states it: "no existing method can even be scored on it." Legitimate as a *capability* report; illegitimate as a table column. |
| **CMR** (Censoring-Mass Recall) | AUC of `p_∅` against never/occurred | labels for "never" | Only for their model | **RIGGED as a comparison.** Same admission: "cannot compete by construction." |
| **FTB** (Frame Timestamp Bias) | Measured per-pixel effective-time deviation vs the `a·T²/(24 v̄)` law | 1 kHz GT | No | **SOUND BUT UNCOMPUTABLE ON PUBLIC DATA.** It is an analysis result with an analytic prediction (slope 1/24), which is good design — but only in a simulator. |

### Team 08

| Metric | Measures | GT needed | Third party? | Verdict |
|---|---|---|---|---|
| **τ̂** (per-method latency, ms) | WLS slope of `e_∥` vs `‖v*‖` through the origin | GT tracks with velocity — from released labels | **Yes**, entirely from dumped prediction files + label files | **SOUND**, with one large asterisk: on DSEC-Det the GT track is a **linear interpolation**, i.e. zero acceleration by construction, so `τ̂` is measured against a motion model. It measures (method latency − annotator latency) and the paper must say so. |
| **b** (speed-independent intercept) | Genuine spatial bias separated from latency | same | Yes | **SOUND.** Separating "your model is late" from "your warp is wrong" is a real diagnostic gain over TIDE's `loc` bucket. |
| **M** / **TS-Split** (`‖v*‖·τ_max/d` deciles) | Stratification by how many object diameters move during the admitted ambiguity | GT velocity + declared supports | Yes | **SOUND**, and importantly **not** a post-hoc stratification: `M` is computable from GT and declared specs *before* any model is run. This is the correct answer to the brief's "was the fast-motion subset chosen after seeing results" question, and team 08 is the only submission that gets it structurally right. |
| **AP^sync** | AP after re-anchoring by `−τ̂·v̂_pred`, with `v̂` from the method's own outputs | none beyond the above | Yes | **SOUND.** Never uses GT velocity at inference; that restriction is load-bearing and correctly imposed. |
| **AP^⊥** | AP after translating each prediction along the GT tangent by ≤ `τ_max` | **GT tangent at inference time** | Yes but | **RIGGED.** It uses the GT track direction to move the prediction, forgives the error component the paper argues is largest, and forgives *more* for later methods, so `AP^⊥ ≥ AP` always with a gain monotone in `\|τ̂\|`. The "flip" between `AP` and `AP^⊥` is mechanically available for any narrow pair. `τ_max` being derived rather than tuned is a genuine and unusual safeguard, and `AP^iso` is a real null — but the null tests *anisotropy*, not *legitimacy of forgiveness*. |
| **AP^iso**, **R** (anisotropy) | Free-direction relaxation of equal budget; ratio | same | Yes | **SOUND as controls**, with the caveat that `R`'s chance value must be simulated, not asserted at 0.5. |
| **Δ_clock**, **Δ_TS** | Gaps attributable to a constant clock offset vs per-object support error | same | Yes | **SOUND.** |
| **EPE_⊥** (flow) | Cross-flow error only | DSEC-Flow GT | Yes | **RIGGED as a ranking instrument.** For optical flow, the along-flow component *is* most of the signal; deleting it and then declaring E+I worse than E is a comparison on a metric that has removed the quantity the image branch most helps with. Report it as a decomposition, never as a verdict. |
| **Three-GT release** (`GT_inst`, `GT_exp`, `GT_lin`) | Spread of one prediction's score across three ground truths | simulation | Released artifact ⇒ yes | **SOUND**, and the most constructive deliverable in the entire round. "How much of your score is agreement with the annotation prior" is a number the community currently cannot compute, and shipping the three-GT set makes it computable by anyone. This alone would justify the paper. |

### Team 09

| Metric | Measures | GT needed | Third party? | Verdict |
|---|---|---|---|---|
| **RIG** (Reparameterisation Invariance Gap) | Metric change under a monotone time warp | none | Yes | **RIGGED.** `RIG = 0` for the proposed representation is a restatement of Proposition (2). The team calls it "a unit test, not a result" and then lists it as prediction P7. |
| **SSI** (Support-Separability Index) | `R²` of iso-error contours against `k·T` vs against `T` | controlled `(k,T)` grid | Yes (constructible) | **RIGGED.** `W(x)` measures `k·T` and the method divides it out; the metric asks whether the method is invariant to what it divides out. Billed as "the frame-side headline metric". |
| **CDR** (Clock Dynamic Range) | Largest speed ratio at which slow-object error stays within 5 % | none | Yes | **RIGGED.** "For any clamped rule this should equal `Δt_max/Δt_min`; for ours, unbounded." The competitor's value is read off their hyper-parameter table; the authors' is infinite by definition. |
| **ORL** (Onset Response Latency) | Settling time after an acceleration step | none | Yes | **RIGGED.** "Ours: **0 by construction**." |
| **HSP** (Heterogeneous-Speed Penalty) | Slow-object degradation per octave of speed ratio at fixed event rate | none | Yes | **SOUND.** This one can come out badly for the proposed method, and P3 is a falsifiable prediction about a *competitor* derived from that competitor's published constants. Keep it; it is the paper. |
| **SWC** (Support-Width Calibration) | Correlation of measured `W(x)` with true per-pixel blur severity | sharp reference (BS-ERGB / HighREV) | Yes where a sharp reference exists | **SOUND.** The only metric here with an external referent. Should be the frame-side headline instead of SSI. |
| **USW** (Undefined-Support Waste) | Fraction of representation entries with zero events | none | Yes | **SOUND** but it is a compute statistic, not a quality metric; report it with FLOPs as they propose. |
| **SSD** (Speed-Slope Dependence) | Metric slope vs `log2` event rate | none | Yes | **SOUND.** |

### Team 10

| Metric | Measures | GT needed | Third party? | Verdict |
|---|---|---|---|---|
| **EU(s)** (Event Utility vs speed) | Metric with the event branch on minus with it zeroed, vs intra-exposure displacement | GT flow + **recorded exposure timestamps** | **Yes**, on DSEC | **SOUND.** Modality dropout is a standard, model-agnostic probe; the x-axis `s = ‖v̄‖·T` uses two *measured* quantities (DSEC flow GT and DSEC's shipped exposure file), not an authored one. This is the submission's real contribution and it should lead. |
| **OSAM** (Off-Support Attention Mass) | Attention/Jacobian influence placed outside the causal tube | GT flow + a tube-dilation budget | Yes | **RIGGED.** The predicted curve `1 − r/(r+s)` is a geometric identity for any block with mixing radius `r`, so it confirms regardless of correctness; and the tube dilation is a free parameter setting the absolute level. Needs a well-typed null architecture with a calibrated zero. |
| **acausal mass** | Attention on bins not intersecting the exposure | declared bin edges | Yes | **SOUND.** Unlike OSAM this has a hard zero: a bin either intersects the exposure or it does not. RENet's 30/50 ms scales guarantee a nonzero floor **by construction**, which is a clean, undeniable finding. Promote it above OSAM. |
| **TM** (temporal misrouting, `W₁`) | Influence-weighted W₁ between mixed supports | declared supports | Yes | **SOUND.** |
| **SII** (Support-Inconsistency Index) | Type distance at each mixing site, aggregated | none | Yes | **SOUND as a descriptor, RIGGED as evidence.** The claim is a cross-model correlation `ρ > 0.7` over ≥ 5 models: at n = 5, r = 0.7 gives p ≈ 0.19. The stated target is below significance before any noise. |
| **SBP score / SBP-ECE** | Accuracy and calibration on provably ambiguous constructed pairs | constructed | Yes (constructible) | **SOUND.** Chance is 50 % by a theorem, not by convention, and every existing deterministic model is at chance *provably*. Cannot fail; should be Figure 1. |
| **Null-space sensitivity**, **certified interval width / coverage** | Whether the head uses invisible directions; ambiguity certificate | closed-form `𝒩` | Yes for their model | **SOUND** as a capability; unscorable for baselines, so not a comparison column. |

### Cross-cutting observations only this section can make

1. **Sixty invented metrics; four external referents.** Across all ten ideas exactly four
   metrics score against something the authors did not define: team 01's **SIE** (DSEC's
   published exposure timestamps), team 05's **OBD** (the calibration literature's own
   "a rig constant does not drift"), team 06's **SFR/MCB** (a zero-parameter predictor with
   a random-regressor null; sharp GT frames), and team 08's **E0 linear oracle** (the
   benchmark's own generative process). Everything else is scored against a definition. In
   the comparison set, C1 (human raters), C2 (re-annotated labels), C3 (human preference) and
   C4 (an invariance the protocol should have had), C10 (the same quantity under a corrected
   protocol) and C13 (an unbiased measure replacing a biased one) all have such a referent.
   That correlation is the whole of my ranking.
   Note also what the comparison set says about the *shape* of an acceptable contribution:
   **C11 was accepted while stating outright that it "does not describe a novel method."** So
   the fear running through teams 06, 08 and 10 — that a measurement paper with no architecture
   will be rejected as such — is empirically unfounded at these venues. All three should stop
   hedging with a token operator and let the measurement carry the paper; team 10 in particular
   should execute its own Death-1 fallback and move `SupportAttention` to the supplement now,
   rather than after a rejection.
2. **Acronym collisions inside the pool.** `SFR` is team 06's *Structured Fraction of the
   Residual* and team 07's *Sub-Frame Resolution ratio*. `SCR` is team 01's *Support Coverage
   Ratio* and team 03's *Support-Conditioned Risk spread*. `τ̂` and `b` mean different things
   in teams 04 and 08. `SOR`/`SOA`/`SID`/`SII`/`SSI`/`SWC` are six different quantities across
   four teams. Whichever idea proceeds, rename.
3. **Post-hoc stratification: one team gets it right.** The brief asks whether a
   "fast-motion subset" is chosen after seeing results. Teams 01, 03, 04, 06 and 10 all
   stratify by a quantity computable *before* running any model (displacement `d`, overlap
   `O*`, exposure `T_exp`, blur length `s`), which is legitimate. Team 08 goes further and
   derives its stratification variable `M` from the benchmark's and the method's declared
   specifications, and pre-commits to reporting the top-`M` decile as the headline slice. That
   is the correct construction and the others should copy it. **Team 02 is the exception**: its
   "top-20 % `ν` subset" and "top `ν` decile" are defined by a quantity (`ν`, intra-exposure
   velocity change) that requires the sub-exposure GT the paper is arguing about, and the
   thresholds (20 %, top decile) are stated without justification. Fix by pre-registering the
   threshold. **C12** (A Framework for Efficient Model Evaluation through Stratification,
   Sampling, and Estimation, ECCV 2024) is the in-venue standard for principled stratification
   with an analysed estimator variance, and not one of the ten submissions cites it.
4. **The interpolation question, decided.** Teams 04, 07 and 08 all propose to measure a
   millisecond-scale quantity against ground truth that is itself an interpolation. For
   DSEC-Det (linear interpolation of a tracker's output on 20 Hz RGB) and DSEC-3DOD (linear
   interpolation plus expert refinement over VFI-synthesised data, per C5), a linearly
   interpolated track has **zero acceleration by construction**. So: a *bias* measurement
   (team 08's `τ̂`, a first-order quantity) partially survives, because a constant-velocity GT
   still gets the tangent direction right; an *acceleration-driven* measurement (team 04's
   content-dependence and `σ_τ`, team 07's `Δt ≈ a·T²/(24 v̄)`, team 02's `ν`) **does not
   survive at all** — it would be measuring the interpolation prior's second derivative, which
   is zero. Team 08's P7 turns this into the finding; teams 04 and 07 must avoid these two
   datasets for their core claims entirely and say why in the paper.
5. **Four teams' primary real-data instrument may not exist.** Teams 01, 02, 04 and 07 all
   build their intra-exposure ground truth on FE108/FE240hz. Team 09 reports the host refuses
   connection. Nobody else checked. This must be resolved on day zero of whichever idea
   proceeds, because for teams 01, 04 and 07 the fallback (EVIMO2 at 200 Hz = 5 ms sampling)
   is comparable to the effect size they need to resolve.

---

## Ranking

1. **Team 06** — the only submission whose headline number needs no ground truth, no
   simulator and no labels, is reproducible by any reviewer from three public DSEC files, and
   already carries a measured null (R² = 0.0015 vs 0.78).
2. **Team 08** — the best anti-rigging engineering in the round (derived relaxation budget,
   isotropic null, injection–recovery, no proposed method, pre-registered stratification), and
   E0 alone is a C2-class benchmark-integrity result; docked for a thesis sentence its own
   §4 disclaims and for measuring against interpolated labels.
3. **Team 01** — SIE is the best-designed single validation in the round, and `K = 0` makes
   the ablation the SOTA comparison; docked for a prediction contradicted by data already on
   this machine, for four invented metrics where two would do, and for betting three of them
   on a dataset that may be gone.
4. **Team 02** — the most sophisticated evaluation theory (conformal coverage over an unknown
   convention, a metric that degenerates to AP, a frontier instead of a number); docked
   because the indictment is an n = 5 rank correlation with no bootstrap and `CS` is a
   minimum over an author-chosen set.
5. **Team 05** — every metric is label-free with an analytic null, and the load-bearing claim
   runs on CPU; docked because the effect may sit below its own derived onset on every real
   dataset it can reach, which is a one-day measurement nobody has made.
6. **Team 10** — the support-blind pair and the acausal-mass floor are two findings that
   cannot fail; docked because the headline diagnostic is a geometric identity and the
   headline statistic is p ≈ 0.19 at its own target value.
7. **Team 04** — `τ̂` is the right primitive and §4.4's pre-specified null is exemplary
   practice; docked because `σ_τ`, the declared kill shot, has no null model and the effect is
   the same size as the GT sampling interval on the only real dataset that could show it.
8. **Team 09** — the best dataset diligence in the round and one genuinely falsifiable
   prediction about a competitor (P3), buried under four metrics whose values are fixed before
   any experiment runs.
9. **Team 07** — one excellent idea (the C1 anchor: held-out real events as free µs ground
   truth) and one excellent null (`SFR ≤ 1`), inside an evaluation whose three remaining
   columns the submission itself admits no baseline can be scored on.
10. **Team 03** — an elegant reformulation whose money plot has an x-axis that exists only
    inside the authors' renderer, and whose escape route (BS-ERGB's measured occupancy
    windows) team 06 reports has gone dark.

---

## My winner and its fatal flaw

**Winner: Team 06, *Frames Are Not Samples: The Exposure Gap*.**

Not because it is the most ambitious — it is not; teams 01, 02 and 04 have larger ideas — but
because it is the only one that has already built a measuring instrument rather than a
scoreboard. The residual `R = c·ΔE − Δ log B` is regressed against a predictor `P` computed
from the event stream and the two exposure windows with **zero fitted parameters**, so there
is no knob with which to make the answer come out. It ships two competing hypotheses as
overlaid flat nulls (a random regressor at R² = 0.0015; an `|ΔE|` threshold-error regressor)
rather than testing against nothing. Its headline is measured with every sensor non-ideality
switched off, which forecloses the standard "that's just the sensor" rebuttal in one table
row. It runs on DSEC, which requires no application form and whose exposure-timestamp files
are already on this machine for eighteen sequences spanning a 127× range of exposure width.
And a reviewer can falsify the entire central claim in an afternoon without the authors' code.
Every paper in my comparison set has that property; almost nothing else in this round does.

The strategic case is the same one C2 makes: the most durable evaluation contributions are the
ones other people can pick up. `SFR` and `EGR` are two numbers any event–frame paper could
report about its own data, and `MCB` scores *other people's released checkpoints*, which is
what turns a diagnosis into an indictment.

**Its fatal flaw: the effect that makes the abstract exciting is measured where the effect is
largest by construction, and the paper has not yet measured it where the field actually lives.**

The 99.1–99.3 % figure — "on textured content, which is what natural video is, 99 % of the
residual is the exposure operator" — comes from a band-limited translating texture rendered
with an ideal sensor. The team's own table shows what happens when reality intrudes: a single
300 µs refractory period drops the slope from 0.955 to 0.779 and R² from 0.78 to 0.283, and
shot noise inflates `Var(R)` by 2.7×. A real DVS has refractory *and* shot noise *and* leak
*and* per-pixel threshold scatter *and* an intensity-dependent photoreceptor bandwidth, all at
once, and the paper has never run the composition. `J = ½·Var_W(L)` also scales with the
*square* of intra-exposure log-intensity variation, so it is largest exactly where DSEC is
weakest: the six night sequences pinned at 14 996 µs, where the exposure is 10× wider but the
scene is dark, low-contrast and low-texture — the regime in which `Var_W(L)` is suppressed by
the very darkness that opened the shutter. The daytime sequences have the texture but a
299–1871 µs window. The two ingredients the effect needs may be anti-correlated across the
entire benchmark.

There is a second, quieter version of the same flaw. `Var(R)` includes the event
quantisation floor of ±c/2, and `SFR` is a *fraction of that total variance*. On real data the
denominator grows — noise, hot pixels, bus effects — so `SFR` can fall for reasons that have
nothing to do with whether the exposure gap is real. The paper needs to report the *absolute*
gap `EGR = |J|/c` alongside `SFR`, because the absolute quantity is the one that is a property
of the world rather than of the noise budget.

The fix is one experiment and no GPU: run `R ~ P` on real DSEC, stratified by the measured
exposure width, per sequence, with bootstrap CIs, before writing a word of the introduction —
and pre-commit to reporting the real-data slope in the abstract even if it is 0.4 rather than
0.955. If it holds at 0.7 across a 50× change in exposure width on real driving data, this is a
CVPR paper and I would fight for it. If it collapses to 0.2, the honest paper is the
identifiability result (`G(a)` recovering per-pixel contrast threshold from two exposure
functionals, with conditioning that *improves* under faster motion), which is the piece
nothing in the comparison set contains — and which the team, to its credit, has already named
as its own strongest novel claim.
