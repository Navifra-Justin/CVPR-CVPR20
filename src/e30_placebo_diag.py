"""E30 - what is the rotated-velocity coefficient, and does it break the lag estimate?

E27's fit carries a placebo: the label velocity rotated a quarter turn. No temporal offset
can load on it, and in the synthetic calibration (E29) it sits at 0.02 ms. On the real
rows it is -7.75 ms at 4.0 standard errors, within a factor of two of the lag it is meant
to bound. Either the residual really contains a component perpendicular to travel and
proportional to speed, or the model is missing a regressor that term is standing in for.

Driving scenes make one alias obvious. Most label motion is horizontal, so R90 v maps a
horizontal speed onto a VERTICAL residual. Oncoming and same-direction traffic move in
opposite horizontal directions, sit on opposite sides of the image and are seen at
different scales, so any vertical bias that differs between the two sides appears as a
coefficient on R90 v without anything rotational being present.

The tests, in order of what they would rule out:
  1. split by the sign of v_x - a real rotational term keeps its sign, an alias flips
  2. split by image side - an alias is carried by position, a rotational term is not
  3. enter box height along the image y axis, and image row, as competing regressors
  4. per-sequence constant vectors, which absorb any scene-level bias
  5. what tau survives each of those
"""
import os, numpy as np, json
Z=np.load(os.environ.get('ROWS','experiments/e27_rows/rows.npz'),allow_pickle=True)
A=Z['rows']; COLS=list(Z['cols']); ci={c:i for i,c in enumerate(COLS)}
seq=A[:,ci['seq']]; dx=A[:,ci['dx']]; dy=A[:,ci['dy']]
fx=A[:,ci['fx']]; fy=A[:,ci['fy']]; dtf=A[:,ci['dt_f']]
bx=A[:,ci['bx']]; by=A[:,ci['by']]; dtb=A[:,ci['dt_b']]
gw=A[:,ci['gw']]; gh=A[:,ci['gh']]; io=A[:,ci['iou']]
gcx=A[:,ci['gcx']]; gcy=A[:,ci['gcy']]; cls=A[:,ci['cls']]
size=np.sqrt(gw*gh)
vx=(fx+bx)/(dtf+dtb); vy=(fy+by)/(dtf+dtb)
ok=np.isfinite(vx)&np.isfinite(vy)&(np.hypot(vx,vy)>0)

def cluster_ols(X,y,g):
    XtXi=np.linalg.inv(X.T@X); b=XtXi@(X.T@y); r=y-X@b
    meat=np.zeros((X.shape[1],)*2)
    for c in np.unique(g):
        m=g==c; u=X[m].T@r[m]; meat+=np.outer(u,u)
    G=len(np.unique(g)); n,k=X.shape
    cov=XtXi@meat@XtXi*(G/max(G-1,1))*((n-1)/max(n-k,1))
    return b,np.sqrt(np.diag(cov))

