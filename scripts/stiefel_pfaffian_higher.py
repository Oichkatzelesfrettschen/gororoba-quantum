"""Exact Pfaffian transport for doubly pure elements of A_n, n = 6, 7, 8, and what survives of the A_5 Stiefel argument.

A_n is the cd_core doubling of two copies of A_(n-1), h = 2^(n-1) coordinates each. A doubly pure y = (p, q) has p, q
pure (y_0 = y_h = 0); z = p + i q in C^(h-1) with i a scalar unit and every dot product complex bilinear; N = z.conj z;
Q = z.z, so that Q = 0 is the Stiefel condition |p| = |q|, <p, q> = 0; C_z is the Im-block of left multiplication by
z on Im (A_(n-1))_C; A(z, t) = [[0, -t^T], [t, C_z]] is h x h.

Identities and facts checked exactly from cd_core.cd_sign:
- Transport. The matrix identity Phi L_y = M Phi holds on every imaginary basis element of A_6 and A_7 (A_8 under
  --explore), where Phi (r, s) = (r, conj s) and M is the real form of xi -> A(z, conj z) conj(xi). Both sides are
  real-linear in y, so rank_R L_y = 2 rank_C A(z, conj z) for every doubly pure y. The identity holds for every n,
  because for pure p, q and pure xi, xi q = -q xi - 2 <xi, q>.
- Cofactors. C_z is skew with C_z z = 0 over Z[z]. At one Gaussian integer point rank_C C_z = h - 2, so the maximal
  Pfaffians P_j = (-1)^(j-1) Pf(C_z without row and column j) satisfy P_j = f z_j over Z[z] with f of degree
  2^(n-2) - 2, Pf A(z, t) = -(z.t) f(z), and det L_y = N^4 |f(z)|^4. The record checks the integer identity
  det L_y |z_j|^4 = N^4 det_R(C_z without j) at five points of A_6 and one each of A_7, A_8, and f_4 = Q,
  f_5 = Q G with Q, G irreducible.
- Irreducibility. f_6 is irreducible over Q, by an exact six-coordinate slice of 792 terms and by a modular line
  restriction, and f_7 by a modular line restriction (a factorization of f over Z factors every line polynomial whose
  leading coefficient f(b) is nonzero modulo p).
- Slices. On three coordinates f = Q^(2^(n-3) - 1) for n = 4 .. 8. On S = {2, 5, 14, 16, 20, 22} in A_6, Q does not
  divide f: the normal form of f modulo Q is 256 z5^2 z14^4 z16^2 z20^2 z22^2 (z14^2 + z16^2 + z20^2 + z22^2). With z_16
  replaced by z_3 in S, Q divides f.
- Stiefel witnesses. The five-term element e_12 + e_15 + e_16 + e_23 + 2 e_34 and the six-term element
  e_2 + e_5 + e_20 + e_46 + e_48 + e_54 of A_6, and one disjoint-support element each of A_6, A_7, A_8, are Stiefel
  with full-rank L_y. The same index patterns lie in the hyperplane z_(h/2) = 0 of A_7 and A_8 and are zero
  divisors there.
- Simple families. Every e_i + i e_j is a zero divisor in A_5, A_6, A_7. A disjoint-support Stiefel element that
  avoids z_(h/2) has nullity 4 at A_6, A_7, A_8; one that avoids another coordinate has nullity 0.

Falsifiers: a transport mismatch on a basis pair; C_z not skew or C_z z != 0; a determinant identity off by a
factor; a slice whose divisibility by Q differs from the record; a witness of rank below its dimension; a pair
e_i + i e_j with nullity 0; an avoiding element whose nullity differs from the table; a recorded line that is
reducible.

Usage:
    "$PYTHON" scripts/stiefel_pfaffian_higher.py --out docs/evidence/stiefel-pfaffian-higher/result.json
    "$PYTHON" scripts/stiefel_pfaffian_higher.py --check docs/evidence/stiefel-pfaffian-higher/result.json
    "$PYTHON" scripts/stiefel_pfaffian_higher.py --self-test
    "$PYTHON" scripts/stiefel_pfaffian_higher.py --explore docs/evidence/stiefel-pfaffian-higher/explore.json
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.metadata
import itertools
import json
import math
import sys
from collections import Counter
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import flint
import flint.utils.flint_exceptions
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402
from cd_core import cd_multiply_exact, cd_sign  # noqa: E402

SCHEMA = "stiefel-pfaffian-higher-v1"
PRIME = (1 << 61) - 1
# Modular line search for an irreducible restriction of f: lines t = 0, 1, ... of the arithmetic family below.
LINE_LIMIT = 400
# Lines on which f mod p is irreducible of full degree, found by irreducible_line in --explore and verified by the gate.
KNOWN_LINES = {6: 30, 7: 52, 8: 112}
GATE_TRANSPORT = (6, 7)
GATE_COFACTOR = (6, 7, 8)
SLICE_THREE = (1, 2, 3)
SLICE_SIX = (2, 5, 14, 16, 20, 22)
SLICE_NO_SIXTEEN = (2, 5, 14, 20, 22, 3)
SLICE_SEVEN = (3, 4, 13, 14, 16, 22, 26)
SLICE_EIGHT = (3, 4, 10, 16, 21, 25, 27, 28)
# z_2, z_5, z_14, z_16, z_20, z_22 = 1, 1, i, i, 1, i has Q = 1 + 1 - 1 - 1 + 1 - 1 = 0 and z_2^2 + z_5^2 = 2.
SIX_TERM_P = (2, 5, 20)
SIX_TERM_Q = (14, 16, 22)
# z_12, z_15, z_16, z_23 = 1 and z_2 = 2i have Q = 4 - 4 = 0.
FIVE_TERM_P = (12, 15, 16, 23)
FIVE_TERM_Q = 2


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"stiefel_pfaffian_higher: {message}")


@functools.cache
def sign_table(dim: int) -> Any:
    """cd_sign(dim, p, q) as an int64 array."""
    return np.array([[cd_sign(dim, p, q) for q in range(dim)] for p in range(dim)], dtype=np.int64)


def left_matrix(dim: int, y: Sequence[int]) -> Any:
    """L_y with (r, c) entry the coefficient of e_r in y e_c: y[r ^ c] cd_sign(dim, r ^ c, c)."""
    index = np.arange(dim)
    xor = index[:, None] ^ index[None, :]
    return np.array(y, dtype=np.int64)[xor] * sign_table(dim)[xor, index[None, :]]


def exact_rank(matrix: Any) -> int:
    return int(flint.fmpz_mat(matrix.tolist()).rank())


def nullity(dim: int, y: Sequence[int]) -> int:
    return dim - exact_rank(left_matrix(dim, y))


def left_matrix_cross_check(dim: int) -> int:
    """L_y x against cd_core.cd_multiply_exact on deterministic small integer vectors."""
    checked = 0
    for shift in range(4):
        y = [((7 * k + 3 * shift) % 5) - 2 for k in range(dim)]
        x = [((11 * k + shift * k * k) % 7) - 3 for k in range(dim)]
        product = left_matrix(dim, y) @ np.array(x, dtype=np.int64)
        _require(tuple(int(v) for v in product) == cd_multiply_exact(dim, y, x), f"L_y differs from cd_core at {dim}")
        checked += 1
    return checked


def basis_vector(dim: int, index: int) -> list[int]:
    return [int(k == index) for k in range(dim)]


def element(dim: int, p_terms: dict[int, int], q_terms: dict[int, int]) -> list[int]:
    """y = p + q-shifted with p, q pure: p_terms on coordinates 1 .. h - 1, q_terms on h + 1 .. 2h - 1."""
    half = dim // 2
    y = [0] * dim
    for k, value in p_terms.items():
        y[k] = value
    for k, value in q_terms.items():
        y[half + k] = value
    return y


def stiefel_defect(dim: int, y: Sequence[int]) -> tuple[int, int]:
    """(|p|^2 - |q|^2, <p, q>): both vanish exactly on Stiefel elements."""
    half = dim // 2
    p, q = y[:half], y[half:]
    _require(p[0] == 0 and q[0] == 0, "an element is not doubly pure")
    return sum(a * a for a in p) - sum(b * b for b in q), sum(a * b for a, b in zip(p, q, strict=True))


def disjoint_stiefel(dim: int, avoid: int | None = None) -> list[int]:
    """Deterministic Stiefel element: values on the first half of the pure coordinates (minus avoid), the same values
    with alternating signs, permuted by k -> r k mod m, on the second half."""
    half = dim // 2
    coordinates = [k for k in range(1, half) if k != avoid]
    if len(coordinates) % 2:
        coordinates = coordinates[:-1]
    count = len(coordinates) // 2
    multiplier = next(r for r in (3, 5, 7, 11, 13, 17) if math.gcd(r, count) == 1)
    values = [((3 * k + 1) % 5) - 2 or 3 for k in range(1, count + 1)]
    y = [0] * dim
    for position in range(count):
        y[coordinates[position]] = values[position]
    for position in range(count):
        target = coordinates[count + (position * multiplier) % count]
        y[half + target] = values[position] * (1 if position % 2 else -1)
    return y


# ---- transport -----------------------------------------------------------------------------------------------------


def bordered_real_form(half: int, zr: Any, zi: Any, tr: Any, ti: Any) -> tuple[Any, Any]:
    """Real and imaginary parts of A(z, t) for z = zr + i zi, t = tr + i ti (arrays of length half, entry 0 unused)."""
    signs = sign_table(half)
    index = np.arange(1, half)
    xor = index[:, None] ^ index[None, :]
    off = index[:, None] != index[None, :]
    block = signs[xor, index[None, :]] * off
    re = np.zeros((half, half), dtype=np.int64)
    im = np.zeros((half, half), dtype=np.int64)
    re[0, 1:], im[0, 1:] = -tr[1:], -ti[1:]
    re[1:, 0], im[1:, 0] = tr[1:], ti[1:]
    re[1:, 1:] = block * zr[xor]
    im[1:, 1:] = block * zi[xor]
    return re, im


def transport_case(item: tuple[int, int, bool]) -> bool:
    """Phi L_y = M Phi for y = e_k, with Phi (r, s) = (r, conj s) and M the real form of xi -> A(z, conj z) conj xi."""
    dim, k, conjugate_s = item
    half = dim // 2
    y = basis_vector(dim, k)
    zr = np.zeros(half, dtype=np.int64)
    zi = np.zeros(half, dtype=np.int64)
    if k < half:
        zr[k] = 1
    else:
        zi[k - half] = 1
    re, im = bordered_real_form(half, zr, zi, zr, -zi)
    conj = np.diag([1] + [-1 if conjugate_s else 1] * (half - 1)).astype(np.int64)
    zeros = np.zeros((half, half), dtype=np.int64)
    phi = np.block([[np.eye(half, dtype=np.int64), zeros], [zeros, conj]])
    m = np.block([[re, im], [im, -re]])
    return bool((phi @ left_matrix(dim, y) == m @ phi).all())


def transport(n: int, conjugate_s: bool = True) -> dict[str, Any]:
    dim = 1 << n
    half = dim // 2
    cases = [(dim, k, conjugate_s) for k in range(dim) if k not in (0, half)]
    return {
        "dimension": dim,
        "imaginary_basis_elements": len(cases),
        "agreeing": sum(parallel.ordered_map(transport_case, cases)),
    }


# ---- cofactors -----------------------------------------------------------------------------------------------------


def cross_identities(n: int, flip: tuple[int, int] | None = None) -> dict[str, Any]:
    """C_z skew and C_z z = 0 over Z[z_1 .. z_(h-1)] from cd_sign; flip negates one structure constant."""
    half = 1 << (n - 1)
    signs = sign_table(half).copy()
    if flip is not None:
        a, b = flip
        signs[a, b] = -signs[a, b]
    ring = flint.fmpz_mpoly_ctx.get([f"z{k}" for k in range(1, half)], "lex")
    z = list(ring.gens())
    zero = ring.from_dict({})
    entry: dict[tuple[int, int], Any] = {}
    for a in range(1, half):
        for b in range(1, half):
            if a != b:
                entry[a, b] = z[(a ^ b) - 1] * int(signs[a ^ b, b])
    skew = all(entry[a, b] + entry[b, a] == 0 for a in range(1, half) for b in range(1, a))
    annihilates = True
    for a in range(1, half):
        total = zero
        for b in range(1, half):
            if a != b:
                total = total + entry[a, b] * z[b - 1]
        annihilates = annihilates and total == 0
    return {"cross_matrix_skew": skew, "cross_matrix_annihilates_z": annihilates}


def cross_real_form(half: int, p: Sequence[int], q: Sequence[int], drop: int | None = None) -> Any:
    """The real form [[C_p, -C_q], [C_q, C_p]] of C_z with row and column `drop` (1-based) removed."""
    signs = sign_table(half)
    index = np.arange(1, half)
    xor = index[:, None] ^ index[None, :]
    block = signs[xor, index[None, :]] * (index[:, None] != index[None, :])
    cp = block * np.array([0, *p], dtype=np.int64)[xor]
    cq = block * np.array([0, *q], dtype=np.int64)[xor]
    if drop is not None:
        keep = [k for k in range(half - 1) if k != drop - 1]
        cp, cq = cp[np.ix_(keep, keep)], cq[np.ix_(keep, keep)]
    return np.block([[cp, -cq], [cq, cp]])


def gaussian_point(half: int) -> tuple[list[int], list[int]]:
    """A deterministic Gaussian integer point z_k = (k mod 7) - 3 + i ((k^2 + 1) mod 5 - 2) for k = 1 .. h - 1."""
    return [(k % 7) - 3 + (k // 7) for k in range(1, half)], [((k * k + 1) % 5) - 2 + (k % 3) for k in range(1, half)]


def cofactor_rank(n: int) -> dict[str, Any]:
    """rank_C C_z at the Gaussian integer point: h - 2 makes P_j proportional to z_j over Z[z]."""
    half = 1 << (n - 1)
    p, q = gaussian_point(half)
    rank = exact_rank(cross_real_form(half, p, q)) // 2
    return {"dimension": 1 << n, "point_rank_cross": rank, "full_rank": half - 2, "z_nonzero": any(p) or any(q)}


def degree_identity(dim: int, y: Sequence[int]) -> dict[str, Any]:
    """det L_y |z_j|^4 = N^4 det_R(C_z without j) for the first two coordinates j with z_j != 0, and nullity."""
    half = dim // 2
    p, q = list(y[1:half]), list(y[half + 1 :])
    norm = sum(a * a for a in p) + sum(b * b for b in q)
    det = int(flint.fmpz_mat(left_matrix(dim, y).tolist()).det())
    coords = [j for j in range(1, half) if p[j - 1] or q[j - 1]][:2]
    holds = []
    for j in coords:
        cofactor = int(flint.fmpz_mat(cross_real_form(half, p, q, drop=j).tolist()).det())
        modulus = p[j - 1] ** 2 + q[j - 1] ** 2
        holds.append(det * modulus**2 == norm**4 * cofactor)
    return {"det_L_zero": det == 0, "identity_holds": holds, "coordinates": coords, "norm": norm}


# ---- slices --------------------------------------------------------------------------------------------------------


def pfaffian_function(matrix: list[list[Any]], zero: Any, one: Any) -> Callable[[int], Any]:
    """Pf of the principal submatrix on a bit mask, by expansion along its first index, memoized."""
    memo: dict[int, Any] = {0: one}

    def pf(mask: int) -> Any:
        if mask in memo:
            return memo[mask]
        indices = [i for i in range(len(matrix)) if mask >> i & 1]
        value = zero
        first = indices[0]
        for position, j in enumerate(indices[1:], start=1):
            entry = matrix[first][j]
            if entry == zero:
                continue
            term = entry * pf(mask & ~(1 << first) & ~(1 << j))
            value = value + term if position % 2 else value - term
        memo[mask] = value
        return value

    return pf


def slice_polynomial(n: int, support: Sequence[int]) -> tuple[Any, Any]:
    """(f, Q) over Z[z_S]: f = P_j / z_j for j the first coordinate of S, with z_k = 0 off S."""
    half = 1 << (n - 1)
    signs = sign_table(half)
    ctx = flint.fmpz_mpoly_ctx.get([f"x{k}" for k in support], "lex")
    gens = ctx.gens()
    zero = ctx.from_dict({})
    one = ctx.from_dict({(0,) * len(support): 1})
    z = [zero] * (half - 1)
    for k, g in zip(support, gens, strict=True):
        z[k - 1] = g
    matrix = [
        [z[(a ^ b) - 1] * int(signs[a ^ b, b]) if a != b else zero for b in range(1, half)] for a in range(1, half)
    ]
    j = support[0] - 1
    keep = [k for k in range(half - 1) if k != j]
    pf = pfaffian_function([[matrix[a][b] for b in keep] for a in keep], zero, one)
    cofactor = pf((1 << (half - 2)) - 1) * (1 if j % 2 == 0 else -1)
    f = cofactor // gens[0]
    _require(f * gens[0] == cofactor, f"P_j is not divisible by z_j on {list(support)}")
    return f, sum((g * g for g in gens), zero)


def reduce_mod_q(f: Any, q: Any) -> Any:
    """Normal form of f modulo Q (Q monic in the lex-leading variable)."""
    return divmod(f, q)[1]


def slice_record(n: int, support: Sequence[int]) -> dict[str, Any]:
    f, q = slice_polynomial(n, support)
    remainder = reduce_mod_q(f, q)
    factors = f.factor()
    special = (1 << (n - 1)) // 2
    exponents = (
        [e[support.index(special)] for e in remainder.to_dict()] if special in support and support[0] != special else []
    )
    return {
        "dimension": 1 << n,
        "support": list(support),
        "terms": len(f),
        "degree": 2 ** (n - 2) - 2,
        "factor_term_counts": [[len(g), e] for g, e in factors[1]],
        "q_divides_f": remainder == 0,
        "remainder_terms": len(remainder),
        "min_special_exponent": int(min(exponents)) if exponents else None,
        "f_is_q_power": len(factors[1]) == 1 and factors[1][0][0] == q,
        "remainder": str(remainder),
    }


def six_slice_closed_form() -> dict[str, Any]:
    """The normal form of f modulo Q on S = {2, 5, 14, 16, 20, 22} against its closed forms."""
    f, q = slice_polynomial(6, SLICE_SIX)
    names = {k: g for k, g in zip(SLICE_SIX, f.context().gens(), strict=True)}
    x2, x5, x14, x16, x20, x22 = (names[k] for k in SLICE_SIX)
    closed = 256 * x5**2 * x14**4 * x16**2 * x20**2 * x22**2 * (x14**2 + x16**2 + x20**2 + x22**2)
    mod_q = -256 * x5**2 * x14**4 * x16**2 * x20**2 * x22**2 * (x2**2 + x5**2)
    remainder = reduce_mod_q(f, q)
    return {
        "remainder_is_closed_form": remainder == closed,
        "closed_form_equals_minus_x2_x5_form_mod_q": reduce_mod_q(closed - mod_q, q) == 0,
        "f_irreducible": [[len(g), e] for g, e in f.factor()[1]] == [[len(f), 1]],
        "f_terms": len(f),
    }


def cofactor_polynomials_small() -> dict[str, Any]:
    """Over Z[z]: f_4 = Q at h = 8 and f_5 = Q G, with G irreducible, at h = 16."""
    out: dict[str, Any] = {}
    for half in (8, 16):
        signs = sign_table(half)
        ctx = flint.fmpz_mpoly_ctx.get([f"z{k}" for k in range(1, half)], "lex")
        z = list(ctx.gens())
        zero, one = ctx.from_dict({}), ctx.from_dict({(0,) * (half - 1): 1})
        matrix = [
            [z[(a ^ b) - 1] * int(signs[a ^ b, b]) if a != b else zero for b in range(1, half)] for a in range(1, half)
        ]
        pf = pfaffian_function(matrix, zero, one)
        full = (1 << (half - 1)) - 1
        cofactors = [pf(full & ~(1 << j)) * (1 if j % 2 == 0 else -1) for j in range(half - 1)]
        q = sum((x * x for x in z), zero)
        if half == 8:
            out["f4_equals_q"] = all(c == q * z[j] for j, c in enumerate(cofactors))
        else:
            u, v = z[:7], z[8:]
            big_u = sum((x * x for x in u), zero)
            big_v = sum((x * x for x in v), zero)
            big_w = sum((a * b for a, b in zip(u, v, strict=True)), zero)
            g = q * q - 4 * (big_u * big_v - big_w * big_w)
            out["f5_equals_q_g"] = all(c == q * g * z[j] for j, c in enumerate(cofactors))
            out["g_factor_term_counts"] = [[len(x), e] for x, e in g.factor()[1]]
            out["q_factor_term_counts"] = [[len(x), e] for x, e in q.factor()[1]]
    return out


# ---- modular line restriction --------------------------------------------------------------------------------------


@functools.cache
def sign_rows(half: int) -> list[list[int]]:
    return [[int(v) for v in row] for row in sign_table(half).tolist()]


def f_squared_mod_p(item: tuple[int, list[int]]) -> int:
    """f(z)^2 mod p = det(C_z without row and column j) / z_j^2, j the first coordinate with z_j != 0 mod p."""
    half, z = item
    signs = sign_rows(half)
    j = next(k + 1 for k in range(half - 1) if z[k] % PRIME)
    keep = [k for k in range(1, half) if k != j]
    rows = [[signs[a ^ b][b] * z[(a ^ b) - 1] % PRIME if a != b else 0 for b in keep] for a in keep]
    return int(flint.nmod_mat(rows, PRIME).det()) * pow(z[j - 1] ** 2, -1, PRIME) % PRIME


def interpolate_square(half: int, a: Sequence[int], b: Sequence[int], degree: int) -> Any:
    """f(a + s b)^2 mod p as a polynomial of degree at most 2 `degree` in s, cross-checked at two further points."""
    xs = list(range(1, 2 * degree + 4))
    points = [(half, [(u + s * v) % PRIME for u, v in zip(a, b, strict=True)]) for s in xs]
    ys = parallel.ordered_map(f_squared_mod_p, points, min_items=8)
    count = 2 * degree + 1
    full = flint.nmod_poly([1], PRIME)
    for x in xs[:count]:
        full = full * flint.nmod_poly([-x % PRIME, 1], PRIME)
    poly = flint.nmod_poly([0], PRIME)
    for i in range(count):
        quotient = full // flint.nmod_poly([-xs[i] % PRIME, 1], PRIME)
        scale = ys[i] * pow(int(quotient(xs[i])), -1, PRIME) % PRIME
        poly += quotient * scale
    for x, y in zip(xs[count:], ys[count:], strict=True):
        _require(int(poly(x)) == y, "the line polynomial of f^2 has degree above 2 (2^(n-2) - 2)")
    return poly


def f_squared_crosschecks() -> dict[str, Any]:
    """f^2 from det(C_z without j) / z_j^2 against exact f: (Q G)^2 at two A_5 points, the A_6 slice polynomial."""
    out: dict[str, Any] = {}
    agree5 = []
    for t in (0, 1):
        z = [((k * k + 3 * k + 1) * (t + 2) + 7 * t) % PRIME for k in range(1, 16)]
        u, mu, v = z[:7], z[7], z[8:]
        big_u, big_v, big_w = (
            sum(x * y for x, y in zip(a, b, strict=True)) % PRIME for a, b in ((u, u), (v, v), (u, v))
        )
        q = (big_u + mu * mu + big_v) % PRIME
        g = (q * q - 4 * (big_u * big_v - big_w * big_w)) % PRIME
        agree5.append(f_squared_mod_p((16, z)) == (q * g) ** 2 % PRIME)
    out["a5_q_g_squared"] = agree5
    f, _ = slice_polynomial(6, SLICE_SIX)
    values = [3, 5, 7, 11, 13, 17]
    z = [0] * 31
    for k, value in zip(SLICE_SIX, values, strict=True):
        z[k - 1] = value
    exact = int(f(*values)) % PRIME
    out["a6_slice_polynomial_squared"] = f_squared_mod_p((32, z)) == exact * exact % PRIME
    return out


def line_ab(n: int, t: int) -> tuple[list[int], list[int]]:
    half = 1 << (n - 1)
    a = [((k * k + 3 * k + 1) * (t + 2) + 7 * t) % PRIME for k in range(1, half)]
    b = [(5 * k**3 + 2 + t) % PRIME for k in range(1, half)]
    return a, b


def line_square(n: int, t: int) -> Any:
    """f(a + s b)^2 mod p for the arithmetic line number t."""
    a, b = line_ab(n, t)
    return interpolate_square(1 << (n - 1), a, b, 2 ** (n - 2) - 2)


def modular_sqrt(value: int) -> int | None:
    try:
        return int(flint.nmod(value % PRIME, PRIME).sqrt())
    except flint.utils.flint_exceptions.DomainError:
        return None


def isotropic_line(half: int, offset: int) -> tuple[list[int], list[int]]:
    """Vectors a, b in F_p^(h-1) with a.a = a.b = b.b = 0: arithmetic entries except three solved coordinates, the
    first candidate sequence (a bump of one free entry) for which the needed square roots exist."""
    count = half - 1
    inverse_two = pow(2, -1, PRIME)
    for bump in range(1000):
        a = [
            ((k * k + 3 * k + 5) * (offset + 2) + offset + (bump if k == count - 2 else 0)) % PRIME
            for k in range(count)
        ]
        last = modular_sqrt(-sum(x * x for x in a[:-1]))
        if last is None:
            continue
        a[-1] = last
        b = [(5 * k**3 + 2 + offset + (bump if k == count - 1 else 0)) % PRIME for k in range(count)]
        rest_lin = sum(x * y for x, y in zip(a[:-3], b[:-3], strict=True)) % PRIME
        rest_sq = sum(x * x for x in b[:-3]) % PRIME
        w = b[-1]
        inverse_a = pow(a[-3], -1, PRIME)
        # u = b[-3] = c0 + c1 v from a.b = 0, then v = b[-2] from b.b = 0.
        c0 = (-(a[-1] * w + rest_lin) * inverse_a) % PRIME
        c1 = (-a[-2] * inverse_a) % PRIME
        qa = (c1 * c1 + 1) % PRIME
        qb = 2 * c0 * c1 % PRIME
        qc = (c0 * c0 + w * w + rest_sq) % PRIME
        root = modular_sqrt(qb * qb - 4 * qa * qc)
        if root is None:
            continue
        v = (-qb + root) * inverse_two * pow(qa, -1, PRIME) % PRIME
        b[-2] = v
        b[-3] = (c0 + c1 * v) % PRIME
        return a, b
    raise SystemExit("stiefel_pfaffian_higher: no isotropic line found")


def special_root_multiplicity(n: int, offset: int) -> dict[str, Any]:
    """Multiplicity of the root of z_(h/2)(a + s b) in f(a + s b) on an isotropic line (a, b) of the quadric Q = 0."""
    half = 1 << (n - 1)
    a, b = isotropic_line(half, offset)
    _require(
        sum(x * x for x in a) % PRIME == 0
        and sum(x * y for x, y in zip(a, b, strict=True)) % PRIME == 0
        and sum(y * y for y in b) % PRIME == 0,
        "the line is not isotropic",
    )
    poly = interpolate_square(half, a, b, 2 ** (n - 2) - 2)
    special = half // 2 - 1
    root = (-a[special] * pow(b[special], -1, PRIME)) % PRIME
    multiplicity = 0
    quotient = poly
    while True:
        divided, remainder = divmod(quotient, flint.nmod_poly([-root % PRIME, 1], PRIME))
        if remainder != 0:
            break
        quotient, multiplicity = divided, multiplicity + 1
    # poly is f^2, so every multiplicity of f is half of the one found here.
    return {
        "dimension": 1 << n,
        "offset": offset,
        "degree_of_f": int(poly.degree()) // 2,
        "multiplicity_at_special_root": multiplicity // 2,
        "quotient_factor_degrees": sorted((int(g.degree()), e // 2) for g, e in quotient.factor()[1]),
    }


def line_is_irreducible(n: int, t: int) -> bool:
    """f(a + s b) mod p is irreducible of full degree d = 2^(n-2) - 2 on the arithmetic line number t, decided from
    f^2 = c g^2 with g irreducible of degree d. A factorization f = g h over Z with g, h of positive degree would factor
    the line polynomial into two factors of positive degree, because the leading coefficient f(b) is nonzero mod p;
    so this proves f irreducible over Q."""
    poly = line_square(n, t)
    factors = poly.factor()[1]
    degree = 2 ** (n - 2) - 2
    return (
        len(factors) == 1
        and factors[0][1] == 2
        and int(factors[0][0].degree()) == degree
        and poly.degree() == 2 * degree
    )


def irreducible_line(n: int) -> dict[str, Any]:
    """The first arithmetic line on which f mod p is irreducible (search, for --explore)."""
    first = next((t for t in range(LINE_LIMIT) if line_is_irreducible(n, t)), None)
    return {"dimension": 1 << n, "line": first, "degree": 2 ** (n - 2) - 2, "prime": PRIME}


def known_lines() -> dict[str, Any]:
    return {
        f"A_{n}": {
            "dimension": 1 << n,
            "line": t,
            "irreducible": line_is_irreducible(n, t),
            "degree": 2 ** (n - 2) - 2,
            "prime": PRIME,
        }
        for n, t in KNOWN_LINES.items()
    }


# ---- witnesses and families ----------------------------------------------------------------------------------------


def witness_record(dim: int, label: str, y: list[int]) -> dict[str, Any]:
    defect = stiefel_defect(dim, y)
    rank = exact_rank(left_matrix(dim, y))
    return {
        "label": label,
        "dimension": dim,
        "nonzero_coordinates": sum(1 for value in y if value),
        "stiefel_defect": list(defect),
        "rank": rank,
        "nullity": dim - rank,
        "element_sha256": hashlib.sha256(json.dumps(y).encode()).hexdigest(),
    }


def six_term(dim: int) -> list[int]:
    return element(dim, dict.fromkeys(SIX_TERM_P, 1), dict.fromkeys(SIX_TERM_Q, 1))


def five_term(dim: int) -> list[int]:
    return element(dim, dict.fromkeys(FIVE_TERM_P, 1), {FIVE_TERM_Q: 2})


def pair_table(n: int) -> dict[str, Any]:
    """Exact nullity of e_i + i e_j (y = e_i + e_(h+j)) over all i != j in 1 .. h - 1, split by whether the pair
    touches the coordinate h/2 (z_(h/2) != 0, outside the Biss-Christensen-Dugger-Isaksen hyperplane z_(h/2) = 0)."""
    dim = 1 << n
    half = dim // 2
    special = half // 2
    pairs = [(i, j) for i in range(1, half) for j in range(1, half) if i != j]
    values = parallel.ordered_map(pair_nullity, [(dim, i, j) for i, j in pairs], min_items=64)
    groups: dict[str, Counter[int]] = {"on_hyperplane": Counter(), "off_hyperplane": Counter()}
    for (i, j), value in zip(pairs, values, strict=True):
        groups["off_hyperplane" if special in (i, j) else "on_hyperplane"][value] += 1
    total = Counter(values)
    return {
        "dimension": dim,
        "pairs": len(pairs),
        "nullity_counts": {str(k): total[k] for k in sorted(total)},
        "off_hyperplane_pairs": sum(groups["off_hyperplane"].values()),
        "off_hyperplane_nullity_counts": {
            str(k): groups["off_hyperplane"][k] for k in sorted(groups["off_hyperplane"])
        },
    }


def pair_nullity(item: tuple[int, int, int]) -> int:
    dim, i, j = item
    return nullity(dim, element(dim, {i: 1}, {j: 1}))


def avoid_nullity(item: tuple[int, int]) -> int:
    dim, k = item
    y = disjoint_stiefel(dim, avoid=k)
    _require(
        stiefel_defect(dim, y) == (0, 0) and y[k] == 0 and y[dim // 2 + k] == 0, "an avoiding element is not Stiefel"
    )
    return nullity(dim, y)


def avoid_table(n: int, coordinates: Sequence[int] | None = None) -> dict[str, Any]:
    dim = 1 << n
    half = dim // 2
    chosen = list(range(1, half)) if coordinates is None else list(coordinates)
    values = parallel.ordered_map(avoid_nullity, [(dim, k) for k in chosen], min_items=8)
    return {
        "dimension": dim,
        "special_coordinate": half // 2,
        "nullity_by_coordinate": {str(k): v for k, v in zip(chosen, values, strict=True)},
    }


def point_records() -> list[dict[str, Any]]:
    dim = 64
    cases = [
        ("six-term Stiefel", six_term(dim)),
        ("disjoint-support Stiefel", disjoint_stiefel(dim)),
        ("disjoint-support Stiefel avoiding z_16", disjoint_stiefel(dim, avoid=16)),
        ("pair e_1 + i e_2", element(dim, {1: 1}, {2: 1})),
        ("non-Stiefel e_1 + e_2 + i e_3", element(dim, {1: 1, 2: 1}, {3: 1})),
    ]
    return [
        {"point": label, "stiefel_defect": list(stiefel_defect(dim, y))} | degree_identity(dim, y) for label, y in cases
    ]


def admit_witness(w: dict[str, Any], zero_divisor: bool) -> None:
    where = f"{w['label']} at {w['dimension']}"
    _require(w["stiefel_defect"] == [0, 0], f"{where} is not a Stiefel element")
    _require(w["rank"] + w["nullity"] == w["dimension"], f"{where}: rank and nullity disagree")
    _require((w["nullity"] > 0) == zero_divisor, f"{where} is {'not ' if zero_divisor else ''}a zero divisor")


def admit_pairs(record: dict[str, Any]) -> None:
    _require(sum(record["nullity_counts"].values()) == record["pairs"], "the pair counts do not add up")
    _require("0" not in record["nullity_counts"], "an e_i + i e_j has nullity 0")
    _require(
        sum(record["off_hyperplane_nullity_counts"].values()) == record["off_hyperplane_pairs"],
        "the off-hyperplane pair counts do not add up",
    )
    _require(
        all(int(k) % 8 == 4 and 4 <= int(k) <= record["dimension"] // 2 - 4 for k in record["nullity_counts"]),
        "a pair nullity is not 4 mod 8 within 4 .. h - 4",
    )


def admit_valuation(record: dict[str, Any], label: str) -> None:
    """Q does not divide f, and f lies in (Q, z_(h/2)^2) but not in (Q, z_(h/2)^3), on the slice."""
    _require(not record["q_divides_f"], f"Q divides f on the {label}-coordinate slice")
    _require(record["min_special_exponent"] == 2, f"f is not exactly order 2 in z_(h/2) modulo Q on the {label} slice")


def admit_avoid(record: dict[str, Any]) -> None:
    special = str(record["special_coordinate"])
    for k, value in record["nullity_by_coordinate"].items():
        _require(value == (4 if k == special else 0), f"avoid table off at coordinate {k}")


def measure() -> dict[str, Any]:
    cross = {f"A_{n}": cross_identities(n) for n in GATE_COFACTOR}
    _require(
        all(r["cross_matrix_skew"] and r["cross_matrix_annihilates_z"] for r in cross.values()), "C_z identity fails"
    )
    ranks = {f"A_{n}": cofactor_rank(n) for n in GATE_COFACTOR}
    _require(all(r["point_rank_cross"] == r["full_rank"] for r in ranks.values()), "C_z lacks the full rank h - 2")
    moved = {f"A_{n}": transport(n) for n in GATE_TRANSPORT}
    _require(
        all(r["agreeing"] == r["imaginary_basis_elements"] for r in moved.values()), "the transport identity fails"
    )
    cross_checks = {f"A_{n}": left_matrix_cross_check(1 << n) for n in (6, 7, 8)}
    small = cofactor_polynomials_small()
    _require(small["f4_equals_q"] and small["f5_equals_q_g"], "f_4 = Q or f_5 = Q G fails")
    _require(
        small["g_factor_term_counts"] == [[141, 1]] and small["q_factor_term_counts"] == [[15, 1]],
        "G or Q is reducible",
    )
    points = point_records()
    squares = f_squared_crosschecks()
    _require(all(squares["a5_q_g_squared"]) and squares["a6_slice_polynomial_squared"], "the f^2 route disagrees")
    higher = {f"A_{n}": degree_identity(1 << n, disjoint_stiefel(1 << n)) for n in (7, 8)}
    _require(all(all(r["identity_holds"]) and not r["det_L_zero"] for r in higher.values()), "det L = N^4 |f|^4 fails")
    _require(all(all(p["identity_holds"]) for p in points), "det L = N^4 |f|^4 fails at a point")
    three = {f"A_{n}": slice_record(n, SLICE_THREE) for n in (4, 5, 6, 7, 8)}
    for n, record in zip((4, 5, 6, 7, 8), three.values(), strict=True):
        _require(record["f_is_q_power"], f"f is not a power of Q on three coordinates at n = {n}")
    six = slice_record(6, SLICE_SIX)
    closed = six_slice_closed_form()
    _require(
        not six["q_divides_f"]
        and closed["remainder_is_closed_form"]
        and closed["closed_form_equals_minus_x2_x5_form_mod_q"],
        "the six-coordinate remainder is not the closed form",
    )
    _require(closed["f_irreducible"], "f is reducible on the six-coordinate slice")
    seven = slice_record(6, SLICE_SEVEN)
    for label, record in (("six", six), ("seven", seven)):
        admit_valuation(record, label)
    no_sixteen = slice_record(6, SLICE_NO_SIXTEEN)
    _require(no_sixteen["q_divides_f"], "Q does not divide f on a slice without z_16")
    lines = known_lines()
    _require(all(r["irreducible"] for r in lines.values()), "a recorded line is not irreducible")
    witnesses = [
        witness_record(64, "five-term", five_term(64)),
        witness_record(64, "six-term", six_term(64)),
        witness_record(64, "disjoint support", disjoint_stiefel(64)),
        witness_record(128, "disjoint support", disjoint_stiefel(128)),
        witness_record(256, "disjoint support", disjoint_stiefel(256)),
        witness_record(128, "five-term indices", five_term(128)),
        witness_record(256, "five-term indices", five_term(256)),
        witness_record(128, "six-term indices", six_term(128)),
        witness_record(256, "six-term indices", six_term(256)),
        witness_record(64, "Moreno 4.3 e1 + e2, e3 + e4", element(64, {1: 1, 2: 1}, {3: 1, 4: 1})),
        witness_record(64, "Moreno 4.3 e1 + e2, e17 + e18", element(64, {1: 1, 2: 1}, {17: 1, 18: 1})),
    ]
    for w in witnesses:
        admit_witness(w, zero_divisor=w["label"].endswith("indices") or w["label"].startswith("Moreno"))
    pairs = {f"A_{n}": pair_table(n) for n in (5, 6, 7)}
    for record in pairs.values():
        admit_pairs(record)
    avoid = {
        "A_6": avoid_table(6),
        "A_7": avoid_table(7),
        "A_8": avoid_table(8, (1, 2, 64, 127)),
    }
    for record in avoid.values():
        admit_avoid(record)
    return {
        "schema": SCHEMA,
        "versions": {"python-flint": importlib.metadata.version("python-flint"), "numpy": np.__version__},
        "left_matrix_cross_checks": cross_checks,
        "cross_matrix": cross,
        "cross_matrix_rank": ranks,
        "transport": moved,
        "small_cofactors": small,
        "degree_identity_points": points,
        "degree_identity_higher": higher,
        "three_coordinate_slices": three,
        "six_coordinate_slice": six,
        "six_coordinate_closed_form": closed,
        "seven_coordinate_slice": seven,
        "f_squared_crosschecks": squares,
        "slice_without_z16": no_sixteen,
        "irreducible_lines": lines,
        "stiefel_witnesses": witnesses,
        "pair_nullities": pairs,
        "avoid_nullities": avoid,
    }


# ---- exploration (not part of the gate) ----------------------------------------------------------------------------


def exhaustive_slice(item: tuple[int, ...]) -> tuple[tuple[int, ...], bool]:
    f, q = slice_polynomial(6, item)
    return item, reduce_mod_q(f, q) == 0


def exploration() -> dict[str, Any]:
    """Divisibility Q | f_S over small coordinate subsets of A_6, plus A_8 transport, pair and avoid tables."""
    out: dict[str, Any] = {}
    for size in (3, 4):
        subsets = list(itertools.combinations(range(1, 32), size))
        results = parallel.ordered_map(exhaustive_slice, subsets, min_items=64)
        out[f"a6_subsets_size_{size}"] = {"count": len(subsets), "q_divides_f": sum(ok for _, ok in results)}
    subsets5 = [s for s in itertools.combinations(range(1, 17), 5) if 16 in s]
    results5 = parallel.ordered_map(exhaustive_slice, subsets5, min_items=64)
    exceptions = [list(s) for s, ok in results5 if not ok]
    out["a6_subsets_size_5_in_1_to_16_containing_16"] = {
        "count": len(subsets5),
        "q_divides_f": len(subsets5) - len(exceptions),
        "exceptions": exceptions,
    }
    out["special_root_multiplicity"] = [special_root_multiplicity(n, o) for n in (6, 7) for o in range(3)]
    eight = slice_record(6, SLICE_EIGHT)
    admit_valuation(eight, "eight")
    out["eight_coordinate_slice"] = {k: v for k, v in eight.items() if k != "remainder"}
    out["transport_A_8"] = transport(8)
    out["pairs_A_8"] = pair_table(8)
    out["avoid_A_8"] = avoid_table(8)
    out["irreducible_line_search_A_7"] = irreducible_line(7)
    out["pairs_A_7"] = pair_table(7)
    out["irreducible_line_search_A_8"] = irreducible_line(8)
    return out


# ---- checks, mutation controls and entry point ---------------------------------------------------------------------

_MISSING = object()


def differences(retained: Any, fresh: Any, path: str = "") -> list[str]:
    """Paths where the records differ."""
    if isinstance(retained, dict) and isinstance(fresh, dict):
        return [
            item
            for key in sorted(set(retained) | set(fresh))
            for item in differences(retained.get(key, _MISSING), fresh.get(key, _MISSING), f"{path}/{key}")
        ]
    if isinstance(retained, list) and isinstance(fresh, list) and len(retained) == len(fresh):
        return [
            item
            for index, pair in enumerate(zip(retained, fresh, strict=True))
            for item in differences(*pair, f"{path}[{index}]")
        ]
    return [] if type(retained) is type(fresh) and retained == fresh else [path or "/"]


def _refused(check: Callable[..., None], *arguments: Any) -> bool:
    try:
        check(*arguments)
    except SystemExit:
        return True
    return False


def self_test() -> str:
    flipped = cross_identities(6, flip=(3, 12))
    _require(
        not (flipped["cross_matrix_skew"] and flipped["cross_matrix_annihilates_z"]),
        "a flipped structure constant keeps C_z skew with C_z z = 0",
    )
    _require(transport(6, conjugate_s=False)["agreeing"] < 62, "transport without conj(s) still agrees")
    y = disjoint_stiefel(64)
    perturbed = list(y)
    perturbed[1] += 1
    _require(stiefel_defect(64, perturbed) != (0, 0), "a perturbed element is Stiefel")
    half = 32
    point = degree_identity(64, y)
    p, q = list(y[1:half]), list(y[half + 1 :])
    det = int(flint.fmpz_mat(left_matrix(64, y).tolist()).det())
    j = point["coordinates"][0]
    cofactor = int(flint.fmpz_mat(cross_real_form(half, p, q, drop=j).tolist()).det())
    modulus = p[j - 1] ** 2 + q[j - 1] ** 2
    _require(
        det != 0 and det * modulus**2 == point["norm"] ** 4 * cofactor, "the determinant identity fails on the control"
    )
    _require(
        det * modulus**2 != point["norm"] ** 2 * cofactor, "N^2 in place of N^4 satisfies the determinant identity"
    )
    f, q_poly = slice_polynomial(6, SLICE_SIX)
    _require(reduce_mod_q(f + q_poly, q_poly) == reduce_mod_q(f, q_poly), "adding Q changes the normal form of f")
    _require(reduce_mod_q(f + 1, q_poly) != reduce_mod_q(f, q_poly), "a corrupted f keeps its normal form")
    witness = witness_record(64, "disjoint support", y)
    admit_witness(witness, zero_divisor=False)
    corrupted_rank = dict(witness, rank=63)
    _require(_refused(admit_witness, corrupted_rank, False), "a corrupted rank is admitted")
    _require(_refused(admit_witness, witness, True), "a full-rank element is admitted as a zero divisor")
    unstiefel = witness_record(64, "unbalanced", perturbed)
    _require(_refused(admit_witness, unstiefel, False), "a non-Stiefel element is admitted")
    pairs = {"pairs": 4, "nullity_counts": {"4": 3, "0": 1}}
    _require(_refused(admit_pairs, pairs), "a pair table with a nullity-0 entry is admitted")
    avoid = avoid_table(6, (16, 17))
    admit_avoid(avoid)
    swapped = {"special_coordinate": 17, "nullity_by_coordinate": avoid["nullity_by_coordinate"]}
    _require(_refused(admit_avoid, swapped), "an avoid table with the wrong special coordinate is admitted")
    _require(not line_is_irreducible(6, 0), "line 0 is irreducible, so the search order is not as recorded")
    slice_seven = slice_record(6, SLICE_SEVEN)
    admit_valuation(slice_seven, "seven")
    _require(_refused(admit_valuation, dict(slice_seven, min_special_exponent=3), "seven"), "order 3 is admitted")
    _require(_refused(admit_valuation, dict(slice_seven, q_divides_f=True), "seven"), "Q | f is admitted")
    return "3 identity mutations, the N^2 control, 8 corrupted records and the avoid-k swap rejected"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--explore", type=Path)
    arguments = parser.parse_args()
    if arguments.self_test:
        print(f"stiefel_pfaffian_higher self-test: {self_test()}")
        return 0
    if arguments.explore is not None:
        arguments.explore.parent.mkdir(parents=True, exist_ok=True)
        data = exploration()
        arguments.explore.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
        print(json.dumps(data, sort_keys=True))
        return 0
    data = measure()
    if arguments.check is not None:
        retained = json.loads(arguments.check.read_text())
        differing = differences(
            {k: v for k, v in retained.items() if k != "versions"}, {k: v for k, v in data.items() if k != "versions"}
        )
        if differing:
            raise SystemExit(f"stiefel_pfaffian_higher: {differing} differ from {arguments.check}")
    else:
        arguments.out.parent.mkdir(parents=True, exist_ok=True)
        arguments.out.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
    for w in data["stiefel_witnesses"]:
        print(
            f"witness {w['label']:18s} dim {w['dimension']:3d} nonzero {w['nonzero_coordinates']:3d} "
            f"nullity {w['nullity']}"
        )
    print(
        f"six-slice remainder terms {data['six_coordinate_slice']['remainder_terms']}, "
        f"lines {data['irreducible_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
