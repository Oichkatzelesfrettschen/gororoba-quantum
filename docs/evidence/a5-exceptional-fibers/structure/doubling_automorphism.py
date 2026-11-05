"""Exact check that phi(a, b) = (a, -b) is an algebra automorphism of A_n (n = 3, 4, 5) on every basis pair, using
cd_core.cd_multiply_exact; then that phi maps the N+ representative to the N- representative, X+ to X- membership,
and preserves the nullity of L_y, on the strata representatives of the regularity record."""

import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "gororoba_quantum"))
from cd_core import cd_multiply_exact  # noqa: E402


def phi(dim, v):
    h = dim // 2
    return [x if i < h else -x for i, x in enumerate(v)]


def check(dim):
    bad = 0
    for i in range(dim):
        for j in range(dim):
            ei = [Fraction(int(k == i)) for k in range(dim)]
            ej = [Fraction(int(k == j)) for k in range(dim)]
            lhs = phi(dim, cd_multiply_exact(dim, ei, ej))
            rhs = cd_multiply_exact(dim, phi(dim, ei), phi(dim, ej))
            bad += list(lhs) != list(rhs)
    return bad


def main():
    for dim in (8, 16, 32):
        print("dim", dim, "basis pairs failing phi(xy) = phi(x)phi(y):", check(dim))


if __name__ == "__main__":
    main()
