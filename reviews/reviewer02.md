# Reviewer 02 — estimation theory, identifiability, mathematical correctness

CVPR20 idea-selection round. Specialism: does the mathematics work, and does it do work in the paper.

My standard is not "is the theory deep". It is: **is the proposition true; is it true only under an
assumption the authors did not state; does it license the conclusion drawn from it; and does an
estimator exist that attains what it claims.** I derived every load-bearing claim myself. Three of
them I also checked numerically, and the scripts are reproduced inline in the audit so that anyone
can re-run them in under a minute.

---

## Comparison set

All ten below were fetched and confirmed present in the official proceedings (CVF Open Access,
ECVA, NeurIPS Proceedings) on 2026-09-01. Titles, venues and author lists are as they appear there.

| # | Paper | Venue | What its theory is, and the standard of rigour it met |
|---|---|---|---|
| 1 | **State Space Models for Event Cameras** — Zubić, Gehrig, Scaramuzza | CVPR 2024 (pp. 5819–5828) | A short frequency-domain argument (an event representation built over window `T` is a sampler whose passband scales with `T`; changing `T` at inference aliases) motivating learnable timescales plus an explicit low-pass. Half a page of signal processing, one falsifiable prediction, then an inference-frequency sweep that confirms it (3.76 mAP drop vs >20 for RNN/transformer). **This is the CVPR bar: theory sized to one prediction, and the prediction is the experiment.** |
| 2 | **Motion-prior Contrast Maximization for Dense Continuous-Time Motion Estimation** — Hamann, Wang, Asmanis, Chaney, Gallego, Daniilidis | ECCV 2024 | Contrast maximization with an explicit motion prior; treats the reference time as a *gauge* and marginalizes it by sampling `t_ref` per batch, rather than asserting a canonical instant. The theory is the loss; validation is EPE on real benchmarks. Relevant precedent: the field already knows the reference instant is arbitrary and already has a principled fix. |
| 3 | **Adaptive Bounding Box Uncertainties via Two-Step Conformal Prediction** — Timans, Straehle, Sakmann, Nalisnick | ECCV 2024 | Split-conformal coverage for a two-stage detect-then-localize pipeline. Guarantee stated *with its exchangeability hypothesis explicit*, and always reported as a coverage–efficiency pair, never coverage alone. This is the rigour standard any coverage claim in this round must meet. |
| 4 | **BeNeRF: Neural Radiance Fields from a Single Blurry Image and Event Stream** — Li, Wan, Wang, P. Wang, Zhou, Liu | ECCV 2024 | The exposure integral and the event double integral used *as the supervision*, with the intra-exposure camera trajectory as an explicit latent. The forward-model derivation earns its column inches because it literally is the loss — the test every "we derive the image formation" section in this round should be held to. |
| 5 | **Latency Correction for Event-guided Deblurring and Frame Interpolation** — Yang, Liang, Yu, Chen, Ren, Shi | CVPR 2024 (pp. 24977–24986) | A parametric per-event latency model made differentiable inside EDI. One equation of theory; the paper is then judged on PSNR. Demonstrates that at CVPR a *first-moment* timing model is publishable, which is exactly the claim Team 5 wants to overturn. |
| 6 | **Ev-3DOD: Pushing the Temporal Boundaries of 3D Object Detection with Event Cameras** — Cho, Kang, Kim, Yoon | CVPR 2025 (Highlight, pp. 27197–27210) | No theorem; a benchmark whose high-rate ground truth is constructed by interpolation and then defended in the text. The standard for how a new temporal GT must be documented — and the source of the 53.6→33.3 mAP "online" gap that Team 8 correctly identifies as an unnamed timing gap. |
| 7 | **Adaptive Spatial-Temporal Window: Unlocking the Potential of Event Cameras in Heterogeneous Velocity Scenarios** — Sui, Hao, He, Lee, W. Wang | CVPR 2026 | Per-patch adaptive windows with a clamp, plus the HetVel benchmark. Confirmed real. This is Team 3's and Team 9's declared nearest neighbour, and Team 9's decisive experiment is defined against its published hyperparameters — so its existence matters to this round. |
| 8 | **Time-Specialized Event-Image Alignment for Blur-to-Video Decomposition** — Sun et al. | CVPR 2026 (pp. 18827–18836) | Confirmed real; this is the paper Teams 3 and 5 refer to as "RTEA"/"TSANet". Relative-time-encoded attention: alignment as a *distance between indices*. Both teams' positioning against it is factually sound. |
| 9 | **Identifiability Guarantees for Causal Disentanglement from Purely Observational Data** | NeurIPS 2024 | What an identifiability theorem looks like when it *is* the contribution: assumptions enumerated up front, a counterexample showing necessity, and an estimator proved to attain the guarantee. Not a CVPR standard — but it is the standard against which I judge whether an identifiability claim in this round is load-bearing or ornamental. |
| 10 | **On the Parameter Identifiability of Partially Observed Linear Causal Models** | NeurIPS 2024 | Same role. Note the calibration datum: **CVPR 2026 accepted 4042 papers and exactly zero have "identifiab*" anywhere in the title**, while seven have "conformal". Identifiability is not a CVPR currency; a coverage guarantee is. Any team leading with an identifiability theorem is spending its first page on something this venue does not reward unless the theorem changes what is measured. |

---

## Per-idea verdicts

| Team | Verdict | One-sentence reason |
|---|---|---|
| **01** — Latent Exposure Support | **BORDERLINE** | The non-identifiability "proof" is a reparameterization tautology (`(t0,T)` vanish because the substitution was defined to remove them), and the derived claim that TSB "is present at the optimum and cannot be trained away" is false for a predictor that also sees events. |
| **02** — Exposure-Occupancy Measures | **REJECT** | Headline Prediction 1 ("at `ν=0, β=3`, `D<0.05`") evaluates to `D = 1.0` under the team's own definition of `𝒜` and `D`, destroying the reframing that acceleration rather than blur governs label well-posedness; two further load-bearing propositions are also wrong. |
| **03** — Temporal Support Fields | **REJECT** | The frame-branch support is not identifiable: `B(x) = Σ_k ŝ^F_k Î(x,τ_k)` is **one** equation in `K` unknowns per pixel, and event count enlarges knowledge of the basis, not the number of equations — so the rescue offered against their own Death 3, and the real-data self-supervision offered against their own Death 2, both fail. |
| **04** — Effective Timestamp `τ̂` | **BORDERLINE** | The identifiability proposition (spatial/temporal offset confounded at constant velocity, separated at order `‖a‖Δt²`) is correct and load-bearing, but the "law" `ŷ ≈ y*(t̄) regardless of the label clock` is not derivable — the evidence centroid governs prediction *variance*, not *bias*. |
| **05** — No Offset Can Fix a Width | **REJECT** | Theorem T2's closed form has a sign error and the wrong spectral weighting; evaluated, the team's own formula returns an offset that is **independent of blur extent**, i.e. it predicts `OBD = 0`, the exact negation of the paper's headline real-data measurement. |
| **06** — The Exposure Gap / LME | **ACCEPT** | The only entry that has already computed its own numbers, and the only genuine identifiability result *with an attaining estimator* (`G(a)` inversion recovers the per-pixel amplitude, better-conditioned under faster motion) — but the advertised closed form `J = ½Var_W(L)` and the claim `J ≥ 0` are both false as stated, and the headline regression `R ~ P` is an algebraic identity, not a discovery. |
| **07** — Chronofields | **BORDERLINE** | The temporal eikonal `∇_u τ · v = 1` is exactly correct and cleanly derived, and the censoring identification (event = uncensored, frame = interval-censored) is the right formalism — but the headline number (`Δt = −8.3 ms`, "42% of the exposure") is computed in a regime where the object reverses direction mid-exposure, violating the derivation that produced it. |
| **08** — Right Place, Wrong Time | **ACCEPT** | The only entry whose central claim is **over-identified and therefore falsifiable**: one scalar `δ` must simultaneously explain the translation and the scale channels, and the paper tests whether it does; it proposes no method, so it cannot be accused of inventing a metric it wins on. |
| **09** — Change-Time / per-pixel clocks | **BORDERLINE** | `τ = C·N` is correctly the total variation of the quantized log-intensity path, and the monotone invariance is exactly true — but it is true *because the representation discards all timestamps*, and the physical corruption invoked to motivate it (refractory loss, AER saturation) **deletes events**, which is not a monotone time warp and therefore lies outside the invariance group. |
| **10** — Fusion Is Ill-Typed | **REJECT** | Proposition 1 is true, trivial ("mass 1 ≠ mass 0"), and does not license its conclusion — every CNN mixes order-0 and order-1 observables (intensities and gradients) without being ill-typed; the null-space dimension count uses the wrong constraint set; and the "support-blind pair" declared un-failable is separable for any `B ≥ 2` bins. |

---

## Detailed review

### Team 08 — *Right Place, Wrong Time* — **ACCEPT** (my winner)

**Summary.** The paper argues that every event benchmark's ground-truth clock has its own temporal
support kernel `k_G` (GoPro exposure ⊛ RGB-detector latency for 1 Mpx; QDTrack on 20 Hz frames plus a
±50 ms linear interpolation kernel for DSEC-Det; LiDAR sweep ⊛ linear prior ⊛ a VFI network's prior
for DSEC-3DOD), that a predictor has its own `k_P`, and that the resulting error is a *time* projected
onto the *pixel* axis. It re-scores released checkpoints by splitting the box-centre error into
`e_⟂` (px, across the GT tangent) and `δ̂ = e_∥/‖v*‖` (ms, along it), and — the part that makes it a
measurement rather than a re-parameterisation — checks that the translation channel and the box-scale
channel `δ̂_s = log(ŝ/s*)/(d log s*/dt)` agree on one `δ`. E0 (label forensics, 4.7 MB of label files,
zero GPU) asks whether the inter-frame GT of DSEC-Det and DSEC-3DOD is recoverable from its own
interpolation prior.

**Strongest reason to accept.** The two-channel consistency test is genuine estimation theory doing
genuine work. A timing error is a one-parameter perturbation constrained to explain translation *and*
scale *and* (in 3D) yaw simultaneously; a spatial error has 2 or 7 free parameters. That over-
identification is what converts "we chose to call this error a time" into a hypothesis that can fail,
and it is the single strongest piece of mathematics anywhere in this round. Ev-3DOD (CVPR 2025
Highlight) already publishes the 53.61→33.32 mAP online/offline gap; this paper supplies the unit.

**Strongest reason to reject.** Control C3 — "predict `τ̂` from each method's declared temporal support
before measuring it" — is **unrunnable on the primary pool**. RVT-{T,S,B} all use
`stacked_histogram_dt=50_nbins=10`, and the paper itself notes that `ssms_event_cameras` consumes the
identical preprocessed tarballs and is built on the RVT codebase. So all five detection checkpoints
share one `w_P = 50 ms`. A predictor with zero variance cannot discriminate the method-level component
from the dataset-level component, which is exactly what Death 3 requires C3 to do. See "My winner and
its fatal flaw".

**Factual errors.**
- §4, "By construction `AP ≤ AP^sync ≤ AP^⟂ ≤ AP^iso`." `AP^sync ≥ AP` is **not** by construction:
  `AP^sync` re-anchors every box by `−τ̂_P·v̂_pred` with `v̂_pred` estimated from the method's own noisy
  consecutive outputs. A wrong `τ̂` or a noisy `v̂` makes `AP^sync < AP`. *Correction:* only
  `AP ≤ AP^⟂ ≤ AP^iso` is by construction; `AP^sync` must be reported as an empirical result, and its
  falling below `AP` is informative rather than a bug.
