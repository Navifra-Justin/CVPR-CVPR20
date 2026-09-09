"""E47c - how much the carried state matters, as a function of position in the chunk.

E47's first attempt showed that SSM-ViT's carried state does not reach the first position of
a chunk. `apply_ssm` injects it as `Lambda_bars[0] = Lambda_bars[0] * prev_state` and the
scan's first output is `Bu_elements[0]`, so the state multiplies only what follows position
zero. The released streaming evaluation processes the validation split in chunks of
`sequence_length` windows with the state carried between chunks, which means the temporal
support of a released detection depends on where its frame falls inside that chunk.

This measures it rather than deducing it. For each position p of a chunk, the reference
output is compared with the output of the same chunk run with the entering state zeroed, as a
relative L2 change in the emitted detection tensor. The prediction from reading the code is
exactly zero at p = 0 and rising with p; anything else means the reading is wrong.

The same arm is run on RVT, where the state enters every step, as the control.
"""
import sys, os, glob, json, numpy as np, torch, h5py, hdf5plugin
FAM=os.environ.get('FAM','ssm'); TAG=os.environ.get('TAG','small')
DEV=os.environ.get('DEV','cuda:0'); NSEQ=int(os.environ.get('NSEQ','12'))
CHUNK=int(os.environ.get('CHUNK','8')); NCHUNK=int(os.environ.get('NCHUNK','6'))
sys.path.insert(0,'/work/src/SSMViT' if FAM=='ssm' else '/work/src/RVT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector
R='/work/src/SSMViT/config/model' if FAM=='ssm' else '/work/src/RVT/config/model'
base=OmegaConf.load(f'{R}/base.yaml'); rnn=OmegaConf.load(f'{R}/rnndet.yaml')
mx  =OmegaConf.load(f'{R}/maxvit_yolox/default.yaml')['model']
cfg =OmegaConf.merge(base.get('model',base),rnn,mx)
if FAM=='ssm':
    cfg=OmegaConf.merge(cfg,OmegaConf.load(
        f'/work/src/SSMViT/config/experiment/gen1/{TAG}.yaml')['model'])
    CK=f'/work/data/ckpt/s5vit-{TAG}-gen1.ckpt'
else:
    C={'t':(32,32,0.33),'s':(48,24,0.33),'b':(64,32,0.67)}[TAG]
    with open_dict(cfg):
        cfg.backbone.embed_dim=C[0]; cfg.backbone.stage.attention.dim_head=C[1]
        cfg.fpn.depth=C[2]
    CK=f'/work/data/ckpt/rvt-{TAG}-gen1.ckpt'
with open_dict(cfg):
    cfg.backbone.in_res_hw=[256,320]; cfg.backbone.stage.attention.partition_size=[4,5]
    cfg.head.num_classes=2
mdl=YoloXDetector(cfg)
sd_=torch.load(CK,map_location='cpu',weights_only=False)['state_dict']
mdl.load_state_dict({k[4:]:v for k,v in sd_.items() if k.startswith('mdl.')},strict=True)
mdl.eval().to(DEV)
name=(f's5vit-{TAG}' if FAM=='ssm' else f'rvt-{TAG}')
print(f"{name}: {sum(p.numel() for p in mdl.parameters())/1e6:.2f}M, chunk {CHUNK}",flush=True)
def clone_states(st):
    if st is None: return None
    if torch.is_tensor(st): return st.detach().clone()
    if isinstance(st,(list,tuple)): return type(st)(clone_states(x) for x in st)
    return st
def pad(t): return torch.nn.functional.pad(t,(0,320-t.shape[-1],0,256-t.shape[-2]))
def run_chunk(xs,states):
    """RVT takes one window per call, SSM-ViT a chunk; both are driven here as one chunk."""
    outs=[]
    with torch.no_grad():
        if FAM=='ssm':
            feats,st=mdl.forward_backbone(xs,previous_states=states,train_step=False)
            outs=[mdl.forward_detect({k:v[p] for k,v in feats.items()})[0]
                  for p in range(xs.shape[0])]
        else:
            st=states
            for p in range(xs.shape[0]):
                o,_,st=mdl.forward(xs[p],previous_states=st); outs.append(o)
    return outs,st
EFF=[[] for _ in range(CHUNK)]     # arm A: zero the state entering the chunk
INCH=[[] for _ in range(CHUNK)]    # arm B: occlude the window one position earlier
for si,sd in enumerate(sorted(glob.glob('/work/data/gen1x/gen1/val/*'))[:NSEQ]):
    h5=os.path.join(sd,'event_representations_v2','stacked_histogram_dt=50_nbins=10',
                    'event_representations.h5')
    if not os.path.exists(h5): continue
    with h5py.File(h5,'r') as f:
        D=f[list(f.keys())[0]]; n=min(D.shape[0],CHUNK*(NCHUNK+1))
        if n<CHUNK*2: continue
        X=torch.stack([pad(torch.from_numpy(np.asarray(D[i],dtype=np.float32))[None])
                       for i in range(n)]).to(DEV)
        st=None
        for c in range(n//CHUNK):
            xs=X[c*CHUNK:(c+1)*CHUNK]
            prev_enter=clone_states(st)
            ref,st=run_chunk(xs,st)
            if c==0: continue
            o0,_=run_chunk(xs,None)
            for p in range(CHUNK):
                rn=float(ref[p].norm())
                if rn>1e-6: EFF[p].append(float((o0[p]-ref[p]).norm())/rn)
            # arm B: is the model recurrent WITHIN the chunk? Occlude the window one
            # position earlier and read the same position. A model that ignores its own
            # history entirely would return zero here too, and then arm A says nothing.
            for p in range(1,CHUNK):
                rn=float(ref[p].norm())
                if rn<1e-6: continue
                xm=xs.clone(); xm[p-1]=0
                om,_=run_chunk(xm,prev_enter)
                INCH[p].append(float((om[p]-ref[p]).norm())/rn)
    print(f"  seq {si+1}, {len(EFF[0])} chunks",flush=True)
m =[float(np.mean(v)) if v else None for v in EFF]
mi=[float(np.mean(v)) if v else None for v in INCH]
print(f"\n{name}: relative change in the emitted detection tensor, by position in the chunk")
print("  position   zeroing the entering state   occluding the previous window")
for p in range(CHUNK):
    a_=f"{m[p]:.5f}" if m[p] is not None else "   -  "
    b_=f"{mi[p]:.5f}" if mi[p] is not None else "   -  "
    print(f"     {p}            {a_}                        {b_}")
os.makedirs('/work/experiments/e47_ssm',exist_ok=True)
json.dump(dict(model=name,family=FAM,chunk=CHUNK,n=len(EFF[0]),
               effect_by_position=m,inchunk_by_position=mi),
          open(f'/work/experiments/e47_ssm/statepos-{name}.json','w'),indent=1,allow_nan=False)
print("WROTE")
