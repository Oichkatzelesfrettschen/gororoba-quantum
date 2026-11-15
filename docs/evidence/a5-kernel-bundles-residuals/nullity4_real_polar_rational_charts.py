"""Rational charts of G_2(C) at the polar normal form of V(G) minus V(Q): the pairing rank is 0 or 2 on each.

Setting (nullity4_real_polar_fiber_four.py, ff). z_0 = (e_1; 5 i; 3 e_1 + 5 e_2) is the normal form (s, v_1, mu) =
(4, 3, 5 i), l its polar plane and C = C(l) = span(k_0, k_1, k_2), a space that holds z_0 (z_0 = i k_0 + 3 k_1 +
5 k_2 in the primitive basis of polar()). For g in G_2(C) and Pi = g^* g the point z = g z_0 has kernel plane g l
exactly when F = z_0^* Pi l vanishes, and then dim L = 2 (3 - rank R) with R = [k_0, k_1, k_2]^* Pi l (3 x 2; where
F = 0 its rank is the rank of the pairing N of ff, because F is a combination of the rows of R). At Pi = 1 both F
and R vanish: z_0 is a
point with dim L = 6. A point with dim L = 4 needs F = 0 and rank R = 1; ff certifies one by an interval box and
holds no exact point. This file records two exact searches for one and the certificate at two further precisions.

1. Stabilizers (exact over Q(i)). In g_2(C) the stabilizer of z_0, the setwise stabilizer of l and the setwise
   stabilizer of C are one subalgebra of dimension 3, and z_0^* X l = 0 and C^* X l = 0 for each X of a basis. A
   chart inside a stabilizer, where the equations would be holomorphic, therefore does not leave R = 0 at first
   order.
2. Root subgroups. Among the elements D_a + sign i D_b (a < b, sign = +-1) of g_2(C), 100 are nilpotent. For
   g = exp(t X), Pi = exp(conj(t) X^*) exp(t X) is a polynomial in t and conj(t); F vanishes identically for 24 of
   them, and R vanishes identically for each of those 24. For each of the other 76, t = 0 is the only complex number
   with F(t, conj(t)) = 0: a lexicographic Groebner basis of the real and imaginary parts of F in (Re t, Im t) has
   a univariate member whose only real root is 0, and at Im t = 0 the only common real root is Re t = 0. So no
   root subgroup holds a point with F = 0 other than the points with R = 0.
3. Boost families. For the pair (4, 7), and for the pair (5, 6), the reflections sigma (+1 on e_1, e_2, e_3) and tau
   (-1 on e_1, e_2 and the pair) lie in G_2, and the elements of g_2 that commute with tau and anticommute with sigma
   are spanned by L_1, L_2 (zero on the three +1 directions of tau, with n_L^2 = -1 on the other four for
   n_L = c_L L_1 + s_L L_2, c_L^2 + s_L^2 = 1) and R_1, R_2 (n_R^2 = -1 on the four and n_R^3 = -4 n_R on the three).
   L_j and R_k commute. With C^2 - S^2 = 1 the matrices A_L = P_3 + P_4 (C_L + i S_L n_L) and
   A_R = P_4 (C_R + i S_R n_R) + P_3 (1 + i S_R C_R n_R - S_R^2 n_R^2 / 2) are exp(i theta n) with C = cosh theta,
   S = sinh theta, so C is at least 1: Hermitian elements of G_2(C), rational for rational (c, s, C, S), with
   M(g t) = g M(t) g^T for g = diag(A, 1, A) checked as an identity modulo the two relations. For g = A_L A_R and
   Pi = g^2 the
   2 x 2 minor of R on the rows k_1, k_2 is a nonzero constant times S_R^2 (S_R^2 + 1) (2 S_L^2 + 1)^2, so
   rank R = 2 unless S_R = 0; at S_R = 0 the two entries of F are C_L S_L times two linear forms in (c_L, s_L)
   whose squares sum to a positive constant, so F = 0 forces S_L = 0, the identity. On each family a point with
   F = 0 has rank R = 0 (the identity) or 2: dim L = 6 or 2, never 4. A point with dim L = 4 needs a Hermitian
   element outside these two four-parameter families.
4. Precision. The Krawczyk test of ff (same midpoint, radius 2^-24) is repeated at 131 and 400 bits with the
   precision passed to every evaluation; it gives the same containment, contraction and pairing bound as at 200
   bits. The exact pairing factors are built first, since ff sets its own precision when it builds them, and each
   evaluation checks the context precision at its end. This removes the dependence of the certificate on one working
   precision, not on python-flint.

Evidence classes. Items 1 to 3 are exact over Q(i) or over the polynomial ring in (c, s, C, S) modulo the two
relations; item 4 is a certified interval statement. The searches are bounded negatives: they exclude an exact point
in these charts and say nothing about other charts.

--write writes nullity4-real-polar-rational-charts-result.json beside this file; --check recomputes and compares.

Run from the repository root:
"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_real_polar_rational_charts.py --check
"""

