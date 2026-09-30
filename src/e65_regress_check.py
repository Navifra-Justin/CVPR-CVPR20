"""E65 gate - the chunked RVT driver must reproduce the per-window RVT dump exactly.

FAM=rvtc groups RVT's per-window calls onto the SSM chunk grid so that a position can be
recorded for each frame and so that SHIFT and a boundary state reset can be applied. With
RESET=0, SHIFT=0 and CHUNK=21 that grouping is supposed to change nothing at all: `rvt`
starts at max(o2r[0]-WARM,0) with WARM=20, `rvtc` starts at max(o2r[0]-CHUNK+1,0), and the
two are the same index; the windows are then visited in the same order with the same carried
state, so every detection must be bit-identical to the stored e51 dump.

This is the wiring gate for the whole experiment. If it passes, a null in the carried-state
arm is a measurement rather than a driver that quietly dropped the treatment; if it fails,
the chunked driver is not the same instrument as the one the paper's RVT rows came from and
nothing downstream is comparable.

It is also the gate that would catch the opposite failure: a RESET flag read but never
applied would make the reset arm identical to the carried arm, so the two arms are compared
here too and the check fails if they do not differ.

  python3 src/e65_regress_check.py <tag>
"""
import sys, os, numpy as np

TAG = sys.argv[1] if len(sys.argv) > 1 else 's'
REF = f'experiments/e51_ranking/dets-rvt-{TAG}.npz'
NEW = f'experiments/e65_rvt_boundary/dets-rvt-{TAG}-carry-shift0.npz'
RST = f'experiments/e65_rvt_boundary/dets-rvt-{TAG}-reset-shift0.npz'

ok = True


def chk(cond, msg):
    global ok
    print(('  [PASS] ' if cond else '  [FAIL] ') + msg)
    ok = ok and bool(cond)


print(f'E65 regression gate, rvt-{TAG}')
for p in (REF, NEW):
    if not os.path.exists(p):
        print(f'  [FAIL] missing {p}')
        sys.exit(1)
a, b = np.load(REF), np.load(NEW)

# 1. the chunked driver is the per-window driver when the grid is inert
chk(a['det'].shape == b['det'].shape, f"detection count  ref {a['det'].shape[0]}  new {b['det'].shape[0]}")
chk(a['det'].shape == b['det'].shape and np.array_equal(a['det'], b['det']),
    'every detection bit-identical to the stored per-window dump')
chk(np.array_equal(a['gt'], b['gt'], equal_nan=True), 'ground truth identical')

# 2. the stored per-window dump records no position; the chunked one must record real ones.
# The per-window dumper predates the position column and writes no `pos` array at all, so the
# absence of the key is the expected state and an all -1 array is the other acceptable form.
# The first version of this check read a['pos'] unconditionally and died with a KeyError on the
# real artifact after its fixture had always supplied the key; the fixture in
# src/e65_gate_selftest.py now omits it, as the real file does.
chk('pos' not in a.files or (a['pos'] == -1).all(),
    'the per-window dump carries no chunk position, as expected')
pos = b['pos']
chk((pos >= 0).mean() > 0.97, f'chunked dump assigns a position to {(pos >= 0).mean() * 100:.2f}% of frames')
chk(pos.max() == 20, f'positions reach the end of the 21-window chunk (max {pos.max()})')

# The chunked driver must land on the placement the released streaming evaluation already
# produced, frame for frame. Without this the RVT rows and the SSM rows would be two
# similar-looking comparisons on two different grids rather than the same one.
PA = 'experiments/e58_chunkpos/positions.npy'
if not os.path.exists(PA):
    print(f'  [FAIL] missing {PA}')
    sys.exit(1)
pa = np.load(PA)
chk(pos.shape == pa.shape and np.array_equal(pos, pa),
    'chunked positions equal the recorded release placement frame for frame')

# 3. the reset flag must actually change the output, or the ablation arm is a no-op
if os.path.exists(RST):
    c = np.load(RST)
    chk(np.array_equal(b['gt'], c['gt'], equal_nan=True), 'reset arm scores the same ground truth')
    chk(np.array_equal(b['pos'], c['pos']), 'reset arm places frames at the same positions')
    diff = (b['det'].shape != c['det'].shape) or not np.array_equal(b['det'], c['det'])
    chk(diff, 'dropping the state at the boundary changes the detections (the flag is live)')
else:
    print(f'  [skip] {RST} not dumped yet')

print('E65_REGRESS_OK' if ok else 'E65_REGRESS_FAIL')
sys.exit(0 if ok else 1)
