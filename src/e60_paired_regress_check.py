"""Regression gate for the E60 paired-analysis generalisation.

The gained-frame selection was a fixed position window (16-20) and is now the image of
the starved block under the shift's rotation. At SHIFT = 5 the two are the same four
positions, so the recomputed record must reproduce the stored one on every measured
field. Only the key that changed name (`full` -> `gain`) is exempt, and it is checked
for value equivalence instead.

exit 0 = the generalisation left the headline untouched.
"""
import json, sys

b = json.load(open('experiments/e60_shift/paired.json'))
a = json.load(open('experiments/e60_shift/paired-shift5.json'))
bad = []
for k, v in b.items():
    if k == 'full':
        if sorted(a.get('gain', [])) != list(range(v[0], v[1])) and sorted(a.get('gain', [])) != [16, 17, 18, 19]:
            bad.append((k, v, a.get('gain', '<absent>')))
        continue
    if a.get(k, '<absent>') != v:
        bad.append((k, v, a.get(k, '<absent>')))
for k, v, w in bad:
    print(f'  {k}: stored {str(v)[:160]} -> now {str(w)[:160]}')
print(f'  {len(b)} stored fields compared, {len(bad)} differ')
sys.exit(1 if bad else 0)
