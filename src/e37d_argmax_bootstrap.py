"""E37d - does the mAP sweep's argmax carry an interval?

Sec. 3.6 reports the maximum of mAP(delta) at -10 ms and, after an audit, says it is
reported for its sign and not for its value because the top is flat to 0.06 points. That
sentence is defensible but it is an assertion about a quantity with no measured spread.
This measures the spread.

Per-frame contributions are precomputed once for each delta on the grid, so a bootstrap
replicate is a resampling of frames and a re-accumulation of precision-recall rather than a
re-evaluation of the sweep. 1000 replicates over frames.

If the argmax distribution covers the whole grid, the honest report is the curve and its
flatness; if it concentrates, the argmax is a second estimator and can be quoted with an
interval.
"""
import numpy as np, json, os
Z=np.load('experiments/e37_map/dets.npz')
DET=Z['det'].astype(np.float64); GT=Z['gt'].astype(np.float64)
hasv=np.isfinite(GT[:,6])&np.isfinite(GT[:,7])
NF=int(max(DET[:,0].max(),GT[:,0].max()))+1
det_by=[[] for _ in range(NF)]
for r in DET: det_by[int(r[0])].append(r)
gt_by=[[] for _ in range(NF)]
for i,r in enumerate(GT): gt_by[int(r[0])].append((r,bool(hasv[i])))
CLASSES=sorted(set(GT[:,5].astype(int)))
THRS=np.arange(0.5,0.96,0.05)
DELTAS=np.round(np.arange(-0.050,0.0301,0.005),4)
NB=int(os.environ.get('NBOOT','1000'))

def iou_mat(D,G):
    if len(D)==0 or len(G)==0: return np.zeros((len(D),len(G)))
    x1=np.maximum(D[:,None,0],G[None,:,0]); y1=np.maximum(D[:,None,1],G[None,:,1])
    x2=np.minimum(D[:,None,2],G[None,:,2]); y2=np.minimum(D[:,None,3],G[None,:,3])
    w=np.clip(x2-x1,0,None); h=np.clip(y2-y1,0,None); it=w*h
    ad=((D[:,2]-D[:,0])*(D[:,3]-D[:,1]))[:,None]
    ag=((G[:,2]-G[:,0])*(G[:,3]-G[:,1]))[None,:]
    return it/np.maximum(ad+ag-it,1e-9)

# per (delta, class, frame): scores, tp flags at each IoU threshold, and npos
print(f"precomputing {len(DELTAS)} deltas x {len(CLASSES)} classes over {NF} frames",flush=True)
PRE={}
for di,dl in enumerate(DELTAS):
    for c in CLASSES:
        sc=[]; fl=[]; npos=[]
        for fi in range(NF):
            G=[]; ign=[]
            for r,hv in gt_by[fi]:
                if int(r[5])!=c: continue
                b=r[1:5].copy()
                if hv:
                    b[0]+=dl*r[6]; b[2]+=dl*r[6]; b[1]+=dl*r[7]; b[3]+=dl*r[7]
                G.append(b); ign.append(not hv)
            G=np.array(G).reshape(-1,4); ign=np.array(ign,dtype=bool)
            npos.append(int((~ign).sum()))
            D=[r for r in det_by[fi] if int(r[6])==c]
            if not len(D): sc.append(np.zeros(0)); fl.append(np.zeros((len(THRS),0))); continue
            D=np.array(D); D=D[np.argsort(-D[:,5])]
            M=iou_mat(D[:,1:5],G); sc.append(D[:,5].copy())
            f=np.zeros((len(THRS),len(D)))
            for ti,t in enumerate(THRS):
                used=np.zeros(len(G),dtype=bool)
                for dj in range(len(D)):
                    j=-1; best=t
                    for gj in range(len(G)):
                        if used[gj] or M[dj,gj]<best: continue
                        best=M[dj,gj]; j=gj
                    if j>=0:
                        used[j]=True; f[ti,dj]= -1.0 if ign[j] else 1.0
            fl.append(f)
        PRE[(di,c)]=(sc,fl,np.array(npos))
    print(f"  delta {dl*1e3:+.0f} ms done",flush=True)

def mAP(di,frames):
    out=[]
    for c in CLASSES:
        sc,fl,npos=PRE[(di,c)]
        S=np.concatenate([sc[f] for f in frames]) if len(frames) else np.zeros(0)
        if not len(S): continue
        F=np.concatenate([fl[f] for f in frames],axis=1)
        n=int(npos[frames].sum())
        if n==0: continue
        o=np.argsort(-S); aps=[]
        for ti in range(len(THRS)):
            f=F[ti][o]; f=f[f>=0]
            ctp=np.cumsum(f==1); cfp=np.cumsum(f==0)
            rec=ctp/n; prec=ctp/np.maximum(ctp+cfp,1e-9)
            mp=np.concatenate([[0],prec,[0]]); mr=np.concatenate([[0],rec,[1]])
            for i in range(len(mp)-2,-1,-1): mp[i]=max(mp[i],mp[i+1])
            idx=np.where(mr[1:]!=mr[:-1])[0]
            aps.append(float(((mr[idx+1]-mr[idx])*mp[idx+1]).sum()))
        out.append(float(np.mean(aps)))
    return float(np.mean(out)) if out else float('nan')

allf=np.arange(NF)
point=np.array([mAP(di,allf) for di in range(len(DELTAS))])
print("\n point estimate")
print("  delta(ms) "+" ".join(f"{d*1e3:+6.0f}" for d in DELTAS))
print("  mAP       "+" ".join(f"{v:6.4f}" for v in point))
print(f"  argmax {DELTAS[int(np.argmax(point))]*1e3:+.0f} ms")

rng=np.random.default_rng(0); arg=[]
for b in range(NB):
    fr=rng.integers(0,NF,NF)
    curve=np.array([mAP(di,fr) for di in range(len(DELTAS))])
    arg.append(DELTAS[int(np.nanargmax(curve))]*1e3)
    if (b+1)%200==0: print(f"  bootstrap {b+1}/{NB}",flush=True)
arg=np.array(arg)
print(f"\n argmax over {NB} frame-resamples")
vals,cts=np.unique(arg,return_counts=True)
for v,c in zip(vals,cts): print(f"   {v:+6.0f} ms  {100*c/NB:5.1f} %")
print(f"  median {np.median(arg):+.1f} ms   95 % interval "
      f"[{np.percentile(arg,2.5):+.0f}, {np.percentile(arg,97.5):+.0f}] ms")
print(f"  fraction at or below -25 ms: {np.mean(arg<=-25):.3f}")
print(f"  fraction at 0 ms or later:   {np.mean(arg>=0):.3f}")
json.dump(dict(deltas_ms=[float(d*1e3) for d in DELTAS],point=[float(v) for v in point],
               argmax_point=float(DELTAS[int(np.argmax(point))]*1e3),n_boot=NB,
               argmax_median=float(np.median(arg)),
               argmax_lo=float(np.percentile(arg,2.5)),
               argmax_hi=float(np.percentile(arg,97.5)),
               frac_le_m25=float(np.mean(arg<=-25)),frac_ge_0=float(np.mean(arg>=0)),
               hist={str(float(v)):int(c) for v,c in zip(vals,cts)}),
          open('experiments/e37_map/argmax_bootstrap.json','w'),indent=1)
print("WROTE experiments/e37_map/argmax_bootstrap.json")
