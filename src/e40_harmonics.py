"""E40 - which frequency carries the mains signature, measured without choosing the band.

E10 reported "the strongest line between 90 and 110 Hz, at 100.00 Hz, a factor of 10841
above the 60-160 Hz continuum". Both the search band and the continuum band were fixed in
advance, so that measurement could not have found a line anywhere else. Rendering one
exposure window as a video showed the event rate peaking about every 5 ms, which is 200 Hz,
and a wide sweep on the whole sequence confirmed it: the strongest line is at exactly
200.00 Hz.

That is not a contradiction of the physics, it is the physics. An event camera responds to
log-intensity CHANGE, so a lamp whose intensity oscillates at 100 Hz drives events on both
the rising and the falling edge, and the arrival rate carries the harmonic series of that
100 Hz fundamental with the second harmonic dominant.

This measures the whole series, in every ceiling sequence and in the daytime control, with
no band chosen in advance: the line-to-local-continuum ratio at 50, 100, 150, 200, 250,
300 and 400 Hz. Odd multiples of 50 that are not multiples of 100 are the diagnostic - a
rectified 50 Hz source puts no power there.
"""
import h5py, hdf5plugin, numpy as np, json, os
SEQS=['zurich_city_00_a','zurich_city_01_a','zurich_city_02_a',
      'zurich_city_03_a','zurich_city_09_a','zurich_city_10_a','interlaken_00_c']
CEILING=set(SEQS[:6])
F=np.arange(20.0,450.1,0.25)
TEST=[50,100,150,200,250,300,400]
NEV=400000
rng=np.random.default_rng(0)
out={}
for SEQ in SEQS:
    p=f'/work/data/dsec/{SEQ}/events.h5'
    if not os.path.exists(p): print(f"  {SEQ}: no events.h5"); continue
    f=h5py.File(p,'r'); ev=f['events']
    N=ev['t'].shape[0]
    idx=np.sort(rng.choice(N,size=min(NEV,N),replace=False))
    t=ev['t'][:][idx].astype(np.float64)*1e-6; t-=t[0]
    A=len(t)*np.abs(np.exp(-2j*np.pi*np.outer(F,t)).mean(axis=1))**2
    row={}
    for f0 in TEST:
        i=int(np.argmin(abs(F-f0)))
        b=(abs(F-f0)<=15.0)&(abs(F-f0)>=1.0)
        row[f0]=float(A[i]/max(np.median(A[b]),1e-12))
    k=int(np.argmax(A[F>60])); pk=float(F[F>60][k])
    row['peak_hz']=pk; row['n_events_total']=int(N)
    out[SEQ]=row
    tag='ceiling' if SEQ in CEILING else 'daytime control'
    print(f"  {SEQ:<20} ({tag:<15})  peak {pk:7.2f} Hz   "
          +"  ".join(f"{f0}:{row[f0]:8.1f}" for f0 in TEST),flush=True)
print("\n  ratios are the line over the median of its own +-15 Hz neighbourhood")
print("  a rectified 50 Hz source has no odd-50 Hz harmonics: 50, 150 and 250 are the check")
cei=[out[s] for s in SEQS[:6] if s in out]
if cei:
    for f0 in TEST:
        v=[c[f0] for c in cei]
        print(f"   {f0:4d} Hz  ceiling median {np.median(v):9.1f}   min {min(v):8.1f}   max {max(v):9.1f}"
              +(f"   daytime {out['interlaken_00_c'][f0]:7.1f}" if 'interlaken_00_c' in out else ""))
os.makedirs('/work/experiments/e40_harmonics',exist_ok=True)
json.dump(out,open('/work/experiments/e40_harmonics/result.json','w'),indent=1)
print("\nWROTE")
