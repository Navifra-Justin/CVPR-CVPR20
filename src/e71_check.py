"""E71 regression + audit gate for one model.
  python3 src/e71_check.py <model e.g. rvt-s> <e71 dump> [--smoke]
(a) H=21 column of the E71 dump vs the E66 dump on the same frames (detection-wise, E66 unit criterion;
    different batch composition, so bit-identity is reported but not required);
(b) negative control: E71 H=40 vs E66 H=21 differ on most frames;
(c) ground truth of the selected frames equals E66 ground truth.
Frame mapping E71 -> E66 goes through (seq, local index j) = frames.npz.
"""
import sys, numpy as np
sys.argv_ = sys.argv
m = sys.argv[1]; Z = np.load(sys.argv[2]); E = np.load(f'experiments/e66_fixedH/dets-{m}.npz')
FR = np.load('experiments/e71_h4080/frames.npz')
def match_diff(a, b):
    if len(a) == 0 and len(b) == 0: return 0, 0.0, 0.0
    used = np.zeros(len(b), bool); wi = 0.0; ws = 0.0; un = 0
    for r in a[np.argsort(-a[:, 4])]:
        c = (b[:, 5] == r[5]) & ~used
        if not c.any(): un += int(r[4] > 0.0102); continue
        x1 = np.maximum(r[0], b[:, 0]); y1 = np.maximum(r[1], b[:, 1]); x2 = np.minimum(r[2], b[:, 2]); y2 = np.minimum(r[3], b[:, 3])
        it = np.clip(x2 - x1, 0, None) * np.clip(y2 - y1, 0, None)
        io = it / np.maximum((r[2]-r[0])*(r[3]-r[1]) + (b[:,2]-b[:,0])*(b[:,3]-b[:,1]) - it, 1e-9)
        io = np.where(c, io, -1); j = int(np.argmax(io))
        if io[j] < 0.5: un += int(r[4] > 0.0102); continue
        used[j] = True; wi = max(wi, 1 - io[j]); ws = max(ws, abs(r[4] - b[j, 4]))
    un += int((b[~used][:, 4] > 0.0102).sum()); return un, wi, ws
# map: e71 local frame id (position in Z arrays) -> e66 global id
seqZ = Z['seq']; locZ = np.zeros(len(seqZ), int)
for s in np.unique(seqZ): k = np.flatnonzero(seqZ == s); locZ[k] = np.arange(len(k))
key66 = {}; seq66 = E['seq']
for s in np.unique(seq66):
    k = np.flatnonzero(seq66 == s)
    for jj, g in enumerate(k): key66[(int(s), jj)] = int(g)
ok = True
def chk(c, t):
    global ok; ok = ok and bool(c); print(('  [PASS] ' if c else '  [FAIL] ') + t)
frames = np.flatnonzero(Z['done'])
g66 = [key66[(int(seqZ[f]), int(locZ[f]))] for f in frames]
chk(len(frames) > 0 and np.array_equal(np.sort(frames), frames), f'{len(frames)} evaluated frames')
sel = set(zip(FR['seq'].tolist(), FR['j'].tolist()))
if '--smoke' not in sys.argv: chk(set((int(seqZ[f]), int(locZ[f])) for f in frames) == sel, 'evaluated set == frames.npz')
def rows(d, f): return d[d[:, 0] == f][:, 1:]
d21 = Z['det_h21'].astype(np.float64); d40 = Z['det_h40'].astype(np.float64); e21 = E['det_h21'].astype(np.float64)
uw = []; ex = 0; neg = 0
for f, g in zip(frames, g66):
    a = rows(e21, g); b = rows(d21, f); uw.append(match_diff(a, b))
    ex += int(a.shape == b.shape and (len(a) == 0 or np.abs(a - b).max() == 0))
    c = rows(d40, f); neg += int(c.shape != a.shape or (len(a) and np.abs(c - a).max() > 1e-3))
un = sum(u[0] for u in uw); wi = max(u[1] for u in uw); ws = max(u[2] for u in uw)
chk(un == 0 and wi < 1e-2 and ws < 5e-3, f'H=21 vs E66 H=21 detection-wise: unpaired {un}, worst 1-IoU {wi:.2e}, worst |score diff| {ws:.2e}; bit-identical {ex}/{len(frames)}')
chk(neg >= 0.5 * len(frames), f'negative control: E71 H=40 differs from E66 H=21 on {neg}/{len(frames)} frames')
gz = Z['gt'].astype(np.float64); ge = E['gt'].astype(np.float64)
okg = True
for f, g in zip(frames, g66):
    a = gz[gz[:, 0] == f][:, 1:]; b = ge[ge[:, 0] == g][:, 1:]
    okg &= a.shape == b.shape and np.allclose(a, b, equal_nan=True, atol=0)
chk(okg, 'ground truth of every evaluated frame equals E66')
print('CHECK', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
