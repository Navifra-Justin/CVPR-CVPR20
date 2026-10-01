"""E66 - per-frame fixed-H dump: every checkpoint scored with EXACTLY H windows of history.

Derived from src/e51_dump_all.py (which is untouched). The released protocols give a frame a
history that depends on where it falls in the evaluation chunk, so "mAP of checkpoint X" is a
mixture over H = 1..21 whose weights differ between releases. This dumper removes that
confound: for every labelled frame at window index ri and every H in HS, the model is run on
the windows ri-H+1 .. ri only, from a fresh (None) recurrent state, and the detections of the
LAST window are kept. Whatever happened before ri-H+1 is never seen (reset).

  FAM=rvt  one window per call, state carried inside the H-window run (RVT release call),
           state started from None at the first of the H windows.
  FAM=ssm  one chunk of H windows through forward_backbone with fresh state and the head
           applied at the last position (SSM-ViT release call; chunk of length H).

H_nominal is the requested H; H_forced = min(H, ri+1) is what the frame could actually be
given (a frame with fewer than H preceding windows cannot have H). Both are stored, and the
common-frame analysis keeps only frames with H_forced == max(HS) for every H (21 history).

Ground truth, frame admission, label linking and the frame counter are copied verbatim from
e51_dump_all.py so frame ids line up with the e51 / e65 dumps over the same sequence prefix.

Resumable: each sequence is written to <OUT>.parts/seqNNNN.npz and skipped if present; the
final npz is assembled from the parts (frame ids renumbered in sequence order).

Audit trail written into every part (checked by src/e66_verify.py): `ev` which (frame,H)
cells were run, `eff_first`/`eff_n` the first window index and the number of distinct windows
that were actually read for each cell (recorded by an access log around the window loader, not
derived from the formula), and with PROBE=k a sensitivity probe: the oldest window of the first
k admissible cells is replaced by zeros and the last-window output must change (support is
really used), plus a hash of all weights before and after the run (weights untouched by H).

Env: FAM TAG DEV NSEQ HS(1,5,10,21) BATCH STRIDE(use every k-th labelled frame, gate only)
     OUT THREADS PROBE
"""
import sys, os, glob, numpy as np, torch, h5py, hdf5plugin, time
FAM = os.environ.get('FAM', 'rvt'); TAG = os.environ.get('TAG', 's')
DEV = os.environ.get('DEV', 'cuda:0'); NSEQ = int(os.environ.get('NSEQ', '1000'))
HS = [int(h) for h in os.environ.get('HS', '1,5,10,21').split(',')]
BATCH = int(os.environ.get('BATCH', '8' if FAM == 'ssm' else '16'))
STRIDE = int(os.environ.get('STRIDE', '1'))
PROBE = int(os.environ.get('PROBE', '0'))
if os.environ.get('THREADS'): torch.set_num_threads(int(os.environ['THREADS']))
NAME = (f'rvt-{TAG}' if FAM == 'rvt' else f's5vit-{TAG}')
OUT = os.environ.get('OUT', f'/work/experiments/e66_fixedH/dets-{NAME}.npz')
PARTS = OUT[:-4] + '.parts'
assert FAM in ('rvt', 'ssm')
sys.path.insert(0, '/work/src/SSMViT' if FAM == 'ssm' else '/work/src/RVT')
from omegaconf import OmegaConf, open_dict
from models.detection.yolox_extension.models.detector import YoloXDetector
from models.detection.yolox.utils.boxes import postprocess
CONF = 0.01; NMS = 0.65; LINK_IOU = 0.3

R = '/work/src/SSMViT/config/model' if FAM == 'ssm' else '/work/src/RVT/config/model'
base = OmegaConf.load(f'{R}/base.yaml'); rnn = OmegaConf.load(f'{R}/rnndet.yaml')
mx = OmegaConf.load(f'{R}/maxvit_yolox/default.yaml')['model']
cfg = OmegaConf.merge(base.get('model', base), rnn, mx)
if FAM == 'ssm':
    cfg = OmegaConf.merge(cfg, OmegaConf.load(
        f'/work/src/SSMViT/config/experiment/gen1/{TAG}.yaml')['model'])
    CK = f'/work/data/ckpt/s5vit-{TAG}-gen1.ckpt'
