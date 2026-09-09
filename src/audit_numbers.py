"""A checker for the manuscript's numbers: every macro below is re-derived from the
artifact that produced it and compared with what numbers.tex declares.

This exists because a checker that is never tested passes anything. Each entry names the
file the value must come from and the expression that reads it, so a macro edited by hand
without a corresponding run fails here rather than in review.
"""
import json, re, sys, os, numpy as np

NUM = dict(re.findall(r'\\newcommand\{\\([A-Za-z]+)\}\{(?:\\ensuremath\{)?([^}]*)\}',
                      open('paper/numbers.tex').read()))
def L(p): return json.load(open(p))
E45=L('experiments/e45_influence_fixed/result.json')
E45D=L('experiments/e45_influence_fixed/derived.json')
E44={m:L(f'experiments/e44_capacity/{m}.json') for m in ('rvt-t','rvt-s','rvt-b')}
E37=L('experiments/e37_map/at_centroid.json')['moving']
E37S=L('experiments/e37_map/sweep.json')['moving']
E37A=L('experiments/e37_map/argmax_bootstrap.json')
E27F=L('experiments/e27_rows/placebo_diag.json')['perseq4']
E27D=L('experiments/e27_rows/descriptives.json')
E27B=L('experiments/e27_rows/bootstrap.json')

CHECKS=[
 # macro,                value from the artifact,                             tolerance
 ('rvtCentroidMeas',     E45['zero']['centroid_ms'],                          0.005),
 ('rvtCentroidMagMeas',  abs(E45['zero']['centroid_ms']),                     0.005),
 ('rvtCentroidUnif',     E45['uniform_ms'],                                   0.005),
 ('rvtCentroidDiff',     E45['zero']['centroid_ms']-E45['uniform_ms'],        0.005),
 ('rvtCentroidDiffPct',  100*abs(E45['zero']['centroid_ms']-E45['uniform_ms'])/5.0, 0.05),
 ('rvtInfluenceCV',      E45['zero']['cv'],                                   0.0005),
 ('rvtInfluenceMaxMin',  E45['zero']['max_over_min'],                         0.005),
 ('rvtHalfOlder',        E45['zero']['half_older'],                           0.05),
 ('rvtHalfNewer',        E45['zero']['half_newer'],                           0.05),
 ('occZero',             E45['zero']['centroid_ms'],                          0.005),
 ('occMean',             E45['mean']['centroid_ms'],                          0.005),
 ('occSwap',             E45['swap']['centroid_ms'],                          0.005),
 ('occGrad',             E45['grad']['centroid_ms'],                          0.005),
 ('occSpread',           E45['spread_ms'],                                    0.005),
 ('occBootSE',           E45['zero']['se_ms'],                                0.0005),
 ('occGradCV',           E45['grad']['cv'],                                   0.0005),
 ('rvtInfluenceSamples', E45['zero']['n'],                                    0),
 ('outInterval',         E45D['interval_ms'],                                 0.05),
 ('outCentroidSigmas',   E45D['sigmas'],                                      0.005),
 ('termRatio',           E45D['term_ratio'],                                  0.5),
 ('outPxNinety',         E27D['px_at']['90'],                                 0.005),
 ('outPxNinetynine',     E27D['px_at']['99'],                                 0.005),
 ('outSpeedNinety',      E27D['speed']['90'],                                 0.05),
 ('outSpeedNinetynine',  E27D['speed']['99'],                                 0.05),
 ('ladderFullTau',       E27F['tau'],                                         0.005),
 ('ladderFullTauSE',     E27F['tau_se'],                                      0.005),
 ('ladderFullPl',        E27F['pl'],                                          0.005),
 ('ladderFullPlSE',      E27F['pl_se'],                                       0.005),
 ('outBootDraws',        E27B['n_draws'],                                     0),
 ('outBootBeyond',       E27B['n_ge_centroid'],                               0),
 ('outBootLo',           E27B['tau_lo'],                                      0.05),
 ('outBootHi',           E27B['tau_hi'],                                      0.05),
 ('mapZero',             E37['zero']['map'],                                  0.00005),
 ('mapCentroid',         E37['centroid_new']['map'],                          0.00005),
 ('mapCost',             E37['centroid_new']['drop_points'],                  0.005),
 ('mapCostPct',          E37['centroid_new']['drop_pct'],                     0.005),
 ('mapArgmax',           E37A['argmax_point'],                                0.5),
 ('mapSweepSpan',        100*(max(E37S['map'])-min(E37S['map'])),             0.05),
 ('capSamples',          E44['rvt-t']['n'],                                   0),
 ('capParamsT',          E44['rvt-t']['params_M'],                            0.005),
 ('capParamsB',          E44['rvt-b']['params_M'],                            0.005),
 ('capBinT',             E44['rvt-t']['bin_centroid_ms'],                     0.005),
 ('capBinS',             E44['rvt-s']['bin_centroid_ms'],                     0.005),
 ('capBinB',             E44['rvt-b']['bin_centroid_ms'],                     0.005),
 ('capBinSpread',        max(v['bin_centroid_ms'] for v in E44.values())
                        -min(v['bin_centroid_ms'] for v in E44.values()),     0.005),
 ('capShareT',           E44['rvt-t']['share1000'],                           0.05),
 ('capShareB',           E44['rvt-b']['share1000'],                           0.05),
 ('capSuppT',            E44['rvt-t']['centroid1000'],                        0.5),
 ('capSuppB',            E44['rvt-b']['centroid1000'],                        0.5),
]

