"""E72 - reset-policy audit of public recurrent event-detector repositories.

For each checkpoint: run the repository's own streaming call over a validation sequence from its first window, carrying the
recurrent state exactly as the repository's evaluation does (reference arm). At a chunk start c (c = k*CHUNK, k=1..NCHUNK) re-run
the chunk with the state entering it replaced by the initial (zero / None) state (zero arm). Output compared per position p in the chunk:
    rel(p) = ||o_zero(p) - o_ref(p)||_2 / ||o_ref(p)||_2
on the raw network output of the repository (RVT/S5-ViT/SAST: YOLOX head tensor before NMS; EvRT-DETR: RT-DETR decoder
pred_logits and pred_boxes concatenated), averaged over chunks and sequences.
rel(0) == 0 and rel(p>0) == 0  -> the state entering a chunk never reaches the output (measured policy: reset at chunk start / state inert)
rel(0) > 0                    -> the state entering the chunk is used (measured policy: carried across the chunk boundary)
Arm B (control): occlude (zero) the window one position earlier and read position p; shows that the model is recurrent within the chunk.
Env: FAM (rvt|ssm|evrt|sast) TAG DEV NSEQ CHUNK NCHUNK OUT
"""
import sys, os, glob, json, numpy as np, torch, h5py, hdf5plugin
FAM = os.environ['FAM']; TAG = os.environ.get('TAG', 's'); DEV = os.environ.get('DEV', 'cpu')
NSEQ = int(os.environ.get('NSEQ', '8')); CHUNK = int(os.environ.get('CHUNK', '21')); NCHUNK = int(os.environ.get('NCHUNK', '4'))
if os.environ.get('THREADS'): torch.set_num_threads(int(os.environ['THREADS']))
DATA = os.environ.get('DATA', '/work/data/gen1x/gen1/val'); H0, W0 = int(os.environ.get('HP', '256')), int(os.environ.get('WP', '320'))
name = {'rvt': f'rvt-{TAG}', 'ssm': f's5vit-{TAG}', 'evrt': f'evrtdetr-{TAG}', 'sast': f'sast-{TAG}'}[FAM]
def pad(t): return torch.nn.functional.pad(t, (0, W0 - t.shape[-1], 0, H0 - t.shape[-2]))
TP = '/work/experiments/e72_reset_audit/third_party'
if FAM in ('rvt', 'ssm', 'sast'):
    sys.path.insert(0, {'rvt': '/work/src/RVT', 'ssm': '/work/src/SSMViT', 'sast': f'{TP}/SAST'}[FAM])
    from omegaconf import OmegaConf, open_dict
    from models.detection.yolox_extension.models.detector import YoloXDetector
    R = {'rvt': '/work/src/RVT', 'ssm': '/work/src/SSMViT', 'sast': f'{TP}/SAST'}[FAM] + '/config/model'
    base = OmegaConf.load(f'{R}/base.yaml'); rnn = OmegaConf.load(f'{R}/rnndet.yaml')
    if FAM == 'sast': mx = OmegaConf.load(f'{R}/sast_yolox/default.yaml')['model']
    else: mx = OmegaConf.load(f'{R}/maxvit_yolox/default.yaml')['model']
    cfg = OmegaConf.merge(base.get('model', base), rnn, mx)
    if FAM == 'ssm':
        cfg = OmegaConf.merge(cfg, OmegaConf.load(f'/work/src/SSMViT/config/experiment/gen1/{TAG}.yaml')['model'])
        CK = f'/work/data/ckpt/s5vit-{TAG}-gen1.ckpt'
    elif FAM == 'rvt':
        C = {'t': (32, 32, 0.33), 's': (48, 24, 0.33), 'b': (64, 32, 0.67)}[TAG]
        with open_dict(cfg): cfg.backbone.embed_dim = C[0]; cfg.backbone.stage.attention.dim_head = C[1]; cfg.fpn.depth = C[2]
        CK = f'/work/data/ckpt/rvt-{TAG}-gen1.ckpt'
    if FAM != 'sast':
        with open_dict(cfg):
            cfg.backbone.in_res_hw = [256, 320]; cfg.backbone.stage.attention.partition_size = [4, 5]; cfg.head.num_classes = 2
        mdl = YoloXDetector(cfg)
        sd_ = torch.load(CK, map_location='cpu', weights_only=False)['state_dict']
        mdl.load_state_dict({k[4:]: v for k, v in sd_.items() if k.startswith('mdl.')}, strict=True)
        mdl.eval().to(DEV)
    else:
        raise SystemExit('sast: construct via src config of the repository (see run script)')
    def run_chunk(xs, st):
        outs = []
        with torch.no_grad():
            if FAM == 'ssm':
                feats, st = mdl.forward_backbone(xs[:, None], previous_states=st, train_step=False)
                outs = [mdl.forward_detect({k: v[p] for k, v in feats.items()})[0] for p in range(xs.shape[0])]
            else:
                for p in range(xs.shape[0]):
                    o, _, st = mdl.forward(xs[p][None], previous_states=st); outs.append(o)
        return outs, st
    def clone_states(st):
        if st is None: return None
        if torch.is_tensor(st): return st.detach().clone()
        if isinstance(st, (list, tuple)): return type(st)(clone_states(x) for x in st)
        if isinstance(st, dict): return {k: clone_states(v) for k, v in st.items()}
        return st
    flat = lambda o: o
