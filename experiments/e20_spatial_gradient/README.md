# E20 — RETRACTED 2026-09-05: the alignment is ego-motion, not per-object evidence time

> **STATUS: this result does not survive its own control. Do not cite it.**
>
> E25 generalized the measurement to all six ceiling sequences and found the alignment
> **stronger where objects move slower** (r = -0.907 against the fraction of objects above
> 20 px/s), which a motion-driven per-object gradient cannot produce. E26 then compared,
> for each box, the gradient inside the box against the gradient in an equal-area annulus
> of surrounding background, aligned with the same label velocity:
>
> | sequence | n | box | ring (background) | paired box - ring |
> |---|---|---|---|---|
> | zurich_city_00_a | 1513 | +0.301 | +0.343 | **-0.042** |
> | zurich_city_01_a | 1124 | +0.192 | +0.262 | **-0.070** (2.5 SE) |
> | zurich_city_02_a | 210 | +0.036 | +0.125 | **-0.088** |
> | zurich_city_03_a | 207 | -0.087 | +0.041 | **-0.129** (2.1 SE) |
> | zurich_city_09_a | 5189 | +0.174 | +0.100 | +0.074 (6.5 SE) |
> | zurich_city_10_a | 2031 | +0.174 | +0.137 | +0.038 |
>
> **In four of six sequences the surrounding background aligns better than the object**, and
> eroding the box to its object-dominated core makes it worse still (negative in five of
> six, -0.178 at 6.2 SE in zurich_city_01_a). Purifying the object region removes the signal.
>
> The explanation is ego-motion. The whole image sweeps coherently, labelled vehicles move
> with traffic, and their label velocities correlate with the background flow, so background
> events inside a box carry the alignment. The paired difference against each box's own
> immediate surroundings removes ego-motion because it is locally common, and what remains
> is not positive.
>
> The flicker-immunity argument for this measurement still holds — flicker is spatially
> uniform and cannot produce a gradient. It was simply not the only confound.
>
> The measurements below are correct; the attribution to per-object evidence time is not.

---

# E20 — Protocol step 10: the spatial gradient of evidence time (2026-09-03)

Three attempts to separate the night evidence-time dispersion from mains flicker had
failed (E11, E12, E18, E19), and the fourth concluded that no flicker-free boxes exist in
this sequence. Stopping there would have been step 6 of the standing protocol. Step 10 is
to change the dimension of the quantity, and there is a quantity flicker cannot reach.

**Flicker modulates the event rate in time and is spatially uniform inside a box, so it
contributes nothing to the spatial gradient of evidence time within that box.** Motion
does: parts of a moving object at different image positions emit their events at
different instants. So instead of the scalar centroid, fit a plane over each box's events,

    t = a + b x + c y ,      grad t = (b, c)   in s/px

and ask whether `grad t` points along the object's own velocity, taken independently from
the labels. 6627 boxes with at least 400 events and a label speed above 5 px/s, median
label speed 58.3 px/s.

## Result — direction

| quantity | mean cos(grad t, v) |
|---|---|
| **measured** | **+0.1518** (median +0.3042) |
| shuffled-velocity null | +0.0284 |
| **time-shuffled null** | **+0.0196** |

With n = 6627 the standard error is 0.0123, so the measured alignment is **12.4 standard
errors from zero** while both nulls sit within about two.

**The time-shuffled null is the control that matters.** Permuting event times within a box
destroys motion while leaving the box's marginal time distribution — and therefore the
whole temporal signature of the flicker — intact. The alignment disappears. Flicker cannot
produce this signal, and neither can the fitting procedure.

## Result — magnitude, and a retracted prediction

    measured |grad t|        11.23 us/px
    time-shuffled floor       5.47 us/px
    1/|v| from labels     17150.20 us/px

**The `1/|v|` prediction is wrong for this geometry and is retracted.** At 58.3 px/s and a
14996 us exposure an object translates 0.87 px, so it does not traverse a 40 px box during
the exposure and the gradient cannot approach `1/|v|`. The measured gradient is 2.05 times
the time-shuffled floor, which is the honest statement: a gradient is present, above the
fitting noise, and its **direction** is the result. No magnitude claim is made.

## What this restores, and what it does not

**Restores:** a component of the night evidence-time structure that mains flicker cannot
explain, by construction rather than by subtraction. This does not depend on estimating a
phase, on a closed form for a periodic contribution, or on finding unmodulated boxes —
the three routes that failed.

**Does not restore:** the scalar dispersion of E09/E11. E19 stands: that quantity rises
monotonically with each box's own flicker modulation, from 93.1 to 208.0 us across
quartiles, and no unmodulated stratum exists in this sequence. The dispersion number
should not be presented as a property of scene evidence.

## Limits

- One sequence, and boxes with a label speed above 5 px/s only.
- The alignment is with the label-derived velocity, which carries the label noise measured
  in E13; that noise attenuates the correlation toward zero, so +0.1518 is a lower bound
  on the true alignment rather than an estimate of it.
- A plane is a first-order model of what is a nonlinear relation between position and
  event time for a rigid moving object; the fit measures the linear component only.
