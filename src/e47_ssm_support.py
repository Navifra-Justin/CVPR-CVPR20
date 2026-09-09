"""E47 - the same predictor-side measurement on a second architecture.

Every predictor-side number in the paper is RVT, whose temporal operator is a per-stage
ConvLSTM. SSM-ViT (Zubic et al., CVPR 2024) is a fork of that repository in which each
stage's ConvLSTM is replaced by an S5 state space layer and nothing else changes: the same
preprocessed Gen1, the same stacked_histogram_dt=50_nbins=10 representation, the same 50 ms
window ending at the label instant, the same MaxViT stages, the same YOLOX head. The two
released capacities are 9.68M and 18.19M parameters against RVT's 9.87M and 18.54M, so
width is matched as well.

That makes this the controlled comparison the paper needs. If the newest window's influence
centroid is the same under a completely different recurrent operator, the centroid is a
property of the released configuration rather than of the ConvLSTM.

The instrument is E45's and E44's, unchanged: the occluded pass starts from the recurrent
state ENTERING the step, the whole-window influence at each lag propagates the state, and
the reset arm removes the history entirely.

One interface difference is handled and does not change the measurement. SSM-ViT's backbone
takes a sequence (L, B, C, H, W) and returns features for every step; the released
validation code applies the detection head to one step at a time. Here L = 1 and the state
is carried across calls, which is the same causal recurrence RVT runs per step.
"""
import sys, os, glob, json, numpy as np, torch, h5py, hdf5plugin
sys.path.insert(0,'/work/src/SSMViT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector

TAG=os.environ.get('TAG','small'); DEV=os.environ.get('DEV','cuda:0')
NSEQ=int(os.environ.get('NSEQ','12')); NSAMP=int(os.environ.get('NSAMP','40'))
WARM=8; KLAG=int(os.environ.get('KLAG','19'))
# The support arm costs (KLAG+1)(KLAG+2)/2 forwards per sample against the bin arm's ten,
# so the two are separable: MODE=bins gives the centroid this paper's generality claim
# needs, MODE=support adds the lag curve, MODE=both runs the pair.
MODE=os.environ.get('MODE','both')
R='/work/src/SSMViT/config/model'
base=OmegaConf.load(f'{R}/base.yaml'); rnn=OmegaConf.load(f'{R}/rnndet.yaml')
mx  =OmegaConf.load(f'{R}/maxvit_yolox/default.yaml')['model']
cfg =OmegaConf.merge(base.get('model',base),rnn,mx)
cfg =OmegaConf.merge(cfg,OmegaConf.load(f'/work/src/SSMViT/config/experiment/gen1/{TAG}.yaml')['model'])
with open_dict(cfg):
    cfg.backbone.in_res_hw=[256,320]; cfg.backbone.stage.attention.partition_size=[4,5]
    cfg.head.num_classes=2
mdl=YoloXDetector(cfg)
ck=torch.load(f'/work/data/ckpt/s5vit-{TAG}-gen1.ckpt',map_location='cpu',weights_only=False)
mdl.load_state_dict({k[4:]:v for k,v in ck['state_dict'].items() if k.startswith('mdl.')},strict=True)
mdl.eval().to(DEV)
NP=sum(p.numel() for p in mdl.parameters())/1e6
print(f"s5vit-{TAG}: {NP:.2f}M params, loaded strict",flush=True)

def clone_states(st):
    if st is None: return None
    if torch.is_tensor(st): return st.detach().clone()
    if isinstance(st,(list,tuple)): return type(st)(clone_states(x) for x in st)
    return st
def pad(t): return torch.nn.functional.pad(t,(0,320-t.shape[-1],0,256-t.shape[-2]))
def step(x,states,grad=False):
    """one causal step: x is (1,1,C,H,W); returns the detection tensor and the new state."""
    ctx=torch.enable_grad() if grad else torch.no_grad()
    with ctx:
        feats,st=mdl.forward_backbone(x,previous_states=states,train_step=False)
        o,_=mdl.forward_detect({k:v[0] for k,v in feats.items()})
    return o,st

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
        X=[pad(torch.from_numpy(np.asarray(D[i],dtype=np.float32))[None])[None].to(DEV)
           for i in range(n)]                       # each (1,1,C,H,W)
        st=None; pre=[]; ref=[]
        for i in range(n):
            pre.append(clone_states(st))
            o,st=step(X[i],st); ref.append(o.detach())
        for i in range(max(WARM,KLAG),n):
            rn=float(ref[i].norm())
            if rn<1e-6: continue
            if MODE in ('bins','both'):
                for b in range(10):
                    xm=X[i].clone(); xm[:,:,2*b:2*b+2]=0
                    o2,_=step(xm,pre[i])
                    BIN[b].append(float((o2-ref[i]).norm())/rn)
            if MODE=='bins':
                RESET.append(float('nan')); continue
            for L in range(KLAG+1):
                j=i-L; s2=clone_states(pre[j])
                for k in range(j,i+1):
                    xin=torch.zeros_like(X[k]) if k==j else X[k]
                    o2,s2=step(xin,s2)
                W[L].append(float((o2-ref[i]).norm())/rn)
            o3,_=step(X[i],None)
            RESET.append(float((o3-ref[i]).norm())/rn)
    print(f"  seq {si+1}, {len(RESET)} samples",flush=True)

bc=np.array([-(50-5*b-2.5) for b in range(10)])
bm=np.array([np.mean(v) for v in BIN]) if BIN[0] else np.full(10,np.nan)
bcen=float(((bm/bm.sum())*bc).sum()); bcv=float(bm.std()/bm.mean())
lag=np.array([-(25.0+50.0*L) for L in range(KLAG+1)])
if MODE=='bins':
    lm=np.full(KLAG+1,np.nan); c10=s10=c20=s20=float('nan')
else:
    lm=np.array([np.mean(v) for v in W])
    def cen(k):
        w=lm[:k]/lm[:k].sum(); return float((w*lag[:k]).sum()), float(100*w[0])
    c10,s10=cen(10); c20,s20=cen(KLAG+1)
print(f"\ns5vit-{TAG}  mode {MODE}  samples {len(BIN[0]) if BIN[0] else len(RESET)}")
print(f"  newest-window centroid   {bcen:+.2f} ms   CV over bins {bcv:.4f}")
print(f"  halves                   {100*bm[:5].sum()/bm.sum():.1f} / "
      f"{100*bm[5:].sum()/bm.sum():.1f} %   max/min {bm.max()/bm.min():.2f}")
if MODE!='bins':
    print(f"  support centroid, 500 ms {c10:+.1f} ms   newest share {s10:.1f} %")
    print(f"  support centroid, {50*(KLAG+1)} ms {c20:+.1f} ms   newest share {s20:.1f} %")
    print(f"  zeroing the state        {np.nanmean(RESET):.4f}   newest window alone "
          f"{lm[0]:.4f}   ratio {np.nanmean(RESET)/max(lm[0],1e-9):.2f}")
os.makedirs('/work/experiments/e47_ssm',exist_ok=True)
json.dump(dict(tag=TAG,arch='S5-ViT',n=len(RESET),params_M=float(NP),
               bin_centres=[float(v) for v in bc],bin_influence=[float(v) for v in bm],
               bin_centroid_ms=bcen,bin_cv=bcv,
               half_older=float(100*bm[:5].sum()/bm.sum()),
               half_newer=float(100*bm[5:].sum()/bm.sum()),
               max_over_min=float(bm.max()/bm.min()),
               lag_ms=([float(v) for v in lag] if MODE!='bins' else None),
               lag_influence=([float(v) for v in lm] if MODE!='bins' else None),
               centroid500=(c10 if MODE!='bins' else None),
               share500=(s10 if MODE!='bins' else None),
               centroid1000=(c20 if MODE!='bins' else None),
               share1000=(s20 if MODE!='bins' else None),
               mode=MODE,n_bins=len(BIN[0]),
               reset=float(np.nanmean(RESET)) if MODE!='bins' else None,
               newest=(float(lm[0]) if MODE!='bins' else None),
               reset_ratio=(float(np.nanmean(RESET)/max(lm[0],1e-9)) if MODE!='bins' else None)),
          open(f'/work/experiments/e47_ssm/s5vit-{TAG}-{MODE}.json','w'),indent=1)
print("WROTE")
