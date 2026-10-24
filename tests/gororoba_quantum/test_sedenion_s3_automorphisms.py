"""Exact certificate of the sedenion S3 automorphisms epsilon and psi (Gresnigt, arXiv 2609.10569, Eqs. 60-62).

An element of Q(sqrt 3)^16 is a pair (a, b) of rational vectors meaning a + sqrt 3 b. epsilon negates the second
octonion half; psi mixes each half with its octonion conjugate and the other half (Eq. 61). Both maps must satisfy
T(e_p e_q) = T(e_p) T(e_q) on every basis pair under cd_core's product, with psi^3 = epsilon^2 = Id and
epsilon psi = psi^2 epsilon, so they generate an S3 inside the automorphism group of the cd_core sedenions
(docs/notes/papers/2609.10569.md).
"""

from fractions import Fraction

import cd_core
import parallel

N = 16
Vector = list[Fraction]
Element = tuple[Vector, Vector]


def unit(p: int) -> Vector:
    return [Fraction(int(i == p)) for i in range(N)]


def zero() -> Vector:
    return [Fraction(0)] * N


def conjugate(half: Vector) -> Vector:
    return [half[0], *(-x for x in half[1:])]


def psi_of_rational(x: Vector) -> Element:
    """psi(x) = (rational part, sqrt 3 part) for a rational vector x."""
    a, b = x[:8], x[8:]
    ac, bc = conjugate(a), conjugate(b)
    rational = [(a[i] + 3 * ac[i]) / 4 for i in range(8)] + [(b[i] + 3 * bc[i]) / 4 for i in range(8)]
    radical = [(b[i] - bc[i]) / 4 for i in range(8)] + [-(a[i] - ac[i]) / 4 for i in range(8)]
    return rational, radical


def psi(x: Element) -> Element:
    """psi on a + sqrt 3 b, by linearity over Q(sqrt 3)."""
    ra, sa = psi_of_rational(x[0])
    rb, sb = psi_of_rational(x[1])
    return [u + 3 * v for u, v in zip(ra, sb, strict=True)], [u + v for u, v in zip(sa, rb, strict=True)]


def epsilon(x: Element) -> Element:
    return tuple([*half[:8], *(-t for t in half[8:])] for half in x)  # type: ignore[return-value]


def multiply(x: Element, y: Element) -> Element:
    def mul(u: Vector, v: Vector) -> Vector:
        return list(cd_core.cd_multiply_exact(N, u, v))

    rational = [u + 3 * v for u, v in zip(mul(x[0], y[0]), mul(x[1], y[1]), strict=True)]
    radical = [u + v for u, v in zip(mul(x[0], y[1]), mul(x[1], y[0]), strict=True)]
    return rational, radical


def basis(p: int) -> Element:
    return unit(p), zero()


def product(p: int, q: int) -> Element:
    return [cd_core.cd_sign(N, p, q) * x for x in unit(p ^ q)], zero()


TRANSFORMS = {"psi": psi, "epsilon": epsilon}


def breaks_product(item: tuple[str, int, int]) -> bool:
    """Whether the named transform maps e_p e_q to something other than T(e_p) T(e_q)."""
    name, p, q = item
    transform = TRANSFORMS[name]
    return transform(product(p, q)) != multiply(transform(basis(p)), transform(basis(q)))


def breaks_relations(p: int) -> bool:
    """Whether psi^3 = epsilon^2 = Id or epsilon psi = psi^2 epsilon fails on e_p."""
    e = basis(p)
    return psi(psi(psi(e))) != e or epsilon(epsilon(e)) != e or epsilon(psi(e)) != psi(psi(epsilon(e)))


def test_psi_and_epsilon_preserve_every_basis_product() -> None:
    items = [(name, p, q) for name in TRANSFORMS for p in range(N) for q in range(N)]
    failing = [item for item, bad in zip(items, parallel.ordered_map(breaks_product, items), strict=True) if bad]
    if failing:
        raise AssertionError(f"T(e_p e_q) = T(e_p) T(e_q) fails at {failing}")


def test_psi_and_epsilon_satisfy_the_s3_relations() -> None:
    failing = [
        p for p, bad in zip(range(N), parallel.ordered_map(breaks_relations, list(range(N))), strict=True) if bad
    ]
    if failing:
        raise AssertionError(f"an S3 relation fails on e_p for p in {failing}")
