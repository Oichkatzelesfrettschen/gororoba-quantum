"""Bounded checks of the nullity-transition record script: item functions on small inputs and one mutant each."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import a5_nullity_transitions as record  # noqa: E402


def expect(actual: object, expected: object) -> None:
    if actual != expected:
        raise AssertionError(f"{actual!r} differs from {expected!r}")


def test_convention_matches_the_doubling_formula() -> None:
    expect(record.convention_item(8), {"dimension": 8, "products": 64, "mismatches": 0})


@pytest.mark.parametrize(("name", "kernel"), [("gamma1 at 0", 8), ("gamma3 at -1", 16)])
def test_compression_rank_at_a_junction(name: str, kernel: int) -> None:
    row = record.compression_item(name)
    expect((row["kernel"], row["compression_rank"], row["skew"]), (kernel, 4, True))


def test_gram_identity_holds_for_the_doubling_unit_only() -> None:
    expect(record.gram_identity_item((16, 8))["cross_term_failures"], 0)
    expect(record.gram_identity_item((32, 26))["cross_term_failures"], 14)


def test_three_form_alternates() -> None:
    expect(record.three_form_item(16), {"dimension": 16, "nonzero_ordered_triples": 210, "alternation_failures": 0})


def test_validate_rejects_a_convention_mismatch() -> None:
    with pytest.raises(ValueError, match="doubling formula"):
        record.validate({"convention": [{"mismatches": 1}]})
