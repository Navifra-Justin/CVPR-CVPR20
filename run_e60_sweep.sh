#!/bin/bash
# The chunk-position rotation read at four amounts instead of one.
#
# SHIFT=0 is the release's own boundary placement; its dumps already exist as
# experiments/e51_ranking/dets-s5vit-*.npz and are copied into the sweep's
# directory under the shift0 name rather than recomputed, so the zero arm is the
# same bytes the ranking experiment used. 5 is the amount E60 already ran. 10 and
# 15 are new. Each amount is verified from the index files before any GPU is
# claimed, by run_e60.sh's own gate.
#
# GPU 1 only. The runs are sequential; run_e60.sh waits for the card.
cd /media/hdd8/justin/my_project/CVPR20
mkdir -p experiments/e60_shift
for TAG in small base; do
  SRC=experiments/e51_ranking/dets-s5vit-$TAG.npz
  DST=experiments/e60_shift/dets-s5vit-$TAG-shift0.npz
  if [ -f "$SRC" ] && [ ! -e "$DST" ]; then
    ln "$SRC" "$DST" && echo "shift0 $TAG linked from the release dump"
  fi
done
for S in 5 10 15; do
  echo "=== SHIFT=$S $(date -u +%F' '%H:%M:%SZ)"
  SHIFT=$S ./run_e60.sh || { echo "SHIFT=$S failed"; exit 1; }
done
echo "E60_SWEEP_DUMPS_DONE $(date -u +%F' '%H:%M:%SZ)"
