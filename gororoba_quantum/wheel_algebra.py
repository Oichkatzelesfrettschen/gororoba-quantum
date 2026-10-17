"""The wheel of fractions over Q: total division, with /0 = infinity and 0/0 = bottom.

Source: J. Carlstrom, "Wheels - On Division by Zero", Research Reports in
Mathematics 2001:11, Stockholm University (version of record: Math. Struct.
in Comp. Science 14(1) (2004) 143-184). docs/notes/wheels-carlstrom.md binds
the retained report and its page references; pages below are the report's
printed page numbers.

The wheel of fractions S(.)A of a commutative ring A with respect to a
multiplicative submonoid S (section 1.2, pp. 4-5) is A x A modulo
(x, y) == (x', y') iff (s x, s y) = (s' x', s' y') for some s, s' in S, with

- [x, y] + [x', y'] = [x y' + x' y, y y'];
- [x, y] [x', y'] = [x x', y y'];
- /[x, y] = [y, x], the reciprocal, an involution of the multiplicative
  monoid (Definition 2.1, p. 8).

This module takes A = Q and S = Q minus 0, which gives Q together with /0
and 0/0 (p. 6, example 1, there as Z minus 0 over Z). Every class has one
canonical pair: (q, 1) for a rational q, infinity = (1, 0) = /0, and
bottom = (0, 0) = 0/0 (the names follow p. 3). Division a / b is a * /b, so
a zero divisor yields infinity or bottom instead of raising.

``axioms`` names each law by its label in the report:

- Definition 1.1 (p. 5): (1) <W, 0, +> is a commutative monoid; (2)
  <W, 1, *, /> is a commutative monoid with involution /, which gives
  //x = x and /(xy) = /x /y; (3) (x + y)z + 0z = xz + yz; (4)
  x/y + z + 0y = (x + yz)/y; (5) 0 * 0 = 0; (6) (x + 0y)z = xz + 0y; (7)
  /(x + 0y) = /x + 0y; (8) x + 0/0 = 0/0.
- Proposition 4.3 (p. 24), derived rules: (10) 0x + 0y = 0xy; (11)
  (0/0)x = 0/0; (12) x/x = 1 + 0x/x.

0 * x = 0 fails at x = infinity (0 * infinity = bottom), and x - x = 0
fails at x = infinity (infinity + infinity = bottom); the report's x - x =
0x^2 (p. 5) holds instead.

``solve`` runs Gaussian elimination in natural pivot order over wheel
elements with no zero test anywhere. On a symmetric positive semidefinite
matrix with a right side in its column space (a Gram or normal-equations
system), every component is finite if and only if the matrix is positive
definite, and every component is bottom otherwise: the first zero pivot has
a zero row in the Schur complement, so the rows below it multiply 0 by its
reciprocal /0 and become bottom, and bottom absorbs every later operation
by (8) and (11). Outside that class a bottom or infinite component carries
no consistency or kernel information: solve([[0, -1], [0, -1]], [-1, 0]) is
inconsistent and returns bottom, and solve([[1, 1], [1, 1]], [1, 2]) is
inconsistent and returns infinity.

``--self-test`` checks every axiom over every triple of a pool holding 0, 1,
-1, infinity, bottom and nonzero rationals, plus seeded random triples, as
(law, triple) cases generated in the seeded order and mapped in chunks
through parallel.ordered_map; the non-field facts above; a mutated wheel
that maps bottom to zero, which the axioms must reject; ``solve`` against
Fraction elimination on positive definite Gram systems and its all-bottom
result on singular consistent Gram systems; and the two inconsistent
examples above as the documented limitation.
"""

from __future__ import annotations

import argparse
import itertools
import random
from collections.abc import Callable, Sequence
from fractions import Fraction

import parallel

SELF_TEST_SEED = 20041027
RANDOM_TRIPLES = 2000
GRAM_TRIALS = 40
# (law, triple) cases per ordered_map item: enough work per item to repay the
# transfer of its Wheel triples.
CASES_PER_CHUNK = 2048

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

    def __getstate__(self) -> tuple[Fraction, Fraction]:
        return self.x, self.y

    def __setstate__(self, state: tuple[Fraction, Fraction]) -> None:
        self.x, self.y = state

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
        """The involution /[x, y] = [y, x]."""
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
Triple = tuple[Wheel, Wheel, Wheel]


