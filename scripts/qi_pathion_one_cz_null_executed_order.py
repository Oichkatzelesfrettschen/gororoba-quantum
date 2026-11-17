"""Executed-order drift correction of the bracketed twin contrasts (preregistered 2026-11-15, issue 791).

The bracketed layout puts both coin twins of a template in one batch, so the twin contrast t = P1 - P0 of a batch
carries a drift term g x x: g is the change of the selector offset per position between consecutive jobs and x is the
executed position of the coin-1 twin minus that of the coin-0 twin within the batch (the order of `queued_at`). The
requested order alternates forward and mirror rounds (x = +1 and -1), so x sums to zero per template and the term
cancels in the pooled contrast. The platform sets the execution order, not the queue (7 of the predecessor's 19
batches and 2 of the 4 hosted QX batches ran out of order by `queued_at`), and a reordered batch changes its own x,
for example to -3 when the coin-1 twin runs three places before the coin-0 twin.

A rule that refused the whole series on one reordered batch would decide almost never at that rate, so the decision
(`evaluate` of `qi_pathion_one_cz_null_bracketed_cases`) reads x from the executed order and fits one drift
g shared by the twin batches beside one contrast per template, by weighted least squares:

    v_b = t_T + g x_b + e_b,   w_b = 1 / se_b^2,   T = the template of batch b.

With W_T = sum w, x_T = sum(w x) / W_T and v_T = sum(w v) / W_T, the fit is g = Sxy / Sxx with Sxx = sum_T sum_b w (x
- x_T)^2 and Sxy = sum_T sum_b w (x - x_T)(v - v_T), var(g) = 1 / Sxx, t_T = v_T - g x_T and var(t_T) = 1 / W_T +
x_T^2 var(g). A balanced order (x_T = 0) returns the pooled mean and its error. `adjusted_rows` returns the rows the
preregistered rule reads: each twin value reduced by g x and each error multiplied by f_T = sqrt(1 + x_T^2 var(g)
W_T), so the inverse-variance mean of the adjusted rows is t_T with the error above. A series in which every template
has one x in all its twin batches has Sxx = 0 and no separable drift (the templates may differ in direction): it reads
`unresolved_order_confounded`.

hypothesis: one drift g, linear in the executed position difference, is common to every template (a device property of
the selector offset between consecutive jobs). The fit reports each template's own drift beside it, `template_drift`,
so a template whose drift departs from g by more than its error is a finding and not a quiet bias. Scope: the twin
contrasts only; the base and calibration batches reorder as well and carry no rule here.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

import numpy as np
from scipy.stats import chi2

Row = tuple[float, float, float]  # (twin contrast, standard error, executed position offset x of the batch)


class ConfoundedOrder(ValueError):
    """Every template has one offset in all its twin batches, so the drift and the contrasts are not separable."""


def executed_offset(stamps: Mapping[str, str], coin0_file: str, coin1_file: str) -> int:
    """Executed position of the coin-1 twin minus that of the coin-0 twin among the circuits of one batch, ordered by
    `queued_at`; equal stamps anywhere in the batch order nothing."""
    if len(set(stamps.values())) != len(stamps):
        raise ConfoundedOrder("two circuits of the batch carry one start stamp")
    rank = {name: place for place, name in enumerate(sorted(stamps, key=lambda name: stamps[name]))}
    return rank[coin1_file] - rank[coin0_file]


def fit(rows: Mapping[str, Sequence[Row]]) -> dict[str, object]:
    """The shared drift g, its error and the contrast and error of every template."""
    weighted = {}
    for name, batch_rows in rows.items():
        if not batch_rows:
            raise ValueError(f"template {name} holds no twin batch")
        for value, se, offset in batch_rows:
            if (
                not (math.isfinite(value) and math.isfinite(se) and se > 0.0)
                or not math.isfinite(offset)
                or offset == 0
            ):
                raise ValueError(f"template {name}: a twin row ({value}, {se}, {offset}) is not usable")
        w = [1.0 / (se * se) for _, se, _ in batch_rows]
        total = sum(w)
        weighted[name] = (
            total,
            sum(wi * s for wi, (_, _, s) in zip(w, batch_rows, strict=True)) / total,
            sum(wi * v for wi, (v, _, _) in zip(w, batch_rows, strict=True)) / total,
            w,
        )
    if all(len({x for _, _, x in batch_rows}) == 1 for batch_rows in rows.values()):
        raise ConfoundedOrder("every template has one position offset in all its twin batches")
    sxx = sxy = 0.0
    for name, batch_rows in rows.items():
        _, s_bar, v_bar, w = weighted[name]
        for wi, (v, _, s) in zip(w, batch_rows, strict=True):
            sxx += wi * (s - s_bar) * (s - s_bar)
            sxy += wi * (s - s_bar) * (v - v_bar)
    if sxx <= 0.0:
        raise ConfoundedOrder("the twin batches carry no variation of the position offset")
    drift, var_drift = sxy / sxx, 1.0 / sxx
    contrast, error, own_drift, own_diff_se = {}, {}, {}, {}
    for name, batch_rows in rows.items():
        total, s_bar, v_bar, w = weighted[name]
        contrast[name] = v_bar - drift * s_bar
        error[name] = math.sqrt(1.0 / total + s_bar * s_bar * var_drift)
        own = sum(wi * (s - s_bar) * s for wi, (_, _, s) in zip(w, batch_rows, strict=True))
        own_drift[name] = (
            None
            if own <= 0.0
            else sum(wi * (s - s_bar) * (v - v_bar) for wi, (v, _, s) in zip(w, batch_rows, strict=True)) / own
        )
        # The shared drift is the own drifts averaged with weights own / Sxx, so cov(own_T, g) = var(g) and
        # var(own_T - g) = 1 / own_T - 1 / Sxx.
        own_diff_se[name] = None if own <= 0.0 else math.sqrt(max(1.0 / own - var_drift, 0.0))
    return {
        "drift": drift,
        "drift_se": math.sqrt(var_drift),
        "contrast": contrast,
        "error": error,
        "template_drift": own_drift,
        "template_drift_difference_se": own_diff_se,
    }


def adjusted_rows(rows: Mapping[str, Sequence[Row]]) -> dict[str, list[tuple[float, float]]]:
    """The (value, se) rows of each template that the preregistered rule pools: values reduced by the drift term, errors
    multiplied by f_T, so the inverse-variance mean and error equal `fit`'s contrast and error."""
    solved = fit(rows)
    drift = float(solved["drift"])  # type: ignore[arg-type]
    var_drift = float(solved["drift_se"]) ** 2  # type: ignore[arg-type]
    out: dict[str, list[tuple[float, float]]] = {}
    for name, batch_rows in rows.items():
        w = [1.0 / (se * se) for _, se, _ in batch_rows]
        total = sum(w)
        s_bar = sum(wi * s for wi, (_, _, s) in zip(w, batch_rows, strict=True)) / total
        inflate = math.sqrt(1.0 + s_bar * s_bar * var_drift * total)
        out[name] = [(v - drift * s, se * inflate) for v, se, s in batch_rows]
    return out


