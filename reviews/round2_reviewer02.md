# Round 2 — Reviewer 02 (estimation theory, identifiability, mathematical correctness)

Target: **Team 08 — *Right Place, Wrong Time*, revision v2** (`ideas/team08_v2.md`, 887 lines, 2026-09-01).
Round-one verdict: ACCEPT, my winner. Round-one required fix #1: retrain RVT at several `dt` so C3 has a
non-degenerate predictor. Round-one required fix #2: correct the errors-in-variables attenuation in `τ̂`.

This round I audit the two repairs **as mathematics**, not as plans, plus four propositions that are new in v2.
Every number below is derived here and re-derivable from
`reviews/round2_reviewer02_audit.py` (pure numpy, no arguments, runs in three seconds). Two facts are read out of the RVT source now present at
`/media/hdd8/justin/my_project/CVPR20/src/RVT`, not out of anyone's description of it.

**Headline of this review.** The revision is a large and mostly honest improvement, and on nine of the twelve
objections it closed I have nothing to add. But the one repair that my round-one review said was *mandatory* —
predictor variance in `w_P` — has not been achieved. Of the three "free levers", **one measures a different
estimand, one is arithmetically invalid on the released tensor, and one does not change temporal support at
all**. And the correction I demanded, the errors-in-variables treatment, is adopted in the right spirit but its
headline estimator — the instrumental variable — **is not a valid instrument as specified**, because the two
"disjoint" label pairs share a label.

I also owe the team a concession: **my ~8 GPU-h retraining estimate was wrong by roughly an order of
magnitude, and their 60–120 GPU-h figure is the right one.** They were entitled to reject my fix on cost. They
were not entitled to the substitute they chose, and there is a third option, costing ~9 GPU-h, that they
missed.

---

## Do the three no-training levers vary temporal support, or only ablate input

### 0. What the estimand has to be

Panel C regresses measured `τ̂` on measured `w_P` and reads a non-zero slope as *"`τ̂` is a property of the
predictor's support and not of the annotation pipeline"*. For that reading, the x-axis must be an index of a
family of **predictors**, and the estimand is

> `τ*(w) := ` the effective timestamp of *the predictor that a competent training procedure produces when its
> input is supported on a window of width `w`*.

That is the quantity Death 3 is about, because Death 3 asks whether the released checkpoints' `τ̂` is a
method-level or a dataset-level property, and "method" means *deployable predictor*.

What masking measures is a different functional. Let `f` be the fixed trained network, `x = (x_1…x_10)` the
stored stacked histogram (`x_1` oldest), and let `ω_k` be `f`'s influence weight on bin `k`. Masking measures

> `τ_mask(j) := ` the effective timestamp of **the same fixed `f`**, optimised for `w = 50 ms`, when it is
> evaluated on an input supported on `w = 5(10−j) ms`.

These are two different objects and there is one and only one condition under which they coincide.

### 1. The condition, derived

Take the smallest model that contains the phenomenon. Bin `k` supplies a noisy read of the object's position at
its centre time `c_k`:

```
m_k = p0 + v·c_k + ε_k ,     ε_k ~ N(0, σ²) ,     v ~ N(0, σ_v²)  (the predictor's prior over speed)
```

A predictor that reports the state at the query time `t = 0` is a linear functional `p̂0 = Σ_k a_k m_k` with
`Σ a_k = 1` (unbiased when `v = 0`). Its **effective timestamp is exactly** `τ = Σ_k a_k c_k`, because
`E[p̂0 | v] = p0 + v·Σ a_k c_k = p(τ)`. Two regimes:

- **A pure smoother** puts `a_k ≥ 0` and cannot look ahead: `τ = ` the evidence centroid `= −w/2` for uniform
  weights. This is the paper's mechanism.
- **An extrapolator** puts *negative* weights on the old bins, uses them to estimate `v`, and cancels its own
  lag. Writing `γ(w) = S_cc(w)/(S_cc(w) + σ²/σ_v²)` for the shrinkage of the fitted velocity
  (`S_cc = Σ(c_k − c̄)²` over the retained bins), the ridge/MAP solution gives, in closed form,

```
τ*(w) = (1 − γ(w)) · c̄(w) = −(1 − γ(w))·w/2 .
```

`γ` is **increasing in `w`**: a wider window estimates velocity better, so a *retrained* predictor extrapolates
better and its lag *shrinks*. `τ*(w)` is therefore **non-monotone**, and its slope is `−1/2` only in the
no-extrapolation limit `γ ≡ 0`.

Now the masked case. The retained set is `S = {k > j}`; the weights are still the full-window `a`. With
`A_j = Σ_{k∈S} a_k` and `C_j = Σ_{k∈S} a_k c_k`,

```
E[p̂0^mask | v] = A_j·p0 + C_j·v .
```

Two things happen at once, and only one of them is a time.

1. **A gain error.** `A_j ≠ 1`. In a linear estimator this multiplies the *absolute position*, which for a
   detector is nonsense; in a real detector the spatial anchoring re-normalises, and only then does the reading
   `τ_mask(j) = C_j / A_j` make sense. So **the time reading of a masked network exists only under an assumed
   normalisation that the network is not required to perform**, and `A_j` is a direct, free measurement of how
   far that assumption is from holding. The paper never mentions `A_j`.
2. **A centroid shift** `C_j/A_j`, which equals the retained-mass centroid *only if `a_k ≥ 0`*. If the network
   extrapolates, masking the leading bins deletes the **negative** weights — i.e. it removes the machinery by
   which the network cancels its own lag — and the masked network becomes **more** lagged as the window gets
   narrower. That is the opposite sign from the paper's mechanism.

**Proposition (the crux).** `τ_mask(j) = τ*(w_j)` for all `j` **iff** the trained network is a non-negative,
self-normalising, non-extrapolating smoother over its bins — i.e. iff it makes no attempt to compensate its own
support. That is precisely the hypothesis Panel C is supposed to *test*. **The lever assumes the hypothesis in
order to manufacture the axis.**

### 2. Settled numerically

Ten bins of 5 ms over `[t−50, t]`. `γ_full` is the full-window extrapolation strength. Both columns are exact.

| `γ_full` | `w` (ms) | `τ*` retrained | `τ_mask` (normalised) | gain `A_j` |
|---|---|---|---|---|
| 0.00 | 50 → 5 | −25.0 → −2.5 | −25.0 → −2.5 | 1.00 → 0.10 |
| 0.50 | 50 / 40 / 20 / 5 | −12.50 / −13.25 / −9.43 / −2.50 | −12.50 / −13.90 / −9.01 / −2.50 | 1.00 / 1.04 / 0.76 / 0.24 |
| 0.90 | 50 / 40 / 30 / 20 / 5 | −2.50 / **−3.58** / −5.16 / −6.47 / −2.50 | −2.50 / **−10.74** / −11.20 / −8.71 / −2.50 | 1.00 / 1.24 / 1.26 / 1.06 / 0.35 |
| 0.99 | 50 / 40 / 30 / 20 / 5 | −0.25 / **−0.39** / −0.68 / −1.43 / −2.50 | −0.25 / **−10.16** / −11.02 / −8.66 / −2.50 | 1.00 / 1.28 / 1.32 / 1.12 / 0.37 |

