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


# Preregistered absolute equivalence margin on a packed-minus-reference score
# difference; the TOST reads a 90 percent interval against it.
EQUIVALENCE_MARGIN = 0.03
# Shots per arm below which no inferential verdict is issued. The difference
# interval is Newcombe's continuity-corrected hybrid score interval (method
# 11): exact enumeration of two equal Bernoulli arms (false_detection_rate)
# over true rates 0.005 to 0.995 in steps of 0.005 puts the probability that
# its 95 percent interval excludes zero at 0.0416 for 64 shots, 0.0420 for
# 128, 0.0466 for 256, 0.0472 for 512, 0.0482 for 1024, and 0.0488 for 4096
# (step 0.01), below the nominal 0.05 at every enumerated size; the
# uncorrected interval (method 10) exceeds it at every one of those sizes,
# 0.0555 at 64 down to 0.0506 at 4096. The floor is the smallest enumerated
# size, and the self-test enumerates the floor and 1024.
EQUIVALENCE_MIN_SHOTS = 64
EQUIVALENCE_NOMINAL_FALSE_DETECTION = 0.05


def difference_interval(
    packed: float,
    packed_variance: float,
    reference: float,
    reference_variance: float,
    shots: int,
    bernoulli: bool,
    confidence: float,
) -> tuple[float, float]:
    """Interval on packed - reference, two scores each measured over shots shots.

    Both scores are means of per-shot weights in [0, 1]. The interval is
    Newcombe's hybrid score interval built from the two continuity-corrected
    Wilson intervals (Newcombe 1998, method 11), whose false-detection
    probability stays below nominal at every enumerated size (see
    EQUIVALENCE_MIN_SHOTS). For a Bernoulli score (every weight 0 or 1) it is
    a proportion interval. For any other [0, 1]-bounded score the
    Bhatia-Davis inequality bounds the per-shot variance by mean (1 - mean),
    so the same interval is conservative: it never shrinks to zero width when
    the observed shots happen to share one score, as a plug-in normal
    interval does, and it stays inside [-1, 1]. The plug-in variances are
    retained by the caller for the z diagnostic only.
    """
    del packed_variance, reference_variance, bernoulli
    difference = packed - reference
    packed_low, packed_high = _wilson_continuity_corrected(packed, shots, confidence)
    reference_low, reference_high = _wilson_continuity_corrected(reference, shots, confidence)
    return (
        difference - math.sqrt((packed - packed_low) ** 2 + (reference_high - reference) ** 2),
        difference + math.sqrt((packed_high - packed) ** 2 + (reference - reference_low) ** 2),
    )


def equivalence(
    packed: float,
    packed_variance: float,
    reference: float,
    reference_variance: float,
    shots: int,
    bernoulli: bool,
    margin: float = EQUIVALENCE_MARGIN,
) -> dict[str, Any]:
    """Difference detection and two-one-sided equivalence of packed against reference.

    The 95 percent interval reports the difference. The 90 percent interval
    inside [-margin, margin] establishes equivalence within the margin (two
    one-sided tests at 5 percent each); a 95 percent interval below zero
    detects packed degradation and one above zero detects packed
    improvement; otherwise the difference is not resolved. A difference can
    be both resolved and inside the margin, so the three flags are reported
    beside the verdict, and a reader of the verdict alone sees equivalence
    first, then the resolved sign.
    """
    interval_95 = difference_interval(packed, packed_variance, reference, reference_variance, shots, bernoulli, 0.95)
    interval_90 = difference_interval(packed, packed_variance, reference, reference_variance, shots, bernoulli, 0.90)
    within = -margin <= interval_90[0] and interval_90[1] <= margin
    below = interval_95[1] < 0
    above = interval_95[0] > 0
    if shots < EQUIVALENCE_MIN_SHOTS:
        verdict = "insufficient_shots"
        within = below = above = False
    elif within:
        verdict = f"equivalent_within_{margin:g}"
    elif below:
        verdict = "packed_degradation_detected"
    elif above:
        verdict = "packed_improvement_detected"
    else:
        verdict = "difference_not_resolved"
    return {
        "method": "newcombe_wilson" if bernoulli else "newcombe_wilson_bhatia_davis",
        "margin": margin,
        "difference_interval_95": list(interval_95),
        "difference_interval_90": list(interval_90),
        "within_margin": within,
        "below_zero_95": below,
        "above_zero_95": above,
        "verdict": verdict,
    }


def false_detection_rate(shots: int, rate: float, confidence: float = 0.95) -> float:
    """Probability that the difference interval excludes zero for two equal Bernoulli arms at rate.

    Exact enumeration over the (shots + 1)^2 outcome pairs; the interval is
    the same continuity-corrected hybrid score interval difference_interval
    uses.
    """
    counts = np.arange(shots + 1)
    pmf = stats.binom.pmf(counts, shots, rate)
    observed = counts / shots
    low = np.empty(shots + 1)
    high = np.empty(shots + 1)
    for index, value in enumerate(observed):
        low[index], high[index] = _wilson_continuity_corrected(float(value), shots, confidence)
    first, second = observed[:, None], observed[None, :]
    difference = first - second
    lower = difference - np.sqrt((first - low[:, None]) ** 2 + (high[None, :] - second) ** 2)
    upper = difference + np.sqrt((high[:, None] - first) ** 2 + (second - low[None, :]) ** 2)
    excluded = (upper < 0) | (lower > 0)
    return float((pmf[:, None] * pmf[None, :] * excluded).sum())