from __future__ import annotations

import argparse
import copy
import functools
import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any

import sympy as sp
from flint import acb_mat, arb, arb_mat, ctx
from sympy import QQ_I
from sympy.polys.matrices import DomainMatrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(HERE))

import nullity4_orbit_normal_forms as forms  # noqa: E402
import nullity4_real_polar_fiber_four as ff  # noqa: E402
import nullity4_real_polar_line as real_line  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-bundles-residuals-nullity4-real-polar-rational-charts-v1"
RECORD = HERE / "nullity4-real-polar-rational-charts-result.json"
SOURCE_PATHS = (
    HERE / "nullity4_real_polar_rational_charts.py",
    HERE / "nullity4_real_polar_fiber_four.py",
    HERE / "nullity4_real_polar_line.py",
    HERE / "nullity4_orbit_normal_forms.py",
)
FIELD = "Q(i) and Q(i)[c, s, C, S] modulo c^2 + s^2 = 1, C^2 - S^2 = 1; arb balls at the listed precisions"
IU = sp.I
CL, SL, CR, SR = sp.symbols("cL sL cR sR", real=True)
CHL, SHL, CHR, SHR = sp.symbols("CL SL CR SR", real=True)

STABILIZERS = {"point": 3, "plane": 3, "common_kernel": 3, "span": 3, "first_order_vanishes": True}
ROOT_SUBGROUPS = {
    "candidates": 182,
    "nilpotent": 100,
    "incidence_zero": 24,
    "pairing_zero_among_them": 24,
    "incidence_only_at_origin": 76,
}
# Each generator as a list of (a, b, value): the skew 7 x 7 matrix with entry value at (a, b), 1-based.
FAMILIES: dict[str, dict[str, Any]] = {
    "4, 7": {
        "four": [1, 2, 4, 7],
        "L": [[(1, 4, 1), (2, 7, 1)], [(1, 7, 1), (2, 4, -1)]],
        "R": [[(1, 7, 1), (2, 4, 1), (3, 5, 2)], [(1, 4, -1), (2, 7, 1), (3, 6, 2)]],
    },
    "5, 6": {
        "four": [1, 2, 5, 6],
        "L": [[(1, 6, 1), (2, 5, 1)], [(1, 5, -1), (2, 6, 1)]],
        "R": [[(1, 6, 1), (2, 5, -1), (3, 4, 2)], [(1, 5, 1), (2, 6, 1), (3, 7, -2)]],
    },
}
STRUCTURE_KEYS = ("in_g2", "commute", "left", "right", "hermitian", "equivariant")
# A rational point of each family: (c, s) = (3/5, 4/5) and (C, S) = (5/3, 4/3) on both factors.
INSTANCE = {"c": "3/5", "s": "4/5", "C": "5/3", "S": "4/3"}
FAMILY_FACTS: dict[str, dict[str, Any]] = {
    "4, 7": {
        "structure": dict.fromkeys(STRUCTURE_KEYS, True),
        "minor": "400*SR**2*(2*SL**2 + 1)**2*(SR**2 + 1)",
        "incidence_at_SR_zero": ["-2*I*CL*SL*(7*cL + 24*sL)", "2*I*CL*SL*(24*cL - 7*sL)"],
        "sum_of_squares": "625",
        "instance": [True, True, False, 2],
    },
    "5, 6": {
        "structure": dict.fromkeys(STRUCTURE_KEYS, True),
        "minor": "400*SR**2*(2*SL**2 + 1)**2*(SR**2 + 1)",
        "incidence_at_SR_zero": ["10*CL*SL*(4*cL - 3*sL)", "10*CL*SL*(3*cL + 4*sL)"],
        "sum_of_squares": "25",
        "instance": [True, True, False, 2],
    },
}
PRECISIONS = (131, 400)
KRAWCZYK = {"interior": True, "contraction_bits": ff.CONTRACTION_BITS, "pairing_bound_bits": ff.PAIRING_BOUND_BITS}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _rank(rows: list[list[Any]]) -> int:
    return int(DomainMatrix.from_Matrix(sp.Matrix(rows).applyfunc(sp.expand)).convert_to(QQ_I).rank())


