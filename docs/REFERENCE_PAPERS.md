# External reference papers for `paper/main.tex`

Target: *Temporal Support Error in Event–RGB Detection Benchmarks* (CVPR 2027 submission),
`/media/hdd8/justin/my_project/CVPR20/paper/main.tex`.

Written 2026-09-02. Every paper below was fetched from outside this repository as a full PDF
and read from the PDF, not from a title or an abstract listing. No internal paper is used as a
reference. WebSearch was unavailable for this session; venue attribution was verified by
grepping the CVF open-access proceedings listings pulled directly from
`openaccess.thecvf.com/<VENUE>?day=all`, and each PDF carries the CVF open-access watermark
("This CVPR/ICCV paper is the Open Access version ... identical to the accepted version").

Local copies of the PDFs and extracted text are in the session scratchpad:
`/tmp/claude-1000/-media-hdd8-justin-my-project-CVPR20/b6a997df-7e53-4247-8ec4-d4bd4f084c49/scratchpad/pdfs/`.

---

## 0. Verification of the candidates named in `docs/CHECKLIST_197.md` (lines 214–216)

The checklist names six structural exemplars. They were checked against the proceedings
listings before any of them was relied on. **One of them does not exist.**

| Named in checklist | Verdict | Evidence |
|---|---|---|
| Generative Image Dynamics (CVPR 2024 Best Paper) | **Exists, and the Best Paper attribution is correct** | In `CVPR2024?day=all` as `Li_Generative_Image_Dynamics_CVPR_2024_paper`. `cvpr.thecvf.com/Conferences/2024/News/Awards` lists it first under "Best Papers" with the correct author list (Li, Tucker, Snavely, Holynski). |
| MVBench (CVPR 2024 Highlight) | **Exists as an accepted CVPR 2024 paper**; Highlight status not verifiable | `Li_MVBench_A_Comprehensive_Multi-modal_Video_Understanding_Benchmark_CVPR_2024_paper`. The CVF listing does not encode Highlight status, and the awards page names only Best Papers, so "Highlight" is unverified here — do not cite it as such. |
| Learning Object State Changes in Videos (CVPR 2024) | **Exists** | `Xue_Learning_Object_State_Changes_in_Videos_An_Open-World_Perspective_CVPR_2024_paper`. Note the full title has the subtitle "An Open-World Perspective". |
| Neuralangelo (CVPR 2023) | **Exists** | Fetched `CVPR2023?day=all` (2353 papers); `Li_Neuralangelo_High-Fidelity_Neural_Surface_Reconstruction_CVPR_2023_paper`. |
| Time Blindness (CVPR 2026) | **Exists** | `Upadhyay_Time_Blindness_Why_Video-Language_Models_Cant_See_What_Humans_Can_CVPR_2026_paper`, pp. 30906–30913. |
| **AbstainEQA (CVPR 2026 Highlight)** | **DOES NOT EXIST — misattributed** | Absent from the 4042-paper CVPR 2026 listing (grep for `abstain` and `EQA` returns only *BridgeEQA*, *OpenEQA*, *SeqAfford*). An arXiv API query for `all:AbstainEQA` returns zero results, as does `ti:"embodied question answering" AND abs:abstention`. **Remove it from the checklist or replace it.** |
| VirtueBench (CVPR 2026) | **Exists**, full title differs | `Yu_VirtueBench_Evaluating_Trustworthiness_under_Uncertainty_in_Long_Video_Understanding_CVPR_2026_paper`. |

---

## Reference 1 — same problem family

### Beyond Duality: A Hybrid Framework of Leveraging Shared and Private Features for RGB-Event Object Detection

- **Authors**: Keyao Wang, Shuai Liu (corresponding), Hengda Shi, Lukui Shi, Haiyong Chen.
  School of Artificial Intelligence, Hebei University of Technology, Tianjin; Tianjin Institute
  of Advanced Technology.
- **Venue / year**: CVPR 2026, pp. 4415–4423.
- **Verification**: present in `openaccess.thecvf.com/CVPR2026?day=all`; the fetched PDF
  carries the CVF open-access watermark and the CVPR 2026 page numbers.
- **Why this one**: it is the closest living neighbour of the submission — RGB–Event object
  detection, **evaluated primarily on DSEC-Det**, the submission's own primary testbed, and it
  re-scores RVT, SAST, S5-ViT and SMamba there.

**Abstract's opening move.** *"RGB-Event object detection is able to capture clear and detailed
features of the target while maintaining high-speed information collection. It is suitable for
high dynamic or harsh environments and has become a research hotspot in recent years."*
Pure background — two sentences that assert the field's value before any problem is named. The
problem arrives in sentence 3, the method in sentence 4, the result in the last sentence.

**Introduction structure (first page, 5 paragraphs).**
1. Task definition and why the modality pair is worth having (RGB gives texture and static
   objects, events give speed and low light), closing on the application (autonomous driving).
2. Names the key challenge (using both modalities effectively), then a two-generation history:
   early concatenation/post-processing fusion, then Transformer-based fusion.
3. The gap, made concrete with two named scenarios: low light where RGB fails (Event-private
   features) and ego-speed-matched motion where events fall silent (RGB-private features).
   Points at Fig. 1(b).
4. Method summary in one paragraph — the three modules by name, then datasets, then the
   result claim.
5. Four numbered contribution bullets.

