# AUDIT — Round 1 of 3 — Checklist items 1–87 (Sections A–H plus 51–87)

**Target**: `/media/hdd8/justin/my_project/CVPR20/paper/main.tex` @ 2026-09-05 11:42,
compiled `main.pdf` (9 pp, body 1–8, references 8–9), `supplement.tex` (3 pp), `numbers.tex`.
**Standard**: `docs/CHECKLIST_197.md` (2026-09-02 revision).
**External reference papers used** (per the mandatory rule): *On the Content Bias in Fréchet
Video Distance*, CVPR 2024 — the closest structural match, cited below as **[FVD]**;
*Time Blindness*, CVPR 2026 — **[TB]**; *Beyond Duality*, CVPR 2026, same testbed — **[BD]**;
*Generative Image Dynamics*, CVPR 2024 — **[GID]**. All four are described in
`docs/REFERENCE_PAPERS.md`; no internal paper was used as a standard.
**Scope note**: items 88–197 and gates G1–G12 / S1–S10 are another auditor's.
**Retraction rule applied**: E12, E18, E20 are retracted; E19's scalar-dispersion route is
abandoned per `PROTOCOL_LEDGER.md` row 2. Every number reaching the paper was traced.
**No file in `paper/` was modified.**

---

## Summary

| verdict | count |
|---|---|
| **PASS** | **46** |
| **FAIL** | **39** |
| **N/A** | **2** |
| total | 87 |

PASS: 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 17, 22, 24, 25, 26, 29, 31, 33, 35, 37, 39, 40, 42,
43, 45, 46, 47, 48, 49, 50, 51, 54, 55, 56, 63, 65, 66, 67, 68, 71, 73, 75, 76, 79, 82.

FAIL: 1, 10, 14, 15, 16, 18, 19, 20, 21, 23, 27, 28, 30, 32, 34, 36, 38, 41, 52, 53, 57, 58,
59, 60, 61, 62, 64, 69, 70, 72, 74, 77, 80, 81, 83, 84, 85, 86, 87.

N/A: 44 (zero occurrences of `i.e.`), 78 (no method, no compute trade-off to trade).

### The five most consequential FAILs

**1. Item 74 / 28 / 77 — the first contribution's whole load is carried by a cancellation
argument that is false as written, and by a standard error the paper admits is wrong.**
The anisotropic decomposition is licensed by supplement Sec. 3, L138–146: *"A scalar factor
$s>0$ multiplying the error vector of a box … multiplies $\mathbb{E}|e_{\parallel}|$ and
$\mathbb{E}|e_{\perp}|$ by the same $s$, so a regressor coupled to that factor enters both
coefficient vectors identically and cancels in the difference."* Multiplying both channels by
the same $s$ does **not** make the two regression coefficients equal. For
$|e_\parallel|\!\approx\! sA$, $|e_\perp|\!\approx\! sB$ with $s=1+\kappa\lVert v\rVert$, the
speed coefficients are $\kappa A$ and $\kappa B$, whose difference is $\kappa(A-B)$ — zero only
if $A=B$. The paper's own Table 1 shows $A\neq B$ by a factor of 4.93 (intercepts $-3.427$ vs
$-0.695$). The single most natural reviewer objection — *"a speed-coupled difficulty effect
survives your difference"* — is therefore not blocked, it is asserted away. Compounding this,
the `3.34` that the contribution rests on is a standard error the paper itself calls wrong in
three places (Table 1 caption main.tex:391, Limitations main.tex:757, supplement L152–162:
*"that expression omits the covariance term"*). Nothing else in the paper stands between the
first contribution and nothing.

**2. Item 23 / 57 — "carries no offset" is asserted for an estimate of $+11.9\pm8.9$ ms, and
that overstatement hides the paper's own strongest agreement.**
Sec. 3.4 states the measurement correctly (main.tex:354, *"No output-time offset is established
by Eq.~1 on this checkpoint"* — an unpowered null). Three other places convert it into a
positive null: abstract main.tex:50 *"carries no offset once box size enters the regression"*;
Sec. 3.6 main.tex:446 *"Its output carries no offset from the label time"*; conclusion
main.tex:774 *"places the output at the label instant"*. At $\tau=+11.9$ ms, SE $8.9$ ms, the
interval excludes neither $0$ nor $+16.6$ nor $+24.94$ ($1.47$ SE away). The two output-time
routes give $+11.9\pm8.9$ and $+16.6\pm5.0$ ms — **the same sign, agreeing within $0.5$ SE**.
The paper calls this a bracket "between no extrapolation and zeroth-order extrapolation"
(main.tex:449) when it is a corroboration. This is the needless-underclaiming half of item 53
at its most expensive.

**3. Item 21 / 60 / 57 — the title names a quantity the body defines as something else.**
The title is *"**Evidence Time** and Output Time of a Released Event Detector"*. The only
operational definition of that phrase in either document is main.tex:614: *"The \emph{evidence
time} of the box is"* Eq. 2 — the mean event time inside one DSEC-Det box, a different
quantity, on a different dataset, belonging to the **second** contribution. The predictor
quantity the title means is called, in the body, "the influence-weighted centroid" (4×), "its
input evidence" (main.tex:442), "the evidence it carries" (main.tex:45) and "$c_P$" — never
"evidence time".

**4. Item 52 / 62 / 69 / 80 / 87 / 36 — the Limitations section is a ten-item confession list,
and it is where the reader first meets a retracted experiment.**
Section 5 (main.tex:735–766) is one unbroken 340-word paragraph carrying ten separate
concessions and no sentence saying what the results *do* hold for. Its single longest sentence
(85 words, main.tex:743–750) introduces the retracted E20 gradient arm — an experiment the
paper does not otherwise mention — with its numbers, so a reader's first encounter with it is
its refutation. Two of the ten are open confessions in research-note register: *"A per-object
temporal claim on these sequences was attempted and is not supported"* (main.tex:741) and
*"Two controls named by our own record are absent"* (main.tex:752). Against the standard:
[BD] limitations = 5 lines, one concession plus future work; [FVD] = one labelled ~7-line
paragraph folded into the Discussion; [TB] = no limitations section at all, handled by running
the experiment that would have been the objection.

**5. Item 72 / 32 / 83 — one checkpoint, one dataset, and no benchmark score is ever moved.**
The predictor arm is `rvt-t` on Gen1 and nothing else. No second checkpoint (the RVT release
ships more than one; `zubic2024ssm` is cited and uses the identical
`stacked_histogram_dt=50_nbins=10` representation), no second dataset (DSEC-Det is the paper's
other testbed and [BD] re-scores RVT on it at 25.1 mAP50 / 12.9 mAP). And no AP is computed
anywhere: the paper measures an interval and converts it to $0.65$ px, then stops. [FVD] — the
paper's own nominated closest structural match, and the same *kind of object*: a metric
critique with no new method — closes exactly this loop by re-scoring published results and
showing the ordering the field reported was wrong. The submission has the finding and does not
take the last step.

---

## Item-by-item

### A. Spine / core claim (1–5)

**1. One-sentence strong message — FAIL.**
There is no one sentence. The title itself is a compound joined by a comma and *"and"*:
*"Evidence Time and Output Time of a Released Event Detector, and a Mains Signature in DSEC's
Ceiling-Exposure Sequences"* (main.tex:32–33). The abstract joins the halves with the word
*"Separately,"* (main.tex:59), which concedes there is no connecting thesis. The two arms share
neither dataset (Gen1 vs DSEC), nor object (a checkpoint vs an archive), nor estimator.
Contrast [FVD], whose every section serves one sentence ("FVD is blind to temporal quality"),
and [TB], whose whole force is one contrast (98 % vs 0 %).

**2. Problem visible in the first 3 sentences — PASS.**
main.tex:42–45: *"A detection benchmark compares a prediction with a label at one query time and
scores their difference as displacement. The prediction is computed from a window of sensor
data, and … that window ends at the label instant, so the evidence it carries is centered half
a window earlier."* The mismatch is stated by sentence 2.

