# AUDIT — Sections A–H (items 1–50) and items 51–87

Auditor scope: items **1–87 only**. Items 88–187 and gate sets G1–G12 / S1–S10 are another
auditor's. Sources read: `paper/main.tex` (995 lines), `paper/main.pdf` (9 pp.),
`paper/supplement.tex`, `paper/supplement.pdf` (3 pp.), `paper/numbers.tex`,
`paper/figs/fig1–fig4.pdf` (rendered at 200 dpi and inspected),
`docs/REFERENCE_PAPERS.md`, and all 14 READMEs under `experiments/e00…e13`.

Line numbers are `main.tex` source lines unless prefixed `p.` (compiled `main.pdf` page).
The six red `[unmeasured]` cells in Table 3 are out of audit scope by instruction; they are
named only where they are the direct cause of a specific criterion failing (items 58, 69).

---

## Summary

| Verdict | Count |
|---|---|
| **PASS** | **49** |
| **FAIL** | **36** |
| **N/A** | **2** |
| Total | 87 |

PASS: 1, 2, 3, 4, 5, 7, 8, 9, 11, 12, 13, 16, 17, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29, 30, 31,
34, 37, 38, 39, 42, 45, 46, 47, 48, 49, 51, 54, 55, 56, 63, 65, 68, 71, 73, 76, 79, 81, 82, 85.

FAIL: 6, 10, 14, 15, 18, 23, 32, 33, 35, 36, 40, 41, 43, 50, 52, 53, 57, 58, 59, 60, 61, 62, 64,
66, 67, 69, 70, 72, 74, 75, 77, 80, 83, 84, 86, 87.

N/A: 44 (no `i.e.` in the paper), 78 (no method with a cost is proposed).

### The five most consequential FAILs

