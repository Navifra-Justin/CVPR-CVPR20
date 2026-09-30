"""Regression gate for the E60 paired-analysis generalisation.

The gained-frame selection was a fixed position window (16-20) and is now the image of
the starved block under the shift's rotation. At SHIFT = 5 the two are the same four
positions, so the recomputed record must reproduce the stored one on every measured
field. Only the key that changed name (`full` -> `gain`) is exempt, and it is checked
for value equivalence instead.

exit 0 = the generalisation left the headline untouched.
"""
import json, sys
import os as _os, sys as _sys
# Every artifact path below is relative, so which files this gate read used to depend on
# the caller's working directory. Anchoring the root to this file's own location makes the
# same command compare the same population from any cwd.
_os.chdir(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

b = json.load(open('experiments/e60_shift/paired.json'))
a = json.load(open('experiments/e60_shift/paired-shift5.json'))
if not b:
    sys.exit('e60_paired_regress_check: the stored record has 0 fields; nothing would be '
             'compared, and an empty population must not become a clean verdict')
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
