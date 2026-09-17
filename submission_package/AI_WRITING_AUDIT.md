# AI Writing Audit (first pass)

This report is diagnostic only. No manuscript source was edited.

GPTZero status: **not_run** (GPTZERO_API_KEY is not set)
Claude status: **not configured**; no external Claude assessment is claimed unless an Anthropic review is run.

## Summary

- Extracted prose chunks: 178
- SAFE passages: 395 (unflagged; not a proof of human authorship)
- REVIEW passages: 178
- REWRITE passages: 0
- GPTZero confidence: unavailable because the API key is not configured.

## Classification policy

A GPTZero flag alone would not trigger a rewrite. In this keyless first pass, REVIEW/REWRITE labels are independent local writing-quality signals and require author review before any edit.

## Highest-priority passages

### 1. REVIEW — The window and the instant it is indexed by
- Source: `paper/main.tex:296-314`
- Reasons: long sentence / modifier load
- Exact sentence: {0.95 } {The newest-window sensitivity centroid differs in point estimate from the regression-based temporal coefficient, while average precision on the velocity-evaluable subset is nearly invariant between the label instant and that centroid. (a) Window-ablation influence of each of the bins of the released input window, over Gen1 validation samples with the recurrent state warmed steps, with sample-level standard errors.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 2. REVIEW — Preamble
- Source: `paper/main.tex:33-54`
- Reasons: absolute wording, long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: Displacing ground-truth centers by that interval changes mAP by points and reorders no checkpoint, and over every labeled box a sequence bootstrap reproduces the published ordering in only \,\ SSM-ViT's released streaming evaluation, in which a detection's recurrent history is one to four windows at one chunk position and to at another, the contrast between the two is mAP points after an RVT control.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 3. REVIEW — Association independent of nominal-time overlap.
- Source: `paper/supplement.tex:301-316`
- Reasons: absolute wording, long sentence / modifier load
- Exact sentence: The informative direction is to open the gate or to remove it. rebuilds the rows from the raw detection dump under association rules and refits the reported specification under each: greedy and Hungarian assignment at overlap floors from 0.05 to 0.50, and a rule that never tests overlap at all, admitting a detection whose center falls within a fixed multiple of the label's box scale.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 4. REVIEW — The DSEC measurements
- Source: `paper/supplement.tex:448-460`
- Reasons: absolute wording, long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: {Every DSEC training sequence whose exposure is pinned at \, s, measured per labeled box over the events inside that box during that frame's own published exposure window, with at least events per box. is the median over boxes of the modulation depth at \,Hz. and are the median over boxes of the Rayleigh statistic at \,Hz and at the off-frequency control on the same events.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 5. REVIEW — Effect of temporal displacement on checkpoint ordering
- Source: `paper/supplement.tex:603-610`
- Reasons: absolute wording, long sentence / modifier load
- Exact sentence: Whether the interval changes a needs more than one detector, so all released checkpoints of main Sec.~3.3 were run over the Gen1 validation split under one protocol: the same frames, the same confidence threshold and non-maximum suppression, and ground truth that is identical across the five and identical to the dump main Sec.~3.5 already uses.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 6. REVIEW — Event benchmarks and their exposures.
- Source: `paper/main.tex:223-255`
- Reasons: long sentence / modifier load
- Exact sentence: That a frame's exposure is long relative to event timing has been stated: Event-based deblurring~ argues that accumulating events from a single frame timestamp loses information, deblurring work names auto-exposure as why the width is unknown~ , and RENet~ uses a DSEC exposure interval as its event window while describing it as short.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 7. REVIEW — Introduction
- Source: `paper/main.tex:120-125`
- Reasons: long sentence / modifier load
- Exact sentence: DSEC's published exposure intervals vary in width by a factor of against a fixed frame period, and in the ceiling-exposure sequences a within-box temporal statistic measured inside one published exposure window carries the \,Hz illumination harmonic, so attributing it to object timing requires separating that structure first (Sec.~ )
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 8. REVIEW — What timing difference the metric resolves
- Source: `paper/supplement.tex:690-698`
- Reasons: absolute wording, long sentence / modifier load
- Exact sentence: Its tightest adjacent pair is separated by points against a paired standard error of and exchanges places in a fraction of replicates. ``The correction changes no ranking'' and ``the benchmark does not resolve this ranking'' are consistent with the same evidence, and the measured noise floor separates them in favor of the second
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 9. REVIEW — The finite difference used for the velocity.
- Source: `paper/main.tex:454-472`
- Reasons: absolute wording, long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: On synthetic tracks whose detector has no lag whatever, with label centers corrupted at the dispersion the supplement's difference ladder measures on Gen1 ( \,px), the forward estimator returns \,ms and the backward one \,ms against a closed form of \,ms, they sum to \,ms, and removing the label noise returns all three to \,ms.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 10. REVIEW — Mains-frequency signature and the per-pixel phase test
- Source: `paper/main.tex:726-741`
- Reasons: absolute wording, long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: Sweeping -- \,Hz on each whole recording, with no band fixed in advance and each frequency divided by the median of its own neighborhood, returns that series in every ceiling sequence: the ceiling median is at \,Hz, at \,Hz and at \,Hz, and the second harmonic is the strongest line in of the , never falling below .
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 11. REVIEW — Recurrent history under the released streaming evaluation.
- Source: `paper/main.tex:379-404`
- Reasons: long sentence / modifier load, dense parenthetical insertion
- Exact sentence: Differencing against the three RVT checkpoints, evaluated on the same frames with a state that crosses chunk boundaries, controls for frame-position effects shared with the RVT checkpoints and leaves points for S5-B ( ) and for S5-S ( ), against placebo differences among the RVT checkpoints of at most points ( ).
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 12. REVIEW — Introduction
- Source: `paper/main.tex:107-118`
- Reasons: long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: Its regression-based output coefficient, estimated on nominal-time-matched detections under Eq.~2 with a vector regression, a placebo term and a sign-flip control on the velocity estimator, is consistent with the label instant and sits \,ms from the newest-window centroid under the reported specification.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 13. REVIEW — The influence profile
- Source: `paper/supplement.tex:138-156`
- Reasons: long sentence / modifier load
- Exact sentence: A bin's influence is the magnitude of the change its ablation produces in the emitted detection tensor, relative to its norm, averaged over samples drawn from the first twelve lexicographically ordered released Gen1 validation sequences, using the first forty post-warm-up samples from each sequence.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 14. REVIEW — Instrumental-variable alternative.
- Source: `paper/supplement.tex:112-123`
- Reasons: long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: The third-difference kernel forces for white noise, the same code returns on white noise and on the DSEC-Det labels, and pooled-ratio bias, heteroscedastic segments and heavy tails each returned the white-noise value through the identical pooling code, so the departure is a property of the labels.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 15. REVIEW — The finite difference used for the velocity.
- Source: `paper/main.tex:478-490`
- Reasons: long sentence / modifier load, dense parenthetical insertion, comma-heavy sentence rhythm
- Exact sentence: Specification & (ms) & placebo (ms) \\ {l}{ }\\ forward difference & \, \, & \, \, \\ backward difference & \, \, & \, \, \\ centered difference & \, \, & \, \, \\ {l}{ }\\ box side along travel & \, \, & \, \, \\ four geometric terms & \, \, & \, \, \\ per-sequence bias & \, \, & \, \, \\
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 16. REVIEW — What is not shown here.
- Source: `paper/supplement.tex:362-369`
- Reasons: long sentence / modifier load
- Exact sentence: The release distribution available to this work carries the validation split alone, sequences with no test directory, so the levels above are validation-split levels and the published numbers are used only for the parameter comparison and for the ordering within RVT, which is preserved.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 17. REVIEW — Introduction
- Source: `paper/main.tex:70-83`
- Reasons: long sentence / modifier load
- Exact sentence: The event branch of the detector examined here~ consumes a window of \,ms divided into bins, and the preprocessing script of its own repository builds the window boundaries by counting backwards from label timestamps, so each window ends at the label it is scored against (Sec.~ ).
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 18. REVIEW — The window and the instant it is indexed by
- Source: `paper/main.tex:296-314`
- Reasons: long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: Gray: the four other checkpoints, each rescaled to its own mean. (b) Average precision against the temporal center displacement applied to the ground-truth boxes, by object speed in px/s, each curve relative to its own value at the label instant, with its maximum marked.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 19. REVIEW — Data path.
- Source: `paper/supplement.tex:463-478`
- Reasons: long sentence / modifier load
- Exact sentence: For the dispersion of main Sec.~4.4 a box contributes only if it carries at least events in the window, and a frame only if at least boxes qualify, the reported statistics are medians over frames of a within-frame quantity, so no frame is weighted by its object count.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 20. REVIEW — Effect on benchmark mAP.
- Source: `paper/main.tex:612-636`
- Reasons: absolute wording, comma-heavy sentence rhythm
- Exact sentence: Displacing the ground truth to the window's centroid costs absolute mAP ( percentage points, \,\ subset is nearly invariant over the measured label-to-centroid displacement, and at the common \,ms displacement the ordering of all released checkpoints is unchanged.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

## Residue scan

### Manuscript sources (`paper/*.tex`, the files that ship)

- `placeholder` in `paper/numbers.tex`

### Other scanned directories (`src/`, `docs/`; tooling and internal notes, not submitted)

- `Here's` in `paper/cvpr.sty`
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

