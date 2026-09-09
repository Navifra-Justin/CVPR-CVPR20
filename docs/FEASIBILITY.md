# CVPR20 — Compute and data feasibility (verified 2026-09-01)

Every fact here was checked on this machine on 2026-09-01. Idea and paper agents must
treat this file as the binding constraint set; anything not listed here is unverified.

## Compute

- Two RTX 5090 (32607 MiB each) are present, but **only GPU 1 may be used**.
- GPU 1 already holds ~23.5 GB across six other processes. **Usable VRAM: ~9 GB**, and
  that figure can move, so a design that needs 9 GB exactly is a design that fails.
  Target <= 7 GB steady-state with gradient checkpointing / AMP available as headroom.
- No host installs. All work runs in Docker (`--gpus '"device=1"'`).
- Disk: 990 GB free on /media/hdd8. Budget for data: <= 300 GB.

## Data — verified reachable

| Source | Probe result | Size |
|---|---|---|
| DSEC per-sequence events (`.../DSEC/train/<seq>/<seq>_events_left.zip`) | HTTP 200 | 856 MB (interlaken_00_c) |
| DSEC per-sequence rectified images | HTTP 200 | 1.36 GB (interlaken_00_c) |
| DSEC per-sequence calibration | HTTP 200 | 2.2 KB |
| DSEC bulk (`train_coarse/train_events.zip` etc.) | listed on the official download page | large |
| HuggingFace mirror `mickeykang/DSEC-3DOD` | HTTP 200 | 40.2 GB single zip |
| HuggingFace mirror `Passwerob/DSEC_proc` | HTTP 200 | 395 GB, chunked — too large |
| EVIMO2 project page | HTTP 200 | download links to be resolved per-sequence |
| pypi | reachable | `tonic` 1.6.0, `dv-processing` 2.0.4, `expelliarmus`, `h5py`, `hdf5plugin` |
| github.com | reachable | v2e / ESIM / rpg_vid2e must be installed from source, not pypi |

Directory listing on `download.ifi.uzh.ch/rpg/DSEC/` returns 403, but **individual file
URLs return 200**. Fetch by explicit path; do not try to crawl the index.

`v2e` and `esim-py` are **not on pypi** — a simulator plan must build from GitHub inside
the Docker image, and the plan must say which repository and commit.

## What is not on disk

No event dataset is present locally. `find` for event/DSEC/MVSEC/DAVIS/Prophesee under
/media/hdd8/justin returns only TensorBoard `events.out.tfevents.*` files and unrelated
trading data. Everything must be downloaded or simulated.

## Local video that could drive a simulator

`/media/hdd8/justin/navifra/wingbody` (463 GB) holds real multi-camera ROS2 rosbags with
RGB and LiDAR. Frame rate and rolling-shutter behaviour are **unverified**; before any
plan depends on it, confirm the actual FPS and exposure metadata. Standard high-FPS video
sets (GoPro, X4K1000FPS, Need-for-Speed) were not probed and remain an open item.

## Consequences for idea selection

1. An idea requiring more than ~7 GB of training VRAM is not runnable here.
2. An idea requiring a dataset larger than ~300 GB is not runnable here.
3. An idea that can be proven on a controlled simulator and then validated on a few DSEC
   sequences is cheap, and cheap is what fits this machine.
4. An idea that only needs to re-score public checkpoints is the cheapest of all.

## Verified container base (2026-09-01)

`cvpr19-gpu-g1:torch2.7.1-cu128` runs on GPU 1 and reports:

    torch 2.7.1+cu128, CUDA 12.8, NVIDIA GeForce RTX 5090, capability (12, 0)

sm_120 is live, so this image is the base for CVPR20. Driver 570.124.06, CUDA 12.8.
Note the image has `python3` but no `python` on PATH.

Run pattern:

    docker run --rm --gpus '"device=1"' -v /media/hdd8/justin/my_project/CVPR20:/work <image> python3 ...
