#!/bin/bash
# One E65 arm, run as NSH sharded processes and merged. src/e65_shard_selftest.sh establishes
# that the merge of a sharded run is element-for-element the single-process dump, so this is
# a scheduling change and not a change to the measurement.
#
#   ./run_e65_shard_arm.sh <gpu> <tag> <regime> <reset> <shift> <nshards>
cd /media/hdd8/justin/my_project/CVPR20
G=$1; TAG=$2; REG=$3; RST=$4; SH=$5; NSH=${6:-3}
D=experiments/e65_rvt_boundary
OUTF=$D/dets-rvt-$TAG-$REG-shift$SH.npz
[ -s "$OUTF" ] && { echo "skip $TAG $REG shift$SH, already dumped"; exit 0; }
mkdir -p $D/parts
pids=""; parts=""
for k in $(seq 0 $((NSH-1))); do
  P=$D/parts/rvt-$TAG-$REG-shift$SH-$k-of-$NSH.npz
  parts="$parts $P"
  if [ -s "$P" ]; then echo "shard $k already present"; continue; fi
  # Retry. The first unsharded SHIFT=0 arm died at sequence 226 inside the HDF5 blosc filter
  # ("filter returned failure during read") while the host had about 2 GB free, on a file that
  # a second process read successfully minutes later; the read is transient under memory
  # pressure, not a corrupt file, so the shard is retried rather than abandoned.
  ( for att in 1 2 3; do
      docker run --rm --gpus "\"device=$G\"" --memory=32g --user $(id -u):$(id -g) -e HOME=/tmp \
        -e DEV=cuda:0 -e FAM=rvtc -e TAG=$TAG -e RESET=$RST -e SHIFT=$SH -e CHUNK=21 \
        -e SHARD=$k -e NSHARD=$NSH -e OUT=/work/$P \
        -v $PWD:/work -w /work cvpr19-gpu-g1:torch2.7.1-cu128 \
        bash -lc "pip install --user hdf5plugin omegaconf hydra-core einops StrEnum scipy >/tmp/pip.log 2>&1 || { echo PIP_FAILED; tail -15 /tmp/pip.log; exit 90; }; python3 -u /work/src/e51_dump_all.py"
      rc=$?
      [ $rc -eq 0 ] && [ -s "$P" ] && exit 0
      echo "shard $k of $NSH for rvt-$TAG $REG shift=$SH failed (attempt $att, rc=$rc); retrying in 180s"
      sleep 180
    done
    exit 1 ) &
  pids="$pids $!"
done
rc=0
for p in $pids; do wait $p || rc=1; done
if [ $rc -ne 0 ]; then echo "rvt-$TAG $REG shift=$SH SHARD FAILED"; exit 1; fi
for P in $parts; do [ -s "$P" ] || { echo "rvt-$TAG $REG shift=$SH missing shard $P"; exit 1; }; done
python3 src/e65_merge_shards.py $OUTF $parts || exit 1
echo "rvt-$TAG $REG shift=$SH merged into place $(date -u +%H:%M:%SZ)"
