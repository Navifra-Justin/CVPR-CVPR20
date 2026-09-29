#!/bin/bash
# E47b driven over both families. GPU 1 only: this machine's GPU 0 is not ours to
# use, so the launcher waits for GPU 1 rather than taking whichever card is free.
#
# The first job is a regression: FAM=ssm TAG=small must reproduce
# experiments/e47_ssm/s5vit-small-chunked.json, which was produced before the
# family switch was added. If it does not, the refactor changed the measurement
# and the RVT rows below are not comparable to the stored SSM rows.
cd /media/hdd8/justin/my_project/CVPR20
mkdir -p experiments/e47_ssm/regress
run() {  # run <FAM> <TAG> <outdir-tag>
  while true; do
    f1=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | sed -n 2p)
    if [ "$f1" -ge 9000 ]; then
      docker run --rm --gpus '"device=1"' --memory=32g --user $(id -u):$(id -g) -e HOME=/tmp \
        -e DEV=cuda:0 -e FAM=$1 -e TAG=$2 -e NSEQ=12 -e NCHUNK=6 -e CHUNK=8 -v $PWD:/work -w /work \
        cvpr19-gpu-g1:torch2.7.1-cu128 \
        bash -lc "pip install -q --user hdf5plugin omegaconf hydra-core einops StrEnum scipy 2>&1|tail -0; python3 -u /work/src/e47b_ssm_chunked.py"
      rc=$?; echo "[$(date +%F' '%H:%M:%S)] FAM=$1 TAG=$2 exit=$rc"
      [ $rc -eq 0 ] && return 0
      echo "  retry in 300s"; sleep 300
    else sleep 60; fi
  done
}

# The reference profile is the one produced before the family switch existed; it is
# written once and never overwritten, so a later run cannot quietly redefine it.
[ -f experiments/e47_ssm/regress/s5vit-small-chunked.before.json ] || \
  cp experiments/e47_ssm/s5vit-small-chunked.json \
     experiments/e47_ssm/regress/s5vit-small-chunked.before.json

# Re-run the SSM arm only if the profile on disk was not already produced by the
# refactored driver; the gate itself is what decides, not the file's timestamp.
python3 src/e47d_regress_check.py >/dev/null 2>&1 || run ssm small
if python3 src/e47d_regress_check.py; then
  echo "REGRESSION_OK the family switch reproduces the stored SSM measurement"
else
  echo "REGRESSION_DIFF the family switch changed the SSM profile; RVT rows withheld"
  exit 1
fi

for T in t s b; do run rvt $T; done
echo "E47D_DONE"
