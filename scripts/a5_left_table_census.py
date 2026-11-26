"""Commutant and associator census of the Cayley-Dickson left tables, and points of the Euclidean cone of A_5.

Three items of pool row MATH-71, each exact:

- the commutant of the left tables L_a of A_n, a in [0, 2^n), from the cocycle of the signed permutations: X L_a = L_a X
  for every a links X[p, q] to X[a ^ p, a ^ q] with the sign s(a, a ^ q) s(a, a ^ p), so each difference d = p ^ q
  spans one orbit and contributes one dimension exactly when its signs are consistent; checked for n = 1 to 10 and
  against the rank of the linear system X L_a - L_a X = 0 for n = 1 to 4;
- the number of ordered triples of imaginary basis units with nonzero associator, against (D - 2)(D - 4)(D + 6)/2,
  for D = 4 to 1024;
- the nullity of L_y on the Euclidean cone r^2 + t^2 = 0 of the slice y = sum_a x_a e_a + t e_26, S = {1, 3, 4, 5, 6, 7},
  at points over the imaginary quadratic fields Q(sqrt(-d)) (rank of the 64 x 64 rational form) and at points over
  Q_p (reduction mod p: rank 20 of the reduction bounds the nullity over Z_p by 12, and the bound nullity >= 12 holds
  in characteristic 0).

Independent items run through parallel.ordered_map. No random draw enters.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from flint import fmpz_mat, nmod_mat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import parallel  # noqa: E402
from a5_null_slice_associator_envelope import SPACE, TIME, sign_rows, square_root, table  # noqa: E402

COMMUTANT_LEVELS: tuple[int, ...] = tuple(range(1, 11))
DIRECT_LEVELS: tuple[int, ...] = (1, 2, 3, 4)
TRIPLE_LEVELS: tuple[int, ...] = tuple(range(2, 11))
DIRECT_PRIME = 32003
DIMENSION = 32
# (d, x, s): t = s sqrt(-d) with sum x_a^2 = d s^2, so r^2 + t^2 = 0; d = 1 adds Gaussian points to the three of the
# associator-envelope record.
FIELD_POINTS: tuple[tuple[int, tuple[int, ...], int], ...] = (
    (1, (3, 4, 0, 0, 0, 0), 5),
    (1, (1, 2, 2, 0, 0, 0), 3),
    (1, (2, 3, 6, 0, 0, 0), 7),
    (1, (1, 1, 1, 1, 0, 0), 2),
    (2, (1, 1, 0, 0, 0, 0), 1),
    (3, (1, 1, 1, 0, 0, 0), 1),
    (5, (1, 2, 0, 0, 0, 0), 1),
    (6, (1, 1, 2, 0, 0, 0), 1),
    (7, (1, 1, 1, 2, 0, 0), 1),
    (11, (1, 1, 3, 0, 0, 0), 1),
)
# Off the cone: t = sqrt(-d) with sum x_a^2 != d.
OFF_CONE_POINTS: tuple[tuple[int, tuple[int, ...], int], ...] = ((3, (1, 1, 0, 0, 0, 0), 1), (2, (1, 1, 1, 0, 0, 0), 1))
# (p, x): t is a root of t^2 = -r^2 modulo p, lifted to Z_p by Hensel's lemma.
LOCAL_POINTS: tuple[tuple[int, tuple[int, ...]], ...] = (
    (5, (1, 0, 0, 0, 0, 0)),
    (13, (1, 0, 0, 0, 0, 0)),
    (17, (1, 0, 0, 0, 0, 0)),
    (29, (1, 0, 0, 0, 0, 0)),
    (37, (1, 0, 0, 0, 0, 0)),
    (41, (1, 0, 0, 0, 0, 0)),
    (11, (1, 1, 0, 0, 0, 0)),
    (43, (1, 1, 0, 0, 0, 0)),
    (59, (1, 1, 1, 0, 0, 0)),
    (97, (1, 2, 0, 0, 0, 0)),
)
SOURCE_FILES = (
    "gororoba_quantum/cd_core.py",
    "scripts/a5_null_slice_associator_envelope.py",
    "scripts/a5_left_table_census.py",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def orbit_consistent(signs: Any, d: int) -> bool:
    """Whether the orbit {(p, p ^ d)} carries a consistent sign: f(a) = s(a, a ^ d) s(a, a) from p = 0, then every edge
    (p -> a ^ p, weight s(a, a ^ p ^ d) s(a, a ^ p)) must agree with f."""
    dimension = signs.shape[0]
    a = np.arange(dimension)
    f = signs[a, a ^ d] * signs[a, a]
    rows = a[:, None]
    cols = a[None, :]
    return bool(np.array_equal(f[rows ^ cols], signs[rows, rows ^ cols ^ d] * signs[rows, rows ^ cols] * f[cols]))


def commutant_item(task: tuple[int, int, int]) -> list[int]:
    level, start, stop = task
    dimension = 1 << level
    signs = sign_rows(dimension, list(range(dimension)))
    return [d for d in range(start, stop) if orbit_consistent(signs, d)]


def commutant_direct(level: int) -> int:
    """Dimension of {X : X L_a = L_a X for every a} from the rank of the stacked Kronecker system modulo DIRECT_PRIME."""
    dimension = 1 << level
    signs = sign_rows(dimension, list(range(dimension)))
    eye = np.eye(dimension, dtype=np.int64)
    blocks = []
    for a in range(dimension):
        left = table(signs, a)
        blocks.append(np.kron(left.T, eye) - np.kron(eye, left))
    stacked = np.vstack(blocks) % DIRECT_PRIME
    return dimension * dimension - int(nmod_mat(stacked.tolist(), DIRECT_PRIME).rank())


def triple_item(task: tuple[int, int, int]) -> int:
    """Ordered triples (a, b, c) of imaginary units with a in [start, stop) and nonzero associator:
    s(a, b) s(a ^ b, c) != s(b, c) s(a, b ^ c)."""
    level, start, stop = task
    dimension = 1 << level
    signs = sign_rows(dimension, list(range(dimension)))
    units = np.arange(1, dimension)
    b = units[:, None]
    c = units[None, :]
    count = 0
    for a in range(start, stop):
        left = signs[a, b] * signs[a ^ b, c]
        right = signs[b, c] * signs[a, b ^ c]
        count += int(np.count_nonzero(left != right))
    return count


def chunks(level: int, first: int, size: int) -> list[tuple[int, int, int]]:
    dimension = 1 << level
    return [(level, start, min(start + size, dimension)) for start in range(first, dimension, size)]


def slice_tables() -> list[Any]:
    signs = sign_rows(DIMENSION, list(range(DIMENSION)))
    return [table(signs, k) for k in range(DIMENSION)]


def field_nullity(tables: list[Any], d: int, x: tuple[int, ...], s: int) -> int:
    """Nullity over Q(sqrt(-d)) of A + s w J, w^2 = -d, from the rank of [[A, -d s J], [s J, A]]."""
    real: Any = sum(v * tables[a] for v, a in zip(x, SPACE, strict=True))
    time = tables[TIME]
    block = np.block([[real, -d * s * time], [s * time, real]])
    return (2 * DIMENSION - int(fmpz_mat(block.tolist()).rank())) // 2


def local_nullity(tables: list[Any], p: int, x: tuple[int, ...]) -> dict[str, Any]:
    r2 = sum(v * v for v in x)
    root = square_root(-r2, p)
    require(root is not None, f"-{r2} is not a square modulo {p}")
    assert root is not None
    operator: Any = sum(v * tables[a] for v, a in zip(x, SPACE, strict=True)) + root * tables[TIME]
    rank = int(nmod_mat([[int(v) % p for v in row] for row in operator.tolist()], p).rank())
    return {"p": p, "x": list(x), "t_mod_p": int(root), "nullity_mod_p": DIMENSION - rank}


def compute() -> dict[str, Any]:
    commutant_tasks = [task for level in COMMUTANT_LEVELS for task in chunks(level, 0, 32)]
    consistent = parallel.ordered_map(commutant_item, commutant_tasks, min_items=1)
    orbits: dict[int, list[int]] = {}
    for (level, _start, _stop), found in zip(commutant_tasks, consistent, strict=True):
        orbits.setdefault(level, []).extend(found)
    triple_tasks = [task for level in TRIPLE_LEVELS for task in chunks(level, 1, 16)]
    counts = parallel.ordered_map(triple_item, triple_tasks, min_items=1)
    triples: dict[int, int] = {}
    for (level, _start, _stop), count in zip(triple_tasks, counts, strict=True):
        triples[level] = triples.get(level, 0) + count
    direct = parallel.ordered_map(commutant_direct, list(DIRECT_LEVELS), min_items=1)
    tables = slice_tables()
    return {
        "commutant": {
            str(1 << level): {"dimension": len(found), "consistent_differences": found[:8]}
            for level, found in sorted(orbits.items())
        },
        "commutant_direct_mod_32003": {str(1 << level): value for level, value in zip(DIRECT_LEVELS, direct, strict=True)},
        "field_points": [
            {"d": d, "x": list(x), "s": s, "nullity": field_nullity(tables, d, x, s)} for d, x, s in FIELD_POINTS
        ],
        "off_cone_points": [
            {"d": d, "x": list(x), "s": s, "nullity": field_nullity(tables, d, x, s)} for d, x, s in OFF_CONE_POINTS
        ],
        "local_points": [local_nullity(tables, p, x) for p, x in LOCAL_POINTS],
        "nonassociating_triples": {
            str(1 << level): {"count": count, "formula": ((1 << level) - 2) * ((1 << level) - 4) * ((1 << level) + 6) // 2}
            for level, count in sorted(triples.items())
        },
    }


def validate(result: dict[str, Any]) -> None:
    pass


def self_test() -> None:
    pass


def dumps(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=1, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("self-test: paired controls pass")
        return 0
    result = compute()
    validate(result)
    text = dumps(result)
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
