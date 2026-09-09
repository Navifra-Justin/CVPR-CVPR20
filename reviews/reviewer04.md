# Reviewer 4 — feasibility, schedule, and dependency audit

**Specialism:** can this be built, on this machine, before the CVPR 2027 deadline.
**Date of review:** 2026-09-01. **Deadline assumed:** ~2026-11-15. **Working time: ~10 weeks.**
**Machine:** one shared RTX 5090 (GPU 1), ~9 GB free and not guaranteed, Docker only, 990 GB disk.

Every link status, file size and bandwidth number in this review was measured by me on
2026-09-01 with `curl` from the target machine. I did not take any team's word for any of it,
and where a team's claim was wrong I say so by name.

I rank the ten ideas by **probability of producing a submittable CVPR paper by November 2026**,
and by nothing else. I state that explicitly because two of the ideas I rank low are, on the
evidence in front of me, the most intellectually interesting of the ten.

---

## Comparison set

Seven main-conference accepted papers, verified against CVF Open Access / ECVA, with the
compute they actually report. Quotes are verbatim from the published PDFs.

| # | Paper | Venue | Reported compute |
|---|---|---|---|
| 1 | **Recurrent Vision Transformers for Object Detection with Event Cameras** (RVT), Gehrig & Scaramuzza | CVPR 2023 | *"we train our models with a batch size of 8, sequence length of 21 … The training takes approximately **2 days on a single A100 GPU**"* (Gen1). 1 Mpx: *"batch size of 24, sequence length of 5 … approximately **3 days on two A100 GPUs**."* Inference timed on a T4. |
| 2 | **State Space Models for Event Cameras** (S5-ViT), Zubić et al. | **CVPR 2024** | *"We conduct training on the GEN1 dataset using **A100 GPU**, employing a batch size of 8 and a sequence length of 21."* 1 Mpx: *"batch size of 12 … across **two A100 GPUs**."* |
| 3 | **LEOD: Label-Efficient Object Detection for Event Cameras** | **CVPR 2024** | *"we can train our model on **2 NVIDIA A40 GPUs**. The pre-training stage takes **60 hours**, while self-training takes around **40 hours**."* And, tellingly: *"We use RVT-S in most of the experiments **due to limited computation resources**."* |
| 4 | **Efficient Meshflow and Optical Flow Estimation from Event Cameras** | **CVPR 2024** | *"We conduct experiments using the PyTorch framework on **two NVIDIA 2080Ti GPUs**."* — the only paper in the set trained on 11 GB-class cards. |
| 5 | **Latency Correction for Event-guided Deblurring and Frame Interpolation**, Yang et al. | **CVPR 2024** | *"runs on an **NVIDIA GeForce RTX 3090 GPU**"*, *"The **batch size is set as 1**."* The smallest footprint in the set. |
| 6 | **Efficient Event-Based Object Detection: A Hybrid Neural Network with Spatial and Temporal Attention** | **CVPR 2025** | Gen1: *"a batch size of 24 … requiring approximately **8 hours on four 3090 GPUs**."* Gen4: *"**1.5 days on four 3090 GPUs**."* An explicitly *efficiency-branded* detector that still needed 4×24 GB. |
| 7 | **EDCFlow** (event optical flow) | **CVPR 2025** | *"AdamW … for 100 and 10 epochs … with a **batch size of 3** … randomly cropped to **288×384**"*; runtime on an RTX 4090. Their Table 1 carries a baseline row reading verbatim **"E-RAFT-4 — GPU out of memory (>40 GB)"**. |

*(Also verified and available if needed: BlinkTrack, ICCV 2025 — "two NVIDIA RTX3090 **24GB** GPUs for 48 hours"; RELED, ECCV 2024 — "batch size of 8 with **four RTX 3090 GPUs**"; EVDM, ICCV 2025 — "**4 NVIDIA 3090 GPUs**", 128×128 crops; ClearSight, ICCV 2025 and MoE Heat Conduction, CVPR 2025 — each a **single** RTX 4090.)*

**What the comparison set tells me, and it is the frame for the whole review.**

1. The de-facto floor in this literature is **one 24 GB consumer card**; the mode is one to four
   of them. Papers 5, 6(inference), and the two ICCV 2025 single-4090 papers prove a single
   consumer card is publishable. **9 GB is below every paper in the set except #4.**
2. **Nobody reports VRAM as a number.** Only three papers in ~19 I checked touch it at all. So
   there is no published bar to clear — but also no published evidence that anyone has trained a
   Gen1/1 Mpx recurrent detector under 24 GB, and the BPTT memory of RVT-family models at
   sequence length 21 is exactly what does not fit.
3. The regimes that demonstrably fit small cards are **event deblurring** (128²–256² crops,
   batch 1–8) and **event optical flow** (288×384, batch 3, 2.5 M params). Both are reachable at
   9 GB. **Recurrent detection training is not**, and no idea in this round should plan to train one.
4. Every idea in this round that is *inference-only on released checkpoints* is therefore
   competing in the only weight class this machine can enter. That is the single largest
   discriminator in my ranking, and it is why the metric/diagnosis ideas outrank the method ideas.

---

## Per-idea verdicts

| Team | Verdict | One-sentence reason |
|---|---|---|
| **08** — Right Place, Wrong Time (metric decomposition) | **STRONG ACCEPT** | Trains nothing, and I verified every checkpoint, tarball and label file it needs is live today with measured sizes; its first figure is a 4.7 MB label file and zero GPU. |
| **06** — Frames Are Not Samples (exposure gap / LME) | **STRONG ACCEPT** | Its headline numbers already exist (computed on CPU), its data is GoPro 19.6 GB + DSEC + REBlur 0.7 GB all verified live, and it is the only team that independently discovered BS-ERGB is dead and routed around it. |
| **05** — No Offset Can Fix a Width | **ACCEPT** | The load-bearing claim is a CPU FFT experiment with no training and no download; the only real dataset on its critical path is DSEC, which is live. |
| **04** — When Is Your Prediction? | **ACCEPT** | Best-de-risked pilot of the ten (3 days, ~3 GPU-h, zero downloads, no v2e), but three of its four named real-data loop-closers are dead or unreachable and the plan must be re-founded on EVIMO2 + DSEC in week 1. |
| **10** — Fusion Is Ill-Typed | **BORDERLINE** | Six repos means six Docker images and two Baidu/Google-Drive weight sources; its FRN fine-tune at 640×480 is budgeted at 8.5 GB, above the safe band on a GPU whose free memory can shrink. |
| **03** — Temporal Support Fields | **BORDERLINE** | Cheap phenomenon plot, but the entire "real" tier is BS-ERGB (dead), NTIRE/HighREV (login-gated) and five baseline repos including two CVPR 2026 methods whose code I could not locate. |
| **02** — Exposure-Occupancy Measures | **BORDERLINE** | Its primary real validation is FE108/FE240hz, whose application portal returns a zero-byte 416 today; the fallback (EVIMO2) is live and must become the plan, not the fallback. |
| **01** — Latent Exposure Support | **BORDERLINE** | Fig 1a is already done, but the money plot (Fig 1b) requires FE240hz, and FE240hz, PKU-DAVIS-SOD and BS-ERGB — its three real-data sources — are respectively dead-portal, unreachable and dead. |
| **07** — Chronofields | **BORDERLINE** | Its own falsification experiment needs Time Lens + RVT both running on sm_120, its real-event tier is HS-ERGB/BS-ERGB (dead), and the team admits the six-dataset plan "must be cut to two before anyone starts" — it has not been. |
| **09** — Change-Time | **REJECT** | Both pre-registered make-or-break experiments depend on artefacts I could not obtain: P3 needs ASTW (CVPR 2026, no locatable public code) and P6's real arm needs BS-ERGB/HS-ERGB (dead) — fatal to *this execution*, not to the idea. |

---

## Detailed review

Rubric items: (1) verdict, (2) 3-sentence summary, (3) strongest accept reason, (4) strongest
reject reason, (5) factual errors, (6) overclaims, (7) the hostile experiment, (8) ranked fixes.

### Team 08 — *Right Place, Wrong Time* — STRONG ACCEPT

