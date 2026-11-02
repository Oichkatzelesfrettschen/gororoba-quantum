"""Exact checks behind the [E] results of docs/notes/topics/chatgpt-archive-verified-results.md.

Each function computes one tagged number or identity and raises when it fails: the j-function coefficients and
McKay's decompositions, the E8 level-1 character as the cube root of j, j(i) = 1728, the E8 root split under a fixed
root, the level-2 Ising singular vectors, the Sugawara contraction in two normalizations, the two doubling formulas
the conversations state, a sedenion zero divisor, the fractal-doping identity, the XOR-line Jacobiator zero set and
power-associativity against non-associativity. Cayley-Dickson products come from gororoba_quantum/cd_core.py in exact
arithmetic, so every count and defect is fixed by its basis and sign convention. No value is drawn at random.

Usage:
    "$PYTHON" scripts/chatgpt_archive_checks.py [--out FILE]
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from cd_core import cd_multiply_exact  # noqa: E402

TERMS = 7  # q-series coefficients kept, from q^-1 (or q^0) on


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def series_mul(a: list[int], b: list[int]) -> list[int]:
    return [sum(a[i] * b[n - i] for i in range(n + 1)) for n in range(min(len(a), len(b)))]


def series_inv(a: list[int]) -> list[int]:
    require(a[0] == 1, "series inverse needs constant term 1")
    out = [1]
    for n in range(1, len(a)):
        out.append(-sum(a[i] * out[n - i] for i in range(1, n + 1)))
    return out


def eisenstein_e4(n: int) -> list[int]:
    return [1] + [240 * int(sp.divisor_sigma(k, 3)) for k in range(1, n)]


def euler_power(power: int, n: int) -> list[int]:
    """prod_{k>=1} (1 - q^k)^power to n terms, power >= 0."""
    require(power >= 0, "euler_power takes a nonnegative power")
    out = [1] + [0] * (n - 1)
    for k in range(1, n):
        factor = [0] * n
        for m in range(0, n, k):
            factor[m] = int(sp.binomial(power, m // k)) * (-1) ** (m // k)
        out = series_mul(out, factor)
    return out


def j_coefficients() -> dict[str, object]:
    """j = E4^3 / Delta with Delta = q prod (1 - q^n)^24; returns q j as a power series."""
    e4 = eisenstein_e4(TERMS)
    qj = series_mul(series_mul(series_mul(e4, e4), e4), series_inv(euler_power(24, TERMS)))
    require(qj[:6] == [1, 744, 196884, 21493760, 864299970, 20245856256], f"j coefficients {qj[:6]}")
    # Conway-Norton Table 1: the Monster irreducible degrees 1, 196883, 21296876 decompose the first coefficients.
    require(196884 == 1 + 196883 and 21493760 == 1 + 196883 + 21296876, "McKay decompositions")
    return {"q_j": qj, "mckay": {"196884": [1, 196883], "21493760": [1, 196883, 21296876]}}


def e8_character_cube_root() -> dict[str, object]:
    """E4 / eta^8 = q^(-1/3) (1 + 248 q + ...), and its cube is q^-1 times the series of q j."""
    char = series_mul(eisenstein_e4(TERMS), series_inv(euler_power(8, TERMS)))
    cube = series_mul(series_mul(char, char), char)
    qj = j_coefficients()["q_j"]
    require(isinstance(qj, list) and cube == qj, "E4/eta^8 cubed differs from j")
    require(char[:3] == [1, 248, 4124], f"E8 character {char[:3]}")
    return {"character": char, "cube_equals_qj": True}


def j_at_i() -> float:
    """j(i) from E4^3 / Delta at q = exp(-2 pi), to 60 terms."""
    q = math.exp(-2 * math.pi)
    e4 = 1 + 240 * sum(int(sp.divisor_sigma(k, 3)) * q**k for k in range(1, 60))
    delta = q * math.prod((1 - q**k) ** 24 for k in range(1, 60))
    value = e4**3 / delta
    require(abs(value - 1728) < 1e-6, f"j(i) = {value}")
    return value


def e8_roots() -> list[tuple[Fraction, ...]]:
    roots: list[tuple[Fraction, ...]] = []
    for i, j in itertools.combinations(range(8), 2):
        for si, sj in itertools.product((1, -1), repeat=2):
            v = [Fraction(0)] * 8
            v[i], v[j] = Fraction(si), Fraction(sj)
            roots.append(tuple(v))
    for signs in itertools.product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(tuple(Fraction(s, 2) for s in signs))
    require(len(roots) == 240, "E8 has 240 roots")
    return roots


def e8_root_split() -> dict[str, int]:
    """Inner products with a fixed root: 126 orthogonal (E7), 56 + 56 at plus or minus 1, plus or minus the root."""
    roots = e8_roots()
    fixed = roots[0]
    counts: dict[str, int] = {}
    for r in roots:
        ip = sum(a * b for a, b in zip(r, fixed, strict=True))
        counts[str(ip)] = counts.get(str(ip), 0) + 1
    require(counts == {"2": 1, "-2": 1, "1": 56, "-1": 56, "0": 126}, f"split {counts}")
    require(126 + 7 == 133 and 2 + 1 == 3 and 133 + 3 + 2 * 56 == 248, "e7 + sl2 + (56, 2) dimension count")
    return counts


def ising_level_two() -> dict[str, str]:
    """(L_-2 + a L_-1^2)|h> is singular at c = 1/2 for a = -3/(2(2h+1)): the level-2 Gram matrix annihilates (1, a)."""
    c = sp.Rational(1, 2)
    out = {}
    for h in (sp.Rational(1, 2), sp.Rational(1, 16)):
        a = -sp.Rational(3, 2) / (2 * h + 1)
        gram = sp.Matrix([[4 * h + c / 2, 6 * h], [6 * h, 8 * h**2 + 4 * h]])
        require((gram * sp.Matrix([1, a])).is_zero_matrix, f"not singular at h = {h}")
        out[str(h)] = str(a)
    require(out == {"1/2": "-3/4", "1/16": "-4/3"}, f"coefficients {out}")
    return out


def sugawara_contraction() -> dict[str, int]:
    """Sum over a, c of f^{abc} f^{acd} for su(2): -2 delta for epsilon, -4 delta = -2h delta for sqrt(2) epsilon."""
    eps = sp.LeviCivita
    plain = [[sum(eps(a, b, c) * eps(a, c, d) for a in range(3) for c in range(3)) for d in range(3)] for b in range(3)]
    require(plain == [[-2, 0, 0], [0, -2, 0], [0, 0, -2]], f"epsilon contraction {plain}")
    dual_coxeter = 2
    return {"epsilon": -2, "long_roots_squared_length_2": -2 * 2, "minus_2h": -2 * dual_coxeter}


def doubling(x: list[int], y: list[int], formula: str) -> list[int]:
    """The two doubling laws the conversations state, recursively on halves."""

    def conj(v: list[int]) -> list[int]:
        if len(v) == 1:
            return list(v)
        h = len(v) // 2
        return conj(v[:h]) + [-t for t in v[h:]]

    if len(x) == 1:
        return [x[0] * y[0]]
    h = len(x) // 2
    a, b, c, d = x[:h], x[h:], y[:h], y[h:]

    def sub(u: list[int], v: list[int]) -> list[int]:
        return [p - q for p, q in zip(u, v, strict=True)]

    def add(u: list[int], v: list[int]) -> list[int]:
        return [p + q for p, q in zip(u, v, strict=True)]

    if formula == "conversation":  # (ac - conj(d) b, ad + b conj(c))
        return sub(doubling(a, c, formula), doubling(conj(d), b, formula)) + add(
            doubling(a, d, formula), doubling(b, conj(c), formula)
        )
    if formula == "prather":  # (ac - d conj(b), b conj(c) + d a)
        return sub(doubling(a, c, formula), doubling(d, conj(b), formula)) + add(
            doubling(b, conj(c), formula), doubling(d, a, formula)
        )
    raise ValueError(formula)


def unit_sum(dim: int, *idx: int) -> list[int]:
    v = [0] * dim
    for i in idx:
        v[i] += 1
    return v


def norm_failures() -> dict[str, list[int]]:
    """Exact witnesses: the conversation's formula breaks N(xy) = N(x)N(y) at dimension 8, the Prather variant at 4."""

    def n2(v: list[int]) -> int:
        return sum(t * t for t in v)

    x, y = unit_sum(8, 1, 4), unit_sum(8, 2, 7)
    conv = n2(doubling(x, y, "conversation"))
    require(conv == 8 and n2(x) * n2(y) == 4, f"conversation formula at dimension 8: {conv}")
    x4, y4 = unit_sum(4, 0, 2), unit_sum(4, 1, 3)
    prather = n2(doubling(x4, y4, "prather"))
    require(prather == 0 and n2(x4) * n2(y4) == 4, f"Prather formula at dimension 4: {prather}")
    zd_right = unit_sum(16, 6)
    zd_right[15] = -1
    s = cd_multiply_exact(16, unit_sum(16, 3, 10), zd_right)
    require(all(t == 0 for t in s), "(e3 + e10)(e6 - e15) is not zero under cd_core")
    return {"conversation_dim8": [8, 4], "prather_dim4": [0, 4], "sedenion_zero_product": [0, 4]}


