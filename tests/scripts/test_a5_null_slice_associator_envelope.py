"""Associator form, isotropic strata and the dimension tower of the Lorentzian slice of A_5 on bounded fixtures."""

from __future__ import annotations

import a5_null_slice_associator_envelope as record
import pytest


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


def test_vectorized_signs_agree_with_cd_core_in_dimension_64() -> None:
    require(record.sign_disagreements(64, set(range(64))) == 0)


def test_defect_is_the_symmetrized_associator_in_dimension_16() -> None:
    row = record.associator_item(16)
    require(row["pairs"] == 210 and row["associator_failures"] == 0 and row["gram_failures"] == 0)


@pytest.mark.parametrize(("t", "nullity"), [(10754, 12), (10755, 0)])
def test_euclidean_cone_point_over_f_32009(t: int, nullity: int) -> None:
    signs = record.sign_rows(record.DIMENSION, list(range(record.DIMENSION)))
    tables = [record.table(signs, k) for k in range(record.DIMENSION)]
    operator = record.slice_operator(tables, (1, 0, 0, 0, 0, 0), t)
    require(record.nullity_mod(operator, 32009) == nullity)


def test_square_root_modulo_both_primes() -> None:
    require(record.square_root(-1, 32009) in (10754, 32009 - 10754))
    require(record.square_root(-1, 32003) is None)


def test_two_term_strata_of_a_5() -> None:
    row = record.two_term_strata()
    require(row["histogram"] == {"0": 15, "4": 84, "12": 126} and row["nullity_4_struts_above_8"])
    require(row["slice_struts"] == {"1": 11, "3": 9, "4": 14, "5": 15, "6": 12, "7": 13})


def test_family_rows_of_dimension_256() -> None:
    rows = record.family_rows(8)
    first, octonion = rows
    require(first["triple_relations"] == [117242, 0] and first["disjoint_stars"] and first["common_kernel"] == 4)
    require(octonion["space_clifford"] and octonion["triple_relations"] == [147, 0] and octonion["common_kernel"] == 224)
    require(first["sign_disagreements"] == 0 and octonion["null_point_nullity"] == 4)


def test_mutation_controls() -> None:
    record.self_test()
