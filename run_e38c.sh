#!/bin/bash
cd /media/hdd8/justin/my_project/CVPR20
docker run --rm --memory=48g --user $(id -u):$(id -g) -e HOME=/tmp -e LINE=200.0 -e SHAM=137.0 \
  -e OUTJ=/work/experiments/e38_empirical_null/local_excess_200.json \
  -v $PWD:/work -w /work cvpr19-gpu-g1:torch2.7.1-cu128 \
  bash -lc "pip install -q --user hdf5plugin 2>&1|tail -0; python3 -u /work/src/e38b_local_excess.py"