else:
    C = {'t': (32, 32, 0.33), 's': (48, 24, 0.33), 'b': (64, 32, 0.67)}[TAG]
    with open_dict(cfg):
        cfg.backbone.embed_dim = C[0]; cfg.backbone.stage.attention.dim_head = C[1]
        cfg.fpn.depth = C[2]
    CK = f'/work/data/ckpt/rvt-{TAG}-gen1.ckpt'
with open_dict(cfg):
    cfg.backbone.in_res_hw = [256, 320]; cfg.backbone.stage.attention.partition_size = [4, 5]
    cfg.head.num_classes = 2
mdl = YoloXDetector(cfg)
sd_ = torch.load(CK, map_location='cpu', weights_only=False)['state_dict']
mdl.load_state_dict({k[4:]: v for k, v in sd_.items() if k.startswith('mdl.')}, strict=True)
mdl.eval().to(DEV)
import hashlib
def whash():
    h = hashlib.sha256()
    for k, v in sorted(mdl.state_dict().items()): h.update(k.encode()); h.update(v.detach().cpu().numpy().tobytes())
    return h.hexdigest()
W0 = whash()
print(f"WEIGHTS_SHA256 {W0}  ckpt {CK}", flush=True)
print(f"{NAME}: {sum(p.numel() for p in mdl.parameters())/1e6:.2f}M params, fixed H {HS}, "
      f"batch {BATCH}, stride {STRIDE}, dev {DEV}", flush=True)


def pad(t): return torch.nn.functional.pad(t, (0, 320 - t.shape[-1], 0, 256 - t.shape[-2]))


def iou1(a, B):
    x1 = np.maximum(a[0], B[:, 0]); y1 = np.maximum(a[1], B[:, 1])
    x2 = np.minimum(a[2], B[:, 2]); y2 = np.minimum(a[3], B[:, 3])
    w = np.clip(x2 - x1, 0, None); h = np.clip(y2 - y1, 0, None); it = w * h
    return it / np.maximum((a[2] - a[0]) * (a[3] - a[1]) + (B[:, 2] - B[:, 0]) * (B[:, 3] - B[:, 1]) - it, 1e-9)


def run_group(get0, ris, Hf, override=None):
    """Detections for the last window of each ri with history Hf, plus the access log.
    override: optional (t, array-index-in-group) -> tensor replacing that window (probe only)."""
    ris = np.asarray(ris); acc = [set() for _ in ris]; bi = {int(r): n for n, r in enumerate(ris)}
    def get_for(n, i):
        acc[n].add(int(i))
        if override is not None and override[0] == (n, i): return override[1]
        return get0(i)
    if FAM == 'rvt':
        states = None
        for t in range(Hf):
            x = torch.stack([get_for(n, int(r) - Hf + 1 + t) for n, r in enumerate(ris)]).to(DEV)
            assert t > 0 or states is None
            with torch.no_grad(): o, _, states = mdl.forward(x, previous_states=states)
    else:
        xs = torch.stack([torch.stack([get_for(n, int(r) - Hf + 1 + t) for n, r in enumerate(ris)])
                          for t in range(Hf)]).to(DEV)                    # (T,B,C,H,W)
        with torch.no_grad():
            feats, _ = mdl.forward_backbone(xs, previous_states=None, train_step=False)
            o = mdl.forward_detect({k: v[-1] for k, v in feats.items()})[0]
    res = postprocess(o.clone(), 2, CONF, NMS)
    return [None if d is None else d.cpu().numpy() for d in res], acc


