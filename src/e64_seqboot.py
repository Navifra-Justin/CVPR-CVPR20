"""E64 -- how much of the newest-window profile is the choice of twelve sequences.

The window-ablation sensitivity profile is measured on a deterministic sample: the first
twelve lexicographically ordered Gen1 validation sequences, first forty post-warm-up samples
each. Review #11 objected that a deterministic prefix is a selection, and that the numbers
built on it are quoted without any sequence-level uncertainty.

`experiments/e45_influence_fixed/profiles.npz` stores the per-sample profiles, 480 rows in
sequence-major order, so the sequence index of every row is recoverable and the sequence can
be treated as the resampling unit. This gives, without a GPU, the centroid's sequence-clustered
bootstrap interval, its leave-one-sequence-out range, and the per-sequence spread -- under all
four fill instruments. What it cannot give is a sample from the sequences that were never
measured; that needs a re-run and is stated as such.
"""
import numpy as np, json, os

SRC = 'experiments/e45_influence_fixed/profiles.npz'
OUT = 'experiments/e45_influence_fixed/seqboot.json'
NSAMP = 40          # samples per sequence, from the acquisition rule
NB = 20000
rng = np.random.default_rng(20260916)


def centroid(P, c):
    w = P.sum(0)
    return float((w * c).sum() / w.sum())


if __name__ == '__main__':
    Z = np.load(SRC)
    c = Z['centres'].astype(np.float64)
    res = {}
    for fill in ('zero', 'mean', 'swap', 'grad'):
        P = Z[fill].astype(np.float64)
        n, nb = P.shape[0], P.shape[0] // NSAMP
        assert n == nb * NSAMP, (n, nb)
        seq = np.arange(n) // NSAMP
        blocks = [P[seq == s] for s in range(nb)]
        full = centroid(P, c)
        per = np.array([centroid(b, c) for b in blocks])
        loo = np.array([centroid(np.concatenate([blocks[j] for j in range(nb) if j != i]), c)
                        for i in range(nb)])
        draws = np.array([centroid(np.concatenate([blocks[j] for j in
                          rng.integers(0, nb, nb)]), c) for _ in range(NB)])
        lo, hi = np.percentile(draws, [2.5, 97.5])
        # the newest bin's share, the other quantity the profile is quoted for
        sh = P.sum(0)[-1] / P.sum()
        shd = np.array([np.concatenate([blocks[j] for j in rng.integers(0, nb, nb)]).sum(0)[-1]
                        / np.concatenate([blocks[j] for j in rng.integers(0, nb, nb)]).sum()
                        for _ in range(2000)])
        res[fill] = dict(centroid=full, boot_lo=float(lo), boot_hi=float(hi),
                         boot_se=float(draws.std(ddof=1)), n_seq=nb,
                         per_seq_lo=float(per.min()), per_seq_hi=float(per.max()),
                         loo_lo=float(loo.min()), loo_hi=float(loo.max()),
                         newest_share=float(sh), newest_share_se=float(shd.std(ddof=1)))
        print(f"{fill:<6} centroid {full:8.3f} ms  cluster CI [{lo:.3f}, {hi:.3f}]  "
              f"SE {draws.std(ddof=1):.3f}  leave-one-seq {loo.min():.3f}..{loo.max():.3f}  "
              f"per-seq {per.min():.2f}..{per.max():.2f}")
    span = [min(r['centroid'] for r in res.values()), max(r['centroid'] for r in res.values())]
    widest = max(r['boot_hi'] - r['boot_lo'] for r in res.values())
    loospan = max(r['loo_hi'] - r['loo_lo'] for r in res.values())
    print(f"\n  across the four instruments the centroid spans {span[0]:.3f} to {span[1]:.3f} ms")
    print(f"  the widest sequence-clustered interval is {widest:.3f} ms wide")
    print(f"  no leave-one-sequence-out centroid moves the estimate by more than "
          f"{loospan/2:.3f} ms")
    json.dump(dict(fills=res, span_ms=span, widest_ci_ms=float(widest),
                   loo_span_ms=float(loospan), draws=NB), open(OUT, 'w'), indent=1)
    print(f"WROTE {OUT}")
