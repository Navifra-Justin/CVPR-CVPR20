"""E70 port parity on 1 Mpx val. Reads released-protocol (SHIFT=0) dumps and reports, per model:
 (1) this project's evaluator (src/e56_eval.Scorer, all labelled boxes, no displacement),
 (2) pycocotools on the same arrays (src/e63_port_parity.coco_map),
 (3) the same with the Prophesee box filter applied to GT and detections (min diagonal 30 px and min side 10 px at
     the 360x640 working scale; the 0.5 s skip of the official evaluator is NOT applied because dumps carry no times),
and prints the published TEST-split mAP next to them for ordering only (val != test).
Published: arXiv:2212.05598 Table 6 (RVT-B 47.4, RVT-S 44.1, RVT-T 41.5) and arXiv:2402.15584 (S5-ViT-B 47.8, S5-ViT-S 46.5), 1 Mpx column.
usage: python3 src/e70_1mpx_parity.py experiments/e70_1mpx/dets-s5vit-base-shift0.npz ...
"""
import sys, json, numpy as np
sys.path.insert(0, 'src')
from e56_eval import Scorer
from e63_port_parity import coco_map
PUB = {'rvt-t': 41.5, 'rvt-s': 44.1, 'rvt-b': 47.4, 's5vit-small': 46.5, 's5vit-base': 47.8}


def filt(a, c):  # a: rows with x1,y1,x2,y2 at columns c..c+3
    w, h = a[:, c + 2] - a[:, c], a[:, c + 3] - a[:, c + 1]
    return (w * w + h * h >= 30 ** 2) & (w >= 10) & (h >= 10)


rows = {}
for p in sys.argv[1:]:
    Z = np.load(p); det = Z['det'].astype(np.float64); gt = Z['gt'].astype(np.float64)
    name = p.split('dets-')[-1].split('-shift')[0]
    own = Scorer(det, gt).evaluate(0.0, require_velocity=False) * 100
    cap, cap50 = coco_map(det, gt)
    gf = gt[filt(gt, 1)]; df = det[filt(det, 1)]
    ownf = Scorer(df, gf).evaluate(0.0, require_velocity=False) * 100
    capf, _ = coco_map(df, gf)
    key = name.split('-carry')[0].split('-reset')[0]
    rows[name] = dict(frames=int(gt[:, 0].max()) + 1, boxes=len(gt), dets=len(det), own_map=own, coco_ap=cap, own_map_filtered=ownf,
                      coco_ap_filtered=capf, published_test=PUB.get(key))
    print(name, json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in rows[name].items()}), flush=True)
