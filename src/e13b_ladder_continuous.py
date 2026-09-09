"""E13b - the same ladder with a continuous estimator, and the quantization term removed.

Two corrections to E13:
  (1) DSEC-Det stores x,y,w,h as INTEGERS, so box centres sit on a 0.5 px lattice.
      A MAD-based variance locks onto discrete values (full and half rate returned
      bit-identical sigmas at k=2,3). Use a trimmed empirical variance instead,
      which moves continuously with the data.
  (2) Uniform quantization with step q contributes q^2/12 to the variance of every
      position independently, hence the SAME q^2/12 * c_k to Var(D_k). Subtract it:
          s_annot^2 = Var(D_k)/c_k - q^2/12
      This is a computable quantity, not an assumption.
"""
import numpy as np, glob, json
from math import comb
Q = 0.5
QVAR = Q*Q/12.0

def diffs(x,k):
    for _ in range(k): x=np.diff(x)
    return x
def tvar(z, p=1.0):                      # trimmed empirical variance, continuous in the data
    lo,hi = np.percentile(z,[p,100-p])
    zz = z[(z>=lo)&(z<=hi)]
    return float(zz.var(ddof=1))

segs=[]
for f in sorted(glob.glob('/work/data/dsec_det/*/*/*/object_detections/left/tracks.npy')):
    a=np.load(f)
    for tid in np.unique(a['track_id']):
        s=np.sort(a[a['track_id']==tid],order='t')
        if len(s)<10: continue
        t=s['t'].astype(np.float64)*1e-6; dt=np.diff(t); h=np.median(dt)
        ok=np.abs(dt-h)<2e-3; idx=np.flatnonzero(~ok)
        b=np.concatenate(([-1],idx,[len(dt)])); g=np.argmax(np.diff(b))
        i0,i1=b[g]+1,b[g+1]+1
        if i1-i0<10: continue
        segs.append(((s['x']+s['w']/2.0)[i0:i1+1].astype(np.float64),
                     (s['y']+s['h']/2.0)[i0:i1+1].astype(np.float64)))
print("segments",len(segs),flush=True)

def ladder(get,label):
    print(f"\n{label}")
    print("   k    c_k       n     Var(D_k)/c_k   sigma_total   sigma_annot (quant removed)")
    out={}
    for k in range(1,8):
        pool=[]
        for X,Y in segs:
            for z in (get(X),get(Y)):
                if len(z)>k+1: pool.append(diffs(z,k))
        if not pool: break
        z=np.concatenate(pool); ck=comb(2*k,k)
        v=tvar(z)/ck
        st=np.sqrt(v); sa=np.sqrt(max(v-QVAR,0.0))
        print(f"  {k:>2}  {ck:>6}  {len(z):>8}    {v:.5f}      {st:.4f}        {sa:.4f}")
        out[k]=dict(var=v, sigma_total=float(st), sigma_annot=float(sa))
    return out
full=ladder(lambda a:a,"FULL RATE 20 Hz")
half=ladder(lambda a:a[::2],"HALVED RATE 10 Hz (motion term x 2^{2k}, noise unchanged)")
print(f"\nquantization step q = {Q} px  ->  q^2/12 = {QVAR:.5f} px^2  ->  sigma_quant = {np.sqrt(QVAR):.4f} px")
print("\nCONVERGENCE (sigma_total): k  full   half   half/full")
for k in sorted(set(full)&set(half)):
    print(f"   {k}  {full[k]['sigma_total']:.4f}  {half[k]['sigma_total']:.4f}  {half[k]['sigma_total']/full[k]['sigma_total']:.3f}")
json.dump(dict(q=Q,qvar=QVAR,full=full,half=half),
          open('/work/experiments/e13_difference_ladder/continuous.json','w'),indent=1)
print("WROTE",flush=True)
