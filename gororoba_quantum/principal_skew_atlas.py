"""Finite principal-pivot covers and exact Cayley-Dickson kernel transport.

The quaternion coordinate blocks give a finite open cover of every nonzero
doubly-pure element. Exact skew elimination refines any admitted principal
pivot to full rank. Constant-rank kernel charts reuse rank_charts.py; the
larger incidence charts retain residual equations across rank changes.
These constructions give an implicit cover, not a classification of nonlinear
rank loci, smooth strata, attachments or the topology of the total pair space.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, replace
from fractions import Fraction
from typing import Any

import sympy as sp

import parallel
from cd_core import cd_sign
from rank_charts import (
    ChartPoint,
    ConstantRankChart,
    RationalMatrix,
    chart_transition,
    multiplication_matrix,
    rank_certificate,
)
from skew_schur_charts import (
    ClearedSchurPoint,
    ReducedRankCertificate,
    _fraction,
    _indices,
    _matrix,
    _rational,
    _reduced_certificate,
    _rows,
)

MAX_DIMENSION = 256


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _dimension(dimension: int) -> None:
    if type(dimension) is not int or not 4 <= dimension <= MAX_DIMENSION or dimension & (dimension - 1):
        raise ValueError("dimension must be a power of two from 4 through 256")


def _coordinates(coordinates: Sequence[int | Fraction], *, allow_zero: bool = False) -> tuple[Fraction, ...]:
    if isinstance(coordinates, (str, bytes)) or not isinstance(coordinates, Sequence):
        raise ValueError("coordinates require an exact rational sequence")
    _dimension(len(coordinates))
    values = tuple(_rational(value) for value in coordinates)
    if values[0] or values[len(values) // 2]:
        raise ValueError("doubly-pure coordinates require entries zero and half-dimension to vanish")
    if not allow_zero and not any(values):
        raise ValueError("the finite open cover excludes the origin")
    return values


def _stored_coordinates(values: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    if not isinstance(values, tuple) or any(type(value) is not Fraction for value in values):
        raise ValueError("retained coordinates require immutable Fractions")
    return _coordinates(values)


def _validate_chart(chart: PrincipalSkewChart) -> None:
    if not isinstance(chart, PrincipalSkewChart):
        raise ValueError("principal chart has the wrong type")
    _dimension(chart.dimension)
    indices = _indices(chart.pivot_indices, chart.dimension)
    if not indices or len(indices) % 2:
        raise ValueError("principal pivot requires a positive even number of indices")


def _verify_residual(matrix_rows: RationalMatrix, certificate: ReducedRankCertificate, dimension: int) -> bool:
    """Extend the existing minor/free-row certificate to every residual size."""
    try:
        if not isinstance(certificate, ReducedRankCertificate) or type(certificate.dimension) is not int:
            return False
        if certificate.dimension != dimension or not 0 <= dimension <= MAX_DIMENSION:
            return False
        matrix = _matrix(matrix_rows, dimension, dimension)
        rows = _indices(certificate.pivot_rows, dimension)
        columns = _indices(certificate.pivot_columns, dimension)
        if len(rows) != len(columns) or type(certificate.pivot_determinant) is not Fraction:
            return False
        free = tuple(index for index in range(dimension) if index not in columns)
        kernel = _matrix(certificate.kernel_basis, dimension, len(free))
        determinant = matrix.extract(rows, columns).det()
        return bool(
            determinant != 0
            and determinant == certificate.pivot_determinant
            and kernel.extract(free, range(len(free))) == sp.eye(len(free))
            and matrix * kernel == sp.zeros(dimension, len(free))
        )
    except ValueError, TypeError, AttributeError, IndexError:
        return False


@dataclass(frozen=True)
class PrincipalSkewChart:
    dimension: int
    pivot_indices: tuple[int, ...]

    @property
    def pivot_dimension(self) -> int:
        return len(self.pivot_indices)

    @property
    def reduced_dimension(self) -> int:
        return self.dimension - self.pivot_dimension

    @property
    def free_indices(self) -> tuple[int, ...]:
        return tuple(index for index in range(self.dimension) if index not in self.pivot_indices)

    @property
    def complement(self) -> RationalMatrix:
        _validate_chart(self)
        return _rows(sp.eye(self.dimension)[:, list(self.pivot_indices)])

    @property
    def free_frame(self) -> RationalMatrix:
        _validate_chart(self)
        return _rows(sp.eye(self.dimension)[:, list(self.free_indices)])

    @property
    def projection(self) -> RationalMatrix:
        _validate_chart(self)
        return _rows(sp.eye(self.dimension)[list(self.free_indices), :])

    def reduce(self, coordinates: Sequence[int | Fraction]) -> PrincipalSkewPoint:
        """Retain all ranks on the principal determinant's nonvanishing domain."""
        _validate_chart(self)
        values = _coordinates(coordinates)
        if len(values) != self.dimension:
            raise ValueError("point dimension differs from the principal chart")
        matrix = sp.Matrix(multiplication_matrix(values))
        pivot = matrix.extract(self.pivot_indices, self.pivot_indices)
        determinant = pivot.det()
        if determinant == 0:
            raise ValueError("principal determinant vanishes outside the pivot domain")
        cross = matrix.extract(self.pivot_indices, self.free_indices)
        diagonal = matrix.extract(self.free_indices, self.free_indices)
        inverse_cross = pivot.inv() * cross
        schur = diagonal + cross.T * inverse_cross
        complement = _matrix(self.complement, self.dimension, self.pivot_dimension)
        free = _matrix(self.free_frame, self.dimension, self.reduced_dimension)
        lift = free - complement * inverse_cross
        congruence = sp.eye(self.dimension)
        congruence[: self.pivot_dimension, self.pivot_dimension :] = -inverse_cross
        certificate = _reduced_certificate(schur)
        reduced_kernel = _matrix(certificate.kernel_basis, self.reduced_dimension, certificate.nullity)
        full_kernel = lift * reduced_kernel
        residual_free = tuple(
            index for index in range(self.reduced_dimension) if index not in certificate.pivot_columns
        )
        kernel_projection = _matrix(self.projection, self.reduced_dimension, self.dimension).extract(
            residual_free, range(self.dimension)
        )
        point = PrincipalSkewPoint(
            self,
            values,
            _rows(matrix),
            _rows(pivot),
            _rows(cross),
            _rows(diagonal),
            _fraction(determinant),
            _rows(schur),
            _rows(lift),
            _rows(lift.T * lift),
            _rows(congruence),
            certificate,
            _rows(full_kernel),
            _rows(kernel_projection),
            _rows(full_kernel.T * full_kernel),
        )
        _require(verify_principal_skew_point(point), "constructed principal point fails verification")
        return point

    def symbolic_domain(self) -> PrincipalPolynomialContract:
        _validate_chart(self)
        return PrincipalPolynomialContract(self)


