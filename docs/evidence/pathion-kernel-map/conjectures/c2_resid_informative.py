"""C2 (d) restricted to the informative blocks: ideal N_b in {0, +-2}; blocks with all-aligned bins (N_b = 4) read N_hat = 4 identically."""

import json
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent

for dev in ("fez", "marrakesh"):
    t = json.load(open(HERE / f"c2_resid_{dev}.json"))
    allb = list(t)
    det = [b for b in allb if abs(t[b]["ideal"]) == 4]
    inf = [b for b in allb if b not in det]
    zero = [b for b in inf if abs(t[b]["ideal"]) < 0.5]
    two = [b for b in inf if abs(abs(t[b]["ideal"]) - 2) < 0.5]
    print(
        f"{dev}: {len(allb)} blocks; deterministic (N_b = 4): {len(det)}; informative {len(inf)} = ideal-zero {len(zero)} + |N_b| = 2 {len(two)}"
    )
    for lab, g in (("ideal-zero", zero), ("|N_b| = 2 (6 positive + xor)", two)):
        r = np.array([t[b]["meas"] - t[b]["ideal"] for b in g])
        p = np.array([t[b]["incoh"] - t[b]["ideal"] for b in g])
        se = np.array([t[b]["meas_se"] for b in g])
        print(
            f"  {lab}: n {len(g)} mean measured residual {r.mean():+.4f}; mean calibrated prediction {p.mean():+.4f}; mean (measured - prediction) {np.mean(r - p):+.4f} +- {np.sqrt((se**2).sum()) / len(g):.4f}; corr(measured, prediction) {np.corrcoef(r, p)[0, 1]:+.2f}"
        )
    pos2 = [b for b in two if t[b]["ideal"] > 0]
    r = np.array([t[b]["meas"] - t[b]["ideal"] for b in pos2])
    p = np.array([t[b]["incoh"] - t[b]["ideal"] for b in pos2])
    print(
        f"  N_b = +2 only (n {len(pos2)}): measured residual {r.min():+.3f} to {r.max():+.3f} (mean {r.mean():+.4f}), prediction {p.min():+.3f} to {p.max():+.3f}; measured - prediction {np.round(r - p, 3).tolist()}"
    )
    cz = np.array([t[b]["cz"] for b in inf])
    res = np.array([t[b]["meas"] - t[b]["ideal"] for b in inf])
    pr = np.array([t[b]["incoh"] - t[b]["ideal"] for b in inf])
    print(
        f"  informative blocks: Spearman(residual, cz) {stats.spearmanr(cz, res).statistic:+.2f}; Spearman(measured - prediction, cz) {stats.spearmanr(cz, res - pr).statistic:+.2f}; corr(measured, prediction) {np.corrcoef(res, pr)[0, 1]:+.2f}"
    )
    print(
        "  xor block:",
        {
            b: (round(t[b]["meas"] - t[b]["ideal"], 4), round(t[b]["incoh"] - t[b]["ideal"], 4))
            for b in two
            if "xor" in b
        },
    )
