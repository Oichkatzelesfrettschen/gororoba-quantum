"""Exact certificates for the compression pencils of the A_5 nullity-transition record, beyond its sympy reach.

Claim. (1) At y = e_1 + e_10 in A_n, n = 4 to 8, the kernel of L_y has dimension 2^(n-2), the compression pencil
dimension 2^(n-2) - 1, its commutant is a quaternion algebra and its Lie closure is sp(2^(n-4)), of dimension
k (2 k + 1) with k = 2^(n-4). (2) At the N- and N+ points e_3 + e_20 +- (e_12 - e_27) the Pfaffian of the
compression pencil, restricted to the doubly pure coordinate units, is a constant times |lead Q|^2 |lead G|^2,
with Q of order 1 and G of order 3 on the lines along those units. (3) In A_4 the left multiplication by the
doubling unit e_8 anticommutes with every other imaginary unit and squares to -I, so every sedenion zero divisor
is doubly pure, its kernel is invariant under L_(e_8), and ker L_p n ker L_q has even dimension 0, 2 or 4.

Arithmetic. Dimensions of kernels and pencils are exact integer ranks (python-flint fmpz_mat). The commutant and
the Lie closure are bounded on both sides: a rank modulo the prime P never exceeds the rational rank, so the
nullity mod P of the commutation system bounds the commutant above and the mod-P span of brackets bounds the
closure below; commutant elements reconstructed from P and checked exactly over Q bound the commutant below, and
the closure lies in the operators that are skew for the frame's Gram form and commute with those elements, whose
dimension mod P bounds it above. The Pfaffian is expanded in a multivariate integer polynomial ring (fmpz_mpoly)
and compared exactly; an implementation that shares no code with cd_core or that expansion repeats the comparison as
a determinant identity at integer points over all 30 doubly pure units. NumPy int64 holds residues mod P
(P < 2^15) and integer frames, forms and Gram matrices whose largest entry the script requires below 2^20, so every
product and sum stays below 2^50. No random draw enters; the generic pencil elements use fixed integer weights.

The replay commands are in docs/evidence/a5-nullity-transitions/README.md ("Replay").
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp
from flint import fmpq, fmpq_mat, fmpz_mat, fmpz_mpoly_ctx, nmod_mat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import cd_core  # noqa: E402
import parallel  # noqa: E402

P = 32749
SOURCE_FILES = (
    "gororoba_quantum/cd_core.py",
    "gororoba_quantum/parallel.py",
    "scripts/a5_pencil_certificates.py",
    "scripts/a5_zero_divisor_strata.py",
)
"""a5_zero_divisor_strata.py defines Q and G, whose leading forms the Pfaffian items read."""
Vector = tuple[tuple[int, int], ...]
BASE: Vector = ((1, 1), (10, 1))
TOWER_LEVELS = (16, 32, 64, 128, 256)
CALIBRATION: dict[str, Vector] = {
    "R e1+e10+e3+e20": ((1, 1), (10, 1), (3, 1), (20, 1)),
    "C e1+e10+2(e20+e31)": ((1, 1), (10, 1), (20, 2), (31, 2)),
}
STRATA: dict[str, Vector] = {
    "VB": ((3, 1), (20, 1)),
    "N-": ((3, 1), (20, 1), (12, 1), (27, -1)),
    "N+": ((3, 1), (20, 1), (12, -1), (27, 1)),
}
CENSUS_STRIDE = 97
CENSUS_CHUNKS = 64
PREDICTIONS = {
    "P20": "at e1 + e10 in A_7 the kernel has dimension 32, meeting each half in 16, the pencil dimension 31, the "
    "commutant is a quaternion algebra and the Lie closure has dimension 136",
    "P21": "at e1 + e10 in A_8 the kernel has dimension 64, meeting each half in 32, the pencil dimension 63, the "
    "commutant is a quaternion algebra and the Lie closure has dimension 528",
    "P22": "the type-R point e1 + e10 + e3 + e20 of A_5 reads commutant 1 and Lie closure 28",
    "P23": "at N- and N+, restricted to the doubly pure coordinates, the Pfaffian of the pencil is a nonzero "
    "constant times |lead Q|^2 |lead G|^2, with 2 (ord Q + ord G) = 8",
    "P24": "for sedenion zero divisors p, q the dimension of ker L_p n ker L_q is 0, 2 or 4, never 1 or 3",
    "P25": "on every W8 point (p, q) of the census the pencil type follows dim (ker L_p n ker L_q)",
    "P26": "an implementation sharing no code with cd_core or the polynomial-ring expansion finds, at N- and N+ over "
    "all 30 doubly pure imaginary units and 60 integer points, det of the pencil equal to a constant times "
    "(|lead Q|^2 |lead G|^2)^2, with the normalized constant 4 of the 18-unit identity",
}
ENTRY_BOUND = 2**20
DETERMINANT_POINTS = 60
NOT_RUN = {"P25"}
"""P25 was written before the runs; the census classifies no W8 point, so it stays open."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sign_table(dimension: int) -> list[list[int]]:
    return [[cd_core.cd_sign(dimension, p, q) for q in range(dimension)] for p in range(dimension)]


def left(dimension: int, table: list[list[int]], vector: dict[int, int]) -> np.ndarray:
    """L_y: column q holds the coefficient of e_k times the sign of e_k e_q in row k XOR q."""
    matrix = np.zeros((dimension, dimension), dtype=np.int64)
    for index, value in vector.items():
        for column in range(dimension):
            matrix[index ^ column, column] += value * table[index][column]
    return matrix


