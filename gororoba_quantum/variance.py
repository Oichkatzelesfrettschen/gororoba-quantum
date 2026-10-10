"""Shot, layout, and instance variance of replicated measurements.

Each shot of a circuit with ideal distribution q scores w(x) = q(x) / max q,
so a deterministic ideal scores the success indicator and a uniform-support
ideal scores the support indicator; a member may instead declare its own
per-outcome weights, such as the indicator of outcomes that decode to a
factor. A replica's estimate is the mean score over its shots, whose shot
variance (sum_x p(x) w(x)^2 - mean^2) / S follows from the measured
distribution p alone. Replicas of one circuit on disjoint layouts then
separate layout variance from shot variance by a one-way random effects
decomposition, and members that are equal-cost instances of one experiment
add an instance axis through a two-way additive decomposition
(literature/notes/2509.18259.md, Eq. 4-5; literature/notes/2507.08088.md,
action item 3).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import numpy as np
from scipy import stats

OUTLIER_SIGMA = 3.0
CONFIDENCE = 0.95


def score(dist: np.ndarray, ideal: np.ndarray, weights: np.ndarray | None = None) -> tuple[float, float]:
    """Mean per-shot score of dist and its per-shot variance.

    weights assigns each outcome a score in [0, 1]; without it, the score is
    the ideal-weighted w(x) = q(x) / max q.
    """
    if weights is None:
        peak = float(np.max(ideal))
        weight = np.asarray(ideal) / peak if peak > 0 else np.zeros_like(ideal)
    else:
        weight = np.asarray(weights, dtype=float)
    mean = float(np.dot(dist, weight))
    second = float(np.dot(dist, weight**2))
    return mean, max(second - mean * mean, 0.0)


def decompose(values: Sequence[float], per_shot_variances: Sequence[float], shots: int) -> dict[str, Any]:
    """Split the spread of per-replica scores into shot and layout variance.

    shot_variance is the mean over replicas of each replica's per-shot variance
    over shots. layout_variance is the sample variance across replicas minus
    that shot variance, floored at zero. The chi-squared statistic tests
    whether the replicas agree within shot noise alone, and a replica more than
    OUTLIER_SIGMA shot standard deviations from the median is an outlier.
    """
    count = len(values)
    mean = float(np.mean(values))
    shot_var = float(np.mean(per_shot_variances)) / shots
    out: dict[str, Any] = {"replicas": float(count), "mean": mean, "shot_variance": shot_var}
    if count < 2:
        return out
    between = float(np.var(values, ddof=1))
    median = float(np.median(values))
    shot_sd = math.sqrt(shot_var)
    out |= {
        "between_replica_variance": between,
        "layout_variance": max(between - shot_var, 0.0),
        "median": median,
        "outliers": [i for i, v in enumerate(values) if shot_sd > 0 and abs(v - median) > OUTLIER_SIGMA * shot_sd],
    }
    if shot_var > 0:
        chi2 = float(np.sum((np.asarray(values) - mean) ** 2) / shot_var)
        out |= {"chi2": chi2, "dof": float(count - 1), "p_value": float(stats.chi2.sf(chi2, count - 1))}
    return out


def instance_layout(table: np.ndarray, per_shot_variances: np.ndarray, shots: int) -> dict[str, float]:
    """Two-way additive decomposition of instance-by-replica scores.

    table[m, k] is instance m's score on replica k. Instance effects are
    constant across replicas, layout effects constant across instances, and
    the residual mean square estimates their interaction plus shot noise; each
    component is the expected-mean-square difference, floored at zero.
    """
    rows, cols = table.shape
    grand = float(table.mean())
    row_means = table.mean(axis=1)
    col_means = table.mean(axis=0)
    ss_rows = cols * float(np.sum((row_means - grand) ** 2))
    ss_cols = rows * float(np.sum((col_means - grand) ** 2))
    residual = table - row_means[:, None] - col_means[None, :] + grand
    ss_res = float(np.sum(residual**2))
    ms_res = ss_res / ((rows - 1) * (cols - 1))
    shot_var = float(np.mean(per_shot_variances)) / shots
    return {
        "instances": float(rows),
        "replicas": float(cols),
        "shot_variance": shot_var,
        "instance_variance": max((ss_rows / (rows - 1) - ms_res) / cols, 0.0),
        "layout_variance": max((ss_cols / (cols - 1) - ms_res) / rows, 0.0),
        "interaction_variance": max(ms_res - shot_var, 0.0),
    }


def interval(values: Sequence[float], shots: int, bernoulli: bool) -> dict[str, Any]:
    """Mean and CONFIDENCE interval of a per-replica quantity.

    Two or more replicas give a Student t interval over the replica values,
    which carries shot and layout variance together. A per-shot Bernoulli rate
    also gets a Wilson interval over the pooled shots, which carries shot
    variance alone and keeps its width when the replicas happen to agree
    exactly; the reported interval is the union of the two. Any other
    single-replica quantity has no interval.
    """
    count = len(values)
    mean = float(np.mean(values))
    bounds: list[tuple[float, float]] = []
    methods = []
    if count >= 2:
        half = float(stats.t.ppf(0.5 + CONFIDENCE / 2, count - 1)) * float(np.std(values, ddof=1)) / math.sqrt(count)
        bounds.append((mean - half, mean + half))
        methods.append(f"student_t_over_{count}_replicas")
    if bernoulli:
        bounds.append(_wilson(mean, count * shots))
        methods.append(f"wilson_over_{count * shots}_shots")
    if not bounds:
        return {"mean": mean, "method": "single_replica_no_interval"}
    return {
        "mean": mean,
        "lo": min(lo for lo, _ in bounds),
        "hi": max(hi for _, hi in bounds),
        "method": "_union_".join(methods),
    }


def _wilson(rate: float, trials: int) -> tuple[float, float]:
    z = float(stats.norm.ppf(0.5 + CONFIDENCE / 2))
    denom = 1 + z * z / trials
    center = (rate + z * z / (2 * trials)) / denom
    half = z * math.sqrt(rate * (1 - rate) / trials + z * z / (4 * trials * trials)) / denom
    return center - half, center + half


def _verify() -> None:
    rng = np.random.default_rng(20261011)
    shots, replicas = 4096, 12
    ideal = np.array([0.0, 1.0])
    # Equal true rates: the decomposition finds shot noise and no layout term.
    flat = [rng.binomial(shots, 0.9) / shots for _ in range(replicas)]
    flat_stats = decompose(flat, [score(np.array([1 - v, v]), ideal)[1] for v in flat], shots)
    if not 0.001 < float(flat_stats["p_value"]) or float(flat_stats["layout_variance"]) > 4 * float(
        flat_stats["shot_variance"]
    ):
        raise RuntimeError(f"equal-rate replicas read as layout-dependent: {flat_stats}")
    # True rates spread by sd 0.02: the layout term recovers about 4e-4.
    rates = rng.normal(0.9, 0.02, size=200)
    spread = [rng.binomial(shots, r) / shots for r in rates]
    spread_stats = decompose(spread, [score(np.array([1 - v, v]), ideal)[1] for v in spread], shots)
    if not 2.5e-4 < float(spread_stats["layout_variance"]) < 6e-4:
        raise RuntimeError(f"layout variance {spread_stats['layout_variance']} misses the injected 4e-4")
    # Instance and layout effects of sd 0.03 and 0.02 separate in the two-way table.
    inst = rng.normal(0, 0.03, size=40)[:, None]
    lay = rng.normal(0, 0.02, size=40)[None, :]
    table = np.clip(0.8 + inst + lay, 0, 1)
    sampled = rng.binomial(shots, table) / shots
    two_way = instance_layout(sampled, sampled * (1 - sampled), shots)
    if not (5e-4 < two_way["instance_variance"] < 1.5e-3 and 2e-4 < two_way["layout_variance"] < 7e-4):
        raise RuntimeError(f"two-way decomposition misses the injected components: {two_way}")
    wilson = interval([0.5], 7, bernoulli=True)
    if not (float(wilson["lo"]) > 0 and float(wilson["hi"]) < 1):
        raise RuntimeError(f"Wilson interval leaves [0, 1]: {wilson}")
    # Replicas that all read zero keep the shot uncertainty of their pooled shots.
    agreed = interval([0.0, 0.0, 0.0], 64, bernoulli=True)
    if not float(agreed["hi"]) > 0.01:
        raise RuntimeError(f"identical replicas collapse the interval: {agreed}")
    print("variance: shot, layout, and instance components recover injected values; intervals bounded")


if __name__ == "__main__":
    _verify()
