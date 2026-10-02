#!/bin/bash
# E66 pre-queue verification, CPU only. rvt-s, first 12 validation sequences, every 3rd labelled frame,
# H = 1,5,10,21, BATCH=4 (the production batched path; probes re-run batch-1), oldest-window probe on.
# Then: regression gate against the E65 reset-shift0 dump (cross-device unit check, GPU dump vs CPU
# dump) and the five-point audit in src/e66_verify.py.
cd /media/hdd8/justin/my_project/CVPR20
TAG=${1:-s}; D=experiments/e66_fixedH/verify; mkdir -p $D
nice -n 19 docker run --rm --cpus=4 --cpu-shares=32 --memory=16g --user $(id -u):$(id -g) -e HOME=/tmp \
  -e DEV=cpu -e THREADS=4 -e FAM=rvt -e TAG=$TAG -e NSEQ=12 -e STRIDE=3 -e HS=1,5,10,21 -e BATCH=4 -e PROBE=2 \
  -e OUT=/work/$D/dets-rvt-$TAG.npz -v $PWD:/work -w /work cvpr19-gpu-g1:torch2.7.1-cu128 \
  bash -lc "pip install --user hdf5plugin omegaconf hydra-core einops StrEnum scipy >/tmp/pip.log 2>&1 || { echo PIP_FAILED; tail -15 /tmp/pip.log; exit 90; }; python3 -u /work/src/e66_fixedH_dump.py" || exit 1
python3 src/e66_gate.py $TAG $D/dets-rvt-$TAG.npz --unit | tee $D/gate-$TAG.log
python3 src/e66_verify.py $D/dets-rvt-$TAG.npz experiments/e65_rvt_boundary/dets-rvt-$TAG-reset-shift0.npz | tee $D/verify-$TAG.log
