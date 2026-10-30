"""Holomorphic Schur blow-ups for the eight first-order-resolved A_5 incidences."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import resource
import subprocess
import sys
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from fractions import Fraction
from functools import partial
from pathlib import Path
from typing import Any, TypeAlias, cast

import flint

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import holomorphic_kernel_lemma as kernel_lemma  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "a5-kernel-attachments-holomorphic-gauss-fibers-v1"
FIRST_ORDER_RESULT = HERE / "first-order-normal-cones-result.json"
KERNEL_LEMMA_RESULT = HERE / "holomorphic-kernel-lemma-result.json"
SOURCE_PATHS = (
    HERE / "holomorphic_gauss_fibers.py",
    HERE / "holomorphic_kernel_lemma.py",
    KERNEL_LEMMA_RESULT,
    FIRST_ORDER_RESULT,
    ROOT / "gororoba_quantum" / "cd_core.py",
    ROOT / "gororoba_quantum" / "parallel.py",
)
RESOLVED_INCIDENCES = (
    "E8bar->B9",
    "E8bar->V",
    "Iso->B9",
    "W8->B9",
    "X+->B9",
    "X+->Va+",
    "X-->B9",
    "X-->Va-",
)
ORBIT_KEYS = {"E8bar": "Ehat", "X+": "Xp", "X-": "Xm", "Va+": "Vap", "Va-": "Vam"}
COMPLEX_DIMENSION = 15
BOUNDARY_C_RANK = 8
BOUNDARY_C_KERNEL_DIMENSION = 7
BOUNDARY_BORDERED_RANK = 10
BOUNDARY_BORDERED_KERNEL_DIMENSION = 6
MODULAR_PRIME = 32003
SINGULAR_MEMORY_LIMIT = "4294967296"
WORKER_MEMORY_LIMIT = int(SINGULAR_MEMORY_LIMIT)
SINGULAR_TIMEOUT_SECONDS = 300

Gaussian = kernel_lemma.Gaussian
GaussianVector = kernel_lemma.GaussianVector
GaussianMatrix = kernel_lemma.GaussianMatrix
RationalVector: TypeAlias = tuple[Fraction, ...]
GaussianPolynomial: TypeAlias = tuple[Any, Any]
GaussianPolynomialMatrix: TypeAlias = tuple[tuple[GaussianPolynomial, ...], ...]


@dataclass(frozen=True)
class IncidenceTask:
    committed_row: dict[str, Any]
    omitted_slice_variable: int | None = None


@dataclass(frozen=True)
class PolynomialData:
    slice_names: tuple[str, ...]
    boundary_c_rank: int
    boundary_bordered_rank: int
    pivot_indices: tuple[int, ...]
    pivot_pfaffian_at_origin: Gaussian
    coordinates: tuple[GaussianPolynomial, ...]
    leading_coordinates: tuple[GaussianPolynomial, ...]
    selected_indices: tuple[int, ...]
    selected_leading_coordinates: tuple[GaussianPolynomial, ...]
    linear_coordinate_matrix: tuple[tuple[Gaussian, ...], ...]
    common_origin_order: int
    maximum_total_degree: int
    maximum_component_terms: int
    coordinate_sha256: str
    schur_skew: bool
    pfaffian_adjugate_identity: bool
    restriction_matches_bordered_form: bool


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _cap_worker_memory() -> None:
    current_soft, current_hard = resource.getrlimit(resource.RLIMIT_AS)
    hard_limit = WORKER_MEMORY_LIMIT if current_hard < 0 else min(current_hard, WORKER_MEMORY_LIMIT)
    soft_limit = hard_limit if current_soft < 0 else min(current_soft, hard_limit)
    resource.setrlimit(resource.RLIMIT_AS, (soft_limit, hard_limit))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_path(path: Path) -> tuple[str, str]:
    return str(path.relative_to(ROOT)), _sha256(path)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"{path.name} does not hold a JSON object")
    return value


def _gaussian_text(value: Gaussian) -> list[str]:
    return [str(value[0]), str(value[1])]


def _numeric_transpose(matrix: GaussianMatrix) -> GaussianMatrix:
    return tuple(tuple(matrix[row][column] for row in range(len(matrix))) for column in range(len(matrix[0])))


def _numeric_matrix_multiply(left: GaussianMatrix, right: GaussianMatrix) -> GaussianMatrix:
    _require(len(left[0]) == len(right), "numeric matrix product dimensions disagree")
    right_columns = _numeric_transpose(right)
    return tuple(
        tuple(
            kernel_lemma._gaussian_sum(
                kernel_lemma._gaussian_multiply(left_value, right_value)
                for left_value, right_value in zip(left_row, right_column, strict=True)
            )
            for right_column in right_columns
        )
        for left_row in left
    )


def _numeric_extract(matrix: GaussianMatrix, rows: Sequence[int], columns: Sequence[int]) -> GaussianMatrix:
    return tuple(tuple(matrix[row][column] for column in columns) for row in rows)


def _numeric_inverse(matrix: GaussianMatrix) -> GaussianMatrix:
    size = len(matrix)
    _require(size > 0 and all(len(row) == size for row in matrix), "numeric inverse needs a nonempty square matrix")
    augmented = tuple(
        (*matrix[row], *(kernel_lemma.ONE if row == column else kernel_lemma.ZERO for column in range(size)))
        for row in range(size)
    )
    reduced, pivots = kernel_lemma._rref(augmented)
    _require(pivots[:size] == tuple(range(size)), "numeric matrix is singular")
    _require(all(pivot < size for pivot in pivots), "numeric inverse system is inconsistent")
    return tuple(tuple(reduced[row][size + column] for column in range(size)) for row in range(size))


def _find_principal_pivot(matrix: GaussianMatrix, matrix_rank: int) -> tuple[int, ...]:
    selected: tuple[int, ...] = ()
    while len(selected) < matrix_rank:
        remaining = tuple(index for index in range(len(matrix)) if index not in selected)
        extension = next(
            (
                pair
                for pair in itertools.combinations(remaining, 2)
                if kernel_lemma._rank(_numeric_extract(matrix, (*selected, *pair), (*selected, *pair)))
                == len(selected) + 2
            ),
            None,
        )
        if extension is None:
            raise RuntimeError(f"rank-{matrix_rank} skew matrix has no principal pivot extension")
        selected = (*selected, *extension)
    return selected


def _principal_frame(
    matrix: GaussianMatrix, matrix_rank: int
) -> tuple[tuple[int, ...], GaussianMatrix, GaussianMatrix]:
    pivot = _find_principal_pivot(matrix, matrix_rank)
    free = tuple(index for index in range(len(matrix)) if index not in pivot)
    block = _numeric_extract(matrix, pivot, pivot)
    upper_right = _numeric_extract(matrix, pivot, free)
    pivot_rows = _numeric_matrix_multiply(_numeric_inverse(block), upper_right)
    pivot_rows = tuple(tuple(kernel_lemma._gaussian_negate(value) for value in row) for row in pivot_rows)
    frame_rows: list[tuple[Gaussian, ...]] = []
    complement_rows: list[tuple[Gaussian, ...]] = []
    for row in range(len(matrix)):
        if row in pivot:
            pivot_position = pivot.index(row)
            frame_rows.append(pivot_rows[pivot_position])
            complement_rows.append(
                tuple(
                    kernel_lemma.ONE if column == pivot_position else kernel_lemma.ZERO for column in range(len(pivot))
                )
            )
        else:
            free_position = free.index(row)
            frame_rows.append(
                tuple(kernel_lemma.ONE if column == free_position else kernel_lemma.ZERO for column in range(len(free)))
            )
            complement_rows.append(tuple(kernel_lemma.ZERO for _column in pivot))
    return pivot, tuple(frame_rows), tuple(complement_rows)


def _solve_frame_coordinates(frame: GaussianMatrix, vectors: GaussianMatrix) -> GaussianMatrix:
    _require(len(frame) == len(vectors), "frame and vector row counts disagree")
    frame_width = len(frame[0])
    vector_width = len(vectors[0])
    solutions: list[GaussianVector] = []
    for vector_column in range(vector_width):
        augmented = tuple((*frame[row], vectors[row][vector_column]) for row in range(len(frame)))
        reduced, pivots = kernel_lemma._rref(augmented)
        _require(pivots == tuple(range(frame_width)), "vector does not lie in the kernel frame")
        solutions.append(tuple(reduced[row][-1] for row in range(frame_width)))
    return tuple(tuple(solutions[column][row] for column in range(vector_width)) for row in range(frame_width))


def _numeric_congruence(form: GaussianMatrix, frame: GaussianMatrix) -> GaussianMatrix:
    return _numeric_matrix_multiply(_numeric_matrix_multiply(_numeric_transpose(frame), form), frame)


def _polynomial_zero(context: Any) -> Any:
    return context.gens()[0] * 0


def _polynomial_constant(context: Any, value: Fraction) -> Any:
    return _polynomial_zero(context) + flint.fmpq(value.numerator, value.denominator)


def _gpoly_zero(context: Any) -> GaussianPolynomial:
    zero = _polynomial_zero(context)
    return zero, zero


def _gpoly_constant(context: Any, value: Gaussian) -> GaussianPolynomial:
    return _polynomial_constant(context, value[0]), _polynomial_constant(context, value[1])


def _gpoly_add(left: GaussianPolynomial, right: GaussianPolynomial) -> GaussianPolynomial:
    return left[0] + right[0], left[1] + right[1]


def _gpoly_negate(value: GaussianPolynomial) -> GaussianPolynomial:
    return -value[0], -value[1]


def _gpoly_subtract(left: GaussianPolynomial, right: GaussianPolynomial) -> GaussianPolynomial:
    return left[0] - right[0], left[1] - right[1]


def _gpoly_multiply(left: GaussianPolynomial, right: GaussianPolynomial) -> GaussianPolynomial:
    return left[0] * right[0] - left[1] * right[1], left[0] * right[1] + left[1] * right[0]


def _gpoly_scale_gaussian(context: Any, value: GaussianPolynomial, scalar: Gaussian) -> GaussianPolynomial:
    return _gpoly_multiply(value, _gpoly_constant(context, scalar))


def _gpoly_sum(context: Any, values: Iterable[GaussianPolynomial]) -> GaussianPolynomial:
    total = _gpoly_zero(context)
    for value in values:
        total = _gpoly_add(total, value)
    return total


def _gpoly_is_zero(value: GaussianPolynomial) -> bool:
    return value[0] == 0 and value[1] == 0


def _gpoly_matrix_multiply(
    context: Any, left: GaussianPolynomialMatrix, right: GaussianPolynomialMatrix
) -> GaussianPolynomialMatrix:
    _require(len(left[0]) == len(right), "polynomial matrix product dimensions disagree")
    right_columns = tuple(tuple(right[row][column] for row in range(len(right))) for column in range(len(right[0])))
    return tuple(
        tuple(
            _gpoly_sum(
                context,
                (
                    _gpoly_multiply(left_value, right_value)
                    for left_value, right_value in zip(left_row, column, strict=True)
                ),
            )
            for column in right_columns
        )
        for left_row in left
    )


def _gpoly_extract(
    matrix: GaussianPolynomialMatrix, rows: Sequence[int], columns: Sequence[int]
) -> GaussianPolynomialMatrix:
    return tuple(tuple(matrix[row][column] for column in columns) for row in rows)


def _gpoly_transpose(matrix: GaussianPolynomialMatrix) -> GaussianPolynomialMatrix:
    return tuple(tuple(matrix[row][column] for row in range(len(matrix))) for column in range(len(matrix[0])))


def _gpoly_congruence(
    context: Any, form: GaussianPolynomialMatrix, numeric_frame: GaussianMatrix
) -> GaussianPolynomialMatrix:
    polynomial_frame = tuple(tuple(_gpoly_constant(context, value) for value in row) for row in numeric_frame)
    return _gpoly_matrix_multiply(
        context,
        _gpoly_matrix_multiply(context, _gpoly_transpose(polynomial_frame), form),
        polynomial_frame,
    )


def _gpoly_pfaffian(context: Any, matrix: GaussianPolynomialMatrix) -> GaussianPolynomial:
    size = len(matrix)
    _require(size % 2 == 0 and all(len(row) == size for row in matrix), "Pfaffian input must be even square")
    if size == 0:
        return _gpoly_constant(context, kernel_lemma.ONE)
    total = _gpoly_zero(context)
    for column in range(1, size):
        remaining = tuple(index for index in range(size) if index not in (0, column))
        minor = _gpoly_extract(matrix, remaining, remaining)
        term = _gpoly_multiply(matrix[0][column], _gpoly_pfaffian(context, minor))
        total = _gpoly_add(total, term) if column % 2 else _gpoly_subtract(total, term)
    return total


def _pfaffian_adjugate(context: Any, matrix: GaussianPolynomialMatrix) -> GaussianPolynomialMatrix:
    size = len(matrix)
    rows = [[_gpoly_zero(context) for _column in range(size)] for _row in range(size)]
    for first in range(size):
        for second in range(first + 1, size):
            remaining = tuple(index for index in range(size) if index not in (first, second))
            cofactor = _gpoly_pfaffian(context, _gpoly_extract(matrix, remaining, remaining))
            if (first + second) % 2:
                cofactor = _gpoly_negate(cofactor)
            rows[first][second] = cofactor
            rows[second][first] = _gpoly_negate(cofactor)
    return tuple(tuple(row) for row in rows)


def _constant_fraction(polynomial: Any, variable_count: int) -> Fraction:
    coefficient = polynomial.to_dict().get((0,) * variable_count, flint.fmpq(0))
    return Fraction(int(coefficient.p), int(coefficient.q))


def _gpoly_constant_coefficient(value: GaussianPolynomial, variable_count: int) -> Gaussian:
    return _constant_fraction(value[0], variable_count), _constant_fraction(value[1], variable_count)


def _homogeneous_part(context: Any, polynomial: Any, degree: int) -> Any:
    selected = {
        exponents: coefficient for exponents, coefficient in polynomial.to_dict().items() if sum(exponents) == degree
    }
    return context.from_dict(selected)


def _gpoly_homogeneous_part(context: Any, value: GaussianPolynomial, degree: int) -> GaussianPolynomial:
    return _homogeneous_part(context, value[0], degree), _homogeneous_part(context, value[1], degree)


def _polynomial_order(polynomial: Any) -> int | None:
    terms = polynomial.to_dict()
    order = min((sum(exponents) for exponents in terms), default=None)
    return int(order) if order is not None else None


def _gpoly_order(value: GaussianPolynomial) -> int | None:
    orders = tuple(order for order in (_polynomial_order(value[0]), _polynomial_order(value[1])) if order is not None)
    return min(orders) if orders else None


def _gpoly_total_degree(value: GaussianPolynomial) -> int:
    degrees = tuple(int(polynomial.total_degree()) for polynomial in value if polynomial != 0)
    return max(degrees, default=-1)


def _gpoly_term_count(value: GaussianPolynomial) -> int:
    return max(len(value[0].to_dict()), len(value[1].to_dict()))


def _gpoly_coefficient(value: GaussianPolynomial, exponents: tuple[int, ...]) -> Gaussian:
    real = value[0].to_dict().get(exponents, flint.fmpq(0))
    imaginary = value[1].to_dict().get(exponents, flint.fmpq(0))
    return Fraction(int(real.p), int(real.q)), Fraction(int(imaginary.p), int(imaginary.q))


def _gpoly_text(value: GaussianPolynomial) -> str:
    return f"({value[0]})+(I)*({value[1]})"


def _coordinate_sha256(values: Sequence[GaussianPolynomial]) -> str:
    payload = json.dumps([_gpoly_text(value) for value in values], separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _polynomial_c_matrix(context: Any, z: Sequence[GaussianPolynomial]) -> GaussianPolynomialMatrix:
    rows: list[tuple[GaussianPolynomial, ...]] = []
    for row in range(1, COMPLEX_DIMENSION + 1):
        values: list[GaussianPolynomial] = []
        for column in range(1, COMPLEX_DIMENSION + 1):
            product = row ^ column
            values.append(
                _gpoly_zero(context)
                if product == 0
                else _gpoly_scale_gaussian(
                    context, z[product - 1], (Fraction(cd_sign(16, product, column)), Fraction(0))
                )
            )
        rows.append(tuple(values))
    return tuple(rows)


def _transformation_matrix(complement: GaussianMatrix, kernel_frame: GaussianMatrix) -> GaussianMatrix:
    return tuple((*complement[row], *kernel_frame[row]) for row in range(len(complement)))


def _matrix_equal(left: GaussianPolynomialMatrix, right: GaussianPolynomialMatrix) -> bool:
    return left == right


def _schur_polynomials(task: IncidenceTask) -> PolynomialData:
    row = task.committed_row
    boundary_point = tuple(Fraction(value) for value in row["boundary_point"])
    slice_columns = tuple(int(value) for value in row["slice_columns_zero_based"])
    slice_names = tuple(f"t{index + 1}" for index in range(len(slice_columns)))
    context = flint.fmpq_mpoly_ctx.get(slice_names, "degrevlex")
    variables = tuple(context.gens())
    split_coordinates = [_polynomial_constant(context, value) for value in boundary_point]
    for variable_index, coordinate in enumerate(slice_columns):
        if variable_index != task.omitted_slice_variable:
            split_coordinates[coordinate] += variables[variable_index]
    z_polynomials = tuple(
        _gpoly_scale_gaussian(
            context,
            (split_coordinate, _polynomial_zero(context)),
            kernel_lemma._phase(index.bit_count()),
        )
        for index, split_coordinate in enumerate(split_coordinates, start=1)
    )
    c_polynomial = _polynomial_c_matrix(context, z_polynomials)

    boundary_z = kernel_lemma._original_z_from_split(boundary_point)
    c_at_origin = kernel_lemma._c_matrix(boundary_z)
    boundary_c_rank = kernel_lemma._rank(c_at_origin)
    _require(boundary_c_rank == BOUNDARY_C_RANK, f"{row['incidence']} boundary C_z rank changed")
    c_pivot, c_kernel_frame, c_complement = _principal_frame(c_at_origin, BOUNDARY_C_RANK)
    transformation = _transformation_matrix(c_complement, c_kernel_frame)
    transformed = _gpoly_congruence(context, c_polynomial, transformation)
    pivot_block = _gpoly_extract(transformed, range(BOUNDARY_C_RANK), range(BOUNDARY_C_RANK))
    coupling = _gpoly_extract(
        transformed,
        range(BOUNDARY_C_RANK),
        range(BOUNDARY_C_RANK, COMPLEX_DIMENSION),
    )
    kernel_block = _gpoly_extract(
        transformed,
        range(BOUNDARY_C_RANK, COMPLEX_DIMENSION),
        range(BOUNDARY_C_RANK, COMPLEX_DIMENSION),
    )
    pivot_pfaffian = _gpoly_pfaffian(context, pivot_block)
    pfaffian_adjugate = _pfaffian_adjugate(context, pivot_block)
    pfaffian_identity = _gpoly_matrix_multiply(context, pivot_block, pfaffian_adjugate)
    expected_identity = tuple(
        tuple(
            pivot_pfaffian if row_index == column_index else _gpoly_zero(context)
            for column_index in range(BOUNDARY_C_RANK)
        )
        for row_index in range(BOUNDARY_C_RANK)
    )
    correction = _gpoly_matrix_multiply(
        context,
        _gpoly_matrix_multiply(context, _gpoly_transpose(coupling), pfaffian_adjugate),
        coupling,
    )
    numerator = tuple(
        tuple(
            _gpoly_add(
                _gpoly_multiply(pivot_pfaffian, kernel_block[row_index][column_index]),
                correction[row_index][column_index],
            )
            for column_index in range(BOUNDARY_C_KERNEL_DIMENSION)
        )
        for row_index in range(BOUNDARY_C_KERNEL_DIMENSION)
    )
    schur_skew = all(
        _gpoly_is_zero(_gpoly_add(numerator[row_index][column_index], numerator[column_index][row_index]))
        for row_index in range(BOUNDARY_C_KERNEL_DIMENSION)
        for column_index in range(BOUNDARY_C_KERNEL_DIMENSION)
    )
    coordinates = tuple(
        numerator[row_index][column_index]
        for row_index in range(BOUNDARY_C_KERNEL_DIMENSION)
        for column_index in range(row_index + 1, BOUNDARY_C_KERNEL_DIMENSION)
    )
    coordinate_orders = tuple(order for order in map(_gpoly_order, coordinates) if order is not None)
    common_origin_order = min(coordinate_orders) if coordinate_orders else -1
    _require(
        common_origin_order == 1,
        f"{row['incidence']} Schur base ideal does not have order one",
    )
    leading_coordinates = tuple(_gpoly_homogeneous_part(context, coordinate, 1) for coordinate in coordinates)
    coefficient_rows = tuple(
        tuple(
            _gpoly_coefficient(
                coordinate,
                tuple(int(index == variable_index) for index in range(len(slice_names))),
            )
            for variable_index in range(len(slice_names))
        )
        for coordinate in leading_coordinates
    )
    transposed_coefficients = tuple(
        tuple(coefficient_rows[row_index][column_index] for row_index in range(len(coefficient_rows)))
        for column_index in range(len(slice_names))
    )
    _reduced, independent_indices = kernel_lemma._rref(transposed_coefficients)
    selected_coordinates = tuple(leading_coordinates[index] for index in independent_indices)
    linear_coordinate_matrix = tuple(coefficient_rows[index] for index in independent_indices)

    bordered_at_origin = kernel_lemma._bordered_matrix(boundary_z, c_at_origin)
    boundary_bordered_rank = kernel_lemma._rank(bordered_at_origin)
    _require(
        boundary_bordered_rank == BOUNDARY_BORDERED_RANK,
        f"{row['incidence']} boundary bordered-matrix rank changed",
    )
    _bordered_pivot, bordered_frame, _bordered_complement = _principal_frame(bordered_at_origin, BOUNDARY_BORDERED_RANK)
    _require(
        all(bordered_frame[0][column] == kernel_lemma.ZERO for column in range(BOUNDARY_BORDERED_KERNEL_DIMENSION)),
        f"{row['incidence']} bordered frame has a nonzero scalar row",
    )
    lower_bordered_frame = tuple(frame_row for frame_row in bordered_frame[1:])
    quotient_frame = _solve_frame_coordinates(c_kernel_frame, lower_bordered_frame)
    pfaffian_at_origin = _gpoly_constant_coefficient(pivot_pfaffian, len(slice_names))
    inverse_pfaffian = kernel_lemma._gaussian_inverse(pfaffian_at_origin)
    restriction_matches = True
    for variable_index, slice_coordinate in enumerate(slice_columns):
        exponents = tuple(int(index == variable_index) for index in range(len(slice_names)))
        leading_form = tuple(
            tuple(
                kernel_lemma._gaussian_multiply(
                    _gpoly_coefficient(numerator[row_index][column_index], exponents), inverse_pfaffian
                )
                for column_index in range(BOUNDARY_C_KERNEL_DIMENSION)
            )
            for row_index in range(BOUNDARY_C_KERNEL_DIMENSION)
        )
        restricted_leading = _numeric_congruence(leading_form, quotient_frame)
        split_direction = tuple(Fraction(index == slice_coordinate) for index in range(COMPLEX_DIMENSION))
        direct_derivative = kernel_lemma._c_matrix(kernel_lemma._original_z_from_split(split_direction))
        direct_restriction = _numeric_congruence(direct_derivative, lower_bordered_frame)
        restriction_matches = restriction_matches and restricted_leading == direct_restriction

    return PolynomialData(
        slice_names=slice_names,
        boundary_c_rank=boundary_c_rank,
        boundary_bordered_rank=boundary_bordered_rank,
        pivot_indices=c_pivot,
        pivot_pfaffian_at_origin=pfaffian_at_origin,
        coordinates=coordinates,
        leading_coordinates=leading_coordinates,
        selected_indices=independent_indices,
        selected_leading_coordinates=selected_coordinates,
        linear_coordinate_matrix=linear_coordinate_matrix,
        common_origin_order=common_origin_order,
        maximum_total_degree=max(map(_gpoly_total_degree, coordinates)),
        maximum_component_terms=max(map(_gpoly_term_count, coordinates)),
        coordinate_sha256=_coordinate_sha256(coordinates),
        schur_skew=schur_skew,
        pfaffian_adjugate_identity=_matrix_equal(pfaffian_identity, expected_identity),
        restriction_matches_bordered_form=restriction_matches,
    )


def _singular_expression(value: GaussianPolynomial) -> str:
    return _gpoly_text(value)


def _singular_script(
    characteristic: int,
    tangent_generators: Sequence[str],
    data: PolynomialData,
) -> str:
    coordinate_names = tuple(f"y{index + 1}" for index in range(len(data.selected_leading_coordinates)))
    variables = (*data.slice_names, *coordinate_names)
    graph_generators = tuple(
        f"{name}-({_singular_expression(coordinate)})"
        for name, coordinate in zip(coordinate_names, data.selected_leading_coordinates, strict=True)
    )
    selected_coordinates_text = ",".join(_singular_expression(value) for value in data.selected_leading_coordinates)
    context = data.leading_coordinates[0][0].context()
    pfaffian_minors: list[GaussianPolynomial] = []
    leading_matrix: list[list[GaussianPolynomial]] = [
        [_gpoly_zero(context) for _column in range(BOUNDARY_C_KERNEL_DIMENSION)]
        for _row in range(BOUNDARY_C_KERNEL_DIMENSION)
    ]
    coordinate_index = 0
    for row in range(BOUNDARY_C_KERNEL_DIMENSION):
        leading_matrix[row][row] = _gpoly_zero(context)
        for column in range(row + 1, BOUNDARY_C_KERNEL_DIMENSION):
            coordinate = data.leading_coordinates[coordinate_index]
            leading_matrix[row][column] = coordinate
            leading_matrix[column][row] = _gpoly_negate(coordinate)
            coordinate_index += 1
    for first, second, third, fourth in itertools.combinations(range(BOUNDARY_C_KERNEL_DIMENSION), 4):
        pfaffian_minors.append(
            _gpoly_add(
                _gpoly_subtract(
                    _gpoly_multiply(leading_matrix[first][second], leading_matrix[third][fourth]),
                    _gpoly_multiply(leading_matrix[first][third], leading_matrix[second][fourth]),
                ),
                _gpoly_multiply(leading_matrix[first][fourth], leading_matrix[second][third]),
            )
        )
    coefficient_field = f"({characteristic},I)" if characteristic else "(0,I)"
    lines = [
        'LIB "primdec.lib";',
        f"ring r = {coefficient_field}, ({','.join(variables)}), dp;",
        "minpoly = I2+1;",
        "option(redSB);",
        f"ideal T = {','.join(tangent_generators)};",
        f"ideal Graph = T, {','.join(graph_generators)};",
        f"ideal Image = std(eliminate(std(Graph), {'*'.join(data.slice_names)}));",
        f'"RESULT image_dimension", dim(Image)-{len(data.slice_names)};',
        '"RESULT image_degree", mult(Image);',
        '"RESULT image_generator_count", size(Image);',
        'for (int i=1; i<=size(Image); i++) { "RESULT image_generator_"+string(i), Image[i]; }',
        "list IP = minAssGTZ(Image);",
        '"RESULT image_component_count", size(IP);',
        f"ideal Degenerate = std(T + ideal({selected_coordinates_text}));",
        f'"RESULT degeneracy_dimension", dim(Degenerate)-{len(coordinate_names)};',
        '"RESULT degeneracy_degree", mult(Degenerate);',
        f"ideal Pfaffians = {','.join(_singular_expression(value) for value in pfaffian_minors)};",
        '"RESULT rank_four_pfaffians_vanish", size(reduce(Pfaffians, std(T))) == 0;',
    ]
    for chart_index, chart_name in enumerate(data.slice_names, start=1):
        lines.extend(
            (
                f"ideal Chart{chart_index} = T, {chart_name}-1;",
                f'"RESULT chart_{chart_index}_nonempty", size(reduce(ideal(1), std(Chart{chart_index}))) != 0;',
                f"ideal Base{chart_index} = Chart{chart_index}, {selected_coordinates_text};",
                f'"RESULT chart_{chart_index}_base_empty", size(reduce(ideal(1), std(Base{chart_index}))) == 0;',
            )
        )
    lines.append("quit;")
    return "\n".join(lines)


def _parse_singular(stdout: str, stderr: str, return_code: int) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in stdout.splitlines():
        match = re.match(r"^RESULT (\S+) (.*)$", line.strip())
        if match:
            parsed[match.group(1)] = match.group(2).strip()
    if return_code != 0 or "error" in stderr.lower() or "? " in stdout:
        parsed["singular_error"] = (stderr + stdout)[-4000:]
    return parsed


def _run_singular(script: str) -> dict[str, str]:
    try:
        process = subprocess.run(
            ["prlimit", f"--as={SINGULAR_MEMORY_LIMIT}", "Singular", "-q", "--no-warn"],
            input=script,
            capture_output=True,
            text=True,
            check=False,
            timeout=SINGULAR_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("Singular exceeded the five-minute incidence limit") from error
    return _parse_singular(process.stdout, process.stderr, process.returncode)


def _singular_summary(result: dict[str, str], slice_names: Sequence[str]) -> dict[str, Any]:
    _require("singular_error" not in result, result.get("singular_error", "Singular failed"))
    image_generator_count = int(result["image_generator_count"])
    chart_rows = tuple(
        {
            "chart": chart_index,
            "exceptional_coordinate": slice_names[chart_index - 1],
            "substitution": (
                f"{slice_names[chart_index - 1]}=e and every other slice coordinate=e*u; "
                "divide the Schur coordinates by e and set e=0, equivalently use their linear parts with "
                f"{slice_names[chart_index - 1]}=1"
            ),
            "nonempty": result[f"chart_{chart_index}_nonempty"] == "1",
            "base_empty": result[f"chart_{chart_index}_base_empty"] == "1",
        }
        for chart_index in range(1, len(slice_names) + 1)
    )
    image_generators = tuple(result[f"image_generator_{index}"] for index in range(1, image_generator_count + 1))
    return {
        "image_affine_dimension": int(result["image_dimension"]),
        "image_projective_dimension": int(result["image_dimension"]) - 1,
        "image_degree": int(result["image_degree"]),
        "image_component_count": int(result["image_component_count"]),
        "image_generators": list(image_generators),
        "image_generator_sha256": hashlib.sha256("\n".join(image_generators).encode("utf-8")).hexdigest(),
        "affine_degeneracy_dimension": int(result["degeneracy_dimension"]),
        "affine_degeneracy_degree": int(result["degeneracy_degree"]),
        "rank_four_pfaffians_vanish": result["rank_four_pfaffians_vanish"] == "1",
        "chart_count": len(slice_names),
        "nonempty_chart_count": sum(bool(row["nonempty"]) for row in chart_rows),
        "nonempty_charts_base_free": all((not bool(row["nonempty"])) or bool(row["base_empty"]) for row in chart_rows),
        "charts": list(chart_rows),
    }


def _comparison_tuple(summary: dict[str, Any]) -> tuple[int, int, int]:
    return (
        int(summary["image_affine_dimension"]),
        int(summary["image_degree"]),
        int(summary["image_component_count"]),
    )


def _expected_image_tuple(row: dict[str, Any]) -> tuple[int, int, int]:
    image = row["first_order_image"]
    return int(image["affine_dimension"]), int(image["degree"]), int(image["component_count"])


def _analyze_incidence(task: IncidenceTask) -> dict[str, Any]:
    _cap_worker_memory()
    row = task.committed_row
    data = _schur_polynomials(task)
    tangent_generators = tuple(str(value) for value in row["tangent_cone"]["generators"])
    modular_result = _singular_summary(
        _run_singular(_singular_script(MODULAR_PRIME, tangent_generators, data)), data.slice_names
    )
    rational_result = _singular_summary(_run_singular(_singular_script(0, tangent_generators, data)), data.slice_names)
    expected_image = _expected_image_tuple(row)
    modular_matches = _comparison_tuple(modular_result) == expected_image
    rational_matches = _comparison_tuple(rational_result) == expected_image
    characteristics_agree = _comparison_tuple(modular_result) == _comparison_tuple(rational_result)
    one_blowup_resolves = (
        rational_result["affine_degeneracy_dimension"] == 0
        and bool(rational_result["nonempty_charts_base_free"])
        and bool(rational_result["rank_four_pfaffians_vanish"])
    )
    passed = (
        data.boundary_c_rank == BOUNDARY_C_RANK
        and data.boundary_bordered_rank == BOUNDARY_BORDERED_RANK
        and data.pivot_pfaffian_at_origin != kernel_lemma.ZERO
        and data.schur_skew
        and data.pfaffian_adjugate_identity
        and data.restriction_matches_bordered_form
        and len(data.selected_indices) == int(row["effective_form"]["ambient_linear_rank"])
        and modular_matches
        and rational_matches
        and characteristics_agree
        and one_blowup_resolves
    )
    return {
        "incidence": row["incidence"],
        "source_orbit": row["source_orbit"],
        "boundary_orbit": row["boundary_orbit"],
        "slice_dimension": len(data.slice_names),
        "slice_parameterization": (
            "z(t)=z_0+sum_j t_j e_(slice_column_j) over C; the retained tangent-cone ideal cuts the exceptional "
            "divisor of the ordinary blow-up at t=0"
        ),
        "slice_columns_zero_based": row["slice_columns_zero_based"],
        "tangent_cone": row["tangent_cone"],
        "c_schur_complement": {
            "boundary_c_rank": data.boundary_c_rank,
            "boundary_kernel_dimension": BOUNDARY_C_KERNEL_DIMENSION,
            "boundary_bordered_rank": data.boundary_bordered_rank,
            "complementary_pivot_indices": list(data.pivot_indices),
            "pivot_pfaffian_at_origin": _gaussian_text(data.pivot_pfaffian_at_origin),
            "coordinate_count": len(data.coordinates),
            "independent_leading_coordinate_indices": list(data.selected_indices),
            "independent_leading_coordinate_count": len(data.selected_indices),
            "maximum_total_degree": data.maximum_total_degree,
            "maximum_component_terms": data.maximum_component_terms,
            "coordinate_sha256": data.coordinate_sha256,
            "common_origin_order": data.common_origin_order,
            "schur_numerator_skew": data.schur_skew,
            "pfaffian_adjugate_identity": data.pfaffian_adjugate_identity,
            "exceptional_restriction_matches_bordered_first_order_form": data.restriction_matches_bordered_form,
            "linear_coordinate_matrix": [
                [_gaussian_text(value) for value in coordinate_row] for coordinate_row in data.linear_coordinate_matrix
            ],
        },
        "explicit_blowup": {
            "center": "slice origin",
            "exceptional_power_removed": data.common_origin_order,
            "secondary_blowup_required": not one_blowup_resolves,
            "one_blowup_resolves": one_blowup_resolves,
            "modular_prime": MODULAR_PRIME,
            "modular": modular_result,
            "rational": rational_result,
        },
        "committed_first_order_image": row["first_order_image"],
        "comparison": {
            "expected_affine_dimension_degree_components": list(expected_image),
            "modular_matches_committed_image": modular_matches,
            "rational_matches_committed_image": rational_matches,
            "modular_and_rational_invariants_agree": characteristics_agree,
        },
        "canonical_paths_input": row["canonical_paths"],
        "pass": passed,
    }


def _path_task(item: tuple[str, tuple[tuple[Gaussian, ...], ...], dict[str, Any]]) -> dict[str, Any]:
    incidence, coefficient_matrix, path = item
    direction = tuple(Fraction(value) for value in path["normal_coordinates"])
    values = tuple(
        kernel_lemma._gaussian_sum(
            kernel_lemma._gaussian_scale(coefficient, direction[index])
            for index, coefficient in enumerate(coordinate_row)
        )
        for coordinate_row in coefficient_matrix
    )
    nonzero = any(value != kernel_lemma.ZERO for value in values)
    return {
        "incidence": incidence,
        "approach": path["approach"],
        "exceptional_coordinates": [_gaussian_text(value) for value in values],
        "exceptional_point_defined": nonzero,
        "committed_first_order_plane_matches_retained_limit": path["first_order_plane_matches_retained_limit"],
        "pass": nonzero and path["first_order_plane_matches_retained_limit"] is True,
    }


def _path_inputs(row: dict[str, Any]) -> tuple[tuple[str, tuple[tuple[Gaussian, ...], ...], dict[str, Any]], ...]:
    coefficient_matrix = tuple(
        tuple((Fraction(value[0]), Fraction(value[1])) for value in coordinate_row)
        for coordinate_row in row["c_schur_complement"]["linear_coordinate_matrix"]
    )
    return tuple((str(row["incidence"]), coefficient_matrix, path) for path in row["canonical_paths_input"])


def _analyze_mutation(task: IncidenceTask) -> dict[str, Any]:
    _cap_worker_memory()
    omitted_slice_variable = task.omitted_slice_variable
    _require(omitted_slice_variable is not None, "mutation task needs an omitted slice variable")
    if omitted_slice_variable is None:
        raise RuntimeError("mutation task needs an omitted slice variable")
    data = _schur_polynomials(task)
    tangent_generators = tuple(str(value) for value in task.committed_row["tangent_cone"]["generators"])
    modular_result = _singular_summary(
        _run_singular(_singular_script(MODULAR_PRIME, tangent_generators, data)), data.slice_names
    )
    rational_result = _singular_summary(_run_singular(_singular_script(0, tangent_generators, data)), data.slice_names)
    modular_base_charts = tuple(
        int(row["chart"]) for row in modular_result["charts"] if row["nonempty"] and not row["base_empty"]
    )
    rational_base_charts = tuple(
        int(row["chart"]) for row in rational_result["charts"] if row["nonempty"] and not row["base_empty"]
    )
    modular_detected = modular_result["affine_degeneracy_dimension"] > 0 and bool(modular_base_charts)
    rational_detected = rational_result["affine_degeneracy_dimension"] > 0 and bool(rational_base_charts)
    characteristics_agree = (
        modular_result["affine_degeneracy_dimension"] == rational_result["affine_degeneracy_dimension"]
        and modular_base_charts == rational_base_charts
    )
    detected = modular_detected and rational_detected and characteristics_agree
    return {
        "name": "omit_w8_b9_t2_c_derivative",
        "target": task.committed_row["incidence"],
        "input_change": (
            "delete the t2 coefficient from the holomorphic slice input z(t) before constructing C_z and its "
            "Schur complement"
        ),
        "omitted_slice_variable_one_based": omitted_slice_variable + 1,
        "modular_prime": MODULAR_PRIME,
        "modular_affine_degeneracy_dimension": modular_result["affine_degeneracy_dimension"],
        "modular_nonempty_base_charts": list(modular_base_charts),
        "rational_affine_degeneracy_dimension": rational_result["affine_degeneracy_dimension"],
        "rational_nonempty_base_charts": list(rational_base_charts),
        "modular_and_rational_mutation_outcomes_agree": characteristics_agree,
        "mutated_one_blowup_resolves": bool(rational_result["nonempty_charts_base_free"]),
        "detected": detected,
    }


def _row_pass(row: dict[str, Any]) -> bool:
    return bool(row["pass"])


def _path_pass(row: dict[str, Any]) -> bool:
    return bool(row["pass"])


def _resolved_candidate(row: dict[str, Any]) -> dict[str, Any] | None:
    return row if row["degeneracy_locus"]["one_blowup_resolves_first_order_map"] else None


def _incidence_task(row: dict[str, Any]) -> IncidenceTask:
    return IncidenceTask(row)


def _incidence_name(row: dict[str, Any]) -> str:
    return str(row["incidence"])


def _mutation_candidate(row: dict[str, Any]) -> dict[str, Any] | None:
    return row if row["incidence"] == "W8->B9" else None


def _path_attachment_input(
    row: dict[str, Any],
    *,
    paths_by_incidence: dict[str, list[dict[str, Any]]],
    path_pass_by_incidence: dict[str, bool],
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...], bool]:
    incidence = str(row["incidence"])
    return row, tuple(paths_by_incidence[incidence]), path_pass_by_incidence[incidence]


def _attach_path_checks(
    task: tuple[dict[str, Any], tuple[dict[str, Any], ...], bool],
) -> dict[str, Any]:
    row, path_checks, paths_pass = task
    updated = dict(row)
    updated.pop("canonical_paths_input")
    updated["canonical_path_checks"] = list(path_checks)
    updated["canonical_paths_pass"] = paths_pass
    updated["pass"] = bool(updated["pass"]) and paths_pass
    return updated


def _one_blowup_flag(row: dict[str, Any]) -> bool:
    return bool(row["explicit_blowup"]["one_blowup_resolves"])


def _secondary_blowup_flag(row: dict[str, Any]) -> bool:
    return bool(row["explicit_blowup"]["secondary_blowup_required"])


def _singular_version() -> str:
    process = subprocess.run(
        ["prlimit", f"--as={SINGULAR_MEMORY_LIMIT}", "Singular", "--version"],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    _require(process.returncode == 0, "Singular --version failed")
    return process.stdout.splitlines()[0]


def build_record() -> dict[str, Any]:
    first_order_record = _load_json(FIRST_ORDER_RESULT)
    kernel_lemma_record = _load_json(KERNEL_LEMMA_RESULT)
    _require(first_order_record.get("pass") is True, "committed first-order input does not pass")
    _require(kernel_lemma_record.get("pass") is True, "committed holomorphic-kernel input does not pass")
    resolved_candidates = parallel.ordered_map(
        _resolved_candidate,
        first_order_record["incidences"],
        min_items=1,
    )
    resolved_rows = cast(tuple[dict[str, Any], ...], tuple(filter(None, resolved_candidates)))
    resolved_names = parallel.ordered_map(_incidence_name, resolved_rows, min_items=1)
    _require(tuple(resolved_names) == RESOLVED_INCIDENCES, "resolved incidence set changed")
    incidence_tasks = parallel.ordered_map(_incidence_task, resolved_rows, min_items=1)
    rows = list(parallel.ordered_map(_analyze_incidence, incidence_tasks, min_items=1))

    path_task_groups = parallel.ordered_map(_path_inputs, rows, min_items=1)
    path_tasks = tuple(itertools.chain.from_iterable(path_task_groups))
    path_rows = parallel.ordered_map(_path_task, path_tasks, min_items=1)
    paths_by_incidence: dict[str, list[dict[str, Any]]] = defaultdict(list)
    path_pass_by_incidence: dict[str, bool] = defaultdict(lambda: True)
    for path_row in path_rows:
        incidence = str(path_row["incidence"])
        paths_by_incidence[incidence].append(path_row)
        path_pass_by_incidence[incidence] = path_pass_by_incidence[incidence] and bool(path_row["pass"])
    attachment_inputs = parallel.ordered_map(
        partial(
            _path_attachment_input,
            paths_by_incidence=dict(paths_by_incidence),
            path_pass_by_incidence=dict(path_pass_by_incidence),
        ),
        rows,
        min_items=1,
    )
    rows = list(parallel.ordered_map(_attach_path_checks, attachment_inputs, min_items=1))

    mutation_candidates = parallel.ordered_map(_mutation_candidate, resolved_rows, min_items=1)
    mutation_targets = cast(tuple[dict[str, Any], ...], tuple(filter(None, mutation_candidates)))
    _require(len(mutation_targets) == 1, "W8-to-B9 mutation target is not unique")
    mutation = parallel.ordered_map(
        _analyze_mutation,
        (IncidenceTask(mutation_targets[0], omitted_slice_variable=1),),
        min_items=1,
    )[0]
    pass_flags = parallel.ordered_map(_row_pass, rows, min_items=1)
    path_flags = parallel.ordered_map(_path_pass, path_rows, min_items=1)
    one_blowup_flags = parallel.ordered_map(_one_blowup_flag, rows, min_items=1)
    secondary_blowup_flags = parallel.ordered_map(_secondary_blowup_flag, rows, min_items=1)
    input_rows = parallel.ordered_map(_hash_path, SOURCE_PATHS, min_items=1)
    passed = all(pass_flags) and all(path_flags) and bool(mutation["detected"])
    return {
        "schema": SCHEMA,
        "inputs": dict(input_rows),
        "tools": {"python_flint": flint.__version__, "singular": _singular_version()},
        "scope": {
            "passage": "the eight first-order-resolved nullity-8 to nullity-12 incidences",
            "claim_boundary": (
                "The record identifies the complex-algebraic exceptional fiber of the holomorphic kernel map at "
                "the selected path-supported basepoint. It does not cover the seven higher-order incidences or "
                "variation along a boundary orbit."
            ),
        },
        "summary": {
            "incidence_count": len(rows),
            "one_blowup_resolves_count": sum(one_blowup_flags),
            "secondary_blowup_count": sum(secondary_blowup_flags),
            "canonical_path_count": len(path_rows),
            "modular_prime": MODULAR_PRIME,
        },
        "incidences": rows,
        "mutation_control": mutation,
        "falsifier": (
            "A boundary C_z block has the wrong rank or zero pivot Pfaffian; the Pfaffian-adjugate or Schur-skew "
            "identity fails; the exceptional restriction differs from the bordered first-order form; a nonempty "
            "ordinary-blow-up chart retains a basepoint; a rank-four Pfaffian survives; the modular or rational "
            "fiber dimension, degree, or component count differs from the committed first-order image; a retained "
            "arc has no exceptional image; or deleting the W8-to-B9 t2 derivative leaves the blow-up resolved."
        ),
        "pass": passed,
    }


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _self_test(record: dict[str, Any]) -> None:
    _require(bool(record["pass"]), "the holomorphic Gauss-fiber record failed")
    _require(record["summary"]["incidence_count"] == 8, "resolved incidence count changed")
    _require(record["summary"]["one_blowup_resolves_count"] == 8, "a resolved incidence needs another blow-up")
    _require(record["summary"]["secondary_blowup_count"] == 0, "a secondary blow-up appeared")
    _require(bool(record["mutation_control"]["detected"]), "the C_z derivative mutation survived")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write the deterministic JSON record")
    parser.add_argument("--check", type=Path, help="compare a deterministic record byte for byte")
    parser.add_argument("--self-test", action="store_true", help="run the baseline and mutation checks")
    arguments = parser.parse_args()
    selected_modes = sum((arguments.out is not None, arguments.check is not None, arguments.self_test))
    if selected_modes != 1:
        parser.error("select exactly one of --out, --check, or --self-test")
    record = build_record()
    _self_test(record)
    rendered = _record_bytes(record)
    if arguments.out is not None:
        arguments.out.write_bytes(rendered)
    elif arguments.check is not None:
        retained = arguments.check.read_bytes()
        _require(
            retained == rendered,
            f"record mismatch: retained={hashlib.sha256(retained).hexdigest()} "
            f"fresh={hashlib.sha256(rendered).hexdigest()}",
        )


if __name__ == "__main__":
    main()
