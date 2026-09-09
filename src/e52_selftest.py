"""E52 self-test - does the faster evaluator reproduce the numbers already in the paper?

E52 rewrites E37b's greedy matching so that 255 evaluations are affordable. A rewrite of a
metric is exactly the kind of change that quietly moves a reported number, so before it is
used it is run on the rvt-t dump and compared against E37b's own sweep and E46b's evaluation
at the corrected centroid, both of which are already in the manuscript.
"""
import numpy as np, json, sys
src=open('src/e52_ranking.py').read()
head=src[:src.index('DELTAS=np.round')]
head=head.replace("FILES=sorted(glob.glob('experiments/e51_ranking/dets-*.npz'))",
                  "FILES=['experiments/e51_ranking/dets-rvt-t.npz']")
head=head.replace("if len(FILES)<2: raise SystemExit","if len(FILES)<1: raise SystemExit")
g={}; exec(head,g)
evaluate=g['evaluate']; NF=g['NF']; M=g['M']
db=[[] for _ in range(NF)]
for r in M[0]['det']: db[int(r[0])].append(r)
ref=json.load(open('experiments/e37_map/sweep.json'))['moving']
cen=json.load(open('experiments/e37_map/at_centroid.json'))['moving']
checks=[('delta=0',0.0,cen['zero']['map']),
        ('delta=-23.810 (E46b)',-0.023810,cen['centroid_new']['map']),
        ('delta=-25 (E37b grid)',-0.025,ref['map'][ref['deltas_ms'].index(-25.0)]),
        ('delta=-10 (E37b argmax)',-0.010,ref['map'][ref['deltas_ms'].index(-10.0)])]
bad=0
for name,d,want in checks:
    got=evaluate(db,d,None,None)
    ok=abs(got-want)<5e-6
    print(f"  {name:<26} E52 {got:.6f}   published {want:.6f}   {'ok' if ok else 'DIFFERS'}")
    bad+= (not ok)
print(f"\n{len(checks)-bad} of {len(checks)} agree with the published numbers")
sys.exit(1 if bad else 0)
