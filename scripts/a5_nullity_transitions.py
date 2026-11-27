"""Exact transitions between the annihilator dimensions 4, 8, 12 and 16 of the 32-dimensional algebra A_5.

For y in A_5 the nullity of left multiplication L_y is 0, 4, 8, 12 or 16. The record certifies, in exact rational
arithmetic, three polynomial paths that join the four nonzero values, the limiting kernels of two nullity-4 paths
into the nullity-8 point e_1 + e_10, the first-order compression P_0 L_w P_0 at each junction, and the structure of
that compression at e_1 + e_10: a seven-dimensional pencil of skew forms on the kernel whose Pfaffian is
16 ((u.u + m^2 + v.v)^2 - 4 ((u.u)(v.v) - (u.v)^2)) in coordinates (u, m, v) of R^3 + R + R^3, and whose rank-4
directions give limiting 4-planes that depend on u x v alone. Along a path the nullity at a real parameter is the
order of x in the characteristic polynomial of the Gram operator, computed over Q[s]; the exceptional parameters are
the real roots of one coefficient polynomial, counted exactly. Three elementary identities are checked at several
levels of the tower. Predictions written before the first run are stored with their outcome. No random draw enters.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
from typing import Any

import sympy as sp
from flint import fmpq, fmpq_mat, fmpz_mat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-exceptional-fibers" / "hardware-orbits"))

import hardware_orbits  # noqa: E402

import cd_core  # noqa: E402
import kernel_limits  # noqa: E402
import parallel  # noqa: E402

DIMENSION = 32
S = sp.Symbol("s", real=True)
X = sp.Symbol("x")
SOURCE_FILES = (
    "gororoba_quantum/cd_core.py",
    "gororoba_quantum/kernel_limits.py",
    "gororoba_quantum/parallel.py",
    "docs/evidence/a5-exceptional-fibers/hardware-orbits/hardware_orbits.py",
    "scripts/a5_nullity_transitions.py",
)
Terms = tuple[tuple[int, int, int], ...]
"""A path y(s): each entry (index, a, b) adds (a + b s) e_index."""
PATHS: dict[str, Terms] = {
    "gamma1": ((1, 1, 0), (10, 1, 0), (9, 0, 1), (26, 0, 1)),
    "gamma2": ((1, 1, -1), (10, 1, -1), (3, 0, 1), (20, 0, 1)),
    "gamma3": ((3, 1, 0), (20, 1, 0), (12, 0, 1), (27, 0, -1)),
    "beta": ((1, 1, 0), (10, 1, 0), (2, 0, 1), (17, 0, 1)),
}
PATH_EXPECTED: dict[str, tuple[int, dict[str, int]]] = {
    "gamma1": (4, {"0": 8}),
    "gamma2": (8, {"1": 12}),
    "gamma3": (12, {"-1": 16, "1": 16}),
    "beta": (4, {"0": 8}),
}
JUNCTIONS: dict[str, tuple[dict[int, int], dict[int, int]]] = {
    "gamma1 at 0": ({1: 1, 10: 1}, {9: 1, 26: 1}),
    "gamma2 at 1": ({3: 1, 20: 1}, {1: -1, 10: -1, 3: 1, 20: 1}),
    "gamma3 at 1": ({3: 1, 20: 1, 12: 1, 27: -1}, {12: 1, 27: -1}),
    "gamma3 at -1": ({3: 1, 20: 1, 12: -1, 27: 1}, {12: 1, 27: -1}),
}
ORBIT_POINTS: dict[str, dict[int, int]] = {
    "gamma1(1)": {1: 1, 10: 1, 9: 1, 26: 1},
    "beta(1)": {1: 1, 10: 1, 2: 1, 17: 1},
    "e1+e10": {1: 1, 10: 1},
    "2 gamma2(1/2)": {1: 1, 10: 1, 3: 1, 20: 1},
    "e3+e20": {3: 1, 20: 1},
    "gamma3(1)": {3: 1, 20: 1, 12: 1, 27: -1},
    "gamma3(-1)": {3: 1, 20: 1, 12: -1, 27: 1},
}
ORBIT_EXPECTED = {
    "gamma1(1)": ("S4_VG", 4),
    "beta(1)": ("S4_VG", 4),
    "e1+e10": ("W8", 8),
    "2 gamma2(1/2)": ("W8", 8),
    "e3+e20": ("VB", 12),
    "gamma3(1)": ("Nm", 16),
    "gamma3(-1)": ("Np", 16),
}
BASE = {1: 1, 10: 1}
BASE_KEY: tuple[tuple[int, int], ...] = ((1, 1), (10, 1))
STRATA_POINTS: dict[str, dict[int, int]] = {
    "VB e3+e20": {3: 1, 20: 1},
    "N- gamma3(1)": {3: 1, 20: 1, 12: 1, 27: -1},
    "N+ gamma3(-1)": {3: 1, 20: 1, 12: -1, 27: 1},
}
JUNCTION_COFACTORS = {"gamma1": 2**40, "gamma2": 2**32, "gamma3": 2**52, "beta": 2**40}
CONIC_PARAMETERS = (1, 2)
CENSUS_PARAMETERS = (3, 5)
W8_POINTS: dict[str, tuple[dict[int, int], str]] = {
    "e1+e10": ({1: 1, 10: 1}, "H"),
    "e1-e10": ({1: 1, 10: -1}, "H"),
    "e17+e26": ({17: 1, 26: 1}, "H"),
    "e1+e10+e4+e15": ({1: 1, 10: 1, 4: 1, 15: 1}, "H"),
    "e1+e10+e17+e26": ({1: 1, 10: 1, 17: 1, 26: 1}, "H"),
    "e1+e10+2(e18-e25)": ({1: 1, 10: 1, 18: 2, 25: -2}, "H"),
    "e1+e10+e3+e20": ({1: 1, 10: 1, 3: 1, 20: 1}, "R"),
    "2(e1+e10)+e3+e20": ({1: 2, 10: 2, 3: 1, 20: 1}, "R"),
    "e1+e10+2(e20+e31)": ({1: 1, 10: 1, 20: 2, 31: 2}, "C"),
    "e1+e10+2(e21-e30)": ({1: 1, 10: 1, 21: 2, 30: -2}, "C"),
}
"""Points of the orbit W8 with the type of the compression pencil, a key of KINDS."""
U_UNITS = (1, 2, 8)
M_UNIT = 16
V_UNITS = (17, 18, 24)
STIEFEL_PAIRS: tuple[tuple[tuple[int, int, int], tuple[int, int, int]], ...] = (
    ((0, 1, 0), (1, 0, 0)),
    ((0, 1, 0), (-1, 0, 0)),
    ((1, 0, 0), (0, 1, 0)),
    ((1, 0, 0), (0, 0, 1)),
    ((0, 0, 1), (1, 0, 0)),
    ((0, 1, 0), (0, 0, 1)),
    ((1, 2, 2), (2, 1, -2)),
    ((3, 3, 0), (1, -1, -4)),
    ((2, -2, 1), (1, 2, 2)),
    ((2, 3, 6), (3, -6, 2)),
)
SAME_NORMAL = (6, 7)
FAILED_PREDICTIONS = {"P3", "P9", "P11", "P14", "P15", "P19"}
PREDICTIONS = {
    "P1": "gamma1 has nullity 4 at every real s != 0 and 8 at s = 0",
    "P2": "gamma2 has nullity 8 at every real s != 1 and 12 at s = 1",
    "P3": "gamma3 has nullity 12 off its exceptional set and 16 at s = 1, the only exceptional real parameter",
    "P4": "the limiting planes of gamma1 and beta at e1 + e10 are orthogonal and span the kernel, and a third "
    "limiting plane is orthogonal to neither",
    "P5": "the first-order compression has rank 4 at every junction",
    "P6": "L_(a,t)^T L_(a,t) = L_(a,0)^T L_(a,0) + t^2 I for imaginary a at levels 16, 32 and 64",
    "P7": "<e_i, e_j e_k> is alternating on the imaginary units at levels 8 to 64",
    "P8": "on u = a e1, v = b e2, mu = i: Q = a^2 + b^2 - 1 and G = ((a+b)^2 - 1)((a-b)^2 - 1)",
    "P9": "at the second W8 point e1 + e10 + e3 + e20 the pencil has dimension 7, a quaternionic commutant of "
    "dimension 4 and a Lie closure of dimension 10",
    "P10": "the upper-half point e17 + e26 and the four-term lower-half point e1 + e10 + e4 + e15 are quaternionic",
    "P11": "the W8 point e1 + e10 + 2 (e18 - e25), whose halves are linearly independent, is not quaternionic",
    "P12": "at e1 + e10 in A_4 the kernel has dimension 4, the commutant is a quaternion algebra and the pencil and "
    "its Lie closure have dimension 3",
    "P13": "at e1 + e10 in A_6 the kernel has dimension 16, the commutant is a quaternion algebra and the Lie "
    "closure has dimension 36",
    "P14": "the Pfaffian of the pencil at the VB point e3 + e20 is a constant times a product of squared moduli of "
    "the leading forms of Q and G",
    "P15": "a four-term W8 point is quaternionic exactly when the XOR group generated by its support has order 8",
    "P16": "a curved arc along the conic limits on the plane of the normal of its base direction",
    "P18": "restricted to the doubly pure coordinates, the Pfaffian of the VB pencil is a constant times the product "
    "of the squared moduli of the leading forms of Q and G",
    "P19": "no W8 point (p, lam q) with p = e1 + e10 and q a two-term zero divisor of A_4 has ker L_p n ker L_q of "
    "dimension 2",
    "P17": "a W8 point is quaternionic exactly when its kernel splits as A + A across the two halves, and has a "
    "scalar commutant with Lie closure of dimension 28 exactly when the kernel meets each half in 0",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def left_matrix(dimension: int, vector: dict[int, int]) -> sp.Matrix:
    """L_y for y = sum vector[k] e_k: column q holds the coefficient of e_k times the sign of e_k e_q in row k XOR q."""
    matrix = sp.zeros(dimension, dimension)
    for index, value in vector.items():
        for column in range(dimension):
            matrix[index ^ column, column] += value * cd_core.cd_sign(dimension, index, column)
    return matrix


def path_matrix(terms: Terms) -> sp.Matrix:
    matrix = sp.zeros(DIMENSION, DIMENSION)
    for index, constant, slope in terms:
        for column in range(DIMENSION):
            matrix[index ^ column, column] += (constant + slope * S) * cd_core.cd_sign(DIMENSION, index, column)
    return matrix


def rational_rank(matrix: sp.Matrix) -> int:
    rows = [[fmpq(int(sp.Rational(value).p), int(sp.Rational(value).q)) for value in row] for row in matrix.tolist()]
    return int(fmpq_mat(rows).rank())


def doubled_product(a: list[int], b: list[int]) -> list[int]:
    """(a, b)(c, d) = (a c - conj(d) b, d a + b conj(c)), recursively, on integer coordinate lists."""
    size = len(a)
    if size == 1:
        return [a[0] * b[0]]
    half = size // 2

    def conj(v: list[int]) -> list[int]:
        return [v[0]] + [-value for value in v[1:]]

    a1, a2, c, d = a[:half], a[half:], b[:half], b[half:]
    first = [p - q for p, q in zip(doubled_product(a1, c), doubled_product(conj(d), a2), strict=True)]
    second = [p + q for p, q in zip(doubled_product(d, a1), doubled_product(a2, conj(c)), strict=True)]
    return first + second


def convention_item(dimension: int) -> dict[str, Any]:
    """Every basis product of cd_core against the doubling formula, written out independently."""
    mismatches = 0
    for p in range(dimension):
        for q in range(dimension):
            a = [int(k == p) for k in range(dimension)]
            b = [int(k == q) for k in range(dimension)]
            expected = [0] * dimension
            expected[p ^ q] = cd_core.cd_sign(dimension, p, q)
            mismatches += doubled_product(a, b) != expected
    return {"dimension": dimension, "products": dimension * dimension, "mismatches": mismatches}


def path_item(name: str) -> dict[str, Any]:
    """Nullity of L_y(s) at every real s from the characteristic polynomial of the Gram operator over Q[s]."""
    matrix = path_matrix(PATHS[name])
    gram = matrix.T * matrix
    poly = sp.Poly(gram.charpoly(X).as_expr(), X, S)
    by_power: dict[int, sp.Expr] = {}
    for (power, s_power), coefficient in poly.terms():
        by_power[power] = by_power.get(power, sp.Integer(0)) + coefficient * S**s_power
    generic = min(by_power)
    lead = sp.Poly(by_power[generic], S)
    square_free = sp.Poly(sp.gcd(lead, lead.diff(S)), S)
    reduced = sp.Poly(sp.quo(lead, square_free), S)
    rational_roots = sorted(sp.Rational(root) for root in sp.roots(reduced, filter="Q"))
    exceptional = {str(root): DIMENSION - rational_rank(matrix.subs(S, root)) for root in rational_roots}
    orders = {}
    for root in rational_roots:
        order, quotient = 0, lead
        while quotient.eval(root) == 0:
            quotient = sp.Poly(sp.quo(quotient, sp.Poly(S - root, S)), S)
            order += 1
        orders[str(root)] = [order, int(quotient.eval(root))]
    samples = {
        str(value): DIMENSION - rational_rank(matrix.subs(S, value))
        for value in (sp.Rational(-3), sp.Rational(-1, 2), sp.Rational(1, 3), sp.Rational(2), sp.Rational(7, 5))
        if value not in rational_roots
    }
    return {
        "name": name,
        "terms": [list(term) for term in PATHS[name]],
        "generic_nullity": generic,
        "lowest_coefficient": [int(value) for value in lead.all_coeffs()],
        "distinct_real_roots": int(reduced.count_roots()),
        "rational_roots": [str(root) for root in rational_roots],
        "nullity_at_rational_roots": exceptional,
        "order_and_cofactor_of_lowest_coefficient": orders,
        "nullity_at_samples": samples,
    }


def orbit_item(name: str) -> dict[str, Any]:
    point = ORBIT_POINTS[name] if name in ORBIT_POINTS else W8_POINTS[name][0]
    row = hardware_orbits.classify({index: Fraction(value) for index, value in point.items()})
    return {"name": name, "orbit": row["orbit"], "nullity": row["nullity"], "orbit_rank": row["orbit_rank"]}


def limit_projector(name: str) -> tuple[sp.Matrix, dict[str, Any]]:
    certificate = kernel_limits.certify_kernel_limit(path_matrix(PATHS[name]), S, 0)
    projector = sp.Matrix(certificate.limit_projector)
    constant = (sp.Matrix(certificate.projector) - projector).applyfunc(sp.cancel).is_zero_matrix
    return projector, {
        "generic_nullity": certificate.generic_nullity,
        "endpoint_nullity": certificate.endpoint_nullity,
        "exceptional_polynomial": [int(v) for v in sp.Poly(certificate.exceptional_polynomial, S).all_coeffs()],
        "projector_constant_on_branch": bool(constant),
    }


def limits_item(pair: tuple[str, str]) -> dict[str, Any]:
    first, first_row = limit_projector(pair[0])
    second, second_row = limit_projector(pair[1])
    base = left_matrix(DIMENSION, BASE)
    return {
        "paths": list(pair),
        "certificates": [first_row, second_row],
        "product_zero": bool((second * first).is_zero_matrix),
        "sum_rank": int((first + second).rank()),
        "sum_inside_endpoint_kernel": bool((base * (first + second)).is_zero_matrix),
        "projectors_idempotent_of_trace_4": bool(
            first * first == first and second * second == second and first.trace() == 4 and second.trace() == 4
        ),
    }


def kernel_frame(vector: dict[int, int]) -> sp.Matrix:
    return sp.Matrix.hstack(*left_matrix(DIMENSION, vector).nullspace())


def compression_item(name: str) -> dict[str, Any]:
    base, direction = JUNCTIONS[name]
    frame = kernel_frame(base)
    form = frame.T * left_matrix(DIMENSION, direction) * frame
    return {
        "name": name,
        "kernel": frame.cols,
        "compression_rank": int(form.rank()),
        "skew": bool((form + form.T).is_zero_matrix),
    }


def pfaffian(matrix: sp.Matrix) -> sp.Expr:
    size = matrix.rows
    if size == 0:
        return sp.Integer(1)
    total = sp.Integer(0)
    for column in range(1, size):
        if matrix[0, column] != 0:
            keep = [k for k in range(size) if k not in (0, column)]
            total += (-1) ** (column - 1) * matrix[0, column] * pfaffian(matrix.extract(keep, keep))
    return sp.expand(total)


def plane_of(frame: sp.Matrix, form: sp.Matrix) -> sp.Matrix:
    """Orthogonal projector of R^32 onto frame * ker(form)."""
    kernel = frame * sp.Matrix.hstack(*form.nullspace())
    return kernel * (kernel.T * kernel).inv() * kernel.T


def direction_of(u: tuple[int, int, int], v: tuple[int, int, int]) -> dict[int, int]:
    return {**dict(zip(U_UNITS, u, strict=True)), **dict(zip(V_UNITS, v, strict=True))}


def cross(u: tuple[int, int, int], v: tuple[int, int, int]) -> tuple[int, int, int]:
    return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])


def structure_item(job: tuple[int, tuple[tuple[int, int], ...]]) -> dict[str, Any]:
    """Dimension of the compression pencil at a base point, its commutant as an algebra, and its Lie closure.

    job = (dimension of the algebra, base point). The record also holds how the kernel meets the two halves of the
    doubling: the dimensions of its intersections with the lower and the upper half, and whether the two
    intersections are one subspace of the half.

    The operators are the compressions P_0 L_w P_0 written in a kernel frame; the pencil is closed under the adjoint
    of the frame's Gram form, so its commutant is semisimple, and traces and dimensions do not depend on the frame.
    A noncommutative semisimple real
    algebra of dimension 4 is M_2(R) or the quaternions, and the trace form on its traceless part has signature
    (2, 1) on the first and is negative definite on the second.
    """
    dimension, base = job
    frame = sp.Matrix.hstack(*left_matrix(dimension, dict(base)).nullspace())
    size = frame.cols
    gram = frame.T * frame
    inverse = gram.inv()
    operators = [inverse * frame.T * left_matrix(dimension, {w: 1}) * frame for w in range(1, dimension)]
    half = dimension // 2
    lower, upper = frame[:half, :], frame[half:, :]
    in_lower, in_upper = size - upper.rank(), size - lower.rank()
    equal = False
    if in_lower and in_lower == in_upper:
        first = lower * sp.Matrix.hstack(*upper.nullspace())
        second = upper * sp.Matrix.hstack(*lower.nullspace())
        equal = sp.Matrix.hstack(first, second).rank() == in_lower
    rows = sp.Matrix([list(m) for m in operators])
    _, pivots = rows.T.rref()
    basis = [operators[p] for p in pivots]
    unknowns = sp.symbols(f"c0:{size * size}")
    candidate = sp.Matrix(size, size, unknowns)
    equations = [value for m in basis for value in candidate * m - m * candidate if value != 0]
    system = sp.Matrix([[sp.diff(e, c) for c in unknowns] for e in equations])
    commutant = [sp.Matrix(size, size, list(vector)) for vector in system.nullspace()]
    noncommutative = any(not (a * b - b * a).is_zero_matrix for a in commutant for b in commutant)
    traceless = [m - (m.trace() / size) * sp.eye(size) for m in commutant]
    span = sp.Matrix([list(m) for m in traceless])
    _, keep = span.T.rref()
    independent = [traceless[p] for p in keep]
    form = sp.Matrix(len(independent), len(independent), lambda a, b: -(independent[a] * independent[b]).trace())
    positive = all(form[:k, :k].det() > 0 for k in range(1, form.rows + 1))
    closure = list(basis)
    closure_rank = len(basis)
    while True:
        candidates = closure + [a * b - b * a for a in closure for b in closure]
        stacked = sp.Matrix([list(m) for m in candidates])
        _, pivots = stacked.T.rref()
        if len(pivots) == closure_rank:
            break
        closure = [candidates[p] for p in pivots]
        closure_rank = len(pivots)
    return {
        "base": [list(term) for term in base],
        "dimension": dimension,
        "kernel": size,
        "kernel_in_lower_half": int(in_lower),
        "kernel_in_upper_half": int(in_upper),
        "kernel_halves_equal": bool(equal),
        "pencil_dimension": len(basis),
        "commutant_dimension": len(commutant),
        "commutant_noncommutative": bool(noncommutative),
        "commutant_traceless_dimension": len(independent),
        "commutant_trace_form_negative_definite": bool(positive),
        "lie_closure_dimension": closure_rank,
    }


def tangent_cone_item(_: int) -> dict[str, Any]:
    """G of the strata record along y_0 + s w, y_0 = e_1 + e_10, w on the six doubly pure coordinate units.

    With z_k = y_k + i y_(16+k) the direction is zeta = (u1 + i v1, u2 + i v2, u3 + i v3) on (z_1, z_2, z_8).
    """
    s = sp.Symbol("s", real=True)
    u = sp.symbols("u1 u2 u3", real=True)
    v = sp.symbols("v1 v2 v3", real=True)
    z = [sp.Integer(0)] * 16
    z[1], z[10] = sp.Integer(1), sp.Integer(1)
    zeta = [a + sp.I * b for a, b in zip(u, v, strict=True)]
    for index, value in zip((1, 2, 8), zeta, strict=True):
        z[index] += s * value
    uu = sum(z[k] ** 2 for k in range(1, 8))
    vv = sum(z[k] ** 2 for k in range(9, 16))
    uv = sum(z[k] * z[8 + k] for k in range(1, 8))
    g = (uu + z[8] ** 2 + vv) ** 2 - 4 * (uu * vv - uv**2)
    square = sum(value**2 for value in zeta)
    closed = s**2 * square * (4 + 4 * s * zeta[0] + s**2 * square)
    real, imaginary = sp.expand(4 * square).as_real_imag()
    uu0, vv0 = sum(a * a for a in u), sum(b * b for b in v)
    uv0 = sum(a * b for a, b in zip(u, v, strict=True))
    pfaffian_m0 = 16 * ((uu0 + vv0) ** 2 - 4 * (uu0 * vv0 - uv0**2))
    return {
        "g_is_s2_zeta2_times_cofactor": bool(sp.expand(g - closed) == 0),
        "pfaffian_at_m0_is_squared_modulus_of_lead": bool(sp.expand(real**2 + imaginary**2 - pfaffian_m0) == 0),
    }


def clifford_item(base: tuple[tuple[int, int], ...]) -> dict[str, Any]:
    """Three involutions E_k = 2 P(e_k) - I on the kernel, P(n) the limiting plane of normal n, and the identity
    B_w (|u|^2 I + (u x v).E) = 0 modulo the Stiefel ideal (u.v, u.u - v.v) for symbolic (u, v)."""
    frame = kernel_frame(dict(base))
    size = frame.cols
    forms = {w: frame.T * left_matrix(DIMENSION, {w: 1}) * frame for w in (*U_UNITS, *V_UNITS)}

    def form_of(u: Any, v: Any) -> sp.Matrix:
        total = sp.zeros(size, size)
        for w, value in zip((*U_UNITS, *V_UNITS), (*u, *v), strict=True):
            total += value * forms[w]
        return total

    involutions = []
    for u_value, v_value in (((0, 1, 0), (0, 0, 1)), ((0, 0, 1), (1, 0, 0)), ((1, 0, 0), (0, 1, 0))):
        kernel = sp.Matrix.hstack(*form_of(u_value, v_value).nullspace())
        involutions.append(2 * kernel * (kernel.T * kernel).inv() * kernel.T - sp.eye(size))
    relations = 0
    for a in range(3):
        relations += not (involutions[a] - involutions[a].T).is_zero_matrix
        relations += involutions[a].trace() != 0
        for b in range(3):
            anticommutator = involutions[a] * involutions[b] + involutions[b] * involutions[a]
            relations += anticommutator != 2 * int(a == b) * sp.eye(size)
    u = sp.symbols("u1 u2 u3")
    v = sp.symbols("v1 v2 v3")
    normal = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    ideal = sp.groebner(
        [sum(a * b for a, b in zip(u, v, strict=True)), sum(a * a for a in u) - sum(b * b for b in v)],
        *u,
        *v,
        order="grevlex",
    )

    def outside(sign: int) -> int:
        plane = sum(a * a for a in u) * sp.eye(size)
        for coordinate, involution in zip(normal, involutions, strict=True):
            plane += sign * coordinate * involution
        product = form_of(u, v) * plane
        return sum(not ideal.contains(sp.expand(value)) for value in product)

    return {
        "clifford_relation_failures": int(relations),
        "kernel_identity_entries_outside_ideal": outside(1),
        "reversed_normal_entries_outside_ideal": outside(-1),
    }


def integer_nullity(vector: dict[int, int]) -> int:
    rows = [[0] * DIMENSION for _ in range(DIMENSION)]
    for index, value in vector.items():
        for column in range(DIMENSION):
            rows[index ^ column][column] += value * cd_core.cd_sign(DIMENSION, index, column)
    return DIMENSION - int(fmpz_mat(rows).rank())


def four_term_chunk(second: int) -> list[dict[int, int]]:
    """The points e_1 +- e_a +- e_b +- e_c of nullity 8 with a = second < b < c, none of the indices 16: for each
    index triple the first sign pattern of itertools.product((1, -1), repeat=3) that gives nullity 8."""
    points = []
    for pair in combinations(range(second + 1, DIMENSION), 2):
        if 16 in (second, *pair):
            continue
        for signs in product((1, -1), repeat=3):
            vector = dict(zip((1, second, *pair), (1, *signs), strict=True))
            if integer_nullity(vector) == 8:
                points.append(vector)
                break
    return points


def four_term_points() -> list[dict[int, int]]:
    chunks = parallel.ordered_map(four_term_chunk, list(range(2, DIMENSION - 2)), 1)
    return [point for chunk in chunks for point in chunk]


def sampled_item(point: tuple[tuple[int, int], ...]) -> dict[str, Any]:
    row = hardware_orbits.classify({index: Fraction(value) for index, value in point})
    out: dict[str, Any] = {"base": [list(term) for term in point], "orbit": row["orbit"]}
    if row["orbit"] == "W8":
        structure = structure_item((DIMENSION, point))
        out["type"] = [
            structure["kernel_in_lower_half"],
            structure["kernel_in_upper_half"],
            structure["kernel_halves_equal"],
            structure["pencil_dimension"],
            structure["commutant_dimension"],
            structure["lie_closure_dimension"],
        ]
    return out


def sampled_structure() -> dict[str, Any]:
    """Every point of four_term_points, classified; the W8 points among them with their type."""
    points = four_term_points()
    rows = parallel.ordered_map(sampled_item, [tuple(sorted(p.items())) for p in points], 1)
    tally: Counter[str] = Counter()
    for row in rows:
        if "type" in row:
            tally[",".join(str(value) for value in row["type"])] += 1
    return {
        "four_term_nullity_8_points": len(points),
        "sampled": len(rows),
        "orbits": dict(sorted(Counter(row["orbit"] for row in rows).items())),
        "w8_type_tally": dict(sorted(tally.items())),
        "rows": rows,
    }


def split_scan_chunk(first: int) -> list[str]:
    """For q = e_first +- e_j, first < j < 16, a zero divisor of A_4, and lam in (1, 2): the dimension of
    ker L_p n ker L_q in A_4 for p = e_1 + e_10, the nullity of y = (p, lam q) in A_5, and for nullity 8 the orbit
    and, on W8, the commutant dimension; one string per case."""
    p = left_matrix(16, {1: 1, 10: 1})
    rows = []
    for j in range(first + 1, 16):
        for sign in (1, -1):
            q = left_matrix(16, {first: 1, j: sign})
            if q.rank() == 16:
                continue
            common = 16 - sp.Matrix.vstack(p, q).rank()
            for scale in (1, 2):
                vector = {1: 1, 10: 1, 16 + first: scale, 16 + j: scale * sign}
                nullity = integer_nullity(vector)
                label = f"common {common}, nullity {nullity}"
                if nullity == 8:
                    row = sampled_item(tuple(sorted(vector.items())))
                    label += f", {row['orbit']}"
                    if "type" in row:
                        label += f", lower {row['type'][0]}, commutant {row['type'][4]}"
                rows.append(label)
    return rows


def split_scan() -> dict[str, int]:
    chunks = parallel.ordered_map(split_scan_chunk, list(range(1, 15)), 1)
    return dict(sorted(Counter(label for chunk in chunks for label in chunk).items()))


def sign_census_chunk(second: int) -> dict[str, int]:
    """Every signed point e_1 +- e_a +- e_b +- e_c with a = second < b < c, none of the indices 16: the nullity,
    and for nullity 8 the orbit and, on W8, the type of the compression pencil."""
    tally: Counter[str] = Counter()
    for pair in combinations(range(second + 1, DIMENSION), 2):
        if 16 in (second, *pair):
            continue
        for signs in product((1, -1), repeat=3):
            vector = dict(zip((1, second, *pair), (1, *signs), strict=True))
            nullity = integer_nullity(vector)
            label = f"nullity {nullity}"
            if nullity == 8:
                row = sampled_item(tuple(sorted(vector.items())))
                label += f", {row['orbit']}"
                if "type" in row:
                    label += ", type " + ",".join(str(value) for value in row["type"])
            tally[label] += 1
    return dict(tally)


def sign_census() -> dict[str, Any]:
    """The census of all signed four-term points through e_1; a separate record, since it takes CPU minutes."""
    total: Counter[str] = Counter()
    for chunk in parallel.ordered_map(sign_census_chunk, list(range(2, DIMENSION - 2)), 1):
        total.update(chunk)
    result = {"points": sum(total.values()), "tally": dict(sorted(total.items())), "sources": source_digests()}
    w8 = {label: count for label, count in total.items() if ", W8" in label}
    allowed = {"nullity 8, W8, type " + ",".join(str(value) for value in kind) for kind in KINDS.values()}
    require(result["points"] == 29232, "8 sign patterns on each of the 3,654 supports")
    require(set(w8) <= allowed, "every W8 point of the census has one of the three types")
    return result


def vb_pfaffian_item(_: int) -> dict[str, Any]:
    """The Pfaffian of the compression pencil at the VB point e_3 + e_20, by expansion along the first index of each
    index subset, and the orders of Q and G of the strata record on the lines through the point."""
    frame = kernel_frame(STRATA_POINTS["VB e3+e20"])
    size = frame.cols
    forms = {w: frame.T * left_matrix(DIMENSION, {w: 1}) * frame for w in range(1, DIMENSION)}
    nonzero = [w for w in range(1, DIMENSION) if not forms[w].is_zero_matrix]
    _, pivots = sp.Matrix([list(forms[w]) for w in nonzero]).T.rref()
    units = [nonzero[p] for p in pivots]
    symbols = sp.symbols(f"x0:{len(units)}", real=True)
    generic = sp.zeros(size, size)
    for symbol, w in zip(symbols, units, strict=True):
        generic += symbol * forms[w]
    entries = [[sp.Poly(generic[a, b], *symbols) for b in range(size)] for a in range(size)]
    cache: dict[int, Any] = {0: sp.Poly(1, *symbols)}

    def pfaffian_of(mask: int) -> Any:
        if mask not in cache:
            indices = [a for a in range(size) if mask >> a & 1]
            first, total = indices[0], sp.Poly(0, *symbols)
            for position, other in enumerate(indices[1:]):
                term = entries[first][other] * pfaffian_of(mask & ~(1 << first) & ~(1 << other))
                total = total + term if position % 2 == 0 else total - term
            cache[mask] = total
        return cache[mask]

    value = pfaffian_of((1 << size) - 1)
    constant, factors = sp.factor_list(value.as_expr())
    s = sp.Symbol("s", real=True)
    z = [sp.Integer(0)] * 16
    for index, coefficient in STRATA_POINTS["VB e3+e20"].items():
        z[index % 16] += coefficient * (sp.I if index >= 16 else 1)
    for symbol, w in zip(symbols, units, strict=True):
        if w % 16:
            z[w % 16] += s * symbol * (sp.I if w >= 16 else 1)
    uu = sum(z[k] ** 2 for k in range(1, 8))
    vv = sum(z[k] ** 2 for k in range(9, 16))
    uv = sum(z[k] * z[8 + k] for k in range(1, 8))
    q = sp.Poly(sp.expand(uu + z[8] ** 2 + vv), s)
    g = sp.Poly(sp.expand((uu + z[8] ** 2 + vv) ** 2 - 4 * (uu * vv - uv**2)), s)

    def order(poly: Any) -> int:
        return min(power for (power,), coefficient in poly.terms() if sp.expand(coefficient) != 0)

    def modulus_squared(poly: Any) -> Any:
        lead = sp.expand(poly.coeff_monomial(s ** order(poly)))
        real, imaginary = lead.as_real_imag()
        return sp.expand(real**2 + imaginary**2)

    off_domain = [symbol for symbol, w in zip(symbols, units, strict=True) if w % 16 == 0]
    restricted = sp.Poly(value.as_expr().subs(dict.fromkeys(off_domain, 0)), *symbols)
    product_of_moduli = sp.Poly(modulus_squared(q) * modulus_squared(g), *symbols)
    quotient, remainder = sp.div(restricted, product_of_moduli)
    _, restricted_factors = sp.factor_list(restricted.as_expr())

    return {
        "kernel": size,
        "frame_gram_scalar": int((frame.T * frame)[0, 0])
        if frame.T * frame == (frame.T * frame)[0, 0] * sp.eye(size)
        else 0,
        "coordinate_units": units,
        "degree": int(value.total_degree()),
        "terms": len(value.terms()),
        "constant": int(constant),
        "irreducible_factor_degrees": [[int(sp.Poly(f, *symbols).total_degree()), int(m)] for f, m in factors],
        "restricted_to_doubly_pure_terms": len(restricted.terms()),
        "restricted_factor_degrees": sorted(
            [int(sp.Poly(f, *symbols).total_degree()), int(m)] for f, m in restricted_factors
        ),
        "restricted_is_constant_times_moduli_of_leading_forms": bool(
            remainder.is_zero and quotient.total_degree() == 0
        ),
        "restricted_quotient_constant": str(quotient.as_expr()) if remainder.is_zero else "",
        "order_of_q_on_lines": order(q),
        "order_of_g_on_lines": order(g),
    }


def sphere_normal(frame: sp.Matrix, involutions: list[sp.Matrix], projector: sp.Matrix) -> list[str] | None:
    """Coordinates n with 2 P - I = n.E on the kernel, P a projector of R^32 with range in the kernel; None when
    2 P - I lies outside the span of the three involutions."""
    gram = frame.T * frame
    reflection = 2 * gram.inv() * frame.T * projector * frame - sp.eye(frame.cols)
    stacked = sp.Matrix([list(involution) for involution in involutions]).T
    solution = (stacked.T * stacked).inv() * stacked.T * sp.Matrix(list(reflection))
    if not (stacked * solution - sp.Matrix(list(reflection))).is_zero_matrix:
        return None
    return [str(value) for value in solution]


def axis_involutions(frame: sp.Matrix) -> list[sp.Matrix]:
    """E_k = 2 P(e_k) - I in kernel coordinates, P(e_k) the limiting plane of the normal e_k of the u x v space."""
    involutions = []
    for u_value, v_value in (((0, 1, 0), (0, 0, 1)), ((0, 0, 1), (1, 0, 0)), ((1, 0, 0), (0, 1, 0))):
        form = frame.T * left_matrix(DIMENSION, direction_of(u_value, v_value)) * frame
        kernel = sp.Matrix.hstack(*form.nullspace())
        involutions.append(2 * kernel * (kernel.T * kernel).inv() * kernel.T - sp.eye(frame.cols))
    return involutions


def zero_pair_chunk(job: tuple[tuple[int, ...], int]) -> list[tuple[str, tuple[tuple[int, int], ...]]]:
    """Nullities at the CENSUS_PARAMETERS of the lines e_1 + e_10 + s (e_a +- e_b), b > a among the given units."""
    units, a = job
    rows: list[tuple[str, tuple[tuple[int, int], ...]]] = []
    for b in units:
        if b <= a:
            continue
        for sign in (1, -1):
            label = ",".join(str(integer_nullity({**BASE, a: step, b: step * sign})) for step in CENSUS_PARAMETERS)
            rows.append((label, ((a, 1), (b, sign))))
    return rows


def zero_line_limit_item(direction: tuple[tuple[int, int], ...]) -> str:
    """Limiting plane at s = 0 of e_1 + e_10 + s w for a direction w of zero first-order compression, as the
    coordinates of 2 P - I in the three involutions."""
    frame = kernel_frame(BASE)
    terms = ((1, 1, 0), (10, 1, 0), *((w, 0, value) for w, value in direction))
    certificate = kernel_limits.certify_kernel_limit(path_matrix(terms), S, 0)
    require(certificate.generic_nullity == 4, "the line has generic nullity 4")
    normal = sphere_normal(frame, axis_involutions(frame), sp.Matrix(certificate.limit_projector))
    require(normal is None or sum(sp.Rational(value) ** 2 for value in normal) == 1, "a unit normal")
    return "off the span" if normal is None else ",".join(normal)


def arcs_item(_: int) -> dict[str, Any]:
    """Arcs into e_1 + e_10 outside the lines of the six coordinate units: lines along the units of zero
    compression and their signed pairs, and two curved arcs along the conic zeta(t) = (1 - t^2, i (1 + t^2), 2 t)."""
    frame = kernel_frame(BASE)
    forms = {w: frame.T * left_matrix(DIMENSION, {w: 1}) * frame for w in range(1, DIMENSION)}
    involutions = axis_involutions(frame)
    zero_units = [w for w in range(1, DIMENSION) if forms[w].is_zero_matrix]
    unit_census: Counter[str] = Counter()
    for w in zero_units:
        unit_census[",".join(str(integer_nullity({**BASE, w: step})) for step in CENSUS_PARAMETERS)] += 1
    pair_census: Counter[str] = Counter()
    nullity_four: list[tuple[tuple[int, int], ...]] = []
    for chunk in parallel.ordered_map(zero_pair_chunk, [(tuple(zero_units), a) for a in zero_units[:-1]], 1):
        for label, direction in chunk:
            pair_census[label] += 1
            if label == ",".join(["4"] * len(CENSUS_PARAMETERS)):
                nullity_four.append(direction)
    normals: Counter[str] = Counter()
    for normal in parallel.ordered_map(zero_line_limit_item, nullity_four, 1):
        normals[normal] += 1
    curved = []
    for parameter in CONIC_PARAMETERS:
        t = parameter + S
        u_arc, v_arc = (1 - t**2, 0, 2 * t), (0, 1 + t**2, 0)
        coefficients: list[Any] = [sp.Integer(0)] * DIMENSION
        coefficients[1] += 1
        coefficients[10] += 1
        for w, value in zip((*U_UNITS, *V_UNITS), (*u_arc, *v_arc), strict=True):
            coefficients[w] += sp.expand(S * value)
        certificate = kernel_limits.certify_kernel_limit(kernel_limits.cd_polynomial_matrix(coefficients, S), S, 0)
        u0, v0 = (1 - parameter**2, 0, 2 * parameter), (0, 1 + parameter**2, 0)
        expected = [str(sp.Rational(value, sum(a * a for a in u0))) for value in cross(u0, v0)]
        curved.append(
            {
                "parameter": parameter,
                "generic_nullity": certificate.generic_nullity,
                "normal": sphere_normal(frame, involutions, sp.Matrix(certificate.limit_projector)),
                "expected_normal": expected,
            }
        )
    return {
        "zero_compression_units": zero_units,
        "census_parameters": list(CENSUS_PARAMETERS),
        "unit_line_nullity_census": dict(sorted(unit_census.items())),
        "pair_line_nullity_census": dict(sorted(pair_census.items())),
        "nullity_four_pair_lines": len(nullity_four),
        "limit_normals_of_nullity_four_pair_lines": dict(sorted(normals.items())),
        "curved_arcs": curved,
    }


def two_term_chunk(job: tuple[tuple[tuple[int, int], ...], int]) -> tuple[list[int], list[tuple[Any, ...]]]:
    """Compression ranks of the signed two-term directions e_i +- e_j, j > i, at a base point, and the limiting
    plane of each direction of rank 4. job = (base point, i)."""
    base, i = job
    frame = kernel_frame(dict(base))
    first = frame.T * left_matrix(DIMENSION, {i: 1}) * frame
    ranks: list[int] = []
    keys: list[tuple[Any, ...]] = []
    for j in range(i + 1, DIMENSION):
        second = frame.T * left_matrix(DIMENSION, {j: 1}) * frame
        for sign in (1, -1):
            form = first + sign * second
            rank = int(form.rank())
            ranks.append(rank)
            if rank == 4:
                keys.append(tuple(plane_of(frame, form)))
    return ranks, keys


def pencil_item(base: tuple[tuple[int, int], ...]) -> dict[str, Any]:
    """The compression pencil w -> K^T L_w K on the kernel of the base point, K an orthogonal frame."""
    vector = dict(base)
    frame = kernel_frame(vector)
    gram = frame.T * frame
    forms = [frame.T * left_matrix(DIMENSION, {w: 1}) * frame for w in range(DIMENSION)]
    skew_units = [w for w in range(1, DIMENSION) if not forms[w].is_zero_matrix]
    span = sp.Matrix([list(forms[w]) for w in skew_units]).rank()
    units = (*U_UNITS, M_UNIT, *V_UNITS)
    independent = sp.Matrix([list(forms[w]) for w in units]).rank()
    size = frame.cols
    unknowns = sp.symbols(f"c0:{size * size}")
    candidate = sp.Matrix(size, size, unknowns)
    equations: list[sp.Expr] = []
    for w in units:
        operator = gram.inv() * forms[w]
        equations.extend(value for value in candidate * operator - operator * candidate if value != 0)
    commutant = size * size - sp.Matrix([[sp.diff(e, c) for c in unknowns] for e in equations]).rank()
    closure = [gram.inv() * forms[w] for w in units]
    closure_rank = independent
    while True:
        brackets = [a * b - b * a for a in closure for b in closure]
        rank = sp.Matrix([list(m) for m in closure + brackets]).rank()
        if rank == closure_rank:
            break
        stacked = sp.Matrix([list(m) for m in closure + brackets])
        _, pivots = stacked.T.rref()
        closure = [(closure + brackets)[p] for p in pivots]
        closure_rank = rank
    coordinates = sp.symbols("u1 u2 u3 m v1 v2 v3")
    generic = sp.zeros(size, size)
    for symbol, w in zip(coordinates, units, strict=True):
        generic += symbol * forms[w]
    u, m, v = coordinates[:3], coordinates[3], coordinates[4:]
    uu, vv, uv = sum(a * a for a in u), sum(a * a for a in v), sum(a * b for a, b in zip(u, v, strict=True))
    invariant = sp.expand((uu + m * m + vv) ** 2 - 4 * (uu * vv - uv * uv))
    pfaffian_matches = sp.expand(pfaffian(generic) - 16 * invariant) == 0
    census: Counter[int] = Counter()
    planes: dict[tuple[Any, ...], int] = {}
    for ranks, keys in parallel.ordered_map(two_term_chunk, [(base, i) for i in range(1, DIMENSION)], 1):
        census.update(ranks)
        for key in keys:
            planes[key] = planes.get(key, 0) + 1
    projectors = [sp.Matrix(DIMENSION, DIMENSION, list(key)) for key in sorted(planes, key=str)]
    axis_planes = set()
    for u_value, v_value in (((0, 1, 0), (0, 0, 1)), ((0, 0, 1), (1, 0, 0)), ((1, 0, 0), (0, 1, 0))):
        for sign in (1, -1):
            signed = (sign * v_value[0], sign * v_value[1], sign * v_value[2])
            direction = direction_of(u_value, signed)
            form = sum((value * forms[w] for w, value in direction.items()), sp.zeros(size, size))
            axis_planes.add(tuple(plane_of(frame, form)))
    overlaps: Counter[str] = Counter()
    for a in range(len(projectors)):
        for b in range(a + 1, len(projectors)):
            overlaps[str((projectors[a] * projectors[b]).trace())] += 1
    stiefel = []
    stiefel_planes = []
    for u_value, v_value in STIEFEL_PAIRS:
        direction = direction_of(u_value, v_value)
        form = sum((value * forms[w] for w, value in direction.items()), sp.zeros(size, size))
        line = {k: vector.get(k, 0) for k in vector}
        nullities = []
        for step in (1, 2, 3):
            point = dict(line)
            for w, value in direction.items():
                point[w] = point.get(w, 0) + step * value
            nullities.append(DIMENSION - rational_rank(left_matrix(DIMENSION, point)))
        stiefel_planes.append(plane_of(frame, form))
        stiefel.append(
            {
                "u": list(u_value),
                "v": list(v_value),
                "normal": list(cross(u_value, v_value)),
                "compression_rank": int(form.rank()),
                "line_nullity_at_1_2_3": nullities,
            }
        )
    law_failures = 0
    law_pairs = 0
    for a in range(len(STIEFEL_PAIRS)):
        for b in range(a, len(STIEFEL_PAIRS)):
            n1, n2 = cross(*STIEFEL_PAIRS[a]), cross(*STIEFEL_PAIRS[b])
            dot = sum(p * q for p, q in zip(n1, n2, strict=True))
            norms = sum(p * p for p in n1) * sum(q * q for q in n2)
            trace = (stiefel_planes[a] * stiefel_planes[b]).trace()
            # trace = 2 (1 + cos) with cos = dot / sqrt(norms): (trace / 2 - 1)^2 norms = dot^2 with matching sign.
            cosine = trace / 2 - 1
            law_pairs += 1
            law_failures += not (cosine**2 * norms == dot * dot and (cosine * dot >= 0))
    return {
        "base": [list(term) for term in base],
        "kernel": size,
        "frame_gram_scalar": bool(gram == gram[0, 0] * sp.eye(size)),
        "skew_units": skew_units,
        "pencil_dimension": int(span),
        "coordinate_units": list(units),
        "coordinate_units_independent": int(independent),
        "commutant_dimension": int(commutant),
        "lie_closure_dimension": int(closure_rank),
        "pfaffian_is_16_times_invariant": bool(pfaffian_matches),
        "two_term_rank_census": {str(k): census[k] for k in sorted(census)},
        "two_term_limit_planes": len(projectors),
        "two_term_planes_are_the_six_axis_planes": bool(axis_planes == set(planes)),
        "two_term_plane_overlap_traces": {k: overlaps[k] for k in sorted(overlaps)},
        "stiefel": stiefel,
        "same_normal_planes_equal": bool(stiefel_planes[SAME_NORMAL[0]] == stiefel_planes[SAME_NORMAL[1]]),
        "overlap_law_pairs": law_pairs,
        "overlap_law_failures": int(law_failures),
    }


def gram_identity_item(job: tuple[int, int]) -> dict[str, Any]:
    """With J = L_(e_h), h the doubling unit of the level: L_a^T J + J^T L_a = 0 for each imaginary unit a below h
    and J^T J = I, which give the identity for every imaginary a by linearity. job = (dimension, unit for J)."""
    dimension, unit = job
    j = left_matrix(dimension, {unit: 1})
    failures = 0
    for a in range(1, dimension // 2):
        table = left_matrix(dimension, {a: 1})
        failures += not (table.T * j + j.T * table).is_zero_matrix
    return {
        "dimension": dimension,
        "unit": unit,
        "cross_term_failures": failures,
        "unit_gram_identity": bool(j.T * j == sp.eye(dimension)),
    }


def three_form_item(dimension: int) -> dict[str, Any]:
    """phi(i, j, k) = <e_i, e_j e_k> on imaginary units, nonzero only for i = j XOR k, against its transposes."""
    failures = 0
    nonzero = 0
    for j in range(1, dimension):
        for k in range(1, dimension):
            if j == k:
                continue
            i = j ^ k
            value = cd_core.cd_sign(dimension, j, k)
            nonzero += 1
            failures += cd_core.cd_sign(dimension, k, j) != -value
            failures += cd_core.cd_sign(dimension, i, k) != -value
            failures += cd_core.cd_sign(dimension, j, i) != -value
    return {"dimension": dimension, "ordered_unit_pairs": nonzero, "alternation_failures": failures}


def section_item(_: int) -> dict[str, Any]:
    a, b = sp.symbols("a b")
    q = a * a + (sp.I) ** 2 + b * b
    delta = (a * a) * (b * b) - 0
    g = sp.expand(q * q - 4 * delta)
    return {
        "q_matches": bool(sp.expand(q - (a * a + b * b - 1)) == 0),
        "g_matches": bool(sp.expand(g - ((a + b) ** 2 - 1) * ((a - b) ** 2 - 1)) == 0),
    }


def source_digests() -> dict[str, str]:
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCE_FILES}


def structure_ok(row: dict[str, Any]) -> bool:
    return (
        (row["kernel"], row["pencil_dimension"], row["commutant_dimension"], row["lie_closure_dimension"])
        == (8, 7, 4, 10)
        and row["commutant_noncommutative"]
        and row["commutant_traceless_dimension"] == 3
        and row["commutant_trace_form_negative_definite"]
    )


def tower_ok(row: dict[str, Any], kernel: int, pencil: int, closure: int) -> bool:
    return (
        (row["kernel"], row["pencil_dimension"], row["commutant_dimension"], row["lie_closure_dimension"])
        == (kernel, pencil, 4, closure)
        and row["commutant_noncommutative"]
        and row["commutant_trace_form_negative_definite"]
    )


def xor_order(indices: list[int]) -> int:
    group = {0}
    for index in indices:
        group |= {element ^ index for element in group}
    return len(group)


def w8_types(result: dict[str, Any]) -> list[list[Any]]:
    """(lower, upper, equal, pencil, commutant, closure) of every W8 point of the record."""
    named = [
        [
            row["kernel_in_lower_half"],
            row["kernel_in_upper_half"],
            row["kernel_halves_equal"],
            row["pencil_dimension"],
            row["commutant_dimension"],
            row["lie_closure_dimension"],
        ]
        for row in result["structure"]
    ]
    return named + [row["type"] for row in result["sampled_structure"]["rows"] if "type" in row]


KINDS = {"R": [0, 0, False, 7, 1, 28], "C": [2, 2, True, 7, 2, 15], "H": [4, 4, True, 7, 4, 10]}
"""The three types of the compression pencil on W8: kernel in the lower half, in the upper half, the two
intersections equal, pencil dimension, commutant dimension, Lie closure dimension (so(8), su(4), sp(2))."""


def split_rule_holds(result: dict[str, Any]) -> bool:
    return all(kind in KINDS.values() for kind in w8_types(result))


def outcomes(result: dict[str, Any]) -> dict[str, bool]:
    paths = {row["name"]: row for row in result["paths"]}

    def profile(name: str, generic: int, roots: dict[str, int]) -> bool:
        row = paths[name]
        return (
            row["generic_nullity"] == generic
            and row["nullity_at_rational_roots"] == roots
            and row["distinct_real_roots"] == len(roots)
        )

    limits, pencil = result["limits"], result["pencil"]
    structure = dict(zip(W8_POINTS, result["structure"], strict=True))
    return {
        "P1": profile("gamma1", 4, {"0": 8}),
        "P2": profile("gamma2", 8, {"1": 12}),
        "P3": profile("gamma3", 12, {"1": 16}),
        "P4": limits["product_zero"] and limits["sum_rank"] == 8 and "2" in pencil["two_term_plane_overlap_traces"],
        "P5": all(row["compression_rank"] == 4 for row in result["compressions"]),
        "P6": all(r["cross_term_failures"] == 0 and r["unit_gram_identity"] for r in result["gram_identity"]),
        "P7": all(row["alternation_failures"] == 0 for row in result["three_form"]),
        "P8": result["section"]["q_matches"] and result["section"]["g_matches"],
        "P9": structure_ok(structure["e1+e10+e3+e20"]),
        "P10": structure_ok(structure["e17+e26"]) and structure_ok(structure["e1+e10+e4+e15"]),
        "P11": not structure_ok(structure["e1+e10+2(e18-e25)"]),
        "P12": tower_ok(result["tower"][0], 4, 3, 3),
        "P13": tower_ok(result["tower"][1], 16, result["tower"][1]["pencil_dimension"], 36),
        "P14": len(result["vb_pfaffian"]["irreducible_factor_degrees"]) > 1,
        "P15": all(
            (xor_order([term[0] for term in row["base"]]) == 8) == (row["type"][4] == 4)
            for row in result["sampled_structure"]["rows"]
            if "type" in row
        ),
        "P16": all(
            arc["generic_nullity"] == 4 and arc["normal"] == arc["expected_normal"]
            for arc in result["arcs"]["curved_arcs"]
        ),
        "P17": split_rule_holds(result),
        "P18": result["vb_pfaffian"]["restricted_is_constant_times_moduli_of_leading_forms"],
        "P19": not any("common 2" in label and "W8" in label for label in result["split_scan"]),
    }


def build_result() -> dict[str, Any]:
    result: dict[str, Any] = {
        "convention": parallel.ordered_map(convention_item, [8, 16, 32], 1),
        "paths": parallel.ordered_map(path_item, list(PATHS), 1),
        "orbits": parallel.ordered_map(orbit_item, list(ORBIT_POINTS), 1),
        "structure_orbits": parallel.ordered_map(orbit_item, list(W8_POINTS), 1),
        "limits": limits_item(("gamma1", "beta")),
        "compressions": parallel.ordered_map(compression_item, list(JUNCTIONS), 1),
        "pencil": pencil_item(tuple(sorted(BASE.items()))),
        "structure": parallel.ordered_map(
            structure_item, [(DIMENSION, tuple(sorted(point.items()))) for point, _ in W8_POINTS.values()], 1
        ),
        "sampled_structure": sampled_structure(),
        "tower": parallel.ordered_map(structure_item, [(16, BASE_KEY), (64, BASE_KEY)], 1),
        "strata_pencils": parallel.ordered_map(
            structure_item, [(DIMENSION, tuple(sorted(point.items()))) for point in STRATA_POINTS.values()], 1
        ),
        "vb_pfaffian": vb_pfaffian_item(0),
        "arcs": arcs_item(0),
        "split_scan": split_scan(),
        "tangent_cone": tangent_cone_item(0),
        "clifford": clifford_item(tuple(sorted(BASE.items()))),
        "gram_identity": parallel.ordered_map(gram_identity_item, [(16, 8), (32, 16), (64, 32)], 1),
        "three_form": parallel.ordered_map(three_form_item, [8, 16, 32, 64], 1),
        "section": section_item(0),
        "predictions": PREDICTIONS,
        "sources": source_digests(),
    }
    result["prediction_held"] = outcomes(result)
    return result


def validate(result: dict[str, Any]) -> None:
    require(all(row["mismatches"] == 0 for row in result["convention"]), "cd_core differs from the doubling formula")
    for row in result["paths"]:
        generic, roots = PATH_EXPECTED[row["name"]]
        require(row["generic_nullity"] == generic, f"{row['name']}: generic nullity")
        require(row["nullity_at_rational_roots"] == roots, f"{row['name']}: exceptional parameters")
        require(row["distinct_real_roots"] == len(roots), f"{row['name']}: a real exceptional root is irrational")
        require(set(row["nullity_at_samples"].values()) == {generic}, f"{row['name']}: sample nullity")
    for row in result["orbits"]:
        require((row["orbit"], row["nullity"]) == ORBIT_EXPECTED[row["name"]], f"orbit of {row['name']}")
    limits = result["limits"]
    require(limits["product_zero"] and limits["sum_rank"] == 8, "limiting planes are orthogonal complements")
    require(limits["sum_inside_endpoint_kernel"], "limit planes in the kernel")
    require(limits["projectors_idempotent_of_trace_4"], "each limit is an orthogonal projector of rank 4")
    for row in limits["certificates"]:
        require((row["generic_nullity"], row["endpoint_nullity"]) == (4, 8), "limit certificate nullities")
        require(row["projector_constant_on_branch"], "the projector is constant on the punctured branch")
        require(row["exceptional_polynomial"] == [1, 0, 1, 0], "exceptional polynomial s^3 + s")
    require([row["dimension"] for row in result["convention"]] == [8, 16, 32], "convention levels")
    require([row["name"] for row in result["paths"]] == list(PATHS), "the four paths")
    require([row["name"] for row in result["orbits"]] == list(ORBIT_POINTS), "the seven orbit points")
    require([row["kernel"] for row in result["compressions"]] == [8, 12, 16, 16], "junction kernels")
    for row in result["compressions"]:
        require(row["compression_rank"] == 4 and row["skew"], f"compression at {row['name']}")
    pencil = result["pencil"]
    require(pencil["kernel"] == 8 and pencil["frame_gram_scalar"], "kernel frame of the base point")
    require(pencil["pencil_dimension"] == 7 and pencil["coordinate_units_independent"] == 7, "pencil dimension")
    require(pencil["commutant_dimension"] == 4, "commutant of the pencil")
    require(pencil["lie_closure_dimension"] == 10, "Lie closure of the pencil")
    require(pencil["pfaffian_is_16_times_invariant"], "Pfaffian of the pencil")
    require(pencil["coordinate_units"] == [1, 2, 8, 16, 17, 18, 24], "coordinate units of the pencil")
    require(pencil["skew_units"] == [1, 2, 8, 9, 10, 16, 17, 18, 24, 25, 26], "units with a nonzero form")
    require(len(pencil["stiefel"]) == len(STIEFEL_PAIRS) == 10, "ten Stiefel directions")
    require(pencil["two_term_planes_are_the_six_axis_planes"], "the six two-term planes are the axis planes")
    require(len(result["structure"]) == len(result["structure_orbits"]) == len(W8_POINTS) == 10, "ten W8 points")
    for (name, (_, kind)), row, orbit in zip(
        W8_POINTS.items(), result["structure"], result["structure_orbits"], strict=True
    ):
        require((orbit["orbit"], orbit["nullity"], orbit["orbit_rank"]) == ("W8", 8, 12), f"{name} lies in W8")
        found = [
            row["kernel_in_lower_half"],
            row["kernel_in_upper_half"],
            row["kernel_halves_equal"],
            row["pencil_dimension"],
            row["commutant_dimension"],
            row["lie_closure_dimension"],
        ]
        require(found == KINDS[kind], f"{name}: type {kind}")
        require(row["commutant_trace_form_negative_definite"], f"{name}: commutant is a division algebra")
        require(row["commutant_noncommutative"] == (kind == "H"), f"{name}: commutativity of the commutant")
        require(row["commutant_traceless_dimension"] == KINDS[kind][4] - 1, f"{name}: traceless part")
    for row in result["paths"]:
        orders = row["order_and_cofactor_of_lowest_coefficient"]
        require(all(order == 8 for order, _ in orders.values()), "junction order 8")
        require({cofactor for _, cofactor in orders.values()} == {JUNCTION_COFACTORS[row["name"]]}, "cofactor")
        require(set(orders) == set(PATH_EXPECTED[row["name"]][1]), "one order per exceptional parameter")
    lower, upper = result["tower"]
    require(tower_ok(lower, 4, 3, 3) and lower["dimension"] == 16, "A_4: kernel 4, pencil 3, closure 3")
    require(tower_ok(upper, 16, 15, 36) and upper["dimension"] == 64, "A_6: kernel 16, pencil 15, closure 36")
    require((upper["kernel_in_lower_half"], upper["kernel_halves_equal"]) == (8, True), "A_6 kernel splits")
    require(split_rule_holds(result), "kernel split decides the pencil type on every W8 point of the record")
    sampled = result["sampled_structure"]
    require(sampled["four_term_nullity_8_points"] == sampled["sampled"] == 474, "every four-term point classified")
    require(sampled["orbits"] == {"Ehat": 18, "Iso": 120, "W8": 312, "Xm": 6, "Xp": 18}, "orbits of the points")
    require(sampled["w8_type_tally"] == {"0,0,False,7,1,28": 240, "4,4,True,7,4,10": 72}, "types of the points")
    witnesses = {
        (xor_order([term[0] for term in row["base"]]), row["type"][4]) for row in sampled["rows"] if "type" in row
    }
    require({(8, 1), (16, 4)} <= witnesses, "the XOR-order rule fails in both directions")
    require(
        result["split_scan"]
        == {
            "common 0, nullity 0": 62,
            "common 0, nullity 4": 22,
            "common 0, nullity 8, Iso": 36,
            "common 0, nullity 8, W8, lower 0, commutant 1": 36,
            "common 2, nullity 12": 4,
            "common 2, nullity 8, W8, lower 2, commutant 2": 4,
            "common 4, nullity 16": 1,
            "common 4, nullity 8, W8, lower 4, commutant 4": 3,
        },
        "split scan over the two-term zero divisors q of A_4",
    )
    strata = dict(zip(STRATA_POINTS, result["strata_pencils"], strict=True))
    for name, expected in (("VB e3+e20", (12, 9, 1, 66)), ("N- gamma3(1)", (16, 19, 1, 120))):
        row = strata[name]
        seen = (row["kernel"], row["pencil_dimension"], row["commutant_dimension"], row["lie_closure_dimension"])
        require(seen == expected, f"pencil at {name}")
    plus, minus = strata["N+ gamma3(-1)"], strata["N- gamma3(1)"]
    same = ("kernel", "pencil_dimension", "commutant_dimension", "lie_closure_dimension", "kernel_in_lower_half")
    require(all(plus[key] == minus[key] for key in (*same, "kernel_in_upper_half", "kernel_halves_equal")), "N+, N-")
    require((minus["kernel_in_lower_half"], minus["kernel_halves_equal"]) == (4, True), "N- kernel meets each half")
    vb = result["vb_pfaffian"]
    require((vb["kernel"], vb["degree"], vb["terms"]) == (12, 6, 50), "VB Pfaffian shape")
    require(vb["frame_gram_scalar"] == 2, "the VB kernel frame has Gram 2 I")
    require(vb["irreducible_factor_degrees"] == [[6, 1]] and vb["constant"] == -(vb["frame_gram_scalar"] ** 6), "VB")
    require((vb["order_of_q_on_lines"], vb["order_of_g_on_lines"]) == (1, 2), "orders of Q and G at the VB point")
    require(vb["coordinate_units"][-1] == 16 and vb["restricted_to_doubly_pure_terms"] == 16, "VB restriction")
    require(vb["restricted_factor_degrees"] == [[2, 1], [2, 1], [2, 1]], "three quadratic factors over Q")
    require(vb["restricted_is_constant_times_moduli_of_leading_forms"], "VB Pfaffian on the doubly pure coordinates")
    require(vb["restricted_quotient_constant"] == "-1", "constant of the VB identity")
    arcs = result["arcs"]
    require(arcs["census_parameters"] == [3, 5], "census parameters")
    require(len(arcs["zero_compression_units"]) == 20 and arcs["unit_line_nullity_census"] == {"0,0": 20}, "units")
    require(arcs["pair_line_nullity_census"] == {"0,0": 200, "4,4": 20, "8,8": 160}, "zero-compression pair lines")
    require(arcs["limit_normals_of_nullity_four_pair_lines"] == {"0,0,-1": 10, "0,0,1": 10}, "second-order limits")
    require(len(arcs["curved_arcs"]) == len(CONIC_PARAMETERS), "curved arcs")
    for arc in arcs["curved_arcs"]:
        require(arc["generic_nullity"] == 4 and arc["normal"] == arc["expected_normal"], "curved arc limit")
    cone = result["tangent_cone"]
    require(cone["g_is_s2_zeta2_times_cofactor"], "closed form of G on the lines through the base point")
    require(cone["pfaffian_at_m0_is_squared_modulus_of_lead"], "Pfaffian at m = 0 from the leading form of G")
    clifford = result["clifford"]
    require(clifford["clifford_relation_failures"] == 0, "three anticommuting symmetric traceless involutions")
    require(clifford["kernel_identity_entries_outside_ideal"] == 0, "kernel identity on the Stiefel cone")
    require(clifford["reversed_normal_entries_outside_ideal"] > 0, "the reversed normal fails the identity")
    require(pencil["two_term_rank_census"] == {"0": 384, "4": 32, "8": 514}, "two-term rank census")
    require(pencil["two_term_limit_planes"] == 6, "two-term limiting planes")
    require(pencil["two_term_plane_overlap_traces"] == {"0": 3, "2": 12}, "two-term plane overlaps")
    for row in pencil["stiefel"]:
        require(row["compression_rank"] == 4, "a Stiefel direction has compression rank 4")
        require(row["line_nullity_at_1_2_3"] == [4, 4, 4], "a Stiefel line has nullity 4 at s = 1, 2, 3")
    require(pencil["same_normal_planes_equal"], "the limiting plane depends on u x v alone")
    require(pencil["overlap_law_failures"] == 0 and pencil["overlap_law_pairs"] == 55, "overlap law")
    require([row["dimension"] for row in result["gram_identity"]] == [16, 32, 64], "Gram identity levels")
    require([row["dimension"] for row in result["three_form"]] == [8, 16, 32, 64], "three-form levels")
    for row in result["gram_identity"]:
        require(row["cross_term_failures"] == 0 and row["unit_gram_identity"], "Gram identity")
    for row in result["three_form"]:
        require(row["alternation_failures"] == 0, "alternating three-form")
        dimension = row["dimension"]
        require(row["ordered_unit_pairs"] == (dimension - 1) * (dimension - 2), "three-form support count")
    require(result["section"]["q_matches"] and result["section"]["g_matches"], "section of Q and G")
    held = result["prediction_held"]
    require(set(held) == set(PREDICTIONS), "one outcome per prediction")
    require({name for name, value in held.items() if not value} == FAILED_PREDICTIONS, "recorded prediction outcomes")


def self_test() -> list[str]:
    """Each mutant changes an input and must fail for the named reason."""
    messages = []
    global PATHS  # noqa: PLW0603
    saved = dict(PATHS)
    try:
        PATHS = {**saved, "gamma1": ((1, 1, 0), (10, 1, 0), (9, 0, 1), (27, 0, 1))}
        row = path_item("gamma1")
        require(row["generic_nullity"] == 0, "the path through e9 + e27 leaves the zero-divisor variety")
        messages.append("mutant direction e9 + e27: generic nullity 0")
        PATHS = {**saved, "beta": saved["gamma1"]}
        row = limits_item(("gamma1", "beta"))
        require(not row["product_zero"] and row["sum_rank"] == 4, "one path twice gives one plane")
        messages.append("mutant pair (gamma1, gamma1): product nonzero, sum rank 4")
    finally:
        PATHS = saved
    row = gram_identity_item((32, 26))
    require(row["cross_term_failures"] > 0, "a unit other than the doubling unit breaks the cross term")
    messages.append(f"mutant J = L_(e_26): {row['cross_term_failures']} cross-term failures")
    bad = doubled_product([0, 1, 0, 0], [0, 0, 1, 0])
    require(bad[3] == cd_core.cd_sign(4, 1, 2) and bad[3] != cd_core.cd_sign(4, 2, 1), "product order matters")
    messages.append("mutant operand order: sign differs")
    form = kernel_frame(BASE).T * left_matrix(DIMENSION, direction_of((1, 0, 0), (1, 0, 0))) * kernel_frame(BASE)
    require(int(form.rank()) == 8, "a parallel pair (u = v) has compression rank 8")
    messages.append(f"mutant parallel pair u = v: compression rank {int(form.rank())}")
    frame = kernel_frame(BASE)
    involutions = axis_involutions(frame)
    stiefel_form = frame.T * left_matrix(DIMENSION, direction_of((0, 1, 0), (0, 0, 1))) * frame
    require(sphere_normal(frame, involutions, plane_of(frame, stiefel_form)) == ["1", "0", "0"], "axis plane e_1")
    half = frame[:, :4]
    coordinate_plane = half * (half.T * half).inv() * half.T
    require(sphere_normal(frame, involutions, coordinate_plane) is None, "a 4-plane off the sphere is reported")
    messages.append("mutant plane (first four frame vectors): outside the span of the involutions")
    require(xor_order([1, 12, 13, 30]) == 8 and xor_order([1, 2, 11, 12]) == 16, "XOR orders of the two witnesses")
    witness = sampled_item(((1, 1), (12, 1), (13, 1), (30, 1)))
    require(witness["orbit"] == "W8" and witness["type"][4] == 1, "an order-8 W8 point with scalar commutant")
    messages.append("witness e1 + e12 + e13 + e30: XOR order 8, W8, commutant 1 (refutes the XOR rule)")
    witness = sampled_item(((1, 1), (2, 1), (11, 1), (12, 1)))
    require(witness["orbit"] == "W8" and witness["type"] == KINDS["H"], "an order-16 W8 point of type H")
    messages.append("witness e1 + e2 + e11 + e12: XOR order 16, W8, type H (refutes the XOR rule)")
    row = structure_item((DIMENSION, ((1, 1), (10, 1), (20, 1), (31, 1))))
    require(row["kernel"] == 12, "the scale 1 on the complex-type line gives nullity 12, outside W8")
    messages.append("mutant scale 1 in e1 + e10 + lam (e20 + e31): kernel 12")
    row = structure_item((DIMENSION, ((3, 1), (20, 1))))
    require(not structure_ok(row) and row["kernel"] == 12, "the VB point e_3 + e_20 has another pencil")
    messages.append(
        f"mutant base e3 + e20: kernel {row['kernel']}, pencil {row['pencil_dimension']}, "
        f"commutant {row['commutant_dimension']}, closure {row['lie_closure_dimension']}"
    )
    return messages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path, help="write the record")
    mode.add_argument("--check", type=Path, help="recompute and compare with a written record")
    mode.add_argument("--self-test", action="store_true", help="run the mutation controls")
    mode.add_argument("--sign-census", type=Path, help="write the census of all signed four-term points")
    mode.add_argument("--check-sign-census", type=Path, help="recompute the sign census and compare")
    arguments = parser.parse_args()
    if arguments.self_test:
        for message in self_test():
            print(message)
        return 0
    if arguments.sign_census is not None or arguments.check_sign_census is not None:
        census_text = json.dumps(sign_census(), indent=1, sort_keys=True) + "\n"
        if arguments.sign_census is not None:
            arguments.sign_census.write_text(census_text, encoding="utf-8")
            return 0
        matches = arguments.check_sign_census.read_text(encoding="utf-8") == census_text
        require(matches, "the recomputed sign census differs from the file")
        return 0
    result = build_result()
    validate(result)
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if arguments.out is not None:
        arguments.out.write_text(text, encoding="utf-8")
        return 0
    require(arguments.check.read_text(encoding="utf-8") == text, "the recomputed record differs from the file")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
