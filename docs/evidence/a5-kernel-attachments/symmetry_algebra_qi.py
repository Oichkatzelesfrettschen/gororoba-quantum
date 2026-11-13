"""The Lie algebra of linear symmetries of the fiber-cone quadrics over Q(i): dimension, radical, Levi factor, torus.

For each incidence from a nullity-8 source into N+ or N- whose fiber cone has quadric relations (W8, E8bar, Iso and
same-sign X, eight cells), `weight_slice_fiber_relations` regenerates the quadrics K over Q(i) and this script checks
their digest against the retained record. g is the algebra of matrices A in gl_n(Q(i)) whose derivation
y_i -> sum_j A_ij y_j maps K into K. In characteristic 0 the stabilizer of K in GL_n is a smooth group scheme, so g is
its Lie algebra, and a Cartan subalgebra of g is the Lie algebra of a Cartan subgroup.

Exact route. With B the reduced echelon basis of K on the quadratic monomials and Ann the basis of the forms that
vanish on K built from the free columns of B, the condition on A is the linear system E vec(A) = 0 with one row per
pair (basis quadric, annihilating form). The system is formed modulo 32009 with i sent to 10754, a set of rows that
spans its row space there is selected, and only those rows are formed over Q(i). Their null space N contains g. Every
basis matrix of N is then applied to every basis quadric and reduced modulo B exactly, which puts N inside g, so
g = N whatever the modular selection did; a selection that loses rank shows as a matrix that fails this test.

Linear algebra over Q(i) runs on pairs of rational matrices. The reduced echelon form of a matrix with rows v comes
from the rational echelon form of the rows v and i v written on interleaved real and imaginary coordinates: the row
space is stable under multiplication by i, so the rational pivots come in pairs and the row with pivot on a real
coordinate is the row of the echelon form over Q(i).

On a reduced echelon basis of g the script computes, exactly over Q(i), the quantities of the modular record
`../a5-exceptional-fibers/quadric-census/symmetry_algebra.py` by the same definitions: the derived series and the
center; r = {x : kappa(x, [g, g]) = 0} with the checks that r is an ideal whose derived series reaches 0 and that
[g, g] + r = g, which make r the radical when g / r is simple; three elements h, e, f of a 3-dimensional g / r with
[h, e] = 2e, [h, f] = -2f and [e, f] = h, which make g / r the split algebra sl2 over Q(i); u = {x in r : tr(x y) = 0
for all y in g} with the checks that it is an ideal whose lower central series reaches 0; and h, the Fitting null
component of ad x for one fixed x, with the checks that it is abelian and that each basis matrix has a squarefree
minimal polynomial (tested on the rational matrix of twice the size, whose minimal polynomial is squarefree exactly
when the one over Q(i) is).

Each cell also records three comparisons. The basis of g reduced at (32009, i -> 10754) is passed to the modular
`decompose`, and the stabilizer of the reduced quadrics is recomputed by the modular `stabilizer`: equal numbers and
equal dimension show that the modular record of this cell is the reduction of the exact one. The diagonal matrix of
the torus weights of the generators must lie in g, since K is weight-homogeneous. The same number of quadrics with
integer coefficients from a fixed hash stream must keep the Euler field alone: its stabilizer modulo 32009 has
dimension 1, the dimension over Q(i) is at most the modular one, and the Euler field stabilizes every homogeneous
ideal.

`--write` writes symmetry-algebra-qi-result.json beside this file and `--check` recomputes and compares. Both need
Singular 4.4 on PATH for the regeneration of the quadrics.

Run from the repository root: "$PYTHON" docs/evidence/a5-kernel-attachments/symmetry_algebra_qi.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from collections.abc import Callable, Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
from flint import fmpq, fmpq_mat, fmpz_mat, nmod_mat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CENSUS = HERE.parent / "a5-exceptional-fibers" / "quadric-census"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(CENSUS.parent))
sys.path.insert(0, str(CENSUS))

import symmetry_algebra as modular  # noqa: E402
import weight_slice_fiber_relations as ws  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-attachments-symmetry-algebra-qi-v1"
RECORD = HERE / "symmetry-algebra-qi-result.json"
RELATIONS_RECORD = HERE / "weight-slice-fiber-relations-result.json"
PRIME = ws.MODULAR_PRIME
I_ROOT = ws.MODULAR_ROOT
# The cells whose fiber cone has quadric relations; the opposite-sign X cells have none (their cone is the plane).
CELLS = tuple((orbit, source) for orbit in ws.ORBITS for source in ws.SOURCES if ws.EXPECTED_COUNTS[(orbit, source)][1])
SOURCE_PATHS = (HERE / "symmetry_algebra_qi.py", CENSUS / "symmetry_algebra.py")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


# ---------------------------------------------------------------------------------------------------------------------
# Scalars and matrices over Q(i)


class Gauss:
    """An element re + im i of Q(i)."""

    __slots__ = ("im", "re")

    def __init__(self, re: Any = 0, im: Any = 0) -> None:
        self.re = re if isinstance(re, fmpq) else _q(re)
        self.im = im if isinstance(im, fmpq) else _q(im)

    def __add__(self, other: Gauss) -> Gauss:
        return Gauss(self.re + other.re, self.im + other.im)

    def __sub__(self, other: Gauss) -> Gauss:
        return Gauss(self.re - other.re, self.im - other.im)

    def __neg__(self) -> Gauss:
        return Gauss(-self.re, -self.im)

    def __mul__(self, other: Gauss) -> Gauss:
        return Gauss(self.re * other.re - self.im * other.im, self.re * other.im + self.im * other.re)

    def inverse(self) -> Gauss:
        norm = self.re * self.re + self.im * self.im
        _require(norm != 0, "division by zero in Q(i)")
        return Gauss(self.re / norm, -self.im / norm)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Gauss) and self.re == other.re and self.im == other.im

    def __hash__(self) -> int:
        return hash((str(self.re), str(self.im)))

    def __bool__(self) -> bool:
        return bool(self.re != 0 or self.im != 0)

    def __repr__(self) -> str:
        return f"Gauss({self.re}, {self.im})"

    def reduce(self, prime: int, root: int) -> int:
        """The image under Z[i] localized at (prime, i - root) -> F_prime."""
        return (_reduce(self.re, prime) + _reduce(self.im, prime) * root) % prime


def _q(value: Any) -> fmpq:
    if isinstance(value, Fraction):
        return fmpq(value.numerator, value.denominator)
    return fmpq(value)


def _reduce(value: fmpq, prime: int) -> int:
    denominator = int(value.q) % prime
    _require(denominator != 0, f"a denominator is divisible by {prime}")
    return int(value.p) % prime * pow(denominator, -1, prime) % prime


def _rational_sqrt(value: fmpq) -> fmpq | None:
    numerator, denominator = int(value.p), int(value.q)
    if numerator < 0:
        return None
    roots = math.isqrt(numerator), math.isqrt(denominator)
    return fmpq(roots[0], roots[1]) if (roots[0] ** 2, roots[1] ** 2) == (numerator, denominator) else None


def gauss_sqrt(value: Gauss) -> Gauss | None:
    """A square root in Q(i), or None when the element is no square there."""
    if value.im == 0:
        real = _rational_sqrt(value.re)
        if real is not None:
            return Gauss(real, 0)
        imaginary = _rational_sqrt(-value.re)
        return None if imaginary is None else Gauss(0, imaginary)
    # (u + v i)^2 = re + im i with u v != 0 forces u^2 = (re + |value|) / 2 and v = im / (2 u).
    modulus = _rational_sqrt(value.re * value.re + value.im * value.im)
    if modulus is None:
        return None
    real = _rational_sqrt((value.re + modulus) / 2)
    return None if real is None else Gauss(real, value.im / (2 * real))


ZERO = Gauss(0, 0)
ONE = Gauss(1, 0)
Rows = list[list[Gauss]]


class CMat:
    """A matrix over Q(i) as a pair of rational matrices."""

    __slots__ = ("im", "re")

    def __init__(self, re: fmpq_mat, im: fmpq_mat) -> None:
        self.re, self.im = re, im

    @classmethod
    def from_rows(cls, rows: Rows, columns: int) -> CMat:
        flat = [entry for row in rows for entry in row]
        _require(len(flat) == len(rows) * columns, "ragged rows")
        return cls(
            fmpq_mat(len(rows), columns, [entry.re for entry in flat]),
            fmpq_mat(len(rows), columns, [entry.im for entry in flat]),
        )

    @classmethod
    def identity(cls, size: int) -> CMat:
        return cls.from_rows([[ONE if i == j else ZERO for j in range(size)] for i in range(size)], size)

    @property
    def shape(self) -> tuple[int, int]:
        return int(self.re.nrows()), int(self.re.ncols())

    def rows(self) -> Rows:
        height, width = self.shape
        return [[Gauss(self.re[i, j], self.im[i, j]) for j in range(width)] for i in range(height)]

    def __add__(self, other: CMat) -> CMat:
        return CMat(self.re + other.re, self.im + other.im)

    def __sub__(self, other: CMat) -> CMat:
        return CMat(self.re - other.re, self.im - other.im)

    def __matmul__(self, other: CMat) -> CMat:
        return CMat(self.re * other.re - self.im * other.im, self.re * other.im + self.im * other.re)

    def scale(self, factor: Gauss) -> CMat:
        return CMat(self.re * factor.re - self.im * factor.im, self.re * factor.im + self.im * factor.re)

    def transpose(self) -> CMat:
        return CMat(self.re.transpose(), self.im.transpose())

    def trace(self) -> Gauss:
        size = self.shape[0]
        return Gauss(
            sum((self.re[k, k] for k in range(size)), fmpq(0)), sum((self.im[k, k] for k in range(size)), fmpq(0))
        )

    def is_zero(self) -> bool:
        height, width = self.shape
        return all(self.re[i, j] == 0 and self.im[i, j] == 0 for i in range(height) for j in range(width))

    def realified(self) -> fmpq_mat:
        """The rational matrix of twice the size that acts on (real parts, imaginary parts)."""
        height, width = self.shape
        entries = []
        for i in range(height):
            entries += [self.re[i, j] for j in range(width)] + [-self.im[i, j] for j in range(width)]
        for i in range(height):
            entries += [self.im[i, j] for j in range(width)] + [self.re[i, j] for j in range(width)]
        return fmpq_mat(2 * height, 2 * width, entries)


def rref(rows: Rows, columns: int) -> tuple[Rows, list[int]]:
    """The reduced echelon basis over Q(i) of the span of the rows, and its pivot columns."""
    rows = [row for row in rows if any(row)]
    if not rows:
        return [], []
    entries = []
    for row in rows:
        entries += [part for entry in row for part in (entry.re, entry.im)]
        entries += [part for entry in row for part in (-entry.im, entry.re)]
    reduced, rank = fmpq_mat(2 * len(rows), 2 * columns, entries).rref()
    _require(rank % 2 == 0, "the rational rank of a span over Q(i) is odd")
    basis, pivots = [], []
    for position in range(0, rank, 2):
        pivot = next(column for column in range(2 * columns) if reduced[position, column] != 0)
        following = next(column for column in range(2 * columns) if reduced[position + 1, column] != 0)
        _require(pivot % 2 == 0 and following == pivot + 1, "the rational pivots do not pair")
        basis.append([Gauss(reduced[position, 2 * j], reduced[position, 2 * j + 1]) for j in range(columns)])
        pivots.append(pivot // 2)
    return basis, pivots


def rank(rows: Rows, columns: int) -> int:
    return len(rref(rows, columns)[0])


def null_space(rows: Rows, columns: int) -> Rows:
    """A basis of {x : rows x = 0}, one vector per row, in reduced echelon form."""
    basis, pivots = rref(rows, columns)
    kernel = []
    for free in (column for column in range(columns) if column not in pivots):
        vector = [ZERO] * columns
        vector[free] = ONE
        for row, pivot in zip(basis, pivots, strict=True):
            vector[pivot] = -row[free]
        kernel.append(vector)
    return rref(kernel, columns)[0]


def combine(coefficients: Sequence[Gauss], matrices: Sequence[CMat]) -> CMat:
    """sum_k coefficients[k] matrices[k]; the matrices share a shape and the sum has at least one term."""
    total = matrices[0].scale(coefficients[0])
    for coefficient, matrix in zip(coefficients[1:], matrices[1:], strict=True):
        if coefficient:
            total = total + matrix.scale(coefficient)
    return total


# ---------------------------------------------------------------------------------------------------------------------
# The stabilizer of a space of quadrics

Quadric = dict[int, Gauss]


def monomials(n: int) -> list[tuple[int, int]]:
    return list(itertools.combinations_with_replacement(range(n), 2))


def quadric_basis(quadrics: list[dict[tuple[int, int], Gauss]], n: int) -> tuple[Rows, list[int]]:
    column = {m: k for k, m in enumerate(monomials(n))}
    rows = []
    for quadric in quadrics:
        row = [ZERO] * len(column)
        for monomial, coefficient in quadric.items():
            row[column[monomial]] = row[column[monomial]] + coefficient
        rows.append(row)
    return rref(rows, len(column))


def annihilator(basis: Rows, pivots: list[int], width: int) -> Rows:
    """The forms that vanish on the span of the echelon basis B: e_f - sum_t B[t, f] e_(pivot t) per free column f."""
    forms = []
    for free in (column for column in range(width) if column not in pivots):
        form = [ZERO] * width
        form[free] = ONE
        for row, pivot in zip(basis, pivots, strict=True):
            form[pivot] = -row[free]
        forms.append(form)
    return forms


def derivation_terms(n: int) -> list[list[list[tuple[int, int]]]]:
    """terms[i][j]: the pairs (source monomial, target monomial) of the matrix unit y_i -> y_j, once per factor y_i."""
    column = {m: k for k, m in enumerate(monomials(n))}
    terms: list[list[list[tuple[int, int]]]] = [[[] for _ in range(n)] for _ in range(n)]
    for (a, b), k in column.items():
        for factor, other in ((a, b), (b, a)):
            for j in range(n):
                terms[factor][j].append((k, column[(min(j, other), max(j, other))]))
    return terms


def modular_pivot_rows(basis: Rows, forms: Rows, n: int) -> list[tuple[int, int]]:
    """Pairs (basis quadric, annihilating form) whose rows span the row space of the system modulo PRIME."""
    width = len(monomials(n))
    reduced_basis = np.array([[entry.reduce(PRIME, I_ROOT) for entry in row] for row in basis], dtype=np.int64)
    reduced_forms = np.array([[entry.reduce(PRIME, I_ROOT) for entry in row] for row in forms], dtype=np.int64)
    terms = derivation_terms(n)
    equations = np.zeros((len(basis) * len(forms), n * n), dtype=np.int64)
    for i, j in itertools.product(range(n), range(n)):
        image = np.zeros((len(basis), width), dtype=np.int64)
        for source, target in terms[i][j]:
            image[:, target] += reduced_basis[:, source]
        equations[:, i * n + j] = ((image % PRIME) @ reduced_forms.T % PRIME).reshape(-1)
    nonzero = np.flatnonzero(equations.any(axis=1))
    if not len(nonzero):
        return []
    transposed = nmod_mat(n * n, len(nonzero), [int(v) for v in equations[nonzero].T.reshape(-1)], PRIME)
    reduced, row_rank = transposed.rref()
    pivots = []
    for position in range(row_rank):
        pivots.append(next(column for column in range(len(nonzero)) if int(reduced[position, column])))
    return [divmod(int(nonzero[pivot]), len(forms)) for pivot in pivots]


def stabilizer(quadrics: list[dict[tuple[int, int], Gauss]], n: int) -> tuple[list[CMat], dict[str, int]]:
    """The reduced echelon basis of g as n x n matrices, and the counts of the route."""
    width = len(monomials(n))
    basis, pivots = quadric_basis(quadrics, n)
    forms = annihilator(basis, pivots, width)
    selected = modular_pivot_rows(basis, forms, n) if basis and forms else []
    terms = derivation_terms(n)
    sparse_basis = [{k: entry for k, entry in enumerate(row) if entry} for row in basis]
    system = []
    for quadric, form in selected:
        row = []
        for i, j in itertools.product(range(n), range(n)):
            total = ZERO
            for source, target in terms[i][j]:
                coefficient = sparse_basis[quadric].get(source)
                if coefficient is not None and forms[form][target]:
                    total = total + coefficient * forms[form][target]
            row.append(total)
        system.append(row)
    kernel = null_space(system, n * n)
    matrices = [CMat.from_rows([vector[i * n : (i + 1) * n] for i in range(n)], n) for vector in kernel]
    failures = sum(not stabilizes(matrix, sparse_basis, basis, pivots, n) for matrix in matrices)
    _require(failures == 0, f"{failures} null vectors of the selected rows do not stabilize the quadrics")
    counts = {
        "quadric_space_dimension": len(basis),
        "system_rows": len(basis) * len(forms),
        "selected_rows": len(selected),
        "selected_rank_over_qi": n * n - len(kernel),
    }
    return matrices, counts


def stabilizes(matrix: CMat, sparse_basis: list[Quadric], basis: Rows, pivots: list[int], n: int) -> bool:
    """Whether the derivation of the matrix maps every basis quadric into the span of the basis, exactly."""
    listing = monomials(n)
    column = {m: k for k, m in enumerate(listing)}
    entries = matrix.rows()
    for quadric in sparse_basis:
        image = [ZERO] * len(listing)
        for source, coefficient in quadric.items():
            a, b = listing[source]
            for factor, other in ((a, b), (b, a)):
                for j in range(n):
                    if entries[factor][j]:
                        target = column[(min(j, other), max(j, other))]
                        image[target] = image[target] + coefficient * entries[factor][j]
        for row, pivot in zip(basis, pivots, strict=True):
            lead = image[pivot]
            if lead:
                image = [value - lead * entry if entry else value for value, entry in zip(image, row, strict=True)]
        if any(image):
            return False
    return True


# ---------------------------------------------------------------------------------------------------------------------
# Structure of a matrix Lie algebra over Q(i)


def flatten(matrix: CMat) -> list[Gauss]:
    return [entry for row in matrix.rows() for entry in row]


def adjoint(algebra: list[CMat], label: str) -> tuple[list[CMat], list[CMat]]:
    """The echelon basis of the span and ad: ad[k] has column m equal to the coordinates of [b_k, b_m]."""
    n = algebra[0].shape[0]
    flat, pivots = rref([flatten(matrix) for matrix in algebra], n * n)
    _require(len(flat) == len(algebra), f"{label}: the given matrices are dependent")
    basis = [CMat.from_rows([vector[i * n : (i + 1) * n] for i in range(n)], n) for vector in flat]
    dim = len(basis)
    columns: list[list[list[Gauss]]] = [[[] for _ in range(dim)] for _ in range(dim)]
    for k, m in itertools.product(range(dim), range(dim)):
        if m < k:
            columns[k][m] = [-entry for entry in columns[m][k]]
            continue
        bracket = flatten(basis[k] @ basis[m] - basis[m] @ basis[k])
        coordinates = [bracket[pivot] for pivot in pivots]
        for coordinate, vector in zip(coordinates, flat, strict=True):
            if coordinate:
                bracket = [
                    value - coordinate * entry if entry else value for value, entry in zip(bracket, vector, strict=True)
                ]
        _require(not any(bracket), f"{label}: the span is not closed under the bracket")
        columns[k][m] = coordinates
    ad = [CMat.from_rows([[columns[k][m][c] for m in range(dim)] for c in range(dim)], dim) for k in range(dim)]
    return basis, ad


class Structure:
    """Subspaces of a Lie algebra of dimension `dim`, each a list of coordinate rows, with its adjoint matrices."""

    def __init__(self, ad: list[CMat]) -> None:
        self.ad = ad
        self.dim = len(ad)
        self.whole = CMat.identity(self.dim).rows()

    def ad_of(self, vector: list[Gauss]) -> CMat:
        return combine(vector, self.ad)

    def bracket_span(self, left: Rows, right: Rows) -> Rows:
        """The span of the brackets [x, y], x in `left`, y in `right`."""
        if not left or not right:
            return []
        targets = CMat.from_rows(right, self.dim).transpose()
        brackets: Rows = []
        for vector in left:
            brackets += (self.ad_of(vector) @ targets).transpose().rows()
        return rref(brackets, self.dim)[0]

    def is_ideal(self, subspace: Rows) -> bool:
        return rank(subspace + self.bracket_span(self.whole, subspace), self.dim) == len(subspace)

    def sums_to_whole(self, left: Rows, right: Rows) -> bool:
        return rank(left + right, self.dim) == self.dim

    def reaches_zero(self, subspace: Rows, step: Callable[[Rows], Rows]) -> bool:
        current = subspace
        for _ in range(self.dim + 1):
            if not current:
                return True
            current = step(current)
        return not current


def quotient_has_sl2_triple(structure: Structure, ideal: Rows) -> bool:
    """Whether g / ideal, of dimension 3, holds h, e, f with [h, e] = 2e, [h, f] = -2f and [e, f] = h over Q(i)."""
    return quotient_sl2_triple(structure, ideal) is not None


def quotient_sl2_triple(structure: Structure, ideal: Rows) -> tuple[list[Gauss], list[Gauss], list[Gauss]] | None:
    """Representatives in g of classes h, e, f of g / ideal with [h, e] = 2e, [h, f] = -2f and [e, f] = h, or None.

    The quotient must have dimension 3. The search runs over classes x with small integer coordinates whose ad on
    the quotient has a nonzero eigenvalue in Q(i); such a class exists in every basis of a split sl2, and a quotient
    without one in this range reads None. Each representative is supported on the non-pivot coordinates of the
    echelon basis of the ideal.
    """
    dim = structure.dim
    ideal, pivots = rref(ideal, dim)
    if ideal and not structure.is_ideal(ideal):
        return None
    free = [k for k in range(dim) if k not in pivots]
    if len(free) != 3:
        return None

    def classes(vector: list[Gauss]) -> list[Gauss]:
        for row, pivot in zip(ideal, pivots, strict=True):
            lead = vector[pivot]
            if lead:
                vector = [value - lead * entry for value, entry in zip(vector, row, strict=True)]
        return [vector[k] for k in free]

    # table[a] has column b equal to the class of [c_a, c_b].
    table = []
    for a in free:
        columns = [classes([row[b] for row in structure.ad[a].rows()]) for b in free]
        table.append(CMat.from_rows([[columns[b][c] for b in range(3)] for c in range(3)], 3))
    identity = CMat.identity(3)
    two = Gauss(2, 0)
    for weights in itertools.product(range(-2, 3), repeat=3):
        if not any(weights):
            continue
        x = [Gauss(weight, 0) for weight in weights]
        operator = combine(x, table)
        root = gauss_sqrt((operator @ operator).trace() * Gauss(fmpq(1, 2), 0))
        if root is None or not root:
            continue
        h = [entry * two * root.inverse() for entry in x]
        ad_h = combine(h, table)
        up = null_space((ad_h - identity.scale(two)).rows(), 3)
        down = null_space((ad_h + identity.scale(two)).rows(), 3)
        if len(up) != 1 or len(down) != 1:
            continue
        e, f = up[0], down[0]
        bracket = (combine(e, table) @ CMat.from_rows([f], 3).transpose()).transpose().rows()[0]
        support = next(k for k in range(3) if h[k])
        scale = bracket[support] * h[support].inverse()
        if not scale or any(value != scale * entry for value, entry in zip(bracket, h, strict=True)):
            continue
        f = [entry * scale.inverse() for entry in f]
        e_column, f_column = CMat.from_rows([e], 3).transpose(), CMat.from_rows([f], 3).transpose()
        relations = [
            (ad_h @ e_column - e_column.scale(two)).is_zero(),
            (ad_h @ f_column + f_column.scale(two)).is_zero(),
            (combine(e, table) @ f_column - CMat.from_rows([h], 3).transpose()).is_zero(),
        ]
        if all(relations) and rank([h, e, f], 3) == 3:
            lifted = []
            for classes_of in (h, e, f):
                vector = [ZERO] * dim
                for position, value in zip(free, classes_of, strict=True):
                    vector[position] = value
                lifted.append(vector)
            return lifted[0], lifted[1], lifted[2]
    return None


def is_semisimple(matrix: CMat) -> bool:
    """Whether the minimal polynomial is squarefree, read on the rational matrix of twice the size."""
    minimal = matrix.realified().minpoly()
    return bool(minimal.gcd(minimal.derivative()).degree() == 0)


def decompose(algebra: list[CMat], label: str) -> tuple[dict[str, Any], list[CMat], list[CMat]]:
    """The structure numbers, the echelon basis and the matrices of a basis of the Cartan subalgebra."""
    basis, ad = adjoint(algebra, label)
    structure = Structure(ad)
    dim = structure.dim
    killing = CMat.from_rows([[(ad[k] @ ad[m]).trace() for m in range(dim)] for k in range(dim)], dim)
    trace = CMat.from_rows([[(basis[k] @ basis[m]).trace() for m in range(dim)] for k in range(dim)], dim)

    def derived(ideal: Rows) -> Rows:
        return structure.bracket_span(ideal, ideal)

    series = [structure.whole]
    while series[-1] and len(series) <= dim + 1:
        following = derived(series[-1])
        if len(following) == len(series[-1]):
            break
        series.append(following)
    commutator = series[1] if len(series) > 1 else series[0]
    # x is central when sum_k x_k ad[k] = 0: one equation per entry of the matrix.
    center = null_space([[ad[k].rows()[c][m] for k in range(dim)] for c in range(dim) for m in range(dim)], dim)
    against_commutator = (CMat.from_rows(commutator, dim) @ killing).rows() if commutator else []
    radical = null_space(against_commutator, dim)
    nil = null_space(against_commutator + trace.rows(), dim)
    digest = hashlib.sha256(label.encode()).digest()
    generic = structure.ad_of([Gauss(digest[k % 32] + 1, 0) for k in range(dim)])
    power = CMat.identity(dim)
    for _ in range(dim):
        power = power @ generic
    cartan = null_space(power.rows(), dim)
    lower = structure.bracket_span(cartan, cartan)
    cartan_matrices = [combine(vector, basis) for vector in cartan]
    if cartan:
        coordinates = CMat.from_rows(cartan, dim)
        torus = rank((coordinates @ trace @ coordinates.transpose()).rows(), len(cartan))
    else:
        torus = 0
    central_torus = len(radical) - len(nil)
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
        "levi_type": modular.LEVI_TYPES.get(levi, "undetermined by (dimension, rank)"),
        "generic_centralizer": dim - rank(generic.rows(), dim),
        "cartan_dimension": len(cartan),
        "cartan_derived_dimension": len(lower),
        "torus_rank": torus,
        "radical_is_solvable_ideal": structure.is_ideal(radical) and structure.reaches_zero(radical, derived),
        "quotient_by_radical_is_perfect": structure.sums_to_whole(commutator, radical),
        "quotient_by_radical_has_sl2_triple": quotient_has_sl2_triple(structure, radical),
        "nil_ideal_is_nilpotent_ideal": (
            structure.is_ideal(nil)
            and structure.reaches_zero(nil, lambda current: structure.bracket_span(nil, current))
        ),
        "cartan_is_toral": not lower and all(is_semisimple(matrix) for matrix in cartan_matrices),
    }
    return numbers, basis, cartan_matrices


# ---------------------------------------------------------------------------------------------------------------------
# A Levi subalgebra, the sl2 strings, a split Cartan subalgebra and the torus weights


def bracket(structure: Structure, left: list[Gauss], right: list[Gauss]) -> list[Gauss]:
    """The coordinates of [left, right]."""
    return (structure.ad_of(left) @ CMat.from_rows([right], structure.dim).transpose()).transpose().rows()[0]


def _sum(left: list[Gauss], right: list[Gauss]) -> list[Gauss]:
    return [a + b for a, b in zip(left, right, strict=True)]


def _scaled(factor: Gauss, vector: list[Gauss]) -> list[Gauss]:
    return [factor * a for a in vector]


def solve(equations: Rows, values: list[Gauss], unknowns: int) -> list[Gauss] | None:
    """One solution x of equations x = values over Q(i), or None when the system is inconsistent."""
    rows = [[*row, -value] for row, value in zip(equations, values, strict=True)]
    for vector in null_space(rows, unknowns + 1):
        if vector[-1]:
            inverse = vector[-1].inverse()
            return [a * inverse for a in vector[:-1]]
    return None


def killing_radical(structure: Structure) -> Rows:
    """{x : kappa(x, [g, g]) = 0} for the Killing form kappa."""
    dim, ad = structure.dim, structure.ad
    killing = CMat.from_rows([[(ad[k] @ ad[m]).trace() for m in range(dim)] for k in range(dim)], dim)
    commutator = structure.bracket_span(structure.whole, structure.whole)
    return null_space((CMat.from_rows(commutator, dim) @ killing).rows() if commutator else [], dim)


def sl2_defects(
    structure: Structure, triple: tuple[list[Gauss], list[Gauss], list[Gauss]]
) -> tuple[list[Gauss], list[Gauss], list[Gauss]]:
    """[h, e] - 2e, [h, f] + 2f and [e, f] - h."""
    h, e, f = triple
    two = Gauss(2, 0)
    return (
        _sum(bracket(structure, h, e), _scaled(-two, e)),
        _sum(bracket(structure, h, f), _scaled(two, f)),
        _sum(bracket(structure, e, f), _scaled(Gauss(-1, 0), h)),
    )


def levi_lift(
    structure: Structure, radical: Rows, triple: tuple[list[Gauss], list[Gauss], list[Gauss]]
) -> tuple[list[Gauss], list[Gauss], list[Gauss]] | None:
    """Elements h, e, f of g with the sl2 relations exactly, lifting a triple that satisfies them modulo the radical.

    Along the derived series r = r_0 > r_1 > ... > 0 of the radical the defects of the relations lie in r_k, and a
    correction (y_h, y_e, y_f) in r_k moves them into r_(k+1) when it solves the linearized relations modulo r_(k+1)
    (the brackets of two corrections lie in r_(k+1)). Levi's theorem makes each system solvable; None reports an
    unsolvable one, and the returned triple has zero defects by an exact test.
    """
    dim = structure.dim
    h, e, f = triple
    series = [rref(radical, dim)[0]]
    while series[-1]:
        series.append(structure.bracket_span(series[-1], series[-1]))
    two, minus = Gauss(2, 0), Gauss(-1, 0)
    for current, following in itertools.pairwise(series):
        count, slack = len(current), len(following)
        unknowns = 3 * count + 3 * slack
        equations = [[ZERO] * unknowns for _ in range(3 * dim)]

        def put(block: int, column: int, vector: list[Gauss], equations: Rows = equations) -> None:
            for position, value in enumerate(vector):
                if value:
                    equations[block * dim + position][column] = equations[block * dim + position][column] + value

        for j, b in enumerate(current):
            hb, eb, fb = bracket(structure, h, b), bracket(structure, e, b), bracket(structure, f, b)
            # Columns: y_h on b_j, then y_e, then y_f. Block 0 is [y_h, e] + [h, y_e] - 2 y_e, block 1 is
            # [y_h, f] + [h, y_f] + 2 y_f, block 2 is [y_e, f] + [e, y_f] - y_h.
            put(0, j, _scaled(minus, eb))
            put(0, count + j, _sum(hb, _scaled(-two, b)))
            put(1, j, _scaled(minus, fb))
            put(1, 2 * count + j, _sum(hb, _scaled(two, b)))
            put(2, count + j, _scaled(minus, fb))
            put(2, 2 * count + j, eb)
            put(2, j, _scaled(minus, b))
        for block in range(3):
            for j, b in enumerate(following):
                put(block, 3 * count + block * slack + j, b)
        values = [-value for defect in sl2_defects(structure, (h, e, f)) for value in defect]
        solution = solve(equations, values, unknowns)
        if solution is None:
            return None
        corrections = []
        for block in range(3):
            vector = [ZERO] * dim
            for coefficient, b in zip(solution[block * count : (block + 1) * count], current, strict=True):
                if coefficient:
                    vector = _sum(vector, _scaled(coefficient, b))
            corrections.append(vector)
        h, e, f = _sum(h, corrections[0]), _sum(e, corrections[1]), _sum(f, corrections[2])
    if any(any(defect) for defect in sl2_defects(structure, (h, e, f))):
        return None
    return h, e, f


def integer_spectrum(matrix: CMat) -> dict[int, int]:
    """Integer eigenvalue -> dimension of its eigenspace, over the integers of absolute value at most the size."""
    n = matrix.shape[0]
    identity = CMat.identity(n)
    spectrum = {}
    for value in range(-n, n + 1):
        multiplicity = n - rank((matrix - identity.scale(Gauss(value, 0))).rows(), n)
        if multiplicity:
            spectrum[value] = multiplicity
    return spectrum


def sl2_strings(spectrum: dict[int, int]) -> dict[int, int]:
    """Highest weight d -> number of irreducible summands of dimension d + 1, read from the weights of h."""
    strings = {}
    for weight in sorted(w for w in spectrum if w >= 0):
        count = spectrum[weight] - spectrum.get(weight + 2, 0)
        if count:
            strings[weight] = count
    return strings


def fitting_null(structure: Structure, vector: list[Gauss]) -> Rows:
    """The generalized zero eigenspace of ad of the vector."""
    operator = structure.ad_of(vector)
    power = CMat.identity(structure.dim)
    for _ in range(structure.dim):
        power = power @ operator
    return null_space(power.rows(), structure.dim)


SPLIT_CARTAN_ATTEMPTS = 8


def cartan_through(
    structure: Structure, basis: list[CMat], fixed: Rows, expected: int, label: str
) -> tuple[Rows, int] | None:
    """A Cartan subalgebra of g that commutes with every vector of `fixed`, and the attempt that found it.

    Candidates are combinations of a basis of the common centralizer of `fixed` with Gaussian integer coefficients
    from a hash of the label and the attempt. A candidate counts when its Fitting null component has the dimension
    `expected`, is abelian, has semisimple basis matrices and contains every vector of `fixed`; such a component
    is its own normalizer, hence a Cartan subalgebra.
    """
    dim = structure.dim
    centralizer = null_space([row for vector in fixed for row in structure.ad_of(vector).rows()], dim)
    for attempt in range(SPLIT_CARTAN_ATTEMPTS):
        digest = hashlib.sha256(f"{label}|cartan|{attempt}".encode()).digest()
        element = [ZERO] * dim
        for k, vector in enumerate(centralizer):
            element = _sum(element, _scaled(Gauss(digest[k % 32] + 1, digest[(k + 7) % 32]), vector))
        cartan = fitting_null(structure, element)
        if (
            len(cartan) == expected
            and not structure.bracket_span(cartan, cartan)
            and rank(cartan + fixed, dim) == expected
            and all(is_semisimple(combine(vector, basis)) for vector in cartan)
        ):
            return cartan, attempt
    return None


def eigenvalues(matrix: CMat) -> list[Gauss] | None:
    """The eigenvalues of a matrix over Q(i), sorted, or None when one of them lies outside Q(i).

    The characteristic polynomial of the rational matrix of twice the size is the product of the characteristic
    polynomial over Q(i) and its conjugate. A rational root, and each root of an irreducible quadratic factor with
    discriminant minus a square, is a candidate; a candidate is an eigenvalue when the shifted matrix loses rank.
    """
    n = matrix.shape[0]
    candidates = []
    for factor, _ in matrix.realified().charpoly().factor()[1]:
        coefficients = [fmpq(value) for value in factor.coeffs()]
        if factor.degree() == 1:
            candidates.append(Gauss(-coefficients[0] / coefficients[1], 0))
        elif factor.degree() == 2:
            c, b, a = coefficients
            root = _rational_sqrt(-(b * b - 4 * a * c))
            if root is None:
                return None
            candidates += [Gauss(-b / (2 * a), root / (2 * a)), Gauss(-b / (2 * a), -root / (2 * a))]
        else:
            return None
    identity = CMat.identity(n)
    found = [value for value in candidates if rank((matrix - identity.scale(value)).rows(), n) < n]
    return sorted(
        found,
        key=lambda value: (Fraction(int(value.re.p), int(value.re.q)), Fraction(int(value.im.p), int(value.im.q))),
    )


def joint_eigenspaces(matrices: list[CMat], n: int) -> list[tuple[Rows, list[Gauss]]] | None:
    """(basis, eigenvalue of each matrix) of the joint eigenspaces of commuting matrices, or None when an eigenvalue
    lies outside Q(i). The dimensions add up to n exactly when the matrices are jointly diagonalizable over Q(i)."""
    spaces: list[tuple[Rows, list[Gauss]]] = [(CMat.identity(n).rows(), [])]
    identity = CMat.identity(n)
    for matrix in matrices:
        values = eigenvalues(matrix)
        if values is None:
            return None
        refined = []
        for vectors, weight in spaces:
            frame = CMat.from_rows(vectors, n)
            for value in values:
                kernel = null_space(((matrix - identity.scale(value)) @ frame.transpose()).rows(), len(vectors))
                if kernel:
                    refined.append(((CMat.from_rows(kernel, len(vectors)) @ frame).rows(), [*weight, value]))
        spaces = refined
    return spaces


def integer_weights(weights: Rows, rank_expected: int) -> list[list[int]] | None:
    """The weights in a basis of the lattice they generate, or None when that lattice has another rank.

    The weights are linear forms on the Cartan subalgebra, given by their values on its basis. They are written on
    the first `rank_expected` independent ones; the coordinates must be rational, and the Hermite normal form of
    their common-denominator multiple gives a basis of the lattice, on which every weight has integer coordinates
    and the weights generate Z^rank.
    """
    chosen: Rows = []
    for weight in weights:
        if rank([*chosen, weight], rank_expected) > len(chosen):
            chosen.append(weight)
    if len(chosen) != rank_expected:
        return None
    frame = CMat.from_rows(chosen, rank_expected).transpose().rows()
    coordinates = []
    for weight in weights:
        solution = solve(frame, weight, rank_expected)
        if solution is None or any(value.im != 0 for value in solution):
            return None
        coordinates.append([value.re for value in solution])
    denominator = math.lcm(*(int(value.q) for row in coordinates for value in row))
    scaled = fmpz_mat(
        len(coordinates), rank_expected, [int(value * denominator) for row in coordinates for value in row]
    )
    hermite = scaled.hnf()
    lattice = fmpq_mat(
        rank_expected,
        rank_expected,
        [fmpq(int(hermite[i, j])) for i in range(rank_expected) for j in range(rank_expected)],
    )
    integral = (
        fmpq_mat(
            len(coordinates),
            rank_expected,
            [fmpq(int(scaled[i, j])) for i in range(len(coordinates)) for j in range(rank_expected)],
        )
        * lattice.inv()
    )
    rows = [[integral[i, j] for j in range(rank_expected)] for i in range(len(coordinates))]
    if any(value.q != 1 for row in rows for value in row):
        return None
    return [[int(value.p) for value in row] for row in rows]


def cocharacter(weights: list[list[int]], values: list[Gauss]) -> list[int] | None:
    """The integer vector a with weights a = values, or None when no integer vector solves it."""
    width = len(weights[0])
    solution = solve([[Gauss(value, 0) for value in row] for row in weights], values, width)
    if solution is None or any(value.im != 0 or value.re.q != 1 for value in solution):
        return None
    return [int(value.re.p) for value in solution]


def quadric_weight_spaces(echelon: Rows, eigenvectors: Rows, weights: list[list[int]], n: int) -> dict[str, Any]:
    """The quadric space K on torus eigen-coordinates, split by weight.

    With y = sum_a y'_a v_a for the eigenvectors v_a, a quadric with symmetric matrix Q becomes P^T Q P for the
    matrix P of eigenvector columns, and the monomial y'_a y'_b has weight w_a + w_b. The ranks of K on the monomials
    of each weight add up to dim K exactly when K is the direct sum of its weight spaces.
    """
    listing = monomials(n)
    frame = CMat.from_rows(eigenvectors, n).transpose()
    half = Gauss(fmpq(1, 2), 0)
    by_weight: dict[tuple[int, ...], list[int]] = {}
    for column, (a, b) in enumerate(listing):
        by_weight.setdefault(tuple(x + y for x, y in zip(weights[a], weights[b], strict=True)), []).append(column)
    transformed = []
    for row in echelon:
        symmetric = [[ZERO] * n for _ in range(n)]
        for column, value in enumerate(row):
            if value:
                a, b = listing[column]
                if a == b:
                    symmetric[a][a] = value
                else:
                    symmetric[a][b] = symmetric[b][a] = value * half
        image = (frame.transpose() @ CMat.from_rows(symmetric, n) @ frame).rows()
        transformed.append([image[a][b] if a == b else image[a][b] + image[b][a] for a, b in listing])
    pairs: dict[tuple[int, int], int] = {}
    total = 0
    for columns in by_weight.values():
        dimension = rank([[row[column] for column in columns] for row in transformed], len(columns))
        total += dimension
        if dimension:
            pairs[(len(columns), dimension)] = pairs.get((len(columns), dimension), 0) + 1
    return {
        "weights_of_quadratic_monomials": len(by_weight),
        "weights_that_carry_a_quadric": sum(pairs.values()),
        "sum_of_weight_space_dimensions": total,
        # [dimension of the monomial weight space, dimension of the quadrics in it, number of such weights]
        "monomials_quadrics_count": sorted([monomial, quadric, count] for (monomial, quadric), count in pairs.items()),
    }


def refine(
    structure: Structure,
    basis: list[CMat],
    pivots: list[int],
    numbers: dict[str, Any],
    echelon: Rows,
    grading: list[int],
    label: str,
) -> dict[str, Any]:
    """The Levi lift with its sl2 strings and the split torus with its integer weights, for one algebra.

    `pivots` are the pivot positions of the echelon basis of g in gl_n, so the coordinates of a matrix of g are its
    entries there; `grading` holds the integer weights of the generators under the slice torus.
    """
    n = basis[0].shape[0]
    radical = killing_radical(structure)
    triple = quotient_sl2_triple(structure, radical)
    lift = None if triple is None else levi_lift(structure, radical, triple)
    if lift is None:
        return {"levi_lift_found": False}
    h = lift[0]
    spectrum = integer_spectrum(combine(h, basis))
    grading_matrix = [Gauss(grading[i], 0) if i == j else ZERO for i in range(n) for j in range(n)]
    derivation = [grading_matrix[pivot] for pivot in pivots]
    result: dict[str, Any] = {
        "levi_lift_found": True,
        "h_spectrum": {str(weight): count for weight, count in sorted(spectrum.items())},
        "h_spectrum_total": sum(spectrum.values()),
        "sl2_strings": {str(weight): count for weight, count in sl2_strings(spectrum).items()},
        "sl2_strings_total": sum((weight + 1) * count for weight, count in sl2_strings(spectrum).items()),
        "h_commutes_with_weight_derivation": not any(bracket(structure, h, derivation)),
    }
    fixed = [h, derivation] if result["h_commutes_with_weight_derivation"] else [h]
    found = cartan_through(structure, basis, fixed, numbers["cartan_dimension"], label)
    result["split_cartan_found"] = found is not None
    if found is None:
        return result
    cartan, attempt = found
    result |= {"split_cartan_attempt": attempt, "split_cartan_contains_weight_derivation": len(fixed) == 2}
    matrices = [combine(vector, basis) for vector in cartan]
    spaces = joint_eigenspaces(matrices, n)
    result["torus_splits_over_qi"] = spaces is not None and sum(len(vectors) for vectors, _ in spaces) == n
    if spaces is None or not result["torus_splits_over_qi"]:
        return result
    eigenvectors = [vector for vectors, _ in spaces for vector in vectors]
    per_vector = [weight for vectors, weight in spaces for _ in vectors]
    weights = integer_weights(per_vector, len(cartan))
    result["weights_are_integral_of_full_rank"] = weights is not None
    if weights is None:
        return result
    frame = CMat.from_rows(eigenvectors, n).transpose()

    def eigenvalues_of(matrix: CMat) -> list[Gauss] | None:
        """The eigenvalue of the matrix on each eigenvector, or None when one is no eigenvector of it."""
        image = (matrix @ frame).transpose().rows()
        values = []
        for vector, moved in zip(eigenvectors, image, strict=True):
            position = next(k for k in range(n) if vector[k])
            value = moved[position] * vector[position].inverse()
            if any(a != value * b for a, b in zip(moved, vector, strict=True)):
                return None
            values.append(value)
        return values

    def named(matrix: CMat) -> list[int] | None:
        values = eigenvalues_of(matrix)
        return None if values is None else cocharacter(weights, values)

    distinct = sorted({tuple(weight) for weight in weights})
    result |= {
        "weights": [[*weight, weights.count(list(weight))] for weight in distinct],
        "distinct_weights": len(distinct),
        "largest_weight_multiplicity": max(weights.count(list(weight)) for weight in distinct),
        "cocharacter_of_euler_field": named(CMat.identity(n)),
        "cocharacter_of_h": named(combine(h, basis)),
        "cocharacter_of_weight_derivation": named(combine(derivation, basis)) if len(fixed) == 2 else None,
        "quadrics_by_weight": quadric_weight_spaces(echelon, eigenvectors, weights, n),
    }
    return result


# ---------------------------------------------------------------------------------------------------------------------
# Cells and the record


def read_quadrics(lines: list[str]) -> list[dict[tuple[int, int], Gauss]]:
    """The `RELATION` lines of a degree-2 cell as quadrics on zero-based generator indices."""
    quadrics = []
    for line in lines:
        quadric = {}
        for key, coefficient in ws.parse_relation(line):
            _require(len(key) == 2 and key[0] <= key[1], f"not a quadratic product index: {key}")
            real, imaginary = ws.parse_gaussian(coefficient)
            quadric[(key[0] - 1, key[1] - 1)] = Gauss(real, imaginary)
        quadrics.append(quadric)
    return quadrics


def control_dimension(count: int, n: int, label: str) -> int:
    """The modular stabilizer dimension of `count` quadrics with coefficients from a fixed hash stream."""
    listing = monomials(n)
    stream = hashlib.shake_256(f"{label}|control".encode()).digest(4 * count * len(listing))
    control = [
        {
            m: int.from_bytes(stream[4 * (i * len(listing) + k) : 4 * (i * len(listing) + k) + 4], "big") % PRIME
            for k, m in enumerate(listing)
        }
        for i in range(count)
    ]
    return len(modular.stabilizer(control, n, PRIME))


def analyze_cell(job: tuple[str, str, int, list[int], list[str]]) -> dict[str, Any]:
    orbit, source, n, weights, lines = job
    label = ws.incidence_name(orbit, source)
    quadrics = read_quadrics(lines)
    matrices, counts = stabilizer(quadrics, n)
    numbers, basis, _ = decompose(matrices, label)
    flat, basis_pivots = rref([flatten(matrix) for matrix in basis], n * n)
    _require(len(flat) == len(basis), f"{label}: the echelon basis of g changed under a second reduction")
    structure = Structure(adjoint(basis, label)[1])
    reduced_quadrics = [{m: c.reduce(PRIME, I_ROOT) for m, c in quadric.items()} for quadric in quadrics]
    reduced_basis = np.array(
        [[[entry.reduce(PRIME, I_ROOT) for entry in row] for row in matrix.rows()] for matrix in basis], dtype=np.int64
    )
    modular_numbers = modular.analyze(reduced_basis, PRIME, label)
    listing = monomials(n)
    echelon, pivots = quadric_basis(quadrics, n)
    sparse = [{k: entry for k, entry in enumerate(row) if entry} for row in echelon]
    weight_matrix = CMat.from_rows([[Gauss(weights[i], 0) if i == j else ZERO for j in range(n)] for i in range(n)], n)
    euler = stabilizes(CMat.identity(n), sparse, echelon, pivots, n)
    return {
        "incidence": label,
        "orbit": orbit,
        "source": source,
        "generators": n,
        "quadrics": len(lines),
        "quadratic_monomials": len(listing),
        "relations_sha256": hashlib.sha256(("\n".join(sorted(lines)) + "\n").encode("utf-8")).hexdigest(),
        "route": counts,
        "algebra": numbers,
        "weight_derivation_stabilizes": stabilizes(weight_matrix, sparse, echelon, pivots, n),
        "euler_field_stabilizes": euler,
        "refinement": refine(structure, basis, basis_pivots, numbers, echelon, weights, label),
        "reduction": {
            "prime": PRIME,
            "i_root": I_ROOT,
            "stabilizer_dimension_of_reduced_quadrics": len(modular.stabilizer(reduced_quadrics, n, PRIME)),
            "numbers_of_reduced_basis_equal": modular_numbers == numbers,
            "differing_keys": sorted(key for key in numbers if modular_numbers.get(key) != numbers[key]),
        },
        "control_stabilizer_dimension_modulo_prime": control_dimension(len(echelon), n, label),
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def regenerate_relations() -> list[tuple[str, str, int, list[int], list[str]]]:
    """(orbit, source, generators, generator weights, relation lines) of each cell, digest-bound to the record."""
    retained = {
        (cell["orbit"], cell["source"]): cell
        for cell in json.loads(RELATIONS_RECORD.read_text(encoding="utf-8"))["cells"]
        if cell["characteristic"] == 0
    }
    pieces = {piece.orbit: piece for piece in parallel.ordered_map(ws.orbit_task, ws.ORBITS, min_items=1)}
    items = [
        ws.RunItem("cell", orbit, source, 0, ws.fiber_script(pieces[orbit], source, 0, 0)) for orbit, source in CELLS
    ]
    jobs = []
    for (orbit, source), run in zip(CELLS, parallel.ordered_map(ws.run_item, items, min_items=1), strict=True):
        summary = run["summary"]
        cell = retained[(orbit, source)]
        _require(
            summary["relations_sha256"] == cell["relations_sha256"],
            f"{orbit} {source}: the regenerated quadrics differ from the retained digest",
        )
        jobs.append(
            (orbit, source, int(summary["generator_count"]), list(summary["generator_weights"]), run["relations"])
        )
    return jobs


def compute() -> dict[str, Any]:
    banner, version = ws.singular_version()
    rows = parallel.ordered_map(analyze_cell, regenerate_relations(), min_items=1)
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": "Q(i)",
        "inputs": {str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS},
        "tools": {"singular": banner, "singular_version": version},
        "rows": rows,
    }
    record["pass"] = verdict(record) == []
    return record


CHECKS = (
    "radical_is_solvable_ideal",
    "quotient_by_radical_is_perfect",
    "quotient_by_radical_has_sl2_triple",
    "nil_ideal_is_nilpotent_ideal",
    "cartan_is_toral",
)


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes."""
    problems = []
    for row in record["rows"]:
        name, algebra, reduction = row["incidence"], row["algebra"], row["reduction"]
        problems += [f"{name}: {check} is false" for check in CHECKS if not algebra[check]]
        if not row["weight_derivation_stabilizes"] or not row["euler_field_stabilizes"]:
            problems.append(f"{name}: the weight derivation or the Euler field leaves the quadrics")
        if reduction["stabilizer_dimension_of_reduced_quadrics"] != algebra["dimension"]:
            problems.append(f"{name}: the stabilizer changes dimension under reduction")
        if not reduction["numbers_of_reduced_basis_equal"]:
            problems.append(f"{name}: the reduced basis has other structure numbers ({reduction['differing_keys']})")
        if row["control_stabilizer_dimension_modulo_prime"] != 1:
            problems.append(f"{name}: the control quadrics keep more than the Euler field")
        problems += [f"{name}: {problem}" for problem in refinement_problems(row)]
    return problems


