"""Exhaustive censuses behind the kernel-map program, written to census.json; --check recomputes and compares.

1. Every two-term operand e_i + t e_j of A_5 (1 <= i < j <= 31, t = +-1; 930 operands): the nullity of its cd_core
   left multiplication (python-flint exact rank) equals the number of XOR pairs {k, k ^ (i ^ j)} on which
   K = L_i^T (t L_j) carries equal signs.
2. The 4 x 4 coset blocks of every four-term flat operand e_a + s_b e_b + s_c e_c + s_d e_d (a ^ b ^ c ^ d = 0, distinct
   nonzero indices) of A_4 and A_5, classified up to row and column permutation and negation by the minimum, over all
   576 permutation pairs, of the matrix normalized to a positive first row and column.

``--wide`` runs both censuses at D = 64 and D = 128 and writes census-wide.json (``--wide --check`` recomputes and
compares). For the two-term operands it certifies the nullity against the cd_core integer rank on every operand and
classifies the coset blocks of the case's tiling (``default_basis``: m followed by the two lowest vectors that extend
it to a 3-dimensional V). A two-term block with |V| = 8 is a direct sum of four 2 x 2 blocks, one per XOR pair
{q, q ^ m}. Row and column permutations and negations bring a 2 x 2 +-1 block to [[1, 1], [1, 1]] (an aligned pair,
rank 1) or [[1, 1], [1, -1]] (a misaligned pair, rank 2), and permuting the four blocks is free, so the class of a
two-term block is its number N_b of aligned pairs, 0 to 4, at every D. The ideal outcome law of the block circuit
(``block_law``) is a second class key. For the four-term operands it lists the 4 x 4 classes that first occur at each
dimension against the 12 classes of all 4 x 4 +-1 matrices.
"""

from __future__ import annotations

import argparse
import functools
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
WIDE_OUT = Path(__file__).with_name("census-wide.json")
WIDE_DIMS = (64, 128)
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


def span(basis: tuple[int, ...]) -> list[int]:
    out = [0]
    for vector in basis:
        out += [member ^ vector for member in out]
    return out


def default_basis(dim: int, m: int) -> tuple[int, ...]:
    """m followed by the two lowest vectors that extend it to a 3-dimensional subspace."""
    basis: list[int] = [m]
    for vector in range(1, dim):
        if len(basis) == 3:
            break
        if vector not in span(tuple(basis)):
            basis.append(vector)
    return tuple(basis)


@functools.cache
def sign_table(dim: int) -> np.ndarray:
    return np.array([[cd_core.cd_sign(dim, p, q) for q in range(dim)] for p in range(dim)], dtype=int)


def block_law(dim: int, operand: tuple[int, int, int], basis: tuple[int, ...], k0: int, plus: bool) -> np.ndarray:
    """Outcome law, index y + 8 s, of the pathion_coset_block circuit on the coset k0 + span(basis)."""
    i, j, t = operand
    m = i ^ j
    signs = sign_table(dim)
    members = span(basis)
    labels = [k0 ^ members[x] for x in range(8)]
    f0 = np.array([signs[i, k] for k in labels], dtype=float)
    f1 = np.array([signs[j, k] for k in labels], dtype=float) * t
    orientation = np.ones(8)
    for x, k in enumerate(labels):
        if k >= k ^ m:
            s_low = float(signs[i, k] * t * signs[j, k ^ m])
            orientation[x] = s_low if plus else -s_low
    psi = orientation * f0 / np.sqrt(8.0)
    low = psi / np.sqrt(2.0)
    high = (psi * f0 * f1 / np.sqrt(2.0))[np.arange(8) ^ 1]
    return np.concatenate([(low + high) / np.sqrt(2.0), (low - high) / np.sqrt(2.0)]) ** 2


def two_term_wide(
    args: tuple[int, tuple[int, int, int]],
) -> tuple[int, int, list[int], list[tuple[tuple[int, ...], ...]]]:
    dim, (i, j, t) = args
    li = np.array(cd_core.left_mult_matrix(dim, cd_core.basis(dim, i)), dtype=int)
    lj = np.array(cd_core.left_mult_matrix(dim, cd_core.basis(dim, j)), dtype=int)
    nullity = dim - int(flint.fmpz_mat((li + t * lj).tolist()).rank())
    kmat = li.T @ (t * lj)
    m = i ^ j
    aligned = {q: bool(kmat[q ^ m, q] == kmat[q, q ^ m]) for q in range(dim) if q < q ^ m}
    basis = default_basis(dim, m)
    members = span(basis)
    counts: list[int] = []
    laws: list[tuple[tuple[int, ...], ...]] = []
    seen: set[int] = set()
    for k in range(dim):
        if k in seen:
            continue
        coset = [k ^ v for v in members]
        seen |= set(coset)
        counts.append(sum(aligned[q] for q in coset if q < q ^ m))
        plus = block_law(dim, (i, j, t), basis, k, True)
        minus = block_law(dim, (i, j, t), basis, k, False)
        laws.append(
            tuple(
                sorted(
                    (round(256 * plus[y]), round(256 * plus[y + 8]), round(256 * minus[y]), round(256 * minus[y + 8]))
                    for y in range(8)
                )
            )
        )
    return nullity, sum(aligned.values()), counts, laws


