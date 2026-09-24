# E58 — one released number, twenty-one different temporal supports (2026-09-16)

## Why this exists

External review #8 accepted the measurement and named the significance: the timing correction
moves mAP by 0.0004, reorders no checkpoint, and the full recurrent centroid is unidentified.
The first two are answered by E56 (what timing difference a benchmark *can* resolve) and this
one answers the same objection from the other side — by finding a place where the unidentified
temporal support is worth **several mAP points of a released number**, not 0.0004.

The paper's thesis is that a single timestamp on a benchmark entry does not identify the
temporal support behind it. SSM-ViT's released Gen1 evaluation is an instance where that is
literally true and costly.

## The mechanism, which was already measured

E47c established it and the supplement already reported it in one sentence. Both releases
carry the recurrent state across streaming chunks; neither resets per chunk
(`modules/detection.py` resets only on `IS_FIRST_SAMPLE`, i.e. at the start of a *sequence*).
The difference is that in the SSM release the carried state is injected as
`Lambda_bars[0] = Lambda_bars[0] * prev_state` before an associative scan, and the modified
`a_0` reaches no output at any position. E47c measured exactly 0.00000 at every position,
against 0.0276–0.0106 for occluding a window one position *earlier inside* the chunk.

So the release intends to carry history, and the algebra says it does not. A released SSM-ViT
detection's temporal support is therefore its position in a 21-window chunk: one window
(50 ms) at position 0, twenty-one (1050 ms) at position 20. The reported Gen1 number averages
over all twenty-one. Nothing in the metric, the protocol, or the published table names the
variable being averaged over.

Validation and test both take this path: `dataset_streaming.py` sets
`guarantee_labels = dataset_mode == DatasetMode.TRAIN`, so the reported splits use a single
uniform chunk stride rather than the training splitter.

## Reconstructing the position without running anything

Chunk starts are placed at `max(objframe_idx_2_repr_idx[0] - sequence_length + 1, 0)` and
advance by `sequence_length` (`sequence_for_streaming.py:80,93`). `e51_dump_all.py` places them
with the identical expression (its `SHIFT` is 0 for every dump this experiment uses). The
position of a labelled frame is therefore `(repr_idx - start) % 21`, recoverable from the index
files alone.

`e58_chunkpos.py` refuses to proceed unless the reconstructed array indexes exactly the frames
in the dump: **20296 positions, 20296 frames**.

## Result: the effect, against a control

Position groups hold *different frames*, so a raw span across positions mixes temporal support
with scene content. RVT is the control — its carried state is not inert, so for RVT the chunk
position is an arbitrary label on the same frames. The estimand is the difference-in-differences,
and a leave-one-out placebo puts each RVT model in the treated slot with the other two as its
control. Uncertainty is a cluster bootstrap over the 406 admitted sequences (B=300).

Contrast: positions 0–3 (1–4 windows of history, n=3672 frames) against positions 16–20
(17–21 windows, n=5069).

| model | short | full | raw | control | **DiD** | SE | 95 % CI | z |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| `rvt-t` | 32.612 | 33.469 | −0.856 | −1.522 | **+0.666** | 0.637 | [−0.74, +1.72] | 1.05 |
| `rvt-s` | 32.601 | 34.202 | −1.601 | −1.149 | **−0.452** | 0.513 | [−1.33, +0.67] | −0.88 |
| `rvt-b` | 36.556 | 37.998 | −1.442 | −1.229 | **−0.214** | 0.549 | [−1.22, +1.11] | −0.39 |
| `s5vit-small` | 24.348 | 31.109 | −6.761 | −1.300 | **−5.461** | 1.012 | [−6.96, −3.24] | **−5.39** |
| `s5vit-base` | 27.518 | 34.879 | −7.361 | −1.300 | **−6.061** | 0.703 | [−7.30, −4.57] | **−8.62** |

Three placebos null, two treated checkpoints at |z| = 5.4 and 8.6, in the predicted direction.

On the population a released Gen1 number is reported over — every labelled box, not only the
velocity-evaluable subset (`e58d_allbox.py`) — the same contrast gives **−4.373** (z = −7.22)
and **−5.322** (z = −10.01), with placebos at +0.666, −0.507, −0.159.

### What the pooled number hides

| model | pooled | at full support | gap | net of control |
|---|---:|---:|---:|---:|
| `rvt-t` | 38.900 | 38.194 | +0.706 | +0.350 |
| `rvt-s` | 39.684 | 39.167 | +0.517 | +0.067 |
| `rvt-b` | 42.320 | 42.126 | +0.194 | −0.417 |
| `s5vit-small` | 35.554 | 36.410 | −0.855 | **−1.328** |
| `s5vit-base` | 38.950 | 40.226 | −1.276 | **−1.748** |

