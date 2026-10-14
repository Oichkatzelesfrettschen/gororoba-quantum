"""Exact checks of octonion associator codes, box-kite frustration, walk sectors and conventions.

Every statement is recomputed from cd_core.cd_sign and predict.associator_phase
in integer, rational or cyclotomic-integer arithmetic; the whole-operator
periods belong to ripple_dynamics.EXPECTED_PERIODS:

1. The 21 associator slices omega_{ij}(x) of the octonions (D = 8) are the
   seven nonzero characters of F_2^3, each three times. With the zero
   character and complements they span RM(1,3), weight enumerator
   1 + 14 z^4 + z^8, and Construction A on it has 240 norm-2 vectors closed
   under every root reflection: the E8 root system.
2. Each of the seven signed sedenion box-kites has 12 edges and 8 triangles
   of sign -1. Over shared vertex signs the frustration
   F = sum_edges (1 - r_uv s_u s_v) / 2 has minimum 4; over shared phases
   F(theta) = sum_edges (1 - r_uv cos(theta_u - theta_v)) / 2 obeys
   F = 6 + (|Z|^2 - |Z_1|^2 - |Z_2|^2 - |Z_3|^2) / 4 in the switched gauge,
   so its minimum is 3, attained with equal phases on opposite vertices and
   120 degrees between the three opposite pairs. The identity is checked as
   an equality of the two bilinear forms in the unit phasors, coefficient by
   coefficient, so it holds for every phase assignment.
3. For the walk cores U = (-i)^popcount(y xor x) w(x) / 4 of the pairs
   (25, 31) and (9, 22) at D = 32, U^120 is the identity, so every eigenvalue
   is a 120th root of unity and the weight of |0> on the primitive-k sector is
   (1/120) sum_{t<120} <0|U^t|0> c_k(t), with c_k Ramanujan's sum. The first
   state return is the order of the eigenvalue ratios lambda / lambda_0 over
   the weighted spectrum; it equals the lcm of the weighted orders when
   lambda = 1 carries weight, as for (9, 22). The weighted spectrum comes
   from exact zero tests of 120 q_n = sum_t <0|U^t|0> zeta^{-n t} in
   Z[zeta_120] / Phi_120.
4. The pure embedding a -> (a, 0) has multiplication operator
   diag(L_a, R_a) exactly, R_a = C L_conj(a) C with C the conjugation and
   L_conj(a) = L_a^T, so G = L_a^T L_a / |a|^2 keeps its excess second moment
   Delta = tr(G^2)/d - 1 and the rank doubles, zero divisors included; integer
   coefficient vectors keep every product and rank exact.
5. The doubling (a, b)(c, d) = (ac - d conj(b), conj(a) d + c b) and the
   repository doubling are intertwined by T(a, b) = (T(a), conj(T(b))) on
   every basis pair through D = 16.
6. Each basis left multiplication L_m is a signed permutation, L_m e_x =
   cd_sign(m, x) e_{m xor x}. On a Fano line {p, q, p xor q} of the
   octonions the product L_p L_q L_{p xor q} is the signed Z-string
   eps_L (-1)^{<x, v_L>}, with v_L the nonzero vector orthogonal to the line.
   Among the 105 sedenion pairs, 63 have {L_p, L_q} = 0; for a = e_i + t e_j,
   L_a^T L_a = 2I - t {L_i, L_j}, so only the other 42 pairs can carry a zero
   divisor, and the index pairs of cd_core.sedenion_zero_divisor_corpus are
   exactly those 42.
"""

from __future__ import annotations

import argparse
import itertools
import math
import random
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from cd_core import cd_sign, left_mult_matrix, sedenion_zero_divisor_corpus  # noqa: E402
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


