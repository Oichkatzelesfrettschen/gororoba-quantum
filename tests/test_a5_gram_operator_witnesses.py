"""Exact Gram filters, Gaussian reduced ranks and coefficient-phase controls on bounded operands."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs/evidence/a5-gram-operator-witnesses"))

import gram_witnesses as gram  # noqa: E402


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


def test_maximal_operand_requires_all_three_positive_gram_roots() -> None:
    row = gram.projector_witness()
    require(row["spectrum"] == {"0": 16, "1": 8, "2": 4, "4": 4})
    require(row["moments"] == ["32", "88", "296"])
    require(row["quadratic_trace"] == "28" and row["quadratic_idempotent"] is False)
    require(row["cubic_trace"] == "16" and row["missing_root_rejected"] is True)


@pytest.mark.parametrize(
    ("terms", "ranks", "jordan"),
    [
        (((1, 1), (18, 1)), [15, 8, 1, 0], [3, 2, 2, 2, 2, 2, 2]),
        (((1, 1), (10, -1), (18, 1), (25, 1)), [15, 6, 1, 0], [3, 2, 2, 2, 2, 1, 1, 1, 1]),
    ],
)
def test_nilpotent_reduced_operators_keep_distinct_jordan_types(
    terms: tuple[tuple[int, int], ...], ranks: list[int], jordan: list[int]
) -> None:
    row = gram.reduced_witness(terms)
    require(row["power_ranks"] == ranks and row["jordan_blocks"] == jordan)
    require(row["characteristic_polynomial"] == "lambda**15")


@pytest.mark.parametrize(("case", "nullities"), [((8, 1, 2), [0, 4]), ((32, 1, 18), [12, 4])])
def test_external_phase_uses_the_hermitian_gram(case: tuple[int, int, int], nullities: list[int]) -> None:
    row = gram.phase_witness(case)
    require(row["nullities_at_one_and_i"] == nullities)
    require(row["bilinear_gram_mutation_detected"] is True)


def test_a_real_scalar_offset_lifts_the_sedenion_kernel() -> None:
    row = gram.scalar_witness(16)
    require(row["pure_nullity"] == 4 and row["shifted_nullity"] == 0)
    require(row["gram_shift_identity"] is True and row["skew_sign_mutation_detected"] is True)


def test_split_congruence_changes_the_kernel_filtration_even_when_the_spectrum_agrees() -> None:
    row = gram.reduced_structure()
    require(row["congruence_rank"] == 6)
    require(row["original_square_rank"] == 1 and row["congruent_square_rank"] == 2)
    require(row["congruence_characteristic_polynomial_equal"] is True)


def test_characteristic_polynomial_checks_gaussian_coefficients_before_realification() -> None:
    row = gram.characteristic_witness(((1, 1), (2, 2), (8, 1), (17, 2), (25, -1)))
    require(row["Q"] == "1 + 4*I")
    require(len(row["complex_characteristic_coefficients"]) == 16)
    require(row["quartic_coefficient_mutation_detected"] is True)