- §4/C1, "Null model (relaxation is just 'loosen IoU') gives `R ≈ 0.5`." The 0.5 is correct for the
  *per-pair* statistic `E[cos²θ]` under isotropic 2-D error, and is asserted, not derived, for the
  *AP-gap ratio*. The set of detections rescued by a 1-D relaxation is not half the set rescued by a
  disc of the same radius; the fraction depends on the IoU distribution near threshold. *Correction:*
  compute the AP-ratio null by simulation on the actual score distribution (cheap; it is a re-score),
  and report the per-pair `E[cos²θ]` as the primary anisotropy statistic since that one has a
  derivable null.
- P1's `τ̂ ∈ [−35,−10] ms` is presented as following from the 50 ms window's uniform centroid at
  `t−25 ms`. The verified machine facts explicitly warn that whether the trained network weights the
  ten bins uniformly is unmeasured. *Correction:* state `−25 ms` as the uniform-weight reference point
  and pre-register the interval as a hypothesis about the network, not as a derived quantity — which
  is what C3 is for, and which is why C3's unrunnability matters.

**Claims whose strength exceeds their evidence.**
- *"a straight line through the origin whose slope is that method's latency in milliseconds"* — the
  regression `e_∥ ~ τ·‖v*‖` is errors-in-variables. `‖v*‖` is finite-differenced from 4 Hz (Gen1) or
  10–20 Hz labels; classical attenuation shrinks the slope by `Var(v)/(Var(v)+σ_v²)`. The reported
  `τ̂` is therefore a *lower bound in magnitude*, and the bias is worst in the low-speed bins where
  most of the data lives. Nothing in the plan corrects for it.
- *"the temporal hypothesis is testable, not assumed"* — true, and the paper's best sentence, but the
  test's power is unquantified. `δ̂_s` requires `d log s*/dt ≠ 0`, i.e. approaching objects only; on
  laterally-crossing traffic the second channel is absent and the claim reverts to untested.
- *"`τ_max` is not a free parameter"* — `w_G` for Gen1 is "the ATIS integration width", which is
  per-pixel and intensity-dependent and is not published as a number. For that dataset `τ_max` **is**
  a free parameter under a different name.

**The experiment a hostile reviewer would demand.** A pool of checkpoints with *deliberately different*
`w_P` on one dataset — e.g. RVT retrained at `dt ∈ {10, 25, 50, 100} ms` — showing `τ̂ ≈ −w_P/2`.
Its absence is **not fatal** (it is ~8 GPU-h of retraining on Gen1 at 240×304, well inside budget) but
it is *mandatory*, because without it C3 has no predictor variance and Death 3 is unanswerable.

**Required fixes, most important first.**
1. Retrain 3–4 RVT variants at different `dt` to give C3 a non-degenerate predictor. Without this the
   paper measures datasets, not methods.
2. Correct the errors-in-variables attenuation in `τ̂` (Deming regression or an instrumental variable
   from the scale channel), and report the attenuation factor.
3. Drop "by construction" from the `AP^sync` link; report `Δ_clock` with its sign.
4. Compute the isotropic null for `R` by simulation rather than asserting 0.5.
5. Run E0 first and publish it standalone-ready; it is the only result immune to every objection above.

---

### Team 06 — *The Exposure Gap* — **ACCEPT**

**Summary.** The paper observes that `log B_k = LME_{W_k}(L) ≠ L(t_k)` where `LME_W(f) = log((1/|W|)∫_W e^f)`,
so the universal event–frame bridging identity `Δ log I = c·E` is misspecified by a deterministic term
`J`, not corrupted by noise. It regresses the measured residual `R` against a zero-free-parameter,
events-only predictor `P` built from the same `LME`, reports slope 0.955 / R² 0.78 with every sensor
non-ideality switched *off*, and proposes both a one-line training-free fix (quadrature inside the
exponential) and a threshold-invariant supervised target `φ` (the normalized cumulative event profile)
whose amplitude is recovered by inverting `G(a) = log M_{k+1}(a) − log M_k(a)`.

**Strongest reason to accept.** The `G(a)` inversion is the only identifiability result in this round
that arrives **with an estimator that attains it**, and it says something non-obvious and
counterintuitive: two exposure functionals determine the per-pixel amplitude `a_p = c_p·E_p`, and the
conditioning *improves* with motion. That is a real theorem doing real work, and it is the one thing
here a restoration paper cannot produce. The team has also already run its own numbers on CPU, which
is worth more at this stage than any other team's promises.

**Strongest reason to reject.** The headline "failure phenomenon" is an algebraic identity, not a
measurement. Substituting `log B_k = L_ref + LME_{W_k}(cE)` into

```
R = c(E(t_{k+1}) − E(t_k)) − (log B_{k+1} − log B_k)
```

gives, with no approximation,

```
R = [cE(t_{k+1}) − LME_{W_{k+1}}(cE)] − [cE(t_k) − LME_{W_k}(cE)] ≡ P
```

`R = P` exactly for an ideal sensor. The reported slope 0.955 and R² 0.779 are therefore not evidence
that the residual is structured — they are a measurement of the event quantisation noise separating
the quantised `E` used to build `P` from the true `L` used to build `B`. The "noise null (random
regressor) R² = 0.0015" is not a control: no regressor explains an identity except the identity. This
is a presentation failure of the single most prominent claim in the document.

**Factual errors.**
- §"What breaks": *"To second order `J_k = ½·Var_{W_k}(L) + O(κ₃)`"*. The cumulant expansion gives
  `LME_W(L) = E_W[L] + ½Var_W(L) + κ₃/6 + …`, hence
  `J = (E_W[L] − L(t_k)) + ½Var_W(L) + O(κ₃)`. The stated form silently drops the first-order term,
  which vanishes only when `t_k` is chosen so that `E_W[L] = L(t_k)` — true for linear `L` at the
  midpoint, false in general, and **first-order dominant** on precisely the non-monotone trajectories
  the paper headlines as its zero-net-event case. Numerically, for `L(t) = −t²` on `[−1,1]` with
  `t_k = 0`: first-order term `−0.3333`, `½Var = +0.0444`, total `−0.2889`, exact `J = −0.2919`.
- §"What breaks" and P4: *"`J_k ≥ 0`"* and *"Because `J ≥ 0` always, the frame reads systematically
  brighter"*. **False.** Jensen gives `LME_W(L) ≥ E_W[L]`, not `LME_W(L) ≥ L(t_k)`. The same
  counterexample gives `J = −0.292 < 0`. *Correction:* `J ≥ 0` holds iff `L(t_k) ≤ E_W[L]`; the
  unconditional sign claim, and P4's predicted signature, must be restated as conditional on the
  trajectory's convexity over the window.
- §"Identification": `φ` is defined with `φ(t_k) = 0`, `φ(t_{k+1}) = 1`, but `M_k(a)` integrates over
  the exposure `W_k`, which straddles `t_k` and therefore samples `φ < 0`. The parameterisation is
  inconsistent with its own integration domain. Fixable by defining `φ` on `[t_0^{(k)}, t_1^{(k+1)}]`.

**Claims whose strength exceeds their evidence.**
- *"this recovers the per-pixel contrast threshold from the exposure integrals"* — `G` identifies
  `a_p = c_p·E_p`. Splitting it into `c_p` requires dividing by the *observed* event count `E_p`,
  which the paper itself documents as rate-dependently depleted by the refractory period (0.26→0.37
  over 32 px of blur). So the recovered quantity is an *effective* threshold that absorbs exactly the
  event loss the paper cites as known prior art. The claim as written promises the physical threshold.
- *"on textured content the residual is 2.6 contrast thresholds and 99% of it is the exposure operator"*
  — this is the identity again, measured on the team's own unshared simulation. It needs the real-data
  EGR distribution on DSEC before it can be stated.
- P6's numbers (0.0% / 51.0% / 91.2%) are reported to three significant figures from a simulation
  whose configuration is not in the document.

**The experiment a hostile reviewer would demand.** The real-data EGR distribution: run `R ~ P` on
DSEC using the published per-frame exposure windows, with no ground truth, and report `|J|/c` per
sequence. Its absence **is fatal** — without it the paper is a simulation study of an identity.
Fortunately it is the cheapest experiment in the entire round (events + two frames + the exposure
file), and the verified machine facts confirm the exposure file exists and is downloaded.

**Required fixes, most important first.**
1. Restate the failure phenomenon as *Proposition (`R = P` exactly)* followed by the empirical
   question *how large is `J` on real data*. Delete the random-regressor null; it is vacuous.
2. Correct `J = (E_W[L] − L(t_k)) + ½Var_W(L) + O(κ₃)` and drop the unconditional `J ≥ 0`.
3. Run the DSEC EGR measurement in week 1, before anything else.
4. Rename the recovered quantity "effective per-pixel amplitude" and state the `E_p` depletion caveat.
5. Fix the `φ` domain.

---

### Team 04 — *When Is Your Prediction?* — **BORDERLINE**

**Summary.** Introduces the effective timestamp `τ̂ = argmin_t d(ŷ, y*(t))` over a continuous GT
trajectory, plus `TEF = 1 − r_min/r_q`, and predicts that the temporal bias `b = E[τ̂ − t_q]` is
non-zero, speed-independent, content-driven, and — the kill shot — spatially *dispersed* (`σ_τ > 0`)
so that no scalar clock correction exists. It names event–RGB fusion a change-of-support problem and
correctly identifies FAOD's shift-invariance training as the disease presented as the cure.

**Strongest reason to accept.** §4.4 is the best-written null-result specification in this round: it
states in advance what a null looks like, names the confound (blur magnitude and temporal displacement
are correlated by construction), specifies the anti-diagonal control at constant `v·T_exp`, and — the
part that shows real estimation-theoretic literacy — notes that `τ̂` is *unidentifiable* on
constant-velocity segments because a spatial shift and a temporal shift coincide there, then requires
an identifiability margin (curvature of the agreement curve at the argmin) to be reported with every
measurement. That is exactly the discipline this round otherwise lacks.

**Strongest reason to reject.** §4.1's "law" is not derivable. The claim is
*"the Bayes-optimal deterministic predictor is `ŷ = E[y*(t_q)|F,E]` … For locally linear motion,
`ŷ ≈ y*(t̄)`, hence `τ̂ ≈ t̄`, regardless of the label clock used in training."* The second sentence
does not follow from the first. For linear motion with the trajectory identifiable from `(F,E)` up to
noise, `y*(t_q)` is a deterministic function of the trajectory parameters, so `E[y*(t_q)|F,E]` equals
it and `τ̂ = t_q` exactly — no bias. What the evidence centroid `t̄` governs is the *variance*: for a
least-squares fit to evidence at times `{t_i}`, `Var(ŷ(t)) ∝ σ²(1/n + (t−t̄)²/Σ(t_i−t̄)²)`, minimised
at `t̄` and growing quadratically away from it. The paper has converted a variance result into a bias
result. Consequently Figure 2's predicted unit-slope collapse of `r_q` on `(τ̂−t_q)·v` is a hypothesis
about a *sub-optimal* estimator, not a law, and the paper's own ablation 8.5(c) is set up to falsify
its own theory ("Theory: the evidence centroid, weakly pulled by the label" — I predict the opposite).

**Factual errors.**
- §4.1, the derivation as stated. See above. *Correction:* replace "Claim (first-order)" with a
  hypothesis, and add the honest alternative: a bias arises only if the network fails to exploit the
  timing information available in the event branch, which is a capacity/training statement and is
  measurable by comparing against an oracle trajectory fit.
- §4.3 table, *"Speed-dependence of `b`: `|∂b/∂v|·v_range < 0.3·b`"*. If `b` really is set by the
  evidence centroid, then `w(t)` for the frame branch is proportional to the moving object's contrast
  energy deposited per instant, which is itself a function of speed (faster ⇒ energy spread thinner
  and more uniformly). Speed-independence of `b` is therefore not implied by the paper's own
  mechanism; it is an additional assumption.

