# Event I/O validated end to end (2026-09-01)

`interlaken_00_c` events downloaded (817 MB zip -> 1.7 GB) and read inside
`cvpr19-gpu-g1:torch2.7.1-cu128` with `h5py` + `hdf5plugin` (pip-installable in-image).

    /events/p  (455650825,) uint8
    /events/t  (455650825,) uint32     # microseconds, relative
    /events/x  (455650825,) uint16     # max 639
    /events/y  (455650825,) uint16     # max 479
    /ms_to_idx (26801,)     uint64     # millisecond -> event index, free random access
    /t_offset  ()           int64      # 51805200776

455.6 M events, 640x480, 26.8 s. `ms_to_idx` means an arbitrary time window can be sliced
without scanning the stream, which is what makes a support-sweep experiment cheap.

## The clocks line up

- absolute first event time  = t_offset + t[0] = **51805200776 us**
- first frame exposure start = **51805200087 us**
- first frame exposure end   = **51805201557 us**

The event stream begins **689 us after the first exposure opened and 781 us before it
closed** — inside the first frame's integration window, on the same clock. Events and
exposure windows are therefore directly comparable in absolute time with no calibration
step, which is the precondition for measuring anything about temporal support on this data.

## Practical notes

- The image has no NVIDIA driver visible unless `--gpus '"device=1"'` is passed; the I/O
  check above ran CPU-only on purpose.
- `hdf5plugin` is required — DSEC events use a Blosc filter and `h5py` alone cannot read
  them.
