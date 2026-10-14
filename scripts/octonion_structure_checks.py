"""Exact checks of octonion associator codes, box-kite frustration, walk sectors and conventions.

Every statement is recomputed from cd_core.cd_sign and predict.associator_phase
in integer or rational arithmetic:

1. The 21 associator slices omega_{ij}(x) of the octonions (D = 8) are the
   seven nonzero characters of F_2^3, each three times. With the zero
   character and complements they span RM(1,3), weight enumerator
   1 + 14 z^4 + z^8, and Construction A on it has 240 norm-2 vectors closed
   under every root reflection: the E8 root system.
2. Each of the seven signed sedenion box-kites has 12 edges and 8 triangles
   of sign -1. Over shared vertex signs the frustration
   F = sum_edges (1 - r_uv s_u s_v) / 2 has minimum 4; over shared phases
   F(theta) = sum_edges (1 - r_uv cos(theta_u - theta_v)) / 2 has minimum 3,
   attained with equal phases on opposite vertices and 120 degrees between
   the three opposite pairs (proof in the note).
3. For the walk cores U = (-i)^popcount(y xor x) w(x) / 4 of the pairs
   (25, 31) and (9, 22) at D = 32, U^120 is the identity, so every eigenvalue
   is a 120th root of unity and the weight of |0> on the primitive-k sector is
   (1/120) sum_{t<120} <0|U^t|0> c_k(t), with c_k Ramanujan's sum. The first
   state return is the lcm of the orders that carry weight.
4. For G = L_a^T L_a / |a|^2 the excess second moment
   Delta = tr(G^2)/d - 1 is unchanged by the pure embedding a -> (a, 0),
   whose multiplication operator is diag(L_a, R_a) up to the doubling signs.
5. The doubling (a, b)(c, d) = (ac - d conj(b), conj(a) d + c b) and the
   repository doubling are intertwined by T(a, b) = (T(a), conj(T(b))) on
   every basis pair through D = 16.
"""

from __future__ import annotations

import argparse
import itertools
import math
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from cd_core import cd_sign, left_mult_matrix  # noqa: E402
from predict import associator_phase  # noqa: E402