**Figure 1.** A **conceptual contrast**, not a system diagram and not a result: (a) a box
diagram of what existing methods do (two encoders → fusion → decoder), (b) the same pipeline
redrawn with the paper's separation. Two rows, no images, no numbers. It exists to make the
delta legible in three seconds.

**Contribution list.** Four numbered bullets, 2–3 lines each, ~30 words each. **No numbers
appear in any bullet** — the bullets name mechanisms ("A frequency-domain disentanglement
module is proposed to separate shared and private features") and the accuracy claim is
qualitative ("achieving satisfactory results in challenging scenarios").

**Claim calibration.** Main claim sentence: *"Experimental results on the DSEC-Det and
PKU-DAVIS-SOD datasets **demonstrate** that our model achieves **competitive** performance with
state-of-the-art methods."* Verb: **demonstrate**, softened by "competitive" rather than
"outperforms" — even though §4.3 does say "achieves state-of-the-art". The abstract is one
notch more conservative than the body.

**Section order.** 1 Introduction / 2 Related Work (2.1 Transformer-based detection, 2.2
RGB-Event fusion, 2.3 Frequency-domain disentanglement) / 3 Method (3.1 overview, 3.2 FCFS,
3.3 TriAdapt Encoder, 3.4 TriInject Decoder) / 4 Experiments (4.1 datasets and metrics, 4.2
implementation, 4.3 comparison, 4.4 ablation, 4.5 effectiveness analysis, 4.6 visualisation) /
**5 Limitations** / 6 Conclusions. Each section answers: what is the task, what has been tried,
what we built, does it work, when does it not, what is the summary.

**Limitations.** A **separate numbered section**, but only five lines: both modalities degraded
simultaneously (low-contrast APS, noisy events, strong blur) makes coherence estimation
unreliable; one sentence of future work. Short and un-hedged.

**Table 1.** SOTA comparison on DSEC-Det and PKU-DAVIS-SOD: mAP, mAP50 and parameter count,
with a `Pub. Year` column and rows grouped Event-only / RGB-only / fused. **It directly tests
the thesis** — the thesis is "our fusion is better", and Table 1 is the ordering.

**Related work.** ~1.1 columns, three subsections, **before** the method.

**Two findings worth importing into `main.tex` regardless of style.**
- *"The DSEC-Det dataset provides multiple annotation versions. Our ablation studies are
  conducted on the original annotations, while for fair comparison with prior works, we adopt
  the SFNet annotation version in the comparative experiments."* The submission's §7.2 label
  forensics (E06, 390 118 boxes) reports on **one** release. A CVPR 2026 paper on the same
  dataset states that more than one exists. **`main.tex` must name which annotation version
  E06 read**, or the forensics claim is under-specified.
- Its Table 1 gives a reproduction target for the submission's "every detection number is
  gated on reproduction" rule: RVT on DSEC-Det = 25.1 mAP50 / 12.9 mAP, 18.5 M parameters;
  SAST 24.3/12.1; S5-ViT 22.3/11.4; SMamba 29.0/14.8; YOLOX (RGB) 43.5/26.5.

---

## Reference 2 — same paper type (the closest structural match, and the most important)

### On the Content Bias in Fréchet Video Distance

- **Authors**: Songwei Ge (UMD), Aniruddha Mahapatra (CMU / Adobe Research), Gaurav Parmar (CMU),
  Jun-Yan Zhu (CMU), Jia-Bin Huang (UMD).
- **Venue / year**: CVPR 2024, pp. 7277–7288 (8-page body + references).
- **Verification**: `Ge_On_the_Content_Bias_in_Frechet_Video_Distance_CVPR_2024_paper` in the
  CVPR 2024 listing; PDF carries the CVF watermark.
- **Why this one**: it is the same *kind of object* as the submission. It proposes no new
  method. It takes a metric the field already publishes, argues the metric is **blind to a
  specific axis** (temporal quality), quantifies the blindness under a controlled perturbation,
  shows the blindness can be exploited to move the score without moving the underlying quality,
  and then re-visits published results to show the ordering the field reported was wrong. That
  is, structurally, exactly what `main.tex` intends to do to average precision and time.

**Abstract's opening move.** *"Fréchet Video Distance (FVD), a prominent metric for evaluating
video generation models, is known to conflict with human perception occasionally. In this paper,
we aim to explore the extent of FVD's bias toward per-frame quality over temporal realism and
identify its sources."*
Sentence 1 = one clause of background plus the **already-known symptom**. Sentence 2 = the
paper's job, stated as a verb of measurement ("explore the extent … and identify its sources").
No definitional preamble. The remaining six sentences of the abstract are, in order, the three
experiments and their outcomes, then the mitigation, then the real-world validation. **Every
result sentence contains a direction ("increases only slightly", "drastically decrease").**

**Introduction structure (first page, ~7 short paragraphs).**
1. Field context in three sentences → *"In this paper, we focus on analyzing the bias of FVD."*
   The target is named on the first page, first paragraph.
2. What FVD is, with Eq. (1) inline. Background is given as **mathematics, not as prose**.
3. Prior evidence in both directions: FVD demonstrably works for convergence, tuning and
   architecture choice [92, 11, 30, 31, 64]; but recent studies report contradictions [11, 20,
   64]. Names the phenomenon: *content bias*.
4. The Figure 1 walkthrough — the reader is taken through (a) reference, (b) spatial-only
   distortion, (c) severe temporal distortion, and told which one FVD prefers and which one a
   human prefers. **Two numbers appear here (317.10 vs 310.52).**
5. *"we present the first systematic study to quantify the content bias"* — the three
   experiments enumerated in the order the paper will run them.
6. A rhetorical question — *"Where does the content bias originate from?"* — then the
   hypothesis (I3D features trained on Kinetics) with two enumerated concerns.
7. Verification of the hypothesis, the headline finding, code release.

**Figure 1.** A **failure example**, full-width, three video columns each with an *x-t* slice
strip underneath, captioned with the two FVD scores and the sentence *"FVD is biased towards
per-frame quality than temporal consistency."* It is the paper's whole argument in one image:
the reader sees the temporal artefact in the *x-t* slice, and sees the metric prefer it anyway.

**Contribution list.** **There is none.** No bullets, no "our contributions are". The
contributions live in the abstract's result sentences and in the section titles. Numbers appear
in the body, not in a bullet list.

**Claim calibration.** Two sentences carry the claim. In the introduction: *"Both studies
**suggest** FVD's bias towards the quality of individual frames."* In the discussion: *"we have
**concluded** that FVD is highly insensitive to the temporal quality and consistency of the
generated videos. We have **verified the hypothesis** that the bias originates from the
content-biased video features."* Verbs: **suggest** before the evidence, **conclude / verify**
after it. Never *prove*, never *enable*.

**Section order and the question each answers.**
1. Introduction — what is wrong with FVD, and what will be done about it.
2. Related Work — *~0.6 columns*, video generation and evaluation metrics.
3. **Quantifying the Temporal Sensitivity of FVD** — how much does FVD move when only
   temporal quality is destroyed? (**starts on page 3 of 8**)
4. **Probing the Perceptual Null Space in FVD** — can the score be lowered without improving
   temporal quality at all?
5. **Case Study: Long Video Generation** — does this change any published conclusion?
6. Discussion — what it means, what remains unexplored.
Note that sections 3, 4 and 5 are named after **questions**, not after objects.

**Limitations.** A single labelled paragraph, ~7 lines, **folded into the Discussion section**
("Limitations. Several critical aspects of FVD remain underexplored…"). Not a section.

**Table 1.** *"Analyzing FVD temporal sensitivity with video distortions."* Six datasets ×
{FID, FVD} × {spatial, spatiotemporal}. **It directly and solely tests the thesis**: FID moves
by −1.1 % to +0.6 % (frame quality held constant, by construction) while FVD moves by +3.6 % to
+35.7 %. One table, one claim, and the null (FID) sits in the same table as the treatment.
Tables 2–4 are the null-space probe and the two re-scored published results.

**Related work.** ~0.6 columns — the shortest of the five — placed **after** the introduction
and **before** the first experiment. It ends with the sentence that licenses the paper:
*"the analysis and improvement of the FVD are much less explored than those of FID."*

---

## Reference 3 — structurally exemplary (and a second instance of the same paper type)

### Time Blindness: Why Video-Language Models Can't See What Humans Can?

- **Authors**: Ujjwal Upadhyay (KAUST / DocPanel Technologies), Mukul Ranjan (VILA Lab, MBZUAI),
  Zhiqiang Shen (MBZUAI), Mohamed Elhoseiny (KAUST). Equal first-authorship; corresponding
  authors marked.
- **Venue / year**: CVPR 2026, pp. 30906–30913.
- **Verification**: `Upadhyay_Time_Blindness_Why_Video-Language_Models_Cant_See_What_Humans_Can_CVPR_2026_paper`
  in the CVPR 2026 listing; PDF carries the CVF watermark.
- **Why this one**: it is a measurement paper whose entire force comes from a **single
  controlled contrast stated as two numbers** (98 % vs 0 %), which is the discipline `main.tex`
  most needs. It also demonstrates the "existing benchmarks are blind to a temporal axis"
  framing at maximum strength.

**Abstract's opening move.** *"Recent advances in vision-language models (VLMs) have made
impressive strides in understanding spatio-temporal relationships in videos. However, when
spatial information is obscured, these models struggle to capture purely temporal patterns."*
Sentence 1 = background stated as a **concession** (the models are good). Sentence 2 = the
condition under which the concession fails. The instrument is named in sentence 3, and the
result — 98 % versus 0 % — lands in sentence 4 of the abstract.

**Introduction structure (first page, 6 paragraphs).**
1. Field context (LMMs → Video-VLMs → four capability areas with citations) → the loophole
   (*"even in tasks labeled as temporal, strong per-frame spatial cues often allow models to
   succeed without genuinely reasoning over time"*) → *"This paper introduces SpookyBench, a
   benchmark that closes this loophole"* → one sentence describing the construction. **The
   contribution is named in the first paragraph.**
2. The prevailing paradigm (frame features → temporal integration → language fusion), then
   *"our findings reveal a critical blind spot"*, then external motivation for why purely
   temporal signals matter (firefly bioluminescence, pre-ictal EEG, Morse code).
3. The human side: neuroscience on distributed temporal processing; participants reach >98 %.
4. The machine side: 15 SOTA models including GPT-4o and Gemini 2.0 Flash; near-zero.
5. Robustness of the gap: across architectures, 2 B to 78 B parameters, and across models
   explicitly built for temporal reasoning.
6. Implication (rethink how architectures process time) and the release call.

**Figure 1.** A **conceptual contrast / system diagram hybrid**: video → frame sampling
("temporal information loss") → visual encoder ("spatial bias") → a fork into a well-represented
"Spatial Features" branch and an under-represented "Temporal Features" branch, with a
"coherence gap ×" between them, feeding the language model. It is the weakest element of an
otherwise very strong paper — it diagrams the hypothesis rather than exhibiting the failure.
The paper's real Figure 1 is its Table 1.

**Contribution list.** **No bullets.** The contributions are carried by the abstract and by the
first paragraph of the introduction.

**Claim calibration.** *"while humans can recognize shapes, text, and patterns in these
sequences with over 98% accuracy, state-of-the-art VLMs **achieve** 0% accuracy. This
**highlights** a critical limitation: an over-reliance on frame-level spatial features and an
inability to extract meaning from temporal cues."* Verbs: **achieve** (factual, for the
measurement) then **highlight** (interpretive, for the reading). The interpretation is kept in
a separate sentence from the measurement — the paper never lets a verb do the work a number
should do.

**Section order.** 1 Introduction / 2 Related Work (2.1 temporal reasoning in Video-VLMs, 2.2
neuroscience) / 3 SpookyBench (3.1 dataset generation, 3.2 temporal encoding framework, 3.3
signal metrics) / 4 Experiments (4.1 model evaluation, 4.2 human evaluation, 4.3 frame-rate,
4.4 fine-tuning, 4.5 motion-boundary augmentation) / 5 Discussion (5.1 architectural
implications) + conclusion. Questions answered: what is missing, who has looked, what did we
build, what does it measure, what does that mean for architectures.

**Limitations.** **Absent as a section.** Folded into §4.4/§4.5 and §5 as controls: fine-tuning
does not fix it, motion-boundary augmentation gives only a small improvement, the failure is
"not from task impossibility but from architectural inability". The paper handles limitations
by *running the experiment that would have been the objection*.

**Table 1.** The benchmark result: 27 models (open and closed source) × {direct prompt, CoT} ×
parameter count, with the human row at the top at 98.0 % ± 0.6. **It is the thesis.** A whole
column of `0% ± 0.0` is the most efficient result table in any of these five papers. It appears
on **page 3 of 8**.

**Related work.** ~1.3 columns, two subsections, before the benchmark construction.

---

## Reference 4 — supporting, structurally exemplary (Introduction pacing and Figure 1)

### Generative Image Dynamics

- **Authors**: Zhengqi Li, Richard Tucker, Noah Snavely, Aleksander Holynski (Google Research).
- **Venue / year**: **CVPR 2024 — Best Paper Award**, pp. 24142–24153.
- **Verification**: in the CVPR 2024 listing as
  `Li_Generative_Image_Dynamics_CVPR_2024_paper`, and named first under "Best Papers" on
  `cvpr.thecvf.com/Conferences/2024/News/Awards` with the matching author list. This is the one
  award attribution in the checklist that verifies exactly.
- **Why included**: the checklist names it for Introduction pacing and Figure 1, and it earns
  that. Its relevance here is narrow but sharp — it is the best available model of a **Figure 1
  that is the paper**, and of a Limitations paragraph that concedes without deflating.

**Abstract's opening move.** *"We present an approach to modeling an image-space prior on scene
motion. Our prior is learned from a collection of motion trajectories extracted from real video
sequences depicting natural, oscillatory dynamics of objects such as trees, flowers, candles,
and clothes swaying in the wind."* Sentence 1 = the contribution, flat, in eleven words.
Sentence 2 = what it is made of, made concrete by naming four physical objects. **Zero
sentences of background.**

**Introduction pacing (7 paragraphs).** motivation (the world is always in motion) → why it is
hard (physical parameters are unmeasurable at scale) → the escape (observed 2D motion suffices,
and is predictable) → the enabling technology (diffusion) → *"In this paper, we model …"* → how
→ why a motion prior beats an RGB prior. Note that paragraphs 2 and 3 are a **problem/escape
pair**: the difficulty is stated at full strength and then dissolved, which is the move
`main.tex` makes with the constant-offset concession but spreads across three separate places.

**Figure 1.** A **result plus representation diagram**: input picture → the predicted spectral
volume rendered as X/Y coefficient stacks at 0.2/0.4/…/3.0 Hz → two output uses (looping video,
interactive dynamics) shown as *x-t* slices. No numbers. Full width, page 1.

**Contribution list.** None. Prose only.

**Claim calibration.** *"We **show** that our approach produces photo-realistic animations from
a single picture and **significantly outperforms** prior baselines."* Verb: **show**. The
strength word attaches to the measured comparison, not to the idea.

**Section order.** 1 Introduction / 2 Related Work (~0.9 columns) / 3 Overview / 4 Predicting
motion / 5 Image-based rendering / 6–7 Applications and experiments (7.3 ablation) / 8
Discussion and conclusion.

**Limitations.** One labelled paragraph, ~8 lines, opening §8 **before** the conclusion
paragraph. Three concrete failure modes, each with a mechanism, one with a figure reference
(Fig. 8). No apology, no hedging language.

**Table 1.** Quantitative comparison on the test set against five baselines. Directly tests the
thesis. It is the paper's **only** table.

---

## Reference 5 — supporting, same problem family (the secondary testbed)

### EvRT-DETR: Latent Space Adaptation of Image Detectors for Event-based Vision

- **Authors**: Dmitrii Torbunov, Yihui Ren, Animesh Ghose, Odera Dim, Yonggang Cui
  (Brookhaven National Laboratory).
- **Venue / year**: ICCV 2025.
- **Verification**: `Torbunov_EvRT-DETR_Latent_Space_Adaptation_of_Image_Detectors_for_Event-based_Vision_ICCV_2025_paper`
  in `openaccess.thecvf.com/ICCV2025?day=all`; PDF carries the CVF watermark.
- **Why included**: it is the current reference point on **Gen1 and 1Mpx/Gen4**, the
  submission's secondary testbed, and it establishes what a 2025-era event-detection reviewer
  expects a results table to contain.

**Abstract's opening move.** *"Event-based cameras (EBCs) have emerged as a bio-inspired
alternative to traditional cameras, offering advantages in power efficiency, temporal
resolution, and high dynamic range. However, development of image analysis methods for EBCs is
challenging due to the sparse and asynchronous nature of the data."* Background then obstacle —
the standard event-vision opening, which is worth knowing precisely because `main.tex`
deliberately refuses it.

**Figure 1.** A **result**: mAP versus inference time scatter on 1Mpx, circle area ∝ parameter
count, the paper's two models in the upper-left. **Not** a teaser image and **not** a diagram —
a Pareto plot that positions the contribution against eight named competitors on page 1.

**Claim calibration.** *"The resulting EvRT-DETR model **reaches** state-of-the-art performance
on the standard benchmark datasets Gen1 (mAP +2.3) and 1Mpx/Gen4 (mAP +1.4). These results
**demonstrate** a fundamentally new approach…"* — the deltas are in the abstract, in
parentheses, attached to the dataset names.

**Section order.** 1 Introduction / 2 Related Work (2.1 EBC data representations, 2.2 EBC
detection, 2.3 Transformer detection, 2.4 model adaptation) / 3 Method / 4 Evaluation (4.1
setting, 4.2 performance analysis, 4.3 generalisability, 4.4 design-choice analysis) /
conclusion. Related work is ~1.5 columns, before the method.

**Table 1.** *"Performance Comparison on Event-based Camera Datasets"* — Gen1 and 1Mpx side by
side against the published event-detection field. Directly tests the thesis. **Limitations are
absent** as either a section or a labelled paragraph.

---

## Comparison table: references vs. `main.tex` as it currently stands

`main.tex` state used below: 60 465 bytes, compiled to `main.pdf` = 11 pages (body pp. 1–9,
references pp. 10–11); **1 figure**, 3 tables; `numbers.tex` shows 7 headline macros
(`\tauHatRVT`, `\tauHatCI`, `\sigmaTau`, `\panelCIntercept`, `\panelCSlope`, `\apSyncDelta`,
`\apBiasDelta`) still resolving to `\TODOnum`, which typesets as a red **[unmeasured]**.

| Dimension | What the references do | What `main.tex` does | Verdict |
|---|---|---|---|
| **Abstract, sentences 1–2** | FVD: known symptom + the paper's measurement job. TB: concession + the condition where it fails. GID: the contribution, flat. All reach a *result* by sentence 3–4. | Two sentences of definitional background about what a benchmark is; the first result sentence is sentence 5. | **DIVERGES** — the opening is correct in kind (problem-first, no field-praise) but the run-up is 2–3 sentences too long, and it delays the one thing every reference front-loads. |
| **Abstract carries a number** | All five. FVD: "increases only slightly". TB: 98 % vs 0 %. EvRT: "(mAP +2.3)". Beyond Duality: none in the abstract, deltas in §4.3. | Carries `\dsecExpRatio` (127×) and `\dsecFramePeriod` (50 ms), which are real; but `\tauHatRVT` and `\sigmaTau` currently render as **[unmeasured]**. | **DIVERGES, severely** — no accepted paper's abstract contains a placeholder. |
| **Introduction: contribution named by ¶1–2** | TB names SpookyBench in ¶1. FVD names its target in ¶1. GID by ¶5. | The contribution paragraph is the **last** paragraph of a six-paragraph introduction. | **DIVERGES** (mild) — acceptable pacing, but late by the standard of the two closest matches. |
| **Introduction concedes and dissolves** | GID ¶2–3 state the difficulty at full strength, then dissolve it. FVD ¶3 concedes FVD works, then reports where it does not. | Does this well — ¶5 concedes that the constant part is a reporting problem before making any claim from it. | **MATCHES** (a genuine strength; do not remove it). |
| **Figure 1 type** | FVD: failure example, with the two metric values. TB: conceptual contrast. Beyond Duality: conceptual contrast. GID: result + representation. EvRT: result (Pareto). | Measurement/evidence plot of published DSEC exposure metadata; full-width; explicitly "no model is run". | **MATCHES in kind** (evidence-first is right for this paper) / **DIVERGES in consequence** — it shows the *dispersion of the cause* but never the *effect*. FVD's Fig. 1 works because the metric values sit in the caption. |
| **Number of figures** | FVD 13, GID 8, Beyond Duality 8, TB ~6, EvRT 5. | **1.** | **DIVERGES** — one figure in a nine-page body reads as an unfinished draft regardless of content. |
| **Contribution list format** | Beyond Duality: 4 numbered bullets, ~30 words each, no numbers in them. FVD / TB / GID: no bullets at all, contributions in the abstract. | One 150-word sentence with four semicolon-separated clauses, buried at the end of §1. No numbers. | **DIVERGES** — it is neither format. It is longer than the prose form and less scannable than the bullet form. |
| **Main claim verb** | suggest → conclude / verify (FVD); achieve → highlight (TB); demonstrate (Beyond Duality); show (GID); reaches → demonstrate (EvRT). Never *prove*, never *enable*. | "We first **show** that the extent is published and large"; "we **claim** no downstream accuracy gain". | **MATCHES** — the verb register is right, and the explicit non-claim is stronger calibration than any reference manages. Keep it. |
| **Section titles** | FVD names sections after questions ("Quantifying…", "Probing…"). TB and Beyond Duality use object names. | Object names throughout ("Temporal support", "Scoring", "Results"). | **DIVERGES** (mild) — legal, but FVD is the closest match and it does the opposite. |
| **Formalism before first measurement** | FVD: first experiment section on **p. 3 of 8**. TB: Table 1 on **p. 3 of 8**. GID: method from §3. | §3 definitions, §4 estimator, §5 metric, §6 protocol — the first table lands on **p. 7 of 9**, and the first table that tests the thesis on **p. 8**. | **DIVERGES, severely** — this is the largest pacing gap in the comparison. |
| **Section order and coverage** | Intro / Related / construction / experiments / discussion — all five. | Intro / Related / support / estimator / metric / protocol / results / limitations / conclusion. | **MATCHES in order**, **DIVERGES in weight** — three formalism sections where the references have one construction section. |
| **Related work: position** | All five: after introduction, before method. | Same (§2). | **MATCHES**. |
| **Related work: length** | FVD ~0.6 col; GID ~0.9 col; Beyond Duality ~1.1 col; TB ~1.3 col; EvRT ~1.5 col. | Spans p. 2 to p. 3 — **~2.4 columns**, five paragraphs, and it is where the novelty defence lives ("What is new here"). | **DIVERGES** — roughly twice the longest reference and four times the closest match. A defence this long on page 2 reads as anticipating an attack. |
| **Table 1: does it test the thesis?** | FVD: yes, and it contains its own null (FID) in the same table. TB: yes, it *is* the result. Beyond Duality / EvRT: yes, it is the ordering. GID: yes. | Table 1 = DSEC exposure metadata. It establishes the **premise** (label support is large and published) and is fully measured and un-simulated — but it does not test the thesis. The thesis tables are 2 and 3, and **every cell in both is [unmeasured]**. | **DIVERGES** — a reviewer opening to Table 1 sees a dataset survey; opening to Tables 2–3 sees red placeholders. |
| **Nulls reported beside treatments** | FVD Table 1 puts FID (the null) beside FVD; Table 2 colours the null-space drop. | Does this better than any reference: `\apbias` is a purpose-built null in the same table as `\apsync`; the estimator's own per-object variance is the null for `\sigma_\tau`. | **MATCHES / EXCEEDS** — this is the submission's strongest structural asset. It is currently invisible because the cells are empty. |
| **Limitations handling** | Beyond Duality: separate section, **5 lines**. GID: labelled paragraph in §8, ~8 lines. FVD: labelled paragraph in §6, ~7 lines. TB: absent as a section — replaced by controls that run the objection. EvRT: absent. | A full `\section{Limitations}` with **six named paragraphs**, ~0.6 page. | **DIVERGES** — 5–10× longer than any reference. The content is excellent and the concessions are load-bearing; the *volume* is what diverges. |
| **Objections answered by experiment rather than by prose** | TB is the model: fine-tuning arm, motion-boundary arm, human arm. | Partially — §7.3 masking probe and §6.2 derivation are exactly this move, and §4.4's three controls are planned. But the strongest objection answers (E05, E06) are currently reported as caveats rather than as results. | **DIVERGES** (mild) — the material exists; its framing is defensive rather than affirmative. |
| **Body length** | FVD, TB, GID, Beyond Duality, EvRT: 8-page bodies. | Body runs pp. 1–9 in the draft's own geometry (`article` + custom `geometry`, **not** `cvpr.sty`, which is present in `paper/` but never `\usepackage`d). | **CANNOT TELL** — the draft does not compile under the real CVPR class, so the true page count is unknown. It is at least one page over on the current geometry. |
| **Reproduction / baseline table on the primary testbed** | Beyond Duality gives RVT/SAST/S5-ViT/SMamba/YOLOX on DSEC-Det. EvRT gives the full field on Gen1 and 1Mpx. | §6.1 states the gating rule ("run through its authors' own validation path … dropped rather than repaired") but no table shows the reproduced scores. | **DIVERGES** — the rule is stated and its output is not shown. Both same-family references show theirs. |
| **Dataset version discipline** | Beyond Duality states DSEC-Det has multiple annotation versions and names which it used for which experiment. | §7.2 reports 390 118 boxes / 6693 tracks / 60 sequences without naming the annotation release. | **DIVERGES** — a one-line fix with real reviewer consequence. |

---

## Actionable changes to `main.tex`, ordered by effect on a reviewer's impression

Ordering rule applied: how much the change moves a reviewer between "unfinished" and
"publishable". None of these narrows the central claim; where a change removes text, the claim
or concession it carried is relocated, not dropped.

### 1. Remove every `[unmeasured]` from the abstract; put the measured result there instead
No accepted paper's abstract contains a placeholder, and a reviewer who sees red in the
abstract stops reading as a reviewer. The submission **already owns four fully measured
results**: the DSEC exposure survey (E00: 127×, 50 ms, 32.5 % pinned, 21 142 frames), the
label-clock convention check (E00: image timestamp = mean mid-exposure to within 1 µs), the
DSEC-Det label forensics (E06: 390 118 boxes, 0.707 px interpolation residual — the released
labels are *not* interpolated), and the masking-lever saturation (E05). Rewrite the abstract so
its result sentences are these, and state the effective-timestamp estimate as **what the paper
reports** rather than as a number that is not there yet: "we estimate it for released
checkpoints … and report it in milliseconds with its within-output dispersion" — then let
`\tauHatRVT` enter only when E1a/E1d land. This is a re-ordering of measured claims, not a
retreat: the thesis sentence ("what a declared scalar cannot absorb is the dispersion") stays
exactly as written.

### 2. Move a measured result to page 2–3
Both same-type references put their thesis-testing table on **page 3 of 8**; `main.tex` puts
its first table on page 7. Promote §7.1 (exposure metadata, Table 1) and §7.2 (label forensics)
out of Results and into a short §2 or §3 titled for the question they answer — e.g.
*"What the label clock of a benchmark actually is"*. These are the paper's finished
measurements and they currently sit behind three sections of formalism. Move the kernel
formalism of §3.1 (Eq. 1, `c_P`/`w_P`) and the relaxation-budget derivation to the supplement,
keeping the definition of the effective timestamp and the `\tau_P` ≠ `c_P` distinction in the
body, since §6.2's argument depends on it.

### 3. Add a second figure that shows the mechanism, and add the consequence to Figure 1
`main.tex` has one figure; the references have five to thirteen. The missing figure is the one
FVD's Figure 1 supplies: the **consequence**, shown rather than asserted. Two candidates, both
buildable from already-measured numbers with no new claim:
- *Figure 2 (conceptual contrast)*: one timeline showing the DSEC exposure window (118–14 996
  µs, E00) and the RVT event window `[t−50 ms, t]` (E02) against the single indexed timestamp
  `t`, with the residual `τ v*` drawn along the track tangent. This is the paper's whole
  argument in one panel and it currently exists only as three paragraphs of §1 and §3.3.
- *Figure 1, third panel*: a DSEC frame with a ground-truth box drawn at `t` and the same box
  displaced by 25 ms at the sequence's measured image speed, so the reader sees the offset in
  pixels. Caption it as a construction from published metadata, matching the existing caption's
  "no model is run" discipline.

### 4. Cut Related Work from ~2.4 columns to ~1, by relocation rather than deletion
The closest structural match (FVD) spends 0.6 columns; the longest reference spends 1.5. Keep
§2's four paragraph headings but move the **differentiation** material to where it is used:
the Qin–Shen provenance belongs beside Eq. (4) in §4.1 (it is already stated there — the §2 copy
is redundant), the Streamer differentiation belongs at the head of §5.1 (also already stated
there), and the LET-3D-AP import belongs in §5.2. Delete the standalone *"What is new here"*
paragraph and let those three in-place sentences carry it. Every ancestor stays cited, every
differentiation survives — the defence stops being a page-2 block and becomes a property of the
sections it defends.

### 5. Turn the contribution sentence into three or four numbered bullets
The current 150-word semicolon chain is neither the bullet form (Beyond Duality) nor the
compressed-prose form (FVD, TB, GID). Split it at the existing semicolons into four bullets of
2–3 lines: (i) operational definition of effective timestamp and label support, with a derived
rather than swept tolerance; (ii) the estimator on released checkpoints, with the
errors-in-variables treatment, the over-identifying scale channel, and the anchor-time form;
(iii) `AP^sync` with a cross-fitted constant, reported against `AP^bias`; (iv) the measurements
on DSEC/DSEC-Det. Where a bullet has a measured number behind it, put the number in the bullet.

### 6. Compress Limitations to one labelled paragraph plus a supplement section — keeping every concession
No reference spends more than eight lines. Six named paragraphs signals to a reviewer that the
authors expect six attacks. **Do not delete any concession**: (a) keep the first paragraph in
the body essentially intact — "the constant part is a reporting problem" is load-bearing for the
paper's calibration and is quoted approvingly nowhere else; (b) fold the remaining five into a
single paragraph of one sentence each, in the §6/§8 style of GID and FVD; (c) move the
supporting reasoning to a supplement section named from the body. This is compression of prose,
not withdrawal of scope — the claim boundary is unchanged.

### 7. Show the reproduction table the gating rule promises
§6.1 states that every checkpoint is run through its authors' validation path and dropped if
its published score is not reproduced. Both same-family references publish exactly this kind of
table. Add a small table — checkpoint, published score, reproduced score, tolerance, kept/dropped
— using Beyond Duality's DSEC-Det numbers (RVT 25.1 mAP50 / 12.9 mAP; SAST 24.3/12.1; S5-ViT
22.3/11.4; SMamba 29.0/14.8) as the published column. This converts a promise into evidence and
costs no new experiment beyond runs already scheduled.