def collapse(w: Wheel) -> Wheel:
    """The mutation the self-test rejects: bottom mapped to zero."""
    return ZERO if w.bottom else w


def operations(name: str) -> Ops:
    """The wheel operations ("standard") or the bottom-collapsed mutation ("collapsed")."""
    if name == "standard":
        return (lambda a, b: a + b, lambda a, b: a * b, lambda a: a.inv())
    if name == "collapsed":
        return (lambda a, b: collapse(a + b), lambda a, b: collapse(a * b), lambda a: collapse(a.inv()))
    raise ValueError(f"unknown operations {name!r}")


def axioms(ops: Ops) -> dict[str, Callable[[Wheel, Wheel, Wheel], bool]]:
    """Carlstrom's wheel axioms (Definition 1.1) and derived rules (Proposition 4.3), each a predicate on a triple."""
    add, mul, inv = ops
    zero, one = ZERO, ONE

    def div(a: Wheel, b: Wheel) -> Wheel:
        return mul(a, inv(b))

    return {
        "(1) addition is associative": lambda x, y, z: add(add(x, y), z) == add(x, add(y, z)),
        "(1) addition is commutative": lambda x, y, z: add(x, y) == add(y, x),
        "(1) 0 is the additive unit": lambda x, y, z: add(x, zero) == x,
        "(2) multiplication is associative": lambda x, y, z: mul(mul(x, y), z) == mul(x, mul(y, z)),
        "(2) multiplication is commutative": lambda x, y, z: mul(x, y) == mul(y, x),
        "(2) 1 is the multiplicative unit": lambda x, y, z: mul(x, one) == x,
        "(2) involution: //x = x": lambda x, y, z: inv(inv(x)) == x,
        "(2) involution is multiplicative: /(xy) = /x /y": lambda x, y, z: inv(mul(x, y)) == mul(inv(x), inv(y)),
        "(3) distributive: (x + y)z + 0z = xz + yz": lambda x, y, z: (
            add(mul(add(x, y), z), mul(zero, z)) == add(mul(x, z), mul(y, z))
        ),
        "(4) division: x/y + z + 0y = (x + yz)/y": lambda x, y, z: (
            add(add(div(x, y), z), mul(zero, y)) == div(add(x, mul(y, z)), y)
        ),
        "(5) 0 * 0 = 0": lambda x, y, z: mul(zero, zero) == zero,
        "(6) (x + 0y)z = xz + 0y": lambda x, y, z: mul(add(x, mul(zero, y)), z) == add(mul(x, z), mul(zero, y)),
        "(7) /(x + 0y) = /x + 0y": lambda x, y, z: inv(add(x, mul(zero, y))) == add(inv(x), mul(zero, y)),
        "(8) x + 0/0 = 0/0": lambda x, y, z: add(x, div(zero, zero)) == div(zero, zero),
        "(10) 0x + 0y = 0xy": lambda x, y, z: add(mul(zero, x), mul(zero, y)) == mul(zero, mul(x, y)),
        "(11) (0/0)x = 0/0": lambda x, y, z: mul(div(zero, zero), x) == div(zero, zero),
        "(12) x/x = 1 + 0x/x": lambda x, y, z: div(x, x) == add(one, mul(mul(zero, x), inv(x))),
    }


class AxiomCases:
    """The failing laws among one chunk of (law, triple) cases, under the named operations."""

    def __init__(self, ops: str) -> None:
        self.ops = ops

    def __call__(self, chunk: list[tuple[str, Triple]]) -> list[str]:
        laws = axioms(operations(self.ops))
        return [law for law, triple in chunk if not laws[law](*triple)]


