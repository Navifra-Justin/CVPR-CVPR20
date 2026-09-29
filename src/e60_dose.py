"""E60 - the chunk-boundary intervention read at four shift amounts.

run_e60_paired_sweep.sh writes one paired record per amount. This collects them into a
single artifact and checks the two properties the dose reading depends on.

The shift rotates every chunk position by -SHIFT (mod 21), so the block the release
starved, positions 0-3, lands on (0-3 - SHIFT) mod 21. The history a starved frame gains
is therefore set by the amount:

    SHIFT =  0  ->  positions  0- 3,  1- 4 windows,  gained  0
    SHIFT = 15  ->  positions  6- 9,  7-10 windows,  gained  6
    SHIFT = 10  ->  positions 11-14, 12-15 windows,  gained 11
    SHIFT =  5  ->  positions 16-19, 17-20 windows,  gained 16

Two checks, because the ladder is only a dose reading if they hold:

  1. every arm scores the SAME frames, not merely the same number of them. If the arms
     scored different frames the four rows would be four populations and could not be read
     as one curve. This is checked from the position files, by set equality.
  2. SHIFT = 0 is the null arm. Its two dumps are the same bytes, so every channel must be
     exactly 0. A non-zero there would mean the pairing itself moves the number.

Writes experiments/e60_shift/dose.json, which src/audit_numbers.py reads.
"""
import json, os, numpy as np

SHIFTS = (0, 15, 10, 5)          # ordered by the history each one gains
CHUNK, SHORT = 21, (0, 4)
D = 'experiments/e60_shift'

pa = np.load('experiments/e58_chunkpos/positions.npy')
starved = np.flatnonzero((pa >= 0) & (pa < SHORT[1]))

rows, framesets = [], {}
for S in SHIFTS:
    rec = json.load(open(f'{D}/paired-shift{S}.json'))
    assert rec['shift'] == S, f'paired-shift{S}.json records shift {rec["shift"]}'
    gain = sorted((p - S) % CHUNK for p in range(*SHORT))
    assert sorted(rec['gain']) == gain, f'SHIFT={S}: gain block {rec["gain"]} != {gain}'

    if S == 0:
        # The null arm's two dumps are the same file; its frame set is every starved frame.
        framesets[S] = set(starved.tolist())
    else:
        z = np.load(f'{D}/positions-shift{S}.npz')
        assert np.array_equal(z['old'], pa), f'SHIFT={S}: replayed release positions differ'
        framesets[S] = set(starved[np.isin(z['new'][starved], gain)].tolist())

    m = rec['models']
    assert m['small']['n'] == m['base']['n'], f'SHIFT={S}: arms pair different frame counts'
    rows.append(dict(
        shift=S, gain_positions=gain, windows=[min(gain) + 1, max(gain) + 1],
        gained=min(gain) + 1 - (SHORT[0] + 1), n=m['base']['n'],
        base=m['base']['map_vel_boot']['obs'], base_se=m['base']['map_vel_boot']['se'],
        base_z=m['base']['map_vel_boot']['z'],
        small=m['small']['map_vel_boot']['obs'], small_se=m['small']['map_vel_boot']['se'],
        small_z=m['small']['map_vel_boot']['z']))

# Check 1: one population, three treatments (the null arm is the identity rotation).
treated = [s for s in SHIFTS if s != 0]
common = set.intersection(*(framesets[s] for s in treated))
same = all(framesets[s] == common for s in treated)
assert same, 'the treated arms do not score the same frames; the ladder is not a dose curve'

# Check 2: the null arm is exactly inert.
null = json.load(open(f'{D}/paired-shift0.json'))['models']
for tag in ('small', 'base'):
    for k in ('map_vel', 'map_all', 'conf', 'conf_tp', 'dpf'):
        v = null[tag][k + '_boot']['obs']
        assert v == 0.0, f'SHIFT=0 {tag} {k} is {v}, not exactly 0'

# The null arm covers every starved frame, because at SHIFT = 0 the rotation is the
# identity and no frame is pushed off the front of its sequence; the treated arms lose the
# frames whose sequence is too short to carry the moved boundary. So n_paired is the
# treated arms' shared count, and the null arm's is recorded separately. The null delta is
# exactly 0 on any subset, the two dumps being the same bytes, so the difference in
# population does not make the two comparable rows.
_tn = {rows[SHIFTS.index(s_)]['n'] for s_ in treated}
assert len(_tn) == 1, f'treated arms pair different frame counts: {_tn}'
out = dict(shifts=list(SHIFTS), chunk=CHUNK, short=list(SHORT),
           n_starved=int(len(starved)), n_paired=_tn.pop(),
           n_null=rows[SHIFTS.index(0)]['n'],
           same_frames_across_arms=bool(same), null_arm_exactly_zero=True, rows=rows)
json.dump(out, open(f'{D}/dose.json', 'w'), indent=1)

# rows[0] is the null arm, which pairs every starved frame; the treated arms pair the
# subset whose sequence is long enough to carry the moved boundary. Reporting rows[0]["n"]
# as the paired count would print the null arm's 3672 beside treated rows measured on 3574.
print(f'{len(starved)} frames the release starved; null arm pairs {out["n_null"]}, '
      f'each treated arm pairs {out["n_paired"]}')
print(f'same frames in every treated arm: {"yes" if same else "no"}    '
      f'SHIFT=0 exactly inert: yes')
print(f'{"shift":>6} {"positions":>10} {"windows":>9} {"gained":>7} {"S5-B dmAP":>18} {"S5-S dmAP":>18}')
for r in rows:
    print(f'{r["shift"]:6d} {str(r["gain_positions"][0])+"-"+str(r["gain_positions"][-1]):>10}'
          f' {str(r["windows"][0])+"-"+str(r["windows"][1]):>9} {r["gained"]:+7d}'
          f'   {r["base"]:+7.2f} +- {r["base_se"]:.2f}   {r["small"]:+7.2f} +- {r["small_se"]:.2f}')
mono = all(rows[i]['base'] <= rows[i + 1]['base'] for i in range(len(rows) - 1))
monos = all(rows[i]['small'] <= rows[i + 1]['small'] for i in range(len(rows) - 1))
print(f'monotone in history gained: S5-B {mono}, S5-S {monos}')
print('WROTE', f'{D}/dose.json')
