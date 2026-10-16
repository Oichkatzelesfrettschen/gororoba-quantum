"""Exact local-dimension certificates for the A_5 rank loci D_(5,k) at named witness points.

D_(5,k) is the set of unit x in A_5 with dim ker L_x = k (RANK_STRATUM_TOPOLOGY.md).
The cone over it is S_k = {x : rank L_x = 32 - k}, the preimage of the
manifold M_r of rank-r matrices under the linear map x -> L_x. At a point x
of S_k with V a basis of ker L_x and U a basis of ker L_x^T, the tangent
space of M_r at L_x is {M : U^T M V = 0}, so every curve of S_k through x
has its velocity in

    T(x) = {y in R^32 : U^T L_y V = 0}.

The tangent cone of S_k at x lies in T(x), and the local dimension of a
semialgebraic set equals that of its tangent cone, so dim_x S_k <= dim T(x).
x itself lies in T(x) and S_k is a cone, so D_(5,k) has local dimension at
most dim T(x) - 1 at x / |x|. The map y -> U^T L_y V is a 32 x k^2 rational
matrix; its rank modulo 2^61 - 1 bounds its rational rank from below, so
31 - rank_p is a valid upper bound.

The lower bounds come from smooth families through the witnesses, in the
bracket coordinates {a, b} = (a + b, e_8 (b - a)) of H_5^perp
(math/0702075, docs/notes/math-0702075.md). Theorem 1.5 fixes the nullity of
each family, and the unit zero divisors of A_4 form V_2(R^7), a manifold of
dimension 11 (Theorem 15.7 at n = 4), so their cone Z has dimension 12. A
family's dimension at unit norm is its cone dimension minus one:

  zd-axis              {a, 0}, a in Z                       nullity 16   12 - 1 = 11
  nonzd-axis           {a, 0}, a in C_4^perp outside Z      nullity 12   14 - 1 = 13
  zd-zd-locus          a, b in Z, b in V(a)                 nullity 12   16 + 1 = 17 (Theorem 7.5 plus the ratio)
  zd-zd-generic        a, b in Z off the D-locus            nullity  8   24 - 1 = 23
  zd-nonzd-locus       a in Z, b in the D-locus space W(a)  nullity  8   12 + dim W(a) - 1
  zd-nonzd-generic     a in Z, b outside Z off the locus    nullity  4   26 - 1 = 25
  nonzd-nonzd-locus    a, b outside Z, C-orthogonal         nullity  4   14 + 12 - 1 = 25

W(a) is the subspace of b in C_4^perp that are C-orthogonal to a and
orthogonal to Ann(a); its dimension is computed exactly at each witness. Each
row is a fiber bundle with linear fibers of constant dimension over a smooth
base, so the family is a manifold of the stated dimension through its
witness, inside D_(5,k) near it. Where the family dimension equals the
tangent bound, D_(5,k) has exactly that local dimension at the witness.
Points outside H_5^perp (Proposition 8.2's (i_4, e_p) and Moreno's
e_1 + e_10 + 2 e_24) carry the upper bound only.

Falsifier, stated before the run: a witness whose certified nullity differs
from its family's, or a family dimension above the tangent bound.

Usage:
    "$PYTHON" scripts/rank_locus_local_dimension.py --out PATH
    "$PYTHON" scripts/rank_locus_local_dimension.py --check PATH
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from math import lcm
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
from d_locus_nullity import (  # noqa: E402
    bracket,
    combination,
    combination_weights,
    frame_spaces,
    kernel,
    left_rational,
    zero_divisor,
)
from moreno_stiefel_nullity import PRIME, rank_mod, rational_kernel  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "rank-locus-local-dimension-v1"
DIM = 32
HALF = 16
I4 = 8
SEED = 5_120_032
FRAMES_PER_FAMILY = 3
ZD_CONE_DIMENSION = 12
C4_PERP_DIMENSION = 14
Vector = list[Fraction]


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"rank_locus_local_dimension: {message}")


def integer_matrix(rows: list[Vector]) -> list[list[int]]:
    scale = 1
    for row in rows:
        for value in row:
            scale = lcm(scale, Fraction(value).denominator)
    return [[int(Fraction(value) * scale) for value in row] for row in rows]


def transpose(rows: list[Vector]) -> list[Vector]:
    return [list(column) for column in zip(*rows, strict=True)]


def basis_vector(index: int, dim: int = DIM) -> Vector:
    return [Fraction(int(k == index)) for k in range(dim)]


def tangent_bound(x: Vector) -> dict[str, int]:
    """The nullity k of L_x and the upper bound 31 - rank_p(y -> U^T L_y V) on the local dimension."""
    left = left_rational(DIM, x)
    right_kernel = rational_kernel(integer_matrix(left))
    left_kernel = rational_kernel(integer_matrix(transpose(left)))
    _require(len(right_kernel) == len(left_kernel), "L_x and its transpose have different nullities")
    columns = []
    for index in range(DIM):
        unit = left_rational(DIM, basis_vector(index))
        images = [[sum((unit[r][c] * v[c] for c in range(DIM)), Fraction(0)) for r in range(DIM)] for v in right_kernel]
        columns.append(
            [sum((u[r] * image[r] for r in range(DIM)), Fraction(0)) for u in left_kernel for image in images]
        )
    rank = rank_mod(integer_matrix(columns), PRIME) if columns[0] else 0
    return {"nullity": len(right_kernel), "tangent_rank_mod_p": rank, "dimension_upper_bound": DIM - 1 - rank}


def c_orthogonal_space(a: Vector, annihilator: list[Vector]) -> list[Vector]:
    """A basis of W(a): b in C_4^perp with <b, a> = <b, e_8 a> = 0 and b orthogonal to Ann(a)."""
    i4a = [
        sum((row[c] * a[c] for c in range(HALF)), Fraction(0)) for row in left_rational(HALF, basis_vector(I4, HALF))
    ]
    constraints = [basis_vector(0, HALF), basis_vector(I4, HALF), a, i4a, *annihilator]
    return kernel(constraints)


def witnesses() -> list[dict[str, Any]]:
    """Every named witness with its family, the nullity Theorem 1.5 assigns, and its family dimension."""
    import random

    rng = random.Random(SEED)
    rows: list[dict[str, Any]] = []
    zero = [Fraction(0)] * HALF
    nonzd_pool = [basis_vector(p, HALF) for p in (1, 2, 3)]
    for frame in range(FRAMES_PER_FAMILY):
        a = zero_divisor(30_000 + frame)
        span, annihilator = frame_spaces(a)
        b_zd = zero_divisor(40_000 + frame)
        locus_b = combination(combination_weights(rng, 6), span)
        w_basis = c_orthogonal_space(a, annihilator)
        w_b = combination(combination_weights(rng, len(w_basis)), w_basis)
        nonzd = nonzd_pool[frame]
        nonzd_b = [Fraction(int(k == 4 + frame)) for k in range(HALF)]
        rows += [
            {"family": "zd-axis", "x": bracket(a, zero), "nullity": 16, "dimension": ZD_CONE_DIMENSION - 1},
            {"family": "nonzd-axis", "x": bracket(nonzd, zero), "nullity": 12, "dimension": C4_PERP_DIMENSION - 1},
            {"family": "zd-zd-locus", "x": bracket(a, locus_b), "nullity": 12, "dimension": 17},
            {"family": "zd-zd-generic", "x": bracket(a, b_zd), "nullity": 8, "dimension": 2 * ZD_CONE_DIMENSION - 1},
            {
                "family": "zd-nonzd-locus",
                "x": bracket(a, w_b),
                "nullity": 8,
                "dimension": ZD_CONE_DIMENSION + len(w_basis) - 1,
                "w_dimension": len(w_basis),
            },
            {
                "family": "zd-nonzd-generic",
                "x": bracket(a, nonzd_b),
                "nullity": 4,
                "dimension": ZD_CONE_DIMENSION + C4_PERP_DIMENSION - 1,
            },
            {
                "family": "nonzd-nonzd-locus",
                "x": bracket(nonzd, nonzd_b),
                "nullity": 4,
                "dimension": C4_PERP_DIMENSION + (C4_PERP_DIMENSION - 2) - 1,
            },
        ]
    for p in range(1, 8):
        x = [Fraction(0)] * DIM
        x[I4] = Fraction(1)
        x[HALF + p] = Fraction(1)
        rows.append({"family": "proposition-8.2", "x": x, "nullity": 12, "dimension": None, "p": p})
    moreno = [Fraction(0)] * DIM
    moreno[1], moreno[10], moreno[24] = Fraction(1), Fraction(1), Fraction(2)
    rows.append({"family": "moreno-unequal-norm", "x": moreno, "nullity": 4, "dimension": None})
    for index, row in enumerate(rows):
        row["witness"] = index
    return rows


def certify(row: dict[str, Any]) -> dict[str, Any]:
    bound = tangent_bound(row["x"])
    out = {key: value for key, value in row.items() if key not in ("x", "nullity")}
    out["x"] = [str(value) for value in row["x"]]
    out["expected_nullity"] = row["nullity"]
    out.update(bound)
    out["certified_local_dimension"] = (
        row["dimension"]
        if row["dimension"] is not None and row["dimension"] == bound["dimension_upper_bound"]
        else None
    )
    return out


def run() -> dict[str, Any]:
    rows = parallel.ordered_map(certify, witnesses(), min_items=2)
    violations = [
        row["witness"]
        for row in rows
        if row["nullity"] != row["expected_nullity"]
        or (row["dimension"] is not None and row["dimension"] > row["dimension_upper_bound"])
    ]
    return {
        "schema": SCHEMA,
        "seed": SEED,
        "rows": rows,
        "violations": violations,
        "summary": summarize(rows),
    }


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    families: dict[str, dict[str, Any]] = {}
    for row in rows:
        entry = families.setdefault(
            row["family"], {"family": row["family"], "nullity": row["nullity"], "dimensions": set(), "bounds": set()}
        )
        if row["dimension"] is not None:
            entry["dimensions"].add(row["dimension"])
        entry["bounds"].add(row["dimension_upper_bound"])
    return [
        {
            **{key: value for key, value in entry.items() if key not in ("dimensions", "bounds")},
            "family_dimensions": sorted(entry["dimensions"]),
            "tangent_bounds": sorted(entry["bounds"]),
        }
        for entry in families.values()
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    args = parser.parse_args()
    record = run()
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    else:
        retained = json.loads(args.check.read_text(encoding="utf-8"))
        _require(retained == json.loads(json.dumps(record)), "the recomputed certificate differs from the record")
    for entry in record["summary"]:
        print(json.dumps(entry))
    _require(not record["violations"], f"witnesses {record['violations']} contradict their family")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
