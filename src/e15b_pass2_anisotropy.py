"""12-step protocol, pass 2, step 10: change the dimension, 1 -> 2.

Pass 1 compared a scalar |temporal deviation| x speed against an isotropic scalar
noise floor and lost. But a temporal error is not isotropic: it displaces a box
ALONG its own velocity and contributes nothing across it. If a per-object temporal
term is real, the label residuals must be elongated along the motion direction.

That signal does not have to exceed sigma_c. It has to exceed sigma_c/sqrt(N),
because it is a systematic anisotropy while the label noise is (assumed) isotropic.

Residual: fit each track's centre with a local quadratic over a 5-sample window and
take the residual at the centre sample. Project it onto the unit velocity direction
(along) and its perpendicular (cross). Under isotropic noise, Var(along)=Var(cross).
Report R = Var(along)/Var(cross) with a bootstrap interval, and a null obtained by
randomising the direction.
"""
import numpy as np, glob, json
rng=np.random.default_rng(0)
al=[]; cr=[]; spd=[]
for f in sorted(glob.glob('/work/data/dsec_det/*/*/*/object_detections/left/tracks.npy')):
    a=np.load(f)
    for tid in np.unique(a['track_id']):
        s=np.sort(a[a['track_id']==tid],order='t')
        if len(s)<7: continue
        t=s['t'].astype(np.float64)*1e-6
        dt=np.diff(t); h=np.median(dt)
        ok=np.abs(dt-h)<2e-3; idx=np.flatnonzero(~ok)
        b=np.concatenate(([-1],idx,[len(dt)])); g=np.argmax(np.diff(b))
        i0,i1=b[g]+1,b[g+1]+1
        if i1-i0<7: continue
        T=t[i0:i1+1]; X=(s['x']+s['w']/2.0)[i0:i1+1].astype(float); Y=(s['y']+s['h']/2.0)[i0:i1+1].astype(float)
        for k in range(2,len(T)-2):
            w=slice(k-2,k+3)
            tt=T[w]-T[k]
            A=np.vstack([np.ones(5),tt,tt**2]).T
            # leave-one-out: fit on the four neighbours, predict the centre
            m=np.ones(5,bool); m[2]=False
            cX=np.linalg.lstsq(A[m],X[w][m],rcond=None)[0]
            cY=np.linalg.lstsq(A[m],Y[w][m],rcond=None)[0]
            rx=X[k]-cX[0]; ry=Y[k]-cY[0]
            vx,vy=cX[1],cY[1]                    # velocity from the same local fit
            n=np.hypot(vx,vy)
            if n<1e-6: continue
            ux,uy=vx/n,vy/n
            al.append(rx*ux+ry*uy); cr.append(-rx*uy+ry*ux); spd.append(n)
A=np.array(al); C=np.array(cr); V=np.array(spd)
print(f"residuals: {len(A)}   median speed {np.median(V):.1f} px/s")
def stat(A,C):
    return float(A.var(ddof=1)/C.var(ddof=1))
R=stat(A,C)
print(f"\nSTEP-10: anisotropy of label residuals")
print(f"  sd along {A.std(ddof=1):.4f} px   sd cross {C.std(ddof=1):.4f} px")
print(f"  R = Var(along)/Var(cross) = {R:.4f}     (isotropic null: 1.0)")
n=len(A); B=2000; boot=np.empty(B)
for i in range(B):
    j=rng.integers(0,n,n); boot[i]=stat(A[j],C[j])
lo,hi=np.percentile(boot,[2.5,97.5])
print(f"  bootstrap 95% CI [{lo:.4f}, {hi:.4f}]  -> {'EXCLUDES' if lo>1 or hi<1 else 'INCLUDES'} 1.0")
# direction-randomised null: rotate each residual by a random angle
th=rng.uniform(0,2*np.pi,n); rr=np.hypot(A,C)
An=rr*np.cos(th); Cn=rr*np.sin(th)
print(f"  direction-randomised null R = {stat(An,Cn):.4f}")
# stratify by speed
print("\n  by speed decile:")
q=np.percentile(V,[10*i for i in range(11)])
for i in range(10):
    m=(V>=q[i])&(V<q[i+1])
    if m.sum()<500: continue
    print(f"    decile {i+1:>2} v in [{q[i]:6.1f},{q[i+1]:6.1f}) n={m.sum():>6}  R={stat(A[m],C[m]):.4f}")
json.dump(dict(n=n,R=R,ci=[float(lo),float(hi)],R_null=float(stat(An,Cn)),
               sd_along=float(A.std(ddof=1)),sd_cross=float(C.std(ddof=1))),
          open('/work/experiments/e15_protocol/pass2.json','w'),indent=1)
print("WROTE")
