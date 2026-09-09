"""E50 - the macro block for E47c, the carried state's effect by position in the chunk."""
import json, glob, os
R={}
for f in sorted(glob.glob('experiments/e47_ssm/statepos-*.json')):
    d=json.load(open(f)); R[d['model']]=d
if not R: raise SystemExit("no statepos artifacts")
print(f"{'model':<14}{'chunks':>8}   zero-state by position      previous-window by position")
for k,d in R.items():
    z=' '.join('%.5f'%v if v is not None else '  -  ' for v in d['effect_by_position'][:4])
    i=' '.join('%.5f'%v if v is not None else '  -  ' for v in d['inchunk_by_position'][:4])
    print(f"{k:<14}{d['n']:>8}   {z}   {i}")
def get(model,key,idx):
    v=R[model][key][idx]; return v
S=[k for k in R if k.startswith('s5vit')]; V=[k for k in R if k.startswith('rvt')]
blk="%% ===== E47c measured 2026-09-08 (experiments/e47_ssm/statepos-*.json): what the\n"
blk+="%% recurrent state carried between evaluation chunks does to the output, by position\n"
blk+="%% in the chunk, as a relative L2 change in the emitted detection tensor. The control\n"
blk+="%% arm occludes the window one position earlier inside the same chunk, which a model\n"
blk+="%% that ignored its own history entirely would also return zero for.\n"
if S:
    s0=S[0]
    mx=max(v for v in R[s0]['effect_by_position'] if v is not None)
    blk+=f"\\newcommand{{\\ssmStateEffect}}{{{mx:.5f}}}   %% largest over all positions, {s0}\n"
    blk+=f"\\newcommand{{\\ssmInchunkOne}}{{{get(s0,'inchunk_by_position',1):.4f}}}      %% previous window, position 1\n"
    blk+=f"\\newcommand{{\\ssmInchunkLast}}{{{get(s0,'inchunk_by_position',R[s0]['chunk']-1):.4f}}}     %% the same at the last position\n"
    blk+=f"\\newcommand{{\\ssmChunkMeas}}{{{R[s0]['chunk']}}}          %% windows per chunk in this measurement\n"
if V:
    v0=V[0]
    blk+=f"\\newcommand{{\\rvtStateEffect}}{{{get(v0,'effect_by_position',R[v0]['chunk']-1):.4f}}}     %% the same arm on {v0}, last position\n"
    blk+=f"\\newcommand{{\\rvtStateEffectOne}}{{{get(v0,'effect_by_position',1):.4f}}}  %% and at position 1\n"
blk+="\\newcommand{\\ssmEvalChunk}{21}          %% windows per chunk in the released streaming\n"
blk+="                                           %% evaluation: config/dataset/gen1.yaml\n"
blk+="                                           %% sequence_length, and sequence_for_streaming.py\n"
blk+="                                           %% start_indices step by exactly that\n"
open('experiments/e47_ssm/macros_statepos.tex','w').write(blk)
print("\nWROTE experiments/e47_ssm/macros_statepos.tex\n"+blk)
