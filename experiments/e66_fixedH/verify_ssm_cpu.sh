#!/bin/bash
# E66 SSM-ViT smoke + gate, CPU only: s5vit-small, 12 sequences, every 3rd frame, batched (2).
# Gate: released e51 s5vit-small detections at chunk position p == fixed H=p+1 (needs the inert carried state).
cd /media/hdd8/justin/my_project/CVPR20
TAG=${1:-small}; D=experiments/e66_fixedH/verify_ssm; mkdir -p $D
nice -n 19 docker run --rm --cpus=4 --cpu-shares=32 --memory=16g --user $(id -u):$(id -g) -e HOME=/tmp \
  -e DEV=cpu -e THREADS=4 -e FAM=ssm -e TAG=$TAG -e NSEQ=12 -e STRIDE=3 -e HS=1,5,10,21 -e BATCH=2 -e PROBE=2 \
  -e OUT=/work/$D/dets-s5vit-$TAG.npz -v $PWD:/work -w /work cvpr19-gpu-g1:torch2.7.1-cu128 \
  bash -lc "pip install --user hdf5plugin omegaconf hydra-core einops StrEnum scipy >/tmp/pip.log 2>&1 || { echo PIP_FAILED; tail -15 /tmp/pip.log; exit 90; }; python3 -u /work/src/e66_fixedH_dump.py" || exit 1
python3 src/e66_gate.py $TAG $D/dets-s5vit-$TAG.npz --unit --ref experiments/e51_ranking/dets-s5vit-$TAG.npz | tee $D/gate-$TAG.log
python3 src/e66_verify.py $D/dets-s5vit-$TAG.npz experiments/e51_ranking/dets-s5vit-$TAG.npz | tee $D/verify-$TAG.log
