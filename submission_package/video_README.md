# Paper video — CVPR20 (2026-09-09)

`CVPR20_paper_video.mp4`, **80.8 s**, 1280x720, 30 fps.

## The one thing a reviewer should remember

**A released recurrent detector has a newest-window occlusion-sensitivity centroid 23.81 ms
before the label instant, while the corresponding center displacement changes mAP by only
0.04 points on velocity-evaluable detections.**

## What this video cannot do, and does not fake

The standard this video is built against assumes a method paper: show the problem, show the
baseline failing, show Ours fixing it on the same scene. **This paper proposes no method.**
It measures properties of released artifacts, so there is no "Ours" and no baseline to beat,
and none is manufactured — inventing one would be the standard's own Critical case, a
performance difference exaggerated by presentation.

What the paper does have is two real contrasts, and both are shown as playback rather than
asserted:

- **detections held fixed while the ground truth is displaced** (scene 2), which is the
  paper's central claim in the benchmark's own units;
- **a ceiling-exposure recording against the daytime control** (scene 4), the same 15 ms of
  raw event stream on both sides, which is the contrast the label-side measurements rest on.

## Scenes, with the experiment each number comes from

| # | clip | length | what it shows | source |
|---|---|---|---|---|
| 0 | `v00_title` | 2.2 s | the paper title | — (item 0: 1.5–2.5 s) |
| 1 | `v02_support` | 17.0 s | **the primary novelty.** Real Gen1 input windows on a time axis; the measured per-bin occlusion influence fills in and the centroid lands at −23.81 ms; the axis opens to a second and the past windows appear with their measured influence, the running centroid sliding to −299 ms; the regression-based temporal coefficient is marked near the label instant | E45 (`e45_influence_fixed/result.json`), E42 (`e42_recurrent_support/result_k19.json`), E27 (`e27_rows/placebo_diag.json`) |
| 2 | `v04_map` | 12.5 s | **the consequence, on one real frame.** The released detections stay fixed while the ground truth slides to the state each object occupied δ later, with the measured mAP(δ) curve tracing beneath | E37 (`e37_map/dets.npz`, `strata.json`), E46b (`e37_map/at_centroid.json`) |
| 3 | `v01_exposure` | 11.4 s | **real playback** (item 21). Every event inside one published 14996 µs DSEC exposure, at ~3000× slow motion, beside the same events as a rate. The rate peaks twice per 100 Hz intensity period, which is why the strongest line is at 200 Hz | E00 (`e00_exposure_survey/e_zurich_city_09_a.txt`), DSEC-Det labels, E40 |
| 4 | `v07_ceiling_vs_day` | 18.0 s | **the climax, and the only controlled visual contrast this paper has.** The same 15 ms of raw event stream from a ceiling-exposure night recording and from the daytime control, the same 350 µs slices, the same slow motion, nearly the same event count (382 861 against 377 007) stated on screen. The rate varies **3.0×** on the left and **1.1×** on the right | `video/v07_stats.json`, DSEC events, E00 exposure metadata; the same contrast E10/E40 measure spectrally |
| 5 | `v05_harmonics` | 10.0 s | the identification: a whole recording's spectrum drawn left to right, lines arriving at 100, 200 and 300 Hz and nothing at 50, 150 or 250; then the line-to-continuum ratios, six ceiling sequences against the daytime one | E39 (`e39_which_frequency/sequence_spectrum.json`), E40 (`e40_harmonics/result.json`) |
| 6 | `v03_generality` | 6.0 s | generalization as evidence: the measured profile of each of the five released checkpoints on one axis, each with its own measured centroid, and the 1.24 ms band they occupy | E48 (`e48_matched_frames/rvt-*.json`), E47b (`e47_ssm/s5vit-*-chunked.json`) |
| 7 | `v06_closing` | 3.6 s | the scoped takeaway: newest-window sensitivity, velocity-evaluable center displacement, and mAP consequence | — |

Every rendered number is read from the artifact at render time, not typed into the plotting
code.

