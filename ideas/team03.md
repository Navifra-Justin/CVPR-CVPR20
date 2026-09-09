# Temporal Support Fields: Predicting *When* a Measurement Is Valid in Event–Frame Perception

*Idea Team 3 — CVPR 2027 candidate. Domain: event-based / asynchronous vision, temporal-support-aligned event–RGB perception.
Attack angle: change the representation unit — make temporal support the predicted quantity.*

---

## One-sentence thesis

Every event–frame system predicts *what* is at a pixel and treats time as an index attached to it; we invert this and predict, per pixel and per modality branch, the **temporal support** — a sub-probability measure on the time axis stating over which instants, and with how much total evidence, that observation is a statement about the scene — and then make fusion an *overlap of supports* rather than a similarity of features, which turns "the two modalities were not looking at the same time" from an invisible silent error into a first-class, measurable, and abstainable output.

---

## The assumption we kill

**The assumption: an observation has a timestamp.**

Not an interval — a *point*. It is so universal that it is never stated:

- An RGB frame is filed as "the frame at $t_k$", and event–frame alignment means warping events *to* $t_k$ (Time Lens, Time Lens++, CMTA, Bridge-Frame-and-Event). A point is the target of alignment.
- An event $e=(x,t_i,p)$ is filed as "an event at $t_i$", and every event representation — voxel grid, EST, Matrix-LSTM, time surface, HATS, RVT's fixed windows — bins those points into windows *chosen by the algorithm*, then asserts that every pixel in a window carries information about the whole window.
- Cross-modal attention scores a frame token against an event token by **feature similarity**; the fact that the two tokens may describe disjoint slices of time never enters the score. The CVPR 2026 RTEA module gets closest by injecting *relative temporal distance between two points* into attention — still a distance between indices, not a relation between supports.

**Why the assumption is universal.** Under slow motion it is harmless. If the object moves less than a pixel during the exposure, the frame *is* effectively instantaneous, and if the scene is texture-rich and moving steadily, inter-event intervals are short and roughly uniform across pixels, so a fixed bin is a fair approximation of every pixel's support. The whole benchmark culture (DSEC at 20 Hz RGB, MVSEC, the standard deblurring splits) sits in that regime, so the assumption is never stress-tested by the metrics.

**What breaks under fast motion.** Physically, neither modality carries a point measurement:

1. **A frame pixel is an integral, and its *effective* support is narrower than the exposure and content-dependent.** $B(x)=\frac1T\int_{\text{exp}} I(x,\tau)d\tau$ is an average over $T$, but as a statement about *one scene point* it is only valid over the interval in which that point occupied the pixel — the occupancy window. For a fast edge, that window is a small, off-centre fraction of $T$, and **it differs from pixel to pixel on the same object**. The exposure box that EDI and every event-deblurring formation model assumes is the *union* of many disjoint per-point supports, not any one of them.
2. **An event pixel's support is the inter-event interval, and it varies by three orders of magnitude across the sensor.** An event asserts $L(x,t_i)-L(x,t_{i-1})=pC$; its information support is $[t_{i-1},t_i]$ — microseconds in texture under motion, hundreds of milliseconds in a flat region. Binning into a fixed window overwrites this with a lie: every pixel is declared to have the bin's support.
3. **The absence of an event is an interval-valued constraint, not a zero.** No event on $(t_{\text{last}},t]$ asserts $|L(x,\tau)-L(x,t_{\text{last}})|<C$ for all $\tau$ in that interval — a *confirmed-static* statement with wide support and coarse value. A voxel-grid zero and an "unobserved" zero are the same number. The representation cannot tell "I checked and nothing changed for 40 ms" from "I have no idea."

So the two branches carry supports that are per-pixel, heterogeneous, and — under fast motion — **frequently disjoint**. Standard fusion sums, concatenates, or cross-attends features whose supports do not intersect. The result is a number that describes no instant that ever existed, and nothing in the pipeline can say so.

---

## The failure phenomenon

We do not open with a method. We open with a plot that no existing axis explains.

### The construction: *matched blur, different support*

The core experimental trick. Build **pairs** of sequences that are matched on every covariate the field currently uses, and differ only in temporal support:

- **(A) constant velocity.** An object traverses displacement $d$ at constant speed across the exposure $T$.
- **(B) dwell-then-dash.** The same object, same exposure $T$, same total displacement $d$, but it sits still for $0.8T$ and covers $d$ in the remaining $0.2T$.

