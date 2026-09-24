"""Video clip 8 - the headline result, as the measured curve it was read from.

Under the released streaming evaluation, a detection's position inside the evaluation
chunk fixes how much recurrent history it was produced from: one window at the first
position, twenty-one at the last.  mAP is plotted against that position for all five
released checkpoints.  The two SSM checkpoints rise across the chunk; the three RVT
checkpoints, whose state crosses chunk boundaries, do not.  The closing frames state the
difference-in-differences after the RVT control, with its sequence-bootstrap error.

Every number is read from the experiment artifacts at render time.
"""
import numpy as np, json, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

W = '/work'
CV = json.load(open(f'{W}/experiments/e58_chunkpos/curve.json'))['map']
AB = json.load(open(f'{W}/experiments/e58_chunkpos/allbox.json'))
SSM = ['s5vit-small', 's5vit-base']
RVT = ['rvt-t', 'rvt-s', 'rvt-b']
NAME = {'rvt-t': 'RVT-T', 'rvt-s': 'RVT-S', 'rvt-b': 'RVT-B',
        's5vit-small': 'S5-ViT-S', 's5vit-base': 'S5-ViT-B'}
SHORT, FULL = (0, 4), (16, 21)
Y = {k: np.array(v, float) * 100 for k, v in CV.items()}
NPOS = len(Y['rvt-t'])
X = np.arange(1, NPOS + 1)
DID = -AB['did']['s5vit-base']; DSE = AB['boot']['s5vit-base']['se']
DIDS = -AB['did']['s5vit-small']; DSES = AB['boot']['s5vit-small']['se']
PLAC = max(abs(AB['did'][m]) for m in RVT)

OUT = f'{W}/video/frames/v08'; os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({'font.size': 9, 'font.family': 'serif',
                     'font.serif': ['Nimbus Roman', 'Times New Roman', 'Times', 'DejaVu Serif'],
                     'mathtext.fontset': 'stix', 'axes.linewidth': 0.8,
                     'text.color': 'white', 'axes.labelcolor': 'white',
                     'xtick.color': 'white', 'ytick.color': 'white'})
GOLD = '#ffd24a'; BLUE = '#4ad2ff'

NA = 4 * NPOS          # the curve arrives position by position
NB = 30                # the two ends of the chunk are marked
NC = 42                # the controlled difference is stated
TOT = NA + NB + NC

def frame(i):
    upto = min(NPOS, i // 4 + 1) if i < NA else NPOS
    mark = i >= NA
    read = i >= NA + NB
    fig = plt.figure(figsize=(12.8, 7.2), facecolor='black')
    ax = fig.add_axes([0.085, 0.14, 0.885, 0.70]); ax.set_facecolor('black')
    if mark:
        ax.axvspan(X[SHORT[0]] - 0.5, X[SHORT[1] - 1] + 0.5, color='white', alpha=0.11, zorder=1)
        ax.axvspan(X[FULL[0]] - 0.5, X[FULL[1] - 1] + 0.5, color='white', alpha=0.11, zorder=1)
        ax.text(2.5, 46.3, '1 to 4 windows of history', color='0.85', fontsize=12,
                ha='center', va='bottom')
        ax.text(19.0, 46.3, '17 to 21 windows of history', color='0.85', fontsize=12,
                ha='center', va='bottom')
    for k in RVT + SSM:
        col = BLUE if k in SSM else GOLD
        ax.plot(X[:upto], Y[k][:upto], color=col, lw=2.6 if k in SSM else 1.5,
                marker='o', ms=5 if k in SSM else 3,
                alpha=1.0 if k in SSM else 0.7, zorder=5 if k in SSM else 3)
    # end labels, nudged apart so no two overlap
    if upto:
        ends = sorted(((Y[k][upto - 1], k) for k in RVT + SSM))
        placed = []
        for y, k in ends:
            yy = y if not placed else max(y, placed[-1] + 0.95)
            placed.append(yy)
            ax.text(X[upto - 1] + 0.35, yy, NAME[k], color=BLUE if k in SSM else GOLD,
                    fontsize=12, va='center', ha='left')
    if read:
        ax.text(0.015, 0.995,
                f'S5-ViT-B   {DID:+.2f} $\\pm$ {DSE:.2f} mAP points,',
                transform=ax.transAxes, color=BLUE, fontsize=15, ha='left', va='top')
        ax.text(0.015, 0.930,
                'last five positions over first four, after the RVT control',
                transform=ax.transAxes, color=BLUE, fontsize=15, ha='left', va='top')
        ax.text(0.015, 0.862,
                f'S5-ViT-S  {DIDS:+.2f} $\\pm$ {DSES:.2f} points        '
                f'RVT placebo, largest of three  {PLAC:.2f} points',
                transform=ax.transAxes, color='0.88', fontsize=13, ha='left', va='top')
    ax.set_xlim(0.2, NPOS + 2.6); ax.set_ylim(28.8, 53.0)
    ax.set_xticks([1, 5, 9, 13, 17, 21]); ax.set_yticks([30, 34, 38, 42, 46])
    ax.set_xlabel('position of the detection inside the evaluation chunk '
                  '(windows of recurrent history available)', fontsize=13)
    ax.set_ylabel('mAP over every labeled box (%)', fontsize=13)
    fig.text(0.5, 0.945, 'one released streaming evaluation, one reported number, '
             'twenty-one different amounts of history',
             ha='center', color='white', fontsize=17)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    for sp in ('left', 'bottom'): ax.spines[sp].set_color('0.5')
    fig.savefig(f'{OUT}/{i:04d}.png', dpi=100, facecolor='black'); plt.close(fig)

for i in range(TOT):
    frame(i)
    if (i + 1) % 30 == 0: print(f'  {i+1}/{TOT}', flush=True)
print(f'WROTE {TOT} frames; DiD base {DID:.2f} +- {DSE:.2f}, small {DIDS:.2f}, placebo {PLAC:.2f}')
