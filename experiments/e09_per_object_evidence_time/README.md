# E09 — Per-object evidence time inside one exposure (measured 2026-09-02)

> **CORRECTION 2026-09-03 — re-run with the exposure window restricted exactly.**
> `measure.py` sliced events through `/ms_to_idx`, which is indexed by whole
> milliseconds, and never restricted them to `[a, b]`. The slice was therefore
> `[floor(a), floor(b)]`: it included up to a millisecond of evidence before the
> exposure opened and dropped everything between `floor(b)` and `b`, while the
> analytic null was computed for the nominal width `w = b - a`. The same defect
> was found in E11 and is described there. The script now extends the raw slice
> one millisecond past `b` and filters `a <= t < b` in microseconds.
>
> | quantity | first run | corrected |
> |---|---|---|
> | night frames used | 1133 | **1134** |
> | night within-frame sd | 229.5 us | **206.6 us** |
> | night analytic null | 93.4 us | **93.0 us** |
> | night excess (median per frame) | 208.8 us | **183.6 us** |
> | frames with sd > null | 91.8 % | **90.1 %** |
> | frame-mean offset from mid-exposure | -862 us | **-102.3 us** |
> | random boxes: frames / sd / null / excess | 1120 / 338.4 / 134.4 / 310.5 | **1123 / 338.2 / 134.5 / 306.3** |
> | day frames used | 12 | **20** |
> | day sd / null | 18.7 / 23.9 us | **18.0 / 21.6 us** |
>
> The corrected night arm reproduces E11's `result_exact.json` and E12's
> `w = 14996 us` arm exactly, and the corrected frame-mean offset reproduces
> E16's `obj_offset_med_us`. Three independent scripts now agree.
>
> The per-track results of section (b) and (c) below were also recomputed, by
> `per_track.py`, which writes `per_track_zurich_city_09_a.json`. Their direction
> is unchanged and their magnitudes moved: variance ratio 20.56x -> **14.4x**,
> lag-1 autocorrelation 0.471 -> **0.721**, ratio after removing 32x32 cell means
> 13.45x -> **8.6x**, and the displacement split 0.152 / 0.567 -> **0.611 /
> 0.773** at a median path length of 278 px. The paper reports the recomputed
> values. **The tables further down this file are the first run and are kept for
> the record only.**
>
> The STATUS banner below predates E10, E11 and E12 and is superseded: the
> flicker confound it names was tested three ways in E11 and E12 and does not
> account for the dispersion.

> **STATUS: the night result is CONFOUNDED and must not be used as written.** E10 measured
> 24.1 % of active night pixels phase-locked to the mains at 100 Hz. The flicker check in
> section (d) below was mine and it was WRONG — underpowered by construction. See (d).
> The daytime arm is clean and its excess is zero.

The first direct measurement of the paper's `σ_τ` quantity. It uses **no detector, no
checkpoint, no velocity denominator and no assumed centre noise** — only the event stream,
DSEC's own published exposure windows (E00) and DSEC-Det's released boxes (E06).

## What is computed

For each labelled frame, take that frame's own published exposure window `[a,b]`, slice the
event stream to it (`/ms_to_idx` random access), and for each labelled box `i` compute the
evidence-weighted time centroid of the events inside that box,

    tbar_i = mean( t of events in box i ) - (a+b)/2        # us, relative to mid-exposure

then report the dispersion of `tbar_i` **across the objects of one frame**.

**The null is analytic, and that is the point.** If the evidence inside each box were
uniform over the exposure, `tbar_i` would have variance `w^2 / (12 N_i)` with `w` the
exposure width and `N_i` the box's event count. So

    sigma_evt^2        = Var_i( tbar_i )
    sigma_evt,excess^2 = sigma_evt^2 - mean_i( w^2 / (12 N_i) )

and the subtrahend contains **no assumed quantity**. This is the structural difference from
the `delta_hat = e_par/||v*||` route: no `sigma_c`, no errors-in-variables, no ratio
estimator with divergent variance.

`MIN_EV = 200` events per box, `MIN_OBJ = 3` qualifying objects per frame.

## Result 1 — the night stratum (zurich_city_09_a, exposure pinned at 14996 us)

1133 of 1557 labelled frames usable, median 6 qualifying objects per frame.

| quantity | value |
|---|---|
| within-frame sd of `tbar_i` | **229.5 us** (p90 333.5) |
| analytic uniform null | 93.4 us (p90 145.7) |
| **excess** | **209.7 us** |
| frames with positive excess | **91.8 %** |
| within-frame peak-to-peak spread | **601.6 us** (p90 956.0) |
| frame-level common offset from mid-exposure | **-862 us** (sd across frames 137 us) |

