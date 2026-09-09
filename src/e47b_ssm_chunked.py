"""E47b - the newest-window bin profile of SSM-ViT, called the way its release calls it.

E47's first attempt fed the backbone one window at a time, which is RVT's convention. That
convention carries no history at all in this implementation. `apply_ssm` injects the carried state as `Lambda_bars[0] = Lambda_bars[0] * prev_state`
before an associative scan whose binary operator is
`(a_i,b_i) o (a_j,b_j) = (a_j*a_i, a_j*b_i + b_j)`. The scan's outputs are the `b`
components, and `b_p` is built from `a_1..a_p` and `b_0..b_p`, so `Lambda_bars[0]` enters
only the `a` component of the first element and reaches no output at all. The carried state
is inert at every position, not merely at position zero.
The L=1 runs are therefore of a model with no history whatever, in-chunk or carried, and are
withdrawn; see experiments/e47_ssm/withdrawn_L1/WHY.md. What a chunk does preserve is the
recurrence WITHIN it, through the scan, and that is what this measures.

The released evaluation passes the whole sequence at once, (L, B, C, H, W), and applies the
detection head per position. This does the same: chunks of CHUNK windows with the state
entering the chunk, one bin of ONE window occluded, and the output read at that window's
position. Only positions with at least CHUNK//2 preceding windows inside the chunk are used,
so every sample carries comparable history.

An arm that tests the instrument runs first: zeroing the state entering the chunk. E47c shows
that this returns exactly zero for this release at every position and a non-zero value for
RVT, so the number it prints here is a statement about the release rather than a pass or fail
for the run; the history these samples do carry is the in-chunk recurrence, which E47c
measures separately by occluding the window one position earlier.
"""
import sys, os, glob, json, numpy as np, torch, h5py, hdf5plugin
sys.path.insert(0,'/work/src/SSMViT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector

TAG=os.environ.get('TAG','small'); DEV=os.environ.get('DEV','cuda:0')
NSEQ=int(os.environ.get('NSEQ','12')); NCHUNK=int(os.environ.get('NCHUNK','6'))
CHUNK=int(os.environ.get('CHUNK','8')); PMIN=CHUNK//2
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
print(f"s5vit-{TAG}: {NP:.2f}M params, chunk {CHUNK}, positions {PMIN}..{CHUNK-1}",flush=True)

def clone_states(st):
    if st is None: return None
    if torch.is_tensor(st): return st.detach().clone()
    if isinstance(st,(list,tuple)): return type(st)(clone_states(x) for x in st)
    return st
def pad(t): return torch.nn.functional.pad(t,(0,320-t.shape[-1],0,256-t.shape[-2]))
def run_chunk(xs,states):
    """xs is (L,1,C,H,W); returns the detection tensor per position and the new state."""
    with torch.no_grad():
        feats,st=mdl.forward_backbone(xs,previous_states=states,train_step=False)
        outs=[mdl.forward_detect({k:v[p] for k,v in feats.items()})[0]
              for p in range(xs.shape[0])]
    return outs,st

BIN=[[] for _ in range(10)]; STATECHK=[]
for si,sd in enumerate(sorted(glob.glob('/work/data/gen1x/gen1/val/*'))[:NSEQ]):
    h5=os.path.join(sd,'event_representations_v2','stacked_histogram_dt=50_nbins=10',
                    'event_representations.h5')
    if not os.path.exists(h5): continue
    with h5py.File(h5,'r') as f:
        D=f[list(f.keys())[0]]
        n=min(D.shape[0],CHUNK*(NCHUNK+1))
        if n<CHUNK*2: continue
        X=torch.stack([pad(torch.from_numpy(np.asarray(D[i],dtype=np.float32))[None])
                       for i in range(n)]).to(DEV)          # (n,1,C,H,W)
        st=None
        for c in range(n//CHUNK):
            xs=X[c*CHUNK:(c+1)*CHUNK]
            enter=clone_states(st)
            ref,st=run_chunk(xs,st)
            if c==0: continue                                # the warm chunk
            for p in range(PMIN,CHUNK):
                rn=float(ref[p].norm())
                if rn<1e-6: continue
                o0,_=run_chunk(xs,None)                      # state zeroed, same input
                STATECHK.append(float((o0[p]-ref[p]).norm())/rn)
                for b in range(10):
                    xm=xs.clone(); xm[p,:,2*b:2*b+2]=0
                    om,_=run_chunk(xm,enter)
                    BIN[b].append(float((om[p]-ref[p]).norm())/rn)
    print(f"  seq {si+1}, {len(BIN[0])} samples",flush=True)

sc=float(np.mean(STATECHK)) if STATECHK else 0.0
print(f"\ninstrument check: zeroing the state entering the chunk changes the output at the "
      f"measured positions by {sc:.4f} of its norm")
if sc<1e-4:
    print("  THE STATE IS INERT. Nothing below is a measurement of a recurrent model.")
bc=np.array([-(50-5*b-2.5) for b in range(10)])
P=np.array(BIN).T; bm=P.mean(0)
bcen=float(((bm/bm.sum())*bc).sum()); bcv=float(bm.std()/bm.mean())
rr=np.random.default_rng(1); bs=[]
for _ in range(4000):
    ii=rr.integers(0,len(P),len(P)); m=P[ii].mean(0); bs.append(((m/m.sum())*bc).sum())
print(f"s5vit-{TAG}  samples {len(P)}")
print(f"  newest-window centroid {bcen:+.3f} ms   CV {bcv:.4f}   boot SE {np.std(bs):.3f}")
print(f"  halves {100*bm[:5].sum()/bm.sum():.1f} / {100*bm[5:].sum()/bm.sum():.1f} %"
      f"   max/min {bm.max()/bm.min():.2f}")
os.makedirs('/work/experiments/e47_ssm',exist_ok=True)
json.dump(dict(tag=TAG,arch='S5-ViT',n=int(len(P)),params_M=float(NP),chunk=CHUNK,
               positions=[PMIN,CHUNK-1],state_effect=sc,
               bin_centres=[float(v) for v in bc],bin_influence=[float(v) for v in bm],
               bin_sem=[float(v) for v in P.std(0,ddof=1)/np.sqrt(len(P))],
               bin_centroid_ms=bcen,bin_cv=bcv,boot_se=float(np.std(bs)),
               half_older=float(100*bm[:5].sum()/bm.sum()),
               half_newer=float(100*bm[5:].sum()/bm.sum()),
               max_over_min=float(bm.max()/bm.min())),
          open(f'/work/experiments/e47_ssm/s5vit-{TAG}-chunked.json','w'),indent=1,allow_nan=False)
print("WROTE")
