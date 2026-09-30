#!/bin/bash
# Sharding self-test. One process over the first NSEQ validation sequences, and the same
# range split over NSHARD processes and merged, must produce arrays that agree element for
# element. Run before any sharded arm is trusted; a merge that only looks right is the exact
# failure mode this project has been burned by before.
cd /media/hdd8/justin/my_project/CVPR20
G=${1:-0}; NSEQ=${2:-12}; NSH=${3:-3}
D=experiments/e65_rvt_boundary/selftest
mkdir -p $D
dump() {  # dump <outfile> <shard> <nshard>
  docker run --rm --gpus "\"device=$G\"" --memory=32g --user $(id -u):$(id -g) -e HOME=/tmp \
    -e DEV=cuda:0 -e FAM=rvtc -e TAG=s -e RESET=0 -e SHIFT=0 -e CHUNK=21 -e NSEQ=$NSEQ \
    -e SHARD=$2 -e NSHARD=$3 -e OUT=/work/$1 \
    -v $PWD:/work -w /work cvpr19-gpu-g1:torch2.7.1-cu128 \
    bash -lc "pip install --user hdf5plugin omegaconf hydra-core einops StrEnum scipy >/tmp/pip.log 2>&1 || { echo PIP_FAILED; tail -15 /tmp/pip.log; exit 90; }; python3 -u /work/src/e51_dump_all.py"
}
dump $D/single.npz 0 1 &
pids=$!
parts=""
for k in $(seq 0 $((NSH-1))); do
  dump $D/shard$k.npz $k $NSH &
  pids="$pids $!"
  parts="$parts $D/shard$k.npz"
done
wait $pids
python3 src/e65_merge_shards.py $D/merged.npz $parts
python3 - "$D" <<'PY'
import sys, numpy as np
d = sys.argv[1]
A = np.load(f'{d}/single.npz'); B = np.load(f'{d}/merged.npz')
ok = True
for k in ('det', 'gt', 'pos', 'seq'):
    # equal_nan, because the ground-truth array carries NaN velocities for boxes with no
    # forward or backward link and NaN != NaN would report an identical array as different.
    # equal_nan still requires the NaNs to sit in the same cells.
    same = A[k].shape == B[k].shape and np.array_equal(A[k], B[k], equal_nan=A[k].dtype.kind == 'f')
    print(f'  {k:4s} single {A[k].shape} merged {B[k].shape}  identical {same}')
    ok &= bool(same)
print('E65_SHARD_OK' if ok else 'E65_SHARD_FAIL')
sys.exit(0 if ok else 1)
PY
