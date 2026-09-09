"""E31 - do the controls eat the lag? Inject a known one into the real rows and look.

E30 selected a specification by a criterion that carries no information about tau: the
placebo, a rotated-velocity term no temporal offset can load on, returns to null only once
four directed geometric regressors and a per-sequence bias vector are present. Under that
specification tau falls from +14.62 to -2.40 +- 7.18 ms.

The obvious objection is that those controls absorbed a real lag. It is answerable on the
real rows rather than by argument. A detector lagging by tau displaces its prediction by
-tau*v; adding exactly that to the observed residual builds a dataset with a known extra
lag and with every real confound, every real correlation between speed and geometry, and
every real sequence, left in place. If the controls ate a lag, the injected one comes back
short.

Arm 2 does the reverse and injects a purely geometric displacement, to check the controls
absorb what they are for.
"""
import os, numpy as np, json
Z=np.load(os.environ.get('ROWS','experiments/e27_rows/rows.npz'),allow_pickle=True)
A=Z['rows']; ci={c:i for i,c in enumerate(list(Z['cols']))}
seq=A[:,ci['seq']]; dx0=A[:,ci['dx']]; dy0=A[:,ci['dy']]
fx=A[:,ci['fx']]; fy=A[:,ci['fy']]; dtf=A[:,ci['dt_f']]
bx=A[:,ci['bx']]; by=A[:,ci['by']]; dtb=A[:,ci['dt_b']]
gw=A[:,ci['gw']]; gh=A[:,ci['gh']]; gcx=A[:,ci['gcx']]; gcy=A[:,ci['gcy']]
size=np.sqrt(gw*gh)
vx=(fx+bx)/(dtf+dtb); vy=(fy+by)/(dtf+dtb)
m=np.isfinite(vx)&np.isfinite(vy)&(np.hypot(vx,vy)>0)
fx,fy,dtf,bx,by,dtb=[a[m] for a in (fx,fy,dtf,bx,by,dtb)]
vx,vy,seq,size,gw,gh,gcx,gcy=[a[m] for a in (vx,vy,seq,size,gw,gh,gcx,gcy)]
dx0,dy0=dx0[m],dy0[m]
V=np.hypot(vx,vy); ux,uy=vx/V,vy/V
one=np.ones(m.sum()); zero=np.zeros(m.sum())

def cluster_ols(X,y,g):
    XtXi=np.linalg.inv(X.T@X); b=XtXi@(X.T@y); r=y-X@b
    meat=np.zeros((X.shape[1],)*2)
    for c in np.unique(g):
        s=g==c; u=X[s].T@r[s]; meat+=np.outer(u,u)
    G=len(np.unique(g)); n,k=X.shape
    cov=XtXi@meat@XtXi*(G/max(G-1,1))*((n-1)/max(n-k,1))
    return b,np.sqrt(np.diag(cov))

def design(full):
    cx=[vx,-vy,size*ux]; cy=[vy,vx,size*uy]
    if full:
        cx+= [zero,zero,gcx,gw]; cy+= [gh,gcy,zero,zero]
    if full:
        u=np.unique(seq); D=(seq[:,None]==u[None,:]).astype(float)
        X=np.vstack([np.hstack([np.column_stack(cx),D,np.zeros_like(D)]),
                     np.hstack([np.column_stack(cy),np.zeros_like(D),D])])
    else:
        X=np.vstack([np.column_stack([one,zero]+cx),np.column_stack([zero,one]+cy)])
    return X
Xmin=design(False); Xfull=design(True)
g2=np.concatenate([seq,seq])
# alpha is column 2 in the minimal design (after the two bias columns), 0 in the full one
IMIN, IFULL = 2, 0
PMIN, PFULL = 3, 1

def run(ddx,ddy):
    out={}
    for tag,X,ia,ip in [('minimal',Xmin,IMIN,PMIN),('full controls',Xfull,IFULL,PFULL)]:
        b,se=cluster_ols(X,np.concatenate([ddx,ddy]),g2)
        out[tag]=(-b[ia]*1e3,se[ia]*1e3,-b[ip]*1e3,se[ip]*1e3)
    return out

