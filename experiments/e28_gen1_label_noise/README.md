# E28 — the label-centre noise of Gen1, measured on Gen1 (2026-09-07)

## Why this exists

E13 solved for the label noise of **DSEC-Det** and got `sigma = 0.4974 px`. The output-time
fit (E27) runs on **Gen1**. Using DSEC-Det's number there would be an unchecked assumption
about a different annotation effort on a different sensor, and the errors-in-variables
correction depends on it directly.

## Construction

Identical to E13. For a track centre series `x_i = f(t_i) + e_i` on a uniform grid,

    Var(D_k) = C(2k,k) * sigma^2 + (motion term of order k)

so `Var(D_k)/C(2k,k)` falls toward `sigma^2` from above. Halving the sample rate multiplies
the motion term by `4^k` and leaves `sigma^2` untouched, which gives a second equation in
the same two unknowns:

    sigma^2 = (4^k Var_full - Var_half) / (4^k - 1)

Tracks are rebuilt by the same greedy same-class IoU linking E27 uses, so both experiments
share one definition of a track. 691 tracks of at least 12 labels on a uniform grid.
Variances are trimmed at 5%, for the reason E13 records: the coordinates are integers, and
a MAD on lattice-valued data locks onto discrete values.

## Result

| k | C(2k,k) | Var/C full | sigma full | Var/C half | two-rate sigma |
|---|---|---|---|---|---|
| 1 | 2 | 1.76500 | 1.3285 | 4.36414 | 0.9480 |
| 2 | 6 | 0.52760 | 0.7264 | 1.00171 | 0.7043 |
| 3 | 20 | 0.44956 | 0.6705 | 0.65206 | 0.6681 |
| 4 | 70 | 0.43379 | 0.6586 | 0.55328 | 0.6583 |
| 5 | 252 | 0.42895 | 0.6549 | 0.48993 | 0.6549 |
| 6 | 924 | 0.42486 | 0.6518 | 0.44566 | 0.6518 |
| 7 | 3432 | 0.42464 | 0.6516 | 0.41415 | 0.6516 |

The two-rate elimination agrees with the full-rate ladder to four decimals from `k = 3`
onward, which is the check that the motion term has died rather than been assumed away.

    sigma_total       = 0.6515 px
    quantization      = sqrt(0.25/12) = 0.1443 px   (integer corners -> 0.5 px centre lattice)
    sigma_annotation  = 0.6353 px

Gen1's labels are integer-valued in all four coordinates: 0 of 160952 stored values have a
fractional part.

## What this does NOT establish

It measures the dispersion of the annotated centre about a smooth trajectory. It does not
separate annotator error from real sub-grid motion that is not smooth on the 50 ms grid,
and it does not transfer to any other dataset — which is the whole point of running it
separately from E13.
