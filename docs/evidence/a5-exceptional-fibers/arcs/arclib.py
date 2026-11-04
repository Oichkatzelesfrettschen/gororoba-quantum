"""Exact F_p series arithmetic for arcs on the slice V(J) of an E8-bar -> N-/N+ target.

The rational parametrization Phi of V(J) in the five parameters (w, rho, sigma, e, zeta) is derived in README.md.
Everything here is integer arithmetic modulo the target's prime; python-flint `nmod_poly` carries truncated power
series in s. Every constructor takes the modulus, and every operation reads it from its operands.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from arc_targets import NGEN, NVAR, Target, header_ideals
from flint import nmod_poly

Poly = dict[tuple[int, ...], int]


class Series:
    """Truncated power series in s over F_p, known modulo s^N."""

    __slots__ = ("N", "c", "p")

    def __init__(self, coeffs: Sequence[Any], N: int, p: int) -> None:
        self.N = N
        self.p = p
        self.c = nmod_poly([int(x) % p for x in list(coeffs)[:N]], p)

    @staticmethod
    def const(a: int, N: int, p: int) -> Series:
        return Series([a % p], N, p)

    @staticmethod
    def mono(a: int, k: int, N: int, p: int) -> Series:
        """a * s^k"""
        if k >= N:
            return Series([], N, p)
        return Series([0] * k + [a % p], N, p)

    def _coerce(self, other: Series | int) -> Series:
        return Series.const(other, self.N, self.p) if isinstance(other, int) else other

    def __add__(self, other: Series | int) -> Series:
        return Series((self.c + self._coerce(other).c).coeffs(), self.N, self.p)

    __radd__ = __add__

    def __sub__(self, other: Series | int) -> Series:
        return Series((self.c - self._coerce(other).c).coeffs(), self.N, self.p)

    def __rsub__(self, other: Series | int) -> Series:
        return (-self) + other

    def __neg__(self) -> Series:
        return Series((-self.c).coeffs(), self.N, self.p)

    def __mul__(self, other: Series | int) -> Series:
        if isinstance(other, int):
            return Series((self.c * (other % self.p)).coeffs(), self.N, self.p)
        return Series(self.c.mul_low(other.c, self.N).coeffs(), self.N, self.p)

    __rmul__ = __mul__

    def val(self) -> int | None:
        for k, v in enumerate(self.c.coeffs()):
            if int(v) % self.p:
                return k
        return None

    def inv(self) -> Series:
        """Inverse of a unit series."""
        if int(self.c[0]) % self.p == 0:
            raise ZeroDivisionError("non-unit series")
        return Series(self.c.inverse_series_trunc(self.N).coeffs(), self.N, self.p)

    def coeff(self, k: int) -> int:
        cs = self.c.coeffs()
        return int(cs[k]) % self.p if k < len(cs) else 0


def _terms(text: str) -> list[str]:
    """Split a Singular polynomial into signed terms."""
    text = re.sub(r"\s", "", text)
    text = re.sub(r"(?<!^)(?<![\^*])-", "+-", text)
    return [t for t in text.removeprefix("+").split("+") if t]


def _parse(text: str, p: int, nvar: int, factor: str) -> Poly:
    """Parse a Singular polynomial whose variables match `factor` (group 1: index, group 2: exponent)."""
    out: Poly = {}
    for term in _terms(text):
        coef = 1
        exps = [0] * nvar
        for fac in term.split("*"):
            if re.fullmatch(r"-?\d+", fac):
                coef = coef * int(fac) % p
                continue
            if fac.startswith("-"):
                coef = -coef % p
                fac = fac[1:]
            found = re.fullmatch(factor, fac)
            if not found:
                raise ValueError(f"bad factor {fac!r} in term {term!r}")
            exps[int(found.group(1)) - 1] += int(found.group(2) or 1)
        key = tuple(exps)
        out[key] = (out.get(key, 0) + coef) % p
    return {k: v for k, v in out.items() if v}


def parse_poly(text: str, p: int) -> Poly:
    """A Singular polynomial in t1..t9 as {exponent tuple: coefficient mod p}."""
    return _parse(text, p, NVAR, r"t(\d)(?:\^(\d+))?")


def parse_ypoly(text: str, p: int) -> Poly:
    """A Singular polynomial in y(1..21) as {exponent tuple: coefficient mod p}."""
    return _parse(text, p, NGEN, r"y\((\d+)\)(?:\^(\d+))?")


def load_slice(target: Target) -> tuple[list[Poly], list[Poly]]:
    """The generators of J and of G of the target's header."""
    j_text, g_text = header_ideals(target)
    return [parse_poly(t, target.prime) for t in j_text], [parse_poly(t, target.prime) for t in g_text]