print(f"rows {m.sum()}  sequences {len(np.unique(seq))}  median |v| {np.median(V):.1f} px/s\n")
print("ARM 1 - inject a lag of tau_inj by adding -tau_inj*v to the observed residual")
print("        recovery = (tau_hat with injection) - (tau_hat without)")
base=run(dx0,dy0)
print(f"  {'tau_inj':>8}   {'minimal: tau_hat':>22}  {'recovered':>10}   "
      f"{'full controls: tau_hat':>24}  {'recovered':>10}")
R={'base':{k:list(v) for k,v in base.items()}}
for ti in [0.0,0.010,0.025,0.050,0.100]:
    o=run(dx0-ti*vx,dy0-ti*vy)
    rmin=o['minimal'][0]-base['minimal'][0]; rful=o['full controls'][0]-base['full controls'][0]
    print(f"  {ti*1e3:+7.1f}   {o['minimal'][0]:+9.2f}+-{o['minimal'][1]:5.2f}       "
          f"{rmin:+7.2f} ({rmin/max(ti*1e3,1e-9) if ti else float('nan'):5.3f})   "
          f"{o['full controls'][0]:+9.2f}+-{o['full controls'][1]:5.2f}       "
          f"{rful:+7.2f} ({rful/max(ti*1e3,1e-9) if ti else float('nan'):5.3f})")
    R[f'inj{ti}']={k:list(v) for k,v in o.items()}

print("\nARM 2 - inject a purely geometric displacement, gamma * height along image y")
print("        the controls exist to absorb this; tau must not move")
for gi in [0.0,0.02,0.05]:
    o=run(dx0,dy0+gi*gh)
    print(f"  gamma={gi:4.2f}   minimal tau {o['minimal'][0]:+8.2f}   "
          f"full-control tau {o['full controls'][0]:+8.2f}   "
          f"minimal placebo {o['minimal'][2]:+8.2f}   full placebo {o['full controls'][2]:+8.2f}")
    R[f'geo{gi}']={k:list(v) for k,v in o.items()}

print("\nARM 3 - the sign-flip control under the full control set")
for mode,VX,VY in [('fwd',fx/dtf,fy/dtf),('back',bx/dtb,by/dtb),('centered',vx,vy)]:
    VV=np.hypot(VX,VY); UX,UY=VX/np.maximum(VV,1e-9),VY/np.maximum(VV,1e-9)
    cx=[VX,-VY,size*UX,zero,zero,gcx,gw]; cy=[VY,VX,size*UY,gh,gcy,zero,zero]
    u=np.unique(seq); D=(seq[:,None]==u[None,:]).astype(float)
    X=np.vstack([np.hstack([np.column_stack(cx),D,np.zeros_like(D)]),
                 np.hstack([np.column_stack(cy),np.zeros_like(D),D])])
    b,se=cluster_ols(X,np.concatenate([dx0,dy0]),g2)
    print(f"  velocity = {mode:<9} tau = {-b[0]*1e3:+8.2f} +- {se[0]*1e3:5.2f} ms   "
          f"placebo = {-b[1]*1e3:+8.2f} +- {se[1]*1e3:5.2f} ms")
    R[f'sf_{mode}']=[float(-b[0]*1e3),float(se[0]*1e3),float(-b[1]*1e3),float(se[1]*1e3)]

print("\nARM 4 - the hypothesis that the output sits at the evidence centroid")
t,s=base['full controls'][0],base['full controls'][1]
for h,nm in [(24.94,'evidence centroid (E17)'),(25.0,'uniform window centroid'),(0.0,'the label instant')]:
    print(f"  H: tau = {h:6.2f} ms ({nm:<26}) -> {abs(t-h)/s:5.2f} SE from the measurement")
json.dump(R,open('experiments/e27_rows/injection.json','w'),indent=1)
print("\nWROTE experiments/e27_rows/injection.json")
