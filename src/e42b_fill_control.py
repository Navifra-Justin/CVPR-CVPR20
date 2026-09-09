"""E42b - is the non-decaying tail of the recurrent support real, or a zero-fill floor?

E42 occludes whole past windows with zeros and finds influence that stops decaying around
0.0022 by one second of history, so the influence-weighted centroid keeps moving with the
horizon (-165.9 ms over 500 ms, -299.4 ms over 1000 ms). Before that is reported as long
memory it has to be separated from its instrument: writing zeros into a past window pushes
the recurrent state off the manifold it was trained on, and the perturbation it leaves may
settle at a floor that has nothing to do with dependence on that window.

The control is the fill. Replacing the window at lag L with the SAME-index window of an
unrelated sample keeps the marginal statistics and the spatial structure of a real window
and still removes that window's own content. If the plateau survives the swap it is
dependence; if it collapses it is the zero fill.

Measured at lags 0, 1, 3, 9 and 19 to keep the cost bounded.
"""
import sys, os, glob, json, numpy as np, torch, h5py, hdf5plugin
sys.path.insert(0,'/work/src/RVT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector

DEV=os.environ.get('DEV','cuda:0'); NSEQ=int(os.environ.get('NSEQ','12'))
NSAMP=int(os.environ.get('NSAMP','40')); WARM=8
LAGS=[0,1,3,9,19]; KMAX=max(LAGS)
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
def clone_states(st):
    if st is None: return None
    if torch.is_tensor(st): return st.detach().clone()
    if isinstance(st,(list,tuple)): return type(st)(clone_states(x) for x in st)
    return st
def pad(t): return torch.nn.functional.pad(t,(0,320-t.shape[-1],0,256-t.shape[-2]))

seqs=sorted(glob.glob('/work/data/gen1x/gen1/val/*'))[:NSEQ]
pool=[]
for sd in seqs[:4]:
    h5=os.path.join(sd,'event_representations_v2','stacked_histogram_dt=50_nbins=10',
                    'event_representations.h5')
    if not os.path.exists(h5): continue
    with h5py.File(h5,'r') as f:
        D=f[list(f.keys())[0]]
        for i in range(0,min(D.shape[0],60),6):
            pool.append(pad(torch.from_numpy(np.asarray(D[i],dtype=np.float32))[None]))
POOL=torch.cat(pool).to(DEV)
print(f"swap pool {POOL.shape[0]} windows",flush=True)
rng=np.random.default_rng(0)
Z={L:[] for L in LAGS}; S={L:[] for L in LAGS}
for si,sd in enumerate(seqs):
    h5=os.path.join(sd,'event_representations_v2','stacked_histogram_dt=50_nbins=10',
                    'event_representations.h5')
    if not os.path.exists(h5): continue
    with h5py.File(h5,'r') as f:
        D=f[list(f.keys())[0]]
        n=min(D.shape[0],WARM+NSAMP+KMAX)
        X=[pad(torch.from_numpy(np.asarray(D[i],dtype=np.float32))[None]).to(DEV)
           for i in range(n)]
        st=None; pre=[]; ref=[]
        for i in range(n):
            pre.append(clone_states(st))
            with torch.no_grad(): o,_,st=mdl.forward(X[i],previous_states=st)
            ref.append(o.detach())
        for i in range(max(WARM,KMAX),n):
            rn=float(ref[i].norm())
            if rn<1e-6: continue
            for L in LAGS:
                j=i-L
                for mode in ('zero','swap'):
                    s2=clone_states(pre[j])
                    for k in range(j,i+1):
                        if k==j:
                            xin=(torch.zeros_like(X[k]) if mode=='zero'
                                 else POOL[int(rng.integers(POOL.shape[0]))][None])
                        else: xin=X[k]
                        with torch.no_grad(): o2,_,s2=mdl.forward(xin,previous_states=s2)
                    (Z if mode=='zero' else S)[L].append(float((o2-ref[i]).norm())/rn)
    print(f"  seq {si+1}, {len(Z[LAGS[0]])} samples",flush=True)

print(f"\nsamples {len(Z[LAGS[0]])}")
print("  lag   centre(ms)     zero fill        swap fill      swap/zero")
out={}
for L in LAGS:
    z=np.mean(Z[L]); s=np.mean(S[L])
    print(f"  {L:3d}   {-(25+50*L):9.0f}   {z:.5f}+-{np.std(Z[L])/np.sqrt(len(Z[L])):.5f}   "
          f"{s:.5f}+-{np.std(S[L])/np.sqrt(len(S[L])):.5f}   {s/max(z,1e-12):6.3f}")
    out[L]=dict(zero=float(z),swap=float(s),ratio=float(s/max(z,1e-12)))
zl=[out[L]['zero'] for L in LAGS]; sl=[out[L]['swap'] for L in LAGS]
print(f"\n  decay from lag 0 to lag {KMAX}:  zero fill {zl[0]/zl[-1]:.2f}x   "
      f"swap fill {sl[0]/sl[-1]:.2f}x")
print("  a plateau that is an artefact of the fill collapses under the swap;")
print("  one that is dependence does not.")
os.makedirs('/work/experiments/e42_recurrent_support',exist_ok=True)
json.dump(dict(n=len(Z[LAGS[0]]),lags=LAGS,per_lag={str(k):v for k,v in out.items()},
               decay_zero=float(zl[0]/zl[-1]),decay_swap=float(sl[0]/sl[-1])),
          open('/work/experiments/e42_recurrent_support/fill_control.json','w'),indent=1)
print("WROTE")