WALK_PAIRS = {
    (25, 31): {6: Fraction(1, 2), 8: Fraction(1, 2)},
    (9, 22): {
        1: Fraction(11, 30),
        2: Fraction(1, 6),
        3: Fraction(1, 12),
        5: Fraction(3, 10),
        6: Fraction(1, 12),
        8: Fraction(0),
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def associator_code() -> dict[str, object]:
    characters = []
    for i, j in itertools.combinations(range(1, 8), 2):
        bits = [(1 - w) // 2 for w in associator_phase(8, i, j)]
        require(
            all(bits[x ^ y] == bits[x] ^ bits[y] for x in range(8) for y in range(8)), f"slice {i},{j} is not linear"
        )
        require(any(bits), f"slice {i},{j} is the zero character")
        characters.append(tuple(bits))
    multiplicity = {c: characters.count(c) for c in set(characters)}
    require(len(multiplicity) == 7 and set(multiplicity.values()) == {3}, "seven characters, three times each")
    generators = [list(c) for c in set(characters)] + [[1] * 8]
    code = {
        tuple(sum(g[k] for g, use in zip(generators, mask, strict=True) if use) % 2 for k in range(8))
        for mask in itertools.product((0, 1), repeat=len(generators))
    }
    weights = sorted(sum(word) for word in code)
    require(len(code) == 16 and weights.count(4) == 14 and weights.count(0) == weights.count(8) == 1, "RM(1,3)")
    require(all(sum(a * b for a, b in zip(u, v, strict=True)) % 2 == 0 for u in code for v in code), "self-orthogonal")
    roots = {tuple(2 * s if k == i else 0 for k in range(8)) for i in range(8) for s in (1, -1)}
    for word in code:
        if sum(word) == 4:
            support = [k for k in range(8) if word[k]]
            for signs in itertools.product((1, -1), repeat=4):
                vector = [0] * 8
                for k, s in zip(support, signs, strict=True):
                    vector[k] = s
                roots.add(tuple(vector))
    require(len(roots) == 240 and all(sum(x * x for x in r) == 4 for r in roots), "240 norm-2 vectors")
    for r in roots:
        for v in roots:
            inner = sum(a * b for a, b in zip(r, v, strict=True))
            require(inner % 2 == 0, "integral inner products")
            reflected = tuple(a - (inner // 2) * b for a, b in zip(v, r, strict=True))
            require(reflected in roots, "root reflections close")
    rank = np.linalg.matrix_rank(np.array(sorted(roots), dtype=float))
    require(rank == 8, "the roots span rank 8")
    return {"characters": 7, "multiplicity": 3, "code_words": 16, "roots": 240, "reflections_checked": 240 * 240}


def box_kites() -> list[dict[str, int]]:
    out = []
    for strut in range(1, 8):
        vertices = [(a, a ^ (8 ^ strut)) for a in range(1, 8) if a != strut]
        edges = []
        for u, v in itertools.combinations(range(6), 2):
            a, b = vertices[u][0], vertices[v][0]
            if a ^ b == strut:
                continue
            edges.append((u, v, -cd_sign(16, a, b) * cd_sign(16, vertices[u][1], vertices[v][1])))
        adjacency = {(u, v): r for u, v, r in edges} | {(v, u): r for u, v, r in edges}
        triangles = [
            (i, j, k)
            for i, j, k in itertools.combinations(range(6), 3)
            if (i, j) in adjacency and (j, k) in adjacency and (i, k) in adjacency
        ]
        require(len(edges) == 12 and len(triangles) == 8, f"strut {strut}: octahedron incidence")
        require(
            all(adjacency[(i, j)] * adjacency[(j, k)] * adjacency[(i, k)] == -1 for i, j, k in triangles),
            f"strut {strut}: every triangle has sign -1",
        )
        discrete = min(
            sum((1 - r * s[u] * s[v]) // 2 for u, v, r in edges) for s in itertools.product((1, -1), repeat=6)
        )
        require(discrete == 4, f"strut {strut}: discrete frustration minimum")
        gauge = next(s for s in itertools.product((1, -1), repeat=6) if all(s[u] * r * s[v] == -1 for u, v, r in edges))
        opposite = [(u, v) for u, v in itertools.combinations(range(6), 2) if (u, v) not in adjacency]
        theta = [0.0] * 6
        for k, pair in enumerate(opposite):
            for u in pair:
                theta[u] = 2 * math.pi * k / 3 + (0.0 if gauge[u] == 1 else math.pi)
        continuous = sum((1 - r * math.cos(theta[u] - theta[v])) / 2 for u, v, r in edges)
        require(abs(continuous - 3) < 1e-12, f"strut {strut}: the 120-degree assignment reaches 3")
        rng = np.random.default_rng(strut)
        for _ in range(2000):
            trial = rng.uniform(0, 2 * math.pi, 6)
            require(
                sum((1 - r * math.cos(trial[u] - trial[v])) / 2 for u, v, r in edges) >= 3 - 1e-12,
                f"strut {strut}: a phase assignment falls below 3",
            )
        out.append({"strut": strut, "discrete_minimum": discrete, "continuous_minimum": 3})
    return out


def _mobius(n: int) -> int:
    result, m, p = 1, n, 2
    while p * p <= m:
        if m % p == 0:
            m //= p
            if m % p == 0:
                return 0
            result = -result
        p += 1
    return -result if m > 1 else result


def ramanujan(k: int, t: int) -> int:
    g = math.gcd(k, t)
    return sum(_mobius(k // d) * d for d in range(1, g + 1) if g % d == 0)


def walk_sectors(pair: tuple[int, int], expected: dict[int, Fraction]) -> dict[str, object]:
    signs = associator_phase(32, *pair)[:16]
    roots = [(1, 0), (0, -1), (-1, 0), (0, 1)]
    real = [[roots[(x ^ y).bit_count() % 4][0] * signs[x] for x in range(16)] for y in range(16)]
    imag = [[roots[(x ^ y).bit_count() % 4][1] * signs[x] for x in range(16)] for y in range(16)]
    power_r = [[int(y == x) for x in range(16)] for y in range(16)]
    power_i = [[0] * 16 for _ in range(16)]
    returns = []
    for t in range(121):
        returns.append((Fraction(power_r[0][0], 4**t), Fraction(power_i[0][0], 4**t)))
        if t == 120:
            break
        power_r, power_i = (
            [
                [sum(real[y][m] * power_r[m][x] - imag[y][m] * power_i[m][x] for m in range(16)) for x in range(16)]
                for y in range(16)
            ],
            [
                [sum(real[y][m] * power_i[m][x] + imag[y][m] * power_r[m][x] for m in range(16)) for x in range(16)]
                for y in range(16)
            ],
        )
    scale = 4**120
    require(
        all(power_r[y][x] == (scale if y == x else 0) and power_i[y][x] == 0 for y in range(16) for x in range(16)),
        f"{pair}: U^120 is the identity",
    )
    weights = {}
    for k in (d for d in range(1, 121) if 120 % d == 0):
        re = sum(returns[t][0] * ramanujan(k, t) for t in range(120)) / 120
        im = sum(returns[t][1] * ramanujan(k, t) for t in range(120)) / 120
        require(im == 0 and re >= 0, f"{pair}: sector {k} weight is a nonnegative rational")
        if re:
            weights[k] = re
    require(sum(weights.values()) == 1, f"{pair}: sector weights sum to one")
    require(
        {k: weights.get(k, Fraction(0)) for k in expected} == expected and set(weights) <= set(expected),
        f"{pair}: sector weights {weights}",
    )
    state_return = math.lcm(*weights)
    first = next(t for t in range(1, 121) if returns[t][0] ** 2 + returns[t][1] ** 2 == 1)
    require(first == state_return, f"{pair}: first state return {first} differs from lcm {state_return}")
    return {"pair": list(pair), "weights": {str(k): str(v) for k, v in weights.items()}, "first_state_return": first}


def _excess_moment(matrix: np.ndarray, norm_squared: float) -> float:
    gram = matrix.T @ matrix / norm_squared
    return float(np.trace(gram @ gram) / gram.shape[0] - 1)


def gram_moment_embedding() -> dict[str, object]:
    rng = np.random.default_rng(20261014)
    for d in (16, 32):
        for _ in range(20):
            a = rng.normal(size=d)
            left = np.array(left_mult_matrix(d, a), dtype=float)
            require(np.allclose(np.diag(left.T @ left) / (a @ a), 1.0), "every basis column of L_a has norm |a|")
            embedded = np.concatenate([a, np.zeros(d)])
            big = np.array(left_mult_matrix(2 * d, embedded), dtype=float)
            require(
                abs(_excess_moment(left, a @ a) - _excess_moment(big, a @ a)) < 1e-10,
                f"D={d}: the pure embedding changes the excess moment",
            )
            require(
                np.linalg.matrix_rank(big, tol=1e-9) == 2 * np.linalg.matrix_rank(left, tol=1e-9),
                f"D={d}: the pure embedding does not double the rank",
            )
    return {"dimensions": [16, 32], "samples": 20}


def _conj(x: tuple[int, ...]) -> tuple[int, ...]:
    return (x[0], *(-v for v in x[1:]))


def _repo_product(x: tuple[int, ...], y: tuple[int, ...]) -> tuple[int, ...]:
    d = len(x)
    return tuple(
        sum(cd_sign(d, p, q) * x[p] * y[q] for p in range(d) for q in range(d) if p ^ q == r) for r in range(d)
    )


def _draft_product(x: tuple[int, ...], y: tuple[int, ...]) -> tuple[int, ...]:
    d = len(x)
    if d == 1:
        return (x[0] * y[0],)
    h = d // 2
    a, b, c, e = x[:h], x[h:], y[:h], y[h:]
    first = tuple(u - v for u, v in zip(_draft_product(a, c), _draft_product(e, _conj(b)), strict=True))
    second = tuple(u + v for u, v in zip(_draft_product(_conj(a), e), _draft_product(c, b), strict=True))
    return first + second


def _bridge(x: tuple[int, ...]) -> tuple[int, ...]:
    if len(x) == 1:
        return x
    h = len(x) // 2
    return _bridge(x[:h]) + _conj(_bridge(x[h:]))


def convention_bridge() -> dict[str, int]:
    checked = 0
    for d in (2, 4, 8, 16):
        basis = [tuple(int(j == k) for j in range(d)) for k in range(d)]
        for x in basis:
            for y in basis:
                require(_bridge(_draft_product(x, y)) == _repo_product(_bridge(x), _bridge(y)), f"D={d}: bridge fails")
                checked += 1
    return {"basis_pairs": checked}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.parse_args(argv)
    associator_code()
    box_kites()
    for pair, expected in WALK_PAIRS.items():
        walk_sectors(pair, expected)
    gram_moment_embedding()
    convention_bridge()
    print(
        "octonion structure: RM(1,3) and E8 from associators; kite minima 4 and 3; walk sectors by Ramanujan sums; "
        "embedding moments; convention bridge"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
