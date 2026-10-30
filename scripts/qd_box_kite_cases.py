"""Photonic box-kite cases for Quandela Belenos, generated from the retained box-kite census.

Every sign comes from docs/evidence/box_kite_census/census.json through
box_kite_cases.validate_census and pair_phases; cd_core enters only to certify
the one-hot sedenion pair. One photon carries the Design B product
x y with x = (e_L + s e_U)/sqrt2 and y = (e_L' + t e_U')/sqrt2.

- Contraction. V = L_x restricted to span{e_L', e_U'}, divided by sqrt2, so
  ||V y||^2 = ||x y||^2 / 2, the census column p_selector_zero, on every row.
  On a two-label row the four product terms land on label_0 = L^L' = U^U' and
  label_1 = L^U' = U^L', and V = M / 2 with the sign block
  M = [[g(L,L'), s g(U,U')], [s g(U,L'), g(L,U')]]; M (1, t) equals the
  census coefficients (c0, c1). A four-label row (the cross-kite controls and
  the negative fixture) sends the two columns to disjoint label pairs, so no
  sign changes any detection probability: one sign-blind 4 x 2 contraction
  with entries 1/2 serves every such row at P = 1/2.
- Dilation. U = [[V, sqrt(I - V V^T)], [sqrt(I - V^T V), -V^T]] is the
  Halmos unitary dilation. V V^T and V^T V have spectra inside {0, 1/2, 1},
  so each square root is the Lagrange polynomial of f(0) = 1,
  f(1/2) = 1/sqrt2, f(1) = 0, and every entry lies in Q(sqrt2). The
  generator computes in that field with Fractions, writes each entry as the
  pair [a, b] meaning a + b sqrt2, and requires U U^T = I exactly.
- Ports. Input ports 0 and 1 carry the coordinates of y on e_L' and e_U';
  output ports are the algebra labels, then the dilation modes. The photon
  enters local mode 0, a balanced splitter on ports (0, 1) with sign t
  prepares y, and the circuit is U (H_t + I). The ideal single-photon
  distribution is |U_tot[k][0]|^2, rational on every mode, and its
  algebra-mode sum equals the census P of each row the block serves.
- One-hot pair. x = e1 + e10 against y = e4 - e15 (dark, the cd_core corpus
  zero product) and e4 + e15 (bright), with all 16 algebra labels as output
  ports plus 2 dilation modes. The 14 labels the product cannot reach see
  the identity part of sqrt(I - V V^T), so detections there measure leakage
  the reduced block cannot see. A one-hot D = 32 embedding needs 34 modes, beyond
  Belenos's 24; scripts/cd_two_blade_blocks.py records that every D = 32
  two-label product uses one of the same sign blocks.

Placement follows the retained qpu:belenos record
(docs/evidence/quandela/catalogue.json): every photon enters a connected
input mode. The single layout puts a 4-mode block on modes 20-23, the
6-mode control on 18-23 and the 18-mode pair on 6-23, whose detectors read
the lowest dark counts. The packed layout puts six 4-mode blocks on modes
0-23 with one photon at each block's first mode; the unitary is block
diagonal, so blocks share no amplitude and only chip crosstalk couples them.

A one-photon two-label circuit depends on (M, t) alone and a two-photon
one on M alone. The census Design B rows reach 14 of the 16 sign matrices;
the other two arise from two-label pairs outside those rows (an assessor
against the (S, 8) plane of its label, two planes on one side of 8), so
each missing configuration carries the first sedenion witness pair whose
cd_core block it is, certified by cd_multiply_exact. Every two-label two-blade
product of any dimension then maps to one circuit of the family
(scripts/cd_two_blade_blocks.py checks that through D = 64).

- Two-photon pairs. One photon on each input port of the dilation of
  V = M / 2 leaves on the two label modes with amplitude perm(V) =
  perm(M) / 4 when the photons are indistinguishable and with probability
  1/8 when they are distinguishable. perm M = g(L,L') g(L,U') (1 + p0 p1)
  and det M = g(L,L') g(L,U') (1 - p0 p1) for the kite phase products
  p0 = g(L,L') g(U,U') and p1 = g(L,U') g(U,L'): an edge (p0 = p1) reads
  1/4 and a strut or (l, l^8) pair (p0 != p1) reads 0, independent of s
  and t. The box-kite edge/strut split is then a two-photon interference
  contrast for source indistinguishability V. Threshold detection keeps the
  two-click samples, so each block preregisters the exact conditional label
  fraction f(V) from its two_click terms, and the suppressed blocks fit V.

Four series land under results/quandela/cases/: box_kite_photonic_single
(one block per job: the 32 two-label configurations, the four-label
control and the one-hot pair), box_kite_photonic_packed (the 32 two-label
configurations six to a job), box_kite_photonic_packed_swapped (the same jobs
with every block moved three slots along) and box_kite_photonic_pairs (the 16 sign
blocks with two photons). Each job-NN/ holds cases.json
and circuit.json; the series cases.json maps every census row to its job.

--write DIR writes every series; --check DIR regenerates them in memory,
compares file sets and bytes and admits the retained files offline
(digests, exact unitarity, connected input modes, ideals, row coverage);
--self-test requires census, circuit, placement, ideal, coverage and
one-hot mutations to be rejected.

Usage: "$PYTHON" scripts/qd_box_kite_cases.py (--write DIR | --check DIR | --self-test)
"""

from __future__ import annotations

import argparse
import copy
import functools
import hashlib
import json
import sys
from collections import Counter
from collections.abc import Callable
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from box_kite_cases import CENSUS, Row, census_rows, load_census, pair_phases, two_label, validate_census  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_multiply_exact, cd_sign, sedenion_zero_divisor_corpus  # noqa: E402

SCHEMA = "qd-box-kite-cases-v1"
CIRCUIT_SCHEMA = "qd-circuit-v1"
SERIES_SCHEMA = "qd-box-kite-series-v1"
CATALOGUE = ROOT / "docs/evidence/quandela/catalogue.json"
PLATFORMS = ("sim:belenos", "qpu:belenos")
CHIP = "qpu:belenos"
CHIP_MODES = 24
COMMAND = "sample_count"
MIN_DETECTED_PHOTONS = 1
# 10000 detected samples per block; a one-photon shot is one detection event,
# so the shot cap doubles the samples as headroom against threshold-detector
# multi-click events and still bounds a QPU job at 1e-6 credits per shot.
SAMPLES_PER_BLOCK = 10_000
SHOT_HEADROOM = 2
MAX_DURATION = 300
SINGLE = "box_kite_photonic_single"
PACKED = "box_kite_photonic_packed"
SWAPPED = "box_kite_photonic_packed_swapped"
PAIRS = "box_kite_photonic_pairs"
DIAGNOSTICS = "belenos_diagnostics"
FRINGE = "belenos_fringe"
FAMILIES = (SINGLE, PACKED, SWAPPED, PAIRS, DIAGNOSTICS, FRINGE)
# A fringe job scans the input phase phi = k pi/4, k = 0..7, through one
# compiled circuit as Perceval iterations; FRINGE_BLOCKS names its sign blocks.
FRINGE_STEPS = 8
FRINGE_SAMPLES = 2_500
FRINGE_BLOCKS = (("edge", "two_label-04"), ("strut", "two_label-00"))
# Diagnostic jobs separate chip routing, circuit width and gate form on one
# bright and one dark block: (config, reference, offset, circuit modes, gate form).
DIAGNOSTIC_JOBS = (
    ("identity", None, 20, CHIP_MODES, "unitary"),
    ("two_label", "two_label-04", 0, 4, "unitary"),
    ("two_label", "two_label-04", 0, 4, "native"),
    ("two_label", "two_label-04", 20, CHIP_MODES, "native"),
    ("two_label", "two_label-05", 0, 4, "native"),
)
SINGLE_OFFSET = {4: 20, 6: 18, 18: 6}
# Two photons enter adjacent connected modes 8 and 9; their detectors read
# dark counts of 0.1 and 0.6 per second in the retained record.
PAIR_OFFSET = 8
PAIR_SAMPLES = 5_000
# estimate_required_shots on the retained qpu:belenos record asks about 7e5
# shots for 1e4 two-photon samples on modes 0 and 1; modes 8 and 9 transmit
# t_in 1.85 % and 2.64 % against 2.83 % and 2.28 %, so 5000 samples need
# well under the cap, which bounds a QPU job at 2 credits.
PAIR_MAX_SHOTS = 2_000_000
PACK_OFFSETS = (0, 4, 8, 12, 16, 20)
# The swapped layout keeps each packed job's block set and moves every block
# half a turn around the six slots: slot k's block sits at PACK_OFFSETS[(k + 3) % 6].
# A per-mode transmission or detector offset follows the slot; an algebra or
# compilation offset follows the block.
SWAP_OFFSETS = PACK_OFFSETS[3:] + PACK_OFFSETS[:3]
ONE_HOT_X = (1, 10)
ONE_HOT_Y = (4, 15)
DIM = 16
TWO_LABEL_SOURCES = ("within_kite", "nonkite_pairs")
FOUR_LABEL_SOURCES = ("cross_kite_controls", "negative_fixture")