def axiom_failures(triples: Sequence[Triple], ops: str = "standard") -> dict[str, int]:
    """Per axiom name, the number of triples on which it fails.

    The cases are generated law by law in the given triple order, then mapped
    in fixed chunks through parallel.ordered_map, so a pooled run counts
    exactly what the serial loop counts.
    """
    names = list(axioms(operations(ops)))
    cases = [(law, triple) for law in names for triple in triples]
    chunks = [cases[start : start + CASES_PER_CHUNK] for start in range(0, len(cases), CASES_PER_CHUNK)]
    failures = dict.fromkeys(names, 0)
    for failed in parallel.ordered_map(AxiomCases(ops), chunks, min_items=2):
        for law in failed:
            failures[law] += 1
    return failures


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


def gram_system(rng: random.Random, rows: int, cols: int, dependent: int | None) -> tuple[list[list[int]], list[int]]:
    """A^T A and A^T b for an integer A; column `dependent` (>= 1) repeats the sum of the columns before it."""
    a = [[rng.randint(-5, 5) for _ in range(cols)] for _ in range(rows)]
    if dependent is not None:
        for row in a:
            row[dependent] = sum(row[:dependent])
    b = [rng.randint(-5, 5) for _ in range(rows)]
    gram = [[sum(r[i] * r[j] for r in a) for j in range(cols)] for i in range(cols)]
    return gram, [sum(r[i] * bi for r, bi in zip(a, b, strict=True)) for i in range(cols)]


def self_test() -> int:
    elements = pool()
    triples: list[Triple] = [(x, y, z) for x, y, z in itertools.product(elements, repeat=3)]
    rng = random.Random(SELF_TEST_SEED)
    triples += [(random_element(rng), random_element(rng), random_element(rng)) for _ in range(RANDOM_TRIPLES)]
    failures = axiom_failures(triples)
    require(not any(failures.values()), f"wheel axioms fail: {[k for k, v in failures.items() if v]}")
    print(f"{len(failures)} wheel axioms hold on {len(triples)} triples")

    require(INFINITY == ONE / ZERO and BOTTOM == ZERO / ZERO, "/0 or 0/0 is not canonical")
    require(ZERO * INFINITY == BOTTOM, "0 * infinity is not bottom")
    require(INFINITY - INFINITY == BOTTOM, "infinity - infinity is not bottom")
    for x in elements:
        require(x - x == ZERO * x * x, f"x - x differs from 0x^2 at {x!r}")
    require(-INFINITY == INFINITY, "infinity is not its own negative")
    require(Wheel(Fraction(1, 3)) + Wheel(Fraction(1, 6)) == Wheel(Fraction(1, 2)), "finite addition differs from Q")

    broken_failures = axiom_failures(triples, "collapsed")
    rejected = sorted(name for name, count in broken_failures.items() if count)
    require(bool(rejected), "the axioms accept a wheel with bottom collapsed to zero")
    print(f"bottom collapsed to zero breaks {len(rejected)} axioms: {rejected}")

    for trial in range(GRAM_TRIALS):
        cols = 2 + trial % 4
        dependent = None if trial % 2 == 0 else 1 + (trial // 2) % (cols - 1)
        gram, rhs = gram_system(rng, 6, cols, dependent)
        wheel = solve(gram, rhs)
        if dependent is not None:
            require(all(w.bottom for w in wheel), f"singular Gram system {gram}: {wheel}")
        else:
            exact = fraction_solve(gram, rhs)
            require(all(w.finite and w.value() == q for w, q in zip(wheel, exact, strict=True)), f"Gram {gram}")
    print(f"{GRAM_TRIALS} Gram systems: positive definite equals Q, singular gives bottom in every component")

    # Outside positive semidefinite systems with a right side in the column
    # space the kinds carry no consistency information: both are inconsistent.
    limitation = solve([[0, -1], [0, -1]], [-1, 0])
    require([w.kind() for w in limitation] == ["bottom", "bottom"], f"nonsymmetric example: {limitation}")
    other = solve([[1, 1], [1, 1]], [1, 2])
    require([w.kind() for w in other] == ["infinity", "infinity"], f"singular example: {other}")
    try:
        fraction_solve([[1, 1, 0], [1, 1, 0], [0, 0, 1]], [2, 2, 1])
    except ZeroDivisionError:
        pass
    else:
        raise SystemExit("Fraction elimination accepted a zero pivot")
    print("documented limitation: two inconsistent systems return bottom and infinity")
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
