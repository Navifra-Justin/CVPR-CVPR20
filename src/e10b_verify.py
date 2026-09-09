import h5py, hdf5plugin, numpy as np, json, sys
DUR_MS = 3000          # 300 flicker cycles at 100 Hz; 0.33 Hz resolution
SUB    = 4             # uniform subsample for the per-pixel part

def load(seq):
    f = h5py.File(f'/work/data/dsec/{seq}/events.h5','r')
    ev, ms2i = f['events'], f['ms_to_idx'][:]
    i0=int(ms2i[2000]); i1=int(ms2i[2000+DUR_MS])
    t = ev['t'][i0:i1].astype(np.int64)
    x = ev['x'][i0:i1:SUB].astype(np.int64); y = ev['y'][i0:i1:SUB].astype(np.int64)
    ts = t[::SUB]
    return t, ts, x, y

res={}
for seq,tag in (('zurich_city_09_a','NIGHT'),('interlaken_00_c','DAY')):
    t, ts, x, y = load(seq); t0=t[0]
    print(f"===== {tag} {seq}  {len(t)/1e6:.1f}M events in {DUR_MS} ms", flush=True)
    d={}
    for bu in (500, 200):
        nb=int((t[-1]-t0)//bu)+1
        r=np.bincount((t-t0)//bu, minlength=nb).astype(float); r-=r.mean()
        P=np.abs(np.fft.rfft(r*np.hanning(len(r))))**2
        fr=np.fft.rfftfreq(len(r), d=bu*1e-6)
        sel=(fr>90)&(fr<110); band=(fr>60)&(fr<160)
        top=np.argsort(P[sel])[::-1][:3]
        lines=", ".join(f"{fr[sel][i]:.2f}Hz" for i in top)
        ratio=float(P[sel].max()/np.median(P[band]))
        print(f"  C1/C2 bin={bu}us top90-110Hz: {lines} | peak/continuum(60-160Hz) = {ratio:.1f}", flush=True)
        d[f'peak_over_continuum_bin{bu}']=round(ratio,1)
        d[f'top_line_Hz_bin{bu}']=round(float(fr[sel][top[0]]),2)
    ph=((ts-t0)%10000)/10000.0
    lin=y*640+x; npx=640*480
    cnt=np.bincount(lin,minlength=npx).astype(float)
    c=np.bincount(lin,weights=np.cos(2*np.pi*ph),minlength=npx)
    s=np.bincount(lin,weights=np.sin(2*np.pi*ph),minlength=npx)
    amp=np.hypot(c,s)
    live=cnt>=50
    mod=np.where(live, amp/np.maximum(cnt,1), np.nan)
    m=mod[live]
    print(f"  C3 live pixels (>=50 ev): {int(live.sum())} = {100*live.mean():.1f}% of sensor", flush=True)
    print(f"     100Hz modulation depth: median {np.nanmedian(m):.4f} p90 {np.nanpercentile(m,90):.4f} p99 {np.nanpercentile(m,99):.4f}", flush=True)
    d.update(live_pixels=int(live.sum()), live_frac=round(float(live.mean()),4),
             mod_median=round(float(np.nanmedian(m)),4),
             mod_p90=round(float(np.nanpercentile(m,90)),4),
             mod_p99=round(float(np.nanpercentile(m,99)),4))
    pw=amp**2; o=np.sort(pw)[::-1]; oc=np.sort(cnt)[::-1]
    for frac in (0.001,0.01,0.05):
        k=int(frac*npx)
        a=100*o[:k].sum()/pw.sum(); b=100*oc[:k].sum()/cnt.sum()
        print(f"     top {frac*100:>5.1f}% pixels: {a:5.1f}% of 100Hz power, {b:5.1f}% of all events", flush=True)
        d[f'pow_top{frac}']=round(float(a),1); d[f'ev_top{frac}']=round(float(b),1)
    res[tag]=d
json.dump(res, open('/work/experiments/e10_flicker/verify.json','w'), indent=1)
print("WROTE", flush=True)
