import numpy as np
np.set_printoptions(precision=4, suppress=True)

print("="*70); print("A. MASKED-FROZEN vs RETRAINED effective timestamp tau(w)")
print("="*70)
c = np.array([-50 + 5*(k+0.5) for k in range(10)])   # bin centres, k=0 oldest
def fit_a(idx, lam):
    X = np.stack([np.ones(len(idx)), c[idx]], 1)
    D = np.diag([0.0, 1.0])
    M = np.linalg.inv(X.T@X + lam*D) @ X.T
    return M[0]                      # weights a_k s.t. phat0 = sum a_k m_k
Scc = ((c-c.mean())**2).sum()
print(f"S_cc(full 10 bins) = {Scc}")
for gam in [0.0, 0.5, 0.9, 0.99]:
    lam = np.inf if gam==0 else Scc*(1-gam)/gam
    lam = 1e12 if gam==0 else lam
    a_full = fit_a(np.arange(10), lam)
    print(f"\n-- extrapolation strength gamma_full={gam}  (lam={lam:.3g})")
    print(f"   full-window weights a_k = {a_full}")
    print(f"   {'w(ms)':>6} {'tau_retrain':>12} {'tau_mask(norm)':>15} {'gain A_j':>9}")
    rows=[]
    for j in [0,2,4,6,8,9]:
        S = np.arange(j,10); w = 5*(10-j)
        a_r = fit_a(S, np.inf if gam==0 else Scc*(1-gam)/gam if len(S)>1 else 1e12)
        if len(S)==1: a_r = np.array([1.0])
        tau_r = float(a_r@c[S])
        A = a_full[S].sum(); C = (a_full[S]*c[S]).sum()
        tau_m = C/A
        rows.append((w,tau_r,tau_m,A))
        print(f"   {w:6d} {tau_r:12.3f} {tau_m:15.3f} {A:9.3f}")
    rows=np.array(rows)
    sr = np.polyfit(rows[:,0], rows[:,1],1)[0]; sm = np.polyfit(rows[:,0], rows[:,2],1)[0]
    print(f"   slope d(tau)/d(w):  retrain={sr:+.4f}   mask={sm:+.4f}   (paper pre-registers |slope| in [0.3,0.7])")

print()
print("="*70); print("B. Does the distance-minimising tangential shift raise IoU?")
print("="*70)
def iou_axis(dx,dy,w,h):
    ix = max(0.0, w-abs(dx)); iy = max(0.0, h-abs(dy))
    inter = ix*iy; return inter/(2*w*h-inter)
# hand counterexample: tall thin box (pedestrian-like), error is vertical, tangent diagonal
w,h = 20.,60.
e = np.array([0.,8.]); u = np.array([1.,1.])/np.sqrt(2)
ep = e - (e@u)*u
print(f"box {w}x{h}, e={e}, u={u}")
print(f"  |e|={np.linalg.norm(e):.3f} -> |e_perp|={np.linalg.norm(ep):.3f}   (distance strictly reduced)")
print(f"  IoU(e)={iou_axis(*e,w,h):.4f}  ->  IoU(e_perp)={iou_axis(*ep,w,h):.4f}")
rng = np.random.default_rng(0)
for ar,(bw,bh) in [("1:3 pedestrian",(20.,60.)),("2:1 vehicle",(60.,30.)),("1:1",(40.,40.))]:
    n=200000
    th = rng.uniform(0,2*np.pi,n); r = rng.uniform(0,0.35*min(bw,bh),n)
    ex,ey = r*np.cos(th), r*np.sin(th)
    ph = rng.uniform(0,2*np.pi,n); ux,uy = np.cos(ph), np.sin(ph)
    dot = ex*ux+ey*uy; px_,py_ = ex-dot*ux, ey-dot*uy
    i0 = np.maximum(0,bw-np.abs(ex))*np.maximum(0,bh-np.abs(ey))
    i1 = np.maximum(0,bw-np.abs(px_))*np.maximum(0,bh-np.abs(py_))
    iou0 = i0/(2*bw*bh-i0); iou1 = i1/(2*bw*bh-i1)
    print(f"  {ar:16s} P(IoU decreases after distance-minimising tangential shift) = {(iou1<iou0-1e-12).mean()*100:5.2f} %")
print("  (0 is always in the feasible set, so an IoU-MAXIMISING relaxation can never decrease IoU.)")

print()
print("C. Greedy (COCO) matching is not monotone in IoU:")
print("   det A (score .9): IoU(GT1)=0.70 IoU(GT2)=0.60 ; det B (score .5): IoU(GT2)=0.55, thr=0.5")
print("   greedy -> A:GT1, B:GT2  => 2 TP")
print("   raise A's IoU(GT2) 0.60 -> 0.80 (a strict improvement):")
print("   greedy -> A:GT2 (0.80 is A's max), B unmatched => 1 TP.  AP DECREASES.")

