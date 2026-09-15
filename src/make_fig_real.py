"""Two figures of actual sensor data, rendered for print from the same sources the
video plays.

fig6_sweep_real: one real Gen1 validation frame carrying several fast boxes, with the
released checkpoint's detections where the release put them and the ground truth drawn
twice, at the label instant and displaced to the newest window's influence centroid.
The frame index is rebuilt with E37's own iteration order, so the boxes drawn are the
ones the sweep scored; the centroid is read from E45's result file, never typed in.

fig7_ceiling_vs_day: the ceiling-exposure recording and the daytime control as event
scatter, one 350 us slice at the instant the ceiling recording's rate peaks and one at
the instant it bottoms, the same two instants cut from the daytime stream, and both
normalised rate curves underneath. Everything is chosen by rule: the window is the
densest published exposure span (as in the video), the instants are the argmax and
argmin of the ceiling recording's own rate.

    python3 src/make_fig_real.py     (inside the docker image that carries h5py)
"""
import glob
import json
import os

import h5py
import hdf5plugin  # noqa: F401  (registers the codec)
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGS = os.path.join(ROOT, 'paper', 'figs')

plt.rcParams.update({
    'font.size': 7,
    'font.family': 'serif',
    'font.serif': ['Nimbus Roman', 'Times New Roman', 'Times', 'DejaVu Serif'],
    'mathtext.fontset': 'stix',
    'axes.linewidth': 0.6,
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6,
    'xtick.labelsize': 6.5,
    'ytick.labelsize': 6.5,
    'axes.labelsize': 7,
    'legend.fontsize': 6.3,
    'legend.frameon': False,
    'pdf.fonttype': 42,
})
COL = 3.32

# ---------------------------------------------------------------- fig6_sweep_real
Z = np.load(os.path.join(ROOT, 'experiments/e37_map/dets.npz'))
DET = Z['det'].astype(np.float64)
GT = Z['gt'].astype(np.float64)
CEN = json.load(open(os.path.join(
    ROOT, 'experiments/e45_influence_fixed/result.json')))['zero']['centroid_ms']

fid = 0
index = {}
for sd in sorted(glob.glob(os.path.join(ROOT, 'data/gen1x/gen1/val/*'))):
    rd = os.path.join(sd, 'event_representations_v2', 'stacked_histogram_dt=50_nbins=10')
    try:
        L = np.load(os.path.join(sd, 'labels_v2', 'labels.npz'))['labels']
        o2r = np.load(os.path.join(rd, 'objframe_idx_2_repr_idx.npy'))
    except Exception:
        continue
    if len(o2r) < 3:
        continue
    ts = np.sort(np.unique(L['t']))
    for k in range(min(len(o2r), len(ts))):
        index[fid] = (rd, int(o2r[k]))
        fid += 1
print(f"rebuilt {fid} frame indices", flush=True)

spd = np.hypot(GT[:, 6], GT[:, 7])
best = None
for f in np.unique(GT[:, 0]):
    m = (GT[:, 0] == f) & np.isfinite(spd)
    if m.sum() < 3 or (spd[m] >= 20).sum() < 2:
        continue
    sc = float(np.median(spd[m]))
    if best is None or sc > best[0]:
        best = (sc, int(f))
sc, F = best
rd, ri = index[F]
with h5py.File(os.path.join(rd, 'event_representations.h5'), 'r') as f:
    IM = np.asarray(f[list(f.keys())[0]][ri], dtype=np.float32)
img = np.log1p(IM.sum(axis=0))
img = img / max(img.max(), 1e-6)
H, W = img.shape
g = GT[GT[:, 0] == F]
d = DET[(DET[:, 0] == F) & (DET[:, 5] >= 0.3)]
fast = np.nanmax(np.hypot(g[:, 6], g[:, 7]))
print(f"frame {F}: median gt speed {sc:.1f} px/s, {len(g)} gt, {len(d)} det, "
      f"fastest {fast:.1f} px/s -> {fast*abs(CEN)*1e-3:.2f} px over {abs(CEN):.2f} ms",
      flush=True)

