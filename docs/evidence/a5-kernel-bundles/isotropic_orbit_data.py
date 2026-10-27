"""Exact compact moduli and kernel representations on ``B9`` and ``VB``.

In original coordinates put ``w=-i*v``.  On ``B9`` the ordered pair
``(u,w)`` spans a totally null cross-zero complex two-plane.  Its normalized
Hermitian Gram matrix is the complete compact-orbit invariant.  On ``VB``
that matrix has rank one and records the projective coefficient ratio.  This
replay checks the invariant domains, compact tangent ranks, connected
stabilizers, and their actions on the complex rank-six kernel.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import aligned_orbit_moduli as aligned  # noqa: E402
import aligned_stabilizer_representation as aligned_representation  # noqa: E402
import kernel_symmetry as symmetry  # noqa: E402
import stabilizer_representation as stabilizer  # noqa: E402

from cd_core import cd_sign, left_mult_matrix_exact  # noqa: E402

DIMENSION = 32
COMPACT_GENERATOR_COUNT = 15
COMPLEX_FIBER_DIMENSION = 6

KERNEL_SYMMETRY_RESULT = HERE / "result.json"
KERNEL_SYMMETRY_SCRIPT = HERE / "kernel_symmetry.py"
NULLITY_SIXTEEN_RESULT = HERE / "stabilizer-result.json"
NULLITY_SIXTEEN_SCRIPT = HERE / "stabilizer_representation.py"
V_MODULI_RESULT = HERE / "v-orbit-moduli-result.json"
V_MODULI_SCRIPT = HERE / "v_orbit_moduli.py"
HELPER_SCRIPTS = (
    HERE / "aligned_orbit_moduli.py",
    HERE / "aligned_stabilizer_representation.py",
)

RationalMatrix = symmetry.RationalMatrix
ComplexRational = tuple[Fraction, Fraction]
CoefficientFrame = tuple[ComplexRational, ComplexRational, ComplexRational, ComplexRational]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _complex_add(first: ComplexRational, second: ComplexRational) -> ComplexRational:
    return first[0] + second[0], first[1] + second[1]


def _complex_multiply(first: ComplexRational, second: ComplexRational) -> ComplexRational:
    return first[0] * second[0] - first[1] * second[1], first[0] * second[1] + first[1] * second[0]


def _complex_conjugate(value: ComplexRational) -> ComplexRational:
    return value[0], -value[1]


def _complex_scale_by_i(value: ComplexRational, sign: int) -> ComplexRational:
    if sign not in (-1, 1):
        raise ValueError("complex i multiplier must have sign +1 or -1")
    return -sign * value[1], sign * value[0]


def _complex_divide(numerator: ComplexRational, denominator: ComplexRational) -> ComplexRational:
    norm_squared = _complex_norm_squared(denominator)
    if norm_squared == 0:
        raise ZeroDivisionError("complex denominator is zero")
    product = _complex_multiply(numerator, _complex_conjugate(denominator))
    return product[0] / norm_squared, product[1] / norm_squared


def _complex_norm_squared(value: ComplexRational) -> Fraction:
    return value[0] * value[0] + value[1] * value[1]


def _complex_dot(first: Sequence[ComplexRational], second: Sequence[ComplexRational]) -> ComplexRational:
    output = (Fraction(0), Fraction(0))
    for left, right in zip(first, second, strict=True):
        output = _complex_add(output, _complex_multiply(left, right))
    return output


def _hermitian_dot(first: Sequence[ComplexRational], second: Sequence[ComplexRational]) -> ComplexRational:
    output = (Fraction(0), Fraction(0))
    for left, right in zip(first, second, strict=True):
        output = _complex_add(output, _complex_multiply(_complex_conjugate(left), right))
    return output


def _complex_cross(first: Sequence[ComplexRational], second: Sequence[ComplexRational]) -> tuple[ComplexRational, ...]:
    output = [(Fraction(0), Fraction(0)) for _ in range(7)]
    for left_index, left in enumerate(first, start=1):
        for right_index, right in enumerate(second, start=1):
            result_index = left_index ^ right_index
            if result_index:
                product = _complex_multiply(left, right)
                signed = (
                    Fraction(cd_sign(8, left_index, right_index)) * product[0],
                    Fraction(cd_sign(8, left_index, right_index)) * product[1],
                )
                output[result_index - 1] = _complex_add(output[result_index - 1], signed)
    return tuple(output)


def _complex_vector_add(
    first: Sequence[ComplexRational], second: Sequence[ComplexRational]
) -> tuple[ComplexRational, ...]:
    return tuple(_complex_add(left, right) for left, right in zip(first, second, strict=True))


def _complex_vector_scale(scalar: ComplexRational, vector: Sequence[ComplexRational]) -> tuple[ComplexRational, ...]:
    return tuple(_complex_multiply(scalar, value) for value in vector)


def _complex_vector_zero(vector: Sequence[ComplexRational]) -> bool:
    return all(value == (Fraction(0), Fraction(0)) for value in vector)


def _canonical_plane() -> tuple[tuple[ComplexRational, ...], tuple[ComplexRational, ...]]:
    zero = (Fraction(0), Fraction(0))
    first = [zero for _ in range(7)]
    second = [zero for _ in range(7)]
    first[0] = (Fraction(0), Fraction(1))
    first[2] = (Fraction(-1), Fraction(0))
    second[3] = (Fraction(0), Fraction(1))
    second[5] = (Fraction(-1), Fraction(0))
    return tuple(first), tuple(second)


def _point_from_coefficients(coefficients: CoefficientFrame, mutation: str = "") -> tuple[Fraction, ...]:
    if mutation not in ("", "force_rank_one"):
        raise ValueError(f"unknown point mutation {mutation!r}")
    first, second = _canonical_plane()
    lower = _complex_vector_add(
        _complex_vector_scale(coefficients[0], first),
        _complex_vector_scale(coefficients[1], second),
    )
    rotated_upper = _complex_vector_add(
        _complex_vector_scale(coefficients[2], first),
        _complex_vector_scale(coefficients[3], second),
    )
    if mutation == "force_rank_one":
        rotated_upper = lower
    upper = tuple(_complex_scale_by_i(value, 1) for value in rotated_upper)
    coordinates = [*lower, (Fraction(0), Fraction(0)), *upper]
    point = [Fraction(0)] * DIMENSION
    for index, value in enumerate(coordinates, start=1):
        point[index] = value[0]
        point[16 + index] = value[1]
    return tuple(point)


def _complex_coordinates(point: Sequence[Fraction]) -> tuple[ComplexRational, ...]:
    _require(len(point) == DIMENSION, "A_5 point must have 32 real coordinates")
    return tuple((Fraction(point[index]), Fraction(point[16 + index])) for index in range(1, 16))


def _blocks(
    point: Sequence[Fraction],
) -> tuple[tuple[ComplexRational, ...], ComplexRational, tuple[ComplexRational, ...]]:
    coordinates = _complex_coordinates(point)
    lower = coordinates[:7]
    middle = coordinates[7]
    rotated_upper = tuple(_complex_scale_by_i(value, -1) for value in coordinates[8:])
    return lower, middle, rotated_upper


def _format_complex(value: ComplexRational) -> str:
    return f"{value[0]}+({value[1]})i"


def _projective_ratio(
    lower: Sequence[ComplexRational], rotated_upper: Sequence[ComplexRational]
) -> tuple[str, ComplexRational | None, bool]:
    lower_nonzero = any(value != (Fraction(0), Fraction(0)) for value in lower)
    if not lower_nonzero:
        collinear = any(value != (Fraction(0), Fraction(0)) for value in rotated_upper)
        return "infinity", None, collinear
    pivot = next(index for index, value in enumerate(lower) if value != (Fraction(0), Fraction(0)))
    ratio = _complex_divide(rotated_upper[pivot], lower[pivot])
    collinear = all(rotated_upper[index] == _complex_multiply(ratio, lower[index]) for index in range(7))
    original_lambda = _complex_scale_by_i(ratio, 1)
    return _format_complex(original_lambda), original_lambda, collinear


def _pair_invariants(point: Sequence[Fraction]) -> dict[str, Any]:
    lower, middle, rotated_upper = _blocks(point)
    lower_square = _complex_dot(lower, lower)
    upper_square = _complex_dot(rotated_upper, rotated_upper)
    mutual_square = _complex_dot(lower, rotated_upper)
    cross = _complex_cross(lower, rotated_upper)
    lower_norm = _hermitian_dot(lower, lower)[0]
    upper_norm = _hermitian_dot(rotated_upper, rotated_upper)[0]
    mixed = _hermitian_dot(lower, rotated_upper)
    trace = lower_norm + upper_norm
    determinant = lower_norm * upper_norm - _complex_norm_squared(mixed)
    _require(trace > 0, "isotropic pair must be nonzero")
    ball_coordinates = (
        (lower_norm - upper_norm) / trace,
        Fraction(2) * mixed[0] / trace,
        Fraction(2) * mixed[1] / trace,
    )
    ball_radius_squared = sum((value * value for value in ball_coordinates), Fraction(0))
    determinant_identity = Fraction(1) - ball_radius_squared == Fraction(4) * determinant / (trace * trace)
    original_lambda_text, original_lambda, collinear = _projective_ratio(lower, rotated_upper)
    excluded_ratio = original_lambda in ((Fraction(0), Fraction(1)), (Fraction(0), Fraction(-1)))
    common_equations = (
        middle == (Fraction(0), Fraction(0))
        and lower_square == (Fraction(0), Fraction(0))
        and upper_square == (Fraction(0), Fraction(0))
        and mutual_square == (Fraction(0), Fraction(0))
        and _complex_vector_zero(cross)
    )
    inside_b9 = common_equations and determinant > 0
    inside_vb = common_equations and determinant == 0 and collinear and not excluded_ratio
    return {
        "middle_zero": middle == (Fraction(0), Fraction(0)),
        "lower_bilinear_square": [str(value) for value in lower_square],
        "upper_bilinear_square": [str(value) for value in upper_square],
        "mutual_bilinear_square": [str(value) for value in mutual_square],
        "cross_zero": _complex_vector_zero(cross),
        "hermitian_gram": [
            [str(lower_norm), _format_complex(mixed)],
            [_format_complex(_complex_conjugate(mixed)), str(upper_norm)],
        ],
        "gram_trace": str(trace),
        "gram_determinant": str(determinant),
        "normalized_ball_coordinates": [str(value) for value in ball_coordinates],
        "normalized_ball_radius_squared": str(ball_radius_squared),
        "determinant_ball_identity": determinant_identity,
        "rank_one_blocks_collinear": collinear,
        "original_projective_ratio_lambda": original_lambda_text,
        "lambda_avoids_plus_minus_i": not excluded_ratio,
        "inside_B9": inside_b9,
        "inside_VB": inside_vb,
    }


def _gram_derivative(
    point: Sequence[Fraction], tangent: Sequence[Fraction], drop_common_phase: bool
) -> tuple[Fraction, Fraction, ComplexRational]:
    lower, _middle, rotated_upper = _blocks(point)
    lower_derivative, _middle_derivative, upper_derivative = _blocks(tangent)
    if drop_common_phase:
        upper_derivative = tuple((Fraction(0), Fraction(0)) for _ in range(7))
    lower_norm_derivative = Fraction(2) * _hermitian_dot(lower, lower_derivative)[0]
    upper_norm_derivative = Fraction(2) * _hermitian_dot(rotated_upper, upper_derivative)[0]
    mixed_derivative = _complex_add(
        _hermitian_dot(lower_derivative, rotated_upper),
        _hermitian_dot(lower, upper_derivative),
    )
    return lower_norm_derivative, upper_norm_derivative, mixed_derivative


def _gram_stationary(point: Sequence[Fraction], mutation: str = "") -> bool:
    if mutation not in ("", "drop_common_phase"):
        raise ValueError(f"unknown Gram mutation {mutation!r}")
    compact = stabilizer._compact_triples()
    for generator_index, (_name, triple) in enumerate(compact):
        tangent = stabilizer._matrix_vector(triple[0], point)
        derivative = _gram_derivative(
            point,
            tangent,
            mutation == "drop_common_phase" and generator_index == len(compact) - 1,
        )
        if derivative != (Fraction(0), Fraction(0), (Fraction(0), Fraction(0))):
            return False
    return True


def _primitive_integer_vector(values: Sequence[Fraction]) -> tuple[int, ...]:
    denominator_lcm = math.lcm(*(value.denominator for value in values))
    integers = [int(value * denominator_lcm) for value in values]
    divisor = math.gcd(*integers)
    if divisor:
        integers = [value // abs(divisor) for value in integers]
    first_nonzero = next((value for value in integers if value), 0)
    if first_nonzero < 0:
        integers = [-value for value in integers]
    return tuple(integers)


def _primitive_scale(primitive: Sequence[int], rational: Sequence[Fraction]) -> Fraction:
    return next(Fraction(integer, value) for integer, value in zip(primitive, rational, strict=True) if value)


def _stabilizer_data(
    point: Sequence[Fraction], mutation: str
) -> tuple[int, list[tuple[Fraction, ...]], list[RationalMatrix], list[RationalMatrix]]:
    compact = stabilizer._compact_triples()
    tangent_rank, _base_stabilizers, coefficient_rows = aligned._stabilizer_data(point, "")
    coefficients = list(coefficient_rows)
    if mutation == "include_moving_direction":
        moving_index = next(
            index for index, (_name, triple) in enumerate(compact) if any(stabilizer._matrix_vector(triple[0], point))
        )
        coefficients[0] = tuple(Fraction(index == moving_index) for index in range(COMPACT_GENERATOR_COUNT))
    elif mutation not in ("", "perturb_fiber_action"):
        raise ValueError(f"unknown stabilizer mutation {mutation!r}")
    base_generators = [triple[0] for _name, triple in compact]
    domain_generators = [triple[1] for _name, triple in compact]
    bases = [stabilizer._linear_combination(row, base_generators) for row in coefficients]
    domains = [stabilizer._linear_combination(row, domain_generators) for row in coefficients]
    return tangent_rank, coefficients, bases, domains


def _spectral_projector(matrix: sp.Matrix, eigenvalue: sp.Expr) -> sp.Matrix:
    projector = sp.eye(matrix.rows)
    for other in matrix.eigenvals():
        if other != eigenvalue:
            projector = projector * (matrix - other * sp.eye(matrix.rows)) / (eigenvalue - other)
    return sp.simplify(projector)


def _circle_certificate(generator: sp.Matrix, representation: Sequence[sp.Matrix]) -> dict[str, Any]:
    weights = generator.eigenvals()
    projectors = [_spectral_projector(generator, weight) for weight in weights]
    zero = sp.zeros(generator.rows)
    projector_checks = (
        all(sp.simplify(projector * projector - projector) == zero for projector in projectors)
        and all(
            sp.simplify(projector * other) == zero
            for index, projector in enumerate(projectors)
            for other_index, other in enumerate(projectors)
            if index != other_index
        )
        and sp.simplify(sum(projectors, zero) - sp.eye(generator.rows)) == zero
        and all(
            sp.simplify(projector * action - action * projector) == zero
            for projector in projectors
            for action in representation
        )
    )
    expected = {-sp.I: 3, -2 * sp.I: 3}
    return {
        "decomposition": "3 C_(-1) + 3 C_(-2)",
        "weight_multiplicities": {sp.sstr(weight): multiplicity for weight, multiplicity in weights.items()},
        "projector_ranks": [projector.rank() for projector in projectors],
        "pass": weights == expected and projector_checks,
    }


def _highest_weight(casimir_eigenvalue: sp.Expr) -> int:
    for highest_weight in range(COMPLEX_FIBER_DIMENSION):
        if sp.simplify(casimir_eigenvalue - sp.Rational(highest_weight * (highest_weight + 2), 8)) == 0:
            return highest_weight
    raise ArithmeticError(f"unrecognized sl2 Casimir eigenvalue {casimir_eigenvalue}")


def _joint_decomposition(center: sp.Matrix, casimir: sp.Matrix) -> list[dict[str, Any]]:
    identity = sp.eye(COMPLEX_FIBER_DIMENSION)
    rows: list[dict[str, Any]] = []
    for center_weight in sorted(center.eigenvals(), key=sp.default_sort_key):
        for casimir_value in sorted(casimir.eigenvals(), key=sp.default_sort_key):
            stacked = (center - center_weight * identity).col_join(casimir - casimir_value * identity)
            joint_dimension = COMPLEX_FIBER_DIMENSION - stacked.rank()
            if joint_dimension:
                highest_weight = _highest_weight(casimir_value)
                irreducible_dimension = highest_weight + 1
                _require(
                    joint_dimension % irreducible_dimension == 0,
                    "joint eigenspace is not a sum of equal sl2 irreducibles",
                )
                rows.append(
                    {
                        "central_weight": sp.sstr(center_weight),
                        "sl2_highest_weight": highest_weight,
                        "irreducible_dimension": irreducible_dimension,
                        "multiplicity": joint_dimension // irreducible_dimension,
                        "joint_dimension": joint_dimension,
                        "casimir_eigenvalue": sp.sstr(casimir_value),
                    }
                )
    return rows


def _u2_projector_certificate(representation: Sequence[sp.Matrix], center: sp.Matrix) -> dict[str, Any]:
    central_projectors = {weight: _spectral_projector(center, weight) for weight in center.eigenvals()}
    repeated_weight = -3 * sp.I
    repeated_projector = central_projectors[repeated_weight]
    block_basis = sp.Matrix.hstack(*repeated_projector.columnspace())
    commutant = aligned_representation._commutant_basis(representation)
    candidates = [*commutant]
    candidates.extend(
        commutant[first] + commutant[second]
        for first in range(len(commutant))
        for second in range(first + 1, len(commutant))
    )
    split: list[sp.Matrix] | None = None
    for candidate in candidates:
        restricted, parameters = block_basis.gauss_jordan_solve(candidate * block_basis)
        _require(parameters.rows == 0, "commutant element escaped the repeated doublet block")
        eigenvalues = restricted.eigenvals()
        if len(eigenvalues) == 2 and all(multiplicity == 2 for multiplicity in eigenvalues.values()):
            first_value, second_value = list(eigenvalues)
            first = sp.simplify(
                repeated_projector
                * (candidate - second_value * sp.eye(COMPLEX_FIBER_DIMENSION))
                * repeated_projector
                / (first_value - second_value)
            )
            split = [first, sp.simplify(repeated_projector - first)]
            break
    if split is None:
        raise RuntimeError("commutant supplies no exact two-plus-two split")
    projectors = [central_projectors[-4 * sp.I], *split, central_projectors[-2 * sp.I]]
    zero = sp.zeros(COMPLEX_FIBER_DIMENSION)
    checks = (
        [projector.rank() for projector in projectors] == [1, 2, 2, 1]
        and all(sp.simplify(projector * projector - projector) == zero for projector in projectors)
        and all(
            sp.simplify(projectors[first] * projectors[second]) == zero
            for first in range(len(projectors))
            for second in range(len(projectors))
            if first != second
        )
        and sp.simplify(sum(projectors, zero) - sp.eye(COMPLEX_FIBER_DIMENSION)) == zero
        and all(
            sp.simplify(projector * action - action * projector) == zero
            for projector in projectors
            for action in representation
        )
    )
    return {
        "commutant_dimension": len(commutant),
        "projector_ranks": [projector.rank() for projector in projectors],
        "pass": checks,
    }


def _representation_check(point: Sequence[Fraction], orbit: str, mutation: str = "") -> dict[str, Any]:
    tangent_rank, coefficients, stabilizer_bases, stabilizer_domains = _stabilizer_data(point, mutation)
    point_fixed = [not any(stabilizer._matrix_vector(matrix, point)) for matrix in stabilizer_bases]
    if mutation == "include_moving_direction":
        return {
            "mutation": mutation,
            "compact_tangent_rank": tangent_rank,
            "point_fixed": point_fixed,
            "pass": all(point_fixed),
        }
    left_matrix = tuple(tuple(row) for row in left_mult_matrix_exact(DIMENSION, tuple(point)))
    complex_structure = aligned_representation._complex_structure()
    adapted_basis = aligned_representation._adapted_kernel_basis(left_matrix, complex_structure, 12)
    kernel_preserved = [
        all(
            not any(stabilizer._matrix_vector(left_matrix, stabilizer._matrix_vector(domain, vector)))
            for vector in adapted_basis
        )
        for domain in stabilizer_domains
    ]
    fiber_matrices = [
        aligned_representation._fiber_matrix(domain, adapted_basis, complex_structure) for domain in stabilizer_domains
    ]
    if mutation == "perturb_fiber_action":
        fiber_matrices[0] = fiber_matrices[0].copy()
        fiber_matrices[0][0, 1] += 1
    commutators_match = aligned_representation._representation_commutators_match(
        stabilizer_domains,
        fiber_matrices,
        adapted_basis,
        complex_structure,
    )
    if mutation == "perturb_fiber_action":
        return {
            "mutation": mutation,
            "point_fixed": point_fixed,
            "kernel_preserved": kernel_preserved,
            "representation_commutators_match": commutators_match,
            "pass": commutators_match,
        }

    compact = stabilizer._compact_triples()
    compact_names = [name for name, _triple in compact]
    if orbit == "B9":
        _require(len(coefficients) == 1, "B9 stabilizer must be one-dimensional")
        primitive = _primitive_integer_vector(coefficients[0])
        scale = _primitive_scale(primitive, coefficients[0])
        generator = sp.simplify(sp.Rational(scale.numerator, scale.denominator) * fiber_matrices[0])
        representation_certificate = _circle_certificate(generator, fiber_matrices)
        primitive_domain = stabilizer._linear_combination(
            tuple(Fraction(value) for value in primitive),
            [triple[1] for _name, triple in compact],
        )
        primitive_base = stabilizer._linear_combination(
            tuple(Fraction(value) for value in primitive),
            [triple[0] for _name, triple in compact],
        )
        group_certificate = {
            "connected_group": "U(1)",
            "base_characteristic_polynomial": sp.sstr(sp.factor(sp.Matrix(primitive_base).charpoly().as_expr())),
            "domain_characteristic_polynomial": sp.sstr(sp.factor(sp.Matrix(primitive_domain).charpoly().as_expr())),
            "primitive_period": "2*pi, because an odd unit imaginary eigenvalue occurs",
            "pass": (-sp.I in generator.eigenvals()),
        }
        derived_dimension = 0
        center_dimension = 1
        representation = representation_certificate
    elif orbit == "VB":
        _require(len(coefficients) == 4, "VB stabilizer must be four-dimensional")
        center_coefficients = stabilizer._center_coefficients(stabilizer_domains)
        compact_center = tuple(
            sum(
                (center_coefficients[row] * coefficients[row][column] for row in range(4)),
                Fraction(0),
            )
            for column in range(COMPACT_GENERATOR_COUNT)
        )
        primitive = _primitive_integer_vector(compact_center)
        scale = _primitive_scale(primitive, compact_center)
        center_fiber = sum(
            (
                sp.Rational(center_coefficients[index].numerator, center_coefficients[index].denominator)
                * fiber_matrices[index]
                for index in range(4)
            ),
            sp.zeros(COMPLEX_FIBER_DIMENSION),
        )
        primitive_center_fiber = sp.simplify(sp.Rational(scale.numerator, scale.denominator) * center_fiber)
        derived_domains = aligned_representation._derived_basis(stabilizer_domains)
        casimir, killing = aligned_representation._casimir(derived_domains, adapted_basis, complex_structure)
        decomposition = _joint_decomposition(primitive_center_fiber, casimir)
        projector_certificate = _u2_projector_certificate(fiber_matrices, primitive_center_fiber)
        expected_decomposition = [
            ("-4*I", 0, 1),
            ("-3*I", 1, 2),
            ("-2*I", 0, 1),
        ]
        signature = [(row["central_weight"], row["sl2_highest_weight"], row["multiplicity"]) for row in decomposition]
        group_certificate = stabilizer._connected_group_certificate(primitive, compact, point, derived_domains)
        representation = {
            "decomposition": "V_(0,-4) + 2 V_(1,-3) + V_(0,-2)",
            "irreducible_decomposition": decomposition,
            "su2_restriction": {"trivial_lines": 2, "standard_doublets": 2},
            "casimir_spectrum": {sp.sstr(value): multiplicity for value, multiplicity in casimir.eigenvals().items()},
            "projectors": projector_certificate,
            "pass": signature == expected_decomposition
            and projector_certificate["pass"]
            and aligned._negative_definite(killing),
        }
        derived_dimension = len(derived_domains)
        center_dimension = 1
    else:
        raise ValueError(f"unknown orbit {orbit!r}")

    primitive_named = {
        name: coefficient for name, coefficient in zip(compact_names, primitive, strict=True) if coefficient
    }
    expected_rank = 14 if orbit == "B9" else 11
    expected_stabilizer_dimension = 1 if orbit == "B9" else 4
    return {
        "mutation": mutation,
        "compact_tangent_rank": tangent_rank,
        "stabilizer_dimension": len(coefficients),
        "stabilizer_center_dimension": center_dimension,
        "stabilizer_derived_dimension": derived_dimension,
        "stabilizer_lie_algebra": "u(1)" if orbit == "B9" else "su(2)+u(1)",
        "connected_group": group_certificate,
        "primitive_center_named_coefficients": primitive_named,
        "point_fixed": point_fixed,
        "kernel_preserved": kernel_preserved,
        "representation_commutators_match": commutators_match,
        "real_kernel_dimension": len(adapted_basis),
        "complex_kernel_dimension": len(adapted_basis) // 2,
        "representation": representation,
        "pass": tangent_rank == expected_rank
        and len(coefficients) == expected_stabilizer_dimension
        and all(point_fixed)
        and all(kernel_preserved)
        and commutators_match
        and representation["pass"]
        and group_certificate["pass"],
    }


def _fixture_task(task: tuple[str, str, CoefficientFrame, str]) -> dict[str, Any]:
    orbit, fixture, coefficients, mutation = task
    point_mutation = mutation if mutation == "force_rank_one" else ""
    point = _point_from_coefficients(coefficients, point_mutation)
    invariants = _pair_invariants(point)
    gram_mutation = mutation if mutation == "drop_common_phase" else ""
    stationary = _gram_stationary(point, gram_mutation)
    if mutation in ("force_rank_one", "drop_common_phase"):
        return {
            "orbit": orbit,
            "fixture": fixture,
            "mutation": mutation,
            **invariants,
            "compact_gram_stationary": stationary,
            "pass": invariants["inside_B9"] and stationary,
        }
    representation_mutation = mutation if mutation in ("include_moving_direction", "perturb_fiber_action") else ""
    representation = _representation_check(point, orbit, representation_mutation)
    expected_membership = invariants["inside_B9"] if orbit == "B9" else invariants["inside_VB"]
    return {
        "orbit": orbit,
        "fixture": fixture,
        "mutation": mutation,
        **invariants,
        "compact_gram_stationary": stationary,
        "left_nullity": symmetry.equations.nullity(point),
        "stabilizer_representation": representation,
        "pass": expected_membership
        and stationary
        and symmetry.equations.nullity(point) == 12
        and representation["pass"],
    }


def _load_inputs() -> tuple[dict[str, str], dict[str, Any]]:
    bindings = (
        ("kernel_symmetry", KERNEL_SYMMETRY_RESULT, KERNEL_SYMMETRY_SCRIPT, "a5-kernel-symmetry-v3"),
        (
            "nullity_sixteen_stabilizer",
            NULLITY_SIXTEEN_RESULT,
            NULLITY_SIXTEEN_SCRIPT,
            "a5-nullity-sixteen-stabilizer-representation-v1",
        ),
        ("v_orbit_moduli", V_MODULI_RESULT, V_MODULI_SCRIPT, "a5-v-compact-orbit-moduli-v1"),
    )
    digests: dict[str, str] = {}
    loaded: dict[str, Any] = {}
    for label, result_path, script_path, schema in bindings:
        result = json.loads(result_path.read_text(encoding="utf-8"))
        script_digest = hashlib.sha256(script_path.read_bytes()).hexdigest()
        _require(result.get("schema") == schema, f"{result_path.name} has an unexpected schema")
        _require(result.get("pass") is True, f"{result_path.name} does not pass")
        _require(result.get("script_sha256") == script_digest, f"{result_path.name} is stale against its producer")
        digests[f"{label}_result_sha256"] = hashlib.sha256(result_path.read_bytes()).hexdigest()
        digests[f"{label}_script_sha256"] = script_digest
        loaded[label] = result
    for helper in HELPER_SCRIPTS:
        digests[f"{helper.stem}_script_sha256"] = hashlib.sha256(helper.read_bytes()).hexdigest()
    return digests, loaded


def _fixtures() -> tuple[list[tuple[str, str, CoefficientFrame, str]], list[tuple[str, str, CoefficientFrame, str]]]:
    zero = (Fraction(0), Fraction(0))
    one = (Fraction(1), Fraction(0))
    two = (Fraction(2), Fraction(0))
    two_i = (Fraction(0), Fraction(2))
    b9 = [
        ("B9", "balanced_diagonal", (one, zero, zero, one), ""),
        ("B9", "unequal_diagonal", (two, zero, zero, one), ""),
        ("B9", "real_off_diagonal", (one, zero, one, two), ""),
        ("B9", "imaginary_off_diagonal", (one, zero, (Fraction(0), Fraction(1)), two), ""),
    ]
    vb = [
        ("VB", "lambda_zero", (one, zero, zero, zero), ""),
        ("VB", "lambda_two_i", (one, zero, two, zero), ""),
        ("VB", "lambda_minus_two", (one, zero, two_i, zero), ""),
        ("VB", "lambda_infinity", (zero, zero, one, zero), ""),
    ]
    return b9, vb


def _representation_signature(row: dict[str, Any]) -> tuple[Any, ...]:
    representation = row["stabilizer_representation"]["representation"]
    if row["orbit"] == "B9":
        return (representation["decomposition"], tuple(sorted(representation["weight_multiplicities"].items())))
    return (
        representation["decomposition"],
        tuple(
            (entry["central_weight"], entry["sl2_highest_weight"], entry["multiplicity"])
            for entry in representation["irreducible_decomposition"]
        ),
    )


def orbit_data_checks(mutation: str = "") -> dict[str, Any]:
    mutations = ("", "drop_common_phase", "force_rank_one", "include_moving_direction", "perturb_fiber_action")
    if mutation not in mutations:
        raise ValueError(f"unknown mutation {mutation!r}")
    input_digests, inputs = _load_inputs()
    b9_fixtures, vb_fixtures = _fixtures()
    if mutation == "drop_common_phase":
        task = (*b9_fixtures[2][:3], mutation)
        rows = [_fixture_task(task)]
        return {
            "mutation": mutation,
            "input_digests": input_digests,
            "rows": rows,
            "pass": all(row["pass"] for row in rows),
        }
    if mutation == "force_rank_one":
        task = (*b9_fixtures[0][:3], mutation)
        rows = [_fixture_task(task)]
        return {
            "mutation": mutation,
            "input_digests": input_digests,
            "rows": rows,
            "pass": all(row["pass"] for row in rows),
        }
    if mutation in ("include_moving_direction", "perturb_fiber_action"):
        task = (*vb_fixtures[0][:3], mutation)
        rows = [_fixture_task(task)]
        return {
            "mutation": mutation,
            "input_digests": input_digests,
            "rows": rows,
            "pass": all(row["pass"] for row in rows),
        }

    rows = symmetry.parallel.ordered_map(_fixture_task, [*b9_fixtures, *vb_fixtures], min_items=1)
    b9_rows = [row for row in rows if row["orbit"] == "B9"]
    vb_rows = [row for row in rows if row["orbit"] == "VB"]
    b9_representations_constant = len({_representation_signature(row) for row in b9_rows}) == 1
    vb_representations_constant = len({_representation_signature(row) for row in vb_rows}) == 1
    nullity_sixteen_rows = inputs["nullity_sixteen_stabilizer"]["stabilizer_representation"]["rows"]
    boundary_decomposition = nullity_sixteen_rows[0]["irreducible_decomposition"]
    vb_decomposition = vb_rows[0]["stabilizer_representation"]["representation"]["irreducible_decomposition"]
    boundary_restriction_matches = vb_decomposition == [
        row for row in boundary_decomposition if row["central_weight"] != "-I"
    ]
    return {
        "mutation": mutation,
        "input_digests": input_digests,
        "common_original_coordinate_model": ("put w=-i*v; then u dot u=w dot w=u dot w=0 and u cross w=0"),
        "B9": {
            "complete_compact_invariant": "H=(u,w)^*(u,w)/trace(H)",
            "compact_orbit_space": "positive-definite Hermitian 2x2 matrices of trace one, the open 3-ball",
            "unit_section_product": "G_2 x open(B^3)",
            "unit_section_homotopy_type": "G_2",
            "completeness_argument": (
                "Hermitian polar normalization turns (u,w) into an orthonormal totally null cross-zero frame; "
                "its four real columns are an oriented coassociative frame, and G_2 acts simply transitively on "
                "such frames"
            ),
            "connected_stabilizer": "U(1), the graph of the common phase circle inside G_2 x U(1)",
            "fiber_representation": "3 C_(-1) + 3 C_(-2)",
            "representations_constant": b9_representations_constant,
        },
        "VB": {
            "complete_compact_invariant": "rank-one H, equivalently lambda in CP^1 minus {+i,-i}",
            "compact_orbit_space": "CP^1 minus {+i,-i}, homotopy equivalent to C^*",
            "unit_section_product": "V_2(R^7) x (CP^1 minus {+i,-i}), noncanonically",
            "unit_section_fundamental_group": "Z",
            "connected_stabilizer": "U(2)=(SU(2) x U(1))/diagonal Z_2",
            "fiber_representation": "V_(0,-4) + 2 V_(1,-3) + V_(0,-2)",
            "su2_restriction": "2 V_0 + 2 V_1",
            "representations_constant": vb_representations_constant,
            "nullity_sixteen_boundary_adds": "V_(1,-1)",
            "boundary_restriction_matches": boundary_restriction_matches,
        },
        "unified_moduli_closure": (
            "B9 is the open Gram ball; VB is its rank-one boundary sphere with the two N_+/- points removed"
        ),
        "rows": rows,
        "pass": all(row["pass"] for row in rows)
        and b9_representations_constant
        and vb_representations_constant
        and boundary_restriction_matches,
    }


def build_result() -> dict[str, Any]:
    result = orbit_data_checks()
    return {
        "schema": "a5-isotropic-orbit-data-v1",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "isotropic_orbit_data": result,
        "pass": result["pass"],
    }


def self_test() -> None:
    baseline = orbit_data_checks()
    if not baseline["pass"]:
        raise RuntimeError("baseline B9/VB orbit-data check failed")
    phase_mutation = orbit_data_checks("drop_common_phase")
    if phase_mutation["pass"] or phase_mutation["rows"][0]["compact_gram_stationary"]:
        raise RuntimeError("one-block phase mutation survived the Gram-invariant check")
    rank_mutation = orbit_data_checks("force_rank_one")
    if rank_mutation["pass"] or rank_mutation["rows"][0]["inside_B9"]:
        raise RuntimeError("rank-one mutation survived the B9 membership check")
    moving_mutation = orbit_data_checks("include_moving_direction")
    if moving_mutation["pass"] or all(moving_mutation["rows"][0]["stabilizer_representation"]["point_fixed"]):
        raise RuntimeError("moving-generator mutation survived the stabilizer check")
    fiber_mutation = orbit_data_checks("perturb_fiber_action")
    if (
        fiber_mutation["pass"]
        or fiber_mutation["rows"][0]["stabilizer_representation"]["representation_commutators_match"]
    ):
        raise RuntimeError("fiber-action mutation survived the representation check")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        self_test()
        print("PASS: B9/VB compact-orbit and kernel-representation self-test")
    if arguments.out is not None:
        result = build_result()
        arguments.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {arguments.out}")
    if not arguments.self_test and arguments.out is None:
        parser.error("choose --self-test or --out")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