**Summary.** It refuses to propose a method: it defines a per-object decomposition of a published
detector's localisation error into a component perpendicular to the object's motion (pixels) and a
component along it (converted to milliseconds by dividing by ground-truth image speed), then
re-scores released checkpoints under `AP`, `AP^sync`, `AP^⟂` and an isotropic control `AP^iso`,
with the relaxation budget `τ_max = (w_G+w_P)/2` read off the benchmark's and the method's own
published specifications rather than tuned. Its cheapest and most damaging experiment (E0) is
label forensics: measure how far each flagship "high-rate" ground truth deviates from the linear
interpolation that produced it, using only a 4.7 MB label file. It pre-registers `τ̂ ∈ [−35,−10] ms`
for RVT from the architecture's declared 50 ms window *before* measuring it — which our own E02
independently confirms is the right prediction to make.

**(3) Strongest reason to accept.** It is the only proposal in the round whose entire critical path
I could verify byte-for-byte in one afternoon, and whose peak VRAM requirement is an *evaluation*
batch. Measured today: `gen1.tar` 98.6 GB and `gen4.tar` 190.4 GB both HTTP 200 at
`download.ifi.uzh.ch/rpg/RVT/datasets/preprocessed/` — **no Prophesee registration needed for the
preprocessed form**, which is a genuinely important and correct observation the team made and I
confirmed; `rvt-b.ckpt` (gen1) 222,937,503 B; `gen1_base.ckpt` (S5-ViT) 218,814,784 B;
`dsec-det.zip` 87.9 GB; `dsec-det_left_object_detections.zip` 4.7 MB; bflow `E_LU4_BD2.ckpt`
129 MB and `E_I_LU4_BD2.ckpt` 161 MB; `dagr_s_50.pth` 333 MB. Its central asset — the BFlow
event-only vs. event+image checkpoint pair, same authors, same architecture, same recipe, one
variable — is a controlled experiment that already exists on a server and costs ~2 GPU-hours.

**(4) Strongest reason to reject.** The toolchain, and the team does not mention it once.
`uzh-rpg/RVT` pins `torch==2.0.0`, `torchvision==0.15.0`, `torchdata==0.6.0` against
`--index-url https://download.pytorch.org/whl/cu118`, plus `pytorch-lightning==1.8.6`. **cu118
does not emit sm_120 kernels**, so this stack cannot execute on a 5090 at all, and PL 1.8.6 will
not import against torch 2.7. `ssms_event_cameras` vendors RVT wholesale (last pushed
2024-09-28), so it inherits the identical problem. Every number in E1 and E2 sits behind a port
of a 2023 Lightning stack to torch 2.7.1+cu128. RVT ships no custom CUDA extension, so the port
is bounded — but budget it at 4–6 days, not zero, and note that a failed port means CPU inference,
which is fine for the 4.7 MB E0 and not fine for a Gen1 validation pass.

**(5) Factual errors.** (a) *"`bflow/DSEC/train.tar` 149.6 GB"* — correct (139.3 GiB). (b) The
MultiFlow fallback in E4 is not viable as written: `multiflow/val.tar` is 325 GB and
`multiflow/train.tar` is **1.63 TB**, which exceeds both the 300 GB data budget and, for the train
split, the 990 GB free disk. Delete the MultiFlow fallback or restrict it to `val.tar` and say so.
(c) The claim that DAGr "ships `run_test_interframe.py`, which already writes inter-frame
detections to disk" is plausible but its install is understated: `install_env.sh` needs
`torch-scatter`, `torch-cluster`, `torch-sparse`, `torch-spline-conv` from `data.pyg.org`, and
`download_and_install_dependencies.sh` clones detectron2 and YOLOX over **`git@github.com:` SSH
URLs**, which fail without a deploy key. Good news I verified: prebuilt PyG wheels *do* exist for
`torch-2.7.1+cu128` (`torch_scatter 2.1.2`, `torch_cluster 1.6.3`, `torch_sparse 0.6.18`,
`torch_spline_conv`), so nothing has to be compiled; rewrite the SSH URLs to HTTPS.

**(6) Overclaims.** *"Total: ≈ 32–40 GPU-hours … The critical path is download bandwidth, not
compute."* Both halves are wrong in the same direction. I measured 4.56 MB/s sustained from
`download.ifi.uzh.ch`, so gen1.tar is 6.0 h, gen4.tar 11.6 h, dsec-det.zip 5.4 h, bflow DSEC train
9.1 h — **~1.5 days of downloading, not a critical path at all.** The critical path is the
sm_120 port, which is unbudgeted. Also *"Reproduce each checkpoint's published headline mAP to
within ±0.3"* is the right standard and it is the thing most likely to fail after a toolchain
port; the reproduction table must be produced before anything else is written.

**(7) The hostile experiment.** *"Show me that `τ̂` is a property of the method and not of the
labels."* The team has already designed the answer (C3 architecture prediction + variance
decomposition across dataset × method), and our E02 gives it a free head start. Its absence would
be fatal; its presence is the paper.

**(8) Ranked fixes.** 1. Build and validate the sm_120 Docker image for RVT/S5-ViT in week 1, with
a documented CPU fallback, before promising E1/E2. 2. Run E0 on day 1 — it needs 4.7 MB and no
GPU and it is independently publishable. 3. Delete the MultiFlow fallback (1.63 TB). 4. Rewrite
DAGr's SSH clones and pin the PyG wheel index. 5. Reproduce published mAP before dumping a single
prediction file.

### Team 06 — *Frames Are Not Samples* — STRONG ACCEPT

**Summary.** It identifies that the working event–frame identity `∫events = Δ log I` is not noisy
but misspecified, because `log B_k = L(t_k) + J_k` with `J_k = LME_W(cE) − cE(t_k) ≈ ½Var_W(L)`,
and that this residual is predictable from the event stream alone with **zero fitted parameters**.
It then reports that regression already run: slope 0.955, R² 0.779 with every sensor
non-ideality switched off, against a noise null of R² 0.0015, rising to R² 0.99 on textured
scenes. The proposed fix is one line — substitute `LME_W(cE)` for `c·E(t_k)` — and the proposed
generalisation is a threshold-invariant normalised event profile whose amplitude is identified
from two exposure windows.

**(3) Strongest reason to accept.** The paper's spine is *already measured*, on CPU, in minutes.
No other team in this round arrives with its headline number in hand. Everything downstream is
small and verified: GoPro with events at ETH Zürich (`GOPRO.zip` 19.6 GB, `GOPRO_rawevents.zip`
29.7 GB, HTTP 200, measured 5.11 MB/s → 1.1 h), REBlur (`REBlur.zip` 704 MB,
`REBlur_rawevents.zip` 503 MB, HTTP 200 — the smallest real blur+event set in existence, and the
team is right about that), REFID's ten checkpoints as **GitHub release assets** (63.7–63.8 MB
each, GoPro and HighREV variants, verified live via the GitHub API — and release assets are the
only rot-proof hosting in this field), and DSEC per-sequence, which we already have on disk.
I also verified the team's claim that `EFNet/requirements.txt` carries **no torch pin** — it is
`addict, future, lmdb, numpy, opencv-python, Pillow, pyyaml, requests, scikit-image, scipy,
tb-nightly, tqdm, yapf, h5py` and nothing else. Their sm_120 reasoning — that the decisive
question is whether a repo compiles custom CUDA, not what its README pins — is correct and is the
single most useful piece of engineering judgement anywhere in the ten proposals.