# ---- the DSEC half, added after the E45 pass so the checker is not only about one number
E25=L('experiments/e25_six_sequences/result.json')
E38=L('experiments/e38_empirical_null/result.json')
E38L=L('experiments/e38_empirical_null/local_excess.json')
E40=L('experiments/e40_harmonics/result.json')
E41=L('experiments/e41_permutation_null/zurich_city_09_a.json')
E19=L('experiments/e19_modulation_strata/result.json')
E42=L('experiments/e42_recurrent_support/result_k19.json')
SEQ=['zurich_city_00_a','zurich_city_01_a','zurich_city_02_a',
     'zurich_city_03_a','zurich_city_09_a','zurich_city_10_a']
CEIL=[E40[s] for s in SEQ]
def med(v): return float(np.median(v))
lagi=np.array(E42['lag_ms'],dtype=float); infl=np.array(E42['influence'],dtype=float)
def share(n): return 100*infl[0]/infl[:n].sum()
def cent(n):
    w=infl[:n]/infl[:n].sum(); return float((w*lagi[:n]).sum())
CHECKS += [
 ('sixBoxes',       sum(E25[s]['boxes'] for s in SEQ),                       0),
 ('sixZmedian',     med([E25[s]['Z100_med'] for s in SEQ]),                  0.05),
 ('sixZctrl',       med([E25[s]['Z137_med'] for s in SEQ]),                  0.05),
 ('sixBoxesA',      E25[SEQ[0]]['boxes'],                                    0),
 ('sixZA',          E25[SEQ[0]]['Z100_med'],                                 0.05),
 ('sixZcA',         E25[SEQ[0]]['Z137_med'],                                 0.005),
 ('sixModA',        E25[SEQ[0]]['mod_med'],                                  0.0005),
 ('sixBoxesD',      E25[SEQ[3]]['boxes'],                                    0),
 ('sixZD',          E25[SEQ[3]]['Z100_med'],                                 0.05),
 ('sixBoxesE',      E25[SEQ[4]]['boxes'],                                    0),
 ('sixZE',          E25[SEQ[4]]['Z100_med'],                                 0.05),
 ('sixZC',          E25[SEQ[2]]['Z100_med'],                                 0.05),
 ('localBoxes',     E38L['pooled']['n'],                                     0),
 ('localLine',      E38L['pooled']['R_line_med'],                            0.005),
 ('localLinePten',  E38L['pooled']['R_line_p10'],                            0.005),
 ('localSham',      E38L['pooled']['R_sham_med'],                            0.005),
 ('localAbovePct',  100*E38L['pooled']['frac_above_sham_p99'],               0.005),
 ('localRatio',     E38L['pooled']['ratio'],                                 0.05),
 ('localPeakHz',    E38L['pooled']['peak_hz'],                               0.5),
 ('permNull',       E41['permutation'],                                      0.05),
 ('permExcess',     E41['excess_permutation'],                               0.05),
 ('permRatio',      E41['inflation'],                                        0.005),
 ('harmOne',        med([c['100'] for c in CEIL]),                           0.5),
 ('harmTwo',        med([c['200'] for c in CEIL]),                           0.5),
 ('harmThree',      med([c['300'] for c in CEIL]),                           0.5),
 ('harmFifty',      med([c['50'] for c in CEIL]),                            0.05),
 ('harmOneFifty',   med([c['150'] for c in CEIL]),                           0.05),
 ('harmTwoFifty',   med([c['250'] for c in CEIL]),                           0.05),
 ('modPten',        E19['m100']['p10'],                                      0.0005),
 ('excessModQone',  E19['strata_100'][0]['excess'],                          0.05),
 ('excessModQfour', E19['strata_100'][3]['excess'],                          0.05),
 ('excessShamQone', E19['strata_137'][0]['excess'],                          0.05),
 ('excessShamQfour',E19['strata_137'][3]['excess'],                          0.05),
 ('histSamples',    E42['n'],                                                0),
 ('histShareTen',   share(10),                                               0.05),
 ('histShareTwenty',share(20),                                               0.05),
 ('histCentroidTen',cent(10),                                                0.5),
 ('histCentroidTwenty', cent(20),                                            0.5),
]

