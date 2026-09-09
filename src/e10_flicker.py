"""E10 - is the night event stream driven by mains flicker?
DSEC's own paper attributes the high night event rate to streetlight flicker.
If true, the per-object dispersion measured inside night exposures is an artifact.
Test: power spectrum of the global event rate, day vs night, on the SAME pipeline.
Mains in Switzerland is 50 Hz, so lamp intensity flickers at 100 Hz (and 120 Hz for
60 Hz regions). Look for line power at 100/120 Hz above the local continuum."""
import h5py, hdf5plugin, numpy as np, sys, json

def rate_series(seq, bin_us=500, dur_s=20.0):
    f = h5py.File(f'/work/data/dsec/{seq}/events.h5', 'r')
    ev, ms2i = f['events'], f['ms_to_idx'][:]
    i0 = int(ms2i[2000]); i1 = int(ms2i[min(2000 + int(dur_s*1000), len(ms2i)-1)])
    t = ev['t'][i0:i1].astype(np.int64)
    x = ev['x'][i0:i1].astype(np.int64); y = ev['y'][i0:i1].astype(np.int64)
    t0 = t[0]; nb = int((t[-1]-t0)//bin_us)+1
    r = np.bincount((t-t0)//bin_us, minlength=nb).astype(np.float64)
    return r, bin_us, x, y, len(t)

def spectrum(r, bin_us):
    r = r - r.mean()
    w = np.hanning(len(r))
    P = np.abs(np.fft.rfft(r*w))**2
    fr = np.fft.rfftfreq(len(r), d=bin_us*1e-6)
    return fr, P

def line_ratio(fr, P, f0, halfwidth=2.0, cont=(8.0, 30.0)):
    """power in [f0-hw, f0+hw] divided by the median continuum in a surrounding band"""
    m = (fr > f0-halfwidth) & (fr < f0+halfwidth)
    c = ((fr > f0-cont[1]) & (fr < f0-cont[0])) | ((fr > f0+cont[0]) & (fr < f0+cont[1]))
    return float(P[m].max()/np.median(P[c])) if m.any() and c.any() else float('nan')

out = {}
for seq, tag in (('zurich_city_09_a','night_14996us'), ('interlaken_00_c','day_1478us')):
    r, bu, x, y, n = rate_series(seq)
    fr, P = spectrum(r, bu)
    peak_i = np.argmax(P[(fr>20)&(fr<900)]); sub = fr[(fr>20)&(fr<900)]
    # spatial concentration: fraction of events in the top 1% of pixels
    lin = y*640+x
    cnt = np.bincount(lin, minlength=640*480)
    srt = np.sort(cnt)[::-1]
    top1 = float(srt[:int(0.01*640*480)].sum()/cnt.sum())
    out[tag] = dict(seq=seq, events=int(n),
        line_ratio_100Hz=round(line_ratio(fr,P,100.0),3),
        line_ratio_120Hz=round(line_ratio(fr,P,120.0),3),
        line_ratio_50Hz=round(line_ratio(fr,P,50.0),3),
        strongest_peak_Hz=round(float(sub[peak_i]),1),
        frac_events_in_top1pct_pixels=round(top1,4))
    print(tag, json.dumps(out[tag]))
json.dump(out, open('/work/experiments/e10_flicker/result.json','w'), indent=1)
