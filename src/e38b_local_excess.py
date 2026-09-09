"""E38b - the per-box mains line measured against its own local background.

E38 showed the analytic Exp(1) null is wrong for a box: pooled over six sequences the
off-frequency per-box Z has a median of 38.39 against 0.693, an inflation of 55. Event
times inside one box during a 15 ms exposure arrive in bursts, so the effective sample
size is far below the raw count and Z is inflated at every frequency. Any statement of the
form "99 % of boxes reach p < 1e-3" was therefore computed against a null the data
rejects, and it is withdrawn.

E38's own control was also imperfect: its sweep reached down to 63 Hz, where a 15 ms
window holds less than one cycle and the statistic measures the burst envelope rather than
any oscillation. Both problems are removed by a statistic that never uses a null.

For each box, compute Z(f) = N|C(f)|^2 on a dense grid and report

    R = Z(100 Hz) / median{ Z(f) : f in the local band, f away from the line }

R compares the line with the background the same box produces at neighbouring
frequencies, so the burst inflation, whatever its size, divides out. The identical
statistic is computed at a sham line, which is the control. The pooled median spectrum is
saved so the line can be seen rather than asserted.
"""
import h5py, hdf5plugin, numpy as np, json, os
SEQS=['zurich_city_00_a','zurich_city_01_a','zurich_city_02_a',
      'zurich_city_03_a','zurich_city_09_a','zurich_city_10_a']
MIN_EV=400; MAXN=3000
F=np.arange(60.0,301.0,1.0)                       # the grid
LINE=float(os.environ.get("LINE","100.0")); SHAM=float(os.environ.get("SHAM","137.0"))
def band(centre):
    b=(F>=centre-30)&(F<=centre+30)
    b&= np.abs(F-centre)>=6                        # exclude the line itself
    for k in range(1,16): b&=np.abs(F-20.0*k)>=3   # exclude label-rate harmonics
    for k in range(1,4):  b&=np.abs(F-100.0*k)>=6  # exclude mains harmonics
    return b
BL=band(LINE); BS=band(SHAM)
iL=int(np.argmin(np.abs(F-LINE))); iS=int(np.argmin(np.abs(F-SHAM)))
print(f"grid {F[0]:.0f}-{F[-1]:.0f} Hz, {len(F)} points; "
      f"line band {BL.sum()} points, sham band {BS.sum()} points")
rng=np.random.default_rng(0)
out={}; RL_all=[]; RS_all=[]; SPEC=[]
for SEQ in SEQS:
    f=h5py.File(f'/work/data/dsec/{SEQ}/events.h5','r'); ev=f['events']; ms2i=f['ms_to_idx'][:]
    t_off=int(f['t_offset'][()])
    exp=[tuple(int(v) for v in l.split(',')) for l in
         open(f'/work/experiments/e00_exposure_survey/e_{SEQ}.txt')
         if not l.startswith('#') and l.strip()]
    tr=np.load(f'/work/data/dsec_det/train/train/{SEQ}/object_detections/left/tracks.npy')
    by_t={}
    for r in tr: by_t.setdefault(int(r['t']),[]).append(r)
    RL=[]; RS=[]; sp=[]
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
        k=(tt>=a)&(tt<b); tt,xx,yy=tt[k],xx[k],yy[k]
        for r in by_t[key]:
            x0,y0=int(r['x']),int(r['y']); x1,y1=x0+int(r['w']),y0+int(r['h'])
            m=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1); n=int(m.sum())
            if n<MIN_EV: continue
            ts=(tt[m]-mid)*1e-6
            if len(ts)>MAXN: ts=ts[rng.choice(len(ts),MAXN,replace=False)]
            Z=len(ts)*np.abs(np.exp(-2j*np.pi*np.outer(F,ts)).mean(axis=1))**2
            RL.append(Z[iL]/max(np.median(Z[BL]),1e-12))
            RS.append(Z[iS]/max(np.median(Z[BS]),1e-12))
            sp.append(Z/max(np.median(Z[BL]),1e-12))
    if not RL: continue
    RL=np.array(RL); RS=np.array(RS); sp=np.array(sp)
    RL_all.append(RL); RS_all.append(RS); SPEC.append(np.median(sp,axis=0))
    out[SEQ]=dict(n=int(len(RL)),R_line_med=float(np.median(RL)),
                  R_sham_med=float(np.median(RS)),
                  frac_line_gt_sham_max=float(np.mean(RL>np.percentile(RS,99))))
    print(f"  {SEQ:<20} boxes {len(RL):5d}  R(100 Hz) median {np.median(RL):8.2f}   "
          f"R(137 Hz) median {np.median(RS):6.2f}   "
          f"boxes above the sham p99 ({np.percentile(RS,99):.1f}): {100*np.mean(RL>np.percentile(RS,99)):6.2f} %",flush=True)
RL=np.concatenate(RL_all); RS=np.concatenate(RS_all)
S=np.median(np.array(SPEC),axis=0)
thr=np.percentile(RS,99)
print(f"\npooled over {len(RL)} boxes of all six sequences")
print(f"  R at the {LINE:.0f} Hz line : median {np.median(RL):.2f}, p10 {np.percentile(RL,10):.2f}, p90 {np.percentile(RL,90):.2f}")
print(f"  R at the {SHAM:.0f} Hz sham : median {np.median(RS):.2f}, p99 {thr:.2f}")
print(f"  ratio of medians                       {np.median(RL)/np.median(RS):.1f}x")
print(f"  boxes whose line exceeds the sham p99  {100*np.mean(RL>thr):.2f} %")
print(f"  boxes whose line exceeds the sham median {100*np.mean(RL>np.median(RS)):.2f} %")
k=np.argsort(-S)[:5]
print(f"  the pooled median spectrum peaks at: "+", ".join(f"{F[i]:.0f} Hz ({S[i]:.1f})" for i in k))
os.makedirs('/work/experiments/e38_empirical_null',exist_ok=True)
json.dump(dict(per_seq=out,
               pooled=dict(n=int(len(RL)),R_line_med=float(np.median(RL)),
                           R_line_p10=float(np.percentile(RL,10)),
                           R_sham_med=float(np.median(RS)),
                           R_sham_p99=float(thr),
                           ratio=float(np.median(RL)/np.median(RS)),
                           frac_above_sham_p99=float(np.mean(RL>thr)),
                           frac_above_sham_med=float(np.mean(RL>np.median(RS))),
                           peak_hz=float(F[int(np.argmax(S))])),
               spectrum_hz=[float(v) for v in F],
               spectrum_median=[float(v) for v in S]),
          open(os.environ.get('OUTJ','/work/experiments/e38_empirical_null/local_excess.json'),'w'),indent=1)
print("WROTE local_excess.json")
