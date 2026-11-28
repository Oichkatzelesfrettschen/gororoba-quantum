"""Nilpotent and idempotent counts of the Cayley-Dickson algebra A_n over F_p with the cd_core product.

The product is e_i e_j = s(i, j) e_(i ^ j) with s = gororoba_quantum.cd_core.cd_sign(2^n, i, j), coordinates in F_p, p
odd. Every element x of every Cayley-Dickson algebra over a field of characteristic other than 2 satisfies
x^2 = 2 Re(x) x - N(x), with N(x) the sum of the squared coordinates. The record enumerates every element of F_p^(2^n)
and checks, with the product computed from the sign table and no use of that identity:

- the identity itself holds at every element;
- the elements with x^2 = 0 are exactly those with Re(x) = 0 and N(x) = 0, and number p^(2^n - 2);
- the elements with x^4 = (x^2)(x^2) = 0 are the same set;
- the idempotents other than 0 and 1 number p^(2^n - 2) + p^(2^(n-1) - 1).

Controls: one negated table entry s(1, 2) breaks the identity and the predicate, and the case n = 1 (the complex numbers
over F_p) lies outside the idempotent formula. Elements are split into index ranges that run through
parallel.ordered_map. No random draw enters.
"""

from __future__ import annotations

import argparse
import json
import sys
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

CASES = ((2, 3), (2, 5), (2, 7), (3, 3), (3, 5), (3, 7), (4, 3))
CONTROLS = ((2, 3, True), (3, 3, True), (1, 3, False), (1, 5, False))
CONTROL_COUNTS = {
    (2, 3, True): {"nil2": 1, "idempotents": 8, "predicate_mismatches": 8},
    (3, 3, True): {"nil2": 369, "idempotents": 432, "predicate_mismatches": 360},
    (1, 3, False): {"nil2": 1, "idempotents": 0, "predicate_mismatches": 0},
    (1, 5, False): {"nil2": 1, "idempotents": 2, "predicate_mismatches": 0},
}
CHUNK = 1 << 17


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


@cache
def kernels(dim: int, flip: bool) -> tuple[tuple[np.ndarray, np.ndarray], ...]:
    """Per left index i: the permutation k -> k ^ i and the signs s(i, k ^ i), so (a_i e_i) b has k-th entry
    s(i, k ^ i) a_i b_(k ^ i)."""
    out = []
    for i in range(dim):
        perm = np.array([k ^ i for k in range(dim)], dtype=np.int64)
        signs = np.array([cd_sign(dim, i, int(j)) for j in perm], dtype=np.int64)
        if flip:
            for k, j in enumerate(perm):
                if (i, int(j)) == (1, 2):
                    signs[k] = -signs[k]
        out.append((perm, signs))
    return tuple(out)


def multiply(a: np.ndarray, b: np.ndarray, p: int, flip: bool) -> np.ndarray:
    out = np.zeros_like(a)
    for i, (perm, signs) in enumerate(kernels(a.shape[1], flip)):
        out += a[:, i : i + 1] * (b[:, perm] * signs)
    return out % p


def count_range(task: tuple[int, int, bool, int, int]) -> tuple[int, int, int, int, int]:
    """Counts over an index range: x^2 = 0, x^4 = 0, idempotents other than 0 and 1, identity failures,
    predicate mismatches."""
    n, p, flip, start, stop = task
    dim = 1 << n
    index = np.arange(start, stop, dtype=np.int64)
    x = np.empty((index.size, dim), dtype=np.int64)
    rest = index.copy()
    for k in range(dim):
        x[:, k] = rest % p
        rest //= p
    x2 = multiply(x, x, p, flip)
    x4 = multiply(x2, x2, p, flip)
    norm = (x * x).sum(axis=1) % p
    rhs = (2 * x[:, :1] * x) % p
    rhs[:, 0] = (rhs[:, 0] - norm) % p
    zero_square = ~x2.any(axis=1)
    one = np.zeros(dim, dtype=np.int64)
    one[0] = 1
    idempotent = (x2 == x).all(axis=1) & x.any(axis=1) & ~(x == one).all(axis=1)
    predicate = (x[:, 0] == 0) & (norm == 0)
    return (
        int(zero_square.sum()),
        int((~x4.any(axis=1)).sum()),
        int(idempotent.sum()),
        int((rhs != x2).any(axis=1).sum()),
        int((predicate != zero_square).sum()),
    )


