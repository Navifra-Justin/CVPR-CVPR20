"""E53 - the fastest stratum, and the arithmetic that bounds the negative result.

E52 found that scoring each detector at its own argmax leaves the ordering of five released
checkpoints unchanged in every stratum it examined. Before that is reported as a negative
result it is worth stating why it cannot be an artefact of the delta grid: the largest gain
any model draws from alignment is smaller than the smallest gap between adjacent models, so
no refinement of the grid can reorder them. That bound is computed here.

The one stratum E52 did not cover is the fastest one, above 50 px/s, where the paper's own
sweep is widest (0.37 points over +-50 ms against 0.11 for the slow stratum) and where the
gaps between models are smallest. If alignment can change a comparison anywhere, it is here.
"""
import numpy as np, json, glob, os, sys
src=open('src/e52_ranking.py').read()
head=src[:src.index('DELTAS=np.round')]
g={}; exec(head,g)
evaluate=g['evaluate']; NF=g['NF']; M=g['M']
DELTAS=np.round(np.arange(-0.050,0.0301,0.005),4)
CK='experiments/e51_ranking/curves_fast.json'
res=json.load(open(CK)) if os.path.exists(CK) else {}
for m in M:
    if m['name'] in res: print(f"  {m['name']:<12} done, skipped",flush=True); continue
    db=[[] for _ in range(NF)]
    for r in m['det']: db[int(r[0])].append(r)
    c=np.array([evaluate(db,float(d),50.,1e9) for d in DELTAS])
    i=int(np.argmax(c)); j=int(np.argmin(abs(DELTAS)))
    res[m['name']]=dict(deltas_ms=[float(d*1e3) for d in DELTAS],map=[float(v) for v in c],
                        map_at_zero=float(c[j]),argmax_ms=float(DELTAS[i]*1e3),
                        map_at_argmax=float(c[i]),span=float(100*(c.max()-c.min())))
    print(f"  {m['name']:<12} >50 px/s  mAP(0) {c[j]:.5f}   argmax {DELTAS[i]*1e3:+6.1f} ms"
          f"   gain {100*(c[i]-c[j]):+.3f} pt   sweep span {100*(c.max()-c.min()):.2f} pt",flush=True)
    json.dump(res,open(CK,'w'),indent=1); m['det']=None

names=[m['name'] for m in M]
z=sorted(((n,res[n]['map_at_zero']) for n in names),key=lambda r:-r[1])
a=sorted(((n,res[n]['map_at_argmax']) for n in names),key=lambda r:-r[1])
print("\n>50 px/s")
print("  order at delta=0         "+" > ".join(n for n,_ in z))
print("  order at each own argmax "+" > ".join(n for n,_ in a))
print(f"  order changes: {[n for n,_ in z]!=[n for n,_ in a]}")

print("\n=== why no grid refinement can change this ===")
allc=json.load(open('experiments/e51_ranking/curves.json'))
for sname in ['all moving','10-25 px/s','25-50 px/s']:
    v=sorted(((n,allc[n][sname]['map_at_zero']) for n in allc),key=lambda r:-r[1])
    gaps=[100*(v[k][1]-v[k+1][1]) for k in range(len(v)-1)]
    gains=[100*(allc[n][sname]['map_at_argmax']-allc[n][sname]['map_at_zero']) for n in allc]
    print(f"  {sname:<11} smallest gap between adjacent models {min(gaps):.3f} pt   "
          f"largest alignment gain {max(gains):.3f} pt   "
          f"reorderable: {max(gains)>min(gaps)}")
v=sorted(((n,res[n]['map_at_zero']) for n in names),key=lambda r:-r[1])
gaps=[100*(v[k][1]-v[k+1][1]) for k in range(len(v)-1)]
gains=[100*(res[n]['map_at_argmax']-res[n]['map_at_zero']) for n in names]
print(f"  {'>50 px/s':<11} smallest gap between adjacent models {min(gaps):.3f} pt   "
      f"largest alignment gain {max(gains):.3f} pt   reorderable: {max(gains)>min(gaps)}")
json.dump(res,open(CK,'w'),indent=1)
print("\nWROTE "+CK)
