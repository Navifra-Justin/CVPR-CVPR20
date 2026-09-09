"""E20 - protocol step 10 for the flicker problem: change the dimension.

Mains flicker modulates the event rate in TIME and is spatially uniform inside a box,
so it contributes nothing to the SPATIAL GRADIENT of evidence time within a box.
Real motion does: the leading and trailing parts of a moving object emit their events
at different instants, so t varies linearly across the box along the motion direction.

For each box, fit  t = a + b*x + c*y  over its events inside the exposure.
Predictions if the gradient is motion:
  |grad t| ~ 1/|v|      (units s/px)
  direction of grad t is (anti)parallel to the label-derived velocity
Flicker predicts neither: it predicts |grad t| ~ 0 and a random direction.

Controls:
  - alignment against the label velocity direction, versus a shuffled-velocity null
  - the same fit on a time-shuffled copy of each box (destroys motion, keeps flicker)
"""
import h5py, hdf5plugin, numpy as np, json
SEQ='zurich_city_09_a'; MIN_EV=400; W1=2*np.pi*100.0
rng=np.random.default_rng(0)
f=h5py.File(f'/work/data/dsec/{SEQ}/events.h5','r'); ev=f['events']; ms2i=f['ms_to_idx'][:]
t_off=int(f['t_offset'][()])
exp=[tuple(int(v) for v in l.split(',')) for l in
     open(f'/work/experiments/e00_exposure_survey/e_{SEQ}.txt') if not l.startswith('#') and l.strip()]
tr=np.load(f'/work/data/dsec_det/train/train/{SEQ}/object_detections/left/tracks.npy')
by_t={}
for r in tr: by_t.setdefault(int(r['t']),[]).append(r)
# label velocity per (track, time)
vel={}
for tid in np.unique(tr['track_id']):
    s=np.sort(tr[tr['track_id']==tid],order='t')
    if len(s)<2: continue
    t=s['t'].astype(np.float64)*1e-6
    cx=s['x']+s['w']/2.0; cy=s['y']+s['h']/2.0
    dx=np.diff(cx)/np.diff(t); dy=np.diff(cy)/np.diff(t)
    for i,tt in enumerate(s['t'][:-1]): vel[(int(tid),int(tt))]=(float(dx[i]),float(dy[i]))

def planefit(x,y,t):
    A=np.column_stack([np.ones_like(x),x,y])
    coef,*_=np.linalg.lstsq(A,t,rcond=None)
    return coef[1],coef[2]           # dt/dx, dt/dy  in s/px

rows=[]
for a,b in exp:
    mid=(a+b)/2.0
    key=min(by_t,key=lambda z:abs(z-mid))
    if abs(key-mid)>26000: continue
    ma=(a-t_off)//1000; mb=(b-t_off)//1000+1
    if ma<0 or mb>=len(ms2i) or mb<=ma: continue
    j0,j1=int(ms2i[ma]),int(ms2i[mb])
    if j1-j0<500: continue
    tt=ev['t'][j0:j1].astype(np.int64)+t_off
    xx=ev['x'][j0:j1].astype(np.int64); yy=ev['y'][j0:j1].astype(np.int64)
    k=(tt>=a)&(tt<b); tt,xx,yy=tt[k],xx[k],yy[k]
    for r in by_t[key]:
        vv=vel.get((int(r['track_id']),key))
        if vv is None: continue
        sp=np.hypot(*vv)
        if sp<5: continue                        # need real motion to have a gradient
        x0,y0=r['x'],r['y']; x1,y1=x0+r['w'],y0+r['h']
        m=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1); n=int(m.sum())
        if n<MIN_EV: continue
        X=xx[m].astype(float); Y=yy[m].astype(float); T=(tt[m]-mid)*1e-6
        gx,gy=planefit(X-X.mean(),Y-Y.mean(),T)
        Ts=rng.permutation(T)                     # time-shuffled: kills motion, keeps rate
        sx,sy=planefit(X-X.mean(),Y-Y.mean(),Ts)
        rows.append((gx,gy,sx,sy,vv[0],vv[1],sp,n))
A=np.array(rows)
gx,gy,sx,sy,vx,vy,sp,N=A.T
gm=np.hypot(gx,gy); sm=np.hypot(sx,sy)
print(f"boxes {len(A)}   median label speed {np.median(sp):.1f} px/s")
print(f"\nGRADIENT MAGNITUDE  (motion predicts 1/|v|)")
print(f"  measured |grad t| median {np.median(gm)*1e6:8.2f} us/px")
print(f"  time-shuffled null      {np.median(sm)*1e6:8.2f} us/px")
print(f"  1/|v| from labels       {np.median(1/sp)*1e6:8.2f} us/px")
# alignment: cos between -grad t and velocity (t increases opposite to travel for a leading edge)
u=np.column_stack([vx,vy])/sp[:,None]
cos=(gx*u[:,0]+gy*u[:,1])/np.maximum(gm,1e-12)
p=rng.permutation(len(A))
cos_null=(gx*u[p,0]+gy*u[p,1])/np.maximum(gm,1e-12)
cos_sh=(sx*u[:,0]+sy*u[:,1])/np.maximum(sm,1e-12)
print(f"\nDIRECTION ALIGNMENT  cos(grad t, v)")
print(f"  measured        mean {cos.mean():+.4f}   median {np.median(cos):+.4f}")
print(f"  shuffled-v null mean {cos_null.mean():+.4f}")
print(f"  time-shuffled   mean {cos_sh.mean():+.4f}")
se=1/np.sqrt(len(A))
print(f"  n={len(A)}  SE~{se:.4f}   -> measured is {abs(cos.mean())/se:.1f} SE from zero")
json.dump(dict(n=int(len(A)),grad_us_px=float(np.median(gm)*1e6),
               shuffle_us_px=float(np.median(sm)*1e6),inv_v_us_px=float(np.median(1/sp)*1e6),
               cos_mean=float(cos.mean()),cos_null=float(cos_null.mean()),
               cos_timeshuf=float(cos_sh.mean()),se=float(se)),
          open('/work/experiments/e20_spatial_gradient/result.json','w'),indent=1)
print("WROTE")
