"""Exact first-order directions that the A_5 rank-locus families with a non-zero-divisor entry leave open.

scripts/rank_locus_local_dimension.py certifies, at each witness x of the
families nonzd-axis, zd-nonzd-locus, zd-nonzd-generic and nonzd-nonzd-locus,
that the unit locus D_(5,k) has local dimension at most dim T(x) - 1, two
above the family. Here V spans ker L_x, U spans ker L_x^T and

    T(x)   = {y in R^32 : U^T L_y V = 0},
    T_1(x) = T(x) intersected with x^perp (the norm row <x, y> = 0),

so the unit tangent bound is dim T_1(x) and the radial direction x is
excluded from every comparison.

The family tangent space T_F at x is built from the family's own
parameterization in the bracket coordinates {a, b} = (a + b, e_8 (b - a)),
a linear injection of C_4^perp x C_4^perp onto H_5^perp. (a, b) is read back
from x as a = (x' + e_8 x'')/2, b = (x' - e_8 x'')/2. Velocities of exact
curves inside the cone family span a subspace P of the parameter space:

  automorphism flows  exp(s D) on both entries for each of the 14 derivations
                      D of the octonions, extended diagonally to A_4; the
                      extension is checked to be a derivation of A_4 and of
                      A_5, skew-symmetric and zero on e_0 and e_8, so exp(s D)
                      is an orthogonal automorphism that fixes e_8 and maps
                      Z, Ann(a) and W(a) onto Z, Ann(exp(sD) a), W(exp(sD) a)
  scalings            (s a, b) and (a, s b), when the family is closed under them
  lines               (a, b + s w) for w in a linear fiber, (a + s v, b) for v in
                      C_4^perp when the a-condition is open (a outside Z)
  projections         a(s) = a + s t with b(s) the orthogonal projection of b onto
                      W'(a(s)) = C_4^perp cap {a(s), e_8 a(s)}^perp, a rational
                      curve with velocity (t, -[a, e_8 a] G^-1 [<t, b>, <e_8 t, b>])

The family is a manifold of dimension d + 1 at the cone level (the
certificate's bundle statement), so rank P = d + 1 makes P its tangent space
exactly. Each family also carries defining equations that vanish on it near
(a, b), so its tangent space lies in the kernel J of their Jacobian:

  nonzd-axis          b = 0 (linear)
  zd-nonzd-generic    q1 = |a'|^2 - |a''|^2, q2 = <a', a''> (Moreno's description of
                      the zero-divisor cone Z of A_4 in Im O x Im O)
  zd-nonzd-locus      q1, q2, <a, b>, <b, e_8 a> and E = (L_a^2 + |a|^2)(L_a^2 + 2|a|^2) b,
                      which is 2|a|^4 times the projection of b on Ann(a) because
                      -L_a^2 / |a|^2 has eigenvalues 0, 1, 2 on a zero divisor
  nonzd-nonzd-locus   <a, b>, <b, e_8 a>; its Jacobian has rank 2, so by the implicit
                      function theorem the family is a 26-manifold with tangent J

The run requires P = J, which sandwiches the family tangent space between
two exact subspaces of the same dimension. At a zero-divisor entry a the
a-component tangent space T_Z(a) = span{D a} + R a is compared with the
Moreno kernel and with the A_4 tangent bound {alpha : U_a^T L_alpha V_a = 0}.
T_F is the image of P under the bracket intersected with x^perp; its
dimension must equal the family dimension of witnesses(), it must lie in
T_1(x) (exact integer check on every basis vector) and in H_5^perp.

H_5 = span{e_0, e_8, e_16, e_24} and T_F lies in H_5^perp, so the coordinate
projection pi(y) = (y_8, y_24) vanishes on T_F and induces a well-defined map
T_1(x)/T_F -> span{e_8, e_24}. Its rank equals rank pi(T_1(x)) and rank pi(C)
for the canonical complement C = T_1(x) cap T_F^perp; when the rank is 2 the
record gives the unique basis c_8, c_24 of C with pi(c_8) = (1, 0) and
pi(c_24) = (0, 1), together with their e_0 and e_16 coordinates. The record
also gives dim(T_1(x) cap H_5^perp).

Prediction, stated before the run: rank 2 at every witness. Falsifier: rank
below 2 at any witness refutes the statement that the extra first-order
directions leave H_5^perp through e_8 and e_24, and leaves the local-dimension
question open. The computation is first order only; T_1(x) bounds the tangent
cone and decides no second-order compatibility.

Exactness: kernels come from FLINT's fmpq_mat reduced row echelon form
(exact_rank.rational_kernel), every kernel vector is checked in Python
integer arithmetic, and each kernel dimension is pinned by rank modulo
2^61 - 1 (a lower bound on the rational rank) plus verified independent
kernel vectors.

Usage:
    "$PYTHON" scripts/rank_locus_gap_directions.py --out PATH
    "$PYTHON" scripts/rank_locus_gap_directions.py --check PATH
    "$PYTHON" scripts/rank_locus_gap_directions.py --self-test

--check recomputes every witness and requires the retained file to equal,
byte for byte, the text --out writes. --self-test requires the row verifier
to reject a corrupted nullity, kernel frame, T_F basis vector, T_F
containment, complement vector, T_1 dimension and projection rank.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
from fractions import Fraction
from functools import cache
from pathlib import Path
from typing import Any

import flint

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
from d_locus_nullity import apply, bracket, dot, frame_spaces, left_rational  # noqa: E402
from exact_rank import rank_mod, rational_kernel  # noqa: E402
from moreno_stiefel_nullity import PRIME  # noqa: E402
from rank_locus_local_dimension import basis_vector, c_orthogonal_space, witnesses  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "rank-locus-gap-directions-v1"
DIM = 32
HALF = 16
OCT = 8
I4 = 8
FAMILIES = ("nonzd-axis", "zd-nonzd-locus", "zd-nonzd-generic", "nonzd-nonzd-locus")
H5 = (0, 8, 16, 24)
EXIT = (8, 24)
C4 = (0, I4)
ZD_TANGENT_DIMENSION = 12
OCTONION_DERIVATIONS = 14
Vector = list[Fraction]


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"rank_locus_gap_directions: {message}")


def encode(vector: Vector) -> str:
    return " ".join(str(value) for value in vector)


def decode(text: str) -> Vector:
    return [Fraction(value) for value in text.split()]


def integer_vector(vector: Vector) -> list[int]:
    """lcm(denominators) times the vector; int and Fraction both carry numerator and denominator."""
    scale = math.lcm(1, *(value.denominator for value in vector))
    return [value.numerator * (scale // value.denominator) for value in vector]


def integer_rows(rows: list[Vector]) -> list[list[int]]:
    return [integer_vector(row) for row in rows]


def kernel(rows: list[Vector], width: int) -> list[Vector]:
    """Null space of the stacked rows, each row scaled to integers on its own."""
    return rational_kernel(integer_rows(rows)) if rows else [basis_vector(k, width) for k in range(width)]


def rank_p(rows: list[Vector]) -> int:
    return rank_mod(integer_rows(rows), PRIME) if rows else 0


def annihilated(rows: list[list[int]], vector: Vector) -> bool:
    scaled = integer_vector(vector)
    return all(sum(entry * value for entry, value in zip(row, scaled, strict=True)) == 0 for row in rows)


def rref(vectors: list[Vector]) -> list[Vector]:
    """The nonzero rows of the reduced row echelon form, the canonical basis of the span."""
    if not vectors:
        return []
    reduced, rank = flint.fmpq_mat(integer_rows(vectors)).rref()
    columns = reduced.ncols()
    return [
        [Fraction(int(reduced[row, column].p), int(reduced[row, column].q)) for column in range(columns)]
        for row in range(rank)
    ]


def verified_kernel(rows: list[Vector], width: int) -> list[Vector]:
    """A kernel basis whose every vector is checked in integers and whose size rank_p pins from both sides."""
    basis = kernel(rows, width)
    integers = integer_rows(rows)
    _require(all(annihilated(integers, vector) for vector in basis), "a kernel vector fails its equations")
    _require(rank_p(rows) + len(basis) == width, "rank modulo P and the kernel size do not pin the nullity")
    _require(rank_p(basis) == len(basis), "kernel vectors are dependent")
    return basis


@cache
def sign_table() -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(cd_sign(DIM, i, j) for j in range(DIM)) for i in range(DIM))


def is_derivation(matrix: list[list[int]], dim: int) -> bool:
    """D(e_i e_j) = D(e_i) e_j + e_i D(e_j) on every basis pair, by cd_sign structure constants."""
    signs = sign_table() if dim == DIM else tuple(tuple(cd_sign(dim, i, j) for j in range(dim)) for i in range(dim))
    for i in range(dim):
        for j in range(dim):
            s = signs[i][j]
            for r in range(dim):
                lhs = s * matrix[r][i ^ j]
                rhs = matrix[r ^ j][i] * signs[r ^ j][j] + matrix[i ^ r][j] * signs[i][i ^ r]
                if lhs != rhs:
                    return False
    return True


@cache
def derivations() -> tuple[tuple[tuple[int, ...], ...], ...]:
    """The 14 derivations of the octonions, extended diagonally to A_4, as integer 16 x 16 matrices.

    The 64 unknowns D[r][c] solve the linear derivation identity on all 64
    basis pairs of A_3; the diagonal extension diag(D, D) is then checked to
    be a skew-symmetric derivation of A_4 vanishing on e_0 and e_8, and
    diag(D, D, D, D) a derivation of A_5.
    """
    equations: list[Vector] = []
    for i in range(OCT):
        for j in range(OCT):
            for r in range(OCT):
                row = [Fraction(0)] * (OCT * OCT)
                row[r * OCT + (i ^ j)] += cd_sign(OCT, i, j)
                row[(r ^ j) * OCT + i] -= cd_sign(OCT, r ^ j, j)
                row[(i ^ r) * OCT + j] -= cd_sign(OCT, i, i ^ r)
                equations.append(row)
    solutions = verified_kernel(equations, OCT * OCT)
    _require(len(solutions) == OCTONION_DERIVATIONS, f"der(O) has dimension {len(solutions)}")
    out = []
    for solution in solutions:
        scaled = integer_vector(solution)
        octonion = [[scaled[r * OCT + c] for c in range(OCT)] for r in range(OCT)]
        extended = [[0] * HALF for _ in range(HALF)]
        doubled = [[0] * DIM for _ in range(DIM)]
        for block in range(DIM // OCT):
            for r in range(OCT):
                for c in range(OCT):
                    if block < 2:
                        extended[block * OCT + r][block * OCT + c] = octonion[r][c]
                    doubled[block * OCT + r][block * OCT + c] = octonion[r][c]
        _require(is_derivation(extended, HALF), "a diagonal extension is not a derivation of A_4")
        _require(is_derivation(doubled, DIM), "a diagonal extension is not a derivation of A_5")
        _require(
            all(extended[r][c] == -extended[c][r] for r in range(HALF) for c in range(HALF)),
            "a derivation is not skew-symmetric",
        )
        _require(all(extended[r][k] == 0 for r in range(HALF) for k in C4), "a derivation moves e_0 or e_8")
        out.append(tuple(tuple(row) for row in extended))
    return tuple(out)


def act(matrix: tuple[tuple[int, ...], ...], vector: Vector) -> Vector:
    return [sum((entry * value for entry, value in zip(row, vector, strict=True)), Fraction(0)) for row in matrix]


def i4_times(vector: Vector) -> Vector:
    return apply(left_rational(HALF, basis_vector(I4, HALF)), vector)


def entries(x: Vector) -> tuple[Vector, Vector]:
    """(a, b) with bracket(a, b) = x, from a + b = x' and b - a = -e_8 x''."""
    upper, lower = x[:HALF], i4_times(x[HALF:])
    a = [(p + q) / 2 for p, q in zip(upper, lower, strict=True)]
    b = [(p - q) / 2 for p, q in zip(upper, lower, strict=True)]
    _require(bracket(a, b) == x, "the bracket entries do not reproduce x")
    return a, b


