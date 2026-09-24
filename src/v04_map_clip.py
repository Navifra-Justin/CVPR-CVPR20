"""Video clip 4 - what the interval is worth on the benchmark's own metric.

The same scene carries the problem and the answer. The detector's boxes stay where the
released checkpoint put them; the ground truth slides to the state each object occupied
delta later, which is exactly what E37 does to compute mAP(delta). The curve underneath is
that measurement, with a playhead at the delta being shown.

Frame indices are rebuilt by repeating E37's own iteration order, which needs only the
label files, so the boxes drawn are the ones the sweep scored.
"""
import numpy as np, json, os, glob, h5py, hdf5plugin
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

Z=np.load('/work/experiments/e37_map/dets.npz')
DET=Z['det'].astype(np.float64); GT=Z['gt'].astype(np.float64)
S=json.load(open('/work/experiments/e37_map/strata.json'))
# the centroid marker is read from the measurement, never typed into the plot (E45)
CEN=json.load(open('/work/experiments/e45_influence_fixed/result.json'))['zero']['centroid_ms']
# the cost is the evaluation at that exact centroid, not a grid point (E46b)
COST=json.load(open('/work/experiments/e37_map/at_centroid.json'))['moving']['centroid_new']['drop_points']
OUT='/work/video/frames/v04'; os.makedirs(OUT,exist_ok=True)

# rebuild fid -> (sequence dir, representation index) with E37's iteration order
fid=0; index={}
for sd in sorted(glob.glob('/work/data/gen1x/gen1/val/*')):
    rd=os.path.join(sd,'event_representations_v2','stacked_histogram_dt=50_nbins=10')
    try:
        L=np.load(os.path.join(sd,'labels_v2','labels.npz'))['labels']
        o2r=np.load(os.path.join(rd,'objframe_idx_2_repr_idx.npy'))
    except Exception: continue
    if len(o2r)<3: continue
    ts=np.sort(np.unique(L['t']))
    for k in range(min(len(o2r),len(ts))):
        index[fid]=(rd,int(o2r[k])); fid+=1
print(f"rebuilt {fid} frame indices",flush=True)

# choose a frame with several fast ground-truth boxes
spd=np.hypot(GT[:,6],GT[:,7])
best=None
for f in np.unique(GT[:,0]):
    m=(GT[:,0]==f)&np.isfinite(spd)
    if m.sum()<3: continue
    if (spd[m]>=20).sum()<2: continue
    sc=float(np.median(spd[m]))
    if best is None or sc>best[0]: best=(sc,int(f))
sc,F=best
print(f"frame {F}, median gt speed {sc:.1f} px/s",flush=True)
rd,ri=index[F]
with h5py.File(os.path.join(rd,'event_representations.h5'),'r') as f:
    IM=np.asarray(f[list(f.keys())[0]][ri],dtype=np.float32)
img=np.log1p(IM.sum(axis=0)); img=img/max(img.max(),1e-6)
H,W=img.shape

g=GT[GT[:,0]==F]; d=DET[(DET[:,0]==F)&(DET[:,5]>=0.3)]
print(f"  {len(g)} gt boxes, {len(d)} detections above 0.3",flush=True)
curve=np.array(S['all moving']['map']); cdel=np.array(S['all moving']['deltas_ms'])
# the span quoted on screen is the span of the curve on screen, which runs over the
# stratum sweep's own range; the paper's wider +-60 ms figure would not describe it
SPAN=100*(curve.max()-curve.min()); DLO,DHI=cdel.min(),cdel.max()
# crop to the boxes so that a displacement of a pixel or two is visible at all
gx0=g[:,1].min(); gx1=g[:,3].max(); gy0=g[:,2].min(); gy1=g[:,4].max()
mx=0.16*(gx1-gx0); my=0.30*(gy1-gy0)
CX0=max(0,gx0-mx); CX1=min(W,gx1+mx); CY0=max(0,gy0-my); CY1=min(H,gy1+my)
ZOOM=W/(CX1-CX0)
fast=np.nanmax(np.hypot(g[:,6],g[:,7]))
print(f"  crop {CX0:.0f}-{CX1:.0f} x {CY0:.0f}-{CY1:.0f}, zoom {ZOOM:.1f}x, "
      f"fastest box {fast:.1f} px/s -> {fast*0.050:.2f} px at 50 ms",flush=True)