def _primitive(vector: list[Any]) -> list[Any]:
    """The vector over the positive greatest common divisor of the real and imaginary parts of its entries."""
    content = sp.gcd([part(entry) for entry in vector for part in (sp.re, sp.im)])
    _require(content != 0, "the vector is zero")
    return [sp.expand(entry / content) for entry in vector]


@functools.cache
def polar() -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    """z_0 (15 x 1), the polar plane l (15 x 2) and a primitive basis of C(l) (15 x 3) at the normal form of ff."""
    s, v1, mu = ff.CONE_POINT
    z0, line, kernel = real_line.polar_data(ff.SIGMA, s, v1, mu * IU)
    _require(len(line) == 2 and len(kernel) == 3, "the polar data have other dimensions")
    _require(_rank([*kernel, z0]) == 3, "z_0 is outside C(l)")
    return sp.Matrix(z0), sp.Matrix(line).T, sp.Matrix([_primitive(row) for row in kernel]).T


@functools.cache
def derivations() -> tuple[sp.Matrix, ...]:
    return tuple(ff._derivations())


def _derivation_image(job: tuple[int, tuple[Any, ...]]) -> list[Any]:
    """D_k v for the job (k, v)."""
    k, vector = job
    return list(derivations()[k] * sp.Matrix(list(vector)))


def _combination_rows(vectors: sp.Matrix, target: sp.Matrix | None) -> list[list[Any]]:
    """Rows of the linear system sum x_k D_k v_i = sum a_ij w_j over the columns v_i of vectors, w_j of target."""
    rows = []
    width = 0 if target is None else target.cols
    count = len(derivations())
    for i in range(vectors.cols):
        column = tuple(vectors[:, i])
        images = parallel.ordered_map(_derivation_image, [(k, column) for k in range(count)], min_items=2)
        for r in range(15):
            extra = [0] * (vectors.cols * width)
            if target is not None:
                for j in range(width):
                    extra[i * width + j] = -target[r, j]
            rows.append([image[r] for image in images] + extra)
    return rows


def _stabilizer(vectors: sp.Matrix, setwise: bool) -> list[sp.Matrix]:
    """A basis of the X = sum x_k D_k with X v = 0 (pointwise) or X span(v) inside span(v) (setwise)."""
    rows = _combination_rows(vectors, vectors if setwise else None)
    null = DomainMatrix.from_Matrix(sp.Matrix(rows).applyfunc(sp.expand)).convert_to(QQ_I).nullspace().to_Matrix()
    basis = []
    for r in range(null.rows):
        matrix = sp.zeros(15, 15)
        for k, d in enumerate(derivations()):
            matrix += null[r, k] * d
        basis.append(matrix.applyfunc(sp.expand))
    return basis


def stabilizer_facts() -> dict[str, Any]:
    """The dimensions of item 1, the dimension of the span of the three stabilizers, and the first-order pairings."""
    z0, line, kernel = polar()
    groups = parallel.ordered_map(_stabilizer_job, ["point", "plane", "common_kernel"], min_items=2)
    union = [list(matrix) for group in groups for matrix in group]
    first = all(
        not any((z0.H * x * line).applyfunc(sp.expand)) and not any((kernel.H * x * line).applyfunc(sp.expand))
        for x in groups[1]
    )
    return {
        "point": len(groups[0]),
        "plane": len(groups[1]),
        "common_kernel": len(groups[2]),
        "span": _rank(union),
        "first_order_vanishes": first,
    }


