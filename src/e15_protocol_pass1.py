"""12-step protocol, pass 1, step 3: the product of medians is not the median of products.

E14 multiplied the median dispersion by the median object speed. The quantity that
matters is per-object: each object's own deviation from its frame's mean evidence
time, times ITS OWN speed. If deviation and speed are correlated, the honest figure
is larger than E14's.
"""
import h5py, hdf5plugin, numpy as np, json
SEQ='zurich_city_09_a'; MIN_EV=200; MIN_OBJ=3
f=h5py.File(f'/work/data/dsec/{SEQ}/events.h5','r'); ev=f['events']; ms2i=f['ms_to_idx'][:]
t_off=int(f['t_offset'][()])
exp=[tuple(int(v) for v in l.split(',')) for l in
     open(f'/work/experiments/e00_exposure_survey/e_{SEQ}.txt') if not l.startswith('#') and l.strip()]
tr=np.load(f'/work/data/dsec_det/train/train/{SEQ}/object_detections/left/tracks.npy')
by_t={}
for r in tr: by_t.setdefault(int(r['t']),[]).append(r)
# per-track speed from consecutive labels
spd={}
for tid in np.unique(tr['track_id']):
    s=np.sort(tr[tr['track_id']==tid],order='t')
    if len(s)<2: continue
    t=s['t'].astype(np.float64)*1e-6
    cx=s['x']+s['w']/2.0; cy=s['y']+s['h']/2.0
    v=np.hypot(np.diff(cx),np.diff(cy))/np.diff(t)
    for i,tt in enumerate(s['t'][:-1]): spd[(int(tid),int(tt))]=float(v[i])

dev_px=[]; dev_us=[]; spds=[]
for a,b in exp:
    mid=(a+b)/2.0
    key=min(by_t,key=lambda k:abs(k-mid))
    if abs(key-mid)>26000: continue
    ma=(a-t_off)//1000; mb=(b-t_off)//1000+1
    if ma<0 or mb>=len(ms2i) or mb<=ma: continue
    j0,j1=int(ms2i[ma]),int(ms2i[mb])
    if j1-j0<500: continue
    tt=ev['t'][j0:j1].astype(np.int64)+t_off
    xx=ev['x'][j0:j1].astype(np.int64); yy=ev['y'][j0:j1].astype(np.int64)
    k=(tt>=a)&(tt<b); tt,xx,yy=tt[k],xx[k],yy[k]
    cs=[]
    for r in by_t[key]:
        x0,y0=r['x'],r['y']; x1,y1=x0+r['w'],y0+r['h']
        m=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)
        if int(m.sum())<MIN_EV: continue
        v=spd.get((int(r['track_id']),key))
        if v is None: continue
        cs.append((float(tt[m].mean()-mid), v))
    if len(cs)<MIN_OBJ: continue
    tb=np.array([c[0] for c in cs]); vv=np.array([c[1] for c in cs])
    d=tb-tb.mean()                       # deviation from this frame's common time
    dev_us.append(np.abs(d)); dev_px.append(np.abs(d)*1e-6*vv); spds.append(vv)
D=np.concatenate(dev_us); P=np.concatenate(dev_px); V=np.concatenate(spds)
sc=0.4974
print(f"objects with both an evidence time and a speed: {len(D)}")
print(f"\nSTEP-3 CHECK: product of medians vs per-object product")
print(f"  E14 route  : median|dev| {np.median(D):.1f} us  x  median v {np.median(V):.1f} px/s"
      f"  = {np.median(D)*1e-6*np.median(V):.4f} px")
print(f"  per-object : median {np.median(P):.4f} px | mean {P.mean():.4f} | p90 {np.percentile(P,90):.4f}"
      f" | p99 {np.percentile(P,99):.4f} | max {P.max():.3f}")
print(f"  as a fraction of sigma_c={sc}: median {100*np.median(P)/sc:.2f}%  p90 {100*np.percentile(P,90)/sc:.2f}%"
      f"  p99 {100*np.percentile(P,99)/sc:.2f}%  max {100*P.max()/sc:.1f}%")
r=np.corrcoef(D,V)[0,1]
print(f"\n  correlation between |deviation| and speed: {r:+.4f}")
print(f"  fraction of objects whose displacement exceeds sigma_c : {100*(P>sc).mean():.3f}%")
print(f"  fraction exceeding the 0.1443 px quantization floor    : {100*(P>0.1443).mean():.3f}%")
hi=V>np.percentile(V,90)
print(f"\n  top-decile speed objects: median displacement {np.median(P[hi]):.4f} px"
      f" = {100*np.median(P[hi])/sc:.1f}% of sigma_c")
json.dump(dict(n=int(len(D)),med_px=float(np.median(P)),p90_px=float(np.percentile(P,90)),
               p99_px=float(np.percentile(P,99)),max_px=float(P.max()),corr=float(r),
               frac_gt_sigma=float((P>sc).mean()),frac_gt_quant=float((P>0.1443).mean()),
               top_decile_med_px=float(np.median(P[hi]))),
          open('/work/experiments/e15_protocol/pass1.json','w'),indent=1)
print("WROTE")