# An element a + b sqrt2 of Q(sqrt2).
Q2 = tuple[Fraction, Fraction]
Matrix = list[list[Q2]]
ZERO: Q2 = (Fraction(0), Fraction(0))
ONE: Q2 = (Fraction(1), Fraction(0))
INV_SQRT2: Q2 = (Fraction(0), Fraction(1, 2))


def cos_quarter(k: int) -> tuple[Fraction, Fraction]:
    """cos(k pi / 4) as a + b sqrt2."""
    half_root = Fraction(1, 2)
    return [
        (Fraction(1), Fraction(0)),
        (Fraction(0), half_root),
        (Fraction(0), Fraction(0)),
        (Fraction(0), -half_root),
        (Fraction(-1), Fraction(0)),
        (Fraction(0), -half_root),
        (Fraction(0), Fraction(0)),
        (Fraction(0), half_root),
    ][k % 8]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def q(value: int | Fraction) -> Q2:
    return (Fraction(value), Fraction(0))


def add(x: Q2, y: Q2) -> Q2:
    return (x[0] + y[0], x[1] + y[1])


def mul(x: Q2, y: Q2) -> Q2:
    return (x[0] * y[0] + 2 * x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def neg(x: Q2) -> Q2:
    return (-x[0], -x[1])


def square(x: Q2) -> Fraction:
    """x^2 for an entry whose square is rational; raises otherwise."""
    value = mul(x, x)
    require(value[1] == 0, f"entry {x} has an irrational square")
    return value[0]


def matmul(a: Matrix, b: Matrix) -> Matrix:
    return [[_dot(row, [b[k][j] for k in range(len(b))]) for j in range(len(b[0]))] for row in a]


def _dot(row: list[Q2], column: list[Q2]) -> Q2:
    total = ZERO
    for x, y in zip(row, column, strict=True):
        if x != ZERO and y != ZERO:
            total = add(total, mul(x, y))
    return total


def transpose(a: Matrix) -> Matrix:
    return [list(column) for column in zip(*a, strict=True)]


def identity(n: int) -> Matrix:
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]


def scale(a: Matrix, factor: Q2) -> Matrix:
    return [[mul(x, factor) for x in row] for row in a]


def plus(a: Matrix, b: Matrix) -> Matrix:
    return [[add(x, y) for x, y in zip(ra, rb, strict=True)] for ra, rb in zip(a, b, strict=True)]


def minus(a: Matrix, b: Matrix) -> Matrix:
    return plus(a, scale(b, q(-1)))


def sqrt_complement(gram: Matrix) -> Matrix:
    """sqrt(I - G) for a symmetric G whose spectrum lies in {0, 1/2, 1}, by Lagrange interpolation."""
    n = len(gram)
    eye = identity(n)
    half = scale(eye, q(Fraction(1, 2)))
    require(
        matmul(matmul(gram, minus(gram, half)), minus(gram, eye)) == scale(eye, q(0)),
        "the Gram matrix has an eigenvalue outside {0, 1/2, 1}",
    )
    # f(G) = f(0) (G - 1/2)(G - 1) / (1/2) + f(1/2) G (G - 1) / (-1/4); f(1) = 0.
    at_zero = scale(matmul(minus(gram, half), minus(gram, eye)), q(2))
    at_half = scale(matmul(gram, minus(gram, eye)), mul(q(-4), INV_SQRT2))
    return plus(at_zero, at_half)


def dilation(v: Matrix) -> Matrix:
    """The Halmos dilation [[V, sqrt(I - V V^T)], [sqrt(I - V^T V), -V^T]] of a real contraction V."""
    vt = transpose(v)
    top = [row + extra for row, extra in zip(v, sqrt_complement(matmul(v, vt)), strict=True)]
    bottom = [row + [neg(x) for x in extra] for row, extra in zip(sqrt_complement(matmul(vt, v)), vt, strict=True)]
    u = top + bottom
    require(matmul(u, transpose(u)) == identity(len(u)), "the dilation is not orthogonal")
    return u


def preparation(n: int, t: int) -> Matrix:
    """The balanced splitter on modes (0, 1): |0> -> (|0> + t|1>)/sqrt2, |1> -> (|0> - t|1>)/sqrt2."""
    p = identity(n)
    p[0][0], p[1][0] = INV_SQRT2, mul(q(t), INV_SQRT2)
    p[0][1], p[1][1] = INV_SQRT2, mul(q(-t), INV_SQRT2)
    return p


def ideal(u: Matrix, column: int = 0) -> list[Fraction]:
    return [square(row[column]) for row in u]


def text(x: Q2) -> list[str]:
    return [str(x[0]), str(x[1])]


def parse(entry: list[str]) -> Q2:
    require(isinstance(entry, list) and len(entry) == 2, f"entry {entry!r} is not a pair [a, b]")
    return (Fraction(entry[0]), Fraction(entry[1]))


# ---------------------------------------------------------------- configurations


def sign_block(row: Row) -> tuple[tuple[int, int], tuple[int, int]]:
    """M with M (1, t) = (c0, c1), from the census phases; raises when the coefficients disagree."""
    g_ll, g_lu, g_ul, g_uu = pair_phases(row)
    s, t = row["x_sign"], row["y_sign"]
    m = ((g_ll, s * g_uu), (s * g_ul, g_lu))
    require(
        (m[0][0] + t * m[0][1], m[1][0] + t * m[1][1]) == (row["c0"], row["c1"]),
        f"census {row['source']}[{row['index']}]: sign block {m} gives coefficients other than (c0, c1)",
    )
    return m


def two_label_block(m: tuple[tuple[int, int], tuple[int, int]], t: int) -> Matrix:
    u = dilation([[q(Fraction(x, 2)) for x in r] for r in m])
    return matmul(u, preparation(4, t))


def four_label_block() -> Matrix:
    half = q(Fraction(1, 2))
    u = dilation([[half, ZERO], [half, ZERO], [ZERO, half], [ZERO, half]])
    return matmul(u, preparation(6, 1))


def one_hot_block(t: int) -> Matrix:
    """x = (e1 + e10)/sqrt2 on y = (e4 + t e15)/sqrt2 over all 16 algebra modes and 2 dilation modes."""
    low, high = ONE_HOT_X
    v = [[ZERO, ZERO] for _ in range(DIM)]
    for column, j in enumerate(ONE_HOT_Y):
        for i in (low, high):
            entry = add(v[i ^ j][column], q(Fraction(cd_sign(DIM, i, j), 2)))
            v[i ^ j][column] = entry
    return matmul(dilation(v), preparation(DIM + 2, t))


