"""Exhaustive censuses behind the kernel-map program, written to census.json; --check recomputes and compares.

1. Every two-term operand e_i + t e_j of A_5 (1 <= i < j <= 31, t = +-1; 930 operands): the nullity of its cd_core
   left multiplication (python-flint exact rank) equals the number of XOR pairs {k, k ^ (i ^ j)} on which
   K = L_i^T (t L_j) carries equal signs.
2. The 4 x 4 coset blocks of every four-term flat operand e_a + s_b e_b + s_c e_c + s_d e_d (a ^ b ^ c ^ d = 0, distinct
   nonzero indices) of A_4 and A_5, classified up to row and column permutation and negation by the minimum, over all
   576 permutation pairs, of the matrix normalized to a positive first row and column.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

import flint
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import cd_core  # noqa: E402
import parallel  # noqa: E402

OUT = Path(__file__).with_name("census.json")
PERMS = list(itertools.permutations(range(4)))


def two_term(args: tuple[int, int, int]) -> tuple[int, int]:
    i, j, t = args
    li = np.array(cd_core.left_mult_matrix(32, cd_core.basis(32, i)), dtype=int)
    lj = np.array(cd_core.left_mult_matrix(32, cd_core.basis(32, j)), dtype=int)
    nullity = 32 - int(flint.fmpz_mat((li + t * lj).tolist()).rank())
    k = li.T @ (t * lj)
    m = i ^ j
    aligned = sum(1 for x in range(32) if x < x ^ m and k[x ^ m, x] == k[x, x ^ m])
    return nullity, aligned


def canonical(block: tuple[int, ...]) -> tuple[int, ...]:
    b = np.array(block).reshape(4, 4)
    best: tuple[int, ...] | None = None
    for rp in PERMS:
        br = b[list(rp), :]
        for cp in PERMS:
            m = br[:, list(cp)]
            m = m * m[0, :][None, :]
            m = m * m[:, 0][:, None]
            key = tuple(int(v) for v in m.flatten())
            if best is None or key < best:
                best = key
    if best is None:
        raise ValueError("empty permutation set")
    return best


def coset_blocks(dim: int) -> set[tuple[int, ...]]:
    out: set[tuple[int, ...]] = set()
    for a, b, c in itertools.combinations(range(1, dim), 3):
        d = a ^ b ^ c
        if d == 0 or d in (a, b, c) or d < c:
            continue
        idx = (a, b, c, d)
        group = sorted({0, a ^ b, a ^ c, a ^ d})
        for signs in itertools.product((1, -1), repeat=3):
            coef = (1, *signs)
            seen: set[tuple[int, ...]] = set()
            for k in range(dim):
                coset = tuple(sorted(k ^ v for v in group))
                if coset in seen:
                    continue
                seen.add(coset)
                outs = sorted({a ^ q for q in coset})
                m = np.zeros((4, 4), dtype=int)
                for col, q in enumerate(coset):
                    for e, cf in zip(idx, coef, strict=True):
                        m[outs.index(e ^ q), col] += cf * cd_core.cd_sign(dim, e, q)
                out.add(tuple(int(v) for v in m.flatten()))
    return out


def spectrum(key: tuple[int, ...]) -> list[float]:
    m = np.array(key).reshape(4, 4)
    return [round(float(v), 3) + 0.0 for v in np.linalg.eigvalsh(m.T @ m)]


def compute() -> dict[str, object]:
    operands = [(i, j, t) for i, j in itertools.combinations(range(1, 32), 2) for t in (1, -1)]
    pairs = parallel.ordered_map(two_term, operands)
    record: dict[str, object] = {
        "schema": "pathion-kernel-map-census-v1",
        "two_term_operands": len(operands),
        "two_term_nullity_equals_aligned_pairs": all(n == a for n, a in pairs),
        "two_term_nullity_counts": {str(k): v for k, v in sorted(Counter(n for n, _ in pairs).items())},
    }
    classes = {}
    for dim in (16, 32):
        blocks = sorted(coset_blocks(dim))
        if any(abs(v) != 1 for blk in blocks for v in blk):
            raise ValueError(f"dimension {dim}: a coset block entry is not +-1")
        classes[dim] = set(parallel.ordered_map(canonical, blocks, min_items=2))
        record[f"four_term_blocks_{dim}"] = len(blocks)
        record[f"four_term_classes_{dim}"] = len(classes[dim])
    # Every 4 x 4 +-1 matrix is equivalent to one with a positive first row and first column.
    normal = (0, 1, 2, 3, 4, 8, 12)
    every = [s for s in itertools.product((1, -1), repeat=16) if all(s[k] == 1 for k in normal)]
    record["classes_of_all_4x4_pm1"] = len(set(parallel.ordered_map(canonical, every, min_items=2)))
    record["classes_new_at_32_spectra"] = sorted(spectrum(k) for k in classes[32] - classes[16])
    return record


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    text = json.dumps(compute(), indent=1, sort_keys=True) + "\n"
    if args.check:
        if OUT.read_text() != text:
            raise SystemExit(f"{OUT} differs from the recomputed census")
        print("pathion kernel-map census reproduces")
        return 0
    OUT.write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
