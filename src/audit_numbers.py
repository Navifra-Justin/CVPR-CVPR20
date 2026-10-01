"""A checker for the manuscript's numbers: every macro below is re-derived from the
artifact that produced it and compared with what numbers.tex declares.

This exists because a checker that is never tested passes anything. Each entry names the
file the value must come from and the expression that reads it, so a macro edited by hand
without a corresponding run fails here rather than in review.
"""
import json, re, sys, os, numpy as np

# Every path below -- numbers.tex and every experiments/ artifact -- is relative, so the
# population this checker reads used to depend on the caller's working directory: run from
# anywhere but the repository root it died in open(), and run from a tree where only some
# artifacts resolved it would have checked a subset. The root is taken from this file's own
# location and made the working directory, so the same command reads the same population
# from any cwd.
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)

# The live submission is submission_2027/paper/latex; the top-level paper/ tree
# is a stale draft whose numbers.tex differs from the submitted one, so this
# checker used to validate macros that are not the ones being submitted.
# PAPER_DIR overrides the directory for testing against a copy.
PAPER_DIR = os.environ.get('PAPER_DIR') or 'submission_2027/paper/latex'
if not os.path.isabs(PAPER_DIR):
    PAPER_DIR = os.path.join(REPO, PAPER_DIR)
_NUMTEX = os.path.join(PAPER_DIR, 'numbers.tex')
if not os.path.exists(_NUMTEX):
    sys.exit(f'audit_numbers: no numbers.tex at {_NUMTEX}; no macro would be checked, '
             'and an unread manuscript is not a manuscript whose numbers agree')
NUM = dict(re.findall(r'\\newcommand\{\\([A-Za-z]+)\}\{(?:\\ensuremath\{)?([^}]*)\}',
                      open(_NUMTEX).read()))
if not NUM:
    sys.exit(f'audit_numbers: {_NUMTEX} declares 0 macros; the population is empty and an '
             'empty population must not become a clean verdict')
def L(p): return json.load(open(p))
E45=L('experiments/e45_influence_fixed/result.json')
E45D=L('experiments/e45_influence_fixed/derived.json')
E44={m:L(f'experiments/e44_capacity/{m}.json') for m in ('rvt-t','rvt-s','rvt-b')}
E37=L('experiments/e37_map/at_centroid.json')['moving']
E37S=L('experiments/e37_map/sweep.json')['moving']
E37A=L('experiments/e37_map/argmax_bootstrap.json')
E27F=L('experiments/e27_rows/placebo_diag.json')['perseq4']
E62=L('experiments/e27_rows/association.json')
E42FC=L('experiments/e42_recurrent_support/fill_control.json')
E63=L('experiments/e63_port/parity.json')
E64=L('experiments/e45_influence_fixed/seqboot.json')
E62G=E62['rows']['greedy_0.3']['reported']; E62C=E62['rows']['center_1.5']['reported']
E27D=L('experiments/e27_rows/descriptives.json')
E27B=L('experiments/e27_rows/bootstrap.json')
E56R=L('experiments/e56_resolving/resolving.json')
E56S=L('experiments/e56_resolving/rankse.json')
E58A=L('experiments/e58_chunkpos/allbox.json')
E58I=L('experiments/e58_chunkpos/invariant.json')
E58P=L('experiments/e58_chunkpos/perm.json')
E60=L('experiments/e60_shift/paired.json')['models']
E60F=L('experiments/e60_shift/figframe.json')
# One \ssmPairedN serves both arms only if they pair the same frames.
assert E60['small']['n']==E60['base']['n'], 'E60 arms pair different frame counts'
E59T=L('experiments/e42_recurrent_support/tail.json')
E56C=L('experiments/e56_resolving/collapse.json')
E57C={d['name']:d for d in L('experiments/e56_resolving/composition.json')}
_QB=min(E56C['cv_fixed_quantile'],key=lambda k:E56C['cv_fixed_quantile'][k]['0.05'])
_MQ=E56C['matched_quantile']; _TC=E56C['tail_cost']
_N=E56R['noise']['all moving']
_SED=[_N[m]['se_dmap_pt'] for m in _N]; _SEM=[_N[m]['se_map_pt'] for m in _N]
_RP=[_N[m]['resolve_paired_ms'] for m in _N]; _RA=[_N[m]['resolve_absolute_ms'] for m in _N]
_TIGHT=min(E56S['pairs']['every labelled box'], key=lambda d: d['gap'])
_RVT=('rvt-t','rvt-s','rvt-b')
# Raw full-minus-short mAP per checkpoint, and the placebo-controlled version of it. The
# control for an RVT row leaves that row out, so a placebo is never its own control.
_RAW={m:(v['full']-v['short']) for m,v in E58A['point'].items()}
def _NET(m):
    others=[j for j in _RVT if j!=m] if m in _RVT else list(_RVT)
    return _RAW[m]-sum(_RAW[j] for j in others)/len(others)
_CS=E58I['conf_by_position']['s5vit-small']

