"""E08 - the label noise floor sigma_c, and whether label errors are white.

Two things the review says are unestablished:
  Major 3: sigma_tau_excess = Var(delta_hat) - E[sigma^2] is fragile to sigma_c.
           Measure sigma_c from the labels themselves instead of assuming it.
  Major 2: the IV instrument assumes disjoint label pairs have uncorrelated errors.
           If labels are tracker output, residuals along a track are autocorrelated.
           Test it directly.

Estimator, assumption-light: for x_i = f(t_i) + e_i on a uniform grid with f smooth,
  Var(2nd difference) = 6 s^2 + (f'' dt^2)^2
  Var(3rd difference) = 20 s^2 + (f''' dt^3)^2
Under locally constant acceleration f'''=0, so the 3rd difference is pure noise and
  s^2 = Var(D3)/20.
If the noise is white, the 2nd-difference estimate s2 = sqrt(Var(D2)/6) is an upper
bound that approaches s from above. If the noise is temporally correlated (a tracker
smooths its own errors), the two estimates disagree in a specific direction, and the
lag-1 autocorrelation of D3 departs from the white-noise value.
For white noise, D3 has autocorrelation rho1 = -15/20 = -0.75, rho2 = 6/20 = 0.30,
rho3 = -1/20 = -0.05 (from the coefficient vector (1,-3,3,-1)).
"""
import numpy as np, glob, json, os

files = sorted(glob.glob('/work/data/dsec_det/*/*/*/object_detections/left/tracks.npy'))
D2x, D3x, D2y, D3y = [], [], [], []
speeds, accels = [], []
ntrk = 0
for f in files:
    a = np.load(f)
    for tid in np.unique(a['track_id']):
        s = np.sort(a[a['track_id'] == tid], order='t')
        if len(s) < 6:
            continue
        t = s['t'].astype(np.float64) * 1e-6
        cx = (s['x'] + s['w'] / 2.0).astype(np.float64)
        cy = (s['y'] + s['h'] / 2.0).astype(np.float64)
        dt = np.diff(t)
        # keep only runs on the regular 20 Hz grid
        ok = np.abs(dt - np.median(dt)) < 2e-3
        if ok.sum() < 5:
            continue
        # longest contiguous regular run
        idx = np.flatnonzero(~ok)
        bounds = np.concatenate(([-1], idx, [len(dt)]))
        seg = np.argmax(np.diff(bounds))
        i0, i1 = bounds[seg] + 1, bounds[seg + 1] + 1
        if i1 - i0 < 6:
            continue
        X, Y, T = cx[i0:i1 + 1], cy[i0:i1 + 1], t[i0:i1 + 1]
        h = float(np.median(np.diff(T)))
        ntrk += 1
        D2x.append(X[2:] - 2 * X[1:-1] + X[:-2])
        D2y.append(Y[2:] - 2 * Y[1:-1] + Y[:-2])
        if len(X) >= 4:
            D3x.append(X[3:] - 3 * X[2:-1] + 3 * X[1:-2] - X[:-3])
            D3y.append(Y[3:] - 3 * Y[2:-1] + 3 * Y[1:-2] - Y[:-3])
        v = np.hypot(np.diff(X), np.diff(Y)) / h
        speeds.append(v)
        if len(v) >= 2:
            accels.append(np.abs(np.diff(v)) / h)

cat = lambda L: np.concatenate(L) if L else np.array([])
D2 = np.concatenate([cat(D2x), cat(D2y)])
D3 = np.concatenate([cat(D3x), cat(D3y)])
V, A = cat(speeds), cat(accels)

def rob_var(z):          # robust, insensitive to a few gross outliers
    return (np.median(np.abs(z - np.median(z))) * 1.4826) ** 2

s_from_D2 = np.sqrt(rob_var(D2) / 6.0)
s_from_D3 = np.sqrt(rob_var(D3) / 20.0)

# lag autocorrelation of the 3rd difference, per track, then pooled
def acf(seq_list, L):
    num = den = 0.0
    for z in seq_list:
        if len(z) <= L: continue
        z = z - np.mean(z)
        num += float(np.dot(z[:-L], z[L:])); den += float(np.dot(z, z))
    return num / den if den else float('nan')

acf1 = acf(D3x + D3y, 1); acf2 = acf(D3x + D3y, 2); acf3 = acf(D3x + D3y, 3)

out = dict(
    tracks_used=ntrk, n_D2=int(D2.size), n_D3=int(D3.size),
    sigma_c_from_2nd_diff_px=round(float(s_from_D2), 4),
    sigma_c_from_3rd_diff_px=round(float(s_from_D3), 4),
    ratio_2nd_over_3rd=round(float(s_from_D2 / s_from_D3), 4),
    D3_acf_lag1=round(acf1, 4), D3_acf_lag2=round(acf2, 4), D3_acf_lag3=round(acf3, 4),
    D3_acf_white_noise_expected=dict(lag1=-0.75, lag2=0.30, lag3=-0.05),
    speed_px_per_s=dict(p10=round(float(np.percentile(V,10)),2),
                        median=round(float(np.median(V)),2),
                        p90=round(float(np.percentile(V,90)),2),
                        p99=round(float(np.percentile(V,99)),2)),
    accel_px_per_s2=dict(median=round(float(np.median(A)),2),
                         p90=round(float(np.percentile(A,90)),2),
                         p99=round(float(np.percentile(A,99)),2)),
)
print(json.dumps(out, indent=1))
os.makedirs('/work/experiments/e08_label_noise', exist_ok=True)
json.dump(out, open('/work/experiments/e08_label_noise/result.json','w'), indent=1)
