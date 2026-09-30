"""Reassemble a sharded dump of src/e51_dump_all.py into the single-process dump.

Sharding partitions the validation sequence list; the recurrent state is started from None
at every sequence in that loop and never crosses a sequence boundary, so each shard computes
exactly the frames it owns and nothing else changes. This script restores the two things
sharding does move: the order of the frames, which is sequence index ascending, and the frame
ids, which are a running counter over that order. Both are restored from the `seq` array each
shard records, so the merged arrays are element-for-element what one process would have
written. src/e65_shard_selftest.sh checks that claim against a real single-process dump.

  python3 src/e65_merge_shards.py OUT.npz SHARD0.npz SHARD1.npz ...
"""
import sys
import numpy as np

out, parts = sys.argv[1], sys.argv[2:]
assert len(parts) >= 2, 'nothing to merge'

Z = [np.load(p) for p in parts]
for p, z in zip(parts, Z):
    assert 'seq' in z, f'{p} predates sharding and carries no sequence index'

# One row per frame: which shard holds it, its index inside that shard, and its sequence.
seqs = np.concatenate([z['seq'] for z in Z])
which = np.concatenate([np.full(len(z['seq']), k, np.int32) for k, z in enumerate(Z)])
local = np.concatenate([np.arange(len(z['seq']), dtype=np.int64) for z in Z])

# A sequence must belong to exactly one shard, or the partition was not a partition and the
# merge would double-count frames. Checked rather than trusted.
owner = {}
for s, k in zip(seqs, which):
    owner.setdefault(int(s), int(k))
    assert owner[int(s)] == int(k), f'sequence {s} appears in more than one shard'

# Stable sort by sequence index puts the frames back in single-process order: every sequence
# is contiguous inside its own shard and already in order there, so stability is enough.
order = np.argsort(seqs, kind='stable')
which, local, seqs = which[order], local[order], seqs[order]

# new frame id -> (shard, old frame id), inverted into the lookup the row arrays need.
lut = [{} for _ in Z]
for new_fid, (k, l) in enumerate(zip(which, local)):
    lut[int(k)][int(l)] = new_fid

def remap(key):
    rows = []
    for k, z in enumerate(Z):
        a = z[key]
        if len(a) == 0:
            continue
        a = a.copy()
        a[:, 0] = np.array([lut[k][int(f)] for f in a[:, 0]], dtype=a.dtype)
        rows.append(a)
    a = np.concatenate(rows) if rows else np.zeros((0, Z[0][key].shape[1]), Z[0][key].dtype)
    return a[np.argsort(a[:, 0], kind='stable')]

det, gt = remap('det'), remap('gt')
pos = np.concatenate([Z[int(k)]['pos'][int(l)][None] for k, l in zip(which, local)])
np.savez_compressed(out, det=det, gt=gt, pos=pos.astype(np.int16),
                    seq=seqs.astype(np.int32))
print(f'MERGED {out}  frames {len(pos)}  dets {len(det)}  gt {len(gt)}  from {len(Z)} shards')
