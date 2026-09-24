# E15 — the per-object temporal term, taken through three passes of the protocol

## Why this exists

E14 asked whether the spread of evidence times inside a frame is large enough to matter
by multiplying the median dispersion by the median object speed. That is the product of two
medians, not the median of the product, and the quantity that actually displaces a box is
per-object: *its own* deviation from its frame's mean evidence time, times *its own* speed.
If deviation and speed are correlated, the honest figure is larger than E14's. E15 is the
12-step protocol applied to that question, and it is recorded here because two of the three
passes are negative — the negative passes are what make the third one credible.

## Pass 1 (step 3) — the per-object product, still below the floor

`e15_protocol_pass1.py` forms the per-object product and compares it against an isotropic
scalar noise floor.

| n | median | p90 | p99 | max | corr(dev, speed) | fraction above σ | fraction above the label quantisation |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 6770 | 0.0058 px | 0.0278 px | 0.0821 px | 0.398 px | −0.125 | 0.000 | 0.0025 |

The correlation runs the wrong way, the top decile still only reaches 0.027 px, and nothing
clears the label noise. Pass 1 is negative, and negative for a reason worth keeping: the
comparison was scalar against scalar.

## Pass 2 (step 10) — lift the comparison from 1-D to 2-D

A temporal error is not isotropic. It displaces a box **along** its own velocity and
contributes nothing across it, so it does not have to beat σ; as a systematic anisotropy
against isotropic noise it has to beat σ/√N. `e15b_pass2_anisotropy.py` fits each track's
centre with a local quadratic over a 5-sample window, takes the residual at the centre
sample, and projects it onto the unit velocity direction and its perpendicular.

| n | R = Var(along)/Var(cross) | 95 % CI | R under a randomised direction | SD along | SD cross |
|---:|---:|---|---:|---:|---:|
| 306381 | **1.939** | [1.594, 2.548] | 0.913 | 1.394 | 1.001 |

Residuals are elongated along the motion by a factor of nearly two, and the direction-
randomised null sits at 1. Changing the dimension of the comparison, step 10, is what turned
the sign.

## Pass 3 (step 11) — a new method, because R = 1.94 has two explanations

Elongation along the motion is predicted both by (A) a real per-object temporal term and by
(B) ordinary local-fit error, which also accumulates along the direction of travel and needs
no temporal term at all. `e15c_pass3_crosslink.py` separates them with a quantity only (A)
predicts: pair each box's along-track label residual with that box's **independently
measured** evidence-time deviation, taken from the event stream by the E09/E11 route. Under
(A) the slope is 1 in units of `x · 1e-6 · v` and the cross-track slope is 0. Under (B) there
is no relation, because a polynomial fit to label positions knows nothing about the events.

| n | r along | slope along | r cross | slope cross | r under permutation |
|---:|---:|---:|---:|---:|---:|
| 6186 | 0.0047 | 0.474 | −0.0055 | −0.467 | −0.0011 |

Both correlations are at the permutation floor, and the two slopes are equal and opposite —
the signature of a fit with no signal in it, not of a temporal term. **Pass 3 is negative,
and it is the one that decides**: the anisotropy of pass 2 is local-fit error, not a
per-object temporal offset. The paper therefore claims a frame-level timing ambiguity and
does not claim a per-object one.

## Files

- `e15_protocol_pass1.py` → `pass1.json` — the per-object product against the scalar floor
- `e15b_pass2_anisotropy.py` → `pass2.json` — the along/cross variance ratio and its null
- `e15c_pass3_crosslink.py` → `pass3.json` — the cross-link that separates (A) from (B)
