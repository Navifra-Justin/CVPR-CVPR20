# PREREG E72 follow-up (written 2026-10-04, before any SAST or SMamba output exists)

Context. Adoption rule (user): a third repository with a different measured reset policy gets a column in Tab. 5.
E72 measured six checkpoints in three repositories: RVT (3 checkpoints) and EvRT-DETR (1) carry the state across the chunk boundary
(output changes after zeroing the entering state, effect decays with position); SSM-ViT (2) shows an inert entering state
(change 0.000 at every position). The rule is NOT met by the measured set (EvRT-DETR has the RVT policy). Tab. 5 keeps its columns.

Not measured, code reading only: SAST (Peterande/SAST @e4645cd) and SMamba (Zizzzzzzz/SMamba_AAAI2025 @0c3f1ed).
Both `modules/detection.py` files reset the state on IS_FIRST_SAMPLE and carry it otherwise, and SMamba's temporal recurrence is a `DWSConvLSTM2d` per stage
(`models/detection/recurrent_backbone/SMamba.py` lines 9, 334; forward(x, prev_states) returns the LSTM states).

Prediction (fixed now): both measure as carried (RVT class). Decision rule: the same instrument as E72 (src/e72_audit.py: 21-window chunk,
chunk starts 21/42/63, three validation sequences, control with identical entering state must be 0). Measured policy "different" means
max over positions of the relative change after zeroing is below 1e-6 (inert), or the effect does not decay with position while the
occlusion control does. If either checkpoint is different: add a column to Tab. 5 for it with its measured policy and report the
RVT-class result of the other. If both are carried: no column; one sentence in the supplement lists them as measured RVT class.
No tuning, no selection among checkpoints (all three smamba_c1..c3 are run, all reported).

What blocks it today. No Gen1 SAST checkpoint is distributed (the README links the repository itself for Gen1; the 1 Mpx SAST needs
the 1 Mpx input path). SMamba needs `selective_scan_cuda_oflex`; a CPU port of the scan (models/kernels/selective_scan/test_selective_scan_easy.py
has a reference scan) must first be shown to reproduce a CUDA forward on one window before any audit number is read from it.
Status 2026-10-04: not run. The paper therefore states the audit as covering three measured repositories and two unmeasured ones.
