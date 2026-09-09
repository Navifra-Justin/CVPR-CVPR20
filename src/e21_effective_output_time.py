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
CONF=0.1; NMS=0.45; WARM=20; MINSPD=15.0   # px/s

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
            vel[(int(tsort[kk]),ii)]=((cb[0]-ca[0])/dt,(cb[1]-ca[1])/dt)
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
                sp=float(np.hypot(*vv))
                if sp<MINSPD: continue
                ious=iou(GB[gi],P)
                j=int(np.argmax(ious))
                if ious[j]<0.5: continue
                pc=np.array([(P[j,0]+P[j,2])/2,(P[j,1]+P[j,3])/2])
                gc=np.array([(GB[gi,0]+GB[gi,2])/2,(GB[gi,1]+GB[gi,3])/2])
                u=np.array(vv)/sp
                epar=float(np.dot(pc-gc,u)); eperp=float(np.cross(u,pc-gc))
                gw=float(GB[gi,2]-GB[gi,0]); gh=float(GB[gi,3]-GB[gi,1])
                rows.append((epar, eperp, sp, float(ious[j]), np.sqrt(gw*gh)))   # px,px,px/s,-,px
    if (si+1)%10==0: print(f"  {si+1} seqs, {len(rows)} matches", flush=True)

A=np.array(rows)
epar,eperp,sp,io,bs=A.T
print(f"\nMATCHES {len(A)}   median speed {np.median(sp):.1f} px/s   median IoU {np.median(io):.3f}")

# --- ratio estimator, the one the reviewers warned about ---------------------
d=epar/sp*1e3
print("RATIO ESTIMATOR  delta = e_par/|v|  (divergent variance at small |v|)")
print(f"  mean {d.mean():+.3f} ms   median {np.median(d):+.3f} ms   SE {d.std(ddof=1)/np.sqrt(len(d)):.3f}")

# --- regression WITH an intercept: e_par = b + tau |v| ------------------------
# Forcing the fit through the origin absorbs any fixed spatial bias b into the slope.
# The detector has one (mean along-track residual is not zero), so b must be fitted.
def fit2(x,y):
    X=np.column_stack([np.ones_like(x),x])
    c,*_=np.linalg.lstsq(X,y,rcond=None)
    r=y-X@c; dof=max(len(x)-2,1)
    cov=np.sum(r*r)/dof*np.linalg.inv(X.T@X)
    return c[0],float(np.sqrt(cov[0,0])),c[1],float(np.sqrt(cov[1,1]))
b0,sb0,b1,sb1=fit2(sp,epar)
print("REGRESSION WITH INTERCEPT  e_par = b + tau |v|")
print(f"  fixed spatial bias b = {b0:+.4f} px   SE {sb0:.4f}   -> {abs(b0)/sb0:.1f} SE")
print(f"  tau = {b1*1e3:+.3f} ms   SE {sb1*1e3:.3f} ms   -> {abs(b1)/sb1:.1f} SE from zero")
c0,sc0,c1,sc1=fit2(sp,eperp)
print(f"  cross-track: b = {c0:+.4f} px (SE {sc0:.4f}), slope = {c1*1e3:+.3f} ms (SE {sc1*1e3:.3f})"
      f"  -> slope {abs(c1)/sc1:.1f} SE")
# --- control for box size: e_par = b + tau|v| + c*size ------------------------
X=np.column_stack([np.ones_like(sp),sp,bs])
c,*_=np.linalg.lstsq(X,epar,rcond=None)
r=epar-X@c; dof=max(len(sp)-3,1)
cov=np.sum(r*r)/dof*np.linalg.inv(X.T@X)
se_=np.sqrt(np.diag(cov))
print("WITH BOX SIZE AS A THIRD REGRESSOR  e_par = b + tau|v| + c*sqrt(area)")
print(f"  b   = {c[0]:+.4f} px  SE {se_[0]:.4f}")
print(f"  tau = {c[1]*1e3:+.3f} ms  SE {se_[1]*1e3:.3f}  -> {abs(c[1])/se_[1]:.1f} SE")
print(f"  c   = {c[2]:+.5f} px/px SE {se_[2]:.5f}  -> {abs(c[2])/se_[2]:.1f} SE")
print(f"  correlation(|v|, box size) = {np.corrcoef(sp,bs)[0,1]:+.3f}")
Xc=np.column_stack([np.ones_like(sp),sp,bs]); cc,*_=np.linalg.lstsq(Xc,eperp,rcond=None)
rc=eperp-Xc@cc; covc=np.sum(rc*rc)/dof*np.linalg.inv(Xc.T@Xc); sec=np.sqrt(np.diag(covc))
print(f"  cross-track slope {cc[1]*1e3:+.3f} ms SE {sec[1]*1e3:.3f} -> {abs(cc[1])/sec[1]:.1f} SE")
print("  by speed tercile, intercept fitted within each:")
q=np.percentile(sp,[0,33,67,100])
for i in range(3):
    m=(sp>=q[i])&(sp<=q[i+1])
    if m.sum()<40: continue
    a0,sa0,a1,sa1=fit2(sp[m],epar[m])
    print(f"    v in [{q[i]:5.1f},{q[i+1]:6.1f}) n={m.sum():>4}  b={a0:+.3f} px  tau={a1*1e3:+8.3f} ms (SE {sa1*1e3:.3f})")
print(f"\nRESIDUAL OFFSETS (px, should be ~0 if the model is unbiased in space)")
print(f"  along-track mean {epar.mean():+.4f} px    cross-track mean {eperp.mean():+.4f} px")
import json
json.dump(dict(n=int(len(A)),ratio_mean_ms=float(d.mean()),ratio_median_ms=float(np.median(d)),
               bias_px=float(b0),bias_se=float(sb0),tau_ms=float(b1*1e3),tau_se_ms=float(sb1*1e3),
               cross_bias_px=float(c0),cross_slope_ms=float(c1*1e3),cross_slope_se_ms=float(sc1*1e3),
               along_px=float(epar.mean()),cross_px=float(eperp.mean()),
               median_speed=float(np.median(sp))),
          open('/work/experiments/e21_effective_output_time/result.json','w'),indent=1)
print("WROTE")
