#!/bin/bash
# The two SSM dumps. The chunk of 21 windows the release evaluates with is a real batch, so
# this waits for a card with room rather than taking one from whoever is already on it.
cd /media/hdd8/justin/my_project/CVPR20
NEED=12000
for TAG in small base; do
  while true; do
    read f0 f1 <<< $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | tr '\n' ' ')
    if [ "$f0" -ge "$NEED" ] || [ "$f1" -ge "$NEED" ]; then
      if [ "$f0" -ge "$f1" ]; then G=0; else G=1; fi
      echo "starting ssm/$TAG on GPU$G (free: $f0 / $f1 MiB)"
      docker run --rm --gpus "\"device=$G\"" --memory=32g --user $(id -u):$(id -g) -e HOME=/tmp \
        -e DEV=cuda:0 -e FAM=ssm -e TAG=$TAG -v $PWD:/work -w /work \
        cvpr19-gpu-g1:torch2.7.1-cu128 \
        bash -lc "pip install -q --user hdf5plugin omegaconf hydra-core einops StrEnum scipy 2>&1|tail -0; python3 -u /work/src/e51_dump_all.py"
      rc=$?; echo "FAM=ssm TAG=$TAG exit=$rc"; [ $rc -eq 0 ] && break
      echo "retry in 300s"; sleep 300
    else sleep 120; fi
  done
done
