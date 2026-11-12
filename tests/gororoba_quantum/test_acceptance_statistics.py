"""Hand-derived six-state counterexamples preserve population and joint-uncertainty semantics."""

from __future__ import annotations

import json
from dataclasses import replace
from typing import Any

import numpy as np
import pytest

from acceptance_statistics import (
    STATE_LABELS,
    AcceptanceCounts,
    AcceptanceError,
    analyze_six_state,
    estimate_acceptance,
)
from provider_counters import Counter, CounterError, Population, Status, unavailable


def _row(state: str, selected: int = 2, accepted: int = 5, attempts: int = 10) -> AcceptanceCounts:
    scope = f"state:{state}"
    counter = Counter("attempts", attempts, Population.CIRCUIT_EXECUTION, scope, Status.OBSERVED, "trial counter")
    return AcceptanceCounts(state, selected, accepted, counter, scope, "selected and accepted counts")


def _lawful_cell() -> list[AcceptanceCounts]:
    # E=diag(0.4,0), S=diag(0.4,0.6) gives p_f=1,p_g=0,p_+-=p_+-i=0.4 under conditioning.
    return [_row("f", 4, 4), _row("g", 0, 6), *[_row(state) for state in STATE_LABELS[2:]]]


def _close(actual: Any, expected: Any) -> None:
    observed = np.asarray(actual, dtype=float)
    reference = np.asarray(expected, dtype=float)
    if not np.isfinite(observed).all():
        raise AssertionError("the expected numerical endpoint is absent or nonfinite")
    np.testing.assert_allclose(observed, reference, rtol=0, atol=1e-15)


def test_state_dependent_acceptance_defect_cancels_with_true_trials() -> None:
    result = analyze_six_state(_lawful_cell(), independent_trials=True, fixed_attempts=True)
    _close(result.conditional_contrasts, [-0.2, -0.2])
    _close(result.unconditional_contrasts, [0.0, 0.0])
    _close(result.contrast_covariance, [[0.056, 0.024], [0.024, 0.056]])
    if result.uncertainty_model != "independent_fixed_attempts_binomial_plugin":
        raise AssertionError("fixed independent trials supply the binomial plug-in covariance")
    if result.uncertainty_reason is None or "boundary" not in result.uncertainty_reason:
        raise AssertionError("the zero-count control needs the boundary-variance qualification")
    record = json.loads(json.dumps(result.record(), allow_nan=False))
    if record["state_order"] != list(STATE_LABELS) or record["estimates"][0]["denominator"]["value"] != 10:
        raise AssertionError("canonical order and observed denominator provenance must survive serialization")


def test_input_order_does_not_reorder_covariance_or_contrasts() -> None:
    baseline = analyze_six_state(_lawful_cell(), independent_trials=True, fixed_attempts=True)
    reordered = analyze_six_state(list(reversed(_lawful_cell())), independent_trials=True, fixed_attempts=True)
    if baseline.record() != reordered.record():
        raise AssertionError("six-state outputs use canonical label order")


def test_zero_acceptance_keeps_observed_unconditional_endpoint() -> None:
    rows = _lawful_cell()
    rows[0] = replace(rows[0], selected=0, accepted=0)
    result = analyze_six_state(rows)
    first = result.estimates[0]
    if first.conditional_probability is not None or first.unconditional_probability != 0:
        raise AssertionError("zero acceptance has no conditional estimate but an observed zero per-attempt rate")
    if result.conditional_contrasts != (None, None):
        raise AssertionError("undefined conditional rates cannot become zero in a contrast")
    _close(result.unconditional_contrasts, [0.4, 0.4])


def test_zero_attempts_leaves_unconditional_rate_undefined() -> None:
    row = _row("f", 0, 0, 0)
    estimate = estimate_acceptance(row)
    if estimate.unconditional_probability is not None or estimate.acceptance_probability is not None:
        raise AssertionError("no attempted trial supplies no unconditional rate")
    if estimate.unconditional_reason is None or "zero" not in estimate.unconditional_reason:
        raise AssertionError("zero exposure needs a reason")


