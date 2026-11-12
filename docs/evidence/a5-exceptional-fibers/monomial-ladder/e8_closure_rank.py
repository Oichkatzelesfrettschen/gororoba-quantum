"""Rank of the k-span of the E8-bar generators in I S / (m_R S) I S, from the normal forms of a Singular log.

`records/e8-ideal-closure-*.sing` computes, in S = (P + P b) localized at 1 + w, the relation module of
I S / (m_R S) I S on the 21 generators G_j and prints the normal form of each unit vector e_j as lines
`RESULT nf_j_i POLY`. I S / (m_R S) I S has dimension 21 (the `vdim` line of the log), so the generators span it over
k exactly when the 21 normal forms are linearly independent over k. Then I + m_R (I S) = I S, and Nakayama's lemma
over the local ring R, over which S = R + w R is finite, gives I = I S.

    $PYTHON docs/evidence/a5-exceptional-fibers/monomial-ladder/e8_closure_rank.py LOG PRIME
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import sympy
from flint import nmod_mat

NAMES = sympy.symbols("qw qr qs qz qa qb qu")


def rank(log: Path, prime: int) -> dict[str, int]:
    rows: dict[int, dict[int, int]] = {}
    columns: dict[tuple[int, tuple[int, ...]], int] = {}
    for line in log.read_text(encoding="utf-8").splitlines():
        match = re.match(r"RESULT nf_(\d+)_(\d+) (.*)", line)
        if not match:
            continue
        j, i = int(match[1]), int(match[2])
        poly = sympy.Poly(sympy.parse_expr(match[3].replace("^", "**")), *NAMES)
        for exponents, coefficient in poly.terms():
            column = columns.setdefault((i, tuple(int(e) for e in exponents)), len(columns))
            rows.setdefault(j, {})[column] = int(coefficient) % prime
    count = max(rows)
    matrix = nmod_mat(count, len(columns), prime)
    for j, row in rows.items():
        for column, value in row.items():
            matrix[j - 1, column] = value
    return {"generators": count, "columns": len(columns), "rank": int(matrix.rank())}


if __name__ == "__main__":
    print(json.dumps(rank(Path(sys.argv[1]), int(sys.argv[2]))))
