# Paper video — CVPR20 (2026-09-16)

`CVPR20_paper_video.mp4`, **87.9 s**, 1280x720, 30 fps. Built by `video/build.sh` inside
`cvpr19-video:torch2.7.1-cu128`; every frame is rendered by a script in `src/v0*.py` that
reads its numbers from the experiment artifacts at render time.

## The one thing a reviewer should remember

**Moving only the chunk boundary of one released streaming evaluation --- same frames, same
weights, same labels, same evaluator, and the evaluated timestamp unchanged --- shifts S5-ViT-B
by 4.20 mAP points over all labeled boxes and 5.23 on the velocity-evaluable subset, so a
nominal benchmark timestamp does not identify the temporal support behind the score.**

## What this video cannot do, and does not fake

The standard this video is built against assumes a method paper: show the problem, show the
baseline failing, show Ours fixing it on the same scene. **This paper proposes no method.**
It measures properties of released artifacts, so there is no "Ours" and no baseline to beat,
and none is manufactured — inventing one would be the standard's own Critical case, a
performance difference exaggerated by presentation.

What the paper does have is three real contrasts, and all three are shown as playback or as
a measured curve arriving over time rather than asserted:

- **the chunk-position curve** (scene 3), the headline result, where the same released
  checkpoint scores differently depending on how much recurrent history the detection
  carries, with an RVT placebo drawn on the same axis;
- **detections held fixed while the ground truth is displaced** (scene 2), the central claim
  in the benchmark's own units;
- **a ceiling-exposure recording against the daytime control** (scene 5), the same 15 ms of
  raw event stream on both sides, which is the contrast the label-side measurements rest on.

## Scenes, with the experiment each number comes from

| # | clip | length | what it shows | source |
|---|---|---|---|---|
| 0 | `v00_title` | 2.2 s | the paper title | — (item 0: 1.5–2.5 s) |
| 1 | `v02_support` | 17.0 s | **predictor-side temporal support.** Real Gen1 input windows on a time axis; the measured per-bin window-ablation influence fills in and the centroid lands 23.81 ms before the label; the axis opens to a second and the past windows appear with their measured influence, the running centroid sliding to −299 ms; the regression-based temporal coefficient is marked near the label instant | E45 (`e45_influence_fixed/result.json`), E42 (`e42_recurrent_support/result_k19.json`), E27 (`e27_rows/placebo_diag.json`) |
| 2 | `v04_map` | 12.5 s | **the consequence, on one real frame.** The released detections stay fixed while the ground truth slides to the state each object occupied δ later, with the measured mAP(δ) curve tracing beneath | E37 (`e37_map/dets.npz`, `strata.json`), E46b (`e37_map/at_centroid.json`) |
| 3 | `v08_chunkpos` | 10.4 s | **the observational contrast.** mAP against the position of the detection inside the released evaluation chunk, one curve per released checkpoint, arriving position by position. The first four positions and the last five are shaded as they are named, then the difference-in-differences readout appears: S5-ViT-B +5.32 ± 0.53 points, S5-ViT-S +4.37 ± 0.61, RVT placebo largest of three 0.67 | E58 (`e58_chunkpos/curve.json`, `allbox.json`) |
| 4 | `v01_exposure` | 11.4 s | **real playback** (item 21). Every event inside one published 14996 µs DSEC exposure, at ~3000× slow motion, beside the same events as a rate. The rate peaks twice per 100 Hz intensity period, which is why the strongest line is at 200 Hz | E00 (`e00_exposure_survey/e_zurich_city_09_a.txt`), DSEC-Det labels, E40 |
| 5 | `v07_ceiling_vs_day` | 18.0 s | **the only controlled visual contrast this paper has.** The same 15 ms of raw event stream from a ceiling-exposure night recording and from the daytime control, the same 350 µs slices, the same slow motion, nearly the same event count (382 861 against 377 007) stated on screen. The rate varies **3.0×** on the left and **1.1×** on the right | `video/v07_stats.json`, DSEC events, E00 exposure metadata; the same contrast E10/E40 measure spectrally |
| 6 | `v05_harmonics` | 7.0 s | the identification: a whole recording's spectrum, lines at 100, 200 and 300 Hz and nothing at 50, 150 or 250; then the line-to-continuum ratios, six ceiling sequences against the daytime one | E39 (`e39_which_frequency/sequence_spectrum.json`), E40 (`e40_harmonics/result.json`) |
| 7 | `v03_generality` | 6.0 s | generalization as evidence: the measured profile of each released checkpoint on one axis, each with its own measured centroid, and the 1.24 ms band they occupy | E48 (`e48_matched_frames/rvt-*.json`), E47b (`e47_ssm/s5vit-*-chunked.json`) |
| 8 | `v06_closing` | 3.6 s | the scoped takeaway, with the 4.20-point all-box and 5.23-point velocity-subset shifts of the same-frame chunk-boundary intervention read from `paired.json` at render time | E60 (`e60_shift/paired.json`) |

Every rendered number is read from the artifact at render time, not typed into the plotting
code, including both cards in `src/v00_cards.py`.

## Actual-evidence ratio, computed two ways

Reported under both readings, because the answer depends on whether a measured quantity
animated over time counts as actual evidence or as a graph.

| classification | scenes counted | seconds | share |
|---|---|---|---|
| **Strict** — only raw sensor or model output played back | scene 4, scene 5, the frame panel of scene 2, the input strip of scene 1, the curve-arrival phase of scene 3 | 46.2 s | **52.6 %** |
| **By §25's own list**, which counts "controlled experimental playback" | scenes 1–5, less the 3.0 s closing beat of scene 1 | 66.2 s | **75.3 %** |

