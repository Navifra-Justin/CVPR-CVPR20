# E38 — the per-box Rayleigh null, measured instead of assumed (2026-09-07)

## Why this exists

E10 and E25 test each labelled box for phase locking with `Z = N|C|^2` and read a p-value
from the `Exp(1)` distribution `Z` follows when the phases are independent and uniform. A
checklist audit pointed at the paper's own table: the 137 Hz off-frequency arm has a
per-box median of 4.01, not 0.693, so the text's claim that the control "returns its null"
is contradicted by the paper's own numbers, and any statement of the form "99 % of boxes
reach p < 1e-3" is then computed against a null the data rejects.

## Arm 1 — how wrong is the analytic null? (`run.log`)

Sweeping 16 off-frequencies away from mains and label-rate harmonics, pooled over all six
ceiling sequences:

| quantity | analytic `Exp(1)` | measured |
|---|---|---|
| median off-frequency `Z` | 0.693 | **38.39** |
| 99th percentile | 4.61 | 2634 |
| 99.9th percentile | 6.91 | 7181 |
| boxes above the `p<1e-3` cut at 100 Hz | — | 99.65 % analytic, **0.20 %** empirical |

The inflation is a factor of 55 at the median. Event times inside one box during a 15 ms
exposure arrive in bursts, so the effective sample size is far below the raw count. **The
per-box p-values and the "99.0 to 100.0 % locked" figure are withdrawn.**

Two things this does *not* touch. The per-**pixel** arm of E10 is unaffected: there the
137 Hz control returns 0.581 against the analytic 0.693, so the null holds where it was
verified. And the 100 Hz to 137 Hz *contrast* is a comparison of two statistics on the
same events and never needed a null.

Arm 1 has a defect of its own: its sweep reached down to 63 Hz, where a 15 ms window holds
less than one cycle and the statistic measures the burst envelope rather than an
oscillation. Arm 2 removes both problems.

## Arm 2 — the line against its own local background (`local_excess.log`)

For each box, `Z(f)` is computed on a 1 Hz grid from 60 to 300 Hz and reported as

    R = Z(100 Hz) / median{ Z(f) : |f-100| in [6,30], f away from 20 Hz and 100 Hz harmonics }

`R` compares the line with the background the *same box* produces at neighbouring
frequencies, so the burst inflation divides out whatever its size. No null is used.

| sequence | boxes | R at 100 Hz | R at 137 Hz | above the sham's 99th pct |
|---|---|---|---|---|
| zurich_city_00_a | 2914 | 1.94 | 0.09 | 100.00 % |
| zurich_city_01_a | 2134 | 1.89 | 0.15 | 99.63 % |
| zurich_city_02_a | 619 | 1.89 | 0.12 | 99.68 % |
| zurich_city_03_a | 241 | 1.79 | 0.18 | 95.44 % |
| zurich_city_09_a | 6997 | 1.81 | 0.11 | 99.23 % |
| zurich_city_10_a | 3611 | 1.91 | 0.10 | 100.00 % |
| **pooled** | **16 516** | **1.87** (p10 1.62, p90 2.18) | **0.11** (p99 1.00) | **99.63 %** |

The medians differ by a factor of 17.5, and the spread of `R` at the line is narrow: the
tenth percentile over 16 516 boxes is 1.62.

## Arm 3 — the same statistic at the second harmonic (`local_excess_200.log`)

E40 later showed the dominant whole-recording line is at 200 Hz, not 100. Running the
identical local-excess construction there gives a **weaker** per-box result:

| | 100 Hz | 200 Hz |
|---|---|---|
| median R over 16 516 boxes | **1.87** | 0.76 |
| boxes above the 137 Hz arm's 99th percentile | 99.63 % | 28.43 % |

That is the transform limit, not a contradiction. One 14996 µs window resolves 67 Hz, so a
single box cannot separate harmonics at all; what it can show is that the modulation reaches
it. The harmonic identification belongs to the whole-recording sweep (E40), and the paper
now says so.

## The pooled spectrum, and what one box can resolve

The median normalised spectrum over all boxes has **one** feature between 60 and 300 Hz:

| f (Hz) | 60 | 80 | 90 | **96** | 100 | 110 | 120 | 137 | 200 | 300 |
|---|---|---|---|---|---|---|---|---|---|---|
| median R(f) | 0.46 | 1.02 | 1.85 | **1.98** | 1.89 | 1.27 | 0.51 | 0.07 | 0.16 | 0.28 |

Peak at 96 Hz, 8.5x the median over 200–300 Hz, half-maximum width 35 Hz. **A 14996 µs
window is transform-limited to 67 Hz**, so a single box cannot separate 96 Hz from 100 Hz,
and the per-box arm establishes a line *near* 100 Hz, not *at* it. The position is fixed
by the per-pixel arm of E10, which pools the whole sequence, resolves the spectrum finely
and puts the line at 100.00 Hz with a ratio of 10841 over the 60–160 Hz continuum.

## What this changes in the manuscript

- withdrawn: the per-box p-values, the `p<1e-3` locked fractions, and the claim that the
  137 Hz arm returns the analytic null per box.
- kept, on the per-pixel arm where the null was verified: the analytic `Exp(1)` reference,
  the 24.07 % locked-pixel fraction, and the 100.00 Hz line position.
- replaced: "essentially every labelled box is locked at `p<1e-3`" becomes "99.63 % of
  boxes carry more power at the line than the off-frequency arm's 99th percentile", a rank
  statement over the same events that assumes no distribution. The number barely moves;
  what changes is what it rests on.
