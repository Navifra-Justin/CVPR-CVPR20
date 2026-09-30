"""Mutation test for src/e65_regress_check.py.

This project has twice been burned by a checker that printed a clean pass while pointed at
nothing (docs/PROTOCOL_LEDGER.md). The E65 regression gate is the single thing that licenses
reading a null in the carried-state arm as a measurement rather than as a driver that
dropped the treatment, so it is exercised here on files it actually reads: one honest case
that must pass and six corruptions that must each be rejected.

  python3 src/e65_gate_selftest.py
"""
import numpy as np, os, subprocess, shutil, tempfile, sys

tmp = tempfile.mkdtemp()
os.makedirs(f'{tmp}/experiments/e51_ranking')
os.makedirs(f'{tmp}/experiments/e65_rvt_boundary')
os.makedirs(f'{tmp}/experiments/e58_chunkpos')
shutil.copy(os.path.join(os.path.dirname(__file__), 'e65_regress_check.py'), f'{tmp}/x.py')
rng = np.random.default_rng(0)
NF = 500
det = rng.random((2000, 7)).astype(np.float32)
gt = rng.random((3000, 8)).astype(np.float32)
pos = np.concatenate([np.arange(21)] * 24 + [np.arange(NF - 504) % 21]).astype(np.int16)[:NF]


def w(p, **k):
    np.savez_compressed(p, **k)


def run(label, ref, new, rst, expect_ok):
    w(f'{tmp}/experiments/e51_ranking/dets-rvt-s.npz', **ref)
    w(f'{tmp}/experiments/e65_rvt_boundary/dets-rvt-s-carry-shift0.npz', **new)
    w(f'{tmp}/experiments/e65_rvt_boundary/dets-rvt-s-reset-shift0.npz', **rst)
    r = subprocess.run(['python3', 'x.py', 's'], cwd=tmp, capture_output=True, text=True)
    good = (r.returncode == 0) == expect_ok
    print(f'  {"[PASS]" if good else "[FAIL]"} {label:50s} rc={r.returncode} expect_ok={expect_ok}')
    return good


# The real per-window dump carries no `pos` key at all. The first version of this fixture
# supplied one, so the gate's unconditional a['pos'] read was never exercised against a file
# shaped like the real one and died with a KeyError the first time it saw it. The fixture now
# matches the artifact, and a separate case covers the all -1 form.
REF = dict(det=det, gt=gt)
REF_MINUS1 = dict(det=det, gt=gt, pos=np.full(NF, -1, dtype=np.int16))
REF_POSITIONED = dict(det=det, gt=gt, pos=pos.copy())
np.save(f'{tmp}/experiments/e58_chunkpos/positions.npy', pos)
GOOD = dict(det=det.copy(), gt=gt.copy(), pos=pos)
RST = dict(det=det.copy() + 0.5, gt=gt.copy(), pos=pos)
d2 = det.copy(); d2[5, 3] += 0.001
g2 = gt.copy(); g2[7, 2] += 0.01
cases = [
    ('honest: identical detections, real positions, live reset', REF, GOOD, RST, True),
    ('one detection coordinate moved', REF, dict(det=d2, gt=gt, pos=pos), RST, False),
    ('a detection dropped', REF, dict(det=det[:-1], gt=gt, pos=pos), RST, False),
    ('ground truth moved', REF, dict(det=det, gt=g2, pos=pos), RST, False),
    ('chunked dump records no positions', REF,
     dict(det=det, gt=gt, pos=np.full(NF, -1, dtype=np.int16)), RST, False),
    ('positions never reach the end of the chunk', REF,
     dict(det=det, gt=gt, pos=np.clip(pos, 0, 15)), RST, False),
    ('the RESET flag is inert (reset arm equals carry arm)', REF, GOOD,
     dict(det=det.copy(), gt=gt.copy(), pos=pos), False),
    ('reference dump with an explicit all -1 position column', REF_MINUS1, GOOD, RST, True),
    ('reference dump that already carries real positions', REF_POSITIONED, GOOD, RST, False),
    ('chunked positions disagree with the release placement', REF,
     dict(det=det, gt=gt, pos=np.roll(pos, 1)), RST, False),
]
print('E65 regression-gate mutation test')
res = [run(*c) for c in cases]
shutil.rmtree(tmp)
print(f'{sum(res)} of {len(res)} behaved as intended')
sys.exit(0 if all(res) else 1)
