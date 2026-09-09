"""C3 with the correct null. For a pixel with N events at random phase, the
resultant length |sum e^{i phi}| has E[R^2] = N, so the modulation depth R/N has
an expected value of about sqrt(pi/4)/sqrt(N) and R^2/N is Exp(1)-distributed.
Rayleigh test: p = exp(-R^2/N). Report the FRACTION OF PIXELS that are
significantly modulated, not the raw depth, and compare night against day."""
import h5py, hdf5plugin, numpy as np, json
DUR_MS, SUB = 2000, 4
res={}
for seq,tag in (('zurich_city_09_a','NIGHT'),('interlaken_00_c','DAY')):
    f=h5py.File(f'/work/data/dsec/{seq}/events.h5','r'); ev=f['events']; ms2i=f['ms_to_idx'][:]
    i0=int(ms2i[2000]); i1=int(ms2i[2000+DUR_MS])
    t=ev['t'][i0:i1:SUB].astype(np.int64)
    x=ev['x'][i0:i1:SUB].astype(np.int64); y=ev['y'][i0:i1:SUB].astype(np.int64)
    f.close()
    npx=640*480; lin=y*640+x; t0=t[0]
    out={}
    for fHz,label in ((100.0,'100Hz'), (137.0,'137Hz_control')):
        per=1e6/fHz
        ph=((t-t0)%per)/per
        cnt=np.bincount(lin,minlength=npx).astype(np.float64)
        c=np.bincount(lin,weights=np.cos(2*np.pi*ph),minlength=npx)
        s=np.bincount(lin,weights=np.sin(2*np.pi*ph),minlength=npx)
        live=cnt>=100
        R2=(c*c+s*s)[live]; N=cnt[live]
        Z=R2/N                       # Rayleigh statistic, Exp(1) under the null
        p=np.exp(-Z)
        out[label]=dict(live=int(live.sum()),
            frac_p_lt_1e3=round(float((p<1e-3).mean()),4),
            frac_p_lt_1e6=round(float((p<1e-6).mean()),4),
            median_Z=round(float(np.median(Z)),3),      # null median = ln2 = 0.693
            p95_Z=round(float(np.percentile(Z,95)),2))  # null p95 = 3.0
    res[tag]=out
    print(f"{tag} live>=100ev  |  null: median Z=0.693, p95 Z=3.00, frac(p<1e-3)=0.001", flush=True)
    for k,v in out.items():
        print(f"   {k:<16} live={v['live']:>6}  medianZ={v['median_Z']:>7}  p95Z={v['p95_Z']:>8}"
              f"  frac(p<1e-3)={v['frac_p_lt_1e3']:.4f}  frac(p<1e-6)={v['frac_p_lt_1e6']:.4f}", flush=True)
json.dump(res, open('/work/experiments/e10_flicker/rayleigh.json','w'), indent=1); print("WROTE",flush=True)
