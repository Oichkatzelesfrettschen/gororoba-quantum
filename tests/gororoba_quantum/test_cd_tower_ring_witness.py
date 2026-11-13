"""The kernel-swap witness of proofs/CdTowerRing.v under the cd_core product over the Gaussian integers.

RingTowerI proves, over a commutative ring with i i = -1, that a = nilpotent2 and w = witness2 satisfy
a u = w for the level-1 unit u, a a = 0, a w = 0 and w a = -2 a at level 2, and lifts the pair to every
higher level by x -> (x, 0). The test reads the two definitions from the proof source, places a nested pair
((x0, x1), (x2, x3)) at coordinates 0 to 3 (the order of the tower's coord, first half first) and checks the
same four products with cd_core.cd_sign extended bilinearly to Gaussian-integer coordinates, in dimensions 4,
8, 16 and 32. The controls replace i by 1, where a w differs from 0, and take a real zero-divisor pair of
the sedenions, where both orders of the product vanish.
"""

import re
from pathlib import Path

import pytest

import cd_core

SOURCE = Path(__file__).resolve().parents[2] / "proofs/CdTowerRing.v"
Gaussian = tuple[int, int]
ZERO: Gaussian = (0, 0)
ATOMS: dict[str, Gaussian] = {
    "D.zero": (0, 0),
    "D.one": (1, 0),
    "D.i": (0, 1),
    "D.opp D.one": (-1, 0),
    "D.opp D.i": (0, -1),
}


def g_mul(x: Gaussian, y: Gaussian) -> Gaussian:
    return (x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def cd_mul(dim: int, a: list[Gaussian], b: list[Gaussian]) -> list[Gaussian]:
    """The bilinear extension of e_p e_q = cd_sign(dim, p, q) e_(p xor q) to Gaussian-integer coordinates."""
    out = [ZERO] * dim
    for p, x in enumerate(a):
        if x == ZERO:
            continue
        for q, y in enumerate(b):
            if y == ZERO:
                continue
            sign = cd_core.cd_sign(dim, p, q)
            term = g_mul(x, y)
            out[p ^ q] = (out[p ^ q][0] + sign * term[0], out[p ^ q][1] + sign * term[1])
    return out


def level2_definition(name: str) -> list[Gaussian]:
    """The four coordinates of ``Definition NAME : T.cd 2 := ((x0, x1), (x2, x3)).`` in the proof source."""
    text = SOURCE.read_text(encoding="utf-8")
    match = re.search(rf"^Definition {name} : T\.cd 2 := \(\((.+?), (.+?)\), \((.+?), (.+?)\)\)\.$", text, re.MULTILINE)
    if match is None:
        raise ValueError(f"{SOURCE} defines no level-2 element {name}")
    return [ATOMS[atom] for atom in match.groups()]


def embed(dim: int, low: list[Gaussian]) -> list[Gaussian]:
    return low + [ZERO] * (dim - len(low))


def scaled(factor: int, vector: list[Gaussian]) -> list[Gaussian]:
    return [(factor * x, factor * y) for x, y in vector]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_source_definitions_are_the_stated_elements() -> None:
    require(level2_definition("nilpotent2") == [(0, 0), (1, 0), (0, 1), (0, 0)], "nilpotent2 is e_1 + i e_2")
    require(level2_definition("witness2") == [(-1, 0), (0, 0), (0, 0), (0, -1)], "witness2 is -e_0 - i e_3")


@pytest.mark.parametrize("dim", [4, 8, 16, 32])
def test_witness_products_under_cd_core(dim: int) -> None:
    a = embed(dim, level2_definition("nilpotent2"))
    w = embed(dim, level2_definition("witness2"))
    u = embed(dim, [(0, 0), (1, 0)])
    zero = [ZERO] * dim
    require(cd_mul(dim, a, u) == w, "a e_1 must equal the witness")
    require(cd_mul(dim, a, a) == zero, "a must square to zero")
    require(cd_mul(dim, a, w) == zero, "a must annihilate the witness on the left")
    require(cd_mul(dim, w, a) == scaled(-2, a), "the witness times a must equal -2 a")
    require(cd_mul(dim, w, a) != zero, "the swapped product must differ from zero")


@pytest.mark.parametrize("dim", [4, 8, 16, 32])
def test_real_coordinates_remove_the_witness(dim: int) -> None:
    """With i replaced by 1 the element e_1 + e_2 has norm 2 and annihilates nothing."""
    a = embed(dim, [(0, 0), (1, 0), (1, 0), (0, 0)])
    u = embed(dim, [(0, 0), (1, 0)])
    require(cd_mul(dim, a, cd_mul(dim, a, u)) != [ZERO] * dim, "e_1 + e_2 must not annihilate (e_1 + e_2) e_1")


def test_real_sedenion_zero_divisor_pair_swaps() -> None:
    a = [ZERO] * 16
    b = [ZERO] * 16
    a[3], a[10] = (1, 0), (1, 0)
    b[6], b[15] = (1, 0), (-1, 0)
    require(cd_mul(16, a, b) == [ZERO] * 16, "(e_3 + e_10)(e_6 - e_15) must vanish")
    require(cd_mul(16, b, a) == [ZERO] * 16, "(e_6 - e_15)(e_3 + e_10) must vanish")
