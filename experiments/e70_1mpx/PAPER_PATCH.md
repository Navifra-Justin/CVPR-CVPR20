# E70 PAPER_PATCH (draft only; no .tex file is modified)

STATUS 2026-10-02: the 1 Mpx experiment is PIPELINE-READY BUT NOT YET MEASURED. Every `[PENDING ...]` below is a
placeholder for a number that does not exist yet. No 1 Mpx mAP, delta or CI has been produced; none may be
written into the paper until `experiments/e70_1mpx/paired-shift2.json` exists and the gate in section 5 passes.
The live paper is `submission_2027/paper/latex/{main,supp,numbers}.tex` (main 7 pp, body 6, refs on 7). The older
`paper/` tree is a stale pre-restructure copy (its section numbering differs); do not patch it.

## 1. What the experiment is (design identical to E60 / E65, ported to 1 Mpx)

- Data: official preprocessed `gen4.tar`, **val split only**: 128 sequences, 26.96 GB, fetched by HTTP range from
  `download.ifi.uzh.ch/rpg/RVT/datasets/preprocessed/gen4.tar` (the server answers byte ranges). Representation
  `event_representations_ds2_nearest.h5` (T,20,360,640 uint8), labels at 720x1280 scaled by 0.5 (LSCALE=0.5, checked:
  x max 1272), classes 0,1,2, labels on every second window (`objframe_idx_2_repr_idx` steps by 2).
- Checkpoints (all strict-load, 0 missing / 0 unexpected, partition (6,10) on 384x640): RVT 1 Mpx t/s/b (md5 prefixes
  5a3c78 / a94207 / 72923a equal the RVT README), S5-ViT gen4 small/base (`download.ifi.uzh.ch/rpg/CVPR24_Zubic/gen4_{small,base}.ckpt`).
- Boundary move: S5-ViT 1 Mpx evaluates in chunks of `sequence_length = 10` (src/SSMViT/config/dataset/gen4.yaml; Gen1 is 21).
  SHIFT=2 moves every boundary 2 windows later, so labelled frames at chunk positions 0-1 (1-2 windows of history) are
  re-scored at positions 8-9 (9-10 windows). This is the chunk-10 analogue of Gen1 SHIFT=5 (positions 0-3 -> 16-19).
  SHIFT=5 (positions 0-1 -> 5-6) is a second dose. Same frames, weights, labels, evaluator (src/e56_eval.Scorer, all labelled
  boxes and velocity-evaluable subset), sequence-cluster bootstrap B=300.
- Controls on RVT-s (E65 design on the same grid): `carry` (released behaviour; expected boundary-insensitive by the
  source-code argument, to be measured) and `reset` (state dropped at every chunk start; positive control).
- Code: `src/e70_1mpx_dump.py` (copy of the COMMITTED `src/e51_dump_all.py`; the working-tree edit by someone else is not included),
  `src/e70_1mpx_paired.py`, `src/e70_1mpx_gate.py`, `src/e70_1mpx_parity.py`, `src/e70_1mpx_verify_data.py`,
  `run_e70.sh`, `run_e70_arm.sh`. No original file was touched.

## 2. Draft text (usable only in the branch the data select)

Location A, main.tex Sec. 3 ("Primary evidence"), new paragraph after "The control, measured rather than assumed":

    \paragraph{The same boundary move on 1\,Mpx.}
    The released 1\,Mpx S5-ViT checkpoints are evaluated in chunks of 10 windows. Moving every chunk boundary
    \onemShift{} windows later re-scores \onemN{} labeled boxes, first with one to two windows of recurrent history
    and then with \onemGainLo--\onemGainHi{}, with the same frames, weights, labels and evaluator. [BRANCH P:]
    The paired change is \onemBaseAll$\pm$\onemBaseAllSE{} mAP points over all labeled boxes for S5-B and
    \onemSmallAll$\pm$\onemSmallAllSE{} for S5-S (\onemBaseVel$\pm$\onemBaseVelSE{} and \onemSmallVel$\pm$\onemSmallVelSE{}
    on the velocity-evaluable subset). With the released state carried across the boundary, RVT-\texttt{s} changes by
    \onemRvtCarry$\pm$\onemRvtCarrySE{}, and with the state dropped at each boundary by
    \onemRvtReset$\pm$\onemRvtResetSE{}. The boundary move therefore changes the reported score on a second dataset, a
    second sensor resolution and a second pair of released checkpoints, so the under-specification is a property of the
    streaming protocol and not of Gen1. [END BRANCH P]

Branch rules (decide from the JSON, not from this draft):
- P (use the paragraph above): S5-B and S5-S 95 % bootstrap CIs exclude 0 in the same direction as Gen1, AND the RVT-carry
  CI contains 0, AND RVT-reset CI excludes 0. Then "property of the streaming protocol" is supported for this checkpoint
  family on this split. Wording stays "for the released S5-ViT 1 Mpx checkpoints on the validation split".
