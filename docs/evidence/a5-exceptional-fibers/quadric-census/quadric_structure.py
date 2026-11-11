"""Term structure and linear symmetries of the retained quadric ideals K2, in the header's coordinates y.

For each fiber the script reads the retained quadrics K2 over F_p and reports

- the support sizes of the reduced row echelon basis of K2 on the quadratic monomials: a basis of monomials and
  binomials (supports 1 and 2) is the form a toric or monomial-binomial presentation takes in these coordinates, and
  larger supports show that K2 is not binomial in the coordinates y (a statement about these coordinates only);
- the Lie algebra g of matrices A in gl_n whose derivation y_i -> sum_j A_ij y_j maps K2 into K2: its dimension, the
  dimension of its diagonal part (the torus of rescalings y_i -> c_i y_i that preserves K2), and the dimension of the
  centralizer of a fixed pseudo-random element of g. The diagonal torus has dimension at least 1 (the Euler field);
  a toric variety of dimension d embedded by monomials has a diagonal torus of dimension at least d.

    $PYTHON docs/evidence/a5-exceptional-fibers/quadric-census/quadric_structure.py OUT.json
"""

from __future__ import annotations

import hashlib
import itertools
import json
import re
import sys
from pathlib import Path
from typing import Any

from flint import nmod_mat

HERE = Path(__file__).resolve().parent
WORKING = HERE.parent / "working"
sys.path.insert(0, str(HERE.parents[3] / "gororoba_quantum"))

import parallel  # noqa: E402

PRIME = 32009
# (fiber, number of generators, relation file under working/)
SOURCES = [
    ("X- -> N-", 15, "distribute/out/a5-xm-d4/xm_p1/d2/relations-upto-d2.rel"),
    ("E8-bar -> VB", 10, "runs/e8vb_a2/k2.rel"),
    ("Iso", 17, "distribute/out/a5-iso-d4/iso_p1/d2/relations-upto-d2.rel"),
    ("E8-bar -> N-", 21, "distribute/out/a5-e8-d2/e8nm_p1/d2/relations-upto-d2.rel"),
    ("W8 -> N-", 24, "runs/w8_a2/w8_k2.rel"),
]
TERM = re.compile(r"([+-]?)(\d*)\*?((?:y\(\d+\)(?:\^\d+)?\*?)+)")


def parse(text: str, n: int) -> list[dict[tuple[int, int], int]]:
    """The quadrics of a Singular ideal string as {(i, j): coefficient}, i <= j."""
    out = []
    for poly in text.strip().rstrip(";").split(","):
        terms: dict[tuple[int, int], int] = {}
        for sign, number, monomial in TERM.findall(poly.replace(" ", "").replace("\n", "")):
            indices: list[int] = []
            for index, power in re.findall(r"y\((\d+)\)(?:\^(\d+))?", monomial):
                indices += [int(index) - 1] * int(power or 1)
            if len(indices) != 2 or max(indices) >= n:
                raise ValueError(f"not a quadric term: {monomial}")
            key = (min(indices), max(indices))
            terms[key] = (terms.get(key, 0) + (-1 if sign == "-" else 1) * int(number or 1)) % PRIME
        out.append(terms)
    return out


def structure(source: tuple[str, int, str]) -> dict[str, Any]:
    fiber, n, relations = source
    path = WORKING / relations
    quadrics = parse(path.read_text(encoding="utf-8"), n)
    monomials = list(itertools.combinations_with_replacement(range(n), 2))
    column = {m: k for k, m in enumerate(monomials)}
    matrix = nmod_mat(len(quadrics), len(monomials), PRIME)
    for i, q in enumerate(quadrics):
        for m, c in q.items():
            matrix[i, column[m]] = c
    reduced, rank = matrix.rref()
    basis = [{k: int(reduced[i, k]) for k in range(len(monomials)) if int(reduced[i, k])} for i in range(rank)]
    supports: dict[str, int] = {}
    for row in basis:
        supports[str(len(row))] = supports.get(str(len(row)), 0) + 1
    pivots = [min(row) for row in basis]
    free = [k for k in range(len(monomials)) if k not in set(pivots)]
    position = {k: i for i, k in enumerate(free)}

    def normal_form(vector: dict[int, int]) -> dict[int, int]:
        out: dict[int, int] = {}
        for k, c in vector.items():
            if k in position:
                out[k] = (out.get(k, 0) + c) % PRIME
            else:
                for kk, cc in basis[pivots.index(k)].items():
                    if kk != k:
                        out[kk] = (out.get(kk, 0) - c * cc) % PRIME
        return out

    # Unknowns A[i][j]; the derivation sends y_a y_b to sum_j A[a][j] y_j y_b + A[b][j] y_a y_j.
    rows: list[dict[int, int]] = []
    for q in basis:
        images: dict[int, dict[int, int]] = {}
        for k, c in q.items():
            a, b = monomials[k]
            for source_index, other in ((a, b), (b, a)):
                for j in range(n):
                    target = column[(min(j, other), max(j, other))]
                    images.setdefault(source_index * n + j, {})
                    images[source_index * n + j][target] = (images[source_index * n + j].get(target, 0) + c) % PRIME
        equations: dict[int, dict[int, int]] = {}
        for unknown, image in images.items():
            for k, c in normal_form(image).items():
                if c:
                    equations.setdefault(k, {})[unknown] = c
        rows.extend(equations.values())
    system = nmod_mat(len(rows), n * n, PRIME)
    for i, row in enumerate(rows):
        for unknown, c in row.items():
            system[i, unknown] = c
    kernel, dimension = system.nullspace()
    algebra = [[[int(kernel[i * n + j, k]) for j in range(n)] for i in range(n)] for k in range(dimension)]
    diagonal = nmod_mat([[row.get(i * n + i, 0) for i in range(n)] for row in rows] or [[0] * n], PRIME)
    # Restricting the system to diagonal unknowns is exact: a diagonal A solves it iff its diagonal entries do.
    torus = n - int(diagonal.rank())
    digest = hashlib.sha256(fiber.encode()).digest()
    weights = [digest[k % 32] + 1 for k in range(dimension)]
    generic = [
        [sum(w * a[i][j] for w, a in zip(weights, algebra, strict=True)) % PRIME for j in range(n)] for i in range(n)
    ]

    def bracket(x: list[list[int]], y: list[list[int]]) -> list[int]:
        return [
            (sum(x[i][k] * y[k][j] - y[i][k] * x[k][j] for k in range(n))) % PRIME for i in range(n) for j in range(n)
        ]

    brackets = nmod_mat([bracket(generic, a) for a in algebra], PRIME) if dimension else None
    return {
        "fiber": fiber,
        "prime": PRIME,
        "generators": n,
        "quadrics": int(rank),
        "relations_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "echelon_support_sizes": dict(sorted(supports.items(), key=lambda kv: int(kv[0]))),
        "monomial_and_binomial_basis": all(int(s) <= 2 for s in supports),
        "symmetry_algebra_dimension": int(dimension),
        "diagonal_torus_dimension": torus,
        "generic_centralizer_dimension": int(dimension - brackets.rank()) if brackets is not None else 0,
    }


def main() -> None:
    rows = parallel.ordered_map(structure, SOURCES, min_items=2)
    Path(sys.argv[1]).write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    for r in rows:
        print(json.dumps(r))


if __name__ == "__main__":
    main()
