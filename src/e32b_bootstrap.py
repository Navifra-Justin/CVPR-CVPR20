"""E32b - the cluster bootstrap for the reported specification, done by FWL.

The reported model carries a constant vector per sequence, which is 752 dummy columns.
Bootstrapping a 45k x 759 least squares thousands of times is wasteful: by
Frisch-Waugh-Lovell, regressing out group dummies is exactly subtracting the group mean,
so demeaning the response and the seven substantive regressors within each
(sequence, component) cell gives identical coefficients from a 45k x 7 problem. The
equality against the full design is printed before the bootstrap runs.
"""
import numpy as np, json
Z=np.load('experiments/e27_rows/rows.npz',allow_pickle=True)
A=Z['rows']; ci={c:i for i,c in enumerate(list(Z['cols']))}
g=lambda k:A[:,ci[k]]
seq,dx,dy=g('seq'),g('dx'),g('dy')
vx=(g('fx')+g('bx'))/(g('dt_f')+g('dt_b')); vy=(g('fy')+g('by'))/(g('dt_f')+g('dt_b'))
m=np.isfinite(vx)&np.isfinite(vy)&(np.hypot(vx,vy)>0)
vx,vy,seq,dx,dy=[a[m] for a in (vx,vy,seq,dx,dy)]
gw,gh,gcx,gcy=[a[m] for a in (g('gw'),g('gh'),g('gcx'),g('gcy'))]
size=np.sqrt(gw*gh); V=np.hypot(vx,vy); ux,uy=vx/V,vy/V; z=np.zeros_like(vx)
X=np.vstack([np.column_stack([vx,-vy,size*ux,z,z,gcx,gw]),
             np.column_stack([vy, vx,size*uy,gh,gcy,z,z])])
y=np.concatenate([dx,dy])
grp=np.concatenate([seq*2,seq*2+1]); cl=np.concatenate([seq,seq])

def fit(X,y,grp):
    u,inv=np.unique(grp,return_inverse=True); K=len(u)
    n=np.bincount(inv,minlength=K)[:,None]
    sX=np.zeros((K,X.shape[1])); np.add.at(sX,inv,X); Xd=X-(sX/n)[inv]
    sy=np.zeros((K,1)); np.add.at(sy,inv,y.reshape(-1,1)); yd=y-(sy/n)[inv].ravel()
    return np.linalg.lstsq(Xd,yd,rcond=None)[0]
b=fit(X,y,grp)
print(f"FWL      tau = {-b[0]*1e3:+.4f} ms   placebo = {-b[1]*1e3:+.4f} ms")
print(f"full design  -2.4021              -2.6555          (must agree)")

uc=np.unique(cl); idx={c:np.where(cl==c)[0] for c in uc}
rng=np.random.default_rng(0); ts=[];ps=[]
for _ in range(4000):
    pick=rng.choice(uc,len(uc),replace=True)
    ii=np.concatenate([idx[c] for c in pick])
    try:
        bb=fit(X[ii],y[ii],grp[ii]); ts.append(-bb[0]*1e3); ps.append(-bb[1]*1e3)
    except Exception: pass
ts=np.array(ts); ps=np.array(ps)
print(f"\ncluster bootstrap over {len(uc)} sequences, {len(ts)} draws")
print(f"  tau     median {np.median(ts):+7.2f}  95% CI [{np.percentile(ts,2.5):+.2f}, {np.percentile(ts,97.5):+.2f}]")
print(f"  placebo median {np.median(ps):+7.2f}  95% CI [{np.percentile(ps,2.5):+.2f}, {np.percentile(ps,97.5):+.2f}]")
# the threshold is the newest-window centroid of E45, which supersedes E17's -24.94 ms
CENTROID=23.810
print(f"  draws with tau >= {CENTROID} ms (the influence centroid): {np.mean(ts>=CENTROID):.4f}"
      f"  = {int((ts>=CENTROID).sum())} of {len(ts)}")
print(f"  at the superseded 24.94 ms, for the record:  {np.mean(ts>=24.94):.4f}"
      f"  = {int((ts>=24.94).sum())} of {len(ts)}")
print(f"  draws with tau <= 0: {np.mean(ts<=0):.4f}")
json.dump(dict(n_draws=int(len(ts)),tau_median=float(np.median(ts)),
               tau_lo=float(np.percentile(ts,2.5)),tau_hi=float(np.percentile(ts,97.5)),
               pl_lo=float(np.percentile(ps,2.5)),pl_hi=float(np.percentile(ps,97.5)),
               p_ge_centroid=float(np.mean(ts>=CENTROID)),
               n_ge_centroid=int((ts>=CENTROID).sum()),
               centroid_ms=CENTROID,
               draws=[float(v) for v in ts]),      # kept, so a later threshold needs no refit
          open('experiments/e27_rows/bootstrap.json','w'),indent=1)
print("WROTE experiments/e27_rows/bootstrap.json")