def certify_one_hot(t: int) -> Fraction:
    """||x y||^2 / 2 through cd_core.cd_multiply_exact, required to be 0 for the corpus pair and 1 for its control."""
    x = [0] * DIM
    y = [0] * DIM
    x[ONE_HOT_X[0]] = x[ONE_HOT_X[1]] = 1
    y[ONE_HOT_Y[0]], y[ONE_HOT_Y[1]] = 1, t
    product = cd_multiply_exact(DIM, x, y)
    require(all(c == int(c) for c in product), "the one-hot product left the integers")
    norm = Fraction(sum(int(c) ** 2 for c in product), 4)
    zero = (ONE_HOT_X[0], ONE_HOT_X[1], 1, ONE_HOT_Y[0], ONE_HOT_Y[1], t) in _corpus()
    require((norm == 0) == zero, f"cd_core and the corpus disagree on the one-hot pair at t = {t}")
    return norm / 2


@functools.cache
def _corpus() -> frozenset[tuple[int, int, int, int, int, int]]:
    return frozenset(sedenion_zero_divisor_corpus())


def all_blocks() -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """The 16 sign matrices with entries +-1, row-major in the order +1 before -1."""
    signs = (1, -1)
    return [((a, b), (c, d)) for a in signs for b in signs for c in signs for d in signs]


def witness(m: tuple[tuple[int, int], tuple[int, int]], t: int) -> list[int]:
    """Find the first two-label pair [i, j, s, k, l, t] with sign block m, using cd_multiply_exact.

    The search runs over labels X, then planes {i, i^X} x {k, k^X} and s in
    (+1, -1); the product of e_i + s e_j and e_k + t e_l must equal
    c0 e_(i^k) + c1 e_(i^l) with (c0, c1) = m (1, t).
    """
    for label in range(1, DIM):
        planes = sorted({tuple(sorted((i, i ^ label))) for i in range(1, DIM) if i ^ label not in (0, i)})
        for i, j in planes:
            for k, el in planes:
                for s in (1, -1):
                    block = (
                        (cd_sign(DIM, i, k), s * cd_sign(DIM, j, el)),
                        (s * cd_sign(DIM, j, k), cd_sign(DIM, i, el)),
                    )
                    if block == m:
                        found = [i, j, s, k, el, t]
                        certify_witness("witness search", found, [list(r) for r in m])
                        return found
    raise ValueError(f"no sedenion two-label pair carries the sign block {m}")


def certify_witness(name: str, w: list[int], m: list[list[int]]) -> None:
    """The witness pair's cd_core sign block equals m and its cd_multiply_exact product equals c0, c1 on its labels."""
    i, j, s, k, el, t = w
    require(i ^ j == k ^ el, f"{name}: witness {w} is not a two-label pair")
    block = [[cd_sign(DIM, i, k), s * cd_sign(DIM, j, el)], [s * cd_sign(DIM, j, k), cd_sign(DIM, i, el)]]
    require(block == m, f"{name}: witness {w} carries the sign block {block}, not {m}")
    x = [0] * DIM
    y = [0] * DIM
    x[i], x[j], y[k], y[el] = 1, s, 1, t
    want = [0] * DIM
    want[i ^ k] += m[0][0] + t * m[0][1]
    want[i ^ el] += m[1][0] + t * m[1][1]
    require(
        cd_multiply_exact(DIM, x, y) == tuple(want), f"{name}: cd_core product of witness {w} differs from its block"
    )


def configurations(census: dict[str, Any]) -> list[dict[str, Any]]:
    """Every distinct circuit with the census rows it serves; two-label circuits cover all 16 sign blocks.

    A two-label circuit depends on (M, t) alone, so rows of both two-label
    sources share it. Census Design B rows reach 14 of the 16 sign blocks;
    the rest come from two-label pairs outside the kites' Design B rows (an
    assessor against the (S, 8) plane of its label, or two planes on one
    side of 8), each carried by a cd_core-certified witness pair.
    """
    rows = validate_census(census)
    singles: dict[tuple[Any, ...], dict[str, Any]] = {}
    pairs: dict[tuple[Any, ...], dict[str, Any]] = {}
    for source in TWO_LABEL_SOURCES:
        for row in rows[source]:
            require(two_label(row), f"census {source}[{row['index']}] is not a two-label row")
            m = sign_block(row)
            singles.setdefault((m, row["y_sign"]), {"kind": "two_label", "m": m, "t": row["y_sign"], "rows": []})[
                "rows"
            ].append(row)
            pairs.setdefault((m,), {"kind": "pair", "m": m, "rows": []})["rows"].append(row)
    for m in all_blocks():
        for t in (1, -1):
            if (m, t) not in singles:
                singles[(m, t)] = {"kind": "two_label", "m": m, "t": t, "rows": [], "witness": witness(m, t)}
        if (m,) not in pairs:
            pairs[(m,)] = {"kind": "pair", "m": m, "rows": [], "witness": witness(m, 1)}
    out = list(singles.values())
    for source in FOUR_LABEL_SOURCES:
        for row in rows[source]:
            require(not two_label(row), f"census {source}[{row['index']}] is a two-label row")
            if not out or out[-1]["kind"] != "four_label":
                out.append({"kind": "four_label", "rows": []})
            out[-1]["rows"].append(row)
    for t in (-1, 1):
        out.append({"kind": "one_hot", "t": t, "rows": [], "p_algebra": str(certify_one_hot(t))})
    out += list(pairs.values())
    counts: Counter[str] = Counter()
    for config in out:
        if "m" in config:
            config["m"] = [list(r) for r in config["m"]]
        config["id"] = f"{config['kind']}-{counts[config['kind']]:02d}"
        counts[config["kind"]] += 1
    return out


# ---------------------------------------------------------------- native gates

# Perceval's BS.H() is (1/sqrt2)[[1, 1], [1, -1]] on two adjacent modes, PS(pi)
# negates one mode and PERM(p) sends mode i to p[i]; a native op is
# ["BS.H", a] (modes a, a + 1), ["PS", k] or ["PERM", p], applied in list order.
SWAP_1_3 = [0, 3, 2, 1]
SWAP_1_2 = [0, 2, 1, 3]
EDGE_CORE: list[list[Any]] = [["BS.H", 0], ["BS.H", 2], ["PERM", SWAP_1_3], ["PS", 2], ["BS.H", 0], ["BS.H", 2]]
STRUT_CORE: list[list[Any]] = [
    ["BS.H", 2],
    ["PERM", SWAP_1_2],
    ["BS.H", 0],
    ["BS.H", 2],
    ["PERM", SWAP_1_2],
    ["BS.H", 0],
]


def op_matrix(n: int, op: list[Any]) -> Matrix:
    g = identity(n)
    if op[0] == "BS.H":
        a = op[1]
        g[a][a], g[a][a + 1], g[a + 1][a], g[a + 1][a + 1] = INV_SQRT2, INV_SQRT2, INV_SQRT2, neg(INV_SQRT2)
    elif op[0] == "PS":
        g[op[1]][op[1]] = q(-1)
    elif op[0] == "PERM":
        g = [[ZERO] * n for _ in range(n)]
        for i, j in enumerate(op[1]):
            g[j][i] = ONE
    else:
        raise ValueError(f"unknown native op {op!r}")
    return g


def native_unitary(n: int, ops: list[list[Any]]) -> Matrix:
    u = identity(n)
    for op in ops:
        u = matmul(op_matrix(n, op), u)
    return u


