# E16 — The common offset, which every earlier experiment removed (2026-09-02)

E09, E11 and E12 all measured the **dispersion** of evidence times across the objects of one
frame after subtracting that frame's mean. The mean itself had never been reported. It
matters for a different reason than the dispersion: it is common to every object, so it
survives aggregation and does not have to be compared against a per-object noise floor.

| sequence | exposure | frames | all events, median offset from mid-exposure | as a fraction of the half-width | labelled objects, median frame-mean offset |
|---|---|---|---|---|---|
| zurich_city_09_a | 14996 us | 1811 | **-16.8 us** (mean -8.7, sd 170.3) | -0.22 % | **-102.3 us** (sd across frames 151.9, n=1134) |
| interlaken_00_c | 1481 us | 535 | -0.6 us (mean -0.5, sd 6.0) | -0.08 % | -1.1 us (sd 19.1, n=20) |

## Reading

**The common offset is small, and it is not the large term hoped for.** At night it is
-16.8 us over all events and -102.3 us inside labelled boxes, against a dispersion of
183.6 us. In daylight both are under 2 us. Whatever else is true, the evidence inside a
DSEC exposure is centred very close to the middle of that exposure, and the mid-exposure
convention DSEC uses is, to this precision, the right one.

One difference is worth keeping. **Events inside labelled boxes are about 85 us earlier
than the frame's evidence as a whole** (-102.3 against -16.8). Objects and background are
not centred at the same time. That is a small number, and it is the same kind of quantity
as the dispersion rather than a larger one.

## Consequence

This closes the hypothesis that a large systematic clock offset is hiding inside the
exposure window. It is not. The large term in this paper is elsewhere: the **predictor's**
window, which for the released RVT configuration ends at the label time and so has a
uniform-weight centroid 25 ms earlier (E02) — 136 times the dispersion measured here.

The two terms play different roles and the paper should say so plainly:

- the predictor window offset is **large and removable** by declaring one number, and no
  released detector declares it;
- the intra-exposure dispersion is **small and not removable** by any single declared
  number, because it differs between objects of the same frame.

## Limits

- Two sequences. The daytime arm has only 20 frames with three or more qualifying objects,
  so its object-level figure is indicative and no more.
- The offset is measured against DSEC's own mid-exposure convention. It says the convention
  is accurate; it says nothing about whether that convention is the right target.