def doubled(a: list[int], b: list[int]) -> list[int]:
    """(a, b)(c, d) = (ac - conj(d) b, da + b conj(c)), an implementation independent of cd_core."""
    if len(a) == 1:
        return [a[0] * b[0]]
    half = len(a) // 2

    def conj(v: list[int]) -> list[int]:
        return [v[0], *(-x for x in v[1:])]

    a1, a2, c, d = a[:half], a[half:], b[:half], b[half:]
    first = [x - y for x, y in zip(doubled(a1, c), doubled(conj(d), a2), strict=True)]
    second = [x + y for x, y in zip(doubled(d, a1), doubled(a2, conj(c)), strict=True)]
    return first + second


def basis_product(dimension: int, p: int, q: int) -> tuple[int, int]:
    """(sign, index) of e_p e_q from (a, b)(c, d) = (ac - conj(d) b, da + b conj(c)) on basis vectors."""
    if dimension == 1:
        return 1, 0
    half = dimension // 2
    if p < half and q < half:
        return basis_product(half, p, q)
    if p < half:
        sign, index = basis_product(half, q - half, p)
        return sign, index + half
    if q < half:
        sign, index = basis_product(half, p - half, q)
        return (sign if q == 0 else -sign), index + half
    sign, index = basis_product(half, q - half, p - half)
    return (-sign if q == half else sign), index