def native_ops(config: dict[str, Any]) -> list[list[Any]]:
    """The block as balanced beam splitters, pi phases and one permutation, from M = D1 K D2.

    D1 = diag(M00, M10) and D2 = diag(1, M00 M01) make K's first row and
    column +1, so K is the edge core [[1, 1], [1, 1]] or the strut core
    [[1, 1], [1, -1]]. The dilation carries the diagonals through:
    dil(D1 K D2) = diag(D1, D2) dil(K / 2) diag(D2, D1). The edge core is
    (BS.H_01 BS.H_23) PS_2 SWAP_13 (BS.H_01 BS.H_23) and the strut core
    BS.H_01 BS.H_02 BS.H_13 BS.H_23, the non-adjacent pair written as
    SWAP_12 (BS.H_01 BS.H_23) SWAP_12. A one-photon block first prepares y
    with BS.H_01 and, for t = -1, PS_1.
    """
    m = config["m"]
    d1 = (m[0][0], m[1][0])
    d2 = (1, m[0][0] * m[0][1])
    k = [[d1[i] * m[i][j] * d2[j] for j in range(2)] for i in range(2)]
    core = EDGE_CORE if k == [[1, 1], [1, 1]] else STRUT_CORE
    if k not in ([[1, 1], [1, 1]], [[1, 1], [1, -1]]):
        raise ValueError(f"{config['id']}: sign block {m} normalizes to {k}")
    ops: list[list[Any]] = []
    if config["kind"] == "two_label":
        ops += [["BS.H", 0]] + ([["PS", 1]] if config["t"] < 0 else [])
    ops += [["PS", mode] for mode, sign in enumerate(d2 + d1) if sign < 0]
    ops += [list(op) for op in core]
    ops += [["PS", mode] for mode, sign in enumerate(d1 + d2) if sign < 0]
    return ops


def block_unitary(config: dict[str, Any]) -> Matrix:
    if config["kind"] == "two_label":
        m = tuple(tuple(r) for r in config["m"])
        return two_label_block(m, config["t"])  # type: ignore[arg-type]
    if config["kind"] == "four_label":
        return four_label_block()
    if config["kind"] == "pair":
        return dilation([[q(Fraction(x, 2)) for x in r] for r in config["m"]])
    if config["kind"] == "identity":
        return [[ONE]]
    if config["kind"] == "fringe":
        return dilation([[q(Fraction(x, 2)) for x in r] for r in config["m"]])
    return one_hot_block(config["t"])


ROLES = {
    "two_label": ["label_0", "label_1", "dilation", "dilation"],
    "four_label": ["label", "label", "label", "label", "dilation", "dilation"],
    "one_hot": [f"e{k}" for k in range(DIM)] + ["dilation", "dilation"],
    "pair": ["label_0", "label_1", "dilation", "dilation"],
    "identity": ["target"],
    "fringe": ["label_0", "label_1", "dilation", "dilation"],
}


def fringe_ideal(u: Matrix, k: int) -> list[Q2]:
    """P(mode) for (|0> + e^{i k pi/4} |1>)/sqrt2 into U: (U_k0^2 + U_k1^2 + 2 U_k0 U_k1 cos phi) / 2."""
    c = cos_quarter(k)
    out = []
    for row in u:
        value = add(add(mul(row[0], row[0]), mul(row[1], row[1])), mul(q(2), mul(mul(row[0], row[1]), c)))
        out.append(mul(value, q(Fraction(1, 2))))
    return out


def fringe_iterations(config: dict[str, Any]) -> list[dict[str, Any]]:
    u = block_unitary(config)
    out = []
    for k in range(FRINGE_STEPS):
        probabilities = fringe_ideal(u, k)
        algebra = ZERO
        for role, value in zip(ROLES["fringe"], probabilities, strict=True):
            if role != "dilation":
                algebra = add(algebra, value)
        out.append({"phi_quarter_pi": k, "ideal": [text(x) for x in probabilities], "p_algebra": text(algebra)})
    return out


TWO_PHOTON = ("pair",)


def photon_ports(kind: str) -> list[int]:
    return [0, 1] if kind in TWO_PHOTON else [0]


def permanent(m: list[list[int]]) -> int:
    return m[0][0] * m[1][1] + m[0][1] * m[1][0]


def determinant(m: list[list[int]]) -> int:
    return m[0][0] * m[1][1] - m[0][1] * m[1][0]


def pair_ideal(u: Matrix) -> list[list[Any]]:
    """[a, b, P_indistinguishable, P_distinguishable] for photons on ports 0 and 1 leaving modes a <= b.

    Indistinguishable photons leave (a, b) with |perm U[(a, b), (0, 1)]|^2,
    halved when a = b; distinguishable photons with the sum of the two
    path probabilities, which for a = b is |U[a][0] U[a][1]|^2.
    """
    out = []
    for a in range(len(u)):
        for b in range(a, len(u)):
            amplitude = add(mul(u[a][0], u[b][1]), mul(u[a][1], u[b][0]))
            if a == b:
                together = square(amplitude) / 2
                apart = square(u[a][0]) * square(u[a][1])
            else:
                together = square(amplitude)
                apart = square(u[a][0]) * square(u[b][1]) + square(u[a][1]) * square(u[b][0])
            if together or apart:
                out.append([a, b, str(together), str(apart)])
    return out


def label_coincidence(roles: list[str], table: list[list[Any]]) -> list[str]:
    """P(one photon on each of two distinct non-dilation modes), indistinguishable then distinguishable."""
    rows = [r for r in table if r[0] != r[1] and "dilation" not in (roles[r[0]], roles[r[1]])]
    return [str(sum((Fraction(r[k]) for r in rows), Fraction(0))) for k in (2, 3)]


def two_click(roles: list[str], table: list[list[Any]]) -> dict[str, list[str]]:
    """The two-click terms a < b: the label pair and their total, indistinguishable then distinguishable.

    Threshold detectors with min_detected_photons 2 keep only a < b, so the
    observable is f(V) = (V L_ind + (1 - V) L_dist) / (V T_ind + (1 - V) T_dist)
    for source indistinguishability V; T_dist > 0 on every block.
    """
    apart = [r for r in table if r[0] != r[1]]
    total = [str(sum((Fraction(r[k]) for r in apart), Fraction(0))) for k in (2, 3)]
    return {"label": label_coincidence(roles, table), "total": total}


def algebra_probability(roles: list[str], probabilities: list[Fraction]) -> Fraction:
    return sum((p for role, p in zip(roles, probabilities, strict=True) if role != "dilation"), Fraction(0))


def check_config(config: dict[str, Any]) -> None:
    """Pool worker: the block's exact orthogonality, ideal and every served row's census P or kite relation."""
    u = block_unitary(config)
    require(matmul(u, transpose(u)) == identity(len(u)), f"{config['id']}: the block is not orthogonal")
    if "witness" in config:
        certify_witness(config["id"], config["witness"], [list(r) for r in config["m"]])
    if config["kind"] in ("two_label", "pair", "fringe"):
        require(native_unitary(len(u), native_ops(config)) == u, f"{config['id']}: native gates differ from the block")
    if config["kind"] in TWO_PHOTON:
        table = pair_ideal(u)
        for k in (2, 3):
            require(sum(Fraction(r[k]) for r in table) == 1, f"{config['id']}: the pair ideal does not sum to 1")
        if config["kind"] == "pair":
            check_relation(config["id"], config["m"], label_coincidence(ROLES["pair"], table), config["rows"])
        return
    probabilities = ideal(u)
    require(sum(probabilities) == 1, f"{config['id']}: the ideal does not sum to 1")
    p = algebra_probability(ROLES[config["kind"]], probabilities)
    for row in config["rows"]:
        require(
            p == Fraction(row["p_selector_zero"]),
            f"{config['id']}: P(algebra) = {p} against census {row['source']}[{row['index']}] "
            f"P = {row['p_selector_zero']}",
        )
    if config["kind"] == "one_hot":
        require(p == Fraction(config["p_algebra"]), f"{config['id']}: P(algebra) = {p} against cd_core")


def check_relation(name: str, m: list[list[int]], coincidence: list[str], rows: list[Row]) -> None:
    """perm M vanishes exactly on struts and (l, l^8) pairs; the label coincidence is (perm M / 4)^2 and 1/8."""
    perm, det = permanent(m), determinant(m)
    require({abs(perm), abs(det)} == {0, 2}, f"{name}: perm {perm} and det {det} are not one 0 and one +-2")
    require(
        coincidence == [str(Fraction(perm * perm, 16)), "1/8"],
        f"{name}: label coincidence {coincidence} differs from (perm/4)^2 = {Fraction(perm * perm, 16)} and 1/8",
    )
    for row in rows:
        suppressed = row["source"] == "nonkite_pairs" or row["relation"] == "strut"
        require(
            (perm == 0) == suppressed,
            f"{name}: perm M = {perm} on census {row['source']}[{row['index']}] ({row.get('relation')})",
        )