**Claims whose strength exceeds their evidence.**
- *"a detector whose output does not change when you shift the temporal support is a detector that has
  thrown time away"* — rhetorically strong, and I agree with the intuition, but FAOD's Time Shift
  trains invariance to a shift *of the input window*, not of the query time. Invariance to input-window
  jitter at fixed query time is the correct property. The sentence conflates two different shifts and
  a hostile reviewer will say so in one line.
- *"`σ_τ > 0` is the kill shot: no scalar clock correction exists"* — `σ_τ > 0` is guaranteed by
  estimator noise alone. The paper needs `σ_τ` in excess of the noise floor of the `argmin`, and the
  noise floor is set by the identifiability margin it correctly introduces. The two must be reported
  together or the kill shot is circular.

**The experiment a hostile reviewer would demand.** The frame-only / event-only control (§8.3, item 5).
The paper says so itself and correctly calls it the single most important control. Its absence would
be fatal; its presence in the plan is the reason this is BORDERLINE and not REJECT.

**Required fixes.** 1) Demote §4.1 from "law" to hypothesis and state the variance-vs-bias distinction
explicitly (a reviewer who knows regression will find it in thirty seconds). 2) Report `σ_τ` jointly
with the identifiability margin and the estimator noise floor. 3) Separate "shift of the input window"
from "shift of the query time" in the FAOD framing. 4) Note that the verified DSEC facts give
`T ∈ [118, 14996] µs` — the paper's simulator sweep `T ∈ {0.5…20} ms` brackets real data correctly,
which is a strength worth stating.

---

### Team 01 — *Latent Exposure Support* — **BORDERLINE**

**Summary.** Argues that a blurred frame carries no information about `(t0, T)`, that dataloaders
therefore impose an unfalsifiable convention `α ∈ [0,1]`, and that the resulting Temporal Support Bias
obeys `E[e_∥|d] = (α_model − α_label)·d + O(d²)`; proposes support-parameterized Bézier trajectories
with the exposure interval as a latent, validated in milliseconds against DSEC's published exposure
timestamps.

**Strongest reason to accept.** The "free-lunch" experiment is the best-designed cheap falsification in
the round: estimate one scalar `α̂` per dataset, shift every baseline's prediction by `(α̂−α_model)·d̂`,
zero learned parameters, and see whether ≥40% of the excess error at `d > 15 px` disappears. And SIE
(`|T̂ − T|` in ms against DSEC's published exposure timestamps, never seen in training) is a genuine,
free, real-data validation of the central latent — the only such validation offered by any team.

**Strongest reason to reject.** The central proposition is a tautology dressed as a theorem. Writing
`γ(u) := p(t0 + uT)` and then observing that `t0` and `T` "are gone from the equation" is not a
discovery — the substitution was *defined* to absorb them. The content of the claim depends entirely on
what is assumed known about `p(·)`. If `p` is an arbitrary unknown function, `(t0,T)` is a pure gauge
and the statement is true and empty. If `p` is constrained at all — constant velocity, a known speed
from events or IMU, a smoothness prior — then `γ` determines the affine map and `(t0,T)` **is**
identifiable. The paper's own method relies on the second regime (the event term "breaks both"). So
the honest statement is *identifiability up to the time-affine group, which a second modality or a
motion prior routinely breaks* — which is a much weaker headline than "no information whatsoever".

Worse, the derived consequence is false. §"The failure phenomenon" states TSB *"is a failure of the
formulation, not of accuracy: the supervision target itself is ill-posed, so the error is present at
the optimum and cannot be trained away."* But the target is a state at a label time generated by a
*consistent* convention, and the model's input includes an event stream that resolves absolute time to
microseconds. The Bayes-optimal predictor of `y*(t_label)` given `(F, E)` therefore has zero systematic
`α` offset. TSB, if it exists, is a property of trained models — an empirical bias worth measuring —
not a property of the formulation, and the paper's strongest sentence is its least defensible.

**Factual errors.**
- Fig 1a, *"Also plot the left–right exposure-midpoint difference: prediction ≥ 1 ms on a substantial
  fraction of frames, meaning the stereo pair — and hence disparity GT — is support-inconsistent."*
  **Falsified by the verified machine facts:** measured L/R divergence is median 16–144 µs, max 380 µs,
  i.e. 3× to 60× below the prediction, and two orders of magnitude below the window width. The brief
  states explicitly that an argument resting on L/R divergence rests on the smaller effect.
  *Correction:* delete the prediction; keep only the exposure-*width* argument, which the same facts
  confirm strongly (118 µs to 14996 µs, factor 127, within-sequence 337→4207 µs).
- §"What existing methods cannot express", item 5: *"DSEC literally averages two different exposure
  midpoints into one number."* True but the residual is ≤380 µs against a 50 ms frame period, and the
  published `image_timestamp` matches the average to within 1 µs. Stating it as a defect overstates a
  negligible effect.
- §"The prediction": the claim that the TSB slope is *"essentially independent of the network"* is
  inconsistent with the same section's definition of `α_model` as the model's *learned* implicit
  convention, which is by definition network-dependent (a frame-dominant model → 0.5, an event-dominant
  model → 1). The document asserts both.

**Claims whose strength exceeds their evidence.**
- *"most of what the field calls 'blur difficulty' is a coordinate-system offset"* — rests on a
  bias/variance decomposition not yet run, on a gated dataset.
- *"A gap that looks like appearance/sensor domain shift is a clock-convention shift"* — predicted to
  within 25%, with no pilot.
- *"Prediction: `T̂` within 15% of DSEC's reported exposure"* — over a range spanning 118 µs to 15 ms,
  15% relative accuracy at the short end means ±18 µs from contrast maximisation on driving data. No
  supporting evidence is offered that this is attainable.

**The experiment a hostile reviewer would demand.** Ablation 3 (drop `L_cm`) rendered as a bar chart —
the proposition as an experiment. The plan has it. What the plan does *not* have, and what I would
demand, is the control that separates "TSB is a formulation defect" from "TSB is a trained-model bias":
train the same architecture with labels at `α = 0, 0.5, 1` and show that `α_model` does **not** follow
`α_label`. If it does follow, the headline claim collapses to a measurement of under-training. Its
absence is fatal to the framing, not to the paper.

**Required fixes.** 1) Restate the proposition as identifiability up to the time-affine group and say
what breaks it. 2) Delete the "present at the optimum" claim or support it with the `α_label` sweep.
3) Delete the L/R divergence prediction. 4) Resolve the network-independence contradiction. 5) Gate on
FE240hz availability by day 14 as planned — note that `fe108.dluticcd.com` answered HTTP 416 (i.e. the
host is *up*, contradicting Team 09's "connection refused"), so this is worth five minutes of checking
before anyone plans around a dead host.

---

### Team 09 — *Change-Time* — **BORDERLINE**

**Summary.** Replaces the global second-valued timeline with a per-pixel counting clock
`τ(x,t) = C·N(x,t)`, correctly identified as the total variation of the quantised log-intensity path;
claims exact invariance to monotone time reparameterisation; and derives a per-pixel frame support
width `W(x) = C·N_exp(x)` that is zero on quiet pixels, giving a `1/W` fusion weight from the sensor
model rather than from learning. Two make-or-break predictions (ASTW's clamp elbow at `ρ≈25`; the
`(k,T)` grid separating rate from support) are pre-registered.

**Strongest reason to accept.** `W(x) = C·N_exp(x)` is the cleanest instantiation of "temporal support"
in the whole round: it is measured by counting, it requires no estimation, it has no lag, and it is
*exactly zero* where the frame is a sharp instantaneous reading. That is a real, checkable object, and
the SWC metric (correlate `W(x)` with per-pixel blur severity) is the right falsification. ASTW
(CVPR 2026) and Time-Specialized Alignment (CVPR 2026) are both confirmed real, so the positioning is
factually sound.

**Strongest reason to reject.** The invariance is true and vacuous, and the physical motivation lies
outside the group it claims. `S = {(x,k,p_k)}` contains no timestamps, so of course warping timestamps
leaves it unchanged — the invariance is achieved by deletion. The paper concedes as much when it
reinjects `dτ/dt = C·r(x)` at the head for rate-valued tasks via `v = (dx/dτ)·(dτ/dt)`; the composite
system is then *not* `φ`-invariant, and every task the field cares about (flow in px/s, TTC, velocity)
is rate-valued. Worse: the motivation is that recorded timestamps are corrupted by AER bus saturation
and refractory dead time. Refractory dead time **drops events**. Dropping events changes `N`, hence
changes `τ = C·N`, hence changes `S`. Event loss is not a monotone reparameterisation of time, so it
is not in the invariance group, and the representation is *not* immune to the corruption invoked to
justify it. The strongest-looking argument in the document is the one that does not hold.

**Factual errors.**
- §"What breaks": *"A `B`-bin voxel grid over `T` seconds has temporal quantization error `C·R·T/B`."*
  `R` is defined as the *global* event rate; the per-pixel quantity requires the per-pixel rate `r(x)`,
  giving `C·r(x)·T/B`. The formula as written is off by the number of active pixels. (Two paragraphs
  later the fixed-count analysis correctly uses `C·n·r(x)/R`, so this is a slip, not a misunderstanding.)
- §"The frame": *"Where `W(x) = 0`, `μ_x = δ_0` and `B(x) = exp(L̃(x,0))` exactly."* Not exactly —
  `W(x)=0` means the log-intensity moved by less than one threshold `C`, so the identity holds to
  `O(C)`, which is the same `O(C)` bound the paper carefully states two paragraphs earlier. Say `O(C)`.
- §"The frame": *"There is nothing to align, and the alignment cost must be exactly zero."* `W(x)=0`
  means *no photometric change*, not *no motion*. A moving textureless surface (the aperture problem)
  emits no events while the semantic content at that pixel changes completely. The derived `1/W`
  weighting will therefore place maximum trust in the frame exactly in the regions where the frame is
  most semantically ambiguous. This is a real defect in the fusion weight, not a caveat.
- §4.1: `CDR = Δt_max/Δt_min = 25` is presented as *"predicted from their published hyperparameter
  table, not fitted."* The elbow location also depends on where the `ρ=1` operating point sits inside
  `[Δt_min, Δt_max]`, which is set by the absolute event rate the experiment chooses. The ratio bounds
  the *width* of the flat region, not its location.

**Claims whose strength exceeds their evidence.** *"`τ(x,·)` … has no free parameter; `C` is the
sensor's own contrast threshold and only sets a scale."* `C` is per-pixel, illumination-dependent and
rate-dependent — the paper's own §"What breaks" says so. A per-pixel unknown scale is not "no free
parameter"; it is one free parameter per pixel, which is what Team 06 spends its identifiability
result recovering.

**The experiment a hostile reviewer would demand.** Ablation (d): re-inject `Δt` as a feature and show
RIG becomes non-zero. The paper has it. What I would additionally demand is the honest version of the
invariance claim measured end-to-end on a *rate-valued* task with the `dτ/dt` head attached — RIG of
the full system, not of the backbone. Its absence is fatal to the invariance headline.

**Required fixes.** 1) State that the invariance holds for the backbone and is deliberately broken at
the head for rate-valued tasks; report RIG for the full system. 2) Remove the AER/refractory motivation
or explain why event *loss* is inside the invariance group (it is not). 3) Fix `C·R·T/B → C·r(x)·T/B`.
4) Replace "exactly zero alignment cost" with the aperture-problem caveat and re-derive the `1/W`
weight accordingly. 5) Verify the FE108 host before declaring it dead — it answered HTTP 416, and
`rpg.ifi.uzh.ch/timelens++download.html` answered HTTP 200, so the two "dataset is gone" findings that
Teams 06 and 09 report to the round should be re-checked rather than propagated.

---

### Team 07 — *Chronofields* — **BORDERLINE**

