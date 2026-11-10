"""Exact limits of ker L_a along the arcs of the fiber track (ledger A5-272 to A5-275 and A5-292).

An arc x(s) of the slice of an incidence is completed by the producer's eliminated slice variables, mapped to the 32
coordinates of A_5 and fed to the left-multiplication matrix of cd_core. The kernel of L_x(s) over the field of
Laurent series has dimension 8, and its saturation in k[[s]]^32 reduced modulo s is the limiting plane. Elimination
over the discrete valuation ring k[[s]] with pivots of least valuation and column operations only keeps the
transformation unimodular, so the columns left without a pivot form a saturated basis of the kernel and their
constant terms span the limit. The series are truncated at the order of the family and the pivot valuations sum to
less than it, so the constant terms of the truncated transformation equal those of the exact one. The kernel
dimension is at least 8 because the arc lies on the slice (J vanishes on it to the truncation order), and at most 8
by the 24 pivots.

Families: the arcs Phi of ../arcs-x on X+ -> N- and X- -> N+ over F_32009, F_32029 and Q (an arc with rational
coefficients is a real arc), and the first-order and order-5 families of ../arcs on E8-bar -> N- and E8-bar -> N+
over the two prime fields (their t8 coordinate carries the square root of -1); the blowup arcs of
../structure/arcs-iso-w8/blowup-arcs on Iso and on the degree-30 component of W8, and the weighted arcs of
../arcs-x-same on X- -> N- and X+ -> N+, over both prime fields and Q; the linear family of ../structure/arcs-iso-w8
on the degree-20 component of W8 over the two prime fields. Arcs are grouped by the projective
limit y of the header's G (by the parameter point over Q, where no header exists); the record states whether
each group has one limiting plane and how many planes the groups give.

Run from the repository root: "$PYTHON" docs/evidence/a5-exceptional-fibers/kernel-limits/plucker_limits.py FAMILY
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE.parent / "a5-kernel-attachments"))
sys.path.insert(0, str(EVIDENCE.parents[2] / "gororoba_quantum"))

import fiber_inputs  # noqa: E402
import nullity16_basepoints as basepoints  # noqa: E402
import nullity16_rees_fibers as rees  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "a5-kernel-plucker-limits-v2"
INPUTS = EVIDENCE / "working" / "build" / "inputs"
DIM = 32
SOURCE_NULLITY = 8
PRIMES = {32009: 10754, 32029: 9115}
# slug: (incidence, sign s9 of the t9 coordinate of the parametrization)
X_INCIDENCES = {"xp-nm": ("X+->N-", 1), "xm-np": ("X-->N+", -1)}
E8_INCIDENCES = {"e8-nm": ("E8bar->N-", 1), "e8-np": ("E8bar->N+", -1)}
ISO_INCIDENCES = {"iso-nm": ("Iso->N-", 1), "iso-np": ("Iso->N+", 1)}
W8_INCIDENCES = {"w8-nm": ("W8->N-", 1), "w8-np": ("W8->N+", -1)}
XS_INCIDENCES = {"xm-nm": ("X-->N-", 1), "xp-np": ("X+->N+", -1)}
INCIDENCES = X_INCIDENCES | E8_INCIDENCES | ISO_INCIDENCES | W8_INCIDENCES | XS_INCIDENCES
X_ORDER = 12
E8_ORDER = 48
ISO_ORDER = 32
W8_ORDER = 32
XS_ORDER = 40
# X arcs: w = W s + W2 s^2, rho = R s + R2 s^2, sig = S s + S2 s^2, s1 = K s + K2 s^2, as (W, R, S) and
# (K, W2, R2, S2, K2).
X_DIRECTIONS = ((1, 0, 0), (1, 1, 0), (1, 0, 1), (1, 2, 3), (1, -1, 2), (2, 1, 1), (2, 3, -1), (3, 1, 5), (1, 4, -3))
X_VARIANTS = ((0, 0, 0, 0, 0), (1, 0, 0, 0, 0), (5, 0, 0, 0, 7), (-2, 3, -1, 4, 1))
# E8-bar arcs (W, R, S, Z, E) of ../arcs: the first-order family (limit order 2, dense in V(P2)) and the order-5
# family at the conic point e = -1 (dense in V(P1)). A variant adds (W', R', S', Z', E') one order above each leading
# term of the family, and a second set two orders above.
E8_POINTS = (
    (1, 2, 1, 4, 2),
    (3, 5, 6, 11, 3),
    (7, 13, 19, 4, 5),
    (1, 5, 19, 11, 10),
    (3, 2, 6, 4, 23),
    (7, 5, 1, 11, 3),
)
E8_VARIANTS = (
    ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0)),
    ((2, -1, 3, 5, 1), (0, 0, 0, 0, 0)),
    ((0, 0, 0, 0, 0), (4, 1, -2, 3, 6)),
    ((-3, 2, 1, -1, 2), (1, 5, 2, -4, 3)),
)

# Iso arcs of ../structure/arcs-iso-w8/blowup-arcs: the point (b, c) of P(L0), the contact parameters (V, A), and a
# variant (r3, r4) that adds r3 s^3 + r4 s^4 to R and keeps the limit of G.
ISO_POINTS = (
    (2, 3, 5, 7),
    (13, 4, 9, 6),
    (2, 3, 5, -4),
    (2, 3, 1, 7),
    (5, 3, 5, 7),
    (2, -7, 5, 7),
    (1, 1, 1, 1),
    (3, -2, 4, 11),
    (7, 5, -3, 2),
)
ISO_VARIANTS = ((0, 0), (5, 0), (0, -3), (2, 9))

# W8 arcs. "c30": the blowup arcs of ../structure/arcs-iso-w8/blowup-arcs at (b, c, V, A, B), which sweep the
# degree-30 component and have rational coefficients; a variant adds (r3, p3) s^3 to the chart coordinates R and P.
# "c20": the linear family a = s, c = C s, d = D s, t7 = T s, t1 = U s, t9 = V s of ../structure/arcs-iso-w8 at
# (C, D, T, U, V), which sweeps the degree-20 component and carries the square root of -1; a variant adds
# (c2, d2) s^2 to c and d.
W8_POINTS = {
    "c30": ((2, 3, 5, 7, 11), (13, 4, 9, 6, 17), (2, 3, 5, -4, 1), (5, 3, 1, 7, 2), (2, -7, 5, 7, 3), (1, 1, 1, 1, 1)),
    "c20": ((2, 3, 5, 7, 11), (13, 4, 9, 6, 17), (1, 2, 3, 4, 5), (3, -2, 4, 11, 7), (7, 5, -3, 2, 1), (1, 1, 1, 1, 1)),
}
W8_VARIANTS = ((0, 0), (5, 0), (0, -3), (2, 9))

# Same-sign X arcs of ../arcs-x-same: w = W s^2, rho = R s, sig = S s, a = A s at (W, R, S, A); a variant adds
# (w', r', s', a') two orders above each leading term.
XS_POINTS = (
    (2, 3, 5, 7),
    (13, 4, 9, 6),
    (1, 1, 1, 1),
    (1, 2, -3, 4),
    (3, -1, 2, 5),
    (2, 3, 5, -4),
    (5, 3, 1, 7),
    (2, -7, 5, 3),
    (7, 5, -3, 2),
)
XS_VARIANTS = ((0, 0, 0, 0), (5, 0, 0, 0), (0, 2, -3, 1), (2, 9, 4, -1))

Scalar = Any  # int modulo a prime, or Fraction
Vector = tuple[Scalar, ...]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


@dataclass(frozen=True)
class Field:
    """F_prime, or Q when prime is None, with power series known modulo s^order."""

    prime: int | None
    order: int

    def scalar(self, value: Fraction | int) -> Scalar:
        fraction = Fraction(value)
        if self.prime is None:
            return fraction
        return fraction.numerator * pow(fraction.denominator, -1, self.prime) % self.prime

    def inverse(self, value: Scalar) -> Scalar:
        return 1 / value if self.prime is None else pow(value, -1, self.prime)


class Series:
    """Truncated power series over a Field."""

    __slots__ = ("c", "f")

    def __init__(self, coefficients: Vector, field: Field) -> None:
        self.f = field
        padded = tuple(coefficients[: field.order]) + (0,) * (field.order - len(coefficients))
        self.c: Vector = tuple(field.scalar(v) for v in padded)

    def _lift(self, other: Series | int | Fraction) -> Series:
        return other if isinstance(other, Series) else Series((other,), self.f)

    def __add__(self, other: Series | int | Fraction) -> Series:
        return Series(tuple(a + b for a, b in zip(self.c, self._lift(other).c, strict=True)), self.f)

    __radd__ = __add__

    def __neg__(self) -> Series:
        return Series(tuple(-a for a in self.c), self.f)

    def __sub__(self, other: Series | int | Fraction) -> Series:
        return self + (-self._lift(other))

    def __rsub__(self, other: Series | int | Fraction) -> Series:
        return (-self) + other

    def __mul__(self, other: Series | int | Fraction) -> Series:
        right = self._lift(other).c
        order = self.f.order
        out = [0] * order
        for i, a in enumerate(self.c):
            if a:
                for j in range(order - i):
                    out[i + j] += a * right[j]
        return Series(tuple(out), self.f)

    __rmul__ = __mul__

    def __pow__(self, exponent: int) -> Series:
        out = Series((1,), self.f)
        for _ in range(exponent):
            out = out * self
        return out

    def valuation(self) -> int:
        return next((k for k, v in enumerate(self.c) if v), self.f.order)

    def shift(self, k: int) -> Series:
        """self / s^k for k at most the valuation."""
        return Series(self.c[k:], self.f)

    def inverse(self) -> Series:
        """Inverse of a unit."""
        lead = self.f.inverse(self.c[0])
        out = [lead]
        for n in range(1, self.f.order):
            out.append(self.f.scalar(-lead * sum(self.c[k] * out[n - k] for k in range(1, n + 1))))
        return Series(tuple(out), self.f)


def monomials(field: Field, *coefficients: int, start: int = 1) -> Series:
    """coefficients[0] s^start + coefficients[1] s^(start + 1) + ..."""
    return Series((0,) * start + coefficients, field)


def evaluate(text: str, values: dict[str, Series], field: Field) -> Series:
    """Evaluate a polynomial in Singular notation at series; I is the field's square root of -1."""
    names = tuple(values)
    polynomial = sympy.Poly(sympy.parse_expr(text.replace("^", "**")), *sympy.symbols(names))
    total = Series((), field)
    for exponents, coefficient in polynomial.terms():
        term = Series((Fraction(int(coefficient.p), int(coefficient.q)),), field)
        for name, exponent in zip(names, exponents, strict=True):
            if exponent:
                term = term * values[name] ** exponent
        total = total + term
    return total


