"""C1: does the anchor calibration (slot efficiency from one anchor configuration per slot) carry the mirror failure?
Recount the mirror table with the efficiency division replaced, and compare the offset/gain slot coefficients with
their distribution under white phase error."""

from pathlib import Path
from typing import Any

import c1_phase as cp
import numpy as np
from c1_common import MIRROR, an, observed_rows, settings, signed_diffs

HERE = Path(__file__).resolve().parent

rows = observed_rows()
OBSERVED = np.load(HERE / "c1_observed.npz")
item = OBSERVED["item"]
ideal = OBSERVED["ideal"]
sgn = np.where(item == 0, 1.0, -1.0)
eta = np.array(an.mode_efficiency_fit(rows, settings))
orig = an.calibrate


def patched(eff):
    def cal(rows_, settings_):
        c = orig(rows_, settings_)
        c = {**c, "efficiency": {"A": eff[0], "B": eff[1]}}
        return c

    return cal


def table(eff):
    an.calibrate = patched(eff) if eff is not None else orig
    keys, d, t, cal = signed_diffs(rows)
    an.calibrate = orig
    return d, cal


base_cal = orig(rows, settings)
effs = {
    "anchor-calibrated (as analyzed)": None,
    "no efficiency division (1, 1)": (1.0, 1.0),
    "equal efficiency, mean of the two anchors": (np.mean(list(base_cal["efficiency"].values())),) * 2,
    "mode-fit slot sums over the failure mode": (eta[:4].mean() / eta[8], eta[4:8].mean() / eta[8]),
}
print(
    "anchor efficiencies (A, B):",
    {k: round(v, 4) for k, v in base_cal["efficiency"].items()},
    "; mode-fit slot/failure:",
    round(eta[:4].mean() / eta[8], 4),
    round(eta[4:8].mean() / eta[8], 4),
)
for lab, eff in effs.items():
    d, cal = table(eff)
    X = np.c_[sgn, sgn * ideal]
    beta, *_ = np.linalg.lstsq(X, d, rcond=None)
    print(
        f"{lab:46s} eff {tuple(round(float(v), 4) for v in (cal['efficiency']['A'], cal['efficiency']['B']))}: failing {(abs(d) > MIRROR).sum()} of 46, |d| median {np.median(abs(d)):.4f} max {abs(d).max():.4f} rms {np.sqrt(np.mean(d**2)):.4f}; slot offset/gain {beta.round(4)}"
    )
# the efficiency ratio that minimizes the mirror rms
best: Any = None
for rb in np.linspace(0.9, 1.25, 71):
    d, _ = table((base_cal["efficiency"]["A"], base_cal["efficiency"]["A"] * rb))
    r = np.sqrt(np.mean(d**2))
    if best is None or r < best[0]:
        best = (r, rb, (abs(d) > MIRROR).sum())
print(
    f"B/A efficiency ratio minimizing the mirror rms: {best[1]:.3f} (anchor-calibrated {base_cal['efficiency']['B'] / base_cal['efficiency']['A']:.3f}); rms {best[0]:.4f}, failing {best[2]}"
)
# null distribution of the gain coefficient and offset under white phase error sigma 0.033
o = cp.one_sigma((0.033, 5, True))
ds = o["d"]
X = np.c_[sgn, sgn * ideal]
bs = np.array([np.linalg.lstsq(X, row, rcond=None)[0] for row in ds])
bo = np.linalg.lstsq(X, OBSERVED["d"], rcond=None)[0]
print(
    f"white phase error sigma 0.033 (300 draws): offset {bs[:, 0].mean():+.4f} +- {bs[:, 0].std():.4f}, gain {bs[:, 1].mean():+.4f} +- {bs[:, 1].std():.4f}; observed offset {bo[0]:+.4f}, gain {bo[1]:+.4f}; gain z {(bo[1] - bs[:, 1].mean()) / bs[:, 1].std():+.1f}; draws with gain >= observed {(bs[:, 1] >= bo[1]).sum()}"
)
