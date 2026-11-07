"""C1 mechanism: random phase error on every phase shifter of each iteration's compiled mesh (independent per
iteration, sigma radians). Reports the mirror-difference distribution, the leakage into the three sentinel modes,
and whether the per-pair sensitivity predicts which pairs fail."""

from pathlib import Path

import numpy as np
from c1_common import MIRROR, an, observed_rows, rows_from_probs, settings, signed_diffs
from c1_mesh import PAIRS, cached, propagate
from scipy import stats

from parallel import ordered_map

HERE = Path(__file__).resolve().parent

kinds, lo, TH, PH, PERF = cached(PAIRS, "pairs")
ETA = np.array(an.mode_efficiency_fit(observed_rows(), settings))
OBS = np.load(HERE / "c1_observed.npz")
KEYS = [tuple(k.split("|")[:1]) + (int(k.split("|")[1]),) for k in OBS["keys"]]
R = 300
# QRNG seed base of the per-sigma draws: docs/evidence/anu_qrng/draw-2026-10-25T015224Z.json index 3
PHASE_SEED = 23523


def one_sigma(task):
    sigma, seed, use_eta = task
    rng = np.random.default_rng(seed)
    probs = np.empty((R, 52, 12))
    for i in range(52):
        dph = rng.normal(0.0, sigma, size=(R, PH.shape[1]))
        probs[:, i, :] = propagate(kinds, lo, TH[i], PH[i], dph=dph)
    leak = probs[:, :, 9:].sum(-1)
    ds = np.empty((R, len(KEYS)))
    for r in range(R):
        p = probs[r].copy()
        if use_eta:
            p[:, :9] *= ETA
        rows = rows_from_probs(p)
        keys, d, _, _ = signed_diffs(rows)
        if [tuple(k) for k in keys] != KEYS:
            raise ValueError("setting keys differ from the observed order")
        ds[r] = d
    return {
        "sigma": sigma,
        "leak_mean": float(leak.mean()),
        "leak_median_iter": float(np.median(leak.mean(0))),
        "d": ds,
    }


def main():
    sigmas = [0.002, 0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.12]
    tasks = [(s, PHASE_SEED + j, True) for j, s in enumerate(sigmas)]
    out = ordered_map(one_sigma, tasks, min_items=1)
    d_obs = OBS["d"]
    obs_stat = (
        np.median(abs(d_obs)),
        np.abs(d_obs).max(),
        np.sqrt(np.mean(d_obs**2)),
        int((abs(d_obs) > MIRROR).sum()),
    )
    print(
        f"observed: |d| median {obs_stat[0]:.4f} max {obs_stat[1]:.4f} rms {obs_stat[2]:.4f} failing {obs_stat[3]}; sentinel share observed ~5.8e-4 (all iterations 3.7e-4..7.9e-4, dark-floor)"
    )
    print(
        "sigma  leak(sentinel share)  |d| median  max  rms  failing/46 (mean over draws)  p(failing>=9)  mean(signed d item0) mean(item1)"
    )
    item = OBS["item"]
    for o in out:
        ds = o["d"]
        med = np.median(abs(ds), axis=1).mean()
        mx = np.abs(ds).max(1).mean()
        rms = np.sqrt((ds**2).mean())
        nf = (abs(ds) > MIRROR).sum(1)
        print(
            f"{o['sigma']:.3f}  {o['leak_mean']:.2e}  {med:.4f}  {mx:.4f}  {rms:.4f}  {nf.mean():5.1f}  {(nf >= 9).mean():.2f}  {ds[:, item == 0].mean():+.4f} {ds[:, item == 1].mean():+.4f}"
        )
        o["rms"] = rms
    # sigma that matches the observed rms, and its leakage
    rmss = np.array([o["rms"] for o in out])
    sg = np.array(sigmas)
    lk = np.array([o["leak_mean"] for o in out])
    s_match = float(np.interp(obs_stat[2], rmss, sg))
    l_match = float(np.interp(s_match, sg, lk))
    print(
        f"sigma matching the observed rms mirror difference {obs_stat[2]:.4f}: {s_match:.3f} rad; the mesh then leaks {l_match:.2e} of clicks into sentinel modes 9-11 (observed 5.8e-4 including detector background)"
    )
    # which-pair prediction at the matching sigma: per-pair rms of simulated d vs observed |d|
    ref = min(out, key=lambda o: abs(o["sigma"] - 0.05))
    s_pair = np.sqrt((ref["d"] ** 2).mean(0))
    sp = stats.spearmanr(s_pair, abs(d_obs))
    fail = abs(d_obs) > MIRROR
    auc = stats.mannwhitneyu(s_pair[fail], s_pair[~fail], alternative="greater").statistic / (
        fail.sum() * (~fail).sum()
    )
    print(
        f"sensitivity (sigma 0.05 per-pair rms of simulated d): spearman with observed |d| {sp.statistic:+.3f} (p {sp.pvalue:.3f}); AUC for failing pairs {auc:.3f}"
    )
    print(
        f"  predicted-rms of failing pairs median {np.median(s_pair[fail]):.4f}, others {np.median(s_pair[~fail]):.4f}"
    )
    # sentinel-bounded sigma: leak at most 2e-4 above the 5.8e-4 floor?
    print("sigma bound from sentinel leak <= 2e-4:", float(np.interp(2e-4, lk, sg)))
    np.savez(HERE / "c1_phase.npz", s_pair=s_pair, sigmas=sg, leak=lk, rms=rmss)


if __name__ == "__main__":
    main()
