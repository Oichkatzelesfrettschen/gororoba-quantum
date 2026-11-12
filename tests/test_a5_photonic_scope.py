"""Bound the operator and event populations established by photonic slice data."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import a5_photonic_scope as scope
import cd_core


def operand(dimension: int = 32, second: int = 10) -> list[int]:
    result = [0] * dimension
    result[1] = result[second] = 1
    return result


def test_denominators_keep_excluded_ports_and_invalid_events() -> None:
    result = scope.branch_accounting(
        [3, 2, 4, 1, 7, 3], {"zero_click": 2, "other_photon_number": 3}, success_modes=(0, 1), failure_modes=(2, 3)
    )
    expected = {
        "success_events": 5,
        "failure_events": 5,
        "eligible_events": 10,
        "excluded_mode_events": 10,
        "invalid_events": 5,
        "returned_events": 25,
    }
    if any(result[key] != value for key, value in expected.items()):
        raise AssertionError("event populations do not partition the returned events")
    if result["success_given_eligible"] != {"numerator": 5, "denominator": 10, "defined": True}:
        raise AssertionError("eligible-event fraction differs")
    if result["success_per_returned_event"] != {"numerator": 5, "denominator": 25, "defined": True}:
        raise AssertionError("returned-event fraction omits excluded events")


@pytest.mark.parametrize("counts,invalid", [([0, 0, 0], {}), ([0, 0, 9], {"zero_click": 1})])
def test_empty_eligible_population_is_undefined(counts: list[int], invalid: dict[str, int]) -> None:
    result = scope.branch_accounting(counts, invalid, success_modes=(0,), failure_modes=(1,))
    if result["success_given_eligible"]["defined"]:
        raise AssertionError("an empty eligible population acquired a fraction")
    if result["success_per_returned_event"]["defined"] != bool(sum(counts) + sum(invalid.values())):
        raise AssertionError("returned-event zero denominator differs")


@pytest.mark.parametrize("bad", [-1, True, 1.0])
def test_malformed_counts_fail_closed(bad: int) -> None:
    with pytest.raises(ValueError, match="nonnegative integer"):
        scope.branch_accounting([bad, 1], {}, success_modes=(0,), failure_modes=(1,))
    with pytest.raises(ValueError, match="nonnegative integer"):
        scope.branch_accounting([1, 1], {"invalid": bad}, success_modes=(0,), failure_modes=(1,))


@pytest.mark.parametrize("success,failure", [((0, 0), (1,)), ((0,), (0,)), ((-1,), (1,)), ((True,), (1,))])
def test_invalid_mode_partitions_fail_closed(success: tuple[int, ...], failure: tuple[int, ...]) -> None:
    with pytest.raises(ValueError):
        scope.branch_accounting([1, 1], {}, success_modes=success, failure_modes=failure)


@pytest.mark.parametrize("second", [9, 10])
def test_current_slice_is_exactly_an_embedded_a4_action(second: int) -> None:
    result = scope.embedded_slice_scope(32, operand(second=second), (4, 15), reference_dimension=16, scale=2)
    if result["same_embedded_action"] is not True or result["unprobed_input_dimension"] != 30:
        raise AssertionError("the declared two-column slice does not match its A4 embedding")
    if result["all_input_columns_checked"] or result["dimension_discrimination_established"]:
        raise AssertionError("two columns were promoted to a full-operator or dimension claim")


def test_operand_outside_a4_does_not_acquire_an_embedding_certificate() -> None:
    result = scope.embedded_slice_scope(32, operand(second=18), (4, 15), reference_dimension=16)
    if result["operand_in_reference_algebra"] or result["same_embedded_action"] is not None:
        raise AssertionError("an operand outside A4 acquired an A4 comparison")
    if result["dimension_discrimination_established"]:
        raise AssertionError("leaving a subalgebra alone established a distinguishing observable")


def test_selected_columns_check_every_output_and_exact_sign() -> None:
    left = operand()
    actual = scope.selected_columns(32, left, (4, 15), scale=2)
    scope.check_selected_columns(actual, 32, left, (4, 15), scale=2)
    outside = [list(row) for row in actual]
    outside[31][0] = Fraction(1, 2)
    with pytest.raises(ValueError, match="output 31, input 4"):
        scope.check_selected_columns(outside, 32, left, (4, 15), scale=2)
    wrong_sign = [list(row) for row in actual]
    wrong_sign[5][0] *= -1
    with pytest.raises(ValueError, match="output 5, input 4"):
        scope.check_selected_columns(wrong_sign, 32, left, (4, 15), scale=2)
    with pytest.raises(ValueError, match="every output row"):
        scope.check_selected_columns(actual[:16], 32, left, (4, 15), scale=2)


def test_out_of_input_slice_mutation_passes_slice_but_fails_fixed_operator() -> None:
    left = operand()
    actual = [list(row) for row in cd_core.left_mult_matrix_exact(32, left)]
    scope.check_fixed_operator(actual, 32, left)
    actual[31][0] += 1
    scope.check_selected_columns([[row[index] for index in (4, 15)] for row in actual], 32, left, (4, 15))
    with pytest.raises(ValueError, match="output 31, input 0"):
        scope.check_fixed_operator(actual, 32, left)


@pytest.mark.parametrize("bad_scale", [0, -1, True, 2.0])
def test_invalid_normalization_fails_closed(bad_scale: int) -> None:
    with pytest.raises(ValueError, match="positive int or Fraction"):
        scope.selected_columns(32, operand(), (4, 15), scale=bad_scale)


def test_repeated_basis_columns_cannot_claim_complete_coverage() -> None:
    with pytest.raises(ValueError, match="repeated index"):
        scope.embedded_slice_scope(32, operand(), (4, 4), reference_dimension=16)


def observation_fixture() -> dict[str, Any]:
    return {
        "name": "kernel-dark",
        "port_counts": [1, 0, 0, 0, 4, 0, 0, 0, 2, 0, 0, 0],
        "invalid_events": {"zero_click": 1, "other_photon_number": 2},
        "returned_events": 10,
        "success": 1,
        "failure": 4,
        "sentinel": 2,
        "conditional_success": 0.2,
        "shots_used": 20,
    }


def test_successor_reuses_counts_without_treating_shots_as_events() -> None:
    import ascella_a5_kernel_scope_analysis as analysis

    original = observation_fixture()
    result = analysis.extend_observation(original)
    if (
        result["event_accounting"]["success_per_returned_event"]
        != {
            "numerator": 1,
            "denominator": 10,
            "defined": True,
        }
        or result["shots_used"] != 20
    ):
        raise AssertionError("returned events were conflated with provider shots")
    if "event_accounting" in original or "conditional_success" in result:
        raise AssertionError("the original changed or a computed floating ratio entered the successor")


@pytest.mark.parametrize("key", ["returned_events", "success", "failure", "sentinel", "conditional_success"])
def test_successor_rejects_inconsistent_derived_counts(key: str) -> None:
    import ascella_a5_kernel_scope_analysis as analysis

    original = observation_fixture()
    original[key] += 1
    with pytest.raises(ValueError, match="differs from its counts"):
        analysis.extend_observation(original)


def recorded_operator_fixture(specification: tuple[str, int, int, int]) -> dict[str, Any]:
    import ascella_a5_kernel_slice as case
    import sympy as sym

    _, second, coefficient, preparation = specification
    expected = sym.eye(12)
    expected[:8, :8] = case.exact_operator(second, coefficient, preparation)
    return {
        "real": [[Fraction(str(float(expected[row, column]))) for column in range(12)] for row in range(12)],
        "imaginary": [[0] * 12 for _ in range(12)],
    }


@pytest.mark.parametrize("index", range(6))
def test_optical_builder_matches_both_unprepared_columns(index: int) -> None:
    import ascella_a5_kernel_scope_analysis as analysis
    import ascella_a5_kernel_slice as case

    specification = case.SETTINGS[index]
    result = analysis.setting_scope((specification, recorded_operator_fixture(specification)))
    if result["scope"]["same_embedded_action"] is not True:
        raise AssertionError("the current optical setting is not its declared embedded A4 slice")


def test_same_name_different_recorded_operator_is_rejected() -> None:
    import ascella_a5_kernel_scope_analysis as analysis
    import ascella_a5_kernel_slice as case

    specification = case.SETTINGS[1]
    recorded = recorded_operator_fixture(specification)
    recorded["real"][11][11] = -1
    with pytest.raises(ValueError, match="recorded operator differs"):
        analysis.setting_scope((specification, recorded))


def test_builder_column_unseen_by_original_prepared_state_is_checked(monkeypatch: pytest.MonkeyPatch) -> None:
    import ascella_a5_kernel_scope_analysis as analysis
    import ascella_a5_kernel_slice as case

    original = case.exact_operator
    specification = case.SETTINGS[1]
    recorded = recorded_operator_fixture(specification)

    def changed(second: int, coefficient: int, preparation: int) -> Any:
        operator = original(second, coefficient, preparation).as_mutable()
        operator[0, 1] *= -1
        return operator

    monkeypatch.setattr(case, "exact_operator", changed)
    with pytest.raises(ValueError, match="operator differs"):
        analysis.setting_scope((specification, recorded))


def test_recorded_operator_rejects_float_components_and_checks_imaginary_part() -> None:
    import sympy as sym

    malformed: Any = {"real": [[1.0]], "imaginary": [[0]]}
    with pytest.raises(ValueError, match="parsed as int or Fraction"):
        scope.check_recorded_operator(malformed, sym.eye(1), tolerance=Fraction(1, 10**12))
    with pytest.raises(ValueError, match="imaginary output 0, input 0"):
        scope.check_recorded_operator({"real": [[1]], "imaginary": [[1]]}, sym.eye(1), tolerance=Fraction(1, 10**12))


def test_cli_retains_and_checks_exact_record_bytes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import ascella_a5_kernel_scope_analysis as analysis

    record = {"schema": "fixture", "source_sha256": "fixed", "numerator": 1, "denominator": 7}
    monkeypatch.setattr(analysis, "describe", lambda _: record)
    output = tmp_path / "scope.json"
    analysis.main([str(tmp_path), "--out", str(output)])
    analysis.main([str(tmp_path), "--out", str(output), "--check"])
    record["source_sha256"] = "changed"
    with pytest.raises(ValueError, match="source-bound replay"):
        analysis.main([str(tmp_path), "--out", str(output), "--check"])


def test_cli_check_requires_a_retained_output(tmp_path: Path) -> None:
    import ascella_a5_kernel_scope_analysis as analysis

    with pytest.raises(SystemExit) as error:
        analysis.main([str(tmp_path), "--check"])
    if error.value.code != 2:
        raise AssertionError("--check without --out did not fail argument admission")
