#!/bin/bash
# E65, one arm, run out of band so that arms that do not depend on each other can share the
# two cards instead of queueing behind run_e65.sh. Same container, same environment and the
# same output path as run_e65.sh; the only difference is that the dump is written to a
# temporary file and moved into place atomically, and that the final path is created empty
# first so a concurrent run_e65.sh skips the arm instead of duplicating it.
#
#   ./run_e65_one.sh <gpu> <tag> <regime> <reset> <shift>
cd /media/hdd8/justin/my_project/CVPR20
G=$1; TAG=$2; REG=$3; RST=$4; SH=$5
OUTF=experiments/e65_rvt_boundary/dets-rvt-$TAG-$REG-shift$SH.npz
TMPF=experiments/e65_rvt_boundary/.tmp-rvt-$TAG-$REG-shift$SH.npz
mkdir -p experiments/e65_rvt_boundary
[ -s "$OUTF" ] && { echo "skip $TAG $REG shift$SH, already dumped"; exit 0; }
: > "$OUTF"
echo "=== rvt-$TAG $REG shift=$SH on GPU$G (out of band) $(date -u +%H:%M:%SZ)"
docker run --rm --gpus "\"device=$G\"" --memory=32g --user $(id -u):$(id -g) -e HOME=/tmp \
  -e DEV=cuda:0 -e FAM=rvtc -e TAG=$TAG -e RESET=$RST -e SHIFT=$SH -e CHUNK=21 \
  -e OUT=/work/$TMPF \
  -v $PWD:/work -w /work cvpr19-gpu-g1:torch2.7.1-cu128 \
  bash -lc "pip install --user hdf5plugin omegaconf hydra-core einops StrEnum scipy >/tmp/pip.log 2>&1 || { echo PIP_FAILED; tail -15 /tmp/pip.log; exit 90; }; python3 -u /work/src/e51_dump_all.py"
rc=$?
if [ $rc -eq 0 ] && [ -s "$TMPF" ]; then
  mv -f "$TMPF" "$OUTF"; echo "rvt-$TAG $REG shift=$SH exit=0 moved into place $(date -u +%H:%M:%SZ)"
else
  rm -f "$OUTF"; echo "rvt-$TAG $REG shift=$SH exit=$rc FAILED, placeholder removed $(date -u +%H:%M:%SZ)"
fi
exit $rc