def nullity16(v: Vector) -> int:
    return HALF - rank_p(left_rational(HALF, v))


def tangent_rows(left_kernel: list[Vector], right_kernel: list[Vector], dim: int) -> list[Vector]:
    """Rows of y -> U^T L_y V: entry y_i of row (u, v) is sum_r u_r sign(i, r ^ i) v_(r ^ i)."""
    signs = sign_table() if dim == DIM else tuple(tuple(cd_sign(dim, i, j) for j in range(dim)) for i in range(dim))
    us = [integer_vector(u) for u in left_kernel]
    vs = [integer_vector(v) for v in right_kernel]
    return [
        [Fraction(sum(u[r] * signs[i][r ^ i] * v[r ^ i] for r in range(dim) if u[r])) for i in range(dim)]
        for u in us
        for v in vs
    ]


def frames(x: Vector, dim: int) -> tuple[list[Vector], list[Vector]]:
    left = left_rational(dim, x)
    right_kernel = verified_kernel(left, dim)
    left_kernel = verified_kernel([list(column) for column in zip(*left, strict=True)], dim)
    return right_kernel, left_kernel


def zd_tangent(a: Vector) -> dict[str, int]:
    """T_Z(a) from automorphism velocities and scaling, against the Moreno kernel and the A_4 tangent bound."""
    curve = [act(d, a) for d in derivations()] + [a]
    curve_rank = rank_p(curve)
    grad_q1 = [2 * a[k] if k < OCT else -2 * a[k] for k in range(HALF)]
    grad_q2 = [a[k + OCT] if k < OCT else a[k - OCT] for k in range(HALF)]
    linear = [basis_vector(k, HALF) for k in C4]
    moreno = verified_kernel([*linear, grad_q1, grad_q2], HALF)
    right_kernel, left_kernel = frames(a, HALF)
    bound = verified_kernel(tangent_rows(left_kernel, right_kernel, HALF), HALF)
    _require(
        all(annihilated(integer_rows([*linear, grad_q1, grad_q2]), v) for v in curve), "D a leaves the Moreno kernel"
    )
    _require(
        all(annihilated(integer_rows(tangent_rows(left_kernel, right_kernel, HALF)), v) for v in curve),
        "D a leaves the A_4 tangent bound",
    )
    return {
        "curve_span": curve_rank,
        "moreno_kernel": len(moreno),
        "a4_tangent_bound": len(bound),
        "annihilator": len(right_kernel),
    }


