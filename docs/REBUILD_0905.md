# Rebuild of 2026-09-05 — the second move of the paper's centre of gravity

The draft of 2026-09-04 (see `RESTRUCTURE_0904.md`) led with the night evidence-time arm
and carried the spatial gradient of evidence time (E20) as its one surviving positive
result on that side. E25 and E26 retracted E20. This rebuild removes that arm's claim
entirely, promotes the predictor-side measurements to the first main result, and
generalizes the flicker finding from one sequence to all six.

Files touched: `paper/main.tex`, `paper/supplement.tex`, `paper/numbers.tex`,
`src/make_figs.py`, `src/make_fig_qualitative.py`, `src/e02_verify_window.py` (new),
`docs/PROTOCOL_LEDGER.md`, `experiments/e18_phase_subtract/README.md` (new).

---

## 1 — What left

### E20, the spatial gradient of evidence time

Retracted. `experiments/e20_spatial_gradient/README.md` carries the banner and the
evidence; `docs/PROTOCOL_LEDGER.md` entry 6 carries the five passes. In short: E25
generalized the measurement to all six ceiling sequences and found the alignment stronger
where objects move slower, which a per-object motion gradient cannot produce; E26 then
compared each box against an equal-area annulus of its own surrounding background, and the
paired difference goes negative in four of six sequences and, on the eroded object core,
in five of six, reaching `-0.178` at 6.2 SE in `zurich_city_01_a`. The signal is
ego-motion.

Removed from the paper:

- the section `\section{The spatial gradient of evidence time}` and its `sec:gradient`
  label;
- the four `Sec.~\ref{sec:gradient}` cross-references in the introduction, the
  contribution list, the end of the old Sec. 6, and the old limitations;
- the abstract sentence and the introduction paragraph built on the mean cosine;
- the conclusion's opening sentence, which was the gradient result;
- panel (c) of the qualitative figure, which drew the alignment against its two nulls;
- all sixteen `\grad*` macros. They are commented out under a retraction note in
  `numbers.tex` rather than deleted, so a later edit cannot silently resurrect one, and no
  text of either document can use one.

Verified: zero occurrences of `grad`, `cosine`, `sec:gradient` or any `\grad*` macro in
`main.tex` and `supplement.tex`, except the single limitations sentence that records the
attempt and its failure. That sentence is required — the arm was run, and a reader is
entitled to know what this data does not support.

### Material removed with it

- `fig4_integer_period()` in `src/make_figs.py`. It rendered E12's four analysis-window
  widths; E12 was retracted 2026-09-03 and the figure was already unreferenced. The
  function is replaced by a comment naming the retraction, and the rendered
  `paper/figs/fig4_integer_period.pdf` is deleted so that no figure of a retracted argument
  remains on disk.
- `fig2_evidence_time()` is no longer rendered by the default run; Fig. 4(a,b) supersedes
  it and it was already unreferenced.
- The supplement's *Estimator calibration*, *Scoring, uncertainty and the declared folds*,
  *Diagnostic scores* and *Manipulations outside the support regression* sections. All four
  described a detection-scoring programme that this paper does not contain: no detection
  score is computed anywhere in it. Their table held five of the six rendered
  `[unmeasured]` placeholders, and the sixth was the sentence in the supplement's opening
  paragraph announcing them.
- The `\apsync`, `\apbias`, `\apperp`, `\apperpl`, `\apiso` command definitions and the six
  `\TODOnum`-valued macros in `numbers.tex`, commented out under a note.
- The supplement's Holm reference, which nothing cites any more, and with it the
  supplement's bibliography.

---

## 2 — What replaced it

### The predictor side is now the first main result (main Sec. 3)

Three measurements, in the order they were run:

- **3.2, E02.** The window fact, verified in the released source rather than in a paper's
  description of it: `config/dataset/gen1.yaml` sets
  `stacked_histogram_dt=50_nbins=10`, and line 405 of `scripts/genx/preprocess_dataset.py`
  builds `ev_repr_timestamps_us_end` by counting backwards from label timestamps. E02 had
  no machine-written artifact, which both audits named as a provenance gap and which
  matters more now that the fact is load-bearing. `src/e02_verify_window.py` now reads both
  files and writes `experiments/e02_rvt_window_alignment/result.json`, and
  `\rvtSourceLine` comes from it.
- **3.3, E17.** The influence-weighted centroid, `-24.94 ms` against a uniform-weight
  reference of `-25.00`, coefficient of variation `0.034` across the ten bins, on 480 real
  Gen1 validation samples with the recurrent state warmed eight steps. Unchanged from the
  previous draft, promoted from Sec. 7.2 to Sec. 3.3.
