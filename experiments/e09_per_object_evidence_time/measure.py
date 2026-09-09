"""
E08 -- Per-object evidence-time dispersion inside ONE exposure, measured from the
sensor alone.  No detector, no checkpoint, no velocity denominator.

For each labelled frame of a DSEC sequence:
  * take that frame's own published exposure window [a, b] (E00 files),
  * slice the event stream to that window (random access via /ms_to_idx),
  * for each DSEC-Det labelled box i in that frame, take the events falling
    inside the box and compute the evidence-weighted time centroid
        tbar_i = mean(t_events_in_box_i)   (relative to the exposure midpoint)
  * report the dispersion of tbar_i ACROSS THE OBJECTS OF ONE FRAME.

The null is analytic, which is the point: if the evidence inside every box were
uniform over the exposure, tbar_i would have variance w^2/(12 N_i) with w the
exposure width and N_i the event count in box i.  So

    sigma_evt^2        = Var_i( tbar_i )
    sigma_evt,excess^2 = sigma_evt^2 - mean_i( w^2 / (12 N_i) )

and the subtrahend contains no assumed quantity.
"""
import h5py, hdf5plugin, numpy as np, sys, json, os

seq = sys.argv[1]
split = sys.argv[2] if len(sys.argv) > 2 else 'train'
MAXFR = int(sys.argv[3]) if len(sys.argv) > 3 else 400
MIN_EV = 200          # minimum events in a box for its centroid to be used
MIN_OBJ = 3           # minimum qualifying objects in a frame

root = f'/work/data/dsec/{seq}'
f = h5py.File(f'{root}/events.h5', 'r')
t_off = int(f['t_offset'][()]); ms2i = f['ms_to_idx'][:]; ev = f['events']
H, W = 480, 640

exp = [tuple(int(x) for x in l.split(','))
       for l in open(f'/work/experiments/e00_exposure_survey/e_{seq}.txt')
       if not l.startswith('#') and l.strip()]
exp = np.array(exp, dtype=np.int64)                       # (n,2) absolute us
mid = (exp[:, 0] + exp[:, 1]) // 2

lab = np.load(f'/work/data/dsec_det/{split}/{split}/{seq}/object_detections/left/tracks.npy')
lt = lab['t'].astype(np.int64)
ult = np.unique(lt)

def idx(t_abs, ceil=False):
    # /ms_to_idx is indexed by whole milliseconds.  ceil=True returns the index
    # one millisecond past t_abs, so that the raw slice [idx(a), idx(b, ceil))
    # is a superset of [a, b] and can then be filtered exactly.
    ms = (t_abs - t_off) // 1000 + (1 if ceil else 0)
    if ms < 0 or ms >= len(ms2i): return None
    return int(ms2i[ms])

