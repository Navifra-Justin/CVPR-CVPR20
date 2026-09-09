#!/bin/bash
cd /media/hdd8/justin/my_project/CVPR20
for TAG in s b t; do
  echo "=================== rvt-$TAG $(date +%H:%M:%S)"
  while true; do
    read f0 f1 <<< $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | tr '\n' ' ')
    if [ "$f0" -ge 12000 ] || [ "$f1" -ge 12000 ]; then
      if [ "$f0" -ge "$f1" ]; then G=0; else G=1; fi
      docker run --rm --gpus "\"device=$G\"" --memory=32g --user $(id -u):$(id -g) -e HOME=/tmp \
        -e DEV=cuda:0 -e TAG=$TAG -e NSEQ=12 -e NSAMP=40 -e KLAG=19 -v $PWD:/work -w /work \
        cvpr19-gpu-g1:torch2.7.1-cu128 \
        bash -lc "pip install -q --user hdf5plugin omegaconf hydra-core einops StrEnum 2>&1|tail -0; python3 -u /work/src/e44_capacity_support.py"
      rc=$?; echo "rvt-$TAG exit=$rc"; [ $rc -eq 0 ] && break
      echo "retry in 300s"; sleep 300
    else sleep 60; fi
  done
done
echo "ALL DONE $(date +%H:%M:%S)"
