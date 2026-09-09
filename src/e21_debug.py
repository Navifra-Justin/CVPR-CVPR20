import sys, os, glob, numpy as np, torch, h5py, hdf5plugin
sys.path.insert(0,'/work/src/RVT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector
from models.detection.yolox.utils.boxes import postprocess
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
mdl.eval().cuda()
sd=sorted(glob.glob('/work/data/gen1x/gen1/val/*'))[0]
rd=os.path.join(sd,'event_representations_v2','stacked_histogram_dt=50_nbins=10')
L=np.load(os.path.join(sd,'labels_v2','labels.npz'))['labels']
o2r=np.load(os.path.join(rd,'objframe_idx_2_repr_idx.npy'))
lts=np.unique(L['t'])
print("o2r[:5]",o2r[:5],"lts[:5]",lts[:5],"n_labels",len(L))
print("h5 files:", os.listdir(rd))
h5p=[p for p in glob.glob(os.path.join(rd,'*.h5'))]
print("h5 path:",h5p)
with h5py.File(h5p[0],'r') as f:
    k=list(f.keys())[0]; D=f[k]
    print("dataset",k,D.shape,D.dtype)
    states=None
    for i in range(max(int(o2r[0])-20,0), int(o2r[0])+1):
        x=torch.from_numpy(D[i][None]).float()
        x=torch.nn.functional.pad(x,(0,320-x.shape[-1],0,256-x.shape[-2])).cuda()
        with torch.no_grad(): out,_,states=mdl.forward(x,previous_states=states)
    print("out shape",tuple(out.shape),"obj-conf min/max",float(out[0,:,4].min()),float(out[0,:,4].max()))
    for c in (0.5,0.3,0.1,0.05,0.01):
        d=postprocess(out.clone(),2,c,0.45)[0]
        print(f"  conf={c}: {0 if d is None else len(d)} det")
    d=postprocess(out.clone(),2,0.01,0.45)[0]
    if d is not None: print("  sample det:",[round(float(v),2) for v in d[0].tolist()])
    G=L[L['t']==lts[0]]
    print("  GT n=",len(G), "first:", G[0] if len(G) else None)
