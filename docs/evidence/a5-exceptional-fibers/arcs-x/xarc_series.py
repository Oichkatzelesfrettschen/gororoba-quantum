"""Exact F_p arithmetic for arcs on the slice V(J): truncated power series in s (python-flint nmod_poly), dual numbers.

Phi (parameters w, rho, sig, s1; m = 1 + w) is the rational map onto V(J) derived in README.md:
  t1 = s1, t4 = (m rho + sig)/2, t5 = (m rho - sig)/2, t6 = (m sig + rho)/2, t7 = (rho - m sig)/2,
  t9 = sgn * t9xp with t9xp = -w^2/(2m) (sgn = +1 for X+ -> N-, -1 for X- -> N+),
  t2 = w (2 + w)/(2 m) * (s1 - t9xp + 2).
Every object carries its modulus p, so one process handles several primes.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from flint import nmod_poly
from xarc_common import NVAR_LOCAL, Poly, inv


class Series:
    """Truncated power series in s over F_p, known modulo s^N."""

    __slots__ = ("N", "c", "p")

    def __init__(self, coeffs: Sequence[Any], N: int, p: int) -> None:
        self.N = N
        self.p = p
        self.c = nmod_poly([int(x) % p for x in list(coeffs)[:N]], p)

    @staticmethod
    def mono(a: int, k: int, N: int, p: int) -> Series:
        return Series([0] * k + [a % p], N, p) if k < N else Series([], N, p)

    def _co(self, o: Series | int) -> Series:
        return Series([o], self.N, self.p) if isinstance(o, int) else o

    def __add__(self, o: Series | int) -> Series:
        return Series((self.c + self._co(o).c).coeffs(), self.N, self.p)

    __radd__ = __add__

    def __neg__(self) -> Series:
        return Series((-self.c).coeffs(), self.N, self.p)

    def __sub__(self, o: Series | int) -> Series:
        return self + (-self._co(o))

    def __rsub__(self, o: Series | int) -> Series:
        return (-self) + o

    def __mul__(self, o: Series | int) -> Series:
        if isinstance(o, int):
            return Series((self.c * (o % self.p)).coeffs(), self.N, self.p)
        return Series(self.c.mul_low(o.c, self.N).coeffs(), self.N, self.p)

    __rmul__ = __mul__

    def inv(self) -> Series:
        if int(self.c[0]) % self.p == 0:
            raise ZeroDivisionError("non-unit series")
        return Series(self.c.inverse_series_trunc(self.N).coeffs(), self.N, self.p)

    def coeff(self, k: int) -> int:
        cs = self.c.coeffs()
        return int(cs[k]) % self.p if k < len(cs) else 0

    def val(self) -> int | None:
        for k, v in enumerate(self.c.coeffs()):
            if int(v) % self.p:
                return k
        return None


class Dual:
    """a + d * eps with eps^2 = 0 over F_p."""

    __slots__ = ("a", "d", "p")

    def __init__(self, a: int, d: int, p: int) -> None:
        self.p = p
        self.a = a % p
        self.d = d % p

    def _co(self, o: Dual | int) -> Dual:
        return Dual(o, 0, self.p) if isinstance(o, int) else o

    def __add__(self, o: Dual | int) -> Dual:
        o = self._co(o)
        return Dual(self.a + o.a, self.d + o.d, self.p)

    __radd__ = __add__

    def __neg__(self) -> Dual:
        return Dual(-self.a, -self.d, self.p)

    def __sub__(self, o: Dual | int) -> Dual:
        return self + (-self._co(o))

    def __rsub__(self, o: Dual | int) -> Dual:
        return (-self) + o

    def __mul__(self, o: Dual | int) -> Dual:
        o = self._co(o)
        return Dual(self.a * o.a, self.a * o.d + self.d * o.a, self.p)

    __rmul__ = __mul__

    def inv(self) -> Dual:
        ia = inv(self.a, self.p)
        return Dual(ia, -self.d * ia * ia, self.p)


def phi(sgn: int, p: int, w: Any, rho: Any, sig: Any, s1: Any) -> list[Any]:
    """Phi(w, rho, sig, s1) = [t1, t2, t4, t5, t6, t7, t9] over a ring with + - * int and inv()."""
    half = inv(2, p)
    m = w + 1
    u = m.inv()
    t9xp = -(w * w) * u * half
    t9 = t9xp * sgn
    t4 = (m * rho + sig) * half
    t5 = (m * rho - sig) * half
    t6 = (m * sig + rho) * half
    t7 = (rho - m * sig) * half
    t2 = (w * (w + 2)) * u * half * (s1 - t9xp + 2)
    return [s1, t2, t4, t5, t6, t7, t9]


def eval_poly(poly: Poly, xs: Sequence[Series], N: int) -> Series:
    """Evaluate {exponents: coefficient} at the series xs, truncated modulo s^N."""
    p = xs[0].p
    maxd = [0] * NVAR_LOCAL
    for ex in poly:
        for i, k in enumerate(ex):
            maxd[i] = max(maxd[i], k)
    powers = []
    for i in range(NVAR_LOCAL):
        lst = [Series([1], N, p)]
        for _ in range(maxd[i]):
            lst.append(lst[-1] * xs[i])
        powers.append(lst)
    acc = Series([], N, p)
    for ex, cf in poly.items():
        term = Series([cf], N, p)
        for i, k in enumerate(ex):
            if k:
                term = term * powers[i][k]
        acc = acc + term
    return acc


def arc(sgn: int, p: int, W: int, R: int, S: int, K: int, N: int) -> list[Series]:
    """x(s) = Phi(W s, R s, S s, K s)."""
    w, rho, sig, s1 = (Series.mono(c, 1, N, p) for c in (W, R, S, K))
    return phi(sgn, p, w, rho, sig, s1)
