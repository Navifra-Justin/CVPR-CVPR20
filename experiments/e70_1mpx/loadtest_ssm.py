import sys,torch
sys.path.insert(0,'/work/src/SSMViT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector
R='/work/src/SSMViT/config/model'
base=OmegaConf.load(f'{R}/base.yaml'); rnn=OmegaConf.load(f'{R}/rnndet.yaml')
mx=OmegaConf.load(f'{R}/maxvit_yolox/default.yaml')['model']
for tag in ['small','base']:
  for ps in ([6,10],):
    cfg=OmegaConf.merge(base.get('model',base),rnn,mx)
    cfg=OmegaConf.merge(cfg,OmegaConf.load(f'/work/src/SSMViT/config/experiment/gen4/{tag}.yaml')['model'])
    with open_dict(cfg):
        cfg.backbone.in_res_hw=[384,640]; cfg.backbone.stage.attention.partition_size=ps; cfg.head.num_classes=3
    try:
        m=YoloXDetector(cfg)
        sd=torch.load(f'/work/data/ckpt1mpx/s5vit-{tag}-1mpx.ckpt',map_location='cpu',weights_only=False)['state_dict']
        m.load_state_dict({k[4:]:v for k,v in sd.items() if k.startswith('mdl.')},strict=True)
        print(tag,ps,'OK',sum(p.numel() for p in m.parameters())/1e6, list(sd.keys())[:2])
    except Exception as e: print(tag,ps,'FAIL',str(e)[:400].replace('\n',' '))
