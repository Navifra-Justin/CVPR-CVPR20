# E10 — Are the night events mains flicker? (measured 2026-09-02, main session)

DSEC's own paper attributes the high night event rate to streetlight flicker. A new
result had just been built on per-object event-time centroids inside night exposure
windows, so this had to be settled before that result could be used.

## Global spectrum

Power spectrum of the global event rate, Hann window, on the same code for both sequences.

| sequence | exposure | strongest line in 90-110 Hz | peak over continuum (60-160 Hz) |
|---|---|---|---|
| zurich_city_09_a (night) | 14996 us | **100.00 Hz** | **10 841** |
| interlaken_00_c (day) | 1478 us | — | 6.4 |

A 20 s window at 500 us bins gave a 100 Hz line ratio of 48 694 and a strongest peak at
200 Hz, the second harmonic. A 3 s window at 500 us bins put the top line at exactly
100.00 Hz with the two adjacent FFT bins beside it. Swiss mains is 50 Hz, so lamp
intensity flickers at 100 Hz. **The night stream is flicker-dominated.**

## Per-pixel test, with the correct null

Raw modulation depth is useless here: for N events at random phase the resultant length
divides to about `sqrt(pi/4)/sqrt(N)`, which at the counts involved is the same size as
the effect. The Rayleigh statistic `Z = R^2/N` is `Exp(1)` under the null, so the null has
median `ln 2 = 0.693`, p95 `3.00`, and a `p < 1e-3` rate of `0.001`. Pixels with at least
100 events, 2 s of data, every 4th event.

| sequence / frequency | live pixels | median Z | p95 Z | fraction p < 1e-3 | fraction p < 1e-6 |
|---|---|---|---|---|---|
| **night @ 100 Hz** | 35 990 | **2.935** | **16.52** | **0.2407** | 0.0750 |
| night @ 137 Hz (off-frequency control) | 35 990 | 0.581 | 2.52 | 0.0004 | 0.0000 |
| day @ 100 Hz | 17 800 | 0.719 | 3.10 | 0.0008 | 0.0000 |
| day @ 137 Hz (off-frequency control) | 17 800 | 0.697 | 3.04 | 0.0011 | 0.0000 |

Two independent nulls land on the analytic values, so the estimator is not producing the
effect: the same code at 137 Hz on the same night events returns the null, and at 100 Hz on
daytime events returns the null.

## What this settles

**Against the night result.** In the night sequence **24.1 % of active pixels are
significantly phase-locked to the mains at 100 Hz**, 240 times the null rate, and 7.5 %
reach `p < 1e-6`. This is not a handful of lamp pixels that a small spatial mask would
remove — it is a quarter of the active sensor. A 100 Hz period is 10 ms and the night
exposure window is 14996 us, so flicker completes one and a half cycles inside a single
exposure. Objects at different image positions see different lamps at different phases,
which displaces their event-time centroids **without any motion**. That is the same
signature as the per-object dispersion recently measured, so **the night dispersion result
cannot be claimed as written.**

The correlation is worse than it first appears: the excess dispersion was found at night
and was zero in daylight, and flicker is present at night and absent in daylight. A
reviewer would reach for that immediately.

**In favour of the daytime data.** The daytime sequence matches the null at both
frequencies, so daytime measurements carry no flicker confound at all.

## The route the protocol prescribes

The failure is at step 6 of the standing protocol: the data does not suit the technique in
the regime where the technique was applied. Step 9 is to change the evaluation method
rather than the claim. The Rayleigh test above supplies a principled per-pixel filter, and
**76 % of active night pixels are not significantly modulated**, so dispersion can be
re-measured on the flicker-free majority with the locked pixels excluded. Until that is
run, the night number stands as unusable.

Two things are worth keeping regardless of how that turns out. The estimator now has two
validated nulls. And "a quarter of the active pixels of DSEC's night sequences are phase-
locked to the mains" is a fact about a widely used benchmark that its users are not told.

## Limits

- Two sequences, one night and one day. Whether the other four ceiling sequences behave the
  same is unmeasured.
- The 137 Hz control was chosen as an arbitrary non-harmonic; it is not a proof that no
  other periodicity exists, only that the estimator does not manufacture one.
- Events were subsampled every 4th for the per-pixel test. Uniform subsampling preserves
  phase statistics but reduces power; the reported fractions are conservative.