- **3.4 and 3.5, E21 and E24.** E21 stays exactly what it was, the negative control: with
  box size as a third regressor and `corr(speed, size) = +0.349`, the temporal slope is
  `+11.9 ms` at 1.3 SE and the cross-track null is clean at 0.1 SE, which is what training
  on a window ending at the label time enforces. E24 is new to the paper: `|e_par|` and
  `|e_perp|` are fitted with the same four regressors and their coefficient vectors
  differenced, which cancels any effect raising both channels equally. The label-speed row
  gives `+0.0166 s` at 3.34 SE, an implied zeroth-order lag of `+16.6 ms`; the acceleration
  row gives `+0.0080 s^2`, an implied first-order lag of `126.9 ms`, longer than the 50 ms
  window, so the first-order account is excluded.

The paper states, in the introduction, in Sec. 3.5 and in the conclusion, that the
intercept and the box-size term carry larger anisotropic components (16.94 and 26.37 SE)
than the temporal one, and that the dominant component of the residual is geometric. The
claim is separability and significance, nowhere dominance.

### The flicker finding is generalized (main Sec. 4)

E10's per-pixel test on one night sequence stays as Sec. 4.2, with its two nulls and its
two denominators kept distinct. E25 supplies the new Sec. 4.3 and **Table 2**: all six
DSEC training sequences pinned at 14996 us, measured per labeled box over 16 516 boxes.
Median per-box Rayleigh statistic 114.58 against an analytic null of 0.693, 98.97 % to
100.00 % of boxes phase-locked at `p < 1e-3`, per-box modulation depth median 0.428 to
0.489 against a 0.125 floor, off-frequency arm at 137 Hz returning 4.01.

Sec. 4.4 then reports what that leaves of a per-object temporal statistic measured inside
one exposure window: the dispersion itself (E09/E11), the pixel-exclusion arm and its
matched random control, the random-position box control, and E19's dose-response from
93.1 to 208.0 us across quartiles of each box's own modulation, with the 137 Hz sham arm
rising too and the absent unmodulated stratum. The section closes with the pixel-scale
conversion (E14), which both audits named as the paper's largest single omission.

### Figures

| | before | after |
|---|---|---|
| Fig. 1 | — | `fig1_dsec_exposure.pdf`, exposure metadata, restored (it had been cut for page budget on 09-04) |
| Fig. 2 | — | `fig_predictor.pdf`, **new**: (a) the ten-bin influence profile with its SEMs, the mean over bins, the label instant and the centroid; (b) the four anisotropic differences in units of their own standard error |
| Fig. 3 | `fig3_day_night.pdf` | same, right panel rebuilt |
| Fig. 4 | `fig5_qualitative.pdf` | panels (a) and (b) kept, panel (c) replaced |

- **Fig. 2 is new** because the predictor arm is now the paper's spine and had no figure.
  E20's panel was the paper's only figure of a population result, and removing it left the
  lead result unillustrated.
- **Fig. 3's right panel was rebuilt.** Both audits recorded that its four x-tick labels
  overprinted in the rendered PDF (`night 100 Hz1 37 Hz1 00 Hz1 37 Hz`) and that the two
  reference lines struck through their own legend entries. It now carries two tick labels,
  night and day, with the tested frequency on the marker, medians with a whisker to p95,
  and the legend clear of the data.
- **Fig. 4(c)** now draws the six-sequence generalization: per sequence, the median per-box
  Rayleigh statistic at 100 Hz and at 137 Hz on a log axis against the Exp(1) null median.
  Panels (a) and (b) are the same real events and the same real per-box measurements as
  before, on the same median-dispersion frame of 602 candidates. Two rendering defects were
  fixed while regenerating: the frame was drawn without an equal aspect ratio, and the
  per-box evidence-time labels in (a) overlapped for the four clustered boxes and one was
  drawn outside the axes into panel (b). Boxes now carry an index and panel (b)'s tick
  labels carry the same index beside the event count.

`src/make_fig_qualitative.py` no longer opens
`experiments/e20_spatial_gradient/result.json`; its example-frame dump moved to
`experiments/e09_per_object_evidence_time/example_frame.json`.

---

## 3 — Judged too weak to keep, or deliberately not quoted

- **`r = -0.907`, the correlation between each sequence's gradient alignment and its
  fraction of objects above 20 px/s.** This is the observation that pointed at a
  scene-level cause and it is recorded in the E20 README and in the ledger, but it exists
  in no stored result file and cannot be re-derived from the artifacts on disk without
  re-running over the DSEC event data. The limitations section therefore rests on E26's
  paired box-minus-annulus numbers, which are in `experiments/e26_egomotion/paired.json`
  and are the decisive control in any case.
