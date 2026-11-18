"""Contracts of the executed-order drift fit of the bracketed twin contrasts."""

from __future__ import annotations

import math
from typing import Any

import pytest
import qi_pathion_one_cz_null_analysis as ana
import qi_pathion_one_cz_null_executed_order as eo

DRIFT = 0.01
CONTRAST = {"b0": 0.0164, "k4": -0.002, "k8": 0.003, "k12": 0.0}


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _rows(signs: dict[str, list[int]], se: float = 0.004) -> dict[str, list[eo.Row]]:
    """Noise-free twin rows: each batch reads its template's contrast plus the drift times its executed sign."""
    return {name: [(CONTRAST[name] + DRIFT * s, se, s) for s in values] for name, values in signs.items()}


BALANCED = {name: [1, -1, 1, -1] for name in CONTRAST}
REORDERED = {"b0": [-1, -1, 1, -1], "k4": [1, 1, 1, -1], "k8": [-1, -1, -1, -1], "k12": [1, -1, -1, 1]}


def test_a_balanced_order_returns_the_pooled_mean_and_error() -> None:
    rows = _rows(BALANCED)
    solved = eo.fit(rows)
    for name, batch_rows in rows.items():
        mean, se = ana.pooled([(v, e) for v, e, _ in batch_rows])
        _expect(math.isclose(solved["contrast"][name], mean, abs_tol=1e-15), f"{name} contrast")  # type: ignore[index]
        _expect(math.isclose(solved["error"][name], se, rel_tol=1e-12), f"{name} error")  # type: ignore[index]
    _expect(math.isclose(float(solved["drift"]), DRIFT, abs_tol=1e-15), f"drift {solved['drift']}")  # type: ignore[arg-type]


def test_reordered_batches_leave_the_contrast_recovered_where_the_plain_pool_is_biased() -> None:
    rows = _rows(REORDERED)
    solved = eo.fit(rows)
    _expect(math.isclose(float(solved["drift"]), DRIFT, abs_tol=1e-12), f"drift {solved['drift']}")  # type: ignore[arg-type]
    for name, batch_rows in rows.items():
        _expect(math.isclose(solved["contrast"][name], CONTRAST[name], abs_tol=1e-12), f"{name}")  # type: ignore[index]
        plain, _ = ana.pooled([(v, e) for v, e, _ in batch_rows])
        mean_sign = sum(s for _, _, s in batch_rows) / len(batch_rows)
        _expect(math.isclose(plain - CONTRAST[name], DRIFT * mean_sign, abs_tol=1e-12), f"{name}: plain pool bias")
        if mean_sign:
            _expect(abs(plain - CONTRAST[name]) > 0.4 * DRIFT, f"{name}: the plain pool is not biased")


def test_unbalanced_templates_pay_a_larger_error_and_balanced_ones_pay_none() -> None:
    solved = eo.fit(_rows(REORDERED))
    base = 0.004 / math.sqrt(4)
    errors = solved["error"]
    _expect(math.isclose(errors["k12"], base, rel_tol=1e-12), f"a balanced template pays {errors['k12']}")  # type: ignore[index]
    # f^2 = 1 + s^2 var(g) W with var(g) = 1 / (10 w) over the four templates and W = 4 w: sqrt(1.4) = 1.183
    _expect(math.isclose(errors["k8"], base * math.sqrt(1.4), rel_tol=1e-9), f"k8 pays {errors['k8']}")  # type: ignore[index]


def test_the_adjusted_rows_pool_to_the_fitted_contrast_and_error() -> None:
    rows = _rows(REORDERED)
    solved, adjusted = eo.fit(rows), eo.adjusted_rows(rows)
    for name, pairs in adjusted.items():
        mean, se = ana.pooled(pairs)
        _expect(math.isclose(mean, solved["contrast"][name], abs_tol=1e-12), f"{name} value")  # type: ignore[index]
        _expect(math.isclose(se, solved["error"][name], rel_tol=1e-12), f"{name} error")  # type: ignore[index]


