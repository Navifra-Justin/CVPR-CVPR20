# PAPER_PATCH_e71_e72 (draft only; no .tex file and nothing under submission_2027/ is modified)

STATUS 2026-10-02 22:10 KST. Part B (reset-policy audit, E72) is measured. Part A (H = 40, 80 on 3,000 stratified frames, E71) is
PIPELINE-READY AND QUEUED: no H = 40/80 number exists yet; every `[PENDING]` below is a placeholder, not a value.

User rules quoted from the task:
- "Adoption: a third repository with a different measured reset policy -> a column in Table 5."
- "If RVT-b overtakes S5-B at H >= 40, report the crossing H (do not drop long H); say if wording 'S5-B first at every H in {1,5,10,21}' would need the crossing statement."

## Part B. Reset-policy audit (E72), measured

Source files: `experiments/e72_reset_audit/audit-*.json`, table in `experiments/e72_reset_audit/audit_table.md`, code `src/e72_audit.py`, `src/e72_table.py`.
Instrument: relative L2 change of the raw output per position in a 21-window chunk when the state entering the chunk is zeroed, 9 chunk starts per
model (3 validation sequences x chunk starts 21, 42, 63), same-state control = 0.0 for every model, occlusion of the previous window as the within-chunk control.

| repository | declared reset policy | measured policy | history range inside the pooled score |
|---|---|---|---|
| RVT (uzh-rpg/RVT; t, s, b) | state cleared at sequence start only, carried across evaluation chunks (`modules/detection.py` 114-117) | carried: rel. change 0.084-0.093 at chunk position 0, 0.031-0.034 at 10, 0.024-0.026 at 20 | 2 to 1200 windows (median 602) |
| SSM-ViT (S5-ViT small, base) | same mechanism, state declared carried across chunks (`modules/detection.py` 135-139) | state entering a chunk has no effect: rel. change 0.0000 at every position (both checkpoints); occluding the previous window changes the output by 0.009-0.030 | 1 to 21 windows (chunk position) |
| EvRT-DETR (realtime-intelligence/evrt-detr, Gen1 presnet18) | memory cleared only when the video changes, carried across 21-frame clips | carried: confident detections without a partner after zeroing 0.435 at position 0, 0.153 at 10, 0.104 at 20; sorted-confidence change 0.227 / 0.115 / 0.089 | 2 to 1200 windows (same frames; from the E66 dump, not from running that repository's evaluator) |
| SAST, SMamba | RVT mechanism (reset on first sample, carried) by code reading | NOT MEASURED (no Gen1 SAST checkpoint distributed; SMamba needs a compiled CUDA scan) | not computed |

Adoption-rule verdict: the third repository that could be measured (EvRT-DETR) has the SAME measured policy as RVT (carried across the chunk boundary,
effect decaying with position). The rule asks for a different measured policy, so it is NOT met and no column is added to Table 5. The audit instead
shows two measured classes among the three measured repositories (carried: RVT, EvRT-DETR; inert: SSM-ViT), and that for SSM-ViT the declared policy
(carried) and the measured policy (inert) differ. Not tested: SAST and SMamba (code reading says carried, i.e. the RVT class). A repository with a third
measured class has not been found; this is a search result, not proof that none exists.

Draft text (supplement, after the reset-policy paragraph):

    To check that the reset policy in Tab.~\ref{tab:fields} is a property of the released code and not of one family, we zeroed the state entering a
    21-window chunk and measured the relative change of the raw output at each position of the chunk (9 chunk starts per checkpoint). For the three RVT
    checkpoints the change is 0.084--0.093 at the first position and falls to 0.024--0.026 at the last; EvRT-DETR (Gen1, PResNet-18 variant) behaves the
    same way, with 43.5\,\% of its confident detections unmatched after zeroing at the first position and 10.4\,\% at the last. For both S5-ViT checkpoints
    the change is zero at every position, although the release declares the state carried. The repositories therefore fall into two measured classes.

(Numbers copied from audit_table.md; check them against the file before use. The EvRT-DETR raw tensor change, 0.63-0.65, is not used because RT-DETR
queries are top-k selected and are not index-aligned between runs.)

## Part A. H = 40, 80 on 3,000 frames (E71), PENDING

Design (frozen before any number): 3,000 frames, proportional to eligible frames per sequence, at least 1 per sequence, only frames with r+1 >= 80
(18,947 eligible frames in 405 of 406 sequences; the 406th has none), seed 20261002: `experiments/e71_h4080/frames.npz|json`, `src/e71_select.py`.
H = 1, 5, 10, 21 and the pooled column are taken from the existing E66 per-frame dumps on the same frames (the same per-frame computation); H = 21 is
recomputed by `src/e71_dump.py` as a regression check (`src/e71_check.py`) and H = 40, 80 are new. Access log and oldest-window probe are applied at 40 and 80
(`src/e66_verify.py`, PROBE=2). Step 0 reproduction of known numbers with the evaluator path: `src/e71_selfcheck.py` gives rvt-s H21 37.02, H1 28.7227,
s5vit-base H21 39.9954, H1 33.685, equal to experiments/e66_fixedH/results.json to the printed digits.
Evaluation: `src/e71_eval.py` -> `experiments/e71_h4080/results.json|tables.md`, including the RVT-b minus S5-B gap per H with a sequence-cluster bootstrap interval and the first sign change.

Verdict on 'S5-B first at every H in {1,5,10,21}': [PENDING until results.json exists]. The wording is about H <= 21 on the 19,946 common frames and
stays literally true whatever H = 40, 80 give; if RVT-b overtakes S5-B at H >= 40 the paper needs one added statement giving the crossing H (the first sign
change of the RVT-b minus S5-B gap in results.json) and noting that SSM-ViT checkpoints were trained on chunks of 21 windows or less (check the training config before writing that).