**(4) Strongest reason to reject.** The contribution is one line of code. That is a schedule
virtue and a review liability, and the team scores itself 6/10 on reviewer-proofness for exactly
this reason. Feasibility-wise my only real objection is that Stage 3(b) ("PACE-small … 128–192²
crops, batch 8, AMP, ~50k iterations") is the one part with no measured basis, and its "4–8 GPU-h
per run" is optimistic by roughly 2× against comparison paper #5, which needed a full 3090 at
batch size 1.

**(5) Factual errors.** I found none — this is the only proposal of the ten whose external claims
survived my probes intact. Specifically confirmed: **BS-ERGB is unobtainable** (see the audit
below; the team is right, and is the only team that checked); DSEC is the only public event–frame
set shipping real per-frame exposure intervals; `esim_py` is pure C++/pybind11 with no CUDA.
One correction of emphasis: the team writes that v2e is needed for Stage 0 — v2e is **not on
pypi** (I confirmed: `pypi.org/pypi/v2e/json` returns `{"message":"Not Found"}`; the 200 on
`pypi.org/project/v2e/` is a Cloudflare "Client Challenge" interstitial, not a package), so the
Dockerfile must clone `github.com/SensorsINI/v2e` at a named commit. The proposal says "build from
source" elsewhere but the plan should name the commit.

**(6) Overclaims.** *"the realistic total is 70–120 GPU-hours, i.e. 1–2 weeks on a card shared at
~8–12 usable hours/day."* The arithmetic works only at the top of that range; 120 GPU-h at 8 h/day
is 15 days, not 14, and leaves no slack for the two paywalled verification gates the team itself
flags (Brandli ISCAS 2014; Electronics 15(7):1420). Also *"VRAM is not the binding constraint
anywhere … PACE training at 192² batch 8 is 6–9 GB"* — 9 GB *is* the binding constraint, exactly.
Rewrite as ≤7 GB with gradient checkpointing.

**(7) The hostile experiment.** "Networks absorb static biases; show me your PSNR gain is not 0.1
dB." The team has pre-registered P6 (train on slow motion, test on fast: learned constant removes
0.0 % of the variance, learned linear 51 %, parameter-free LME 91.2 %) and it must be reproduced
at network scale. Its absence is fatal to the *method* half and not to the measurement half —
which is precisely the structure that makes this idea safe to schedule.

**(8) Ranked fixes.** 1. Pin the v2e commit in the Dockerfile; do not write "pip install v2e".
2. Re-budget Stage 3(b) at 8–16 GPU-h/run and cap crops at 160². 3. Close the two paywalled
verification gates in week 1 — they are the only thing that can retroactively destroy the
introduction. 4. Move the DSEC `R ~ P` regression to day 2; the events for `interlaken_00_c` are
already on disk and it is a real-data figure for free. 5. Drop HS-ERGB entirely (see audit).

### Team 05 — *No Offset Can Fix a Width* — ACCEPT

**Summary.** It argues that "alignment" between a frame and an event stream is not the estimation
of a scalar delay but the identification of two temporal support kernels, and proves that a shift
is a unit-modulus linear-phase multiplier in Fourier while a width mismatch is a modulus mismatch
with exact zeros — so no offset can close the gap, and the offset that minimises the residual is a
scene- and speed-dependent quantity masquerading as a rig constant. Its three panels are: the
argmin drifts with blur extent, the residual floor never returns to zero, and the residual
spectrum carries notches at `k/(vT)` that migrate as `1/b`. Its deliverable is a calibration
protocol whose output is a pair of measures plus a per-pixel blind-band mask, not a number.

**(3) Strongest accept.** The load-bearing claim is a numerical experiment on synthetic data where
the opposing formulation is given an *oracle* over the shift, with a computed theoretical floor to
compare against. **It requires no training, no download, and could run on CPU.** Budget: ~96
GPU-h, <8 GB, with 6 GPU-h for the whole failure-phenomenon sweep. That is the second-safest
schedule in the round after team 08, and the safest of the three "theory" ideas. Its one real
dataset — DSEC, 5–6 sequences, ~50 GB — is verified live and partially on disk already.

**(4) Strongest reject.** Its real-data story is a coin flip that the team has correctly identified
but not de-risked: if DSEC daytime exposures give `b < 1 px`, the theory is correct and irrelevant.
Our own E00 partly rescues this — six DSEC sequences sit pinned at 14 996 µs, 10.1× the daytime
width — but E01 explicitly warns that events-per-exposure is **not** a displacement measurement,
and the `b = vT` axis this idea needs *is* a displacement. So the one-day `(T,v)` joint-distribution
check the team schedules is not optional; it is the paper's go/no-go, and it needs the DSEC
optical-flow GT (`train_optical_flow.zip`, 3.96 GB, verified 200) or `lidar_imu.zip`, neither of
which is on disk.

**(5) Factual errors.** (a) *"all simulators pip-installable"* — false. v2e is not on pypi
(verified above), and neither is `esim-py`. Both must be built from GitHub inside the image.
(b) *"EventAid-B … BS-ERGB … Medium risk: BS-ERGB is behind a request form"* — BS-ERGB is not
behind a request form; the request form is **404** (audit below). Mark Real-C as unavailable.
(c) The claim that the CVPR 2026 proceedings "contain 60+ event papers and none is about
event–frame temporal support" is unverifiable and should be softened.

**(6) Overclaims.** *"Feasibility 8/10 … all simulators pip-installable"* — the score survives,
the justification does not. And *"~50 GB of DSEC"* undercounts if the flow GT and IMU are needed
for the `(T,v)` measurement; call it 60 GB.

**(7) Hostile experiment.** Ablation 1 — global shutter, `τ=0`, noiseless, `δ*=0`, ideal
thresholding — is exactly the experiment a hostile reviewer would demand, and the team schedules
it first. Correct instinct, correctly scheduled.

**(8) Ranked fixes.** 1. Measure the DSEC `(T, v)` joint distribution in week 1, before anything
else; it decides whether there is a real-data story. 2. Delete BS-ERGB and EventAid-B from the
plan. 3. Name the v2e / DVS-Voltmeter commits in the Dockerfile. 4. Add the DSEC flow GT to the
download list.

### Team 04 — *When Is Your Prediction?* — ACCEPT

**Summary.** It defines an "effective timestamp" `τ̂ = argmin_t d(ŷ, y*(t))` — the time at which a
prediction would have been right — and predicts that a fused event–RGB head emits the state at the
evidence-weighted centroid `t̄` rather than at the queried time, with a bias that grows with
exposure and is independent of speed, and, crucially, a **within-frame dispersion `σ_τ > 0`** that
no scalar calibration can remove. Its four figures are a support-offset sweep whose V-vertices sit
off zero, a collapse plot across four independent variables, a within-frame `τ̂` histogram, and a
content-control experiment holding the clock fixed while moving contrast energy inside the exposure.

**(3) Strongest accept.** The pilot is the best-engineered piece of scheduling in the round:
3 days, ~3 GPU-h, ~5 GB, **zero external downloads**, one Docker image. And the decision to render
natively at 10 kHz rather than upsample removes v2e's SuperSloMo checkpoint — a Google-Drive
dependency that is the single most common silent killer in this literature. That one design choice
is worth more than any other risk mitigation proposed by any team.

**(4) Strongest reject.** Its real-data closure table is now mostly fiction. FE240hz: portal
returns a zero-byte 416. PKU-DAVIS-SOD: `git.openi.org.cn` times out and then fails TLS handshake
from this machine. BS-ERGB/HS-ERGB: 404. PEOD: the team itself marks "High" risk. That leaves
**EVIMO2 and DSEC**, both live — and the team's own text concedes EVIMO2's 200 Hz Vicon gives a
5 ms sampling interval against a 2–5 ms effect, which is marginal by its own standard. So the
simulation half ships and the real half is in genuine doubt.

**(5) Factual errors.** (a) *"FE240hz … Medium — author-hosted (zhangjiqing.com); Baidu-only
mirrors would hurt"* — the landing page is live (13.7 KB) but its only Download link points to
`http://fe108.dluticcd.com/`, which returns HTTP 416 with a **zero-byte body** on `/` and
`/index.html` and refuses TLS on 443. There is no mirror. Reclassify from Medium to **Dead**.
(b) *"BS-ERGB / HS-ERGB … Low — uzh-rpg download page"* — 404. Reclassify to Dead.
(c) *"`v2e` and `DVS-Voltmeter` (both pip/GitHub installable in Docker)"* — v2e is GitHub-only.
(d) EVIMO2 "*full set large (hundreds of GB); use the npz subsets (~tens of GB)*" is right and I
can make it precise: the independently-moving-object subsets are `npz_left_camera_imo` 1.8 GB,
`npz_right_camera_imo` 1.7 GB, `npz_samsung_mono_imo` 2.4 GB, `npz_flea3_7_imo` (the colour
camera) 33.0 GB — **37 GB total, direct HTTP, no gate, measured 7.03 MB/s → 1.5 hours.**

