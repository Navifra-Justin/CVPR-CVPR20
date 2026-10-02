#!/bin/bash
# One E70 arm (1 Mpx), run as NSH sharded processes under the GPU queue lock and merged with the
# existing src/e65_merge_shards.py (sharding is an exact partition: state starts from None per sequence).
#
#   ./run_e70_arm.sh <gpu> <fam ssm|rvtc> <tag> <regime|-> <reset> <shift> <nshards> <outdir> [seqlist]
cd /media/hdd8/justin/my_project/CVPR20
G=$1; FAM=$2; TAG=$3; REG=$4; RST=$5; SH=$6; NSH=${7:-1}; D=$8; SL=$9
[ $FAM = ssm ] && M=s5vit-$TAG || M=rvt-$TAG
[ "$REG" = "-" ] && R="" || R="-$REG"
OUTF=$D/dets-$M$R-shift$SH.npz
[ -s "$OUTF" ] && { echo "skip $M$R shift$SH, already dumped"; exit 0; }
mkdir -p $D/parts; pids=""; parts=""
ENVSL=""; [ -n "$SL" ] && ENVSL="-e SEQLIST=/work/$SL"
for k in $(seq 0 $((NSH-1))); do
  P=$D/parts/$M$R-shift$SH-$k-of-$NSH.npz; parts="$parts $P"
  [ -s "$P" ] && { echo "shard $k present"; continue; }
  ( for att in 1 2 3; do
      flock /tmp/gpu${G}_queue.lock docker run --rm --gpus "\"device=$G\"" --memory=24g --user $(id -u):$(id -g) -e HOME=/tmp \
        -e DEV=cuda:0 -e FAM=$FAM -e TAG=$TAG -e RESET=$RST -e SHIFT=$SH -e CHUNK=10 \
        -e SHARD=$k -e NSHARD=$NSH -e OUT=/work/$P $ENVSL \
        -v $PWD:/work -w /work cvpr19-gpu-g1:torch2.7.1-cu128 \
        bash -lc "pip install --user hdf5plugin omegaconf hydra-core einops StrEnum scipy >/tmp/pip.log 2>&1 || { echo PIP_FAILED; tail -15 /tmp/pip.log; exit 90; }; nice -n 19 python3 -u /work/src/e70_1mpx_dump.py"
      rc=$?; [ $rc -eq 0 ] && [ -s "$P" ] && exit 0
      echo "shard $k of $M$R shift=$SH failed (attempt $att, rc=$rc); retry in 120s"; sleep 120
    done; exit 1 ) &
  pids="$pids $!"
done
rc=0; for p in $pids; do wait $p || rc=1; done
[ $rc -ne 0 ] && { echo "$M$R shift=$SH SHARD FAILED"; exit 1; }
if [ $NSH -eq 1 ]; then cp $parts $OUTF; else python3 src/e65_merge_shards.py $OUTF $parts || exit 1; fi
echo "WROTE $OUTF"
