"""Emit the LaTeX macros for E65 from experiments/e65_rvt_boundary/paired-shift5.json.

Nothing here is typed by hand. src/audit_numbers.py re-derives each of these from the same
file, so a macro edited without a corresponding run fails the audit rather than review.
"""
import json

P = json.load(open('experiments/e65_rvt_boundary/paired-shift5.json'))
A = P['arms']

# One n serves every row only if every arm paired the same frames, which they do by
# construction: the four arms share a position file and the same selection rule. Asserted
# rather than assumed, because a silent difference would make the rows incomparable.
_n = {k: v['n'] for k, v in A.items()}
assert len(set(_n.values())) == 1, f'E65 arms pair different frame counts: {_n}'

_carry = [A[k]['map_vel_boot']['obs'] for k in A if k.endswith('-carry')]
_reset = [A[k]['map_vel_boot']['obs'] for k in A if k.endswith('-reset')]
_perm = [A[k]['perm_null'] for k in A]

M = dict(
    rvtBoundN=(next(iter(_n.values())), 0),
    rvtBoundShift=(P['shift'], 0),
    rvtBoundB=(P['B'], 0),
    rvtBoundPermR=(P['rperm'], 0),
)
for tag, lab in (('s', 'S'), ('b', 'B')):
    for reg, rlab in (('carry', 'Carry'), ('reset', 'Reset')):
        k = f'{tag}-{reg}'
        if k not in A:
            continue
        d = A[k]['map_vel_boot']
        M[f'rvtBound{rlab}{lab}'] = (d['obs'], 2)
        M[f'rvtBound{rlab}{lab}SE'] = (d['se'], 2)
        M[f'rvtBound{rlab}{lab}Z'] = (d['z'], 1)
        M[f'rvtBound{rlab}{lab}All'] = (A[k]['map_all_boot']['obs'], 2)

# The two summary quantities the manuscript states: the largest magnitude the released
# carried-state arm reaches over the checkpoints, and the smallest the reset ablation
# reaches. Stated as a bound and a floor rather than as one checkpoint's value, so the
# sentence does not depend on which checkpoint happens to be larger.
M['rvtBoundCarryMax'] = (max(abs(x) for x in _carry), 2)
M['rvtBoundResetMin'] = (min(_reset), 2)
# The random-frame null: its largest absolute centre and its largest spread over the arms.
M['rvtBoundPermMax'] = (max(abs(p['mean']) for p in _perm), 3)
M['rvtBoundPermSd'] = (max(p['sd'] for p in _perm), 2)

for k, (v, d) in M.items():
    print(f'\\newcommand{{\\{k}}}{{{v:.{d}f}}}')