gx0, gx1 = g[:, 1].min(), g[:, 3].max()
gy0, gy1 = g[:, 2].min(), g[:, 4].max()
mx, my = 0.16 * (gx1 - gx0), 0.30 * (gy1 - gy0)
CX0, CX1 = max(0, gx0 - mx), min(W, gx1 + mx)
CY0, CY1 = max(0, gy0 - my), min(H, gy1 + my)

GOLD = '#b8860b'
RED = '#c23b3b'
BLUE = '#2b6ca3'
h_img = COL * (CY1 - CY0) / (CX1 - CX0)
h_leg = 0.34  # a white strip under the image carries the legend, in inches
h_tot = h_img + h_leg
fig = plt.figure(figsize=(COL, h_tot))
ax = fig.add_axes([0, h_leg / h_tot, 1, h_img / h_tot])
ax.imshow(img, cmap='bone', vmin=0, vmax=1, extent=(0, W, H, 0), aspect='auto')
for r in d:
    ax.add_patch(Rectangle((r[1], r[2]), r[3] - r[1], r[4] - r[2],
                           fill=False, ec=GOLD, lw=1.1))
for r in g:
    vx, vy = r[6], r[7]
    ax.add_patch(Rectangle((r[1], r[2]), r[3] - r[1], r[4] - r[2],
                           fill=False, ec=RED, lw=1.0, ls='--'))
    if np.isfinite(vx):
        s = CEN * 1e-3  # the displaced instant, in seconds
        ax.add_patch(Rectangle((r[1] + s * vx, r[2] + s * vy),
                               r[3] - r[1], r[4] - r[2],
                               fill=False, ec=BLUE, lw=1.0, ls=':'))
ax.set_xlim(CX0, CX1)
ax.set_ylim(CY1, CY0)
ax.set_xticks([])
ax.set_yticks([])
for sp in ax.spines.values():
    sp.set_color('0.4')
for yin, col, txt in [(h_leg - 0.095, GOLD, 'released detections'),
                      (h_leg - 0.200, RED, 'ground truth at the label instant'),
                      (h_leg - 0.305, BLUE, 'ground truth at the newest window\'s '
                       'centroid, $\\delta=%.2f$ ms' % CEN)]:
    fig.text(0.012, yin / h_tot, txt, color=col, fontsize=6.5, va='baseline')
fig.savefig(os.path.join(FIGS, 'fig6_sweep_real.pdf'), dpi=300)
plt.close(fig)
json.dump(dict(frame=int(F), n_gt=int(len(g)), n_det=int(len(d)),
               med_speed=float(sc), fastest_px_s=float(fast),
               disp_px=float(fast * abs(CEN) * 1e-3), centroid_ms=float(CEN),
               score_floor=0.3),
          open(os.path.join(ROOT, 'experiments/e37_map/fig6_stats.json'), 'w'),
          indent=1)
print('WROTE fig6_sweep_real.pdf', flush=True)

# ------------------------------------------------------------- fig7_ceiling_vs_day
SPAN = 15000
SLICE = 350
PANELS = [('zurich_city_09_a', 'ceiling exposure, night'),
          ('interlaken_00_c', 'daytime control')]


def load(seq):
    f = h5py.File(os.path.join(ROOT, f'data/dsec/{seq}/events.h5'), 'r')
    ev = f['events']
    ms2i = f['ms_to_idx'][:]
    t_off = int(f['t_offset'][()])
    exp = [tuple(int(v) for v in l.split(',')) for l in
           open(os.path.join(ROOT, f'experiments/e00_exposure_survey/e_{seq}.txt'))
           if not l.startswith('#') and l.strip()]
    best = None
    for a, b in exp:
        s = a
        e = s + SPAN
        ma = (s - t_off) // 1000
        mb = (e - t_off) // 1000 + 1
        if ma < 0 or mb >= len(ms2i) or mb <= ma:
            continue
        j0, j1 = int(ms2i[ma]), int(ms2i[mb])
        if j1 - j0 < 2000:
            continue
        if best is None or (j1 - j0) > best[0]:
            best = (j1 - j0, s, e, j0, j1)
        if best and best[0] > 400000:
            break
    n, s, e, j0, j1 = best
    t = ev['t'][j0:j1].astype(np.int64) + t_off
    x = ev['x'][j0:j1].astype(np.int64)
    y = ev['y'][j0:j1].astype(np.int64)
    k = (t >= s) & (t < e)
    t, x, y = t[k], x[k], y[k]
    edges = np.arange(s, s + SPAN + 1, SLICE)
    rate, _ = np.histogram(t, bins=edges)
    f.close()
    return dict(seq=seq, t=t, x=x, y=y, s=s, rate=rate.astype(float), edges=edges)


