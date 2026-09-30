#!/bin/bash
# E65 - the chunk-boundary intervention applied to RVT, in two state regimes.
#
# E60 ran this intervention on SSM-ViT, whose carried state is provably inert across chunks,
# and measured a large within-frame gain. The mechanism that explains it predicts the
# opposite for RVT, whose validation state crosses chunk boundaries in the release
# (modules/detection.py keeps it in mode_2_rnn_states and clears it only on the first
# sample). Sec. 5 of the manuscript already leans on that prediction when it differences the
# observational contrast against the RVT checkpoints. This measures it instead of assuming.
#
# Four arms per checkpoint: {carry, reset} x SHIFT {0, 5}.
#   carry  RESET=0, the released behaviour.
#   reset  RESET=1, the state dropped at every chunk start. This is the positive control of
#          the design: it puts RVT in the condition the SSM release is already in, so it
#          shows the shift really reaches the model and a null in `carry` is a fact about
#          the release rather than a driver that dropped the treatment.
#
# GPU is a parameter: both cards on this machine are shared, so the arm waits for whichever
# one it was given rather than assuming it is free.
#
#   ./run_e65.sh <gpu> <tag>
cd /media/hdd8/justin/my_project/CVPR20
G=${1:-0}; TAG=${2:-s}
NEED=9000; HOSTNEED=16000
mkdir -p experiments/e65_rvt_boundary

run() {  # run <regime> <reset> <shift>
  local REG=$1 RST=$2 SH=$3
  local HOSTOUT=experiments/e65_rvt_boundary/dets-rvt-$TAG-$REG-shift$SH.npz
  if [ -f "$HOSTOUT" ]; then echo "skip $TAG $REG shift$SH, already dumped"; return 0; fi
  while true; do
    free1=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i $G)
    hostfree=$(free -m | awk '/^메모리:|^Mem:/{print $7}')
    if [ "${free1:-0}" -ge "$NEED" ] && [ "${hostfree:-0}" -ge "$HOSTNEED" ]; then
      echo "=== rvt-$TAG $REG shift=$SH on GPU$G (gpu free ${free1} MiB) $(date -u +%H:%M:%SZ)"
      # h5py arrives with hdf5plugin from this pip install and is not in the image; keep the
      # log and exit 90 on a dependency failure so the retry is known to be retrying a
      # download and not re-running broken code.
      docker run --rm --gpus "\"device=$G\"" --memory=32g --user $(id -u):$(id -g) -e HOME=/tmp \
        -e DEV=cuda:0 -e FAM=rvtc -e TAG=$TAG -e RESET=$RST -e SHIFT=$SH -e CHUNK=21 \
        -e OUT=/work/$HOSTOUT \
        -v $PWD:/work -w /work cvpr19-gpu-g1:torch2.7.1-cu128 \
        bash -lc "pip install --user hdf5plugin omegaconf hydra-core einops StrEnum scipy >/tmp/pip.log 2>&1 || { echo PIP_FAILED; tail -15 /tmp/pip.log; exit 90; }; python3 -u /work/src/e51_dump_all.py"
      rc=$?; echo "rvt-$TAG $REG shift=$SH exit=$rc $(date -u +%H:%M:%SZ)"
      [ $rc -eq 0 ] && return 0
      echo "retry in 300s"; sleep 300
    else
      sleep 120
    fi
  done
}

# SHIFT=0 first, both regimes: those two are what src/e65_regress_check.py needs to decide
# whether the chunked driver is the same instrument as the per-window one and whether the
# RESET flag is live. If that gate fails the shifted arms are not worth the card.
run carry 0 0
run reset 1 0
python3 src/e65_regress_check.py $TAG | tee experiments/e65_rvt_boundary/regress-$TAG.log
if [ "${PIPESTATUS[0]}" -ne 0 ]; then echo "E65 regression gate failed for rvt-$TAG; shifted arms withheld"; exit 1; fi

run carry 0 5
run reset 1 5
echo "E65_DONE rvt-$TAG $(date -u +%H:%M:%SZ)"
