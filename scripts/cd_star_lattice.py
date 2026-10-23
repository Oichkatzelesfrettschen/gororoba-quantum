"""Census of the Cayley-Dickson star lattices: Tuna-17's coupling graph and its lifts to dimensions 3, 4, 8 and 16.

The lattice S_n holds the points of Z^n within taxicab distance 2 of the
origin together with a boundary set B_n of 2n(n-1) points at distance 3, one
on each edge of the cross-polytope |x|_1 = 2. Unit-distance pairs are the
edges. In a Cayley-Dickson algebra of dimension n, B_n is

    { u (1 + 2 w) : u = +-e_a, w = +e_b, b >= 1 },

and each element is s e_a + 2 s cd_sign(n, a, b) e_{a XOR b}, so
cd_core.cd_sign is the only multiplication table. Dimension 3 carries no
Cayley-Dickson algebra; its boundary is the orbit of (1, 2, 0) under the
rotation group of the tetrahedron, and every one-per-edge boundary of the
octahedron is enumerated beside it.

For each dimension the census records point, edge, degree and parity counts;
the one-boundary-point-per-edge property; the subgroup of signed permutation
matrices that maps B_n onto itself, with its determinant split, element-order
profile, stabilizer of e_0 and whether it holds -1; closure of B_n under left
multiplication by the 2n signed basis units; and the check-type classes a CSS
code reading each odd site's full neighborhood would need: two odd sites whose
neighborhoods meet in an odd count must carry one Pauli type, and the classes
are the connected components of that relation. In dimension 2 the lattice
maps onto the Tuna-17 couplers of docs/evidence/quantum_inspire/catalogue.json
through QUBIT_COORDINATES. In dimension 16 the census binds the sedenion
two-blade zero divisors of cd_core.sedenion_zero_divisor_corpus to the
lattice and certifies every unit and boundary point invertible through
cd_core.left_mult_determinant_exact.

The identification block certifies the groups without an external algebra
system. The boundary is the signed support of the arc matrix W, right
multiplication by e_1 + ... + e_{n-1}, and W is checked to be a skew
conference matrix through dimension 128; the left and right multiplications by
the imaginary sum are checked against the doubling block recurrence that
proves the conference property in every dimension. In dimensions 4 and 8 W is
signed-permutation equivalent to the Paley matrix of q = 3, 7; read through
that equivalence each symmetry permutes the projective line over F_q by a map
of PSL(2, q), and a lift of those maps to SL(2, q) that is a bijective
homomorphism certifies the isomorphism. In dimension 16 the group permutes the
eight doubling pairs {a, a + 8} through PGL(2, 7) with kernel {+-1}, and its
derived subgroup lifts to SL(2, 7) the same way. The commutant of each group
and the e_0 stabilizer's agreement with the table's own permutation
automorphisms complete the record.

Usage: "$PYTHON" scripts/cd_star_lattice.py (--write PATH | --check PATH)
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from cd_core import cd_sign, left_mult_determinant_exact, sedenion_zero_divisor_corpus  # noqa: E402
from parallel import ordered_map  # noqa: E402

SCHEMA = "cd-star-lattice-census-v2"
CATALOGUE = ROOT / "docs/evidence/quantum_inspire/catalogue.json"
RECORD = ROOT / "docs/evidence/cd-star-lattice/census.json"
TUNA17_TYPE_ID = 7
CD_DIMENSIONS = (2, 4, 8, 16)
CONFERENCE_DIMENSIONS = (2, 4, 8, 16, 32, 64, 128)
# Dimensions whose arc matrix is the Paley matrix of the prime q = n - 1.
PALEY_PRIMES = {4: 3, 8: 7}
# Tuna-17 qubit -> lattice point of S_2: Q8 at the origin, the weight-4
# ancillas at distance 1, the boundary ancillas Q0, Q6, Q10, Q16 at the unit
# multiples of 1 + 2i.
QUBIT_COORDINATES: dict[int, tuple[int, ...]] = {
    0: (1, 2), 1: (0, 2), 2: (1, 1), 3: (2, 0), 4: (0, 1), 5: (1, 0), 6: (2, -1), 7: (-1, 1), 8: (0, 0),
    9: (1, -1), 10: (-2, 1), 11: (-1, 0), 12: (0, -1), 13: (-2, 0), 14: (-1, -1), 15: (0, -2), 16: (-1, -2),
}  # fmt: skip
# Logical-operator search depth for the CSS assignments of dimensions 2 and 3.
DISTANCE_SEARCH_WEIGHT = 3

Point = tuple[int, ...]
SignedUnit = tuple[int, int]
SignedPermutation = tuple[SignedUnit, ...]
Matrix = list[list[int]]
Mobius = tuple[int, int, int, int]


class CensusError(RuntimeError):
    """A recomputed fact disagrees with its closed form or with the retained record."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CensusError(message)


def point(n: int, terms: Iterable[tuple[int, int]]) -> Point:
    coordinates = [0] * n
    for coefficient, axis in terms:
        coordinates[axis] += coefficient
    return tuple(coordinates)


