"""Emit the LaTeX macros for E71 (Support-Conditioned AP at H = 1..80 on 3,000 frames) and E72 (reset-policy audit).

Sources:
  experiments/e71_h4080/results.json     mAP, intervals, gaps, Kendall tau, ordering reproduction, crossing
  experiments/e71_h4080/frames.json      frame selection summary
  experiments/e71_h4080/verify-*.log     access-log and oldest-window-probe counts
  experiments/e71_h4080/probe_explained.log   why the unchanged probe cells did not change (src/e71_probe_explain.py)
  experiments/e72_reset_audit/audit-*.json    relative output change after zeroing the state entering a 21-window chunk

Prefix lh = E71 (letters only; TeX control sequences cannot contain digits).  Model codes Rt/Rs/Rb = RVT-t/s/b, Ss/Sb = S5-S/S5-B.
Column codes: Pool, HOne, HFive, HTen, HTwentyone, HForty, HEighty.  Prefix ra = E72.

Usage:  python3 src/e71_macros.py            print the blocks
        python3 src/e71_macros.py --write    replace/insert the two blocks in numbers.tex
"""
import json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D71 = os.path.join(REPO, 'experiments/e71_h4080'); D72 = os.path.join(REPO, 'experiments/e72_reset_audit')
NUMTEX = os.path.join(REPO, 'submission_2027/paper/latex/numbers.tex')
B71 = ('% ---- E71 BEGIN (src/e71_macros.py; do not edit by hand) ----', '% ---- E71 END ----')
B72 = ('% ---- E72 BEGIN (src/e71_macros.py; do not edit by hand) ----', '% ---- E72 END ----')

MODELS = ['rvt-t', 'rvt-s', 'rvt-b', 's5vit-small', 's5vit-base']
MC = {'rvt-t': 'Rt', 'rvt-s': 'Rs', 'rvt-b': 'Rb', 's5vit-small': 'Ss', 's5vit-base': 'Sb'}
CC = {'pooled': 'Pool', 'H1': 'HOne', 'H5': 'HFive', 'H10': 'HTen', 'H21': 'HTwentyone', 'H40': 'HForty', 'H80': 'HEighty'}
HSHORT = ['H1', 'H5', 'H10', 'H21']


def thousands(n):
    return f'{n:,}'.replace(',', '\\,')


def signed(v, d=2):
    return f'\\ensuremath{{{v:+.{d}f}}}'


def tau(v):
    return f'\\ensuremath{{{v:.2f}}}' if v < 0 else f'{v:.2f}'


def read_verify():
    out = {}
    for m in MODELS:
        t = open(os.path.join(D71, f'verify-{m}.log')).read()
        mm = re.search(r'oldest-window probe changed the output in (\d+)/(\d+) probed cells', t)
        assert mm, m
        out[m] = (int(mm.group(1)), int(mm.group(2)))
        assert '[PASS] (4)(5) effective support count == H_forced in every cell' in t, m
        assert '[PASS] (4) first window read == ri-H_forced+1 in every cell' in t, m
        assert '[PASS] (3) weights sha256 unchanged' in t, m
        assert '[PASS] (5) effective support == nominal H whenever H_forced == H' in t, m
    # every unchanged probe cell is explained (empty oldest window or a frame without detections)
    pe = open(os.path.join(D71, 'probe_explained.log')).read()
    for m in MODELS:
        mm = re.search(rf'^{re.escape(m)}: probed (\d+), output changed (\d+), unchanged (\d+) = oldest window all-zero (\d+) \+ '
                       rf'frame without detections (\d+) \+ unexplained (\d+)$', pe, re.M)
        assert mm, m
        n, ch, un, ez, nd, ux = map(int, mm.groups())
        assert (n, ch) == (out[m][1], out[m][0]) and ux == 0 and ch + ez + nd == n, (m, mm.group(0))
    return out


