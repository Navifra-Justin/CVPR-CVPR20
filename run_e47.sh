#!/bin/bash
# The bin arm first for both capacities, since the centroid is what the paper's generality
# claim rests on; then the support arm at a 500 ms horizon, which is the E44 column it is
# compared against and costs a quarter of the 1 s one.
cd /media/hdd8/justin/my_project/CVPR20
run () {  # $1 tag  $2 mode  $3 klag
  while true; do
    read f0 f1 <<< $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | tr '\n' ' ')
    if [ "$f0" -ge 9000 ] || [ "$f1" -ge 9000 ]; then
      if [ "$f0" -ge "$f1" ]; then G=0; else G=1; fi
      docker run --rm --gpus "\"device=$G\"" --memory=32g --user $(id -u):$(id -g) -e HOME=/tmp \
        -e DEV=cuda:0 -e TAG=$1 -e MODE=$2 -e KLAG=$3 -e NSEQ=12 -e NSAMP=40 -v $PWD:/work -w /work \
        cvpr19-gpu-g1:torch2.7.1-cu128 \
        bash -lc "pip install -q --user hdf5plugin omegaconf hydra-core einops StrEnum scipy 2>&1|tail -0; python3 -u /work/src/e47_ssm_support.py"
      rc=$?; echo "TAG=$1 MODE=$2 exit=$rc"; [ $rc -eq 0 ] && break
      echo "retry in 300s"; sleep 300
    else sleep 60; fi
  done
}
run small bins 0
run base  bins 0
run small support 9
run base  support 9
