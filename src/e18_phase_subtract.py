"""E18 - the correct flicker control: subtract each box's OWN predicted contribution.

E12's integer-period argument is retracted: an integer window cancels a periodic
source's zeroth moment but not its first. The centroid contribution of
lambda(t) = lambda_0 (1 + m cos(w t + phi)) over a symmetric integer-period window is
    delta = -(m sin phi) / w.
That quantity is directly observable per box, with no fitting. Writing
    C = (1/N) sum_k exp(-i w t_k)   over the box's events, t_k centred on mid-exposure,
we have C ~= (m/2) exp(i phi), so Im(C) = (m/2) sin phi and
    delta = -2 Im(C) / w.
Subtract delta from each box's measured centroid and re-measure the within-frame
dispersion. If the excess survives, flicker is excluded properly this time.

Arms:
  RAW        measured centroids, as before
  PHASESUB   centroids with each box's own predicted flicker contribution removed
  SHAMSUB    the same subtraction computed at an off-frequency (137 Hz) control,
             which should remove nothing and is the guard against the subtraction
             itself destroying the signal
"""
import h5py, hdf5plugin, numpy as np, json
SEQ='zurich_city_09_a'; MIN_EV=200; MIN_OBJ=3
W_MAINS=2*np.pi*100.0; W_CTRL=2*np.pi*137.0
f=h5py.File(f'/work/data/dsec/{SEQ}/events.h5','r'); ev=f['events']; ms2i=f['ms_to_idx'][:]
t_off=int(f['t_offset'][()])
exp=[tuple(int(v) for v in l.split(',')) for l in
     open(f'/work/experiments/e00_exposure_survey/e_{SEQ}.txt') if not l.startswith('#') and l.strip()]
tr=np.load(f'/work/data/dsec_det/train/train/{SEQ}/object_detections/left/tracks.npy')
by_t={}
for r in tr: by_t.setdefault(int(r['t']),[]).append(r)

rows=[]; mods=[]
for a,b in exp:
    mid=(a+b)/2.0; w=b-a
    key=min(by_t,key=lambda z:abs(z-mid))
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
        m=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1); n=int(m.sum())
        if n<MIN_EV: continue
        ts=(tt[m]-mid)*1e-6                       # seconds, centred on mid-exposure
        raw=float(ts.mean())
        C1=np.exp(-1j*W_MAINS*ts).mean(); C2=np.exp(-1j*W_CTRL*ts).mean()
        d1=-2.0*float(C1.imag)/W_MAINS            # predicted flicker centroid contribution
        d2=-2.0*float(C2.imag)/W_CTRL             # off-frequency sham
        cs.append((raw, raw-d1, raw-d2, n))
        mods.append(2*abs(C1))
    if len(cs)<MIN_OBJ: continue
    A=np.array([[c[0],c[1],c[2]] for c in cs]); N=np.array([c[3] for c in cs],float)
    null=np.sqrt(np.mean((w*1e-6)**2/(12*N)))
    rows.append([A[:,0].std(ddof=1),A[:,1].std(ddof=1),A[:,2].std(ddof=1),null,len(cs)])
R=np.array(rows); us=1e6
print(f"frames {len(R)}   median modulation depth of boxes at 100 Hz: {np.median(mods):.4f}")
names=['RAW','PHASESUB (100 Hz removed)','SHAMSUB (137 Hz removed)']
out={}
for i,nm in enumerate(names):
    sd=R[:,i]*us; null=R[:,3]*us
    exc=np.sqrt(np.maximum(sd**2-null**2,0))
    out[nm]=dict(sd=round(float(np.median(sd)),1),null=round(float(np.median(null)),1),
                 excess=round(float(np.median(exc)),1),frac=round(float((sd>null).mean()),4))
    print(f"  {nm:<28} sd={out[nm]['sd']:>7} null={out[nm]['null']:>6} "
          f"excess={out[nm]['excess']:>7} frac(sd>null)={out[nm]['frac']}")
json.dump(dict(frames=len(R),median_modulation=float(np.median(mods)),arms=out),
          open('/work/experiments/e18_phase_subtract/result.json','w'),indent=1)
print("WROTE")
