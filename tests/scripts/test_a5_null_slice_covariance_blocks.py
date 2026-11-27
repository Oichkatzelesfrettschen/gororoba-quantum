"""Covariance blocks of the A_5 null slice and the octonion derivations on bounded fixtures."""

from __future__ import annotations

import a5_null_slice_covariance_blocks as record
import pytest


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


@pytest.mark.audit
def test_anchor_cosets_give_g2_at_level_six() -> None:
    anchors = record.coset_tables(6, record.anchor_representatives(6))
    rows = [row for tables in anchors.values() for row in record.table_constraints(tables)]
    require(len(anchors) == 4 and record.intersection(rows) == {"all": 14, "rotations": 14, "boosts": 0})


def test_anchor_coset_tables_agree_at_levels_six_and_seven() -> None:
    six = record.coset_tables(6, record.anchor_representatives(6))
    seven = record.coset_tables(7, record.anchor_representatives(7))
    require(len(six) == 4 and list(six) == list(seven))


def test_block_signs_agree_at_levels_six_and_seven() -> None:
    require(record.block_sign_table(6) == record.block_sign_table(7))
