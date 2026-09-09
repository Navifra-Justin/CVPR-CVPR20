# E41 — the within-frame dispersion against a null that assumes nothing (2026-09-07)

## Why this exists

Sec. 4.4 compares the within-frame dispersion of the per-box mean event time against
`w²/12Nᵢ`, the variance of a mean of `Nᵢ` draws uniform on the exposure. That null assumes
the events of a box arrive independently and uniformly. Sec. 4.3 of the same paper reports
that they arrive in **bursts**, and E38 measured what burstiness does to a different
statistic: it inflates the per-box Rayleigh null 55-fold. A round-3 audit named this as the
claim most likely to fall, and said so in the right terms — the paper asserted at one point
that the subtrahend "contains no assumed quantity", which was false.

## The null that assumes nothing

For each frame, pool the events of all qualifying boxes and reassign them at random to
boxes, preserving each box's count. Everything about the frame survives untouched — the
exposure, the mains flicker, the scene's burstiness, the counts. Only **which box an event
belongs to** is destroyed. If the observed dispersion is a property of objects it exceeds
this null; if it is the frame's own arrival statistics it does not. 200 draws per frame,
1134 qualifying frames of `zurich_city_09_a`, median 6 boxes each.

## Result

| null | value | excess over it |
|---|---|---|
| observed within-frame sd of `t̄ᵢ` | **206.6 µs** | — |
| analytic, `w²/12Nᵢ` | 93.0 µs | 184.5 µs |
| **permutation, box identity destroyed** | **78.6 µs** | **191.1 µs** |

**The predicted failure did not happen.** The permutation null is *smaller* than the
analytic one, by a factor of 0.85, so the excess is slightly larger under the better null,
not smaller. 94.1 % of frames exceed their own permutation null.

The reason is structural and it is worth stating: burstiness common to the frame — which is
what the flicker is — displaces every box's `t̄ᵢ` in the same direction and **cancels in
their dispersion**. The statistic was already differential. What burstiness inflates is a
per-box statistic compared against an absolute reference, which is exactly the Rayleigh
test E38 had to withdraw, and not this one.

Random-position boxes of the same shapes: observed 339.4 µs against a permutation null of
113.3 µs, an excess of 320.0 µs — larger than the annotated boxes', which is the same
conclusion Sec. 4.4 already draws from the analytic null. The dispersion is a property of
where evidence falls in the image during the exposure and is not specific to objecthood.

## What this does NOT establish

That the dispersion is a per-object temporal signal. It is not: the random-box arm exceeds
the annotated arm under both nulls. What it establishes is that the *excess* is not an
artifact of assuming independent uniform arrivals, so the bound Sec. 4.4 places on any
per-object temporal statistic stands on a null that assumes nothing about arrival
statistics. One sequence, the one Sec. 4.4 reports.
