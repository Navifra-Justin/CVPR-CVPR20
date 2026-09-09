"""E43 - do the released rvt-s and rvt-b checkpoints load, and with which configuration?

The predictor-side measurements are all on rvt-t. An external review names a second
released detector as the single highest-value reduction of the "one checkpoint" objection.
RVT publishes three capacities for Gen1, so the same measurement can be repeated on each
without changing dataset, representation or evaluation code.

The configurations differ only in embed_dim, attention dim_head and FPN depth
(config/experiment/gen1/{tiny,small,base}.yaml). This verifies that each checkpoint loads
into a model built from those files with no missing and no unexpected keys, which is the
same port check E04 ran for rvt-t.
"""
import sys, os, torch
sys.path.insert(0,'/work/src/RVT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector

CFG={'t':dict(embed_dim=32,dim_head=32,fpn=0.33),
     's':dict(embed_dim=48,dim_head=24,fpn=0.33),
     'b':dict(embed_dim=64,dim_head=32,fpn=0.67)}
for tag,c in CFG.items():
    p=f'/work/data/ckpt/rvt-{tag}-gen1.ckpt'
    if not os.path.exists(p): print(f"  rvt-{tag}: no checkpoint"); continue
    base=OmegaConf.load('/work/src/RVT/config/model/base.yaml')
    rnn =OmegaConf.load('/work/src/RVT/config/model/rnndet.yaml')
    mx  =OmegaConf.load('/work/src/RVT/config/model/maxvit_yolox/default.yaml')['model']
    cfg =OmegaConf.merge(base.get('model',base),rnn,mx)
    with open_dict(cfg):
        cfg.backbone.embed_dim=c['embed_dim']; cfg.fpn.depth=c['fpn']
        cfg.backbone.stage.attention.dim_head=c['dim_head']
        cfg.backbone.in_res_hw=[256,320]; cfg.backbone.stage.attention.partition_size=[4,5]
        cfg.head.num_classes=2
    mdl=YoloXDetector(cfg)
    ck=torch.load(p,map_location='cpu',weights_only=False)
    sd={k[4:]:v for k,v in ck['state_dict'].items() if k.startswith('mdl.')}
    r=mdl.load_state_dict(sd,strict=False)
    n=sum(v.numel() for v in mdl.parameters())/1e6
    print(f"  rvt-{tag}: embed_dim {c['embed_dim']:3d} dim_head {c['dim_head']:3d} "
          f"fpn {c['fpn']:.2f}  params {n:5.2f}M  "
          f"missing {len(r.missing_keys)}  unexpected {len(r.unexpected_keys)}")
    if r.missing_keys: print("     first missing:",r.missing_keys[:3])
    if r.unexpected_keys: print("     first unexpected:",r.unexpected_keys[:3])
