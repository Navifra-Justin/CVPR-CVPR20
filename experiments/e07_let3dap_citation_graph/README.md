# E07 — The LET-3D-AP citation graph (checked 2026-09-01, main session)

Reviewer 5 named this "the only remaining check with a realistic chance of being fatal":
LET-3D-AP is the acknowledged ancestor of the paper's device, so if anyone in its citation
graph has already carried the decomposition to a **temporal** axis, or to event cameras,
the remaining novelty is gone. Reviewer 5 could not pull the graph; this is that pull.

Source: Semantic Scholar graph API,
`/paper/arXiv:2206.07705/citations?fields=title,year,venue,abstract&limit=100`.
Raw response saved beside this file.

## Result

**40 citing papers returned.** Filtering titles and abstracts for
`temporal | time | timestamp | latency | clock | event camera | event-based | async |
exposure | streaming | sync` leaves **6**:

| year | venue | title |
|---|---|---|
| 2026 | J. King Saud Univ. | DCRT: Depth-confidence-guided complementary residual temporal adapter for camera-based BEV 3D object detection |
| 2025 | arXiv | StixelNExT++: Lightweight Monocular Scene Segmentation and Representation for Collective Perception |
| 2025 | arXiv | Rethink 3D Object Detection from Physical World |
| 2025 | arXiv | Cosmos-Drive-Dreams: Scalable Synthetic Driving Data Generation with World Foundation Models |
| 2024 | IEEE TIP | Graph-DETR4D: Spatio-Temporal Graph Modeling for Multi-View 3D Object Detection |
| 2023 | CVPR | 3D Video Object Detection with Learnable Object-Centric Global Optimization |

Five of the six use "temporal" to mean multi-frame feature aggregation, which is a
different thing from an error axis. **None applies an error decomposition to a time axis,
and none involves an event camera.** On this sample the check comes back clean and the
remaining novelty survives.

## Limits of this check — read before relying on it

1. **40 citations is what the API returned, not necessarily all of them.** A follow-up call
   for the paper's total `citationCount` was **rate-limited (HTTP 429)** before it returned,
   so the coverage fraction is unknown. This is a sample, not a census, and it should be
   redone with an API key.
2. **One paper is unresolved.** *Rethink 3D Object Detection from Physical World* (2025) is
   the one title whose framing could plausibly concern latency rather than feature
   aggregation. Two attempts to fetch its abstract failed — Semantic Scholar returned 429
   and the arXiv API returned an empty document. **It has not been read and it must be**
   before this check is cited as clean.
3. Keyword filtering on title plus the first 600 characters of abstract will miss a paper
   that does the relevant thing without saying so early. Reviewer 5 made the same point
   about arXiv keyword conjunctions in round one, and it applies here too.

## Standing items reviewer 5 left open and this does not close

IEEE Xplore, T-PAMI, RA-L, ICRA and IROS — which is where both of reviewer 5's hardest
findings came from, including **Qin & Shen, IROS 2018** (VINS-Mono online temporal
calibration), whose estimator `z(t_d) = [u,v]^T + t_d·V` with `V` finite-differenced from
consecutive observations is the paper's `δ̂ = e_∥/‖v*‖` in vision, four years before
LET-3D-AP, and is uncited in both versions of the idea. Also open: ICLR, ICML, AAAI.
