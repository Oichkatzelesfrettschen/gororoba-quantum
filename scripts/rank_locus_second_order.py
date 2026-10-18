"""Exact second-order compatibility of the first-order exit directions of the A_5 rank-locus gap.

At each witness x of the families nonzd-axis, zd-nonzd-locus, zd-nonzd-generic
and nonzd-nonzd-locus, scripts/rank_locus_gap_directions.py proves

    T_1(x) = T_F (+) span{e_8, e_24}   (orthogonal direct sum),

with T_F the family tangent space as an exact rational basis. This script
decides which velocities v = tau + s e_8 + t e_24 (tau in T_F) pass the
second-order test for staying in the rank locus, keeping every variable.

Schur reduction. V spans ker L_x and U spans ker L_x^T. Complements V_c and
U_c give the invertible pivot P = U_c^T L_x V_c and the generalized inverse
G = V_c P^-1 U_c^T, with L_x G L_x = L_x. In the basis (U_c, U) x (V_c, V)
the matrix L_(x+h) has blocks A = P + U_c^T L_h V_c, B = U_c^T L_h V,
C = U^T L_h V_c and D = U^T L_h V, because U^T L_x = 0 and L_x V = 0. So
rank L_(x+h) = rank A + rank S(h) with the Schur complement

    S(h) = D - C A^-1 B = U^T L_h V - U^T L_h G L_h V + U^T L_h G L_h G L_h V - ...

and, while A stays invertible, L_(x+h) has nullity k exactly when S(h) = 0.
On a curve h = eps v + eps^2 w + eps^3 u the coefficients vanish order by order:

    eps^1   Delta(v) = 0,  where Delta(y) = U^T L_y V            (v in T(x))
    eps^2   Delta(w) = U^T L_v G L_v V
    eps^3   Delta(u) = U^T L_v G L_w V + U^T L_w G L_v V - U^T L_v G L_v G L_v V

With N spanning the cokernel of Delta : R^32 -> R^(k x k), the order-2
equation is solvable in w exactly when Q(v) = N^T vec(U^T L_v G L_v V) = 0. For
v in T(x), U^T L_v = M L_x and L_v V = L_x M', so U^T L_v G L_v V = M L_x M'
and the target, hence Q, is independent of the complements. Every witness is
doubly pure (x_0 = x_16 = 0), so L_x is skew, U = V, and the targets are skew;
the residual keeps all k^2 entries and w ranges over all of R^32.

Tangent cone. A Bouligand tangent vector v is the limit of (y_n - x)/t_n with
y_n in the locus; writing y_n - x = t_n v + r_n with r_n = o(t_n) and projecting
S(y_n) = 0 onto the cokernel removes Delta(r_n), so N^T S(y_n) / t_n^2 -> -Q(v)
forces Q(v) = 0. Every tangent-cone vector therefore passes the order-2 test.

Recorded per witness, all in exact rational arithmetic:
  the cokernel dimension, pinned by rank modulo 2^61 - 1 and integer-checked
  vectors; the coefficient matrix of Q in the coordinates (tau, s, t) of the
  basis T_F, e_8, e_24 over the monomials z_i z_j (i <= j); its rank, the
  number of independent quadratic equations; explicit order-2 solutions (v, w)
  for v = e_8 and v = e_24; a sign check on an exact curve of the cone, an
  automorphism curve exp(eps D) x with w = D^2 x / 2 and u = D^3 x / 6 or else
  the rotation curve below, whose coefficients must satisfy the order-2 and
  order-3 equations with nonzero target and triple term; and the order-3
  cubic. When Q
  vanishes on T(x), its polarization vanishes on T(x) x T(x), so the order-3
  condition no longer depends on the choice of w and reads K3(v) = 0 for the
  cubic K3(v) = N^T vec(B(v, R(v)) - U^T L_v G L_v G L_v V), with R a fixed
  linear right inverse of Delta applied to the order-2 target and
  B(v, w) = U^T L_v G L_w V + U^T L_w G L_v V.

Transverse curves. For each half of x = (p, q) the rotation of that half
toward its e_8 is the polynomial curve Y(u) = x + u v + u^2 w with velocity v
on e_8 or e_24. Its nullity is decided exactly from the ranks at 2 (33 - k) + 1
integer nodes: every (33 - k)-minor of L_Y(u) has degree at most 2 (33 - k).
A curve that keeps nullity k is an actual curve of the cone through x with a
transverse velocity; it shows that e_8 or e_24 lies in the tangent cone and
raises no local dimension by itself.

A control at e1 + e18 runs the same construction on the tangent coordinates of
gororoba_quantum/nullity_twelve_locus.py and requires its row space to equal
that module's eight canonical quadrics, and that rescaling the frame vectors
by unequal multiples leaves the row space unchanged.

Outcome labels: "A" every real zero of Q has s = t = 0 (needs a certificate);
"B" a real zero with (s, t) != 0 is recorded and verified; "undecided"
otherwise. Order-2 and order-3 compatibility are formal statements about the
coefficients of a curve; they construct no curve and bound no local dimension.

Usage:
    "$PYTHON" scripts/rank_locus_second_order.py --out PATH
    "$PYTHON" scripts/rank_locus_second_order.py --check PATH
    "$PYTHON" scripts/rank_locus_second_order.py --self-test

--check recomputes every witness and the control and requires the retained
file to equal, byte for byte, the text --out writes. --self-test requires the
row verifier to reject a nonzero coefficient, a wrong coefficient rank, a
corrupted order-2 solution, a solution with s = t = 0, a wrong outcome label,
a corrupted kernel frame, a corrupted T_F vector, a wrong cokernel dimension, a
sign-flipped exact-curve acceleration, a corrupted order-3 curve coefficient, a nonzero
cubic coefficient and a flipped transverse-curve verdict.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import flint
import sympy as sp

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
import rank_locus_gap_directions as gap  # noqa: E402
from exact_rank import rational_kernel  # noqa: E402
from rank_locus_local_dimension import basis_vector, witnesses  # noqa: E402

import parallel  # noqa: E402
from nullity_twelve_locus import MONOMIAL_PAIRS, _canonical_quadrics  # noqa: E402
from skew_schur_charts import COORDINATE_INDICES  # noqa: E402

SCHEMA = "rank-locus-second-order-v1"
DIM = 32
HALF = 16
EXIT = gap.EXIT
FAMILIES = gap.FAMILIES
CONTROL_SUPPORT = (1, 18)
CONTROL_RANK = 8
Vector = list[Fraction]


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"rank_locus_second_order: {message}")


def to_flint(value: Fraction) -> flint.fmpq:
    return flint.fmpq(value.numerator, value.denominator)


def from_flint(value: flint.fmpq) -> Fraction:
    return Fraction(int(value.p), int(value.q))


def matrix(rows: list[Vector]) -> flint.fmpq_mat:
    return flint.fmpq_mat([[to_flint(value) for value in row] for row in rows])


def columns(vectors: list[Vector]) -> flint.fmpq_mat:
    return flint.fmpq_mat([[to_flint(vector[r]) for vector in vectors] for r in range(len(vectors[0]))])


def operator(v: Vector) -> flint.fmpq_mat:
    """L_v with (L_v)[r][c] = sign(r ^ c, c) v_(r ^ c), the cd_core product e_i e_c = sign(i, c) e_(i ^ c)."""
    signs = gap.sign_table()
    return flint.fmpq_mat([[signs[r ^ c][c] * to_flint(v[r ^ c]) for c in range(DIM)] for r in range(DIM)])


def flat(block: flint.fmpq_mat) -> list[flint.fmpq]:
    return [block[a, b] for a in range(block.nrows()) for b in range(block.ncols())]


def is_zero(block: flint.fmpq_mat) -> bool:
    return all(value == 0 for value in block.entries())


def pivots(rows: flint.fmpq_mat) -> list[int]:
    reduced, rank = rows.rref()
    return [next(c for c in range(reduced.ncols()) if reduced[r, c] != 0) for r in range(rank)]


def generalized_inverse(x: Vector, complement: str) -> tuple[flint.fmpq_mat, Fraction]:
    """G = V_c P^-1 U_c^T and det P, for coordinate complements or the image columns of L_x."""
    lx = operator(x)
    column_pivots = pivots(lx)
    if complement == "coordinate":
        row_pivots = pivots(lx.transpose())
        right = flint.fmpq_mat([[int(r == p) for p in column_pivots] for r in range(DIM)])
        left = flint.fmpq_mat([[int(r == p) for p in row_pivots] for r in range(DIM)])
    else:
        right = flint.fmpq_mat([[lx[r, p] for p in column_pivots] for r in range(DIM)])
        left = right
    pivot = left.transpose() * lx * right
    determinant = from_flint(pivot.det())
    _require(determinant != 0, "the Schur pivot is singular")
    inverse = right * pivot.inv() * left.transpose()
    _require(lx * inverse * lx == lx, "G is not a generalized inverse of L_x")
    return inverse, determinant


class Frame:
    """ker L_x, ker L_x^T, a generalized inverse and the cokernel of Delta at one center."""

    def __init__(self, x: Vector, right: list[Vector], left: list[Vector], complement: str) -> None:
        self.x = x
        self.k = len(right)
        self.v = columns(right)
        self.ut = columns(left).transpose()
        self.inverse, self.pivot_determinant = generalized_inverse(x, complement)
        # Delta's columns are vec(U^T L_(e_j) V) for the recorded frames; the cokernel acts on the same entries.
        images = [flat(self.ut * operator(basis_vector(j)) * self.v) for j in range(DIM)]
        self.delta_rows = [[from_flint(images[j][r]) for j in range(DIM)] for r in range(self.k**2)]
        cokernel = gap.verified_kernel([list(column) for column in zip(*self.delta_rows, strict=True)], self.k**2)
        self.cokernel_dimension = len(cokernel)
        self.cokernel = matrix(cokernel) if cokernel else flint.fmpq_mat(0, self.k**2)
        self.delta = matrix(self.delta_rows)
        self.delta_rank = self.k**2 - len(cokernel)

    def residual(self, v: Vector) -> flint.fmpq_mat:
        return self.ut * operator(v) * self.v

    def target(self, v: Vector) -> flint.fmpq_mat:
        lv = operator(v)
        return self.ut * lv * self.inverse * lv * self.v

    def order_three(self, v: Vector, w: Vector) -> flint.fmpq_mat:
        """B(v, w) - U^T L_v G L_v G L_v V, the order-3 right side Delta(u) must equal."""
        lv, lw = operator(v), operator(w)
        mixed = self.ut * lv * self.inverse * lw * self.v + self.ut * lw * self.inverse * lv * self.v
        return mixed - self.triple(v)

    def triple(self, v: Vector) -> flint.fmpq_mat:
        lv = operator(v)
        return self.ut * lv * self.inverse * lv * self.inverse * lv * self.v

    def project(self, block: flint.fmpq_mat) -> list[Fraction]:
        if not self.cokernel_dimension:
            return []
        values = self.cokernel * flint.fmpq_mat([[value] for value in flat(block)])
        return [from_flint(value) for value in values.entries()]

    def solve(self, targets: flint.fmpq_mat) -> flint.fmpq_mat:
        """Columns w with Delta(w) = target, supported on Delta's pivot columns; a fixed linear right inverse.

        The reduced form of [Delta | I] gives E with E Delta = rref(Delta). For a
        target in the image of Delta the rows of E target below the rank vanish,
        and w is E target placed on the pivot columns.
        """
        size = self.k**2
        augmented = flint.fmpq_mat(
            [
                [*(to_flint(entry) for entry in self.delta_rows[r]), *(int(r == c) for c in range(size))]
                for r in range(size)
            ]
        )
        reduced, _ = augmented.rref()
        pivot_columns = [
            c for c in (next((c for c in range(DIM) if reduced[r, c] != 0), DIM) for r in range(size)) if c < DIM
        ]
        rank = len(pivot_columns)
        _require(rank == self.delta_rank, "the reduced form of Delta disagrees with its cokernel")
        elimination = flint.fmpq_mat([[reduced[r, DIM + c] for c in range(size)] for r in range(size)])
        images = elimination * targets
        _require(
            all(images[r, c] == 0 for r in range(rank, size) for c in range(images.ncols())),
            "an order-2 target lies outside the image of Delta",
        )
        out = flint.fmpq_mat(DIM, targets.ncols())
        for r, column in enumerate(pivot_columns):
            for c in range(targets.ncols()):
                out[column, c] = images[r, c]
        return out

    def right_inverse(self, block: flint.fmpq_mat) -> Vector:
        solution = self.solve(flint.fmpq_mat([[value] for value in flat(block)]))
        return [from_flint(solution[r, 0]) for r in range(DIM)]


def quadratic_coefficients(frame: Frame, basis: list[Vector]) -> list[list[Fraction]]:
    """Coefficients of Q on the basis by polarization: z_i^2 from M_ii, z_i z_j from M_ij + M_ji."""
    n = len(basis)
    ops = [operator(b) for b in basis]
    lefts = [frame.ut * op for op in ops]
    rights = [frame.inverse * op * frame.v for op in ops]
    blocks = []
    for i in range(n):
        for j in range(i, n):
            block = lefts[i] * rights[j]
            blocks.append(block if i == j else block + lefts[j] * rights[i])
    _require(all(block.transpose() == -block for block in blocks), "an order-2 target is not skew")
    if not frame.cokernel_dimension:
        return []
    stacked = flint.fmpq_mat([[value for value in flat(block)] for block in blocks]).transpose()
    product = frame.cokernel * stacked
    return [[from_flint(product[r, c]) for c in range(product.ncols())] for r in range(product.nrows())]


def evaluated_coefficients(frame: Frame, basis: list[Vector]) -> list[list[Fraction]]:
    """The same coefficients from values of Q: Q(b_i) and Q(b_i + b_j) - Q(b_i) - Q(b_j)."""
    n = len(basis)
    singles = [frame.project(frame.target(b)) for b in basis]
    out: list[list[Fraction]] = []
    for i in range(n):
        for j in range(i, n):
            if i == j:
                out.append(singles[i])
            else:
                both = frame.project(frame.target([p + q for p, q in zip(basis[i], basis[j], strict=True)]))
                out.append([p - q - r for p, q, r in zip(both, singles[i], singles[j], strict=True)])
    return [list(row) for row in zip(*out, strict=True)] if out and out[0] else []


def cubic_coefficients(frame: Frame, basis: list[Vector]) -> tuple[int, int, list[list[str]]]:
    """Shape, rank and nonzero entries of K3 over the monomials z_a z_b z_c (a <= b <= c).

    N_g, the cokernel row g read as a k x k matrix, turns each term into a
    linear functional: N_g . (U^T L_m Z) = vec(L_m^T U N_g) . vec(Z) for a
    32 x k block Z, and N_g . (X G L_m V) = vec(N_g (G L_m V)^T) . vec(X) for a
    k x 32 block X. L_w is linear in w, so the blocks G L_w V and U^T L_w for
    the order-2 accelerations w come from those of the 32 unit vectors.
    """
    n, k, count = len(basis), frame.k, frame.cokernel_dimension
    ops = [operator(b) for b in basis]
    lefts = [frame.ut * op for op in ops]
    rights = [frame.inverse * op * frame.v for op in ops]
    pairs = [(i, j) for i in range(n) for j in range(i, n)]
    triples = [(a, b, c) for a in range(n) for b in range(a, n) for c in range(b, n)]
    if not count:
        return 0, len(triples), []
    gauges = [
        flint.fmpq_mat([[frame.cokernel[g, a * k + b] for b in range(k)] for a in range(k)]) for g in range(count)
    ]
    left_functionals = flint.fmpq_mat([flat(lefts[m].transpose() * gauge) for m in range(n) for gauge in gauges])
    right_functionals = flint.fmpq_mat([flat(gauge * rights[m].transpose()) for m in range(n) for gauge in gauges])
    targets = flint.fmpq_mat(
        [flat(lefts[i] * rights[j] if i == j else lefts[i] * rights[j] + lefts[j] * rights[i]) for i, j in pairs]
    ).transpose()
    accelerations = frame.solve(targets)
    units = [operator(basis_vector(j)) for j in range(DIM)]
    right_units = flint.fmpq_mat([flat(frame.inverse * unit * frame.v) for unit in units]).transpose()
    left_units = flint.fmpq_mat([flat(frame.ut * unit) for unit in units]).transpose()
    mixed = (left_functionals * right_units + right_functionals * left_units) * accelerations
    triple_blocks = flint.fmpq_mat([flat(frame.inverse * ops[b] * rights[c]) for b in range(n) for c in range(n)])
    cubed = left_functionals * triple_blocks.transpose()
    index = {triple: position for position, triple in enumerate(triples)}

    def monomial(*factors: int) -> int:
        low, middle, high = sorted(factors)
        return index[(low, middle, high)]

    coefficients = [[flint.fmpq(0)] * len(triples) for _ in range(count)]
    for m in range(n):
        for p, (i, j) in enumerate(pairs):
            column = monomial(m, i, j)
            for g in range(count):
                coefficients[g][column] += mixed[m * count + g, p]
    for a in range(n):
        for b in range(n):
            for c in range(n):
                column = monomial(a, b, c)
                for g in range(count):
                    coefficients[g][column] -= cubed[a * count + g, b * n + c]
    nonzero = [
        [str(g), str(c), str(from_flint(value))]
        for g, row in enumerate(coefficients)
        for c, value in enumerate(row)
        if value != 0
    ]
    return flint.fmpq_mat(coefficients).rank(), len(triples), nonzero


def automorphism_curve(x: Vector, index: int) -> tuple[Vector, Vector, Vector]:
    """Coefficients D x, D^2 x / 2 and D^3 x / 6 of exp(eps D) x for derivation index."""
    derivation = gap.derivations()[index]

    def apply(y: Vector) -> Vector:
        return [*gap.act(derivation, y[:HALF]), *gap.act(derivation, y[HALF:])]

    v = apply(x)
    square = apply(v)
    return v, [value / 2 for value in square], [value / 6 for value in apply(square)]


def rotation_curve(x: Vector, half: int = 0) -> tuple[Vector, Vector, Fraction]:
    """Velocity and u^2 coefficient of the rotation of one half of x = (p, q) toward e_8 of that half.

    half 0: Y(u) = (1 - m u^2) p + 2 m u e_8 + (1 + m u^2) q with m = |p|^2;
    half 1: Y(u) = (1 + m u^2) p + (1 - m u^2) q + 2 m u e_24 with m = |q|^2.
    Y(u) / (1 + m u^2) turns the half toward its e_8 through the rational
    parametrization of c^2 + m r^2 = 1, and Y(u) = x + u v + u^2 w exactly.
    """
    turned = range(half * HALF, (half + 1) * HALF)
    m = gap.dot(x[turned.start : turned.stop], x[turned.start : turned.stop])
    v = [2 * m * Fraction(int(k == EXIT[half])) for k in range(DIM)]
    w = [(-m if k in turned else m) * value for k, value in enumerate(x)]
    return v, w, m


def rotation_nodes(nullity: int) -> int:
    """A (33 - k)-minor of L_Y(u) has degree at most 2 (33 - k) in u; one more node than that pins it to zero."""
    return 2 * (DIM + 1 - nullity) + 1


def rotation_keeps_nullity(x: Vector, nullity: int, half: int = 0) -> bool:
    """Whether rank L_Y(u) <= 32 - k at every node u = 1 .. rotation_nodes(k).

    True makes every (33 - k)-minor of L_Y(u) vanish identically, so Y(u) has
    nullity at least k for every u, and exactly k near u = 0 where rank is
    32 - k. False exhibits a nonzero (33 - k)-minor, a polynomial with finitely
    many roots, so Y(u) has nullity below k for all but finitely many u.
    """
    v, w, _ = rotation_curve(x, half)
    for u in range(1, rotation_nodes(nullity) + 1):
        point = [p + u * q + u * u * r for p, q, r in zip(x, v, w, strict=True)]
        if operator(point).rank() > DIM - nullity:
            return False
    return True


def transverse_curves(x: Vector, nullity: int) -> list[dict[str, Any]]:
    """Both half rotations, with velocities on e_8 and e_24, and whether each stays in the rank locus."""
    out = []
    for half in (0, 1):
        v, _, m = rotation_curve(x, half)
        out.append(
            {
                "half": half,
                "m": str(m),
                "velocity": gap.encode(v),
                "nodes": rotation_nodes(nullity),
                "keeps_nullity": rotation_keeps_nullity(x, nullity, half),
            }
        )
    return out


def sign_check(x: Vector, frame: Frame) -> dict[str, Any]:
    """An exact curve of the cone through x that fixes the signs of the order-2 and order-3 equations.

    An automorphism curve exp(eps D) x preserves nullity because
    L_(g x) = g L_x g^-1 for an automorphism g. The first derivation serves
    whose order-2 target and triple term U^T L_v G L_v G L_v V are nonzero
    for the frame's complements, so a flipped sign of the target or of the
    triple term against B(v, w) fails there. Where no derivation qualifies the rotation curve serves,
    certified by rank at the interpolation nodes and by rank 32 - k at
    u = 0; it is exactly quadratic, so its order-3 equation reads
    B(v, w) = U^T L_v G L_v G L_v V with a nonzero triple term.
    """
    for index in range(len(gap.derivations())):
        v, w, jerk = automorphism_curve(x, index)
        if not (is_zero(frame.target(v)) or is_zero(frame.triple(v))):
            return {
                "curve": "automorphism",
                "derivation": index,
                "velocity": gap.encode(v),
                "acceleration": gap.encode(w),
                "jerk": gap.encode(jerk),
            }
    v, w, m = rotation_curve(x)
    _require(not is_zero(frame.target(v)), "the rotation curve has a zero order-2 target")
    _require(not is_zero(frame.triple(v)), "the rotation curve has a zero order-3 triple term")
    _require(rotation_keeps_nullity(x, frame.k), "the rotation curve leaves the rank locus")
    return {
        "curve": "rotation",
        "m": str(m),
        "nodes": rotation_nodes(frame.k),
        "velocity": gap.encode(v),
        "acceleration": gap.encode(w),
        "jerk": gap.encode([Fraction(0)] * DIM),
    }


def nonzero_entries(rows: list[list[Fraction]]) -> list[list[str]]:
    return [[str(r), str(c), str(value)] for r, row in enumerate(rows) for c, value in enumerate(row) if value]


def exact_rank(rows: list[list[Fraction]]) -> int:
    return matrix(rows).rank() if rows and rows[0] else 0


def certify(row: dict[str, Any]) -> dict[str, Any]:
    first = gap.certify(row)
    x = gap.decode(first["x"])
    right = [gap.decode(v) for v in first["kernel_frame"]]
    left = [gap.decode(u) for u in first["cokernel_frame"]]
    tf_basis = [gap.decode(v) for v in first["tf_basis"]]
    basis = [*tf_basis, basis_vector(EXIT[0]), basis_vector(EXIT[1])]
    frame = Frame(x, right, left, "coordinate")
    coefficients = quadratic_coefficients(frame, basis)
    rank = exact_rank(coefficients)
    solutions = []
    for index in EXIT:
        v = basis_vector(index)
        solutions.append(
            {
                "velocity": gap.encode(v),
                "s": str(v[EXIT[0]]),
                "t": str(v[EXIT[1]]),
                "acceleration": gap.encode(frame.right_inverse(frame.target(v))),
            }
        )
    cubic_rank, cubic_monomials, cubic_nonzero = cubic_coefficients(frame, basis) if rank == 0 else (None, 0, [])
    n = len(basis)
    return {
        "witness": first["witness"],
        "family": first["family"],
        "x": first["x"],
        "nullity": first["nullity"],
        "family_dimension": first["family_dimension"],
        "kernel_frame": first["kernel_frame"],
        "cokernel_frame": first["cokernel_frame"],
        "doubly_pure_skew": not x[0] and not x[HALF] and right == left,
        "t1_dimension": first["t1_dimension"],
        "tf_basis": first["tf_basis"],
        "variables": "tau_0 .. tau_(d-1) on tf_basis, then s on e_8 and t on e_24",
        "pivot_determinant": str(frame.pivot_determinant),
        "residual_entries": frame.k**2,
        "delta_rank": frame.delta_rank,
        "cokernel_dimension": frame.cokernel_dimension,
        "coefficient_shape": [frame.cokernel_dimension, n * (n + 1) // 2],
        "coefficient_nonzero": nonzero_entries(coefficients),
        "coefficient_rank": rank,
        "independent_quadratic_equations": rank,
        "zero_set": "T_1" if rank == 0 else "proper",
        "outcome": "B" if rank == 0 else "undecided",
        "solutions": solutions,
        "sign_check": sign_check(x, frame),
        "transverse_curves": transverse_curves(x, frame.k),
        "cubic_shape": [frame.cokernel_dimension, cubic_monomials],
        "cubic_nonzero": cubic_nonzero,
        "cubic_rank": cubic_rank,
    }


def verify_row(row: dict[str, Any]) -> list[str]:
    """Every failure of a recorded row, recomputed through image-column complements and values of Q."""
    failures: list[str] = []
    try:
        x = gap.decode(row["x"])
        right = [gap.decode(v) for v in row["kernel_frame"]]
        left = [gap.decode(u) for u in row["cokernel_frame"]]
        tf_basis = [gap.decode(v) for v in row["tf_basis"]]
        solutions = [(gap.decode(s["velocity"]), gap.decode(s["acceleration"]), s) for s in row["solutions"]]
        flow = row["sign_check"]
        flow_v, flow_w = gap.decode(flow["velocity"]), gap.decode(flow["acceleration"])
        flow_jerk = gap.decode(flow["jerk"])
    except (KeyError, ValueError, ZeroDivisionError) as error:
        return [f"unreadable row: {error}"]
    vectors = [
        x,
        *right,
        *left,
        *tf_basis,
        flow_v,
        flow_w,
        flow_jerk,
        *(v for v, _, _ in solutions),
        *(w for _, w, _ in solutions),
    ]
    if any(len(v) != DIM for v in vectors):
        return ["a vector has the wrong length"]
    lx = gap.left_rational(DIM, x)
    rank = gap.rank_p(lx)
    if not (
        all(gap.annihilated(gap.integer_rows(lx), v) for v in right)
        and all(gap.annihilated(gap.integer_rows([list(c) for c in zip(*lx, strict=True)]), u) for u in left)
        and gap.rank_p(right) == len(right) == DIM - rank
        and gap.rank_p(left) == len(left) == DIM - rank
    ):
        return ["kernel frame does not span ker L_x and ker L_x^T"]
    if row["nullity"] != len(right):
        failures.append("nullity differs from the kernel frame")
    if row["doubly_pure_skew"] != (not x[0] and not x[HALF] and right == left) or not row["doubly_pure_skew"]:
        failures.append("the doubly pure skew structure differs from x and its frames")
    t1_rows = gap.first_order_rows(x, right, left)
    t1_integers = gap.integer_rows(t1_rows)
    t1_dimension = DIM - gap.rank_p(t1_rows)
    basis = [*tf_basis, basis_vector(EXIT[0]), basis_vector(EXIT[1])]
    if tf_basis != gap.family_tangent(row["family"], x)["basis"] or len(tf_basis) != row["family_dimension"]:
        failures.append("T_F differs from the family tangent space the family builder constructs")
    if not (
        all(gap.annihilated(t1_integers, v) for v in basis)
        and gap.rank_p(basis) == len(basis) == t1_dimension == row["t1_dimension"]
    ):
        failures.append("T_F, e_8 and e_24 do not form a basis of T_1")
    frame = Frame(x, right, left, "image")
    if (
        row["cokernel_dimension"] != frame.cokernel_dimension
        or row["delta_rank"] != frame.delta_rank
        or row["residual_entries"] != frame.k**2
    ):
        failures.append("cokernel dimension differs from Delta")
    coefficients = evaluated_coefficients(frame, basis)
    n = len(basis)
    if (
        row["coefficient_shape"] != [frame.cokernel_dimension, n * (n + 1) // 2]
        or row["coefficient_nonzero"] != nonzero_entries(coefficients)
        or row["coefficient_rank"] != exact_rank(coefficients)
        or row["independent_quadratic_equations"] != row["coefficient_rank"]
    ):
        failures.append("coefficient matrix differs from the values of Q")
    transverse = False
    for v, w, record in solutions:
        target = frame.target(v)
        if not (
            gap.annihilated(t1_integers, v)
            and frame.residual(w) == target
            and record["s"] == str(v[EXIT[0]])
            and record["t"] == str(v[EXIT[1]])
        ):
            failures.append("an order-2 solution fails Delta(w) = U^T L_v G L_v V")
        if v[EXIT[0]] or v[EXIT[1]]:
            transverse = True
    if not transverse:
        failures.append("no recorded solution is transverse, (s, t) = 0")
    expected_outcome = "B" if row["coefficient_rank"] == 0 and transverse else "undecided"
    if row["outcome"] != expected_outcome or row["zero_set"] != ("T_1" if row["coefficient_rank"] == 0 else "proper"):
        failures.append("outcome label differs from the coefficient rank and the solutions")
    if flow["curve"] == "automorphism":
        expected_v, expected_w, expected_jerk = automorphism_curve(x, flow["derivation"])
        on_curve = True
    else:
        expected_v, expected_w, m = rotation_curve(x)
        expected_jerk = [Fraction(0)] * DIM
        on_curve = (
            flow["curve"] == "rotation"
            and flow["m"] == str(m)
            and flow["nodes"] == rotation_nodes(len(right))
            and rotation_keeps_nullity(x, len(right))
        )
    flow_target = frame.target(flow_v)
    # B(v, w) and the triple term depend on the complements separately and only their difference is intrinsic;
    # the triple term is nonzero for the coordinate complements the cubic of certify uses.
    coordinate = Frame(x, right, left, "coordinate")
    if not (
        on_curve
        and flow_v == expected_v
        and flow_w == expected_w
        and gap.annihilated(t1_integers, flow_v)
        and not is_zero(flow_target)
        and frame.residual(flow_w) == flow_target
    ):
        failures.append("sign check: the exact curve fails Delta(w) = +U^T L_v G L_v V")
    elif not (
        flow_jerk == expected_jerk
        and not is_zero(coordinate.triple(flow_v))
        and coordinate.residual(flow_jerk) == coordinate.order_three(flow_v, flow_w)
        and frame.residual(flow_jerk) == frame.order_three(flow_v, flow_w)
    ):
        failures.append("order-3 sign check: the exact curve fails Delta(u) = B(v, w) - U^T L_v G L_v G L_v V")
    if row["transverse_curves"] != transverse_curves(x, len(right)):
        failures.append("transverse rotation curves differ from the node ranks")
    # The order-3 recomputation is the costly step; it runs on a row that passes every other check.
    if not failures and row["coefficient_rank"] == 0:
        cubic_rank, monomials, nonzero = cubic_coefficients(frame, basis)
        if (
            row["cubic_rank"] != cubic_rank
            or row["cubic_nonzero"] != nonzero
            or row["cubic_shape"] != [frame.cokernel_dimension, monomials]
        ):
            failures.append("cubic coefficients differ from the order-3 recomputation")
    return failures


def control() -> dict[str, Any]:
    """The construction at e1 + e18 against the eight canonical quadrics of nullity_twelve_locus."""
    x = [Fraction(int(k in CONTROL_SUPPORT)) for k in range(DIM)]
    right, left = gap.frames(x, DIM)
    k = len(right)
    upper = [(r, c) for r in range(k) for c in range(r + 1, k)]
    derivative = [[Fraction(0)] * len(COORDINATE_INDICES) for _ in upper]
    for position, coordinate in enumerate(COORDINATE_INDICES):
        block = columns(right).transpose() * operator(basis_vector(coordinate)) * columns(right)
        for row_index, (a, b) in enumerate(upper):
            derivative[row_index][position] = from_flint(block[a, b])
    radial = [x[coordinate] for coordinate in COORDINATE_INDICES]
    tangent = rational_kernel(gap.integer_rows([*derivative, radial]))
    ambient = []
    for vector in tangent:
        full = [Fraction(0)] * DIM
        for position, coordinate in enumerate(COORDINATE_INDICES):
            full[coordinate] = vector[position]
        ambient.append(full)
    frame = Frame(x, right, left, "coordinate")
    coefficients = quadratic_coefficients(frame, ambient)
    n = len(ambient)
    pairs = [(i, j) for i in range(n) for j in range(i, n)]
    reordered = [[row[pairs.index(pair)] for pair in MONOMIAL_PAIRS] for row in coefficients]
    variables = tuple(sp.Symbol(f"z{index}", real=True) for index in range(n))
    canonical = []
    for polynomial in _canonical_quadrics(variables):
        poly = sp.Poly(polynomial, *variables)
        canonical.append([Fraction(str(poly.coeff_monomial(variables[i] * variables[j]))) for i, j in MONOMIAL_PAIRS])
    rank = exact_rank(reordered)
    agrees = rank == CONTROL_RANK == exact_rank(canonical) and gap.rref(reordered) == gap.rref(canonical)
    # Unequal multiples of the frame vectors scale Delta's rows unevenly; the cokernel coordinates follow them.
    rescaled = Frame(
        x,
        [[Fraction(i + 2) * value for value in v] for i, v in enumerate(right)],
        [[Fraction(i + 2) * value for value in u] for i, u in enumerate(left)],
        "coordinate",
    )
    moved = [[row[pairs.index(pair)] for pair in MONOMIAL_PAIRS] for row in quadratic_coefficients(rescaled, ambient)]
    return {
        "center": "e1 + e18",
        "nullity": k,
        "t1_dimension": n,
        "cokernel_dimension": frame.cokernel_dimension,
        "coefficient_rank": rank,
        "row_space_equals_canonical_quadrics": agrees,
        "rescaled_frames_agree": exact_rank(moved) == rank and gap.rref(moved) == gap.rref(reordered),
    }


def _task(item: dict[str, Any] | None) -> dict[str, Any]:
    return control() if item is None else certify(item)


def run() -> dict[str, Any]:
    targets: list[dict[str, Any] | None] = [row for row in witnesses() if row["family"] in FAMILIES]
    gap.derivations()
    results = parallel.ordered_map(_task, [None, *targets], min_items=2)
    reference, rows = results[0], results[1:]
    checks = parallel.ordered_map(verify_row, rows, min_items=2)
    violations = [row["witness"] for row, failures in zip(rows, checks, strict=True) if failures]
    return {
        "schema": SCHEMA,
        "witness_source": "scripts/rank_locus_local_dimension.py witnesses()",
        "first_order_source": "scripts/rank_locus_gap_directions.py certify()",
        "condition": "N^T vec(U^T L_v G L_v V) = 0, G = V_c P^-1 U_c^T, N spanning coker(w -> U^T L_w V)",
        "control": reference,
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
            (
                row["t1_dimension"],
                row["cokernel_dimension"],
                row["coefficient_rank"],
                row["cubic_rank"],
                row["outcome"],
            )
        )
    return [
        {
            "family": entry["family"],
            "nullity": entry["nullity"],
            "witnesses": entry["witnesses"],
            "t1_dimension": sorted({v[0] for v in entry["values"]}),
            "cokernel_dimension": sorted({v[1] for v in entry["values"]}),
            "independent_quadratic_equations": sorted({v[2] for v in entry["values"]}),
            "cubic_rank": sorted({-1 if v[3] is None else v[3] for v in entry["values"]}),
            "outcome": sorted({v[4] for v in entry["values"]}),
        }
        for entry in out.values()
    ]


def _mutations(row: dict[str, Any]) -> list[tuple[str, str, dict[str, Any]]]:
    """(label, expected failure text, damaged row) for each corruption the verifier must reject."""
    damaged: list[tuple[str, str, dict[str, Any]]] = []

    def edit(label: str, expected: str, change: Any) -> None:
        copy_row = copy.deepcopy(row)
        change(copy_row)
        damaged.append((label, expected, copy_row))

    x = gap.decode(row["x"])
    right, left = [gap.decode(v) for v in row["kernel_frame"]], [gap.decode(u) for u in row["cokernel_frame"]]
    delta_rows = gap.tangent_rows(left, right, DIM)
    moving = next(k for k in range(DIM) if any(r[k] for r in delta_rows))

    def bump(text: str, index: int) -> str:
        vector = gap.decode(text)
        vector[index] += 1
        return gap.encode(vector)

    edit("coefficient entry", "coefficient matrix", lambda r: r.__setitem__("coefficient_nonzero", [["0", "0", "1"]]))
    edit("coefficient rank", "coefficient matrix", lambda r: r.__setitem__("coefficient_rank", 1))
    edit(
        "order-2 acceleration",
        "order-2 solution",
        lambda r: r["solutions"][0].__setitem__("acceleration", bump(r["solutions"][0]["acceleration"], moving)),
    )

    def family_only(r: dict[str, Any]) -> None:
        for solution in r["solutions"]:
            solution["velocity"], solution["s"], solution["t"] = r["tf_basis"][0], "0", "0"

    edit("solution with s = t = 0", "transverse", family_only)
    edit("outcome label", "outcome label", lambda r: r.__setitem__("outcome", "A"))
    frame = [gap.decode(v) for v in row["kernel_frame"]]
    frame[0][next(k for k in range(DIM) if frame[0][k])] += 1
    edit("kernel frame", "kernel frame", lambda r: r.__setitem__("kernel_frame", [gap.encode(v) for v in frame]))
    t1_integers = gap.integer_rows(gap.first_order_rows(x, right, left))
    outside = next(k for k in range(DIM) if k not in gap.H5 and not gap.annihilated(t1_integers, basis_vector(k)))
    edit("T_F vector", "T_F", lambda r: r["tf_basis"].__setitem__(-1, bump(r["tf_basis"][-1], outside)))
    edit(
        "cokernel dimension",
        "cokernel dimension",
        lambda r: r.__setitem__("cokernel_dimension", r["cokernel_dimension"] + 1),
    )
    edit(
        "sign-flipped exact-curve acceleration",
        "sign check",
        lambda r: r["sign_check"].__setitem__(
            "acceleration", gap.encode([-value for value in gap.decode(r["sign_check"]["acceleration"])])
        ),
    )

    edit(
        "order-3 curve coefficient",
        "order-3 sign check",
        lambda r: r["sign_check"].__setitem__("jerk", bump(r["sign_check"]["jerk"], moving)),
    )
    edit("cubic coefficient", "cubic coefficients", lambda r: r.__setitem__("cubic_nonzero", [["0", "0", "1"]]))
    edit(
        "transverse-curve verdict",
        "transverse rotation curves",
        lambda r: r["transverse_curves"][0].__setitem__(
            "keeps_nullity", not r["transverse_curves"][0]["keeps_nullity"]
        ),
    )
    return damaged


def _reject(task: tuple[str, str, dict[str, Any]]) -> str:
    label, expected, damaged = task
    failures = verify_row(damaged)
    _require(any(expected in failure for failure in failures), f"verifier accepted a damaged row: {label} ({failures})")
    return label


def self_test() -> str:
    """Mutate the first witness of each family; --check covers the other frames."""
    targets: list[dict[str, Any] | None] = []
    for family in FAMILIES:
        targets.append(next(row for row in witnesses() if row["family"] == family))
    gap.derivations()
    results = parallel.ordered_map(_task, [None, *targets], min_items=2)
    _require(
        results[0]["row_space_equals_canonical_quadrics"] and results[0]["rescaled_frames_agree"],
        "the e1 + e18 control differs",
    )
    rows = results[1:]
    checks = parallel.ordered_map(verify_row, rows, min_items=2)
    _require(not any(checks), f"a witness fails before mutation: {checks}")
    tasks = [task for row in rows for task in _mutations(row)]
    labels = parallel.ordered_map(_reject, tasks, min_items=2)
    return f"rank_locus_second_order: self-test rejected {len(labels)} damaged rows across {len(FAMILIES)} families"


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
    print(json.dumps(record["control"]))
    for entry in record["summary"]:
        print(json.dumps(entry))
    _require(not record["violations"], f"witnesses {record['violations']} fail their certificate")
    _require(
        record["control"]["row_space_equals_canonical_quadrics"] and record["control"]["rescaled_frames_agree"],
        "the e1 + e18 control differs",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
