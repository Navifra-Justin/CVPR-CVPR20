"""Test of the E70 gate's box-geometry and localisation checks (the checker is tested, not trusted).
Takes the real gate dumps and corrupts the detections in ways a porting bug would; the checks must PASS the real dumps and FAIL every corruption
that is a coordinate/scale/orientation/alignment fault. Known limit: a 1-2 frame label offset is NOT detected (localisation precision stays
0.57-0.69 because boxes move little in 50-100 ms); timestamp alignment is covered by src/e70_1mpx_verify_data.py instead."""
import sys, numpy as np
sys.path.insert(0, 'src')
from e70_1mpx_gate import geometry_ok, loc_precision
G = 'experiments/e70_1mpx/gate'; bad = 0
def corrupt(d, kind, nf):
    d = d.copy()
    if kind == 'x2 scale': d[:, 1:5] *= 2
    if kind == 'x0.5 scale': d[:, 1:5] *= .5
    if kind == '+40px x': d[:, [1, 3]] += 40
    if kind == 'y flip': d[:, [2, 4]] = 360 - d[:, [4, 2]]
    if kind == 'frame roll 7': d[:, 0] = (d[:, 0] + 7) % nf
    return d
for n in ['s5vit-base', 'rvt-s-carry', 'rvt-s-reset']:
    Z = np.load(f'{G}/dets-{n}-shift0.npz'); d = Z['det'].astype(float); g = Z['gt'].astype(float); nf = len(Z['seq'])
    r = (geometry_ok(d), loc_precision(d, g)); print(n, 'real: geometry', r[0], 'loc %.3f' % r[1])
    bad += not (r[0] and r[1] >= .5)
    for k in ['x2 scale', 'x0.5 scale', '+40px x', 'y flip', 'frame roll 7']:
        c = corrupt(d, k, nf); gm, lp = geometry_ok(c), loc_precision(c, g)
        caught = (not gm) or lp < .5; bad += not caught
        print('   %-14s geometry %-5s loc %.3f  -> %s' % (k, gm, lp, 'CAUGHT' if caught else 'MISSED'))
print('SELFTEST', 'PASS' if bad == 0 else 'FAIL'); sys.exit(bad != 0)
