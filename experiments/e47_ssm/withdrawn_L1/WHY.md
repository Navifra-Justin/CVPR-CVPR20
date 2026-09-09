# Withdrawn: the L=1 calling convention makes S5-ViT stateless (2026-09-08)

These files were produced by calling SSM-ViT's backbone one step at a time, `L = 1`, with the
recurrent state carried across calls — the convention RVT uses and the one E45 and E48 use.

That convention carries no history at all in this implementation. In
`src/SSMViT/models/layers/s5/s5_model.py`, `apply_ssm` injects the previous state as

    Lambda_bars[0] = Lambda_bars[0] * prev_state
    _, xs = associative_scan(binary_operator, (Lambda_bars, Bu_elements))

with `binary_operator((a_i,b_i),(a_j,b_j)) = (a_j*a_i, a_j*b_i + b_j)`. The scan's outputs
are the `b` components, and `b_p` is built from `a_1..a_p` and `b_0..b_p`. `Lambda_bars[0]`
enters only the `a` component of the first element, so it reaches no output: the carried
state is inert at every position, which E47c then measured directly. With a chunk of length
one there is no in-chunk recurrence either, so the model runs with no history whatever.

An earlier reading of this code, recorded in the first version of this note, said the state
reached positions 1, 2, ... and only missed position 0. The measurement contradicted it, and
re-deriving the scan showed the measurement was right.

The measurement said so plainly, which is how it was caught: zeroing the recurrent state
changed the emitted detection tensor by 0.0000, and every past window's influence was zero
against 0.1401 for the newest. A recurrent detector that is unaffected by its own history is
not a result, it is a symptom.

The consequence for the per-bin numbers in `s5vit-*-bins.json` (-23.91 and -24.97 ms) is that
they describe the model run without history, which is not the regime the released checkpoint
is evaluated in and not the instrument applied to RVT. They are withdrawn rather than
reported, and E47b repeats them with the released chunked convention.

The released evaluation calls the backbone with the whole sequence at once
(`modules/detection.py`: `forward_backbone(x=ev_tensor_sequence, ...)` where the tensor is
`(L, B, C, H, W)`), then applies the detection head per step. E47b does the same: a chunk of
`L` windows with the state entering the chunk, occlusion applied to the last window only, and
the output read at the last position.