@pytest.mark.parametrize("kind", ("requested", "detected", "filtered", "modeled", "unknown"))
def test_nontrial_denominators_preserve_conditional_only_information(kind: str) -> None:
    row = _row("+")
    scope = row.scope
    if kind == "requested":
        counter = Counter("max_shots", 10, Population.REQUESTED_CAP, scope, Status.REQUESTED, "request")
    elif kind == "detected":
        counter = Counter(
            "shots_used", 10, Population.DETECTION_EVENT, scope, Status.OBSERVED, "result", terminated_by="max_shots"
        )
    elif kind == "filtered":
        counter = Counter("samples", 10, Population.PHOTON_FILTERED_SAMPLE, scope, Status.OBSERVED, "result")
    elif kind == "modeled":
        counter = Counter(
            "trials", 10.0, Population.SOURCE_TRIGGER, scope, Status.MODELED, "exposure model", ("assumed efficiency",)
        )
    else:
        counter = unavailable("trials", Population.SOURCE_TRIGGER, scope, "not retained")
    estimate = estimate_acceptance(replace(row, denominator=counter))
    if estimate.conditional_probability != 0.4 or estimate.unconditional_probability is not None:
        raise AssertionError("a cap, detection/sample count, model or missing count cannot identify attempted trials")
    if estimate.unconditional_reason is None:
        raise AssertionError("the unidentified trial denominator needs its retained reason")


@pytest.mark.parametrize("population", (Population.SOURCE_TRIGGER, Population.CIRCUIT_EXECUTION))
def test_observed_trial_populations_supply_unconditional_rates(population: Population) -> None:
    row = _row("+")
    estimate = estimate_acceptance(replace(row, denominator=replace(row.denominator, population=population)))
    if estimate.acceptance_probability != 0.5 or estimate.unconditional_probability != 0.2:
        raise AssertionError("both supported observed trial populations identify per-attempt rates")


def test_recorded_stopping_keeps_rates_but_requires_sampling_design_covariance() -> None:
    rows = _lawful_cell()
    rows[0] = replace(rows[0], denominator=replace(rows[0].denominator, terminated_by="accepted_event_budget"))
    result = analyze_six_state(rows, independent_trials=True, fixed_attempts=True)
    if result.estimates[0].unconditional_probability != 0.4 or result.contrast_covariance is not None:
        raise AssertionError("observed stopped exposure gives a descriptive rate but no fixed-N covariance")
    if result.uncertainty_reason is None or "stopping" not in result.uncertainty_reason:
        raise AssertionError("the missing stopping-design covariance needs a reason")
    supplied = analyze_six_state(rows, rate_covariance=np.eye(6) * 0.01)
    _close(supplied.contrast_covariance, [[0.04, 0.02], [0.02, 0.04]])


@pytest.mark.parametrize("independent,fixed", ((False, False), (True, False), (False, True)))
def test_uncertainty_is_not_invented_without_both_sampling_declarations(independent: bool, fixed: bool) -> None:
    result = analyze_six_state(_lawful_cell(), independent_trials=independent, fixed_attempts=fixed)
    if result.contrast_covariance is not None or result.contrast_standard_errors is not None:
        raise AssertionError("both fixed attempts and independent trials are required for the plug-in reference")
    if result.uncertainty_reason is None:
        raise AssertionError("unqualified uncertainty needs a reason")


def test_supplied_joint_covariance_retains_cross_state_dependence() -> None:
    covariance = np.eye(6) * 0.008 + np.ones((6, 6)) * 0.002
    result = analyze_six_state(_lawful_cell(), rate_covariance=covariance)
    _close(result.contrast_covariance, [[0.032, 0.016], [0.016, 0.032]])
    if result.uncertainty_model != "supplied_joint_rate_covariance":
        raise AssertionError("supplied covariance and binomial assumptions are separate contracts")
    covariance[:] = 0
    if result.rate_covariance is None or result.rate_covariance[0][0] != 0.01:
        raise AssertionError("result covariance must not alias the caller's mutable array")


