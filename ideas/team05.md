# No Offset Can Fix a Width: Temporal Support Calibration for Event–Frame Perception

*Idea Team 5 — CVPR 2027 candidate. Domain: Temporal-Support-Aligned Event–RGB Perception.*

## One-sentence thesis

Frame and event measurements are integrals of the same latent continuous-time radiance against **two different measures on the time axis**, so "temporal alignment" is not the estimation of a scalar delay but the identification of a *pair of temporal support kernels* and of the observable subspace they jointly span — and we prove and measure that the best possible time offset leaves a structured, speed-dependent residual with spectral nulls at $k/(vT)$ that no offset, learned or hardware, can remove.

---

## The assumption we kill

**The assumption.** *The temporal relationship between a frame channel and an event channel is a scalar delay $\delta$, and the frame is a point sample at a single timestamp $c_n$.* Therefore alignment = find $\hat\delta$, add it to one clock, and the two streams describe "the same instant."

**Where it lives, verbatim, in every layer of the field:**

| Layer | How the assumption appears |
|---|---|
| Hardware | A trigger pulse defines *one* time per frame; the event camera records the pulse as a special event. DSEC's microcontroller triggers both at 20 Hz. |
| Dataset convention | DSEC ships `image_exposure_timestamps_left.txt` with exposure **start and end** in µs — and then defines the canonical `image_timestamps.txt` as *"the average of the middle exposures"*, plus a scalar `t_offset` "that must be added to the timestamps of the events." The benchmark itself collapses an interval to its midpoint and reconciles the modalities with one number. |
| Calibration literature | EF-Calib (RA-L'24), eKalibr / eKalibr-Stereo / eKalibr-Inertial (RA-L'25), Kalibr-style continuous-time B-spline calibration: the temporal unknown is a **scalar** $t_d$. |
| Sensor-physics literature | Yang et al., CVPR 2024, the state of the art in event timing: latency is a *per-event shift* $l_\mathbf{p}(\tau)$ parameterized as a polynomial of illuminance. The underlying physics they cite is a **first/second-order low-pass photoreceptor** — i.e. a kernel — and they keep only its **first moment**. |
| Deep fusion | FAOD's "Time Shift" training strategy; NER-Net's learnable event-timestamp calibration; TSANet (CVPR 2026) "time-specialized alignment" by warping features to a query time. Every one of them is a translation on the time axis, only made spatially varying or learned. |

**Why it is universal.** Because it is the only thing you can write down if your representation unit is a *timestamp*. A voxel grid, a time surface, an event frame, an EST — each stores *when*. None of them has a slot for *over what width*, so the only degree of freedom left to "fix alignment" is to slide the index.

**What breaks.** A shift is a unitary operator: in Fourier it is multiplication by $e^{-i2\pi\xi v\delta}$, unit modulus and **linear phase**. Support mismatch is multiplication by $\hat H_F(\xi)/\hat H_E(\xi)$, which has (a) non-unit modulus, **with exact zeros**, and (b) **non-linear phase with $\pi$ jumps** at those zeros. The one-parameter group of linear-phase unit-modulus multipliers cannot contain such an operator. So no $\delta$ — not per-frame, not per-pixel, not per-event, not learned — reduces the disagreement to zero, and the $\delta$ that minimizes it is a *scene- and speed-dependent* quantity masquerading as a rig constant.

The seed statement "frame and event observations do not share the same temporal support under fast motion" is usually read as *the windows are offset*. It should be read as *the windows have different **shapes**, and one of them has zero width*. Offsets are the wrong group.

---

## The failure phenomenon

*Found first, explained second. It is designed to indict the formulation, not a method.*

### Setup (the strongest possible version of the opponent)

Take a rig where the scalar-offset formulation is **true by construction**: a synthetic latent scene $\ell_0$ translating at a known constant velocity $v$, frames rendered as an *exact* box integral over exposure $T$, events generated from the *same* latent at 1 µs resolution with the true offset $\delta^\star = 0$. Nothing is misaligned in the sense the literature means. Then give the offset estimator every advantage: an oracle grid search over $\delta$ at 10 µs resolution, minimizing the cross-modal residual directly.

### Measurement

$$R(\delta; v) \;=\; \big\| \log F \;-\; \Phi_{\delta}\big[\text{latent reconstructed from events}\big] \big\|^2, \qquad \hat\delta(v) = \arg\min_\delta R(\delta;v)$$

with $\Phi_\delta$ the shift-based aligner. Two numbers per speed: the **argmin** $\hat\delta(v)$ and the **residual at the argmin** $R(\hat\delta;v)$.

- **Independent variable:** blur extent $b = vT$ in pixels, swept by varying $v \in \{12.5,\dots,800\}$ px/s at fixed $T$, and independently by varying $T \in \{1,2,5,10,20\}$ ms at fixed $v$. If the phenomenon is a function of $b$ alone, the two sweeps collapse onto one curve — that collapse is itself part of the claim.
- **Controls:** contrast threshold $C$, illumination (which sets the event low-pass $\tau$), scene power-spectrum exponent $\alpha \in \{0,1,2\}$ for $S(\xi)\propto\xi^{-\alpha}$.

