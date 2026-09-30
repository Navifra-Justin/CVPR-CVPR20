#!/bin/bash
# E65 orchestrator, third form. Two things changed under it: the SHIFT=0 arms are no longer
# all alive (rvt-s carry died at sequence 226 inside the HDF5 blosc filter, a transient read
# failure under host memory pressure -- the same sequences were read successfully by the
# rvt-b arm), and sharding is now available and verified exact. So this waits for whatever
# unsharded SHIFT=0 arms are still running, re-runs any SHIFT=0 arm whose dump is missing as
# a sharded arm with retries, runs the wiring gate, and only then runs the shifted arms.
cd /media/hdd8/justin/my_project/CVPR20
D=experiments/e65_rvt_boundary
WAITPIDS="$1"; NSH=${2:-3}
echo "orch3: waiting on surviving unsharded pids $WAITPIDS  $(date -u +%H:%M:%SZ)"
while true; do
  alive=0
  for p in $WAITPIDS; do kill -0 $p 2>/dev/null && alive=1; done
  [ $alive -eq 0 ] && break
  sleep 60
done
sleep 20   # let the out-of-band arms finish moving their dump into place
echo "orch3: unsharded SHIFT=0 arms done  $(date -u +%H:%M:%SZ)"
rc=0
for a in s:carry:0 s:reset:1 b:carry:0 b:reset:1; do
  T=${a%%:*}; rest=${a#*:}; REG=${rest%%:*}; RST=${rest##*:}
  F=$D/dets-rvt-$T-$REG-shift0.npz
  if [ -s "$F" ]; then echo "orch3: have $F"; continue; fi
  echo "orch3: re-running rvt-$T $REG shift=0 sharded x$NSH  $(date -u +%H:%M:%SZ)"
  rm -f "$F"
  ./run_e65_shard_arm.sh 0 $T $REG $RST 0 $NSH > logs_e65_${T}_${REG}0_shard.log 2>&1 || rc=1
done
[ $rc -ne 0 ] && { echo "orch3: a SHIFT=0 re-run failed"; exit 2; }
for f in $D/dets-rvt-s-carry-shift0.npz $D/dets-rvt-s-reset-shift0.npz \
         $D/dets-rvt-b-carry-shift0.npz $D/dets-rvt-b-reset-shift0.npz; do
  [ -s "$f" ] || { echo "orch3: MISSING $f"; exit 2; }
done
ok=1
for T in s b; do
  python3 src/e65_regress_check.py $T | tee $D/regress-$T.log
  [ "${PIPESTATUS[0]}" -ne 0 ] && ok=0
done
if [ $ok -ne 1 ]; then echo "orch3: E65 regression gate failed; shifted arms withheld"; exit 1; fi
echo "orch3: gate passed, launching shifted arms sharded x$NSH  $(date -u +%H:%M:%SZ)"
./run_e65_shard_arm.sh 0 s carry 0 5 $NSH > logs_e65_s_carry5.log 2>&1 & p1=$!
./run_e65_shard_arm.sh 0 s reset 1 5 $NSH > logs_e65_s_reset5.log 2>&1 & p2=$!
./run_e65_shard_arm.sh 1 b carry 0 5 $NSH > logs_e65_b_carry5.log 2>&1 & p3=$!
./run_e65_shard_arm.sh 1 b reset 1 5 $NSH > logs_e65_b_reset5.log 2>&1 & p4=$!
rc=0
for p in $p1 $p2 $p3 $p4; do wait $p || rc=1; done
[ $rc -ne 0 ] && { echo "orch3: a shifted arm failed"; exit 1; }
echo "E65_DONE all arms $(date -u +%H:%M:%SZ)"
