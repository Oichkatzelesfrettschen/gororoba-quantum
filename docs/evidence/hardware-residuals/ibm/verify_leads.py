"""Independent recomputation of five leads of REPORT.md with plain statistics.

common.py supplies only the dataset list, the error matrices and the coupler graph. Each statistic is recomputed
here; `control` repeats the lag and run statistics after the fixed reordering n -> 7919 n mod N of the shots.
"""

import math
from typing import Any

import common
import numpy as np
from scipy import stats

cat = common.catalog()
sets = common.ground_datasets(cat)
dist = {b: common.graph_distances(common.coupling_graph(b)) for b in ("ibm_kingston", "ibm_fez")}


def lag_stats(x, lag=1):
    n = x.shape[0]
    k = x.sum(0).astype(float)
    obs = (x[:-lag] & x[lag:]).sum(0).astype(float)
    exp = k * k / n
    return obs, exp


def runs5(x):
    n = x.shape[0]
    p = x.mean(0)
    w = x[:-4] & x[1:-3] & x[2:-2] & x[3:-1] & x[4:]
    start = w.copy()
    start[1:] &= ~w[:-1].astype(bool)
    obs = start.sum()
    exp = ((n - 5) * p**5 * (1 - p) + p**5).sum()
    return int(obs), float(exp)


def blocks_p(x, blocks=8):
    n = x.shape[0] // blocks * blocks
    c = x[:n].reshape(blocks, -1, x.shape[1]).sum(1).astype(float)
    m = n // blocks
    p = c.sum(0) / n
    ok = p * m >= 5
    chi = ((c - p * m) ** 2 / (p * m * (1 - p) + 1e-300)).sum(0)
    return stats.chi2.sf(chi[ok], blocks - 1)


print("== ibm_kingston state-prep PUBs")
tot = {"drift_cols": 0, "drift_hit": 0}
for ds in sets:
    if ds["kind"] != "state_prep":
        continue
    x, qubits = common.load_errors(ds)
    n = x.shape[0]
    perm = (np.arange(n) * 7919) % n
    out: dict[str, Any] = {}
    for label, y in (("data", x), ("control", x[perm])):
        obs, exp = lag_stats(y)
        z = (obs - exp) / np.sqrt(np.maximum(exp, 1e-9))
        sig = (stats.poisson.sf(obs - 1, np.maximum(exp, 1e-9)) < 0.05 / (2 * len(qubits))) & (exp > 0)
        neg = (stats.poisson.cdf(obs, np.maximum(exp, 1e-9)) < 0.05 / (2 * len(qubits))) & (exp >= 5)
        r = runs5(y)
        out[label] = (int(sig.sum()), int(neg.sum()), r[0], round(r[1], 2))
        if label == "data" and sig.any():
            ratios = []
            for lag in (1, 2, 3):
                o, e = lag_stats(y, lag)
                ratios.append(round(float(o[sig].sum() / e[sig].sum()), 2))
            out["lag_ratio_123"] = ratios
    r = np.corrcoef(x[:, x.std(0) > 0].T.astype(float))
    q = [qq for qq, s in zip(qubits, x.std(0) > 0, strict=True) if s]
    d = dist[ds["backend"]][np.ix_(q, q)]
    iu = np.triu_indices(len(q), 1)
    means = [round(float(r[iu][d[iu] == h].mean()), 5) for h in (1, 2)] + [round(float(r[iu][d[iu] >= 11].mean()), 5)]
    p = blocks_p(x)
    tot["drift_cols"] += len(p)
    tot["drift_hit"] += int((p < 1e-7).sum())
    print(
        ds["id"][-36:],
        "N",
        n,
        "Q",
        len(qubits),
        "rep_us",
        round(ds["rep_delay_s"] * 1e6),
        "| lag1 sig+,sig-,runs>=5 obs,exp: data",
        out["data"],
        "control",
        out["control"],
        "| lag ratios",
        out.get("lag_ratio_123"),
        "| r at 1,2,11+ hops",
        means,
        "| drift cols p<1e-7:",
        int((p < 1e-7).sum()),
        "of",
        len(p),
        flush=True,
    )
print("drift total", tot)

print("== ibm_fez actor pilot, pair (7, 8)")
joint = exp = 0.0
shots = 0
for ds in sets:
    if ds["kind"] != "pilot":
        continue
    x, ids = common.load_errors(ds)
    a, b = x[:, ids.index(7)], x[:, ids.index(8)]
    joint += int((a & b).sum())
    exp += a.sum() * b.sum() / x.shape[0]
    shots += x.shape[0]
print(
    "shots",
    shots,
    "joint",
    joint,
    "expected",
    round(exp, 2),
    "log10 p",
    round(math.log10(stats.poisson.sf(joint - 1, exp)), 1),
)