os.makedirs(PARTS, exist_ok=True)
t0 = time.time(); nfr = 0
for si, sd in enumerate(sorted(glob.glob('/work/data/gen1x/gen1/val/*'))[:NSEQ]):
    rd = os.path.join(sd, 'event_representations_v2', 'stacked_histogram_dt=50_nbins=10')
    try:
        L = np.load(os.path.join(sd, 'labels_v2', 'labels.npz'))['labels']
        o2r = np.load(os.path.join(rd, 'objframe_idx_2_repr_idx.npy'))
    except Exception: continue
    if len(o2r) < 3: continue
    pf = os.path.join(PARTS, f'seq{si:04d}.npz')
    ts = np.sort(np.unique(L['t'])); B = []; C = []; CL = []
    for t in ts:
        G = L[L['t'] == t]
        bb = np.column_stack([G['x'], G['y'], G['x'] + G['w'], G['y'] + G['h']]).astype(float)
        B.append(bb); C.append(np.column_stack([(bb[:, 0] + bb[:, 2]) / 2, (bb[:, 1] + bb[:, 3]) / 2]))
        CL.append(np.asarray(G['class_id']))
    if os.path.exists(pf): continue
    fwd = []
    for k in range(len(ts) - 1):
        m = -np.ones(len(B[k]), dtype=int)
        for i in range(len(B[k])):
            same = (CL[k][i] == CL[k + 1])
            if not same.any(): continue
            io = np.where(same, iou1(B[k][i], B[k + 1]), 0.0); j = int(np.argmax(io))
            if io[j] >= LINK_IOU: m[i] = j
        fwd.append(m)
    fwd.append(-np.ones(len(B[-1]), dtype=int))
    prev = [-np.ones(len(B[k]), dtype=int) for k in range(len(ts))]
    for k in range(len(ts) - 1):
        for i, j in enumerate(fwd[k]):
            if j >= 0: prev[k + 1][j] = i
    cache = {}
    with h5py.File(os.path.join(rd, 'event_representations.h5'), 'r') as f:
        D = f[list(f.keys())[0]]
        def get(i):
            if i not in cache: cache[i] = pad(torch.from_numpy(D[i][None]).float())[0]
            return cache[i]
        want = {int(o2r[i]): i for i in range(min(len(o2r), len(ts)))}
        ris = sorted(want)                         # frame order of e51 (sorted by window index)
        nF = len(ris)
        hf = np.array([[min(h, r + 1) for h in HS] for r in ris], dtype=np.int16)
        DET = {h: [] for h in HS}
        ev = np.zeros((nF, len(HS)), dtype=bool); eff_first = -np.ones((nF, len(HS)), np.int32)
        eff_n = np.zeros((nF, len(HS)), np.int16); probes = []
        todo = [j for j in range(nF) if j % STRIDE == 0 and ris[j] < D.shape[0]]   # e51 emits no detections past the array
        done = np.zeros(nF, dtype=bool); done[todo] = True
        for b0 in range(0, len(todo), BATCH):
            bj = todo[b0:b0 + BATCH]
            lo = min(ris[j] for j in bj) - max(HS)
            for kk in [k for k in cache if k < lo]: del cache[kk]
            for hi_, h in enumerate(HS):
                groups = {}
                for j in bj: groups.setdefault(int(hf[j, hi_]), []).append(j)
                for Hf, js in groups.items():
                    dets, acc = run_group(get, [ris[j] for j in js], Hf)
                    for j, d, a_ in zip(js, dets, acc):
                        ev[j, hi_] = True; eff_first[j, hi_] = min(a_); eff_n[j, hi_] = len(a_)
                        assert a_ == set(range(ris[j] - Hf + 1, ris[j] + 1)), (j, h, sorted(a_))
                        if PROBE and len(probes) < PROBE * len(HS) and Hf == h and h >= 2 and \
                                sum(1 for q in probes if q[1] == h) < PROBE:
                            z = torch.zeros_like(get(ris[j] - Hf + 1))
                            d1, _ = run_group(get, [ris[j]], Hf)          # batch-1 reference
                            d2, _ = run_group(get, [ris[j]], Hf, override=((0, ris[j] - Hf + 1), z))
                            r1, a2 = d1[0], d2[0]
                            same = (r1 is None and a2 is None) or (r1 is not None and a2 is not None
                                    and r1.shape == a2.shape and np.array_equal(r1, a2))
                            probes.append((j, h, not same))
                        if d is None: continue
                        sc = d[:, 4] * d[:, 5]
                        for r in range(len(d)):
                            DET[h].append((j, d[r, 0], d[r, 1], d[r, 2], d[r, 3], sc[r], d[r, 6]))
    GT = []
    for j, ri in enumerate(ris):
        k = want[ri]
        for gi in range(len(B[k])):
            jf = fwd[k][gi]; jb = prev[k][gi]
            if jf >= 0 and jb >= 0:
                dt = (ts[k + 1] - ts[k - 1]) * 1e-6
                vx, vy = (C[k + 1][jf] - C[k - 1][jb]) / dt
            else: vx = vy = np.nan
            GT.append((j, B[k][gi, 0], B[k][gi, 1], B[k][gi, 2], B[k][gi, 3], CL[k][gi], vx, vy))
    part = dict(gt=np.array(GT, dtype=np.float32), ri=np.array(ris, dtype=np.int32),
                hforced=hf, done=done, ev=ev, eff_first=eff_first, eff_n=eff_n,
                probe=np.array(probes, dtype=np.int32).reshape(-1, 3))
    for h in HS: part[f'det_h{h}'] = np.array(DET[h], dtype=np.float32).reshape(-1, 7)
    np.savez_compressed(pf + '.tmp.npz', **part); os.replace(pf + '.tmp.npz', pf)
    nfr += len(todo)
    print(f"  seq {si} frames {len(todo)} total {nfr} elapsed {time.time()-t0:.0f}s", flush=True)

