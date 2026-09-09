# E51–E54 — does the interval change a comparison? (2026-09-08)

## Why this exists

External review #7 accepted the paper's measurements, found no technical flaw, and named one
gap: the temporal support is shown to exist and never shown to change a benchmark
*conclusion*. Its suggested experiment was a cross-model, time-aware re-evaluation — does the
ordering of detectors change when each is scored at the instant its own output describes?

## Protocol

E51 dumped detections for all five released Gen1 checkpoints over the whole validation split
under one protocol: same frames, same confidence threshold (0.01), same NMS (0.65), each
model driven the way its own release drives it (RVT one window per call; SSM-ViT in
non-overlapping chunks of 21 with the head applied per position, chunk starts placed as
`sequence_for_streaming.py` places them).

Two things were checked before any comparison was drawn:

- `dets-rvt-t.npz` reproduces E37's `dets.npz` **exactly**, detections and ground truth,
  0 differing entries. An earlier version did not — it rebuilt track links by a backward
  greedy match instead of inverting the forward links, and 193 of 40 698 velocities differed.
  See case 11 in `docs/PROTOCOL_LEDGER.md`.
- The ground-truth array is identical across all five dumps. E52 exits rather than compare
  if it is not.

E52 and E53 then swept δ per model in four speed strata, and E54 emitted the macros.
`src/e52_selftest.py` checks the rewritten evaluator against four numbers already in the
paper (0.334580 at δ=0, 0.334193 at −23.810 ms, 0.333990 at −25 ms, 0.334632 at −10 ms);
all four agree to six decimals.

## Result: the ordering does not change, and cannot

| stratum | ordering at the label instant | smallest gap | largest gain | reorderable |
|---|---|---|---|---|
| all moving | b > s > t > S5-B > S5-S | 0.472 pt | 0.085 pt | no |
| 10–25 px/s | S5-B > b > t > S5-S > s | 0.331 pt | 0.136 pt | no |
| 25–50 px/s | S5-B > b > S5-S > s > t | 0.112 pt | 0.058 pt | no |
| >50 px/s | b > t > S5-S > s > S5-B | 0.209 pt | 0.065 pt | no |

Scoring each model at its own preferred displacement leaves every ordering unchanged and
reverses no pair, 0 of 10 per stratum. The per-model preferred displacement does differ, from
−15 to 0 ms.

**This is a bound, not a failure to find an effect.** In every stratum the largest gain any
model draws from alignment is at most 52 % of the smallest gap between adjacent models, so no
refinement of the δ grid — nor a continuous optimum — can reorder them. The negative result
is closed by arithmetic.

## What did move: speed, not alignment

The ordering is not stable across strata. `s5vit-base` is first in both middle strata and
**last** above 50 px/s; `rvt-t` is third overall, last between 25 and 50 px/s and second above
50. The aggregate number and the fast-object number name different winners, and the size of
that reordering is more than ten times the largest alignment effect. That is a reason to
report strata, but its cause is object speed, not the temporal support this paper measures,
and the manuscript says so.

## Where it went in the paper

One clause in main Sec. 3.6, on the sentence that already says the metric does not register
the separation, and a supplement section with the table. The conclusion carries "and no
reordering".

## Files

- `dets-*.npz` — the five dumps (detections, ground truth, centered label velocities)
- `curves.json`, `curves_fast.json` — mAP(δ) per model per stratum
- `summary.json`, `macros.tex`, `ranking.json` — the orderings, the bound, the manuscript macros
- `ranking.log`, `fast.log`, `macros.log` — the runs
