"""Render every figure in paper/figs/ from the measured JSON files in experiments/.

Times-family fonts (Nimbus Roman, metric-compatible with Times New Roman), no
colour-only encoding: every series is separated by marker, hatch or line style as
well as by grey level.

    python3 src/make_figs.py
"""
import glob
import json
import os
import re

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXP = os.path.join(ROOT, 'experiments')
FIGS = os.path.join(ROOT, 'paper', 'figs')
os.makedirs(FIGS, exist_ok=True)

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

COL = 3.32   # one column width, inches
FULL = 7.0   # two columns


def grp(n):
    """Integer grouped in threes, matching the paper's thousands separator.
    A plain space is used because Nimbus Roman carries no U+2009 glyph."""
    if abs(n) < 10000:            # four digits and fewer take no separator
        return '%d' % n
    return ' '.join(re.findall(r'\d{1,3}', ('%d' % n)[::-1]))[::-1]


def nospine(ax, which=('top', 'right')):
    for s in which:
        ax.spines[s].set_visible(False)


# ---------------------------------------------------------------- figure 1
def fig1_exposure():
    files = sorted(glob.glob(os.path.join(EXP, 'e00_exposure_survey', 'e_*.txt')))
    seqs = []
    for f in files:
        name = os.path.basename(f)[2:-4]
        rows = [l.split(',') for l in open(f) if not l.startswith('#') and l.strip()]
        w = np.array([int(b) - int(a) for a, b in rows])
        seqs.append((name, w))
    seqs.sort(key=lambda s: np.median(s[1]))
    allw = np.concatenate([w for _, w in seqs])
    gap = ((allw > 4207) & (allw < 14996)).sum()

    fig, (axl, axr) = plt.subplots(1, 2, figsize=(FULL, 1.92),
                                   gridspec_kw={'width_ratios': [2.5, 1]})
    for i, (name, w) in enumerate(seqs):
        q = np.percentile(w, [5, 25, 50, 75, 95])
        axl.plot([q[0], q[4]], [i, i], color='0.65', lw=0.8, zorder=1)
        axl.plot([q[1], q[3]], [i, i], color='0.25', lw=2.2,
                 solid_capstyle='butt', zorder=2)
        axl.plot(q[2], i, 'o', ms=2.6, color='white', mec='black', mew=0.6, zorder=3)
    axl.axvline(50000, color='0.1', lw=0.9, ls='--', zorder=0)
    axl.text(50000, len(seqs) - 0.4, ' frame period\n 50 ms', fontsize=6.5,
             va='top', ha='left')
    axl.axvline(14996, color='0.1', lw=0.9, ls=':', zorder=0)
    axl.text(14996, 1.2, 'ceiling\n%s $\\mu$s ' % grp(14996), fontsize=6.5,
             va='bottom', ha='right')
    axl.set_yticks(np.arange(len(seqs)))
    axl.set_yticklabels([n for n, _ in seqs], fontsize=5.6)
    axl.set_xscale('log')
    axl.set_xlim(80, 90000)
    axl.set_ylim(-0.8, len(seqs) - 0.2)
    axl.set_xlabel('exposure width per frame ($\\mu$s, log scale)')
    nospine(axl)

    bins = np.logspace(np.log10(100), np.log10(20000), 60)
    axr.hist(allw, bins=bins, color='0.35', edgecolor='none')
    axr.set_xscale('log')
    axr.set_xlim(100, 20000)
    axr.axvline(14996, color='0.1', lw=0.9, ls=':')
    axr.set_xlabel('exposure width ($\\mu$s)')
    axr.set_ylabel('frames')
    axr.set_ylim(0, 8600)
    axr.annotate('%s of %s frames\nat the ceiling' % (grp((allw == 14996).sum()), grp(len(allw))),
                 xy=(14996, 6866), xytext=(560, 7750), fontsize=6.3, ha='left',
                 va='center',
                 arrowprops=dict(arrowstyle='-', lw=0.6, color='0.4',
                                 connectionstyle='arc3,rad=-0.15'))
    axr.axvspan(4207, 14996, color='0.85', zorder=0)
    axr.annotate('', xy=(4207, 1100), xytext=(14996, 1100),
                 arrowprops=dict(arrowstyle='<->', lw=0.6, color='0.3'))
    axr.text(6300, 1500, '%s frames between\n%s and %s $\\mu$s' % (grp(gap), grp(4207), grp(14996)),
             fontsize=6.2, ha='center', va='bottom', color='0.2')
    nospine(axr)

    fig.tight_layout(pad=0.35)
    out = os.path.join(FIGS, 'fig1_dsec_exposure.pdf')
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    print('fig1', len(seqs), 'sequences', len(allw), 'frames, gap count', gap)


