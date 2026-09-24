# E26 — is the gradient alignment a per-object quantity, or ego-motion?

## Why this exists

E25 found that the evidence-time gradient aligns with label velocity *more strongly where
objects move slower* (r = −0.91 against the fraction of boxes above 20 px/s). A per-object
motion signal should behave the other way round. The obvious alternative is deflationary: a
labelled box contains background as well as object, the whole image sweeps under ego-motion,
and for a slow object the label velocity is nearly the background velocity — so the alignment
would be with the scene, not with the object, and the per-object reading would be wrong.

## The decisive control

For each box compute the evidence-time gradient three ways and align each with the **same**
label velocity:

| region | what it contains |
|---|---|
| **BOX** | all events inside the labelled box |
| **CORE** | inside the box eroded by 25 % on each side — object-dominated |
| **RING** | a surrounding annulus of equal area, box excluded — background only |

If RING aligns as well as BOX, the signal is ego-motion. If CORE > BOX > RING, it is the object.
Equal area is the point of the ring: it holds the estimator's variance fixed so the three
numbers are comparable.

## Unpaired result (`result.json`, cos / n / σ)

| sequence | BOX | CORE | RING |
|---|---|---|---|
| `zurich_city_00_a` | +0.2406 (2734, 12.6σ) | +0.2417 (1681, 9.9σ) | +0.2694 (2269, 12.8σ) |
| `zurich_city_09_a` | +0.1518 (6627, 12.4σ) | +0.1229 (5336, 9.0σ) | +0.0756 (6425, 6.1σ) |
| `zurich_city_10_a` | +0.1191 (3450, 7.0σ) | +0.0879 (2055, 4.0σ) | +0.0453 (3292, 2.6σ) |
| `zurich_city_02_a` | +0.0002 (600, 0.0σ) | +0.0106 (213, 0.2σ) | +0.0735 (589, 1.8σ) |

Two sequences give the object ordering (BOX > RING by 2× and 2.6×), one gives the ego-motion
ordering, one is null on the object and weakly positive on the background. The three arms do
not use the same boxes — CORE drops boxes too small to erode — so an unpaired comparison mixes
the contrast with a change of population.

## Paired result (`paired.json`) — the one to read

`e26_paired.py` restricts every arm to the boxes where **all three** gradients exist and
differences the same box against itself.

| sequence | n | BOX | RING | BOX − RING | σ | CORE − RING | σ |
|---|---:|---:|---:|---:|---:|---:|---:|
| `zurich_city_00_a` | 1513 | +0.301 | +0.343 | −0.042 | 1.78 | −0.083 | 3.52 |
| `zurich_city_01_a` | 1124 | +0.192 | +0.262 | −0.070 | 2.51 | −0.178 | 6.20 |
| `zurich_city_02_a` | 210 | +0.036 | +0.124 | −0.088 | 1.60 | −0.123 | 2.21 |
| `zurich_city_03_a` | 207 | −0.087 | +0.041 | −0.129 | 2.08 | −0.207 | 3.37 |
| `zurich_city_09_a` | 5189 | +0.174 | +0.100 | **+0.073** | 6.48 | +0.025 | 2.00 |
| `zurich_city_10_a` | 2031 | +0.174 | +0.137 | **+0.037** | 1.75 | −0.046 | 2.13 |

**The control does not come back clean.** In four of six sequences the background ring aligns
*better* than the box, and CORE − RING is negative in five of six, several at 2–6 σ. Only
`zurich_city_09_a` gives the object ordering at any strength.

## What this means for the paper

E26 is a negative result that was kept and acted on. The evidence-time gradient inside a box is
**not** established as a per-object quantity: on the majority of ceiling sequences an
equal-area background annulus carries the alignment at least as well, which is the signature of
ego-motion, exactly as the deflationary reading predicted. The paper therefore does not claim
a per-object gradient; the night-sequence claim it does make rests on the mains signature (E25
instrument A), which replicates in all six sequences at Z = 68–311 against an off-frequency
control of 2.7–25.8 and is immune to this confound because flicker is spatially uniform inside
a box and so contributes nothing to a gradient either way.

## Files

- `e26_egomotion_control.py` → `result.json`, `run.log` — the three-region gradient, unpaired
- `e26_paired.py` → `paired.json`, `paired.log` — the same restricted to boxes present in all
  three arms, differenced within box