def table_mismatches(dimension: int, table: list[list[int]]) -> int:
    """Every basis product e_p e_q against basis_product, and the vector doubling formula for every q and p in a
    stride of the indices (all p up to dimension 16)."""
    bad = sum(
        basis_product(dimension, p, q) != (table[p][q], p ^ q) for p in range(dimension) for q in range(dimension)
    )
    for p in range(0, dimension, max(1, dimension // 16)):
        for q in range(dimension):
            a, b = [0] * dimension, [0] * dimension
            a[p], b[q] = 1, 1
            want = [0] * dimension
            want[p ^ q] = table[p][q]
            bad += doubled(a, b) != want
    return bad


def to_int(matrix: np.ndarray) -> list[list[int]]:
    return [[int(x) for x in row] for row in matrix]


def nmod(matrix: np.ndarray) -> nmod_mat:
    rows, cols = matrix.shape
    return nmod_mat(rows, cols, [int(x) for x in (matrix % P).ravel()], P)


def nullity_mod_p(matrix: np.ndarray) -> int:
    return int(matrix.shape[1] - nmod(matrix).rank())


def rref_mod_p(matrix: np.ndarray) -> np.ndarray:
    reduced, rank = nmod(matrix).rref()
    cols = matrix.shape[1]
    return np.array([[int(reduced[i, j]) for j in range(cols)] for i in range(rank)], dtype=np.int64).reshape(
        rank, cols
    )


def nullspace_mod_p(matrix: np.ndarray) -> np.ndarray:
    space, nullity = nmod(matrix).nullspace()
    cols = matrix.shape[1]
    basis = np.array([[int(space[i, j]) for j in range(nullity)] for i in range(cols)], dtype=np.int64)
    return rref_mod_p(basis.T.reshape(nullity, cols)) if nullity else np.zeros((0, cols), dtype=np.int64)


def reconstruct(value: int) -> Fraction | None:
    """Rational reconstruction of a residue mod P with numerator and denominator below sqrt(P / 2)."""
    bound = int((P // 2) ** 0.5)
    r0, r1, s0, s1 = P, value % P, 0, 1
    while r1 > bound:
        quotient = r0 // r1
        r0, r1 = r1, r0 - quotient * r1
        s0, s1 = s1, s0 - quotient * s1
    if s1 == 0 or abs(s1) > bound:
        return None
    return Fraction(r1, s1)


def residue(value: Any) -> int:
    exact = fmpq(value)
    return int(exact.p) * pow(int(exact.q), -1, P) % P


def commutation_system(generators: list[np.ndarray], size: int) -> np.ndarray:
    """Rows of X M - M X = 0 on vec(X), row-major: vec(X M) = (I kron M^T) vec X, vec(M X) = (M kron I) vec X."""
    identity = np.eye(size, dtype=np.int64)
    return np.vstack([(np.kron(identity, g.T) - np.kron(g, identity)) % P for g in generators])


def skew_system(gram: np.ndarray) -> np.ndarray:
    """Rows of X^T G + G X = 0 on vec(X), row-major."""
    size = gram.shape[0]
    rows = np.zeros((size * size, size * size), dtype=np.int64)
    for i in range(size):
        for j in range(size):
            for m in range(size):
                rows[i * size + j, m * size + i] += gram[m, j]
                rows[i * size + j, m * size + j] += gram[i, m]
    return rows % P


class Echelon:
    """Reduced row echelon basis mod P, extended batch by batch."""

    def __init__(self, width: int) -> None:
        self.rows = np.zeros((0, width), dtype=np.int64)
        self.pivots: list[int] = []

    def add(self, batch: np.ndarray) -> list[np.ndarray]:
        batch = batch % P
        if self.pivots:
            batch = (batch - (batch[:, self.pivots] @ self.rows) % P) % P
        batch = batch[np.any(batch != 0, axis=1)]
        if batch.shape[0] == 0:
            return []
        new = rref_mod_p(batch)
        new_pivots = [int(np.nonzero(row)[0][0]) for row in new]
        if self.pivots:
            self.rows = (self.rows - (self.rows[:, new_pivots] @ new) % P) % P
        self.rows = np.vstack([self.rows, new])
        self.pivots += new_pivots
        order = np.argsort(self.pivots)
        self.rows = self.rows[order]
        self.pivots = [self.pivots[i] for i in order]
        return list(new)


def generic_weights(count: int) -> list[list[int]]:
    """Three fixed integer weight vectors on the pencil basis; any choice gives valid bounds."""
    return [
        [i + 1 for i in range(count)],
        [(i + 1) ** 2 + 3 for i in range(count)],
        [(7 * i * i + 5 * i + 2) % 97 + 1 for i in range(count)],
    ]


def structure_item(job: tuple[int, Vector]) -> dict[str, Any]:
    """Kernel, pencil, commutant and Lie closure at a base point of A_n, with two-sided bounds."""
    dimension, base = job
    table = sign_table(dimension)
    space, size = fmpz_mat(to_int(left(dimension, table, dict(base)))).nullspace()
    frame = np.array([[int(space[i, j]) for j in range(size)] for i in range(dimension)], dtype=np.int64)
    gram = frame.T @ frame
    half = dimension // 2
    in_lower = size - int(fmpz_mat(to_int(frame[half:])).rank())
    in_upper = size - int(fmpz_mat(to_int(frame[:half])).rank())
    forms = [frame.T @ left(dimension, table, {w: 1}) @ frame for w in range(1, dimension)]
    skew = all(np.array_equal(f, -f.T) for f in forms)
    require(
        max(int(np.abs(m).max()) for m in [frame, gram, *forms]) < ENTRY_BOUND,
        "frame, Gram and form entries stay below the int64 bound",
    )
    basis: list[int] = []
    stacked: list[list[int]] = []
    for w, form in enumerate(forms):
        if np.any(form):
            trial = [*stacked, [int(x) for x in form.ravel()]]
            if int(fmpz_mat(trial).rank()) > len(stacked):
                stacked, basis = trial, [*basis, w]
    inverse = fmpq_mat(to_int(gram)).inv()
    inverse_p = np.array([[residue(inverse[i, j]) for j in range(size)] for i in range(size)], dtype=np.int64)
    operators_p = [(inverse_p @ forms[w]) % P for w in basis]
    operators_q = [inverse * fmpq_mat(to_int(forms[w])) for w in basis]
    generic = [
        sum((c * m for c, m in zip(weights, operators_p, strict=True)), np.zeros((size, size), dtype=np.int64)) % P
        for weights in generic_weights(len(basis))
    ]
    commutant_space = nullspace_mod_p(commutation_system(generic, size))
    elements: list[fmpq_mat] = []
    for row in commutant_space:
        values = [reconstruct(int(x)) for x in row]
        if any(v is None for v in values):
            elements = []
            break
        elements.append(fmpq_mat(size, size, [fmpq(v.numerator, v.denominator) for v in values if v is not None]))
    verified = bool(elements) and all(x * m == m * x for x in elements for m in operators_q)
    lower = (
        int(fmpq_mat([[x[i, j] for i in range(size) for j in range(size)] for x in elements]).rank()) if verified else 0
    )
    trace_form_negative = noncommutative = False
    closure_upper = closure_upper_skew_only = -1
    kept: list[fmpq_mat] = []
    orthogonal: list[fmpq_mat] = []
    if verified:
        noncommutative = any(a * b != b * a for a in elements for b in elements)
        unit = fmpq_mat(size, size, [fmpq(int(i == j)) for i in range(size) for j in range(size)])

        def trace(x: fmpq_mat) -> Any:
            return sum((x[i, i] for i in range(size)), fmpq(0))

        traceless = [x - unit * (trace(x) / size) for x in elements]
        for x in traceless:
            rows = [[y[i, j] for i in range(size) for j in range(size)] for y in [*kept, x]]
            if int(fmpq_mat(rows).rank()) > len(kept):
                kept.append(x)
        form = [[-trace(a * b) for b in kept] for a in kept]
        trace_form_negative = all(fmpq_mat([row[:m] for row in form[:m]]).det() > 0 for m in range(1, len(kept) + 1))
        residues = [
            np.array([[residue(x[i, j]) for j in range(size)] for i in range(size)], dtype=np.int64) for x in elements
        ]
        container = np.vstack([skew_system(gram), commutation_system(residues, size)])
        closure_upper_skew_only = nullity_mod_p(container)
        # tr(J [A, B]) = tr([J, A] B) = 0 for J in the commutant and A in the closure, so a traceless commutant element
        # orthogonal to every pencil element under the trace pairing is orthogonal to the whole closure.
        orthogonal = [x for x in kept if all(trace(x * m) == 0 for m in operators_q)]
        trace_rows = [
            np.array([[residue(x[j, i]) for j in range(size)] for i in range(size)], dtype=np.int64).ravel()
            for x in orthogonal
        ]
        closure_upper = nullity_mod_p(np.vstack([container, *trace_rows])) if trace_rows else closure_upper_skew_only
    echelon = Echelon(size * size)
    frontier = echelon.add(np.array([g.ravel() for g in generic]))
    while frontier:
        brackets = [
            ((f.reshape(size, size) @ g - g @ f.reshape(size, size)) % P).ravel() for f in frontier for g in generic
        ]
        frontier = echelon.add(np.array(brackets))
    return {
        "dimension": dimension,
        "base": [list(t) for t in base],
        "table_mismatches": table_mismatches(dimension, table),
        "kernel": int(size),
        "kernel_in_lower_half": int(in_lower),
        "kernel_in_upper_half": int(in_upper),
        "gram_scalar": int(gram[0, 0]) if np.array_equal(gram, gram[0, 0] * np.eye(size, dtype=np.int64)) else 0,
        "forms_skew": bool(skew),
        "pencil_dimension": len(basis),
        "commutant_upper": len(commutant_space),
        "commutant_lower": lower,
        "commutant_verified": bool(verified),
        "commutant_noncommutative": bool(noncommutative),
        "commutant_trace_form_negative_definite": bool(trace_form_negative),
        "closure_lower": len(echelon.pivots),
        "closure_upper": int(closure_upper),
        "closure_upper_skew_only": int(closure_upper_skew_only),
        "commutant_traceless_dimension": len(kept),
        "trace_constraints": len(orthogonal),
    }


def pencil_frame(name: str) -> tuple[int, np.ndarray, dict[int, np.ndarray], list[int]]:
    """Kernel size, frame Gram matrix, compressions K^T L_w K of the 31 imaginary units, and a greedy basis of units."""
    dimension = 32
    table = sign_table(dimension)
    space, size = fmpz_mat(to_int(left(dimension, table, dict(STRATA[name])))).nullspace()
    frame = np.array([[int(space[i, j]) for j in range(size)] for i in range(dimension)], dtype=np.int64)
    forms = {w: frame.T @ left(dimension, table, {w: 1}) @ frame for w in range(1, dimension)}
    units: list[int] = []
    stacked: list[list[int]] = []
    for w in range(1, dimension):
        if np.any(forms[w]):
            trial = [*stacked, [int(x) for x in forms[w].ravel()]]
            if int(fmpz_mat(trial).rank()) > len(stacked):
                stacked, units = trial, [*units, w]
    return int(size), frame.T @ frame, forms, units


def pfaffian_terms(size: int, forms: dict[int, np.ndarray], coordinates: list[int]) -> dict[tuple[int, ...], int]:
    """Pfaffian of sum x_i K^T L_(coordinates[i]) K in Z[x], by expansion along the first index of each subset."""
    context = fmpz_mpoly_ctx.get(("x", len(coordinates)), "lex")
    gens = context.gens()
    zero = context.from_dict({})
    entries = [
        [
            sum((int(forms[w][a, b]) * gens[i] for i, w in enumerate(coordinates) if forms[w][a, b]), zero)
            for b in range(size)
        ]
        for a in range(size)
    ]
    cache: dict[int, Any] = {0: context.from_dict({(0,) * len(coordinates): 1})}

    def pfaffian(mask: int) -> Any:
        if mask not in cache:
            indices = [a for a in range(size) if mask >> a & 1]
            first, total = indices[0], zero
            for position, other in enumerate(indices[1:]):
                if entries[first][other] != 0:
                    term = entries[first][other] * pfaffian(mask & ~(1 << first) & ~(1 << other))
                    total = total + term if position % 2 == 0 else total - term
            cache[mask] = total
        return cache[mask]

    return {tuple(int(e) for e in m): int(c) for m, c in pfaffian((1 << size) - 1).to_dict().items()}


def leading_forms(name: str, coordinates: list[int], s: Any, xs: Any) -> tuple[Any, Any, int, int]:
    """Leading coefficients of Q and G of the strata record on the line y_0 + s sum x_i e_(coordinates[i])."""
    z: list[Any] = [sp.Integer(0)] * 16
    for index, value in STRATA[name]:
        z[index % 16] += value * (sp.I if index >= 16 else 1)
    for x, w in zip(xs, coordinates, strict=True):
        if w % 16:
            z[w % 16] += s * x * (sp.I if w >= 16 else 1)
    uu = sum(z[k] ** 2 for k in range(1, 8))
    vv = sum(z[k] ** 2 for k in range(9, 16))
    uv = sum(z[k] * z[8 + k] for k in range(1, 8))
    q = sp.Poly(sp.expand(uu + z[8] ** 2 + vv), s)
    g = sp.Poly(sp.expand((uu + z[8] ** 2 + vv) ** 2 - 4 * (uu * vv - uv**2)), s)

    def order(poly: Any) -> int:
        return int(min(e for (e,), c in poly.terms() if sp.expand(c) != 0))

    return (
        sp.expand(q.coeff_monomial(s ** order(q))),
        sp.expand(g.coeff_monomial(s ** order(g))),
        order(q),
        order(g),
    )


def modulus_squared(value: Any) -> Any:
    real, imaginary = sp.expand(value).as_real_imag()
    return sp.expand(real**2 + imaginary**2)


def strata_item(job: tuple[str, bool]) -> dict[str, Any]:
    """Pfaffian of the pencil on the doubly pure coordinate units against |lead Q|^2 |lead G|^2.

    job = (point, keep_off_domain): with keep_off_domain the coordinate on e_16, outside the doubly pure domain of Q
    and G, stays in the pencil; the self-test uses it as the mutant on which the identity fails. The record also holds
    the reduction from all 30 doubly pure units to the basis units: the forms of the 30 units span the same space as
    those of the basis units, and the leading forms of Q and G are constant along the kernel of w -> K^T L_w K on R^30.
    """
    name, keep_off_domain = job
    size, gram, forms, units = pencil_frame(name)
    pure = list(units) if keep_off_domain else [w for w in units if w % 16]
    s = sp.Symbol("s", real=True)
    xs = sp.symbols(f"x0:{len(pure)}", real=True)
    lead_q, lead_g, order_q, order_g = leading_forms(name, pure, s, xs)
    target = sp.Poly(sp.expand(modulus_squared(lead_q) * modulus_squared(lead_g)), *xs)
    if target.is_zero:
        require(keep_off_domain, f"{name}: the leading forms vanish on the doubly pure units")
        return {"point": name, "pfaffian_equals_constant_times_moduli": False}
    value_terms = pfaffian_terms(size, forms, pure)
    target_terms = {tuple(int(e) for e in m): int(c) for m, c in target.terms()}
    lead = max(target_terms)
    constant = Fraction(value_terms.get(lead, 0), target_terms[lead])
    identity = (
        constant != 0
        and constant.denominator == 1
        and value_terms == {m: int(constant) * c for m, c in target_terms.items()}
    )
    context = fmpz_mpoly_ctx.get(("x", len(pure)), "lex")
    factors = context.from_dict(value_terms).factor()[1]
    gram_det = int(fmpz_mat(to_int(gram)).det())
    all_pure = [w for w in range(1, 32) if w % 16]
    columns = fmpz_mat([[int(x) for x in forms[w].ravel()] for w in all_pure]).transpose()
    kernel, kernel_dimension = columns.nullspace()
    ys = sp.symbols(f"y0:{len(all_pure)}", real=True)
    t = sp.Symbol("t", real=True)
    full_q, full_g, _, _ = leading_forms(name, all_pure, s, ys)
    invariant = True
    for column in range(kernel_dimension):
        shift = {y: y + t * int(kernel[i, column]) for i, y in enumerate(ys)}
        invariant = invariant and all(sp.expand(f.subs(shift, simultaneous=True) - f) == 0 for f in (full_q, full_g))
    return {
        "point": name,
        "kernel": size,
        "coordinate_units": units,
        "doubly_pure_units": pure,
        "order_q": order_q,
        "order_g": order_g,
        "pfaffian_terms": len(value_terms),
        "pfaffian_degree": max(sum(m) for m in value_terms),
        "pfaffian_factor_degrees": sorted([int(f.total_degree()), int(m)] for f, m in factors),
        "pfaffian_equals_constant_times_moduli": bool(identity),
        "constant_squared_in_gram_2_frame": str(constant**2 * 2**size / gram_det),
        "all_doubly_pure_forms_rank": int(fmpz_mat([[int(x) for x in forms[w].ravel()] for w in all_pure]).rank()),
        "kernel_on_all_doubly_pure_units": int(kernel_dimension),
        "leading_forms_constant_along_kernel": bool(invariant),
    }


def automorphism_item(_: int) -> dict[str, Any]:
    """The sign character chi(k) = (-1)^(bit 3 of k) gives the automorphism e_k -> chi(k) e_k; it maps N- to N+, and
    the Pfaffians of the two pencils on the doubly pure basis units correspond under x_w -> chi(w) x_w."""

    def chi(k: int) -> int:
        return -1 if k >> 3 & 1 else 1

    character = all(chi(p) * chi(q) == chi(p ^ q) for p in range(32) for q in range(32))
    image = tuple(sorted((k, chi(k) * v) for k, v in STRATA["N-"]))
    size_m, _gram_m, forms_m, units_m = pencil_frame("N-")
    size_p, _gram_p, forms_p, units_p = pencil_frame("N+")
    pure_m = [w for w in units_m if w % 16]
    pure_p = [w for w in units_p if w % 16]
    minus = pfaffian_terms(size_m, forms_m, pure_m)
    plus = pfaffian_terms(size_p, forms_p, pure_p)
    signs = [chi(w) for w in pure_m]
    substituted = {m: c * int(np.prod([signs[i] ** e for i, e in enumerate(m)])) for m, c in minus.items()}
    lead = max(plus)
    ratio = Fraction(substituted.get(lead, 0), plus[lead])
    proportional = (
        ratio != 0
        and set(substituted) == set(plus)
        and all(Fraction(c, plus[m]) == ratio for m, c in substituted.items())
    )
    return {
        "character_is_multiplicative": bool(character),
        "maps_n_minus_to_n_plus": image == tuple(sorted(STRATA["N+"])),
        "same_units": pure_m == pure_p,
        "pfaffians_proportional": bool(proportional),
    }


def anticommutation_item(job: tuple[int, int]) -> dict[str, Any]:
    """L_w L_h + L_h L_w for the unit h and every other imaginary unit w, L_h^2 + I, and skewness of every L_w;
    job = (dimension, h)."""
    dimension, h = job
    table = sign_table(dimension)
    doubling = left(dimension, table, {h: 1})
    skew = all(np.array_equal(m, -m.T) for m in (left(dimension, table, {w: 1}) for w in range(1, dimension)))
    failures = [
        w
        for w in range(1, dimension)
        if w != h and np.any(left(dimension, table, {w: 1}) @ doubling + doubling @ left(dimension, table, {w: 1}))
    ]
    return {
        "dimension": dimension,
        "anticommutation_failures": failures,
        "square_is_minus_identity": bool(np.array_equal(doubling @ doubling, -np.eye(dimension, dtype=np.int64))),
        "imaginary_units_skew": bool(skew),
    }


def gauss_mul(a: list[tuple[int, int]], b: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Product of two polynomials in s with Gaussian-integer coefficients (re, im)."""
    out = [(0, 0)] * (len(a) + len(b) - 1)
    for i, (ar, ai) in enumerate(a):
        for j, (br, bi) in enumerate(b):
            r, m = out[i + j]
            out[i + j] = (r + ar * br - ai * bi, m + ar * bi + ai * br)
    return out


def gauss_add(a: list[tuple[int, int]], b: list[tuple[int, int]], scale: int = 1) -> list[tuple[int, int]]:
    size = max(len(a), len(b))
    a = a + [(0, 0)] * (size - len(a))
    b = b + [(0, 0)] * (size - len(b))
    return [(x[0] + scale * y[0], x[1] + scale * y[1]) for x, y in zip(a, b, strict=True)]


def square_sum(line: list[list[tuple[int, int]]], indices: range) -> list[tuple[int, int]]:
    total: list[tuple[int, int]] = [(0, 0)]
    for k in indices:
        total = gauss_add(total, gauss_mul(line[k], line[k]))
    return total


def determinant_item(name: str) -> dict[str, Any]:
    """det of the pencil against (|lead Q|^2 |lead G|^2)^2 at integer points over all doubly pure units.

    Products come from the doubling formula (doubled), Q and G from Gaussian-integer polynomials in s; nothing is
    shared with cd_core, sympy or the polynomial-ring expansion of strata_item.
    """
    dimension, base = 32, dict(STRATA[name])

    def left_doubled(vector: dict[int, int]) -> np.ndarray:
        element = [vector.get(k, 0) for k in range(dimension)]
        columns = [doubled(element, [int(r == q) for r in range(dimension)]) for q in range(dimension)]
        return np.array([[columns[q][r] for q in range(dimension)] for r in range(dimension)], dtype=np.int64)

    space, size = fmpz_mat(to_int(left_doubled(base))).nullspace()
    frame = np.array([[int(space[i, j]) for j in range(size)] for i in range(dimension)], dtype=np.int64)
    gram_det = int(fmpz_mat(to_int(frame.T @ frame)).det())
    units = [w for w in range(1, dimension) if w % 16]
    forms = {w: frame.T @ left_doubled({w: 1}) @ frame for w in units}
    z0 = [(0, 0)] * 16
    for index, value in base.items():
        r, m = z0[index % 16]
        z0[index % 16] = (r, m + value) if index >= 16 else (r + value, m)
    ratios: set[str] = set()
    points: set[tuple[int, ...]] = set()
    lower_vanish = True
    zero_targets = 0
    for t in range(1, DETERMINANT_POINTS + 1):
        x = [((7 * t * (i + 1) + 3 * i * i + t * t) % 1009) - 504 for i in range(len(units))]
        points.add(tuple(x))
        zeta = [(0, 0)] * 16
        for value, w in zip(x, units, strict=True):
            r, m = zeta[w % 16]
            zeta[w % 16] = (r, m + value) if w >= 16 else (r + value, m)
        line = [[z0[k], zeta[k]] for k in range(16)]
        uu, vv = square_sum(line, range(1, 8)), square_sum(line, range(9, 16))
        uv: list[tuple[int, int]] = [(0, 0)]
        for k in range(1, 8):
            uv = gauss_add(uv, gauss_mul(line[k], line[8 + k]))
        q = gauss_add(gauss_add(uu, gauss_mul(line[8], line[8])), vv)
        g = gauss_add(gauss_mul(q, q), gauss_add(gauss_mul(uu, vv), gauss_mul(uv, uv), -1), -4)
        lower_vanish = lower_vanish and q[0] == (0, 0) and all(c == (0, 0) for c in g[:3])
        target = (q[1][0] ** 2 + q[1][1] ** 2) * (g[3][0] ** 2 + g[3][1] ** 2)
        det = int(
            fmpz_mat(
                to_int(sum((v * forms[w] for v, w in zip(x, units, strict=True)), np.zeros((size, size), np.int64)))
            ).det()
        )
        if target == 0:
            zero_targets += 1
            lower_vanish = lower_vanish and det == 0
            continue
        ratios.add(str(Fraction(det * 2**size, target * target * gram_det)))
    return {
        "point": name,
        "doubly_pure_units": len(units),
        "points": DETERMINANT_POINTS,
        "distinct_points": len(points),
        "lower_coefficients_vanish": bool(lower_vanish),
        "zero_targets": zero_targets,
        "normalized_ratios": sorted(ratios),
    }


def zero_divisor_block(a: tuple[int, ...]) -> list[tuple[int, ...]]:
    """The elements (a, b) of the census for one first half a, with b in product order."""
    norm = sum(x * x for x in a)
    return [
        (0, *a, 0, *b)
        for b in product((-1, 0, 1), repeat=7)
        if sum(x * x for x in b) == norm and sum(x * y for x, y in zip(a, b, strict=True)) == 0
    ]


def sedenion_zero_divisors() -> list[tuple[int, ...]]:
    """(a, b) with a, b pure octonions with entries in {-1, 0, 1}, |a|^2 = |b|^2 <= 3 and a.b = 0, in product order;
    the blocks of each a are independent and map through the pool in that order."""
    halves = [a for a in product((-1, 0, 1), repeat=7) if 0 < sum(x * x for x in a) <= 3]
    return [v for block in parallel.ordered_map(zero_divisor_block, halves, 1) for v in block]


def census_chunk(job: tuple[int, tuple[tuple[int, ...], ...]]) -> dict[str, Any]:
    """Nullity of each zero divisor of the chunk, L_(e_8)-invariance of its kernel, and dim (ker L_p n ker L_q) for
    pairs (i, j) with j = i + 1, i + 1 + CENSUS_STRIDE, ... ."""
    chunk, points = job
    table = sign_table(16)
    doubling = left(16, table, {8: 1})
    matrices = [left(16, table, dict(enumerate(v))) for v in points]
    nullities: Counter[int] = Counter()
    invariant = 0
    dims: Counter[int] = Counter()
    for i in range(chunk, len(points), CENSUS_CHUNKS):
        space, nullity = fmpz_mat(to_int(matrices[i])).nullspace()
        nullities[int(nullity)] += 1
        frame = np.array([[int(space[r, c]) for c in range(nullity)] for r in range(16)], dtype=np.int64)
        invariant += int(fmpz_mat(to_int(np.hstack([frame, doubling @ frame]))).rank()) == nullity
        for j in range(i + 1, len(points), CENSUS_STRIDE):
            dims[16 - int(fmpz_mat(to_int(np.vstack([matrices[i], matrices[j]]))).rank())] += 1
    return {"nullities": dict(nullities), "invariant": invariant, "dims": dict(dims)}


def census() -> dict[str, Any]:
    points = tuple(sedenion_zero_divisors())
    parts = parallel.ordered_map(census_chunk, [(c, points) for c in range(CENSUS_CHUNKS)], 1)
    nullities: Counter[int] = Counter()
    dims: Counter[int] = Counter()
    for part in parts:
        nullities.update(part["nullities"])
        dims.update(part["dims"])
    return {
        "zero_divisors": len(points),
        "nullities": {str(k): v for k, v in sorted(nullities.items())},
        "kernels_invariant_under_doubling_unit": sum(p["invariant"] for p in parts),
        "pairs": sum(dims.values()),
        "common_kernel_dimensions": {str(k): v for k, v in sorted(dims.items())},
    }


def sp_dimension(k: int) -> int:
    return k * (2 * k + 1)


def tower_ok(row: dict[str, Any], n: int) -> bool:
    k = 2 ** (n - 4)
    return (
        row["kernel"] == 2 ** (n - 2)
        and row["pencil_dimension"] == 2 ** (n - 2) - 1
        and row["commutant_upper"] == row["commutant_lower"] == 4
        and row["commutant_noncommutative"]
        and row["commutant_trace_form_negative_definite"]
        and row["closure_lower"] == row["closure_upper"] == sp_dimension(k)
    )


def outcomes(result: dict[str, Any]) -> dict[str, bool]:
    tower = {row["dimension"]: row for row in result["tower"]}
    calibration = {row["base"][2][0]: row for row in result["calibration"]}
    strata = {row["point"]: row for row in result["strata"]}
    dims = result["census"]["common_kernel_dimensions"]
    return {
        "P20": tower_ok(tower[128], 7)
        and tower[128]["kernel_in_lower_half"] == tower[128]["kernel_in_upper_half"] == 16,
        "P21": tower_ok(tower[256], 8)
        and tower[256]["kernel_in_lower_half"] == tower[256]["kernel_in_upper_half"] == 32,
        "P22": calibration[3]["commutant_lower"] == calibration[3]["commutant_upper"] == 1
        and calibration[3]["closure_lower"] == calibration[3]["closure_upper"] == 28,
        "P23": all(
            strata[n]["pfaffian_equals_constant_times_moduli"]
            and 2 * (strata[n]["order_q"] + strata[n]["order_g"]) == 8
            for n in ("N-", "N+")
        ),
        "P24": set(dims) <= {"0", "2", "4"},
        "P26": all(
            row["lower_coefficients_vanish"] and row["normalized_ratios"] == ["4"] for row in result["determinant"]
        ),
    }


def validate(result: dict[str, Any]) -> None:
    tower = {row["dimension"]: row for row in result["tower"]}
    for dimension, n in zip(TOWER_LEVELS, range(4, 9), strict=True):
        row = tower[dimension]
        require(row["table_mismatches"] == 0, f"A_{n}: the sign table follows the doubling formula")
        require(row["forms_skew"], f"A_{n}: every compression is skew")
        require(row["gram_scalar"] != 0, f"A_{n}: the kernel frame has scalar Gram")
        require(tower_ok(row, n), f"A_{n}: kernel, pencil, quaternion commutant and closure sp(2^(n-4))")
        if n > 4:
            require(
                row["kernel_in_lower_half"] == row["kernel_in_upper_half"] == 2 ** (n - 3),
                f"A_{n}: the kernel meets each half in 2^(n-3)",
            )
    r_row, c_row = result["calibration"]
    require(r_row["forms_skew"] and c_row["forms_skew"], "types R and C: every compression is skew")
    require(r_row["commutant_verified"] and r_row["commutant_upper"] == r_row["commutant_lower"] == 1, "type R: R")
    require(r_row["closure_lower"] == r_row["closure_upper"] == 28, "type R: closure so(8)")
    require(c_row["commutant_upper"] == c_row["commutant_lower"] == 2, "type C: commutant of dimension 2")
    require(not c_row["commutant_noncommutative"], "type C: the commutant is commutative")
    require(
        c_row["commutant_traceless_dimension"] == 1 and c_row["commutant_trace_form_negative_definite"],
        "type C: the traceless part is one element of negative square trace, so the commutant is C",
    )
    require(c_row["closure_upper_skew_only"] == 16, "type C: the Gram-skew container alone bounds the closure by 16")
    require(c_row["trace_constraints"] == 1, "type C: the commutant element is trace-orthogonal to the pencil")
    require(c_row["closure_lower"] == c_row["closure_upper"] == 15, "type C: closure of dimension 15, su(4)")
    strata = {row["point"]: row for row in result["strata"]}
    require(strata["VB"]["order_q"] == 1 and strata["VB"]["order_g"] == 2, "VB: Q order 1, G order 2")
    require(strata["VB"]["constant_squared_in_gram_2_frame"] == "1", "VB: the constant is -1 or 1 with Gram 2 I")
    require(strata["VB"]["pfaffian_factor_degrees"] == [[2, 1], [2, 1], [2, 1]], "VB: three quadratic factors")
    for name, basis, kernel in (("VB", 8, 22), ("N-", 18, 12), ("N+", 18, 12)):
        row = strata[name]
        require(
            row["all_doubly_pure_forms_rank"] == basis and row["kernel_on_all_doubly_pure_units"] == kernel,
            f"{name}: the forms of all 30 doubly pure units span the space of the basis units",
        )
        require(row["leading_forms_constant_along_kernel"], f"{name}: lead Q and lead G are constant on the kernel")
    for name in ("VB", "N-", "N+"):
        require(strata[name]["pfaffian_equals_constant_times_moduli"], f"{name}: Pf = c |lead Q|^2 |lead G|^2")
    for name in ("N-", "N+"):
        row = strata[name]
        require(row["kernel"] == 16 and len(row["coordinate_units"]) == 19, f"{name}: kernel 16, pencil 19")
        require(len(row["doubly_pure_units"]) == 18, f"{name}: 18 doubly pure units")
        require(row["order_q"] == 1 and row["order_g"] == 3, f"{name}: Q order 1, G order 3")
        require(row["pfaffian_degree"] == 8 and row["pfaffian_terms"] == 8395, f"{name}: degree 8, 8,395 terms")
        require(row["pfaffian_factor_degrees"] == [[2, 1], [6, 1]], f"{name}: factors of degree 2 and 6")
        require(row["constant_squared_in_gram_2_frame"] == "4", f"{name}: |c| = 2 in a frame of Gram 2 I")
    anticommutation = result["anticommutation"]
    require(
        anticommutation["anticommutation_failures"] == [] and anticommutation["square_is_minus_identity"],
        "A_4: L_(e_8) anticommutes with the other imaginary units and squares to -I",
    )
    require(anticommutation["imaginary_units_skew"], "A_4: every imaginary unit acts by a skew matrix")
    require([row["point"] for row in result["determinant"]] == ["N-", "N+"], "determinant route at N- and N+")
    automorphism = result["automorphism"]
    require(
        all(automorphism[k] for k in ("character_is_multiplicative", "maps_n_minus_to_n_plus", "same_units")),
        "e_k -> (-1)^(bit 3 of k) e_k is an automorphism mapping N- to N+",
    )
    require(automorphism["pfaffians_proportional"], "the N- and N+ Pfaffians correspond under x_w -> chi(w) x_w")
    for row in result["determinant"]:
        require(row["doubly_pure_units"] == 30, f"{row['point']}: 30 doubly pure units")
        require(
            row["points"] == row["distinct_points"] == DETERMINANT_POINTS and row["zero_targets"] == 0,
            f"{row['point']}: 60 distinct points, none with a vanishing leading form",
        )
        require(row["lower_coefficients_vanish"], f"{row['point']}: Q of order 1 and G of order 3 at every point")
        require(row["normalized_ratios"] == ["4"], f"{row['point']}: det = 4 (|lead Q|^2 |lead G|^2)^2 in Gram 2 I")
    census_row = result["census"]
    require(census_row["zero_divisors"] == 26096, "census: 26,096 zero divisors")
    require(census_row["nullities"] == {"4": 26096}, "census: every one has nullity 4")
    require(census_row["kernels_invariant_under_doubling_unit"] == 26096, "census: every kernel is L_(e_8)-invariant")
    require(census_row["pairs"] == 3523095, "census: 3,523,095 pairs")
    require(
        census_row["common_kernel_dimensions"] == {"0": 3518410, "2": 4268, "4": 417},
        "census: common kernels of dimension 0, 2 and 4 only",
    )
    held = outcomes(result)
    require(set(held) | NOT_RUN == set(PREDICTIONS), "every prediction has an outcome or is marked not run")
    require(all(held.values()), "P20 to P24 and P26 held")
    require(result["predictions"] == PREDICTIONS and result["prediction_held"] == held, "predictions stored")


def build_result() -> dict[str, Any]:
    jobs = [(d, BASE) for d in TOWER_LEVELS] + list((32, v) for v in CALIBRATION.values())
    rows = parallel.ordered_map(structure_item, jobs, 1)
    result: dict[str, Any] = {
        "schema": "a5-pencil-certificates/1",
        "prime": P,
        "tower": rows[: len(TOWER_LEVELS)],
        "calibration": rows[len(TOWER_LEVELS) :],
        "strata": parallel.ordered_map(strata_item, [(name, False) for name in STRATA], 1),
        "determinant": parallel.ordered_map(determinant_item, ["N-", "N+"], 1),
        "automorphism": automorphism_item(0),
        "anticommutation": anticommutation_item((16, 8)),
        "census": census(),
        "predictions": PREDICTIONS,
        "predictions_not_run": sorted(NOT_RUN),
    }
    result["prediction_held"] = outcomes(result)
    validate(result)
    return result


def self_test() -> list[str]:
    passed: list[str] = []

    def control(name: str, baseline: bool, mutant_fails: bool) -> None:
        require(baseline, f"{name}: holds on the record's input")
        require(mutant_fails, f"{name}: fails on the mutant")
        passed.append(name)

    sedenion = structure_item((16, BASE))
    real_point = structure_item((32, CALIBRATION["R e1+e10+e3+e20"]))
    control("tower rule at A_4 against a type-R point of A_5", tower_ok(sedenion, 4), not tower_ok(real_point, 5))
    complex_point = structure_item((32, CALIBRATION["C e1+e10+2(e20+e31)"]))
    control(
        "closure bounds meet at sp(1), so(8) and su(4), and the type-C bound needs the trace constraint",
        sedenion["closure_lower"] == sedenion["closure_upper"] == 3
        and real_point["closure_lower"] == real_point["closure_upper"] == 28
        and complex_point["closure_lower"] == complex_point["closure_upper"] == 15,
        complex_point["closure_upper_skew_only"] != complex_point["closure_lower"],
    )
    table = sign_table(16)
    mutant = [row[:] for row in table]
    mutant[3][5] = -mutant[3][5]
    control(
        "sign table against the doubling formula", table_mismatches(16, table) == 0, table_mismatches(16, mutant) > 0
    )
    control(
        "anticommutation holds for the doubling unit e_8 and fails for e_4",
        anticommutation_item((16, 8))["anticommutation_failures"] == [],
        anticommutation_item((16, 4))["anticommutation_failures"] != [],
    )
    control(
        "VB Pfaffian identity holds on the doubly pure units and fails with the coordinate on e_16 kept",
        strata_item(("VB", False))["pfaffian_equals_constant_times_moduli"],
        not strata_item(("VB", True))["pfaffian_equals_constant_times_moduli"],
    )
    control(
        "imaginary units act by skew matrices, the real unit does not",
        anticommutation_item((16, 8))["imaginary_units_skew"],
        not np.array_equal(left(16, table, {0: 1}), -left(16, table, {0: 1}).T),
    )
    control(
        "reconstruction of a residue below the bound, and not above it",
        reconstruct(residue(fmpq(-5, 7))) == Fraction(-5, 7),
        reconstruct(residue(fmpq(200, 3))) != Fraction(200, 3),
    )
    return passed


def source_digests() -> dict[str, str]:
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCE_FILES}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path, help="write the record")
    mode.add_argument("--check", type=Path, help="recompute and compare with a written record")
    mode.add_argument("--self-test", action="store_true", help="run the mutation controls")
    arguments = parser.parse_args()
    if arguments.self_test:
        names = self_test()
        print(f"self-test passed: {len(names)} controls")
        return 0
    result = build_result()
    result["sources"] = source_digests()
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if arguments.out:
        arguments.out.write_text(text, encoding="utf-8")
        return 0
    require(arguments.check.read_text(encoding="utf-8") == text, "the record differs from its recomputation")
    print("record matches its recomputation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