### 8. Name the DSEC-Det annotation version in §7.2
Beyond Duality (CVPR 2026) states that DSEC-Det ships **multiple annotation versions**, and uses
the original annotations for ablation and the SFNet version for comparison. `main.tex`'s
forensics (390 118 boxes, 6693 tracks, 60 sequences) does not say which release it read. One
clause fixes it; without it, a reviewer from this exact subfield can dismiss the forensics as
version-ambiguous. Also add the corresponding line to `experiments/e06_dsec_det_label_forensics`.

### 9. Rename sections after the questions they answer
FVD — the closest structural match — uses *"Quantifying the Temporal Sensitivity of FVD"* and
*"Probing the Perceptual Null Space in FVD"*. Rename: §3 "Temporal support" → *"What the two
clocks are"*; §4 "Estimating the effective timestamp" → keep (already a verb); §5 "Scoring" →
*"Re-anchoring, and whether the gain is a clock or a fit"*; §7 "Results" → keep. Cheap, and it
signals a measurement paper rather than a method paper on the contents page.

### 10. Compile under the real CVPR class and settle the page count
`paper/cvpr.sty` is present but never loaded; the draft uses `article` with custom `geometry`,
and its body currently runs nine pages. Until it compiles under the actual class, the length is
unknown and the eventual cut will be forced rather than chosen. Doing this now means changes
1–9 can absorb the overflow deliberately.

