"""C1: phase-error scan with the slot efficiencies fixed to the mode-fit values (anchor division removed), against the observed
mirror table under the same calibration."""

import c1_phase as cp
import numpy as np
from c1_common import MIRROR, an, observed_rows, rows_from_probs, signed_diffs
from c1_mesh import propagate

from parallel import ordered_map

ETA = cp.ETA
# QRNG seed base of the per-sigma draws: docs/evidence/anu_qrng/draw-2026-10-25T015224Z.json index 4
PHASE_EQ_SEED = 13183
EFF = (ETA[:4].mean() / ETA[8], ETA[4:8].mean() / ETA[8])
orig = an.calibrate


def cal(rows, settings_):
    c = orig(rows, settings_)
    return {**c, "efficiency": {"A": EFF[0], "B": EFF[1]}}


def diffs(rows):
    an.calibrate = cal
    try:
        return signed_diffs(rows)[1]
    finally:
        an.calibrate = orig


def one(task):
    sigma, seed = task
    rng = np.random.default_rng(seed)
    R = 200
    probs = np.empty((R, 52, 12))
    for i in range(52):
        probs[:, i, :] = propagate(
            cp.kinds, cp.lo, cp.TH[i], cp.PH[i], dph=rng.normal(0, sigma, size=(R, cp.PH.shape[1]))
        )
    out = []
    for r in range(R):
        p = probs[r].copy()
        p[:, :9] *= ETA
        out.append(diffs(rows_from_probs(p)))
    return sigma, np.array(out)


if __name__ == "__main__":
    d_obs = diffs(observed_rows())
    print(
        f"observed under mode-fit slot efficiencies {tuple(round(float(x), 4) for x in EFF)}: |d| median {np.median(abs(d_obs)):.4f} max {abs(d_obs).max():.4f} rms {np.sqrt(np.mean(d_obs**2)):.4f} failing {(abs(d_obs) > MIRROR).sum()}"
    )
    for sigma, ds in ordered_map(
        one, [(s, PHASE_EQ_SEED + j) for j, s in enumerate((0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04))], min_items=1
    ):
        print(
            f"sigma {sigma:.3f}: |d| median {np.median(abs(ds), axis=1).mean():.4f} max {abs(ds).max(1).mean():.4f} rms {np.sqrt((ds**2).mean()):.4f} failing {(abs(ds) > MIRROR).sum(1).mean():.1f}"
        )
