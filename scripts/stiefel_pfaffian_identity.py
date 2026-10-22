"""Pfaffian reduction and randomized identity test for Moreno's Stiefel question in A_5.

Moreno (math/0512517, Theorem 2.3) gives, for pure a, b in A_n,
L_(a,b)^2 = [[A, -S], [S, A]] with A = L_a^2 + R_b^2 and S = R_b L_a - L_a R_b.
The block matrix is the real form of the complex matrix A + iS, and
A + iS = (L_a + i R_b)(L_a - i R_b) term by term, with no commutation. For pure
a and b, L_a and R_b are skew-symmetric, so N = L_a + i R_b is a complex
skew-symmetric matrix and det N = Pf(N)^2. With a, b real,
det(L_(a,b))^2 = |det(A + iS)|^2 = |Pf(N)|^8, so (a, b) is a zero divisor of
A_(n+1) exactly when the degree-2^(n-1) polynomial Pf(L_a + i R_b) vanishes.

The Stiefel elements (|a| = |b|, a orthogonal to b) form the real points of
the complete intersection a.a = b.b, a.b = 0, whose complexification is the
product of two isotropic cones under z = a + ib, z' = a - ib. That variety is
irreducible and has smooth real points, so its real points are Zariski dense
in it, and a polynomial vanishes on the real Stiefel set exactly when it
vanishes on the complex variety the identity test samples. The set where
rank L_(a,b) <= r is closed, so every Stiefel element of A_5 is a zero divisor
exactly when Pf(N) vanishes on a dense subset of the Stiefel set: no special
point can refute the question, only a generic one.

Certificates:

- Theorem 2.3 and the skew-symmetry of L_a and R_b are polynomial identities
  of degree at most 2 in (a, b), while the factorization is matrix algebra
  valid for any two square matrices. A form of degree at most 2 vanishes
  identically when it vanishes on every e_i and every e_i + e_j, so both
  identities are checked exactly on those integer points of the 30 pure
  coordinates of A_5.
- The identity test draws points of the Stiefel variety over F_p with
  p = 1 mod 4, so that iota = sqrt(-1) lies in F_p. An isotropic z in F_p^m
  comes from u != 0 and w in F_p^(m-2): z_1 = (u + u')/2,
  z_2 = (u - u')/(2 iota), z_(3..m) = w with u' = -(w.w)/u. Two independent
  isotropic vectors z, z' give a = (z + z')/2 and b = (z - z')/(2 iota),
  which satisfy a.a = b.b and a.b = 0 over F_p. Clearing u and u' makes
  (u u'_2)^(2^(n-1)) Pf(N) a polynomial of degree at most 3 * 2^(n-1) in the
  parameters, so by Schwartz-Zippel a nonzero restriction of Pf(N) modulo p
  vanishes at one uniformly drawn point with probability at most
  (3 * 2^(n-1) + 2) / p. The evidence records rank N and rank L_(a,b) modulo p
  at every point.
- Controls: A_6 Stiefel points, where generic invertibility is a theorem
  (docs/notes/stiefel_generic_invertibility.md), must read rank 32 for N and
  64 for L_v through the same pipeline, and non-Stiefel A_5 points must read
  full rank.

Usage:
    "$PYTHON" scripts/stiefel_pfaffian_identity.py --out docs/evidence/moreno_stiefel/pfaffian-identity.json
    "$PYTHON" scripts/stiefel_pfaffian_identity.py --check docs/evidence/moreno_stiefel/pfaffian-identity.json
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
from moreno_stiefel_nullity import left_matrix, rank_mod  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SEED = 20261022
TRIALS = {5: 48, 6: 8}
CONTROL_TRIALS = 8
PRIME_CEILING = 1 << 61
MILLER_RABIN_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)

Matrix = list[list[int]]


def is_prime(n: int) -> bool:
    """Deterministic Miller-Rabin; the first twelve prime bases decide every n below 3.3e24."""
    if n < 2:
        return False
    for p in MILLER_RABIN_BASES:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d, s = d // 2, s + 1
    for base in MILLER_RABIN_BASES:
        x = pow(base, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def primes_one_mod_four(count: int) -> list[int]:
    """The largest primes p = 1 mod 4 below 2^61."""
    found: list[int] = []
    candidate = PRIME_CEILING - 3
    while len(found) < count:
        if is_prime(candidate):
            found.append(candidate)
        candidate -= 4
    return found


def sqrt_minus_one(p: int) -> int:
    for base in range(2, p):
        root = pow(base, (p - 1) // 4, p)
        if root * root % p == p - 1:
            return root
    raise ValueError(f"{p} has no square root of -1")


def left_block(half: int, x: list[int]) -> Matrix:
    """L_x on A of dimension half: (x y)_k = sum_j x_(k xor j) cd_sign(half, k xor j, j) y_j."""
    return [[x[k ^ j] * cd_sign(half, k ^ j, j) for j in range(half)] for k in range(half)]


def right_block(half: int, x: list[int]) -> Matrix:
    """R_x on A of dimension half: (y x)_k = sum_j y_j x_(k xor j) cd_sign(half, j, k xor j)."""
    return [[x[k ^ j] * cd_sign(half, j, k ^ j) for j in range(half)] for k in range(half)]


def combine(*terms: tuple[int, Matrix]) -> Matrix:
    size = len(terms[0][1])
    return [[sum(c * m[i][j] for c, m in terms) for j in range(size)] for i in range(size)]


def pure_point(half: int, coordinates: list[int]) -> list[int]:
    return [0, *coordinates] if len(coordinates) == half - 1 else coordinates


def identity_point(item: tuple[int, list[int]]) -> None:
    """Skew-symmetry of L_a, R_b and Theorem 2.3 at one integer point of the pure (a, b) space."""
    n, point = item
    half = 1 << n
    m = half - 1
    a, b = pure_point(half, point[:m]), pure_point(half, point[m:])
    la = np.array(left_block(half, a), dtype=np.int64)
    rb = np.array(right_block(half, b), dtype=np.int64)
    if not (np.array_equal(la.T, -la) and np.array_equal(rb.T, -rb)):
        raise ValueError(f"A_{n}: L_a or R_b is not skew-symmetric at {point}")
    big = np.array(left_matrix(2 * half, a + b), dtype=np.int64)
    block_a = la @ la + rb @ rb
    block_s = rb @ la - la @ rb
    if not np.array_equal(big @ big, np.block([[block_a, -block_s], [block_s, block_a]])):
        raise ValueError(f"A_{n + 1}: Theorem 2.3 fails at {point}")


def check_identities(n: int) -> int:
    """Theorem 2.3 and skew-symmetry on every e_i and e_i + e_j of the pure (a, b) space, in exact integers."""
    half = 1 << n
    m = half - 1
    rng = random.Random(SEED)
    for _ in range(8):
        x, y = [rng.randint(-3, 3) for _ in range(half)], [rng.randint(-3, 3) for _ in range(half)]
        if not np.array_equal(np.array(right_block(half, x)) @ y, np.array(left_matrix(half, y)) @ x):
            raise ValueError(f"A_{n}: R_x y differs from L_y x")
    points: list[tuple[int, list[int]]] = []
    for i in range(2 * m):
        points.append((n, [int(t == i) for t in range(2 * m)]))
        points.extend((n, [int(t in (i, j)) for t in range(2 * m)]) for j in range(i + 1, 2 * m))
    parallel.ordered_map(identity_point, points)
    return len(points)


def isotropic(rng: random.Random, m: int, p: int, iota: int) -> list[int]:
    u = rng.randrange(1, p)
    w = [rng.randrange(p) for _ in range(m - 2)]
    u_bar = -sum(x * x for x in w) * pow(u, p - 2, p) % p
    inverse_two = pow(2, p - 2, p)
    z1 = (u + u_bar) * inverse_two % p
    z2 = (u - u_bar) * pow(2 * iota, p - 2, p) % p
    return [z1, z2, *w]


def stiefel_mod(rng: random.Random, m: int, p: int, iota: int) -> tuple[list[int], list[int]]:
    z, z_bar = isotropic(rng, m, p, iota), isotropic(rng, m, p, iota)
    inverse_two = pow(2, p - 2, p)
    inverse_two_iota = pow(2 * iota, p - 2, p)
    a = [(x + y) * inverse_two % p for x, y in zip(z, z_bar, strict=True)]
    b = [(x - y) * inverse_two_iota % p for x, y in zip(z, z_bar, strict=True)]
    if sum(x * x for x in a) % p != sum(y * y for y in b) % p or sum(x * y for x, y in zip(a, b, strict=True)) % p:
        raise ValueError("drawn pair violates a.a = b.b or a.b = 0 modulo p")
    return a, b


def ranks(item: tuple[int, list[int], list[int], int, int]) -> dict[str, int]:
    n, a, b, p, iota = item
    half = 1 << n
    a_full, b_full = pure_point(half, a), pure_point(half, b)
    n_matrix = combine((1, left_block(half, a_full)), (iota, right_block(half, b_full)))
    return {
        "rank_N": rank_mod(n_matrix, p),
        "rank_L": rank_mod(left_matrix(2 * half, a_full + b_full), p),
    }


def identity_test(n: int, p: int, iota: int, trials: int, rng: random.Random) -> dict[str, Any]:
    """Draws every point in the generator's order, then maps the exact ranks over the pool."""
    m = (1 << n) - 1
    draws = [(n, *stiefel_mod(rng, m, p, iota), p, iota) for _ in range(trials)]
    controls = 0
    if n == 4:
        for _ in range(CONTROL_TRIALS):
            draws.append((n, [rng.randrange(p) for _ in range(m)], [rng.randrange(p) for _ in range(m)], p, iota))
        controls = CONTROL_TRIALS
    results = parallel.ordered_map(ranks, draws)
    stiefel, generic = results[:trials], results[trials:]
    out: dict[str, Any] = {
        "pure_coordinates": m,
        "pfaffian_degree": 1 << (n - 1),
        "schwartz_zippel_bound_per_point": f"{3 * (1 << (n - 1)) + 2}/p",
        "stiefel_points": stiefel,
        "stiefel_ranks": sorted({(r["rank_N"], r["rank_L"]) for r in stiefel}),
    }
    if controls:
        out["non_stiefel_controls"] = sorted({(r["rank_N"], r["rank_L"]) for r in generic})
    return out