def test_incomplete_trial_information_preserves_only_identified_contrasts() -> None:
    rows = _lawful_cell()
    rows[4] = replace(
        rows[4], denominator=unavailable("trials", Population.CIRCUIT_EXECUTION, rows[4].scope, "not retained")
    )
    result = analyze_six_state(rows, independent_trials=True, fixed_attempts=True)
    if result.unconditional_contrasts != (0.0, None) or result.contrast_covariance is not None:
        raise AssertionError("partial exposure identifies the real contrast but no complete joint uncertainty")
    with pytest.raises(AcceptanceError, match="six identified"):
        analyze_six_state(rows, rate_covariance=np.eye(6))


@pytest.mark.parametrize("bad", (True, False, -1, 1.0, float("nan"), float("inf"), "2", None, 2**53 + 1))
@pytest.mark.parametrize("field", ("selected", "accepted"))
def test_counts_reject_nonintegral_and_boolean_inputs(field: str, bad: Any) -> None:
    with pytest.raises(AcceptanceError):
        replace(_row("f"), **{field: bad})


def test_counts_reject_invalid_subset_and_provenance() -> None:
    row = _row("f")
    for changes in ({"selected": 6}, {"accepted": 11}, {"source": " "}, {"scope": "other"}, {"state": "x"}):
        with pytest.raises(AcceptanceError):
            replace(row, **changes)
    with pytest.raises(AcceptanceError):
        replace(row, denominator=replace(row.denominator, source=""))


def test_provider_counter_rejects_boolean_or_nonfinite_attempts() -> None:
    row = _row("f")
    for invalid in (True, 1.0, float("nan"), float("inf"), -1):
        with pytest.raises(CounterError):
            replace(row.denominator, value=invalid)


def test_six_state_rejects_duplicate_or_missing_labels() -> None:
    rows = _lawful_cell()
    with pytest.raises(AcceptanceError, match="exactly six"):
        analyze_six_state(rows[:-1])
    with pytest.raises(AcceptanceError, match="each canonical state"):
        analyze_six_state([*rows[:-1], rows[0]])


@pytest.mark.parametrize("bad", (0, 1, "true", None, np.bool_(True)))
def test_sampling_flags_require_bool(bad: object) -> None:
    with pytest.raises(AcceptanceError, match="must be bool"):
        analyze_six_state(_lawful_cell(), independent_trials=bad)  # type: ignore[arg-type]
    with pytest.raises(AcceptanceError, match="must be bool"):
        analyze_six_state(_lawful_cell(), fixed_attempts=bad)  # type: ignore[arg-type]


def test_uncertainty_contract_rejects_ambiguous_or_invalid_covariance() -> None:
    rows = _lawful_cell()
    with pytest.raises(AcceptanceError, match="not both"):
        analyze_six_state(rows, independent_trials=True, rate_covariance=np.eye(6))
    for bad in (np.eye(5), np.eye(6) * -1, np.full((6, 6), np.nan)):
        with pytest.raises(ValueError):
            analyze_six_state(rows, rate_covariance=bad)
    asymmetric = np.eye(6)
    asymmetric[0, 1] = 0.1
    with pytest.raises(ValueError):
        analyze_six_state(rows, rate_covariance=asymmetric)


def test_contrast_covariance_rejects_overflow_without_a_nonfinite_output() -> None:
    with pytest.raises(AcceptanceError, match="overflows"):
        analyze_six_state(_lawful_cell(), rate_covariance=np.eye(6) * 1e308)


def test_contrast_covariance_rejects_nonfinite_blas_output(monkeypatch: pytest.MonkeyPatch) -> None:
    original_errstate = np.errstate

    def ignore_floating_exceptions(**_kwargs: str) -> np.errstate:
        return original_errstate(all="ignore")

    monkeypatch.setattr(np, "errstate", ignore_floating_exceptions)
    with pytest.raises(AcceptanceError, match="overflows"):
        analyze_six_state(_lawful_cell(), rate_covariance=np.eye(6) * 1e308)
