"""The wheel of fractions over the Gaussian rationals Q(i): total division with 1/0 = infinity and 0/0 = bottom.

Q(i) is a field, so its wheel of fractions (Carlstrom, "Wheels - On Division
by Zero", Math. Struct. Comp. Sci. 14 (2004) 143-184) is the set of pairs
(x, y) of Q(i) modulo (x, y) ~ (s x, s y) for nonzero s in Q(i), with the
operations of wheel_algebra: (x, y) + (x', y') = (x y' + x' y, y y'),
(x, y)(x', y') = (x x', y y') and /(x, y) = (y, x). Every class has one
canonical pair: (q, 1) for q in Q(i), infinity = (1, 0) and bottom = (0, 0).
The involution / is the wheel's reciprocal and is distinct from complex
conjugation, which ``GaussianRational.conjugate`` carries.

``GaussianRational`` holds a + b i as two Fractions with the standard library
alone, so CI imports it without a pin. ``solve`` is wheel_algebra.solve over
this wheel: Gaussian elimination in natural pivot order, with no branch in the
elimination, where a zero pivot becomes infinity through the involution. On a
Hermitian positive definite matrix every leading principal minor is a positive
rational (Sylvester), so every pivot is finite and nonzero and the result
equals ``gaussian_solve``. ``rank`` is exact elimination with a pivot search.

``--self-test`` checks Carlstrom's axioms (Definition 1.1 and the derived
identities wheel_algebra.axioms names) on every triple of a pool holding 0, 1,
-1, i, -i, 1 + i, two other Gaussian rationals, infinity and bottom, plus
seeded random triples; a mutant wheel that maps bottom to zero, which the
axioms reject; the non-field facts 0 * infinity = bottom and
infinity - infinity = bottom; and ``solve`` on a Hermitian positive definite,
a consistent singular and an inconsistent singular system.
"""

from __future__ import annotations

import argparse
import itertools
import random
from collections.abc import Callable, Sequence
from fractions import Fraction

SELF_TEST_SEED = 20041028
RANDOM_TRIPLES = 2000

Scalar = int | Fraction


class GaussianRational:
    """re + im i with re and im rational."""

    __slots__ = ("re", "im")

    re: Fraction
    im: Fraction

    def __init__(self, re: Scalar = 0, im: Scalar = 0) -> None:
        self.re, self.im = Fraction(re), Fraction(im)

    def __add__(self, other: GaussianRational) -> GaussianRational:
        return GaussianRational(self.re + other.re, self.im + other.im)

    def __sub__(self, other: GaussianRational) -> GaussianRational:
        return GaussianRational(self.re - other.re, self.im - other.im)

    def __mul__(self, other: GaussianRational) -> GaussianRational:
        return GaussianRational(self.re * other.re - self.im * other.im, self.re * other.im + self.im * other.re)

    def __neg__(self) -> GaussianRational:
        return GaussianRational(-self.re, -self.im)

    def __truediv__(self, other: GaussianRational) -> GaussianRational:
        """Field division; raises ZeroDivisionError on a zero divisor through Fraction."""
        modulus = other.modulus_squared()
        numerator = self * other.conjugate()
        return GaussianRational(numerator.re / modulus, numerator.im / modulus)

    def conjugate(self) -> GaussianRational:
        """Complex conjugation re - im i."""
        return GaussianRational(self.re, -self.im)

    def modulus_squared(self) -> Fraction:
        return self.re * self.re + self.im * self.im

    def scale(self, factor: Scalar) -> GaussianRational:
        return GaussianRational(self.re * factor, self.im * factor)

    def __bool__(self) -> bool:
        return bool(self.re) or bool(self.im)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int | Fraction):
            return self.re == other and not self.im
        return isinstance(other, GaussianRational) and self.re == other.re and self.im == other.im

    def __hash__(self) -> int:
        return hash((self.re, self.im))

    def __str__(self) -> str:
        sign = "-" if self.im < 0 else "+"
        return f"{self.re}{sign}{abs(self.im)}i"

    def __repr__(self) -> str:
        return f"GaussianRational({self.re}, {self.im})"


ZERO_Q = GaussianRational(0)
ONE_Q = GaussianRational(1)
I_Q = GaussianRational(0, 1)


