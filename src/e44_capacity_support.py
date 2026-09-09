"""E44 - the newest-window influence centroid and the recurrent support, per capacity.

Everything on the predictor side was measured on rvt-t. RVT releases three capacities for
Gen1 that differ only in embed_dim, attention dim_head and FPN depth, so the same
measurement runs on each without changing dataset, representation, evaluation code or the
window the release fixes. If the newest window's centroid and the share of influence it
carries are the same across 4.41M, 9.87M and 18.54M parameters, they are properties of the
released configuration rather than of one trained checkpoint.

Three quantities per capacity, identical to E17/E34 and E42:
  (a) the per-bin occlusion influence of the newest window, and its centroid
  (b) the whole-window influence at each lag back to 1 s, with the state propagating
  (c) the change when the recurrent state is zeroed, against removing the newest window
"""
import sys, os, glob, json, numpy as np, torch, h5py, hdf5plugin
sys.path.insert(0,'/work/src/RVT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector

TAG=os.environ.get('TAG','t'); DEV=os.environ.get('DEV','cuda:0')
NSEQ=int(os.environ.get('NSEQ','12')); NSAMP=int(os.environ.get('NSAMP','40'))
WARM=8; KLAG=int(os.environ.get('KLAG','19'))
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
print(f"rvt-{TAG}: {sum(p.numel() for p in mdl.parameters())/1e6:.2f}M params",flush=True)

def clone_states(st):
    if st is None: return None
    if torch.is_tensor(st): return st.detach().clone()
    if isinstance(st,(list,tuple)): return type(st)(clone_states(x) for x in st)
    return st
def pad(t): return torch.nn.functional.pad(t,(0,320-t.shape[-1],0,256-t.shape[-2]))

BIN=[[] for _ in range(10)]
W=[[] for _ in range(KLAG+1)]
RESET=[]
for si,sd in enumerate(sorted(glob.glob('/work/data/gen1x/gen1/val/*'))[:NSEQ]):
    h5=os.path.join(sd,'event_representations_v2','stacked_histogram_dt=50_nbins=10',
                    'event_representations.h5')
    if not os.path.exists(h5): continue
    with h5py.File(h5,'r') as f:
        D=f[list(f.keys())[0]]
        n=min(D.shape[0],WARM+NSAMP+KLAG)
        X=[pad(torch.from_numpy(np.asarray(D[i],dtype=np.float32))[None]).to(DEV)
           for i in range(n)]
        st=None; pre=[]; ref=[]
        for i in range(n):
            pre.append(clone_states(st))
            with torch.no_grad(): o,_,st=mdl.forward(X[i],previous_states=st)
            ref.append(o.detach())
        for i in range(max(WARM,KLAG),n):
            rn=float(ref[i].norm())
            if rn<1e-6: continue
            # (a) per-bin influence of the newest window, state held fixed
            for b in range(10):
                xm=X[i].clone(); xm[:,2*b:2*b+2]=0
                with torch.no_grad(): o2,_,_=mdl.forward(xm,previous_states=pre[i])
                BIN[b].append(float((o2-ref[i]).norm())/rn)
            # (b) whole-window influence at each lag, state propagating
            for L in range(KLAG+1):
                j=i-L; s2=clone_states(pre[j])
                for k in range(j,i+1):
                    xin=torch.zeros_like(X[k]) if k==j else X[k]
                    with torch.no_grad(): o2,_,s2=mdl.forward(xin,previous_states=s2)
                W[L].append(float((o2-ref[i]).norm())/rn)
            # (c) no history at all
            with torch.no_grad(): o3,_,_=mdl.forward(X[i],previous_states=None)
            RESET.append(float((o3-ref[i]).norm())/rn)
    print(f"  seq {si+1}, {len(RESET)} samples",flush=True)

bc=np.array([-(50-5*b-2.5) for b in range(10)])
bm=np.array([np.mean(v) for v in BIN])
bcen=float(((bm/bm.sum())*bc).sum()); bcv=float(bm.std()/bm.mean())
lag=np.array([-(25.0+50.0*L) for L in range(KLAG+1)])
lm=np.array([np.mean(v) for v in W])
def cen(n):
    w=lm[:n]/lm[:n].sum(); return float((w*lag[:n]).sum()), float(100*w[0])
c10,s10=cen(10); c20,s20=cen(KLAG+1)
print(f"\nrvt-{TAG}  samples {len(RESET)}")
print(f"  newest-window centroid   {bcen:+.2f} ms   CV over bins {bcv:.4f}")
print(f"  support centroid, 500 ms {c10:+.1f} ms   newest share {s10:.1f} %")
print(f"  support centroid, {50*(KLAG+1)} ms {c20:+.1f} ms   newest share {s20:.1f} %")
print(f"  zeroing the state        {np.mean(RESET):.4f}   newest window alone {lm[0]:.4f}"
      f"   ratio {np.mean(RESET)/max(lm[0],1e-9):.2f}")
os.makedirs('/work/experiments/e44_capacity',exist_ok=True)
json.dump(dict(tag=TAG,n=len(RESET),params_M=float(sum(p.numel() for p in mdl.parameters())/1e6),
               bin_centres=[float(v) for v in bc],bin_influence=[float(v) for v in bm],
               bin_centroid_ms=bcen,bin_cv=bcv,
               lag_ms=[float(v) for v in lag],lag_influence=[float(v) for v in lm],
               centroid500=c10,share500=s10,centroid1000=c20,share1000=s20,
               reset=float(np.mean(RESET)),newest=float(lm[0]),
               reset_ratio=float(np.mean(RESET)/max(lm[0],1e-9))),
          open(f'/work/experiments/e44_capacity/rvt-{TAG}.json','w'),indent=1)
print("WROTE")