def pair(alpha: Vector, beta: Vector) -> Vector:
    return [*alpha, *beta]


def matrix_product(left: list[Vector], right: list[Vector]) -> list[Vector]:
    columns = list(zip(*right, strict=True))
    return [[sum((p * q for p, q in zip(row, column, strict=True)), Fraction(0)) for column in columns] for row in left]


def shifted(matrix: list[Vector], value: Fraction) -> list[Vector]:
    return [[entry + (value if r == c else 0) for c, entry in enumerate(row)] for r, row in enumerate(matrix)]


def projector_equation(a: Vector, b: Vector) -> tuple[list[Vector], Vector]:
    """Jacobian rows of E(a, b) = (L_a^2 + n)(L_a^2 + 2n) b, n = |a|^2, and E at (a, b)."""
    left = left_rational(HALF, a)
    square = matrix_product(left, left)
    norm = dot(a, a)
    m1, m2 = shifted(square, norm), shifted(square, 2 * norm)
    m1m2 = matrix_product(m1, m2)
    # L_a^2 is symmetric, so L_a^2 (L_a^2 + n)(L_a^2 + 2n) = 0 makes m1m2 equal 2 n^2 times the Ann(a) projector.
    _require(
        not any(any(row) for row in matrix_product(square, m1m2)), "-L_a^2 / |a|^2 has an eigenvalue outside 0, 1, 2"
    )
    m2b, value = apply(m2, b), apply(m1m2, b)
    columns = []
    for k in range(HALF):
        direction = left_rational(HALF, basis_vector(k, HALF))
        symmetric = [
            [p + q for p, q in zip(r1, r2, strict=True)]
            for r1, r2 in zip(matrix_product(left, direction), matrix_product(direction, left), strict=True)
        ]
        d1 = apply(shifted(symmetric, 2 * a[k]), m2b)
        d2 = apply(m1, apply(shifted(symmetric, 4 * a[k]), b))
        columns.append([p + q for p, q in zip(d1, d2, strict=True)])
    columns += [[m1m2[r][k] for r in range(HALF)] for k in range(HALF)]
    return [list(row) for row in zip(*columns, strict=True)], value


