# E11 — Re-measuring the night dispersion with mains-locked pixels removed (2026-09-02)

E10 established that the DSEC night stream is dominated by a 100.00 Hz mains line, which
put the per-object evidence-time dispersion of E09 at risk of being a flicker artifact.
This is the first of two controls.

Method identical to E09 in every respect except the pixel set. Three arms:

- **ALL** — every pixel, reproducing E09.
- **CLEAN** — pixels not individually phase-locked (Rayleigh `p >= 1e-3` at 100 Hz, mask
  built from a 6 s slice, every 4th event).
- **RANDCTL** — a random pixel subset of exactly the same size as the excluded set. Without
  this arm, "we removed a quarter of the evidence and the effect went away" would be
  unanswerable.

Mask size: **14 334 pixels, 4.67 % of the sensor.** Note that E10's headline of 24.1 % is a
fraction of *live* pixels (at least 100 events), not of the sensor. The two figures have
different denominators and the paper must say which it means.

| arm | frames | within-frame sd | analytic null | **excess** | frames with sd > null |
|---|---|---|---|---|---|
| ALL | 1133 | 229.5 us | 93.4 us | **208.8 us** | 91.8 % |
| CLEAN | 1133 | 232.9 us | 97.6 us | **207.3 us** | 91.2 % |
| RANDCTL | 1133 | 229.4 us | 95.3 us | **207.5 us** | 91.6 % |

Removing the phase-locked pixels changes the excess by 0.7 %, and by less than the matched
random control does. The effect is not carried by the pixels that are individually locked
to the mains.

**Why this alone is not enough.** E10 measured a median Rayleigh `Z` of 2.935 across all
live night pixels against a null of 0.693, so a large population is weakly modulated
without reaching individual significance. Excluding only the significant ones leaves that
population in. E12 addresses this with a test that does not depend on identifying which
pixels are affected.

---

# CORRECTION (2026-09-02, same day) — the first run used the wrong window

Two independent checklist audits noticed that Table 2 of the paper carried the same night
configuration twice with different numbers. The cause was a defect in **this** experiment,
not in E12.

The first run sliced events to whole-millisecond boundaries via `ms_to_idx` and **never
restricted them to the exposure interval itself**. The analysis window was therefore
`[floor(a), floor(b)]` in milliseconds rather than `[a, b]` in microseconds, while the
analytic null was computed for the nominal width `w = b - a`. Data and null came from
different windows.

E12 filtered exactly (`t >= lo` and `t < hi`) and was right. Adding the same filter here:

| arm | frames | sd, first run -> exact | null, first -> exact | **excess, first -> exact** |
|---|---|---|---|---|
| ALL | 1133 -> 1134 | 229.5 -> **206.6** us | 93.4 -> 93.0 | 208.8 -> **183.6** us |
| CLEAN | 1133 -> 1134 | 232.9 -> **205.1** us | 97.6 -> 97.1 | 207.3 -> **180.6** us |
| RANDCTL | 1133 -> 1133 | 229.4 -> **206.3** us | 95.3 -> 94.8 | 207.5 -> **182.9** us |

The corrected ALL arm now matches E12's `w = 14996 us` arm exactly (1134 frames, 206.6,
93.0, 183.6), which is what two measurements of the same quantity should do. The
contradiction the audits found is resolved, and the resolution went against the first run.

**The flicker conclusion is unchanged.** Excluding phase-locked pixels moves the excess from
183.6 to 180.6 us, a change of 1.6 %, while a matched random exclusion moves it to 182.9 us.
Every number in the paper that came from the first run has been replaced;
`result.json` is kept beside `result_exact.json` so the change is auditable.
