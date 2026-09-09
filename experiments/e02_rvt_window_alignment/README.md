# E02 — Verifying that RVT's event window ends at the label time (2026-09-01)

Checked against the RVT source itself (github.com/uzh-rpg/RVT, master), not against a
paper's description of it.

`config/dataset/gen1.yaml`:

    ev_repr_name: 'stacked_histogram_dt=50_nbins=10'
    sequence_length: 11
    resolution_hw: [240, 304]

`scripts/genx/preprocess_dataset.py`, in `labels_and_ev_repr_timestamps`:

    line 343-344   align_t_ms, ts_step_ev_repr_ms   are parameters
    line 348-350   ts_step_frame_ms = 100; assert ts_step_frame_ms % ts_step_ev_repr_ms == 0
    line 405       ev_repr_timestamps_us_end = list(reversed(range(frame_timestamps_us[0], 0, -delta_t_us)))[1:-1]
    line 409-415   the edge timestamps are then extended between consecutive frame_timestamps_us

The variable is named `ev_repr_timestamps_us_end` and it is constructed by counting
**backwards from a label timestamp** in steps of `delta_t_us`. Every event representation
is therefore indexed by the **end** of its window, and the window boundaries are placed to
land on label times.

## Consequence

A `dt=50ms` representation attached to a label at time `t` is built from events in
`[t - 50 ms, t]`. Under uniform weighting its information centroid is `t - 25 ms`, while
the label asserts the state **at** `t`. The offset is a property of the published
configuration, not of anything measured.

This matters for the metric-oriented idea (team 8): the sign and rough magnitude of the
temporal bias can be **stated before the measurement is run**, from the released config.
A metric that then recovers it is not a metric tuned to make its authors win.

## Limits of this check

- Verified for `gen1`; `gen4`/1 Mpx uses the same code path but was not separately read.
- "Information centroid at `t - 25 ms`" assumes the ten bins contribute equally. Whether
  the trained network actually weights them uniformly is exactly the empirical question,
  and this note does not answer it. The 25 ms figure is the uniform-weight reference
  point, not a prediction of the network's behaviour.
