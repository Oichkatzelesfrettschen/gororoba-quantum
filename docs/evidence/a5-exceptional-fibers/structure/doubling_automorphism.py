"""Exact check that phi(a, b) = (a, -b) is an algebra automorphism of A_n (n = 3, 4, 5) on every basis pair.

Each basis pair (e_i, e_j) is checked with cd_core.cd_multiply_exact: phi(e_i e_j) = phi(e_i) phi(e_j). The pairs
are independent and run through parallel.ordered_map; the output lists the failing-pair count per dimension.
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "gororoba_quantum"))

import parallel  # noqa: E402
from cd_core import cd_multiply_exact  # noqa: E402

DIMS = (8, 16, 32)


def phi(dim: int, v: list[Fraction]) -> list[Fraction]:
    half = dim // 2
    return [x if i < half else -x for i, x in enumerate(v)]


def basis(dim: int, index: int) -> list[Fraction]:
    return [Fraction(int(k == index)) for k in range(dim)]


def pair_fails(job: tuple[int, int, int]) -> int:
    dim, i, j = job
    ei, ej = basis(dim, i), basis(dim, j)
    lhs = phi(dim, list(cd_multiply_exact(dim, ei, ej)))
    rhs = list(cd_multiply_exact(dim, phi(dim, ei), phi(dim, ej)))
    return int(lhs != rhs)


def main() -> int:
    jobs = [(dim, i, j) for dim in DIMS for i in range(dim) for j in range(dim)]
    fails = parallel.ordered_map(pair_fails, jobs, min_items=64)
    for dim in DIMS:
        bad = sum(f for (d, _, _), f in zip(jobs, fails, strict=True) if d == dim)
        print("dim", dim, "basis pairs failing phi(xy) = phi(x)phi(y):", bad)
    return 0


if __name__ == "__main__":
    sys.exit(main())
