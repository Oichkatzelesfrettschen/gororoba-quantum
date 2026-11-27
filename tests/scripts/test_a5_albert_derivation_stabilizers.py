"""Derivations of the octonions and of J_3(R) under the cd_core product, on bounded fixtures."""

from __future__ import annotations

import a5_albert_derivation_stabilizers as record
import pytest


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


def test_octonion_derivations_span_g2() -> None:
    sign = record.octonion_sign()
    dim, basis, rank, rows = record.derivations(record.octonion_algebra(sign))
    require((dim, len(basis), rank, rows) == (14, 14, 50, 512))


def test_a_negated_sign_pair_leaves_four_octonion_derivations() -> None:
    sign = record.mutated_sign(record.octonion_sign(), 1, 2)
    require(record.derivations(record.octonion_algebra(sign))[0] == 4)


def test_the_zero_product_admits_every_linear_map() -> None:
    zero = record.Alg(8, [[{} for _ in range(8)] for _ in range(8)], False)
    require(record.derivations(zero)[0] == 64)


def test_the_real_jordan_algebra_has_three_derivations() -> None:
    algebra, _ = record.jordan_algebra([[1]], 1)
    require(record.derivations(algebra)[0] == 3)


@pytest.mark.audit
def test_the_exceptional_jordan_algebra_has_f4_derivations() -> None:
    algebra, _ = record.jordan_algebra(record.octonion_sign(), 8)
    dim, _basis, rank, rows = record.derivations(algebra)
    require((dim, rank, rows) == (52, 677, 9063))


def test_validate_rejects_one_changed_count() -> None:
    result = dict(record.EXPECTED)
    record.validate(result)
    result["stab_E1"] = 37
    with pytest.raises(RuntimeError, match="stab_E1"):
        record.validate(result)