def header(slug: str, prime: int) -> tuple[tuple[str, ...], list[str], list[str]]:
    """Variables, J and G of the retained header."""
    lines = (INPUTS / f"p{prime}-r{PRIMES[prime]}" / f"{slug}.sing").read_text(encoding="utf-8").splitlines()
    _require(lines[1] == f"number I={PRIMES[prime]};", f"{slug}: header root differs")
    variables = tuple(lines[0].split("(")[1].split(")")[0].split(","))
    ideal_j, ideal_g = (line.split("=", 1)[1].rstrip(";").split(",") for line in lines[2:4])
    return variables, ideal_j, ideal_g


def slice_data(slug: str, field: Field) -> dict[str, Any]:
    """Base point, slice columns and the producer's eliminated slice variables, over F_prime or over Q(i)."""
    task = fiber_inputs._task(INCIDENCES[slug][0])
    base = rees._base_task(task)
    data = basepoints._schur_coordinates(base)
    root = PRIMES[field.prime] if field.prime else None
    lines = (
        *rees._local_germ_lines(root, task, data, field.prime or rees.MODULAR_PRIME),
        'LIB "presolve.lib";',
        "list EP=elimpart(J);",
        'for(int i=1;i<=nvars(basering);i++){"RESULT ep_"+string(i),EP[5][i];}',
        "quit;",
    )
    outcome = rees._run_singular("\n".join(lines), "eliminated_slice_variables", 900)
    _require(outcome.status == "completed", f"{slug} elimpart {outcome.status}: {outcome.diagnostic}")
    substitutions = {name: outcome.results[f"ep_{i}"] for i, name in enumerate(data.slice_names, start=1)}
    _require(all("I" not in text for text in substitutions.values()), f"{slug}: a substitution involves I")
    kept = tuple(name for name, text in substitutions.items() if text == name)
    _require(
        kept == header(slug, next(iter(PRIMES)))[0], f"{slug}: kept slice variables {kept} differ from the header's"
    )
    return {
        "slug": slug,
        "prime": field.prime,
        "order": field.order,
        "boundary_point": [str(value) for value in base.boundary_point],
        "slice_columns": list(data.slice_columns),
        "slice_names": list(data.slice_names),
        "substitutions": substitutions,
    }


