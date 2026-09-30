#!/bin/bash
# The four SHIFT=5 arms of E65. Launched in two batches; the outer loop was then killed by PID
# and the reset pair started out of band once GPU 0 turned out to hold only about 0.8 GB per
# shard, so all four arms could run at once. Kept for the record of how the carry pair started.
#
# The four SHIFT=5 arms of E65, in two batches. GPU 1 held 29 of its 32 GB for another user's
# job when this was launched, so every shard goes to GPU 0 and the batch size is set by GPU 0's
# free memory (about 24 GB, and a shard holds roughly 4 GB) rather than by the host's cores.
# The regression gate passed on both tags before this ran (experiments/e65_rvt_boundary/regress-*.log).
cd /media/hdd8/justin/my_project/CVPR20
NSH=${1:-2}
set -x
for BATCH in carry reset; do
  RST=0; [ $BATCH = reset ] && RST=1
  ./run_e65_shard_arm.sh 0 s $BATCH $RST 5 $NSH > logs_e65_s_$BATCH-5.log 2>&1 &
  a=$!
  ./run_e65_shard_arm.sh 0 b $BATCH $RST 5 $NSH > logs_e65_b_$BATCH-5.log 2>&1 &
  b=$!
  wait $a; ra=$?
  wait $b; rb=$?
  echo "batch $BATCH done rc=$ra/$rb $(date -u +%H:%M:%SZ)"
  [ $ra -ne 0 ] || [ $rb -ne 0 ] && { echo "E65_SHIFT5_FAIL in batch $BATCH"; exit 1; }
done
echo "E65_SHIFT5_DONE all four shifted arms $(date -u +%H:%M:%SZ)"
