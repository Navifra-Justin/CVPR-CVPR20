"""E60 figure - the same frame under both chunk positions.

The pair is what the experiment is: one frame, one checkpoint, one set of weights and one
set of labels, scored twice because the streaming protocol's chunk boundary was displaced
\ssmPairedShift windows. The left panel is the position the release gives the frame, one
to four windows of recurrent history; the right panel is the same frame at seventeen to
twenty. Nothing in the scene, the labels or the network differs between them.

Frame ids follow the E51/E58/E60 dumps, whose order is seqmap.json: sequence by sequence,
label by label, so a frame id resolves to a sequence and a representation index through
that sequence's own objframe_idx_2_repr_idx file.
"""
import numpy as np, json, os, sys, glob, h5py, hdf5plugin
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, 'src')
from e56_eval import iou_mat

SHIFT, TAG = 5, 'base'
SHORT, FULL = (0, 4), (16, 21)
SHOW = 0.3          # display threshold, stated in the caption; scoring uses every box
ROOT = 'data/gen1x/gen1/val'
GOLD, GT_C = '#e8a33d', '#1f9be0'

plt.rcParams.update({
    'font.size': 7, 'font.family': 'serif',
    'font.serif': ['Nimbus Roman', 'Times New Roman', 'Times', 'DejaVu Serif'],
    'mathtext.fontset': 'stix', 'axes.linewidth': 0.6, 'pdf.fonttype': 42,
})

A = np.load(f'experiments/e51_ranking/dets-s5vit-{TAG}.npz')
B = np.load(f'experiments/e60_shift/dets-s5vit-{TAG}-shift{SHIFT}.npz')
PA = np.load('experiments/e58_chunkpos/positions.npy')
PB = B['pos']
GT = A['gt'].astype(np.float64)
DA = A['det'].astype(np.float64)
DB = B['det'].astype(np.float64)
SEQ = json.load(open('experiments/e56_resolving/seqmap.json'))
assert np.array_equal(A['gt'], B['gt'], equal_nan=True), 'ground truth differs'

# the E60 pairing: starved under the release, full history after the shift
paired = np.flatnonzero((PA >= SHORT[0]) & (PA < SHORT[1]) &
                        (PB >= FULL[0]) & (PB < FULL[1]))
print(f'{len(paired)} paired frames', flush=True)

gt_by = {}
for r in GT:
    gt_by.setdefault(int(r[0]), []).append(r)


def boxes(D, f):
    d = D[(D[:, 0] == f) & (D[:, 5] >= SHOW)]
    return d[np.argsort(-d[:, 5])]


def matched(d, g):
    """Which displayed detections match a label of their own class at IoU >= 0.5."""
    if len(d) == 0 or len(g) == 0:
        return np.zeros(len(d), dtype=bool)
    gg = np.asarray(g)
    M = iou_mat(d[:, 1:5], gg[:, 1:5])   # iou_mat reads columns 0..3 as the box
    ok = np.zeros(len(d), dtype=bool)
    taken = np.zeros(len(g), dtype=bool)
    for k in range(len(d)):
        c = (~taken) & (gg[:, 5] == d[k, 6]) & (M[k] >= 0.5)
        if c.any():
            j = int(np.flatnonzero(c)[np.argmax(M[k][c])])
            taken[j] = True
            ok[k] = True
    return ok


# Pick the frame that shows the measured effect, and record the population the pick comes
# from so the caption can say whether the frame runs with the average or against it. A
# frame where the full-history arm detects nothing would show a false-positive drop and a
# total miss at once, so recovering labels is required first and the junk drop breaks ties.
best = None
cand = []
rows = []
for f in paired:
    g = gt_by.get(int(f))
    if not g:
        continue
    da, db = boxes(DA, f), boxes(DB, f)
    oa, ob = matched(da, g), matched(db, g)
    ma, mb = int(oa.sum()), int(ob.sum())
    fa, fb = int((~oa).sum()), int((~ob).sum())
    rows.append((len(g), ma, mb, fa, fb))
    if len(g) < 3 or mb < 2 or mb < ma:
        continue
    score = (mb - ma, fa - fb, mb)
    if best is None or score > best[0]:
        cand.append((score, int(f), len(g), fa, fb, ma, mb))
        best = (score,)
R = np.array(rows, dtype=np.float64)
print(f'over all {len(R):d} paired frames with labels: labels/frame {R[:, 0].mean():.2f}; '
      f'matched {R[:, 1].mean():.2f} -> {R[:, 2].mean():.2f}; '
      f'unmatched {R[:, 3].mean():.2f} -> {R[:, 4].mean():.2f} '
      f'(boxes shown at >= {SHOW:g})', flush=True)
print(f'  frames where the full arm matches more: {(R[:, 2] > R[:, 1]).mean() * 100:.1f}%, '
      f'fewer: {(R[:, 2] < R[:, 1]).mean() * 100:.1f}%; '
      f'emits fewer unmatched: {(R[:, 4] < R[:, 3]).mean() * 100:.1f}%', flush=True)
assert cand, 'no paired frame satisfies the display criteria'
TOP = max(c[0] for c in cand)
short = [c for c in cand if c[0] == TOP]
print(f'{len(short)} frame(s) tie at the strongest contrast {TOP}', flush=True)