@dataclass(frozen=True)
class PrincipalSkewPoint:
    chart: PrincipalSkewChart
    coordinates: tuple[Fraction, ...]
    matrix: RationalMatrix
    pivot: RationalMatrix
    cross: RationalMatrix
    diagonal: RationalMatrix
    pivot_determinant: Fraction
    schur_complement: RationalMatrix
    lift: RationalMatrix
    gram_metric: RationalMatrix
    congruence: RationalMatrix
    reduced_certificate: ReducedRankCertificate
    full_kernel: RationalMatrix
    kernel_projection: RationalMatrix
    kernel_metric: RationalMatrix

    @property
    def rank(self) -> int:
        return self.chart.pivot_dimension + self.reduced_certificate.rank

    @property
    def nullity(self) -> int:
        return self.reduced_certificate.nullity

    def constant_rank_chart(self) -> ChartPoint:
        """Refine to the existing constant-rank kernel-bundle interface."""
        if not verify_principal_skew_point(self):
            raise ValueError("kernel refinement requires an intact principal point")
        selection = select_maximal_principal_pivot(self.coordinates, self.chart.pivot_indices)
        return ConstantRankChart(
            self.chart.dimension, "left", selection.pivot_indices, selection.pivot_indices
        ).certify(self.coordinates)


def verify_principal_skew_point(point: PrincipalSkewPoint) -> bool:
    """Verify provenance, residual rank bounds, the full kernel and its metric."""
    try:
        if not isinstance(point, PrincipalSkewPoint):
            return False
        _validate_chart(point.chart)
        chart = point.chart
        dimension, pivot_size, residual_size = chart.dimension, chart.pivot_dimension, chart.reduced_dimension
        values = _stored_coordinates(point.coordinates)
        if len(values) != dimension or point.matrix != multiplication_matrix(values):
            return False
        matrix = _matrix(point.matrix, dimension, dimension)
        pivot = _matrix(point.pivot, pivot_size, pivot_size)
        cross = _matrix(point.cross, pivot_size, residual_size)
        diagonal = _matrix(point.diagonal, residual_size, residual_size)
        schur = _matrix(point.schur_complement, residual_size, residual_size)
        lift = _matrix(point.lift, dimension, residual_size)
        metric = _matrix(point.gram_metric, residual_size, residual_size)
        congruence = _matrix(point.congruence, dimension, dimension)
        if not _verify_residual(point.schur_complement, point.reduced_certificate, residual_size):
            return False
        nullity = point.nullity
        reduced_kernel = _matrix(point.reduced_certificate.kernel_basis, residual_size, nullity)
        full_kernel = _matrix(point.full_kernel, dimension, nullity)
        kernel_projection = _matrix(point.kernel_projection, nullity, dimension)
        kernel_metric = _matrix(point.kernel_metric, nullity, nullity)
        complement = _matrix(chart.complement, dimension, pivot_size)
        free = _matrix(chart.free_frame, dimension, residual_size)
        projection = _matrix(chart.projection, residual_size, dimension)
        if (
            type(point.pivot_determinant) is not Fraction
            or point.pivot_determinant == 0
            or pivot != matrix.extract(chart.pivot_indices, chart.pivot_indices)
            or pivot.det() != point.pivot_determinant
        ):
            return False
        inverse_cross = pivot.inv() * cross
        expected_congruence = sp.eye(dimension)
        expected_congruence[:pivot_size, pivot_size:] = -inverse_cross
        transform = complement.row_join(free)
        blocked = pivot.row_join(cross).col_join((-cross.T).row_join(diagonal))
        residual_free = tuple(
            index for index in range(residual_size) if index not in point.reduced_certificate.pivot_columns
        )
        return bool(
            matrix + matrix.T == sp.zeros(dimension)
            and cross == matrix.extract(chart.pivot_indices, chart.free_indices)
            and diagonal == matrix.extract(chart.free_indices, chart.free_indices)
            and transform.T * matrix * transform == blocked
            and schur == diagonal + cross.T * inverse_cross
            and schur + schur.T == sp.zeros(residual_size)
            and congruence == expected_congruence
            and congruence.T * blocked * congruence == sp.diag(pivot, schur)
            and lift == free - complement * inverse_cross
            and matrix * lift == free * schur
            and projection * lift == sp.eye(residual_size)
            and metric == lift.T * lift
            and full_kernel == lift * reduced_kernel
            and matrix * full_kernel == sp.zeros(dimension, nullity)
            and kernel_projection == projection.extract(residual_free, range(dimension))
            and kernel_projection * full_kernel == sp.eye(nullity)
            and kernel_metric == full_kernel.T * full_kernel
        )
    except ValueError, TypeError, AttributeError, IndexError:
        return False