CHECKS=[
 # --- E56: what timing difference the score separates from its sampling uncertainty.
 ('seDmapLo',           min(_SED),                                           0.0005),
 ('seDmapHi',           max(_SED),                                           0.0005),
 ('seMapLo',            min(_SEM),                                           0.005),
 ('seMapHi',            max(_SEM),                                           0.005),
 ('resPairedLo',        min(_RP),                                            0.05),
 ('resPairedHi',        max(_RP),                                            0.05),
 ('effTauLo',           min(_N[m]['effect_at_tau_pt'] for m in _N),          0.0005),
 ('effTauHi',           max(_N[m]['effect_at_tau_pt'] for m in _N),          0.0005),
 ('twoSeDmapLo',        2*min(_SED),                                         0.0005),
 ('twoSeDmapHi',        2*max(_SED),                                         0.0005),
 ('effTauResolved',     sum(_N[m]['effect_at_tau_pt'] > 2*_N[m]['se_dmap_pt'] for m in _N), 0.5),
 ('resAbsLo',           min(_RA),                                            0.5),
 ('resAbsHi',           max(_RA),                                            0.5),
 ('dstarAll',           E56R['strata']['all moving']['dstar_ms'],            0.05),
 ('dstarAllTau',        E56R['strata']['all moving']['dstar_over_tau'],      0.005),
 ('dstarMid',           E56R['strata']['25-50 px/s']['dstar_ms'],            0.05),
 ('dstarMidTau',        E56R['strata']['25-50 px/s']['dstar_over_tau'],      0.005),
 # --- E56d: whether the published ordering survives the benchmark's own resampling.
 ('rankHoldBox',        100*E56S['order_preserved']['every labelled box'],   0.05),
 ('rankHoldMov',        100*E56S['order_preserved']['moving subset'],        0.05),
 ('rankFlipMax',        _TIGHT['p_flip'],                                    0.005),
 ('rankGapMin',         _TIGHT['gap'],                                       0.0005),
 ('rankGapMinSE',       _TIGHT['se'],                                        0.005),
 # --- E56e: which summary of the composition sets the resolution, and its price.
 ('collapseCVraw',      E56C['cv_no_rescaling']['0.05'],                     0.005),
 ('collapseCVmed',      E56C['cv_fixed_quantile']['50']['0.05'],             0.005),
 ('collapseQbest',      float(_QB),                                          0.5),
 ('collapseCVbest',     E56C['cv_fixed_quantile'][_QB]['0.05'],              0.005),
 ('collapseCV',         _MQ['0.05']['cv3'],                                  0.0005),
 ('collapseD',          _MQ['0.05']['d_star'],                               0.00005),
 ('collapseDsd',        _MQ['0.05']['d_sd'],                                 0.00005),
 ('collapseIoU',        _MQ['0.05']['iou_at_d'],                             0.0005),
 ('collapseCVten',      _MQ['0.10']['cv3'],                                  0.005),
 ('collapseCVqtr',      _MQ['0.25']['cv3'],                                  0.005),
 ('tailGainTop',        _TC['>50 px/s']['resolution_gain'],                   0.005),
 ('tailSeTop',          _TC['>50 px/s']['se_inflation'],                      0.005),
 ('tailNetTop',         _TC['>50 px/s']['net'],                               0.005),
 ('tailNetMid',         _TC['25-50 px/s']['net'],                             0.005),
 ('stNtop',             E56C['r_summary']['>50 px/s']['n'],                   0.5),
 ('rGenAll',            E57C['Gen1 (all moving)']['r_median'],                0.0005),
 ('rDsecTrain',         E57C['DSEC-Det (train)']['r_median'],                 0.005),
 ('ddRatioMed',         E57C['DSEC-Det (train)']['ratio_to_gen1'],            0.05),
 ('ddBoxesTrain',       E57C['DSEC-Det (train)']['n'],                        0.5),
 ('qGenAll',            E57C['Gen1 (all moving)']['r_p95'],                   0.005),
 ('qDsecTrain',         E57C['DSEC-Det (train)']['r_p95'],                    0.005),
 ('qDsecRatio',         E57C['DSEC-Det (train)']['ratio_q95'],                0.005),
 ('qDsecNet',           E57C['DSEC-Det (train)']['net_of_n'],                 0.05),
 # --- E58: the support the released streaming evaluation actually hands a detection.
 ('chunkDidBase',       -E58A['did']['s5vit-base'],                          0.005),
 ('chunkDidBaseSE',     E58A['boot']['s5vit-base']['se'],                    0.005),
 ('chunkDidBaseZ',      -E58A['did']['s5vit-base']/E58A['boot']['s5vit-base']['se'], 0.05),
 ('chunkDidSmall',      -E58A['did']['s5vit-small'],                         0.005),
 ('chunkDidSmallSE',    E58A['boot']['s5vit-small']['se'],                   0.005),
 ('chunkDidSmallZ',     -E58A['did']['s5vit-small']/E58A['boot']['s5vit-small']['se'], 0.05),
 ('chunkPlaceboMax',    max(abs(E58A['did'][m]) for m in _RVT),              0.005),
 # The raw full-minus-short difference and the same difference net of the placebo trend
 # are separate columns of the supplement's chunk table and must not be interchanged: an
 # RVT row is controlled by the mean of the other two, an SSM row by the mean of all three.
 ('chunkRawT',          100*_RAW['rvt-t'],                                   0.005),
 ('chunkRawS',          100*_RAW['rvt-s'],                                   0.005),
 ('chunkRawB',          100*_RAW['rvt-b'],                                   0.005),
 ('chunkNetT',          100*_NET('rvt-t'),                                   0.005),
 ('chunkNetS',          100*_NET('rvt-s'),                                   0.005),
 ('chunkNetB',          100*_NET('rvt-b'),                                   0.005),
 # --- E60: the same-frame chunk-boundary intervention. No control model, no parallel
 # trends: the identical frame, ground truth and weights, differing only in the history
 # the shifted streaming protocol hands it.
 ('ssmPairedN',         E60['small']['n'],                                   0.5),
 ('ssmPairedMapVelBase',    E60['base']['map_vel_boot']['obs'],              0.005),
 ('ssmPairedMapVelBaseSE',  E60['base']['map_vel_boot']['se'],               0.005),
 ('ssmPairedMapVelSmall',   E60['small']['map_vel_boot']['obs'],             0.005),
 ('ssmPairedMapVelSmallSE', E60['small']['map_vel_boot']['se'],              0.005),
 ('ssmPairedMapAllBase',    E60['base']['map_all_boot']['obs'],              0.005),
 ('ssmPairedMapAllSmall',   E60['small']['map_all_boot']['obs'],             0.005),
 ('ssmPairedConfBase',      E60['base']['conf_boot']['obs'],                 0.0005),
 ('ssmPairedConfBaseSE',    E60['base']['conf_boot']['se'],                  0.0005),
 ('ssmPairedConfSmall',     E60['small']['conf_boot']['obs'],                0.0005),
 ('ssmPairedConfSmallSE',   E60['small']['conf_boot']['se'],                 0.0005),
 ('ssmPairedDpfBase',       -E60['base']['dpf_boot']['obs'],                 0.005),
 ('ssmPairedDpfSmall',      -E60['small']['dpf_boot']['obs'],                0.005),
 ('ssmPairedShift',     5,                                                   0.5),
 ('ssmPairedB',          300,                                                 0.5),
 # The qualitative pair: the frame drawn, and the population it was selected from, so the
 # caption cannot describe a picked frame as if it were the average one.
 ('pairedFigLabels',      E60F['n_gt'],                                       0.5),
 ('pairedFigMatchShort',  E60F['short']['matched'],                           0.5),
 ('pairedFigMatchFull',   E60F['full']['matched'],                            0.5),
 ('pairedFigUnmatchShort',E60F['short']['unmatched'],                         0.5),
 ('pairedFigUnmatchFull', E60F['full']['unmatched'],                          0.5),
 ('pairedFigShow',        E60F['show'],                                       0.005),
 ('pairedFigMeanMatchShort', E60F['population']['matched'][0],                0.005),
 ('pairedFigMeanMatchFull',  E60F['population']['matched'][1],                0.005),
 ('pairedFigMoreMatched', 100*E60F['population']['frac_more_matched'],        0.05),
 ('pairedFigFewerMatched',100*E60F['population']['frac_fewer_matched'],       0.05),
 ('ssmPairedMapAllBaseSE',  E60['base']['map_all_boot']['se'],                0.005),
 ('ssmPairedMapAllSmallSE', E60['small']['map_all_boot']['se'],               0.005),
 ('ssmPairedConfTpBase',    E60['base']['conf_tp_boot']['obs'],               0.0005),
 ('ssmPairedConfTpBaseSE',  E60['base']['conf_tp_boot']['se'],                0.0005),
 ('ssmPairedConfTpSmall',   E60['small']['conf_tp_boot']['obs'],              0.0005),
 ('ssmPairedConfTpSmallSE', E60['small']['conf_tp_boot']['se'],               0.0005),
 ('ssmPairedDpfBaseSE',     E60['base']['dpf_boot']['se'],                    0.005),
 ('ssmPairedDpfSmallSE',    E60['small']['dpf_boot']['se'],                   0.005),
 ('ssmPairedMapVelBaseZ',   E60['base']['map_vel_boot']['z'],                 0.05),
 ('ssmPairedMapVelSmallZ',  E60['small']['map_vel_boot']['z'],                0.05),
 ('ssmPairedConfBaseZ',     E60['base']['conf_boot']['z'],                    0.05),
 ('ssmPairedConfSmallZ',    E60['small']['conf_boot']['z'],                   0.05),
 # The two designs agree on S5-B: |same-frame paired - placebo-differenced|, mAP points.
 ('ssmPairedAgreeBase',  abs(E60['base']['map_vel_boot']['obs']-(-E58A['did']['s5vit-base'])), 0.005),
 ('chunkPlaceboZ',      max(abs(E58A['did'][m])/E58A['boot'][m]['se'] for m in _RVT), 0.005),
 ('chunkGapBase',       -E58A['pooled_gap']['s5vit-base'],                   0.005),
 ('chunkGapSmall',      -E58A['pooled_gap']['s5vit-small'],                  0.005),
 ('chunkShortBase',     100*E58A['point']['s5vit-base']['short'],            0.0006),
 ('chunkFullBase',      100*E58A['point']['s5vit-base']['full'],             0.0006),
 ('chunkRelBase',       100*E58A['point']['s5vit-base']['pooled'],           0.05),
 ('chunkPermB',         200,                                          0.5),
 ('chunkPermSd',        max(E58P['s5vit-base']['null_sd'],
                            E58P['s5vit-small']['null_sd']),          0.005),
 ('chunkPermZBase',     abs(E58P['s5vit-base']['z']),                 0.05),
 ('chunkPermZSmall',    abs(E58P['s5vit-small']['z']),                0.05),
 ('chunkPermPlaceboZ',  max(abs(E58P[k]['z']) for k in _RVT),         0.005),
 ('chunkPermP',         E58P['s5vit-base']['p'],                      0.0005),
 ('chunkRiseBase',      100*(E58A['point']['s5vit-base']['full']
                            -E58A['point']['s5vit-base']['short']),   0.005),
 ('chunkRiseSmall',     100*(E58A['point']['s5vit-small']['full']
                            -E58A['point']['s5vit-small']['short']),  0.005),
 ('chunkRiseRvt',       max(abs(E58A['point'][k]['full']
                                -E58A['point'][k]['short'])*100 for k in _RVT), 0.005),
 ('chunkConfOne',       _CS[0],                                              0.0005),
 ('chunkConfFull',      _CS[16],                                             0.0005),
 ('chunkConfPct',       100*(_CS[16]/_CS[0]-1),                              0.05),
 # --- E59: the influence tail, and the non-existence of the recurrent centroid.
 ('aFitShort',          E59T['a_fit_1_9'],                                   0.0005),
 ('chunkShortSmall',    100*E58A['point']['s5vit-small']['short'],           0.0006),
 ('chunkFullSmall',     100*E58A['point']['s5vit-small']['full'],            0.0006),
 ('chunkRelSmall',      100*E58A['point']['s5vit-small']['pooled'],          0.05),
 ('chunkShortT',        100*E58A['point']['rvt-t']['short'],                 0.0006),
 ('chunkFullT',         100*E58A['point']['rvt-t']['full'],                  0.0006),
 ('chunkShortS',        100*E58A['point']['rvt-s']['short'],                 0.0006),
 ('chunkFullS',         100*E58A['point']['rvt-s']['full'],                  0.0006),
 ('chunkShortB',        100*E58A['point']['rvt-b']['short'],                 0.0006),
 ('chunkFullB',         100*E58A['point']['rvt-b']['full'],                  0.0006),
 ('chunkDidT',          E58A['did']['rvt-t'],                                0.005),
 ('chunkSeT',           E58A['boot']['rvt-t']['se'],                         0.005),
 ('chunkDidS',          E58A['did']['rvt-s'],                                0.005),
 ('chunkSeS',           E58A['boot']['rvt-s']['se'],                         0.005),
 ('chunkDidB',          E58A['did']['rvt-b'],                                0.005),
 ('chunkSeB',           E58A['boot']['rvt-b']['se'],                         0.005),
 ('tailExp',            E59T['a_all'],                                       0.0005),
 ('tailExpSE',          E59T['a_se'],                                        0.0005),
 ('tailExpLo',           E59T['a_lo'],                                        0.0005),
 ('tailExpHi',           E59T['a_hi'],                                        0.0005),
 ('tailRatio',          E59T['ratio'],                                       0.0005),
 ('tailRatioLo',        E59T['ratio_lo'],                                    0.0005),
 ('tailRatioHi',        E59T['ratio_hi'],                                    0.0005),
 ('tailOutside',        100*E59T['outside_current_window'],                  0.05),
 ('tailRmsPower',       E59T['rmsz_power'],                                  0.05),
 ('tailRmsExp',         E59T['rmsz_exp'],                                    0.05),
 ('tailRmsRatio',       E59T['rmsz_exp']/E59T['rmsz_power'],                 0.05),
 ('histSwapRatioLo',     E42FC['per_lag']['0']['ratio'],                      0.005),
 ('histSwapRatioHi',     E42FC['per_lag']['19']['ratio'],                     0.005),
 ('histDecayZero',       E42FC['decay_zero'],                                 0.05),
 ('histDecaySwap',       E42FC['decay_swap'],                                 0.05),
 ('occSeqs',             E64['fills']['zero']['n_seq'],                       0.5),
 ('occSeqCiLo',          E64['fills']['zero']['boot_lo'],                     0.005),
 ('occSeqCiHi',          E64['fills']['zero']['boot_hi'],                     0.005),
 ('occSeqSE',            E64['fills']['zero']['boot_se'],                     0.005),
 ('occSeqWidest',        E64['widest_ci_ms'],                                 0.005),
 ('occSeqLoo',           E64['loo_span_ms']/2,                                0.005),
 ('occPerSeqLo',         E64['fills']['zero']['per_seq_lo'],                  0.005),
 ('occPerSeqHi',         E64['fills']['zero']['per_seq_hi'],                  0.005),
 ('portEvalGap',         E63['max_gap'],                                      0.0005),
 ('portParamDev',        E63['max_params_dev'],                               0.0005),
 ('portSeqs',            E63['val_sequences'],                                0.5),
 ('portApT',             E63['rows']['rvt-t']['coco_ap'],                     0.005),
 ('portApOwnT',          E63['rows']['rvt-t']['own_ap'],                      0.005),
 ('portApFifty',         E63['rows']['rvt-t']['coco_ap50'],                   0.05),
 ('assocRules',         E62['n_rules'],                                      0.5),
 ('assocLo',            E62['span_ms'][0],                                   0.005),
 ('assocHi',            E62['span_ms'][1],                                   0.005),
 ('assocSpread',        E62['spread_ms'],                                    0.005),
 ('assocSE',            E62['median_se_ms'],                                 0.005),
 ('assocGate',          E62G['tau_ms'],                                      0.005),
 ('assocGateSE',        E62G['tau_se_ms'],                                   0.005),
 ('assocGateN',         E62G['n'],                                           0.5),
 ('assocFree',          E62C['tau_ms'],                                      0.005),
 ('assocFreeSE',        E62C['tau_se_ms'],                                   0.005),
 ('assocFreeN',         E62C['n'],                                           0.5),
 ('assocDelta',         abs(E62C['tau_ms']-E62G['tau_ms'])/E62G['tau_se_ms'],0.005),
 ('assocGateVsTable',   abs(E62G['tau_ms']-float(NUM['ladderFullTau'].replace('$','')))/E62G['tau_se_ms'], 0.005),
 ('assocMinLo',         E62['span_minimal_ms'][0],                           0.005),
 ('assocMinHi',         E62['span_minimal_ms'][1],                           0.005),
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
# One value per released checkpoint, each driven the way its own release drives it,
# which is what the manuscript's sentence counts. E47d added rvt-{t,s,b}-chunked.json
# beside the SSM rows: those are the same three RVT checkpoints pushed through the SSM's
# chunked instrument as E58's control, not further checkpoints, so counting the directory
# would report each of them twice and make \archCkpts read 8.
_E47SSM={k:v for k,v in _E47.items() if k.startswith('s5vit')}
if _E48 and _E47SSM:
    _all=[v['bin_centroid_ms'] for v in list(_E48.values())+list(_E47SSM.values())]
    CHECKS += [
     ('archCkpts',   len(_all),                                    0),
     ('archSpan',    max(_all)-min(_all),                          0.005),
     ('archLo',      min(_all),                                    0.005),
     ('archHi',      max(_all),                                    0.005),
     ('archUnifMax', max(abs(v+25.0) for v in _all),               0.005),
     ('archUnifPct', 100*max(abs(v+25.0) for v in _all)/5.0,       0.5),
     ('archSamples', max((v.get('n') or 0) for v in _E48.values()),0),
     ('archSamplesSsm', min((v.get('n') or 0) for v in _E47SSM.values()),0),
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

if os.path.exists('experiments/e37_map/stratum_table.json'):
    _E55=L('experiments/e37_map/stratum_table.json')
    _sl=_E55['slow, |v| < 10']; _md=_E55['10 <= |v| < 25']
    _hg=_E55['25 <= |v| < 50']; _tp=_E55['fast, |v| >= 50']; _am=_E55['all moving']
    CHECKS += [
     ('stShareSlow', _sl['share_pct'],      0.05), ('stShareMid', _md['share_pct'],  0.05),
     ('stShareHigh', _hg['share_pct'],      0.05), ('stShareTop', _tp['share_pct'],  0.05),
     ('stSpdSlow',   _sl['speed_median'],   0.05), ('stSpdMid',   _md['speed_median'],0.05),
     ('stSpdHigh',   _hg['speed_median'],   0.05), ('stSpdTop',   _tp['speed_median'],0.05),
     ('stPxSlow',    _sl['disp_px_median'], 0.005),('stPxMid',    _md['disp_px_median'],0.005),
     ('stPxHigh',    _hg['disp_px_median'], 0.005),('stPxTop',    _tp['disp_px_median'],0.005),
     ('stCostSlow',  _sl['cost_points'],    0.005),('stCostMid',  _md['cost_points'], 0.005),
     ('stCostHigh',  _hg['cost_points'],    0.005),('stCostTop',  _tp['cost_points'], 0.005),
     ('stSpanAll',   _am['span_points'],    0.005),
     ('stNmoving',   _am['n'],              0),
    ]

# ---- the real-image figures, added when they entered the paper
if os.path.exists('experiments/e37_map/fig6_stats.json'):
    _F6=L('experiments/e37_map/fig6_stats.json')
    CHECKS += [('sweepRealFast', _F6['fastest_px_s'], 0.05),
               ('sweepRealPx',   _F6['disp_px'],      0.005)]
if os.path.exists('experiments/e00_exposure_survey/fig7_stats.json'):
    _F7=L('experiments/e00_exposure_survey/fig7_stats.json')
    CHECKS += [('ceilVarNight', _F7['zurich_city_09_a']['rate_max_over_min'], 0.05),
               ('ceilVarDay',   _F7['interlaken_00_c']['rate_max_over_min'],  0.05)]

# E60 read at four shift amounts. dose.json is written by src/e60_dose.py, which also
# gates the two properties the ladder depends on: every treated arm scores the same frames,
# and the SHIFT = 0 arm is exactly inert. The +16 row is the headline shift and is already
# covered by the \ssmPairedMapVel* entries above, so only the two intermediate doses get
# their own macros and the null arm gets one shared zero.
_DOSEWORD={6:'Six', 11:'Eleven', 16:'Sixteen'}
if os.path.exists('experiments/e60_shift/dose.json'):
    _DOSE=L('experiments/e60_shift/dose.json')
    CHECKS.append(('ssmDoseN', _DOSE['n_paired'], 0))
    for _r in _DOSE['rows']:
        if _r['gained']==0:
            CHECKS += [('ssmDoseNull', abs(_r['base'])+abs(_r['small']), 1e-12)]
            continue
        if _r['gained'] not in _DOSEWORD:
            continue
        # The +16 rung is the amount E60 already reported, so it is already named by the
        # headline macros. Checking it under a second name would put the same measurement
        # in numbers.tex twice and let the two copies drift; pointing this rung at the
        # existing names instead makes the audit confirm that dose.json and the immutable
        # paired.json agree on the rung they share.
        if _r['gained']==16:
            CHECKS += [('ssmPairedMapVelBase',    _r['base'],     0.005),
                       ('ssmPairedMapVelBaseSE',  _r['base_se'],  0.005),
                       ('ssmPairedMapVelSmall',   _r['small'],    0.005),
                       ('ssmPairedMapVelSmallSE', _r['small_se'], 0.005)]
            continue
        _w=_DOSEWORD[_r['gained']]
        CHECKS += [(f'ssmDoseBase{_w}',    _r['base'],     0.005),
                   (f'ssmDoseBase{_w}SE',  _r['base_se'],  0.005),
                   (f'ssmDoseSmall{_w}',   _r['small'],    0.005),
                   (f'ssmDoseSmall{_w}SE', _r['small_se'], 0.005)]

# E65: the same chunk-boundary shift applied to RVT, which carries its recurrent state
# across chunk boundaries, in two regimes. `carry` is the released streaming evaluation and
# is the arm the Sec. 5 difference-in-differences control assumes to be insensitive to the
# boundary; `reset` drops the state at every chunk start and is the positive control that
# proves the treatment reaches the model. src/e65_regress_check.py gates the wiring before
# this file ever sees the json: the SHIFT = 0 carry dump must be bit-identical to the
# e51 release dump, and the reset dump must differ from it.
if os.path.exists('experiments/e65_rvt_boundary/paired-shift5.json'):
    _E65=L('experiments/e65_rvt_boundary/paired-shift5.json')
    _A=_E65['arms']
    _n65={k:v['n'] for k,v in _A.items()}
    CHECKS += [('rvtBoundN',     next(iter(_n65.values())), 0),
               ('rvtBoundShift', _E65['shift'], 0),
               ('rvtBoundB',     _E65['B'],     0),
               ('rvtBoundPermR', _E65['rperm'], 0)]
    for _t,_lab in (('s','S'),('b','B')):
        for _reg,_rlab in (('carry','Carry'),('reset','Reset')):
            _k=f'{_t}-{_reg}'
            if _k not in _A: continue
            _d=_A[_k]['map_vel_boot']
            CHECKS += [(f'rvtBound{_rlab}{_lab}',    _d['obs'], 0.005),
                       (f'rvtBound{_rlab}{_lab}SE',  _d['se'],  0.005),
                       (f'rvtBound{_rlab}{_lab}Z',   _d['z'],   0.05),
                       (f'rvtBound{_rlab}{_lab}All', _A[_k]['map_all_boot']['obs'], 0.005)]
    _c65=[_A[_k]['map_vel_boot']['obs'] for _k in _A if _k.endswith('-carry')]
    _r65=[_A[_k]['map_vel_boot']['obs'] for _k in _A if _k.endswith('-reset')]
    _p65=[_A[_k]['perm_null'] for _k in _A]
    # The supplement quotes the size of the bit-identity check, so the counts are read from
    # the same release dumps e65_regress_check.py compares against rather than transcribed.
    for _t,_lab in (('s','S'),('b','B')):
        _rp=f'experiments/e51_ranking/dets-rvt-{_t}.npz'
        if os.path.exists(_rp):
            import numpy as _np
            CHECKS += [(f'rvtBoundDets{_lab}', int(_np.load(_rp)['det'].shape[0]), 0)]
    CHECKS += [('rvtBoundCarryMax', max(abs(_x) for _x in _c65), 0.005),
               ('rvtBoundResetMin', min(_r65),                   0.005),
               ('rvtBoundPermMax',  max(abs(_p['mean']) for _p in _p65), 0.0005),
               ('rvtBoundPermSd',   max(_p['sd'] for _p in _p65),        0.005)]

# E66 Support-Conditioned AP: five released checkpoints scored under exactly H windows of
# history. Every number is re-read from results.json (and, for the audit-trail counts, from the
# verify logs) with its own expression, and the ordering statements the prose makes are
# asserted here rather than trusted: a changed ordering must break this file, not the review.
_E66F='experiments/e66_fixedH/results.json'
_FH_DERIVED=set()
if os.path.exists(_E66F):
    import re as _re
    _R=L(_E66F)
    _MS=['rvt-t','rvt-s','rvt-b','s5vit-small','s5vit-base']
    _MC=dict(zip(_MS,('Rt','Rs','Rb','Ss','Sb')))
    _CC={'pooled':'Pool','H1':'HOne','H5':'HFive','H10':'HTen','H21':'HTwentyone'}
    assert _R['models']==_MS and list(_R['cols'])==list(_CC), 'E66 model or column set changed'
    _E66=[('fhNAll',_R['n_frames'],0),('fhNCommon',_R['n_common'],0),('fhNExcl',_R['n_excluded'],0),
          ('fhNSeq',_R['n_seq_common'],0),('fhB',_R['B'],0)]
    assert _R['n_frames']-_R['n_common']==_R['n_excluded']
    for _m in _MS:
        for _c,_cc in _CC.items():
            _E66+=[(f'fhMap{_MC[_m]}{_cc}',_R['map'][_m][_c],0.005),
                   (f'fhMap{_MC[_m]}{_cc}Lo',_R['ci'][_m][_c][0],0.005),
                   (f'fhMap{_MC[_m]}{_cc}Hi',_R['ci'][_m][_c][1],0.005)]
        _E66+=[(f'fhMap{_MC[_m]}All',_R['pooled_all_frames'][_m],0.005)]
    for _c,_cc in _CC.items():
        _E66+=[(f'fhTau{_cc}',_R['kendall_vs_pooled'][_c],0.005),
               (f'fhRepro{_cc}',100*_R['rank_repro'][_c],0.05)]
    _PAIRS=[(a,b) for i,a in enumerate(_MS) for b in _MS[i+1:]]
    for _a,_b in _PAIRS:
        _g=_R['gap'][f'{_a}-{_b}']
        for _c,_cc in _CC.items():
            # a gap is re-derived from the two models' own mAP, not only read from the stored gap
            assert abs(_g[_c][0]-(_R['map'][_a][_c]-_R['map'][_b][_c]))<1e-9, (_a,_b,_c)
            _E66+=[(f'fhGap{_MC[_a]}{_MC[_b]}{_cc}',_g[_c][0],0.005),
                   (f'fhGap{_MC[_a]}{_MC[_b]}{_cc}Lo',_g[_c][1],0.005),
                   (f'fhGap{_MC[_a]}{_MC[_b]}{_cc}Hi',_g[_c][2],0.005)]
        _hp=[_R['map'][_a][c]-_R['map'][_b][c] for c in ('H1','H5','H10','H21')]
        _E66+=[(f'fhGap{_MC[_a]}{_MC[_b]}Min',min(_hp),0.005),(f'fhGap{_MC[_a]}{_MC[_b]}Max',max(_hp),0.005)]
    _PV={}
    for _m in _MS:
        _t=open(f'experiments/e66_fixedH/verify-{_m}.log').read()
        _x=_re.search(r'changed the output in (\d+)/(\d+) probed cells',_t)
        _PV[_m]=(int(_x.group(1)),int(_x.group(2)))
        for _need in ('[PASS] (4)(5) effective support count == H_forced in every cell',
                      '[PASS] (4) first window read == ri-H_forced+1 in every cell',
                      '[PASS] (3) weights sha256 unchanged'):
            assert _need in _t, f'verify-{_m}.log lost the line {_need!r}'
    _E66+=[('fhProbeN',_PV['rvt-t'][1],0),('fhProbeHit',_PV['rvt-s'][0],0),('fhProbeHitT',_PV['rvt-t'][0],0)]
    assert {v[1] for v in _PV.values()}=={_PV['rvt-t'][1]} and \
           {_PV[m][0] for m in _MS if m!='rvt-t'}=={_PV['rvt-s'][0]}, 'probe counts differ across checkpoints'
    _fd=[float(x) for x in _re.findall(r'so far ([0-9.e+-]+)',open('experiments/e66_fixedH/eval.log').read())]
    _E66+=[('fhFastDiff',max(_fd)*1e6,0.005)]
    # --- statements the prose makes about orderings and signs ---
    _O=_R['order']
    assert _O['pooled']==['rvt-b','rvt-s','s5vit-base','rvt-t','s5vit-small'], 'pooled ordering changed'
    assert all(_O[h][0]=='s5vit-base' for h in ('H1','H5','H10','H21')), 'S5-B is no longer first at every H'
    assert all(_O[h]!=_O['pooled'] for h in ('H1','H5','H10','H21')), 'an H ordering equals the pooled one'
    _gp=lambda a,b,c: _R['gap'][f'{a}-{b}'][c]
    _opp=lambda g,h: g[1]>0>h[2] or h[1]>0>g[2]       # intervals exclude zero on opposite sides
    _flip=[(a,b) for a,b in _PAIRS if _opp(_gp(a,b,'pooled'),_gp(a,b,'H1'))]
    assert _flip==[('rvt-t','s5vit-small'),('rvt-s','s5vit-small'),('rvt-b','s5vit-base')], _flip
    for _a,_b in (('rvt-s','s5vit-base'),('rvt-t','s5vit-base')):
        assert _gp(_a,_b,'pooled')[1]<0<_gp(_a,_b,'pooled')[2], 'pooled interval no longer covers zero'
        assert all(_gp(_a,_b,h)[2]<0 for h in ('H1','H5','H10','H21')), 'a fixed-H gap interval reaches zero'
    assert all(_gp('rvt-b','s5vit-base',h)[2]<0 for h in ('H1','H5','H10','H21'))
    for _m in ('rvt-t','rvt-s','rvt-b'):
        assert _R['map'][_m]['pooled']>max(_R['map'][_m][h] for h in ('H1','H5','H10','H21')), _m
    for _m in ('s5vit-small','s5vit-base'):
        assert _R['map'][_m]['H1']<_R['map'][_m]['pooled']<_R['map'][_m]['H21'], _m
    assert _O['H1']==['s5vit-base','s5vit-small','rvt-b','rvt-s','rvt-t']
    assert _O['H5']==['s5vit-base','rvt-b','s5vit-small','rvt-s','rvt-t']
    assert _O['H10']==['s5vit-base','rvt-b','s5vit-small','rvt-s','rvt-t']
    assert _O['H21']==['s5vit-base','rvt-b','rvt-s','s5vit-small','rvt-t']
    _tau=[_R['kendall_vs_pooled'][h] for h in ('H1','H5','H10','H21')]
    assert min(_tau)==_tau[0] and max(_tau)==_tau[-1], 'abstract names tau(H=1) and tau(H=21) as the range ends'
    _gap=lambda a,b,c: _R['gap'][f'{a}-{b}'][c]
    assert _gap('rvt-s','s5vit-small','H21')[1]<0<_gap('rvt-s','s5vit-small','H21')[2]
    _FH_DERIVED={c[0] for c in _E66}
    CHECKS+=_E66
else:
    _FH_DERIVED={n for n in NUM if n.startswith('fh')}   # artifact gone: each such macro is an ORPHAN

bad=0
if not CHECKS:
    sys.exit(f'audit_numbers: 0 macros to check against {_NUMTEX}; nothing was verified, '
             'and an empty population must not become a clean verdict')

# A macro whose artifact has gone is worse than one that disagrees: it drops out of the
# checks silently and the paper keeps quoting it. Every macro this file knows how to derive
# must therefore either be checked or be absent from numbers.tex.
DERIVABLE={'archCkpts','archSpan','archLo','archHi','archSamples','archUnifMax','archUnifPct',
           'ssmParamsS','ssmParamsB','ssmBinS','ssmBinB','mfBinT','mfBinS','mfBinB',
           'ssmStateEffect','ssmInchunkOne','ssmInchunkLast','ssmChunkMeas',
           'rvtStateEffect','rvtStateEffectOne','archOther','archSamplesSsm',
           'rankCkpts','rankFlips','rankMaxGain','rankMinGap','rankRatio',
           'rankArgLo','rankArgHi','rankMoverBest','rankMoverWorst',
           'stShareSlow','stShareMid','stShareHigh','stShareTop',
           'stSpdSlow','stSpdMid','stSpdHigh','stSpdTop',
           'stPxSlow','stPxMid','stPxHigh','stPxTop',
           'stCostSlow','stCostMid','stCostHigh','stCostTop',
           'stSpanAll','stNmoving',
           'sweepRealFast','sweepRealPx','ceilVarNight','ceilVarDay',
           'ssmDoseN','ssmDoseNull',
           'rvtBoundN','rvtBoundShift','rvtBoundB','rvtBoundPermR',
           'rvtBoundCarryMax','rvtBoundResetMin','rvtBoundPermMax','rvtBoundPermSd',
           'rvtBoundDetsS','rvtBoundDetsB'} | {f'ssmDose{_m}{_w}{_s}'
           for _m in ('Base','Small') for _w in ('Six','Eleven') for _s in ('','SE')} | {f'rvtBound{_r}{_t}{_s}'
           for _r in ('Carry','Reset') for _t in ('S','B') for _s in ('','SE','Z','All')}
DERIVABLE|=_FH_DERIVED
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
print(f"\nexamined {len(NUM)} macro declaration(s) in {_NUMTEX}")
print(f"{len(CHECKS)} macros checked against their artifacts, {bad} disagree")

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
