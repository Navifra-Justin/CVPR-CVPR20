"""Emit the LaTeX macros for E56/E56d/E58/E59 from their artifacts.

Nothing here is typed by hand: every value is read from the JSON the experiment wrote, so
`src/audit_numbers.py` can re-derive each one and a macro edited without a corresponding
run fails the audit rather than review.
"""
import json, numpy as np
def L(p): return json.load(open(p))
R  = L('experiments/e56_resolving/resolving.json')
RS = L('experiments/e56_resolving/rankse.json')
AB = L('experiments/e58_chunkpos/allbox.json')
PM = L('experiments/e58_chunkpos/perm.json')
IV = L('experiments/e58_chunkpos/invariant.json')
TL = L('experiments/e42_recurrent_support/tail.json')
CO = L('experiments/e56_resolving/collapse.json')
CM = {d['name']: d for d in L('experiments/e56_resolving/composition.json')}
AS = L('experiments/e27_rows/association.json')
PP = L('experiments/e63_port/parity.json')
SB = L('experiments/e45_influence_fixed/seqboot.json')
_ag = AS['rows']['greedy_0.3']['reported']; _af = AS['rows']['center_1.5']['reported']
_q = min(CO['cv_fixed_quantile'], key=lambda k: CO['cv_fixed_quantile'][k]['0.05'])

