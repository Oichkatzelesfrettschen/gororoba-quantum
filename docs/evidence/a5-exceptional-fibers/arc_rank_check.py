"""Recomputation of the limit-map ranks of the arc certificates without Singular, by dual-number power series.

The certificates of structure/arcs-iso-w8/blowup-arcs, arcs-x-same and arcs-vb compute the limit vector F of an arc
family symbolically in Singular and take the rank of [dF | F] at two parameter points. This script recomputes those
ranks without Singular: the arc is written here from its formula, evaluated at the same two parameter points over
F_p[eps]/(eps^2) with one parameter carrying eps, pushed through the header's J and G by the truncated series of
kernel-limits/plucker_limits.py, and the eps-part of the coefficient of s^nu is the derivative of F in that
parameter. The header parser, the Series class and the polynomial evaluator are those of plucker_limits.py, so the
check is independent of Singular and of the arc formulas in the generators, not of that Python evaluator. The record
holds, per family, prime and point: the least order of J on the arc (the truncation order when
J vanishes), the order nu of G, and the rank of [dF | F] over F_p, beside the rank the Singular log reports.

    $PYTHON docs/evidence/a5-exceptional-fibers/arc_rank_check.py
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from flint import nmod_mat

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "kernel-limits"))
sys.path.insert(0, str(HERE.parents[2] / "gororoba_quantum"))

import plucker_limits as limits  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-arc-rank-check-v1"
ORDER = 14
# The parameter points of the certificates, as (b, c, V, A, B) or (W, R, S, K) prefixes.
POINTS = ((2, 3, 5, 7, 11), (13, 4, 9, 6, 17))


@dataclass(frozen=True)
class Dual:
    """x + y eps modulo a prime, eps^2 = 0."""

    x: int
    y: int
    p: int

    def _lift(self, other: Dual | int) -> Dual:
        return other if isinstance(other, Dual) else Dual(other % self.p, 0, self.p)

    def __add__(self, other: Dual | int) -> Dual:
        o = self._lift(other)
        return Dual((self.x + o.x) % self.p, (self.y + o.y) % self.p, self.p)

    __radd__ = __add__

    def __neg__(self) -> Dual:
        return Dual(-self.x % self.p, -self.y % self.p, self.p)

    def __sub__(self, other: Dual | int) -> Dual:
        return self + (-self._lift(other))

    def __rsub__(self, other: Dual | int) -> Dual:
        return (-self) + other

    def __mul__(self, other: Dual | int) -> Dual:
        o = self._lift(other)
        return Dual(self.x * o.x % self.p, (self.x * o.y + self.y * o.x) % self.p, self.p)

    __rmul__ = __mul__

    def __bool__(self) -> bool:
        return bool(self.x or self.y)


@dataclass(frozen=True)
class DualField(limits.Field):
    """F_prime[eps]/(eps^2) with power series known modulo s^order."""

    def scalar(self, value: Any) -> Any:
        if isinstance(value, Dual):
            return value
        fraction = Fraction(value)
        prime = self.prime or 0
        return Dual(fraction.numerator * pow(fraction.denominator, -1, prime) % prime, 0, prime)

    def inverse(self, value: Any) -> Any:
        prime = self.prime or 0
        inverse = pow(value.x, -1, prime)
        return Dual(inverse, -value.y * inverse * inverse % prime, prime)


def constant(field: DualField, value: Any) -> limits.Series:
    return limits.Series((value,), field)


def power(field: DualField, exponent: int) -> limits.Series:
    return limits.Series((0,) * exponent + (1,), field)


def unit_inverse(series: limits.Series) -> limits.Series:
    return series.inverse()


def rank_one_block(m: limits.Series, rho: limits.Series, sig: limits.Series) -> tuple[limits.Series, ...]:
    half = Fraction(1, 2)
    return (m * rho + sig) * half, (m * rho - sig) * half, (m * sig + rho) * half, (rho - m * sig) * half


def iso_arc(field: DualField, q: list[Any]) -> dict[str, limits.Series]:
    b, c, big_v, big_a = (constant(field, v) for v in q[:4])
    s = power(field, 1)
    u2 = b * big_v * s
    big_r = b * b * big_v * s + b * big_a * s * s
    big_p = (big_r * c * 2 - u2 * u2) * unit_inverse(b * 2)
    half = Fraction(1, 2)
    return {
        "t2": s * u2,
        "t3": s,
        "t4": s * (b * 2 + big_p) * half,
        "t5": s * (c * 2 + big_r) * half,
        "t6": s * (b * 2 - big_p) * half,
        "t7": s * (c * 2 - big_r) * half,
    }


def w8_arc(field: DualField, q: list[Any]) -> dict[str, limits.Series]:
    b, c, big_v, big_a, big_b = (constant(field, v) for v in q[:5])
    s = power(field, 1)
    u2 = big_v * s
    big_r = b * big_v * s + big_a * s * s
    big_p = c * big_v * s + big_b * s * s
    n = big_r * c * 2 - big_p * b * 2 - u2 * u2
    u9 = limits.Series((), field)
    for _ in range(field.order):
        u9 = (n - s * u9 * 2 + s * u9 * u9 * 2 + s * s * u9 * u9) * Fraction(1, 4)
    half = Fraction(1, 2)
    return {
        "t1": s,
        "t2": s * u2,
        "t4": s * (b * 2 + big_p) * half,
        "t5": s * (c * 2 + big_r) * half,
        "t6": s * (b * 2 - big_p) * half,
        "t7": s * (c * 2 - big_r) * half,
        "t9": s * u9,
    }


def x_same_arc(field: DualField, q: list[Any], sign: int) -> dict[str, limits.Series]:
    big_w, big_r, big_s, big_a = (constant(field, v) for v in q[:4])
    s = power(field, 1)
    w, rho, sig, a = big_w * s * s, big_r * s, big_s * s, big_a * s
    m = w + 1
    u = unit_inverse(m)
    t9 = -(w * w) * u * Fraction(1, 2)
    t4, t5, t6, t7 = rank_one_block(m, rho, sig)
    return {
        "t1": a - t9,
        "t2": a * w * (w + 2) * u * Fraction(1, 2),
        "t4": t4,
        "t5": t5,
        "t6": t6,
        "t7": t7,
        "t9": t9 * sign,
    }


def vb_arc(field: DualField, q: list[Any], special: bool) -> dict[str, limits.Series]:
    big_w, big_r, big_s, big_k = (constant(field, v) for v in q[:4])
    s = power(field, 1)
    k = big_k * s - 9 if special else big_k
    w = big_w * s * s if special else big_w * s
    rho, sig = big_r * s, big_s * s
    m = w + 1
    u, z, v = unit_inverse(m), unit_inverse(m * m + 1), unit_inverse(k * k + 1)
    a1 = w**4 - w * w * 6 - w * 4
    a2 = w**4 + w**3 * 8 + w * w * 18 + w * 12
    t1 = (k * k * a1 - a2) * u * u * v * Fraction(1, 4)
    block = rank_one_block(m, rho, sig)
    return {
        "t1": t1,
        "t2": (t1 * w * (w + 2) + w * w * 2) * z,
        "t3": -block[0],
        "t4": block[2],
        "t5": block[1],
        "t6": block[3],
        "t7": k * w * (w + 2) * u * v,
        "t8": -(w * w) * u * Fraction(1, 2),
    }


# family: (header slug, arc, number of parameters, log of the Singular certificate with {prime})
FAMILIES: dict[str, tuple[str, Any, int, str]] = {
    "iso": ("iso-nm", iso_arc, 4, "structure/arcs-iso-w8/blowup-arcs/iso-blowup-arcs-p{prime}.log"),
    "w8-c30": ("w8-nm", w8_arc, 5, "structure/arcs-iso-w8/blowup-arcs/w8-blowup-arcs-p{prime}.log"),
    "xm-nm": ("xm-nm", lambda f, q: x_same_arc(f, q, 1), 4, "arcs-x-same/xm-nm-arcs-p{prime}.log"),
    "xp-np": ("xp-np", lambda f, q: x_same_arc(f, q, -1), 4, "arcs-x-same/xp-np-arcs-p{prime}.log"),
    "vb-generic": ("e8-vb", lambda f, q: vb_arc(f, q, False), 4, "arcs-vb/vb-generic-p{prime}.log"),
    "vb-special": ("e8-vb", lambda f, q: vb_arc(f, q, True), 4, "arcs-vb/vb-special-p{prime}.log"),
}
X_POINTS = ((2, 3, 5, 7), (13, 4, 9, 6))


def singular_ranks(family: str, prime: int) -> list[int]:
    text = (HERE / FAMILIES[family][3].format(prime=prime)).read_text(encoding="utf-8")
    match = re.search(r"RESULT rank of \[dF \| F\] at two points (\d+) (\d+)", text)
    if match is None:
        raise RuntimeError(f"{family} {prime}: no rank line in the Singular log")
    return [int(match.group(1)), int(match.group(2))]


def one(item: tuple[str, int, int]) -> dict[str, Any]:
    family, prime, index = item
    slug, arc, count, _ = FAMILIES[family]
    point = (POINTS if family in ("iso", "w8-c30") else X_POINTS)[index][:count]
    field = DualField(prime, ORDER)
    _, ideal_j, ideal_g = limits.header(slug, prime)
    columns: list[list[int]] = []
    orders = set()
    j_order = ORDER
    limit: list[int] = []
    for varied in range(count):
        q = [Dual(v % prime, int(i == varied), prime) for i, v in enumerate(point)]
        values = dict(arc(field, q), I=limits.Series((limits.PRIMES[prime],), field))
        j_order = min(j_order, *(limits.evaluate(text, values, field).valuation() for text in ideal_j))
        forms = [limits.evaluate(text, values, field) for text in ideal_g]
        nu = min(form.valuation() for form in forms)
        orders.add(nu)
        columns.append([form.c[nu].y for form in forms])
        limit = [form.c[nu].x for form in forms]
    matrix = nmod_mat([*columns, limit], prime)
    return {
        "family": family,
        "prime": prime,
        "point": list(point),
        "least_order_of_J": j_order,
        "order_of_G": sorted(orders),
        "rank": int(matrix.rank()),
        "singular_rank": singular_ranks(family, prime)[index],
    }


def main() -> None:
    items = [(family, prime, index) for family in FAMILIES for prime in limits.PRIMES for index in range(2)]
    rows = parallel.ordered_map(one, items, min_items=1)
    # The W8 arc solves J = 0 by iteration, exact to the truncation order; the other arcs are exact identities.
    verdict = all(
        row["rank"] == row["singular_rank"] and len(row["order_of_G"]) == 1 and row["least_order_of_J"] >= ORDER - 2
        for row in rows
    )
    record = {"schema": SCHEMA, "order": ORDER, "verdict": "agrees" if verdict else "differs", "rows": rows}
    (HERE / "arc-rank-check.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    for row in rows:
        print(row)
    print("verdict", record["verdict"])


if __name__ == "__main__":
    main()
