"""Check that the recursive pair tower of proofs/CdImaginarySumConference.v multiplies basis units as cd_core.cd_sign.

The Rocq tower stores a level-(j + 1) element as a pair of level-j elements, coordinate i in the first half when
i < 2^j, and multiplies (a, b)(c, d) = (ac - conj(d) b, da + b conj(c)). This script transcribes that recursion onto
coordinate lists and requires e_a e_b = cd_sign(n, a, b) e_(a XOR b) for every a, b and n = 2 to 64, and the
imaginary sum (s, 1 + s) to equal e_1 + ... + e_(n-1). The Rocq theorems hold for the tower; this finite check
carries them to the sign table the census reads.

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
    if failures:
        raise SystemExit("tower and cd_sign differ: " + ", ".join(failures))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
