# E44 — the same measurement on three released capacities (2026-09-07)

## Why this exists

Every predictor-side measurement was on `rvt-t`. External review #5 named a second released
detector as the single highest-value reduction of the "one checkpoint" objection, and
answered "is a Weak Reject reasonable for its absence?" with Borderline — the only one of
its three candidate experiments to get anything other than No.

RVT publishes three capacities for Gen1 that differ only in `embed_dim`, attention
`dim_head` and FPN depth (`config/experiment/gen1/{tiny,small,base}.yaml`). The same
measurement therefore runs on each without changing dataset, representation, evaluation
code, or the window the release fixes. All three load with **0 missing and 0 unexpected
keys** (E43).

## Result

576 samples over the same 12 Gen1 validation sequences, recurrent state warmed 8 steps,
lags to 1 s, identical code for all three.

| | rvt-t | rvt-s | rvt-b |
|---|---|---|---|
| parameters | 4.41 M | 9.87 M | 18.54 M |
| newest-window influence centroid | **−23.84 ms** | **−23.89 ms** | **−24.11 ms** |
| CV of the profile over bins | 0.132 | 0.122 | 0.107 |
| support centroid, 500 ms horizon | −160.6 ms | −168.7 ms | −173.4 ms |
| newest window's share, 500 ms | 30.0 % | 29.2 % | 26.8 % |
| support centroid, 1000 ms horizon | −299.4 ms | −337.3 ms | −339.3 ms |
| newest window's share, 1000 ms | 22.7 % | 20.6 % | 19.0 % |
| zeroing the state, over removing the newest window | 3.76 | 3.73 | 3.03 |

The newest-window centroid spans **0.27 ms** across a four-fold range of capacity. The
newest window's share of the influence falls slightly with capacity, 22.7 % to 19.0 %, and
the support centroid moves further back with it. Zeroing the recurrent state costs three to
four times what removing the newest window costs, in every capacity.

Each of these is therefore a property of the released configuration and of the recurrent
form, not of one trained checkpoint.

## What it caught

Running the same quantity through two code paths exposed a defect in the older one. E44's
`rvt-t` centroid is −23.84 ms; E17 and E34 reported −24.94 ms. The cause is the recurrent
state handed to the occluded pass: E17 passed the state the reference forward **returned**,
which has already absorbed the unoccluded window, where the counterfactual needs the state
**entering** the step. E45 repeats E34's four instruments with the entering state.

## What this does NOT establish

Three capacities of one architecture on one dataset. A second architecture — a state-space
or transformer-decoder event detector — would test whether the recurrent share is a
property of recurrence in general, and is not run. The influences are norms of differences
and remain a weighting rather than a decomposition.
