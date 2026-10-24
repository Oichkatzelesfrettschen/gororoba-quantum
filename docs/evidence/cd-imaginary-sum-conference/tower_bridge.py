"""Check that the recursive pair tower of proofs/CdImaginarySumConference.v multiplies basis units as cd_core.cd_sign.

The Rocq tower stores a level-(j + 1) element as a pair of level-j elements, coordinate i in the first half when
i < 2^j, and multiplies (a, b)(c, d) = (ac - conj(d) b, da + b conj(c)). This script transcribes that recursion onto
coordinate lists and requires e_a e_b = cd_sign(n, a, b) e_(a XOR b) for every a, b and n = 2 to 64, and the
imaginary sum (s, 1 + s) to equal e_1 + ... + e_(n-1). The Rocq theorems hold for the tower; this finite check
carries them to the sign table the census reads.

It also mirrors the Fixpoint sigma of proofs/CdTowerBasisSign.v, whose theorem basis_mul gives
e_a e_b = sigma_k(a, b) e_(a XOR b) for every k, and requires sigma_k(a, b) = cd_sign(2^k, a, b) on every pair
through n = 64. As a negative control, negating any one of sigma's four branches must disagree with cd_sign on some
pair at every n >= 4.

Usage: "$PYTHON" docs/evidence/cd-imaginary-sum-conference/tower_bridge.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from cd_core import cd_sign  # noqa: E402
from parallel import ordered_map  # noqa: E402

DIMENSIONS = (2, 4, 8, 16, 32, 64)

Vector = list[int]


def conjugate(x: Vector) -> Vector:
    return [x[0], *(-value for value in x[1:])]


def mul(x: Vector, y: Vector) -> Vector:
    if len(x) == 1:
        return [x[0] * y[0]]
    half = len(x) // 2
    a, b, c, d = x[:half], x[half:], y[:half], y[half:]
    first = [p - q for p, q in zip(mul(a, c), mul(conjugate(d), b), strict=True)]
    second = [p + q for p, q in zip(mul(d, a), mul(b, conjugate(c)), strict=True)]
    return first + second


def imaginary_sum(n: int) -> Vector:
    if n == 1:
        return [0]
    lower = imaginary_sum(n // 2)
    return lower + [lower[0] + 1, *lower[1:]]


def sigma(k: int, p: int, q: int, flip: int | None = None) -> int:
    """The Rocq Fixpoint sigma branch for branch; flip negates one branch, numbered in source order."""
    if k == 0:
        return 1
    half = 1 << (k - 1)
    if p < half and q < half:
        branch, value = 0, sigma(k - 1, p, q, flip)
    elif p < half:
        branch, value = 1, sigma(k - 1, q - half, p, flip)
    elif q < half:
        branch, value = 2, (1 if q == 0 else -1) * sigma(k - 1, p - half, q, flip)
    else:
        branch, value = 3, -1 if q - half == 0 else sigma(k - 1, q - half, p - half, flip)
    return -value if branch == flip else value


def sigma_disagreements(task: tuple[int, int, int | None]) -> int:
    n, a, flip = task
    k = n.bit_length() - 1
    return sum(sigma(k, a, b, flip) != cd_sign(n, a, b) for b in range(n))


def row_matches(task: tuple[int, int]) -> bool:
    n, a = task
    unit_a = [int(i == a) for i in range(n)]
    for b in range(n):
        expected = [0] * n
        expected[a ^ b] = cd_sign(n, a, b)
        if mul(unit_a, [int(i == b) for i in range(n)]) != expected:
            return False
    return True


def main() -> int:
    failures = []
    for n in DIMENSIONS:
        if imaginary_sum(n) != [0] + [1] * (n - 1):
            failures.append(f"imaginary sum at n = {n}")
        rows = ordered_map(row_matches, [(n, a) for a in range(n)], min_items=1)
        failures += [f"row {a} at n = {n}" for a, ok in enumerate(rows) if not ok]
        print(f"n = {n}: tower products match cd_sign on {sum(rows)} of {n} rows")
        for flip in (None, 0, 1, 2, 3):
            count = sum(ordered_map(sigma_disagreements, [(n, a, flip) for a in range(n)], min_items=1))
            if flip is None and count:
                failures.append(f"sigma differs from cd_sign on {count} pairs at n = {n}")
            elif flip is not None and n >= 4 and not count:
                failures.append(f"sigma with branch {flip} negated still matches cd_sign at n = {n}")
            if flip is None:
                print(f"n = {n}: sigma matches cd_sign on {n * n - count} of {n * n} pairs")
    if failures:
        raise SystemExit("tower and cd_sign differ: " + ", ".join(failures))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
