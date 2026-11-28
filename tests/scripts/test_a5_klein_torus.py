"""The Klein sign group of N- against the boost-free centralizer torus, exact over Q."""

from __future__ import annotations

import a5_klein_torus as record
import pytest


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


def test_boost_free_torus_two_torsion_is_the_klein_group() -> None:
    r = record.analyse()
    require((r["stabilizer_dim"], r["centralizer_dim"], r["centralizer_boost_free_dim"]) == (10, 3, 2))
    require(r["torus_boost_free"]["diagonalizable"] and r["torus_boost_free"]["lattice_rank"] == 2)
    require(r["boost_free_two_torsion_equals_klein"])


def test_dropping_the_scaling_loses_the_klein_group() -> None:
    r = record.analyse(drop_scaling=True)
    require(r["torus_boost_free"]["rank"] == 1 and not r["boost_free_two_torsion_equals_klein"])


def test_validate_rejects_a_changed_dimension() -> None:
    result = {"result": record.analyse()}
    record.validate(result)
    result["result"]["centralizer_dim"] = 4
    with pytest.raises(RuntimeError, match="centralizer"):
        record.validate(result)
