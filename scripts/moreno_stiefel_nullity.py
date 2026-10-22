"""Exact nullity of left multiplication by Moreno's Stiefel elements in A_5 and A_6.

A Stiefel element of A_(n+1) is v = (a, b) with a and b pure in A_n, a orthogonal
to b and |a| = |b| != 0 (Moreno, math/0512517, Section 5), which asks whether
every Stiefel element is a zero divisor. v sits in the repository's doubling
convention: a on indices 0 .. 2^n - 1 and b on 2^n .. 2^(n+1) - 1, so that
(e1, e2) in A_4 is e1 + e10 (cd_core).

Generic rational points come from the Cayley transform: for a seeded skew-symmetric
integer matrix S of size m = 2^n - 1, Q = (I - S)(I + S)^-1 is an exactly rational
orthogonal matrix, so its first two columns are an orthonormal pure pair with no
square root or rescaling. A second family places small integers on disjoint
supports, b a signed permutation of a's values, which is exactly orthogonal and
equal-norm but non-generic.

Nullity is certified exactly. The integer matrix D L_v (D clears the
denominators of v) has rank at least its rank modulo the prime P, so full rank
modulo P proves nullity 0 over Q. A positive nullity k is certified by rank
2^(n+1) - k modulo P together with k exact rational kernel vectors with
L_v x = 0. L_v is checked against cd_core.cd_multiply_exact on small integer vectors.

Usage:
    "$PYTHON" scripts/moreno_stiefel_nullity.py --out docs/evidence/moreno_stiefel/nullity-exact-contracts.json
    "$PYTHON" scripts/moreno_stiefel_nullity.py --check docs/evidence/moreno_stiefel/nullity-exact-contracts.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from cd_core import cd_multiply_exact, cd_sign  # noqa: E402

PRIME = (1 << 61) - 1
SECOND_PRIME = 1_000_000_007
CAYLEY_POINTS = 24
DISJOINT_POINTS = 8
SKEW_RANGE = 2
ALGEBRAS = (5, 6)


def left_matrix(dim: int, v: list[int]) -> list[list[int]]:
    """L_v with (L_v x)_k = sum_j v_(k xor j) cd_sign(dim, k xor j, j) x_j."""
    return [[v[k ^ j] * cd_sign(dim, k ^ j, j) for j in range(dim)] for k in range(dim)]


def rank_mod(matrix: list[list[int]], prime: int) -> int:
    rows = [[value % prime for value in row] for row in matrix]
    rank, columns = 0, len(rows[0])
    for column in range(columns):
        pivot = next((r for r in range(rank, len(rows)) if rows[r][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column], prime - 2, prime)
        rows[rank] = [value * inverse % prime for value in rows[rank]]
        for r in range(len(rows)):
            if r != rank and rows[r][column]:
                factor = rows[r][column]
                rows[r] = [(x - factor * y) % prime for x, y in zip(rows[r], rows[rank], strict=True)]
        rank += 1
    return rank


def determinant_mod(matrix: list[list[int]], prime: int) -> int:
    """det(matrix) modulo prime by elimination with row swaps."""
    rows = [[value % prime for value in row] for row in matrix]
    size, det = len(rows), 1
    for column in range(size):
        pivot = next((r for r in range(column, size) if rows[r][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            det = -det
        det = det * rows[column][column] % prime
        inverse = pow(rows[column][column], prime - 2, prime)
        for r in range(column + 1, size):
            if rows[r][column]:
                factor = rows[r][column] * inverse % prime
                rows[r] = [(x - factor * y) % prime for x, y in zip(rows[r], rows[column], strict=True)]
    return det % prime


def rational_kernel(matrix: list[list[int]]) -> list[list[Fraction]]:
    """A basis of the rational null space by exact reduced row echelon form."""
    rows = [[Fraction(value) for value in row] for row in matrix]
    columns = len(rows[0])
    pivots: list[int] = []
    rank = 0
    for column in range(columns):
        pivot = next((r for r in range(rank, len(rows)) if rows[r][column] != 0), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        lead = rows[rank][column]
        rows[rank] = [value / lead for value in rows[rank]]
        for r in range(len(rows)):
            if r != rank and rows[r][column] != 0:
                factor = rows[r][column]
                rows[r] = [x - factor * y for x, y in zip(rows[r], rows[rank], strict=True)]
        pivots.append(column)
        rank += 1
    basis = []
    for free in (c for c in range(columns) if c not in pivots):
        vector = [Fraction(0)] * columns
        vector[free] = Fraction(1)
        for row, pivot in enumerate(pivots):
            vector[pivot] = -rows[row][free]
        basis.append(vector)
    return basis


def solve(matrix: list[list[Fraction]], rhs: list[Fraction]) -> list[Fraction]:
    size = len(matrix)
    rows = [row[:] + [value] for row, value in zip(matrix, rhs, strict=True)]
    for column in range(size):
        pivot = next(r for r in range(column, size) if rows[r][column] != 0)
        rows[column], rows[pivot] = rows[pivot], rows[column]
        lead = rows[column][column]
        rows[column] = [value / lead for value in rows[column]]
        for r in range(size):
            if r != column and rows[r][column] != 0:
                factor = rows[r][column]
                rows[r] = [x - factor * y for x, y in zip(rows[r], rows[column], strict=True)]
    return [row[size] for row in rows]


def cayley_frame(m: int, seed: int) -> tuple[list[Fraction], list[Fraction], list[int]]:
    """Columns 1 and 2 of Q = (I - S)(I + S)^-1 for a seeded skew-symmetric integer S."""
    rng = random.Random(seed)
    skew = [[0] * m for _ in range(m)]
    for i in range(m):
        for j in range(i + 1, m):
            value = rng.randint(-SKEW_RANGE, SKEW_RANGE)
            skew[i][j], skew[j][i] = value, -value
    plus = [[Fraction(int(i == j) + skew[i][j]) for j in range(m)] for i in range(m)]
    columns = []
    for unit in range(2):
        x = solve(plus, [Fraction(int(i == unit)) for i in range(m)])
        columns.append([x[i] - sum(skew[i][j] * x[j] for j in range(m)) for i in range(m)])
    return columns[0], columns[1], [skew[i][j] for i in range(m) for j in range(i + 1, m)]


def disjoint_pair(m: int, seed: int) -> tuple[list[Fraction], list[Fraction]]:
    """Small integers on half the pure coordinates and their signed permutation on the other half."""
    rng = random.Random(seed)
    coordinates = list(range(m))
    rng.shuffle(coordinates)
    half = m // 2
    values = [rng.choice((-3, -2, -1, 1, 2, 3)) for _ in range(half)]
    a, b = [Fraction(0)] * m, [Fraction(0)] * m
    order = list(range(half))
    rng.shuffle(order)
    for index, coordinate in enumerate(coordinates[:half]):
        a[coordinate] = Fraction(values[index])
    for index, coordinate in enumerate(coordinates[half : 2 * half]):
        b[coordinate] = Fraction(values[order[index]] * rng.choice((-1, 1)))
    return a, b


def element(n: int, a: list[Fraction], b: list[Fraction]) -> tuple[list[int], int]:
    """v = (a, b) in A_(n+1) as an integer vector D v, pure halves on indices 1 .. 2^n - 1 and 2^n + 1 .."""
    half = 1 << n
    v = [Fraction(0)] * (2 * half)
    for i, value in enumerate(a):
        v[1 + i] = value
    for i, value in enumerate(b):
        v[half + 1 + i] = value
    scale = math.lcm(*(value.denominator for value in v))
    return [int(value * scale) for value in v], scale


def certify(n: int, a: list[Fraction], b: list[Fraction]) -> dict[str, Any]:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a, norm_b = sum(x * x for x in a), sum(x * x for x in b)
    if dot != 0 or norm_a != norm_b or norm_a == 0:
        raise ValueError(f"not a Stiefel element: a.b = {dot}, |a|^2 = {norm_a}, |b|^2 = {norm_b}")
    dim = 1 << (n + 1)
    v, scale = element(n, a, b)
    matrix = left_matrix(dim, v)
    rank = rank_mod(matrix, PRIME)
    kernel_dimension = 0
    if rank < dim:
        kernel = rational_kernel(matrix)
        for vector in kernel:
            if any(sum(row[j] * vector[j] for j in range(dim)) != 0 for row in matrix):
                raise ValueError("a rational kernel vector fails L_v x = 0")
        kernel_dimension = len(kernel)
        if rank + kernel_dimension != dim:
            raise ValueError(f"rank {rank} modulo P and {kernel_dimension} kernel vectors do not bound the nullity")
    canonical = json.dumps([[str(x) for x in a], [str(x) for x in b]])
    return {
        "algebra_dimension": dim,
        "norm_squared": str(norm_a),
        "denominator_lcm_digits": len(str(scale)),
        "rank_mod_prime": rank,
        "nullity": dim - rank,
        "kernel_vectors_verified": kernel_dimension,
        "element_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
    }


def check_left_matrix() -> int:
    rng = random.Random(0)
    checked = 0
    for dim in (32, 64):
        for _ in range(4):
            v = [rng.randint(-3, 3) for _ in range(dim)]
            x = [rng.randint(-3, 3) for _ in range(dim)]
            matrix = left_matrix(dim, v)
            product = [sum(row[j] * x[j] for j in range(dim)) for row in matrix]
            if tuple(product) != cd_multiply_exact(dim, v, x):
                raise ValueError(f"L_v differs from cd_core.cd_multiply at dimension {dim}")
            checked += 1
    return checked


def measure() -> dict[str, Any]:
    algebras: dict[str, Any] = {}
    for n_plus_1 in ALGEBRAS:
        n = n_plus_1 - 1
        m = (1 << n) - 1
        cayley = []
        for seed in range(CAYLEY_POINTS):
            a, b, skew = cayley_frame(m, seed)
            cayley.append(
                {"seed": seed, "skew_sha256": hashlib.sha256(json.dumps(skew).encode()).hexdigest()} | certify(n, a, b)
            )
        disjoint = [{"seed": seed} | certify(n, *disjoint_pair(m, seed)) for seed in range(DISJOINT_POINTS)]
        algebras[f"A_{n_plus_1}"] = {
            "pure_coordinates": m,
            "cayley_points": cayley,
            "disjoint_support_points": disjoint,
            "nullities": sorted({point["nullity"] for point in cayley + disjoint}),
        }
    controls = []
    for label, b_terms in (
        ("Proposition 4.3: a = e1 + e2, b = e3 + e4 in H_a^perp", {3: 1, 4: 1}),
        ("Proposition 4.3: a = e1 + e2, b = a ee0 = e17 + e18", {17: 1, 18: 1}),
    ):
        a = [Fraction(int(i in (1, 2))) for i in range(1, 32)]
        b = [Fraction(b_terms.get(i, 0)) for i in range(1, 32)]
        result = certify(5, a, b)
        if result["nullity"] == 0:
            raise ValueError(f"{label}: Moreno's zero divisor reads nullity 0")
        controls.append({"element": label} | result)
    witness_a, witness_b = disjoint_pair(31, 0)
    witness, _ = element(5, witness_a, witness_b)
    return {
        "schema": "moreno-stiefel-exact-nullity-v1",
        "question": "math/0512517, Section 5 (p. 26): is every Stiefel element of A_(n+1) a zero divisor?",
        "method": (
            "Exact: rank of the integer matrix D L_v modulo P = 2^61 - 1 bounds the rational rank from below; "
            "positive nullity also carries that many exact rational kernel vectors."
        ),
        "prime": PRIME,
        "skew_entry_range": [-SKEW_RANGE, SKEW_RANGE],
        "cd_multiply_cross_checks": check_left_matrix(),
        "a6_integer_witness": {
            "seed": 0,
            "v": witness,
            "determinant_residues": {
                str(prime): determinant_mod(left_matrix(64, witness), prime) for prime in (PRIME, SECOND_PRIME)
            },
        },
        "a6_zero_divisor_controls": controls,
        "algebras": algebras,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    data = measure()
    rendered = json.dumps(data, indent=1, sort_keys=True) + "\n"
    if arguments.out is not None:
        arguments.out.parent.mkdir(parents=True, exist_ok=True)
        arguments.out.write_text(rendered)
    elif arguments.check.read_text() != rendered:
        raise SystemExit(f"Stiefel nullity evidence differs from {arguments.check}")
    for name, algebra in data["algebras"].items():
        points = algebra["cayley_points"] + algebra["disjoint_support_points"]
        print(f"{name}: {len(points)} Stiefel elements, nullities {algebra['nullities']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
