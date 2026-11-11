"""Independent recomputation of five leads of REPORT.md with plain statistics.

common.py supplies only the dataset list, the error matrices and the coupler graph. Each statistic is recomputed
here; `control` repeats the lag and run statistics after the fixed reordering n -> 7919 n mod N of the shots.
The datasets are independent, so each one's statistics run through `common.ordered_map` and print in dataset order.
"""

import math
from functools import cache
from typing import Any

import common
import numpy as np
from scipy import stats


@cache
def backend_distances(backend: str) -> np.ndarray:
    """Hop distances between the qubits of one backend's coupling graph."""
    return np.asarray(common.graph_distances(common.coupling_graph(backend)))


def lag_stats(x: np.ndarray, lag: int = 1) -> tuple[np.ndarray, np.ndarray]:
    n = x.shape[0]
    k = x.sum(0).astype(float)
    obs = (x[:-lag] & x[lag:]).sum(0).astype(float)
    exp = k * k / n
    return obs, exp


def runs5(x: np.ndarray) -> tuple[int, float]:
    n = x.shape[0]
    p = x.mean(0)
    w = x[:-4] & x[1:-3] & x[2:-2] & x[3:-1] & x[4:]
    start = w.copy()
    start[1:] &= ~w[:-1].astype(bool)
    obs = start.sum()
    exp = ((n - 5) * p**5 * (1 - p) + p**5).sum()
    return int(obs), float(exp)


def blocks_p(x: np.ndarray, blocks: int = 8) -> np.ndarray:
    n = x.shape[0] // blocks * blocks
    c = x[:n].reshape(blocks, -1, x.shape[1]).sum(1).astype(float)
    m = n // blocks
    p = c.sum(0) / n
    ok = p * m >= 5
    chi = ((c - p * m) ** 2 / (p * m * (1 - p) + 1e-300)).sum(0)
    return np.asarray(stats.chi2.sf(chi[ok], blocks - 1))


def mean_or_nan(values: np.ndarray) -> float:
    """Mean of the values; an empty selection (no qubit pair at that hop distance) reads nan."""
    return float(values.mean()) if values.size else float("nan")


def state_prep_task(ds: dict[str, Any]) -> dict[str, Any]:
    """Lag, run, correlation and block-drift statistics of one state-preparation dataset, as plain printable fields."""
    x, qubits = common.load_errors(ds)
    n = x.shape[0]
    perm = (np.arange(n) * 7919) % n
    out: dict[str, Any] = {}
    for label, y in (("data", x), ("control", x[perm])):
        obs, exp = lag_stats(y)
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
    d = backend_distances(ds["backend"])[np.ix_(q, q)]
    iu = np.triu_indices(len(q), 1)
    means = [round(mean_or_nan(r[iu][d[iu] == h]), 5) for h in (1, 2)] + [round(mean_or_nan(r[iu][d[iu] >= 11]), 5)]
    p = blocks_p(x)
    return {
        "id": ds["id"][-36:],
        "n": n,
        "qubits": len(qubits),
        "rep_us": round(ds["rep_delay_s"] * 1e6),
        "data": out["data"],
        "control": out["control"],
        "lag_ratio_123": out.get("lag_ratio_123"),
        "hop_means": means,
        "drift_cols": len(p),
        "drift_hit": int((p < 1e-7).sum()),
    }


def pilot_task(ds: dict[str, Any]) -> tuple[int, float, int]:
    """Joint error count, expected joint count and shots of pair (7, 8) in one pilot dataset."""
    x, ids = common.load_errors(ds)
    a, b = x[:, ids.index(7)], x[:, ids.index(8)]
    return int((a & b).sum()), float(a.sum() * b.sum() / x.shape[0]), int(x.shape[0])


def main() -> None:
    sets = common.ground_datasets(common.catalog())

    print("== ibm_kingston state-prep PUBs")
    tot = {"drift_cols": 0, "drift_hit": 0}
    state_prep = [ds for ds in sets if ds["kind"] == "state_prep"]
    for row in common.ordered_map(state_prep_task, state_prep, min_items=1):
        tot["drift_cols"] += row["drift_cols"]
        tot["drift_hit"] += row["drift_hit"]
        print(
            row["id"],
            "N",
            row["n"],
            "Q",
            row["qubits"],
            "rep_us",
            row["rep_us"],
            "| lag1 sig+,sig-,runs>=5 obs,exp: data",
            row["data"],
            "control",
            row["control"],
            "| lag ratios",
            row["lag_ratio_123"],
            "| r at 1,2,11+ hops",
            row["hop_means"],
            "| drift cols p<1e-7:",
            row["drift_hit"],
            "of",
            row["drift_cols"],
            flush=True,
        )
    print("drift total", tot)

    print("== ibm_fez actor pilot, pair (7, 8)")
    joint = exp = 0.0
    shots = 0
    pilots = [ds for ds in sets if ds["kind"] == "pilot"]
    for pair_joint, pair_exp, pair_shots in common.ordered_map(pilot_task, pilots, min_items=1):
        joint += pair_joint
        exp += pair_exp
        shots += pair_shots
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


if __name__ == "__main__":
    main()
