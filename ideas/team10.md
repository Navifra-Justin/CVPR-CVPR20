# Fusion Is Ill-Typed: Temporal Support as a First-Class Type in Event–RGB Perception

## One-sentence thesis

A frame and an event tensor are not two views of the same observable at slightly different times — a frame is a **positive interval-mean of irradiance** and an event bin is a **zero-mass signed boundary difference of log-irradiance** — so every concatenation, gate, cross-attention and contrastive loss in the RGB–event literature mixes measurements of different *type*, not merely different *timing*; we give the type system that says which operations are legal, a diagnostic that audits published architectures for illegal mixing, and the measurable prediction that follows: **existing fusion models extract less from events as scene speed increases**, i.e. event utility inverts exactly in the regime events exist for.

---

## The assumption we kill

**The assumption.** *Frame features and event features are comparable tensors: they describe the same scene content over (approximately) the same time interval, differing only in modality; therefore a learned affine mixer — concat+conv, gated sum, cross-attention, AdaIN statistic matching, or a shared-token backbone — is the right operation, and any residual mismatch is a spatio-temporal **alignment** problem to be solved by warping, registration, or a bigger temporal window.*

**Why it is universal.** It is inherited wholesale from RGB-D and RGB-thermal fusion, where both sensors *are* instantaneous samplers of co-located quantities and misalignment really is the only problem. Every RGB–event paper we surveyed adopts it verbatim: RENet (ICRA'23) accumulates event frames over the RGB exposure *and* over 30 ms and 50 ms windows and concatenates all of them with one RGB tensor; FRN (ECCV'24) aligns channel-wise mean and variance of the two streams with AdaIN; CEUTrack (CVPR'23) feeds RGB patches and event-voxel patches as tokens into one self-attention backbone; SODFormer (TPAMI'23) attends across frames and events asynchronously; BRENet (2025) makes the assumption explicit and admirable by "recasting RGB-Event segmentation **from fusion to registration**." The field's own diagnosis is "temporal misalignment: events are µs, frames are ms," and its own prescription is alignment. That diagnosis is one level too shallow.

**What actually breaks.** Write the latent scene as continuous log-irradiance $L(\mathbf x,t)$, $I=e^{L}$.

- Global-shutter frame with exposure $[t_0,t_0{+}T]$:
  $F(\mathbf x)=\tfrac1T\int_{t_0}^{t_0+T}e^{L(\mathbf x,t)}\,dt$, i.e. $F=\int e^{L}\,d\mu_F$ with $\mu_F=\tfrac1T\mathbf 1_{[t_0,t_0+T]}dt$: a **probability measure on the interior** of the exposure, applied in the **linear** domain.
- Event bin over $[a_b,a_{b+1}]$ with contrast threshold $C$ (polarity sum, the standard voxel/EST/SCER primitive):
  $V_b(\mathbf x)=\sum_{t_i\in[a_b,a_{b+1}]}p_i\approx\tfrac1C\!\left(L(\mathbf x,a_{b+1})-L(\mathbf x,a_b)\right)$, i.e. $V_b=\int L\,d\mu_b$ with $\mu_b=\tfrac1C(\delta_{a_{b+1}}-\delta_{a_b})$: a **signed measure of total mass zero supported on two instants**, applied in the **log** domain.

**Proposition 1 (a type error, not a misalignment).** $\mu_F$ lies in the cone of probability measures ($\mu(\mathbb R)=1$); $\mu_b$ lies in the subspace of zero-mass signed measures ($\mu(\mathbb R)=0$). These sets are disjoint. Hence there is **no** time shift $s$, no positive scale $c$, and no spatial warp $W$ with $c\,\mu_b(\cdot-s)=\mu_F$; and the photometric maps ($\exp$ vs. $\mathrm{id}$) differ, so no pointwise reweighting closes the gap either. **Perfect temporal and spatial registration leaves the two quantities as different observables.** Alignment is orthogonal to the defect.

The corollary that indicts the architecture: a convex mixture $\alpha F+(1-\alpha)V_b$ has temporal measure $\alpha\mu_F+(1-\alpha)\mu_b$, whose total mass is $\alpha\neq 0,1$. It is not an estimate of the frame's observable, not an estimate of the event's observable, and not an estimate of any scene quantity at all. The mixer is well-defined as arithmetic and undefined as measurement. Nothing in a modern fusion codebase can notice this, because a tensor carries a shape and a dtype but not a support.