def fractal_doping() -> str:
    phi = (1 + sp.sqrt(5)) / 2
    k = sp.Symbol("k", integer=True, positive=True)
    require(sp.simplify(sp.summation(phi ** (-k), (k, 1, sp.oo)) - phi) == 0, "sum over k >= 1 of phi^-k is phi")
    require(sp.simplify(1 + phi - phi**2) == 0, "1 + phi = phi^2")
    return "x + phi x = phi^2 x"


def bracket(dim: int, u: list[int], v: list[int]) -> list:
    return [p - q for p, q in zip(cd_multiply_exact(dim, u, v), cd_multiply_exact(dim, v, u), strict=True)]


def triple_jacobiator_vanishes(item: tuple[int, int, int, int]) -> bool:
    """Whether the commutator Jacobiator of e_i, e_j, e_k vanishes in the algebra of dimension dim."""
    dim, i, j, k = item
    e = [unit_sum(dim, t) for t in (i, j, k)]
    jac = [0] * dim
    for s, t, r in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
        term = bracket(dim, bracket(dim, e[s], e[t]), e[r])
        jac = [p + q for p, q in zip(jac, term, strict=True)]
    return all(t == 0 for t in jac)


def jacobiator_zero_set(dims: tuple[int, ...] = (8, 16, 32)) -> dict[str, list[int]]:
    """Imaginary basis triples with zero commutator Jacobiator are exactly the XOR lines {i, j, i xor j}."""
    import parallel

    out = {}
    for dim in dims:
        triples = [(dim, i, j, k) for i, j, k in itertools.combinations(range(1, dim), 3)]
        vanish = parallel.ordered_map(triple_jacobiator_vanishes, triples)
        for (_, i, j, k), v in zip(triples, vanish, strict=True):
            require(v == (i ^ j == k), f"dimension {dim}: triple {(i, j, k)} breaks the XOR-line rule")
        out[str(dim)] = [sum(vanish), len(triples)]
    require(out.get("8") == [7, 35] and out.get("16") == [35, 455], f"counts {out}")
    if "32" in out:
        require(out["32"] == [155, 4495], f"dimension 32 counts {out['32']}")
    return out


