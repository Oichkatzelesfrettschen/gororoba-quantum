#!/usr/bin/env python3
"""Exact rank gate for modular-to-characteristic-zero truncated fiber bounds.

Input is a JSON object with W and P matrices sharing a row count. Entries
are integers, rational strings (e.g. "3/7"), or [real, imaginary] Gaussian
rationals. The first matrix represents the subspace to be SUBTRACTED;
P represents the appended product columns. Reduction uses i -> root mod p.

This is a finite matrix checker, not a certificate of ambient good reduction,
header identity, or identification of the supplied columns with the source ideal.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

Gaussian = tuple[Fraction, Fraction]


def gaussian(value: Any) -> Gaussian:
    if isinstance(value, bool):
        raise ValueError("Boolean is not a matrix coefficient")
    if isinstance(value, (int, str)):
        return Fraction(value), Fraction(0)
    if isinstance(value, list) and len(value) == 2:
        return Fraction(value[0]), Fraction(value[1])
    raise ValueError(f"Invalid Gaussian-rational coefficient: {value!r}")


def add(a: Gaussian, b: Gaussian) -> Gaussian:
    return a[0] + b[0], a[1] + b[1]


def sub(a: Gaussian, b: Gaussian) -> Gaussian:
    return a[0] - b[0], a[1] - b[1]


def mul(a: Gaussian, b: Gaussian) -> Gaussian:
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def div(a: Gaussian, b: Gaussian) -> Gaussian:
    norm = b[0] * b[0] + b[1] * b[1]
    if norm == 0:
        raise ZeroDivisionError("Zero Gaussian pivot")
    return (
        (a[0] * b[0] + a[1] * b[1]) / norm,
        (a[1] * b[0] - a[0] * b[1]) / norm,
    )


def read_matrix(value: Any, name: str) -> list[list[Gaussian]]:
    if not isinstance(value, list) or any(not isinstance(row, list) for row in value):
        raise ValueError(f"{name} must be an array of rows")
    lengths = {len(row) for row in value}
    if len(lengths) > 1:
        raise ValueError(f"{name} is not rectangular")
    return [[gaussian(x) for x in row] for row in value]


def rank_qi(matrix: list[list[Gaussian]]) -> int:
    if not matrix:
        return 0
    m = [row.copy() for row in matrix]
    rows, columns = len(m), len(m[0])
    pivot_row = 0
    for col in range(columns):
        pivot = next((i for i in range(pivot_row, rows) if m[i][col] != (0, 0)), None)
        if pivot is None:
            continue
        m[pivot_row], m[pivot] = m[pivot], m[pivot_row]
        top = m[pivot_row][col]
        for i in range(pivot_row + 1, rows):
            if m[i][col] != (0, 0):
                factor = div(m[i][col], top)
                for j in range(col, columns):
                    m[i][j] = sub(m[i][j], mul(factor, m[pivot_row][j]))
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def reduce_entry(value: Gaussian, prime: int, root: int) -> int:
    def residue(q: Fraction) -> int:
        den = q.denominator % prime
        if den == 0:
            raise ValueError(f"Denominator {q.denominator} is not invertible mod {prime}")
        return (q.numerator % prime) * pow(den, -1, prime) % prime

    return (residue(value[0]) + root * residue(value[1])) % prime


def rank_mod(matrix: list[list[int]], prime: int) -> int:
    if not matrix:
        return 0
    m = [row.copy() for row in matrix]
    rows, columns = len(m), len(m[0])
    pivot_row = 0
    for col in range(columns):
        pivot = next((i for i in range(pivot_row, rows) if m[i][col] % prime), None)
        if pivot is None:
            continue
        m[pivot_row], m[pivot] = m[pivot], m[pivot_row]
        inv = pow(m[pivot_row][col] % prime, -1, prime)
        for i in range(pivot_row + 1, rows):
            factor = m[i][col] * inv % prime
            if factor:
                for j in range(col, columns):
                    m[i][j] = (m[i][j] - factor * m[pivot_row][j]) % prime
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1 if d == 2 else 2
    return True


def check(data: dict[str, Any]) -> dict[str, Any]:
    prime, root = data["prime"], data["i_root"]
    if not isinstance(prime, int) or isinstance(prime, bool) or not is_prime(prime):
        raise ValueError("prime must be a prime integer")
    if not isinstance(root, int) or root * root % prime != (prime - 1) % prime:
        raise ValueError("i_root must square to -1 modulo prime")
    w = read_matrix(data["W"], "W")
    p = read_matrix(data["P"], "P")
    if len(w) != len(p):
        raise ValueError("W and P must have equal row counts")
    if not w:
        raise ValueError("Supply at least one row; encode zero columns as empty rows")
    combined = [a + b for a, b in zip(w, p)]
    wm = [[reduce_entry(x, prime, root) for x in row] for row in w]
    cm = [[reduce_entry(x, prime, root) for x in row] for row in combined]
    rank_w_q = rank_qi(w)
    rank_w_p = rank_mod(wm, prime)
    rank_c_q = rank_qi(combined)
    rank_c_p = rank_mod(cm, prime)
    stable = rank_w_q == rank_w_p
    return {
        "prime": prime,
        "i_root": root,
        "rank_W_Qi": rank_w_q,
        "rank_W_Fp": rank_w_p,
        "rank_joined_Qi": rank_c_q,
        "rank_joined_Fp": rank_c_p,
        "truncated_difference_Qi": rank_c_q - rank_w_q,
        "truncated_difference_Fp": rank_c_p - rank_w_p,
        "subtracted_rank_stable": stable,
        "lower_bound_transfer_admissible": stable,
        "scope": "Finite matrices only; source and ambient good-reduction witnesses required separately",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON containing prime, i_root, W, P")
    parser.add_argument("--require-stable", action="store_true", help="Return nonzero if subtracted rank changes")
    args = parser.parse_args()
    try:
        result = check(json.loads(args.input.read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        print(f"rank gate: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return int(args.require_stable and not result["subtracted_rank_stable"])


if __name__ == "__main__":
    raise SystemExit(main())
