"""E65 - the chunk-boundary intervention applied to RVT, in two state regimes.

E60 ran the intervention on SSM-ViT and measured a large within-frame gain. The mechanism
the paper gives for it is specific: the SSM release's carried state is inert across chunks
(experiments/e47_ssm/README.md, checked three independent ways), so a chunk boundary is an
effective reset and a frame's recurrent history is set by its position in the chunk.

That mechanism makes a falsifiable prediction about RVT, and the paper already depends on
it: Sec. 5 differences the observational chunk-position contrast against the three RVT
checkpoints "evaluated on the same frames with a state that crosses chunk boundaries". That
sentence is an assumption about RVT, not a measurement of it. This measures it.

Two regimes of the same driver, the same checkpoints, the same frames, the same estimand as
E60:

  carry - RESET=0, the released behaviour. modules/detection.py keeps the validation state
          in `mode_2_rnn_states` across chunks and clears it only on `is_first_sample`. If
          the mechanism is right, moving the boundary should not recover anything here,
          because nothing was lost at the boundary.
  reset - RESET=1, the state dropped at every chunk start. This puts RVT in the condition
          the SSM release is already in and is the positive control for the whole design:
          it shows the shift is actually applied and the frames actually change history, so
          a null in `carry` is a property of the release and not of a driver that dropped
          the treatment.

The estimand is E60's, unchanged, so the rows are directly comparable to dose.json:

    gain = mAP(shifted dump, paired frames) - mAP(released dump, paired frames)

on the frames the release placed at positions 0-3 that the shift carries to (0-3 - SHIFT)
mod 21, with the same 406-sequence cluster bootstrap at B = 300.

A permutation null is run alongside: the same paired delta on random frame sets of the same
size drawn from the frames covered in both arms. A rotation is a bijection, so over random
frames the gains at one position are offset by losses at another and the null is centred on
zero; a null that is not centred on zero means the pairing itself moves the number and the
treated rows cannot be read.
"""
import json, os, sys, numpy as np

SHIFT = int(os.environ.get('SHIFT', '5'))
os.environ['SHIFT'] = str(SHIFT)
sys.path.insert(0, 'src')
from e56_eval import Scorer                                    # noqa: E402
from e60_paired import perframe_conf, conf_of, ci, BOUNDS, CHUNK, SHORT  # noqa: E402
from multiprocessing import Pool                               # noqa: E402

# The reported numbers are B = 300 and RPERM = 200; the environment overrides exist only so
# src/e65_paired_selftest.sh can exercise the same code path cheaply, and are never set in a
# production run.
B = int(os.environ.get('B', '300'))
NPROC = int(os.environ.get('NPROC', '8'))
RPERM = int(os.environ.get('RPERM', '200'))
# E65DIR exists so the analysis can be exercised end to end on synthetic dumps before the
# real arms land (src/e65_paired_selftest.sh); production runs leave it unset.
D = os.environ.get('E65DIR', 'experiments/e65_rvt_boundary')
TAGS = os.environ.get('TAGS', 's,b').split(',')
REGIMES = ('carry', 'reset')
OUT = os.environ.get('OUT', f'{D}/paired-shift{SHIFT}.json')
GAIN = sorted((p - SHIFT) % CHUNK for p in range(*SHORT))
SHORT_LAB = f'{SHORT[0] + 1}-{SHORT[1]}'
GAIN_LAB = f'{min(GAIN) + 1}-{max(GAIN) + 1}'

# The SSM release's recorded placement. The chunked RVT driver walks the same grid with the
# same start expression, so its SHIFT=0 positions must equal this file frame for frame. That
# equality is what makes the RVT rows and the SSM rows in dose.json the same comparison on
# the same frames rather than two similar-looking ones.
PA = np.load('experiments/e58_chunkpos/positions.npy')

_S, TARGET, CONF, COVER = {}, {}, {}, {}


def _job(seed):
    rng = np.random.default_rng(seed)
    units = [np.arange(x['start'], x['start'] + x['n']) for x in BOUNDS]
    pick = rng.integers(0, len(units), len(units))
    fr = np.concatenate([units[i] for i in pick])
    out = {}
    for key, (sa, sb) in _S.items():
        keep = fr[np.isin(fr, TARGET[key])]
        if len(keep) == 0:
            continue
        ca, cb = conf_of(CONF[key][0], keep), conf_of(CONF[key][1], keep)
        out[key] = dict(
            map_vel=(sa.evaluate(0.0, frames=keep) * 100, sb.evaluate(0.0, frames=keep) * 100),
            map_all=(sa.evaluate(0.0, frames=keep, require_velocity=False) * 100,
                     sb.evaluate(0.0, frames=keep, require_velocity=False) * 100),
            conf=(ca[0], cb[0]), conf_tp=(ca[1], cb[1]), dpf=(ca[2], cb[2]))
    return out


def _perm(seed):
    """The treated delta on a random frame set of the same size, drawn from both-arm frames."""
    rng = np.random.default_rng(100000 + seed)
    out = {}
    for key, (sa, sb) in _S.items():
        pool = COVER[key]
        n = len(TARGET[key])
        if n == 0 or len(pool) < n:
            continue
        keep = rng.choice(pool, size=n, replace=False)
        out[key] = (sb.evaluate(0.0, frames=keep) * 100) - (sa.evaluate(0.0, frames=keep) * 100)
    return out


