"""E46b - the mAP cost of the corrected centroid, evaluated rather than interpolated.

E37b swept delta on a 5 ms grid, so the cost was read at the grid point -25 ms while the
centroid was -24.94 ms. The corrected centroid, -23.81 ms, is not a grid point and the
curve is not linear near its peak, so it is evaluated directly here. The reference at the
label instant and the grid neighbours are re-evaluated in the same call so that the cost
is a difference between two numbers produced by one run of one estimator.
"""
import numpy as np, json
src=open('src/e37b_map_sweep.py').read()
exec(src[:src.index('DELTAS=')], globals())        # data, iou_mat and evaluate, nothing else
NEWC=-0.023810; OLDC=-0.024944
res={}
for mode in ('all','moving'):
    print(f"\n=== {mode} ===")
    row={}
    for name,d in (('zero',0.0),('centroid_new',NEWC),('centroid_old',OLDC),
                   ('grid_25',-0.025),('grid_20',-0.020)):
        m,a=evaluate(d,mode); row[name]=dict(map=m,ap50=a)
        print(f"  {name:<13} delta {d*1e3:+7.2f} ms   mAP {m:.5f}   AP50 {a:.5f}",flush=True)
    z=row['zero']['map']
    for name in ('centroid_new','centroid_old'):
        c=row[name]['map']
        row[name]['drop_points']=100*(z-c); row[name]['drop_pct']=100*(z-c)/z
        print(f"  cost at {name:<13} {100*(z-c):+.3f} mAP points = {100*(z-c)/z:+.2f} % of mAP")
    res[mode]=row
json.dump(res,open('experiments/e37_map/at_centroid.json','w'),indent=1)
print("\nWROTE experiments/e37_map/at_centroid.json")
