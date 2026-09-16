"""E27 fit - identify the detector's output time from the raw row table (CPU only).

Three estimator defects are corrected here relative to E21/E24.

1. MAGNITUDE -> SIGNED.  E[|eps + tau v|] != E[|eps|] + tau v, so a slope fitted on
   |e| does not identify a temporal offset. Everything below is signed.

2. PROJECTION -> VECTOR.  Projecting onto u = v/|v| uses a direction estimated from
   the same noisy velocity, and then regresses on |v|, a nonlinear function of it.
   The zeroth-order lag model is a linear VECTOR statement,
        p - g  =  -tau * v  +  eps,
   so it is fitted as one stacked regression on the velocity components. tau is then
   identified by construction under the stated model, with no magnitude step.
   The velocity rotated by 90 degrees is entered alongside as a placebo: it has the
   same magnitude and the same noise, and no lag can load on it.

3. FORWARD -> CENTERED DIFFERENCES.  A forward-difference velocity
        v_f = (c_{k+1} - c_k)/dt
   contains the label-centre noise delta_k with weight -1/dt, and the residual
        dx = p_x - c_{k,x}
   contains the same delta_k with weight -1. Their covariance is +var(delta)/dt even
   when the detector has no lag at all. A backward difference contains delta_k with
   the opposite sign and manufactures the opposite artefact. A centered difference
        v_c = (c_{k+1} - c_{k-1}) / (dt_f + dt_b)
   does not use c_k at all and is free of it. Fitting all three is a sign-flip control:
   if the forward and backward estimates straddle the centered one roughly
   symmetrically, the spread is label noise, not detector behaviour.

Standard errors are clustered by sequence. Rows from one sequence share a scene, a
track and an ego-motion, and the paired x/y components of one sample share everything;
treating 4000 such rows as independent is what produced the earlier 8 SE claims.
"""
import os, sys, numpy as np, json

SRC=os.environ.get('ROWS','/work/experiments/e27_rows/rows.npz')
OUTD=os.environ.get('OUTD','/work/experiments/e27_rows')
SIGMA_C=float(os.environ.get('SIGMA_C','0.6515'))   # E28 Gen1 label-centre noise, px per axis
NBOOT=int(os.environ.get('NBOOT','2000'))
Z=np.load(SRC,allow_pickle=True); A=Z['rows']; COLS=list(Z['cols'])
ci={c:i for i,c in enumerate(COLS)}
print(f"rows {A.shape[0]}  sequences {len(np.unique(A[:,ci['seq']]))}")

seq=A[:,ci['seq']]; dx=A[:,ci['dx']]; dy=A[:,ci['dy']]
fx=A[:,ci['fx']]; fy=A[:,ci['fy']]; dtf=A[:,ci['dt_f']]
bx=A[:,ci['bx']]; by=A[:,ci['by']]; dtb=A[:,ci['dt_b']]
gw=A[:,ci['gw']]; gh=A[:,ci['gh']]; io=A[:,ci['iou']]
size=np.sqrt(gw*gh)

def velocities(mode):
    if mode=='fwd':  return fx/dtf, fy/dtf
    if mode=='back': return bx/dtb, by/dtb
    return (fx+bx)/(dtf+dtb), (fy+by)/(dtf+dtb)
# signed acceleration vector, from the two one-sided velocities
ax=(fx/dtf-bx/dtb)/((dtf+dtb)/2); ay=(fy/dtf-by/dtb)/((dtf+dtb)/2)

def cluster_ols(X,y,g):
    """OLS with cluster-robust (sandwich) covariance, clusters given by g."""
    XtXi=np.linalg.inv(X.T@X); beta=XtXi@(X.T@y); r=y-X@beta
    meat=np.zeros((X.shape[1],X.shape[1]))
    for c in np.unique(g):
        m=g==c; u=X[m].T@r[m]; meat+=np.outer(u,u)
    G=len(np.unique(g)); n,k=X.shape
    adj=G/max(G-1,1)*(n-1)/max(n-k,1)
    cov=XtXi@meat@XtXi*adj
    return beta,np.sqrt(np.diag(cov)),cov

