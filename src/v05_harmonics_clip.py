"""Video clip 5 - the label side: the mains harmonic series, and its absence in daylight.

The spectrum is the measured one (E39, one whole ceiling recording, 0.25 Hz grid). It is
drawn left to right so the viewer watches the lines arrive, and the frequencies that carry
nothing are marked as they are passed. The bars underneath are E40's line-to-continuum
ratios: the ceiling median against the daytime sequence, at every frequency tested.
"""
import numpy as np, json, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

SP=json.load(open('/work/experiments/e39_which_frequency/sequence_spectrum.json'))
H=json.load(open('/work/experiments/e40_harmonics/result.json'))
OUT='/work/video/frames/v05'; os.makedirs(OUT,exist_ok=True)
F=np.array(SP['freq']); A=np.array(SP['power'])
TEST=[50,100,150,200,250,300,400]
CEIL=['zurich_city_00_a','zurich_city_01_a','zurich_city_02_a',
      'zurich_city_03_a','zurich_city_09_a','zurich_city_10_a']
cm=[float(np.median([H[s][str(f)] for s in CEIL])) for f in TEST]
day=[float(H['interlaken_00_c'][str(f)]) for f in TEST]

plt.rcParams.update({'font.size':9,'font.family':'serif',
                     'font.serif':['Nimbus Roman','Times New Roman','Times','DejaVu Serif'],
                     'mathtext.fontset':'stix','axes.linewidth':0.8,
                     'text.color':'white','axes.labelcolor':'white',
                     'xtick.color':'white','ytick.color':'white'})
GOLD='#ffd24a'; BLUE='#4ad2ff'; GREY='0.55'
NS,NB,NH=78,54,30
for i in range(NS+NB+NH):
    fig=plt.figure(figsize=(12.8,7.2),facecolor='black')
    gs=fig.add_gridspec(2,1,height_ratios=[1.25,1.0],hspace=0.42,
                        left=0.075,right=0.98,top=0.90,bottom=0.10)
    ax=fig.add_subplot(gs[0,0]); ax.set_facecolor('black')
    p=min(1.0,i/(NS-1)) if i<NS else 1.0
    fmax=20+p*430
    k=F<=fmax
    ax.semilogy(F[k],np.maximum(A[k],1e-2),color=GOLD,lw=1.1)
    ax.set_xlim(20,450); ax.set_ylim(0.05,5000)
    ax.set_xlabel('frequency (Hz)',fontsize=12)
    ax.set_ylabel('power, one whole recording',fontsize=11)
    for f0,lab,col in [(50,'50',GREY),(100,'100 Hz',BLUE),(150,'150',GREY),
                       (200,'200 Hz',BLUE),(250,'250',GREY),(300,'300 Hz',BLUE)]:
        if fmax<f0: continue
        ax.axvline(f0,color=col,lw=0.8,ls='--' if col==GREY else ':')
        ax.text(f0,3000 if col!=GREY else 0.10,lab,color=col,fontsize=11,
                ha='center',va='top' if col!=GREY else 'bottom')
    ax.set_title('a whole DSEC ceiling-exposure recording, no band chosen in advance',
                 color='white',fontsize=15,pad=18)
    if fmax>=210:
        ax.text(0.985,0.92,'lines at 100, 200 and 300 Hz',transform=ax.transAxes,
                color=BLUE,fontsize=13,ha='right')
    if fmax>=260:
        ax.text(0.985,0.83,'nothing at 50, 150 or 250 Hz',transform=ax.transAxes,
                color=GREY,fontsize=13,ha='right')
    if fmax>=300:
        ax.text(0.985,0.74,'the fingerprint of a rectified supply',transform=ax.transAxes,
                color='white',fontsize=12,ha='right')
    for sp in ('top','right'): ax.spines[sp].set_visible(False)
    for sp in ('left','bottom'): ax.spines[sp].set_color('0.5')

    ax2=fig.add_subplot(gs[1,0]); ax2.set_facecolor('black')
    n=0 if i<NS else min(len(TEST),int(round((i-NS)/max(NB-1,1)*len(TEST))))
    x=np.arange(len(TEST))
    if n:
        ax2.bar(x[:n]-0.19,cm[:n],width=0.36,color=GOLD,label='six ceiling sequences, median')
        ax2.bar(x[:n]+0.19,day[:n],width=0.36,color='0.42',label='daytime sequence')
    ax2.set_yscale('log'); ax2.set_ylim(0.3,4000)
    ax2.set_xticks(x); ax2.set_xticklabels([f'{f}' for f in TEST])
    ax2.set_xlim(-0.6,len(TEST)-0.4)
    ax2.set_xlabel('frequency (Hz)',fontsize=12)
    ax2.set_ylabel('line over its own\nlocal continuum',fontsize=11)
    ax2.axhline(1.0,color='0.6',lw=0.8,ls=':')
    if n>=len(TEST):
        ax2.legend(fontsize=11,frameon=False,loc='upper right',ncol=2)
        ax2.text(0.015,0.86,'the daytime sequence carries neither harmonic',
                 transform=ax2.transAxes,color='white',fontsize=12)
    for sp in ('top','right'): ax2.spines[sp].set_visible(False)
    for sp in ('left','bottom'): ax2.spines[sp].set_color('0.5')
    fig.savefig(f'{OUT}/{i:04d}.png',dpi=100,facecolor='black'); plt.close(fig)
    if (i+1)%40==0: print(f"  {i+1}",flush=True)
print("WROTE frames")