def run_case(n: int, p: int, flip: bool) -> dict[str, Any]:
    dim = 1 << n
    total = p**dim
    tasks = [(n, p, flip, start, min(total, start + CHUNK)) for start in range(0, total, CHUNK)]
    sums = [sum(column) for column in zip(*parallel.ordered_map(count_range, tasks), strict=True)]
    return {
        "n": n,
        "p": p,
        "dim": dim,
        "flip": flip,
        "elements": total,
        "nil2": sums[0],
        "nil4": sums[1],
        "idempotents": sums[2],
        "identity_failures": sums[3],
        "predicate_mismatches": sums[4],
        "formula_nil2": p ** (dim - 2),
        "formula_idempotents": p ** (dim - 2) + p ** (dim // 2 - 1),
    }


def compute() -> dict[str, Any]:
    return {
        "schema": "a5-nilpotent-idempotent-counts/1",
        "cases": [run_case(n, p, False) for n, p in CASES],
        "controls": [run_case(n, p, flip) for n, p, flip in CONTROLS],
    }


def validate(result: dict[str, Any]) -> None:
    require([(r["n"], r["p"]) for r in result["cases"]] == list(CASES), "case list")
    for r in result["cases"]:
        label = f"A_{r['n']} over F_{r['p']}"
        require(
            r["identity_failures"] == 0, f"{label}: x^2 = 2 Re(x) x - N(x) fails at {r['identity_failures']} elements"
        )
        require(r["predicate_mismatches"] == 0, f"{label}: nilpotent set differs from Re = 0, N = 0")
        require(r["nil2"] == r["formula_nil2"], f"{label}: nilpotent count {r['nil2']}")
        require(r["nil4"] == r["nil2"], f"{label}: x^4 = 0 count {r['nil4']}")
        require(r["idempotents"] == r["formula_idempotents"], f"{label}: idempotent count {r['idempotents']}")
    for r in result["controls"]:
        expected = CONTROL_COUNTS[(r["n"], r["p"], r["flip"])]
        got = {k: r[k] for k in expected}
        require(got == expected, f"control {(r['n'], r['p'], r['flip'])}: {got}")
        if r["flip"]:
            require(r["identity_failures"] > 0, f"control {(r['n'], r['p'])}: the identity survives a flipped sign")
        else:
            require(r["identity_failures"] == 0, f"control {(r['n'], r['p'])}: identity")
    by_p = {(r["n"], r["p"]): r for r in result["controls"]}
    require(
        by_p[(1, 3)]["idempotents"] != by_p[(1, 3)]["formula_idempotents"], "n = 1 lies inside the idempotent formula"
    )


def self_test() -> None:
    def control(baseline: bool, mutant: bool, name: str) -> None:
        require(baseline and not mutant, f"control {name}: baseline {baseline}, mutant {mutant}")

    base = run_case(2, 3, False)
    flipped = run_case(2, 3, True)
    control(base["identity_failures"] == 0, flipped["identity_failures"] == 0, "identity under one negated sign")
    control(base["predicate_mismatches"] == 0, flipped["predicate_mismatches"] == 0, "nilpotent predicate")
    control(base["nil2"] == base["formula_nil2"], flipped["nil2"] == flipped["formula_nil2"], "nilpotent count")
    control(
        base["idempotents"] == base["formula_idempotents"],
        run_case(1, 3, False)["idempotents"] == run_case(1, 3, False)["formula_idempotents"],
        "idempotent formula at n = 2 against n = 1",
    )


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