def principal_cover(dimension: int) -> tuple[PrincipalSkewChart, ...]:
    """Return half-dimension minus one coordinate-quaternion pivot domains."""
    _dimension(dimension)
    half = dimension // 2
    return tuple(PrincipalSkewChart(dimension, (0, half, index, half + index)) for index in range(1, half))


@dataclass(frozen=True)
class PrincipalCoverSelection:
    coordinates: tuple[Fraction, ...]
    pair_norms_squared: tuple[Fraction, ...]
    selected_index: int
    input_norm_squared: Fraction
    selected_pair_norm_squared: Fraction
    pivot_determinant: Fraction
    inverse_norm_squared: Fraction

    @property
    def chart(self) -> PrincipalSkewChart:
        half = len(self.coordinates) // 2
        return PrincipalSkewChart(len(self.coordinates), (0, half, self.selected_index, half + self.selected_index))


def select_principal_cover(coordinates: Sequence[int | Fraction]) -> PrincipalCoverSelection:
    """Maximize the exact pair norm, breaking ties by the lowest basis index."""
    values = _coordinates(coordinates)
    half = len(values) // 2
    norms = tuple(values[index] ** 2 + values[half + index] ** 2 for index in range(1, half))
    position = max(range(half - 1), key=lambda index: norms[index])
    selected = norms[position]
    selection = PrincipalCoverSelection(
        values, norms, position + 1, sum(norms, Fraction(0)), selected, selected**2, 1 / selected
    )
    _require(verify_principal_cover_selection(selection), "constructed cover selector fails verification")
    return selection


def select_cover_chart(coordinates: Sequence[int | Fraction]) -> PrincipalSkewChart:
    return select_principal_cover(coordinates).chart


def verify_principal_cover_selection(selection: PrincipalCoverSelection) -> bool:
    try:
        if not isinstance(selection, PrincipalCoverSelection):
            return False
        values = _stored_coordinates(selection.coordinates)
        half = len(values) // 2
        if (
            type(selection.selected_index) is not int
            or not 1 <= selection.selected_index < half
            or not isinstance(selection.pair_norms_squared, tuple)
            or any(type(value) is not Fraction for value in selection.pair_norms_squared)
            or any(
                type(value) is not Fraction
                for value in (
                    selection.input_norm_squared,
                    selection.selected_pair_norm_squared,
                    selection.pivot_determinant,
                    selection.inverse_norm_squared,
                )
            )
        ):
            return False
        norms = tuple(values[index] ** 2 + values[half + index] ** 2 for index in range(1, half))
        position = max(range(half - 1), key=lambda index: norms[index])
        selected = norms[position]
        norm = sum(norms, Fraction(0))
        return bool(
            selection.pair_norms_squared == norms
            and selection.selected_index == position + 1
            and selection.input_norm_squared == norm
            and selection.selected_pair_norm_squared == selected
            and selection.pivot_determinant == selected**2
            and selection.inverse_norm_squared == 1 / selected
            and selected * (half - 1) >= norm
            and selection.pivot_determinant * (half - 1) ** 2 >= norm**2
            and selection.inverse_norm_squared * norm <= half - 1
        )
    except ValueError, TypeError, AttributeError, IndexError:
        return False


@dataclass(frozen=True)
class PrincipalPivotStep:
    pair_indices: tuple[int, int]
    pivot_entry: Fraction


@dataclass(frozen=True)
class PrincipalPivotSelection:
    coordinates: tuple[Fraction, ...]
    initial_indices: tuple[int, ...]
    pivot_indices: tuple[int, ...]
    steps: tuple[PrincipalPivotStep, ...]
    pivot_determinant: Fraction

    @property
    def chart(self) -> PrincipalSkewChart:
        return PrincipalSkewChart(len(self.coordinates), self.pivot_indices)


