import glob, os, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

files = sorted(glob.glob('/work/experiments/e00_exposure_survey/e_*.txt'))
seqs = []
for f in files:
    name = os.path.basename(f)[2:-4]
    rows = [l.split(',') for l in open(f) if not l.startswith('#') and l.strip()]
    w = np.array([int(b) - int(a) for a, b in rows])
    seqs.append((name, w))
seqs.sort(key=lambda s: np.median(s[1]))
allw = np.concatenate([w for _, w in seqs])
print("sequences", len(seqs), "frames", len(allw),
      "min", allw.min(), "max", allw.max(),
      "pinned", int((allw == 14996).sum()), "%.1f%%" % (100*(allw == 14996).mean()))

plt.rcParams.update({'font.size': 7, 'font.family': 'serif',
                     'font.serif': ['Nimbus Roman', 'Times New Roman', 'Times', 'DejaVu Serif'],
                     'mathtext.fontset': 'stix', 'pdf.fonttype': 42,
                     'axes.linewidth': 0.6, 'xtick.major.width': 0.6,
                     'ytick.major.width': 0.6})
fig, (axl, axr) = plt.subplots(1, 2, figsize=(7.0, 2.5),
                               gridspec_kw={'width_ratios': [2.5, 1]})

# LEFT: per-sequence exposure width distribution, log scale
pos = np.arange(len(seqs))
for i, (name, w) in enumerate(seqs):
    q = np.percentile(w, [5, 25, 50, 75, 95])
    axl.plot([q[0], q[4]], [i, i], color='0.65', lw=0.8, zorder=1)
    axl.plot([q[1], q[3]], [i, i], color='0.25', lw=2.2, solid_capstyle='butt', zorder=2)
    axl.plot(q[2], i, 'o', ms=2.6, color='white', mec='black', mew=0.6, zorder=3)
axl.axvline(50000, color='C3', lw=0.9, ls='--', zorder=0)
axl.text(50000, len(seqs)-0.4, ' frame period\n 50 ms', color='C3', fontsize=6.5,
         va='top', ha='left')
axl.axvline(14996, color='C0', lw=0.9, ls=':', zorder=0)
axl.text(14996, 1.2, 'ceiling\n14996 µs ', color='C0', fontsize=6.5, va='bottom', ha='right')
axl.set_yticks(pos); axl.set_yticklabels([n for n, _ in seqs], fontsize=5.6)
axl.set_xscale('log'); axl.set_xlim(80, 90000)
axl.set_ylim(-0.8, len(seqs)-0.2)
axl.set_xlabel('exposure width per frame (µs, log scale)')
for s in ('top', 'right'): axl.spines[s].set_visible(False)

# RIGHT: pooled histogram
bins = np.logspace(np.log10(100), np.log10(20000), 60)
axr.hist(allw, bins=bins, color='0.35', edgecolor='none')
axr.set_xscale('log'); axr.set_xlim(100, 20000)
axr.axvline(14996, color='C0', lw=0.9, ls=':')
axr.set_xlabel('exposure width (µs)')
axr.set_ylabel('frames')
frac = 100*(allw == 14996).mean()
axr.set_ylim(0, 8600)
axr.annotate('%.1f%% of %d frames\nat the ceiling' % (frac, len(allw)),
             xy=(14996, 6866), xytext=(2600, 7600), fontsize=6.3, ha='left', va='center',
             arrowprops=dict(arrowstyle='-', lw=0.6, color='0.4',
                             connectionstyle='arc3,rad=-0.15'))
axr.annotate('', xy=(5000, 900), xytext=(13000, 900),
             arrowprops=dict(arrowstyle='<->', lw=0.6, color='0.55'))
axr.text(8000, 1700, 'little mass\n5 to 15 ms', fontsize=6.2, ha='center',
         va='bottom', color='0.4')
for s in ('top', 'right'): axr.spines[s].set_visible(False)

fig.tight_layout(pad=0.35)
fig.savefig('/work/paper/figs/fig1_dsec_exposure.pdf', bbox_inches='tight')
print("WROTE fig1")
