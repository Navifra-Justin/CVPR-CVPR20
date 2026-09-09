"""E39 - is the line at 100 Hz or at 200 Hz? Measured, not eyeballed.

Rendering one exposure window as a video made the event rate visible, and its humps looked
about 5 ms apart, which is 200 Hz rather than the 100 Hz the paper claims. That is not a
contradiction on its face: an event camera responds to log-intensity CHANGE, so a lamp
whose intensity oscillates at 100 Hz drives events on both the rising and the falling edge
and can produce a rate at 200 Hz. It matters anyway, because the paper names the frequency
and the per-box statistic is evaluated at it.

Three measurements settle it:
  1. the rate spectrum of the one frame the video shows, 20-400 Hz;
  2. the same over the whole ceiling sequence, which resolves finely;
  3. the same split by event polarity, since a rectified drive puts ON events on one edge
     and OFF events on the other, which is what would move power between 100 and 200 Hz.
"""
import h5py, hdf5plugin, numpy as np, json, os
SEQ=os.environ.get('SEQ','zurich_city_09_a')
f=h5py.File(f'/work/data/dsec/{SEQ}/events.h5','r'); ev=f['events']; ms2i=f['ms_to_idx'][:]
t_off=int(f['t_offset'][()])
exp=[tuple(int(v) for v in l.split(',')) for l in
     open(f'/work/experiments/e00_exposure_survey/e_{SEQ}.txt')
     if not l.startswith('#') and l.strip()]
F=np.arange(20.0,400.1,0.25)

def spec(ts, pol=None):
    """N|C(f)|^2 over the given event times, in seconds."""
    if pol is not None: ts=ts[pol]
    if len(ts)<50: return np.zeros_like(F)
    return len(ts)*np.abs(np.exp(-2j*np.pi*np.outer(F,ts)).mean(axis=1))**2

# --- 1. the frame the video shows: the median-dispersion frame with >= 6 boxes
tr=np.load(f'/work/data/dsec_det/train/train/{SEQ}/object_detections/left/tracks.npy')
by_t={}
for r in tr: by_t.setdefault(int(r['t']),[]).append(r)
best=None; cands=[]
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
    pp=ev['p'][j0:j1].astype(np.int64)
    k=(tt>=a)&(tt<b); tt,xx,yy,pp=tt[k],xx[k],yy[k],pp[k]
    n=0; tb=[]
    for r in by_t[key]:
        x0,y0=int(r['x']),int(r['y']); x1,y1=x0+int(r['w']),y0+int(r['h'])
        m=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)
        if int(m.sum())>=200: n+=1; tb.append(float(tt[m].mean()-mid))
    if n>=6: cands.append((np.std(tb,ddof=1),a,b,tt,pp))
cands.sort(key=lambda z:z[0])
sd,a,b,tt,pp=cands[len(cands)//2]
ts=(tt-a)*1e-6
S1=spec(ts)
print(f"1) the frame the clip shows: {len(ts)} events over {(b-a)} us")
for lab,arr in [("all",S1),("ON",spec(ts,pp==1)),("OFF",spec(ts,pp==0))]:
    i=int(np.argmax(arr))
    p100=arr[int(np.argmin(abs(F-100)))]; p200=arr[int(np.argmin(abs(F-200)))]
    print(f"   {lab:<4} peak {F[i]:6.1f} Hz   Z(100)={p100:9.1f}  Z(200)={p200:9.1f}  "
          f"ratio 200/100 = {p200/max(p100,1e-9):6.2f}")

# --- 2. the whole sequence, which resolves finely. Subsample to keep the sum tractable.
rng=np.random.default_rng(0)
N=ev['t'].shape[0]
idx=np.sort(rng.choice(N,size=min(400000,N),replace=False))
tt2=ev['t'][:][idx].astype(np.int64)*1e-6
pp2=ev['p'][:][idx].astype(np.int64)
tt2=tt2-tt2[0]
print(f"\n2) the whole sequence, {len(tt2)} events subsampled from {N}")
for lab,sel in [("all",slice(None)),("ON",pp2==1),("OFF",pp2==0)]:
    t=tt2[sel] if not isinstance(sel,slice) else tt2
    A=len(t)*np.abs(np.exp(-2j*np.pi*np.outer(F,t)).mean(axis=1))**2
    i=int(np.argmax(A))
    p100=A[int(np.argmin(abs(F-100)))]; p200=A[int(np.argmin(abs(F-200)))]
    print(f"   {lab:<4} peak {F[i]:7.2f} Hz   Z(100)={p100:11.1f}  Z(200)={p200:11.1f}  "
          f"ratio 200/100 = {p200/max(p100,1e-9):7.3f}")
    if lab=="all":
        k=np.argsort(-A)[:400]
        tops=sorted(set(np.round(F[k]).astype(int)))
        print(f"        strongest frequencies: {tops[:12]}")
        json.dump(dict(freq=[float(v) for v in F],power=[float(v) for v in A]),
                  open('/work/experiments/e39_which_frequency/sequence_spectrum.json','w'))
print("\nWROTE")
