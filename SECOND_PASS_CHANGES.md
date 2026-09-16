# Second-pass wording-only changes

No experiments, data, numerical results, equations, or model settings were changed.

FILE: `paper/main.tex:108-122`

BEFORE: A single long sentence combined the two predictor measurements with the DSEC case study.

AFTER: The paragraph now states the two predictor-side quantities in separate sentences and presents DSEC as a complementary label-side case study.

REASON: Reduce information-order load and keep the predictor and label analyses separate.

FILE: `paper/main.tex:127-133`

BEFORE: The mAP consequence and speed-scale comparison were joined by a long contrastive sentence.

AFTER: The mAP observation and the speed-scale observation are stated in separate sentences.

REASON: Improve native academic sentence rhythm without changing the claim.

FILE: `paper/main.tex:250-252`

BEFORE: Section 3.4 measures the effective timestamp.

AFTER: Section 3.4 estimates the regression coefficient `tau=-tau_P`, from which the effective timestamp follows.

REASON: Align the prose with the signed convention and distinguish the coefficient from the timestamp.

FILE: `paper/main.tex:481-485`

BEFORE: A rhetorical sentence stated that the controls did not absorb a lag and that the axis pairing supplied the answer.

AFTER: The direct regressor perturbation recovery, geometric-control result, and specification span are stated as observations.

REASON: Remove presentation-style explanation and avoid implying physical-lag recovery from a direct regressor perturbation.

FILE: `paper/main.tex:702-707`

BEFORE: The pixel-to-box null result used a colon and a long causal chain.

AFTER: The null limitation and the absence of a per-box p-value are stated directly in separate sentences.

REASON: Improve precision and sentence boundaries.

FILE: `paper/main.tex:438-443`

BEFORE: The regression estimate was described as applying to matched detections without explicitly naming conditioning.

AFTER: The estimate is conditional on detections matched at the nominal label time.

REASON: Scope the estimate to the actual analysis sample.

FILE: `paper/supplement.tex:148-150`

BEFORE: The measured ablation centroid used the generic signed-weight symbol `a_k`.

AFTER: The centroid uses non-negative sensitivity weights `s_k`.

REASON: Keep empirical ablation sensitivity separate from the theoretical signed effective weights.

FILE: `paper/supplement.tex:461-462`

BEFORE: The prior-art search record described API calls, coverage counts, and retrieval history.

AFTER: The coverage statement is restricted to the citation-graph and keyword searches described above.

REASON: Remove research-log and rebuttal-style metadata from the submission.

FILE: `paper/main.tex:547-550`

BEFORE: `the measured center displacement is not register it.`

AFTER: `On this velocity-evaluable subset, the benchmark metric does not register the measured center displacement.`

REASON: Correct the grammatical error and state the measured scope directly.

FILE: `paper/main.tex:509-512`

BEFORE: `a measured offset near zero reports the objective.`

AFTER: `a measured offset near zero is consistent with the training objective indexed at the label time.`

REASON: Avoid implying that the estimate demonstrates exact temporal coincidence.

FILE: `paper/main.tex:715-719`

BEFORE: `That signature bounds any within-box temporal statistic inside one published exposure window.`

AFTER: `That signature limits the attribution of within-exposure event timing to object timing. We therefore quantify the dispersion of each box's event-time centroid within its published exposure window.`

REASON: Match the claim to the event-time centroid/dispersion measurement actually reported.

FILE: `paper/supplement.tex:384-385;526-533`

BEFORE: `Which archive, and how tracks are associated`; `The withdrawn spatial statistic`; `the wrong sign for an object-borne effect`.

AFTER: `Archive version and track association`; `Spatial-control analysis`; `which yields the opposite sign from that expected for an object-borne effect`.

REASON: Remove rebuttal-style wording while preserving the control result.

FILE: `paper/main.tex:48-50,176-181,807-811`

BEFORE: The DSEC abstract claim omitted the uniqueness condition, and the Related Work section did not cite the direct AP-delay precedent.

AFTER: The abstract now requires separating illumination structure, and Mao et al.'s Average Delay work is cited with an explicit distinction from the present timestamp-support analysis.

REASON: Align the label-side claim with the evidence and close the nearest-prior novelty gap.
