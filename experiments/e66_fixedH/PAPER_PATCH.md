# E66 PAPER_PATCH (draft only; paper/main.tex is NOT modified)

STATUS 2026-10-01: applied. The text is main.tex Sec. 5 (Support-conditioned AP) and supp.tex Sec. 13.4; every number there is an \fh... macro emitted by src/e66_macros.py from results.json, with the macro names listed in numbers.tex (E66 block) instead of the \e66... placeholders below.

All numbers below are placeholders written as \e66... macros. They are to be generated from
`experiments/e66_fixedH/results.json` (src/e66_eval.py) and added to numbers.tex through the
existing macro pipeline; nothing here is a measured value. Read tables.md first and keep only
the sentences the data support (the draft assumes nothing about whether the ranking changes).

## Where

1. Sec. "Effect on benchmark mAP" (after the chunk-position figure, paragraph beginning
   "Effect on benchmark mAP."): new paragraph "Support-conditioned AP" and one table
   (released-pooled and H = 1, 5, 10, 21 columns, five checkpoints, 95% sequence-cluster CI).
2. Intro, paragraph "Evaluation support.": one sentence pointing to the table.
3. Scope and limitations: the two scope sentences below.

## Draft text (Sec. effect on benchmark mAP)

\paragraph{Support-conditioned AP.}
The chunk-position contrast above compares frames that received different history inside one
release. To compare checkpoints under equal history we re-ran all five released Gen1
checkpoints with exactly $H\in\{1,5,10,21\}$ windows per labeled frame: the recurrent state is
started at the first of the $H$ windows and the detections of the last window are scored, so
no earlier window reaches the model. All checkpoints are scored on the same \e66NCommon{} frames
(those with at least 21 preceding windows; \e66NExcl{} frames are excluded), with the same
labels, confidence threshold and NMS as the released-protocol dumps. At $H=21$ the per-frame
call reproduces the released reset-at-boundary RVT detections at chunk position 20 (regression
gate, \e66GateFrames{} frames, detection-wise match). Table~\ref{tab:sc_ap} reports mAP per $H$
next to the released-pooled score on the same frames. [IF DATA SUPPORT: The S5 minus ConvLSTM
gap at matched width is \e66GapOne{} points at $H=1$ and \e66GapFull{} at $H=21$
(cluster-bootstrap 95\% intervals \e66GapOneCI{}, \e66GapFullCI{}); the released-pooled gap,
which mixes the two supports with release-specific weights, is \e66GapPooled{}.] [IF THE
ORDERING CHANGES: The full ordering at $H=1$ and at $H=21$ differs from the pooled ordering
(Kendall $\tau$ \e66TauOne{}, \e66TauFull{}); the ordering reproduces in \e66ReproOne{} and
\e66ReproFull{} of sequence-bootstrap draws.] [IF IT DOES NOT: The ordering of the five
checkpoints is the same at every $H$; the gaps between them vary with $H$ as listed.]

## Table skeleton (Table sc_ap)

| model | pooled | H=1 | H=5 | H=10 | H=21 |   (mAP x100, [95% CI], n = \e66NCommon frames, \e66NSeq sequences)

Caption: "mAP on the common frames under fixed recurrent history. Pooled: released protocol
(history depends on chunk position), restricted to the same frames. H: exactly H windows of
history, state reset before them. CI: 200 sequence-cluster bootstrap draws, the same draw for
every model and column."

## Scope sentences to add (limitations)

- "Fixed-H scoring removes all earlier windows from the model's input; it does not equal the
  training distribution of any checkpoint, so the numbers are conditional on this protocol."
- "Frames with fewer than 21 preceding windows (\e66NExcl{}) are excluded from the common set;
  their H_forced is stored in the dump."

## Claims this experiment cannot support (do not write)

- That any checkpoint is better "in general"; the experiment varies only history length at test time.
- That the pooled ranking is wrong, unless the corrected ordering differs beyond the bootstrap
  reproduction rate in tables.md.
- Anything about H > 21 (SSM chunk length is 21; RVT would accept more but E66 does not test it).