def resolve(f):
    row = [x for x in SEQ if x['start'] <= f < x['start'] + x['n']][0]
    rd = os.path.join(ROOT, row['seq'], 'event_representations_v2',
                      'stacked_histogram_dt=50_nbins=10')
    o2r = np.load(os.path.join(rd, 'objframe_idx_2_repr_idx.npy'))
    return row, int(f - row['start']), rd, o2r


def frame_img(rd, o2r, local):
    with h5py.File(os.path.join(rd, 'event_representations.h5'), 'r') as h:
        IM = np.asarray(h[list(h.keys())[0]][int(o2r[local])], dtype=np.float32)
    return IM.sum(axis=0)


# Among the frames tied at the strongest contrast, show the one with the most events: an
# event frame carrying almost nothing displays the result without displaying the scene.
pick = None
for c in short:
    row, local, rd, o2r = resolve(c[1])
    n = float((frame_img(rd, o2r, local) > 0).sum())
    if pick is None or n > pick[0]:
        pick = (n, c, row, local, rd, o2r)
nev, (score, F, ng, fa, fb, ma, mb), row, local, rd, o2r = pick
print(f'frame {F}: {ng} labels; starved {ma} matched / {fa} unmatched, '
      f'full {mb} matched / {fb} unmatched  (release pos {PA[F]}, shifted pos {PB[F]})',
      flush=True)
raw = frame_img(rd, o2r, local)
H, W = raw.shape
# Events are sparse by construction, so the map is clipped rather than max-normalised: at
# the max a single hot pixel would drive every other event to near black.
img = np.clip(raw, 0, 2.0) / 2.0
print(f'  {row["seq"]} local {local} repr {int(o2r[local])}  {W}x{H}, '
      f'{nev / (H * W) * 100:.2f}% of pixels carry an event', flush=True)

g = gt_by[F]
PANEL = [(boxes(DA, F), '(a) 1–4 windows (as released)'),
         (boxes(DB, F), '(b) 17–20 windows (displaced)')]

# One crop for both panels, around everything either panel draws, so the two are
# comparable pixel for pixel and the objects are large enough to read.
allb = np.vstack([np.asarray(g)[:, 1:5]] + [d[:, 1:5] for d, _ in PANEL if len(d)])
PAD = 18
x0 = max(0, int(allb[:, 0].min()) - PAD); x1 = min(W, int(allb[:, 2].max()) + PAD)
y0 = max(0, int(allb[:, 1].min()) - PAD); y1 = min(H, int(allb[:, 3].max()) + PAD)
cw, ch = x1 - x0, y1 - y0
print(f'  crop x {x0}-{x1} y {y0}-{y1}  ({cw}x{ch})', flush=True)

COL = 3.32
fig, ax = plt.subplots(1, 2, figsize=(COL, COL * ch / (2 * cw) + 0.20))
for a, (d, title) in zip(ax, PANEL):
    a.imshow(img, cmap='bone', vmin=0, vmax=1, extent=(0, W, H, 0), aspect='equal',
             interpolation='nearest')
    for r in np.asarray(g):
        a.add_patch(Rectangle((r[1], r[2]), r[3] - r[1], r[4] - r[2], fill=False,
                              ec=GT_C, lw=0.9, ls=(0, (2.4, 1.5)), zorder=3))
    ok = matched(d, g)
    for r, m in zip(d, ok):
        a.add_patch(Rectangle((r[1], r[2]), r[3] - r[1], r[4] - r[2], fill=False,
                              ec=GOLD, lw=1.1 if m else 0.7,
                              ls='solid' if m else (0, (1.2, 1.2)), zorder=4))
    a.set_title(title, fontsize=6.2, pad=1.6)
    a.set_xlim(x0, x1); a.set_ylim(y1, y0)
    a.set_xticks([]); a.set_yticks([])
    for sp in a.spines.values():
        sp.set_linewidth(0.5); sp.set_color('0.55')
    a.text(0.02, 0.11, f'{int(ok.sum())}/{len(g)} labels matched, '
                       f'{int((~ok).sum())} unmatched', transform=a.transAxes,
           fontsize=6.2, color='w', va='bottom', ha='left')
fig.tight_layout(pad=0.14, w_pad=0.45)
fig.savefig('paper/figs/paired_frame.pdf', bbox_inches='tight', pad_inches=0.01)
print('WROTE paper/figs/paired_frame.pdf')
json.dump(dict(frame=F, seq=row['seq'], local=int(local), repr=int(o2r[local]),
               population=dict(
                   n=int(len(R)), gt_per_frame=float(R[:, 0].mean()),
                   matched=[float(R[:, 1].mean()), float(R[:, 2].mean())],
                   unmatched=[float(R[:, 3].mean()), float(R[:, 4].mean())],
                   frac_more_matched=float((R[:, 2] > R[:, 1]).mean()),
                   frac_fewer_matched=float((R[:, 2] < R[:, 1]).mean()),
                   frac_fewer_unmatched=float((R[:, 4] < R[:, 3]).mean())),
               pos_release=int(PA[F]), pos_shift=int(PB[F]), n_gt=int(ng),
               show=SHOW, tag=TAG, shift=SHIFT,
               crop=[x0, y0, x1, y1], event_pixels=int(nev),
               short=dict(shown=int(len(PANEL[0][0])), matched=ma, unmatched=fa),
               full=dict(shown=int(len(PANEL[1][0])), matched=mb, unmatched=fb)),
          open('experiments/e60_shift/figframe.json', 'w'), indent=1)
print('WROTE experiments/e60_shift/figframe.json')
