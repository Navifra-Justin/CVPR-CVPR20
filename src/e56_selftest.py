"""E56 self-test: the refactored evaluator must reproduce the four values E52 was pinned to.

E52's own self-test fixed these against E37b, an independently written evaluator. Re-running
them here is what licenses E56 to quote numbers on the same scale as the manuscript's.
"""
import sys
from e56_eval import Scorer, load_dump

PINS = [(0.0, 0.334580), (-0.023810, 0.334193), (-0.025, 0.333990), (-0.010, 0.334632)]
det, gt = load_dump('experiments/e51_ranking/dets-rvt-t.npz')
S = Scorer(det, gt)
bad = 0
for d, want in PINS:
    got = S.evaluate(d)
    ok = abs(got - want) < 5e-6
    bad += (not ok)
    print(f"  delta {d*1e3:+8.3f} ms   got {got:.6f}   pinned {want:.6f}   {'ok' if ok else 'DISAGREES'}")
print(f"\n{len(PINS)-bad}/{len(PINS)} agree")
sys.exit(1 if bad else 0)
