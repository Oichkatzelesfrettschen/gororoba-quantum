"""Covariance algebras of the A_5 null slice and of the octonion-space slices by XOR blocks and by cosets.

For a slice with frame F = (space..., tau) of the Cayley-Dickson algebra of dimension D, the covariance system asks for
matrices X, Y and a generator w of so(|F| - 1, 1) with X L_y + L_y Y = L_(w y) for every y in the span of F. With
L_a e_c = s(a, c) e_(a ^ c), the equation at (a, r, c) involves X[r, a ^ c] and Y[a ^ r, c], whose row-column XOR is
e = r ^ c ^ a, so the X and Y unknowns split into D blocks of 2D (one per e) with |F| D equations each; the generator
coefficients couple the blocks. Each block's left kernel turns into linear constraints on the generators, and the
covariant generators are the common solutions: dimension = generators - rank(constraints). The constraints do not
depend on which generators are admitted, so the rotation and boost subsystems take column subsets.

This record checks, exactly over Q:

- calibration: on the A_5 slice (space 1, 3, 4, 5, 6, 7; time 26) the method returns 8, 8, 0 for all generators,
  rotations and boosts, the values the dense 7168-row system of a5-null-slice-boost-algebra records (A5-615);
- on the octonion-space slices of A_6 (space 1..7, time 56; the dense system has 32768 x 8220 entries) and of A_7
  (time 104) and A_8 (time 200) the covariant generators span 14 dimensions, all rotations, no boost;
- that space equals the derivation algebra of the octonions (G_2) in so(7), and the A_5 space equals the stabilizer
  of e_2 in G_2 restricted to the A_5 frame (su(3));
- on V = span(e_0..e_7, e_(tau ^ 0)..e_(tau ^ 7)), invariant under the eight frame tables, the restricted system
  admits all 21 rotations and no boost, and its tables are the same at every level n = 6 to 12, so no level n >= 6
  admits a boost;
- the covariance algebra is the intersection over the cosets c ^ G of G = {0..7} u (tau ^ {0..7}); at n = 6 to 10
  the intersection is 14-dimensional, all rotations, and the cosets carry 7 sign types, the same set from n = 7 on;
- the four cosets with c in {0, 8, Q, Q + 8} have the same tables at every n = 6 to 12, and their intersection is 14,
  which with the README argument gives G_2 for every n >= 6; the signs s_n(alpha Q + u, beta Q + v), alpha and beta in
  0..3, u and v below 16, which cover the frame rows and every anchor-coset index, agree at n = 6 to 12.

Blocks run through parallel.ordered_map. No random draw enters.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Any

from flint import fmpq_mat, fmpz_mat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

from a5_null_slice_associator_envelope import sign_rows  # noqa: E402

import parallel  # noqa: E402

SLICES: dict[str, tuple[int, tuple[int, ...], int]] = {
    "A5": (32, (1, 3, 4, 5, 6, 7), 26),
    "A6": (64, (1, 2, 3, 4, 5, 6, 7), 56),
    "A7": (128, (1, 2, 3, 4, 5, 6, 7), 104),
    "A8": (256, (1, 2, 3, 4, 5, 6, 7), 200),
}
OCTONION = 8


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def generators(frame: tuple[int, ...]) -> list[tuple[int, int, bool]]:
    """(a, b, boost) for frame positions a < b; boost when position b is the time index (the last)."""
    return [(a, b, b == len(frame) - 1) for a, b in combinations(range(len(frame)), 2)]


def generator_weight(generator: tuple[int, int, bool], other: int, position: int) -> int:
    """Entry (other, position) of the generator matrix: E_ab - E_ba for a rotation, E_ab + E_ba for a boost."""
    a, b, boost = generator
    if (other, position) == (a, b):
        return 1
    if (other, position) == (b, a):
        return 1 if boost else -1
    return 0


def block_constraints(task: tuple[str, int, tuple[int, int] | None, bool]) -> list[list[int]]:
    """Constraint rows on the generator coefficients from the left kernel of block e; flip negates one sign s(a, c)
    of the equations (self-test only); tied imposes Y = -X, the derivation-type system X L_y - L_y X = L_(w y)."""
    name, e, flip, tied = task
    dimension, space, tau = SLICES[name]
    frame = (*space, tau)
    gens = generators(frame)
    signs = sign_rows(dimension, list(range(dimension)))

    def sign(p: int, q: int) -> int:
        value = int(signs[p, q])
        return -value if flip == (p, q) else value

    plain: list[list[int]] = []
    coupled: list[list[int]] = []
    for position, a in enumerate(frame):
        for r in range(dimension):
            c = r ^ e ^ a
            row = [0] * (2 * dimension)
            row[r] += sign(a, c)
            if tied:
                row[a ^ r] -= sign(a, a ^ r)
            else:
                row[dimension + (a ^ r)] += sign(a, a ^ r)
            plain.append(row)
            image = []
            for generator in gens:
                total = 0
                for other, b in enumerate(frame):
                    weight = generator_weight(generator, other, position)
                    if weight and r ^ c == b:
                        total += weight * sign(b, c)
                image.append(-total)
            coupled.append(image)
    kernel, nullity = fmpz_mat(plain).transpose().nullspace()
    rows = []
    for j in range(nullity):
        vector = [int(kernel[i, j]) for i in range(len(plain))]
        constraint = [sum(v * coupled[i][g] for i, v in enumerate(vector) if v) for g in range(len(gens))]
        if any(constraint):
            rows.append(constraint)
    return rows


def constraints(name: str, flip: tuple[int, int] | None = None, *, tied: bool = False) -> list[list[int]]:
    dimension = SLICES[name][0]
    tasks = [(name, e, flip, tied) for e in range(dimension)]
    blocks = parallel.ordered_map(block_constraints, tasks, min_items=1)
    return [row for block in blocks for row in block]


def solution_space(rows: list[list[int]], columns: list[int]) -> list[list[int]]:
    """Basis of {w supported on columns : rows w = 0}, as full-length integer vectors."""
    size = len(rows[0])
    restricted = fmpz_mat([[row[g] for g in columns] for row in rows])
    kernel, nullity = restricted.nullspace()
    basis = []
    for j in range(nullity):
        vector = [0] * size
        for i, g in enumerate(columns):
            vector[g] = int(kernel[i, j])
        basis.append(vector)
    return basis


def rank(vectors: list[list[int]]) -> int:
    return int(fmpq_mat(vectors).rank()) if vectors else 0


def octonion_derivations(*, mutate: bool = False) -> list[list[int]]:
    """Derivations of the octonions as antisymmetric 7 x 7 matrices on e_1..e_7, coordinates (a, b), a < b, from
    D(e_i e_j) = D(e_i) e_j + e_i D(e_j); mutate negates one structure constant (self-test only)."""
    signs = sign_rows(OCTONION, list(range(OCTONION)))

    def s(p: int, q: int) -> int:
        value = int(signs[p, q])
        return -value if mutate and (p, q) == (1, 2) else value

    pairs = list(combinations(range(1, OCTONION), 2))
    index = {pair: k for k, pair in enumerate(pairs)}

    def column(target: int, source: int) -> tuple[int, int] | None:
        """D[target][source] in pair coordinates: +coordinate for target < source, -coordinate otherwise."""
        if target == source or 0 in (target, source):
            return None
        return (index[(min(target, source), max(target, source))], 1 if target < source else -1)

    equations = []
    for i in range(1, OCTONION):
        for j in range(1, OCTONION):
            if i == j:
                continue
            product = i ^ j
            for out in range(OCTONION):
                row = [0] * len(pairs)
                entry = column(out, product)
                if entry:
                    row[entry[0]] += s(i, j) * entry[1]
                for k in range(1, OCTONION):
                    left = column(k, i)
                    if left and k ^ j == out:
                        row[left[0]] -= left[1] * s(k, j)
                    right = column(k, j)
                    if right and i ^ k == out:
                        row[right[0]] -= right[1] * s(i, k)
                if any(row):
                    equations.append(row)
    kernel, nullity = fmpz_mat(equations).nullspace()
    return [[int(kernel[i, j]) for i in range(len(pairs))] for j in range(nullity)]


def frame_coordinates(name: str, derivation: list[int]) -> list[int]:
    """A derivation in so(7) pair coordinates, written in the generator coordinates of the slice frame."""
    _dimension, space, _tau = SLICES[name]
    pairs = list(combinations(range(1, OCTONION), 2))
    value = dict(zip(pairs, derivation, strict=True))
    out = []
    for a, b, boost in generators((*space, _tau)):
        out.append(0 if boost else value.get((space[a], space[b]), 0))
    return out


def stabilizer(derivations: list[list[int]], unit: int) -> list[list[int]]:
    """Derivations D with D e_unit = 0, from the 6 conditions D[k][unit] = 0."""
    pairs = list(combinations(range(1, OCTONION), 2))
    conditions = []
    for k in range(1, OCTONION):
        if k != unit:
            pair = (min(k, unit), max(k, unit))
            conditions.append([d[pairs.index(pair)] for d in derivations])
    kernel, nullity = fmpz_mat(conditions).nullspace()
    return [
        [sum(int(kernel[i, j]) * derivations[i][c] for i in range(len(derivations))) for c in range(len(pairs))]
        for j in range(nullity)
    ]


def slice_result(name: str) -> dict[str, Any]:
    rows = constraints(name)
    gens = generators((*SLICES[name][1], SLICES[name][2]))
    rotations = [g for g, (_a, _b, boost) in enumerate(gens) if not boost]
    boosts = [g for g, (_a, _b, boost) in enumerate(gens) if boost]
    every = solution_space(rows, list(range(len(gens))))
    return {
        "generators": len(gens),
        "constraint_rows": len(rows),
        "constraint_rank": rank(rows),
        "all": len(every),
        "rotations": len(solution_space(rows, rotations)),
        "boosts": len(solution_space(rows, boosts)),
        "basis": every,
    }


def tied_dimension(name: str) -> int:
    """Covariant dimension of the derivation-type system X L_y - L_y X = L_(w y) (Y = -X)."""
    rows = constraints(name, tied=True)
    count = len(generators((*SLICES[name][1], SLICES[name][2])))
    return count - rank(rows) if rows else count


RESTRICTED_LEVELS: tuple[int, ...] = tuple(range(6, 13))


def octonion_slice_time(level: int) -> int:
    return (1 << (level - 1)) + (1 << (level - 2)) + 8


def restricted_tables(level: int) -> list[list[list[int]]]:
    """The eight frame tables L_a (a = 1..7, tau) on V = span(e_0..e_7, e_(tau ^ 0)..e_(tau ^ 7)), local index j or
    8 + j."""
    tau = octonion_slice_time(level)
    dimension = 1 << level
    local = [*range(8), *(tau ^ j for j in range(8))]
    position = {index: i for i, index in enumerate(local)}
    signs = sign_rows(dimension, [*range(1, 8), tau])
    out = []
    for row, a in enumerate([*range(1, 8), tau]):
        matrix = [[0] * 16 for _ in range(16)]
        for c in local:
            matrix[position[a ^ c]][position[c]] = int(signs[row, c])
        out.append(matrix)
    return out


def restricted_covariance(tables: list[list[list[int]]]) -> dict[str, int]:
    """Covariant dimensions of X L_y + L_y Y = L_(w y) on the 16-dimensional V: all generators, rotations, boosts."""
    size = 16
    frame_size = len(tables)
    gens = generators(tuple(range(frame_size)))
    rows = []
    for position, table in enumerate(tables):
        for r in range(size):
            for c in range(size):
                row = [0] * (2 * size * size + len(gens))
                for k in range(size):
                    if table[k][c]:
                        row[r * size + k] += table[k][c]
                    if table[r][k]:
                        row[size * size + k * size + c] += table[r][k]
                for g, generator in enumerate(gens):
                    row[2 * size * size + g] = -sum(
                        generator_weight(generator, other, position) * tables[other][r][c]
                        for other in range(frame_size)
                    )
                rows.append(row)
    plain = 2 * size * size
    rank_plain = rank([row[:plain] for row in rows])

    def dimension(columns: list[int]) -> int:
        chosen = [row[:plain] + [row[plain + g] for g in columns] for row in rows]
        return (plain + len(columns) - rank(chosen)) - (plain - rank_plain)

    rotations = [g for g, (_a, _b, boost) in enumerate(gens) if not boost]
    boosts = [g for g, (_a, _b, boost) in enumerate(gens) if boost]
    return {"all": dimension(list(range(len(gens)))), "rotations": dimension(rotations), "boosts": dimension(boosts)}


COSET_LEVELS: tuple[int, ...] = tuple(range(6, 11))


def coset_tables(level: int, representatives: tuple[int, ...] | None = None) -> dict[Any, list[list[list[int]]]]:
    """Distinct local sign tables of the cosets c ^ G of G = {0..7} u (tau ^ {0..7}) under the eight frame tables,
    keyed by the tables themselves; representatives restricts to the cosets of the named c."""
    tau = octonion_slice_time(level)
    dimension = 1 << level
    group = [*range(8), *(tau ^ j for j in range(8))]
    frame = [*range(1, 8), tau]
    signs = sign_rows(dimension, frame)
    seen: set[int] = set()
    types: dict[Any, list[list[list[int]]]] = {}
    for c in range(dimension) if representatives is None else representatives:
        if c in seen:
            continue
        members = [c ^ g for g in group]
        seen.update(members)
        position = {m: i for i, m in enumerate(members)}
        tables = []
        for row, a in enumerate(frame):
            matrix = [[0] * 16 for _ in range(16)]
            for x in members:
                matrix[position[a ^ x]][position[x]] = int(signs[row, x])
            tables.append(matrix)
        types.setdefault(tuple(tuple(tuple(r) for r in m) for m in tables), tables)
    return types


def anchor_representatives(level: int) -> tuple[int, ...]:
    """c in {0, 8, Q, Q + 8}, Q = 2^(level-2): four cosets present at every level >= 6."""
    q = 1 << (level - 2)
    return (0, 8, q, q + 8)


def intersection(rows: list[list[int]]) -> dict[str, int]:
    gens = generators(tuple(range(8)))
    rotations = [g for g, (_a, _b, boost) in enumerate(gens) if not boost]
    boosts = [g for g, (_a, _b, boost) in enumerate(gens) if boost]
    return {
        "all": len(solution_space(rows, list(range(len(gens))))),
        "rotations": len(solution_space(rows, rotations)),
        "boosts": len(solution_space(rows, boosts)),
    }


def block_sign_table(level: int) -> list[list[int]]:
    """s_level(alpha Q + u, beta Q + v) for alpha, beta in 0..3 and u, v < 16, Q = 2^(level-2): every frame row and
    every index of the four anchor cosets has this form."""
    q = 1 << (level - 2)
    indices = [alpha * q + u for alpha in range(4) for u in range(16)]
    signs = sign_rows(1 << level, indices)
    return [[int(signs[i, beta * q + v]) for beta in range(4) for v in range(16)] for i in range(len(indices))]


def coset_section() -> dict[str, Any]:
    """Coset decompositions of levels 6 to 10 and the anchor cosets, with every distinct type's constraints computed
    once through one flat pool."""
    per_level = {level: coset_tables(level) for level in COSET_LEVELS}
    anchors = coset_tables(6, anchor_representatives(6))
    unique: dict[Any, list[list[list[int]]]] = {}
    for types in (*per_level.values(), anchors):
        unique.update(types)
    keys = list(unique)
    solved = parallel.ordered_map(table_constraints, [unique[k] for k in keys], min_items=1)
    constraint_rows = dict(zip(keys, solved, strict=True))
    cosets = []
    for level, types in per_level.items():
        rows = [row for key in types for row in constraint_rows[key]]
        cosets.append(
            {
                "level": level,
                "cosets": (1 << level) // 16,
                "types": len(types),
                "type_keys": sorted(hash_key(key) for key in types),
                **intersection(rows),
            }
        )
    anchor_rows = [row for key in anchors for row in constraint_rows[key]]
    reference = coset_tables(6, anchor_representatives(6))
    return {
        "cosets": cosets,
        "anchor_cosets": {
            "intersection_at_level_6": intersection(anchor_rows),
            "tables_equal_to_level_6": [
                level
                for level in RESTRICTED_LEVELS
                if list(coset_tables(level, anchor_representatives(level))) == list(reference)
            ],
        },
        "block_signs_equal_to_level_6": [
            level for level in RESTRICTED_LEVELS if block_sign_table(level) == block_sign_table(6)
        ],
    }


def hash_key(key: Any) -> str:
    return hashlib.sha256(repr(key).encode()).hexdigest()[:16]


def table_constraints(tables: list[list[list[int]]]) -> list[list[int]]:
    """Constraint rows on the generators from the left kernel of the 16-dimensional system of one coset."""
    size = 16
    gens = generators(tuple(range(len(tables))))
    plain = []
    coupled = []
    for position, table in enumerate(tables):
        for r in range(size):
            for c in range(size):
                row = [0] * (2 * size * size)
                for k in range(size):
                    if table[k][c]:
                        row[r * size + k] += table[k][c]
                    if table[r][k]:
                        row[size * size + k * size + c] += table[r][k]
                plain.append(row)
                coupled.append(
                    [
                        -sum(generator_weight(g, other, position) * tables[other][r][c] for other in range(len(tables)))
                        for g in gens
                    ]
                )
    kernel, nullity = fmpz_mat(plain).transpose().nullspace()
    out = []
    for j in range(nullity):
        vector = [int(kernel[i, j]) for i in range(len(plain))]
        constraint = [sum(v * coupled[i][g] for i, v in enumerate(vector) if v) for g in range(len(gens))]
        if any(constraint):
            out.append(constraint)
    return out


def identification(name: str, basis: list[list[int]], reference: list[list[int]]) -> dict[str, int]:
    mapped = [frame_coordinates(name, d) for d in reference]
    return {"covariant": rank(basis), "reference": rank(mapped), "union": rank(basis + mapped)}


def compute() -> dict[str, Any]:
    slices = {name: slice_result(name) for name in SLICES}
    derivations = octonion_derivations()
    return {
        "schema": "a5-null-slice-covariance-blocks/1",
        "slices": {name: {k: v for k, v in row.items() if k != "basis"} for name, row in slices.items()},
        "octonion_derivations": len(derivations),
        "a6_against_g2": identification("A6", slices["A6"]["basis"], derivations),
        "a7_against_g2": identification("A7", slices["A7"]["basis"], derivations),
        "a8_against_g2": identification("A8", slices["A8"]["basis"], derivations),
        "derivation_type": {name: tied_dimension(name) for name in ("A6", "A7", "A8")},
        "restricted": {
            "covariance": restricted_covariance(restricted_tables(6)),
            "tables_equal_to_level_6": [
                level for level in RESTRICTED_LEVELS if restricted_tables(level) == restricted_tables(6)
            ],
        },
        **coset_section(),
        "a5_against_e2_stabilizer": identification("A5", slices["A5"]["basis"], stabilizer(derivations, 2)),
    }


def validate(result: dict[str, Any]) -> None:
    a5, a6 = result["slices"]["A5"], result["slices"]["A6"]
    require((a5["generators"], a5["all"], a5["rotations"], a5["boosts"]) == (21, 8, 8, 0), f"A5 calibration {a5}")
    require((a6["generators"], a6["all"], a6["rotations"], a6["boosts"]) == (28, 14, 14, 0), f"A6 covariance {a6}")
    a7 = result["slices"]["A7"]
    require((a7["generators"], a7["all"], a7["rotations"], a7["boosts"]) == (28, 14, 14, 0), f"A7 covariance {a7}")
    require((a5["constraint_rows"], a5["constraint_rank"]) == (344, 13), f"A5 constraints {a5}")
    require((a6["constraint_rows"], a6["constraint_rank"]) == (652, 14), f"A6 constraints {a6}")
    require(result["a7_against_g2"] == {"covariant": 14, "reference": 14, "union": 14}, "A7 space is not G_2")
    a8 = result["slices"]["A8"]
    require((a8["generators"], a8["all"], a8["rotations"], a8["boosts"]) == (28, 14, 14, 0), f"A8 covariance {a8}")
    require(result["a8_against_g2"] == {"covariant": 14, "reference": 14, "union": 14}, "A8 space is not G_2")
    for name, counts in (("A7", (1100, 14)), ("A8", (1996, 14))):
        row = result["slices"][name]
        require((row["constraint_rows"], row["constraint_rank"]) == counts, f"{name} constraints {row}")
    restricted = result["restricted"]
    require(restricted["covariance"] == {"all": 21, "rotations": 21, "boosts": 0}, f"restricted {restricted}")
    cosets = result["cosets"]
    require([row["level"] for row in cosets] == list(COSET_LEVELS), "coset levels")
    for row in cosets:
        require((row["all"], row["rotations"], row["boosts"]) == (14, 14, 0), f"coset intersection {row}")
    require([row["types"] for row in cosets] == [4, 7, 7, 7, 7], "coset type counts")
    require(all(row["type_keys"] == cosets[1]["type_keys"] for row in cosets[1:]), "coset types change after n = 7")
    anchor = result["anchor_cosets"]
    require(anchor["intersection_at_level_6"] == {"all": 14, "rotations": 14, "boosts": 0}, f"anchor cosets {anchor}")
    require(anchor["tables_equal_to_level_6"] == list(RESTRICTED_LEVELS), "anchor coset tables depend on the level")
    require(restricted["tables_equal_to_level_6"] == list(RESTRICTED_LEVELS), "restricted tables depend on the level")
    require(result["block_signs_equal_to_level_6"] == list(RESTRICTED_LEVELS), "block signs depend on the level")
    expected_tied = {"A6": 14, "A7": 14, "A8": 14}
    require(result["derivation_type"] == expected_tied, f"derivation-type system {result['derivation_type']}")
    require(result["octonion_derivations"] == 14, "octonion derivations")
    require(result["a6_against_g2"] == {"covariant": 14, "reference": 14, "union": 14}, "A6 space is not G_2")
    require(result["a5_against_e2_stabilizer"] == {"covariant": 8, "reference": 8, "union": 8}, "A5 space is not su(3)")


def self_test() -> None:
    def control(baseline: bool, mutant: bool, name: str) -> None:
        require(baseline and not mutant, f"control {name}: baseline {baseline}, mutant {mutant}")

    gens = generators((*SLICES["A5"][1], SLICES["A5"][2]))
    rotations = [g for g, (_a, _b, boost) in enumerate(gens) if not boost]
    baseline = len(solution_space(constraints("A5"), rotations))
    mutant = len(solution_space(constraints("A5", flip=(1, 2)), rotations))
    control(baseline == 8, mutant == 8, "block signs")
    derivations = octonion_derivations()
    control(len(derivations) == 14, len(octonion_derivations(mutate=True)) == 14, "Leibniz system")
    basis = slice_result("A5")["basis"]
    e2 = identification("A5", basis, stabilizer(derivations, 2))
    e3 = identification("A5", basis, stabilizer(derivations, 3))
    control(e2["union"] == e2["covariant"] == 8, e3["union"] == e3["covariant"], "stabilized unit")
    anchors = coset_tables(6, anchor_representatives(6))
    zero = coset_tables(6, (0,))
    four = intersection([row for tables in anchors.values() for row in table_constraints(tables)])
    one = intersection([row for tables in zero.values() for row in table_constraints(tables)])
    control(four["all"] == 14, one["all"] == 14, "anchor cosets against V alone")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("self-test: 4 paired controls pass")
        return 0
    result = compute()
    validate(result)
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
        return 0
    if args.check.read_text(encoding="utf-8") != text:
        print("record differs from its recomputation", file=sys.stderr)
        return 1
    print("record matches its recomputation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