def build(mode,use_size,use_acc,keep):
    """Stack the x and y residual components into one regression."""
    vx,vy=velocities(mode)
    m=keep&np.isfinite(vx)&np.isfinite(vy)&np.isfinite(ax)&np.isfinite(ay)
    sp=np.hypot(vx,vy); m&=sp>0
    vx,vy,sp=vx[m],vy[m],sp[m]; ux,uy=vx/sp,vy/sp
    Rx,Ry=dx[m],dy[m]; s=size[m]; g=seq[m]; AX,AY=ax[m],ay[m]
    one=np.ones_like(vx); zero=np.zeros_like(vx)
    cx=[one,zero,vx,-vy]; cy=[zero,one,vy,vx]
    names=['bias_x','bias_y','alpha (v)','placebo (Rv)']
    if use_size: cx.append(s*ux); cy.append(s*uy); names.append('size*u')
    if use_acc:  cx+= [AX,-AY];   cy+= [AY,AX];    names+=['kappa (a)','placebo (Ra)']
    X=np.vstack([np.column_stack(cx),np.column_stack(cy)])
    y=np.concatenate([Rx,Ry]); gg=np.concatenate([g,g])
    return X,y,gg,names,int(m.sum()),sp

def report(tag,mode,use_size,use_acc,keep):
    X,y,g,names,n,sp=build(mode,use_size,use_acc,keep)
    b,se,_=cluster_ols(X,y,g)
    ai=names.index('alpha (v)'); pi=names.index('placebo (Rv)')
    tau=-b[ai]*1e3; tse=se[ai]*1e3
    pl =-b[pi]*1e3; pse=se[pi]*1e3
    print(f"  {tag:<34} n={n:5d} med|v|={np.median(sp):5.1f}  "
          f"tau={tau:+7.2f}+-{tse:5.2f} ms ({abs(tau/max(tse,1e-9)):4.1f}SE)   "
          f"placebo={pl:+7.2f}+-{pse:5.2f} ms ({abs(pl/max(pse,1e-9)):4.1f}SE)")
    return dict(tag=tag,mode=mode,n=n,tau_ms=tau,tau_se_ms=tse,placebo_ms=pl,
                placebo_se_ms=pse,coef={names[i]:[float(b[i]),float(se[i])] for i in range(len(names))})

R={}
base=np.isfinite(dx)
print("\n=== 1. SIGN-FLIP CONTROL: the same fit under three velocity estimators ===")
print("   a forward difference shares the label-centre noise with the residual and")
print("   manufactures a lag; a backward difference manufactures the opposite one.")
for mode in ['fwd','back','centered']:
    R[f'signflip_{mode}']=report(f"velocity = {mode}",mode,False,False,base)

print("\n=== 2. MAIN SPECIFICATION (centered velocity) ===")
R['main']         =report("v only",             'centered',False,False,base)
R['main_size']    =report("v + size*u",         'centered',True, False,base)
R['main_acc']     =report("v + acceleration",   'centered',False,True, base)
R['main_full']    =report("v + size + accel",   'centered',True, True, base)

print("\n=== 3. ROBUSTNESS ===")
for thr in [0.3,0.5,0.7]:
    R[f'iou{thr}']=report(f"match IoU >= {thr}",'centered',True,False,base&(io>=thr))
for floor in [0.0,10.0,15.0,25.0]:
    vx,vy=velocities('centered'); sp=np.hypot(vx,vy)
    R[f'floor{floor}']=report(f"speed floor {floor:.0f} px/s",'centered',True,False,
                              base&np.isfinite(sp)&(np.nan_to_num(sp,nan=-1)>=floor))

print("\n=== 4. CLUSTER BOOTSTRAP over sequences (main + size) ===")
X,y,g,names,n,_=build('centered',True,False,base)
ai=names.index('alpha (v)'); pi=names.index('placebo (Rv)')
uc=np.unique(g); idx={c:np.where(g==c)[0] for c in uc}
rng=np.random.default_rng(0); ts=[]; ps=[]
for _ in range(NBOOT):
    pick=rng.choice(uc,len(uc),replace=True)
    ii=np.concatenate([idx[c] for c in pick])
    try:
        bb=np.linalg.lstsq(X[ii],y[ii],rcond=None)[0]
        ts.append(-bb[ai]*1e3); ps.append(-bb[pi]*1e3)
    except Exception: pass
