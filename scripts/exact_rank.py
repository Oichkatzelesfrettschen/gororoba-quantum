"""Exact rank modulo a prime and rational null spaces of integer matrices through FLINT.

rank_mod reduces an integer matrix modulo a word-size prime and eliminates in
FLINT's nmod_mat; the rank modulo a prime bounds the rational rank from below.
rational_kernel reads a null-space basis from FLINT's fmpq_mat reduced row
echelon form. That form is unique, so the basis (one vector per free column:
1 on the free column and minus the free column's entry of each pivot row on
that row's pivot column) depends on the matrix alone, and equals the basis the
Fraction elimination of moreno_stiefel_nullity.rational_kernel returns.
d_locus_nullity.nullity checks each kernel vector it certifies against the
integer matrix in Python arithmetic, so its upper bound on the rank rests on
no FLINT result.

--self-test compares both functions with moreno_stiefel_nullity's Fraction and
modular elimination on seeded integer matrices of every rank, wide, tall and
square, plus the left-multiplication matrices of sedenion and 32-ion zero
divisors, and requires equal ranks and equal Fraction bases.

Usage:
    "$PYTHON" scripts/exact_rank.py --self-test
"""

from __future__ import annotations

import argparse
import random
import sys
from fractions import Fraction
from pathlib import Path

import flint

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

SELF_TEST_SEED = 20261017
RANDOM_MATRICES = 240
ENTRY_RANGE = 6

Matrix = list[list[int]]


def rank_mod(matrix: Matrix, prime: int) -> int:
    """Rank of matrix modulo prime, a prime below 2^64, by nmod_mat elimination."""
    return flint.nmod_mat([[value % prime for value in row] for row in matrix], prime).rank()


def rational_kernel(matrix: Matrix) -> list[list[Fraction]]:
    """The null-space basis of the reduced row echelon form, one vector per free column."""
    reduced, rank = flint.fmpq_mat(matrix).rref()
    columns = reduced.ncols()
    pivots = [next(column for column in range(columns) if reduced[row, column] != 0) for row in range(rank)]
    basis = []
    for free in (column for column in range(columns) if column not in pivots):
        vector = [Fraction(0)] * columns
        vector[free] = Fraction(1)
        for row, pivot in enumerate(pivots):
            entry = reduced[row, free]
            vector[pivot] = -Fraction(int(entry.p), int(entry.q))
        basis.append(vector)
    return basis


def _random_matrix(rng: random.Random) -> Matrix:
    """A rows x columns integer product of rank at most inner, so every rank up to min(rows, columns) occurs."""
    rows, columns = rng.randint(1, 12), rng.randint(1, 12)
    inner = rng.randint(0, min(rows, columns))
    left = [[rng.randint(-ENTRY_RANGE, ENTRY_RANGE) for _ in range(inner)] for _ in range(rows)]
    right = [[rng.randint(-ENTRY_RANGE, ENTRY_RANGE) for _ in range(columns)] for _ in range(inner)]
    return [[sum(left[r][k] * right[k][c] for k in range(inner)) for c in range(columns)] for r in range(rows)]


def _zero_divisor_matrices() -> list[Matrix]:
    """D L_v for Cayley-frame zero divisors of A_4 and their brackets in A_5, nullity 4, 8 and 12."""
    from d_locus_nullity import bracket, frame_spaces, integer_rows, left_rational, zero_divisor

    matrices = []
    for seed in range(3):
        a = zero_divisor(10_000 + seed)
        span, annihilator = frame_spaces(a)
        matrices.append(integer_rows(left_rational(16, a)))
        for b in (span[2], annihilator[0], zero_divisor(20_000 + seed)):
            matrices.append(integer_rows(left_rational(32, bracket(a, b))))
    return matrices


def _compare(matrix: Matrix) -> tuple[int, int]:
    from moreno_stiefel_nullity import PRIME, SECOND_PRIME
    from moreno_stiefel_nullity import rank_mod as fraction_rank_mod
    from moreno_stiefel_nullity import rational_kernel as fraction_kernel

    for prime in (PRIME, SECOND_PRIME):
        rank = rank_mod(matrix, prime)
        if rank != fraction_rank_mod(matrix, prime):
            raise SystemExit(f"exact_rank: rank modulo {prime} differs on {matrix}")
    basis = rational_kernel(matrix)
    if basis != fraction_kernel(matrix) or not all(type(value) is Fraction for vector in basis for value in vector):
        raise SystemExit(f"exact_rank: rational kernel differs on {matrix}")
    return rank, len(basis)


def self_test() -> str:
    import parallel

    rng = random.Random(SELF_TEST_SEED)
    matrices = [_random_matrix(rng) for _ in range(RANDOM_MATRICES)]
    matrices += [[[0] * 5 for _ in range(3)], [[1, 2], [2, 4]], *_zero_divisor_matrices()]
    results = parallel.ordered_map(_compare, matrices, min_items=2)
    ranks = sorted({rank for rank, _ in results})
    nullities = sorted({nullity for _, nullity in results})
    return f"exact_rank: {len(matrices)} matrices agree; ranks {ranks}, nullities {nullities}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true", required=True)
    parser.parse_args()
    print(self_test())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
