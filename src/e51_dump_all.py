"""E51 - dump detections for every released checkpoint under one identical protocol.

External review #7 named the one thing the paper does not yet show: whether the temporal
support it measures changes a benchmark CONCLUSION rather than merely existing inside one
detector. That question is about comparison, so it needs more than one detector scored the
same way.

This dumps detections for all five released Gen1 checkpoints over the same validation
sequences, the same frames, the same confidence threshold and the same NMS, so the only
thing that differs between the dumps is the network. Ground truth is emitted identically by
every run and is checked to be identical afterwards; it carries each box's centered label
velocity so the offline sweep can displace it by delta*v.

Calling convention per family, each the one its own release uses:
  rvt  - one window per call, recurrent state carried across calls
  ssm  - non-overlapping chunks of sequence_length windows with the detection head applied
         per position, and chunk starts placed as sequence_for_streaming.py places them,
         because in that release a frame's history depends on its position in the chunk
         (experiments/e47_ssm/README.md)
"""
import sys, os, glob, numpy as np, torch, h5py, hdf5plugin
FAM=os.environ.get('FAM','rvt'); TAG=os.environ.get('TAG','t')
DEV=os.environ.get('DEV','cuda:0'); NSEQ=int(os.environ.get('NSEQ','1000'))
CHUNK=int(os.environ.get('CHUNK','21'))          # SSM-ViT gen1 sequence_length
# E60: move every chunk boundary LATER by SHIFT windows. The release uses SHIFT=0. Any other
# value rotates every labelled frame's position by -SHIFT mod CHUNK, giving it a different
# amount of history under an otherwise identical protocol, which is what turns the
# chunk-position comparison into a paired one on identical frames. The position each frame
# actually received is recorded in the dump, so nothing downstream has to re-derive it, and
# src/e60_verify_shift.py checks the re-assignment from the index files with no GPU.
SHIFT=int(os.environ.get('SHIFT','0'))
NAME=(f'rvt-{TAG}' if FAM=='rvt' else f's5vit-{TAG}')
OUT=os.environ.get('OUT',f'/work/experiments/e51_ranking/dets-{NAME}.npz')
sys.path.insert(0,'/work/src/SSMViT' if FAM=='ssm' else '/work/src/RVT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector
from models.detection.yolox.utils.boxes import postprocess
CONF=0.01; NMS=0.65; WARM=20; LINK_IOU=0.3

R='/work/src/SSMViT/config/model' if FAM=='ssm' else '/work/src/RVT/config/model'
base=OmegaConf.load(f'{R}/base.yaml'); rnn=OmegaConf.load(f'{R}/rnndet.yaml')
mx  =OmegaConf.load(f'{R}/maxvit_yolox/default.yaml')['model']
cfg =OmegaConf.merge(base.get('model',base),rnn,mx)
if FAM=='ssm':
    cfg=OmegaConf.merge(cfg,OmegaConf.load(
        f'/work/src/SSMViT/config/experiment/gen1/{TAG}.yaml')['model'])
    CK=f'/work/data/ckpt/s5vit-{TAG}-gen1.ckpt'
else:
    C={'t':(32,32,0.33),'s':(48,24,0.33),'b':(64,32,0.67)}[TAG]
    with open_dict(cfg):
        cfg.backbone.embed_dim=C[0]; cfg.backbone.stage.attention.dim_head=C[1]
        cfg.fpn.depth=C[2]
    CK=f'/work/data/ckpt/rvt-{TAG}-gen1.ckpt'
with open_dict(cfg):
    cfg.backbone.in_res_hw=[256,320]; cfg.backbone.stage.attention.partition_size=[4,5]
    cfg.head.num_classes=2
mdl=YoloXDetector(cfg)
sd_=torch.load(CK,map_location='cpu',weights_only=False)['state_dict']
mdl.load_state_dict({k[4:]:v for k,v in sd_.items() if k.startswith('mdl.')},strict=True)
mdl.eval().to(DEV)
print(f"{NAME}: {sum(p.numel() for p in mdl.parameters())/1e6:.2f}M params, "
      f"{'chunks of %d'%CHUNK if FAM=='ssm' else 'one window per call'}",flush=True)

def pad(t): return torch.nn.functional.pad(t,(0,320-t.shape[-1],0,256-t.shape[-2]))
def iou1(a,B):
    x1=np.maximum(a[0],B[:,0]); y1=np.maximum(a[1],B[:,1])
    x2=np.minimum(a[2],B[:,2]); y2=np.minimum(a[3],B[:,3])
    w=np.clip(x2-x1,0,None); h=np.clip(y2-y1,0,None); it=w*h
    return it/np.maximum((a[2]-a[0])*(a[3]-a[1])+(B[:,2]-B[:,0])*(B[:,3]-B[:,1])-it,1e-9)

DET=[]; GT=[]; POS=[]; fid=0
for si,sd in enumerate(sorted(glob.glob('/work/data/gen1x/gen1/val/*'))[:NSEQ]):
    rd=os.path.join(sd,'event_representations_v2','stacked_histogram_dt=50_nbins=10')
    try:
        L=np.load(os.path.join(sd,'labels_v2','labels.npz'))['labels']
        o2r=np.load(os.path.join(rd,'objframe_idx_2_repr_idx.npy'))
    except Exception: continue
    if len(o2r)<3: continue
    posmap={}
    ts=np.sort(np.unique(L['t'])); B=[];C=[];CL=[]
    for t in ts:
        G=L[L['t']==t]
        bb=np.column_stack([G['x'],G['y'],G['x']+G['w'],G['y']+G['h']]).astype(float)
        B.append(bb); C.append(np.column_stack([(bb[:,0]+bb[:,2])/2,(bb[:,1]+bb[:,3])/2]))
        CL.append(np.asarray(G['class_id']))
    # E37's construction, verbatim: greedy FORWARD links, then inverted to give the
    # predecessor. Matching backwards independently disagrees on 193 of 40,698 boxes and
    # would score these models against a different ground truth than the paper reports.
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
        want={int(o2r[i]):i for i in range(min(len(o2r),len(ts)))}
        stop=min(int(o2r[-1])+1,D.shape[0])
        if FAM=='rvt':
            start=max(int(o2r[0])-WARM,0)
            outs={}; states=None
            for ri in range(start,stop):
                x=pad(torch.from_numpy(D[ri][None]).float()).to(DEV)
                with torch.no_grad(): o,_,states=mdl.forward(x,previous_states=states)
                if ri in want: outs[ri]=o
        else:
            # chunk starts exactly where the released streaming dataset puts them, then
            # moved LATER by SHIFT. Later, not earlier: the release's own start is already
            # max(o2r[0]-20,0) and Gen1 labels begin early enough in most sequences that it
            # is pinned at 0, so subtracting SHIFT there would be a no-op. And not clamped
            # at o2r[0] either: 216 of the 406 validation sequences have their first label
            # below index SHIFT, and a clamp there would give those sequences a rotation of
            # o2r[0] instead of SHIFT. The price is the handful of labelled frames that then
            # sit before the first chunk; they get position -1 and no detections, and the
            # paired analysis drops them from both arms. src/e60_verify_shift.py checks all
            # of this from the index files before any GPU is claimed.
            start=max(int(o2r[0])-CHUNK+1,0)+SHIFT
            outs={}; states=None; posmap={}
            for c0 in range(start,stop,CHUNK):
                idx=list(range(c0,min(c0+CHUNK,stop)))
                if not idx: break
                xs=torch.stack([pad(torch.from_numpy(D[i][None]).float()) for i in idx]).to(DEV)
                with torch.no_grad():
                    feats,states=mdl.forward_backbone(xs,previous_states=states,train_step=False)
                    for p_,ri in enumerate(idx):
                        if ri in want:
                            outs[ri]=mdl.forward_detect({k:v[p_] for k,v in feats.items()})[0]
                            posmap[ri]=p_
        for ri in sorted(want):
            k=want[ri]
            o=outs.get(ri)
            if o is not None:
                det=postprocess(o.clone(),2,CONF,NMS)[0]
                if det is not None:
                    d=det.cpu().numpy(); sc=d[:,4]*d[:,5]
                    for r in range(len(d)):
                        DET.append((fid,d[r,0],d[r,1],d[r,2],d[r,3],sc[r],d[r,6]))
            for gi in range(len(B[k])):
                jf=fwd[k][gi]; jb=prev[k][gi]
                if jf>=0 and jb>=0:
                    dt=(ts[k+1]-ts[k-1])*1e-6
                    vx,vy=(C[k+1][jf]-C[k-1][jb])/dt
                else: vx=vy=np.nan
                GT.append((fid,B[k][gi,0],B[k][gi,1],B[k][gi,2],B[k][gi,3],CL[k][gi],vx,vy))
            POS.append(posmap.get(ri,-1))
            fid+=1
    if (si+1)%25==0: print(f"  {si+1} seqs, {fid} frames, {len(DET)} dets",flush=True)

os.makedirs(os.path.dirname(OUT),exist_ok=True)
np.savez_compressed(OUT,det=np.array(DET,dtype=np.float32),gt=np.array(GT,dtype=np.float32),
                    pos=np.array(POS,dtype=np.int16))
print(f"\nWROTE {OUT}  frames {fid}  dets {len(DET)}  gt {len(GT)}  shift {SHIFT}")