def test_one_direction_in_every_batch_is_confounded_and_one_mixed_template_is_enough() -> None:
    with pytest.raises(eo.ConfoundedOrder):
        eo.fit(_rows({name: [1, 1, 1, 1] for name in CONTRAST}))
    solved = eo.fit(_rows({**{name: [1, 1, 1, 1] for name in ("b0", "k4", "k8")}, "k12": [1, -1, 1, -1]}))
    _expect(math.isclose(float(solved["drift"]), DRIFT, abs_tol=1e-12), "a mixed template does not fix the drift")  # type: ignore[arg-type]
    _expect(solved["template_drift"]["b0"] is None, "a one-direction template reports its own drift")  # type: ignore[index]


def test_executed_offset_reads_the_rank_difference_of_the_stamps_and_refuses_a_tie() -> None:
    requested = {"r0": 1, "c0": 2, "c1": 3, "r1": 4, "b": 5}
    _expect(eo.executed_offset(requested, "c0", "c1") == 1, "the requested order reads +1")
    _expect(eo.executed_offset({**requested, "c0": 3, "c1": 2}, "c0", "c1") == -1, "swapped twins")
    # the batch 02 of the hosted QX run: coin 1 ran second, coin 0 last of five
    scrambled = {"r0": 1, "c1": 2, "r1": 3, "b": 4, "c0": 5}
    _expect(eo.executed_offset(scrambled, "c0", "c1") == -3, "coin 1 three places before coin 0")
    with pytest.raises(eo.ConfoundedOrder):
        eo.executed_offset({**requested, "c1": 2}, "c0", "c1")


def test_a_position_offset_other_than_one_enters_the_drift_term_in_proportion() -> None:
    offsets = {"b0": [-3, 1, -1, 1], "k4": [1, -1, 1, -1], "k8": [1, -1, -3, 1], "k12": [1, -1, 1, -1]}
    solved = eo.fit(_rows({name: [int(v) for v in values] for name, values in offsets.items()}))
    _expect(math.isclose(float(solved["drift"]), DRIFT, abs_tol=1e-12), f"drift {solved['drift']}")  # type: ignore[arg-type]
    for name in CONTRAST:
        _expect(math.isclose(solved["contrast"][name], CONTRAST[name], abs_tol=1e-12), f"{name}")  # type: ignore[index]


def test_templates_that_are_each_one_directional_in_opposite_directions_are_confounded() -> None:
    # Sxx is zero when every template has one offset in all its batches, even if the templates differ.
    rows = _rows({"b0": [1, 1, 1, 1], "k4": [-1, -1, -1, -1], "k8": [1, 1, 1, 1], "k12": [-1, -1, -1, -1]})
    with pytest.raises(eo.ConfoundedOrder):
        eo.fit(rows)


def test_the_enumerated_confounded_probability_of_two_templates_matches_its_closed_form() -> None:
    for rate in (0.1, 0.25, 7 / 19):
        per_template = 2 * rate**2 * (1 - rate) ** 2  # a template [+, -, +, -] ends one-directional
        seen = eo.operating_characteristics(rate, templates=2)["confounded"]
        _expect(math.isclose(seen, per_template**2, rel_tol=1e-9), f"rate {rate}: {seen} against {per_template**2}")
    _expect(
        eo.operating_characteristics(0.0, templates=2)["mean_error_ratio"] == 1.0, "a balanced design pays no error"
    )


