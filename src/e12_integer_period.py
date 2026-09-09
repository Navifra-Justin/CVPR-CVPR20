"""E12 - the decisive flicker test: integer-period windows.

Mains flicker is exactly periodic at 10000 us. Integrated over an INTEGER number
of flicker periods its net contribution to a time centroid is zero, whatever its
amplitude or phase. So: recompute the per-object evidence-time dispersion inside
windows of exactly one flicker period, and compare against non-integer windows of
similar width. If the excess survives at w = 10000 us, flicker cannot be producing it.

  w = 10000 us  -> exactly 1.0 flicker periods : flicker cancels
  w = 14996 us  -> 1.4996 periods              : flicker maximally uncancelled
  w =  5000 us  -> 0.5 periods                 : flicker maximally uncancelled, narrower
  w = 20000 us  -> exactly 2.0 periods         : flicker cancels, widest
All windows are centred on the same mid-exposure instant, so the scene content is
the same and only the flicker cancellation differs.
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

def run(W):
    rows=[]
    for a,b in exp:
        mid=(a+b)/2.0
        lo,hi=mid-W/2.0, mid+W/2.0
        key=min(by_t, key=lambda k: abs(k-mid))
        if abs(key-mid)>26000: continue
        ma=int((lo-t_off)//1000); mb=int((hi-t_off)//1000)+1
        if ma<0 or mb>=len(ms2i) or mb<=ma: continue
        j0,j1=int(ms2i[ma]),int(ms2i[mb])
        if j1-j0<500: continue
        tt=ev['t'][j0:j1].astype(np.int64)+t_off
        xx=ev['x'][j0:j1].astype(np.int64); yy=ev['y'][j0:j1].astype(np.int64)
        k=(tt>=lo)&(tt<hi); tt,xx,yy=tt[k],xx[k],yy[k]
        cs=[]
        for r in by_t[key]:
            x0,y0=r['x'],r['y']; x1,y1=x0+r['w'],y0+r['h']
            m=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1); n=int(m.sum())
            if n<MIN_EV: continue
            cs.append((float(tt[m].mean()-mid), n))
        if len(cs)<MIN_OBJ: continue
        tb=np.array([c[0] for c in cs]); N=np.array([c[1] for c in cs],float)
        rows.append((tb.std(ddof=1), np.sqrt(np.mean(W*W/(12*N))), len(cs)))
    A=np.array(rows)
    if not len(A): return None
    sd,null=A[:,0],A[:,1]
    exc=np.sqrt(np.maximum(sd**2-null**2,0))
    # report the excess as a RATIO to the null so widths are comparable
    d=dict(W_us=W, periods=round(W/10000.0,4), frames=len(A),
           sd_us=round(float(np.median(sd)),1), null_us=round(float(np.median(null)),1),
           excess_us=round(float(np.median(exc)),1),
           excess_over_null=round(float(np.median(exc)/np.median(null)),3),
           frac_sd_gt_null=round(float((sd>null).mean()),4))
    print(f"W={W:>6}us ({d['periods']:>6} periods) frames={d['frames']:<5} "
          f"sd={d['sd_us']:>7} null={d['null_us']:>6} excess={d['excess_us']:>7} "
          f"excess/null={d['excess_over_null']:>6} frac={d['frac_sd_gt_null']}", flush=True)
    return d

out={}
for W in (5000, 10000, 14996, 20000):
    r=run(W)
    if r: out[str(W)]=r
json.dump(out,open('/work/experiments/e12_integer_period/result.json','w'),indent=1)
print("WROTE",flush=True)