def c_orthogonality_rows(a: Vector, b: Vector) -> list[Vector]:
    """Gradients of <a, b> and <b, e_8 a> in (a, b); L_(e_8) is skew, so grad_a <b, e_8 a> = -e_8 b."""
    return [pair(b, a), pair([-v for v in i4_times(b)], i4_times(a))]


def family_space(family: str, a: Vector, b: Vector) -> dict[str, Any]:
    """Curve velocities P and the defining-equation kernel J of the cone family at (a, b)."""
    zero = [Fraction(0)] * HALF
    c4perp = [basis_vector(k, HALF) for k in range(HALF) if k not in C4]
    linear = [pair(basis_vector(k, HALF), zero) for k in C4] + [pair(zero, basis_vector(k, HALF)) for k in C4]
    generators: dict[str, list[Vector]] = {}
    equations: list[Vector] = list(linear)
    values: list[Fraction] = [dot(row, pair(a, b)) for row in linear]
    zd_a = family.startswith("zd-")
    _require(nullity16(a) == (4 if zd_a else 0), f"a has nullity {nullity16(a)} in A_4")
    _require(not any(b) if family == "nonzd-axis" else nullity16(b) == 0, f"b has nullity {nullity16(b)} in A_4")
    if zd_a:
        grad_q1 = [2 * a[k] if k < OCT else -2 * a[k] for k in range(HALF)]
        grad_q2 = [a[k + OCT] if k < OCT else a[k - OCT] for k in range(HALF)]
        equations += [pair(grad_q1, zero), pair(grad_q2, zero)]
        values += [dot(a[:OCT], a[:OCT]) - dot(a[OCT:], a[OCT:]), dot(a[:OCT], a[OCT:])]
    if family == "nonzd-axis":
        generators["line_a"] = [pair(v, zero) for v in c4perp]
        equations += [pair(zero, basis_vector(k, HALF)) for k in range(HALF)]
        values += list(b)
    elif family == "zd-nonzd-generic":
        generators["automorphism"] = [pair(act(d, a), zero) for d in derivations()]
        generators["scale_a"] = [pair(a, zero)]
        generators["line_b"] = [pair(zero, v) for v in c4perp]
    elif family == "zd-nonzd-locus":
        _span, annihilator = frame_spaces(a)
        fiber = c_orthogonal_space(a, annihilator)
        generators["automorphism"] = [pair(act(d, a), act(d, b)) for d in derivations()]
        generators["scale_a"] = [pair(a, zero)]
        generators["line_b"] = [pair(zero, w) for w in fiber]
        equations += c_orthogonality_rows(a, b)
        values += [dot(a, b), dot(b, i4_times(a))]
        jacobian, value = projector_equation(a, b)
        equations += jacobian
        values += value
    elif family == "nonzd-nonzd-locus":
        frame = [a, i4_times(a)]
        fiber = verified_kernel([*[basis_vector(k, HALF) for k in C4], *frame], HALF)
        gram = [[dot(p, q) for q in frame] for p in frame]
        det = gram[0][0] * gram[1][1] - gram[0][1] * gram[1][0]
        _require(det != 0, "a and e_8 a are dependent")
        inverse = [[gram[1][1] / det, -gram[0][1] / det], [-gram[1][0] / det, gram[0][0] / det]]
        lifts = []
        for t in c4perp:
            pairing = [dot(t, b), dot(i4_times(t), b)]
            weights = [sum((inverse[r][c] * pairing[c] for c in range(2)), Fraction(0)) for r in range(2)]
            lifts.append(pair(t, [-(weights[0] * p + weights[1] * q) for p, q in zip(*frame, strict=True)]))
        generators["projection_lift"] = lifts
        generators["line_b"] = [pair(zero, w) for w in fiber]
        equations += c_orthogonality_rows(a, b)
        values += [dot(a, b), dot(b, i4_times(a))]
    else:
        _require(False, f"unknown family {family}")
    _require(not any(values), f"(a, b) violates the {family} equations")
    every = [vector for vectors in generators.values() for vector in vectors]
    span = rref(every)
    constraint = verified_kernel(equations, 2 * HALF)
    _require(
        all(annihilated(integer_rows(equations), vector) for vector in every),
        f"a {family} curve velocity leaves the defining-equation kernel",
    )
    return {
        "span": span,
        "generators": {name: len(vectors) for name, vectors in generators.items()},
        "constraint_kernel_dimension": len(constraint),
    }


