"""Title and closing cards. Item 0 of the video standard requires the paper title on
screen for 1.5-2.5 s; the closing card carries one sentence and no bullet list."""
import os, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'serif',
                     'font.serif':['Nimbus Roman','Times New Roman','Times','DejaVu Serif'],
                     'mathtext.fontset':'stix','text.color':'white'})
def card(path,lines,sizes,colors,n,ys=None):
    os.makedirs(path,exist_ok=True)
    ys = ys if ys is not None else np.linspace(0.62,0.38,len(lines))
    for i in range(n):
        fig=plt.figure(figsize=(12.8,7.2),facecolor='black')
        a=fig.add_axes([0,0,1,1]); a.set_facecolor('black'); a.axis('off')
        for t,s,c,y in zip(lines,sizes,colors,ys):
            a.text(0.5,y,t,ha='center',va='center',fontsize=s,color=c,wrap=True)
        fig.savefig(f'{path}/{i:04d}.png',dpi=100,facecolor='black'); plt.close(fig)

card('/work/video/frames/v00',
     ['Evidence Time and Output Time of a Released Event Detector,',
      "and a Mains Signature in DSEC's Ceiling-Exposure Sequences",
      '','CVPR 2027 submission'],
     [25,25,10,15],['white','white','white','0.6'],
     66, ys=[0.60,0.53,0.46,0.36])

card('/work/video/frames/v06',
     ['A recurrent event detector’s evidence reaches back past a second,',
      'its output is scored at one instant,',
      'and the benchmark’s metric moves 0.06 points across that gap.','',
      'Everything above is measured from released files alone.'],
     [23,23,23,10,14],['white','white','#ffd24a','white','0.6'],
     108, ys=[0.62,0.555,0.49,0.42,0.33])
print("WROTE cards")
