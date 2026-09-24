"""E58c - the same periodicity, read off an instrument that never touches the metric.

E58b's difference-in-differences runs through the evaluator, the ground truth and the IoU
matcher. If the chunk-position effect is real it must also be visible in the raw detection
tensors alone, with no labels involved at all: a detector that at position 0 has seen one
50 ms window instead of twenty-one should be less confident and should fire less often.

So this counts detections and averages confidences per frame, groups by chunk position, and
asks for the same contrast. Nothing here loads a label.
"""
import numpy as np, json
from e56_eval import model_paths

P = np.load('experiments/e58_chunkpos/positions.npy')
TH = 0.1
NF = len(P)

print(f"detections per frame and mean confidence, by chunk position (score > {TH})\n")
print(f"{'model':<14}{'pos0-3 n/f':>12}{'pos16-20':>10}{'ratio':>8}"
      f"{'pos0-3 conf':>13}{'pos16-20':>10}{'ratio':>8}")
out = {}
for nm, q in model_paths():
    d = np.load(q)['det']
    d = d[d[:, 5] > TH]
    fi = d[:, 0].astype(int)
    pos = P[fi]
    row = []
    for lo, hi in [(0, 4), (16, 21)]:
        m = (pos >= lo) & (pos < hi)
        nfr = int(((P >= lo) & (P < hi)).sum())
        row.append((m.sum() / nfr, d[m, 5].mean()))
    print(f"{nm:<14}{row[0][0]:12.3f}{row[1][0]:10.3f}{row[0][0]/row[1][0]:8.3f}"
          f"{row[0][1]:13.4f}{row[1][1]:10.4f}{row[0][1]/row[1][1]:8.3f}")
    out[nm] = {"short_per_frame": float(row[0][0]), "full_per_frame": float(row[1][0]),
               "short_conf": float(row[0][1]), "full_conf": float(row[1][1])}

print(f"\nper-position mean confidence (score > {TH})")
print(f"{'windows':>8}" + "".join(f"{n:>13}" for n, _ in model_paths()))
curves = {}
for nm, q in model_paths():
    d = np.load(q)['det']; d = d[d[:, 5] > TH]
    pos = P[d[:, 0].astype(int)]
    curves[nm] = [float(d[pos == p, 5].mean()) for p in range(21)]
for p in range(21):
    print(f"{p+1:>8}" + "".join(f"{curves[n][p]:13.4f}" for n, _ in model_paths()))
out['conf_by_position'] = curves
json.dump(out, open('experiments/e58_chunkpos/invariant.json', 'w'), indent=1)
print("\nWROTE experiments/e58_chunkpos/invariant.json")