def x_arc(field: Field, sign: int, parameters: tuple[tuple[int, ...], ...]) -> dict[str, Series]:
    """Phi of ../arcs-x."""
    (big_w, big_r, big_s), (k1, w2, r2, s2, k2) = parameters
    w, rho, sig, s1 = (monomials(field, a, b) for a, b in ((big_w, w2), (big_r, r2), (big_s, s2), (k1, k2)))
    half = Fraction(1, 2)
    m = w + 1
    u = m.inverse()
    t9xp = -(w * w) * u * half
    return {
        "t1": s1,
        "t2": w * (w + 2) * u * half * (s1 - t9xp + 2),
        "t4": (m * rho + sig) * half,
        "t5": (m * rho - sig) * half,
        "t6": (m * sig + rho) * half,
        "t7": (rho - m * sig) * half,
        "t9": t9xp * sign,
    }


def e8_arc(field: Field, sign: int, parameters: tuple[Any, ...]) -> dict[str, Series]:
    """Phi of ../arcs on the first-order family ("p2") or the order-5 family at e = -1 ("p1")."""
    family, (big_w, big_r, big_s, big_z, big_e), (first, second) = parameters
    _require(field.prime is not None, "the E8-bar arcs carry the square root of -1")
    extra = tuple(zip(first, second, strict=True))
    if family == "p2":
        w, rho, sigma, zeta = (monomials(field, a, *extra[i]) for i, a in enumerate((big_w, big_r, big_s, big_z)))
        e = Series((big_e, *extra[4]), field)
    else:
        w = monomials(field, big_w, *extra[0], start=2)
        rho = monomials(field, big_r + big_s, *extra[1]) * Fraction(1, 2)
        sigma = monomials(field, big_r - big_s, *extra[2]) * Fraction(1, 2)
        zeta = monomials(field, big_z, *extra[3])
        e = Series((-1, 0, big_e, *extra[4]), field)
    return e8_phi(field, sign, w, rho, sigma, zeta, e)


