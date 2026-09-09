"""E54 - the manuscript macros for the cross-model ranking result (E51-E53).

The result is negative in the sense external review #7 asked about: scoring each detector at
its own best displacement does not reorder five released checkpoints in any speed stratum.
What makes it a measurement rather than a failure to find one is the bound: in every stratum
the largest gain any model draws from alignment is a fraction of the smallest gap between
adjacent models, so no refinement of the delta grid can reorder them.
"""
import json, numpy as np
A=json.load(open('experiments/e51_ranking/curves.json'))
F=json.load(open('experiments/e51_ranking/curves_fast.json'))
NAMES=['rvt-t','rvt-s','rvt-b','s5vit-small','s5vit-base']
STR=[('all moving',lambda n:A[n]['all moving']),('10-25 px/s',lambda n:A[n]['10-25 px/s']),
     ('25-50 px/s',lambda n:A[n]['25-50 px/s']),('>50 px/s',lambda n:F[n])]
rows=[]; worst=0.0
print(f"{'stratum':<12}{'order at delta=0':<52}{'gap':>7}{'gain':>7}{'ratio':>7}")
for sname,get in STR:
    z=sorted(((n,get(n)['map_at_zero']) for n in NAMES),key=lambda r:-r[1])
    a=sorted(((n,get(n)['map_at_argmax']) for n in NAMES),key=lambda r:-r[1])
    gaps=[100*(z[k][1]-z[k+1][1]) for k in range(len(z)-1)]
    gains=[100*(get(n)['map_at_argmax']-get(n)['map_at_zero']) for n in NAMES]
    r=max(gains)/min(gaps); worst=max(worst,r)
    same=[n for n,_ in z]==[n for n,_ in a]
    rows.append(dict(stratum=sname,order=[n for n,_ in z],order_aligned=[n for n,_ in a],
                     same=same,min_gap=min(gaps),max_gain=max(gains),ratio=r,
                     argmax_ms={n:get(n)['argmax_ms'] for n in NAMES}))
    print(f"{sname:<12}{' > '.join(n for n,_ in z):<52}{min(gaps):7.3f}{max(gains):7.3f}{r:7.2f}")
    assert same, f"{sname}: the order changed, the paragraph below is wrong"
ams=sorted({v for r in rows for v in r['argmax_ms'].values()})
pos={n:{r['stratum']:[x for x,_ in [(m,0) for m in r['order']]].index(n)+1 for r in rows} for n in NAMES}
print("\nrank by stratum")
for n in NAMES: print(f"  {n:<12} "+"  ".join(f"{s}:{pos[n][s]}" for s in [r['stratum'] for r in rows]))
mover=max(NAMES,key=lambda n: max(pos[n].values())-min(pos[n].values()))
blk=f"""
%% ===== E51-E53 measured 2026-09-08 (experiments/e51_ranking): does the interval change a
%% benchmark COMPARISON? Detections for all five released checkpoints were dumped under one
%% protocol (same frames, same confidence, same NMS, ground truth identical across models and
%% identical to E37's), then each model was scored at delta = 0 and again at its own best
%% displacement, in four speed strata. The ordering never changes, and it cannot: in every
%% stratum the largest gain any model draws from alignment is a fraction of the smallest gap
%% between adjacent models, so no refinement of the grid can reorder them.
\\newcommand{{\\rankCkpts}}{{{len(NAMES)}}}            %% released checkpoints scored
\\newcommand{{\\rankStrata}}{{four}}          %% speed strata examined
\\newcommand{{\\rankFlips}}{{0}}              %% pairwise sign flips, of 10 per stratum
\\newcommand{{\\rankMaxGain}}{{{max(r['max_gain'] for r in rows):.2f}}}      %% mAP points, the largest alignment gain seen
\\newcommand{{\\rankMinGap}}{{{min(r['min_gap'] for r in rows):.2f}}}       %% mAP points, the smallest adjacent gap seen
\\newcommand{{\\rankRatio}}{{{100*worst:.0f}}}          %% percent: worst-case gain over gap within a stratum
\\newcommand{{\\rankArgLo}}{{\\ensuremath{{{min(ams):.0f}}}}}   %% ms, earliest per-model argmax
\\newcommand{{\\rankArgHi}}{{\\ensuremath{{{max(ams):.0f}}}}}    %% ms, latest per-model argmax
\\newcommand{{\\rankMover}}{{\\texttt{{{mover.replace('_','\\\\_')}}}}}  %% the checkpoint whose rank moves most
\\newcommand{{\\rankMoverBest}}{{{min(pos[mover].values())}}}          %% its best rank across strata
\\newcommand{{\\rankMoverWorst}}{{{max(pos[mover].values())}}}         %% and its worst
"""
open('experiments/e51_ranking/macros.tex','w').write(blk)
json.dump(dict(rows=rows,worst_ratio=worst,rank_by_stratum=pos),
          open('experiments/e51_ranking/summary.json','w'),indent=1)
print("\nWROTE experiments/e51_ranking/macros.tex\n"+blk)