else:
    sys.path.insert(0, f'{TP}/evrt-detr')
    from evlearn.eval.eval import load_model
    args, model = load_model(f'/work/experiments/e72_reset_audit/ckpt/video_evrtdetr_presnet18', None, device=DEV)
    model.eval(); nets = model._nets
    assert not model._train_state
    def run_chunk(xs, st):
        with torch.no_grad():
            enc = model.encode_clip_frames(xs[:, None].to(DEV))
            mask = torch.zeros((len(enc), 1), dtype=torch.bool, device=DEV)
            tenc, st = model.encode_temporal_dependencies(enc, mask, st)
            outs = []
            for t in tenc:
                d = nets.decoder(t)
                outs.append(torch.cat([d['pred_logits'].sigmoid().flatten(), d['pred_boxes'].flatten()]))
        return outs, st
    def clone_states(st):
        if st is None: return None
        return model._nets.temp_enc.detach_mem(st) if False else __import__('copy').deepcopy(st)

def evrt_view(o):
    """order-invariant view of an RT-DETR output (queries are top-k selected from encoder tokens, so query index i is not the same
    object in two runs): returns (class-wise sigmoid scores (nq,2), boxes cxcywh (nq,4))"""
    nq = o.numel() // 6; return o[:nq * 2].view(nq, 2), o[nq * 2:].view(nq, 4)
def evrt_sorted_rel(a, b, top=100):
    sa = evrt_view(a)[0].max(1).values.sort(descending=True).values[:top]; sb = evrt_view(b)[0].max(1).values.sort(descending=True).values[:top]
    return float((sa - sb).norm() / max(float(sa.norm()), 1e-12))
def evrt_unmatched(a, b, thr=0.25):
    """share of confident detections (score>=thr) of the reference that have no same-class IoU>=0.5 partner among confident detections of b, symmetrised"""
    def dets(o):
        sc, bx = evrt_view(o); m = sc.max(1); k = m.values >= thr
        c = torch.stack([bx[:, 0] - bx[:, 2] / 2, bx[:, 1] - bx[:, 3] / 2, bx[:, 0] + bx[:, 2] / 2, bx[:, 1] + bx[:, 3] / 2], 1)[k]
        return c, m.indices[k]
    (ca, la), (cb, lb) = dets(a), dets(b)
    if len(ca) + len(cb) == 0: return 0.0
    if len(ca) == 0 or len(cb) == 0: return 1.0
    lt = torch.max(ca[:, None, :2], cb[None, :, :2]); rb = torch.min(ca[:, None, 2:], cb[None, :, 2:]); wh = (rb - lt).clamp(min=0)
    it = wh[..., 0] * wh[..., 1]; ar = lambda c: (c[:, 2] - c[:, 0]) * (c[:, 3] - c[:, 1])
    iou = it / (ar(ca)[:, None] + ar(cb)[None] - it).clamp(min=1e-9); iou = torch.where(la[:, None] == lb[None], iou, torch.zeros_like(iou))
    ma = (iou.max(1).values >= 0.5).float().sum(); mb = (iou.max(0).values >= 0.5).float().sum()
    return float(1 - (ma + mb) / (len(ca) + len(cb)))
