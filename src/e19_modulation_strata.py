"""E19 - the assumption-free flicker control: stratify by each box's own modulation.

E12's integer-period argument was wrong. E18 then applied an integer-period formula
to a 1.4996-period window, so it is wrong in the same way. Both attempts leaned on a
closed form for the flicker contribution. This one does not.

For each box compute its own modulation depth at 100 Hz, m = 2|C| with
C = (1/N) sum exp(-i w t_k). Then measure the within-frame dispersion of evidence
times using ONLY boxes in a given modulation stratum. If the dispersion is present
among boxes whose own flicker modulation is small, flicker cannot be producing it.
No formula, no subtraction, no window geometry.

Also reported: the same stratification at an off-frequency (137 Hz), where the strata
are noise and any trend is an artifact of stratifying on a noisy statistic.
"""
import h5py, hdf5plugin, numpy as np, json
SEQ='zurich_city_09_a'; MIN_EV=200; MIN_OBJ=3
W1=2*np.pi*100.0; W2=2*np.pi*137.0
f=h5py.File(f'/work/data/dsec/{SEQ}/events.h5','r'); ev=f['events']; ms2i=f['ms_to_idx'][:]
t_off=int(f['t_offset'][()])
exp=[tuple(int(v) for v in l.split(',')) for l in
     open(f'/work/experiments/e00_exposure_survey/e_{SEQ}.txt') if not l.startswith('#') and l.strip()]
tr=np.load(f'/work/data/dsec_det/train/train/{SEQ}/object_detections/left/tracks.npy')
by_t={}
for r in tr: by_t.setdefault(int(r['t']),[]).append(r)

recs=[]
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
    fr=[]
    for r in by_t[key]:
        x0,y0=r['x'],r['y']; x1,y1=x0+r['w'],y0+r['h']
        m=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1); n=int(m.sum())
        if n<MIN_EV: continue
        ts=(tt[m]-mid)*1e-6
        C1=np.exp(-1j*W1*ts).mean(); C2=np.exp(-1j*W2*ts).mean()
        # noise floor of |C| for N random phases is sqrt(pi)/2/sqrt(N); report excess modulation
        fr.append((float(ts.mean()), 2*abs(C1), 2*abs(C2), n, w*1e-6))
    if len(fr)>=MIN_OBJ: recs.append(fr)
allm=np.array([o[1] for f_ in recs for o in f_])
print(f"frames {len(recs)}  boxes {len(allm)}  modulation m=2|C| at 100 Hz:"
      f" p10 {np.percentile(allm,10):.3f} med {np.median(allm):.3f} p90 {np.percentile(allm,90):.3f}")
print(f"  noise floor of m for N=200 random phases: {2*np.sqrt(np.pi)/2/np.sqrt(200):.3f}")

def strat(idx_key, label):
    vals=np.array([o[idx_key] for f_ in recs for o in f_])
    q=np.percentile(vals,[0,25,50,75,100])
    print(f"\n{label}: dispersion within modulation strata")
    print("  stratum   m range        frames  boxes   sd_us   null_us  excess_us")
    out=[]
    for i in range(4):
        lo,hi=q[i],q[i+1]
        sds=[];nulls=[];nb=0
        for f_ in recs:
            sel=[o for o in f_ if lo<=o[idx_key]<=hi]
            if len(sel)<MIN_OBJ: continue
            t=np.array([o[0] for o in sel]); N=np.array([o[3] for o in sel],float); W=sel[0][4]
            sds.append(t.std(ddof=1)); nulls.append(np.sqrt(np.mean(W*W/(12*N)))); nb+=len(sel)
        if not sds: continue
        sd=np.median(sds)*1e6; nu=np.median(nulls)*1e6
        exc=float(np.sqrt(max(sd**2-nu**2,0)))
        print(f"   Q{i+1}     [{lo:.3f},{hi:.3f}]   {len(sds):>5}  {nb:>5}  {sd:7.1f} {nu:8.1f} {exc:9.1f}")
        out.append(dict(q=i+1,lo=float(lo),hi=float(hi),frames=len(sds),boxes=nb,
                        sd=round(sd,1),null=round(nu,1),excess=round(exc,1)))
    return out
o100=strat(1,"100 Hz (mains)")
o137=strat(2,"137 Hz (off-frequency control)")
json.dump(dict(frames=len(recs),boxes=int(len(allm)),
               m100=dict(p10=float(np.percentile(allm,10)),med=float(np.median(allm)),
                         p90=float(np.percentile(allm,90))),
               strata_100=o100,strata_137=o137),
          open('/work/experiments/e19_modulation_strata/result.json','w'),indent=1)
print("WROTE")
