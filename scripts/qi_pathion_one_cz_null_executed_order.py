"""Executed-order drift correction of the bracketed twin contrasts (preregistered 2026-11-15, issue 791).

The bracketed layout puts both coin twins of a template in one batch, so the twin contrast t = P1 - P0 of a batch
carries a drift term g x s: g is the change of the selector offset between two consecutive jobs and s is +1 when the
coin-1 twin executes after the coin-0 twin and -1 otherwise. The requested order alternates forward and mirror rounds,
so s sums to zero per template and the term cancels in the pooled contrast. The platform sets the execution order, not
the queue (7 of the predecessor's 19 batches ran out of order by `queued_at`), and a reordered batch flips its own s.

The strict gate (`order_gate` of `qi_pathion_one_cz_null_bracketed_cases`) refuses the whole series on one reordered
batch, which at that rate decides almost never. This module reads s from the executed order instead and fits one drift
g shared by the twin batches beside one contrast per template, by weighted least squares:

    v_b = t_T + g s_b + e_b,   w_b = 1 / se_b^2,   T = the template of batch b.

With W_T = sum w, s_T = sum(w s) / W_T and v_T = sum(w v) / W_T, the fit is g = Sxy / Sxx with Sxx = sum_T sum_b w (s
- s_T)^2 and Sxy = sum_T sum_b w (s - s_T)(v - v_T), var(g) = 1 / Sxx, t_T = v_T - g s_T and var(t_T) = 1 / W_T +
s_T^2 var(g). A balanced order (s_T = 0) returns the pooled mean and its error. `adjusted_rows` returns the rows the
preregistered rule reads: each twin value reduced by g s and each error multiplied by f_T = sqrt(1 + s_T^2 var(g)
W_T), so the inverse-variance mean of the adjusted rows is t_T with the error above. A series whose twin batches all
share one executed s has Sxx = 0 and no separable drift: it reads `unresolved_order_confounded`.

hypothesis: one drift g is common to every template (a device property of the selector offset between consecutive
jobs). The fit reports each template's own drift beside it, `template_drift`, so a template whose drift departs from g
by more than its error is a finding and not a quiet bias."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

Row = tuple[float, float, int]  # (twin contrast, standard error, executed sign s of the batch)


class ConfoundedOrder(ValueError):
    """Every twin batch of the series executed in one direction, so the drift and the contrasts are not separable."""


def executed_sign(stamp_coin0: str, stamp_coin1: str) -> int:
    """+1 when the coin-1 twin executed after the coin-0 twin, -1 when before; equal stamps order nothing."""
    if stamp_coin0 == stamp_coin1:
        raise ConfoundedOrder("the two twins carry one start stamp")
    return 1 if stamp_coin1 > stamp_coin0 else -1


def fit(rows: Mapping[str, Sequence[Row]]) -> dict[str, object]:
    """The shared drift g, its error and the contrast and error of every template."""
    weighted = {}
    for name, batch_rows in rows.items():
        if not batch_rows:
            raise ValueError(f"template {name} holds no twin batch")
        for value, se, sign in batch_rows:
            if not (math.isfinite(value) and math.isfinite(se) and se > 0.0) or sign not in (-1, 1):
                raise ValueError(f"template {name}: a twin row ({value}, {se}, {sign}) is not usable")
        w = [1.0 / (se * se) for _, se, _ in batch_rows]
        total = sum(w)
        weighted[name] = (
            total,
            sum(wi * s for wi, (_, _, s) in zip(w, batch_rows, strict=True)) / total,
            sum(wi * v for wi, (v, _, _) in zip(w, batch_rows, strict=True)) / total,
            w,
        )
    sxx = sxy = 0.0
    for name, batch_rows in rows.items():
        _, s_bar, v_bar, w = weighted[name]
        for wi, (v, _, s) in zip(w, batch_rows, strict=True):
            sxx += wi * (s - s_bar) * (s - s_bar)
            sxy += wi * (s - s_bar) * (v - v_bar)
    if sxx <= 0.0:
        raise ConfoundedOrder("every twin batch executed in the same direction")
    drift, var_drift = sxy / sxx, 1.0 / sxx
    contrast, error, own_drift = {}, {}, {}
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
    return {
        "drift": drift,
        "drift_se": math.sqrt(var_drift),
        "contrast": contrast,
        "error": error,
        "template_drift": own_drift,
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
