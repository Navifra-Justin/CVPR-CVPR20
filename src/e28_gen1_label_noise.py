"""E28 - the label-centre noise of Gen1, measured on Gen1.

E13 solved for the label noise of DSEC-Det and got sigma = 0.4974 px. The E27 output-time
fit runs on Gen1, and an errors-in-variables correction there needs Gen1's own number:
importing DSEC-Det's would be an unchecked assumption about a different annotation effort
on a different sensor.

Same construction as E13. For a track centre series x_i = f(t_i) + e_i on a uniform grid,
    Var(D_k) = C(2k,k) * sigma^2 + (motion term of order k),
so Var(D_k)/C(2k,k) falls toward sigma^2 from above as the motion term dies. Halving the
sample rate multiplies the motion term by 4^k and leaves sigma^2 alone, giving a second
equation:  sigma^2 = (4^k Var_full - Var_half) / (4^k - 1).

Tracks are rebuilt by the same greedy same-class IoU linking E27 uses, so the two
experiments share one definition of a track.
"""
import glob, os, numpy as np
from math import comb

ROOT=os.environ.get('ROOT','data/gen1x/gen1/val')
MINLEN=int(os.environ.get('MINLEN','12'))
LINK_IOU=0.3

def iou1(a,B):
    x1=np.maximum(a[0],B[:,0]); y1=np.maximum(a[1],B[:,1])
    x2=np.minimum(a[2],B[:,2]); y2=np.minimum(a[3],B[:,3])
    w=np.clip(x2-x1,0,None); h=np.clip(y2-y1,0,None); it=w*h
    return it/np.maximum((a[2]-a[0])*(a[3]-a[1])+(B[:,2]-B[:,0])*(B[:,3]-B[:,1])-it,1e-9)

series=[]      # each entry: (cx array, cy array) on a uniform label grid
nfrac=0; ntot=0
for sd in sorted(glob.glob(os.path.join(ROOT,'*'))):
    p=os.path.join(sd,'labels_v2','labels.npz')
    if not os.path.exists(p): continue
    L=np.load(p)['labels']
    ts=np.sort(np.unique(L['t']))
    if len(ts)<MINLEN: continue
    B=[];C=[];CL=[]
    for t in ts:
        G=L[L['t']==t]
        bb=np.column_stack([G['x'],G['y'],G['x']+G['w'],G['y']+G['h']]).astype(float)
        B.append(bb); C.append(np.column_stack([(bb[:,0]+bb[:,2])/2,(bb[:,1]+bb[:,3])/2]))
        CL.append(np.asarray(G['class_id']))
        ntot+=G['x'].size*4
        nfrac+=int(np.sum(np.asarray(G['x'],dtype=float)%1!=0)+np.sum(np.asarray(G['y'],dtype=float)%1!=0)
                  +np.sum(np.asarray(G['w'],dtype=float)%1!=0)+np.sum(np.asarray(G['h'],dtype=float)%1!=0))
    # link forward, then walk chains
    fwd=[]
    for k in range(len(ts)-1):
        m=-np.ones(len(B[k]),dtype=int)
        for i in range(len(B[k])):
            same=(CL[k][i]==CL[k+1])
            if not same.any(): continue
            io=np.where(same,iou1(B[k][i],B[k+1]),0.0); j=int(np.argmax(io))
            if io[j]>=LINK_IOU: m[i]=j
        fwd.append(m)
    used=[np.zeros(len(B[k]),dtype=bool) for k in range(len(ts))]
    dts=np.diff(ts)
    for k in range(len(ts)-1):
        for i in range(len(B[k])):
            if used[k][i]: continue
            ks=[k]; idxs=[i]; kk,ii=k,i
            while kk<len(ts)-1 and fwd[kk][ii]>=0:
                jj=fwd[kk][ii]; kk+=1; ii=jj; ks.append(kk); idxs.append(ii); used[kk][ii]=True
            if len(ks)<MINLEN: continue
            d=np.diff(ts[ks])
            if len(np.unique(d))!=1: continue      # uniform grid only
            series.append((np.array([C[a][b][0] for a,b in zip(ks,idxs)]),
                           np.array([C[a][b][1] for a,b in zip(ks,idxs)])))
print(f"tracks of length >= {MINLEN} on a uniform grid: {len(series)}")
print(f"fractional label coordinates: {nfrac}/{ntot}  -> Gen1 stores integers: {nfrac==0}")

def trimmed_var(v,frac=0.05):
    v=np.sort(v); n=len(v); a=int(n*frac); b=n-a
    if b-a<8: return np.var(v)
    return np.var(v[a:b])

def ladder(step):
    out={}
    for k in range(1,8):
        acc=[]
        for cx,cy in series:
            for c in (cx,cy):
                s=c[::step]
                if len(s)<k+2: continue
                d=s.copy()
                for _ in range(k): d=np.diff(d)
                acc.append(d)
        if not acc: continue
        d=np.concatenate(acc)
        out[k]=trimmed_var(d)/comb(2*k,k)
    return out
full=ladder(1); half=ladder(2)
print("\n k  C(2k,k)   Var/C full   sigma_full   Var/C half   two-rate sigma")
rows=[]
for k in sorted(full):
    sf=np.sqrt(full[k]); s2=None
    if k in half:
        num=4**k*full[k]-half[k]; s2=num/(4**k-1)
    st=np.sqrt(max(s2,0)) if s2 is not None else float('nan')
    print(f" {k}  {comb(2*k,k):6d}   {full[k]:10.5f}   {sf:10.4f}   "
          f"{half.get(k,float('nan')):10.5f}   {st:10.4f}")
    rows.append((k,full[k],sf,half.get(k,np.nan),st))
sig=[r[2] for r in rows]
d=np.diff(sig)
if len(d)>=3 and all(x<0 for x in d[-3:]):
    r=np.mean([d[-1]/d[-2],d[-2]/d[-3]])
    lim=sig[-1]+d[-1]*r/(1-r) if 0<r<1 else sig[-1]
else:
    lim=sig[-1]
q2=0.25/12    # integer corners -> centres on a 0.5 px lattice
print(f"\nsigma_total  -> {lim:.4f} px")
print(f"quantization  q^2/12 = {q2:.5f} px^2  (0.5 px lattice) -> {np.sqrt(q2):.4f} px")
print(f"sigma_annotation = {np.sqrt(max(lim**2-q2,0)):.4f} px")
import json; os.makedirs('experiments/e28_gen1_label_noise',exist_ok=True)
json.dump(dict(n_tracks=len(series),sigma_total=float(lim),
               sigma_annotation=float(np.sqrt(max(lim**2-q2,0))),
               ladder=[[int(a),float(b),float(c),float(dd),float(e)] for a,b,c,dd,e in rows]),
          open('experiments/e28_gen1_label_noise/result.json','w'),indent=1)
print("WROTE experiments/e28_gen1_label_noise/result.json")
