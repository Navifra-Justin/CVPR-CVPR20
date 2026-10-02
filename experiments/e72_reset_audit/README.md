# E72 reset-policy audit of public recurrent event detectors

Question: which reset policy does each public repository declare, which one does it measurably have, and which history range lies inside its pooled score.

Method (src/e72_audit.py): run the repository's own streaming call from the first window of a Gen1 validation sequence with the state carried exactly as its evaluation carries it; at chunk starts c = 21, 42, 63 re-run the chunk with the entering state replaced by the initial state; report the relative L2 change of the raw output per position in the chunk (3 sequences x 3 chunk starts = 9 per model). Controls: (i) same chunk, same entering state -> 0 (instrument is deterministic); (ii) occluding the window one position earlier changes the output (the model is recurrent inside the chunk, so a zero in the state arm is not a model that ignores history).

Declared policy (from the code, file:line):
- RVT (uzh-rpg/RVT, vendored src/RVT): `modules/detection.py` 114-117 and 127/159: validation state is kept in `mode_2_rnn_states` and cleared only on `IS_FIRST_SAMPLE`; carried across chunks.
- SSM-ViT (vendored src/SSMViT): `modules/detection.py` 135-139, 150, 201: same mechanism, state declared carried across chunks.
- EvRT-DETR (realtime-intelligence/evrt-detr @5a2ffff): `evlearn/models/vcf_detection_evrtdetr.py` `_set_inputs`/`forward_video` and `evlearn/models/funcs.py:find_new_video_mask`: memory reset only when the video index changes, detached and carried across clips (eval clip length 21, config.json of the Zenodo model).
- SAST (Peterande/SAST @e4645cd) and SMamba (Zizzzzzzz/SMamba_AAAI2025 @0c3f1ed): `modules/detection.py` is the RVT mechanism (reset on `IS_FIRST_SAMPLE`, carried). NOT MEASURED here: no Gen1 SAST checkpoint is distributed (README links the repository itself for Gen1); the 1 Mpx SAST and the SMamba checkpoints were downloaded (ckpt/, not tracked) but SMamba needs a compiled CUDA selective-scan extension and SAST a 1 Mpx input path; both were left out for lack of an uncontended GPU. These two rows are code reading only.

Results: audit_table.md, audit-*.json. Checkpoints: RVT/S5-ViT as in data/ckpt; EvRT-DETR gen1_video_evrtdetr_presnet18 from https://zenodo.org/records/14548751 (md5 of the zip da1af156292d3ec47d04b2156f945864 for the first, partly resumed download; re-check before reuse). `audit-evrtdetr-r18-rawquery-v1.json` is an earlier run of the same model that only had the raw query-indexed metric (superseded: RT-DETR queries are not index-aligned between runs).
Run: `experiments/e72_reset_audit/run_all.sh` (CPU containers, nice 19; pip packages installed per container with --user, nothing on the host).
