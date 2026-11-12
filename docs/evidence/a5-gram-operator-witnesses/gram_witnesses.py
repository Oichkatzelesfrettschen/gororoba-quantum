"""Exact multiplication, Gram-filter and reduced-operator witnesses over Q and Q(i).

The record separates finite arithmetic checks from classification, topology and physical inference. Independent
items use parallel.ordered_map; the replay consumes deterministic named operands and finite enumerations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Any

import sympy as sp
from flint import fmpq, fmpq_mat

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
for directory in (
    ROOT / "gororoba_quantum",
    ROOT / "docs/evidence/a5-rank-strata-equations",
    ROOT / "docs/evidence/kaplansky-cd-mechanisms",
):
    sys.path.insert(0, str(directory))

import kaplansky_cd_replay as cancellation  # noqa: E402
import rederive_strata_equations as canonical  # noqa: E402

import cd_core  # noqa: E402
import cd_quantum_contracts as contracts  # noqa: E402
import kernel_limit_contracts as limits  # noqa: E402
import parallel  # noqa: E402

Terms = tuple[tuple[int, int], ...]
ComplexMatrix = tuple[Any, Any]
MAXIMAL: Terms = ((1, 1), (10, -1), (18, 1), (25, 1))
SOURCE_FILES = (
    "gororoba_quantum/cd_core.py",
    "gororoba_quantum/cd_quantum_contracts.py",
    "gororoba_quantum/parallel.py",
    "gororoba_quantum/kernel_limits.py",
    "gororoba_quantum/kernel_limit_contracts.py",
    "gororoba_quantum/four_support_rank.py",
    "docs/evidence/a5-rank-strata-equations/rederive_strata_equations.py",
    "docs/evidence/kaplansky-cd-mechanisms/kaplansky_cd_replay.py",
    "docs/notes/topics/strata-gauss-bottleneck.md",
    "docs/evidence/a5-gram-operator-witnesses/claim_definitions.json",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def rational_matrix(rows: Any) -> Any:
    return fmpq_mat([[fmpq(str(value)) for value in row] for row in rows])


def identity(dimension: int) -> Any:
    return fmpq_mat([[int(row == column) for column in range(dimension)] for row in range(dimension)])


def vector(dimension: int, terms: Terms) -> tuple[Fraction, ...]:
    values = [Fraction(0)] * dimension
    for index, coefficient in terms:
        values[index] += coefficient
    return tuple(values)


def left(dimension: int, terms: Terms) -> Any:
    return rational_matrix(cd_core.left_mult_matrix_exact(dimension, vector(dimension, terms)))


def right(dimension: int, terms: Terms) -> Any:
    values = vector(dimension, terms)
    return rational_matrix(
        [
            [values[row ^ column] * cd_core.cd_sign(dimension, column, row ^ column) for column in range(dimension)]
            for row in range(dimension)
        ]
    )


def trace(matrix: Any) -> Any:
    return sum((matrix[index, index] for index in range(matrix.nrows())), fmpq(0))


def embed(matrix: ComplexMatrix) -> Any:
    real, imaginary = matrix
    dimension = real.nrows()
    return fmpq_mat(
        [
            [real[row, column] for column in range(dimension)]
            + [-imaginary[row, column] for column in range(dimension)]
            for row in range(dimension)
        ]
        + [
            [imaginary[row, column] for column in range(dimension)] + [real[row, column] for column in range(dimension)]
            for row in range(dimension)
        ]
    )


def complex_rank(matrix: ComplexMatrix) -> int:
    rank = int(embed(matrix).rank())
    require(rank % 2 == 0, "Gaussian rank has an odd realification rank")
    return rank // 2


def complex_product(first: ComplexMatrix, second: ComplexMatrix) -> ComplexMatrix:
    real, imaginary = first
    other_real, other_imaginary = second
    return real * other_real - imaginary * other_imaginary, real * other_imaginary + imaginary * other_real


def reduced(terms: Terms) -> tuple[ComplexMatrix, list[Any]]:
    values = vector(32, terms)
    coordinates = [canonical.GP(int(values[index]), int(values[16 + index])) for index in range(1, 16)]
    rows = canonical.cz_original(coordinates)
    return (
        fmpq_mat([[entry.re for entry in row] for row in rows]),
        fmpq_mat([[entry.im for entry in row] for row in rows]),
    ), coordinates


def rank_identity(terms: Terms) -> dict[str, Any]:
    matrix, coordinates = reduced(terms)
    real, imaginary = matrix
    border_real = fmpq_mat(16, 16)
    border_imaginary = fmpq_mat(16, 16)
    for row in range(15):
        border_real[0, row + 1], border_real[row + 1, 0] = -coordinates[row].re, coordinates[row].re
        border_imaginary[0, row + 1], border_imaginary[row + 1, 0] = coordinates[row].im, -coordinates[row].im
        for column in range(15):
            border_real[row + 1, column + 1] = real[row, column]
            border_imaginary[row + 1, column + 1] = imaginary[row, column]
    reduced_rank = complex_rank(matrix)
    bordered_rank = complex_rank((border_real, border_imaginary))
    real_nullity = 32 - int(left(32, terms).rank())
    require(real_nullity == 28 - 2 * reduced_rank, "reduced rank/nullity identity fails")
    require(32 - real_nullity == 2 * bordered_rank, "bordered real-rank identity fails")
    require(real_nullity != 29 - 2 * reduced_rank, "rank-offset mutation escaped")
    return {"terms": terms, "reduced_rank": reduced_rank, "bordered_rank": bordered_rank, "nullity": real_nullity}


def reduced_witness(terms: Terms) -> dict[str, Any]:
    matrix, _ = reduced(terms)
    powers = [15]
    current = matrix
    for _exponent in range(1, 4):
        powers.append(complex_rank(current))
        current = complex_product(current, matrix)
    require(powers[-1] == 0, "named reduced witness is not nilpotent of index at most three")
    blocks = []
    padded = [*powers, 0]
    for size in range(1, 4):
        blocks.extend([size] * (padded[size - 1] - 2 * padded[size] + padded[size + 1]))
    require(sum(blocks) == 15, "Jordan partition loses dimension")
    row = rank_identity(terms)
    row.update(
        {
            "power_ranks": powers,
            "jordan_blocks": sorted(blocks, reverse=True),
            "characteristic_polynomial": "lambda**15",
        }
    )
    return row


def scalar_witness(dimension: int) -> dict[str, Any]:
    terms = ((1, 1), (10, 1)) if dimension == 16 else (((1, 1), (18, 1)) if dimension == 32 else ((1, 1),))
    pure = left(dimension, terms)
    shifted = pure + identity(dimension)
    gram = pure.transpose() * pure
    require(pure.transpose() == -pure, "pure left multiplication is not skew")
    require(shifted.transpose() * shifted == gram + identity(dimension), "scalar-offset identity fails")
    altered = fmpq_mat(pure)
    altered[0, 1] = -altered[0, 1]
    require(altered.transpose() != -altered, "skew-sign mutation escaped")
    require(int(shifted.rank()) == dimension, "nonzero real scalar leaves a kernel")
    return {
        "dimension": dimension,
        "pure_nullity": dimension - int(pure.rank()),
        "shifted_nullity": 0,
        "scalar": "1",
        "gram_shift_identity": True,
        "skew_sign_mutation_detected": True,
    }


def phase_witness(case: tuple[int, int, int]) -> dict[str, Any]:
    dimension, first_index, second_index = case
    first = left(dimension, ((first_index, 1),))
    second = left(dimension, ((second_index, 1),))
    product = first.transpose() * second
    displacement = first_index ^ second_index
    symmetric = sum(
        product[index, index ^ displacement] == product[index ^ displacement, index]
        for index in range(dimension)
        if index < (index ^ displacement)
    )
    rows = []
    for cosine, sine in ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)), (Fraction(3, 5), Fraction(4, 5))):
        real = first + fmpq(str(cosine)) * second
        imaginary = fmpq(str(sine)) * second
        gram = (
            real.transpose() * real + imaginary.transpose() * imaginary,
            real.transpose() * imaginary - imaginary.transpose() * real,
        )
        expected: Counter[Fraction] = Counter()
        for value, multiplicity in (
            (2 + 2 * cosine, symmetric),
            (2 - 2 * cosine, symmetric),
            (2 + 2 * sine, dimension // 2 - symmetric),
            (2 - 2 * sine, dimension // 2 - symmetric),
        ):
            expected[value] += multiplicity
        for value, multiplicity in expected.items():
            actual = dimension - complex_rank((gram[0] - fmpq(str(value)) * identity(dimension), gram[1]))
            require(actual == multiplicity, "coefficient-phase spectral multiplicity differs")
        rows.append(
            {
                "cos": str(cosine),
                "sin": str(sine),
                "spectrum": {str(k): v for k, v in sorted(expected.items())},
                "nullity": dimension - complex_rank((real, imaginary)),
            }
        )
    bilinear = first.transpose() * first - second.transpose() * second
    hermitian = first.transpose() * first + second.transpose() * second
    require(bilinear != hermitian, "transpose-for-adjoint mutation escaped")
    require([rows[0]["nullity"], rows[1]["nullity"]] == [symmetric, dimension // 2 - symmetric], "phase swap fails")
    return {
        "dimension": dimension,
        "pair": [first_index, second_index],
        "symmetric_blocks": symmetric,
        "nullities_at_one_and_i": [rows[0]["nullity"], rows[1]["nullity"]],
        "phase_cases": rows,
        "bilinear_gram_mutation_detected": True,
    }


def projector_witness() -> dict[str, Any]:
    exact = cd_core.left_mult_matrix_exact(32, tuple(value / 2 for value in vector(32, MAXIMAL)))
    matrix = rational_matrix(exact)
    gram = matrix.transpose() * matrix
    unit = identity(32)
    spectrum = {str(value): 32 - int((gram - value * unit).rank()) for value in (0, 1, 2, 4)}
    require(sum(spectrum.values()) == 32, "named spectrum is incomplete")
    moments = [str(trace(gram**power)) for power in (1, 2, 3)]
    quadratic = unit - fmpq(3, 2) * gram + fmpq(1, 2) * gram**2
    certificate = contracts.kernel_projector(exact, (1, 2, 4))
    cubic = rational_matrix(certificate.projector)
    require(
        cubic == unit - fmpq(7, 4) * gram + fmpq(7, 8) * gram**2 - fmpq(1, 8) * gram**3,
        "cubic coefficient expansion differs",
    )
    require(quadratic * quadratic != quadratic and trace(quadratic) == 28, "quadratic counterexample disappeared")
    try:
        contracts.kernel_projector(exact, (1, 2))
    except ValueError:
        missing_rejected = True
    else:
        raise ValueError("missing positive Gram root was admitted")
    squared = gram * gram
    input_index = next(index for index in range(32) if gram[index, index] ** 2 != squared[index, index])
    moment_square = gram[input_index, input_index] ** 2
    second_moment = squared[input_index, input_index]
    require(moment_square != second_moment, "success-square counterexample disappeared")
    require(gram[0, 0] ** 2 == squared[0, 0], "identity-input equality control fails")
    vandermonde = fmpq_mat([[1, value, value**2] for value in (0, 1, 2, 4)])
    augmented = fmpq_mat([[1, value, value**2, int(value == 0)] for value in (0, 1, 2, 4)])
    require(vandermonde.rank() == 3 and augmented.rank() == 4, "degree-two interpolation unexpectedly exists")
    return {
        "operand": [[index, str(Fraction(coefficient, 2))] for index, coefficient in MAXIMAL],
        "spectrum": spectrum,
        "moments": moments,
        "quadratic_trace": str(trace(quadratic)),
        "quadratic_idempotent": False,
        "cubic_trace": str(trace(cubic)),
        "cubic_idempotent": cubic * cubic == cubic,
        "annihilation": matrix * cubic == fmpq_mat(32, 32),
        "missing_root_rejected": missing_rejected,
        "minimal_filter_degree": 3,
        "mean_squared": str(moment_square),
        "second_moment": str(second_moment),
        "moment_input_basis_index": input_index,
        "identity_input_has_equal_moments": True,
    }


def basis_witness(case: tuple[int, int]) -> dict[str, Any]:
    dimension, index = case
    matrix = left(dimension, ((index, 1),))
    unit = identity(dimension)
    require(matrix.transpose() * matrix == unit, "basis action loses orthogonality")
    require(index == 0 or matrix.transpose() == -matrix, "imaginary basis action loses skewness")
    if dimension <= 16:
        ordinary = left(2 * dimension, ((index, 1),))
        other = right(dimension, ((index, 1),))
        block = fmpq_mat(2 * dimension, 2 * dimension)
        for row in range(dimension):
            for column in range(dimension):
                block[row, column] = matrix[row, column]
                block[row + dimension, column + dimension] = other[row, column]
        require(ordinary == block, "ordinary-doubling block identity fails")
    for partner in range(dimension):
        expected = -2 if index == partner and index else (2 if index == partner == 0 else 0)
        if index == 0 and partner:
            expected = 2
        if partner == 0 and index:
            expected = 2
        product_sign = cd_core.cd_sign(dimension, index, partner) + cd_core.cd_sign(dimension, partner, index)
        require(product_sign == expected, "polarized quadratic identity fails")
    return {
        "dimension": dimension,
        "index": index,
        "signed_orthogonal": True,
        "pure_skew": index != 0,
        "ordinary_embedding": dimension <= 16,
        "quadratic_basis_pairs": dimension,
    }


def two_support_witness(case: tuple[int, int, int]) -> dict[str, Any]:
    dimension, first_index, second_index = case
    first, second = left(dimension, ((first_index, 1),)), left(dimension, ((second_index, 1),))
    mixed = first.transpose() * second
    displacement = first_index ^ second_index
    symmetric = sum(
        mixed[index, index ^ displacement] == mixed[index ^ displacement, index]
        for index in range(dimension)
        if index < (index ^ displacement)
    )
    rows = []
    unit = identity(dimension)
    for beta in (1, -1, 2, 3):
        matrix = first + beta * second
        gram = matrix.transpose() * matrix
        expected = ((1 + beta) ** 2, (1 - beta) ** 2, 1 + beta**2)
        polynomial = (gram - expected[0] * unit) * (gram - expected[1] * unit) * (gram - expected[2] * unit)
        require(polynomial == fmpq_mat(dimension, dimension), "two-support spectral polynomial fails")
        require(
            trace(gram**2) == dimension * (1 + beta**2) ** 2 + 8 * symmetric * beta**2,
            "second Gram moment identity fails",
        )
        require(all(gram[index, index] == 1 + beta**2 for index in range(dimension)), "basis intensity differs")
        require(dimension - int(matrix.rank()) == (symmetric if abs(beta) == 1 else 0), "two-support nullity differs")
        normalized = gram / 2
        if abs(beta) == 1:
            projector = unit - fmpq(3, 2) * normalized + fmpq(1, 2) * normalized**2
            require(
                projector * projector == projector and matrix * projector == fmpq_mat(dimension, dimension),
                "two-support quadratic filter fails",
            )
            require(trace(projector) == symmetric, "two-support projector loses complete kernel")
        rows.append({"beta": beta, "nullity": dimension - int(matrix.rank())})
    return {
        "dimension": dimension,
        "pair": [first_index, second_index],
        "symmetric_blocks": symmetric,
        "coefficients_checked": [1, -1, 2, 3],
        "nullities": [row["nullity"] for row in rows],
    }


def lift_witness(case: tuple[int, int, int, int, int]) -> dict[str, Any]:
    dimension, first_index, second_index, coefficient, sign = case
    operand = vector(dimension, ((first_index, 1), (second_index, coefficient)))
    imaginary_unit = vector(dimension, ((dimension // 2, 1),))
    high = cd_core.cd_multiply_exact(dimension, imaginary_unit, operand)
    lifted = (*operand, *(sign * value for value in high))
    nullity = dimension - int(left(dimension, ((first_index, 1), (second_index, coefficient))).rank())
    actual = 2 * dimension - int(rational_matrix(cd_core.left_mult_matrix_exact(2 * dimension, lifted)).rank())
    require(actual == nullity + dimension - 4, "perpendicular special-lift nullity differs")
    require(actual != 2 * nullity, "ordinary-embedding substitution escaped the special-lift check")
    return {
        "dimension": dimension,
        "pair": [first_index, second_index],
        "coefficient": coefficient,
        "sign": sign,
        "initial_nullity": nullity,
        "lifted_nullity": actual,
        "ordinary_embedding_substitution_detected": True,
    }


def inverse_witness(terms: Terms) -> dict[str, Any]:
    dimension = 32 if any(index >= 16 for index, _ in terms) else 16
    operand = vector(dimension, terms)
    norm = sum(value * value for value in operand)
    inverse = tuple((value if index == 0 else -value) / norm for index, value in enumerate(operand))
    matrix = sp.Matrix(cd_core.left_mult_matrix_exact(dimension, operand))
    frame = matrix.nullspace()
    one = (Fraction(1), *(Fraction(0) for _ in range(dimension - 1)))
    for kernel_vector in frame:
        offset = tuple(Fraction(str(value)) for value in kernel_vector)
        require(not any(cd_core.cd_multiply_exact(dimension, offset, operand)), "right annihilator differs")
        candidate = tuple(value + change for value, change in zip(inverse, offset, strict=True))
        require(
            cd_core.cd_multiply_exact(dimension, operand, candidate) == one
            and cd_core.cd_multiply_exact(dimension, candidate, operand) == one,
            "affine inverse offset fails",
        )
    require(cd_core.cd_multiply_exact(dimension, operand, inverse) == one, "canonical inverse fails")
    altered = tuple(-value for value in inverse)
    require(cd_core.cd_multiply_exact(dimension, operand, altered) != one, "inverse sign mutation escaped")
    require(
        left(dimension, terms).transpose() * left(dimension, terms)
        == right(dimension, terms).transpose() * right(dimension, terms),
        "left/right Gram matrices differ on a pure operand",
    )
    return {
        "dimension": dimension,
        "terms": terms,
        "nullity": len(frame),
        "inverse_basis_offsets_checked": len(frame),
        "inverse_sign_mutation_detected": True,
    }


def reduced_structure() -> dict[str, Any]:
    require(
        all(
            cd_core.cd_sign(16, row ^ column, column) == -cd_core.cd_sign(16, row ^ column, row)
            for row in range(1, 16)
            for column in range(1, 16)
            if row != column
        ),
        "C_z coefficient skewness fails",
    )
    matrix, _ = reduced(((1, 1), (18, 1)))
    real, imaginary = matrix
    require(real.transpose() == -real and imaginary.transpose() == -imaginary, "complex transpose skewness fails")
    require(imaginary != fmpq_mat(15, 15), "nonreal witness lost imaginary part")
    require((real.transpose(), -imaginary.transpose()) == (-real, imaginary), "adjoint identity fails")
    require((real.transpose(), -imaginary.transpose()) != (-real, -imaginary), "skew-Hermitian mutation escaped")
    matrix, _coordinates = reduced(MAXIMAL)
    real, imaginary = matrix
    diagonal = [canonical.ipow(index.bit_count(), 1, 0) for index in range(1, 16)]
    transformed = [
        [
            diagonal[row] * canonical.GP(int(real[row, column]), int(imaginary[row, column])) * diagonal[column]
            for column in range(15)
        ]
        for row in range(15)
    ]
    split = (
        fmpq_mat([[entry.re for entry in row] for row in transformed]),
        fmpq_mat([[entry.im for entry in row] for row in transformed]),
    )
    require(complex_rank(split) == complex_rank(matrix), "invertible congruence loses rank")
    require(embed(split).charpoly() == embed(matrix).charpoly(), "congruence nilpotent spectrum control differs")
    require(
        complex_rank(complex_product(split, split)) != complex_rank(complex_product(matrix, matrix)),
        "congruence kernel-filtration mutation escaped",
    )
    require(
        complex_rank(complex_product(complex_product(split, split), split)) == 0,
        "congruent operator is not nilpotent of index three",
    )
    note = (ROOT / "docs/notes/topics/strata-gauss-bottleneck.md").read_text()
    require(
        "The 15 × 15 complex matrix C_z" in note and "skew-Hermitian only for real z" in note,
        "mapped note dimension/skewness correction differs",
    )
    return {
        "shape": [15, 15],
        "bordered_shape": [16, 16],
        "coefficient_offdiagonal_pairs": 210,
        "transpose_skew": True,
        "adjoint_equals_negative_conjugate": True,
        "nonreal_skew_hermitian": False,
        "congruence_rank": complex_rank(split),
        "original_square_rank": complex_rank(complex_product(matrix, matrix)),
        "congruent_square_rank": complex_rank(complex_product(split, split)),
        "congruence_operand": MAXIMAL,
        "congruence_characteristic_polynomial_equal": True,
        "original_jordan_blocks": [3, 2, 2, 2, 2, 1, 1, 1, 1],
        "congruent_jordan_blocks": [3, 3, 2, 2, 1, 1, 1, 1, 1],
        "note_already_corrected": True,
    }


def characteristic_witness(terms: Terms) -> dict[str, Any]:
    matrix, coordinates = reduced(terms)
    values = [sp.Integer(value.re) + sp.I * value.im for value in coordinates]
    low, middle, high = values[:7], values[7], values[8:]
    first_norm, second_norm = sum(value**2 for value in low), sum(value**2 for value in high)
    mixed = sum(first * second for first, second in zip(low, high, strict=True))
    quadratic = sp.expand(first_norm + middle**2 + second_norm)
    delta = sp.expand(first_norm * second_norm - mixed**2)
    quartic = sp.expand(quadratic**2 - 4 * delta)
    variable = sp.Symbol("lambda", real=True)
    predicted = variable * (variable**2 + quadratic) ** 3 * (variable**4 + 2 * quadratic * variable**2 + quartic) ** 2
    real, imaginary = matrix
    operator = sp.Matrix(
        15,
        15,
        lambda row, column: sp.Rational(str(real[row, column])) + sp.I * sp.Rational(str(imaginary[row, column])),
    )
    complex_coefficients = [sp.expand(value) for value in operator.charpoly(variable).all_coeffs()]
    require(
        complex_coefficients == [sp.expand(value) for value in sp.Poly(predicted, variable).all_coeffs()],
        "Gaussian characteristic polynomial fails before realification",
    )
    expected = sp.Poly(sp.expand(predicted * sp.conjugate(predicted)), variable).all_coeffs()
    actual = list(reversed(embed(matrix).charpoly().coeffs()))
    require(
        [str(value) for value in actual] == [str(value) for value in expected],
        "reduced characteristic polynomial fails",
    )
    altered = variable * (variable**2 + quadratic) ** 3 * (variable**4 + 2 * quadratic * variable**2 + quartic + 1) ** 2
    wrong_coefficients = sp.Poly(sp.expand(altered * sp.conjugate(altered)), variable).all_coeffs()
    require(expected != wrong_coefficients, "quartic coefficient mutation escaped")
    return {
        "terms": terms,
        "Q": str(quadratic),
        "Delta": str(delta),
        "G": str(quartic),
        "realified_characteristic_coefficients": [str(value) for value in actual],
        "complex_characteristic_coefficients": [str(value) for value in complex_coefficients],
        "quartic_coefficient_mutation_detected": True,
    }


def kernel_limit_witness(family: str) -> dict[str, Any]:
    row: Any
    if family == "controls":
        row = limits._toy_contracts()
        return {
            "family": family,
            "mutations_rejected": row["mutations_rejected"],
            "invalid_inputs_rejected": row["invalid_inputs_rejected"],
        }
    if family == "four_support":
        row = limits._four_support_paths()
        return {
            "family": family,
            "path_count": len(row["paths"]),
            "generic_nullities": [4] * 3,
            "endpoint_nullity": 12,
            "pairwise_intersections": row["pairwise_intersections"],
            "sum_equals_endpoint_projector": row["sum_equals_endpoint_kernel_projector"],
        }
    certificates, row = limits._eight_nullity_paths()
    return {
        "family": family,
        "path_count": len(certificates),
        "generic_nullities": [8] * 4,
        "endpoint_nullity": 12,
        "pairwise_intersections": row["pairwise_intersections"],
        "first_second_projector_product_trace": row["first_second_projector_product_trace"],
        "automorphism_checked": True,
    }


def cancellation_witness(dimension: int) -> dict[str, Any]:
    row = cancellation.skeleton_facts(dimension)
    expected = {8: (42, 0), 16: (630, 168), 32: (6510, 2520)}[dimension]
    require(
        (row["skeleton_ordered_pairs_of_index_pairs"], row["chi_plus_one"]) == expected, "cancellation counts differ"
    )
    require(
        row["zero_products_off_skeleton"] == 0 and row["chi_invariant_under_single_index_resigning"],
        "support or re-signing obstruction fails",
    )
    table = cancellation.sign_table(dimension)
    require(all(value % 2 == 1 for line in table for value in line), "mod-two sign erasure fails")
    first_row = cancellation._skeleton_rows((dimension, 1))[0]
    first, second, third, fourth = first_row[:4]
    partial = table[first][third] * table[second][fourth]
    signs = [-1 if index == first else 1 for index in range(dimension)]
    resigned = (
        partial
        * signs[first]
        * signs[third]
        * signs[first ^ third]
        * signs[second]
        * signs[fourth]
        * signs[second ^ fourth]
    )
    require(partial != resigned, "incomplete cross-ratio mutation stayed invariant")
    return {
        "dimension": dimension,
        **row,
        "partial_cross_ratio_mutation_detected": True,
        "sign_erasure_additional_zero_product_patterns": expected[0] - expected[1],
    }


def associator_witness(first_index: int) -> dict[str, Any]:
    dimension = 32
    first = left(dimension, ((first_index, 1),))
    nonassociative = 0
    for second_index in range(dimension):
        second = left(dimension, ((second_index, 1),))
        product = cd_core.cd_multiply_exact(
            dimension, vector(dimension, ((first_index, 1),)), vector(dimension, ((second_index, 1),))
        )
        encoded = rational_matrix(cd_core.left_mult_matrix_exact(dimension, product))
        difference = first * second - encoded
        for third_index in range(dimension):
            left_sign, right_sign = cd_core.triple_sign(dimension, first_index, second_index, third_index)
            column = first_index ^ second_index ^ third_index
            require(difference[column, third_index] == right_sign - left_sign, "associator operator identity fails")
            nonassociative += left_sign != right_sign
    return {
        "first_index": first_index,
        "basis_triples": dimension**2,
        "homomorphism_mutation_rejected_triples": nonassociative,
    }


def gram_expansion() -> dict[str, Any]:
    matrix = left(32, MAXIMAL)
    basis = {index: left(32, ((index, 1),)) for index, _coefficient in MAXIMAL}
    expanded = sum(coefficient**2 for _index, coefficient in MAXIMAL) * identity(32)
    for (first, first_coefficient), (second, second_coefficient) in combinations(MAXIMAL, 2):
        expanded += (
            first_coefficient
            * second_coefficient
            * (basis[first].transpose() * basis[second] + basis[second].transpose() * basis[first])
        )
    gram = matrix.transpose() * matrix
    require(gram == expanded, "Gram coefficient expansion fails")
    require((matrix / 4).transpose() * (matrix / 4) == gram / 16, "encoding normalization fails")
    require(gram != trace(gram) / 32 * identity(32), "offdiagonal-interference mutation escaped")
    return {
        "terms": MAXIMAL,
        "cross_terms": 6,
        "cross_term_omission_detected": True,
        "encoding_scale": "4",
        "gram_scale_squared": "16",
    }


def hardware_block_witness(case: tuple[tuple[int, int, int, int], int]) -> dict[str, Any]:
    terms, coset = case
    first_delta, second_delta = terms[0] ^ terms[1], terms[0] ^ terms[2]
    inputs = [coset ^ ((index & 1) * first_delta) ^ ((index >> 1) * second_delta) for index in range(4)]
    outputs = [index ^ terms[0] for index in inputs]
    full = left(32, tuple((index, 1) for index in terms))
    block = fmpq_mat([[full[row, column] for column in inputs] for row in outputs])
    gram = block.transpose() * block
    expected = (0, 0, 48, -16, 1) if terms[1] == 10 else (0, -64, 64, -16, 1)
    actual = tuple(int(value) for value in gram.charpoly().coeffs())
    require(actual == expected, "matched hardware block spectrum differs")
    orthogonal = fmpq_mat([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
    require((orthogonal * block).transpose() * (orthogonal * block) == gram, "output-isometry invariance fails")
    require((2 * block).transpose() * (2 * block) != gram, "nonisometric output mutation escaped")
    return {
        "operand_indices": terms,
        "coset": coset,
        "gram_characteristic_coefficients_low_first": list(actual),
        "success_scale_squared": 16,
        "output_orthogonal_invariance": True,
        "scaling_mutation_detected": True,
    }


def validate_claim_definitions(definitions: Any, expected: set[str]) -> dict[str, Any]:
    require(isinstance(definitions, list), "claim definitions must be a list")
    mapping: dict[str, Any] = {}
    for definition in definitions:
        require(isinstance(definition, dict), "claim definition must be an object")
        claim = definition.get("claim")
        require(isinstance(claim, str), "claim definition needs a string ID")
        require(claim not in mapping, f"duplicate claim definition: {claim}")
        proposition = definition.get("proposition")
        require(isinstance(proposition, str) and bool(proposition.strip()), f"claim definition {claim}: proposition")
        source = definition.get("source")
        require(isinstance(source, dict), f"claim definition {claim}: source")
        for field in ("path", "locator"):
            require(
                isinstance(source.get(field), str) and bool(source[field].strip()),
                f"claim definition {claim}: source {field}",
            )
        require((ROOT / source["path"]).is_file(), f"claim definition {claim}: source file absent")
        mapping[claim] = definition
    require(set(mapping) == expected, "claim definition coverage differs from the numbered verdicts")
    return mapping


def validate_validation_receipt(receipt: Path, witnesses: Path, expected_sha256: str) -> None:
    payload = receipt.read_bytes()
    require(hashlib.sha256(payload).hexdigest() == expected_sha256, "validation receipt SHA-256 differs")
    record = json.loads(payload)
    require(isinstance(record, dict), "validation receipt must be an object")
    require(record.get("schema") == "a5-gram-operator-validation/1", "validation receipt schema differs")
    require(
        record.get("witnesses_sha256") == hashlib.sha256(witnesses.read_bytes()).hexdigest(),
        "validation receipt names a stale witness digest",
    )


def claim_rows() -> list[dict[str, Any]]:
    families = {
        "basis": ("1.2", "2.2", "4.1"),
        "reduced_structure": ("0.1", "0.2"),
        "gram_expansion": ("4.2", "7.5"),
        "two_support": ("1.5", "4.3", "4.4", "5.1"),
        "special_lifts": ("1.4",),
        "inverses": ("1.3", "2.1"),
        "cancellation": ("3.1", "3.2", "3.3"),
        "projector": ("5.2", "5.3", "5.4"),
        "reduced": ("6.1", "6.2", "6.3", "6.4"),
        "scalar": ("7.1",),
        "phase": ("7.2", "7.3"),
        "kernel_limits": ("8.2",),
        "hardware_blocks": ("9.1",),
        "associator": ("9.4",),
    }
    rows: list[dict[str, Any]] = [
        {
            "claim": claim,
            "verdict": "confirmed",
            "evidence": family,
            "scope": "The declared finite inputs and coefficient identities; wider domains need the cited proofs.",
        }
        for family, claims in families.items()
        for claim in claims
    ]
    rows.append(
        {
            "claim": "0.3",
            "verdict": "refuted",
            "evidence": "reduced_structure.note_already_corrected",
            "scope": "The tracked note already has the correct matrix dimension and transpose-skew domain.",
        }
    )
    skipped = {
        "1.1": "Complete real nullity classification is a published theorem; named attainment witnesses are computed.",
        "1.6": "Maximal-locus topology and partner spheres require the published geometric proofs.",
        "3.4": "The separate Lean project and the group-algebra theorem are outside this arithmetic replay.",
        "6.5": "Selecting a complete invariant for attachments requires a classification beyond these power ranks.",
        "7.4": "The experimental distinction between operator and input phase needs its declared encoding.",
        "8.1": "Stable bundle equivalence and nontriviality require the cited topology argument.",
        "8.3": "The retained acquisitions establish neither Berry transport nor holonomy.",
        "9.2": "Calibrated provider readings are owned by their retained analyses; raw acquisitions are not replayed.",
        "9.3": "The Ascella acquisition and denominators belong to a5_photonic_scope; that analysis is not duplicated.",
        "9.5": "Mesh variance and repeat correlations require the existing acquisition-level analyses.",
        "9.6": "External review citation line numbers are not scientific evidence or an input to the calculation.",
    }
    rows.extend(
        {"claim": claim, "verdict": "not_checked", "evidence": "README.md#scope", "scope": reason}
        for claim, reason in skipped.items()
    )
    definitions = json.loads((HERE / "claim_definitions.json").read_text())
    require(definitions.get("schema") == "a5-gram-claim-definitions/1", "claim definition schema differs")
    mapping = validate_claim_definitions(definitions.get("claims"), {row["claim"] for row in rows})
    for row in rows:
        row.update(mapping[row["claim"]])
    return sorted(rows, key=lambda row: tuple(int(part) for part in row["claim"].split(".")))


def build_result() -> dict[str, Any]:
    basis = parallel.ordered_map(
        basis_witness,
        [(dimension, index) for dimension in (1, 2, 4, 8, 16, 32) for index in range(dimension)],
        min_items=1,
    )
    pairs = parallel.ordered_map(
        two_support_witness,
        [
            (dimension, first, second)
            for dimension in (8, 16, 32)
            for first, second in combinations(range(1, dimension), 2)
        ],
        min_items=1,
    )
    lifts = parallel.ordered_map(
        lift_witness,
        [
            (dimension, first, second, coefficient, sign)
            for dimension in (8, 16)
            for first, second in combinations([index for index in range(1, dimension) if index != dimension // 2], 2)
            for coefficient in (1, -1)
            for sign in (1, -1)
        ],
        min_items=1,
    )
    reductions = parallel.ordered_map(
        rank_identity,
        [
            ((first, 1), (second, sign))
            for first, second in combinations([index for index in range(1, 32) if index != 16], 2)
            for sign in (1, -1)
        ],
        min_items=1,
    )
    named = parallel.ordered_map(reduced_witness, [((1, 1), (18, 1)), MAXIMAL], min_items=1)
    characteristic = parallel.ordered_map(
        characteristic_witness,
        [
            ((1, 1),),
            ((1, 1), (9, 1)),
            ((1, 1), (10, 1)),
            ((1, 1), (18, 1)),
            MAXIMAL,
            ((1, 1), (2, 2), (8, 1), (17, 2), (25, -1)),
        ],
        min_items=1,
    )
    data = {
        "basis": {
            "count": len(basis),
            "basis_pairs": sum(row["quadratic_basis_pairs"] for row in basis),
            "all_checks_pass": True,
        },
        "two_support": {
            "pairs": len(pairs),
            "signed_pathion_elements": 930,
            "pathion_pair_nullity_histogram": dict(
                sorted(Counter(str(row["symmetric_blocks"]) for row in pairs if row["dimension"] == 32).items())
            ),
            "coefficient_choices_per_pair": 4,
            "all_checks_pass": True,
        },
        "special_lifts": {
            "count": len(lifts),
            "all_checks_pass": True,
            "lifted_nullity_histogram": dict(sorted(Counter(str(row["lifted_nullity"]) for row in lifts).items())),
        },
        "inverses": parallel.ordered_map(inverse_witness, [((1, 1), (10, 1)), MAXIMAL], min_items=1),
        "cancellation": parallel.ordered_map(cancellation_witness, [8, 16, 32], min_items=1),
        "projector": projector_witness(),
        "gram_expansion": gram_expansion(),
        "associator": parallel.ordered_map(associator_witness, list(range(32)), min_items=1),
        "reduced_structure": reduced_structure(),
        "reduced": {
            "named": named,
            "doubly_pure_signed_two_support_count": len(reductions),
            "rank_identity_checks_pass": True,
            "characteristic_polynomial_cases": characteristic,
        },
        "scalar": parallel.ordered_map(scalar_witness, [2, 4, 8, 16, 32], min_items=1),
        "phase": parallel.ordered_map(phase_witness, [(8, 1, 2), (32, 1, 18), (32, 1, 26)], min_items=1),
        "kernel_limits": parallel.ordered_map(
            kernel_limit_witness, ["four_support", "eight_nullity", "controls"], min_items=1
        ),
        "hardware_blocks": parallel.ordered_map(
            hardware_block_witness, [((1, 10, 20, 31), 2), ((1, 8, 18, 27), 5)], min_items=1
        ),
    }
    return {
        "schema": "a5-gram-operator-witnesses/1",
        "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "sources_sha256": {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in SOURCE_FILES},
        "claims": claim_rows(),
        "checks": data,
        "boundary": "Exact finite arithmetic and coefficient identities; calibration and full topology stay separate.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--validation-sha256", help="full validation receipt digest recorded by the replay gate")
    arguments = parser.parse_args()
    destination = HERE / "witnesses.json"
    if arguments.check:
        if arguments.validation_sha256 is None:
            parser.error("--check requires --validation-sha256 from the replay gate")
        validate_validation_receipt(HERE / "validation.json", destination, arguments.validation_sha256)
    elif arguments.validation_sha256 is not None:
        parser.error("--validation-sha256 applies to --check")
    encoded = json.dumps(build_result(), indent=2, sort_keys=True) + "\n"
    if arguments.write:
        destination.write_text(encoded)
    else:
        require(destination.read_text() == encoded, "retained Gram witnesses differ from the exact replay")
    print("Exact Gram, coefficient-phase, reduced-rank and kernel-limit witnesses pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
