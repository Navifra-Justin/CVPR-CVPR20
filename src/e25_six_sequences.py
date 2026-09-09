"""E25 - do the two surviving night results hold across all six ceiling sequences?

Both audits named "one sequence" as the paper's largest limitation. All six DSEC
train sequences whose exposure is pinned at 14996 us now have events, exposure
metadata and DSEC-Det labels on disk. Reproduce, per sequence:

  (A) E10  the mains signature: per-box modulation m = 2|C| at 100 Hz, and the
           Rayleigh statistic against its analytic Exp(1) null, with an
           off-frequency control at 137 Hz.
  (B) E20  the spatial gradient of evidence time: fit t = a + bx + cy inside each
           box and align grad t with the label-derived velocity. Flicker is
           spatially uniform inside a box and cannot contribute. Two nulls:
           shuffled velocity, and shuffled event times within the box.
"""
import h5py, hdf5plugin, numpy as np, json, os
SEQS=['zurich_city_00_a','zurich_city_01_a','zurich_city_02_a',
      'zurich_city_03_a','zurich_city_09_a','zurich_city_10_a']
MIN_EV=400; W1=2*np.pi*100.0; W2=2*np.pi*137.0
rng=np.random.default_rng(0)
out={}
for SEQ in SEQS:
    f=h5py.File(f'/work/data/dsec/{SEQ}/events.h5','r'); ev=f['events']; ms2i=f['ms_to_idx'][:]
    t_off=int(f['t_offset'][()])
    exp=[tuple(int(v) for v in l.split(',')) for l in
         open(f'/work/experiments/e00_exposure_survey/e_{SEQ}.txt') if not l.startswith('#') and l.strip()]
    tr=np.load(f'/work/data/dsec_det/train/train/{SEQ}/object_detections/left/tracks.npy')
    by_t={}
    for r in tr: by_t.setdefault(int(r['t']),[]).append(r)
    vel={}
    for tid in np.unique(tr['track_id']):
        s=np.sort(tr[tr['track_id']==tid],order='t')
        if len(s)<2: continue
        t=s['t'].astype(float)*1e-6; cx=s['x']+s['w']/2.0; cy=s['y']+s['h']/2.0
        for i in range(len(s)-1):
            dt=t[i+1]-t[i]
            if dt>0: vel[(int(tid),int(s['t'][i]))]=((cx[i+1]-cx[i])/dt,(cy[i+1]-cy[i])/dt)
    mods=[]; Z1=[]; Z2=[]; cosm=[]; cosn=[]; cost=[]
    for a,b in exp:
        mid=(a+b)/2.0
        key=min(by_t,key=lambda z:abs(z-mid)) if by_t else None
        if key is None or abs(key-mid)>26000: continue
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
            C1=np.exp(-1j*W1*ts).mean(); C2=np.exp(-1j*W2*ts).mean()
            mods.append(2*abs(C1)); Z1.append(n*abs(C1)**2); Z2.append(n*abs(C2)**2)
            vv=vel.get((int(r['track_id']),key))
            if vv is None: continue
            spd=float(np.hypot(*vv))
            if spd<5: continue
            X=xx[m].astype(float); Y=yy[m].astype(float); T=ts
            A=np.column_stack([np.ones_like(X),X-X.mean(),Y-Y.mean()])
            co,*_=np.linalg.lstsq(A,T,rcond=None); gx,gy=co[1],co[2]
            g=np.hypot(gx,gy)
            if g<1e-12: continue
            u=(vv[0]/spd,vv[1]/spd)
            cosm.append((gx*u[0]+gy*u[1])/g)
            th=rng.uniform(0,2*np.pi); cosn.append((gx*np.cos(th)+gy*np.sin(th))/g)
            Ts=rng.permutation(T)
            cs,*_=np.linalg.lstsq(A,Ts,rcond=None); sx,sy=cs[1],cs[2]; s2=np.hypot(sx,sy)
            if s2>1e-12: cost.append((sx*u[0]+sy*u[1])/s2)
    f.close()
    M=np.array(mods); z1=np.array(Z1); z2=np.array(Z2)
    cm=np.array(cosm); cn=np.array(cosn); ct=np.array(cost)
    se=1/np.sqrt(max(len(cm),1))
    d=dict(boxes=int(len(M)),
           mod_p10=round(float(np.percentile(M,10)),3),mod_med=round(float(np.median(M)),3),
           Z100_med=round(float(np.median(z1)),3),Z137_med=round(float(np.median(z2)),3),
           frac_p1e3=round(float((np.exp(-z1)<1e-3).mean()),4),
           n_grad=int(len(cm)),cos_mean=round(float(cm.mean()),4),
           cos_null_rot=round(float(cn.mean()),4),cos_null_time=round(float(ct.mean()),4) if len(ct) else None,
           se=round(float(se),4),sigma=round(float(abs(cm.mean())/se),2))
    out[SEQ]=d
    print(f"{SEQ:<20} boxes={d['boxes']:>5} mod_med={d['mod_med']:.3f} Z100={d['Z100_med']:6.2f} "
          f"Z137={d['Z137_med']:5.2f} lock={d['frac_p1e3']:.3f} | grad n={d['n_grad']:>5} "
          f"cos={d['cos_mean']:+.4f} rot={d['cos_null_rot']:+.4f} time={d['cos_null_time']} {d['sigma']:.1f}SE",flush=True)
allc=[out[s]['cos_mean'] for s in out]; alln=[out[s]['n_grad'] for s in out]
w=np.array(alln,float); w/=w.sum()
print(f"\nPOOLED across {len(out)} sequences: weighted mean cos = {float(np.dot(w,allc)):+.4f}")
print(f"  sequences with cos > 0: {sum(1 for c in allc if c>0)}/{len(allc)}")
print(f"  median 100 Hz Rayleigh Z across sequences: {np.median([out[s]['Z100_med'] for s in out]):.2f} (null 0.693)")
print(f"  median 137 Hz control Z: {np.median([out[s]['Z137_med'] for s in out]):.2f}")
os.makedirs('/work/experiments/e25_six_sequences',exist_ok=True)
json.dump(out,open('/work/experiments/e25_six_sequences/result.json','w'),indent=1)
print("WROTE")