def _wilson_continuity_corrected(rate: float, trials: int, confidence: float) -> tuple[float, float]:
    """Wilson score interval with continuity correction (Newcombe 1998, method 4), clipped to [0, 1]."""
    z = float(stats.norm.ppf(0.5 + confidence / 2))
    n = trials
    if rate <= 0:
        low = 0.0
    else:
        low = (2 * n * rate + z * z - 1 - z * math.sqrt(z * z - 2 - 1 / n + 4 * rate * (n * (1 - rate) + 1))) / (
            2 * (n + z * z)
        )
    if rate >= 1:
        high = 1.0
    else:
        high = (2 * n * rate + z * z + 1 + z * math.sqrt(z * z + 2 - 1 / n + 4 * rate * (n * (1 - rate) - 1))) / (
            2 * (n + z * z)
        )
    return max(low, 0.0), min(high, 1.0)


def _wilson(rate: float, trials: int, confidence: float = CONFIDENCE) -> tuple[float, float]:
    z = float(stats.norm.ppf(0.5 + confidence / 2))
    denom = 1 + z * z / trials
    center = (rate + z * z / (2 * trials)) / denom
    half = z * math.sqrt(rate * (1 - rate) / trials + z * z / (4 * trials * trials)) / denom
    return center - half, center + half


def _verify_equivalence() -> None:
    shots = 4096
    same = equivalence(0.50, 0.25, 0.50, 0.25, shots, True)
    if same["verdict"] != "equivalent_within_0.03" or not same["within_margin"] or same["below_zero_95"]:
        raise RuntimeError(f"equal rates at {shots} shots read {same}")
    low, high = same["difference_interval_95"]
    if not (-0.03 < low < 0 < high < 0.03) or same["method"] != "newcombe_wilson":
        raise RuntimeError(f"equal-rate interval is {same}")
    worse = equivalence(0.40, 0.24, 0.50, 0.25, shots, True)
    if worse["verdict"] != "packed_degradation_detected" or worse["within_margin"]:
        raise RuntimeError(f"a 0.10 drop reads {worse}")
    coarse = equivalence(0.49, 0.25, 0.50, 0.25, 1024, True)
    if coarse["verdict"] != "difference_not_resolved" or coarse["within_margin"] or coarse["below_zero_95"]:
        raise RuntimeError(f"1024 shots at a 0.01 difference read {coarse}")
    # The error bound is enumerated, not assumed: at the floor over the fine
    # grid and at 1024 over a coarser one, the false-detection probability of
    # two equal arms stays below nominal.
    fine = [round(0.005 * step, 3) for step in range(1, 200)]
    for arm_shots, grid in ((EQUIVALENCE_MIN_SHOTS, fine), (1024, fine[::10])):
        worst = max(false_detection_rate(arm_shots, rate) for rate in grid)
        if not worst <= EQUIVALENCE_NOMINAL_FALSE_DETECTION:
            raise RuntimeError(f"false detection at {arm_shots} shots is {worst:.4f}, above nominal")
    below = equivalence(0.0, 0.0, 1.0, 0.0, EQUIVALENCE_MIN_SHOTS - 1, True)
    if below["verdict"] != "insufficient_shots":
        raise RuntimeError(f"one shot below the floor issues a verdict: {below}")
    small = equivalence(0.49, 0.25, 0.50, 0.25, 65536, True)
    if small["verdict"] != "equivalent_within_0.03" or not small["below_zero_95"]:
        raise RuntimeError(f"a resolved 0.01 drop inside the margin reads {small}")
    bounded = equivalence(0.50, 0.25, 0.50, 0.25, shots, False)
    if (
        bounded["method"] != "newcombe_wilson_bhatia_davis"
        or bounded["difference_interval_95"] != same["difference_interval_95"]
    ):
        raise RuntimeError(f"the bounded-score interval differs from the Bernoulli one at equal means: {bounded}")
    one_shot = equivalence(0.6, 0.0, 0.6, 0.0, 1, False)
    low_90, high_90 = one_shot["difference_interval_90"]
    if one_shot["verdict"] != "insufficient_shots" or high_90 - low_90 < 0.5 or one_shot["below_zero_95"]:
        raise RuntimeError(f"one shot with zero plug-in variance issues a verdict: {one_shot}")
    two_shots = equivalence(0.0, 0.0, 1.0, 0.0, 2, True)
    if two_shots["verdict"] != "insufficient_shots" or two_shots["below_zero_95"]:
        raise RuntimeError(f"opposite endpoints at two shots per arm resolve a difference: {two_shots}")
    floor = equivalence(0.0, 0.0, 1.0, 0.0, EQUIVALENCE_MIN_SHOTS, True)
    if floor["verdict"] != "packed_degradation_detected":
        raise RuntimeError(f"the shot floor withholds a verdict at the floor: {floor}")
    better = equivalence(0.60, 0.24, 0.50, 0.25, shots, True)
    if better["verdict"] != "packed_improvement_detected" or not better["above_zero_95"] or better["within_margin"]:
        raise RuntimeError(f"a 0.10 gain reads {better}")
    edge = equivalence(0.0, 0.0, 0.0, 0.0, shots, True)
    if edge["difference_interval_95"][0] < -1 or edge["difference_interval_95"][1] > 1:
        raise RuntimeError(f"Newcombe interval leaves [-1, 1] at p = 0: {edge}")


def _verify() -> None:
    _verify_equivalence()
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
    print(
        "variance: shot, layout, and instance components recover injected values; "
        "intervals bounded; equivalence verdicts classified"
    )


if __name__ == "__main__":
    _verify()
