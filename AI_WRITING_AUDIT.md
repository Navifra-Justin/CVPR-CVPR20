# AI Writing Audit (first pass)

This report is diagnostic only. No manuscript source was edited.

GPTZero status: **not_run** (GPTZERO_API_KEY is not set)
Claude status: **not configured**; no external Claude assessment is claimed unless an Anthropic review is run.

## Summary

- Extracted prose chunks: 136
- SAFE passages: 313 (unflagged; not a proof of human authorship)
- REVIEW passages: 122
- REWRITE passages: 0
- GPTZero confidence: unavailable because the API key is not configured.

## Classification policy

A GPTZero flag alone would not trigger a rewrite. In this keyless first pass, REVIEW/REWRITE labels are independent local writing-quality signals and require author review before any edit.

## Highest-priority passages

### 1. REVIEW — Recovering a time offset from image-plane displacement.
- Source: `paper/main.tex:156-181`
- Reasons: long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: Sensor latency, the illumination-dependent delay between a change and the timestamp the sensor assigns it, is measured at microseconds~ , and nighttime event imaging corrects an illumination-dependent trailing by learning a per-event timestamp calibration~ , both target the sensor, while here the released exposure metadata and event stream bound what a within-box temporal statistic computed inside one published exposure can be attributed to.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 2. REVIEW — The window and the instant it is indexed by
- Source: `paper/main.tex:289-308`
- Reasons: long sentence / modifier load
- Exact sentence: {0.95 } {The newest-window sensitivity centroid differs in point estimate from the regression-based temporal coefficient, while average precision on the velocity-evaluable subset is nearly invariant between the label instant and that centroid. (a) Occlusion influence of each of the bins of the released input window, over real Gen1 validation samples with the recurrent state warmed steps, with descriptive sample-level standard errors.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 3. REVIEW — Recovering a time offset from image-plane displacement.
- Source: `paper/main.tex:156-181`
- Reasons: long sentence / modifier load
- Exact sentence: Streaming perception~ folds wall-clock compute latency into average precision and re-anchors any detector from box coordinates alone, later work adapts to the measured runtime delay~ , a continuous-stream framework scores the latest available output against high-rate ground truth and reports reordered rankings~ , and temporal tolerance has been argued for time-series event detection~ .
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 4. REVIEW — The DSEC measurements
- Source: `paper/supplement.tex:372-384`
- Reasons: absolute wording, long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: {Every DSEC training sequence whose exposure is pinned at \, s, measured per labeled box over the events inside that box during that frame's own published exposure window, with at least events per box. is the median over boxes of the modulation depth at \,Hz. and are the median over boxes of the Rayleigh statistic at \,Hz and at the off-frequency control on the same events.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 5. REVIEW — Preamble
- Source: `paper/main.tex:33-57`
- Reasons: absolute wording, long sentence / modifier load
- Exact sentence: On the velocity-evaluable subset, average precision is nearly invariant between the label instant and the newest-window occlusion-sensitivity centroid: applying the corresponding center displacement changes mAP by only absolute mAP ( percentage points, \,\ relative to ) and reorders none of the checkpoints at the measured centroid displacement.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 6. REVIEW — Effect of Temporal Displacement on Checkpoint Ordering
- Source: `paper/supplement.tex:527-534`
- Reasons: absolute wording, long sentence / modifier load
- Exact sentence: Whether the interval changes a needs more than one detector, so all released checkpoints of main Sec.~3.3 were run over the Gen1 validation split under one protocol: the same frames, the same confidence threshold and non-maximum suppression, and ground truth that is identical across the five and identical to the dump main Sec.~3.5 already uses.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 7. REVIEW — Event benchmarks and their exposures.
- Source: `paper/main.tex:216-248`
- Reasons: long sentence / modifier load
- Exact sentence: That a frame's exposure is long relative to event timing has been stated: Event-based deblurring~ argues that accumulating events from a single frame timestamp loses information, deblurring work names auto-exposure as why the width is unknown~ , and RENet~ uses a DSEC exposure interval as its event window while describing it as short.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 8. REVIEW — Preamble
- Source: `paper/main.tex:33-57`
- Reasons: long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: For a released recurrent detector, the newest \,ms input window has an occlusion-sensitivity centroid \,ms before the label instant, while the regression-based temporal coefficient estimated on nominal-time-matched detections with centered label velocity is \,ms, statistically consistent with zero under the reported specification.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 9. REVIEW — The finite difference used for the velocity.
- Source: `paper/main.tex:419-437`
- Reasons: absolute wording, long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: On synthetic tracks whose detector has no lag whatever, with label centers corrupted at the dispersion the supplement's difference ladder measures on Gen1 ( \,px), the forward estimator returns \,ms and the backward one \,ms against a closed form of \,ms, they sum to \,ms, and removing the label noise returns all three to \,ms.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 10. REVIEW — Mains-Frequency Signature and Per-Pixel Phase Test
- Source: `paper/main.tex:687-702`
- Reasons: absolute wording, long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: Sweeping -- \,Hz on each whole recording, with no band fixed in advance and each frequency divided by the median of its own neighborhood, returns that series in every ceiling sequence: the ceiling median is at \,Hz, at \,Hz and at \,Hz, and the second harmonic is the strongest line in of the , never falling below .
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 11. REVIEW — The influence profile
- Source: `paper/supplement.tex:138-156`
- Reasons: long sentence / modifier load
- Exact sentence: A bin's influence is the magnitude of the change its occlusion produces in the emitted detection tensor, relative to its norm, averaged over samples drawn from the first twelve lexicographically ordered released Gen1 validation sequences, using the first forty post-warm-up samples from each sequence.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 12. REVIEW — Instrumental-Variable Alternative.
- Source: `paper/supplement.tex:112-123`
- Reasons: long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: The third-difference kernel forces for white noise, the same code returns on white noise and on the DSEC-Det labels, and pooled-ratio bias, heteroscedastic segments and heavy tails each returned the white-noise value through the identical pooling code, so the departure is a property of the labels.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 13. REVIEW — The finite difference used for the velocity.
- Source: `paper/main.tex:443-455`
- Reasons: long sentence / modifier load, dense parenthetical insertion, comma-heavy sentence rhythm
- Exact sentence: Specification & (ms) & placebo (ms) \\ {l}{ }\\ forward difference & \, \, & \, \, \\ backward difference & \, \, & \, \, \\ centered difference & \, \, & \, \, \\ {l}{ }\\ box side along travel & \, \, & \, \, \\ four geometric terms & \, \, & \, \, \\ per-sequence bias & \, \, & \, \, \\
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 14. REVIEW — Across the released checkpoints and a second architecture.
- Source: `paper/main.tex:352-369`
- Reasons: absolute wording, long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: On the same sequences, and driving each the way its own release drives it, all checkpoints put the newest window's occlusion-sensitivity centroid between and \,ms, none further than \,ms, or \,\ The state the SSM release carries between evaluation chunks reaches none of its outputs.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 15. REVIEW — Introduction
- Source: `paper/main.tex:73-87`
- Reasons: long sentence / modifier load
- Exact sentence: The event branch of the detector examined here~ consumes a window of \,ms divided into bins, and the preprocessing script of its own repository builds the window boundaries by counting backwards from label timestamps, so each window ends at the label it is scored against (Sec.~ ).
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 16. REVIEW — The window and the instant it is indexed by
- Source: `paper/main.tex:289-308`
- Reasons: long sentence / modifier load, comma-heavy sentence rhythm
- Exact sentence: Gray lines show the four other checkpoints, each rescaled to its own mean. (b) Average precision against the temporal center displacement applied to the ground truth boxes, by object speed in px/s, each curve relative to its own value at the label instant, with its maximum marked.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 17. REVIEW — Introduction
- Source: `paper/main.tex:116-132`
- Reasons: absolute wording
- Exact sentence: DSEC provides a complementary exposure-side attribution case study: a harmonic series at \,Hz in ceiling-exposure sequences shows that a within-box temporal statistic measured inside one published exposure window cannot, by itself, be attributed to object timing (Secs.~ -- )
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 18. REVIEW — Data path.
- Source: `paper/supplement.tex:387-402`
- Reasons: long sentence / modifier load
- Exact sentence: For the dispersion of main Sec.~4.4 a box contributes only if it carries at least events in the window, and a frame only if at least boxes qualify, the reported statistics are medians over frames of a within-frame quantity, so no frame is weighted by its object count.
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 19. REVIEW — The carried state of the SSM release
- Source: `paper/supplement.tex:516-523`
- Reasons: long sentence / modifier load
- Exact sentence: A model that ignored its history altogether would return zero to both arms, so the control occludes the window one position earlier inside the same chunk: SSM-ViT answers there, falling to , so it is recurrent within a chunk and only across chunks is the state lost
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

### 20. REVIEW — Effect of Temporal Displacement on Checkpoint Ordering
- Source: `paper/supplement.tex:565-572`
- Reasons: absolute wording, long sentence / modifier load
- Exact sentence: This is reported as a property of the release that its documentation does not state, which is the same class of undeclared quantity the rest of this paper measures, and not as a claim about what the architecture could support if the state were carried
- GPTZero signal: unavailable in this run
- Claude independent assessment: unavailable; local assessment requires human confirmation

## Repository residue scan

- `Here's` in `paper/cvpr.sty`
- `placeholder` in `paper/numbers.tex`
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

