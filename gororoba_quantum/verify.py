"""Fail-closed checks of the cd_core port against open_gororoba ground truth.

Every check raises CheckFailed on a mismatch and the module exits nonzero; the
checks use explicit raises because `python -O` strips assert.

The kernel's multiplication_table_{8,16}D.csv fixes every product e_p e_q by
index and sign, so a cell-for-cell diff pins cd_sign to the kernel's
orientation. The zero-divisor corpus is a structural check: the rephasing
e_p -> -e_p (p != 0) multiplies every imaginary-imaginary product sign by -1 and
carries each zero divisor to a zero divisor, so the opposite orientation
reproduces the corpus row for row. Norm multiplicativity is invariant under the
same orthogonal basis change. Each kernel CSV is read only after its sha256
matches every registry record that pins it.

The 42/168 associative/anti-associative split of ordered octonion triples comes
from the Cayley-Dickson signs; the all-positive XOR-indexed table is the group
algebra of F_2^3, which is associative and splits 210/0.
"""

from __future__ import annotations

import csv
import hashlib
import os
import random
import sys
import tomllib
from collections import Counter
from collections.abc import Callable
from itertools import combinations
from math import isclose
from pathlib import Path

from cd_core import (
    cd_multiply,
    cd_sign,
    classify_octonion_triples,
    left_mult_matrix_check,
    sedenion_zero_divisor_corpus,
)
from predict import anf_degree, associator_phase

# GOROROBA_ROOT locates the open_gororoba checkout; the default assumes a
# sibling checkout under ~/Github.
GOROROBA_ROOT = Path(os.environ.get("GOROROBA_ROOT", "~/Github/open_gororoba")).expanduser()
REGISTRY = GOROROBA_ROOT / "registry/data/project_csv"
ZD_CSV = "data/csv/reggiani_standard_zero_divisor_pairs.csv"
ZD_COLUMNS = ("u_low", "u_high", "u_sign", "v_low", "v_high", "v_sign")

SignFn = Callable[[int, int, int], int]
ZdRow = tuple[int, int, int, int, int, int]


class CheckFailed(RuntimeError):
    """A ground-truth check disagreed with the cd_core port."""


def _require(cond: bool, message: str) -> None:
    if not cond:
        raise CheckFailed(message)


