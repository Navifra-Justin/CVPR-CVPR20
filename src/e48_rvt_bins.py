"""E48 - the RVT bin arm on the same frames E47 uses, so the architectures are comparable.

E44 measured rvt-s and rvt-b with KLAG=19, so its samples begin at frame 19; E45 and E47's
bin arm begin at frame 8. A 0.03 ms difference between E45's rvt-t and E44's rvt-t is
already attributable to that. To compare a ConvLSTM against an S5 layer, the frames have to
be the same, so this runs RVT's three capacities through the bin arm alone on E47's frames.

Zero fill only, with the recurrent state entering the step, which is E45's zero arm.
"""
import sys, os, glob, json, numpy as np, torch, h5py, hdf5plugin
sys.path.insert(0,'/work/src/RVT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector

TAG=os.environ.get('TAG','t'); DEV=os.environ.get('DEV','cuda:0')
NSEQ=int(os.environ.get('NSEQ','12')); NSAMP=int(os.environ.get('NSAMP','40')); WARM=8
CFG={'t':dict(embed_dim=32,dim_head=32,fpn=0.33),
     's':dict(embed_dim=48,dim_head=24,fpn=0.33),
     'b':dict(embed_dim=64,dim_head=32,fpn=0.67)}[TAG]
base=OmegaConf.load('/work/src/RVT/config/model/base.yaml')
rnn =OmegaConf.load('/work/src/RVT/config/model/rnndet.yaml')
mx  =OmegaConf.load('/work/src/RVT/config/model/maxvit_yolox/default.yaml')['model']
cfg =OmegaConf.merge(base.get('model',base),rnn,mx)
with open_dict(cfg):
    cfg.backbone.embed_dim=CFG['embed_dim']; cfg.fpn.depth=CFG['fpn']
    cfg.backbone.stage.attention.dim_head=CFG['dim_head']
    cfg.backbone.in_res_hw=[256,320]; cfg.backbone.stage.attention.partition_size=[4,5]
    cfg.head.num_classes=2
mdl=YoloXDetector(cfg)
ck=torch.load(f'/work/data/ckpt/rvt-{TAG}-gen1.ckpt',map_location='cpu',weights_only=False)
mdl.load_state_dict({k[4:]:v for k,v in ck['state_dict'].items() if k.startswith('mdl.')},strict=True)
mdl.eval().to(DEV)
NP=sum(p.numel() for p in mdl.parameters())/1e6
print(f"rvt-{TAG}: {NP:.2f}M params",flush=True)
def clone_states(st):
    if st is None: return None
    if torch.is_tensor(st): return st.detach().clone()
    if isinstance(st,(list,tuple)): return type(st)(clone_states(x) for x in st)
    return st
def pad(t): return torch.nn.functional.pad(t,(0,320-t.shape[-1],0,256-t.shape[-2]))
BIN=[[] for _ in range(10)]
for si,sd in enumerate(sorted(glob.glob('/work/data/gen1x/gen1/val/*'))[:NSEQ]):
    h5=os.path.join(sd,'event_representations_v2','stacked_histogram_dt=50_nbins=10',
                    'event_representations.h5')
    if not os.path.exists(h5): continue
    with h5py.File(h5,'r') as f:
        D=f[list(f.keys())[0]]; n=min(D.shape[0],WARM+NSAMP)
        X=[pad(torch.from_numpy(np.asarray(D[i],dtype=np.float32))[None]).to(DEV)
           for i in range(n)]
        st=None; pre=[]; ref=[]
        for i in range(n):
            pre.append(clone_states(st))
            with torch.no_grad(): o,_,st=mdl.forward(X[i],previous_states=st)
            ref.append(o.detach())
        for i in range(WARM,n):
            rn=float(ref[i].norm())
            if rn<1e-6: continue
            for b in range(10):
                xm=X[i].clone(); xm[:,2*b:2*b+2]=0
                with torch.no_grad(): o2,_,_=mdl.forward(xm,previous_states=pre[i])
                BIN[b].append(float((o2-ref[i]).norm())/rn)
    print(f"  seq {si+1}, {len(BIN[0])} samples",flush=True)
bc=np.array([-(50-5*b-2.5) for b in range(10)])
P=np.array(BIN).T                     # samples x bins
bm=P.mean(0)
bcen=float(((bm/bm.sum())*bc).sum()); bcv=float(bm.std()/bm.mean())
rr=np.random.default_rng(1); bs=[]
for _ in range(4000):
    ii=rr.integers(0,len(P),len(P)); m=P[ii].mean(0); bs.append(((m/m.sum())*bc).sum())
print(f"\nrvt-{TAG}  samples {len(P)}")
print(f"  newest-window centroid {bcen:+.3f} ms   CV {bcv:.4f}   boot SE {np.std(bs):.3f}")
print(f"  halves {100*bm[:5].sum()/bm.sum():.1f} / {100*bm[5:].sum()/bm.sum():.1f} %"
      f"   max/min {bm.max()/bm.min():.2f}")
os.makedirs('/work/experiments/e48_matched_frames',exist_ok=True)
json.dump(dict(tag=f'rvt-{TAG}',arch='RVT (ConvLSTM)',n=int(len(P)),params_M=float(NP),
               bin_centres=[float(v) for v in bc],bin_influence=[float(v) for v in bm],
               bin_sem=[float(v) for v in P.std(0,ddof=1)/np.sqrt(len(P))],
               bin_centroid_ms=bcen,bin_cv=bcv,boot_se=float(np.std(bs)),
               half_older=float(100*bm[:5].sum()/bm.sum()),
               half_newer=float(100*bm[5:].sum()/bm.sum()),
               max_over_min=float(bm.max()/bm.min())),
          open(f'/work/experiments/e48_matched_frames/rvt-{TAG}.json','w'),indent=1)
print("WROTE")