def iso_arc(field: Field, sign: int, parameters: tuple[tuple[int, ...], ...]) -> dict[str, Series]:
    """The blowup arcs of the Iso slice: Q = t4 + t6 = 2 b s, T = t5 + t7 = 2 c s, t2 = b V s^2,
    R = t5 - t7 = s (b^2 V s + b A s^2 + r3 s^3 + r4 s^4) and P = t4 - t6 = (R T - t2^2) / Q, which solves
    J = t2^2 + P Q - R T. sign = -1 reverses the t2^2 term, so the mutated arc leaves V(J)."""
    (b, c, big_v, big_a), (r3, r4) = parameters
    half = Fraction(1, 2)
    s = monomials(field, 1)
    t2 = monomials(field, b * big_v, start=2)
    q, t = s * (2 * b), s * (2 * c)
    r = monomials(field, b * b * big_v, b * big_a, r3, r4, start=2)
    p = (r * (2 * c) - t2.shift(1) * t2 * sign) * Fraction(1, 2 * b)
    return {"t2": t2, "t3": s, "t4": (q + p) * half, "t5": (t + r) * half, "t6": (q - p) * half, "t7": (t - r) * half}


def w8_arc(field: Field, sign: int, parameters: tuple[Any, ...]) -> dict[str, Series]:
    """An arc of the W8 slice J = g(t1, s9 t9) - t2^2 - P Q + R T, g = t1^2 t9^2 - 2 t1^2 t9 + 2 t1 t9^2 - 4 t1 t9,
    with sign = s9 (the header of W8 -> N+ is that of W8 -> N- at -t9)."""
    kind, point, (first, second) = parameters
    half = Fraction(1, 2)
    s = monomials(field, 1)
    if kind == "c30":
        b, c, big_v, big_a, big_b = point
        u2 = monomials(field, big_v)
        r = monomials(field, b * big_v, big_a, first)
        p = monomials(field, c * big_v, big_b, second)
        n = r * (2 * c) - p * (2 * b) - u2 * u2
        u9 = Series((), field)
        for _ in range(field.order):
            u9 = (n - s * u9 * 2 + s * u9 * u9 * 2 + s * s * u9 * u9) * Fraction(1, 4)
        return {
            "t1": s,
            "t2": s * u2,
            "t4": s * (p + 2 * b) * half,
            "t5": s * (r + 2 * c) * half,
            "t6": s * (-p + 2 * b) * half,
            "t7": s * (-r + 2 * c) * half,
            "t9": s * u9 * sign,
        }
    _require(field.prime is not None, "the degree-20 arcs carry the square root of -1")
    big_c, big_d, big_t, big_u, big_w = point
    root = PRIMES[field.prime or 0]
    c, d = monomials(field, big_c, first), monomials(field, big_d, second)
    t7, t1, t9 = monomials(field, big_t), monomials(field, big_u), monomials(field, big_w)
    g = t1 * t1 * t9 * t9 - t1 * t1 * t9 * 2 + t1 * t9 * t9 * 2 - t1 * t9 * 4
    b = (g + c * d - t7 * t7).shift(1)
    inverse = Fraction(1, 2 * root)
    return {
        "t1": t1,
        "t2": (s + b) * half,
        "t4": (s - b) * inverse,
        "t5": (c + d) * half,
        "t6": (c - d) * inverse,
        "t7": t7,
        "t9": t9 * sign,
    }