**1. Item 33 / 86 — the headline number is never put on the paper's own pixel scale, and the
arithmetic a reviewer will do makes it look inconsequential.**
The paper measures an excess of 208.8 µs and supplies, in §7.3, everything needed to convert it:
"Median box-centre image speed on DSEC-Det is 40 px/s and the ninety-ninth percentile is 360 px/s"
(L669–671) and "σ_c = 0.4973 px" (L654). 208.8 µs × 40 px/s = **0.0084 px**; × 360 px/s =
**0.075 px**, i.e. **0.15 σ_c at the 99th-percentile object and 0.017 σ_c at the median**. The
paper performs exactly this conversion for a *different, 120× larger* quantity ("a 25 ms offset is
1.0 px at the median object and 9.0 px at the ninety-ninth percentile, about two and eighteen
times σ_c", L671–673) and never performs it for its own headline. A reviewer does this in ten
seconds and concludes the effect is two orders of magnitude below the label noise floor. The
omission reads as evasion whether or not it is.

**2. Item 57 — Table 2 reports the same night configuration twice with different numbers, and no
text explains the difference.**
Row 1: "Night, 14996 µs | 1133 | 229.5 | 93.4 | 208.8 | 0.9179" (L371). Row 7: "14996 µs
(1.4996 p) | 1134 | 206.6 | 93.0 | 183.6 | 0.901" (L382). Same sequence, same width, same
mid-exposure centre — 1133 vs 1134 frames, sd 229.5 vs 206.6, excess 208.8 vs 183.6 (a 12 %
gap). `experiments/e09` and `experiments/e12` produced these separately and neither README
reconciles them. Compounding: §5 says "the other **four** ceiling sequences" (L491) while §6
(L533) and §8 (L768) say "the other **five**"; `e00` establishes six pinned sequences and Fig. 1
shows six, so "five" is right and "four" is wrong.

**3. Items 52 / 62 / 87 — the strongest affirmative evidence in the experiment record is absent
from the paper while every caveat is present.**
`experiments/e09_per_object_evidence_time/README.md` reports a per-track structure —
"between-track sd of the centred residual | **170.3 µs**", "between-track sd expected if there
were NO track effect | 37.6 µs", "**variance ratio, observed / no-effect | 20.56x**", "lag-1
autocorrelation along the track | **0.471**" — and an image-displacement stratification —
"low image displacement (< 235 px) | 49 | 0.152" vs "**high image displacement (≥ 235 px) | 50 |
0.567**". None of this appears in `main.tex`. These are precisely the results that would answer
finding 1 above (the dispersion is motion-coupled and track-persistent, not noise). What the
paper keeps instead is the one control that runs against it — "an excess of 310.5 µs --- larger
than the annotated boxes'" (L446) — plus four separate limitation blocks.

**4. Items 23 / 75 — §2 asserts what a paper measures that the project's own record says was
never read.**
Main paper: "a latency-aware average precision inside LET-3D-AP's citation graph~\cite{rethink3d2025}
**measures device latency**" (L217–218). Supplement §7: "One returned title remains unread, and it
is the one whose framing could plausibly concern latency rather than multi-frame feature
aggregation." `experiments/e07` README: "*Rethink 3D Object Detection from Physical World* (2025)
… **It has not been read and it must be** before this check is cited as clean." The body states a
fact the supplement and the record both deny having.

**5. Items 41 / 43 — sentence length and heavy punctuation are far outside the range of any
reference paper.**
**64 of 199 sentences (32.2 %) exceed 35 words**; 45 exceed 40; the longest is **66 words**
(abstract, L52–59). Prose punctuation: **49 semicolons, 40 colons, 14 em-dashes** — one heavy
mark every 1.9 sentences. `docs/REFERENCE_PAPERS.md` sets the standard from five accepted CVPR
papers, none of which reads like this.

---

## Item-by-item

### A. Paper spine / core claim (1–5)

| # | Short name | Verdict | Evidence |
|---|---|---|---|
| 1 | One-sentence message | **PASS** | Conclusion opening, L789–794: "Inside a single published exposure window of DSEC, the event evidence belonging to different labelled objects is centred at measurably different times: a within-frame standard deviation of 229.5 µs against an analytic null of 93.4 µs, an excess of 208.8 µs, in 0.9179 of 1133 frames." One sentence, falsifiable, carries the number and the null. |
| 2 | Problem visible in first 3 sentences | **PASS** | Abstract sentences 1–2 (L47–52): "A detection benchmark indexes a label and a prediction with one scalar timestamp and scores their difference as displacement. The frame carrying the label integrates light over an interval the dataset publishes…" The mismatch is stated by sentence 2; sentence 3 states the job. |
| 3 | Core contribution on page 1 | **PASS** | Abstract on p. 1 carries the full headline (229.5 / 93.4 / 208.8 µs, 0.9179 of 1133 frames) plus the strength claim "No detector is run, no velocity divides a residual and no label-noise level is assumed" (L68–69). |
| 4 | Identity defined positively | **PASS** | L52–53: "We measure where inside one such interval the event evidence of each labelled object falls." Positive, declarative, names the measurement. |
| 5 | Contribution tied to problem structure, not a method trick | **PASS** | No method is proposed. The contribution is a property of how benchmarks index frames: L91–95, "the metric itself has no argument in which a time could appear, so a temporal discrepancy is scored as displacement." Bullet 1 (L158–160) defines a quantity, not a technique. |

### B. Reader comprehension flow (6–12)

| # | Short name | Verdict | Evidence |
|---|---|---|---|
| 6 | No assumed reader knowledge | **FAIL** | Three undefined, uncited terms. (a) "the **Frisch bracket**, with a sensitivity curve in the assumed variance ratio" (L626–627), repeated at L632 and in Table 3 (L744) — never defined, never cited. (b) "**Holm** corrected" (L722) — no definition, no citation. (c) "the **other five ceiling sequences** are unmeasured" (L533–534, L768) — the paper never states that six sequences sit at the ceiling; Table 1 gives only "Frames at the ceiling 6866 (32.5 %)", so "five" has no antecedent the reader can resolve. Also "the **Streamer** post-processing of~\cite{li2020streaming}" (L706–707) names a system the cited work's title does not. |
| 7 | Reader's question order | **PASS** | §1 runs: what a benchmark scores (¶1) → is this already known (¶2) → what we measure (¶3) → what we found (¶4) → is it flicker (¶5) → contributions. That is the order a reader asks in. |
| 8 | New concepts introduced after their necessity | **PASS** | "evidence time" appears at L335 only after L91–103 establishes why a per-object time is missing; "effective timestamp" is introduced at L563–566 with its necessity stated first ("The corresponding property of a predictor is its effective timestamp"). |
| 9 | Failure cause before method name | **PASS** | The indexing failure (L91–103) precedes the name "evidence time" (L335) by two pages. |
| 10 | One role per paragraph | **FAIL** | Three paragraphs carry three or more jobs. (a) L306–326 ("Labels.") does a label census, an interpolation forensic, a provenance caveat about tracker output, *and* an annotation-version caveat — 21 source lines, 5 sentences, 4 topics. (b) L679–700 does: why masking is not the support axis + the algebra + the released-weights probe + the probe's own disclaimer + the replacement instrument — 22 source lines. (c) L702–723 does: the transformation + its sign caveat + the cross-fitting + the AP^bias null + the uncertainty procedure — 22 source lines. |
| 11 | Paragraph endings generate the next question | **PASS** | L454–455 is the model: "The two strata differ in exposure width and in illumination, and illumination has a candidate mechanism of its own." — followed immediately by §5 on flicker. Likewise L268 → §3 "Labels.", and L455 → §5. |
| 12 | Physical example after abstraction | **PASS** | "auto-exposure ceiling" → 14996 µs (L251); "mains line" → "Swiss mains is 50 Hz and lamp intensity therefore flickers at 100.00 Hz" (L464–465); "phase" → "a lamp displaces the evidence time of the boxes near it by an amount set by its phase, with no motion involved" (L501–502). |

### C. Abstract / Introduction structure (13–20)

| # | Short name | Verdict | Evidence |
|---|---|---|---|
| 13 | Abstract opens on background or problem | **PASS** | L47–48: "A detection benchmark indexes a label and a prediction with one scalar timestamp and scores their difference as displacement." Background stated as the problem's premise; no field-praise opening. |
| 14 | 2–4 representative numbers in the abstract | **FAIL** | **17 numerals**: 118, 14996, 50 ms, 32.5 %, 229.5, 93.4, w²/12N, 208.8, 0.9179, 1133, 100.00 Hz, 0.2407, 10⁻³, 0.0008, 207.3, 207.5, 195.2, 246.8. Sixteen distinct macros are expanded in the abstract (`numbers.tex` expansion count). The permitted range is 2–4. |
| 15 | No mixed metric regimes in the abstract | **FAIL** | Four regimes and an internal inconsistency in how proportions are written: percent ("32.5 % of frames sit at the auto-exposure ceiling", L51–52) beside bare fractions ("0.9179 of 1133 frames", L59; "0.2407 of live night pixels", L62) for the same kind of quantity, alongside µs, ms, Hz and a p-value. |
| 16 | One mechanism and one main result clear | **PASS** | Mechanism: the evidence-time centroid and its analytic null, L52–58. Main result: 229.5 vs 93.4 µs, stated first and repeated verbatim in the Conclusion (L791–793). Distinguishable despite the crowding logged at item 14. |
| 17 | First page does not jump to high-level claims | **PASS** | §1 ¶1 (L91–103) is entirely mechanical — ρ(ŝ,s*), the query time, the two extents — with no claim of significance. |
| 18 | 2–3 sentence bridge before contributions | **FAIL** | The paragraph preceding "The contributions are:" (L155) is the flicker paragraph L143–153, which ends on a forward reference: "…cancel a periodic source exactly (Sec.~\ref{sec:controls})." There is no bridge sentence; the bullets begin cold on the next line. |
| 19 | Contribution bullets concise and parallel | **PASS** | Four bullets (L157–172), each an indefinite noun phrase of 3–4 lines: "a per-object evidence time…", "its within-frame dispersion…", "a measurement of that flicker…", "an operational definition…". Grammatically parallel throughout. |
| 20 | Contributions not overloaded with numbers | **PASS** | Six numbers across four bullets (208.8, 0.9179, 1133 in bullet 2; 0.2407, 4.67 %, 100.00 Hz in bullet 3). Two bullets carry none. This follows `docs/REFERENCE_PAPERS.md` §5 ("Where a bullet has a measured number behind it, put the number in the bullet"). |

### D. Precision of claims and terminology (21–27)

| # | Short name | Verdict | Evidence |
|---|---|---|---|
| 21 | Operational definitions for core terms | **PASS** | "evidence time" — Eq. 1, L338–341. "excess" — Eq. 2, L348–352. "phase-locked" — "Z = R²/N … is Exp(1) under uniform phase" with the p<10⁻³ threshold, L469–475. "effective timestamp" — "τ_P = Σ_k a_k c_k", L579–583. (The one umbrella term without an operational definition, "dispersion", is logged at item 60.) |
| 22 | Claimed vs not claimed is explicit | **PASS** | Four explicit non-claims: "Nothing here identifies the dispersion as specific to objecthood, and we make no such claim" (L449–450); "it is a different quantity from Sec.~4's and no result transfers between them" (L600–601); "so it bounds nothing about the effective timestamp" (L695–696); "no claim in Secs.~3--6 depends on them" (L733–734). This is the paper's strongest single discipline. |
| 23 | Claim strength matches evidence strength | **FAIL** | Three over-strength statements. (a) L217–218: "a latency-aware average precision … \cite{rethink3d2025} **measures device latency**" — supplement §7 and `e07` both record this paper as unread. (b) Conclusion L798–799: "**The same sequences** are shown to carry a 100.00 Hz line on 0.2407 of their live pixels" — 0.2407 is one sequence (`zurich_city_09_a`); the other sequence gives 0.0008. (c) Abstract L59–60: "**In daylight**, at an exposure an order of magnitude shorter, the dispersion sits at the null" — this rests on 12 usable frames of one sequence, and `e09` records the day arm as needing to "be redone with a lower event floor before it is cited as more than directional". |
| 24 | No overuse of every / all / only / must / cannot | **PASS** | Body counts: `every` 9, `all` 7, `only` 13, `must` 1, `cannot` 4, `never` 1, `always` 0. Nearly every `only` is restrictive rather than absolute ("only its width changed" L522; "only 7.1 % fall below" L314–315). The single `must` (L70) is about the estimator, not a claim. |
| 25 | First-claim not overstated | **PASS** | No "we are the first" anywhere. The novelty statement is scoped and negative: "None of these reads the released per-frame widths or measures what is inside one" (L234–235), with the search limits carried in §8 ("that count comes from one API call whose coverage is unknown", L784–785). |
| 26 | Strong words adjacent to evidence | **PASS** | "centred at measurably different times" is immediately followed by the colon and the four numbers (L790–794). "the strongest line between 90 and 110 Hz at 100.00 Hz … standing 10 841 above the … continuum" (L461–463). |
| 27 | Value not described only in negatives | **PASS** | The negation chain ("No detector is run, no checkpoint is loaded…", L131–132) is preceded by the positive definition (L123–130) and the four positive contribution bullets (L158–171). |

### E. Experimental design and defensibility (28–36)

| # | Short name | Verdict | Evidence |
|---|---|---|---|
| 28 | Most natural objection blocked first | **PASS** | The most natural objection to a night-sequence timing effect is mains flicker, and §5–§6 (L457–558, two full sections) are that objection, placed immediately after the measurement. Second objection (small counts) is pre-empted by the analytic null in the definition itself (L344–352). *Minor gap:* Fig. 2's middle panel shows all eight objects at −270 to −1060 µs, i.e. a large frame-common offset (`e09`: "−862 µs"), which the text never mentions. |
| 29 | Simple and strong baselines both compared | **PASS** | Simple: the analytic null w²/12N_i, per frame (L344–352). Strong: the integer-period cancellation, which removes a periodic source "whatever its amplitude, its phase or how many pixels carry it" (L518–520) without needing to identify affected pixels. Plus a random-box control, a matched random-pixel exclusion, an off-frequency arm and a daytime arm. |
| 30 | Negative result supports the paper's logic | **PASS** | The random-box control returns a *larger* excess (310.5 vs 208.8 µs, L446) and the paper uses it correctly rather than burying it: "The dispersion is therefore a property of where evidence falls in the image during the exposure" (L447–448). The day stratum's zero excess is likewise reported as the null-side of the contrast. |
| 31 | External reference exists | **PASS** | `docs/REFERENCE_PAPERS.md` names and verifies five external accepted papers (FVD content-bias CVPR 2024, Time Blindness, Generative Image Dynamics, Beyond Duality CVPR 2026, EvRT-DETR) with CVF listing verification. Inside the paper, Waymo `label.proto`, LET-3D-AP and Qin & Shen serve as the external standards. |
| 32 | Cross-dataset or cross-backbone validation | **FAIL** | One dataset (DSEC), two sequences, zero backbones evaluated. §7 names RVT (L594) but produces no number from it; all six Table 3 cells are `[unmeasured]`. The paper itself concedes the scope: "The evidence-time result is one night sequence at one exposure setting and 12 usable day frames at the other" (L762–763). |
| 33 | Metric connected to practical meaning | **FAIL** | See Summary finding 1. §7.3 converts 25 ms into pixels and σ_c units (L669–673) but the headline 208.8 µs is never converted anywhere in the paper, in any unit a benchmark consumer uses (px, IoU, AP). The paper supplies both multipliers it would need (40 and 360 px/s, L670–671) on the same page. |
| 34 | Different experiments' numbers explained to the reader | **PASS** | The one genuinely confusable pair is separated twice and explicitly: "That is a property of a predictor, not of the sensor evidence inside a label's exposure window, so it is a different quantity from Sec.~4's and no result transfers between them" (L598–601), and Table 3's caption, "σ_τ is the dispersion of a *predictor's* effective timestamps and is not the evidence-time dispersion of Table~2" (L753–756). |
| 35 | Results presented in claim order | **FAIL** | Contribution bullet 2 (L161–164) bundles the controls and cites "Secs.~4--6", spanning bullet 3's own section; bullet 3 (L165–167) is the flicker measurement in Sec. 5. So bullet order is 4 → (4,5,6) → 5 → 7 while section order is 4 → 5 → 6 → 7. The bullet list and the body disagree on which result comes second. |
| 36 | Limitations organised as boundaries, or removed | **FAIL** | See items 52 / 62 / 87. §8 mixes genuine boundaries ("σ_c = 0.4973 px is an upper bound, since real jerk enters the third difference", L772–773) with open confessions that bound nothing ("that count comes from one API call whose coverage is unknown", L784–785; "cannot say whether its labels are tracker output", L773–774). Limitation prose also appears in three other places (L489–495, L533–539, L554–558). |

### F. Related work and section headings (37–40)

| # | Short name | Verdict | Evidence |
|---|---|---|---|
| 37 | Related-work heading is a neutral noun phrase | **PASS** | `\section{Related work}` (L174). No qualifier, no slogan. |
| 38 | No explanatory sentences or slogans in headings | **PASS** | All headings are noun or gerund phrases: "The label clock of DSEC", "Per-object evidence time", "Mains flicker in DSEC night sequences", "Controls against mains flicker", "The effective timestamp of a predictor", "Definition and null", "Measurement", "Estimator", "The label noise floor", "Support manipulation and scoring", "Per-object time in labels.", "Decomposing localisation error along a privileged axis.", "Recovering a time offset from image-plane displacement.", "Event benchmarks and their exposures.", "Exposure.", "Convention.", "Labels.", "Excluding phase-locked pixels.", "Integer-period windows." No sentence, no slogan, no question mark. |
| 39 | Related work: category → prior work → difference | **PASS** | ¶1 (L176–187): category ("Per-object time in labels") → Waymo, LET-3D-AP, Nuñez → difference ("Each of these computes a per-object time in order to remove it. The quantity reported here is the dispersion itself…"). ¶4 (L222–242): category → Gen1, 1 Mpx, DSEC-Det, Ev-3DOD, REFID, RENet → "None of these reads the released per-frame widths or measures what is inside one." |
| 40 | Difference from competing methods not written defensively | **FAIL** | Three defensive constructions in §2. (a) L199–200: "the response of average precision to isotropic box perturbation~\cite{apsensitivity2022} is **our null rather than our competitor**" — frames a cited work in competitor terms, which no reference paper does. (b) L205–206: "that is the estimator of Sec.~7, **published in vision four years before LET-3D-AP**" — a priority aside inserted into a related-work description. (c) L218–220: "An **unrefereed preprint** names the event--RGB frequency mismatch~\cite{faod2024} **but reports plain average precision**" — dismissal by venue plus a "but". |

### G. Sentence length and readability (41–45)

| # | Short name | Verdict | Evidence |
|---|---|---|---|
| 41 | Sentences over 35 words checked | **FAIL** | Computed over 199 body-prose sentences (abstract + §1–§9, floats excluded): **64 sentences (32.2 %) exceed 35 words**, 45 exceed 40, maximum **66 words**. Mean 26.5, median 24. Full enumeration in *Mechanical scans → G1*. |
| 42 | No more than one contrast per sentence | **PASS** | Exactly one sentence in the body carries two contrast markers: L193–195, "We import all four devices in Sec.~7, with the object's velocity **in place of** the sensor's line of sight and a tolerance read off a declared and a measured temporal support **rather than** swept." The two are parallel, not competing, and the sentence reads cleanly. |
| 43 | `;`, `—`, `:` not overused | **FAIL** | Body prose: **49 semicolons**, **40 colons**, **14 em-dashes** — 103 heavy marks across 199 sentences, one every 1.9 sentences. Three sentences carry a colon *and* two semicolons (L429–441, L621–633, L702–723). One paragraph (L196–200) carries three semicolons in a single sentence. Enumeration in *Mechanical scans → G3*. |
| 44 | `i.e.` used correctly | **N/A** | `grep -c 'i\.e\.'` over the body = **0**. `e.g.` = 0. Nothing to judge. |
| 45 | Referents of this / it / which are clear | **PASS** | Nine candidate sites checked individually; all resolve on one reading. "It is one sequence" (L533) ← "this arm" in the immediately preceding sentence. "That is a property of a predictor" (L598) ← "the induced spread of effective timestamps". "This is an upper bound" (L656) ← σ_c. Five `, which` clauses (L257, L319, L494, L688, L774, L781) all attach to the nearest full noun phrase. The loosest is L256–258, "…a two-level factor that can be switched between strata but not swept, **which** fixes the design of Sec.~4" (clausal referent), and it still resolves. |

### H. Parentheses, quotes, parentheticals (46–50)

| # | Short name | Verdict | Evidence |
|---|---|---|---|
| 46 | No core claim inside parentheses | **PASS** | Eight prose parentheses in the whole body (enumerated in *Mechanical scans → H1*). Six are pure cross-references ("(Fig.~1)", "(Sec.~6)"). The two with content — "(207.3 µs, against 207.5 µs for a matched random exclusion)" (L64–65) and "(0.581 at an off-frequency on the same events, 0.719 at 100.00 Hz in daylight)" (L147–149) — are corroborating figures for a claim already made in the main clause. |
| 47 | Not too many parentheses per paragraph | **PASS** | Maximum per prose paragraph is **2** (L143–153 and L429–441). No paragraph exceeds two. Counted with inline math and LaTeX command arguments stripped. |
| 48 | No raw double quotes | **PASS** | `grep '"'` over the body: **0 hits**. The only `''`/```` `` ```` sequences are the math primes of `$(f''h^{2})^{2}$` and `$(f'''h^{3})^{2}$` (L650–651). |
| 49 | Logic survives deleting the parentheses | **PASS** | Tested on both content-bearing parentheses. L63–65 without the parenthetical: "The dispersion survives excluding those pixels and survives integration over an integer number of mains periods" — intact. L146–149 without it: "Two off-null arms of the same estimator return the null." — intact. |
| 50 | Colloquial / presentation-register expressions searched and removed | **FAIL** | Greps run on `main.tex` (full output in *Mechanical scans → H2*). Live hits: **`because` ×3** (L99, L467, L630); **`The reason` ×1** (L232); **`;` ×49**, **`---` ×14** (both flagged by the item's own list and by item 43). Near-hit not caught by the literal pattern: "reproduces that optimism rather than **pricing** it" (L712) — the metaphorical `price` register the item targets. Zero hits for `This is not`, `We do not`, `The point is`, `cleanly`, `curiosity`, `sacrifice`, `Why no`, raw `"`, `i.e.` |

### Items 51–70

| # | Short name | Verdict | Evidence |
|---|---|---|---|
| 51 | 8-page limit | **PASS** | Verified against `main.pdf`, not the source. `pdfinfo`: 9 pages. Per-page `pdftotext`: body §1–§9 occupies pp. 1–8; "9 Conclusion" and its final sentence sit in the right column of **p. 8**; "References" begins in the same column and runs to p. 9. Body = 8 pages, references excluded. Geometry check, since `cvpr.sty` is present in `paper/` but never `\usepackage`d: this draft's text block is 6.78 × 9.00 in = **61.02 in²**; CVPR's is 6.875 × 8.875 in = **61.02 in²** — identical area, so the page count is robust to switching to the real class (line breaks will shift; the count will not). |
| 52 | Strengths emphasised, limitations minimised or removed | **FAIL** | Limitation prose totals ~**40 source lines across four locations**: §5 ¶3 (L489–495, "Two limits attach."), §6 ¶3 (L533–539, "Three limits attach to this arm."), §6 close (L554–558), and all of §8 (L762–785, 24 lines). `docs/REFERENCE_PAPERS.md` measures the five accepted references at 5–8 lines each, in one place. Against that, the strength statements total three sentences (L68–69, L131–132, L795–796), and the strongest available strengths — `e09`'s 20.56× per-track variance ratio and the 0.567-vs-0.152 displacement stratification — are omitted entirely. |
| 53 | Generality claim matches the evidence (both directions) | **FAIL** | **Overclaiming.** (a) Conclusion L798–799: "**The same sequences** are shown to carry a 100.00 Hz line on **0.2407** of their live pixels" — plural, but 0.2407 is `zurich_city_09_a` alone; `interlaken_00_c` gives 0.0008 (L480). (b) Conclusion L789: "Inside a single published exposure window **of DSEC**" — unqualified dataset attribution for a one-sequence result. (c) Abstract L59–60: "**In daylight**, at an exposure an order of magnitude shorter, the dispersion sits at the null" — a generic claim on 12 frames, and the sd (18.7) is 22 % *below* the null (23.9), not at it. **Underclaiming.** The one-sequence boundary is restated **five times** (L490–491, L533–534, L555–556, L762–763, L768–769), and §8 downgrades σ_c to "an upper bound" (L772) although `experiments/e13_difference_ladder` has since solved it — "sigma_total → 0.4974 px", decomposed into "sigma_annotation = 0.476 px" plus a "0.144 px quantization floor" from DSEC-Det's integer box storage. The paper is simultaneously broader than its evidence in the abstract and conclusion, and narrower than its evidence in §7.3 and §8. |
| 54 | Unnatural nominalisations checked | **PASS** | No invented capitalised compounds of the "Directional Unsafety" type. All coined terms are lower-case descriptive noun phrases with definitions attached: "evidence time" (Eq. 1), "effective timestamp" (L579), "label clock" (§3 title, operationalised at L307–308 "every label sits on the frame clock"), "analysis window" (L521–522). |
| 55 | Number–percent spacing | **PASS** | All **10** occurrences of `\%` use the thin space `\,\%`: L51, 166, 250, 262, 282, 288, 315, 475, 485, 508. Rendered consistently as "32.5 %", "4.67 %", "7.1 %", "100.00 %". No mixed forms. (Note for item 67: the thin space *before* % is the SI/British convention; American house style sets "32.5%". Consistency is met; the convention choice compounds the item-67 finding.) |
| 56 | British/American mixing avoided | **PASS** | Not mixed — the paper is **consistently British**. Zero American variants in prose (the seven `center` hits are the LaTeX command `\centering`; "parameter" is not a variant). Full list at *Mechanical scans → M2*. Item 56 asks about mixing and is satisfied; item 67 asks for American and is not. |
| 57 | No contradictions between sections | **FAIL** | Six. (1) **"four" vs "five" ceiling sequences**: L491 "the other four ceiling sequences" vs L533–534 and L768 "the other five"; Fig. 1 shows six pinned sequences, so "four" is wrong. (2) **Table 2 reports the 14996 µs night arm twice with different values**: L371 (1133 / 229.5 / 93.4 / 208.8 / 0.9179) vs L382 (1134 / 206.6 / 93.0 / 183.6 / 0.901); no text distinguishes them. (3) **Main §2 vs supplement §7 on `rethink3d2025`**: body asserts it "measures device latency" (L217–218), supplement says "One returned title remains unread". (4) **Supplement cites "main Eq.~10"** (`supplement.tex`, §2 "Estimator calibration") — `main.tex` contains exactly three numbered equations (L338, L348, L610). (5) **Titles differ**: `main.tex` L37 "Evidence Time Within a Single Exposure" vs `supplement.tex` "Per-Object Evidence Time Within a Single Exposure". (6) **§8's σ_c framing is superseded** by `experiments/e13`, whose README states of the earlier run "Any number taken from that first run should be discarded." Minor: abstract L60 "the dispersion sits at the null" for a day sd 22 % below its null. |
| 58 | No research-note register | **FAIL** | L565–566: "its measurement on released checkpoints **is not yet in place**" — prose, not a placeholder macro. Table 3 caption L751–752: "…on released checkpoints, **awaiting the detection runs**." L629–631: "That instrument **was justified** by disjointness implying independent errors, and **that justification does not hold here**" — a lab-notebook correction narrated in the body. |
| 59 | Figure text legibility and overlap | **FAIL** | **Fig. 3, right panel**: the four x tick labels collide — rendered at 200 dpi they read "100 H**137 H**00 H**137 Hz**", i.e. "100 Hz" and "137 Hz" overprint at every tick. The in-plot annotations "null p95" and "null median" are also struck through by their own dashed reference lines and run into the axis frame. Figs. 1, 2 and 4 are clean at print size; Fig. 1's right-panel annotation "0 frames between 4207 and 14996 µs" sits partly over the shaded band but remains legible. |
| 60 | Internal terminology consistency | **FAIL** | Four drifts. (a) **The day stratum has four names**: "In daylight" (L59), "the daytime stratum" (L138–139), "Day, 1524 µs" (Table 2, L372), "the narrow-exposure stratum" (L794). (b) **"dispersion" is used for two different quantities** — the within-frame sd ("the dispersion sits at the null", L60) and the null-subtracted excess ("Mains flicker does not account for the dispersion", L554–555) — 20 occurrences, no operational definition. (c) **Thousands separators are applied inconsistently**: `10\,000`, `20\,000`, `35\,990`, `390\,118`, `70\,379`, `629\,442`, `361\,628`, `50\,001`, `14\,334`, `17\,800`, `10\,841`, `4\,655\,023` all take the thin space, but `21142` (L253, Fig. 1 caption) and `14996` (throughout, incl. Table 2 row 7 beside "10 000" and "20 000") do not. `experiments/e00` itself writes "21 142" and "14 996". (d) **The headline object is renamed in the abstract**: "the evidence-weighted time centroids" (L54) for what §4 calls "the evidence time". Plus the main/supplement title mismatch logged at item 57. |
| 61 | No semicolons without sentence separation | **FAIL** | Two. Table 2 header, L379: "*Night window width**;** \wOnePeriod{} and \wTwoPeriod{} cancel flicker*" — a noun phrase joined by semicolon to a clause. Fig. 2 caption, L408–409: "…each frame's own analytic null $w^{2}/12N_{i}$**;** medians 229.5 and 93.4 µs." — right side is a fragment. (The 47 other semicolons all join independent clauses; their *volume* is item 43's finding, not item 61's.) |
| 62 | Strengths emphasised, limitations minimised (second gate) | **FAIL** | Same evidence as item 52. Reading §8 as a whole: it opens with a concession, contains nine concessive clauses, and closes on "that count comes from one API call whose coverage is unknown" (L784–785). Register is flat rather than apologetic — there is no "unfortunately" and no self-deprecation — but the *shape* is a confession list, not a validity envelope: the section never states what the result **does** license. A boundary paragraph would end with the envelope; this one ends with a methodological apology about an API call. |
| 63 | Academic register; no promotional tone | **PASS** | Zero hits for `novel`, `significant`, `dramatic`, `striking`, `remarkable`, `crucial`, `key insight`, `we believe`, `notably`, `importantly`, `clearly`, `of course`, `indeed`, `in fact`, `surprisingly`, `state of the art`, `community`. The single evaluative adjective in the body is "a **widely used** night driving sequence" (L483), which is defensible. |
| 64 | No meta sentences | **FAIL** | Three instances of the enumerate-then-list pattern the item names. L261: "**Two checks fix** what the indexed timestamp denotes." L489–490: "**Two limits attach.**" L533: "**Three limits attach to this arm.**" Also L476: "**Two arms hold** the estimator to its null:" and L625: "**Three estimates are reported** side by side:". |
| 65 | No presentation-style prose | **PASS** | Prose is declarative and measured throughout. Sentences are long (item 41) but none is oral-register; there are no rhetorical questions, no direct address, no "let us", no imperatives to the reader. |
| 66 | No slide / rebuttal / oral-explanation sentences | **FAIL** | Four rebuttal-register constructions. L199–200: "…is **our null rather than our competitor**." Fig. 1 caption, L85: "Read from the dataset's own files; **no model is run**." Table 1 caption, L300: "…retrieved 2026-09-01); **no model is run**." — the same pre-emption twice in captions. Fig. 1 caption, L84–85: "**Every consumer addresses such a frame with one scalar timestamp.**" — a slide-closer assertion in a metadata caption. |
| 67 | American English verified, British register removed | **FAIL** | **35 British-only spellings** in the body. `centre`/`centres`/`centred` ×11 (L313, 452, 521, 544, 580, 606, 616, 648, 669, 681, 790); `labelled` ×6 (L53, 124, 225, 333, 429, 790); `normalis*` ×4 (L570, 619, 685, 688); `localis*` ×3 (L189, 190, 198); `cancelling`/`non-cancelling` ×3 (L528, 529, 530); `synchronis*` ×2 (L179, 265); `summaris*` ×2 (L359, 389); `grey` ×2 (L78, 223); `recognised` ×1 (L106); `modelling` ×1 (L203). American forms required: center/centers/centered, labeled, normaliz*, localiz*, canceling/non-canceling, synchroniz*, summariz*, gray, recognized, modeling. Note `analysis`/`analytic` are correct in both and are **not** in this list. |
| 68 | Academic register; paragraph transitions sound | **PASS** | Transitions are explicit and earned: L454–455 into §5; L497–504 opens §6 by restating the mechanism it must exclude; L563–566 opens §7 by separating its quantity from §4's. No abrupt starts. (Spelling register is item 67's finding, not this one's.) |
| 69 | No open confession | **FAIL** | Five. L565–566: "its measurement on released checkpoints is not yet in place." L629–633: "That instrument was justified by disjointness implying independent errors, and that justification does not hold here … the instrumented value is reported beside them rather than as the headline." L695–696: "so it **bounds nothing** about the effective timestamp." L665–667: "what the specific correlation structure is, this measurement does not identify." L784–785: "that count comes from one API call whose coverage is unknown." The first two are corrections of the paper's own earlier design narrated in the body; only the last three are legitimate scope statements. |
| 70 | Reads non-interventionally, like a top-tier body | **FAIL** | Aggregate of 64, 66, 69 and 87: the enumerative meta-sentences ("Two limits attach."), the twice-repeated caption pre-emption ("no model is run"), the competitor framing (L200), the priority aside (L206), and the narrated design corrections (L629–633) all put the author between the reader and the measurement. The measurement prose itself (§3, §4.1, §5, §6) does read the way the item asks; the surrounding apparatus does not. |

### Items 71–87

| # | Short name | Verdict | Evidence |
|---|---|---|---|
| 71 | Falsifiable Thesis Test | **PASS** | Thesis: within one published exposure window, per-object evidence times are dispersed beyond w²/12N. Falsified by excess ≈ 0 — and the paper contains that outcome, in the day stratum: "the excess is zero, and only 0.33 of frames exceed their null" (L440–441). The test the thesis could fail is run and reported. |
| 72 | Final-Objective Alignment | **FAIL** | The stated final objective is a change in reporting practice: "the label format used by this dataset family already has a per-object field in which a different value could be recorded" (L801–803). Nothing in the paper measures what would change if it were recorded — no AP, no px, no downstream effect. §7 is the bridge to that objective and every one of its six cells is `[unmeasured]`. |
| 73 | Nearest-Alternative Delta | **PASS** | The nearest alternatives are named and the delta is stated at operation level: "Each of these computes a per-object time in order to remove it. The quantity reported here is the dispersion itself, measured from the sensor rather than reconstructed from LiDAR and a known velocity, on global-shutter data where the rolling-shutter mechanism that produces Waymo's t_capture is absent." (L183–187). |
| 74 | Alternative-Explanation Kill Test | **FAIL** | Mains flicker is killed three ways (L506–531) and small-count noise is killed by construction. Not addressed: sensor/DVS noise and hot pixels — `graca2021noise` is cited for the phenomenon (L488–489) and never controlled for; ego-motion; and, most directly, `experiments/e09` names the missing control itself: "**Still owed before publication**, and this is the load-bearing wall for every night number …: a denoiser ablation … and a static-camera or stopped-vehicle segment as a motion-free control." Neither exists and the paper does not mention that it does not. |
| 75 | Claim–Evidence Ledger | **FAIL** | The ledger is mostly explicit and well kept ("no claim in Secs.~3--6 depends on them", L733–734; Table 1 and Table 2 captions name their sources and archive). Two entries have no evidence behind them: the `rethink3d2025` assertion (L217–218, contradicted by the supplement) and the daytime generality of the abstract (L59–60, on 12 frames the record calls "directional"). |
| 76 | Validity Envelope | **PASS** | Stated in four dimensions: sequences (L762–763), exposure setting (L555–556), benchmarks whose documentation was read ("Gen1, 1 Mpx, DSEC-Det, DSEC-3DOD, DSEC-Flow and MVSEC, and the statement is scoped to those six", L575–576), and prior-art search ("statements about prior art to the searches recorded in the supplement", L780–781). |
| 77 | Claim Fragility Test | **FAIL** | The headline is fragile in three ways the paper does not address. (a) The integer-period series is non-monotone and the widest cancelling arm is the *largest* excess: 212.6 → 195.2 → 183.6 → **246.8** µs (L380–383). The paper says only "the four values are interleaved" (L529). (b) The same 14996 µs configuration yields 208.8 in one table row and 183.6 in another (item 57). (c) The whole result is one sequence, and the six-sequence ceiling population is otherwise unmeasured. |
| 78 | Quality–Cost Pareto Test | **N/A** | The paper proposes no method, model or procedure with a runtime, memory or annotation cost. There is no quality–cost axis to place it on. |
| 79 | SOTA-Independent Value Test | **PASS** | The strongest property of the submission, and stated three times: "No detector is run, no checkpoint is loaded, no velocity divides a residual, and no label-noise level is assumed" (L131–132); abstract L68–69; conclusion L795–796. Table 1, Table 2 and Figs. 1–4 are all produced without a model — "no model is run" (L85, L300). |
| 80 | Bounded Limitation Test | **FAIL** | Four of §8's nine concessions are bounded (the two-point support contrast L762–765; the window-width growth L766–768; the σ_c upper bound L772–773; the six-benchmark scope L779–781). Three are unbounded — they state that something is unknown without saying what follows: "cannot say whether its labels are tracker output" (L773–774), "an offset estimated against tracker-generated labels is an offset between two models" (L775–776), "that count comes from one API call whose coverage is unknown" (L784–785). An unbounded limitation is an invitation, not an envelope. |
| 81 | Paradigm-Delta Test | **PASS** | The delta is a reporting change on an existing field, stated concretely: "Reporting a per-object time on this data is a change of reporting practice, not of format" (L120–121), and "the label format used by this dataset family already has a per-object field in which a different value could be recorded" (L801–803). |
| 82 | Method Compression Test | **PASS** | The whole construction compresses to one sentence, and the paper writes it: "For every labelled box we take the events falling inside that box during that frame's own exposure and compute their mean time; the dispersion of that quantity across the objects annotated in one frame is the estimand." (L124–127), plus one null, Eq. 2. |
| 83 | Hard-Case-First Evidence | **FAIL** | The evidence is presented easiest-first. The night ceiling stratum — widest window, 310 320 events per exposure (`e01`), 1133 usable frames — is the most favourable regime for the effect and leads the abstract, §1 ¶4, §4.2 and the Conclusion. The hard case, the 1524 µs daytime stratum where the effect vanishes, is 12 frames and gets one sentence in each place (L138–141, L437–441). The order is not deceptive — the null result is in the abstract — but it is the reverse of what this test asks. |
| 84 | Cross-Task Reuse Test | **FAIL** | The construct is defined generally and the paper names six benchmarks it could apply to (L575–576), but it is measured on exactly one dataset and two sequences, and no transfer is demonstrated or estimated. The one adjacent task in the paper, predictor effective timestamp (§7), is explicitly walled off: "no result transfers between them" (L601). |
| 85 | Reviewer Memory Test | **PASS** | The four memorable items are all present and repeated identically in abstract, §1, §4.2 and Conclusion: the object (evidence time inside one exposure), the number (229.5 vs 93.4 µs), the null (analytic, w²/12N), and the killed alternative (mains flicker, cancelled at integer periods). A reviewer will retain "inside one 15 ms DSEC exposure, per-object evidence sits ~229 µs apart against a 93 µs null, and it is not the mains." |
| 86 | Field-Consequence Test | **FAIL** | Same root as item 33. The paper states the consequence qualitatively — "A benchmark that indexes such a frame with one scalar timestamp is asserting a common instant that the sensor data inside its own exposure window does not support" (L799–801) — and never quantifies it in any unit the field acts on. With the paper's own numbers the consequence is 0.008–0.075 px, which is 1.7–15 % of σ_c; unless the paper argues why that is the wrong conversion, a reviewer supplies it and the consequence evaporates. |
| 87 | No defensive phrasing; strengths emphasised | **FAIL** | Defensive: "our null rather than our competitor" (L200); "published in vision four years before LET-3D-AP" (L206); "An unrefereed preprint … but reports plain average precision" (L218–220); "no model is run" repeated in two captions (L85, L300); "dropped rather than repaired" (L727–728). Strengths under-emphasised: the affirmative per-track and displacement results in `experiments/e09` (variance ratio 20.56×, correlation 0.567 vs 0.152) are absent, and `experiments/e13`'s solved σ_c (0.4974 px, with a 0.144 px quantisation floor separated out) is absent while §8 keeps the older, weaker "upper bound" framing. |

---

## Mechanical scans

### G1 — Sentence-length distribution (item 41)

Method: `main.tex` abstract + §1–§9, floats (`table`, `figure`, `tabular`, `equation`, `itemize`)
excluded, `numbers.tex` macros expanded, inline math collapsed to one token, sentence split on
`[.!?]` + whitespace with `Sec./Fig./Eq./Secs./Tab./vs./et al./i.e./e.g./cf.` protected.

```
n sentences: 199
mean 26.5   median 24   max 66
    0-  9: 40
   10- 19: 38
   20- 29: 41
   30- 39: 28
   40- 49: 30
   50- 59: 13
   60- 69:  9
over 35 words: 64  = 32.2%
over 40 words: 45
```

Every sentence over 35 words, with source-line span and length (macros expanded; ` Q ` = inline
math, ` X ` = `\ref`/`\cite`):

| Lines | Words | Sentence (head) |
|---|---|---|
| 46–89 | 42 | The frame carrying the label integrates light over an interval the dataset publishes: across the DSEC training split that interval runs from 118 to 14996 µs against a frame period fixed at 50 ms, and 32.5 % of frames sit at the auto-exposure ceiling. |
| 46–89 | **66** | On the sequence whose exposure is pinned at the ceiling, the evidence-weighted time centroids of the objects annotated in one frame have a within-frame standard deviation of 229.5 µs against an analytic null of 93.4 µs --- the value Q implied by evidence uniform over the exposure --- an excess of 208.8 µs, and the standard deviation exceeds its own null in 0.9179 of 1133 frames. |
| 46–89 | 47 | The dispersion survives excluding those pixels (207.3 µs, against 207.5 µs for a matched random exclusion) and survives integration over an integer number of mains periods, where a periodic source cancels whatever its amplitude, phase or spatial extent: 195.2 and 246.8 µs at one and two periods. |
| 91–103 | 55 | In the event--RGB setting the two extents differ, because the two sensors do not integrate over the same interval, and the frame extent is published: across the DSEC training split the interval over which one indexed frame integrates light runs from 118 to 14996 µs against a frame period fixed at 50 ms (Fig. X). |
| 105–121 | 48 | Waymo's label definition solves a per-object capture time Q from rolling-shutter geometry and object velocity, and uses it to shift the ground-truth box by Q for its camera-only challenge~X; the solved time is absorbed into that spatial shift and the Label message carries no timestamp field. |
| 105–121 | 41 | What no release fills is the field's per-object degree of freedom --- across the 60 released DSEC-Det sequences, 390 118 boxes take 70 379 distinct values of t, 5.54 boxes per value, and those values are the 50 ms frame clock (Sec. X). |
| 123–132 | 37 | For every labelled box we take the events falling inside that box during that frame's own exposure and compute their mean time; the dispersion of that quantity across the objects annotated in one frame is the estimand. |
| 123–132 | 47 | Its null is analytic: if the evidence inside a box were uniform over the exposure, the mean of Q event times would have variance Q for exposure width Q, so the excess subtracts a quantity that assumes nothing about the scene, the labels or the sensor. |
| 134–141 | 43 | On zurich\_city\_09\_a, whose exposure is pinned at 14996 µs, the within-frame standard deviation of the evidence time is 229.5 µs against an analytic null of 93.4 µs, an excess of 208.8 µs, and it exceeds its own null in 0.9179 of 1133 frames. |
| 143–153 | 41 | The night sequence is where the wide exposures are, and it carries a 100.00 Hz mains line: 0.2407 of live night pixels are phase-locked to it at Q, with a median Rayleigh statistic of 2.935 against an Q null of 0.693. |
| 143–153 | 51 | A 10 000 µs period inside a 14996 µs exposure displaces per-object evidence times with no motion at all, so the dispersion is measured again under two exclusions and under four analysis-window widths, two of which span an integer number of mains periods and cancel a periodic source exactly (Sec. X). |
| 176–187 | 45 | Waymo's camera\_synced\_box solves Q per object and stores the resulting box shift rather than the time~X; LET-3D-AP, the primary metric of that challenge, reports a camera-to-label synchronisation gap as a per-dataset interval and states that it depends on horizontal object position~X. |
| 189–200 | 36 | We import all four devices in Sec.~X, with the object's velocity in place of the sensor's line of sight and a tolerance read off a declared and a measured temporal support rather than swept. |
| 189–200 | 43 | TIDE~X and DETAD~X bucket detection error atemporally, and a temporal offset falls inside their localisation bucket; HOTA~X takes the label clock as exact; the response of average precision to isotropic box perturbation~X is our null rather than our competitor. |
| 202–220 | 52 | Qin and Shen~X calibrate a clock offset online by modelling a feature observation as Q, with Q differenced from consecutive observations; that is the estimator of Sec.~X, published in vision four years before LET-3D-AP, and the same work identifies the offset by making one scalar reconcile two channels. |
| 202–220 | 42 | Temporal calibration removes the offset between two sensor clocks by pooling over features, so the spread of per-feature estimates is its error bar; here the offset lies between a predictor's clock and a benchmark's label clock, and the spread is the estimand. |
| 202–220 | 43 | Streaming perception~X folds wall-clock compute latency into average precision and re-anchors any detector from box coordinates alone; AP^sync in Sec.~X is that operation with an estimated rather than a timed offset, on a latency that does not vanish on a faster device. |
| 222–242 | 38 | Gen1~X labels are drawn on grey-level images assembled from asynchronous per-pixel measurements; on the 1 Mpx dataset~X the event count inside a labelled box at its own timestamp is often too small to support detection~X. |
| 222–242 | 57 | That a frame's exposure is long relative to event timing has been stated: REFID~X argues that accumulating events from a single frame timestamp loses information, deblurring work names auto-exposure as the reason the width is unknown~X, and RENet~X uses a DSEC exposure interval as its event window while describing that exposure as short. |
| 222–242 | 50 | Protocol work supplies standards: re-measurement under a repaired protocol can reverse a field's conclusion~X, a reported score is an estimate with a variance~X, a label audit is judged by whether the errors it finds move benchmark results~X, and EVREAL~X re-scores event reconstruction atemporally. |
| 247–259 | 40 | The width varies by a factor of 127 against a frame period fixed at 50 ms, 32.5 % of frames sit at the auto-exposure ceiling of 14996 µs, and within one recording the width varies by up to a factor of 12.5. |
| 247–259 | 40 | On this data the exposure width is therefore a two-level factor that can be switched between strata but not swept, which fixes the design of Sec.~X: the support contrast is a comparison of two strata, not a curve. |
| 261–268 | **65** | The left and right exposures open at the same microsecond in 100.00 % of the 7080 frames checked and differ only in when they close, so the divergence between the cameras is a width difference rather than a synchronisation error, one to two orders of magnitude below the window itself; and the published image timestamp equals the mean of the two mid-exposures to within 1 µs. |
| 306–326 | 50 | The released DSEC-Det labels comprise 390 118 boxes on 6693 tracks across 60 sequences, and every label sits on the frame clock: the median spacing between consecutive label times is 50 001 µs, the spacings track each sequence's frame period, and the fraction shorter than four fifths of that period is 0.0000. |
| 306–326 | 60 | Consecutive labels are not linear interpolants of one another: over 361 628 triples of consecutive labels on a track, the median distance from the middle box centre to the linear interpolant of its neighbours is 0.707 px with a ninetieth percentile of 1.819 px, and only 7.1 % fall below a hundredth of a pixel, where interpolated labels would place that fraction near unity. |
| 306–326 | **63** | Whether the 20 Hz labels are themselves detector and tracker output on the RGB frames, which the dataset's own description states, is not distinguishable from human annotation by a second-difference residual, since both produce residuals of the same order; and what the inter-frame evaluation protocol of the associated work~X uses between frames is a property of a procedure rather than of this archive. |
| 354–361 | 40 | Variances are taken across the objects of a single frame and summarised by their median over frames, so a frame-level common offset --- the component a declared per-output scalar timestamp would cancel --- does not enter Eq.~X at all. |
| 429–441 | 55 | The within-frame standard deviation of Q is 229.5 µs, with a ninetieth percentile of 333.5 µs, against an analytic null of 93.4 µs; the excess by Eq.~X is 208.8 µs, the median within-frame peak-to-peak spread is 601.6 µs, and the standard deviation exceeds that frame's own null in 0.9179 of frames (Fig. X). |
| 429–441 | 44 | On interlaken\_00\_c, where the exposure is 1524 µs and the 200-event floor leaves 12 usable frames, the standard deviation is 18.7 µs against a null of 23.9 µs, the excess is zero, and only 0.33 of frames exceed their null (Fig. X, left). |
| 443–452 | 37 | Boxes of the same shapes placed at random positions in the same frames give a standard deviation of 338.4 µs against a null of 134.4 µs, an excess of 310.5 µs --- larger than the annotated boxes'. |
| 460–465 | 43 | The power spectrum of the global event rate, computed with the same code and window for both sequences, has its strongest line between 90 and 110 Hz at 100.00 Hz on zurich\_city\_09\_a, standing 10 841 above the 60--160 Hz continuum; on interlaken\_00\_c the same ratio is 6.6. |
| 467–481 | 39 | The Rayleigh statistic Q, for Q the resultant length of the event phases at the test frequency, is Q under uniform phase, so its null has median 0.693, p95 3.00 and a rate of 0.001 at Q. |
| 467–481 | 42 | Over 35 990 night pixels with at least 100 events, the median Q at 100.00 Hz is 2.935 with p95 16.52, and 0.2407 of those live pixels reach Q --- 4.67 % of the sensor's pixels --- with 0.0750 of live pixels at Q. |
| 467–481 | 46 | Two arms hold the estimator to its null: on the same night events at an off-frequency the median Q is 0.581 with a Q rate of 0.0004, and on 17 800 daytime pixels at 100.00 Hz it is 0.719 with a rate of 0.0008 (Fig. X, right). |
| 483–495 | 36 | DSEC's own description attributes high night event rates near street lamps to flashing lights~X, and event noise is known to rise in dim light~X; neither is quantified per pixel in the release. |
| 500–504 | 38 | A 10 000 µs period inside a 14996 µs exposure completes one and a half cycles, so a lamp displaces the evidence time of the boxes near it by an amount set by its phase, with no motion involved. |
| 506–516 | 40 | A matched random exclusion of exactly the same number of pixels gives 207.5 µs, so the removal of a quarter of the evidence accounts for the change and the pixels individually locked to the mains do not carry the effect. |
| 506–516 | 39 | This control is bounded by what it excludes: the median Q over all live night pixels is 2.935 against a null of 0.693, so a population that is weakly modulated without reaching individual significance remains in the clean arm. |
| 518–531 | 37 | Integrated over an integer number of periods, a periodic source contributes zero to a time centroid whatever its amplitude, its phase or how many pixels carry it, so this control does not require identifying the affected pixels. |
| 518–531 | 49 | If flicker produced the dispersion the two cancelling widths would return approximately zero; the four values are interleaved, with the cancelling pair neither smallest nor separated from the non-cancelling pair, and the fraction of frames whose standard deviation exceeds the analytic null is at least 0.901 at every width. |
| 552–558 | 43 | The dispersion remains a measurement on one sequence at one exposure setting, and the day--night contrast of Fig.~X confounds exposure width with illumination: what these controls remove is the flicker explanation of the night measurement, not the coupling between the two strata. |
| 570–577 | 60 | Let a predictor Q emit a state at query time Q with normalised temporal support kernel Q, the share of the emitted state's information coming from Q, of centroid Q and width Q, and let the label-generating process have centroid Q and width Q; a benchmark scoring at a nominal instant treats all four as zero. |
| 570–577 | 43 | Of the benchmarks whose documentation we read --- Gen1, 1 Mpx, DSEC-Det, DSEC-3DOD, DSEC-Flow and MVSEC, and the statement is scoped to those six --- none states, enforces or checks this, and in each the published label construction implies tens of milliseconds of support. |
| 579–588 | **62** | For a predictor linear in position measurements at bin centres Q with weights Q summing to one, the conditional expectation of the output under constant velocity is the true position at Q: non-negative weights give Q, while a predictor that uses older evidence to compensate its own lag has negative weights and moves Q toward zero without moving Q. |
| 590–601 | 58 | A DSEC frame's indexed timestamp is the mean of the two mid-exposures to within 1 µs (Sec.~X), so the frame branch's centroid sits at the label time; the event branch of the detector we examine~X consumes a window of 50 ms ending at the label time, so under uniform weighting its centroid sits 25 ms before it. |
| 621–633 | 40 | The denominator is finite differenced from labels, so the regression of Q on Q is an errors-in-variables problem; its two mechanisms, classical dilution and a smoothing bias of order Q from differencing over Q, are derived in the supplement. |
| 621–633 | 44 | Three estimates are reported side by side: Q, weighted least squares, a lower bound in magnitude; the Frisch bracket, with a sensitivity curve in the assumed variance ratio; and an instrumented estimate using a velocity differenced from a strictly disjoint earlier label pair. |
| 635–643 | 55 | A benchmark whose high-rate labels are constructed between anchors adds a term to Q that has nothing to do with the predictor: the chord of a curved image trajectory runs ahead of the truth throughout the interval and meets it at the anchors, producing a signed, frame-locked, resetting Q for a predictor with no latency. |
| 669–675 | 37 | Median box-centre image speed on DSEC-Det is 40 px/s and the ninety-ninth percentile is 360 px/s, so a 25 ms offset is 1.0 px at the median object and 9.0 px at the ninety-ninth percentile, about two and eighteen times Q. |
| 679–700 | 56 | For a fixed network of influence weights Q on bin centres Q, the conditional expectation after masking the leading Q bins is Q with Q and Q over the retained set Q, so a time reading Q requires a normalisation the network need not perform and equals the retained-mass centroid only for non-negative weights. |
| 679–700 | **62** | A probe on the released weights bounds the lever's range independently: with recurrent state disabled and synthetic sparse input, cumulative masking moves the backbone features monotonically only up to a retained width of 25 ms, reaching 0.1248, and the narrowest nominal width reaches only 0.1538; single-bin occlusion gives a nearly flat profile, a factor of about 2 between least and most influential bin. |
| 702–723 | 48 | The one transformation applied to a prediction file is Q, with Q from the method's own consecutive outputs and never from ground truth, scored with the unmodified standard metric to give AP^sync and Q: the Streamer post-processing of~X with an estimated rather than a timed offset. |
| 702–723 | 56 | Its calibration constant is fitted on the data it is scored on, since Q is the slope of a regression on ground-truth tracks, and refitting inside each bootstrap replicate reproduces that optimism rather than pricing it; we therefore cross-fit over folds of the evaluation sequences and report the cross-fitted score with the in-sample score beside it. |
| 702–723 | 41 | Whether any one-parameter test-set fit would raise the score as much is answered by the same regression's other parameter: the speed-independent intercept Q absorbs calibration, parallax and extrinsic error and carries no clock, so Q is reported beside AP^sync in every table. |
| 702–723 | 36 | Uncertainty uses the recording rather than the detection as the exchangeable unit, over a list of compared pairs fixed before any prediction file is scored, Holm corrected; tolerant diagnostic scores after~X are in the supplement. |
| 725–734 | 39 | Every detection number is gated on reproduction: each released checkpoint is run through its authors' own validation path under our ported stack, and one whose published score is not reproduced within a stated tolerance is dropped rather than repaired. |
| 725–734 | 40 | The port is verified --- the released checkpoint loads into a model built from the repository's own configuration files with 0 missing and 0 unexpected keys at 4.41 M parameters and runs forward, without the training framework it was serialised from. |
| 762–785 | 48 | The evidence-time result is one night sequence at one exposure setting and 12 usable day frames at the other, so the support contrast is a two-point comparison in which exposure width and illumination move together, and the flicker controls address only the flicker explanation of the night arm. |
| 762–785 | **63** | The integer-period arms do not separate the growth of the excess with window width from a widening of whatever else varies with the window, and the other five ceiling sequences are unmeasured; the phase-locked-pixel exclusion leaves in the weakly modulated population that does not reach individual significance, and the flicker measurement covers one night and one day sequence with events subsampled every fourth. |
| 762–785 | 46 | The constant part of a predictor's temporal offset is a reporting problem rather than a research problem --- a downstream constant-velocity filter absorbs a constant offset of declared sign exactly, by stamping the detection at Q --- and we claim no downstream accuracy improvement from it. |
| 762–785 | **63** | Statements about what benchmarks record are scoped to the six whose documentation we read, and statements about prior art to the searches recorded in the supplement, which returned 40 papers citing~X, of which 6 mention time, latency, streaming or event sensing and 0 apply the decomposition to a temporal axis; that count comes from one API call whose coverage is unknown. |
| 789–803 | 53 | Inside a single published exposure window of DSEC, the event evidence belonging to different labelled objects is centred at measurably different times: a within-frame standard deviation of 229.5 µs against an analytic null of 93.4 µs, an excess of 208.8 µs, in 0.9179 of 1133 frames, and zero excess in the narrow-exposure stratum. |
| 789–803 | 40 | The measurement needs no detector, no checkpoint, no velocity denominator and no assumed label noise, and it survives the removal of the pixels phase-locked to the mains, a matched random removal, and integration over one and two full mains periods. |
| 789–803 | 50 | A benchmark that indexes such a frame with one scalar timestamp is asserting a common instant that the sensor data inside its own exposure window does not support, and the label format used by this dataset family already has a per-object field in which a different value could be recorded. |

### G3 — Heavy punctuation (item 43)

Body prose totals: **semicolons 49**, **colons 40**, **em-dashes (`---`) 14**. 103 marks / 199
sentences = one every 1.9 sentences.

Em-dash sites (excluding the one `---` used as a table em-dash placeholder at L373):
L56, L57 (paired, abstract), L117, L360, L361 (paired), L446, L475 ×2 (paired), L575, L576
(paired), L728, L777, L779 (paired).

Semicolon sites: L85, 94, 109, 126, 160, 164, 167, 178, 198 ×2, 205, 209, 213, 217, 224, 228,
265, 300, 321, 325, 339 (math `\;`), 357, 379, 388, 408, 422, 433, 450, 463, 485, 489, 524, 528,
545, 573, 593, 618, 622, 626, 627, 660, 665, 693, 712, 718, 722, 733, 769, 775, 784.
Of these, L160/L164/L167 are `itemize` separators and L339 is math spacing; the remaining **45**
are prose.

### H1 — Parentheses per prose paragraph (items 46–49)

Inline math and LaTeX command arguments stripped before counting. **No paragraph exceeds two.**

| Lines | Count | Contents |
|---|---|---|
| 47–89 (abstract) | 1 | `(207.3 µs, against 207.5 µs for a matched random exclusion)` |
| 91–103 | 1 | `(Fig.~1)` |
| 105–121 | 1 | `(Sec.~3)` |
| **143–153** | **2** | `(0.581 at an off-frequency on the same events, 0.719 at 100.00 Hz in daylight)`; `(Sec.~6)` |
| **429–441** | **2** | `(Fig.~2)`; `(Fig.~3, left)` |
| 467–481 | 1 | `(Fig.~3, right)` |
| 518–531 | 1 | `(Table~2, Fig.~4)` |
| 590–601 | 1 | `(Sec.~3)` |

Paragraphs exceeding two: **none**.

### H2 — Item 50 register greps (run on `main.tex`)

```
because            3   L99, L467, L630
This is not        0
We do not          0
The point is       0
The reason         1   L232
cleanly            0
curiosity          0
sacrifice          0
price              0   (near-hit: "pricing" L712)
Why no             0
i.e.               0
raw "              0
every              9   L84, L124, L307, L494, L531, L605, L718, L725, L771
all                7   L150, L193, L361, L370, L514, L574, L674
only              13   L109, L190, L263, L314, L440, L492, L522, L523, L545, L686, L691, L693, L765
must               1   L70
cannot             4   L467, L588, L656, L773
never              1   L704
always             0
;                 49   (45 in prose — see G3)
---               14   (see G3)
```

### M1 — Percent spacing (item 55)

All 10 `\%` uses take `\,\%`; no bare `N%` and no `N \%`:
L51, L166, L250, L262, L282, L288, L315, L475, L485, L508.
Rendered: `32.5 %`, `4.67 %`, `7.1 %`, `100.00 %`. **Consistent.**

### M2 — British vs American spelling (items 56, 67)

**British-only forms present — 35 tokens:**

```
centre/centres/centred  11   L313, L452, L521, L544, L580, L606, L616, L648, L669, L681, L790
labelled                 6   L53, L124, L225, L333, L429, L790
normalis*                4   L570, L619, L685, L688
localis*                 3   L189, L190, L198
cancelling               3   L528, L529, L530
synchronis*              2   L179, L265
summaris*                2   L359, L389
grey                     2   L78, L223
recognised               1   L106
modelling                1   L203
```

**American-only forms present in prose: 0.** (`center` ×7 are the LaTeX command `\centering`
at L74, 271, 364, 401, 414, 542, 737. `parameter`/`parameters` at L714, 715, 731 are not a
spelling variant. `toward` at L584 is standard in both.)
`analysis` / `analytic` (L151, 394, 521, 544, 675) are correct in both varieties and are **not**
British forms.

### M3 — Terminology consistency (item 60)

```
exposure window        8    exposure interval      2
analysis window        4    event window           1
evidence time         10    evidence-weighted time centroid  1    time centroid  2
analytic null         10    its own null           2
dispersion            20    within-frame standard deviation  5
mains flicker          5    mains line             2
labelled object        2    annotated object       1
labelled box           2    annotated box          1
stratum/strata        10    arm                   10
daylight / daytime stratum / day frames / narrow-exposure stratum   3 / 1 / 2 / 1
```

Thousands separators — inconsistent (`numbers.tex`):
with `\,`: `10\,000`, `20\,000`, `35\,990`, `17\,800`, `10\,841`, `14\,334`, `50\,001`,
`70\,379`, `390\,118`, `361\,628`, `629\,442`, `4\,655\,023`.
without: `21142` (`\dsecFrameCount`), `14996` (`\dsecExpMax`, `\dsecExpGapHi`, `\wFullExp`).
`14996` and `10\,000` appear in adjacent rows of Table 2 (L381–383).

### M4 — Page-count verification (item 51)

```
$ pdfinfo paper/main.pdf | grep Pages
Pages:           9
```
Per-page `pdftotext`: p.1 abstract + §1; p.2 Fig. 1 + §1 + §2; p.3 §2 + Table 1 + §3;
p.4 §3 + Table 2 + §4 + §5; p.5 Figs. 2–3 + §5 + §6; p.6 Fig. 4 + §6 + §7;
p.7 §7.2–§7.4; **p.8 Table 3 + §7.4 + §8 Limitations + §9 Conclusion + References [1]–[2]**;
p.9 References [3]–[33].
Body = pp. 1–8. Text-block area 6.78 × 9.00 in = 61.02 in² vs `cvpr.sty` 6.875 × 8.875 in =
61.02 in². Note `paper/cvpr.sty` exists but is never `\usepackage`d (`grep -n cvpr main.tex` →
no `\usepackage{cvpr}`).

### M5 — Figure legibility (item 59)

Rendered at 200 dpi via `pdftoppm` and inspected.

- `fig1_dsec_exposure.pdf` — clean. 18 sequence labels legible; six sequences visibly pinned at
  the 14996 µs ceiling (this is the "six" that "the other five" refers to). Right-panel
  annotation "0 frames between 4207 and 14996 µs" overlaps the shaded band edge but is readable.
- `fig2_evidence_time.pdf` — clean. All eight per-object markers legible.
- `fig3_day_night.pdf` — **DEFECT.** Right-panel x tick labels collide: "100 Hz" and "137 Hz"
  overprint at all four ticks, extracting as `100 H137 H00 H137 Hz`. The in-plot labels
  "null p95" and "null median" are overstruck by their own dashed reference lines and run into
  the right axis frame.
- `fig4_integer_period.pdf` — clean. Uses `10000 µs` / `20000 µs` without the thin space the
  body text uses for the same numbers (item 60).

---

## Ordered fix list

Most consequential first. Locations are `main.tex` source lines. Do not apply these here — this
is a report.

**1. (items 33, 86, 72) Put the headline on the paper's own pixel scale.**
Insert after L675 (end of §7.3, immediately after the existing 25 ms conversion), or as the
closing sentence of §4.2 after L441:
> "At the same speeds, the 208.8 µs excess corresponds to 0.008 px at the median object and
> 0.075 px at the ninety-ninth percentile, well below σ_c: the quantity measured here is a
> property of when the sensor evidence for an object accumulates, not a displacement a current
> metric could resolve. What it bounds is the instant a single scalar timestamp can be taken to
> denote, not the score any detector receives."
Whatever the authors decide the right framing is, the conversion must appear. Leaving a reviewer
to compute 0.075 px unassisted is the single largest risk in the submission.

**2. (item 57) Reconcile the two 14996 µs rows of Table 2.**
L371 gives 1133 / 229.5 / 93.4 / 208.8 / 0.9179; L382 gives 1134 / 206.6 / 93.0 / 183.6 / 0.901
for the same sequence and the same width. Either (a) state the methodological difference in the
caption — the E09/E11 arm slices each frame's own published `[a,b]`, the E12 arm slices a
fixed-width window centred on mid-exposure, which differ on the frames not exactly at the ceiling
— or (b) re-run one arm so the two agree. Proposed caption addition after L390:
> "The top row slices each frame's own published exposure interval; the width rows slice a
> fixed-width window centred on the same mid-exposure instant, which is why the 14996 µs row of
> the bottom block retains one further frame and differs slightly from the top row."
If the 12 % sd gap is not explained by that, it is a bug and must be found before submission.

**3. (item 57) Fix "four" → "five" ceiling sequences at L491.**
Replace `whether the other four ceiling sequences behave the same is unmeasured` with
`whether the other five ceiling sequences behave the same is unmeasured`.
Six sequences are pinned (`experiments/e00`; visible in Fig. 1). Also add the antecedent once, in
§3 after L251, so "the other five" is resolvable:
`\dsecPinnedFrac\,\% of frames sit at the auto-exposure ceiling of \dsecExpMax\,\micro s, all of
them in six of the eighteen sequences,` (define a `\dsecCeilingSeqs` macro in `numbers.tex`).

**4. (items 23, 53, 57) Correct the Conclusion's plural attribution.**
L798–799 currently: `The same sequences are shown to carry a \flickerLineHz\,Hz line on
\flickerFracLocked{} of their live pixels.`
Replace with:
> `The night sequence carries a \flickerLineHz\,Hz line on \flickerFracLocked{} of its live
> pixels, against \flickerFracLockedDay{} in the day sequence.`

**5. (items 23, 75) Remove the assertion about the unread reference.**
L217–218 currently: `a latency-aware average precision inside LET-3D-AP's citation
graph~\cite{rethink3d2025} measures device latency.`
Replace with a citation that does not claim to have read it, e.g.:
> `a further preprint inside LET-3D-AP's citation graph is titled for the physical
> world~\cite{rethink3d2025}; the supplement records that it was not retrieved.`
Or read the paper and state what it does. As written the body contradicts `supplement.tex` §7 and
`experiments/e07`.

**6. (items 52, 62, 87) Promote the affirmative evidence that already exists.**
Add to §4.2 after L452, from `experiments/e09_per_object_evidence_time/README.md` (numbers are
measured; they need macros in `numbers.tex`):
> "The dispersion is structured rather than frame-independent. Across 102 tracks with at least
> five observations, the between-track standard deviation of the centred residual is 170.3 µs
> against 37.6 µs expected with no track effect, a variance ratio of 20.6, and the residual has a
> lag-1 autocorrelation of 0.471 along a track. Stratifying by image displacement, that
> autocorrelation is 0.152 in the low-displacement half and 0.567 in the high-displacement half."
This is the strongest material the project owns and it is the direct answer to fix 1.

**7. (item 67) Convert to American spelling — 35 tokens.**
`centre→center`, `centres→centers`, `centred→centered` (L313, 452, 521, 544, 580, 606, 616, 648,
669, 681, 790); `labelled→labeled` (L53, 124, 225, 333, 429, 790); `normalised→normalized`,
`normalisation→normalization`, `self-normalising→self-normalizing` (L570, 619, 685, 688);
`localisation→localization` (L189, 190, 198); `cancelling→canceling`, `non-cancelling→
non-canceling` (L528, 529, 530); `synchronisation→synchronization` (L179, 265);
`summarised→summarized` (L359, 389); `grey→gray` (L78, 223); `recognised→recognized` (L106);
`modelling→modeling` (L203). Do **not** touch `analysis`/`analytic`. Regenerate `figs/` if any
axis label carries a British form.

**8. (items 41, 43) Split the eight longest sentences and cut the punctuation load.**
Priority targets, all ≥ 60 words: L52–59 (66 w, abstract), L261–267 (65 w), L318–324 (63 w),
L766–772 (63 w), L780–785 (63 w), L579–585 (62 w), L689–695 (62 w), L306–311 (60 w),
L570–577 (60 w). Target: no sentence over 40 words, and ≤ 25 prose semicolons (from 45). The
abstract sentence at L52–59 should become three: the measurement, the null, the frame fraction.

**9. (items 52, 62, 36, 80) Consolidate the four limitation blocks into one bounded paragraph.**
Delete the §5 block (L489–495, "Two limits attach.…") and the §6 block (L533–539, "Three limits
attach to this arm.…"), moving their content — without loss — into §8, which is already the
right place. Then rewrite §8 so it ends on the envelope rather than on the API call. Proposed
closing sentence to replace L783–785:
> "Within these bounds — one ceiling sequence, one narrow-exposure stratum, and the six benchmarks
> whose documentation was read — the measurement stands without a detector, a checkpoint, a
> velocity denominator or an assumed label-noise level."
Target length: 10–12 rendered lines, against the 5–8 of the five reference papers.

**10. (item 57, `experiments/e13`) Update the σ_c statement to the current measurement.**
L652–657 and L772–773 report σ_c = 0.4973 px as an upper bound from the third difference.
`experiments/e13_difference_ladder` has since solved it: σ_total → 0.4974 px by a k-th-difference
ladder with two-rate elimination, decomposed into σ_annotation = 0.476 px plus a 0.144 px
quantisation floor arising because DSEC-Det stores box coordinates as integers. Either cite E13
and drop "upper bound", or state explicitly why E08's bound is retained. Keeping the weaker
framing when the stronger measurement exists is the clearest instance of item 53's
underclaiming direction.

**11. (item 59) Fix Fig. 3's colliding tick labels.**
`figs/fig3_day_night.pdf`, right panel: the four x ticks ("night 100 Hz", "night 137 Hz",
"day 100 Hz", "day 137 Hz") overprint. Two-line tick labels or a smaller font in
`src/make_figs.py`. While there, move "null p95" and "null median" off their dashed lines.

**12. (item 64) Remove the three enumerate-then-list meta sentences.**
L261 `Two checks fix what the indexed timestamp denotes.` → delete; begin "The left and right
exposures open at the same microsecond…".
L489–490 `Two limits attach.` → delete (the block moves to §8 per fix 9).
L533 `Three limits attach to this arm.` → delete (likewise).

**13. (item 40, 66, 87) Neutralise the three defensive constructions in §2 and the captions.**
L199–200 `is our null rather than our competitor` → `supplies the isotropic null used in
Sec.~7.4`.
L205–206 `published in vision four years before LET-3D-AP` → `published in visual-inertial
odometry` (keep the citation; drop the priority framing).
L218–220 `An unrefereed preprint names the event--RGB frequency mismatch~\cite{faod2024} but
reports plain average precision.` → `The event--RGB frequency mismatch is named
in~\cite{faod2024}, which scores with unmodified average precision.`
Delete one of the two `no model is run` caption pre-emptions (keep L85, drop it from L300).

**14. (item 14, 15) Cut the abstract from 17 numerals to four, and unify proportion format.**
Keep: 14996 µs (the window), 229.5 µs (the measurement), 93.4 µs (the null), and one frame
fraction. Move 118, 50 ms, 32.5 %, 208.8, 1133, 100.00 Hz, 0.2407, 0.0008, 207.3, 207.5, 195.2,
246.8 into the body, where all of them already appear. Write every proportion the same way —
either all percent ("92 % of 1133 frames", "24 % of live night pixels") or all fractions — not
both in one abstract.

**15. (item 18) Add a two-sentence bridge before the contribution list.**
Insert between L153 and L155:
> "The measurement and its controls fix what this paper reports and what it does not: a property
> of the sensor evidence inside a label's own exposure window, on the data the benchmark
> publishes. Nothing below requires a detector."

**16. (item 60) Unify terminology.**
(a) Name the narrow stratum one way throughout — "the daytime stratum" — at L59, L138–139,
Table 2 row 2 (L372) and L794.
(b) Give "dispersion" one referent. Use "within-frame standard deviation" for the sd and
"excess" for the null-subtracted quantity; at present L60 uses "dispersion" for the first and
L554–555 for the second.
(c) Apply the `\,` thousands separator to `21142` → `21\,142` and `14996` → `14\,996` in
`numbers.tex` (`\dsecFrameCount`, `\dsecExpMax`, `\dsecExpGapHi`, `\wFullExp`), matching every
other five-digit number in the paper and `experiments/e00`'s own text. Regenerate `figs/fig4`
so its axis reads `10\,000 µs` / `20\,000 µs` like the body.
(d) Abstract L54: `the evidence-weighted time centroids` → `the evidence times`, matching §4.

**17. (item 57) Fix the two cross-document defects in `supplement.tex`.**
(a) "the support regression of main Eq.~10" — `main.tex` has three numbered equations. Replace
with a section reference: "the support regression of main Sec.~7.4".
(b) Supplement title reads "Per-Object Evidence Time Within a Single Exposure"; `main.tex` L37
reads "Evidence Time Within a Single Exposure". Make them identical.

**18. (item 61) Repair the two non-clausal semicolons.**
Table 2 header L379: `Night window width; \wOnePeriod{} and \wTwoPeriod{} cancel flicker` →
`Night window width (\wOnePeriod{} and \wTwoPeriod{} cancel flicker)`.
Fig. 2 caption L408–409: `…own analytic null $w^{2}/12N_{i}$; medians \sigmaEvtNight{} and
\sigmaEvtNullNight\,\micro s.` → `…own analytic null $w^{2}/12N_{i}$. The medians are
\sigmaEvtNight{} and \sigmaEvtNullNight\,\micro s.`

**19. (item 6) Define or cite the three unexplained terms.**
"Frisch bracket" (L626, L632, Table 3 L744) — add a one-clause gloss ("the interval between the
two extreme-assumption slopes of an errors-in-variables regression") and a citation, or replace
with "the bounding interval of the errors-in-variables slope".
"Holm corrected" (L722) — add a citation.
"the Streamer post-processing of~\cite{li2020streaming}" (L706–707) — name it as the cited work
names it.

**20. (item 10) Split the three multi-role paragraphs.**
L306–326 → three paragraphs (census; interpolation forensics; provenance and version).
L679–700 → two (why masking is not the support axis; the probe and the replacement instrument).
L702–723 → two (the transformation and its null; uncertainty and the comparison list).

**21. (items 35) Align the contribution bullets with the section order.**
Bullet 2 (L161–164) cites "Secs.~4–6" and so spans bullet 3's section. Either move the flicker
measurement bullet ahead of the dispersion bullet, or narrow bullet 2's reference to Sec. 4 and
let bullet 3 carry Secs. 5–6.

**22. (item 74) State the two controls that do not exist.**
`experiments/e09` names "a denoiser ablation … and a static-camera or stopped-vehicle segment as
a motion-free control" as still owed. Sensor noise (`\cite{graca2021noise}` is cited at L488 for
the phenomenon and never controlled) is a live alternative explanation. Either run the motion-free
control — it is one segment of one sequence — or add one clause to §8 naming it, so the paper
is not silent on an objection its own record raises.

**23. (item 83) Consider leading §4.2 with the daytime stratum.**
Reporting the null result first and the ceiling stratum second costs nothing, reads as
hard-case-first, and makes the exposure-width contrast the subject rather than the night number.
Optional; lower priority than 1–10.
