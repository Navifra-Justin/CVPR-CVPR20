# E00 — DSEC exposure survey (measured 2026-09-01, main session, not an agent)

Source: `https://download.ifi.uzh.ch/rpg/DSEC/train/<seq>/<seq>_image_exposure_timestamps_left.txt`
Raw files copied into this directory. Header of each file:
`# exposure_start_timestamp_us, exposure_end_timestamp_us`.

19 of 23 probed train sequences returned the file; 4 (interlaken_01_a, zurich_city_12_a,
13_a, 15_a) 404 under this naming and were not resolved.

| seq | n | exp_min (us) | exp_med | exp_max | frame_dt (us) |
|---|---|---|---|---|---|
| interlaken_00_c | 537 | 786 | 1475 | 2614 | 49997 |
| interlaken_00_d | 1991 | 337 | 882 | 4207 | 49997 |
| interlaken_00_e | 1991 | 642 | 1096 | 2903 | 49997 |
| interlaken_00_f | 1491 | 989 | 1091 | 1353 | 49997 |
| interlaken_00_g | 1335 | 620 | 920 | 3395 | 49997 |
| thun_00_a | 239 | 941 | 1005 | 1128 | 50001 |
| zurich_city_00_a | 939 | 14996 | 14996 | 14996 | 50001 |
| zurich_city_01_a | 681 | 14996 | 14996 | 14996 | 50001 |
| zurich_city_02_a | 235 | 14996 | 14996 | 14996 | 50001 |
| zurich_city_03_a | 883 | 14996 | 14996 | 14996 | 50001 |
| zurich_city_04_a | 701 | 802 | 1133 | 1882 | 49997 |
| zurich_city_05_a | 1753 | 658 | 1871 | 3988 | 50001 |
| zurich_city_06_a | 1523 | 118 | 454 | 797 | 50001 |
| zurich_city_07_a | 1463 | 203 | 299 | 647 | 50001 |
| zurich_city_08_a | 787 | 513 | 797 | 1657 | 50001 |
| zurich_city_09_a | 1813 | 14996 | 14996 | 14996 | 50001 |
| zurich_city_10_a | 2315 | 14996 | 14996 | 14996 | 50001 |
| zurich_city_11_a | 465 | 577 | 647 | 1160 | 50001 |

## What this establishes

1. Exposure spans **118 us to 14996 us across DSEC train, a factor of 127**, while the
   frame period is fixed at 50 ms (20 Hz) in every sequence. The ratio of exposure to
   frame period therefore ranges from 0.24 % to 30 %.
2. Six sequences sit **pinned at exactly 14996 us**, the auto-exposure ceiling. Their
   integration window is 15 ms wide; at 50 km/h that is 21 cm of ego translation inside
   one frame, and a frame is nonetheless indexed by a single scalar timestamp.
3. Within a single sequence exposure varies up to 12.5x (interlaken_00_d, 337 -> 4207 us),
   so the integration window changes **frame to frame** inside one recording.

## Why it matters for this paper

The independent variable that a temporal-support argument needs is not something we have
to synthesise: DSEC already publishes it, already varies it by two orders of magnitude,
and every downstream method still consumes one timestamp per frame. Whatever idea is
selected, this table is the evidence that the quantity in dispute is real and measurable
on a standard benchmark with zero training.

Caveat before use in the paper: these are the **left camera** exposure files. DSEC's image
timestamp is documented as the average of the middle exposures of the left and right
cameras, so the left-only window is not identical to the indexed instant. That gap must be
measured, not assumed, before it is cited.

## Follow-up measurement: is the indexed timestamp really the exposure midpoint?

Measured the same day on left+right exposure files and the published `image_timestamps.txt`.

| seq | n | median &#124;w_L - w_R&#124; | max | median &#124;mid_L - mid_R&#124; | max | ts - avg(mid_L,mid_R) |
|---|---|---|---|---|---|---|
| zurich_city_09_a | 1813 | 0 | 0 | 0 | 0 | 0 (max 0) |
| interlaken_00_d | 1991 | 54 us | 305 us | 27 us | 152 us | median 1 us (max 1) |
| zurich_city_05_a | 1753 | 144 us | 380 us | 72 us | 190 us | median 0 us (max 1) |
| zurich_city_06_a | 1523 | 16 us | 102 us | 8 us | 51 us | median 0 us (max 1) |

