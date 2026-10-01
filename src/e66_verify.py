"""E66 pre-queue verification of a small fixed-H dump (one model, a validation subset).

  python3 src/e66_verify.py <e66 dump> [<e65 or e51 dump to compare ground truth with>]

(1) the evaluated frame-id set is one object shared by every H: `ev` columns equal, equal to `done`,
    and detections only refer to those frames
(2) labels: one gt array serves every H (a single key), equals the reference dump's gt on the prefix
(3) weights: sha256 of all parameters before == after the whole run
(4) state init is the only thing that varies with H: every cell read exactly the windows
    ri-H_forced+1..ri (access log), first read = ri-H_forced+1, i.e. nothing earlier reached the
    model, and starting state was None (asserted in the dumper at the first step of each group)
(5) effective support count == specified H for every cell whose H_forced == H, and the oldest-window
    probe changed the output in every probed cell
"""
import sys, numpy as np
Z = np.load(sys.argv[1]); HS = [int(h) for h in Z['hnominal']]
ok = True
def chk(c, m):
    global ok; ok = ok and bool(c); print(('  [PASS] ' if c else '  [FAIL] ') + m)
ev, done, hf, ri = Z['ev'], Z['done'], Z['hforced'], Z['ri']
chk(all(np.array_equal(ev[:, i], done) for i in range(len(HS))), f'(1) evaluated frame set identical for H={HS}: {int(done.sum())} frames of {len(done)}')
fid_ok = all(set(np.unique(Z[f'det_h{h}'][:, 0]).astype(int)) <= set(np.flatnonzero(done)) for h in HS)
chk(fid_ok, '(1) detection frame ids are a subset of the evaluated set for every H')
chk(sum(1 for k in Z.files if k == 'gt') == 1, '(2) one ground-truth array for all H')
if len(sys.argv) > 2:
    g = np.load(sys.argv[2])['gt'].astype(np.float64); g = g[g[:, 0] < len(ri)]
    chk(g.shape == Z['gt'].shape and np.allclose(g, Z['gt'], equal_nan=True, atol=0), '(2) labels identical to reference dump on the prefix')
w = Z['weights_sha']; chk(w[0] == w[1], f'(3) weights sha256 unchanged by the run {w[0][:16]}..')
good = True; cnt = 0; first_ok = True
for i, h in enumerate(HS):
    m = ev[:, i]
    good &= bool((Z['eff_n'][m, i] == hf[m, i]).all())
    first_ok &= bool((Z['eff_first'][m, i] == ri[m] - hf[m, i] + 1).all())
    full = m & (hf[:, i] == h); cnt += int(full.sum())
    print(f'    H={h:2d}: cells {int(m.sum())}, with H_forced==H {int(full.sum())}, effective windows min/max '
          f'{Z["eff_n"][m,i].min()}/{Z["eff_n"][m,i].max()}')
chk(good, '(4)(5) effective support count == H_forced in every cell (access log)')
chk(first_ok, '(4) first window read == ri-H_forced+1 in every cell: no earlier window reached the model')
chk(all((Z['eff_n'][ev[:, i] & (hf[:, i] == h), i] == h).all() for i, h in enumerate(HS)), '(5) effective support == nominal H whenever H_forced == H')
P = Z['probe']
chk(len(P) > 0 and (P[:, 2] == 1).all(), f'(5) oldest-window probe changed the output in {int(P[:,2].sum()) if len(P) else 0}/{len(P)} probed cells')
print('VERIFY', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
