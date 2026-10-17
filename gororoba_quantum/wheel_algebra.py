"""The wheel of fractions over Q: total division, with 1/0 = infinity and 0/0 = bottom.

A wheel (Carlstrom, "Wheels - On Division by Zero", Math. Struct. Comp. Sci.
14 (2004) 143-184) extends a commutative ring with a unary involution ``/``
that is total. The wheel of fractions over a field K is the set of pairs
(x, y) of K under (x, y) ~ (s x, s y) for every nonzero s, with

- (x, y) + (x', y') = (x y' + x' y, y y');
- (x, y) (x', y') = (x x', y y');
- /(x, y) = (y, x).

Over Q every class has one canonical pair: (q, 1) for a rational q,
infinity = (1, 0) = /0, and bottom = (0, 0) = 0/0. Division a / b is
a * /b, so a zero divisor yields infinity or bottom instead of raising, and
bottom absorbs every operation it enters: 0 * bottom and bottom + x are both
bottom. The ring laws that fail are the ones division by zero would break:
0 * x = 0 fails at x = infinity (0 * infinity = bottom), and x - x = 0 fails
at x = infinity (infinity + infinity = bottom). Carlstrom's axioms replace
them; ``axiom_failures`` checks every one by name.

``solve`` runs Gaussian elimination in natural pivot order over wheel
elements with no zero test anywhere: a zero pivot becomes infinity through
the involution, and its products with the zero entries of a consistent
singular system become bottom, which then spreads to every component it
touches. On a nonsingular system whose leading minors are nonzero (a
symmetric positive definite matrix) every intermediate stays finite and the
result equals Fraction elimination.

``--self-test`` checks the axioms over every triple of a pool holding 0, 1,
-1, infinity, bottom and nonzero rationals, plus seeded random triples; the
non-field facts above; a mutated wheel that maps bottom to zero, which the
axioms must reject; and ``solve`` on a nonsingular, a consistent singular and
an inconsistent singular system (bottom on the second, infinity on the third).
"""

from __future__ import annotations

import argparse
import itertools
import random
from collections.abc import Callable, Sequence
from fractions import Fraction

SELF_TEST_SEED = 20041027
RANDOM_TRIPLES = 2000

ZERO_Q = Fraction(0)
ONE_Q = Fraction(1)


class Wheel:
    """One element of the wheel of fractions over Q, held as its canonical pair."""

    __slots__ = ("x", "y")

    x: Fraction
    y: Fraction

    def __init__(self, x: Fraction | int, y: Fraction | int = 1) -> None:
        x, y = Fraction(x), Fraction(y)
        if y:
            self.x, self.y = (x / y if y != 1 else x), ONE_Q
        elif x:
            self.x, self.y = ONE_Q, ZERO_Q
        else:
            self.x, self.y = ZERO_Q, ZERO_Q

    def __add__(self, other: Wheel) -> Wheel:
        if self.y == 1 and other.y == 1:
            return Wheel(self.x + other.x)
        return Wheel(self.x * other.y + other.x * self.y, self.y * other.y)

    def __mul__(self, other: Wheel) -> Wheel:
        return Wheel(self.x * other.x, self.y * other.y)

    def __neg__(self) -> Wheel:
        return Wheel(-self.x, self.y)

    def __sub__(self, other: Wheel) -> Wheel:
        return self + (-other)

    def inv(self) -> Wheel:
        """The involution /(x, y) = (y, x)."""
        return Wheel(self.y, self.x)

    def __truediv__(self, other: Wheel) -> Wheel:
        return self * other.inv()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Wheel) and self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        return f"Wheel({self.x}, {self.y})"

    @property
    def finite(self) -> bool:
        return self.y != 0

    @property
    def bottom(self) -> bool:
        return self.y == 0 and self.x == 0

    @property
    def infinite(self) -> bool:
        return self.y == 0 and self.x != 0

    def value(self) -> Fraction:
        if not self.finite:
            raise ValueError(f"{self!r} is not a rational")
        return self.x

    def kind(self) -> str:
        return "bottom" if self.bottom else "infinity" if self.infinite else "finite"


ZERO = Wheel(0)
ONE = Wheel(1)
INFINITY = Wheel(1, 0)
BOTTOM = Wheel(0, 0)

