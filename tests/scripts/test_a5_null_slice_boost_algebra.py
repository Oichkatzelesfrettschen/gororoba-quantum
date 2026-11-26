"""Exact Clifford-defect identities on the Lorentzian slice of A_5 and their controls in dimensions 16 and 64."""

from __future__ import annotations

import a5_null_slice_boost_algebra as record
import pytest


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


def test_slice_operator_identities() -> None:
    lefts = record.left_tables(record.DIMENSION)
    require(record.specification_agreement(lefts))
    row = record.operator_identities(lefts, record.TIME, record.SPACE)
    require(row["cubic_relation"] == [56, 0] and row["defect_ranks"] == [8] and row["defect_square_traces"] == [8])
    require(record.gram_identity(lefts, record.TIME, record.SPACE, (2, 3, 6, 0, 0, 0), 5))


def test_defects_satisfy_so_6_1_and_split_four_vector_modules() -> None:
    lefts = record.left_tables(record.DIMENSION)
    row = record.boost_algebra(lefts, record.TIME, record.SPACE, record.TIME_SUPPORT)
    require(row["triple_relations"] == [90, 0] and row["lie_dimension"] == {"dimension": 21, "capped": False})
    require(row["time_support"] == [2, 8, 18, 24] and row["common_kernel_support"] == [0, 10, 16, 26])
    require(row["range_span"] == 28 and row["vector_orbits_are_boosts"] and row["orbit_indices_distinct"])


def test_conjugate_maps_and_kernel_on_the_cone() -> None:
    lefts = record.left_tables(record.DIMENSION)
    maps = record.conjugate_maps(lefts, record.TIME, record.SPACE, record.TIME_SUPPORT)
    require(
        {key: (row["target"], row["sign"]) for key, row in maps.items()}
        == {"2": (24, 1), "8": (18, -1), "18": (8, 1), "24": (2, -1)}
    )
    require(all(row["t_x_coefficients_vanish"] and row["x_x_coefficients"] for row in maps.values()))
    for row in record.kernel_formula(lefts, record.TIME, record.SPACE, record.TIME_SUPPORT)["points"]:
        require(row["annihilated"] and row["span_rank"] == 4 and row["nullity"] == 4)


@pytest.mark.parametrize(("item", "failures", "lie"), [((16, 2), 42, 15), ((32, 1), 42, 15), ((32, 10), 0, 21)])
def test_tower_rows_separate_the_slices(item: tuple[int, int], failures: int, lie: int) -> None:
    row = record.tower_item(item)
    require(len(row["clean"]) == 6 and row["cubic_relation"] == [56, 0] and row["null_point_nullity"] == 4)
    require(row["triple_relations"] == [90, failures] and row["lie_dimension"]["dimension"] == lie)


@pytest.mark.parametrize(("level", "relations"), [(4, 2), (5, 90), (6, 1274)])
def test_family_slice_satisfies_so_m_1(level: int, relations: int) -> None:
    row = record.family_item(level)
    require(row["triple_relations"] == [relations, 0] and row["common_kernel_dimension"] == 4)
    require(row["range_span"] == row["dimension"] - 4 and row["null_point_nullity"] == 4)


def test_octonion_space_slice_of_dimension_64() -> None:
    row = record.octonion_space_item(6)
    require(row["space_clifford"] and row["gram_identity"] and row["disjoint_stars"])
    require(row["triple_relations"] == [147, 0] and row["null_point_nullity"] == 4)


def test_star_criterion_and_clifford_space_separate_dimension_64() -> None:
    row = record.tower_item((64, 18))
    require(row["disjoint_stars"] and row["triple_relations"][1] == 0)
    require(not row["space_clifford"] and not row["gram_identity"])


def test_mutation_controls() -> None:
    record.self_test()
