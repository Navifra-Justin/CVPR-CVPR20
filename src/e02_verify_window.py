"""E02 - verify, in the released RVT source, that the event window ends at the label time.

The claim rests on two released artifacts and nothing else: the Gen1 dataset config,
which fixes the window duration and the bin count, and the preprocessing script, which
builds the representation timestamps by counting backwards from label timestamps. This
script reads both and writes the values it found, so that the numbers quoted in the paper
have a machine-written source rather than a note.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, 'src', 'RVT', 'config', 'dataset', 'gen1.yaml')
PRE = os.path.join(ROOT, 'src', 'RVT', 'scripts', 'genx', 'preprocess_dataset.py')
OUT = os.path.join(ROOT, 'experiments', 'e02_rvt_window_alignment')

cfg = {}
for line in open(CFG):
    m = re.match(r"\s*(ev_repr_name|sequence_length|resolution_hw)\s*:\s*(.+)", line)
    if m:
        cfg[m.group(1)] = m.group(2).strip().strip("'\"")

name = cfg['ev_repr_name']
dt_ms = int(re.search(r'dt=(\d+)', name).group(1))
nbins = int(re.search(r'nbins=(\d+)', name).group(1))

hits = [(i + 1, l.rstrip()) for i, l in enumerate(open(PRE))
        if 'ev_repr_timestamps_us_end' in l and '=' in l and 'extend' not in l]
line_no, line_src = hits[0]
backwards = '-delta_t_us' in line_src and 'reversed' in line_src

res = dict(config_file=os.path.relpath(CFG, ROOT),
           ev_repr_name=name,
           window_ms=dt_ms,
           n_bins=nbins,
           bin_width_ms=dt_ms / nbins,
           uniform_weight_centroid_ms=-dt_ms / 2.0,
           preprocess_file=os.path.relpath(PRE, ROOT),
           construction_line=line_no,
           construction_source=line_src.strip(),
           counts_backwards_from_label=bool(backwards))
os.makedirs(OUT, exist_ok=True)
json.dump(res, open(os.path.join(OUT, 'result.json'), 'w'), indent=1)
for k, v in res.items():
    print(f'{k:32s} {v}')
