# Audit round after E45 (2026-09-08)

Scope: `paper/main.tex`, `paper/supplement.tex`, `paper/numbers.tex`, the figure and video
generators, run against `docs/CHECKLIST_197.md`. This round was triggered by a measurement
correction, so it began with the numbers and then read the whole body once, continuously,
before judging any sentence.

## Defects found and fixed

| # | Item | What was wrong | Fix |
|---|---|---|---|
| 1 | 192 evidence-calibrated claim | "The profile is close to flat", CV 0.034. The corrected profile has CV 0.131 and a heaviest/lightest ratio of 1.52. | Replaced by the measured statement: the profile varies across bins and is balanced between halves, 48.6 % / 51.4 %, which is what actually keeps the centroid near the uniform value. |
| 2 | 8 traceability / 40 number consistency | Ten macros and every value derived from the centroid still carried E17's number. | Recomputed from the artifacts (`e46_recompute.py`), and the mAP cost re-evaluated at the exact centroid instead of read off a 5 ms grid (`e46b_map_at_centroid.py`). |
| 3 | build hygiene | `numbers.tex` line 696 carried a stray `}`, producing a real `! Too many }'s` on every build. The previous build check counted only "Undefined control sequence" and "Overfull", so it had never looked. | Brace removed; the build check now counts lines beginning `! ` as well, plus undefined references and citations. |
| 4 | 8 traceability | Figure 2b still labelled the shaded band's edge "evidence centroid", a term withdrawn after review #4 because it conflates the newest window with the whole support. | Relabelled "newest window's centroid", and the label now reads its position from the artifact rather than a literal. |
| 5 | cross-reference | "the identification is the sweep of Sec. 4.1" pointed at *Exposure and labels*; the sweep is in *The line, and the per-pixel test*. That subsection had no label. | Added `sec:line` and repointed. |
| 6 | 188 rhetorical contrast | "The profile is not uniform, but it is balanced"; "a label velocity that is not observed but finite differenced". | Both restated positively. |
| 7 | 189 meta-sentence | "what the measurement adds is that…" (abstract), "What it does establish is the separation", "What it does not enforce is the interval", "and that is the second result". | All four replaced with direct statements. The one that was doing review-mandated work — flagging the flat mAP curve as a finding — kept that job as a claim rather than as commentary. |
| 8 | 190 technical agency | "so it sees both edges of that oscillation". | "so both edges of that oscillation produce events". |
| 9 | 147 reference naturalness | The introduction's closing passage opened "That timestamp…", whose antecedent was three paragraphs back. | "The single timestamp the metric is indexed by…". |
| 10 | video, item 8 | Scene 2 said "the whole sweep moves mAP by 0.9 points", the paper's figure over ±60 ms, on top of a curve running −50 to +30 ms that moves 0.37. | The clip computes the span of the curve it draws. |
| 11 | 152 single central thesis | The introduction restated its three measurements as a bulleted list immediately after stating them in prose, working against review #5's first must-fix. | Replaced by one connected passage, which also freed the space E44 needed. |

## Added

- **E44 in the body** (Sec. 3.3, *Across the released capacities*): three released capacities,
  4.41 to 18.54 M parameters, newest-window centroids spanning 0.27 ms, support lengthening
  with capacity. This is item 163's *generalization* level of evidence, which the paper
  previously reached only in the supplement.
- **`src/audit_numbers.py`**: 87 macros re-derived from their artifacts. Zero disagree. The
  checker is itself mutation-tested, per [[test-the-checkers]]; all 87 entries reject a
  corrupted value.
- **A containment check on the state defect**: of the six scripts that run a counterfactual
  forward pass, only the two already withdrawn had it. The detection dump behind the mAP
  sweep and the output-time regression is unaffected.

## Checked and left alone

- Sentences that were already natural were not touched. The 197-item pass produced eleven
  edits, and each replaced a construction the checklist names, not a construction that merely
  had an alternative.
- The four-instrument spread (4.01 ms) is wider than it was (3.9 ms). It is reported as
  instrument dependence, unaveraged, in both the body and the limitations.
- `\rvtCentroidMeas` (−23.81, E45, 480 samples) and `\capBinT` (−23.84, E44, 576 samples) are
  the same quantity on different samples and differ by less than the bootstrap standard error.
  The body now says so in the capacity paragraph rather than leaving a reader to notice.

## Standing verdict