# ---------------------------------------------------------------- emission


def connected_modes(catalogue_path: Path = CATALOGUE) -> list[int]:
    catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
    specs = catalogue["processors"][CHIP]["specs"]
    require(specs["constraints"]["max_mode_count"] == CHIP_MODES, f"{CHIP} no longer serves {CHIP_MODES} modes")
    modes: list[int] = specs["connected_input_modes"]
    return modes


def block_record(config: dict[str, Any], offset: int) -> dict[str, Any]:
    u = block_unitary(config)
    roles = ROLES[config["kind"]]
    record: dict[str, Any] = {
        "config": config["id"],
        "kind": config["kind"],
        "offset": offset,
        "photons": [offset + port for port in photon_ports(config["kind"])],
    }
    if config["kind"] == "two_label":
        record.update(m=config["m"], t=config["t"])
    if "witness" in config:
        record.update(witness=config["witness"])
    if "reference" in config:
        record.update(reference=config["reference"])
    if config["kind"] == "one_hot":
        record.update(x=list(ONE_HOT_X), y=list(ONE_HOT_Y), t=config["t"])
    if config["kind"] == "fringe":
        record.update(m=config["m"], roles=ROLES["fringe"], iterations=fringe_iterations(config), rows=[])
        return record
    if config["kind"] in TWO_PHOTON:
        table = pair_ideal(u)
        if config["kind"] == "pair":
            record.update(m=config["m"], permanent=permanent(config["m"]), determinant=determinant(config["m"]))
        record.update(
            roles=roles,
            pair_ideal=table,
            label_coincidence=label_coincidence(roles, table),
            two_click=two_click(roles, table),
            rows=[[row["source"], row["index"]] for row in config["rows"]],
        )
        return record
    probabilities = ideal(u)
    record.update(
        roles=roles,
        ideal=[str(p) for p in probabilities],
        p_algebra=str(algebra_probability(roles, probabilities)),
        rows=[[row["source"], row["index"]] for row in config["rows"]],
    )
    return record


def circuit_text(blocks: list[tuple[dict[str, Any], int]], modes: int = CHIP_MODES) -> str:
    input_state = [0] * modes
    components: list[dict[str, Any]] = []
    for config, offset in blocks:
        u = block_unitary(config)
        require(offset + len(u) <= modes, f"{config['id']} at {offset} leaves the circuit")
        for port in photon_ports(config["kind"]):
            input_state[offset + port] = 1
        component: dict[str, Any] = {"at": offset, "unitary": [[text(x) for x in row] for row in u]}
        if config["kind"] in ("two_label", "pair", "fringe"):
            component["native"] = native_ops(config)
        if config["kind"] == "fringe":
            component["prep_phase"] = "phi"
        components.append(component)
    head = {
        "schema": CIRCUIT_SCHEMA,
        "modes": modes,
        "number_field": "each unitary entry [a, b] is the real number a + b sqrt(2)",
        "input_state": input_state,
    }
    # One unitary row per line keeps an 18-mode block reviewable in a diff.
    lines = ["{"] + [f" {json.dumps(key)}: {json.dumps(value)}," for key, value in head.items()]
    lines.append(' "components": [')
    for number, component in enumerate(components):
        rows = component["unitary"]
        native = f', "native": {json.dumps(component["native"])}' if "native" in component else ""
        if "prep_phase" in component:
            native = f', "prep_phase": {json.dumps(component["prep_phase"])}' + native
        lines.append(f'  {{"at": {component["at"]}{native}, "unitary": [')
        lines += [f"   {json.dumps(row)}" + ("," if k < len(rows) - 1 else "") for k, row in enumerate(rows)]
        lines.append("  ]}" + ("," if number < len(components) - 1 else ""))
    lines += [" ]", "}"]
    return "\n".join(lines) + "\n"


DEFINITIONS = {
    "dark": "a one-photon block whose ideal algebra-mode probability p_algebra is 0: x y = 0, so the photon "
    "leaves only through the dilation ports and any algebra-mode detection is implementation error",
    "bright": "a one-photon block with p_algebra = 1: ||x y||^2 = 2, so the photon never reaches a dilation port",
    "half": "a strut, non-kite or four-label block with p_algebra = 1/2, independent of the signs s and t",
    "constructive pair": "a two-photon block on a kite edge: |perm M| = 2, det M = 0, label coincidence "
    "(perm M / 4)^2 = 1/4 for indistinguishable photons against 1/8 for distinguishable ones",
    "suppressed pair": "a two-photon block on a strut or an (l, l^8) pair: perm M = 0, |det M| = 2, label "
    "coincidence 0 for indistinguishable photons against 1/8 for distinguishable ones",
}


MODE_SWAP = {
    "pairing": "block (m, t) of job-NN here against the same block in the same-numbered job of "
    "box_kite_photonic_packed on qpu:belenos, both counted on the samples with exactly one click inside the block",
    "observable": "the residual r = a - p of each of the 16 half blocks (p = 1/2) and the leakage of each dark "
    "(a) and bright (1 - a) block, per layout",
    "block_predictor": "r_swapped(b) = r_packed(b), the residual belongs to the block",
    "slot_predictor": "r_swapped(b) = the mean packed-layout residual of the other half blocks on the slot that "
    "b occupies here, the residual belongs to the modes",
    "statistics": "the Pearson correlation of r_swapped with each predictor over the 16 half blocks, its Fisher-z "
    "95% interval, and per block the two-sample z of a_swapped - a_packed",
    "decision": "block attribute when the block predictor's correlation exceeds 0.7 with a lower bound above 0.3 "
    "and exceeds the slot predictor's; slot attribute for the reverse; mixed otherwise, and a 16-block "
    "correlation cannot distinguish a mixture's weights",
    "falsifier": "a block whose |a_swapped - a_packed| exceeds 4.5 standard errors is a placement effect; a "
    "dark or bright block whose leakage moves with its slot places the 14% outlier in the modes",
}


