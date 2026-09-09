"""E52 - does the temporal support change a benchmark CONCLUSION, not just exist?

E51 dumped detections for five released Gen1 checkpoints under one protocol. This scores
them the way the benchmark does, and then the way the benchmark would if each detector were
scored against the state its own output describes, and asks whether the comparison changes.

Three things are reported, in increasing order of what they would cost the field:
  (a) each model's mAP(delta) curve, its argmax, and its mAP at delta = 0
  (b) the ordering of the models at delta = 0 against the ordering when each is scored at
      its own argmax, and the pairwise gaps under both
  (c) the same within speed strata, because the aggregate curve is flat by construction:
      most Gen1 objects barely move, and any temporal effect has to live where they do

The fairness condition is that every model sees the same ground truth, the same frames and
the same threshold. The ground-truth arrays are emitted by every dump and are checked to be
identical here; if they are not, nothing below is a comparison.
"""
import numpy as np, json, glob, os, sys
FILES=sorted(glob.glob('experiments/e51_ranking/dets-*.npz'))
if len(FILES)<2: raise SystemExit(f"need at least two dumps, have {len(FILES)}")
ORDER={'rvt-t':0,'rvt-s':1,'rvt-b':2,'s5vit-small':3,'s5vit-base':4}
M=[]
for f in FILES:
    nm=os.path.basename(f)[5:-4]
    Z=np.load(f); M.append(dict(name=nm,det=Z['det'].astype(np.float64),gt=Z['gt'].astype(np.float64)))
M.sort(key=lambda r: ORDER.get(r['name'],9))
GT=M[0]['gt']
for m in M:
    if m['gt'].shape!=GT.shape or not np.allclose(m['gt'],GT,equal_nan=True):
        raise SystemExit(f"ground truth differs for {m['name']}: not a comparison")
print(f"{len(M)} models, identical ground truth: {GT.shape[0]} boxes over "
      f"{int(GT[:,0].max())+1} frames")
hasv=np.isfinite(GT[:,6])&np.isfinite(GT[:,7])
SPD=np.hypot(np.nan_to_num(GT[:,6]),np.nan_to_num(GT[:,7]))
NF=int(GT[:,0].max())+1
CLASSES=sorted(set(GT[:,5].astype(int)))
THRS=np.arange(0.5,0.96,0.05)
gt_by=[[] for _ in range(NF)]
for i,r in enumerate(GT): gt_by[int(r[0])].append((r,hasv[i],SPD[i]))

def iou_mat(D,G):
    if len(D)==0 or len(G)==0: return np.zeros((len(D),len(G)))
    x1=np.maximum(D[:,None,0],G[None,:,0]); y1=np.maximum(D[:,None,1],G[None,:,1])
    x2=np.minimum(D[:,None,2],G[None,:,2]); y2=np.minimum(D[:,None,3],G[None,:,3])
    w=np.clip(x2-x1,0,None); h=np.clip(y2-y1,0,None); it=w*h
    ad=((D[:,2]-D[:,0])*(D[:,3]-D[:,1]))[:,None]
    ag=((G[:,2]-G[:,0])*(G[:,3]-G[:,1]))[None,:]
    return it/np.maximum(ad+ag-it,1e-9)

def evaluate(det_by,delta,lo=None,hi=None):
    """mAP over gt with a centered velocity; boxes outside [lo,hi) px/s are ignored."""
    out={}
    for c in CLASSES:
        scores=[]; tp={t:[] for t in THRS}; npos=0
        for fi in range(NF):
            G=[]; ign=[]
            for r,hv,sp in gt_by[fi]:
                if int(r[5])!=c: continue
                b=r[1:5].copy()
                keep=hv and (lo is None or (sp>=lo and sp<hi))
                if hv:
                    b[0]+=delta*r[6]; b[2]+=delta*r[6]
                    b[1]+=delta*r[7]; b[3]+=delta*r[7]
                G.append(b); ign.append(not keep)
            D=[r for r in det_by[fi] if int(r[6])==c]
            G=np.array(G).reshape(-1,4); ign=np.array(ign,dtype=bool)
            npos+=int((~ign).sum())
            if not len(D): continue
            D=np.array(D); D=D[np.argsort(-D[:,5])]
            IM=iou_mat(D[:,1:5],G); scores.append(D[:,5])
            # same greedy one-to-one matching as E37b, with the inner search over ground
            # truth done by numpy instead of a Python loop. 255 evaluations are needed here
            # against E37b's 34, and the two are checked to agree before this is used.
            for t in THRS:
                used=np.zeros(len(G),dtype=bool); flag=np.zeros(len(D))
                row=IM  # (nD, nG)
                for di in range(len(D)):
                    r=row[di]
                    cand=(~used)&(r>=t)
                    if not cand.any(): continue
                    j=int(np.flatnonzero(cand)[np.argmax(r[cand])])
                    used[j]=True; flag[di]= -1.0 if ign[j] else 1.0
                tp[t].append(flag)
        if not scores: continue
        S=np.concatenate(scores); o=np.argsort(-S); aps=[]
        for t in THRS:
            f=np.concatenate(tp[t])[o]; f=f[f>=0]
            ctp=np.cumsum(f==1); cfp=np.cumsum(f==0)
            rec=ctp/max(npos,1); prec=ctp/np.maximum(ctp+cfp,1e-9)
            mp=np.concatenate([[0],prec,[0]]); mr=np.concatenate([[0],rec,[1]])
            for i in range(len(mp)-2,-1,-1): mp[i]=max(mp[i],mp[i+1])
            idx=np.where(mr[1:]!=mr[:-1])[0]
            aps.append(float(((mr[idx+1]-mr[idx])*mp[idx+1]).sum()))
        out[c]=float(np.mean(aps))
    return float(np.mean(list(out.values()))) if out else 0.0

