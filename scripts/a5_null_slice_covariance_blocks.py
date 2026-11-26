"""Covariance algebras of the A_5 and A_6 null slices by XOR-block decomposition, and their G_2 identifications.

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
- on the octonion-space slices of A_6 and A_7 (time 104) (space 1..7, time 56; the dense system has 32768 x 8220 entries) the covariant
  generators span 14 dimensions, all rotations, no boost;
- that space equals the derivation algebra of the octonions (G_2) in so(7), and the A_5 space equals the stabilizer
  of e_2 in G_2 restricted to the A_5 frame (su(3)).

Blocks run through parallel.ordered_map. No random draw enters.
"""

from __future__ import annotations

import argparse
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


def block_constraints(task: tuple[str, int, tuple[int, int] | None]) -> list[list[int]]:
    """Constraint rows on the generator coefficients from the left kernel of block e; flip negates one sign s(a, c)
    of the equations (self-test only)."""
    name, e, flip = task
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


def constraints(name: str, flip: tuple[int, int] | None = None) -> list[list[int]]:
    dimension = SLICES[name][0]
    blocks = parallel.ordered_map(block_constraints, [(name, e, flip) for e in range(dimension)], min_items=1)
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("self-test: 3 paired controls pass")
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