REFINEMENT_FLAGS = (
    "levi_lift_found",
    "h_commutes_with_weight_derivation",
    "split_cartan_found",
    "split_cartan_contains_weight_derivation",
    "torus_splits_over_qi",
    "weights_are_integral_of_full_rank",
)


def refinement_problems(row: dict[str, Any]) -> list[str]:
    """The reasons the Levi and torus part of a row fails its rules."""
    refinement, n = row["refinement"], row["generators"]
    problems = [f"{flag} is false" for flag in REFINEMENT_FLAGS if not refinement.get(flag)]
    if problems:
        return problems
    spectrum = {int(weight): count for weight, count in refinement["h_spectrum"].items()}
    if refinement["h_spectrum_total"] != n or any(spectrum.get(-weight) != count for weight, count in spectrum.items()):
        problems.append("the weights of h do not fill the generators symmetrically")
    if refinement["sl2_strings_total"] != n:
        problems.append("the sl2 strings do not fill the generators")
    if sum(weight[-1] for weight in refinement["weights"]) != n:
        problems.append("the torus weights do not fill the generators")
    if len(refinement["weights"][0]) - 1 != row["algebra"]["cartan_dimension"]:
        problems.append("the weight lattice has another rank than the Cartan subalgebra")
    for name in ("cocharacter_of_euler_field", "cocharacter_of_h", "cocharacter_of_weight_derivation"):
        if refinement[name] is None:
            problems.append(f"{name} is no integer vector")
    if refinement["quadrics_by_weight"]["sum_of_weight_space_dimensions"] != row["route"]["quadric_space_dimension"]:
        problems.append("the quadric space is not the sum of its weight spaces")
    return problems


def comparable(record: dict[str, Any]) -> dict[str, Any]:
    """The record without the Singular banner, whose build date varies between hosts; the version number stays."""
    tools = {key: value for key, value in record.get("tools", {}).items() if key != "singular"}
    return {**record, "tools": tools}


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    record = compute()
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if args.write:
        RECORD.write_text(text, encoding="utf-8")
    else:
        if comparable(json.loads(RECORD.read_text(encoding="utf-8"))) != comparable(record):
            raise SystemExit(f"{RECORD.name} differs from the recomputation")
    problems = verdict(record)
    if problems:
        raise SystemExit("\n".join(problems))
    print(json.dumps({row["incidence"]: row["algebra"]["dimension"] for row in record["rows"]}, sort_keys=True))


if __name__ == "__main__":
    main()
