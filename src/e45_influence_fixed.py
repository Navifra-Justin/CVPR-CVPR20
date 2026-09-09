"""E45 - the newest-window influence profile, with the state the occluded pass should get.

E17 and E34 measured the per-bin influence like this:

    out, _, states = mdl.forward(x_i, previous_states=states)   # states now post-i
    ...
    o2, _, _ = mdl.forward(x_i_occluded, previous_states=states)

The state handed to the counterfactual is the one the reference pass RETURNED, which has
already absorbed the unoccluded window. The output at step i is f(x_i, s_{i-1}), so the
counterfactual has to be f(x_i_occluded, s_{i-1}) with the state ENTERING the step. E42 and
E44 do that; E17 and E34 did not, and E44's rvt-t centroid (-23.84 ms) differs from E17's
(-24.94 ms) for that reason and no other.

This repeats E34 exactly - zero fill, dataset-mean fill, unrelated-sample fill, and a
gradient sensitivity that occludes nothing - with the entering state, and reports the
bootstrap error and the spread across instruments so the manuscript's headline number and
its robustness both come from the corrected measurement.
"""
import sys, os, glob, json, numpy as np, torch, h5py, hdf5plugin
sys.path.insert(0,'/work/src/RVT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector

DEV=os.environ.get('DEV','cuda:0'); NSEQ=int(os.environ.get('NSEQ','12'))
NSAMP=int(os.environ.get('NSAMP','40')); WARM=8
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
acc=None; cnt=0; pool=[]
for sd in seqs:
    h5=os.path.join(sd,'event_representations_v2','stacked_histogram_dt=50_nbins=10',
                    'event_representations.h5')
    if not os.path.exists(h5): continue
    with h5py.File(h5,'r') as f:
        D=f[list(f.keys())[0]]; n=min(D.shape[0],WARM+NSAMP)
        for i in range(0,n,7):
            a=np.asarray(D[i],dtype=np.float32)
            acc=a if acc is None else acc+a; cnt+=1
            if len(pool)<64: pool.append(a)
MEANp=pad(torch.from_numpy(acc/max(cnt,1)).to(DEV)[None])[0]
POOLp=pad(torch.from_numpy(np.stack(pool)).float().to(DEV))
print(f"mean fill from {cnt} frames, swap pool {POOLp.shape[0]}",flush=True)

rng=np.random.default_rng(0)
prof={k:[] for k in ('zero','mean','swap','grad')}
for si,sd in enumerate(seqs):
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
            for mode in ('zero','mean','swap'):
                w=[]
                for b in range(10):
                    xm=X[i].clone()
                    if mode=='zero':   xm[:,2*b:2*b+2]=0
                    elif mode=='mean': xm[:,2*b:2*b+2]=MEANp[2*b:2*b+2]
                    else:
                        j=int(rng.integers(POOLp.shape[0])); xm[:,2*b:2*b+2]=POOLp[j,2*b:2*b+2]
                    with torch.no_grad():
                        o2,_,_=mdl.forward(xm,previous_states=pre[i])
                    w.append(float((o2-ref[i]).norm())/rn)
                prof[mode].append(w)
            xg=X[i].clone().requires_grad_(True)
            o3,_,_=mdl.forward(xg,previous_states=pre[i])
            o3.norm().backward()
            g=xg.grad.detach().abs()
            prof['grad'].append([float(g[:,2*b:2*b+2].sum()) for b in range(10)])
    print(f"  seq {si+1}/{len(seqs)}, {len(prof['zero'])} samples",flush=True)

centres=np.array([-(50-5*b-2.5) for b in range(10)])
def centroid(P):
    m=P.mean(0); w=m/m.sum(); return float((w*centres).sum()), float(m.std()/m.mean())
def boot(P,n=4000):
    rr=np.random.default_rng(1); out=[]
    for _ in range(n):
        ii=rr.integers(0,len(P),len(P)); m=P[ii].mean(0); out.append(((m/m.sum())*centres).sum())
    return float(np.std(out)),float(np.percentile(out,2.5)),float(np.percentile(out,97.5))
R={}
print(f"\nsamples {len(prof['zero'])}   (state entering the step, as it should be)")
print(" instrument   centroid (ms)   CV over bins   bootstrap SE   95% CI")
for k in ('zero','mean','swap','grad'):
    P=np.array(prof[k]); c,cv=centroid(P); se,lo,hi=boot(P)
    print(f"  {k:<10}  {c:+10.3f}      {cv:.4f}        {se:.3f}      [{lo:+.2f}, {hi:+.2f}]")
    R[k]=dict(n=int(len(P)),centroid_ms=c,cv=cv,se_ms=se,lo=lo,hi=hi,
              mean=[float(v) for v in P.mean(0)],
              sem=[float(v) for v in P.std(0,ddof=1)/np.sqrt(len(P))],
              max_over_min=float(P.mean(0).max()/P.mean(0).min()),
              half_older=float(100*P.mean(0)[:5].sum()/P.mean(0).sum()),
              half_newer=float(100*P.mean(0)[5:].sum()/P.mean(0).sum()))
sp=[R[k]['centroid_ms'] for k in R]
print(f"\n uniform-weight reference {centres.mean():+.2f} ms")
print(f" spread across instruments {min(sp):+.3f} to {max(sp):+.3f}  = {max(sp)-min(sp):.3f} ms")
print(f" E17/E34 reported -24.94 ms with the post-step state; the difference is that state.")
os.makedirs('/work/experiments/e45_influence_fixed',exist_ok=True)
np.savez_compressed('/work/experiments/e45_influence_fixed/profiles.npz',
                    **{k:np.array(prof[k]) for k in prof}, centres=centres)
json.dump(dict(R,spread_ms=float(max(sp)-min(sp)),
               centres=[float(v) for v in centres],
               uniform_ms=float(centres.mean())),
          open('/work/experiments/e45_influence_fixed/result.json','w'),indent=1)
print("WROTE")