### Explicitly **not** recommended
- Do not soften "we claim no downstream accuracy gain from the constant part". Every reference
  either states a gain or states none; this paper states none and says why, which is stronger
  calibration than any of the five achieves. Keep it in the abstract.
- Do not remove `AP^bias`, the `\sigma_c` band, or the cross-fitting. FVD's Table 1 owes its
  force to carrying its own null (FID) beside the treatment; this submission's null design is
  its closest structural claim to that paper.
- Do not add a "future work" paragraph. None of the five has one.
- Do not import the event-vision abstract opening ("Event cameras offer high temporal
  resolution, low latency and high dynamic range…") from EvRT-DETR or Beyond Duality. This
  paper's refusal of it is correct for its type — FVD and Time Blindness both refuse it too.

---

## 한국어 요약

- 외부 기준 논문 5편을 CVF 공개 프로시딩에서 직접 PDF로 받아 읽었다. 저장소 내부 논문은 쓰지 않았다.
  **① 같은 문제군**: *Beyond Duality* (CVPR 2026, RGB-Event 검출, **DSEC-Det가 주 실험대**),
  **② 같은 논문 유형**: *On the Content Bias in Fréchet Video Distance* (CVPR 2024, 기존 지표가
  특정 축에 눈멀었음을 측정으로 논증 — 본 논문과 구조가 가장 가깝다),
  **③ 구조 모범**: *Time Blindness* (CVPR 2026), 보조로 *Generative Image Dynamics*
  (CVPR 2024 Best Paper, 수상 확인됨)와 *EvRT-DETR* (ICCV 2025, Gen1/1Mpx 기준점).
- **체크리스트 214–216행의 `AbstainEQA (CVPR 2026 Highlight)`는 존재하지 않는다.** CVPR 2026
  전체 4042편 목록과 arXiv API 양쪽에서 무결과. 삭제하거나 교체해야 한다. MVBench의 Highlight
  여부는 확인 불가(채택 사실만 확인됨). 나머지 넷(GID, Neuralangelo, Time Blindness, VirtueBench)은 확인됨.
- 가장 큰 괴리 세 가지: (1) **초록과 Table 2·3의 핵심 수치가 전부 `[unmeasured]`** — 기준 논문 중
  초록에 자리표시자를 둔 사례는 없다. (2) **첫 측정 결과가 7쪽에 나온다** — FVD와 Time Blindness는
  8쪽 본문의 **3쪽**에 논지 검증 표를 놓는다. (3) **그림이 1개뿐**이고 Related work가 ~2.4단으로
  가장 긴 기준 논문의 두 배다.
- 반대로 **주장 보정(verb register), 널(null) 설계(`AP^bias`, σ_c 밴드, cross-fitting), 상수항을
  먼저 양보하는 서론 구성은 다섯 편 중 어느 것보다 낫다.** 지금은 표가 비어 있어 보이지 않을 뿐이다.
- 권고안은 주장 축소가 아니라 **재배치**다. 한정(limitation)은 지우지 말고 압축하고, Related work의
  변별 문장은 삭제 대신 해당 절로 옮긴다. 초록에서 빼는 것은 주장이 아니라 아직 존재하지 않는 숫자뿐이다.
- 부수 소득 하나: Beyond Duality가 **DSEC-Det에 주석(annotation) 버전이 여러 개 있음**을 명시하고
  비교 실험에는 SFNet 버전을, 절제 실험에는 원본을 썼다고 밝힌다. E06 라벨 포렌식(390 118 boxes)이
  어느 릴리스를 읽었는지 §7.2에 반드시 적어야 한다. 같은 표에서 DSEC-Det RVT = 25.1 mAP50 / 12.9 mAP를
  재현 목표치로 쓸 수 있다.

---

## CORRECTION (main session, 2026-09-02) — the "fabricated reference" finding is WRONG

This document claimed that `AbstainEQA (CVPR 2026 Highlight)`, listed in
`docs/CHECKLIST_197.md`, does not exist. **That claim is false and is retracted.**

The paper is in the CVPR 2026 proceedings listing:

> **When Robots Should Say ''I Don't Know'': Benchmarking Abstention in Embodied
> Question Answering** — Wu, Tao; Zhou, Chuhao; Zhao, Guangyu; Cao, Haozhi; Pu, Yewen;
> Yang, Jianfei. `@InProceedings{Wu_2026_CVPR}`.

The checklist names it by exactly that title. `AbstainEQA` was a short label, not a
claimed title.

**Cause of the error.** The search string used was `abstain`. The title spells it
`Abstention` — a-b-s-t-e-n-t-i-o-n, which does not contain the substring a-b-s-t-a-i-n.
The zero hit was a spelling artifact, and the main session initially reproduced the same
mistake with the same string before grepping `embodied question` instead, which found it.

Everything else in this document stands, but the lesson applies to it: a claim of
non-existence based on one keyword is not evidence of non-existence.
