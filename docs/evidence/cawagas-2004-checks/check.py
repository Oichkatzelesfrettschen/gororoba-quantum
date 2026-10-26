"""Cawagas (2004) sedenion statements checked against gororoba_quantum/cd_core.py.

The probe rebuilds the paper's multiplication rule from its 35 associative triplets (Section 2), finds the
diagonal sign map onto cd_core's basis, and recomputes the order-16 subloop census and Moufang split
(Section 3, Tables 2 and 3), the 84 zero-divisor pairs of Table 5, the worked product of Section 4 and
Moreno's footnoted pair. It closes with a cd_core zero divisor whose support spans no order-16 subloop,
which bounds Proposition 2 to the listed pairs. Exact integer arithmetic throughout; no randomness.

Usage: "$PYTHON" docs/evidence/cawagas-2004-checks/check.py > docs/evidence/cawagas-2004-checks/check.txt
"""

from __future__ import annotations

import itertools
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import flint  # noqa: E402

import cd_core  # noqa: E402
import parallel  # noqa: E402

DIM = 16
OCTONION_TRIPLETS = ((1, 2, 3), (1, 4, 5), (1, 7, 6), (2, 4, 6), (2, 5, 7), (3, 4, 7), (3, 6, 5))
SEDENION_TRIPLETS = (
    (1, 8, 9), (1, 11, 10), (1, 13, 12), (1, 14, 15),
    (2, 8, 10), (2, 9, 11), (2, 14, 12), (2, 15, 13),
    (3, 8, 11), (3, 10, 9), (3, 15, 12), (3, 13, 14),
    (4, 8, 12), (4, 9, 13), (4, 10, 14), (4, 11, 15),
    (5, 8, 13), (5, 12, 9), (5, 10, 15), (5, 14, 11),
    (6, 8, 14), (6, 15, 9), (6, 12, 10), (6, 11, 13),
    (7, 8, 15), (7, 9, 14), (7, 13, 10), (7, 12, 11),
)  # fmt: skip
# Table 3 (p. 259): FINITAS subloop numbers of the octonion-loop and quasi-octonion-loop copies, positive indices.
TABLE3_OCTONION = {
    2: (0, 1, 2, 3, 4, 5, 6, 7),
    3: (0, 1, 2, 3, 8, 9, 10, 11),
    6: (0, 1, 4, 5, 8, 9, 12, 13),
    9: (0, 1, 6, 7, 8, 9, 14, 15),
    17: (0, 2, 4, 6, 8, 10, 12, 14),
    20: (0, 2, 5, 7, 8, 10, 13, 15),
    28: (0, 3, 4, 7, 8, 11, 12, 15),
    31: (0, 3, 5, 6, 8, 11, 13, 14),
}
TABLE3_QUASI = {
    4: (0, 1, 2, 3, 12, 13, 14, 15),
    7: (0, 1, 4, 5, 10, 11, 14, 15),
    10: (0, 1, 6, 7, 10, 11, 12, 13),
    18: (0, 2, 4, 6, 9, 11, 13, 15),
    21: (0, 2, 5, 7, 9, 11, 12, 14),
    29: (0, 3, 4, 7, 9, 10, 13, 14),
    32: (0, 3, 5, 6, 9, 10, 12, 15),
}
# Table 5 (de Marrais GoTo lists as printed by Cawagas, p. 263): each row is (a s1 b)(c s2 d).
TABLE5 = """
(1+13)(2-14) (1+14)(2+13) (1-12)(2-15) (1-15)(2+12) (2-14)(3+15) (2+13)(3-12) (2-15)(3-14) (2+12)(3+13)
(3+15)(1-13) (3-12)(1-14) (3-14)(1+12) (3+13)(1+15)
(1+14)(4-11) (1+11)(4+14) (1-15)(4-10) (1-10)(4+15) (4-11)(5+10) (4+14)(5-15) (4-10)(5-11) (4+15)(5+14)
(5+10)(1-14) (5-15)(1-11) (5-11)(1+15) (5+14)(1+10)
(1+11)(7-13) (1+13)(7+11) (1-10)(7-12) (1-12)(7+10) (7-13)(6+12) (7+11)(6-10) (7-12)(6-13) (7+10)(6+11)
(6+12)(1-11) (6-10)(1-13) (6-13)(1+10) (6+11)(1+12)
(2+15)(4-9) (2+9)(4+15) (2-13)(4-11) (2-11)(4+13) (4-9)(6+11) (4+15)(6-13) (4-11)(6-9) (4+13)(6+15)
(6+11)(2-15) (6-13)(2-9) (6-9)(2+13) (6+15)(2+11)
(2+9)(5-14) (2+14)(5+9) (2-11)(5-12) (2-12)(5+11) (5-14)(7+12) (5+9)(7-11) (5-12)(7-14) (5+11)(7+9)
(7+12)(2-9) (7-11)(2-14) (7-14)(2+11) (7+9)(2+12)
(3+13)(4-10) (3+10)(4+13) (3-14)(4-9) (3-9)(4+14) (4-10)(7+9) (4+13)(7-14) (4-9)(7-10) (4+14)(7+13)
(7+9)(3-13) (7-14)(3-10) (7-10)(3+14) (7+13)(3+9)
(3+10)(6-15) (3+15)(6+10) (3-9)(6-12) (3-12)(6+9) (6-15)(5+12) (6+10)(5-9) (6-12)(5-15) (6+9)(5+10)
(5+12)(3-10) (5-9)(3-15) (5-15)(3+9) (5+10)(3+12)
"""


