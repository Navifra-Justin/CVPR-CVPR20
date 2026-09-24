# E39 — is the line at 100 Hz or at 200 Hz? Measured, not eyeballed

## Why this exists

Rendering one exposure window as a video made the event rate visible, and its humps looked
about 5 ms apart — 200 Hz, not the 100 Hz the paper names. That is not a contradiction on its
face: an event camera responds to log-intensity *change*, so a lamp oscillating at 100 Hz
drives events on both the rising and the falling edge and can produce a rate at 200 Hz. It
matters anyway, because the paper names the frequency and the per-box Rayleigh statistic is
evaluated **at** it.

## Method

`N·|C(f)|²` over the event times, 20–400 Hz, in three measurements that together settle it:

1. the rate spectrum of the single frame the video shows;
2. the same over the whole ceiling sequence, which resolves finely;
3. the same split by polarity — a rectified drive puts ON events on one edge and OFF events on
   the other, which is exactly what moves power between 100 and 200 Hz.

## Result

**1) the one frame the clip shows** — 407 942 events over 14 996 µs:

| | peak | Z(100) | Z(200) | ratio 200/100 |
|---|---:|---:|---:|---:|
| all | 20.0 Hz | 31573.7 | 11757.4 | 0.37 |
| ON | 20.0 Hz | 25253.0 | 355.0 | 0.01 |
| OFF | 20.0 Hz | 111396.0 | 23394.6 | 0.21 |

A 15 ms record cannot resolve 100 from 200 Hz — its Rayleigh resolution is ~67 Hz — so the peak
lands on the record-length harmonic at 20 Hz and the two candidate bins leak into each other.
**The video could not have settled this, and the eyeball reading of "humps 5 ms apart" is a
windowing artefact.** That is the first finding.

**2) the whole sequence**, 400 000 events subsampled from 1.79 × 10⁹:

| | peak | Z(100) | Z(200) | ratio 200/100 |
|---|---:|---:|---:|---:|
| all | 200.00 Hz | 65.1 | 1664.3 | **25.58** |
| ON | 200.00 Hz | 221.9 | 239.7 | 1.08 |
| OFF | 200.00 Hz | 634.7 | 1754.6 | 2.76 |

With the full record the peak is unambiguous and it is at **200 Hz**. Pooled over polarity the
200 Hz line is 25× the 100 Hz one.

**3) the polarity split is the mechanism.** Separating ON from OFF collapses the ratio from
25.6 to 1.08 (ON) and 2.76 (OFF): each polarity carries comparable power at both lines, and it
is their *sum* that concentrates at 200 Hz. That is the rectification signature — one edge per
half-cycle of a 100 Hz drive, alternating in polarity, doubling the rate line.

## What the paper does with it

The physical drive is 100 Hz mains; the **event-rate** line is at 200 Hz, and the per-box
statistic is computed on the event rate. The paper says 100 Hz mains and evaluates the box
statistic at the frequency the rate actually carries, with the off-frequency control at 137 Hz
(prime to both, and to the strongest sequence-level harmonics listed in `run.log`: 20, 22, 24,
25, 26, 28–32, 34, 35 Hz).

## Files

- `e39_which_frequency.py` → `sequence_spectrum.json`, `run.log`
