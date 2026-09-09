# E04 — Is the RVT stack actually a blocker on sm_120? (2026-09-01, main session)

Reviewer 4 named this the fatal flaw of the leading idea: RVT pins `torch 2.0.0 / cu118`,
cu118 emits no `sm_120` kernels, therefore nothing runs on the RTX 5090 until the stack is
ported, and the plan budgets zero days for that port. The premise is true. The conclusion
is weaker than it looks, for two reasons measured here.

## 1. RVT contains no custom CUDA or C++ source

Pulled the full repository tree from the GitHub API (`uzh-rpg/RVT`, master, recursive):

    total files: 184
    files ending .cu / .cpp / .cuh: NONE
    setup.py: 404 (there is none)
    detectron2 / mmdet vendored code: none

So there is nothing to compile against a CUDA toolkit, and no kernel that has to be
rebuilt for `sm_120`. The `cu118` pin is a dependency pin, not a compilation requirement.
Porting is a version exercise. That is real work, but it is a different and much smaller
kind of work than "port a CUDA extension".

## 2. `requirements.txt` is pure Python and does not pin torch

    h5py==3.8.0            hydra-core==1.3.2     pytorch-lightning==1.8.6
    hdf5plugin==4.4.0      einops==0.6.0         wandb==0.14.0
    numba                  pandas==1.5.3         opencv-python==4.6.0.66
    tqdm                   plotly==5.13.1        tabulate==0.9.0
    pycocotools==2.0.6     bbox-visualizer==0.1.0  StrEnum==0.4.10

Torch itself is pinned in `environment.yaml`, which fetched empty over raw.githubusercontent
and was not read. The binding constraint in this list is `pytorch-lightning==1.8.6`, which
is old enough to be a genuine compatibility problem against torch 2.7.

## 3. Why that matters less for an inference-only plan

The leading idea trains nothing; it re-scores released checkpoints. Lightning's role in
this repository is the training loop. The model itself is ordinary PyTorch —
`models/detection/recurrent_backbone/maxvit_rnn.py` and a vendored YOLOX head — so a
checkpoint's `state_dict` can be loaded into the model definition directly and run forward
without instantiating a Lightning trainer at all.

**Revised risk.** Not "zero days budgeted for a port that gates every number", but
"one to three days to load released weights into the model definition under torch 2.7.1,
bypassing Lightning". That should be scheduled explicitly, and it should be done in week 1,
because if the released `state_dict` does not load cleanly the whole plan changes shape.

## What is still unverified

- `environment.yaml` was not read (empty response); the exact torch pin is unconfirmed.
- No checkpoint has been downloaded or loaded. Until a released RVT checkpoint is actually
  restored into the model under torch 2.7.1 on this machine, the paragraph above is a
  reasoned expectation, not a result. **This is the single cheapest experiment that would
  de-risk the leading idea, and it should be run before the idea is committed to.**

---

# RESOLVED — the port is not a blocker (measured 2026-09-01, same day)

The open item above was run. Result: **the released RVT checkpoint loads into a model built
under `torch 2.7.1+cu128` with zero missing and zero unexpected keys, and runs forward.**

    CFG: embed_dim 32  in_ch 20  in_res [256, 320]  partition [4, 5]
    MODEL BUILT params=4.41M
    MISSING: 0 []
    UNEXPECTED: 0 []
    FORWARD OK, returned 3 items: ['Tensor', 'NoneType', 'list']

## What was actually done

1. `git clone --depth 1 https://github.com/uzh-rpg/RVT` into `src/RVT`.
2. Downloaded `checkpoints/gen1/rvt-t.ckpt` (51 MB) from `download.ifi.uzh.ch`.
3. Inspected the checkpoint: 376 tensors, all under the `mdl.` prefix,
   `pytorch-lightning_version: 1.8.6`, no `hyper_parameters` entry.
4. Rebuilt the model config by hand from the repo's own files rather than through Hydra:
   `config/model/base.yaml` + `rnndet.yaml` + `maxvit_yolox/default.yaml`, then the two
   `experiment/gen1/tiny.yaml` overrides (`embed_dim: 32`, `fpn.depth: 0.33`).
5. Reproduced what `config/modifier.py` computes at runtime, which is the step that is easy
   to miss: for gen1 the dataloading size (240, 304) is rounded up to a multiple of
   `32 * partition_split_32 = 64`, giving `in_res_hw = (256, 320)`, and
   `partition_size = (256//64, 320//64) = (4, 5)`. `head.num_classes = 2` for gen1.
6. Instantiated `YoloXDetector`, stripped the `mdl.` prefix from the state dict, loaded it,
   and ran a forward pass on a zero input of shape `(1, 20, 256, 320)`.

Dependencies needed inside the container: `omegaconf`, `hydra-core`, `einops`, `StrEnum`.
`pytorch-lightning` was **never installed** and was not needed. The one non-obvious failure
along the way was `StrEnum`, which the repo imports but which is only in the stdlib from
Python 3.11; the container has 3.10, so the pypi backport is required.

## Consequence for the review record

Reviewer 4 named "zero days budgeted for the sm_120 port that gates every number" as the
fatal flaw of the leading idea. That flaw is now closed: the port cost was one working
session, not days, because there is no CUDA extension to rebuild and the inference path
does not need Lightning. Reviewer 4's ranking should be read with that correction applied.

Still not established: that the loaded model **reproduces the published mAP**. Weights
loading cleanly is necessary, not sufficient — the data pipeline (`gen1.tar`, 98.6 GB) has
not been downloaded and no evaluation has been run. That is the next check, and it is the
one that would actually validate the re-scoring plan.
