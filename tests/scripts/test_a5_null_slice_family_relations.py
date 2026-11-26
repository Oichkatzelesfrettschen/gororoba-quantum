"""Direct so(m,1) relation checks of the first null-slice family on a bounded level."""

from __future__ import annotations

import a5_null_slice_family_relations as record


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


def test_level_six_relations_hold() -> None:
    result = record.compute(6)
    record.validate(result)
    require(result["space_size"] == 14 and result["relations"] == 14 * 14 * 13 // 2 and result["failures"] == 0)


def test_a_moved_space_fails() -> None:
    _tau, space = record.family(6)
    require(record.compute(6, (*space[:-1], 8))["failures"] > 0)
