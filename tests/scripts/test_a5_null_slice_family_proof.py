"""Proof checks of the null-slice families on bounded levels."""

from __future__ import annotations

import a5_null_slice_family_proof as record


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


def test_recursion_and_lemmas_at_small_levels() -> None:
    for name, level in (("cd_core", 5), ("identities", 6), ("T", 6), ("U", 5), ("R", 5)):
        require(record.check_item((name, level)) == 0)


def test_family_claims_at_level_seven() -> None:
    rows = record.family_item(7)["rows"]
    require([row["failures"] for row in rows] == [0, 0])
    require([row["common_kernel"] for row in rows] == [4, 128 - 32])
