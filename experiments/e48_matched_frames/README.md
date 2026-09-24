# E48 — the RVT bin arm on E47's frames, so the architectures are comparable

## Why this exists

The bin-influence numbers on record were not measured on the same frames. E44 ran `rvt-s` and
`rvt-b` with KLAG = 19, so its samples begin at frame 19; E45 and E47's bin arm begin at frame
8. A 0.03 ms difference between E45's `rvt-t` and E44's `rvt-t` is already attributable to that
alone. Comparing a ConvLSTM against an S5 layer requires the frames to be identical, so this
re-runs RVT's three capacities through the bin arm only, on E47's frames.

Zero fill only, with the recurrent state entering the step — E45's zero arm.

## Result (n = 480 frames, identical across all three)

| checkpoint | params | bin centroid | bootstrap SE | CV | max/min | older half | newer half |
|---|---:|---:|---:|---:|---:|---:|---:|
| `rvt-t` | 4.41 M | **−23.810 ms** | 0.054 | 0.1313 | 1.520 | 48.55 % | 51.45 % |
| `rvt-s` | 9.87 M | **−23.981 ms** | 0.043 | 0.1144 | 1.466 | 48.76 % | 51.24 % |
| `rvt-b` | 18.54 M | **−24.133 ms** | 0.044 | 0.1002 | 1.405 | 49.18 % | 50.82 % |

Three readings, all on the same frames:

1. **The centroid is stable across a 4.2× range of capacity.** −23.81 to −24.13 ms, a spread of
   0.32 ms on bootstrap SEs of 0.04–0.05 ms. It is resolvably capacity-dependent and the
   dependence is tiny; the profile does not become more or less front-loaded as the network
   grows.
2. **The profile is not flat, and flattens with capacity.** CV falls 0.131 → 0.100 and max/min
   falls 1.52 → 1.40 monotonically in parameter count. A bigger network spreads its dependence
   more evenly over the 50 ms window.
3. **The two halves of the window are near-balanced**, 48.6/51.4 to 49.2/50.8, newer half
   always slightly ahead — which is why all three centroids land just *after* the −25 ms that
   uniform weighting would give, and why the deviation from uniform is a fraction of a
   millisecond rather than the several milliseconds a strongly recency-weighted network would
   show.

Taken with E47's SSM arm on the identical 480 frames, this is the comparison the paper makes
between a ConvLSTM and an S5 layer: the difference between the families is not in where the
input centroid sits, which is within ~0.3 ms across every RVT capacity.

## Files

- `e48_rvt_bins.py` → `rvt-t.json`, `rvt-s.json`, `rvt-b.json`
