# AI Writing Audit (first pass)

This report is diagnostic only. No manuscript source was edited.

GPTZero status: **not_run** (GPTZERO_API_KEY is not set)
Claude status: **not configured**; no external Claude assessment is claimed unless an Anthropic review is run.

## Summary

- Extracted prose chunks: 392
- SAFE passages: 908 (unflagged; not a proof of human authorship)
- REVIEW passages: 355
- REWRITE passages: 0
- GPTZero confidence: unavailable because the API key is not configured.

## Classification policy

A GPTZero flag alone would not trigger a rewrite. In this keyless first pass, REVIEW/REWRITE labels are independent local writing-quality signals and require author review before any edit.

## Highest-priority passages

### 1. REVIEW — Contributions.
- Source: `submission_2027/paper/latex/main.tex:94-105`
- Reasons: long sentence / modifier load, dense parenthetical insertion, comma-heavy sentence rhythm
- Exact sentence: The event branch examined here~ consumes a window of \,ms in bins ending on the label instant (Sec.~ ), so under uniform weighting its evidence is centered \,ms earlier; ablating each bin on real validation samples puts the ablation-sensitivity centroid at \,ms (Sec.~ ), the newest window carrying 22.7\ preceding windows 77.3\ nominal-time-matched detections under Eq.~2 with a placebo term and a sign-flip control, is \, \, \,ms, sits \,ms from that centroid and is compatible with zero: it is an association between nominal-time-matched detections, not an estimate of recurrent support, and the nominal timestamp encodes neither (Secs.~ -- )
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 2. REVIEW — Introduction
- Source: `paper/main.tex:90-105`
- Reasons: long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: Over a 1000\,ms horizon, the newest window accounts for 22.7\ window-ablation sensitivity, while the remaining 77.3\ regression-based temporal coefficient, estimated on nominal-time-matched detections under Eq.~2 with a vector regression, a placebo term and a sign-flip control on the velocity estimator, is \, \, \,ms, statistically compatible with zero under the selected specification, and it sits \,ms from that centroid under the reported specification.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 3. REVIEW — The same-frame intervention.
- Source: `submission_2027/paper/latex/main.tex:272-285`
- Reasons: absolute wording, long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: The intervention moves every chunk boundary windows later and changes nothing else: the same frames, the same weights, the same labels, the same evaluator, and the evaluated timestamp of each frame unchanged. labeled boxes are scored twice under this shift, once with one to four windows of recurrent history and once with seventeen to twenty, and are compared paired within frame with a cluster bootstrap over the sequences.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 4. REVIEW — Association independent of nominal-time overlap.
- Source: `paper/supplement.tex:300-323`
- Reasons: absolute wording, long sentence / modifier load
- Exact sentence: The informative direction is to open the gate or to remove it. rebuilds the rows from the five-checkpoint detection dump of Sec.~11 under association rules and refits the reported specification under each: greedy and Hungarian assignment at overlap floors from 0.05 to 0.50, and a rule that never tests overlap at all, admitting a detection whose center falls within a fixed multiple of the label's box scale.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 5. REVIEW — Association independent of nominal-time overlap.
- Source: `submission_2027/paper/latex/supp.tex:300-323`
- Reasons: absolute wording, long sentence / modifier load
- Exact sentence: The informative direction is to open the gate or to remove it. rebuilds the rows from the five-checkpoint detection dump of Sec.~11 under association rules and refits the reported specification under each: greedy and Hungarian assignment at overlap floors from 0.05 to 0.50, and a rule that never tests overlap at all, admitting a detection whose center falls within a fixed multiple of the label's box scale.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 6. REVIEW — Conclusion
- Source: `submission_2027/paper/latex/main.tex:778-1004`
- Reasons: long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: Two scores at the same nominal timestamp are not performance at the same effective time when the recurrent support behind them differs, so comparisons across recurrent architectures should report or control predictor initialization, reset policy, chunk boundaries, effective history and label-acquisition intervals alongside the score, which makes these quantities protocol-identifiable. { {0.4pt}
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 7. REVIEW — Preamble
- Source: `submission_2027/paper/latex/main.tex:33-33`
- Reasons: long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: Two supporting diagnostics bound the interpretation without being used as recurrent-support estimators: on the predictor side, the newest RVT input window has an ablation-sensitivity centroid \,ms before the label instant and a nominal-time-matched regression coefficient of \, \, \,ms; on the label side, within-exposure event timing contains an illumination-locked component.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 8. REVIEW — The DSEC measurements
- Source: `paper/supplement.tex:469-481`
- Reasons: absolute wording, long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: {Every DSEC training sequence whose exposure is pinned at \, s, measured per labeled box over the events inside that box during that frame's own published exposure window, with at least events per box. is the median over boxes of the modulation depth at \,Hz. and are the median over boxes of the Rayleigh statistic at \,Hz and at the off-frequency control on the same events.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 9. REVIEW — The DSEC measurements
- Source: `submission_2027/paper/latex/supp.tex:469-481`
- Reasons: absolute wording, long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: {Every DSEC training sequence whose exposure is pinned at \, s, measured per labeled box over the events inside that box during that frame's own published exposure window, with at least events per box. is the median over boxes of the modulation depth at \,Hz. and are the median over boxes of the Rayleigh statistic at \,Hz and at the off-frequency control on the same events.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 10. REVIEW — Effect of temporal displacement on checkpoint ordering
- Source: `paper/supplement.tex:627-634`
- Reasons: absolute wording, long sentence / modifier load
- Exact sentence: Whether the interval changes a needs more than one detector, so all released checkpoints of main Sec.~3.3 were run over the Gen1 validation split under one protocol: the same frames, the same confidence floor of 0.01 and non-maximum-suppression overlap of 0.65, and ground truth that is identical across the five and identical to the dump main Sec.~3.5 already uses.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 11. REVIEW — Effect of temporal displacement on checkpoint ordering
- Source: `submission_2027/paper/latex/supp.tex:627-634`
- Reasons: absolute wording, long sentence / modifier load
- Exact sentence: Whether the interval changes a needs more than one detector, so all released checkpoints of main Sec.~4.3 were run over the Gen1 validation split under one protocol: the same frames, the same confidence floor of 0.01 and non-maximum-suppression overlap of 0.65, and ground truth that is identical across the five and identical to the dump main Sec.~4.5 already uses.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 12. REVIEW — Introduction
- Source: `paper/main.tex:107-114`
- Reasons: absolute wording, long sentence / modifier load
- Exact sentence: Chunk position assigns detections between one and twenty-one windows of recurrent history under a single reported score, and the score moves with it: on all labeled boxes, the 1--4 versus 17--21 window contrast is mAP points net of the RVT control, while the same-frame chunk-boundary intervention changes S5-B by points ( points on the velocity-evaluable subset).
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 13. REVIEW — The observational contrast across chunk positions.
- Source: `submission_2027/paper/latex/main.tex:287-300`
- Reasons: long sentence / modifier load, dense parenthetical insertion
- Exact sentence: This contrast compares different frames, so it is differenced against the three RVT checkpoints, evaluated on the same frames with a state that crosses chunk boundaries; that controls for frame-position effects shared with them and leaves points for S5-B ( ) and for S5-S ( ), against placebo differences among the RVT checkpoints of at most points ( ).
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 14. REVIEW — Event benchmarks and their exposures.
- Source: `paper/main.tex:250-279`
- Reasons: long sentence / modifier load
- Exact sentence: That a frame's exposure is long relative to event timing has been stated: Event-based deblurring~ argues that accumulating events from a single frame timestamp loses information, deblurring work names auto-exposure as why the width is unknown~ , and RENet~ uses a DSEC exposure interval as its event window while describing it as short.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 15. REVIEW — Event benchmarks and their exposures.
- Source: `submission_2027/paper/latex/main.tex:228-257`
- Reasons: long sentence / modifier load
- Exact sentence: That a frame's exposure is long relative to event timing has been stated: Event-based deblurring~ argues that accumulating events from a single frame timestamp loses information, deblurring work names auto-exposure as why the width is unknown~ , and RENet~ uses a DSEC exposure interval as its event window while describing it as short.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 16. REVIEW — The same frames under four boundary positions
- Source: `paper/supplement.tex:923-931`
- Reasons: rhetorical contrast, long sentence / modifier load
- Exact sentence: The three amounts select the same labeled frames, so the rungs are one population under three doses rather than three separate comparisons; asserts set equality of the selected frames before recording the curve. re-runs the release's own boundary placement through the identical pipeline and serves as the negative control
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 17. REVIEW — Scope and limitations
- Source: `submission_2027/paper/latex/main.tex:768-770`
- Reasons: long sentence / modifier load
- Exact sentence: Temporal-support identifiability is a uniqueness claim, so one controlled pair with identical recorded protocol variables, different effective support, and different score is already a protocol-level counterexample; the second checkpoint tests that the observed violation is not confined to one released weight set.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 18. REVIEW — Recurrent history under the released streaming evaluation.
- Source: `paper/main.tex:416-453`
- Reasons: long sentence / modifier load, dense parenthetical insertion
- Exact sentence: Differencing against the three RVT checkpoints, evaluated on the same frames with a state that crosses chunk boundaries, controls for frame-position effects shared with the RVT checkpoints and leaves points for S5-B ( ) and for S5-S ( ), against placebo differences among the RVT checkpoints of at most points ( ).
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 19. REVIEW — Exposure and labels
- Source: `paper/main.tex:708-722`
- Reasons: absolute wording
- Exact sentence: DSEC provides a separate exposure-side analysis: published exposure intervals bound the interval within which event timing is observed, while within-exposure event timing contains illumination-locked structure and therefore cannot be uniquely attributed to object timing without separating that structure.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 20. REVIEW — Exposure and labels
- Source: `submission_2027/paper/latex/main.tex:685-699`
- Reasons: absolute wording
- Exact sentence: DSEC provides a separate exposure-side analysis: published exposure intervals bound the interval within which event timing is observed, while within-exposure event timing contains illumination-locked structure and therefore cannot be uniquely attributed to object timing without separating that structure.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

## Residue scan

### Manuscript sources (`submission_2027/paper/latex/*.tex`, the files that ship)

- `placeholder` in `submission_2027/paper/latex/numbers.tex`

### Other scanned directories (`src/`, `docs/`; tooling and internal notes, not submitted)

- `rewrite` in `submission_2027/paper/latex/README.md`
- `placeholder` in `submission_2027/paper/latex/README.md`
- `Here's` in `submission_2027/paper/latex/cvpr.sty`
- `prompt` in `submission_2027/paper/latex/CHECKLIST_VERDICT_0916.md`
- `instruction` in `submission_2027/paper/latex/CHECKLIST_VERDICT_0916.md`
- `rewrite` in `submission_2027/paper/latex/CHECKLIST_VERDICT_0916.md`
- `placeholder` in `submission_2027/paper/latex/CHECKLIST_VERDICT_0916.md`
- `Certainly` in `submission_2027/paper/latex/AI_WRITING_AUDIT.md`
- `Here's` in `submission_2027/paper/latex/AI_WRITING_AUDIT.md`
- `prompt` in `submission_2027/paper/latex/AI_WRITING_AUDIT.md`
- `instruction` in `submission_2027/paper/latex/AI_WRITING_AUDIT.md`
- `rewrite` in `submission_2027/paper/latex/AI_WRITING_AUDIT.md`
- `placeholder` in `submission_2027/paper/latex/AI_WRITING_AUDIT.md`
- `rewrite` in `src/e52_selftest.py`
- `rewrite` in `src/e51_check.py`
- `instruction` in `src/SSMViT/README.md`
- `instruction` in `src/RVT/README.md`
- `placeholder` in `docs/REBUILD_0905.md`
- `rewrite` in `docs/AUDIT_R1_88_197.md`
- `placeholder` in `docs/AUDIT_R1_88_197.md`
- `placeholder` in `docs/FIXES_APPLIED.md`
- `Certainly` in `docs/AUDIT_88_197.md`
- `rewrite` in `docs/AUDIT_88_197.md`
- `placeholder` in `docs/AUDIT_88_197.md`
- `rewrite` in `docs/CHECKLIST_197.md`
- `prompt` in `docs/CHECKLIST_VERDICT_0916.md`
- `instruction` in `docs/CHECKLIST_VERDICT_0916.md`
- `rewrite` in `docs/CHECKLIST_VERDICT_0916.md`
- `placeholder` in `docs/CHECKLIST_VERDICT_0916.md`
- `placeholder` in `docs/RESTRUCTURE_0904.md`
- `rewrite` in `docs/AUDIT_R1_A_H.md`
- `placeholder` in `docs/AUDIT_R1_A_H.md`
- `instruction` in `docs/NOVELTY.md`
- `rewrite` in `docs/PROTOCOL_LEDGER.md`
- `instruction` in `docs/AUDIT_A_H.md`
- `rewrite` in `docs/AUDIT_A_H.md`
- `placeholder` in `docs/AUDIT_A_H.md`
- `prompt` in `docs/REFERENCE_PAPERS.md`
- `rewrite` in `docs/REFERENCE_PAPERS.md`
- `placeholder` in `docs/REFERENCE_PAPERS.md`

## GPTZero raw-response location

`.ai-audit/gptzero_raw.json`

