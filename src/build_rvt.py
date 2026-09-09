import sys, torch
sys.path.insert(0, '/work/src/RVT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector

base = OmegaConf.load('/work/src/RVT/config/model/base.yaml')
rnn  = OmegaConf.load('/work/src/RVT/config/model/rnndet.yaml')
mx   = OmegaConf.load('/work/src/RVT/config/model/maxvit_yolox/default.yaml')['model']
cfg  = OmegaConf.merge(base.get('model', base), rnn, mx)
with open_dict(cfg):
    cfg.backbone.embed_dim = 32          # gen1/tiny.yaml
    cfg.fpn.depth = 0.33                 # gen1/tiny.yaml
    cfg.backbone.in_res_hw = [256, 320]  # modifier.py: ceil(240/64)*64, ceil(304/64)*64
    cfg.backbone.stage.attention.partition_size = [4, 5]   # mdl_hw // (32*2)
    cfg.head.num_classes = 2             # gen1
print("CFG: embed_dim", cfg.backbone.embed_dim, "in_ch", cfg.backbone.input_channels,
      "in_res", list(cfg.backbone.in_res_hw), "partition", list(cfg.backbone.stage.attention.partition_size))

mdl = YoloXDetector(cfg)
print(f"MODEL BUILT params={sum(p.numel() for p in mdl.parameters())/1e6:.2f}M")

ck = torch.load('/work/data/ckpt/rvt-t-gen1.ckpt', map_location='cpu', weights_only=False)
sd = {k[4:]: v for k, v in ck['state_dict'].items() if k.startswith('mdl.')}
missing, unexpected = mdl.load_state_dict(sd, strict=False)
print("MISSING:", len(missing), missing[:4])
print("UNEXPECTED:", len(unexpected), unexpected[:4])

mdl.eval()
with torch.no_grad():
    x = torch.zeros(1, 20, 256, 320)
    r = mdl.forward(x, previous_states=None)
print("FORWARD OK, returned", len(r), "items:", [type(a).__name__ for a in r])
bb = r[0]
if hasattr(bb, "keys"):
    for k in bb.keys(): print("  backbone level", k, tuple(bb[k].shape))
