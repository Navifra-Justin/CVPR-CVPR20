"""E71 step 0: reproduce known E66 numbers (results.json) with the Cell/Scorer path used by e71_eval, full common set."""
import numpy as np, json, sys
sys.path.insert(0, 'src')
from e66_eval import Cell
from e56_eval import Scorer
R = json.load(open('experiments/e66_fixedH/results.json'))
for m in sys.argv[1:]:
    Z = np.load(f'experiments/e66_fixedH/dets-{m}.npz'); gt = Z['gt'].astype(np.float64)
    hf = Z['hforced']; common = np.flatnonzero((hf == Z['hnominal'][None]).all(1) & Z['done'])
    w = np.zeros(len(Z['seq'])); w[common] = 1
    for c, det in [('H21', Z['det_h21']), ('H1', Z['det_h1'])]:
        v = Cell(Scorer(det.astype(np.float64), gt)).ap(w); print(m, c, round(v, 4), 'published', round(R['map'][m][c], 4), flush=True)
