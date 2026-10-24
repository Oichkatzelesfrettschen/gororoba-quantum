"""Contracts for cd_phase_degree's Proposition 5 check: the point-indicator pairs hold on cd_sign's tables, and a
flipped cell in one family row or a constant-shifted m = 0 row fails the check."""

from __future__ import annotations

import cd_phase_degree as degree
import pytest

from cd_core import cd_sign


@pytest.mark.parametrize("n", range(3, 8))
def test_point_family_holds_on_cd_sign(n: int) -> None:
    degree.check_point_family(n, degree.phi_table(n, cd_sign))


@pytest.mark.parametrize("n", range(3, 7))
def test_point_family_rejects_an_edited_table(n: int) -> None:
    dim, quarter = 1 << n, 1 << (n - 2)
    phi = degree.phi_table(n, cd_sign)
    # phi(j, x) enters g_ij directly, so flipping it at one x != 0 flips the family's phase at that x.
    edited = phi.copy()
    edited[(dim >> 1) + quarter + quarter - 1, dim - 1] ^= 1
    with pytest.raises(degree.Mismatch, match="point pairs"):
        degree.check_point_family(n, edited)
    # phi(i, j) is the constant term; flipping it for m = 0 turns N(z) into delta_0(z).
    shifted = phi.copy()
    shifted[dim >> 1, (dim >> 1) + quarter] ^= 1
    with pytest.raises(degree.Mismatch, match="point pairs"):
        degree.check_point_family(n, shifted)
