# Response to external review #6 (2026-09-08) — Accept, 0 Critical, 2 Major, 3 Must-Fix

The review returns **Accept**, places the paper at the **lower edge of the accepted band**,
records **Technical Soundness: Pass**, and names **no acceptance-critical experiment**. All
three Must-Fixes were text-only and are applied.

## Must-Fix 1 — expose the specification dependence beside the 3.65-SE headline

*Objection.* Table 1 moves τ materially as controls are added (+17.51 → +14.62 → −7.62 →
−2.40 ms) and the reported specification was selected by the placebo, so the abstract and
conclusion made "3.65 standard errors" read as more specification-robust than the analysis
establishes. Valid: the range was in Sec. 3.5 but not where the headline is remembered.

*Applied, in three places.*

- **Abstract.** After the 3.65-SE clause: "That offset spans −20.2 to +11.1 ms across
  specifications with geometric controls, never reaching the +23.81 ms the centroid would
  require."
- **Sec. 3.5.** The sign convention is now stated at the claim: "On the convention of Eq. 1
  the centroid hypothesis is τ = +23.81 ms, and no specification carrying geometric controls
  reaches it: τ spans −20.2 to +11.1 ms across them." The reviewer is right that this is the
  reading that matters — the qualitative separation survives every controlled specification
  while the exact magnitude does not.
- **Conclusion.** "…at 3.65 standard errors, which no specification carrying geometric
  controls overturns, …"

The weaker and clearly true claim was chosen deliberately. Every controlled τ is also closer
to the label instant than to the centroid, but "none reaches it" is what the ladder shows
without further argument.

## Must-Fix 2 — frame the DSEC half as an attribution bound in the abstract too

*Objection.* Sec. 4.4 and the limitations already say "identifiability bound, not a timing
error", but the abstract's "exposure-conditioned support of the labels" could be read as a
measurement of per-object label time, which the paper's own random-position and background
controls do not support. Valid: a framing mismatch, not a claim mismatch.

*Applied.* The abstract now says outright, before the flicker result, that **no per-object
label time is inferred**, and calls what follows an **attribution limit**. The enumeration
sentence became "This paper separates the three and measures what released artifacts identify
of each", which is honest about the third being bounded rather than identified.

## Must-Fix 3 — cite *Seeing Motion at Nighttime with an Event Camera* (CVPR 2024)

*Objection.* The nearest label-side accepted prior was missing, and its absence could shrink
the perceived novelty to "illumination-dependent event timing was already known".

*Applied.* Cited in Sec. 2 beside the sensor-latency discussion, with the distinction stated:
"Those corrections target the sensor; here the released exposure metadata and event stream
bound what a per-object temporal statistic computed inside one published exposure can be
attributed to."

## What paid for the added text

The body still ends inside page 8. The additions were funded by compressing the protocol-work
gloss while keeping all four of its citations, removing a statement of the τ range that
appeared twice three paragraphs apart, shortening a doubled clause in the abstract about the
recurrent tail, compressing the placebo sign-split diagnosis, and moving two provenance
details — which DSEC-Det archive was measured, and how Gen1 tracks are associated — into the
supplement, where they are stated in full.

## Not applied, and why

The review's three suggested experiments are classified by the reviewer as "high-value risk
reduction" (an independent detector family; an output-time specification multiverse) and
"nice-to-have" (a flicker-removed DSEC control), with **none** acceptance-critical and each
answered "No" to "would its absence alone justify a Weak Reject". They are not run. The first
is already the leading item in `paper/OUTSTANDING.md`; the second is largely a presentation of
data already in Table 1 and Sec. 3.5, and is a candidate for the supplement if space allows;
the third would change the claim from a bound to a causal estimate, which the paper
deliberately does not make.

## Verification after the edits

`main.pdf` body ends inside page 8, references pages 9–10; `supplement.pdf` 5 pages. Both:
0 TeX errors, 0 undefined control sequences, 0 overfull boxes, 0 undefined references,
0 undefined citations. `src/audit_numbers.py`: 109 macros re-derived from their artifacts,
0 disagree, checker self-test 109/109. Style scan for checklist items 188–191: clean.
