"""Rank strata of the A_5 zero-divisor set: components, dimensions, closure incidences, connected components.

A_5 is the cd_core doubling of two copies of A_4 (16 coordinates each). A doubly pure y = (p, q) has y_0 = y_16 = 0;
z = p + i q in C^15, C_z is the 15 x 15 Im-block of left multiplication by z on Im (A_4)_C, and Q = z.z, G = Q^2 - 4
(U V - W^2) with u = z_1..z_7, mu = z_8, v = z_9..z_15, U = u.u, V = v.v, W = u.v. The record proves, from exact integer
and polynomial computations over Z:
- Zero divisors are doubly pure: L_y^T L_y = (y_0^2 + y_16^2) I + L_d^T L_d for d = y - y_0 - y_16 e_16.
- For doubly pure y != 0: nullity L_y = 28 - 2 rank C_z, so nullity 4, 8, 12, 16 is rank C_z = 12, 10, 8, 6.
- The scaling e'_k = i^popcount(k) e_k gives a Q-form of (A_4)_C with rational structure constants and a skew matrix
  eta C' congruent to C_z by a diagonal matrix. In these split coordinates every cofactor is P_j = Q G z_j, and C_z
  satisfies C (C^2 + Q)(C^4 + 2 Q C^2 + G) = 0 with characteristic polynomial l (l^2 + Q)^3 (l^4 + 2 Q l^2 + G)^2.
- G_2(C), the 14 derivations, is transitive on each quadric eta(e, e) = kappa != 0 (a Gram-matrix certificate),
  stabilizes e'_1 as sl_3 on the eigenspaces V_+ and V_-, is transitive on null vectors, and is transitive on the
  non-special isotropic planes through a null vector (a minor Groebner certificate). Every pair (u, v) of C^7 therefore
  lies in a G_2-translate of one of six slice families with at most five parameters.
- On each slice and each rank level the Pfaffian ideal has the exact variety recorded in LEVEL_PIECES (Groebner
  membership and radical-power certificates). With representatives, tangent dimensions and orbit dimensions this gives
    R_16 = N_+ u N_-,  R_12 = V u B9,  R_8 = W8 u E8-bar,  R_4 = V(Q) u V(G),
  where R_k = {rank L_y <= 32 - k}, the pieces have complex dimensions 6, 8 and 9, 12 and 11, 14 and 14, and the unit
  sections D_(5,k) of the strata have 1, 2, 1, 2 connected components for k = 4, 8, 12, 16.

Falsifiers: a basis pair on which eta C' is not skew or not congruent to C_z; a cofactor off Q G z_j; a point whose
nullity differs from 28 - 2 rank C_z; a slice whose Pfaffian ideal escapes the recorded pieces (an uncovered
generator or a product outside the radical); a representative of the wrong rank, tangent dimension or orbit dimension;
a quadric, sl_3 or minor certificate that fails; a nullity-4 point of V(Q) and V(G) that lies in R_8.

Usage:
    "$PYTHON" scripts/a5_zero_divisor_strata.py --out docs/evidence/a5-zero-divisor-strata/result.json
    "$PYTHON" scripts/a5_zero_divisor_strata.py --check docs/evidence/a5-zero-divisor-strata/result.json
    "$PYTHON" scripts/a5_zero_divisor_strata.py --self-test
    "$PYTHON" scripts/a5_zero_divisor_strata.py --explore docs/evidence/a5-zero-divisor-strata/explore.json
"""

from __future__ import annotations

import argparse
import copy
import importlib.metadata
import itertools
import json
import math
import sys
from collections.abc import Callable, Sequence
from fractions import Fraction
from math import gcd
from pathlib import Path
from typing import Any

import flint
import sympy

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "a5-zero-divisor-strata-v1"
DIM = 32
HALF = 16
IMAG = 15
SEVEN = 7
MU = 7
LEVELS = (12, 10, 8)
SLICE_NAMES = ("P2", "P3a", "P3b", "P3c", "P4s", "P4g")
PARAMS = ("a", "b", "c", "d", "m")

# Split structure constants: e'_k = i^popcount(k) e_k turns the cd_core table into a +-1 table over Q.
EPS = [(-1) ** k.bit_count() for k in range(HALF)]
ETA = EPS[:8]  # the invariant form on e'_1 .. e'_7: diag(-, -, +, -, +, +, -)
SPLIT = [[(-1) ** (p & q).bit_count() * cd_sign(HALF, p, q) for q in range(HALF)] for p in range(HALF)]
CD16 = [[cd_sign(HALF, p, q) for q in range(HALF)] for p in range(HALF)]

# Slice families: ordered basis (A, B) of a plane of the module C^7 as {index 1..7: coefficient};
# the slice point is u' = a A + b B, mu' = m, v' = c A + d B.
SLICES: dict[str, tuple[dict[int, int], dict[int, int]]] = {
    "P2": ({1: 1}, {2: 1}),  # non-degenerate plane
    "P3a": ({2: 1, 3: 1}, {1: 1}),  # Gram rank 1, radical vector in V_+ of e'_1
    "P3b": ({2: 1, 3: -1}, {1: 1}),  # Gram rank 1, radical vector in V_-
    "P3c": ({2: 1, 3: 1, 4: 1, 5: -1}, {1: 1}),  # Gram rank 1, radical vector in neither eigenspace
    "P4s": ({1: 1, 3: 1}, {4: 1, 6: 1}),  # totally isotropic, special (n x k = 0)
    "P4g": ({1: 1, 3: 1}, {2: 1, 5: 1}),  # totally isotropic, generic
}
# Named pieces whose union is the exact variety of the order-`level` Pfaffian ideal on each slice.
LEVEL_PIECES: dict[int, dict[str, tuple[str, ...]]] = {
    12: {"P2": ("W8", "V"), "P3a": ("E8",), "P3b": ("E8",), "P3c": ("V",), "P4s": ("W8",), "P4g": ("W8",)},
    10: {"P2": ("V",), "P3a": ("V",), "P3b": ("V",), "P3c": ("V",), "P4s": ("B9",), "P4g": ("V",)},
    8: {name: ("Np", "Nm") for name in SLICE_NAMES},
}
PIECE_ORDER = ("W8", "E8", "V", "B9", "Np", "Nm")
PREFIXES = (4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096)
RADICAL_POWER_LIMIT = 8
# Complex dimensions of the pieces (cones in C^15); W8 = N x N, N_+ and N_- = the null cone, V(Q), V(G) hypersurfaces.
PIECE_DIMENSIONS = {"W8": 12, "E8": 11, "V": 8, "B9": 9, "N": 6, "VQ": 14, "VG": 14}
W8_HYPERBOLIC = "W8 hyperbolic plane (e1; e3)"


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"a5_zero_divisor_strata: {message}")


# ---------------------------------------------------------------------------------------------------------------------
# Matrices and Pfaffians


def chat(z: Sequence[Any], zero: Any, table: list[list[int]] | None = None) -> list[list[Any]]:
    """eta C': entry (a, b) is eps_a split(k, b) z_k at k = a XOR b, for imaginary indices a != b."""
    signs = SPLIT if table is None else table
    return [
        [z[(a ^ b) - 1] * (EPS[a] * signs[a ^ b][b]) if a != b else zero for b in range(1, HALF)]
        for a in range(1, HALF)
    ]


def cprime(z: Sequence[Any], zero: Any) -> list[list[Any]]:
    """C', the matrix of z on Im in the split basis: entry (a, b) is split(k, b) z_k at k = a XOR b."""
    return [[z[(a ^ b) - 1] * SPLIT[a ^ b][b] if a != b else zero for b in range(1, HALF)] for a in range(1, HALF)]


def pfaffian_memo(matrix: list[list[Any]], zero: Any, one: Any) -> Callable[[int], Any]:
    """Pf of the principal submatrix on a bit mask of indices, by expansion along its first index, memoized."""
    memo: dict[int, Any] = {0: one}

    def pf(mask: int) -> Any:
        if mask in memo:
            return memo[mask]
        indices = [i for i in range(len(matrix)) if mask >> i & 1]
        value = zero
        if len(indices) % 2 == 0:
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


def ideal_generators(matrix: list[list[Any]], zero: Any, one: Any, order: int) -> list[Any]:
    """The nonzero principal Pfaffians of the given order, deduplicated, smallest first."""
    pf = pfaffian_memo(matrix, zero, one)
    found: dict[str, Any] = {}
    for subset in itertools.combinations(range(IMAG), order):
        value = pf(sum(1 << i for i in subset))
        if value != zero:
            found[str(value)] = value
    return sorted(found.values(), key=lambda p: (len(p), p.total_degree()))


def rank_int(rows: Sequence[Sequence[int]]) -> int:
    if not rows:
        return 0
    return int(flint.fmpz_mat(len(rows), len(rows[0]), [x for row in rows for x in row]).rank())


def rank_q(rows: Sequence[Sequence[Any]]) -> int:
    if not rows:
        return 0
    return int(flint.fmpq_mat(len(rows), len(rows[0]), [flint.fmpq(x) for row in rows for x in row]).rank())