def ball(n: int) -> set[Point]:
    """Points of Z^n with taxicab norm at most 2."""
    points = {point(n, [])}
    for a in range(n):
        for s in (1, -1):
            points.add(point(n, [(s, a)]))
            points.add(point(n, [(2 * s, a)]))
            for b in range(a + 1, n):
                for t in (1, -1):
                    points.add(point(n, [(s, a), (t, b)]))
    return points


def cd_boundary(n: int, flipped: frozenset[int] = frozenset()) -> set[Point]:
    """u (1 + 2 w) for u = +-e_a and w = +e_b; an index in `flipped` takes w = -e_b instead."""
    return {
        point(n, [(s, a), (2 * s * (-1 if b in flipped else 1) * cd_sign(n, a, b), a ^ b)])
        for a in range(n)
        for b in range(1, n)
        for s in (1, -1)
    }


def tetrahedral_boundary() -> set[Point]:
    """Orbit of (1, 2, 0) under cyclic coordinate shifts and sign flips of even count."""
    orbit: set[Point] = set()
    for a, b, c in ((1, 2, 0), (0, 1, 2), (2, 0, 1)):
        for sx, sy, sz in itertools.product((1, -1), repeat=3):
            if sx * sy * sz == 1:
                orbit.add((a * sx, b * sy, c * sz))
    return orbit


def unit_edges(points: set[Point]) -> list[tuple[Point, Point]]:
    edges = []
    for p in sorted(points):
        for axis in range(len(p)):
            q = p[:axis] + (p[axis] + 1,) + p[axis + 1 :]
            if q in points:
                edges.append((p, q))
    return edges


def neighbors(points: set[Point]) -> dict[Point, set[Point]]:
    table: dict[Point, set[Point]] = {p: set() for p in points}
    for p, q in unit_edges(points):
        table[p].add(q)
        table[q].add(p)
    return table