# ---------------------------------------------------------------- figure 2
def fig2_evidence_time():
    d = json.load(open(os.path.join(EXP, 'e09_per_object_evidence_time',
                                    'zurich_city_09_a.json')))
    rows = d['rows']
    sd = np.array([r['sd_tbar_us'] for r in rows])
    nl = np.array([r['sd_null_us'] for r in rows])

    cand = [r for r in rows if r['n_obj'] == 8]
    frame = min(cand, key=lambda r: abs(r['sd_tbar_us'] - np.median(sd)))
    tb = np.array(frame['tbar'], dtype=float)
    nev = np.array(frame['n_ev'], dtype=float)
    order = np.argsort(tb)
    tb, nev = tb[order], nev[order]
    w = frame['w_us']

    fig = plt.figure(figsize=(COL, 3.35))
    gs = fig.add_gridspec(3, 1, height_ratios=[0.20, 0.85, 1.10], hspace=0.62)
    axc, axa, axb = (fig.add_subplot(gs[0]), fig.add_subplot(gs[1]),
                     fig.add_subplot(gs[2]))

    span = float(tb.max() - tb.min())
    lo, hi = tb.min() - 0.55 * span, tb.max() + 0.12 * span

    # (a, top strip) the whole exposure window, with the zoomed interval marked
    axc.axhspan(0, 1, xmin=0, xmax=1, color='0.92', zorder=0)
    axc.axvline(0, color='0.1', lw=0.9, ls='--', zorder=2)
    axc.axvspan(lo, hi, facecolor='none', edgecolor='black', lw=0.7, zorder=3)
    axc.set_xlim(-w / 2.0, w / 2.0)
    axc.set_ylim(0, 1)
    axc.set_yticks([])
    axc.set_xticks([-7000, -3500, 0, 3500, 7000])
    axc.tick_params(axis='x', length=2, pad=1.5)
    axc.text(-w / 2.0 + 150, 0.55, 'exposure window, %s $\\mu$s' % grp(w),
             fontsize=5.8, ha='left', va='center', color='0.3')
    for s in ('top', 'right', 'left'):
        axc.spines[s].set_visible(False)

    # (a) one frame, zoomed on the box centroids
    y = np.arange(len(tb))
    axa.axvline(0, color='0.1', lw=0.9, ls='--', zorder=1)
    axa.plot(tb, y, 'o', ms=4.0, color='0.15', mec='black', mew=0.5, zorder=3)
    for i in range(len(tb)):
        axa.plot([lo, tb[i]], [y[i], y[i]], color='0.6', lw=0.6, zorder=2)
        axa.text(lo + 0.02 * span, y[i] + 0.16, '%s events' % grp(nev[i]), fontsize=5.2,
                 ha='left', va='bottom', color='0.35')
    axa.set_ylim(-0.8, len(tb) - 0.2)
    axa.set_yticks([])
    axa.set_xlim(lo, hi)
    axa.set_xlabel('evidence time $\\bar{t}_i$, relative to the '
                   'indexed timestamp ($\\mu$s)')
    axa.text(0.03 * span, -0.75, 'indexed timestamp', fontsize=6.0, ha='left',
             va='bottom')
    axa.set_ylabel('one frame,\n%d objects' % len(tb), fontsize=6.5)
    nospine(axa)
    axa.spines['left'].set_visible(False)

    # (b) 1133 frames: sd against its own analytic null
    bins = np.linspace(0, 620, 63)
    axb.hist(sd, bins=bins, color='0.35', edgecolor='none',
             label='measured, within-frame sd')
    axb.hist(nl, bins=bins, histtype='step', color='black', lw=0.9, ls='--',
             hatch='///', label='analytic null $w^2/12N_i$')
    top = axb.get_ylim()[1] * 1.22
    axb.plot([np.median(sd)] * 2, [0, top * 0.88], color='0.15', lw=0.8)
    axb.plot([np.median(nl)] * 2, [0, top * 0.88], color='0.15', lw=0.8, ls=':')
    axb.text(np.median(sd) + 8, top * 0.89, '%.1f' % np.median(sd), fontsize=6.0,
             ha='left', va='bottom')
    axb.text(np.median(nl) - 8, top * 0.89, '%.1f' % np.median(nl), fontsize=6.0,
             ha='right', va='bottom')
    axb.set_xlim(0, 620)
    axb.set_ylim(0, top)
    axb.set_xlabel('within-frame sd of $\\bar{t}_i$ ($\\mu$s)')
    axb.set_ylabel('frames (of %d)' % len(rows))
    axb.legend(loc='upper right', handlelength=1.6)
    nospine(axb)

    fig.savefig(os.path.join(FIGS, 'fig2_evidence_time.pdf'), bbox_inches='tight')
    plt.close(fig)
    print('fig2 frame t=%d n=%d sd=%.1f' % (frame['t'], frame['n_obj'],
                                            frame['sd_tbar_us']))