def preregistered(family: str) -> dict[str, Any]:
    if family == FRINGE:
        return {
            "definitions": {k: DEFINITIONS[k] for k in ("dark", "bright", "half")},
            "observable": "per iteration phi = k pi/4, a(phi): the algebra-mode share of one-click samples in the "
            "block; the fit a(phi) = A + B cos(phi - phi0) over the eight iterations",
            "ideal": "P(phi) = [4 + 2 cos phi (m00 m01 + m10 m11)] / 8: an edge block (job-00) follows "
            "(1 + cos phi)/2, bright at phi = 0 and dark at phi = pi; a strut block (job-01) is flat at 1/2 because "
            "m00 m01 + m10 m11 = 0; every iteration's per-mode ideal is exact over Q(sqrt2)",
            "hardware_report": "fringe visibility B/A against 1 (edge) and 0 (strut), phase offset phi0, a_dark "
            "= a(pi) and a_bright = a(0) on one compiled mesh, with binomial intervals per iteration",
            "falsifier": "on sim:belenos a fitted B more than 4.5 standard errors from 1/2 (edge) or 0 (strut); "
            "on qpu:belenos the edge-minus-strut visibility difference is the chip's zero-divisor contrast",
            "server": "the job sends one ComputationIterator; a result without results_list, or one computed_circuit "
            "per iteration, shows how the platform executes iterations",
        }
    if family == DIAGNOSTICS:
        return {
            "definitions": {k: DEFINITIONS[k] for k in ("dark", "bright")},
            "observable": "per job, in_block: the share of one-click samples on the block's modes, and a, the "
            "algebra-mode share of those, with the per-mode histogram against the exact ideal",
            "hypotheses": {
                "routing": "job-00 sends one photon through the identity on 24 modes; in_block below 0.9 on "
                "qpu:belenos places the bright block's leakage in the chip's realization of the identity",
                "width": "job-01 compiles the bright block as a 4-mode circuit, whose unused chip modes the "
                "transpiler sets as mirrors; in_block and a above the 24-mode single/job-04 result by more than "
                "4.5 standard errors attribute the leakage to the 24-mode fit",
                "gate_form": "job-02 and job-03 send the exact native BS.H / PS / PERM gates; a computed_circuit "
                "equal to the unitary form's, or counts within 4.5 standard errors of job-01 and single/job-04, "
                "show that the transpiler re-fits native gates as a unitary",
                "dark_floor": "job-04 is the dark block in the best form; its a is the chip's dark floor",
            },
            "simulator_stop_rule": "on sim:belenos every job reads in_block 1 and its exact ideal within the "
            "simulator's g2 floor",
        }
    if family == PAIRS:
        return {
            "definitions": {k: DEFINITIONS[k] for k in ("constructive pair", "suppressed pair")},
            "observable": "per job, the two-click samples (min_detected_photons 2, threshold detectors) by mode "
            "pair; the label fraction f is the share of two-click samples with one click on each label mode",
            "ideal": "two_click lists L (the label pair) and T (every a < b pair) for indistinguishable and "
            "distinguishable photons; at source indistinguishability V, f(V) = (V L_ind + (1 - V) L_dist) / "
            "(V T_ind + (1 - V) T_dist): 1/2 on an edge and 0 on a strut at V = 1, 1/6 and 1/7 at V = 0",
            "model": "the fit model is Perceval SLOS of circuit.json under NoiseModel(indistinguishability=V, "
            "g2=the qpu:belenos g2 read at submission) with threshold detection and min_detected_photons 2, V its "
            "only free parameter; the exact two_click terms are its g2 = 0 limit, and at the retained g2 = 0.01 a "
            "suppressed block reads 0.0008 and a constructive block 0.4975 at V = 1, so multiphoton emission "
            "enters the model rather than the fitted V",
            "calibration": "V is fitted from the suppressed (strut and non-kite) blocks, whose f falls from about "
            "1/7 at V = 0 to the g2 floor at V = 1, and the catalogue's HOM figure is the prior it is compared with",
            "hardware_report": "the fitted V with its interval, every constructive block's f against the model's "
            "f_edge(V), every mode-pair frequency against the model at V, with Wilson 95% intervals",
            "falsifier": "a constructive block whose f lies more than 4.5 standard errors from the model's f_edge "
            "at the fitted V, or suppressed blocks whose f values disagree with one V at that bound",
        }
    layout = "single blocks share no job"
    if family == SWAPPED:
        layout = (
            "each job holds the block set of the same-numbered box_kite_photonic_packed job with every block on "
            "the slot three places along (modes 12-23 then 0-11), so each block's modes differ from its packed "
            "run and its job neighbors stay the same; a block's residual a - p that follows the block is an "
            "algebra or compilation property, one that follows the slot is a per-mode source, transmission or "
            "detector property"
        )
    if family == PACKED:
        layout = (
            "blocks share a job and a block-diagonal unitary; inter-block crosstalk is a variable the single "
            "series lacks, and the block on modes 4-7 reads mode 5 (38.2 dark counts per second in the retained "
            "record) as label_1, a floor near 4e-3 of its samples"
        )
    return {
        "definitions": {k: DEFINITIONS[k] for k in ("dark", "bright", "half")},
        "observable": "per block, the fraction a of detected samples whose photon lands on an algebra mode "
        "(roles other than dilation), counted on the samples with exactly one click inside the block; the "
        "full per-mode histogram is kept, since the dilation split carries the direction of y in the kernel",
        "ideal": "a equals the block's p_algebra; the per-mode ideal is the exact |U[k][0]|^2 of circuit.json",
        "simulator_stop_rule": "on sim:belenos, any algebra-mode sample of a dark block or dilation-mode sample "
        "of a bright block, or a half block outside |z| < 4.5 of its binomial, stops the series until the "
        "circuit, the compiler or the simulator's noise model explains it",
        "hardware_report": "on qpu:belenos, the dark floor a_dark, the bright ceiling a_bright, the contrast "
        "a_bright - a_dark, the total variation distance of each per-mode histogram from its ideal and the "
        "one-hot leakage into the 14 unreachable labels, each with a Wilson 95% interval and the dark counts "
        "of the detectors involved",
        "layout": layout,
        **({"mode_swap": MODE_SWAP} if family == SWAPPED else {}),
    }


Job = dict[str, Any]


def family_jobs(configs: list[dict[str, Any]]) -> dict[str, list[Job]]:
    """Each family's jobs: blocks with offsets, the circuit width and the gate form the runner sends."""
    one_photon = [c for c in configs if c["kind"] in ("two_label", "four_label", "one_hot")]
    pairs = [c for c in configs if c["kind"] == "two_label"]
    by_id = {c["id"]: c for c in configs}

    def job(blocks: list[tuple[dict[str, Any], int]], modes: int = CHIP_MODES, form: str = "unitary") -> Job:
        return {"blocks": blocks, "modes": modes, "gate_form": form}

    diagnostics = []
    for number, (kind, reference, offset, modes, form) in enumerate(DIAGNOSTIC_JOBS):
        if kind == "identity":
            config: dict[str, Any] = {"kind": "identity", "id": f"identity-{number:02d}", "rows": []}
        else:
            source = by_id[str(reference)]
            config = {**source, "rows": [], "reference": source["id"], "id": f"{source['id']}-{form}-{modes}"}
        diagnostics.append(job([(config, offset)], modes, form))
    return {
        SINGLE: [job([(c, SINGLE_OFFSET[len(ROLES[c["kind"]])])]) for c in one_photon],
        PACKED: [
            job([(c, PACK_OFFSETS[k]) for k, c in enumerate(pairs[start : start + len(PACK_OFFSETS)])])
            for start in range(0, len(pairs), len(PACK_OFFSETS))
        ],
        SWAPPED: [
            job([(c, SWAP_OFFSETS[k]) for k, c in enumerate(pairs[start : start + len(SWAP_OFFSETS)])])
            for start in range(0, len(pairs), len(SWAP_OFFSETS))
        ],
        PAIRS: [job([(c, PAIR_OFFSET)]) for c in configs if c["kind"] in TWO_PHOTON],
        DIAGNOSTICS: diagnostics,
        FRINGE: [
            job(
                [({**by_id[ref], "kind": "fringe", "rows": [], "reference": ref, "id": f"fringe-{name}"}, 0)],
                4,
                "native",
            )
            for name, ref in FRINGE_BLOCKS
        ],
    }


def budget(family: str, blocks: int) -> dict[str, int]:
    if family == FRINGE:
        samples = FRINGE_SAMPLES * FRINGE_STEPS
        return {"min_detected_photons": 1, "max_samples": samples, "max_shots": SHOT_HEADROOM * samples}
    if family == PAIRS:
        return {"min_detected_photons": 2, "max_samples": PAIR_SAMPLES, "max_shots": PAIR_MAX_SHOTS}
    samples = SAMPLES_PER_BLOCK * blocks
    return {"min_detected_photons": MIN_DETECTED_PHOTONS, "max_samples": samples, "max_shots": SHOT_HEADROOM * samples}


