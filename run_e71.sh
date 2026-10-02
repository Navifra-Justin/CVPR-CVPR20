#!/bin/bash
# E71: fixed-H dump at H = 21 (regression), 40, 80 on the 3000 stratified frames (r+1 >= 80), five Gen1 checkpoints, GPU 0 queue.
#   setsid nohup ./run_e71.sh > logs_e71.log 2>&1 < /dev/null &
# H = 1, 5, 10, 21 columns on the same frames are taken from the E66 dumps (same per-frame computation, same frame ids);
# H = 21 is recomputed here as the regression check of this dumper (src/e71_check.py). Resumable per sequence (parts dir).
cd /media/hdd8/justin/my_project/CVPR20
OUTD=experiments/e71_h4080; mkdir -p $OUTD
GPU=${GPU:-0}
ORDER=${ORDER:-fwd}   # fwd | rev: two runners (GPU 0 fwd, GPU 1 rev) never take the same model (mkdir claim)
WAIT_UNTIL=${WAIT_UNTIL:-}   # epoch seconds; GPU 1 runner waits for 2026-10-03 00:00 KST and an idle card
gpu_run() {  # gpu_run <fam> <tag> <batch> <name>
  local FAM=$1 TAG=$2 BS=$3 NAME=$4
  flock /tmp/gpu${GPU}_queue.lock docker run --rm --name cvpr20_e71_${NAME}_$$ --gpus "\"device=$GPU\"" --memory=24g --user $(id -u):$(id -g) -e HOME=/tmp \
    -e DEV=cuda:0 -e FAM=$FAM -e TAG=$TAG -e NSEQ=1000 -e HS=21,40,80 -e BATCH=$BS -e PROBE=2 \
    -e FRAMES=/work/$OUTD/frames.npz -e OUT=/work/$OUTD/dets-$NAME.npz -v $PWD:/work -w /work cvpr19-gpu-g1:torch2.7.1-cu128 \
    bash -lc "pip install --user hdf5plugin omegaconf hydra-core einops StrEnum scipy >/tmp/pip.log 2>&1 || { echo PIP_FAILED; tail -15 /tmp/pip.log; exit 90; }; nice -n 19 python3 -u /work/src/e71_dump.py"
}
LIST=("rvt b 16" "ssm base 2" "rvt s 16" "ssm small 2" "rvt t 16")
[ "$ORDER" = rev ] && LIST=("rvt t 16" "ssm small 2" "rvt s 16" "ssm base 2" "rvt b 16")
if [ -n "$WAIT_UNTIL" ]; then
  while [ $(date +%s) -lt $WAIT_UNTIL ]; do sleep 60; done
  while [ $(nvidia-smi --id=$GPU --query-gpu=memory.used --format=csv,noheader,nounits | head -1) -ge 500 ]; do sleep 120; done
fi
for M in "${LIST[@]}"; do
  set -- $M; FAM=$1; TAG=$2; BS=$3
  NAME=$([ $FAM = rvt ] && echo rvt-$TAG || echo s5vit-$TAG)
  [ -s $OUTD/dets-$NAME.npz ] || mkdir $OUTD/.claim-$NAME 2>/dev/null || { echo "$NAME claimed by the other runner"; continue; }
  for try in 1 2 3; do
    [ -s $OUTD/dets-$NAME.npz ] && break
    echo "=== $NAME attempt $try $(date -u +%H:%M:%SZ)"
    gpu_run $FAM $TAG $BS $NAME
    echo "$NAME attempt $try exit=$? $(date -u +%H:%M:%SZ)"
  done
  if [ -s $OUTD/dets-$NAME.npz ]; then
    python3 src/e66_verify.py $OUTD/dets-$NAME.npz | tee $OUTD/verify-$NAME.log
    python3 src/e71_check.py $NAME $OUTD/dets-$NAME.npz | tee $OUTD/check-$NAME.log
  fi
done
echo "E71_DUMPS_DONE $(date -u +%H:%M:%SZ)"
