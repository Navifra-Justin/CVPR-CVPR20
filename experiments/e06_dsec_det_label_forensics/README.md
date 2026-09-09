# E06 — Are the released DSEC-Det labels interpolated? (measured 2026-09-01, main session)

This is the paper's own cheapest headline experiment ("E0, label forensics, a 4.7 MB file
and no GPU"), run now because two reviewers built arguments on assumptions about it.

Downloaded `dsec-det_left_object_detections.zip` (4 655 023 bytes) from
`download.ifi.uzh.ch/rpg/DSEC/detection/`. It expands to 60 `tracks.npy` files
(train + test), Prophesee dtype:

    ('t','<u8') ('x','<f4') ('y','<f4') ('w','<f4') ('h','<f4')
    ('class_id','u1') ('class_confidence','<f4') ('track_id','<u4')

390 118 boxes, 6 693 tracks, 60 sequences.

## Finding 1 — every released label sits on the 20 Hz frame clock

    label-time spacing (us):  min 40454   p1 49934   median 50001   p99 50049
    most common spacings:     49993, 49997, 50001, 50017, 50005, 49998, 49994, 50002
    fraction of spacings below 40 ms:  0.0000

**There are no sub-frame labels in this release.** Every label time is one frame period
from the next, and the spacings track the per-sequence frame period exactly (compare E00:
`interlaken_*` runs at 49997 us, `zurich_city_*` at 50001 us — the same two values dominate
here). The single 24.3 s maximum spacing is a track gap, not a label rate.

## Finding 2 — consecutive labels are not linear interpolants of each other

For every track, for every evenly spaced triple of consecutive labels, the middle box
centre was compared against the linear interpolant of its two neighbours:

| spacing | n | median residual | p90 | fraction below 0.01 px |
|---|---|---|---|---|
| 50 ms | 361 628 | **0.707 px** | 1.819 px | 0.071 |
| 100 ms | 469 | 1.118 px | 3.486 px | 0.021 |

If the labels were produced by linear interpolation between anchors, the residual at
interpolated positions would be ~0 and the "fraction below 0.01 px" would be near 1. It is
0.071. **The released labels are not interpolated from each other.**

## What this refutes, and what it leaves standing

**Refuted:** reviewer 8's round-one statement that "DSEC-Det inter-frame labels are pure
linear interpolation", *as a claim about this released file*. And with it, the premise of
reviewer 10's round-two killing review, which argues that moving the primary `tau_hat`
testbed to DSEC-Det "puts the headline measurement on labels that are, by E0's own finding,
linear interpolation", and derives from that a negative, frame-locked, resetting sawtooth
that would forge three headline results. **That mechanism cannot operate on these labels,
because these labels have no interpolated entries.** Reviewer 10's objection should be
re-examined against this measurement before the authors spend effort answering it.

**Left standing, and not addressed by this measurement:** whether the 20 Hz labels are
themselves the output of a detector run on RGB rather than human annotation. A second
difference of 0.71 px is what real annotation *and* real detector output both look like, so
this test cannot separate them. The "the ground truth is a model" claim — which is the
actual content of E0 and the paper's most defensible result — is untouched here and still
needs its own evidence, from the DSEC-Det paper's own description of its pipeline.

**Also unchecked:** interpolation may well exist in the *inter-frame evaluation protocol*
of the Nature 2024 work, where labels between frames are needed and must come from
somewhere. That would be a property of an evaluation procedure, not of this file. The
distinction matters and the paper must state which object it is talking about.

`dsec-det.zip`, the full release with images and events, is 87 888 596 740 bytes (87.9 GB)
and was not downloaded; only the label archive was needed for this.

## Provenance gap, flagged 2026-09-02

DSEC-Det is reported to ship **more than one annotation version** (an original release, and
a later revised set). This measurement read
`dsec-det_left_object_detections.zip`, 4 655 023 bytes, fetched on 2026-09-01 from
`download.ifi.uzh.ch/rpg/DSEC/detection/`, expanding to 60 `tracks.npy` files with
390 118 boxes and 6 693 tracks.

Which named release that corresponds to is **not established here**. Any statement in the
paper about "the DSEC-Det labels" must name the release and the checksum, because a
reviewer comparing against a different version would get different numbers. E08's noise
and autocorrelation results inherit the same caveat: they describe this file.