**Summary.** Inverts the query: predict a distribution over *when* a queried state held, with events as
uncensored observations, frames as interval-censored ones, and a `∅` atom for "never". Adds a dwell-time
change of variables (EDI with the unknown swapped) and a temporal eikonal regulariser `∇_u τ · v = 1`.

**Strongest reason to accept.** The censoring identification is exactly right and is the best-chosen
formalism in the round: an event is an uncensored crossing time, a frame is a genuine interval
observation, a non-crossing is right-censored. That is textbook survival analysis correctly mapped onto
a physical measurement structure, and it makes the frame's exposure interval a first-class citizen with
no fudging. The eikonal identity is also correct — see the audit — and I verified the derivation.

**Strongest reason to reject.** The headline number is computed outside its own derivation's domain of
validity. §F2 offers `T = 20 ms`, `a = −2 px/ms²`, `v̄ = 4 px/ms` ⇒ `Δt ≈ −8.3 ms`, "42% of the
exposure". But `v̄ = v₀ + aT/2` forces `v₀ = 24 px/ms` and `v(T) = −16 px/ms`: the object **reverses
direction at `t = 12 ms`, inside the exposure**. The dwell density diverges at the turning point, the
first-order treatment that produced `aT²/24` is invalid, and the case is precisely the multi-valued
regime the same document says is a "type error" rather than a bias. The paper's most quotable number is
its least admissible one. Related: the observation that `Δt` *"diverges as `v̄ → 0`"* is presented as
alarming, when it is an artifact of dividing a bounded spatial offset `aT²/24` by a vanishing speed —
the *position* error stays small and the divergent *time* error is unobservable.

**Factual errors.**
- §F1, *"Proposition (constructive, not empirical). … If `δ·v_max < ε` … mAP is exactly unchanged …
  Therefore mAP is invariant to a group of temporal shifts."* Two errors. (i) IoU is continuous in the
  shift, so for any `δ > 0` some detections cross the matching threshold; AP is piecewise constant in
  `δ` and generically changes, though possibly negligibly. "Exactly unchanged" requires the additional
  condition that no matching decision flips, which is a statement about the IoU distribution near
  threshold, not about a tolerance `ε`. (ii) The set of `δ` leaving AP fixed is a neighbourhood of 0,
  not a group — it is not closed under composition. *Correction:* state it as "AP is insensitive to
  shifts small relative to box size", and lean on the constructive two-systems demonstration, which is
  sound and sufficient.
- §F2 numeric example: see above.

**Claims whose strength exceeds their evidence.** *"the events themselves measure the frame's own
effective timestamp — no simulator needed at test time"* via the contrast-weighted barycentre
`t̂(u) = (Σ_k t_k)/N_u`. This is the barycentre of the *event* times at a pixel, which equals the
frame's effective time only under an assumed proportionality between event rate and the frame's
per-instant contribution — the same `w(t)` assumption Team 04 makes and cannot derive.

**The experiment a hostile reviewer would demand.** Time Lens → 1000 fps → RVT versus the chronofield,
head to head, at matched and unmatched compute. The paper names this as Death 1 and pre-registers a
falsification criterion (within 15% of P95 CTE = dead), which is admirable. Its absence would be fatal;
its presence keeps this at BORDERLINE.

**Required fixes.** 1) Re-do the F2 headline with a monotone trajectory inside its validity domain and
report the honest magnitude. 2) Restate the mAP proposition correctly and drop "group". 3) Bound the
`v̄ → 0` divergence by reporting the *position* error, which is what a downstream consumer feels.
4) Run the C1 anchor (held-out real events as µs ground truth) first — it is the only claim here immune
to every simulator objection.

---

### Team 03 — *Temporal Support Fields* — **REJECT** (fatal to the frame half of the idea)

**Summary.** Predicts, per pixel and per modality branch, a sub-probability measure on the time axis —
shape *and* mass — and replaces similarity-based cross-modal attention with an overlap of supports,
enabling abstention ("no valid observation of this pixel at this time"). The failure phenomenon is a
matched-blur/different-support pair (constant-velocity vs dwell-then-dash) on which every covariate the
field regresses against is held fixed and only the support overlap `O*` changes.

**Strongest reason to accept.** The matched-pair construction is genuinely clever experimental design,
and the sub-probability (mass ≤ 1) rather than probability is a correct and load-bearing modelling
choice: a probability measure is forced to place mass somewhere and therefore cannot express "no
observation exists here". The event-branch support really does have free ground truth on real data
(inter-event intervals are in the raw stream), which is a real asset.

**Strongest reason to reject — the fatal flaw.** The frame-branch support is not identifiable, and the
paper's own rescue is false. Death 3's answer reads: *"with the events fixing the trajectory shape `Î`
up to scale, `ŝ^F_x` solves a linear system whose basis is the event-defined trajectory samples; the
null space shrinks as the in-exposure event count approaches `K`."* But the system is

```
B(x) = Σ_{k=1..K} ŝ^F_{x,k} · Î(x, τ_k)
```

which is **one scalar equation in `K` unknowns per pixel**. Adding events refines the *basis vectors*
`Î(x,τ_k)`; it does not add equations. The null space has dimension `K−1` per pixel for every event
count. The proposed "recoverability regime" plot (support-recovery error vs events-per-exposure) will
therefore measure the strength of the TV and entropy priors, not identifiability, and the plot's
intended message ("support is identifiable above `N` events per exposure") is not a thing that can
happen. Both stated retreats also fail: the 2-parameter (centre, width) form leaves 2 unknowns against
1 equation, and even the "first moment + mass" fallback leaves 2 against 1. RGB gives 3 equations, still
far short of `K = 16`.

This matters more than a technical footnote because `L_ren` is the paper's answer to Death 2 ("you
invented the ground truth"): the frame-branch support is supposed to be self-supervised on real data
without labels. It cannot be. **Fatal to this execution and to the frame half of the idea**; the
event-branch half (support read from the raw stream, abstention on staleness) survives as a smaller,
honest paper, which is what the team's own Death 1 fallback proposes.

**Further errors.**
- §"Derived quantities": `O(x) = Σ_k min(ŝ^F, ŝ^E)` is described as *"exactly the probability that the
  two observations are statements about the same instant"*. For two distributions, `Σ_k min(p_k,q_k) =
  1 − TV(p,q)` — the total-variation overlap. The coincidence probability is `Σ_k p_k q_k`, which is
  the quantity actually used in the attention gate. The document uses two different functionals and
  attaches the interpretation to the wrong one.
- `D_W(x) = (1/K)Σ_k |cdf^F − cdf^E|` is called *"the closed-form 1-D Wasserstein-1 distance"*. Correct
  for two *probability* measures on a window normalised to unit length. `ŝ^F` and `ŝ^E` are
  sub-probability measures of generally unequal mass, for which the CDF-difference formula is not `W₁`
  (that is unbalanced optimal transport). The normalised version `\bar s` is used correctly in
  `L_supp`; `D_W` is defined on the unnormalised one.
- §"What existing methods cannot express", item 2 conflates "no event ⇒ verifiably static for 40 ms"
  with "verified". No event means `|ΔL| < C` at that pixel — a photometric statement, not a scene
  statement, and false for textureless motion.

**Claim exceeding evidence.** *"$\ge 3.5$ dB PSNR drop between `O* ∈ [0.7,1]` and `O* ∈ [0,0.3]`, with
blur extent matched to ±5% and event count within ±5%"* — the dwell-then-dash construction changes the
*intensity profile* of the PSF while holding its support length fixed. A deblurring network conditioned
on events sees a different PSF, so some of the predicted drop is ordinary PSF mismatch, not support
mismatch. The partial-correlation control (prediction 2) is the right instrument but PSF profile, not
just extent, must enter the conditioning set.

**Required fixes.** 1) Either establish identifiability of `ŝ^F` from a *shared* support across a
region (many pixels, one support ⇒ many equations, few unknowns), or drop the frame-branch prediction
and ship the event-branch paper. 2) Fix the `min` / inner-product interpretation. 3) Define `D_W` on
normalised measures or use unbalanced OT. 4) Add PSF profile to the matched-pair conditioning set.

---

### Team 02 — *Exposure-Occupancy Measures* — **REJECT** (fatal to this execution)

**Summary.** Argues the frame-level label is an unstated functional `A` of the occupancy measure
`μ = y_#Unif(W)`, that conventions disagree systematically, and that the correct prediction target is
`μ` itself — support curve `γ_θ` plus dwell density `p_φ` — with the convention as a latent fitted by
EM and a split-conformal wrapper providing convention-marginal coverage on point-labelled benchmarks.

**Strongest reason to accept.** `L_point = −log Σ_A π_A N(ŷ; A[μ̂], σ²)` with `π` fitted by EM is a
genuinely good idea and the identifiability sketch for it is sound in kind: different frames have
differently-shaped `μ̂`, so the functionals separate. "We read a benchmark's unwritten annotation
convention off its labels" is a quotable, checkable, novel result. The conformal half is also the one
piece of coverage machinery in this round that is legible to CVPR (7 CVPR 2026 titles mention conformal;
zero mention identifiability).

**Strongest reason to reject — the fatal flaw.** Quantitative prediction 1 is false by the paper's own
definitions, and it is the prediction the paper says *"indicts the formulation rather than the
accuracy"*. `D := 1 − min_{A,A' ∈ 𝒜} IoU(A[y], A'[y])` with `𝒜 = {A_mid, A_mean, A_mode, A_start,
A_end, A_hull, A_core}`. At `ν = 0` (constant velocity) and `β = 3` (streak three object-diagonals
long), take a unit-width object and a path of length 3 along the motion axis:

```
A_start = [0,1]   A_end = [3,4]   →  IoU = 0
A_mid   = [1.5,2.5]  A_hull = [0,4]  →  IoU = 0.25
A_core  = intersection over the exposure = [3,1] = ∅  →  IoU = 0
⇒ D = 1 − 0 = 1.0        (predicted: D < 0.05)
```

Verified numerically. `D` is in fact **monotone increasing in `β` at `ν = 0`**, which is the exact
opposite of the paper's thesis. The claim survives only if `𝒜` is silently narrowed to
`{A_mid, A_mean}` — and even then `A_mode` is ill-defined at constant velocity, because the dwell
density is uniform and its argmax is the entire streak, not a point. So the reframing "acceleration,
not blur magnitude, governs label well-posedness" is not supported by the paper's own construction,
and the entire failure phenomenon (Panels A, B, C, predictions 1–2, the `β`-matched `ν` sweep) rests
on it.

**Further errors, both load-bearing.**
- **Proposition 1**: *"It is therefore invariant to *every* time-reparametrisation of `y`, including
  time reversal."* False. `B = I ⊛ Π_#μ` is invariant only to reparametrisations that **preserve the
  pushforward measure** — time reversal is one such, an arbitrary diffeomorphism of `W` is not, because
  it changes the dwell density. The correct statement is the one the paper gives immediately
  afterwards (identifiable up to the orbit `{y' : y'_#Unif(W) = μ}`). The wrong statement is also
  *internally fatal*: if `B` were invariant to every reparametrisation, `L_blur = ‖B − Â ⊛ Π_#μ̂‖₁`
  would carry zero gradient about `p_φ`, and the dwell head — the paper's whole novelty over
  trajectory methods — would be unsupervised by the frame.
- **Corollary (complementary identifiability)**: *"`Π_#μ` from the frame + the time-ordering from the
  events jointly identify the image-space intra-exposure state process, and neither modality alone
  does."* The second clause is false for events. By the paper's own Proposition 2, the event timestamp
  field `t(x)` is the inverse of `t ↦ Π(y(t))`; inverting it recovers `Π(y(t))` for all `t ∈ W`, which
  *is* the parametrised trajectory, from which `μ` and its dwell density follow immediately. Events
  alone determine the occupancy measure. What events do **not** determine is the *appearance* `I` —
  the radiometric content — and that is the true complementarity. As written, ablation A1's prediction
  ("event-only degrades `dW₁` badly — no mass") is unsupported by the theory it is meant to test; it
  would be supported by a contrast-threshold/sparsity argument, which is a practical claim, not an
  identifiability one.

