"""Regression gate for the E47b family switch.

The refactored driver writes two metadata keys the pre-refactor profile does not
carry (`fam`, `arch`), so a byte comparison of the two JSON files reports a
difference that is not a difference in the measurement. This compares every key
the stored profile has, and additionally requires the new file to declare the
family it was produced under, so a profile written by the wrong arm cannot pass.

exit 0 = the refactor reproduces the stored measurement.
"""
import json, sys

BEFORE = 'experiments/e47_ssm/regress/s5vit-small-chunked.before.json'
AFTER = 'experiments/e47_ssm/s5vit-small-chunked.json'

b = json.load(open(BEFORE))
a = json.load(open(AFTER))
bad = [(k, v, a.get(k, '<absent>')) for k, v in b.items() if a.get(k, '<absent>') != v]
if a.get('fam') != 'ssm':
    bad.append(('fam', 'ssm', a.get('fam', '<absent>')))
for k, v, w in bad:
    print(f'  {k}: stored {v!r} -> now {w!r}')
print(f'  {len(b)} stored fields compared, {len(bad)} differ')
sys.exit(1 if bad else 0)