Two findings, one of which corrects the caveat written above.

1. **The published image timestamp is the average of the left and right mid-exposures, to
   within 1 us.** DSEC's documentation is exact, not approximate. The caveat in the
   previous section — that the left-only window might not match the indexed instant — is
   resolved: the convention is precisely the mid-exposure average, and the paper may say so.
2. **The two cameras do not share an integration window in daytime sequences.** Auto-exposure
   runs independently per camera, so left and right exposure widths differ by a median of
   16-144 us and up to 380 us, and their midpoints by up to 190 us. In the night sequences
   both cameras sit pinned at the 14996 us ceiling and the two windows coincide exactly.

So one scalar timestamp does stand in for two different integration windows, but the
divergence between them is on the order of 10^2 us, while the window itself is 10^2 to
1.5x10^4 us wide. **The dominant quantity is the width of the window, not the disagreement
between the two cameras.** Any argument built here should rest on the width. A claim that
leans on left/right divergence would be resting on the smaller of the two effects by one
to two orders of magnitude, and a reviewer would find that immediately.

## Refinement: the two cameras are co-triggered (measured 2026-09-01, second pass)

Prompted by reviewer 1, who computed this independently. Re-measured here and confirmed.

| seq | n | exposure START identical L vs R | max abs diff of starts | median abs diff of widths | max |
|---|---|---|---|---|---|
| interlaken_00_d | 1991 | **1991/1991 = 100.00 %** | 0 us | 54 us | 305 us |
| zurich_city_05_a | 1753 | **1753/1753 = 100.00 %** | 0 us | 144 us | 380 us |
| zurich_city_06_a | 1523 | **1523/1523 = 100.00 %** | 0 us | 16 us | 102 us |
| zurich_city_09_a | 1813 | **1813/1813 = 100.00 %** | 0 us | 0 us | 0 us |

7080 frames, zero exceptions. The left and right exposures **open at the same microsecond**
and differ only in when they close, because auto-exposure sets each camera's width
independently. That is why the mid-exposure difference measured earlier is exactly half the
width difference — it is not an independent quantity.

This supersedes the looser statement above that "the two cameras do not share an
integration window". They share a trigger; they do not share a width.

**Consequence for any claim built on left/right divergence:** it is not a synchronisation
effect and it is not a timing jitter. It is the width difference, halved. Team 1's
pre-registered prediction of "≥ 1 ms divergence on a substantial fraction of frames" is
falsified: **0.00 % of frames exceed 1 ms**, and the maximum observed anywhere is 190 us.

## How much of DSEC is at the exposure ceiling

Across all 18 surveyed train sequences, 21 142 frames:

    frames pinned at exactly 14996 us = 6866 = 32.5 %

So a third of DSEC train sits at the auto-exposure ceiling. Reviewer 1's observation
follows and is worth recording: **long exposure and exposure *variation* are
anti-correlated in DSEC.** The sequences with the widest integration window are exactly the
ones where the width never changes, and the sequences where width varies frame-to-frame are
the daytime ones where the window is short. Any experimental design that wants both a wide
support and a varying support will not find both in the same DSEC sequence.

## Correction: the distribution is two-point, not bimodal (re-measured 2026-09-02)

Earlier text here and elsewhere described the exposure distribution as bimodal with
"little mass between 5 and 15 ms". Measured exactly, over all 21 142 frames:

    frames strictly between  4207 and 14996 us : 0
    frames strictly between  5000 and 14996 us : 0
    largest exposure below the ceiling         : 4207 us
    percentile 66 : 2999 us      percentile 68 : 14996 us

**There is no mass between the two modes at all.** The distribution is a continuous mode
below 4.21 ms and a spike at exactly 14996 us, separated by an empty interval of 10.8 ms.
The 66th to 68th percentile step jumps from 3.0 ms to 15.0 ms.

"Little mass between" understates this and should not be used. The correct statement is
that DSEC's auto-exposure occupies two disjoint regimes and nothing in between, so exposure
width is effectively a binary condition on this dataset rather than a continuous covariate.
That is a constraint on any experiment that wants to sweep support width: on DSEC it cannot
be swept, only switched.

Figure 1's caption and the paper text must be corrected accordingly.
