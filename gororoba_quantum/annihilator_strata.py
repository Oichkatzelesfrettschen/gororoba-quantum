"""Exact finite annihilator strata for signed two-term Cayley-Dickson elements.

The census covers (e_i + sign*e_j)/sqrt(2), with distinct imaginary basis
indices and both relative signs. Every left-action matrix splits into two by
two integer blocks after row and column permutations. A singular block has
rank one; an invertible block has rank two. Independent integer elimination
and full-matrix kernel products verify a representative of every stratum.

The output describes a finite sparse family rather than the full continuous
zero-divisor variety. Published maximal-annihilator lifts receive separate
exact rank checks. The rank, kernel and block-scale separation follows
open_gororoba's exact_annihilator.rs certificate interface. All arithmetic
runs locally using (a,b)(c,d) = (ac-conj(d)b, da+b conj(c)).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
from collections import Counter
from itertools import combinations, product

import parallel
from cd_core import cd_sign

ALLOWED_DIMENSIONS = (8, 16, 32, 64, 128, 256)
CERTIFICATE_SOURCE_SHA256 = "0769f94d0ceb9bf935324a5220c5905d2826e6b88be19ef7e0c45d6b4d96ead2"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _integer_rank(matrix: list[list[int]]) -> int:
    """Compute rational rank by fraction-free integer row elimination."""
    if not matrix:
        return 0
    reduced = [row.copy() for row in matrix]
    column_count = len(matrix[0])
    if any(len(row) != column_count for row in matrix):
        raise ValueError("integer rank requires a rectangular matrix")
    pivot_count = 0
    for column_index in range(column_count):
        pivot_index = next(
            (row_index for row_index in range(pivot_count, len(reduced)) if reduced[row_index][column_index]),
            None,
        )
        if pivot_index is None:
            continue
        reduced[pivot_count], reduced[pivot_index] = reduced[pivot_index], reduced[pivot_count]
        pivot_value = reduced[pivot_count][column_index]
        for row_index in range(pivot_count + 1, len(reduced)):
            multiplier = reduced[row_index][column_index]
            if multiplier == 0:
                continue
            updated_row = [
                pivot_value * entry - multiplier * pivot_entry
                for entry, pivot_entry in zip(reduced[row_index], reduced[pivot_count], strict=True)
            ]
            common_divisor = math.gcd(*updated_row)
            reduced[row_index] = [entry // common_divisor for entry in updated_row] if common_divisor else updated_row
        pivot_count += 1
    return pivot_count


def _left_action_matrix(dimension: int, coefficients: dict[int, int]) -> list[list[int]]:
    matrix = [[0] * dimension for _ in range(dimension)]
    for basis_index, coefficient in coefficients.items():
        for column_index in range(dimension):
            matrix[basis_index ^ column_index][column_index] += coefficient * cd_sign(
                dimension, basis_index, column_index
            )
    return matrix


def _pair_kernel(
    sign_table: list[list[int]], first_index: int, second_index: int, relative_sign: int
) -> list[tuple[int, int, int]]:
    """Sparse kernel basis: each tuple means e_first + sign*e_second."""
    if relative_sign not in (-1, 1) or not 0 < first_index < second_index < len(sign_table):
        raise ValueError("pair kernel requires distinct ordered imaginary indices and a relative sign")
    displacement = first_index ^ second_index
    kernel_basis = []
    for first_column in range(len(sign_table)):
        second_column = first_column ^ displacement
        if first_column > second_column:
            continue
        diagonal_first = sign_table[first_index][first_column]
        diagonal_second = sign_table[first_index][second_column]
        upper_right = relative_sign * sign_table[second_index][second_column]
        lower_left = relative_sign * sign_table[second_index][first_column]
        determinant = diagonal_first * diagonal_second - upper_right * lower_left
        _require(determinant in (-2, 0, 2), "signed block determinant left its exact range")
        if determinant == 0:
            second_coefficient = -diagonal_first * upper_right
            _require(lower_left + diagonal_second * second_coefficient == 0, "block kernel equation failed")
            kernel_basis.append((first_column, second_column, second_coefficient))
    return kernel_basis


def _verify_pair_representative(
    dimension: int, first_index: int, second_index: int, nullity: int, sign_table: list[list[int]]
) -> dict[str, object]:
    first_kernel_vector: list[list[int]] | None = None
    mutation_detected: bool | None = None
    for relative_sign in (1, -1):
        matrix = _left_action_matrix(dimension, {first_index: 1, second_index: relative_sign})
        kernel_basis = _pair_kernel(sign_table, first_index, second_index, relative_sign)
        exact_rank = _integer_rank(matrix)
        _require(exact_rank == dimension - nullity, "integer elimination disagrees with block rank")
        _require(len(kernel_basis) == nullity, "kernel basis dimension disagrees with exact rank")
        occupied_columns: set[int] = set()
        for first_column, second_column, second_coefficient in kernel_basis:
            _require(
                first_column not in occupied_columns and second_column not in occupied_columns,
                "kernel basis supports overlap",
            )
            occupied_columns.update((first_column, second_column))
            _require(
                all(row[first_column] + second_coefficient * row[second_column] == 0 for row in matrix),
                "full integer left-action matrix rejects its kernel vector",
            )
        # Disjoint two-entry supports give B^T B=2I exactly, so the verified
        # vectors form a basis and division by sqrt(2) gives an orthonormal basis.
        if relative_sign == 1 and kernel_basis:
            first_column, second_column, second_coefficient = kernel_basis[0]
            first_kernel_vector = [[first_column, 1], [second_column, second_coefficient]]
            mutated = [row.copy() for row in matrix]
            mutated_row = first_index ^ first_column
            mutated[mutated_row][first_column] *= -1
            mutation_detected = any(row[first_column] + second_coefficient * row[second_column] != 0 for row in mutated)
            _require(mutation_detected, "a flipped nonzero matrix entry escaped the annihilator check")
    return {
        "first_basis_index": first_index,
        "second_basis_index": second_index,
        "representative_relative_sign": 1,
        "rank": dimension - nullity,
        "nullity": nullity,
        "both_relative_signs_independently_checked": True,
        "full_kernel_basis_vectors_checked_per_sign": nullity,
        "first_kernel_vector_integer_coefficients": first_kernel_vector,
        "kernel_vector_normalization": "divide by sqrt(2)",
        "input_norm_squared": 2,
        "block_encoding_alpha": 2,
        "unit_input_block_alpha_squared": 2,
        "kernel_basis_gram": "B^T B = 2I from disjoint two-entry supports",
        "fixed_element_unit_kernel_sphere": f"S{nullity - 1}" if nullity else "empty",
        "single_entry_mutation_detected": mutation_detected,
        "unscaled_gram_spectrum": [
            {"eigenvalue": 0, "multiplicity": nullity},
            {"eigenvalue": 2, "multiplicity": dimension - 2 * nullity},
            {"eigenvalue": 4, "multiplicity": nullity},
        ],
    }


def _lift_with_distinguished_unit(coefficients: dict[int, int], dimension: int, relative_sign: int) -> dict[int, int]:
    distinguished_unit = dimension // 2
    _require(0 not in coefficients and distinguished_unit not in coefficients, "lift input intersects C_n")
    lifted = dict(coefficients)
    for basis_index, coefficient in coefficients.items():
        upper_index = dimension + (distinguished_unit ^ basis_index)
        lifted[upper_index] = relative_sign * coefficient * cd_sign(dimension, distinguished_unit, basis_index)
    return lifted


def _maximal_lift_witness(dimension: int, sign_path: tuple[int, ...]) -> dict[str, object]:
    """Check one published lift witness; the global upper bound is external."""
    coefficients = {1: 1, 10: 1}
    kernel_vector = {4: 1, 15: -1}
    current_dimension = 16
    expected_nullity = 4
    for relative_sign in sign_path:
        _require(relative_sign in (-1, 1), "maximal lift requires a signed branch")
        coefficients = _lift_with_distinguished_unit(coefficients, current_dimension, relative_sign)
        kernel_vector = _lift_with_distinguished_unit(kernel_vector, current_dimension, relative_sign)
        expected_nullity += current_dimension - 4
        current_dimension *= 2
    _require(current_dimension == dimension, "maximal lift sign-path length disagrees with its dimension")
    matrix = _left_action_matrix(dimension, coefficients)
    exact_rank = _integer_rank(matrix)
    _require(dimension - exact_rank == expected_nullity, "published annihilator lift failed its exact rank check")
    stage = dimension.bit_length() - 1
    published_maximum = dimension - 4 * stage + 4
    _require(expected_nullity == published_maximum, "lift recurrence disagrees with the published maximum")
    _require(
        all(sum(row[index] * coefficient for index, coefficient in kernel_vector.items()) == 0 for row in matrix),
        "propagated kernel witness fails full integer matrix multiplication",
    )
    input_norm_squared = sum(coefficient**2 for coefficient in coefficients.values())
    block_alpha = sum(abs(coefficient) for coefficient in coefficients.values())
    _require(input_norm_squared == dimension // 8, "integer lift normalization changed")
    return {
        "integer_coefficients": [[index, coefficient] for index, coefficient in sorted(coefficients.items())],
        "lift_sign_path": list(sign_path),
        "rank": exact_rank,
        "nullity": expected_nullity,
        "published_global_maximum": published_maximum,
        "input_norm_squared": input_norm_squared,
        "unit_normalization": "divide every integer coefficient by sqrt(input_norm_squared)",
        "block_encoding_alpha": block_alpha,
        "unit_input_block_alpha_squared": block_alpha**2 // input_norm_squared,
        "kernel_witness_integer_coefficients": [
            [index, coefficient] for index, coefficient in sorted(kernel_vector.items())
        ],
        "kernel_witness_norm_squared": sum(coefficient**2 for coefficient in kernel_vector.values()),
        "construction": "a_(n+1)=(a_n,sign*i_n*a_n), i_n=e_(2^(n-1)); a_4=e1+e10",
        "source": "Biss-Dugger-Isaksen math/0511691v1 Theorem 10.2 and Proposition 9.10",
        "scope": "Exact rank verifies the listed finite witness; the cited theorem supplies the global maximum.",
    }


def _maximal_lift_records(dimension: int) -> list[dict[str, object]]:
    if dimension < 16:
        return []
    lift_count = dimension.bit_length() - 5
    records = [_maximal_lift_witness(dimension, sign_path) for sign_path in product((1, -1), repeat=lift_count)]
    distinct_coordinates = {json.dumps(record["integer_coefficients"]) for record in records}
    _require(len(records) == len(distinct_coordinates) == 1 << lift_count, "signed lift representatives collided")
    return records


def _dimension_census(dimension: int) -> dict[str, object]:
    sign_table = [[cd_sign(dimension, first, second) for second in range(dimension)] for first in range(dimension)]
    histogram: Counter[int] = Counter()
    representatives: dict[int, tuple[int, int]] = {}
    partition_histograms: dict[str, Counter[int]] = {
        "lower_lower": Counter(),
        "lower_upper": Counter(),
        "upper_upper": Counter(),
    }
    rows_digest = hashlib.sha256()
    for first_index, second_index in combinations(range(1, dimension), 2):
        if second_index < dimension // 2:
            partition = "lower_lower"
        elif first_index < dimension // 2:
            partition = "lower_upper"
        else:
            partition = "upper_upper"
        for relative_sign in (1, -1):
            nullity = len(_pair_kernel(sign_table, first_index, second_index, relative_sign))
            histogram[nullity] += 1
            partition_histograms[partition][nullity] += 1
            representatives.setdefault(nullity, (first_index, second_index))
            rows_digest.update(f"{dimension},{first_index},{second_index},{relative_sign},{nullity}\n".encode("ascii"))
    denominator = (dimension - 1) * (dimension - 2)
    _require(sum(histogram.values()) == denominator, "signed census denominator changed")
    _require(sum(sum(counts.values()) for counts in partition_histograms.values()) == denominator, "partition gap")
    _require(all(nullity % 4 == 0 for nullity in histogram), "finite two-term nullity escaped multiples of four")
    if dimension == 8:
        _require(dict(histogram) == {0: 42}, "octonion pair baseline changed")
    elif dimension == 16:
        _require(dict(histogram) == {0: 126, 4: 84}, "sedenion pair baseline changed")
    elif dimension == 32:
        _require(dict(histogram) == {0: 342, 4: 168, 8: 168, 12: 252}, "dimension-32 strata changed")
        _require(set(histogram) - {0, 4} == {8, 12}, "constant-four zero-divisor kernel claim escaped falsification")
    representative_records = [
        _verify_pair_representative(dimension, *representatives[nullity], nullity, sign_table)
        for nullity in sorted(histogram)
    ]
    return {
        "dimension": dimension,
        "cayley_dickson_stage": dimension.bit_length() - 1,
        "signed_element_count": denominator,
        "rank_nullity_histogram": [
            {"rank": dimension - nullity, "nullity": nullity, "signed_element_count": histogram[nullity]}
            for nullity in sorted(histogram)
        ],
        "partition_nullity_histograms": {
            partition: [{"nullity": nullity, "signed_element_count": counts[nullity]} for nullity in sorted(counts)]
            for partition, counts in partition_histograms.items()
        },
        "ordered_rows_sha256": rows_digest.hexdigest(),
        "ordered_rows_encoding": "ASCII dimension,i,j,relative_sign,nullity plus LF; i<j ascending; signs +1,-1",
        "representatives": representative_records,
        "independent_integer_rank_checks": 2 * len(representative_records),
        "largest_two_term_nullity": max(histogram),
        "published_maximum_lift_witnesses": _maximal_lift_records(dimension),
    }


def _verify_rank_engine() -> None:
    fixtures: tuple[tuple[list[list[int]], int], ...] = (
        ([], 0),
        ([[0, 0], [0, 0]], 0),
        ([[2, 3], [4, 6]], 1),
        ([[2, 3], [4, 5]], 2),
        ([[0, 2, 4], [0, 3, 6], [0, -4, -8]], 1),
        ([[2, 3, 5], [3, 5, 8], [5, 8, 13]], 2),
    )
    for matrix, expected_rank in fixtures:
        _require(_integer_rank(matrix) == expected_rank, "fraction-free rank fixture failed")
    try:
        _integer_rank([[1, 2], [3]])
    except ValueError:
        pass
    else:
        raise RuntimeError("integer rank accepted a ragged matrix")


def _upstream_regression_checks() -> dict[str, object]:
    """Repeat concrete rank fixtures from the established rational certificates."""
    fixtures = (
        (16, {0: 1, 9: 1}, 16),
        (16, {1: 1, 9: 1}, 16),
        (32, {1: 1, 10: 1}, 24),
        (32, {1: -3, 10: -3}, 24),
        (32, {1: 2, 10: 2}, 24),
        (32, {0: 1, 1: 1, 10: 1}, 32),
    )
    for dimension, coefficients, expected_rank in fixtures:
        _require(
            _integer_rank(_left_action_matrix(dimension, coefficients)) == expected_rank,
            "upstream exact-annihilator rank fixture changed",
        )
    return {
        "source_repository": "open_gororoba",
        "source_path": "crates/algebra_analysis/src/exact_annihilator.rs",
        "source_read_sha256": CERTIFICATE_SOURCE_SHA256,
        "fixture_count": len(fixtures),
        "verified_fixtures": "two invertible sedenions; A5 scalar orbit at 1,-3,2; identity-induced rank jump",
        "additional_census_overlap": "all 84 signed sedenion assessor elements have exact rank twelve",
        "scope": "Python repeats source fixtures with integer elimination; this audit does not execute Rust tests.",
    }


def audit_annihilator_strata(maximum_dimension: int = 128) -> dict[str, object]:
    """Return exact finite strata up to one supported power-of-two dimension."""
    if maximum_dimension not in ALLOWED_DIMENSIONS:
        raise ValueError(f"maximum_dimension must be one of {ALLOWED_DIMENSIONS}")
    _verify_rank_engine()
    dimensions = [dimension for dimension in ALLOWED_DIMENSIONS if dimension <= maximum_dimension]
    return {
        "schema": "cayley-dickson-annihilator-strata-v1",
        "execution": "local exact integer arithmetic",
        "qpu_executed": False,
        "python_version": platform.python_version(),
        "element_domain": "(e_i + sign*e_j)/sqrt(2), 1 <= i < j < D, sign in {+1,-1}",
        "denominator_per_dimension": "2*binomial(D-1,2) = (D-1)(D-2); global negatives identified",
        "multiplication_convention": "(a,b)(c,d)=(ac-conj(d)b, da+b conj(c)); cd_core.cd_sign",
        "rank_method": (
            "D/2 exact 2x2 blocks; independent fraction-free integer elimination on every stratum representative"
        ),
        "normalization": (
            "L_unit = L_integer/sqrt(2); rank and kernel agree; listed integer Gram eigenvalues divide by 2"
        ),
        "scope": (
            "The finite two-term family establishes its listed strata; global dimensions, "
            "topology, and completeness require separate theorems."
        ),
        "upstream_certificate_regressions": _upstream_regression_checks(),
        "dimensions": parallel.ordered_map(_dimension_census, dimensions, min_items=2),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-dimension",
        type=int,
        choices=ALLOWED_DIMENSIONS,
        default=128,
        help="largest census/lift dimension; fixed source-regression fixtures include dimensions 16 and 32",
    )
    arguments = parser.parse_args()
    print(json.dumps(audit_annihilator_strata(arguments.max_dimension), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