def x_same_arc(field: Field, sign: int, parameters: tuple[tuple[int, ...], ...]) -> dict[str, Series]:
    """Phi of ../arcs-x-same on its weighted arc; sign = s9."""
    (big_w, big_r, big_s, big_a), (w2, r2, s2, a2) = parameters
    half = Fraction(1, 2)
    w = monomials(field, big_w, 0, w2, start=2)
    rho, sig, a = (monomials(field, lead, 0, extra) for lead, extra in ((big_r, r2), (big_s, s2), (big_a, a2)))
    m = w + 1
    u = m.inverse()
    t9 = -(w * w) * u * half
    return {
        "t1": a - t9,
        "t2": a * w * (w + 2) * u * half,
        "t4": (m * rho + sig) * half,
        "t5": (m * rho - sig) * half,
        "t6": (m * sig + rho) * half,
        "t7": (rho - m * sig) * half,
        "t9": t9 * sign,
    }


def e8_phi(
    field: Field, sign: int, w: Series, rho: Series, sigma: Series, zeta: Series, e: Series
) -> dict[str, Series]:
    """The slice coordinates of Phi(m = 1 + w, rho, sigma, e, zeta) of ../arcs, with t9 carrying the incidence sign."""
    half = Fraction(1, 2)
    m = w + 1
    m_inverse = m.inverse()
    below, above = m * m - 1, m * m + 1
    e_inverse = (e * 4).inverse()
    nu = (e + 1) * (e + 1) * e_inverse
    omega = (e * e - 1) * e_inverse
    t3 = zeta
    t2 = (below * nu * 2 + below * zeta) * above.inverse()
    return {
        "t1": (-below * t2 + above * t3 + w * w) * m_inverse * half,
        "t2": t2,
        "t3": t3,
        "t4": (m * rho + sigma) * half,
        "t5": (m * rho - sigma) * half,
        "t6": (m * sigma + rho) * half,
        "t7": (rho - m * sigma) * half,
        "t8": -(below * omega * m_inverse * PRIMES[field.prime or 0]),
        "t9": -(w * w) * m_inverse * half * sign,
    }


