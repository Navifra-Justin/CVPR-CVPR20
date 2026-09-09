"""E36 - the descriptive statistics of the E27 fit sample, measured on that sample.

Two numbers reached the manuscript from the retracted E21 experiment: the correlation
between label speed and box side (+0.349) and the fraction of boxes that link between
adjacent label times (81.5 %). Both were measured on E21's 2235 rows under a 15 px/s speed
floor, and the manuscript attaches them to E27's 22 534 rows with no floor. They are
recomputed here on the sample that is actually reported.
"""
import numpy as np, glob, os, json
Z=np.load('experiments/e27_rows/rows.npz',allow_pickle=True)
A=Z['rows']; ci={c:i for i,c in enumerate(list(Z['cols']))}
g=lambda k:A[:,ci[k]]
vx=(g('fx')+g('bx'))/(g('dt_f')+g('dt_b')); vy=(g('fy')+g('by'))/(g('dt_f')+g('dt_b'))
m=np.isfinite(vx)&np.isfinite(vy)&(np.hypot(vx,vy)>0)
V=np.hypot(vx,vy)[m]; size=np.sqrt(g('gw')*g('gh'))[m]
r=float(np.corrcoef(V,size)[0,1])
print(f"fit sample n={m.sum()}")
print(f"  corr(|v|, sqrt(A))            {r:+.4f}   (E21 reported +0.349 on 2235 floored rows)")
for f in (15.,):
    k=V>=f; print(f"  the same above {f:.0f} px/s (n={k.sum()}) {np.corrcoef(V[k],size[k])[0,1]:+.4f}")

# the linking rate, on the whole validation split, by the rule E27 and E28 both use
LINK=0.3
def iou1(a,B):
    x1=np.maximum(a[0],B[:,0]); y1=np.maximum(a[1],B[:,1])
    x2=np.minimum(a[2],B[:,2]); y2=np.minimum(a[3],B[:,3])
    w=np.clip(x2-x1,0,None); h=np.clip(y2-y1,0,None); it=w*h
    return it/np.maximum((a[2]-a[0])*(a[3]-a[1])+(B[:,2]-B[:,0])*(B[:,3]-B[:,1])-it,1e-9)
tot=0; lnk=0
for sd in sorted(glob.glob('data/gen1x/gen1/val/*')):
    p=os.path.join(sd,'labels_v2','labels.npz')
    if not os.path.exists(p): continue
    L=np.load(p)['labels']; ts=np.sort(np.unique(L['t']))
    B=[];CL=[]
    for t in ts:
        G=L[L['t']==t]
        B.append(np.column_stack([G['x'],G['y'],G['x']+G['w'],G['y']+G['h']]).astype(float))
        CL.append(np.asarray(G['class_id']))
    for k in range(len(ts)-1):
        for i in range(len(B[k])):
            tot+=1
            same=(CL[k][i]==CL[k+1])
            if not same.any(): continue
            io=np.where(same,iou1(B[k][i],B[k+1]),0.0)
            if io.max()>=LINK: lnk+=1
print(f"\n  boxes with a successor at IoU >= {LINK}: {lnk}/{tot} = {100*lnk/max(tot,1):.1f} %"
      f"   (E21's comment said 81.5 %)")
json.dump(dict(n=int(m.sum()),corr_speed_size=r,link_pct=100*lnk/max(tot,1),
               link_num=int(lnk),link_den=int(tot)),
          open('experiments/e27_rows/split_stats.json','w'),indent=1)
print("WROTE experiments/e27_rows/split_stats.json")
