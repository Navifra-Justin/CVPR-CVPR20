# E72 reset-policy audit (relative L2 change of the output when the state entering a 21-window chunk is zeroed)

Per model: mean over chunk starts (sequences x chunks listed), positions p = 0 / 10 / 20 inside the chunk. Control = same chunk re-run with the identical entering state (max relative difference over all positions and chunks; must be 0).

| model | repository (commit) | chunk starts | rel. change p=0 / 10 / 20 | control | occluding the previous window (p=1 / 10 / 20) | measured policy |
|---|---|--:|---|--:|---|---|
| evrtdetr-r18 | realtime-intelligence/evrt-detr 5a2ffff | 9 | 0.6475 / 0.6319 / 0.6427 | 0.0e+00 | 0.6410 / 0.6388 / 0.6488 | state entering a chunk reaches the output at every position; effect decays with position (carried across the chunk boundary) |
| rvt-b | uzh-rpg/RVT (vendored src/RVT) | 9 | 0.0839 / 0.0308 / 0.0242 | 0.0e+00 | 0.0148 / 0.0148 / 0.0154 | state entering a chunk reaches the output at every position; effect decays with position (carried across the chunk boundary) |
| rvt-s | uzh-rpg/RVT (vendored src/RVT) | 9 | 0.0931 / 0.0326 / 0.0239 | 0.0e+00 | 0.0122 / 0.0120 / 0.0127 | state entering a chunk reaches the output at every position; effect decays with position (carried across the chunk boundary) |
| rvt-t | uzh-rpg/RVT (vendored src/RVT) | 9 | 0.0880 / 0.0344 / 0.0256 | 0.0e+00 | 0.0122 / 0.0117 / 0.0117 | state entering a chunk reaches the output at every position; effect decays with position (carried across the chunk boundary) |
| s5vit-base | uzh-rpg/ssms_event_cameras (vendored src/SSMViT) | 9 | 0.0000 / 0.0000 / 0.0000 | 0.0e+00 | 0.0300 / 0.0126 / 0.0131 | state entering a chunk never reaches the output (reset at every chunk / inert state) |
| s5vit-small | uzh-rpg/ssms_event_cameras (vendored src/SSMViT) | 9 | 0.0000 / 0.0000 / 0.0000 | 0.0e+00 | 0.0273 / 0.0110 / 0.0094 | state entering a chunk never reaches the output (reset at every chunk / inert state) |

EvRT-DETR decoder queries are top-k selected from encoder tokens, so output index i is not the same object in two runs and the raw tensor change above is not a clean magnitude. Order-invariant views (p = 0 / 10 / 20):
- sorted top-100 confidence vector, relative L2 change: 0.2270 / 0.1146 / 0.0891; occluding previous window (p=1/10/20): 0.0701 / 0.0870 / 0.0790
- share of confident detections (score >= 0.25) without a same-class IoU >= 0.5 partner after zeroing: 0.4347 / 0.1533 / 0.1042; occluding previous window: 0.0476 / 0.0249 / 0.0145

History range inside the pooled Gen1 validation score (labelled frames, windows seen since the sequence start; from experiments/e66_fixedH/dets-rvt-s.npz ri+1): min 2, median 602, max 1200; share with <= 21 windows 0.017.
For RVT and EvRT-DETR the pooled score therefore mixes histories from 2 to 1200 windows (state carried from the sequence start); for SSM-ViT the evaluation chunk is 21 windows, so the position inside the chunk (1..21 windows) is the history, because the state entering a chunk is inert (rel. change 0 at every position).
