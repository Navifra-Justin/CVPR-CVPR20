# Response to external review #4 (2026-09-07, evening)

Verdict: **Borderline**, lower edge of the accepted band. **Critical 0, Major 2**, four
must-fixes, and the review states explicitly that **no new experiment is
acceptance-critical** — for each of the three it considers, it answers "is Weak Reject
reasonable for its absence?" with No.

The two Majors are both about framing, not evidence: significance framing, and contribution
coherence. All four must-fixes are applied.

## Must-fix 1 — 27.3 ms must not read as the principal quantity

The centroid moves 3.9 ms across four instruments and `tau` spans −20.2 to +11.1 ms across
specifications; the abstract presented `27.3 ms` as a point estimate. **Applied.** The
abstract now leads with the separation and Sec. 3.6 says it outright:

> the output is incompatible with that window's centroid at 3.81 standard errors, and
> 27.3 ms is the point estimate of their distance under the reported specification rather
> than a latency of this architecture.

## Must-fix 2 — separate "evidence time" from the newest window's influence centroid

The full recurrent support does not decay within the measured second and its centroid
follows the horizon, so −24.94 ms is the **newest window's** influence centroid and nothing
larger. **Applied**, and further than asked:

- The phrase "evidence centroid" now appears **zero times** in the manuscript.
- The abstract states the non-identification directly: "a tail that does not decay within
  the second measured and no centroid the measured horizon identifies."
- **The title changed** to *The Temporal Support Behind One Benchmark Timestamp: A Released
  Event Detector and DSEC's Ceiling Exposures*, which removes "Evidence Time" from the one
  place a reader meets it first.

## Must-fix 3 — bind the two halves into one thesis

**Applied**, in the abstract, the introduction and the conclusion, in the review's own
terms: one nominal timestamp stands for the temporal support of both sides of the
comparison, hiding on the predictor side the separation between the evidence a network is
given and the state it emits, and on the label side exposure-conditioned structure that
object motion does not account for. The title now names both sides under that thesis.

## Must-fix 4 — the small mAP effect is the second finding, not a caveat

The review calls this "the most important revision in this manuscript", and it is right:
the 0.06-point response was being read as a concession. **Applied** in the abstract, in
Sec. 3.6 and in the conclusion:

> The curve is nearly flat, and that is the second result rather than a caveat on the
> first. ... A score that insensitive cannot be used to ask whether a detector's query
> timestamp represents the temporal support of its prediction: the mismatch measured above
> is real and this metric does not register it.

## What was not changed, and why

The review's three candidate experiments — a second checkpoint, a second dataset sweep, a
controlled-lighting DSEC capture — are all recorded as **not** grounds for a Weak Reject
given the paper's stated scope. The scope statements they rely on are already in
Limitations and are unchanged.

## What the paper now claims, in the order it claims it

1. One benchmark timestamp stands for the temporal support of both sides of the comparison.
2. On the predictor side, the newest window's influence centroid is −24.94 ms; the newest
   window carries 22.7 % of the influence; the support has no centroid the measured horizon
   identifies; the output time is 3.81 SE from that centroid.
3. Average precision moves 0.06 points across that interval, so the metric cannot register
   the mismatch.
4. On the label side, six ceiling-exposure sequences carry a 100 Hz mains harmonic series
   that bounds what a per-object temporal statistic measured inside one can be attributed to.