Two readings. First, the pooled evidence that forms the image has a centroid **862 us before
the instant DSEC asserts as the frame's timestamp** — the indexed instant is the
mid-exposure, and the evidence is not centred there. Second, that centroid **varies across
the image within one exposure**, by 230 us sd and 600 us peak-to-peak across the annotated
objects of a single frame, on 91.8 % of frames.

## Result 2 — the daytime stratum (interlaken_00_c, exposure 1523 us): the effect vanishes

12 usable frames (the 200-event floor is severe at a 1.5 ms exposure), median 3 objects.

| quantity | value |
|---|---|
| within-frame sd of `tbar_i` | 18.7 us |
| analytic uniform null | 23.9 us |
| excess | **0 (sd is below the null)** |
| frames with positive excess | 33 % |

**The dispersion scales with the temporal support and disappears when the support is
narrow.** That is the paper's own thesis, demonstrated with no network trained and no
checkpoint run, across E00's two-level exposure factor. The daytime sample is small and this
should be redone with a lower event floor before it is cited as more than directional.

## Result 3 — the controls

### (a) Random-box control — NEGATIVE, and reported as such

Same box shapes, random positions, same frame, same null:

| | sd | null | excess |
|---|---|---|---|
| labelled boxes | 229.5 us | 93.4 us | 209.7 us |
| **random boxes** | **338.4 us** | 134.4 us | **310.5 us** |

Random image regions show a **larger** excess than annotated objects. So the raw within-frame
dispersion is **not** a property of objecthood — it is a property of where events land in the
image during the exposure, and annotated vehicles are in fact *more* temporally coherent than
arbitrary regions. **Any claim that the raw dispersion is object-specific is refuted by this
control and must not be made.**

### (b) Per-track persistence — POSITIVE, and this is the result that survives

The frame-level common component is what a declared per-output scalar timestamp cancels, so
it is removed first: within each frame, centre `tbar_i` on the frame mean. The question is
whether the *residual* is a persistent property of the object.

102 tracks with >= 5 observations:

| quantity | value |
|---|---|
| between-track sd of the centred residual | **170.3 us** |
| mean within-track sd | 187.0 us |
| between-track sd expected if there were NO track effect | 37.6 us |
| **variance ratio, observed / no-effect** | **20.56x** |
| lag-1 autocorrelation along the track | **0.471** (99 tracks) |

An object's evidence-time offset relative to its frame-mates is autocorrelated at 0.47 from
frame to frame and has 20.6x the between-track variance that independent per-frame noise
would produce. **After the frame-level component is removed, per-object structure remains.**

