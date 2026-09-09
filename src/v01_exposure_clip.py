"""Video clip 1 - every event inside one published DSEC exposure window, in time order.

This is the paper's third claim shown rather than asserted, and it can only be verified by
playing it: the events pulse at 100 Hz inside a single 14996 us exposure, twice, because
the mains drives the lamps at twice the 50 Hz line frequency. Nothing is simulated. The
frame is the one main Fig. 3a already uses, the median-dispersion frame of
zurich_city_09_a, chosen before its spectrum was looked at.

Left: the sensor plane. Each rendered frame draws the events of a 350 us slice, so the
whole 14996 us exposure plays as 3000x slow motion. Boxes are the released DSEC-Det labels
of that frame.
Right: the event rate against time inside the exposure, with the playhead. The rate is
computed once over the whole window, so the curve is not built to match the playhead.
"""
import h5py, hdf5plugin, numpy as np, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

SEQ='zurich_city_09_a'; MIN_EV=200; NFRAME=180; SLICE_US=350
OUT='/work/video/frames/v01'
os.makedirs(OUT,exist_ok=True)
f=h5py.File(f'/work/data/dsec/{SEQ}/events.h5','r'); ev=f['events']; ms2i=f['ms_to_idx'][:]
t_off=int(f['t_offset'][()])
exp=[tuple(int(v) for v in l.split(',')) for l in
     open(f'/work/experiments/e00_exposure_survey/e_{SEQ}.txt')
     if not l.startswith('#') and l.strip()]
tr=np.load(f'/work/data/dsec_det/train/train/{SEQ}/object_detections/left/tracks.npy')
by_t={}
for r in tr: by_t.setdefault(int(r['t']),[]).append(r)

cands=[]
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
    cs=[]
    for r in by_t[key]:
        x0,y0=int(r['x']),int(r['y']); x1,y1=x0+int(r['w']),y0+int(r['h'])
        m=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)
        if int(m.sum())<MIN_EV: continue
        cs.append((x0,y0,x1,y1,int(m.sum()),float(tt[m].mean()-mid)))
    if len(cs)>=6:
        cands.append((np.std([c[5] for c in cs],ddof=1),a,b,mid,tt,xx,yy,cs))
cands.sort(key=lambda z:z[0])
sd,a,b,mid,tt,xx,yy,cs=cands[len(cands)//2]
w=b-a
print(f"frame: exposure {w} us, {len(cs)} boxes, {len(tt)} events, within-frame sd {sd:.1f} us")

rel=(tt-a).astype(float)                                   # us since the exposure opened
BINS=np.arange(0,w+50,50.0)
rate,_=np.histogram(rel,bins=BINS)
rate=rate/50.0                                             # events per us
ctr=(BINS[:-1]+BINS[1:])/2

plt.rcParams.update({'font.size':9,'font.family':'serif',
                     'font.serif':['Nimbus Roman','Times New Roman','Times','DejaVu Serif'],
                     'mathtext.fontset':'stix','axes.linewidth':0.8,
                     'text.color':'white','axes.labelcolor':'white',
                     'xtick.color':'white','ytick.color':'white'})
H,W=480,640
for i in range(NFRAME):
    t0=i*(w-SLICE_US)/(NFRAME-1); t1=t0+SLICE_US
    m=(rel>=t0)&(rel<t1)
    fig=plt.figure(figsize=(12.8,7.2),facecolor='black')
    gs=fig.add_gridspec(1,2,width_ratios=[1.32,1.0],wspace=0.20,
                        left=0.045,right=0.985,top=0.90,bottom=0.10)
    ax=fig.add_subplot(gs[0,0]); ax.set_facecolor('black')
    ax.scatter(xx[m],yy[m],s=0.45,c='#ffd24a',linewidths=0,rasterized=True)
    for (x0,y0,x1,y1,n,tb) in cs:
        ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fill=False,ec='#4ad2ff',lw=1.1))
    ax.set_xlim(0,W); ax.set_ylim(H,0); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_color('0.35')
    ax.set_title(f'DSEC {SEQ.replace("_"," ")} — events inside one published '
                 f'{w}\\,µs exposure'.replace('\\,',' '),
                 fontsize=13,color='white',pad=10)
    ax.text(0.015,0.03,f'{t0/1000:6.2f} ms into the exposure',transform=ax.transAxes,
            fontsize=10,color='#ffd24a',family='monospace')
    ax2=fig.add_subplot(gs[0,1]); ax2.set_facecolor('black')
    ax2.plot(ctr/1000.0,rate,color='#ffd24a',lw=1.3)
    ax2.axvspan(t0/1000.0,t1/1000.0,color='white',alpha=0.20)
    ax2.set_xlim(0,w/1000.0); ax2.set_ylim(0,rate.max()*1.15)
    ax2.set_xlabel('time inside the exposure (ms)',fontsize=10)
    ax2.set_ylabel('events per µs',fontsize=10)
    for sp in ('top','right'): ax2.spines[sp].set_visible(False)
    for sp in ('left','bottom'): ax2.spines[sp].set_color('0.5')
    ax2.set_title('the same events, as a rate',fontsize=13,color='white',pad=10)
    for k in range(1,3):
        ax2.axvline(k*10.0,color='#4ad2ff',lw=1.0,ls=':')
    for k in range(1,3):
        ax2.axvline((2*k-1)*5.0,color='#ff9d4a',lw=0.8,ls='--')
    ax2.text(0.985,0.955,'dotted: one 100 Hz intensity period',transform=ax2.transAxes,
             fontsize=10,color='#4ad2ff',ha='right')
    ax2.text(0.985,0.895,'dashed: its midpoint — the rate peaks on both edges,',
             transform=ax2.transAxes,fontsize=10,color='#ff9d4a',ha='right')
    ax2.text(0.985,0.840,'so the strongest line in the event stream is at 200 Hz',
             transform=ax2.transAxes,fontsize=10,color='#ff9d4a',ha='right')
    fig.savefig(f'{OUT}/{i:04d}.png',dpi=100,facecolor='black')
    plt.close(fig)
    if (i+1)%30==0: print(f"  {i+1}/{NFRAME}",flush=True)
print("WROTE frames")