def cawagas_sign() -> dict[tuple[int, int], int]:
    """Sign of e_a e_b = +-e_(a^b) in the paper's rule: each triplet and its cyclic shifts multiply to +."""
    sign: dict[tuple[int, int], int] = {}
    for a in range(DIM):
        sign[(0, a)] = sign[(a, 0)] = 1
        if a:
            sign[(a, a)] = -1
    for a, b, c in OCTONION_TRIPLETS + SEDENION_TRIPLETS:
        if a ^ b != c:
            raise ValueError(f"triplet {(a, b, c)} breaks the XOR index rule")
        for x, y in ((a, b), (b, c), (c, a)):
            sign[(x, y)], sign[(y, x)] = 1, -1
    if len(sign) != DIM * DIM:
        raise ValueError(f"the 35 triplets fix {len(sign)} of {DIM * DIM} products")
    return sign


def sign_map(bits: int) -> tuple[int, ...] | None:
    """The diagonal map s with s_0 = 1 encoded by bits when cw(a, b) = s_a s_b s_(a^b) cd_sign(a, b) on all pairs."""
    cw = cawagas_sign()
    s = (1,) + tuple(-1 if bits >> k & 1 else 1 for k in range(DIM - 1))
    ok = all(cw[(a, b)] == s[a] * s[b] * s[a ^ b] * cd_core.cd_sign(DIM, a, b) for a in range(DIM) for b in range(DIM))
    return s if ok else None


def diagonal_maps() -> list[tuple[int, ...]]:
    """Every s in {+-1}^16 with s_0 = 1 carrying the paper's rule onto cd_core, in candidate order."""
    return [s for s in parallel.ordered_map(sign_map, list(range(1 << (DIM - 1)))) if s is not None]


def subspaces() -> list[tuple[int, ...]]:
    """The 15 three-dimensional subspaces of F_2^4, as sorted index sets of size 8."""
    found = set()
    for a, b, c in itertools.combinations(range(1, DIM), 3):
        span = {x ^ y ^ z for x in (0, a) for y in (0, b) for z in (0, c)}
        if len(span) == 8:
            found.add(tuple(sorted(span)))
    return sorted(found)


