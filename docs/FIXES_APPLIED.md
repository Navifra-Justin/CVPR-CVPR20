# FIXES_APPLIED — 2026-09-03

Applied to `paper/main.tex`, `paper/supplement.tex`, `paper/numbers.tex`,
`src/make_figs.py`, and the experiment records that the paper's numbers are read
from. Inputs: `docs/AUDIT_A_H.md` (items 1–87, 36 FAILs, 23-entry fix list),
`docs/AUDIT_88_197.md` (items 88–197 + G/S gates, 35 FAILs, 16-entry fix list),
`docs/CHECKLIST_197.md`, `docs/REFERENCE_PAPERS.md`, and the five measurements
made after the draft (E11 correction, E13, E14, E16, E17).

## Build state

| | |
|---|---|
| `main.pdf` | 9 pages — **body §1–§9 ends on p. 8**, references occupy p. 9 alone |
| `supplement.pdf` | 4 pages |
| Undefined references / citations | **0** in both documents |
| Undefined control sequences | **0** in both |
| Overfull/underfull boxes | **0** overfull in both |
| Rendered `[unmeasured]` in `main.pdf` | **0** |
| Rendered `[unmeasured]` in `supplement.pdf` | **6** — p. 1, one occurrence, in the sentence that declares the convention; p. 3, five cells of Table 1 (the tolerant diagnostic scores `AP⊥−AP`, `APiso−AP`, `R`, `AP⊥L−AP`, `E[cos²θ]`), which require detection runs that have not been made |

Compiled twice per document with `pdflatex` (TeX Live 2022) in
`cvpr19-tex:cvpr2026-v1`.

---

## A measurement defect found and fixed while applying the fixes

