"""Contracts of the executed-order drift fit of the bracketed twin contrasts."""

from __future__ import annotations

import math

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
    requested = {"r0": "00:00:01", "c0": "00:00:02", "c1": "00:00:03", "r1": "00:00:04", "b": "00:00:05"}
    _expect(eo.executed_offset(requested, "c0", "c1") == 1, "the requested order reads +1")
    _expect(eo.executed_offset({**requested, "c0": "00:00:03", "c1": "00:00:02"}, "c0", "c1") == -1, "swapped twins")
    # the batch 02 of the hosted QX run: coin 1 ran second, coin 0 last of five
    scrambled = {"r0": "00:00:01", "c1": "00:00:02", "r1": "00:00:03", "b": "00:00:04", "c0": "00:00:05"}
    _expect(eo.executed_offset(scrambled, "c0", "c1") == -3, "coin 1 three places before coin 0")
    with pytest.raises(eo.ConfoundedOrder):
        eo.executed_offset({**requested, "c1": "00:00:02"}, "c0", "c1")


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


def test_the_enumerated_confounded_probability_matches_its_closed_form() -> None:
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


def test_unusable_inputs_fail_closed_instead_of_returning_a_number() -> None:
    times, ses = [0.0, 1.0], [0.004, 0.004]
    with pytest.raises(ValueError):
        eo.constrained_weights(times, ses, math.nan)
    with pytest.raises(ValueError):
        eo.constrained_weights(times, ses, math.inf)
    series = [float(i) for i in range(6)]
    for bad_ses in ([-0.003] * 6, [0.0] * 6, [math.nan] * 6):
        with pytest.raises(ValueError):
            eo.drift_monitor(series, series, bad_ses)
    with pytest.raises(ValueError):
        eo.drift_monitor(series, [math.nan] + series[1:], [0.003] * 6)
    for kwargs in (
        {"rate": -0.1},
        {"rate": 1.1},
        {"rate": math.nan},
        {"rate": 0.2, "templates": 0},
        {"rate": 0.2, "requested": ()},
        {"rate": 0.2, "requested": (0, 0, 0, 0)},
    ):
        with pytest.raises(ValueError):
            eo.operating_characteristics(templates=kwargs.pop("templates", 1), **kwargs)  # type: ignore[arg-type]
