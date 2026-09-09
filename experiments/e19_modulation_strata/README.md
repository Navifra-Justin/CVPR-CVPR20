# E19 — Stratifying by each box's own flicker modulation (2026-09-03)

The third and last attempt to separate the night evidence-time dispersion from mains
flicker, after E12's integer-period argument was retracted as mathematically wrong and
E18 repeated the same error by applying an integer-period formula to a 1.4996-period
window. This attempt uses no closed form: each box's own modulation depth at 100 Hz is
measured as `m = 2|C|` with `C = (1/N) sum exp(-i w t_k)`, and the within-frame dispersion
is then computed inside modulation strata.

1134 frames, 6841 boxes.

## There is no unmodulated stratum

    modulation m at 100 Hz:  p10 0.355   median 0.467   p90 0.609
    noise floor of m for N = 200 random phases: 0.125

Every labelled box in this sequence is strongly modulated at the mains frequency. The
lowest decile sits at nearly three times the noise floor. **A flicker-free control group
does not exist inside this sequence.**

## Dose-response

| stratum | m range | frames | boxes | sd | null | **excess** |
|---|---|---|---|---|---|---|
| Q1 | 0.122-0.410 | 270 | 1009 | 119.3 us | 74.6 | **93.1 us** |
| Q2 | 0.410-0.467 | 243 | 862 | 149.1 | 76.2 | **128.1** |
| Q3 | 0.467-0.534 | 207 | 774 | 156.6 | 85.1 | **131.5** |
| Q4 | 0.534-1.050 | 265 | 903 | 227.2 | 91.5 | **208.0** |

Off-frequency control at 137 Hz, same procedure:

| stratum | m range | frames | boxes | sd | null | excess |
|---|---|---|---|---|---|---|
| Q1 | 0.002-0.058 | 240 | 879 | 167.3 | 73.3 | 150.3 |
| Q2 | 0.058-0.086 | 221 | 780 | 160.6 | 72.5 | 143.3 |
| Q3 | 0.086-0.117 | 221 | 763 | 179.2 | 75.1 | 162.7 |
| Q4 | 0.117-0.958 | 218 | 797 | 229.1 | 131.5 | 187.6 |

## Reading

The excess rises monotonically with 100 Hz modulation, from 93.1 to 208.0 us, a factor of
2.2. The off-frequency control also rises, from 150.3 to 187.6, a factor of 1.25, so part
of the trend belongs to stratifying on any amplitude statistic: boxes whose events are
temporally clustered have larger `|C|` at every frequency and also more room for centroid
deviation. But the 100 Hz span is much wider, and its lowest stratum (93.1 us) sits far
below the 137 Hz lowest stratum (150.3 us), which the confound alone does not explain.

**Mains flicker contributes substantially to the night dispersion, and this sequence
contains no boxes free enough of it to separate the two.** The night arm of the
evidence-time result cannot be defended as written.

## What this closes and what it leaves

**Closed, against the result:** the night dispersion is not established as a property of
scene evidence. Three controls were attempted and all three failed — pixel exclusion (E11)
left a weakly modulated majority, integer-period cancellation (E12) rested on a false
identity, and phase subtraction (E18) misapplied that identity to a non-integer window.

**Left standing, and unaffected by flicker:**

- The daytime arm has no flicker at all (E10 matches the analytic null at both
  frequencies) — and its excess is zero, so it demonstrates no effect either.
- **E17**, the predictor's measured effective timestamp of -24.94 ms on Gen1, which
  involves no RGB frame, no exposure window and no mains.
- **E10 itself**: a median modulation of 0.467 against a 0.125 noise floor, on essentially
  every labelled object of a widely used benchmark's night sequences, undocumented.
- E00, E06, E08, E13: the exposure distribution, the label clock, the label noise floor
  and its integer lattice.

The route the protocol prescribes from here is step 12 with a different quantity, not a
fourth attempt to rescue this one.