if __name__ == '__main__':
    rows = {}
    for tag in TAGS:
        for reg in REGIMES:
            fa = f'{D}/dets-rvt-{tag}-{reg}-shift0.npz'
            fb = f'{D}/dets-rvt-{tag}-{reg}-shift{SHIFT}.npz'
            if not (os.path.exists(fa) and os.path.exists(fb)):
                print(f'  [skip] rvt-{tag} {reg}: dumps not both present')
                continue
            key = f'{tag}-{reg}'
            a, b = np.load(fa), np.load(fb)
            pa, pb = a['pos'], b['pos']
            assert np.array_equal(a['gt'], b['gt'], equal_nan=True), f'{key}: ground truth differs'
            assert len(pa) == len(pb) == len(PA), f'{key}: frame count differs'
            # the unshifted chunked RVT dump must sit on the released placement exactly
            assert np.array_equal(pa, PA), \
                f'{key}: the SHIFT=0 chunked RVT placement differs from the recorded release placement'
            # every frame's position must rotate by exactly SHIFT where both arms cover it
            cov = np.flatnonzero((pa >= 0) & (pb >= 0))
            bad = int((((pa[cov] - SHIFT) % CHUNK) != pb[cov]).sum())
            assert bad == 0, f'{key}: {bad} covered frames do not rotate by {SHIFT}'
            f = np.flatnonzero((pa >= SHORT[0]) & (pa < SHORT[1]))
            gained = f[np.isin(pb[f], GAIN)]
            sa_, sb_ = (Scorer(a['det'].astype(np.float64), a['gt'].astype(np.float64)),
                        Scorer(b['det'].astype(np.float64), b['gt'].astype(np.float64)))
            _S[key] = (sa_, sb_)
            TARGET[key] = gained
            COVER[key] = cov
            CONF[key] = (perframe_conf(sa_), perframe_conf(sb_))
            ca, cb = conf_of(CONF[key][0], gained), conf_of(CONF[key][1], gained)
            rows[key] = dict(tag=tag, regime=reg, n=int(len(gained)), n_cover=int(len(cov)),
                             map_vel=[sa_.evaluate(0.0, frames=gained) * 100,
                                      sb_.evaluate(0.0, frames=gained) * 100],
                             map_all=[sa_.evaluate(0.0, frames=gained, require_velocity=False) * 100,
                                      sb_.evaluate(0.0, frames=gained, require_velocity=False) * 100],
                             conf=[ca[0], cb[0]], conf_tp=[ca[1], cb[1]], dpf=[ca[2], cb[2]])
            r = rows[key]
            print(f"  rvt-{tag} {reg}: n={r['n']} paired frames", flush=True)
            for k, unit in (('map_vel', 'pt mAP, velocity-evaluable'), ('map_all', 'pt mAP, all boxes'),
                            ('conf', 'mean confidence'), ('dpf', 'detections per frame')):
                lo, hi = r[k]
                print(f'      {unit:32s} {SHORT_LAB} win {lo:8.4f}   {GAIN_LAB} win {hi:8.4f}'
                      f'   paired {hi - lo:+8.4f}', flush=True)
    assert rows, 'no E65 arm has both its dumps'

    print(f'cluster bootstrap B={B} over {len(BOUNDS)} sequences', flush=True)
    with Pool(NPROC) as p:
        reps = p.map(_job, range(B))
        perms = p.map(_perm, range(RPERM))
    res = {}
    for key, r in rows.items():
        d = dict(r)
        for k in ('map_vel', 'map_all', 'conf', 'conf_tp', 'dpf'):
            g = [x[key][k][1] - x[key][k][0] for x in reps if key in x]
            st = ci(g)
            obs = r[k][1] - r[k][0]
            d[k + '_boot'] = dict(obs=obs, **st, z=obs / st['se'] if st['se'] else float('nan'))
        pv = np.asarray([x[key] for x in perms if key in x], dtype=float)
        d['perm_null'] = dict(r=int(len(pv)), mean=float(pv.mean()), sd=float(pv.std(ddof=1)),
                              lo=float(np.percentile(pv, 2.5)), hi=float(np.percentile(pv, 97.5)),
                              z_obs=float((d['map_vel_boot']['obs'] - pv.mean()) / pv.std(ddof=1)))
        res[key] = d
        mv = d['map_vel_boot']
        pn = d['perm_null']
        print(f"  rvt-{key:12s} dmAP(vel) {mv['obs']:+8.4f} +- {mv['se']:.4f}"
              f"  95% CI [{mv['ci'][0]:+7.4f}, {mv['ci'][1]:+7.4f}]  z={mv['z']:+6.2f}"
              f"   | random-frame null {pn['mean']:+.4f} +- {pn['sd']:.4f}, z_obs={pn['z_obs']:+6.2f}",
              flush=True)
    json.dump(dict(shift=SHIFT, B=B, rperm=RPERM, chunk=CHUNK, short=list(SHORT), gain=GAIN,
                   arms=res), open(OUT, 'w'), indent=1)
    print('WROTE', OUT)