This is the form of the `sigma_tau` claim that the review record's three hardest objections
do not reach: it needs no `sigma_c` (R7's +-20 %-flips-the-result), no ratio estimator
(R2's divergent variance), and it is not the permutation null whose direction R2, R7 and R10
all showed points the wrong way — the frame-level component is *removed by construction*
rather than tested for.

### (c) Positional control — POSITIVE: the offset is object-bound, not region-bound

The open question left by (b) was whether the persistence is *positional* — a region of the
image having a persistent evidence-time offset, which a track sitting in that region
inherits without owning a clock. Two tests, both on the same 6837 observations.

**Test 1: remove the mean residual of each image cell, then repeat the track test.**

| residual | tracks | between sd | no-effect sd | ratio | lag-1 |
|---|---|---|---|---|---|
| raw (frame-centred) | 102 | 170.3 us | 37.6 us | **20.56x** | 0.471 |
| minus 8x8 cell means | 102 | 157.1 us | 37.4 us | 17.64x | 0.451 |
| minus 16x16 cell means | 102 | 150.5 us | 37.5 us | 16.13x | 0.425 |
| minus 32x32 cell means | 102 | 143.3 us | 39.1 us | **13.45x** | 0.381 |

Removing image position at 32x32 granularity takes the track effect from 20.6x to 13.5x.
**At most about a third of the variance is positional; two thirds is not.**

**Test 2: does a track carry its offset with it as it crosses the image?** If the offset
were positional, tracks that move further would *decorrelate*. The opposite is observed.

| track group | n | lag-1 autocorrelation |
|---|---|---|
| low image displacement (< 235 px) | 49 | 0.152 |
| **high image displacement (>= 235 px)** | 50 | **0.567** |

**The confound check on Test 2.** A moving track might simply be a larger, closer, more
event-rich object whose `tbar` is better estimated, and lower measurement noise would inflate
autocorrelation on its own. It is not that: displacement and per-observation event count are
*negatively* correlated (r = -0.195), and the effect holds inside both event-count strata.

| event-count stratum | low displacement | high displacement |
|---|---|---|
| below median (4188 events) | -0.040 (n=24) | **0.479** (n=25) |
| above median | 0.437 (n=25) | **0.572** (n=25) |

**Conclusion.** The per-object evidence-time offset survives removal of the frame-level
component, survives removal of image position, and travels with the object. It is a property
of the object, not of the frame and not of the image region.

## What E08 does not establish

Only two sequences are measured, one per exposure stratum, so the support-scaling result in
(2) is a two-point contrast rather than a curve. The night result rests on one sequence.

Also outstanding: only two sequences are measured, one per exposure stratum. The
support-scaling result in (2) is a two-point curve and should be a curve.

## Reproduce

    docker run --rm -v $PWD:/work -w /work cvpr19-gpu-g1:torch2.7.1-cu128 \
      bash -lc "pip install -q h5py hdf5plugin; \
                python3 experiments/e09_per_object_evidence_time/measure.py zurich_city_09_a train"

CPU only. Needs `data/dsec/<seq>/events.h5`, `experiments/e00_exposure_survey/e_<seq>.txt`
and `data/dsec_det/<split>/<split>/<seq>/object_detections/left/tracks.npy`.

## (d) Flicker check — SUPERSEDED BY E10, AND WRONG

This section originally reported that no mains-flicker signature was present and treated the
night numbers as usable. **That was an error and it is kept here rather than deleted, because
the failure mode is instructive.**

The check took a 60-bin FFT of the event-rate profile *inside one 14 996 us exposure*. That
window has a bin spacing of 66.7 Hz, so a 100 Hz line falls between bins and **cannot be
resolved at all**. What was read as "a ladder of window harmonics, present in daytime too,
therefore an analysis artefact" was the window function itself. Absence of a resolvable line
was mistaken for absence of flicker.

`experiments/e10_flicker/` did it correctly, with a long window and a per-pixel Rayleigh test
against the analytic `Exp(1)` null: the night sequence's strongest line is at **100.00 Hz**
with a line ratio of 48 694, and **24.07 % of active pixels are phase-locked at p < 1e-3**,
240x the null rate. Two nulls validate the estimator (137 Hz on night, 100 Hz on day).

100 Hz is a 10 ms period inside a 14 996 us exposure, so flicker completes 1.5 cycles per
exposure and displaces per-object event-time centroids **with no motion at all**. The controls
in (a)-(c) do not rescue it: street lamps are static in the world and therefore move through
the image, so cell-mean removal cannot remove a lamp-phase effect; and the 50 001 us frame
period is 5.0001 flicker cycles, which manufactures the lag-1 autocorrelation that (b) read as
persistence.

**What to do:** re-measure using only the 76 % of active pixels that are not significantly
modulated. Until then the night number is unusable. The daytime arm is unaffected — day
matches the null at both frequencies — and its excess is zero.

The original (and incorrect) reading is preserved below for the record.

### Original section, superseded

## (d) Flicker and low-light-noise check — run because it is the largest threat to (a)-(c)

DSEC's own paper attributes high night event rates near street lamps to **flashing lights**,
and Graca & Delbruck (arXiv 2109.08640) show DVS noise rises in dim light. Either would
corrupt every night number above. `flicker_check.py`, 200 exposures per sequence.

| | night (zurich_city_09_a) | day (interlaken_00_c) |
|---|---|---|
| dominant frequency of the within-exposure rate profile | 200.1 Hz | 66.7 Hz |
| frequency ladder | 66.7 / 133.4 / **200.1** / 266.7 / 333.4 Hz | same ladder |
| exposures whose peak is within 10 Hz of 100 or 120 Hz | **0.000** | **0.000** |
| polarity, ON fraction | 0.482 | 0.528 |
| events on pixels firing >= 2x in one exposure | 0.839 | 0.162 |

Three readings, none of them conclusive on its own.

1. **No mains-flicker signature.** Swiss mains is 50 Hz, so flicker would appear at 100 Hz.
   **Zero** exposures peak near 100 or 120 Hz in either sequence.
2. **The periodic structure is an analysis artefact, not a light source.** The frequencies form
   the ladder 1x, 2x, 3x, 4x, 5x of 66.7 Hz, and 66.7 Hz is exactly one cycle per 14996 us
   exposure — i.e. the FFT window's own fundamental. The **same ladder appears in the daytime
   sequence with three times the power**, where street-lamp flicker is irrelevant. A physical
   flicker source would not behave this way.
3. **The events are spatially concentrated, which argues against shot noise.** 83.9 % of night
   events fall on pixels that fired at least twice within the same exposure. Uncorrelated shot
   noise over 307 200 pixels with 310 320 events would give about one event per pixel and a
   low repeat fraction. Polarity is near-balanced (0.482), as edge motion produces.

**Still owed before publication**, and this is the load-bearing wall for every night number in
E01 and E08: a denoiser ablation (recompute `tbar_i` after a standard DVS denoiser and report
the change), and a static-camera or stopped-vehicle segment as a motion-free control. Until
those exist, the night measurements are reported with this confound named.