**Claims whose strength exceeds their evidence.**
- *"the RSR change of a single fixed model under a convention switch is 10–20 points, whereas the RSR
  spread between the five published trackers is 3–8 points"* — a specific two-digit prediction on a
  gated dataset with no pilot.
- *"`P(ŷ_new ∈ Ŝ_new ⊕ r̂) ≥ 1−α`, marginally over the benchmark's own (unknown) convention
  distribution"* — correct **under exchangeability of calibration and test labels**, which is an
  assumption the paper does not state and which its own thesis undermines: if `π` differs per dataset
  and per sequence (as claimed and as the EM is designed to detect), calibration and test splits drawn
  across sequences are not exchangeable. Also, coverage is of the *label*, not of the physical state
  set — a fact the paper never says, and one that matters because a reader will read `1−α` as a
  guarantee about the world.

**The experiment a hostile reviewer would demand.** The time-reversal pair discriminating experiment
(A1) at `B ≥ 2` event bins, with the *finest* binning the baselines actually use. Frame-only will be at
chance (correctly), but a voxel-grid baseline with more than one bin resolves reversal — see the audit
of Team 10, which builds the same witness. If a two-bin voxel grid solves it, "no existing
representation can separate them, even in principle" collapses to "the one-bin case cannot".

**Required fixes.** 1) Recompute `D` for the stated `𝒜`; either narrow `𝒜` and say so, or abandon the
"blur and ill-posedness are orthogonal" thesis. 2) Restate Prop 1 as invariance under measure-preserving
reparametrisation, and note that this is what makes `L_blur` informative. 3) Delete or repair the
complementary-identifiability corollary — the honest version is mass/appearance from the frame,
geometry/timing from the events. 4) State the exchangeability hypothesis and the label-vs-state
distinction in the conformal claim. 5) Run the reversal experiment against multi-bin baselines.

---

### Team 05 — *No Offset Can Fix a Width* — **REJECT** (fatal to this execution)

**Summary.** Reframes event–frame temporal calibration from estimating a scalar delay to identifying a
*pair of temporal support kernels*, with three theorems: T1, a shift cannot close a modulus mismatch,
so a positive Support Mismatch Floor survives any offset; T2, the best-fit offset is a spectrum-weighted
delay and therefore scene- and speed-dependent, not a rig constant; T3, a speed sweep with `J ≥ 2`
distinct speeds identifies the kernels. The proposed real-data measurement is Offset Bias Drift,
`OBD = dδ̂/db` on a hardware-synchronised rig where the true offset is zero.

**Strongest reason to accept.** T1 is correct, cleanly proved, and I verified it: for complex `a, b`,
`|a − e^{iθ}b| ≥ ||a| − |b||` pointwise, and integrating against `S ≥ 0` gives the bound uniformly in
`δ`. The core algebraic identity — that under local translation, temporal convolution becomes spatial
convolution with the kernel dilated by the speed, `Ĥ(ξ) = ŵ(vξ)` — is right and is the cleanest piece
of derivation in the round. The plan is also the most feasible of the ten: ~96 GPU-h, the load-bearing
tier is CPU-FFT, and the decisive ablation (global shutter, `τ=0`, noiseless, `δ*=0`) is scheduled
first, at four days' cost.

**Strongest reason to reject — the fatal flaw.** **Theorem T2's closed form is wrong, and evaluated it
contradicts the paper's headline real-data prediction.** Minimising
`J(δ) = ∫S|Ĥ_F − e^{−i2πξvδ}Ĥ_E|²dξ` means maximising `∫W cos(φ + 2πξvδ)` with
`W = S|Ĥ_F||Ĥ_E|`, `φ = arg Ĥ_F − arg Ĥ_E`. The stationary point requires `φ + 2πξvδ ≈ 0`, i.e.
`δ ≈ −φ/(2πξv)`, and linearising the stationarity condition `∫W ξ sin(φ + 2πξvδ) dξ = 0` gives

```
δ̂  =  −∫ W ξ φ dξ  /  (2π v ∫ W ξ² dξ)          [correct]
δ̂  =  +∫ W φ/(2πξv) dξ / ∫ W dξ                  [T2, as written]
```

Two independent errors: the **sign is flipped**, and the weighting is `W` where it should be `W·ξ²`.
(The quantity `φ/(2πξv)` is also *phase* delay, not group delay `−dφ/dω`; the theorem is mislabelled.)

Numerically, with a box frame kernel `Ĥ_F = sinc(π v T ξ)`, an event low-pass
`Ĥ_E = (1 + i2πξvτ)^{-1}` with `τ = 0.3T`, `S ∝ ξ^{-2}` on `[0, 0.5]` cyc/px, exposure `T` fixed and
speed swept so that `b = vT` runs 0.25 → 8 px:

| `b` (px) | true `argmin δ` | T2's formula |
|---|---|---|
| 0.25 | −0.2983 | +0.3000 |
| 0.50 | −0.2935 | +0.3000 |
| 1.00 | −0.2810 | +0.3000 |
| 2.00 | −0.2687 | +0.3000 |
| 4.00 | −0.2787 | +0.3000 |
| 8.00 | −0.2772 | +0.2999 |

T2's formula returns `+τ`, constant to four digits across a 32× speed sweep. **The paper's own theorem
predicts `OBD = dδ̂/db = 0`** — precisely the null of the paper's headline measurement, and the exact
opposite of quantitative prediction 4 (`|dδ̂/db| ≳ 0.05·T` per pixel, `≥0.3·T` swing, "≥3 ms of drift on
a rig whose true offset is exactly 0").

The true argmin does drift, but by `0.029 T` over the whole sweep — roughly **ten times smaller** than
prediction 4 claims, and non-monotone. At DSEC daytime exposures (verified: 118 µs–4.2 ms in
`interlaken_00_d`) that is a sub-100 µs effect, well below the resolution of any of the five baseline
estimators the paper proposes to run. So the theorem is wrong, and the corrected theorem does not
support the paper's real-data story.

**Further errors.**
- Panel B / T1: *"the shift curve … tracks the floor within a few percent — i.e., after `b≈2` px,
  optimizing `δ` buys essentially nothing"*, and the claim `< 5%` of SMF. T1 is a *pointwise-optimal-
  phase* bound; attaining it needs a frequency-dependent phase, which one scalar `δ` cannot supply, so
  the bound is generally loose. In the configuration above `J(δ̂)/SMF` ranges over **1.00–24.0**, not
  1.00–1.05. The `<5%` claim is not a corollary of T1 and fails in the simplest instance.
- T3 (speed-sweep identifiability). Correct in kind — this is the multichannel-blind-deconvolution
  dilation argument — but stated without its necessary condition. In the log domain the observations
  are `f(v_j ξ) + g(ξ) = G_j(ξ)`, with `f = log ŵ`, `g = log Ŝ`. The ambiguity `f → f+p`, `g → g−q`
  requires `p(v_1ξ) = p(v_2ξ) = q(ξ)`, i.e. `p` invariant under scaling by `v_2/v_1` — the set of
  **log-periodic functions with period `log(v₂/v₁)`**, which is infinite-dimensional and non-trivial.
  Identifiability up to a scale therefore requires either incommensurable speed ratios, or the
  parametric/compact-support restriction on `w` the paper happens to impose elsewhere. *Correction:*
  state the condition; it is satisfiable and stating it costs one sentence.
- T1's phrasing *"the one-parameter group of linear-phase unit-modulus multipliers cannot contain such
  an operator"* is correct but is a triviality — it says two different filters are different. The
  content of the paper is entirely in the *magnitude* of SMF and OBD, i.e. in predictions 1–4, not in
  T1.

**Claims whose strength exceeds their evidence.** *"Calibrating faster makes your calibration worse,
which is the opposite of every calibration protocol's assumption"* — the strongest sentence in the
document, and it rests on prediction 4, which its own theorem negates.

**The experiment a hostile reviewer would demand.** Exactly the one already scheduled first — Ablation
1, the all-non-idealities-off decisive configuration. Its absence would be fatal. Its presence is why
this is a reject of the *execution*, not of the idea: fixing T2 costs an afternoon, and the paper
should then re-run the numerical sweep **before writing anything**, because the corrected theory may
show that the real effect on DSEC is below detectability, in which case the honest outcome is a
negative result.

**Required fixes.** 1) Fix T2's sign and weighting; rename phase delay. 2) Re-derive prediction 4 from
the corrected T2 and report the honest magnitude. 3) Measure the DSEC `(T, v)` joint distribution — as
Death 2's fallback (ii) already says — *before* committing, and be prepared to report a null. 4) State
T3's incommensurability/parametric condition. 5) Replace the `<5%` tightness claim with a computed
`J(δ̂)/SMF` curve, which is itself an interesting quantity.

---

### Team 10 — *Fusion Is Ill-Typed* — **REJECT** (fatal to this execution)

**Summary.** Types every measurement as `(φ, μ, κ, π)` — photometric domain, temporal measure, spatial
trajectory, per-pixel offset — observes that a frame is an order-0 probability measure applied in the
linear domain while an event bin is an order-1 mass-zero signed measure applied in the log domain, and
argues that every affine mixer in the RGB–event literature is therefore committing a *type error*
rather than a misalignment. Delivers typing rules, a null-space regulariser, a cross-model audit
(EU(s), OSAM, SII, SBP), and a minimal `SupportAttention` operator.

**Strongest reason to accept.** Panel C is the best-value experiment in the entire round: DSEC's
per-frame exposure varies frame to frame under auto-exposure (verified: 118 µs–14996 µs, and
337→4207 µs *within* `interlaken_00_d`), no published RGB–event model reads `T`, and testing whether
per-frame error correlates with `T·‖v̄‖` after controlling for `‖v̄‖` costs one afternoon of inference
and is genuinely undeniable. The Jacobian-influence form of OSAM (so the diagnostic applies to gates
and AdaIN, not just softmax attention) is the right engineering call.

**Strongest reason to reject — the fatal flaw.** Proposition 1 is true, trivial, and does not license
its conclusion. `μ_F(ℝ) = 1` and `μ_b(ℝ) = 0`, so no positive scalar times a shifted `μ_b` equals
`μ_F` — this is "1 ≠ 0". The conclusion drawn is: *"a convex mixture `αF + (1−α)V_b` … is not an
estimate of any scene quantity at all. The mixer is well-defined as arithmetic and undefined as
measurement."* By that argument every convolutional network ever built is ill-typed, because the first
layer mixes intensities (order 0) with finite differences (order 1) in a single affine map, and no
harm results. A hidden feature is not required to be an unbiased estimator of a named physical
observable; it is required to be a sufficient statistic for the decision. The proposition establishes
that `F` and `V_b` are different observables — which nobody disputes and which is the *reason* to fuse
them — and establishes nothing about whether a learned map of the pair is well-posed. The paper's own
Death 3 anticipates the "two-line triviality" charge and answers it with "so show the violation in
published code" — but showing that models mix order-0 with order-1 tensors is showing that they are
CNNs.