**(6) Overclaims.** *"Reformulated model: sim + FE240hz + DSEC-Det, 3 seeds ~80 GPU-h, ~8.5 GB"* —
8.5 GB on a card with ~9 GB free and shrinking is a design that fails, per FEASIBILITY.md's
explicit rule. And the FE240hz component of that line no longer exists. Also *"≤ 9 GB throughout"*
in the budget table is stated as a guarantee and is not one.

**(7) Hostile experiment.** §8.3's frame-only/event-only control — *"If `σ_τ` is just as large for
the frame-only model, the phenomenon is not about fusion and the paper's framing is wrong"* — is
correctly identified by the team as the single most important control. Its absence would be fatal.

**(8) Ranked fixes.** 1. Rewrite §8.2 around EVIMO2 + DSEC only; delete FE240hz, PKU-DAVIS-SOD,
BS-ERGB and PEOD. 2. Re-budget the reformulated model at ≤7 GB (drop to 320×240 crops, batch 8).
3. Run the pilot immediately — it is download-free and settles the idea in 3 days. 4. Decide, in
week 2, whether EVIMO2's 5 ms GT can resolve `τ̂`; if not, pre-commit to publishing as
simulation + protocol rather than discovering it in October.

### Team 03 — *Temporal Support Fields* — BORDERLINE

**Summary.** Predicts, per pixel and per modality branch, a sub-probability measure on the time
axis — mass for "is there any valid observation" and shape for "from when" — and replaces
similarity-based cross-modal attention with an overlap-of-supports gate, making abstention a
representable output. The failure phenomenon is a matched-pair construction (constant velocity vs.
dwell-then-dash) with identical blur extent and event count but support overlap 0.8 vs. 0.15.

**Structural problem (one sentence, per the rubric):** its real-data tier is Real-1 BS-ERGB (404),
Real-4 NTIRE/HighREV (CodaLab presigned URLs on a `py3-private` bucket, HTTP 403 without a
competition login), and five baseline repos of which two — ASTW and RTEA, both CVPR 2026 — I could
not locate public code for at all.

**Accept reason:** the phenomenon plot needs only the procedural renderer plus inference from
EFNet/CMTA/REFID, and EFNet and REFID are verified live with weights; ~18 GPU-h lands it in 2–3
days. **Reject reason:** the team itself names the real risk — *"Five external repos in 'days not
weeks' is the real schedule risk"* — and then budgets zero days for it. **Errors:** BS-ERGB
"medium (host availability)" → dead; "low; pypi/HF reachable" for the v2e path → v2e is not on
pypi. **Overclaim:** *"Total ~163 [GPU-h] … At ~50% availability of one shared GPU this is ~2
weeks wall-clock"* — 163 GPU-h at 12 h/day is 13.6 days of *pure GPU*, with no time for the six
repos, the containers, or the failed runs. **Hostile experiment:** ablation (vi), a model trained
with zero simulator labels; without it "you invented the ground truth" is unanswerable. **Fixes:**
1. cut the baseline set to EFNet + REFID + a voxel-grid control; 2. replace BS-ERGB with REBlur
(704 MB, live) and DSEC; 3. drop ASTW and RTEA to "cited, not compared"; 4. re-budget at 100 GPU-h.

### Team 02 — *Exposure-Occupancy Measures* — BORDERLINE

**Summary.** Argues the label attached to a frame is an unspecified functional `A[y]` of the
state's occupancy measure over the exposure, that no benchmark states which `A` it used, and that
label ill-posedness is governed by intra-exposure *acceleration* rather than blur magnitude —
then predicts the measure itself, with the annotation convention as a latent fitted by EM and
conformal coverage marginal over it.

**Structural problem:** its stated primary real validation, and the source of its make-or-break
day-7 kill criterion, is FE108/FE240hz, whose access portal serves a zero-byte body today.

**Accept reason:** the model is genuinely small (ConvNeXt-T / ResNet-18, 256² crops, batch 24,
~5.5–7 GB) and the fallback — EVIMO2, which I verified is 37 GB of direct HTTP with 200 Hz Vicon
6-DoF poses — fully supports the argument in pose space, where the team's own observation that
rotation makes `A_mean ≠ A_mid` even at constant angular velocity is arguably *stronger* than the
box-space version. **Reject reason:** the plan is written with the dead dataset as primary and
the live one as backup, so week 1 will be spent discovering what I already know. **Errors:**
*"v2e is pip-installable. This is why simulation is the right call here"* — wrong, and it is load
bearing, because "no availability risk" is the justification for making simulation primary; v2e
must be built from `github.com/SensorsINI/v2e`. *"FE108 … Medium. Gated by an application form
(fe108.dluticcd.com)"* — the form host is dead. *"BS-ERGB … ~30–60 GB … Low"* — dead.
**Overclaim:** *"One training run ≈ 5–6 h on a half-shared RTX 5090"* is asserted, not measured;
comparison paper #6 needed 8 h on four 3090s for a comparable schedule. **Hostile experiment:**
A1, the frame-only/event-only/both identifiability test with time-reversal pairs — it is a proof
rather than a benchmark delta and it is the paper's best asset. **Fixes:** 1. promote EVIMO2 to
primary and rewrite the kill criterion against it; 2. delete FE108 and BS-ERGB; 3. fix the v2e
install claim; 4. re-time one training run before committing to 16 runs.

### Team 01 — *Latent Exposure Support* — BORDERLINE

**Summary.** Proves that after substituting `u = (τ−t0)/T` the exposure interval vanishes from the
image-formation equation, so a blurred frame carries *no* information about `(t0, T)` or even the
direction of traversal; predicts a Temporal Support Bias law `E[e_∥|d] = (α_model − α_label)·d`;
and replaces the point state with a Bézier trajectory on the normalised support plus an estimated
support field, with `K=0` recovering the current formulation exactly.

**Structural problem:** the paper's argument is Fig 1b, and Fig 1b requires FE240hz, which cannot
be obtained today.

**Accept reason:** the non-identifiability proposition is provable in half a page, the `K=0`
ablation *is* the SOTA comparison, and Fig 1a is essentially already delivered by our E00 — the
team's insight that DSEC publishes the support for free and nobody reads it is correct and is the
best single observation in the round. **Reject reason:** every real-data source it names for the
*measurement* is gone. FE240hz portal: zero-byte 416. PKU-DAVIS-SOD: `git.openi.org.cn`
unreachable from this machine (connect timeout, then TLS handshake failure). BS-ERGB: 404. And
its tracker baselines — FENet, AFNet, ISTASTrack — exist only on FE240hz, so without FE240hz there
are no checkpoints to indict. **Errors:** the availability column is wrong in three of six rows;
"FE108/FE240hz … Medium-high. Access is by application" understates a dead portal;
"PKU-DAVIS-SOD … Medium. Hosted on OpenI" understates an unreachable host. **Overclaim:**
*"Fig 1 (the whole argument): inference-only with released checkpoints … ~10 [GPU-h]"* — the
checkpoints in question are FE240hz-only and the data does not exist here; the 10 GPU-h figure is
for an experiment that cannot be started. Also its own risk section names access to FE240hz as the
dominant risk and then proposes "apply on day 1" as the mitigation — there is nothing to apply to.
**Hostile experiment:** a hostile reviewer demands the TSB slope on *real* data with *other
people's* checkpoints. Its absence is fatal to the paper as pitched. **Fixes:** 1. find a real
dataset with GT above the frame rate that actually downloads — EVIMO2 (37 GB, verified) is the
only candidate, and it is 6-DoF pose, not boxes, so the paper must change task; 2. failing that,
re-pitch as "DSEC exposure statistics + SIE validation + SupportBench", which the team already
names as a graceful degradation and which is a real but much smaller paper; 3. delete the FE240hz
day-14 go/no-go gate and replace it with a day-3 EVIMO2 gate.

### Team 10 — *Fusion Is Ill-Typed* — BORDERLINE

**Summary.** Types a frame as a mass-one probability measure applied in the linear domain and an
event bin as a mass-zero signed measure applied in the log domain, proves the two sets are
disjoint so no shift/scale/warp reconciles them, and audits published fusion models for illegal
mixing via off-support attention mass computed from Jacobian influence (so it applies to gates and
AdaIN, not just softmax attention).

