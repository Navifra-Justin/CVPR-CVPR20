import sys,torch
sys.path.insert(0,'/work/src/RVT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector
R='/work/src/RVT/config/model'
base=OmegaConf.load(f'{R}/base.yaml'); rnn=OmegaConf.load(f'{R}/rnndet.yaml')
mx=OmegaConf.load(f'{R}/maxvit_yolox/default.yaml')['model']
for tag,C in {'t':(32,32,0.33),'s':(48,24,0.33),'b':(64,32,0.67)}.items():
  for ps in ([6,10],[12,20]):
    cfg=OmegaConf.merge(base.get('model',base),rnn,mx)
    with open_dict(cfg):
        cfg.backbone.embed_dim=C[0]; cfg.backbone.stage.attention.dim_head=C[1]; cfg.fpn.depth=C[2]
        cfg.backbone.in_res_hw=[384,640]; cfg.backbone.stage.attention.partition_size=ps; cfg.head.num_classes=3
    try:
        m=YoloXDetector(cfg)
        sd=torch.load(f'/work/data/ckpt1mpx/rvt-{tag}-1mpx.ckpt',map_location='cpu',weights_only=False)['state_dict']
        r=m.load_state_dict({k[4:]:v for k,v in sd.items() if k.startswith('mdl.')},strict=True)
        print(tag,ps,'OK',sum(p.numel() for p in m.parameters())/1e6)
    except Exception as e: print(tag,ps,'FAIL',str(e)[:150].replace('\n',' '))