**Further errors, both load-bearing.**
- **Null-space dimension.** `𝒩 = {η : η(a_b)=0 ∀b, ∫e^L η dμ_F = 0}` with
  `dim 𝒩 = max(0, d − B − 1)`. The event constraints are `V_b = (1/C)(L(a_{b+1}) − L(a_b))`, so a
  perturbation leaves them fixed iff `η(a_{b+1}) = η(a_b)` for all `b` — i.e. `η` is **constant** on
  the `B+1` grid nodes, not zero. That is `B` constraints, not `B+1`. With the single frame constraint,
  `dim 𝒩 = (d+1) − (B+1) = d − B` for a degree-`d` basis: the paper **under-states its own ambiguity by
  one dimension**. (Under a "`d`-dimensional basis" reading the arithmetic matches, but the constraint
  set written is still wrong.) This matters because the count is promoted to a design rule ("this task
  at this speed needs `≥ B*` bins"), and the rule is off by one — and, more seriously, `d` is a free
  modelling choice never tied to physics, so the rule is circular until `d` is derived from a bandwidth
  argument.
- **The support-blind pair.** *"Take one bin `[a,b]` and two per-pixel paths `L₂(t) = L₁(a+b−t)`.
  Then: identical endpoints ⇒ identical polarity-sum voxel grids."* For a general path the endpoints
  **swap**, so the polarity sum is *negated*, not preserved: `L₂(b) − L₂(a) = −(L₁(b) − L₁(a))`. The
  construction requires the unstated extra condition `L₁(a) = L₁(b)` — true for the intended
  right-then-left bar, false for the general reversal as written. Worse, for `B ≥ 2` bins the
  time-reversed path has voxel grid `V'_b = −V_{B+1−b}`, which is generally *distinguishable* from
  `V_b`. So the witness separates only at `B = 1`, or when the reversal happens to be bin-symmetric.
  This is exactly what the paper's own `dim 𝒩 = d − B − 1` predicts, so the two claims are consistent
  with each other but inconsistent with the rhetoric. And this construction is the declared un-failable
  fallback: *"the **support-blind pair** result cannot fail."* It can, and against every baseline that
  uses more than one temporal bin — which is all of them.

**Claims whose strength exceeds their evidence.**
- *"`OSAM(s) ≈ 1 − r/(r+s)`: from `0.12±0.03` at `s=0.5` px to `0.83±0.05` at `s=12` px"* — an ansatz
  with error bars attached and no derivation.
- *"`EU` at the top flow decile is at most 60% of `EU` at the median decile"* on DSEC, where the same
  document concedes exposures may be ~1 ms and the displacement too small.
- *"Fine-tune each model on the high-`s` regime … OSAM falls by `<0.08` absolute"* — a two-digit
  prediction about other people's fine-tuning dynamics.

**The experiment a hostile reviewer would demand.** The CNN control: take an ordinary RGB-only detector,
apply the same type analysis to its first layer (which mixes intensities and differences), compute SII,
and show that SII does *not* predict its degradation. Without that control, SII is measuring
"architectures that mix things" and the correlation with speed degradation has an obvious confound.
Its absence is fatal to the type-system claim.

**Required fixes.** 1) Either derive why a *learned* map across types is ill-posed (it is not, in
general) or drop the type-error framing and lead with the empirical EU(s) audit, which stands on its
own. 2) Fix the null-space constraint set and the dimension count; tie `d` to a bandwidth argument or
delete the design rule. 3) Add the `L₁(a) = L₁(b)` condition to the support-blind pair and restrict the
claim to `B = 1`, or construct a genuinely `B`-robust witness. 4) Add the RGB-only CNN control for SII.
5) Run Panel C first — it costs an afternoon and is the only unimpeachable result here.

---

## Proposition audit

Every mathematical claim I could find across the ten, graded. Load-bearing derivations shown.

### Legend
**C** = correct · **CV** = correct but vacuous · **CUA** = correct under an unstated assumption (named) ·
**F** = false (shown why)