def operating_characteristics(
    rate: float, requested: Sequence[int] = (1, -1, 1, -1), templates: int = 4
) -> dict[str, float]:
    """Exact enumeration, with no random draw, of the confounded probability and of the mean and 95th percentile of
    the error ratio of the first template's contrast against the balanced design, when each twin batch flips its own
    sign independently with probability `rate` (a model: hypothesis, independent reordering, equal batch errors, a
    drift linear in the sign). The retained distribution of executed offsets replaces the flip model once measured."""
    if not (math.isfinite(rate) and 0.0 <= rate <= 1.0) or templates < 1:
        raise ValueError("the flip rate lies outside [0, 1] or the template count is not positive")
    if not requested or any(x not in (-1, 1) for x in requested):
        raise ValueError("the requested pattern is empty or holds an entry other than +1 or -1")
    n = templates * len(requested)
    ratios: list[tuple[float, float]] = []
    confounded = 0.0
    for mask in range(1 << n):
        flips = [(mask >> i) & 1 for i in range(n)]
        weight = math.prod(rate if f else 1.0 - rate for f in flips)
        names = [f"t{k}" for k in range(templates)]
        rows = {
            name: [(0.0, 1.0, float(-s if flips[k * len(requested) + i] else s)) for i, s in enumerate(requested)]
            for k, name in enumerate(names)
        }
        try:
            error = fit(rows)["error"]["t0"]  # type: ignore[index]
        except ConfoundedOrder:
            confounded += weight
            continue
        ratios.append((float(error) * math.sqrt(len(requested)), weight))
    live = sum(w for _, w in ratios)
    mean = sum(r * w for r, w in ratios) / live
    ordered = sorted(ratios)
    cumulative, p95 = 0.0, ordered[-1][0]
    for ratio, w in ordered:
        cumulative += w
        if cumulative >= 0.95 * live:
            p95 = ratio
            break
    return {"confounded": confounded, "mean_error_ratio": mean, "p95_error_ratio": p95}


