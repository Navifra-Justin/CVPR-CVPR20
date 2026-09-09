"""E42 - the temporal support of a RECURRENT detector, including its history.

E17 and E34 occlude the bins of the current 50 ms window while holding the recurrent state
fixed, and report the centroid of that profile. An external review is right that this is
the influence of the current window CONDITIONAL on an intact recurrent state, and not the
temporal support of the emitted state as Sec. 3.1 defines it: RVT carries an LSTM state
between timesteps, so the prediction at t depends on windows before t as well.

The paper's own sentence "the profile is a property of the current window and not of a
perturbed history" states what was measured. The abstract and conclusion then generalise
it. Rather than narrow the wording, this measures the missing part.

Two measurements.

  (A) The window-level kernel. For each lag L, occlude the ENTIRE window at t - 50L,
      restart from the state saved before that step, and let the recurrent state propagate
      forward normally to t. The change in the emitted state at t is that window's
      influence. Because E17 measured the within-window profile to be flat (CV 0.034), a
      window at lag L contributes at a centroid of -(25 + 50L) ms, and the full support
      centroid is the influence-weighted mean over lags.

  (B) How much of the output depends on history at all: run the target step with the true
      warmed state and again with a zeroed state, same input window, and compare. If that
      change is small the two definitions nearly coincide; if it is large the history term
      is what the review says it is.

States are saved per step and restored, so occluding lag L costs L+1 forwards rather than
a whole re-run.
"""
import sys, os, glob, json, numpy as np, torch, h5py, hdf5plugin
sys.path.insert(0,'/work/src/RVT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector

DEV=os.environ.get('DEV','cuda:0'); NSEQ=int(os.environ.get('NSEQ','12'))
NSAMP=int(os.environ.get('NSAMP','40')); WARM=8; KLAG=int(os.environ.get('KLAG','9'))
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

W=[[] for _ in range(KLAG+1)]      # per-lag relative influence
RESET=[]                            # relative change when the state is zeroed
for si,sd in enumerate(sorted(glob.glob('/work/data/gen1x/gen1/val/*'))[:NSEQ]):
    h5=os.path.join(sd,'event_representations_v2','stacked_histogram_dt=50_nbins=10',
                    'event_representations.h5')
    if not os.path.exists(h5): continue
    with h5py.File(h5,'r') as f:
        D=f[list(f.keys())[0]]
        n=min(D.shape[0],WARM+NSAMP+KLAG)
        X=[pad(torch.from_numpy(np.asarray(D[i],dtype=np.float32))[None]).to(DEV)
           for i in range(n)]
        # reference pass, saving the state ENTERING each step and the output of each step
        st=None; pre=[]; ref=[]
        for i in range(n):
            pre.append(clone_states(st))
            with torch.no_grad(): o,_,st=mdl.forward(X[i],previous_states=st)
            ref.append(o.detach())
        for i in range(max(WARM,KLAG),n):
            rn=float(ref[i].norm())
            if rn<1e-6: continue
            for L in range(KLAG+1):
                j=i-L
                s2=clone_states(pre[j])
                for k in range(j,i+1):
                    xin=X[k]
                    if k==j: xin=torch.zeros_like(X[k])      # the whole window at lag L
                    with torch.no_grad(): o2,_,s2=mdl.forward(xin,previous_states=s2)
                W[L].append(float((o2-ref[i]).norm())/rn)
            with torch.no_grad():
                o3,_,_=mdl.forward(X[i],previous_states=None)  # no history at all
            RESET.append(float((o3-ref[i]).norm())/rn)
    print(f"  seq {si+1}, {len(W[0])} samples",flush=True)

lag_ms=np.array([-(25.0+50.0*L) for L in range(KLAG+1)])
m=np.array([np.mean(w) for w in W]); se=np.array([np.std(w)/max(np.sqrt(len(w)),1) for w in W])
print(f"\nsamples {len(W[0])}")
print(" lag  window centre (ms)   influence   sem    share of total")
tot=m.sum()
for L in range(KLAG+1):
    print(f"  {L:2d}   {lag_ms[L]:12.1f}   {m[L]:9.5f}  {se[L]:.5f}   {100*m[L]/tot:6.2f} %")
cen=float((m/tot*lag_ms).sum())
cur=float(lag_ms[0])
print(f"\n current window alone (E17's conditional measurement) centres at {cur:+.2f} ms")
print(f" FULL support centroid over {KLAG+1} windows            {cen:+.2f} ms")
print(f" the current window carries {100*m[0]/tot:.1f} % of the total influence")
half=np.cumsum(m)/tot
k=int(np.searchsorted(half,0.5))
print(f" half the influence is reached by lag {k} ({lag_ms[k]:+.0f} ms)")
print(f"\n zeroing the recurrent state changes the output by "
      f"{np.mean(RESET):.4f} of its norm (sem {np.std(RESET)/np.sqrt(len(RESET)):.4f})")
print(f"   for comparison, occluding the whole current window changes it by {m[0]:.4f}")
os.makedirs('/work/experiments/e42_recurrent_support',exist_ok=True)
json.dump(dict(n=len(W[0]),klag=KLAG,lag_ms=[float(v) for v in lag_ms],
               influence=[float(v) for v in m],sem=[float(v) for v in se],
               centroid_full_ms=cen,centroid_current_ms=cur,
               current_share=float(m[0]/tot),
               reset_change=float(np.mean(RESET)),
               reset_sem=float(np.std(RESET)/np.sqrt(len(RESET)))),
          open(os.environ.get('OUTJ','/work/experiments/e42_recurrent_support/result.json'),'w'),indent=1)
print("WROTE")
