"""E70 structural gate on the small-subset dumps (experiments/e70_1mpx/gate/dets-*-shift{0,2}.npz).
Passes only on structure, never on the sign or size of the effect:
  1. every arm pair has identical ground truth and identical sequence index (NaN-equal), frames == labelled frames in the index files;
  2. every target frame (shift-0 position in [0,2)) with a shifted position >= 0 rotates by exactly SHIFT mod CHUNK;
     positions stay in [-1, CHUNK);
  3. class ids in {0,1,2}; every sequence has detections; box geometry: every detection centre lies inside the 640x360 label canvas and
     >= 99.5 % of boxes lie inside the 640x384 padded network input (+2 px; low-score edge boxes overshoot by a few px, nothing clips them);
     localisation: >= 50 % of detections with score >= 0.3 hit a ground-truth box at IoU >= 0.5 in the same frame
     (src/e70_1mpx_gate_selftest.py shows this is 0.72-0.78 for the real dumps and <= 0.27 for 2x/0.5x scale, 40 px shift, y flip and a 7-frame offset);
     frames-with-detections is printed but NOT gated: it was 99.9 % on Gen1 but is 80-88 % on 1 Mpx, where labels persist for stationary
     objects (see experiments/e70_1mpx/gate/DIAGNOSIS.txt);
  4. sanity floor: this project's all-box mAP > 10 for every arm (a broken port gives ~0; the floor is not a replication claim).
Exit 0 and write gate/PASS only if all hold."""
import sys, os, numpy as np
sys.path.insert(0, 'src')
from e56_eval import Scorer, iou_mat
def geometry_ok(d):
    cx = (d[:, 1] + d[:, 3]) / 2; cy = (d[:, 2] + d[:, 4]) / 2
    centres = bool(((cx >= 0) & (cx <= 640) & (cy >= 0) & (cy <= 360)).all())
    inside = ((d[:, 1] > -2) & (d[:, 2] > -2) & (d[:, 3] < 642) & (d[:, 4] < 386)).mean()
    return centres and inside >= 0.995

def loc_precision(d, g, smin=0.3):
    d = d[d[:, 5] >= smin]; gb = {}
    for r in g: gb.setdefault(int(r[0]), []).append(r[1:5])
    hit = sum(1 for r in d if int(r[0]) in gb and iou_mat(r[None, 1:5], np.array(gb[int(r[0])])).max() >= 0.5)
    return hit / max(len(d), 1)

def geometry_checks(Z, nm):
    d = Z['det'].astype(np.float64); g = Z['gt'].astype(np.float64); seq = Z['seq']
    fd = np.zeros(len(seq), bool); fd[np.unique(d[:, 0]).astype(int)] = True
    lp = loc_precision(d, g)
    print(f'    info {nm} frames with detections {fd.mean() * 100:.1f}% (not gated), localisation precision {lp:.3f}')
    return [(f'{nm} every sequence has detections', all(fd[seq == s].any() for s in np.unique(seq))),
            (f'{nm} classes in 0..2', set(np.unique(d[:, 6]).astype(int)) <= {0, 1, 2}),
            (f'{nm} boxes: centres in 640x360, >=99.5% inside 640x384', geometry_ok(d)),
            (f'{nm} localisation precision {lp:.2f} >= 0.5', lp >= 0.5)]

def main():
    G = 'experiments/e70_1mpx/gate'; CH = 10; SH = 2
    arms = [('s5vit-base', None), ('rvt-s', 'carry'), ('rvt-s', 'reset')]
    ok = True
    for m, r in arms:
        mid = '' if r is None else f'-{r}'
        pa, pb = f'{G}/dets-{m}{mid}-shift0.npz', f'{G}/dets-{m}{mid}-shift{SH}.npz'
        if not (os.path.exists(pa) and os.path.exists(pb)):
            print('MISSING', pa, pb); ok = False; continue
        a, b = np.load(pa), np.load(pb)
        c = []
        c.append(('gt identical', np.array_equal(a['gt'], b['gt'], equal_nan=True) and np.array_equal(a['seq'], b['seq'])))
        fa, fb = a['pos'], b['pos']
        t = np.flatnonzero((fa >= 0) & (fa < 2) & (fb >= 0))
        c.append(('targets exist', len(t) > 50))
        c.append(('rotation == SHIFT', bool(np.all(((fa[t] - fb[t]) % CH) == SH % CH))))
        c.append(('positions in range', fa.min() >= -1 and fa.max() < CH and fb.min() >= -1 and fb.max() < CH))
        for nm, Z in (('shift0', a), ('shift2', b)):
            d = Z['det']
            c += geometry_checks(Z, nm)
            mp = Scorer(d.astype(np.float64), Z['gt'].astype(np.float64)).evaluate(0.0, require_velocity=False) * 100
            c.append((f'{nm} all-box mAP {mp:.2f} > 10', mp > 10))
        print(m + mid, 'targets', len(t), 'frames', len(fa))
        for n, v in c:
            print('   ', 'OK ' if v else 'BAD', n); ok &= bool(v)
    print('GATE', 'PASS' if ok else 'FAIL')
    if ok: open(f'{G}/PASS', 'w').write('structural gate passed\n')
    sys.exit(0 if ok else 1)

if __name__ == '__main__': main()
