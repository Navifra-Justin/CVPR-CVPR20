"""12-step protocol, pass 3, step 11: a new method that separates the two explanations.

Pass 2 found label residuals elongated along the motion (R=1.94). Two explanations:
  (A) a real per-object temporal term, which displaces a box along its velocity;
  (B) local-fit error, which also accumulates along the motion and needs no temporal term.

They differ in one testable way. Explanation (A) predicts that the along-track residual of
a box is proportional to that box's OWN evidence-time deviation, measured independently
from the event stream. Explanation (B) predicts no relation: a polynomial fit to label
positions knows nothing about the events.

So: pair the two independent measurements per (frame, track) and correlate.
    x = evidence-time deviation (us, from events, E09/E11 route)
    y = along-track label residual (px, from labels, E15b route)
    prediction of (A): y ~= x * 1e-6 * v, slope 1 in those units, and cross-track ~ 0.
"""
import h5py, hdf5plugin, numpy as np, json
SEQ='zurich_city_09_a'; MIN_EV=200; MIN_OBJ=3
f=h5py.File(f'/work/data/dsec/{SEQ}/events.h5','r'); ev=f['events']; ms2i=f['ms_to_idx'][:]
t_off=int(f['t_offset'][()])
exp=[tuple(int(v) for v in l.split(',')) for l in
     open(f'/work/experiments/e00_exposure_survey/e_{SEQ}.txt') if not l.startswith('#') and l.strip()]
tr=np.load(f'/work/data/dsec_det/train/train/{SEQ}/object_detections/left/tracks.npy')

# --- label-side: leave-one-out local quadratic residual, projected -------------
res={}
for tid in np.unique(tr['track_id']):
    s=np.sort(tr[tr['track_id']==tid],order='t')
    if len(s)<7: continue
    T=s['t'].astype(np.float64)*1e-6
    X=(s['x']+s['w']/2.0).astype(float); Y=(s['y']+s['h']/2.0).astype(float)
    for k in range(2,len(T)-2):
        w=slice(k-2,k+3); tt=T[w]-T[k]
        if abs(np.median(np.diff(T[w]))-0.05)>0.002: continue
        A=np.vstack([np.ones(5),tt,tt**2]).T
        m=np.ones(5,bool); m[2]=False
        cX=np.linalg.lstsq(A[m],X[w][m],rcond=None)[0]
        cY=np.linalg.lstsq(A[m],Y[w][m],rcond=None)[0]
        rx=X[k]-cX[0]; ry=Y[k]-cY[0]; vx,vy=cX[1],cY[1]
        n=np.hypot(vx,vy)
        if n<1e-6: continue
        res[(int(tid),int(s['t'][k]))]=(rx*vx/n+ry*vy/n, -rx*vy/n+ry*vx/n, n)

# --- event-side: evidence-time deviation within each frame --------------------
by_t={}
for r in tr: by_t.setdefault(int(r['t']),[]).append(r)
X=[]; Yal=[]; Ycr=[]; V=[]
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
        key2=(int(r['track_id']),key)
        if key2 not in res: continue
        x0,y0=r['x'],r['y']; x1,y1=x0+r['w'],y0+r['h']
        m=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)
        if int(m.sum())<MIN_EV: continue
        cs.append((float(tt[m].mean()-mid), res[key2]))
    if len(cs)<MIN_OBJ: continue
    tb=np.array([c[0] for c in cs]); d=tb-tb.mean()
    for dev,(al,cr,v) in zip(d,[c[1] for c in cs]):
        X.append(dev*1e-6*v); Yal.append(al); Ycr.append(cr); V.append(v)
X=np.array(X); Yal=np.array(Yal); Ycr=np.array(Ycr); V=np.array(V)
print(f"paired observations: {len(X)}")
def rep(x,y,lab):
    r=np.corrcoef(x,y)[0,1]
    sl=np.polyfit(x,y,1)[0]
    n=len(x); se=(1-r*r)/max(n-2,1); t=r/np.sqrt(se) if se>0 else float('inf')
    print(f"  {lab:<34} r={r:+.4f}  slope={sl:+.3f}  t={t:+.1f}  n={n}")
    return float(r),float(sl)
print("\nSTEP-11 DISCRIMINATING TEST")
print("  explanation A (real temporal term) predicts: along-track correlates with x, slope ~1, cross-track ~0")
print("  explanation B (local-fit error)    predicts: neither correlates")
ra,sa=rep(X,Yal,"x  vs ALONG-track residual")
rc,sc_=rep(X,Ycr,"x  vs CROSS-track residual (null)")
# permutation null: shuffle x within the dataset
rng=np.random.default_rng(0); p=rng.permutation(len(X))
rp,_=rep(X[p],Yal,"shuffled x vs along (permutation null)")
json.dump(dict(n=int(len(X)),r_along=ra,slope_along=sa,r_cross=rc,slope_cross=sc_,r_perm=rp),
          open('/work/experiments/e15_protocol/pass3.json','w'),indent=1)
print("WROTE")
