"""E35 - the nearest prior estimator, fitted on the same rows.

Sec. 3.4 argues against the per-object ratio delta = <p-g, u>/|v| on the grounds that its
variance diverges as |v| approaches zero. An argument is not a comparison, so the ratio is
fitted on exactly the rows the reported regression uses and reported beside it.

Three forms of it are shown, because the ratio has no single conventional summary: the
mean, which is what a naive average gives; the median, which is robust but estimates a
different functional; and the mean over a speed floor, which is how practitioners avoid
the divergence. The reported vector regression needs no floor.
"""
import numpy as np, json
Z=np.load('experiments/e27_rows/rows.npz',allow_pickle=True)
A=Z['rows']; ci={c:i for i,c in enumerate(list(Z['cols']))}
g=lambda k:A[:,ci[k]]
seq,dx,dy=g('seq'),g('dx'),g('dy')
vx=(g('fx')+g('bx'))/(g('dt_f')+g('dt_b')); vy=(g('fy')+g('by'))/(g('dt_f')+g('dt_b'))
m=np.isfinite(vx)&np.isfinite(vy)&(np.hypot(vx,vy)>0)
vx,vy,seq,dx,dy=[a[m] for a in (vx,vy,seq,dx,dy)]
V=np.hypot(vx,vy); ux,uy=vx/V,vy/V
epar=dx*ux+dy*uy                      # signed along-track residual, px
delta=-epar/V*1e3                     # ms, sign convention p-g = -tau v
def clse(x,g,n=2000):
    """Cluster bootstrap over sequences. An analytic cluster SE is not usable here:
    some sequences contribute a single row, and the ratio's within-cluster variance is
    undefined for them. The bootstrap needs no within-cluster variance."""
    u=np.unique(g); idx={c:np.where(g==c)[0] for c in u}
    rr=np.random.default_rng(0); out=[]
    for _ in range(n):
        pick=rr.choice(u,len(u),replace=True)
        out.append(x[np.concatenate([idx[c] for c in pick])].mean())
    return float(x.mean()), float(np.std(out))
print(f"rows {len(V)}   median |v| {np.median(V):.2f} px/s   "
      f"{100*np.mean(V<2):.1f} % below 2 px/s\n")
print(" estimator                                   value (ms)")
mu,se=clse(delta,seq)
print(f"  ratio, mean over all rows                  {mu:+9.2f} +- {se:.2f}")
print(f"  ratio, median over all rows                {np.median(delta):+9.2f}")
print(f"  ratio, interquartile range                 {np.percentile(delta,75)-np.percentile(delta,25):9.2f}")
R={'all_mean':[float(mu),float(se)],'all_median':float(np.median(delta))}
for f in [5.,10.,15.,25.]:
    k=V>=f; mu,se=clse(delta[k],seq[k])
    print(f"  ratio, mean above {f:4.0f} px/s (n={k.sum():6d})   {mu:+9.2f} +- {se:.2f}")
    R[f'floor{f:.0f}']=[float(mu),float(se),int(k.sum())]
print(f"\n  reported vector regression, no floor        {-2.40:+9.2f} +- {7.18:.2f}")
print("\n  the ratio's sample standard deviation over all rows: "
      f"{delta.std():.1f} ms, against {delta[V>=15].std():.1f} ms above 15 px/s")
json.dump(R,open('experiments/e27_rows/ratio.json','w'),indent=1)
print("WROTE experiments/e27_rows/ratio.json")
