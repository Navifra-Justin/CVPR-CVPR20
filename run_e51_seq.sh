#!/bin/bash
# One dump at a time. Two 32 GB containers plus other users exhausted host RAM and the
# harness killed both queues, so this runs strictly sequentially with a modest cap and
# resumes by skipping any model whose dump already exists.
cd /media/hdd8/justin/my_project/CVPR20
NEED=12000
HOSTNEED=12000
for SPEC in rvt:t rvt:s rvt:b ssm:small ssm:base; do
  FAM=${SPEC%%:*}; TAG=${SPEC##*:}
  if [ "$FAM" = "rvt" ]; then NM="rvt-$TAG"; else NM="s5vit-$TAG"; fi
  if [ -f "experiments/e51_ranking/dets-$NM.npz" ]; then echo "skip $NM, already dumped"; continue; fi
  while true; do
    read f0 f1 <<< $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | tr '\n' ' ')
    # the machine is shared and was out of host RAM once already; wait for both resources
    hostfree=$(free -m | awk '/^메모리:|^Mem:/{print $7}')
    if [ "${hostfree:-0}" -lt "$HOSTNEED" ]; then sleep 120; continue; fi
    if [ "$f0" -ge "$NEED" ] || [ "$f1" -ge "$NEED" ]; then
      if [ "$f0" -ge "$f1" ]; then G=0; else G=1; fi
      echo "=== $NM on GPU$G (gpu free $f0 / $f1 MiB, host free $hostfree MiB) $(date -u +%H:%M:%SZ)"
      docker run --rm --gpus "\"device=$G\"" --memory=8g --user $(id -u):$(id -g) -e HOME=/tmp \
        -e DEV=cuda:0 -e FAM=$FAM -e TAG=$TAG -v $PWD:/work -w /work \
        cvpr19-gpu-g1:torch2.7.1-cu128 \
        bash -lc "pip install -q --user hdf5plugin omegaconf hydra-core einops StrEnum scipy 2>&1|tail -0; python3 -u /work/src/e51_dump_all.py"
      rc=$?; echo "$NM exit=$rc"
      [ $rc -eq 0 ] && break
      echo "retry in 300s"; sleep 300
    else sleep 120; fi
  done
done
echo ALLDONE