def _stabilizer_job(name: str) -> list[sp.Matrix]:
    z0, line, kernel = polar()
    if name == "point":
        return _stabilizer(z0, setwise=False)
    _require(name in ("plane", "common_kernel"), f"unknown stabilizer {name}")
    return _stabilizer(line if name == "plane" else kernel, setwise=True)


ROOT_JOBS = tuple((a, b, sign) for a, b in itertools.combinations(range(14), 2) for sign in (1, -1))


def _origin_is_the_only_real_zero(polynomials: list[Any], a: sp.Symbol, b: sp.Symbol) -> bool:
    """Whether (0, 0) is the only real common zero of the polynomials in (a, b), all of which vanish there.

    Certificate: a lexicographic Groebner basis for a > b holds members in b alone whose greatest common divisor
    has the single real root 0, and the members at b = 0 have a greatest common divisor in a with the single real
    root 0. False when the basis has no member in b alone or when every member vanishes at b = 0.
    """
    nonzero = [p for p in polynomials if p != 0]
    if not nonzero or any(p.subs({a: 0, b: 0}) != 0 for p in nonzero):
        return False
    basis = [sp.expand(p) for p in sp.groebner(nonzero, a, b, order="lex").exprs]
    in_b = [sp.Poly(p, b) for p in basis if p.free_symbols <= {b}]
    if not in_b:
        return False
    common_b = functools.reduce(sp.gcd, in_b)
    if set(sp.real_roots(common_b)) != {sp.Integer(0)}:
        return False
    at_zero = [sp.Poly(p.subs(b, 0), a) for p in basis if p.subs(b, 0) != 0]
    if not at_zero:
        return False
    return set(sp.real_roots(functools.reduce(sp.gcd, at_zero))) <= {sp.Integer(0)}


def root_subgroup(job: tuple[int, int, int]) -> list[bool] | None:
    """For X = D_a + sign i D_b: None when X is not nilpotent, else three facts of g = exp(t X).

    Whether F vanishes identically in t; whether R does; and, when F does not, whether t = 0 is the only complex
    number with F(t, conj(t)) = 0 (False when F vanishes identically).
    """
    a, b, sign = job
    x = derivations()[a] + sign * IU * derivations()[b]
    t, tb = sp.symbols("t tb")
    power, order = x, 1
    g, gs = sp.eye(15) + t * x, sp.eye(15) + tb * x.H
    while order < 15 and any(power):
        power = (power * x).applyfunc(sp.expand)
        order += 1
        g += t**order * power / sp.factorial(order)
        gs += tb**order * power.H / sp.factorial(order)
    if any(power):
        return None
    z0, line, kernel = polar()
    pi = gs * g
    incidence = (z0.H * pi * line).applyfunc(sp.expand)
    identically_zero = not any(incidence)
    isolated = False
    if not identically_zero:
        re, im = sp.symbols("re im", real=True)
        parts = [
            part
            for entry in incidence
            for part in sp.expand(entry.subs({t: re + IU * im, tb: re - IU * im})).as_real_imag()
        ]
        isolated = _origin_is_the_only_real_zero([sp.expand(part) for part in parts], re, im)
    return [identically_zero, not any((kernel.H * pi * line).applyfunc(sp.expand)), isolated]


def root_subgroup_tally() -> dict[str, int]:
    rows = [row for row in parallel.ordered_map(root_subgroup, list(ROOT_JOBS), min_items=2) if row is not None]
    return {
        "candidates": len(ROOT_JOBS),
        "nilpotent": len(rows),
        "incidence_zero": sum(row[0] for row in rows),
        "pairing_zero_among_them": sum(row[0] and row[1] for row in rows),
        "incidence_only_at_origin": sum(not row[0] and row[2] for row in rows),
    }


def _skew(entries: list[tuple[int, int, int]]) -> sp.Matrix:
    matrix = sp.zeros(7, 7)
    for a, b, value in entries:
        matrix[a - 1, b - 1] = value
        matrix[b - 1, a - 1] = -value
    return matrix


