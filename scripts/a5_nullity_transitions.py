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
from pathlib import Path
from typing import Any

import sympy as sp
from flint import fmpq, fmpq_mat

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
W8_POINTS: dict[str, tuple[dict[int, int], bool]] = {
    "e1+e10": ({1: 1, 10: 1}, True),
    "e1-e10": ({1: 1, 10: -1}, True),
    "e17+e26": ({17: 1, 26: 1}, True),
    "e1+e10+e4+e15": ({1: 1, 10: 1, 4: 1, 15: 1}, True),
    "e1+e10+e17+e26": ({1: 1, 10: 1, 17: 1, 26: 1}, True),
    "e1+e10+2(e18-e25)": ({1: 1, 10: 1, 18: 2, 25: -2}, True),
    "e1+e10+e3+e20": ({1: 1, 10: 1, 3: 1, 20: 1}, False),
    "2(e1+e10)+e3+e20": ({1: 2, 10: 2, 3: 1, 20: 1}, False),
}
"""Points of the orbit W8 with the type of the compression pencil: True for a quaternion commutant with Lie closure
of dimension 10, False for a scalar commutant with Lie closure of dimension 28."""
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


def structure_item(base: tuple[tuple[int, int], ...]) -> dict[str, Any]:
    """Dimension of the compression pencil at a base point, its commutant as an algebra, and its Lie closure.

    The operators are the compressions P_0 L_w P_0 written in a kernel frame; the pencil is closed under the adjoint
    of the frame's Gram form, so its commutant is semisimple, and traces and dimensions do not depend on the frame.
    A noncommutative semisimple real
    algebra of dimension 4 is M_2(R) or the quaternions, and the trace form on its traceless part has signature
    (2, 1) on the first and is negative definite on the second.
    """
    frame = kernel_frame(dict(base))
    size = frame.cols
    gram = frame.T * frame
    inverse = gram.inv()
    operators = [inverse * frame.T * left_matrix(DIMENSION, {w: 1}) * frame for w in range(1, DIMENSION)]
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
        "kernel": size,
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
    for i in range(1, DIMENSION):
        for j in range(i + 1, DIMENSION):
            for sign in (1, -1):
                form = forms[i] + sign * forms[j]
                rank = int(form.rank())
                census[rank] += 1
                if rank == 4:
                    key = tuple(plane_of(frame, form))
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
            structure_item, [tuple(sorted(point.items())) for point, _ in W8_POINTS.values()], 1
        ),
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
    require(len(result["structure"]) == len(result["structure_orbits"]) == len(W8_POINTS) == 8, "eight W8 points")
    for (name, (_, quaternionic)), row, orbit in zip(
        W8_POINTS.items(), result["structure"], result["structure_orbits"], strict=True
    ):
        require((orbit["orbit"], orbit["nullity"], orbit["orbit_rank"]) == ("W8", 8, 12), f"{name} lies in W8")
        if quaternionic:
            require(structure_ok(row), f"{name}: quaternion commutant and Lie closure of dimension 10")
        else:
            scalar = (row["kernel"], row["pencil_dimension"], row["commutant_dimension"]) == (8, 7, 1)
            require(scalar and row["lie_closure_dimension"] == 28, f"{name}: scalar commutant and closure so(8)")
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
    failed = {"P3": False, "P9": False, "P11": False}
    require(held == {**dict.fromkeys(PREDICTIONS, True), **failed}, "recorded prediction outcomes")


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
    row = structure_item(((3, 1), (20, 1)))
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
    arguments = parser.parse_args()
    if arguments.self_test:
        for message in self_test():
            print(message)
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