**Structural problem:** it needs six repos with six dependency stacks, and it says so —
*"Six repos means six dependency stacks; the real cost is Docker builds, not GPU. Budget two days
for environments"* — which is the correct diagnosis attached to a wrong estimate. Two days for six
Docker images including a Baidu-hosted checkpoint and two Google-Drive weight sets is off by a
factor of five; the honest number is two to three weeks.

**Accept reason:** the support-blind-pair result is a construction plus a theorem and *cannot
fail*, which is a rare floor to have under a deadline; and DSEC plus EFNet's GoPro/REBlur (all
verified live) carry the real-data half without any gated source. **Reject reason:** besides the
Docker breadth, its own budget table has *"Operator fine-tune, FRN (640×480, batch 2, AMP + grad
ckpt) ~40 GPU-h, ~8.5 GB"* — that is above the safe band on a card whose free memory can shrink,
and it is 40 GPU-h that will be lost when someone else's job grows. **Errors:** *"events by exact
log-threshold crossing, then re-generated with v2e and DVS-Voltmeter (both pip/Docker-installable)"*
— v2e is not pip-installable. Also the plan lists FE240hz and BS-ERGB in Death 2's mitigation
("use … REBlur, FE240hz, BS-ERGB") — two of those three are unobtainable; REBlur alone survives,
and at 704 MB it is a fine choice. **Overclaim:** *"Target: ≥4 models fully diagnosed"* with two
days of environment budget. **Hostile experiment:** fine-tune each model on the high-`s` regime
and show OSAM does not fall — the experiment that converts "your weights are bad" into "your
formulation is bad". Its absence is fatal. **Fixes:** 1. cut to three models with the cleanest
stacks (EFNet, RENet, FRN) and drop CEUTrack/Gev-RS with their Baidu hosting; 2. re-budget FRN
fine-tuning at 448×448 to reach ≤7 GB; 3. lead with the support-blind pairs, which need nothing;
4. budget 10 working days for containers.

### Team 07 — *Chronofields* — BORDERLINE

**Summary.** Inverts the query: instead of `time → state`, predict for a queried state a
distribution over *when* it held, with events entering as exact observations, frames as
interval-censored ones, and an explicit `∅` atom for "never in this window"; adds a temporal
eikonal constraint `∇_u τ · v = 1` that exists only when time is the output.

**Structural problem:** the experiment the team itself says the paper lives or dies on —
Time Lens → 1000 fps → RVT versus the chronofield — requires two of the hardest toolchains in the
field to run simultaneously on sm_120, and neither is budgeted.

**Accept reason:** the C1 anchor is genuinely excellent scheduling — hold out a slice of a real
event stream and predict when each pixel next crosses threshold, supervised by the held-out real
events. Real sensor, microsecond ground truth, no simulator, no annotator, and DSEC is already
partly on disk. **Reject reason:** the plan names six datasets, of which HS-ERGB and BS-ERGB are
dead, EvTTC is unverified, X4K1000FPS needs ESIM built from source (not on pypi), and EVIMO2's
200 Hz GT the team itself calls "supporting, not primary". The team writes *"the plan as written
names six datasets and must be cut to two before anyone starts"* and then does not cut it.
**Errors:** *"HS-ERGB / BS-ERGB … ~30–60 GB (size unverified — rate-limited …) | availability"* —
now verified: unavailable. *"v2e is far too slow for this volume. Use DVS-Voltmeter or ESIM"* is
correct advice; `esim_py` is however also not on pypi and must be built. **Overclaim:**
*"Total ≈ 75–90 GPU-hours ≈ 4–6 days"*, which excludes, by the team's own admission, that
"reproducing FAOD/RVT baselines faithfully enough that a reviewer believes the comparison is a week
of unglamorous work not counted above." Note also that I could not locate a public FAOD repository
under any obvious name — treat FAOD as cited-only. Good news for the head-to-head: the Time Lens
checkpoint is live (`download.ifi.uzh.ch/rpg/web/data/timelens/data2/checkpoint.bin`, 0.44 GB,
HTTP 200). **Hostile experiment:** the reconstruct-then-detect head-to-head, and the team has
pre-registered its own falsification criterion (P95 CTE within 15 % ⇒ dead), which is admirable
and also means the paper has a real chance of dying in week 4. **Fixes:** 1. cut to DSEC + EVIMO2,
today; 2. run the C1 anchor first — it needs one DSEC sequence; 3. schedule the RVT sm_120 port
before the head-to-head, or accept a weaker detector; 4. drop X4K1000FPS and the ESIM build.

### Team 09 — *Change-Time* — REJECT

