# E18 — RETRACTED 2026-09-03: the subtraction formula is the retracted E12 identity

> **STATUS: the method of this experiment is wrong. Do not cite `result.json`.**

E18 subtracted each box's own periodic contribution from its evidence-time centroid using
the identity retracted in E12: an integer number of mains periods cancels the *zeroth*
moment of a periodic rate, not the *first*. The centroid contribution of a periodic
component is `-(A/lambda_0) sin(phi)/omega`, which vanishes only when `sin(phi) = 0`. E18
applied that cancellation to a window of **1.4996 periods**, so the correction it computed
was not the correction it was meant to compute.

The numbers on disk (`result.json`, 1134 frames: RAW excess 183.6 us, PHASESUB 311.2 us,
SHAMSUB at 137 Hz 185.2 us) were measured correctly under a false identity, and the
PHASESUB arm rising above the raw arm is the visible symptom of it.

Nothing from this experiment appears in the paper. The route that replaced it is E19,
which stratifies by each box's own modulation depth rather than attempting to subtract it,
and E19 is what demotes the scalar dispersion to a bounded statement.

See `experiments/e12_integer_period/README.md` and `docs/PROTOCOL_LEDGER.md` entry 2.
