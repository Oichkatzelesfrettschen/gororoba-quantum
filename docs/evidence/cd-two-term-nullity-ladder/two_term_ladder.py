"""Exact nullity of every two-term operand e_i +- e_j of the Cayley-Dickson algebras of dimension 8 to 128.

For each dimension D the script computes the rank over Q of cd_core.left_mult_matrix(D, e_i +- e_j) for 1 <= i < j < D
and both signs (python-flint fmpz_mat.rank, exact), and checks four statements:
- doubling: the nullity in dimension 2D of an operand of the first half is twice its nullity in dimension D;
- maximum: the largest two-term nullity is D/2 - 4 for D >= 16 (every two-term operand of the octonions is invertible);
- recurrence: the number of maximal-nullity operands in dimension 2D is twice the number of invertible operands in D;
- palindrome: for 0 < k < max, the numbers of operands of nullity k and of nullity max - k agree.
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


def nullity(item: tuple[int, int, int, int]) -> int:
    dim, i, j, sign = item
    a = [0] * dim
    a[i], a[j] = 1, sign
    rows = cd_core.left_mult_matrix(dim, a)
    return dim - int(flint.fmpz_mat([[int(x) for x in row] for row in rows]).rank())


def items(dim: int) -> list[tuple[int, int, int, int]]:
    return [(dim, i, j, s) for i, j in itertools.combinations(range(1, dim), 2) for s in (1, -1)]


def main() -> None:
    values: dict[int, dict[tuple[int, int, int], int]] = {}
    for dim in DIMS:
        work = items(dim)
        values[dim] = {w[1:]: n for w, n in zip(work, parallel.ordered_map(nullity, work), strict=True)}
    spectrum = {dim: dict(sorted(Counter(v.values()).items())) for dim, v in values.items()}
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
    }
    (HERE / "two_term_ladder.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(record, indent=1))


if __name__ == "__main__":
    main()
