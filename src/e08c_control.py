"""Control: push KNOWN noise through the exact pooling estimator used in E08.
H1 labels are genuinely correlated | H2 pooling across heterogeneous-variance
segments biases the ACF toward zero | H3 heavy tails inflate the denominator."""
import numpy as np, glob, json
rng = np.random.default_rng(0)

def acf(seqs, L):
    num = den = 0.0
    for z in seqs:
        if len(z) <= L: continue
        z = z - np.mean(z)
        num += float(np.dot(z[:-L], z[L:])); den += float(np.dot(z, z))
    return num / den if den else float('nan')

def D3(x): return x[3:] - 3*x[2:-1] + 3*x[1:-2] - x[:-3]

# real segment-length distribution, so the control matches the data's shape
lens = []
for f in sorted(glob.glob('/work/data/dsec_det/*/*/*/object_detections/left/tracks.npy')):
    a = np.load(f)
    for tid in np.unique(a['track_id']):
        n = int((a['track_id'] == tid).sum())
        if n >= 6: lens.append(n)
lens = np.array(lens); print("segments", len(lens), "median len", int(np.median(lens)))

def run(kind):
    seqs = []
    for n in lens:
        if kind == 'white':      e = rng.normal(0, 1, n)
        elif kind == 'hetero':   e = rng.normal(0, rng.uniform(0.2, 3.0), n)
        elif kind == 'heavy':    e = rng.standard_t(2.5, n)
        elif kind == 'ar1':
            e = np.zeros(n); 
            for i in range(1, n): e[i] = 0.6*e[i-1] + rng.normal(0, 1)
        seqs.append(D3(e))
    return [round(acf(seqs, L), 4) for L in (1, 2, 3)]

print("white-noise theory     : [-0.75, 0.30, -0.05]")
for k in ('white', 'hetero', 'heavy', 'ar1'):
    print(f"control {k:<7}        : {run(k)}")
m = json.load(open('/work/experiments/e08_label_noise/result.json'))
print("MEASURED on real labels:", [m['D3_acf_lag1'], m['D3_acf_lag2'], m['D3_acf_lag3']])
