"""Qualitative figure: the actual measurement on one real exposure window.

Panel A: every event inside one published 14996 us exposure window, coloured by its
         time within that window, with the labelled boxes drawn on top.
Panel B: the same frame's per-box evidence times against the frame's common time,
         each box's own count and its analytic null.
Panel C: the six-sequence generalisation of the mains signature (E25) - per-box
         Rayleigh Z at 100 Hz and at the 137 Hz off-frequency control, for every
         DSEC train sequence whose exposure is pinned at the 14996 us ceiling.

Panel C previously drew E20's spatial-gradient alignment. E20 was retracted on
2026-09-05 (the alignment is ego-motion; see experiments/e20_spatial_gradient and
experiments/e26_egomotion), so that panel is gone and nothing in this script reads
its result file.
"""
import h5py, hdf5plugin, numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

SEQ='zurich_city_09_a'; MIN_EV=200
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

cands=[]
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
    cs=[]
    for r in by_t[key]:
        x0,y0=int(r['x']),int(r['y']); x1,y1=x0+int(r['w']),y0+int(r['h'])
        m=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1); n=int(m.sum())
        if n<MIN_EV: continue
        cs.append(dict(box=(x0,y0,x1,y1),n=n,tbar=float(tt[m].mean()-mid),
                       tid=int(r['track_id']),v=vel.get((int(r['track_id']),key))))
    if len(cs)>=6:
        sd=np.std([c['tbar'] for c in cs],ddof=1)
        cands.append((sd,a,b,mid,tt,xx,yy,cs))
cands.sort(key=lambda z:z[0])
sd,a,b,mid,tt,xx,yy,cs=cands[len(cands)//2]        # MEDIAN frame, not the largest
print(f"candidate frames {len(cands)}, dispersion p50 {cands[len(cands)//2][0]:.1f} us, "
      f"min {cands[0][0]:.1f}, max {cands[-1][0]:.1f}")
w=b-a
print(f"chosen frame: exposure {w} us, {len(cs)} boxes, {len(tt)} events, sd {sd:.1f} us")

plt.rcParams.update({'font.size':7,'font.family':'serif',
                     'font.serif':['Nimbus Roman','Times New Roman','Times','DejaVu Serif'],
                     'mathtext.fontset':'stix','axes.linewidth':0.6,'pdf.fonttype':42})
# Panel B (per-box event centroid against the frame mean) was dropped on 2026-09-07:
# E38 withdrew the per-box p-values it illustrated, and Sec. 4.4 reports the quantity
# as bounded rather than identified, so it had no surviving claim. The figure is now
# single-column, which is what pays for the E38 controls in the body.
# Panel (b), the six-sequence comparison, was dropped on 2026-09-07: it repeated
# Table 2's numbers, and the space pays for the recurrent-support measurement.
fig=plt.figure(figsize=(3.35,2.05))
gs=fig.add_gridspec(1,1)

# --- A: the whole frame -------------------------------------------------------
axA=fig.add_subplot(gs[0,0])
rel=(tt-a)/w
s=np.random.default_rng(0).permutation(len(tt))[:260000]
axA.scatter(xx[s],yy[s],c=rel[s],s=0.06,cmap='viridis',linewidths=0,rasterized=True)
# Boxes carry an index rather than their evidence time: four of the six overlap in
# the image and their values collide. Panel (b) prints the values against the same
# indices.
for i,c in enumerate(sorted(cs,key=lambda z:z['box'][0])):
    c['idx']=i+1
for c in cs:
    x0,y0,x1,y1=c['box']
    axA.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fill=False,ec='red',lw=0.7))
    tx=min(x1+2,628); ty=max(y0-1,10)
    axA.text(tx,ty,'%d'%c['idx'],color='red',fontsize=5.6,va='bottom',
             ha='right' if tx>600 else 'left', clip_on=True,
             bbox=dict(fc='white',ec='none',alpha=0.75,pad=0.5))
axA.set_xlim(0,640); axA.set_ylim(480,0); axA.set_aspect('equal'); axA.set_anchor('N')
axA.set_xticks([]); axA.set_yticks([])
axA.set_title('every event in one %d $\\mu$s exposure' % w, fontsize=6.6)
cb=fig.colorbar(axA.collections[0],ax=axA,fraction=0.030,pad=0.015,location='bottom')
cb.set_label('position within the exposure window',fontsize=5.6); cb.ax.tick_params(labelsize=5.2)

fig.savefig('/work/paper/figs/fig5_qualitative.pdf',bbox_inches='tight',dpi=300)
print("WROTE fig5")
json.dump(dict(exposure_us=int(w),boxes=len(cs),events=int(len(tt)),sd_us=float(sd),
               candidates=len(cands),
               tbar=[float(c['tbar']) for c in cs],counts=[int(c['n']) for c in cs]),
          open('/work/experiments/e09_per_object_evidence_time/example_frame.json','w'),indent=1)