## Actual-evidence ratio, computed two ways

Reported under both readings, because the answer depends on whether a measured quantity
animated over time counts as actual evidence or as a graph.

| classification | scenes counted | seconds | share |
|---|---|---|---|
| **Strict** — only raw sensor or model output played back | scene 3, scene 4, the frame panel of scene 2, the input strip of scene 1 | 40.7 s | **50 %** |
| **By §25's own list**, which counts "controlled experimental playback" | scenes 1, 2, 3, 4 | 58.9 s | **73 %** |

Explanatory material — title, closing card, the two spectrum/profile scenes — is 21.8 s, 27 %.
No footage was padded to raise the ratio; scene 4 was lengthened because it is the strongest
actual evidence in the video, which is what item 20 asks for.

## Self-audit against the nine axes

- **actual evidence dominance** — the two longest scenes carrying new material are real
  playback (scene 4, 18.0 s) and the measured support on real input windows (scene 1, 17.0 s).
  No architecture diagram appears anywhere in the video; the paper has no architecture to show.
- **novelty alignment** — the primary claim is where a released detector's evidence sits and
  what the benchmark can see of it. Scenes 1 and 2 carry it and run 29.5 s of 80.8.
- **problem–result continuity** — scene 1 opens on the released window and closes on the
  measured output time without changing axis. Scene 2 uses one real frame for both the
  detections and the displaced ground truth. Scene 4's two panels are the same 15 ms.
- **direct comparability** — scene 4 is a true side-by-side: same span, same slice width, same
  slow motion, same marker size, each rate normalised to its own mean, which is stated on
  screen because the two recordings differ in absolute event rate.
- **temporal evidence** — every temporal claim is played, not stilled: the influence profile
  fills in over the window, the ground truth slides over δ, the events play inside the
  exposure, the rate oscillates.
- **evidence fidelity** — every number matches the manuscript, and `src/audit_numbers.py`
  checks the manuscript against the same artifacts the clips read.
- **mechanism clarity** — scene 2 shows *when* the effect is visible (the curve deepens with
  object speed) rather than only that it exists; scene 4 shows the illumination contrast that
  the label-side bound rests on.
- **interpretability** — one claim per screen; the two numbers that carry scene 4 are on
  screen with their semantic label ("rate varies 3.0×").
- **reviewer memory** — the closing sentence repeats the one thing.

## The §30 test

> "If every piece of actual experimental footage were removed and only the graphs, schematics
> and text remained, would the paper's message still come across?"

**No.** Scene 4's claim — that the ceiling recording's event rate oscillates and the daytime
control's does not — is a statement about what the raw stream does over 15 ms, and the
spectra in scene 5 summarise it but cannot show it. Scene 3 is the same: the 200 Hz structure
was found by drawing the rate, and it corrected a claim in the paper.

## What production caught that analysis had not

1. **A rate curve found a factual error.** A number summarised for weeks showed peaks 5 ms
   apart the moment it was drawn — 200 Hz, not the 100 Hz the paper claimed. The original
   spectrum searched a band fixed in advance at 90–110 Hz and could never have found it.
2. **A rounded number on screen.** 22.7 % had been rounded to 23 %. Corrected; every number
   on screen has to be the paper's.
3. **A sweep quoted over a curve that did not cover it.** The mAP scene said the whole sweep
   moves 0.9 points, the paper's figure over ±60 ms, while the curve beneath ran −50 to
   +30 ms and moved 0.37. The clip now computes the span of the curve it draws.
4. **The centroid moved.** E45 found that E17 and E34 handed the occluded pass the recurrent
   state their reference pass returned rather than the state entering the step. Scenes 1 and 2
   were re-rendered from the corrected artifact and now read their numbers from JSON at
   render time.

## What the video does not claim

It does not show a method being improved, because the paper proposes none, and it does not
show a baseline being beaten. The mAP scene shows a curve that is nearly flat and says so:
the finding is that the benchmark cannot resolve the interval, not that anything scores
better.