E11's correction note said the first run "never restricted events to `[a,b]`".
Re-running `experiments/e09_per_object_evidence_time/measure.py` with only an
`a <= t < b` filter added did **not** reproduce E11's corrected numbers
(206.6/93.0/183.6 became 204.4/95.3/179.6, and the frame-mean offset came out at
−497.6 µs against E16's −102.3 µs). Under the *suspect-new-runs* rule the gap was
treated as a bug and found: `/ms_to_idx` is indexed by whole milliseconds, so the
raw slice `[ms2i[floor(a)], ms2i[floor(b)])` **excludes** every event between
`floor(b)` and `b`. E11 and E16 extend the slice one millisecond past `b` before
filtering; `measure.py` did not. With that fixed, three independent scripts now
agree exactly: E09 gives 1134 frames / sd 206.6 / null 93.0 / excess 183.6 /
90.1 %, equal to E11's `result_exact.json` (`ALL`) and E12's `w = 14996 µs` arm,
and its frame-mean offset of −102.3 µs equals E16's `obj_offset_med_us`.

Consequences, all carried into `numbers.tex` and the figures:

- the **day** arm gains frames — 12 → **20** usable frames, sd 18.7 → **18.0**,
  null 23.9 → **21.6**, exposure 1524 → **1556** µs, 33 % → **35 %** of frames
  above null. The conclusion is unchanged: the day sd sits **below** its null and
  the excess is zero.
- random boxes: 1120 → **1123** frames, sd 338.4 → **338.2**, null 134.4 →
  **134.5**, excess 310.5 → **306.3** µs. Still larger than the labeled boxes'.
- p90 of the night sd 333.5 → **344.5** µs; peak-to-peak 601.6 → **563.9** µs.
- the E09 per-track statistics were recomputed on the corrected window by a new
  script, `experiments/e09_per_object_evidence_time/per_track.py`, which writes
  `per_track_zurich_city_09_a.json`. Direction unchanged, magnitudes moved:
  variance ratio 20.56× → **14.4×**, lag-1 autocorrelation 0.471 → **0.721**,
  ratio after removing 32×32 cell means 13.45× → **8.6×**, displacement split
  0.152/0.567 → **0.611/0.773** at a median path length of 278 px. The paper
  reports the recomputed values, not the README's first-run values.

`experiments/e09_per_object_evidence_time/README.md` now carries a correction
banner with the before/after table; `experiments/e14_pixel_scale/README.md`'s
stale column header (`displacement from 208.8 us`) was corrected to 183.6 µs.

---

## The five post-draft measurements, as carried into the paper

1. **E17 — the influence profile.** New §7.2, *The measured influence profile*:
   480 samples of the released Gen1 validation split with the released `rvt-t`
   checkpoint, recurrent state warmed eight steps, each of the ten 5 ms bins
   occluded in turn. Coefficient of variation across bins 0.034;
   influence-weighted centroid −24.94 ms against the uniform-weight −25.00 ms,
   a difference of +0.06 ms or 1.2 % of one bin width. The draft's hedge
   ("a reference point and not a prediction of network behaviour") is replaced by
   the measurement, and `\tauHatRVT` is no longer a placeholder. E17's own limits
   are stated in the body (occlusion measures sensitivity, which equals the
   linear weight only for a predictor linear in its bins; one checkpoint, one
   configuration, one dataset) and expanded in supplement §3.
2. **E11 correction.** Every affected macro re-sourced from
   `result_exact.json` (excess 208.8 → 183.6 µs, clean arm 180.6, random control
   182.9, 1134 frames, 90.1 %). **The duplicated Table 2 row is deleted**: the
   bottom block now lists 5000/10 000/20 000 µs only, and the caption states that
   the fourth width, 14 996 µs at 1.4996 periods, *is* the first row of the table.
3. **E13 — the noise floor, solved.** New §3 paragraph *Center noise* (moved
   there from §7.3, since it is a property of the labels and belongs with the
   label clock). It states the difference-order ladder, the two-rate elimination,
   σ_c = 0.4974 px total, the **0.1443 px integer lattice as a fact about the
   benchmark** ("The released boxes are stored as integers, so box centers lie on
   a 0.5 px lattice"), and the 0.476 px annotation component = 11.9 ms of timing
   at the median object speed. All "upper bound" language for σ_c is gone; what
   replaces it in Limitations is the true limit — the ladder is still decreasing
   at k = 7, so the total is an extrapolation. Table 1 now carries the three σ_c
   figures.
4. **E14 — the pixel scale.** New §4.2 paragraph *On the pixel scale*: 0.0073 px
   at the median object, 0.0275 at p90, 0.0661 at p99, i.e. 1.5 %–13.3 % of σ_c;
   the displacement reaches the 0.1443 px lattice component only at 786 px/s and
   the full 0.4974 px at 2709 px/s, against DSEC's p99 object speed of 360 px/s.
   The paragraph closes on what the measurement does and does not bound.
5. **E16 — the common offset.** New §4.2 paragraph *The common offset*:
   −16.8 µs over all events and −102.3 µs inside labeled boxes over 1811 night
   frames, both under 2 µs in daylight. Stated as evidence that DSEC's
   mid-exposure convention is accurate at this precision.

**The two-term framing** is now §7.4 *The two terms* plus **Table 3**: the
predictor's effective time (24.94 ms, property of a released configuration,
common to every object of one output, removable by declaring one number, declared
by no released detector) first; the intra-exposure dispersion (183.6 µs, differs
between objects of one frame, not removable by any declared number) second; the
factor of about 136 stated plainly; the pixel conversion beside both, with the
frame-common offset as the third row. The table caption states that no detection
score is computed and no accuracy gain is claimed from correcting any term.

---

## Audit FAILs addressed

### AUDIT_A_H (items 1–87)

| Item | What was done |
|---|---|
| 6 | "Frisch bracket" now glossed in supplement §1; Holm cited (`holm1979`); "Streamer" removed, now "the post-processing of [6]"; the antecedent for "the other five ceiling sequences" added — §3 and Table 1 state six of the eighteen sequences sit at the ceiling. |
| 10 | The 21-line "Labels." paragraph split into three (census / interpolation forensics / provenance). §7's masking algebra moved to the supplement; §7's scoring paragraph split and mostly moved. |
| 14 | Abstract numerals cut from 17 to 7 distinct values (window, frame period, sd, null, excess, one frame fraction, one pixel fraction). Not the 2–4 the item asks for — see *deliberately not done*. |
| 15 | **Every proportion in both documents is now a percentage** (`\...Pct` macros, all with `\,\%`). No bare fractions beside percentages. |
| 18 | Two-sentence bridge added before the contribution list. |
| 23 | `rethink3d2025` **read** (arXiv 2507.00190, Tanaka et al.) and described accurately: latency-aware AP + planning-aware AP, evaluated on nuPlan, pricing compute latency on named hardware; bibliography entry now carries the authors. Conclusion's plural attribution fixed. Abstract's daylight claim now says the sd *falls below* its null. |
| 32 | Not fixed — see *deliberately not done*. |
| 33, 86 | The pixel-scale conversion is now in the paper (§4.2 and Table 3). |
| 35 | Contribution list reduced to three bullets whose section references no longer straddle one another. |
| 36, 52, 62, 80 | The §5 and §6 limitation blocks deleted and merged into a single §8 that ends on the validity envelope ("Within those bounds the measurement stands without a detector, a checkpoint, a velocity denominator or an assumed label-noise level"). Every limit that existed is still stated, once. The unbounded concessions are bounded (the tracker-output limit now ends in what follows from it; the API-count limit is one clause). |
| 40, 66, 87 | "our null rather than our competitor" → "supplies the isotropic null of the supplement's diagnostic scores"; the LET-3D-AP priority aside deleted; the `faod2024` dismissal-by-venue rewritten neutrally; "no model is run" kept in the Fig. 1 caption only; the slide-closer sentence removed from that caption; "dropped rather than repaired" moved to the supplement. |
| 41, 148, 149 | Longest sentence 66 → 45 words; over 35 words 64/199 → 30/240; over 40 words 45 → 9. |
| 43 | Body prose semicolons 49 → **5**, colons 40 → **13**, em-dashes 14 → **0**. |
| 50 | "pricing" removed; heavy punctuation cut as above. |
| 53 | Both directions: the conclusion no longer attributes the 24.07 % line to "the same sequences"; σ_c is no longer downgraded to an upper bound when E13 has solved it; the affirmative per-track evidence is in. |
| 57 | All six contradictions: Table 2's duplicate row deleted; four → five ceiling sequences everywhere, with the antecedent supplied; the `rethink3d2025` assertion made true; "main Eq. 10" → a section reference; the supplement title made identical to the paper's; σ_c re-sourced to E13. |
| 58, 69 | "is not yet in place", "awaiting the detection runs", and the narrated withdrawal of the instrument's justification are out of the body (the withdrawal is stated once, in supplement §1, as a property of the estimator rather than as a correction of an earlier draft). |
| 59, 111(part) | **Figure 3 regenerated.** The two null levels moved from in-plot annotations into the legend, the x range tightened from (−0.5, 4.6) to (−0.55, 3.55), tick font 6.0 → 5.8, panel height 1.75 → 1.85 in. Verified by rendering the PDF at 400 dpi: no collision, nothing overprinted. Times-family fonts and grayscale-with-hatch preserved (`pdffonts`: STIXGeneral + NimbusRoman only). |
| 60 | One name for the day stratum; §4.1 now *defines* "dispersion" (the within-frame sd) against "excess" (the null-subtracted quantity); thousands separators applied to `21 142`, `14 996` in `numbers.tex` and to every grouped integer inside the figures (`grp()` in `src/make_figs.py`, using a plain space because Nimbus Roman has no U+2009 glyph); the abstract now says "evidence times", the term §4 defines, and Fig. 2's axis label was changed to match. |
| 61 | Table 2's block header parenthesized; Fig. 2's caption fragment made a sentence. |
| 64 | "Two checks fix…", "Two limits attach.", "Three limits attach to this arm.", "Two arms hold the estimator to its null." all removed. |
| 67 | All 35 British tokens converted (`center*`, `labeled`, `normaliz*`, `localiz*`, `canceling`, `synchroniz*`, `summariz*`, `gray`, `recognized`, `modeling`). Bibliography titles untouched. Verified by grep over both documents: 0 remaining. |
| 70 | Aggregate of 64/66/69/87 above. |
| 74 | Limitations now names the two controls the record calls owed: a denoiser ablation against `graca2021noise`, and a static or stopped-vehicle motion-free arm. |
| 75 | Both ledger entries repaired (see 23). |
| 77 | The non-monotonicity is now stated as a fact ("It is not monotone in the width, and how it varies with the width is not established here"); the 208.8/183.6 contradiction is gone. |
| 83, 84 | Not fixed — see *deliberately not done*. |

### AUDIT_88_197 (items 88–187, G, 188–197, S)

| Item | What was done |
|---|---|
| 90 | Three bullets, core measurement first, the predictor-side bullet worded as a measurement plus a bound rather than as an equal result. |
| 100, 101 | One surface name for `t̄_i`: "evidence time" in the abstract, the body and Fig. 2's axis. |
| 105 | The window arm's uncontrolled variables are stated as such, without the false monotonicity that used to justify them. |
| 106 | The integer lattice that the σ_c estimator's assumption violates is now stated in §3 and quantified in Table 1. |
| 111 (figure priority) | Partly — Fig. 3 fixed; the Fig. 1/Fig. 2 swap not done, see below. |
| 112, G10 | Table 2's duplicate condition removed; the random-box row's sample size corrected to its own measured value (1123 after the re-run, not `\sigmaEvtFramesNight`), via a new `\framesRandBoxes` macro. |
| 115 | "the removal of a quarter of the evidence" → "removing that many pixels", which is what was measured. |
| 122, 123, 133, 134, 136, 157, 160, 184, 187 | §7 rebuilt. The all-`[unmeasured]` Table 3 is replaced by a fully measured three-row table. §7.3's noise floor moved to §3. The masking algebra, the three estimates, the instrument, the chord term, the cross-fitting, `AP^bias`'s protocol, Holm, the comparison list and the re-binning check moved to the supplement. Body symbol count roughly halved; §7 now carries a measurement (E17) rather than a programme. |
| 124, 192, S5 | **"The excess grows with window width" deleted in both places** and replaced with what the numbers support. |
| 126 | The random-box control is now in the abstract and in the introduction. |
| 130 | Both reader inferences removed. |
| 131 | All three dangling cross-references repaired: "main Eq. 10" → a section reference; `E[cos²θ]` is now actually reported in the supplement (added to Table 1); the query-rate paragraph points at the supplement section that carries the scoring protocol. |
| 142 | Not specifically addressed — low severity, see below. |
| 163, 178 | Not fixed — needs a second ceiling sequence, see below. |
| 165 | E13's two facts are in the paper and the retracted MAD numbers are gone. |
| 167 | Not fixed — see below. |
| 191, S4 | "do not carry the effect" → "do not account for the effect"; "cannot buy a more permissive score" → "cannot widen the tolerance"; "the lever's range" removed with the paragraph it sat in. |
| 195, S8 | The four-number headline string no longer appears in eight places: the introduction and the contribution bullet carry the excess and the frame fraction only; the conclusion carries the sd/null pair and the excess. |
| 52/87 (affirmative evidence) | New §4.2 paragraph *Per-track structure*: 103 tracks, between-track sd 149.2 µs against 39.3 µs expected with no track effect (variance ratio 14.4), lag-one autocorrelation 0.721, ratio 8.6 after removing 32×32 image-cell means, and the displacement split 0.611 vs 0.773 at a median path length of 278 px — with the sentence that makes the split load-bearing ("A periodic image-plane effect that a stationary track inherits would run the other way"). |

---

## Deliberately not done, and why

1. **Item 14 — abstract to 2–4 numbers.** Cut from 17 to 7. Going to 4 would mean
   dropping either the null or the excess, and the null is what makes the excess
   meaningful; the paper's whole claim is a measured value against an analytic
   null. Judged as: the item's failure mode (a crowded, unreadable abstract) is
   gone, and further cutting would cost the claim.
2. **Items 32, 163, 178 — cross-dataset / cross-backbone / generalization rung.**
   Requires measuring a second ceiling sequence (E09/E11/E12 on another pinned
   DSEC sequence). This is compute, not editing, and the fix brief did not
   authorize new sequence runs. The paper states the gap twice and does not
   claim otherwise. This is the single highest-value remaining item.
3. **Items 111, 167 — promote Fig. 2 to the full-width slot and demote the
   exposure survey.** Not done. It requires redesigning both figures (Fig. 2 is a
   three-panel vertical column figure; Fig. 1's left panel carries eighteen
   sequence labels and does not survive a column-width reduction legibly), and
   the body is exactly at its 8-page budget with no slack to absorb a layout
   change. Fig. 3's legibility defect, which both audits raised alongside these,
   *is* fixed.
4. **Item 72 — final-objective alignment.** Still no AP number, because no
   detection run exists. Partly answered: Table 3 now quantifies, in pixels, what
   each term would move, which is the closest thing available without a run.
5. **Item 83 — lead §4.2 with the daytime stratum.** The audit marks it optional.
   Not done: the daytime arm is 20 frames, and leading with it would put the
   weakest sample first for a structural reason that the two-level exposure
   factor (§3) already explains.
6. **Item 84 — cross-task reuse.** Same root as 32/178.
7. **Item 106 (secondary) — name the DSEC-Det release and its checksum.** Not
   done: the archive is identified by byte size and retrieval date, and no
   release name or published checksum is resolvable from the repository. Adding
   a locally computed checksum would not identify the release to a reader.
8. **Item 142 — nominalization density.** Not specifically attacked. The audit
   itself notes the offenders are the paper's domain vocabulary (dispersion,
   measurement, illumination) rather than abstraction hiding an operation, and
   the sentence-length work already broke up the worst instances.
