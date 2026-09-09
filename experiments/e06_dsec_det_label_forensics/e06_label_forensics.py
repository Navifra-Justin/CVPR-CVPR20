import numpy as np, glob, collections, os
files = sorted(glob.glob('/work/data/dsec_det/*/*/*/object_detections/left/tracks.npy'))
print("FILES", len(files))

all_dt = []; tot = 0; ntracks = 0
per_seq = []
for f in files:
    a = np.load(f)
    tot += len(a)
    ts = np.unique(a['t'])
    d = np.diff(np.sort(ts))
    all_dt.append(d)
    ntracks += len(np.unique(a['track_id']))
    seq = f.split('/')[-4]
    per_seq.append((seq, len(a), len(ts), int(np.median(d)) if len(d) else 0))
d = np.concatenate(all_dt)
print("TOTAL_BOXES", tot, "TOTAL_TRACKS", ntracks, "UNIQUE_LABEL_TIMES", len(d)+len(files))
print("LABEL_TIME_SPACING_us: min %d p1 %d median %d p99 %d max %d" %
      (d.min(), np.percentile(d,1), np.median(d), np.percentile(d,99), d.max()))
vals, cnts = np.unique(d, return_counts=True)
order = np.argsort(-cnts)[:8]
print("MOST_COMMON_SPACINGS:", [(int(vals[i]), int(cnts[i])) for i in order])
print("FRAC_SPACING_UNDER_40ms: %.4f" % float((d < 40000).mean()))

# second-difference test on evenly spaced triples within a track
res = collections.defaultdict(list)
for f in files:
    a = np.load(f)
    for tid in np.unique(a['track_id']):
        s = np.sort(a[a['track_id'] == tid], order='t')
        if len(s) < 3: continue
        t = s['t'].astype(np.float64)
        cx = s['x'] + s['w']/2.0
        cy = s['y'] + s['h']/2.0
        for i in range(1, len(s)-1):
            dt1 = t[i]-t[i-1]; dt2 = t[i+1]-t[i]
            if abs(dt1-dt2) > 2000 or dt1 > 120000: continue
            # linear interpolant of neighbours evaluated at t[i]
            wgt = dt1/(dt1+dt2)
            px = s['x'][i-1]+s['w'][i-1]/2 + wgt*((s['x'][i+1]+s['w'][i+1]/2)-(s['x'][i-1]+s['w'][i-1]/2))
            py = s['y'][i-1]+s['h'][i-1]/2 + wgt*((s['y'][i+1]+s['h'][i+1]/2)-(s['y'][i-1]+s['h'][i-1]/2))
            r = float(np.hypot(cx[i]-px, cy[i]-py))
            res[int(round(dt1/1000.0))].append(r)
print("SECOND_DIFF_RESIDUAL (px) by spacing_ms: spacing n median p90 frac_below_0.01px")
for k in sorted(res):
    v = np.array(res[k])
    if len(v) < 30: continue
    print("SD %3d %6d %.4f %.4f %.4f" % (k, len(v), np.median(v), np.percentile(v,90), float((v < 0.01).mean())))
