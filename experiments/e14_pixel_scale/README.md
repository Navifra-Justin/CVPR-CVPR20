# E14 — What the measured dispersion is worth in pixels (2026-09-02)

The paper reports a within-frame dispersion of evidence times of 183.6 us. A benchmark
scores in pixels. The conversion is one multiplication and a reviewer will do it, so it
belongs in the paper rather than in a reviewer's margin.

Inputs, all measured in this repository: dispersion 183.6 us (E11 exact / E12), object speeds
from DSEC-Det tracks (E08), label noise floor 0.4974 px with a 0.1443 px integer-lattice
component (E13).

| object speed | displacement from 183.6 us | as a fraction of `sigma_c` | as a fraction of the 0.5 px lattice step |
|---|---|---|---|
| 40 px/s (median) | 0.0073 px | 1.5 % | 0.015 |
| 150 px/s (p90) | 0.0275 px | 5.5 % | 0.055 |
| 360 px/s (p99) | 0.0661 px | 13.3 % | 0.132 |

Inverting the relation:

| to reach | requires |
|---|---|
| the 0.1443 px quantization floor | 786 px/s |
| the 0.4974 px label noise floor | 2709 px/s |
| one 0.5 px lattice step | 2723 px/s |

**DSEC does not contain those speeds.** Its 99th percentile object speed is 360 px/s, so on
this dataset the temporal dispersion is between one and fifteen percent of the noise a
single box already carries.

## Consequence for the paper's claims

The measurement is not weakened; its **spatial consequence on this dataset** is small, and
the paper must say so in the same breath as the measurement. Three statements survive and
should replace any implication that the effect is large:

1. **Per box, at DSEC speeds, the effect is below the annotation noise.** It is not
   something a practitioner would notice on one detection.
2. **Pooled, it is not.** Per-box annotation noise averages down as `sigma_c/sqrt(N)` while a
   systematic temporal term does not. Across the 6693 DSEC-Det tracks the pooled noise is
   0.0061 px against 0.0073 px of displacement, a ratio of 1.21; across all 390 118 boxes it
   is 0.0008 px against 0.0073 px, a ratio of 9.2. An effect invisible on one box is the
   larger term once a benchmark aggregates, which is what a benchmark does.
3. **The regime where it is not small is the regime event cameras are sold for.** The effect
   reaches the annotation floor above roughly 800 to 2700 px/s. DSEC's driving sequences do
   not reach that; the fast-motion settings event sensors are deployed in do.

## What this rules out

Any sentence implying that correcting the effect would visibly improve a detector on DSEC.
It would not, and the paper already declines to claim a downstream gain. The claim that
survives is about what the benchmark's format can express and what its aggregate score
contains, not about a per-image improvement.

## Limits

- Speeds are box-centre image speeds derived from the labels, so they carry the same noise;
  at the low end they are not distinguishable from zero (E08).
- The pooled argument assumes the per-object temporal terms do not themselves average to
  zero across the dataset. Whether they do is **not measured here** and is the obvious next
  check: if the per-object offsets are symmetric about zero, the pooled ratio above
  overstates the aggregate effect.


## Note on inputs
Recomputed 2026-09-02 after E11's exposure-window defect was fixed; the dispersion input
fell from 208.8 to 183.6 us and every figure in this file moved with it.
