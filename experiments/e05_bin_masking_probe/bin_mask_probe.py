"""Does masking leading bins of the stored 20-channel tensor move the network's
output, and how? Sanity probe on synthetic sparse input; no dataset needed."""
import sys, torch
sys.path.insert(0, '/work/src/RVT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector

base = OmegaConf.load('/work/src/RVT/config/model/base.yaml')
rnn  = OmegaConf.load('/work/src/RVT/config/model/rnndet.yaml')
mx   = OmegaConf.load('/work/src/RVT/config/model/maxvit_yolox/default.yaml')['model']
cfg  = OmegaConf.merge(base.get('model', base), rnn, mx)
with open_dict(cfg):
    cfg.backbone.embed_dim = 32; cfg.fpn.depth = 0.33
    cfg.backbone.in_res_hw = [256, 320]
    cfg.backbone.stage.attention.partition_size = [4, 5]
    cfg.head.num_classes = 2
mdl = YoloXDetector(cfg)
ck = torch.load('/work/data/ckpt/rvt-t-gen1.ckpt', map_location='cpu', weights_only=False)
mdl.load_state_dict({k[4:]: v for k, v in ck['state_dict'].items() if k.startswith('mdl.')}, strict=True)
mdl.eval()

torch.manual_seed(0)
x = (torch.rand(1, 20, 256, 320) < 0.02).float() * torch.randint(1, 4, (1, 20, 256, 320)).float()

def feat(t):
    with torch.no_grad():
        return mdl.forward(t, previous_states=None)[0]

ref = feat(x)
keys = list(ref.keys()) if hasattr(ref, 'keys') else range(len(ref))
print("MASKLEAD nbins w_P_ms relL2")
for nmask in range(0, 10):
    xm = x.clone()
    for b in range(nmask):
        xm[:, 2*b:2*b+2] = 0          # zero the OLDEST bins -> narrower window
    out = feat(xm)
    num = sum(((out[k]-ref[k])**2).sum() for k in keys)
    den = sum((ref[k]**2).sum() for k in keys)
    print(f"MASKLEAD {nmask} {50-5*nmask} {(num/den).sqrt().item():.4f}")

print("MASKONE bin t_center_ms relL2   # single-bin occlusion = influence profile")
for b in range(10):
    xm = x.clone(); xm[:, 2*b:2*b+2] = 0
    out = feat(xm)
    num = sum(((out[k]-ref[k])**2).sum() for k in keys)
    den = sum((ref[k]**2).sum() for k in keys)
    print(f"MASKONE {b} {-(50-5*b-2.5):.1f} {(num/den).sqrt().item():.4f}")
