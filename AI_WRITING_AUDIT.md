# AI Writing Audit (first pass)

This report is diagnostic only. No manuscript source was edited.

GPTZero status: **not_run** (GPTZERO_API_KEY is not set)
Claude status: **not configured**; no external Claude assessment is claimed unless an Anthropic review is run.

## Summary

- Manuscript sources read: 3 — submission_2027/paper/latex/main.tex, submission_2027/paper/latex/numbers.tex, submission_2027/paper/latex/supp.tex
- Residue-scan files read: 501 (3 shipping `.tex`)
- Sentences examined: 663
- Extracted prose chunks: 209
- SAFE passages: 483 (unflagged; not a proof of human authorship)
- REVIEW passages: 181
- REWRITE passages: 0
- GPTZero confidence: unavailable because the API key is not configured.

## Classification policy

A GPTZero flag alone would not trigger a rewrite. In this keyless first pass, REVIEW/REWRITE labels are independent local writing-quality signals and require author review before any edit.

## Highest-priority passages

### 1. REVIEW — The same-frame intervention.
- Source: `submission_2027/paper/latex/main.tex:277-290`
- Reasons: absolute wording, long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: The intervention moves every chunk boundary windows later and changes nothing else: the same frames, the same weights, the same labels, the same evaluator, and the evaluated timestamp of each frame unchanged. labeled boxes are scored twice under this shift, once with one to four windows of recurrent history and once with seventeen to twenty, and are compared paired within frame with a cluster bootstrap over the sequences.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 2. REVIEW — Temporal windows and benchmark identifiability.
- Source: `submission_2027/paper/latex/main.tex:137-151`
- Reasons: rhetorical contrast, absolute wording, long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: Both released implementations leave a frame's position inside the evaluation chunk unspecified by the protocol rather than fixed by the model: the recurrent state entering a chunk is the state saved at the end of the previous chunk and is reset only at the first sample of a sequence, and under streaming sampling every timestep emits predictions while otherwise only the last does (RVT :232,\,243 and SSM-ViT :315,\,318).
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 3. REVIEW — Association independent of nominal-time overlap.
- Source: `submission_2027/paper/latex/supp.tex:302-325`
- Reasons: absolute wording, long sentence / modifier load
- Exact sentence: The informative direction is to open the gate or to remove it. rebuilds the rows from the five-checkpoint detection dump of Sec.~11 under association rules and refits the reported specification under each: greedy and Hungarian assignment at overlap floors from 0.05 to 0.50, and a rule that never tests overlap at all, admitting a detection whose center falls within a fixed multiple of the label's box scale.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 4. REVIEW — Preamble
- Source: `submission_2027/paper/latex/main.tex:41-41`
- Reasons: long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: Two supporting diagnostics bound the interpretation without being used as recurrent-support estimators: on the predictor side, the newest RVT input window has an ablation-sensitivity centroid \,ms before the label instant and a nominal-time-matched regression coefficient of \, \, \,ms; on the label side, within-exposure event timing contains an illumination-locked component.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 5. REVIEW — The DSEC measurements
- Source: `submission_2027/paper/latex/supp.tex:471-483`
- Reasons: absolute wording, long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: {Every DSEC training sequence whose exposure is pinned at \, s, measured per labeled box over the events inside that box during that frame's own published exposure window, with at least events per box. is the median over boxes of the modulation depth at \,Hz. and are the median over boxes of the Rayleigh statistic at \,Hz and at the off-frequency control on the same events.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 6. REVIEW — Effect of temporal displacement on checkpoint ordering
- Source: `submission_2027/paper/latex/supp.tex:629-636`
- Reasons: absolute wording, long sentence / modifier load
- Exact sentence: Whether the interval changes a needs more than one detector, so all released checkpoints of main Sec.~4.3 were run over the Gen1 validation split under one protocol: the same frames, the same confidence floor of 0.01 and non-maximum-suppression overlap of 0.65, and ground truth that is identical across the five and identical to the dump main Sec.~4.5 already uses.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 7. REVIEW — The observational contrast across chunk positions.
- Source: `submission_2027/paper/latex/main.tex:292-305`
- Reasons: long sentence / modifier load, dense parenthetical insertion
- Exact sentence: This contrast compares different frames, so it is differenced against the three RVT checkpoints, evaluated on the same frames with a state that crosses chunk boundaries; that controls for frame-position effects shared with them and leaves points for S5-B ( ) and for S5-S ( ), against placebo differences among the RVT checkpoints of at most points ( ).
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 8. REVIEW — Conclusion
- Source: `submission_2027/paper/latex/main.tex:794-794`
- Reasons: absolute wording, long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: At the same evaluated timestamp, with frames, weights, labels and evaluator fixed, moving only the chunk boundary shifts S5-B by mAP over all labeled validation boxes and mAP on the velocity-evaluable subset, because one pooled score in the released SSM-ViT pipeline combines predictions carrying one to twenty-one windows of recurrent history.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 9. REVIEW — Event benchmarks and their exposures.
- Source: `submission_2027/paper/latex/main.tex:233-262`
- Reasons: long sentence / modifier load
- Exact sentence: That a frame's exposure is long relative to event timing has been stated: Event-based deblurring~ argues that accumulating events from a single frame timestamp loses information, deblurring work names auto-exposure as why the width is unknown~ , and RENet~ uses a DSEC exposure interval as its event window while describing it as short.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 10. REVIEW — The same frames under four boundary positions
- Source: `submission_2027/paper/latex/supp.tex:928-936`
- Reasons: rhetorical contrast, long sentence / modifier load
- Exact sentence: The three amounts select the same labeled frames, so the rungs are one population under three doses rather than three separate comparisons; asserts set equality of the selected frames before recording the curve. re-runs the release's own boundary placement through the identical pipeline and serves as the negative control
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 11. REVIEW — Contributions.
- Source: `submission_2027/paper/latex/main.tex:81-91`
- Reasons: absolute wording, long sentence / modifier load
- Exact sentence: Its measured consequence: support the protocol does not record moves a pooled leaderboard-style score by mAP overall and mAP on the velocity-evaluable subset, while the same benchmark reproduces its validation-split ordering over all labeled boxes in only \,\ predictor-side and label-side audits delimit the result
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 12. REVIEW — Exposure and labels
- Source: `submission_2027/paper/latex/main.tex:705-719`
- Reasons: absolute wording
- Exact sentence: DSEC provides a separate exposure-side analysis: published exposure intervals bound the interval within which event timing is observed, while within-exposure event timing contains illumination-locked structure and therefore cannot be uniquely attributed to object timing without separating that structure.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 13. REVIEW — The same frame under both chunk positions
- Source: `submission_2027/paper/latex/supp.tex:881-890`
- Reasons: long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: Those frames are then scored twice: once with one to four windows of recurrent history, as the release scores them, and once with seventeen to twenty, under the same weights, the same ground truth and the same evaluator. labeled frames satisfy both, and the comparison is within model and within frame.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 14. REVIEW — The influence profile
- Source: `submission_2027/paper/latex/supp.tex:140-158`
- Reasons: long sentence / modifier load
- Exact sentence: A bin's influence is the magnitude of the change its ablation produces in the emitted detection tensor, relative to its norm, averaged over samples drawn from the first twelve lexicographically ordered released Gen1 validation sequences, using the first forty post-warm-up samples from each sequence.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 15. REVIEW — Instrumental-variable alternative.
- Source: `submission_2027/paper/latex/supp.tex:114-125`
- Reasons: long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: The third-difference kernel forces for white noise, the same code returns on white noise and on the DSEC-Det labels, and pooled-ratio bias, heteroscedastic segments and heavy tails each returned the white-noise value through the identical pooling code, so the departure is a property of the labels.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 16. REVIEW — Preamble
- Source: `submission_2027/paper/latex/main.tex:41-41`
- Reasons: absolute wording, long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: At the same evaluated timestamp, with frames, weights, labels and evaluator fixed, moving only the chunk boundary changes the recurrent history from one to twenty-one windows within the pooled score, and changes S5-B by mAP over all labeled boxes and by \, \, mAP on the velocity-evaluable subset.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 17. REVIEW — The same intervention on RVT, in two state regimes
- Source: `submission_2027/paper/latex/supp.tex:980-991`
- Reasons: absolute wording, long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: With no shift and the state carried, the grouping is inert by construction, and confirms it on the artifacts: every one of the RVT- and RVT- detections is bit-identical to the stored per-window dump, the ground truth matches, and the recorded positions equal the release placement frame for frame.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 18. REVIEW — The same intervention on RVT, in two state regimes
- Source: `submission_2027/paper/latex/supp.tex:980-991`
- Reasons: absolute wording, long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: Two regimes are then compared on the frames the shift carries from positions -- to -- , the same selection rule and the same estimand as Tab.~ : , the released behavior, and , with the recurrent state dropped at every chunk start, which places RVT in the condition the SSM release is already in
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 19. REVIEW — The finite difference used for the velocity.
- Source: `submission_2027/paper/latex/main.tex:531-543`
- Reasons: long sentence / modifier load, dense parenthetical insertion, comma-heavy sentence rhythm
- Exact sentence: Specification & (ms) & placebo (ms) \\ {l}{ }\\ forward difference & \, \, & \, \, \\ backward difference & \, \, & \, \, \\ centered difference & \, \, & \, \, \\ {l}{ }\\ box side along travel & \, \, & \, \, \\ four geometric terms & \, \, & \, \, \\ per-sequence bias & \, \, & \, \, \\
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 20. REVIEW — Effect on benchmark mAP.
- Source: `submission_2027/paper/latex/main.tex:633-659`
- Reasons: absolute wording, long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: Displacing the ground truth to the window's centroid costs absolute mAP ( percentage points, \,\ subset is nearly invariant over the measured label-to-centroid displacement, and at the common \,ms displacement the ordering of all released checkpoints is unchanged on the validation split.
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

