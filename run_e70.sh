#!/bin/bash
# E70 - chunk-boundary move on 1 Mpx, full chain.   setsid nohup ./run_e70.sh > logs_e70.log 2>&1 < /dev/null &
# 1. wait for data/gen4x/fetch.log FETCH_END (parallel range fetch of the 128 val sequences of the official gen4.tar)
# 1b. wait for experiments/e70_1mpx/gate/PASS (structural gate on a 6-sequence subset, src/e70_1mpx_gate.py)
# 2. data check (src/e70_1mpx_verify_data.py) - refuses to claim the GPU if any sequence is bad
# 3. dumps, each arm under `flock /tmp/gpu<G>_queue.lock docker run` (run_e70_arm.sh), 4 resumable shards:
#      headline  : s5vit-base, s5vit-small at SHIFT 0 and 2   (positions 0-1 -> 8-9 of a 10-window chunk)
#      control   : rvtc-s carry and reset at SHIFT 0 and 2    (E65 design: carry = no-op, reset = positive control)
#      dose      : s5vit-base SHIFT 5 (positions 0-1 -> 5-6)
# 4. CPU evaluation (nice 19): src/e70_1mpx_paired.py
cd /media/hdd8/justin/my_project/CVPR20
G=${G:-0}; D=experiments/e70_1mpx
until grep -q FETCH_END data/gen4x/fetch.log; do sleep 60; done
grep FAILED data/gen4x/fetch.log && { echo "fetch had failures"; exit 1; }
nice -n 19 docker run --rm --memory=8g --user $(id -u):$(id -g) -e HOME=/tmp -v $PWD:/work -w /work cvpr19-gpu-g1:torch2.7.1-cu128 \
  bash -lc "pip install --user hdf5plugin h5py >/tmp/pip.log 2>&1; python3 src/e70_1mpx_verify_data.py" | tee $D/verify_data.log
[ ${PIPESTATUS[0]} -eq 0 ] || { echo "data check failed; GPU not claimed"; exit 1; }
# gate: small-subset dumps (experiments/e70_1mpx/run_gate.sh) must pass the structural check first
until [ -f $D/gate/PASS ]; do
  if grep -q GATE_DUMPS_END $D/gate/run.log 2>/dev/null; then
    python3 src/e70_1mpx_gate.py | tee $D/gate/gate.log; [ -f $D/gate/PASS ] || { echo "gate failed; GPU not claimed for production"; exit 1; }
  fi; sleep 60; done
for SH in 0 2; do ./run_e70_arm.sh $G ssm base - 0 $SH 4 $D; done
for SH in 0 2; do ./run_e70_arm.sh $G ssm small - 0 $SH 4 $D; done
for SH in 0 2; do ./run_e70_arm.sh $G rvtc s carry 0 $SH 4 $D; ./run_e70_arm.sh $G rvtc s reset 1 $SH 4 $D; done
./run_e70_arm.sh $G ssm base - 0 5 4 $D
ARMS="s5vit-base:- s5vit-small:- rvt-s:carry,reset" nice -n 19 env SHIFT=2 python3 src/e70_1mpx_paired.py | tee $D/paired-shift2.log
echo "E70_DONE $(date -u +%H:%M:%SZ)"
