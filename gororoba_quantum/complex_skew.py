"""Exact complex skew coordinates, Pfaffians, and annihilator kernel charts.

The real-linear coordinate map Phi(c,d)=c+i*conj(d) intertwines left
multiplication with K*complex_conjugation, where K=L_a-i*R_b. The complex
kernel therefore needs conjugation before transport back to real coordinates.
The polynomial cover describes rank loci implicitly; it does not classify
connected components, smooth strata, or frontier attachments.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from fractions import Fraction
from functools import cache, lru_cache
from itertools import combinations

import sympy as sp

from cd_core import cd_sign
from rank_charts import _coordinates, _indices, multiplication_matrix


def _dimension(dimension: int) -> None:
    if type(dimension) is not int or dimension < 4 or dimension > 256 or dimension & (dimension - 1):
        raise ValueError("dimension must be a power of two from 4 through 256")


def _values(coordinates: Sequence[int | Fraction]) -> tuple[Fraction, ...]:
    values = _coordinates(coordinates)
    _dimension(len(values))
    if values[0] or values[len(values) // 2]:
        raise ValueError("doubly-pure coordinates require zero scalar parts in both halves")
    return values


def _operator(values: Sequence[sp.Expr]) -> sp.ImmutableMatrix:
    half = len(values) // 2
    return sp.ImmutableMatrix(
        half,
        half,
        lambda row, column: (
            values[row ^ column] * cd_sign(half, row ^ column, column)
            - sp.I * values[half + (row ^ column)] * cd_sign(half, column, row ^ column)
        ),
    )


def complex_operator(coordinates: Sequence[int | Fraction]) -> sp.ImmutableMatrix:
    """Return K over Q(i); the executable point interface rejects floats."""
    return _operator(tuple(sp.Rational(value) for value in _values(coordinates)))


def symbolic_operator(dimension: int) -> tuple[tuple[sp.Expr, ...], sp.ImmutableMatrix]:
    """Return every doubly-pure coefficient as an independent real symbol."""
    _dimension(dimension)
    values = list(sp.symbols(f"x0:{dimension}", real=True))
    values[0] = values[dimension // 2] = sp.Integer(0)
    return tuple(values), _operator(values)


def _skew(matrix: sp.MatrixBase) -> sp.ImmutableMatrix:
    if not isinstance(matrix, sp.MatrixBase) or matrix.rows != matrix.cols:
        raise ValueError("a square exact skew matrix is required")
    if any(value.has(sp.Float) or value.is_finite is False for value in matrix):
        raise ValueError("matrix entries must be exact and finite")
    result = sp.ImmutableMatrix(matrix.applyfunc(sp.expand))
    if result + result.T != sp.zeros(result.rows):
        raise ValueError("matrix must be skew under transpose, not Hermitian adjoint")
    return result


@lru_cache(maxsize=128)
def _rational_pfaffian(matrix: sp.ImmutableMatrix) -> sp.Expr:
    """Eliminate exact Gaussian-rational pivots; each denominator is nonzero."""
    domain_matrix = matrix.to_DM().to_field()
    domain = domain_matrix.domain
    rows = domain_matrix.to_list()
    value = domain.one
    size = len(rows)
    if size % 2:
        return sp.Integer(0)
    for first in range(0, size, 2):
        selected = next((index for index in range(first + 1, size) if rows[first][index] != domain.zero), None)
        if selected is None:
            return sp.Integer(0)
        second = first + 1
        if selected != second:
            rows[second], rows[selected] = rows[selected], rows[second]
            for row in rows:
                row[second], row[selected] = row[selected], row[second]
            value = -value
        pivot = rows[first][second]
        value *= pivot
        for row in range(first + 2, size):
            for column in range(row + 1, size):
                rows[row][column] += (
                    rows[second][row] * rows[first][column] - rows[first][row] * rows[second][column]
                ) / pivot
                rows[column][row] = -rows[row][column]
    return domain.to_sympy(value)


def pfaffian(matrix: sp.MatrixBase) -> sp.Expr:
    """Exact Pfaffians over Q(i), or division-free symbolic matching recurrence.

    Exact symbolic expansion grows combinatorially. Callers select the desired
    principal minors; the API never substitutes generic numerical rank for a
    polynomial identity. The empty Pfaffian is one, and odd order gives zero.
    """
    matrix = _skew(matrix)
    if matrix.to_DM().domain in (sp.ZZ, sp.QQ, sp.ZZ_I, sp.QQ_I):
        return _rational_pfaffian(matrix)

    @cache
    def expand(indices: tuple[int, ...]) -> sp.Expr:
        if not indices:
            return sp.Integer(1)
        if len(indices) % 2:
            return sp.Integer(0)
        first = indices[0]
        return sp.expand(
            sum(
                (
                    (-1) ** (position + 1)
                    * matrix[first, indices[position]]
                    * expand(indices[1:position] + indices[position + 1 :])
                    for position in range(1, len(indices))
                    if matrix[first, indices[position]] != 0
                ),
                sp.Integer(0),
            )
        )

    return expand(tuple(range(matrix.rows)))


def principal_pfaffians(matrix: sp.MatrixBase, order: int) -> Iterator[tuple[tuple[int, ...], sp.Expr]]:
    """Enumerate all principal Pfaffians of one even order, without sampling."""
    matrix = _skew(matrix)
    if type(order) is not int or order < 0 or order > matrix.rows or order % 2:
        raise ValueError("Pfaffian order must be even and within the matrix")
    for indices in combinations(range(matrix.rows), order):
        yield indices, pfaffian(matrix.extract(indices, indices))


def real_rank_equations(dimension: int, real_rank: int) -> Iterator[tuple[tuple[int, ...], sp.Expr, sp.Expr]]:
    """Equations for real rank <= real_rank on the entire doubly-pure space.

    Exact rank also requires a nonzero principal Pfaffian of order real_rank/2.
    Full-rank bounds have an empty equation list. Zero is included explicitly.
    """
    _dimension(dimension)
    if type(real_rank) is not int or not 0 <= real_rank <= dimension or real_rank % 4:
        raise ValueError("real rank must be a multiple of four within the dimension")
    if real_rank == dimension:
        return
    _, matrix = symbolic_operator(dimension)
    for indices, value in principal_pfaffians(matrix, real_rank // 2 + 2):
        real, imaginary = sp.expand_complex(value).as_real_imag()
        yield indices, sp.expand(real), sp.expand(imaginary)


def pivot_cover(dimension: int) -> tuple[tuple[int, int], ...]:
    """Cover all nonzero doubly-pure points by K[0,j]=-a_j+i*b_j != 0."""
    _dimension(dimension)
    return tuple((0, index) for index in range(1, dimension // 2))


def cleared_pair_residual(dimension: int, index: int) -> tuple[sp.Expr, sp.ImmutableMatrix]:
    """Return q and q*S, with S the complex Schur residual on q != 0.

    The real open domain is a_j^2+b_j^2>0. Every upper-triangular entry of
    q*S equals the corresponding four-coordinate principal Pfaffian in the
    ordered pivot/free basis. Clearing q does not extend the chart to q=0.
    """
    _dimension(dimension)
    if type(index) is not int or not 1 <= index < dimension // 2:
        raise ValueError("cover index must lie strictly between zero and half-dimension")
    _, matrix = symbolic_operator(dimension)
    free = tuple(position for position in range(matrix.rows) if position not in (0, index))
    first = matrix.extract([0], free)
    second = matrix.extract([index], free)
    pivot = matrix[0, index]
    cleared = pivot * matrix.extract(free, free) - first.T * second + second.T * first
    return pivot, sp.ImmutableMatrix(cleared.applyfunc(sp.expand))


def realify(matrix: sp.MatrixBase) -> sp.ImmutableMatrix:
    """Real matrix of a complex-linear map in real/imaginary coordinate order."""
    real, imaginary = matrix.as_real_imag()
    return sp.ImmutableMatrix(sp.BlockMatrix([[real, -imaginary], [imaginary, real]]).as_explicit())


def kernel_to_real(frame: sp.MatrixBase) -> sp.ImmutableMatrix:
    """Transport F*z to Phi^-1(conj(F*z)), including both real directions."""
    _dimension(2 * frame.rows)
    real, imaginary = frame.as_real_imag()
    conjugation = sp.diag(1, *([-1] * (frame.rows - 1)))
    return sp.ImmutableMatrix(
        sp.BlockMatrix([[real, -imaginary], [-conjugation * imaginary, -conjugation * real]]).as_explicit()
    )


@dataclass(frozen=True)
class ComplexKernelChart:
    coordinates: tuple[Fraction, ...]
    pivot_indices: tuple[int, ...]
    pivot_pfaffian: sp.Expr
    frame: sp.ImmutableMatrix
    real_frame: sp.ImmutableMatrix
    hermitian_metric: sp.ImmutableMatrix

    @property
    def free_indices(self) -> tuple[int, ...]:
        return tuple(index for index in range(len(self.coordinates) // 2) if index not in self.pivot_indices)

    @property
    def real_rank(self) -> int:
        return 2 * len(self.pivot_indices)


def kernel_chart(
    coordinates: Sequence[int | Fraction],
    pivot_indices: Sequence[int] | None = None,
) -> ComplexKernelChart:
    """Certify a complete kernel frame on a specified constant-rank pivot chart.

    Omitting the pivot chooses independent columns by exact elimination. An
    explicit pivot requires both a nonzero Pfaffian and a zero Schur residual.
    """
    values = _values(coordinates)
    matrix = complex_operator(values)
    indices = (
        tuple(int(index) for index in matrix.to_DM().to_field().rref()[1])
        if pivot_indices is None
        else _indices(pivot_indices, matrix.rows)
    )
    if len(indices) % 2:
        raise ValueError("skew pivot order must be even")
    free = tuple(index for index in range(matrix.rows) if index not in indices)
    pivot = matrix.extract(indices, indices)
    pivot_value = pfaffian(pivot)
    if pivot_value == 0:
        raise ValueError("point lies outside the nonzero Pfaffian domain")
    cross = matrix.extract(indices, free)
    inverse_cross = pivot.inv() * cross if indices else sp.zeros(0, len(free))
    residual = matrix.extract(free, free) + cross.T * inverse_cross
    if residual.applyfunc(sp.simplify) != sp.zeros(len(free)):
        raise ValueError("pivot omits nonzero residual rank; refine the constant-rank chart")
    frame = sp.eye(matrix.rows)[:, list(free)] - sp.eye(matrix.rows)[:, list(indices)] * inverse_cross
    frame = sp.ImmutableMatrix(frame.applyfunc(sp.simplify))
    result = ComplexKernelChart(
        values,
        indices,
        pivot_value,
        frame,
        kernel_to_real(frame),
        sp.ImmutableMatrix((frame.H * frame).applyfunc(sp.simplify)),
    )
    if not verify_kernel_chart(result):
        raise RuntimeError("constructed complex kernel chart fails exact verification")
    return result


def verify_kernel_chart(chart: ComplexKernelChart) -> bool:
    """Check provenance, rank lower/upper bounds, conjugation, and metric."""
    try:
        if not isinstance(chart, ComplexKernelChart):
            return False
        values = _values(chart.coordinates)
        if type(chart.coordinates) is not tuple or any(type(value) is not Fraction for value in chart.coordinates):
            return False
        matrix = complex_operator(values)
        indices = _indices(chart.pivot_indices, matrix.rows)
        if type(chart.pivot_indices) is not tuple or len(indices) % 2:
            return False
        free = chart.free_indices
        if any(
            type(value) is not sp.ImmutableMatrix for value in (chart.frame, chart.real_frame, chart.hermitian_metric)
        ):
            return False
        if chart.frame.shape != (matrix.rows, len(free)):
            return False
        pivot_value = pfaffian(matrix.extract(indices, indices))
        return bool(
            pivot_value != 0
            and chart.pivot_pfaffian == pivot_value
            and chart.frame.extract(free, range(len(free))) == sp.eye(len(free))
            and (matrix * chart.frame).applyfunc(sp.simplify) == sp.zeros(matrix.rows, len(free))
            and chart.real_frame == kernel_to_real(chart.frame)
            and chart.hermitian_metric == (chart.frame.H * chart.frame).applyfunc(sp.simplify)
            and sp.Matrix(multiplication_matrix(values)) * chart.real_frame == sp.zeros(len(values), 2 * len(free))
        )
    except ValueError, TypeError, AttributeError, IndexError:
        return False


def chart_transition(source: ComplexKernelChart, target: ComplexKernelChart) -> sp.ImmutableMatrix:
    """Return z_target=T*z_source; real partner coordinates use realify(T)."""
    if not verify_kernel_chart(source) or not verify_kernel_chart(target):
        raise ValueError("transitions require intact complete kernel certificates")
    if source.coordinates != target.coordinates:
        raise ValueError("overlap certificates must describe the same coefficient point")
    transport = sp.ImmutableMatrix(source.frame.extract(target.free_indices, range(source.frame.cols)))
    if (target.frame * transport - source.frame).applyfunc(sp.simplify) != sp.zeros(*source.frame.shape):
        raise RuntimeError("kernel transition reconstruction fails")
    return transport
