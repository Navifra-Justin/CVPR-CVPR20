"""E37b - average precision as a function of the instant the ground truth describes.

Every other measurement in this work describes a property. This one asks the benchmark's
own question: if the detector's output describes the state at t + delta rather than at the
label instant t, then scoring it against ground truth displaced to t + delta should score
better, and the delta that maximises average precision is an estimate of the output time
from the metric itself.

The ground truth is displaced, not the detections. Every ground-truth box carries a track
velocity from its own labels; detections do not, and moving a detection by the velocity of
the box it happens to match would be circular. Displacing the ground truth by delta*v
scores the released predictions against the state each object occupied delta later and
leaves the detector untouched.

Two evaluation sets are reported.
  all      every ground-truth box; the 31 % without a centered velocity stay put, which
           attenuates the curve without moving its argmax.
  moving   only boxes with a centered velocity, the rest marked ignore in the COCO sense,
           so a detection matching one is neither a hit nor a false positive.

AP is computed the standard way: per frame and class, detections sorted by score, greedy
one-to-one matching at an IoU threshold, then all-point interpolated precision-recall.
mAP averages IoU 0.5 to 0.95 in steps of 0.05.
"""
import numpy as np, json, os
Z=np.load('experiments/e37_map/dets.npz')
DET=Z['det'].astype(np.float64); GT=Z['gt'].astype(np.float64)
print(f"frames {int(GT[:,0].max())+1}  detections {len(DET)}  ground truth {len(GT)}")
hasv=np.isfinite(GT[:,6])&np.isfinite(GT[:,7])
print(f"ground truth with a centered velocity: {hasv.sum()} ({100*hasv.mean():.1f} %)")

NF=int(max(DET[:,0].max(),GT[:,0].max()))+1
det_by=[[] for _ in range(NF)]
for r in DET: det_by[int(r[0])].append(r)
gt_by=[[] for _ in range(NF)]
for i,r in enumerate(GT): gt_by[int(r[0])].append((r,hasv[i]))
CLASSES=sorted(set(GT[:,5].astype(int)))
THRS=np.arange(0.5,0.96,0.05)

def iou_mat(D,G):
    if len(D)==0 or len(G)==0: return np.zeros((len(D),len(G)))
    x1=np.maximum(D[:,None,0],G[None,:,0]); y1=np.maximum(D[:,None,1],G[None,:,1])
    x2=np.minimum(D[:,None,2],G[None,:,2]); y2=np.minimum(D[:,None,3],G[None,:,3])
    w=np.clip(x2-x1,0,None); h=np.clip(y2-y1,0,None); it=w*h
    ad=((D[:,2]-D[:,0])*(D[:,3]-D[:,1]))[:,None]
    ag=((G[:,2]-G[:,0])*(G[:,3]-G[:,1]))[None,:]
    return it/np.maximum(ad+ag-it,1e-9)

def evaluate(delta, mode):
    """mode 'all' keeps every gt; mode 'moving' marks velocity-less gt as ignore."""
    out={}
    for c in CLASSES:
        scores=[]; tp={t:[] for t in THRS}; npos=0
        for fi in range(NF):
            G=[]; ign=[]
            for r,hv in gt_by[fi]:
                if int(r[5])!=c: continue
                b=r[1:5].copy()
                if hv:
                    b[0]+=delta*r[6]; b[2]+=delta*r[6]
                    b[1]+=delta*r[7]; b[3]+=delta*r[7]
                G.append(b); ign.append((mode=='moving') and (not hv))
            D=[r for r in det_by[fi] if int(r[6])==c]
            G=np.array(G).reshape(-1,4); ign=np.array(ign,dtype=bool)
            npos+=int((~ign).sum())
            if not len(D): continue
            D=np.array(D); order=np.argsort(-D[:,5]); D=D[order]
            M=iou_mat(D[:,1:5],G)
            scores.append(D[:,5])
            for t in THRS:
                used=np.zeros(len(G),dtype=bool); flag=np.zeros(len(D))
                for di in range(len(D)):
                    j=-1; best=t
                    for gj in range(len(G)):
                        if used[gj] or M[di,gj]<best: continue
                        best=M[di,gj]; j=gj
                    if j>=0:
                        used[j]=True
                        flag[di]= -1.0 if ign[j] else 1.0     # -1 marks an ignored match
                tp[t].append(flag)
        if not scores: continue
        S=np.concatenate(scores); o=np.argsort(-S)
        aps=[]
        for t in THRS:
            f=np.concatenate(tp[t])[o]
            keep=f>=0                                  # drop detections matched to ignores
            f=f[keep]
            ctp=np.cumsum(f==1); cfp=np.cumsum(f==0)
            rec=ctp/max(npos,1); prec=ctp/np.maximum(ctp+cfp,1e-9)
            mp=np.concatenate([[0],prec,[0]]); mr=np.concatenate([[0],rec,[1]])
            for i in range(len(mp)-2,-1,-1): mp[i]=max(mp[i],mp[i+1])
            idx=np.where(mr[1:]!=mr[:-1])[0]
            aps.append(float(((mr[idx+1]-mr[idx])*mp[idx+1]).sum()))
        out[c]=dict(ap50=aps[0],map=float(np.mean(aps)),npos=npos)
    m=float(np.mean([v['map'] for v in out.values()]))
    a50=float(np.mean([v['ap50'] for v in out.values()]))
    return m,a50

DELTAS=np.round(np.arange(-0.060,0.0601,0.005),4)
res={}
for mode in ('all','moving'):
    print(f"\n=== {mode} ===")
    print("  delta (ms)     mAP      AP50")
    rows=[]
    for d in DELTAS:
        m,a=evaluate(float(d),mode)
        rows.append((float(d)*1e3,m,a))
        print(f"  {d*1e3:+8.1f}   {m:.5f}   {a:.5f}",flush=True)
    R=np.array(rows)
    i=int(np.argmax(R[:,1]))
    # parabolic refinement of the argmax
    if 0<i<len(R)-1:
        y0,y1,y2=R[i-1,1],R[i,1],R[i+1,1]
        sh=0.5*(y0-y2)/max(y0-2*y1+y2,1e-12)
        peak=R[i,0]+sh*(R[1,0]-R[0,0])
    else: peak=R[i,0]
    j=int(np.argmin(np.abs(R[:,0]-0.0))); k=int(np.argmin(np.abs(R[:,0]+23.81)))
    print(f"  argmax at {R[i,0]:+.1f} ms (parabolic {peak:+.2f} ms), mAP {R[i,1]:.5f}")
    print(f"  mAP at the label instant      {R[j,1]:.5f}")
    print(f"  mAP at the evidence centroid  {R[k,1]:.5f}   "
          f"cost {100*(R[j,1]-R[k,1])/max(R[j,1],1e-9):.2f} % of mAP, "
          f"{100*(R[j,1]-R[k,1]):.2f} mAP points")
    res[mode]=dict(deltas_ms=[float(v) for v in R[:,0]],
                   map=[float(v) for v in R[:,1]],ap50=[float(v) for v in R[:,2]],
                   argmax_ms=float(R[i,0]),argmax_parabolic_ms=float(peak),
                   map_at_zero=float(R[j,1]),map_at_centroid=float(R[k,1]),
                   drop_points=float(100*(R[j,1]-R[k,1])))
os.makedirs('experiments/e37_map',exist_ok=True)
json.dump(res,open('experiments/e37_map/sweep.json','w'),indent=1)
print("\nWROTE experiments/e37_map/sweep.json")
