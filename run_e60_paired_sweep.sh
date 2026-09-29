#!/bin/bash
# The paired analysis at each shift amount. CPU only: the dumps are already on disk,
# so this claims no GPU and can run beside the E47d rows.
#
# SHIFT=5 runs first as a regression. The selection window was a fixed 16-20 block and
# is now the image of positions 0-3 under the rotation; at 5 the two are the same set,
# so paired-shift5.json must reproduce the stored paired.json on every measured field.
# If it does not, the generalisation changed the headline and the other amounts are
# withheld rather than reported beside a number that moved.
cd /media/hdd8/justin/my_project/CVPR20
run() {
  docker run --rm --memory=48g --user $(id -u):$(id -g) -e HOME=/tmp \
    -e SHIFT=$1 -v $PWD:/work -w /work cvpr19-gpu-g1:torch2.7.1-cu128 \
    python3 -u /work/src/e60_paired.py
}
run 5 || { echo "PAIRED_SHIFT5_FAILED"; exit 1; }
if python3 src/e60_paired_regress_check.py; then
  echo "PAIRED_REGRESSION_OK"
else
  echo "PAIRED_REGRESSION_DIFF the selection change moved the headline; other amounts withheld"
  exit 1
fi
for S in 0 10 15; do
  echo "=== paired SHIFT=$S $(date -u +%F' '%H:%M:%SZ)"
  run $S || { echo "PAIRED_SHIFT${S}_FAILED"; exit 1; }
done
echo "E60_PAIRED_SWEEP_DONE $(date -u +%F' '%H:%M:%SZ)"
