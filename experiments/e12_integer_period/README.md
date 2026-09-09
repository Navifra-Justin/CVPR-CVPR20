# E12 — RETRACTED 2026-09-03: the integer-period argument is mathematically wrong

> **STATUS: the central claim of this experiment does not hold. Do not cite it.**
>
> The argument was that a source periodic at exactly 10 000 us contributes nothing to a
> time centroid when integrated over an integer number of periods. That is true of the
> **zeroth** moment (the event count) and false of the **first** moment (the centroid).
> For `lambda(t) = lambda_0 + A cos(w t + phi)` on a symmetric one-period window,
>
>     integral of  A cos(w t + phi)      dt  =  0            (count cancels)
>     integral of  t A cos(w t + phi)    dt  =  -(A T / w) sin(phi)   (centroid does not)
>
> so the centroid contribution is `-(A/lambda_0) sin(phi) / w`, which vanishes only when
> `sin(phi) = 0`. Verified numerically to machine precision at seven phases.
>
> **The magnitude matters.** At 100 Hz one unit of modulation depth is 1592 us of centroid
> shift, so a modulation depth of 0.10 gives 159 us — the same order as the 183.6 us
> dispersion this repository measures. Objects at different image positions see different
> lamps at different phases, which produces dispersion of exactly the observed size.
>
> **Consequence: mains flicker is not excluded by this experiment, and the night result is
> once again unprotected on that axis.** E11's pixel exclusion remains, but E10 measured a
> median Rayleigh statistic of 2.935 against a null of 0.693 across all live night pixels,
> so a weakly modulated population survives that exclusion. E18 replaces this control with
> one that estimates each box's own flicker phase and subtracts its predicted contribution.
>
> The numbers below were measured correctly; only the inference drawn from them was wrong.

---

# E12 — Integer-period windows: flicker cannot explain the dispersion (2026-09-02)

The decisive control on E09's night result, and stronger than E11 because it does not
require identifying which pixels are affected.

Mains flicker is periodic at exactly 10 000 us. Integrated over an **integer** number of
flicker periods, its net contribution to a time centroid is zero regardless of its
amplitude, its phase, or how many pixels carry it. So the same measurement is repeated with
the analysis window centred on the same mid-exposure instant and only its width changed.
Scene content is held fixed; only flicker cancellation varies.

| window | flicker periods | flicker | frames | sd | null | **excess** | excess / null |
|---|---|---|---|---|---|---|---|
| 5 000 us | 0.5 | uncancelled | 1085 | 218.1 us | 46.5 us | **212.6 us** | 4.572 |
| **10 000 us** | **1.0** | **cancels exactly** | 1118 | 211.5 us | 74.4 us | **195.2 us** | 2.624 |
| 14 996 us | 1.4996 | uncancelled | 1134 | 206.6 us | 93.0 us | **183.6 us** | 1.975 |
| **20 000 us** | **2.0** | **cancels exactly** | 1137 | 271.2 us | 108.0 us | **246.8 us** | 2.284 |

## Reading

If flicker produced the dispersion, the two integer-period windows would show an excess of
approximately zero. They do not: the excess is 195.2 us at one full period and 246.8 us at
two. It is present at every width tested, and more than 90 % of frames exceed the analytic
null in every arm.

The ordering carries no trace of flicker cancellation either. Ranked by flicker
cancellation the widths pair as (1.0, 2.0) cancelling and (0.5, 1.4996) not, but the
excesses are 195.2, 246.8, 212.6 and 183.6 us respectively — interleaved, with no
separation between the cancelling and non-cancelling pairs.

**Mains flicker is not the source of the per-object dispersion.** Together with E11, the
night result now survives three independent controls: exclusion of phase-locked pixels, a
matched random exclusion, and integer-period cancellation.

## Limits

- One sequence. The other five ceiling sequences are unmeasured.
- **Retracted 2026-09-02:** an earlier version of this list said the excess grows with
  window width. The measured values are 212.6, 195.2, 183.6 and 246.8 us at 0.5, 1.0,
  1.4996 and 2.0 periods, so three of the four widths run downward and the claim is false.
  It reached the paper in two places before the audits caught it. What the numbers support
  is that the excess is present at every width tested, not that it varies monotonically
  with width; how it varies is not established here.
- Boxes carrying fewer than 200 events in a window are dropped, so the narrow-window arms
  keep slightly fewer frames and a mildly different object population.