def family_tangent(family: str, x: Vector) -> dict[str, Any]:
    """T_F = bracket(P) cap x^perp in canonical RREF form, with the parameter-space data."""
    a, b = entries(x)
    space = family_space(family, a, b)
    cone = [bracket(vector[:HALF], vector[HALF:]) for vector in space["span"]]
    _require(rank_p(cone) == len(cone), "the bracket is not injective on the family span")
    _require(flint.fmpq_mat(integer_rows([*cone, x])).rank() == len(cone), "x is outside the cone family tangent space")
    weights = verified_kernel([[dot(x, vector) for vector in cone]], len(cone))
    unit = [
        [sum((w * v[k] for w, v in zip(weight, cone, strict=True)), Fraction(0)) for k in range(DIM)]
        for weight in weights
    ]
    out = {
        "a": a,
        "b": b,
        "basis": rref(unit),
        "cone_dimension": len(cone),
        "generators": space["generators"],
        "constraint_kernel_dimension": space["constraint_kernel_dimension"],
        "zero_divisor_tangent": zd_tangent(a) if family.startswith("zd-") else None,
    }
    return out


def first_order_rows(x: Vector, right_kernel: list[Vector], left_kernel: list[Vector]) -> list[Vector]:
    return [*tangent_rows(left_kernel, right_kernel, DIM), x]


