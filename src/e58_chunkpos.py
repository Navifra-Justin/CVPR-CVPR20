"""E58 - one released number, twenty-one different temporal supports.

SSM-ViT's released streaming evaluation steps the validation split in non-overlapping chunks
of 21 windows, and E47c measured that the state it carries *between* chunks reaches the output
not at all: zeroing it changes the emitted detection tensor by 0.00000 at every position, while
occluding a window one position earlier *inside* the chunk changes it by 0.0276 to 0.0106. The
history available to a released detection is therefore its position in the chunk: one window
(50 ms) at position 0, twenty-one (1050 ms) at position 20.

The benchmark number the release reports averages over all twenty-one. Nothing in the metric,
the protocol or the published table names the variable being averaged over.

The position is deterministic given the release's own indexing -- chunk starts are placed by
`sequence_for_streaming.py` at `max(first_labelled_repr - 20, 0)` and advance by 21 -- so it is
reconstructed here from the index files alone, with no model run. RVT is scored on exactly the
same frame subsets as a control: RVT is driven one window per call and carries its state across
the whole sequence, so chunk position is a meaningless label for it and its curve must be flat.
"""
import numpy as np, glob, os, json, sys
from multiprocessing import Pool
from e56_eval import Scorer, load_dump, model_paths

CHUNK = 21
ROOT = 'data/gen1x/gen1/val'
OUT = 'experiments/e58_chunkpos/positions.npy'
GROUPS = [('pos 0-3', 0, 4), ('pos 4-9', 4, 10), ('pos 10-15', 10, 16), ('pos 16-20', 16, 21)]
DELTAS_MS = [-50.0, -40.0, -30.0, -23.81, -20.0, -15.0, -10.0, -5.0, 0.0, 5.0, 10.0, 20.0, 30.0]


def build_positions():
    pos = []; fid = 0
    for sd in sorted(glob.glob(os.path.join(ROOT, '*'))):
        rd = os.path.join(sd, 'event_representations_v2', 'stacked_histogram_dt=50_nbins=10')
        try:
            L = np.load(os.path.join(sd, 'labels_v2', 'labels.npz'))['labels']
            o2r = np.load(os.path.join(rd, 'objframe_idx_2_repr_idx.npy'))
        except Exception:
            continue
        if len(o2r) < 3:
            continue
        nts = len(np.unique(L['t']))
        want = sorted(set(int(v) for v in o2r[:min(len(o2r), nts)]))
        start = max(int(o2r[0]) - CHUNK + 1, 0)
        for ri in want:
            pos.append((ri - start) % CHUNK)
            fid += 1
    return np.array(pos, dtype=np.int16)


_S = {}
_P = None


def _init(paths, p):
    global _P
    _P = p
    for nm, q in paths:
        det, gt = load_dump(q)
        _S[nm] = Scorer(det, gt)


def _job(a):
    nm, gname, lo, hi, d = a
    frames = np.flatnonzero((_P >= lo) & (_P < hi))
    return (nm, gname, d, _S[nm].evaluate(d * 1e-3, None, None, frames=frames), len(frames))


if __name__ == '__main__':
    os.makedirs('experiments/e58_chunkpos', exist_ok=True)
    P = build_positions()
    gt = np.load('experiments/e51_ranking/dets-rvt-t.npz')['gt']
    NF = int(gt[:, 0].max()) + 1
    print(f"reconstructed {len(P)} frame positions; dump has {NF} frames")
    if len(P) != NF:
        raise SystemExit("MISMATCH: the position array does not index the dumped frames")
    np.save(OUT, P)
    cnt = np.bincount(P, minlength=CHUNK)
    print("frames per chunk position:", " ".join(str(c) for c in cnt))

    paths = model_paths()
    jobs = [(nm, g, lo, hi, d) for nm, _ in paths for g, lo, hi in GROUPS for d in DELTAS_MS]
    print(f"\n{len(jobs)} evaluations on 64 workers", flush=True)
    acc = {}
    with Pool(processes=64, initializer=_init, initargs=(paths, P)) as pool:
        for i, (nm, g, d, v, n) in enumerate(pool.imap_unordered(_job, jobs, chunksize=1)):
            acc.setdefault(nm, {}).setdefault(g, {})[f"{d:.2f}"] = v
            acc[nm][g]['n_frames'] = n
            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{len(jobs)}", flush=True)

    print(f"\nmAP at the label instant, by chunk position group")
    print(f"{'model':<14}" + "".join(f"{g:>12}" for g, _, _ in GROUPS) + f"{'span pt':>10}")
    res = {'groups': [g for g, _, _ in GROUPS], 'deltas_ms': DELTAS_MS, 'per_model': {}}
    for nm, _ in paths:
        v = [acc[nm][g]['0.00'] * 100 for g, _, _ in GROUPS]
        print(f"{nm:<14}" + "".join(f"{x:12.4f}" for x in v) + f"{max(v)-min(v):10.4f}")
        res['per_model'][nm] = {g: dict(map={k: acc[nm][g][k] for k in acc[nm][g] if k != 'n_frames'},
                                        n_frames=acc[nm][g]['n_frames'])
                                for g, _, _ in GROUPS}

    print(f"\nmetric-preferred instant (argmax of mAP over delta), by chunk position group")
    print(f"{'model':<14}" + "".join(f"{g:>12}" for g, _, _ in GROUPS))
    for nm, _ in paths:
        row = []
        for g, _, _ in GROUPS:
            c = np.array([acc[nm][g][f"{d:.2f}"] for d in DELTAS_MS])
            row.append(DELTAS_MS[int(np.argmax(c))])
        print(f"{nm:<14}" + "".join(f"{x:12.2f}" for x in row))
        res['per_model'][nm]['argmax_ms'] = row

    json.dump(res, open('experiments/e58_chunkpos/result.json', 'w'), indent=1)
    print("\nWROTE experiments/e58_chunkpos/result.json")
