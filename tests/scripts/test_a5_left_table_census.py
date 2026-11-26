"""Left-table commutant, associator census and Euclidean-cone points on bounded fixtures."""

from __future__ import annotations

import a5_left_table_census as record


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


def test_orbit_commutant_agrees_with_the_direct_system() -> None:
    for level, expected in ((1, 2), (2, 4), (3, 1)):
        signs = record.sign_rows(1 << level, list(range(1 << level)))
        orbit = sum(record.orbit_consistent(signs, d) for d in range(1 << level))
        require(orbit == record.commutant_direct(level) == expected)


def test_nonassociating_triples_of_the_sedenions() -> None:
    require(record.triple_item((4, 1, 16)) == 1848 == (16 - 2) * (16 - 4) * (16 + 6) // 2)


def test_euclidean_cone_points() -> None:
    tables = record.slice_tables()
    require(record.field_nullity(tables, 2, (1, 1, 0, 0, 0, 0), 1) == 12)
    require(record.field_nullity(tables, 3, (1, 1, 0, 0, 0, 0), 1) == 0)
    require(record.local_nullity(tables, 17, (1, 0, 0, 0, 0, 0))["nullity_mod_p"] == 12)