plt.rcParams.update({'font.size':9,'font.family':'serif',
                     'font.serif':['Nimbus Roman','Times New Roman','Times','DejaVu Serif'],
                     'mathtext.fontset':'stix','axes.linewidth':0.8,
                     'text.color':'white','axes.labelcolor':'white',
                     'xtick.color':'white','ytick.color':'white'})
GOLD='#ffd24a'; RED='#ff6b6b'; BLUE='#4ad2ff'
DEL=np.concatenate([np.linspace(0,-50,45),np.linspace(-50,30,72),np.linspace(30,0,27)])
for i,dl in enumerate(DEL):
    fig=plt.figure(figsize=(12.8,7.2),facecolor='black')
    gs=fig.add_gridspec(2,1,height_ratios=[1.55,1.0],hspace=0.34,
                        left=0.07,right=0.98,top=0.90,bottom=0.10)
    ax=fig.add_subplot(gs[0,0]); ax.set_facecolor('black')
    ax.imshow(img,cmap='bone',vmin=0,vmax=1,extent=(0,W,H,0),aspect='auto')
    for r in d:
        ax.add_patch(Rectangle((r[1],r[2]),r[3]-r[1],r[4]-r[2],fill=False,ec=GOLD,lw=1.6))
    for r in g:
        vx,vy=r[6],r[7]
        sh=(dl*1e-3*vx,dl*1e-3*vy) if np.isfinite(vx) else (0.0,0.0)
        ax.add_patch(Rectangle((r[1]+sh[0],r[2]+sh[1]),r[3]-r[1],r[4]-r[2],
                               fill=False,ec=RED,lw=1.6,ls='--'))
    ax.set_xlim(CX0,CX1); ax.set_ylim(CY1,CY0); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_color('0.3')
    ax.set_title('the detections stay fixed while the ground truth moves to the state '
                 'each object occupied $\\delta$ later',color='white',fontsize=15,pad=18)
    BB=dict(facecolor='black',alpha=0.6,edgecolor='none',pad=1.8)
    ax.text(0.014,0.075,'released detections',transform=ax.transAxes,color=GOLD,
            fontsize=12,bbox=BB)
    ax.text(0.014,0.025,'ground truth at $\\delta$ = %+6.1f ms'%dl,
            transform=ax.transAxes,color=RED,fontsize=12,bbox=BB)
    ax.text(0.978,0.045,'fastest box moves %.1f px over 50 ms'%(fast*0.050),
            transform=ax.transAxes,color='0.8',fontsize=11,ha='right',bbox=BB)
    ax2=fig.add_subplot(gs[1,0]); ax2.set_facecolor('black')
    ax2.plot(cdel,100*(curve-curve[np.argmin(abs(cdel))]),color=GOLD,lw=2.0)
    ax2.axvline(0,color='white',lw=1.0,ls=':')
    ax2.axvline(CEN,color=BLUE,lw=1.0,ls='--')
    ax2.axvline(dl,color=RED,lw=1.6)
    ax2.set_xlim(-52,32); ax2.set_xlabel('$\\delta$ (ms)',fontsize=12)
    ax2.set_ylabel('mAP relative to $\\delta=0$\n(points)',fontsize=11)
    ax2.text(CEN+0.9,ax2.get_ylim()[0]*0.90,"ablation-sensitivity centroid",
             color=BLUE,fontsize=10,rotation=90,va='bottom')
    ax2.text(0.985,0.14,'over %+.0f to %+.0f ms the curve moves %.2f points'%(DLO,DHI,SPAN),
             transform=ax2.transAxes,color='white',fontsize=12,ha='right')
    ax2.text(0.985,0.03,'the interval costs %.2f points'%COST,
             transform=ax2.transAxes,color=GOLD,fontsize=12,ha='right')
    for sp in ('top','right'): ax2.spines[sp].set_visible(False)
    for sp in ('left','bottom'): ax2.spines[sp].set_color('0.5')
    fig.savefig(f'{OUT}/{i:04d}.png',dpi=100,facecolor='black'); plt.close(fig)
    if (i+1)%36==0: print(f"  {i+1}/{len(DEL)}",flush=True)
print("WROTE frames")
