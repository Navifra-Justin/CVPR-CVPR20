"""Unit confirmation that the release's carried state reaches no output of its scan.

E47c measured, on the real model, that zeroing the state entering a chunk changes the
emitted detection tensor by exactly 0.0 at every position, and
experiments/e47_ssm/withdrawn_L1/WHY.md derives why: apply_ssm injects the state only as
`Lambda_bars[0] = Lambda_bars[0] * prev_state`, while the scan's outputs are the `b`
components of `(a_i,b_i) o (a_j,b_j) = (a_j*a_i, a_j*b_i + b_j)`, so `b_p` is built from
`a_1..a_p` and `b_0..b_p` and `a_0` reaches nothing.

A derivation and a whole-model measurement can agree for the wrong reason, so this calls
apply_ssm itself with two different states on one input and reports the change per position.
It measures the release's code, not this paper's method, and decides one thing: whether the
state argument can affect any output at all.
"""
import sys, os
import numpy as np, torch
sys.path.insert(0, '/work/src/SSMViT')
from models.layers.s5.s5_model import apply_ssm

torch.manual_seed(0)
L, H, N = 8, 6, 4                       # positions, feature width, state width
# as_complex reads a trailing pair, which is how the release stores its complex tensors.
lam = torch.randn(N, 2); lam[:, 0] += 0.9
Bb  = torch.randn(N, H, 2) * 0.1
Ct  = torch.randn(H, N, 2) * 0.1
D   = torch.randn(H)
u   = torch.randn(L, H)
zero = torch.zeros(N, dtype=torch.complex64)
rand = torch.randn(N, dtype=torch.complex64)

def run(ps):
    y, last = apply_ssm(lam.clone(), Bb.clone(), Ct.clone(), D.clone(), u.clone(), ps.clone())
    return y, last

y0, s0 = run(zero)
y1, s1 = run(rand)
rel = [float((y1[p] - y0[p]).norm() / max(float(y0[p].norm()), 1e-12)) for p in range(L)]
print('relative change per position, prev_state zero -> random:')
print('  ' + '  '.join(f'{p}:{v:.3e}' for p, v in enumerate(rel)))
print(f'  max over positions {max(rel):.3e}   outputs bitwise equal {torch.equal(y0, y1)}')
print(f'  returned state bitwise equal {torch.equal(s0, s1)}   |state| {float(s0.abs().sum()):.4f}')
ok = torch.equal(y0, y1)
print('STATE_INERT_CONFIRMED' if ok else 'STATE_REACHES_OUTPUT')
sys.exit(0 if ok else 1)
