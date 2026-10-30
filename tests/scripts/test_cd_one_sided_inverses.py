"""Contracts for cd_one_sided_inverses: the multiplication matrices are cd_multiply_exact's, the basis identities
decide the adjoint laws, kernels of L_a and R_a agree on the sedenion zero divisor e_1 + e_10, and each check
rejects a planted defect: a flipped sign table entry per identity, a kernel vector with a real part, a corrupted
b a product, a wrong conjugation under the canonical inverse, and a right matrix with one flipped sign.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Sequence
from fractions import Fraction

import cd_one_sided_inverses as osi
import pytest

import parallel
from cd_core import cd_multiply_exact

E1_PLUS_E10 = (0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0)
D32_ELEMENT = tuple(1 if i in (3, 5, 17, 30) else 0 for i in range(32))


def unit(dim: int, index: int) -> list[Fraction]:
    e = [Fraction(0)] * dim
    e[index] = Fraction(1)
    return e


def test_matrices_are_the_columns_of_cd_multiply_exact() -> None:
    for dim, a in ((16, E1_PLUS_E10), (32, D32_ELEMENT)):
        left, right = osi.left_matrix(dim, a), osi.right_matrix(dim, a)
        for i in range(dim):
            if [row[i] for row in left] != list(cd_multiply_exact(dim, a, unit(dim, i))):
                raise AssertionError(f"D={dim}: column {i} of L_a departs from a e_{i}")
            if [row[i] for row in right] != list(cd_multiply_exact(dim, unit(dim, i), a)):
                raise AssertionError(f"D={dim}: column {i} of R_a departs from e_{i} a")


def test_basis_identities_hold_through_dimension_64() -> None:
    for dim in (2, 4, 8, 16, 32, 64):
        if osi.identity_record(dim)["basis_pairs"] != dim * dim:
            raise AssertionError(dim)


def flipped_table(dim: int, cells: tuple[tuple[int, int], ...]) -> Callable[[int], tuple[tuple[int, ...], ...]]:
    table = [list(row) for row in osi.sign_table(dim)]
    for i, j in cells:
        table[i][j] = -table[i][j]
    frozen = tuple(tuple(row) for row in table)
    return lambda _dim: frozen


@pytest.mark.parametrize(
    ("cells", "identity"),
    [(((0, 0),), "L1"), (((1, 1),), "L2"), (((3, 1),), "L2'")],
    ids=["L1", "L2", "L2'"],
)
def test_one_flipped_sign_fails_the_named_identity_first(
    monkeypatch: pytest.MonkeyPatch, cells: tuple[tuple[int, int], ...], identity: str
) -> None:
    monkeypatch.setattr(osi, "sign_table", flipped_table(4, cells))
    with pytest.raises(osi.ContractError, match=f"{identity} fails"):
        osi.identity_record(4)


def test_conjugation_fixing_a_unit_fails_the_identities(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(osi, "conj_sign", lambda index: 1 if index in (0, 1) else -1)
    with pytest.raises(osi.ContractError):
        osi.identity_record(4)


def test_sedenion_zero_divisor_has_equal_four_dimensional_annihilators() -> None:
    left = osi.kernel(osi.left_matrix(16, E1_PLUS_E10))
    right = osi.kernel(osi.right_matrix(16, E1_PLUS_E10))
    if len(left) != 4 or not osi.same_span(left, right):
        raise AssertionError((len(left), len(right)))
    expected = {"kernel_dimension": 4, "inverse_offsets_checked": 4, "one_sided": 0}
    if osi.element_check((16, E1_PLUS_E10)) != expected:
        raise AssertionError("element_check departs from four checked offsets with no one-sided inverse")


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
    with pytest.raises(osi.ContractError, match="differ"):
        osi.element_check((16, E1_PLUS_E10))


def test_a_kernel_vector_with_a_real_part_fails_purity(monkeypatch: pytest.MonkeyPatch) -> None:
    impure = [[Fraction(1)] + [Fraction(0)] * 15]
    monkeypatch.setattr(osi, "kernel", lambda _matrix: [row[:] for row in impure])
    with pytest.raises(osi.ContractError, match="real part"):
        osi.element_check((16, E1_PLUS_E10))


def test_a_corrupted_b_a_product_is_a_one_sided_inverse(monkeypatch: pytest.MonkeyPatch) -> None:
    a = tuple(Fraction(x) for x in E1_PLUS_E10)

    def corrupted(dim: int, x: Sequence[Fraction | int], y: Sequence[Fraction | int]) -> tuple[Fraction, ...]:
        if tuple(y) == a:
            return tuple([Fraction(0)] * dim)
        return tuple(cd_multiply_exact(dim, x, y))

    monkeypatch.setattr(osi, "cd_multiply_exact", corrupted)
    with pytest.raises(osi.ContractError, match="b a != 1"):
        osi.element_check((16, E1_PLUS_E10))


def test_a_wrong_conjugation_breaks_the_canonical_inverse(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(osi, "conj", lambda a: list(a))
    with pytest.raises(osi.ContractError, match="a b != 1"):
        osi.element_check((16, E1_PLUS_E10))


def test_invertible_element_reports_no_kernel() -> None:
    a = tuple([1] + [0] * 15)
    if osi.element_check((16, a)) != {"kernel_dimension": 0, "inverse_offsets_checked": 0, "one_sided": 0}:
        raise AssertionError("e_0 has a kernel")


def test_family_sizes_and_membership() -> None:
    sizes = (len(osi.two_blades(16)), len(osi.three_units(16)), len(osi.doubly_pure(16)), len(osi.two_blades(32)))
    if sizes != (210, 455, 1764, 930):
        raise AssertionError(sizes)
    if [name for name, _ in osi.families(32)] != ["two_blade"]:
        raise AssertionError("dimension 32 checks the two-blade family alone")
    if set(osi.doubly_pure(16)) & set(osi.two_blades(16)):
        raise AssertionError("the doubly pure grid repeats a two-blade")


def test_pooled_and_serial_runs_write_the_same_bytes(monkeypatch: pytest.MonkeyPatch) -> None:
    """The test session caps the pool at one worker (tests/conftest.py); the pooled run lifts it to two."""
    if parallel.available_cpus() < 2:
        pytest.skip("the CPU budget holds one worker, so no pooled run is possible")
    monkeypatch.setattr(osi, "KERNEL_DIMENSIONS", (16,))
    monkeypatch.setattr(osi, "families", lambda dim: [("two_blade", osi.two_blades)])
    if len(osi.two_blades(16)) < parallel.MIN_PARALLEL_ITEMS:
        raise AssertionError("the two-blade family is too small to reach the pool")
    monkeypatch.setitem(os.environ, "GOROROBA_WORKERS", "2")
    if parallel.workers() != 2:
        raise AssertionError("GOROROBA_WORKERS=2 leaves the pool at one worker")
    pooled = osi.render(osi.record())
    monkeypatch.setitem(os.environ, "GOROROBA_WORKERS", "1")
    if parallel.workers() != 1:
        raise AssertionError("GOROROBA_WORKERS=1 leaves the pool wider than one worker")
    if osi.render(osi.record()) != pooled:
        raise AssertionError("the serial record departs from the pooled record")