def mul(cw: dict[tuple[int, int], int], x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    """Signed basis product (sign, index) in the paper's rule."""
    return x[0] * y[0] * cw[(x[1], y[1])], x[1] ^ y[1]


def moufang(cw: dict[tuple[int, int], int], indices: tuple[int, ...], printed: bool = False) -> bool:
    """Moufang identity (xy)(zx) = (x(yz))x on the basis elements, or with printed=True the Table 2 text
    (xy)(zx) = (x(yx))z; central signs factor out of both sides."""
    for x, y, z in itertools.product(indices, repeat=3):
        ex, ey, ez = (1, x), (1, y), (1, z)
        left = mul(cw, mul(cw, ex, ey), mul(cw, ez, ex))
        if printed:
            right = mul(cw, mul(cw, ex, mul(cw, ey, ex)), ez)
        else:
            right = mul(cw, mul(cw, ex, mul(cw, ey, ez)), ex)
        if left != right:
            return False
    return True


def vector(terms: list[tuple[int, int]], s: tuple[int, ...] | None = None) -> list[int]:
    v = [0] * DIM
    for coeff, index in terms:
        v[index] += coeff * (s[index] if s else 1)
    return v


def cawagas_product(cw: dict[tuple[int, int], int], u: list[int], v: list[int]) -> list[int]:
    out = [0] * DIM
    for a, b in itertools.product(range(DIM), repeat=2):
        if u[a] and v[b]:
            out[a ^ b] += u[a] * v[b] * cw[(a, b)]
    return out


def parse_table5() -> list[tuple[list[tuple[int, int]], list[tuple[int, int]]]]:
    rows = []
    for a, s1, b, c, s2, d in re.findall(r"\((\d+)([+-])(\d+)\)\((\d+)([+-])(\d+)\)", TABLE5):
        left = [(1, int(a)), (1 if s1 == "+" else -1, int(b))]
        right = [(1, int(c)), (1 if s2 == "+" else -1, int(d))]
        rows.append((left, right))
    return rows


def nullity(v: list[int]) -> int:
    rows = cd_core.left_mult_matrix_exact(DIM, v)
    return DIM - flint.fmpz_mat([[int(x) for x in row] for row in rows]).rank()


def rank_f2(support: tuple[int, ...]) -> int:
    basis: list[int] = []
    for x in support:
        for b in basis:
            x = min(x, x ^ b)
        if x:
            basis.append(x)
    return len(basis)


def candidate(args: tuple[tuple[int, ...], tuple[int, ...]]) -> tuple[tuple[int, ...], tuple[int, ...], int]:
    support, signs = args
    return support, signs, nullity(vector(list(zip(signs, support, strict=True))))


def main() -> int:
    cw = cawagas_sign()
    print("rule: the 35 triplets fix all 256 basis products and obey e_a e_b = +-e_(a^b)")
    agree = sum(cw[(a, b)] == cd_core.cd_sign(DIM, a, b) for a in range(DIM) for b in range(DIM))
    print(f"sign agreement with cd_core.cd_sign before any map: {agree} of 256")
    maps = diagonal_maps()
    print(f"diagonal sign maps e_i -> s_i e_i carrying the paper's rule onto cd_core: {len(maps)}")
    s = maps[0] if maps else None
    if s:
        print(f"first map: flipped indices {[i for i in range(DIM) if s[i] < 0]}")

    spaces = subspaces()
    split = [(space, moufang(cw, space)) for space in spaces]
    oct_copies = [space for space, ok in split if ok]
    quasi = [space for space, ok in split if not ok]
    printed = [space for space in spaces if moufang(cw, space, printed=True)]
    print(f"order-16 subloops satisfying Table 2's printed MP (xy)(zx) = (x(yx))z: {len(printed)} of {len(spaces)}")
    print(f"order-16 subloops {{+-e_i : i in V}}, V a 3-dim subspace of F_2^4: {len(spaces)}")
    print(f"Moufang (octonion loop copies): {len(oct_copies)}; non-Moufang (quasi-octonion copies): {len(quasi)}")
    print(f"Moufang copies equal Table 3's octonion column: {set(oct_copies) == set(TABLE3_OCTONION.values())}")
    print(f"non-Moufang copies equal Table 3's quasi-octonion column: {set(quasi) == set(TABLE3_QUASI.values())}")
    print(f"octonion-loop copies other than O contain e_8: {all(8 in v or v == tuple(range(8)) for v in oct_copies)}")
    planes = {tuple(sorted({0, a, b, a ^ b})) for a, b in itertools.combinations(range(1, DIM), 2)}
    print(f"order-8 subloops (2-dim subspaces): {len(planes)}; order-4 subloops (nonzero vectors): {DIM - 1}")
    if s:
        cd_moufang = [moufang({k: cd_core.cd_sign(DIM, *k) for k in cw}, space) for space in spaces]
        print(f"cd_core rule: Moufang split {sum(cd_moufang)} / {len(spaces) - sum(cd_moufang)}")

    rows = parse_table5()
    zero_cw = sum(not any(cawagas_product(cw, vector(left), vector(right))) for left, right in rows)
    in_quasi = sum(any({i for _, i in left + right} <= set(space) for space in quasi) for left, right in rows)
    print(f"Table 5 pairs: {len(rows)}; zero in the paper's rule: {zero_cw}; inside a quasi-octonion copy: {in_quasi}")
    if s:
        zero_cd = sum(
            not any(cd_core.cd_multiply_exact(DIM, vector(left, s), vector(right, s))) for left, right in rows
        )
        print(f"Table 5 pairs zero in cd_core after the sign map: {zero_cd}")
    raw_cd = sum(not any(cd_core.cd_multiply_exact(DIM, vector(left), vector(right))) for left, right in rows)
    print(f"Table 5 pairs zero in cd_core with indices copied unmapped: {raw_cd}")

    worked = cawagas_product(cw, vector([(1, 2), (-1, 14)]), vector([(1, 3), (1, 15)]))
    print(f"Section 4 worked product (e2 - e14)(e3 + e15) in the paper's rule: {worked}")
    moreno_cw = cawagas_product(cw, vector([(1, 1), (1, 10)]), vector([(1, 15), (-1, 4)]))
    moreno_cd = cd_core.cd_multiply_exact(DIM, vector([(1, 1), (1, 10)]), vector([(1, 15), (-1, 4)]))
    print(f"Moreno (e1 + e10)(e15 - e4): paper's rule {moreno_cw}; cd_core unmapped {[int(x) for x in moreno_cd]}")

    supports = [t for t in itertools.combinations(range(1, DIM), 4) if rank_f2(t) == 4]
    jobs = [(t, signs) for t in supports for signs in itertools.product((1, -1), repeat=4)]
    results = parallel.ordered_map(candidate, jobs)
    spanning = [(t, sg, n) for t, sg, n in results if n]
    print(f"cd_core four-term +-1 elements, every sign, spanning support: {len(jobs)}; zero divisors: {len(spanning)}")
    if spanning:
        t, sg, n = spanning[0]
        print(f"  first: support {t} signs {sg} nullity {n}; it lies in no order-16 subloop, so no quasi-octonion copy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