class GaussianWheel:
    """One element of the wheel of fractions over Q(i), held as its canonical pair."""

    __slots__ = ("x", "y")

    x: GaussianRational
    y: GaussianRational

    def __init__(self, x: GaussianRational | Scalar, y: GaussianRational | Scalar = 1) -> None:
        x = x if isinstance(x, GaussianRational) else GaussianRational(x)
        y = y if isinstance(y, GaussianRational) else GaussianRational(y)
        if y:
            self.x, self.y = (x / y if y != ONE_Q else x), ONE_Q
        elif x:
            self.x, self.y = ONE_Q, ZERO_Q
        else:
            self.x, self.y = ZERO_Q, ZERO_Q

    def __add__(self, other: GaussianWheel) -> GaussianWheel:
        if self.y == ONE_Q and other.y == ONE_Q:
            return GaussianWheel(self.x + other.x)
        return GaussianWheel(self.x * other.y + other.x * self.y, self.y * other.y)

    def __mul__(self, other: GaussianWheel) -> GaussianWheel:
        return GaussianWheel(self.x * other.x, self.y * other.y)

    def __neg__(self) -> GaussianWheel:
        return GaussianWheel(-self.x, self.y)

    def __sub__(self, other: GaussianWheel) -> GaussianWheel:
        return self + (-other)

    def inv(self) -> GaussianWheel:
        """The involution /(x, y) = (y, x)."""
        return GaussianWheel(self.y, self.x)

    def __truediv__(self, other: GaussianWheel) -> GaussianWheel:
        return self * other.inv()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, GaussianWheel) and self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        return f"GaussianWheel({self.x}, {self.y})"

    def __str__(self) -> str:
        return str(self.x) if self.finite else self.kind()

    @property
    def finite(self) -> bool:
        return bool(self.y)

    @property
    def bottom(self) -> bool:
        return not self.y and not self.x

    @property
    def infinite(self) -> bool:
        return not self.y and bool(self.x)

    def value(self) -> GaussianRational:
        if not self.finite:
            raise ValueError(f"{self!r} is not a Gaussian rational")
        return self.x

    def kind(self) -> str:
        return "bottom" if self.bottom else "infinity" if self.infinite else "finite"


ZERO = GaussianWheel(0)
ONE = GaussianWheel(1)
IMAGINARY = GaussianWheel(I_Q)
INFINITY = GaussianWheel(1, 0)
BOTTOM = GaussianWheel(0, 0)

Ops = tuple[
    Callable[[GaussianWheel, GaussianWheel], GaussianWheel],
    Callable[[GaussianWheel, GaussianWheel], GaussianWheel],
    Callable[[GaussianWheel], GaussianWheel],
]
Triple = tuple[GaussianWheel, GaussianWheel, GaussianWheel]


def standard_ops() -> Ops:
    return (lambda a, b: a + b, lambda a, b: a * b, lambda a: a.inv())


def axioms(ops: Ops) -> dict[str, Callable[[GaussianWheel, GaussianWheel, GaussianWheel], bool]]:
    """Carlstrom's wheel axioms and derived identities, under the names wheel_algebra.axioms gives them."""
    add, mul, inv = ops
    zero, one = ZERO, ONE

    def div(a: GaussianWheel, b: GaussianWheel) -> GaussianWheel:
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


def axiom_failures(triples: Sequence[Triple], ops: Ops | None = None) -> dict[str, int]:
    """Per axiom name, the number of triples on which it fails."""
    laws = axioms(ops or standard_ops())
    return {name: sum(1 for t in triples if not law(*t)) for name, law in laws.items()}


Matrix = Sequence[Sequence[GaussianRational]]


def solve(matrix: Matrix, rhs: Sequence[GaussianRational]) -> list[GaussianWheel]:
    """Gaussian elimination in natural pivot order over wheel elements, then back substitution."""
    n = len(rhs)
    m = [[GaussianWheel(v) for v in row] for row in matrix]
    v = [GaussianWheel(value) for value in rhs]
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


def gaussian_solve(matrix: Matrix, rhs: Sequence[GaussianRational]) -> list[GaussianRational]:
    """Gaussian elimination over Q(i) in natural pivot order; raises ZeroDivisionError on a zero pivot."""
    n = len(rhs)
    m = [list(row) for row in matrix]
    v = list(rhs)
    for c in range(n):
        for i in range(c + 1, n):
            factor = m[i][c] / m[c][c]
            for j in range(c, n):
                m[i][j] = m[i][j] - factor * m[c][j]
            v[i] = v[i] - factor * v[c]
    x = [ZERO_Q] * n
    for i in reversed(range(n)):
        total = v[i]
        for j in range(i + 1, n):
            total = total - m[i][j] * x[j]
        x[i] = total / m[i][i]
    return x


def rank(matrix: Matrix) -> int:
    """Exact rank over Q(i) by elimination with a pivot search."""
    rows = [list(row) for row in matrix]
    found = 0
    for column in range(len(rows[0]) if rows else 0):
        pivot = next((r for r in range(found, len(rows)) if rows[r][column]), None)
        if pivot is None:
            continue
        rows[found], rows[pivot] = rows[pivot], rows[found]
        lead = rows[found][column]
        for r in range(found + 1, len(rows)):
            if rows[r][column]:
                factor = rows[r][column] / lead
                rows[r] = [x - factor * y for x, y in zip(rows[r], rows[found], strict=True)]
        found += 1
    return found


