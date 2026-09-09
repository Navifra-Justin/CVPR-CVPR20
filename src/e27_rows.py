"""E27 - one pass over gen1 val that saves the RAW per-match row table.

E21 and E24 each ran the detector and then threw the rows away, keeping only fitted
coefficients. That made the two disagree (tau = +11.9 ms vs +52.7 ms) with no way to
find out why without another GPU pass. It also hid two estimator defects that a
checklist audit and an external review both reached independently:

  (a) E24 fitted np.abs(epar) and np.abs(eperp). E[|eps + tau*v|] is not
      E[|eps|] + tau*v, so a magnitude slope does not identify a temporal offset.
  (b) E24's acceleration regressor was |dv|/dt, a magnitude. A first-order
      extrapolation cost is (1/2) a tau^2 ALONG travel and needs a signed a_par.
      A non-negative regressor correlated with speed (r = +0.36) instead moves the
      speed coefficient, which is exactly the 11.9 -> 52.7 ms gap.

There is a third defect neither caught: velocity was taken from the forward interval
only, so it estimates v(t) + a*dt/2, not v(t).

This script fixes none of those inline. It records the raw quantities - the residual
vector, the forward and backward inter-label displacements, the box, the match quality -
and leaves every projection, every derived regressor and every model choice to a CPU
script that can be re-run in seconds. Nothing here is a fit.
"""
import sys, os, glob, numpy as np, torch, h5py, hdf5plugin
sys.path.insert(0,'/work/src/RVT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector
from models.detection.yolox.utils.boxes import postprocess

DEV=os.environ.get('DEV','cuda:0'); NSEQ=int(os.environ.get('NSEQ','1000'))
OUT=os.environ.get('OUT','/work/experiments/e27_rows/rows.npz')
CONF=0.1; NMS=0.45; WARM=20
LINK_IOU=0.3      # track linking threshold between adjacent label times
MATCH_IOU=0.3     # detection<->gt threshold; recorded, so it can be raised offline

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

COLS=['seq','t_us','k','gi','cls','iou',
      'dx','dy',                 # detection centre minus label centre, px
      'fx','fy','dt_f',          # forward displacement to the next label time, px and s
      'bx','by','dt_b',          # backward displacement from the previous label time
      'gw','gh','gcx','gcy']     # label box
rows=[]
seqs=sorted(glob.glob('/work/data/gen1x/gen1/val/*'))[:NSEQ]
for si,sd in enumerate(seqs):
    rd=os.path.join(sd,'event_representations_v2','stacked_histogram_dt=50_nbins=10')
    try:
        L=np.load(os.path.join(sd,'labels_v2','labels.npz'))['labels']
        o2r=np.load(os.path.join(rd,'objframe_idx_2_repr_idx.npy'))
    except Exception: continue
    if len(o2r)<3: continue
    ts=np.sort(np.unique(L['t']))
    # per label time: boxes as corner arrays and centres
    B=[]; C=[]; CL=[]
    for t in ts:
        G=L[L['t']==t]
        bb=np.column_stack([G['x'],G['y'],G['x']+G['w'],G['y']+G['h']]).astype(float)
        B.append(bb); C.append(np.column_stack([(bb[:,0]+bb[:,2])/2,(bb[:,1]+bb[:,3])/2]))
        CL.append(np.asarray(G['class_id']))
    # forward links by greedy same-class IoU
    fwd=[]
    for k in range(len(ts)-1):
        m=-np.ones(len(B[k]),dtype=int)
        for i in range(len(B[k])):
            same=(CL[k][i]==CL[k+1])
            if not same.any(): continue
            io=np.where(same,iou1(B[k][i],B[k+1]),0.0)
            j=int(np.argmax(io))
            if io[j]>=LINK_IOU: m[i]=j
        fwd.append(m)
    fwd.append(-np.ones(len(B[-1]),dtype=int))
    # backward predecessor implied by the forward map
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
            if det is None: continue
            P=det[:,:4].cpu().numpy()
            for gi in range(len(B[k])):
                io=iou1(B[k][gi],P); j=int(np.argmax(io))
                if io[j]<MATCH_IOU: continue
                pc=np.array([(P[j,0]+P[j,2])/2,(P[j,1]+P[j,3])/2])
                gc=C[k][gi]
                jf=fwd[k][gi] if k<len(ts) else -1
                jb=prev[k][gi]
                if jf>=0: fx,fy=C[k+1][jf]-gc; dtf=(ts[k+1]-ts[k])*1e-6
                else:     fx=fy=np.nan; dtf=np.nan
                if jb>=0: bx,by=gc-C[k-1][jb]; dtb=(ts[k]-ts[k-1])*1e-6
                else:     bx=by=np.nan; dtb=np.nan
                rows.append((si,float(ts[k]),k,gi,float(CL[k][gi]),float(io[j]),
                             float(pc[0]-gc[0]),float(pc[1]-gc[1]),
                             fx,fy,dtf, bx,by,dtb,
                             float(B[k][gi,2]-B[k][gi,0]),float(B[k][gi,3]-B[k][gi,1]),
                             float(gc[0]),float(gc[1])))
    if (si+1)%25==0: print(f"  {si+1}/{len(seqs)} seqs, {len(rows)} rows",flush=True)

A=np.array(rows,dtype=float)
os.makedirs(os.path.dirname(OUT),exist_ok=True)
np.savez_compressed(OUT,rows=A,cols=np.array(COLS))
print(f"\nWROTE {OUT}  shape {A.shape}  sequences {len(np.unique(A[:,0]))}")
print("  with forward velocity :",int(np.isfinite(A[:,8]).sum()))
print("  with both directions  :",int((np.isfinite(A[:,8])&np.isfinite(A[:,11])).sum()))
