#!/bin/bash
cd /media/hdd8/justin/my_project/CVPR20
runc () {  # $1 family  $2 tag
  while true; do
    read f0 f1 <<< $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | tr '\n' ' ')
    if [ "$f0" -ge 9000 ] || [ "$f1" -ge 9000 ]; then
      if [ "$f0" -ge "$f1" ]; then G=0; else G=1; fi
      docker run --rm --gpus "\"device=$G\"" --memory=32g --user $(id -u):$(id -g) -e HOME=/tmp \
        -e DEV=cuda:0 -e FAM=$1 -e TAG=$2 -e NSEQ=12 -e NCHUNK=6 -e CHUNK=8 -v $PWD:/work -w /work \
        cvpr19-gpu-g1:torch2.7.1-cu128 \
        bash -lc "pip install -q --user hdf5plugin omegaconf hydra-core einops StrEnum scipy 2>&1|tail -0; python3 -u /work/src/e47c_state_by_position.py"
      rc=$?; echo "FAM=$1 TAG=$2 exit=$rc"; [ $rc -eq 0 ] && break
      echo "retry in 300s"; sleep 300
    else sleep 60; fi
  done
}
runc ssm small
runc rvt t
runc ssm base
