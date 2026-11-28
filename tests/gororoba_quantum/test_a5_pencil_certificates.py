"""Bounded checks of the pencil-certificate record script: item functions on small inputs and one mutant each."""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

import pytest
from flint import fmpq

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import a5_pencil_certificates as record  # noqa: E402


def expect(actual: object, expected: object) -> None:
    if actual != expected:
        raise AssertionError(f"{actual!r} differs from {expected!r}")


def test_doubling_unit_anticommutes_and_another_unit_does_not() -> None:
    good = record.anticommutation_item((16, 8))
    expect((good["anticommutation_failures"], good["square_is_minus_identity"]), ([], True))
    expect(record.anticommutation_item((16, 4))["anticommutation_failures"] != [], True)


def test_sedenion_tower_level_meets_its_bounds() -> None:
    row = record.structure_item((16, record.BASE))
    expect(record.tower_ok(row, 4), True)
    expect((row["closure_lower"], row["closure_upper"]), (3, 3))


def test_type_r_point_fails_the_tower_rule() -> None:
    row = record.structure_item((32, record.CALIBRATION["R e1+e10+e3+e20"]))
    expect((row["commutant_lower"], row["commutant_upper"], row["closure_lower"], row["closure_upper"]), (1, 1, 28, 28))
    expect(record.tower_ok(row, 5), False)


def test_rational_reconstruction() -> None:
    expect(record.reconstruct(record.residue(fmpq(-5, 7))), Fraction(-5, 7))
    expect(record.reconstruct(record.residue(fmpq(200, 3))) == Fraction(200, 3), False)


def test_validate_rejects_a_wrong_pencil_dimension() -> None:
    row = record.structure_item((16, record.BASE))
    row["pencil_dimension"] = 4
    with pytest.raises(ValueError, match="A_4"):
        record.validate({"tower": [row]})
