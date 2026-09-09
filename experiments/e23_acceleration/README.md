# E23 — The cost of extrapolating, tested on object acceleration (2026-09-04)

> **Read the cross-track row before quoting the along-track one.** The acceleration term
> is significant on the along-track error at 10.0 SE **and on the cross-track error at
> 13.4 SE**, where no extrapolation can put it. This experiment does not confirm the
> extrapolation account.

E17 places the network's evidence 24.94 ms before the label time. E21, with box size in
the regression, places its output at the label time. The difference is an extrapolation
of about 25 ms, which is exact under constant velocity and costs `a tau^2 / 2` under
acceleration. Nothing in the training objective fixes that cost, so it is testable.

Same matching procedure as E21 (released `rvt-t` over Gen1 val, recurrent state carried,
detections matched to ground truth at IoU >= 0.5), with each object's acceleration taken
as the change in its label-derived velocity over the next label interval.

    MATCHES 4332   median speed 19.0 px/s   median IoU 0.892
    acceleration px/s^2:  p25 10.0   med 16.5   p75 29.7   p95 77.3
    corr(acc, |v|) = +0.360     corr(acc, size) = +0.327

## Result

    |along-track error| = b + b1|v| + b2 size + b3 acc

    | term          | coefficient | SE       | SE from zero |
    |---------------|-------------|----------|--------------|
    | intercept     | -3.4266 px  | 0.1476   | 23.2         |
    | speed         | -0.0146 s   | 0.0046   |  3.2         |
    | size          | +0.1215     | 0.0026   | 46.0         |
    | acceleration  | +0.0198 s^2 | 0.0020   | **10.0**     |

    cross-track error, same regressors, acceleration term:
                      +0.0117 s^2   SE 0.0009   -> **13.4 SE**

    by acceleration quartile, median |along| and |cross| error in px:
    Q1 [  0.0,  10.0)  n=1196   0.7159   0.5036   ratio 1.422
    Q2 [ 10.0,  16.5)  n=1090   0.7861   0.5525   ratio 1.423
    Q3 [ 16.5,  29.7)  n=1113   1.1073   0.6669   ratio 1.660
    Q4 [ 29.7, 346.2)  n=1099   2.7635   1.0674   ratio 2.589

## Reading

Two facts close this as written.

1. **The cross-track control does not vanish.** Extrapolating a position forward
   displaces it along the direction of travel and nowhere else, so a term of the same
   order across the track is not the predicted effect.
2. **The magnitude is wrong by two orders.** The predicted coefficient is
   `tau^2 / 2 = 3.11e-4 s^2` at `tau = 24.94 ms`. The measured along-track coefficient
   is 0.0198 s^2, about 64 times larger.

The simplest reading is that acceleration indexes hard objects rather than timing:
acceleration correlates with speed at +0.360 and with box side at +0.327, both of which
are in the regression, and objects that turn or change speed are also the objects whose
boxes the detector localizes worst in every direction.

What survives is the ratio: the along-track coefficient is larger than the cross-track
one, and the median error ratio rises from 1.42 to 2.59 across acceleration quartiles.
That is a directional excess, but the two coefficients come from the same objects and
their difference has no honest error bar here, so nothing is claimed from it.

**No pass of the 12-step protocol has been run against this result.** The paper reports
both coefficients and states that no extrapolation cost is established; it does not
report a refutation. `docs/PROTOCOL_LEDGER.md` entry 5 names the first pass to run: the
acceleration is a difference of differences of label centres over a 50 ms base, so it
carries the label centre noise of E13 amplified, and the term should be re-measured with
the acceleration estimated over a wider base before anything is concluded.

## In the paper

Sec. 8.4 of `paper/main.tex`, macros `\accCoef`, `\accSigmas`, `\accCross`,
`\accCrossSigmas`, `\accPredCoef`, `\accRatio`, `\accSpeedCorr`, `\accSizeCorr`,
`\accMatches` in `paper/numbers.tex`.
