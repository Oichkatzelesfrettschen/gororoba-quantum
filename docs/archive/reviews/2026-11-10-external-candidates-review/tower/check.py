"""Exact checks of the sedenion claims in the reviewed tower text.

Run from the repository root: ``"$PYTHON" PATH/check.py``. Every product goes
through ``cd_core``; the arithmetic is rational, so each printed count is exact.
"""

import sys
from fractions import Fraction
from pathlib import Path

import sympy

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "gororoba_quantum"))

from cd_core import cd_multiply_exact, cd_sign  # noqa: E402

DIM = 16


def closed_form(dim: int) -> int:
    """The reviewed closed form N(D) = (D - 2)(D - 4)(D + 6) / 2."""
    return (dim - 2) * (dim - 4) * (dim + 6) // 2


def unit(index: int, coefficient: int = 1) -> list[Fraction]:
    vector = [Fraction(0)] * DIM
    vector[index] = Fraction(coefficient)
    return vector


def add(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    return [a + b for a, b in zip(left, right, strict=True)]


def chi(i: int, j: int, k: int, m: int) -> int:
    return cd_sign(DIM, i, k) * cd_sign(DIM, j, m) * cd_sign(DIM, i, m) * cd_sign(DIM, j, k)


def recurrence() -> None:
    for dim in (4, 8, 16, 32):
        pasted = 4 * closed_form(dim) + (dim - 2) * (dim - 4) * (3 * dim + 4)
        exact = 4 * closed_form(dim) + 2 * (dim - 2) * (dim * dim + 2 * dim + 18)
        print(f"D={dim}: N(2D)={closed_form(2 * dim)} pasted recurrence={pasted} corrected recurrence={exact}")


def rounding() -> None:
    for exponent in (53, 52):
        u = 2.0**-exponent
        print(f"u=2^-{exponent}: (1+u/2)+u/2={(1.0 + u / 2) + u / 2!r} 1+(u/2+u/2)={1.0 + (u / 2 + u / 2)!r}")


def skeleton() -> None:
    pairs = [(i, j) for i in range(1, DIM) for j in range(i + 1, DIM)]
    disjoint = [(a, b) for a in pairs for b in pairs if not set(a) & set(b) and a[0] ^ a[1] == b[0] ^ b[1]]
    positive = sum(chi(*a, *b) == 1 for a, b in disjoint)
    print(
        f"ordered disjoint pairs with equal XOR: {len(disjoint)}; with chi=+1: {positive}; unordered: {positive // 2}"
    )
    by_class: dict[int, int] = {}
    for a, b in ((a, b) for a in pairs for b in pairs if not set(a) & set(b)):
        for s in (1, -1):
            for t in (1, -1):
                x = add(unit(a[0]), unit(a[1], s))
                y = add(unit(b[0]), unit(b[1], t))
                if not any(cd_multiply_exact(DIM, x, y)):
                    by_class[a[0] ^ a[1]] = by_class.get(a[0] ^ a[1], 0) + 1
    print(f"signed zero products per XOR class: {dict(sorted(by_class.items()))}; total {sum(by_class.values())}")


def inverses() -> None:
    x = add(unit(1), unit(10))
    half_conjugate = [Fraction(0)] * DIM
    half_conjugate[1] = half_conjugate[10] = Fraction(-1, 2)
    one = (Fraction(1), *[Fraction(0)] * (DIM - 1))
    columns = [cd_multiply_exact(DIM, x, unit(c)) for c in range(DIM)]
    kernel = sympy.Matrix(DIM, DIM, lambda r, c: columns[c][r]).nullspace()
    two_sided = 0
    for vector in kernel:
        z = add(half_conjugate, [Fraction(int(v.p), int(v.q)) for v in vector])
        two_sided += cd_multiply_exact(DIM, x, z) == one and cd_multiply_exact(DIM, z, x) == one
    print(f"e1+e10: dim ker L_x={len(kernel)}; kernel basis shifts of conj(x)/2 that invert on both sides: {two_sided}")


def main() -> None:
    recurrence()
    rounding()
    skeleton()
    inverses()


if __name__ == "__main__":
    main()
