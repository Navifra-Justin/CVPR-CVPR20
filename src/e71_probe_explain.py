"""E71: explain the oldest-window-probe cells whose output did not change (verify-*.log reports e.g. 2251/2259).
A zeroed oldest window cannot change the output if (a) that window is already all zero (no events), or (b) the frame has no
detection with and without the probe (the post-NMS output is None in both runs).  For every unchanged probe cell of every
checkpoint this script reads the oldest window from the Gen1 HDF5 representation and the stored detections of that frame and
prints which of (a)/(b) holds; any cell that is neither is listed as UNEXPLAINED.
Run in docker (needs h5py, hdf5plugin):  python3 src/e71_probe_explain.py  > experiments/e71_h4080/probe_explained.log
"""
import numpy as np, glob, os, h5py, hdf5plugin
ROOT = '/work' if os.path.isdir('/work/data') else os.getcwd()
seqs = sorted(glob.glob(f'{ROOT}/data/gen1x/gen1/val/*'))
tot = {}
for m in ['rvt-t', 'rvt-s', 'rvt-b', 's5vit-small', 's5vit-base']:
    n = nch = ne = nz = nu = 0
    for pf in sorted(glob.glob(f'{ROOT}/experiments/e71_h4080/dets-{m}.parts/seq*.npz')):
        Z = np.load(pf); P = Z['probe']
        n += len(P); nch += int(P[:, 2].sum())
        bad = P[P[:, 2] == 0]
        if not len(bad): continue
        si = int(os.path.basename(pf)[3:7]); ri = Z['ri']
        rd = os.path.join(seqs[si], 'event_representations_v2', 'stacked_histogram_dt=50_nbins=10', 'event_representations.h5')
        with h5py.File(rd, 'r') as f:
            D = f[list(f.keys())[0]]
            for j, h, _ in bad:
                x = D[int(ri[j]) - int(h) + 1]; nd = int((Z[f'det_h{int(h)}'][:, 0] == j).sum())
                empty = not np.any(x != 0)
                if empty: ne += 1
                elif nd == 0: nz += 1
                else: nu += 1; print('UNEXPLAINED', m, si, int(j), int(h), 'ndet', nd)
    print(f'{m}: probed {n}, output changed {nch}, unchanged {n-nch} = oldest window all-zero {ne} + frame without detections {nz} + unexplained {nu}')