def series(census_path: Path = CENSUS, catalogue_path: Path = CATALOGUE) -> dict[str, str]:
    census = load_census(census_path)
    configs = configurations(census)
    parallel.ordered_map(check_config, configs)
    connected = connected_modes(catalogue_path)
    census_sha256 = hashlib.sha256(census_path.read_bytes()).hexdigest()
    files: dict[str, str] = {}
    for family, jobs in family_jobs(configs).items():
        index = []
        for number, spec in enumerate(jobs):
            name = f"job-{number:02d}"
            blocks = spec["blocks"]
            for config, offset in blocks:
                for port in photon_ports(config["kind"]):
                    require(offset + port in connected, f"{config['id']}: mode {offset + port} has no photon source")
            circuit = circuit_text(blocks, spec["modes"])
            manifest = {
                "schema": SCHEMA,
                "family": family,
                "job": name,
                "platforms": list(PLATFORMS),
                "command": COMMAND,
                "gate_form": spec["gate_form"],
                **budget(family, len(blocks)),
                **(
                    {"parameter": {"name": "phi", "unit": "pi/4"}, "iterations": FRINGE_STEPS}
                    if family == FRINGE
                    else {}
                ),
                "max_duration": MAX_DURATION,
                "census": {"path": census_path.relative_to(ROOT).as_posix(), "sha256": census_sha256},
                "circuit": {"file": "circuit.json", "sha256": hashlib.sha256(circuit.encode()).hexdigest()},
                "blocks": [block_record(config, offset) for config, offset in blocks],
                "preregistered": preregistered(family),
            }
            files[f"{family}/{name}/circuit.json"] = circuit
            files[f"{family}/{name}/cases.json"] = json.dumps(manifest, indent=1) + "\n"
            index.append({"job": name, "configs": [config["id"] for config, _ in blocks]})
        summary: dict[str, dict[str, int]] = {}
        for spec in jobs:
            for config, _ in spec["blocks"]:
                label = f"{config['kind']}_witness" if "witness" in config else config["kind"]
                entry = summary.setdefault(label, {"configs": 0, "rows": 0})
                entry["configs"] += 1
                entry["rows"] += len(config["rows"])
        files[f"{family}/cases.json"] = (
            json.dumps(
                {
                    "schema": SERIES_SCHEMA,
                    "family": family,
                    "census_sha256": census_sha256,
                    "census_sign_blocks": len(
                        {json.dumps(c["m"]) for c in configs if c["kind"] == "pair" and c["rows"]}
                    ),
                    "summary": summary,
                    "jobs": index,
                },
                indent=1,
            )
            + "\n"
        )
    return files


# ---------------------------------------------------------------- admission


def admit(files: dict[str, str], census_path: Path = CENSUS, catalogue_path: Path = CATALOGUE) -> None:
    """Offline admission of written series: digests, exact orthogonality, placement, ideals and row coverage."""
    rows = census_rows(load_census(census_path))
    connected = connected_modes(catalogue_path)
    by_key = {(source, row["index"]): row for source in rows for row in rows[source]}
    for family in FAMILIES:
        index = json.loads(files[f"{family}/cases.json"])
        require(index.get("schema") == SERIES_SCHEMA, f"{family}: series schema differs")
        served: list[tuple[str, int]] = []
        for entry in index["jobs"]:
            base = f"{family}/{entry['job']}"
            manifest = json.loads(files[f"{base}/cases.json"])
            circuit_bytes = files[f"{base}/circuit.json"].encode()
            require(manifest.get("schema") == SCHEMA, f"{base}: cases schema differs")
            require(
                hashlib.sha256(circuit_bytes).hexdigest() == manifest["circuit"]["sha256"],
                f"{base}: circuit.json differs from its cases.json sha256",
            )
            circuit = json.loads(circuit_bytes)
            width = circuit["modes"]
            require(
                isinstance(width, int) and 0 < width <= CHIP_MODES and len(circuit["input_state"]) == width,
                f"{base}: circuit modes {width} do not fit the chip or the input state",
            )
            blocks = manifest["blocks"]
            require(len(circuit["components"]) == len(blocks), f"{base}: components and blocks differ in number")
            occupied: set[int] = set()
            for block, component in zip(blocks, circuit["components"], strict=True):
                name = f"{base}: {block['config']}"
                at = component["at"]
                u = [[parse(x) for x in row] for row in component["unitary"]]
                span = set(range(at, at + len(u)))
                require(
                    at == block["offset"] and not occupied & span and max(span) < width,
                    f"{name} overlaps another block or leaves the chip",
                )
                occupied |= span
                require(
                    block["photons"] == [at + port for port in photon_ports(block["kind"])],
                    f"{name} photons differ from its kind's input ports",
                )
                for mode in block["photons"]:
                    require(mode in connected, f"{name} input mode {mode} has no photon source")
                require(matmul(u, transpose(u)) == identity(len(u)), f"{name} is not orthogonal")
                if block["kind"] in ("two_label", "pair", "fringe"):
                    require(
                        native_unitary(len(u), component.get("native", [])) == u,
                        f"{name} native gates differ from its unitary",
                    )
                if block["kind"] == "fringe":
                    require(component.get("prep_phase") == "phi", f"{name} lacks its phi phase shifter")
                    require(
                        block["iterations"] == fringe_iterations({"kind": "fringe", "m": block["m"]}),
                        f"{name} iteration ideals differ from its sign block",
                    )
                    require(
                        block_unitary({"kind": "fringe", "m": block["m"]}) == u,
                        f"{name} differs from its sign block",
                    )
                    continue
                if "witness" in block:
                    require(not block["rows"], f"{name} carries both census rows and a witness")
                    certify_witness(name, block["witness"], block["m"])
                    if block["kind"] == "two_label":
                        require(block["witness"][5] == block["t"], f"{name} witness t differs from the block's")
                elif "reference" in block:
                    require(
                        family == DIAGNOSTICS and not block["rows"], f"{name} references a block outside diagnostics"
                    )
                    require(
                        block_unitary({"kind": block["kind"], "m": block["m"], "t": block["t"]}) == u,
                        f"{name} differs from the sign block it references",
                    )
                elif block["kind"] in ("two_label", "pair"):
                    require(block["rows"], f"{name} serves no census row and carries no witness")
                block_rows = [by_key.get((source, number)) for source, number in block["rows"]]
                require(None not in block_rows, f"{name} names a row outside the census")
                if block["kind"] in TWO_PHOTON:
                    table = pair_ideal(u)
                    require(table == block["pair_ideal"], f"{name} pair ideal differs from its unitary")
                    coincidence = label_coincidence(block["roles"], table)
                    require(coincidence == block["label_coincidence"], f"{name} label coincidence differs")
                    require(two_click(block["roles"], table) == block["two_click"], f"{name} two-click terms differ")
                    if block["kind"] == "pair":
                        check_relation(name, block["m"], coincidence, block_rows)  # type: ignore[arg-type]
                else:
                    probabilities = ideal(u)
                    require([str(p) for p in probabilities] == block["ideal"], f"{name} ideal differs from its unitary")
                    p = algebra_probability(block["roles"], probabilities)
                    require(str(p) == block["p_algebra"], f"{name} p_algebra differs")
                    for row in block_rows:
                        require(Fraction(row["p_selector_zero"]) == p, f"{name}: census row P differs")  # type: ignore[index]
                served += [(source, number) for source, number in block["rows"]]
            photons = [k for k, n in enumerate(circuit["input_state"]) if n]
            require(
                photons == sorted(mode for b in blocks for mode in b["photons"]),
                f"{base}: input_state differs from the block photons",
            )
        require(len(set(served)) == len(served), f"{family}: a census row is served twice")
        if family in (DIAGNOSTICS, FRINGE):
            require(not served, f"{family}: a diagnostic job serves census rows")
            continue
        kinds = [json.loads(files[f"{family}/{e['job']}/cases.json"])["blocks"] for e in index["jobs"]]
        keys = [
            (json.dumps(b["m"]), b.get("t")) for blocks in kinds for b in blocks if b["kind"] in ("two_label", "pair")
        ]
        want = 16 if family == PAIRS else 32
        require(
            len(set(keys)) == len(keys) == want, f"{family}: {len(set(keys))} distinct sign configurations, not {want}"
        )
        sources = tuple(rows) if family == SINGLE else TWO_LABEL_SOURCES
        expected = {(source, row["index"]) for source in sources for row in rows[source]}
        require(set(served) == expected, f"{family}: served rows differ from the census rows")