---

## The failure phenomenon

We lead with the *consequence*, because it is the statement about the field; the attention-level mechanism is the second panel.

### Panel A (headline) — Event utility inverts with speed

**Measurement.** For a published RGB–event model $M$ and a test sample, compute the **event utility**
$$\mathrm{EU} = \text{metric}\big(M(F,\mathcal E)\big) - \text{metric}\big(M(F,\mathbf 0)\big)$$
(modality dropout: zero the event branch at inference). Inference only, no training.

**Independent variable.** $s$ = mean displacement of scene content **during the frame's own exposure**, in pixels: $s=\|\bar v\|\cdot T$, with $\bar v$ from the dataset's ground-truth flow (DSEC ships optical flow) and $T$ from the dataset's **recorded exposure timestamps** (DSEC ships `image_exposure_timestamps_left/right.txt` per sequence — the support is a *measured* quantity, not an assumption). In the simulator $s$ is dialed exactly.

**Axes.** x: $s\in[0.25,16]$ px (log). y-left: $\mathrm{EU}$ (mAP points, or dB). y-right: OSAM from Panel B. One curve per published model.

**Expected curve.** $\mathrm{EU}(s)$ rises to a peak near $s\approx r$ (the fusion block's effective spatial mixing radius, 2–4 px at the fused stride) and then **falls**, crossing toward zero — the event branch stops contributing precisely where the frame is most degraded. The field's motivating claim predicts the opposite (monotone increasing).

**Quantitative prediction.** Across ≥4 published models: $\mathrm{EU}$ at the top flow decile is at most **60%** of $\mathrm{EU}$ at the median decile, and for at least two models $\mathrm{EU}<0.3$ mAP points in the top decile versus $>1.5$ points at the median. Peak location correlates with the block's mixing radius, $\rho>0.7$ over models.

### Panel B (mechanism) — Off-Support Attention Mass

**Measurement.** Instrument every mixing site. For attention-based fusion take the softmax weights directly; for gates/AdaIN/convolutional mixers use the **Jacobian influence** $\alpha_j\propto\|\partial y/\partial v_j\|_F$, normalized — so the diagnostic is *not* attention-only and applies to FRN, RENet and every gated design. Define the **causal tube** of a query pixel $\mathbf y$: the set of $(\mathbf x,b)$ such that the scene point imaged at $\mathbf y$ during the exposure is at $\mathbf x$ during bin $b$ (from GT flow, dilated by the calibration/flow error budget). Then
$$\mathrm{OSAM}(\mathbf y)=\!\!\sum_{(\mathbf x,b)\notin \text{tube}(\mathbf y)}\!\!\alpha_{\mathbf y,(\mathbf x,b)},\qquad
\mathrm{TM}=\mathbb E_{\mathbf y}\Big[\sum_j\alpha_j\,\tfrac{1}{T}W_1(\hat\mu_j,\hat\mu_F)\Big]$$
plus **acausal mass**: weight placed on bins whose interval does not intersect the exposure at all (RENet's 30/50 ms scales guarantee a nonzero floor here by construction).

**Expected curve.** $\mathrm{OSAM}(s)\approx 1-\tfrac{r}{r+s}$: from $0.12\pm0.03$ at $s{=}0.5$ px to $0.83\pm0.05$ at $s{=}12$ px, while **attention entropy stays flat or decreases** — the model gets *more* confident as it gets more wrong about provenance. On real DSEC-Det the OSAM gap between the top and bottom flow deciles is $\geq0.35$ absolute for RENet and FRN.

**The indictment of the formulation, not the weights.** Fine-tune each model on the high-$s$ regime. Prediction: task metric improves 2–4 points, **OSAM falls by $<0.08$ absolute**, and $\mathrm{EU}$ does not recover — the model adapts by *down-weighting the event branch*, not by routing correctly. Training cannot fix it because the architecture has no channel through which the correct routing could be expressed: the tensors do not carry their supports, so no layer can condition on them. This is what makes the phenomenon indict the *formulation*.

### Panel C (free, real-data) — Auto-exposure is an unread variable

DSEC's exposure timestamps show $T$ varying frame to frame (auto-exposure across tunnels, shade, sun). No published RGB–event model reads $T$. Prediction: per-frame error correlates with $T\cdot\|\bar v\|$ at $\rho>0.5$ even after controlling for $\|\bar v\|$ alone — a measurable dependence on a quantity the models are structurally blind to. This costs one afternoon of inference and it is undeniable.

---

## The reformulation

### Support types

A measurement is a pair $m=(v,\tau)$ where the **support type** is
$$\tau=(\phi,\ \mu,\ \kappa,\ \pi),\qquad v = \int \phi\big(L(\kappa(\cdot),t)\big)\,d\mu_{\pi}(t)$$
- $\phi\in\{\exp,\mathrm{id}\}$ — photometric domain (linear irradiance / log);
- $\mu$ — signed Borel measure on time, the **temporal support**;
- $\kappa$ — spatial reference: not a pixel index but a *trajectory* $\mathbf x(t)$ (a pixel index is the degenerate static case);
- $\pi(\mathbf x)$ — per-pixel offset of $\mu$ (rolling shutter, per-row readout, flicker-locked illumination).

Two derived tags: **order** $o(\tau)=0$ if $\mu(\mathbb R)\neq0$ (an integral/mean observable) and $1$ if $\mu(\mathbb R)=0$ (a difference observable); **centroid** $\bar t(\tau)$ and **width** $|\mu|$.

Canonical types: $\tau_F=(\exp,\ \tfrac1T\mathbf 1_{[t_0,t_0+T]}dt,\ \cdot,\ \pi_{\text{RS}})$, $o=0$; $\tau_{V_b}=(\mathrm{id},\ \tfrac1C(\delta_{a_{b+1}}-\delta_{a_b}),\ \cdot,\ 0)$, $o=1$. Also expressible and currently inexpressible: SCER-style exposure-referenced cumulants, event *counts* (order 0 in $|\mu|$), time surfaces (order 0 with an exponential kernel), and rolling-shutter frames (a *field* of types).

### The allowed operations (typing rules)

Let $m_j=(v_j,\tau_j)$.

- **R1 — Affine mixing.** $\sum_j\alpha_j v_j$ (concat+linear, sum, gate, attention, AdaIN) requires equal $\phi$, equal $o$, and compatible $\kappa$. If those hold, the mix is legal **but the output type changes**: $\mu_{\text{out}}=\sum_j\alpha_j\mu_j$, and the result must carry it. Mixing across $o$ or across $\phi$ is a **type error** with no repair by shifting, scaling, or warping (Prop. 1).
- **R2 — Comparison.** Losses, metrics, cosine similarity, contrastive alignment, distillation: legal only if $\tau_1=\tau_2$ exactly. (Most event–image contrastive objectives are ill-typed under this rule; so is supervising an instantaneous prediction against a blurry frame.)
- **R3 — `lift`** (the *only* type-raising primitive): $\{m_j\}\mapsto(\hat L,\ \mathcal N)$, a latent estimate on an interval **together with the affine set of latents it cannot distinguish**.
- **R4 — `render`** (type-lowering): $\hat L\mapsto \mathcal A_\tau[\hat L]$. Every cross-type interaction must factor as $\mathrm{render}_{\tau_{\text{target}}}\circ\mathrm{lift}$. Nothing else may cross a type boundary.
- **R5 — Support–motion coupling.** Because $\kappa$ is a trajectory, an event at $(\mathbf x,t)$ is co-typed with frame pixel $\mathbf y$ only if $\mathbf x$ lies on $\mathbf y$'s causal tube. Pixel-aligned mixing silently violates R5 as soon as displacement over the window exceeds the mixing radius — this is where speed enters, and it is the analytic source of Panel B.

A **support-typed network** is one where every tensor carries $\tau$ and every module is one of R1/R3/R4 with its type transition recorded; a static checker rejects the rest. This is ~200 lines over PyTorch (`TypedTensor` + module wrappers), not an architecture.

### Identifiability: what a support pair can and cannot answer

Given $F$ with $\tau_F$ and $\{V_b\}_{b=1}^{B}$ over $[t_0,t_1]$, the consistent set is
$\mathcal C=\{L:\ \mathcal A_{\tau_F}[L]=F,\ \mathcal A_{\tau_b}[L]=V_b\ \forall b\}$, with tangent space (the **support null space**)
$$\mathcal N=\Big\{\eta:\ \eta(a_b)=0\ \forall b,\quad \int e^{L}\,\eta\, d\mu_F=0\Big\}.$$
Restricted to a degree-$d$ temporal basis, $\dim\mathcal N=\max(0,\ d-B-1)$ per pixel.

**Support-identifiability condition.** A task functional $\Psi$ (a sharp frame at $t^\star$, an instantaneous velocity, an object's position at the shutter centre) is answerable from these measurements **iff $\nabla\Psi\perp\mathcal N$**. Otherwise the correct output is an interval, not a point.

**Support-blind pairs (constructive witness).** Take one bin $[a,b]$ and two per-pixel paths $L_2(t)=L_1(a{+}b{-}t)$ (time reversal). Then: identical endpoints $\Rightarrow$ identical polarity-sum voxel grids; identical integral $\Rightarrow$ identical blurry frames; but $L_1(t^\star)\neq L_2(t^\star)$ at any asymmetric $t^\star$. Physically: a bar that goes right-then-left versus left-then-right within the bin. **Every published model maps this pair to one input point and emits one confident answer for two different worlds.** The pair is renderable procedurally in an afternoon, needs no download, and the ambiguity is a theorem, not an empirical hope.

### The operator (minimal demonstration, deliberately small)

`SupportAttention` replaces a fusion block $\mathrm{Attn}(Q_F,K_E,V_E)$ with:
1. read $\tau_F$ from the dataset's exposure timestamps and $\{\tau_b\}$ from the model's own event-binning config;
2. **lift**: a $1\!\times\!1$ head predicts coefficients $c$ of a B-spline basis $\{\psi_k\}$ on $[t_0,t_1]$, then **projects onto the affine solution set** of the linear constraints $\hat L(a_{b+1})-\hat L(a_b)=C\,V_b$ (closed form; the projector is precomputed once). The remaining freedom is exactly $\mathcal N$, whose basis is carried forward;
3. **render**: $\tilde K_b=\mathcal A_{\tau_F}[\hat L]$ evaluated along the causal tube — every key now has the *frame's* type;
4. attention over re-typed keys/values, masked by the tube (R5);
5. output tagged $\tau_{\text{out}}=\tau_F$, so all downstream layers type-check.

Overhead: one $1\!\times\!1$ conv, one fixed linear projection, one mask.

**Objective — type-correct supervision plus a null-space prohibition:**
$$\mathcal L=\underbrace{\big\|\mathcal A_{\tau_F}[\hat L]-F\big\|^2+\lambda\sum_b\big\|\mathcal A_{\tau_b}[\hat L]-V_b\big\|^2}_{\text{render back to each measurement's own type}}\;+\;\beta\underbrace{\mathbb E_{\eta\sim\mathcal N,\|\eta\|=1}\big\|\nabla_{\hat L}\Psi\cdot\eta\big\|^2}_{\mathcal R:\ \text{decisions may not use invisible directions}}\;+\;\mathcal L_{\text{task}}$$
$\mathcal R$ is new in kind: it forbids the head from making decisions along directions the measurement pair provably cannot see, and it is cheap (a few Hutchinson samples from an analytically known $\mathcal N$). It is the direct antidote to the shortcut that support-blind pairs expose.

**What we predict for the operator, stated in advance.** It will *not* top the average leaderboard, and we will say so. It should (a) flatten OSAM to near the tube-error floor, (b) make $\mathrm{EU}(s)$ monotone increasing, (c) win the top flow decile by 1.5–3 mAP / 0.5–1.0 dB, (d) be the only model with non-degenerate calibration on support-blind pairs. The operator is an existence proof for the principle; the diagnostic is the contribution.

---

## What existing methods cannot express

1. **Their own ambiguity.** No RGB–event model can emit "these measurements do not determine the answer." $\mathcal N$ is computable in closed form; nobody computes it. Certified ambiguity intervals ($\sup_{\mathcal C}\Psi-\inf_{\mathcal C}\Psi$) are a *new output*, not a new score.
2. **A per-pixel support.** A rolling-shutter frame is a field of types $\pi(\mathbf x)$ spanning 10–30 ms across rows; every architecture represents it as one tensor with one timestamp. Same for flicker-locked illumination and for the contrast- and illumination-dependent latency of the event pixel itself (the support of an event is *itself* uncertain and biased).
3. **The difference between "nothing happened" and "it cancelled."** A zero in a polarity-sum bin is a mass-zero boundary statement; an interval mean cannot separate the cases either. Only the typed pair with an explicit null space can flag the distinction.
4. **The type of a fused feature.** After the first mixer the output has a well-defined but unrecorded support $\sum_j\alpha_j\mu_j$; the second fusion layer therefore cannot know what it is mixing. Deep fusion stacks compound the error and no framework can see it.
5. **The legality of a loss.** Nothing in current practice can answer "is this contrastive event–image alignment comparing comparable things?" R2 answers it, and the answer is usually no.
6. **A varying exposure.** DSEC's own auto-exposure varies $T$ frame to frame; no model reads $T$. The support is *recorded in the dataset and ignored by every consumer of it.*

---

## Why this is not <closest work>

| Work (venue, year) | What it does | Why we differ |
|---|---|---|
| **BRENet**, *Rethinking RGB-Event Semantic Segmentation with a Bidirectional Motion-enhanced Event Representation* (arXiv 2505.01548, 2025) | Explicitly "recasts RGB-Event segmentation from fusion to **registration**"; flow-guided bidirectional pairing; Motion-Enhanced Event Tensor | The strongest statement of the assumption we kill. Registration fixes $\kappa$ and shifts $\bar t$; Prop. 1 shows an interval mean and a mass-zero boundary difference remain incomparable after perfect registration. We attack $\phi$ and $o$, which registration cannot touch. |
| **RENet** (ICRA 2023, code+weights) | Event frames over the RGB exposure **and** over 30 ms / 50 ms, all concatenated with one RGB tensor; bidirectional attentive fusion | This is our canonical ill-typed mixer: three supports, one frame, one mixer, no type recorded. We quantify its acausal attention mass — nonzero *by construction* — and its cost. Not a competitor; a subject. |
| **FRN** (ECCV 2024, code+weights) | Bidirectional cross-modality interaction + AdaIN channel mean/variance alignment; SOTA on DSEC-Det | Matching first and second channel moments of two *different observables* is statistical alignment of incomparables. Our Jacobian-influence OSAM applies to non-attention mixers precisely so FRN is auditable. |
| **CEUTrack / COESOT** (CVPR 2023, code+weights) | RGB patches and event-voxel patches as tokens in one self-attention backbone | Maximal type violation: every token pair is mixed regardless of support. A worst case for the diagnostic, and a clean test of whether SII ranks models by their speed-degradation slope. |
| **SODFormer** (TPAMI 2023) | Streaming detection with asynchronous attention over events and frames | Closest on treating asynchrony as first-class. But it asynchronizes *when computation happens*, not *what each tensor measures*; the mixing rule is still type-blind. |
| **EFNet** (ECCV 2022, code+weights) | Cross-modal attention for deblurring + **SCER**, a symmetric cumulative event representation referenced to the exposure | Honestly the most support-aware prior art: SCER is a hand-designed, single-task instance of `render`-to-frame-type. We generalize it into a rule, show EFNet still mixes ill-typedly at other levels, and remove its assumptions of a single known exposure and a single reference instant. |
| **E-CIR** (CVPR 2022), **UniINR** (ECCV 2024), **Neural Image Re-Exposure** (2023), **Exposure-agnostic event VFI** (arXiv 2510.22565, 2025) | Continuous-time latent (polynomial / INR / "neural film"); exposure embedded as a parameter | Closest on the `lift`/`render` mechanism, and we credit them. All are single-task *reconstruction* methods: they assume one known-or-estimated exposure, do not carry types through the network, state no legality rule for mixing, provide no audit of other models, and return point estimates with no null space. Our claim is a discipline plus a field-level measurement, not a reconstruction pipeline. |
| **EBFI-BE**, *Blurry Frame Interpolation under Blind Exposure* (CVPR 2023, code) | Estimates the unknown exposure prior from events | Closest on "the support is unknown and must be inferred" — but it infers one scalar $T$ for one task. We type every tensor at every layer and constrain every operation. |
| **AKF / Asynchronous Linear Filter for hybrid event-frame cameras** (arXiv 2309.01159, 2023) | A state updated asynchronously with per-modality observation models; HDR reconstruction | The classical, correct version of `lift`+`render` — and the honest answer to "hasn't someone done this?" It is a hand-built filter for one task, with no learning-time discipline, no identifiability analysis, and no diagnostic applicable to learned architectures. |
| **Change-of-support problem (COSP)** — geostatistics / remote-sensing data fusion (Cressie; INLA-SPDE point-grid fusion, 2025) | Fuses observations with different spatial/temporal *supports* through a latent field and per-source observation operators | The mathematical ancestor, and to our knowledge never posed for event–RGB vision. COSP handles differing *resolution* of same-order observables. Here the **orders differ (0 vs 1)** and the **photometric domains differ**, for which COSP has no machinery. Importing and extending it is part of the contribution. |

**Honest verdict.** No work we found claims a support/type discipline for asynchronous perception, a support-identifiability theorem for the (frame, event-bin) pair, a null-space regularizer, or an audit of published RGB–event models. The *mechanism* (shared continuous latent) is well-trodden; the *principle, the legality rules, and the diagnostic* appear open. **Next idea if this is taken:** invert the framing entirely — instead of typing the network, redesign the *sensor pairing*: derive, from the identifiability theorem, the optimal exposure schedule and event-bin edges that make a stated task identifiable, and validate that a support-optimal capture protocol beats a support-typed network on the same data ("stop fixing the network, fix the shutter").

---

## Experimental plan

### Architectures we diagnose (code and weights located)

| Model | Venue | Repo | Weights | Data |
|---|---|---|---|---|
| EFNet | ECCV'22 | `AHupuJR/EFNet` | Google Drive (GoPro, REBlur) | GoPro+events, REBlur |
| RENet | ICRA'23 | `ZZY-Zhou/RENet` | provided | DSEC-MOD (13,314 frames) |
| FRN | ECCV'24 | `HuCaoFighting/FRN` | Google Drive (DSEC, DDD17) | DSEC-Det, PKU-DDD17-Car |
| CEUTrack | CVPR'23 | `Event-AHU/COESOT` | Baidu (risk) | COESOT |
| SODFormer | TPAMI'23 | official | check | PKU-DAVIS-SOD |
| BRENet | 2025 | `zyaocoder/BRENet` | check | DSEC/DDD17 segmentation |
| EvUnroll | CVPR'22 | `zxyemo/EvUnroll` | Google Drive | Gev-RS (RS + events) |

Target: **≥4 models fully diagnosed** (EFNet, RENet, FRN, + one of CEUTrack/BRENet); the rest are bonus rows. Each gets its own Docker image; no host installs.

### Data (disk budget ≤ 200 GB of 990 GB free)

- **Controlled simulator (0 GB download, ~20 GB generated).** Procedural 2D/2.5D scenes rendered at 10–20 kHz; frames formed by *exact* integration over a chosen $[t_0,t_0{+}T]$; events by exact log-threshold crossing, then re-generated with **v2e** and **DVS-Voltmeter** (both pip/Docker-installable) for sensor realism. Supports are known to machine precision. This carries Panels A/B at controlled $s$, the identifiability sweep, and the support-blind pairs. *This is the first week's work and the paper's spine.*
- **DSEC / DSEC-Det (~40 GB subset).** Ten sequences rather than the 341 GB full train split. Provides real events, real 20 Hz RGB, GT optical flow, and — critically — `image_exposure_timestamps_*.txt`, so $\tau_F$ is measured. Carries Panels A/B/C on real data.
- **PKU-DDD17-Car (~10 GB)**, **GoPro+events / REBlur (~25 GB)** for EFNet.
- **COESOT (105 GB test split, or a ~20 GB 100-video slice)** — Baidu-hosted; treat as optional.
- **Gev-RS** for per-row supports; fallback is to simulate rolling shutter from high-fps video ourselves (which is how Gev-RS was made).

### Baselines

Each published model, unmodified, is its own baseline. For the operator: (i) original block; (ii) original block + causal-tube mask only (isolates R5 from R3/R4); (iii) original block + a naive learned temporal-offset alignment (the field's own prescription — shows alignment does not fix a type error, the empirical counterpart of Prop. 1); (iv) full `SupportAttention`; (v) + null-space regularizer.

### Metrics

Standard task metrics (mAP, PSNR/SSIM, mIoU, AUC/PR) **stratified by $s$**, plus invented:
- **EU$(s)$** — event utility vs. speed (the headline curve).
- **OSAM / acausal mass / TM** — off-support attention mass, attention on non-intersecting bins, $W_1$ temporal misrouting; attention-based *and* Jacobian-influence variants.
- **SII** — support-inconsistency index: per mixing site, the pair (order-mismatch flag, $W_1(\hat\mu_1,\hat\mu_2)/T$, domain-mismatch flag), aggregated by downstream compute share. The scientific claim is the *cross-model correlation*: models with larger type distance at their first mixing site degrade faster with $s$ (target $\rho>0.7$ over ≥5 models).
- **SBP score & SBP-ECE** — accuracy and calibration on provably ambiguous support-blind pairs; a well-typed model should be at chance *and* say so.
- **Null-space sensitivity $\mathcal R$** and **certified interval width / coverage**.

### Ablations

(i) types on/off; (ii) exact projection vs. learned lift; (iii) tube mask alone; (iv) **bin-count sweep $B$** to test the $\dim\mathcal N=d-B-1$ prediction and derive the *minimum bin count* a task needs at a given speed — then show published configurations sit below their own requirement; (v) null-space regularizer vs. SBP; (vi) real recorded exposure vs. assumed instantaneous timestamp (Panel C).

### Compute (one shared RTX 5090, ~9 GB usable, Docker)

| Item | Cost |
|---|---|
| Simulator generation (CPU-bound) | ~10 h CPU, <2 GB VRAM for v2e |
| Diagnostics: 6 models × 4 datasets, inference + hooks, batch 1–4 | ~30 GPU-h, peak ~5 GB |
| Support-blind pair evaluation | ~3 GPU-h |
| Operator fine-tune, EFNet (256² crops, batch 4, AMP) | ~35 GPU-h, ~7 GB |
| Operator fine-tune, FRN (640×480, batch 2, AMP + grad ckpt) | ~40 GPU-h, ~8.5 GB |
| Ablations (short schedules from released checkpoints) | ~20 GPU-h |
| **Total** | **≈ 140 GPU-h ≈ 7–9 days wall on a shared card** |

No model is trained from scratch; everything fine-tunes from released checkpoints. Schedule: W1 simulator + Panels A/B on 3 models (this alone is a paper); W2 support-blind pairs + identifiability sweep; W3 operator; W4 real-data DSEC validation + Panel C.

---

## Risks

**Death 1 — "This is just a new fusion module."** The single most likely rejection, and the user has forbidden exactly this paper.
*Mitigation:* the operator gets ≤1.5 pages, no leaderboard table in the main paper, and an explicit statement that it does not win on average. The main results are the cross-model tables (EU$(s)$, OSAM, SII, SBP over 5–6 published architectures) and the two propositions. The abstract's last sentence is a claim about the field, not about our numbers.
*Fallback:* delete the operator to supplementary and submit as a measurement-theoretic **audit** paper — "what are RGB–event fusion models actually mixing?" — which stands on the diagnostics alone.

**Death 2 — the phenomenon does not appear.** DSEC drives at urban speeds with ~1 ms exposures; displacement during exposure may be too small for EU$(s)$ to invert, and the curve flattens instead of falling.
*Mitigation:* do not rely on driving data for the headline. Force the regime in the simulator (exact control of $s$) and on genuinely fast real data — REBlur, FE240hz, BS-ERGB — rather than DSEC; use DSEC for Panel C, where the auto-exposure effect does not need high speed.
*Fallback:* the **support-blind pair** result cannot fail. It is a construction plus a theorem; it only requires that published models be deterministic and confident, which they are by definition. If Panels A and B both soften, the paper becomes "event–RGB fusion is provably non-identifiable on a constructible family, and every published model answers it confidently" — still a field-level statement.

**Death 3 — "the type system is bookkeeping; of course the null space is large; so what."** A hostile reviewer calls Prop. 1 a two-line triviality and $\mathcal N$ an unsurprising infinite-dimensional set.
*Mitigation:* triviality of the proof is a feature only if the field visibly violates it — so the paper must *show* the violation in published code, by name, with numbers, not argue it. And make identifiability **actionable**: the $B$-sweep turns $\dim\mathcal N=d-B-1$ into a design rule ("this task at this speed needs ≥$B^\star$ bins"), and we show shipped configurations under-provision. A rule with a number is not bookkeeping.
*Fallback:* if the theory reads as thin, promote the empirical inversion (EU$(s)$) to the title claim and demote the algebra to the explanatory section.

**Secondary risks.** (a) Several fusion blocks are gates/AdaIN with no softmax — handled by the Jacobian-influence form of OSAM, which we must present as the primary definition, not an afterthought. (b) Baidu-hosted weights (CEUTrack, Gev-RS) may be unobtainable — drop those rows; four models suffice. (c) Six repos means six dependency stacks; the real cost is Docker builds, not GPU. Budget two days for environments and pick the four with the cleanest requirements first.

---

## Self-score

*Scoring direction: higher is better for novelty / feasibility / reviewer-proof-ness; **lower is better for incrementality**.*

- **Novelty — 8/10.** The support-type discipline, the identifiability theorem for the (frame, event-bin) pair, the null-space regularizer, the support-blind pair construction, and the cross-model audit all appear unclaimed. Held back from 9 because the *mechanism* — route both modalities through a shared continuous-time latent — is genuinely well-trodden (E-CIR, UniINR, Neural Image Re-Exposure, AKF), and a reviewer who reads only the operator will see prior art. The novelty lives in the discipline and the diagnostic, and the paper must be written so that is unmissable.
- **Feasibility — 7/10.** Diagnostics are inference-only and cheap; the controlled proof needs no download; DSEC ships the exposure timestamps that make the real-data claim measurable. The genuine risks are engineering breadth (six repos, six Dockerfiles) and dataset logistics, not compute. ~140 GPU-h fits under 9 GB.
- **Reviewer-proof-ness — 6/10.** The strongest and weakest aspect are the same: the paper's value is a claim about other people's models. If EU$(s)$ inverts across four architectures, it is very hard to argue with. If it merely flattens, the paper becomes a formalism paper with a synthetic witness, and R2 will ask for the leaderboard we deliberately refused to chase. Prop. 1 is trivially provable, which cuts both ways.
- **Incrementality — 3/10 (low is good).** It changes what a fusion operation *is* rather than how it is parameterized, and its headline output (an ambiguity certificate) does not exist in the field. The 3 rather than 2 is the honest cost of the operator section, which is the part that most resembles a normal contribution and is therefore the part most likely to be mistaken for the whole.

---

## 한국어 요약

프레임은 노출 구간에 대한 **밝기의 적분(내부 평균, 질량 1, 선형 영역)**, 이벤트 빈은 **로그 밝기의 경계 차분(질량 0의 부호 측도, 두 시점에만 지지)**이다. 둘은 "시간이 어긋난 같은 관측"이 아니라 **형(type)이 다른 관측**이며, 따라서 정합(registration)·워핑·시간 시프트로는 원리적으로 메울 수 없다(명제 1). 그런데 RENet·FRN·CEUTrack·SODFormer·BRENet 등 공개된 RGB–이벤트 융합 모델은 전부 이 둘을 같은 텐서처럼 concat·게이트·크로스어텐션으로 섞는다.

제안: (1) 모든 텐서에 시간 지지(temporal support)를 **타입으로 부착**하고 허용 연산(혼합·비교·lift·render·인과 튜브)을 규정하는 대수/타입 시스템, (2) 기존 공개 모델을 감사하는 진단 지표 — 속도에 따른 **이벤트 효용 역전(EU 곡선)**, **오프-서포트 어텐션 질량(OSAM, 야코비안 기반이라 게이트/AdaIN에도 적용)**, **지지 비일관성 지수(SII)**, (3) 식별가능성 정리와 **support-blind pair**(프레임·이벤트 복셀이 동일하지만 정답이 다른 쌍) — 즉 현재 표현으로는 원리적으로 답할 수 없는데도 모든 모델이 확신에 차서 답하고 있음을 증명. 연산자(SupportAttention)와 널스페이스 정규화는 원리의 최소 시연일 뿐, 리더보드가 목표가 아님.

핵심 리스크는 "결국 새 융합 모듈 아니냐"는 오독이며, 대응은 연산자를 1.5쪽으로 줄이고 본문 주 결과를 **여러 공개 모델에 대한 진단표**로 두는 것. 데이터는 시뮬레이터(다운로드 0GB) + DSEC 부분집합(~40GB, 실제 노출 타임스탬프 제공) 중심, 총 ~140 GPU-h, 9GB VRAM 내 수행 가능.
