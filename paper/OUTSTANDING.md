# Outstanding, as of 2026-09-09, after external reviews #6, #7 and #8

## State

`main.pdf` — body ends inside page 8, references run to page 10. `supplement.pdf` — 4 pages.
Both: 0 TeX errors, 0 undefined control sequences, 0 overfull boxes, 0 undefined references,
0 undefined citations. Figures: 3 (exposure survey, predictor, one real exposure window).
Tables: 2 (output-time ladder, six ceiling sequences).

Every measured value in prose is a macro from `numbers.tex` whose comment names the
experiment that produced it, and `src/audit_numbers.py` re-derives 109 of those macros from
their artifacts and fails if any disagrees. That checker is itself tested twice over: each
entry is mutated in turn and must be rejected, and a macro it knows how to derive whose
artifact has gone is reported as an orphan rather than silently dropped, which is the failure
mode that let eleven withdrawn numbers stand in the manuscript for an hour.

## What changed since the last note

- **E45 corrected the paper's most-quoted number.** E17 and E34 handed the occluded forward
  pass the recurrent state their reference pass *returned* rather than the state entering the
  step. The newest-window influence centroid is **-23.81 ms**, not -24.94 ms, and it now
  agrees with E44's independently written measurement. Every downstream value was recomputed
  (`src/e46_recompute.py`) and the mAP cost was re-evaluated at the exact centroid rather than
  interpolated between grid points (`src/e46b_map_at_centroid.py`). Recorded as case 9 in
  `docs/PROTOCOL_LEDGER.md`.
- **"The profile is close to flat" was withdrawn.** The corrected coefficient of variation is
  0.131, four times what E17 reported, and the heaviest bin carries 1.52x the lightest. The
  centroid still sits within a quarter of a bin of the uniform value, for a different reason:
  the five older bins hold 48.6 % of the influence against 51.4 % for the five newer. The
  paper states the balance rather than flatness.
- **E44 entered the paper.** Three released capacities, and the support behind the newest
  window lengthening with capacity (share of a 1 s horizon 22.7 % to 19.0 %, support centroid
  -299 to -339 ms). Its centroids have since been superseded by E48's, which are measured on
  the frames the architecture comparison uses; the support columns are still E44's.
- **The introduction's three-bullet contribution list became one connected passage**, which
  is what review #5's first must-fix asked for and also bought the space E44 needed.
- **Audit fixes.** A stray brace in `numbers.tex` was producing a real `! Too many }'s` that
  the earlier build check never looked for; the figure's mAP panel still carried the
  withdrawn term "evidence centroid"; a cross-reference to the harmonic sweep pointed at
  Sec. 4.1 instead of Sec. 4.2; four LLM-style constructions (items 188-190) were removed.
- **The video is 69.2 s**, with a new generalization scene (`v03_generality`) that draws the
  five measured profiles and their five measured centroids on one axis rather than asserting
  generality on a card. The rest was rebuilt at its original lengths.

## Added overnight: a second architecture

- **E47/E48.** SSM-ViT (Zubic et al., CVPR 2024) is a fork of the RVT repository in which
  each stage's ConvLSTM is replaced by an S5 state space layer; it distributes RVT's own
  preprocessed Gen1 and inherits its window construction, and its two released capacities are
  9.68 M and 18.19 M against RVT's 9.87 M and 18.54 M. Both load with 0 missing and
  0 unexpected keys. Run through E45's instrument on the same frames, the five released
  checkpoints put the newest window's centroid between **−23.76 and −24.72 ms**, none further
  than 1.24 ms from the uniform-weight value. E48 re-runs RVT's three on the SSM's frames so
  the families are compared on identical samples, and its `rvt-t` reproduces E45 to three
  decimals. Sec. 3.3, Fig. 2a and the limitations now say two architectures, not one.
