"""E63 -- what the port of each released checkpoint is, and is not, verified to reproduce.

The manuscript's predictor measurements run on a port: the released checkpoints loaded into
models rebuilt from each repository's own configuration files and run under a current
framework, without the training code they were serialized from. Review #11 objected that the
port was validated only by a key count, which is a structural check and not a numerical one.

This script supplies the numerical checks that need no GPU:

  1. the parameter count each checkpoint actually carries, read from the tensors themselves,
  2. the split's mAP recomputed by `pycocotools`, an implementation this project did not
     write, against this paper's own evaluator on the identical detection dump.

What it deliberately does not claim is a reproduction of the published table. Those numbers
are reported on the Gen1 *test* split; the release distribution available here carries the
validation split alone (429 sequences, no test directory), so the level reported below is a
validation-split level and is compared with the published one only in ordering.
"""
import numpy as np, json, os, glob, io, contextlib

MODELS = ['rvt-t', 'rvt-s', 'rvt-b', 's5vit-small', 's5vit-base']
# Published Gen1 mAP, test split, as printed by each paper. Recorded for the ordering check.
PUBLISHED = {'rvt-t': 44.1, 'rvt-s': 46.5, 'rvt-b': 47.2,
             's5vit-small': 46.6, 's5vit-base': 47.7}
# Published parameter counts, in millions, as printed by the same two papers. These are a
# published quantity the port can be held against without the test split.
PUB_PARAMS = {'rvt-t': 4.4, 'rvt-s': 9.9, 'rvt-b': 18.5,
              's5vit-small': 9.7, 's5vit-base': 18.2}
OUT = 'experiments/e63_port/parity.json'


def params(ckpt):
    import torch
    sd = torch.load(ckpt, map_location='cpu', weights_only=False)
    sd = sd.get('state_dict', sd)
    n = sum(v.numel() for v in sd.values() if hasattr(v, 'numel'))
    return n, len(sd)


def coco_map(det, gt, maxdet=100):
    """AP@[.50:.95] by pycocotools, on the same arrays this paper's evaluator reads."""
    from pycocotools.coco import COCO
    from pycocotools.cocoeval import COCOeval
    imgs = sorted(set(gt[:, 0].astype(int)) | set(det[:, 0].astype(int)))
    G = dict(images=[dict(id=int(i)) for i in imgs],
             categories=[dict(id=int(c)) for c in sorted(set(gt[:, 5].astype(int)))],
             annotations=[])
    for k, r in enumerate(gt):
        w, h = r[3] - r[1], r[4] - r[2]
        G['annotations'].append(dict(id=k + 1, image_id=int(r[0]), category_id=int(r[5]),
                                     bbox=[float(r[1]), float(r[2]), float(w), float(h)],
                                     area=float(w * h), iscrowd=0))
    D = [dict(image_id=int(r[0]), category_id=int(r[6]),
              bbox=[float(r[1]), float(r[2]), float(r[3] - r[1]), float(r[4] - r[2])],
              score=float(r[5])) for r in det]
    with contextlib.redirect_stdout(io.StringIO()):
        c = COCO(); c.dataset = G; c.createIndex()
        e = COCOeval(c, c.loadRes(D), 'bbox'); e.params.maxDets = [1, 10, maxdet]
        e.evaluate(); e.accumulate(); e.summarize()
    return 100 * e.stats[0], 100 * e.stats[1]


if __name__ == '__main__':
    import sys
    sys.path.insert(0, 'src')
    from e56_eval import Scorer
    rows = {}
    for m in MODELS:
        Z = np.load(f'experiments/e51_ranking/dets-{m}.npz')
        det, gt = Z['det'].astype(np.float64), Z['gt'].astype(np.float64)
        ap, ap50 = coco_map(det, gt)
        own = 100 * Scorer(det, gt).evaluate(0.0, require_velocity=False)
        n, keys = params(f'data/ckpt/{m}-gen1.ckpt')
        rows[m] = dict(coco_ap=ap, coco_ap50=ap50, own_ap=own, gap=abs(ap - own),
                       params_m=n / 1e6, tensors=keys, published_test=PUBLISHED[m],
                       published_params_m=PUB_PARAMS[m],
                       params_dev=abs(n / 1e6 - PUB_PARAMS[m]),
                       n_det=int(len(det)))
        print(f"{m:<14} params {n/1e6:6.2f} M  pycocotools {ap:6.3f}  this paper {own:6.3f}"
              f"  |diff| {abs(ap-own):.3f}")
    gaps = [r['gap'] for r in rows.values()]
    pdev = max(r['params_dev'] for r in rows.values())
    print(f"\n  largest deviation from a published parameter count: {pdev:.3f} M")
    ordr = [m for m in sorted(rows, key=lambda k: -rows[k]['coco_ap'])]
    opub = [m for m in sorted(rows, key=lambda k: -rows[k]['published_test'])]
    rvt = [m for m in ordr if m.startswith('rvt')]
    rvt_pub = [m for m in opub if m.startswith('rvt')]
    print(f"\n  largest disagreement between the two evaluators: {max(gaps):.3f} points")
    print(f"  ordering here     {' > '.join(ordr)}")
    print(f"  published (test)  {' > '.join(opub)}")
    print(f"  within RVT the two orderings agree: {rvt == rvt_pub}")
    nseq = len(glob.glob('data/gen1x/gen1/val/*'))
    print(f"  split available locally: val only, {nseq} sequences; "
          f"test present: {os.path.isdir('data/gen1x/gen1/test')}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(dict(rows=rows, max_gap=float(max(gaps)), max_params_dev=float(pdev), order=ordr, order_published=opub,
                   rvt_order_agrees=bool(rvt == rvt_pub), val_sequences=nseq,
                   test_split_present=os.path.isdir('data/gen1x/gen1/test')),
              open(OUT, 'w'), indent=1)
    print(f"WROTE {OUT}")
