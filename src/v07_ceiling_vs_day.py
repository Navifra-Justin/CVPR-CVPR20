"""Video clip 7 - the flicker, played, against the daytime control played the same way.

This paper proposes no method, so it has no baseline-versus-ours footage and none is
manufactured. The one controlled visual contrast it does make is the one the measurements
rest on: the ceiling-exposure recordings carry a mains-driven temporal structure and the
daytime recording does not. That is shown here as actual event playback rather than as a
spectrum, because it can only be checked by watching it.

Both panels are rendered identically. The same 15 ms of raw event stream, taken from inside
a published exposure of each recording, in the same 350 us slices, at the same slow motion.
Each rate curve is normalised to its own mean, which is stated on screen: the two recordings
differ in event count by more than an order of magnitude and the claim is about the shape of
the rate, not its height.
"""
import h5py, hdf5plugin, numpy as np, os, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

SPAN=15000; SLICE=350; NSL=SPAN//SLICE          # 42 slices of the same width for both
PANELS=[('zurich_city_09_a','ceiling exposure, night'),
        ('interlaken_00_c','daytime control')]
OUT='/work/video/frames/v07'; os.makedirs(OUT,exist_ok=True)

def load(seq):
    f=h5py.File(f'/work/data/dsec/{seq}/events.h5','r')
    ev=f['events']; ms2i=f['ms_to_idx'][:]; t_off=int(f['t_offset'][()])
    exp=[tuple(int(v) for v in l.split(',')) for l in
         open(f'/work/experiments/e00_exposure_survey/e_{seq}.txt')
         if not l.startswith('#') and l.strip()]
    best=None
    for a,b in exp:                              # the densest window of the right length
        s=a; e=s+SPAN
        ma=(s-t_off)//1000; mb=(e-t_off)//1000+1
        if ma<0 or mb>=len(ms2i) or mb<=ma: continue
        j0,j1=int(ms2i[ma]),int(ms2i[mb])
        if j1-j0<2000: continue
        if best is None or (j1-j0)>best[0]: best=(j1-j0,s,e,j0,j1)
        if best and best[0]>400000: break
    n,s,e,j0,j1=best
    t=ev['t'][j0:j1].astype(np.int64)+t_off
    x=ev['x'][j0:j1].astype(np.int64); y=ev['y'][j0:j1].astype(np.int64)
    k=(t>=s)&(t<e); t,x,y=t[k],x[k],y[k]
    edges=np.arange(s,s+SPAN+1,SLICE)
    rate,_=np.histogram(t,bins=edges)
    f.close()
    return dict(seq=seq,t=t,x=x,y=y,s=s,rate=rate.astype(float),edges=edges)

P=[load(s) for s,_ in PANELS]
for p,(s,lab) in zip(P,PANELS):
    print(f"{s:<18} {len(p['t']):>9} events in {SPAN/1000:.0f} ms   "
          f"rate mean {p['rate'].mean():.0f}/slice   max/min {p['rate'].max()/max(p['rate'].min(),1):.1f}",
          flush=True)
plt.rcParams.update({'font.size':9,'font.family':'serif',
                     'font.serif':['Nimbus Roman','Times New Roman','Times','DejaVu Serif'],
                     'mathtext.fontset':'stix','axes.linewidth':0.8,
                     'text.color':'white','axes.labelcolor':'white',
                     'xtick.color':'white','ytick.color':'white'})
GOLD='#ffd24a'; BLUE='#4ad2ff'; H,W=480,640

def frame(i):
    fig=plt.figure(figsize=(12.8,7.2),facecolor='black')
    gs=fig.add_gridspec(2,2,height_ratios=[1.0,0.62],hspace=0.32,wspace=0.10,
                        left=0.055,right=0.985,top=0.88,bottom=0.10)
    for c,(p,(seq,lab)) in enumerate(zip(P,PANELS)):
        ax=fig.add_subplot(gs[0,c]); ax.set_facecolor('black')
        lo=p['s']+i*SLICE; hi=lo+SLICE
        k=(p['t']>=lo)&(p['t']<hi)
        ax.scatter(p['x'][k],p['y'][k],s=0.6,c=('#ffffff' if c==0 else '#ffffff'),
                   alpha=0.85,linewidths=0,marker='.')
        ax.set_xlim(0,W); ax.set_ylim(H,0); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values(): sp.set_color('0.4')
        ax.set_title(f"{lab}\n{seq.replace('_',chr(92)+'_') if False else seq}",
                     color=(GOLD if c==0 else BLUE),fontsize=13,pad=6)
        ax.text(0.02,0.04,f"{len(p['t']):,} events in the 15 ms shown",
                transform=ax.transAxes,color='0.85',fontsize=11)
        axr=fig.add_subplot(gs[1,c]); axr.set_facecolor('black')
        r=p['rate']/p['rate'].mean()
        axr.plot((p['edges'][:-1]-p['s'])/1000.0,r,color=(GOLD if c==0 else BLUE),lw=2.0)
        axr.axvline((lo-p['s'])/1000.0,color='white',lw=1.4)
        axr.set_ylim(0,max(2.2,r.max()*1.12)); axr.set_xlim(0,SPAN/1000.0)
        axr.text(0.985,0.90,f"rate varies {p['rate'].max()/max(p['rate'].min(),1):.1f}$\\times$",
                 transform=axr.transAxes,ha='right',va='top',
                 color=(GOLD if c==0 else BLUE),fontsize=14)
        axr.set_xlabel('time inside the window (ms)',fontsize=11)
        if c==0: axr.set_ylabel('event rate,\nnormalised to its own mean',fontsize=10)
        for sp in ('top','right'): axr.spines[sp].set_visible(False)
        for sp in ('left','bottom'): axr.spines[sp].set_color('0.5')
    fig.text(0.5,0.955,'the same 15 ms of raw event stream, the same 350 $\\mu$s slices, '
             'the same slow motion',ha='center',color='white',fontsize=15)
    fig.savefig(f'{OUT}/{i:04d}.png',dpi=100,facecolor='black'); plt.close(fig)

for i in range(NSL):
    frame(i)
    if (i+1)%10==0: print(f"  {i+1}/{NSL}",flush=True)
json.dump({p['seq']:dict(events=int(len(p['t'])),span_us=SPAN,slice_us=SLICE,
                         rate_max_over_min=float(p['rate'].max()/max(p['rate'].min(),1)))
           for p in P}, open('/work/video/v07_stats.json','w'), indent=1)
print("WROTE frames")