# assemble (frame ids renumbered in sequence order; sequence index = directory order index)
parts = sorted(glob.glob(os.path.join(PARTS, 'seq*.npz')))
G = []; RI = []; HF = []; SEQ = []; DN = []; DT = {h: [] for h in HS}; off = 0
for p in parts:
    si = int(os.path.basename(p)[3:7]); Z = np.load(p)
    n = len(Z['ri']); g = Z['gt'].copy(); g[:, 0] += off; G.append(g)
    for h in HS:
        d = Z[f'det_h{h}'].copy(); d[:, 0] += off; DT[h].append(d)
    RI.append(Z['ri']); HF.append(Z['hforced']); DN.append(Z['done']); SEQ.append(np.full(n, si, np.int32))
    off += n
EV = []; EF = []; EN = []; PR = []
for p in parts:
    Z = np.load(p); EV.append(Z['ev']); EF.append(Z['eff_first']); EN.append(Z['eff_n']); PR.append(Z['probe'])
W1 = whash(); print(f"WEIGHTS_SHA256_END {W1}  unchanged {W0 == W1}", flush=True)
out = dict(weights_sha=np.array([W0, W1]), ev=np.concatenate(EV), eff_first=np.concatenate(EF),
           eff_n=np.concatenate(EN), probe=np.concatenate(PR), gt=np.concatenate(G), ri=np.concatenate(RI), hforced=np.concatenate(HF),
           hnominal=np.array(HS, dtype=np.int16), seq=np.concatenate(SEQ),
           done=np.concatenate(DN))
for h in HS: out[f'det_h{h}'] = np.concatenate(DT[h])
np.savez_compressed(OUT + '.tmp.npz', **out); os.replace(OUT + '.tmp.npz', OUT)
print(f"WROTE {OUT}  frames {off}  " + "  ".join(f"H{h}:{len(out[f'det_h{h}'])}" for h in HS), flush=True)
try:
    print(f"PEAK_VRAM_BYTES {torch.cuda.max_memory_allocated()}", flush=True)
except Exception as e: print(f"PEAK_VRAM unavailable: {e}", flush=True)
