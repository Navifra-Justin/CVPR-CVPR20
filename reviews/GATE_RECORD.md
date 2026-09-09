# Gate record — Team 08, two review rounds (2026-09-01)

## Round 1, on `ideas/team08.md`

| reviewer | specialism | verdict |
|---|---|---|
| R1 | event sensor physics | ACCEPT |
| R2 | estimation theory | ACCEPT (its winner) |
| R3 | benchmarks and metrics | ACCEPT (ranked 2nd behind team 06) |
| R4 | feasibility | STRONG ACCEPT |
| R5 | prior art | ACCEPT (novelty cut 7 -> 5) |
| R6 | deblurring | ACCEPT |
| R7 | robotics impact | STRONG ACCEPT |
| R8 | claim calibration | STRONG ACCEPT |
| R9 | area chair | STRONG ACCEPT (its decision) |
| R10 | hostile | **BORDERLINE** |

Eight of ten named Team 08 their winner. **The gate did not pass**: one BORDERLINE sends
the work back for revision, so it went back.

## Round 2, on `ideas/team08_v2.md`

Five reviewers re-run — the four whose objections drove the revision, plus the hostile one
who held the gate. The other five accepted in round 1 and their verdicts stand.

| reviewer | round 1 | round 2 | movement |
|---|---|---|---|
| R2 | ACCEPT | **WEAK ACCEPT** | down; the levers do not do what the revision claims |
| R3 | ACCEPT | ACCEPT | unchanged in letter, stronger in substance |
| R5 | ACCEPT | ACCEPT | novelty held at 5/10 |
| R7 | STRONG ACCEPT | ACCEPT | down, because its own round-1 objection was right |
| R10 | **BORDERLINE** | **ACCEPT** | **the gate-holding vote flipped** |

**Ten of ten now sit at ACCEPT or above.** The gate passes.

It passes **conditionally**, and the conditions are recorded here so that "ten reviewers
passed it" is never read as stronger than it is. R2 graded WEAK ACCEPT, which is not one of
the rubric's four levels; it is above BORDERLINE and it arrives with a named minimum change.
R10's ACCEPT carries four conditions and it named one of them as a REJECT trigger if
unaddressed at submission.

## Conditions attached to the pass

1. **R2 — the three no-training levers do not vary temporal support.** Derived and verified
   numerically: masking measures the conditional evidence centroid of a *fixed* influence
   profile under off-distribution input, while Panel C needs the effective timestamp of a
   predictor *matched* to that support. They coincide only when the network is a
   non-negative self-normalising non-extrapolating smoother — which is the hypothesis Panel C
   exists to test. At extrapolation strength 0.99 the masked reading gives -10.16 ms against
   a retrained -0.39 ms, a 26x discrepancy. **Corroborated independently by E05 in this
   repository**, which measured the masking response saturating past 25 ms. R2's minimum
   change is ~9 GPU-hours and needs no raw data: fine-tune on *masked stored tensors* at
   five mask levels and report the frozen-minus-finetuned difference.
2. **R3 — `AP^sync` has a test-set fit leak.** Its calibration constant is the slope of a
   regression on ground-truth tracks, fitted and applied on the same evaluation data, and
   refitting inside each bootstrap replicate reproduces the leak rather than removing it.
   The free fix is to report `AP^bias` — the other parameter of the same regression — as the
   missing null.
3. **R5 — two uncited ancestors.** Qin and Shen, IROS 2018 (VINS-Mono online temporal
   calibration) publishes `z(t_d) = [u,v]^T + t_d V` with `V` finite-differenced from
   consecutive observations, which is this paper's estimator, in vision, four years before
   LET-3D-AP, and is uncited in both versions. And `AP^sync` is close to scooped by sAP's
   Streamer. Both must be cited and differentiated.
4. **R10 — estimate `tau_hat` at anchor times.** Named as its REJECT trigger.
5. **R7 — the effect is small where it was measured.** At the pre-registered 3 ms dispersion,
   leaving it unmodelled costs a constant-velocity filter 0.10-1.64 % of RMS position error.
   R7 supplies the rescue the paper is not using: E00 and E02 together predict a
   **cross-branch** dispersion of 7.2 ms, worth about +20 % RMS, which would be decisive.

## Corrections this repository's measurements made to the reviews

- **E06 refutes the premise of R10's round-2 killing review.** R10 argued that moving the
  primary testbed to DSEC-Det puts the headline on linearly interpolated labels, producing a
  sawtooth that forges three results. Measured: all 390 118 released DSEC-Det labels sit on
  the 20 Hz frame clock, no spacing below 40 ms exists, and the linear-interpolation residual
  is 0.707 px median rather than ~0. **The released labels are not interpolated**, so that
  mechanism cannot operate. What survives untouched is the separate question of whether the
  20 Hz labels are themselves detector output.
- **E04 closes R4's stated fatal flaw.** The released RVT checkpoint loads under
  torch 2.7.1+cu128 with zero missing and zero unexpected keys and runs forward, with
  pytorch-lightning never installed.
- **E00 falsified Team 1's pre-registered prediction** and was used by four reviewers.
- **E07** pulled the LET-3D-AP citation graph R5 could not: 40 citing papers, none applying
  the decomposition to a temporal axis or to event cameras — on a sample of unknown coverage,
  with one paper still unread.