def build71():
    R = json.load(open(os.path.join(D71, 'results.json')))
    F = json.load(open(os.path.join(D71, 'frames.json')))
    M = []

    def add(name, text, comment=''):
        M.append((name, text, comment))

    assert [c for c in R['cols'] if c != 'H21x'] == list(CC), R['cols']
    assert R['models'] == MODELS
    add('lhNFrames', thousands(R['n_frames']), 'frames scored at every H (stratified sample of the eligible frames)')
    add('lhNElig', thousands(F['eligible_frames']), 'labeled frames with at least 80 windows available (r+1 >= 80)')
    add('lhNEligSeq', str(F['n_sequences_eligible']), 'validation sequences containing an eligible frame')
    add('lhNSeqAll', str(F['n_sequences_total']), 'validation sequences in all')
    add('lhNSeq', str(R['n_seq']), 'sequences represented in the 3,000 frames')
    add('lhMaxPerSeq', str(F['max_per_seq']), 'most frames drawn from one sequence')
    add('lhB', str(R['B']), 'sequence-cluster bootstrap draws')
    for m in MODELS:
        for c in CC:
            v = R['map'][m][c]; lo, hi = R['ci'][m][c]
            add(f'lhMap{MC[m]}{CC[c]}', f'{v:.2f}')
            add(f'lhMap{MC[m]}{CC[c]}Lo', f'{lo:.2f}')
            add(f'lhMap{MC[m]}{CC[c]}Hi', f'{hi:.2f}')
    for c in CC:
        add(f'lhTau{CC[c]}', tau(R['kendall_vs_pooled'][c]), 'Kendall tau of this ordering against the pooled one')
        add(f'lhRepro{CC[c]}', f'{100 * R["rank_repro"][c]:.1f}', 'percent of draws reproducing the point ordering')
    for i, a in enumerate(MODELS):
        for b in MODELS[i + 1:]:
            k = f'{a}-{b}'
            for c in CC:
                g, lo, hi = R['gap'][k][c]
                add(f'lhGap{MC[a]}{MC[b]}{CC[c]}', signed(g))
                add(f'lhGap{MC[a]}{MC[b]}{CC[c]}Lo', signed(lo))
                add(f'lhGap{MC[a]}{MC[b]}{CC[c]}Hi', signed(hi))
            pts = [R['gap'][k][c][0] for c in HSHORT]
            add(f'lhGap{MC[a]}{MC[b]}Min', signed(min(pts)), 'smallest point gap over H = 1, 5, 10, 21')
            add(f'lhGap{MC[a]}{MC[b]}Max', signed(max(pts)), 'largest point gap over H = 1, 5, 10, 21')
    mp = R['map']
    rv = [m for m in MODELS if m.startswith('rvt')]
    add('lhGainRvtLo', f'{min(mp[m]["H21"] - mp[m]["H1"] for m in rv):.1f}', 'smallest RVT gain from H=1 to H=21 (points)')
    add('lhGainRvtHi', f'{max(mp[m]["H21"] - mp[m]["H1"] for m in rv):.1f}', 'largest RVT gain from H=1 to H=21')
    ss = ['s5vit-small', 's5vit-base']
    add('lhGainSsmLo', f'{min(mp[m]["H21"] - mp[m]["H1"] for m in ss):.1f}', 'smallest S5 gain from H=1 to H=21')
    add('lhGainSsmHi', f'{max(mp[m]["H21"] - mp[m]["H1"] for m in ss):.1f}', 'largest S5 gain from H=1 to H=21')
    add('lhLateRvtLo', f'{min(mp[m]["H80"] - mp[m]["H21"] for m in rv):.1f}', 'smallest RVT gain from H=21 to H=80')
    add('lhLateRvtHi', f'{max(mp[m]["H80"] - mp[m]["H21"] for m in rv):.1f}', 'largest RVT gain from H=21 to H=80')
    add('lhLateSsmS', f'{mp["s5vit-small"]["H21"] - mp["s5vit-small"]["H80"]:.1f}', 'S5-S loss from H=21 to H=80 (points)')
    add('lhLateSsmB', f'{mp["s5vit-base"]["H21"] - mp["s5vit-base"]["H80"]:.1f}', 'S5-B loss from H=21 to H=80 (points)')
    cr = R['crossing_rvt_b_over_s5_base']
    a, b, x = cr['first_sign_change']
    add('lhCrossLo', str(a), 'last H with RVT-b below S5-B')
    add('lhCrossHi', str(b), 'first H with RVT-b above S5-B')
    add('lhCrossH', f'{x:.0f}', 'linear interpolation of the two gaps to zero (rounded)')
    add('lhHTwentyoneDiff', f'{max(abs(v) for v in R["h21_recompute_diff"].values()):.3f}', 'largest |mAP(H=21 recomputed) - mAP(H=21 from the E66 dump)| over the five checkpoints, points')
    P = json.load(open(os.path.join(D71, 'population.json')))
    assert P['n_frames'] == F['eligible_frames'] and P['n_seq'] == F['n_sequences_eligible']
    k = 'rvt-b-s5vit-base'
    for c in ('H21',):
        g, lo, hi = P['gap'][k][c]
        add('lqGapRbSbHTwentyone', signed(g), 'population (all eligible frames): RVT-b minus S5-B at H=21')
        add('lqGapRbSbHTwentyoneLo', signed(lo))
        add('lqGapRbSbHTwentyoneHi', signed(hi))
    add('lqNSeq', str(P['n_seq']), 'sequences among the eligible frames')
    V = read_verify()
    add('lhProbeN', str(V['rvt-t'][1]), 'oldest-window probe cells per checkpoint')
    add('lhProbeHitLo', str(min(v[0] for v in V.values())), 'fewest cells whose output changed, over checkpoints')
    add('lhProbeHitHi', str(max(v[0] for v in V.values())), 'most cells whose output changed, over checkpoints')
    assert len({v[1] for v in V.values()}) == 1
    pe = open(os.path.join(D71, 'probe_explained.log')).read()
    ez = [int(x) for x in re.findall(r'oldest window all-zero (\d+) \+', pe)]
    nd = [int(x) for x in re.findall(r'frame without detections (\d+) \+', pe)]
    assert len(ez) == len(nd) == len(MODELS)
    add('lhProbeMissLo', str(V['rvt-t'][1] - max(v[0] for v in V.values())), 'fewest probe cells whose output did not change, over checkpoints')
    add('lhProbeMissHi', str(V['rvt-t'][1] - min(v[0] for v in V.values())), 'most probe cells whose output did not change, over checkpoints')
    add('lhProbeEmptyMin', str(min(ez)), 'unchanged cells whose oldest window holds no events: fewest over checkpoints')
    add('lhProbeEmptyMax', str(max(ez)), 'same: most')
    add('lhProbeNoDetMax', str(max(nd)), 'unchanged cells whose frame has no detection: most over checkpoints')
    DD = json.load(open(os.path.join(D71, 'h21_detdiff.json')))
    assert list(DD) == MODELS
    add('lhDetUnpairPct', f'{max(100 * v["n_unpaired"] / v["n_dets_e71"] for v in DD.values()):.2f}', 'percent of H=21 detections without a partner in the other run (largest over checkpoints)')
    add('lhDetUnpairScore', f'{max(v["max_unpaired_score"] for v in DD.values()):.2f}', 'largest confidence of an unpaired H=21 detection')
    add('lhDetP', f'{1e4 * max(v["p999_abs_score_diff"] for v in DD.values()):.1f}', 'x 1e-4: 99.9th percentile of the paired score difference (largest over checkpoints)')
    return M


