# E01 — How much asynchronous evidence falls inside one exposure? (2026-09-01)

Measured, not estimated. For each frame of a DSEC sequence, the events whose absolute
timestamps fall between that frame's own published `exposure_start` and `exposure_end` are
counted. Random access via `/ms_to_idx`, so the sweep is cheap. Script: `measure.py`,
run in `cvpr19-gpu-g1:torch2.7.1-cu128`, CPU only.

## interlaken_00_c — daytime, the *short*-exposure regime

| quantity | median | p90 |
|---|---|---|
| exposure width | 1478 us | — |
| **events inside one exposure** | **20 616** | 33 319 |
| fraction of pixels firing at least once | 6.0 % | 8.8 % |
| crossings per firing pixel | 1.10 | 1.24 |

536 frames measured.

## Reading

A single 640x480 frame in the *least* favourable sequence for this argument — daytime, an
exposure of 1.5 ms, 0.3 % of the 50 ms frame period — nonetheless integrates over a window
in which **20 616 asynchronous measurements occur**, spread across 6 % of the sensor. The
frame reports one number per pixel for that window and the benchmark indexes it with one
scalar timestamp.

This answers the risk Team 5 raised, that DSEC daytime motion might be too small for a
support argument to have anything to measure. It is not: the evidence inside the window is
four orders of magnitude more than one sample, and that is before the night sequences,
whose exposure is 14996 us — **10.1x wider** (see E00).

## What this measurement does not establish

`crossings_per_active_pix` near 1.1 means most firing pixels cross threshold about once
per exposure, so this is not yet a statement about **pixel displacement**. Displacement in
pixels needs either the DSEC optical-flow ground truth or ego-motion from `lidar_imu.zip`,
and neither has been downloaded. Until that is measured, this table supports "there is
substantial intra-exposure evidence" and **not** "the object moves k pixels during the
exposure." Do not let the second claim into the paper on the strength of this table.

## zurich_city_09_a — night, the exposure-ceiling regime

Same script, same method, on the 15 ms sequence.

| quantity | daytime (interlaken_00_c) | night (zurich_city_09_a) | ratio |
|---|---|---|---|
| exposure width | 1478 us | 14996 us | 10.1x |
| **events inside one exposure** (median) | 20 616 | **310 320** | **15.1x** |
| p90 | 33 319 | 463 045 | 13.9x |
| fraction of pixels firing | 6.0 % | **38.2 %** | 6.4x |
| crossings per firing pixel | 1.10 | **2.60** | 2.4x |

452 frames measured.

## What changes with the wider window

The daytime table could not support a displacement claim, because 1.10 crossings per firing
pixel is consistent with each pixel crossing threshold once and nothing moving far. **The
night figure is different in kind: 2.60 crossings per firing pixel, on 38 % of the sensor.**
A pixel that crosses the contrast threshold two or three times within a single exposure is
reporting a scene that changed repeatedly while the shutter was open, and 38 % coverage
means this is the image, not a few edges.

This is the regime in which a temporal-support argument has something to measure. It is also,
per E00, exactly the regime in which DSEC's exposure is **pinned** — the six ceiling
sequences never vary their exposure. So the wide-support regime and the varying-support
regime do not coexist in DSEC, and an experimental design needs both from different sources.

Caveat carried forward unchanged: crossings per firing pixel is still not a measurement of
pixel displacement. It bounds it from below in the sense that repeated crossings require
change, but converting it to pixels needs flow or ego-motion, which has not been downloaded.