def complement(t1_rows: list[Vector], tf_basis: list[Vector]) -> tuple[list[Vector], int]:
    """C = T_1 cap T_F^perp; the basis with pi = identity when pi(C) has rank 2, else the RREF of C."""
    space = verified_kernel([*t1_rows, *tf_basis], DIM)
    projection = [[vector[k] for k in EXIT] for vector in space]
    rank = rank_p(projection)
    if rank < 2 or len(space) != 2:
        return rref(space), rank
    (p, q), (r, s) = projection
    det = p * s - q * r
    inverse = [[s / det, -q / det], [-r / det, p / det]]
    basis = [[inverse[row][0] * space[0][k] + inverse[row][1] * space[1][k] for k in range(DIM)] for row in range(2)]
    return basis, rank


def certify(row: dict[str, Any]) -> dict[str, Any]:
    x = row["x"]
    right_kernel, left_kernel = frames(x, DIM)
    t_rows = tangent_rows(left_kernel, right_kernel, DIM)
    t_basis = verified_kernel(t_rows, DIM)
    t1_rows = [*t_rows, x]
    t1_basis = verified_kernel(t1_rows, DIM)
    tangent = family_tangent(row["family"], x)
    h5perp = verified_kernel([*t1_rows, *(basis_vector(k) for k in H5)], DIM)
    comp, rank = complement(t1_rows, tangent["basis"])
    return {
        "witness": row["witness"],
        "family": row["family"],
        "x": encode(x),
        "a": encode(tangent["a"]),
        "b": encode(tangent["b"]),
        "nullity": len(right_kernel),
        "expected_nullity": row["nullity"],
        "family_dimension": row["dimension"],
        "kernel_frame": [encode(v) for v in right_kernel],
        "cokernel_frame": [encode(u) for u in left_kernel],
        "t_dimension": len(t_basis),
        "t1_dimension": len(t1_basis),
        "family_generators": tangent["generators"],
        "family_cone_dimension": tangent["cone_dimension"],
        "constraint_kernel_dimension": tangent["constraint_kernel_dimension"],
        "zero_divisor_tangent": tangent["zero_divisor_tangent"],
        "tf_dimension": len(tangent["basis"]),
        "tf_basis": [encode(v) for v in tangent["basis"]],
        "t1_h5perp_dimension": len(h5perp),
        "quotient_dimension": len(t1_basis) - len(tangent["basis"]),
        "complement_basis": [encode(v) for v in comp],
        "complement_h5_coordinates": [{f"e{k}": str(v[k]) for k in H5} for v in comp],
        "t1_projection_rank": rank_p([[v[k] for k in EXIT] for v in t1_basis]),
        "projection_rank": rank,
    }


