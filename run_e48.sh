#!/bin/bash
cd /media/hdd8/justin/my_project/CVPR20
for TAG in t s b; do
  while true; do
    read f0 f1 <<< $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | tr '\n' ' ')
    if [ "$f0" -ge 9000 ] || [ "$f1" -ge 9000 ]; then
      G=1
      docker run --rm --gpus "\"device=$G\"" --memory=32g --user $(id -u):$(id -g) -e HOME=/tmp \
        -e DEV=cuda:0 -e TAG=$TAG -e NSEQ=12 -e NSAMP=40 -v $PWD:/work -w /work \
        cvpr19-gpu-g1:torch2.7.1-cu128 \
        bash -lc "pip install -q --user hdf5plugin omegaconf hydra-core einops StrEnum 2>&1|tail -0; python3 -u /work/src/e48_rvt_bins.py"
      rc=$?; echo "TAG=$TAG exit=$rc"; [ $rc -eq 0 ] && break
      echo "retry in 300s"; sleep 300
    else sleep 60; fi
  done
done