def _eliminate_principal(values: tuple[Fraction, ...], initial_indices: tuple[int, ...]) -> PrincipalPivotSelection:
    dimension = len(values)
    initial = _indices(initial_indices, dimension)
    if len(initial) % 2:
        raise ValueError("initial principal pivot size must be even")
    matrix = sp.Matrix(multiplication_matrix(values))
    pivot = matrix.extract(initial, initial)
    determinant = pivot.det()
    if determinant == 0:
        raise ValueError("initial principal pivot is singular")
    selected = list(initial)
    remaining = [index for index in range(dimension) if index not in initial]
    cross = matrix.extract(initial, remaining)
    residual = matrix.extract(remaining, remaining) + cross.T * pivot.inv() * cross
    steps = []
    while any(residual):
        pair = next(
            (
                (row, column)
                for row in range(residual.rows)
                for column in range(row + 1, residual.cols)
                if residual[row, column] != 0
            ),
            None,
        )
        if pair is None:
            raise RuntimeError("nonzero skew residual has no off-diagonal pivot")
        row, column = pair
        entry = residual[row, column]
        pair_indices = (remaining[row], remaining[column])
        steps.append(PrincipalPivotStep(pair_indices, _fraction(entry)))
        pair_positions = (row, column)
        rest = tuple(index for index in range(len(remaining)) if index not in pair_positions)
        small_pivot = residual.extract(pair_positions, pair_positions)
        small_cross = residual.extract(pair_positions, rest)
        residual = residual.extract(rest, rest) + small_cross.T * small_pivot.inv() * small_cross
        determinant *= entry**2
        selected.extend(pair_indices)
        remaining = [remaining[index] for index in rest]
    return PrincipalPivotSelection(values, initial, tuple(selected), tuple(steps), _fraction(determinant))


def select_maximal_principal_pivot(
    coordinates: Sequence[int | Fraction], initial_indices: tuple[int, ...] = ()
) -> PrincipalPivotSelection:
    """Construct a maximal nonsingular principal minor by exact skew elimination."""
    values = _coordinates(coordinates)
    selection = _eliminate_principal(values, initial_indices)
    _require(verify_principal_pivot_selection(selection), "constructed principal pivot selection fails verification")
    return selection


def verify_principal_pivot_selection(selection: PrincipalPivotSelection) -> bool:
    try:
        if not isinstance(selection, PrincipalPivotSelection):
            return False
        values = _stored_coordinates(selection.coordinates)
        _indices(selection.initial_indices, len(values))
        _indices(selection.pivot_indices, len(values))
        if type(selection.pivot_determinant) is not Fraction or not isinstance(selection.steps, tuple):
            return False
        for step in selection.steps:
            if (
                not isinstance(step, PrincipalPivotStep)
                or len(_indices(step.pair_indices, len(values))) != 2
                or type(step.pivot_entry) is not Fraction
                or step.pivot_entry == 0
            ):
                return False
        if selection != _eliminate_principal(values, selection.initial_indices):
            return False
        point = selection.chart.reduce(values)
        return point.reduced_certificate.rank == 0 and point.pivot_determinant == selection.pivot_determinant
    except ValueError, TypeError, AttributeError, IndexError:
        return False


@dataclass(frozen=True)
class PrincipalOverlap:
    source: PrincipalSkewPoint
    target: PrincipalSkewPoint
    transport: RationalMatrix
    reverse_transport: RationalMatrix
    correction: RationalMatrix
    residual_intertwiner: RationalMatrix
    kernel_transport: RationalMatrix
    reverse_kernel_transport: RationalMatrix


def build_overlap(source: PrincipalSkewPoint, target: PrincipalSkewPoint) -> PrincipalOverlap:
    """Map source to target coordinates, restricting ambient maps to kernels."""
    if not verify_principal_skew_point(source) or not verify_principal_skew_point(target):
        raise ValueError("overlap requires intact principal points")
    if source.coordinates != target.coordinates:
        raise ValueError("overlap requires one coefficient point")
    dimension = source.chart.dimension
    source_size, target_size = source.chart.reduced_dimension, target.chart.reduced_dimension
    source_lift = _matrix(source.lift, dimension, source_size)
    target_lift = _matrix(target.lift, dimension, target_size)
    source_projection = _matrix(source.chart.projection, source_size, dimension)
    target_projection = _matrix(target.chart.projection, target_size, dimension)
    target_complement = _matrix(target.chart.complement, dimension, target.chart.pivot_dimension)
    source_free = _matrix(source.chart.free_frame, dimension, source_size)
    correction = (
        target_complement
        * _matrix(target.pivot, target.chart.pivot_dimension, target.chart.pivot_dimension).inv()
        * target_complement.T
        * source_free
    )
    nullity = source.nullity
    overlap = PrincipalOverlap(
        source,
        target,
        _rows(target_projection * source_lift),
        _rows(source_projection * target_lift),
        _rows(correction),
        _rows(target_lift.T * source_free),
        _rows(_matrix(target.kernel_projection, nullity, dimension) * _matrix(source.full_kernel, dimension, nullity)),
        _rows(_matrix(source.kernel_projection, nullity, dimension) * _matrix(target.full_kernel, dimension, nullity)),
    )
    _require(verify_principal_overlap(overlap), "constructed principal overlap fails verification")
    return overlap


