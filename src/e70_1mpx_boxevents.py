"""E70 gate helper (needs h5py/hdf5plugin, run in docker, CPU only): for every labelled frame of the gate subset, the number of
event-histogram counts (all 20 channels) inside the union of that frame's ground-truth boxes, in the 360x640 representation.
Writes experiments/e70_1mpx/gate/boxevents.npy (one int64 per frame, same frame order as the dets-*.npz files).
Why it exists: the gate's 'frames with detections' check was inherited from Gen1 (99.9 % of frames), but on 1 Mpx the labels persist
for stationary objects that produce no events, and no detector can fire on an empty window."""
import sys, numpy as np, h5py, hdf5plugin
G = '/work/experiments/e70_1mpx/gate/'
z = np.load(G + 'dets-s5vit-base-shift0.npz'); g = z['gt']; seq = z['seq']
seqs = [l.strip() for l in open(G + 'seqlist.txt') if l.strip()]
out = np.zeros(len(seq), np.int64); base = 0
for si, s in enumerate(seqs):
    rd = f'/work/data/gen4x/gen4/val/{s}/event_representations_v2/stacked_histogram_dt=50_nbins=10'
    o2r = np.load(rd + '/objframe_idx_2_repr_idx.npy'); n = int((seq == si).sum())
    with h5py.File(rd + '/event_representations_ds2_nearest.h5', 'r') as f:
        D = f['data']
        for k in range(n):
            fid = base + k; gg = g[g[:, 0] == fid]
            X = D[int(o2r[k])].astype(np.int64).sum(0); M = np.zeros(X.shape, bool)
            for b in gg:
                x1, y1, x2, y2 = [int(round(v)) for v in b[1:5]]
                M[max(y1, 0):max(y2, 0), max(x1, 0):max(x2, 0)] = True
            out[fid] = X[M].sum()
    base += n
np.save(G + 'boxevents.npy', out); print('WROTE', G + 'boxevents.npy', len(out), 'zero-event frames', int((out == 0).sum()))
