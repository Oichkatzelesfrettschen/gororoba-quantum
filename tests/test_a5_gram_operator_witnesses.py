"""Exact Gram filters, Gaussian reduced ranks and coefficient-phase controls on bounded operands."""

from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
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


@pytest.mark.parametrize(("dimension", "pair", "blocks"), [(8, (1, 2), 0), (32, (1, 10), 8), (32, (1, 18), 12)])
@pytest.mark.parametrize("beta", [1, -1])
def test_two_support_block_count_distinguishes_raw_and_unit_norm_gram(
    dimension: int, pair: tuple[int, int], blocks: int, beta: int
) -> None:
    operand = [Fraction(0)] * dimension
    operand[pair[0]], operand[pair[1]] = Fraction(1), Fraction(beta)
    matrix = gram.rational_matrix(gram.cd_core.left_mult_matrix_exact(dimension, tuple(operand)))
    operator = matrix.transpose() * matrix
    raw_square, normalized_square = operator**2, (operator / 2) ** 2
    raw_second = sum(raw_square[index, index] for index in range(dimension))
    normalized_second = sum(normalized_square[index, index] for index in range(dimension))
    require(raw_second == 4 * dimension + 8 * blocks)
    require(normalized_second == dimension + 2 * blocks)
    require((raw_second - dimension) / 2 != blocks)
    row = gram.two_support_witness((dimension, *pair))
    moment = next(entry for entry in row["equal_weight_moments"] if entry["beta"] == beta)
    require(moment["raw_second_moment"] == str(raw_second))
    require(moment["unit_norm_second_moment"] == str(normalized_second))
    require(moment["raw_block_count"] == moment["unit_norm_block_count"] == str(blocks))
    require(moment["normalization_mutation_detected"] is True)


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


def test_split_congruence_claim_locates_the_rank_preserving_jordan_witness() -> None:
    record = json.loads((gram.HERE / "witnesses.json").read_text())
    claim = next(row for row in record["claims"] if row["claim"] == "6.4")
    witness = record["checks"][claim["evidence"]]
    require(witness["congruence_rank"] == 6)
    require(witness["original_square_rank"] == 1 and witness["congruent_square_rank"] == 2)
    require(witness["original_jordan_blocks"] != witness["congruent_jordan_blocks"])


@pytest.mark.parametrize("terms", [(), ((1, 1), (1, -1))])
def test_zero_operand_is_outside_the_reduced_nullity_formula(terms: tuple[tuple[int, int], ...]) -> None:
    reduced, _coordinates = gram.reduced(terms)
    actual_nullity = 32 - int(gram.left(32, terms).rank())
    expression = 28 - 2 * gram.complex_rank(reduced)
    require(actual_nullity == 32 and expression == 28)
    with pytest.raises(ValueError, match="nonzero doubly pure operand"):
        gram.rank_identity(terms)


def test_characteristic_polynomial_checks_gaussian_coefficients_before_realification() -> None:
    row = gram.characteristic_witness(((1, 1), (2, 2), (8, 1), (17, 2), (25, -1)))
    require(row["Q"] == "1 + 4*I")
    require(len(row["complex_characteristic_coefficients"]) == 16)
    require(row["quartic_coefficient_mutation_detected"] is True)


def test_every_numbered_claim_carries_its_proposition_and_tracked_source() -> None:
    rows = gram.claim_rows()
    require(len(rows) == len({row["claim"] for row in rows}) == 42)
    for row in rows:
        require(bool(row["proposition"].strip()))
        require(bool(row["source"]["locator"].strip()))
        require((ROOT / row["source"]["path"]).is_file())


@pytest.mark.parametrize("mutation", ["missing", "duplicate"])
def test_claim_definitions_reject_incomplete_or_ambiguous_coverage(mutation: str) -> None:
    definitions = json.loads((gram.HERE / "claim_definitions.json").read_text())["claims"]
    expected = {row["claim"] for row in definitions}
    if mutation == "missing":
        definitions.pop()
    else:
        definitions.append(definitions[0])
    with pytest.raises(ValueError, match="claim definition"):
        gram.validate_claim_definitions(definitions, expected)


@pytest.mark.parametrize("field", ["verdict", "evidence", "scope"])
def test_claim_metadata_cannot_upgrade_an_unchecked_proposition(field: str) -> None:
    definitions = json.loads((gram.HERE / "claim_definitions.json").read_text())["claims"]
    expected = {row["claim"] for row in definitions}
    unchecked = next(row for row in definitions if row["claim"] == "9.5")
    unchecked[field] = "confirmed"
    with pytest.raises(ValueError, match="claim definition metadata"):
        gram.validate_claim_definitions(definitions, expected)


@pytest.mark.parametrize("mutation", ["receipt", "witness", "schema", "valid"])
def test_validation_receipt_binds_whole_bytes_schema_and_witness(tmp_path: Path, mutation: str) -> None:
    witness = tmp_path / "witnesses.json"
    witness.write_text("{}\n")
    receipt = tmp_path / "validation.json"
    record = {
        "schema": "a5-gram-operator-validation/1",
        "witnesses_sha256": hashlib.sha256(witness.read_bytes()).hexdigest(),
        "measurements": {"check": {"wall_seconds": 1.25}},
    }
    if mutation == "schema":
        record["schema"] = "unrecognized"
    receipt.write_text(json.dumps(record))
    expected_digest = hashlib.sha256(receipt.read_bytes()).hexdigest()
    if mutation == "receipt":
        receipt.write_text(receipt.read_text() + "\n")
    elif mutation == "witness":
        witness.write_text('{"changed":true}\n')
    if mutation == "valid":
        gram.validate_validation_receipt(receipt, witness, expected_digest)
    else:
        with pytest.raises(ValueError, match="validation receipt"):
            gram.validate_validation_receipt(receipt, witness, expected_digest)
