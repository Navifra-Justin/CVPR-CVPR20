# Restructure of 2026-09-04

The draft of 2026-09-03 was written before E19, E20 and E21 returned. Two of its
claims are retracted, one new result replaces them, and the predictor side is closed
with a negative control. This file records what left the paper, what took its place,
and what was judged too weak to keep. Files touched: `paper/main.tex`,
`paper/supplement.tex`, `paper/numbers.tex`.

## 1. Removed: the integer-period flicker argument (E12)

The argument was that a source periodic at exactly 10 000 us contributes nothing to a
time centroid when the analysis window spans an integer number of periods. That holds
for the **zeroth** moment and not for the **first**: the centroid contribution is
`-(A/lambda_0) sin(phi) / omega`, which vanishes only at `sin(phi) = 0`, verified
numerically at seven phases (`experiments/e12_integer_period/README.md`).

Removed from the paper:

- the paragraph *Integer-period windows* of the old Sec. 6 and its concluding
  paragraph ("present at both integer-period widths / mains flicker does not account
  for the dispersion");
- **Figure 4** (`figs/fig4_integer_period.pdf`), which plotted the four window widths;
- the bottom block of the controls table (`tab:controls`), the four analysis-window
  rows and their caption text;
- the abstract sentence "integration over one and two full mains periods, where a
  periodic source cancels whatever its amplitude, phase or spatial extent";
- the introduction sentence announcing four window widths as a control;
- the conclusion sentence repeating the same;
- the supplement paragraph *Pixel exclusion and window widths*, whose window-width
  half is replaced by the modulation-stratum data path.

In `numbers.tex` the E12 macros (`\excessHalfPeriod`, `\excessOnePeriod`,
`\excessFullExp`, `\excessTwoPeriod`, the `\w*`, `\sd*`, `\null*`, `\frames*`,
`\frac*Period*` families, `\periodsHalf`, `\periodsOne`, `\periodsTwo`) are commented
out under a retraction note rather than deleted, so the measured values stay on the
record and no surviving text can use them. `\periodsFullExp` is kept, as an E10 fact
about the ceiling exposure rather than as a cancellation claim. `\flickerPeriodUs` is
kept for the same reason.

Verified: no reference to integer periods, period counting or cancellation survives in
`main.tex` or `supplement.tex`.

## 2. Demoted: the night scalar dispersion as a property of scene evidence (E19)

E19 measured, per box, the modulation depth `m = 2|C|` at 100 Hz on that box's own
events and recomputed the within-frame dispersion inside quartiles of `m`:

- the excess rises monotonically, 93.1 -> 128.1 -> 131.5 -> 208.0 us;
- the 137 Hz off-frequency control also rises, 150.3 -> 187.6 us, so part of the trend
  belongs to stratifying on any amplitude statistic, but the 100 Hz span is wider and
  its lowest stratum sits below the control's lowest stratum;
- `m` has p10 0.355, median 0.467, p90 0.609 against a floor of 0.125 for the 200
  events a box enters with at random phase, so **no unmodulated stratum exists**.

The scalar is now reported as a bounded statement everywhere it appears. It is a
property of the event stream inside the published window that this sequence does not
resolve into a scene component and an illumination component; what its magnitude
bounds is the precision to which one scalar timestamp denotes an instant. The paper
states in Sec. 6, in the limitations and in the conclusion that it is not evidence
that the objects of one frame are captured at different times.

Old Sec. 6 *Controls against mains flicker* is now **Sec. 6, Separability of the
dispersion from flicker**: the pixel-exclusion control (E11) with its own bound, the
modulation strata (E19), and the absent stratum. The third block of the controls table
(`tab:controls`, Table 1 in the new numbering) is now the four modulation quartiles; the caption states that its excess is
`(sd^2 - null^2)^{1/2}` of the two medians beside it, unlike the other blocks, and
that a frame enters a stratum when at least three of its boxes fall in it.

## 3. Added: the spatial gradient of evidence time (E20), the new Sec. 7

Flicker is periodic in time and uniform across the pixels of one box, so it
contributes nothing to how evidence time varies with position inside the box; a moving
object does. Fitting `t = a + b x + c y` over each box's events and comparing
`grad t` with the label-derived velocity direction, over 6627 boxes with at least 400
events and a label speed above 5 px/s:

| quantity | value |
|---|---|
| mean cos(grad t, v) | +0.152 (median +0.304) |
| shuffled-velocity null | +0.028 |
| time-shuffled null | +0.020 |
| SE (1/sqrt n, a bound) | 0.012 -> **12.4 SE** |

The time-shuffled null is stated in the paper as the control that matters: permuting
event times inside a box destroys the motion structure and leaves that box's marginal
time distribution, and with it the whole temporal signature of the flicker, unchanged.

The `1/|v|` magnitude prediction is **retracted in the paper as well as in the E20
README**. The paper reports the measured median `|grad t|` of 11.23 us/px against the
time-shuffled floor of 5.47 us/px, then states why the velocity scale does not apply:
at the median label speed of 58.3 px/s an object translates 0.87 px over the 14 996 us
exposure while the median box side in this sequence is 42 px, so no part of the object
crosses its own box during the exposure. Only the direction is claimed.

`\gradBoxSide` (42 px) was measured for this restructure as the median `sqrt(wh)` over
the released boxes of `zurich_city_09_a`; the macro comment names that source.

## 4. Added: Figure 5 (`figs/fig5_qualitative.pdf`), which prints as Figure 2

Three panels on real data: (a) every event inside one published 14 996 us exposure
window colored by its position in the window with the released boxes and their
evidence times, (b) that frame's per-box evidence times with their analytic nulls,
(c) the population gradient alignment with its two nulls. The caption states that the
frame is the **median-dispersion frame of the 602 candidates and not the largest**.
This is the paper's first figure of real data and closes checklist items 109, 110
and 128.

The candidate count was cross-checked here rather than taken on trust: 1557 of the
sequence's 1813 exposures match a label time, and 631 of those carry at least six
released boxes, which bounds the 602 that also clear the per-box event floor.

## 5. Rewritten: the predictor side (E17, E21, E23)

- **Sec. 8.2** keeps E17 unchanged: influence-weighted centroid -24.94 ms against a
  uniform-weight reference of -25.00, coefficient of variation 0.034 across the ten
  bins, 480 real Gen1 val samples with the recurrent state warmed.
- **Sec. 8.3 is new.** E21 measures the effective *output* time by matching the
  released checkpoint's detections to ground truth and regressing the along-track
  residual on label speed **with box size as a third regressor**, because
  `corr(speed, size) = +0.349`. The temporal term falls to +11.9 ms at 1.3 SE, the
  size term is +0.0162 px per px of box side at 3.0 SE, and the cross-track slope is
  -0.19 ms at 0.1 SE over 2235 matches. The section states that no output-time offset
  is established **and that this is what the training objective enforces**: RVT is
  trained with the ground truth at the label time on a window ending there. It is
  reported as the negative control it is, including the confound and the clean
  cross-track null.
- **Sec. 8.4 is new.** Evidence centered 24.94 ms before the label with the output at
  the label is an extrapolation over that interval, exact under constant velocity and
  costing `a tau^2 / 2` under acceleration: 0.31 px at 1000 px/s^2, between the
  0.1443 px lattice component of the label center noise and its 0.4974 px total. E23
  tests the consequence.

**E23 returned while this pass was being written and is wired in.** Over 4332
matches, the acceleration term on the along-track error is +0.0198 s^2 at 10.0 SE.
The cross-track control **does not vanish**: the same term on the cross-track error is
+0.0117 s^2 at 13.4 SE. The along-track coefficient is about 64 times the
3.11e-4 s^2 that `tau^2/2` implies at tau = 24.94 ms, and acceleration correlates with
label speed at +0.360 and with box side at +0.327. Sec. 8.4 reports the prediction,
then all of these numbers, then the conclusion the data supports: acceleration predicts
localization error in both directions, the measured term is not the extrapolation
cost, and no extrapolation cost is established. The limitations say the same in one
sentence. No `\TODOnum` cell remains in the body.

## 6. Claims judged too weak to keep

- **The `1/|v|` gradient magnitude.** Retracted with its geometry stated (item 3).
- **The per-track structure of the scalar residual** (E09 `per_track.py`: between-track
  sd 149.2 us against 39.3, variance ratio 14.4, lag-one autocorrelation 0.721, higher
  for tracks that move more). It is a claim about the internal structure of the
  quantity E19 demotes, and it carries the same confound, since a track occupies image
  positions that see the same lamps. Its counter-argument, that a periodic image-plane
  effect inherited by a stationary track would run the other way, is not strong enough
  to carry a paragraph on its own. Removed from the body and from the supplement's
  data-path section.
- **The two-branch effective-timestamp spread** (`\rvtTwoBranchScale`, 7.2 ms). The old
  Sec. 7.2 closed by deriving a spread for a fused event--RGB predictor and then
  saying it is not measured here. Unmeasured speculation, removed.
- **"Annotated vehicles are somewhat more temporally coherent than arbitrary regions
  of the same shape."** The random-box arm's excess is larger than the labelled boxes'
  and the difference was never given an error bar. The paper now states only that the
  dispersion is a property of where evidence falls in the image and is not specific to
  objecthood.
- **The day--night contrast as a support contrast.** Kept as a reported measurement
  (Table 2, Fig. 3 left) and stated in the limitations as a two-point comparison in
  which exposure width and illumination move together.

## 7. Removed for the page budget, with the evidence kept

The body is capped at eight pages and Figure 5 spans both columns. Removed:

- **Figure 2** (`fig2_evidence_time.pdf`), whose middle panel is superseded by
  Fig. 5(a,b) and whose bottom panel is the left panel of Fig. 3.
- **Figure 1** (`fig1_dsec_exposure.pdf`) and **Table 1** (the label-clock table).
  Every quantity either plotted or tabulated is stated in the prose of Sec. 3; the
  archive name, byte count and retrieval date moved into that prose.
- The `AP^sync` / `AP^bias` transformation paragraph of the old Sec. 7.3. No detection
  score is computed in this paper and the full protocol is in the supplement; the two
  related-work sentences that pointed at the body now point at the supplement.
- The `tau_max` tolerance definition, moved to the supplement section that uses it.
- The label-noise whiteness result, moved to the supplement paragraph where it
  justifies dropping the instrumented estimator.

Figure 3 (`fig3_day_night.pdf`) was removed and then restored at column width once the
body fitted, because its right panel is the per-pixel evidence for the flicker the
paper now leans on.

## 8. Verification

Compiled twice with `texlive/texlive:latest`.

- `main.pdf`: **9 pages. Body ends on page 8**, the bibliography starts on page 8 and
  ends on page 9.
- **Rendered `[unmeasured]` placeholders in the body: 0.** E23 returned before this
  pass closed, so the three cells that would have carried them in Sec. 8.4 carry
  measurements. The word "unmeasured" occurs once on page 8 as ordinary prose, in the
  limitations, about the other five ceiling sequences; that is not a placeholder.
- `supplement.pdf`: 5 pages, 6 rendered placeholders, one in the opening paragraph that
  defines the convention and five in the diagnostic-score table, all pre-existing.
- Undefined references: 0. Undefined citations: 0. Undefined control sequences: 0.
  Overfull boxes: 0 in both documents. The remaining box warnings are underfull hboxes,
  loose lines in narrow two-column text, and one underfull vbox in the supplement.
- No numeral appears in prose: every measured quantity comes from a `numbers.tex`
  macro, and each new macro carries a comment naming its experiment directory.
- No surviving reference to the integer-period argument.


## 9. Addendum, E23 as a negative result

E23 is recorded in `docs/PROTOCOL_LEDGER.md` as entry 5. No pass of the 12-step
protocol has been run against it yet: it returned at the end of this restructure, and
the paper states only what it measured. The reading to check first, when a pass is run,
is that the regression is dominated by object difficulty rather than by timing --
acceleration correlates with label speed at +0.360 and with box side at +0.327, the
median along-track over cross-track error ratio rises from 1.42 in the lowest
acceleration quartile to 2.59 in the highest, and the predicted extrapolation
coefficient is two orders of magnitude below the measured one.
