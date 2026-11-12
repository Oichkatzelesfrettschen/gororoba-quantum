"""Levi structure and torus rank of the Lie algebra of linear symmetries of each retained quadric ideal K2.

g is the algebra of matrices A in gl_n whose derivation y_i -> sum_j A_ij y_j maps K2 into K2, over F_p. The script
computes g by a dense route independent of quadric_structure.py (the action of each matrix unit on the quadratic
monomials, projected to the quotient by K2) and then, in coordinates on a reduced echelon basis of g:

- the derived series and the center;
- the radical r = {x : kappa(x, [g, g]) = 0} for the Killing form kappa, so dim g - dim r is the dimension of a
  Levi factor;
- the ideal u = {x in r : tr(x y) = 0 for all y in g} of the trace form of the defining representation; over a field
  of characteristic 0 it is the set of nilpotent matrices of r for an algebraic g (the stabilizer of a subspace is
  algebraic), so r / u is the central torus of a reductive complement;
- a Cartan subalgebra h, the Fitting null component of ad x for one fixed element x, and the rank of the trace form
  on h. h is nilpotent and splits as torus + nilpotent matrices, the trace form vanishes on the nilpotent part and
  is non-degenerate on the torus in characteristic 0, so that rank is the rank of a maximal torus of g.

The two characterizations by forms are theorems in characteristic 0; at p near 32000 they are the reading of a
modular computation, and the record states each dimension as computed over F_p. `--write` writes
symmetry-algebra.json beside this file, `--check` recomputes and compares.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from flint import nmod_mat

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "gororoba_quantum"))

import parallel  # noqa: E402

sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import k2_hilbert  # noqa: E402
import quadric_structure  # noqa: E402

SCHEMA = "a5-quadric-symmetry-algebra/1"
RECORD = HERE / "symmetry-algebra.json"
SOURCES = list(k2_hilbert.SOURCES)
# Semisimple Lie algebras fixed by (dimension, rank) among those of rank at most 3.
LEVI_TYPES = {
    (0, 0): "0",
    (3, 1): "sl2",
    (6, 2): "sl2 + sl2",
    (8, 2): "sl3",
    (10, 2): "sp4",
    (14, 2): "g2",
    (9, 3): "sl2 + sl2 + sl2",
    (11, 3): "sl3 + sl2",
    (13, 3): "sp4 + sl2",
    (15, 3): "sl4",
    (17, 3): "g2 + sl2",
}


def _mat(rows: np.ndarray, prime: int) -> nmod_mat:
    return nmod_mat([[int(v) for v in row] for row in rows.reshape(len(rows), -1)], prime)


def _array(matrix: nmod_mat) -> np.ndarray:
    return np.array([[int(matrix[i, j]) for j in range(matrix.ncols())] for i in range(matrix.nrows())], dtype=np.int64)


def row_space(rows: np.ndarray, prime: int) -> np.ndarray:
    """The reduced echelon basis of the row space, as an array with one basis vector per row."""
    if rows.size == 0:
        return rows.reshape(0, rows.shape[-1] if rows.ndim > 1 else 0)
    reduced, rank = _mat(rows, prime).rref()
    return _array(reduced)[:rank]


def null_space(rows: np.ndarray, columns: int, prime: int) -> np.ndarray:
    """A basis of {x : rows x = 0}, one vector per row; every vector when rows is empty."""
    if rows.size == 0:
        return np.eye(columns, dtype=np.int64)
    kernel, dimension = _mat(rows, prime).nullspace()
    return _array(kernel).T[:dimension]


def stabilizer(quadrics: list[dict[tuple[int, int], int]], n: int, prime: int) -> np.ndarray:
    """A reduced echelon basis of g as an array (dim g, n, n)."""
    monomials = list(itertools.combinations_with_replacement(range(n), 2))
    column = {m: k for k, m in enumerate(monomials)}
    span = np.zeros((len(quadrics), len(monomials)), dtype=np.int64)
    for i, quadric in enumerate(quadrics):
        for m, c in quadric.items():
            span[i, column[m]] = c % prime
    basis = row_space(span, prime)
    # Linear forms that vanish exactly on K2: a vector lies in K2 iff every row of `annihilator` kills it.
    annihilator = null_space(basis, len(monomials), prime)
    equations = np.zeros((len(basis) * len(annihilator), n * n), dtype=np.int64)
    for i, j in itertools.product(range(n), range(n)):
        # The matrix unit E_ij sends y_i to y_j: a monomial y_i y_b goes to y_j y_b, once per factor y_i.
        image = np.zeros((len(basis), len(monomials)), dtype=np.int64)
        for (a, b), k in column.items():
            for factor, other in ((a, b), (b, a)):
                if factor == i:
                    target = column[(min(j, other), max(j, other))]
                    image[:, target] += basis[:, k]
        equations[:, i * n + j] = ((image % prime) @ annihilator.T % prime).reshape(-1)
    return null_space(row_space(equations, prime), n * n, prime).reshape(-1, n, n)


def _echelon(algebra: np.ndarray, prime: int) -> tuple[np.ndarray, list[int]]:
    flat = row_space(algebra.reshape(len(algebra), -1), prime)
    pivots = [int(np.flatnonzero(row)[0]) for row in flat]
    return flat, pivots


def analyze(algebra: np.ndarray, prime: int, label: str) -> dict[str, Any]:
    """The structure numbers of a matrix Lie algebra given by a basis (dim, n, n) over F_p."""
    dim, n = len(algebra), algebra.shape[1]
    flat, pivots = _echelon(algebra, prime)
    basis = flat.reshape(dim, n, n)
    # ad[k][:, l] holds the coordinates of [b_k, b_l]; coordinates on an echelon basis are the pivot entries.
    ad = np.zeros((dim, dim, dim), dtype=np.int64)
    for k, m in itertools.product(range(dim), range(dim)):
        bracket = (basis[k] @ basis[m] - basis[m] @ basis[k]) % prime
        coordinates = bracket.reshape(-1)[pivots]
        if ((coordinates @ flat - bracket.reshape(-1)) % prime).any():
            raise ValueError(f"{label}: the span is not closed under the bracket")
        ad[k][:, m] = coordinates
    killing = np.array([[int(np.trace(ad[k] @ ad[m] % prime)) % prime for m in range(dim)] for k in range(dim)])
    trace = np.array([[int(np.trace(basis[k] @ basis[m] % prime)) % prime for m in range(dim)] for k in range(dim)])

    def derived(ideal: np.ndarray) -> np.ndarray:
        brackets = [(np.tensordot(x, ad, axes=(0, 0)) % prime) @ y % prime for x, y in itertools.product(ideal, ideal)]
        return row_space(np.array(brackets, dtype=np.int64).reshape(-1, dim), prime)

    series = [np.eye(dim, dtype=np.int64)]
    while len(series[-1]) and len(series) <= dim + 1:
        nxt = derived(series[-1])
        if len(nxt) == len(series[-1]):
            break
        series.append(nxt)
    commutator = series[1] if len(series) > 1 else series[0]
    center = null_space(np.concatenate([ad[:, :, m].T for m in range(dim)]), dim, prime)
    radical = null_space(commutator @ killing % prime, dim, prime)
    nil = null_space(np.concatenate([commutator @ killing % prime, trace]), dim, prime)
    digest = hashlib.sha256(label.encode()).digest()
    weights = np.array([digest[k % 32] + 1 for k in range(dim)], dtype=np.int64)
    generic = np.tensordot(weights, ad, axes=(0, 0)) % prime
    power = np.eye(dim, dtype=np.int64)
    for _ in range(dim):
        power = power @ generic % prime
    cartan = null_space(power, dim, prime)
    brackets_in_cartan = [(np.tensordot(x, ad, axes=(0, 0)) % prime) @ y % prime for x in cartan for y in cartan]
    lower = row_space(np.array(brackets_in_cartan, dtype=np.int64).reshape(-1, dim), prime)
    torus_form = cartan @ trace % prime @ cartan.T % prime
    torus = int(_mat(torus_form, prime).rank()) if len(cartan) else 0
    central_torus = len(radical) - len(nil)
    levi = (dim - len(radical), torus - central_torus)
    return {
        "dimension": dim,
        "derived_series": [len(s) for s in series],
        "center": len(center),
        "radical": len(radical),
        "trace_form_nil_ideal": len(nil),
        "central_torus": central_torus,
        "levi_dimension": levi[0],
        "levi_rank": levi[1],
        "levi_type": LEVI_TYPES.get(levi, "undetermined by (dimension, rank)"),
        "generic_centralizer": dim - int(_mat(generic, prime).rank()),
        "cartan_dimension": len(cartan),
        "cartan_derived_dimension": len(lower),
        "torus_rank": torus,
    }


def structure(source: tuple[str, int, int, str]) -> dict[str, Any]:
    fiber, prime, n, relations = source
    path = k2_hilbert.W / relations
    quadrics = quadric_structure.parse(path.read_text(encoding="utf-8"), n, prime)
    algebra = stabilizer(quadrics, n, prime)
    # Control: the same number of quadrics with coefficients from a fixed hash stream keeps only the Euler field.
    stream = hashlib.shake_256(f"{fiber}|{prime}|control".encode()).digest(4 * len(quadrics) * n * (n + 1) // 2)
    monomials = list(itertools.combinations_with_replacement(range(n), 2))
    control = [
        {m: int.from_bytes(stream[4 * (i * len(monomials) + k) :][:4], "big") % prime for k, m in enumerate(monomials)}
        for i in range(len(quadrics))
    ]
    return {
        "fiber": fiber,
        "prime": prime,
        "generators": n,
        "relations": relations,
        "relations_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "quadrics": len(row_space(_span(quadrics, n, prime), prime)),
        "algebra": analyze(algebra, prime, fiber),
        "control_stabilizer_dimension": len(stabilizer(control, n, prime)),
    }


def _span(quadrics: list[dict[tuple[int, int], int]], n: int, prime: int) -> np.ndarray:
    monomials = list(itertools.combinations_with_replacement(range(n), 2))
    column = {m: k for k, m in enumerate(monomials)}
    span = np.zeros((len(quadrics), len(monomials)), dtype=np.int64)
    for i, quadric in enumerate(quadrics):
        for m, c in quadric.items():
            span[i, column[m]] = c % prime
    return span


def compute() -> list[dict[str, Any]]:
    return parallel.ordered_map(structure, SOURCES, min_items=2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = json.dumps({"schema": SCHEMA, "rows": compute()}, indent=1, sort_keys=True) + "\n"
    if args.write:
        RECORD.write_text(text, encoding="utf-8")
    elif RECORD.read_text(encoding="utf-8") != text:
        raise SystemExit(f"{RECORD.name} differs from the recomputation")
    print(text, end="")


if __name__ == "__main__":
    main()