N = R['noise']['all moving']
sed = [N[m]['se_dmap_pt'] for m in N]; sem = [N[m]['se_map_pt'] for m in N]
eft = [N[m]['effect_at_tau_pt'] for m in N]
rp  = [N[m]['resolve_paired_ms'] for m in N]; ra = [N[m]['resolve_absolute_ms'] for m in N]
box = RS['pairs']['every labelled box']
tight = min(box, key=lambda d: d['gap'])
M = dict(
  seDmapLo=(min(sed), 3), seDmapHi=(max(sed), 3),
  seMapLo=(min(sem), 2), seMapHi=(max(sem), 2),
  resPairedLo=(min(rp), 1), resPairedHi=(max(rp), 1),
  effTauLo=(min(eft), 3), effTauHi=(max(eft), 3),
  twoSeDmapLo=(2 * min(sed), 3), twoSeDmapHi=(2 * max(sed), 3),
  effTauResolved=(sum(e > 2 * N[m]['se_dmap_pt'] for e, m in zip(eft, N)), 0),
  resAbsLo=(min(ra), 0), resAbsHi=(max(ra), 0),
  dstarAll=(R['strata']['all moving']['dstar_ms'], 1),
  dstarAllTau=(R['strata']['all moving']['dstar_over_tau'], 2),
  dstarMid=(R['strata']['25-50 px/s']['dstar_ms'], 1),
  dstarMidTau=(R['strata']['25-50 px/s']['dstar_over_tau'], 2),
  rankHoldBox=(100 * RS['order_preserved']['every labelled box'], 1),
  rankHoldMov=(100 * RS['order_preserved']['moving subset'], 1),
  rankFlipMax=(tight['p_flip'], 2),
  rankGapMin=(tight['gap'], 3), rankGapMinSE=(tight['se'], 2),
  chunkDidBase=(-AB['did']['s5vit-base'], 2),
  chunkDidBaseSE=(AB['boot']['s5vit-base']['se'], 2),
  chunkDidBaseZ=(-AB['did']['s5vit-base'] / AB['boot']['s5vit-base']['se'], 1),
  chunkDidSmall=(-AB['did']['s5vit-small'], 2),
  chunkDidSmallSE=(AB['boot']['s5vit-small']['se'], 2),
  chunkDidSmallZ=(-AB['did']['s5vit-small'] / AB['boot']['s5vit-small']['se'], 1),
  chunkPlaceboMax=(max(abs(AB['did'][m]) for m in ('rvt-t', 'rvt-s', 'rvt-b')), 2),
  chunkPlaceboZ=(max(abs(AB['did'][m]) / AB['boot'][m]['se']
                     for m in ('rvt-t', 'rvt-s', 'rvt-b')), 2),
  chunkGapBase=(-AB['pooled_gap']['s5vit-base'], 2),
  chunkGapSmall=(-AB['pooled_gap']['s5vit-small'], 2),
  chunkShortBase=(100 * AB['point']['s5vit-base']['short'], 1),
  chunkFullBase=(100 * AB['point']['s5vit-base']['full'], 1),
  chunkRelBase=(100 * AB['point']['s5vit-base']['pooled'], 1),
  chunkPermB=(200, 0),
  chunkPermSd=(max(PM['s5vit-base']['null_sd'], PM['s5vit-small']['null_sd']), 2),
  chunkPermZBase=(abs(PM['s5vit-base']['z']), 1),
  chunkPermZSmall=(abs(PM['s5vit-small']['z']), 1),
  chunkPermPlaceboZ=(max(abs(PM[k]['z']) for k in ('rvt-t', 'rvt-s', 'rvt-b')), 2),
  chunkPermP=(PM['s5vit-base']['p'], 3),
  chunkRiseBase=((AB['point']['s5vit-base']['full']
                  - AB['point']['s5vit-base']['short']) * 100, 2),
  chunkRiseSmall=((AB['point']['s5vit-small']['full']
                   - AB['point']['s5vit-small']['short']) * 100, 2),
  chunkRiseRvt=(max(abs(AB['point'][k]['full'] - AB['point'][k]['short']) * 100
                    for k in ('rvt-t', 'rvt-s', 'rvt-b')), 2),
  chunkConfOne=(IV['conf_by_position']['s5vit-small'][0], 3),
  chunkConfFull=(IV['conf_by_position']['s5vit-small'][16], 3),
  chunkConfPct=(100 * (IV['conf_by_position']['s5vit-small'][16]
                       / IV['conf_by_position']['s5vit-small'][0] - 1), 1),
  # per-model cells of the supplement's chunk-position table
  chunkShortSmall=(100 * AB['point']['s5vit-small']['short'], 1),
  chunkFullSmall=(100 * AB['point']['s5vit-small']['full'], 1),
  chunkRelSmall=(100 * AB['point']['s5vit-small']['pooled'], 1),
  chunkShortT=(100 * AB['point']['rvt-t']['short'], 1),
  chunkFullT=(100 * AB['point']['rvt-t']['full'], 1),
  chunkShortS=(100 * AB['point']['rvt-s']['short'], 1),
  chunkFullS=(100 * AB['point']['rvt-s']['full'], 1),
  chunkShortB=(100 * AB['point']['rvt-b']['short'], 1),
  chunkFullB=(100 * AB['point']['rvt-b']['full'], 1),
  chunkDidT=(AB['did']['rvt-t'], 2), chunkSeT=(AB['boot']['rvt-t']['se'], 2),
  chunkDidS=(AB['did']['rvt-s'], 2), chunkSeS=(AB['boot']['rvt-s']['se'], 2),
  chunkDidB=(AB['did']['rvt-b'], 2), chunkSeB=(AB['boot']['rvt-b']['se'], 2),
  # E56e: which summary of the label composition sets the resolution, and its price
  collapseCVraw=(CO['cv_no_rescaling']['0.05'], 2),
  collapseCVmed=(CO['cv_fixed_quantile']['50']['0.05'], 2),
  collapseQbest=(float(_q), 0),
  collapseCVbest=(CO['cv_fixed_quantile'][_q]['0.05'], 2),
  collapseCV=(CO['matched_quantile']['0.05']['cv3'], 3),
  collapseD=(CO['matched_quantile']['0.05']['d_star'], 4),
  collapseDsd=(CO['matched_quantile']['0.05']['d_sd'], 4),
  collapseIoU=(CO['matched_quantile']['0.05']['iou_at_d'], 3),
  collapseCVten=(CO['matched_quantile']['0.10']['cv3'], 2),
  collapseCVqtr=(CO['matched_quantile']['0.25']['cv3'], 2),
  tailGainTop=(CO['tail_cost']['>50 px/s']['resolution_gain'], 2),
  tailSeTop=(CO['tail_cost']['>50 px/s']['se_inflation'], 2),
  tailNetTop=(CO['tail_cost']['>50 px/s']['net'], 2),
  tailNetMid=(CO['tail_cost']['25-50 px/s']['net'], 2),
  stNtop=(CO['r_summary']['>50 px/s']['n'], 0),
  rGenAll=(CM['Gen1 (all moving)']['r_median'], 3),
  rDsecTrain=(CM['DSEC-Det (train)']['r_median'], 2),
  ddRatioMed=(CM['DSEC-Det (train)']['ratio_to_gen1'], 1),
  ddBoxesTrain=(CM['DSEC-Det (train)']['n'], 0),
  qGenAll=(CM['Gen1 (all moving)']['r_p95'], 2),
  qDsecTrain=(CM['DSEC-Det (train)']['r_p95'], 2),
  qDsecRatio=(CM['DSEC-Det (train)']['ratio_q95'], 2),
  qDsecNet=(CM['DSEC-Det (train)']['net_of_n'], 1),
  aFitShort=(TL['a_fit_1_9'], 3),
  tailExp=(TL['a_all'], 3), tailExpSE=(TL['a_se'], 3),
  tailExpLo=(TL['a_lo'], 3), tailExpHi=(TL['a_hi'], 3),
  tailRatio=(TL['ratio'], 3), tailRatioLo=(TL['ratio_lo'], 3), tailRatioHi=(TL['ratio_hi'], 3),
  tailOutside=(100 * TL['outside_current_window'], 1),
  tailRmsPower=(TL['rmsz_power'], 1), tailRmsExp=(TL['rmsz_exp'], 1),
  tailRmsRatio=(TL['rmsz_exp'] / TL['rmsz_power'], 1),
  assocRules=(AS['n_rules'], 0),
  assocLo=(AS['span_ms'][0], 2), assocHi=(AS['span_ms'][1], 2),
  assocSpread=(AS['spread_ms'], 2), assocSE=(AS['median_se_ms'], 2),
  assocGate=(_ag['tau_ms'], 2), assocGateSE=(_ag['tau_se_ms'], 2),
  assocFree=(_af['tau_ms'], 2), assocFreeSE=(_af['tau_se_ms'], 2),
  assocFreeN=(_af['n'], 0), assocGateN=(_ag['n'], 0),
  assocDelta=(abs(_af['tau_ms'] - _ag['tau_ms']) / _ag['tau_se_ms'], 2),
  assocMinLo=(AS['span_minimal_ms'][0], 2), assocMinHi=(AS['span_minimal_ms'][1], 2),
  portEvalGap=(PP['max_gap'], 3), portParamDev=(PP['max_params_dev'], 3),
  portSeqs=(PP['val_sequences'], 0),
  portApT=(PP['rows']['rvt-t']['coco_ap'], 2), portApOwnT=(PP['rows']['rvt-t']['own_ap'], 2),
  portApFifty=(PP['rows']['rvt-t']['coco_ap50'], 1),
  occSeqs=(SB['fills']['zero']['n_seq'], 0),
  occSeqCiLo=(SB['fills']['zero']['boot_lo'], 2), occSeqCiHi=(SB['fills']['zero']['boot_hi'], 2),
  occSeqSE=(SB['fills']['zero']['boot_se'], 2),
  occSeqWidest=(SB['widest_ci_ms'], 2), occSeqLoo=(SB['loo_span_ms'] / 2, 2),
  occPerSeqLo=(SB['fills']['zero']['per_seq_lo'], 2),
  occPerSeqHi=(SB['fills']['zero']['per_seq_hi'], 2),
)
for k, (v, d) in M.items():
    print(f'\\newcommand{{\\{k}}}{{{v:.{d}f}}}')