def hermitian_gram(matrix: Matrix) -> list[list[GaussianRational]]:
    """M^H M: Hermitian positive semidefinite, positive definite exactly when M has full column rank."""
    rows, columns = len(matrix), len(matrix[0])
    gram = []
    for r in range(columns):
        row = []
        for c in range(columns):
            total = ZERO_Q
            for k in range(rows):
                if matrix[k][r] and matrix[k][c]:
                    total = total + matrix[k][r].conjugate() * matrix[k][c]
            row.append(total)
        gram.append(row)
    return gram


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def pool() -> list[GaussianWheel]:
    values = [
        GaussianRational(-1),
        I_Q,
        -I_Q,
        GaussianRational(1, 1),
        GaussianRational(Fraction(1, 2), -3),
        GaussianRational(Fraction(-2, 3), Fraction(1, 5)),
    ]
    return [ZERO, ONE, INFINITY, BOTTOM, *(GaussianWheel(v) for v in values)]


def random_element(rng: random.Random) -> GaussianWheel:
    roll = rng.random()
    if roll < 0.1:
        return INFINITY
    if roll < 0.2:
        return BOTTOM
    if roll < 0.3:
        return ZERO
    re = Fraction(rng.randint(-9, 9), rng.randint(1, 9))
    return GaussianWheel(GaussianRational(re, Fraction(rng.randint(-9, 9), rng.randint(1, 9))))


def self_test() -> int:
    elements = pool()
    triples: list[Triple] = [(x, y, z) for x, y, z in itertools.product(elements, repeat=3)]
    rng = random.Random(SELF_TEST_SEED)
    triples += [(random_element(rng), random_element(rng), random_element(rng)) for _ in range(RANDOM_TRIPLES)]
    failures = axiom_failures(triples)
    require(not any(failures.values()), f"wheel axioms fail over Q(i): {[k for k, v in failures.items() if v]}")
    print(f"{len(failures)} wheel axioms hold over Q(i) on {len(triples)} triples")

    def collapse(w: GaussianWheel) -> GaussianWheel:
        return ZERO if w.bottom else w

    broken: Ops = (lambda a, b: collapse(a + b), lambda a, b: collapse(a * b), lambda a: collapse(a.inv()))
    rejected = sorted(name for name, count in axiom_failures(triples, broken).items() if count)
    require(bool(rejected), "the axioms accept a Q(i) wheel with bottom collapsed to zero")
    print(f"bottom collapsed to zero breaks {len(rejected)} axioms: {rejected}")

    require(INFINITY == ONE / ZERO and BOTTOM == ZERO / ZERO, "1/0 or 0/0 is not canonical")
    require(ZERO * INFINITY == BOTTOM and INFINITY - INFINITY == BOTTOM, "0 * infinity or infinity - infinity")
    require(IMAGINARY * INFINITY == INFINITY and -INFINITY == INFINITY, "i * infinity or -infinity is not infinity")
    require(IMAGINARY * IMAGINARY == GaussianWheel(-1) and IMAGINARY / IMAGINARY == ONE, "i^2 = -1 or i / i = 1 fails")
    half = GaussianRational(Fraction(1, 2), Fraction(-1, 2))
    require(ONE / GaussianWheel(GaussianRational(1, 1)) == GaussianWheel(half), "1 / (1 + i) is not (1 - i) / 2")
    require(GaussianRational(1, 2).conjugate() == GaussianRational(1, -2), "conjugation of 1 + 2i")

    a, b = GaussianRational(1, 1), GaussianRational(Fraction(1, 2), -1)
    hermitian = [
        [GaussianRational(4), a, ZERO_Q],
        [a.conjugate(), GaussianRational(3), b],
        [ZERO_Q, b.conjugate(), GaussianRational(2)],
    ]
    rhs = [GaussianRational(Fraction(1, 2)), GaussianRational(0, -3), GaussianRational(Fraction(7, 4), 1)]
    exact = gaussian_solve(hermitian, rhs)
    wheel = solve(hermitian, rhs)
    agree = all(w.finite and w.value() == q for w, q in zip(wheel, exact, strict=True))
    require(agree, "wheel solve differs from Q(i)")
    require(rank(hermitian) == 3, "the Hermitian positive definite fixture is not full rank")
    # [[1, i], [-i, 1]] is Hermitian positive semidefinite of rank 1, with range spanned by (1, -i).
    singular = [[ONE_Q, I_Q], [-I_Q, ONE_Q]]
    require(rank(singular) == 1, "the singular Hermitian fixture is not rank 1")
    consistent = solve(singular, [ONE_Q, -I_Q])
    require([w.kind() for w in consistent] == ["bottom", "bottom"], f"consistent singular: {consistent}")
    inconsistent = solve(singular, [ONE_Q, I_Q])
    require([w.kind() for w in inconsistent] == ["infinity", "infinity"], f"inconsistent singular: {inconsistent}")
    two, two_i = GaussianRational(2), GaussianRational(0, 2)
    require(hermitian_gram(singular) == [[two, two_i], [-two_i, two]], "M^H M of the singular fixture")
    try:
        gaussian_solve(singular, [ONE_Q, -I_Q])
    except ZeroDivisionError:
        pass
    else:
        raise SystemExit("elimination over Q(i) accepted a zero pivot")
    print("wheel solve over Q(i): Hermitian positive definite equals Q(i), consistent singular gives bottom")
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
