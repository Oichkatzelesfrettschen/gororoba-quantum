"""Exact census of the seven sedenion box-kites on cd_core, and every ideal prediction the box-kite experiments use.

cd_core.cd_sign is the only multiplication table: every product below is
sum_{p,q} x_p y_q cd_sign(16, p, q) e_{p XOR q} with integer coefficients, and
the Design B products are checked term for term against cd_core.cd_multiply.
Nothing is read from a box-kite formula; each structure is derived from the
products and then required to equal its closed form.

- Two-blades. The 210 elements e_i + t e_j (1 <= i < j <= 15, t = +-1) and all
  210 x 210 products give the squared norms N(ab) in {0, 4, 8}. The ordered
  zero products are exactly the 336 rows of cd_core.sedenion_zero_divisor_corpus.
- Assessors and kites. The planes span(e_L, e_U) carrying a zero product are the
  42 assessors; grouped by X = L XOR U they form 7 box-kites with strut constant
  S = X XOR 8, assessors (L, L XOR X) for L in 1..7 minus S, and index set
  {1..15} minus {S, 8, X}. The 7 planes (l, l XOR 8) carry no zero product.
- Edges, struts, faces. For assessors P = (L, U) and Q = (L', U') of one kite
  the zero set of (e_L + s e_U)(e_L' + t e_U') over (s, t) is {(+,+), (-,-)}
  (same-sign edge), {(+,-), (-,+)} (opposite-sign edge) or empty (strut). The
  four product terms land on two labels, L^L' = U^U' and L^U' = U^L', so
  everything rests on p0 = g(L,L') g(U,U') and p1 = g(L,U') g(U,L'): same
  p0 = p1 = -1, opposite p0 = p1 = +1, strut p0 != p1. Faces split into the
  zigzag sail (3 opposite edges), 3 trefoil sails (1 opposite edge, the one not
  incident to the vertex shared with the zigzag), the vent opposite the zigzag
  (3 opposite edges) and 3 further vents (1 opposite edge).
- Design B. The fixed-operand LCU applies (L_{e_L} + s L_{e_U})/2 to
  y = (e_L' + t e_U')/sqrt2 and reads the selector: P(s = 0) = N/8 =
  ||x y||^2 / 2 for x = (e_L + s e_U)/sqrt2. Restricted to span{e_L', e_U'}
  the same LCU is a selector plus one data qubit (labels L^L', L^U'), whose
  output coefficients c0, c1 reproduce P exactly; the selector-1 branch gives
  1 - P. The post-selected two-label state carries the coherence c0 c1 /
  (c0^2 + c1^2), read in the full encoding with 2^popcount(X) settings.
- Twist. (B + b)(D + d) = 0 iff (B + d)(D - b) = 0 over all signed basis
  pairs with b, d low and B, D high; the twist sends an edge of kite S to an
  edge of kite S XOR b XOR d with the other sign type, and a strut to a pair
  of (l, l XOR 8) planes; P(s = 0) is preserved on every within-kite and
  non-kite signed pair.
- Annihilators. ker L_x and ker R_x have dimension 4 on each of the 84
  diagonals, spanned by their 4 two-blade partners, and 0 on every other
  two-blade.
- Associator signs omega(i, j, k) on the kite index triples, the fixed-pair
  witness with uniform k, the fixed-i witness with uniform (j, k), and the
  uniform baseline 25/256 with P(c = 1) = 231/512.

Package witnesses. scripts/box_kite_packages.py recomputes the basis-product,
sign and zero-product facts through every package of the Cayley-Dickson stack
under its declared map (identity, python-octonion's signed relabeling,
SageMath's opposite algebra and e3/e5/e6 flip, the split relation of the
negative controls) and the record keeps one sha256 per fact. --write
multiplies with each package's own arithmetic on the build host; --check
recomputes the digests through the retained basis tables and requires the
retained element verdicts to equal them, so CI imports no package.

open_gororoba's de_marrais CSVs enter only through a declared map (identity on
(low, high) and signs, box_kite id to strut_signature): --open-gororoba DIR
recomputes the comparison, and the record retains file digests and agreement
counts, never the tables. --check without DIR binds the retained comparison
to the census counts.

Usage: "$PYTHON" scripts/box_kite_census.py
       (--write PATH --open-gororoba DIR | --check PATH [--open-gororoba DIR] | --self-test [--record PATH])
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import itertools
import json
import re
import sys
from collections.abc import Callable
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import box_kite_packages as packages  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_multiply, cd_sign, left_mult_matrix, sedenion_zero_divisor_corpus, triple_sign  # noqa: E402

DIM = 16
GENERATOR = 8
SCHEMA = "box-kite-census-v1"
RECORD = ROOT / "docs/evidence/box_kite_census/census.json"
OPEN_GOROROBA_FILES = (
    "data/csv/de_marrais_assessors.csv",
    "data/csv/de_marrais_boxkites.csv",
    "data/csv/de_marrais_strut_table.csv",
    "data/csv/de_marrais_boxkite_edges.csv",
)
SIGNS = (1, -1)
SAME = frozenset({(1, 1), (-1, -1)})
OPPOSITE = frozenset({(1, -1), (-1, 1)})
DESIGN_B_COLUMNS = [
    "kite",
    "p_low",
    "p_high",
    "x_sign",
    "q_low",
    "q_high",
    "y_sign",
    "relation",
    "p_selector_zero",
    "label_0",
    "label_1",
    "c0",
    "c1",
    "d0",
    "d1",
    "coherence_selector_0",
    "coherence_selector_1",
    "full_coherence_settings",
]

Blade = tuple[int, int, int]
Plane = tuple[int, int]


class CensusError(RuntimeError):
    """A recomputed fact disagrees with its closed form or with the retained record."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CensusError(message)


def frac(value: Fraction) -> str:
    return str(value)


def product(x: dict[int, int], y: dict[int, int]) -> dict[int, int]:
    """x y with integer coefficients from cd_core.cd_sign; zero terms dropped."""
    out: dict[int, int] = {}
    for p, a in x.items():
        for q, b in y.items():
            out[p ^ q] = out.get(p ^ q, 0) + cd_sign(DIM, p, q) * a * b
    return {k: v for k, v in sorted(out.items()) if v}


def blade_vector(blade: Blade) -> dict[int, int]:
    i, j, t = blade
    return {i: 1, j: t}


def dense(terms: dict[int, int]) -> list[float]:
    out = [0.0] * DIM
    for index, value in terms.items():
        out[index] = float(value)
    return out


def checked_product(x: dict[int, int], y: dict[int, int]) -> dict[int, int]:
    """product(x, y), required to equal cd_core.cd_multiply term for term."""
    sparse = product(x, y)
    full = cd_multiply(DIM, dense(x), dense(y))
    require(all(full[k] == float(sparse.get(k, 0)) for k in range(DIM)), f"cd_multiply disagrees on {x} {y}: {full}")
    return sparse


def g(p: int, q: int) -> int:
    return cd_sign(DIM, p, q)


def omega(i: int, j: int, k: int) -> int:
    left, right = triple_sign(DIM, i, j, k)
    return left * right


BLADES: list[Blade] = [(i, j, t) for i, j in itertools.combinations(range(1, DIM), 2) for t in SIGNS]


