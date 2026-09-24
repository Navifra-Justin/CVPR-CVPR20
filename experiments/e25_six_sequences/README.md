# E25 — do the two surviving night results hold across all six ceiling sequences?

## Why this exists

Both audits named the same largest limitation: **one sequence**. All six DSEC train sequences
whose exposure is pinned at 14996 µs now have events, exposure metadata and DSEC-Det labels on
disk, so the two night results can be reproduced per sequence instead of argued from one.

Reproduced per sequence:

- **(A) E10 — the mains signature.** Per-box modulation `m = 2|C|` at 100 Hz, with the Rayleigh
  statistic against its analytic Exp(1) null, and an off-frequency control at 137 Hz.
- **(B) E20 — the spatial gradient of evidence time.** Fit `t = a + bx + cy` inside each box and
  align ∇t with the label-derived velocity. Flicker is spatially uniform inside a box and
  cannot contribute to a gradient, so the two instruments are independent. Two nulls: shuffled
  velocity, and event times shuffled within the box.

## Result

| sequence | boxes | m (median) | Z(100 Hz) | Z(137 Hz) | lock | n grad | cos | null (rot) | null (time) | σ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `zurich_city_00_a` | 2914 | 0.428 | 117.60 | 3.15 | 0.997 | 2734 | **+0.2406** | −0.0053 | +0.0022 | 12.6 |
| `zurich_city_01_a` | 2134 | 0.440 | 99.11 | 4.69 | 0.990 | 2061 | **+0.1791** | +0.0033 | −0.0000 | 8.1 |
| `zurich_city_02_a` | 619 | 0.445 | 68.40 | 2.75 | 0.994 | 600 | +0.0002 | −0.0033 | −0.0081 | 0.0 |
| `zurich_city_03_a` | 241 | 0.489 | 310.86 | 25.84 | 1.000 | 232 | −0.1068 | −0.0555 | +0.0205 | 1.6 |
| `zurich_city_09_a` | 6997 | 0.466 | 251.52 | 7.82 | 0.998 | 6627 | **+0.1518** | +0.0022 | −0.0058 | 12.4 |
| `zurich_city_10_a` | 3611 | 0.438 | 111.56 | 3.33 | 0.997 | 3450 | **+0.1191** | −0.0109 | −0.0075 | 7.0 |

**(A) replicates in all six.** Median Rayleigh Z at 100 Hz is 114.58 against a null mean of
0.693, and the 137 Hz control sits at 4.01. Per-box modulation is 0.43–0.49 everywhere, and
99–100 % of boxes lock.

**(B) replicates in four of six, with one sequence against.** Pooled weighted mean cos = +0.1540,
5 of 6 sequences positive, both nulls flat. `zurich_city_02_a` is exactly null (0.0002, 0.0 σ)
and `zurich_city_03_a` is negative at 1.6 σ on only 232 boxes. Both nulls being flat while the
observed statistic varies across sequences says the variation is scene content, not method.

The instrument (A) is strong enough to be a per-sequence fact. Instrument (B) is a pooled fact
with visible heterogeneity, and the paper reports it that way. The heterogeneity also generated
its own follow-up: alignment is *stronger* where objects move slower (r = −0.91 against the
fraction of boxes above 20 px/s), which is backwards for a per-object motion signal, and that
is what `experiments/e26_egomotion/` exists to settle.

## Files

- `e25_six_sequences.py` → `result.json`, `run.log`