def build72():
    A = {m: json.load(open(os.path.join(D72, f'audit-{m}.json'))) for m in ['rvt-t', 'rvt-s', 'rvt-b', 's5vit-small', 's5vit-base', 'evrtdetr-r18']}
    M = []

    def add(name, text, comment=''):
        M.append((name, text, comment))

    for m, d in A.items():
        assert d['chunk'] == 21 and d['n_chunk_starts'] == 9 and d['control_max_rel'] == 0.0, m
    add('raChunk', '21', 'windows per chunk in the reset audit')
    add('raStarts', '9', 'chunk starts per checkpoint (3 sequences x 3 chunk starts)')
    for m in ['rvt-t', 'rvt-s', 'rvt-b']:
        e = A[m]['effect_by_position']
        add(f'raEff{MC[m]}First', f'{e[0]:.3f}', 'relative L2 change of the output, first position of the chunk')
        add(f'raEff{MC[m]}Mid', f'{e[10]:.3f}', 'same, eleventh position')
        add(f'raEff{MC[m]}Last', f'{e[20]:.3f}', 'same, last position')
    for pos, nm in ((0, 'First'), (10, 'Mid'), (20, 'Last')):
        vs = [A[m]['effect_by_position'][pos] for m in ['rvt-t', 'rvt-s', 'rvt-b']]
        add(f'raEffRvt{nm}Lo', f'{min(vs):.3f}', 'smallest over the three RVT checkpoints')
        add(f'raEffRvt{nm}Hi', f'{max(vs):.3f}', 'largest over the three RVT checkpoints')
    for m in ['s5vit-small', 's5vit-base']:
        add(f'raEff{MC[m]}Max', f'{max(A[m]["effect_by_position"]):.3f}', 'largest relative change over the 21 positions')
    iv = [A[m]['inchunk_by_position'][p] for m in ['s5vit-small', 's5vit-base'] for p in (1, 10, 20)]
    add('raInSsmLo', f'{min(iv):.3f}', 'S5 change when the previous window is occluded, smallest over positions 1/10/20 and both checkpoints')
    add('raInSsmHi', f'{max(iv):.3f}', 'same, largest')
    ev = A['evrtdetr-r18']['effect_unmatched_dets']
    add('raEvFirst', f'{100 * ev[0]:.1f}', 'percent of confident EvRT-DETR detections without a partner after zeroing, first position')
    add('raEvMid', f'{100 * ev[10]:.1f}', 'same, eleventh position')
    add('raEvLast', f'{100 * ev[20]:.1f}', 'same, last position')
    iu = A['evrtdetr-r18']['inchunk_unmatched_dets']
    add('raEvInOne', f'{100 * iu[1]:.1f}', 'same when the previous window is occluded, position 1')
    return M


def block(M, marks, title):
    lines = [marks[0], title]
    for name, text, comment in M:
        lines.append(f'\\newcommand{{\\{name}}}{{{text}}}' + (f'  % {comment}' if comment else ''))
    lines.append(marks[1])
    return '\n'.join(lines) + '\n'


def splice(t, blk, marks):
    if marks[0] in t:
        a, b = t.index(marks[0]), t.index(marks[1]) + len(marks[1]) + 1
        return t[:a] + blk + t[b:]
    return t.rstrip('\n') + '\n\n' + blk


if __name__ == '__main__':
    b71 = block(build71(), B71, '% E71 Support-Conditioned AP at H = 1..80 on 3,000 frames. Emitted from experiments/e71_h4080/. mAP in points (x100).')
    b72 = block(build72(), B72, '% E72 reset-policy audit. Emitted from experiments/e72_reset_audit/audit-*.json.')
    if '--write' in sys.argv:
        t = open(NUMTEX).read()
        t = splice(splice(t, b71, B71), b72, B72)
        open(NUMTEX, 'w').write(t)
        print(f'wrote {b71.count(chr(10)) - 3} E71 and {b72.count(chr(10)) - 3} E72 macros into {NUMTEX}')
    else:
        print(b71 + b72)