def verify_principal_overlap(overlap: PrincipalOverlap) -> bool:
    """Check universal residual-factor defects and exact kernel isomorphisms."""
    try:
        if not isinstance(overlap, PrincipalOverlap):
            return False
        source, target = overlap.source, overlap.target
        if not verify_principal_skew_point(source) or not verify_principal_skew_point(target):
            return False
        if source.coordinates != target.coordinates or source.nullity != target.nullity:
            return False
        dimension, nullity = source.chart.dimension, source.nullity
        source_size, target_size = source.chart.reduced_dimension, target.chart.reduced_dimension
        source_lift = _matrix(source.lift, dimension, source_size)
        target_lift = _matrix(target.lift, dimension, target_size)
        source_projection = _matrix(source.chart.projection, source_size, dimension)
        target_projection = _matrix(target.chart.projection, target_size, dimension)
        source_free = _matrix(source.chart.free_frame, dimension, source_size)
        target_complement = _matrix(target.chart.complement, dimension, target.chart.pivot_dimension)
        source_residual = _matrix(source.schur_complement, source_size, source_size)
        target_residual = _matrix(target.schur_complement, target_size, target_size)
        source_kernel = _matrix(source.reduced_certificate.kernel_basis, source_size, nullity)
        target_kernel = _matrix(target.reduced_certificate.kernel_basis, target_size, nullity)
        source_full = _matrix(source.full_kernel, dimension, nullity)
        target_full = _matrix(target.full_kernel, dimension, nullity)
        transport = _matrix(overlap.transport, target_size, source_size)
        reverse = _matrix(overlap.reverse_transport, source_size, target_size)
        correction = _matrix(overlap.correction, dimension, source_size)
        intertwiner = _matrix(overlap.residual_intertwiner, target_size, source_size)
        kernel_transport = _matrix(overlap.kernel_transport, nullity, nullity)
        kernel_reverse = _matrix(overlap.reverse_kernel_transport, nullity, nullity)
        return bool(
            transport == target_projection * source_lift
            and reverse == source_projection * target_lift
            and correction
            == target_complement
            * _matrix(target.pivot, target.chart.pivot_dimension, target.chart.pivot_dimension).inv()
            * target_complement.T
            * source_free
            and intertwiner == target_lift.T * source_free
            and target_lift * transport - source_lift == -correction * source_residual
            and target_residual * transport == intertwiner * source_residual
            and reverse * transport - sp.eye(source_size) == -source_projection * correction * source_residual
            and kernel_transport == _matrix(target.kernel_projection, nullity, dimension) * source_full
            and kernel_reverse == _matrix(source.kernel_projection, nullity, dimension) * target_full
            and transport * source_kernel == target_kernel * kernel_transport
            and reverse * target_kernel == source_kernel * kernel_reverse
            and kernel_reverse * kernel_transport == sp.eye(nullity)
            and kernel_transport * kernel_reverse == sp.eye(nullity)
            and target_full * kernel_transport == source_full
            and kernel_transport.T * _matrix(target.kernel_metric, nullity, nullity) * kernel_transport
            == _matrix(source.kernel_metric, nullity, nullity)
            and source_kernel.T
            * transport.T
            * _matrix(target.gram_metric, target_size, target_size)
            * transport
            * source_kernel
            == _matrix(source.kernel_metric, nullity, nullity)
        )
    except ValueError, TypeError, AttributeError, IndexError:
        return False


def verify_overlap_cocycle(first: PrincipalOverlap, second: PrincipalOverlap, direct: PrincipalOverlap) -> bool:
    """Check source->middle->target transport on the complete pointwise kernel."""
    try:
        if not all(verify_principal_overlap(overlap) for overlap in (first, second, direct)):
            return False
        if first.target != second.source or direct.source != first.source or direct.target != second.target:
            return False
        source_size, middle_size, target_size = (
            first.source.chart.reduced_dimension,
            first.target.chart.reduced_dimension,
            second.target.chart.reduced_dimension,
        )
        dimension, nullity = first.source.chart.dimension, first.source.nullity
        defect = _matrix(second.transport, target_size, middle_size) * _matrix(
            first.transport, middle_size, source_size
        ) - _matrix(direct.transport, target_size, source_size)
        correction = (
            -_matrix(second.target.chart.projection, target_size, dimension)
            * _matrix(first.correction, dimension, source_size)
            * _matrix(first.source.schur_complement, source_size, source_size)
        )
        return bool(
            defect == correction
            and defect * _matrix(first.source.reduced_certificate.kernel_basis, source_size, nullity)
            == sp.zeros(target_size, nullity)
            and _matrix(second.kernel_transport, nullity, nullity) * _matrix(first.kernel_transport, nullity, nullity)
            == _matrix(direct.kernel_transport, nullity, nullity)
        )
    except ValueError, TypeError, AttributeError, IndexError:
        return False


