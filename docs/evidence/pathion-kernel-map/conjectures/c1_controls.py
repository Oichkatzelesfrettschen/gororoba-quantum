"""C1: does the phase-error sensitivity predict failing pairs beyond simple ideal-level predictors? Level deviation of the pairs job under white sigma."""

from pathlib import Path
from typing import Any

import numpy as np
from c1_common import MIRROR, mirror_table, rows_from_probs, settings
from scipy import stats

HERE = Path(__file__).resolve().parent
OBSERVED = np.load(HERE / "c1_observed.npz")
P = np.load(HERE / "c1_phase.npz")
d, item = OBSERVED["d"], OBSERVED["item"]
keys = [tuple(k.split("|")[:1]) + (int(k.split("|")[1]),) for k in OBSERVED["keys"]]
s_pair = P["s_pair"]
absd = abs(d)
L = {}
for k in keys:
    s = [s for s in settings if s["setting"] == k[0] and s["orientation"] == 0][0]
    L[k] = (s["slots"]["A"]["ideal_level"], s["slots"]["B"]["ideal_level"], s["ideal_label_law"], s["role"])
own = np.array([L[k][k[1]] if isinstance(L[k][k[1]], float) else 0 for k in keys])
own = np.array([L[k][0] if k[1] == 0 else L[k][1] for k in keys])
other = np.array([L[k][1] if k[1] == 0 else L[k][0] for k in keys])
tot = own + other
law = np.array([L[k][2] for k in keys])
ent = -(np.where(law > 1e-9, law, 1) * np.log(np.where(law > 1e-9, law, 1))).sum(1)
nz = (law > 1e-9).sum(1)
cand = {
    "phase sensitivity (sigma .05 sim)": s_pair,
    "own ideal level": own,
    "sum of both ideal levels": tot,
    "own(1-own)": own * (1 - own),
    "label-law entropy": ent,
    "number of lit modes": nz.astype(float),
}
print("spearman(|d|, predictor):")
for n, v in cand.items():
    r = stats.spearmanr(v, absd)
    print(f"  {n:36s} {r.statistic:+.3f} (p {r.pvalue:.3f})")


# partial: rank-regress |d| and sensitivity on the other predictors
def rank(x):
    return stats.rankdata(x)


Z = np.c_[np.ones(len(d)), rank(own), rank(tot), rank(ent), rank(nz)]


def resid(y):
    return rank(y) - Z @ np.linalg.lstsq(Z, rank(y), rcond=None)[0]


pr = stats.pearsonr(resid(s_pair), resid(absd))
print(
    f"partial rank correlation of |d| with phase sensitivity given own level, total level, entropy, lit modes: {pr.statistic:+.3f} (p {pr.pvalue:.3f})"
)
# per-pair listing
fail = absd > MIRROR
print(
    "sensitivity rank of failing pairs among 46 (1 = most sensitive):",
    sorted(int(46 - stats.rankdata(s_pair)[j] + 1) for j in np.where(fail)[0]),
)
# white-sigma deviation of levels from ideal for the pairs job
import c1_phase as cp

o = cp.one_sigma((0.033, 5, True))
# need per-reading deviations: recompute quickly with a small loop
import numpy as np
from c1_mesh import propagate

# QRNG seed: docs/evidence/anu_qrng/draw-2026-10-25T015224Z.json index 1
rng = np.random.default_rng(52300)
R = 120
dev: Any = []
devA: list[float] = []
devB: list[float] = []
for _draw in range(R):
    pr_ = np.empty((52, 12))
    for i in range(52):
        pr_[i] = propagate(cp.kinds, cp.lo, cp.TH[i], cp.PH[i], dph=rng.normal(0, 0.033, size=(1, 126)))[0]
    pr_[:, :9] *= cp.ETA
    t, cal = mirror_table(rows_from_probs(pr_))
    for k in t:
        s = [s for s in settings if s["setting"] == k[0] and s["orientation"] == 0][0]
        ideal = s["slots"]["AB"[k[1]]]["ideal_level"]
        for oo in (0, 1):
            dv = t[k][oo][2] - ideal
            dev.append(dv)
            (devA if t[k][oo][1] == "A" else devB).append(dv)
dev = np.array(dev)
print(
    f"white sigma 0.033, pairs job: per-reading deviation rms {np.sqrt(np.mean(dev**2)):.4f} (observed 0.0282); slot A mean {np.mean(devA):+.4f} (observed +0.0200), slot B mean {np.mean(devB):+.4f} (observed -0.0155)"
)