def verify_row(row: dict[str, Any]) -> list[str]:
    """Every failure of a recorded row against x, its frames, the family builder and T_1; empty when sound."""
    failures: list[str] = []
    try:
        x = decode(row["x"])
        right_kernel = [decode(v) for v in row["kernel_frame"]]
        left_kernel = [decode(u) for u in row["cokernel_frame"]]
        tf_basis = [decode(v) for v in row["tf_basis"]]
        comp = [decode(v) for v in row["complement_basis"]]
    except (KeyError, ValueError, ZeroDivisionError) as error:
        return [f"unreadable row: {error}"]
    if len(x) != DIM or any(len(v) != DIM for v in [*right_kernel, *left_kernel, *tf_basis, *comp]):
        return ["a vector has the wrong length"]
    left = left_rational(DIM, x)
    left_integers = integer_rows(left)
    transpose_integers = integer_rows([list(column) for column in zip(*left, strict=True)])
    rank = rank_p(left)
    if not (
        all(annihilated(left_integers, v) for v in right_kernel)
        and all(annihilated(transpose_integers, u) for u in left_kernel)
        and rank_p(right_kernel) == len(right_kernel) == DIM - rank
        and rank_p(left_kernel) == len(left_kernel) == DIM - rank
    ):
        return ["kernel frame does not span ker L_x and ker L_x^T"]
    if not row["nullity"] == len(right_kernel) == row["expected_nullity"]:
        failures.append("nullity differs from the kernel frame or the family")
    t1_rows = first_order_rows(x, right_kernel, left_kernel)
    t1_integers = integer_rows(t1_rows)
    t1_dimension = DIM - rank_p(t1_rows)
    if not all(annihilated(t1_integers, v) for v in tf_basis):
        failures.append("a T_F basis vector leaves T_1")
    if any(v[k] for v in tf_basis for k in H5):
        failures.append("a T_F basis vector leaves H_5^perp")
    if len(tf_basis) != row["family_dimension"] or row["tf_dimension"] != len(tf_basis):
        failures.append("dim T_F differs from the family dimension")
    if tf_basis != family_tangent(row["family"], x)["basis"]:
        failures.append("T_F differs from the family tangent space the family builder constructs")
    if not all(annihilated(t1_integers, v) for v in comp) or any(dot(c, v) for c in comp for v in tf_basis):
        failures.append("a complement vector leaves T_1 cap T_F^perp")
    if rank_p([*tf_basis, *comp]) != len(tf_basis) + len(comp) or len(tf_basis) + len(comp) != t1_dimension:
        failures.append("T_F and the complement do not span T_1")
    if row["t1_dimension"] != t1_dimension or row["quotient_dimension"] != t1_dimension - len(tf_basis):
        failures.append("recorded dim T_1 differs from the first-order equations")
    projection = [[v[k] for k in EXIT] for v in comp]
    rank = rank_p(projection)
    if row["projection_rank"] != rank:
        failures.append("projection rank differs from the complement")
    if rank == 2 and projection != [[1, 0], [0, 1]]:
        failures.append("complement basis is not the pi-dual basis")
    if rank < 2 and comp != rref(verified_kernel([*t1_rows, *tf_basis], DIM)):
        failures.append("complement basis is not the RREF of T_1 cap T_F^perp")
    return failures


def run() -> dict[str, Any]:
    targets = [row for row in witnesses() if row["family"] in FAMILIES]
    derivations()
    rows = parallel.ordered_map(certify, targets, min_items=2)
    checks = parallel.ordered_map(verify_row, rows, min_items=2)
    violations = [
        row["witness"]
        for row, failures in zip(rows, checks, strict=True)
        if failures
        or row["family_cone_dimension"] != row["constraint_kernel_dimension"]
        or row["t1_h5perp_dimension"] != row["tf_dimension"]
        or row["t_dimension"] - 1 != row["t1_dimension"]
        or (
            row["zero_divisor_tangent"] is not None
            and row["zero_divisor_tangent"]
            != {
                "curve_span": ZD_TANGENT_DIMENSION,
                "moreno_kernel": ZD_TANGENT_DIMENSION,
                "a4_tangent_bound": ZD_TANGENT_DIMENSION,
                "annihilator": 4,
            }
        )
    ]
    return {
        "schema": SCHEMA,
        "witness_source": "scripts/rank_locus_local_dimension.py witnesses()",
        "families": list(FAMILIES),
        "projection": "pi(y) = (y_8, y_24); T_F lies in H_5^perp, so pi induces T_1(x)/T_F -> span{e_8, e_24}",
        "rows": rows,
        "violations": violations,
        "summary": summarize(rows),
    }


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        entry = out.setdefault(
            row["family"],
            {"family": row["family"], "nullity": row["nullity"], "witnesses": [], "values": set()},
        )
        entry["witnesses"].append(row["witness"])
        entry["values"].add(
            (row["t1_dimension"], row["tf_dimension"], row["t1_h5perp_dimension"], row["projection_rank"])
        )
    return [
        {
            "family": entry["family"],
            "nullity": entry["nullity"],
            "witnesses": entry["witnesses"],
            "t1_dimension": sorted({v[0] for v in entry["values"]}),
            "tf_dimension": sorted({v[1] for v in entry["values"]}),
            "t1_h5perp_dimension": sorted({v[2] for v in entry["values"]}),
            "projection_rank": sorted({v[3] for v in entry["values"]}),
        }
        for entry in out.values()
    ]


