# E47 / E48 — the same measurement on a second architecture (2026-09-08)

## Why this exists

Every predictor-side number in the paper was RVT, whose temporal operator is a per-stage
ConvLSTM. External review #5 named the "one checkpoint" objection as the highest-value
reduction available; E44 answered it with three capacities, and this answers it with a second
architecture.

SSM-ViT (Zubic et al., *State Space Models for Event Cameras*, CVPR 2024) is the right
second architecture because it is a fork of the RVT repository with one thing changed. See
`PROVENANCE.md` for the fetch record, the checksums, and the list of what is held fixed:
the same preprocessed Gen1 archive, the same `stacked_histogram_dt=50_nbins=10`
representation, the same window-construction statement, the same MaxViT stages and YOLOX
head, and matched widths. What differs is `DWSConvLSTM2d` → `S5Block`.

## Result

Five released checkpoints, same 12 Gen1 validation sequences, same frames, same zero fill,
the occluded pass started from the state entering the step (E45's rule).

| model | operator | params | n | centroid | CV | max/min | older half |
|---|---|---|---|---|---|---|---|
| `rvt-t` | ConvLSTM | 4.41 M | 480 | **−23.810** | 0.131 | 1.52 | 48.6 % |
| `rvt-s` | ConvLSTM | 9.87 M | 480 | **−23.981** | 0.114 | 1.47 | 48.8 % |
| `rvt-b` | ConvLSTM | 18.54 M | 480 | **−24.133** | 0.100 | 1.40 | 49.2 % |
| `s5vit-small` | S5 state space | 9.68 M | 288 | **−23.758** | 0.101 | 1.42 | 46.7 % |
| `s5vit-base` | S5 state space | 18.19 M | 288 | **−24.723** | 0.078 | 1.27 | 50.8 % |

Span 0.96 ms; none further than 1.24 ms, a quarter of one bin, from the uniform-weight
−25.00 ms. E48's `rvt-t` reproduces E45 to three decimals (−23.810, CV 0.1313, bootstrap SE
0.054), which is the check that the matched-frame code path is the same instrument.

## The part that had to be measured twice

The first attempt drove SSM-ViT the way RVT is driven, one window per call with the state
carried. Its own support arm then reported that zeroing the recurrent state changed the
output by 0.0000 and that no past window carried influence. That is not a result, and the
runs are withdrawn: `withdrawn_L1/WHY.md`.

The release injects the carried state as `Lambda_bars[0] = Lambda_bars[0] * prev_state`
before an associative scan whose outputs are the `b` components of
`(a_i,b_i)∘(a_j,b_j) = (a_j a_i, a_j b_i + b_j)`. Since `b_p` is built from `a_1…a_p`, the
modified `a_0` reaches no output at any position: the carried state is inert. E47c measured
exactly that, with a control that rules out the alternative explanation:

| position in chunk | zero the entering state | occlude the previous window |
|---|---|---|
| | `s5vit-small` / `rvt-t` | `s5vit-small` / `rvt-t` |
| 0 | 0.00000 / 0.08211 | — |
| 1 | 0.00000 / 0.06162 | 0.02760 / 0.01278 |
| 4 | 0.00000 / 0.03946 | 0.01305 / 0.01234 |
| 7 | 0.00000 / 0.03044 | 0.01060 / 0.01246 |

`s5vit-base` gives the same zeros with in-chunk values 0.0281 falling to 0.0131. So the SSM
release is recurrent *within* a chunk and loses the state *between* chunks, and its released
streaming evaluation steps through the split in non-overlapping chunks of 21 windows
(`sequence_length` in `config/dataset/gen1.yaml`; `start_indices` in
`sequence_for_streaming.py` steps by exactly that). A released detection's temporal support
therefore runs from the current window alone at the first position of a chunk to 21 windows
at the last. The paper reports this as a property of the release, in the supplement, and not
as a claim about what the architecture could support if the state were carried.

E47b consequently measures the bin profile the way the release computes detections: chunks
of eight windows, occlusion applied to one window, the output read at that window's position,
and only positions carrying at least four preceding windows used. That is why the SSM rows
have 288 samples against 480.

## Files

- `PROVENANCE.md` — where the code and checkpoints came from, and what is held fixed
- `s5vit-{small,base}-chunked.json` — the reported bin profiles
- `statepos-{s5vit-small,s5vit-base,rvt-t}.json` — the state-effect-by-position arms
- `../e48_matched_frames/rvt-{t,s,b}.json` — RVT on the same frames
- `compare.log`, `macros.tex`, `macros_statepos.tex` — the table and the manuscript macros
- `withdrawn_L1/` — the first attempt and why it was withdrawn

Recorded as case 10 in `docs/PROTOCOL_LEDGER.md`.