DELTAS=np.round(np.arange(-0.050,0.0301,0.005),4)
STRATA=[('all moving',None,None),('10-25 px/s',10.,25.),('25-50 px/s',25.,50.)]
# The shared machine has killed this process for host memory more than once, so each model's
# curves are written as they finish and a restart picks up where the last one stopped.
CKPT='experiments/e51_ranking/curves.json'
res=json.load(open(CKPT)) if os.path.exists(CKPT) else {}
for m in M:
    if m['name'] in res and len(res[m['name']])==len(STRATA):
        print(f"  {m['name']:<12} already done, skipped",flush=True); continue
    db=[[] for _ in range(NF)]
    for r in m['det']: db[int(r[0])].append(r)
    res.setdefault(m['name'],{})
    for sname,lo,hi in STRATA:
        if sname in res[m['name']]: continue
        curve=[evaluate(db,float(d),lo,hi) for d in DELTAS]
        c=np.array(curve); i=int(np.argmax(c)); j=int(np.argmin(abs(DELTAS)))
        res[m['name']][sname]=dict(deltas_ms=[float(d*1e3) for d in DELTAS],
                                   map=[float(v) for v in c],
                                   map_at_zero=float(c[j]),argmax_ms=float(DELTAS[i]*1e3),
                                   map_at_argmax=float(c[i]))
        print(f"  {m['name']:<12} {sname:<11} mAP(0) {c[j]:.5f}   argmax "
              f"{DELTAS[i]*1e3:+6.1f} ms   mAP(argmax) {c[i]:.5f}   "
              f"gain {100*(c[i]-c[j]):+.3f} pt",flush=True)
        json.dump(res,open(CKPT,'w'),indent=1)
    m['det']=None   # release before the next model is loaded

print("\n=== does the comparison change? ===")
summary={}
for sname,_,_ in STRATA:
    z=[(m['name'],res[m['name']][sname]['map_at_zero']) for m in M]
    a=[(m['name'],res[m['name']][sname]['map_at_argmax']) for m in M]
    oz=[n for n,_ in sorted(z,key=lambda r:-r[1])]
    oa=[n for n,_ in sorted(a,key=lambda r:-r[1])]
    dz=dict(z); da=dict(a)
    pairs=[]
    for i in range(len(M)):
        for j in range(i+1,len(M)):
            n1,n2=M[i]['name'],M[j]['name']
            g0=100*(dz[n1]-dz[n2]); g1=100*(da[n1]-da[n2])
            pairs.append((n1,n2,g0,g1,np.sign(g0)!=np.sign(g1)))
    flips=[p for p in pairs if p[4]]
    print(f"\n{sname}")
    print(f"  order at delta=0        {' > '.join(oz)}")
    print(f"  order at each own argmax{' > '.join(oa)}")
    print(f"  order changes: {oz!=oa}   pairwise sign flips: {len(flips)} of {len(pairs)}")
    worst=max(pairs,key=lambda p: abs(p[3]-p[2]))
    print(f"  largest change in a pairwise gap: {worst[0]} vs {worst[1]}, "
          f"{worst[2]:+.3f} -> {worst[3]:+.3f} points")
    summary[sname]=dict(order_zero=oz,order_aligned=oa,order_changes=bool(oz!=oa),
                        n_flips=len(flips),n_pairs=len(pairs),
                        flips=[[p[0],p[1],p[2],p[3]] for p in flips],
                        largest_gap_change=[worst[0],worst[1],worst[2],worst[3]])
os.makedirs('experiments/e51_ranking',exist_ok=True)
json.dump(dict(models=[m['name'] for m in M],per_model=res,summary=summary),
          open('experiments/e51_ranking/ranking.json','w'),indent=1)
print("\nWROTE experiments/e51_ranking/ranking.json")
