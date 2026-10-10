"""Non-circular checks of the cd_core port against open_gororoba ground truth.

The 42/168 triple split holds for any XOR-indexed sign convention, so it cannot
confirm the kernel's signs. These checks do: the sedenion zero-divisor set is
diffed against the kernel's own reggiani_standard_zero_divisor_pairs.csv, and
octonion norm multiplicativity exercises the sign table directly. The associator
operator W is shown to be a signed Z-string, which is the content of design A.
"""
from __future__ import annotations

import csv
import os
import random
from itertools import combinations
from math import isclose
from pathlib import Path

from cd_core import cd_multiply, left_mult_matrix_check, sedenion_zero_divisors

# The kernel ground-truth CSV lives in the open_gororoba checkout. GOROROBA_ROOT
# overrides its location; the default assumes a sibling checkout under ~/Github.
GOROROBA_ROOT = Path(os.environ.get("GOROROBA_ROOT", "~/Github/open_gororoba")).expanduser()
REGGIANI = str(GOROROBA_ROOT / "data/csv/reggiani_standard_zero_divisor_pairs.csv")


def norm_sq(v: list[float]) -> float:
    return sum(x * x for x in v)


def check_zero_divisors_against_kernel() -> tuple[int, int, bool]:
    """Diff sedenion_zero_divisors() against the kernel CSV (u_sign=+1 subset)."""
    kernel = set()
    with open(REGGIANI, newline="") as handle:
        for row in csv.DictReader(handle):
            if int(row["u_sign"]) != 1:
                continue
            a = (int(row["u_low"]), int(row["u_high"]))
            b = (int(row["v_low"]), int(row["v_high"]))
            kernel.add((a, b, int(row["v_sign"])))
    mine = {(a, b, s) for a, b, s in sedenion_zero_divisors()}
    return len(mine), len(kernel), mine == kernel


def check_octonion_norm_multiplicative(trials: int = 2000) -> bool:
    """|x y| = |x| |y| for octonions; this fails under a wrong sign table."""
    rng = random.Random(20261010)
    for _ in range(trials):
        x = [rng.gauss(0, 1) for _ in range(8)]
        y = [rng.gauss(0, 1) for _ in range(8)]
        lhs = norm_sq(cd_multiply(8, x, y))
        rhs = norm_sq(x) * norm_sq(y)
        if not isclose(lhs, rhs, rel_tol=1e-9, abs_tol=1e-9):
            return False
    return True


def check_sedenion_norm_not_multiplicative(trials: int = 4000) -> bool:
    """The sedenions carry zero divisors, so |x y| = |x| |y| must sometimes fail."""
    rng = random.Random(20261011)
    for _ in range(trials):
        x = [rng.gauss(0, 1) for _ in range(16)]
        y = [rng.gauss(0, 1) for _ in range(16)]
        if not isclose(norm_sq(cd_multiply(16, x, y)), norm_sq(x) * norm_sq(y),
                       rel_tol=1e-9, abs_tol=1e-9):
            return True
    return False


def check_w_is_signed_z_string() -> list[tuple[int, int, tuple[float, ...]]]:
    """W = L_{e_{i^j}}^{-1} L_{e_i} L_{e_j} is diagonal +/-1 for all 21 pairs.

    Its diagonal is a character of F_2^3 (a signed Z-string), +1 exactly on the
    subspace {0, i, j, i^j} of associating k. Returns (i, j, diagonal).
    """
    out = []
    for i, j in combinations(range(1, 8), 2):
        w = left_mult_matrix_check(i, j)
        diag = tuple(round(w[q][q], 9) for q in range(8))
        off = max(abs(w[r][c]) for r in range(8) for c in range(8) if r != c)
        assert off < 1e-9, f"W not diagonal for ({i},{j})"
        assert all(abs(abs(d) - 1.0) < 1e-9 for d in diag)
        subspace = {0, i, j, i ^ j}
        assert all((diag[q] > 0) == (q in subspace) for q in range(8))
        out.append((i, j, diag))
    return out


if __name__ == "__main__":
    mine, kernel, match = check_zero_divisors_against_kernel()
    print(f"zero divisors vs kernel CSV: mine={mine} kernel(u+)= {kernel} exact_match={match}")
    print(f"octonion norm multiplicative: {check_octonion_norm_multiplicative()}")
    print(f"sedenion norm sometimes non-multiplicative: {check_sedenion_norm_not_multiplicative()}")
    ws = check_w_is_signed_z_string()
    distinct = {w[2] for w in ws}
    print(f"associator W: all 21 pairs diagonal +/-1; distinct Z-strings = {len(distinct)}")
    print(f"  example ({ws[0][0]},{ws[0][1]}) diag = {ws[0][2]}")
    print(f"  identity partner e0 always associates: {all(d[0] > 0 for *_ , d in ws)}")
