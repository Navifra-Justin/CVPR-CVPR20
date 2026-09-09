import h5py, hdf5plugin, numpy as np, sys, json
seq=sys.argv[1]; root=f'/work/data/dsec/{seq}'
f=h5py.File(f'{root}/events.h5','r')
t_off=int(f['t_offset'][()]); ms2i=f['ms_to_idx'][:]
ev=f['events']
exp=[tuple(int(x) for x in l.split(',')) for l in open(f'/work/experiments/e00_exposure_survey/e_{seq}.txt') if not l.startswith('#') and l.strip()]
H,W=480,640
def slice_idx(t_abs_us):
    ms=(t_abs_us - t_off)//1000
    if ms<0 or ms>=len(ms2i): return None
    return int(ms2i[ms])
rows=[]
N=min(len(exp),400)
step=max(1,len(exp)//N)
for k in range(0,len(exp),step):
    a,b=exp[k]
    i0,i1=slice_idx(a),slice_idx(b)
    if i0 is None or i1 is None or i1<=i0: continue
    n=i1-i0
    x=ev['x'][i0:i1]; y=ev['y'][i0:i1]
    # pixels that fired at all during this single exposure
    lin=y.astype(np.int64)*W+x.astype(np.int64)
    uniq=np.unique(lin)
    npix=len(uniq)
    # per-firing-pixel crossing count = how many contrast crossings inside ONE exposure
    rows.append(dict(k=k, exp_us=b-a, n_events=int(n),
                     active_pix=int(npix),
                     crossings_per_active_pix=float(n/max(npix,1)),
                     frac_pixels_active=float(npix/(H*W))))
q=lambda key,p: float(np.percentile([r[key] for r in rows],p))
out=dict(seq=seq, n_frames_measured=len(rows),
         exp_us_med=q('exp_us',50),
         events_per_exposure_med=q('n_events',50),
         events_per_exposure_p90=q('n_events',90),
         frac_pixels_active_med=q('frac_pixels_active',50),
         frac_pixels_active_p90=q('frac_pixels_active',90),
         crossings_per_active_pix_med=q('crossings_per_active_pix',50),
         crossings_per_active_pix_p90=q('crossings_per_active_pix',90))
print(json.dumps(out,indent=1))
json.dump(dict(summary=out,rows=rows),open(f'/work/experiments/e01_intra_exposure_change/{seq}.json','w'),indent=1)
