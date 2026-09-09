"""C3 (decisive): is the 100 Hz modulation confined to a few pixels, or does it
modulate the whole image? If confined, a spatial mask defends the night result.
If spread, per-object event-time centroids are explained by flicker phase."""
import h5py, hdf5plugin, numpy as np, json
DUR_MS, SUB = 1000, 8
res={}
for seq,tag in (('zurich_city_09_a','NIGHT'),('interlaken_00_c','DAY')):
    f=h5py.File(f'/work/data/dsec/{seq}/events.h5','r'); ev=f['events']; ms2i=f['ms_to_idx'][:]
    i0=int(ms2i[2000]); i1=int(ms2i[2000+DUR_MS])
    t=ev['t'][i0:i1:SUB].astype(np.int64)
    x=ev['x'][i0:i1:SUB].astype(np.int64); y=ev['y'][i0:i1:SUB].astype(np.int64)
    f.close()
    npx=640*480; lin=y*640+x; t0=t[0]
    ph=((t-t0)%10000)/10000.0
    cnt=np.bincount(lin,minlength=npx).astype(np.float32)
    c=np.bincount(lin,weights=np.cos(2*np.pi*ph).astype(np.float32),minlength=npx)
    s=np.bincount(lin,weights=np.sin(2*np.pi*ph).astype(np.float32),minlength=npx)
    amp=np.hypot(c,s); live=cnt>=30
    mod=amp[live]/cnt[live]
    pw=amp**2
    o=np.sort(pw)[::-1]; oc=np.sort(cnt)[::-1]
    d=dict(events=int(len(t)), live_pixels=int(live.sum()), live_frac=round(float(live.mean()),4),
           mod_median=round(float(np.median(mod)),4), mod_p90=round(float(np.percentile(mod,90)),4),
           mod_p99=round(float(np.percentile(mod,99)),4))
    print(f"{tag}: {len(t)/1e6:.1f}M ev  live {int(live.sum())} px ({100*live.mean():.1f}%)"
          f"  modulation median {d['mod_median']} p90 {d['mod_p90']} p99 {d['mod_p99']}", flush=True)
    for frac in (0.001,0.01,0.05,0.20):
        k=int(frac*npx); a=100*o[:k].sum()/pw.sum(); b=100*oc[:k].sum()/cnt.sum()
        print(f"   top {frac*100:>5.1f}% px: {a:5.1f}% of 100Hz power | {b:5.1f}% of events", flush=True)
        d[f'pow_{frac}']=round(float(a),1); d[f'ev_{frac}']=round(float(b),1)
    res[tag]=d
json.dump(res, open('/work/experiments/e10_flicker/spatial.json','w'), indent=1); print("WROTE",flush=True)
