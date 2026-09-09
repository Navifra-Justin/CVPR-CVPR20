"""E37 - what does the interval cost on the benchmark's own metric?

Every measurement so far describes a property. None of them moves a number anyone
reports, and that is the objection an accepted paper in this genre has to answer: the
label-leakage and metric-bias audits of recent CVPR all end on a score that changes.

The question this asks is the benchmark's own: if the detector's output describes the
state at some instant t + delta rather than at the label instant, then scoring it against
the ground truth displaced to t + delta should score better. Sweeping delta and reading
the argmax gives an estimate of the output time from average precision itself, by an
argmax rather than a slope, and the height of the curve at delta = -24.94 ms gives what
the evidence-to-output interval is worth in mAP.

Ground truth is displaced, not the detections. Every ground-truth box has a track velocity
from its own labels; detections do not, and using a matched box's velocity to move a
detection would be circular. Displacing the ground truth by +delta*v scores the released
predictions against the state the object occupied delta later, which is exactly the
quantity in question, and it leaves the detector untouched.

This dumps every detection and every ground-truth box once, then sweeps offline.
"""
import sys, os, glob, numpy as np, torch, h5py, hdf5plugin
sys.path.insert(0,'/work/src/RVT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector
from models.detection.yolox.utils.boxes import postprocess

DEV=os.environ.get('DEV','cuda:0'); NSEQ=int(os.environ.get('NSEQ','1000'))
OUT=os.environ.get('OUT','/work/experiments/e37_map/dets.npz')
CONF=0.01; NMS=0.65; WARM=20; LINK_IOU=0.3
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

def iou1(a,B):
    x1=np.maximum(a[0],B[:,0]); y1=np.maximum(a[1],B[:,1])
    x2=np.minimum(a[2],B[:,2]); y2=np.minimum(a[3],B[:,3])
    w=np.clip(x2-x1,0,None); h=np.clip(y2-y1,0,None); it=w*h
    return it/np.maximum((a[2]-a[0])*(a[3]-a[1])+(B[:,2]-B[:,0])*(B[:,3]-B[:,1])-it,1e-9)

DET=[]   # frame_id, x1,y1,x2,y2, score, cls
GT =[]   # frame_id, x1,y1,x2,y2, cls, vx, vy   (vx,vy NaN when no centered velocity)
fid=0
for si,sd in enumerate(sorted(glob.glob('/work/data/gen1x/gen1/val/*'))[:NSEQ]):
    rd=os.path.join(sd,'event_representations_v2','stacked_histogram_dt=50_nbins=10')
    try:
        L=np.load(os.path.join(sd,'labels_v2','labels.npz'))['labels']
        o2r=np.load(os.path.join(rd,'objframe_idx_2_repr_idx.npy'))
    except Exception: continue
    if len(o2r)<3: continue
    ts=np.sort(np.unique(L['t'])); B=[];C=[];CL=[]
    for t in ts:
        G=L[L['t']==t]
        bb=np.column_stack([G['x'],G['y'],G['x']+G['w'],G['y']+G['h']]).astype(float)
        B.append(bb); C.append(np.column_stack([(bb[:,0]+bb[:,2])/2,(bb[:,1]+bb[:,3])/2]))
        CL.append(np.asarray(G['class_id']))
    fwd=[]
    for k in range(len(ts)-1):
        m=-np.ones(len(B[k]),dtype=int)
        for i in range(len(B[k])):
            same=(CL[k][i]==CL[k+1])
            if not same.any(): continue
            io=np.where(same,iou1(B[k][i],B[k+1]),0.0); j=int(np.argmax(io))
            if io[j]>=LINK_IOU: m[i]=j
        fwd.append(m)
    fwd.append(-np.ones(len(B[-1]),dtype=int))
    prev=[-np.ones(len(B[k]),dtype=int) for k in range(len(ts))]
    for k in range(len(ts)-1):
        for i,j in enumerate(fwd[k]):
            if j>=0: prev[k+1][j]=i
    with h5py.File(os.path.join(rd,'event_representations.h5'),'r') as f:
        D=f[list(f.keys())[0]]
        start=max(int(o2r[0])-WARM,0); stop=min(int(o2r[-1])+1,D.shape[0])
        want={int(o2r[i]):i for i in range(min(len(o2r),len(ts)))}
        states=None
        for ri in range(start,stop):
            x=torch.from_numpy(D[ri][None]).float()
            x=torch.nn.functional.pad(x,(0,320-x.shape[-1],0,256-x.shape[-2])).to(DEV)
            with torch.no_grad():
                out,_,states=mdl.forward(x,previous_states=states)
            if ri not in want: continue
            k=want[ri]
            det=postprocess(out.clone(),2,CONF,NMS)[0]
            if det is not None:
                d=det.cpu().numpy()
                sc=d[:,4]*d[:,5]
                for r in range(len(d)):
                    DET.append((fid,d[r,0],d[r,1],d[r,2],d[r,3],sc[r],d[r,6]))
            for gi in range(len(B[k])):
                jf=fwd[k][gi]; jb=prev[k][gi]
                if jf>=0 and jb>=0:
                    dt=(ts[k+1]-ts[k-1])*1e-6
                    vx,vy=(C[k+1][jf]-C[k-1][jb])/dt
                else: vx=vy=np.nan
                GT.append((fid,B[k][gi,0],B[k][gi,1],B[k][gi,2],B[k][gi,3],CL[k][gi],vx,vy))
            fid+=1
    if (si+1)%25==0: print(f"  {si+1} seqs, {fid} frames, {len(DET)} dets, {len(GT)} gt",flush=True)

os.makedirs(os.path.dirname(OUT),exist_ok=True)
np.savez_compressed(OUT,det=np.array(DET,dtype=np.float32),gt=np.array(GT,dtype=np.float32))
print(f"\nWROTE {OUT}  frames {fid}  dets {len(DET)}  gt {len(GT)}")
print(f"  gt with a centered velocity: {int(np.isfinite(np.array(GT,dtype=float)[:,6]).sum())}")
