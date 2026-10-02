"""E71 frame selection: 3000 frames stratified over the validation sequences, only frames with r+1 >= 80.

Frame universe = the e66 dump (same frame ids as e51 / e65). Stratum = sequence; proportional allocation
(largest remainder), every sequence with eligible frames gets >=1 if the budget allows, no sequence gets more than
its eligible count; inside a sequence frames are drawn without replacement (seed fixed).
Output: experiments/e71_h4080/frames.npz (gid, seq, j, ri) and frames.json (summary).
"""
import numpy as np, json
Z = np.load('experiments/e66_fixedH/dets-rvt-s.npz')
seq, ri, done = Z['seq'], Z['ri'], Z['done']
gid = np.arange(len(seq)); loc = np.zeros(len(seq), int)
for s in np.unique(seq):
    m = np.flatnonzero(seq == s); loc[m] = np.arange(len(m))
el = done & (ri + 1 >= 80)
N = 3000; rng = np.random.default_rng(20261002)
S = np.unique(seq[el]); cnt = np.array([(el & (seq == s)).sum() for s in S])
q = cnt / cnt.sum() * N; a = np.minimum(np.floor(q).astype(int), cnt)
a = np.maximum(a, 1)
while a.sum() > N:
    i = np.argmax(a - q); a[i] -= 1
while a.sum() < N:
    r = np.where(a < cnt, q - a, -1e9); a[np.argmax(r)] += 1
assert a.sum() == N and (a <= cnt).all()
sel = []
for s, k in zip(S, a):
    m = np.flatnonzero(el & (seq == s)); sel += list(np.sort(rng.choice(m, k, replace=False)))
sel = np.array(sorted(sel))
np.savez('experiments/e71_h4080/frames.npz', gid=gid[sel], seq=seq[sel], j=loc[sel], ri=ri[sel])
info = dict(n_frames=int(len(sel)), n_sequences_eligible=int(len(S)), n_sequences_total=int(len(np.unique(seq))),
            eligible_frames=int(el.sum()), done_frames=int(done.sum()), min_per_seq=int(a.min()), max_per_seq=int(a.max()), seed=20261002,
            ri_min=int(ri[sel].min()), ri_max=int(ri[sel].max()))
json.dump(info, open('experiments/e71_h4080/frames.json', 'w'), indent=1); print(info)