Fitted slopes `dτ/dw`:

| `γ_full` | retrained | masked | inside the pre-registered `[0.3, 0.7]`? |
|---|---|---|---|
| 0.00 | −0.500 | −0.500 | yes / yes |
| 0.50 | −0.234 | −0.243 | **no / no** |
| 0.90 | +0.021 | −0.053 | **no / no** |
| 0.99 | +0.063 | −0.012 | **no / no** |

Three readings, all load-bearing.

- **At `γ = 0` the two designs agree exactly and both return `−w/2`.** The lever is faithful precisely in the
  case where the answer is already known by arithmetic from the config file — i.e. it adds no information
  exactly where the paper needs none.
- **As soon as the network compensates at all, they diverge, and at `γ = 0.99, w = 40 ms` the masked reading
  reports 26× the lag of the retrained predictor** (−10.16 ms vs −0.39 ms). At `γ = 0.9` the factor is 3.0.
  The divergence is largest exactly in the regime that discriminates the paper's hypothesis from its
  alternative.
- **The pre-registered slope band `[0.3, 0.7]` is attainable only in the `γ = 0` limit.** For every partially
  extrapolating network — retrained *or* masked — the slope falls outside the band. P6 as written is therefore
  a test of "is the network a pure boxcar averager", not a test of "is `τ̂` a property of support"; and by K4 a
  network that extrapolates would be recorded as *"the slope is null, so `τ̂` is a property of the dataset"*,
  which is a wrong inference from a correct measurement.

The gain column is the OOD magnitude in the same units: at `γ = 0.9`, masking six bins leaves the network
computing a position functional whose gain is 1.26, a 26 % over-shoot of the position itself. Their control
(iii), mean-imputation, does not touch this: mean-imputation fixes "zeros are out of distribution" and leaves
"the evidence is gone" and "the weights are wrong for this support" entirely intact.

### 3. Lever 1 — leading-bin masking: four further defects, ordered by size

**(a) The support is a comb, not a window, and the recurrence is untouched.** RVT carries LSTM state across the
sequence (`sequence_length: 11` in `config/dataset/gen1.yaml`) and the paper's own E1c is built on that fact.
To mask coherently in a recurrent rollout you must mask *every* window, which gives the network a duty-cycled
stream: a union of `5(10−j)` ms teeth spaced 50 ms apart, extending backwards through the whole sequence. The
support of the prediction is then a comb of *total* mass `(10−j)/10` over an *unbounded* span — not a window of
width `5(10−j)` ms. The x-coordinate `w_P = 5(10−j)` describes the most recent tooth and nothing else. If
instead they mask only the current window and leave the state intact, then the evidence at `t−50…t−45` ms is
still present *via the state from the previous step*, and the manipulation removes nothing at all beyond one
step of freshness. There is no version of this that yields the labelled x-value.

**(b) Bin edges are not on a 5 ms grid.** `data/utils/representations.py:104-108`:

```python
t0_int = time[0]; t1_int = time[-1]
t_norm = (time - t0_int) / max((t1_int - t0_int), 1)
t_idx  = clamp(floor(t_norm * bins), max=bins-1)
```

The ten bins are placed by the **empirical first and last event timestamps inside the window**, not by absolute
time. The physical width of a bin is therefore a random variable driven by scene activity — which is, ironically,
exactly the "activity-driven support" the paper claims no metric can see (§*What existing methods cannot
express*, item 4). Consequence: `c_k = −5(10−k+0.5)` ms is an approximation whose error is largest in quiet
intervals, and the mapping from `j` to a physical `w_P` must be *measured per sample*, not asserted.

**(c) Evidence loss and support change are confounded, and the proposed control cannot separate them.** Removing
`j` bins removes ~`j/10` of the events, degrading the network's velocity/appearance estimate. A degraded
estimate shrinks toward the prior; shrinkage of a motion-compensation term is observationally identical to a
change in `τ̂` (it *is* the `(1−γ)` factor above). The separating control is not mean-imputation; it is a
manipulation that changes the support **at constant evidence**.

**(d) Effective `n` is not 12.** Six masks × three checkpoints = 18 points, but the six masks on one checkpoint
lie on a deterministic curve of one underlying `ω`, and the three Gen1 checkpoints share dataset, labels and
annotation offset. The sequence-level bootstrap of §4.5 resamples *sequences* and will not see this. The
regression's effective degrees of freedom is the number of distinct manipulation *types*, which is four, not
the number of points, which is twelve.

### 4. Lever 2 — re-binning: arithmetically invalid on the released tensor, and equivalent to a speed change

Two independent kills, one of which is decidable today from the source.

**(a) `count_cutoff = 10`. Additivity is false.** `scripts/genx/conf_preprocess/representation/stacked_hist.yaml`:

```yaml
name: "stacked_histogram"
nbins: 10
count_cutoff: 10
```

and `representations.py:117`: `representation = clamp(representation, min=0, max=self.count_cutoff)`. Note that
`StackedHistogramFactory.name` (line 653) — unlike `MixedDensityStackFactory.name` (line 667) — does **not**
append a `_cutoff=` string, so the released tarball name `stacked_histogram_dt=50_nbins=10` is entirely
consistent with, and on the repo's own default config *is*, `count_cutoff = 10`. Every per-pixel, per-polarity
bin count in the stored tensor is clipped at 10.

Therefore `clip(a) + clip(b) ≠ clip(a + b)`, and the re-binned tensor is not the `dt=100, nbins=10`
representation it is claimed to be. Worse in two directions at once: the summed tensor takes values up to 20 on
a network trained on `[0, 10]`; and the discrepancy from the true wide-bin histogram is exactly zero on quiet
pixels and maximal on saturated ones — i.e. **the distortion is concentrated on fast, high-contrast edges,
which is the paper's own headline `AP@HiM` slice.** The team's plan is to "verify the additivity assumption on
one file in week 1"; the answer is already in the repository they have cloned, and it is *no*.

**(b) Even absent clipping, re-binning is a speed change, not a support change.** Doubling the bin width while
holding the number of bins and the event statistics fixed produces, tensor-for-tensor, the same input as the
identical scene played at 2× speed viewed through the original `dt=50` window: per bin, both the event count and
the object displacement double. So the re-binned points on Panel C are **speed-manipulated points placed on a
support axis**, perfectly confounded with the paper's own Panel A/P2 speed effect, and pushed toward the
event-rate ceiling that the paper itself (corollary 2) says makes `w_P(v)` non-monotone. They are also scored
against unchanged labels and unchanged `v*`, so any lag the network carries in *bin* units is converted to real
time at the new bin width and doubles — reproducing slope ≈ 1/2 by construction, again only under the smoother
model.

### 5. Lever 3 — query-step subsampling: it does not change the support of any prediction