# ---------------------------------------------------------------- figure 3
def fig3_day_night():
    night = json.load(open(os.path.join(EXP, 'e09_per_object_evidence_time',
                                        'zurich_city_09_a.json')))['summary']
    day = json.load(open(os.path.join(EXP, 'e09_per_object_evidence_time',
                                      'interlaken_00_c.json')))['summary']
    ray = json.load(open(os.path.join(EXP, 'e10_flicker', 'rayleigh.json')))

    fig, (axa, axb) = plt.subplots(1, 2, figsize=(COL, 1.85))

    # (a) dispersion, day against night
    labels = ['night\n%s $\\mu$s exp.' % grp(round(night['exposure_us_med'])),
              'day\n%s $\\mu$s exp.' % grp(round(day['exposure_us_med']))]
    meas = [night['sd_tbar_us_med'], day['sd_tbar_us_med']]
    null = [night['sd_null_us_med'], day['sd_null_us_med']]
    x = np.arange(2)
    axa.bar(x - 0.19, meas, 0.36, color='0.35', edgecolor='none', label='measured sd')
    axa.bar(x + 0.19, null, 0.36, facecolor='white', edgecolor='black', lw=0.7,
            hatch='///', label='analytic null')
    for i in range(2):
        axa.text(x[i] - 0.19, meas[i] + 6, '%.1f' % meas[i], fontsize=5.8,
                 ha='center', va='bottom')
        axa.text(x[i] + 0.19, null[i] + 6, '%.1f' % null[i], fontsize=5.8,
                 ha='center', va='bottom')
    axa.set_xticks(x)
    axa.set_xticklabels(labels, fontsize=6.0)
    axa.set_ylabel('within-frame sd of $\\bar{t}_i$ ($\\mu$s)')
    axa.set_ylim(0, 285)
    axa.legend(loc='upper right', handlelength=1.4, borderpad=0.1)
    nospine(axa)

    # (b) per-pixel Rayleigh statistic against the Exp(1) null. Two tick labels
    # rather than four: the tested frequency is carried by the marker, so the
    # labels cannot overprint at column width, and the two reference levels are
    # named in the legend rather than annotated inside the axes.
    arms = {'night': (ray['NIGHT']['100Hz'], ray['NIGHT']['137Hz_control']),
            'day': (ray['DAY']['100Hz'], ray['DAY']['137Hz_control'])}
    xs = np.arange(2)
    keys = ['night', 'day']
    for j, off, mfc, mew, lab in ((0, -0.14, '0.15', 0.5, '100 Hz'),
                                  (1, +0.14, 'white', 0.8, '137 Hz')):
        med = [arms[k][j]['median_Z'] for k in keys]
        p95 = [arms[k][j]['p95_Z'] for k in keys]
        for i in range(2):
            axb.plot([xs[i] + off] * 2, [med[i], p95[i]], color='0.6', lw=0.6, zorder=0)
        axb.plot(xs + off, med, 'o', ms=4.0, mfc=mfc, mec='black', mew=mew, label=lab)
        axb.plot(xs + off, p95, '_', ms=5.0, color='0.35', mew=0.9)
    axb.axhline(3.00, color='0.1', lw=0.7, ls=':', label='null p95')
    axb.axhline(0.693, color='0.1', lw=0.7, ls='--', label='null median')
    axb.set_yscale('log')
    axb.set_ylim(0.35, 60)
    axb.set_xlim(-0.5, 1.5)
    axb.set_xticks(xs)
    axb.set_xticklabels(keys, fontsize=6.5)
    axb.set_ylabel('per-pixel Rayleigh $Z$')
    axb.legend(loc='upper left', handlelength=1.1, borderpad=0.1,
               labelspacing=0.22, fontsize=5.5, handletextpad=0.4, ncol=2,
               columnspacing=0.7)
    nospine(axb)

    fig.tight_layout(pad=0.30, w_pad=1.1)
    fig.savefig(os.path.join(FIGS, 'fig3_day_night.pdf'), bbox_inches='tight')
    plt.close(fig)
    print('fig3 night sd %.1f day sd %.1f' % (night['sd_tbar_us_med'],
                                              day['sd_tbar_us_med']))


