"""E37c - the benchmark's sensitivity to a temporal offset, by object speed.

E37b swept the instant the ground truth describes and found a smooth unimodal curve whose
maximum sits at -10 ms, between the label instant and the evidence centroid, and whose
total variation over +/-60 ms is under one mAP point. That flatness is the finding, not a
failure: it says the metric can barely see the interval this paper measures.

It should be flat, and the reason is computable. A displacement of tau costs IoU only in
proportion to tau*|v| against the box size, and Gen1's median label speed is 5.4 px/s, so
24.94 ms is 0.13 px on a 41.7 px box. The prediction is that the curve deepens with speed.
Stratifying by each box's own speed tests that prediction and gives the cost in the regime
where an event camera is supposed to earn its keep.

Ground truth without a centered velocity is marked ignore throughout, so every stratum is
scored against the same kind of object.
"""
import numpy as np, json, os
Z=np.load('experiments/e37_map/dets.npz')
DET=Z['det'].astype(np.float64); GT=Z['gt'].astype(np.float64)
hasv=np.isfinite(GT[:,6])&np.isfinite(GT[:,7])
SPD=np.hypot(GT[:,6],GT[:,7])
NF=int(max(DET[:,0].max(),GT[:,0].max()))+1
det_by=[[] for _ in range(NF)]
for r in DET: det_by[int(r[0])].append(r)
gt_by=[[] for _ in range(NF)]
for i,r in enumerate(GT): gt_by[int(r[0])].append((r,bool(hasv[i]),float(SPD[i])))
CLASSES=sorted(set(GT[:,5].astype(int)))
THRS=np.arange(0.5,0.96,0.05)
side=np.sqrt((GT[:,3]-GT[:,1])*(GT[:,4]-GT[:,2]))
print(f"gt {len(GT)}, with velocity {hasv.sum()} ({100*hasv.mean():.1f} %)")
for q in (50,75,90,99):
    print(f"  speed p{q}: {np.percentile(SPD[hasv],q):6.2f} px/s   "
          f"24.94 ms = {np.percentile(SPD[hasv],q)*0.02494:5.3f} px   "
          f"box side median {np.median(side[hasv]):.1f} px")

def iou_mat(D,G):
    if len(D)==0 or len(G)==0: return np.zeros((len(D),len(G)))
    x1=np.maximum(D[:,None,0],G[None,:,0]); y1=np.maximum(D[:,None,1],G[None,:,1])
    x2=np.minimum(D[:,None,2],G[None,:,2]); y2=np.minimum(D[:,None,3],G[None,:,3])
    w=np.clip(x2-x1,0,None); h=np.clip(y2-y1,0,None); it=w*h
    ad=((D[:,2]-D[:,0])*(D[:,3]-D[:,1]))[:,None]
    ag=((G[:,2]-G[:,0])*(G[:,3]-G[:,1]))[None,:]
    return it/np.maximum(ad+ag-it,1e-9)

def evaluate(delta, lo, hi):
    out={}
    for c in CLASSES:
        scores=[]; tp={t:[] for t in THRS}; npos=0
        for fi in range(NF):
            G=[]; ign=[]
            for r,hv,sp in gt_by[fi]:
                if int(r[5])!=c: continue
                b=r[1:5].copy()
                if hv:
                    b[0]+=delta*r[6]; b[2]+=delta*r[6]
                    b[1]+=delta*r[7]; b[3]+=delta*r[7]
                G.append(b); ign.append((not hv) or not (lo<=sp<hi))
            D=[r for r in det_by[fi] if int(r[6])==c]
            G=np.array(G).reshape(-1,4); ign=np.array(ign,dtype=bool)
            npos+=int((~ign).sum())
            if not len(D): continue
            D=np.array(D); D=D[np.argsort(-D[:,5])]
            M=iou_mat(D[:,1:5],G); scores.append(D[:,5])
            for t in THRS:
                used=np.zeros(len(G),dtype=bool); flag=np.zeros(len(D))
                for di in range(len(D)):
                    j=-1; best=t
                    for gj in range(len(G)):
                        if used[gj] or M[di,gj]<best: continue
                        best=M[di,gj]; j=gj
                    if j>=0:
                        used[j]=True; flag[di]= -1.0 if ign[j] else 1.0
                tp[t].append(flag)
        if not scores or npos==0: continue
        S=np.concatenate(scores); o=np.argsort(-S); aps=[]
        for t in THRS:
            f=np.concatenate(tp[t])[o]; f=f[f>=0]
            ctp=np.cumsum(f==1); cfp=np.cumsum(f==0)
            rec=ctp/npos; prec=ctp/np.maximum(ctp+cfp,1e-9)
            mp=np.concatenate([[0],prec,[0]]); mr=np.concatenate([[0],rec,[1]])
            for i in range(len(mp)-2,-1,-1): mp[i]=max(mp[i],mp[i+1])
            idx=np.where(mr[1:]!=mr[:-1])[0]
            aps.append(float(((mr[idx+1]-mr[idx])*mp[idx+1]).sum()))
        out[c]=float(np.mean(aps))
    return float(np.mean(list(out.values()))) if out else float('nan')

DELTAS=np.round(np.arange(-0.050,0.0301,0.005),4)
STRATA=[("all moving",0.0,1e9),("slow, |v| < 10",0.0,10.0),
        ("10 <= |v| < 25",10.0,25.0),("25 <= |v| < 50",25.0,50.0),
        ("fast, |v| >= 50",50.0,1e9)]
res={}
for name,lo,hi in STRATA:
    n=int(((SPD>=lo)&(SPD<hi)&hasv).sum())
    row=[]
    for d in DELTAS: row.append(evaluate(float(d),lo,hi))
    row=np.array(row)
    i=int(np.nanargmax(row))
    j=int(np.argmin(np.abs(DELTAS-0.0))); k=int(np.argmin(np.abs(DELTAS+0.02494)))
    span=float(np.nanmax(row)-np.nanmin(row))
    print(f"\n{name}  (n = {n})")
    print("   delta(ms) "+" ".join(f"{d*1e3:+6.0f}" for d in DELTAS))
    print("   mAP       "+" ".join(f"{v:6.3f}" for v in row))
    print(f"   argmax {DELTAS[i]*1e3:+.0f} ms   mAP(0) {row[j]:.4f}   "
          f"mAP(-24.94) {row[k]:.4f}   cost {100*(row[j]-row[k]):.2f} points "
          f"({100*(row[j]-row[k])/max(row[j],1e-9):.2f} %)   span {100*span:.2f} points",flush=True)
    res[name]=dict(n=n,deltas_ms=[float(d*1e3) for d in DELTAS],
                   map=[float(v) for v in row],argmax_ms=float(DELTAS[i]*1e3),
                   map_zero=float(row[j]),map_centroid=float(row[k]),
                   cost_points=float(100*(row[j]-row[k])),span_points=float(100*span))
json.dump(res,open('experiments/e37_map/strata.json','w'),indent=1)
print("\nWROTE experiments/e37_map/strata.json")
