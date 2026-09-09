#!/bin/bash
# Queue A on GPU0: the three RVT capacities, one window per call.
cd /media/hdd8/justin/my_project/CVPR20
for TAG in t s b; do
  docker run --rm --gpus '"device=0"' --memory=32g --user $(id -u):$(id -g) -e HOME=/tmp \
    -e DEV=cuda:0 -e FAM=rvt -e TAG=$TAG -v $PWD:/work -w /work \
    cvpr19-gpu-g1:torch2.7.1-cu128 \
    bash -lc "pip install -q --user hdf5plugin omegaconf hydra-core einops StrEnum scipy 2>&1|tail -0; python3 -u /work/src/e51_dump_all.py"
  echo "FAM=rvt TAG=$TAG exit=$?"
done
