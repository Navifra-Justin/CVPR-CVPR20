# E45 — the influence profile with the correct recurrent state (2026-09-07)

## Why this exists

E17 measured the newest window's influence profile by occluding each bin and reading the
relative L2 change in the emitted detection tensor; E34 repeated it under four instruments.
Both advanced the recurrence and then handed the occluded pass the state the reference pass
had **returned**:

```python
out,_,states = mdl.forward(x, previous_states=states)   # states is now post-step
...
o2,_,_       = mdl.forward(xm, previous_states=states)  # one step out of phase
```

The occluded pass must start from the state **entering** the step it is differenced against.
E42 and E44 do that; E17 and E34 did not, which is why E44's `rvt-t` centroid (−23.84 ms)
disagreed with E17's (−24.94 ms) by more than either run's sampling error. This experiment
repeats E34's four instruments with `previous_states=pre[i]` and supersedes both.

## What changed in the code

```python
st=None; pre=[]
for i in range(n):
    pre.append(clone_states(st))                        # the state entering step i
    with torch.no_grad(): o,_,st = mdl.forward(X[i], previous_states=st)
...
o2,_,_ = mdl.forward(xm, previous_states=pre[i])        # the same history, one bin occluded
```

Nothing else differs from E34: same checkpoint, same 12 Gen1 validation sequences, same
warm-up, same 480 samples, same four fills.

## Result

| instrument | centroid (ms) | CV over bins | bootstrap SE (ms) |
|---|---|---|---|
| zero fill | **−23.810** | 0.1313 | 0.054 |
| dataset-mean fill | −26.354 | 0.1523 | 0.026 |
| swap from an unrelated sample | −25.007 | 0.0752 | 0.118 |
| gradient, no occlusion at all | −22.346 | 0.1907 | 0.006 |

Spread across instruments 4.008 ms; uniform-weight reference −25.00 ms. The zero-fill
centroid agrees with E44's independently written `rvt-t` measurement (−23.84 ms) to within
0.03 ms, which is the check that the state, and only the state, was the difference.

## What the profile actually looks like

E17 reported CV 0.034 and the manuscript called the profile "close to flat". That does not
survive. The corrected profile has CV 0.131 and its heaviest bin carries 1.52x its lightest.
The centroid is nevertheless within a quarter of a bin of the uniform value, because the
imbalance is between neighbouring bins and cancels in the first moment: the five older bins
hold 48.6 % of the influence against 51.4 % for the five newer.

The manuscript now states the balance rather than flatness. It is a weaker premise, and it
supports the same conclusion: the centroid of the input is the uniform-weight centroid of
the window to within a fraction of one bin.

## What this moved in the paper

Recomputed in `src/e46_recompute.py` (arithmetic) and `src/e46b_map_at_centroid.py` (a
direct evaluation at the new centroid rather than an interpolation between grid points):

| | E17 | E45 |
|---|---|---|
| centroid | −24.94 ms | −23.81 ms |
| difference from uniform | +0.06 ms | +1.19 ms |
| interval to the fitted output time | 27.3 ms | 26.2 ms |
| that interval, in SE of the fit | 3.81 | 3.65 |
| ratio to the 183.6 µs label dispersion | 136 | 130 |
| displacement at the 99th percentile speed | 1.35 px | 1.29 px |
| mAP cost of displacing gt to the centroid | 0.06 pt | 0.04 pt |

No claim reverses. The bootstrap of the output-time fit still puts 3 of 4000 draws at or
beyond the centroid, and no resample of the mAP argmax reaches it.

## Files

- `result.json`, `run.log` — the four instruments, per-bin means, per-bin SEM, centroids
- `profiles.npz` — the raw per-sample profiles, so a later statistic needs no GPU pass
- `derived.json`, `derived.log` — every manuscript number that depends on the centroid
- `../e37_map/at_centroid.json` — mAP evaluated at the new centroid, not interpolated

Recorded as case 9 in `docs/PROTOCOL_LEDGER.md`.
