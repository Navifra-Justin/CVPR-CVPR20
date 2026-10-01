"""E66 regression gate: the RVT reset-shift0 dump (E65, RESET=1, SHIFT=0, CHUNK=21) is the
fixed-H dump in disguise. A frame recorded at chunk position p has seen exactly the p+1 windows
since the chunk start with a fresh state, so its detections must equal the per-frame fixed
H=p+1 detections of src/e66_fixedH_dump.py, detection for detection.

  python3 src/e66_gate.py <tag> <e66 dump> [--tol 1e-3] [--unit]

Exit 0 only if (a) the ground truth of the compared frames is identical, (b) every compared
frame has the same detection count and (c) every detection row is within --tol (exact
equality is reported separately), and (d) the negative control holds: the same frames compared
against a DIFFERENT H must disagree on most frames (a gate that cannot fail is not a gate).
"""
import sys, os, numpy as np
ROOT = os.environ.get('E66_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tag = sys.argv[1]; new = sys.argv[2]
tol = float(sys.argv[sys.argv.index('--tol') + 1]) if '--tol' in sys.argv else 1e-3
REF = sys.argv[sys.argv.index('--ref') + 1] if '--ref' in sys.argv else None
A = np.load(REF if REF else os.path.join(ROOT, f'experiments/e65_rvt_boundary/dets-rvt-{tag}-reset-shift0.npz'))
# --ref <released dump without a pos column> (SSM-ViT e51 dump): positions of the released 21-grid are
# experiments/e58_chunkpos/positions.npy; the gate then asserts that fixed H = p+1 equals the release
# at position p, which holds only because the SSM release's carried state is inert (E47).
POS = np.load(os.path.join(ROOT, 'experiments/e58_chunkpos/positions.npy')) if REF else A['pos']
Z = np.load(new)
HS = [int(h) for h in Z['hnominal']]
nF = len(Z['ri']); done = Z['done']
pos = POS[:nF]
adet = A['det'].astype(np.float64); agt = A['gt'].astype(np.float64)
ok = True
def chk(c, m):
    global ok; ok = ok and bool(c); print(('  [PASS] ' if c else '  [FAIL] ') + m)

def match_diff(a, b):
    """Detection-wise comparison independent of row order: pair rows of the same class by best
    IoU. Returns (n_unpaired, worst 1-IoU, worst |score diff|) over paired rows."""
    if len(a) == 0 and len(b) == 0: return 0, 0.0, 0.0
    # a row present on one side only is tolerated if its score is within 2% of the confidence
    # threshold 0.01 (a cross-device rounding can push a borderline row over or under it)
    used = np.zeros(len(b), bool); wi = 0.0; ws = 0.0; un = 0
    for r in a[np.argsort(-a[:, 4])]:
        c = (b[:, 5] == r[5]) & ~used
        if not c.any():
            un += int(r[4] > 0.0102); continue
        x1 = np.maximum(r[0], b[:, 0]); y1 = np.maximum(r[1], b[:, 1])
        x2 = np.minimum(r[2], b[:, 2]); y2 = np.minimum(r[3], b[:, 3])
        it = np.clip(x2 - x1, 0, None) * np.clip(y2 - y1, 0, None)
        io = it / np.maximum((r[2]-r[0])*(r[3]-r[1]) + (b[:,2]-b[:,0])*(b[:,3]-b[:,1]) - it, 1e-9)
        io = np.where(c, io, -1); j = int(np.argmax(io))
        if io[j] < 0.5: un += int(r[4] > 0.0102); continue
        used[j] = True; wi = max(wi, 1 - io[j]); ws = max(ws, abs(r[4] - b[j, 4]))
    un += int((b[~used][:, 4] > 0.0102).sum())
    return un, wi, ws


def rows(det, f):
    return det[det[:, 0] == f][:, 1:]
# (a) ground truth of the prefix
g1 = Z['gt'].astype(np.float64); g0 = agt[agt[:, 0] < nF]
chk(g1.shape == g0.shape and np.allclose(g1, g0, equal_nan=True, atol=0),
    f'ground truth of the {nF}-frame prefix identical ({g1.shape[0]} boxes)')
# sort rows by fid once
UNIT = '--unit' in sys.argv; uw = []; ex = 0; close = 0; tot = 0; cnt_bad = 0; maxd = 0.0; per_p = {}
neg_diff = 0; neg_tot = 0
for p, h in [(h - 1, h) for h in HS]:
    fr = np.flatnonzero(done & (pos == p))
    d = Z[f'det_h{h}'].astype(np.float64)
    hs_other = HS[(HS.index(h) + 1) % len(HS)]; do = Z[f'det_h{hs_other}'].astype(np.float64)
    e = c = 0
    for f in fr:
        a = rows(adet, f); b = rows(d, f); tot += 1
        if UNIT: uw.append(match_diff(a, b))
        if a.shape != b.shape: cnt_bad += 1; continue
        df = np.abs(a - b).max() if len(a) else 0.0
        maxd = max(maxd, df); e += int(df == 0.0); c += int(df <= tol)
        o = rows(do, f); neg_tot += 1
        neg_diff += int(o.shape != a.shape or (len(a) and np.abs(o - a).max() > tol))
    ex += e; close += c; per_p[h] = (len(fr), e, c)
for h, (n, e, c) in per_p.items():
    print(f'    H={h:2d} (position {h-1:2d}): {n:4d} frames, bit-identical {e}, within tol {c}')
chk(tot > 0, f'{tot} frames compared (positions {sorted(h-1 for h in per_p)})')
if UNIT: print(f'    frames with a different detection count: {cnt_bad} (allowed only if the extra rows are borderline)')
else: chk(cnt_bad == 0, f'detection counts equal on every compared frame ({cnt_bad} mismatches)')
if UNIT:
    un = sum(u[0] for u in uw); wi = max(u[1] for u in uw); ws = max(u[2] for u in uw)
    chk(un == 0 and wi < 1e-2 and ws < 5e-3,
        f'detection-wise match (cross-device unit check): unpaired {un}, worst 1-IoU {wi:.2e}, worst |score diff| {ws:.2e}')
else:
  chk(close == tot, f'all frames within tol {tol:g}: {close}/{tot}; bit-identical {ex}/{tot}; max abs diff {maxd:.3g}')
print(f'    bit-identical {ex}/{tot}; max raw abs diff {maxd:.3g}')
chk(neg_tot > 0 and neg_diff >= 0.5 * neg_tot,
    f'negative control: against the wrong H the frames differ in {neg_diff}/{neg_tot}')
print('GATE', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
