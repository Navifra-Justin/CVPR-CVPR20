#!/bin/bash
# E65 - exercise src/e65_paired.py end to end on synthetic dumps.
#
# The analysis is the last step of an eight-hour dumping run, so an assertion or a bootstrap
# bug found after the arms land costs the whole run. This builds dumps that have the real
# shape - the recorded release placement, its rotation by SHIFT, a plausible detection and
# ground-truth table - runs the real analysis on them, and then checks two things:
#
#   1. the analysis completes and writes the json the macro emitter reads, with one row per
#      arm and a finite bootstrap standard error;
#   2. the placement guard fires when the shifted dump does not rotate by SHIFT, which is
#      the failure mode a silently mis-driven arm would present as.
#
# It measures nothing about RVT. A pass means the analysis code runs, not that any number
# in the paper is right; src/audit_numbers.py is what ties the numbers to their artifacts.
set -euo pipefail
cd "$(dirname "$0")/.."
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT

python3 - "$T" <<'PY'
import sys, numpy as np
T = sys.argv[1]
CHUNK, SHIFT = 21, 5
pa = np.load('experiments/e58_chunkpos/positions.npy')
gt = np.load('experiments/e51_ranking/dets-rvt-s.npz')['gt']
rng = np.random.default_rng(0)
pb = np.where(pa >= 0, (pa - SHIFT) % CHUNK, pa)
for tag in ('s', 'b'):
    for reg, lift in (('carry', 0.0), ('reset', 0.30)):
        for tail, pos in (('shift0', pa), (f'shift{SHIFT}', pb)):
            # one detection on each ground-truth box, its score raised in the arm that is
            # supposed to gain, so the analysis sees a non-degenerate paired difference.
            # Column order is the dumps' own: frame, box, score, class. Putting the class
            # in the score column instead is not a harmless fixture slip - it leaves every
            # detection unmatched, so the matched-confidence channel is all NaN and the
            # bootstrap sees an empty vector rather than a wrong number.
            det = np.zeros((len(gt), 7), dtype=np.float32)
            det[:, 0] = gt[:, 0]
            det[:, 1:5] = gt[:, 1:5]
            base = rng.uniform(0.2, 0.9, len(gt)).astype(np.float32)
            det[:, 5] = np.clip(base + (lift if tail != 'shift0' else 0.0), 0, 1)
            det[:, 6] = gt[:, 5]
            np.savez_compressed(f'{T}/dets-rvt-{tag}-{reg}-{tail}.npz',
                                det=det, gt=gt, pos=pos.astype(np.int16))
np.savez_compressed(f'{T}/bad.npz', det=np.zeros((1, 7), np.float32), gt=gt,
                    pos=np.roll(pb, 1).astype(np.int16))
print('synthetic dumps written')
PY

echo "--- case 1: the analysis runs end to end"
E65DIR="$T" OUT="$T/paired-shift5.json" SHIFT=5 B=${B:-24} RPERM=${RPERM:-12} python3 -u src/e65_paired.py > "$T/run.log" 2>&1 \
  || { echo "FAIL: analysis did not complete"; tail -40 "$T/run.log"; exit 1; }
python3 - "$T" <<'PY'
import json, sys, math
r = json.load(open(f'{sys.argv[1]}/paired-shift5.json'))
arms = r['arms']
assert set(arms) == {'s-carry', 's-reset', 'b-carry', 'b-reset'}, sorted(arms)
for k, a in arms.items():
    for f in ('map_vel_boot', 'map_all_boot', 'perm_null'):
        assert f in a, f'{k}: no {f}'
    assert math.isfinite(a['map_vel_boot']['se']), f'{k}: non-finite bootstrap se'
    assert a['n'] > 0, f'{k}: no paired frames'
print(f"  [pass] four arms, finite bootstrap, n={arms['s-carry']['n']}")
PY

echo "--- case 2: a shifted dump that does not rotate by SHIFT is rejected"
cp "$T/bad.npz" "$T/dets-rvt-s-carry-shift5.npz"
if E65DIR="$T" OUT="$T/bad.json" SHIFT=5 TAGS=s B=${B:-24} RPERM=${RPERM:-12} python3 -u src/e65_paired.py > "$T/bad.log" 2>&1; then
  echo "FAIL: the placement guard did not fire on a non-rotating dump"; exit 1
fi
grep -q "do not rotate by 5" "$T/bad.log" \
  || { echo "FAIL: analysis failed for the wrong reason"; tail -5 "$T/bad.log"; exit 1; }
echo "  [pass] the guard fires and names the rotation"

echo "e65_paired_selftest: 2 of 2 cases behaved as intended"