def constrained_weights(times: Sequence[float], ses: Sequence[float], reference: float, order: int = 1) -> list[float]:
    """Weights w of the minimum-variance level at `reference` that annihilates a drift polynomial of `order`.

    Model: v_r = mu + sum_{k=1..order} g_k (t_r - reference)^k + e_r, var(e_r) = se_r^2. The estimator mu_hat = sum
    w_r v_r is unbiased for mu whatever g_k are exactly when B^T w = e_0, with B_rk = (t_r - reference)^k for k =
    0..order (so sum w = 1 and sum w (t - reference)^k = 0), and the minimum-variance solution is w = C^-1 B (B^T
    C^-1 B)^-1 e_0 with C = diag(se^2): the weighted regression's intercept at `reference`. For order 1, var(mu_hat)
    = (1 / W)(1 + (t_w - reference)^2 / S_tt) with W = sum 1/se^2, t_w the inverse-variance mean time and S_tt = sum
    (t - t_w)^2 / se^2 / W, so the cost over the plain mean is 1 + (t_w - reference)^2 / S_tt: nothing when the
    weighted mean time is the reference, and large when the replicates cluster in time. Fewer distinct times than
    order + 1 leave the polynomial unseparated.
    """
    if order < 0 or len(times) != len(ses) or len(set(times)) < order + 1:
        raise ConfoundedOrder("the replicate times cannot separate the drift polynomial from the level")
    if not all(math.isfinite(x) and x > 0.0 for x in ses) or not all(math.isfinite(t) for t in (*times, reference)):
        raise ValueError("a replicate time, reference or error is not usable")
    shifted = np.asarray(times, dtype=float) - reference
    design = np.vander(shifted, order + 1, increasing=True)
    precision = np.diag(1.0 / np.asarray(ses, dtype=float) ** 2)
    information = design.T @ precision @ design
    unit = np.zeros(order + 1)
    unit[0] = 1.0
    solved = np.linalg.solve(information, unit)
    return [float(x) for x in precision @ design @ solved]


def level_at(
    values: Sequence[float], ses: Sequence[float], times: Sequence[float], reference: float, order: int = 1
) -> tuple[float, float]:
    """(level at `reference`, its standard error) from `constrained_weights`; the variance is sum w^2 se^2."""
    if len(values) != len(times) or not all(math.isfinite(v) for v in values):
        raise ValueError("a replicate value is not usable")
    weights = constrained_weights(times, ses, reference, order)
    level = sum(w * v for w, v in zip(weights, values, strict=True))
    return level, math.sqrt(sum(w * w * se * se for w, se in zip(weights, ses, strict=True)))


MONITOR_ALPHA = 0.001


def drift_monitor(times: Sequence[float], values: Sequence[float], ses: Sequence[float]) -> dict[str, float | bool]:
    """The preregistered check of the linear drift model on a reference series (the readout offset of every batch).
    Weighted least squares of the series on time gives a slope and its error; the residual chi-square has n - 2
    degrees of freedom and exceeds the alpha = MONITOR_ALPHA quantile when the series carries more than a line plus
    its shot noise (a step, a burst, a curve). `adequate` is False then. A slope that departs from zero is a finding
    about the drift rate, and not a failure of the model.
    """
    n = len(times)
    if n < 3 or len(values) != n or len(ses) != n or len(set(times)) < 2:
        raise ConfoundedOrder("the reference series cannot fit a line and test its residual")
    if not all(math.isfinite(x) and x > 0.0 for x in ses) or not all(math.isfinite(x) for x in (*times, *values)):
        raise ValueError("a series time, value or error is not usable")
    weights = [1.0 / (se * se) for se in ses]
    total = sum(weights)
    mean_t = sum(w * t for w, t in zip(weights, times, strict=True)) / total
    mean_v = sum(w * v for w, v in zip(weights, values, strict=True)) / total
    stt = sum(w * (t - mean_t) ** 2 for w, t in zip(weights, times, strict=True))
    slope = sum(w * (t - mean_t) * (v - mean_v) for w, t, v in zip(weights, times, values, strict=True)) / stt
    statistic = sum(
        w * (v - mean_v - slope * (t - mean_t)) ** 2 for w, t, v in zip(weights, times, values, strict=True)
    )
    threshold = float(chi2.ppf(1.0 - MONITOR_ALPHA, n - 2))
    return {
        "slope": slope,
        "slope_se": math.sqrt(1.0 / stt),
        "chi_square": statistic,
        "degrees_of_freedom": float(n - 2),
        "threshold": threshold,
        "adequate": statistic <= threshold,
    }