Ops = tuple[Callable[[Wheel, Wheel], Wheel], Callable[[Wheel, Wheel], Wheel], Callable[[Wheel], Wheel]]


def standard_ops() -> Ops:
    return (lambda a, b: a + b, lambda a, b: a * b, lambda a: a.inv())


def axioms(ops: Ops) -> dict[str, Callable[[Wheel, Wheel, Wheel], bool]]:
    """Carlstrom's wheel axioms (Definition 1.1) and the derived identities, each as a predicate on a triple."""
    add, mul, inv = ops
    zero, one = ZERO, ONE

    def div(a: Wheel, b: Wheel) -> Wheel:
        return mul(a, inv(b))

    return {
        "addition is associative": lambda x, y, z: add(add(x, y), z) == add(x, add(y, z)),
        "addition is commutative": lambda x, y, z: add(x, y) == add(y, x),
        "0 is the additive unit": lambda x, y, z: add(x, zero) == x,
        "multiplication is associative": lambda x, y, z: mul(mul(x, y), z) == mul(x, mul(y, z)),
        "multiplication is commutative": lambda x, y, z: mul(x, y) == mul(y, x),
        "1 is the multiplicative unit": lambda x, y, z: mul(x, one) == x,
        "involution: //x = x": lambda x, y, z: inv(inv(x)) == x,
        "involution is multiplicative: /(xy) = /x /y": lambda x, y, z: inv(mul(x, y)) == mul(inv(x), inv(y)),
        "distributive with 0z: xz + yz = (x + y)z + 0z": lambda x, y, z: (
            add(mul(x, z), mul(y, z)) == add(mul(add(x, y), z), mul(zero, z))
        ),
        "division law: x/y + z + 0y = (x + yz)/y": lambda x, y, z: (
            add(add(div(x, y), z), mul(zero, y)) == div(add(x, mul(y, z)), y)
        ),
        "0 * 0 = 0": lambda x, y, z: mul(zero, zero) == zero,
        "absorption: (x + 0y)z = xz + 0y": lambda x, y, z: mul(add(x, mul(zero, y)), z) == add(mul(x, z), mul(zero, y)),
        "involution of absorption: /(x + 0y) = /x + 0y": lambda x, y, z: (
            inv(add(x, mul(zero, y))) == add(inv(x), mul(zero, y))
        ),
        "bottom absorbs addition: 0/0 + x = 0/0": lambda x, y, z: add(div(zero, zero), x) == div(zero, zero),
        "derived: x/x = 1 + 0x/x": lambda x, y, z: div(x, x) == add(one, mul(mul(zero, x), inv(x))),
        "derived: 0x + 0y = 0xy": lambda x, y, z: add(mul(zero, x), mul(zero, y)) == mul(zero, mul(x, y)),
        "derived: bottom absorbs multiplication": lambda x, y, z: mul(div(zero, zero), x) == div(zero, zero),
    }


def axiom_failures(triples: Sequence[tuple[Wheel, Wheel, Wheel]], ops: Ops | None = None) -> dict[str, int]:
    """Per axiom name, the number of triples on which it fails."""
    laws = axioms(ops or standard_ops())
    return {name: sum(1 for t in triples if not law(*t)) for name, law in laws.items()}


def solve(matrix: Sequence[Sequence[Fraction | int]], rhs: Sequence[Fraction | int]) -> list[Wheel]:
    """Gaussian elimination in natural pivot order over wheel elements, then back substitution."""
    n = len(rhs)
    m = [[Wheel(v) for v in row] for row in matrix]
    v = [Wheel(value) for value in rhs]
    for c in range(n):
        pivot = m[c][c].inv()
        for i in range(c + 1, n):
            factor = m[i][c] * pivot
            for j in range(c, n):
                m[i][j] = m[i][j] - factor * m[c][j]
            v[i] = v[i] - factor * v[c]
    x = [ZERO] * n
    for i in reversed(range(n)):
        total = v[i]
        for j in range(i + 1, n):
            total = total - m[i][j] * x[j]
        x[i] = total * m[i][i].inv()
    return x


