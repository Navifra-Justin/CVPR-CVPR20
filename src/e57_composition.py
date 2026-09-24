"""E57 - the label composition that decides whether a timing difference is visible at all.

Displacing a box by a timing error tau moves it tau*|v| pixels, and what an IoU-thresholded
metric registers is that displacement relative to the box's own size. The scale-free quantity
is therefore

    r = |v| / sqrt(w*h)          box-widths of motion per second,

and the pixel displacement of a tau-second timing error is tau * r box-widths. r is invariant
to sensor resolution, so two benchmarks at different resolutions are directly comparable on it.

This computes the distribution of r for Gen1 (from E51's ground-truth dump, whose centered
velocities the manuscript already uses) and for DSEC-Det (from the released `tracks.npy`,
where track_id gives the association directly rather than by IoU linking). A third column
reports the Gen1 subset with |v| >= 25 px/s, the stratum in which the released checkpoints sit
closest together.

E56e later showed that the median is the wrong summary: because mAP thresholds each box rather
than averaging over them, the level at which a loss is read off selects the quantile of r that
sets the timescale, and the first few percent of loss are bought from the upper tail. So the
comparison between benchmarks is repeated here on Q95, and on Q95 discounted by the sampling
noise each population's size implies -- the quantity that decides whether a benchmark can
actually resolve a timing difference.
"""
import numpy as np, glob, os, json

OUT = 'experiments/e56_resolving/composition.json'


def gen1(lo=None, hi=None):
    G = np.load('experiments/e51_ranking/dets-rvt-t.npz')['gt'].astype(np.float64)
    w = G[:, 3] - G[:, 1]; h = G[:, 4] - G[:, 2]
    sp = np.hypot(G[:, 6], G[:, 7])
    m = np.isfinite(sp) & (w > 0) & (h > 0)
    if lo is not None:
        m &= (sp >= lo) & (sp < hi)
    return sp[m] / np.sqrt((w * h)[m]), sp[m], np.sqrt((w * h)[m])


def dsec(split='train'):
    R = []; SP = []; SZ = []
    files = sorted(glob.glob(f'data/dsec_det/{split}/{split}/*/object_detections/left/tracks.npy'))
    for f in files:
        T = np.load(f)
        for tid in np.unique(T['track_id']):
            s = T[T['track_id'] == tid]
            if len(s) < 3:
                continue
            s = s[np.argsort(s['t'])]
            cx = s['x'] + s['w'] / 2; cy = s['y'] + s['h'] / 2
            t = s['t'].astype(np.float64) * 1e-6          # tracks.npy timestamps are us (dt = 50.00 ms)
            dt = t[2:] - t[:-2]
            ok = dt > 0
            vx = np.where(ok, (cx[2:] - cx[:-2]) / np.where(ok, dt, 1), np.nan)
            vy = np.where(ok, (cy[2:] - cy[:-2]) / np.where(ok, dt, 1), np.nan)
            sp = np.hypot(vx, vy)
            sz = np.sqrt(s['w'][1:-1] * s['h'][1:-1])
            g = np.isfinite(sp) & (sz > 0)
            R.append(sp[g] / sz[g]); SP.append(sp[g]); SZ.append(sz[g])
    return (np.concatenate(R), np.concatenate(SP), np.concatenate(SZ)) if R else \
           (np.array([]), np.array([]), np.array([]))


def describe(name, r, sp, sz, n_files=None):
    q = lambda a, p: float(np.percentile(a, p))
    d = dict(name=name, n=int(len(r)),
             r_median=float(np.median(r)), r_mean=float(r.mean()),
             r_p75=q(r, 75), r_p90=q(r, 90), r_p95=q(r, 95), r_p99=q(r, 99),
             speed_median=float(np.median(sp)), speed_p90=q(sp, 90),
             size_median=float(np.median(sz)))
    print(f"{name:<22} n={d['n']:>7}  median r {d['r_median']:.5f}/s   p90 {d['r_p90']:.5f}/s"
          f"   median |v| {d['speed_median']:7.2f} px/s   median sqrt(area) {d['size_median']:6.2f} px")
    return d


if __name__ == '__main__':
    rows = []
    r, sp, sz = gen1(); rows.append(describe('Gen1 (all moving)', r, sp, sz))
    r, sp, sz = gen1(25., 50.); rows.append(describe('Gen1 (25-50 px/s)', r, sp, sz))
    r, sp, sz = gen1(50., 1e9); rows.append(describe('Gen1 (>50 px/s)', r, sp, sz))
    r, sp, sz = dsec('train'); rows.append(describe('DSEC-Det (train)', r, sp, sz))
    r, sp, sz = dsec('test'); rows.append(describe('DSEC-Det (test)', r, sp, sz))
    base = rows[0]['r_median']
    print(f"\nratio to Gen1 (all moving), on median r:")
    for d in rows:
        d['ratio_to_gen1'] = d['r_median'] / base
        print(f"  {d['name']:<22} {d['ratio_to_gen1']:6.2f}x")
    # The tail comparison (E56e). Resolution scales as the quantile that matches the loss
    # level; the standard error of the mAP difference scales as 1/sqrt(n). A population only
    # resolves better than Gen1 if it wins the first race by more than it loses the second.
    b95, bn = rows[0]['r_p95'], rows[0]['n']
    print(f"\n{'population':<22} {'n':>7} {'median':>8} {'Q95':>8} {'med ratio':>10}"
          f" {'Q95 ratio':>10} {'net of sqrt(n)':>15}")
    for d in rows:
        d['ratio_q95'] = d['r_p95'] / b95
        d['net_of_n'] = d['ratio_q95'] / np.sqrt(bn / max(d['n'], 1))
        print(f"  {d['name']:<20} {d['n']:>7} {d['r_median']:8.4f} {d['r_p95']:8.4f}"
              f" {d['ratio_to_gen1']:9.2f}x {d['ratio_q95']:9.2f}x {d['net_of_n']:14.2f}x")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(rows, open(OUT, 'w'), indent=1)
    print(f"\nWROTE {OUT}")