The same weights, frames, labels and metric score **1.7 points higher** when the protocol
grants the full temporal support it already intends to grant. These levels are this paper's
evaluator on every labelled box, not the official COCO tool, so the level is comparable to a
published table but is not itself the published number.

## An instrument that never touches the metric

If this is real it must be visible in the raw detection tensors, with no labels involved.
`e58c_invariant.py` counts detections and averages confidence per frame by position:

| windows of history | 1 | 5 | 9 | 13 | 17 | 21 |
|---|---:|---:|---:|---:|---:|---:|
| `rvt-t` | 0.6680 | 0.6662 | 0.6611 | 0.6579 | 0.6776 | 0.6625 |
| `s5vit-small` | 0.4634 | 0.5515 | 0.5500 | 0.5497 | **0.5737** | 0.5417 |
| `s5vit-base` | 0.4833 | 0.5395 | 0.5553 | 0.5585 | **0.5893** | 0.5470 |

SSM confidence rises monotonically over the first third of the chunk and then plateaus,
+23.8 % from one window to seventeen. RVT is flat across all twenty-one on the same frames.
No ground truth, no IoU matcher, no evaluator.

## A permutation null for the position labels themselves

The cluster bootstrap gives the sampling error of the DiD but assumes the reconstructed
positions mean what the reconstruction says they mean. `e58g_perm.py` removes that assumption by
reshuffling chunk position among the frames of each sequence. That preserves scene, sequence
length, label density and the sizes of both blocks, and destroys only the correspondence between
a frame and the history the protocol gave it.

| model | observed | null mean | null SD | \|z\| | p (2-sided) |
|---|---:|---:|---:|---:|---:|
| `rvt-t` | +0.666 | −0.045 | 0.469 | 1.52 | 0.139 |
| `rvt-s` | −0.507 | −0.063 | 0.445 | 1.00 | 0.269 |
| `rvt-b` | −0.159 | +0.108 | 0.466 | 0.57 | 0.607 |
| `s5vit-small` | **−4.373** | −0.161 | 0.553 | **7.61** | 0.005 |
| `s5vit-base` | **−5.322** | −0.237 | 0.517 | **9.84** | 0.005 |

All three placebos sit inside their own null; both treated checkpoints sit 7.6 and 9.8 standard
deviations outside theirs, at the resolution floor of a 201-draw permutation.

## Position by position, rather than two blocks

`e58e_curve.py` measures the same contrast at each of the 21 positions separately, which
distinguishes a monotone consequence of accumulated history from a step at the aggregation
boundary, and puts the placebos on the same axis. `e58f_fig.py` draws it as `paper/figs/chunkpos.pdf`:
panel (a) is mAP over every labelled box, panel (b) is mean detection confidence, which uses
neither the ground truth nor the evaluator.

## Files

- `e58_chunkpos.py` → `positions.npy`, `result.json` — position reconstruction and the position-grouped sweep
- `e58b_did.py` → `did.json` — difference-in-differences, placebo, cluster bootstrap
- `e58d_allbox.py` → `allbox.json` — the same on every labelled box
- `e58c_invariant.py` → `invariant.json` — the label-free confidence curve
- `e58e_curve.py` → `curve.json` — mAP and confidence at each of the 21 positions
- `e58f_fig.py` → `paper/figs/chunkpos.pdf`, `chunkpos_full.pdf` — the figure
- `e58g_perm.py` → `perm.json` — the within-sequence position-permutation null
- `verify.log`, `verify-shift0.npz` — the patched dumper reproducing an existing dump at SHIFT=0

## What this still assumes, and E60

The difference-in-differences assumes RVT and SSM respond to scene content alike (parallel
trends). The leave-one-out placebo bounds the slack among RVT models at 0.67 points against a
treated effect of 5–6, but it does not eliminate the assumption. `run_e60.sh` removes it: the
same SSM checkpoints are re-run with every chunk boundary moved **5 windows later**, which
rotates every position by −5 and so carries the release's starved block, positions 0–3, onto
16–19. The 3574 frames the protocol gave one to four windows of history are scored again with
seventeen to twenty, and the comparison becomes within-model and within-frame with no control
at all. See `experiments/e60_shift/README.md`, including the two ways the shift was got wrong
before a GPU-free check on the index files caught them.
