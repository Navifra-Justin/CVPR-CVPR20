# Reviewer brief — CVPR20, idea-selection round

## What you are judging

Ten competing research ideas for a CVPR 2027 submission, in
`/media/hdd8/justin/my_project/CVPR20/ideas/team01.md` ... `team10.md`.
They share one domain: **Temporal-Support-Aligned Event–RGB Perception**. The seed
observation is that frame and event observations do not share the same temporal support
under fast motion. Plain event+RGB fusion was forbidden as a contribution.

Each team was given a different assumption to attack. Several converged anyway, which is
itself evidence you should weigh — for or against.

## Facts verified on the target machine, not by the idea teams

These were measured directly and supersede any team's guess. Full records are in
`/media/hdd8/justin/my_project/CVPR20/experiments/`.

**Hardware.** One usable GPU (RTX 5090, GPU index 1), already holding ~23.5 GB of other
people's processes, so **~9 GB free and not guaranteed**. Docker only. `torch 2.7.1+cu128`
on `sm_120` confirmed working in `cvpr19-gpu-g1:torch2.7.1-cu128`. 990 GB disk free.

**DSEC publishes per-frame exposure start and end in microseconds** — the file
`<seq>_image_exposure_timestamps_left.txt` exists and was downloaded. Across 18 train
sequences the exposure width ranges **118 us to 14996 us, a factor of 127**, while the
frame period is 50 ms everywhere. Six sequences sit pinned at exactly 14996 us. Within
`interlaken_00_d` alone exposure varies 337 -> 4207 us, frame to frame.

**The published `image_timestamp` equals the average of the left and right mid-exposures
to within 1 us.** DSEC's documented convention is exact. Left and right exposure windows
do differ in daytime (median 16-144 us, max 380 us), but that divergence is two orders of
magnitude smaller than the window width itself. An argument resting on left/right
divergence rests on the smaller effect and should be marked down.

**Inside one 1478 us daytime exposure there are a median of 20 616 events**, touching 6 %
of pixels, ~1.10 threshold crossings per firing pixel (536 frames of `interlaken_00_c`).
The night sequences' windows are 10.1x wider. This answers the objection that DSEC daytime
motion is too small to measure. It does **not** establish pixel displacement during
exposure — crossings per firing pixel near 1.1 is not a displacement measurement, and no
team may claim displacement from it without measuring flow or IMU.

**Events and frames share one clock with no calibration step.** In `interlaken_00_c` the
first event lands 689 us after the first exposure opened and 781 us before it closed.

**RVT's event window ends at the label time.** Verified in the released source:
`config/dataset/gen1.yaml` sets `stacked_histogram_dt=50_nbins=10`, and
`preprocess_dataset.py:405` builds `ev_repr_timestamps_us_end` by counting **backwards**
from label timestamps. So a `dt=50 ms` representation attached to a label at `t` is built
from `[t-50 ms, t]`, uniform-weight centroid `t-25 ms`. Whether the trained network
weights the ten bins uniformly is unmeasured, so 25 ms is a reference point, not a
prediction of network behaviour.

## Known process defects you must account for

The idea teams shared a 200-call web-search budget and **exhausted it**. Teams 2, 3, 5, 7
and 8 each reported that they could not finish their prior-art sweep. Treat every novelty
claim as provisional. If an idea's novelty is its only real asset, say so — that is a
reason to rank it lower, because an unverified novelty claim is a liability under a
deadline, not an asset.

## Your job

You are one of ten reviewers with different specialisms. Follow `reviews/RUBRIC.md`.
Ground your judgement in real accepted papers you fetch and name — at least five from
CVPR/ICCV/ECCV/NeurIPS 2024-2026. A reviewer who cannot name their comparison set is
disqualified for the round.

Judge what would survive the actual CVPR process: an idea that is beautiful and
unfinishable by November 2026 on 9 GB is worth less than one that is merely good and
certain to produce a real figure.
