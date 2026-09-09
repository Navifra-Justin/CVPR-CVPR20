"""E11 - re-measure the per-object evidence-time dispersion with mains-locked
pixels excluded, against a matched random-exclusion control.

Three arms, identical in every other respect:
  ALL     every pixel                      (reproduces E09's night number)
  CLEAN   pixels with Rayleigh p >= 1e-3 at 100 Hz
  RANDCTL a random pixel subset of the SAME size as CLEAN
The control is what separates "flicker was the effect" from "removing a quarter
of the evidence destroyed the measurement".
"""
import h5py, hdf5plugin, numpy as np, json, sys
SEQ='zurich_city_09_a'; MIN_EV=200; MIN_OBJ=3
rng=np.random.default_rng(0); NPX=640*480

f=h5py.File(f'/work/data/dsec/{SEQ}/events.h5','r'); ev=f['events']; ms2i=f['ms_to_idx'][:]
t_off=int(f['t_offset'][()])
exp=[tuple(int(v) for v in l.split(',')) for l in
     open(f'/work/experiments/e00_exposure_survey/e_{SEQ}.txt') if not l.startswith('#') and l.strip()]

# ---- build the 100 Hz phase-lock mask from a long slice -------------------
print("building mask...", flush=True)
i0=int(ms2i[2000]); i1=int(ms2i[2000+6000])          # 6 s
t=ev['t'][i0:i1:4].astype(np.int64); x=ev['x'][i0:i1:4].astype(np.int64); y=ev['y'][i0:i1:4].astype(np.int64)
lin=y*640+x; t0=t[0]; ph=((t-t0)%10000)/10000.0
cnt=np.bincount(lin,minlength=NPX).astype(np.float64)
c=np.bincount(lin,weights=np.cos(2*np.pi*ph),minlength=NPX)
s=np.bincount(lin,weights=np.sin(2*np.pi*ph),minlength=NPX)
Z=np.zeros(NPX); nz=cnt>0; Z[nz]=(c[nz]**2+s[nz]**2)/cnt[nz]
locked=(cnt>=100)&(np.exp(-Z)<1e-3)
clean=~locked
nlock=int(locked.sum()); print(f"locked pixels {nlock} ({100*nlock/NPX:.2f}% of sensor)", flush=True)
randctl=np.ones(NPX,bool); randctl[rng.choice(NPX,nlock,replace=False)]=False
del t,x,y,lin,ph,c,s,Z,cnt

# ---- labels ---------------------------------------------------------------
tr=np.load(f'/work/data/dsec_det/train/train/{SEQ}/object_detections/left/tracks.npy')
by_t={}
for r in tr: by_t.setdefault(int(r['t']),[]).append(r)

def run(mask,name):
    per_frame=[]
    for a,b in exp:
        mid=(a+b)/2.0; w=b-a
        key=min(by_t, key=lambda k: abs(k-mid)) if by_t else None
        if key is None or abs(key-mid)>26000: continue
        boxes=by_t[key]
        ma=(a-t_off)//1000; mb=(b-t_off)//1000
        if ma<0 or mb>=len(ms2i) or mb<=ma: continue
        mb=mb+1
        if mb>=len(ms2i): continue
        j0,j1=int(ms2i[ma]),int(ms2i[mb])
        if j1-j0<500: continue
        tt=ev['t'][j0:j1].astype(np.int64)+t_off
        xx=ev['x'][j0:j1].astype(np.int64); yy=ev['y'][j0:j1].astype(np.int64)
        ex=(tt>=a)&(tt<b)                      # FIX: restrict to the exposure window exactly
        tt,xx,yy=tt[ex],xx[ex],yy[ex]
        keep=mask[yy*640+xx]
        tt,xx,yy=tt[keep],xx[keep],yy[keep]
        cs=[]
        for r in boxes:
            x0,y0=r['x'],r['y']; x1,y1=x0+r['w'],y0+r['h']
            m=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)
            n=int(m.sum())
            if n<MIN_EV: continue
            cs.append((float(tt[m].mean()-mid), n))
        if len(cs)<MIN_OBJ: continue
        tb=np.array([c[0] for c in cs]); N=np.array([c[1] for c in cs],float)
        per_frame.append((float(tb.std(ddof=1)), float(np.sqrt(np.mean(w*w/(12*N)))), len(cs)))
    A=np.array(per_frame)
    if not len(A): print(name,"no frames"); return None
    sd,null,nob=A[:,0],A[:,1],A[:,2]
    exc=np.sqrt(np.maximum(sd**2-null**2,0))
    d=dict(frames=len(A), median_objects=float(np.median(nob)),
           sd_us=round(float(np.median(sd)),1), sd_p90=round(float(np.percentile(sd,90)),1),
           null_us=round(float(np.median(null)),1),
           excess_us=round(float(np.median(exc)),1),
           frac_frames_sd_gt_null=round(float((sd>null).mean()),4))
    print(f"{name:<8} frames={d['frames']:<5} sd={d['sd_us']:>7} null={d['null_us']:>6} "
          f"excess={d['excess_us']:>7} frac(sd>null)={d['frac_frames_sd_gt_null']}", flush=True)
    return d

out={}
for mask,name in ((np.ones(NPX,bool),'ALL'),(clean,'CLEAN'),(randctl,'RANDCTL')):
    out[name]=run(mask,name)
json.dump(out,open('/work/experiments/e11_flicker_excluded/result_exact.json','w'),indent=1)
print("WROTE",flush=True)
