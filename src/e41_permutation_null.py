"""E41 - the within-frame dispersion against a null that does not assume independence.

Sec. 4.4 compares the within-frame dispersion of the per-box mean event time against the
analytic null w^2/12N_i, which is the variance of a mean of N_i draws uniform on [a,b].
That null assumes the events of a box arrive independently and uniformly. Sec. 4.3 of the
same paper reports that they do not: they arrive in bursts, and E38 measured the
consequence for a different statistic, a 55-fold inflation of the per-box Rayleigh null.
A round-3 audit named this as the most likely of the paper's claims to fall, and it is
right that it has to be tested rather than argued.

The permutation null keeps everything about the frame except which box an event belongs
to. For each frame, the events of all qualifying boxes are pooled and reassigned at random
to boxes, preserving each box's count. Every temporal structure common to the frame - the
exposure, the mains flicker, the burstiness of the scene - survives the reassignment
untouched; only box identity is destroyed. If the observed dispersion is a property of
objects, it exceeds this null. If it is the frame's own arrival statistics, it does not.

The analytic and permutation nulls are reported side by side so the difference between
them is visible.
"""
import h5py, hdf5plugin, numpy as np, json, os
SEQ=os.environ.get('SEQ','zurich_city_09_a'); MIN_EV=200; MIN_OBJ=3; NPERM=200
f=h5py.File(f'/work/data/dsec/{SEQ}/events.h5','r'); ev=f['events']; ms2i=f['ms_to_idx'][:]
t_off=int(f['t_offset'][()])
exp=[tuple(int(v) for v in l.split(',')) for l in
     open(f'/work/experiments/e00_exposure_survey/e_{SEQ}.txt')
     if not l.startswith('#') and l.strip()]
tr=np.load(f'/work/data/dsec_det/train/train/{SEQ}/object_detections/left/tracks.npy')
by_t={}
for r in tr: by_t.setdefault(int(r['t']),[]).append(r)
rng=np.random.default_rng(0)
obs=[]; ana=[]; perm=[]; permsd=[]; nb=[]
obsR=[]; anaR=[]; permR=[]
for a,b in exp:
    mid=(a+b)/2.0; w=float(b-a)
    if not by_t: continue
    key=min(by_t,key=lambda z:abs(z-mid))
    if abs(key-mid)>26000: continue
    ma=(a-t_off)//1000; mb=(b-t_off)//1000+1
    if ma<0 or mb>=len(ms2i) or mb<=ma: continue
    j0,j1=int(ms2i[ma]),int(ms2i[mb])
    if j1-j0<500: continue
    tt=ev['t'][j0:j1].astype(np.int64)+t_off
    xx=ev['x'][j0:j1].astype(np.int64); yy=ev['y'][j0:j1].astype(np.int64)
    k=(tt>=a)&(tt<b); tt,xx,yy=tt[k],xx[k],yy[k]
    if not len(tt): continue
    times=[]; counts=[]
    for r in by_t[key]:
        x0,y0=int(r['x']),int(r['y']); x1,y1=x0+int(r['w']),y0+int(r['h'])
        m=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1); n=int(m.sum())
        if n<MIN_EV: continue
        times.append(tt[m].astype(np.float64)-mid); counts.append(n)
    if len(counts)<MIN_OBJ: continue
    tb=np.array([t.mean() for t in times])
    sd=float(np.std(tb,ddof=1))
    an=float(np.sqrt(np.mean([w*w/(12.0*n) for n in counts])))
    pool=np.concatenate(times); cuts=np.cumsum(counts)[:-1]
    ps=[]
    for _ in range(NPERM):
        q=rng.permutation(pool)
        ps.append(np.std([g.mean() for g in np.split(q,cuts)],ddof=1))
    pm=float(np.median(ps))
    obs.append(sd); ana.append(an); perm.append(pm); nb.append(len(counts))
    # the same three, for random-position boxes of the same shapes
    rt=[]
    for r in by_t[key]:
        bw=int(r['w']); bh=int(r['h'])
        for _ in range(6):
            x0=int(rng.integers(0,max(640-bw,1))); y0=int(rng.integers(0,max(480-bh,1)))
            m=(xx>=x0)&(xx<x0+bw)&(yy>=y0)&(yy<y0+bh)
            if int(m.sum())>=MIN_EV: rt.append(tt[m].astype(np.float64)-mid); break
    if len(rt)>=MIN_OBJ:
        cR=[len(t) for t in rt]; tbR=np.array([t.mean() for t in rt])
        obsR.append(float(np.std(tbR,ddof=1)))
        anaR.append(float(np.sqrt(np.mean([w*w/(12.0*n) for n in cR]))))
        poolR=np.concatenate(rt); cutsR=np.cumsum(cR)[:-1]
        obsRp=[np.std([g.mean() for g in np.split(rng.permutation(poolR),cutsR)],ddof=1)
               for _ in range(NPERM)]
        permR.append(float(np.median(obsRp)))
obs=np.array(obs); ana=np.array(ana); perm=np.array(perm)
def ex(o,n): 
    v=np.median(o)**2-np.median(n)**2
    return float(np.sign(v)*np.sqrt(abs(v)))
print(f"{SEQ}: {len(obs)} qualifying frames, median {np.median(nb):.0f} boxes each\n")
print(f"  observed within-frame sd of t-bar   {np.median(obs):8.1f} us")
print(f"  analytic null  w^2/12N              {np.median(ana):8.1f} us   "
      f"excess {ex(obs,ana):8.1f} us")
print(f"  permutation null (box identity destroyed, {NPERM} draws)"
      f"  {np.median(perm):8.1f} us   excess {ex(obs,perm):8.1f} us")
print(f"  the permutation null exceeds the analytic one by a factor of "
      f"{np.median(perm)/max(np.median(ana),1e-9):.2f}")
print(f"  frames whose observed sd exceeds their own permutation null: "
      f"{100*np.mean(obs>perm):.1f} %")
if obsR:
    obsR=np.array(obsR); anaR=np.array(anaR); permR=np.array(permR)
    print(f"\n  random-position boxes, same shapes ({len(obsR)} frames)")
    print(f"    observed {np.median(obsR):8.1f}   analytic {np.median(anaR):8.1f}"
          f"   permutation {np.median(permR):8.1f}   excess over permutation "
          f"{ex(obsR,permR):8.1f} us")
os.makedirs('/work/experiments/e41_permutation_null',exist_ok=True)
json.dump(dict(seq=SEQ,frames=int(len(obs)),nperm=NPERM,
               obs=float(np.median(obs)),analytic=float(np.median(ana)),
               permutation=float(np.median(perm)),
               excess_analytic=ex(obs,ana),excess_permutation=ex(obs,perm),
               inflation=float(np.median(perm)/max(np.median(ana),1e-9)),
               frac_above_perm=float(np.mean(obs>perm)),
               rand_obs=float(np.median(obsR)) if len(obsR) else None,
               rand_perm=float(np.median(permR)) if len(obsR) else None),
          open(f'/work/experiments/e41_permutation_null/{SEQ}.json','w'),indent=1)
print("\nWROTE")
