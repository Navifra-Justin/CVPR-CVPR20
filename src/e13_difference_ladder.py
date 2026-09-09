"""E13 - solve for the label noise instead of bounding it (elimination, not a bound).

E08 reported sigma_c <= 0.497 px because the 3rd difference still contains real
jerk. That is one equation in two unknowns. Taking differences of successive
order gives a system with DIFFERENT coefficients on the same two unknowns:

    Var(D_k) = c_k * s^2  +  (motion term of order k)
    c_k = binom(2k, k):   c_1=2, c_2=6, c_3=20, c_4=70, c_5=252, c_6=924

For motion that is smooth on the 50 ms grid the motion term falls fast with k,
while c_k grows. So Var(D_k)/c_k decreases toward s^2 from above and converges.
Report where the ladder converges, and the successive differences that show it,
instead of stopping at k=3 and calling it a bound.

Cross-check with an independent construction: interleaved subsampling. Splitting
one track into even and odd indices halves the sampling rate, which multiplies the
motion term by 2^(2k) while leaving s^2 alone. Comparing the two ladders gives a
second, independent estimate of the same s^2.
"""
import numpy as np, glob, json
from math import comb

def diffs(x, k):
    for _ in range(k): x = np.diff(x)
    return x

def rvar(z):
    return (np.median(np.abs(z - np.median(z))) * 1.4826) ** 2

segs = []
for f in sorted(glob.glob('/work/data/dsec_det/*/*/*/object_detections/left/tracks.npy')):
    a = np.load(f)
    for tid in np.unique(a['track_id']):
        s = np.sort(a[a['track_id'] == tid], order='t')
        if len(s) < 10: continue
        t = s['t'].astype(np.float64) * 1e-6
        dt = np.diff(t); h = np.median(dt)
        ok = np.abs(dt - h) < 2e-3
        idx = np.flatnonzero(~ok); b = np.concatenate(([-1], idx, [len(dt)]))
        seg = np.argmax(np.diff(b)); i0, i1 = b[seg]+1, b[seg+1]+1
        if i1 - i0 < 10: continue
        segs.append((( s['x'] + s['w']/2.0)[i0:i1+1].astype(np.float64),
                     ( s['y'] + s['h']/2.0)[i0:i1+1].astype(np.float64)))
print("segments", len(segs), flush=True)

def ladder(getter, label):
    print(f"\n{label}")
    print("  k  c_k=C(2k,k)      n      Var(D_k)/c_k -> sigma (px)   change vs k-1")
    prev = None; vals = {}
    for k in range(1, 7):
        pool = []
        for X, Y in segs:
            for z in (getter(X), getter(Y)):
                if len(z) > k + 1: pool.append(diffs(z, k))
        if not pool: break
        z = np.concatenate(pool)
        s2 = rvar(z) / comb(2*k, k)
        s = float(np.sqrt(s2)); vals[k] = s
        ch = "" if prev is None else f"  {100*(s-prev)/prev:+7.2f} %"
        print(f"  {k}  {comb(2*k,k):>10}  {len(z):>8}   {s:.4f}{ch}")
        prev = s
    return vals

full = ladder(lambda a: a, "FULL RATE (20 Hz)")
half = ladder(lambda a: a[::2], "HALVED RATE (10 Hz): motion term x 2^(2k), noise unchanged")

print("\nCONVERGENCE")
for k in sorted(set(full) & set(half)):
    print(f"  k={k}  full {full[k]:.4f}   half {half[k]:.4f}   ratio {half[k]/full[k]:.3f}")
json.dump(dict(full=full, half=half), open('/work/experiments/e13_difference_ladder/result.json','w'), indent=1)
print("WROTE", flush=True)
