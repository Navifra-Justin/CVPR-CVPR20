"""E26 - is the gradient alignment a per-object quantity, or ego-motion?

E25 found the alignment is STRONGER where objects move slower (r = -0.91 against
the fraction above 20 px/s). A per-object motion signal should behave the other way.
The obvious alternative: a labelled box contains background as well as object, the
whole image sweeps under ego-motion, and for slow objects the label velocity is
nearly the background velocity, so the alignment is with the scene rather than the
object.

Decisive control. For each box compute the evidence-time gradient three ways:
  BOX      all events inside the box
  CORE     events inside the box eroded by 25 % on each side (object-dominated)
  RING     events in a surrounding annulus of equal area, box excluded (background only)
and align each with the same label velocity. If RING aligns as well as BOX, the
signal is ego-motion and the per-object reading is wrong. If CORE > BOX > RING, it
is the object.
"""
import h5py, hdf5plugin, numpy as np, json, os
SEQS=['zurich_city_00_a','zurich_city_01_a','zurich_city_02_a','zurich_city_03_a','zurich_city_09_a','zurich_city_10_a']
MIN_EV=400
rng=np.random.default_rng(0)
def grad(X,Y,T):
    A=np.column_stack([np.ones_like(X),X-X.mean(),Y-Y.mean()])
    c,*_=np.linalg.lstsq(A,T,rcond=None); return c[1],c[2]
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
    cb=[];cc=[];cr=[]
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
        ts=(tt-mid)*1e-6
        for r in by_t[key]:
            x0,y0=int(r['x']),int(r['y']); w0=int(r['w']); h0=int(r['h']); x1,y1=x0+w0,y0+h0
            vv=vel.get((int(r['track_id']),key))
            if vv is None: continue
            sp=float(np.hypot(*vv))
            if sp<5: continue
            u=(vv[0]/sp,vv[1]/sp)
            inb=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)
            ex,ey=int(0.25*w0),int(0.25*h0)
            core=(xx>=x0+ex)&(xx<x1-ex)&(yy>=y0+ey)&(yy<y1-ey)
            # annulus of equal area: expand by factor sqrt(2), exclude the box
            gx0,gy0=int(x0-0.207*w0),int(y0-0.207*h0); gx1,gy1=int(x1+0.207*w0),int(y1+0.207*h0)
            outer=(xx>=gx0)&(xx<gx1)&(yy>=gy0)&(yy<gy1)&(~inb)
            vals={}
            ok=True
            for nm,mask in (('box',inb),('core',core),('ring',outer)):
                n=int(mask.sum())
                if n<MIN_EV: ok=False; break
                gx,gy=grad(xx[mask].astype(float),yy[mask].astype(float),ts[mask])
                g=np.hypot(gx,gy)
                if g<1e-12: ok=False; break
                vals[nm]=(gx*u[0]+gy*u[1])/g
            if not ok: continue
            cb.append(vals['box']); cc.append(vals['core']); cr.append(vals['ring'])
    f.close()
    B=np.array(cb); C=np.array(cc); R=np.array(cr)
    if len(B)<30: print(f"{SEQ}: too few paired boxes ({len(B)})",flush=True); continue
    dBR=B-R; dCR=C-R          # paired: each box minus its OWN local background
    seB=B.std(ddof=1)/np.sqrt(len(B)); seD=dBR.std(ddof=1)/np.sqrt(len(dBR))
    seC=dCR.std(ddof=1)/np.sqrt(len(dCR))
    out[SEQ]=dict(n=len(B),box=float(B.mean()),ring=float(R.mean()),
                  paired_box_minus_ring=float(dBR.mean()),se=float(seD),
                  sigma=float(abs(dBR.mean())/seD),
                  paired_core_minus_ring=float(dCR.mean()),core_sigma=float(abs(dCR.mean())/seC))
    print(f"{SEQ:<20} n={len(B):>5}  BOX {B.mean():+.4f}  RING {R.mean():+.4f}  "
          f"PAIRED box-ring {dBR.mean():+.4f} ({abs(dBR.mean())/seD:.1f}SE)  "
          f"core-ring {dCR.mean():+.4f} ({abs(dCR.mean())/seC:.1f}SE)",flush=True)
vals=[v['paired_box_minus_ring'] for v in out.values()]
ns=[v['n'] for v in out.values()]
w=np.array(ns,float); w/=w.sum()
print(f"\nPAIRED EXCESS over each box's own local background: weighted mean {float(np.dot(w,vals)):+.4f}")
print(f"  sequences positive: {sum(1 for v in vals if v>0)}/{len(vals)}")
print("verdict: a positive paired excess means the object carries alignment its own")
print("surrounding background does not. Ego-motion is common to both and cancels.")
os.makedirs('/work/experiments/e26_egomotion',exist_ok=True)
json.dump(out,open('/work/experiments/e26_egomotion/paired.json','w'),indent=1)
print("WROTE")