def matmul(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    return [[sum(a[r][k] * b[k][c] for k in range(len(b))) for c in range(len(b[0]))] for r in range(len(a))]


# ---------------------------------------------------------------------------------------------------------------------
# Doubly pure zero divisors


def left_matrix_32(y: Sequence[int]) -> list[list[int]]:
    return [[y[r ^ c] * cd_sign(DIM, r ^ c, c) for c in range(DIM)] for r in range(DIM)]


def doubly_pure(flip: tuple[int, int] | None = None) -> dict[str, Any]:
    """J = L_(e_16) squares to -I, every L_(e_k) is skew, and J anticommutes with L_(e_k) for k not in {0, 16}.

    With y = y_0 + y_16 e_16 + d and d orthogonal to span(e_0, e_16), L_y = y_0 I + y_16 J + L_d, so these identities
    give L_y^T L_y = (y_0^2 + y_16^2) I + L_d^T L_d, which is positive definite when (y_0, y_16) != 0.
    flip = (r, c) negates one entry of J, a mutation that must break the identities.
    """
    unit = [[1 if r == c else 0 for c in range(DIM)] for r in range(DIM)]
    basis = {k: left_matrix_32([1 if j == k else 0 for j in range(DIM)]) for k in range(1, DIM)}
    j_matrix = copy.deepcopy(basis[HALF])
    if flip is not None:
        j_matrix[flip[0]][flip[1]] = -j_matrix[flip[0]][flip[1]]
    square = matmul(j_matrix, j_matrix)
    skew = all(basis[k][r][c] == -basis[k][c][r] for k in basis for r in range(DIM) for c in range(DIM))
    anticommute = []
    for k in basis:
        if k == HALF:
            continue
        left = matmul(j_matrix, basis[k])
        right = matmul(basis[k], j_matrix)
        anticommute.append(all(left[r][c] + right[r][c] == 0 for r in range(DIM) for c in range(DIM)))
    return {
        "j_squares_to_minus_identity": all(square[r][c] == -unit[r][c] for r in range(DIM) for c in range(DIM)),
        "imaginary_left_matrices_skew": skew,
        "anticommuting_basis_elements": sum(anticommute),
        "basis_elements_outside_C5": len(anticommute),
    }


# ---------------------------------------------------------------------------------------------------------------------
# Split coordinates


def split_algebra(table: list[list[int]] | None = None) -> dict[str, Any]:
    """eta C' is skew, and eta C' = D C D with D = diag(i^popcount) on every basis vector of z."""
    signs = SPLIT if table is None else table
    skew = True
    congruent = True
    for k in range(1, HALF):
        for a in range(1, HALF):
            for b in range(1, HALF):
                if a == b or (a ^ b) != k:
                    continue
                forward = EPS[a] * signs[k][b]
                backward = EPS[b] * signs[k][a]
                skew = skew and forward == -backward
                exponent = a.bit_count() + b.bit_count() + k.bit_count()
                congruent = congruent and exponent % 2 == 0 and forward == (-1) ** (exponent // 2) * CD16[k][b]
    return {"skew_on_basis": skew, "congruent_to_cross_matrix": congruent}


def split_forms(z: Sequence[Any], zero: Any) -> dict[str, Any]:
    """eta(u'), eta(v'), eta(u', v'), Q = eta(u') - mu'^2 - eta(v'), Delta = U V - W^2 and G = Q^2 - 4 Delta."""
    u, mu, v = z[:SEVEN], z[MU], z[SEVEN + 1 :]
    eta_u = sum((ETA[k + 1] * u[k] * u[k] for k in range(SEVEN)), zero)
    eta_v = sum((ETA[k + 1] * v[k] * v[k] for k in range(SEVEN)), zero)
    eta_uv = sum((ETA[k + 1] * u[k] * v[k] for k in range(SEVEN)), zero)
    q = eta_u - mu * mu - eta_v
    delta = eta_uv * eta_uv - eta_u * eta_v
    return {"eta_u": eta_u, "eta_v": eta_v, "eta_uv": eta_uv, "q": q, "delta": delta, "g": q * q - 4 * delta}


def split_factorization() -> dict[str, Any]:
    """P_j = (-1)^j Pf(eta C' without j) equals Q G z_j over Z[z'] with Q = z.z and G = Q^2 - 4 (U V - W^2)."""
    names = [f"z{k}" for k in range(1, HALF)]
    ring = flint.fmpz_mpoly_ctx.get(names, "lex")
    z = list(ring.gens())
    zero, one = ring.from_dict({}), ring.from_dict({(0,) * IMAG: 1})
    c = chat(z, zero)
    pf = pfaffian_memo(c, zero, one)
    full = (1 << IMAG) - 1
    cofactors = [pf(full & ~(1 << j)) * (1 if j % 2 == 0 else -1) for j in range(IMAG)]
    forms = split_forms(z, zero)
    q, g = forms["q"], forms["g"]
    original_q = sum((EPS[k] * z[k - 1] * z[k - 1] for k in range(1, HALF)), zero)
    return {
        "skew": all(c[i][j] + c[j][i] == 0 for i in range(IMAG) for j in range(IMAG)),
        "cofactors_equal_q_g_z": [p == q * g * z[j] for j, p in enumerate(cofactors)],
        "cofactor_terms": len(cofactors[0]),
        "q_is_sum_eps_z_squared": q == original_q,
        "q_terms": len(q),
        "g_terms": len(g),
    }


def y_from_split(z: Sequence[int]) -> list[int]:
    """z_k = i^popcount(k) z'_k and y = (Re z, Im z) on e_1..e_15 and e_17..e_31."""
    y = [0] * DIM
    for k in range(1, HALF):
        power = k.bit_count() % 4
        y[k] = z[k - 1] * (1, 0, -1, 0)[power]
        y[HALF + k] = z[k - 1] * (0, 1, 0, -1)[power]
    return y


def nullity_32(y: Sequence[int]) -> int:
    return DIM - rank_int(left_matrix_32(y))


def cross_rank(z: Sequence[int]) -> int:
    return rank_int(chat(z, 0))


def nullity_identity(item: tuple[str, list[int], int]) -> dict[str, Any]:
    """nullity L_y = offset - 2 rank C_z at one integer split point (offset 28 is the theorem)."""
    name, z, offset = item
    rank = cross_rank(z)
    nullity = nullity_32(y_from_split(z))
    return {"point": name, "rank_C": rank, "nullity": nullity, "agrees": nullity == offset - 2 * rank}


# ---------------------------------------------------------------------------------------------------------------------
# Derivations, equivariance, characteristic polynomial


def split_derivations() -> list[list[list[int]]]:
    """An integer basis of the derivations of the split sedenion table; D[r][c] is the e'_r coefficient of D e'_c."""
    rows = []
    for i in range(HALF):
        for j in range(HALF):
            for m in range(HALF):
                row = [0] * (HALF * HALF)
                row[m * HALF + (i ^ j)] += SPLIT[i][j]
                row[(m ^ j) * HALF + i] -= SPLIT[m ^ j][j]
                row[(i ^ m) * HALF + j] -= SPLIT[i][i ^ m]
                rows.append(row)
    basis, count = flint.fmpz_mat(rows).nullspace()
    return [[[int(basis[r * HALF + c, k]) for c in range(HALF)] for r in range(HALF)] for k in range(count)]


def act(derivation: list[list[int]], z: Sequence[Any]) -> list[Any]:
    return [sum(derivation[r][c] * z[c - 1] for c in range(1, HALF)) for r in range(1, HALF)]


def block7(derivation: list[list[int]]) -> list[list[int]]:
    return [[derivation[r][c] for c in range(1, 8)] for r in range(1, 8)]


def derivation_data(derivations: list[list[list[int]]]) -> dict[str, Any]:
    """14 derivations, block diagonal on (u', mu', v'), killing e_0 and e_8, the same 7 x 7 block on u' and v'."""
    blocks_diagonal = all(
        derivation[r][c] == 0
        for derivation in derivations
        for r in range(HALF)
        for c in range(HALF)
        if (r < 8) != (c < 8) or r in (0, 8) or c in (0, 8)
    )
    same_block = all(
        derivation[r][c] == derivation[r + 8][c + 8]
        for derivation in derivations
        for r in range(1, 8)
        for c in range(1, 8)
    )
    form_invariant = all(
        ETA[r] * derivation[r][c] + ETA[c] * derivation[c][r] == 0
        for derivation in derivations
        for r in range(1, 8)
        for c in range(1, 8)
    )
    return {
        "count": len(derivations),
        "block_diagonal_fixing_e0_e8": blocks_diagonal,
        "same_block_on_u_and_v": same_block,
        "eta_invariant": form_invariant,
    }


def equivariance(derivations: list[list[list[int]]]) -> bool:
    """[D, C'_z] = C'_(D z) for every derivation D (linear in z, so the 15 basis vectors decide it)."""
    for derivation in derivations:
        d_block = [[derivation[r][c] for c in range(1, HALF)] for r in range(1, HALF)]
        for k in range(1, HALF):
            z = [1 if j == k else 0 for j in range(1, HALF)]
            c_z = cprime(z, 0)
            c_dz = cprime(act(derivation, z), 0)
            left = matmul(d_block, c_z)
            right = matmul(c_z, d_block)
            if any(left[r][c] - right[r][c] != c_dz[r][c] for r in range(IMAG) for c in range(IMAG)):
                return False
    return True


def characteristic_identities() -> dict[str, Any]:
    """On the slice z' = (x e_1, m, a e_1 + s e_2) the minimal and characteristic polynomials are as stated."""
    x, a, s, m, lam = sympy.symbols("x a s m lam")
    z: list[Any] = [0] * IMAG
    z[0], z[MU], z[8], z[9] = x, m, a, s
    matrix = sympy.Matrix(IMAG, IMAG, lambda i, j: cprime(z, 0)[i][j])
    q = -(x**2) - m**2 + a**2 + s**2
    delta = -(x**2) * s**2
    g = q * q - 4 * delta
    identity = sympy.eye(IMAG)
    square = matrix * matrix
    relation = matrix * (square + q * identity) * (square * square + 2 * q * square + g * identity)
    char = matrix.charpoly(lam).as_expr()
    target = lam * (lam**2 + q) ** 3 * (lam**4 + 2 * q * lam**2 + g) ** 2
    return {
        "minimal_polynomial_relation_on_slice": bool(relation.applyfunc(sympy.expand) == sympy.zeros(IMAG, IMAG)),
        "characteristic_polynomial_on_slice": bool(sympy.expand(char - target) == 0),
    }


def slice_dominance(derivations: list[list[list[int]]]) -> int:
    """Rank of the differential of (g, x, a, s, m) -> g z' at a rational slice point: 15 means G_2 x slice is dense."""
    z = [0] * IMAG
    z[0], z[MU], z[8], z[9] = 2, 3, 5, 7
    rows = [act(derivation, z) for derivation in derivations]
    for index in (0, MU, 8, 9):
        rows.append([1 if j == index else 0 for j in range(IMAG)])
    return rank_q(rows)


# ---------------------------------------------------------------------------------------------------------------------
# Orbit facts for G_2(C) on the module C^7


def vec7(entries: dict[int, int]) -> list[int]:
    return [entries.get(k, 0) for k in range(1, 8)]


def apply7(matrix: list[list[int]], x: Sequence[Any]) -> list[Any]:
    return [sum(matrix[r][c] * x[c] for c in range(7)) for r in range(7)]


def eta7(x: Sequence[Any], y: Sequence[Any]) -> Any:
    return sum(ETA[k + 1] * x[k] * y[k] for k in range(7))


def cross7(x: Sequence[Any], y: Sequence[Any]) -> list[Any]:
    """Imaginary part of the split octonion product of two pure elements, coordinates e'_1 .. e'_7."""
    out = [0] * 8
    for a in range(1, 8):
        for b in range(1, 8):
            if a != b and x[a - 1] != 0 and y[b - 1] != 0:
                out[a ^ b] += SPLIT[a][b] * x[a - 1] * y[b - 1]
    return out[1:]


def quadric_certificate(blocks: list[list[list[int]]], form: Sequence[int]) -> dict[str, Any]:
    """M(e) W M(e)^T = eta(e) eta^-1 + beta e e^T with M(e) = [D_1 e ... D_14 e], solved exactly for (W, beta).

    The coefficient equations in the monomials e_c e_d form a linear system in the entries of W and in beta. A unique
    solution with the inhomogeneous term present means the identity holds over Z[e], so rank M(e) >= 6 wherever
    eta(e) != 0, and every G_2-orbit of a quadric eta = kappa != 0 is open.
    """
    count = len(blocks)
    rows = []
    targets = []
    for r in range(7):
        for s in range(r, 7):
            for c in range(7):
                for d in range(c, 7):
                    row = [0] * (count * count + 1)
                    for i in range(count):
                        for j in range(count):
                            coefficient = blocks[i][r][c] * blocks[j][s][d]
                            if c != d:
                                coefficient += blocks[i][r][d] * blocks[j][s][c]
                            row[i * count + j] += coefficient
                    if (c, d) == (r, s):
                        row[count * count] -= 1
                    rows.append(row)
                    targets.append(form[c + 1] * form[r + 1] if r == s and c == d else 0)
    augmented = [row + [-target] for row, target in zip(rows, targets, strict=True)]
    matrix = flint.fmpz_mat(len(augmented), count * count + 2, [x for row in augmented for x in row])
    kernel, nullity = matrix.nullspace()
    solutions = [
        [int(kernel[r, c]) for r in range(count * count + 2)]
        for c in range(nullity)
        if int(kernel[count * count + 1, c]) != 0
    ]
    unique = len(solutions) == 1
    beta = str(Fraction(solutions[0][count * count], solutions[0][count * count + 1])) if unique else None
    return {"unique_solution": unique, "kernel_dimension": nullity, "beta": beta}


def stabilizer_algebra(blocks: list[list[list[int]]], vectors: Sequence[Sequence[int]]) -> list[list[int]]:
    """Coefficient vectors t with (sum t_i D_i) v = 0 for every v."""
    count = len(blocks)
    columns = [[x for v in vectors for x in apply7(block, v)] for block in blocks]
    matrix = flint.fmpz_mat(
        len(columns[0]), count, [columns[j][i] for i in range(len(columns[0])) for j in range(count)]
    )
    kernel, nullity = matrix.nullspace()
    return [[int(kernel[i, c]) for i in range(count)] for c in range(nullity)]


def combine(blocks: list[list[list[int]]], t: Sequence[int]) -> list[list[int]]:
    return [[sum(t[i] * blocks[i][r][c] for i in range(len(blocks))) for c in range(7)] for r in range(7)]


def orbit_dimension(blocks: list[list[list[int]]], vectors: Sequence[Sequence[int]]) -> int:
    return rank_int([[x for v in vectors for x in apply7(block, v)] for block in blocks])


def coordinates_in(basis: Sequence[Sequence[int]], w: Sequence[Any]) -> list[Any] | None:
    """Coordinates of w in the span of an independent basis, or None when w lies outside it."""
    size = len(basis)
    gram = flint.fmpq_mat(
        size,
        size,
        [flint.fmpq(sum(basis[j][i] * basis[k][i] for i in range(7))) for j in range(size) for k in range(size)],
    )
    rhs = flint.fmpq_mat(size, 1, [flint.fmpq(sum(basis[j][i] * w[i] for i in range(7))) for j in range(size)])
    solution = gram.solve(rhs)
    coordinates = [solution[j, 0] for j in range(size)]
    rebuilt = [sum(coordinates[j] * basis[j][i] for j in range(size)) for i in range(7)]
    return coordinates if all(rebuilt[i] == w[i] for i in range(7)) else None


def plane_stabilizer(blocks: list[list[list[int]]], basis: Sequence[Sequence[int]]) -> tuple[int, int]:
    """(dimension of the stabilizer of span(basis), rank of its induced action in gl_2)."""
    count = len(blocks)
    annihilators, nullity = flint.fmpz_mat(len(basis), 7, [x for v in basis for x in v]).nullspace()
    functionals = [[int(annihilators[r, c]) for r in range(7)] for c in range(nullity)]
    constraints = [
        [sum(f[r] * apply7(block, v)[r] for r in range(7)) for block in blocks] for f in functionals for v in basis
    ]
    kernel, dimension = flint.fmpz_mat(len(constraints), count, [x for row in constraints for x in row]).nullspace()
    images = []
    for c in range(dimension):
        d = combine(blocks, [int(kernel[i, c]) for i in range(count)])
        row: list[Any] = []
        for v in basis:
            coordinates = coordinates_in(basis, apply7(d, v))
            row.extend(coordinates if coordinates is not None else [0, 0])
        images.append(row)
    return dimension, rank_q(images) if images else 0


def sl3_data(blocks: list[list[list[int]]]) -> dict[str, Any]:
    """The stabilizer of e'_1 has dimension 8 and acts on the eigenspaces V_+ and V_- of x -> e'_1 x as sl_3."""
    e1 = vec7({1: 1})
    algebra = [combine(blocks, t) for t in stabilizer_algebra(blocks, [e1])]
    left = [[0] * 7 for _ in range(7)]
    for k in range(2, 8):
        column = cross7(e1, vec7({k: 1}))
        for r in range(7):
            left[r][k - 1] = column[r]
    commute = all(
        sum(h[r][k] * left[k][c] - left[r][k] * h[k][c] for k in range(7)) == 0
        for h in algebra
        for r in range(7)
        for c in range(7)
    )
    spaces = {
        "plus": [vec7({2: 1, 3: 1}), vec7({4: 1, 5: 1}), vec7({6: 1, 7: -1})],
        "minus": [vec7({2: 1, 3: -1}), vec7({4: 1, 5: -1}), vec7({6: 1, 7: 1})],
    }
    result: dict[str, Any] = {"stabilizer_dimension": len(algebra), "commutes_with_left_e1": commute}
    for name, basis in spaces.items():
        sign = 1 if name == "plus" else -1
        images = []
        traceless = True
        invariant = True
        for h in algebra:
            matrix = []
            for v in basis:
                coordinates = coordinates_in(basis, apply7(h, v))
                invariant = invariant and coordinates is not None
                matrix.append(coordinates if coordinates is not None else [0, 0, 0])
            traceless = traceless and sum(matrix[j][j] for j in range(3)) == 0
            images.append([x for row in matrix for x in row])
        result[name] = {
            "eigenvectors": all(cross7(e1, v) == [sign * x for x in v] for v in basis),
            "totally_null": all(eta7(v, w) == 0 for v in basis for w in basis),
            "invariant": invariant,
            "traceless": traceless,
            "action_rank": rank_q(images),
        }
    result["pairing_plus_minus_rank"] = rank_int([[eta7(v, w) for w in spaces["minus"]] for v in spaces["plus"]])
    return result


def null_orbits(blocks: list[list[list[int]]]) -> dict[str, int]:
    """Orbit dimensions of the three SL_3-types of null vectors of e'_1^perp and of e'_1 + e'_3."""
    vectors = {
        "n_plus": vec7({2: 1, 3: 1}),
        "n_minus": vec7({2: 1, 3: -1}),
        "n_mixed": vec7({2: 1, 3: 1, 4: 1, 5: -1}),
        "e1_plus_e3": vec7({1: 1, 3: 1}),
    }
    return {name: orbit_dimension(blocks, [v]) for name, v in vectors.items()}


def determinant(matrix: list[list[Any]], zero: Any) -> Any:
    size = len(matrix)
    if size == 1:
        return matrix[0][0]
    total = zero
    for j in range(size):
        if matrix[0][j] == zero:
            continue
        minor = [row[:j] + row[j + 1 :] for row in matrix[1:]]
        term = matrix[0][j] * determinant(minor, zero)
        total = total + term if j % 2 == 0 else total - term
    return total


def isotropic_plane_certificate(blocks: list[list[list[int]]]) -> dict[str, Any]:
    """The stabilizer H of n = e'_1 + e'_3 is transitive on the isotropic planes through n except the special ones.

    A plane <n, x> with x null in n^perp mod n has H-orbit of dimension rank{h x, n, x} - 2, and 3 is the dimension of
    the quadric of such planes. The 5 x 5 minors of [h_1 x, .., h_8 x, n, x] together with eta(x) = 0 have common zeros
    inside L = ker(x -> n x x) (Groebner radical powers of the three linear forms defining L), and H acts on L through
    all of sl_2, hence transitively on P(L).
    """
    n1 = vec7({1: 1, 3: 1})
    algebra = [combine(blocks, t) for t in stabilizer_algebra(blocks, [n1])]
    ring = flint.fmpz_mpoly_ctx.get(["x2", "x4", "x5", "x6", "x7"], "lex")
    gens = list(ring.gens())
    zero = ring.from_dict({})
    x = [zero] * 7
    for gen, position in zip(gens, (1, 3, 4, 5, 6), strict=True):
        x[position] = gen
    columns = [apply7(h, x) for h in algebra]
    columns.append([ring.from_dict({(0,) * 5: n1[i]}) for i in range(7)])
    columns.append(list(x))
    form = sum((ETA[k + 1] * x[k] * x[k] for k in range(7)), zero)
    minors: dict[str, Any] = {}
    for rows in itertools.combinations(range(7), 5):
        for chosen in itertools.combinations(range(len(columns)), 5):
            value = determinant([[columns[c][r] for c in chosen] for r in rows], zero)
            if value != zero:
                minors[str(value)] = value
    ordered = sorted(minors.values(), key=lambda p: (len(p), p.total_degree()))
    tool = GroebnerTool(ring)
    basis = tool.groebner([*ordered[:300], form])
    special = [gens[0], gens[2] - gens[4], gens[1] - gens[3]]
    # n x x as linear forms in x: the special locus L is where all of them vanish.
    cross_forms = [zero] * 7
    for a in range(1, 8):
        for b in range(1, 8):
            if a != b and n1[a - 1] != 0:
                cross_forms[(a ^ b) - 1] = cross_forms[(a ^ b) - 1] + x[b - 1] * (SPLIT[a][b] * n1[a - 1])
    cross_zero_locus = tool.groebner([p for p in cross_forms if p != zero])
    same_locus = all(tool.is_member(p, cross_zero_locus) for p in special)
    powers = [tool.in_radical(linear, basis) for linear in special]
    l_basis = [vec7({4: 1, 6: 1}), vec7({5: 1, 7: 1})]
    traceless_rows: list[list[Any]] = []
    invariant = True
    for h in algebra:
        images = []
        for v in l_basis:
            w = apply7(h, v)
            w = [w[i] - w[0] * n1[i] for i in range(7)]
            coordinates = coordinates_in(l_basis, w)
            invariant = invariant and coordinates is not None
            images.append(coordinates if coordinates is not None else [0, 0])
        m11, m21 = images[0]
        m12, m22 = images[1]
        traceless_rows.append([m11 - m22, m12, m21])
    return {
        "stabilizer_dimension": len(algebra),
        "minors": len(minors),
        "groebner_size": len(basis),
        "special_forms_radical_powers": powers,
        "special_forms_equal_cross_product_locus": same_locus,
        "special_subspace_invariant": invariant,
        "traceless_action_rank_on_special_line": rank_q(traceless_rows),
    }


def plane_table(blocks: list[list[list[int]]]) -> dict[str, Any]:
    """Plane-stabilizer dimension, induced rank in gl_2 and ordered-pair orbit dimension for each slice plane."""
    table = {}
    for name in SLICE_NAMES:
        first, second = SLICES[name]
        basis = [vec7(first), vec7(second)]
        dimension, induced = plane_stabilizer(blocks, basis)
        table[name] = {
            "plane_stabilizer_dimension": dimension,
            "plane_orbit_dimension": 14 - dimension,
            "induced_rank_in_gl2": induced,
            "ordered_pair_orbit_dimension": orbit_dimension(blocks, basis),
        }
    return table


def orbit_facts() -> dict[str, Any]:
    derivations = split_derivations()
    blocks = [block7(d) for d in derivations]
    return {
        "derivations": derivation_data(derivations),
        "equivariance_cprime": equivariance(derivations),
        "slice_dominance_rank": slice_dominance(derivations),
        "quadric_certificate": quadric_certificate(blocks, ETA),
        "sl3": sl3_data(blocks),
        "null_orbit_dimensions": null_orbits(blocks),
        "isotropic_planes": isotropic_plane_certificate(blocks),
        "plane_table": plane_table(blocks),
        "orbit_dimension_e1": orbit_dimension(blocks, [vec7({1: 1})]),
        "orbit_dimension_frame_e1_e2": orbit_dimension(blocks, [vec7({1: 1}), vec7({2: 1})]),
    }


# ---------------------------------------------------------------------------------------------------------------------
# Groebner certificates on the slice families


class GroebnerTool:
    """Exact ideal membership over Q in a fixed lex ring: Buchberger from python-flint and pseudo-division."""

    def __init__(self, ring: Any) -> None:
        self.ring = ring
        self.zero = ring.from_dict({})

    @staticmethod
    def lead(f: Any) -> tuple[tuple[int, ...], int]:
        return f.monoms()[0], int(f.coeffs()[0])

    def groebner(self, generators: Sequence[Any]) -> list[Any]:
        vector = flint.fmpz_mpoly_vec([g for g in generators if g != self.zero], self.ring)
        basis: Any = vector.buchberger_naive()
        _require(bool(basis.is_groebner(vector)), "Buchberger returned a set that is not a Groebner basis of its input")
        return [basis[i] for i in range(len(basis))]

    def is_member(
        self, f: Any, basis: Sequence[Any], leads: list[tuple[tuple[tuple[int, ...], int], Any]] | None = None
    ) -> bool:
        """f in the ideal of a Groebner basis: every leading term must be divisible by a basis leading term."""
        if leads is None:
            leads = [(self.lead(g), g) for g in basis]
        while f != self.zero:
            monomial, coefficient = self.lead(f)
            for (lead_monomial, lead_coefficient), g in leads:
                if all(p <= q for p, q in zip(lead_monomial, monomial, strict=True)):
                    common = abs(coefficient) * abs(lead_coefficient) // gcd(abs(coefficient), abs(lead_coefficient))
                    shift = self.ring.from_dict({tuple(q - p for p, q in zip(lead_monomial, monomial, strict=True)): 1})
                    f = f * (common // coefficient) - shift * g * (common // lead_coefficient)
                    if f != self.zero:
                        content = int(f.content())
                        if content > 1:
                            f = self.ring.from_dict({k: int(v) // content for k, v in f.to_dict().items()})
                    break
            else:
                return False
        return True

    def in_radical(self, h: Any, basis: Sequence[Any], limit: int = RADICAL_POWER_LIMIT) -> int | None:
        """The least exponent e <= limit with h^e in the ideal, or None."""
        leads = [(self.lead(g), g) for g in basis]
        power = h
        for exponent in range(1, limit + 1):
            if self.is_member(power, basis, leads):
                return exponent
            power = power * h
        return None


def slice_ring() -> tuple[Any, list[Any], Any, Any]:
    ring = flint.fmpz_mpoly_ctx.get(list(PARAMS), "lex")
    gens = list(ring.gens())
    return ring, gens, ring.from_dict({}), ring.from_dict({(0,) * len(PARAMS): 1})


def slice_point(name: str, gens: list[Any], zero: Any) -> list[Any]:
    """z' = (a A + b B, m, c A + d B) in the slice ring."""
    a, b, c, d, m = gens
    first, second = SLICES[name]
    z = [zero] * IMAG
    for k, coefficient in first.items():
        z[k - 1] = z[k - 1] + a * coefficient
        z[SEVEN + k] = z[SEVEN + k] + c * coefficient
    for k, coefficient in second.items():
        z[k - 1] = z[k - 1] + b * coefficient
        z[SEVEN + k] = z[SEVEN + k] + d * coefficient
    z[MU] = m
    return z


def slice_pieces(name: str, gens: list[Any], zero: Any) -> dict[str, list[Any]]:
    """Generators of the named pieces restricted to the slice (intrinsic equations in u', v', mu')."""
    a, b, c, d, m = gens
    first, second = SLICES[name]
    av, bv = vec7(first), vec7(second)
    eaa, eab, ebb = eta7(av, av), eta7(av, bv), eta7(bv, bv)
    eta_u = a * a * eaa + 2 * a * b * eab + b * b * ebb
    eta_v = c * c * eaa + 2 * c * d * eab + d * d * ebb
    eta_uv = a * c * eaa + (a * d + b * c) * eab + b * d * ebb
    q = eta_u - m * m - eta_v
    wedge = a * d - b * c
    pieces = {
        "W8": [m, eta_u + eta_v, eta_uv],
        "V": [q, wedge],
        "B9": [m, eta_u, eta_v, eta_uv, *[wedge * int(value) for value in cross7(av, bv) if value != 0]],
        "Np": [m, c - a, d - b, eta_u],
        "Nm": [m, c + a, d + b, eta_u],
        "E8": [q],
    }
    return {key: [p for p in value if p != zero] for key, value in pieces.items()}


def slice_certificate(item: tuple[str, int, bool]) -> dict[str, Any]:
    """Exact variety of the Pfaffian ideal of one order on one slice, and which pieces contain it.

    Containment (i): every principal Pfaffian lies in the ideal of the piece. Covering (ii): every product of one
    generator from each named piece has a power in the ideal of the first `prefix` Pfaffians, so the variety of that
    ideal lies in the union of the pieces. (i) and (ii) together make the union exactly the variety.
    """
    name, order, drop_last = item
    ring, gens, zero, one = slice_ring()
    tool = GroebnerTool(ring)
    generators = ideal_generators(chat(slice_point(name, gens, zero), zero), zero, one, order)
    pieces = slice_pieces(name, gens, zero)
    named = list(LEVEL_PIECES[order][name])
    if drop_last and len(named) > 1:
        named = named[:-1]
    contained: dict[str, bool] = {}
    for piece in PIECE_ORDER:
        if piece == "E8" and name not in ("P3a", "P3b"):
            continue
        basis = tool.groebner(pieces[piece])
        leads = [(tool.lead(g), g) for g in basis]
        contained[piece] = all(tool.is_member(g, basis, leads) for g in generators)
    covering: dict[str, Any] = {"prefix": None, "max_power": None}
    for prefix in (*[n for n in PREFIXES if n < len(generators)], len(generators)):
        basis_i = tool.groebner(generators[:prefix])
        worst = 0
        good = True
        for combination in itertools.product(*[pieces[p] for p in named]):
            product = one
            for factor in combination:
                product = product * factor
            power = tool.in_radical(product, basis_i)
            if power is None:
                good = False
                break
            worst = max(worst, power)
        if good:
            covering = {"prefix": prefix, "max_power": worst}
            break
    forms = split_forms(slice_point(name, gens, zero), zero)
    return {
        "slice": name,
        "order": order,
        "generators": len(generators),
        "named_pieces": named,
        "ideal_inside_piece_ideal": contained,
        "covering": covering,
        "gram_determinant_vanishes": forms["delta"] == zero,
    }


# ---------------------------------------------------------------------------------------------------------------------
# Representatives: ranks, tangent dimensions, orbit dimensions


def pfaffian_table_int(matrix: list[list[int]], maxsize: int) -> dict[int, int]:
    """Pf of every principal submatrix of an integer skew matrix up to the given size, by first-index expansion."""
    table = {0: 1}
    masks = sorted(
        (m for m in range(1 << IMAG) if m.bit_count() % 2 == 0 and m.bit_count() <= maxsize),
        key=lambda m: m.bit_count(),
    )
    for mask in masks:
        if mask == 0:
            continue
        indices = [i for i in range(IMAG) if mask >> i & 1]
        first = indices[0]
        rest = mask & ~(1 << first)
        value = 0
        for position, j in enumerate(indices[1:], start=1):
            entry = matrix[first][j]
            if entry == 0:
                continue
            sub = table[rest & ~(1 << j)]
            if sub == 0:
                continue
            value = value + entry * sub if position % 2 else value - entry * sub
        table[mask] = value
    return table


def masks_of_size(size: int) -> list[int]:
    return [sum(1 << i for i in subset) for subset in itertools.combinations(range(IMAG), size)]


def jacobian_rows(table: dict[int, int], order: int) -> list[list[int]]:
    """Rows d Pf(mask) / d z_k of all principal Pfaffians of one order, from the numeric sub-Pfaffian table.

    For a skew matrix M with entries M_ij = c_ij z_k at k = (i + 1) XOR (j + 1), d Pf / d M_ij is
    (-1)^(p + q + 1) Pf(M without i, j) for the positions p < q of i and j in the index set.
    """
    rows = []
    for mask in masks_of_size(order):
        indices = [i for i in range(IMAG) if mask >> i & 1]
        row = [0] * IMAG
        for p in range(order):
            for q in range(p + 1, order):
                i, j = indices[p], indices[q]
                k = (i + 1) ^ (j + 1)
                sub = table[mask & ~(1 << i) & ~(1 << j)]
                if sub:
                    row[k - 1] += EPS[i + 1] * SPLIT[k][j + 1] * (-1 if (p + q + 1) % 2 else 1) * sub
        rows.append(row)
    return rows


def split_vector(u: dict[int, int] | None = None, mu: int = 0, v: dict[int, int] | None = None) -> list[int]:
    z = [0] * IMAG
    for k, coefficient in (u or {}).items():
        z[k - 1] = coefficient
    z[MU] = mu
    for k, coefficient in (v or {}).items():
        z[SEVEN + k] = coefficient
    return z


def mix(*terms: tuple[int, dict[int, int]]) -> dict[int, int]:
    out: dict[int, int] = {}
    for coefficient, vector in terms:
        for k, value in vector.items():
            out[k] = out.get(k, 0) + coefficient * value
    return {k: v for k, v in out.items() if v}


def point_invariants(z: Sequence[int]) -> dict[str, int]:
    """mu', eta(u'), eta(v'), eta(u', v'), Q, G and the wedge u' ^ v' (as the sum of squares of its components)."""
    forms = split_forms(list(z), 0)
    u, v = z[:SEVEN], z[SEVEN + 1 :]
    wedge = sum((u[i] * v[j] - u[j] * v[i]) ** 2 for i in range(SEVEN) for j in range(i + 1, SEVEN))
    return {
        "mu": z[MU],
        "eta_u": forms["eta_u"],
        "eta_v": forms["eta_v"],
        "eta_uv": forms["eta_uv"],
        "Q": forms["q"],
        "G": forms["g"],
        "wedge_squares": wedge,
    }


def representative(item: tuple[str, list[int], list[list[int]], list[list[list[int]]]]) -> dict[str, Any]:
    """Rank of C_z, nullity of L_y, tangent dimension of each Pfaffian scheme containing z, orbit dimensions."""
    name, z, family, derivations = item
    matrix = chat(z, 0)
    table = pfaffian_table_int(matrix, 14)
    record: dict[str, Any] = {"point": name, "rank_C": rank_int(matrix), "nullity": nullity_32(y_from_split(z))}
    for order in (14, 12, 10, 8):
        values = [table[m] for m in masks_of_size(order)]
        record[f"tangent_order_{order}"] = None if any(values) else IMAG - rank_int(jacobian_rows(table, order))
    orbit = [act(d, z) for d in derivations]
    record["orbit_dimension"] = rank_q(orbit)
    record["orbit_plus_scaling"] = rank_q([*orbit, z])
    record["orbit_scaling_family"] = rank_q([*orbit, z, *family])
    record["invariants"] = point_invariants(z)
    return record


def representative_points() -> list[tuple[str, list[int], list[list[int]]]]:
    """Exact integer points of every piece and of the strata, with tangent vectors of the family through each."""
    n1 = {1: 1, 3: 1}
    n2s = {4: 1, 6: 1}
    n2g = {2: 1, 5: 1}
    nn = {2: 1, 3: 1}
    e1 = {1: 1}
    # E8 slice parameters (a, b, c, d, m) = (1, 3, 2, 5, 4) with d^2 - b^2 - m^2 = 0 and n = e'_2 + e'_3:
    # tangent vectors da, dc and the two (db, dd, dm) in the kernel of (-2 b, 2 d, -2 m): (5, 3, 0) and (4, 0, -3).
    e8_family = [
        split_vector(nn),
        split_vector({}, 0, nn),
        split_vector({1: 5}, 0, {1: 3}),
        split_vector({1: 4}, -3, {}),
    ]
    b9_family = [split_vector(n1), split_vector(n2s), split_vector({}, 0, n1), split_vector({}, 0, n2s)]
    # V at u' = 3 e'_1, v' = 5 e'_1, mu' = 4 (lambda = 5/3, Q = (1 - lambda^2) eta(u') - mu'^2 = 0): the map
    # (du', dlambda) -> (du', dmu', lambda du' + dlambda u') is injective, and these are 8 of its tangent vectors,
    # scaled to integers (du' = e'_k for k = 2..7 has dmu' = 0; du' = e'_1 has dmu' = 4/3; dlambda = 1 has dmu' = 15/4).
    v_family = [split_vector({k: 3}, 0, {k: 5}) for k in range(2, 8)]
    v_family.append(split_vector({1: 3}, 4, {1: 5}))
    v_family.append(split_vector({}, 15, {1: 12}))
    return [
        (W8_HYPERBOLIC, split_vector(e1, 0, {3: 1}), []),
        ("W8 generic isotropic plane", split_vector(n1, 0, n2g), []),
        ("E8", split_vector(mix((3, e1), (1, nn)), 4, mix((5, e1), (2, nn))), e8_family),
        ("B9", split_vector(mix((1, n1), (2, n2s)), 0, mix((3, n1), (5, n2s))), b9_family),
        ("V", split_vector({1: 3}, 4, {1: 5}), v_family),
        ("V axis {a,0}", split_vector(e1, 0, e1), []),
        ("V and B9 dependent null pair", split_vector(n1, 0, {1: 2, 3: 2}), [split_vector({}, 0, n1)]),
        ("N+", split_vector(n1, 0, n1), []),
        ("N-", split_vector(n1, 0, {1: -1, 3: -1}), []),
        ("V(G) generic", split_vector(e1, 3, {1: 5, 3: 3}), []),
        ("V(Q) and V(G), nullity 4", split_vector(mix((3, e1), (1, {2: 1, 3: 1, 4: 1, 5: -1})), 4, {1: 5}), []),
        ("V(Q) all coordinates nonzero", [1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 2, 3, 2, 2, 3], []),
        ("generic", [1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43], []),
        ("e1 alone", split_vector(e1), []),
    ]


EXPECTED: dict[str, dict[str, Any]] = {
    W8_HYPERBOLIC: {"rank_C": 10, "nullity": 8, "tangent_order_12": 12, "orbit_scaling_family": 12},
    "W8 generic isotropic plane": {"rank_C": 10, "nullity": 8, "tangent_order_12": 12, "orbit_dimension": 11},
    "E8": {"rank_C": 10, "nullity": 8, "tangent_order_12": 11, "orbit_scaling_family": 11},
    "B9": {"rank_C": 8, "nullity": 12, "tangent_order_10": 9, "orbit_scaling_family": 9},
    "V": {"rank_C": 8, "nullity": 12, "tangent_order_10": 8, "orbit_scaling_family": 8},
    "V axis {a,0}": {"rank_C": 8, "nullity": 12, "tangent_order_10": 8},
    "V and B9 dependent null pair": {"rank_C": 8, "nullity": 12, "orbit_scaling_family": 7},
    "N+": {"rank_C": 6, "nullity": 16, "tangent_order_8": 6, "orbit_dimension": 6},
    "N-": {"rank_C": 6, "nullity": 16, "tangent_order_8": 6, "orbit_dimension": 6},
    "V(G) generic": {"rank_C": 12, "nullity": 4, "tangent_order_14": 14},
    "V(Q) and V(G), nullity 4": {"rank_C": 12, "nullity": 4},
    "V(Q) all coordinates nonzero": {"rank_C": 12, "nullity": 4, "tangent_order_14": 14},
    "generic": {"rank_C": 14, "nullity": 0},
}


def admit(record: dict[str, Any], expectation: dict[str, Any]) -> None:
    for key, value in expectation.items():
        _require(record.get(key) == value, f"{record['point']}: {key} is {record.get(key)}, expected {value}")


# ---------------------------------------------------------------------------------------------------------------------
# Zero-divisor set, curve from E8 to B9, piece identities


def zero_divisor_set() -> dict[str, Any]:
    """Q' has a full-rank Hessian; G' is irreducible over Q with a smooth rational zero; Q' does not divide G'.

    Q' and G' are Q and G in the split coordinates z = D z' with D = diag(i^popcount), an invertible linear map over
    Q(i), so absolute irreducibility transfers. The real zeros of G in the original coordinates are singular (they lie
    on W8), which is why the smooth rational point is taken in split coordinates.
    """
    names = [f"z{k}" for k in range(1, HALF)]
    ring = flint.fmpz_mpoly_ctx.get(names, "lex")
    z = list(ring.gens())
    zero = ring.from_dict({})
    forms = split_forms(z, zero)
    q, g = forms["q"], forms["g"]
    hessian = [[q.derivative(i).derivative(j) for j in range(IMAG)] for i in range(IMAG)]
    hessian_rank = rank_int([[int(h.coeffs()[0]) if h != zero else 0 for h in row] for row in hessian])
    content, factors = g.factor()
    point = split_vector({1: 1}, 3, {1: 5, 3: 3})
    gradient = [int(g.derivative(k)(*point)) for k in range(IMAG)]
    return {
        "q_terms": len(q),
        "g_terms": len(g),
        "g_degree": int(g.total_degree()),
        "q_hessian_rank": hessian_rank,
        "g_factor_count": len(factors),
        "g_factor_exponent": int(factors[0][1]),
        "g_content": int(content),
        "smooth_point_split": {"G": int(g(*point)), "Q": int(q(*point)), "gradient_nonzero": any(gradient)},
        "q_divides_g": g % q == zero,
    }


def curve_to_b9(e0_sign: int = -1) -> dict[str, Any]:
    """z(s) with u' = 4 a n + 16 s e0 + 4 k, mu' = 12 s, v' = 4 c n + 20 s e0 + 5 k, n = e'_1 + e'_3, k = e'_4 + e'_6.

    The frame e0 = -e'_2 has eta(e0) = -1, e0 perp n, k and e0 x n = n, while n x k = 0 and n, k are null. For s != 0
    the point is a multiple of (a n + b e_t, m, c n + d e_t) with the unit vector e_t = e0 + k / (4 s), b = 4 s,
    d = 5 s and m = 12 s up to scale, so Q = d^2 - b^2 - m^2 = 0 and z(s) lies in E8. The order-12 Pfaffians vanish in s
    identically, and z(0) lies in B9 with nullity 12.
    """
    s = flint.fmpz_poly([0, 1])
    one = flint.fmpz_poly([1])
    zero = flint.fmpz_poly([0])
    a, c = 1, 2
    n = {1: 1, 3: 1}
    k = {4: 1, 6: 1}
    e0 = {2: e0_sign}
    z = [zero] * IMAG
    for index, coefficient in n.items():
        z[index - 1] = z[index - 1] + one * (4 * a * coefficient)
        z[SEVEN + index] = z[SEVEN + index] + one * (4 * c * coefficient)
    for index, coefficient in k.items():
        z[index - 1] = z[index - 1] + one * (4 * coefficient)
        z[SEVEN + index] = z[SEVEN + index] + one * (5 * coefficient)
    for index, coefficient in e0.items():
        z[index - 1] = z[index - 1] + s * (16 * coefficient)
        z[SEVEN + index] = z[SEVEN + index] + s * (20 * coefficient)
    z[MU] = s * 12
    pf = pfaffian_memo(chat(z, zero), zero, one)
    at_zero = [int(x(0)) for x in z]
    at_two = [int(x(2)) for x in z]
    frame = {
        "eta_e0": eta7(vec7(e0), vec7(e0)),
        "e0_perp_n": eta7(vec7(e0), vec7(n)),
        "e0_perp_k": eta7(vec7(e0), vec7(k)),
        "e0_cross_n_is_n": cross7(vec7(e0), vec7(n)) == vec7(n),
        "n_cross_k_zero": all(x == 0 for x in cross7(vec7(n), vec7(k))),
        "eta_k": eta7(vec7(k), vec7(k)),
        "eta_n": eta7(vec7(n), vec7(n)),
        "eta_k_n": eta7(vec7(k), vec7(n)),
    }
    return {
        "order_12_pfaffians_vanish_identically": all(pf(m) == zero for m in masks_of_size(12)),
        "order_10_pfaffians_not_all_zero": any(pf(m) != zero for m in masks_of_size(10)),
        "frame": frame,
        "rank_at_s_equal_0": cross_rank(at_zero),
        "nullity_at_s_equal_0": nullity_32(y_from_split(at_zero)),
        "rank_at_s_equal_2": cross_rank(at_two),
        "nullity_at_s_equal_2": nullity_32(y_from_split(at_two)),
    }


def piece_identities() -> dict[str, Any]:
    """Polynomial identities that place the pieces inside V(Q) and V(G) (over Z[u', v', mu'])."""
    names = [f"z{k}" for k in range(1, HALF)]
    ring = flint.fmpz_mpoly_ctx.get(names, "lex")
    z = list(ring.gens())
    zero = ring.from_dict({})
    forms = split_forms(z, zero)
    u, mu, v = z[:SEVEN], z[MU], z[SEVEN + 1 :]
    eta_u, eta_v, eta_uv = forms["eta_u"], forms["eta_v"], forms["eta_uv"]
    gram = eta_u * eta_v - eta_uv * eta_uv
    wedge_sum = sum(
        (ETA[i + 1] * ETA[j + 1] * (u[i] * v[j] - u[j] * v[i]) ** 2 for i in range(SEVEN) for j in range(i + 1, SEVEN)),
        zero,
    )
    q = forms["q"]
    q_at_mu_zero = eta_u - eta_v
    g_at_mu_zero = q_at_mu_zero * q_at_mu_zero + 4 * gram
    return {
        "binet_cauchy": gram == wedge_sum,
        "g_equals_q_squared_plus_4_gram": forms["g"] == q * q + 4 * gram,
        "q_without_mu": q + mu * mu == eta_u - eta_v,
        "g_at_mu_zero_is_square_difference": g_at_mu_zero == (eta_u + eta_v) ** 2 - 4 * eta_uv * eta_uv,
    }


# ---------------------------------------------------------------------------------------------------------------------
# Strata, incidences and connected components


def unit_dimension(complex_dimension: int) -> int:
    """Real dimension of the unit section of a complex cone of the given dimension in C^15 = R^30."""
    return 2 * complex_dimension - 1


def in_piece(name: str, z: Sequence[int]) -> bool:
    """Membership of an integer split point in the intrinsic equations of a piece."""
    inv = point_invariants(z)
    isotropic = inv["eta_u"] == 0 and inv["eta_v"] == 0 and inv["eta_uv"] == 0
    u, v = z[:SEVEN], z[SEVEN + 1 :]
    if name == "W8":
        return inv["mu"] == 0 and inv["eta_u"] + inv["eta_v"] == 0 and inv["eta_uv"] == 0
    if name == "V":
        return inv["Q"] == 0 and inv["wedge_squares"] == 0
    if name == "B9":
        return inv["mu"] == 0 and isotropic and all(x == 0 for x in cross7(u, v))
    if name == "Np":
        return inv["mu"] == 0 and list(u) == list(v) and inv["eta_u"] == 0
    if name == "Nm":
        return inv["mu"] == 0 and list(u) == [-x for x in v] and inv["eta_u"] == 0
    raise KeyError(name)


def piece_row(piece: str, in_mu_zero: bool) -> dict[str, Any]:
    dimension = PIECE_DIMENSIONS[piece]
    return {
        "complex": dimension,
        "cone_real": 2 * dimension,
        "unit_real": unit_dimension(dimension),
        "inside_mu_zero": in_mu_zero,
        "unit_real_in_mu_zero": unit_dimension(dimension if in_mu_zero else dimension - 1),
    }


def topology(reps: list[dict[str, Any]], certificates: list[dict[str, Any]], orbits: dict[str, Any]) -> dict[str, Any]:
    """Dimensions, components, incidences and connected components, each derived from the exact data above."""
    by_name = {row["point"]: row for row in reps}
    points = {name: z for name, z, _family in representative_points()}
    dims = PIECE_DIMENSIONS
    # Exact local dimensions: the orbit-family rank (a lower bound) equals the tangent dimension of the scheme.
    hyperbolic = by_name[W8_HYPERBOLIC]
    exact = {
        "W8": (hyperbolic["orbit_scaling_family"], hyperbolic["tangent_order_12"]),
        "E8": (by_name["E8"]["orbit_scaling_family"], by_name["E8"]["tangent_order_12"]),
        "B9": (by_name["B9"]["orbit_scaling_family"], by_name["B9"]["tangent_order_10"]),
        "V": (by_name["V"]["orbit_scaling_family"], by_name["V"]["tangent_order_10"]),
        "N": (by_name["N+"]["orbit_dimension"], by_name["N+"]["tangent_order_8"]),
    }
    for piece, (lower, upper) in exact.items():
        _require(lower == upper == dims[piece], f"the dimension of {piece} is not pinned: {lower}, {upper}")
    _require(
        by_name["V(G) generic"]["tangent_order_14"] == 14
        and by_name["V(Q) all coordinates nonzero"]["tangent_order_14"] == 14,
        "V(Q) or V(G) is not a regular hypersurface at its representative",
    )
    # Representatives lie on the intended pieces and off the others.
    membership = {
        name: {piece: in_piece(piece, z) for piece in ("W8", "V", "B9", "Np", "Nm")} for name, z in points.items()
    }
    _require(membership[W8_HYPERBOLIC]["W8"] and not membership[W8_HYPERBOLIC]["V"], "the W8 representative")
    _require(membership["B9"]["B9"] and not membership["B9"]["V"], "the B9 representative is not on B9 alone")
    _require(membership["V"]["V"] and not membership["V"]["W8"] and not membership["V"]["B9"], "the V representative")
    both = membership["V and B9 dependent null pair"]
    _require(both["V"] and both["B9"] and both["W8"], "the V and B9 intersection point")
    axis = membership["V axis {a,0}"]
    _require(axis["V"] and not axis["W8"] and not axis["B9"], "the {a,0} point")
    _require(
        membership["N+"]["Np"]
        and membership["N+"]["V"]
        and membership["N+"]["B9"]
        and membership["N-"]["Nm"]
        and membership["N-"]["V"]
        and membership["N-"]["B9"],
        "an N point is off V or B9",
    )
    inv = {name: by_name[name]["invariants"] for name in by_name}
    _require(inv["E8"]["mu"] != 0 and inv["V"]["mu"] != 0, "E8 or V lies in mu = 0")
    _require(inv[W8_HYPERBOLIC]["mu"] == 0 and inv["B9"]["mu"] == 0, "W8 or B9 leaves mu = 0")
    _require(inv[W8_HYPERBOLIC]["Q"] != 0 and inv[W8_HYPERBOLIC]["G"] == 0, "W8 is not in V(G) outside V(Q)")
    for name in ("E8", "V", "B9", "N+", "V(Q) and V(G), nullity 4"):
        _require(inv[name]["Q"] == 0 and inv[name]["G"] == 0, f"{name} is outside V(Q) and V(G)")
    _require(
        all(row["gram_determinant_vanishes"] for row in certificates if row["slice"] in ("P3a", "P3b")),
        "the P3 slices do not have Gram rank 1",
    )
    _require(by_name["V(Q) and V(G), nullity 4"]["nullity"] == 4, "no nullity-4 point on V(Q) and V(G)")
    regular = (hyperbolic["tangent_order_12"], by_name["W8 generic isotropic plane"]["tangent_order_12"])
    _require(all(value == dims["W8"] for value in regular), "W8 is not regular at its nullity-8 orbit types")
    planes = orbits["plane_table"]
    _require(
        planes["P2"]["plane_orbit_dimension"] == 10
        and planes["P4g"]["induced_rank_in_gl2"] == 4
        and planes["P4g"]["ordered_pair_orbit_dimension"] == 11
        and orbits["orbit_dimension_frame_e1_e2"] == 11,
        "W8 minus R_12 is not two single orbit types",
    )
    pieces = {
        "W8": piece_row("W8", True),
        "E8": piece_row("E8", False),
        "V": piece_row("V", False),
        "B9": piece_row("B9", True),
        "N": piece_row("N", True),
        "VQ": piece_row("VQ", False),
        "VG": piece_row("VG", False),
    }
    strata = {
        "4": {
            "irreducible_pieces": ["VQ", "VG"],
            "unit_dimensions": [pieces["VQ"]["unit_real"], pieces["VG"]["unit_real"]],
            "connected_components": 1,
            "why": "V(Q) and V(G) are irreducible, R_8 is a proper closed subset of each, and a nullity-4 point lies "
            "on both",
        },
        "8": {
            "irreducible_pieces": ["W8", "E8-bar"],
            "unit_dimensions": [pieces["W8"]["unit_real"], pieces["E8"]["unit_real"]],
            "connected_components": 2,
            "why": "W8 minus R_12 is regular for the order-12 Pfaffian scheme (two single orbit types), so E8-bar, "
            "irreducible and not inside {mu = 0}, misses it",
        },
        "12": {
            "irreducible_pieces": ["V", "B9"],
            "unit_dimensions": [pieces["V"]["unit_real"], pieces["B9"]["unit_real"]],
            "connected_components": 1,
            "why": "V minus R_16 and B9 minus R_16 are connected and share a nullity-12 point",
        },
        "16": {
            "irreducible_pieces": ["N+", "N-"],
            "unit_dimensions": [pieces["N"]["unit_real"]] * 2,
            "connected_components": 2,
            "why": "N+ and N- are irreducible cones meeting only at 0",
        },
    }
    return {
        "pieces": pieces,
        "strata": strata,
        "intersection_V_B9": {
            "complex": 7,
            "unit_real": unit_dimension(7),
            "lower_bound_rank": by_name["V and B9 dependent null pair"]["orbit_scaling_family"],
        },
        "membership_of_representatives": membership,
    }


def strata_statements() -> list[dict[str, Any]]:
    """The registry statements with status, each tied to the record fields that carry it."""
    return [
        {
            "id": 1,
            "status": "established",
            "claim": "every zero divisor of A_5 is doubly pure (y_0 = y_16 = 0)",
            "carried_by": ["doubly_pure"],
        },
        {
            "id": 2,
            "status": "established",
            "claim": "for doubly pure y != 0, nullity L_y = 28 - 2 rank C_z, so nullity 4, 8, 12, 16 is rank C_z = "
            "12, 10, 8, 6",
            "carried_by": ["nullity_identity", "split_algebra"],
        },
        {
            "id": 3,
            "status": "established",
            "claim": "Z_5 minus 0 is V(Q) u V(G) in C^15; Q and G are absolutely irreducible; complex dimension 14, "
            "real cone dimension 28, unit dimension 27; each unit section is connected",
            "carried_by": ["split_factorization", "zero_divisor_set"],
        },
        {
            "id": 4,
            "status": "established",
            "claim": "C_z satisfies C (C^2 + Q)(C^4 + 2 Q C^2 + G) = 0 with characteristic polynomial "
            "l (l^2 + Q)^3 (l^4 + 2 Q l^2 + G)^2",
            "carried_by": ["characteristic_identities", "orbit_facts"],
        },
        {
            "id": 5,
            "status": "established",
            "claim": "every pair (u, v) lies in a G_2-translate of one of six slice families, and on each slice the "
            "Pfaffian ideals of orders 12, 10, 8 have the exact varieties of LEVEL_PIECES",
            "carried_by": ["orbit_facts", "slice_certificates"],
        },
        {
            "id": 6,
            "status": "established",
            "claim": "R_16 = N_+ u N_-: two irreducible cones of complex dimension 6, unit dimension 11 (V_2(R^7)), "
            "meeting only at 0; R_12 = V u B9, irreducible of complex dimensions 8 and 9 (unit 15 and 17), "
            "meeting in complex dimension 7 (unit 13); R_8 = W8 u E8-bar, irreducible of complex dimensions 12 "
            "and 11 (unit 23 and 21)",
            "carried_by": ["slice_certificates", "containment_table", "representatives", "topology"],
        },
        {
            "id": 7,
            "status": "established",
            "claim": "V lies in E8-bar, B9 in W8 and in E8-bar, N_+ and N_- in V and in B9; W8 lies in V(G) only; "
            "E8-bar, V, B9 lie in V(Q) and V(G)",
            "carried_by": ["curve_to_b9", "piece_identities", "topology"],
        },
        {
            "id": 8,
            "status": "established",
            "claim": "D_(5,4) is connected (two irreducible algebraic pieces, unit dimension 27 each); D_(5,8) has two "
            "connected components (unit dimensions 23 and 21); D_(5,12) is connected (two irreducible pieces, unit "
            "dimensions 15 and 17); D_(5,16) has two components (unit dimension 11 each)",
            "carried_by": ["topology"],
        },
        {
            "id": 9,
            "status": "open",
            "claim": "smoothness and singular loci of the pieces, normal links, kernel bundles, attachments and "
            "homology (roadmap items 4 to 8)",
            "carried_by": [],
        },
    ]


# ---------------------------------------------------------------------------------------------------------------------
# Drivers


def containment_table(certificates: list[dict[str, Any]]) -> dict[str, dict[str, bool]]:
    """piece -> True when the order-L Pfaffian ideal lies in the piece ideal on every slice (the piece lies in R_L)."""
    table: dict[str, dict[str, bool]] = {}
    for level in LEVELS:
        rows = [row for row in certificates if row["order"] == level]
        table[str(level)] = {}
        for piece in PIECE_ORDER:
            relevant = [
                row["ideal_inside_piece_ideal"][piece] for row in rows if piece in row["ideal_inside_piece_ideal"]
            ]
            table[str(level)][piece] = bool(relevant) and all(relevant)
    return table


def check_orbit_facts(orbits: dict[str, Any]) -> None:
    _require(
        orbits["derivations"]["count"] == 14
        and orbits["derivations"]["block_diagonal_fixing_e0_e8"]
        and orbits["derivations"]["same_block_on_u_and_v"]
        and orbits["derivations"]["eta_invariant"]
        and orbits["equivariance_cprime"]
        and orbits["slice_dominance_rank"] == IMAG
        and orbits["quadric_certificate"]["unique_solution"],
        "a derivation, equivariance or quadric certificate fails",
    )
    sl3 = orbits["sl3"]
    _require(
        sl3["stabilizer_dimension"] == 8
        and sl3["commutes_with_left_e1"]
        and all(
            sl3[name]["eigenvectors"]
            and sl3[name]["totally_null"]
            and sl3[name]["invariant"]
            and sl3[name]["traceless"]
            and sl3[name]["action_rank"] == 8
            for name in ("plus", "minus")
        )
        and sl3["pairing_plus_minus_rank"] == 3,
        "the stabilizer of e_1 is not sl_3 on V_+ and V_-",
    )
    _require(all(value == 6 for value in orbits["null_orbit_dimensions"].values()), "a null orbit is not open")
    planes = orbits["isotropic_planes"]
    _require(
        planes["stabilizer_dimension"] == 8
        and all(power is not None for power in planes["special_forms_radical_powers"])
        and planes["special_forms_equal_cross_product_locus"]
        and planes["special_subspace_invariant"]
        and planes["traceless_action_rank_on_special_line"] == 3,
        "the isotropic plane certificate fails",
    )
    table = orbits["plane_table"]
    _require(
        table["P2"]["plane_orbit_dimension"] == 10
        and table["P4g"]["plane_orbit_dimension"] == 7
        and table["P4g"]["induced_rank_in_gl2"] == 4
        and table["P4g"]["ordered_pair_orbit_dimension"] == 11
        and table["P4s"]["plane_orbit_dimension"] == 5
        and table["P4s"]["induced_rank_in_gl2"] == 4
        and table["P4s"]["ordered_pair_orbit_dimension"] == 9,
        "a plane orbit dimension differs",
    )


def measure() -> dict[str, Any]:
    doubly = doubly_pure()
    _require(
        doubly["j_squares_to_minus_identity"]
        and doubly["imaginary_left_matrices_skew"]
        and doubly["anticommuting_basis_elements"] == doubly["basis_elements_outside_C5"] == 30,
        "the operator identities of the doubly pure theorem fail",
    )
    algebra = split_algebra()
    _require(all(algebra.values()), "the split matrix is not skew or not congruent to C_z")
    factorization = split_factorization()
    _require(
        factorization["skew"]
        and all(factorization["cofactors_equal_q_g_z"])
        and factorization["q_is_sum_eps_z_squared"],
        "a cofactor of eta C' is not Q G z_j",
    )
    derivations = split_derivations()
    points = [(name, z, 28) for name, z, _family in representative_points()]
    nullities = parallel.ordered_map(nullity_identity, points, min_items=2)
    _require(all(row["agrees"] for row in nullities), "nullity differs from 28 - 2 rank C_z")
    characteristic = characteristic_identities()
    _require(all(characteristic.values()), "a characteristic identity fails on the slice")
    orbits = orbit_facts()
    check_orbit_facts(orbits)
    items = [(name, z, family, derivations) for name, z, family in representative_points()]
    reps = parallel.ordered_map(representative, items, min_items=2)
    for row in reps:
        if row["point"] in EXPECTED:
            admit(row, EXPECTED[row["point"]])
    certificates = parallel.ordered_map(
        slice_certificate, [(name, level, False) for level in LEVELS for name in SLICE_NAMES], min_items=2
    )
    for row in certificates:
        _require(row["covering"]["prefix"] is not None, f"{row['slice']} order {row['order']}: pieces do not cover")
        for piece in row["named_pieces"]:
            _require(
                row["ideal_inside_piece_ideal"][piece], f"{row['slice']} order {row['order']}: ideal not inside {piece}"
            )
    containment = containment_table(certificates)
    for level, named in {12: ("W8", "E8", "V"), 10: ("V", "B9"), 8: ("Np", "Nm")}.items():
        for piece in named:
            _require(containment[str(level)][piece], f"{piece} is not inside R at order {level}")
    for level, named in {10: ("W8", "E8"), 8: ("W8", "V", "B9")}.items():
        for piece in named:
            _require(not containment[str(level)][piece], f"{piece} lies inside R at order {level}")
    divisor = zero_divisor_set()
    _require(
        divisor["q_hessian_rank"] == IMAG
        and divisor["g_factor_count"] == 1
        and divisor["g_factor_exponent"] == 1
        and not divisor["q_divides_g"]
        and divisor["smooth_point_split"]["gradient_nonzero"]
        and divisor["smooth_point_split"]["G"] == 0
        and divisor["smooth_point_split"]["Q"] != 0,
        "Q or G fails its irreducibility certificate",
    )
    curve = curve_to_b9()
    frame = curve["frame"]
    _require(
        curve["order_12_pfaffians_vanish_identically"]
        and curve["order_10_pfaffians_not_all_zero"]
        and frame["eta_e0"] == -1
        and frame["e0_perp_n"] == 0
        and frame["e0_perp_k"] == 0
        and frame["e0_cross_n_is_n"]
        and frame["n_cross_k_zero"]
        and frame["eta_k"] == 0
        and frame["eta_n"] == 0
        and frame["eta_k_n"] == 0
        and curve["nullity_at_s_equal_0"] == 12
        and curve["nullity_at_s_equal_2"] == 8,
        "the curve from E8 to B9 fails",
    )
    identities = piece_identities()
    _require(all(identities.values()), "a piece identity fails")
    summary = topology(reps, certificates, orbits)
    return {
        "schema": SCHEMA,
        "versions": {
            "python-flint": importlib.metadata.version("python-flint"),
            "sympy": importlib.metadata.version("sympy"),
        },
        "doubly_pure": doubly,
        "split_algebra": algebra,
        "split_factorization": factorization,
        "nullity_identity": nullities,
        "characteristic_identities": characteristic,
        "orbit_facts": orbits,
        "slice_certificates": certificates,
        "containment_table": containment,
        "representatives": reps,
        "zero_divisor_set": divisor,
        "curve_to_b9": curve,
        "piece_identities": identities,
        "topology": summary,
        "statements": strata_statements(),
    }


_MISSING = object()


def differences(retained: Any, fresh: Any, path: str = "") -> list[str]:
    """Paths where the records differ; a key present on one side only, or a value of another type, differs."""
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


def refused(function: Callable[..., Any], *arguments: Any) -> bool:
    try:
        function(*arguments)
    except SystemExit:
        return True
    return False


def self_test() -> str:
    count = 0
    # A flipped structure constant breaks skewness of eta C'.
    flipped = copy.deepcopy(SPLIT)
    flipped[3][12] = -flipped[3][12]
    _require(not split_algebra(flipped)["skew_on_basis"], "a flipped split constant keeps eta C' skew")
    count += 1
    # A flipped entry of J breaks the operator identities of the doubly pure theorem.
    broken = doubly_pure(flip=(1, 17))
    _require(
        not broken["j_squares_to_minus_identity"]
        or broken["anticommuting_basis_elements"] < broken["basis_elements_outside_C5"],
        "a flipped entry of L_(e_16) keeps the operator identities",
    )
    count += 1
    # The nullity formula needs the constant 28.
    wrong = [nullity_identity((name, z, 26)) for name, z, _ in representative_points()[:6]]
    _require(not all(row["agrees"] for row in wrong), "nullity = 26 - 2 rank agrees")
    count += 1
    # A dropped piece breaks the radical-power covering, and a wrong piece breaks containment.
    _require(slice_certificate(("P2", 12, True))["covering"]["prefix"] is None, "P2 order 12 is covered without V")
    count += 1
    ring, gens, zero, one = slice_ring()
    tool = GroebnerTool(ring)
    generators = ideal_generators(chat(slice_point("P2", gens, zero), zero), zero, one, 12)
    pieces = slice_pieces("P2", gens, zero)
    only_m = tool.groebner([gens[4]])
    _require(
        not all(tool.is_member(g, only_m) for g in generators),
        "the order-12 ideal lies in (m): the V piece would be spurious",
    )
    count += 1
    wrong_w8 = tool.groebner(pieces["W8"][:2])
    _require(
        not all(tool.is_member(g, wrong_w8) for g in generators),
        "a W8 piece without eta(u, v) = 0 still contains the ideal",
    )
    count += 1
    derivations = split_derivations()
    blocks = [block7(d) for d in derivations]
    _require(
        not quadric_certificate(blocks, [0, 1, 1, 1, 1, 1, 1, 1])["unique_solution"],
        "a wrong form passes the quadric certificate",
    )
    count += 1
    # The E8-to-B9 curve needs the eigenvalue-one frame.
    _require(not curve_to_b9(e0_sign=1)["frame"]["e0_cross_n_is_n"], "the reversed frame keeps e0 x n = n")
    count += 1
    # A corrupted representative row is refused.
    rows = parallel.ordered_map(
        representative, [(n, z, f, derivations) for n, z, f in representative_points()[:4]], min_items=2
    )
    damaged = copy.deepcopy(rows[2])
    damaged["tangent_order_12"] = 12
    _require(refused(admit, damaged, EXPECTED["E8"]), "a corrupted tangent dimension is admitted")
    damaged = copy.deepcopy(rows[3])
    damaged["rank_C"] = 10
    _require(refused(admit, damaged, EXPECTED["B9"]), "a corrupted rank is admitted")
    count += 2
    # The intrinsic equations separate the pieces at the representatives.
    points = {name: z for name, z, _ in representative_points()}
    _require(not in_piece("V", points[W8_HYPERBOLIC]), "the W8 representative lies in V")
    _require(not in_piece("B9", points["V"]), "the V representative lies in B9")
    _require(not in_piece("W8", points["V"]), "the V representative lies in W8")
    count += 3
    return f"{count} mutations and corruptions rejected"


# ---------------------------------------------------------------------------------------------------------------------
# Exploration: order-14 slice varieties and a deterministic numerical search for stray components


def order_14_certificate(name: str) -> dict[str, Any]:
    """The order-14 Pfaffian ideal on a slice has Q G in its radical and every generator in (Q) or (G)."""
    ring, gens, zero, one = slice_ring()
    tool = GroebnerTool(ring)
    z = slice_point(name, gens, zero)
    forms = split_forms(z, zero)
    generators = ideal_generators(chat(z, zero), zero, one, 14)
    q, g = forms["q"], forms["g"]
    basis = tool.groebner(generators)
    inside_q = tool.groebner([q])
    inside_g = tool.groebner([g])
    contained = all(tool.is_member(p, inside_q) or tool.is_member(p, inside_g) for p in generators)
    return {
        "slice": name,
        "generators": len(generators),
        "q_g_radical_power": tool.in_radical(q * g, basis),
        "each_generator_in_q_or_g": contained,
    }


def numerical_start(item: tuple[int, int]) -> dict[str, Any]:
    """Least squares for a point with rank C <= bound from a Kronecker-sequence start (deterministic, no seed)."""
    import numpy as np  # noqa: PLC0415
    from scipy.optimize import least_squares  # noqa: PLC0415

    index, rank_bound = item
    table = np.array([[cd_sign(HALF, a, b) for b in range(HALF)] for a in range(HALF)])
    idx = np.arange(1, HALF)
    xor = idx[:, None] ^ idx[None, :]
    signs = table[xor, idx[None, :]]
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    primes += [53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113]
    start = np.array([((index * math.sqrt(p)) % 1.0 - 0.5) * 3.0 for p in primes])

    def residual(x: Any) -> Any:
        z = x[:IMAG] + 1j * x[IMAG:]
        matrix = z[xor - 1] * signs
        matrix[np.arange(IMAG), np.arange(IMAG)] = 0
        values = np.linalg.svd(matrix, compute_uv=False)
        return np.concatenate([values[rank_bound : IMAG - 1] ** 2, [np.linalg.norm(z) ** 2 - 1.0]])

    result = least_squares(residual, start, method="trf", xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=2000)
    if np.linalg.norm(result.fun) > 1e-9:
        return {"index": index, "converged": False}
    z = result.x[:IMAG] + 1j * result.x[IMAG:]
    u, mu, v = z[:7], z[7], z[8:]
    big_u, big_v, big_w = u @ u, v @ v, u @ v
    q = big_u + mu * mu + big_v
    delta = big_u * big_v - big_w * big_w
    w, wp = u + 1j * v, u - 1j * v
    tolerance = 1e-5
    kind = "other"
    if abs(mu) < tolerance and abs(w @ w) < tolerance and abs(wp @ wp) < tolerance:
        kind = "W8"
    elif abs(q) < tolerance and abs(delta) < tolerance:
        kind = "V(Q) with Gram rank at most 1"
    return {"index": index, "converged": True, "kind": kind}


def explore() -> dict[str, Any]:
    order_14 = parallel.ordered_map(order_14_certificate, list(SLICE_NAMES), min_items=2)
    searches = {}
    for bound, label in ((10, "R_8"), (8, "R_12"), (6, "R_16")):
        rows = parallel.ordered_map(numerical_start, [(index, bound) for index in range(1, 25)], min_items=2)
        counts: dict[str, int] = {}
        for row in rows:
            key = row["kind"] if row["converged"] else "not converged"
            counts[key] = counts.get(key, 0) + 1
        searches[label] = counts
    return {"schema": SCHEMA + "-explore", "order_14_slices": order_14, "numerical_search_counts": searches}


def summarize(data: dict[str, Any]) -> None:
    for row in data["nullity_identity"]:
        print(f"point {row['point']:36s} rank C {row['rank_C']:2d} nullity {row['nullity']:2d}")
    for row in data["slice_certificates"]:
        print(
            f"slice {row['slice']:4s} order {row['order']:2d} gens {row['generators']:5d} pieces {row['named_pieces']} "
            f"prefix {row['covering']['prefix']} power {row['covering']['max_power']}"
        )
    for row in data["representatives"]:
        print(
            f"rep {row['point']:36s} rank {row['rank_C']:2d} T14 {row['tangent_order_14']} "
            f"T12 {row['tangent_order_12']} "
            f"T10 {row['tangent_order_10']} T8 {row['tangent_order_8']} orbit {row['orbit_dimension']} "
            f"+scale {row['orbit_plus_scaling']} +family {row['orbit_scaling_family']}"
        )
    for level, row in data["topology"]["strata"].items():
        print(
            f"D_(5,{level}): pieces {row['irreducible_pieces']} unit dimensions {row['unit_dimensions']} "
            f"connected components {row['connected_components']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--explore", type=Path)
    arguments = parser.parse_args()
    if arguments.self_test:
        print(f"a5_zero_divisor_strata self-test: {self_test()}")
        return 0
    if arguments.explore is not None:
        arguments.explore.parent.mkdir(parents=True, exist_ok=True)
        arguments.explore.write_text(json.dumps(explore(), indent=1, sort_keys=True) + "\n")
        return 0
    data = json.loads(json.dumps(measure(), default=int))
    if arguments.check is not None:
        retained = json.loads(arguments.check.read_text())
        differing = differences(
            {k: v for k, v in retained.items() if k != "versions"}, {k: v for k, v in data.items() if k != "versions"}
        )
        if differing:
            raise SystemExit(f"a5_zero_divisor_strata: {differing} differ from {arguments.check}")
    else:
        arguments.out.parent.mkdir(parents=True, exist_ok=True)
        arguments.out.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
    summarize(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