ts=np.array(ts); ps=np.array(ps)
print(f"  tau     median {np.median(ts):+7.2f} ms   95% CI [{np.percentile(ts,2.5):+.2f}, {np.percentile(ts,97.5):+.2f}]"
      f"   P(tau<=0) = {np.mean(ts<=0):.4f}")
print(f"  placebo median {np.median(ps):+7.2f} ms   95% CI [{np.percentile(ps,2.5):+.2f}, {np.percentile(ps,97.5):+.2f}]"
      f"   P(|placebo|>=|tau|) = {np.mean(np.abs(ps)>=np.abs(ts)):.4f}")
R['bootstrap']=dict(n_boot=int(len(ts)),tau_median=float(np.median(ts)),
                    tau_lo=float(np.percentile(ts,2.5)),tau_hi=float(np.percentile(ts,97.5)),
                    p_tau_le_0=float(np.mean(ts<=0)),
                    placebo_median=float(np.median(ps)),
                    placebo_lo=float(np.percentile(ps,2.5)),placebo_hi=float(np.percentile(ps,97.5)))

print("\n=== 5. ERRORS-IN-VARIABLES ATTENUATION ===")
print(f"   label-centre noise, E28 measured on Gen1: sigma = {SIGMA_C:.4f} px per axis")
vx,vy=velocities('centered')
m=np.isfinite(vx)&np.isfinite(vy)
dsum=(dtf+dtb)[m]
var_noise=np.mean(2*SIGMA_C**2/dsum**2)     # row-wise centered difference of independent centres
var_obs=0.5*(np.var(vx[m])+np.var(vy[m]))
lam=max(var_obs-var_noise,1e-9)/var_obs
print(f"   Var(v_observed) = {var_obs:8.1f} (px/s)^2   Var(v_noise) = {var_noise:8.1f}   "
      f"attenuation lambda = {lam:.3f}")
print(f"   the attenuation biases tau TOWARD zero; the corrected value is tau/lambda")
tm=R['main_size']['tau_ms']; tse=R['main_size']['tau_se_ms']
print(f"   tau = {tm:+.2f} ms  ->  corrected {tm/lam:+.2f} ms (SE {tse/lam:.2f})")
R['eiv']=dict(sigma_c=SIGMA_C,var_obs=float(var_obs),var_noise=float(var_noise),
              lam=float(lam),tau_corrected_ms=float(tm/lam),tau_corrected_se_ms=float(tse/lam))

print("\n=== 6. WHAT THE OLD ESTIMATORS GAVE ON THESE SAME ROWS ===")
vx,vy=velocities('fwd'); sp=np.hypot(vx,vy)
m=np.isfinite(sp)&(sp>=15.0)&np.isfinite(ax)
ux,uy=vx[m]/sp[m],vy[m]/sp[m]
epar=dx[m]*ux+dy[m]*uy; eperp=ux*dy[m]-uy*dx[m]
amag=np.hypot(ax,ay)[m]
X0=np.column_stack([np.ones(m.sum()),sp[m],size[m],amag])
for lab,ya,yc in [("signed  (E21/E24 style)",epar,eperp),
                  ("magnitude (E24 as run)",np.abs(epar),np.abs(eperp))]:
    ba,sa,_=cluster_ols(X0,ya,seq[m]); bc,sc,_=cluster_ols(X0,yc,seq[m])
    d=ba[1]-bc[1]
    print(f"  {lab:<26} along-speed {ba[1]*1e3:+7.2f} ms ({abs(ba[1]/sa[1]):4.1f}SE)  "
          f"cross {bc[1]*1e3:+7.2f} ms ({abs(bc[1]/sc[1]):4.1f}SE)  diff {d*1e3:+7.2f} ms")
print("  (both are shown with sequence-clustered SEs; the earlier runs used OLS SEs)")

os.makedirs(OUTD,exist_ok=True)
json.dump(R,open(os.path.join(OUTD,'fit.json'),'w'),indent=1)
print(f"\nWROTE {OUTD}/fit.json")
