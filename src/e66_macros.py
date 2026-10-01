"""Emit the LaTeX macros for E66 (Support-Conditioned AP) and write them into numbers.tex.

Sources, all under experiments/e66_fixedH/:
  results.json   every mAP, interval, gap, Kendall tau and ordering-reproduction rate
  verify-*.log   the access-log and oldest-window-probe counts of src/e66_verify.py
  eval.log       the largest difference between the fast evaluator and the E56 Scorer

Nothing is typed by hand: src/audit_numbers.py re-derives each macro from the same files, so a
macro edited without a run fails the audit. Names carry letters only (TeX control sequences
cannot contain digits). Model codes: Rt/Rs/Rb = RVT-t/s/b, Ss/Sb = S5-ViT small/base. Column
codes: Pool, HOne, HFive, HTen, HTwentyone.

Usage:  python3 src/e66_macros.py            print the block
        python3 src/e66_macros.py --write    replace the E66 block in numbers.tex
"""
import json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'experiments/e66_fixedH')
NUMTEX = os.path.join(REPO, 'submission_2027/paper/latex/numbers.tex')
BEGIN, END = '% ---- E66 BEGIN (src/e66_macros.py; do not edit by hand) ----', '% ---- E66 END ----'

MODELS = ['rvt-t', 'rvt-s', 'rvt-b', 's5vit-small', 's5vit-base']
MC = {'rvt-t': 'Rt', 'rvt-s': 'Rs', 'rvt-b': 'Rb', 's5vit-small': 'Ss', 's5vit-base': 'Sb'}
CC = {'pooled': 'Pool', 'H1': 'HOne', 'H5': 'HFive', 'H10': 'HTen', 'H21': 'HTwentyone'}
HCOLS = ['H1', 'H5', 'H10', 'H21']


def thousands(n):
    s = f'{n:,}'.replace(',', '\\,')
    return s


def signed(v, d=2):
    """Explicit-sign number for gaps; the minus sign is set in math mode."""
    return f'\\ensuremath{{{v:+.{d}f}}}'


def read_verify():
    out = {}
    for m in MODELS:
        t = open(os.path.join(D, f'verify-{m}.log')).read()
        mm = re.search(r'oldest-window probe changed the output in (\d+)/(\d+) probed cells', t)
        assert mm, f'no probe line in verify-{m}.log'
        out[m] = (int(mm.group(1)), int(mm.group(2)))
        assert '[PASS] (4)(5) effective support count == H_forced in every cell' in t, m
        assert '[PASS] (4) first window read == ri-H_forced+1 in every cell' in t, m
    return out


def read_fastdiff():
    t = open(os.path.join(D, 'eval.log')).read()
    return max(float(x) for x in re.findall(r'max \|fast - Scorer\| so far ([0-9.e+-]+)', t))


def build():
    R = json.load(open(os.path.join(D, 'results.json')))
    M = []  # (name, text, comment)

    def add(name, text, comment=''):
        M.append((name, text, comment))

    add('fhNAll', thousands(R['n_frames']), 'frames in the released-protocol evaluation')
    add('fhNCommon', thousands(R['n_common']), 'frames with H_forced == H_nominal at every H (common frames)')
    add('fhNExcl', str(R['n_excluded']), 'frames excluded: fewer than 21 windows of history')
    add('fhNSeq', str(R['n_seq_common']), 'validation sequences in the common set')
    add('fhB', str(R['B']), 'sequence-cluster bootstrap draws')
    for m in MODELS:
        for c in R['cols']:
            v = R['map'][m][c]; lo, hi = R['ci'][m][c][0], R['ci'][m][c][1]
            add(f'fhMap{MC[m]}{CC[c]}', f'{v:.2f}')
            add(f'fhMap{MC[m]}{CC[c]}Lo', f'{lo:.2f}')
            add(f'fhMap{MC[m]}{CC[c]}Hi', f'{hi:.2f}')
        add(f'fhMap{MC[m]}All', f'{R["pooled_all_frames"][m]:.2f}', 'released pooled score, all frames')
    for c in R['cols']:
        add(f'fhTau{CC[c]}', f'{R["kendall_vs_pooled"][c]:.2f}', 'Kendall tau of this ordering against the pooled one')
        add(f'fhRepro{CC[c]}', f'{100 * R["rank_repro"][c]:.1f}', 'percent of draws reproducing the point ordering')
    for a in MODELS:
        for b in MODELS:
            k = f'{a}-{b}'
            if k not in R['gap']:
                continue
            for c in R['cols']:
                g, lo, hi = R['gap'][k][c]
                add(f'fhGap{MC[a]}{MC[b]}{CC[c]}', signed(g))
                add(f'fhGap{MC[a]}{MC[b]}{CC[c]}Lo', signed(lo))
                add(f'fhGap{MC[a]}{MC[b]}{CC[c]}Hi', signed(hi))
            pts = [R['gap'][k][c][0] for c in HCOLS]
            add(f'fhGap{MC[a]}{MC[b]}Min', signed(min(pts)), 'smallest point gap over H = 1, 5, 10, 21')
            add(f'fhGap{MC[a]}{MC[b]}Max', signed(max(pts)), 'largest point gap over H = 1, 5, 10, 21')
    V = read_verify()
    add('fhProbeN', str(V['rvt-t'][1]), 'oldest-window probe cells per checkpoint')
    add('fhProbeHit', str(V['rvt-s'][0]), 'cells whose output changed (four checkpoints)')
    add('fhProbeHitT', str(V['rvt-t'][0]), 'cells whose output changed (RVT-t)')
    assert len({V[m][1] for m in MODELS}) == 1
    assert len({V[m][0] for m in MODELS if m != 'rvt-t'}) == 1
    add('fhFastDiff', f'{read_fastdiff() * 1e6:.2f}', 'x 1e-6 mAP points: fast path vs E56 Scorer, largest difference')
    return M


def block(M):
    lines = [BEGIN,
             '% E66 Support-Conditioned AP. Emitted by src/e66_macros.py from',
             '% experiments/e66_fixedH/{results.json,verify-*.log,eval.log}. mAP in points (x100).']
    for name, text, comment in M:
        lines.append(f'\\newcommand{{\\{name}}}{{{text}}}' + (f'  % {comment}' if comment else ''))
    lines.append(END)
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    blk = block(build())
    if '--write' in sys.argv:
        t = open(NUMTEX).read()
        if BEGIN in t:
            a, b = t.index(BEGIN), t.index(END) + len(END) + 1
            t = t[:a] + blk + t[b:]
        else:
            t = t.rstrip('\n') + '\n\n' + blk
        open(NUMTEX, 'w').write(t)
        print(f'wrote {blk.count(chr(10)) - 4} E66 macros into {NUMTEX}')
    else:
        print(blk)
