"""E33 - is the reported tau an artefact of which geometric controls were paired with
which axis?

E30 entered box height and image row along y_hat, and box width and image column along
x_hat. Those pairings are the ones perspective suggests, but they are pairings, and a
reviewer is entitled to ask whether the choice made the answer. This enters every
geometric variable on BOTH axes - a saturated control set - and also drops each control in
turn, so the spread of tau across specifications is visible rather than asserted.
"""
import numpy as np, itertools, json
Z=np.load('experiments/e27_rows/rows.npz',allow_pickle=True)
A=Z['rows']; ci={c:i for i,c in enumerate(list(Z['cols']))}
g=lambda k:A[:,ci[k]]
seq,dx,dy=g('seq'),g('dx'),g('dy')
vx=(g('fx')+g('bx'))/(g('dt_f')+g('dt_b')); vy=(g('fy')+g('by'))/(g('dt_f')+g('dt_b'))
m=np.isfinite(vx)&np.isfinite(vy)&(np.hypot(vx,vy)>0)
vx,vy,seq,dx,dy=[a[m] for a in (vx,vy,seq,dx,dy)]
gw,gh,gcx,gcy,io=[a[m] for a in (g('gw'),g('gh'),g('gcx'),g('gcy'),g('iou'))]
size=np.sqrt(gw*gh); V=np.hypot(vx,vy); ux,uy=vx/V,vy/V; z=np.zeros_like(vx)
y=np.concatenate([dx,dy]); grp=np.concatenate([seq*2,seq*2+1]); cl=np.concatenate([seq,seq])
GEO={'height':gh,'row':gcy,'column':gcx,'width':gw,'side':size}

def fit(cols,keep=None,ret_se=True):
    kx=[vx,-vy,size*ux]; ky=[vy,vx,size*uy]
    for nm,ax in cols:
        v=GEO[nm]
        if ax=='x': kx.append(v); ky.append(z)
        elif ax=='y': kx.append(z); ky.append(v)
        else: kx.append(v*ux); ky.append(v*uy)
    X=np.vstack([np.column_stack(kx),np.column_stack(ky)]); yy=y; gp=grp; cc=cl
    if keep is not None:
        k2=np.concatenate([keep,keep]); X=X[k2]; yy=y[k2]; gp=grp[k2]; cc=cl[k2]
    u,inv=np.unique(gp,return_inverse=True); K=len(u)
    n=np.bincount(inv,minlength=K)[:,None]
    s=np.zeros((K,X.shape[1])); np.add.at(s,inv,X); Xd=X-(s/n)[inv]
    s2=np.zeros((K,1)); np.add.at(s2,inv,yy.reshape(-1,1)); yd=yy-(s2/n)[inv].ravel()
    XtXi=np.linalg.pinv(Xd.T@Xd); b=XtXi@(Xd.T@yd); r=yd-Xd@b
    meat=np.zeros((Xd.shape[1],)*2)
    for c in np.unique(cc):
        sm=np.concatenate([cc,cc])[: len(cc)*0] if False else None
    # cluster on the doubled index
    ccd=np.concatenate([cc[:len(cc)//2*0+len(cc)]]) if False else np.concatenate([cc])
    ccd=np.concatenate([cc])  # cc already doubled length
    for c in np.unique(ccd):
        sel=ccd==c; uu=Xd[sel].T@r[sel]; meat+=np.outer(uu,uu)
    G=len(np.unique(ccd)); nn,kk=Xd.shape
    cov=XtXi@meat@XtXi*(G/max(G-1,1))*((nn-1)/max(nn-kk,1))
    se=np.sqrt(np.diag(cov))
    return -b[0]*1e3,se[0]*1e3,-b[1]*1e3,se[1]*1e3

REPORTED=[('height','y'),('row','y'),('column','x'),('width','x')]
SATURATED=[(n,a) for n in ('height','row','column','width') for a in ('x','y')]
ALONG=[(n,'u') for n in ('height','row','column','width')]
print("specification                                       tau (ms)        placebo (ms)")
def show(tag,cols,keep=None):
    t,ts,p,ps=fit(cols,keep)
    print(f"  {tag:<48} {t:+7.2f}+-{ts:5.2f}   {p:+7.2f}+-{ps:5.2f}")
    return dict(tau=float(t),tau_se=float(ts),pl=float(p),pl_se=float(ps))
R={}
R['none']      =show("per-sequence bias only",[])
R['reported']  =show("reported: h,row on y; col,w on x",REPORTED)
R['saturated'] =show("saturated: all four on BOTH axes",SATURATED)
R['along']     =show("all four projected on the travel direction",ALONG)
R['sat_along'] =show("saturated + all four along travel",SATURATED+ALONG)
print("\ndrop one control at a time from the reported set")
for i in range(len(REPORTED)):
    sub=[c for j,c in enumerate(REPORTED) if j!=i]
    R[f'drop_{REPORTED[i][0]}']=show(f"without {REPORTED[i][0]} on {REPORTED[i][1]}",sub)
print("\nthe saturated set under subsets of the data")
for lab,k in [("IoU >= 0.5",io>=0.5),("IoU >= 0.7",io>=0.7),
              ("|v| >= 5 px/s",V>=5),("|v| >= 15 px/s",V>=15),
              ("box side >= 40 px",size>=40)]:
    R[f'sat_{lab}']=show(f"saturated, {lab}  (n={int(k.sum())})",SATURATED,keep=k)
taus=[v['tau'] for k,v in R.items() if k!='none']
print(f"\nspread of tau across every specification with geometric controls: "
      f"{min(taus):+.2f} to {max(taus):+.2f} ms")
print(f"the influence centroid to be excluded is +24.94 ms; the largest value here is {max(taus):+.2f}")
json.dump(R,open('experiments/e27_rows/saturate.json','w'),indent=1)
print("WROTE experiments/e27_rows/saturate.json")
