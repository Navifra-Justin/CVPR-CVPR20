# E65 — the chunk-boundary intervention applied to RVT, in two state regimes

## What this measures and why

Main Sec. 3 differences the observational chunk-position contrast against the three RVT
checkpoints. That differencing is only valid if an RVT chunk boundary is not an effective
reset. The released implementation says it is not — `modules/detection.py` keeps the
validation state in `mode_2_rnn_states` and clears it only on `is_first_sample` — but reading
the source is not a measurement. E65 measures it.

The design is 2 x 2: regime x shift, on two released RVT checkpoints.

| regime | `RESET` | what it is |
|---|---|---|
| `carry` | 0 | the released behaviour; the arm the paper's control assumes is boundary-insensitive |
| `reset` | 1 | state dropped at every chunk start, which puts RVT in the condition the SSM release is already in; the positive control that proves the treatment reaches the model |

Shift 0 is the release's own placement; shift 5 moves every boundary five windows later,
rotating each labelled frame's position by `-5 (mod 21)` and carrying the starved block
(positions 0–3) onto 16–19. The estimand is E60's, unchanged, so the rows are directly
comparable to `experiments/e60_*/dose.json`.

## Result

`paired-shift5.json`, n = 3574 paired frames, cluster bootstrap over the 406 validation
sequences with B = 300, permutation null R = 200:

```
  rvt-s-carry   dmAP(vel)  -0.0101 +- 0.0344  95% CI [-0.0591, +0.0786]  z= -0.29
  rvt-s-reset   dmAP(vel)  +5.3913 +- 0.4490  95% CI [+4.6724, +6.3376]  z=+12.01
  rvt-b-carry   dmAP(vel)  +0.0522 +- 0.0393  95% CI [-0.0369, +0.1174]  z= +1.33
  rvt-b-reset   dmAP(vel)  +6.9144 +- 0.6371  95% CI [+5.3509, +7.8387]  z=+10.85
```

Random-frame permutation nulls are centred within 0.112 points of zero with sd <= 0.33 in
every arm, so the pairing itself does not move the number.

Reading: under the released carried state the boundary does nothing; with the state dropped
at the boundary the same weights on the same frames gain a magnitude comparable to the SSM
release's own +5.23 / +4.81. Within this protocol the boundary effect follows whether the
recurrent state survives the boundary, not the architecture. The comparison covers two RVT
capacities on Gen1 validation at one shift amount and says nothing about training-time
behaviour, which is not what either release's streaming evaluator exercises.

## Why a null here is readable

A null is only evidence if the treatment was applied and the driver was not silently broken.
Three things establish that:

1. **Bit-identity at shift 0.** `src/e65_regress_check.py` requires the chunked `carry`
   shift-0 dump to reproduce the stored per-window release dump detection for detection —
   101,591 for rvt-s, 74,805 for rvt-b — with identical ground truth, and requires the
   recorded positions to equal `experiments/e58_chunkpos/positions.npy` frame for frame. Both
   tags pass all ten checks (`regress-s.log`, `regress-b.log`). The gate is itself
   mutation-tested by `src/e65_gate_selftest.py`: 10 of 10 corruptions are rejected.
2. **The positive control.** The `reset` arms move by +5.39 and +6.91 on the same frames with
   the same weights, so the shift demonstrably reaches the model.
3. **The permutation null.** Centred on zero in all four arms.

## Layout

```
dets-rvt-{s,b}-{carry,reset}-shift{0,5}.npz   the eight dumps: det, gt, pos
paired-shift5.json / .log                     the analysis output and its console log
regress-{s,b}.log                             the wiring gate on the shift-0 carry arms
shard-selftest.log                            bit-exactness of sequence sharding
parts/                                        per-shard dumps before merging
selftest/                                     fixtures from the gate mutation test
pilot-rvt-s.npz                               the first single-sequence pilot
```

Sharding is exact rather than approximate: the dumper's recurrent state starts from `None` at
each sequence and never crosses a sequence boundary, so partitioning the sequence list over
processes is a partition of the work. `src/e65_merge_shards.py` restores sequence order and
renumbers frame ids; `src/e65_shard_selftest.sh` proves the merge bit-exact on twelve
sequences, and the full-dataset shift-0 bit-identity above proves it on all 406.

## Reproducing

```bash
bash run_e65_shift5.sh                 # the four shifted arms (GPU, Docker)
python3 src/e65_regress_check.py s     # wiring gate, per tag
SHIFT=5 python3 -u src/e65_paired.py   # the analysis -> paired-shift5.json
python3 src/e65_macros.py              # the \rvtBound* macros
bash src/e65_paired_selftest.sh        # the analysis exercised on synthetic dumps
python3 src/audit_numbers.py           # ties every macro back to this json
```