**3. Core contribution on page 1 — PASS.**
Rendered p.1 carries $-24.94$ ms (col. 2, *"the influence-weighted centroid is −24.94 ms
(Sec. 3.3)"*), $+16.6$ ms at $3.34$ SE, and the opening of the flicker paragraph. Both
contributions are on p.1.

**4. Identity defined in a positive statement — PASS.**
Title and abstract name measured quantities, not absences. (The *value* argument is negative —
see item 27 — but the identity is positive.)

**5. Contribution tied to problem structure, not a method trick — PASS.**
main.tex:70–78 derives both contributions from one structural fact: *"The metric itself has no
argument in which a time could appear, so a temporal discrepancy is scored as displacement.
Neither side of the comparison is a state at an instant."* Predictor side and label side follow
from that sentence. No trick is proposed; no method is proposed at all.

### B. Reader flow (6–12)

**6. Nothing assumed known — PASS.** RVT's representation is spelled out
(main.tex:259–262, the config string and its decomposition), the Rayleigh statistic is defined
with its null (main.tex:513–516), the anisotropic difference is derived before it is used
(main.tex:399–409). A reader outside event vision can follow.

**7. Reader's question order — PASS.** Sec. 3 runs: what is the quantity (3.1) → what does the
released file say (3.2) → does the trained network agree (3.3) → where is the output (3.4) →
what is not forced by training (3.5) → what is the gap (3.6). That is the order a reader asks.

**8. New concepts appear after their necessity — PASS.** $\tau_P$ is introduced
(main.tex:244–252) only after $c_P$ has been defined and the distinction is needed. (That it is
then abandoned by name is item 60, not item 8.)

**9. Failure cause named before the method name — PASS.** main.tex:357–360 gives the cause
before the estimator that answers it: *"That outcome is the one the training objective enforces.
The detector is trained against the ground truth at the label time on a window ending at that
time, so the loss places the output at that instant."* Only then does Sec. 3.5 introduce the
anisotropic difference.

**10. One role per paragraph — FAIL.** Two paragraphs carry many roles.
(a) Sec. 5 Limitations, main.tex:735–766: one paragraph, ten concessions (see FAIL #4).
(b) main.tex:718–733: the pixel conversion, the $\sigma_c$ comparison, the speed required to
reach it, the frame-common offset on two sequences, a cross-dataset ratio, and a policy
recommendation to data producers — six roles, one paragraph, closing a section.

**11. Paragraph end poses the next question — PASS.** e.g. main.tex:92 *"A network whose
evidence sits there and whose output is scored at the label instant extrapolates over that
interval."* → next paragraph opens on the output time. main.tex:305 *"the configuration fact
of Sec. 3.2 is also a measured property of the trained network"* → Sec. 3.4 opens *"The
influence profile is a statement about the network's input."*

**12. Physical example after an abstraction — PASS.** main.tex:117–119: *"A 10 000 μs period
inside a 14 996 μs exposure displaces the event times inside a box with no motion involved."*

### C. Abstract / Introduction (13–20)

**13. Abstract opens on background or problem — PASS.** main.tex:42, quoted at item 2. Matches
[FVD]'s move (background clause + already-known symptom) and [TB]'s (concession then failure).

**14. Abstract carries 2–4 representative numbers — FAIL.** Rendered abstract carries **six**
measured numerals plus a spelled count: $-24.94$, $+16.6$, $3.34$, $100.00$, $114.58$, $0.693$,
and "six". Standard asks 2–4. [TB]'s abstract lands on two (98 %, 0 %); [BD]'s carries none.

**15. Metric regimes not mixed in the abstract — FAIL.** The abstract runs milliseconds and
standard errors (predictor, Gen1) against hertz and a Rayleigh statistic against an Exp(1) null
(illumination, DSEC), joined only by *"Separately,"* (main.tex:59). Two regimes, two datasets,
one abstract.

**16. One mechanism and one main result clear — FAIL.** The abstract carries two mechanisms
(bin occlusion; the along-minus-cross coefficient difference) and three results (the $-24.94$ ms
centroid, the $+16.6$ ms anisotropic lag with an excluded first-order account, the 100 Hz
signature).

**17. Introduction does not race to a high-level claim — PASS.** Every intro paragraph is
anchored to a file, a measurement or a number. No paragraph reaches for a field-level
statement before p.1 col. 2.

**18. 2–3 sentence bridge before the contribution list — FAIL.** There is **none**. The
itemize at main.tex:124 opens directly after main.tex:121 (*"…measured on this data."*), with no
lead-in sentence and no colon. In the rendered PDF (p.2 col. 1) the bullets begin
*"• the measured temporal influence profile of a released event detector, …"* — lowercase noun
fragments with no grammatical antecedent anywhere on the page.

**19. Bullets concise and parallel — FAIL.** Parallel in form (all four are noun phrases), but
bullet 2 (main.tex:129–133) runs **44 words** and bullet 1 **33**. [BD]'s four bullets run
~30 words each; [FVD] and [TB] have no bullets at all.

**20. Contribution bullets not overloaded with figures — FAIL.** Three of four carry measured
numbers: `24.94 ms` (b1), `+16.6 ms at 3.34 standard errors` (b2), `100.00 Hz` and `six` (b3).
The standard is explicit — [BD]: *"No numbers appear in any bullet"*; the bullets name
mechanisms and the accuracy claim is qualitative.

### D. Claims and terminology (21–27)

**21. Operational definitions for core terms — FAIL.** See FAIL #3. Every other core term is
properly defined ($k_P$, $c_P$, $\tau_P$, $e_\parallel/e_\perp$, $\bar t_i$, $Z=R^2/N$,
$m=2|C|$); the one term in the **title** is not — or rather, it is defined as a different
quantity at main.tex:614.

**22. Claimed vs not claimed is explicit — PASS.** Unusually strong. main.tex:105 *"The claim
made here is that the temporal term is separable and significant."* main.tex:354 *"No
output-time offset is established by Eq.~1 on this checkpoint."* main.tex:715 *"It is not
evidence that the objects of one frame are captured at different times."* supplement L160–162
*"The paper claims separability and significance for the speed row and no ordering among the
four rows beyond what their magnitudes show."*

**23. Claim strength matches evidence strength — FAIL.** See FAIL #2. Second instance:
*"essentially every labeled box"* (abstract main.tex:61–62 and conclusion main.tex:783) for a
measured range of 98.97–100.00 % — a rhetorical quantifier standing in front of a precise one.

**24. `every / all / only / must / cannot` not overused — PASS.** Counts in the body: `every` 9,
`all` 7, `only` 6, `must` 0, `cannot` 0. Every instance is factual scoping, and the `only`
uses *narrow* the claims (*"equals the linear weight $a_k$ only for a predictor linear in its
bins"*, main.tex:307). Full listing in Mechanical Scans.

**25. No overreaching "first" claim — PASS.** Zero occurrences of "first" as a novelty claim;
all seven hits are "first-order", "the first block", "the first row".

**26. Strong words sit beside their evidence — PASS.** `significant` ×3 and `dominant` ×2 are
the only strong words, and each is attached to a standard-error count in the same clause
(main.tex:105, 437, 454, 103, 433).

**27. Value not explained only in the negative — FAIL.** Both contributions are sold on an
absence. Abstract: *"none of the releases we read declares it"* (main.tex:59) and *"That
signature is undocumented in the release"* (main.tex:63). Conclusion repeats both
(main.tex:780, 785). The positive statements exist but are measurements, not consequences; the
sentence that would carry positive value — *"of the three terms it is the one that a single
number declared by a producer would remove"* — is a subordinate clause on p.8 (main.tex:733).

### E. Experiment design and defensibility (28–36)

**28. The most natural objection blocked first — FAIL.** See FAIL #1. The defense is available
free of charge from Table 1 and is not made: under a speed-coupled multiplicative difficulty
effect, the speed row's channel ratio would reproduce the baseline anisotropy ratio
$(-3.427)/(-0.695)=4.93$, predicting $\beta_{\parallel,\text{speed}}\approx-0.154$ s and a
difference of $\approx-0.123$ s. The measured difference is $+0.0166$ s — **opposite in sign**
and 7.4× smaller. The isotropic-difficulty account predicts the wrong sign on the one row that
carries a time. That argument is in the paper's own numbers and nowhere in its prose.

**29. Simple and strong baselines both compared — PASS.** Simple: Eq. 1's signed regression
(main.tex:322). Strong: the anisotropic difference (Sec. 3.5). Nulls on the flicker arm: an
off-frequency arm at 137 Hz on the same events, a daytime arm at the same frequency, an
analytic Exp(1) null, a matched random pixel exclusion, and random-position boxes
(Table 3, main.tex:648–679). This is the paper's strongest section.

**30. Negative results support the paper's logic — FAIL, on balance.**
Two work as defence: (a) E21's null is what licenses the anisotropic decomposition — *"The
quantity the objective does not fix is how the residual splits"* (main.tex:95–97) — a genuine
load-bearing negative; (b) the excluded first-order account (main.tex:423–428, implied lag
126.9 ms, longer than the 50 ms window) discriminates order 0 from order 1 and is a real
result. Two work as damage: (c) Sec. 3.6 **closes** on
*"The acceleration coefficient of Table 1 is more than an order of magnitude above $\tau^2/2$,
and it is significant on the cross-track channel as well, where no extrapolation puts it"*
(main.tex:452–455) — the paper hands a reviewer the weapon against its own lead contribution in
the last sentence of that section, with no counter, when the counter is the very construction
the section is built on (a term significant on both channels is isotropic difficulty, which is
what the difference operator exists to remove); (d) the retracted E20 arm enters only as an
85-word refutation in the Limitations (see FAIL #4).

**31. External reference present — PASS.** LET-3D-AP (`hung2022let`), Qin & Shen
(`qin2018temporal`), streaming perception (`li2020streaming`), Beyond Duality
(`beyondduality2026`, cited for the multiple DSEC-Det annotation versions at main.tex:485), and
four protocol papers (main.tex:224–230).

**32. Cross-dataset or cross-backbone validation — FAIL.** See FAIL #5. Zero of either.

**33. Metric connected to practical meaning — PASS.** Every temporal quantity is converted to
pixels on the split it was measured on: $0.65$ px (main.tex:444), $0.32$ px (main.tex:421),
$0.0073$–$0.0661$ px = $1.5$–$13.3$ % of $\sigma_c$ (main.tex:721–724), and the speed that
would be required to reach $\sigma_c$ (2709 px/s, *"and DSEC-Det does not contain those
speeds"*).

**34. The reader is guided on what different numbers mean — FAIL.** Table 1's `along` column
gives a label-speed coefficient of $-0.0146$ s: the along-track error magnitude **falls** with
speed, significant at 3.2 SE (E24 run.log). A lag would make it rise. No sentence of the paper
mentions the sign of either raw coefficient; the prose discusses only the difference
(main.tex:418–420). A reviewer reading the table before the prose meets a fact that appears to
contradict the claim and is given nothing.

**35. Results presented in claim order — PASS.** Abstract order = body order = Secs. 3.2 → 3.3
→ 3.4 → 3.5 → 4. (Figure order does not match: Fig. 1 supports Sec. 4 and lands on p.3 before
Sec. 3 begins, while the lead result's Fig. 2 is on p.4. Noted, not scored here.)

**36. Limitations organized as a boundary, or removed — FAIL.** See FAIL #4. Nothing in
Section 5 states a boundary in the positive form ("within X, the result holds"); all ten items
are subtractive.

### F. Related work and headings (37–40)

**37. Related-work heading is a neutral noun phrase — PASS.** `\section{Related work}`
(main.tex:157).

**38. No explanatory sentences or slogans in headings — FAIL.** One heading is a fragment with
a stray comma: `\subsection{The line, and the per-pixel test}` (main.tex:503) — and "the line"
has no antecedent at that point in the reading order; the mains line is named for the first
time *inside* the subsection (main.tex:510). Two related-work paragraph heads are full
predicative clauses terminated by periods: *"Recovering a time offset from image-plane
displacement."* (main.tex:160), *"Decomposing localization error along a privileged axis."*
(main.tex:181). Also, `\section{The interval between evidence and label}` (main.tex:232) and
`\subsection{The interval between the two measurements}` (main.tex:439) name two different
intervals with near-identical headings.

**39. Category → prior work → difference — PASS.** All four related-work paragraphs follow it,
each closing on an explicit delta: main.tex:167–168 (*"Here the offset lies between a
predictor's clock and a benchmark's label clock"*), main.tex:185–188, main.tex:201, main.tex:222.

**40. Not over-defensive about competing methods — PASS.** Deltas are stated as facts, not
defences: *"the latency it scores is compute latency, which falls as the device gets faster.
The interval measured in Sec. 3.6 is fixed by a data representation and does not"*
(main.tex:175–177).

### G. Sentence length and readability (41–45)

**41. 35-word sentences checked — FAIL.** **62 of 226** sentences (27.4 %) are ≥ 35 words:
54 in body prose of 197, 8 in captions of 29. Mean 26.4, median 25, p90 42, max 85. Full
listing with locations in Mechanical Scans. The 85-word sentence (main.tex:743–750) and the
59-word abstract sentence (main.tex:52–58) are the two that must go first.

**42. No more than one contrast per sentence — PASS.** Exactly one sentence in the body carries
two contrast markers, and it is a deliberate parallel: *"Both statements are read from the
released source **rather than** from a description of it, and the 25 ms figure is a reference
point **rather than** a property of the trained network"* (main.tex:269–271).

**43. `;`, `—`, `:` not overused — PASS.** Body prose over 8 pages: **0** em-dashes,
**10** semicolons (3 of them bullet terminators), **9** colons, all introducing a specification.
Locations in Mechanical Scans.

**44. `i.e.` used correctly — N/A.** Zero occurrences in either document.

**45. Referents of `this / it / which` are clear — PASS, strongly.** Nine sentence-initial
demonstratives, and eight of them repeat the noun: *"That signature"*, *"That quantity"*,
*"That population"*, *"That control"*, *"That alignment"*, *"That fraction"*, *"That
denominator"*, *"That outcome"*. The two bare `It is` and one `That is` each refer to the
immediately preceding subject.

### H. Parentheses, quotes, insertions (46–50)

**46. No core claim inside a parenthesis — PASS.** Machine check: of every parenthesis in the
body and captions, **zero** contain content. All are `(Sec. n)`, `(Fig. n)`, `(Table n)`
cross-references or `(a)`/`(b)`/`(c)` panel labels. The single exception is the math token
`( t_i )` in Eq. 2's lead-in.

**47. Not too many parentheses per paragraph — PASS.** Three blocks exceed two: the contribution
itemize (4 — one cross-reference per bullet), the Fig. 4 caption (3 — three panel labels),
and main.tex:442–455 (3 — three section cross-references). None is an aside.

**48. No raw double quotes — PASS.** Zero occurrences of `"` or ` `` ` in either document.

**49. Logic survives deleting the parentheses — PASS.** Follows from 46: nothing but navigation
is inside them.

**50. Colloquial / presentation register removed — PASS.** Grep of all 16 listed expressions
over the body: `because` **0**, `This is not` **0**, `We do not` **0**, `The point is` **0**,
`The reason` **0**, `cleanly` **0**, `curiosity` **0**, `sacrifice` **0**, `price` **0**,
`must` **0**, `cannot` **0**, `i.e.` **0**, `—` **0**, `"` **0**, `Why no` **0**. The three
non-zero terms (`every` 9, `all` 7, `only` 6) are all factual scoping — see item 24. Raw hits
in Mechanical Scans.

### 51–70

**51. Eight-page limit — PASS, with zero slack.** `pdfinfo main.pdf` → 9 pages; body pp. 1–8,
References heading on p. 8 col. 2, list runs to p. 9. Verified independently under CVPR's exact
textblock (`total={6.875in,8.875in}`, `columnsep=0.3125in`, from `cvpr.sty:232–234`) by
recompiling in `cvpr19-tex:cvpr2026-v1`: still 9 pages, body pp. 1–8, References moving to
p. 9, 0 overfull boxes, 0 LaTeX warnings. The conclusion's last line lands at the **bottom** of
p. 8 under CVPR geometry. **Any prose added in round 2 breaks the limit.**

**52. Weaknesses minimized or removed, strengths emphasized — FAIL.** See FAIL #4. Quantified:
Section 5 is ~340 words = ~0.6 column of an 8-page paper, spent entirely on subtraction. Two
further section-closing self-undercuts sit outside it: main.tex:452–455 (Sec. 3.6, quoted at
item 30) and main.tex:713–716 (Sec. 4.4, *"…is therefore reported here as a property of the
event stream inside the published window that this data does not resolve into a scene component
and an illumination component. It is not evidence that the objects of one frame are captured at
different times."*). A reader forms an impression at a section's last sentence; all three of
these sections end by taking something back.

**53. Generality language — FAIL, in both directions.**
*Needless underclaiming (predictor arm).* The same scope disclaimer is made **three** times:
main.tex:307–308 (*"the profile is one checkpoint at one configuration on one dataset"*),
main.tex:442 (*"Both measurements are of one checkpoint at one configuration"*), main.tex:755
(*"the influence profile is one checkpoint of one architecture on one dataset"*). Meanwhile the
one thing that **does** generalize without a further experiment is never claimed: the window
fact of Sec. 3.2 is a property of the released string
`stacked_histogram_dt=50_nbins=10` and of `preprocess_dataset.py:405`, and therefore holds for
every model trained on that released representation — including `zubic2024ssm`, which the paper
cites (main.tex:224) and which uses it. Under the checklist's own note (*"데이터셋 2~4개 검증
후 일반화 주장은 표준 관행"*), and against [BD], which generalizes from two datasets, three
disclaimers for one configuration fact is under-claiming.
*Overclaiming (flicker arm).* The six are described as a census — *"all six DSEC training
sequences pinned at the auto-exposure ceiling"* (main.tex:781–782), *"Every DSEC training
sequence whose exposure is pinned at 14 996 μs"* (Table 2 caption, main.tex:547). They are six
of the **eighteen sequences whose exposure files resolved**, and E00's README records that
*"19 of 23 probed train sequences returned the file; 4 … 404 under this naming and were not
resolved"*. Neither the four unresolved sequences nor the test split is mentioned anywhere in
the paper. "Every" is asserted over a population the paper never states it did not fully
enumerate.

**54. Unnatural coined nominalizations — PASS.** No `Directional Unsafety`-class coinage. Every
named quantity is either standard (Rayleigh statistic, modulation depth, resultant length) or
defined on the spot (temporal support kernel, effective timestamp, evidence time, anisotropic
part). One awkward heading is scored at item 38, not here.

**55. Number–percent spacing — PASS.** **26 of 26** percent signs in `main.tex` use the identical
form `\,\%` (thin space), zero exceptions, zero bare `%`, zero spelled `percent`. Rendered
output is uniformly `32.5 %`, `98.97 %`, `5–95 %`. *Note for round 2, not a failure*: the four
reference papers use the closed form (`98% accuracy`, `0% accuracy` — [TB]); if the round-3
target is CVPR house style, this is the one global substitution to make, and it is currently
free of exceptions.

**56. British/American mixing — PASS.** Full scan of 48 British forms across both documents:
the only hit is `Towards` in two **bibliography titles** (`li2020streaming`, `ercan2023evreal`,
main.tex:824, 952), which are the works' real titles and must not be changed. Body prose:
`center`, `centered`, `labeled`, `modeling`, `gray`, `analyze` throughout. Zero mixing.

**57. Contradictions between sections — FAIL.** Four:
(a) main.tex:114–115 *"between 99.0 % and 100.0 % of boxes are phase-locked"* against Table 2,
which shows `zurich_city_01_a` at **98.97 %**. The stated lower bound excludes the measured
minimum. `\sixLockedLoPct` is defined as `99.0` in `numbers.tex:454` from a value of 98.97 —
a minimum rounded upward.
(b) *"carries no offset"* (abstract, Sec. 3.6, conclusion) against *"No output-time offset is
established"* (Sec. 3.4) — see FAIL #2.
(c) "evidence time" in the title vs its definition at main.tex:614 — see FAIL #3.
(d) main.tex:731–733: *"Against these, the predictor window of Sec. 3.3 is larger by a factor of
136"*. `\termRatio` = 24.94 ms / 183.6 μs — a **Gen1** predictor quantity divided by a
**DSEC** dispersion. `docs/REBUILD_0905.md` §3 records that the old Table 4 was deleted for
exactly this reason (*"It converted a predictor term measured on Gen1 using DSEC-Det's speed
percentiles"*), and the prose form of the same cross-dataset comparison survived the deletion
with no caveat.

**58. Research-note register — FAIL.** Three hits, all in Section 5: *"A per-object temporal
claim on these sequences **was attempted** and is not supported"* (main.tex:741); *"Two controls
**named by our own record** are absent"* (main.tex:752); *"the searches recorded in the
supplement, which returned 40 papers citing [1] **from one API call of unknown coverage**"*
(main.tex:765–766). The last reports the paper's literature-search tooling in the body.

**59. Figure legibility and overlap — FAIL.** Rendered at 190 dpi from `figs/*.pdf`:
- **Fig. 4(a)** (`fig5_qualitative.pdf`): the six box index labels overprint. Boxes 1, 2, 3 and
  4 are small and adjacent, and their numerals render as an unreadable run `12 3 1` with `5`
  and `6` overlapping the box edges. `docs/REBUILD_0905.md` §2 claims this was fixed
  (*"Boxes now carry an index"*) — the indices were added, the collision was not resolved.
- **Fig. 2** (`fig_predictor.pdf`): the caption reads *"(a) Occlusion influence …(b) The
  anisotropic part…"* but **neither panel is labelled** in the figure. The reader must infer
  top = (a), bottom = (b).
- **Fig. 4** mixes registers with the other three: it is the only figure using colour (a viridis
  colourbar in (a), a red dashed "frame mean" in (b)); Figs. 1, 2, 3 are monochrome. In
  greyscale print, (a)'s colourbar carries no information.
- Figs. 1 and 3 are clean; the four-tick overprint recorded in the previous audits of Fig. 3 is
  genuinely fixed.
- *(Out of this range, for the 88–197 auditor / item 151:* `fig5_qualitative.pdf` embeds
  **DejaVuSerif**; the other three embed NimbusRoman/STIXGeneral.*)*

**60. Internal terminology unified — FAIL.** Four drifts:
(a) "evidence time" for two different quantities — FAIL #3.
(b) One instant, five names: `label instant` (7 rendered), `label time` (10), `query time` (4),
`label clock` (2), `nominal instant` (1, main.tex:239), plus the periphrasis *"the instant the
label asserts"* (main.tex:268).
(c) `\emph{effective timestamp}` is formally introduced at main.tex:244 and then never used by
name again: the body switches to `$\tau_P$` (5×) and then to "the output time" (subsection
heading, main.tex:310). One quantity, three names.
(d) Two near-identical headings for different intervals — see item 38.
*(Hygiene, unscored: `\eff` is defined in both `main.tex:22` and `supplement.tex:19` and used
zero times; 90 of `numbers.tex`'s 326 macros are unused.)*

**61. Semicolon without sentence separation — FAIL.** One: main.tex:520 *"That fraction is
quoted of live pixels; of the sensor it is 4.67 %."* The second clause is elliptical, not
independent. The other nine prose semicolons all join independent clauses correctly.

**62. Strengths emphasized, weaknesses minimized or removed — FAIL.** Same evidence as item 52;
the checklist lists this twice and it fails twice.

**63. Academic register maintained, no promotional or presentation tone — PASS.** Grep of 20
promotional markers (`we show`, `we demonstrate`, `we believe`, `novel`, `state-of-the-art`,
`outperform`, `remarkable`, `surprisingly`, `clearly`, `obviously`, `indeed`, …): **one** hit,
*"an object that is **simply** harder to localize"* (main.tex:96–97), which is descriptive.

**64. No meta sentences — FAIL.** One hit, and it is on the checklist's own list:
*"**We therefore** fit $|e_\parallel|$ and $|e_\perp|$ with the same four regressors…"*
(main.tex:411). `Finding`, `Rationale`, `Mechanism`, `Three points follow`, `A natural
objection`, `This is what makes`, `Note that`, `In this paper`, `Importantly`, `Notably`,
`In other words`, `To summarize`: all zero.

**65. No presentation-style prose — PASS.** Covered by the item 63 scan.

**66. No slide / rebuttal / oral-explanation sentences — PASS.** No rhetorical questions, no
`as we will see`, no `recall that`, no `let us`. Zero.

**67. American English verified — PASS.** Same evidence as item 56.

**68. American academic tone, paragraph boundaries — PASS.** Paragraph openings are topic
sentences throughout; no paragraph opens on a pronoun or a citation.

**69. No open confession — FAIL.** Three, all in Section 5: main.tex:741 (*"was attempted and is
not supported"*), main.tex:752 (*"Two controls named by our own record are absent"*),
main.tex:765–766 (*"one API call of unknown coverage"*). Each states not a boundary on the
result but a fact about what the authors did and failed to do.

**70. Reads non-interventionally, like a top-tier paper body — FAIL.** The body prose does
read this way — restrained, numeric, unrhetorical — for Secs. 1–4.3. It breaks in exactly three
places, and all three are section closings: main.tex:452–455, main.tex:713–716, and the whole of
Section 5. Against [FVD], which folds its limitations into a Discussion and whose every section
ends on a result, and [TB], which has no limitations section at all.

### 71–87

**71. Falsifiable Thesis Test — PASS.** Each claim names an artifact and a procedure that would
refute it: re-run the bin occlusion on the released `rvt-t` checkpoint; refit the two channels
on the 4332 matches; re-run the Rayleigh test on the six sequences. Nothing rests on an
unfalsifiable framing.

**72. Final-Objective Alignment Test — FAIL.** See FAIL #5. The stated objective is that a
benchmark scores a temporal discrepancy as displacement (main.tex:72–74). No benchmark score is
ever computed, so the discrepancy is never shown to move one.

**73. Nearest-Alternative Delta Test — PASS.** Both nearest alternatives are named and
differenced at the operation level: Qin & Shen (main.tex:160–168, *"Temporal calibration removes
the offset between two sensor clocks by pooling over features … Here the offset lies between a
predictor's clock and a benchmark's label clock"*) and LET-3D-AP (main.tex:181–188, *"…with the
object's own direction of travel in place of the sensor's line of sight, and takes the difference
between the two channels as the estimand rather than defining a tolerant score"*).

**74. Alternative-Explanation Kill Test — FAIL.** See FAIL #1. Note the asymmetry: on the
flicker arm the kill test is executed to an exemplary standard (off-frequency arm, daytime arm,
matched random pixel exclusion, random-position boxes, modulation strata, and the honest
admission that the 137 Hz sham arm also rises). On the predictor arm it is not executed at all.

**75. Claim–Evidence Ledger — PASS.** `numbers.tex` enforces one: 326 macros, each carrying a
comment naming the experiment directory that produced it. Independent check: **zero** bare
numerals in body prose outside proper names (`Argoverse 2`, `1 Mpx`, `DSEC-3DOD`) and the
literal config string. **Zero** `[unmeasured]` placeholders render in either PDF. Spot-checks
against source: `\rvtCentroidMeas` = `-24.94` ↔ `e17_bin_influence/result.json:centroid_ms`
= −24.94375; `\aniSpeed` = `+0.0166`, `\aniSpeedSigmas` = `3.34`, `\aniInterSigmas` = `16.94`,
`\aniSizeSigmas` = `26.37` ↔ `e24_order/run.log`; `\sixZmedian` = `114.58` = median of
{117.6, 99.1, 68.4, 310.9, 251.5, 111.6} ✓; `\sixZctrl` = `4.01` = median of
{3.15, 4.69, 2.75, 25.85, 7.82, 3.33} ✓; `\termRatio` = 136 = 24.94 ms / 183.6 μs ✓.
**Retraction check: clean.** All 16 `\grad*` macros (E20) are commented out under a retraction
note (`numbers.tex`, the block above `\figFiveCands`); E12's four window widths and E18's
`PHASESUB` value are commented out; zero occurrences of `grad`, `cosine` or `sec:gradient` in
either document. Table 3's values (206.6 / 93.0 / 183.6; 205.1 / 97.1 / 180.6; 206.3 / 94.8 /
182.9; 338.2 / 134.5 / 306.3) match E09 and E11's **corrected** exact-window re-runs, not their
superseded first runs. **No claim in the paper rests on a retracted result.**

**76. Validity Envelope Test — PASS.** The envelope is stated on both arms, and on the flicker
arm it is stated with unusual precision: the archive is named by filename, byte count and
retrieval date (main.tex:485–487), the label-version ambiguity is acknowledged via [BD]
(main.tex:485), and the two denominators for "locked" are kept separate (main.tex:519–520).

**77. Claim Fragility Test — FAIL.** See FAIL #1. The whole first contribution reduces to one
number, `3.34`, and that number is computed from
$(\mathrm{se}_\parallel^2+\mathrm{se}_\perp^2)^{1/2}$ on two fits over the **same** 4332 boxes
sharing three of four regressors. The paper states the defect three times and never removes it,
although a paired bootstrap over boxes costs seconds. If the two channels are negatively
correlated — which the opposite-signed intercept and speed anisotropies make plausible — the
quoted SE **understates** the true one and `3.34` falls.

**78. Quality–Cost Pareto Test — N/A.** The paper proposes no method and no compute trade-off.

**79. SOTA-Independent Value Test — PASS.** The paper's strongest item. It computes no
detection score, claims no improvement, and its value would be unchanged if every detector in
the field improved tomorrow. This is precisely [FVD]'s and [TB]'s position.

**80. Bounded Limitation Test — FAIL.** See FAIL #4 and item 36. Not one of the ten Limitations
items is phrased as a bound of the form "within X the result holds"; all ten are of the form
"Y is absent / Y failed / Y is only".

**81. Paradigm-Delta Test — FAIL.** The delta exists — a release should declare the interval
between its evidence and its output, and a dataset should declare a mains signature — but it
appears once, as a subordinate clause on p. 8: *"…and of the three terms it is the one that a
single number declared by a producer would remove"* (main.tex:732–733). It is absent from the
abstract, the introduction, the contribution list and the conclusion.

**82. Method Compression Test — PASS.** Both estimators compress to one line each: the
influence-weighted centroid $\sum_k a_k c_k/\sum_k a_k$ over occlusion sensitivities, and
$\beta_\parallel - \beta_\perp$ from two OLS fits on a common design matrix. Nothing decorative.

**83. Hard-Case-First Evidence — FAIL.** The flicker arm passes this (it moves from one sequence
to all six, and Table 2's weakest sequence, `zurich_city_02_a` at $Z=68.4$, is shown rather than
hidden). The predictor arm never reaches its hard case: the hardest test available — a second
checkpoint, or the same measurement on the DSEC-Det-trained RVT that [BD] re-scores — is not
run, and the acceleration term, which is the arm's hard case, is conceded rather than tested
(`PROTOCOL_LEDGER.md` entry 5: *"No pass of the protocol has been run against this."*).

**84. Cross-Task Reuse Test — FAIL.** The anisotropic difference operator is generic — it needs
only a detector, tracked labels and a direction of travel — and would apply to any tracking
benchmark, to 3D detection along the LET-3D-AP axis, and to any of the four other released event
detectors named in Sec. 3.1. The paper never says so and never applies it twice.

**85. Reviewer Memory Test — FAIL.** What a reviewer will carry away is the flicker result:
"all six DSEC ceiling sequences are phase-locked to 100 Hz mains, $Z=114.58$ against a null of
$0.693$" — vivid, six-of-six, a 165× separation from its null. What they will not carry away is
the lead contribution: $-24.94$ vs $+16.6$ ms at $3.34$ SE, next to $16.94$ and $26.37$ SE on
rows that carry no time, in a paper whose own Fig. 2(b) shows the temporal bar as the smallest
of four. The paper leads with the result that is harder to remember and titles itself after it.

**86. Field-Consequence Test — FAIL.** Same evidence as item 81, compounded by item 72: with no
benchmark score moved, the consequence is a recommendation without a demonstrated cost. [FVD]
answers this by re-scoring published long-video results and showing the field's ordering was
wrong; the submission's equivalent move — showing an AP ordering that changes when the interval
is declared — is available and not made.

**87. No defensive phrasing; emphasize strengths — FAIL.** Same evidence as 52, 62, 69, 70.
Three of six section closings retract. Section 5 is 340 subtractive words. The paper's genuinely
strong results — a 165× separation from an analytic null reproduced in six of six sequences, a
configuration fact read from released source, two independent estimators agreeing on the output
time — are nowhere assembled into a statement of what the paper establishes.

---

## Mechanical scans

Reproduce with `scratchpad/prose2.py` (macro-expanding LaTeX prose extractor; expands all 326
`numbers.tex` macros, strips floats to their captions, protects `Sec./Fig./Eq./al.` from the
sentence splitter).

### Item 41 — sentence-length distribution, `main.tex` body + captions

```
n = 226    mean = 26.4    median = 25    p90 = 42    max = 85
  0-  4 :   1
  5-  9 :  19
 10- 14 :  42
 15- 19 :  22
 20- 24 :  26
 25- 29 :  23
 30- 34 :  31
 35- 39 :  26   <-- 62 sentences (27.4 %) at or above 35 words
 40- 44 :  20
 45- 49 :   5
 50- 54 :   5
 55- 59 :   3
 60- 64 :   1
 80- 84 :   1
body ≥35: 54 of 197      captions ≥35: 8 of 29
```
(The 124-word entry in the raw dump is the four-bullet `itemize` block read as one unit; the
bullets individually are 33 / 44 / 22 / 24 words and are scored at items 19–20.)

Every sentence ≥ 35 words, longest first (`words | region | main.tex line | section`). The
line number is the source line on which the sentence begins; all were verified individually
against `main.tex` at the audited revision.

```
 85 | body    | L743 | Limitations   A spatial statistic chosen for its immunity to a spatially uniform source, the gradient of evidence time inside a box aligned with the object's velocity, does not survive its own background control: against an equal-area annulus of each box's own surroundings, which cancels a cause common to both, the background aligns at least as well as the object in four of the six sequences, and eroding the box to its object-dominated core drives the paired difference negative in five, to -0.178 at 6.2 standard errors.
 61 | body    | L781 | Conclusion    Separately, all six DSEC training sequences pinned at the auto-exposure ceiling carry a 100.00 Hz mains modulation on essentially every labeled box, at a median per-box Rayleigh statistic of 114.58 against an analytic null of 0.693, which the release does not state and which bounds what a per-object temporal statistic measured inside one of those exposure windows can be attributed to.
 59 | abstract| L52  | Abstract      Fitting the along-track and the cross-track error magnitudes with the same regressors and taking their difference removes any effect that raises both channels equally, and the term proportional to label speed then implies a lag of +16.6 ms at 3.34 standard errors, while the term proportional to acceleration implies a lag longer than the window itself and is excluded.
 57 | body    | L700 | Sec. 4.4      The same procedure at 137 Hz, where the test returns its null, also rises, from 150.3 to 187.6 us, a factor of 1.25, so part of the trend belongs to stratifying on any amplitude statistic: ...
 56 | body    | L480 | Sec. 4.1      Over 361 628 triples of consecutive labels on a track the median distance from the middle box center to the linear interpolant of its neighbors is 0.707 px and 7.1 % fall below a hundredth of a pixel, ...
 53 | body    | L224 | Related work  Protocol work supplies the standards these measurements are held to: re-measurement under a repaired protocol can reverse a field's conclusion [26], a reported score is an estimate with a variance [27], ...
 51 | body    | L774 | Conclusion    The signed along-track residual of its detections places the output at the label instant, which its training objective enforces, while the difference between the along-track and cross-track error magnitudes, ...
 51 | body    | L107 | Introduction  DSEC publishes each frame's own exposure interval, and across the eighteen training sequences whose exposure files resolve, the width varies by a factor of 127 ...
 50 | body    | L81  | Introduction  The event branch of the detector examined here [23] consumes a window of 50 ms divided into ten bins, and the preprocessing script of its own repository ...
 50 | body    | L505 | Sec. 4.2      The power spectrum of the global event rate, computed with the same code and window for a ceiling sequence and a daytime one, has its strongest line between 90 and 110 Hz at 100.00 Hz ...
 49 | body    | L727 | Sec. 4.4      The frame-common part is separately small: over 1811 frames of the ceiling sequence the evidence of all events is centered -16.8 us from the mid-exposure instant ...
 48 | body    | L770 | Conclusion    The evidence a released event detector is given is centered 24.94 ms before the instant its output is scored at, ...
 47 | body    | L493 | Sec. 4.1      On a uniform grid the variance of the k-th difference of a track's box center is C(2k,k) sigma_c^2 plus a motion term whose order rises with k, ...
 46 | body    | L682 | Sec. 4.4      Boxes of the same shapes placed at random positions in the same frames give an excess of 306.3 us, larger than the annotated boxes', ...
 46 | body    | L520 | Sec. 4.2      The estimator returns its null on the same events at 137 Hz, where the median Z is 0.581 with a p<1e-3 rate of 0.04 %, and again on 17 800 daytime pixels ...
 44 | caption | L667 | Table 3       In the lower block a frame enters a stratum when at least 3 of its boxes fall in it, so its frame counts are not a partition of the first row's, ...
 44 | body    | L411 | Sec. 3.5      We therefore fit |e_par| and |e_perp| with the same four regressors, a constant, the label speed, the box side and the object's acceleration, over 4332 matches ...
 44 | body    | L357 | Sec. 3.4      The detector is trained against the ground truth at the label time on a window ending at that time, so the loss places the output at that instant, ...
 44 | body    | L189 | Related work  TIDE [7,8] and DETAD [9] bucket detection error atemporally, so a temporal offset falls inside their localization bucket, HOTA [10] takes the label clock as exact, ...
 43 | body    | L685 | Sec. 4.4      Removing the 14 334 pixels that reach p<1e-3 in the per-pixel test changes the excess from 183.6 to 180.6 us, ...
 42 | caption | L147 | Fig. 1        32.5 % of frames sit at the auto-exposure ceiling of 14 996 us, and zero frames fall between the largest non-ceiling width of 4207 us and that ceiling, ...
 42 | body    | L422 | Sec. 3.5      The acceleration coefficients differ by +0.0080 s^2, which a first-order extrapolation would read as a lag of 126.9 ms, longer than the 50 ms window ...
 42 | body    | L293 | Sec. 3.3      We take 480 samples of the released Gen1 validation split with the released rvt-t checkpoint, warm the recurrent state for eight steps, ...
 42 | body    | L218 | Related work  REFID [20] argues that accumulating events from a single frame timestamp loses information, deblurring work names auto-exposure as why the width is unknown [21], ...
 42 | body    | L172 | Related work  Inside the citation graph of LET-3D-AP [1], a latency-aware average precision scores 3D detection at the instant a prediction becomes available on a named device, ...
 41 | caption | L385 | Table 1       The along-track and cross-track error magnitudes of the released rvt-t checkpoint, fitted with the same four regressors over 4332 matched boxes ...
 41 | body    | L689 | Sec. 4.4      That control is bounded by what it excludes: the median Z over all live pixels of this sequence is 2.935 against a null of 0.693, ...
 41 | body    | L466 | Sec. 4.1      The auto-exposure ceiling of 14 996 us holds 32.5 % of frames, in six of the eighteen sequences, and the distribution is not continuous over that range: ...
 41 | body    | L471 | Sec. 4.1      The left and right exposures open at the same microsecond in 100.00 % of the 7080 frames checked and differ only in when they close, ...
 41 | body    | L114 | Introduction  Per labeled box, between 99.0 % and 100.0 % of boxes are phase-locked to it at p<1e-3, the median per-box Rayleigh statistic is 114.58 ...
 40 | body    | L708 | Sec. 4.4      Over the same boxes, m at 100.00 Hz has a tenth percentile of 0.355, a median of 0.467 and a ninetieth percentile of 0.609, ...
 40 | body    | L638 | Sec. 4.4      The within-frame standard deviation of t-bar_i is 206.6 us against an analytic null of 93.0 us, the excess is 183.6 us, ...
 40 | body    | L759 | Limitations   The acceleration regressor is a difference of differences of label centers over a 50 ms base, so it carries the label noise of Sec. 4.1 amplified, ...
 40 | body    | L98  | Introduction  Fitting both channels with the same regressors and differencing them isolates the second, and the term proportional to label speed gives an implied lag of +16.6 ms ...
 40 | body    | L337 | Sec. 3.4      The released checkpoint is run over 200 sequences of the Gen1 validation split with its recurrent state carried across steps, ...
 40 | body    | L302 | Sec. 3.3      For this configuration the centroid of the input is therefore the uniform-weight centroid of the window to within a small fraction of a bin, ...
 39 | caption | L390 | Table 1       The difference column is the along-track coefficient minus the cross-track one, in which an effect raising both channels equally cancels; ...
 39 | caption | L280 | Fig. 2        (b) The anisotropic part of the same checkpoint's localization residual over 4332 matched boxes, each of the four regression terms ...
 39 | body    | L513 | Sec. 4.2      Per pixel, the Rayleigh statistic Z=R^2/N, for R the resultant length of the event phases at the test frequency, is Exp(1) under uniform phase, ...
 39 | abstract| L43  | Abstract      The prediction is computed from a window of sensor data, and in the released configuration of the event detector examined here that window ends at the label instant, ...
 39 | abstract| L59  | Abstract      Separately, the six DSEC training sequences whose exposure is pinned at the auto-exposure ceiling carry a 100.00 Hz mains modulation on essentially every labeled box, ...
 38 | body    | L778 | Conclusion    The interval between the two is a zeroth-order extrapolation that is measurable from released artifacts and that none of the releases we read declares, ...
 38 | body    | L763 | Limitations   Statements about what benchmarks record are scoped to those whose documentation we read, and statements about prior art to the searches recorded in the supplement, ...
 38 | body    | L185 | Related work  Sec. 3.5 performs the same decomposition with the object's own direction of travel in place of the sensor's line of sight, ...
 38 | body    | L182 | Related work  LET-3D-AP [1] decomposes camera-only 3D localization error along the line of sight and defines an average precision tolerant of the longitudinal part, ...
 38 | body    | L168 | Related work  Streaming perception [6] folds wall-clock compute latency into average precision and re-anchors any detector from box coordinates alone; ...
 38 | body    | L117 | Introduction  A 10 000 us period inside a 14 996 us exposure displaces the event times inside a box with no motion involved, ...
 37 | body    | L564 | Sec. 4.3      The median per-box Rayleigh statistic at 100.00 Hz runs from 68.4 to 310.9 with a median over sequences of 114.58, ...
 37 | body    | L445 | Sec. 3.6      Its output carries no offset from the label time under Eq. 1 (Sec. 3.4), which the training objective forces, ...
 37 | body    | L361 | Sec. 3.4      The measurement does control Eq. 1 itself: a cross-track slope at 0.1 standard errors beside a size term at 3.0 ...
 37 | body    | L349 | Sec. 3.4      With the size term present, tau=+11.9 ms with a standard error of 8.9 ms, which is 1.3 standard errors from zero, ...
 36 | caption | L673 | Table 3       Rows two and three remove the 14 334 pixels phase-locked at 100.00 Hz and a random subset of exactly that size; ...
 36 | caption | L547 | Table 2       Every DSEC training sequence whose exposure is pinned at 14 996 us, measured per labeled box over the events inside that box ...
 36 | body    | L737 | Limitations   The evidence-time measurement of Sec. 4.4 is one ceiling sequence against 20 usable frames at the narrow exposure, ...
 36 | body    | L403 | Sec. 3.5      A zeroth-order extrapolation over a lag tau, which reports the position the object last occupied, displaces the prediction by tau|v| ...
 36 | body    | L363 | Sec. 3.4      The released checkpoint loads into a model built from the repository's own configuration files with 0 missing and 0 unexpected keys at 4.41 M parameters, ...
 36 | body    | L307 | Sec. 3.3      Occlusion measures the sensitivity of the output to a bin, which equals the linear weight a_k only for a predictor linear in its bins, ...
 35 | caption | L276 | Fig. 2        (a) Occlusion influence of each of the ten bins of the released rvt-t input window, over 480 real Gen1 validation samples ...
 35 | body    | L642 | Sec. 4.4      On interlaken_00_c, where the exposure is 1556 us and the 200-event floor leaves 20 usable frames, ...
 35 | body    | L400 | Sec. 3.5      An effect that raises the magnitude of the localization error without a preferred direction, such as an object being harder to localize, ...
 35 | body    | L331 | Sec. 3.4      That denominator is finite differenced from labels, so the regression is an errors-in-variables problem; ...
 35 | body    | L261 | Sec. 3.2      Line 405 of scripts/genx/preprocess_dataset.py constructs the array ev_repr_timestamps_us_end by counting backwards from a label timestamp ...
```

Supplement, for reference (not scored in this range): n = 81, mean 23.3, median 21, max 51;
five sentences ≥ 45 words, longest at `supplement.tex:179`.

### Items 46–49 — parentheses per paragraph, classified

Every parenthesis in the body and captions, with content-bearing asides separated from
cross-references and panel labels:

```
block                                          total  ref/panel  content
[body]    L80-92    Introduction                   2       2         0
[body]    L94-105   Introduction                   1       1         0
[body]    L107-121  Introduction                   2       2         0
[body]    L123-139  Introduction (contributions)   4       4         0   <- 4 > 2
[caption] L273-287  Fig. 2                         2       2         0
[body]    L298-308  Sec. 3.3                       1       1         0
[body]    L411-416  Sec. 3.5                       1       1         0
[body]    L442-455  Sec. 3.6                       3       3         0   <- 3 > 2
[body]    L463-474  Sec. 4.1                       1       1         0
[body]    L513-528  Sec. 4.2                       1       1         0
[body]    L560-573  Sec. 4.3                       1       1         0
[caption] L592-608  Fig. 4                         3       3         0   <- 3 > 2
[body]    L626-630  Sec. 4.4                       1       0         1   (math token " t_i ")
[body]    L632-646  Sec. 4.4                       1       1         0
                                            TOTAL 24      23         1
```
Three blocks exceed two parentheses; **none** contains an aside. The four in the contribution
list are one cross-reference per bullet; the three in the Fig. 4 caption are the panel labels
(a)(b)(c). Items 46, 47, 49 pass on this evidence.

### Item 48 — raw double quotes

`grep -n '"\|``' main.tex supplement.tex` (body range) → **0 hits** in both documents.

### Item 50 — colloquial / presentation-register expressions

Body range `main.tex:37–790`, all sixteen listed expressions:

```
because        0        cleanly        0        every        9   (factual)
This is not    0        curiosity      0        all          7   (factual)
We do not      0        sacrifice      0        only         6   (restrictive)
The point is   0        price          0        must         0
The reason     0        i.e.           0        cannot       0
Why no         0        "  (raw)       0        --- (em dash) 0
```
The three non-zero terms in full:
```
every  L62(abstract) essentially every labeled box | L316 for every matched prediction |
       L477 every label sits on the frame clock | L547(cap) Every DSEC training sequence |
       L562 every sequence that reaches the ceiling | L595(cap) Every event inside one window |
       L703 a larger |C| at every frequency | L740 subsamples every fourth event |
       L783 essentially every labeled box
all    L135 measured in all six | L530(head) All six ceiling sequences | L563 reports all six |
       L655(table) all pixels | L690 over all live pixels | L728 the evidence of all events |
       L781 all six DSEC training sequences
only   L98 raises only the first | L182 camera-only 3D localization | L307 only for a predictor
       linear in its bins | L399 not the only estimator | L473 differ only in when they close |
       L756 only for a predictor linear in its bins
```

### Item 43 — `;`, `—`, `:` in body prose

```
em dash (---)  : 0
semicolons     : 13   L128, L133, L136 (bullet terminators) | L170 | L175 | L332 |
                      L390 (Table 1 caption) | L393 (Table 1 caption) | L485 | L520 |
                      L599 (Fig. 4 caption) | L673 (Table 3 caption)   [+1 inside math, L617;
                      +1 inside a \ref group, L641]
colons         :  9   L48 (abstract) | L89 | L202 | L225 | L361 | L469 | L703 | L727 | L746
```
Ten of the thirteen semicolons are in body prose or captions; three are `itemize` terminators.
Item 61's single defective semicolon is `main.tex:520`.

### Items 55 / 56 / 60 / 67 — spacing, spelling, terminology

**Percent (item 55).** 26 of 26 occurrences use `\,\%`. Zero bare `%`, zero `percent`, zero
exceptions. Rendered forms verified in `main.pdf` pp. 1–8:
`32.5 %  99.0 %  100.0 %  100.00 %  98.97 %  99.35 %  99.69 %  99.70 %  99.84 %  90.1 %
 81.5 %  24.07 %  13.3 %  5–95 %  4.67 %  1.5 %  1.2 %  0.1 %  0.08 %  0.04 %  0.00 %  7.1 %`

**British spellings (items 56 / 67).** 48 forms scanned across both documents
(`colour behaviour labelled modelling centre centred analyse normalise organise recognise
utilise summarise generalise visualise emphasise minimise characterise practise defence
licence programme travelling cancelled fibre metre grey towards whilst amongst learnt
neighbour …`). **One hit**: `Towards` at `main.tex:824` and `main.tex:952`, both inside
`\bibitem` titles (`Towards streaming perception`; `EVREAL: Towards a comprehensive
benchmark…`). Correct as published titles. Rendered PDF: 2 occurrences, both in References.

**Terminology drift (item 60).** Rendered-PDF counts, body pp. 1–8:
```
label instant  7    evidence time  8    mains       9
label time    10    output time    2    flicker     2
query time     4    effective timestamp 1   ceiling 22
label clock    2    nominal instant     1
```
`effective timestamp` is introduced in italics at `main.tex:244` and never reused; the same
quantity is then `$\tau_P$` (main.tex:247, 248, 249, 251, 292) and then "the output time"
(heading, main.tex:310). `evidence time` is formally defined at `main.tex:614` as the DSEC
per-box quantity while the title uses it for the Gen1 predictor quantity. Dead macro: `\eff`
defined at `main.tex:22` and `supplement.tex:19`, zero uses. 90 of 326 `numbers.tex` macros are
unused (full list available; all are commented-provenance leftovers, none renders).

### Item 51 — page limit, verified on the compiled PDF and re-verified under CVPR geometry

```
pdfinfo main.pdf        -> Pages: 9   (612 x 792 pts, letter)
pdfinfo supplement.pdf  -> Pages: 3
submitted geometry: body pp.1-8; "References" heading p.8 col.2; list pp.8-9
CVPR textblock (total={6.875in,8.875in}, columnsep=0.3125in, from cvpr.sty:232-234),
  recompiled twice in cvpr19-tex:cvpr2026-v1:
    -> Pages: 9 ;  body pp.1-8 (Conclusion's last line at the FOOT of p.8) ;
       "References" heading moves to p.9 ; Overfull boxes 0 ; LaTeX Warnings 0
```
The 8-page body limit is met under both. Slack: none.

### Item 30 / retraction check — every experiment README status

```
e00 e01 e02 e03 e04 e05 e06 e07 e08 e09* e10 e11* e13 e14 e16 e19 e23**   READMEs present
e12  RETRACTED 2026-09-03  (integer-period identity is false)  -> 0 macros reach the paper
e18  RETRACTED 2026-09-03  (repeats E12's identity)            -> 0 macros reach the paper
e20  RETRACTED 2026-09-05  (alignment is ego-motion)           -> 16 \grad* macros commented out;
                                                                  0 occurrences of grad/cosine/
                                                                  sec:gradient in either document
e15 e17 e21 e24 e25 e26  NO README (result.json + run.log only)
* e09 and e11 carry CORRECTION banners, not retractions; the paper uses the corrected values.
** e23 carries a "read the cross-track row first" banner; the paper reports both rows.
```
No claim in the paper rests on a retracted result. **Provenance gap for round 2**: E17, E21,
E24, E25, E26 and E15 — which produce the numbers behind *both* contributions — have no README,
only a `result.json` and a `run.log`; and `e24_order/result.json` stores only
`{n, aniso_accel, aniso_speed, median_speed}`, so the four SE values in Table 1 (16.94, 3.34,
26.37, 3.72) and the eight along/cross coefficients exist **only as stdout text** in
`e24_order/run.log`. Every one of them was verified against that log for this audit and they
match, but they are not in a machine-readable artifact.

---

## Ordered fix list

Most consequential first. Locations are `main.tex` line numbers at the audited revision.
**Page budget: zero slack under CVPR geometry (item 51). Every addition below is paired with a
deletion of at least equal length.**

---

**F1 — Block the isotropic-difficulty objection with the paper's own Table 1.**
*(items 74, 28, 77, 30, 34; the paper's largest single vulnerability)*

Two edits.

(a) `supplement.tex:137–150`, replace the false cancellation sentence
> *"A scalar factor $s>0$ multiplying the error vector of a box, which is what an object being
> harder or easier to localize produces, multiplies $\mathbb{E}|e_{\parallel}|$ and
> $\mathbb{E}|e_{\perp}|$ by the same $s$, so a regressor coupled to that factor enters both
> coefficient vectors identically and cancels in the difference."*

with the correct statement and the test it implies:

> A scalar factor $s>0$ multiplying the error vector of a box multiplies
> $\mathbb{E}|e_{\parallel}|$ and $\mathbb{E}|e_{\perp}|$ by the same $s$. It does not follow
> that a regressor coupled to $s$ enters both coefficient vectors identically: for
> $\mathbb{E}|e_{\parallel}|=sA$ and $\mathbb{E}|e_{\perp}|=sB$ with $s=1+\kappa r$ in a
> regressor $r$, the two coefficients are $\kappa A$ and $\kappa B$ and their difference is
> $\kappa(A-B)$, which vanishes only for $A=B$. The difference therefore cancels an isotropic
> effect exactly when the two channels have equal baseline magnitude, and otherwise leaves a
> residue proportional to the baseline anisotropy. That residue is testable, because the
> baseline anisotropy is a fitted quantity: a single scale factor coupled to any regressor
> reproduces the same channel ratio on every row.

(b) `main.tex:430–437`, append to the paragraph beginning *"The two remaining differences are
larger."* (this is the paragraph that currently concedes and stops):

> The four rows do not share one channel ratio. The along-track coefficient is
> \aniInterRatio{} times the cross-track one on the intercept, \aniSizeRatio{} on the box
> side and \aniAccelRatio{} on the acceleration, but \aniSpeedRatio{} on the label speed. A
> single scale factor coupled to speed would carry the baseline ratio onto the speed row and
> predict a difference of \aniSpeedPredIso\,s there; the measured difference is \aniSpeed\,s,
> of the opposite sign. The anisotropy on the one row that carries a time is not a scaled copy
> of the geometric anisotropy on the rows that do not.

New macros for `numbers.tex`, all computable from `e24_order/run.log` with no re-run:
`\aniInterRatio` = 4.93 (= −3.427/−0.695), `\aniSizeRatio` = 2.67, `\aniAccelRatio` = 1.69,
`\aniSpeedRatio` = 0.47, `\aniSpeedPredIso` = −0.123 (= 4.93 × −0.0312 − (−0.0312)).
*Verify each against the log before writing; this audit computed them from the printed
coefficients, not from a re-run.*

Space: F1(b) is ~85 words. Pay for it with F4, which removes ~110.

---

**F2 — Replace the admitted-wrong standard error with a measured one.**
*(items 77, 74, 23; removes the paper's single point of failure)*

Re-run `src/e24_order.py` with a paired bootstrap: resample the 4332 matched boxes with
replacement (B = 2000), refit both channels on each resample, and take the standard deviation
of $\beta_\parallel-\beta_\perp$ per row. This is the exact SE of the difference including the
covariance, costs seconds, and needs no new data.

Then delete all three disclaimers and replace them with the number:
- `main.tex:390–392` (Table 1 caption): *"…in units of its own standard error, formed as if the
  two fits were independent."* → *"…in units of its own standard error, taken from a paired
  bootstrap over the \aniMatches{} matched boxes, which carries the covariance of the two fits."*
- `main.tex:757–759` (Limitations): delete the sentence *"The standard error of each difference
  in Table~\ref{tab:aniso} is formed as if the two channel fits were independent, when both are
  computed on the same matched boxes."* entirely (−27 words, contributes to F4's budget).
- `supplement.tex:152–162` (*The standard error*): replace the four-sentence hedge with the
  bootstrap definition and the resulting per-row values.

If the bootstrap SE moves `3.34` materially, that is the round-2 finding, not a formatting one.

---

**F3 — Stop calling an unpowered null a null, and claim the agreement the paper already has.**
*(items 23, 57, 53, 34)*

Four edits, all substitutions of equal or shorter length.

- `main.tex:50–52` (abstract): *"The signed along-track residual of its own detections carries
  no offset once box size enters the regression, which is the outcome that training on a window
  ending at the label time enforces."*
  → *"The signed along-track residual of its own detections gives \outTau\,ms with a standard
  error of \outTauSE\,ms, which the training objective's placement of the output at the label
  time predicts and which does not separate that placement from the window centroid."*
- `main.tex:446–448` (Sec. 3.6): *"Its output carries no offset from the label time under
  Eq.~\ref{eq:outreg} (Sec.~\ref{sec:outputtime}), which the training objective forces, and
  carries an anisotropic term of \aniTauZero\,ms…"*
  → *"Its output gives \outTau\,ms under Eq.~\ref{eq:outreg} (Sec.~\ref{sec:outputtime}), at
  \outTauSigmas{} standard errors, and \aniTauZero\,ms under the decomposition that removes the
  isotropic part (Sec.~\ref{sec:aniso}). The two estimators agree in sign and to within
  \outAniGap{} standard errors of the wider of the two intervals."*
  (`\outAniGap` = |11.9 − 16.6| / 8.9 = 0.53.)
- `main.tex:449–451`: *"The two routes to the output time bracket the network's behavior between
  no extrapolation and zeroth-order extrapolation over an interval of the order of the window
  centroid."* → *"Both routes to the output time place it at a zeroth-order extrapolation over an
  interval shorter than, and of the same sign as, the window centroid."*
- `main.tex:774–775` (conclusion): *"places the output at the label instant"* →
  *"places the output within \outTauSE\,ms of the label instant"*.

Sec. 3.4's own wording at `main.tex:354` (*"No output-time offset is established by
Eq.~\ref{eq:outreg} on this checkpoint"*) is correct — **do not change it**; it is the sentence
the other three should have matched.

---

**F4 — Rewrite Section 5 as a bounded envelope; cut it by half.**
*(items 52, 62, 69, 80, 87, 36, 70, 58, 41, 10; also frees the page budget for F1)*

Replace the whole of `main.tex:735–766` with a paragraph that opens on what holds, states the
retraction in one clause, and drops the three research-note phrasings. Draft (~170 words, down
from ~340):

> **Limitations.** The predictor measurements are of one released checkpoint at one released
> configuration on one dataset; the configuration fact of Sec.~\ref{sec:window} is a property of
> the released representation and holds wherever it is used, and the influence profile and the
> anisotropic term are not. Occlusion reports a sensitivity that equals a linear weight only for
> a predictor linear in its bins, and the acceleration regressor is a difference of differences
> of label centers over a \dsecFramePeriod\,ms base, so it carries the label noise of
> Sec.~\ref{sec:labelclock} amplified; $\sigma_{c}$ is itself an extrapolation of a difference
> ladder still decreasing at $k=\ladderK$. The flicker result holds for the
> \dsecCeilingSeqs{} training sequences that reach the ceiling and is not measured on the test
> split or on the sequences whose exposure files did not resolve. Inside those sequences no
> unmodulated stratum exists, so the within-frame dispersion of Sec.~\ref{sec:cost} is bounded
> as a property of the event stream and supports no per-object temporal claim; a spatial
> statistic built to evade the modulation aligns no better than each box's own background
> annulus, and is reported here as ego-motion. Statements about what benchmarks record are
> scoped to those whose documentation we read.

What this removes and why:
- the 85-word E20 sentence and its four numbers (`\egoRingBetter`, `\egoCoreNeg`,
  `\egoCoreWorst`, `\egoCoreWorstSigmas`) → one clause. The retraction is still recorded, as
  `REBUILD_0905.md` requires, but a reader no longer meets a whole experiment for the first time
  as a refutation.
- *"A per-object temporal claim on these sequences was attempted and is not supported"* → folded
  into "supports no per-object temporal claim" (item 58, 69).
- *"Two controls named by our own record are absent, a denoiser ablation … and a stopped-vehicle
  segment"* → **deleted**. Naming two experiments you did not run, from your own internal record,
  is the definition of item 69's open confession. `PROTOCOL_LEDGER.md` keeps the record.
- *"from one API call of unknown coverage"* → deleted from the body; it is already stated twice
  in `supplement.tex:249–256`, which is where a search-tooling caveat belongs.
- the Table 1 SE disclaimer → deleted by F2.
- adds the one positive boundary the section currently lacks (the configuration fact's scope),
  which is also fix F6.

Net: roughly −170 words, which pays for F1(b), F3 and F5 with room left.

---

**F5 — Add the bridge sentence before the contribution list, and strip the numbers from it.**
*(items 18, 19, 20)*

Insert before `main.tex:124`:

> Two measurements follow, one on a released detector and one on a released dataset, each read
> from artifacts the field already distributes.

and reduce the four bullets to mechanism-only noun phrases, following [BD]'s standard of no
numbers in bullets and ~30 words each. Bullet 2 (currently 44 words, `main.tex:129–133`):

> the anisotropic part of the same checkpoint's localization residual, which separates a term
> acting along the direction of travel from the isotropic part, reported beside the two larger
> geometric terms of the same fit (Secs.~\ref{sec:outputtime}--\ref{sec:aniso});

Remove `\rvtCentroidMagMeas` from bullet 1, `\aniTauZero`/`\aniSpeedSigmas` from bullet 2, and
`\flickerLineHz` from bullet 3. All four numbers already appear on the same page.

---

**F6 — Claim the generality that is free, and scope the census that is not.**
*(item 53, both directions; item 84)*

(a) Add to Sec. 3.2, after `main.tex:271`:

> Both files are the released defaults, so the window's placement is a property of the
> representation \texttt{stacked\_histogram\_dt=50\_nbins=10} rather than of any one trained
> model, and holds for every model trained on it, including the state space
> backbones of~\cite{zubic2024ssm}.

Then delete one of the three identical scope disclaimers — `main.tex:442` (*"Both measurements
are of one checkpoint at one configuration"*) is redundant with `main.tex:307–308` on the same
page-turn and with the new Limitations. Net cost ≈ 0 words.

(b) Add nine words to Table 2's caption (`main.tex:547`) so "Every" is scoped:
*"Every DSEC training sequence whose exposure is pinned at \dsecExpMax\,\micro s"* →
*"Every one of the \dsecSeqCount{} DSEC training sequences whose exposure file resolves that is
pinned at \dsecExpMax\,\micro s"*.

(c) Add one sentence to Sec. 3.5 or 3.6 stating the estimator's reuse (item 84):
> The decomposition needs only a detector, tracked labels and a direction of travel, so it
> applies to any benchmark that supplies them.

---

**F7 — Fix the four cross-section contradictions.** *(item 57)*

- `numbers.tex:454`: `\newcommand{\sixLockedLoPct}{99.0}` → `{98.97}`, and `main.tex:114`
  *"between 99.0 % and 100.0 %"* → *"between \sixLockedLoPct\,\% and \sixLockedHiPct\,\%"*
  renders as *"between 98.97 % and 100.00 %"*, matching Table 2. Also set
  `\sixLockedHiPct` to `100.00` for column agreement. A minimum must not be rounded up.
- The `\termRatio` sentence, `main.tex:731–733`: *"Against these, the predictor window of
  Sec.~\ref{sec:influence} is larger by a factor of \termRatio{}"* → name the two datasets:
  *"Against these, the predictor centroid of Sec.~\ref{sec:influence}, measured on Gen1, is
  larger than this DSEC dispersion by a factor of \termRatio{}"*. `REBUILD_0905.md` §3 deleted
  the old Table 4 for exactly this conflation; the prose form must carry the same caveat or go.
- The `evidence time` collision: see F8.
- The `carries no offset` contradiction: fixed by F3.

---

**F8 — Resolve the title / body term collision.** *(items 21, 60, 57, 100–101)*

Pick one. The lower-cost option is to rename the **DSEC** quantity, since it is used seven times
in one subsection and the title is used everywhere:

- `main.tex:614`: *"The \emph{evidence time} of the box is"* →
  *"The \emph{within-window event centroid} of the box is"*, and follow the rename through
  `main.tex:601` (Fig. 4 caption), `main.tex:667` (Table 3 caption), `main.tex:737`,
  `main.tex:744`, `main.tex:751`, `supplement.tex:176` (`\label{sup:evidencetime}` and its
  paragraph), and the Fig. 4(b) axis label `evidence time t̄_i minus mid-exposure (μs)` in
  `src/make_fig_qualitative.py`.
- Then **define** the title's term where it is first used, at `main.tex:244`, folding it into the
  existing `effective timestamp` sentence so no words are added:
  *"The \emph{evidence time} of a predictor is $c_{P}$; its \emph{output time} $\tau_{P}$ is
  not $c_{P}$."* — and use `evidence time` and `output time` consistently thereafter, retiring
  `effective timestamp` (which currently appears once and is then abandoned) and collapsing
  `label instant` / `label time` / `nominal instant` / *"the instant the label asserts"* onto
  one of them.

---

**F9 — Fix Fig. 4(a)'s label collision and Fig. 2's missing panel labels.** *(item 59)*

- `src/make_fig_qualitative.py`: the six box indices in panel (a) overprint for boxes 1–4. Draw
  them with leader lines to an uncrowded margin, or number the boxes in panel (b)'s tick labels
  only and drop the in-image numerals (panel (b) already carries `1 n=601`, `2 n=1224`, …).
  `REBUILD_0905.md` §2 records this as fixed; it is not.
- `src/make_figs.py`, `fig_predictor()`: add `(a)` and `(b)` panel labels — the caption uses them
  and the figure does not carry them.
- Optional, for register consistency: Fig. 4 is the only colour figure (viridis colourbar in (a),
  red dashed line in (b)) among four; the red `frame mean` line should be black dashed.

---

**F10 — Cut the seven long sentences that carry no measurement.** *(items 41, 10)*

After F4 removes the 85-word Limitations sentence, the remaining priority targets are the
abstract's 59-word sentence (`main.tex:52–58`, split at *"…standard errors."*), the conclusion's
61-word (`main.tex:781–787`) and 51-word (`main.tex:775–778`) sentences, and
`main.tex:224–230`'s 53-word four-clause related-work chain. Splitting these four brings the
≥ 35-word count from 62 to roughly 55 and takes the maximum from 85 to ~45. Do not touch the
36–42-word sentences that carry a measurement and its null in one breath — those are the
paper's register and item 150 forbids changing what is not awkward.

---

**F11 — Small, mechanical.**

- `main.tex:411`: *"**We therefore** fit…"* → *"The two channels are fitted with the same four
  regressors…"* (item 64, the only meta sentence).
- `main.tex:520`: *"That fraction is quoted of live pixels; of the sensor it is
  \lockedSensorPct\,\%."* → *"That fraction is quoted of live pixels, and of the sensor it is
  \lockedSensorPct\,\%."* (item 61, the only defective semicolon).
- `main.tex:503`: `\subsection{The line, and the per-pixel test}` →
  `\subsection{The mains line and the per-pixel test}` (item 38; also gives "the line" its
  antecedent).
- `main.tex:439`: `\subsection{The interval between the two measurements}` →
  `\subsection{Evidence time against output time}` (item 38/60; removes the collision with the
  Sec. 3 heading).
- Delete `\eff` from `main.tex:22` and `supplement.tex:19` (defined, never used).
- Write a README for `e17`, `e21`, `e24`, `e25`, `e26`, and add the four SE values and eight
  coefficients of Table 1 to `e24_order/result.json`. Every Table 1 number currently exists only
  as stdout in `run.log`. This is round 2's provenance blocker, not a paper edit.

---

## What was checked and found sound

Recorded so round 2 does not re-litigate it: the retraction firewall (zero retracted numbers,
macros or cross-references reach either document, verified three ways); the numbers-to-experiment
ledger (326 macros, zero bare numerals in prose, zero `[unmeasured]` rendered); the page limit
under both the submitted and CVPR's own textblock; British/American spelling (one hit, correct);
percent spacing (26/26 consistent); raw quotes (zero); em dashes (zero); parenthetical asides
(zero); demonstrative referents; the four flicker control arms; and the claim-vs-non-claim
discipline of Secs. 3.3, 3.4 and 4.4, which is better than the reference papers'.