### The plot (one figure, three panels)

- **Panel A — the argmin drifts.** $x$: $b$ (px). $y$: $\hat\delta$ (ms). *Expected curve:* a rig constant must be a horizontal line at $T/2$ (the exposure midpoint). Instead $\hat\delta$ drifts monotonically and then jumps once $b$ passes the first sinc null.
- **Panel B — the minimum does not go to zero.** $x$: $b$. $y$: $R(\hat\delta;v)$ normalized by signal energy, on log scale, with the theoretical floor $\mathrm{SMF}(b)$ overlaid, and a third curve: the residual of our support-matched comparison. *Expected:* the shift curve rises and **tracks the floor within a few percent** — i.e., after $b\approx 2$ px, optimizing $\delta$ buys essentially nothing — while the support-matched curve stays flat at the noise floor for all $b$.
- **Panel C — the residual has structure the shift cannot touch.** $x$: spatial frequency $\xi$ (cycles/px) along the motion direction. $y$: residual power, one curve per speed. *Expected:* **notches at $\xi = k/b$ that migrate leftward as $1/b$**, plus contrast inversion (sign flip of the frame's reported gradient) in the bands between consecutive nulls.

### Quantitative predictions (falsifiable, written before the experiment)

1. **Onset.** The first null enters the passband when $b \ge 2$ px ($\xi_1 = 1/b \le \xi_{\text{Nyq}} = 0.5$). Below $b \approx 1$ px nothing happens and the scalar-offset formulation is *correct*; this is why the field has not noticed.
2. **Floor growth.** With $S(\xi)\propto\xi^{-2}$ and negligible $\tau$, the small-$b$ expansion $1-|\mathrm{sinc}(\pi b\xi)| \approx (\pi b\xi)^2/6$ gives $\mathrm{SMF} \propto b^4$; the floor is $<10^{-3}$ of signal energy at $b<0.5$ px, crosses $10^{-2}$ near $b \approx 1.5$ px, and **saturates near $0.2$–$0.3$ for $b>10$ px**. It never returns to the noise floor.
3. **Onset is scene-dependent, not speed-dependent.** The crossover $b^\star \approx 1/\xi_{\text{eff}}$, where $\xi_{\text{eff}}$ is the scene's spectral centroid. Sweeping $\alpha$ moves $b^\star$ by $\ge 2\times$. A rig constant cannot depend on texture; this alone falsifies "offset is a property of the rig."
4. **Offset bias drift.** $|\mathrm{d}\hat\delta/\mathrm{d}b| \gtrsim 0.05\,T$ per pixel of blur over $b\in[1,8]$, so $\hat\delta$ swings by $\ge 0.3\,T$ across the sweep. At $T=10$ ms that is **$\ge 3$ ms of drift on a rig whose true offset is exactly 0** — an order of magnitude above the sub-ms precision EF-Calib/eKalibr-class methods report. The drift is not noise; it is the estimator absorbing a width into a location.
5. **Bias injection.** Repeating with a *known nonzero* $\delta^\star$: the estimator recovers $\delta^\star$ only as $v\to 0$; the error $\hat\delta - \delta^\star$ grows with $b$ following prediction 4. **Calibrating faster makes your calibration worse**, which is the opposite of every calibration protocol's assumption that more motion excites more constraints.

### Why this indicts the formulation and not a method

Every panel is produced with an *oracle* over the shift, on data where the shift model is nominally exact, with an ideal event sensor. There is no estimator to blame, no noise to blame, no hardware to blame. The residual is the distance from the shift group to the operator that actually relates the two channels.

---

## The reformulation

### The unit changes: from a timestamp to a measure

Replace "each observation has a time $t$" with "**each channel is a measure $w(\cdot)$ on the time axis, and an observation is the pairing of the latent field with that measure.**" A timestamp is the degenerate case $w = \delta_t$. The frame channel has $\mathrm{supp}(w_F)$ of width $T$; the event channel has a causal kernel of width $\tau(\bar I)$ followed by a threshold crossing. Alignment is a statement about two measures, and the only shift-invariant thing a shift can change is the first moment.

### State space

Latent per-pixel log-radiance as a continuous-time field
$$\ell(\mathbf{x},t), \qquad \ell(\mathbf{x},\cdot) \in \mathcal{S}_{\Delta} = \text{cubic B-spline, knot spacing } \Delta = 1\text{ ms (controlled: 0.1 ms)}.$$
Under local translation at velocity $\mathbf{v}(\mathbf{x})$, $\ell(\mathbf{x},t)=\ell_0(\mathbf{x}-\mathbf{v}t)$ locally; this is the only structural assumption and it is what converts time into space.

### Forward model (two operators, one latent)

**Frame channel** (linear-domain integration, log-domain readout):
$$F_n(\mathbf{x}) = g\!\left( \int w_F(t-c_n)\, e^{\ell(\mathbf{x},t)}\, \mathrm{d}t \right), \qquad w_F\ge 0,\ \textstyle\int w_F = 1,\ \mathrm{supp}(w_F)\subseteq[-T_n/2,\,T_n/2].$$
Log-linearize: $\log F_n \approx (w_F * \ell)(\mathbf{x},c_n) + \tfrac12 \mathrm{Var}_{w_F}[\ell]$. The second term is the **Jensen gap** — it is exactly the term that makes a best-fit offset content-dependent, and we keep it rather than assume it away. $w_F$ is parameterized as a non-negative low-dimensional spline (box / trapezoid with rise+fall / free 5-knot non-negative spline) with its *scale* locked to the metadata exposure $T_n$ and its *shape* free.

**Event channel** (bandlimited log-domain threshold crossing):
$$\tilde\ell = w_E * \ell, \qquad w_E(t) = \tfrac{1}{\tau}e^{-t/\tau}\mathbf{1}_{t\ge0},\ \ \tau = \tau(\bar I;\,\theta_\tau),$$
$$e_k = (\mathbf{p},t_k,\sigma_k) \iff \sigma_k\big(\tilde\ell(\mathbf{p},t_k)-\tilde\ell(\mathbf{p},t_{k-1})\big) \ge C .$$
Second-order $w_E$ is an ablation. Note that the entire existing latency literature is the statement $w_E \mapsto \delta_{\mathbb{E}[w_E]}$: replace the kernel by its mean.

### The algebra you need: time-convolution becomes space-convolution scaled by $v$

For $\ell(\mathbf{x},t)=\ell_0(\mathbf{x}-vt)$,
$$(w*\ell)(\mathbf{x},c) = (\ell_0 \star w^{v})(\mathbf{x}-vc), \qquad w^{v}(u) \equiv \tfrac{1}{v}\,w(-u/v), \qquad \widehat{w^{v}}(\xi) = \hat w(v\xi).$$
Everything follows from this single identity. Both channels become **spatial** filters whose transfer functions are the *same* temporal kernels *dilated by the speed*:
$$\hat H_F(\xi) = \hat w_F(v\xi) \ \ \big(=\mathrm{sinc}(\pi vT\xi)\ \text{for a box}\big), \qquad \hat H_E(\xi) = \hat w_E(v\xi) \ \ \big(=(1+i2\pi v\tau\xi)^{-1}\big).$$

### What is predicted

Given calibrated $(w_F, w_E)$ and a local speed $v(\mathbf{x})$ estimated from the events themselves (contrast maximization), the model predicts, per pixel and per spatial frequency, **what each channel can and cannot see**:
- the **blind band** $\mathcal{B}(\mathbf{x}) = \{\xi : |\hat w_F(v\xi)| < \epsilon\}$ — a comb at $k/(vT)$, moving with local speed;
- the **sign-inversion band** $\{\xi: \hat w_F(v\xi) < 0\}$, where the frame reports contrast with the wrong sign;
- the **Support Overlap Ratio** $\mathrm{SOR}(\mathbf{x}) = \dfrac{\int \min(|\hat H_F|,|\hat H_E|)^2 S \,\mathrm{d}\xi}{\int \max(|\hat H_F|,|\hat H_E|)^2 S\,\mathrm{d}\xi} \in [0,1]$.

### What "aligned" means now

Not *shift the frame to the events*, and not *shift the events to the frame*. **Render the query through the target's support, and compare only inside the overlap.**
$$\text{aligned}(F_n,\;E) \iff \Pi_{\mathcal{O}}\Big[\log F_n\Big] \;=\; \Pi_{\mathcal{O}}\Big[(w_F * \hat\ell_E)(c_n) + \tfrac12\mathrm{Var}_{w_F}[\hat\ell_E]\Big],$$
where $\hat\ell_E$ is the event-derived latent and $\Pi_{\mathcal{O}}$ projects onto the common observable subspace (complement of both blind bands, and of the event channel's DC null). Calibration no longer returns a number; it returns **a pair of measures and a comparison operator**. Its correctness is not verified by "sync error in ms" — that quantity does not exist in this formulation — but by whether the *predicted* blind band coincides with the *measured* residual spectrum.

### Objective (implementable)

Controlled calibration on a target moving at $J$ known speeds $v_j$:
$$\min_{\ell_0,\,w_F,\,w_E,\,\delta_0} \sum_{j,n} \big\| \log F_{j,n} - \big[(\ell_0 \star w_F^{v_j})(\cdot - v_j c_n) + \tfrac12\mathrm{Var}\big] \big\|^2 \;+\; \lambda \sum_{j,k} \rho\big(\sigma_k C - \Delta(\ell_0 \star w_E^{v_j})\big) \;+\; \mathcal{R},$$
$\mathcal{R}$ enforcing $w\ge0$, $\int w=1$, support length from metadata, and smoothness. Solved in Fourier per motion direction (alternating minimization; each $w$-step is a small non-negative least squares in the spline coefficients). $\delta_0$ is retained as a free scalar so the old model is literally a nested special case, and we report how much of the residual it explains (prediction: almost none beyond $b=2$ px).

### Theorem (informal), and the experiment that measures it

> **T1 (No shift fixes a width).** Let $\mathcal{G}=\{\Phi_\delta\}$ be the group of temporal shifts. For any scene spectrum $S$ with support beyond $\xi_1 = 1/(vT)$,
> $$\min_{\delta}\ \big\|\hat H_F - e^{-i2\pi\xi v\delta}\hat H_E\big\|^2_{S} \;\ge\; \underbrace{\int S(\xi)\,\big(|\hat H_F(\xi)| - |\hat H_E(\xi)|\big)^2 \mathrm{d}\xi}_{\textstyle \mathrm{SMF}(v,T,\tau;S)} \;>\;0,$$
> because a shift is a unit-modulus multiplier and cannot alter a modulus mismatch. **Measured by:** Panel B — the empirical $R(\hat\delta;v)$ against the computed $\mathrm{SMF}$; the claim is that the gap between them is $<5\%$ of $\mathrm{SMF}$ for $b>2$ px.

> **T2 (The best offset is not a rig constant).** The minimizer is the spectrum-weighted group delay
> $$\hat\delta \;=\; \frac{\int W(\xi)\,\phi(\xi)/(2\pi \xi v)\,\mathrm{d}\xi}{\int W(\xi)\,\mathrm{d}\xi},\quad W = S\,|\hat H_F||\hat H_E|,\quad \phi = \arg\hat H_F - \arg\hat H_E,$$
> and $\phi$ contains $\pi$ jumps at $\xi = k/(vT)$. Hence $\hat\delta = \hat\delta(S, v, T, \tau)$: it depends on the *scene* and the *speed*. **Measured by:** Panel A and prediction 3 (moving $b^\star$ by changing $\alpha$ at fixed rig).

> **T3 (Speed-sweep identifiability).** From a single speed, only the product $b = vT$ is observed and the kernel width is confounded with the texture bandwidth ($\hat w(v\xi)\hat S(\xi)$ is one product). From $J\ge2$ distinct known speeds sharing one texture, $\hat w$ is sampled on a *union of dilated grids* while $\hat S$ is common — the dilation breaks the confound and $(w_F,w_E)$ is identifiable up to a common time shift (and, for symmetric kernels, a time reversal). This is the event–frame analogue of multichannel blind deconvolution identifiability. **Measured by:** the identifiability ablation — kernel-recovery error vs. number of speeds $J\in\{1,2,3,5,8\}$; prediction is a sharp drop from $J{=}1$ to $J{=}2$ and a slow tail after.

---

## What existing methods cannot express

Existing representations index time. They therefore **have no symbol for width, and no symbol for "unobservable."** Concretely:

1. **Speed-dependent spectral blindness.** No voxel grid, time surface, event frame, EST, or learned temporal embedding can encode "at this pixel, right now, the frame carries *zero* information at spatial frequencies near $k/(vT)$, and $v$ changes per pixel per frame." The best any of them can do is downweight the whole frame.
2. **Contrast inversion as a signed, systematic error.** Past the first sinc null the frame reports edge contrast with the **wrong sign**. Every fusion module treats the frame as a noisy-but-sign-correct observation, so an $L_1/L_2$ objective *averages a sign-flipped observation with a correct one* — producing a systematic bias, not extra variance. This is invisible to PSNR/SSIM/EPE, which aggregate magnitudes over frequency.
3. **The complementary-nullspace structure.** The frame carries DC (absolute radiance) which the event channel structurally cannot; the event channel carries the comb frequencies which the frame structurally cannot. Their observable subspaces are *complementary in a speed-dependent way*. "Aligning" them is therefore not making them equal — they can never be equal — but computing the intersection. No shift-based formulation can even state this.
4. **A calibration result that is a function, not a number.** eKalibr/EF-Calib report $t_d \pm \sigma$. There is no slot in their output for "the frame's temporal aperture has a 0.8 ms rise time and is not a box," even though that is measurable and changes what the frame means.
5. **Auto-exposure as a time-varying measurement operator.** On DSEC the exposure width swings with illumination *frame to frame*; a fixed learned temporal-shift module is not merely inaccurate, it is estimating a parameter of a model whose true parameter changes every frame. The representation cannot express that its own operator moved.

---

## Why this is not <closest work>

| Work (venue, year) | What it does | The temporal unknown it estimates | Why we differ |
|---|---|---|---|
| **Pan et al., EDI / mEDI** (CVPR'19, TPAMI'20) | Blurry frame = exposure integral of latent; events give ratios. The *ancestor* of our forward model. | **None.** $[\tau-\Delta\tau,\tau+\Delta\tau]$ is assumed a known, exact box on a shared clock. | EDI *uses* the support model to reconstruct; we make the support the **unknown to be calibrated**, prove no shift can substitute for it, and output a validity operator. EDI is a special case of our model at $w_F=$ box, $w_E=\delta_0$. |
| **Yang et al., Latency Correction for Event-guided Deblurring and FI** (CVPR'24) — *closest work* | Per-event latency as a per-pixel polynomial of intensity; EDI made differentiable w.r.t. latency; self-supervised "event temporal fidelity." | A **scalar shift per event** $l_\mathbf{p}(\tau)$ — spatially varying, but still a location. | They cite the photoreceptor low-pass and then keep only its **first moment**. We show the *width* (second moment and beyond) carries the irreducible residual, that a first-moment correction provably cannot remove SMF, and that the frame side has a kernel too — which they assume is a known box. They report PSNR; we report an impossibility bound and a measured OBD on a hardware-synced rig. |
| **Jiang et al., EVS-assisted Joint Deblurring / RS / VFI via Sensor Inverse Modeling** (CVPR'24) | Per-pixel inverse with EVS pixel latency, readout latency, refractory period in the measurement model. | Fixed, *pre-specified* sensor non-idealities. | Closest on modelling richness, but it is a reconstruction pipeline with parameters given, on one hybrid sensor. No calibration problem, no identifiability claim, no impossibility statement, no cross-modal validity mask, and no analysis of what a shift-based aligner does wrong. |
| **EF-Calib** (RA-L'24); **eKalibr / -Stereo / -Inertial** (RA-L'25) | Continuous-time B-spline spatiotemporal calibration of event+frame / event+event / event+IMU. | A **scalar** $t_d$. | This is the assumption, stated in its most rigorous form. Their continuous-time machinery models the *trajectory* continuously while collapsing the *measurement* to a point. We keep their splines and replace the scalar with a measure; T2 predicts their $t_d$ drifts with the speed of the calibration motion — testable against their own protocol. |
| **Tulyakov et al., Time Lens / Time Lens++** (CVPR'21/'22) | Event-guided video frame interpolation; BS-ERGB. | Frames are instantaneous samples at their timestamps. | We do not propose an interpolator. We show that the "target time" the interpolator is asked to hit is not well defined for the frame channel when $b>2$ px, and supply the operator that makes the comparison well posed. |
| **FAOD, Frequency-Adaptive Low-Latency Detection** (arXiv'24) | Names "Event-RGB Mismatch"; Align module + **"Time Shift"** training strategy; robust to 80× frequency mismatch. | A learned shift, enforced by shift-consistency training. | The name is right, the group is wrong. Shift-consistency training explicitly *teaches* the network that the two modalities are related by a translation — by T2 this injects a speed-dependent bias. We predict FAOD-style robustness curves degrade specifically in high-$b$ pixels; that is one of our stratified evaluations. |
| **Sun et al., TSANet: Time-Specialized Event-Image Alignment** (CVPR'26) | Relative-time-encoded attention + timesurface dynamic warping to align features at a query time. | A learned per-feature **warp** to a query time. | The most recent restatement of the assumption: alignment = get features to the right *instant*. It has no way to represent that at that instant, the frame's information at some frequencies does not exist. Our blind-band mask is exactly the missing object; TSANet is a natural consumer of it. |
| **Zhang et al., Generalizing Event-Based Motion Deblurring** (ICCV'23) — EGER | Exposure-Guided Event Representation: exposure interval selects/indexes the events used for an arbitrary target latent image. | Exposure as an **index range**. | The closest anyone comes to letting $T$ into the representation — but as a selection window, not a measurement operator. No kernel, no shape, no identifiability, no notion of what the exposure destroys. |
| **Raskar et al., Coded Exposure Photography** (SIGGRAPH'06) | Box exposure ⇒ sinc nulls ⇒ ill-posed deblurring; flutter the shutter to flatten the spectrum. | — | Our theory's true ancestor, and we say so. But it is a *single-modality* argument about invertibility, and its answer is to change the hardware. We use the same spectral fact to argue about **cross-modal alignment and calibration semantics**, with the event channel as the entity that *does* observe the nulled band — which is what makes the intersection nontrivial rather than empty. |
| **Scheerlinck et al., Continuous-time Intensity Estimation** (ACCV'18) | Asynchronous complementary filter fusing frames and events into a continuous state. | Shared clock; frames are instantaneous. | Continuous in *state*, discrete in *measurement*. Same substitution as EF-Calib, in a filtering rather than calibration setting. |

**Honest assessment of overlap.** The physics (box ⇒ sinc ⇒ nulls; photoreceptor ⇒ low-pass) is textbook and I claim none of it. Two claims are ours: (i) the *reframing of temporal calibration* as identification of a pair of measures, with T1–T3, and (ii) the *measurement* that on hardware-synchronized rigs the best-fit offset is not a rig constant. I found no paper — CVPR/ICCV/ECCV/NeurIPS/ICLR 2023–2026, nor the calibration literature — making either. The CVPR 2026 proceedings contain 60+ event papers and none is about event–frame temporal support or exposure-aware calibration.

**If it turns out to be taken, the next idea:** invert the direction — *design* the frame channel's temporal support (a coded/fluttered exposure driven by the event rate itself, closing a loop between the two sensors) so that the two channels' observable subspaces are made complementary **by construction**, and calibration becomes a decoding problem with a guarantee. Same algebra, different half of the problem, and it survives even if the diagnostic half is scooped.

---

## Experimental plan

### Data

| Tier | Data | Size / risk |
|---|---|---|
| **Sim-A** (theory ⇒ measurement) | Procedural latents: gratings sweep, slanted edges, textures with $S\propto\xi^{-\alpha}$, $\alpha\in\{0,1,2\}$; plus high-FPS real video (GoPro 240fps, X4K1000FPS, Need-for-Speed 240fps) as latent. Frames = exact box integrals; events from (a) ideal thresholding, (b) **v2e** (has an explicit configurable photoreceptor low-pass), (c) **DVS-Voltmeter**. | Generated on disk, <100 GB. **Zero availability risk.** $T$, $\delta^\star$, $v$, $\tau$ are set as known independent variables — this is the point of simulating. |
| **Real-B** (the "perfect sync still fails" test) | **DSEC**, 5–6 sequences chosen to span auto-exposure range (bright interlaken + night/tunnel zurich_city). Per-sequence 2.4–13 GB; **~50 GB total**, well under 990 GB free. Uses the shipped `image_exposure_timestamps_*.txt` (exposure start/end in µs) — the key asset. Secondary: **MVSEC** (smaller, ROS bags, hardware synced). | Low risk; direct HTTP download, no form. |
| **Real-C** (large blur, deliberate) | **EventAid-B** (blurry + sharp + events, 3-camera beam splitter; 10 groups / 7,436 frames) and **BS-ERGB** (Prophesee Gen4M + FLIR, Time Lens++). | Medium risk: BS-ERGB is behind a request form; EventAid via project page. Fallback: Sim-A + Real-B suffice for every claim; Real-C only strengthens the downstream tier. |
| *Not used* | GEN1/1Mpx, N-Caltech, EventVOT — no frame channel with exposure metadata, so irrelevant here. State this explicitly in the paper to preempt "why not more datasets." |

### The controlled variable

$b = vT$ (blur extent, px), swept two independent ways ($v$ at fixed $T$; $T$ at fixed $v$) precisely so we can show they collapse. Secondary sweeps: $\tau$ via illumination, $C$, scene spectral slope $\alpha$, true offset $\delta^\star$.

### Baselines (real, named, run — not cited)

**Offset/latency estimators.** (E1) event-count-image ↔ frame-gradient cross-correlation (the standard practice); (E2) EDI-sharpness offset search (Pan et al.); (E3) EF-Calib-style continuous-time B-spline reprojection with free $t_d$ (reimplemented on our targets); (E4) Yang et al. CVPR'24 illumination-polynomial latency (public formulation, reimplemented); (E5) a learned temporal-shift head in the style of FAOD's Time Shift.
**Downstream consumers (unchanged weights, alignment operator swapped).** EDI/mEDI; EFNet (ECCV'22) and REFID/Sun et al. for event-guided deblurring; a DSEC-Flow event–RGB flow model for the mask experiment; TSANet if code lands in time.

### Metrics

*Invented (and why the existing ones are structurally blind):*
- **SMF — Support Mismatch Floor.** $\min_\delta$ cross-modal residual. *Existing metric "sync error in ms" reports 0 on DSEC by construction and can never see this.*
- **OBD — Offset Bias Drift**, $\mathrm{d}\hat\delta/\mathrm{d}b$ [ms/px]. A rig constant must have $\mathrm{OBD}=0$. *Calibration papers report mean±std of $\hat\delta$ over one motion profile, so the drift is aliased into their variance.*
- **NDE — Notch Depth/Location Error.** Distance between measured residual-spectrum nulls and predicted $k/b$ [cycles/px]. *This is the direct measurement of T1; no existing metric is frequency-resolved.*
- **SFA — Sign-Flip Agreement.** Fraction of pixels where the frame's local contrast sign disagrees with the event-derived sign. *PSNR/SSIM/EPE average signed errors and are blind to a systematic inversion.*
- **SOR — Support Overlap Ratio** per pixel; used as the reporting axis for all downstream results.

*Standard, kept for comparability:* PSNR/SSIM/LPIPS for deblurring, EPE for flow — **always stratified by $b$**, because the aggregate number is exactly where the effect hides.

### Ablations

1. **Cause isolation (run first, it is the paper's spine).** Turn off, one at a time: event low-pass ($\tau\to0$), Jensen/log-vs-linear nonlinearity, rolling shutter, refractory period, event noise, $\delta^\star\ne0$. Claim: OBD and SMF **persist with all of them off**, driven by the box width alone. If they do not, the paper's thesis is wrong and we find out in week one.
2. **Identifiability:** kernel-recovery error vs. $J\in\{1,2,3,5,8\}$ speeds (measures T3).
3. **Kernel family:** box / trapezoid / free 5-knot non-negative spline / 2nd-order $w_E$.
4. **Speed source:** oracle $v$ vs. event-derived contrast-maximization $v$.
5. **Simulator transfer:** ideal vs. v2e vs. DVS-Voltmeter vs. real DSEC.
6. **Nested-model check:** how much residual the free scalar $\delta_0$ explains once $(w_F,w_E)$ are in the model (predicted: $\to0$ beyond $b=2$ px).

### Compute (single RTX 5090, ~9 GB usable, Docker only)

| Stage | Nature | Est. GPU-h | Peak VRAM |
|---|---|---|---|
| Sim-A rendering + v2e / DVS-Voltmeter | batched FFT + simulator | 12 | ~4 GB |
| Failure-phenomenon sweeps (all 5 estimators × full grid) | FFT + 1-D grid search, no training | 6 | ~2 GB |
| TSC calibration solver (alternating NNLS in Fourier) | convex substeps | 8 | ~3 GB |
| Real-B DSEC: per-frame $v$ (contrast maximization) + $\hat\delta$ + spectra | dense but shallow | 20 | ~5 GB |
| Downstream swap (EFNet/REFID/EDI inference; optional light finetune, 256² crops, bs 4) | inference-dominated | 25 | ~7 GB |
| Slack / reruns | — | 25 | — |
| **Total** | | **~96 GPU-h (≈4 days on a shared card)** | **<8 GB** |

No training from scratch, no model larger than an existing deblurring backbone at $256^2$/bs 4. The theory tier is CPU-FFT-bound and could run without a GPU at all — which is the point of putting the load-bearing claim there.

---

## Risks

**Death 1 — "This is motion deblurring with new vocabulary. EDI did this in 2019."**
The most likely reviewer response, and it is not unreasonable. *Fallback / preemption:* move the deliverable decisively out of image restoration. The paper's product is (a) a **calibration protocol** whose output is a pair of measures plus a per-pixel blind-band mask, and (b) the **OBD measurement on a hardware-synchronized benchmark** — a number no deblurring paper has ever reported because their formulation has no place to put it. Downstream results are shown *only* as "existing method, unchanged weights, alignment operator swapped, stratified by $b$" so they read as validation, not as a restoration contribution. If reviewers still read it as deblurring, pivot the headline downstream task to **event–RGB correspondence/flow**, where no deblurring baseline exists and the blind-band mask is the only thing on offer.

**Death 2 — the effect is invisible on real data.**
DSEC daytime driving may run exposures of 0.1–1 ms, giving $b<1$ px, below the onset in prediction 1 — the theory would then be *correct and irrelevant*. *Fallback, in the order the negative-result protocol demands:* (i) target night/tunnel DSEC sequences where auto-exposure opens to 5–20 ms and ego-speed is still high; (ii) measure the actual joint distribution of $(T, v)$ across all DSEC sequences *first*, before committing — this is a one-day check on ~50 GB and it decides the paper's real-data story; (iii) fall back to EventAid-B / BS-ERGB where blur is deliberate; (iv) worst case, retreat to OBD only, which needs $\hat\delta$ vs $b$ and no visible notch, and carry the notch evidence entirely in Sim-A. Do not declare the phenomenon absent until three independent checks agree.

**Death 3 — "mundane cause; just model latency like Yang et al. and move on."**
A reviewer attributes the drift to the event low-pass, rolling shutter, or noise, all of which have published first-moment fixes. *Fallback:* Ablation 1 exists precisely to kill this and is scheduled first, not last. The decisive configuration is **global shutter, $\tau=0$, noiseless, $\delta^\star=0$, ideal thresholding** — a setting in which every mundane cause is removed by construction and only the box width remains. If SMF and OBD survive that, the objection is answered by a single row of a table. If they do not survive it, the thesis is false and we stop, four days in, having spent almost nothing.

*(Fourth, acknowledged: the identifiability result could be trivial or false in the nonlinear regime. Mitigation: state T3 only for the log-linearized model, prove it there, and validate numerically in the full nonlinear simulator via Ablation 2. A theorem that holds only in the linearization, honestly labelled, is publishable; an overclaimed one is not.)*

---

## Self-score

| Axis | Score | Harsh justification |
|---|---|---|
| **Novelty** | **8 / 10** | The reframing of temporal calibration from a scalar to a pair of measures, with an impossibility bound and a speed-sweep identifiability result, is not in the literature — I checked CVPR/ICCV/ECCV/NeurIPS/ICLR 2023–2026, the full CVPR 2026 proceedings, and the event calibration line (EF-Calib, eKalibr, latency correction). Docked two points honestly: the underlying physics (sinc nulls, photoreceptor low-pass) is textbook and EDI already contains the forward model. My contribution is what the forward model *means for calibration*, which is a genuinely new question but built from old parts. |
| **Feasibility** | **8 / 10** | The load-bearing claim is a numerical experiment with no training and known ground truth; the whole theory tier could run on CPU. ~96 GPU-h, <8 GB peak, ~50 GB of DSEC, Docker-only, all simulators pip-installable. Docked for the one genuine dependency: the real-data effect size, which is unknown until the $(T,v)$ distribution of DSEC is measured. |
| **Reviewer-proof-ness** | **6 / 10** | The honest weak point. "Isn't this deblurring?" and "the sinc null is from 2006" are both available to a hostile reviewer, and the answer to each takes a paragraph rather than a sentence. Mitigated by three things a deblurring paper cannot produce: an impossibility bound, an identifiability theorem, and OBD measured on a hardware-synchronized benchmark. But a reviewer who does not read past the figures may see blur curves. |
| **Incrementality** | **3 / 10** *(lower is better — this is a "how incremental is it" score)* | It changes the problem definition rather than the architecture, proposes no new backbone, and its main deliverable is a measurement plus an operator. It is not incremental in kind. It scores 3 rather than 1 because the forward model is EDI's and the spectral analysis is Raskar's — the *assembly* is new, the *ingredients* are not. |

**Overall honest read:** the strongest thing here is that the failure phenomenon is guaranteed to exist (it is a consequence of the Fourier transform of a box, not an empirical hope) and can be demonstrated in days at almost no compute cost, on data where the opposing formulation is given every advantage. The weakest thing is that "frames are blurry and events are not" sounds obvious until you notice that every calibration paper in the field still estimates a single number.

---

## 한국어 요약

**핵심 주장.** 프레임과 이벤트는 같은 잠재 연속시간 신호를 서로 다른 *시간축 측도*로 적분한 관측이다. 프레임은 노출폭 $T$의 상자적분, 이벤트는 (거의) 순간 표본이다. 폭이 다른 두 관측은 어떤 시간 이동(offset)으로도 같아질 수 없다 — 이동은 푸리에 영역에서 단위 크기·선형 위상 곱셈이지만, 지지폭 불일치는 크기 불일치(영점 포함)와 $\pi$ 위상 점프를 만든다. 따라서 "정렬 = 지연 추정"이라는 전 분야의 가정이 틀렸다.

**죽이는 가정.** DSEC조차 노출 시작/끝(µs)을 제공하면서 공식 타임스탬프는 "노출 중앙값"으로 뭉개고 이벤트에는 스칼라 `t_offset` 하나를 더한다. EF-Calib·eKalibr는 스칼라 $t_d$를, CVPR'24 지연보정(Yang et al.)은 커널의 **1차 모멘트**만 추정한다. 폭은 아무도 추정하지 않는다.

**실패 현상 (그림 하나).** 오프셋이 진짜로 0인 합성 데이터에서 오라클 오프셋 탐색을 돌리면 — (A) 추정 오프셋 $\hat\delta$가 블러 길이 $b=vT$에 따라 표류하고($T$=10 ms에서 3 ms 이상, 캘리브레이션 정밀도의 10배), (B) 최소 잔차가 0으로 돌아가지 않고 이론 하한 SMF를 따라 올라가며, (C) 잔차 스펙트럼에 $\xi=k/b$의 노치 빗살이 속도에 따라 이동한다. 즉 **빨리 움직일수록 캘리브레이션이 나빠진다.**

**재정식화.** 표현 단위를 타임스탬프에서 **시간축 커널(측도)**로 바꾼다. 등속 운동에서 시간 합성곱이 속도 $v$로 스케일된 공간 합성곱이 된다는 항등식이 전부의 출발점이다. 정렬은 "프레임을 옮기는 것"이 아니라 "**질의를 상대의 지지를 통과시켜 렌더링하고 겹치는 대역에서만 비교**"하는 것. 캘리브레이션의 산출물은 숫자가 아니라 커널 쌍 $(w_F,w_E)$과 화소별 맹점 대역 마스크다. 정리 3개: T1 불가능성 하한, T2 최적 오프셋은 장면·속도 의존, T3 **속도 스윕 식별가능성**(2개 이상 속도면 커널 식별 가능 — 다채널 블라인드 디컨볼루션의 이벤트-프레임 판본).

**실험.** 시뮬(v2e/DVS-Voltmeter, $T,\delta,v,\tau$를 독립변수로 설정) + DSEC 5~6 시퀀스(~50 GB, 노출 타임스탬프 사용) + EventAid-B/BS-ERGB. 베이스라인은 상호상관·EDI·EF-Calib식·Yang et al.·FAOD Time Shift. 새 지표 SMF/OBD/NDE/SFA/SOR. 총 ~96 GPU-h, VRAM 8 GB 미만, 도커만 사용.

**가장 큰 위험.** (1) "결국 디블러링 아니냐" → 산출물을 캘리브레이션 프로토콜과 유효성 마스크로 고정하고 다운스트림은 가중치 그대로 정렬 연산자만 교체. (2) 실데이터에서 효과가 안 보임(DSEC 주간 노출이 짧으면 $b<1$ px) → 첫 주에 $(T,v)$ 분포부터 측정하고 야간·터널 시퀀스로 이동. (3) "평범한 원인" 반박 → 전역셔터·$\tau=0$·무잡음 조건에서도 현상이 남는 어블레이션을 **가장 먼저** 실행. 이 어블레이션이 실패하면 4일 만에 논지를 접는다.

**자체 평가.** 참신성 8, 실현가능성 8, 리뷰 방어력 6, 증분성 3(낮을수록 좋음).
