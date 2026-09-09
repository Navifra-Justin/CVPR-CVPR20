"""Video clip 3 - the generalization beat, as measured profiles rather than a title card.

Five released checkpoints of two architectures, run through one instrument on the same
sequences: RVT's three capacities (a per-stage ConvLSTM) and SSM-ViT's two (an S5 state
space layer). Each profile arrives in turn on one axis, rescaled to its own mean so the
shapes are comparable, with its own measured centroid marked. The closing frame shows the
band the five centroids occupy against the uniform-weight half-window.

Every number is read from the experiment artifacts at render time.
"""
import numpy as np, json, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

SRC=[('experiments/e48_matched_frames/rvt-t.json','rvt-t','ConvLSTM'),
     ('experiments/e48_matched_frames/rvt-s.json','rvt-s','ConvLSTM'),
     ('experiments/e48_matched_frames/rvt-b.json','rvt-b','ConvLSTM'),
     ('experiments/e47_ssm/s5vit-small-chunked.json','S5-ViT-S','S5 state space'),
     ('experiments/e47_ssm/s5vit-base-chunked.json','S5-ViT-B','S5 state space')]
M=[]
for f,nm,op in SRC:
    d=json.load(open(os.path.join('/work',f)))
    M.append(dict(name=nm,op=op,c=np.array(d['bin_centres'],float),
                  v=np.array(d['bin_influence'],float),
                  cen=d['bin_centroid_ms'],par=d['params_M']))
UNIF=-25.0
cens=[m['cen'] for m in M]
SPAN=max(cens)-min(cens); FAR=max(abs(c-UNIF) for c in cens)
OUT='/work/video/frames/v03'; os.makedirs(OUT,exist_ok=True)
plt.rcParams.update({'font.size':9,'font.family':'serif',
                     'font.serif':['Nimbus Roman','Times New Roman','Times','DejaVu Serif'],
                     'mathtext.fontset':'stix','axes.linewidth':0.8,
                     'text.color':'white','axes.labelcolor':'white',
                     'xtick.color':'white','ytick.color':'white'})
GOLD='#ffd24a'; BLUE='#4ad2ff'
NPER=18; NEND=54; TOT=NPER*len(M)+NEND

def frame(i):
    shown=min(len(M), i//NPER+1) if i<NPER*len(M) else len(M)
    final=i>=NPER*len(M)
    fig=plt.figure(figsize=(12.8,7.2),facecolor='black')
    ax=fig.add_axes([0.075,0.13,0.90,0.70]); ax.set_facecolor('black')
    base=M[0]['v'].mean()
    for k in range(shown):
        m=M[k]; y=m['v']/m['v'].mean()*base
        col=GOLD if m['op']=='ConvLSTM' else BLUE
        fresh=(not final) and (k==shown-1) and (i%NPER)<NPER-4
        ax.plot(m['c'],y,color=col,lw=3.0 if fresh else 1.6,
                marker='o',ms=6 if fresh else 3,zorder=5 if fresh else 3,
                alpha=1.0 if fresh else 0.75)
        ax.axvline(m['cen'],color=col,lw=2.0 if fresh else 0.9,
                   alpha=1.0 if fresh else 0.5,zorder=4)
        ax.text(0.013,0.94-0.075*k,
                f"{m['name']}   {m['op']}   {m['par']:.2f} M   centroid {m['cen']:.2f} ms",
                transform=ax.transAxes,color=col,fontsize=13,ha='left',va='top')
    if final:
        lo,hi=min(cens),max(cens)
        ax.axvspan(lo,hi,color='white',alpha=0.14,zorder=1)
        ax.axvline(UNIF,color='white',lw=1.2,ls='--',zorder=2)
        ax.text(0.013,0.94-0.075*len(M)-0.03,
                f"all five within {FAR:.2f} ms of the uniform-weight "
                f"{abs(UNIF):.2f} ms half-window",
                transform=ax.transAxes,color='white',fontsize=14,ha='left',va='top')
    ax.axvline(0.0,color='white',lw=1.2,ls=':',zorder=2)
    # headroom, so the measured curves never run under the text that names them
    allv=np.concatenate([m['v']/m['v'].mean()*base for m in M])
    ax.set_ylim(allv.min()*0.94, allv.max()*1.62)
    ax.set_xlim(-54,6)
    ax.set_xlabel('bin center, relative to the label instant (ms)',fontsize=13)
    ax.set_ylabel('occlusion influence, rescaled to each\nmodel\'s own mean',fontsize=12)
    fig.text(0.5,0.93,'one instrument, five released checkpoints, two temporal operators',
             ha='center',color='white',fontsize=17)
    for sp in ('top','right'): ax.spines[sp].set_visible(False)
    for sp in ('left','bottom'): ax.spines[sp].set_color('0.5')
    fig.savefig(f'{OUT}/{i:04d}.png',dpi=100,facecolor='black'); plt.close(fig)

for i in range(TOT):
    frame(i)
    if (i+1)%30==0: print(f"  {i+1}/{TOT}",flush=True)
print(f"WROTE frames, span {SPAN:.2f} ms, farthest from uniform {FAR:.2f} ms")
