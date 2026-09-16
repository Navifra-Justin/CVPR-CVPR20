# CPU-only temporal evaluation

This report summarizes existing prediction-dump evaluations. No model
inference, training, or new dataset processing was run.

## Speed-stratified sensitivity

| Stratum | Boxes | AP span (points) | AP cost at centroid (points) | Argmax (ms) |
|---|---:|---:|---:|---:|
| all moving | 27,943 | 0.372 | 0.059 | -10 |
| slow, |v| < 10 | 20,154 | 0.107 | 0.019 | -10 |
| 10 <= |v| < 25 | 5,356 | 0.333 | 0.035 | -10 |
| 25 <= |v| < 50 | 2,096 | 0.784 | 0.090 | -10 |
| fast, |v| >= 50 | 337 | 0.368 | 0.007 | -5 |

The largest stratum span is **0.784 AP points** in **25 <= |v| < 50**, compared with **0.372** points for all moving boxes.

## Checkpoint ranking stability

| Stratum | Checkpoints | Pairwise flips | Ordering changed | Maximum individual gain (points) |
|---|---:|---:|---|---:|
| all moving | 5 | 0 | no | 0.085 |
| 10-25 px/s | 5 | 0 | no | 0.136 |
| 25-50 px/s | 5 | 0 | no | 0.058 |
| >50 px/s | 5 | 0 | no | 0.065 |

The own-preferred-offset scores preserve the reported ordering in every
speed stratum. Under a common displacement sweep, the 25--50 px/s stratum
contains one localized inversion relation between rvt-b and s5vit-small;
the other evaluated strata contain no sign-changing pair.

## Common-offset ranking sweep

| Stratum | Pairwise sign-changing relations |
|---|---|
| all moving | none |
| 10-25 px/s | none |
| 25-50 px/s | rvt-b vs s5vit-small |
| fast (>50 px/s) | none |

The result supports a composition-dependent metric sensitivity claim: the
pooled curve is small because most boxes move slowly, while the middle-speed
stratum shows a larger displacement response.
