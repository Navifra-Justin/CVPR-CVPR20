"""Is the night intra-exposure event stream driven by AC flicker or low-light noise?

DSEC's own paper attributes high night event rates near street lamps to flashing lights, and
Graca & Delbruck show DVS noise rises in dim light.  Both would corrupt E08.  Three checks:

 1. PERIODICITY.  Mains flicker is 100 Hz (2x 50 Hz) -> a 10 ms period inside a 14996 us
    exposure.  Histogram event times within each exposure and look for power at 100/120 Hz.
 2. POLARITY BALANCE.  Flicker drives strongly ON/OFF-alternating bursts; shot noise is
    balanced but unstructured; edge motion is balanced with spatial structure.
 3. SPATIAL CLUSTERING.  Noise is spatially unstructured (isolated pixels); motion and
    flicker are clustered.
"""
import h5py, hdf5plugin, numpy as np, sys, json
seq = sys.argv[1]
f = h5py.File(f'/work/data/dsec/{seq}/events.h5', 'r')
t_off = int(f['t_offset'][()]); ms2i = f['ms_to_idx'][:]; ev = f['events']
exp = np.array([[int(x) for x in l.split(',')] for l in
                open(f'/work/experiments/e00_exposure_survey/e_{seq}.txt')
                if not l.startswith('#') and l.strip()], dtype=np.int64)
def idx(t):
    ms = (t - t_off)//1000
    return int(ms2i[ms]) if 0 <= ms < len(ms2i) else None
NB = 60                      # bins over the exposure -> 250 us at 15 ms
acc = np.zeros(NB); pol = []; clus = []; peaks = []
n = 0
for k in range(0, len(exp), 7):
    a, b = int(exp[k,0]), int(exp[k,1]); w = b - a
    i0, i1 = idx(a), idx(b)
    if i0 is None or i1 is None or i1-i0 < 5000: continue
    t = ev['t'][i0:i1].astype(np.int64) + t_off
    p = ev['p'][i0:i1]; x = ev['x'][i0:i1].astype(np.int64); y = ev['y'][i0:i1].astype(np.int64)
    h, _ = np.histogram(t, bins=NB, range=(a, b))
    h = h / max(h.mean(), 1e-9)
    acc += h
    # power spectrum of the within-exposure time histogram
    H = np.abs(np.fft.rfft(h - h.mean()))
    fr = np.fft.rfftfreq(NB, d=w/NB/1e6)          # Hz
    if len(H) > 2:
        j = int(np.argmax(H[1:])) + 1
        peaks.append(float(fr[j]))
    pol.append(float((p == 1).mean()))
    # spatial clustering: fraction of events whose pixel fired >=2 times in this exposure
    lin = y*640 + x
    u, c = np.unique(lin, return_counts=True)
    clus.append(float(c[c >= 2].sum() / len(lin)))
    n += 1
    if n >= 200: break
acc /= n
H = np.abs(np.fft.rfft(acc - acc.mean())); fr = np.fft.rfftfreq(NB, d=14996/NB/1e6)
order = np.argsort(H[1:])[::-1][:5] + 1
out = dict(seq=seq, exposures=n,
           mean_within_exposure_profile=[round(v,4) for v in acc],
           profile_relative_range=float(acc.max()-acc.min()),
           top_frequencies_hz=[round(float(fr[i]),1) for i in order],
           top_power=[round(float(H[i]),3) for i in order],
           power_at_100hz=float(H[np.argmin(np.abs(fr-100))]),
           power_at_120hz=float(H[np.argmin(np.abs(fr-120))]),
           peak_freq_per_exposure_median=float(np.median(peaks)),
           peak_freq_per_exposure_frac_near_100_120=float(np.mean(
               [(abs(v-100) < 10) or (abs(v-120) < 10) for v in peaks])),
           polarity_on_fraction_median=float(np.median(pol)),
           frac_events_on_repeat_pixels_median=float(np.median(clus)))
print(json.dumps(out, indent=1))