EFFO = [[] for _ in range(CHUNK)]; EFFU = [[] for _ in range(CHUNK)]; INO = [[] for _ in range(CHUNK)]; INU = [[] for _ in range(CHUNK)]
NSC = None  # number of leading elements that are class scores (EvRT-DETR only)
EFF = [[] for _ in range(CHUNK)]; EFFS = [[] for _ in range(CHUNK)]; CTRL = []; INCH = [[] for _ in range(CHUNK)]; nchunks = 0
for si, sd in enumerate(sorted(glob.glob(f'{DATA}/*'))[:NSEQ]):
    h5 = os.path.join(sd, 'event_representations_v2', 'stacked_histogram_dt=50_nbins=10', 'event_representations.h5')
    if not os.path.exists(h5): continue
    with h5py.File(h5, 'r') as f:
        D = f[list(f.keys())[0]]; n = min(D.shape[0], CHUNK * (NCHUNK + 1))
        if n < CHUNK * 2: continue
        X = torch.stack([pad(torch.from_numpy(np.asarray(D[i], dtype=np.float32))[None])[0] for i in range(n)]).to(DEV)
    st = None
    for c in range(n // CHUNK):
        xs = X[c * CHUNK:(c + 1) * CHUNK]; prev_enter = clone_states(st)
        ref, st = run_chunk(xs, st)
        if c == 0: continue
        o0, _ = run_chunk(xs, None); nchunks += 1
        oc, _ = run_chunk(xs, clone_states(prev_enter))        # control: same chunk, same entering state -> must be 0 (determinism of the instrument)
        CTRL.append(max(float((oc[p] - ref[p]).norm()) / max(float(ref[p].norm()), 1e-12) for p in range(CHUNK)))
        for p in range(CHUNK):
            rn = float(ref[p].norm())
            if rn > 1e-6: EFF[p].append(float((o0[p] - ref[p]).norm()) / rn)
            if FAM == 'evrt':
                k = ref[p].numel() // 3          # 300 queries x (2 class scores + 4 box values) -> first third holds the class scores
                rs = float(ref[p][:k].norm())
                if rs > 1e-6: EFFS[p].append(float((o0[p][:k] - ref[p][:k]).norm()) / rs)
                EFFO[p].append(evrt_sorted_rel(ref[p], o0[p])); EFFU[p].append(evrt_unmatched(ref[p], o0[p]))
        for p in (1, 5, 10, CHUNK - 1):
            if p >= CHUNK: continue
            rn = float(ref[p].norm())
            if rn < 1e-6: continue
            xm = xs.clone(); xm[p - 1] = 0
            om, _ = run_chunk(xm, clone_states(prev_enter))
            INCH[p].append(float((om[p] - ref[p]).norm()) / rn)
            if FAM == 'evrt': INO[p].append(evrt_sorted_rel(ref[p], om[p])); INU[p].append(evrt_unmatched(ref[p], om[p]))
    print(f'  seq {si + 1}, {nchunks} chunks', flush=True)
m = [float(np.mean(v)) if v else None for v in EFF]; ms = [float(np.mean(v)) if v else None for v in EFFS]; mi = [float(np.mean(v)) if v else None for v in INCH]
print(f'\n{name}: relative L2 change of the output by position, state entering the chunk zeroed; chunk {CHUNK}, {nchunks} chunk starts')
for p in range(CHUNK):
    print(f'  p={p:2d}  zero-entering-state {m[p]:.3e} (scores only {ms[p] if ms[p] is None else "%.3e" % ms[p]})   occlude-previous-window {("%.3e" % mi[p]) if mi[p] is not None else "-"}')
out = os.environ.get('OUT', f'/work/experiments/e72_reset_audit/audit-{name}.json')
json.dump(dict(model=name, family=FAM, chunk=CHUNK, n_chunk_starts=nchunks, nseq=NSEQ, effect_by_position=m, effect_scores_only=ms, effect_sorted_scores=[float(np.mean(v)) if v else None for v in EFFO], effect_unmatched_dets=[float(np.mean(v)) if v else None for v in EFFU], inchunk_sorted_scores=[float(np.mean(v)) if v else None for v in INO], inchunk_unmatched_dets=[float(np.mean(v)) if v else None for v in INU], control_max_rel=max(CTRL) if CTRL else None, inchunk_by_position=mi),
          open(out, 'w'), indent=1, allow_nan=False); print('WROTE', out)
print('control (same entering state re-run), max rel over positions and chunks:', max(CTRL) if CTRL else None)
