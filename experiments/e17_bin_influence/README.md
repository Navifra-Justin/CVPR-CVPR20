# E17 — the network's temporal influence profile, measured rather than assumed

## Why this exists

E02 established from the released source that RVT's dt = 50 ms window **ends** at the label
time, so under uniform bin weighting the information centroid sits 25 ms before the label.
Whether the trained network actually weights its ten 5 ms bins uniformly was never measured,
so −25 ms was recorded as a reference point and explicitly not as a prediction. This measures
it.

## Method

For each sample the ten bins are occluded one at a time and the change in the detector's
output is recorded. The resulting profile w(k) is the network's influence per bin, and its
centroid is the effective input time of the prediction in the network's own weighting. Run on
real Gen1 val data with the released `rvt-t` checkpoint, sequentially through each sequence
so the recurrent state is the one the model would actually have had.

## Result (n = 480 samples)

| bin centre (ms) | −47.5 | −42.5 | −37.5 | −32.5 | −27.5 | −22.5 | −17.5 | −12.5 | −7.5 | −2.5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| influence | .01218 | .01256 | .01298 | .01320 | .01317 | .01199 | .01208 | .01274 | .01274 | .01299 |
| SEM | .00019 | .00020 | .00021 | .00021 | .00021 | .00017 | .00017 | .00020 | .00019 | .00020 |

**Centroid −24.94 ms**, against −25.00 ms for a uniform window: a difference of **0.056 ms**.
The profile is not flat bin by bin — it has a shallow maximum around −32 ms and a second rise
at the newest bins — but the two humps sit either side of the midpoint and the centroid lands
essentially where uniform weighting puts it.

This is the number the paper uses when it says the *input* centroid is measured, and it is
also the reason E21 exists: a centroid of the occlusion profile is an input-side quantity, and
a reviewer's objection that it does not identify the **output** time is correct. See
`experiments/e21_effective_output_time/README.md`.

## Files

- `e17_bin_influence.py` → `result.json`, `run.log`
