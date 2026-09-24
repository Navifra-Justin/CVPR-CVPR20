# E56/E57 — what timing difference can this benchmark resolve at all? (2026-09-16)

## Why this exists

Review #8's objection has two halves. The timing correction moves mAP by 0.0004, and it
reorders no checkpoint. Both are true. E58 answers them from one side, by finding a place where
the same unidentified support is worth several mAP points of a released number. E56 answers them
from the other side, by asking what the objection is implicitly assuming: that a displacement
too small to move the ordering is a displacement that does not matter.

That assumption is testable, and it fails. **The ordering it leaves intact is not resolved to
begin with.** A cluster bootstrap over the 406 validation sequences reproduces the published
ordering in 42.5 % of replicates on the population a released Gen1 number is reported over, and
the tightest adjacent pair inverts in 48 % of them. An invariance to a 24 ms displacement is not
evidence that 24 ms is unimportant; it is a measurement of the resolution of the metric, and
that resolution is coarse.

## The evaluator, and what licenses its numbers

`e56_eval.py` is E52's mAP-vs-displacement evaluator, unchanged in semantics, factored out so
the wide sweep, the bootstrap and the rank test all score through one function. E52 was itself
pinned against E37b, an independently written evaluator. `e56_selftest.py` re-runs those four
pins against this copy and is the precondition for quoting anything here:

```
delta   +0.000 ms   got 0.334580   pinned 0.334580   ok
delta  -23.810 ms   got 0.334193   pinned 0.334193   ok
delta  -25.000 ms   got 0.333990   pinned 0.333990   ok
delta  -10.000 ms   got 0.334632   pinned 0.334632   ok
4/4 agree
```

`e56_seqmap.py` recovers the frame → sequence map that E51's dump did not emit, replaying the
dump's own admission rule from the label and index files alone, and is accepted only when the
frame total matches the dumps: **406 sequences, 20 296 frames**. The cluster bootstrap resamples
those sequences, because frames inside one sequence are not independent.

## The scaling identity that makes one sweep answer two questions

The intervention moves every ground-truth box by `delta * v` with `v` that box's own centered
label velocity, so it depends on `delta` and `v` only through their product:

    mAP(k * delta ; velocities v)  ==  mAP(delta ; velocities v / k)      exactly

Sweeping `delta` past the measured interval is therefore the same experiment as holding the
interval fixed at `tau = 23.81 ms` and asking what a benchmark would report if its objects moved
`k = delta / tau` times faster. Detections never move, so nothing here is a statement about a
detector; it is a statement about what the metric can see at a given label composition.

## Two standard errors, answering two different questions (`e56b`)

| | `rvt-t` | `rvt-s` | `rvt-b` | `s5vit-small` | `s5vit-base` |
|---|---:|---:|---:|---:|---:|
| SE(mAP), pt — the bar on a *published* number | 2.227 | 2.453 | 2.815 | 2.186 | 2.354 |
| SE(ΔmAP), pt — the bar on a *within-paper* difference | 0.0501 | 0.0351 | 0.0447 | 0.0579 | 0.0459 |
| displacement cost at `tau`, pt | 0.0414 | 0.0713 | 0.0619 | 0.0632 | 0.0808 |
| smallest interval resolvable, paired | 17.2 ms | 14.5 ms | 13.7 ms | 19.8 ms | 18.7 ms |
| smallest interval resolvable, between papers | 163 ms | 174 ms | 166 ms | 160 ms | 153 ms |

The two rows differ by an order of magnitude because scene difficulty cancels in a paired
difference and does not cancel between two papers scored on different resamples. The honest
reading of the 0.0004: it is **at** the paired resolution limit and two orders of magnitude
below the absolute one. A published event-detection mAP does not resolve a tenth of a second.

## The timing difference that would move the ordering (`e56c`)

Two detectors differing only in effective output time differ in their boxes by
`(tau_i - tau_j) * v` pixels, which the metric registers as a loss. So an ordering responds to a
timing difference only once that loss exceeds the published gap:

    D*_ij = min { |D| : L_j(D) >= G_ij }

| stratum | published order | tightest adjacent pair | D* | in units of `tau` |
|---|---|---|---:|---:|
| all moving | rvt-b, rvt-s, rvt-t, s5vit-base, s5vit-small | rvt-s / rvt-t | 43.7 ms | 1.83 |
| 10–25 px/s | s5vit-base, rvt-b, rvt-t, s5vit-small, rvt-s | rvt-t / s5vit-small | 33.5 ms | 1.41 |
| 25–50 px/s | s5vit-base, rvt-b, s5vit-small, rvt-s, rvt-t | rvt-b / s5vit-small | 11.2 ms | 0.47 |
| > 50 px/s | rvt-b, rvt-t, s5vit-small, rvt-s, s5vit-base | s5vit-small / rvt-s | 26.4 ms | 1.11 |

