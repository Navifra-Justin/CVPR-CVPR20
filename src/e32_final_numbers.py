"""E32 - the numbers that go into the manuscript, and a cluster bootstrap on the
specification E30 selected.

The specification was not chosen to make tau large. It was chosen by the placebo - the
rotated-velocity coefficient, on which no temporal offset can load - returning to null.
That criterion carries no information about tau. This script reports that specification,
its bootstrap interval, the two hypothesis tests, and the displacement the interval
amounts to at speeds that occur in the split.
"""
import os, numpy as np, json
Z=np.load('experiments/e27_rows/rows.npz',allow_pickle=True)
A=Z['rows']; ci={c:i for i,c in enumerate(list(Z['cols']))}
g=lambda k:A[:,ci[k]]
seq,dx,dy=g('seq'),g('dx'),g('dy')
fx,fy,dtf,bx,by,dtb=g('fx'),g('fy'),g('dt_f'),g('bx'),g('by'),g('dt_b')
gw,gh,gcx,gcy,io=g('gw'),g('gh'),g('gcx'),g('gcy'),g('iou')
vx=(fx+bx)/(dtf+dtb); vy=(fy+by)/(dtf+dtb)
m=np.isfinite(vx)&np.isfinite(vy)&(np.hypot(vx,vy)>0)
vx,vy,seq,dx,dy,gw,gh,gcx,gcy,io=[a[m] for a in (vx,vy,seq,dx,dy,gw,gh,gcx,gcy,io)]
size=np.sqrt(gw*gh); V=np.hypot(vx,vy); ux,uy=vx/V,vy/V
zero=np.zeros_like(vx)
u=np.unique(seq); D=(seq[:,None]==u[None,:]).astype(float)
cx=[vx,-vy,size*ux,zero,zero,gcx,gw]; cy=[vy,vx,size*uy,gh,gcy,zero,zero]
X=np.vstack([np.hstack([np.column_stack(cx),D,np.zeros_like(D)]),
             np.hstack([np.column_stack(cy),np.zeros_like(D),D])])
y=np.concatenate([dx,dy]); gg=np.concatenate([seq,seq])

def cluster_ols(X,y,g):
    XtXi=np.linalg.inv(X.T@X); b=XtXi@(X.T@y); r=y-X@b
    meat=np.zeros((X.shape[1],)*2)
    for c in np.unique(g):
        s=g==c; uu=X[s].T@r[s]; meat+=np.outer(uu,uu)
    G=len(np.unique(g)); n,k=X.shape
    cov=XtXi@meat@XtXi*(G/max(G-1,1))*((n-1)/max(n-k,1))
    return b,np.sqrt(np.diag(cov))
b,se=cluster_ols(X,y,gg)
tau,tse=-b[0]*1e3,se[0]*1e3; pl,pse=-b[1]*1e3,se[1]*1e3
print(f"rows {len(vx)}  sequences {len(u)}  regressors {X.shape[1]}")
print(f"tau      = {tau:+.2f} +- {tse:.2f} ms   ({abs(tau/tse):.2f} SE from zero)")
print(f"placebo  = {pl:+.2f} +- {pse:.2f} ms   ({abs(pl/pse):.2f} SE from zero)")
CEN=23.810   # E45; E17's 24.94 is superseded
print(f"H tau=0      : {abs(tau-0)/tse:.2f} SE")
print(f"H tau={CEN}  : {abs(tau-CEN)/tse:.2f} SE")
print(f"interval evidence->output = {CEN-tau:+.2f} +- {tse:.2f} ms")

# cluster bootstrap over sequences
rng=np.random.default_rng(0); idx={c:np.where(gg==c)[0] for c in u}
ts=[];ps=[]
for _ in range(2000):
    pick=rng.choice(u,len(u),replace=True)
    ii=np.concatenate([idx[c] for c in pick])
    try:
        bb=np.linalg.lstsq(X[ii],y[ii],rcond=None)[0]; ts.append(-bb[0]*1e3); ps.append(-bb[1]*1e3)
    except Exception: pass
ts=np.array(ts); ps=np.array(ps)
print(f"bootstrap tau     median {np.median(ts):+.2f}  95% CI [{np.percentile(ts,2.5):+.2f}, {np.percentile(ts,97.5):+.2f}]")
print(f"bootstrap placebo median {np.median(ps):+.2f}  95% CI [{np.percentile(ps,2.5):+.2f}, {np.percentile(ps,97.5):+.2f}]")
print(f"  fraction of bootstrap draws with tau >= {CEN} ms: {np.mean(ts>=CEN):.4f}")

print("\nspeed distribution of the matched boxes (px/s)")
qs=[50,75,90,95,99]
for q in qs: print(f"  p{q:<3d} {np.percentile(V,q):8.2f}   displacement over {CEN:.2f} ms = {np.percentile(V,q)*CEN*1e-3:6.4f} px")
print(f"  mean  {V.mean():8.2f}")
print(f"\nmatched-box statistics: median IoU {np.median(io):.3f}, median box side {np.median(size):.1f} px")
json.dump(dict(n=int(len(vx)),nseq=int(len(u)),tau_ms=float(tau),tau_se_ms=float(tse),
               placebo_ms=float(pl),placebo_se_ms=float(pse),
               se_from_zero=float(abs(tau/tse)),se_from_centroid=float(abs(tau-CEN)/tse),
               interval_ms=float(CEN-tau),
               boot_lo=float(np.percentile(ts,2.5)),boot_hi=float(np.percentile(ts,97.5)),
               boot_median=float(np.median(ts)),
               p_boot_ge_centroid=float(np.mean(ts>=CEN)),
               speed_p50=float(np.percentile(V,50)),speed_p90=float(np.percentile(V,90)),
               speed_p99=float(np.percentile(V,99)),
               median_iou=float(np.median(io)),median_side=float(np.median(size))),
          open('experiments/e27_rows/final.json','w'),indent=1)
print("WROTE experiments/e27_rows/final.json")
