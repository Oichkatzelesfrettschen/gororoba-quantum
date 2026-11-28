"""Derivations of A_n and the base-point stabilizers at A_5 and A_6, on bounded fixtures."""

from __future__ import annotations

import a5_a6_stabilizer as record


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


def test_derivation_dimensions_through_a5() -> None:
    require([record.der_dim(n)["dim"] for n in (2, 3, 4, 5)] == [3, 14, 14, 14])


def test_a_negated_sign_changes_der_a3() -> None:
    require(record.der_dim(3, flip=True)["dim"] != 14)


def test_extension_satisfies_leibniz_at_a5() -> None:
    d = record.octonion_derivations()[0]
    require(record.leibniz_failures(record.extend(d, 32), 32) == 0)


def test_a6_lift_has_nullity_36_and_klein_times_z2() -> None:
    ders = [record.extend(d, 32) for d in record.octonion_derivations()]
    row = record.point_facts(6, "lift", ders)
    require(row["nullity"] == 36 and row["g2_stabilizer_dim"] == 8 and len(row["character_stabilizer"]) == 8)