def exact_rank(rows: list[list[int]]) -> int:
    """Rank over the rationals by Gaussian elimination in Fraction arithmetic."""
    matrix = [[Fraction(x) for x in row] for row in rows]
    rank = 0
    for col in range(len(matrix[0]) if matrix else 0):
        pivot = next((r for r in range(rank, len(matrix)) if matrix[r][col]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        for r in range(rank + 1, len(matrix)):
            if matrix[r][col]:
                factor = matrix[r][col] / matrix[rank][col]
                matrix[r] = [x - factor * y for x, y in zip(matrix[r], matrix[rank], strict=True)]
        rank += 1
    return rank


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
    require(exact_rank([list(r) for r in sorted(roots)]) == 8, "the roots span rank 8")
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
        gauges = [s for s in itertools.product((1, -1), repeat=6) if all(s[u] * r * s[v] == -1 for u, v, r in edges)]
        require(len(gauges) == 2, f"strut {strut}: switching to the all-negative octahedron")
        gauge = gauges[0]
        opposite = [(u, v) for u, v in itertools.combinations(range(6), 2) if (u, v) not in adjacency]
        # Phases in sixths of a turn have rational cosines: equal phases on each
        # opposite pair, 120 degrees between pairs, switched by the gauge.
        cosine = (Fraction(1), Fraction(1, 2), Fraction(-1, 2), Fraction(-1), Fraction(-1, 2), Fraction(1, 2))
        sixth = [0] * 6
        for k, pair in enumerate(opposite):
            for u in pair:
                sixth[u] = 2 * k + (0 if gauge[u] == 1 else 3)
        continuous = sum((1 - r * cosine[(sixth[u] - sixth[v]) % 6]) / 2 for u, v, r in edges)
        require(continuous == 3, f"strut {strut}: the 120-degree assignment reaches 3")
        # The proof's identity as bilinear forms in unit phasors p_v: F is
        # 6 + sum_edges (-r_uv / 2) <p_u, p_v>; with switched phasors g_v p_v,
        # |Z|^2 = 6 + 2 sum_{u<v} g_u g_v <p_u, p_v> and an opposite pair's
        # |Z_k|^2 = 2 + 2 g_a g_b <p_a, p_b>. Equal constants and coefficients
        # make the identity hold for every phase assignment; |Z_k| <= 2 then
        # gives F >= 6 - 12/4 = 3.
        frustration_form = {(u, v): Fraction(-r, 2) for u, v, r in edges}
        identity_form: dict[tuple[int, int], Fraction] = {}
        identity_constant = Fraction(6) + Fraction(6, 4)
        for u, v in itertools.combinations(range(6), 2):
            identity_form[(u, v)] = Fraction(2 * gauge[u] * gauge[v], 4)
        for u, v in opposite:
            identity_constant -= Fraction(2, 4)
            identity_form[(u, v)] -= Fraction(2 * gauge[u] * gauge[v], 4)
        identity_form = {pair: c for pair, c in identity_form.items() if c}
        require(
            identity_constant == 6 and identity_form == frustration_form,
            f"strut {strut}: the frustration identity fails",
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


def _poly_divmod(numerator: list[int], divisor: list[int]) -> tuple[list[int], list[int]]:
    """Quotient and remainder of integer polynomials (coefficients low to high) by a monic divisor."""
    remainder = list(numerator)
    quotient = [0] * max(1, len(numerator) - len(divisor) + 1)
    for shift in range(len(numerator) - len(divisor), -1, -1):
        lead = remainder[shift + len(divisor) - 1]
        if lead:
            quotient[shift] = lead
            for k, c in enumerate(divisor):
                remainder[shift + k] -= lead * c
    return quotient, remainder[: len(divisor) - 1]


def cyclotomic(n: int) -> list[int]:
    """Phi_n by dividing x^n - 1 by Phi_d for every proper divisor d."""
    poly = [-1] + [0] * (n - 1) + [1]
    for d in range(1, n):
        if n % d == 0:
            poly, remainder = _poly_divmod(poly, cyclotomic(d))
            require(not any(remainder), f"Phi_{d} does not divide x^{n} - 1")
    return poly


def eigenvalue_support(amplitudes: list[tuple[int, int]]) -> list[int]:
    """Exponents n with nonzero sum_t a_t zeta^{-n t} in Z[zeta_120] / Phi_120, a_t = re + i im, i = zeta^30."""
    phi = cyclotomic(120)
    support = []
    for n in range(120):
        element = [0] * 120
        for t, (re, im) in enumerate(amplitudes):
            element[(-n * t) % 120] += re
            element[(30 - n * t) % 120] += im
        if any(_poly_divmod(element, phi)[1]):
            support.append(n)
    return support


def support_calibration() -> None:
    """Known spectra: the returns 1, i^t, and those of a 3-cycle times diag(i, 1, 1).

    A unitary's returns satisfy a_{-t} = conj(a_t), so the real part is even in
    t; the 3-cycle's eigenvalues, the cube roots of i at n = 10, 50, 90, are
    not closed under n -> -n and fix the sign convention of i = zeta^30.
    """
    require(eigenvalue_support([(1, 0)] * 120) == [0], "the support of a constant return is not lambda = 1")
    powers_of_i = [((1, 0, -1, 0)[t % 4], (0, 1, 0, -1)[t % 4]) for t in range(120)]
    require(eigenvalue_support(powers_of_i) == [30], "the support of i^t is not lambda = i")
    cycle = [powers_of_i[t // 3] if t % 3 == 0 else (0, 0) for t in range(120)]
    require(eigenvalue_support(cycle) == [10, 50, 90], "the support of a 3-cycle times diag(i, 1, 1)")


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
    first = next(t for t in range(1, 121) if returns[t][0] ** 2 + returns[t][1] ** 2 == 1)
    # Per-eigenvalue weights q_n on lambda = zeta^n, zeta = exp(2 pi i / 120):
    # 120 q_n = sum_t <0|U^t|0> zeta^{-n t} with i = zeta^30. Scaled by 4^120
    # the amplitudes are Gaussian integers, so q_n is zero exactly when that
    # sum reduces to zero modulo Phi_120. The first return is the order of
    # the ratios lambda_n / lambda_n0 over the weighted support:
    # 120 / gcd(120, n - n0 for all weighted n).
    scaled = [(re * scale, im * scale) for re, im in returns[:120]]
    require(all(re.denominator == im.denominator == 1 for re, im in scaled), f"{pair}: 4^120 U^t is not integral")
    support = eigenvalue_support([(re.numerator, im.numerator) for re, im in scaled])
    # q_n >= 0, so a sector carries weight exactly when one of its eigenvalues does.
    require(
        {120 // math.gcd(120, n) for n in support} == set(weights),
        f"{pair}: the weighted eigenvalues and the exact sector weights disagree",
    )
    ratio_order = 120 // math.gcd(120, *(n - support[0] for n in support))
    require(first == ratio_order, f"{pair}: first return {first} differs from the ratio order {ratio_order}")
    if 1 in weights:
        require(first == math.lcm(*weights), f"{pair}: lambda = 1 carries weight, so the lcm rule must hold")
    return {
        "pair": list(pair),
        "weights": {str(k): str(v) for k, v in weights.items()},
        "first_state_return": first,
        "weighted_eigenvalue_exponents": support,
        "lcm_of_weighted_orders": math.lcm(*weights),
    }


def _excess_moment(matrix: list[list[int]], norm_squared: int) -> Fraction:
    """Delta = tr(G^2)/d - 1 for G = M^T M / |a|^2, exactly."""
    d = len(matrix)
    gram = [[sum(matrix[k][i] * matrix[k][j] for k in range(d)) for j in range(d)] for i in range(d)]
    trace = sum(gram[i][j] * gram[j][i] for i in range(d) for j in range(d))
    return Fraction(trace, d * norm_squared**2) - 1


def _integer(matrix: list[list[float]]) -> list[list[int]]:
    require(all(x == int(x) for row in matrix for x in row), "an integer coefficient vector gave a fractional entry")
    return [[int(x) for x in row] for row in matrix]


def right_mult_matrix(dim: int, v: list[float]) -> list[list[float]]:
    """R_v: x -> x v, column q holding e_q v = sum_p v_p cd_sign(q, p) e_{q xor p}."""
    mat = [[0.0] * dim for _ in range(dim)]
    for p, vp in enumerate(v):
        if vp == 0.0:
            continue
        for q in range(dim):
            mat[q ^ p][q] += vp * cd_sign(dim, q, p)
    return mat


def gram_moment_embedding() -> dict[str, object]:
    rng = random.Random(20261014)
    checked = 0
    for d in (16, 32):
        zero_divisor = [0] * d
        zero_divisor[1] = zero_divisor[10] = 1
        samples = [[rng.randint(-3, 3) for _ in range(d)] for _ in range(10)] + [zero_divisor]
        for a in samples:
            if not any(a):
                continue
            norm_squared = sum(x * x for x in a)
            conj = [a[0], *(-x for x in a[1:])]
            left = _integer(left_mult_matrix(d, [float(x) for x in a]))
            right = _integer(right_mult_matrix(d, [float(x) for x in a]))
            big = _integer(left_mult_matrix(2 * d, [float(x) for x in a] + [0.0] * d))
            require(
                all(big[i][j] == left[i][j] and big[d + i][d + j] == right[i][j] for i in range(d) for j in range(d)),
                "diag(L_a, R_a)",
            )
            require(
                not any(big[i][d + j] or big[d + i][j] for i in range(d) for j in range(d)),
                "the embedding operator is block diagonal",
            )
            transpose_left = _integer(left_mult_matrix(d, [float(x) for x in conj]))
            require(all(transpose_left[i][j] == left[j][i] for i in range(d) for j in range(d)), "L_conj(a) = L_a^T")
            flip = [1] + [-1] * (d - 1)
            require(
                all(right[i][j] == flip[i] * transpose_left[i][j] * flip[j] for i in range(d) for j in range(d)),
                "R_a = C L_conj(a) C",
            )
            require(
                all(sum(left[k][j] ** 2 for k in range(d)) == norm_squared for j in range(d)),
                "every basis column of L_a has norm |a|",
            )
            require(
                _excess_moment(left, norm_squared) == _excess_moment(big, norm_squared),
                f"D={d}: the pure embedding changes the excess moment",
            )
            rank_left = exact_rank(left)
            require(exact_rank(big) == 2 * rank_left, f"D={d}: the rank does not double")
            if a is zero_divisor:
                require(rank_left == 3 * d // 4, f"D={d}: e1 + e10 has rank {rank_left}, not {3 * d // 4}")
            checked += 1
    return {"dimensions": [16, 32], "samples": checked}


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


def _apply(dim: int, factors: tuple[int, ...], x: int) -> tuple[int, int]:
    """(sign, index) of L_{f_1} ... L_{f_n} e_x for basis factors, applied right to left."""
    sign = 1
    for m in reversed(factors):
        sign *= cd_sign(dim, m, x)
        x ^= m
    return sign, x


def _sparse_gram(dim: int, i: int, j: int, t: int) -> list[list[int]]:
    """L_a^T L_a for a = e_i + t e_j, from the two nonzero entries of each column."""
    columns = [{i ^ x: cd_sign(dim, i, x), j ^ x: t * cd_sign(dim, j, x)} for x in range(dim)]
    return [[sum(v * columns[y].get(r, 0) for r, v in columns[x].items()) for y in range(dim)] for x in range(dim)]


def left_multiplication_products() -> dict[str, object]:
    signs: dict[str, dict[str, int]] = {}
    for p, q in itertools.combinations(range(1, 8), 2):
        r = p ^ q
        if r < q:
            continue
        orthogonal = [v for v in range(1, 8) if all(bin(v & w).count("1") % 2 == 0 for w in (p, q))]
        require(len(orthogonal) == 1, f"line {p, q, r}: one orthogonal vector")
        diagonal = []
        for x in range(8):
            sign, image = _apply(8, (p, q, r), x)
            require(image == x, f"line {p, q, r}: L_p L_q L_r is not diagonal")
            diagonal.append(sign)
        character = [(-1) ** bin(x & orthogonal[0]).count("1") for x in range(8)]
        eps = diagonal[0]
        require(diagonal == [eps * c for c in character], f"line {p, q, r}: not +/- Z^(v_L)")
        signs[f"{p},{q},{r}"] = {"v_L": orthogonal[0], "sign": eps}
    require(len(signs) == 7, "seven Fano lines")
    anticommuting: set[tuple[int, int]] = set()
    other: set[tuple[int, int]] = set()
    for i, j in itertools.combinations(range(1, 16), 2):
        anti = [[0] * 16 for _ in range(16)]
        for x in range(16):
            for factors in ((i, j), (j, i)):
                sign, image = _apply(16, factors, x)
                anti[image][x] += sign
        (anticommuting if not any(any(row) for row in anti) else other).add((i, j))
        for t in (1, -1):
            gram = _sparse_gram(16, i, j, t)
            require(
                all(gram[x][y] == 2 * (x == y) - t * anti[x][y] for x in range(16) for y in range(16)),
                f"({i}, {j}, {t}): L_a^T L_a differs from 2I - t {{L_i, L_j}}",
            )
    require(len(anticommuting) == 63 and len(other) == 42, f"split {len(anticommuting)} / {len(other)}")
    corpus = sedenion_zero_divisor_corpus()
    used = {(i, j) for i, j, _, _, _, _ in corpus} | {(k, el) for _, _, _, k, el, _ in corpus}
    require(len(corpus) == 336 and used == other, "the corpus index pairs differ from the non-anticommuting pairs")
    return {"fano_line_signs": signs, "anticommuting_pairs": 63, "corpus_index_pairs": 42}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.parse_args(argv)
    associator_code()
    box_kites()
    support_calibration()
    for pair, expected in WALK_PAIRS.items():
        walk_sectors(pair, expected)
    gram_moment_embedding()
    convention_bridge()
    left_multiplication_products()
    print(
        "octonion structure: RM(1,3) and E8 from associators; kite minima 4 and 3; walk sectors by Ramanujan sums; "
        "embedding moments; convention bridge; Fano-line Z-strings and the 63/42 sedenion anticommutation split"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
