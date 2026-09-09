"""E09b -- is the per-object evidence-time offset a property of the object?

Reads the per-frame rows written by measure.py and answers three questions, in
order, on the residual that remains after each frame's own mean is removed.
The frame mean is the component a declared per-output scalar timestamp would
cancel, so removing it first is what makes the remainder about the object.

  1. persistence  -- does a track's residual repeat across frames?
  2. position     -- is the persistence just a region of the image having a
                     persistent offset, which a track inherits by sitting in it?
  3. transport    -- does a track carry its offset with it as it crosses the
                     image?  A positional effect would decorrelate with
                     displacement; an object-bound one would not.

    python3 experiments/e09_per_object_evidence_time/per_track.py zurich_city_09_a
"""
import json, os, sys
import numpy as np

SEQ = sys.argv[1] if len(sys.argv) > 1 else 'zurich_city_09_a'
HERE = os.path.dirname(os.path.abspath(__file__))
MIN_OBS = 5                       # observations required for a track to enter
W, H = 640, 480

rows = json.load(open(os.path.join(HERE, f'{SEQ}.json')))['rows']

# ---- frame-centred residual, one record per (frame, object) ----------------
rec = []                          # (t, track, residual_us, cx, cy, n_events)
for r in rows:
    tb = np.array(r['tbar'], dtype=float)
    res = tb - tb.mean()
    for k in range(len(tb)):
        rec.append((int(r['t']), int(r['track'][k]), float(res[k]),
                    float(r['cx'][k]), float(r['cy'][k]), float(r['n_ev'][k])))
rec.sort(key=lambda z: (z[1], z[0]))
t = np.array([z[0] for z in rec], dtype=np.int64)
tid = np.array([z[1] for z in rec], dtype=np.int64)
res = np.array([z[2] for z in rec], dtype=float)
cx = np.array([z[3] for z in rec], dtype=float)
cy = np.array([z[4] for z in rec], dtype=float)
nev = np.array([z[5] for z in rec], dtype=float)

uid, counts = np.unique(tid, return_counts=True)
keep_tracks = uid[counts >= MIN_OBS]
sel = np.isin(tid, keep_tracks)


def track_stats(values):
    """Between-track spread of the track means, the spread expected with no
    track effect, their variance ratio, and the pooled lag-one autocorrelation
    along tracks."""
    means, within_var, ns, acf_x, acf_y = [], [], [], [], []
    wacf_x, wacf_y = [], []
    for k in keep_tracks:
        m = (tid == k)
        v = values[m]
        order = np.argsort(t[m])
        v = v[order]
        means.append(v.mean())
        within_var.append(v.var(ddof=1))
        ns.append(len(v))
        acf_x.extend(v[:-1]); acf_y.extend(v[1:])
        vc = v - v.mean()
        wacf_x.extend(vc[:-1]); wacf_y.extend(vc[1:])
    means = np.array(means); within_var = np.array(within_var)
    ns = np.array(ns, dtype=float)
    between_sd = float(means.std(ddof=1))
    # under independent per-observation noise of the observed within-track size,
    # a track mean of n_k observations has variance within_var_k / n_k
    no_effect_sd = float(np.sqrt(np.mean(within_var / ns)))
    ax = np.array(acf_x); ay = np.array(acf_y)
    acf = float(np.corrcoef(ax, ay)[0, 1])
    wacf = float(np.corrcoef(np.array(wacf_x), np.array(wacf_y))[0, 1])
    return dict(tracks=int(len(keep_tracks)), observations=int(sel.sum()),
                between_sd_us=round(between_sd, 1),
                mean_within_sd_us=round(float(np.sqrt(within_var.mean())), 1),
                no_effect_sd_us=round(no_effect_sd, 1),
                var_ratio=round((between_sd / no_effect_sd) ** 2, 2),
                lag1_acf=round(acf, 3),
                lag1_acf_within_track_centred=round(wacf, 3),
                acf_pairs=int(len(ax)))


def cell_removed(values, n):
    """Subtract the mean residual of each cell of an n-by-n grid over the image."""
    ix = np.clip((cx / W * n).astype(int), 0, n - 1)
    iy = np.clip((cy / H * n).astype(int), 0, n - 1)
    cell = iy * n + ix
    out = values.copy()
    for c in np.unique(cell):
        m = cell == c
        out[m] -= out[m].mean()
    return out


out = {'seq': SEQ, 'min_observations': MIN_OBS,
       'raw': track_stats(res)}
for n in (8, 16, 32):
    out[f'minus_{n}x{n}_cell_means'] = track_stats(cell_removed(res, n))

# ---- transport: split tracks at their median image path length -------------
path = {}
for k in keep_tracks:
    m = (tid == k)
    order = np.argsort(t[m])
    px, py = cx[m][order], cy[m][order]
    path[int(k)] = float(np.hypot(np.diff(px), np.diff(py)).sum())
med_path = float(np.median(list(path.values())))


def acf_of(track_subset):
    xs, ys = [], []
    for k in track_subset:
        m = (tid == k)
        order = np.argsort(t[m])
        v = res[m][order]
        xs.extend(v[:-1]); ys.extend(v[1:])
    return round(float(np.corrcoef(np.array(xs), np.array(ys))[0, 1]), 3), len(track_subset)


low = [k for k in keep_tracks if path[int(k)] < med_path]
high = [k for k in keep_tracks if path[int(k)] >= med_path]
a_low, n_low = acf_of(low)
a_high, n_high = acf_of(high)
out['displacement_split'] = dict(median_path_px=round(med_path, 1),
                                 low_tracks=n_low, low_lag1_acf=a_low,
                                 high_tracks=n_high, high_lag1_acf=a_high)

# a track that moves further is not simply a track with more events, which would
# raise its autocorrelation through lower measurement noise alone
per_track_ev = np.array([nev[tid == k].mean() for k in keep_tracks])
per_track_path = np.array([path[int(k)] for k in keep_tracks])
out['displacement_split']['corr_path_events'] = round(
    float(np.corrcoef(per_track_path, per_track_ev)[0, 1]), 3)

json.dump(out, open(os.path.join(HERE, f'per_track_{SEQ}.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