Under the paper's own definition, `w_P` is the width of the kernel describing where *one emitted state's*
information comes from. Subsampling the query grid from 20 Hz to 6.7 Hz leaves that kernel identical: each
prediction still consumes `[t−50 ms, t]`. What changes is (i) the emission rate and (ii), for a recurrent model,
the density of state updates. Neither is a support width, and the value assigned on the axis — 150 ms, the query
*period* — is a third quantity again.

Both readings of the manipulation fail, in opposite directions:

- If outputs are scored against later query instants (streaming style), subsampling injects a mean staleness of
  half the period, i.e. **+75 ms of additive latency at 6.7 Hz**. That is *system* latency, exactly the quantity
  `sAP` (Li et al., ECCV 2020) measures and exactly the quantity §*Why this is not <closest work>* says the
  paper is **not** about ("sAP … cannot see representational latency … which is our main quantity"). Putting it
  on the representational-support axis is a category error that would *manufacture* a large slope.
- If outputs are scored only at the instants they are emitted, then relative to the 20 Hz rollout the most
  recent window is byte-identical and only the older tiles `[t−150, t−50]` are deleted from the state. Expected
  effect on `τ̂`: small. So the point sits at `x = 150 ms` with `y ≈ y(50 ms)` and **biases the fitted slope
  toward zero** — toward the K4 kill branch, for a reason unrelated to support.

The paper also calls this "the downward half of the S5-ViT inference-frequency sweep R1 recommends". It is not.
Zubić et al. (CVPR 2024) change the *representation window* `T` at inference — their whole argument is that the
representation is a sampler whose passband scales with `T`. Skipping stored windows changes no `T`. The
citation misdescribes the experiment it borrows authority from.

### 6. Verdict on the crux, and the part that does work

**The three levers do not vary a common estimand, and none of them varies `τ*(w)`.**

- Lever 1 varies the *conditional evidence centroid of a fixed influence profile under an off-distribution
  input*. That is a real quantity, and it is worth measuring — but it equals the estimand only under the
  hypothesis being tested, it is confounded with evidence loss and gain distortion, and for a recurrent model
  its nominal `w_P` is not the support of anything.
- Lever 2 is arithmetically invalid on the released tensor (`count_cutoff = 10`), and where it is valid it is a
  speed manipulation.
- Lever 3 changes no support at all.

Panel C as designed therefore regresses `τ̂` on an x-axis whose *definition changes between points*: a masked
window width, a re-binned nominal width, a query period, a recurrent-truncation memory length in E1c, and a
qualitative "≈100× wider" for BFlow's image branch in E2. **Regressing on an x whose units are not common
across observations is not a regression**, and no confidence interval covers that.

**What does work, and should be promoted to the headline.** E1b's *per-bin occlusion* measurement is the good
experiment and it is being used as scaffolding for the bad one. It yields `ω_k` and the influence centroid
`c_P = Σω_k c_k / Σω_k` by a *sensitivity* measurement, while `τ̂` is obtained by a *bias-against-GT*
measurement. Those are genuinely different measurements of the same latent, so

```
τ̂ = τ_G + c_P ,     slope 1 against the measured influence centroid, intercept = the annotation offset
```

is falsifiable, over-identified in exactly the style that made me pick this paper in round one, and free. Two
consequences the paper misses:

1. **The intercept, not the slope, is what Death 3 needs.** With one dataset and one checkpoint family, the
   dataset-level component of `τ̂` is *identified as the intercept* of this regression, extrapolated to
   `c_P = 0`. That is a stronger and cheaper answer to "you are measuring the labels, not the models" than the
   slope ever was. It is unstated anywhere in v2.
2. **Predicted slope is 1, not 1/2.** Regressing on a *centroid* gives 1; the 1/2 in P6 comes from regressing on
   a *width* under a uniform-weight assumption. The paper should not spend its pre-registration on the weaker
   of the two.

---

## The EIV treatment audited

The direction is right, the diagnosis is largely right, and one of the three estimators is invalid as
specified. Taking the three claims in turn.

### 1. The instrument is not disjoint — and the violation inflates rather than attenuates

`τ̂_IV` instruments `‖v̂*(t)‖` — a **central difference over `±Δ`**, i.e. labels `{t−Δ, t+Δ}` — with the
velocity from the pair `(t−2Δ, t−Δ)`, i.e. labels `{t−2Δ, t−Δ}`. **The label at `t−Δ` is in both sets.** With
i.i.d. box-centre noise `σ_c`:

```
η_X = (ε_{t+Δ} − ε_{t−Δ})/(2Δ)        Var(η_X) = σ_c²/(2Δ²)      [their own σ_η = σ_c/(√2 Δ) — correct]
η_Z = (ε_{t−Δ} − ε_{t−2Δ})/Δ          Var(η_Z) = 2σ_c²/Δ²
Cov(η_X, η_Z) = −σ_c²/(2Δ²)           corr(η_X, η_Z) = −1/2       [MC over 4×10⁶ draws: −0.5002]
```

The IV exclusion restriction `Cov(Z, η_X) = 0` fails by a **fixed correlation of −1/2**, independent of `Δ` and
of `σ_c`. The resulting probability limit is

```
plim τ̂_IV = τ · Var(v) / ( Var(v) + Cov(η_X, η_Z) ) = τ · Var(v) / ( Var(v) − σ_c²/(2Δ²) )   >  τ ,
```

i.e. the instrument **over-corrects**, and blows up (or changes sign) as `σ_c²/(2Δ²) → Var(v)`. On DSEC-Det
(`Δ = 50 ms`, image-speed spread taken as `sd(v) = 0.06 px/ms`):

| `σ_c` | `λ_att` (naive attenuation) | shared-anchor IV inflation |
|---|---|---|
| 1 px | 0.947 | 1.06× |
| 2 px | 0.818 | 1.29× |
| 3 px | 0.667 | **2.00×** |

At `σ_c = 3 px` — entirely plausible for QDTrack-generated boxes warped through a homography — the naive
estimator is 33 % too small and the proposed IV is 100 % too large. Both are wrong; a *strictly* disjoint
instrument is right.

This defect is worse than a bias because of the paper's own pre-registration: *"if `τ̂_IV` and `τ̂_naive` differ
by more than a factor of 1.5 we report the discrepancy as a finding about the labels."* At `σ_c = 3 px` the
ratio is `2.00/0.667 = 3.0` **from the estimator alone**, and the pre-registered rule would book an estimator
defect as a finding about the annotation pipeline.

*Fix, one line:* use a strictly disjoint quadruple — regressor from `{t, t+Δ}` or `{t−Δ, t+Δ}`, instrument from
`{t−3Δ, t−2Δ}`. Cost: zero.

### 2. Even when disjoint, the instrument's independence claim fails on the primary testbed — by the paper's own P7

The stated justification is *"measurement noise is independent across disjoint pairs while true speed is
strongly autocorrelated."* On DSEC-Det that first clause is false twice over:

- **Tracker error is autocorrelated.** DSEC-Det labels are QDTrack outputs on 20 Hz RGB, warped and cleaned. A
  tracker's box error at consecutive frames shares the appearance model, the regressor and the occlusion state.
  Independence across pairs 50 ms apart is an assumption about an annotation pipeline, and it is the *opposite*
  of what a tracker does.
- **Decisively: P7 says the inter-frame labels are exactly the linear interpolation of their anchors.** Inside
  one anchor interval every finite difference of the released labels is *identically* the anchor-to-anchor
  velocity. Regressor and instrument are then the same number, error and all: `Cov(η_X, η_Z) = Var(η_X)`,
  `corr = 1`, and the IV degenerates to OLS with no correction whatsoever. The IV is informative only for pairs
  that straddle anchors, i.e. only at `Δ ≥ 50 ms`, which is exactly where the shared-anchor defect of §1 bites
  hardest.

The paper's strongest label-forensics result and its headline estimator are **in direct tension**, and neither
section mentions the other. This has to be resolved in the text, not in a rebuttal.

### 3. Deming's variance ratio is not knowable here — but a bound is, and it is free

Deming with a known `λ = σ_ε²/σ_η²` is consistent. With `λ` estimated from the same data it is **not
identified**: for a single regressor with Gaussian errors, the EIV model is unidentified without external
information (Reiersøl 1950) — replication, an instrument, or non-Gaussianity of the true regressor. The paper
proposes `σ_η` from a measured `σ_c` (fine, if track residuals really estimate annotation noise rather than
object jerk) and `σ_ε` "from the residual". That second step is circular: `σ_ε` is the *along-track error that
is not timing*, which is the very decomposition being estimated; taking it from the residual of the attenuated
naive fit makes `λ` a function of the answer.

*Recommendation, free and assumption-light:* report the **Frisch/Gini bracket**. For a single regressor,

```
β_OLS(y | x)  ≤  τ_true  ≤  1 / β_OLS(x | y)
```

with the lower end being `τ̂_naive` (which they already print) and the upper end being the inverse reverse
regression — one extra line of code, no `λ`, no instrument, and a *guaranteed* bracket. Then report
`τ̂_Deming(λ)` as a sensitivity curve over the plausible `λ` range rather than as a point.

### 4. The smoothing-bias claim: right that it exists, wrong about its order and its driver

The claim: *"On Gen1 (Δ = 250 ms), a central difference returns the mean velocity over 500 ms, not `v*(t)`. …
it is correlated with acceleration and it is not fixed by Deming regression."*

- *"returns the mean velocity over the window"* — **correct**:
  `(p(t+Δ) − p(t−Δ))/(2Δ) = (1/2Δ)∫_{t−Δ}^{t+Δ} v`.
- *"not fixed by Deming"* — **correct**. It is a bias in the conditional mean of the regressor, not extra
  variance, and no error-variance-ratio method addresses it.
- *"correlated with acceleration"* — **FALSE for a central difference.** Taylor:
  `(p(t+Δ) − p(t−Δ))/(2Δ) = v(t) + (Δ²/6)·v̈(t) + O(Δ⁴)`. The acceleration term cancels by symmetry. Verified
  numerically: for `p(t) = t²` (constant acceleration) the central difference error is `−4.6e−15` at `Δ = 50 ms`
  and `+1.5e−14` at `Δ = 250 ms` — machine zero. For `p(t) = t³` the error is exactly `Δ²/6 · p'''` (2 500 and
  62 500, matching to all digits printed). **The central difference is exact under constant acceleration; its
  leading bias is `(Δ²/6)·jerk`.**