Note the ordering is not the same in any two strata. That instability is attributed to object
speed, not to temporal support, and is reported as such — it is more than ten times the largest
alignment effect, and presenting it as a consequence of this paper's mechanism would have been
the easy overclaim.

## Is the published ordering resolved at all? (`e56d`)

`e56b` gives SE(mAP) ≈ 2.2–2.8 points, which is the right floor for a number computed on a
different sample and the wrong floor for comparing two checkpoints scored on the *same*
sequences. The honest quantity is SE(mAP_i − mAP_j) formed inside each replicate. B = 200,
clustered on sequences, both populations scored:

**Every labelled box** — the population a released Gen1 number is reported over:

| adjacent pair | gap, pt | SE(Δ) | P(inverts) |
|---|---:|---:|---:|
| rvt-b > rvt-s | 2.636 | 0.328 | 0.00 |
| rvt-s > s5vit-base | 0.734 | 0.514 | 0.095 |
| **s5vit-base > rvt-t** | **0.050** | 0.529 | **0.48** |
| rvt-t > s5vit-small | 3.346 | 0.431 | 0.00 |

**Full ordering held in 42.5 % of replicates** (80.5 % on this paper's moving subset, where the
gaps are wider). A coin-flip pair sits in the middle of a published leaderboard. The
displacement's failure to reorder anything is therefore not the null result it looks like —
there is no resolved ordering there for it to disturb.

## The label composition that decides whether any of this is visible (`e57`)

What an IoU-thresholded metric registers is displacement *relative to box size*, so the
scale-free quantity is

    r = |v| / sqrt(w * h)            box-widths of motion per second

`r` is invariant to sensor resolution, so benchmarks at different resolutions compare directly
on it. A timing error `tau` displaces a box by `tau * r` box-widths.

| benchmark | n boxes | median `r` | median speed px/s | median size px | vs Gen1 |
|---|---:|---:|---:|---:|---:|
| Gen1, all moving | 27 943 | 0.095 | 4.0 | 41.5 | 1.0× |
| Gen1, 25–50 px/s | 2 096 | 0.641 | 32.3 | 53.5 | 6.8× |
| Gen1, > 50 px/s | 337 | 0.866 | 57.4 | 68.5 | 9.1× |
| DSEC-Det, train | 290 163 | 1.314 | 32.0 | 23.9 | **13.9×** |
| DSEC-Det, test | 86 586 | 1.043 | 26.9 | 25.4 | 11.0× |

Gen1's ordering needs 1.83× its current composition before `tau` moves it. DSEC-Det already has
13.9×. The invariance this paper measures is a property of Gen1's label composition, not a
property of event detection, and the composition that would break it exists today.

The median is the natural summary to reach for and it is the wrong one; the next section
measures which summary actually governs the resolution, and repeats this comparison on it.

## What actually sets the resolution: the tail, not the typical object (`e56e`)

E56a was written to feed three questions. Two are answered above. The third — whether the four
strata collapse onto one curve once δ is scaled by each stratum's own speed — turns out to
answer a question the paper needed more than the one it asked.

### The obvious rescaling, and its failure

A δ-second timing error moves a box `δ·r` box-widths, and an IoU matcher sees box-widths and
nothing else, so the loss curve `L(δ) = 1 − mAP(δ)/mAP(0)` ought to collapse when plotted
against `δ · r_median`. Gen1's strata span 9× in `r_median`, which is ample lever arm.

It does not collapse. It **anti-collapses**: rescaling by the median leaves the strata three
times *more* dispersed than leaving δ in milliseconds, and no fixed quantile of `r` repairs it
— the best single choice is the 85th percentile and it is still worse than not rescaling at
all. The raw fact underneath, `D` being the δ at which a stratum loses 5 % of its mAP:

| | all moving | 10–25 px/s | 25–50 px/s | > 50 px/s | CV |
|---|---:|---:|---:|---:|---:|
| `r_median` | 0.095 | 0.358 | 0.641 | 0.866 | — |
| **D (ms), `rvt-t`** | 95.0 | 85.2 | 61.0 | 67.4 | 0.204 |
| **D (ms), `s5vit-base`** | 85.0 | 80.0 | 58.7 | 67.2 | 0.165 |

Median displacement rate varies by 9×; the loss timescale varies by ±20 % and is not even
monotone in speed.

### The model that does collapse

mAP is not an average over boxes, it is a threshold on each box. Take the crudest model: a box
drops its match once displaced past a fixed `d*` box-widths, and is untouched before. Then
`L(δ) = P(r > d*/δ)`, so