P = [load(s) for s, _ in PANELS]
r0 = P[0]['rate'] / P[0]['rate'].mean()
IPK, ITR = int(np.argmax(r0)), int(np.argmin(r0))
print(f"ceiling peak slice {IPK} ({r0[IPK]:.2f}x mean), trough slice {ITR} "
      f"({r0[ITR]:.2f}x mean)", flush=True)

H2, W2 = 480, 640
BAND = (100, 420)  # the vertical crop shown, stated in the caption
fig = plt.figure(figsize=(COL, 2.34))
gs = fig.add_gridspec(3, 2, height_ratios=[1.0, 1.0, 0.80], hspace=0.06, wspace=0.04,
                      left=0.085, right=0.995, top=0.89, bottom=0.16)
for row, p in enumerate(P):
    for coli, (idx, tag) in enumerate([(IPK, 'peak'), (ITR, 'trough')]):
        ax = fig.add_subplot(gs[row, coli])
        lo = p['s'] + idx * SLICE
        k = (p['t'] >= lo) & (p['t'] < lo + SLICE)
        ax.scatter(p['x'][k], p['y'][k], s=0.22, c='black', alpha=0.65,
                   linewidths=0, marker='.')
        ax.set_xlim(0, W2)
        ax.set_ylim(BAND[1], BAND[0])
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color('0.45')
        if row == 0:
            ax.set_title(f"at the ceiling rate {tag}", fontsize=6.5, pad=2)
        ax.text(0.015, 0.06, f"{int(k.sum()):,} events", transform=ax.transAxes,
                fontsize=6.0, color='0.25')
        if coli == 0:
            ax.set_ylabel(p['seq'].replace('_', '\\_') if False else
                          ('ceiling, night' if row == 0 else 'daytime'),
                          fontsize=6.5)
axr = fig.add_subplot(gs[2, :])
tgrid = (P[0]['edges'][:-1] - P[0]['s']) / 1000.0
axr.plot(tgrid, r0, color='black', lw=0.9, label='ceiling, night')
axr.plot(tgrid, P[1]['rate'] / P[1]['rate'].mean(), color='0.55', lw=0.9,
         ls='--', label='daytime')
for idx, tag in [(IPK, 'peak'), (ITR, 'trough')]:
    axr.axvline(tgrid[idx] + SLICE / 2000.0, color='0.3', lw=0.5, ls=':')
axr.set_xlim(0, SPAN / 1000.0)
axr.set_ylim(0, 1.9)
axr.set_xlabel('time inside the window (ms)', labelpad=1.5)
axr.set_ylabel('rate / mean', fontsize=6.5)
axr.legend(loc='lower right', ncol=2, borderaxespad=0.1)
for sp in ('top', 'right'):
    axr.spines[sp].set_visible(False)
fig.savefig(os.path.join(FIGS, 'fig7_ceiling_vs_day.pdf'), dpi=300)
plt.close(fig)
stats = {p['seq']: dict(events=int(len(p['t'])), span_us=SPAN, slice_us=SLICE,
                        rate_max_over_min=float(p['rate'].max() /
                                                max(p['rate'].min(), 1)))
         for p in P}
json.dump(stats, open(os.path.join(ROOT, 'experiments/e00_exposure_survey/'
                                   'fig7_stats.json'), 'w'), indent=1)
print('WROTE fig7_ceiling_vs_day.pdf', json.dumps(stats), flush=True)