def boundary_arcs(boundary: set[Point]) -> set[tuple[SignedUnit, SignedUnit]]:
    """Each boundary point s e_a + 2 t e_c as the arc (a, s) -> (c, t) of the cross-polytope edge it sits on."""
    arcs = set()
    for p in boundary:
        support = [(axis, value) for axis, value in enumerate(p) if value]
        require(len(support) == 2, f"boundary point {p} has support {len(support)}")
        (i, ci), (j, cj) = support
        require(sorted((abs(ci), abs(cj))) == [1, 2], f"boundary point {p} is not of type (1, 2)")
        tail, head = ((i, ci), (j, cj // 2)) if abs(cj) == 2 else ((j, cj), (i, ci // 2))
        arcs.add((tail, head))
    return arcs


def one_per_edge(n: int, boundary: set[Point]) -> bool:
    """True when every edge {s e_a, t e_c} of the cross-polytope carries exactly one boundary point."""
    hits = Counter(frozenset((tail, head)) for tail, head in boundary_arcs(boundary))
    return len(hits) == 2 * n * (n - 1) and set(hits.values()) == {1} and len(boundary) == 2 * n * (n - 1)


def apply(g: SignedPermutation, unit: SignedUnit) -> SignedUnit:
    image, sign = g[unit[0]]
    return image, sign * unit[1]


def _stabilizer_branch(
    task: tuple[int, frozenset[tuple[SignedUnit, SignedUnit]], SignedUnit],
) -> list[SignedPermutation]:
    """The stabilizer elements that send axis 0 to the root image, by backtracking over the remaining axes."""
    n, arcs, root = task
    by_axes: dict[tuple[int, int], list[tuple[SignedUnit, SignedUnit]]] = {}
    for tail, head in arcs:
        by_axes.setdefault((max(tail[0], head[0]), min(tail[0], head[0])), []).append((tail, head))
    found: list[SignedPermutation] = []

    def extend(partial: list[SignedUnit], used: set[int]) -> None:
        axis = len(partial)
        if axis == n:
            found.append(tuple(partial))
            return
        for image in range(n):
            if image in used:
                continue
            for sign in (1, -1):
                partial.append((image, sign))
                g = tuple(partial)
                if all(
                    (apply(g, tail), apply(g, head)) in arcs
                    for other in range(axis)
                    for tail, head in by_axes.get((axis, other), [])
                ):
                    extend(partial, used | {image})
                partial.pop()

    extend([root], {root[0]})
    return found


def stabilizer(n: int, boundary: set[Point]) -> list[SignedPermutation]:
    """Signed permutations of the axes that map the boundary arcs onto themselves.

    Axis 0 carries no constraint of its own, so each of its 2n signed images roots an independent search;
    the roots run through ordered_map in the order image, then sign +1 before -1.
    """
    arcs = frozenset(boundary_arcs(boundary))
    roots = [(n, arcs, (image, sign)) for image in range(n) for sign in (1, -1)]
    return [g for branch in ordered_map(_stabilizer_branch, roots, min_items=1) for g in branch]


def compose(g: SignedPermutation, h: SignedPermutation) -> SignedPermutation:
    """g after h."""
    return tuple(apply(g, (h[axis][0], h[axis][1])) for axis in range(len(h)))


def determinant(g: SignedPermutation) -> int:
    sign = 1
    for _, s in g:
        sign *= s
    images = [image for image, _ in g]
    seen = set()
    for start in range(len(images)):
        length = 0
        axis = start
        while axis not in seen:
            seen.add(axis)
            axis = images[axis]
            length += 1
        if length and length % 2 == 0:
            sign = -sign
    return sign


def element_order(g: SignedPermutation) -> int:
    identity = tuple((axis, 1) for axis in range(len(g)))
    power, order = g, 1
    while power != identity:
        power = compose(g, power)
        order += 1
    return order


def group_facts(n: int, group: list[SignedPermutation]) -> dict[str, Any]:
    minus_one = tuple((axis, -1) for axis in range(n))
    determinants = Counter(determinant(g) for g in group)
    return {
        "order": len(group),
        "determinant_counts": {str(k): determinants[k] for k in sorted(determinants)},
        "reflection_free": determinants[-1] == 0,
        "element_order_profile": {str(k): v for k, v in sorted(Counter(element_order(g) for g in group).items())},
        "stabilizer_of_e0": sum(1 for g in group if g[0] == (0, 1)),
        "contains_minus_one": minus_one in group,
    }


def graph_facts(points: set[Point]) -> dict[str, Any]:
    edges = unit_edges(points)
    require(all((sum(p) - sum(q)) % 2 for p, q in edges), "an edge joins two sites of one parity")
    degree = Counter(len(v) for v in neighbors(points).values())
    return {
        "points": len(points),
        "edges": len(edges),
        "degree_counts": {str(k): degree[k] for k in sorted(degree)},
        "even_sites": sum(1 for p in points if sum(p) % 2 == 0),
        "odd_sites": sum(1 for p in points if sum(p) % 2),
        "bipartite_by_parity": True,
    }


def rank_gf2(rows: list[int]) -> int:
    basis: dict[int, int] = {}
    for row in rows:
        while row:
            top = row.bit_length() - 1
            if top not in basis:
                basis[top] = row
                break
            row ^= basis[top]
    return len(basis)


def min_logical_weight(checks: list[int], stabilizers: list[int], width: int, limit: int) -> int | None:
    """Least weight <= limit of a word commuting with `checks` and outside the span of `stabilizers`."""
    base = rank_gf2(stabilizers)
    for weight in range(1, limit + 1):
        for support in itertools.combinations(range(width), weight):
            word = sum(1 << q for q in support)
            if all(bin(word & c).count("1") % 2 == 0 for c in checks) and rank_gf2([*stabilizers, word]) > base:
                return weight
    return None


def check_type_facts(points: set[Point], search_codes: bool) -> dict[str, Any]:
    """Classes of odd sites forced to one Pauli type, and each two-type assignment's logical count and distance."""
    table = neighbors(points)
    data = sorted(p for p in points if sum(p) % 2 == 0)
    column = {p: index for index, p in enumerate(data)}
    odd = sorted(p for p in points if sum(p) % 2)
    masks = {a: sum(1 << column[q] for q in table[a]) for a in odd}
    parent = {a: a for a in odd}

    def root(a: Point) -> Point:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b in itertools.combinations(odd, 2):
        if bin(masks[a] & masks[b]).count("1") % 2:
            parent[root(a)] = root(b)
    classes: dict[Point, list[Point]] = {}
    for a in odd:
        classes.setdefault(root(a), []).append(a)
    ordered = sorted(classes.values(), key=lambda members: members[0])
    facts: dict[str, Any] = {"forced_type_classes": sorted(len(members) for members in ordered)}
    if not search_codes:
        return facts
    assignments = []
    for types in itertools.product("XZ", repeat=len(ordered)):
        if len(set(types)) < 2:
            continue
        x_rows = [masks[a] for members, t in zip(ordered, types, strict=True) if t == "X" for a in members]
        z_rows = [masks[a] for members, t in zip(ordered, types, strict=True) if t == "Z" for a in members]
        require(all(bin(x & z).count("1") % 2 == 0 for x in x_rows for z in z_rows), f"assignment {types} anticommutes")
        logical = len(data) - rank_gf2(x_rows) - rank_gf2(z_rows)
        distances = [
            min_logical_weight(z_rows, x_rows, len(data), DISTANCE_SEARCH_WEIGHT),
            min_logical_weight(x_rows, z_rows, len(data), DISTANCE_SEARCH_WEIGHT),
        ]
        found = [d for d in distances if d is not None]
        assignments.append(
            {
                "types": "".join(types),
                "x_checks": len(x_rows),
                "z_checks": len(z_rows),
                "logical_qubits": logical,
                "distance": min(found) if found else f">{DISTANCE_SEARCH_WEIGHT}",
            }
        )
    facts["data_qubits"] = len(data)
    facts["two_type_assignments"] = assignments
    return facts


def left_unit_closure(n: int, boundary: set[Point]) -> dict[str, int]:
    """Products u' p for the 2n signed basis units u' and every boundary point p that land back in the boundary."""
    stays = 0
    for a, s in itertools.product(range(n), (1, -1)):
        for p in boundary:
            product = [0] * n
            for q, coefficient in enumerate(p):
                if coefficient:
                    product[a ^ q] += s * coefficient * cd_sign(n, a, q)
            stays += tuple(product) in boundary
    return {"products": 2 * n * len(boundary), "in_boundary": stays}


def tuna17_binding() -> dict[str, Any]:
    """S_2 maps onto the catalogue's Tuna-17 couplers through QUBIT_COORDINATES."""
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    matches = [b for b in catalogue["backend_types"] if b.get("id") == TUNA17_TYPE_ID]
    require(len(matches) == 1 and matches[0].get("name") == "Tuna-17", "catalogue needs one Tuna-17 backend type")
    couplers = {tuple(sorted(edge)) for edge in matches[0]["topology"]}
    points = ball(2) | cd_boundary(2)
    require(set(QUBIT_COORDINATES.values()) == points, "QUBIT_COORDINATES does not cover S_2")
    qubit = {p: q for q, p in QUBIT_COORDINATES.items()}
    lattice = {tuple(sorted((qubit[p], qubit[q]))) for p, q in unit_edges(points)}
    require(lattice == couplers, f"S_2 edges differ from the catalogue: {sorted(lattice ^ couplers)}")
    mirror = {(x, -y) for x, y in points}
    return {
        "catalogue_couplers": len(couplers),
        "edge_sets_equal": True,
        "boundary_qubits": sorted(qubit[p] for p in cd_boundary(2)),
        "mirror_point_set_differs": mirror != points,
    }


def _selection_stabilizer(choice: tuple[int, ...]) -> tuple[int, bool, int]:
    """Stabilizer order, reflection-free flag and largest element order of one one-per-edge boundary."""
    edges = _octahedron_edges()
    boundary = set()
    for (u, v), pick in zip(edges, choice, strict=True):
        tail, head = (u, v) if pick else (v, u)
        boundary.add(point(3, [(tail[1], tail[0]), (2 * head[1], head[0])]))
    group = stabilizer(3, boundary)
    return len(group), all(determinant(g) == 1 for g in group), max(element_order(g) for g in group)


def _octahedron_edges() -> list[tuple[SignedUnit, SignedUnit]]:
    units = [(a, s) for a in range(3) for s in (1, -1)]
    return [(u, v) for u, v in itertools.combinations(units, 2) if u[0] != v[0]]


def octahedron_selections() -> dict[str, Any]:
    """Every one-per-edge boundary of the octahedron with its signed-permutation stabilizer."""
    choices = list(itertools.product((0, 1), repeat=len(_octahedron_edges())))
    results = ordered_map(_selection_stabilizer, choices)
    orders = Counter(order for order, _, _ in results)
    reflection_free = Counter(order for order, free, _ in results if free)
    # A reflection-free group of order 4 is cyclic exactly when it holds an element of order 4.
    free_shapes = Counter(f"{order}:{largest}" for order, free, largest in results if free)
    return {
        "selections": len(choices),
        "stabilizer_order_counts": {str(k): orders[k] for k in sorted(orders)},
        "reflection_free_stabilizer_order_counts": {str(k): reflection_free[k] for k in sorted(reflection_free)},
        "reflection_free_order_and_largest_element_order_counts": dict(sorted(free_shapes.items())),
    }


def _is_zero_divisor(p: Point) -> bool:
    return left_mult_determinant_exact(len(p), list(p)) == 0


def sedenion_facts(boundary: set[Point], group: list[SignedPermutation]) -> dict[str, Any]:
    n = 16
    corpus_points = set()
    for i, j, t, _, _, _ in sedenion_zero_divisor_corpus():
        for s in (1, -1):
            corpus_points.add(point(n, [(s, i), (s * t, j)]))
    two_blades = {p for p in ball(n) if sum(map(abs, p)) == 2 and max(map(abs, p)) == 1}
    units = {p for p in ball(n) if sum(map(abs, p)) == 1}
    require(corpus_points <= two_blades, "a corpus zero divisor lies outside the two-blade shell")
    probe = sorted(two_blades | units | boundary)
    singular = {p for p, zero in zip(probe, ordered_map(_is_zero_divisor, probe), strict=True) if zero}
    require(singular == corpus_points, "determinant zeros differ from the zero-divisor corpus")
    assessors = {frozenset(a for a, c in enumerate(p) if c) for p in corpus_points}
    orbit: set[frozenset[int]] = set()
    for g in group:
        for pair in assessors:
            orbit.add(frozenset(g[a][0] for a in pair))
    return {
        "two_blade_points": len(two_blades),
        "zero_divisor_points": len(corpus_points),
        "zero_divisors_with_e0": sum(1 for p in corpus_points if p[0]),
        "assessor_pairs": len(assessors),
        "unit_zero_divisors": len(singular & units),
        "boundary_zero_divisors": len(singular & boundary),
        "assessor_orbit_pairs": len(orbit),
        "assessor_orbit_extra_pairs": sorted(sorted(pair) for pair in orbit - assessors),
        "symmetry_preserves_zero_divisors": all(
            {tuple(_signed_image(g, p)) for p in corpus_points} == corpus_points for g in group
        ),
    }


def _signed_image(g: SignedPermutation, p: Point) -> list[int]:
    image = [0] * len(p)
    for axis, value in enumerate(p):
        target, sign = g[axis]
        image[target] = sign * value
    return image


def arc_matrix(n: int) -> Matrix:
    """W[a XOR b][a] = cd_sign(n, a, b), b >= 1: right multiplication by e_1 + ... + e_{n-1}; B_n is its signed support.

    A signed permutation maps the boundary arcs onto themselves exactly when it commutes with W, so the boundary group
    is the signed-permutation centralizer of W.
    """
    matrix = [[0] * n for _ in range(n)]
    for a in range(n):
        for b in range(1, n):
            matrix[a ^ b][a] = cd_sign(n, a, b)
    return matrix


def left_matrix(n: int) -> Matrix:
    """L[a XOR b][a] = cd_sign(n, b, a), b >= 1: left multiplication by e_1 + ... + e_{n-1}."""
    matrix = [[0] * n for _ in range(n)]
    for a in range(n):
        for b in range(1, n):
            matrix[a ^ b][a] = cd_sign(n, b, a)
    return matrix


def doubling_blocks(n: int) -> tuple[Matrix, Matrix]:
    """Right and left multiplication by s' = (s, 1 + s) in dimension 2n, assembled from L, R and conjugation C at n.

    The doubling (a, b)(c, d) = (ac - conj(d) b, da + b conj(c)) gives R' = [[R, L - I], [I + L, -R]] and
    L' = [[L, -(I + R) C], [(I + L) C, R]], the block recurrence of the conference-matrix induction in
    docs/notes/topics/cd-star-lattice-tower.md.
    """
    right, left = arc_matrix(n), left_matrix(n)
    conj = [1] + [-1] * (n - 1)
    eye = [[int(i == j) for j in range(n)] for i in range(n)]
    big_right = [[0] * (2 * n) for _ in range(2 * n)]
    big_left = [[0] * (2 * n) for _ in range(2 * n)]
    for i in range(n):
        for j in range(n):
            big_right[i][j] = right[i][j]
            big_right[i][n + j] = left[i][j] - eye[i][j]
            big_right[n + i][j] = eye[i][j] + left[i][j]
            big_right[n + i][n + j] = -right[i][j]
            big_left[i][j] = left[i][j]
            big_left[i][n + j] = -(eye[i][j] + right[i][j]) * conj[j]
            big_left[n + i][j] = (eye[i][j] + left[i][j]) * conj[j]
            big_left[n + i][n + j] = right[i][j]
    return big_right, big_left


def is_skew_conference(matrix: Matrix) -> bool:
    """Zero diagonal, W^T = -W and W^T W = (n - 1) I, so I + W is a skew Hadamard matrix."""
    n = len(matrix)
    columns = [[matrix[row][column] for row in range(n)] for column in range(n)]
    skew = all(matrix[i][j] == -matrix[j][i] for i in range(n) for j in range(n))
    gram = all(
        sum(x * y for x, y in zip(columns[a], columns[b], strict=True)) == (n - 1 if a == b else 0)
        for a in range(n)
        for b in range(a, n)
    )
    return skew and gram


def paley_matrix(q: int) -> Matrix:
    """Skew conference matrix of order q + 1 for a prime q = 3 mod 4, indexed by the projective line over F_q.

    Index 0 is infinity and index x + 1 is x; entry (x, y) is the quadratic character of y - x.
    """
    squares = {x * x % q for x in range(1, q)}
    matrix = [[0] * (q + 1) for _ in range(q + 1)]
    for x in range(q):
        matrix[0][x + 1] = 1
        matrix[x + 1][0] = -1
        for y in range(q):
            if (y - x) % q:
                matrix[x + 1][y + 1] = 1 if (y - x) % q in squares else -1
    return matrix


def signed_equivalences(source: Matrix, target: Matrix) -> list[SignedPermutation]:
    """Signed permutations i -> (t_i, s_i) with target[t_i][t_j] s_i s_j = source[i][j]: P source P^T = target."""
    n = len(source)
    found: list[SignedPermutation] = []

    def extend(partial: list[SignedUnit]) -> None:
        i = len(partial)
        if i == n:
            found.append(tuple(partial))
            return
        used = {t for t, _ in partial}
        for t in range(n):
            if t in used:
                continue
            for s in (1, -1):
                if all(target[t][tj] * s * sj == source[i][j] for j, (tj, sj) in enumerate(partial)):
                    partial.append((t, s))
                    extend(partial)
                    partial.pop()

    extend([])
    return found


def mobius_image(q: int, m: Mobius, p: int) -> int:
    """x -> (a x + b) / (c x + d) on the projective line, with 0 for infinity and x + 1 for x."""
    a, b, c, d = m
    numerator, denominator = (a, c) if p == 0 else ((a * (p - 1) + b) % q, (c * (p - 1) + d) % q)
    return 0 if denominator % q == 0 else numerator * pow(denominator, -1, q) % q + 1


def mobius_classes(q: int) -> dict[tuple[int, ...], bool]:
    """Every map of PGL(2, q) on the projective line, keyed by its image tuple; True when ad - bc is a square (PSL)."""
    squares = {x * x % q for x in range(1, q)}
    table: dict[tuple[int, ...], bool] = {}
    for a, b, c, d in itertools.product(range(q), repeat=4):
        m = (a, b, c, d)
        det = (a * d - b * c) % q
        if det:
            table[tuple(mobius_image(q, m, p) for p in range(q + 1))] = det in squares
    return table


def sl2_lifts(q: int) -> dict[tuple[int, ...], list[Mobius]]:
    """The two matrices +-M of SL(2, q) over each map of PSL(2, q)."""
    lifts: dict[tuple[int, ...], list[Mobius]] = {}
    for a, b, c, d in itertools.product(range(q), repeat=4):
        m = (a, b, c, d)
        if (a * d - b * c) % q == 1:
            lifts.setdefault(tuple(mobius_image(q, m, p) for p in range(q + 1)), []).append(m)
    return lifts


def matmul2(q: int, x: Mobius, y: Mobius) -> Mobius:
    return (
        (x[0] * y[0] + x[1] * y[2]) % q,
        (x[0] * y[1] + x[1] * y[3]) % q,
        (x[2] * y[0] + x[3] * y[2]) % q,
        (x[2] * y[1] + x[3] * y[3]) % q,
    )


def inverse(g: SignedPermutation) -> SignedPermutation:
    table: list[SignedUnit] = [(0, 1)] * len(g)
    for axis, (image, sign) in enumerate(g):
        table[image] = (axis, sign)
    return tuple(table)


def closure(generators: list[SignedPermutation], n: int) -> set[SignedPermutation]:
    identity = tuple((axis, 1) for axis in range(n))
    span, frontier = {identity}, [identity]
    while frontier:
        h = frontier.pop()
        for g in generators:
            x = compose(g, h)
            if x not in span:
                span.add(x)
                frontier.append(x)
    return span


def generating_set(group: list[SignedPermutation]) -> list[SignedPermutation]:
    """Greedy generators in list order: each one lies outside the span of those before it."""
    n = len(group[0])
    generators: list[SignedPermutation] = []
    span = closure([], n)
    for g in group:
        if g not in span:
            generators.append(g)
            span = closure(generators, n)
    return generators


def is_isomorphic_to_sl2(
    group: list[SignedPermutation], line: dict[SignedPermutation, tuple[int, ...]], q: int
) -> bool:
    """Search a homomorphism to SL(2, q) that lifts each element's projective-line map, and test it for bijectivity.

    Each generator takes one of the two lifts +-M of its line map; a choice is a homomorphism when the Cayley-graph
    walk assigns every element one matrix, and an isomorphism when the matrices are distinct and |group| = |SL(2, q)|.
    Every element's matrix must also lie over its own line map, so the certificate binds the recorded line action.
    """
    lifts = sl2_lifts(q)
    if len(group) != q * (q * q - 1) or any(line[g] not in lifts for g in group):
        return False
    generators = generating_set(group)
    identity = tuple((axis, 1) for axis in range(len(group[0])))
    for choice in itertools.product((0, 1), repeat=len(generators)):
        images = [lifts[line[g]][c] for g, c in zip(generators, choice, strict=True)]
        phi: dict[SignedPermutation, Mobius] = {identity: (1, 0, 0, 1)}
        frontier, consistent = [identity], True
        while frontier and consistent:
            h = frontier.pop()
            for g, m in zip(generators, images, strict=True):
                x, value = compose(g, h), matmul2(q, m, phi[h])
                if x not in phi:
                    phi[x] = value
                    frontier.append(x)
                elif phi[x] != value:
                    consistent = False
                    break
        if (
            consistent
            and len(phi) == len(group)
            and len(set(phi.values())) == len(group)
            and all(phi[g] in lifts[line[g]] for g in group)
        ):
            return True
    return False


def commutant_basis(n: int, group: list[SignedPermutation]) -> list[Matrix]:
    """Integer basis of the matrices commuting with every group element: the nonzero orbit sums of the units E_ij."""
    seen: set[tuple[int, int]] = set()
    basis: list[Matrix] = []
    for i, j in itertools.product(range(n), repeat=2):
        if (i, j) in seen:
            continue
        total: Counter[tuple[int, int]] = Counter()
        for g in group:
            (gi, si), (gj, sj) = g[i], g[j]
            total[(gi, gj)] += si * sj
        seen |= set(total)
        if any(total.values()):
            scale = max(abs(v) for v in total.values())
            matrix = [[0] * n for _ in range(n)]
            for (row, column), value in total.items():
                matrix[row][column] = value // scale
            basis.append(matrix)
    return basis


def matmul(x: Matrix, y: Matrix) -> Matrix:
    n = len(x)
    return [[sum(x[i][k] * y[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def scalar_value(matrix: Matrix) -> int | None:
    n = len(matrix)
    value = matrix[0][0]
    return value if all(matrix[i][j] == (value if i == j else 0) for i in range(n) for j in range(n)) else None


def commutant_facts(n: int, group: list[SignedPermutation]) -> dict[str, Any]:
    """The commutant's dimension and basis squares; in dimension 16 the quaternion relations it carries."""
    basis = commutant_basis(n, group)
    squares = [scalar_value(matmul(b, b)) for b in basis]
    values = [s for s in squares if s is not None]
    require(len(values) == len(basis), f"a commutant basis element of dimension {n} squares to a non-scalar")
    facts: dict[str, Any] = {"dimension": len(basis), "basis_squares": sorted(values)}
    if n == 16:
        right_e8 = [[0] * n for _ in range(n)]
        for a in range(n):
            right_e8[a ^ 8][a] = cd_sign(n, a, 8)
        negated = [[-v for v in row] for row in right_e8]
        sevens = [b for b, s in zip(basis, values, strict=True) if s == -7]
        facts["right_multiplication_by_e8_in_basis"] = right_e8 in basis or negated in basis
        facts["e8_anticommutes_with_square_minus_7"] = bool(sevens) and all(
            matmul(b, right_e8) == [[-v for v in row] for row in matmul(right_e8, b)] for b in sevens
        )
    return facts


def table_automorphisms(n: int) -> set[SignedPermutation]:
    """Unsigned XOR-linear index permutations that preserve cd_sign: the basis table's permutation automorphisms."""
    bits = n.bit_length() - 1
    sign = [[cd_sign(n, a, b) for b in range(n)] for a in range(n)]
    found: set[SignedPermutation] = set()
    for images in itertools.permutations(range(1, n), bits):
        f = [0] * n
        for x in range(1, n):
            f[x] = f[x & (x - 1)] ^ images[(x & -x).bit_length() - 1]
        if len(set(f)) == n and all(sign[f[a]][f[b]] == sign[a][b] for a in range(n) for b in range(n)):
            found.add(tuple((image, 1) for image in f))
    return found


def is_xor_linear(g: SignedPermutation) -> bool:
    n = len(g)
    return all(g[a ^ b][0] == g[a][0] ^ g[b][0] for a in range(n) for b in range(n))


def line_action(
    group: list[SignedPermutation], equivalence: SignedPermutation
) -> dict[SignedPermutation, tuple[int, ...]]:
    """Each element's permutation of the projective line, read through an equivalence that sends axis i to point t_i."""
    position = [t for t, _ in equivalence]
    line: dict[SignedPermutation, tuple[int, ...]] = {}
    for g in group:
        image = [0] * len(g)
        for axis, (target, _) in enumerate(g):
            image[position[axis]] = position[target]
        line[g] = tuple(image)
    return line


def paley_facts(n: int, q: int, group: list[SignedPermutation]) -> dict[str, Any]:
    """W_n against the Paley matrix of q = n - 1: equivalences, projective-line action and SL(2, q) certificate."""
    w, paley = arc_matrix(n), paley_matrix(q)
    equivalences = signed_equivalences(w, paley)
    require(bool(equivalences), f"the dimension-{n} arc matrix is not equivalent to the Paley matrix of q = {q}")
    classes = mobius_classes(q)
    line = line_action(group, equivalences[0])
    identity_line = tuple(range(n))
    return {
        "paley_prime": q,
        "equivalences_to_paley": len(equivalences),
        "paley_automorphisms": len(signed_equivalences(paley, paley)),
        "line_maps_in_psl2": all(classes.get(image) is True for image in line.values()),
        "line_action_kernel": sum(1 for image in line.values() if image == identity_line),
        "isomorphic_to_sl2_by_lift": is_isomorphic_to_sl2(group, line, q),
    }


def doubling_pair_labels(
    pair_image: dict[SignedPermutation, tuple[int, ...]], generators: list[SignedPermutation], q: int
) -> tuple[int, ...]:
    """First labeling of the doubling pairs by projective-line points that makes every generator a Moebius map."""
    classes = mobius_classes(q)
    for labels in itertools.permutations(range(q + 1)):
        position = {label: pair for pair, label in enumerate(labels)}
        if all(tuple(labels[pair_image[g][position[p]]] for p in range(q + 1)) in classes for g in generators):
            return labels
    raise CensusError(f"no labeling of the doubling pairs by the projective line over F_{q} makes the group Moebius")


def sedenion_identification(group: list[SignedPermutation]) -> dict[str, Any]:
    """G_16 on the eight doubling pairs {a, a + 8}: PGL(2, 7) image, kernel and derived subgroup SL(2, 7)."""
    n, q = 16, 7
    half = n // 2
    for g in group:
        require(all(g[a][0] % half == g[a + half][0] % half for a in range(half)), "an element splits a doubling pair")
    pair_image = {g: tuple(g[k][0] % half for k in range(half)) for g in group}
    generators = generating_set(group)
    labels = doubling_pair_labels(pair_image, generators, q)
    position = {label: pair for pair, label in enumerate(labels)}
    line = {g: tuple(labels[pair_image[g][position[p]]] for p in range(half)) for g in group}
    classes = mobius_classes(q)
    identity_line = tuple(range(half))
    commutators = [compose(compose(g, h), compose(inverse(g), inverse(h))) for g in group for h in generators]
    derived = sorted(closure(generating_set(list(dict.fromkeys(commutators))), n))
    psl_preimage = {g for g in group if classes.get(line[g]) is True}
    derived_orbits: list[list[int]] = []
    for a in range(n):
        if not any(a in orbit for orbit in derived_orbits):
            derived_orbits.append(sorted({g[a][0] for g in derived}))
    pair_orbits: list[int] = []
    covered: set[frozenset[int]] = set()
    for pair in itertools.combinations(range(n), 2):
        if frozenset(pair) not in covered:
            orbit = {frozenset(g[a][0] for a in pair) for g in group}
            covered |= orbit
            pair_orbits.append(len(orbit))
    return {
        "doubling_pair_maps_in_pgl2_7": all(image in classes for image in line.values()),
        "doubling_pair_image_order": len(set(line.values())),
        "doubling_pair_kernel": sum(1 for image in line.values() if image == identity_line),
        "derived_subgroup_order": len(derived),
        "derived_subgroup_is_psl2_7_preimage": set(derived) == psl_preimage,
        "derived_isomorphic_to_sl2_7_by_lift": is_isomorphic_to_sl2(derived, line, q),
        "derived_index_orbits": derived_orbits,
        "index_pair_orbit_sizes": sorted(pair_orbits),
    }


def identification_facts(groups: dict[int, list[SignedPermutation]]) -> dict[str, Any]:
    """Arc-matrix, Paley, commutant and table-automorphism facts that identify the boundary groups."""
    facts: dict[str, Any] = {
        "arc_matrix_skew_conference": {str(n): is_skew_conference(arc_matrix(n)) for n in CONFERENCE_DIMENSIONS},
        "doubling_blocks_match_cd_sign": {
            str(n): doubling_blocks(n // 2) == (arc_matrix(n), left_matrix(n)) for n in CONFERENCE_DIMENSIONS[1:]
        },
    }
    for n, group in groups.items():
        w = arc_matrix(n)
        require(
            all(w[g[i][0]][g[j][0]] * g[i][1] * g[j][1] == w[i][j] for g in group for i in range(n) for j in range(n)),
            f"a dimension-{n} boundary symmetry fails to commute with the arc matrix",
        )
    for n in (4, 8, 16):
        group = groups[n]
        stabilizer_of_e0 = {g for g in group if g[0] == (0, 1)}
        entry: dict[str, Any] = {
            "commutant": commutant_facts(n, group),
            "stabilizer_of_e0_equals_table_automorphisms": stabilizer_of_e0 == table_automorphisms(n),
            "xor_linear_elements": sum(1 for g in group if is_xor_linear(g)),
        }
        if n in PALEY_PRIMES:
            entry["paley"] = paley_facts(n, PALEY_PRIMES[n], group)
        else:
            entry["doubling_pairs"] = sedenion_identification(group)
        facts[str(n)] = entry
    return facts


def dimension_facts(n: int, boundary: set[Point], search_codes: bool) -> tuple[dict[str, Any], list[SignedPermutation]]:
    points = ball(n) | boundary
    require(len(points) == 4 * n * n + 1, f"S_{n} holds {len(points)} points, not 4n^2 + 1")
    group = stabilizer(n, boundary)
    facts = {
        "dimension": n,
        "graph": graph_facts(points),
        "boundary_points": len(boundary),
        "one_boundary_point_per_cross_polytope_edge": one_per_edge(n, boundary),
        "boundary_symmetry": group_facts(n, group),
        "check_types": check_type_facts(points, search_codes),
    }
    return facts, group


def build() -> dict[str, Any]:
    record: dict[str, Any] = {"schema": SCHEMA, "tuna17": tuna17_binding(), "cayley_dickson": []}
    groups: dict[int, list[SignedPermutation]] = {}
    for n in CD_DIMENSIONS:
        boundary = cd_boundary(n)
        facts, groups[n] = dimension_facts(n, boundary, search_codes=n == 2)
        facts["left_unit_closure"] = left_unit_closure(n, boundary)
        if n == 16:
            facts["sedenion_zero_divisors"] = sedenion_facts(boundary, groups[n])
        record["cayley_dickson"].append(facts)
    record["identification"] = identification_facts(groups)
    tetrahedral, _ = dimension_facts(3, tetrahedral_boundary(), search_codes=True)
    tetrahedral["octahedron_selections"] = octahedron_selections()
    record["tetrahedral_3d"] = tetrahedral
    return record


def canonical(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    args = parser.parse_args()
    text = canonical(build())
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(text, encoding="utf-8")
        print(f"wrote {args.write}")
        return 0
    retained = args.check.read_text(encoding="utf-8")
    require(retained == text, f"{args.check} differs from the recomputed census")
    print(f"cd star lattice census: dimensions 2, 3, {', '.join(map(str, CD_DIMENSIONS[1:]))}; byte-identical")
    return 0


if __name__ == "__main__":
    sys.exit(main())
