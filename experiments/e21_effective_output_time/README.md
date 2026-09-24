# E21 — the predictor's effective OUTPUT time, measured directly

## Why this exists

E17 measured the input influence profile by occluding bins and put its centroid at −24.94 ms.
A reviewer objected, correctly, that occlusion sensitivity equals a linear weight only for a
predictor linear in its bins. RVT is nonlinear and recurrent, so a network could weight the
whole window evenly and still extrapolate its output to the query instant. **Input influence
does not identify output time.** This measures the output time instead, and the fact that it
comes back weak is one of the load-bearing negative results in the paper.

## Method

Run the released `rvt-t` through Gen1 val sequentially, keeping the recurrent state,
postprocess to detections at each labelled frame, match to ground truth, project the residual
onto the track's own direction of travel and divide by its speed:

```
delta = <p - g, u> / |v|     seconds
```

A predictor describing the state at the query instant gives δ ≈ 0; one describing the state
τ earlier gives δ ≈ −τ along travel. The cross-track projection is the null: a timing lag has
no cross-track component.

## Result (n = 2235 matched boxes)

| quantity | value |
|---|---:|
| mean of per-box ratio | +7.13 ms |
| median | −3.23 ms |
| fixed spatial bias b | −0.340 ± 0.279 px (1.2 SE) |
| **τ from `e_par = b + τ·\|v\|`** | **+21.11 ± 8.38 ms (2.5 SE)** |
| cross-track bias | +0.035 ± 0.114 px |
| cross-track slope | +5.47 ± 3.41 ms (1.6 SE) |
| median speed | 26.2 px/s |

τ is nominally 2.5 SE from zero and of the right sign, but it does not survive the obvious
confound. Boxes that move fast are also big (r = +0.349 with √area), and adding box size as a
third regressor takes τ to **+11.9 ± 8.9 ms (1.3 SE)** while the size coefficient itself lands
at 3.0 SE. Fitting an intercept within each speed tercile gives +85.6 ± 80.9, +15.3 ± 56.4 and
+10.2 ± 20.8 ms — nothing is resolved inside a tercile.

**The honest reading**: this experiment cannot identify an output lag at this sample size, and
the size confound is at least as good an explanation as a lag. That is precisely why the paper
frames the output time as *consistent with* the label instant rather than *at* it, and why the
argument moved to instruments that do not depend on sub-pixel residuals — E42's influence tail
and E58's chunk position.

## Files

- `e21_effective_output_time.py` → `result.json`, `run.log` … `run5.log` (successive
  refinements: the ratio estimator, the regression with intercept, the size regressor, the
  within-tercile fits)
- `e21_debug.py`, `e21_trace.py` — the matcher and per-box traces used to check the residuals
