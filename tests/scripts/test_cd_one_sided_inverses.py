"""Contracts for cd_one_sided_inverses: the basis identities decide the adjoint law, kernels of L_a and R_a agree on
the sedenion zero divisor e_1 + e_10, and each check rejects a planted defect.
"""

from __future__ import annotations

from fractions import Fraction

import cd_one_sided_inverses as osi
import pytest

E1_PLUS_E10 = (0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0)


def test_basis_identities_hold_through_dimension_64() -> None:
    for dim in (2, 4, 8, 16, 32, 64):
        if osi.identity_record(dim)["basis_pairs"] != dim * dim:
            raise AssertionError(dim)


def test_conjugation_fixing_a_unit_fails_the_adjoint_law(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(osi, "conj_sign", lambda index: 1 if index in (0, 1) else -1)
    with pytest.raises(osi.ContractError):
        osi.identity_record(4)


def test_sedenion_zero_divisor_has_equal_four_dimensional_annihilators() -> None:
    left = osi.kernel(osi.left_matrix(16, E1_PLUS_E10))
    right = osi.kernel(osi.right_matrix(16, E1_PLUS_E10))
    if len(left) != 4 or not osi.same_span(left, right):
        raise AssertionError((len(left), len(right)))
    if osi.element_check((16, E1_PLUS_E10)) != {"kernel_dimension": 4}:
        raise AssertionError("element_check departs from the kernel dimension 4")


def test_partner_blade_kernel_is_a_different_subspace() -> None:
    partner = tuple(-x if i == 10 else x for i, x in enumerate(E1_PLUS_E10))
    left = osi.kernel(osi.left_matrix(16, E1_PLUS_E10))
    other = osi.kernel(osi.left_matrix(16, partner))
    if len(other) != 4 or osi.same_span(left, other):
        raise AssertionError("e_1 - e_10 shares the kernel of e_1 + e_10")


def test_a_right_matrix_with_one_flipped_sign_fails_the_kernel_equality(monkeypatch: pytest.MonkeyPatch) -> None:
    original = osi.right_matrix

    def flipped(dim: int, a: tuple[int, ...]) -> list[list[Fraction]]:
        m = original(dim, a)
        m[2][3] = -m[2][3]
        return m

    monkeypatch.setattr(osi, "right_matrix", flipped)
    with pytest.raises(osi.ContractError):
        osi.element_check((16, E1_PLUS_E10))


def test_invertible_element_reports_no_kernel() -> None:
    a = tuple([1] + [0] * 15)
    if osi.element_check((16, a)) != {"kernel_dimension": 0}:
        raise AssertionError("e_0 has a kernel")


def test_two_blade_and_doubly_pure_counts() -> None:
    if len(osi.two_blades(16)) != 210 or len(osi.three_units(32)) != 455 or len(osi.doubly_pure(32)) != 450:
        raise AssertionError((len(osi.two_blades(16)), len(osi.three_units(32)), len(osi.doubly_pure(32))))