def normalized(matrix: np.ndarray) -> tuple[int, ...]:
    matrix = matrix * matrix[0, :][None, :]
    matrix = matrix * matrix[:, 0][:, None]
    return tuple(int(v) for v in matrix.flatten())


def four_term_blocks_from(args: tuple[int, int]) -> set[tuple[int, ...]]:
    """Normalized 4 x 4 coset blocks of every four-term flat operand whose smallest index is ``a``."""
    dim, a = args
    signs = sign_table(dim)
    out: set[tuple[int, ...]] = set()
    for b, c in itertools.combinations(range(a + 1, dim), 2):
        d = a ^ b ^ c
        if d == 0 or d in (a, b, c) or d < c:
            continue
        idx = (a, b, c, d)
        group = sorted({0, a ^ b, a ^ c, a ^ d})
        seen: set[tuple[int, ...]] = set()
        for k in range(dim):
            coset = tuple(sorted(k ^ v for v in group))
            if coset in seen:
                continue
            seen.add(coset)
            outs = sorted({a ^ q for q in coset})
            for coef in itertools.product((1, -1), repeat=3):
                m = np.zeros((4, 4), dtype=int)
                for col, q in enumerate(coset):
                    for e, cf in zip(idx, (1, *coef), strict=True):
                        m[outs.index(e ^ q), col] += cf * signs[e, q]
                out.add(normalized(m))
    return out


def compute_wide() -> dict[str, object]:
    normal = (0, 1, 2, 3, 4, 8, 12)
    every = [s for s in itertools.product((1, -1), repeat=16) if all(s[k] == 1 for k in normal)]
    all_classes = set(parallel.ordered_map(canonical, every, min_items=2))
    seen_classes: set[tuple[int, ...]] = set()
    for dim in (16, 32):
        seen_classes |= set(parallel.ordered_map(canonical, sorted(coset_blocks(dim)), min_items=2))
    record: dict[str, object] = {
        "schema": "pathion-kernel-map-census-wide-v1",
        "classes_of_all_4x4_pm1": len(all_classes),
        "spectra_of_all_4x4_pm1": sorted(spectrum(k) for k in all_classes),
    }
    seen_block_classes, seen_laws, seen_nullity = d32_two_term_state()
    for dim in WIDE_DIMS:
        operands = [(dim, (i, j, t)) for i, j in itertools.combinations(range(1, dim), 2) for t in (1, -1)]
        rows = parallel.ordered_map(two_term_wide, operands, min_items=2)
        blocks: Counter[int] = Counter()
        laws: set[tuple[tuple[int, ...], ...]] = set()
        for _, _, counts, block_laws in rows:
            blocks.update(counts)
            laws |= set(block_laws)
        nullities = Counter(r[0] for r in rows)
        record[f"d{dim}_two_term_operands"] = len(operands)
        record[f"d{dim}_nullity_equals_aligned_pairs_and_cd_core_rank"] = all(r[0] == r[1] for r in rows)
        record[f"d{dim}_two_term_nullity_counts"] = {str(k): v for k, v in sorted(nullities.items())}
        record[f"d{dim}_nullities_new"] = sorted(set(nullities) - seen_nullity)
        record[f"d{dim}_two_term_block_aligned_counts"] = {str(k): v for k, v in sorted(blocks.items())}
        record[f"d{dim}_two_term_block_classes_new"] = sorted(set(blocks) - seen_block_classes)
        record[f"d{dim}_two_term_block_law_classes"] = len(laws)
        record[f"d{dim}_two_term_block_law_classes_new"] = len(laws - seen_laws)
        seen_block_classes |= set(blocks)
        seen_laws |= laws
        seen_nullity |= set(nullities)
        normals: set[tuple[int, ...]] = set()
        for found in parallel.ordered_map(four_term_blocks_from, [(dim, a) for a in range(1, dim)], min_items=2):
            normals |= found
        classes = set(parallel.ordered_map(canonical, sorted(normals), min_items=2))
        record[f"d{dim}_four_term_normalized_blocks"] = len(normals)
        record[f"d{dim}_four_term_classes"] = len(classes)
        record[f"d{dim}_four_term_classes_new"] = sorted(spectrum(k) for k in classes - seen_classes)
        seen_classes |= classes
    record["four_term_classes_missing_after_128"] = sorted(spectrum(k) for k in all_classes - seen_classes)
    return record


def d32_two_term_state() -> tuple[set[int], set[tuple[tuple[int, ...], ...]], set[int]]:
    rows = parallel.ordered_map(
        two_term_wide,
        [(32, (i, j, t)) for i, j in itertools.combinations(range(1, 32), 2) for t in (1, -1)],
        min_items=2,
    )
    blocks: set[int] = set()
    laws: set[tuple[tuple[int, ...], ...]] = set()
    for _, _, counts, block_laws in rows:
        blocks |= set(counts)
        laws |= set(block_laws)
    return blocks, laws, {r[0] for r in rows}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--wide", action="store_true", help="the D = 64 and D = 128 censuses (census-wide.json)")
    args = ap.parse_args()
    out = WIDE_OUT if args.wide else OUT
    text = json.dumps(compute_wide() if args.wide else compute(), indent=1, sort_keys=True) + "\n"
    if args.check:
        if out.read_text() != text:
            raise SystemExit(f"{out} differs from the recomputed census")
        print("pathion kernel-map census reproduces")
        return 0
    out.write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
