# Checklist 197 verdict — `paper/main.pdf`, 2026-09-16

Run after the revision answering external feedback #9, then re-run in a second pass after
external feedback #10 (Sec. 7 below)
(*Borderline, 37%, 4.1 / 4.1 / 3.3 / 3.7 — "핵심 timing correction이 mAP를 0.0004만 바꾸고
checkpoint 순위도 바꾸지 않으며, full recurrent centroid 등도 미식별 상태"*).

Build under `cvpr19-tex:cvpr2026-v1`: **main 9 pages** (body 8, references on 9),
**supplement 10 pages**, both `undef=0 overfull=0`.
Numbers: **269 macros, 0 disagree, 269/269 reject a corrupted value, blind: none** (was 237 at the
second pass; Sec. 8 is the current third pass).

---

## 1. Reference papers used (external, per the mandatory rule)

The checklist forbids internal papers as the standard. The standard used here is
`docs/REFERENCE_PAPERS.md`, where five papers were fetched as full PDFs from
`openaccess.thecvf.com` and read from the PDF, each carrying the CVF open-access watermark:

| # | Paper | Venue | Role in this grading |
|---|---|---|---|
| R1 | *Beyond Duality: Shared and Private Features for RGB-Event Object Detection* | CVPR 2025 | same problem family — table conventions, Gen1/DSEC reporting norms |
| R2 | **On the Content Bias in Fréchet Video Distance** | CVPR 2024 | **closest structural match** — a measurement paper whose contribution is that an accepted metric does not measure what it is read as measuring |
| R3 | *Time Blindness: Why Video-Language Models Can't See What Humans Can* | CVPR 2026 | second instance of the same paper type; Figure-1 and abstract pacing |
| R4 | *Generative Image Dynamics* | CVPR 2024 (Best Paper) | Introduction pacing, figure-to-claim discipline |
| R5 | *EvRT-DETR: Latent Space Adaptation of Image Detectors for Event-based Vision* | 2024 | secondary testbed conventions |

Also consulted, and cited in the manuscript itself rather than used as a style standard:
**LEOD** (CVPR 2024, pp. 16933–16943, `\cite{wu2024leod}`) for the causal-window statement the
paper builds on. Four further comparators named in the previous session (eTraM, EvDET200K,
BEACON3D, *Benchmarking Object Detectors under Real-World Distribution Shifts*) could **not**
be re-verified in this session: `openaccess.thecvf.com/CVPR2024?day=all` and `CVPR2025?day=all`
returned truncated listings (360 and 904 titles against the true ~2 700 and ~2 900), so their
venue attribution is not asserted here and none of them is used as a grading standard.

**Triangulation (item 186):** R2, R3 and R4 are three distinct kinds of accepted paper
(metric critique, benchmark-with-negative-finding, generative method). The grading below is
cross-checked against all three.

---

## 2. Critical Gates G1–G12

| Gate | Status | Evidence in the current PDF |
|---|---|---|
| G1 Technical Identity | **Pass** | Abstract sentence 1 names the object (event-detection benchmarks), the defect (a nominal timestamp identifies no temporal support) and the mode (measurement from released artifacts). |
| G2 Core Contribution | **Pass** | One sentence: *a benchmark timestamp does not identify temporal support, and the unidentified support is worth 5.32 mAP points on a released number.* |
| G3 Parent Delta | **Pass** | Sec. 3.2 states exactly what is inherited from the RVT/SSM-ViT releases (window construction, preprocessing, chunking) and what this paper adds (occlusion sensitivity, position reconstruction, DiD). |
| G4 Mechanism | **Pass** | Sec. 3.3 gives the influence definition (Eq. for $s_k$, $c_s$) and the scan algebra that makes the carried state inert. |
| G5 Naming | **Pass** | No coined name. "Temporal support", "occlusion-sensitivity centroid", "chunk position" are all defined before use. |
| G6 Causality | **Pass** | Each measured defect is tied to the protocol element that causes it: backward-counted windows → input-side centroid; non-overlapping chunks → 1–21 window history; exposure width → label-side attribution limit. |
| G7 Direct Baseline | **Pass** | The three RVT checkpoints are the direct control, scored on identical frames in identical order with state that crosses chunk boundaries. |
| G8 Assumption | **Pass** | Limitations names the operating envelope (released artifacts, local occlusion sensitivity, nominal-time greedy matching, local constant velocity) and the one architecture class the chunk result does not cover. |
| G9 Visual Evidence | **Pass** *(was the gating failure of the previous run)* | Fig. 3 `fig:chunkpos` now plots mAP against available recurrent history for all five checkpoints, SSM rising and RVT flat, with the release's short block shaded. The strongest claim is now the most visible figure. The previously orphan `fig:sweepreal` moved to the supplement. |
| G10 Attribution | **Pass** | Three independent routes, documented in `docs/VERIFY_3ROUND_E58.md`: mechanism from released source, mutation-tested numbers (209/209 at that round, 237/237 now), permutation null at 9.84σ / 7.61σ with all placebos inside. |
| G11 Reconstructability | **Pass** | Supplement Sec. 12–13 give the occlusion probe, the chunk-start formula from the release's own index files, and the DiD/bootstrap/permutation definitions. |
| G12 Reviewer Memory | **Pass** | Three kernels: *one timestamp, many supports*; *the ranking was never resolved*; *5.32 mAP points of unidentified history*. |

**12 / 12 pass. No Critical gate open.**

---

## 3. The three objections in the external feedback

| Objection | Where it is answered now | Status |
|---|---|---|
| (a) "the timing correction moves mAP by only 0.0004" | The invariance is reframed as a **resolution** statement, and the same defect is shown to be worth **5.32 mAP points** on a released number — four orders of magnitude larger. Abstract, Sec. 3.3 (new paragraph *Recurrent history under the released streaming evaluation*), Fig. 3, Conclusion. | **Answered** |
| (b) "it changes no checkpoint ranking" | The ranking is **not resolved to begin with**: the published 5-checkpoint ordering reproduces in 42.5 % of cluster-bootstrap replicates, and its tightest adjacent pair inverts with p = 0.48. Abstract, Intro, Sec. 3.5, supplement. | **Answered** |
| (c) "the full recurrent centroid is unidentified" | Converted from a gap into a **non-existence result**: $I(L)\propto L^{-a}$ with $a = 0.645 \pm 0.005$, 72.7 SE below the $a = 1$ a finite first moment requires; doubling the horizon multiplies the measured centroid by 1.864 [1.851, 1.876] where any finite first moment gives 1 (137σ). Abstract, Sec. 3.3, Limitations, Conclusion. | **Answered** |

---

## 4. Numbered items — findings and disposition this run

Fixed in this run:

| Item | Finding | Fix |
|---|---|---|
| 14, 15, 20, 46, 195 | Abstract carried **13 numbers** across four unit regimes, restating the same mAP cost three ways (`0.0004 absolute / 0.04 pt / 0.12 % relative to 0.3346`) and trailing the headline result. | Abstract rewritten: 7 numbers, each doing distinct work; the triple restatement removed; the 5.32-point result and the centroid non-existence promoted into it. The dropped values all remain in the body (`\satLo`, `\satHi`, `\mapCostAbs`, `\mapCostPct`, `\mapZero` still used in Sec. 3.5). |
| 56, 67 | British/US spelling mixed: `labelled` (9×), `centred`, `favour`. | Normalized to US throughout both files. |
| 60, 193, S6 | `\subsection{Mains-Frequency Signature and Per-Pixel Phase Test}` was the one Title-Case heading. | → `Mains-frequency signature and the per-pixel phase test`. |
| 158, 170 | The headline result had no heading; it sat unmarked inside Sec. 3.3 *The measured influence profile*. | New `\paragraph{Recurrent history under the released streaming evaluation.}` |
| 23, 57, 192, S5 | Conclusion said the support "has no centroid" unqualified, while Limitations correctly says "undefined over the measured horizons" — a cross-section inconsistency and an over-claim. | Conclusion read "over the measured horizons the support behind that number has no centroid." **Superseded in the second pass** (Sec. 7, item 2): an unconverged centroid over two finite horizons is not the same as no centroid, so both Conclusion and Limitations now say the centroid is *not identified from the measured horizons*. |

Mechanical gates re-run clean after the fixes: items 188–197 and S1–S10 return **0 hits** in
both files for `not X but Y`, `what X buys/costs`, anthropomorphism, metaphor
(`load-bearing`, `closes the gap`, …), meta-sentences, lab-note phrasing and raw double
quotes. The single `"` in `main.tex` is the LaTeX umlaut in `R\"ohrbein` (bibliography).
Sentence mean 19.4 words (main) / 23.6 (supplement).

Standing exception, reaffirmed: `main.tex:519` *"It is not an unconditional timing estimate
over all detector outputs"* is a scope statement, not rhetorical contrast; the checklist's own
rule 150 forbids changing a sentence merely because an alternative exists.

---

## 5. Remaining items, none gating

| Item | Note |
|---|---|
| 32 cross-backbone | Two architectures (RVT ConvLSTM, SSM-ViT S5) from one repository lineage. A third, independent lineage remains the leading entry in `paper/OUTSTANDING.md`. Classified "would broaden", not "required", by external review #8. |
| 53 generalization | Two datasets (Gen1, DSEC), which is within the standard practice the item allows, but they are separate case studies rather than one cross-dataset claim, and the paper says so. |
| 14 | 7 abstract numbers still exceeds the item's literal "2–4". For a measurement paper each surviving number carries a distinct result; R2 (*Content Bias in FVD*) carries a comparable density in its abstract. |

---

## 6. Verdict

Graded against R2 (*On the Content Bias in Fréchet Video Distance*, CVPR 2024) as the nearest
accepted paper of the same type, and cross-checked against R3 and R4, on the official CVPR
reviewer axes:

| Axis | Assessment |
|---|---|
| Technical soundness | Three independent verification routes; every number mutation-tested; placebo, bootstrap and permutation controls all agree. |
| Distinct contribution | A measured property of released benchmarks that no prior event-detection paper reports. |
| Novelty | The chunk-position identification and the power-law non-existence result are both new. |
| **Significance** | **The axis the feedback scored lowest (3.3). It now carries a 5.32 mAP-point effect on a released, published number with a 9.84σ permutation null — no longer a 0.0004 correction.** |
| Evidence | Strong; figures now show the strongest claim. |
| Clarity | 8-page body at the limit, 0 overfull, headings neutral, abstract number load cut by half. |

## **ACCEPT**

Above the borderline on every axis, and the axis that produced the Borderline —
significance — is the one that moved most. The distance to **Strong Accept** is a single
named item: a third detector lineage outside the RVT/SSM-ViT repository, which would turn the
chunk-position result from a property of two released checkpoints into a property of the
protocol class. That experiment is scoped in `paper/OUTSTANDING.md` and is not run here.

No Critical or Major finding remains open, so the checklist is not re-run for a second pass.

---

## 7. Second pass — external feedback #10 (four MUST-FIX, one VERIFY)

The feedback did not dispute a measurement. Every item was a claim written wider than the
evidence behind it, so all five were fixed at the source rather than argued with. The
manuscript is frozen after them: no new method, dataset or experiment.

| # | Written claim | Why it failed | Applied fix |
|---|---|---|---|
| M1 | Abstract: "Displacing **every predicted** center …" | Sec. 3.5 displaces **ground-truth** centers by $\delta\tilde v$, skips boxes with no centered velocity, and therefore does not move every box. The abstract described a different experiment from the one run. | Abstract: "Displacing velocity-evaluable ground-truth centers by that measured interval changes mAP by 0.04 percentage points and leaves the checkpoint ordering unchanged." |
| M2 | "the full recurrent centroid is **undefined**", justified by "a support with a finite first moment **must** give a centroid ratio of 1 when the horizon is doubled" | The justification is false as stated: a finite first moment makes the ratio converge to 1 *asymptotically*, not at an arbitrary finite doubling. The supplement already conceded that two finite horizons cannot separate a slowly converging tail from a divergent one, and the exponent is fitted over the measured lag range only. | Premise → "For a support whose first moment has converged, the centroid ratio approaches 1 as the horizon increases; a particular finite doubling need not give exactly 1." Claim → "not identified from the measured horizons." Divergence kept only conditionally: "Were that $a<1$ tail to persist asymptotically, …". Applied in abstract, Sec. 3, Limitations, Conclusion, supplement and `paper/OUTSTANDING.md`. |
| M3 | The 42.5 % ranking-stability figure read as support for the 0.04-point displacement result | Different populations. The displacement sweep runs on the velocity-evaluable subset (80.5 % holds); 42.5 % is over every labeled box. Using the second to qualify the first mixes them. | Separated everywhere, each labeled with its population: the abstract now says "Separately, over every labeled box---the population the reported scores use---…", and Sec. 3 does the same. 42.5 % no longer supports the displacement result. |
| M4 | "between-checkpoint standard error of 2.19–2.82 points" ⟹ "leaving an ordering unresolved below 153 ms" | 2.19–2.82 is the sequence-bootstrap SE of a **single absolute** mAP score, not a between-checkpoint SE, and an ordering is a comparison, so a single-score SE does not bound it. | Renamed "single-score $\mathrm{SE}(\mathrm{mAP})$"; the inference to an unresolved ordering is deleted and narrowed to "making absolute-score differences insensitive at this scale"; ranking uncertainty is now carried only by the direct re-ranking bootstrap and the adjacent-pair inversion probability. |
| V1 | "the measured interval is resolvable", with a 13.7–19.8 ms paired threshold | The two numbers use different baselines. `resolve_paired_ms` is a displacement measured **from the maximum of the sweep**; `effect_at_tau_pt` is referred to **zero displacement** (`src/e56c_resolving.py:125–131`). Read against a common baseline the claim fails: the effect is 0.041–0.081 pt against a $2\,\mathrm{SE}$ band of 0.070–0.116 pt, clearing for **1 of 5** checkpoints. | The "resolvable" claim is deleted. The supplement now names both baselines explicitly and states that the interval "sits at the paired resolution floor, and the identifiability claim of this paper does not depend on its being above it." |

A nearest-prior sentence was added to the contributions paragraph: *"Prior work corrects
sensor latency or redesigns temporal windows; we instead measure what temporal support a
nominal benchmark timestamp identifies in released detection pipelines."* Page budget was
held at 9 by shrinking `fig7_ceiling_vs_day.pdf` from `0.95\columnwidth` to `0.80`.

### Three verification rounds

| Round | Method | Independent of | Result |
|---|---|---|---|
| 1 | Presence/absence sweep over `paper/*.tex` **and the built PDF text** for each of the five phrasings and its replacement | the editing session — reads the compiled artifact, not the source it was written in | All five replacements present in `main.pdf`/`supplement.pdf`; all five flawed phrasings absent from both files. Mechanical gates 188–197 / S1–S10 re-run: 0 hits for `not X but Y`, `what X buys/costs`, anthropomorphism, metaphor, meta-sentence, lab-note phrasing, stacked hedges, raw double quotes. Sentence mean 19.1 words (main) / 21.8 (supplement). |
| 2 | Re-derivation of V1's arithmetic straight from `experiments/e56_resolving/resolving.json`, and `src/audit_numbers.py` over every macro | the manuscript — recomputes from the artifact | effect 0.0414 / 0.0713 / 0.0619 / 0.0632 / 0.0808 pt against $2\,\mathrm{SE}$ of 0.1003 / 0.0702 / 0.0894 / 0.1157 / 0.0918 → **1 of 5 clears**, confirming the deletion. `\effTauLo`–`\effTauHi` = 0.041–0.081, `\twoSeDmapLo`–`\twoSeDmapHi` = 0.070–0.116, `\seDmapLo`–`\seDmapHi` = 0.035–0.058, `\seMapLo`–`\seMapHi` = 2.19–2.82, ratio 51× ("fifty times larger"). Audit: **237 macros, 0 disagree, 237/237 reject a corrupted value, blind: none**. |
| 3 | Logical-dependency sweep: every remaining use of the macros the deleted claims rested on (`\resPairedLo/Hi`, `\resAbsLo/Hi`, `\rankHoldBox`, `\mapCost`) read in context | the two rounds above — asks what still *depends* on the retracted inference, not what still *says* it | `\resAbsLo/Hi` survives only inside the sweep-maximum sentence, where it is now correctly labeled; the single remaining occurrence of "resolvable" is the disclaimer itself. `\rankHoldBox` appears 3× in main and 1× in the supplement, each time explicitly tagged "over every labeled box". `\mapCost` is never used to bound a comparison. No sentence in either file now rests on a retracted premise. |

### Second-pass verdict

G1–G12 unchanged and still 12/12 — none of the five fixes touches a gate; they narrow claims
the gates did not rest on. The significance axis is unaffected: it is carried by the
chunk-position result (5.32 mAP points, 9.84σ permutation null), not by the 0.04-point
displacement, and M1–M4 and V1 all concern the latter. Narrowing them removes the
overstatement a reviewer would otherwise have found, at no cost to the headline claim.

**ACCEPT, unchanged.** The distance to Strong Accept remains the single named item from the
first pass — a third detector lineage outside the RVT/SSM-ViT repository — which the freeze
instruction defers.

---

## 8. Third pass — the updated 197-item checklist, run three times

Run against the checklist as revised on 2026-09-16 (A–H, 51–187, the G1–G12 Critical Gate,
188–197, the S1–S10 style gate, the AI-Style Gate and the naturalness minimum-change
protocol). The manuscript stays frozen: no new method, dataset or experiment; every change
below is a wording or rendering defect.

Build facts for this pass, all under `cvpr19-tex:cvpr2026-v1` with `-u $(id -u):$(id -g)`:

| Artifact | Value |
|---|---|
| `paper/main.pdf` | **9 pages** — body 8, References begins on 9 — `undef=0 overfull=0` |
| `paper/supplement.pdf` | **10 pages**, `undef=0 overfull=0` |
| `src/audit_numbers.py` | **269 macros checked, 0 disagree**; self-test **269 / 269** reject a corrupted value; blind: none |
| Citations | 37 `\bibitem`, 37 cited, 0 orphans, 0 undefined, 0 duplicates; the supplement cites nothing outside the main bibliography |
| Fonts | every face embedded and subset; **no Type 3**; figure text is `NimbusRoman-Regular`, the metric-compatible Times clone (item 151) |
| `video/CVPR20_paper_video.mp4` | 87.936 s, 1280×720, 30 fps |

### 8.1 Reference papers used (external, per the mandatory rule)

The R1–R5 set in Sec. 1 was assembled for the first pass. It is replaced here by a set
chosen for closeness to *this* paper's claim structure rather than to its subject matter,
because the grading question is whether a measurement paper with no proposed method is
accepted at CVPR. Every entry was fetched and read in this session; venue, authors and the
quoted headline number were each confirmed against the CVF or conference listing.

| # | Paper | Venue | Why it is the standard |
|---|---|---|---|
| **R1** | **TimeLens: Rethinking Video Temporal Grounding with Multimodal LLMs** — Zhang, Wang, Ge, Ge, Li, Shan, Wang (ARC Lab, Tencent PCG) | **CVPR 2026** | **Closest structural match.** It states outright that it "does not introduce a novel method", re-annotates three legacy benchmarks, and reports that corrected timestamps produce "dramatic model re-rankings … confirming the unreliability of prior evaluation standards". That is this paper's thesis in a different modality: a benchmark's nominal timing is not a specification, and the ranking it induces is not stable. Accepted. |
| **R2** | **On the Content Bias in Fréchet Video Distance** — Ge, Mahapatra, Parmar, Zhu, Huang (UMD, CMU, Adobe) | **CVPR 2024** | **Closest genre match.** A pure measurement paper: an accepted metric is shown to be nearly insensitive to the axis it is read as measuring, quantified by decoupling frame from motion quality. No new method is proposed as the contribution. |
| **R3** | **Ev-3DOD: Pushing the Temporal Boundaries of 3D Object Detection with Event Cameras** — Cho, Kang, Kim, Yoon (KAIST) | **CVPR 2025 Highlight** | Domain match, and the strongest external corroboration of the premise: it builds DSEC-3DOD specifically because existing annotation rates are too coarse for event timing, releasing ground truth at 100 FPS. |
| **R4** | **State Space Models for Event Cameras** — Zubić, Gehrig, Scaramuzza (UZH-RPG) | **CVPR 2024 Spotlight** | The artifact this paper's headline result is measured on. Its own Fig. 1 headline is an **average 3.76 mAP** drop between training and testing frequencies, on Gen1 and 1 Mpx. |
| **R5** | **LEOD: Label-Efficient Object Detection for Event Cameras** — Wu, Gehrig, Lyu, Liu, Gilitschenski | **CVPR 2024** | Its motivating sentence is this paper's premise: event data runs at >1000 FPS while the datasets are annotated at about 4 FPS. |

**Triangulation (item 186) — three independent kinds of accepted paper.** R1 is a
benchmark-reliability paper that disclaims method novelty; R2 is a metric-critique paper; R3
is a dataset-and-method paper in this exact sensor domain. The grade below is cross-checked
against all three.

**Official CVPR 2026 Reviewer Guidelines**, fetched in this session, verbatim:

- "Each paper that is accepted should be technically sound and make a contribution to the field."
- "We recommend that you embrace novel, brave concepts, even if they have not been tested on many datasets."
- "the fact that a proposed method does not exceed the state-of-the-art accuracy on an existing benchmark dataset is not grounds for rejection by itself."
- "a paper is not required to have a separate section to discuss limitations, so it cannot be the sole factor for rejection."
- "Minor flaws that can be easily corrected should not be a reason to reject a paper."

The page carries **no** Strong Accept / Borderline / Reject anchor definitions; those live in
the review form, so the grade below is anchored on the accepted comparators R1–R3 instead.

### 8.2 Round 1 — rendering, typography and structure

| Item | Finding | Severity | Fix |
|---|---|---|---|
| **151** | `pdffonts` showed **every figure embedding DejaVuSerif**, not a Times-metric face. The figures had been rendered in a container without Nimbus Roman installed. | **Major** | All figure scripts re-run inside `cvpr19-video:torch2.7.1-cu128`. Every figure now embeds `NimbusRoman-Regular`. |
| **151** | `fig1_dsec_exposure.pdf` additionally carried a **Type 3** font — `src/make_fig1.py` was the one generator with no `rcParams` block. | **Major** | Added `font.serif`, `mathtext.fontset: stix` and `pdf.fonttype: 42` to `src/make_fig1.py`. |
| **51** | The figure re-render pushed the body to **10 pages**. Diagnosed by comparing MediaBox aspect ratios against a backup: only `fig1_dsec_exposure.pdf` had changed, 0.283 → 0.368. | **Critical** *(page limit)* | **Root cause: `src/make_fig1.py` and `src/make_figs.py` both write `paper/figs/fig1_dsec_exposure.pdf` with different layouts.** `make_figs.py` (`fig1_exposure()`) is the one the page layout is tuned to and **must be run last**. Back to 9 pages. |
| 14 | Abstract carried 3 headline numbers where the item asks for 2–4 and the paper has 4 results worth naming. | Minor | `\flickerLineHz\,Hz` replaced with the paper's own term "mains-frequency harmonic signature", freeing the slot. Abstract now carries exactly **23.81 ms, 0.04 pt, 42.5 %, 5.32 mAP**. |
| 54, 60 | Three comma splices (intro, related work ×2) and one subject–verb disagreement in related work. | Minor | Split into sentences; `"the Prophesee dtype used by Gen1 and the 1 Mpx dataset, and the DSEC-Det format, both have a per-box t."` |
| 60, 193, S6 | Six Title-Case headings remained — one in `main.tex`, five in `supplement.tex`. | Minor | All normalized to sentence case. |

### 8.3 Round 2 — mechanical, AI-style and forensic gates

Re-run after the Round 1 fixes, on the source **and** on the rebuilt PDFs.

| Gate | Result |
|---|---|
| Semicolons (item 61) | **0** in both files |
| `---` em-dashes, `i.e.`, `e.g.` | **0** in both files |
| Raw double quote | 1 in `main.tex`, the LaTeX umlaut in `R\"ohrbein` (bibliography) — false positive, re-confirmed |
| Number–% and unit spacing (item 55) | **0** violations |
| 188–197 + S1–S10 regex gate: `not X but Y`, `what X buys/costs`, anthropomorphism, metaphor, exaggerated adjectives, promo tone, generic significance, `not only … but also`, `We therefore`, `A natural objection`, oral register, lab-notebook phrasing | **0 hits in both files** |
| `tools/style_gate.py` | 4 hits, all previously adjudicated false positives: three true-statement `never` (`main.tex:382`, `main.tex:735`, `supplement.tex:308`) and `analyses`, which is the correct US plural (`supplement.tex:34`) |
| `tools/ai_cadence.py`, main | 249 sentences, mean 21.3 w, **CV 0.51**, short/mid/long 39 / 152 / 58, three-part parallelism **5.6 %** (flag at 15 %), LLM vocabulary **0.00 / 1000** over 5 337 words |
| `tools/ai_cadence.py`, supplement | 293 sentences, mean 21.3 w, **CV 0.55**, three-part parallelism **6.1 %**, LLM vocabulary **0.00 / 1000** over 6 278 words |
| Citation integrity | 37 / 37, no orphans, no duplicates, no undefined, supplement inside the main bibliography |
| PDF active content | `/JavaScript`, `/JS`, `/Annots`, `/EmbeddedFile`, `/Launch`, `/OpenAction`, `/RichMedia`, `/AA`: **none** in either PDF |
| PDF hidden text | 1.95 MB (main) and 2.07 MB (supplement) of decompressed stream content scanned. **Zero** `3 Tr` invisible-text operators. The single `1 1 1 rg` in the supplement is inside a 72×72 hatch-pattern tile with no text operator — benign. |
| Hidden prompt/instruction residue | **None.** No match for `ignore previous`, `as an AI`, `system prompt`, `language model`, model names, `instructions to the reviewer`, `accept this paper` in any decompressed stream of either PDF. |

**Two openers sit at the cadence tool's own flag line in `main.tex`: "On the" 7 / 249 and
"The released" 6 / 249.** Both were read in place and left. "The released X" is the paper's
controlled term for the artifacts it audits, so varying it would trade terminology unity
(item 59) for surface variety, and checklist rule 150 forbids rewriting a sentence merely
because an alternative wording exists.

### 8.4 Round 3 — claims, terminology and evidence correspondence

This round asks a different question from Rounds 1 and 2: not whether the prose is clean but
whether each claim is carried by the artifact it names.

| Item | Finding | Fix |
|---|---|---|
| **59** | **Two words for one operation.** The measured quantity had been renamed to *window-ablation sensitivity*, but the operation producing it was still called *occlusion* in 13 places across both files — `occlude each bin`, `the unoccluded input`, `a single-bin occlusion`, `Occlusion reports the sensitivity of …`. | Unified to *ablate / ablation* at all 13 sites. Zero occurrences of `occlud`/`occlusion` remain in either file. |
| **59** | Two names for one symbol. `main.tex:321` calls $s_k$ the "bin-ablation sensitivity"; five lines later `main.tex:326` defined it as "the influence of bin $k$", with the two never bound. The supplement used "bin-ablation sensitivity" for the same symbol. | One edit at the definition: *"We define the ablation sensitivity, or influence, of bin $k$ as …"*. The synonym is now declared where the symbol is introduced, which also keeps the video's on-screen "window-ablation influence" consistent with the paper. |
| **59** | `main.tex:353` alone read "the **window-ablation-sensitivity** centroid"; everywhere else the quantity is "the ablation-sensitivity centroid". | Normalized. |
| **54, 55** | Spurious precision. `\flickerLineHz` printed **100.00 Hz** in five prose sentences while its siblings `\mainsHz` 50, `\flickerCtrlHz` 137, `\harmSecondHz` 200, `\harmThirdHz` 300 are integers — and one sentence read "…at 100.00 Hz, … at 200 Hz and … at 300 Hz". 100 Hz is a fixed analysis frequency in `src/e10d_null.py`, not a measured peak, so the decimals assert precision that does not exist. Likewise `\dsecCotriggerPct` printed **100.00 %**. | Both → integers. The per-sequence `sixLock*` column keeps two decimals because its other entries (99.63, 95.44) need them. Neither macro is in the audited set, and the audit still returns 269 / 0. |
| **A, 14** | Abstract headline-number count re-verified against the audit: `\rvtCentroidMagMeas` 23.81, `\mapCost` 0.04, `\rankHoldBox` 42.5, `\chunkDidBase` 5.32 — **all four are covered by `src/audit_numbers.py`**, so every number the reader meets first is mutation-tested. | — |
| **71, 99** | Headline DiD re-derived from `experiments/e58_chunkpos/allbox.json` independently of the manuscript: s5vit-base **5.3225 ± 0.5318**, CI **[4.13, 6.23]**, excluding zero; s5vit-small 4.3732 ± 0.6058; RVT placebo largest **0.666**, its CI **[−0.224, 1.417]** spanning zero. Matches the paper. | — |
| **E, 165** | Definition-before-usage: §3.1 is *Definition*; "ablation-sensitivity centroid", "temporal support" and "chunk position" are each defined before their first body use, with forward references where the intro states a result early. | — |
| **52, 62, 69, 80, 87** | No `Limitations` section and no open confession; the bounded-scope section is §5 *Scope of the measurements*. Matches the reviewer guidelines, which state a separate limitations section is not required. | — |

**One structural item inspected and deliberately not changed.** Figure 1 is
`fig_predictor` (the predictor-side audit, carrying 23.81 and 0.04), and the headline 5.32
result is Figure 2, `fig:chunkpos`. The Figure-1-as-Paper item would be better served by a
page-1 teaser carrying the chunk-position curve. The body is **exactly at the 8-page limit**,
so a teaser must be paid for by deleting measured content, and the manuscript is under a
freeze instruction. Recorded as an accepted, bounded design decision rather than an open
defect.

### 8.5 AI-Style Gate

| Probe | Result |
|---|---|
| LLM vocabulary repetition | 0.00 per 1000 words in both files |
| Rhetorical-contrast overuse | 0 hits |
| "This finding underscores / highlights" and generic significance sentences | 0 hits |
| Identical sentence cadence | CV 0.51 / 0.55 — wide, not uniform |
| Three-part parallelism | 5.6 % / 6.1 %, against a 15 % flag |
| Exaggerated adjectives | 0 hits |
| Citation–claim correspondence | 37 / 37 cited, every `\bibitem` reached, none orphaned |
| Existence of every reference | The 37 entries are the paper's own bibliography, unchanged since the author-kit switch; the five *grading standards* R1–R5 were each fetched and their venue confirmed in this session |
| Hidden prompt or instruction text in the LaTeX or PDF | **None** — see the forensic row in Sec. 8.3. No `\color{white}`, `\phantom` or shrunken-font construct appears in either source. |

**GPTZero:** `tools/gptzero_audit.py` exists and reads its key from `$GPTZERO_API_KEY`. That
variable is **not set in this environment**, so no detector pass was run.
`.ai-audit/gptzero_raw.json` records `status: not_run` truthfully rather than carrying a
fabricated score, and `AI_WRITING_AUDIT.md` states it as a limitation. No REWRITE passage was
raised by the local gates, so the second-pass edit protocol was not triggered.

### 8.6 Video inspection

`video/CVPR20_paper_video.mp4`, 87.936 s, 1280×720, 30 fps, nine scenes, rebuilt by
`video/build.sh` after the fixes below. Every frame is rendered by a script in `src/v0*.py`
that reads its numbers from the experiment artifacts at render time, so no number on screen
is typed by hand.

| Check | Result |
|---|---|
| Title card duration (item 0: 1.5–2.5 s) | 2.2 s |
| Actual-evidence ratio, strict reading | 46.2 s = **52.6 %** (target ≥ 50 %) |
| Actual-evidence ratio, §25 list | 66.2 s = **75.3 %** |
| Novelty-carrying scenes | 39.9 s = 45 % |
| Architecture after results | yes — no architecture scene precedes the chunk-position result |
| Climax = strongest actual evidence | scene 3, the chunk-position curve with the +5.32 ± 0.53 readout |
| Typography (item 151) | Nimbus Roman throughout |

Defects found and fixed during this inspection: **2 Critical, 2 Major, 5 minor**, listed in
`video/README.md` under *What inspection caught*. The last one found was a **double negative
on screen** — `'%.2f ms before the label' % centroid_ms` printed "−23.81 ms before the
label". Fixed with `abs(...)` in `src/v02_support_clip.py`, v02's 190 frames re-rendered, the
cut rebuilt, and the fix **verified by cropping and reading the actual PNG** rather than
assumed. The video's on-screen term *window-ablation influence* remains correct under the
Round 3 terminology fix, because "influence" is now declared as the synonym at the point the
symbol is defined.

### 8.7 Relative grade against R1–R3

| Reviewer axis | This paper | Nearest accepted comparator |
|---|---|---|
| Technically sound | 269 mutation-tested macros; permutation null at 9.84σ / 7.61σ; RVT placebo control with a CI spanning zero; three independent verification routes in `docs/VERIFY_3ROUND_E58.md` | Above R1 and R2, neither of which mutation-tests its reported numbers |
| Contribution to the field | A measured property of two released event-detection benchmarks that no prior paper in the domain reports | R1 makes the same *kind* of contribution — benchmark timing is unreliable, ranking moves — and was accepted at CVPR 2026 while disclaiming method novelty |
| Novelty | Chunk-position identifiability and the horizon-dependence of the support centroid are both new | R2 is the precedent that a metric-property finding, with no method, is a CVPR contribution |
| Significance | **5.32 ± 0.53 mAP** on a released, published number. R4's own headline effect, on the same architecture family, is **3.76 mAP**. | The effect this paper measures is **larger than the headline effect of the Spotlight paper whose checkpoints it is measured on** |
| Datasets | Gen1 and DSEC — 2, within the item-53/88 standard | R4 uses 2 (Gen1, 1 Mpx); the guidelines explicitly bless "novel, brave concepts, even if they have not been tested on many datasets" |
| Evidence and clarity | 8-page body at the limit, 0 overfull, Times-metric figure text, no Type 3, neutral headings, 4 audited headline numbers in the abstract | At or above all three comparators |
| Reproducibility | Released artifacts only; every probe, formula and bootstrap specified in supplement §12–13 | Above R2 |

**No Critical or Major finding is open.** The three Major/Critical items raised in this pass
— DejaVuSerif in every figure, the Type 3 font, and the 10-page regression — were all fixed
and re-verified against the rebuilt PDFs.

## **ACCEPT** *(third pass, unchanged from the second)*

The grade holds for the reason the guidelines give directly: an accepted paper "should be
technically sound and make a contribution to the field", and failing to beat a benchmark "is
not grounds for rejection by itself". R1's acceptance at CVPR 2026 — a paper that states it
proposes no novel method and whose result is that legacy benchmark timestamps produce
unreliable rankings — is the closest available evidence that this paper's *type* clears the
bar. On significance the comparison is favorable in the strongest available direction: the
effect measured here, 5.32 mAP, exceeds the 3.76 mAP headline of the Spotlight paper whose
released checkpoints it is measured on.

**The distance to Strong Accept is unchanged and is a single named experiment**, not a
writing defect: a third detector lineage outside the RVT / SSM-ViT repository, which would
turn the chunk-position result from a property of two released checkpoint families into a
property of the protocol class. It is scoped in `paper/OUTSTANDING.md`, requires GPU 1, and
is deferred by the freeze instruction. Two smaller items in the same category — bootstrap
re-selection of the specification (item 6) and a sequence-stratified cluster bootstrap over
lags (items 8/9) — are also GPU-bound and also deferred.

Three rounds run, all gates green, no Critical or Major finding open. A fourth round
follows in Sec. 9; it is the one that closes the review.

---

## 9. Fourth pass — writing audit regenerated, three defects found and closed

The third pass left `AI_WRITING_AUDIT.md` stale: its top-ranked finding quoted a comma
splice that had already been repaired, so the report described a manuscript that no longer
existed. Regenerating it surfaced two measurement bugs in the auditing tool itself and three
real defects in the prose.

### 9.1 Two bugs in `tools/gptzero_audit.py`, fixed

| Bug | Effect | Fix |
|---|---|---|
| `source_chunks()` globbed every `*.tex` under the repository root | `submission_package/main.tex` and `supplement.tex` are verbatim copies, so every chunk and every finding was counted twice — 343 chunks reported against 178 real ones | `submission_package` added to the skip set |
| The residue scan pooled `paper/`, `src/` and `docs/` into one list | The terms it looks for (`prompt`, `instruction`, `rewrite`, `placeholder`) legitimately occur in the tooling and in this verdict document, so internal notes were reported beside the manuscript and the gate became unreadable | The scan now reports `paper/*.tex` — the files that actually ship — separately from the rest |

After the fix: 178 chunks, **0 REWRITE**, 178 REVIEW, 395 SAFE. Because the count of
REWRITE passages is zero, the second-pass edit protocol was not triggered; no passage was
rewritten under it.

`GPTZERO_API_KEY` is not set on this machine. `.ai-audit/gptzero_raw.json` therefore records
`{"status": "not_run", "reason": "GPTZERO_API_KEY is not set"}`. No detector score is
reported and none is inferred from the local heuristics. The key is read from the
environment and is never written to any file.

### 9.2 Manuscript residue

One hit in the shipped sources, both occurrences in `paper/numbers.tex`:

```
78:  % that could use them and are left undefined rather than rendering a placeholder.
276: \newcommand{\tauHatRVT}{\rvtCentroidMeas}  %% E17, no longer a placeholder
```

Both are LaTeX comments describing the macro file's own fallback behavior and its
provenance. Neither renders, neither reads as an instruction to a language model, and both
are accurate. Kept.

### 9.3 Three prose defects, fixed

Read the top-20 flagged passages in place against their sources. Seventeen were artifacts of
the extractor: `visible()` strips `$...$` and macro calls, so a sentence carrying six numbers
reads as a run-on once they are removed. Three were real.

A dedicated scan for clause chains — a capitalised sentence joined by `, and` twice or more —
returned exactly three hits across both documents.

| # | File:line | Defect | Change |
|---|---|---|---|
| 1 | `paper/main.tex:616` | Three clauses joined by two `and`s: `…is nearly invariant over X, and at Y the ordering is unchanged, and scoring each checkpoint…` | Second `and` replaced by a sentence break: `…is unchanged. Scoring each checkpoint…` |
| 2 | `paper/supplement.tex:728` | Same pattern: `…running 1.8× above d*, and its N boxes cannot explain a gap that size, and the likeliest cause is…` | `…a gap that size. The likeliest cause is…` |
| 3 | `paper/main.tex:616` | Two sentences three apart in one paragraph both opened `On the` (l. 612 `On the −50 to +30 ms grid…`, l. 616 `On the velocity-evaluable subset…`) | Subject moved forward: `Average precision on the velocity-evaluable subset is nearly invariant…` |

The third hit of the clause scan, `…the medians of X, Y, and Z over eligible frames`
(`paper/supplement.tex`), is an Oxford-comma list, not a clause chain. Unchanged.

All three edits preserve every number, citation and controlled term; none is a rewrite for
variety, and each repairs a defect a reader would trip on (items 137–151, and item 150's
prohibition on rewriting merely because an alternative wording exists).

### 9.4 Full gate re-run after the edits

| Gate | Result |
|---|---|
| Build, `main` | 9 pages, body 8, References open page 9, undef 0, overfull 0 |
| Build, `supplement` | 10 pages, undef 0, overfull 0 |
| Standalone build of `submission_package/` from a clean copy | 9 / 10 pages, undef 0, overfull 0, 0 missing-figure placeholders |
| Number audit | 269 macros checked, 0 disagree; 269/269 reject a corrupted value; blind none |
| Mechanical + AI-style regex gate (15 patterns) | **0 hits** |
| Clause-chain scan | 0 (one Oxford list, correct) |
| Terminology, `occlu*` | 0 in both files |
| Cadence, `main` | 250 sentences, mean 21.2 w, CV 0.51, three-part 5.2 %, LLM vocabulary 0.00 / 1000 over 5339 w, no opener above the flag line |
| Cadence, `supplement` | 294 sentences, mean 21.3 w, CV 0.54, three-part 6.1 %, LLM vocabulary 0.00 / 1000 over 6277 w, no opener above the flag line |
| Citations | 37 bibitems, 37 cited, 0 undefined, 0 orphaned, 0 duplicated |
| PDF forensics | `/JavaScript` `/JS` `/Annots` `/EmbeddedFile` `/Launch` `/OpenAction` `/RichMedia` `/AA` all 0; 1 949 026 + 2 068 419 decompressed stream bytes, 0 prompt/instruction residue; 0 invisible-text (`3 Tr`) operators |
| Fonts | 23 (main) and 29 (supplement), all embedded and subset, **0 Type 3** |
| Video | 87.936 s, 1280×720, 30 fps, 9 scenes, title card 2.2 s; actual-evidence 52.6 % strict / 75.3 % by the checklist's own scene list; all on-screen text Nimbus Roman |

The `main.tex` cadence flag recorded in the third pass — `On the` at 7/249 — is now at the
threshold rather than above it, and the fix was a real local repetition rather than a
concession to the statistic.

### 9.5 Housekeeping

Scratch removed from the tree: six page-preview PNGs in `paper/`, five in `paper/figs/`,
four `pdftotext`/`pdftohtml` dumps, and `src/e51_orig_cpu.py`. `submission_package/` was
deleted and rebuilt from the current `paper/`: it no longer carries `.aux`, `.log`, `.out`,
`.blg`, `.brf` or the two 0-byte `.bbl` files, and its `README.md` was rewritten, the old one
having stated the previous title, a 9-page supplement, a 237-macro count, and a caveat that
the video predated the chunk-position result. All four were out of date. `figs/` ships the
eight PDFs the sources actually reference; `fig2_evidence_time.pdf` exists in `paper/figs/`
but is referenced by neither document and is not shipped.

### 9.6 Verdict

Four rounds run. Round 4 found three prose defects and two bugs in the audit tooling, fixed
all five, and re-ran every gate clean. No Critical or Major finding is open, and the grade of
Sec. 8 is unchanged:

## **ACCEPT** *(fourth pass, unchanged)*

The distance to Strong Accept is the same single GPU-bound experiment named in Sec. 8 — a
third detector lineage outside RVT / SSM-ViT — and is not a writing defect.

Review **complete**.

---

## 10. Fifth pass — external feedback #11 (MUST-FIX set, section-B checklist, novelty)

Review #11 arrived as three parts: a MUST-FIX list on the framing and the abstract, a
section-B pass over the mechanical checklist, and a section-C novelty assessment placing the
paper against SSM-ViT (CVPR 2024), *Seeing Motion at Nighttime* (CVPR 2024), LEOD (CVPR
2024), Ev-3DOD (CVPR 2025) and ASTW (CVPR 2026), with no direct overlap found. The review
also fixed a working order, and that order was followed.

### 10.1 MUST-FIX disposition

| # | Ask | Disposition |
|---|---|---|
| MF1 | Rename the metric-noise / resolution language to sequence-resampling uncertainty | **Done** (fourth-pass session), verified by build and by the 270-macro audit |
| MF2 | A formal identifiability definition at the head of Sec. 3.1 | **Done.** New `\subsection{Identifiability and the timing estimands}`: the released tuple (nominal timestamp, labels, predictions, score), the three latent quantities (predictor temporal support, effective state time, label acquisition support), *identified* = the released protocol and artifacts determine the quantity uniquely, and the paper's claim that the nominal timestamp alone does not |
| MF3 | Re-verify `c_s`, the newest-window share and the 500/1000 ms centroid over 50–100 sequences or the full validation split, sequence-stratified, rather than the first 12 lexicographic sequences | **Open, GPU-bound.** Only GPU 1 is available and it is committed; this is a re-sampling of an existing measurement, not a new claim |
| MF4 | Explain the main/supplement τ mismatch (−2.40 ± 7.18 over 22 534 against −2.96 ± 7.12 over 22 518) | **Done**, and machine-checked by the new `assocGateVsTable` entry in `src/audit_numbers.py` |
| MF5 | Fig. 1 caption against the figure | **Done the stronger way.** Rather than weakening the caption, the regression coefficient was drawn: panel (a) now carries `τ_P = −τ` as a dash-dot line with a ±1 SE marker and an explicit 26.2 ms span annotation against the ablation-sensitivity centroid |
| MF6 | Three supplement cross-reference errors | **Done** (fourth-pass session) |
| MF7 | State that 100 Hz is prespecified by the 50 Hz Swiss mains and that the broadband sweep is descriptive | **Done.** Sec. 4.2 now fixes the tested frequency from mains physics before any spectrum is read, and declares the sweep descriptive |
| MF8 | Keep DSEC as attribution failure, not causation; ban `caused by illumination` | **Already satisfied — verified, not edited.** A six-pattern causal-language scan over both manuscripts plus a full read of supplement Sec. 8 and `tab:controls` found only attribution-limit phrasing ("limits attribution of…", "confounded with illumination structure", "induces temporal structure without object motion") and no instance of the banned phrase. Left unchanged under item 150 |
| MF9 | The centroid and the regression coefficient as two distinct operational timing quantities, never a "timing error" or "latency" | **Done.** The abstract now reads "They are two distinct operational timing quantities, not two estimates of one latent time." A repository-wide scan for the banned nouns found one survivor, `supplement.tex:696` "timing errors of this size", describing the displacement a leaderboard could resolve; changed to "timing displacements of this size" |
| MF10 | Separate the two populations in the abstract | **Done.** "On the velocity-evaluable subset, displacing ground-truth centers … by \mapCost points and reorders no checkpoint. Separately, over all labeled boxes, a sequence bootstrap reproduces the published ordering in only \rankHoldBox %" |
| P7 | Compress the abstract onto one spine: one timestamp → several non-equivalent temporal quantities | **Done.** The abstract opens on that sentence and every later clause hangs off it |

### 10.2 Section-B checklist items

| Item | Disposition |
|---|---|
| 8-page limit, semicolons, "first" overclaim, British spelling | Already passing; re-verified (0 semicolons, 0 em-dashes, 0 overclaim patterns, 0 British forms in both files) |
| Abbreviation first use | **Done in the abstract, where each abbreviation now first appears expanded and in order:** *recurrent vision transformer (RVT)*, then *mean average precision (mAP)*, then *the state-space detector SSM-ViT* |
| Raw-quote sentence in the supplement | Removed (fourth-pass session) |
| Heading `What is not shown here.` | **Renamed** to `Validation-split and checkpoint-port limitations.` (`supplement.tex:369`) |
| Fig. 1 too small | **Enlarged** to full `\columnwidth` with larger type (fourth-pass session) |
| Supplement p. 10 whitespace | Accepted by the reviewer; unchanged |

### 10.3 Defects this pass found that no earlier pass could

1. **`paper/figs/fig_predictor.pdf` still rendered the withdrawn term "occlusion influence."**
   Every earlier terminology gate scanned `.tex` only, so a term retired from the prose survived
   inside a figure for four passes. Fixed at the source (`src/make_figs.py`, y-label now
   "window-ablation influence") and regenerated. A figure-PDF text scan
   (`pdftotext figs/*.pdf | grep -i`) is now part of the gate set and returns 0 over eight PDFs
   for `occlu*`, `metric noise`, `resolution limit`, `timing error` and `latency`.
2. **`tools/ai_cadence.py` was miscounting and mislabelling.** It split sentences on any period,
   so `Sec.`, `Eq.`, `Fig.` and `Tab.` each manufactured a spurious sentence start and inflated
   the opener-repetition counts (main read 249 sentences against a true 236), and its printed
   header announced a flag line of 6 while the code flagged at 12. Both fixed. The tool was the
   instrument the third and fourth passes graded prose with, so its numbers are restated below.
3. **An abstract long enough to leave the first column half empty.** The first rewrite ran 33
   lines, pushed the Introduction heading into the right column, and `\flushbottom` stretched the
   only rubber glue left in the left column into a one-inch gap under the word *Abstract*. Caught
   by rasterizing page 1 rather than by any textual gate. The abstract was tightened to 32 lines,
   which restores the heading to the left column and closes the gap.

### 10.4 Page budget

Every addition was funded by a named deletion, so the body still ends on page 8.

| Change | Cost | Funded by |
|---|---|---|
| MF2 identifiability paragraph | +6 lines | two genuinely redundant Introduction passages and a results recap misplaced in Related Work |
| MF7 mains-physics sentences | +2 lines | a tightened Conclusion |
| Abstract rewrite (MF9, MF10, P7, three abbreviation expansions) | +10 lines at first draft | the two Introduction sentences duplicated elsewhere (the `rvt-b`/S5-S stratum inversion, already at `main.tex:624`; the p90/p99 pixel restatement, already in the Fig. 1 caption) plus a tightening of the abstract itself |

Body 8 pages, ending at CVPR review line 654; References 655–780; 9 pages total.

### 10.5 Full gate re-run

| Gate | Result |
|---|---|
| Build, `main` | 9 pages, body 8, References open page 9, undef 0, overfull 0 |
| Build, `supplement` | 10 pages, undef 0, overfull 0 |
| Standalone build of `submission_package/` from a clean copy | 9 / 10 pages, undef 0, overfull 0, 0 missing-figure placeholders |
| Number audit | **270 macros checked, 0 disagree; 270/270 reject a corrupted value; blind none** |
| Mechanical style gate | 4 hits, all inspected and kept: `analyses` (the noun plural, not the British verb) and three exact uses of `never` (a rule that never tests overlap, a scan whose outputs never read the coefficient, a harmonic never falling below a level). Item 150 forbids rewriting these for the statistic |
| Cadence, `main` (repaired tool) | 236 sentences, mean 22.5 w, cv 0.50, top opener 6 (flag 12), three-part 5.9 %, LLM vocabulary 0.00 / 1000 over 5 314 w |
| Cadence, `supplement` (repaired tool) | 275 sentences, mean 23.2 w, cv 0.52, top opener 6 and it is `main sec` — a cross-reference, not a prose habit — with the first prose opener at 5, three-part 6.9 %, LLM vocabulary 0.00 / 1000 over 6 385 w |
| Figure-PDF terminology (new gate) | 0 hits over eight PDFs |
| Citations | 37 `\bibitem`, 37 cited, 0 undefined, 0 orphaned |
| PDF forensics | `/JavaScript` `/JS` `/Annots` `/EmbeddedFile` `/Launch` `/OpenAction` `/RichMedia` `/AA` all 0 in both files; 1 960 466 + 2 072 017 decompressed stream bytes with 0 prompt or model residue; 0 invisible-text (`3 Tr`) operators |
| Fonts | 24 faces in `main.pdf`, **all embedded and subset, 0 Type 3, 0 unembedded**. Poppler emits four `Mismatch between font type and embedded font file` warnings: matplotlib writes the CFF-flavoured Nimbus Roman OpenType under `/FontFile2`. Page-1 rasterization at 150 dpi renders every glyph correctly, and the alternative — reflowing eight figures onto a TrueType Times clone with the body at exactly 8 pages — buys nothing a reviewer sees. Kept, and recorded here rather than silently |
| Video | Unchanged and still current: it draws `\rvtCentroidMagMeas`, the E42 tail centroid and `E27['tau']`, none of which moved this pass, and its title card already carries the current title |
| AI writing audit | **Not re-run.** `$GPTZERO_API_KEY` is unset in this environment, and the specification forbids hard-coding it. `AI_WRITING_AUDIT.md` therefore predates the abstract rewrite of this pass; the local half of that gate (cadence, LLM vocabulary, style regex, PDF residue) was re-run and is above |

### 10.6 Grading against the external standard

Graded against `docs/REFERENCE_PAPERS.md`, five papers fetched as full PDFs from
`openaccess.thecvf.com` and read from the PDF, with R2 (*On the Content Bias in Fréchet Video
Distance*, CVPR 2024) as the closest structural match: a measurement paper whose contribution
is that an accepted metric does not measure what it is read as measuring.

Against R2 the fifth pass closes the gap that mattered. R2 states its estimand before it
measures anything; until MF2 this paper measured first and defined after, and a reviewer
reading Sec. 3.1 could not tell which quantity was claimed unidentifiable. That is now the
opening move of the section. MF9 and MF10 remove the two readings a hostile reviewer would
have taken from the abstract — that 26.2 ms is an error in someone's clock, and that 0.04 mAP
and 42.5 % describe one population. Neither survives the current text.

What still separates this from R2's acceptance profile is breadth, not framing, and it is the
same distance named in Sec. 8 and unchanged since: the chunk-position result rests on two
checkpoint families, and MF3 asks for the ablation-sensitivity measurements to be re-sampled
over 50–100 sequences instead of 12. Both are GPU-bound, both are scoped in
`paper/OUTSTANDING.md`, and neither is a writing defect.

Five rounds run. No Critical or Major writing finding is open.

## **ACCEPT** *(fifth pass — at the upper end, with the two GPU-bound items of Sec. 10.6 standing between it and Strong Accept)*

Review **complete** for every non-GPU item of feedback #11.

---

## 11. Sixth pass — external feedback #12, and the one experiment it asked for

Feedback #12 arrived as two parts: two `MUST FIX` defects, three methodological demotions,
two items to *leave alone*, one checklist error, and a six-step "Strong Accept minimum path".
Every non-GPU item is closed. The path item that was not a writing change — a same-frame
chunk-boundary intervention — was run on GPU 1 and is now in both documents.

### 11.1 The two MUST FIX items

**MF12-1, Supplement Table 4.** The column labelled `difference` carried the
control-adjusted point estimate while the `short` and `full` columns carried raw scores, so
the table's own arithmetic did not close: `short` 34.4 and `full` 40.2 imply −5.8, not the
−5.32 printed. The reviewer read this correctly. The table now has two separate columns,
`raw ΔmAP` and `ΔmAP net of RVT control (±SE)`, the raw column reproduces Main Fig. 2's
5.78 and 4.83 exactly, and all five checkpoints' rows close against their own `short` and
`full` entries. Both columns are audited macros.

**MF12-2, "published ordering".** The phrase asserted something the paper does not
measure: the published Gen1 table is a test-split result and every measurement here is on
validation. Replaced everywhere, including each 42.5 % sentence, with
`validation-split ordering at the nominal label time` and, where the referent is the
artifact evaluation rather than the split, `reference ordering under our released-artifact
evaluation`. A grep for the old phrase over both documents returns zero.

### 11.2 The three demotions

1. `regression-based effective timestamp` → `regression-implied timestamp under Eq. 2`.
   Standalone `effective timestamp` is gone from the Fig. 1 caption, the Abstract and the
   Conclusion. It survives at one site only, main.tex:246, which is the sentence that
   *defines* $\tau_P$ inside the signed effective-weight model and is immediately followed
   by the statement that it is a different quantity from the sensitivity centroid. That is
   the one place the term is load-bearing rather than rhetorical.
2. **Abstract evidence order.** Rebuilt to the requested ①–⑤. Measured positions in the
   abstract source: the 5.32 mAP chunk-position result at character 726, the same-frame
   replication at 844, DSEC at 1612, the 0.04 mAP Gen1-composition result at 1956. The
   0.04 mAP number is now last, not first.
3. **Contribution spine.** The Introduction closes on
   *"A nominal benchmark timestamp does not identify the temporal support on either side of
   an event-detection score"*, with exactly three items beneath it — predictor
   input/support, evaluation support, label acquisition support. `benchmark temporal-support
   identifiability` is named there as the novelty against the accepted prior work.

### 11.3 The two items to leave alone

Both verified unchanged. The recurrent-tail asymptotic claim is still conditional, and DSEC
is still phrased as *preventing attribution without separation* rather than as illumination
causing object timing. No edit was made to either, which is the disposition the feedback
asked for.

### 11.4 The checklist error

Supplement Fig. 3's caption read `every labelled box`. Now `every labeled box`. A scan of
both documents and all ten figure PDFs for `labelled|behaviour|modelling|occlusion|effective
timestamp|published ordering` returns zero hits in figures and, in the body, only the single
licensed `effective timestamp` of Sec. 11.2.

The same feedback said the Introduction pre-releases too many numbers. SE ranges, the
inversion probability and the detailed bootstrap figures moved to Results; the Introduction
now carries the effect sizes and not their dispersion.

### 11.5 The experiment: a same-frame chunk-boundary intervention

This was both the reviewer's Strong Accept path item and the substance of the earlier
question about the minimum extra experiment. It removes the parallel-trends assumption that
the placebo-differenced design needs.

Design. Every chunk boundary in the released streaming evaluation is displaced 5 windows
later, so position $p$ becomes $(p-5)\bmod 21$ and the starved block at positions 0–3 is
carried onto 16–19. The 3 574 frames that make that crossing are scored twice — once under
one to four windows of recurrent history, once under seventeen to twenty — with the same
weights, the same ground truth and the same frames. No control model and no parallel-trends
assumption enters. Shifting *earlier* does not work: the release's own start expression is
`max(first_label − 20, 0)`, which is already clamped at 0 for most Gen1 sequences, so the
subtraction is a no-op on 14 927 of 20 296 frames. The verification log records that
asymmetry rather than hiding it.

Result, the two quantities the feedback asked for, cluster-bootstrapped over the same 406
sequences with 300 replicates:

| paired quantity, 3 574 frames | S5-B | S5-S |
|---|---|---|
| ΔmAP, velocity-evaluable (pt) | +5.23 ± 0.49 (z = 10.7) | +4.81 ± 0.52 (z = 9.3) |
| Δ mean detection confidence | +0.0579 ± 0.0048 (z = 12.0) | +0.0509 ± 0.0035 (z = 14.6) |

Both reproduce the 4–5 mAP direction. The result that matters most for the review is the
agreement: on S5-B the same-frame estimate of 5.23 and the placebo-differenced estimate of
5.32 differ by 0.09 mAP points, well inside either standard error. Two designs with
different assumptions, one checkpoint, the same answer. That is recorded as an audited
macro rather than asserted.

The mechanism rows say what moves. Confidence rises on the detections that match a label
(+0.0409 and +0.0519) and total output falls (−3.49 and −5.09 boxes per frame), so both
terms of precision move together: the starved arm emits more boxes and scores the real ones
lower.

**A real bug was found and fixed while doing this.** `iou_mat` in `src/e56_eval.py` reads
columns 0..3 of its arguments as the box, and two call sites passed full 7- and 8-column
rows, computing IoU over `[frame, x1, y1, x2]`. One was in the new figure script, one was
pre-existing in `src/e60_paired.py`. Symptom: 67 matched detections against roughly 7 400
labels. `map_vel` and `map_all` route through `Scorer.evaluate`, which slices correctly, and
`conf` and `dpf` are raw per-frame sums, so every headline number was unaffected — but the
matched-confidence row was wrong, and the prose built on it claimed the opposite mechanism
("matched confidence barely shifts"). Both call sites are fixed, the analysis was re-run,
and the invalidated sentence was rewritten to what the corrected numbers say.

### 11.6 The experimental-result image

The main paper carried no qualitative detection image, which for a CVPR submission is a real
gap. Main Fig. 2 now has a second panel row: one Gen1 frame under both chunk positions,
identical frame, identical labels, identical weights, only the boundary displaced. The
starved arm matches 0 of the 4 labels and returns 2 unmatched boxes; the long-history arm
matches 3 and returns none.

The caption does not let that frame stand in for the average. It says the frame is the
clearest of the 3 574 pairs and gives the population beside it: matched labels per frame go
from 1.40 to 1.53, the long arm matching more on 13.1 % of frames and fewer on 2.7 %. All
ten of those numbers are read from `experiments/e60_shift/figframe.json` by
`src/audit_numbers.py`, not typed.

### 11.7 Page budget

Adding the figure pushed the body onto page 9 by 12 CVPR lines. Funded without deleting a
result, in this order: the two chunk-position figures merged into one float with one caption
(they are two views of the same result, so the second caption was redundant); the new
figure's panel labels moved out of a title strip and its crop tightened, which made the
panels both shorter and larger; Figs. 1, 3 and 4 shrunk by 5–20 %, then partly restored once
the budget allowed, and each re-inspected at 300 dpi; one orphan single-sentence paragraph
folded into the paragraph it belongs to; and one clause dropped from Sec. 3.3 — the
detections-per-frame figure, which the supplement's paired table reports in full and which,
after its numbers moved there, was an unquantified assertion in the main text.

Body ends on page 8 (CVPR line 654), references occupy page 9, 9 pages total. Every figure
was rasterized and read after each change; the two panels of the new figure are legible at
print size and their labels no longer collide with the panel borders.

### 11.8 Gate state after the sixth pass

| gate | result |
|---|---|
| `src/audit_numbers.py` | 314 macros checked, 0 disagree; self-test 314/314 reject a corrupted value, blind: none |
| main.pdf | 9 pages, body ends p8, 0 undefined, 0 overfull, 25/25 fonts embedded |
| supplement.pdf | 10 pages, 0 undefined, 0 overfull, 29/29 fonts embedded |
| citations | 37 bibitems, 37 cited, 0 orphans, 0 missing |
| floats | 6 floats, all referenced |
| figure fonts (item 151) | Nimbus Roman in all four regenerated figures, STIX for math italic |
| style gate | 4 hits, all four pre-inspected and kept |
| cadence | 520 sentences, top opener 9 (flag at 12), three-part lists 7.1 % (flag at 15 %), LLM vocabulary 0.00 per 1000 |
| figure-PDF text scan | 0 banned terms across all ten figure PDFs |
| `submission_package/` | main/supplement/numbers/PDFs byte-identical to `paper/`, all ten figures synced, both documents build standalone in a scratch copy at 9 and 10 pages, README macro count 270 → 314 |

Two package defects were found and fixed in the process: `figs/` was missing
`paired_frame.pdf` and `fig2_evidence_time.pdf`, so the package could not build standalone
at all, and a build run inside the package directory deleted its `main.pdf` (restored,
byte-identical; package builds are now done in a scratch copy).

### 11.9 External grading, sixth pass

Graded against the same five papers in `docs/REFERENCE_PAPERS.md`, R2 (*On the Content Bias
in Fréchet Video Distance*, CVPR 2024) still the closest structural match.

The fifth pass placed this at the upper end of Accept with two GPU-bound items standing
between it and Strong Accept: the chunk-position result resting on two checkpoint families,
and MF3's request to re-sample the ablation-sensitivity measurements over 50–100 sequences
instead of 12.

The same-frame intervention changes the first of those less than it changes something else.
It does not add a third detector lineage — it is still S5-B and S5-S. What it removes is the
strongest methodological objection available to a reviewer: that the 5.32 mAP headline is a
difference-in-differences whose validity rests on an untestable parallel-trends assumption
about RVT and SSM-ViT responding alike to frame composition. A within-frame, within-model,
same-weights paired comparison needs none of that, and it returns the same number to 0.09
points. R2's own structure is exactly this — a claim about a metric, then an intervention
that isolates the mechanism — and R2 gets there with one family of generators.

What has not changed is breadth. R2 grades out where it does partly because its claim is
tested across generator families a reader already trusts separately. Here the third detector
lineage outside RVT/SSM-ViT is still absent, and MF3 is still open, both GPU-bound, both
scoped in `paper/OUTSTANDING.md`. That is the same distance named in Secs. 8 and 10 and it
is not a writing defect.

Six rounds run. No Critical or Major writing finding is open. Every item of feedback #12 is
closed, including the one that required GPU work.

## **ACCEPT** *(sixth pass — at the upper end. The same-frame intervention removes the parallel-trends objection and adds the paper's first qualitative result figure; the remaining distance to Strong Accept is breadth, which is GPU-bound and scoped.)*

Review **complete** for every item of feedback #12.

---

## 12. Third verification round of the sixth pass — two defects the gates could not see

The sixth pass was recorded as closed. Re-checking its own claims against the artifacts (the
standing "수정이 완료되면, 논문체크리스트는 항상 기억해서 검수해줘") found two things no
mechanical gate reports, because both are consistency defects between numbers that each pass
their own check.

### 12.1 Supplement Table 4 did not close arithmetically (MF12-1, re-opened and now closed)

§11.1 recorded that Table 4's raw ΔmAP column had been separated from the RVT-control-adjusted
column and matched main Fig. 2's 5.78 / 4.83 exactly. Both were true. What was not true is
that a reviewer differencing the table's own `short` and `full` columns reproduces the raw
column — which is the whole reason MF12-1 asked for the separation. At one decimal:

```
  row      short   full    full-short   printed raw   closes
  rvt-t     38.2   38.2      +0.0          +0.01     no (the difference is invisible)
  rvt-s     38.4   39.2      +0.8          +0.80     yes
  rvt-b     41.6   42.1      +0.5          +0.56     no
  S5-S      31.6   36.4      +4.8          +4.83     no
  S5-B      34.4   40.2      +5.8          +5.78     no
```

The caption had been patched with a disclaimer ("the short and full columns are rounded to one
decimal, so differencing them reproduces the raw column only to that precision"). A disclaimer
that explains why the arithmetic fails is weaker than arithmetic that works.

Three routes were measured against the full-precision `experiments/e58_chunkpos/allbox.json`:

```
  rvt-t        short 38.179921  full 38.194128  diff +0.014207
  rvt-s        short 38.370587  full 39.166770  diff +0.796184
  rvt-b        short 41.560809  full 42.125502  diff +0.564693
  s5vit-small  short 31.578044  full 36.409650  diff +4.831606
  s5vit-base   short 34.444648  full 40.225509  diff +5.780861
```

- **2 decimals** closes three rows and leaves two: rvt-b reads 42.13 − 41.56 = +0.57 against a
  printed 0.56, and S5-B reads 40.23 − 34.44 = **+5.79 against a printed 5.78**.
- **2 decimals with the raw column re-derived from the rounded operands** closes all five, but
  moves the raw value to 5.79 — and therefore main Fig. 2's caption. Feedback #12 required the
  opposite ("Main Fig.2의 raw 5.78/4.83과도 정확히 일치시킬 것"), so this route is excluded.
- **3 decimals** closes all five against the raw values already published, changing nothing
  else. This is the minimum-change route under checklist item 150.

Applied: the ten cells `\chunkShort{T,S,B,Small,Base}` / `\chunkFull{...}` now carry three
decimals; `src/audit_numbers.py` tolerances on those ten tightened 0.05 → 0.0006; the caption
disclaimer replaced by the fact ("carry three decimals, so differencing them reproduces the raw
column exactly"). Verified from the rendered PDF text, not the source:

```
  rvt-t   38.194 − 38.180 = +0.014 -> +0.01   printed +0.01   closes
  rvt-s   39.167 − 38.371 = +0.796 -> +0.80   printed +0.80   closes
  rvt-b   42.126 − 41.561 = +0.565 -> +0.56   printed +0.56   closes
  S5-S    36.410 − 31.578 = +4.832 -> +4.83   printed +4.83   closes
  S5-B    40.226 − 34.445 = +5.781 -> +5.78   printed +5.78   closes
```

`\chunkRiseBase` 5.78 and `\chunkRiseSmall` 4.83 are untouched, so main Fig. 2 still matches.
A side effect worth recording: main Sec. 3's prose sentence (main.tex:372) now reads
34.445 → 40.226, which differences to 5.78 as well. At one decimal it differenced to 5.8.

### 12.2 Three supplement floats had no in-text pointer, and a fourth had no label

The float gate had only ever been run over `main.tex` ("6/6 floats referenced"). Run over the
supplement it reports three floats that nothing points to — `fig:chunkfull`, `tab:paired`,
`fig:sweepreal` — and the checkpoint-ordering table at supplement.tex:632 carries no `\label`
at all, so the gate could not even see it. A CVPR reviewer reaching an unreferenced float has
to guess what it belongs to.

- `fig:chunkfull` — the placebo sentence in the same section now ends `(Fig.~\ref{fig:chunkfull})`.
- `tab:paired` — "The remaining two rows" → "The remaining two rows of Tab.~\ref{tab:paired}".
- `tab:ordering` — label added, and the sentence that already describes it
  ("The own-preferred-offset scores preserve the reported ordering in each speed stratum")
  now names it.
- `fig:sweepreal` — this one was not a missing pointer but a misplaced float. Its caption says
  "One validation frame of the sweep of Main Fig. 1b", and the only section that discusses that
  sweep is Sec. 5 (`sup:sweeps`) — but the float was parked after the last section, before
  `\end{document}`, with no owner. Moved into Sec. 5 and pointed at from the sentence that
  closes the association sweep. It now renders at the top of supplement p. 4 with its pointer
  on the same page; it was previously supplement Fig. 3 at the very end.

Renumbering risk checked before moving it: every hard-coded float number inside
`supplement.tex` refers to a **main-paper** float and is prefixed accordingly (main Tab. 1,
main Tab. 2 ×2, Main Fig. 1b, main Fig. 2 ×2), and `main.tex` cites the supplement only by
section number plus one "Supplement Table~2", which is `tab:sixseq` and unaffected because only
a figure moved. No wording depends on a supplement figure number.

### 12.3 Gate state after this round

| gate | result |
|---|---|
| number audit | **314/314**, 0 disagree; self-test 314/314 reject a corrupted value, blind none — at the tightened 0.0006 tolerance |
| main.pdf | **9 pages**, body ends p. 8 at CVPR line 654, References p. 9 (655–780), 0 undefined, 0 overfull, 25/25 fonts embedded |
| supplement.pdf | **10 pages**, 0 undefined, 0 overfull, 29/29 fonts embedded |
| floats | main **6/6** labelled and referenced; supplement **9/9** labelled and referenced (was 8 floats, 5 referenced, 1 unlabelled) |
| citations | 37 bibitems, 37 cited, 0 missing, 0 orphans |
| style gate | 4 hits, exactly the four pre-inspected ones (main.tex:366, main.tex:740, supplement.tex:34, supplement.tex:308) |
| cadence | 520 sentences, cv 0.52; top opener 9 vs flag 12; three-part lists 7.1 % vs flag 15 %; LLM vocabulary 0.00 per 1000 over 12 046 words |
| figure text | 10 figure PDFs, 0 banned terms; Nimbus Roman embedded in all four regenerated figures (item 151) |
| submission package | main.tex / supplement.tex / numbers.tex / main.pdf / supplement.pdf all `cmp`-identical to `paper/`; 10/10 figure PDFs identical; builds standalone in `/tmp/pkgbuild` to 9 and 10 pages, 0 undefined, 0 overfull, and its PDFs are **text-identical** to the shipped ones |

Both defects were consistency failures between individually-passing numbers, which is the class
of defect a reviewer finds by hand and a gate does not. The float gate is now run over both
documents, not just `main.tex`.

### 12.4 The three verification rounds this required

The standing rule is "이 조건 반드시 3번이상 검수 필요", so each claim above was checked three
times by a different route, not three times the same way.

1. **Source and render.** Macro values read out of `numbers.tex`, the ten cells recomputed from
   `experiments/e58_chunkpos/allbox.json`, the rebuilt PDFs checked for pages / undefined /
   overfull / embedded fonts, and supplement pp. 4 and 9 rasterised at 130 dpi and read as
   images to confirm the table and the moved figure land where intended.
2. **PDF against artifact, source excluded.** The five table rows parsed back out of
   `supplement.pdf` with `pdftotext -layout` and compared three ways against `allbox.json`:
   each printed cell matches the artifact to 0.0006, `full − short` of the *printed* cells
   equals the *printed* raw column at two decimals, and the printed raw column matches the
   artifact. All five rows pass all three. `main.pdf` confirmed to still carry 5.78 and 4.83.
3. **Float referencing from the PDFs alone.** Every rendered "Figure N." / "Table N." caption
   matched against a pointer in the running text with captions stripped. Main 6/6, supplement
   9/9.

Round 3 first reported main Figure 1 as unreferenced. That was the checker, not the paper: main
Fig. 1 is `fig:predictor` and is cited as `Fig.~\ref{fig:predictor}a` and `...b` at main.tex:323,
612 and 657, which render "Fig. 1a" and "Fig. 1b", and a `\b` word boundary after the digit
rejects both. Recorded because the same boundary bug would hide a genuine miss on any
sub-panelled float.

## **ACCEPT** *(sixth pass, third verification round — unchanged in grade. Table 4's arithmetic now closes as printed, and every float in both documents is labelled and pointed at. Neither defect changed a measurement; the distance to Strong Accept is still the GPU-bound breadth of Sec. 11.9.)*