External reviews #3 (Reject), #4 (Borderline, Critical 0), #5 (Borderline lower edge,
Critical 0) were answered in `docs/REVIEW{3,4,5}_RESPONSE.md`. Neither #4 nor #5 named an
acceptance-critical experiment. Since #5, the paper has gained the generality axis it asked
for (three capacities), singularized its contribution statement, and corrected its
most-quoted number downward by 1.1 ms without reversing any claim. Reference papers are the
externally fetched set recorded in `docs/REFERENCE_PAPERS.md` (2026-09-02), which includes
the nearest living neighbour, *Beyond Duality* (CVPR 2026), evaluated on the same DSEC-Det.

Against that set the honest self-grade is still **Borderline**, above the lower edge it sat on
at review #5. What moves it is generality, and the next step is a second architecture rather
than a fourth capacity: an SSM or DETR-style event detector with released Gen1 weights, run
through the same occlusion instrument. That is not run, and it is the first thing named in
`paper/OUTSTANDING.md`.

---

## Second pass, 2026-09-08 05:30, after the architecture port

Added since the table above:

- **A second architecture in the body** (E47/E48). Five released checkpoints, two temporal
  operators, centroids between −23.76 and −24.72 ms. Sec. 3.3's paragraph, Fig. 2a's grey
  overlay, the conclusion's opening clause and the limitations paragraph all state it. This
  moves the paper up item 163's evidence hierarchy from *generalization across capacity* to
  *generalization across architecture*, which is what external review #5 asked for.
- **A supplement section on the SSM release's carried state** (E47c), reported as a property
  of the release with a control arm, not as a claim about the architecture.

Defects this pass found and fixed:

| # | Item | What was wrong | Fix |
|---|---|---|---|
| 12 | 8 traceability | The first S5 numbers measured a model whose carried state is inert, because the one-window calling convention that RVT uses does not carry state in that implementation. | Withdrawn with a written reason; re-measured with the release's own chunked convention (E47b), and the inertness itself measured by position with a control (E47c). |
| 13 | checker coverage | `audit_numbers.py` stopped checking eleven macros when their artifacts were moved aside, and reported "0 disagree" while the manuscript still quoted them. Silence read as success. | It now fails on any macro it knows how to derive whose artifact is absent. |
| 14 | build hygiene | `\ref` to a supplement label from the main document, and a `\cite` in the supplement, which has no bibliography. | Both replaced with plain text; 0 undefined references and 0 undefined citations in both documents. |
| 15 | figure provenance | Fig. 2a's overlay read the withdrawn artifacts by filename and would have drawn nothing once they moved. | Repointed at the chunked artifacts; the panel is rendered and checked visually. |
| 16 | claim precision | The ledger and two notes carried an intermediate reading of the S5 code — that the state reaches positions 1, 2, … and misses only position 0 — which the measurement contradicted. | Corrected in all three places, with the correction itself recorded: the measurement corrected the reading, not the other way round. |

Page budget: the body still ends inside page 8. Paying for the new paragraph took a
redundant sentence out of Sec. 3.1, a duplicated clause out of related work, two intermediate
stratum numbers out of Sec. 3.6 that Fig. 2b already shows, and the erosion control out of
the limitations into the supplement, where its two numbers are now stated in full.

Standing verdict unchanged in kind, stronger in degree: **Borderline**, and the generality
axis that held it at the lower edge at review #5 is the one that moved.

---

## Third pass, 2026-09-08, external review #6

Verdict **Accept**, Technical Soundness **Pass**, 0 Critical, no acceptance-critical
experiment, positioned at the lower edge of the accepted band. Three Must-Fixes, all
text-only, all applied — see `docs/REVIEW6_RESPONSE.md` for the full response.

| # | Item | What was wrong | Fix |
|---|---|---|---|
| 17 | 192 evidence-calibrated claim | The 3.65-SE separation read as specification-robust in the abstract and conclusion, though Table 1 moves τ materially as controls are added and the range lived only in Sec. 3.5. | The range and the sign convention (the centroid hypothesis is τ = +23.81 ms) now sit beside the claim in all three places. |
| 18 | 152 single central thesis / framing | The abstract's "exposure-conditioned support of the labels" could be read as a measurement of per-object label time, which the paper's own controls do not support. | The abstract now says outright that no per-object label time is inferred and calls the DSEC result an attribution limit. |
| 19 | prior-art coverage | The nearest label-side accepted prior, *Seeing Motion at Nighttime with an Event Camera* (CVPR 2024), was uncited. | Cited in Sec. 2 with the distinction stated in two clauses. |

A note on the review's own reading, which is worth keeping: it points out that on the paper's
sign convention every geometrically controlled τ, including the largest at +11.1 ms, is closer
to the label instant than to the +23.81 ms the centroid hypothesis requires. That is a
stronger statement than the paper makes; the manuscript claims only that none of them reaches
the centroid, which is what the ladder shows without further argument.