# --------------------------------------------------- figure 4 (E12) RETRACTED
# fig4_integer_period() rendered the four analysis-window widths of E12. The
# integer-period cancellation argument those widths were reported under is wrong
# and was retracted on 2026-09-03, so the figure is not rendered and the file is
# not referenced by the paper.


# ---------------------------------------------------------------- the predictor
def fig_predictor():
    """(a) the measured temporal influence profile of the released rvt-t
    checkpoint (E17); (b) average precision against the instant the ground truth
    describes, by object speed (E37)."""
    # E45, not E17: E17 handed the occluded pass the state its reference pass returned
    # rather than the state entering the step. See experiments/e45_influence_fixed.
    d = json.load(open(os.path.join(EXP, 'e45_influence_fixed', 'result.json')))
    c = np.array(d['centres'], dtype=float)
    a = np.array(d['zero']['mean'], dtype=float)
    e = np.array(d['zero']['sem'], dtype=float)
    cen = d['zero']['centroid_ms']

    # the regression-based temporal coefficient of Sec. 3.4, placed on this same axis as
    # the effective timestamp tau_P = -tau, so panel (a) carries both timing quantities
    R = json.load(open(os.path.join(EXP, 'e27_rows', 'placebo_diag.json')))['perseq4']
    tp, tpse = -R['tau'], R['tau_se']

    fig, (axa, axb) = plt.subplots(2, 1, figsize=(COL, 2.76),
                                  gridspec_kw={'height_ratios': [1.0, 1.10]})

    axa.bar(c, a, width=4.2, color='0.72', edgecolor='black', lw=0.5, zorder=2)
    axa.errorbar(c, a, yerr=e, fmt='none', ecolor='black', elinewidth=0.8,
                 capsize=1.6, zorder=3)
    axa.axhline(a.mean(), color='0.1', lw=0.7, ls='--', zorder=4)
    axa.axvline(cen, color='black', lw=1.1, zorder=5)
    axa.axvline(0.0, color='0.1', lw=1.0, ls=':', zorder=5)
    axa.axvline(tp, color='0.1', lw=1.1, ls=(0, (5, 1.4, 1, 1.4)), zorder=5)
    top = a.max() * 1.72
    axa.set_ylim(0, top)
    axa.set_xlim(-54, 19)
    axa.text(-53.0, top * 0.985, 'newest-window\nsensitivity centroid\n\u2212%.2f ms' % abs(cen),
             fontsize=6.6, va='top', ha='left')
    axa.text(18.0, top * 0.985, 'regression\n$\\tau_P\\!=\\!%+.2f$ ms' % tp,
             fontsize=6.6, va='top', ha='right')
    axa.errorbar([tp], [top * 0.615], xerr=[[tpse], [tpse]], fmt='D', ms=2.4,
                 color='0.1', elinewidth=0.9, capsize=2.2, zorder=7)
    axa.annotate('', xy=(cen, top * 0.27), xytext=(tp, top * 0.27),
                 arrowprops=dict(arrowstyle='<->', lw=0.7, color='0.1'))
    axa.text((cen + tp) / 2.0, top * 0.27, '%.1f ms' % abs(tp - cen),
             fontsize=6.6, ha='center', va='center',
             bbox=dict(fc='white', ec='none', pad=0.9))
    axa.text(-1.6, top * 0.735, 'label instant', fontsize=6.0, va='center',
             ha='right', color='0.15')
    # the other released checkpoints, each rescaled to its own mean so the shapes are
    # comparable on one axis (E48 for RVT's three, E47 for SSM-ViT's two). Drawn thin and
    # grey: the claim they carry is that the centroid does not move, not their detail.
    others = []
    for pth, lab in (('e48_matched_frames/rvt-s.json', 'rvt-s'),
                     ('e48_matched_frames/rvt-b.json', 'rvt-b'),
                     ('e47_ssm/s5vit-small-chunked.json', 'S5-ViT-S'),
                     ('e47_ssm/s5vit-base-chunked.json',  'S5-ViT-B')):
        f = os.path.join(EXP, pth)
        if os.path.exists(f):
            o = json.load(open(f))
            others.append((np.array(o['bin_influence'], dtype=float), lab))
    for prof, lab in others:
        axa.plot(c, prof / prof.mean() * a.mean(), color='0.35', lw=0.6,
                 marker='o', ms=1.3, zorder=6, alpha=0.85)
    axa.set_xlabel('bin center, relative to the label time (ms)', fontsize=8)
    axa.set_ylabel('window-ablation\ninfluence', fontsize=8)
    nospine(axa)

    # (b) average precision as a function of the instant the ground truth describes
    # (E37, experiments/e37_map/strata.json). Panel (b) previously repeated Table 1's
    # specification ladder; the ladder has a table and this curve does not.
    S = json.load(open(os.path.join(EXP, 'e37_map', 'strata.json')))
    order = [('all moving', 'all moving', 'black', '-', 1.5),
             ('slow, |v| < 10', r'$|v|<10$', '0.62', '-', 1.0),
             ('10 <= |v| < 25', r'$10\!\leq\!|v|\!<\!25$', '0.42', '--', 1.0),
             ('25 <= |v| < 50', r'$25\!\leq\!|v|\!<\!50$', '0.15', '-.', 1.1)]
    axb.axvspan(cen, 0.0, color='0.94', zorder=0)   # read from the artifact, never typed
    axb.axvline(0.0, color='0.1', lw=0.8, ls=':', zorder=2)
    axb.axvline(cen, color='0.1', lw=0.8, ls='--', zorder=2)
    for key, lab, col, ls, lw in order:
        d = np.array(S[key]['deltas_ms']); m = np.array(S[key]['map'])
        z = int(np.argmin(np.abs(d)))
        axb.plot(d, 100.0 * (m - m[z]), ls, color=col, lw=lw, zorder=3, label=lab)
        k = int(np.argmax(m))
        axb.plot([d[k]], [100.0 * (m[k] - m[z])], 'o', ms=2.8, color=col, zorder=4)
    axb.set_xlim(-54, 32)
    axb.set_xlabel('the instant the ground truth describes, $\\delta$ (ms)', fontsize=8)
    axb.set_ylabel('mAP relative to $\\delta=0$ (points)', fontsize=8)
    lo, hi = axb.get_ylim()
    axb.set_ylim(lo, hi + 0.78 * (hi - lo))
    lo, hi = axb.get_ylim()
    # the term "evidence centroid" was withdrawn: this line is the newest window's
    # centroid, not the centroid of the whole support, and the label must say so
    axb.text(cen + 0.9, lo + 0.02 * (hi - lo), 'newest-window centroid',
             fontsize=6.3, rotation=90, va='bottom', ha='left', color='0.35')
    axb.text(1.3, lo + 0.02 * (hi - lo), 'label instant', fontsize=6.3,
             rotation=90, va='bottom', ha='left', color='0.35')
    axb.legend(fontsize=6.3, loc='upper center', frameon=False, ncol=4,
               handlelength=1.5, handletextpad=0.35, columnspacing=0.75,
               borderaxespad=0.1, labelspacing=0.22)
    nospine(axb)

    for ax in (axa, axb):
        ax.tick_params(labelsize=7.4)
    fig.tight_layout(pad=0.30, h_pad=1.1)
    fig.savefig(os.path.join(FIGS, 'fig_predictor.pdf'), bbox_inches='tight')
    plt.close(fig)
    print('fig_predictor centroid %.3f ms, CV %.4f, tau_P %+.3f +- %.3f, gap %.2f ms'
          % (cen, a.std(ddof=0) / a.mean(), tp, tpse, abs(tp - cen)))


if __name__ == '__main__':
    fig1_exposure()
    fig3_day_night()
    fig_predictor()