def fit(mask,extra=(),perseq=False,label=""):
    m=ok&mask
    if m.sum()<200: print(f"  {label:<40} n={m.sum()} too few"); return None
    V=np.hypot(vx[m],vy[m]); ux,uy=vx[m]/V,vy[m]/V
    one=np.ones(m.sum()); zero=np.zeros(m.sum())
    cx=[vx[m],-vy[m],size[m]*ux]; cy=[vy[m],vx[m],size[m]*uy]
    names=['alpha','placebo','size*u']
    for nm in extra:
        if nm=='h_y':   cx.append(zero);      cy.append(gh[m]);        names.append('h*yhat')
        if nm=='row_y': cx.append(zero);      cy.append(gcy[m]);       names.append('row*yhat')
        if nm=='col_x': cx.append(gcx[m]);    cy.append(zero);         names.append('col*xhat')
        if nm=='w_x':   cx.append(gw[m]);     cy.append(zero);         names.append('w*xhat')
    if perseq:
        u=np.unique(seq[m]); D=(seq[m][:,None]==u[None,:]).astype(float)
        Cx=np.hstack([np.column_stack(cx),D,np.zeros_like(D)])
        Cy=np.hstack([np.column_stack(cy),np.zeros_like(D),D])
        X=np.vstack([Cx,Cy])
    else:
        X=np.vstack([np.column_stack([one,zero]+cx),np.column_stack([zero,one]+cy)])
        names=['bias_x','bias_y']+names
    y=np.concatenate([dx[m],dy[m]]); g=np.concatenate([seq[m]]*2)
    b,se=cluster_ols(X,y,g)
    ai=names.index('alpha'); pi=names.index('placebo')
    print(f"  {label:<40} n={m.sum():6d}  tau={-b[ai]*1e3:+7.2f}+-{se[ai]*1e3:5.2f} "
          f"({abs(b[ai]/se[ai]):4.1f}SE)   placebo={-b[pi]*1e3:+7.2f}+-{se[pi]*1e3:5.2f} "
          f"({abs(b[pi]/se[pi]):4.1f}SE)")
    return dict(n=int(m.sum()),tau=float(-b[ai]*1e3),tau_se=float(se[ai]*1e3),
                pl=float(-b[pi]*1e3),pl_se=float(se[pi]*1e3))

R={}
print("\n=== 0. baseline (E27 main + size) ===")
R['base']=fit(np.ones_like(ok,bool),label="all rows")

print("\n=== 1. split by the sign of the horizontal velocity ===")
print("   a rotational term keeps its sign under this split; a vertical-bias alias flips it")
R['vx_pos']=fit(vx>0, label="v_x > 0 (moving right)")
R['vx_neg']=fit(vx<0, label="v_x < 0 (moving left)")

print("\n=== 2. split by image side ===")
mid=np.median(gcx[ok])
R['left'] =fit(gcx<mid, label=f"box centre left of {mid:.0f} px")
R['right']=fit(gcx>=mid,label=f"box centre right of {mid:.0f} px")

print("\n=== 3. does a vertical geometric regressor absorb it? ===")
R['h_y']   =fit(np.ones_like(ok,bool),extra=('h_y',),      label="+ box height along yhat")
R['row_y'] =fit(np.ones_like(ok,bool),extra=('row_y',),    label="+ image row along yhat")
R['both']  =fit(np.ones_like(ok,bool),extra=('h_y','row_y'),label="+ height and row along yhat")
R['four']  =fit(np.ones_like(ok,bool),extra=('h_y','row_y','col_x','w_x'),
                label="+ height, row, column, width")

print("\n=== 4. a constant vector per sequence ===")
R['perseq']=fit(np.ones_like(ok,bool),perseq=True,label="per-sequence bias vectors")
R['perseq4']=fit(np.ones_like(ok,bool),extra=('h_y','row_y','col_x','w_x'),perseq=True,
                 label="per-sequence bias + four geometric")

print("\n=== 5. by class ===")
for c in np.unique(cls[ok]):
    R[f'cls{int(c)}']=fit(cls==c,label=f"class {int(c)}")

print("\n=== 6. the same, restricted to objects that actually move ===")
V=np.hypot(vx,vy)
for f in [5.,10.,15.,20.]:
    R[f'move{f:.0f}']=fit(np.nan_to_num(V,nan=-1)>=f,extra=('h_y','row_y','col_x','w_x'),
                          perseq=True,label=f"|v| >= {f:.0f} px/s, full controls")

print("\n=== 7. detection floor: what lag would this sample have shown? ===")
b=R['perseq4']
print(f"   with all controls, tau = {b['tau']:+.2f} +- {b['tau_se']:.2f} ms")
print(f"   two-sided 95% exclusion: |tau| > {2*b['tau_se']:.1f} ms is ruled out")
print(f"   the influence centroid to be compared against is 23.81 ms (E45)")
json.dump(R,open('experiments/e27_rows/placebo_diag.json','w'),indent=1)
print("\nWROTE experiments/e27_rows/placebo_diag.json")
