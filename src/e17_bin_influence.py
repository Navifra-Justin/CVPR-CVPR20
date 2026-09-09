"""E17 - the network's actual temporal influence profile, measured.

E02 established from the released source that RVT's dt=50 ms window ENDS at the
label time, so under uniform bin weighting the information centroid sits 25 ms
before the label. Whether the trained network weights its ten bins uniformly was
never measured, so 25 ms was recorded as a reference point and not as a prediction.

This measures it. For each sample the ten 5 ms bins are occluded one at a time and
the change in the detector's output is recorded. The resulting profile w(k) is the
network's influence per bin; its centroid is the effective time of the prediction,
in the network's own weighting rather than an assumed one.

Runs on real gen1 val data with the released rvt-t checkpoint, sequentially through
each sequence so the recurrent state is the one the model would actually have.
"""
import sys, os, glob, json, numpy as np, torch, h5py, hdf5plugin
sys.path.insert(0,'/work/src/RVT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector

DEV = os.environ.get('DEV','cuda:0')
NSEQ = int(os.environ.get('NSEQ','12'))
NSAMP = int(os.environ.get('NSAMP','40'))     # samples per sequence after warmup
WARM  = 8                                      # recurrent warmup steps

base=OmegaConf.load('/work/src/RVT/config/model/base.yaml')
rnn =OmegaConf.load('/work/src/RVT/config/model/rnndet.yaml')
mx  =OmegaConf.load('/work/src/RVT/config/model/maxvit_yolox/default.yaml')['model']
cfg =OmegaConf.merge(base.get('model',base),rnn,mx)
with open_dict(cfg):
    cfg.backbone.embed_dim=32; cfg.fpn.depth=0.33
    cfg.backbone.in_res_hw=[256,320]
    cfg.backbone.stage.attention.partition_size=[4,5]
    cfg.head.num_classes=2
mdl=YoloXDetector(cfg)
ck=torch.load('/work/data/ckpt/rvt-t-gen1.ckpt',map_location='cpu',weights_only=False)
mdl.load_state_dict({k[4:]:v for k,v in ck['state_dict'].items() if k.startswith('mdl.')},strict=True)
mdl.eval().to(DEV)
print(f"model on {DEV}", flush=True)

seqs=sorted(glob.glob('/work/data/gen1x/gen1/val/*'))[:NSEQ]
prof=[]; base_norm=[]
for si,sd in enumerate(seqs):
    h5=os.path.join(sd,'event_representations_v2','stacked_histogram_dt=50_nbins=10','event_representations.h5')
    if not os.path.exists(h5): continue
    with h5py.File(h5,'r') as f:
        key=[k for k in f.keys()][0]
        D=f[key]
        n=min(D.shape[0], WARM+NSAMP)
        states=None; buf=[]
        for i in range(n):
            x=torch.from_numpy(D[i][None]).float()
            # pad 240x304 -> 256x320 as config/modifier does
            x=torch.nn.functional.pad(x,(0,320-x.shape[-1],0,256-x.shape[-2]))
            x=x.to(DEV)
            with torch.no_grad():
                out,_,states=mdl.forward(x,previous_states=states)
            if i<WARM: continue
            ref=out.detach()
            rn=float(ref.norm())
            if rn<1e-6: continue
            w=[]
            for b in range(10):
                xm=x.clone(); xm[:,2*b:2*b+2]=0
                with torch.no_grad():
                    o2,_,_=mdl.forward(xm,previous_states=states)
                w.append(float((o2-ref).norm())/rn)
            buf.append(w); base_norm.append(rn)
        prof.extend(buf)
    print(f"  seq {si+1}/{len(seqs)} done, {len(prof)} samples", flush=True)

P=np.array(prof)
print(f"\nSAMPLES {len(P)}")
m=P.mean(0); s=P.std(0)/max(np.sqrt(len(P)),1)
centres=np.array([-(50-5*b-2.5) for b in range(10)])   # bin centre relative to the label time
print("bin  centre_ms  influence  sem")
for b in range(10):
    print(f" {b:>2}  {centres[b]:>8.1f}  {m[b]:.5f}  {s[b]:.5f}")
w=m/m.sum()
cent=float((w*centres).sum())
unif=float(centres.mean())
print(f"\nINFLUENCE-WEIGHTED CENTROID  {cent:+.2f} ms")
print(f"UNIFORM-WEIGHT REFERENCE     {unif:+.2f} ms")
print(f"DIFFERENCE                   {cent-unif:+.2f} ms")
json.dump(dict(n=int(len(P)),mean=m.tolist(),sem=s.tolist(),centres=centres.tolist(),
               centroid_ms=cent,uniform_ms=unif,diff_ms=cent-unif),
          open('/work/experiments/e17_bin_influence/result.json','w'),indent=1)
print("WROTE",flush=True)
