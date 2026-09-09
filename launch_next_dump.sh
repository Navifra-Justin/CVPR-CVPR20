#!/bin/bash
# Launch the next missing dump as a DETACHED container and exit immediately.
# The queue shells kept being killed when the shared machine ran low on host memory while
# the containers themselves survived, so nothing long-lived is held here: one call starts at
# most one container, and calling it again after that container exits starts the next.
cd /media/hdd8/justin/my_project/CVPR20
if [ "$(docker ps -q --filter ancestor=cvpr19-gpu-g1:torch2.7.1-cu128 | wc -l)" -gt 0 ]; then
  for c in $(docker ps -q --filter ancestor=cvpr19-gpu-g1:torch2.7.1-cu128); do
    echo "busy: $(docker inspect -f '{{index .Config.Env 2}} {{index .Config.Env 3}}' $c) — $(docker logs --tail 1 $c 2>&1 | tail -1)"
  done
  exit 0
fi
read f0 f1 <<< $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | tr '\n' ' ')
hostfree=$(free -m | awk '/^메모리:|^Mem:/{print $7}')
if [ "${hostfree:-0}" -lt 16000 ]; then echo "host memory low (${hostfree} MiB) — not starting"; exit 0; fi
if [ "$f0" -lt 12000 ] && [ "$f1" -lt 12000 ]; then echo "no GPU with room ($f0 / $f1 MiB)"; exit 0; fi
if [ "$f0" -ge "$f1" ]; then G=0; else G=1; fi
for SPEC in rvt:t rvt:s rvt:b ssm:small ssm:base; do
  FAM=${SPEC%%:*}; TAG=${SPEC##*:}
  if [ "$FAM" = "rvt" ]; then NM="rvt-$TAG"; else NM="s5vit-$TAG"; fi
  [ -f "experiments/e51_ranking/dets-$NM.npz" ] && continue
  echo "starting $NM on GPU$G (gpu $f0/$f1 MiB, host $hostfree MiB) $(date -u +%H:%M:%SZ)"
  docker run -d --rm --gpus "\"device=$G\"" --memory=6g --user $(id -u):$(id -g) -e HOME=/tmp \
    -e DEV=cuda:0 -e FAM=$FAM -e TAG=$TAG -v $PWD:/work -w /work \
    cvpr19-gpu-g1:torch2.7.1-cu128 \
    bash -lc "pip install -q --user hdf5plugin omegaconf hydra-core einops StrEnum scipy 2>&1|tail -0; python3 -u /work/src/e51_dump_all.py" > /dev/null
  echo "launched detached"
  exit 0
done
echo "ALLDONE - every dump present"
