"""E21 - the predictor's effective OUTPUT time, measured directly.

E17 measured the input influence profile by occluding bins and found its centroid at
-24.94 ms. A reviewer objected, correctly, that occlusion sensitivity equals a linear
weight only for a predictor linear in its bins; RVT is nonlinear and recurrent, so a
network could weight the whole window evenly and still extrapolate its output to the
query instant. Input influence does not identify output time.

This measures the output time. Run the released rvt-t through gen1 val sequentially,
keeping the recurrent state, postprocess to detections at each labelled frame, match to
ground truth, project the residual onto the track's own direction of travel and divide
by its speed:
    delta = <p - g, u> / |v|          seconds
A predictor whose output describes the state at the query instant gives delta ~ 0.
A predictor whose output describes the state tau earlier gives delta ~ -tau along travel.
"""
import sys, os, glob, json, numpy as np, torch, h5py, hdf5plugin
sys.path.insert(0,'/work/src/RVT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector
from models.detection.yolox.utils.boxes import postprocess

DEV=os.environ.get('DEV','cuda:0'); NSEQ=int(os.environ.get('NSEQ','40'))
CONF=0.1; NMS=0.45; WARM=20; MINSPD=10.0   # px/s

base=OmegaConf.load('/work/src/RVT/config/model/base.yaml')
rnn =OmegaConf.load('/work/src/RVT/config/model/rnndet.yaml')
mx  =OmegaConf.load('/work/src/RVT/config/model/maxvit_yolox/default.yaml')['model']
cfg =OmegaConf.merge(base.get('model',base),rnn,mx)
with open_dict(cfg):
    cfg.backbone.embed_dim=32; cfg.fpn.depth=0.33
    cfg.backbone.in_res_hw=[256,320]; cfg.backbone.stage.attention.partition_size=[4,5]
    cfg.head.num_classes=2
mdl=YoloXDetector(cfg)
ck=torch.load('/work/data/ckpt/rvt-t-gen1.ckpt',map_location='cpu',weights_only=False)
mdl.load_state_dict({k[4:]:v for k,v in ck['state_dict'].items() if k.startswith('mdl.')},strict=True)
mdl.eval().to(DEV)

def iou(a,B):
    x1=np.maximum(a[0],B[:,0]); y1=np.maximum(a[1],B[:,1])
    x2=np.minimum(a[2],B[:,2]); y2=np.minimum(a[3],B[:,3])
    w=np.clip(x2-x1,0,None); h=np.clip(y2-y1,0,None); inter=w*h
    ua=(a[2]-a[0])*(a[3]-a[1])+(B[:,2]-B[:,0])*(B[:,3]-B[:,1])-inter
    return inter/np.maximum(ua,1e-9)

rows=[]
for si,sd in enumerate(sorted(glob.glob('/work/data/gen1x/gen1/val/*'))[:NSEQ]):
    rd=os.path.join(sd,'event_representations_v2','stacked_histogram_dt=50_nbins=10')
    try:
        L=np.load(os.path.join(sd,'labels_v2','labels.npz'))['labels']
        o2r=np.load(os.path.join(rd,'objframe_idx_2_repr_idx.npy'))
        rts=np.load(os.path.join(rd,'timestamps_us.npy'))
    except Exception: continue
    lts=np.unique(L['t'])
    if len(o2r)<3: continue
    # Gen1 track_id is a per-frame index, not a persistent track: 145 labels carry 145
    # distinct ids. Rebuild association by greedy same-class IoU matching between
    # adjacent label times (81.5 % of boxes link at IoU >= 0.3) and take velocity from
    # the matched pair. Key velocities by (label time, box index) rather than track id.
    def _iou(a,B):
        x1=np.maximum(a[0],B[:,0]); y1=np.maximum(a[1],B[:,1])
        x2=np.minimum(a[2],B[:,2]); y2=np.minimum(a[3],B[:,3])
        w=np.clip(x2-x1,0,None); h=np.clip(y2-y1,0,None); it=w*h
        return it/np.maximum((a[2]-a[0])*(a[3]-a[1])+(B[:,2]-B[:,0])*(B[:,3]-B[:,1])-it,1e-9)
    vel={}
    tsort=np.sort(np.unique(L['t']))
    for kk in range(len(tsort)-1):
        Aa=L[L['t']==tsort[kk]]; Bb=L[L['t']==tsort[kk+1]]
        if not len(Aa) or not len(Bb): continue
        AB=np.column_stack([Aa['x'],Aa['y'],Aa['x']+Aa['w'],Aa['y']+Aa['h']]).astype(float)
        BB=np.column_stack([Bb['x'],Bb['y'],Bb['x']+Bb['w'],Bb['y']+Bb['h']]).astype(float)
        dt=(tsort[kk+1]-tsort[kk])*1e-6
        if dt<=0: continue
        for ii in range(len(AB)):
            same=(Aa['class_id'][ii]==Bb['class_id'])
            if not same.any(): continue
            io=np.where(same,_iou(AB[ii],BB),0.0)
            jj=int(np.argmax(io))
            if io[jj]<0.3: continue
            ca=((AB[ii,0]+AB[ii,2])/2,(AB[ii,1]+AB[ii,3])/2)
            cb=((BB[jj,0]+BB[jj,2])/2,(BB[jj,1]+BB[jj,3])/2)
            vel[(int(tsort[kk]),ii)]=((cb[0]-ca[0])/dt,(cb[1]-ca[1])/dt,jj)
    with h5py.File(os.path.join(rd,'event_representations.h5'),'r') as f:
        key=list(f.keys())[0]; D=f[key]
        start=max(int(o2r[0])-WARM,0); stop=min(int(o2r[-1])+1,D.shape[0])
        want={int(o2r[i]):int(lts[i]) for i in range(min(len(o2r),len(lts)))}
        states=None
        for i in range(start,stop):
            x=torch.from_numpy(D[i][None]).float()
            x=torch.nn.functional.pad(x,(0,320-x.shape[-1],0,256-x.shape[-2])).to(DEV)
            with torch.no_grad():
                out,_,states=mdl.forward(x,previous_states=states)
            if i not in want: continue
            det=postprocess(out.clone(),2,CONF,NMS)[0]
            if det is None: continue
            P=det[:,:4].cpu().numpy()
            lt=want[i]; G=L[L['t']==lt]
            if not len(G): continue
            GB=np.column_stack([G['x'],G['y'],G['x']+G['w'],G['y']+G['h']]).astype(float)
            for gi in range(len(GB)):
                vv=vel.get((int(lt),gi))
                if vv is None: continue
                sp=float(np.hypot(vv[0],vv[1]))
                # acceleration: velocity of the NEXT interval minus this one
                nxt=None
                _ti=int(np.searchsorted(np.sort(np.unique(L['t'])),lt))
                _ts=np.sort(np.unique(L['t']))
                if _ti+1<len(_ts): nxt=vel.get((int(_ts[_ti+1]),int(vv[2])))
                if nxt is None: continue
                _dt=(_ts[_ti+1]-lt)*1e-6
                acc=float(np.hypot(nxt[0]-vv[0],nxt[1]-vv[1])/max(_dt,1e-6))
                if sp<MINSPD: continue
                ious=iou(GB[gi],P)
                j=int(np.argmax(ious))
                if ious[j]<0.5: continue
                pc=np.array([(P[j,0]+P[j,2])/2,(P[j,1]+P[j,3])/2])
                gc=np.array([(GB[gi,0]+GB[gi,2])/2,(GB[gi,1]+GB[gi,3])/2])
                u=np.array(vv[:2])/sp
                epar=float(np.dot(pc-gc,u)); eperp=float(np.cross(u,pc-gc))
                gw=float(GB[gi,2]-GB[gi,0]); gh=float(GB[gi,3]-GB[gi,1])
                rows.append((epar, eperp, sp, float(ious[j]), np.sqrt(gw*gh), acc))
    if (si+1)%10==0: print(f"  {si+1} seqs, {len(rows)} matches", flush=True)

A=np.array(rows)
epar,eperp,sp,io,bs,acc=A.T
print(f"\nMATCHES {len(A)}   median speed {np.median(sp):.1f} px/s   median IoU {np.median(io):.3f}")

# --- E24: identify the extrapolation ORDER, and isolate the anisotropic term ----
# An isotropic "hard object" effect raises along- and cross-track error equally and
# cancels in their difference. Only a term acting along the direction of travel
# survives. Fit both channels with the same regressors and test the difference.
#   zeroth-order extrapolation (report the last seen position) costs ~ v*tau
#   first-order  (report position + velocity*tau)          costs ~ a*tau^2/2
# so the two orders are separated by which regressor carries the anisotropic excess.
print(f"acceleration px/s^2: p25 {np.percentile(acc,25):.1f} med {np.median(acc):.1f} p75 {np.percentile(acc,75):.1f}")
print(f"corr(acc,|v|) {np.corrcoef(acc,sp)[0,1]:+.3f}   corr(acc,size) {np.corrcoef(acc,bs)[0,1]:+.3f}")
def lsq(X,y):
    c,*_=np.linalg.lstsq(X,y,rcond=None); r=y-X@c
    cov=np.sum(r*r)/max(len(y)-X.shape[1],1)*np.linalg.inv(X.T@X)
    return c,np.sqrt(np.diag(cov)),cov
X=np.column_stack([np.ones_like(sp),sp,bs,acc])
names=["intercept","speed  (order 0)","size","accel  (order 1)"]
ca,sea,cova=lsq(X,epar)      # SIGNED: the lag maps to the speed coefficient only for a signed residual
cc,sec,covc=lsq(X,eperp)     # SIGNED cross-track null
print("\nSIGNED residuals (the lag conversion is only valid here)")
print("                      along-track        cross-track        ANISOTROPIC (along-cross)")
for k,nm in enumerate(names):
    d=ca[k]-cc[k]; sd=np.sqrt(sea[k]**2+sec[k]**2)
    print(f"  {nm:<18} {ca[k]:+.6f}({abs(ca[k])/max(sea[k],1e-12):4.1f}SE)  "
          f"{cc[k]:+.6f}({abs(cc[k])/max(sec[k],1e-12):4.1f}SE)   {d:+.6f}  {abs(d)/max(sd,1e-12):5.2f} SE")
ma,sma,_=lsq(X,np.abs(epar)); mc,smc,_=lsq(X,np.abs(eperp))
print("\nMAGNITUDE residuals (valid for asking whether error GROWS, not for a lag)")
for k,nm in enumerate(names):
    d=ma[k]-mc[k]; sd=np.sqrt(sma[k]**2+smc[k]**2)
    print(f"  {nm:<18} {ma[k]:+.6f}({abs(ma[k])/max(sma[k],1e-12):4.1f}SE)  "
          f"{mc[k]:+.6f}({abs(mc[k])/max(smc[k],1e-12):4.1f}SE)   {d:+.6f}  {abs(d)/max(sd,1e-12):5.2f} SE")
tau=24.94e-3
da=ca[3]-cc[3]; ds=ca[1]-cc[1]
print(f"\nEXTRAPOLATION ORDER")
print(f"  order 1 predicts the anisotropic ACCEL coefficient = tau^2/2 = {tau*tau/2:.6f} s^2")
print(f"    measured {da:+.6f} -> implied tau = {np.sqrt(max(2*da,0))*1e3:.1f} ms")
print(f"  order 0 predicts the anisotropic SPEED coefficient = tau = {tau:.6f} s")
print(f"    measured {ds:+.6f} -> implied tau = {ds*1e3:+.1f} ms")
import json
json.dump(dict(n=int(len(A)),aniso_accel=float(ca[3]-cc[3]),aniso_speed=float(ca[1]-cc[1]),
               median_speed=float(np.median(sp))),
          open('/work/experiments/e24_order/signed.json','w'),indent=1)
print("WROTE")