def write(directory: Path) -> None:
    files = series()
    admit(files)
    for name, content in files.items():
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"wrote {len(files)} files under {directory}")


def check(directory: Path) -> None:
    files = series()
    retained = {
        path.relative_to(directory).as_posix(): path.read_text(encoding="utf-8")
        for family in FAMILIES
        for path in sorted((directory / family).rglob("*.json"))
    }
    require(set(retained) == set(files), f"file sets differ: {sorted(set(retained) ^ set(files))}")
    differing = sorted(name for name in files if files[name] != retained[name])
    require(not differing, f"retained files differ from the generator: {differing}")
    admit(retained)
    jobs = {family: len(json.loads(files[f"{family}/cases.json"])["jobs"]) for family in FAMILIES}
    print(f"qd box-kite cases: {jobs} jobs, {len(files)} files match")


def _edit(name: str, mutate: Callable[[Any], None]) -> Callable[[dict[str, str]], None]:
    def apply(files: dict[str, str]) -> None:
        value = json.loads(files[name])
        mutate(value)
        files[name] = json.dumps(value, indent=1) + "\n"

    return apply


def _rehash(base: str) -> Callable[[dict[str, str]], None]:
    def apply(files: dict[str, str]) -> None:
        manifest = json.loads(files[f"{base}/cases.json"])
        manifest["circuit"]["sha256"] = hashlib.sha256(files[f"{base}/circuit.json"].encode()).hexdigest()
        files[f"{base}/cases.json"] = json.dumps(manifest, indent=1) + "\n"

    return apply


def self_test() -> int:
    files = series()
    admit(files)
    first = f"{SINGLE}/job-00"
    last_single = f"{SINGLE}/job-{len(json.loads(files[f'{SINGLE}/cases.json'])['jobs']) - 1:02d}"

    def flip_entry(c: Any) -> None:
        c["components"][0]["unitary"][0][0] = ["-" + c["components"][0]["unitary"][0][0][0].lstrip("-"), "0"]

    def move_input(c: Any) -> None:
        c["components"][0]["at"] = 19
        c["input_state"] = [1 if k == 19 else 0 for k in range(CHIP_MODES)]

    def both(*steps: Callable[[dict[str, str]], None]) -> Callable[[dict[str, str]], None]:
        def apply(files: dict[str, str]) -> None:
            for step in steps:
                step(files)

        return apply

    def unplaced(m: Any) -> None:
        m["blocks"][0]["offset"] = 19
        m["blocks"][0]["photons"] = [19]

    file_mutations: list[tuple[str, Callable[[dict[str, str]], None]]] = [
        ("an edited circuit without a new digest", _edit(f"{first}/circuit.json", flip_entry)),
        (
            "a non-orthogonal block under a fresh digest",
            both(_edit(f"{first}/circuit.json", flip_entry), _rehash(first)),
        ),
        (
            "a photon on a mode without a source",
            both(_edit(f"{first}/circuit.json", move_input), _rehash(first), _edit(f"{first}/cases.json", unplaced)),
        ),
        ("an edited ideal", _edit(f"{first}/cases.json", lambda m: m["blocks"][0]["ideal"].reverse())),
        ("a dropped census row", _edit(f"{first}/cases.json", lambda m: m["blocks"][0]["rows"].pop())),
        (
            "a row served twice",
            _edit(f"{first}/cases.json", lambda m: m["blocks"][0]["rows"].append(m["blocks"][0]["rows"][0])),
        ),
        ("a one-hot block claiming another P", _edit(f"{last_single}/cases.json", _claim_bright)),
        ("a strut pair serving kite-edge rows", _swap_pair_rows),
        ("a pair whose sign block is an edge's", _edit(f"{PAIRS}/job-00/cases.json", _edge_block)),
        ("an edited native gate", _edit_native),
        (
            "an edited two-click total",
            _edit(f"{PAIRS}/job-00/cases.json", lambda m: m["blocks"][0]["two_click"]["total"].reverse()),
        ),
    ]
    rejected = 0
    for label, mutate in file_mutations:
        mutated = copy.deepcopy(files)
        mutate(mutated)
        try:
            admit(mutated)
        except (ValueError, KeyError) as error:
            rejected += 1
            print(f"rejected {label}: {error}")
        else:
            raise SystemExit(f"self-test: admission accepted {label}")
    census = load_census()
    census_mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("a census coefficient flip", lambda c: c["design_b"]["within_kite"][0].__setitem__(_column(c, "c0"), 0)),
        ("a census sign flip", lambda c: _flip_sign(c)),
    ]
    for label, mutate in census_mutations:
        mutated_census = copy.deepcopy(census)
        mutate(mutated_census)
        try:
            for config in configurations(mutated_census):
                check_config(config)
        except ValueError as error:
            rejected += 1
            print(f"rejected {label}: {error}")
        else:
            raise SystemExit(f"self-test: generation accepted {label}")
    global ONE_HOT_Y
    saved = ONE_HOT_Y
    ONE_HOT_Y = (2, 13)
    try:
        certify_one_hot(-1)
        check_config({"id": "one_hot-moved", "kind": "one_hot", "t": -1, "rows": [], "p_algebra": "0"})
    except ValueError as error:
        rejected += 1
        print(f"rejected a one-hot pair off the corpus: {error}")
    else:
        raise SystemExit("self-test: the one-hot check accepted (e1 + e10)(e2 - e13), which is not zero")
    finally:
        ONE_HOT_Y = saved
    print(f"self-test: {rejected} mutations rejected")
    return 0


def _edit_native(files: dict[str, str]) -> None:
    """Move one beam splitter of the first single job's native gates and rebind the circuit digest."""
    base = f"{SINGLE}/job-00"
    circuit = files[f"{base}/circuit.json"]
    edited = circuit.replace('["BS.H", 2]', '["BS.H", 1]', 1)
    if edited == circuit:
        raise ValueError("the native-gate fixture holds no BS.H on modes 2 and 3")
    files[f"{base}/circuit.json"] = edited
    _rehash(base)(files)


def _pair_jobs(files: dict[str, str]) -> tuple[str, str]:
    """The first suppressed and the first constructive pair job of the pairs series."""
    names = [f"{PAIRS}/{entry['job']}/cases.json" for entry in json.loads(files[f"{PAIRS}/cases.json"])["jobs"]]
    blocks = {name: json.loads(files[name])["blocks"][0] for name in names}
    pairs = [name for name in names if blocks[name]["kind"] == "pair"]
    strut = next(name for name in pairs if blocks[name]["permanent"] == 0)
    edge = next(name for name in pairs if blocks[name]["permanent"] != 0)
    return strut, edge


def _swap_pair_rows(files: dict[str, str]) -> None:
    strut, edge = _pair_jobs(files)
    a, b = json.loads(files[strut]), json.loads(files[edge])
    a["blocks"][0]["rows"], b["blocks"][0]["rows"] = b["blocks"][0]["rows"], a["blocks"][0]["rows"]
    files[strut], files[edge] = json.dumps(a, indent=1) + "\n", json.dumps(b, indent=1) + "\n"


def _edge_block(m: Any) -> None:
    m["blocks"][0]["m"] = [[1, 1], [1, 1]]


def _claim_bright(m: Any) -> None:
    m["blocks"][0]["p_algebra"] = "0" if m["blocks"][0]["p_algebra"] == "1" else "1"


def _column(census: dict[str, Any], name: str) -> int:
    columns: list[str] = census["design_b"]["columns"]
    return columns.index(name)


def _flip_sign(census: dict[str, Any]) -> None:
    row = census["design_b"]["within_kite"][0]
    column = _column(census, "y_sign")
    row[column] = -row[column]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path)
    group.add_argument("--check", type=Path)
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.write:
        write(args.write)
    else:
        check(args.check)
    return 0


if __name__ == "__main__":
    sys.exit(main())
