# CVPR 2027 submission package

Title: *Temporal-Support Identifiability in Event-Detection Benchmarks*.
Rebuilt 2026-09-16 from `paper/` after the third checklist pass. Every file here is
current.  The build artifacts `.aux`, `.log`, `.out`, `.blg`, `.brf`, `.fls`, `.fdb_latexmk`
are present in this working directory but are not tracked and are not part of the upload.
`main.bbl` and the two `.buildlog` files are tracked deliberately, the first so `main.tex`
compiles without a `bibtex` step and the logs as the build record.  `supp.bbl` is also
tracked and is zero bytes: `supp.tex` has no bibliography, so the file is a remnant that
the build neither writes nor reads.

## Upload these

| File | Pages / size | Notes |
|---|---|---|
| `main.pdf` | 9 (body 8, references on 9) | anonymous, `\usepackage[review]{cvpr}`, `\author{Anonymous CVPR submission}` |
| `supp.pdf` | 18 | supplementary material, including the predictor-side and label-side audits (Secs. 5 and 14) that main Sec. 5 summarizes and the fixed-history scoring of Sec. 1.4 that main Sec. 6 summarizes |
| `video/main.mp4` | 87.9 s, 1280x720, 30 fps, 9,466,456 bytes | research video, nine scenes |

## Sources (for the camera-ready and for the record)

`main.tex`, `supp.tex`, `numbers.tex`, `cvpr.sty`, `figs/` (10 PDFs read by the two
documents: `chunkpos`, `chunkpos_full`, `fig1_dsec_exposure`, `fig3_day_night`,
`fig5_qualitative`, `fig6_sweep_real`, `fig7_ceiling_vs_day`, `fig_predictor`,
`paired_frame`, `e71_hcurve`).  `figs/fig2_evidence_time.pdf` is also present and is read by neither.

These compile standalone from this directory with no other input:

```
pdflatex main && bibtex main && pdflatex main && pdflatex main
pdflatex supp && pdflatex supp && pdflatex supp
```

Verified in `cvpr19-tex:cvpr2026-v1` from a clean copy of this directory, and re-verified
2026-10-01 in `texlive/texlive:latest`:
`main 9 pages, supp 18 pages, undef=0, overfull=0, 0 missing-figure placeholders` (rebuilt 2026-10-04 after adding the H = 40, 80 columns on 3,000 frames and the reset-policy audit).
Both documents built from a clean copy reproduce the shipped PDFs' `pdftotext` output
exactly, and `main.pdf` passes the reference-page check (references start on page 9 with
no body text on it).  `main` needs no `bibtex` run when `main.bbl` is present.
(`\figasset` substitutes a visible box for a missing figure rather than failing, so the
placeholder count is checked explicitly, not assumed.)

The bibliography is an inline `thebibliography` environment in `main.tex`; there is no
`.bib` file, and the `bibtex` step above is a no-op kept for the camera-ready workflow.
`supp.tex` carries its own inline `thebibliography` of the five entries that Secs. 15 and 16
cite, so it needs no `bibtex` step either.  It does
need three `pdflatex` passes: at two, one table has not yet reached its final page and the
text stream differs from the shipped `supp.pdf`.  This was checked by building a clean copy
at two and at three passes and comparing `pdftotext` output against the shipped file.
37 entries, 37 cited, 0 undefined, 0 orphaned, 0 duplicated.

## Verification records

- `CHECKLIST_VERDICT_0916.md` — graded against the 197-item checklist and five externally
  fetched reference papers (CVPR 2024-2026) plus the official CVPR 2026 reviewer
  guidelines. Three independent passes. **Verdict: Accept.** G1-G12 all pass.
- `VERIFY_3ROUND_E58.md` — three independent verifications of the headline chunk-position
  result (mechanism from released source, mutation-tested numbers, permutation null at
  9.84 sigma / 7.61 sigma with all placebos inside). The 209/209 macro count quoted there
  is the count at the time of that round; the current manuscript carries 623.
- `AI_WRITING_AUDIT.md` — first-pass writing audit. GPTZero status is `not_run`: the
  `GPTZERO_API_KEY` environment variable is not configured on this machine, so no
  detector score is reported and none is inferred. The local heuristic pass returns
  0 REWRITE passages, so the second-pass edit protocol was not triggered. Raw response
  file: `.ai-audit/gptzero_raw.json` in the repository.
- `video_README.md` — scene list, screen times, and the defect log for the video.

All 623 manuscript numbers re-derive from their artifacts:
`python3 src/audit_numbers.py` (623 checked, 0 disagree, 623/623 reject a corrupted
value, blind: none).

## Video

The cut carries the paper's headline evidence. Nine scenes, in screen order:

| # | Scene | s | Content |
|---|---|---|---|
| 1 | `s0` | 2.2 | title card |
| 2 | `s1` | 17.0 | predictor-side temporal support, ablation-sensitivity centroid |
| 3 | `s2` | 12.5 | the mAP consequence on one real frame |
| 4 | `s6` | 10.4 | the headline: mAP against chunk position, 5.32 points after an RVT control |
| 5 | `s3` | 11.4 | events inside one published DSEC exposure |
| 6 | `s2b` | 18.0 | ceiling exposure against the daytime control |
| 7 | `s4` | 7.0 | the harmonic identification |
| 8 | `s1b` | 6.0 | five released checkpoints, one instrument |
| 9 | `s5` | 3.6 | closing statement |

Actual measured footage and measured plots occupy 46.2 s under the strict reading
(52.6 %) and 66.2 s under the checklist's own scene list (75.3 %). All on-screen text is
set in Nimbus Roman, the metric-compatible Times clone.

## Not in this package

Source clips in `video/`, experiment artifacts in `experiments/`, analysis code in `src/`.
The one open experiment — replicating the chunk-position result on a detector lineage
outside RVT/SSM-ViT — is scoped in `paper/OUTSTANDING.md`. It is the named distance
between the current Accept and a Strong Accept; it needs GPU time and is deferred under
the manuscript freeze.
