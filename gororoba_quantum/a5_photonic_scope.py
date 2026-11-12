"""Exact operator scope and returned-event accounting for photonic algebra slices.

A selected-column certificate covers only its declared input span. The fixed
operator contract compares every matrix entry. Neither contract identifies a
physical algebra from agreement with its encoded linear operator.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from fractions import Fraction
from typing import Any

import cd_core


def _counts(values: Sequence[int], name: str) -> tuple[int, ...]:
    if any(type(value) is not int or value < 0 for value in values):
        raise ValueError(f"{name} must contain nonnegative integer counts")
    return tuple(values)


def _indices(values: Sequence[int], dimension: int, name: str) -> tuple[int, ...]:
    indices = tuple(values)
    if any(type(index) is not int or not 0 <= index < dimension for index in indices):
        raise ValueError(f"{name} contains an invalid index")
    if len(set(indices)) != len(indices):
        raise ValueError(f"{name} contains a repeated index")
    return indices


def _positive_rational(value: cd_core.ExactScalar, name: str) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, int | Fraction) or value <= 0:
        raise ValueError(f"{name} must be a positive int or Fraction")
    return Fraction(value)


def _fraction(numerator: int, denominator: int) -> dict[str, int | bool]:
    return {"numerator": numerator, "denominator": denominator, "defined": denominator != 0}


def branch_accounting(
    port_counts: Sequence[int],
    invalid_events: Mapping[str, int],
    *,
    success_modes: Sequence[int],
    failure_modes: Sequence[int],
) -> dict[str, Any]:
    """Partition returned events, with undefined fractions explicit at zero denominator.

    Port counts describe single-photon events. Invalid events and other ports
    remain in the returned-event denominator. Provider shot counters and
    unobserved source trials are separate populations and are not inferred.
    """
    ports = _counts(port_counts, "port counts")
    invalid = _counts(tuple(invalid_events.values()), "invalid events")
    success_indices = _indices(success_modes, len(ports), "success modes")
    failure_indices = _indices(failure_modes, len(ports), "failure modes")
    if not ports or not success_indices or not failure_indices:
        raise ValueError("ports, success modes and failure modes must be nonempty")
    if set(success_indices) & set(failure_indices):
        raise ValueError("success and failure modes overlap")
    success = sum(ports[index] for index in success_indices)
    failure = sum(ports[index] for index in failure_indices)
    eligible = success + failure
    excluded_ports = sum(ports) - eligible
    invalid_total = sum(invalid)
    returned = eligible + excluded_ports + invalid_total
    return {
        "success_events": success,
        "failure_events": failure,
        "eligible_events": eligible,
        "excluded_mode_events": excluded_ports,
        "invalid_events": invalid_total,
        "returned_events": returned,
        "success_given_eligible": _fraction(success, eligible),
        "success_per_returned_event": _fraction(success, returned),
        "eligible_per_returned_event": _fraction(eligible, returned),
        "excluded_modes_per_returned_event": _fraction(excluded_ports, returned),
        "invalid_per_returned_event": _fraction(invalid_total, returned),
        "denominator_boundary": "Returned events are not unobserved source trials or a provider shot population.",
    }


def selected_columns(
    dimension: int,
    left: Sequence[cd_core.ExactScalar],
    input_basis: Sequence[int],
    *,
    scale: cd_core.ExactScalar = 1,
) -> cd_core.ExactMatrix:
    """All output coordinates of L_left / scale on the declared basis inputs."""
    matrix = cd_core.left_mult_matrix_exact(dimension, left)
    inputs = _indices(input_basis, dimension, "input basis")
    if not inputs:
        raise ValueError("input basis must be nonempty")
    divisor = _positive_rational(scale, "scale")
    return tuple(tuple(row[index] / divisor for index in inputs) for row in matrix)


def check_selected_columns(
    actual: Sequence[Sequence[cd_core.ExactScalar]],
    dimension: int,
    left: Sequence[cd_core.ExactScalar],
    input_basis: Sequence[int],
    *,
    scale: cd_core.ExactScalar = 1,
) -> None:
    """Require exact selected columns, including every output outside an encoded slice."""
    expected = selected_columns(dimension, left, input_basis, scale=scale)
    if len(actual) != dimension or any(len(row) != len(input_basis) for row in actual):
        raise ValueError("selected operator must contain every output row and exactly the declared input columns")
    for row, (observed, target) in enumerate(zip(actual, expected, strict=True)):
        for column, (value, required) in enumerate(zip(observed, target, strict=True)):
            if isinstance(value, bool) or not isinstance(value, int | Fraction):
                raise ValueError("operator entries must be int or Fraction")
            if value != required:
                raise ValueError(f"operator differs at output {row}, input {input_basis[column]}")


def check_fixed_operator(
    actual: Sequence[Sequence[cd_core.ExactScalar]],
    dimension: int,
    left: Sequence[cd_core.ExactScalar],
    *,
    scale: cd_core.ExactScalar = 1,
) -> None:
    """Require one fixed operator on all basis inputs, not one prepared column per setting."""
    check_selected_columns(actual, dimension, left, tuple(range(dimension)), scale=scale)


def embedded_slice_scope(
    dimension: int,
    left: Sequence[cd_core.ExactScalar],
    input_basis: Sequence[int],
    *,
    reference_dimension: int,
    scale: cd_core.ExactScalar = 1,
) -> dict[str, Any]:
    """Compare a declared slice with its canonical lower-dimensional embedding exactly.

    An operand or input outside the reference algebra is reported as such;
    failure of containment alone establishes no dimension-sensitive observable.
    """
    columns = selected_columns(dimension, left, input_basis, scale=scale)
    cd_core.cd_sign(reference_dimension, 0, 0)
    if reference_dimension >= dimension:
        raise ValueError("reference dimension must be smaller than the ambient dimension")
    operand_contained = not any(left[reference_dimension:])
    inputs_contained = all(index < reference_dimension for index in input_basis)
    outputs_contained = not any(value for row in columns[reference_dimension:] for value in row)
    same_action: bool | None = None
    if operand_contained and inputs_contained:
        reference = selected_columns(reference_dimension, left[:reference_dimension], input_basis, scale=scale)
        same_action = outputs_contained and columns[:reference_dimension] == reference
    return {
        "ambient_dimension": dimension,
        "reference_dimension": reference_dimension,
        "input_basis": list(input_basis),
        "input_span_dimension": len(input_basis),
        "unprobed_input_dimension": dimension - len(input_basis),
        "all_input_columns_checked": len(input_basis) == dimension,
        "operand_in_reference_algebra": operand_contained,
        "inputs_in_reference_algebra": inputs_contained,
        "outputs_in_reference_algebra": outputs_contained,
        "same_embedded_action": same_action,
        "dimension_discrimination_established": False,
    }


def check_recorded_operator(
    recorded: Mapping[str, Sequence[Sequence[cd_core.ExactScalar]]],
    expected: Any,
    *,
    tolerance: cd_core.ExactScalar,
) -> None:
    """Bound each recorded decimal component against an exact symbolic operator.

    Parse JSON with parse_float=Fraction before calling. The tolerance applies
    separately to each real and imaginary component. It binds the requested
    finite-precision optical matrix, not a measured physical implementation.
    """
    import sympy as sym

    limit = _positive_rational(tolerance, "tolerance")
    target = sym.Matrix(expected)
    if target.rows != target.cols or not target.rows or target.atoms(sym.Float) or target.free_symbols:
        raise ValueError("the target must be a nonempty exact constant square matrix")
    bound = sym.Rational(limit.numerator, limit.denominator)
    if set(recorded) != {"real", "imaginary"}:
        raise ValueError("the recorded operator must have real and imaginary components")
    for component, part in (("real", sym.re), ("imaginary", sym.im)):
        matrix = recorded[component]
        if len(matrix) != target.rows or any(len(row) != target.cols for row in matrix):
            raise ValueError("recorded operator dimensions differ from the exact target")
        for row, values in enumerate(matrix):
            for column, value in enumerate(values):
                if isinstance(value, bool) or not isinstance(value, int | Fraction):
                    raise ValueError("recorded decimals must be parsed as int or Fraction")
                rational = Fraction(value)
                error = abs(sym.Rational(rational.numerator, rational.denominator) - part(target[row, column]))
                if (error <= bound) is not sym.true:
                    raise ValueError(f"recorded operator differs at {component} output {row}, input {column}")
