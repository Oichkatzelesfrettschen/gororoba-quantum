"""Exact nullity of every two-term operand e_i +- e_j of the Cayley-Dickson algebras of dimension 8 to 128.

For each dimension D the script computes the rank over Q of cd_core.left_mult_matrix(D, e_i +- e_j) for 1 <= i < j < D
and both signs (python-flint fmpz_mat.rank, exact), and checks four statements:
- doubling: the nullity in dimension 2D of an operand of the first half is twice its nullity in dimension D;
- maximum: the largest two-term nullity is D/2 - 4 for D >= 16 (every two-term operand of the octonions is invertible);
- recurrence: the number of maximal-nullity operands in dimension 2D is twice the number of invertible operands in D;
- palindrome: for 0 < k < max, the numbers of operands of nullity k and of nullity max - k agree;
- fold: every two-term nullity in dimension D follows from the octonions (all invertible) by the recursion of fold():
  an operand inside one half has twice the nullity of its image one level down (0 when it contains the half's unit),
  and a cross operand e_i +- e_(h+j), h = D/2, has nullity h - 4 - 2 n_h(e_i +- e_j) for distinct nonzero i, j and 0
  otherwise. The script compares fold() with the exact rank of every two-term operand up to dimension 256.
Output: two_term_ladder.json beside this script (the spectrum per dimension and each statement's verdict).
"""

import itertools
import json
import sys
from collections import Counter
from pathlib import Path

import flint

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "gororoba_quantum"))
import cd_core  # noqa: E402
import parallel  # noqa: E402

DIMS = (8, 16, 32, 64, 128)
FOLD_DIMS = (*DIMS, 256)


def nullity(item: tuple[int, int, int, int]) -> int:
    dim, i, j, sign = item
    a = [0] * dim
    a[i], a[j] = 1, sign
    rows = cd_core.left_mult_matrix(dim, a)
    return dim - int(flint.fmpz_mat([[int(x) for x in row] for row in rows]).rank())


def fold(dim: int, i: int, j: int, sign: int) -> int:
    """Two-term nullity of e_i + sign e_j (i < j) predicted from the octonions, with no matrix."""
    if dim == 8:
        return 0
    h = dim // 2
    if j < h:
        return 2 * fold(h, i, j, sign) if i > 0 else 0
    if i >= h:
        return 2 * fold(h, i - h, j - h, sign) if i > h else 0
    a, b = i, j - h
    if a == 0 or b == 0 or a == b:
        return 0
    return h - 4 - 2 * fold(h, min(a, b), max(a, b), sign)


def items(dim: int) -> list[tuple[int, int, int, int]]:
    return [(dim, i, j, s) for i, j in itertools.combinations(range(1, dim), 2) for s in (1, -1)]


def main() -> None:
    values: dict[int, dict[tuple[int, int, int], int]] = {}
    for dim in DIMS:
        work = items(dim)
        values[dim] = {w[1:]: n for w, n in zip(work, parallel.ordered_map(nullity, work), strict=True)}
    work = items(256)
    values[256] = {w[1:]: n for w, n in zip(work, parallel.ordered_map(nullity, work), strict=True)}
    fold_violations = {
        str(dim): sum(fold(dim, i, j, s) != n for (i, j, s), n in values[dim].items()) for dim in FOLD_DIMS
    }
    spectrum = {dim: dict(sorted(Counter(v.values()).items())) for dim, v in values.items() if dim in DIMS}
    doubling = {
        f"{dim}->{2 * dim}": sum(values[2 * dim][key] != 2 * n for key, n in values[dim].items()) for dim in DIMS[:-1]
    }
    maximum = {dim: (max(s), dim // 2 - 4) for dim, s in spectrum.items() if dim >= 16}
    recurrence = {
        f"{dim}->{2 * dim}": (spectrum[2 * dim][max(spectrum[2 * dim])], 2 * spectrum[dim].get(0, 0))
        for dim in DIMS[:-1]
    }
    palindrome = {
        dim: all(s.get(k, 0) == s.get(max(s) - k, 0) for k in s if 0 < k < max(s)) for dim, s in spectrum.items()
    }
    record = {
        "method": "rank over Q of cd_core.left_mult_matrix by python-flint fmpz_mat.rank",
        "spectrum": {str(d): {str(k): c for k, c in s.items()} for d, s in spectrum.items()},
        "doubling_violations": doubling,
        "maximum_vs_D_over_2_minus_4": {str(d): list(v) for d, v in maximum.items()},
        "recurrence_max_count_vs_twice_invertible": {k: list(v) for k, v in recurrence.items()},
        "palindrome": {str(d): v for d, v in palindrome.items()},
        "fold_violations_against_exact_rank": fold_violations,
    }
    (HERE / "two_term_ladder.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(record, indent=1))


if __name__ == "__main__":
    main()
