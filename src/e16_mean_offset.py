"""E16 - the common term, which every previous experiment subtracted away.

E09/E11/E12 measured the DISPERSION of evidence times across the objects of one
frame, after removing that frame's mean. The mean itself was never reported. If the
evidence inside an exposure is systematically biased toward one end of the window,
that common offset is a clock error in its own right, and it does not need to be
compared against a per-object noise floor: it is the same for every object, so it
survives any amount of aggregation.

Three quantities per frame:
  tbar_frame   mean over objects of (evidence-time centroid - mid-exposure)
  tbar_global  the same for ALL events in the window, objects or not
  and, for scale, the exposure half-width w/2.
"""
import h5py, hdf5plugin, numpy as np, json
MIN_EV=200
out={}
for SEQ,tag in (('zurich_city_09_a','night_14996us'),('interlaken_00_c','day_1478us')):
    f=h5py.File(f'/work/data/dsec/{SEQ}/events.h5','r'); ev=f['events']; ms2i=f['ms_to_idx'][:]
    t_off=int(f['t_offset'][()])
    exp=[tuple(int(v) for v in l.split(',')) for l in
         open(f'/work/experiments/e00_exposure_survey/e_{SEQ}.txt') if not l.startswith('#') and l.strip()]
    split='train' if SEQ.startswith('zurich_city_09') else None
    import os
    cand=[f'/work/data/dsec_det/train/train/{SEQ}/object_detections/left/tracks.npy',
          f'/work/data/dsec_det/test/test/{SEQ}/object_detections/left/tracks.npy']
    tr=None
    for c in cand:
        if os.path.exists(c): tr=np.load(c); break
    by_t={}
    if tr is not None:
        for r in tr: by_t.setdefault(int(r['t']),[]).append(r)
    fo=[]; go=[]; ws=[]
    for a,b in exp:
        mid=(a+b)/2.0; w=b-a
        ma=(a-t_off)//1000; mb=(b-t_off)//1000+1
        if ma<0 or mb>=len(ms2i) or mb<=ma: continue
        j0,j1=int(ms2i[ma]),int(ms2i[mb])
        if j1-j0<500: continue
        tt=ev['t'][j0:j1].astype(np.int64)+t_off
        xx=ev['x'][j0:j1].astype(np.int64); yy=ev['y'][j0:j1].astype(np.int64)
        k=(tt>=a)&(tt<b); tt,xx,yy=tt[k],xx[k],yy[k]
        if len(tt)<1000: continue
        go.append(float(tt.mean()-mid)); ws.append(w)
        if by_t:
            key=min(by_t,key=lambda z:abs(z-mid))
            if abs(key-mid)<=26000:
                cs=[]
                for r in by_t[key]:
                    x0,y0=r['x'],r['y']; x1,y1=x0+r['w'],y0+r['h']
                    m=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)
                    if int(m.sum())>=MIN_EV: cs.append(float(tt[m].mean()-mid))
                if len(cs)>=3: fo.append(float(np.mean(cs)))
    G=np.array(go); F=np.array(fo); W=np.array(ws,float)
    d=dict(seq=SEQ, frames=len(G), w_med=float(np.median(W)),
           global_offset_med_us=round(float(np.median(G)),1),
           global_offset_mean_us=round(float(G.mean()),1),
           global_offset_sd_us=round(float(G.std(ddof=1)),1),
           global_offset_frac_of_halfwidth=round(float(np.median(G)/(np.median(W)/2)),4),
           obj_offset_med_us=round(float(np.median(F)),1) if len(F) else None,
           obj_offset_sd_us=round(float(F.std(ddof=1)),1) if len(F)>1 else None,
           n_obj_frames=len(F))
    out[tag]=d
    print(f"{tag}: frames={d['frames']} w={d['w_med']:.0f}us")
    print(f"   ALL events   : median offset {d['global_offset_med_us']:+.1f} us"
          f"  mean {d['global_offset_mean_us']:+.1f}  sd {d['global_offset_sd_us']:.1f}"
          f"  = {100*d['global_offset_frac_of_halfwidth']:+.2f}% of the half-width")
    if d['obj_offset_med_us'] is not None:
        print(f"   labelled objs: median frame-mean offset {d['obj_offset_med_us']:+.1f} us"
              f"  sd across frames {d['obj_offset_sd_us']:.1f}  (n={d['n_obj_frames']})", flush=True)
json.dump(out,open('/work/experiments/e16_mean_offset/result.json','w'),indent=1)
print("WROTE",flush=True)
