"""E29 - does the forward-difference velocity really manufacture a lag? Simulate it.

The claim to be tested is about the estimator, not about the detector, so it can be
tested without a detector. Generate tracks whose detector has NO lag (tau = 0 exactly),
corrupt the label centres with the noise E28 measured on Gen1 (sigma = 0.6515 px), and
run the same three velocity estimators the real fit uses.

Predicted, if the mechanism is what E27's docstring says:
    forward   v_f = (c_{k+1} - c_k)/dt   shares -delta_k/dt with the residual -delta_k
              -> cov = +var(delta)/dt  -> positive slope -> apparent tau < 0
    backward  shares +delta_k/dt         -> negative slope -> apparent tau > 0
    centered  does not use c_k at all    -> no artefact
and the forward and backward artefacts should be equal and opposite.

A second arm injects a true tau to check the estimator recovers it, and to measure the
errors-in-variables attenuation directly instead of only predicting it.
"""
import numpy as np
SIG=float(__import__('os').environ.get('SIGMA','0.6515'))
DT=0.05; N_TRACK=2000; LEN=14; RNG=np.random.default_rng(7)

def make(tau_true, sigma, n=N_TRACK):
    """A track is a smooth path; the detector reports the position at t - tau_true."""
    cx=[];cy=[];dxs=[];dys=[]
    for _ in range(n):
        v0=RNG.normal(0,30,2); a=RNG.normal(0,40,2)         # px/s, px/s^2
        p0=RNG.uniform(50,250,2)
        t=np.arange(LEN)*DT
        true=p0[None,:]+v0[None,:]*t[:,None]+0.5*a[None,:]*t[:,None]**2
        # the detector reports the true position at t - tau_true, with its own error
        det=(p0[None,:]+v0[None,:]*(t-tau_true)[:,None]
             +0.5*a[None,:]*(t-tau_true)[:,None]**2)+RNG.normal(0,0.3,true.shape)
        lab=true+RNG.normal(0,sigma,true.shape)             # the annotated centres
        cx.append(lab[:,0]); cy.append(lab[:,1])
        dxs.append(det[:,0]-lab[:,0]); dys.append(det[:,1]-lab[:,1])
    return np.array(cx),np.array(cy),np.array(dxs),np.array(dys)

def fit(cx,cy,dx,dy,mode):
    k=np.arange(1,LEN-1)
    if mode=='fwd':   vx=(cx[:,k+1]-cx[:,k])/DT;      vy=(cy[:,k+1]-cy[:,k])/DT
    elif mode=='back':vx=(cx[:,k]-cx[:,k-1])/DT;      vy=(cy[:,k]-cy[:,k-1])/DT
    else:             vx=(cx[:,k+1]-cx[:,k-1])/(2*DT);vy=(cy[:,k+1]-cy[:,k-1])/(2*DT)
    RX=dx[:,k].ravel(); RY=dy[:,k].ravel(); VX=vx.ravel(); VY=vy.ravel()
    one=np.ones_like(VX); zero=np.zeros_like(VX)
    X=np.vstack([np.column_stack([one,zero,VX,-VY]),
                 np.column_stack([zero,one,VY, VX])])
    y=np.concatenate([RX,RY])
    b=np.linalg.lstsq(X,y,rcond=None)[0]
    return -b[2]*1e3, -b[3]*1e3          # tau ms, placebo ms

print(f"synthetic tracks {N_TRACK} x {LEN} labels, dt = {DT*1e3:.0f} ms, "
      f"label noise sigma = {SIG:.4f} px (E28, Gen1)\n")
print("A. NO LAG IN THE DETECTOR (tau_true = 0). Any non-zero output is estimator artefact.")
print("   velocity     tau_hat (ms)   placebo (ms)")
cx,cy,dx,dy=make(0.0,SIG)
res={}
for m in ['fwd','back','centered']:
    t,p=fit(cx,cy,dx,dy,m); res[m]=t
    print(f"   {m:<9}    {t:+8.2f}       {p:+8.2f}")
print(f"   forward + backward = {res['fwd']+res['back']:+.2f} ms  "
      f"(equal and opposite if the mechanism is the shared label-noise term)")
print(f"   analytic prediction for the forward artefact: "
      f"-var(delta)/dt / var(v) ~ {-SIG**2/DT/np.var((cx[:,2:]-cx[:,1:-1])/DT)*1e3:+.2f} ms")

print("\n   the same with NO label noise, to confirm nothing else in the setup leaks:")
cx0,cy0,dx0,dy0=make(0.0,0.0)
for m in ['fwd','back','centered']:
    t,p=fit(cx0,cy0,dx0,dy0,m); print(f"   {m:<9}    {t:+8.2f}       {p:+8.2f}")

print("\nB. RECOVERY AND ATTENUATION. A true lag is injected; centered velocity is used.")
print("   tau_true (ms)   tau_hat (ms)   ratio (attenuation)")
for tt in [0.010,0.025,0.050]:
    cx,cy,dx,dy=make(tt,SIG)
    t,p=fit(cx,cy,dx,dy,'centered')
    print(f"   {tt*1e3:+8.1f}       {t:+8.2f}       {t/(tt*1e3):.3f}")
vx=(cx[:,2:]-cx[:,:-2])/(2*DT)
lam=1-(2*SIG**2/(2*DT)**2)/np.var(vx)
print(f"   predicted attenuation lambda = 1 - Var(noise)/Var(observed) = {lam:.3f}")
print("\n   and with no label noise, recovery should be exact:")
for tt in [0.025]:
    cx,cy,dx,dy=make(tt,0.0); t,p=fit(cx,cy,dx,dy,'centered')
    print(f"   {tt*1e3:+8.1f}       {t:+8.2f}       {t/(tt*1e3):.3f}")
