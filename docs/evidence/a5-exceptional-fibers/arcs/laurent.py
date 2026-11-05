"""Laurent series over F_p (truncated), for arcs whose parameters carry negative powers of s."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import arclib as A
from arc_targets import Target
from flint import nmod_poly


class L:
    """s^sh * poly(s), known modulo s^top (absolute exponent bound, exclusive)."""

    __slots__ = ("p", "poly", "sh", "top")

    def __init__(self, coeffs: Sequence[Any], sh: int, top: int, p: int) -> None:
        self.sh = sh
        self.top = top
        self.p = p
        n = max(top - sh, 0)
        self.poly = nmod_poly([int(x) % p for x in list(coeffs)[:n]], p)

    @staticmethod
    def mono(a: int, k: int, top: int, p: int) -> L:
        return L([a % p], k, top, p)

    @staticmethod
    def const(a: int, top: int, p: int) -> L:
        return L([a % p], 0, top, p)

    def _ints(self) -> list[int]:
        return [int(c) for c in self.poly.coeffs()]

    def val(self) -> int | None:
        for k, v in enumerate(self._ints()):
            if v % self.p:
                return k + self.sh
        return None

    def _coerce(self, other: L | int) -> L:
        return L.const(other, self.top, self.p) if isinstance(other, int) else other

    def __add__(self, other: L | int) -> L:
        o = self._coerce(other)
        sh = min(self.sh, o.sh)
        top = min(self.top, o.top)

        def lift(x: L) -> nmod_poly:
            return nmod_poly([0] * (x.sh - sh) + x._ints(), self.p)

        return L((lift(self) + lift(o)).coeffs(), sh, top, self.p)

    __radd__ = __add__

    def __neg__(self) -> L:
        return L((-self.poly).coeffs(), self.sh, self.top, self.p)

    def __sub__(self, other: L | int) -> L:
        return self + (-self._coerce(other))

    def __rsub__(self, other: L | int) -> L:
        return (-self) + other

    def __mul__(self, other: L | int) -> L:
        if isinstance(other, int):
            return L((self.poly * (other % self.p)).coeffs(), self.sh, self.top, self.p)
        sh = self.sh + other.sh
        va, vb = self.val(), other.val()
        # The product is known modulo s^min(self.top + val(other), other.top + val(self)); a zero factor has none.
        top = min(self.top + (other.sh if vb is None else vb), other.top + (self.sh if va is None else va))
        if va is None or vb is None:
            return L([], sh, top, self.p)
        n = max(top - sh, 0)
        return L(self.poly.mul_low(other.poly, n).coeffs() if n > 0 else [], sh, top, self.p)

    __rmul__ = __mul__

    def inv(self) -> L:
        v = self.val()
        if v is None:
            raise ZeroDivisionError("zero series")
        unit = nmod_poly(self._ints()[v - self.sh :], self.p)
        prec = self.top - v
        return L(unit.inverse_series_trunc(prec).coeffs(), -v, -v + prec, self.p)

    def to_series(self, N: int) -> A.Series:
        """Regular series with exponents 0..N-1; requires val >= 0 and precision >= N."""
        v = self.val()
        if v is not None and v < 0:
            raise ValueError(f"pole of order {-v}")
        if self.top < N:
            raise ValueError(f"precision {self.top} < {N}")
        cs = self._ints()
        if self.sh >= 0:
            full = [0] * self.sh + cs
        else:
            drop = -self.sh
            if any(cs[:drop]):
                raise ValueError("nonzero coefficient below s^0")
            full = cs[drop:]
        return A.Series(full, N, self.p)


def phi_laurent(target: Target, w: L, rho: L, sigma: L, e: L, zeta: L) -> list[L]:
    """Phi with Laurent parameters; e is a unit-valued series. Returns [t1..t9] as L."""
    p = target.prime
    half = pow(2, -1, p)
    quarter = pow(4, -1, p)
    m = w + 1
    minv = m.inv()
    mm = m * m
    mm1 = mm - 1
    mp1 = mm + 1
    e_inv = e.inv()
    nu = (e + e_inv + 2) * quarter
    om = (e - e_inv) * quarter
    t9 = -(w * w) * minv * (half * target.sign9 % p)
    t4 = (m * rho + sigma) * half
    t5 = (m * rho - sigma) * half
    t6 = (m * sigma + rho) * half
    t7 = (rho - m * sigma) * half
    z = mm1 * nu * 2
    wc = mm1 * om * 2
    t8 = -(wc * minv * (target.root * half % p))
    t3 = zeta
    t2 = (z + mm1 * zeta) * mp1.inv()
    t1 = ((-mm1 * t2) + mp1 * t3 + w * w) * minv * half
    return [t1, t2, t3, t4, t5, t6, t7, t8, t9]