@dataclass(frozen=True)
class PrincipalPolynomialContract:
    chart: PrincipalSkewChart

    def symbolic_blocks(self) -> tuple[tuple[sp.Symbol, ...], sp.Matrix, sp.Matrix, sp.Matrix]:
        """Build linear principal blocks while retaining determinants unexpanded."""
        _validate_chart(self.chart)
        dimension = self.chart.dimension
        indices = tuple(index for index in range(dimension) if index not in (0, dimension // 2))
        symbols = tuple(sp.Symbol(f"x{index}", real=True) for index in indices)
        lookup = dict(zip(indices, symbols, strict=True))

        def block(rows: tuple[int, ...], columns: tuple[int, ...]) -> sp.Matrix:
            return sp.Matrix(
                len(rows),
                len(columns),
                lambda row, column: (
                    lookup.get(rows[row] ^ columns[column], sp.Integer(0))
                    * cd_sign(dimension, rows[row] ^ columns[column], columns[column])
                ),
            )

        pivot, free = self.chart.pivot_indices, self.chart.free_indices
        return symbols, block(pivot, pivot), block(pivot, free), block(free, free)

    def determinant_expression(self) -> sp.Expr:
        return sp.Determinant(sp.ImmutableMatrix(self.symbolic_blocks()[1]))

    def cofactor_expression(self, row: int, column: int) -> sp.Expr:
        _validate_chart(self.chart)
        pivot_size = self.chart.pivot_dimension
        if type(row) is not int or type(column) is not int or not 0 <= row < pivot_size or not 0 <= column < pivot_size:
            raise ValueError("adjugate indices lie outside the pivot")
        pivot = self.symbolic_blocks()[1]
        minor = pivot.extract(
            [index for index in range(pivot_size) if index != column],
            [index for index in range(pivot_size) if index != row],
        )
        return (-1) ** (row + column) * sp.Determinant(sp.ImmutableMatrix(minor))

    def evaluate(self, coordinates: Sequence[int | Fraction]) -> ClearedSchurPoint:
        _validate_chart(self.chart)
        values = _coordinates(coordinates, allow_zero=True)
        if len(values) != self.chart.dimension:
            raise ValueError("polynomial evaluation dimension differs from the chart")
        matrix = sp.Matrix(multiplication_matrix(values))
        pivot = matrix.extract(self.chart.pivot_indices, self.chart.pivot_indices)
        cross = matrix.extract(self.chart.pivot_indices, self.chart.free_indices)
        diagonal = matrix.extract(self.chart.free_indices, self.chart.free_indices)
        determinant = pivot.det()
        # An even singular skew matrix has corank at least two, so every
        # codimension-one minor vanishes and its adjugate is zero.
        adjugate = determinant * pivot.inv() if determinant else sp.zeros(pivot.rows)
        schur = determinant * diagonal + cross.T * adjugate * cross
        complement = _matrix(self.chart.complement, self.chart.dimension, self.chart.pivot_dimension)
        free = _matrix(self.chart.free_frame, self.chart.dimension, self.chart.reduced_dimension)
        lift = determinant * free - complement * adjugate * cross
        _require(matrix * lift == free * schur, "cleared principal lift identity fails")
        return ClearedSchurPoint(_fraction(determinant), _rows(adjugate), _rows(schur), _rows(lift))

    def description(self) -> dict[str, object]:
        _validate_chart(self.chart)
        return {
            "dimension": self.chart.dimension,
            "pivot_indices": list(self.chart.pivot_indices),
            "coefficient_domain": "real doubly-pure nonzero elements",
            "chart_inequation": "delta=det(A)!=0",
            "cleared_residual": "Sbar=delta*D+B.T*adj(A)*B",
            "cleared_lift": "Hbar=delta*V-U*adj(A)*B",
            "rank_locus": "rank(L)=pivot_size+rank(Sbar) on delta!=0",
            "kernel_incidence": "Sbar*w=0; w.T*Hbar.T*Hbar*w=delta^2; y=Hbar*w/delta",
            "scope": (
                "finite implicit cover; nonlinear rank geometry, smooth strata and global topology remain separate"
            ),
        }


def _fixture(sparse: dict[int, int | Fraction], dimension: int = 32) -> tuple[Fraction, ...]:
    return tuple(Fraction(sparse.get(index, 0)) for index in range(dimension))


def _audit_fixture(task: tuple[str, dict[int, int | Fraction], int]) -> dict[str, object]:
    name, sparse, expected_nullity = task
    values = _fixture(sparse)
    selection = select_principal_cover(values)
    first = selection.chart.reduce(values)
    maximal = select_maximal_principal_pivot(values, first.chart.pivot_indices)
    last = maximal.chart.reduce(values)
    independent = rank_certificate(values)
    _require(
        first.nullity == last.nullity == independent.nullity == expected_nullity,
        "principal rank differs from full rank certificate",
    )
    bundle = first.constant_rank_chart()
    _require(len(bundle.free_columns) == expected_nullity, "constant-rank refinement changes kernel dimension")
    bundle_frame = _matrix(bundle.kernel_frame, 32, expected_nullity)
    _require(bundle.kernel_frame == last.full_kernel, "principal refinement differs from the constant-rank frame")
    _require(_rows(bundle_frame.T * bundle_frame) == last.kernel_metric, "constant-rank Gram metric differs")
    alternate_index = next(
        index for index in range(1, 16) if index != selection.selected_index and selection.pair_norms_squared[index - 1]
    )
    alternate = select_maximal_principal_pivot(values, (0, 16, alternate_index, 16 + alternate_index))
    alternate_point = alternate.chart.reduce(values)
    alternate_bundle = alternate_point.constant_rank_chart()
    exact_overlap = build_overlap(last, alternate_point)
    _require(
        exact_overlap.kernel_transport == chart_transition(alternate_bundle, bundle),
        "principal kernel transport differs from the existing constant-rank transition",
    )
    overlap = build_overlap(first, last)
    reverse = build_overlap(last, first)
    identity = build_overlap(first, first)
    _require(verify_overlap_cocycle(overlap, reverse, identity), "principal overlap cocycle fails")
    return {
        "label": name,
        "nullity": first.nullity,
        "selected_pair": selection.selected_index,
        "pivot_indices": list(first.chart.pivot_indices),
        "maximal_pivot_size": last.chart.pivot_dimension,
        "elimination_steps": len(maximal.steps),
        "initial_pivot_determinant": str(first.pivot_determinant),
        "rank_certificate_matches": True,
        "rectangular_overlap_shape": [last.chart.reduced_dimension, first.chart.reduced_dimension],
    }


def _mutated(rows: RationalMatrix) -> RationalMatrix:
    return tuple(
        tuple(value + int(row == 0 and column == 0) for column, value in enumerate(entries))
        for row, entries in enumerate(rows)
    )


def _audit_runtime_dimension(dimension: int) -> dict[str, object]:
    element = _fixture({1: Fraction(2, 3)}, dimension)
    selection = select_principal_cover(element)
    smaller = selection.chart.reduce(element)
    maximum = select_maximal_principal_pivot(element, smaller.chart.pivot_indices)
    maximal = maximum.chart.reduce(element)
    _require(
        smaller.rank == maximal.rank == maximum.chart.pivot_dimension == dimension
        and smaller.nullity == maximal.nullity == 0,
        "generic-dimension principal cover or maximal refinement fails",
    )
    empty_frame = tuple(() for _ in range(dimension))
    _require(
        smaller.full_kernel == maximal.full_kernel == maximal.lift == empty_frame,
        "invertible kernel or maximal lift loses zero-column shape",
    )
    _require(
        maximal.schur_complement == maximal.gram_metric == maximal.kernel_metric == (),
        "invertible residual or metric loses zero-dimensional shape",
    )
    _require(
        smaller.kernel_projection == maximal.kernel_projection == (),
        "invertible kernel projection loses zero-row shape",
    )
    bundle = ConstantRankChart(dimension, "left", maximum.pivot_indices, maximum.pivot_indices).certify(element)
    _require(
        bundle.kernel_frame == empty_frame and bundle.free_columns == (),
        "constant-rank maximal refinement loses empty kernel shape",
    )
    overlap = build_overlap(smaller, maximal)
    _require(
        overlap.transport == overlap.kernel_transport == overlap.reverse_kernel_transport == (),
        "invertible overlap loses zero-row transport shape",
    )
    _require(
        overlap.reverse_transport == tuple(() for _ in range(smaller.chart.reduced_dimension)),
        "invertible reverse overlap loses zero-column shape",
    )
    _require(
        verify_principal_skew_point(smaller)
        and verify_principal_skew_point(maximal)
        and verify_principal_pivot_selection(maximum)
        and verify_principal_overlap(overlap),
        "generic-dimension runtime certificates fail verification",
    )
    return {
        "dimension": dimension,
        "cover_size": len(principal_cover(dimension)),
        "rank": smaller.rank,
        "maximal_pivot_size": maximum.chart.pivot_dimension,
        "elimination_steps": len(maximum.steps),
        "nullity": smaller.nullity,
        "full_kernel_shape": [dimension, 0],
        "maximal_lift_shape": [dimension, 0],
        "maximal_residual_shape": [0, 0],
        "overlap_transport_shape": [0, smaller.chart.reduced_dimension],
        "kernel_transport_shape": [0, 0],
        "runtime_certificates_verified": True,
        "constant_rank_empty_frame_matches": True,
    }


def audit_principal_skew_atlas() -> dict[str, object]:
    fixtures = [
        ("nullity0", {1: 1, 3: 1, 10: 1}, 0),
        ("nullity4", {1: 1, 10: 2, 18: 3, 25: -4}, 4),
        ("nullity8", {1: 1, 10: 1}, 8),
        ("nullity12", {1: 1, 18: 1}, 12),
        ("nullity16", {1: 1, 10: 1, 18: 1, 25: -1}, 16),
        ("dense", {index: Fraction(index + 1, 31) for index in range(32) if index not in (0, 16)}, 0),
    ]
    records = parallel.ordered_map(_audit_fixture, fixtures, min_items=2)
    values = _fixture({1: 1, 10: 1})
    point = select_cover_chart(values).reduce(values)
    target = PrincipalSkewChart(32, (0, 16, 10, 26)).reduce(values)
    overlap = build_overlap(point, target)
    damaged = 0
    for field in (
        "matrix",
        "pivot",
        "cross",
        "diagonal",
        "schur_complement",
        "lift",
        "gram_metric",
        "congruence",
        "full_kernel",
        "kernel_projection",
        "kernel_metric",
    ):
        changed = replace(point, **dict[str, Any]({field: _mutated(getattr(point, field))}))
        _require(not verify_principal_skew_point(changed), f"altered principal {field} accepted")
        damaged += 1
    for field in (
        "transport",
        "reverse_transport",
        "correction",
        "residual_intertwiner",
        "kernel_transport",
        "reverse_kernel_transport",
    ):
        changed_overlap = replace(overlap, **dict[str, Any]({field: _mutated(getattr(overlap, field))}))
        _require(not verify_principal_overlap(changed_overlap), f"altered overlap {field} accepted")
        damaged += 1
    selected = select_principal_cover(values)
    _require(
        not verify_principal_cover_selection(replace(selected, selected_index=10)), "selector tie mutation accepted"
    )
    damaged += 1
    maximum = select_maximal_principal_pivot(values, point.chart.pivot_indices)
    _require(
        not verify_principal_pivot_selection(replace(maximum, pivot_determinant=maximum.pivot_determinant + 1)),
        "principal elimination mutation accepted",
    )
    damaged += 1
    for change in (
        {"coordinates": tuple(value * 2 for value in selected.coordinates)},
        {"pair_norms_squared": tuple(Fraction(0) for _ in selected.pair_norms_squared)},
        {"input_norm_squared": selected.input_norm_squared + 1},
        {"selected_pair_norm_squared": selected.selected_pair_norm_squared + 1},
        {"pivot_determinant": selected.pivot_determinant + 1},
        {"inverse_norm_squared": selected.inverse_norm_squared + 1},
    ):
        altered_selection = replace(selected, **dict[str, Any](change))
        _require(not verify_principal_cover_selection(altered_selection), "altered cover-selection metadata accepted")
        damaged += 1
    changed_steps = (replace(maximum.steps[0], pivot_entry=maximum.steps[0].pivot_entry + 1),) + maximum.steps[1:]
    _require(
        not verify_principal_pivot_selection(replace(maximum, steps=changed_steps)),
        "altered elimination pivot accepted",
    )
    damaged += 1
    for reduced_change in (
        {"dimension": True},
        {"pivot_rows": ()},
        {"pivot_columns": ()},
        {"pivot_determinant": point.reduced_certificate.pivot_determinant + 1},
        {"kernel_basis": _mutated(point.reduced_certificate.kernel_basis)},
    ):
        altered_reduced = replace(point.reduced_certificate, **dict[str, Any](reduced_change))
        _require(
            not verify_principal_skew_point(replace(point, reduced_certificate=altered_reduced)),
            "altered residual certificate accepted",
        )
        damaged += 1
    for point_change in ({"coordinates": tuple(2 * value for value in values)}, {"pivot_determinant": True}):
        _require(
            not verify_principal_skew_point(replace(point, **dict[str, Any](point_change))),
            "altered principal metadata accepted",
        )
        damaged += 1
    singular_cleared = point.chart.symbolic_domain().evaluate(_fixture({2: 1}))
    _require(
        singular_cleared.determinant == 0
        and not any(value for row in singular_cleared.lift_numerator for value in row),
        "singular cleared polynomial evaluation fails",
    )
    rejected = 0
    for invalid in ([0] * 32, [False] * 32, [0.0] * 32, [0] * 30, _fixture({0: 1}), _fixture({16: 1})):
        try:
            select_cover_chart(invalid)  # type: ignore[arg-type]
        except ValueError:
            rejected += 1
        else:
            raise RuntimeError("invalid atlas coordinates accepted")
    for invalid_chart in (
        PrincipalSkewChart(32, (0, 0)),
        PrincipalSkewChart(32, (True, 1)),
        PrincipalSkewChart(32, (0,)),
        PrincipalSkewChart(32, ()),
        PrincipalSkewChart(30, (0, 1)),
        PrincipalSkewChart(32, (0, 16, 2, 18)),
    ):
        try:
            invalid_chart.reduce(values)
        except ValueError:
            rejected += 1
        else:
            raise RuntimeError("invalid or singular principal chart accepted")
    dimension_records = parallel.ordered_map(_audit_runtime_dimension, (4, 8, 16, 64, 128, 256), min_items=2)
    return {
        "schema": "principal-skew-kernel-atlas-v1",
        "qpu_executed": False,
        "dimension32_cover_size": len(principal_cover(32)),
        "fixtures": records,
        "generic_dimensions": dimension_records,
        "damaged_fields_rejected": damaged,
        "invalid_inputs_rejected": rejected,
        "cover_scope": "all real nonzero doubly-pure elements by coordinate quaternion pivots",
        "classification_scope": (
            "implicit determinantal rank domains and kernel transport; "
            "smooth subdivisions and global topology remain open"
        ),
    }


def main() -> int:
    print(json.dumps(audit_principal_skew_atlas(), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
