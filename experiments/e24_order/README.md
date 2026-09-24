# E24 — which extrapolation order the residuals actually support

## Why this exists

E21 fitted `e_par = b + τ|v|`, a **zeroth-order** model: the detector reports the object's
position at one fixed instant τ in the past, so the residual grows linearly with speed. That
is not the only possibility. A detector that extrapolates could instead be leaving a residual
proportional to acceleration, in which case the anisotropic coefficient on the acceleration
term should be τ²/2 rather than τ. The two orders make different, checkable predictions about
*which* regressor carries the along-minus-cross anisotropy, and E24 fits both at once.

## Method

Regress the along-track and the cross-track residual on the same design — intercept, speed,
box size, acceleration — and read off the **anisotropic** part, along minus cross, for each
coefficient. Cross-track is the null channel: a timing term lives only along the motion, so a
coefficient that shows up equally in both is a nuisance, not a lag. `rvt-t`, Gen1 val,
CONF = 0.1, NMS = 0.45, minimum speed 10 px/s, n = 4332.

## Result

| regressor | along | cross | anisotropic | |
|---|---:|---:|---:|---:|
| intercept | −3.4266 (23.2 SE) | −0.6946 (10.7 SE) | −2.7320 | 16.94 SE |
| speed (order 0) | −0.0146 (3.2 SE) | −0.0312 (15.5 SE) | +0.0166 | 3.34 SE |
| size | +0.1215 (46.0 SE) | +0.0455 (39.0 SE) | +0.0761 | 26.37 SE |
| accel (order 1) | +0.0198 (10.0 SE) | +0.0117 (13.4 SE) | +0.0080 | 3.72 SE |

Converting each to the lag it would imply:

- order 0 predicts the anisotropic **speed** coefficient equals τ. Measured +0.01663 s →
  **τ = +16.6 ms**, comfortably inside the 50 ms window.
- order 1 predicts the anisotropic **accel** coefficient equals τ²/2 = 0.000311 s². Measured
  +0.00805 → **τ = 126.9 ms**, which is 2.5 windows and physically incompatible with the
  architecture.

The order-1 reading is self-refuting, so the residuals — insofar as they carry any timing at
all — carry it at order 0. The dominant term in the table is neither: **box size**, at 26.4 SE
anisotropic, is much the largest, which is the same confound E21 ran into.

## The signed variant, and why it matters

`e24_signed.py` re-runs the identical fit on **signed** residuals rather than magnitudes. The
distinction is not cosmetic: a lag maps onto the speed coefficient only for a signed residual;
a magnitude regression answers a different question ("does the error grow?") and cannot be
converted into a τ at all.

| | anisotropic speed | implied τ | anisotropic accel | implied τ |
|---|---:|---:|---:|---:|
| magnitude (`result.json`) | +0.01663 | +16.6 ms | +0.00805 | 126.9 ms |
| **signed** (`signed.json`) | **+0.05183** | **+51.8 ms** | −0.01185 | — (wrong sign) |

On the signed fit the acceleration coefficient changes sign, killing the order-1 reading
outright, and the order-0 lag moves to 51.8 ms. The spread between 16.6 and 51.8 ms across two
defensible estimators on the same 4332 boxes is the real content of this experiment: **the
residual route does not pin the lag to better than a factor of three**, which is why the paper
does not quote a τ from it.

## Files

- `e24_order.py` → `result.json`, `run.log` — magnitude residuals, both orders
- `e24_signed.py` → `signed.json`, `signed.log` — signed residuals, plus the magnitude fit
  reported alongside so the two are visibly the same data
