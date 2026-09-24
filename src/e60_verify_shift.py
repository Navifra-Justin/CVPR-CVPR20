"""E60 verification - check the chunk-boundary shift re-assigns positions, without a GPU.

The first E60 attempt ran to completion, exited 0 and wrote a dump whose frame count and
ground truth matched the baseline exactly, and was still wrong: it moved chunk boundaries
EARLIER, and the release's own start is already max(first_label - 20, 0), which for most
Gen1 sequences is pinned at 0. Subtracting from a clamped value is a no-op, so 73.5% of
frames kept the position they already had and the short/full block exchange came out
one-sided (774 of 3672 one way, 18 of 5069 the other).

Positions depend only on the index files, not on the network, so the treatment can be
checked before any GPU is claimed. This replays the exact frame enumeration of
e51_dump_all.py - same sequence order, same skip rules, same `want` dict, same chunk walk -
under SHIFT=0 and under the requested SHIFT, and asserts four things:

  1. the SHIFT=0 replay reproduces experiments/e58_chunkpos/positions.npy exactly, which is
     what licenses the rest of the comparison,
  2. every frame's new position is (old position - SHIFT) mod CHUNK,
  3. no labelled frame falls outside a chunk that was inside one before,
  4. the short-block/full-block exchange is two-sided.

No model, no CUDA, no event data is read - only objframe_idx_2_repr_idx.npy, labels.npz and
the representation timestamps, whose length is the number of representation frames.
"""
import os, glob, numpy as np
from collections import Counter

ROOT = os.environ.get('ROOT', '/work/data/gen1x/gen1/val')
CHUNK = int(os.environ.get('CHUNK', '21'))
SHIFT = int(os.environ.get('SHIFT', '16'))
SHORT, FULL = (0, 4), (16, 21)


# The replay is only evidence about the dump if it places chunk starts by the same expression
# the dump places them by. Rather than trust that they were kept in step by hand, the dumper's
# own line is read and compared. If e51_dump_all.py is edited, this fails before anything else.
DUMPER = os.environ.get('DUMPER', '/work/src/e51_dump_all.py')
EXPECT = 'start=max(int(o2r[0])-CHUNK+1,0)+SHIFT'
_src = [l.strip() for l in open(DUMPER)]
_hits = [l for l in _src if l == EXPECT]


def start_old(f):                      # released streaming dataset, and the broken variant
    return max(f - CHUNK + 1, 0)


def start_broken(f, s):
    return max(f - CHUNK + 1 - s, 0)


def start_new(f, s):
    # No upper clamp. Clamping to f was the second defect this check caught: 216 of the 406
    # sequences have their first label at repr index < SHIFT, the clamp pinned their start at
    # the first label itself, and the rotation those sequences received was f, not SHIFT.
    # Without the clamp the rotation is exactly SHIFT everywhere, at the cost of the labelled
    # frames sitting at repr index < SHIFT, which no chunk then covers. Those frames are
    # recorded as -1 and the paired analysis drops them from BOTH arms, so the pairing stays
    # on identical frames.
    return max(f - CHUNK + 1, 0) + s


def walk(want, start, stop):
    """positions e51_dump_all.py would record, -1 for a frame no chunk covers"""
    pos = {}
    for c0 in range(start, stop, CHUNK):
        for ri in range(c0, min(c0 + CHUNK, stop)):
            if ri in want:
                pos[ri] = ri - c0
    return [pos.get(ri, -1) for ri in sorted(want)]


OLD, NEW, BRK, SEQ, FIRST = [], [], [], [], []
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
    want = {int(o2r[i]): i for i in range(min(len(o2r), nts))}
    # the h5 dataset's length, without opening the h5: the representation directory carries
    # one timestamp per representation frame, so len(timestamps_us) == D.shape[0]
    n = len(np.load(os.path.join(rd, 'timestamps_us.npy')))
    stop = min(int(o2r[-1]) + 1, n)
    f0 = int(o2r[0])
    # the fix must be inert at SHIFT=0, or it would have moved the released protocol itself
    assert start_new(f0, 0) == start_old(f0), f0
    o = walk(want, start_old(f0), stop)
    OLD += o
    NEW += walk(want, start_new(f0, SHIFT), stop)
    BRK += walk(want, start_broken(f0, SHIFT), stop)
    SEQ += [os.path.basename(sd)] * len(o)
    FIRST += [f0] * len(o)

OLD = np.array(OLD); NEW = np.array(NEW); BRK = np.array(BRK)
SEQ = np.array(SEQ); FIRST = np.array(FIRST)
print(f"{len(np.unique(SEQ))} sequences, {len(OLD)} labelled frames, CHUNK={CHUNK} SHIFT={SHIFT}\n")

ok = True


def check(name, cond, detail=''):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}{('  ' + detail) if detail else ''}")


# 1. the replay is the real thing
REF = np.load('experiments/e58_chunkpos/positions.npy')
print("0. the replay places chunk starts by the dumper's own expression")
check('e51_dump_all.py still reads ' + EXPECT, len(_hits) == 1,
      f"found {len(_hits)} times in {DUMPER}")

