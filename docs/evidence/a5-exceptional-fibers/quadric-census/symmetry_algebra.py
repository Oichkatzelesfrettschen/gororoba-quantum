"""Levi structure and torus rank of the Lie algebra of linear symmetries of each retained quadric ideal K2.

g is the algebra of matrices A in gl_n whose derivation y_i -> sum_j A_ij y_j maps K2 into K2, over F_p. The script
computes g by a dense route independent of quadric_structure.py (the action of each matrix unit on the quadratic
monomials, projected to the quotient by K2) and then, in coordinates on a reduced echelon basis of g:

- the derived series and the center;
- r = {x : kappa(x, [g, g]) = 0} for the Killing form kappa, with three checks that hold over F_p without any
  criterion: r is an ideal, its derived series reaches 0, [g, g] + r = g, and, when g / r has dimension 3, three
  elements h, e, f of g / r with [h, e] = 2e, [h, f] = -2f and [e, f] = h, found and verified in coordinates. The
  triple spans g / r, so g / r is sl2 over F_p, and a solvable ideal with simple quotient is the radical;
- u = {x in r : tr(x y) = 0 for all y in g}, the trace form of the defining representation, with the checks that u
  is an ideal and its lower central series reaches 0 (a nilpotent ideal);
- h, the Fitting null component of ad x for one fixed element x, with the checks that h is abelian and that each
  basis matrix is annihilated by the squarefree part of its characteristic polynomial. Commuting semisimple
  matrices are simultaneously diagonalizable over the algebraic closure, so h is then a toral subalgebra. The rank
  of the trace form on h is recorded beside dim h; the two agree on every retained file, which torality alone
  does not force over F_p (the span of diag(1, i), i^2 = -1, is toral with trace form 0);
- for a fiber with retained component ideals, the restriction of h to the linear subspace cut out by the linear
  forms among the generators of each component ideal.

Every statement of the record is a statement about the Lie algebra over F_p. The reading in characteristic 0 (a Levi
factor, a maximal torus of the symmetry group, a torus action on the cone) is a hypothesis the record does not test:
it needs the same computation over Q(i). The relation files are read by `quadric_structure.parse`, so the two
stabilizer constructions share their parser. `--write` writes symmetry-algebra.json beside this file, `--check`
recomputes and compares.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import sys
from collections.abc import Callable
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
# Retained ideals of the irreducible components of V(K2), in the coordinates of the relation file, with the
# dimension of each cone: (fiber, prime) -> component -> (path under the fiber evidence directory, dimension).
COMPONENTS = {
    ("W8 -> N-", 32009): {
        "C20": ("structure/w8-kp/P-p32009.txt", 6),
        "C30": ("structure/w8-kp/quotient.txt", 6),
    },
}
LINEAR_TERM = re.compile(r"([+-]?)(?:(\d+)\*)?y\((\d+)\)")
LINEAR_FORM = re.compile(r"(?:[+-]?(?:\d+\*)?y\(\d+\))(?:[+-](?:\d+\*)?y\(\d+\))*")
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


def bracket_span(left: np.ndarray, right: np.ndarray, ad: np.ndarray, prime: int) -> np.ndarray:
    """The span of the brackets [x, y], x in `left`, y in `right`, in coordinates; ad[k][:, l] holds [b_k, b_l]."""
    dim = ad.shape[0]
    brackets = [(np.tensordot(x, ad, axes=(0, 0)) % prime) @ y % prime for x, y in itertools.product(left, right)]
    return row_space(np.array(brackets, dtype=np.int64).reshape(-1, dim), prime)


def is_ideal(subspace: np.ndarray, ad: np.ndarray, prime: int) -> bool:
    """Whether [g, subspace] lies in the subspace."""
    whole = np.eye(ad.shape[0], dtype=np.int64)
    return len(row_space(np.concatenate([subspace, bracket_span(whole, subspace, ad, prime)]), prime)) == len(subspace)


def reaches_zero(subspace: np.ndarray, step: Callable[[np.ndarray], np.ndarray]) -> bool:
    """Whether iterating `step` from the subspace reaches 0 within dim + 1 steps."""
    current = subspace
    for _ in range(subspace.shape[1] + 1):
        if not len(current):
            return True
        current = step(current)
    return not len(current)


def sums_to_whole(left: np.ndarray, right: np.ndarray, prime: int) -> bool:
    """Whether the two subspaces together span the ambient space."""
    return len(row_space(np.concatenate([left, right]), prime)) == left.shape[1]


def quotient_has_sl2_triple(ad: np.ndarray, ideal: np.ndarray, prime: int) -> bool:
    """Whether g / ideal has dimension 3 and holds h, e, f with [h, e] = 2e, [h, f] = -2f, [e, f] = h.

    A class is written on the basis vectors at the non-pivot columns of the reduced echelon basis of the ideal,
    and the search runs over x with small integer coordinates whose ad on the quotient has eigenvalues 0, a, -a
    in F_p.
    """
    dim = ad.shape[0]
    ideal = row_space(ideal, prime) if len(ideal) else ideal
    pivots = [int(np.flatnonzero(row)[0]) for row in ideal]
    free = [k for k in range(dim) if k not in pivots]
    if len(free) != 3:
        return False

    def classes(vector: np.ndarray) -> np.ndarray:
        reduced = (vector - vector[pivots] @ ideal) % prime if len(ideal) else vector % prime
        return reduced[free]

    # table[a][:, b] holds the class of [c_a, c_b].
    table = np.array([[classes(ad[a][:, b]) for b in free] for a in free], dtype=np.int64).transpose(0, 2, 1)
    roots = {value * value % prime: value for value in range(1, prime)}
    for weights in itertools.product(range(-2, 3), repeat=3):
        x = np.array(weights, dtype=np.int64) % prime
        operator = np.tensordot(x, table, axes=(0, 0)) % prime
        square = int(np.trace(operator @ operator % prime)) * pow(2, -1, prime) % prime
        if square not in roots:
            continue
        h = x * (2 * pow(roots[square], -1, prime)) % prime
        ad_h = np.tensordot(h, table, axes=(0, 0)) % prime
        up = null_space((ad_h - 2 * np.eye(3, dtype=np.int64)) % prime, 3, prime)
        down = null_space((ad_h + 2 * np.eye(3, dtype=np.int64)) % prime, 3, prime)
        if len(up) != 1 or len(down) != 1:
            continue
        e, f = up[0], down[0]
        bracket = (np.tensordot(e, table, axes=(0, 0)) % prime) @ f % prime
        support = np.flatnonzero(h)
        scale = int(bracket[support[0]]) * pow(int(h[support[0]]), -1, prime) % prime
        if not scale or ((bracket - scale * h) % prime).any():
            continue
        f = f * pow(scale, -1, prime) % prime
        relations = [
            ((ad_h @ e - 2 * e) % prime).any(),
            ((ad_h @ f + 2 * f) % prime).any(),
            (((np.tensordot(e, table, axes=(0, 0)) % prime) @ f - h) % prime).any(),
        ]
        if not any(relations) and len(row_space(np.array([h, e, f]), prime)) == 3:
            return True
    return False


def analyze(algebra: np.ndarray, prime: int, label: str) -> dict[str, Any]:
    """The structure numbers of a matrix Lie algebra given by a basis (dim, n, n) over F_p."""
    return decompose(algebra, prime, label)[0]


def decompose(algebra: np.ndarray, prime: int, label: str) -> tuple[dict[str, Any], np.ndarray]:
    """The structure numbers and the matrices (rank, n, n) of a basis of the Cartan subalgebra."""
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

    def product(left: np.ndarray, right: np.ndarray) -> np.ndarray:
        return bracket_span(left, right, ad, prime)

    def derived(ideal: np.ndarray) -> np.ndarray:
        return product(ideal, ideal)

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
    lower = product(cartan, cartan)
    torus_form = cartan @ trace % prime @ cartan.T % prime
    torus = int(_mat(torus_form, prime).rank()) if len(cartan) else 0
    central_torus = len(radical) - len(nil)
    # Facts over F_p that need no form criterion: the radical is a solvable ideal with quotient sl2, the nil
    # ideal is a nilpotent ideal, and the Cartan subalgebra is spanned by commuting semisimple matrices.
    perfect_quotient = sums_to_whole(commutator, radical, prime)
    cartan_matrices = (cartan @ flat % prime).reshape(len(cartan), n, n)
    levi = (dim - len(radical), torus - central_torus)
    numbers = {
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
        "radical_is_solvable_ideal": is_ideal(radical, ad, prime) and reaches_zero(radical, derived),
        "quotient_by_radical_is_perfect": perfect_quotient,
        "quotient_by_radical_has_sl2_triple": quotient_has_sl2_triple(ad, radical, prime),
        "nil_ideal_is_nilpotent_ideal": (
            is_ideal(nil, ad, prime) and reaches_zero(nil, lambda current: product(nil, current))
        ),
        "cartan_is_toral": not len(lower) and all(is_semisimple(matrix, prime) for matrix in cartan_matrices),
    }
    return numbers, cartan_matrices


def is_semisimple(matrix: np.ndarray, prime: int) -> bool:
    """Whether the squarefree part of the characteristic polynomial annihilates the matrix; needs size below p.

    chi / gcd(chi, chi') is the squarefree part only when every root multiplicity is below p.
    """
    if len(matrix) >= prime:
        raise ValueError(f"matrix size {len(matrix)} is not below the prime {prime}")
    poly = _mat(matrix, prime).charpoly()
    squarefree = poly // poly.gcd(poly.derivative())
    value = np.zeros_like(matrix)
    identity = np.eye(len(matrix), dtype=np.int64)
    for coefficient in reversed([int(c) for c in squarefree.coeffs()]):
        value = (value @ matrix + coefficient * identity) % prime
    return not value.any()


def linear_forms(text: str, n: int, prime: int) -> np.ndarray:
    """The generators of degree 1 of a Singular ideal string, as rows of coefficients on y(1..n).

    A generator counts when it is a sum of terms `c*y(i)` or `y(i)` in Singular's printed form; every other
    generator, a constant or a product included, is skipped.
    """
    rows = []
    for poly in text.strip().rstrip(";").replace(" ", "").replace("\n", "").split(","):
        if not LINEAR_FORM.fullmatch(poly):
            continue
        row = np.zeros(n, dtype=np.int64)
        for sign, number, index in LINEAR_TERM.findall(poly):
            if not 1 <= int(index) <= n:
                raise ValueError(f"y({index}) lies outside y(1..{n})")
            row[int(index) - 1] += (-1 if sign == "-" else 1) * int(number or 1)
        rows.append(row % prime)
    return row_space(np.array(rows, dtype=np.int64).reshape(-1, n), prime)


def restricted_torus(cartan: np.ndarray, forms: np.ndarray, prime: int) -> dict[str, Any]:
    """The matrices `cartan` on the linear subspace W cut out by `forms`: whether they preserve W, and their rank on W.

    A matrix A acts on a linear form c by c -> c A and on a point x by x -> A x. W is preserved when forms A x = 0
    for every x in W, and the rank of the torus on W is the dimension of the span of the restrictions A|W.
    """
    n = forms.shape[1]
    points = null_space(forms, n, prime).T
    restrictions = np.array([a @ points % prime for a in cartan], dtype=np.int64)
    preserved = not any((forms @ r % prime).any() for r in restrictions)
    return {
        "linear_forms": len(forms),
        "span_dimension": points.shape[1],
        "span_preserved": preserved,
        "torus_rank_on_span": len(row_space(restrictions.reshape(len(cartan), -1), prime)),
    }


def structure(source: tuple[str, int, int, str]) -> dict[str, Any]:
    fiber, prime, n, relations = source
    path = k2_hilbert.W / relations
    quadrics = quadric_structure.parse(path.read_text(encoding="utf-8"), n, prime)
    algebra = stabilizer(quadrics, n, prime)
    numbers, cartan = decompose(algebra, prime, fiber)
    components = {}
    for name, (relative, dimension) in COMPONENTS.get((fiber, prime), {}).items():
        ideal = HERE.parent / relative
        row = restricted_torus(cartan, linear_forms(ideal.read_text(encoding="utf-8"), n, prime), prime)
        row.update(
            ideal=relative,
            ideal_sha256=hashlib.sha256(ideal.read_bytes()).hexdigest(),
            dimension=dimension,
            dimension_minus_torus_rank_on_span=dimension - row["torus_rank_on_span"],
        )
        components[name] = row
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
        "algebra": numbers,
        "components": components,
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