def slice_of(item: tuple[str, Field]) -> dict[str, Any]:
    """slice_data of one (slug, field). The unit parallel.ordered_map maps."""
    return slice_data(*item)


def operand(split: list[Series], field: Field) -> list[Series]:
    """The 32 coordinates of the operand with z_k = i^popcount(k) split_k and z_k = x_k + i x_(16+k)."""
    x = [Series((), field)] * DIM
    for k, value in enumerate(split, start=1):
        power = k.bit_count() % 4
        x[k + (16 if power % 2 else 0)] = value if power < 2 else -value
    return x


def left_matrix(x: list[Series]) -> list[list[Series]]:
    return [[x[row ^ column] * cd_sign(DIM, row ^ column, column) for column in range(DIM)] for row in range(DIM)]


def saturated_kernel(matrix: list[list[Series]], field: Field) -> tuple[list[Vector], list[int]]:
    """Constant terms of a saturated kernel basis over k[[s]], and the pivot valuations."""
    size = len(matrix)
    one, zero = Series((1,), field), Series((), field)
    transform = [[one if i == j else zero for j in range(size)] for i in range(size)]
    columns = list(range(size))
    rows = list(range(size))
    valuations: list[int] = []
    while columns:
        best = min(((matrix[i][j].valuation(), i, j) for i in rows for j in columns), default=(field.order, 0, 0))
        if best[0] >= field.order - sum(valuations):
            break
        value, i, j = best
        unit_inverse = matrix[i][j].shift(value).inverse()
        for c in columns:
            if c != j and matrix[i][c].valuation() < field.order:
                factor = matrix[i][c].shift(value) * unit_inverse
                for r in range(size):
                    matrix[r][c] = matrix[r][c] - factor * matrix[r][j]
                    transform[r][c] = transform[r][c] - factor * transform[r][j]
        valuations.append(value)
        columns.remove(j)
        rows.remove(i)
    return [tuple(transform[r][c].c[0] for r in range(size)) for c in columns], valuations


def rref(vectors: list[Vector], field: Field) -> list[Vector]:
    rows = [list(v) for v in vectors]
    out: list[list[Scalar]] = []
    for column in range(len(rows[0]) if rows else 0):
        pivot = next((r for r in rows if r[column]), None)
        if pivot is None:
            continue
        rows.remove(pivot)
        inverse = field.inverse(pivot[column])
        pivot = [field.scalar(v * inverse) for v in pivot]
        for other in (*rows, *out):
            factor = other[column]
            if factor:
                other[:] = [field.scalar(a - factor * b) for a, b in zip(other, pivot, strict=True)]
        out.append(pivot)
    return [tuple(r) for r in sorted(out, key=lambda r: next(i for i, v in enumerate(r) if v))]


def plane_text(plane: list[Vector]) -> list[list[str]]:
    return [[str(v) for v in row] for row in plane]