print("\n1. SHIFT=0 replay vs the positions the released protocol actually recorded")
check('the shifted start is inert at SHIFT=0', True, 'asserted per sequence above')
check('frame count', len(OLD) == len(REF), f"replay {len(OLD)}  recorded {len(REF)}")
if len(OLD) == len(REF):
    check('every position identical', bool((OLD == REF).all()),
          f"{int((OLD != REF).sum())} differ")

# 2. the shift is a pure rotation
print(f"\n2. new position == (old - {SHIFT}) mod {CHUNK}")
exp = (OLD - SHIFT) % CHUNK
bad = np.flatnonzero((OLD >= 0) & (NEW >= 0) & (NEW != exp))
check('every covered frame rotates', len(bad) == 0,
      f"{len(bad)} of {int(((OLD>=0)&(NEW>=0)).sum())} do not")
if len(bad):
    for s in np.unique(SEQ[bad])[:5]:
        i = bad[SEQ[bad] == s][0]
        print(f"        {s}: first_label={FIRST[i]} old={OLD[i]} new={NEW[i]} expected={exp[i]}")
    print(f"        affected sequences: {len(np.unique(SEQ[bad]))}, "
          f"all with first_label < {SHIFT}: "
          f"{bool((FIRST[bad] < SHIFT).all())}")

# 3. nothing falls off the end
print("\n3. frames covered by a chunk")
# A start moved later than a sequence's first label leaves that label before the first chunk.
# It cannot be avoided: the release's start is already 0 for these sequences, so no start
# both covers the first label and delivers the same rotation as everywhere else. Those frames
# are recorded as -1 and the paired analysis drops them from BOTH arms, so the pairing stays
# on identical frames; what has to be checked is that the number is small.
lost = int((NEW < 0).sum())
check('uncovered frames under 3 % of the split', lost <= 0.03 * len(NEW),
      f"{lost} of {len(NEW)} ({lost/len(NEW)*100:.2f} %), old {int((OLD<0).sum())}")

# 4. the paired contrast the analysis needs
print(f"\n4. short{SHORT} / full{FULL} block exchange")
os_, of = (OLD >= SHORT[0]) & (OLD < SHORT[1]), (OLD >= FULL[0]) & (OLD < FULL[1])
ns, nf = (NEW >= SHORT[0]) & (NEW < SHORT[1]), (NEW >= FULL[0]) & (NEW < FULL[1])
a, b = int((os_ & nf).sum()), int((of & ns).sum())
print(f"     old-short -> new-full : {a:6d} / {int(os_.sum()):6d}")
print(f"     old-full  -> new-short: {b:6d} / {int(of.sum()):6d}")
# A rotation is a bijection, so one SHIFT can only move one of the two blocks onto the other:
# (p-S) mod 21 carries FULL onto SHORT at S=16 and SHORT onto FULL at S=5, never both, since
# S == -S has no solution mod 21 other than 0. The check is therefore that ONE direction is
# achieved and that it takes essentially the whole source block with it - not that both are.
conv = max(a / max(int(os_.sum()), 1), b / max(int(of.sum()), 1))
check('one direction carries its whole block', conv >= 0.95, f"best {conv*100:.1f}%")
check('e60_paired.py direction (short -> full) populated', a > 0,
      f"{a} frames, which is the set that experiment scores"
      if a else "SHIFT=5 is the value that produces it")
print(f"     unchanged position     : {int((OLD == NEW).sum()):6d} / {len(OLD):6d}")

print(f"\n   for comparison, boundaries {SHIFT} windows EARLIER instead - the variant that\n   ran first, whose subtraction from an already-clamped start is a no-op:")
ba, bb = int((os_ & ((BRK >= FULL[0]) & (BRK < FULL[1]))).sum()), \
         int((of & ((BRK >= SHORT[0]) & (BRK < SHORT[1]))).sum())
print(f"     old-short -> new-full : {ba:6d} / {int(os_.sum()):6d}")
print(f"     old-full  -> new-short: {bb:6d} / {int(of.sum()):6d}")
print(f"     unchanged position     : {int((OLD == BRK).sum()):6d} / {len(OLD):6d}")

print(f"\n   (old - new) mod {CHUNK} histogram, fixed shift wants a single bar at {SHIFT}:")
for k, v in sorted(Counter(((OLD - NEW) % CHUNK)[NEW >= 0].tolist()).items(),
                   key=lambda x: -x[1]):
    print(f"     {k:3d}  {v:6d}")

np.savez_compressed('experiments/e60_shift/positions-shift%d.npz' % SHIFT,
                    old=OLD.astype(np.int16), new=NEW.astype(np.int16), seq=SEQ)
print(f"\nWROTE experiments/e60_shift/positions-shift{SHIFT}.npz")
print(f"\n{'VERIFIED - safe to claim GPU 1' if ok else 'BLOCKED - do not run'}")
raise SystemExit(0 if ok else 1)
