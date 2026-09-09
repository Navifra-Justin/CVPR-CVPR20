"""E47a - can the released S5-ViT Gen1 checkpoints be loaded, and do they read the same input.

The paper's predictor-side measurements are all on RVT. The nearest thing to a second
architecture that keeps every other variable fixed is SSM-ViT (Zubic et al., CVPR 2024):
it is a fork of the RVT repository in which the per-stage ConvLSTM is replaced by an S5
state space layer, trained on the same preprocessed Gen1 with the same representation
(stacked_histogram_dt=50_nbins=10) and the same 50 ms window. So the temporal operator
changes and the window does not, which is the comparison the paper needs.

This checks only that the released weights load into the released code with no missing or
unexpected keys, and that a forward pass runs, before any measurement is attempted.
"""
import sys, os, json, numpy as np, torch
sys.path.insert(0,'/work/src/SSMViT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector
DEV=os.environ.get('DEV','cuda:0')
R='/work/src/SSMViT/config/model'
def build(tag):
    base=OmegaConf.load(f'{R}/base.yaml'); rnn=OmegaConf.load(f'{R}/rnndet.yaml')
    mx  =OmegaConf.load(f'{R}/maxvit_yolox/default.yaml')['model']
    cfg =OmegaConf.merge(base.get('model',base),rnn,mx)
    exp =OmegaConf.load(f'/work/src/SSMViT/config/experiment/gen1/{tag}.yaml')['model']
    cfg =OmegaConf.merge(cfg,exp)
    with open_dict(cfg):
        cfg.backbone.in_res_hw=[256,320]
        cfg.backbone.stage.attention.partition_size=[4,5]
        cfg.head.num_classes=2
    return cfg
for tag,ck in (('small','s5vit-small-gen1.ckpt'),('base','s5vit-base-gen1.ckpt')):
    p=f'/work/data/ckpt/{ck}'
    if not os.path.exists(p): print(f"{tag}: checkpoint absent, skipped"); continue
    cfg=build(tag); mdl=YoloXDetector(cfg)
    sd=torch.load(p,map_location='cpu',weights_only=False)['state_dict']
    pref=sorted({k.split('.')[0] for k in sd})[:5]
    sd2={k[4:]:v for k,v in sd.items() if k.startswith('mdl.')}
    r=mdl.load_state_dict(sd2,strict=False)
    n=sum(p_.numel() for p_ in mdl.parameters())/1e6
    print(f"{tag}: prefixes {pref}  params {n:.2f} M  "
          f"missing {len(r.missing_keys)}  unexpected {len(r.unexpected_keys)}")
    if r.missing_keys: print("   missing e.g.", r.missing_keys[:4])
    if r.unexpected_keys: print("   unexpected e.g.", r.unexpected_keys[:4])
    mdl.eval().to(DEV)
    # SSM-ViT's backbone takes a sequence (L, B, C, H, W) and returns features for every
    # step, so the detection head is applied to one step at a time exactly as the released
    # validation code does. With L=1 and the state carried across calls this is the same
    # causal recurrence RVT runs per step, which is what makes the two measurements
    # comparable.
    x=torch.zeros(1,1,20,256,320,device=DEV)
    with torch.no_grad():
        feats,st=mdl.forward_backbone(x,previous_states=None,train_step=False)
        o,_=mdl.forward_detect({k:v[0] for k,v in feats.items()})
    print(f"   forward ok: out {tuple(o.shape)}  states {len(st)} stages, "
          f"stage0 {tuple(st[0].shape)}")
