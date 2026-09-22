# Three-round verification of the chunk-position result (E58)

Required by the standing rule **"이 조건 반드시 3번이상 검수 필요"**. The claim under test is the
one that carries the paper's answer to the reviewer's significance objection:

> Under the released SSM-ViT streaming evaluation the recurrent history behind a detection
> ranges from 1 to 21 windows with its position in the chunk, and that variation is worth
> **5.32 mAP points** for S5-B (4.37 for S5-S) net of an architecture control, on every
> labeled Gen1 box.

Each round below is an independent route to the same conclusion. A round is only counted if it
could have falsified the claim on its own.

---

## Round 1 — the mechanism, from the released source and the released index files

*What could have failed:* the carried state might actually reach the outputs, in which case
position in the chunk would not bound the available history and there would be nothing to
measure.

Two separate checks:

1. **Algebraic inertness.** The SSM release injects the carried state as
   `Λ̄₀ ← Λ̄₀ ⊙ s` before an associative scan with operator
   `(aᵢ,bᵢ)∘(aⱼ,bⱼ) = (aⱼaᵢ, aⱼbᵢ+bⱼ)`. The scan's outputs are the `b` components, and
   `b_p` is built from `a₁…a_p` and `b₀…b_p`. The modified `a₀` appears in no output.
   Read off the released code, not inferred from behaviour.
2. **Empirical confirmation.** Zeroing the state entering a chunk changes the emitted
   detection tensor by a relative L2 of ~0 for SSM-ViT, while the same occlusion one position
   earlier *inside* the chunk produces a large change — so the probe is not insensitive by
   construction (`experiments/e42_recurrent_support/`, supplement Sec. 12).
3. **Position reconstruction.** Chunk starts follow from the release's own index files
   (`max(objframe_idx_2_repr_idx[0] − sequence_length + 1, 0)`, later chunks step by
   `sequence_length`). Reconstructing position over the 20 296 labeled frames reproduces,
   position by position, the frame counts the release's own loader produces.

**Verdict: passed.** The mechanism is real and position is recoverable without approximation.

---

## Round 2 — the numbers, against their artifacts and against corruption

*What could have failed:* the manuscript could quote a number the artifact does not contain,
or a number that no artifact constrains.

`src/audit_numbers.py` re-derives every manuscript macro from the JSON/NPZ artifact that
produced it, then mutates each artifact value and requires the check to reject it.

```
209 macros checked against their artifacts, 0 disagree
checker self-test: 209 of 209 entries reject a corrupted value; blind: none
```

"blind: none" means no macro is checked by a rule that would accept any value — every one of
the 209 is genuinely pinned. The nine new chunk-position macros
(`chunkRiseBase/Small/Rvt`, `chunkPermB/Sd/ZBase/ZSmall/PlaceboZ/P`) are inside that count.

**Verdict: passed.** No number in the paper is unsourced, and none is unconstrained.

---

## Round 3 — the inference, against a null that preserves everything except position

*What could have failed:* the effect could be an artifact of which frames land in which block —
early-chunk frames might simply be harder, or the reconstruction itself could induce the
grouping.

Three independent controls, each answering a different alternative explanation:

| Control | Alternative it kills | Result |
|---|---|---|
| **RVT placebos** (`src/e58d_allbox.py`) | frame difficulty at early positions | RVT state crosses chunk boundaries, so the same frames in the same order give |DiD| ≤ 0.67 pt |
| **Cluster bootstrap** over 406 sequences | sampling noise | SE 0.53/0.61 pt; S5-B z = 10.0, S5-S z = 7.2 |
| **Position permutation** (`src/e58g_perm.py`) | the reconstruction itself | position reshuffled *within each sequence*, preserving scene, sequence length, label density and both block sizes |

The permutation null is the strongest of the three because it holds constant everything the
first two leave open. Over B = 200 reshuffles:

```
model           observed  null mean  null SD    |z|  p (2-sided)
rvt-t              0.666     -0.045    0.469   1.52     0.1393   <- placebo
rvt-s             -0.507     -0.063    0.445   1.00     0.2687   <- placebo
rvt-b             -0.159      0.108    0.466   0.57     0.6070   <- placebo
s5vit-small       -4.373     -0.161    0.553   7.61     0.0050
s5vit-base        -5.322     -0.237    0.517   9.84     0.0050
```

The null is centered on zero, both SSM values sit 7.6σ and 9.8σ outside it at the smallest
p-value B = 200 can return, and all three placebos sit inside. A fourth, label-free statistic —
mean detection confidence — separates the same two blocks in the same direction
(0.499 → 0.566 for S5-B; RVT moves by ≤ 0.013), so the effect is visible without using the
labels at all.

**Verdict: passed.** The reconstructed chunk position is the only variable that carries the
effect.

---

## Summary

| Round | Route | Independent of | Outcome |
|---|---|---|---|
| 1 | released source + index files | any scoring | mechanism confirmed |
| 2 | artifact re-derivation + mutation | any modelling assumption | 209/209 |
| 3 | permutation null + placebos + label-free statistic | the bootstrap's assumptions | 9.84σ / 7.61σ, placebos inside |

Three rounds, three routes, one conclusion. Requirement satisfied.