This matters both ways. It weakens the stated case against Gen1 — a `Δ²·jerk` term is third-order and on
smooth vehicle trajectories is much smaller than the paper implies. And it removes the stated ground for the
testbed switch, which the paper leans on in three places ("This is why DSEC-Det, not Gen1, is now the primary
testbed"). Two *better* grounds for the same decision survive and should be used instead: `w_G` is unpublished
on Gen1 so `τ_max` is a free parameter there (my round-one point, which they already accept), and Gen1 has no
track IDs so `σ_τ` is unavailable.

### 5. The real EIV problem on DSEC-Det is one the paper does not name

If P7 holds — released labels = linear interpolation of anchors — then between anchors the label trajectory has
**zero acceleration by construction**, so there is no measurement noise in `v̂` at all *relative to the labels*.
The error is not statistical, it is a **model error**: writing `r(s) = p(s) − ℓ(s)` for the interpolation
residual, with constant true acceleration `a` over an anchor interval of length `Δ`,

```
r(s) = −(a/2)(s − t₀)(t₁ − s) ,        mean over the interval  E[r] = −aΔ²/12 .
```

This term appears **in the outcome**, `e_∥ = τ‖v‖ + r(t) + …`, not only in the regressor, because the GT
position itself is wrong. Magnitudes, at a modest image acceleration `a = 10⁻³ px/ms²`:

| dataset | `Δ` | `aΔ²/12` | compare: the signal `τ‖v‖` at `τ = 25 ms, ‖v‖ = 0.1 px/ms` |
|---|---|---|---|
| DSEC-Det | 50 ms | 0.21 px | 2.5 px |
| Gen1 (if inter-label times were used) | 250 ms | **5.2 px** | 2.5 px |

On DSEC-Det it is ~8 % of the signal — tolerable, and it must be reported. Neither Deming nor IV touches it,
because it is an omitted variable correlated with the regressor, not classical measurement error. The honest
control is to run `τ̂` **at the anchor instants only** (where `r = 0` by construction) and compare against the
full inter-frame estimate; the difference is a direct measurement of how much of `τ̂` is the annotation prior.
That control is free and is missing.

### 6. Two smaller things the paper gets right, confirmed

- `σ_η = σ_c/(√2 Δ)` for a central difference over `±Δ`: **correct** (`Var = 2σ_c²/(2Δ)²`).
- *"the `‖v*‖·τ_max > 2 px` filter is a second speed-correlated bias in the same direction as attenuation"*:
  **correct**, and here is the mechanism they don't state. Selecting on the *noisy* `‖v̂‖` induces
  `E[η | selected] > 0`, so the retained sample's regressor is upward-biased and the slope is depressed beyond
  classical attenuation. This is why the filter's retained fraction must be published **with `τ̂` re-estimated
  at several thresholds**, not just the fraction.

---

## New propositions audited

### P-A. *"By construction `AP ≤ AP^sync`"* is false — CORRECT (my round-one finding stands), and my own correction was too generous

**Status of the attributed finding: CONFIRMED.** `AP^sync` re-anchors by `−τ̂_P·v̂_pred` with `v̂_pred` from the
method's own noisy consecutive outputs. Nothing constrains the result to improve. The team has adopted this and
now reports `Δ_clock` with its sign, which is the right response.

**The conditions under which `AP^sync` decreases**, which the paper does not state and should:

1. **Velocity-estimation noise, with a sharp threshold.** With `s = −τ̂ v̂`, `v̂ = v + ν`, true along-track error
   `e_∥ = τ‖v‖`, and `ν ⟂ e`:

   ```
   E[Δ(e²)] = −2 τ̂ τ S + τ̂² (S + N) ,     S = E‖v‖² ,  N = E‖ν‖²
   argmin over τ̂ :   τ̂* = τ · S/(S + N)      — the AP-optimal re-anchoring is itself ATTENUATED
   break-even at τ̂ = τ  ⟺  N = S  ⟺  SNR = 1 .
   ```

   So **applying the EIV-corrected `τ̂_IV` makes `AP^sync` worse than applying the attenuated `τ̂_naive`, at
   every SNR**, and strictly worse than doing nothing once `E‖ν‖² > E‖v‖²`. Numerically (`E[Δ(e²)]/τ²`): at
   SNR = 1, `τ̂_naive = 0.7τ` gives −0.42 while `τ̂_IV = τ` gives exactly 0.00; at SNR = 0.5 they give +0.07 and
   +1.00 — both harmful, the corrected one fourteen times more so. This is a **direct internal conflict**: §4.3
   makes `τ̂_IV` the headline and §4.4/C5 uses `τ̂_P` to re-anchor, and C5 is declared a falsification test
   ("if it does not recover most of `Δ_clock`, we report that our metric failed its own test"). Is the SNR
   order-1 here? `σ_ν = √2 σ_c/Δ` with `Δ = 50 ms` gives 0.028–0.085 px/ms for `σ_c` of 1–3 px, against an image
   speed distribution whose retained mass starts at `‖v‖ > 2/τ_max = 0.04 px/ms`. **SNR is plausibly between 1
   and 3** — squarely in the regime where C5 can fail for reasons that have nothing to do with whether `τ̂` is
   real. Required: measure `S` and `N` and print them beside `Δ_clock`, and re-anchor with `τ̂ S/(S+N)`.
2. **Anisotropic boxes.** A shift that strictly reduces the Euclidean centre error can strictly reduce IoU — see
   P-B, which applies verbatim to `AP^sync`.
3. **Threshold non-linearity.** AP is a threshold functional, not a mean-squared-error functional. Detections
   comfortably above IoU 0.5 gain no credit from being moved closer; detections just above it are lost when
   moved wrongly. The net is a difference of two near-threshold densities, not the sign of a mean improvement.
4. **Greedy matching.** See P-B.3.

*One further consequence worth a sentence in the paper:* `τ̃ := argmax_τ AP(shift by −τ v̂)` is a **third
estimator of the same scalar, obtained without ever dividing by `‖v*‖`** — hence immune to classical dilution
and to the whole EIV apparatus. Agreement between `τ̃` and `τ̂_IV` is a genuine over-identification test of the
same kind that made me pick this paper, it costs a 1-D CPU sweep of re-scores, and it is not in the plan.

### P-B. The `AP ≤ AP^⟂ ≤ AP^iso` chain — **CORRECT UNDER UNSTATED ASSUMPTIONS**, and my round-one statement that it holds "by construction" was itself too generous

I wrote in round one that *"only `AP ≤ AP^⟂ ≤ AP^iso` is by construction"*. Auditing my own finding: **that is
not right either**, under the definition v2 gives. §4.3 defines `AP^⟂` as translating each prediction along the
GT tangent *"by the amount minimising the distance"*. Two gaps.

1. **Minimising centre distance does not maximise IoU.** For axis-aligned boxes, IoU is monotone in `|dx|` and
   `|dy|` *separately*; projecting the error onto the tangent's orthogonal complement reduces `‖e‖` but can move
   error from a cheap axis to an expensive one. Worked counterexample: a pedestrian-shaped box `20 × 60 px`,
   error `e = (0, 8) px`, tangent `û = (1,1)/√2`. Then `‖e‖ = 8.00 → ‖e_⟂‖ = 5.66` (strictly better) while
   **`IoU = 0.7647 → 0.5957`** (strictly worse). Monte-Carlo over isotropic errors and random tangents:

   | box aspect | P(IoU decreases after the distance-minimising tangential shift) |
   |---|---|
   | 1:3 (pedestrian) | **21.3 %** |
   | 2:1 (vehicle) | 18.1 % |
   | 1:1 | 14.0 % |

   This is not a pathological corner; it is one detection in five, and the worst class is pedestrians, which is
   one of Gen1's two classes.
2. **Greedy matching is not monotone in IoU.** COCO assigns each detection, in score order, to the unmatched GT
   of highest IoU above threshold. Counterexample: det A (score .9) has IoU .70 with GT1 and .60 with GT2; det B
   (score .5) has .55 with GT2; threshold .5. Greedy gives A→GT1, B→GT2 = **2 TP**. Now *improve* A's IoU with
   GT2 from .60 to .80: greedy gives A→GT2, B unmatched = **1 TP**. A strict per-pair improvement lowers AP.

**Corrected statement, and it is a one-line fix.** Define the relaxation as *maximising IoU over the feasible
displacement set* rather than minimising centre distance. Then `{0} ⊆ tangent segment ⊆ disc`, per-pair IoU is
monotone in the feasible set, and — provided matching is **optimal (max-cardinality) rather than greedy** — the
cumulative TP count at every score rank is monotone, the PR curve dominates, and `AP ≤ AP^⟂ ≤ AP^iso` holds by
construction, exactly as advertised. Under the current definition it does not, and `R = (AP^⟂ − AP)/(AP^iso −
AP)` can come back negative or greater than 1, which is uninterpretable and would look like a bug rather than
the definitional artefact it is.

### P-C. `τ_max = (w_G + min(w_P^decl, w_P^meas))/2` — **FALSE as a conservative safeguard: the min is inert, and `w_P` is used inconsistently with its own definition**

Three findings, increasing in severity.

**(i) The `min` can never bind.** E1c's grid is `k ∈ {1,2,4,8,16,32,∞}` recurrent steps of 50 ms each, so
`w_P^meas ∈ {50, 100, 200, 400, 800, 1600, ∞} ms`. `w_P^decl = 50 ms`. Hence
`min(w_P^decl, w_P^meas) = 50 ms` **always**, for every checkpoint and every outcome of E1c. The safeguard
advertised in three separate places as the thing that guarantees "a wider measured support can never buy a more
flattering permissive score" is a no-op by construction of the measurement grid. It is not wrong; it is empty,
and the paper claims credit for it.

**(ii) `w_P` is defined as a 2σ and used as a full width.** §*The assumption we kill* defines
`w_P = 2√(∫(u−c_P)²k_P)`. For the uniform kernel on a 50 ms window that is `2·50/√12 = 28.87 ms`, not 50 ms. For
DSEC-Det's triangular interpolation kernel of half-width 50 ms it is `2·50/√6 = 40.82 ms`, not 50 ms. So

```
τ_max (as used, "full width")            = (50 + 50)/2       = 50.00 ms
τ_max (paper's own 2σ definition)        = (40.82 + 28.87)/2 = 34.85 ms      — 30 % smaller
```

`τ_max` multiplies the relaxation budget, the stratifier `M = ‖v*‖τ_max/d`, and the `‖v*‖τ_max > 2 px` filter
threshold. A 30 % ambiguity in a quantity the paper repeatedly calls "derived, not a free parameter" is a
definitional debt, not a rounding issue. Pick one and use it everywhere.

**(iii) `(w_G + w_P)/2` is the correct maximal centroid separation only for kernels *centred* on `t`.** If both
kernels' centroids are free within symmetric windows of full widths `W_G, W_P` about `t`, the centroid
difference ranges over `±(W_G + W_P)/2` and the formula is tight. But RVT's kernel is **strictly causal**: the
window is `[t−50, t]`, so `c_P ∈ [−50, 0]` and the difference `c_P − c_G` ranges over `[−50 − W_G/2, +W_G/2]`,
an asymmetric interval. The formula is correct for DSEC-Det's symmetric triangular `k_G` and incorrect for the
predictor side of every event detector in the pool. State the one-sided version.

**Is it conservative in the required direction?** Not uniformly, and it cannot be, because one symbol serves
three roles with different signs:

| use of `τ_max` | smaller `τ_max` ⇒ |
|---|---|
| relaxation cap in `AP^⟂`/`AP^iso` | less forgiveness — **conservative** ✓ |
| stratifier `M`, and P5 ("≥ 5 % of `M` > 0.3") | fewer high-`M` objects — **conservative** ✓ |
| filter `‖v*‖τ_max > 2 px` | stricter cut ⇒ more speed-selection ⇒ `|τ̂|` depressed — conservative for the magnitude claim, but **`n` falls and CIs widen** |

That last row is the one that inverts. The paper has four kill criteria of the form *"the CI contains 0, so we
report the null branch as a finding"* (K1, K3, K4, K5). For those, a smaller `n` and a wider CI make the
"publishable null" **easier to obtain**. A shrinking `τ_max` is therefore conservative for every positive claim
and **anti-conservative for every negative one**, and the negative branches are the ones the paper says it will
publish. Fix: fix the filter threshold in *physical* units (px/ms) independent of `τ_max`, and report `τ̂` and
`σ_τ` as functions of it.

### P-D. `σ_τ` and its permutation null — **FALSE: the permutation is not exchangeable under the relevant hypothesis, and §4.6 and P8 state the test in opposite directions**

**(i) Internal contradiction, decidable by reading the two sentences side by side.**

- §4.6: *"If within-frame dispersion is **not detectably smaller** than this across-frame dispersion, there is
  no frame-level clock coherence, `σ_τ` carries nothing, and we drop it (K5)."*
- P8 / K5: *"`σ_τ,excess ≥ 3 ms` … **exceeding** its permutation null with a bootstrap CI excluding 0"* /
  *"does not **exceed** the permutation null ⇒ drop"*.

These are opposite inequalities on the same statistic against the same null. One of them has to go.

**(ii) The deeper problem: the permutation tests the wrong hypothesis.** The alternative that motivates `σ_τ`
(Death 4, §*What existing methods cannot express* item 3) is *"a single output tensor carries several
timestamps, and a declared scalar cannot cancel a dispersion."* That requires **within-frame excess dispersion
above the estimator noise floor** — and nothing else. The permutation null tests something different: whether
the *frame* is a meaningful grouping, i.e. whether there is frame-level clustering of `δ̂`. The two come apart in
both directions:

- Within-frame ≪ across-frame (the §4.6 pass condition) means the frame **has** a coherent clock — which is
  exactly the case where a declared per-frame scalar timestamp *does* cancel it, i.e. the reporting-contract
  answer wins and Death 4's escape closes.
- Within-frame ≈ across-frame (the §4.6 fail condition, which drops `σ_τ`) is fully consistent with large
  within-frame excess dispersion, i.e. with the Death-4 claim being **true**. §4.6's kill rule would discard
  `σ_τ` in a world where its motivating claim holds.

The right instrument is a two-level variance decomposition — per-method constant, per-frame random effect,
per-object residual — with the propagated per-object estimator variance subtracted from each level. The
per-frame term is what the reporting contract can cancel; the per-object residual is Death 4's escape. The
permutation null estimates only the middle term.

**(iii) Exchangeability fails even under H₀**, for two independent reasons, so rejection does not license the
temporal reading:

- **Objects in a frame share ego-motion.** Speeds within a frame are strongly dependent (common ego-velocity,
  common depth structure), so `{δ̂_i}` are not i.i.d. within a stratum even under H₀. Since
  `Var(δ̂_i) ≈ σ_e²/‖v_i‖²`, a permuted "frame" mixes speed regimes that never co-occur, inflating the null.
  Stratifying on the *marginal* speed decile does not fix a within-set *composition* effect.
- **Frame-level spatial nuisances are not clocks.** A moment of ego-rotation, a homography/parallax error, a
  rolling-shutter row offset, or an RGB-branch blur event shifts *all* boxes in a frame coherently. Divided by
  each object's own `‖v_i‖`, that produces exactly the within-frame `δ̂` coherence the permutation is designed to
  detect. The permutation cannot distinguish a frame-level clock from a frame-level warp. C2's near-zero-
  intercept check is the right idea but is a *global* check, not a per-frame one.

**(iv) `σ_τ` is the dispersion of a ratio estimator and its population variance may not exist.**
`δ̂_i = e_∥,i/‖v̂_i‖` is a ratio of two noisy quantities; as the denominator's noise becomes comparable to its
mean, the distribution acquires Cauchy-like tails and `Var` diverges. Simulation (`v` lognormal with median
0.06 px/ms, `τ = −25 ms`, along-track noise 1.5 px):

| filter `‖v̂‖ >` | kept | `sd(δ̂)` | robust (1.4826·MAD) |
|---|---|---|---|
| 0.005 px/ms | 99.9 % | 45.7 ms | 22.7 ms |
| 0.010 | 98.7 % | 40.9 | 22.3 |
| 0.020 | 91.5 % | 31.7 | 20.4 |
| 0.040 | 69.4 % | 21.1 | 16.1 |
| 0.080 | 36.0 % | 12.5 | 10.6 |

`sd(δ̂)` moves by **3.7×** across plausible filter thresholds while the robust scale moves by 2.1×. P8's
pre-registered *"`σ_τ,excess ≥ 3 ms`"* is therefore a statement about the filter, not about the data, until the
threshold is fixed and justified. Required: use a robust dispersion, and publish `σ_τ` as a curve in the filter
threshold. The `σ_δ̂,i²` subtraction must also carry the denominator term,
`σ_δ̂² ≈ σ_{e∥}²/‖v‖² + (e_∥²/‖v‖⁴)σ_v²`, whose second piece scales as `‖v‖⁻⁴` and dominates.

**(v) The resampling unit contradicts §4.5.** §4.5 declares the exchangeable unit to be *the sequence*. §4.6
permutes objects across frames *within* a sequence and treats them as exchangeable. Both cannot be right.

### P-E. *"A null slope is publishable"* — **CORRECT IN FORM, UNFALSIFIABLE IN SUBSTANCE as currently specified**

This is a genuine pre-registration by the formal criteria: K4 names the statistic, the threshold (slope CI
contains 0), the date (2026-10-19), the fallback text, and it commits the *abstract* to change. That is more
than most CVPR submissions do and it should be credited. It is also not a blanket hedge, because the paper does
retain outcomes that kill it (K1, K3, K6, K8).

But the null branch is **under-identified**. A null slope on Panel C has at least four causes:

1. `τ̂` is dataset-driven — the branch they pre-register;
2. the levers do not vary the estimand — the crux above, which by my table produces slopes of −0.05 and −0.01
   for perfectly ordinary partially-extrapolating networks;
3. the networks *do* compensate their own support, so `τ*(w) ≈ 0` for all `w` — a genuine scientific finding
   that **contradicts the paper's thesis**, and which the pre-registration does not name at all;
4. low power, made worse because the effective `n` is four manipulation types, not twelve points.

Pre-registering one of four readings of a null is not a pre-registration of the null. Two further gaps:

- **K4's fallback sentence requires the intercept, and K4 does not mention it.** *"Every published number on
  this benchmark is scored against labels offset by X ms"* is only true if the intercept CI excludes 0.
  Null slope *and* null intercept is "no effect at all", which is K3, not K4. K4 must be stated as a joint
  condition on (slope, intercept).
- **Cause 2 is testable in advance and should gate Panel C.** A lever earns a point on Panel C only if it moves
  the *measured influence centroid* `c_P` (from E1b's occlusion) by an amount consistent with its nominal
  `w_P`. Lever 3 will fail that gate immediately; lever 2 will fail it wherever `count_cutoff` saturates.

**Verdict: CORRECT UNDER UNSTATED ASSUMPTIONS** — the assumptions being (a) intercept ≠ 0 and (b) the levers
are valid manipulations. Under my crux finding (b) fails for two of three, and the design as it stands cannot
distinguish its own two pre-registered branches.

---

## Was my objection closed

### Objection 1 (C3 has no predictor variance) — **NOT CLOSED**, and I concede one third of their rebuttal

Their rebuttal has three legs. I take them in order, and I lose one of them.

**Leg 2 — cost. They are right and I was wrong.** RVT's published Gen1 budget is ~2 days on an A100, against a
*shared* 5090 with a self-imposed 7 GB ceiling. Three retrainings is 60–120 GPU-h. My round-one "~8 GPU-h,
well inside budget" was low by roughly an order of magnitude and I withdraw it without reservation. **Required
fix #1 of my round-one review, as written, was bad advice and the team was right to refuse it.**

**Leg 1 — gating. Not established, and false for the primary testbed.** §8.6 states *"`experiments/e03`
establishes that only the preprocessed form bypasses registration"*. `experiments/e03/README.md` contains
**nothing about Prophesee, GEN1, or registration**; it covers FE108/FE240hz and BS-ERGB only. The substantive
claim about raw GEN1 is probably true in the world, but it is not established by the artefact cited, and the
paper cites it three times. More importantly it is **irrelevant to the primary testbed**: DSEC events are open
and already on this machine (`e00/PIPELINE_CHECK.md`: 455.6 M events downloaded, µs timestamps, `/ms_to_idx`
random access, event and exposure clocks aligned to 689 µs). Any `dt` can be built on DSEC today. And —
decisively — **the training-based fix I now recommend needs no raw events at all**, because masks are applied
to the *stored* tensor. Leg 1 does not defend the design.

**Leg 3 — "the within-subject manipulation is the better experiment, not merely the cheaper one." False.** A
within-subject design is cleaner only when the treatment changes the factor of interest and nothing else.
Masking changes support **and** evidence quantity **and** input distribution **and** the match between the
estimator and its input; §1–§2 above quantify a 26× discrepancy from the last of these alone. Between-subject
retraining carries optimisation noise, but each of its points is an on-distribution, deployable predictor —
which is the population Death 3 is actually about. A masked RVT is not a member of that population and its
`τ̂` is not a draw from it.

So: the objection is not closed. Panel C, the experiment built to close it, currently regresses on an axis whose
units change between points, and its slope is manufactured by the smoother assumption where it is not
manufactured by staleness.

### Objection 2 (errors-in-variables) — **PARTIALLY CLOSED**

Accepted in the right spirit; the machinery is the right machinery; three defects, all cheap:

- the IV's two label pairs share the label at `t−Δ` (`corr(η_X, η_Z) = −1/2`, over-correction up to 2.0× at
  `σ_c = 3 px`) — fix by using strictly disjoint quadruples, cost zero;
- Deming's `λ` is not identified from the data proposed — replace the point estimate with the Frisch bracket
  plus a `τ̂(λ)` sensitivity curve, cost one line;
- the smoothing-bias claim mis-states the order (central difference is exact under constant acceleration;
  leading bias `Δ²·jerk/6`), and the interpolation-residual term `−aΔ²/12` — which enters the **outcome**, not
  the regressor — is the term that actually matters and is unnamed.

The direction of the correction is stated honestly (corrections make `|τ̂|` larger, pre-registered against),
which is exactly right, and it is one of the better-argued paragraphs in the round.

---

## Verdict

### **WEAK ACCEPT** — down from my round-one ACCEPT, and still the strongest mathematics in the round.

The reason for the downgrade is narrow and specific. In round one I wrote that the retrained-`w_P` experiment
was *"not fatal but mandatory, because without it C3 has no predictor variance and Death 3 is unanswerable."*
The team has replaced it with a substitute and declared the objection **resolved** in the response table. It is
not resolved. Declaring a repair complete when the repair does not measure the target is a different and worse
position than declaring the experiment out of budget, which is what leg 2 of their own rebuttal honestly
establishes.

What still holds, and holds strongly:

- **The over-identification argument is untouched.** One scalar `δ` must explain translation and scale (and yaw
  in 3D) simultaneously; a spatial error has 2 or 7 DoF. That is still the best piece of estimation theory in
  this round, and P-A's `τ̃ = argmax_τ AP^sync` gives it a **third**, division-free channel for free.
- **E0 is immune to every objection in this review** and is correctly scheduled first. It requires no model, no
  GPU, no estimator and no `w_P`, and both of its outcomes are findings.
- The response to R3 on `AP^⟂` — *"we do not answer this; we comply with it"* — is the right response, and
  demoting the ranking flip out of the headline was correct.
- Conceding the bias half of R7's "so what" in the paper's own words, rather than defending it, is the kind of
  thing that makes a submission survive rebuttal.

What is now on the record as wrong or empty, none of it fatal, all of it one-line:

| # | Item | Status |
|---|---|---|
| 1 | Two of three "free levers" do not vary temporal support; the third does so only under the hypothesis under test | crux, must be fixed |
| 2 | `count_cutoff: 10` in `stacked_hist.yaml` — the re-binning lever's additivity premise is **false** on the released tensor, and fails hardest on the fast objects | verified from source |
| 3 | The IV's "disjoint" label pairs share a label; `corr = −1/2` | must be fixed |
| 4 | `min(w_P^decl, w_P^meas)` is inert: E1c's grid starts at 50 ms | claim credit withdrawn |
| 5 | `w_P` defined as 2σ, used as a full width — a 30 % ambiguity in `τ_max` | pick one |
| 6 | §4.6 and P8/K5 state the `σ_τ` test in **opposite** directions | one must go |
| 7 | The permutation null tests frame-clustering, not the alternative that motivates `σ_τ` | wrong instrument |
| 8 | `AP ≤ AP^⟂` requires an IoU-maximising relaxation and optimal (not greedy) matching; under the stated definition IoU falls in 21 % of pedestrian cases | my own round-one correction, corrected |
| 9 | "Central-difference smoothing bias is correlated with acceleration" — false; it is `Δ²·jerk/6` | restate |
| 10 | `e03` does not establish the Prophesee gate it is cited three times for | re-cite or measure |

None of these is of the kind that killed Teams 02, 03, 05 and 10 in round one — a false proposition at the
centre of the thesis. Every one is a specification error in scaffolding around a thesis that is still correct
and still falsifiable. That is why this is a WEAK ACCEPT and not a BORDERLINE.

---

## Minimum change to reach ACCEPT

Five changes. Together they cost **~9 GPU-h — inside the plan's own 9 GPU-h contingency line — plus about a day
of CPU.** No gated dataset, no raw Prophesee, no retraining from scratch.

**1. Fine-tune at each mask level. This is the whole difference between an ablation and a support axis. (~9 GPU-h.)**

Masks are applied to the **stored** tensor, so training on masked input needs no raw events and no
`preprocess_dataset.py` re-run — leg 1 of the §8.6 rebuttal does not apply to it. Take RVT-T (4.41 M params,
already loading cleanly per `e04`), and for `j ∈ {0, 4, 6, 8, 9}` fine-tune the released checkpoint for a short
schedule on masked inputs — ~1.5–2 GPU-h each at Gen1's 240×304 and batch 4. Each result is an **on-distribution,
deployable predictor whose support really is `5(10−j)` ms**, which is the population Death 3 asks about. Then
report both curves:

```
τ̂_frozen(w)      — the fixed checkpoint on ablated input          (what v2 currently plans)
τ̂_finetuned(w)   — a predictor matched to its own support         (the estimand Panel C needs)
Δ(w) = τ̂_frozen − τ̂_finetuned  —  the network's support-compensation capacity
```

`Δ(w)` is not overhead; it is a **new result**, and it is the one quantity in this design that measures whether
event detectors compensate their own temporal support at all. My §2 table says `Δ` can reach a factor of 26 —
if the real `Δ` is near zero the paper gets its slope *and* the demonstration that the frozen lever was valid;
if `Δ` is large the paper gets a better finding than the one it was chasing. Keep "all primary numbers come
from released checkpoints; one control fine-tunes for 9 GPU-h" — that sentence costs nothing and buys the
objection.

**2. Rebuild Panel C on the measured influence centroid, and make the intercept the headline. (CPU, free.)**

Replace the x-axis. Points enter Panel C only if E1b's per-bin occlusion shows the manipulation actually moved
`c_P`. Regress

```
τ̂  =  τ_G  +  β · c_P^meas ,     pre-register β = 1 (not 1/2) and report the INTERCEPT with its CI.
```

`τ_G` is the dataset-level annotation offset, identified as the intercept, and it is what Death 3 has been
asking for since round one. Delete lever 3 from the axis entirely and report it where it belongs — as a
staleness measurement, next to the sAP discussion. Delete lever 2 or first verify `count_cutoff` on a stored
file and report the saturated-pixel fraction stratified by object speed; if the fraction is non-trivial in the
top-`M` decile, lever 2 is unusable and must go.

**3. Add the two free real-data controls that the kinematic rig cannot give. (CPU, free.)**

- **Window translation.** Concatenate two consecutive stored windows, take any contiguous 10-bin sub-window
  ending at `t − 5m`, score against the label at `t`. This shifts `τ̂` by exactly `−5m` **by construction**, at
  constant width and constant evidence quantity — a real-data, real-network injection–recovery test of the
  `δ̂ = e_∥/‖v̂*‖` estimator that is strictly stronger than E4's synthetic rig for C4. It is *not* a support
  lever and must not appear on Panel C.
- **Anchor-only `τ̂`.** On DSEC-Det, estimate `τ̂` at the 20 Hz anchor instants only, where the interpolation
  residual `r` is zero by construction, and compare against the full inter-frame estimate. The difference
  measures directly how much of `τ̂` is agreement with the annotation prior — which is E0's thesis, applied to
  the paper's own estimator.

**4. Repair the three estimator specifications. (CPU, an afternoon.)**

- IV on **strictly disjoint** label quadruples (regressor `{t−Δ, t+Δ}`, instrument `{t−3Δ, t−2Δ}`); print
  `corr(η_X, η_Z)` for the pair actually used.
- Replace point-Deming with the **Frisch bracket** `[β_OLS(y|x), 1/β_OLS(x|y)]` plus a `τ̂(λ)` sensitivity curve.
- Re-anchor `AP^sync` with `τ̂·S/(S+N)` and print `S = E‖v‖²` and `N = E‖ν‖²`; add `τ̃ = argmax_τ AP^sync` as a
  third, division-free estimator and test it against `τ̂_IV` — this is a new over-identification channel and it
  costs a 1-D CPU sweep.
- Correct the sentence about central-difference smoothing bias to `(Δ²/6)·v̈`, and add the interpolation
  residual `−aΔ²/12` in the **outcome**.

**5. Fix the four definitional debts. (Text only.)**

- Define the relaxation as **IoU-maximising over the feasible displacement set** and state that the chain
  `AP ≤ AP^⟂ ≤ AP^iso` requires optimal rather than greedy matching; report both matchings if COCO's evaluator
  is used unmodified.
- Pick one meaning of `w_P` (2σ or full width) and propagate it through `τ_max`, `M`, and the filter; state the
  **one-sided** centroid bound for causal predictor kernels.
- Drop the claim that `min(w_P^decl, w_P^meas)` is a safeguard, or change E1c's grid so it can bind.
- Resolve §4.6 versus P8: state `σ_τ` as a two-level variance decomposition against the **estimator noise
  floor**, use a robust scale, publish it as a function of the speed filter, and demote the permutation to what
  it actually tests — whether the frame is a meaningful grouping — noting that a frame-level *spatial* nuisance
  produces the same signature.

With (1) and (2) done, my round-one objection is genuinely closed rather than declared closed, Panel C measures
one quantity in one unit across all its points, and the paper's answer to Death 3 becomes an identified
intercept rather than an argued-for slope. At that point this is an **ACCEPT** again, and by a clear margin —
it remains the only entry in this round whose central claim is over-identified, and therefore the only one that
can be wrong in public.
