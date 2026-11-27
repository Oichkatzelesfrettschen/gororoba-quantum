"""Covariance blocks of the A_5 null slice and the octonion derivations on bounded fixtures."""

from __future__ import annotations

import a5_null_slice_covariance_blocks as record


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


def test_a5_calibration() -> None:
    row = record.slice_result("A5")
    require((row["all"], row["rotations"], row["boosts"]) == (8, 8, 0))


def test_octonion_derivations_span_g2() -> None:
    require(len(record.octonion_derivations()) == 14)


def test_a5_space_is_the_e2_stabilizer() -> None:
    basis = record.slice_result("A5")["basis"]
    stabilizer = record.stabilizer(record.octonion_derivations(), 2)
    require(record.identification("A5", basis, stabilizer) == {"covariant": 8, "reference": 8, "union": 8})
