#!/bin/bash
# E66 Support-Conditioned AP: full fixed-H dump of all five released Gen1 checkpoints on GPU 1.
#
#   setsid nohup ./run_e66.sh > logs_e66.log 2>&1 < /dev/null &
#
# Order: wait for the running GPU-1 jobs (CVPR8 jolly_curran and the CVPR20 E65 chain), then
#   0. short GPU regression gate (rvt-s, 12 sequences, BATCH=1): e66 H=p+1 vs E65 reset-shift0 at
#      position p, same device so the log also reports the bit-identical count; the enforced criterion is the
#      detection-wise unit match (src/e66_gate.py --unit);
#      the full run is withheld if it fails
#   1. the five dumps, each under `flock /tmp/gpu1_queue.lock docker run ...`, resumable per sequence
#      (parts dir), three attempts each
#   2. CPU evaluation (nice 19, one process): src/e66_eval.py
# Per model: 20,296 frames x (1+5+10+21) windows = 751,000 window forwards (the release dump is
# 385,638), batched over 16 frames (8 for SSM-ViT, whose chunk is a (H,B) tensor).
cd /media/hdd8/justin/my_project/CVPR20
OUTD=experiments/e66_fixedH; mkdir -p $OUTD

gpu_run() {  # gpu_run <fam> <tag> <extra env...>
  local FAM=$1 TAG=$2; shift 2
  flock /tmp/gpu1_queue.lock docker run --rm --gpus '"device=1"' --memory=32g --user $(id -u):$(id -g) -e HOME=/tmp \
    -e DEV=cuda:0 -e FAM=$FAM -e TAG=$TAG "$@" -v $PWD:/work -w /work cvpr19-gpu-g1:torch2.7.1-cu128 \
    bash -lc "pip install --user hdf5plugin omegaconf hydra-core einops StrEnum scipy >/tmp/pip.log 2>&1 || { echo PIP_FAILED; tail -15 /tmp/pip.log; exit 90; }; python3 -u /work/src/e66_fixedH_dump.py"
}

# 0. gate
mkdir -p $OUTD/gate_gpu
for try in 1 2 3; do
  [ -s $OUTD/gate_gpu/dets-rvt-s.npz ] && break
  gpu_run rvt s -e NSEQ=12 -e STRIDE=3 -e HS=1,5,10,21 -e BATCH=1 -e PROBE=2 -e OUT=/work/$OUTD/gate_gpu/dets-rvt-s.npz
done
python3 src/e66_gate.py s $OUTD/gate_gpu/dets-rvt-s.npz --unit | tee $OUTD/gate_gpu/gate-s.log
[ ${PIPESTATUS[0]} -eq 0 ] || { echo "E66 GPU gate FAILED; full dump withheld"; exit 1; }
python3 src/e66_verify.py $OUTD/gate_gpu/dets-rvt-s.npz experiments/e65_rvt_boundary/dets-rvt-s-reset-shift0.npz | tee $OUTD/gate_gpu/verify-s.log
[ ${PIPESTATUS[0]} -eq 0 ] || { echo "E66 audit FAILED; full dump withheld"; exit 1; }
# 0b. the production path is batched: same gate with BATCH=16
mkdir -p $OUTD/gate_gpu16
for try in 1 2 3; do
  [ -s $OUTD/gate_gpu16/dets-rvt-s.npz ] && break
  gpu_run rvt s -e NSEQ=12 -e STRIDE=3 -e HS=1,5,10,21 -e BATCH=16 -e OUT=/work/$OUTD/gate_gpu16/dets-rvt-s.npz
done
python3 src/e66_gate.py s $OUTD/gate_gpu16/dets-rvt-s.npz --unit | tee $OUTD/gate_gpu16/gate-s.log
[ ${PIPESTATUS[0]} -eq 0 ] || { echo "E66 batched GPU gate FAILED; full dump withheld"; exit 1; }

# 1. full dumps (headline pair first: one ConvLSTM and one S5 of the same width class)
for M in "rvt s" "ssm small" "rvt b" "ssm base" "rvt t"; do
  set -- $M; FAM=$1; TAG=$2
  NAME=$([ $FAM = rvt ] && echo rvt-$TAG || echo s5vit-$TAG)
  for try in 1 2 3; do
    [ -s $OUTD/dets-$NAME.npz ] && break
    echo "=== $NAME attempt $try $(date -u +%H:%M:%SZ)"
    gpu_run $FAM $TAG -e NSEQ=1000 -e HS=1,5,10,21 -e PROBE=1 -e OUT=/work/$OUTD/dets-$NAME.npz
    echo "$NAME attempt $try exit=$? $(date -u +%H:%M:%SZ)"
  done
  [ -s $OUTD/dets-$NAME.npz ] && python3 src/e66_verify.py $OUTD/dets-$NAME.npz experiments/e51_ranking/dets-$NAME.npz | tee $OUTD/verify-$NAME.log
done

# 2. evaluation (CPU, one process, lowest priority)
nice -n 19 env B=200 python3 src/e66_eval.py | tee $OUTD/eval.log
echo "E66_DONE $(date -u +%H:%M:%SZ)"