def _pinned_csv(rel: str) -> Path:
    """The kernel CSV at rel, once its bytes match every registry record of it."""
    path = GOROROBA_ROOT / rel
    _require(path.is_file(), f"{rel} missing under GOROROBA_ROOT={GOROROBA_ROOT}")
    pins = []
    for record in sorted(REGISTRY.rglob("*.toml")):
        with open(record, "rb") as handle:
            dataset = tomllib.load(handle).get("dataset", {})
        if dataset.get("source_csv") == rel:
            pins.append((record.name, dataset.get("source_sha256")))
    _require(bool(pins), f"no registry record pins {rel}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    stale = [name for name, pin in pins if pin != digest]
    _require(not stale, f"{rel} sha256 {digest} disagrees with {stale}")
    return path


def _unit_label(index: int) -> str:
    return "1" if index == 0 else f"e{index}"


def check_sign_tensor_against_kernel() -> int:
    """Diff every e_p e_q of the kernel's 8D and 16D tables against cd_sign."""
    cells = 0
    for dim in (8, 16):
        path = _pinned_csv(f"data/csv/multiplication_table_{dim}D.csv")
        with open(path, newline="") as handle:
            rows = list(csv.reader(handle))
        labels = [_unit_label(q) for q in range(dim)]
        _require(rows[0][1:] == labels and len(rows) == dim + 1, f"{path.name}: unexpected header or shape")
        for p, row in enumerate(rows[1:]):
            _require(row[0] == labels[p] and len(row) == dim + 1, f"{path.name}: row {p} label or width")
            for q, cell in enumerate(row[1:]):
                want = ("-" if cd_sign(dim, p, q) < 0 else "") + labels[p ^ q]
                _require(cell == want, f"dim {dim}: e{p} e{q} = {cell} in the kernel, {want} from cd_sign")
                cells += 1
    return cells


def _corpus(sign: SignFn) -> set[ZdRow]:
    """Integer-exact (e_i + t e_j)(e_k + s e_l) = 0 enumeration under a sign table."""
    found = set()
    pairs = list(combinations(range(1, 16), 2))
    for i, j in pairs:
        for k, el in pairs:
            if len({i, j, k, el}) != 4:
                continue
            for t in (1, -1):
                for s in (1, -1):
                    out = [0] * 16
                    for p, ap in ((i, 1), (j, t)):
                        for q, bq in ((k, 1), (el, s)):
                            out[p ^ q] += sign(16, p, q) * ap * bq
                    if not any(out):
                        found.add((i, j, t, k, el, s))
    return found


def check_zero_divisor_corpus_against_kernel() -> int:
    """The full signed corpus equals the kernel CSV, row for row."""
    rows: list[ZdRow] = []
    with open(_pinned_csv(ZD_CSV), newline="") as handle:
        for row in csv.DictReader(handle):
            u_low, u_high, u_sign, v_low, v_high, v_sign = (int(row[c]) for c in ZD_COLUMNS)
            rows.append((u_low, u_high, u_sign, v_low, v_high, v_sign))
    kernel = set(rows)
    _require(len(kernel) == len(rows), "kernel corpus carries duplicate rows")
    mine = sedenion_zero_divisor_corpus()
    _require(len(set(mine)) == len(mine), "cd_core corpus carries duplicate rows")
    extra, missing = len(set(mine) - kernel), len(kernel - set(mine))
    _require(not extra and not missing, f"corpus differs: {extra} extra, {missing} missing")
    _require(_corpus(cd_sign) == kernel, "integer-exact corpus disagrees with the float enumeration")
    return len(kernel)


def check_rephasing_preserves_corpus() -> tuple[int, int]:
    """e_p -> -e_p (p != 0) flips sign cells yet leaves the corpus unchanged.

    The flipped table is why the corpus diff carries no orientation evidence.
    Returns the count of flipped cells at dims 8 and 16.
    """

    def t(p: int) -> int:
        return 1 if p == 0 else -1

    def flipped(dim: int, p: int, q: int) -> int:
        return t(p) * t(q) * t(p ^ q) * cd_sign(dim, p, q)

    f8, f16 = (sum(flipped(dim, p, q) != cd_sign(dim, p, q) for p in range(dim) for q in range(dim)) for dim in (8, 16))
    _require((f8, f16) == (42, 210), f"rephasing flips {f8}/{f16} cells, expected 42/210")
    _require(_corpus(flipped) == _corpus(cd_sign), "rephasing changed the zero-divisor corpus")
    return f8, f16


def norm_sq(v: list[float]) -> float:
    return sum(x * x for x in v)


def check_octonion_norm_multiplicative(trials: int = 2000) -> int:
    """|x y| = |x| |y| for octonions on random vectors."""
    rng = random.Random(20261010)
    for n in range(trials):
        x = [rng.gauss(0, 1) for _ in range(8)]
        y = [rng.gauss(0, 1) for _ in range(8)]
        lhs, rhs = norm_sq(cd_multiply(8, x, y)), norm_sq(x) * norm_sq(y)
        _require(isclose(lhs, rhs, rel_tol=1e-9, abs_tol=1e-9), f"octonion norm fails on trial {n}")
    return trials


def check_sedenion_norm_not_multiplicative(trials: int = 4000) -> int:
    """The sedenions carry zero divisors, so |x y| = |x| |y| fails on some trial."""
    rng = random.Random(20261011)
    for n in range(trials):
        x = [rng.gauss(0, 1) for _ in range(16)]
        y = [rng.gauss(0, 1) for _ in range(16)]
        if not isclose(norm_sq(cd_multiply(16, x, y)), norm_sq(x) * norm_sq(y), rel_tol=1e-9, abs_tol=1e-9):
            return n
    raise CheckFailed(f"sedenion norm multiplicative on all {trials} trials")


def check_octonion_triple_split() -> tuple[int, int]:
    split = classify_octonion_triples()
    _require(split == (42, 168), f"octonion triple split {split}, expected (42, 168)")
    return split


def check_w_is_signed_z_string() -> dict[tuple[float, ...], int]:
    """W = L_{e_i e_j}^{-1} L_{e_i} L_{e_j} is a signed Z-string for all 21 pairs.

    Its diagonal is a character of F_2^3, +1 exactly on the subspace
    {0, i, j, i^j} of associating k. The 21 pairs land on the 7 non-identity
    characters, 3 pairs each, one character per Fano line. Returns the
    character multiplicities.
    """
    hits: Counter[tuple[float, ...]] = Counter()
    for i, j in combinations(range(1, 8), 2):
        w = left_mult_matrix_check(i, j)
        diag = tuple(round(w[q][q], 9) for q in range(8))
        off = max(abs(w[r][c]) for r in range(8) for c in range(8) if r != c)
        _require(off < 1e-9, f"W not diagonal for ({i},{j})")
        _require(all(abs(abs(d) - 1.0) < 1e-9 for d in diag), f"W not +/-1 for ({i},{j})")
        subspace = {0, i, j, i ^ j}
        _require(all((diag[q] > 0) == (q in subspace) for q in range(8)), f"W sign pattern for ({i},{j})")
        hits[diag] += 1
    _require(len(hits) == 7 and set(hits.values()) == {3}, f"W characters {dict(hits)}")
    return dict(hits)


def check_associator_degree_rule(dims: tuple[int, ...] = (8, 16, 32, 64, 128)) -> dict[int, dict[int, int]]:
    """deg omega_ij = max(1, bitlen(max(i,j)) - 2) for every pair, dims 8 through 128.

    omega_ij is the diagonal of W = L_{e_i e_j}^dagger L_{e_i} L_{e_j}. The
    degree depends only on the doubling level where the pair first appears:
    octonion pairs carry linear phases (Z-strings), sedenion pairs quadratic
    phases (CZ), and each further doubling raises the degree by one, so W
    leaves the Clifford group from dim 32 on. Quaternion pairs have degree 0 at
    dim 4 and degree 1 from dim 8. Returns the degree census per dimension.
    """
    census: dict[int, dict[int, int]] = {}
    for dim in dims:
        hist: Counter[int] = Counter()
        for i, j in combinations(range(1, dim), 2):
            degree = anf_degree([0 if w > 0 else 1 for w in associator_phase(dim, i, j)])
            _require(degree == max(1, max(i, j).bit_length() - 2), f"dim {dim} ({i},{j}) degree {degree}")
            hist[degree] += 1
        census[dim] = dict(sorted(hist.items()))
    return census


def check_left_mult_sign_degree(dims: tuple[int, ...] = (8, 16, 32, 64, 128)) -> None:
    """f_m(x) = [cd_sign(dim,m,x) = -1] has degree log2(dim) - 1 for every m != 0.

    L_{e_m} is that sign diagonal followed by X gates, so octonion left
    multiplications are Clifford (degree 2: Z and CZ) and sedenion ones carry a
    degree-3 sign (CCZ) that leaves the Clifford group.
    """
    for dim in dims:
        want = dim.bit_length() - 2
        for m in range(1, dim):
            degree = anf_degree([0 if cd_sign(dim, m, x) > 0 else 1 for x in range(dim)])
            _require(degree == want, f"dim {dim} L_e{m} sign degree {degree}, expected {want}")


def _schreier_sign_vector(dim: int, a: int, b: int) -> int:
    """Bit x of the result is set where L_{e_{a^b}}^{-1} L_{e_a} L_{e_b} has sign -1 on |x>."""
    vec = 0
    for x in range(dim):
        sign = cd_sign(dim, b, x) * cd_sign(dim, a, b ^ x) * cd_sign(dim, a ^ b, x)
        if sign < 0:
            vec |= 1 << x
    return vec


def _f2_basis(vectors: set[int]) -> list[int]:
    basis: list[int] = []
    for v in sorted(vectors):
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return basis


def _group_by_enumeration(dim: int) -> tuple[int, int]:
    """|<L_{e_m}>| and its largest element order, by closing the generators.

    An element is (mask, a): |x> -> (-1)^(bit x of mask) |x ^ a>.
    """

    def compose(g: tuple[int, int], h: tuple[int, int]) -> tuple[int, int]:
        shifted = sum(1 << x for x in range(dim) if (g[0] >> (x ^ h[1])) & 1)
        return h[0] ^ shifted, g[1] ^ h[1]

    gens = [(sum(1 << x for x in range(dim) if cd_sign(dim, m, x) < 0), m) for m in range(dim)]
    seen = {(0, 0)}
    frontier = [(0, 0)]
    while frontier:
        fresh = []
        for e in frontier:
            for g in gens:
                p = compose(g, e)
                if p not in seen:
                    seen.add(p)
                    fresh.append(p)
        frontier = fresh
    max_order = 1
    for e in seen:
        k, p = 1, e
        while p != (0, 0):
            p, k = compose(e, p), k + 1
        max_order = max(max_order, k)
    return len(seen), max_order


def check_left_mult_group(dims: tuple[int, ...] = (4, 8, 16, 32, 64)) -> dict[int, int]:
    """G = <L_{e_m}> has exponent 4 at every dimension and order 2^(n + 2^(n-1)) at the checked ones.

    The exponent bound holds for every n (the argument below). The order
    formula is a computed pattern: this check pins it at the dimensions passed
    in, 8 through 64 by default, and the survey's closure extends it to n = 8;
    no proof covers larger n.

    Every element is a signed XOR translation D P_a, so the translation part maps
    G onto F_2^n with kernel H, the +/-1 diagonals in G. Schreier's lemma with
    transversal {L_{e_a}} generates H by the diagonals L_{e_{a^b}}^{-1} L_{e_a}
    L_{e_b}; H is abelian, so log2 |H| is the F_2 rank of their sign vectors: 1 at
    dim 4 (H = {+/-I}, G = Q8) and 2^(n-1) at the checked dims from 8, every vector of
    degree at most n - 2. (D P_a)^2 is diagonal and squares to I, so no product of basis
    left multiplications has order beyond 4. Enumeration confirms |G| and the
    exponent through dim 16. Returns log2 |G| per dimension.
    """
    out = {}
    for dim in dims:
        n = dim.bit_length() - 1
        basis = _f2_basis({_schreier_sign_vector(dim, a, b) for a in range(dim) for b in range(dim)})
        want = 1 if n == 2 else 2 ** (n - 1)
        _require(len(basis) == want, f"dim {dim}: sign subgroup rank {len(basis)}, expected {want}")
        for v in basis:
            degree = anf_degree([(v >> x) & 1 for x in range(dim)])
            _require(degree <= max(n - 2, 0), f"dim {dim}: sign subgroup vector of degree {degree}")
        out[dim] = n + len(basis)
        if dim <= 16:
            order, max_order = _group_by_enumeration(dim)
            _require(order == 2 ** out[dim], f"dim {dim}: enumeration finds |G| = {order}, Schreier 2^{out[dim]}")
            _require(max_order == 4, f"dim {dim}: largest element order {max_order}")
    return out


def main() -> int:
    try:
        cells = check_sign_tensor_against_kernel()
        print(f"sign tensor vs kernel multiplication tables: {cells} cells match (dims 8, 16)")
        rows = check_zero_divisor_corpus_against_kernel()
        print(f"zero-divisor corpus vs kernel CSV: {rows} signed rows match")
        f8, f16 = check_rephasing_preserves_corpus()
        print(f"rephasing e_p -> -e_p flips {f8}/{f16} sign cells and preserves the corpus")
        print(f"octonion norm multiplicative: {check_octonion_norm_multiplicative()} trials")
        print(f"sedenion norm non-multiplicative at trial {check_sedenion_norm_not_multiplicative()}")
        print(f"octonion triple split (assoc, anti): {check_octonion_triple_split()}")
        hits = check_w_is_signed_z_string()
        print(f"associator W: 21 pairs diagonal +/-1, {len(hits)} Z-strings x 3 pairs each")
        for dim, hist in check_associator_degree_rule().items():
            print(f"associator phase degree census dim {dim}: {hist}")
        check_left_mult_sign_degree()
        print("L_e_m sign degree = log2(dim) - 1 for every m != 0, dims 8 through 128")
        orders = check_left_mult_group()
        print(f"<L_e_m> order log2 per dim: {orders}; exponent 4 (enumerated through dim 16)")
    except CheckFailed as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
