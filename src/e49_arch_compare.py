"""E49 - the architecture comparison, assembled from E47 and E48 on identical frames.

E48 runs RVT's three capacities and E47 runs SSM-ViT's two through the same bin arm, on the
same 12 Gen1 validation sequences, the same frames, the same zero fill and the same entering
recurrent state. The only thing that differs between the two families is the per-stage
temporal operator: a ConvLSTM against an S5 state space layer.

Prints the table and writes the LaTeX macro block, so no number is retyped.
"""
import json, glob, os, numpy as np
ROWS=[]
for p in sorted(glob.glob('experiments/e48_matched_frames/rvt-*.json')):
    ROWS.append(json.load(open(p)))
for p in sorted(glob.glob('experiments/e47_ssm/s5vit-*-chunked.json')):
    ROWS.append(json.load(open(p)))
if not ROWS: raise SystemExit("no artifacts yet")
order={'rvt-t':0,'rvt-s':1,'rvt-b':2,'small':3,'base':4}
ROWS.sort(key=lambda r: order.get(r['tag'],9))
print(f"{'model':<14}{'operator':<18}{'params':>8}{'n':>6}{'centroid':>11}"
      f"{'CV':>8}{'max/min':>9}{'older %':>9}")
for r in ROWS:
    nm=r['tag'] if r['tag'].startswith('rvt') else 's5vit-'+r['tag']
    op='ConvLSTM' if r['arch'].startswith('RVT') else 'S5 state space'
    n=r.get('n') or r.get('n_bins')
    print(f"{nm:<14}{op:<18}{r['params_M']:>7.2f}M{n:>6}{r['bin_centroid_ms']:>+11.3f}"
          f"{r['bin_cv']:>8.4f}{r['max_over_min']:>9.2f}{r['half_older']:>9.1f}")
c=[r['bin_centroid_ms'] for r in ROWS]
lstm=[r['bin_centroid_ms'] for r in ROWS if r['arch'].startswith('RVT')]
ssm =[r['bin_centroid_ms'] for r in ROWS if not r['arch'].startswith('RVT')]
print(f"\nall {len(c)} released checkpoints span {min(c):+.2f} to {max(c):+.2f} "
      f"= {max(c)-min(c):.2f} ms, against a uniform-weight reference of -25.00 ms")
if lstm and ssm:
    print(f"  ConvLSTM family {min(lstm):+.2f} to {max(lstm):+.2f}   "
          f"S5 family {min(ssm):+.2f} to {max(ssm):+.2f}   "
          f"difference of the family means {np.mean(ssm)-np.mean(lstm):+.2f} ms")
def g(tag,k):
    for r in ROWS:
        if r['tag']==tag: return r[k]
    return None
blk=f"""
%% ===== E47/E48 measured 2026-09-08 (experiments/e47_ssm, experiments/e48_matched_frames):
%% the newest-window bin arm on TWO architectures over the same 12 Gen1 validation
%% sequences and the same frames. SSM-ViT (Zubic et al., CVPR 2024) is a fork of the RVT
%% repository in which each stage's ConvLSTM is replaced by an S5 state space layer; it
%% distributes RVT's own preprocessed Gen1 and builds its window boundaries with the same
%% line of the same script. Both released checkpoints load with 0 missing and 0 unexpected
%% keys. E48 re-runs RVT's three capacities on E47's frames so the two families are
%% measured on identical samples; its rvt-t agrees with E45. SSM-ViT is driven the way its
%% released evaluation drives it, a chunk of windows at a time with the detection head
%% applied per position, and measured at positions carrying half a chunk of history or more
%% (E47b); the one-window-at-a-time convention is withdrawn, see withdrawn_L1/WHY.md.
\\newcommand{{\\archCkpts}}{{{len(ROWS)}}}            %% released checkpoints measured
\\newcommand{{\\archOther}}{{{len(ROWS)-1}}}            %% the ones Fig. 2a draws besides rvt-t
\\newcommand{{\\archSpan}}{{{max(c)-min(c):.2f}}}       %% ms, range of all their centroids
\\newcommand{{\\archLo}}{{\\ensuremath{{{min(c):.2f}}}}}   \\newcommand{{\\archHi}}{{\\ensuremath{{{max(c):.2f}}}}}
\\newcommand{{\\ssmParamsS}}{{{g('small','params_M') or float('nan'):.2f}}}  \\newcommand{{\\ssmParamsB}}{{{g('base','params_M') or float('nan'):.2f}}}
\\newcommand{{\\ssmBinS}}{{\\ensuremath{{{g('small','bin_centroid_ms') or float('nan'):.2f}}}}}
\\newcommand{{\\ssmBinB}}{{\\ensuremath{{{g('base','bin_centroid_ms') or float('nan'):.2f}}}}}
\\newcommand{{\\mfBinT}}{{\\ensuremath{{{g('rvt-t','bin_centroid_ms') or float('nan'):.2f}}}}}
\\newcommand{{\\mfBinS}}{{\\ensuremath{{{g('rvt-s','bin_centroid_ms') or float('nan'):.2f}}}}}
\\newcommand{{\\mfBinB}}{{\\ensuremath{{{g('rvt-b','bin_centroid_ms') or float('nan'):.2f}}}}}
\\newcommand{{\\archSamples}}{{{max((r.get('n') or 0) for r in ROWS)}}}          %% samples per RVT checkpoint
\\newcommand{{\\archSamplesSsm}}{{{min((r.get('n') or 0) for r in ROWS)}}}       %% samples per SSM-ViT checkpoint:
                                           %% fewer, because only chunk positions carrying
                                           %% half a chunk of history or more are used
\\newcommand{{\\archUnifMax}}{{{max(abs(v+25.0) for v in c):.2f}}}       %% ms, the largest distance of any
                                           %% of them from the uniform-weight -25.00
\\newcommand{{\\archUnifPct}}{{{100*max(abs(v+25.0) for v in c)/5.0:.0f}}}        %% that, as a percent of one bin
"""
open('experiments/e47_ssm/macros.tex','w').write(blk)
print("\nWROTE experiments/e47_ssm/macros.tex")
print(blk)