Explanatory material — title, closing card, the spectrum and profile scenes — is 21.7 s,
24.7 % under the second reading. No footage was padded to raise the ratio. Scene 6 was
trimmed from 10.0 s to 7.0 s when scene 3 was added, so that the added time went to measured
output rather than to a summary plot.

## Self-audit against the nine axes

- **actual evidence dominance** — the longest scenes carrying new material are real playback
  (scene 5, 18.0 s) and the measured support on real input windows (scene 1, 17.0 s), and the
  headline scene is a measured curve that arrives position by position rather than a summary
  bar. No architecture diagram appears anywhere in the video; the paper has no architecture
  to show.
- **novelty alignment** — the primary claim is what temporal support a nominal benchmark
  timestamp identifies. Scenes 1, 2 and 3 carry it and run 39.9 s of 87.9, or 45 %.
- **problem–result continuity** — scene 1 opens on the released window and closes on the
  measured output time without changing axis. Scene 2 uses one real frame for both the
  detections and the displaced ground truth. Scene 3 keeps one axis while all five curves
  and both shaded bands arrive on it. Scene 5's two panels are the same 15 ms.
- **direct comparability** — scene 5 is a true side-by-side: same span, same slice width, same
  slow motion, same marker size, each rate normalized to its own mean, which is stated on
  screen because the two recordings differ in absolute event rate. Scene 3 draws the RVT
  placebo on the same axis and in the same units as the S5-ViT curves.
- **temporal evidence** — every temporal claim is played, not stilled: the influence profile
  fills in over the window, the ground truth slides over δ, the chunk-position curve is drawn
  left to right, the events play inside the exposure, the rate oscillates.
- **evidence fidelity** — every number matches the manuscript, and `src/audit_numbers.py`
  checks the manuscript against the same artifacts the clips read (269 macros, 0 disagree).
- **mechanism clarity** — scene 2 shows *when* the effect is visible (the curve deepens with
  object speed) rather than only that it exists; scene 3 shows that the effect tracks the
  amount of recurrent history and vanishes in the placebo; scene 5 shows the illumination
  contrast that the label-side bound rests on.
- **interpretability** — one claim per screen; the numbers that carry each scene are on screen
  with their semantic label ("rate varies 3.0×", "1 to 4 windows of history").
- **reviewer memory** — the closing sentence repeats the one thing, and its numbers are the
  4.20 and 5.23 the manuscript's abstract, introduction and conclusion lead with; the 5.32 the
  chunk-position scene ends on is the observational contrast the same section of the paper
  reports alongside them.

## The §30 test

> "If every piece of actual experimental footage were removed and only the graphs, schematics
> and text remained, would the paper's message still come across?"

**No.** Scene 5's claim — that the ceiling recording's event rate oscillates and the daytime
control's does not — is a statement about what the raw stream does over 15 ms, and the
spectra in scene 6 summarize it but cannot show it. Scene 4 is the same: the 200 Hz structure
was found by drawing the rate, and it corrected a claim in the paper.

## What inspection caught, and what was done about it

Two Critical and two Major defects were found against the current manuscript and fixed before
this cut was built.

1. **Critical — the title card carried a title the paper no longer has.** Rewritten to
   "Temporal-Support Identifiability in Event-Detection Evaluation Pipelines".
2. **Critical — the closing card stated 0.06 where the manuscript reports 0.04.** The closing
   card no longer carries a hand-typed number at all: it reads the chunk-position result from
   `experiments/e58_chunkpos/allbox.json` at render time, so it cannot go stale again.
3. **Major — the paper's headline result was absent from the video.** Added as scene 3,
   `src/v08_chunkpos_clip.py`, 10.4 s, reading `curve.json` and `allbox.json`.
4. **Major — on-screen terminology had drifted from the manuscript.** "occlusion influence"
   and "newest window's centroid" became "window-ablation influence" and "ablation-sensitivity
   centroid" in scenes 1, 2 and 7.
5. Minor: British spellings on screen ("normalised", "centred"), two on-screen em-dashes and a
   semicolon in a scene title were removed; the three overlay labels in scene 2 were given a
   dark background box and moved inward, because grey text over bright event pixels was not
   legible; the centroid label in scene 1 printed "−23.81 ms before the label", a double
   negative, and now prints the magnitude.

## What production caught that analysis had not

1. **A rate curve found a factual error.** A number summarized for weeks showed peaks 5 ms
   apart the moment it was drawn — 200 Hz, not the 100 Hz the paper claimed. The original
   spectrum searched a band fixed in advance at 90–110 Hz and could never have found it.
2. **A rounded number on screen.** 22.7 % had been rounded to 23 %. Corrected; every number
   on screen has to be the paper's.
3. **A sweep quoted over a curve that did not cover it.** The mAP scene said the whole sweep
   moves 0.9 points, the paper's figure over ±60 ms, while the curve beneath ran −50 to
   +30 ms and moved 0.37. The clip now computes the span of the curve it draws.
4. **The centroid moved.** E45 found that E17 and E34 handed the ablated pass the recurrent
   state their reference pass returned rather than the state entering the step. Scenes 1 and 7
   were re-rendered from the corrected artifact and now read their numbers from JSON at
   render time.

## What the video does not claim

It does not show a method being improved, because the paper proposes none, and it does not
show a baseline being beaten. The mAP scene shows a curve that is nearly flat and says so:
the finding is that the benchmark cannot resolve the interval, not that anything scores
better.

## Typography

All on-screen text is set in Nimbus Roman, the metric-compatible Times New Roman clone
installed in `cvpr19-video:torch2.7.1-cu128`, with `mathtext.fontset=stix`.
