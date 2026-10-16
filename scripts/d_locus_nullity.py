"""Exact nullity of the A_5 bracket {a, b} across the D-locus of two sedenion zero divisors.

Biss, Christensen, Dugger and Isaksen (math/0702075, docs/notes/math-0702075.md)
write H_5^perp as brackets {a, b} = (a + b, i_4 (-a + b))/sqrt 2 with a, b in
C_4^perp, C_4 = span(e_0, e_8) and i_4 = e_8, in cd_core's doubling (index k of
the second half is 16 + k). The script uses (a + b, e_8 (-a + b)), sqrt 2 times
the bracket, so every entry stays rational; nullity is scale-free. Theorem 1.5
gives nullity dim Ann(a) + dim Ann(b) off the D-locus and 4 more on it, so 8
and 12 when both entries are zero divisors. Corollary 7.4 places {a, b}, for
zero divisors a = (a1, a2) and b, on the D-locus exactly when b lies in

    V(a) = span_R{(a1, -a2), (a2, a1)} + Eig_2(a),
    Eig_2(a) = {x : a(ax) = -2 |a|^2 x}.

Each zero divisor a comes from a Cayley frame (an exactly rational orthonormal
pure pair, scripts/moreno_stiefel_nullity.py) times a seeded positive rational,
and is paired with five b's, each times its own seeded positive rational so
the length ratio |b|/|a| varies:

  locus      a seeded rational combination of a basis of V(a)
  generic    an independent Cayley-frame zero divisor
  annihilator a seeded rational combination of a basis of Ann(a)
  self       b = a
  swap       b = (a2, -a1), inside <<a1, a2>>^2 and outside span{(a1, -a2), (a2, a1)}

Before the table the run asserts, and stops at the first failure: L_v against
cd_core.cd_multiply; |(a + b, e_8 (b - a))|^2 = 2 (|a|^2 + |b|^2) (Lemma 3.5);
dim Ann(a) = dim Eig_2(a) = 4, dim V(a) = 6 and Ann(a) orthogonal to V(a);
and nullity 4 in A_4 for every b, which Theorem 7.5 implies on V(a). The table
then sets membership in V(a), by exact rank, against the A_5 nullity.
Falsifier: a member with nullity other than 12, or a non-member with nullity
other than 8. Nullity is certified as in moreno_stiefel_nullity.certify: the
rank modulo 2^61 - 1 bounds the rational rank below and exact rational kernel
vectors bound it above.

Usage:
    "$PYTHON" scripts/d_locus_nullity.py --out docs/evidence/d_locus_nullity/result.json
    "$PYTHON" scripts/d_locus_nullity.py --check docs/evidence/d_locus_nullity/result.json [--limit K]

--check recomputes every pair, or the pairs of the first K frames, and requires
them to equal the retained rows; it also re-derives the summary from the rows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
from moreno_stiefel_nullity import PRIME, cayley_frame, check_left_matrix, rank_mod, rational_kernel  # noqa: E402

from cd_core import cd_sign  # noqa: E402

SCHEMA = "d-locus-nullity-v1"
SEED = 702075
FRAMES = 200
A_SEED_BASE = 10_000
B_SEED_BASE = 20_000
KINDS = ("locus", "generic", "annihilator", "self", "swap")
SCALE_RANGE = 9
COMBINATION_RANGE = 4
I4 = 8

Vector = list[Fraction]


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"d_locus_nullity: {message}")


def left_rational(dim: int, v: Vector) -> list[Vector]:
    return [[v[k ^ j] * cd_sign(dim, k ^ j, j) for j in range(dim)] for k in range(dim)]


def apply(matrix: list[Vector], x: Vector) -> Vector:
    return [sum((row[j] * x[j] for j in range(len(x))), Fraction(0)) for row in matrix]


def dot(x: Vector, y: Vector) -> Fraction:
    return sum((p * q for p, q in zip(x, y, strict=True)), Fraction(0))


def integer_rows(rows: list[Vector]) -> list[list[int]]:
    scale = math.lcm(1, *(value.denominator for row in rows for value in row))
    return [[int(value * scale) for value in row] for row in rows]


def kernel(rows: list[Vector]) -> list[Vector]:
    return rational_kernel(integer_rows(rows))


def span_rank(vectors: list[Vector]) -> int:
    return rank_mod(integer_rows(vectors), PRIME) if vectors else 0


def nullity(dim: int, v: Vector) -> int:
    """Rank modulo PRIME bounds the rational rank below; verified kernel vectors bound it above."""
    matrix = integer_rows(left_rational(dim, v))
    rank = rank_mod(matrix, PRIME)
    if rank == dim:
        return 0
    basis = rational_kernel(matrix)
    _require(
        all(
            all(value == 0 for value in apply([[Fraction(x) for x in row] for row in matrix], vector))
            for vector in basis
        ),
        "a rational kernel vector fails L_v x = 0",
    )
    _require(rank + len(basis) == dim, f"rank {rank} modulo P and {len(basis)} kernel vectors do not bound the nullity")
    return dim - rank


def zero_divisor(seed: int) -> Vector:
    a1, a2, _ = cayley_frame(7, seed)
    return [Fraction(0), *a1, Fraction(0), *a2]


def bracket(a: Vector, b: Vector) -> Vector:
    """sqrt 2 {a, b} = (a + b, i_4 (b - a)) in A_5."""
    i4 = left_rational(16, [Fraction(int(k == I4)) for k in range(16)])
    return [x + y for x, y in zip(a, b, strict=True)] + apply(i4, [y - x for x, y in zip(a, b, strict=True)])


def frame_spaces(a: Vector) -> tuple[list[Vector], list[Vector]]:
    """A basis of V(a) and one of Ann(a), with the dimensions and orthogonality Section 7 states."""
    left = left_rational(16, a)
    square = [[dot(row, [left[k][j] for k in range(16)]) for j in range(16)] for row in left]
    shifted = [[square[i][j] + (2 * dot(a, a) if i == j else 0) for j in range(16)] for i in range(16)]
    eig2 = kernel(shifted)
    annihilator = kernel(left)
    _require(len(annihilator) == 4 and len(eig2) == 4, f"dim Ann(a) = {len(annihilator)}, dim Eig_2(a) = {len(eig2)}")
    a1, a2 = a[:8], a[8:]
    span = [a1 + [-x for x in a2], a2 + a1, *eig2]
    _require(span_rank(span) == 6, "dim V(a) is not 6")
    _require(all(dot(u, w) == 0 for u in annihilator for w in span), "Ann(a) is not orthogonal to V(a)")
    return span, annihilator


def combination(rng: random.Random, basis: list[Vector]) -> Vector:
    while True:
        weights = [
            Fraction(rng.randint(-COMBINATION_RANGE, COMBINATION_RANGE), rng.randint(1, COMBINATION_RANGE))
            for _ in basis
        ]
        vector = [sum((w * v[k] for w, v in zip(weights, basis, strict=True)), Fraction(0)) for k in range(16)]
        if any(vector):
            return vector


def scale(rng: random.Random) -> Fraction:
    return Fraction(rng.randint(1, SCALE_RANGE), rng.randint(1, SCALE_RANGE))


def digest(values: Vector) -> str:
    return hashlib.sha256(json.dumps([str(x) for x in values]).encode()).hexdigest()


def frame_rows(frame: int, rng: random.Random) -> list[dict[str, Any]]:
    a_scale = scale(rng)
    a = [x * a_scale for x in zero_divisor(A_SEED_BASE + frame)]
    _require(nullity(16, a) == 4, f"frame {frame}: a is not a zero divisor of A_4")
    span, annihilator = frame_spaces(a)
    candidates = {
        "locus": combination(rng, span),
        "generic": zero_divisor(B_SEED_BASE + frame),
        "annihilator": combination(rng, annihilator),
        "self": a[:],
        "swap": a[8:] + [-x for x in a[:8]],
    }
    rows = []
    for kind in KINDS:
        b_scale = scale(rng)
        b = [x * b_scale for x in candidates[kind]]
        element = bracket(a, b)
        _require(dot(element, element) == 2 * (dot(a, a) + dot(b, b)), f"frame {frame} {kind}: Lemma 3.5 norm")
        b_nullity = nullity(16, b)
        _require(b_nullity == 4, f"frame {frame} {kind}: b has A_4 nullity {b_nullity}")
        member = span_rank([*span, b]) == 6
        rows.append(
            {
                "frame": frame,
                "kind": kind,
                "a_scale": str(a_scale),
                "b_scale": str(b_scale),
                "length_ratio_squared": str(dot(b, b) / dot(a, a)),
                "member": member,
                "b_nullity_a4": b_nullity,
                "nullity": nullity(32, element),
                "element_sha256": digest(element),
            }
        )
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    table = Counter((row["kind"], row["member"], row["nullity"]) for row in rows)
    violations = [
        row
        for row in rows
        if row["nullity"] != (12 if row["member"] else 8) or row["member"] != (row["kind"] == "locus")
    ]
    ratios = [math.sqrt(Fraction(row["length_ratio_squared"])) for row in rows if row["member"]]
    return {
        "pairs": len(rows),
        "table": [
            {"kind": kind, "member": member, "nullity": value, "pairs": count}
            for (kind, member, value), count in sorted(table.items())
        ],
        "violations": len(violations),
        "member_length_ratio_range": [round(min(ratios), 6), round(max(ratios), 6)] if ratios else None,
    }


def run(frames: int) -> list[dict[str, Any]]:
    rng = random.Random(SEED)
    rows: list[dict[str, Any]] = []
    for frame in range(frames):
        rows += frame_rows(frame, rng)
    return rows


def result(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "source": "Biss, Christensen, Dugger, Isaksen, math/0702075 v2: Lemma 3.5, Theorem 1.5, Corollary 7.4, "
        "Theorem 7.5",
        "convention": "cd_core doubling; element (a + b, e_8 (b - a)) = sqrt 2 {a, b}; i_4 = e_8",
        "seed": SEED,
        "frames": FRAMES,
        "kinds": list(KINDS),
        "nullity_certificate": "rank modulo 2^61 - 1 plus verified rational kernel vectors",
        "left_matrix_checks": check_left_matrix(),
        "summary": summarize(rows),
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    parser.add_argument("--limit", type=int, help="with --check, recompute only the first LIMIT frames")
    args = parser.parse_args()
    if args.out:
        record = result(run(FRAMES))
        _require(
            record["summary"]["violations"] == 0, f"{record['summary']['violations']} pairs contradict Theorem 1.5"
        )
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(record["summary"]))
        return 0
    retained = json.loads(args.check.read_text(encoding="utf-8"))
    _require(retained.get("schema") == SCHEMA, "schema differs")
    _require(retained["summary"] == summarize(retained["rows"]), "the retained summary differs from its rows")
    _require(retained["summary"]["violations"] == 0, "the retained rows contradict Theorem 1.5")
    frames = FRAMES if args.limit is None else min(args.limit, FRAMES)
    rows = run(frames)
    _require(rows == retained["rows"][: len(rows)], f"recomputed rows of the first {frames} frames differ")
    _require(retained["left_matrix_checks"] == check_left_matrix(), "the cd_multiply cross-check differs")
    print(
        f"d_locus_nullity: {len(rows)} of {len(retained['rows'])} pairs recomputed; {json.dumps(retained['summary'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
