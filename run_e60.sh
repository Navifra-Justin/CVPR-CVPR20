#!/bin/bash
# E60 - the paired chunk-position experiment.
#
# E58 compared frames that sat at different positions in the release's streaming chunk, and
# controlled for scene content with RVT. That control rests on parallel trends. This removes
# the need for it: the same SSM checkpoints are re-run with every chunk boundary moved 5
# windows LATER, which rotates every position by -5 and so carries the release's starved
# block, positions 0-3, onto 16-19. A frame the release gave one to four windows of history
# is scored again with seventeen to twenty. The comparison is then within model and within
# frame, and no control is required.
#
# Five later, not sixteen earlier. src/e60_verify_shift.py checks the re-assignment from the
# index files before any GPU is claimed; the earlier-by-16 variant that ran first left 73.5 %
# of frames at the position they already had, because the release's own start is already
# max(first_label - 20, 0) and is pinned at 0 for most Gen1 sequences.
#
# Only GPU 1 may be used on this machine, so this waits for GPU 1 specifically rather than
# taking whichever card is free.
cd /media/hdd8/justin/my_project/CVPR20
NEED=12000; HOSTNEED=16000; G=1
SHIFT=5

# Verify the treatment before spending the card on it. This reads only the index files, needs
# no GPU, and exits non-zero unless every covered frame's position rotates by exactly SHIFT.
echo "=== verifying the shift re-assignment (no GPU) $(date -u +%H:%M:%SZ)"
docker run --rm --memory=16g --user $(id -u):$(id -g) -e HOME=/tmp -e SHIFT=$SHIFT \
  -v $PWD:/work -w /work cvpr19-gpu-g1:torch2.7.1-cu128 \
  python3 -u /work/src/e60_verify_shift.py | tee experiments/e60_shift/verify-shift$SHIFT.log
if [ "${PIPESTATUS[0]}" -ne 0 ]; then echo "shift verification failed, not claiming GPU"; exit 1; fi

for TAG in small base; do
  OUT=/work/experiments/e60_shift/dets-s5vit-$TAG-shift$SHIFT.npz
  HOSTOUT=experiments/e60_shift/dets-s5vit-$TAG-shift$SHIFT.npz
  if [ -f "$HOSTOUT" ]; then echo "skip $TAG, already dumped"; continue; fi
  while true; do
    free1=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i $G)
    hostfree=$(free -m | awk '/^메모리:|^Mem:/{print $7}')
    if [ "${free1:-0}" -ge "$NEED" ] && [ "${hostfree:-0}" -ge "$HOSTNEED" ]; then
      echo "=== s5vit-$TAG shift=$SHIFT on GPU$G (gpu free ${free1} MiB, host free ${hostfree} MiB) $(date -u +%H:%M:%SZ)"
      docker run --rm --gpus "\"device=$G\"" --memory=32g --user $(id -u):$(id -g) -e HOME=/tmp \
        -e DEV=cuda:0 -e FAM=ssm -e TAG=$TAG -e SHIFT=$SHIFT -e OUT=$OUT \
        -v $PWD:/work -w /work cvpr19-gpu-g1:torch2.7.1-cu128 \
        bash -lc "pip install -q --user hdf5plugin omegaconf hydra-core einops StrEnum scipy 2>&1|tail -0; python3 -u /work/src/e51_dump_all.py"
      rc=$?; echo "TAG=$TAG exit=$rc $(date -u +%H:%M:%SZ)"
      [ $rc -eq 0 ] && break
      echo "retry in 300s"; sleep 300
    else
      sleep 120
    fi
  done
done
echo "E60 dumps complete $(date -u +%H:%M:%SZ)"
