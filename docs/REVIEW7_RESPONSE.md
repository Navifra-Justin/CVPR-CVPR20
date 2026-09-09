# Response to external review #7 (2026-09-08) — Borderline, 0 Critical, 1 Must-Fix

Review #7 and review #6 read the same manuscript and agree on everything except one axis.
Both: Technical Soundness **Pass**, Novelty **Clear**, Distinct Contribution **Clearly
distinct**, not subsumed by the nearest accepted priors, and neither treats "few datasets" or
"not SOTA" as grounds for rejection. #6 returned **Accept**; #7 returned **Borderline** on
significance, with one gating issue and one Must-Fix.

## The gating issue, and what was run for it

> "Temporal-support mismatch가 실제 benchmark conclusion을 materially 바꾼다는 evidence가 없음."

The review's own experiment was run: E51 dumped detections for all five released Gen1
checkpoints under one protocol, E52 and E53 scored each at the label instant and again at the
displacement it prefers, in four speed strata, and E54 emitted the macros. Details and the
two integrity checks that preceded any comparison are in `experiments/e51_ranking/README.md`.

**The result is negative, and it is reported as such.** The ordering does not change in any
stratum and no pair reverses.

**It is a bound rather than a failure to find an effect.** In every stratum the largest gain
any model draws from alignment is at most 52 % of the smallest gap between adjacent models,
0.058 against 0.112 points at the tightest. No refinement of the displacement grid, and no
continuous optimum, can reorder them. The paper's existing claim — that this metric does not
resolve the interval — was an assertion about one checkpoint; it is now a quantitative limit
over five checkpoints, two architectures and four speed strata.

This is not what the review hoped for. It asked whether alignment changes a conclusion, and
the answer is that it cannot, at this scale. That answer strengthens the identifiability
framing and does not manufacture the significance the review wanted. Both readings are
available to a reviewer and the paper does not argue for one.

**What did move.** The ordering is unstable across speed strata: `s5vit-base` is first in
both middle strata and last above 50 px/s, `rvt-t` is third overall, last between 25 and
50 px/s and second above 50. The size of that reordering is more than ten times the largest
alignment effect. It is reported in the supplement and attributed to object speed, not to the
temporal support this paper measures, because that is what it is.

## Must-Fix — the distance claim's scope

> "'effect is graded by distance'만 단독으로 읽으면 broader quantitative relationship으로 해석될 여지가 있습니다."

Not applicable to this manuscript. The graded-by-distance claim the review quotes belongs to
a different paper; review #7's body text (DEIMv2, RF-DETR, Grounding DINO, encoder-position
allocation, width-matched label-only intervention) describes the open-world detection paper,
not this one. The verdict, the gating issue and the recommended experiment are nonetheless
answerable here and were answered above, since they turn on cross-model generality rather
than on that paper's specifics.

## Where it went in the paper

- Main Sec. 3.6, one clause on the sentence that already states the metric does not register
  the separation: the ordering of the five released checkpoints is unchanged by displacing
  each to the instant the metric prefers, and cannot change, since the largest alignment gain
  within a stratum is 52 % of the smallest adjacent gap.
- Conclusion: "…a separation average precision registers as 0.04 points and no reordering."
- Supplement: a section with the four orderings, the bound, and the speed-stratum instability.

## Verification

`main.pdf` body ends inside page 8, references pages 9–10; `supplement.pdf` 6 pages. Both:
0 TeX errors, 0 undefined control sequences, 0 overfull boxes, 0 undefined references,
0 undefined citations. `src/audit_numbers.py`: 118 macros re-derived from their artifacts,
0 disagree, self-test 118/118. Style scan for checklist items 188–191: clean.
