# Provenance of the second architecture (2026-09-08)

## What was fetched, and from where

| item | source | size | md5 |
|---|---|---|---|
| code | `https://github.com/uzh-rpg/ssms_event_cameras` (shallow clone, `RVT/` subtree vendored to `src/SSMViT/`) | 1.2 MB | — |
| S5-ViT-Small, Gen1 | `https://download.ifi.uzh.ch/rpg/CVPR24_Zubic/gen1_small.ckpt` | 116 575 480 B | `0e4e37d7806a05d65bd63e0b114cc1c6` |
| S5-ViT-Base, Gen1 | `https://download.ifi.uzh.ch/rpg/CVPR24_Zubic/gen1_base.ckpt` | 218 814 784 B | `448ee83f988da39e9596226e29003e0a` |

Paper: N. Zubic, M. Gehrig, D. Scaramuzza, *State Space Models for Event Cameras*, CVPR 2024,
pp. 5819–5828. Cited in the manuscript as `zubic2024ssm`.

## Why this is the right second architecture, and what it controls for

It is a fork of the RVT repository. Everything except the temporal operator is held fixed:

- **Same data.** Its README links RVT's own preprocessed Gen1 tar
  (`download.ifi.uzh.ch/rpg/RVT/datasets/preprocessed/gen1.tar`), so the archive is
  byte-identical to the one every other predictor-side measurement in this paper runs on.
- **Same representation and window.** `config/dataset/gen1.yaml` names
  `stacked_histogram_dt=50_nbins=10`, ten 5 ms bins over 50 ms.
- **Same window construction.** `scripts/genx/preprocess_dataset.py` builds
  `ev_repr_timestamps_us_end` with the identical statement,
  `list(reversed(range(frame_timestamps_us[0], 0, -delta_t_us)))[1:-1]`, reformatted but not
  changed. The convention that each window ends on a label instant travels with the archive.
- **Same backbone, head and interface.** MaxViT stages, YOLOX head,
  `forward(x, previous_states=...) -> (out, losses, states)`.
- **Matched width.** 9.68 M and 18.19 M parameters against RVT's 9.87 M and 18.54 M.

What differs: each stage's `DWSConvLSTM2d` is replaced by an `S5Block`, a state space layer
evaluated by a parallel associative scan instead of a gated recurrence.

## The one interface difference, and why it does not change the measurement

SSM-ViT's backbone takes a sequence `(L, B, C, H, W)` and returns features for every step;
the released validation code then applies the detection head to one step at a time. Here
`L = 1` and the state is carried across calls, which is the same causal recurrence RVT runs
per step, and `forward_detect` is applied to index 0 exactly as the released code does. The
occlusion instrument is otherwise E45's, unchanged, including the rule that the occluded pass
starts from the recurrent state entering the step.

## Load check (E47a)

Both checkpoints load into a model built from the repository's own configuration files with
**0 missing and 0 unexpected keys**, and run forward under a current framework without the
training code they were serialized from.

## Frame matching (E48)

E44 measured RVT's capacities with a 19-window lag arm, so its samples begin at frame 19,
while E47's bin arm begins at frame 8. E48 re-runs RVT's three capacities on E47's frames
with the same zero fill, so the two families are compared on identical samples rather than on
overlapping ones.
