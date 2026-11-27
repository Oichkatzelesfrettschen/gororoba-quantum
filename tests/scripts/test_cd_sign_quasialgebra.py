"""Contracts for the quasialgebra form of cd_sign (ledger A5-648 and A5-649).

cd_sign(p, q) equals F(q, p) for the cochain F = (-1)^f that the standard Cayley-Dickson process of Albuquerque and
Majid (arXiv math/9802116, Corollary 4.3) builds; the associativity cocycle phi = dF is 1 off the generic set Gamma,
the condition that makes the signed basis set a quasigroup (Klim and Majid, arXiv 0906.5026, Proposition 3.7); and the
count of triples with phi = -1 follows the recursion of their Proposition 4.5. An edited cochain fails each check.
"""

from __future__ import annotations

import pytest

from cd_core import cd_sign

Table = list[list[int]]


def majid_cochain(n: int) -> Table:
    """F = (-1)^f on (Z_2)^n with f((x, a), (y, b)) = f(x, y)(1 - a) + f(y, x) a + b f(x, x) + a b."""
    f = [[0]]
    for k in range(n):
        half = 1 << k
        g = [[0] * (2 * half) for _ in range(2 * half)]
        for x in range(half):
            for y in range(half):
                for a in (0, 1):
                    for b in (0, 1):
                        g[x + a * half][y + b * half] = (f[x][y] * (1 - a) + f[y][x] * a + b * f[x][x] + a * b) % 2
        f = g
    return [[-1 if value else 1 for value in row] for row in f]


def cd_table(n: int) -> Table:
    dim = 1 << n
    return [[cd_sign(dim, p, q) for q in range(dim)] for p in range(dim)]


def phi(s: Table, a: int, b: int, c: int) -> int:
    """-1 exactly when (e_a e_b) e_c != e_a (e_b e_c) for the signs s."""
    return s[a][b] * s[a ^ b][c] * s[b][c] * s[a][b ^ c]


def generic(x: int, y: int, z: int) -> bool:
    return x != 0 and y != 0 and x != y and z not in (0, x, y, x ^ y)


def census(s: Table) -> tuple[int, bool]:
    """Triples with phi = -1, and whether phi = 1 on every triple outside Gamma."""
    dim, count, degenerate = len(s), 0, True
    for x in range(dim):
        for y in range(dim):
            for z in range(dim):
                value = phi(s, x, y, z)
                count += value == -1
                degenerate = degenerate and (value == 1 or generic(x, y, z))
    return count, degenerate


@pytest.mark.parametrize("n", range(1, 7))
def test_cd_sign_is_the_transposed_majid_cochain(n: int) -> None:
    s, f = cd_table(n), majid_cochain(n)
    if not all(s[p][q] == f[q][p] for p in range(1 << n) for q in range(1 << n)):
        raise AssertionError(f"cd_sign differs from the transposed cochain at n = {n}")


@pytest.mark.parametrize("n", range(1, 7))
def test_phi_is_one_off_gamma_and_the_count_follows_the_formula(n: int) -> None:
    dim = 1 << n
    count, degenerate = census(cd_table(n))
    if not degenerate or count != (dim - 2) * (dim - 4) * (dim + 6) // 2:
        raise AssertionError(f"n = {n}: count {count}, phi = 1 off Gamma {degenerate}")


def test_an_edited_cochain_fails_both_checks() -> None:
    s = cd_table(4)
    s[3][5] = -s[3][5]
    f = majid_cochain(4)
    if all(s[p][q] == f[q][p] for p in range(16) for q in range(16)):
        raise AssertionError("the edited table still matches the cochain")
    count, degenerate = census(s)
    if degenerate and count == 1848:
        raise AssertionError("the edited table still passes the census")
