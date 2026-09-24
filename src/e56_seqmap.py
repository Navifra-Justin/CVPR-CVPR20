"""Frame index -> validation sequence, reconstructed exactly as E51's dump assigned it.

E51 wrote a single global frame counter over the sorted validation directories and emitted
no sequence column. The cluster bootstrap of E56b resamples sequences, so the mapping has to
be recovered. The dump's own admission rule is replayed here from the label and index files
alone -- no event data is read -- and the reconstruction is accepted only if the frame total
matches the dumps.
"""
import numpy as np, glob, os, json

NSEQ = int(os.environ.get('NSEQ', '10000'))
ROOT = os.environ.get('GEN1', 'data/gen1x/gen1/val')
OUT = 'experiments/e56_resolving/seqmap.json'


def build():
    bounds = []; fid = 0
    for sd in sorted(glob.glob(os.path.join(ROOT, '*')))[:NSEQ]:
        rd = os.path.join(sd, 'event_representations_v2', 'stacked_histogram_dt=50_nbins=10')
        try:
            L = np.load(os.path.join(sd, 'labels_v2', 'labels.npz'))['labels']
            o2r = np.load(os.path.join(rd, 'objframe_idx_2_repr_idx.npy'))
        except Exception:
            continue
        if len(o2r) < 3:
            continue
        nts = len(np.unique(L['t']))
        n = len(set(int(v) for v in o2r[:min(len(o2r), nts)]))
        bounds.append(dict(seq=os.path.basename(sd), start=fid, n=n))
        fid += n
    return bounds, fid


if __name__ == '__main__':
    bounds, total = build()
    gt = np.load('experiments/e51_ranking/dets-rvt-t.npz')['gt']
    want = int(gt[:, 0].max()) + 1
    print(f"{len(bounds)} sequences, {total} frames reconstructed; dump has {want}")
    if total != want:
        raise SystemExit(f"MISMATCH: {total} != {want}; the bootstrap would resample the wrong units")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(bounds, open(OUT, 'w'), indent=1)
    print(f"WROTE {OUT}")
