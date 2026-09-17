"""Title and closing cards. Item 0 of the video standard requires the paper title on
screen for 1.5-2.5 s; the closing card carries one sentence and no bullet list."""
import os, json, numpy as np
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

AB = json.load(open('experiments/e58_chunkpos/allbox.json'))
DID = -AB['did']['s5vit-base']

card('video/frames/v00',
     ['Temporal-Support Identifiability',
      'in Event-Detection Evaluation Pipelines',
      '', 'CVPR 2027 submission'],
     [30, 30, 10, 15], ['white', 'white', 'white', '0.6'],
     66, ys=[0.60, 0.52, 0.46, 0.36])

card('video/frames/v06',
     ['A nominal benchmark timestamp is not a temporal specification.',
      'Under one released streaming evaluation, detections carrying 1 to 4 windows',
      'of recurrent history and detections carrying 17 to 21',
      f'differ by {DID:.2f} mAP points, after an RVT control.', '',
      'Every number here is read from released files alone.'],
     [22, 20, 20, 22, 10, 14],
     ['white', 'white', 'white', '#ffd24a', 'white', '0.6'],
     108, ys=[0.66, 0.585, 0.525, 0.45, 0.39, 0.30])
print("WROTE cards")