def test_the_pooled_enumeration_of_two_templates_equals_the_serial_one_bit_for_bit(
    forced_pool: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    for rate in (0.0, 0.1, 0.25, 7 / 19):
        monkeypatch.setattr(eo, "MASK_BLOCK", 1 << 8)  # one block of all 2^8 patterns runs inline
        serial = eo.operating_characteristics(rate, templates=2)
        monkeypatch.setattr(eo, "MASK_BLOCK", 1 << 5)  # eight blocks of 32 patterns run in two spawned workers
        pooled = eo.operating_characteristics(rate, templates=2)
        _expect(pooled == serial, f"rate {rate}: {pooled} against {serial}")
    _expect(
        forced_pool.maps[-1] == ("function", 8) and set(forced_pool.pools) == {2},
        str((forced_pool.maps, forced_pool.pools)),
    )


@pytest.mark.audit
def test_the_pooled_enumeration_of_four_templates_equals_the_serial_one_bit_for_bit(
    forced_pool: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(eo, "MASK_BLOCK", 1 << 16)  # one block of all 2^16 patterns runs inline
    serial = eo.operating_characteristics(0.25)
    monkeypatch.setattr(eo, "MASK_BLOCK", 512)
    pooled = eo.operating_characteristics(0.25)
    _expect(pooled == serial, f"{pooled} against {serial}")
    _expect(
        forced_pool.maps[-1] == ("function", 128) and set(forced_pool.pools) == {2},
        str((forced_pool.maps, forced_pool.pools)),
    )


@pytest.mark.audit
def test_the_enumerated_confounded_probability_matches_its_closed_form(forced_pool: Any) -> None:
    for rate in (0.1, 0.25, 7 / 19):
        per_template = 2 * rate**2 * (1 - rate) ** 2  # a template [+, -, +, -] ends one-directional
        seen = eo.operating_characteristics(rate)["confounded"]
        _expect(math.isclose(seen, per_template**4, rel_tol=1e-9), f"rate {rate}: {seen} against {per_template**4}")
    _expect(eo.operating_characteristics(0.0)["mean_error_ratio"] == 1.0, "a balanced design pays no error")


@pytest.mark.parametrize(
    "bad", [{"b0": []}, {"b0": [(0.0, 0.0, 1)]}, {"b0": [(math.nan, 0.01, 1)]}, {"b0": [(0.0, 0.01, 0)]}]
)
def test_an_unusable_row_is_refused(bad: dict[str, list[eo.Row]]) -> None:
    with pytest.raises(ValueError):
        eo.fit(bad)


TIMES = [0.0, 1.5, 6.0, 11.0]  # hours of four base replicates, unequally spaced
SES = [0.004, 0.005, 0.004, 0.006]


def test_the_constrained_weights_obey_their_moment_conditions() -> None:
    reference = 5.2
    for order in (0, 1, 2):
        weights = eo.constrained_weights(TIMES, SES, reference, order)
        _expect(math.isclose(sum(weights), 1.0, abs_tol=1e-12), f"order {order}: weights sum to {sum(weights)}")
        for k in range(1, order + 1):
            moment = sum(w * (t - reference) ** k for w, t in zip(weights, TIMES, strict=True))
            _expect(abs(moment) < 1e-9, f"order {order}: moment {k} is {moment}")


def test_the_level_is_exact_under_a_linear_drift_where_the_plain_mean_is_biased() -> None:
    reference, level, slope = 5.2, 0.0164, 0.01
    values = [level + slope * (t - reference) for t in TIMES]
    solved, _ = eo.level_at(values, SES, TIMES, reference)
    _expect(math.isclose(solved, level, abs_tol=1e-12), f"level {solved}")
    plain, _ = ana.pooled(list(zip(values, SES, strict=True)))
    weighted_time = sum(t / (s * s) for t, s in zip(TIMES, SES, strict=True)) / sum(1 / (s * s) for s in SES)
    _expect(math.isclose(plain - level, slope * (weighted_time - reference), abs_tol=1e-12), "the plain-mean bias")
    _expect(abs(plain - level) > 1e-3, f"the plain mean is not biased here: {plain - level}")


def test_a_quadratic_drift_needs_the_second_order_column() -> None:
    reference = 5.2
    values = [0.0164 + 0.004 * (t - reference) ** 2 for t in TIMES]
    first, _ = eo.level_at(values, SES, TIMES, reference, order=1)
    second, _ = eo.level_at(values, SES, TIMES, reference, order=2)
    _expect(abs(first - 0.0164) > 1e-3 and math.isclose(second, 0.0164, abs_tol=1e-12), f"{first} {second}")


def test_the_variance_follows_the_closed_form_and_costs_nothing_at_the_weighted_mean_time() -> None:
    reference = 3.0
    _, se = eo.level_at([0.0] * 4, SES, TIMES, reference)
    w = [1 / (s * s) for s in SES]
    total = sum(w)
    t_w = sum(wi * t for wi, t in zip(w, TIMES, strict=True)) / total
    stt = sum(wi * (t - t_w) ** 2 for wi, t in zip(w, TIMES, strict=True)) / total
    expected = math.sqrt((1 / total) * (1 + (t_w - reference) ** 2 / stt))
    _expect(math.isclose(se, expected, rel_tol=1e-12), f"{se} against {expected}")
    _, at_mean = eo.level_at([0.0] * 4, SES, TIMES, t_w)
    _expect(
        math.isclose(at_mean, math.sqrt(1 / total), rel_tol=1e-12), "a reference at the weighted mean time costs error"
    )


def test_replicates_at_one_time_cannot_separate_the_drift() -> None:
    with pytest.raises(eo.ConfoundedOrder):
        eo.constrained_weights([1.0, 1.0, 1.0], [0.004] * 3, 2.0)
    with pytest.raises(eo.ConfoundedOrder):
        eo.constrained_weights([0.0, 1.0], [0.004] * 2, 2.0, order=2)


def test_the_drift_monitor_passes_a_line_and_refuses_a_step() -> None:
    times = [float(i) for i in range(12)]
    ses = [0.003] * 12
    line = eo.drift_monitor(times, [0.002 + 0.0007 * t for t in times], ses)
    _expect(math.isclose(float(line["slope"]), 0.0007, abs_tol=1e-12) and line["adequate"] is True, f"{line}")
    step = eo.drift_monitor(times, [0.0 if t < 6 else 0.03 for t in times], ses)
    _expect(step["adequate"] is False, f"a 10-sigma step passed: {step}")
    with pytest.raises(eo.ConfoundedOrder):
        eo.drift_monitor([0.0, 1.0], [0.0, 0.0], [0.003, 0.003])


def test_a_nonfinite_reference_or_value_is_refused_by_the_level() -> None:
    times, ses = [0.0, 1.0], [0.004, 0.004]
    for reference in (math.nan, math.inf):
        with pytest.raises(ValueError):
            eo.constrained_weights(times, ses, reference)
    with pytest.raises(ValueError):
        eo.level_at([0.01, math.nan], ses, times, 0.5)


@pytest.mark.parametrize("bad_ses", [[-0.003] * 6, [0.0] * 6, [math.nan] * 6])
def test_the_drift_monitor_refuses_an_unusable_error(bad_ses: list[float]) -> None:
    series = [float(i) for i in range(6)]
    with pytest.raises(ValueError):
        eo.drift_monitor(series, series, bad_ses)


def test_the_drift_monitor_refuses_a_nonfinite_value() -> None:
    series = [float(i) for i in range(6)]
    with pytest.raises(ValueError):
        eo.drift_monitor(series, [math.nan, *series[1:]], [0.003] * 6)


@pytest.mark.parametrize("rate", [-0.1, 1.1, math.nan])
def test_the_operating_characteristics_refuse_a_rate_outside_the_unit_interval(rate: float) -> None:
    with pytest.raises(ValueError):
        eo.operating_characteristics(rate, templates=1)


def test_the_operating_characteristics_refuse_an_empty_template_count_or_pattern() -> None:
    with pytest.raises(ValueError):
        eo.operating_characteristics(0.2, templates=0)
    for pattern in ((), (0, 0, 0, 0), (1, 2, -1, -1)):
        with pytest.raises(ValueError):
            eo.operating_characteristics(0.2, requested=pattern, templates=1)


def test_the_own_drift_difference_error_matches_the_covariance_of_the_two_linear_estimators() -> None:
    rows = {
        "b0": [(0.0, 0.003, -1), (0.0, 0.004, -1), (0.0, 0.005, 1), (0.0, 0.003, -1)],
        "k4": [(0.0, 0.004, 1), (0.0, 0.003, 1), (0.0, 0.006, -3), (0.0, 0.004, -1)],
    }
    solved = eo.fit(rows)
    sxx = 0.0
    parts: dict[str, list[tuple[float, float, float]]] = {}
    for name, batch in rows.items():
        w = [1.0 / se**2 for _, se, _ in batch]
        s_bar = sum(wi * s for wi, (_, _, s) in zip(w, batch, strict=True)) / sum(w)
        parts[name] = [
            (wi * (s - s_bar), se, wi * (s - s_bar) * (s - s_bar)) for wi, (_, se, s) in zip(w, batch, strict=True)
        ]
        sxx += sum(c for _, _, c in parts[name])
    for name, items in parts.items():
        own = sum(c for _, _, c in items)
        # Coefficients of v in the own drift (a_i / own) and in the shared drift (a_i / sxx), per row of the template.
        cov = sum((a / own) * (a / sxx) * se * se for a, se, _ in items)
        var_own = sum((a / own) ** 2 * se * se for a, se, _ in items)
        var_shared = 1.0 / sxx
        expected = math.sqrt(var_own - 2.0 * cov + var_shared)
        got = solved["template_drift_difference_se"][name]  # type: ignore[index]
        _expect(math.isclose(got, expected, rel_tol=1e-9), f"{name}: {got} against {expected}")


def test_a_correlated_pool_follows_the_generalized_least_squares_by_hand() -> None:
    # S = [[1, 1/2], [1/2, 2]]: S^-1 = [[2, -1/2], [-1/2, 1]] / (7/4), S^-1 1 = [3/2, 1/2] / (7/4), 1' S^-1 1 = 8/7.
    mean, se, chi, weights = eo.pool_correlated([1.0, 3.0], [[1.0, 0.5], [0.5, 2.0]])
    _expect(
        math.isclose(mean, 1.5, rel_tol=1e-12) and math.isclose(se, math.sqrt(7 / 8), rel_tol=1e-12), f"{mean} {se}"
    )
    _expect(math.isclose(chi, 2.0, rel_tol=1e-12), f"chi-square {chi}")
    _expect(all(math.isclose(a, b, rel_tol=1e-12) for a, b in zip(weights, [0.75, 0.25], strict=True)), f"{weights}")
    # A diagonal matrix is the inverse-variance pool.
    plain = ana.pooled([(1.0, 0.5), (3.0, 1.0)])
    diagonal = eo.pool_correlated([1.0, 3.0], [[0.25, 0.0], [0.0, 1.0]])
    _expect(
        math.isclose(diagonal[0], plain[0], rel_tol=1e-12) and math.isclose(diagonal[1], plain[1], rel_tol=1e-12), "d"
    )


@pytest.mark.parametrize(
    "matrix",
    [[[1.0, 2.0], [2.0, 1.0]], [[1.0, 0.0]], [[1.0, 0.0], [0.0, math.nan]], [[0.0, 0.0], [0.0, 1.0]]],
)
def test_a_covariance_that_is_not_positive_definite_or_finite_is_refused(matrix: list[list[float]]) -> None:
    with pytest.raises(ValueError):
        eo.pool_correlated([0.0, 1.0], matrix)


def test_a_series_that_kept_its_order_has_no_covariance_between_templates() -> None:
    solved = eo.fit(_rows(BALANCED))
    for a in CONTRAST:
        for b in CONTRAST:
            if a != b:
                _expect(solved["covariance"][a][b] == 0.0, f"{a},{b}")  # type: ignore[index]
    _expect(all(math.isclose(solved["covariance"][a][a], solved["error"][a] ** 2) for a in CONTRAST), "variances")  # type: ignore[index]


def test_a_template_with_one_offset_has_no_own_drift_and_one_varying_template_has_no_difference() -> None:
    # k4, k8 and k12 keep one offset in all four batches; only b0 varies. Their own drift is undefined, and b0's own
    # drift is the shared drift to rounding: the difference and its error are zero.
    rows = _rows({"b0": [-3, 1, -1, 1], "k4": [1, 1, 1, 1], "k8": [-1, -1, -1, -1], "k12": [3, 3, 3, 3]})
    solved = eo.fit(rows)
    for name in ("k4", "k8", "k12"):
        _expect(solved["template_drift"][name] is None, f"{name}: {solved['template_drift'][name]}")  # type: ignore[index]
    _expect(abs(solved["template_drift"]["b0"] - solved["drift"]) < 1e-12, "b0's own drift is the shared drift")  # type: ignore[index]
    _expect(solved["template_drift_difference_se"]["b0"] < 1e-6, f"{solved['template_drift_difference_se']['b0']}")  # type: ignore[index]


def test_the_shared_drift_covariance_of_a_three_batch_fixture_follows_the_hand_arithmetic() -> None:
    # Template A holds two batches at x = 3 and 1 and template B one batch at x = 2, every error 1 (weight 1), values
    # A: 0.30 and 0.10, B: 0.35.
    #   x_A = (3 + 1) / 2 = 2, v_A = 0.20, W_A = 2; x_B = 2, v_B = 0.35, W_B = 1.
    #   Sxx = (3 - 2)^2 + (1 - 2)^2 = 2 (B has one offset and adds nothing); Sxy = (3 - 2)(0.30 - 0.20) +
    #   (1 - 2)(0.10 - 0.20) = 0.2; g = Sxy / Sxx = 0.1 and var(g) = 1 / Sxx = 0.5.
    #   t_A = 0.20 - 0.1 x 2 = 0 and t_B = 0.35 - 0.1 x 2 = 0.15.
    #   var(t_A) = 1 / 2 + 2^2 x 0.5 = 2.5, var(t_B) = 1 / 1 + 2^2 x 0.5 = 3 and cov(t_A, t_B) = x_A x_B var(g) = 2.
    # The pool of (t_A, t_B) with S = [[2.5, 2], [2, 3]]: det S = 3.5, S^-1 1 = (1, 0.5) / 3.5, 1' S^-1 1 = 3 / 7, so
    # the weights are (2/3, 1/3), the mean is 0.15 / 3 = 0.05 and the variance is 7 / 3; the residuals (-0.05, 0.10)
    # give the chi-square (3 x 0.0025 + 2 x 2 x 0.005 + 2.5 x 0.01) / 3.5 = 0.015.
    # The independent pool of the same contrasts reads variance 1 / (1 / 2.5 + 1 / 3), about 1.364, below the 7/3 here.
    rows = {"A": [(0.30, 1.0, 3.0), (0.10, 1.0, 1.0)], "B": [(0.35, 1.0, 2.0)]}
    solved = eo.fit(rows)
    close = lambda got, want: _expect(abs(got - want) < 1e-12, f"{got} against {want}")  # noqa: E731
    close(solved["drift"], 0.1)
    close(solved["drift_se"] ** 2, 0.5)  # type: ignore[operator]
    close(solved["contrast"]["A"], 0.0)  # type: ignore[index]
    close(solved["contrast"]["B"], 0.15)  # type: ignore[index]
    close(solved["error"]["A"] ** 2, 2.5)  # type: ignore[index]
    close(solved["error"]["B"] ** 2, 3.0)  # type: ignore[index]
    cov = solved["covariance"]
    close(cov["A"]["B"], 2.0)  # type: ignore[index]
    close(cov["B"]["A"], 2.0)  # type: ignore[index]
    mean, se, chi2_value, weights = eo.pool_correlated(
        [solved["contrast"]["A"], solved["contrast"]["B"]],  # type: ignore[index]
        [[cov["A"]["A"], cov["A"]["B"]], [cov["B"]["A"], cov["B"]["B"]]],  # type: ignore[index]
    )
    close(mean, 0.05)
    close(se**2, 7.0 / 3.0)
    close(chi2_value, 0.015)
    close(weights[0], 2.0 / 3.0)
    close(weights[1], 1.0 / 3.0)
