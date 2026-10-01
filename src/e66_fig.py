"""E66 figure: mAP of the five released Gen1 checkpoints under fixed recurrent history H.

Reads experiments/e66_fixedH/results.json only. The right-hand marker of each curve is the
released pooled score restricted to the same common frames (heterogeneous H, release-specific
weights); the four points to its left are exactly H = 1, 5, 10, 21 windows.
"""
import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.size': 7, 'font.family': 'serif',
    'font.serif': ['Nimbus Roman', 'Times New Roman', 'Times', 'DejaVu Serif'],
    'axes.linewidth': 0.6, 'xtick.major.width': 0.6, 'ytick.major.width': 0.6,
    'xtick.labelsize': 6.5, 'ytick.labelsize': 6.5, 'axes.labelsize': 7,
    'legend.fontsize': 6.3, 'legend.frameon': False, 'pdf.fonttype': 42,
})
R = json.load(open('experiments/e66_fixedH/results.json'))
SPEC = [('s5vit-base', 'S5-B', '#c0392b', 'o', '-'), ('s5vit-small', 'S5-S', '#e67e22', 's', '-'),
        ('rvt-b', 'RVT-b', '#2c3e50', 'o', '--'), ('rvt-s', 'RVT-s', '#5d6d7e', 's', '--'),
        ('rvt-t', 'RVT-t', '#99a3a4', '^', '--')]
xs = [0, 1, 2, 3]; XP = 4.4
f, a = plt.subplots(figsize=(3.32, 1.9))
for k, lb, c, mk, ls in SPEC:
    y = [R['map'][k][h] for h in ('H1', 'H5', 'H10', 'H21')]
    a.plot(xs, y, ls, color=c, lw=1.2, marker=mk, ms=3.0, label=lb)
    a.plot([XP], [R['map'][k]['pooled']], marker=mk, ms=3.6, color=c, mfc='none', mew=0.9, ls='none')
a.axvline(3.7, color='0.75', lw=0.5, ls=':')
a.set_xticks(xs + [XP]); a.set_xticklabels(['1', '5', '10', '21', 'pooled'])
a.set_xlim(-0.3, 4.8); a.set_xlabel('recurrent windows allowed before the scored window ($H$)')
a.set_ylabel('mAP (%)')
a.tick_params(length=2.5, pad=1.5)
for sp in ('top', 'right'):
    a.spines[sp].set_visible(False)
a.grid(axis='y', color='0.9', lw=0.5, zorder=0)
a.legend(loc='upper left', ncol=2, handlelength=1.8, borderpad=0.1, labelspacing=0.25, columnspacing=1.0)
a.set_ylim(26, 46.5)
f.tight_layout(pad=0.2)
f.savefig('paper/figs/e66_hcurve.pdf', bbox_inches='tight', pad_inches=0.01)
print('WROTE paper/figs/e66_hcurve.pdf')