def blade_norm_row(a: Blade) -> list[int]:
    """N(a b) = sum of squared coefficients of a b for every two-blade b, in BLADES order."""
    x = blade_vector(a)
    return [sum(c * c for c in product(x, blade_vector(b)).values()) for b in BLADES]


def exact_rank(rows: list[list[int]]) -> int:
    a = [[Fraction(v) for v in row] for row in rows]
    rank = 0
    for col in range(len(a[0]) if a else 0):
        pivot = next((r for r in range(rank, len(a)) if a[r][col] != 0), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        for r in range(len(a)):
            if r != rank and a[r][col] != 0:
                factor = a[r][col] / a[rank][col]
                a[r] = [u - factor * v for u, v in zip(a[r], a[rank], strict=True)]
        rank += 1
    return rank


def right_mult_matrix(x: dict[int, int]) -> list[list[int]]:
    """R_x: y -> y x over the basis, (R_x)[q ^ p][q] = sum_p x_p cd_sign(16, q, p)."""
    mat = [[0] * DIM for _ in range(DIM)]
    for p, xp in x.items():
        for q in range(DIM):
            mat[q ^ p][q] += xp * cd_sign(DIM, q, p)
    return mat


def blade_nullities(a: Blade) -> tuple[int, int]:
    """(dim ker L_a, dim ker R_a) over the rationals."""
    x = blade_vector(a)
    floats = left_mult_matrix(DIM, dense(x))
    left = [[int(v) for v in row] for row in floats]
    require(
        all(float(v) == w for row, frow in zip(left, floats, strict=True) for v, w in zip(row, frow, strict=True)),
        "L_a entries",
    )
    return DIM - exact_rank(left), DIM - exact_rank(right_mult_matrix(x))


def twist_block(b: int) -> tuple[int, int, int]:
    """(tests, mismatches, zero products) of the twist over every B, d, D and sign at low index b.

    Claim: (sB e_B + sb e_b)(sD e_D + sd e_d) = 0 iff (sB e_B + sd e_d)(sD e_D - sb e_b) = 0.
    """
    tests = mismatches = zeros = 0
    for big_b in range(9, DIM):
        for d in range(1, GENERATOR):
            for big_d in range(9, DIM):
                if b == d or big_b == big_d:
                    continue
                for sb, s_big_b, sd, s_big_d in itertools.product(SIGNS, repeat=4):
                    lhs = not product({big_b: s_big_b, b: sb}, {big_d: s_big_d, d: sd})
                    rhs = not product({big_b: s_big_b, d: sd}, {big_d: s_big_d, b: -sb})
                    tests += 1
                    mismatches += lhs != rhs
                    zeros += lhs
    return tests, mismatches, zeros


def kite_index_set(strut: int) -> list[int]:
    return sorted(set(range(1, DIM)) - {strut, GENERATOR, GENERATOR ^ strut})


def kite_triples(strut: int) -> list[tuple[str, int, int, int]]:
    """Every ordered distinct triple of kite indices with its vertex-shape class.

    Each kite index is the low or high member of one assessor (vertex). Two
    indices on one vertex give the classes ij/jk/ik-same, split by whether the
    third index sits on the strut partner or an edge neighbor; three vertices
    split by the number of strut pairs among them and, for a face, sail or
    vent and whether i ^ j ^ k = 0.
    """
    x = GENERATOR ^ strut
    assessors = [(low, low ^ x) for low in range(1, GENERATOR) if low != strut]
    vertex = {index: v for v, pair in enumerate(assessors) for index in pair}
    partner = {u: v for u in range(6) for v in range(6) if u != v and assessors[u][0] ^ assessors[v][0] == strut}
    out = []
    for i, j, k in itertools.permutations(kite_index_set(strut), 3):
        vs = (vertex[i], vertex[j], vertex[k])
        if len(set(vs)) == 2:
            position = "ij" if vs[0] == vs[1] else ("jk" if vs[1] == vs[2] else "ik")
            same = max(set(vs), key=vs.count)
            other = min(set(vs), key=vs.count)
            name = f"{position}-same-vertex-third-{'strut' if partner[same] == other else 'edge'}"
        else:
            struts = sum(partner[p] == q for p, q in ((vs[0], vs[1]), (vs[1], vs[2]), (vs[0], vs[2])))
            if struts:
                name = f"three-vertices-{struts}-strut"
            else:
                lows = [assessors[v][0] for v in vs]
                face = "sail" if lows[0] ^ lows[1] ^ lows[2] == 0 else "vent"
                name = f"face-{face}-{'xor0' if i ^ j ^ k == 0 else 'xor-nonzero'}"
        out.append((name, i, j, k))
    return out


def associator_classes(strut: int) -> dict[str, list[int]]:
    """[non-associating, total] ordered distinct triples of kite indices per vertex-shape class."""
    out: dict[str, list[int]] = {}
    for name, i, j, k in kite_triples(strut):
        cell = out.setdefault(name, [0, 0])
        cell[0] += omega(i, j, k) == -1
        cell[1] += 1
    return dict(sorted(out.items()))


def associator_exemplars(strut: int) -> dict[str, list[int]]:
    """Cheapest triple of each class whose sign is constant: [i, j, k, omega, walk CNOTs, data bits].

    The fixed-triple Hadamard test on a basis input walks the data register
    k -> k^j -> k^j^i -> k under control, one CNOT per set bit of j, i and
    i^j, over the popcount(i | j) data bits those indices touch; the cheapest
    walk (then permutation order) represents the class.
    """
    classes = associator_classes(strut)
    found: dict[str, list[int]] = {}
    for name, i, j, k in kite_triples(strut):
        negative, total = classes[name]
        if negative not in (0, total):
            continue
        cost = i.bit_count() + j.bit_count() + (i ^ j).bit_count()
        if name not in found or cost < found[name][4]:
            found[name] = [i, j, k, omega(i, j, k), cost, (i | j).bit_count()]
    return dict(sorted(found.items()))


def design_b_row(kite: int, p: Plane, s: int, q: Plane, t: int, relation: str) -> list[Any]:
    """One Design B prediction with its reduced two-label encoding and post-selected coherences."""
    (low, high), (q_low, q_high) = p, q
    x = {low: 1, high: s}
    y = {q_low: 1, q_high: t}
    terms = checked_product(x, y)
    norm = sum(c * c for c in terms.values())
    p0 = Fraction(norm, 8)
    if (low ^ high) != (q_low ^ q_high):
        # Different XOR labels put the four terms on four labels, so the two
        # selector branches are orthogonal whatever the signs.
        require(len(terms) == 4 and p0 == Fraction(1, 2), f"cross-slug pair {p} {q} is not four labels at P = 1/2")
        return [kite, low, high, s, q_low, q_high, t, relation, frac(p0), *([None] * 9)]
    label_0, label_1 = low ^ q_low, low ^ q_high
    c0 = g(low, q_low) + s * t * g(high, q_high)
    c1 = t * g(low, q_high) + s * g(high, q_low)
    d0 = g(low, q_low) - s * t * g(high, q_high)
    d1 = t * g(low, q_high) - s * g(high, q_low)
    require(terms == {k: v for k, v in sorted({label_0: c0, label_1: c1}.items()) if v}, f"labels of {p}{q}")
    require(Fraction(c0 * c0 + c1 * c1, 8) == p0, f"reduced encoding P differs on {p} {q}")
    require(Fraction(d0 * d0 + d1 * d1, 8) == 1 - p0, f"selector-1 branch of {p} {q}")
    coherence = [frac(Fraction(a * b, a * a + b * b)) if a * a + b * b else None for a, b in ((c0, c1), (d0, d1))]
    settings = 1 << (label_0 ^ label_1).bit_count()
    return [
        kite,
        low,
        high,
        s,
        q_low,
        q_high,
        t,
        relation,
        frac(p0),
        label_0,
        label_1,
        c0,
        c1,
        d0,
        d1,
        coherence[0],
        coherence[1],
        settings,
    ]


def nonkite_rows_for(nonkite: list[Plane]) -> list[list[Any]]:
    """Design B rows on ordered pairs of distinct (l, l^8) planes, all four signs (kite field 0)."""
    return [
        design_b_row(0, p, s, q, t, "nonkite")
        for p, q in itertools.permutations(nonkite, 2)
        for s, t in itertools.product(SIGNS, SIGNS)
    ]


class DesignBRows:
    """Design B rows of one kite (both orders of every assessor pair, all four signs); picklable for the pool."""

    def __init__(self, kites: dict[int, dict[str, Any]]) -> None:
        self.kites = kites

    def __call__(self, strut: int) -> list[list[Any]]:
        kite = self.kites[strut]
        relation = {}
        for edge in kite["edges"]:
            a, b = (tuple(v) for v in edge["pair"])
            relation[(a, b)] = relation[(b, a)] = f"edge_{edge['type']}"
        for a, b in kite["struts"]:
            relation[(tuple(a), tuple(b))] = relation[(tuple(b), tuple(a))] = "strut"
        rows = []
        for p, q in itertools.permutations([tuple(v) for v in kite["assessors"]], 2):
            for s, t in itertools.product(SIGNS, SIGNS):
                rows.append(design_b_row(strut, p, s, q, t, relation[(p, q)]))
        return rows


def census() -> dict[str, Any]:
    """Every box-kite fact, recomputed from cd_core; the gororoba-open comparison is attached separately."""
    norms = parallel.ordered_map(blade_norm_row, BLADES)
    position = {blade: n for n, blade in enumerate(BLADES)}

    def n_of(a: Blade, b: Blade) -> int:
        return norms[position[a]][position[b]]

    histogram: dict[int, int] = {}
    for row in norms:
        for value in row:
            histogram[value] = histogram.get(value, 0) + 1
    require(set(histogram) <= {0, 4, 8}, f"two-blade norms outside {{0, 4, 8}}: {histogram}")
    zero_pairs = [(a, b) for a in BLADES for b in BLADES if n_of(a, b) == 0]
    corpus = sorted(sedenion_zero_divisor_corpus())
    require(sorted((*a, *b) for a, b in zero_pairs) == corpus, "two-blade zero products differ from the cd_core corpus")
    require(len(corpus) == 336, f"corpus has {len(corpus)} rows")
    require(all(n_of(b, a) == 0 for a, b in zero_pairs), "a zero product fails in the swapped order")
    diagonals = sorted({a for a, _ in zero_pairs} | {b for _, b in zero_pairs})
    require(len(diagonals) == 84, f"{len(diagonals)} diagonals")
    planes = sorted({(i, j) for i, j, _ in diagonals})
    require(len(planes) == 42 and all(i < GENERATOR < j for i, j in planes), "42 low/high assessor planes")
    nonkite = [(low, low ^ GENERATOR) for low in range(1, GENERATOR)]
    require(not set(nonkite) & set(planes), "an (l, l^8) plane carries a zero product")

    def zero_set(p: Plane, q: Plane) -> frozenset[tuple[int, int]]:
        return frozenset((s, t) for s in SIGNS for t in SIGNS if n_of((*p, s), (*q, t)) == 0)

    kites: dict[int, dict[str, Any]] = {}
    by_x: dict[int, list[Plane]] = {}
    for plane in planes:
        by_x.setdefault(plane[0] ^ plane[1], []).append(plane)
    require(sorted(by_x) == list(range(9, DIM)), f"kite XOR labels {sorted(by_x)}")
    totals = {"same": 0, "opposite": 0}
    eta_rows = []
    for x, assessors in sorted(by_x.items()):
        strut = x ^ GENERATOR
        require(assessors == [(low, low ^ x) for low in range(1, GENERATOR) if low != strut], f"U = L ^ (8 ^ {strut})")
        require(sorted(i for pair in assessors for i in pair) == kite_index_set(strut), f"kite {strut} index set")
        edges: list[dict[str, Any]] = []
        struts: list[list[list[int]]] = []
        strut_signs: list[list[int]] = []
        for p, q in itertools.combinations(assessors, 2):
            zs = zero_set(p, q)
            require(zero_set(q, p) == zs, f"zero set of {p}{q} depends on the order")
            p0 = g(p[0], q[0]) * g(p[1], q[1])
            p1 = g(p[0], q[1]) * g(p[1], q[0])
            if not zs:
                require(p[0] ^ q[0] == strut and p0 != p1, f"strut {p}{q}: lows xor S and p0 != p1")
                struts.append([list(p), list(q)])
                strut_signs.append([p0, p1])
                continue
            require(zs in (SAME, OPPOSITE), f"edge {p}{q} zero set {sorted(zs)}")
            kind = "same" if zs == SAME else "opposite"
            require(p0 == p1 == (-1 if kind == "same" else 1), f"edge {p}{q}: sign products {p0} {p1}")
            psi = {(a, b): 0 if g(a, b) == 1 else 1 for a in p + q for b in p + q}
            eta_anti = psi[(p[0], q[1])] ^ psi[(p[1], q[0])]
            eta_diag = psi[(p[0], q[0])] ^ psi[(p[1], q[1])]
            eta_rows.append((kind, eta_anti, eta_diag))
            totals[kind] += 1
            edges.append(
                {
                    "pair": [list(p), list(q)],
                    "type": kind,
                    "zero_signs": [list(z) for z in sorted(zs, reverse=True)],
                    "sign_products": [p0, p1],
                }
            )
        require(len(edges) == 12 and len(struts) == 3, f"kite {strut}: {len(edges)} edges, {len(struts)} struts")
        require(sum(e["type"] == "same" for e in edges) == 6, f"kite {strut}: same/opposite split")
        degree = {v: 0 for v in assessors}
        for e in edges:
            for v in e["pair"]:
                degree[tuple(v)] += 1
        require(set(degree.values()) == {4}, f"kite {strut}: assessor degrees {degree}")
        kind_of = {}
        for e in edges:
            a, b = (tuple(v) for v in e["pair"])
            kind_of[frozenset((a, b))] = e["type"]
        partner = {tuple(a): tuple(b) for a, b in struts} | {tuple(b): tuple(a) for a, b in struts}
        faces = []
        for tri in itertools.combinations(assessors, 3):
            sides = [frozenset(pair) for pair in itertools.combinations(tri, 2)]
            if not all(side in kind_of for side in sides):
                continue
            sail = tri[0][0] ^ tri[1][0] ^ tri[2][0] == 0
            opposite = sum(kind_of[side] == "opposite" for side in sides)
            require(opposite in (1, 3), f"kite {strut} face {tri}: {opposite} opposite edges")
            name = (
                ("zigzag" if opposite == 3 else "trefoil")
                if sail
                else ("vent_all_opposite" if opposite == 3 else "vent")
            )
            faces.append(
                {"vertices": [list(v) for v in tri], "lows_xor_zero": sail, "opposite_edges": opposite, "class": name}
            )
        require(len(faces) == 8, f"kite {strut}: {len(faces)} faces")
        classes = sorted(f["class"] for f in faces)
        require(classes == ["trefoil"] * 3 + ["vent"] * 3 + ["vent_all_opposite", "zigzag"], f"kite {strut}: {classes}")
        zigzag = next({tuple(v) for v in f["vertices"]} for f in faces if f["class"] == "zigzag")
        vent = next({tuple(v) for v in f["vertices"]} for f in faces if f["class"] == "vent_all_opposite")
        require(
            vent == {partner[v] for v in zigzag}, f"kite {strut}: the all-opposite vent is the zigzag's opposite face"
        )
        for f in faces:
            if f["class"] != "trefoil":
                continue
            members = {tuple(v) for v in f["vertices"]}
            shared = members & zigzag
            require(len(shared) == 1, f"kite {strut}: trefoil {members} shares {len(shared)} zigzag vertices")
            (apex,) = shared
            for pair in itertools.combinations(sorted(members), 2):
                expected = "same" if apex in pair else "opposite"
                require(kind_of[frozenset(pair)] == expected, f"kite {strut}: trefoil {members} edge {pair}")
            f["shared_zigzag_vertex"] = list(apex)
        twists = []
        for e in edges + [{"pair": pair, "type": "strut"} for pair in struts]:
            (b, big_b), (d, big_d) = (tuple(v) for v in e["pair"])
            p_new, q_new = (d, big_b), (b, big_d)
            x_new = d ^ big_b
            if x_new == GENERATOR:
                target, relation = None, "nonkite_planes"
            else:
                target = x_new ^ GENERATOR
                zs = zero_set(p_new, q_new)
                relation = "strut" if not zs else ("edge_same" if zs == SAME else "edge_opposite")
            twists.append(
                {
                    "pair": e["pair"],
                    "relation": "strut" if e["type"] == "strut" else f"edge_{e['type']}",
                    "twisted": [list(p_new), list(q_new)],
                    "twisted_kite": target,
                    "twisted_relation": relation,
                }
            )
        kites[strut] = {
            "strut_constant": strut,
            "xor_label": x,
            "index_set": kite_index_set(strut),
            "assessors": [list(a) for a in assessors],
            "struts": struts,
            "strut_sign_products": strut_signs,
            "edges": edges,
            "faces": faces,
            "twists": twists,
        }
    require(totals == {"same": 42, "opposite": 42}, f"edge totals {totals}")
    for kite in kites.values():
        for tw in kite["twists"]:
            require(
                (tw["relation"] == "strut") == (tw["twisted_relation"] == "nonkite_planes"),
                f"twist of {tw['pair']} lands on {tw['twisted_relation']}",
            )
            if tw["relation"] != "strut":
                require(tw["twisted_relation"].startswith("edge_"), f"twist of edge {tw['pair']}")

    # Frustration of each kite's signed octahedron under vertex switching.
    frustration = {}
    for negative_kind in ("same", "opposite"):
        values = []
        for kite in kites.values():
            labels = [tuple(v) for v in kite["assessors"]]
            signed = [
                (labels.index(tuple(e["pair"][0])), labels.index(tuple(e["pair"][1])), e["type"] == negative_kind)
                for e in kite["edges"]
            ]
            values.append(
                min(sum(bad ^ sw[u] ^ sw[v] for u, v, bad in signed) for sw in itertools.product((0, 1), repeat=6))
            )
        frustration[f"negative_on_{negative_kind}"] = values

    # Theorem 3 over all 49 low/high planes: never one, three or four zero sign choices.
    all_planes = [(low, high) for low in range(1, GENERATOR) for high in range(9, DIM)]
    theorem3: dict[str, int] = {}
    for p, q in itertools.combinations(all_planes, 2):
        key = str(len(zero_set(p, q)))
        theorem3[key] = theorem3.get(key, 0) + 1
    require(set(theorem3) == {"0", "2"} and theorem3["2"] == 84, f"Theorem 3 histogram {theorem3}")

    nullities = parallel.ordered_map(blade_nullities, BLADES)
    diagonal_set = set(diagonals)
    for blade, (left, right) in zip(BLADES, nullities, strict=True):
        require((left, right) == ((4, 4) if blade in diagonal_set else (0, 0)), f"nullity of {blade}: {left}, {right}")
    annihilators = []
    for a in diagonals:
        left = [b for b in BLADES if n_of(a, b) == 0]
        right = [b for b in BLADES if n_of(b, a) == 0]
        for side in (left, right):
            require(len(side) == 4, f"{a}: {len(side)} partners")
            require(
                exact_rank([[blade_vector(b).get(k, 0) for k in range(DIM)] for b in side]) == 4, f"{a}: partner rank"
            )
        annihilators.append(
            {
                "diagonal": list(a),
                "left_partners": [list(b) for b in left],
                "right_partners": [list(b) for b in right],
                "nullity_left": 4,
                "nullity_right": 4,
            }
        )

    twist_counts = parallel.ordered_map(twist_block, list(range(1, GENERATOR)), min_items=1)
    twist = {
        "claim": "(sB e_B + sb e_b)(sD e_D + sd e_d) = 0 iff (sB e_B + sd e_d)(sD e_D - sb e_b) = 0, "
        "b, d in 1..7, B, D in 9..15, b != d, B != D",
        "tests": sum(c[0] for c in twist_counts),
        "mismatches": sum(c[1] for c in twist_counts),
        "zero_products": sum(c[2] for c in twist_counts),
    }
    require(twist == {**twist, "tests": 28224, "mismatches": 0, "zero_products": 1344}, f"twist {twist}")

    rows = [row for chunk in parallel.ordered_map(DesignBRows(kites), sorted(kites), min_items=1) for row in chunk]
    require(len(rows) == 840, f"{len(rows)} within-kite Design B rows")
    zero_signs = {"edge_same": SAME, "edge_opposite": OPPOSITE, "strut": frozenset()}
    for row in rows:
        require((row[8] == "0") == ((row[3], row[6]) in zero_signs[row[7]]), f"row {row}: zero set")
        require(row[8] in ("0", "1", "1/2") and (row[7] == "strut") == (row[8] == "1/2"), f"row {row}: value")
    # The twist maps the row (L, U, s; L', U', t) to (L', U, s; L, U', -t):
    # x' = s e_U + e_L' and y' = t e_U' - e_L = -(e_L - t e_U').
    twist_rows = rows + nonkite_rows_for(nonkite)
    for row in twist_rows:
        _, low, high, s, q_low, q_high, t = row[:7]
        before = n_of((low, high, s), (q_low, q_high, t))
        after = n_of((q_low, high, s), (low, q_high, -t))
        require(before == after, f"twist changes P on {row[:7]}")
    twist["rows_with_p_preserved"] = len(twist_rows)
    swapped = sum(
        tw["relation"] != tw["twisted_relation"]
        for kite in kites.values()
        for tw in kite["twists"]
        if tw["relation"] != "strut"
    )
    require(swapped == 84, f"the twist keeps the sign type on {84 - swapped} edges")
    twist["edges_with_sign_type_swapped"] = swapped
    cross = []
    first = {strut: tuple(kites[strut]["assessors"][0]) for strut in kites}
    for sa, sb in itertools.permutations(sorted(kites), 2):
        for s, t in itertools.product(SIGNS, SIGNS):
            cross.append(design_b_row(sa, first[sa], s, first[sb], t, f"cross_kite_{sb}"))
    nonkite_rows = nonkite_rows_for(nonkite)
    require(all(r[8] == "1/2" for r in nonkite_rows), "an (l, l^8) pair departs from P = 1/2")
    all_cross: dict[str, int] = {}
    for p, q in itertools.permutations(planes + nonkite, 2):
        if (p[0] ^ p[1]) == (q[0] ^ q[1]) and p in planes:
            continue
        for s, t in itertools.product(SIGNS, SIGNS):
            key = frac(Fraction(n_of((*p, s), (*q, t)), 8))
            all_cross[key] = all_cross.get(key, 0) + 1
    require(set(all_cross) == {"1/2"}, f"cross-kite and nonkite pairs {all_cross}")
    fixture = design_b_row(3, (1, 10), 1, (2, 13), -1, "cross_kite_7")
    require(checked_product({1: 1, 10: 1}, {2: 1, 13: -1}) == {3: 1, 7: 1, 8: 1, 12: -1}, "negative fixture product")
    require(checked_product({1: 1, 10: 1}, {4: 1, 15: -1}) == {}, "dark witness product")

    class_tables = parallel.ordered_map(associator_classes, sorted(kites), min_items=1)
    require(all(table == class_tables[0] for table in class_tables), "associator classes differ between kites")
    fixed_pair: dict[str, list[list[int]]] = {}
    for i, j in itertools.combinations(range(1, DIM), 2):
        fixed_pair.setdefault(frac(Fraction(sum(omega(i, j, k) for k in range(DIM)), DIM)), []).append([i, j])
    fixed_i = {
        str(i): frac(Fraction(sum(omega(i, j, k) for j in range(DIM) for k in range(DIM)), DIM * DIM))
        for i in range(DIM)
    }
    negative = sum(omega(i, j, k) == -1 for i in range(DIM) for j in range(DIM) for k in range(DIM))
    require(negative == 1848, f"{negative} non-associating sedenion basis triples")
    uniform = Fraction(DIM**3 - 2 * negative, DIM**3)
    require(uniform == Fraction(25, 256) and Fraction(negative, DIM**3) == Fraction(231, 512), "uniform baseline")
    xor_zero = [(a, b, a ^ b) for a, b in itertools.combinations(range(1, DIM), 2) if b < a ^ b]
    require(
        len(xor_zero) == 35 and all(omega(*p) == 1 for t in xor_zero for p in itertools.permutations(t)),
        "xor-zero triples",
    )
    octonion_negative = sum(
        triple_sign(8, i, j, k)[0] != triple_sign(8, i, j, k)[1] for i in range(8) for j in range(8) for k in range(8)
    )
    require(octonion_negative == 168, f"{octonion_negative} non-associating octonion triples")
    assessor_pairs = {tuple(a) for a in planes}
    assessor_values = {frac(Fraction(sum(omega(i, j, k) for k in range(DIM)), DIM)) for i, j in assessor_pairs}

    eta = {
        "edges": len(eta_rows),
        "anti_diagonal_one_iff_same": sum((e[1] == 1) == (e[0] == "same") for e in eta_rows),
        "diagonal_equals_anti_diagonal": sum(e[1] == e[2] for e in eta_rows),
    }

    widths = {str(s): 1 << (GENERATOR ^ s).bit_count() for s in sorted(kites)}
    return {
        "schema": SCHEMA,
        "convention": {
            "algebra": "sedenions, D = 16, cd_core.cd_sign, doubling (a,b)(c,d) = (ac - conj(d) b, da + b conj(c))",
            "basis": "e_k is basis state |k>, index bit b on register qubit b",
            "diagonal": "(L, U, s) is e_L + s e_U with L in 1..7 and U in 9..15",
            "design_b": "P(selector=0) = N(x y)/8 = ||x y||^2 / 2 for x = (e_L + x_sign e_U)/sqrt2, "
            "y = (e_L' + y_sign e_U')/sqrt2",
        },
        "two_blades": {
            "count": len(BLADES),
            "ordered_products_by_norm": {str(k): v for k, v in sorted(histogram.items())},
            "ordered_zero_products": len(zero_pairs),
            "zero_products_equal_cd_core_corpus": True,
            "zero_product_order_swap_symmetric": True,
            "diagonals": len(diagonals),
        },
        "assessors": [list(p) for p in planes],
        "nonkite_planes": [list(p) for p in nonkite],
        "kites": [kites[s] for s in sorted(kites)],
        "edge_totals": totals,
        "theorem3_zero_sign_choices_over_49_planes": dict(sorted(theorem3.items())),
        "eta_parity": eta,
        "frustration_minimum": frustration,
        "annihilators": annihilators,
        "twist": twist,
        "design_b": {
            "columns": DESIGN_B_COLUMNS,
            "within_kite": rows,
            "cross_kite_controls": cross,
            "nonkite_pairs": nonkite_rows,
            "negative_fixture": fixture,
            "all_cross_and_nonkite_ordered_signed_pairs": dict(sorted(all_cross.items())),
        },
        "associator": {
            "kite_triple_classes": class_tables[0],
            "classes_identical_across_kites": True,
            "deterministic_exemplars": {str(s): associator_exemplars(s) for s in sorted(kites)},
            "fixed_pair_uniform_k": {k: v for k, v in sorted(fixed_pair.items())},
            "fixed_pair_uniform_k_on_assessor_planes": sorted(assessor_values),
            "fixed_i_uniform_jk": fixed_i,
            "uniform_all_triples": frac(uniform),
            "uniform_p_control_one": frac(Fraction(negative, DIM**3)),
            "non_associating_basis_triples": negative,
            "xor_zero_triples_all_associate": len(xor_zero),
            "octonion_non_associating_basis_triples": octonion_negative,
        },
        "experiment_counts": {
            "within_kite_rows": len(rows),
            "cross_kite_control_rows": len(cross),
            "nonkite_rows": len(nonkite_rows),
            "fixed_pair_witnesses": sum(len(v) for v in fixed_pair.values()),
            "fixed_i_witnesses": len(fixed_i),
            "full_coherence_settings_by_kite": widths,
        },
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_open_gororoba(record: dict[str, Any], base: Path) -> dict[str, Any]:
    """Agreement of gororoba-open's de_marrais CSVs with the census under the identity map."""
    files = {name: sha256(base / name) for name in OPEN_GOROROBA_FILES}

    def rows(name: str) -> list[dict[str, str]]:
        with (base / name).open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    census_assessors = {tuple(a) for a in record["assessors"]}
    kites = {k["strut_constant"]: k for k in record["kites"]}
    assessor_rows = {(int(r["low"]), int(r["high"])) for r in rows(OPEN_GOROROBA_FILES[0])}
    membership = rows(OPEN_GOROROBA_FILES[1])
    member_agree = sum(
        (int(r["low"]), int(r["high"])) in {tuple(a) for a in kites[int(r["strut_signature"])]["assessors"]}
        for r in membership
    )
    strut_rows = rows(OPEN_GOROROBA_FILES[2])
    set_agree = 0
    columns_agree = 0
    disagree = []
    for r in strut_rows:
        kite = kites[int(r["strut_signature"])]
        cols = {letter: (int(r[f"{letter}_low"]), int(r[f"{letter}_high"])) for letter in "ABCDEF"}
        set_agree += set(cols.values()) == {tuple(a) for a in kite["assessors"]}
        read = {frozenset((cols[a], cols[b])) for a, b in (("A", "F"), ("B", "E"), ("C", "D"))}
        actual = {frozenset((tuple(a), tuple(b))) for a, b in kite["struts"]}
        if read == actual:
            columns_agree += 1
        else:
            disagree.append(kite["strut_constant"])
    edge_rows = rows(OPEN_GOROROBA_FILES[3])
    census_edges = {}
    for kite in record["kites"]:
        for e in kite["edges"]:
            census_edges[(kite["strut_constant"], tuple(e["pair"][0]), tuple(e["pair"][1]))] = {
                tuple(z) for z in e["zero_signs"]
            }
    edge_agree = 0
    for r in edge_rows:
        key = (int(r["strut_signature"]), (int(r["a_low"]), int(r["a_high"])), (int(r["b_low"]), int(r["b_high"])))
        solutions = {tuple(int(v) for v in item.split(",")) for item in r["sign_solutions"].split(";")}
        edge_agree += census_edges.get(key) == solutions
    return {
        "map": "identity on (low, high) and on signs; box_kite id -> strut_signature (the census strut constant)",
        "files_sha256": files,
        "assessors": {
            "total": len(census_assessors),
            "agree": len(assessor_rows & census_assessors),
            "csv_rows": len(assessor_rows),
        },
        "kite_membership": {"total": len(census_assessors), "agree": member_agree, "csv_rows": len(membership)},
        "strut_table_assessor_sets": {"total": len(kites), "agree": set_agree},
        "strut_table_columns_read_as_struts": {
            "total": len(kites),
            "agree": columns_agree,
            "disagreeing_strut_constants": sorted(disagree),
            "reading": "(A,F), (B,E), (C,D) as strut pairs; the CSV writer sorts assessors by (low, high) "
            "before filling A..F",
        },
        "edges": {"total": len(census_edges), "agree": edge_agree, "csv_rows": len(edge_rows)},
    }


def validate_comparison(comparison: Any, record: dict[str, Any]) -> None:
    """Bind a retained comparison to the census counts when the CSVs are not at hand."""
    require(isinstance(comparison, dict), "open_gororoba comparison missing")
    require(
        set(comparison)
        == {
            "map",
            "files_sha256",
            "assessors",
            "kite_membership",
            "strut_table_assessor_sets",
            "strut_table_columns_read_as_struts",
            "edges",
        },
        "comparison fields",
    )
    require(sorted(comparison["files_sha256"]) == sorted(OPEN_GOROROBA_FILES), "comparison file set")
    require(all(re.fullmatch(r"[0-9a-f]{64}", v) for v in comparison["files_sha256"].values()), "comparison digests")
    totals = {
        "assessors": len(record["assessors"]),
        "kite_membership": len(record["assessors"]),
        "strut_table_assessor_sets": len(record["kites"]),
        "strut_table_columns_read_as_struts": len(record["kites"]),
        "edges": sum(len(k["edges"]) for k in record["kites"]),
    }
    for name, total in totals.items():
        entry = comparison[name]
        require(entry["total"] == total, f"comparison {name} total {entry['total']} != census {total}")
        require(type(entry["agree"]) is int and 0 <= entry["agree"] <= total, f"comparison {name} agreement")
        for key in ("csv_rows",):
            if key in entry:
                require(type(entry[key]) is int and entry[key] >= entry["agree"], f"comparison {name} rows")
    columns = comparison["strut_table_columns_read_as_struts"]
    require(
        len(columns["disagreeing_strut_constants"]) == columns["total"] - columns["agree"]
        and set(columns["disagreeing_strut_constants"]) <= set(range(1, GENERATOR)),
        "comparison strut-column disagreements",
    )


def witness_inputs(record: dict[str, Any]) -> packages.Task:
    """The Design B operand pairs and kite triples every witness multiplies, from the census rows."""
    table = record["design_b"]
    rows = table["within_kite"] + table["cross_kite_controls"] + table["nonkite_pairs"] + [table["negative_fixture"]]
    pairs = [({r[1]: 1, r[2]: r[3]}, {r[4]: 1, r[5]: r[6]}) for r in rows]
    return packages.Task(
        "table", pairs, {k["strut_constant"]: kite_triples(k["strut_constant"]) for k in record["kites"]}
    )


def witness_digests(record: dict[str, Any], mode: str, names: list[str]) -> dict[str, dict[str, Any]]:
    """Fact digests (or the import error) of each named witness under one product mode."""
    task = witness_inputs(record)
    task.mode = mode
    items = [item for name in names for item in packages.tasks_for(name)]
    results = parallel.ordered_map(task, items, min_items=1)
    out: dict[str, dict[str, Any]] = {}
    position = 0
    for name in names:
        count = len(packages.tasks_for(name))
        out[name] = packages.assemble(name, results[position : position + count])
        position += count
    return out


WRAPPER_EXPRESSIONS = (("e1+e10", "e4-e15"), ("e1+e10", "e4+e15"), ("e1+e10", "e2-e13"))


def parse_expression(text: str) -> dict[int, int]:
    """'2e5 - 2e14' -> {5: 2, 14: -2}; '0' -> {}."""
    compact = text.replace(" ", "")
    if compact == "0":
        return {}
    terms = re.findall(r"([+-]?)(\d*)e(\d+)", compact)
    require("".join(f"{a}{b}e{c}" for a, b, c in terms).lstrip("+") == compact.lstrip("+"), f"expression {text!r}")
    return {int(c): (-1 if a == "-" else 1) * int(b or 1) for a, b, c in terms}


def expression_terms(text: str) -> dict[int, int]:
    return dict(sorted(parse_expression(text).items()))


def pinned_release(package: str) -> str:
    """The release tables.json binds the package to, or the SageMath export's version line."""
    if package == "sagemath":
        return str(json.loads(packages.SAGE_TABLE.read_text(encoding="utf-8"))["sage"])
    return str(json.loads(packages.TABLES.read_text(encoding="utf-8"))["packages"][package]["version"])


def package_section(record: dict[str, Any]) -> dict[str, Any]:
    """Every witness through its package's own arithmetic (build host only), against cd_core."""
    import importlib.metadata

    names = [w[0] for w in packages.WITNESSES if w[4] != "wrapper"]
    reference = witness_digests(record, "table", ["cd_core-16", "cd_core-8"])
    element = witness_digests(record, "element", names)
    witnesses: dict[str, Any] = {}
    for spec in packages.WITNESSES:
        name, package, dim, mapping, role, arithmetic, key, traps = spec
        try:
            if package == "sagemath":
                import sage.version

                version = str(sage.version.version)
            else:
                distribution = {"splitoct": "SplitOct"}.get(package, package)
                version = importlib.metadata.version(distribution)
        except Exception as failure:  # noqa: BLE001  (a missing distribution is the retained verdict)
            version = f"unavailable: {type(failure).__name__}: {failure}"
        entry: dict[str, Any] = {
            "package": package,
            "version": version,
            "dimension": dim,
            "map": mapping,
            "role": role,
            "arithmetic": arithmetic,
            "retained_table": key,
            "traps": traps,
            "pinned_release": pinned_release(package),
        }
        if role == "wrapper":
            try:
                import hypercomplex_algebra

                texts = {f"({a})({b})": hypercomplex_algebra.multiply_expressions(a, b) for a, b in WRAPPER_EXPRESSIONS}
                entry["expressions"] = texts
                entry["error"] = None
            except Exception as failure:  # noqa: BLE001
                entry["expressions"] = None
                entry["error"] = f"{type(failure).__name__}: {failure}"
        else:
            result = element[name]
            entry["error"] = result.get("error")
            entry["facts"] = result.get("facts")
        witnesses[name] = entry
    section = {
        "method": "each fact is the sha256 of its canonical JSON computed through the witness's own product "
        "under its declared map; agreement is digest equality with cd_core",
        "reference": {name: value["facts"] for name, value in reference.items()},
        "witnesses": witnesses,
    }
    finish_package_section(section, record, reference)
    return section


def finish_package_section(section: dict[str, Any], record: dict[str, Any], reference: dict[str, Any]) -> None:
    """Agreement flags, the split control and the strut-line binding; required laws raise."""
    ref16, ref8 = reference["cd_core-16"]["facts"], reference["cd_core-8"]["facts"]
    lines = reference["cd_core-8"]["values"]["strut_lines"] if "values" in reference["cd_core-8"] else None
    if lines is not None:
        struts = sorted([k["strut_constant"], *sorted([a[0], b[0]])] for k in record["kites"] for a, b in k["struts"])
        require(sorted(line[:3] for line in lines) == struts, "strut lines (u, v, S) differ from the kite struts")
        require(all(line[3] is True and line[4] == 1 for line in lines), "a strut line is not an associative triple")
    split: dict[str, Any] = {}
    for name, entry in section["witnesses"].items():
        # Every declared witness is evidence only through its mapped arithmetic, so a
        # package that fails to import or evaluate fails the census.
        require(entry["error"] is None, f"{name}: the declared witness failed: {entry['error']}")
        if entry["role"] == "wrapper":
            agree = {}
            require(
                sorted(entry["expressions"]) == sorted(f"({a})({b})" for a, b in WRAPPER_EXPRESSIONS),
                f"{name}: expression set",
            )
            for a, b in WRAPPER_EXPRESSIONS:
                text = entry["expressions"][f"({a})({b})"]
                agree[f"({a})({b})"] = expression_terms(text) == checked_product(
                    expression_terms(a), expression_terms(b)
                )
            require(all(agree.values()), f"{name}: wrapper expressions differ from cd_core on {agree}")
            entry["agrees_with_cd_core"] = agree
            continue
        ref = ref16 if entry["dimension"] == 16 else ref8
        require(sorted(entry["facts"]) == sorted(ref), f"{name}: fact set differs")
        entry["agrees_with_cd_core"] = {fact: entry["facts"][fact] == ref[fact] for fact in sorted(ref)}
        if entry["role"] == "split control":
            shared = [f for f in packages.SPLIT_FACTS_SHARED if entry["agrees_with_cd_core"][f]]
            differing = [f for f in sorted(ref) if not entry["agrees_with_cd_core"][f]]
            require(shared == list(packages.SPLIT_FACTS_SHARED), f"{name}: split control loses a shared fact")
            require(
                set(packages.SPLIT_FACTS_DIFFERING) <= set(differing),
                f"{name}: split control keeps a zero-product fact",
            )
            split[name] = {"shared_with_octonions": shared, "differing": differing}
        else:
            require(
                all(entry["agrees_with_cd_core"].values()),
                f"{name}: declared map fails on {entry['agrees_with_cd_core']}",
            )
    section["split_control"] = split
    section["strut_lines_are_kite_struts"] = True


def verify_package_section(
    section: Any, record: dict[str, Any], table_digests: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Bind a retained package section to cd_core and to the retained basis tables (CI imports no package)."""
    require(isinstance(section, dict) and set(section) >= {"method", "reference", "witnesses"}, "package section")
    require(set(section["witnesses"]) == {w[0] for w in packages.WITNESSES}, "package witness set")
    reference = {name: table_digests[name] for name in ("cd_core-16", "cd_core-8")}
    require(section["reference"] == {name: value["facts"] for name, value in reference.items()}, "cd_core fact digests")
    versions = json.loads(packages.TABLES.read_text(encoding="utf-8"))["packages"]
    sage_version = json.loads(packages.SAGE_TABLE.read_text(encoding="utf-8"))["sage"]
    rebuilt: dict[str, Any] = {}
    for spec in packages.WITNESSES:
        name, package, dim, mapping, role, arithmetic, key, traps = spec
        entry = section["witnesses"][name]
        fixed = {
            "package": package,
            "dimension": dim,
            "map": mapping,
            "role": role,
            "arithmetic": arithmetic,
            "retained_table": key,
            "traps": traps,
        }
        require(all(entry.get(k) == v for k, v in fixed.items()), f"{name}: declared witness fields")
        if package == "sagemath":
            require(entry["pinned_release"] == sage_version, f"{name}: pinned release")
            require(f"version {entry['version']}," in sage_version, f"{name}: version {entry['version']}")
        else:
            pinned = versions[package]["version"]
            require(entry["pinned_release"] == pinned, f"{name}: pinned release {entry['pinned_release']}")
            require(
                pinned.startswith("commit ") or entry["version"] == pinned,
                f"{name}: installed version {entry['version']} against the pin {pinned}",
            )
        clean = {
            **fixed,
            "version": entry["version"],
            "pinned_release": entry["pinned_release"],
            "error": entry["error"],
        }
        if role == "wrapper":
            clean["expressions"] = entry["expressions"]
        else:
            require(
                entry["facts"] == table_digests[name]["facts"],
                f"{name}: retained verdict differs from its retained table",
            )
            clean["facts"] = entry["facts"]
        rebuilt[name] = clean
    out = {"method": section["method"], "reference": section["reference"], "witnesses": rebuilt}
    finish_package_section(out, record, reference)
    return out


def table_digest_names() -> list[str]:
    return ["cd_core-16", "cd_core-8"] + [w[0] for w in packages.WITNESSES if w[6] is not None]


def canonical(record: dict[str, Any]) -> str:
    return json.dumps(record, sort_keys=True, indent=1, ensure_ascii=True) + "\n"


def build(
    open_gororoba: Path | None, retained: dict[str, Any] | None, table_digests: dict[str, dict[str, Any]] | None = None
) -> dict[str, Any]:
    record = census()
    if retained is None:
        record["package_witnesses"] = package_section(record)
    else:
        digests = table_digests if table_digests is not None else witness_digests(record, "table", table_digest_names())
        record["package_witnesses"] = verify_package_section(retained.get("package_witnesses"), record, digests)
    if open_gororoba is not None:
        record["open_gororoba_comparison"] = compare_open_gororoba(record, open_gororoba)
    else:
        require(retained is not None, "--write needs --open-gororoba")
        comparison = retained.get("open_gororoba_comparison") if isinstance(retained, dict) else None
        validate_comparison(comparison, record)
        record["open_gororoba_comparison"] = comparison
    validate_comparison(record["open_gororoba_comparison"], record)
    return record


def check_text(text: str, recompute: Callable[[dict[str, Any] | None], dict[str, Any]]) -> None:
    try:
        retained = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CensusError(f"record is not JSON: {exc}") from exc
    require(isinstance(retained, dict), "record is not an object")
    require(canonical(recompute(retained)) == text, "retained census differs from the recomputation")


def self_test(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    base = census()
    digests = witness_digests(base, "table", table_digest_names())

    def recompute(retained: dict[str, Any] | None) -> dict[str, Any]:
        record = copy.deepcopy(base)
        if not isinstance(retained, dict):
            raise CensusError("record is not an object")
        record["package_witnesses"] = verify_package_section(retained.get("package_witnesses"), record, digests)
        comparison = retained.get("open_gororoba_comparison")
        validate_comparison(comparison, record)
        record["open_gororoba_comparison"] = comparison
        return record

    check_text(text, recompute)
    pristine = json.loads(text)

    def edge_type(r: dict[str, Any]) -> None:
        edge = r["kites"][0]["edges"][0]
        edge["type"] = "opposite" if edge["type"] == "same" else "same"

    def strut_swap(r: dict[str, Any]) -> None:
        s = r["kites"][0]["struts"]
        s[0][1], s[1][1] = s[1][1], s[0][1]

    def drop_assessor(r: dict[str, Any]) -> None:
        r["kites"][2]["assessors"].pop()

    def probability(r: dict[str, Any]) -> None:
        row = r["design_b"]["within_kite"][0]
        row[8] = "1/2" if row[8] != "1/2" else "0"

    def coherence(r: dict[str, Any]) -> None:
        row = next(x for x in r["design_b"]["within_kite"] if x[15] not in (None, "0"))
        row[15] = "-" + row[15] if not row[15].startswith("-") else row[15][1:]

    def face_class(r: dict[str, Any]) -> None:
        face = next(f for f in r["kites"][1]["faces"] if f["class"] == "trefoil")
        face["class"] = "vent"

    def nullity(r: dict[str, Any]) -> None:
        r["annihilators"][5]["nullity_left"] = 5

    def twisted(r: dict[str, Any]) -> None:
        r["kites"][3]["twists"][0]["twisted_kite"] = 7 if r["kites"][3]["twists"][0]["twisted_kite"] != 7 else 6

    def baseline(r: dict[str, Any]) -> None:
        r["associator"]["uniform_all_triples"] = "1/4"

    def associator_count(r: dict[str, Any]) -> None:
        cell = next(iter(r["associator"]["kite_triple_classes"].values()))
        cell[0] += 1

    def twist_mismatch(r: dict[str, Any]) -> None:
        r["twist"]["mismatches"] = 1

    def comparison_agree(r: dict[str, Any]) -> None:
        r["open_gororoba_comparison"]["edges"]["agree"] = r["open_gororoba_comparison"]["edges"]["total"] + 1

    def comparison_columns(r: dict[str, Any]) -> None:
        r["open_gororoba_comparison"]["strut_table_columns_read_as_struts"]["agree"] += 1

    def nonkite_plane(r: dict[str, Any]) -> None:
        r["nonkite_planes"][0] = [1, 10]

    def witness_digest(r: dict[str, Any]) -> None:
        facts = r["package_witnesses"]["witnesses"]["hyprat-16"]["facts"]
        facts["kite_structure"] = "0" * 64

    def witness_agreement(r: dict[str, Any]) -> None:
        r["package_witnesses"]["witnesses"]["cayley-dickson-16"]["agrees_with_cd_core"]["twist_counts"] = False

    def split_control(r: dict[str, Any]) -> None:
        r["package_witnesses"]["split_control"]["splitoct-8"]["differing"] = []

    def witness_version(r: dict[str, Any]) -> None:
        r["package_witnesses"]["witnesses"]["hypercomplex-16"]["pinned_release"] = "0.3.3"

    def wrapper_expression(r: dict[str, Any]) -> None:
        texts = r["package_witnesses"]["witnesses"]["hypercomplex-16-wrapper"]["expressions"]
        texts[next(iter(texts))] = "e5"

    def witness_missing(r: dict[str, Any]) -> None:
        entry = r["package_witnesses"]["witnesses"]["hypercomplex-16"]
        entry["error"], entry["facts"], entry["agrees_with_cd_core"] = "ImportError: hypercomplex", None, None

    def wrapper_missing(r: dict[str, Any]) -> None:
        r["package_witnesses"]["witnesses"]["hypercomplex-16-wrapper"]["error"] = "ImportError: hypercomplex_algebra"

    def reference_digest(r: dict[str, Any]) -> None:
        r["package_witnesses"]["reference"]["cd_core-8"]["strut_lines"] = "f" * 64

    mutations = (
        witness_digest,
        witness_agreement,
        split_control,
        witness_version,
        wrapper_expression,
        witness_missing,
        wrapper_missing,
        reference_digest,
        edge_type,
        strut_swap,
        drop_assessor,
        probability,
        coherence,
        face_class,
        nullity,
        twisted,
        baseline,
        associator_count,
        twist_mismatch,
        comparison_agree,
        comparison_columns,
        nonkite_plane,
    )
    for mutate in mutations:
        mutated = copy.deepcopy(pristine)
        mutate(mutated)
        try:
            check_text(canonical(mutated), recompute)
        except CensusError:
            continue
        raise CensusError(f"--check accepted the {mutate.__name__} mutation")
    print(f"box-kite census self-test: retained record passes; {len(mutations)} mutations rejected")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--open-gororoba", type=Path, help="open_gororoba checkout whose de_marrais CSVs are compared")
    parser.add_argument("--record", type=Path, default=RECORD, help="retained record the self-test mutates")
    args = parser.parse_args()
    if args.self_test:
        return self_test(args.record)
    if args.write:
        require(args.open_gororoba is not None, "--write needs --open-gororoba DIR")
        record = build(args.open_gororoba, None)
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(canonical(record), encoding="utf-8")
        print(f"wrote {args.write}")
        return 0
    text = args.check.read_text(encoding="utf-8")
    check_text(text, lambda retained: build(args.open_gororoba, retained))
    k = json.loads(text)
    print(
        f"box-kite census: {len(k['assessors'])} assessors, {len(k['kites'])} kites, "
        f"{k['edge_totals']['same']}/{k['edge_totals']['opposite']} same/opposite edges, "
        f"{len(k['design_b']['within_kite'])} Design B rows; byte-identical"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