def one_arc(item: tuple[dict[str, Any], tuple[Any, ...], bool]) -> dict[str, Any]:
    data, parameters, mutate = item
    slug = data["slug"]
    field = Field(data["prime"], data["order"])
    sign = -INCIDENCES[slug][1] if mutate else INCIDENCES[slug][1]
    arc = (
        x_arc
        if slug in X_INCIDENCES
        else iso_arc
        if slug in ISO_INCIDENCES
        else w8_arc
        if slug in W8_INCIDENCES
        else x_same_arc
        if slug in XS_INCIDENCES
        else e8_arc
    )
    values = arc(field, sign, parameters)
    full = dict(values)
    for name in data["slice_names"]:
        if name not in full:
            full[name] = evaluate(data["substitutions"][name], values, field)
    base = [Fraction(v) for v in data["boundary_point"]]
    split = [
        full[data["slice_names"][data["slice_columns"].index(k)]] + base[k]
        if k in data["slice_columns"]
        else Series((base[k],), field)
        for k in range(len(base))
    ]
    matrix = left_matrix(operand(split, field))
    base_matrix = [[Series((entry.c[0],), field) for entry in row] for row in matrix]
    base_kernel = rref(saturated_kernel(base_matrix, field)[0], field)
    kernel, valuations = saturated_kernel(matrix, field)
    plane = rref(kernel, field)
    record: dict[str, Any] = {
        "parameters": parameters,
        "mutated": mutate,
        "base_nullity": len(base_kernel),
        "arc_nullity": len(kernel),
        "pivot_valuations": sorted(valuations),
        "limit_dimension": len(plane),
        "limit_in_base_kernel": len(rref([*base_kernel, *plane], field)) == len(base_kernel),
        "plane": plane_text(plane),
        "plane_sha256": hashlib.sha256(json.dumps(plane_text(plane)).encode()).hexdigest(),
        # Over Q the arcs of one parameter point form a group: every entry but the trailing variant.
        "group": json.dumps(parameters[0] if len(parameters) == 2 else parameters[:-1]),
    }
    if field.prime:
        _, ideal_j, ideal_g = header(slug, field.prime)
        with_root = dict(values, I=Series((PRIMES[field.prime],), field))
        record["j_nonzero"] = sum(evaluate(text, with_root, field).valuation() < field.order for text in ideal_j)
        forms = [evaluate(text, with_root, field) for text in ideal_g]
        order = min(form.valuation() for form in forms)
        record["g_order"] = order
        if order < field.order:
            lead = [form.c[order] for form in forms]
            unit = field.inverse(next(v for v in lead if v))
            record["g_limit"] = [field.scalar(v * unit) for v in lead]
            record["group"] = json.dumps(record["g_limit"])
    return record


def summarize(data: dict[str, Any], arcs: list[dict[str, Any]]) -> dict[str, Any]:
    kept = [a for a in arcs if not a["mutated"]]
    groups: dict[str, set[str]] = {}
    for a in kept:
        groups.setdefault(a["group"], set()).add(a["plane_sha256"])
    sizes: dict[str, int] = {}
    for a in kept:
        sizes[a["group"]] = sizes.get(a["group"], 0) + 1
    return {
        "slug": data["slug"],
        "incidence": INCIDENCES[data["slug"]][0],
        "field": f"F_{data['prime']}" if data["prime"] else "Q",
        "slice": data,
        "arcs": len(kept),
        "base_nullity": sorted({a["base_nullity"] for a in kept}),
        "arc_nullity": sorted({a["arc_nullity"] for a in kept}),
        "limit_dimension": sorted({a["limit_dimension"] for a in kept}),
        "g_order": sorted({a["g_order"] for a in kept if "g_order" in a}),
        "largest_pivot_valuation_sum": max(sum(a["pivot_valuations"]) for a in kept),
        "limit_in_base_kernel": all(a["limit_in_base_kernel"] for a in kept),
        # None over Q: J is evaluated only modulo a prime, where the headers exist.
        "on_slice": all(a["j_nonzero"] == 0 for a in kept) if all("j_nonzero" in a for a in kept) else None,
        "groups": len(groups),
        "groups_with_several_arcs": sum(size > 1 for size in sizes.values()),
        "one_plane_per_group": all(len(planes) == 1 for planes in groups.values()),
        "distinct_planes": len({p for planes in groups.values() for p in planes}),
        "mutation_columns_without_pivot": sorted({a["arc_nullity"] for a in arcs if a["mutated"]}),
        "records": arcs,
    }


def reduces(rational: dict[str, Any], modular: dict[str, Any]) -> bool:
    """Every plane over Q, reduced modulo the prime, equals the plane of the same arc modulo the prime."""
    field = Field(modular["slice"]["prime"], 1)
    for q_arc, p_arc in zip(rational["records"], modular["records"], strict=True):
        _require(q_arc["parameters"] == p_arc["parameters"], "arc order")
        if q_arc["mutated"]:
            continue
        rows = [tuple(field.scalar(Fraction(v)) for v in row) for row in q_arc["plane"]]
        if plane_text(rref(rows, field)) != p_arc["plane"]:
            return False
    return True


