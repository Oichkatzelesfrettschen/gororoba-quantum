"""Exact kernel transport and constant-symmetry checks for the A_5 rank strata.

The transport proved by the Pfaffian record is antilinear in the transported
input:

    phi(y x) = A(z, conjugate(z)) conjugate(phi(x)).

This script checks that formula, the formula without input conjugation, and
the action of J = L_(e_16) on every nullity-12 and nullity-16 orbit
representative from the regularity record. It also solves the constant-triple
Lie algebra that transports the full left-multiplication pencil.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

from sympy import ZZ
from sympy.polys.matrices import DomainMatrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REGULARITY = HERE.parent / "a5-strata-regularity"
EQUATIONS = HERE.parent / "a5-rank-strata-equations"
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(REGULARITY))
sys.path.insert(0, str(EQUATIONS))

import rederive_strata_equations as equations  # noqa: E402
import strata_regularity as regularity  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign, left_mult_matrix_exact  # noqa: E402

DIMENSION = 32
HALF_DIMENSION = 16
HIGH_NULLITY_ORBITS = ("B9", "V", "VB", "Vap", "Vam", "Np", "Nm")
EXPECTED_ORBIT_DIMENSIONS = {
    "B9": {"unit_section": 14, "cone": 15},
    "V": {"unit_section": 7, "cone": 8},
    "VB": {"unit_section": 11, "cone": 12},
    "Vap": {"unit_section": 7, "cone": 8},
    "Vam": {"unit_section": 7, "cone": 8},
    "Np": {"unit_section": 11, "cone": 12},
    "Nm": {"unit_section": 11, "cone": 12},
}
DOUBLY_PURE_INDICES = tuple(index for index in range(DIMENSION) if index not in (0, HALF_DIMENSION))
MATRIX_COORDINATES = DIMENSION * DIMENSION
LIE_UNKNOWN_COUNT = 2 * MATRIX_COORDINATES

RationalMatrix = tuple[tuple[Fraction, ...], ...]
LieTriple = tuple[RationalMatrix, RationalMatrix, RationalMatrix]


@dataclass(frozen=True)
class GaussianRational:
    """A Gaussian rational represented without floating-point conversion."""

    real: Fraction
    imaginary: Fraction

    def __add__(self, other: GaussianRational) -> GaussianRational:
        return GaussianRational(self.real + other.real, self.imaginary + other.imaginary)

    def __neg__(self) -> GaussianRational:
        return GaussianRational(-self.real, -self.imaginary)

    def __sub__(self, other: GaussianRational) -> GaussianRational:
        return self + (-other)

    def __mul__(self, other: GaussianRational) -> GaussianRational:
        return GaussianRational(
            self.real * other.real - self.imaginary * other.imaginary,
            self.real * other.imaginary + self.imaginary * other.real,
        )

    def conjugate(self) -> GaussianRational:
        return GaussianRational(self.real, -self.imaginary)

    def __bool__(self) -> bool:
        return self.real != 0 or self.imaginary != 0


@dataclass(frozen=True)
class QuadraticRational:
    """An exact element rational + radical * sqrt(3)."""

    rational: Fraction
    radical: Fraction

    def __add__(self, other: QuadraticRational) -> QuadraticRational:
        return QuadraticRational(self.rational + other.rational, self.radical + other.radical)

    def __neg__(self) -> QuadraticRational:
        return QuadraticRational(-self.rational, -self.radical)

    def __sub__(self, other: QuadraticRational) -> QuadraticRational:
        return self + (-other)

    def __mul__(self, other: QuadraticRational) -> QuadraticRational:
        return QuadraticRational(
            self.rational * other.rational + 3 * self.radical * other.radical,
            self.rational * other.radical + self.radical * other.rational,
        )

    def __truediv__(self, other: QuadraticRational) -> QuadraticRational:
        denominator = other.rational * other.rational - 3 * other.radical * other.radical
        if denominator == 0:
            raise ZeroDivisionError("division by zero in Q(sqrt(3))")
        return QuadraticRational(
            (self.rational * other.rational - 3 * self.radical * other.radical) / denominator,
            (self.radical * other.rational - self.rational * other.radical) / denominator,
        )

    def __bool__(self) -> bool:
        return self.rational != 0 or self.radical != 0


GAUSSIAN_ZERO = GaussianRational(Fraction(0), Fraction(0))
GAUSSIAN_I = GaussianRational(Fraction(0), Fraction(1))
GAUSSIAN_MINUS_I = GaussianRational(Fraction(0), Fraction(-1))
QUADRATIC_ZERO = QuadraticRational(Fraction(0), Fraction(0))
QUADRATIC_ONE = QuadraticRational(Fraction(1), Fraction(0))

QuadraticVector = tuple[QuadraticRational, ...]
QuadraticMatrix = tuple[QuadraticVector, ...]


def _gaussian_sum(values: Sequence[GaussianRational]) -> GaussianRational:
    total = GAUSSIAN_ZERO
    for value in values:
        total = total + value
    return total


def _gaussian_matrix_vector_product(
    matrix: Sequence[Sequence[GaussianRational]], vector: Sequence[GaussianRational]
) -> tuple[GaussianRational, ...]:
    return tuple(_gaussian_sum([entry * value for entry, value in zip(row, vector, strict=True)]) for row in matrix)


def _rational_matrix_vector_product(
    matrix: Sequence[Sequence[Fraction]], vector: Sequence[Fraction]
) -> tuple[Fraction, ...]:
    return tuple(sum((entry * value for entry, value in zip(row, vector, strict=True)), Fraction(0)) for row in matrix)


def _gaussian_rank(matrix: Sequence[Sequence[GaussianRational]]) -> int:
    """Complex rank from the rank of the rational realification."""
    order = len(matrix)
    realification = [[entry.real for entry in row] + [-entry.imaginary for entry in row] for row in matrix] + [
        [entry.imaginary for entry in row] + [entry.real for entry in row] for row in matrix
    ]
    rational_rank = equations.qrank(realification)
    if rational_rank % 2:
        raise ArithmeticError(f"Gaussian matrix realification has odd rank {rational_rank}")
    if any(len(row) != order for row in matrix):
        raise ValueError("Gaussian matrix must be square")
    return rational_rank // 2


def _phi(vector: Sequence[Fraction]) -> tuple[GaussianRational, ...]:
    """phi(r, s) = r + i conjugate(s) for x = (r, s) in A_5."""
    if len(vector) != DIMENSION:
        raise ValueError(f"A_5 vector must have {DIMENSION} coordinates")
    return tuple(
        GaussianRational(vector[index], vector[HALF_DIMENSION + index] * (1 if index == 0 else -1))
        for index in range(HALF_DIMENSION)
    )


def _bordered_matrix(y: Sequence[Fraction]) -> tuple[tuple[GaussianRational, ...], ...]:
    """A(z, conjugate(z)) for z_k = y_k + i y_(16+k), k = 1..15."""
    z = tuple(GaussianRational(y[index], y[HALF_DIMENSION + index]) for index in range(1, HALF_DIMENSION))
    conjugate_z = tuple(value.conjugate() for value in z)
    cross_rows: list[tuple[GaussianRational, ...]] = []
    for row_index in range(1, HALF_DIMENSION):
        row: list[GaussianRational] = []
        for column_index in range(1, HALF_DIMENSION):
            product_index = row_index ^ column_index
            row.append(
                GAUSSIAN_ZERO
                if product_index == 0
                else GaussianRational(
                    Fraction(cd_sign(HALF_DIMENSION, product_index, column_index)) * z[product_index - 1].real,
                    Fraction(cd_sign(HALF_DIMENSION, product_index, column_index)) * z[product_index - 1].imaginary,
                )
            )
        cross_rows.append(tuple(row))
    return (tuple([GAUSSIAN_ZERO, *(-value for value in conjugate_z)]),) + tuple(
        tuple([conjugate_z[row_index], *cross_rows[row_index]]) for row_index in range(HALF_DIMENSION - 1)
    )


def _kernel_vector_check(
    item: tuple[
        tuple[tuple[Fraction, ...], ...],
        tuple[tuple[Fraction, ...], ...],
        tuple[tuple[GaussianRational, ...], ...],
        tuple[Fraction, ...],
    ],
) -> dict[str, bool]:
    left_matrix, j_matrix, bordered, kernel_vector = item
    phi_vector = _phi(kernel_vector)
    conjugate_phi_vector = tuple(value.conjugate() for value in phi_vector)
    j_vector = _rational_matrix_vector_product(j_matrix, kernel_vector)
    phi_j_vector = _phi(j_vector)
    conjugate_phi_j_vector = tuple(value.conjugate() for value in phi_j_vector)
    return {
        "left_kernel": not any(_rational_matrix_vector_product(left_matrix, kernel_vector)),
        "transport_conjugated": not any(_gaussian_matrix_vector_product(bordered, conjugate_phi_vector)),
        "transport_unconjugated": not any(_gaussian_matrix_vector_product(bordered, phi_vector)),
        "j_preserves_kernel": not any(_rational_matrix_vector_product(left_matrix, j_vector)),
        "phi_j_equals_i_phi": phi_j_vector == tuple(GAUSSIAN_I * value for value in phi_vector),
        "conjugate_phi_j_equals_minus_i_conjugate_phi": conjugate_phi_j_vector
        == tuple(GAUSSIAN_MINUS_I * value for value in conjugate_phi_vector),
    }


def _representative_check(item: tuple[str, str]) -> dict[str, Any]:
    orbit, mutation = item
    split_point = [Fraction(value) for value in regularity.REPS[orbit]]
    y = tuple(equations.y_from_split(split_point))
    left_matrix = tuple(tuple(row) for row in left_mult_matrix_exact(DIMENSION, y))
    j_vector = [Fraction(0)] * DIMENSION
    j_vector[HALF_DIMENSION] = Fraction(-1 if mutation == "wrong_j_phase" else 1)
    j_matrix = tuple(tuple(row) for row in left_mult_matrix_exact(DIMENSION, j_vector))
    bordered = _bordered_matrix(y)
    kernel_basis = [tuple(row) for row in equations.nullspace(left_matrix)]
    vector_items = [(left_matrix, j_matrix, bordered, vector) for vector in kernel_basis]
    vector_checks = parallel.ordered_map(_kernel_vector_check, vector_items, min_items=1)
    real_nullity = len(kernel_basis)
    complex_nullity = HALF_DIMENSION - _gaussian_rank(bordered)
    transport_failures = sum(
        not row["transport_unconjugated" if mutation == "omit_input_conjugation" else "transport_conjugated"]
        for row in vector_checks
    )
    row_pass = (
        real_nullity == 2 * complex_nullity
        and transport_failures == 0
        and all(row["left_kernel"] and row["j_preserves_kernel"] for row in vector_checks)
        and all(row["phi_j_equals_i_phi"] for row in vector_checks)
        and all(row["conjugate_phi_j_equals_minus_i_conjugate_phi"] for row in vector_checks)
    )
    return {
        "orbit": orbit,
        "real_nullity": real_nullity,
        "complex_nullity": complex_nullity,
        "kernel_basis_vectors": real_nullity,
        "transport_with_input_conjugation": all(row["transport_conjugated"] for row in vector_checks),
        "transport_without_input_conjugation": all(row["transport_unconjugated"] for row in vector_checks),
        "transport_failures": transport_failures,
        "j_preserves_kernel": all(row["j_preserves_kernel"] for row in vector_checks),
        "phi_j_equals_i_phi": all(row["phi_j_equals_i_phi"] for row in vector_checks),
        "conjugate_phi_j_equals_minus_i_conjugate_phi": all(
            row["conjugate_phi_j_equals_minus_i_conjugate_phi"] for row in vector_checks
        ),
        "pass": row_pass,
    }


def representative_kernel_checks(mutation: str = "") -> dict[str, Any]:
    """Check the transport and J action on the seven representatives of nullity at least 12."""
    if mutation not in ("", "omit_input_conjugation", "wrong_j_phase"):
        raise ValueError(f"unknown mutation {mutation!r}")
    items = [(orbit, mutation) for orbit in HIGH_NULLITY_ORBITS]
    rows = parallel.ordered_map(_representative_check, items, min_items=1)
    return {"mutation": mutation, "rows": rows, "pass": all(row["pass"] for row in rows)}


# ---------------------------------------------------------------------------------------------------------------
# Constant kernel-pencil symmetries


def _structure_sign(left_index: int, right_index: int, mutation: str) -> int:
    sign = cd_sign(DIMENSION, left_index, right_index)
    if mutation == "flip_structure_sign" and (left_index, right_index) == (1, 2):
        return -sign
    return sign


def _add_coefficient(row: dict[int, int], column: int, value: int) -> None:
    updated = row.get(column, 0) + value
    if updated:
        row[column] = updated
    else:
        row.pop(column, None)


def _matrix_difference_coefficients(
    base_index: int, row_index: int, column_index: int, mutation: str
) -> dict[int, int]:
    """Coefficients of (H' L_p - L_p H)[row, column] in the 2,048 H/H' unknowns."""
    coefficients: dict[int, int] = {}
    left_sign = _structure_sign(base_index, column_index, mutation)
    prime_column = base_index ^ column_index
    _add_coefficient(
        coefficients,
        MATRIX_COORDINATES + row_index * DIMENSION + prime_column,
        left_sign,
    )
    domain_row = base_index ^ row_index
    domain_sign = _structure_sign(base_index, domain_row, mutation)
    _add_coefficient(coefficients, domain_row * DIMENSION + column_index, -domain_sign)
    return coefficients


def _lie_constraint_block(item: tuple[int, str]) -> tuple[dict[int, int], ...]:
    """Eliminate G for one basis element of the doubly pure base."""
    base_index, mutation = item
    rows: list[dict[int, int]] = []

    # The first column of L_(G e_p) is G e_p. Doubly pure output forces its scalar coordinates to vanish.
    for excluded_row in (0, HALF_DIMENSION):
        rows.append(_matrix_difference_coefficients(base_index, excluded_row, 0, mutation))

    # Every remaining column of a left-multiplication matrix is fixed by that first column.
    for column_index in range(1, DIMENSION):
        for row_index in range(DIMENSION):
            row = _matrix_difference_coefficients(base_index, row_index, column_index, mutation)
            coefficient_index = row_index ^ column_index
            if coefficient_index in DOUBLY_PURE_INDICES:
                predicted = _matrix_difference_coefficients(base_index, coefficient_index, 0, mutation)
                prediction_sign = _structure_sign(coefficient_index, column_index, mutation)
                for unknown_index, value in predicted.items():
                    _add_coefficient(row, unknown_index, -prediction_sign * value)
            rows.append(row)
    if len(rows) != 994:
        raise ArithmeticError(f"constraint block has {len(rows)} rows instead of 994")
    return tuple(rows)


def _zero_matrix() -> RationalMatrix:
    return tuple(tuple(Fraction(0) for _ in range(DIMENSION)) for _ in range(DIMENSION))


def _identity_matrix() -> RationalMatrix:
    return tuple(
        tuple(Fraction(row_index == column_index) for column_index in range(DIMENSION))
        for row_index in range(DIMENSION)
    )


def _basis_left_matrix(left_index: int, mutation: str = "") -> RationalMatrix:
    return tuple(
        tuple(
            Fraction(_structure_sign(left_index, column_index, mutation))
            if row_index == (left_index ^ column_index)
            else Fraction(0)
            for column_index in range(DIMENSION)
        )
        for row_index in range(DIMENSION)
    )


def _basis_right_matrix(right_index: int, mutation: str = "") -> RationalMatrix:
    return tuple(
        tuple(
            Fraction(_structure_sign(column_index, right_index, mutation))
            if row_index == (column_index ^ right_index)
            else Fraction(0)
            for column_index in range(DIMENSION)
        )
        for row_index in range(DIMENSION)
    )


def _matrix_add(first: RationalMatrix, second: RationalMatrix) -> RationalMatrix:
    return tuple(
        tuple(first[row_index][column_index] + second[row_index][column_index] for column_index in range(DIMENSION))
        for row_index in range(DIMENSION)
    )


def _matrix_scale(matrix: RationalMatrix, scalar: int) -> RationalMatrix:
    return tuple(tuple(scalar * entry for entry in row) for row in matrix)


def _restrict_base_matrix(matrix: RationalMatrix) -> RationalMatrix:
    return tuple(
        tuple(
            matrix[row_index][column_index]
            if row_index in DOUBLY_PURE_INDICES and column_index in DOUBLY_PURE_INDICES
            else Fraction(0)
            for column_index in range(DIMENSION)
        )
        for row_index in range(DIMENSION)
    )


def _matrix_product(first: RationalMatrix, second: RationalMatrix) -> RationalMatrix:
    product = [[Fraction(0) for _ in range(DIMENSION)] for _ in range(DIMENSION)]
    second_nonzero_rows = [tuple((index, value) for index, value in enumerate(row) if value) for row in second]
    for row_index, row in enumerate(first):
        for middle_index, first_value in enumerate(row):
            if first_value:
                for column_index, second_value in second_nonzero_rows[middle_index]:
                    product[row_index][column_index] += first_value * second_value
    return tuple(tuple(row) for row in product)


def _matrix_commutator(first: RationalMatrix, second: RationalMatrix) -> RationalMatrix:
    first_second = _matrix_product(first, second)
    second_first = _matrix_product(second, first)
    return tuple(
        tuple(
            first_second[row_index][column_index] - second_first[row_index][column_index]
            for column_index in range(DIMENSION)
        )
        for row_index in range(DIMENSION)
    )


def _triple_commutator(first: LieTriple, second: LieTriple) -> LieTriple:
    return tuple(_matrix_commutator(first[index], second[index]) for index in range(3))  # type: ignore[return-value]


def _flattened_commutator(pair: tuple[LieTriple, LieTriple]) -> tuple[Fraction, ...]:
    return _flatten_triple(_triple_commutator(pair[0], pair[1]))


def _flatten_matrix(matrix: RationalMatrix) -> tuple[Fraction, ...]:
    return tuple(entry for row in matrix for entry in row)


def _flatten_triple(triple: LieTriple) -> tuple[Fraction, ...]:
    return tuple(entry for matrix in triple for row in matrix for entry in row)


def _matrix_from_flat(values: Sequence[Fraction]) -> RationalMatrix:
    if len(values) != MATRIX_COORDINATES:
        raise ValueError(f"matrix requires {MATRIX_COORDINATES} entries, got {len(values)}")
    return tuple(
        tuple(values[row_index * DIMENSION + column_index] for column_index in range(DIMENSION))
        for row_index in range(DIMENSION)
    )


def _fraction_from_sympy(value: Any) -> Fraction:
    numerator, denominator = value.as_numer_denom()
    return Fraction(int(numerator), int(denominator))


def _derive_base_matrix(domain: RationalMatrix, codomain: RationalMatrix, mutation: str) -> RationalMatrix:
    base = [[Fraction(0) for _ in range(DIMENSION)] for _ in range(DIMENSION)]
    for base_index in DOUBLY_PURE_INDICES:
        for output_index in DOUBLY_PURE_INDICES:
            base[output_index][base_index] = (
                codomain[output_index][base_index]
                - _structure_sign(base_index, base_index ^ output_index, mutation)
                * domain[base_index ^ output_index][0]
            )
    return tuple(tuple(row) for row in base)


def _solve_lie_triples(mutation: str) -> tuple[tuple[LieTriple, ...], int, int]:
    blocks = parallel.ordered_map(
        _lie_constraint_block,
        [(base_index, mutation) for base_index in DOUBLY_PURE_INDICES],
        min_items=1,
    )
    entries: dict[tuple[int, int], int] = {}
    row_index = 0
    for block in blocks:
        for row in block:
            for column_index, value in row.items():
                entries[(row_index, column_index)] = value
            row_index += 1
    constraint_matrix = DomainMatrix.from_dok(entries, (row_index, LIE_UNKNOWN_COUNT), ZZ).to_field()
    nullspace = constraint_matrix.nullspace().to_Matrix().tolist()
    triples: list[LieTriple] = []
    for solution_row in nullspace:
        values = tuple(_fraction_from_sympy(value) for value in solution_row)
        domain = _matrix_from_flat(values[:MATRIX_COORDINATES])
        codomain = _matrix_from_flat(values[MATRIX_COORDINATES:])
        base = _derive_base_matrix(domain, codomain, mutation)
        triples.append((base, domain, codomain))
    return tuple(triples), row_index, len(entries)


def _octonion_derivation_triples() -> tuple[LieTriple, ...]:
    octonion_table = [[cd_sign(8, left_index, right_index) for right_index in range(8)] for left_index in range(8)]
    derivations = equations.derivations(octonion_table)
    triples: list[LieTriple] = []
    for derivation in derivations:
        extended = [[Fraction(0) for _ in range(DIMENSION)] for _ in range(DIMENSION)]
        for block_index in range(4):
            for row_index in range(8):
                for column_index in range(8):
                    extended[8 * block_index + row_index][8 * block_index + column_index] = derivation[row_index][
                        column_index
                    ]
        extended_matrix = tuple(tuple(row) for row in extended)
        triples.append((extended_matrix, extended_matrix, extended_matrix))
    if len(triples) != 14:
        raise ArithmeticError(f"octonion derivation algebra has dimension {len(triples)} instead of 14")
    return tuple(triples)


def _expected_lie_triples(mutation: str) -> tuple[tuple[str, LieTriple], ...]:
    zero = _zero_matrix()
    identity = _identity_matrix()
    left_j = _basis_left_matrix(HALF_DIMENSION, mutation)
    right_j = _basis_right_matrix(HALF_DIMENSION, mutation)
    base_identity = _restrict_base_matrix(identity)
    base_j = _restrict_base_matrix(left_j)
    named: list[tuple[str, LieTriple]] = [
        (f"compact_g2_{index + 1}", triple) for index, triple in enumerate(_octonion_derivation_triples())
    ]
    named.extend(
        [
            ("base_scaling", (base_identity, zero, identity)),
            ("domain_scaling", (zero, identity, identity)),
            ("vertical_j_phase", (zero, left_j, _matrix_scale(left_j, -1))),
            ("base_phase_lift", (base_j, right_j, _matrix_add(left_j, right_j))),
        ]
    )
    return tuple(named)


def _verify_lie_triple(item: tuple[LieTriple, str]) -> bool:
    """Check every coefficient of L_(G e_p) + L_p H = H' L_p."""
    (base, domain, codomain), mutation = item
    for base_index in DOUBLY_PURE_INDICES:
        for row_index in range(DIMENSION):
            for column_index in range(DIMENSION):
                output_index = row_index ^ column_index
                base_term = base[output_index][base_index] * _structure_sign(output_index, column_index, mutation)
                domain_term = (
                    _structure_sign(base_index, base_index ^ row_index, mutation)
                    * domain[base_index ^ row_index][column_index]
                )
                codomain_term = codomain[row_index][base_index ^ column_index] * _structure_sign(
                    base_index, column_index, mutation
                )
                if base_term + domain_term != codomain_term:
                    return False
    return True


def _boost_base_matrix() -> RationalMatrix:
    """Real form of the split-coordinate boost u' <-> v'."""
    boost = [[Fraction(0) for _ in range(DIMENSION)] for _ in range(DIMENSION)]
    for octonion_index in range(1, 8):
        upper_index = 8 + octonion_index
        boost[octonion_index][HALF_DIMENSION + upper_index] = Fraction(1)
        boost[HALF_DIMENSION + octonion_index][upper_index] = Fraction(-1)
        boost[upper_index][HALF_DIMENSION + octonion_index] = Fraction(-1)
        boost[HALF_DIMENSION + upper_index][octonion_index] = Fraction(1)
    return tuple(tuple(row) for row in boost)


def _rank(vectors: Sequence[Sequence[Fraction]]) -> int:
    return equations.qrank(vectors) if vectors else 0


def _center_commutator_block(
    item: tuple[int, LieTriple, tuple[LieTriple, ...]],
) -> tuple[int, tuple[tuple[int, int, int], ...]]:
    """Return the sparse center constraints contributed by one fixed triple."""
    fixed_index, fixed, triples = item
    commutator_vectors = [_flatten_triple(_triple_commutator(candidate, fixed)) for candidate in triples]
    entries: list[tuple[int, int, int]] = []
    for coordinate_index in range(3 * MATRIX_COORDINATES):
        for candidate_index, commutator_vector in enumerate(commutator_vectors):
            value = commutator_vector[coordinate_index]
            if value.denominator != 1:
                raise ArithmeticError("expected integral commutator coefficient")
            if value:
                entries.append((coordinate_index, candidate_index, value.numerator))
    return fixed_index, tuple(entries)


def _center_dimension(triples: Sequence[LieTriple]) -> int:
    triple_tuple = tuple(triples)
    blocks = parallel.ordered_map(
        _center_commutator_block,
        [(fixed_index, fixed, triple_tuple) for fixed_index, fixed in enumerate(triple_tuple)],
        min_items=1,
    )
    entries: dict[tuple[int, int], int] = {}
    rows_per_block = 3 * MATRIX_COORDINATES
    for fixed_index, block_entries in blocks:
        row_offset = fixed_index * rows_per_block
        for coordinate_index, candidate_index, value in block_entries:
            entries[(row_offset + coordinate_index, candidate_index)] = value
    row_count = len(triple_tuple) * rows_per_block
    center = DomainMatrix.from_dok(entries, (row_count, len(triple_tuple)), ZZ).to_field().nullspace()
    return center.shape[0]


def _orbit_dimension_task(
    item: tuple[str, tuple[RationalMatrix, ...]],
) -> tuple[str, dict[str, int]]:
    """Compute the compact and radially extended tangent ranks at one named representative."""
    orbit, base_generators = item
    point = tuple(equations.y_from_split([Fraction(value) for value in regularity.REPS[orbit]]))
    tangent_vectors = [_rational_matrix_vector_product(generator, point) for generator in base_generators]
    radial_vector = _rational_matrix_vector_product(_identity_matrix(), point)
    return orbit, {
        "unit_section": _rank(tangent_vectors),
        "cone": _rank([*tangent_vectors, radial_vector]),
    }


def _orbit_dimensions(base_generators: Sequence[RationalMatrix]) -> dict[str, dict[str, int]]:
    generator_tuple = tuple(base_generators)
    rows = parallel.ordered_map(
        _orbit_dimension_task,
        [(orbit, generator_tuple) for orbit in HIGH_NULLITY_ORBITS],
        min_items=1,
    )
    return dict(rows)


@lru_cache(maxsize=2)
def lie_algebra_checks(mutation: str = "") -> dict[str, Any]:
    """Solve the constant-triple kernel-pencil symmetry algebra over the rationals."""
    if mutation not in ("", "flip_structure_sign"):
        raise ValueError(f"unknown mutation {mutation!r}")

    if mutation:
        expected_named = _expected_lie_triples(mutation)
        expected_verified = parallel.ordered_map(
            _verify_lie_triple,
            [(triple, mutation) for _name, triple in expected_named],
            min_items=1,
        )
        return {
            "mutation": mutation,
            "control_scope": "explicit triples against the altered multiplication tensor",
            "all_expected_triples_verified": all(expected_verified),
            "expected_triple_verification": {
                name: verified for (name, _triple), verified in zip(expected_named, expected_verified, strict=True)
            },
            "pass": False,
        }

    solution_triples, constraint_rows, constraint_nonzeros = _solve_lie_triples(mutation)
    expected_named = _expected_lie_triples(mutation)
    expected_triples = tuple(triple for _name, triple in expected_named)
    solution_verified = parallel.ordered_map(
        _verify_lie_triple, [(triple, mutation) for triple in solution_triples], min_items=1
    )
    expected_verified = parallel.ordered_map(
        _verify_lie_triple, [(triple, mutation) for triple in expected_triples], min_items=1
    )

    solution_vectors = [_flatten_triple(triple) for triple in solution_triples]
    expected_vectors = [_flatten_triple(triple) for triple in expected_triples]
    solution_dimension = _rank(solution_vectors)
    expected_dimension = _rank(expected_vectors)
    combined_dimension = _rank([*solution_vectors, *expected_vectors])
    base_vectors = [_flatten_matrix(triple[0]) for triple in solution_triples]
    domain_vectors = [_flatten_matrix(triple[1]) for triple in solution_triples]
    base_projection_dimension = _rank(base_vectors)
    domain_projection_dimension = _rank(domain_vectors)
    boost = _flatten_matrix(_boost_base_matrix())
    boost_extension_dimension = _rank([*base_vectors, boost])
    expected_span_equals_solution = (
        solution_dimension == expected_dimension == combined_dimension == len(expected_triples)
    )

    pairs = [
        (expected_triples[first], expected_triples[second])
        for first in range(len(expected_triples))
        for second in range(first + 1, len(expected_triples))
    ]
    expected_commutators = parallel.ordered_map(_flattened_commutator, pairs, min_items=1)
    derived_dimension = _rank(expected_commutators)
    center_dimension = _center_dimension(expected_triples)
    compact_base_generators = [triple[0] for triple in expected_triples[:14]] + [expected_triples[-1][0]]
    orbit_dimensions = _orbit_dimensions(compact_base_generators)

    all_solution_verified = all(solution_verified)
    all_expected_verified = all(expected_verified)
    baseline_pass = (
        solution_dimension == 18
        and base_projection_dimension == 16
        and solution_dimension - base_projection_dimension == 2
        and domain_projection_dimension == 17
        and constraint_rows == 29_820
        and constraint_nonzeros == 115_440
        and all_solution_verified
        and all_expected_verified
        and expected_span_equals_solution
        and boost_extension_dimension == base_projection_dimension + 1
        and center_dimension == 4
        and derived_dimension == 14
        and orbit_dimensions == EXPECTED_ORBIT_DIMENSIONS
    )
    return {
        "mutation": mutation,
        "constraint_rows": constraint_rows,
        "constraint_unknowns": LIE_UNKNOWN_COUNT,
        "constraint_nonzero_coefficients": constraint_nonzeros,
        "dimension": solution_dimension,
        "base_projection_dimension": base_projection_dimension,
        "domain_projection_dimension": domain_projection_dimension,
        "vertical_dimension": solution_dimension - base_projection_dimension,
        "expected_span_dimension": expected_dimension,
        "center_dimension": center_dimension,
        "derived_algebra_dimension": derived_dimension,
        "decomposition": {
            "compact_g2": 14,
            "base_scaling": 1,
            "domain_scaling": 1,
            "vertical_j_phase": 1,
            "base_phase_lift": 1,
        },
        "all_solution_basis_triples_verified": all_solution_verified,
        "all_expected_triples_verified": all_expected_verified,
        "expected_triple_verification": {
            name: verified for (name, _triple), verified in zip(expected_named, expected_verified, strict=True)
        },
        "expected_span_equals_solution": expected_span_equals_solution,
        "boost_lifts": boost_extension_dimension == base_projection_dimension,
        "boost_base_rank_with_projection": boost_extension_dimension,
        "orbit_dimensions": orbit_dimensions,
        "pass": baseline_pass if not mutation else False,
    }


# ---------------------------------------------------------------------------------------------------------------
# Visible finite component symmetries


def _quadratic_identity(dimension: int) -> QuadraticMatrix:
    return tuple(
        tuple(QUADRATIC_ONE if row_index == column_index else QUADRATIC_ZERO for column_index in range(dimension))
        for row_index in range(dimension)
    )


def _quadratic_matrix_product(first: QuadraticMatrix, second: QuadraticMatrix) -> QuadraticMatrix:
    dimension = len(first)
    product = [[QUADRATIC_ZERO for _ in range(dimension)] for _ in range(dimension)]
    second_nonzero_rows = [tuple((index, value) for index, value in enumerate(row) if value) for row in second]
    for row_index, row in enumerate(first):
        for middle_index, first_value in enumerate(row):
            if first_value:
                for column_index, second_value in second_nonzero_rows[middle_index]:
                    product[row_index][column_index] = product[row_index][column_index] + first_value * second_value
    return tuple(tuple(row) for row in product)


def _quadratic_matrix_power(matrix: QuadraticMatrix, exponent: int) -> QuadraticMatrix:
    if exponent < 0:
        raise ValueError("matrix exponent must be nonnegative")
    result = _quadratic_identity(len(matrix))
    for _factor in range(exponent):
        result = _quadratic_matrix_product(result, matrix)
    return result


def _lower_epsilon() -> QuadraticMatrix:
    return tuple(
        tuple(
            QuadraticRational(Fraction(1 if column_index < 8 else -1), Fraction(0))
            if row_index == column_index
            else QUADRATIC_ZERO
            for column_index in range(HALF_DIMENSION)
        )
        for row_index in range(HALF_DIMENSION)
    )


def _lower_psi(mutation: str) -> QuadraticMatrix:
    matrix = [[QUADRATIC_ZERO for _ in range(HALF_DIMENSION)] for _ in range(HALF_DIMENSION)]
    matrix[0][0] = QUADRATIC_ONE
    matrix[8][8] = QUADRATIC_ONE
    for octonion_index in range(1, 8):
        matrix[octonion_index][octonion_index] = QuadraticRational(Fraction(-1, 2), Fraction(0))
        matrix[8 + octonion_index][8 + octonion_index] = QuadraticRational(Fraction(-1, 2), Fraction(0))
        radical_sign = -1 if mutation == "break_lower_psi" and octonion_index == 1 else 1
        matrix[octonion_index][8 + octonion_index] = QuadraticRational(Fraction(0), Fraction(radical_sign, 2))
        matrix[8 + octonion_index][octonion_index] = QuadraticRational(Fraction(0), Fraction(-1, 2))
    return tuple(tuple(row) for row in matrix)


def _extend_lower_matrix(matrix: QuadraticMatrix) -> QuadraticMatrix:
    extended = [[QUADRATIC_ZERO for _ in range(DIMENSION)] for _ in range(DIMENSION)]
    for block_offset in (0, HALF_DIMENSION):
        for row_index in range(HALF_DIMENSION):
            for column_index in range(HALF_DIMENSION):
                extended[block_offset + row_index][block_offset + column_index] = matrix[row_index][column_index]
    return tuple(tuple(row) for row in extended)


def _outer_reflection() -> QuadraticMatrix:
    return tuple(
        tuple(
            QuadraticRational(Fraction(1 if column_index < HALF_DIMENSION else -1), Fraction(0))
            if row_index == column_index
            else QUADRATIC_ZERO
            for column_index in range(DIMENSION)
        )
        for row_index in range(DIMENSION)
    )


def _finite_matrix(
    dimension: int,
    epsilon_exponent: int,
    psi_exponent: int,
    outer_exponent: int,
    mutation: str,
) -> QuadraticMatrix:
    lower = _quadratic_matrix_product(
        _quadratic_matrix_power(_lower_epsilon(), epsilon_exponent),
        _quadratic_matrix_power(_lower_psi(mutation), psi_exponent),
    )
    if dimension == HALF_DIMENSION:
        if outer_exponent:
            raise ValueError("the outer reflection belongs only to dimension 32")
        return lower
    if dimension != DIMENSION:
        raise ValueError(f"finite symmetry dimension must be 16 or 32, got {dimension}")
    extended = _extend_lower_matrix(lower)
    return _quadratic_matrix_product(_quadratic_matrix_power(_outer_reflection(), outer_exponent), extended)


def _quadratic_cd_multiply(
    dimension: int, first: Sequence[QuadraticRational], second: Sequence[QuadraticRational]
) -> QuadraticVector:
    product = [QUADRATIC_ZERO for _ in range(dimension)]
    for left_index, left_value in enumerate(first):
        if left_value:
            for right_index, right_value in enumerate(second):
                if right_value:
                    term = left_value * right_value
                    if cd_sign(dimension, left_index, right_index) < 0:
                        term = -term
                    output_index = left_index ^ right_index
                    product[output_index] = product[output_index] + term
    return tuple(product)


def _finite_automorphism_row(
    item: tuple[int, int, int, int, int, str],
) -> int:
    dimension, epsilon_exponent, psi_exponent, outer_exponent, left_index, mutation = item
    matrix = _finite_matrix(dimension, epsilon_exponent, psi_exponent, outer_exponent, mutation)
    columns = tuple(
        tuple(matrix[row_index][column_index] for row_index in range(dimension)) for column_index in range(dimension)
    )
    failures = 0
    for right_index in range(dimension):
        product_index = left_index ^ right_index
        product_sign = cd_sign(dimension, left_index, right_index)
        transformed_product = tuple(value if product_sign > 0 else -value for value in columns[product_index])
        if transformed_product != _quadratic_cd_multiply(dimension, columns[left_index], columns[right_index]):
            failures += 1
    return failures


def _quadratic_from_rational(matrix: RationalMatrix) -> QuadraticMatrix:
    return tuple(tuple(QuadraticRational(value, Fraction(0)) for value in row) for row in matrix)


def _quadratic_commutes(first: QuadraticMatrix, second: QuadraticMatrix) -> bool:
    return _quadratic_matrix_product(first, second) == _quadratic_matrix_product(second, first)


def _quadratic_rank(rows: Sequence[Sequence[QuadraticRational]]) -> int:
    if not rows:
        return 0
    reduced = [list(row) for row in rows]
    rank = 0
    for column_index in range(len(reduced[0])):
        pivot_index = next((index for index in range(rank, len(reduced)) if reduced[index][column_index]), None)
        if pivot_index is None:
            continue
        reduced[rank], reduced[pivot_index] = reduced[pivot_index], reduced[rank]
        pivot = reduced[rank][column_index]
        reduced[rank] = [value / pivot for value in reduced[rank]]
        for row_index in range(len(reduced)):
            if row_index != rank and reduced[row_index][column_index]:
                coefficient = reduced[row_index][column_index]
                reduced[row_index] = [
                    value - coefficient * pivot_value
                    for value, pivot_value in zip(reduced[row_index], reduced[rank], strict=True)
                ]
        rank += 1
        if rank == len(reduced):
            break
    return rank


def _quadratic_determinant(matrix: QuadraticMatrix, indices: Sequence[int]) -> QuadraticRational:
    reduced = [[matrix[row_index][column_index] for column_index in indices] for row_index in indices]
    determinant = QUADRATIC_ONE
    dimension = len(reduced)
    for column_index in range(dimension):
        pivot_index = next((index for index in range(column_index, dimension) if reduced[index][column_index]), None)
        if pivot_index is None:
            return QUADRATIC_ZERO
        if pivot_index != column_index:
            reduced[column_index], reduced[pivot_index] = reduced[pivot_index], reduced[column_index]
            determinant = -determinant
        pivot = reduced[column_index][column_index]
        determinant = determinant * pivot
        for row_index in range(column_index + 1, dimension):
            if reduced[row_index][column_index]:
                coefficient = reduced[row_index][column_index] / pivot
                for trailing_index in range(column_index, dimension):
                    reduced[row_index][trailing_index] = (
                        reduced[row_index][trailing_index] - coefficient * reduced[column_index][trailing_index]
                    )
    return determinant


def _quadratic_integer(value: QuadraticRational) -> int:
    if value.radical != 0 or value.rational.denominator != 1:
        raise ArithmeticError(f"expected an integer in Q(sqrt(3)), got {value}")
    return value.rational.numerator


def _flatten_quadratic_matrix(matrix: QuadraticMatrix) -> tuple[QuadraticRational, ...]:
    return tuple(value for row in matrix for value in row)


def _finite_automorphism_failures(mutation: str) -> tuple[int, int]:
    lower_elements = [(epsilon_exponent, psi_exponent, 0) for epsilon_exponent in range(2) for psi_exponent in range(3)]
    extended_elements = [
        (epsilon_exponent, psi_exponent, outer_exponent)
        for epsilon_exponent in range(2)
        for psi_exponent in range(3)
        for outer_exponent in range(2)
    ]
    lower_items = [
        (HALF_DIMENSION, epsilon_exponent, psi_exponent, 0, left_index, mutation)
        for epsilon_exponent, psi_exponent, _outer_exponent in lower_elements
        for left_index in range(HALF_DIMENSION)
    ]
    extended_items = [
        (DIMENSION, epsilon_exponent, psi_exponent, outer_exponent, left_index, mutation)
        for epsilon_exponent, psi_exponent, outer_exponent in extended_elements
        for left_index in range(DIMENSION)
    ]
    lower_failures = sum(parallel.ordered_map(_finite_automorphism_row, lower_items, min_items=1))
    extended_failures = sum(parallel.ordered_map(_finite_automorphism_row, extended_items, min_items=1))
    return lower_failures, extended_failures


@lru_cache(maxsize=2)
def finite_symmetry_checks(mutation: str = "") -> dict[str, Any]:
    """Verify the visible lower S3 and outer-reflection component subgroup."""
    if mutation not in ("", "break_lower_psi"):
        raise ValueError(f"unknown mutation {mutation!r}")

    lower_failures, extended_failures = _finite_automorphism_failures(mutation)
    if mutation:
        return {
            "mutation": mutation,
            "lower_automorphism_failures": lower_failures,
            "a5_extension_failures": extended_failures,
            "all_lower_s3_automorphisms": lower_failures == 0,
            "all_a5_extensions_verified": extended_failures == 0,
            "pass": False,
        }

    lower_identity = _quadratic_identity(HALF_DIMENSION)
    lower_epsilon = _lower_epsilon()
    lower_psi = _lower_psi("")
    lower_elements = tuple(
        _finite_matrix(HALF_DIMENSION, epsilon_exponent, psi_exponent, 0, "")
        for epsilon_exponent in range(2)
        for psi_exponent in range(3)
    )
    extended_lower_generators = (_extend_lower_matrix(lower_epsilon), _extend_lower_matrix(lower_psi))
    extended_lower_elements = tuple(_extend_lower_matrix(matrix) for matrix in lower_elements)
    outer = _outer_reflection()
    extended_identity = _quadratic_identity(DIMENSION)
    s3_relations = (
        _quadratic_matrix_power(lower_psi, 3) == lower_identity
        and _quadratic_matrix_power(lower_epsilon, 2) == lower_identity
        and _quadratic_matrix_product(lower_epsilon, lower_psi)
        == _quadratic_matrix_product(_quadratic_matrix_power(lower_psi, 2), lower_epsilon)
    )
    outer_relation = _quadratic_matrix_power(outer, 2) == extended_identity
    factors_commute = all(_quadratic_commutes(outer, generator) for generator in extended_lower_generators)

    expected_triples = tuple(triple for _name, triple in _expected_lie_triples(""))
    finite_generators_centralize_lie_algebra = all(
        _quadratic_commutes(generator, _quadratic_from_rational(matrix))
        for generator in extended_lower_generators
        for triple in expected_triples
        for matrix in triple
    )
    identity = _identity_matrix()
    left_j = _basis_left_matrix(HALF_DIMENSION)
    right_j = _basis_right_matrix(HALF_DIMENSION)
    center_domain_algebra = tuple(
        _quadratic_from_rational(matrix) for matrix in (identity, left_j, right_j, _matrix_product(left_j, right_j))
    )
    center_vectors = [_flatten_quadratic_matrix(matrix) for matrix in center_domain_algebra]
    center_rank = _quadratic_rank(center_vectors)
    lower_center_extension_ranks = [
        _quadratic_rank([*center_vectors, _flatten_quadratic_matrix(_extend_lower_matrix(matrix))])
        for matrix in lower_elements
    ]
    nonidentity_lower_outside = (
        center_rank == 4
        and lower_center_extension_ranks.count(4) == 1
        and lower_center_extension_ranks.count(5) == 5
        and finite_generators_centralize_lie_algebra
    )
    lower_base_determinants = [
        _quadratic_integer(_quadratic_determinant(matrix, DOUBLY_PURE_INDICES)) for matrix in extended_lower_elements
    ]
    outer_base_determinant = _quadratic_integer(_quadratic_determinant(outer, DOUBLY_PURE_INDICES))
    lower_s3_order = len(set(lower_elements))
    baseline_pass = (
        lower_failures == 0
        and extended_failures == 0
        and lower_s3_order == 6
        and s3_relations
        and outer_relation
        and factors_commute
        and nonidentity_lower_outside
        and lower_base_determinants == [1] * 6
        and outer_base_determinant == -1
    )
    return {
        "mutation": mutation,
        "lower_s3_order": lower_s3_order,
        "visible_component_cosets": 2 * lower_s3_order,
        "lower_automorphism_failures": lower_failures,
        "a5_extension_failures": extended_failures,
        "all_lower_s3_automorphisms": lower_failures == 0,
        "all_a5_extensions_verified": extended_failures == 0,
        "s3_relations": s3_relations,
        "outer_reflection_relation": outer_relation,
        "factors_commute": factors_commute,
        "finite_generators_centralize_lie_algebra": finite_generators_centralize_lie_algebra,
        "connected_center_domain_algebra_rank": center_rank,
        "lower_s3_center_extension_ranks": lower_center_extension_ranks,
        "nonidentity_lower_s3_outside_identity_component": nonidentity_lower_outside,
        "lower_s3_base_determinants": lower_base_determinants,
        "outer_reflection_base_determinant": outer_base_determinant,
        "classification_status": "visible subgroup, not an exhaustive component census",
        "pass": baseline_pass,
    }


def build_result() -> dict[str, Any]:
    checks = representative_kernel_checks()
    lie_algebra = lie_algebra_checks()
    finite_symmetries = finite_symmetry_checks()
    unconjugated_failures = sum(
        row["kernel_basis_vectors"] for row in checks["rows"] if not row["transport_without_input_conjugation"]
    )
    return {
        "schema": "a5-kernel-symmetry-v3",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "kernel_transport": {
            **checks,
            "proved_formula": "phi(y*x) = A(z, conjugate(z)) * conjugate(phi(x))",
            "program_formula": "phi(y*x) = A(z, conjugate(z)) * phi(x)",
            "program_formula_status": "refuted" if unconjugated_failures else "not refuted",
            "representatives_refuting_program_formula": [
                row["orbit"] for row in checks["rows"] if not row["transport_without_input_conjugation"]
            ],
        },
        "lie_algebra": lie_algebra,
        "finite_symmetries": finite_symmetries,
        "pass": checks["pass"] and unconjugated_failures > 0 and lie_algebra["pass"] and finite_symmetries["pass"],
    }


def _self_test_mutation_task(item: tuple[str, str]) -> tuple[str, dict[str, Any]]:
    """Build one independent mutation control for the parent self-test."""
    check, mutation = item
    if check == "representative":
        return mutation, representative_kernel_checks(mutation=mutation)
    if check == "lie_algebra":
        return mutation, lie_algebra_checks(mutation=mutation)
    if check == "finite_symmetry":
        return mutation, finite_symmetry_checks(mutation=mutation)
    raise ValueError(f"unknown self-test check {check!r}")


def self_test() -> None:
    baseline = representative_kernel_checks()
    if not baseline["pass"]:
        raise RuntimeError("baseline kernel transport or J check failed")
    lie_algebra = lie_algebra_checks()
    if not lie_algebra["pass"]:
        raise RuntimeError("constant-triple Lie algebra check failed")
    finite_symmetries = finite_symmetry_checks()
    if not finite_symmetries["pass"]:
        raise RuntimeError("visible finite symmetry check failed")

    mutations = dict(
        parallel.ordered_map(
            _self_test_mutation_task,
            [
                ("representative", "omit_input_conjugation"),
                ("representative", "wrong_j_phase"),
                ("lie_algebra", "flip_structure_sign"),
                ("finite_symmetry", "break_lower_psi"),
            ],
            min_items=1,
        )
    )
    missing_conjugation = mutations["omit_input_conjugation"]
    if missing_conjugation["pass"]:
        raise RuntimeError("transport mutation without input conjugation passed")
    wrong_j_phase = mutations["wrong_j_phase"]
    if wrong_j_phase["pass"]:
        raise RuntimeError("J-phase mutation passed")
    structure_mutation = mutations["flip_structure_sign"]
    if structure_mutation["all_expected_triples_verified"]:
        raise RuntimeError("multiplication-structure mutation preserved every expected Lie triple")
    finite_mutation = mutations["break_lower_psi"]
    if finite_mutation["all_lower_s3_automorphisms"]:
        raise RuntimeError("mutated lower order-three map remained an automorphism")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if args.check is not None and (args.self_test or args.out is not None):
        parser.error("--check cannot be combined with --self-test or --out")
    if not args.self_test and args.out is None and args.check is None:
        parser.error("choose --self-test, --out, or --check")
    if args.self_test:
        self_test()
        print("kernel transport and symmetry self-test: pass")
    if args.out is not None or args.check is not None:
        result = build_result()
        if not result["pass"]:
            raise RuntimeError("kernel transport or symmetry result failed")
        payload = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
        if args.check is not None:
            if payload != args.check.read_bytes():
                raise SystemExit(f"kernel_symmetry.py: fresh JSON differs byte-for-byte from {args.check}")
            print(f"kernel_symmetry.py: fresh JSON matches {args.check}")
        else:
            args.out.write_bytes(payload)
            print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