def fraction_solve(matrix: Sequence[Sequence[Fraction | int]], rhs: Sequence[Fraction | int]) -> list[Fraction]:
    """Gaussian elimination over Q in natural pivot order; raises ZeroDivisionError on a zero pivot."""
    n = len(rhs)
    m = [[Fraction(v) for v in row] for row in matrix]
    v = [Fraction(value) for value in rhs]
    for c in range(n):
        for i in range(c + 1, n):
            factor = m[i][c] / m[c][c]
            for j in range(c, n):
                m[i][j] -= factor * m[c][j]
            v[i] -= factor * v[c]
    x = [ZERO_Q] * n
    for i in reversed(range(n)):
        x[i] = (v[i] - sum((m[i][j] * x[j] for j in range(i + 1, n)), ZERO_Q)) / m[i][i]
    return x


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def pool() -> list[Wheel]:
    rationals = [Fraction(n, d) for n, d in ((2, 1), (-3, 2), (5, 3), (-1, 4), (7, 5))]
    return [ZERO, ONE, Wheel(-1), INFINITY, BOTTOM, *(Wheel(q) for q in rationals)]


def random_element(rng: random.Random) -> Wheel:
    roll = rng.random()
    if roll < 0.1:
        return INFINITY
    if roll < 0.2:
        return BOTTOM
    if roll < 0.3:
        return ZERO
    return Wheel(Fraction(rng.randint(-9, 9), rng.randint(1, 9)))


def self_test() -> int:
    elements = pool()
    triples = [(x, y, z) for x, y, z in itertools.product(elements, repeat=3)]
    rng = random.Random(SELF_TEST_SEED)
    triples += [(random_element(rng), random_element(rng), random_element(rng)) for _ in range(RANDOM_TRIPLES)]
    failures = axiom_failures(triples)
    require(not any(failures.values()), f"wheel axioms fail: {[k for k, v in failures.items() if v]}")
    print(f"{len(failures)} wheel axioms hold on {len(triples)} triples")

    require(INFINITY == ONE / ZERO and BOTTOM == ZERO / ZERO, "1/0 or 0/0 is not canonical")
    require(ZERO * INFINITY == BOTTOM, "0 * infinity is not bottom")
    require(INFINITY - INFINITY == BOTTOM, "infinity - infinity is not bottom")
    require(Wheel(3) / Wheel(3) == ONE and ZERO / ZERO == BOTTOM, "x/x is not 1 + 0x/x on 3 or 0")
    require(-INFINITY == INFINITY, "infinity is not its own negative")
    require(Wheel(Fraction(1, 3)) + Wheel(Fraction(1, 6)) == Wheel(Fraction(1, 2)), "finite addition differs from Q")

    # A wheel that collapses bottom to zero is a field with a broken division;
    # the absorption and bottom axioms must reject it.
    def collapse(w: Wheel) -> Wheel:
        return ZERO if w.bottom else w

    broken: Ops = (lambda a, b: collapse(a + b), lambda a, b: collapse(a * b), lambda a: collapse(a.inv()))
    broken_failures = axiom_failures(triples, broken)
    rejected = sorted(name for name, count in broken_failures.items() if count)
    require(bool(rejected), "the axioms accept a wheel with bottom collapsed to zero")
    print(f"bottom collapsed to zero breaks {len(rejected)} axioms: {rejected}")

    nonsingular = [[4, 1, 0], [1, 3, 1], [0, 1, 2]]
    rhs = [Fraction(1, 2), Fraction(-3), Fraction(7, 4)]
    exact = fraction_solve(nonsingular, rhs)
    wheel = solve(nonsingular, rhs)
    require(all(w.finite and w.value() == q for w, q in zip(wheel, exact, strict=True)), "wheel solve differs from Q")
    singular = [[1, 1, 0], [1, 1, 0], [0, 0, 1]]
    consistent = solve(singular, [2, 2, 1])
    require([w.kind() for w in consistent] == ["bottom", "bottom", "bottom"], f"consistent singular: {consistent}")
    inconsistent = solve([[1, 1], [1, 1]], [1, 2])
    require([w.kind() for w in inconsistent] == ["infinity", "infinity"], f"inconsistent singular: {inconsistent}")
    try:
        fraction_solve(singular, [2, 2, 1])
    except ZeroDivisionError:
        pass
    else:
        raise SystemExit("Fraction elimination accepted a zero pivot")
    print("wheel solve: nonsingular equals Q, consistent singular gives bottom, inconsistent gives infinity")
    print("self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    require(args.self_test, "nothing to do: pass --self-test")
    return self_test()


if __name__ == "__main__":
    raise SystemExit(main())