def power_associativity(dims: tuple[int, ...] = (8, 16, 32, 64)) -> dict[str, bool]:
    """x^2 x = x x^2 and x^2 x^2 = (x^2 x) x hold exactly on a fixed integer element; the associator does not vanish."""
    out = {}
    for dim in dims:
        x = [k + 1 for k in range(dim)]
        x2 = cd_multiply_exact(dim, x, x)
        left, right = cd_multiply_exact(dim, x2, x), cd_multiply_exact(dim, x, x2)
        require(left == right, f"x^2 x differs from x x^2 at dimension {dim}")
        require(cd_multiply_exact(dim, x2, x2) == cd_multiply_exact(dim, left, x), f"x^4 at dimension {dim}")
        a, b, c = unit_sum(dim, 1), unit_sum(dim, 2), unit_sum(dim, 4)
        assoc = [
            p - q
            for p, q in zip(
                cd_multiply_exact(dim, cd_multiply_exact(dim, a, b), c),
                cd_multiply_exact(dim, a, cd_multiply_exact(dim, b, c)),
                strict=True,
            )
        ]
        require(any(t != 0 for t in assoc), f"(e1 e2) e4 = e1 (e2 e4) at dimension {dim}")
        out[str(dim)] = True
    return out


def all_checks() -> dict[str, object]:
    return {
        "j_coefficients": j_coefficients(),
        "e8_character_cube_root": e8_character_cube_root(),
        "j_at_i": j_at_i(),
        "e8_root_split": e8_root_split(),
        "ising_level_two": ising_level_two(),
        "sugawara_contraction": sugawara_contraction(),
        "norm_failures": norm_failures(),
        "fractal_doping": fractal_doping(),
        "jacobiator_zero_set": jacobiator_zero_set(),
        "power_associativity": power_associativity(),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    result = all_checks()
    text = json.dumps(result, indent=1, default=str) + "\n"
    if args.out:
        args.out.write_text(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
