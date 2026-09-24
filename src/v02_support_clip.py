"""Video clip 2 - the primary novelty: where a recurrent event detector's evidence is.

Three beats on one axis, so the viewer never has to re-orient:
  (a) the released window. Ten bins of real Gen1 input, drawn as event images, ending at
      the label instant. The per-bin window-ablation influence (E45) fills in and the centroid
      lands at -23.81 ms. E17 measured this with the wrong recurrent state; E45 supersedes
      it, so the clip and the paper carry the same number.
  (b) the history. The axis zooms out to a second and the past windows appear with their
      measured influence (E42). The running influence-weighted centroid slides left as the
      horizon grows, ending at -299 ms with no sign of settling.
  (c) the output. A marker at the label instant, with the measured output time.

Every bar is a measured number; nothing is drawn to scale by hand.
"""
import numpy as np, json, os, h5py, hdf5plugin, glob
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

E45=json.load(open('/work/experiments/e45_influence_fixed/result.json'))
E27=json.load(open('/work/experiments/e27_rows/placebo_diag.json'))['perseq4']
E42=json.load(open('/work/experiments/e42_recurrent_support/result_k19.json'))
OUT='/work/video/frames/v02'; os.makedirs(OUT,exist_ok=True)
binc=np.array(E45['centres'],dtype=float)
binf=np.array(E45['zero']['mean'],dtype=float)
lag=np.array(E42['lag_ms'],dtype=float); linf=np.array(E42['influence'],dtype=float)

# a real input window, drawn as an event image, for the strip at the top
sd=sorted(glob.glob('/work/data/gen1x/gen1/val/*'))[3]
h5=os.path.join(sd,'event_representations_v2','stacked_histogram_dt=50_nbins=10',
                'event_representations.h5')
with h5py.File(h5,'r') as f:
    D=f[list(f.keys())[0]]
    IMG=[np.asarray(D[i],dtype=np.float32) for i in range(30,50)]   # 20 windows
def render(a):
    """one representation -> a displayable image, summed over bins and polarities"""
    v=a.sum(axis=0); v=np.log1p(v)
    return v/max(v.max(),1e-6)

plt.rcParams.update({'font.size':9,'font.family':'serif',
                     'font.serif':['Nimbus Roman','Times New Roman','Times','DejaVu Serif'],
                     'mathtext.fontset':'stix','axes.linewidth':0.8,
                     'text.color':'white','axes.labelcolor':'white',
                     'xtick.color':'white','ytick.color':'white'})
GOLD='#ffd24a'; BLUE='#4ad2ff'; GREY='0.45'
NA,NB,NC=54,96,40                      # frames per beat
TOT=NA+NB+NC

def frame(i):
    fig=plt.figure(figsize=(12.8,7.2),facecolor='black')
    gs=fig.add_gridspec(2,1,height_ratios=[1.0,1.35],hspace=0.30,
                        left=0.075,right=0.985,top=0.90,bottom=0.10)
    axs=fig.add_subplot(gs[0,0]); axs.set_facecolor('black')
    ax=fig.add_subplot(gs[1,0]);  ax.set_facecolor('black')

    if i<NA:                       # beat A: the released window
        p=i/(NA-1); xlim=(-58,22); nb=int(round(p*10))
        title='the released window ends at the label instant'
    elif i<NA+NB:                  # beat B: the history opens up
        p=(i-NA)/(NB-1)
        xlim=(-58-(1010-58)*min(1.0,p*1.6),22)
        nb=10; title='the detector is recurrent: its evidence does not end there'
    else:
        p=1.0; xlim=(-1068,22); nb=10
        title='its output is scored at one instant'

    # --- the input strip: real event windows on the same time axis
    axs.set_xlim(*xlim); axs.set_ylim(0,1); axs.set_yticks([]); axs.set_xticks([])
    for sp in axs.spines.values(): sp.set_visible(False)
    span=xlim[1]-xlim[0]
    nshow=min(20,max(1,int(span/50)+1))
    for k in range(nshow):
        c=-(25.0+50.0*k)
        if c<xlim[0]: continue
        im=render(IMG[len(IMG)-1-k])
        w=44.0
        axs.imshow(im,extent=(c-w/2,c+w/2,0.10,0.95),aspect='auto',cmap='bone',
                   vmin=0,vmax=1,zorder=2,alpha=1.0 if k==0 else 0.72)
        axs.add_patch(Rectangle((c-w/2,0.10),w,0.85,fill=False,
                                ec=GOLD if k==0 else GREY,lw=1.3 if k==0 else 0.7,zorder=3))
    axs.axvline(0,color='white',lw=1.4,ls=':',zorder=4)
    axs.text(0,1.04,'label instant',color='white',fontsize=10,ha='right',va='bottom')
    axs.set_title(title,color='white',fontsize=15,pad=26)

    # --- the influence axis
    ax.set_xlim(*xlim)
    if i<NA:
        ax.bar(binc[:nb],binf[:nb],width=4.4,color=GOLD,edgecolor='none',zorder=3)
        ax.set_ylim(0,binf.max()*1.45)
        ax.set_ylabel('window-ablation influence',fontsize=11)
        if nb==10:
            ax.axvline(E45['zero']['centroid_ms'],color=BLUE,lw=1.8,zorder=4)
            ax.text(E45['zero']['centroid_ms']-2,binf.max()*1.30,
                    'this window is centered\n%.2f ms before the label'%abs(E45['zero']['centroid_ms']),
                    color=BLUE,fontsize=11,ha='right',va='top')
    else:
        nl=1+int(round(min(1.0,(i-NA)/(NB*0.72))*19)) if i<NA+NB else 20
        ax.bar(lag[:nl],linf[:nl],width=42,color=[GOLD]+[ '#c8a53a']*19,
               edgecolor='none',zorder=3)
        ax.set_ylim(0,linf.max()*1.45)
        ax.set_ylabel('influence of each 50 ms window',fontsize=11)
        w=linf[:nl]/linf[:nl].sum(); cen=float((w*lag[:nl]).sum())
        ax.axvline(cen,color=BLUE,lw=1.8,zorder=4)
        ax.text(cen+14,linf.max()*1.36,'ablation-sensitivity centroid %.0f ms'%cen,
                color=BLUE,fontsize=12,ha='left',va='top')
        share=100*linf[0]/linf[:nl].sum()
        ax.text(0.015,0.86,'newest window carries %.1f %% of it'%share,
                transform=ax.transAxes,color=GOLD,fontsize=12,ha='left')
        if nl==20:
            ax.text(0.015,0.74,'the tail has not decayed at %d ms'%abs(lag[-1]),
                    transform=ax.transAxes,color='white',fontsize=11,ha='left')
    ax.axvline(0,color='white',lw=1.2,ls=':',zorder=4)
    if i>=NA+NB:
        ax.plot([E27['tau']],[0],'o',ms=12,color='#ff6b6b',zorder=6,clip_on=False)
        ax.text(0.015,0.62,'measured output time $%+.2f\\pm%.2f$ ms'%(E27['tau'],E27['tau_se']),
                transform=ax.transAxes,color='#ff6b6b',fontsize=12,ha='left')
    ax.set_xlabel('time relative to the label instant (ms)',fontsize=12)
    for sp in ('top','right'): ax.spines[sp].set_visible(False)
    for sp in ('left','bottom'): ax.spines[sp].set_color('0.5')
    fig.savefig(f'{OUT}/{i:04d}.png',dpi=100,facecolor='black')
    plt.close(fig)

for i in range(TOT):
    frame(i)
    if (i+1)%30==0: print(f"  {i+1}/{TOT}",flush=True)
print("WROTE frames")
