import sys, os, glob, numpy as np, torch, h5py, hdf5plugin
sys.path.insert(0,'/work/src/RVT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector
from models.detection.yolox.utils.boxes import postprocess
base=OmegaConf.load('/work/src/RVT/config/model/base.yaml'); rnn=OmegaConf.load('/work/src/RVT/config/model/rnndet.yaml')
mx=OmegaConf.load('/work/src/RVT/config/model/maxvit_yolox/default.yaml')['model']
cfg=OmegaConf.merge(base.get('model',base),rnn,mx)
with open_dict(cfg):
    cfg.backbone.embed_dim=32; cfg.fpn.depth=0.33; cfg.backbone.in_res_hw=[256,320]
    cfg.backbone.stage.attention.partition_size=[4,5]; cfg.head.num_classes=2
mdl=YoloXDetector(cfg)
ck=torch.load('/work/data/ckpt/rvt-t-gen1.ckpt',map_location='cpu',weights_only=False)
mdl.load_state_dict({k[4:]:v for k,v in ck['state_dict'].items() if k.startswith('mdl.')},strict=True)
mdl.eval().cuda()
def iou(a,B):
    x1=np.maximum(a[0],B[:,0]); y1=np.maximum(a[1],B[:,1])
    x2=np.minimum(a[2],B[:,2]); y2=np.minimum(a[3],B[:,3])
    w=np.clip(x2-x1,0,None); h=np.clip(y2-y1,0,None); inter=w*h
    return inter/np.maximum((a[2]-a[0])*(a[3]-a[1])+(B[:,2]-B[:,0])*(B[:,3]-B[:,1])-inter,1e-9)
sd=sorted(glob.glob('/work/data/gen1x/gen1/val/*'))[0]
rd=os.path.join(sd,'event_representations_v2','stacked_histogram_dt=50_nbins=10')
L=np.load(os.path.join(sd,'labels_v2','labels.npz'))['labels']
o2r=np.load(os.path.join(rd,'objframe_idx_2_repr_idx.npy')); lts=np.unique(L['t'])
vel={}
for tid in np.unique(L['track_id']):
    s=np.sort(L[L['track_id']==tid],order='t')
    if len(s)<2: continue
    t=s['t'].astype(float)*1e-6; cx=s['x']+s['w']/2.0; cy=s['y']+s['h']/2.0
    for i in range(len(s)-1):
        dt=t[i+1]-t[i]
        if dt>0: vel[(int(tid),int(s['t'][i]))]=((cx[i+1]-cx[i])/dt,(cy[i+1]-cy[i])/dt)
print("velocity entries:",len(vel))
sp_all=[np.hypot(*v) for v in vel.values()]
print("speed px/s: p10 %.1f med %.1f p90 %.1f"%(np.percentile(sp_all,10),np.median(sp_all),np.percentile(sp_all,90)))
want={int(o2r[i]):int(lts[i]) for i in range(min(len(o2r),len(lts)))}
cnt=dict(frames=0,det_none=0,gt0=0,novel=0,slow=0,lowiou=0,ok=0)
with h5py.File(os.path.join(rd,'event_representations.h5'),'r') as f:
    D=f['data']; states=None
    start=max(int(o2r[0])-20,0); stop=min(int(o2r[-1])+1,D.shape[0])
    for i in range(start,stop):
        x=torch.from_numpy(D[i][None]).float()
        x=torch.nn.functional.pad(x,(0,320-x.shape[-1],0,256-x.shape[-2])).cuda()
        with torch.no_grad(): out,_,states=mdl.forward(x,previous_states=states)
        if i not in want: continue
        cnt['frames']+=1
        det=postprocess(out.clone(),2,0.1,0.45)[0]
        if det is None: cnt['det_none']+=1; continue
        P=det[:,:4].cpu().numpy()
        lt=want[i]; G=L[L['t']==lt]
        if not len(G): cnt['gt0']+=1; continue
        GB=np.column_stack([G['x'],G['y'],G['x']+G['w'],G['y']+G['h']]).astype(float)
        for gi in range(len(GB)):
            vv=vel.get((int(G['track_id'][gi]),int(lt)))
            if vv is None: cnt['novel']+=1; continue
            if np.hypot(*vv)<20.0: cnt['slow']+=1; continue
            io=iou(GB[gi],P)
            if io.max()<0.5: cnt['lowiou']+=1; continue
            cnt['ok']+=1
print(cnt)
