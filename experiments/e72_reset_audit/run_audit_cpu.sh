#!/bin/bash
# E72 reset-policy audit, CPU container (nice 19). usage: run_audit_cpu.sh <fam> <tag> [NSEQ] [NCHUNK]
cd /media/hdd8/justin/my_project/CVPR20
FAM=$1; TAG=$2; NS=${3:-8}; NC=${4:-4}
nice -n 19 docker run --rm --name cvpr20_e72_${FAM}_${TAG}_$$ --cpus=${CPUS:-6} --cpu-shares=32 --memory=${MEM:-12g} --user $(id -u):$(id -g) -e HOME=/tmp \
  -e FAM=$FAM -e TAG=$TAG -e NSEQ=$NS -e NCHUNK=$NC -e THREADS=${CPUS:-6} -e PYTHONPATH=/work/experiments/e72_reset_audit/third_party/psee_adt \
  -v $PWD:/work -w /work cvpr19-gpu-g1:torch2.7.1-cu128 bash -lc "pip install --user pyyaml pandas tqdm scipy psutil tabulate pycocotools opencv-python-headless scikit-learn loguru thop hdf5plugin omegaconf hydra-core einops StrEnum >/tmp/pip.log 2>&1 || { echo PIP_FAILED; exit 90; }; nice -n 19 python3 -u src/e72_audit.py"