Both give a blurred frame with the *same spatial blur extent* $d$ (the PSF's support length is identical; only its intensity profile differs). Event counts are matched by construction (same $d$, same contrast, same threshold ⇒ same number of threshold crossings). Average speed over the exposure is identical. Every covariate the literature regresses against — blur radius, event rate, mean optical flow magnitude, exposure length — is held fixed.

What differs is the **ground-truth support overlap**
$$O^\ast(x)=\sum_k \min\big(s^{F\ast}_{x,k},\,s^{E\ast}_{x,k}\big)\in[0,1],$$
the total-variation intersection mass between the frame pixel's occupancy measure and the event pixel's inter-event measure, both computed exactly by the simulator. In (A) the frame support is uniform over $T$ and the event support is uniform over $T$ ⇒ $O^\ast\approx 0.8$. In (B) the frame support is concentrated on the dwell (the first $0.8T$) while the event support is concentrated on the dash (the last $0.2T$) ⇒ $O^\ast\approx 0.15$.

### Data and axis

- **Primary (bulletproof):** a procedural 10 kHz renderer — textured sprites on textured backgrounds, analytic trajectories, pure `torch`/`numpy`, no assets, no interpolation network. Support ground truth is analytic. Disk cost ~0.
- **Secondary:** GoPro-240 / Adobe-240 / X4K1000FPS clips, temporally upsampled with RIFE, integrated to blurred RGB, converted to events with v2e (and cross-checked with DVS-Voltmeter to show the phenomenon is not a simulator artifact). Support GT is exact by construction: we know which sub-frames entered the integral and which inter-event interval each pixel had.
- **Real:** BS-ERGB / HS-ERGB (beam-splitter, pixel-aligned — no parallax confound) with occupancy windows *measured* from the high-speed strand; DSEC and NTIRE-2025 event-deblurring real data for validation.

**One plot.** $x$-axis: ground-truth support overlap $O^\ast$ in 10 bins. $y$-axis: task error (PSNR for event-guided deblurring; mAP for detection; EPE for flow). One curve per baseline. Point colour = blur extent $d$. The visual claim: **the colours are shuffled — blur extent does not order the points — while the curve falls off a cliff in $O^\ast$.**

### Quantitative predictions (falsifiable, stated in advance)

1. **Overlap cliff.** For EFNet, CMTA, REFID and Time Lens++, mean PSNR drops by $\ge 3.5$ dB between $O^\ast\in[0.7,1.0]$ and $O^\ast\in[0.0,0.3]$, with blur extent matched to within $\pm5\%$ and event count within $\pm5\%$.
2. **The standard axis is a confound.** Partial correlation $|\rho(\text{err},\,O^\ast \mid d,\,N_{\text{ev}})| \ge 0.6$, while $|\rho(\text{err},\,d \mid O^\ast, N_{\text{ev}})| \le 0.25$. The field's covariate explains the error only because it is correlated with the one nobody measures.
3. **Detection.** $\ge 8$ mAP gap between the top and bottom $O^\ast$ terciles at matched blur and event count, for RVT and an RGB-E fusion detector.
4. **Inexpressibility (the sharpest number).** For a matched pair (A,B) the fused representation of a voxel-grid + frame-encoder pipeline satisfies $\|\phi(A)-\phi(B)\|/\|\phi(A)\| < 3\%$ while the ground-truth targets differ by more than the inter-class spread. The representation is *provably* unable to separate two inputs whose correct answers differ. Our support-augmented encoder gives $>30\%$.
5. **Staleness tail.** On the $10\%$ of pixels with the lowest total support mass $m^\ast$, baseline error is $\approx 4\times$ the mean, and this subset is **not** identified by any confidence score the baselines produce (risk–coverage AUC of softmax/entropy confidence on this subset is within noise of random ordering).

Each of these indicts the *formulation*, not a hyper-parameter: no amount of retraining a model whose representation maps (A) and (B) to the same code can distinguish them.

---

## The reformulation

### State space

Latent log-intensity trajectory $L(x,\tau)$ (or, for high-level tasks, a latent scene state $z(x,\tau)$). Every observation $o$ is a linear functional of that trajectory against a finite nonnegative measure $\mu_o$ on the time axis:
$$o \;=\; \langle L(x,\cdot),\,\mu_o\rangle \;=\;\int L(x,\tau)\,d\mu_o(\tau).$$
$\mu_o$ is the **temporal support**. Two parts matter and must be kept separate:
- **mass** $m_o=\mu_o(\mathbb{R})\in[0,1]$ — *how much evidence exists at all* (this is what makes abstention expressible);
- **shape** $\bar\mu_o=\mu_o/m_o$ — *when the evidence is from*.

Instances:
- **Frame branch.** $\mu^F_x$ = occupancy-weighted measure on the exposure: the sub-measure of $[t_k-\tfrac T2,\,t_k+\tfrac T2]$ during which the scene point that dominates pixel $x$ actually projected into $x$. The classical exposure box is the special case $\mu^F_x=\mathrm{Unif}(T)$, i.e. the static-content assumption.
- **Event branch.** For the event at $t_i$, the signed functional is $\delta_{t_i}-\delta_{t_{i-1}}$ and the information support is $\mathrm{Unif}([t_{i-1},t_i])$. For a non-event stretch, the support is $\mathrm{Unif}([t_{\text{last}},t])$ with a *bound* value $|\Delta L|<C$ rather than an equality — full mass, coarse precision. **Crucially, this branch's ground truth is readable from the raw stream on real data, for free, with no annotation.**

### What is predicted

For branch $b\in\{F,E\}$ and site $x$ (pixel or token), the network emits a **sub-probability measure** over a normalized reference window $W=[t_{\text{ref}}-\Delta,\,t_{\text{ref}}+\Delta]$ discretized into $K$ bins ($K=16$ default):
$$\hat s^{\,b}_x \;=\; \hat m^{\,b}_x\cdot \mathrm{softmax}\big(\ell^{\,b}_x\big)\in[0,1]^K,\qquad \hat m^{\,b}_x=\sigma(\text{scalar head})\in[0,1].$$
Cost: $2(K{+}1)$ output channels on top of any backbone — negligible parameters, negligible memory. **The sub-probability (mass $\le 1$, not $=1$) is load-bearing:** a probability distribution is forced to place its mass somewhere and therefore cannot say "there is no valid observation here"; a sub-probability can.

Derived quantities, all differentiable:
$$O(x)=\textstyle\sum_k\min(\hat s^F_{x,k},\hat s^E_{x,k}),\qquad
\mathrm{BC}(x)=\textstyle\sum_k\sqrt{\hat s^F_{x,k}\hat s^E_{x,k}},\qquad
D_{W}(x)=\tfrac1K\textstyle\sum_k\big|\mathrm{cdf}^F_{x,k}-\mathrm{cdf}^E_{x,k}\big|.$$
$D_W$ is the closed-form 1-D Wasserstein-1 distance on the time axis — the natural metric for "how far apart in time the two branches are looking," and it is $O(K)$ to compute.

### Support-gated aggregation (the operator that replaces similarity fusion)

Standard cross-modal attention: $a_{xy}=\mathrm{softmax}_y(q_x\!\cdot\! k_y/\sqrt d)$.
Ours:
$$a_{xy}=\mathrm{softmax}_y\!\Big(\frac{q_x\cdot k_y}{\sqrt d} \;+\; \lambda\,\log\big(\langle \hat s^F_x,\hat s^E_y\rangle+\varepsilon\big)\Big),\qquad \langle \hat s^F_x,\hat s^E_y\rangle=\sum_k \hat s^F_{x,k}\hat s^E_{y,k}.$$
$\langle\hat s^F_x,\hat s^E_y\rangle$ is exactly *the probability that the two observations are statements about the same instant*. It is a **time-legality prior**, not a similarity: when it vanishes the logit goes to $-\infty$ and the pair is refused aggregation no matter how similar the features look. This is the mechanism claim of the paper — **an attention weight between asynchronous observations should be an overlap of supports, gated by (not replaced by) feature similarity.**

### Query-conditioned readout and abstention

The head takes a **query measure** $\nu$ — a requested instant $\delta_{t^\ast}$ (mollified), or a requested exposure box the sensor never actually took — and returns the task output together with an **answerable mass**
$$\alpha(x;\nu)=\big\langle \nu,\;\max\big(\hat s^F_x,\hat s^E_x\big)\big\rangle\in[0,1].$$
If $\alpha<\tau_{\text{abstain}}$ the model returns *no support* at that pixel and query time. This is not confidence: it is a statement about measurement coverage on the time axis.

### Objective

$$\mathcal L=\underbrace{\mathcal L_{\text{supp}}}_{\text{sim GT}}+\underbrace{\mathcal L_{\text{evt}}}_{\text{free on real}}+\underbrace{\mathcal L_{\text{ren}}}_{\text{self-sup on real}}+\mathcal L_{\text{task}}+\beta\,\mathcal L_{\text{cal}}+\gamma\,\mathcal R.$$

1. **Support supervision (simulator).** $\displaystyle\mathcal L_{\text{supp}}=\sum_{b,x}\underbrace{\tfrac1K\sum_k\big|\mathrm{cdf}(\hat{\bar s}^{\,b}_x)_k-\mathrm{cdf}(\bar s^{\,b\ast}_x)_k\big|}_{W_1\ \text{on the time axis}}+\mathrm{BCE}\big(\hat m^b_x,\,m^{b\ast}_x\big).$ $W_1$, not KL: two supports offset by one bin should cost less than two supports offset by ten, which KL cannot express.
2. **Event-support supervision on real data (free).** $s^{E\ast}$ is computed directly from the raw stream (inter-event intervals, last-event times). No annotation, no simulator. This is what makes the method trainable on DSEC/BS-ERGB as-is.
3. **Frame-support self-supervision on real data (rendering loss).** With the event-derived intensity trajectory $\hat I(x,\tau)=I_0(x)\exp\!\big(C\!\!\sum_{e\in(t_0,\tau]}\!\!p_e\big)$ (the EDI double-integral model), re-render the observed blurred frame under the *predicted* support:
$$\hat B(x)=\int \hat I(x,\tau)\,d\hat\mu^F_x(\tau)=\sum_k \hat s^F_{x,k}\,\hat I(x,\tau_k),\qquad \mathcal L_{\text{ren}}=\|\hat B-B\|_1.$$
EDI is the degenerate case $\hat s^F=\mathrm{Unif}$ with known exposure; here the box becomes a **learned, per-pixel, non-uniform measure**, and the loss requires no ground truth at all.
4. **Task loss** conditioned on $\hat s$ and on the query $\nu$, evaluated only where $\alpha\ge\tau_{\text{abstain}}$, plus an abstention-rate penalty so the model cannot abstain everywhere.
5. **Support calibration.** $\mathcal L_{\text{cal}}$ enforces that $\mathbb E[\text{err}\mid\alpha\text{-bin}]$ is monotone decreasing and matches a predicted risk — ECE, but on the temporal-support axis.
6. **Regularizers** $\mathcal R$: total variation of $\hat s$ over $x$ (supports vary smoothly on an object), entropy penalty on $\hat s$ over $k$ (prefer concentrated supports when the data allows), to control the identifiability null space (see Risks).

---

## What existing methods cannot express

Five statements no current event/frame representation can make. The first four are *inexpressibility*, not *inaccuracy* — no retraining fixes them.

1. **"There is no valid observation of this pixel at the requested time."** Every existing model always outputs a value. Sub-probability mass $\hat m\to0$ makes the empty answer a representable output. Confidence scores do not substitute: they are computed on the feature axis and are provably uninformative for the low-mass subset (prediction 5 above).
2. **"No event here means the scene was verifiably static for 40 ms."** A voxel-grid zero conflates a *strong interval constraint* ($|\Delta L|<C$ on a known interval, full support mass) with *no information* (zero mass). Ours separates them by construction: same value, different mass.
3. **"These two pixels, in the same frame, are valid over different intervals."** A fixed-window representation asserts one support for the entire tensor. Even adaptive slicing (ASTW, CVPR 2026) assigns one scalar window per *patch* by an event-density heuristic; it cannot represent a support whose shape is non-uniform inside the window, nor a support that is *different in the two modalities at the same pixel*.
4. **"These two observations have the same value but describe different instants."** The matched-blur/different-support pair (A,B) maps to the same code under every voxel/EST/time-surface + frame encoder. Note the honest distinction from the CVPR 2026 blur motion-ambiguity argument: they resolve ambiguity in the *motion pattern* using events; the residual we attack is in the **fused** representation — after events are consumed, the support relation between the two branches is still not represented, so the aggregation itself is unsound.
5. **"Render what a camera with exposure $\nu$ would have seen, and mark where you cannot."** A query-measure input is not even a well-typed argument to any existing event–frame model. Neural Image Re-Exposure comes closest by aggregating into a "neural film" under a chosen shutter, but the shutter is a *given* strategy, not an estimated per-pixel property of the input, and there is no coverage output.

**Newly solvable tasks that follow:** (a) support-conditioned re-exposure with an honest gap map; (b) temporal blind-spot detection — a detector that reports *"I hold no observation of this region at $t^\ast$"*, which is a safety primitive that Ev-3DOD-style "blind time" methods currently *fill in* rather than *flag*; (c) support-aware association — matching tokens across branches by overlap instead of similarity; (d) targeted support repair — deblur exactly where the event branch supplies overlap, and abstain where it does not.

---

## Why this is not <closest work>

| # | Work (venue, year) | What it does | Why we differ |
|---|---|---|---|
| 1 | **Adaptive Spatial-Temporal Window (ASTW)**, Sui et al., CVPR 2026 | Per-patch time-window length from event density, $\Delta t_{ij}=\gamma/D_{ij}$; training-free preprocessing; **event-only**, no losses | Nearest neighbour. Theirs is a *heuristic scalar window* chosen for aggregation convenience; ours is a **predicted, supervised, per-pixel sub-probability measure** with shape *and* mass, defined on **both** branches, whose cross-branch **overlap** is the fusion operator, and whose mass supports abstention. ASTW cannot represent non-uniform support, cross-modal support mismatch, or "no observation". We use ASTW as a baseline. |
| 2 | **Time-Specialized Event-Image Alignment (RTEA)**, Sun et al., CVPR 2026 | Blur-to-video decomposition; Relative Time-Encoded Attention injects *relative temporal distance* between event and image features | Their time term is a **distance between two point indices** — a positional encoding. Ours is an **overlap between two estimated measures**, which is zero for non-overlapping supports regardless of how close their centres are; and they never output support, so they cannot abstain or re-expose. |
| 3 | **Event-guided Deblurring of Unknown Exposure Time Videos (REFID)**, Kim et al., ECCV 2022 | Estimates the *unknown exposure/readout time*; ETES selects events by cross-modal correlation | The closest work on "predict the frame's temporal extent". But the estimated quantity is a **frame-level scalar** (an exposure duration) used for event *selection*; ours is a per-pixel measure whose *shape inside the exposure* is the point, plus an event-side support and a support-overlap operator. Their exposure box is our degenerate ablation. |
| 4 | **EDI — Bringing a Blurry Frame Alive**, Pan et al., CVPR 2019 | Double-integral formation model; blurred frame = uniform integral of the event-derived trajectory over a **known** exposure | We keep the double integral and replace $\mathrm{Unif}(T)$ with a learned per-pixel $\hat\mu^F_x$; the EDI residual becomes our *self-supervised support loss on real data*. EDI has no notion of the event branch's own support, no mass, no fusion gate. |
| 5 | **EFNet**, Sun et al., ECCV 2022 / **CMTA**, ECCV 2024 | Cross-modal attention (EFNet) and cross-modal temporal alignment (CMTA) for event-guided deblurring | Both align/attend toward a *target frame time* using feature similarity. Neither represents how much time each token speaks for; both are exactly the models our $O^\ast$ cliff plot indicts. |
| 6 | **Time Lens**, CVPR 2021 / **Time Lens++**, CVPR 2022 | Warping + synthesis interpolation to an arbitrary target *instant* | Their output time is a **point** and the interpolated frame is asserted valid at that point. We predict the *measure* an observation actually carries, and we can refuse to answer at a queried instant. Complementary, not competing: Time Lens is a strong source of high-support data for us. |
| 7 | **EST**, Gehrig et al., ICCV 2019 / **Matrix-LSTM**, Cannici et al., ECCV 2020 | Learn the kernel / recurrent surface that converts events into a grid | They learn a **feature-extraction kernel**, shared globally (EST) or recurrent per pixel (Matrix-LSTM), optimized only for task loss. It is a filter, not a *validity measure*: it has no ground truth, no physical semantics, no mass, and it cannot be compared across modalities. Ours is supervised against a quantity that exists in the world. |
| 8 | **Time surfaces / HOTS / HATS** | Per-pixel exponentially decayed last-event timestamp | A time surface is the *lower edge* of our event-branch support, collapsed to a scalar feature and fed to a CNN. It is event-only, has no frame counterpart, no mass, and is never used to gate aggregation. We can initialize $\hat s^E$ from it — that is precisely the ablation "is the network needed on the event side?" |
| 9 | **EVS-assisted Joint Deblurring / RS-correction / VFI by sensor inverse modeling**, Jiang et al., CVPR 2024 | Per-pixel optimization with an explicit measurement model incl. pixel latency, readout, refractory period | Closest on "explicit temporal measurement model." But theirs is a **known parametric sensor model solved by optimization for restoration**; the support is a hardware constant, not a content-dependent unknown. Ours *predicts* a content-dependent support field and uses it as the representation for downstream perception and abstention. |
| 10 | **RAM-Net**, Gehrig et al., RA-L 2021 | Recurrent asynchronous multimodal state updated whenever any modality arrives, queryable at any time | Handles asynchronous **arrival**; each observation is still consumed as instantaneous. Query-at-any-time returns an answer always. We add the support that makes "queryable at any time" honest. |
| 11 | **Bridge Frame and Event**, Zhou et al., CVPR 2025 | Common latent space between frame and event for high-dynamic optical flow | Bridges the *representation* gap; the *temporal support* gap remains, and their common latent is exactly where a support-overlap gate would apply. |
| 12 | **Exposure Trajectory Recovery from Motion Blur**, Zhang et al., TIP 2021 | Per-pixel motion **offsets** at multiple timepoints inside the exposure | Predicts *where* content was as a function of time (a spatial trajectory) assuming the whole exposure is valid. We predict *how much validity mass* an observation carries at each time and *whether it overlaps the other branch* — a different object, frame-only vs. bi-modal, and no abstention or overlap operator in theirs. |
| 13 | Per-pixel modality-reliability gating (e.g. gated event–RGB fusion, 2025–2026) | Predicts a scalar per-pixel weight for each modality | A scalar reliability has **no time axis**: it cannot answer "valid over which interval", cannot compute overlap, cannot re-expose, cannot abstain *at a specified instant*. This is the strongest "isn't this just uncertainty?" foil and it is an explicit ablation (§ Ablations, viii). |

**Honest verdict after search:** we found no work that predicts a temporal support measure as its output, and no work that computes attention as an overlap of supports. The two genuine collisions are ASTW (CVPR 2026) on *adaptive windows* and REFID (ECCV 2022) on *unknown exposure*; both are scalar, single-branch, and unsupervised-by-construction, and both become baselines and degenerate ablations here. The idea appears open.

---

## Experimental plan

### Datasets and sizes (990 GB free; budget $\le$ 250 GB)

| Strand | Data | Size | Role | Availability risk |
|---|---|---|---|---|
| Controlled-A | **Procedural 10 kHz renderer** (torch, no assets) | $<$5 GB | Phenomenon plot, analytic support GT, unlimited $O^\ast$ control | none |
| Controlled-B | **GoPro-240 / Adobe-240 / X4K1000FPS** → RIFE ×8 → v2e events + box-integrated RGB | ~40–80 GB derived (verify at download) | Realistic textures with exact support GT | low; pypi/HF reachable |
| Controlled-B′ | Same clips through **DVS-Voltmeter** | +15 GB | Simulator-invariance check | low |
| Real-1 | **BS-ERGB / HS-ERGB** (beam-splitter, pixel-aligned) | verify at download | Real RGB-E with a high-speed strand ⇒ *measured* occupancy windows | medium (host availability) |
| Real-2 | **DSEC** subset, 4–6 sequences | ~30 GB of ~150 GB total | Real driving detection/flow | low |
| Real-3 | **MVSEC** | ~30 GB | Flow/depth cross-check | low |
| Real-4 | **NTIRE-2025 event-deblurring / REBlur** real pairs | ~20 GB | Real deblurring benchmark with public baselines | medium |
| Stretch | **EVIMO2** | verify | GT object motion ⇒ approximate real support GT | medium |

### Controlled variable

**Support overlap $O^\ast$**, swept over $[0,1]$ by the dwell-fraction / exposure-ratio / speed-profile knob, **with blur extent and event count held fixed by construction** (matched pairs). Secondary sweep: support **mass** $m^\ast$ (staleness), by holding the scene static for a controlled interval before the query.

### Baselines (named, public code)

Deblur/decomposition: **EFNet** (ECCV'22), **REFID / Unknown-Exposure** (ECCV'22), **CMTA** (ECCV'24), **RTEA** (CVPR'26, if released).
Interpolation/alignment: **Time Lens** (CVPR'21), **Time Lens++** (CVPR'22).
Representation: voxel grid, **EST** (ICCV'19), **Matrix-LSTM** (ECCV'20), time surface / **HATS**, **ASTW** (CVPR'26, training-free).
Fusion/async/detection: **RAM-Net** (RA-L'21), **RVT** (CVPR'23).
Uncertainty foil: learned per-pixel scalar modality-reliability gating.

### Metrics

**Existing (and why they are blind).** PSNR/SSIM/LPIPS, EPE, mAP average over all pixels regardless of whether any modality held a valid observation at the query instant, so a method that *hallucinates a plausible value where no observation exists* scores identically to one that *reads a real observation*; and they aggregate over $O^\ast$, hiding the cliff entirely. This is why the failure has not been reported.

**Invented.**
1. **SOA — Support Overlap Accuracy.** $W_1$ (in ms) between predicted and GT normalized support, plus AUC of mass prediction. Measures the new output directly.
2. **SCR-spread — Support-Conditioned Risk spread.** $\text{err}(O^\ast{<}0.3)-\text{err}(O^\ast{>}0.7)$, and the AUC of the whole risk-vs-$O^\ast$ curve. A method is support-robust iff the spread is small. This is the headline table column and every baseline can be scored on it without modification.
3. **TAB — Temporal Abstention Benefit.** Risk–coverage AUC when coverage is ordered by answerable mass $\alpha$, minus the same when ordered by softmax/entropy confidence. Isolates information that lives only on the time axis.
4. **SCE — Support Calibration Error.** ECE computed over $\alpha$-bins.
5. **SID — Support Identifiability Distance.** $\|\phi(A)-\phi(B)\|/\|\phi(A)\|$ on matched-blur/different-support pairs. The inexpressibility number.
6. **RSE — Re-Exposure Error.** Given a query measure $\nu$ the sensor never took, error against the simulator's ground-truth $\nu$-exposure image, restricted to non-abstained pixels, reported jointly with abstention rate. Existing methods cannot accept $\nu$ as an input at all.

### Ablations

(i) predicted vs. GT support (oracle ceiling); (ii) probability instead of sub-probability (removes mass ⇒ abstention impossible) — quantifies how much of the gain is the mass channel; (iii) overlap-gated attention vs. plain cross-attention at matched parameter count; (iv) $K\in\{4,8,16,32\}$; (v) event-branch support *read directly from the raw stream* vs. predicted — is the network needed on that side at all; (vi) frame-branch support from $\mathcal L_{\text{ren}}$ self-supervision only, no simulator labels ⇒ sim-to-real transfer; (vii) uniform box support (= EDI / known exposure) ⇒ must recover EFNet-level numbers, proving the gain comes from non-uniformity; (viii) replace the overlap term with a learned scalar reliability ⇒ the uncertainty foil; (ix) ASTW's density heuristic substituted for the predicted support.

### GPU budget (one shared RTX 5090, design for $\le$ 9 GB)

| Item | GPU-h | Peak VRAM |
|---|---|---|
| Procedural renderer + support GT | 2 | $<$2 GB |
| RIFE upsampling + v2e/DVS-Voltmeter on ~30 clips @ 256² crops | 8 | ~5 GB |
| Phenomenon study: 4 pretrained baselines, inference only, ~2k matched pairs | 8 | $<$6 GB, batch 1–4 |
| Main model: small U-Net / RVT-S backbone, 256², $K{=}16$, batch 4, AMP, 60k iters × 3 runs | 60 | ~5.5 GB |
| 9 ablations @ 20k iters | 45 | ~5.5 GB |
| Real validation (BS-ERGB + DSEC subset) | 40 | ~7 GB |
| **Total** | **~163** | **$\le$ 7 GB** |

At ~50% availability of one shared GPU this is ~2 weeks wall-clock; the phenomenon plot alone (rows 1–3, ~18 GPU-h) lands in **2–3 days** and is the go/no-go gate. All work in Docker; no host installs.

---

## Risks

**Death 1 — the phenomenon is blur or uncertainty in disguise.** If, after matching blur extent and event count, the $O^\ast$ effect collapses (prediction 2 fails), there is no target for the reformulation.
*Fallback:* pivot the axis from **overlap** to **mass**. The staleness result is independent: pixels whose event support is old and whose frame support is saturated genuinely hold no information at $t^\ast$, and that is demonstrable from first principles. The paper then becomes *temporal abstention for asynchronous perception* — a smaller but intact contribution with the same predicted object. Additionally, the SID construction is an *existence proof*: a single matched pair with identical encoder output and different ground truth establishes inexpressibility even if the population effect is modest, and it is cheap to produce.

**Death 2 — "you invented the ground truth" (simulator-only).** Reviewers reject support supervision that exists only where we generated it.
*Fallback, in order of strength:* (a) the **event-branch support has exact ground truth on real data for free** — it is the inter-event interval, present in the raw stream; half the supervision is therefore real by construction; (b) the **frame-branch support is self-supervised on real data** by the EDI-rendering loss $\mathcal L_{\text{ren}}$, requiring no labels; (c) BS-ERGB/HS-ERGB give *measured* occupancy windows from the high-speed strand — measured, not simulated; (d) ship the ablation showing a model trained with **zero simulator labels** (real self-supervision only) recovers most of the gain. If (d) holds, the simulator is a diagnostic instrument, not a crutch, and the attack fails.

**Death 3 — the support is not identifiable.** The map (latent trajectory, support) $\to$ observation is bilinear; different $(L,\mu)$ pairs can explain the same $B$, so training may collapse to a uniform box and the whole output degenerates.
*Fallback:* (a) treat identifiability as a *result*, not an obstacle — with the events fixing the trajectory shape $\hat I$ up to scale, $\hat s^F_x$ solves a linear system whose basis is the event-defined trajectory samples; the null space shrinks as the in-exposure event count approaches $K$. **Measure and publish the recoverability regime** (support-recovery error vs. events-per-exposure): a plot that says *"support is identifiable above $N$ events per exposure"* is itself a contribution and pre-empts the objection; (b) adaptive parameterization — where events are sparse, predict only a 2-parameter (centre, width) support, which is identifiable under much weaker conditions, and switch to the $K$-bin form where events are dense; (c) if even the 2-parameter form fails, retreat to predicting only the *first moment* and the *mass*, which is enough for the overlap gate and for abstention, and drop the re-exposure task.

**Minor — baseline plumbing.** Five external repos in "days not weeks" is the real schedule risk. Mitigation: the phenomenon plot needs only *inference* from EFNet/CMTA/REFID (all with public weights); RTEA and ASTW are added if code appears, and their absence does not block the argument.

---

## Self-score

*(novelty, feasibility, reviewer-proof-ness: higher is better. incrementality: lower is better.)*

| Axis | Score | Harsh justification |
|---|---|---|
| **Novelty** | **8 / 10** | The predicted object — a per-pixel, per-branch sub-probability measure on the time axis, supervised against a physically defined ground truth and used as the *aggregation kernel* — does not exist in the literature we searched. The nearest work, ASTW (CVPR 2026), is a training-free scalar heuristic on one modality. Docked two points because "adaptive temporal windows" and "uncertainty-aware fusion" are both crowded neighbourhoods, and a hostile reviewer will file this under one of them on a first read. |
| **Feasibility** | **7 / 10** | The simulator gives free ground truth, the model is a $2(K{+}1)$-channel head on any backbone, peak VRAM ~7 GB, and the go/no-go phenomenon plot lands in 2–3 days. Docked for the five-baseline plumbing burden and for the real datasets (BS-ERGB, NTIRE) whose availability we could not verify before the search budget ran out. |
| **Reviewer-proof-ness** | **6 / 10** | Two attacks are certain: *"this is uncertainty estimation with extra steps"* and *"your ground truth is synthetic."* Both have pre-registered answers (the scalar-reliability ablation (viii); the zero-simulator-label ablation (vi) plus the free real event-side GT), but the answers must land in the main paper, not the supplement. The identifiability question is the one a strong reviewer will find on their own, which is why it is promoted to an experiment. |
| **Incrementality** | **3 / 10** *(lower is better)* | It changes the predicted object and the aggregation operator, and it makes two tasks (support-conditioned re-exposure, temporal blind-spot flagging) newly well-posed. It is not fully non-incremental: it still lives inside the existing event–frame task suite and reports PSNR/mAP alongside the invented metrics, and its strongest single experiment (the $O^\ast$ cliff) is an analysis of *existing* methods. |

---

## 한국어 요약

**한 줄:** 모든 이벤트–프레임 방법이 "관측에는 타임스탬프가 있다"고 가정하지만, 실제로 RGB 픽셀은 노출 구간에 대한 적분이고 이벤트 픽셀은 직전 이벤트까지의 구간에 대한 진술이다. 우리는 이 **시간적 지지(temporal support)** 자체를 — 픽셀별·모달리티별 시간축 위의 준확률측도로 — 네트워크가 *예측하게* 만들고, 융합을 특징 유사도가 아니라 **지지의 겹침(overlap)**으로 재정의한다.

**핵심 실패 현상:** 블러 크기와 이벤트 수를 동일하게 맞춘 "등속 vs 정지-후-질주" 쌍을 만들면, 기존 지표(블러 반경·속도·이벤트율)는 전부 같은데 지지 겹침 $O^\ast$만 0.8 대 0.15로 달라진다. 예측: EFNet/CMTA/REFID의 PSNR이 3.5 dB 이상 벌어지고, 편상관은 $O^\ast$ 쪽이 0.6 이상, 블러 쪽은 0.25 이하. 즉 학계가 쓰는 축은 교란변수이고 진짜 축은 아무도 측정하지 않는 양이다.

**표현 불가능성:** 기존 표현은 (1) "이 시점에 유효한 관측이 없음", (2) "이벤트 없음 = 40 ms 동안 정적임이 확인됨 vs 미관측", (3) 같은 프레임 안에서 픽셀마다 다른 지지, (4) 값은 같지만 시간이 다른 두 관측을 **원리적으로** 구분할 수 없다.

**가장 가까운 경쟁 연구:** ASTW (CVPR 2026, 이벤트 전용 밀도 휴리스틱 윈도우)와 REFID (ECCV 2022, 프레임 단위 스칼라 노출시간 추정). 둘 다 스칼라·단일 브랜치·비지도이며, 본 아이디어의 퇴화 케이스이자 베이스라인. 검색 범위 내에서 지지 측도를 **출력으로 예측**하거나 어텐션을 **지지 겹침**으로 계산한 연구는 없음.

**자체 평가:** 독창성 8, 실현가능성 7, 리뷰어 방어력 6, 증분성 3(낮을수록 좋음). 최대 위험은 "결국 불확실성 추정 아니냐"와 "GT가 합성 아니냐"이며, 각각 스칼라-신뢰도 대체 ablation과 시뮬레이터 라벨 0개 학습 ablation(이벤트 측 지지는 실데이터에서 무료로 GT가 나옴)으로 본문에서 선제 방어.
