# E13 — Solving for the label noise instead of bounding it (2026-09-02)

E08 reported `sigma_c <= 0.497 px` as an **upper bound**, because real jerk also enters the
third difference and could not be separated from noise. That is one equation in two
unknowns. This experiment supplies more equations with different coefficients on the same
two unknowns and solves the system.

## The construction

For `x_i = f(t_i) + e_i` on a uniform grid, the k-th difference has

    Var(D_k) = C(2k,k) * s^2  +  (motion term of order k)

`C(2k,k)` grows as 2, 6, 20, 70, 252, 924, 3432 while the motion term falls, provided the
trajectory is smooth on the 50 ms grid. So `Var(D_k)/C(2k,k)` approaches `s^2` from above
and the sequence itself shows the approach.

A second, independent equation comes from **halving the sampling rate**: taking every other
sample multiplies the motion term by `4^k` and leaves `s^2` untouched. Two rates give

    s^2 = ( 4^k * Var_full(D_k) - Var_half(D_k) ) / ( 4^k - 1 )

## A failure that had to be fixed first

The first run used a MAD-based variance and returned **bit-identical** sigmas for the full
and half rate at k=2 and k=3 (0.6053 and 0.4973), which cannot happen with different sample
counts. The cause is in the data, not the code: **DSEC-Det stores `x`, `y`, `w`, `h` as
integers** — every fractional part is exactly 0 — so box centres lie on a 0.5 px lattice,
and a MAD on lattice-valued data locks onto discrete values. Re-run with a trimmed
empirical variance, which moves continuously with the data.

## Result

| k | C(2k,k) | Var/C, full rate | sigma_total, full | Var/C, half rate | sigma from the two-rate elimination |
|---|---|---|---|---|---|
| 2 | 6 | 0.34504 | 0.5874 | 0.65744 | 0.5694 |
| 3 | 20 | 0.29567 | 0.5438 | 0.46152 | 0.5413 |
| 4 | 70 | 0.28097 | 0.5301 | 0.40975 | 0.5296 |
| 5 | 252 | 0.27316 | 0.5226 | 0.38001 | 0.5225 |
| 6 | 924 | 0.26765 | 0.5174 | 0.35916 | 0.5173 |
| 7 | 3432 | 0.26175 | 0.5116 | 0.34184 | 0.5116 |

The half-rate ladder sits above the full-rate one and the ratio falls from 1.848 at k=1 to
1.143 at k=7, which is the behaviour the `4^k` scaling predicts. The two-rate elimination
agrees with the full-rate ladder to four decimals from k=4 onward, because `4^k` makes the
full-rate term dominate — the elimination confirms the ladder rather than replacing it.

The full-rate tail differences are -0.0137, -0.0074, -0.0053, -0.0057, a ratio near 0.713.
Geometric extrapolation gives

    sigma_total  ->  0.4974 px

**Quantization is a computable part of that.** A uniform 0.5 px lattice contributes
`q^2/12 = 0.02083 px^2` to every position independently, so

    sigma_annotation = sqrt(0.4974^2 - 0.02083)  =  **0.476 px**

## What this changes

E08's `<= 0.497 px` was a bound; this is a value with a convergence argument behind it, plus
a decomposition. The two figures are close, so E08's bound was nearly tight — but it was
tight by luck, and the intermediate MAD result of 0.4203 px at k=5 was an artifact of the
lattice rather than a better estimate. Any number taken from that first run should be
discarded.

**Two facts worth stating in the paper.** The DSEC-Det boxes are integer-valued, so the
annotation carries a 0.144 px quantization floor that no method can go below. And the
remaining annotation noise, 0.476 px, is what a temporal estimate has to work against: at
the median object speed measured in E08 (40 px/s), it corresponds to 11.9 ms of timing.

## Limits

- The full-rate ladder is **still decreasing at k=7**; 0.4974 is an extrapolation, not an
  observed plateau. The last four differences are not perfectly geometric (-0.0053 then
  -0.0057), so the extrapolation is worth about two decimal places, not three.
- Trimming at 1 % on each tail is a choice. It was not swept.
- The smoothness assumption is that the motion term falls with k. It is supported by the
  observed monotone decrease and by the two-rate agreement, not proved.