| # | Team | Claim | Grade |
|---|---|---|---|
| 1 | 01 | `B(x) = ∫₀¹ L(x;γ(u))du` after `u = (τ−t₀)/T`; hence `(t₀,T)` do not appear | **CV** — the substitution was defined to absorb them; see Derivation A |
| 2 | 01 | `(t₀,T)` non-identifiable from a single blurred frame | **CUA** — requires the motion `p(·)` to be an unknown free function; any motion prior or a second modality breaks the gauge, as the team's own method does |
| 3 | 01 | `B` invariant under `u → 1−u` (traversal direction unrecoverable) | **C** |
| 4 | 01 | `E[e_∥\|d] = (α_model − α_label)·d + O(d²)` | **C** as kinematics, given a fixed `α_model` |
| 5 | 01 | "the error is present at the optimum and cannot be trained away" | **F** — with events in the input, `E[y*(t_label)\|F,E]` is unbiased for a consistent labelling convention; TSB is a property of trained models, not of the formulation |
| 6 | 02 | Prop 1: `B = I ⊛ Π_#μ` for a locally rigid translating patch | **C** |
| 7 | 02 | Prop 1: "invariant to *every* time-reparametrisation of `y`" | **F** — invariant only under **measure-preserving** reparametrisations; otherwise `L_blur` would carry no gradient about `p_φ` |
| 8 | 02 | Prop 2: events determine the parametrisation up to per-pixel threshold gain | **C** |
| 9 | 02 | Corollary: `μ` from frames + order from events, **neither alone** identifies the process | **F** — inverting the event timestamp field gives `Π(y(t))` for all `t ∈ W`, hence `μ` *and* its order; the true complementarity is appearance (frame) vs geometry/timing (events). See Derivation B |
| 10 | 02 | At constant velocity `A_mid = A_mean = A_mode` exactly | **F** for `A_mode` (uniform dwell ⇒ argmax is the whole streak, not a point); **C** for `A_mid = A_mean` |
| 11 | 02 | Prediction 1: at `ν=0, β=3`, `D < 0.05` | **F** — `D = 1.0` under the stated `𝒜`. See Derivation C |
| 12 | 02 | `(b2)`: blur magnitude and label ill-posedness are orthogonal axes | **F** — follows from 11; `D` is monotone in `β` at `ν = 0` |
| 13 | 02 | Split-conformal: `P(ŷ ∈ Ŝ ⊕ r̂) ≥ 1−α` marginally over the convention | **CUA** — requires exchangeability of calibration and test labels, which the paper's own per-dataset `π` claim undermines; and the guarantee covers the **label**, not the state |
| 14 | 02 | Every existing detector is `M=1, K=1`; every trajectory method is `p ≡ Unif` | **C** |
| 15 | 03 | Observation = `⟨L, μ_o⟩`; event functional `δ_{t_i} − δ_{t_{i−1}}` | **C** for the ideal DVS model |
| 16 | 03 | `O(x) = Σ min(ŝ^F,ŝ^E)` is "the probability the two are statements about the same instant" | **F** — that is `1 − TV`, the TV overlap; the coincidence probability is `Σ p_k q_k`, which is what the attention gate actually uses |
| 17 | 03 | `D_W = (1/K)Σ\|cdf^F − cdf^E\|` is the closed-form `W₁` | **CUA** — true for **probability** measures on a unit-normalised window; false for the sub-probability measures it is defined on (needs unbalanced OT) |
| 18 | 03 | "the null space shrinks as the in-exposure event count approaches `K`" | **F** — one equation, `K` unknowns per pixel, for every event count. See Derivation D |
| 19 | 03 | Sub-probability (mass ≤ 1) is required to express "no observation" | **C** |
| 20 | 04 | `ŷ ≈ y*(t̄)` hence `τ̂ ≈ t̄`, "regardless of the label clock" | **F** — the evidence centroid governs prediction **variance** (`Var ∝ σ²[1/n + (t−t̄)²/Σ(tᵢ−t̄)²]`), not bias; the Bayes predictor of `y*(t_q)` is unbiased |
| 21 | 04 | For constant velocity, (spatial offset, temporal offset) is unidentifiable; identifiability restored at order `‖a‖(Δt)²` | **C** — and load-bearing. See Derivation E |
| 22 | 04 | `TEF = 1 − r_min/r_q ∈ [0,1]` | **C** by construction (`r_min ≤ r_q`) |
| 23 | 05 | T1: `min_δ ‖Ĥ_F − e^{−i2πξvδ}Ĥ_E‖²_S ≥ ∫S(\|Ĥ_F\|−\|Ĥ_E\|)² > 0` | **C**, and near-vacuous (it says two different filters differ). See Derivation F |
| 24 | 05 | T1 corollary: the empirical `R(δ̂)` tracks SMF within 5% for `b > 2` px | **F** — measured `J(δ̂)/SMF ∈ [1.00, 24.0]` in the canonical box/low-pass configuration |
| 25 | 05 | T2: `δ̂ = ∫W φ/(2πξv) dξ / ∫W dξ`, "spectrum-weighted group delay" | **F** — sign flipped, weighting should be `W·ξ²`, and it is phase delay not group delay. See Derivation G |
| 26 | 05 | Prediction 4: `\|dδ̂/db\| ≳ 0.05T` per px, `≥ 0.3T` swing | **F as a consequence of T2** (T2 as written gives `dδ̂/db = 0`); the corrected argmin drifts `≈0.03T` over a 32× sweep |
| 27 | 05 | Prediction 1: first sinc null enters the passband at `b ≥ 2` px | **C** (`ξ₁ = 1/b ≤ 0.5`) |
| 28 | 05 | Prediction 2: `SMF ∝ b⁴` at small `b` with `S ∝ ξ^{-2}` | **C** — `1−\|sinc(πbξ)\| ≈ (πbξ)²/6`, squared ⇒ `b⁴`; `∫ξ^{-2}ξ⁴` converges on a bounded band |
| 29 | 05 | Time-convolution ⇒ space-convolution: `Ĥ(ξ) = ŵ(vξ)` under `ℓ(x,t)=ℓ₀(x−vt)` | **C** — the cleanest identity in the round |
| 30 | 05 | T3: `J ≥ 2` known speeds identify `(w_F, w_E)` up to a common shift | **CUA** — requires incommensurable speed ratios (or a parametric/compact-support restriction), else the ambiguity class contains all **log-periodic** perturbations of period `log(v₂/v₁)`. See Derivation H |
| 31 | 06 | `log B_k = L(t_k) + J_k`, `J_k = LME_{W_k}(cE) − cE(t_k)` | **C**, exact |
| 32 | 06 | `J_k = ½Var_{W_k}(L) + O(κ₃)` | **CUA** — the full expansion is `J = (E_W[L] − L(t_k)) + ½Var_W(L) + O(κ₃)`; the first-order term vanishes only when `E_W[L] = L(t_k)` (linear `L`, midpoint `t_k`), and **dominates** on the non-monotone case the paper headlines. See Derivation I |
| 33 | 06 | `J_k ≥ 0` always | **F** — counterexample `L(t) = −t²` on `[−1,1]`, `t_k=0`: `J = −0.2919` |
| 34 | 06 | `R ~ P` regression: slope ≈ 1 shows the residual is structural, not noise | **CV** — `R ≡ P` identically for an ideal sensor; the measured `R² = 0.78` quantifies event quantisation, and the random-regressor null is not a control. See Derivation J |
| 35 | 06 | `φ = E(t_k→t)/E(t_k→t_{k+1})` is invariant to per-pixel threshold scaling, absolute level, global gain | **C** to first order (their own table shows 8× threshold change ⇒ 2.5× drift, i.e. sub-linear) |
| 36 | 06 | `G(a) = log M_{k+1}(a) − log M_k(a)` monotone ⇒ `a_p` identifiable from two exposure functionals | **C** — a genuine identifiability result **with an attaining estimator**; conditioning does improve with motion |
| 37 | 06 | "recovers the per-pixel contrast threshold" | **CUA** — `a_p = c_p·E_p` is identified; dividing by the *observed* `E_p` inherits rate-dependent refractory depletion, so the recovered `c_p` is an effective, motion-dependent threshold |
| 38 | 07 | `x̄ − x(T/2) = aT²/6 − aT²/8 = aT²/24`; `Δt ≈ aT²/(24 v̄)` | **C** as algebra |
| 39 | 07 | Worked example `T=20 ms, a=−2, v̄=4 ⇒ Δt = −8.3 ms` ("42% of the exposure") | **CUA / invalid** — `v̄ = v₀+aT/2` forces `v₀=24`, `v(T)=−16`: the object **reverses direction at `t=12 ms`, inside the exposure**, where the dwell density diverges and the perturbative derivation fails |
| 40 | 07 | "`Δt` diverges as `v̄ → 0`" | **C** but an artifact — the *position* offset `aT²/24` stays bounded; the divergent time error is unobservable |
| 41 | 07 | Temporal eikonal `∇_u τ(u) · v(u) = 1` | **C**, exactly, under brightness constancy with `∇I·v ≠ 0`. See Derivation K. Additionally forces `∇τ ∥ ∇I`, a stronger fact the paper does not use |
| 42 | 07 | `‖∇_u τ‖ = 1/v_⊥` | **C**, follows from 41 with `∇τ ∥ ∇I` |
| 43 | 07 | "mAP is *exactly unchanged* … invariant to a **group** of temporal shifts" | **F** — IoU is continuous in the shift, so AP is piecewise constant and generically changes; and a neighbourhood of 0 is not a group. The honest claim is insensitivity, and the constructive two-systems demo suffices |
| 44 | 07 | The frame is interval-censored, the event uncensored, a non-crossing right-censored | **C** — correct survival-analysis identification |
| 45 | 08 | `δ̂ = e_∥/‖v*‖`; a timing error is a 1-parameter perturbation constrained across translation, scale and yaw | **C**, and the best-used theory in the round: it makes the hypothesis over-identified |
| 46 | 08 | `τ̂_P = Σwᵢe_∥,ᵢ‖v*ᵢ‖ / Σwᵢ‖v*ᵢ‖²` (WLS through the origin) | **C** as an estimator; **biased** in practice by errors-in-variables in `‖v*‖` (attenuation toward zero) — not addressed |
| 47 | 08 | "By construction `AP ≤ AP^sync ≤ AP^⟂ ≤ AP^iso`" | **F** for the `AP ≤ AP^sync` link — re-anchoring by an estimated `τ̂` and a self-estimated `v̂` can lower AP |
| 48 | 08 | Isotropic null gives `R ≈ 0.5` | **C** for the per-pair `E[cos²θ]` in 2-D; **asserted, not derived** for the AP-gap ratio |
| 49 | 08 | Uniform-weight centroid of a `[t−50 ms, t]` window is `t−25 ms` | **C**, and matches the verified RVT source; but it is a property of the *representation*, not of the trained network's bin weighting |
| 50 | 09 | `τ(x,t) = C·N(x,t)` equals the total variation of the quantised log-intensity path | **C** |
| 51 | 09 | Exact invariance: `N(x, φ(t)) = N(x,t)` for strictly increasing `φ`, so `S` is unchanged bit-for-bit | **CV** — true because `S` contains no timestamps; the composite system reinjects `dτ/dt` for rate-valued tasks and is then not invariant |
| 52 | 09 | The invariance protects against the physical corruption (AER saturation, refractory) | **F** — refractory dead time **deletes events**, changing `N` and hence `τ`; event loss is not a monotone reparameterisation and lies outside the group |
| 53 | 09 | `\|L̃(x,τ) − L̃(x,kC)\| ≤ C` uniformly, independent of speed | **CUA** — true for an ideal sensor by the trigger condition; degrades with the very event loss invoked in 52 |
| 54 | 09 | Voxel-grid quantisation error `C·R·T/B` | **F** (unit slip) — per pixel it is `C·r(x)·T/B` with the *local* rate; the fixed-count analysis two paragraphs later uses `r(x)` correctly |
| 55 | 09 | `W(x)=0 ⇒ B(x)=exp(L̃(x,0))` **exactly**, alignment cost exactly zero | **CUA** — holds to `O(C)`, and only photometrically: a moving textureless surface has `W=0` while its semantic content changes, so the derived `1/W` weight maximally trusts the frame under the aperture problem |
| 56 | 09 | Fixed-count per-pixel quantisation error `C·n·r(x)/R` | **C** |
| 57 | 09 | `CDR = Δt_max/Δt_min` for any clamped rule | **CUA** — bounds the **width** of the flat region; the elbow *location* also depends on the `ρ=1` operating point inside the clamp range |
| 58 | 10 | Prop 1: `μ_F(ℝ)=1`, `μ_b(ℝ)=0`, sets disjoint, no shift/scale/warp maps one to the other | **C** and trivial |
| 59 | 10 | Corollary: an affine mix of the two "is not an estimate of any scene quantity at all" ⇒ the mixer is ill-typed | **F as a critique** — every CNN's first layer mixes order-0 intensities with order-1 differences; hidden features are not required to be unbiased estimators of named observables |
| 60 | 10 | `𝒩 = {η : η(a_b)=0 ∀b, ∫e^Lη dμ_F=0}`, `dim 𝒩 = max(0, d−B−1)` | **F** (constraint set) — events constrain **differences**, so the condition is `η(a_{b+1})=η(a_b)`, giving `B` constraints and `dim 𝒩 = d−B`; the paper under-states its own ambiguity by one dimension |
| 61 | 10 | Support-blind pair: `L₂(t)=L₁(a+b−t)` ⇒ identical polarity-sum voxel grid | **CUA / F** — requires the unstated `L₁(a)=L₁(b)`; and for `B ≥ 2` bins the reversed path gives `V'_b = −V_{B+1−b}`, generally distinguishable. The "cannot fail" fallback fails against every multi-bin baseline |
| 62 | 10 | Frame and event bin are time-reversal-degenerate in the **frame** channel | **C** (this half is right, and matches Team 02's #3) |

### Derivations

**A — Team 01's non-identifiability (why it is a tautology).**
`B(x) = (1/T)∫_{t₀}^{t₀+T} L(x;p(τ))dτ`. Set `u = (τ−t₀)/T`, `γ(u) := p(t₀+uT)`. Then
`B(x) = ∫₀¹ L(x;γ(u))du`. The map `(t₀,T,p) ↦ γ` is many-to-one: for any `(t₀',T')` there is a `p'`
with `p'(t₀'+uT') = γ(u)`, so `(t₀,T)` is a gauge **of the parameterisation we just chose**. This is a
statement about the coordinates, not about the physics. The physical question is whether `(t₀,T)` is
identifiable given a *model class* for `p(·)`. If `p` ranges over all continuous paths: not identifiable
(the fibre is non-trivial). If `p` is constrained — constant velocity of known magnitude, an event-
derived speed, an IMU — then `γ` plus the constraint pins `(t₀,T)` in general. The paper's own
Proposition says exactly this in its second half ("jointly, `(γ,t₀,T)` is identifiable"), so the correct
headline is *identifiability up to the time-affine group, which a second modality breaks*, and the
"no information whatsoever" framing is the paper's weakest sentence, not its strongest.

**B — Team 02's complementary identifiability (why the "neither alone" clause is false).**
Let `Π(y(t))` be the image-plane position at time `t ∈ W`, and suppose (as Prop 2 assumes) the event
timestamp field `t(x)` records when the edge crossed pixel `x`. Then `t(·)` is, by construction, the
inverse of `t ↦ Π(y(t))` on the swept set. Inverting a monotone-along-path field yields
`Π(y(t))` for every `t ∈ W`, i.e. the **parametrised** trajectory. From it, `μ = y_#Unif(W)` and its
dwell density follow immediately by pushforward. So events determine both the occupancy measure and
its order. What events cannot determine is the sharp appearance `I` (the radiometric content), which
is precisely what the frame supplies through `B = I ⊛ Π_#μ`. The correct complementarity is
**appearance from the frame, geometry-and-timing from the events**; the practical case for the frame
is contrast-threshold sparsity and textureless regions, which is an SNR argument, not an identifiability
one. Ablation A1's prediction ("event-only degrades `dW₁` badly — no mass") therefore tests a claim the
theory does not make.

**C — Team 02's Prediction 1 (numerically).**
1-D along the motion axis, unit object width, path length `p = β·w = 3` at constant velocity (`ν = 0`):

```python
def iou1d(a,b):
    lo,hi = max(a[0],b[0]), min(a[1],b[1]); inter = max(0.0, hi-lo)
    return inter/((a[1]-a[0])+(b[1]-b[0])-inter)
start,end,mid,hull = (0,1),(3,4),(1.5,2.5),(0,4)
iou1d(start,end)  # 0.0
iou1d(mid,hull)   # 0.25
# A_core = intersection over the exposure = [3,1] = empty  -> IoU 0
```
`D = 1 − min IoU = 1.0`. Predicted `< 0.05`. `D` is monotone increasing in `β` at `ν = 0`, which
inverts the paper's thesis. Narrowing `𝒜` to `{A_mid, A_mean}` rescues `D ≈ 0` — but then
`A_mode` (listed in `𝒜`) is ill-defined at constant velocity, since the dwell density is uniform.

**D — Team 03's frame-support identifiability.**
The rendering constraint per pixel is `B(x) = Σ_{k=1}^{K} ŝ^F_{x,k} Î(x,τ_k)` — one scalar equation,
`K` unknowns `ŝ^F_{x,·}`. Write it as `⟨ŝ^F_x, i_x⟩ = B(x)` with `i_x ∈ ℝ^K` the event-derived
trajectory samples. The solution set is an affine hyperplane of dimension `K−1`, **independent of the
number of events**: more events sharpen `i_x` (the normal vector), they do not add rows. Adding RGB
channels gives 3 rows; `K = 16`. The stated retreats do not help: `(centre, width)` is 2 unknowns
against 1 equation, `(first moment, mass)` likewise. Identifiability must come from *sharing* a support
across many pixels of one object — which is a different model than the per-pixel one proposed.

**E — Team 04's identifiability proposition (why it is right).**
Constant velocity: `x(t+δ) = x(t) + vδ`, so a temporal shift `δ` is exactly the spatial shift `vδ`; the
pair is unidentifiable from any support-averaged observation. With acceleration:
`x(t+δ) = x(t) + vδ + aδ²/2 + aδt`. The `aδt` term is time-varying and cannot be absorbed by a constant
spatial offset, so the two hypotheses separate at order `a·δ·Δt`. The paper's "identifiability margin"
(curvature of `d(ŷ, y*(t))` at the argmin) is exactly the right diagnostic for it. This is a theorem
that does work in the paper.

**F — Team 05's T1.**
For complex `a, b` and any real `θ`: `|a − e^{iθ}b| ≥ ||a| − |e^{iθ}b|| = ||a| − |b||`. Squaring and
integrating against `S(ξ) ≥ 0` gives, uniformly in `δ`,
`∫S|Ĥ_F − e^{−i2πξvδ}Ĥ_E|² dξ ≥ ∫S(|Ĥ_F| − |Ĥ_E|)² dξ = SMF`. Correct. But the bound is attained only
if `e^{−i2πξvδ}Ĥ_E` is phase-aligned with `Ĥ_F` at **every** `ξ`, which one scalar `δ` cannot do; so
SMF is generally loose. Numerically (box `Ĥ_F=sinc(πvTξ)`, low-pass `Ĥ_E=(1+i2πξvτ)^{-1}`, `τ=0.3T`,
`S∝ξ^{-2}` on `[0,0.5]`), `J(δ̂)/SMF` runs 1.00–24.0 as `b` sweeps 0.25→8 px. The paper's Panel-B
prediction of `<5%` is not a corollary and does not hold.

**G — Team 05's T2 (the fatal one).**
`J(δ) = ∫S(|Ĥ_F|²+|Ĥ_E|²)dξ − 2∫S·Re(conj(Ĥ_F)e^{−iψ}Ĥ_E)dξ`, `ψ = 2πξvδ`. With
`Ĥ_F=|Ĥ_F|e^{iθ_F}`, `Ĥ_E=|Ĥ_E|e^{iθ_E}`, `φ := θ_F − θ_E`:
`Re(conj(Ĥ_F)e^{−iψ}Ĥ_E) = |Ĥ_F||Ĥ_E|cos(θ_E − θ_F − ψ) = W/S · cos(φ + ψ)`.
So minimising `J` maximises `∫W cos(φ + 2πξvδ)dξ`, whose stationary condition is
`∫W·ξ·sin(φ + 2πξvδ)dξ = 0`. Linearising `sin z ≈ z`:

```
δ̂ = − ∫ W ξ φ dξ / ( 2π v ∫ W ξ² dξ )
```

The paper's `δ̂ = +∫W φ/(2πξv)dξ / ∫W dξ` has the **wrong sign** and the **wrong weight** (`W` instead
of `W·ξ²`); and `φ/(2πξv)` is *phase* delay, not group delay `−dφ/dω`. Numerically (same configuration,
`T` fixed, `v` swept so `b=vT` runs 0.25→8 px), the true `argmin δ` runs `−0.2983 → −0.2772` while the
paper's formula returns `+0.3000` at every `b` to four significant figures. Two consequences: (i) the
sign is inverted; (ii) **T2 as written predicts `OBD = dδ̂/db = 0`**, which is the null of the paper's
own headline real-data measurement (prediction 4: `|dδ̂/db| ≳ 0.05T` per px, swing `≥0.3T`). The
corrected argmin drifts by `0.029T` across the sweep — about ten times smaller than claimed, and
non-monotone. Reproduce with:

```python
import numpy as np
T, tau = 1.0, 0.30
xi = np.linspace(1e-4, 0.5, 4001); S = xi**-2.0
ds = np.linspace(-1.0, 1.0, 8001)
for v in [0.25,0.5,1,2,4,8]:
    Hf = np.sinc(v*T*xi); He = 1/(1+1j*2*np.pi*xi*v*tau)
    E  = np.exp(-1j*2*np.pi*np.outer(ds,xi)*v)*He[None,:]
    J  = np.trapezoid(S[None,:]*np.abs(Hf[None,:]-E)**2, xi, axis=1)
    phi = np.angle(Hf)-np.angle(He); W = S*np.abs(Hf)*np.abs(He)
    d5 = np.trapezoid(W*phi/(2*np.pi*xi*v),xi)/np.trapezoid(W,xi)
    print(v, ds[J.argmin()], d5)
```

**H — Team 05's T3 (the unstated condition).**
Observations `G_j(ξ) = ŵ(v_jξ)·Ŝ(ξ)`, `j=1..J`. In the log domain, `f(v_jξ) + g(ξ) = log G_j(ξ)` with
`f = log ŵ`, `g = log Ŝ`. An ambiguity `(f+p, g−q)` requires `p(v_jξ) = q(ξ)` for all `j`, hence
`p(v_1ξ) = p(v_2ξ)`, i.e. `p` is invariant under scaling by `v_2/v_1` — the **log-periodic** functions
of period `log(v₂/v₁)`, an infinite-dimensional family. Identifiability up to a scalar therefore needs
either (i) speed ratios whose logarithms are incommensurable, or (ii) a parametric/compact-support
restriction on `w` that excludes the log-periodic modes. The paper's non-negativity and
support-length-from-metadata constraints likely do (ii), but the theorem does not say so.

**I — Team 06's exposure gap (the missing first-order term).**
For `X = L(t)` with `t ~ Unif(W)`, the cumulant generating function at 1 gives
`log E[e^X] = E[X] + ½Var(X) + κ₃/6 + …`. Since `log B_k = LME_W(L)`,

```
J = LME_W(L) − L(t_k) = ( E_W[L] − L(t_k) ) + ½Var_W(L) + O(κ₃)
```

The paper drops the first bracket. It vanishes only when `E_W[L] = L(t_k)` — exactly true for linear
`L` at the midpoint. Numerically on `W=[−1,1]`, `t_k=0`:

| `L(t)` | `E_W[L] − L(t_k)` | `½Var_W(L)` | sum | exact `J` |
|---|---|---|---|---|
| `0.7t` (linear) | `+0.0000` | `+0.0817` | `+0.0817` | `+0.0804` |
| `t²` (convex) | `+0.3333` | `+0.0444` | `+0.3778` | `+0.3803` |
| `−t²` (concave) | `−0.3333` | `+0.0444` | `−0.2889` | **`−0.2919`** |

The concave row also refutes `J ≥ 0`, and refutes P4's "the frame reads systematically brighter". The
first-order term dominates on non-monotone trajectories — the paper's own zero-net-event headline case.

**J — Team 06's `R ~ P` (the identity).**
`log B_k = L_ref + LME_{W_k}(cE)` exactly. Substituting into
`R = c(E(t_{k+1})−E(t_k)) − (log B_{k+1} − log B_k)`:

```
R = cE(t_{k+1}) − cE(t_k) − LME_{W_{k+1}}(cE) + LME_{W_k}(cE)
  = [cE(t_{k+1}) − LME_{W_{k+1}}(cE)] − [cE(t_k) − LME_{W_k}(cE)]  ≡  P
```

`R = P` identically for an ideal sensor: the `L_ref` cancels and there is nothing left to measure. The
reported slope 0.955 / `R² = 0.779` therefore quantify the event quantisation separating the quantised
`E` in `P` from the true `L` in `B` — which the paper itself names ("remainder is ±c/2 event
quantisation"). The "noise null (random regressor) `R² = 0.0015`" is not a control against an identity.
This does **not** invalidate the fix or the identifiability result; it invalidates the framing of the
measurement as a discovery.

**K — Team 07's temporal eikonal.**
Define `τ(u)` by `I(u, τ(u)) = L` (the time pixel `u` crosses level `L`). Differentiating in `u`:
`∇_u I + I_t ∇_u τ = 0`. Brightness constancy `I_t + ∇_u I · v = 0` gives `I_t = −∇_u I · v`. Hence
`∇_u I = (∇_u I · v)∇_u τ`, so **`∇_u τ ∥ ∇_u I`**; dotting with `v` and dividing by `∇_u I·v ≠ 0`:

```
∇_u τ(u) · v(u) = 1                     [exact]
‖∇_u τ‖ = 1/v_⊥   with v_⊥ = n̂·v, n̂ = ∇I/‖∇I‖
```

Correct. Valid where `∇I ≠ 0` and `∇I·v ≠ 0` — i.e. exactly where events fire — and `τ` is multi-valued
when a level is crossed more than once. Note that this identity *is* brightness constancy in level-set
form, so `L_eik` is a flow-consistency term in different clothing; it adds no constraint beyond the flow
head. The paper's own Death 3 anticipates this and is right to.

---

## Ranking

1. **Team 08 — Right Place, Wrong Time.** The only entry whose central claim is over-identified and
   therefore falsifiable, the only one that proposes no method, and the cheapest to run (~35 GPU-h,
   inference only, E0 needs 4.7 MB and no GPU).
2. **Team 06 — The Exposure Gap.** Only entry that has already computed its own numbers, and the only
   identifiability result with an estimator that attains it; two repairable formula errors and one
   tautology-as-headline.
3. **Team 04 — When Is Your Prediction?** The best null-result specification and a correct, load-bearing
   identifiability proposition; the "law" it leads with is a variance result mistaken for a bias result.
4. **Team 01 — Latent Exposure Support.** Cheapest headline figure and the only free real-data validation
   of its own latent (SIE against DSEC's published exposures); the central proposition is a
   reparameterisation tautology and one prediction is already falsified by the verified machine facts.
5. **Team 09 — Change-Time.** A correct and elegant coordinate (`τ = C·N` as path total variation) and a
   genuinely measured per-pixel frame support; the invariance is bought by deletion, and the corruption
   it is motivated by lies outside the invariance group.
6. **Team 07 — Chronofields.** Two correct pieces of mathematics (the eikonal, the censoring
   identification) attached to a headline number computed outside its own validity domain, and a
   competitor (reconstruct-then-detect) the team itself says may kill it.
7. **Team 05 — No Offset Can Fix a Width.** Best feasibility in the round and a correct impossibility
   bound, wrecked by a theorem whose corrected form predicts the negation of the paper's headline
   measurement.
8. **Team 03 — Temporal Support Fields.** The best-designed matched-pair experiment in the round,
   attached to a frame-branch output that is not identifiable, with no working fallback.
9. **Team 10 — Fusion Is Ill-Typed.** Excellent cheap audit (Panel C) buried under a proposition that is
   true, trivial, and does not license its own conclusion, plus a broken dimension count and a broken
   witness.
10. **Team 02 — Exposure-Occupancy Measures.** The best *idea* on this list — reading a benchmark's
    annotation convention off its labels — sitting on a headline prediction that is false by the team's
    own definitions and two further load-bearing propositional errors.

---

## My winner and its fatal flaw

**Winner: Team 08.**

It is the only entry in the round whose mathematics is *over-identified*. Everyone else asserts a
decomposition and then measures it. Team 08 asserts that one scalar `δ` must simultaneously explain the
box translation `δ·v*`, the box scale change `δ·ṡ*` and, in 3D, the yaw change — and then checks
whether the two channels agree, with `κ = |δ̂ − δ̂_s|/(σ_δ̂ + σ_δ̂_s)`. That is the difference between a
re-parameterisation and a hypothesis. It proposes no architecture and no loss, so the standing charge
"you invented a metric and then won on it" has nowhere to land. It is also, by a wide margin, the most
executable: inference only, ~35 GPU-h, every checkpoint and tarball verified live by the team, and its
single most damaging experiment (E0 — is DSEC-Det's and DSEC-3DOD's inter-frame ground truth recoverable
from its own linear-interpolation prior?) needs a 4.7 MB label file and no GPU at all.

**Its fatal flaw: control C3, the control the whole paper's credibility rests on, cannot be run on the
data the paper plans to run it on.**

Death 3 — *"you are measuring the labels, not the models"* — is correctly identified as the sharpest
attack. The paper's answer is C3: predict `τ̂` from each method's *declared* temporal support before
measuring it, then check whether `τ̂` tracks the declared window (⇒ it's the method) or is constant
across methods (⇒ it's the dataset). That discrimination requires **variance in the predictor**. It does
not exist. RVT-{T,S,B} all use `stacked_histogram_dt=50_nbins=10` — the verified machine facts confirm
this from the released source — and the paper's own strongest feasibility argument is that
`ssms_event_cameras` *"consumes the identical preprocessed tarballs as RVT"* and is built on the RVT
codebase, hence uses the identical representation. All five detection checkpoints therefore share one
`w_P = 50 ms`. The very property that makes the comparison fair (one data pipeline, zero preprocessing
degrees of freedom) makes the control vacuous: a regression of `τ̂` on `w_P` with a single value of
`w_P` has no slope to estimate.

Compounding it: `w_G` for Gen1 is "the ATIS integration width", per-pixel and intensity-dependent and
never published as a number, so `τ_max = (w_G + w_P)/2` — the quantity advertised as *not* a free
parameter — is a free parameter on that dataset under another name. And the estimator `τ̂` itself is
errors-in-variables: `‖v*‖` is finite-differenced from 4 Hz (Gen1) or 10–20 Hz labels, so the WLS slope
is attenuated by `Var(v)/(Var(v)+σ_v²)`, biasing the headline `τ̂` toward zero, worst in the low-speed
bins where most of the data sits. The paper's whole claim is a magnitude in milliseconds; two of its
three sources of confidence in that magnitude are unavailable as planned.

**The fix is cheap and must be done before anything else.** Retrain RVT at `dt ∈ {10, 25, 50, 100} ms`
on Gen1 (240×304, ~2 GPU-h per run, well inside 9 GB) so that C3 has a real predictor and the
architecture-prediction claim becomes testable; and replace the WLS with an errors-in-variables
estimator (Deming, or use the scale channel as an instrument), reporting the attenuation factor. With
those two changes this is the submission I would fight for in the AC discussion. Without them, its
central number is a biased estimate of a quantity it cannot attribute.
