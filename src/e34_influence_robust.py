"""E34 - is the -24.94 ms influence centroid an artefact of how a bin is occluded?

E17 occludes a bin by writing zeros into it. Zero is a valid value for this
representation - it means "no events in this bin" - but it is still an intervention, and
a flat profile is exactly what an off-manifold intervention could produce for reasons
that have nothing to do with temporal weighting. E17 measured CV = 0.034, so the profile
IS flat, and the objection has to be answered rather than dismissed.

Three fills and one entirely different instrument:
  zero      what E17 did
  mean      the bin replaced by its dataset mean, which keeps the input in range
  swap      the bin replaced by the SAME bin of an unrelated sample, which keeps both the
            marginal statistics and the spatial structure of a real bin
  gradient  no intervention at all: d||out|| / d(bin), the local sensitivity, summed over
            the bin's channels. This has no occlusion and no off-manifold step.

If the centroid moves between these, the E17 number is about the intervention. If it does
not, it is about the network. The recurrent state is held fixed across every variant
within a sample - the reference and the perturbed pass are given the same `states` and the
returned states are discarded - so nothing here measures state perturbation.

A bootstrap over samples gives the centroid its own standard error, which the paper needs
in order to state the evidence-to-output interval's uncertainty honestly.
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

seqs=sorted(glob.glob('/work/data/gen1x/gen1/val/*'))[:NSEQ]
# pass 1: the per-channel dataset mean of the representation, for the mean fill
acc=None; cnt=0; pool=[]
for sd in seqs:
    h5=os.path.join(sd,'event_representations_v2','stacked_histogram_dt=50_nbins=10','event_representations.h5')
    if not os.path.exists(h5): continue
    with h5py.File(h5,'r') as f:
        D=f[list(f.keys())[0]]; n=min(D.shape[0],WARM+NSAMP)
        for i in range(0,n,7):
            a=np.asarray(D[i],dtype=np.float32)
            acc=a if acc is None else acc+a; cnt+=1
            if len(pool)<64: pool.append(a)
MEAN=torch.from_numpy(acc/max(cnt,1)).to(DEV)
POOL=torch.from_numpy(np.stack(pool)).float().to(DEV)
print(f"mean fill from {cnt} frames, swap pool {POOL.shape[0]} frames",flush=True)
def pad(t):
    return torch.nn.functional.pad(t,(0,320-t.shape[-1],0,256-t.shape[-2]))
MEANp=pad(MEAN[None])[0]; POOLp=pad(POOL)

prof={k:[] for k in ('zero','mean','swap','grad')}
rng=np.random.default_rng(0)
for si,sd in enumerate(seqs):
    h5=os.path.join(sd,'event_representations_v2','stacked_histogram_dt=50_nbins=10','event_representations.h5')
    if not os.path.exists(h5): continue
    with h5py.File(h5,'r') as f:
        D=f[list(f.keys())[0]]; n=min(D.shape[0],WARM+NSAMP); states=None
        for i in range(n):
            x=pad(torch.from_numpy(np.asarray(D[i],dtype=np.float32))[None]).to(DEV)
            with torch.no_grad():
                out,_,states=mdl.forward(x,previous_states=states)
            if i<WARM: continue
            ref=out.detach(); rn=float(ref.norm())
            if rn<1e-6: continue
            for mode in ('zero','mean','swap'):
                w=[]
                for b in range(10):
                    xm=x.clone()
                    if mode=='zero':   xm[:,2*b:2*b+2]=0
                    elif mode=='mean': xm[:,2*b:2*b+2]=MEANp[2*b:2*b+2]
                    else:
                        j=int(rng.integers(POOLp.shape[0])); xm[:,2*b:2*b+2]=POOLp[j,2*b:2*b+2]
                    with torch.no_grad():
                        o2,_,_=mdl.forward(xm,previous_states=states)
                    w.append(float((o2-ref).norm())/rn)
                prof[mode].append(w)
            xg=x.clone().requires_grad_(True)
            o3,_,_=mdl.forward(xg,previous_states=states)
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
    return float(np.std(out)), float(np.percentile(out,2.5)), float(np.percentile(out,97.5))
R={}
print(f"\nsamples {len(prof['zero'])}")
print(" instrument   centroid (ms)   CV over bins   bootstrap SE   95% CI")
for k in ('zero','mean','swap','grad'):
    P=np.array(prof[k]); c,cv=centroid(P); se,lo,hi=boot(P)
    print(f"  {k:<10}  {c:+10.3f}      {cv:.4f}        {se:.3f}      [{lo:+.2f}, {hi:+.2f}]")
    R[k]=dict(n=int(len(P)),centroid_ms=c,cv=cv,se_ms=se,lo=lo,hi=hi,
              mean=[float(v) for v in P.mean(0)])
print(f"\n uniform-weight reference: {centres.mean():+.2f} ms")
sp=[R[k]['centroid_ms'] for k in R]
print(f" spread of the centroid across all four instruments: {min(sp):+.3f} to {max(sp):+.3f} ms")
os.makedirs('/work/experiments/e34_influence_robust',exist_ok=True)
json.dump(R,open('/work/experiments/e34_influence_robust/result.json','w'),indent=1)
print("WROTE")
