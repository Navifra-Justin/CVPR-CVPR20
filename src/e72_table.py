"""E72: assemble the reset-policy audit table from experiments/e72_reset_audit/audit-*.json (written by src/e72_audit.py)."""
import json, glob, numpy as np
R = 'experiments/e72_reset_audit'
A = {json.load(open(f))['model']: json.load(open(f)) for f in sorted(glob.glob(f'{R}/audit-*.json')) if 'rawquery' not in f}
Z = np.load('experiments/e66_fixedH/dets-rvt-s.npz'); ri = Z['ri'][Z['done']] + 1
def rng(d, key='effect_by_position'):
    e = d[key]; return f"{e[0]:.4f} / {e[10]:.4f} / {e[20]:.4f}"
L = ['# E72 reset-policy audit (relative L2 change of the output when the state entering a 21-window chunk is zeroed)', '',
     'Per model: mean over chunk starts (sequences x chunks listed), positions p = 0 / 10 / 20 inside the chunk. Control = same chunk re-run with the identical entering state (max relative difference over all positions and chunks; must be 0).', '',
     '| model | repository (commit) | chunk starts | rel. change p=0 / 10 / 20 | control | occluding the previous window (p=1 / 10 / 20) | measured policy |', '|---|---|--:|---|--:|---|---|']
repo = {'rvt': 'uzh-rpg/RVT (vendored src/RVT)', 's5vit': 'uzh-rpg/ssms_event_cameras (vendored src/SSMViT)', 'evrtdetr': 'realtime-intelligence/evrt-detr 5a2ffff'}
for m, d in A.items():
    k = 'rvt' if m.startswith('rvt') else 's5vit' if m.startswith('s5') else 'evrtdetr'
    e = d['effect_by_position']; iv = d['inchunk_by_position']
    pol = ('state entering a chunk never reaches the output (reset at every chunk / inert state)' if max(e) < 1e-6 else
           'state entering a chunk reaches the output at every position; effect decays with position (carried across the chunk boundary)')
    inn = ' / '.join('%.4f' % iv[p] for p in (1, 10, 20))
    L.append(f"| {m} | {repo[k]} | {d['n_chunk_starts']} | {rng(d)} | {d['control_max_rel']:.1e} | {inn} | {pol} |")
if 'evrtdetr-r18' in A:
    d = A['evrtdetr-r18']
    L += ['', 'EvRT-DETR decoder queries are top-k selected from encoder tokens, so output index i is not the same object in two runs and the raw tensor change above is not a clean magnitude. Order-invariant views (p = 0 / 10 / 20):',
          f"- sorted top-100 confidence vector, relative L2 change: {rng(d, 'effect_sorted_scores')}; occluding previous window (p=1/10/20): " + ' / '.join('%.4f' % d['inchunk_sorted_scores'][p] for p in (1, 10, 20)),
          f"- share of confident detections (score >= 0.25) without a same-class IoU >= 0.5 partner after zeroing: {rng(d, 'effect_unmatched_dets')}; occluding previous window: " + ' / '.join('%.4f' % d['inchunk_unmatched_dets'][p] for p in (1, 10, 20))]
L += ['', f'History range inside the pooled Gen1 validation score (labelled frames, windows seen since the sequence start; from experiments/e66_fixedH/dets-rvt-s.npz ri+1): min {ri.min()}, median {int(np.median(ri))}, max {ri.max()}; share with <= 21 windows {np.mean(ri <= 21):.3f}.',
      'For RVT and EvRT-DETR the pooled score therefore mixes histories from 2 to 1200 windows (state carried from the sequence start); for SSM-ViT the evaluation chunk is 21 windows, so the position inside the chunk (1..21 windows) is the history, because the state entering a chunk is inert (rel. change 0 at every position).']
open(f'{R}/audit_table.md', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
