"""Exact nullity-eight kernel limits inside adjacent nullity-twelve kernels."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from pathlib import Path
from typing import Any, TypeAlias, cast

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KERNEL_BUNDLES = HERE.parent / "a5-kernel-bundles"
REGULARITY = HERE.parent / "a5-strata-regularity"
EQUATIONS = HERE.parent / "a5-rank-strata-equations"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(KERNEL_BUNDLES))
sys.path.insert(0, str(REGULARITY))
sys.path.insert(0, str(EQUATIONS))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import aligned_orbit_moduli as aligned  # noqa: E402
import aligned_stabilizer_representation as aligned_representation  # noqa: E402
import kernel_frames  # noqa: E402
import kernel_symmetry as symmetry  # noqa: E402
import stabilizer_representation as stabilizer  # noqa: E402
import strata_regularity as regularity  # noqa: E402
import verify_regularity_independent as independent  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-bundles-nullity8-boundary-specializations-v1"
MATRIX_DIMENSION = 16
BOUNDARY_MATRIX_RANK = 10
BOUNDARY_KERNEL_DIMENSION = 6
LIMITING_KERNEL_DIMENSION = 4
QUOTIENT_DIMENSION = 2
COMPACT_GENERATOR_COUNT = 15

INCIDENCES = {
    "W8": ("B9", "VB"),
    "E8bar": ("B9", "V", "VB", "Va+", "Va-"),
    "Iso": ("B9", "VB"),
    "X+": ("B9", "VB", "Va+"),
    "X-": ("B9", "VB", "Va-"),
}
SOURCE_PATHS = (
    HERE / "boundary_specializations.py",
    KERNEL_BUNDLES / "kernel_frames.py",
    KERNEL_BUNDLES / "kernel_symmetry.py",
    KERNEL_BUNDLES / "stabilizer_representation.py",
    KERNEL_BUNDLES / "aligned_orbit_moduli.py",
    KERNEL_BUNDLES / "aligned_stabilizer_representation.py",
    REGULARITY / "strata_regularity.py",
    REGULARITY / "verify_regularity_independent.py",
)

RationalVector: TypeAlias = tuple[Fraction, ...]
RationalMatrix: TypeAlias = tuple[tuple[Fraction, ...], ...]


@dataclass(frozen=True)
class PathSpec:
    high_orbit: str
    boundary_orbit: str
    approach: str
    coefficients: tuple[RationalVector, RationalVector, RationalVector]

    @property
    def incidence(self) -> str:
        return f"{self.high_orbit}->{self.boundary_orbit}"


@dataclass(frozen=True)
class PathAnalysis:
    path: PathSpec
    row: dict[str, Any]
    limiting_plane: sp.Matrix
    quotient_frame: sp.Matrix
    boundary_kernel: sp.Matrix


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zero_vector(dimension: int = 15) -> RationalVector:
    return tuple(Fraction(0) for _index in range(dimension))


def _vector(*entries: int | Fraction) -> RationalVector:
    return tuple(Fraction(entry) for entry in entries)


def _scaled_vector(scale: int | Fraction, vector: Sequence[Fraction]) -> RationalVector:
    return tuple(Fraction(scale) * value for value in vector)


def _sum_vectors(*vectors: Sequence[Fraction]) -> RationalVector:
    return tuple(sum((vector[index] for vector in vectors), Fraction(0)) for index in range(len(vectors[0])))


def _difference(first: Sequence[Fraction], second: Sequence[Fraction]) -> RationalVector:
    return tuple(left - right for left, right in zip(first, second, strict=True))


def _split_point(first: Sequence[Fraction], middle: int | Fraction, second: Sequence[Fraction]) -> RationalVector:
    return tuple([*first, Fraction(middle), *second])


def _sum_difference_point(
    sum_vector: Sequence[Fraction], difference_vector: Sequence[Fraction], middle: int | Fraction = 0
) -> RationalVector:
    half = Fraction(1, 2)
    first = tuple(
        half * (sum_value + difference_value)
        for sum_value, difference_value in zip(sum_vector, difference_vector, strict=True)
    )
    second = tuple(
        half * (sum_value - difference_value)
        for sum_value, difference_value in zip(sum_vector, difference_vector, strict=True)
    )
    return _split_point(first, middle, second)


def _linear_path(high_orbit: str, boundary_orbit: str, approach: str, direction: Sequence[Fraction]) -> PathSpec:
    boundary = tuple(independent.REPS[boundary_orbit])
    return PathSpec(high_orbit, boundary_orbit, approach, (boundary, tuple(direction), _zero_vector()))


def _slice_path(
    high_orbit: str,
    boundary_orbit: str,
    approach: str,
    slice_name: str,
    boundary_parameters: Sequence[int],
    high_parameters: Sequence[int],
) -> PathSpec:
    boundary = tuple(independent.slice_point(slice_name, tuple(Fraction(value) for value in boundary_parameters)))
    high = tuple(independent.slice_point(slice_name, tuple(Fraction(value) for value in high_parameters)))
    return PathSpec(high_orbit, boundary_orbit, approach, (boundary, _difference(high, boundary), _zero_vector()))


def _w8_paths() -> list[PathSpec]:
    directions = []
    for second_sign in (-1, 1):
        direction = [Fraction(0)] * 15
        direction[1] = Fraction(-1)
        direction[12] = Fraction(second_sign)
        directions.append(tuple(direction))
    return [
        _linear_path("W8", boundary, f"opposite-null-directions-{index + 1}", direction)
        for boundary in ("B9", "VB")
        for index, direction in enumerate(directions)
    ]


def _e8_b9_paths() -> list[PathSpec]:
    boundary = tuple(independent.REPS["B9"])
    boundary_sum = _sum_vectors(boundary[:7], boundary[8:])
    boundary_difference = _difference(boundary[:7], boundary[8:])
    directions = (
        (
            _vector(-1, 5, -1, -1, 5, -1, -1),
            _vector(1, Fraction(-11, 3), 1, 1, Fraction(-11, 3), 1, 1),
        ),
        (
            _vector(-1, -5, -1, -1, -5, -1, 1),
            _vector(1, Fraction(11, 3), 1, 1, Fraction(11, 3), 1, -1),
        ),
    )
    paths = []
    for index, (sum_direction, difference_direction) in enumerate(directions):
        first_order = _difference(
            _sum_difference_point(
                _sum_vectors(boundary_sum, sum_direction),
                _sum_vectors(boundary_difference, difference_direction),
                1,
            ),
            boundary,
        )
        paths.append(
            PathSpec(
                "E8bar",
                "B9",
                f"rank-three-cone-line-{index + 1}",
                (boundary, first_order, _zero_vector()),
            )
        )
    return paths


def _e8_slice_paths() -> list[PathSpec]:
    return [
        _slice_path("E8bar", "V", "transverse-line-1", "P3a", (0, 0, -2, -2, -2), (-2, 0, -2, -2, -2)),
        _slice_path("E8bar", "V", "transverse-line-2", "P3a", (0, 0, -2, -2, -2), (-2, 0, -2, 1, 1)),
        _slice_path("E8bar", "VB", "transverse-line-1", "P3a", (-2, 0, -1, 0, 0), (-2, 0, -2, -2, -2)),
        _slice_path("E8bar", "VB", "transverse-line-2", "P3a", (-2, 0, -1, 0, 0), (-2, 0, -2, -2, 2)),
    ]


def _e8_aligned_paths(boundary_orbit: str) -> list[PathSpec]:
    associative_null = tuple(independent.A_VEC)
    first_basis = tuple(independent.e(1))
    if boundary_orbit == "Va+":
        boundary_first = _sum_vectors(associative_null, first_basis)
        boundary_second = boundary_first
        second_order = _split_point(_scaled_vector(-1, first_basis), 0, first_basis)
    elif boundary_orbit == "Va-":
        boundary_first = _sum_vectors(associative_null, _scaled_vector(-1, first_basis))
        boundary_second = _sum_vectors(_scaled_vector(-1, associative_null), first_basis)
        second_order = _split_point(first_basis, 0, first_basis)
    else:
        raise ValueError(f"unknown aligned boundary {boundary_orbit!r}")
    boundary = _split_point(boundary_first, 0, boundary_second)
    return [
        PathSpec(
            "E8bar",
            boundary_orbit,
            f"middle-coordinate-sheet-{sheet_sign:+d}",
            (boundary, _split_point(_zero_vector(7), 2 * sheet_sign, _zero_vector(7)), second_order),
        )
        for sheet_sign in (-1, 1)
    ]


def _iso_paths() -> list[PathSpec]:
    b9_directions = []
    for fifth_sign in (-1, 1):
        direction = [Fraction(0)] * 15
        direction[1] = Fraction(-1)
        direction[4] = Fraction(fifth_sign)
        b9_directions.append(tuple(direction))
    return [
        *[
            _linear_path("Iso", "B9", f"isotropic-three-plane-{index + 1}", direction)
            for index, direction in enumerate(b9_directions)
        ],
        _slice_path("Iso", "VB", "isotropic-line-1", "P4g", (-2, -2, -1, -1, 0), (-2, -2, -2, -1, 0)),
        _slice_path("Iso", "VB", "isotropic-line-2", "P4g", (-2, -2, -1, -1, 0), (-2, -2, -2, 0, 0)),
    ]


def _x_b9_paths(high_orbit: str) -> list[PathSpec]:
    boundary = tuple(independent.REPS["B9"])
    boundary_sum = _sum_vectors(boundary[:7], boundary[8:])
    boundary_difference = _difference(boundary[:7], boundary[8:])
    if high_orbit == "X+":
        variables = (_vector(0, 13, 0, 0, 12, 0, 0), _vector(0, -13, 0, 0, -12, 0, 0))
        points = [_sum_difference_point(variable, boundary_difference) for variable in variables]
    elif high_orbit == "X-":
        variables = (_vector(0, 65, 0, 0, 56, 0, 0), _vector(0, -65, 0, 0, -56, 0, 0))
        points = [_sum_difference_point(boundary_sum, variable) for variable in variables]
    else:
        raise ValueError(f"unknown X branch {high_orbit!r}")
    return [
        PathSpec(
            high_orbit,
            "B9",
            f"fixed-null-fiber-{index + 1}",
            (boundary, _difference(point, boundary), _zero_vector()),
        )
        for index, point in enumerate(points)
    ]


def _x_vb_paths(high_orbit: str) -> list[PathSpec]:
    boundary_parameters = (-2, 0, -1, 0, 0)
    high_parameters = {
        "X+": ((-2, -2, -1, -2, 0), (-2, -2, 0, -2, 0)),
        "X-": ((-2, -2, -2, 2, 0), (-2, -2, -1, 2, 0)),
    }[high_orbit]
    return [
        _slice_path(high_orbit, "VB", f"null-fiber-line-{index + 1}", "P3a", boundary_parameters, parameters)
        for index, parameters in enumerate(high_parameters)
    ]


def _x_aligned_paths(high_orbit: str) -> list[PathSpec]:
    first_basis = tuple(independent.e(1))
    null_directions = (
        tuple(independent.A_VEC),
        tuple(independent.vadd((1, independent.e(4)), (1, independent.e(5)))),
    )
    if high_orbit == "X+":
        boundary_orbit = "Va+"
        boundary = _split_point(first_basis, 0, first_basis)
        directions = [
            _split_point(null_direction, 0, _scaled_vector(-1, null_direction)) for null_direction in null_directions
        ]
    elif high_orbit == "X-":
        boundary_orbit = "Va-"
        boundary = _split_point(first_basis, 0, _scaled_vector(-1, first_basis))
        directions = [_split_point(null_direction, 0, null_direction) for null_direction in null_directions]
    else:
        raise ValueError(f"unknown X branch {high_orbit!r}")
    return [
        PathSpec(
            high_orbit,
            boundary_orbit,
            f"null-eigenline-{index + 1}",
            (boundary, direction, _zero_vector()),
        )
        for index, direction in enumerate(directions)
    ]


def _boundary_moved_paths() -> list[PathSpec]:
    zero = _zero_vector()
    return [
        PathSpec(
            "E8bar",
            "V",
            "boundary-stabilizer-unipotent-21",
            (
                _vector(0, 0, 0, 0, 0, 0, 0, -2, -2, -2, -2, 0, 0, 0, 0),
                _vector(0, -2, -2, 2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                zero,
            ),
        ),
        PathSpec(
            "E8bar",
            "Va+",
            "boundary-stabilizer-unipotent-21",
            (
                _vector(1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0),
                _vector(0, 0, 0, 0, 0, 0, 0, -2, 0, 0, 0, 0, 0, 0, 0),
                _vector(-1, 0, 0, -1, 0, -1, 0, 0, 1, 0, 0, 1, 0, 1, 0),
            ),
        ),
        PathSpec(
            "E8bar",
            "Va-",
            "boundary-stabilizer-unipotent-20",
            (
                _vector(-1, 1, 1, 0, 0, 0, 0, 0, 1, -1, -1, 0, 0, 0, 0),
                _vector(0, 0, 0, 0, 0, 0, 0, -2, 0, 0, 0, 0, 0, 0, 0),
                _vector(1, 0, 0, -1, 0, 1, 0, 0, 1, 0, 0, -1, 0, 1, 0),
            ),
        ),
        PathSpec(
            "W8",
            "VB",
            "boundary-stabilizer-unipotent-18",
            (
                _vector(1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                _vector(1, -1, 1, 0, 0, 0, 0, 0, 0, 0, 0, -1, Fraction(-3, 2), 0, Fraction(-1, 2)),
                zero,
            ),
        ),
        PathSpec(
            "Iso",
            "VB",
            "boundary-stabilizer-null-basis-3",
            (
                _vector(-2, -2, -2, 0, -2, 0, 0, 0, -1, -1, -1, 0, -1, 0, 0),
                _vector(0, 0, 0, 0, 0, 0, 0, 0, -1, 2, -2, -2, 3, 0, 2),
                zero,
            ),
        ),
        PathSpec(
            "X+",
            "VB",
            "boundary-stabilizer-unipotent-22",
            (
                _vector(0, -2, -2, 0, 0, 0, 0, 0, 0, -1, -1, 0, 0, 0, 0),
                _vector(-2, 0, 0, 0, 0, -2, -2, 0, -2, 0, 0, 0, 0, -2, -2),
                zero,
            ),
        ),
        PathSpec(
            "X-",
            "VB",
            "boundary-stabilizer-unipotent-22",
            (
                _vector(0, -2, -2, 0, 0, 0, 0, 0, 0, -1, -1, 0, 0, 0, 0),
                _vector(-2, 0, 0, 0, 0, -2, -2, 0, 2, -1, -1, 0, 0, 2, 2),
                zero,
            ),
        ),
    ]


def _path_specs() -> list[PathSpec]:
    paths = [
        *_w8_paths(),
        *_e8_b9_paths(),
        *_e8_slice_paths(),
        *_e8_aligned_paths("Va+"),
        *_e8_aligned_paths("Va-"),
        *_iso_paths(),
        *_x_b9_paths("X+"),
        *_x_vb_paths("X+"),
        *_x_aligned_paths("X+"),
        *_x_b9_paths("X-"),
        *_x_vb_paths("X-"),
        *_x_aligned_paths("X-"),
    ]
    replacements = {"W8->VB", "Iso->VB", "X+->VB", "X-->VB"}
    paths = [
        path
        for path in paths
        if not (path.incidence in replacements and path.approach.endswith("line-2"))
        and not (path.incidence == "W8->VB" and path.approach == "opposite-null-directions-2")
    ]
    paths.extend(_boundary_moved_paths())
    expected = {f"{high}->{boundary}" for high, boundaries in INCIDENCES.items() for boundary in boundaries}
    observed = {path.incidence for path in paths}
    _require(observed == expected, "path table does not cover the declared incidences")
    _require(
        all(sum(path.incidence == incidence for path in paths) >= 2 for incidence in expected),
        "each incidence needs at least two approaches",
    )
    return sorted(paths, key=lambda path: (path.incidence, path.approach))


def _path_degree(path: PathSpec) -> int:
    return 2 if any(path.coefficients[2]) else 1


def _evaluate_path(path: PathSpec, parameter: int | Fraction) -> RationalVector:
    value = Fraction(parameter)
    return tuple(
        path.coefficients[0][index] + value * path.coefficients[1][index] + value * value * path.coefficients[2][index]
        for index in range(15)
    )


def _curve_certificate(path: PathSpec) -> dict[str, Any]:
    generators = independent.GENS[path.high_orbit]
    generator_degree = max(int(generator.total_degree()) for generator in generators)
    substituted_degree_bound = generator_degree * _path_degree(path)
    samples = tuple(range(substituted_degree_bound + 1))
    containment = all(
        generator(
            *(independent.flint.fmpq(value.numerator, value.denominator) for value in _evaluate_path(path, parameter))
        )
        == 0
        for generator in generators
        for parameter in samples
    )
    boundary = _evaluate_path(path, 0)
    boundary_pattern = independent.pattern(boundary)
    expected_boundary_pattern = independent.pattern(independent.REPS[path.boundary_orbit])
    open_samples = [_evaluate_path(path, parameter) for parameter in (1, 2, 3)]
    expected_open_pattern = independent.pattern(independent.REPS[path.high_orbit])
    open_patterns = [independent.pattern(point) for point in open_samples]
    nullities = [independent.nullity_ly(boundary), *(independent.nullity_ly(point) for point in open_samples)]
    return {
        "path_degree": _path_degree(path),
        "closure_generator_max_degree": generator_degree,
        "substituted_degree_bound": substituted_degree_bound,
        "containment_sample_parameters": list(samples),
        "closure_containment_proved": containment,
        "containment_argument": (
            "each substituted generator has degree at most the recorded bound and vanishes at one more distinct "
            "rational parameter"
        ),
        "boundary_pattern": boundary_pattern,
        "expected_boundary_pattern": expected_boundary_pattern,
        "boundary_orbit_verified": boundary_pattern == expected_boundary_pattern,
        "open_sample_parameters": [1, 2, 3],
        "open_patterns": open_patterns,
        "expected_open_pattern": expected_open_pattern,
        "open_orbit_samples_verified": all(pattern == expected_open_pattern for pattern in open_patterns),
        "left_nullities_at_0_1_2_3": nullities,
        "nullity_jump_verified": nullities == [12, 8, 8, 8],
        "pass": containment
        and boundary_pattern == expected_boundary_pattern
        and all(pattern == expected_open_pattern for pattern in open_patterns)
        and nullities == [12, 8, 8, 8],
    }


@cache
def _matrix_for_split(split_point: Sequence[Fraction | sp.Expr]) -> sp.Matrix:
    # _original_z_from_split is annotated for integers but substitutes any exact scalar, sympy expressions included.
    return kernel_frames._bordered_matrix(kernel_frames._original_z_from_split(cast("Sequence[int]", split_point)))


def _standard_columns(indices: Sequence[int]) -> sp.Matrix:
    matrix = sp.zeros(MATRIX_DIMENSION, len(indices))
    for column, row in enumerate(indices):
        matrix[row, column] = 1
    return matrix


def _quotient_coordinates(limit_coordinates: sp.Matrix) -> sp.Matrix:
    columns = [limit_coordinates[:, column] for column in range(limit_coordinates.cols)]
    rank = limit_coordinates.rank()
    quotient_columns = []
    for index in range(BOUNDARY_KERNEL_DIMENSION):
        candidate = sp.eye(BOUNDARY_KERNEL_DIMENSION)[:, index]
        candidate_rank = sp.Matrix.hstack(*columns, candidate).rank()
        if candidate_rank > rank:
            columns.append(candidate)
            quotient_columns.append(candidate)
            rank = candidate_rank
        if rank == BOUNDARY_KERNEL_DIMENSION:
            break
    _require(len(quotient_columns) == QUOTIENT_DIMENSION, "failed to construct the two-dimensional quotient")
    return sp.Matrix.hstack(*quotient_columns)


def _matrix_rows(matrix: sp.Matrix) -> list[list[str]]:
    return [[sp.sstr(matrix[row, column]) for column in range(matrix.cols)] for row in range(matrix.rows)]


@cache
def _boundary_frame_data(
    split_point: RationalVector,
) -> tuple[sp.Matrix, tuple[int, ...], sp.Matrix, sp.Expr, sp.Expr, sp.Matrix, sp.Matrix]:
    boundary_matrix = _matrix_for_split(split_point)
    pivot = kernel_frames._find_principal_pivot(boundary_matrix, BOUNDARY_MATRIX_RANK)
    boundary_frame, pivot_determinant, pivot_pfaffian = kernel_frames._principal_frame(boundary_matrix, pivot)
    return (
        boundary_matrix,
        pivot,
        boundary_frame,
        pivot_determinant,
        pivot_pfaffian,
        _standard_columns(pivot),
        boundary_matrix.extract(pivot, pivot),
    )


def _kernel_limit(
    path: PathSpec, drop_schur_correction: bool = False
) -> tuple[dict[str, Any], sp.Matrix, sp.Matrix, sp.Matrix]:
    first_matrix = _matrix_for_split(path.coefficients[1])
    second_matrix = _matrix_for_split(path.coefficients[2])
    (
        boundary_matrix,
        pivot,
        boundary_frame,
        pivot_determinant,
        pivot_pfaffian,
        pivot_columns,
        pivot_block,
    ) = _boundary_frame_data(path.coefficients[0])
    boundary_rank = boundary_matrix.rank()
    first_restriction = sp.simplify(boundary_frame.T * first_matrix * boundary_frame)
    first_rank = first_restriction.rank()
    if first_rank == 2:
        leading_order = 1
        effective = first_restriction
    elif first_rank == 0:
        leading_order = 2
        first_coupling = first_matrix.extract(pivot, range(MATRIX_DIMENSION)) * boundary_frame
        second_restriction = sp.simplify(boundary_frame.T * second_matrix * boundary_frame)
        schur_correction = sp.simplify(first_coupling.T * pivot_block.inv() * first_coupling)
        effective = second_restriction if drop_schur_correction else sp.simplify(second_restriction + schur_correction)
    else:
        raise RuntimeError(f"unexpected first restricted rank {first_rank} on {path.incidence} {path.approach}")
    effective_rank = effective.rank()
    effective_skew = sp.simplify(effective.T + effective) == sp.zeros(BOUNDARY_KERNEL_DIMENSION)
    nullspace = effective.nullspace()
    limit_coordinates = sp.Matrix.hstack(*nullspace) if nullspace else sp.zeros(BOUNDARY_KERNEL_DIMENSION, 0)
    limiting_plane = boundary_frame * limit_coordinates
    quotient_coordinates = _quotient_coordinates(limit_coordinates) if effective_rank == 2 else sp.zeros(6, 0)
    quotient_frame = boundary_frame * quotient_coordinates
    full_frame = sp.Matrix.hstack(limiting_plane, quotient_frame)
    correction_verified = False
    if effective_rank == 2:
        first_coupling = first_matrix.extract(pivot, range(MATRIX_DIMENSION)) * boundary_frame
        first_correction = -pivot_columns * pivot_block.inv() * first_coupling * limit_coordinates
        first_residual = sp.simplify(boundary_matrix * first_correction + first_matrix * limiting_plane)
        correction_verified = first_residual == sp.zeros(MATRIX_DIMENSION, LIMITING_KERNEL_DIMENSION)
        if leading_order == 2:
            second_residual = sp.simplify(first_matrix * first_correction + second_matrix * limiting_plane)
            correction_verified = correction_verified and sp.simplify(boundary_frame.T * second_residual) == sp.zeros(
                BOUNDARY_KERNEL_DIMENSION, LIMITING_KERNEL_DIMENSION
            )
    plane_rank = limiting_plane.rank()
    quotient_rank = quotient_frame.rank()
    plane_inside = boundary_matrix * limiting_plane == sp.zeros(MATRIX_DIMENSION, LIMITING_KERNEL_DIMENSION)
    boundary_split = full_frame.rank() == BOUNDARY_KERNEL_DIMENSION
    row_pass = (
        boundary_rank == BOUNDARY_MATRIX_RANK
        and pivot_determinant == pivot_pfaffian * pivot_pfaffian
        and effective_skew
        and effective_rank == 2
        and plane_rank == LIMITING_KERNEL_DIMENSION
        and plane_inside
        and quotient_rank == QUOTIENT_DIMENSION
        and boundary_split
        and boundary_matrix * full_frame == sp.zeros(MATRIX_DIMENSION, BOUNDARY_KERNEL_DIMENSION)
        and correction_verified
    )
    return (
        {
            "boundary_bordered_rank": boundary_rank,
            "boundary_pivot_indices": list(pivot),
            "boundary_pivot_pfaffian": sp.sstr(pivot_pfaffian),
            "boundary_pivot_determinant": sp.sstr(pivot_determinant),
            "first_restricted_rank": first_rank,
            "effective_leading_order": leading_order,
            "effective_restricted_rank": effective_rank,
            "effective_restriction_skew": effective_skew,
            "limiting_plane_dimension": plane_rank,
            "limiting_plane_inside_boundary_kernel": plane_inside,
            "quotient_dimension": quotient_rank,
            "boundary_kernel_split_verified": boundary_split,
            "formal_lift_solvability_verified": correction_verified,
            "limiting_plane_rref": _matrix_rows(limiting_plane.T.rref()[0]),
            "quotient_frame_rref": _matrix_rows(quotient_frame.T.rref()[0]),
            "pass": row_pass,
        },
        limiting_plane,
        quotient_frame,
        boundary_frame,
    )


def _fraction(value: sp.Expr) -> Fraction:
    rational = sp.Rational(value)
    return Fraction(int(rational.p), int(rational.q))


def _adapted_real_basis(complex_frame: sp.Matrix) -> tuple[tuple[Fraction, ...], ...]:
    real_frame = kernel_frames._real_kernel_frame(complex_frame)
    transported_columns = tuple(
        tuple(_fraction(real_frame[row, column]) for row in range(real_frame.rows)) for column in range(real_frame.cols)
    )
    complex_structure = aligned_representation._complex_structure()
    adapted: list[tuple[Fraction, ...]] = []
    for index in range(0, len(transported_columns), 2):
        first = transported_columns[index]
        second = transported_columns[index + 1]
        image = stabilizer._matrix_vector(complex_structure, first)
        if image == second:
            adapted.extend((first, second))
        elif image == tuple(-value for value in second):
            adapted.extend((first, tuple(-value for value in second)))
        else:
            raise RuntimeError("transported complex frame pair is not invariant under J")
    return tuple(adapted)


def _path_stabilizer_coefficients(path: PathSpec) -> tuple[tuple[Fraction, ...], ...]:
    compact = stabilizer._compact_triples()
    real_coefficients = [tuple(symmetry.equations.y_from_split(coefficient)) for coefficient in path.coefficients]
    tangent_rows: list[list[Fraction]] = []
    for real_coefficient in real_coefficients:
        tangent_columns = [stabilizer._matrix_vector(triple[0], real_coefficient) for _name, triple in compact]
        tangent_rows.extend(
            [tangent_columns[column][row] for column in range(COMPACT_GENERATOR_COUNT)] for row in range(32)
        )
    return tuple(tuple(row) for row in symmetry.equations.nullspace(tangent_rows))


def _combine_coefficients(
    combination: Sequence[Fraction], coefficient_rows: Sequence[Sequence[Fraction]]
) -> tuple[Fraction, ...]:
    return tuple(
        sum(
            (coefficient * coefficient_rows[index][column] for index, coefficient in enumerate(combination)),
            Fraction(0),
        )
        for column in range(COMPACT_GENERATOR_COUNT)
    )


def _primitive_global_coefficients(values: Sequence[Fraction]) -> tuple[Fraction, ...]:
    return tuple(Fraction(value) for value in stabilizer._primitive_integer_vector(values))


def _casimir(derived_domains: Sequence[RationalMatrix], represented: Sequence[sp.Matrix]) -> sp.Matrix:
    inverse = stabilizer._killing_matrix(derived_domains).inv()
    casimir = sp.zeros(represented[0].rows)
    for row, left in enumerate(represented):
        for column, right in enumerate(represented):
            casimir += inverse[row, column] * left * right
    return sp.simplify(casimir)


def _highest_weight(casimir_eigenvalue: sp.Expr, maximum: int) -> int:
    for highest_weight in range(maximum + 1):
        if sp.simplify(casimir_eigenvalue - sp.Rational(highest_weight * (highest_weight + 2), 8)) == 0:
            return highest_weight
    raise ArithmeticError(f"unrecognized su(2) Casimir eigenvalue {casimir_eigenvalue}")


def _decomposition(
    algebra: str,
    dimension: int,
    center: sp.Matrix | None,
    casimir: sp.Matrix | None,
) -> dict[str, Any]:
    if algebra == "zero":
        rows = [{"highest_weight": 0, "multiplicity": dimension, "joint_dimension": dimension}]
        label = f"{dimension} V_0"
    elif algebra == "u(1)":
        if center is None:
            raise RuntimeError("u(1) decomposition needs its center")
        rows = [
            {"central_weight": sp.sstr(weight), "multiplicity": multiplicity, "joint_dimension": multiplicity}
            for weight, multiplicity in sorted(
                center.eigenvals().items(), key=lambda item: sp.default_sort_key(item[0])
            )
        ]
        label = " + ".join(f"{row['multiplicity']} C_({row['central_weight']})" for row in rows)
    elif algebra == "su(2)":
        if casimir is None:
            raise RuntimeError("su(2) decomposition needs its Casimir")
        rows = []
        for eigenvalue, joint_dimension in sorted(
            casimir.eigenvals().items(), key=lambda item: sp.default_sort_key(item[0])
        ):
            highest_weight = _highest_weight(eigenvalue, dimension)
            irreducible_dimension = highest_weight + 1
            _require(
                joint_dimension % irreducible_dimension == 0,
                "Casimir eigenspace has a fractional multiplicity",
            )
            rows.append(
                {
                    "highest_weight": highest_weight,
                    "multiplicity": joint_dimension // irreducible_dimension,
                    "joint_dimension": joint_dimension,
                    "casimir_eigenvalue": sp.sstr(eigenvalue),
                }
            )
        label = " + ".join(
            f"{row['multiplicity']} V_{row['highest_weight']}"
            if row["multiplicity"] != 1
            else f"V_{row['highest_weight']}"
            for row in rows
        )
    elif algebra == "su(2)+u(1)":
        if center is None or casimir is None:
            raise RuntimeError("u(2) decomposition needs center and Casimir")
        rows = []
        identity = sp.eye(dimension)
        for central_weight in center.eigenvals():
            for casimir_value in casimir.eigenvals():
                joint_dimension = len(
                    sp.Matrix.vstack(
                        center - central_weight * identity,
                        casimir - casimir_value * identity,
                    ).nullspace()
                )
                if not joint_dimension:
                    continue
                highest_weight = _highest_weight(casimir_value, dimension)
                irreducible_dimension = highest_weight + 1
                _require(
                    joint_dimension % irreducible_dimension == 0,
                    "joint eigenspace has a fractional multiplicity",
                )
                rows.append(
                    {
                        "central_weight": sp.sstr(central_weight),
                        "highest_weight": highest_weight,
                        "multiplicity": joint_dimension // irreducible_dimension,
                        "joint_dimension": joint_dimension,
                        "casimir_eigenvalue": sp.sstr(casimir_value),
                    }
                )
        rows.sort(key=lambda row: (row["central_weight"], row["highest_weight"]))
        label = " + ".join(f"{row['multiplicity']} V_({row['highest_weight']},{row['central_weight']})" for row in rows)
    else:
        raise RuntimeError(f"unsupported preserved stabilizer algebra {algebra!r}")
    return {"decomposition": label, "irreducibles": rows, "dimension": dimension}


def _decomposition_counts(decomposition: dict[str, Any]) -> dict[tuple[Any, ...], int]:
    counts: dict[tuple[Any, ...], int] = {}
    for row in decomposition["irreducibles"]:
        key = tuple((name, row[name]) for name in sorted(row) if name not in ("multiplicity", "joint_dimension"))
        counts[key] = counts.get(key, 0) + int(row["multiplicity"])
    return counts


def _representation_certificate(
    path: PathSpec,
    limiting_plane: sp.Matrix,
    quotient_frame: sp.Matrix,
) -> dict[str, Any]:
    compact = stabilizer._compact_triples()
    coefficients = _path_stabilizer_coefficients(path)
    base_generators = [triple[0] for _name, triple in compact]
    domain_generators = [triple[1] for _name, triple in compact]
    base_stabilizers = tuple(stabilizer._linear_combination(row, base_generators) for row in coefficients)
    domain_stabilizers = tuple(stabilizer._linear_combination(row, domain_generators) for row in coefficients)
    real_path_coefficients = [tuple(symmetry.equations.y_from_split(row)) for row in path.coefficients]
    path_fixed = all(
        not any(stabilizer._matrix_vector(base, coefficient))
        for base in base_stabilizers
        for coefficient in real_path_coefficients
    )
    full_complex_frame = sp.Matrix.hstack(limiting_plane, quotient_frame)
    full_adapted = _adapted_real_basis(full_complex_frame)
    complex_structure = aligned_representation._complex_structure()

    def represented(domain: RationalMatrix) -> sp.Matrix:
        return aligned_representation._fiber_matrix(domain, full_adapted, complex_structure)

    full_representations = [represented(domain) for domain in domain_stabilizers]
    limiting_invariant = all(
        matrix[LIMITING_KERNEL_DIMENSION:, :LIMITING_KERNEL_DIMENSION]
        == sp.zeros(QUOTIENT_DIMENSION, LIMITING_KERNEL_DIMENSION)
        for matrix in full_representations
    )
    commutators_match = aligned_representation._representation_commutators_match(
        domain_stabilizers,
        full_representations,
        full_adapted,
        complex_structure,
    )
    stabilizer_dimension = len(coefficients)
    if stabilizer_dimension == 0:
        algebra = "zero"
        center_dimension = 0
        derived_domains: tuple[RationalMatrix, ...] = ()
        compact_semisimple = True
    else:
        center_dimension = aligned._center_dimension(domain_stabilizers)
        derived_domains = aligned_representation._derived_basis(domain_stabilizers)
        killing = stabilizer._killing_matrix(derived_domains) if derived_domains else sp.zeros(0)
        compact_semisimple = aligned._negative_definite(killing) if derived_domains else True
        if stabilizer_dimension == 1 and center_dimension == 1 and not derived_domains:
            algebra = "u(1)"
        else:
            algebra = aligned._lie_algebra_label(
                stabilizer_dimension,
                center_dimension,
                len(derived_domains),
                compact_semisimple,
            )
    center_full = None
    center_global_coefficients: tuple[Fraction, ...] | None = None
    if algebra == "u(1)":
        center_global_coefficients = _primitive_global_coefficients(coefficients[0])
        center_domain = stabilizer._linear_combination(center_global_coefficients, domain_generators)
        center_full = represented(center_domain)
    elif algebra == "su(2)+u(1)":
        local_center = stabilizer._center_coefficients(domain_stabilizers)
        center_global_coefficients = _primitive_global_coefficients(_combine_coefficients(local_center, coefficients))
        center_domain = stabilizer._linear_combination(center_global_coefficients, domain_generators)
        center_full = represented(center_domain)
    casimir_full = None
    if derived_domains:
        casimir_full = _casimir(derived_domains, [represented(domain) for domain in derived_domains])
    limiting_decomposition = _decomposition(
        algebra,
        LIMITING_KERNEL_DIMENSION,
        center_full[:4, :4] if center_full is not None else None,
        casimir_full[:4, :4] if casimir_full is not None else None,
    )
    quotient_decomposition = _decomposition(
        algebra,
        QUOTIENT_DIMENSION,
        center_full[4:, 4:] if center_full is not None else None,
        casimir_full[4:, 4:] if casimir_full is not None else None,
    )
    boundary_decomposition = _decomposition(
        algebra,
        BOUNDARY_KERNEL_DIMENSION,
        center_full,
        casimir_full,
    )
    combined_counts = _decomposition_counts(limiting_decomposition)
    for key, multiplicity in _decomposition_counts(quotient_decomposition).items():
        combined_counts[key] = combined_counts.get(key, 0) + multiplicity
    representation_sum_matches = combined_counts == _decomposition_counts(boundary_decomposition)
    return {
        "preserved_stabilizer_dimension": stabilizer_dimension,
        "preserved_stabilizer_lie_algebra": algebra,
        "stabilizer_center_dimension": center_dimension,
        "stabilizer_derived_dimension": len(derived_domains),
        "derived_killing_negative_definite": compact_semisimple,
        "global_generator_coefficients": [[str(value) for value in row] for row in coefficients],
        "primitive_center_global_coefficients": (
            [str(value) for value in center_global_coefficients] if center_global_coefficients is not None else None
        ),
        "path_coefficients_fixed": path_fixed,
        "limiting_plane_invariant": limiting_invariant,
        "represented_brackets_match": commutators_match,
        "limiting_plane_representation": limiting_decomposition,
        "quotient_representation": quotient_decomposition,
        "boundary_kernel_representation": boundary_decomposition,
        "representation_sum_matches_boundary": representation_sum_matches,
        "pass": path_fixed and limiting_invariant and commutators_match and representation_sum_matches,
    }


def _analyze_path(path: PathSpec) -> PathAnalysis:
    curve = _curve_certificate(path)
    kernel, limiting_plane, quotient_frame, boundary_frame = _kernel_limit(path)
    representation = _representation_certificate(path, limiting_plane, quotient_frame)
    row = {
        "incidence": path.incidence,
        "high_orbit": path.high_orbit,
        "boundary_orbit": path.boundary_orbit,
        "approach": path.approach,
        "split_path_coefficients": [
            [str(value) for value in coefficient] for coefficient in path.coefficients[: _path_degree(path) + 1]
        ],
        "curve": curve,
        "kernel_limit": kernel,
        "preserved_stabilizer": representation,
        "pass": curve["pass"] and kernel["pass"] and representation["pass"],
    }
    return PathAnalysis(path, row, limiting_plane, quotient_frame, boundary_frame)


def _analyze_path_task(path: PathSpec) -> PathAnalysis:
    return _analyze_path(path)


def _normal_restriction_certificate(analysis: PathAnalysis, perturb_imaginary_normal: bool = False) -> dict[str, Any]:
    boundary_frame = analysis.boundary_kernel
    normal_direction = analysis.path.coefficients[1]
    imaginary_direction = [sp.I * value for value in normal_direction]
    mutation_coordinate = None
    if perturb_imaginary_normal:
        mutation_coordinate = 0
        imaginary_direction[mutation_coordinate] += 1
    normal_restriction = sp.simplify(boundary_frame.T * _matrix_for_split(normal_direction) * boundary_frame)
    imaginary_restriction = sp.simplify(
        boundary_frame.T * _matrix_for_split(tuple(imaginary_direction)) * boundary_frame
    )
    orbit_tangents = regularity.h_generators(analysis.path.coefficients[0])
    orbit_restriction_ranks = [
        sp.simplify(boundary_frame.T * _matrix_for_split(tuple(tangent)) * boundary_frame).rank()
        for tangent in orbit_tangents
    ]
    imaginary_relation = sp.simplify(imaginary_restriction - sp.I * normal_restriction) == sp.zeros(
        BOUNDARY_KERNEL_DIMENSION
    )
    return {
        "normal_restriction": _matrix_rows(normal_restriction),
        "imaginary_normal_restriction": _matrix_rows(imaginary_restriction),
        "normal_restriction_rank": normal_restriction.rank(),
        "imaginary_normal_restriction_rank": imaginary_restriction.rank(),
        "imaginary_normal_equals_i_times_normal": imaginary_relation,
        "boundary_orbit_tangent_count": len(orbit_tangents),
        "boundary_orbit_restriction_ranks": orbit_restriction_ranks,
        "all_boundary_orbit_tangents_restrict_to_zero": all(rank == 0 for rank in orbit_restriction_ranks),
        "complex_nonzero_normal_multiples_have_same_kernel": imaginary_relation and normal_restriction.rank() == 2,
        "mutation_coordinate": mutation_coordinate,
        "pass": (
            normal_restriction.rank() == 2
            and imaginary_restriction.rank() == 2
            and imaginary_relation
            and all(rank == 0 for rank in orbit_restriction_ranks)
        ),
    }


def _canonical_x_b9_certificate(analysis: PathAnalysis, perturb_imaginary_normal: bool = False) -> dict[str, Any]:
    named_triples = symmetry._expected_lie_triples("")
    base_generators = [triple[0] for _name, triple in named_triples]
    domain_generators = [triple[1] for _name, triple in named_triples]
    boundary_point = tuple(symmetry.equations.y_from_split(analysis.path.coefficients[0]))
    tangent_columns = [stabilizer._matrix_vector(generator, boundary_point) for generator in base_generators]
    tangent_rows = [[tangent_columns[column][row] for column in range(len(named_triples))] for row in range(32)]
    coefficients = tuple(tuple(row) for row in symmetry.equations.nullspace(tangent_rows))
    domains = tuple(stabilizer._linear_combination(row, domain_generators) for row in coefficients)
    full_adapted = _adapted_real_basis(sp.Matrix.hstack(analysis.limiting_plane, analysis.quotient_frame))
    complex_structure = aligned_representation._complex_structure()
    representations = [
        aligned_representation._fiber_matrix(domain, full_adapted, complex_structure) for domain in domains
    ]
    plane_invariant = all(
        matrix[LIMITING_KERNEL_DIMENSION:, :LIMITING_KERNEL_DIMENSION]
        == sp.zeros(QUOTIENT_DIMENSION, LIMITING_KERNEL_DIMENSION)
        for matrix in representations
    )
    closure_key = "Xp" if analysis.path.high_orbit == "X+" else "Xm"
    germ = regularity.EXPECTED_GERMS[(closure_key, "B9")]
    smooth_normal_line = germ == (1, 1, 1, -1, 1, None)
    normal_restriction = _normal_restriction_certificate(analysis, perturb_imaginary_normal)
    return {
        "transverse_germ": {
            "dimension": germ[0],
            "multiplicity": germ[1],
            "embedding_dimension": germ[2],
            "sheets": germ[4],
            "smooth_normal_line": smooth_normal_line,
        },
        "constant_lift_stabilizer_dimension": len(coefficients),
        "expected_constant_lift_stabilizer_dimension": 3,
        "limiting_plane_invariant_under_full_constant_lift_stabilizer": plane_invariant,
        "normal_restriction_certificate": normal_restriction,
        "argument": (
            "the reduced transverse germ is one smooth complex normal line; the constant-rank lemma makes every "
            "boundary-orbit tangent restrict to zero on the boundary kernel, and the exact identity "
            "F^T A(i d) F=i F^T A(d) F makes every nonzero complex normal multiple have the same kernel"
        ),
        "pass": smooth_normal_line and len(coefficients) == 3 and plane_invariant and normal_restriction["pass"],
    }


def _incidence_row(incidence: str, analyses: Sequence[PathAnalysis]) -> dict[str, Any]:
    _require(len(analyses) >= 2, f"{incidence} needs at least two analyzed approaches")
    first = analyses[0]
    comparisons = []
    same_boundary_kernel = True
    for left_index, right_index in itertools.combinations(range(len(analyses)), 2):
        left = analyses[left_index]
        right = analyses[right_index]
        same_boundary_kernel = same_boundary_kernel and (
            sp.Matrix.hstack(left.boundary_kernel, right.boundary_kernel).rank() == BOUNDARY_KERNEL_DIMENSION
        )
        union_rank = sp.Matrix.hstack(left.limiting_plane, right.limiting_plane).rank()
        comparisons.append(
            {
                "left_approach": left.row["approach"],
                "right_approach": right.row["approach"],
                "limiting_plane_union_dimension": union_rank,
                "limiting_plane_intersection_dimension": 2 * LIMITING_KERNEL_DIMENSION - union_rank,
                "limiting_planes_equal": union_rank == LIMITING_KERNEL_DIMENSION,
            }
        )
    path_dependent = any(not comparison["limiting_planes_equal"] for comparison in comparisons)
    canonical_certificate = None
    canonical_inclusion = False
    if not path_dependent and incidence in ("X+->B9", "X-->B9"):
        canonical_certificate = _canonical_x_b9_certificate(first)
        canonical_inclusion = bool(canonical_certificate["pass"])
    sheet_analyses = [
        analysis for analysis in analyses if str(analysis.row["approach"]).startswith("middle-coordinate-sheet")
    ]
    sheet_comparison = None
    if len(sheet_analyses) == 2:
        sheet_union_rank = sp.Matrix.hstack(
            sheet_analyses[0].limiting_plane,
            sheet_analyses[1].limiting_plane,
        ).rank()
        sheet_comparison = {
            "approaches": [analysis.row["approach"] for analysis in sheet_analyses],
            "limiting_plane_union_dimension": sheet_union_rank,
            "sheet_limits_equal": sheet_union_rank == LIMITING_KERNEL_DIMENSION,
        }
    decision_complete = path_dependent or canonical_inclusion
    return {
        "incidence": incidence,
        "high_orbit": first.row["high_orbit"],
        "boundary_orbit": first.row["boundary_orbit"],
        "same_boundary_kernel": same_boundary_kernel,
        "approaches": [analysis.row for analysis in analyses],
        "comparison": {
            "pairwise": comparisons,
            "path_dependent": path_dependent,
            "canonical_inclusion": canonical_inclusion,
            "decision_complete": decision_complete,
            "canonical_certificate": canonical_certificate,
            "sheet_comparison": sheet_comparison,
            "conclusion": (
                "Exact approaches at the same boundary point give different limiting four-planes."
                if path_dependent
                else "The smooth normal line and stabilizer invariance give a canonical limiting four-plane."
            ),
        },
        "pass": same_boundary_kernel and decision_complete and all(analysis.row["pass"] for analysis in analyses),
    }


def _incidence_task(task: tuple[str, tuple[PathAnalysis, ...]]) -> dict[str, Any]:
    incidence, analyses = task
    return _incidence_row(incidence, analyses)


def _path_mutation_control(path: PathSpec) -> dict[str, Any]:
    first_order = list(path.coefficients[1])
    first_order[7] += 1
    mutated = PathSpec(
        path.high_orbit,
        path.boundary_orbit,
        path.approach,
        (path.coefficients[0], tuple(first_order), path.coefficients[2]),
    )
    certificate = _curve_certificate(mutated)
    return {
        "mutation": "add a middle-coordinate term to a W8 degeneration",
        "target": path.incidence,
        "closure_containment_changed": not certificate["closure_containment_proved"],
        "detected": not certificate["pass"],
    }


def _schur_mutation_control(path: PathSpec) -> dict[str, Any]:
    baseline, _plane, _quotient, _boundary = _kernel_limit(path)
    mutated, _mutated_plane, _mutated_quotient, _mutated_boundary = _kernel_limit(path, drop_schur_correction=True)
    return {
        "mutation": "delete the second-order Schur correction",
        "target": path.incidence,
        "baseline_effective_rank": baseline["effective_restricted_rank"],
        "mutated_effective_rank": mutated["effective_restricted_rank"],
        "downstream_rank_changed": baseline["effective_restricted_rank"] != mutated["effective_restricted_rank"],
        "detected": not mutated["pass"],
    }


def _imaginary_normal_mutation_control(analysis: PathAnalysis) -> dict[str, Any]:
    baseline = _canonical_x_b9_certificate(analysis)
    mutated = _canonical_x_b9_certificate(analysis, perturb_imaginary_normal=True)
    return {
        "mutation": "add one split-coordinate basis vector to the imaginary normal direction",
        "target": analysis.path.incidence,
        "baseline_imaginary_relation": baseline["normal_restriction_certificate"][
            "imaginary_normal_equals_i_times_normal"
        ],
        "mutated_imaginary_relation": mutated["normal_restriction_certificate"][
            "imaginary_normal_equals_i_times_normal"
        ],
        "downstream_certificate_changed": baseline["pass"] and not mutated["pass"],
        "detected": not mutated["pass"],
    }


def _mutation_control_task(task: tuple[str, PathSpec | PathAnalysis]) -> tuple[str, dict[str, Any]]:
    mutation_name, target = task
    if mutation_name == "path":
        if not isinstance(target, PathSpec):
            raise TypeError("the path mutation needs a path specification")
        return mutation_name, _path_mutation_control(target)
    if mutation_name == "frame":
        if not isinstance(target, PathSpec):
            raise TypeError("the frame mutation needs a path specification")
        return mutation_name, _schur_mutation_control(target)
    if mutation_name == "imaginary_normal":
        if not isinstance(target, PathAnalysis):
            raise TypeError("the normal mutation needs an analyzed path")
        return mutation_name, _imaginary_normal_mutation_control(target)
    raise ValueError(f"unknown boundary mutation {mutation_name!r}")


def build_record() -> dict[str, Any]:
    paths = _path_specs()
    analyses = parallel.ordered_map(_analyze_path_task, paths, min_items=1)
    by_incidence: dict[str, list[PathAnalysis]] = {}
    for analysis in analyses:
        by_incidence.setdefault(str(analysis.row["incidence"]), []).append(analysis)
    incidence_rows = parallel.ordered_map(
        _incidence_task,
        [(incidence, tuple(by_incidence[incidence])) for incidence in sorted(by_incidence)],
        min_items=1,
    )
    mutation_control = dict(
        parallel.ordered_map(
            _mutation_control_task,
            [
                ("path", next(path for path in paths if path.incidence == "W8->B9")),
                (
                    "frame",
                    next(path for path in paths if path.incidence == "E8bar->Va+" and _path_degree(path) == 2),
                ),
                ("imaginary_normal", by_incidence["X+->B9"][0]),
            ],
            min_items=1,
        )
    )
    path_mutation = mutation_control["path"]
    schur_mutation = mutation_control["frame"]
    imaginary_normal_mutation = mutation_control["imaginary_normal"]
    path_dependent_count = sum(bool(row["comparison"]["path_dependent"]) for row in incidence_rows)
    canonical_count = sum(bool(row["comparison"]["canonical_inclusion"]) for row in incidence_rows)
    result = {
        "schema": SCHEMA,
        "inputs": {str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS},
        "incidences": incidence_rows,
        "summary": {
            "incidence_count": len(incidence_rows),
            "approach_count": len(paths),
            "path_dependent_incidence_count": path_dependent_count,
            "canonical_incidence_count": canonical_count,
            "standing_question_answer": (
                "There is no universal canonical inclusion: thirteen incidences are path-dependent. The X_+ to B9 "
                "and X_- to B9 incidences have canonical limits because their transverse germs are smooth normal "
                "lines, boundary-orbit tangents restrict to zero, and F^T A(i d) F=i F^T A(d) F."
            ),
        },
        "mutation_control": mutation_control,
        "scope": (
            "The record treats every nullity-twelve orbit in the committed closure table. It compares two exact "
            "algebraic approaches at one verified point of each boundary orbit and classifies the connected compact "
            "stabilizer that fixes the whole path. Different limiting planes refute a path-independent canonical "
            "inclusion; matching planes would not by themselves prove one. The 33 paths do not compute the full "
            "fiber of the closed kernel Gauss graph in Gr(4,K_0), so they do not supply the attaching data required "
            "by roadmap item 6."
        ),
        "pass": (
            len(incidence_rows) == 15
            and len(paths) == 33
            and path_dependent_count == 13
            and canonical_count == 2
            and all(row["pass"] for row in incidence_rows)
            and path_mutation["detected"]
            and path_mutation["closure_containment_changed"]
            and schur_mutation["detected"]
            and schur_mutation["downstream_rank_changed"]
            and imaginary_normal_mutation["detected"]
            and imaginary_normal_mutation["downstream_certificate_changed"]
        ),
    }
    return result


def self_test() -> None:
    record = build_record()
    _require(record["pass"], "baseline boundary-specialization record failed")
    _require(record["mutation_control"]["path"]["detected"], "path mutation survived")
    _require(
        record["mutation_control"]["path"]["closure_containment_changed"],
        "path mutation changed no closure check",
    )
    _require(record["mutation_control"]["frame"]["detected"], "Schur mutation survived")
    _require(
        record["mutation_control"]["frame"]["downstream_rank_changed"],
        "Schur mutation changed no downstream rank",
    )
    _require(record["mutation_control"]["imaginary_normal"]["detected"], "imaginary-normal mutation survived")
    _require(
        record["mutation_control"]["imaginary_normal"]["downstream_certificate_changed"],
        "imaginary-normal mutation changed no downstream canonicity certificate",
    )


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--out", type=Path)
    output.add_argument("--check", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        self_test()
    if arguments.out is not None:
        arguments.out.write_bytes(_record_bytes(build_record()))
    if arguments.check is not None:
        expected = arguments.check.read_bytes()
        actual = _record_bytes(build_record())
        _require(actual == expected, f"record differs from {arguments.check}")
    if not arguments.self_test and arguments.out is None and arguments.check is None:
        parser.error("select --out, --check, or --self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