def measure() -> dict[str, Any]:
    rng = random.Random(SEED)
    primes = primes_one_mod_four(2)
    result: dict[str, Any] = {
        "schema": "moreno-stiefel-pfaffian-identity-v1",
        "question": "math/0512517, Section 5 (p. 26): is every Stiefel element of A_5 a zero divisor?",
        "seed": SEED,
        "identity_points": {"A_5": check_identities(4)},
        "primes": {},
    }
    for p in primes:
        iota = sqrt_minus_one(p)
        result["primes"][str(p)] = {
            "sqrt_minus_one": iota,
            "algebras": {f"A_{n + 1}": identity_test(n, p, iota, TRIALS[n + 1], rng) for n in (4, 5)},
        }
    for p, entry in result["primes"].items():
        a5, a6 = entry["algebras"]["A_5"], entry["algebras"]["A_6"]
        if any(rank_n > 14 or rank_l > 28 for rank_n, rank_l in a5["stiefel_ranks"]):
            raise ValueError(f"p = {p}: an A_5 Stiefel point has Pf(N) != 0, refuting universality modulo p")
        if a6["stiefel_ranks"] != [(32, 64)]:
            raise ValueError(f"p = {p}: the A_6 control reads ranks {a6['stiefel_ranks']}, not generic invertibility")
        if a5["non_stiefel_controls"] != [(16, 32)]:
            raise ValueError(f"p = {p}: non-Stiefel A_5 controls read {a5['non_stiefel_controls']}")
    return result


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
        raise SystemExit(f"Pfaffian identity evidence differs from {arguments.check}")
    for p, entry in data["primes"].items():
        for name, algebra in entry["algebras"].items():
            print(f"p = {p} {name}: {len(algebra['stiefel_points'])} Stiefel points, ranks {algebra['stiefel_ranks']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