- Q (partial): S5 effect present but RVT-carry CI also excludes 0 -> drop the sentence about the control and the "protocol, not
  Gen1" clause; report the numbers as a replication of the sign only.
- N (null or reversed): report as stated, in Scope and limitations ("the same move on 1 Mpx changes S5-B by X [CI]; the
  Gen1 magnitude is not reproduced"), and do NOT write the user's target sentence.
- The sentence "so the under-specification is a property of the streaming protocol and not of Gen1" is a generalization
  from two datasets and one architecture family. In branch P the safe form is "is not specific to Gen1".

Location B, supp.tex, new subsection after 13.4 "Scoring at a fixed history": table of SHIFT 0 / 2 / 5 arms (n target frames, mAP
before, after, delta, CI) for S5-B, S5-S, RVT-s carry, RVT-s reset; the parity table (section 4 below); the data and
checkpoint provenance of section 1; chunk length 10, labels every second window, SHIFT definition.
Location C, Scope and limitations: "The 1 Mpx replication uses the validation split (128 sequences), released checkpoints
only, chunk length 10 and labels on every second window; box-size filtering of the official evaluator is not applied."
Location D, Conclusion: add the 1 Mpx number only in branch P, one clause.

## 3. Numbers already in the paper that this patch must stay consistent with (checked against every file that produces them)

| quantity | file | value | script | split / seed | matches paper setting? |
|---|---|---|---|---|---|
| S5-B paired gain, SHIFT 5, all boxes | submission_2027/paper/latex/numbers.tex (`ssmPairedMapAllBase`) | 4.20 | audit_numbers.py | Gen1 val | paper value |
| same | experiments/e60_shift/paired-shift5.json | 4.195 (se 0.358) | src/e60_paired.py, B=300 | Gen1 val, 406 seq, n=3574 | YES (rounds to 4.20) |
| same | experiments/e60_shift/paired.json | 4.195 | src/e60_paired.py | same | duplicate of the above; differs only in key names (`full` vs `gain`, block 21 vs 17-19) |
| S5-B paired gain, SHIFT 5, velocity subset | numbers.tex `ssmPairedMapVelBase`/`SE` | 5.23 / 0.49 | | Gen1 val | paper value |
| same | paired-shift5.json | 5.230 (se 0.487) | e60_paired.py | same | YES |
| S5-S, SHIFT 5, vel / all | numbers.tex ; paired-shift5.json | 4.81 ; 4.814 (se 0.518), all 4.099 | | same | YES |
| **"+4.20" appears for a different quantity** | experiments/e66_fixedH/tables.md, row rvt-s minus s5vit-small, pooled | +4.20 [+3.35, +4.88] | src/e66_eval.py | Gen1 val common frames | NOT the boundary-move gain; coincidental equality, keep the two apart in prose |
| RVT-s carry / reset, SHIFT 5, vel | numbers.tex ; experiments/e65_rvt_boundary/paired-shift5.json | -0.01, 5.39 ; -0.010, 5.391 (all: 0.066, 4.836) | src/e65_paired.py | Gen1 val, n=3574 | YES |
| RVT-b carry / reset, vel | same | 0.05, 6.91 ; 0.052, 6.914 | | | YES |

No 1 Mpx number is listed because none exists yet; when it does, it must be entered here with its JSON path, script, B, seed and split.

## 4. Port parity on 1 Mpx (to be filled by src/e70_1mpx_parity.py; published numbers are TEST split, ours is VAL)

Published 1 Mpx test mAP read from the papers: RVT-B 47.4, RVT-S 44.1, RVT-T 41.5 (arXiv:2212.05598 Table 6); S5-ViT-B 47.8, S5-ViT-S 46.5
(arXiv:2402.15584 results table, 1 Mpx column). Our evaluator does not apply the official 0.5 s skip and (in the primary column)
no box-size filter, so a level difference is expected; compare ordering and the filtered column. Not measured yet: [PENDING parity.log].
Caution carried from Gen1: E63 found this port 5 to 11 mAP below the published Gen1 level (rvt-t 38.9 vs 44.1, s5vit-small 35.7 vs 46.6, val vs test).
The same gap on 1 Mpx would be a port question, not a boundary-effect question, and would be reported as such.

## 5. Gate (structural only; never on the sign or size of the effect)

`src/e70_1mpx_gate.py` on a 6-sequence subset: identical GT across arms, target frames rotate by exactly SHIFT mod 10, positions in range,
detections present for >=95 % of frames, boxes inside the canvas, all-box mAP > 10 (a broken port gives about 0). `run_e70.sh` refuses to
start the production dumps unless `experiments/e70_1mpx/gate/PASS` exists. Status: [PENDING; gate dumps are waiting in the gpu0 queue].

## 6. Which supplement analysis to promote to the main text (existing results only, no new computation)

Candidates in the LIVE supplement: (A) "RVT input sensitivity" = supp Sec. 2 "The influence profile" (`sup:influence`) plus Sec. 15.3
"The measured influence profile" and Fig. `fig:predictor` (figs/fig_predictor.pdf, 251x207 pt); (B) "DSEC exposure" = supp Sec. 8
"The DSEC measurements" (supp Sec. 8; Table `tab:sixseq`, Figs. `fig:qualitative`, `fig:daynight`) plus Sec. 16 with Figs. `fig:exposure`
(figs/fig1_dsec_exposure.pdf, 511x145 pt, full width) and `fig:flickerreal` (figs/fig7_ceiling_vs_day.pdf, 239x168 pt).
Main Sec. 4 currently carries both only as one dense paragraph each, with no figure or table.

**Recommendation: promote (A), the RVT input sensitivity, as one figure (fig_predictor, both panels) and a four-row instrument table.**
Reasons, each tied to an existing result:
1. It is the part of the audits that shares models and dataset with the primary evidence (RVT checkpoints, Gen1), so the main text stays on one
   subject; (B) brings in a second dataset and an RGB-event label-annotation question (DSEC-Det labels may be tracker output; supp Sec. 8 says the
   second-difference test cannot tell) that the main argument does not need.
2. It contains the number most open to attack, the newest-window centroid -23.81 ms, and the supplement already holds its defense: four instruments
   (zero -23.81, dataset-mean -26.35, cross-sample swap -25.01, gradient -22.35; spread 4.01 ms; experiments/e45_influence_fixed/result.json and
   seqboot.json) and the 12-sequence bootstrap (zero-fill 95 % CI [-24.07, -23.56], se 0.13, widest CI over instruments 0.51 ms, leave-one-out
   at most 0.08 ms, per-sequence range -24.63 to -23.20). The binding uncertainty is the instrument (4.01 ms), not sampling; a main-text table shows that.
3. Fig. `fig:predictor` shows in one panel pair the paper's distinct-descriptor claim: centroid vs regression coefficient 26.2 ms apart (tau = -2.40 +- 7.18 ms),
   and AP nearly invariant over the displacement (panel b), which main Sec. 4 states only in words ("an effect at the benchmark's sampling-resolution floor").
4. Cost: about 0.3 page for the figure plus 0.15 page for the table, inside the +2 pages available (main 6 body pages + references on p. 7, limit 9 as stated).
Honest weaknesses of (A) to state in the same paragraph: single checkpoint for the instrument comparison (rvt-t), 12 validation sequences, ablation
sensitivity is an operational descriptor and not a decomposition of temporal weights (supp Sec. 2 says so). The five-checkpoint range (-24.72 to -23.76 ms,
E48) is already in main and supports generality.
Why not (B): its strongest evidence is one frame (qualitative figure) and a six-sequence descriptive table whose caption itself states that the
nominal Exp(1) null does not describe the statistics and that the 137-Hz control is descriptive; the claim that carries the argument (100-Hz line and
harmonics, daytime control) is already summarized in one sentence. Promoting it would put the weaker-evidence half of the audits in the main text.
If the authors prefer a label-side figure instead, `fig7_ceiling_vs_day` (0.66 column) is the smallest self-contained one.

Number provenance for section 6 (all verified against files, not only numbers.tex):
| quantity | file | value | script | note |
|---|---|---|---|---|
| zero-fill centroid | experiments/e45_influence_fixed/result.json ; numbers.tex `occZero`, `rvtCentroidMeas` | -23.8105 ; -23.81 | src/e45_influence_fixed.py | 480 samples, 12 seq, Gen1 val: paper setting |
| same | experiments/e48_matched_frames/rvt-t.json | -23.8105 | src/e48_rvt_bins.py | matched frames; identical to 4 decimals |
| same | experiments/e44_capacity/rvt-t.json | -23.8436 | src/e44_capacity_support.py | 576 samples, same 12 seq, different sampling; used for capacity columns only |
| same | experiments/e17_bin_influence/result.json | -24.9438 | src/e17_bin_influence.py | SUPERSEDED (state handed over was the returned one, case 9); do not cite |
| mean / swap / gradient | e45 result.json ; numbers.tex | -26.354 / -25.007 / -22.346 ; -26.35 / -25.01 / -22.35 | | match |
| spread across instruments | -22.346 - (-26.354) = 4.008 ; numbers.tex `occSpread` | 4.01 | | match |
| sequence-bootstrap CI (zero) | e45 seqboot.json ; numbers.tex | [-24.069, -23.556], se 0.132 ; [-24.07, -23.56], 0.13 | | match |
| regression coefficient | numbers.tex `ladderFullTau` | -2.40 +- 7.18 | E27 family | not re-derived here |

## 7. Claims this experiment cannot support (do not write)

- That the boundary effect is "universal" or independent of architecture: two S5-ViT checkpoints and one RVT size on one split.
- Anything about the test split, other 1 Mpx checkpoints, or training-time behavior.
- A level comparison with published 1 Mpx mAP (val vs test, no official 0.5 s skip).
- Any effect size before `paired-shift2.json` exists.