# family: (incidences, truncation order, whether the arcs have rational coefficients)
FAMILIES: dict[str, tuple[dict[str, tuple[str, int]], int, bool]] = {
    "x": (X_INCIDENCES, X_ORDER, True),
    "e8": (E8_INCIDENCES, E8_ORDER, False),
    "iso": (ISO_INCIDENCES, ISO_ORDER, True),
    "w8-c30": (W8_INCIDENCES, W8_ORDER, True),
    "w8-c20": (W8_INCIDENCES, W8_ORDER, False),
    "x-same": (XS_INCIDENCES, XS_ORDER, True),
}
RESULTS = {
    "x": "x-opposite-result.json",
    "e8": "e8-result.json",
    "iso": "iso-result.json",
    "w8-c30": "w8-c30-result.json",
    "w8-c20": "w8-c20-result.json",
    "x-same": "x-same-result.json",
}


def parameter_sets(family: str) -> list[tuple[tuple[Any, ...], bool]]:
    if family == "x":
        return [
            ((direction, variant), mutate)
            for direction in X_DIRECTIONS
            for variant, mutate in (*((v, False) for v in X_VARIANTS), (X_VARIANTS[1], True))
        ]
    if family == "iso":
        return [
            ((point, variant), mutate)
            for point in ISO_POINTS
            for variant, mutate in (*((v, False) for v in ISO_VARIANTS), (ISO_VARIANTS[0], True))
        ]
    if family == "x-same":
        return [
            ((point, variant), mutate)
            for point in XS_POINTS
            for variant, mutate in (*((v, False) for v in XS_VARIANTS), (XS_VARIANTS[0], True))
        ]
    if family.startswith("w8-"):
        kind = family.removeprefix("w8-")
        return [
            ((kind, point, variant), mutate)
            for point in W8_POINTS[kind]
            for variant, mutate in (*((v, False) for v in W8_VARIANTS), (W8_VARIANTS[0], True))
        ]
    return [
        ((kind, point, variant), mutate)
        for kind in ("p2", "p1")
        for point in E8_POINTS
        for variant, mutate in (*((v, False) for v in E8_VARIANTS), (E8_VARIANTS[0], True))
    ]


def build(family: str) -> dict[str, Any]:
    slugs, order, rational = FAMILIES[family]
    fields = (*PRIMES, None) if rational else tuple(PRIMES)
    slices = parallel.ordered_map(
        slice_of, [(slug, Field(prime, order)) for slug, prime in itertools.product(slugs, fields)], min_items=1
    )
    sets = parameter_sets(family)
    items = [(data, parameters, mutate) for data in slices for parameters, mutate in sets]
    results = parallel.ordered_map(one_arc, items, min_items=1)
    summaries = [summarize(data, results[i * len(sets) : (i + 1) * len(sets)]) for i, data in enumerate(slices)]
    by_key = {(s["slug"], s["slice"]["prime"]): s for s in summaries}
    reductions = {
        f"{slug}:Q->F_{prime}": reduces(by_key[slug, None], by_key[slug, prime])
        for slug in slugs
        for prime in PRIMES
        if None in fields
    }
    verdict = all(
        s["base_nullity"] == [16]
        and s["arc_nullity"] == [SOURCE_NULLITY]
        and s["limit_dimension"] == [SOURCE_NULLITY]
        and s["limit_in_base_kernel"]
        and s["on_slice"] is not False
        and s["one_plane_per_group"]
        and s["mutation_columns_without_pivot"] != [SOURCE_NULLITY]
        for s in summaries
    ) and all(reductions.values())
    return {
        "schema": SCHEMA,
        "family": family,
        "order": order,
        "reductions": reductions,
        "verdict": "survives" if verdict else "refuted",
        "cases": summaries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("family", choices=tuple(FAMILIES))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    record = build(args.family)
    out = args.out or HERE / RESULTS[args.family]
    out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    for case in record["cases"]:
        print(
            case["slug"],
            case["field"],
            {k: case[k] for k in case if k not in ("records", "slice", "slug", "field", "incidence")},
        )
    print("reductions", record["reductions"], "verdict", record["verdict"])


if __name__ == "__main__":
    main()