def _reduced(expression: Any) -> Any:
    """The normal form modulo sL^2 = 1 - cL^2, sR^2 = 1 - cR^2, CL^2 = 1 + SL^2, CR^2 = 1 + SR^2."""
    relations = {SL**2: 1 - CL**2, SR**2: 1 - CR**2, CHL**2: 1 + SHL**2, CHR**2: 1 + SHR**2}
    polynomial = sp.Poly(sp.expand(expression), SL, SR, CHL, CHR)
    result = sp.Integer(0)
    for (e_sl, e_sr, e_chl, e_chr), coefficient in polynomial.terms():
        term = coefficient * relations[SL**2] ** (e_sl // 2) * SL ** (e_sl % 2)
        term *= relations[SR**2] ** (e_sr // 2) * SR ** (e_sr % 2)
        term *= relations[CHL**2] ** (e_chl // 2) * CHL ** (e_chl % 2)
        term *= relations[CHR**2] ** (e_chr // 2) * CHR ** (e_chr % 2)
        result += term
    return sp.expand(result)


@functools.cache
def _family(name: str) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix, list[sp.Matrix]]:
    """n_L, n_R, the projections P_4 and P_3 and the four generators of the family."""
    _require(name in FAMILIES, f"unknown family {name}")
    data = FAMILIES[name]
    generators = [_skew(entries) for entries in [*data["L"], *data["R"]]]
    p4 = sp.diag(*[1 if index + 1 in data["four"] else 0 for index in range(7)])
    n_left = CL * generators[0] + SL * generators[1]
    n_right = CR * generators[2] + SR * generators[3]
    return n_left, n_right, p4, sp.eye(7) - p4, generators


@functools.cache
def _hermitian_element(name: str) -> sp.Matrix:
    """A = A_L A_R of item 3 as a 7 x 7 matrix in (c, s, C, S)."""
    n_left, n_right, p4, p3, _ = _family(name)
    a_left = p3 + p4 * (CHL * sp.eye(7) + IU * SHL * n_left)
    a_right = p4 * (CHR * sp.eye(7) + IU * SHR * n_right)
    a_right += p3 * (sp.eye(7) + IU * SHR * CHR * n_right - (SHR**2 / 2) * n_right * n_right)
    return (a_left * a_right).applyfunc(_reduced)


def family_structure(name: str) -> dict[str, bool]:
    """Per STRUCTURE_KEYS: generators in g_2; L_j, R_k commute; minimal polynomials; A Hermitian; A equivariant."""
    n_left, n_right, p4, p3, generators = _family(name)
    small = [matrix[0:7, 0:7] for matrix in derivations()]
    flat = sp.Matrix([list(matrix) for matrix in small])
    in_g2 = all(sp.Matrix.vstack(flat, sp.Matrix([list(g)])).rank() == 14 for g in generators)
    commute = all(
        not any(generators[i] * generators[j] - generators[j] * generators[i]) for i in (0, 1) for j in (2, 3)
    )
    zero = sp.zeros(7, 7)
    left = (n_left * p3).applyfunc(_reduced) == zero and (p4 * n_left * n_left + p4).applyfunc(_reduced) == zero
    right = (p4 * n_right * n_right + p4).applyfunc(_reduced) == zero
    right = right and (p3 * (n_right**3 + 4 * n_right)).applyfunc(_reduced) == zero
    a = _hermitian_element(name)
    g = sp.diag(a, sp.Matrix([[1]]), a)
    t = sp.Matrix(sp.symbols("t1:16"))
    moved = forms.block(list(g * t), forms.ALL, forms.ALL)
    difference = (moved - g * forms.block(list(t), forms.ALL, forms.ALL) * g.T).applyfunc(_reduced)
    values = (in_g2, commute, left, right, (a - a.H).applyfunc(_reduced) == zero, not any(difference))
    return dict(zip(STRUCTURE_KEYS, [bool(value) for value in values], strict=True))


@functools.cache
def _pairings(name: str) -> tuple[sp.Matrix, sp.Matrix]:
    """F = z_0^* Pi l (1 x 2) and R = C^* Pi l (3 x 2) for Pi = diag(A^2, 1, A^2)."""
    z0, line, kernel = polar()
    a = _hermitian_element(name)
    square = (a * a).applyfunc(_reduced)
    pi = sp.diag(square, sp.Matrix([[1]]), square)
    return (z0.H * pi * line).applyfunc(_reduced), (kernel.H * pi * line).applyfunc(_reduced)


def family_minor(name: str) -> str:
    """The 2 x 2 minor of R on the rows of k_1 and k_2 of the primitive basis of C(l), factored."""
    _, r = _pairings(name)
    return str(sp.factor(_reduced(r[1, 0] * r[2, 1] - r[1, 1] * r[2, 0])))


def family_incidence_at_zero(name: str) -> list[str]:
    """The two entries of F at S_R = 0 (C_R = 1), factored."""
    f, _ = _pairings(name)
    return [str(sp.factor(entry.subs({SHR: 0, CHR: 1}))) for entry in f]


def family_sum_of_squares(name: str) -> str:
    """The sum of the squares of the two linear forms in (c_L, s_L) of F at S_R = 0, reduced."""
    f, _ = _pairings(name)
    forms_ = [sp.cancel(entry.subs({SHR: 0, CHR: 1}) / (CHL * SHL)) for entry in f]
    total = sum(sp.expand(form * sp.conjugate(form)) for form in forms_)
    constants = {"4, 7": 4, "5, 6": 100}
    return str(_reduced(total) / constants[name])


def family_instance(name: str) -> list[Any]:
    """At the rational point INSTANCE: equivariance of diag(A, 1, A), Hermitian, F = 0, and the rank of R."""
    values = {key: sp.Rational(value) for key, value in INSTANCE.items()}
    point = {CL: values["c"], SL: values["s"], CR: values["c"], SR: values["s"]}
    point.update({CHL: values["C"], SHL: values["S"], CHR: values["C"], SHR: values["S"]})
    a = _hermitian_element(name).subs(point).applyfunc(sp.expand)
    g = sp.diag(a, sp.Matrix([[1]]), a)
    t = sp.Matrix(sp.symbols("t1:16"))
    moved = forms.block(list(g * t), forms.ALL, forms.ALL)
    difference = (moved - g * forms.block(list(t), forms.ALL, forms.ALL) * g.T).applyfunc(sp.expand)
    f, r = _pairings(name)
    return [
        not any(difference),
        not any((a - a.H).applyfunc(sp.expand)),
        not any(f.subs(point).applyfunc(sp.expand)),
        _rank(r.subs(point).tolist()),
    ]


FAMILY_JOBS = tuple((name, part) for name in FAMILIES for part in FAMILY_FACTS["4, 7"])


def family_fact(job: tuple[str, str]) -> Any:
    name, part = job
    parts = {
        "structure": family_structure,
        "minor": family_minor,
        "incidence_at_SR_zero": family_incidence_at_zero,
        "sum_of_squares": family_sum_of_squares,
        "instance": family_instance,
    }
    _require(part in parts, f"unknown fact {part}")
    return parts[part](name)


def family_record() -> dict[str, dict[str, Any]]:
    values = parallel.ordered_map(family_fact, list(FAMILY_JOBS), min_items=2)
    record: dict[str, dict[str, Any]] = {name: {} for name in FAMILIES}
    for (name, part), value in zip(FAMILY_JOBS, values, strict=True):
        record[name][part] = value
    return record


def evaluation_at(job: tuple[int, int, int]) -> tuple[list[Any], list[Any]]:
    """The evaluation of ff at the precision of the job (precision, radius_bits, k), serialized."""
    precision, radius_bits, k = job
    _require(precision >= 64, f"the precision {precision} is below 64 bits")
    # ff._pairing_factors sets the context to ff.PRECISION on its first call in a process; its balls are exact.
    z, line = ff._pairing_factors()
    ctx.prec = precision
    exponential = ff._block_matrix(ff._slice_point(ff.MIDPOINT, radius_bits), k).exp()
    pi = acb_mat([[exponential[a, b] for b in range(15)] for a in range(15)])
    derivative = acb_mat([[exponential[a, 15 + b] for b in range(15)] for a in range(15)])
    values = ff._ser_matrix(z * pi * line), ff._ser_matrix(z * derivative * line)
    _require(ctx.prec == precision, "the working precision changed during the evaluation")
    return values


def krawczyk_at(precision: int) -> dict[str, Any]:
    """The Krawczyk test of ff.krawczyk at the box of ff, with every evaluation at the given precision."""
    radius_bits = ff.RADIUS_BITS
    _require(radius_bits >= 1, "the radius selects the point evaluation")
    free = ff.SLICE_FREE
    jobs = [(precision, 0, k) for k in free] + [(precision, radius_bits, k) for k in free]
    rows = parallel.ordered_map(evaluation_at, jobs, min_items=2)
    ff._pairing_factors()
    ctx.prec = precision
    count = len(free)
    f0, j0 = ff._equations(ff._de_matrix(rows[0][0]), [ff._de_matrix(rows[k][1]) for k in range(count)])
    box_t = ff._de_matrix(rows[count][0])
    _, jx = ff._equations(box_t, [ff._de_matrix(rows[count + k][1]) for k in range(count)])
    inverse = arb_mat([[j0[a][b].mid() for b in range(count)] for a in range(count)]).inv().mid()
    radius = ff._dyadic(1, radius_bits)
    identity = arb_mat([[arb(1 if a == b else 0) for b in range(count)] for a in range(count)])
    offset = arb_mat([[arb(0, radius)] for _ in range(count)])
    image = -(inverse * arb_mat([[v] for v in f0])) + (identity - inverse * arb_mat(jx)) * offset
    interior = all(image[c, 0].lower() > -radius and image[c, 0].upper() < radius for c in range(count))
    worst = max((image[c, 0].abs_upper() for c in range(count)), key=lambda x: float(x.mid()))
    entry = box_t[ff.PAIRING_ENTRY[0] + 1, ff.PAIRING_ENTRY[1]].abs_lower()
    result = {
        "interior": bool(interior),
        "contraction_bits": ff._largest_power(worst / radius, True, 200) if interior else 0,
        "pairing_bound_bits": ff._largest_power(entry, False, 300),
    }
    _require(ctx.prec == precision, "the working precision changed during the Krawczyk test")
    return result


def precision_record() -> dict[str, dict[str, Any]]:
    return {
        str(p): row
        for p, row in zip(PRECISIONS, parallel.ordered_map(krawczyk_at, list(PRECISIONS), min_items=2), strict=True)
    }


def _inputs() -> dict[str, str]:
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS}


def compute() -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "stabilizers": stabilizer_facts(),
        "root_subgroups": root_subgroup_tally(),
        "families": family_record(),
        "instance": dict(INSTANCE),
        "precisions": precision_record(),
        "pass": True,
    }
    record["pass"] = verdict(record) == []
    return record


def expected_record() -> dict[str, Any]:
    """The record that the constants of this module determine, with the digests of the files as they are."""
    return {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "stabilizers": dict(STABILIZERS),
        "root_subgroups": dict(ROOT_SUBGROUPS),
        "families": copy.deepcopy(FAMILY_FACTS),
        "instance": dict(INSTANCE),
        "precisions": {str(p): dict(KRAWCZYK) for p in PRECISIONS},
        "pass": True,
    }


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes. The comparison is on serialized text."""
    expected = expected_record()
    problems = []
    messages = {
        "inputs": "the input digests differ from the files",
        "stabilizers": "the stabilizers of z_0, l and C(l) are not one subalgebra of dimension 3 with zero pairings",
        "root_subgroups": "the tally of the root subgroups differs",
        "families": "a boost family has a minor, an incidence form or an instance other than the pinned one",
        "precisions": "the Krawczyk test differs at a second precision",
    }
    for group, message in messages.items():
        if json.dumps(record.get(group), sort_keys=True) != json.dumps(expected[group], sort_keys=True):
            problems.append(message)
    if record.get("pass") is not True:
        problems.append("the record states that it fails")
    if not problems and _serialized(record) != _serialized(expected):
        problems.append("the record differs from the record the constants determine")
    return problems


def _serialized(record: dict[str, Any]) -> str:
    """The retained text of a record. The replay compares text, so true and 1, which compare equal, differ."""
    return json.dumps(record, indent=1, sort_keys=True) + "\n"


def main() -> None:
    """Write the record with --write, or recompute and compare its text with --check."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    record = compute()
    if args.write:
        RECORD.write_text(_serialized(record), encoding="utf-8")
    elif RECORD.read_text(encoding="utf-8") != _serialized(record):
        raise SystemExit(f"{RECORD.name} differs from the recomputation")
    problems = verdict(record)
    if problems:
        raise SystemExit("\n".join(problems))
    print(f"pass: {len(record['families'])} boost families, {len(record['precisions'])} further precisions")


if __name__ == "__main__":
    main()