```
D(L = p)  =  d* / Q_{1−p}(r)
```

and the scale-setter is the **(1−p) quantile of r, matched to the loss level being read off** —
not the median, and not any fixed quantile. With it the strata collapse:

| scale-setter | CV at L=0.05 | CV at L=0.10 | CV at L=0.25 |
|---|---:|---:|---:|
| none (raw ms) | 0.209 | 0.216 | 0.261 |
| × `r_median` | 0.599 | 0.594 | 0.564 |
| × `Q_85(r)` — best fixed | 0.291 | 0.294 | 0.259 |
| **× `Q_{1−p}(r)` — level-matched** | **0.042** | **0.100** | 0.276 |

(three strata × five checkpoints; `> 50 px/s`, n = 337, is excluded and discussed below)

The collapse constant is **d\* = 0.0628 ± 0.0029 box-widths** at the 5 % level. That is the
right number on independent grounds: displacing a square box by a fraction `d` of its width
gives `IoU = (1−d)/(1+d)`, so `d* = 0.063` is the displacement that breaks a match at **IoU
0.882** — inside the 0.50 : 0.05 : 0.95 range this mAP averages over, near its top, which is
exactly where the first 5 % of loss should come from. The model degrades as expected at larger
losses (CV 0.10 at 10 %, 0.28 at 25 %), where the single-threshold caricature stops holding.

The `> 50 px/s` stratum is the one outlier at every level, running ~1.8× above `d*`. Its 337
boxes are not the explanation — the gap is far outside anything a quantile estimated from 337
samples can produce. The likely cause is saturation: that stratum's mAP(0) is 11.8–14.5 against
29–37.6 elsewhere, so much of its high-IoU headroom is already spent on localisation error and
a displacement cannot cost what was never there. It is recorded as unexplained rather than
argued away.

### Why this matters to the paper

It closes an escape hatch. A reader can grant that the 23.81 ms correction moves Gen1's mAP by
0.0004 and still say this is a fact about Gen1's slow objects rather than about benchmarks —
so use faster objects and the metric will resolve timing fine. The measurement says timing
resolution is bought from the **upper tail** of the displacement-rate distribution, and a tail
is the most expensive thing in a dataset to buy:

| stratum | n | `Q95(r)` | resolution gain | SE inflation | net |
|---|---:|---:|---:|---:|---:|
| all moving | 27 943 | 0.701 | 1.00× | 1.00× | 1.00× |
| 10–25 px/s | 5 356 | 0.713 | 1.02× | 2.28× | 0.44× |
| 25–50 px/s | 2 096 | 1.077 | 1.54× | 3.65× | 0.42× |
| > 50 px/s | 337 | 1.724 | 2.46× | 9.11× | **0.27×** |

Resolution improves as the quantile; the standard error grows as 1/√n. **Every stratification
of Gen1 loses that race** — the fastest stratum buys 2.5× in resolution and pays 9.1× in noise.
The paper's argument therefore cannot be rescued, and does not need to be rescued, by picking
faster objects out of the same benchmark.

It also corrects the comparison in the section above, which used medians. On the quantity that
actually governs resolution the gap is smaller than 13.9× — and the conclusion is stronger,
because a different benchmark buys the tail without paying for it in sample size:

| population | n | median `r` | `Q95(r)` | median ratio | **`Q95` ratio** | net of √n |
|---|---:|---:|---:|---:|---:|---:|
| Gen1 (all moving) | 27 943 | 0.095 | 0.701 | 1.00× | 1.00× | 1.00× |
| DSEC-Det (train) | 290 163 | 1.314 | 5.590 | 13.88× | **7.97×** | **25.7×** |
| DSEC-Det (test) | 86 586 | 1.043 | 4.704 | 11.01× | 6.71× | 11.8× |

## Files

- `e56_eval.py`, `e56_selftest.py` — the shared evaluator and the four pins that license it
- `e56_seqmap.py` → `seqmap.json` — frame → sequence, 406 units, replayed from the index files
- `e56a_wide_sweep.py` → `wide_sweep.json`, `wide_sweep.log` — the sweep, under the scaling identity
- `e56b_bootstrap.py` → `bootstrap.json`, `bootstrap.log` — SE(mAP) and SE(ΔmAP), clustered
- `e56c_resolving.py` → `resolving.json` — D* per stratum and the composition it implies
- `e56d_rankse.py` → `rankse.json`, `rankse.log` — does the published ordering survive resampling
- `e57_composition.py` → `composition.json` — `r` for Gen1 and DSEC-Det
- `e56e_collapse.py` → `collapse.json`, `collapse.log` — the stratum collapse test, the
  level-matched-quantile model, and the cost of buying resolution from the tail
