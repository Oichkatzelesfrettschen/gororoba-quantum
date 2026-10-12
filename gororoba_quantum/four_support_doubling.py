"""Ordinary-doubling frames for a fixed four-coordinate Cayley-Dickson family.

The all-stage theorem follows from structural conjugation and doubling, as
proved in docs/notes/four_support_doubling.md. Descriptors store exponent
metadata for every integer stage >=5. Expanded exact operators and frames
have an explicit dimension-256 resource boundary, checked before allocation.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

import sympy as sp

import parallel
from cd_core import cd_sign
from four_support_geometry import (
    BLOCK_NAMES,
    LINEAR_TRANSFORM,
    Stratum,
    _frame_matrices,
    closure_contains,
    incidence_frame,
)
from four_support_rank import COEFFICIENTS, SUPPORT, evaluate_four_support, support_coordinates
from rank_charts import RationalMatrix

BASE_STAGE = 5
MAX_EXPANDED_STAGE = 8


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _equal(actual: sp.Matrix, expected: sp.Matrix, label: str) -> None:
    difference = sp.SparseMatrix(actual - expected).applyfunc(sp.expand)
    _require(difference == sp.zeros(*difference.shape), label)


@dataclass(frozen=True)
class DoublingModel:
    """Allocation-free exponent metadata for the uniform fixed-support theorem."""

    stage: int

    def __post_init__(self) -> None:
        if type(self.stage) is not int or self.stage < BASE_STAGE:
            raise ValueError("stage must be an integer at least five")

    @property
    def ambient_exponent(self) -> int:
        return self.stage

    @property
    def block_exponent(self) -> int:
        return self.stage - 3

    def record(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "ambient_dimension": {"base": 2, "exponent": self.ambient_exponent},
            "factor_block_dimension": {"base": 2, "exponent": self.block_exponent},
            "factor_block_names": BLOCK_NAMES,
            "frame_column_multiplier": len(BLOCK_NAMES),
            "coefficient_base_dimension": 4,
            "normalized_coefficient_base": "S3",
            "nullity": "k*2^(stage-3), where k is the number of vanishing factors among Delta,p,q,r,s",
            "unit_partner_fiber": "empty for k=0; S^(k*2^(stage-3)-1) otherwise",
        }


def _expanded_dimension(stage: int) -> int:
    model = DoublingModel(stage)
    if model.stage > MAX_EXPANDED_STAGE:
        raise ValueError("expanded artifacts support stages five through eight, up to dimension256")
    return 1 << model.stage


def _entries(values: Sequence[int | Fraction], length: int) -> tuple[Fraction, ...]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)) or len(values) != length:
        raise ValueError(f"expected {length} exact rational entries")
    if any(isinstance(value, bool) or not isinstance(value, (int, Fraction)) for value in values):
        raise ValueError("entries must be exact integers or Fractions")
    return tuple(Fraction(value) for value in values)


def _coefficients(values: Sequence[int | Fraction]) -> tuple[Fraction, ...]:
    embedded = support_coordinates(values)
    return tuple(embedded[index] for index in SUPPORT)


def _fractions(matrix: sp.Matrix) -> RationalMatrix:
    return tuple(tuple(Fraction(value) for value in row) for row in matrix.tolist())


def doubling_column_order(source_stage: int) -> tuple[int, ...]:
    """Regroup two frame copies into the same five ordered factor blocks."""
    _expanded_dimension(source_stage)
    _expanded_dimension(source_stage + 1)
    block_size = 1 << (source_stage - 3)
    order = tuple(
        copy * 5 * block_size + block * block_size + local
        for block in range(5)
        for copy in range(2)
        for local in range(block_size)
    )
    _require(sorted(order) == list(range(10 * block_size)), "column regrouping fails to be a permutation")
    return order


def _conjugate_rows(matrix: sp.Matrix, scale: int = 1) -> sp.Matrix:
    return sp.SparseMatrix(
        matrix.rows,
        matrix.cols,
        {(row, column): scale * (1 if row == 0 else -1) * value for (row, column), value in matrix.todok().items()},
    )


def _block_diagonal(first: sp.Matrix, second: sp.Matrix) -> sp.Matrix:
    entries = dict(first.todok())
    entries.update({(row + first.rows, column + first.cols): value for (row, column), value in second.todok().items()})
    return sp.SparseMatrix(first.rows + second.rows, first.cols + second.cols, entries)


def _double_frame(matrix: sp.Matrix, source_stage: int, residual: bool = False) -> sp.Matrix:
    lower = _conjugate_rows(matrix, -1 if residual else 1)
    return _block_diagonal(matrix, lower)[:, list(doubling_column_order(source_stage))]


def _double_diagonal(values: Sequence[Any], source_stage: int) -> tuple[Any, ...]:
    duplicated = tuple(values) + tuple(values)
    return tuple(duplicated[index] for index in doubling_column_order(source_stage))


@dataclass(frozen=True)
class ExpandedFrame:
    stage: int
    coefficients: tuple[Fraction, ...]
    matrix: RationalMatrix
    gram_diagonal: tuple[Fraction, ...]
    factors: tuple[Fraction, ...]

    @property
    def kernel_slots(self) -> tuple[int, ...]:
        return tuple(index for index, factor in enumerate(self.factors) if factor == 0)

    @property
    def nullity(self) -> int:
        return len(self.kernel_slots)


def expanded_frame(stage: int, coefficients: Sequence[int | Fraction]) -> ExpandedFrame:
    """Build the exact polynomial/rational frame within the expansion boundary."""
    _expanded_dimension(stage)
    base = incidence_frame(coefficients)
    frame = sp.SparseMatrix(base.matrix)
    diagonal, factors = base.gram_diagonal, base.factors
    for source_stage in range(BASE_STAGE, stage):
        frame = _double_frame(frame, source_stage)
        diagonal = _double_diagonal(diagonal, source_stage)
        factors = _double_diagonal(factors, source_stage)
    _require(all(value > 0 for value in diagonal), "doubled frame metric loses positivity")
    return ExpandedFrame(stage, base.coefficients, _fractions(frame), diagonal, factors)


def _conjugate_vector(values: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return (values[0],) + tuple(-value for value in values[1:])


def _apply_left(stage: int, coefficients: tuple[Fraction, ...], partner: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    if stage == BASE_STAGE:
        result = [Fraction(0)] * 32
        for basis_index, coefficient in zip(SUPPORT, coefficients, strict=True):
            for column, value in enumerate(partner):
                result[basis_index ^ column] += coefficient * cd_sign(32, basis_index, column) * value
        return tuple(result)
    half = len(partner) // 2
    first = _apply_left(stage - 1, coefficients, partner[:half])
    second = _apply_left(stage - 1, coefficients, _conjugate_vector(partner[half:]))
    return first + tuple(-value for value in _conjugate_vector(second))


def apply_left(
    stage: int, coefficients: Sequence[int | Fraction], partner: Sequence[int | Fraction]
) -> tuple[Fraction, ...]:
    """Apply L_(x,0,...) by the exact left/right recurrence without a dense matrix.

    Zero x is valid for multiplication; normalized incidence frames separately
    require a nonzero coefficient tuple.
    """
    dimension = _expanded_dimension(stage)
    return _apply_left(stage, _coefficients(coefficients), _entries(partner, dimension))


def lift_kernel_coordinates(
    stage: int, coefficients: Sequence[int | Fraction], coordinates: Sequence[int | Fraction]
) -> tuple[Fraction, ...]:
    """Lift weighted fiber coordinates after checking every scalar-factor equation."""
    point = expanded_frame(stage, coefficients)
    values = _entries(coordinates, len(point.factors))
    if any(factor * value for factor, value in zip(point.factors, values, strict=True)):
        raise ValueError("fiber coordinates violate the doubled factor equations")
    return tuple(Fraction(value) for value in sp.SparseMatrix(point.matrix) * sp.Matrix(values))


def kernel_coordinates(
    stage: int, coefficients: Sequence[int | Fraction], partner: Sequence[int | Fraction]
) -> tuple[Fraction, ...]:
    """Recover weighted coordinates by D^-1 G^T on the complete doubled kernel."""
    point = expanded_frame(stage, coefficients)
    values = _entries(partner, len(point.matrix))
    if any(apply_left(stage, point.coefficients, values)):
        raise ValueError("partner lies outside the embedded left-multiplication kernel")
    projected = sp.SparseMatrix(point.matrix).T * sp.Matrix(values)
    recovered = tuple(Fraction(value) / weight for value, weight in zip(projected, point.gram_diagonal, strict=True))
    _require(lift_kernel_coordinates(stage, point.coefficients, recovered) == values, "doubled kernel inverse fails")
    return recovered


def kernel_inclusion(stage: int, source: Stratum, target: Stratum) -> RationalMatrix:
    """Retain literal factor-block inclusions along a base-stratum closure."""
    _expanded_dimension(stage)
    if not closure_contains(source, target):
        raise ValueError("target stratum lies outside the source closure")
    block_size = 1 << (stage - 3)
    source_blocks = sorted({slot // 4 for slot in source.kernel_slots})
    target_blocks = sorted({slot // 4 for slot in target.kernel_slots})
    source_slots = tuple(block * block_size + local for block in source_blocks for local in range(block_size))
    target_slots = tuple(block * block_size + local for block in target_blocks for local in range(block_size))
    return tuple(
        tuple(Fraction(source_slot == target_slot) for source_slot in source_slots) for target_slot in target_slots
    )


def _action(dimension: int, coefficients: Sequence[Any], right: bool = False) -> sp.Matrix:
    entries = {}
    for column in range(dimension):
        for basis_index, coefficient in zip(SUPPORT, coefficients, strict=True):
            sign = cd_sign(dimension, column, basis_index) if right else cd_sign(dimension, basis_index, column)
            entries[basis_index ^ column, column] = coefficient * sign
    return sp.SparseMatrix(dimension, dimension, entries)


def _pure_right_from_left(left: sp.Matrix) -> sp.Matrix:
    return sp.SparseMatrix(
        left.rows,
        left.cols,
        {
            (row, column): -(1 if row == 0 else -1) * value * (1 if column == 0 else -1)
            for (row, column), value in left.todok().items()
        },
    )


def _audit_symbolic_recurrence() -> list[dict[str, Any]]:
    frame, residual, diagonal, factors = _frame_matrices(COEFFICIENTS)
    frame, residual = sp.SparseMatrix(frame), sp.SparseMatrix(residual)
    records = []
    for stage in range(BASE_STAGE, MAX_EXPANDED_STAGE):
        dimension = _expanded_dimension(stage)
        left, right = _action(dimension, COEFFICIENTS), _action(dimension, COEFFICIENTS, right=True)
        _equal(right, _pure_right_from_left(left), "pure-element right-action conjugation")
        _require(right != left, "incorrect repeated-left operator escapes the right-action check")
        _require(right != -_pure_right_from_left(left), "missing conjugation minus escapes the right-action check")
        _equal(_conjugate_rows(frame), -frame, "frame columns remain imaginary")
        next_left = _action(2 * dimension, COEFFICIENTS)
        _equal(next_left, _block_diagonal(left, right), "ordinary zero-padding operator")
        frame = _double_frame(frame, stage)
        residual = _double_frame(residual, stage, residual=True)
        diagonal = _double_diagonal(diagonal, stage)
        factors = _double_diagonal(factors, stage)
        _equal(frame.T * frame, sp.diag(*diagonal), "recursive positive diagonal Gram identity")
        _equal(next_left * frame, residual * sp.diag(*factors), "recursive factor action identity")
        block_size = 1 << (stage - 2)
        wrong_order = list(range(frame.cols))
        wrong_order[0], wrong_order[block_size] = wrong_order[block_size], wrong_order[0]
        try:
            _equal(
                next_left * frame[:, wrong_order],
                residual[:, wrong_order] * sp.diag(*factors),
                "cross-factor column permutation",
            )
        except RuntimeError:
            pass
        else:
            raise RuntimeError("cross-factor column permutation escapes the factor identity")
        records.append(
            {
                "source_stage": stage,
                "target_stage": stage + 1,
                "target_dimension": 2 * dimension,
                "frame_shape": list(frame.shape),
                "factor_block_dimension": block_size,
                "column_regrouping": doubling_column_order(stage),
                "conjugation_and_doubling_verified": True,
                "gram_and_factor_identities_verified": True,
            }
        )
    return records


def _audit_rational_case(task: tuple[int, tuple[int, ...]]) -> dict[str, Any]:
    stage, linear_coordinates = task
    coefficients = tuple(Fraction(value) for value in LINEAR_TRANSFORM.T * sp.Matrix(linear_coordinates) / 4)
    point = expanded_frame(stage, coefficients)
    base_nullity = evaluate_four_support(coefficients).nullity
    _require(
        point.nullity == base_nullity * (1 << (stage - BASE_STAGE)), "nullity doubling disagrees with the base theorem"
    )
    coordinates = tuple(
        Fraction(index + 1, 7) if factor == 0 else Fraction(0) for index, factor in enumerate(point.factors)
    )
    partner = lift_kernel_coordinates(stage, coefficients, coordinates)
    _require(
        kernel_coordinates(stage, coefficients, partner) == coordinates, "exact doubled forward/inverse round trip"
    )
    _require(
        sum(value * value for value in partner)
        == sum(weight * value * value for weight, value in zip(point.gram_diagonal, coordinates, strict=True)),
        "doubled weighted sphere metric",
    )
    arbitrary = tuple(Fraction(index - 7, 11) for index in range(1 << stage))
    direct = tuple(Fraction(value) for value in _action(1 << stage, coefficients) * sp.Matrix(arbitrary))
    _require(
        apply_left(stage, coefficients, arbitrary) == direct,
        "structured operator disagrees with independent basis multiplication",
    )
    return {
        "stage": stage,
        "linear_coordinates": linear_coordinates,
        "coefficients": [str(value) for value in coefficients],
        "nullity": point.nullity,
        "frame_shape": [len(point.matrix), len(point.factors)],
        "round_trip_and_metric_verified": True,
        "independent_operator_verified": True,
    }


def _audit_invalid_inputs() -> int:
    checks = 0
    for stage in (True, 4, -1, 5.0):
        try:
            DoublingModel(stage)  # type: ignore[arg-type]
        except ValueError:
            checks += 1
        else:
            raise RuntimeError("invalid model stage accepted")
    for stage in (9, 10**9):
        try:
            expanded_frame(stage, (1, 0, 0, 0))
        except ValueError:
            checks += 1
        else:
            raise RuntimeError("oversized expanded stage accepted")
    invalid_calls = (
        lambda: expanded_frame(5, (0, 0, 0, 0)),
        lambda: expanded_frame(5, (1.0, 0, 0, 0)),  # type: ignore[arg-type]
        lambda: expanded_frame(5, (True, 0, 0, 0)),
        lambda: apply_left(5, (1, 0, 0, 0), (0,) * 31),
        lambda: doubling_column_order(8),
        lambda: lift_kernel_coordinates(5, (1, 0, 0, 0), (1,) + (0,) * 19),
        lambda: kernel_coordinates(5, (1, 0, 0, 0), (1,) + (0,) * 31),
        lambda: kernel_inclusion(5, Stratum((1, 1, 1, -1), 0), Stratum((1, 1, 1, -1), 1)),
    )
    for call in invalid_calls:
        try:
            call()
        except ValueError:
            checks += 1
        else:
            raise RuntimeError("invalid doubling domain accepted")
    _require(apply_left(5, (0, 0, 0, 0), (1,) * 32) == (Fraction(0),) * 32, "zero multiplier action")
    huge = DoublingModel(10**9)
    _require(
        huge.ambient_exponent == 10**9 and huge.block_exponent == 10**9 - 3, "allocation-free descriptor exponents"
    )
    return checks


def audit_four_support_doubling() -> dict[str, Any]:
    """Replay finite exact regressions for the separately proved uniform theorem."""
    examples = ((1, 1, 1, 1), (1, 1, 1, -1), (0, 1, 1, 1), (0, 0, 1, 1), (0, 1, 0, 1), (0, 0, 0, 1))
    tasks = [(stage, example) for stage in range(BASE_STAGE, MAX_EXPANDED_STAGE + 1) for example in examples]
    rational_records = parallel.ordered_map(_audit_rational_case, tasks, min_items=2)
    source, target = Stratum((1, 1, 1, -1), 0), Stratum((1, 0, 0, 0), 0)
    inclusion_shapes = []
    for stage in range(BASE_STAGE, MAX_EXPANDED_STAGE + 1):
        inclusion = sp.Matrix(kernel_inclusion(stage, source, target))
        _equal(inclusion.T * inclusion, sp.eye(inclusion.cols), "doubled kernel inclusion metric")
        inclusion_shapes.append({"stage": stage, "shape": list(inclusion.shape)})
    return {
        "schema": "cayley-dickson-four-support-ordinary-doubling-v1",
        "qpu_executed": False,
        "sympy_version": sp.__version__,
        "theorem_domain": "every integer stage>=5; ordinary zero padding of support {1,10,18,25}",
        "expanded_artifact_domain": {
            "minimum_stage": BASE_STAGE,
            "maximum_stage": MAX_EXPANDED_STAGE,
            "maximum_dimension": 1 << MAX_EXPANDED_STAGE,
        },
        "large_stage_descriptor": DoublingModel(10**9).record(),
        "symbolic_recurrence": _audit_symbolic_recurrence(),
        "rational_cases": rational_records,
        "kernel_inclusion_shapes": inclusion_shapes,
        "invalid_inputs_rejected": _audit_invalid_inputs(),
        "negative_controls": [
            "repeated-left operator rejected",
            "missing conjugation minus rejected",
            "cross-factor regrouping rejected",
            "oversized allocation rejected before expansion",
            "origin frame and malformed domains rejected",
            "reversed closure inclusion rejected",
        ],
        "structural_induction": "conjugation anti-automorphism; pure right action=-C L C; L_(x,0)=diag(L_x,-C L_x C)",
        "global_model": (
            "five blocks of dimension 2^(stage-3), masked by Delta,p,q,r,s; "
            "normalized frame and transpose give inverse incidence maps"
        ),
        "proof_boundary": (
            "The written structural induction proves every stage; exact polynomial regressions verify the "
            "implementation through dimension 256. A Rocq kernel proof remains separate."
        ),
        "scope": (
            "The same four-dimensional coefficient base, 96 normalized strata and 704 closure incidences including "
            "96 reflexive pairs; other coefficient directions and computed topological invariants "
            "remain outside the theorem."
        ),
    }


def main() -> int:
    print(json.dumps(audit_four_support_doubling(), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
