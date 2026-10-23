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

SCHEMA = "cd-star-lattice-census-v1"
CATALOGUE = ROOT / "docs/evidence/quantum_inspire/catalogue.json"
RECORD = ROOT / "docs/evidence/cd-star-lattice/census.json"
TUNA17_TYPE_ID = 7
CD_DIMENSIONS = (2, 4, 8, 16)
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


def stabilizer(n: int, boundary: set[Point]) -> list[SignedPermutation]:
    """Signed permutations of the axes that map the boundary arcs onto themselves, by backtracking over axes."""
    arcs = boundary_arcs(boundary)
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

    extend([], set())
    return found


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
    for n in CD_DIMENSIONS:
        boundary = cd_boundary(n)
        facts, group = dimension_facts(n, boundary, search_codes=n == 2)
        facts["left_unit_closure"] = left_unit_closure(n, boundary)
        if n == 16:
            facts["sedenion_zero_divisors"] = sedenion_facts(boundary, group)
        record["cayley_dickson"].append(facts)
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