print()
print("="*70); print("D. The IV: is a 'disjoint earlier label pair' disjoint?")
print("="*70)
print("X = central diff over +-Delta uses labels {t-D, t+D};  Z = (t-2D,t-D) pair uses {t-2D, t-D}")
print("shared label at t-D  =>  Cov(eta_X, eta_Z) != 0.")
D=50.; sc=1.0; n=4_000_000
rng=np.random.default_rng(1)
e_m2,e_m1,e_p1 = rng.normal(0,sc,(3,n))
etaX = (e_p1-e_m1)/(2*D); etaZ=(e_m1-e_m2)/D
print(f"  analytic Var(etaX)=sc^2/(2D^2)={sc**2/(2*D*D):.3e}  MC={etaX.var():.3e}")
print(f"  analytic Cov      =-sc^2/(2D^2)={-sc**2/(2*D*D):.3e}  MC={np.cov(etaX,etaZ)[0,1]:.3e}")
print(f"  analytic corr = -1/2                                MC={np.corrcoef(etaX,etaZ)[0,1]:+.4f}")
print("  plim beta_IV = tau * Var(v) / (Var(v) + Cov(etaX,etaZ))  -> INFLATED (denominator shrinks)")
for sc_ in [1.0,2.0,3.0]:
    cov = -sc_**2/(2*D*D); varv=(0.06)**2
    latt = varv/(varv+sc_**2/(2*D*D))
    print(f"   sigma_c={sc_} px, Var(v)=(0.06 px/ms)^2 :  lambda_att={latt:.3f} (naive shrinks {100*(1-latt):.0f}%)"
          f"   shared-anchor IV inflation = {varv/(varv+cov):.3f}x")

print()
print("="*70); print("E. Smoothing bias of a central difference")
print("="*70)
for name,p,dp in [("const accel  p=t^2", lambda t:t**2, lambda t:2*t),
                  ("const jerk   p=t^3", lambda t:t**3, lambda t:3*t**2)]:
    for Dl in [50.,250.]:
        t=0.3
        cd=(p(t+Dl)-p(t-Dl))/(2*Dl); tru=dp(t)
        print(f"  {name}, Delta={Dl:5.0f}: central diff={cd:.6g}  v(t)={tru:.6g}  error={cd-tru:.6g}"
              f"   (predicted Delta^2/6 * p''' = {Dl**2/6*(6 if 't^3' in name else 0):.6g})")
print("  => central difference is EXACT under constant acceleration; leading error is (Delta^2/6)*jerk,")
print("     NOT a term 'correlated with acceleration'.")

print()
print("="*70); print("F. w_P: the paper's own 2-sigma definition vs the 50 ms it uses")
print("="*70)
W=50.
print(f"  uniform kernel, full width {W} ms: sigma={W/np.sqrt(12):.2f} ms -> w_P = 2*sigma = {2*W/np.sqrt(12):.2f} ms (not 50)")
print(f"  triangular kernel half-width 50 ms: sigma={50/np.sqrt(6):.2f} ms -> w_G = {2*50/np.sqrt(6):.2f} ms (not 50)")
print(f"  tau_max with 'full width' reading  = (50+50)/2 = 50.00 ms")
print(f"  tau_max with the paper's OWN 2-sigma reading = ({2*50/np.sqrt(6):.2f}+{2*W/np.sqrt(12):.2f})/2 = {(2*50/np.sqrt(6)+2*W/np.sqrt(12))/2:.2f} ms  ({100*(1-(2*50/np.sqrt(6)+2*W/np.sqrt(12))/2/50):.0f}% smaller)")

print()
print("="*70); print("G. AP^sync: when does re-anchoring by -tau_hat*v_pred make things WORSE?")
print("="*70)
print("  E[Delta(e^2)] = -2*that*tau*E||v||^2 + that^2*(E||v||^2 + E||nu||^2)")
print("  minimiser   that* = tau * S/(S+N),  S=E||v||^2, N=E||nu||^2   (ATTENUATED)")
print("  break-even that = tau  <=>  N = S, i.e. SNR = 1.  N > S => applying that=tau raises MSE.")
for snr in [4.,2.,1.,0.5]:
    S=1.; N=S/snr
    for lab,that in [("tau_naive (0.7 tau)",0.7),("tau_IV (tau)",1.0)]:
        d = -2*that*S + that**2*(S+N)
        print(f"   SNR=S/N={snr:4.1f}  {lab:20s}: E[Delta(e^2)]/tau^2 = {d:+.3f}  {'WORSE' if d>0 else 'better'}")

print()
print("="*70); print("H. sigma_tau is the dispersion of a RATIO estimator")
print("="*70)
rng=np.random.default_rng(3); n=400000
v = rng.lognormal(np.log(0.06),0.8,n)            # px/ms
tau=-25.; se=1.5                                  # px along-track noise
epar = tau*v + rng.normal(0,se,n)
for vmin in [0.005,0.01,0.02,0.04,0.08]:
    m = v>vmin
    d = epar[m]/v[m]
    print(f"   filter ||v||>{vmin:.3f} px/ms : kept {100*m.mean():5.1f}%  sd(delta_hat)={np.std(d):8.1f} ms  MAD-sd={1.4826*np.median(np.abs(d-np.median(d))):7.2f} ms")
print("   sd(delta_hat) is unbounded as the filter loosens; the population variance does not exist")
print("   when v_hat has mass near 0 (ratio of two noisy quantities -> Cauchy-like tails).")

print()
print("="*70); print("I. Is min(w_P^decl, w_P^meas) ever binding?")
print("="*70)
ks=[1,2,4,8,16,32]
print(f"  E1c grid k in {ks} (+inf), one sequence step = 50 ms -> w_P^meas in {[50*k for k in ks]} ms (+inf)")
print("  w_P^decl = 50 ms.  min(50, >=50) = 50 ALWAYS.  The 'conservative' min can never bind.")
