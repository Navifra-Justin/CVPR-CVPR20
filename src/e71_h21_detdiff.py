"""E71: detection-wise comparison of the H=21 column recomputed by src/e71_dump.py with the H=21 column of the E66 dump,
on the 3,000 frames.  Writes experiments/e71_h4080/h21_detdiff.json (one record per checkpoint) and prints a summary.
A detection of one run is paired with the unused detection of the other run of the same class with the largest IoU (>= 0.5),
walking in descending confidence.  'unpaired' counts detections with confidence above the 0.01 floor + 2e-4 without a partner."""
import numpy as np, json
OUT = {}
for m in ['rvt-t', 'rvt-s', 'rvt-b', 's5vit-small', 's5vit-base']:
    Z = np.load(f'experiments/e71_h4080/dets-{m}.npz'); E = np.load(f'experiments/e66_fixedH/dets-{m}.npz')
    seqZ = Z['seq']; locZ = np.zeros(len(seqZ), int)
    for s in np.unique(seqZ):
        k = np.flatnonzero(seqZ == s); locZ[k] = np.arange(len(k))
    key66 = {}
    for s in np.unique(E['seq']):
        for jj, g in enumerate(np.flatnonzero(E['seq'] == s)): key66[(int(s), jj)] = int(g)
    d21 = Z['det_h21'].astype(float); e21 = E['det_h21'].astype(float)
    ds = []; un = []; n = 0
    for f in np.flatnonzero(Z['done']):
        g = key66[(int(seqZ[f]), int(locZ[f]))]
        a = e21[e21[:, 0] == g][:, 1:]; b = d21[d21[:, 0] == f][:, 1:]; n += len(b)
        used = np.zeros(len(b), bool)
        for r in a[np.argsort(-a[:, 4])]:
            c = (b[:, 5] == r[5]) & ~used
            if not c.any():
                if r[4] > 0.0102: un.append(float(r[4]))
                continue
            x1 = np.maximum(r[0], b[:, 0]); y1 = np.maximum(r[1], b[:, 1]); x2 = np.minimum(r[2], b[:, 2]); y2 = np.minimum(r[3], b[:, 3])
            it = np.clip(x2 - x1, 0, None) * np.clip(y2 - y1, 0, None)
            io = it / np.maximum((r[2] - r[0]) * (r[3] - r[1]) + (b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1]) - it, 1e-9)
            io = np.where(c, io, -1); j = int(np.argmax(io))
            if io[j] < 0.5:
                if r[4] > 0.0102: un.append(float(r[4]))
                continue
            used[j] = True; ds.append(abs(r[4] - b[j, 4]))
        un += [float(x) for x in b[~used][:, 4] if x > 0.0102]
    ds = np.array(ds)
    OUT[m] = dict(n_dets_e71=int(n), n_paired=int(len(ds)), median_abs_score_diff=float(np.median(ds)), p999_abs_score_diff=float(np.percentile(ds, 99.9)),
                  max_abs_score_diff=float(ds.max()), n_unpaired=len(un), max_unpaired_score=float(max(un)) if un else 0.0)
    print(m, OUT[m])
json.dump(OUT, open('experiments/e71_h4080/h21_detdiff.json', 'w'), indent=1)