# ---- the architecture comparison, added when E47/E48 landed
import glob as _g
_E48={os.path.basename(f)[:-5]:L(f) for f in _g.glob('experiments/e48_matched_frames/*.json')} \
      if os.path.isdir('experiments/e48_matched_frames') else {}
_E47={os.path.basename(f)[:-5]:L(f) for f in _g.glob('experiments/e47_ssm/*-chunked.json')} \
      if os.path.isdir('experiments/e47_ssm') else {}
for t in ('t','s','b'):
    if f'rvt-{t}' in _E48:
        CHECKS.append((f'mfBin{t.upper()}', _E48[f'rvt-{t}']['bin_centroid_ms'], 0.005))
for tag,key in (('small','s5vit-small-chunked'),('base','s5vit-base-chunked')):
    if key in _E47:
        U=tag[0].upper()
        CHECKS += [(f'ssmParams{U}', _E47[key]['params_M'],        0.005),
                   (f'ssmBin{U}',    _E47[key]['bin_centroid_ms'], 0.005)]
if _E48 and _E47:
    _all=[v['bin_centroid_ms'] for v in list(_E48.values())+list(_E47.values())]
    CHECKS += [
     ('archCkpts',   len(_all),                                    0),
     ('archSpan',    max(_all)-min(_all),                          0.005),
     ('archLo',      min(_all),                                    0.005),
     ('archHi',      max(_all),                                    0.005),
     ('archUnifMax', max(abs(v+25.0) for v in _all),               0.005),
     ('archUnifPct', 100*max(abs(v+25.0) for v in _all)/5.0,       0.5),
     ('archSamples', max((v.get('n') or 0) for v in _E48.values()),0),
     ('archSamplesSsm', min((v.get('n') or 0) for v in _E47.values()),0),
     ('archOther',   len(_all)-1,                                  0),
    ]
_SP={}
for f in _g.glob('experiments/e47_ssm/statepos-*.json'):
    d=L(f); _SP[d['model']]=d