**Summary.** Replaces the shared global timeline with a per-pixel clock `τ(x,t) = C·N(x,t)` — the
accumulated change, i.e. the arc length of the quantised log-intensity path — in which the event
stream is a complete observation up to one unknown scalar per pixel, the representation is exactly
invariant to any monotone time reparameterisation, and the frame's temporal support becomes a
measured per-pixel width `W(x) = C·N_exp(x)`. Two independent pillars: P3, that any rule emitting a
window *in seconds* must clamp and therefore has a bounded speed dynamic range (predicted elbow at
ASTW's own `Δt_max/Δt_min = 25`); and P6, that on a decoupled `(k, T)` grid baseline iso-error
contours run along hyperbolas `k·T = const` while theirs run along horizontal lines.

**Is the flaw fatal to the idea or to this execution?** To **this execution**. The coordinate is a
real idea and the `β`-is-the-window observation from released code is genuinely strong. But as
scheduled it cannot be built here by November.

**(3) Strongest accept reason.** Stage 0 is an analytic simulator plus a small classifier: one day,
zero downloads, and it settles P3. Two independent pillars with two independent one-day gates is
the correct structure for a risky idea, and the team's instruction — *"Run Stage 0 and Stage 0b
before writing another word"* — is right.

**(4) Strongest reject reason.** Both make-or-break experiments depend on artefacts I could not
obtain. **P3 requires ASTW** (CVPR 2026): the entire prediction is *"ASTW tracks us to ρ ≈ 25,
then turns upward"*, with an elbow computed from ASTW's published hyperparameter table, and the
plan additionally requires sweeping ASTW over patch size and `(Δt_min, Δt_max)` because
*"if any clamp setting flattens the ρ curve, the hyperparameter objection stands."* I could find no
public ASTW implementation; a GitHub code search returned nothing. Re-implementing a CVPR 2026
method well enough that a reviewer accepts a negative result about it, and then tuning it
adversarially against yourself, is a month of work with an unbounded rebuttal surface —
"you re-implemented it wrong" is unanswerable. **P6's real arm requires BS-ERGB/HS-ERGB and
HighREV**: BS-ERGB is 404, HS-ERGB is 404 with only a 2.8 GB third-party derivative on
HuggingFace, HighREV is behind a CodaLab login. The team's own table already marks FE108 dead and
HetVel unconfirmed. So pillar 1 needs an unobtainable *baseline* and pillar 2 needs unobtainable
*data*, and the fallback for each is the other.

**(5) Factual errors.** (a) *"Prophesee GEN1 … not published; est. ≥250 GB | medium; form-gated"* —
**wrong, and the error costs the team its cheapest path.** The RVT-preprocessed `gen1.tar` is
98.6 GB at `download.ifi.uzh.ch/rpg/RVT/datasets/preprocessed/gen1.tar`, HTTP 200, **no form**,
downloadable in ~6.0 hours at the 4.56 MB/s I measured. Team 08 found this; team 09 did not.
(b) *"FE240hz / FE108 … DEAD: host fe108.dluticcd.com refused connection"* — nearly right, and I
confirm the practical conclusion, but the mechanism is different: the host resolves to
38.6.135.80 and answers on port 80 with HTTP 416 and a zero-byte body; it refuses only TLS on 443.
Same verdict, better evidence. (c) *"BS-ERGB … form-gated + non-standard 'evaluation license' …
Start the form today"* — there is no form to start; the URL named in the official
`uzh-rpg/timelens-pp` README is a 404. (d) *"DVS-Voltmeter … is a one-evening container; v2e's
pinned CUDA + SuperSloMo stack is the real friction. Budget a day for containers"* — the diagnosis
is right and the budget is not; v2e's SuperSloMo checkpoint is Google-Drive hosted and is a
single point of failure the team has not probed.

**(6) Overclaims.** *"Core (Stage 0 + 0b + N-Caltech + GEN1) ≈ 135 GPU-h ≈ 6 days. Full ≈ 215
GPU-h."* 215 GPU-h at a realistic 10 h/day on a contended card is 21.5 days of *pure GPU*, on top
of: containerising three simulators, re-implementing nine partitioning strategies plus ASTW, and
running a `β`-sensitivity test across seven graph/point methods (AEGNN, DAGr, EvGNN, SlideGCN,
PEPNet, EventMamba, SECNet), each with its own environment. The baseline list runs to more than
twenty named methods across three axes. That is a two-person-year plan compressed into ten weeks.
Also *"GPU 0 currently free as headroom"* directly contradicts the binding constraint in
FEASIBILITY.md, which says only GPU 1 may be used; a plan that quietly assumes a second card is a
plan that fails.

**(7) The hostile experiment.** "Re-tune ASTW's six knobs and show the elbow survives." The team
anticipates it — *"Sweeping ASTW's clamp is mandatory"* — and cannot execute it without ASTW.
That is the definition of an unfixable schedule problem.

**(8) Ranked fixes** (what would make me revisit this). 1. Drop pillar 1 entirely, or re-found it
against **fixed-time and fixed-count** baselines only, which are trivially re-implementable and
whose clamps are ours to set — the argument survives, weaker, and becomes buildable. 2. Re-found
pillar 2 on DSEC (live, real per-frame exposure intervals) plus REBlur (704 MB, live) instead of
BS-ERGB/HighREV; SWC can be measured against DSEC's published exposure widths. 3. Use RVT's
`gen1.tar` — no form, 6 hours. 4. Cut the baseline list from twenty-plus to five. 5. Remove every
assumption about GPU 0. With 1–5 done this becomes a reasonable ACCEPT; as written it is a REJECT.

---

## Dependency audit

Every external dependency named across the ten proposals, with the status I measured on
2026-09-01 from the target machine. Sizes are as returned by `Content-Length`. "Critical path"
means at least one team's headline figure cannot be produced without it.

### Datasets

| Dependency | Status (verified 2026-09-01) | Size | Critical path for |
|---|---|---|---|
| **DSEC** per-sequence events/images/calib/exposure | **VERIFIED LIVE** — `interlaken_00_c_events_left.zip` 856,188,821 B, `..._image_exposure_timestamps_left.txt` 13,482 B, `zurich_city_09_a_events_left.zip` 2.80 GiB, all HTTP 200. Directory index is 403; fetch by explicit path. | 0.25–9 GB/seq | 1, 3, 4, 5, 6, 7, 8, 9, 10 |
| **DSEC bulk** (`train_coarse/`) | **VERIFIED LIVE** — `train_events.zip` 122.83 GiB, `train_images.zip` 215.53 GiB, `train_optical_flow.zip` 3.69 GiB. | up to 338 GiB | 1 (flow GT), 5 |
| **DSEC-Detection** | **VERIFIED LIVE** — `dsec-det.zip` 81.85 GiB, `dsec-det_left_images_distorted.zip` 34.07 GiB, `dsec-det_left_object_detections.zip` **4.7 MB**. | 4.7 MB – 87.9 GB | **8 (E0/E3)**, 1, 10 |
| **Prophesee GEN1 / 1 Mpx, RVT-preprocessed** | **VERIFIED LIVE, NO FORM** — `gen1.tar` **98,628,976,640 B**, `gen4.tar` **190,351,165,440 B**, HTTP 200. This bypasses Prophesee's registration entirely. | 98.6 / 190.4 GB | **8 (E1)**, 9 |
| **Prophesee GEN1 original** | **GATED** — `prophesee.ai` landing page HTTP 200, download behind a request form. Irrelevant given the row above. | — | none, if the row above is used |
| **EVIMO2 v2 (npz)** | **VERIFIED LIVE, NO GATE** — full bucket listing at `obj.umiacs.umd.edu/evimo2v2npz/`. IMO subsets: `left_camera_imo` 1.8 GB, `right_camera_imo` 1.7 GB, `samsung_mono_imo` 2.4 GB, `flea3_7_imo` (colour) 33.0 GB. Measured 7.03 MB/s. | 37 GB (IMO) / 330 GB (all) | **2 (fallback→primary)**, 4, 7 |
| **FE108 / FE240hz** | **DEAD (portal).** Landing page `zhangjiqing.com/dataset/` live, 13,721 B; its only Download link is `http://fe108.dluticcd.com/`, which resolves to 38.6.135.80 and returns **HTTP 416 with a 0-byte body** on `/` and `/index.html`, and **refuses TLS on 443**. No form, no content, no mirror. | unknown | **1 (Fig 1b)**, **2 (primary real)**, 4 |
| **BS-ERGB** (Time Lens++) | **DEAD.** The official `uzh-rpg/timelens-pp` README says *"Download the dataset after filling out this form"* → `rpg.ifi.uzh.ch/timelens/timelens++download.html` → **HTTP 404**. The near-miss path `rpg.ifi.uzh.ch/timelens++download.html` returns 200 but is **5,062 bytes of RPG site navigation** with zero `<form>`, zero `<input>` and zero dataset links. HuggingFace search for `ergb` and `bsergb`: **0 datasets**. | — | **9 (pillar 2)**, 1, 3, 4, 5, 7 |
| **HS-ERGB** (Time Lens) | **DEAD (official).** `rpg.ifi.uzh.ch/timelens/` is a 126-byte meta-refresh; `timelensdownload.html` is the same navigation-only 5,062-byte page. Only surviving copy: third-party HF mirror `RuixuanJiang/Low_Level_Datasets/HS_ERGB_CDS.zip`, **2.61 GiB** — a processed subset, not the dataset. | 2.8 GB (partial) | 3, 7, 9 |
| **PKU-DAVIS-SOD** | **UNREACHABLE from this machine.** `git.openi.org.cn:443` — TCP connect timeout at 30 s, then `SSL routines::sslv3 alert handshake failure`. | unknown | 1, 4 |
| **GoPro + events (EFNet mirror, ETH)** | **VERIFIED LIVE** — `GOPRO.zip` 18.26 GiB, `GOPRO_rawevents.zip` 27.65 GiB, HTTP 200, measured 5.11 MB/s. Also `RuixuanJiang/Low_Level_Datasets/GOPRO.zip` 32.05 GiB on HF at 6.88 MB/s. | 19.6–34 GB | **6 (Stage 0)** |
| **REBlur** | **VERIFIED LIVE** — `REBlur.zip` 0.656 GiB, `REBlur_rawevents.zip` 0.468 GiB at `data.vision.ee.ethz.ch/csakarid/shared/EFNet/`. The `better-tomorrow.oss-cn-beijing` host cited by some teams is **404**; use the ETH mirror. | 0.7 / 0.5 GB | 6, 10, 3 |
| **HighREV (NTIRE 2025)** | **GATED / UNVERIFIED** — CodaLab redirects resolve to presigned URLs on a `py3-private` MinIO bucket and return **403** without a competition login. Alternate paths are Google Drive and OneDrive links. | unknown | 3, 6 (secondary), 9 |
| **N-Caltech101 (DAGr mirror)** | **VERIFIED LIVE** — `download.ifi.uzh.ch/rpg/dagr/data/ncaltech101.zip` 2.489 GiB. | 2.7 GB | 9 |
| **MultiFlow (bflow)** | **VERIFIED LIVE BUT UNUSABLE** — `multiflow/train.tar` **1,516.71 GiB ≈ 1.63 TB** (exceeds 990 GB free disk); `multiflow/val.tar` 303.09 GiB ≈ 325 GB (consumes the entire 300 GB budget, ~20 h to fetch). | 325 GB / 1.63 TB | 8 (fallback — must be deleted) |
| **DSEC-Flow (bflow)** | **VERIFIED LIVE** — `bflow/DSEC/train.tar` 139.34 GiB ≈ 149.6 GB, ~9.1 h at measured rate. | 149.6 GB | **8 (E2)** |
| **COESOT / EventVOT / Gev-RS** | **UNVERIFIED** — Baidu Pan (`pan.baidu.com` reachable, contents not) and Google Drive. EventVOT additionally has no RGB channel and is unusable for fusion (team 9 is right about this). | — | 10 (optional) |
| **X4K1000FPS / Adobe240 / Need-for-Speed** | **UNVERIFIED** — not probed; repo `JihyongOh/XVFI` is live. | — | 3, 5, 7 |
| **HuggingFace DSEC mirrors** | `mickeykang/DSEC-3DOD` HTTP 200 (40.2 GB single zip, per FEASIBILITY.md); `Passwerob/DSEC_proc` 395 GB, too large. | 40.2 GB | 8 (DSEC-3DOD labels) |

### Checkpoints

| Dependency | Status | Size | Critical path for |
|---|---|---|---|
| **RVT** rvt-{b,s,t} × {gen1, 1mpx} | **VERIFIED LIVE** — `gen1/rvt-b.ckpt` 222,937,503 B, all six URLs present in the README. | ~0.22–0.30 GB ea. | **8** |
| **S5-ViT / SSM-ViT** gen1/gen4 base+small | **VERIFIED LIVE** — `CVPR24_Zubic/gen1_base.ckpt` 218,814,784 B. Repo `uzh-rpg/ssms_event_cameras` live, default branch `master`, last pushed 2024-09-28. | 0.22 GB ea. | **8** |
| **BFlow** `E_LU4_BD2` / `E_I_LU4_BD2` | **VERIFIED LIVE** — 0.12 GiB / 0.15 GiB. The single-variable event-only vs. event+image pair. | 0.13 / 0.16 GB | **8 (E2 headline)** |
| **DAGr** `dagr_s_50.pth` | **VERIFIED LIVE** — 0.31 GiB. | 0.33 GB | 8 (E3), 1 |
| **E-RAFT** dsec / mvsec_20 / mvsec_45 | **VERIFIED LIVE** — `checkpoints/dsec.tar` 0.06 GiB (note: the README URL is `/checkpoints/`, not `/models/`). | 64 MB ea. | 8 |
| **REFID** (10 checkpoints, GoPro + HighREV) | **VERIFIED LIVE** — GitHub *release assets* under tag `v0.1`, 63.7–63.8 MB each. Rot-proof hosting. | 0.64 GB total | **6** |
| **EFNet** (GoPro, REBlur) | **LIVE, GOOGLE DRIVE** — three Drive file links in the README; the *data* is on ETH (verified), the *weights* are on Drive (quota risk). `requirements.txt` confirmed to carry **no torch pin**. | ~35 MB | **6**, 10 |
| **Time Lens** | **VERIFIED LIVE** — `download.ifi.uzh.ch/rpg/web/data/timelens/data2/checkpoint.bin` 0.44 GiB. | 0.47 GB | **7 (head-to-head)** |
| **E2VID** | **UNVERIFIED** — the URL cited by team 6 (`rpg/web/data/e2vid/model/E2VID_lightweight.pth.tar`) returns 404; repo `uzh-rpg/rpg_e2vid` is live and carries its own link. | 41 MB | 6 (minor) |
| **FAOD** | **UNVERIFIED / probably unreleased** — no repository found under any obvious name. Treat as cited-only. | — | 1, 4, 7, 8 (all as a baseline they can drop) |
| **ASTW (CVPR 2026), RTEA/TSANet (CVPR 2026)** | **UNVERIFIED / no locatable public code.** | — | **9 (P3, fatal)**, 3, 5 |
| **FENet / AFNet / ISTASTrack** | **UNVERIFIED** — moot: they exist only on FE240hz, which cannot be downloaded. | — | **1 (fatal)**, 2 |
| **RENet / FRN / CEUTrack / SODFormer / BRENet / EvUnroll** | Repos all HTTP 200. Weights: Google Drive (FRN, EvUnroll), Baidu (CEUTrack), unverified (SODFormer, whose *data* is on the unreachable OpenI). | — | 10 |

### Simulators and toolchain

| Dependency | Status | Notes |
|---|---|---|
| **v2e** | **NOT ON PYPI — CONFIRMED.** `pypi.org/pypi/v2e/json` → `{"message": "Not Found"}`. (The HTTP 200 on `pypi.org/project/v2e/` is a Cloudflare "Client Challenge" interstitial, **not** a package — do not be fooled by a 200 here.) `github.com/SensorsINI/v2e` HTTP 200; must be cloned at a named commit and built in-image. Its SuperSloMo checkpoint is **Google-Drive hosted** and is the single biggest silent failure mode in this literature. Teams 2, 3, 5, 10 all assert v2e is pip-installable. **They are all wrong.** | critical for 2, 3, 5, 8(E4), 9, 10 |
| **esim-py / ESIM** | **NOT ON PYPI — CONFIRMED** (`pypi.org/pypi/esim-py/json` → Not Found). `github.com/uzh-rpg/rpg_esim` and `rpg_vid2e` both HTTP 200. Pure C++/pybind11, no CUDA. | 7, 8, 9 |
| **DVS-Voltmeter** | **VERIFIED LIVE** — `github.com/Lynn0306/DVS-Voltmeter` HTTP 200, source archive downloadable. MIT, small dependency set; genuinely the cheapest to containerise. | 3, 5, 6, 7, 9, 10 |
| **RVT / S5-ViT toolchain vs. sm_120** | **HAZARD, VERIFIED.** `torch-req.txt`: `torch==2.0.0 / torchvision==0.15.0 / torchdata==0.6.0`, installed from `download.pytorch.org/whl/cu118`; `requirements.txt`: `pytorch-lightning==1.8.6`. **cu118 emits no sm_120 kernels** and PL 1.8.6 will not import against torch 2.7. No custom CUDA extension in the repo, so the port is bounded but real. | **8 (both E1 and E2)**, 7, 9 |
| **PyTorch Geometric extensions (DAGr)** | **VERIFIED AVAILABLE** — `data.pyg.org/whl/torch-2.7.1+cu128.html` exists and carries `torch_scatter 2.1.2`, `torch_cluster 1.6.3`, `torch_sparse 0.6.18`, `torch_spline_conv`, `pyg_lib` for cp310/cp311 linux. Nothing needs compiling. Remaining DAGr friction: `download_and_install_dependencies.sh` clones detectron2 and YOLOX over `git@github.com:` **SSH** URLs, which fail without a key — rewrite to HTTPS. | 8 (E3), 1 |
| **Base image** | `cvpr19-gpu-g1:torch2.7.1-cu128` verified working on sm_120 per FEASIBILITY.md; `hdf5plugin` required for DSEC events and is pip-installable in-image. | all |

### Measured bandwidth (this machine, 2026-09-01, 60 MB range requests)

| Host | Sustained | Implication |
|---|---|---|
| `download.ifi.uzh.ch` (DSEC, RVT, bflow, DAGr, S5-ViT) | **4.56 MB/s** = 16.4 GB/h | gen1.tar 6.0 h · gen4.tar 11.6 h · dsec-det.zip 5.4 h · bflow DSEC train 9.1 h · DSEC bulk events 8.0 h |
| `data.vision.ee.ethz.ch` (EFNet GoPro/REBlur) | **5.11 MB/s** | GOPRO.zip 1.1 h · REBlur 4 min |
| `huggingface.co` | **6.88 MB/s** | GOPRO 32 GB in 1.4 h |
| `obj.umiacs.umd.edu` (EVIMO2) | **7.03 MB/s** | full IMO subset (37 GB) in 1.5 h |

**Conclusion on bandwidth, which contradicts three teams:** download time is **not** a critical
path for any plan under ~300 GB. Team 08's *"the critical path is download bandwidth, not compute"*
is wrong — its whole ~440 GB is under two days of wall clock. The critical paths in this round are
**toolchain ports** and **dead hosts**, in that order.

---

## Schedule verdict

Dates are the earliest a **real figure** — a plot made from data, not from a plan — can exist.
GPU-hours and peak VRAM are my estimates, not the teams'.

| Team | First real figure | What it is | GPU-h (mine) | Peak VRAM (mine) | P(submittable by Nov 2026) |
|---|---|---|---|---|---|
| **08** | **2026-09-03** | E0 label forensics: DSEC-Det inter-frame GT vs. its own linear-interpolation prior, from a 4.7 MB file, **zero GPU** | 40–55 (+40 h of toolchain porting) | ~6 GB (1 Mpx eval, batch 2) | **85 %** |
| **06** | **2026-09-04** | `R ~ P` regression on `interlaken_00_c`, which is already on disk; the simulation half already exists | 90–140 | ~7 GB (192² batch 8) | **82 %** |
| **05** | **2026-09-05** | Panels A–C from the CPU/FFT oracle-offset sweep, no download, no training | 90–110 | <5 GB | **75 %** |
| **04** | **2026-09-05** | Fig 1 + Fig 2 from the 10 kHz analytic renderer, zero downloads | 150–200 | 7 GB *if re-budgeted*; 8.5 GB as written | **65 %** |
| **10** | **2026-09-12** | Support-blind pairs (a construction, cannot fail) on the procedural renderer | 130–170 | 8.5 GB as written (too high) | **50 %** |
| **03** | **2026-09-09** | `O*` cliff from matched pairs + EFNet/REFID inference | 130–170 | ~7 GB | **48 %** |
| **02** | **2026-09-11** | Panel B (`D` vs `ν` at fixed `β`) in simulation; needs v2e built first | 110–150 | ~7 GB | **45 %** |
| **01** | 2026-09-03 for Fig 1a (largely already done by E00); **never** for Fig 1b as scoped | DSEC exposure/`d` statistics | 60 (achievable) of 217 (planned) | ~7 GB | **35 %** |
| **07** | **2026-09-16** | C1 anchor: next-crossing-time on held-out real DSEC events | 100–140 | ~6 GB | **32 %** |
| **09** | **2026-09-08** | Stage 0 `ρ`-sweep against fixed-time/fixed-count only (ASTW absent) | 215+ planned; ~60 achievable | ~6 GB | **20 %** |

**Justification of the percentages.**

- **08 at 85 %.** The only failure modes are the RVT/S5-ViT sm_120 port and "no ranking flip". The
  port has a CPU fallback for E0 and a bounded scope (no custom CUDA). "No flip" is a *result*
  quality risk, not a schedule risk, and the team has pre-specified a weaker but publishable
  fallback (E0 + the architecture-predicted `τ̂`, which our E02 already half-confirms). I take
  15 % off for the port going badly and for the ±0.3 mAP reproduction failing after it.
- **06 at 82 %.** The headline number already exists. The data is small and verified. The only real
  risk is the trained PACE model, and the paper is explicitly publishable without it. I take 18 %
  off for the two paywalled verification gates (either could reveal the exposure gap is known) and
  for v2e's build.
- **05 at 75 %.** Theory tier is essentially guaranteed. The 25 % is entirely the real-data
  question: if DSEC gives `b < 1 px` even at night, the paper is a simulation study, and the team
  would have to decide in week 2 whether to ship that.
- **04 at 65 %.** The pilot is near-certain to produce figures by 2026-09-05. The 35 % is the
  collapse of the real-data plan — three of four sources gone — plus the genuine risk that
  EVIMO2's 5 ms GT cannot resolve a 2–5 ms effect, which would leave a simulation-only paper the
  team itself calls "a calibration note".
- **10 at 50 %.** Split almost exactly by the container question. The support-blind pairs are a
  guaranteed figure; four fully-diagnosed models in ten weeks with six dependency stacks and two
  Baidu/Drive weight sources are not. If they cut to three models on day 1 I would raise this to 62 %.
- **03 at 48 %.** The phenomenon plot lands fast; the paper as scoped needs five baselines and a
  real tier that is mostly dead. Reduce to EFNet + REFID + REBlur + DSEC and this goes to 65 %.
- **02 at 45 %.** Everything hinges on re-founding the plan on EVIMO2 in week 1. If they do, 65 %.
  If they spend three weeks chasing FE108, 25 %.
- **01 at 35 %.** Fig 1a is free and already done; the paper it wants to write is not reachable
  because every real-data source and every baseline checkpoint it names is behind a dead host. The
  35 % is the probability that the graceful degradation the team already wrote down — DSEC
  statistics + SupportBench + SIE validation — is executed early enough to become a real paper.
- **07 at 32 %.** The C1 anchor is real and cheap. But the paper's own falsification criterion is a
  head-to-head against Time Lens → RVT, which needs the RVT port, and its real-event tier is dead.
  The team is admirably honest that a tie kills the idea; I price that in.
- **09 at 20 %.** Stage 0 will produce *a* figure. But the figure the paper is built on requires
  ASTW, and the 20 % is essentially the probability that they abandon P3 fast enough to rebuild
  around fixed-time/fixed-count baselines and DSEC, and still write a paper.

---

## Ranking

By probability of shipping a submittable CVPR 2027 paper by November 2026, best first:

1. **Team 08** — Right Place, Wrong Time (85 %)
2. **Team 06** — Frames Are Not Samples (82 %)
3. **Team 05** — No Offset Can Fix a Width (75 %)
4. **Team 04** — When Is Your Prediction? (65 %)
5. **Team 10** — Fusion Is Ill-Typed (50 %)
6. **Team 03** — Temporal Support Fields (48 %)
7. **Team 02** — Exposure-Occupancy Measures (45 %)
8. **Team 01** — Latent Exposure Support (35 %)
9. **Team 07** — Chronofields (32 %)
10. **Team 09** — Change-Time (20 %)

Note the shape of this list. The top four all share one property: **their first real figure needs
no download, or needs only a file that is already on disk.** The bottom four all share the
opposite: their headline figure requires a specific external artefact, and in every case that
artefact is dead, unreachable, or unreleased. That is not a coincidence and it is not a
coincidence in any deadline-bound research programme I have watched fail.

---

## My winner and its fatal flaw

**Winner: Team 08 — *Right Place, Wrong Time*.**

It is the only proposal that competes in the weight class this machine can enter. Read the
comparison set again: RVT needed 2 days on an A100 for Gen1 and 3 days on two A100s for 1 Mpx;
S5-ViT the same; the CVPR 2025 paper that *brands itself as efficient* still needed four 3090s;
LEOD says out loud that it used RVT-S "due to limited computation resources" on two A40s. There is
no world in which 9 GB of a shared 5090 trains a competitive recurrent event detector before
November. Team 08 does not try. It takes other people's checkpoints, other people's benchmarks and
other people's labels, and asks a question none of them can answer about themselves — and the
answer to that question, if it lands, belongs to the field rather than to us, which is exactly the
kind of contribution that survives an AC discussion without a leaderboard.

And its dependency graph is the only one I could verify end to end: 98.6 GB of Gen1 and 190.4 GB of
Gen4 downloadable **without a Prophesee form**, five RVT and four S5-ViT checkpoints on the same
server consuming the same preprocessed tarballs so there is no preprocessing degree of freedom for
a reviewer to attack, a BFlow event-only/event+image checkpoint pair that is a single-variable
controlled experiment already sitting on a server, and a headline first result that costs a 4.7 MB
label file and no GPU at all. First real figure on 2026-09-03.

**Its fatal flaw: the plan contains no line for the toolchain, and the toolchain is the whole
paper.** `uzh-rpg/RVT` pins `torch==2.0.0` against `whl/cu118` with `pytorch-lightning==1.8.6`, and
`ssms_event_cameras` vendors that same tree. **cu118 produces no sm_120 kernels.** Nothing in E1 or
E2 executes on this GPU until someone has ported a 2023 Lightning stack to torch 2.7.1+cu128 and
then reproduced five published mAP numbers to ±0.3 through it. The proposal's own feasibility
self-score is 8/10 with the words *"~35 GPU-hours, nothing over 9 GB VRAM, no training"* — and the
sentence that should have been there instead is *"and four to six days of dependency archaeology
before the first GPU-hour is spent."* If the port fails, everything except E0 falls back to CPU
inference, which is adequate for the 4.7 MB label forensics and hopeless for a Gen1 validation
pass. That is the difference between a CVPR paper and a workshop note, and it will be decided in
week one by a `pip install`, not by an idea.

