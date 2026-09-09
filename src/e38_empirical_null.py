"""E38 - the per-box Rayleigh null, measured instead of assumed.

E10 and E25 test each labelled box for phase locking with Z = N|C|^2 and read the p-value
from the Exp(1) distribution that Z follows when the phases are independent and uniform.
Event times inside one box during a 15 ms exposure are not independent: events arrive in
bursts, so the effective sample size is below the raw count and Z is inflated at every
frequency. The paper's own 137 Hz control shows it - the per-box median there is 4.01
against an analytic 0.693 - and a checklist audit was right that the reported locked
fractions are then computed against a null the data rejects.

The contrast between 100 Hz and the off-frequency arm does not depend on the null, and it
is 114.58 against 4.01. What does depend on it is the absolute statement "99 to 100 % of
boxes are locked at p < 1e-3". This replaces the analytic null with an empirical one:
sweep many off-frequencies that carry no mains harmonic, pool the per-box Z values, and
read the 100 Hz locked fraction against that pooled distribution.

Frequencies are chosen away from 100 Hz and its harmonics and away from the 20 Hz label
rate and its harmonics, and the sweep is wide enough that no single choice carries the
result.
"""
import h5py, hdf5plugin, numpy as np, json, os
SEQS=['zurich_city_00_a','zurich_city_01_a','zurich_city_02_a',
      'zurich_city_03_a','zurich_city_09_a','zurich_city_10_a']
MIN_EV=400
LINE=100.0
# off-frequencies: avoid multiples of 20 (label rate) and of 50 (mains and harmonics)
OFF=[f for f in np.arange(63.0,190.0,7.0)
     if min(abs(f-50*k) for k in range(1,5))>6 and min(abs(f-20*k) for k in range(1,10))>4]
print(f"off-frequencies ({len(OFF)}): "+", ".join(f"{f:.0f}" for f in OFF))
out={}
Zline_all=[]; Zoff_all=[]
for SEQ in SEQS:
    f=h5py.File(f'/work/data/dsec/{SEQ}/events.h5','r'); ev=f['events']; ms2i=f['ms_to_idx'][:]
    t_off=int(f['t_offset'][()])
    exp=[tuple(int(v) for v in l.split(',')) for l in
         open(f'/work/experiments/e00_exposure_survey/e_{SEQ}.txt')
         if not l.startswith('#') and l.strip()]
    tr=np.load(f'/work/data/dsec_det/train/train/{SEQ}/object_detections/left/tracks.npy')
    by_t={}
    for r in tr: by_t.setdefault(int(r['t']),[]).append(r)
    Zl=[]; Zo=[]
    for a,b in exp:
        mid=(a+b)/2.0
        if not by_t: continue
        key=min(by_t,key=lambda z:abs(z-mid))
        if abs(key-mid)>26000: continue
        ma=(a-t_off)//1000; mb=(b-t_off)//1000+1
        if ma<0 or mb>=len(ms2i) or mb<=ma: continue
        j0,j1=int(ms2i[ma]),int(ms2i[mb])
        if j1-j0<500: continue
        tt=ev['t'][j0:j1].astype(np.int64)+t_off
        xx=ev['x'][j0:j1].astype(np.int64); yy=ev['y'][j0:j1].astype(np.int64)
        k=(tt>=a)&(tt<b); tt,xx,yy=tt[k],xx[k],yy[k]
        for r in by_t[key]:
            x0,y0=int(r['x']),int(r['y']); x1,y1=x0+int(r['w']),y0+int(r['h'])
            m=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1); n=int(m.sum())
            if n<MIN_EV: continue
            ts=(tt[m]-mid)*1e-6
            Zl.append(n*abs(np.exp(-2j*np.pi*LINE*ts).mean())**2)
            for fo in OFF:
                Zo.append(n*abs(np.exp(-2j*np.pi*fo*ts).mean())**2)
    Zl=np.array(Zl); Zo=np.array(Zo)
    if not len(Zl): continue
    Zline_all.append(Zl); Zoff_all.append(Zo)
    thr=np.percentile(Zo,99.9)
    out[SEQ]=dict(n_boxes=int(len(Zl)),z_line_med=float(np.median(Zl)),
                  z_off_med=float(np.median(Zo)),
                  emp_thr_999=float(thr),
                  frac_above_emp=float(np.mean(Zl>=thr)),
                  frac_above_analytic=float(np.mean(Zl>=6.908)))
    print(f"  {SEQ:<20} boxes {len(Zl):5d}  Z100 med {np.median(Zl):8.2f}  "
          f"Zoff med {np.median(Zo):6.2f}  empirical p<1e-3 cut {thr:7.2f}  "
          f"locked {100*np.mean(Zl>=thr):6.2f} % (analytic {100*np.mean(Zl>=6.908):6.2f} %)")
Zl=np.concatenate(Zline_all); Zo=np.concatenate(Zoff_all)
thr=np.percentile(Zo,99.9)
print(f"\npooled over all six sequences")
print(f"  off-frequency Z: median {np.median(Zo):.3f}, p99 {np.percentile(Zo,99):.2f}, "
      f"p99.9 {thr:.2f}   (Exp(1) gives 0.693, 4.61, 6.91)")
print(f"  the empirical null is inflated over Exp(1) by a factor of "
      f"{np.median(Zo)/0.6931:.2f} at the median")
print(f"  100 Hz Z: median {np.median(Zl):.2f}")
print(f"  boxes above the EMPIRICAL 1e-3 cut: {100*np.mean(Zl>=thr):.2f} %")
print(f"  boxes above the ANALYTIC  1e-3 cut: {100*np.mean(Zl>=6.908):.2f} %")
print(f"  ratio of medians, 100 Hz to off-frequency: {np.median(Zl)/np.median(Zo):.1f}x")
out['pooled']=dict(off_med=float(np.median(Zo)),off_p999=float(thr),
                   line_med=float(np.median(Zl)),
                   frac_emp=float(np.mean(Zl>=thr)),
                   frac_analytic=float(np.mean(Zl>=6.908)),
                   inflation=float(np.median(Zo)/0.6931),
                   ratio=float(np.median(Zl)/np.median(Zo)),
                   n_off_freqs=len(OFF),off_freqs=[float(v) for v in OFF])
os.makedirs('/work/experiments/e38_empirical_null',exist_ok=True)
json.dump(out,open('/work/experiments/e38_empirical_null/result.json','w'),indent=1)
print("WROTE")
