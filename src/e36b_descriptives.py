"""E36b - the descriptive numbers the manuscript quotes, written to a log.

A number-verification audit found several macros whose only written source was a README
paragraph rather than a machine-written artifact: the speed percentiles of the fit sample,
the displacement they imply, the median overlap and box side, and the static fraction.
They were correct, but "correct and unlogged" is the state that lets a number drift. This
recomputes each from rows.npz and prints it.
"""
import numpy as np, json
Z=np.load('experiments/e27_rows/rows.npz',allow_pickle=True)
A=Z['rows']; ci={c:i for i,c in enumerate(list(Z['cols']))}
g=lambda k:A[:,ci[k]]
vx=(g('fx')+g('bx'))/(g('dt_f')+g('dt_b')); vy=(g('fy')+g('by'))/(g('dt_f')+g('dt_b'))
m=np.isfinite(vx)&np.isfinite(vy)&(np.hypot(vx,vy)>0)
V=np.hypot(vx,vy)[m]; io=g('iou')[m]; side=np.sqrt(g('gw')*g('gh'))[m]
CEN=0.023810   # E45; E17's 0.02494 is superseded
print(f"fit sample: n={m.sum()}  sequences={len(np.unique(g('seq')[m]))}")
print(f"  median overlap        {np.median(io):.3f}")
print(f"  median box side       {np.median(side):.1f} px")
print(f"  below 2 px/s          {100*np.mean(V<2):.1f} %")
for q in (50,75,90,95,99):
    print(f"  speed p{q:<3d}          {np.percentile(V,q):7.2f} px/s   "
          f"x {CEN*1e3:.2f} ms = {np.percentile(V,q)*CEN:6.4f} px")
print(f"  mean speed            {V.mean():7.2f} px/s")
json.dump(dict(n=int(m.sum()),median_iou=float(np.median(io)),
               median_side=float(np.median(side)),
               frac_below_2=float(np.mean(V<2)),
               speed={str(q):float(np.percentile(V,q)) for q in (50,75,90,95,99)},
               px_at={str(q):float(np.percentile(V,q)*CEN) for q in (50,75,90,95,99)}),
          open('experiments/e27_rows/descriptives.json','w'),indent=1)
print("WROTE experiments/e27_rows/descriptives.json")