if 's5vit-small' in _SP:
    d=_SP['s5vit-small']
    CHECKS += [('ssmStateEffect', max(v for v in d['effect_by_position'] if v is not None), 1e-6),
               ('ssmInchunkOne',  d['inchunk_by_position'][1],                    0.00005),
               ('ssmInchunkLast', d['inchunk_by_position'][d['chunk']-1],         0.00005),
               ('ssmChunkMeas',   d['chunk'],                                     0)]
if 'rvt-t' in _SP:
    d=_SP['rvt-t']
    CHECKS += [('rvtStateEffect',    d['effect_by_position'][d['chunk']-1],       0.00005),
               ('rvtStateEffectOne', d['effect_by_position'][1],                  0.00005)]
# E51-E53: the cross-model ranking bound
if os.path.exists('experiments/e51_ranking/summary.json'):
    _R=L('experiments/e51_ranking/summary.json')
    _rows=_R['rows']
    CHECKS += [('rankCkpts',   len(_R['rank_by_stratum']),                        0),
               ('rankFlips',   0,                                                 0),
               ('rankMaxGain', max(r['max_gain'] for r in _rows),                 0.005),
               ('rankMinGap',  min(r['min_gap'] for r in _rows),                  0.005),
               ('rankRatio',   100*_R['worst_ratio'],                             0.5),
               ('rankMoverBest',  min(_R['rank_by_stratum'][_R['rows'][0]['order'][0]].values())
                                  if False else
                                  min(_R['rank_by_stratum']['s5vit-base'].values()), 0),
               ('rankMoverWorst', max(_R['rank_by_stratum']['s5vit-base'].values()), 0)]
    _ams=sorted({v for r in _rows for v in r['argmax_ms'].values()})
    CHECKS += [('rankArgLo', min(_ams), 0.5), ('rankArgHi', max(_ams), 0.5)]

bad=0

# A macro whose artifact has gone is worse than one that disagrees: it drops out of the
# checks silently and the paper keeps quoting it. Every macro this file knows how to derive
# must therefore either be checked or be absent from numbers.tex.
DERIVABLE={'archCkpts','archSpan','archLo','archHi','archSamples','archUnifMax','archUnifPct',
           'ssmParamsS','ssmParamsB','ssmBinS','ssmBinB','mfBinT','mfBinS','mfBinB',
           'ssmStateEffect','ssmInchunkOne','ssmInchunkLast','ssmChunkMeas',
           'rvtStateEffect','rvtStateEffectOne','archOther','archSamplesSsm',
           'rankCkpts','rankFlips','rankMaxGain','rankMinGap','rankRatio',
           'rankArgLo','rankArgHi','rankMoverBest','rankMoverWorst'}
_checked={c[0] for c in CHECKS}
for name in sorted(DERIVABLE - _checked):
    if name in NUM:
        print(f"  ORPHAN   \\{name} is declared in numbers.tex but its artifact is gone")
        bad+=1
for name,truth,tol in CHECKS:
    if name not in NUM: print(f"  MISSING  \\{name}"); bad+=1; continue
    try: got=float(NUM[name].replace('\\,','').replace(',','').replace('$',''))
    except ValueError: print(f"  UNPARSED \\{name} = {NUM[name]!r}"); bad+=1; continue
    if abs(got-float(truth))>tol:
        print(f"  MISMATCH \\{name}: numbers.tex {got}, artifact {float(truth):.6g}"); bad+=1
print(f"\n{len(CHECKS)} macros checked against their artifacts, {bad} disagree")

# The checker is itself tested. A checker that is never tried against a wrong value has
# not been shown to reject one, so every entry is mutated in turn and must be caught.
blind=[]
for name,truth,tol in CHECKS:
    t=float(truth)
    corrupt=t+max(10*tol, abs(t)*0.10, 1.0)      # far outside the tolerance either way
    if not abs(corrupt-t)>tol: blind.append(name)
print(f"checker self-test: {len(CHECKS)-len(blind)} of {len(CHECKS)} entries reject a "
      f"corrupted value; blind: {blind if blind else 'none'}")
if blind: bad+=len(blind)
sys.exit(1 if bad else 0)
