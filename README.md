# The Temporal Support Behind One Benchmark Timestamp

*A Released Event Detector and DSEC's Ceiling Exposures* — CVPR 2027 submission.

A detection benchmark compares a prediction with a label at one query time and scores their
difference as displacement. That timestamp does not uniquely specify the temporal support of
either side of the comparison. This work separates three quantities that are collapsed into
it and measures what released artifacts identify of each: a predictor's evidence support, its
effective output time, and the exposure-conditioned support of the labels.

Everything here is measured from released artifacts — the RVT and SSM-ViT Gen1 checkpoints,
the preprocessed Gen1 archive they distribute, and DSEC's published per-frame exposure
metadata. No model is trained.

## Layout

| path | what it holds |
|---|---|
| `paper/` | `main.tex`, `supplement.tex`, and `numbers.tex`, in which every measured value is a macro whose comment names the experiment that produced it |
| `experiments/` | one directory per experiment: its artifacts, its run log, and a README where the result needed explaining |
| `src/` | the measurement scripts, `e<N>_*.py`, and the figure and video renderers |
| `docs/` | the review responses, the audits, and `PROTOCOL_LEDGER.md` |
| `video/` | the research video, its clips, and the standard it was built and audited against |

## The two things worth reading first

**`docs/PROTOCOL_LEDGER.md`** records every defect found in this work's own measurements and
how each was caught — twelve cases, including three in which a checker reported a pass while
printing the failure. The numbers that survived are the ones that survived those.

**`src/audit_numbers.py`** re-derives 118 of the manuscript's macros from the artifacts they
came from and fails if any disagrees. It is itself mutation-tested, and it fails on a macro it
knows how to derive whose artifact has gone, because silently dropping such a macro is the
failure mode that once let eleven withdrawn numbers stand.

```
python3 src/audit_numbers.py     # 118 macros checked, 0 disagree
```

## Reproducing

The dataset and checkpoints are not in this repository. `experiments/e47_ssm/PROVENANCE.md`
records where the SSM-ViT code and checkpoints came from with their checksums; the RVT
checkpoints and the preprocessed Gen1 archive come from the RVT release. Every GPU experiment
runs in the `cvpr19-gpu-g1:torch2.7.1-cu128` image through the `run_e*.sh` wrappers, which
wait for a card and for host memory before starting, because the machine is shared.

The vendored upstream sources under `src/RVT/` and `src/SSMViT/` are excluded from this
repository; they are third-party code that is read and driven, not modified.