- **E23 as a separate subsection.** Its content is subsumed by E24's acceleration row,
  which is the same regression with the cross-track channel differenced rather than
  reported beside it. The paper keeps the honest statement, in Sec. 3.6 and in
  Table 1's caption, that the acceleration coefficient is more than an order of magnitude
  above `tau^2/2` and is significant on the cross-track channel as well.
- **The old Table 4, the three temporal terms on the pixel scale.** It converted a
  predictor term measured on Gen1 using DSEC-Det's speed percentiles. The conversions now
  live in prose, each on the split it was measured on: `0.65 px` for the E17 centroid at
  E21's median Gen1 label speed, `0.32 px` for E24's anisotropic term at its own median,
  and E14's `0.0073` to `0.0661 px` for the DSEC dispersion at DSEC-Det's speeds.
- **The evidence-time day/night contrast as a support contrast.** It remains a reported
  measurement with one limitations sentence, as decided on 09-04; exposure width and
  illumination move together and 20 usable day frames cannot carry more.
- **The instrumented errors-in-variables estimate.** Kept out of the paper and reported in
  the supplement only as an estimator whose justification does not hold on labels whose
  errors are not white.

---

## 4 — Verification

Compiled twice from clean, `cvpr19-tex:cvpr2026-v1`, after removing root-owned `.aux` and
`.pdf` left by an earlier container run (they silently blocked every non-root compile and
left a stale PDF in place, which is why the first checks of this session reported the
previous draft's page 6).

| check | result |
|---|---|
| `main.pdf` total | 9 pages |
| body | pages 1–8; the References heading is on page 8 and the list runs to page 9 |
| `supplement.pdf` | 3 pages, down from 5 |
| rendered `[unmeasured]` in `main.pdf` | **0**, on every page |
| rendered `[unmeasured]` in `supplement.pdf` | **0**, on every page (was 6) |
| `LaTeX Warning` in either log | 0 |
| undefined references, citations, control sequences | 0 |
| Overfull boxes | 0 in both documents |
| surviving references to the retracted gradient result | 0 claims, 0 macros, 0 cross-references; one limitations sentence that records the retraction |
| uncited `\bibitem`s / cites without a `\bibitem` | 0 / 0 |
| numerals in prose | none outside proper names (`Gen1`, `1 Mpx`, `3D`, `LET-3D-AP`, `Argoverse 2`, `Ev-3DOD`, `DSEC-3DOD`) and the percentile symbol `p95` |
| British spellings | 0 |

Cross-reference numbering used by the supplement, checked against `main.aux`: Eq. 1
`eq:outreg`, Eq. 2 `eq:tbar`, Eq. 3 `eq:excess`; Table 1 `tab:aniso`, Table 2 `tab:sixseq`,
Table 3 `tab:controls`; Sec. 3.1 definition, 3.3 `sec:influence`, 3.5 `sec:aniso`, 4.1
`sec:labelclock`, 4.2 per-pixel test, 4.4 `sec:cost`. Every `main Sec./Eq./Table` reference
in the supplement resolves to the intended target.

Every macro added in this rebuild carries a comment naming its experiment directory:
`\ani*` from `experiments/e24_order`, `\six*` from `experiments/e25_six_sequences`,
`\ego*` from `experiments/e26_egomotion`, `\rvtSourceLine` from
`src/e02_verify_window.py`, and the two derived pixel conversions naming both experiments
they multiply.

---

## 5 — Records corrected outside the paper

- `docs/PROTOCOL_LEDGER.md` row 2 said the mains-flicker confound was *"resolved at step 10
  (E20, spatial gradient)"*. That is now false. Row 2, the E20 bullet in section 2, and the
  stale claim in section 1 that E20 supplied steps 7–9 are corrected. No route to resolving
  the flicker confound stands, and the ledger now says so.
- `experiments/e18_phase_subtract/` had a `result.json` on disk and no README, while three
  other files retract it by name. It now carries its own retraction notice, so the
  `PHASESUB` excess of 311.2 us cannot be picked up by mistake.

---

## 6 — Open, and disclosed in the paper

- The standard error of each anisotropic difference is formed as if the two channel fits
  were independent. They run on the same matched boxes. Stated in Table 1's caption, in the
  limitations, and derived in supplement Sec. 3.
- The acceleration regressor is a difference of differences of label centers over a 50 ms
  base and carries the label noise of Sec. 4.1 amplified. Stated in the limitations.
- `sigma_c = 0.4974 px` is an extrapolation of a difference ladder still decreasing at
  `k = 7`. Stated in the limitations.
- The denoiser ablation against intensity-dependent event noise and a stopped-vehicle
  motion-free arm are both still unrun. Stated in the limitations.
- E23 has never had a pass of the 12-step protocol run against it. Recorded in the ledger
  as entry 5; the paper makes no claim that would need one.