rows = []
matched = 0
for ti in ult:
    # the exposure whose midpoint is closest to this label time
    j = int(np.argmin(np.abs(mid - ti)))
    if abs(int(mid[j]) - int(ti)) > 25000:   # more than half a frame period away
        continue
    a, b = int(exp[j, 0]), int(exp[j, 1])
    w = b - a
    i0, i1 = idx(a), idx(b, ceil=True)
    if i0 is None or i1 is None or i1 - i0 < 1000: continue
    matched += 1
    ex = ev['x'][i0:i1].astype(np.int32)
    ey = ev['y'][i0:i1].astype(np.int32)
    et = ev['t'][i0:i1].astype(np.int64) + t_off      # absolute us
    # /ms_to_idx resolves to whole milliseconds, so the slice above is
    # [floor(a), floor(b)] rather than [a, b].  Restrict it exactly, so that the
    # data and the analytic null (computed for w = b - a) come from the same
    # window.  Without this filter the two disagree; see e11/README.md.
    keep = (et >= a) & (et < b)
    ex, ey, et = ex[keep], ey[keep], et[keep]
    if et.size < 1000: continue
    m = lt == ti
    tb, nn, bid, pos = [], [], [], []
    for x, y, bw, bh, cid, tid in zip(lab['x'][m], lab['y'][m], lab['w'][m],
                                      lab['h'][m], lab['class_id'][m], lab['track_id'][m]):
        x0, y0 = int(max(0, x)), int(max(0, y))
        x1, y1 = int(min(W, x + bw)), int(min(H, y + bh))
        if x1 <= x0 or y1 <= y0: continue
        sel = (ex >= x0) & (ex < x1) & (ey >= y0) & (ey < y1)
        n = int(sel.sum())
        if n < MIN_EV: continue
        tb.append(float(et[sel].mean() - (a + b) / 2.0))   # us, rel. to mid-exposure
        nn.append(n); bid.append(int(tid))
        pos.append(((x0 + x1) / 2.0, (y0 + y1) / 2.0))
    if len(tb) < MIN_OBJ: continue
    # CONTROL: same box shapes, random positions -> is the dispersion object-specific
    # or a scene-wide property of where events land in the exposure?
    rtb, rnn = [], []
    rng = np.random.default_rng(int(ti) % (2**31))
    for x, y, bw, bh in zip(lab['x'][m], lab['y'][m], lab['w'][m], lab['h'][m]):
        bwi, bhi = int(min(W, max(1, bw))), int(min(H, max(1, bh)))
        for _ in range(6):
            x0 = int(rng.integers(0, max(1, W - bwi))); y0 = int(rng.integers(0, max(1, H - bhi)))
            x1, y1 = x0 + bwi, y0 + bhi
            sel = (ex >= x0) & (ex < x1) & (ey >= y0) & (ey < y1)
            n = int(sel.sum())
            if n >= MIN_EV:
                rtb.append(float(et[sel].mean() - (a + b) / 2.0)); rnn.append(n); break
    tb = np.array(tb); nn = np.array(nn, dtype=np.float64)
    var_obs = float(tb.var(ddof=1))
    var_null = float(np.mean(w * w / (12.0 * nn)))
    rows.append(dict(t=int(ti), w_us=int(w), n_obj=len(tb),
                     mean_tbar_us=float(tb.mean()),
                     sd_tbar_us=float(np.sqrt(var_obs)),
                     sd_null_us=float(np.sqrt(var_null)),
                     excess_var=var_obs - var_null,
                     ptp_us=float(tb.max() - tb.min()),
                     n_rand=len(rtb),
                     sd_rand_us=(float(np.std(rtb, ddof=1)) if len(rtb) >= MIN_OBJ else None),
                     sd_rand_null_us=(float(np.sqrt(np.mean(w * w / (12.0 * np.array(rnn, dtype=float)))))
                                      if len(rtb) >= MIN_OBJ else None),
                     n_ev=[int(v) for v in nn], tbar=[float(v) for v in tb],
                     track=bid, cx=[p[0] for p in pos], cy=[p[1] for p in pos]))

def q(k, p): return float(np.percentile([r[k] for r in rows], p))
if rows:
    ev_ = np.array([r['excess_var'] for r in rows])
    pos = float((ev_ > 0).mean())
    med_excess_sd = float(np.sqrt(max(np.median(ev_), 0.0)))
    pooled_excess_sd = float(np.sqrt(max(np.mean(ev_), 0.0)))
    out = dict(seq=seq, frames_with_labels=int(len(ult)), frames_matched=matched,
               frames_used=len(rows),
               exposure_us_med=q('w_us', 50),
               objects_per_frame_med=q('n_obj', 50),
               mean_tbar_us_med=q('mean_tbar_us', 50),
               sd_tbar_us_med=q('sd_tbar_us', 50), sd_tbar_us_p90=q('sd_tbar_us', 90),
               sd_null_us_med=q('sd_null_us', 50), sd_null_us_p90=q('sd_null_us', 90),
               ptp_us_med=q('ptp_us', 50), ptp_us_p90=q('ptp_us', 90),
               frac_frames_excess_positive=pos,
               sd_rand_us_med=float(np.median([r['sd_rand_us'] for r in rows if r['sd_rand_us'] is not None])),
               sd_rand_null_us_med=float(np.median([r['sd_rand_null_us'] for r in rows if r['sd_rand_null_us'] is not None])),
               n_frames_with_rand=int(sum(1 for r in rows if r['sd_rand_us'] is not None)),
               excess_sd_us_from_median_var=med_excess_sd,
               excess_sd_us_from_mean_var=pooled_excess_sd,
               # E11/E12's convention, and the one the paper reports: the median
               # over frames of each frame's own excess.
               excess_sd_us_median_per_frame=float(np.median(
                   np.sqrt(np.maximum(ev_, 0.0)))))
    print(json.dumps(out, indent=1))
    json.dump(dict(summary=out, rows=rows),
              open(f'/work/experiments/e09_per_object_evidence_time/{seq}.json', 'w'))
else:
    print(json.dumps(dict(seq=seq, frames_used=0, frames_matched=matched)))