- **E47c, a finding that came out of that port.** The state SSM-ViT carries between
  evaluation chunks reaches no output: zeroing it changes the emitted detection tensor by
  0.00000 at every position, against 0.0616 to 0.0304 for `rvt-t`, while occluding the window
  one position earlier inside the chunk changes it by 0.0276 to 0.0106, so the model is
  recurrent within a chunk and only across chunks is the state lost. Its released streaming
  evaluation steps in non-overlapping chunks of 21 windows, so a released detection's support
  runs from one window at the first position of a chunk to 21 at the last. Reported in the
  supplement as a property of the release. Case 10 in `docs/PROTOCOL_LEDGER.md`.
- The first S5 runs, which drove the model one window at a time, are withdrawn:
  `experiments/e47_ssm/withdrawn_L1/WHY.md`.

## External review #6 (Accept, lower edge of the accepted band)

Technical Soundness Pass, 0 Critical, no acceptance-critical experiment. Its three Must-Fixes
were text-only and are applied; see `docs/REVIEW6_RESPONSE.md`. In short: the 3.65-SE headline
now carries the specification range and the sign convention wherever it appears, the abstract
states outright that no per-object DSEC label time is inferred, and the nearest label-side
prior (Liu et al., CVPR 2024) is cited with the distinction stated.

The two objections the review calls Major but not rejection-level are the ones to keep in
view: the exact 26.2 ms magnitude is specification-dependent, and the DSEC displacement is
small in pixels. Both are stated in the paper rather than argued away.

## External review #7 (Borderline) and what was run for it

#6 and #7 read the same manuscript and differ only on significance. #7's gating issue was
that the interval is never shown to change a benchmark conclusion, and its experiment was
run: five released checkpoints scored under one protocol at the label instant and at each
model's preferred displacement, in four speed strata. **The ordering does not change and
cannot** — the largest alignment gain within a stratum is 52 % of the smallest adjacent gap.
The negative result is in the paper as a bound, not hidden and not dressed up; see
`docs/REVIEW7_RESPONSE.md` and `experiments/e51_ranking/README.md`.

Note that #7's Must-Fix and much of its body describe a different paper (DEIMv2 /
encoder-position allocation). Its verdict and gating issue are still answerable here and were
answered; the Must-Fix is not applicable.

## External review #8 (Accept)

Accept on the current PDF and supplement, Evidence **Strong**, no gating issue and no
acceptance-critical experiment. Its single Must-Fix — the abstract and introduction stated the
output-time null as an equality — is applied; see `docs/REVIEW8_RESPONSE.md`. Its one
recommended experiment, an audit on a detector independent of this repository lineage, is
classified by the review as broadening rather than required, and is the leading item below.

## Known and accepted

- Two architectures, but they share a repository, a representation and a dataset. A detector
  built independently of RVT is the next generality step and is not run.
- The SSM rows carry 288 samples against RVT's 480, because only chunk positions holding at
  least half a chunk of history are used. The sample sets are the same sequences.
- The support comparison (share of a horizon, support centroid) is RVT-only. It is not
  defined the same way for a model whose carried state is inert, and no attempt is made to
  force one.
- The predictor half is Gen1 and the label half is DSEC. The thesis that binds them is
  stated, but they are not the same system.
- The full recurrent centroid is not identified from the measured horizons. Two finite
  horizons cannot separate a slowly converging tail from a divergent one, so the divergence
  the observed a<1 tail would imply is stated conditionally, never asserted. This is
  reported rather than resolved; a longer horizon moves the number rather than converging it.
- The zero-fill and mean-fill instruments disagree by 2.5 ms and the gradient by 4.0 ms. The
  spread is reported as the instrument dependence it is, not averaged away.
- Unused macros in `numbers.tex` are the record of measurements that did not reach the text,
  including retracted ones, and are left deliberately.

## Retracted, with the reason

E12 and E18 (integer-period cancellation is false for the first moment), E20 (the spatial
gradient is ego-motion, E26), E21/E23/E24 (the estimator was wrong in four ways, E27), the
per-box `p<1e-3` locked fractions (the analytic null is inflated 55x at the box level, E38),
and **E17/E34** (the recurrent state, E45). None is reachable from the text.
