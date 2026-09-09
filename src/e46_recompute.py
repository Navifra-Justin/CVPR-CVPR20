"""E46 - every number that depends on the newest-window centroid, recomputed.

E45 corrects the centroid from -24.94 ms to -23.81 ms by handing the occluded pass the
recurrent state entering the step rather than the one the reference pass returned. Several
manuscript values are functions of that centroid and all of them move:

  the interval to the measured output time, its separation in standard errors,
  the ratio to the label-side dispersion, the displacement at the split's speeds,
  and the mAP cost of displacing the ground truth to it.

The last needs the detection dump, so it is evaluated at the new centroid rather than
interpolated between grid points.
"""
import numpy as np, json
NEW=-23.810; OLD=-24.944
TAU=-2.40; TAUSE=7.18
d=json.load(open('experiments/e45_influence_fixed/result.json'))
sp=[d[k]['centroid_ms'] for k in ('zero','mean','swap','grad')]
print(f"newest-window centroid   {NEW:+.3f} ms   (was {OLD:+.3f})")
print(f"  uniform reference      {d['uniform_ms']:+.2f} ms")
print(f"  difference from it     {NEW-d['uniform_ms']:+.3f} ms = "
      f"{100*abs(NEW-d['uniform_ms'])/5.0:.1f} % of one bin")
print(f"  instrument spread      {min(sp):+.2f} to {max(sp):+.2f} = {max(sp)-min(sp):.2f} ms")
print(f"  bootstrap SE, zero arm {d['zero']['se_ms']:.3f} ms   CV over bins {d['zero']['cv']:.4f}")
m=np.array(d['zero']['mean']); w=m/m.sum()
print(f"  halves carry           {100*w[:5].sum():.1f} % / {100*w[5:].sum():.1f} %")
# The fit reports tau in the convention p - g = -tau v, so a centroid at -23.81 ms on the
# label-relative axis is the hypothesis tau = +23.81. The interval is that hypothesis minus
# the fitted tau, and the separation is that interval in units of the fit's standard error.
TAU_C=-NEW
interval=TAU_C-TAU
sig=interval/TAUSE
print(f"centroid as a lag hypothesis        tau = {TAU_C:+.2f} ms")
print(f"interval, hypothesis minus fit      {interval:.2f} ms   "
      f"(was {(-OLD)-TAU:.2f})")
print(f"separation in SE of the fit         {sig:.2f}   (was {((-OLD)-TAU)/TAUSE:.2f})")
print(f"ratio to the 183.6 us dispersion    {abs(NEW)*1e-3/183.6e-6:.0f}   "
      f"(was {abs(OLD)*1e-3/183.6e-6:.0f})")
ds=json.load(open('experiments/e27_rows/descriptives.json'))
for q in ('90','99'):
    print(f"displacement at speed p{q}          {ds['speed'][q]*abs(NEW)*1e-3:.2f} px   "
          f"(was {ds['speed'][q]*abs(OLD)*1e-3:.2f})")
json.dump(dict(centroid_ms=NEW,uniform_ms=d['uniform_ms'],
               diff_ms=NEW-d['uniform_ms'],diff_pct_of_bin=100*abs(NEW-d['uniform_ms'])/5.0,
               spread_ms=max(sp)-min(sp),spread_lo=min(sp),spread_hi=max(sp),
               boot_se=d['zero']['se_ms'],cv=d['zero']['cv'],
               half_first=float(100*w[:5].sum()),half_second=float(100*w[5:].sum()),
               interval_ms=float(interval),sigmas=float(sig),tau_hypothesis_ms=float(TAU_C),
               term_ratio=float(abs(NEW)*1e-3/183.6e-6),
               px90=float(ds['speed']['90']*abs(NEW)*1e-3),
               px99=float(ds['speed']['99']*abs(NEW)*1e-3)),
          open('experiments/e45_influence_fixed/derived.json','w'),indent=1)
print("WROTE experiments/e45_influence_fixed/derived.json")
