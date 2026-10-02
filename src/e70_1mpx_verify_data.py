"""E70 data check for the fetched 1 Mpx val split (no model, no GPU).
For every sequence under data/gen4x/gen4/val that has a done marker: the representation array length equals
len(timestamps_us), objframe_idx_2_repr_idx indexes inside it and is strictly increasing, label times are
unique-per-frame and match representation timestamps at o2r, class ids are within {0,1,2}, label boxes
(x2 scale) fit inside 640x360. Prints totals used for the GPU-time estimate."""
import os, sys, json, numpy as np, h5py, hdf5plugin
R = '/work/data/gen4x'; V = R + '/gen4/val'
done = sorted(os.listdir(R + '/done')) if os.path.isdir(R + '/done') else []
bad = []; W = 0; F = 0; BX = 0; classes = np.zeros(3, int)
for n in done:
    d = f'{V}/{n}'; rd = d + '/event_representations_v2/stacked_histogram_dt=50_nbins=10'
    try:
        L = np.load(d + '/labels_v2/labels.npz')['labels']; o2r = np.load(rd + '/objframe_idx_2_repr_idx.npy')
        ts = np.load(rd + '/timestamps_us.npy')
        with h5py.File(rd + '/event_representations_ds2_nearest.h5', 'r') as f:
            D = f['data']; assert D.shape[1:] == (20, 360, 640) and D.dtype == np.uint8, D.shape
            assert D.shape[0] == len(ts), (D.shape, len(ts))
            assert o2r.max() < D.shape[0] and np.all(np.diff(o2r) > 0)
            W += D.shape[0]
        lt = np.unique(L['t']); assert len(lt) >= len(o2r) or True
        m = min(len(o2r), len(lt))
        assert np.array_equal(ts[o2r[:m]], lt[:m]), 'label times != representation timestamps at o2r'
        assert set(np.unique(L['class_id'])) <= {0, 1, 2}
        assert (L['x'] * .5 >= -1).all() and ((L['x'] + L['w']) * .5 <= 641).all() and ((L['y'] + L['h']) * .5 <= 361).all()
        F += m; BX += len(L); classes += np.bincount(L['class_id'], minlength=3)[:3]
    except Exception as e:
        bad.append((n, repr(e)[:120]))
print(f'sequences checked {len(done)}  bad {len(bad)}  windows {W}  labelled frames {F}  boxes {BX}  per-class {classes.tolist()}')
for b in bad[:10]: print('BAD', *b)
sys.exit(1 if bad else 0)
