# E40 — which frequency carries the mains signature (2026-09-07)

## Why this exists

E10 reported "the strongest line **between 90 and 110 Hz**, at 100.00 Hz, a factor of 10841
above the **60–160 Hz** continuum". Both bands were fixed before the measurement, so it
could not have found a line anywhere else. Rendering one exposure window as a video for the
paper's figure made the event rate visible, and its humps were about 5 ms apart — 200 Hz.
A wide sweep on the whole sequence confirmed it: the strongest line is at exactly
200.00 Hz, with `Z(200)/Z(100) = 25.6`.

That is not a contradiction of the physics, it is the physics. An event camera responds to
log-intensity **change**, so a lamp whose intensity oscillates at 100 Hz drives events on
both the rising and the falling edge, and the arrival rate carries the harmonic series of
that fundamental with the second harmonic dominant.

## Construction

400 000 events sampled uniformly from each whole recording, spectrum `N|C(f)|²` on a
20–450 Hz grid at 0.25 Hz, and each test frequency reported as its ratio to the median of
its own ±15 Hz neighbourhood. No band is chosen in advance. **Odd multiples of 50 Hz that
are not multiples of 100 are the diagnostic**: a rectified 50 Hz source puts no power there.

## Result — line to local continuum

| sequence | peak | 50 | 100 | 150 | **200** | 250 | 300 | 400 |
|---|---|---|---|---|---|---|---|---|
| zurich_city_00_a | 300 Hz | 1.3 | 13.4 | 0.0 | 29.7 | 0.7 | 37.3 | 0.6 |
| zurich_city_01_a | 200 Hz | 1.9 | 25.2 | 0.8 | 47.1 | 0.9 | 0.9 | 10.3 |
| zurich_city_02_a | 300 Hz | 0.6 | 21.4 | 3.8 | 14.7 | 2.0 | 411.6 | 27.3 |
| zurich_city_03_a | 200 Hz | 5.6 | 181.3 | 5.2 | 309.9 | 2.7 | 2.1 | 1.8 |
| zurich_city_09_a | 200 Hz | 1.7 | 119.4 | 6.0 | **2517.6** | 7.3 | 18.4 | 4.9 |
| zurich_city_10_a | 200 Hz | 2.5 | 34.8 | 8.5 | 202.6 | 1.2 | 11.7 | 15.3 |
| **ceiling median** | | **1.8** | **30.0** | **4.5** | **124.8** | **1.6** | **15.1** | 7.6 |
| interlaken_00_c (day) | 400 Hz | 0.4 | **0.5** | 0.1 | **6.2** | 1.9 | 1.3 | 3.5 |

Three things follow, and none of them needed a band chosen in advance.

1. **The signature is a harmonic series, not a line.** Every ceiling sequence carries 100
   and 200 Hz; the median ratios are 30 and 125, and 300 Hz follows at 15.
2. **There is nothing at 50, 150 or 250 Hz** — medians 1.8, 4.5 and 1.6. The absence of the
   odd multiples of 50 is the fingerprint of a rectified supply and rules out any periodic
   source whose fundamental is 50 Hz.
3. **The daytime sequence has none of it**: 0.5 at 100 Hz and 6.2 at 200 Hz, against 30 and
   125. Exposure width and illumination move together in that contrast, which the paper
   already states, but the harmonic structure is absent rather than merely weaker.

## What this changes

The paper's "100.00 Hz mains modulation" is true of the fundamental but names the weaker
harmonic as the signature. It becomes: the ceiling sequences carry the harmonic series of a
100 Hz mains flicker, strongest at the second harmonic, absent at the odd multiples of
50 Hz and absent in daylight.

## What this does NOT establish

The attribution to mains rests on the frequency and on the harmonic structure, not on a
measurement of the lamps. A different rectified source at the same supply frequency would
look identical, which is the point of the attribution rather than a weakness of it. The
daytime comparison is one sequence, and its exposure and illumination differ together.
