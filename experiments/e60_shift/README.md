# E60 — the same frame, with and without its history (2026-09-16)

## Why this exists

E58 measured what the release's streaming chunk position is worth: **−4.37** and **−5.32** mAP
points for `s5vit-small` and `s5vit-base`, net of an RVT control, on every labelled box. The
control is what a reviewer will press on. Frames at chunk position 0–3 are *different frames*
from those at 16–20, so the raw span mixes temporal support with scene content, and RVT removes
the scene term only under parallel trends — the assumption that, absent a support difference,
early-chunk frames would have scored like late-chunk frames up to a model-independent offset.
The leave-one-out placebo bounds the slack among RVT models at 0.67 points against a treated
effect of 5–6, but bounding an assumption is not removing it.

E60 removes it. The same checkpoints, the same weights, the same ground truth, the same
evaluator, and **the same frames** are scored twice, differing only in how many windows of
recurrent history the streaming protocol handed each frame.

## The intervention

`e51_dump_all.py` places chunk starts where `sequence_for_streaming.py` places them,

    start = max(objframe_idx_2_repr_idx[0] - sequence_length + 1, 0)

and advances by `sequence_length = 21`, so a labelled frame's position is `(repr_idx - start) % 21`.
Moving `start` later by `SHIFT` rotates every position by `-SHIFT (mod 21)`.

**`SHIFT = 5`.** That is the value that carries the release's starved block onto its full block:
positions 0–3 become 16–19. The frames the released protocol gave one to four windows of history
are scored again with seventeen to twenty, and nothing else about them changes.

## Two defects this found before spending the card, and one after

**Defect A — subtracting from a clamped value.** The first version moved boundaries *earlier*:
`start = max(o2r[0] - 21 + 1 - SHIFT, 0)`. The release's own start is already `max(o2r[0]-20, 0)`,
and Gen1 labels begin early enough that for most sequences it is pinned at 0. Subtracting from a
value that is already clamped does nothing. The run exited 0, wrote 20 296 frames matching E58
exactly and ground truth identical to the baseline — and had left **73.5 % of frames at the
position they already had**:

| | old-short → new-full | old-full → new-short | unchanged |
|---|---:|---:|---:|
| boundaries earlier by 16 (run, then discarded) | 774 / 3672 | **18 / 5069** | 14 927 / 20 296 |
| boundaries later by 5 (the design) | **3574 / 3672** | 0 / 5069 | 0 / 20 296 |

The 18 is the tell. A genuine rotation moves every frame; this one moved a fifth of them, in one
direction, in the sequences that happened to start late. The dump is kept as
`dets-s5vit-small-shift16.BROKEN-earlier-clamp.npz` rather than deleted, because it is the
evidence for the row above.

**Defect B — clamping the other end.** The repair `start = min(max(o2r[0]-20,0) + SHIFT, o2r[0])`
clamped the start at the first labelled frame so that no frame could fall outside a chunk. **216
of the 406 sequences** have their first label at a repr index below 16, so for those the clamp
pinned the start at the label itself and the rotation they received was `o2r[0]`, not `SHIFT`.
The `(old - new) mod 21` histogram came out as six bars instead of one. Caught by the check
below, with no GPU used.

**The check is now a precondition of the run.** `run_e60.sh` executes
`src/e60_verify_shift.py` first and refuses to claim GPU 1 unless it exits 0. The script reads
only `objframe_idx_2_repr_idx.npy`, `labels.npz` and the representation timestamps — no model,
no CUDA, no event data — and replays the dumper's exact frame enumeration.

## What the check asserts, and what it reports at SHIFT = 5

```
406 sequences, 20296 labelled frames, CHUNK=21 SHIFT=5

1. SHIFT=0 replay vs the positions the released protocol actually recorded
  [PASS] the shifted start is inert at SHIFT=0
  [PASS] frame count                      replay 20296  recorded 20296
  [PASS] every position identical         0 differ
2. new position == (old - 5) mod 21
  [PASS] every covered frame rotates      0 of 20189 do not
3. frames covered by a chunk
  [PASS] uncovered frames under 3 %       107 of 20296 (0.53 %), old 0
4. short(0,4) / full(16,21) block exchange
     old-short -> new-full : 3574 / 3672
  [PASS] one direction carries its whole block            best 97.3 %
  [PASS] e60_paired.py direction (short -> full) populated 3574 frames
```

Item 1 is what licenses the rest: the replay is only a statement about the real dump if it
reproduces `experiments/e58_chunkpos/positions.npy` exactly, which it does, and the modified
start expression must be inert at `SHIFT = 0` or it would have moved the released protocol
itself.

**On the 107 uncovered frames.** A start moved later than a sequence's first label leaves that
label before the first chunk. It cannot be avoided — those sequences' released start is already
0, so no start both covers the first label and delivers the same rotation as everywhere else.
The dump records `-1` for them and the paired analysis requires FULL in the shifted arm, which
excludes them by construction, so the pairing stays on frames covered in *both* arms.

**Why one direction and not two.** A rotation is a bijection, so a single `SHIFT` cannot carry
0–3 onto 16–20 and 16–20 onto 0–3 at once: that needs `S ≡ -S (mod 21)`, which has no solution
but 0. `SHIFT = 5` gives short → full, `SHIFT = 16` gives full → short. The first is the
direction `e60_paired.py` scores, and it is the stronger statement of the two — it takes the
frames the released protocol starved and hands them the history the release already intends to
carry.

## The estimand

For each SSM checkpoint, over the 3574 frames that sat at positions 0–3 under the release and at
16–19 under the shift:

    gain = mAP(shifted dump, those frames) - mAP(released dump, those frames)

Same frames, same labels, same weights, same evaluator, delta = 0. Uncertainty is the same
cluster bootstrap over the 406 validation sequences E58 uses (B = 300). E58's difference-in-
differences predicts a gain of roughly +6 to +7 points; if the E58 number were an artifact of
the parallel-trends assumption rather than of temporal support, this is where it would vanish.

## Files

- `e51_dump_all.py` with `SHIFT` → `dets-s5vit-{small,base}-shift5.npz`, carrying each frame's position
- `e60_verify_shift.py` → `positions-shift{5,16}.npz`, `verify-shift{5,16}.log` — the GPU-free precondition
- `e60_paired.py` → `paired.json` — the within-frame contrast and its cluster bootstrap
- `run_e60.sh` — verification, then the GPU 1 wait, then both dumps
- `dets-s5vit-small-shift16.BROKEN-earlier-clamp.npz` — defect A, kept as evidence