def _mutations(row: dict[str, Any]) -> list[tuple[str, str, dict[str, Any]]]:
    """(label, expected failure text, damaged row) for each corruption the verifier must reject."""
    x = decode(row["x"])
    right_kernel, left_kernel = [decode(v) for v in row["kernel_frame"]], [decode(u) for u in row["cokernel_frame"]]
    t1_integers = integer_rows(first_order_rows(x, right_kernel, left_kernel))
    outside = next(k for k in range(DIM) if k not in H5 and not annihilated(t1_integers, basis_vector(k)))
    damaged: list[tuple[str, str, dict[str, Any]]] = []

    def edit(label: str, expected: str, field: str, value: Any) -> None:
        copy_row = copy.deepcopy(row)
        copy_row[field] = value
        damaged.append((label, expected, copy_row))

    edit("nullity", "nullity differs", "nullity", row["nullity"] + 1)
    frame = [decode(v) for v in row["kernel_frame"]]
    frame[0][next(k for k in range(DIM) if frame[0][k])] += 1
    edit("kernel frame", "kernel frame", "kernel_frame", [encode(v) for v in frame])
    tf = [decode(v) for v in row["tf_basis"]]
    tf[0] = [value + int(k == EXIT[0]) for k, value in enumerate(tf[0])]
    edit("T_F basis vector", "leaves H_5^perp", "tf_basis", [encode(v) for v in tf])
    tf = [decode(v) for v in row["tf_basis"]]
    tf[-1] = [value + int(k == outside) for k, value in enumerate(tf[-1])]
    edit("T_F containment", "leaves T_1", "tf_basis", [encode(v) for v in tf])
    edit(
        "T_F replaced by a complement vector",
        "family tangent space",
        "tf_basis",
        [*row["tf_basis"][:-1], row["complement_basis"][0]],
    )
    comp = [decode(v) for v in row["complement_basis"]]
    comp[1] = [value + int(k == outside) for k, value in enumerate(comp[1])]
    edit("complement vector", "complement vector", "complement_basis", [encode(v) for v in comp])
    edit("T_1 dimension", "dim T_1", "t1_dimension", row["t1_dimension"] - 1)
    edit("projection rank", "projection rank", "projection_rank", row["projection_rank"] - 1)
    return damaged


def _reject(task: tuple[str, str, dict[str, Any]]) -> str:
    label, expected, damaged = task
    failures = verify_row(damaged)
    _require(any(expected in failure for failure in failures), f"verifier accepted a damaged row: {label} ({failures})")
    return label


def self_test() -> str:
    record = run()
    _require(not record["violations"], f"witnesses {record['violations']} fail before mutation")
    tasks = [task for row in record["rows"][: len(FAMILIES)] for task in _mutations(row)]
    labels = parallel.ordered_map(_reject, tasks, min_items=2)
    return f"rank_locus_gap_directions: self-test rejected {len(labels)} damaged rows across {len(FAMILIES)} families"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
        return 0
    record = run()
    text = json.dumps(record, indent=1) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    else:
        _require(args.check.read_text(encoding="utf-8") == text, "the retained file differs from the recomputed text")
    for entry in record["summary"]:
        print(json.dumps(entry))
    _require(not record["violations"], f"witnesses {record['violations']} fail their certificate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
