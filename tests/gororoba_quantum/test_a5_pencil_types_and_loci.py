"""Bounded checks of the types-and-loci record script: item functions on small inputs and one mutant each."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import a5_pencil_types_and_loci as record  # noqa: E402


def expect(actual: object, expected: object) -> None:
    if actual != expected:
        raise AssertionError(f"{actual!r} differs from {expected!r}")


def test_j_k_commutes_and_its_mutant_does_not() -> None:
    expect(record.normal_form_item(("2i", -1))["commutes_with_all_31"], True)
    expect(record.normal_form_item(("2i", 1))["commutes_with_all_31"], False)


def test_type_of_reads_matched_bounds() -> None:
    expect(record.type_of({"commutant": [2, 2], "closure": [15, 15]}), "C")
    expect(record.type_of({"commutant": [2, 2], "closure": [15, 16]}), "unresolved")


def test_vb_line_on_and_off_the_plane() -> None:
    row = record.vb_line_item(((1, 1), (10, 1)))
    expect(row is not None and row[1:], [0, [8, 8]])
    expect(record.vb_line_item(((3, 1), (9, 1))), None)


def test_validate_rejects_a_reducible_full_pfaffian() -> None:
    rows = [record.full_pfaffian_item("VB")]
    rows[0]["factor_degrees"] = [[2, 1], [4, 1]]
    with pytest.raises(ValueError, match="VB"):
        record.validate({"full_pfaffians": rows})
