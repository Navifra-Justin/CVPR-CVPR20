# Response to external review #8 (2026-09-09) — Accept, 0 gating issues, 1 Must-Fix

Review #8 returns **Accept** on the current PDF and supplement: Technical Soundness **Pass**,
Distinct Contribution **Clearly distinct**, Novelty **Clear**, Significance **Meaningful**,
Evidence **Strong**, lower edge of the accepted band. It records **no acceptance-critical
experiment and no gating issue**, and one Must-Fix, which is applied.

## Must-Fix — the output-time wording

*Objection.* The abstract said the regression "place[s] the output time at the label
instant", which is stronger than a fit of $-2.40\pm7.18$\,ms supports. That number is
consistent with zero; it does not establish equality. Sec. 3.5 already said so; the abstract
and introduction did not. Valid, and the review is right that this is the easiest place for a
statistically minded reviewer to attack the paper's own central distinction.

*Applied, in three places.*

- **Abstract.** "…put the output time at $-2.40\pm7.18$\,ms: consistent with the label
  instant, which its training objective encourages, and 3.65 standard errors from the
  window's own centroid. This establishes the separation, not an equality with the label
  timestamp."
- **Introduction.** "…the measurement of Sec. 3.4 is consistent with it, at
  $-2.40\pm7.18$\,ms, which is a failure to reject and not a demonstration that they
  coincide."
- **Sec. 3.5** already carried the caveat and now states it once rather than twice; the
  sentence that follows still says what the measurement does establish.

The conclusion needed no change: it already says the output time is *bounded away from* the
window's centroid rather than equal to the label instant.

## Not applied, and why

The review's one recommended experiment — repeating the predictor-side audit on a released
detector independent of the RVT/SSM-ViT lineage — is classified by the review itself as
"Would broaden the claim", not required to establish it, and it answers "No" to whether its
absence alone would justify a Weak Reject. It is not run. It remains the leading item in
`paper/OUTSTANDING.md`, and it is the same axis review #5 named and E47/E48 partly answered
by adding a second architecture that shares a repository.

## On the two objections the review raises but does not treat as gating

Both concern significance rather than validity, and both are already stated in the paper
rather than argued away: the predictor-side work is one dataset and one repository lineage,
and correcting the measured separation moves mAP by 0.04 points and reorders none of the five
checkpoints. The second of those is not a failed experiment — it is the evidence for the
paper's own claim that this metric cannot resolve the interval, and E51–E53 turn it into a
bound: within a stratum the largest alignment gain is 52 % of the smallest gap between
adjacent models, so no realignment can reorder them.

## Verification after the edits

`main.pdf` body ends within page 8, references pages 9–10; `supplement.pdf` 6 pages. Both:
0 TeX errors, 0 undefined control sequences, 0 overfull boxes, 0 undefined references,
0 undefined citations. `src/audit_numbers.py`: 118 macros re-derived from their artifacts,
0 disagree, self-test 118/118. Style scan for checklist items 188–191: clean. One clause
moved to the supplement to pay for the added wording (the DSEC stereo co-trigger check),
where it is stated in full.
