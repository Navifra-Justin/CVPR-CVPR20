"""E51-check - is the new dump the same instrument E37 used?

E51 rewrote the detection dump to take a family and a tag. If its rvt-t output does not
reproduce E37's dets.npz, then every comparison built on E51 is measuring the rewrite rather
than the models. This compares the two arrays directly before any of that is trusted.
"""
import numpy as np, os, sys
A='experiments/e37_map/dets.npz'; B='experiments/e51_ranking/dets-rvt-t.npz'
if not os.path.exists(B): raise SystemExit("rvt-t dump not written yet")
Za,Zb=np.load(A),np.load(B)
FAIL=False
for k in ('det','gt'):
    a,b=Za[k],Zb[k]
    same_shape=a.shape==b.shape
    print(f"{k}: E37 {a.shape}  E51 {b.shape}  same shape {same_shape}")
    if not same_shape:
        print("   SHAPES DIFFER - the rewrite changed what is dumped"); sys.exit(1)
    fa,fb=np.isfinite(a),np.isfinite(b)
    nanmis=int((fa!=fb).sum())
    d=np.abs(a.astype(np.float64)-b.astype(np.float64)); d=d[fa&fb]
    bad=int((d>0).sum())+nanmis
    print(f"   differing entries {bad}   max abs diff {(d.max() if len(d) else 0):.3e}")
    if bad:
        cols=['fid','x1','y1','x2','y2','cls','vx','vy'] if k=='gt' else \
             ['fid','x1','y1','x2','y2','score','cls']
        for c in range(a.shape[1]):
            f1,f2=np.isfinite(a[:,c]),np.isfinite(b[:,c])
            dd=np.abs(a[:,c]-b[:,c])[f1&f2]
            n=int((dd>0).sum())+int((f1!=f2).sum())
            if n: print(f"     column {cols[c]}: {n} differ, max {dd.max() if len(dd) else float('nan'):.4g}")
        FAIL=True
print()
if FAIL:
    print("E51 does NOT reproduce E37's rvt-t dump. Until it does, a cross-model comparison "
          "built on it is not commensurable with the numbers already in the paper.")
    sys.exit(1)
print("E51 reproduces E37's rvt-t dump, so the cross-model comparison is the same "
      "instrument the paper already reports.")
