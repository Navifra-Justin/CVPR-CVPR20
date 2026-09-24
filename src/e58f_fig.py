"""E58f - the chunk-position figure.

Panel (a) is mAP at each of the 21 chunk positions over every labeled box (E58e), so the
level matches a published table. Panel (b) is mean detection confidence at the same
positions (E58c), which uses neither the ground truth nor the evaluator. The three RVT
checkpoints are placebos: they are scored on the same frames and their state crosses chunk
boundaries, so a curve that rises only for the two SSM checkpoints cannot be a property of
which frames land early in a chunk.
"""
import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.size': 7, 'font.family': 'serif',
    'font.serif': ['Nimbus Roman', 'Times New Roman', 'Times', 'DejaVu Serif'],
    'mathtext.fontset': 'stix', 'axes.linewidth': 0.6,
    'xtick.major.width': 0.6, 'ytick.major.width': 0.6,
    'xtick.labelsize': 6.5, 'ytick.labelsize': 6.5,
    'axes.labelsize': 7, 'legend.fontsize': 6.3, 'legend.frameon': False,
    'pdf.fonttype': 42,
})

CUR = json.load(open('experiments/e58_chunkpos/curve.json'))
IV = json.load(open('experiments/e58_chunkpos/invariant.json'))['conf_by_position']
x = np.arange(1, 22)
SSM = [('s5vit-base', 'S5-B', '#c0392b', 'o'), ('s5vit-small', 'S5-S', '#e67e22', 's')]
RVT = [('rvt-b', 'RVT-B', 'o'), ('rvt-s', 'RVT-S', 's'), ('rvt-t', 'RVT-T', '^')]
G = '#8a9099'

COL, FULL = 3.32, 7.0
fig, ax = plt.subplots(1, 2, figsize=(FULL, 2.35))
for k, lb, m in RVT:
    ax[0].plot(x, np.array(CUR['map'][k]) * 100, '-', color=G, lw=0.9, marker=m, ms=2.4,
               mfc='none', mew=0.7, zorder=1)
    ax[1].plot(x, IV[k], '-', color=G, lw=0.9, marker=m, ms=2.4, mfc='none', mew=0.7, zorder=1)
for k, lb, c, m in SSM:
    ax[0].plot(x, np.array(CUR['map'][k]) * 100, '-', color=c, lw=1.5, marker=m, ms=3.2,
               label=lb, zorder=3)
    ax[1].plot(x, IV[k], '-', color=c, lw=1.5, marker=m, ms=3.2, label=lb, zorder=3)
ax[0].plot([], [], '-', color=G, lw=0.9, label='RVT-T/S/B (placebo)')

for a in ax:
    a.axvspan(0.5, 4.5, color='#2c3e50', alpha=0.07, lw=0, zorder=0)
    a.set_xlim(0.4, 21.6); a.set_xticks([1, 4, 8, 12, 16, 21])
    a.set_xlabel('windows of history available (50 ms each)', fontsize=7)
    a.tick_params(length=2.5, pad=1.5)
    for s in ('top', 'right'):
        a.spines[s].set_visible(False)
    a.grid(axis='y', color='0.9', lw=0.5, zorder=0)
ax[0].set_ylabel('mAP (%), every labeled box', fontsize=7)
ax[1].set_ylabel('mean detection confidence', fontsize=7)
ax[0].set_title('(a) benchmark score by chunk position', fontsize=7.5, pad=3)
ax[1].set_title('(b) label-free instrument', fontsize=7.5, pad=3)
ax[0].legend(fontsize=6.3, loc='lower right', frameon=False, handlelength=1.6,
             borderpad=0.1, labelspacing=0.25)
ax[0].set_ylim(29, 46.6)
fig.tight_layout(pad=0.25, w_pad=1.1)
fig.savefig('paper/figs/chunkpos_full.pdf', bbox_inches='tight', pad_inches=0.01)
print('WROTE paper/figs/chunkpos_full.pdf')

# single-column version for the main paper: panel (a) alone
f2, b = plt.subplots(figsize=(COL, 1.42))
for k, lb, m in RVT:
    b.plot(x, np.array(CUR['map'][k]) * 100, '-', color=G, lw=0.9, marker=m, ms=2.2,
           mfc='none', mew=0.7, zorder=1)
for k, lb, c, m in SSM:
    b.plot(x, np.array(CUR['map'][k]) * 100, '-', color=c, lw=1.4, marker=m, ms=3.0,
           label=lb, zorder=3)
b.plot([], [], '-', color=G, lw=0.9, label='RVT-T/S/B (placebo)')
b.axvspan(0.5, 4.5, color='#2c3e50', alpha=0.07, lw=0, zorder=0)
b.set_xlim(0.4, 21.6); b.set_ylim(29, 46.6); b.set_xticks([1, 4, 8, 12, 16, 21])
b.set_xlabel('windows of history available (50 ms each)')
b.set_ylabel('mAP (%)')
b.tick_params(length=2.5, pad=1.5)
for sp in ('top', 'right'):
    b.spines[sp].set_visible(False)
b.grid(axis='y', color='0.9', lw=0.5, zorder=0)
b.legend(loc='lower right', handlelength=1.6, borderpad=0.1, labelspacing=0.25)
f2.tight_layout(pad=0.2)
f2.savefig('paper/figs/chunkpos.pdf', bbox_inches='tight', pad_inches=0.01)
print('WROTE paper/figs/chunkpos.pdf')
print('S5-B  pos1 %.3f  pos17 %.3f  rise %.3f' % (CUR['map']['s5vit-base'][0]*100,
      CUR['map']['s5vit-base'][16]*100,
      (CUR['map']['s5vit-base'][16]-CUR['map']['s5vit-base'][0])*100))
print('rvt-t pos1 %.3f  pos17 %.3f  rise %.3f' % (CUR['map']['rvt-t'][0]*100,
      CUR['map']['rvt-t'][16]*100, (CUR['map']['rvt-t'][16]-CUR['map']['rvt-t'][0])*100))