9. **σ_c printed to four significant figures.** E13 says the extrapolation is
   "worth about two decimal places, not three". The figures 0.4974 / 0.1443 /
   0.476 are printed as given, and the reason is stated once, in Limitations: the
   ladder is still decreasing at k = 7, so the total is an extrapolation rather
   than an observed plateau. A reader can round it; the decomposition is only
   legible at that precision.
10. **The E05 bin-masking probe** (synthetic input, backbone features, no
    recurrence) is no longer cited in the body. E17 measures the same thing on
    real data with recurrence, so the probe bounds nothing the paper now needs.
    Its macros remain defined in `numbers.tex`, unused.

---

## Files changed

- `paper/main.tex` — rewritten in full (structure, prose, tables, captions).
- `paper/supplement.tex` — rewritten; gained the estimator's three estimates, the
  chord term, the influence-profile protocol, the support-regression algebra, the
  scoring protocol, the reproduction gate, the declared fold rule, and `E[cos²θ]`.
- `paper/numbers.tex` — E11/E09 values re-sourced to the exact-window runs; E13,
  E14, E16, E17 and the per-track macros added; percentage forms added for every
  proportion; thousands separators unified; `\sigmaCsecond`/`\sigmaCthird`
  retired.
- `src/make_figs.py` — Fig. 3 right panel rebuilt; Fig. 2 x-axis relabeled and
  its middle panel's x-range fixed so no marker is clipped; grouped-integer
  formatting added to all four figures.
- `paper/figs/fig1–fig4.pdf` — regenerated.
- `experiments/e09_per_object_evidence_time/measure.py` — exposure-window slice
  fixed; a median-per-frame excess added to the summary.
- `experiments/e09_per_object_evidence_time/per_track.py` — new; writes
  `per_track_zurich_city_09_a.json`.
- `experiments/e09_per_object_evidence_time/README.md`,
  `experiments/e14_pixel_scale/README.md` — correction notes.