def load_yideal(text: str, p: int) -> list[Poly]:
    """An ideal in y(1..21) from a comma separated generator list."""
    return [parse_ypoly(t, p) for t in text.strip().rstrip(";").split(",") if t.strip()]


def phi_series(target: Target, w: Series, rho: Series, sigma: Series, e: int, zeta: Series) -> list[Series]:
    """Phi with a series w, rho, sigma, zeta and an integer e: returns [t1..t9].

    m = 1 + w, t9 = -sign9 (m-1)^2/(2m), t4..t7 from the rank-one matrix [[m rho, m sigma],[rho, sigma]],
    Z = 2(m^2-1) nu, W = 2(m^2-1) omega with nu = (e+1)^2/(4e), omega = (e^2-1)/(4e),
    t8 = -i W/(2m), t3 = zeta, t2 = (Z + (m^2-1) zeta)/(m^2+1), t1 = ((1-m^2) t2 + (m^2+1) t3 + (m-1)^2)/(2m).
    """
    p = target.prime
    half = pow(2, -1, p)
    m = w + 1
    minv = m.inv()
    m2m1 = m * m - 1
    m2p1 = m * m + 1
    inv4e = pow(4 * e, -1, p)
    nu = (e + 1) ** 2 * inv4e % p
    om = (e * e - 1) * inv4e % p
    t9 = -(w * w) * minv * (half * target.sign9 % p)
    t4 = (m * rho + sigma) * half
    t5 = (m * rho - sigma) * half
    t6 = (m * sigma + rho) * half
    t7 = (rho - m * sigma) * half
    z = m2m1 * (2 * nu % p)
    wc = m2m1 * (2 * om % p)
    t8 = -(wc * minv * (target.root * half % p))
    t3 = zeta
    t2 = (z + m2m1 * zeta) * m2p1.inv()
    t1 = ((-m2m1 * t2) + m2p1 * t3 + w * w) * minv * half
    return [t1, t2, t3, t4, t5, t6, t7, t8, t9]


def eval_poly(poly: Poly, xs: Sequence[Series], N: int) -> Series:
    """Evaluate {exps: coeff} at the series xs with truncation N."""
    p = xs[0].p
    maxd = [0] * NVAR
    for ex in poly:
        for i, k in enumerate(ex):
            maxd[i] = max(maxd[i], k)
    powers: list[list[Series]] = []
    for i in range(NVAR):
        lst = [Series.const(1, N, p)]
        for _ in range(maxd[i]):
            lst.append(lst[-1] * xs[i])
        powers.append(lst)
    acc = Series([], N, p)
    for ex, cf in poly.items():
        term = Series.const(cf, N, p)
        for i, k in enumerate(ex):
            if k:
                term = term * powers[i][k]
        acc = acc + term
    return acc


def eval_y(poly: Poly, y: Sequence[int], p: int) -> int:
    """Value of a polynomial in y(1..21) at the point y, modulo p."""
    tot = 0
    for ex, cf in poly.items():
        t = cf
        for i, k in enumerate(ex):
            if k:
                t = t * pow(y[i], k, p) % p
        tot = (tot + t) % p
    return tot


def inside(ideal: Sequence[Poly], point: Sequence[int], p: int) -> bool:
    """True when every generator vanishes at the point."""
    return all(eval_y(g, point, p) == 0 for g in ideal)


def leading_vector(
    gens: Sequence[Poly], xs: Sequence[Series], N: int
) -> tuple[int | None, list[int] | None, list[int | None]]:
    """(nu, F, valuations): F is the coefficient vector of (G_j(x(s))) at the minimal order nu, or None."""
    vals = [eval_poly(g, xs, N) for g in gens]
    vs = [v.val() for v in vals]
    finite = [v for v in vs if v is not None]
    if not finite:
        return None, None, vs
    nu = min(finite)
    return nu, [v.coeff(nu) for v in vals], vs
