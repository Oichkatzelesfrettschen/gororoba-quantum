"""Complete real rank loci and kernel attachments on a dimension-32 cone slice.

The affine slice e1+e18+A*e3+B*e8+C*e27 has rank 32 off the quadratic
cone, rank 24 on its punctured cone, and rank 20 at the origin of coefficient
space. Two global circle charts certify the kernel bundle. Exact projector
identities and endpoint incidence equations describe every attachment limit
within this slice; ambient neighborhoods retain separate coverage obligations.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from typing import Any

import sympy as sp

from cd_core import cd_sign

DIMENSION = 32
SUBGROUP = (0, 2, 9, 11, 17, 19, 24, 26)
REPRESENTATIVES = (0, 1, 4, 5)
INTERNAL_REPRESENTATIVES = (0, 1)
PIVOT_POSITIONS = (0, 1, 3, 4, 5, 7)
FREE_POSITIONS = (2, 6)
AMPLITUDE, SLOPE, SECOND_SLOPE = sp.symbols("u v w", real=True)
FIRST, SECOND, THIRD = sp.symbols("A B C", real=True)
CIRCLE_FIRST, CIRCLE_SECOND = sp.symbols("a b", real=True)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _equal(actual: Any, expected: Any, label: str) -> None:
    difference = actual - expected
    if isinstance(difference, sp.MatrixBase):
        valid = difference.applyfunc(sp.cancel) == sp.zeros(*difference.shape)
    else:
        valid = sp.cancel(difference) == 0
    _require(bool(valid), label)


def _rational(value: object) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise ValueError("exact rational inputs require integers or Fractions")
    return Fraction(value)


def _coefficients(values: Sequence[int | Fraction]) -> tuple[Fraction, Fraction, Fraction]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence) or len(values) != 3:
        raise ValueError("the affine slice requires exactly three rational coefficients")
    first, second, third = (_rational(value) for value in values)
    return first, second, third


def _chart(chart: str) -> None:
    if chart not in ("first", "second"):
        raise ValueError("the circle chart must be first or second")


def _indices(representative: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    columns = tuple(representative ^ offset for offset in SUBGROUP)
    return tuple(1 ^ column for column in columns), columns


def _symbolic_coordinates(first: Any, second: Any, third: Any) -> sp.Matrix:
    coordinates = sp.zeros(DIMENSION, 1)
    coordinates[1] = coordinates[18] = 1
    coordinates[3], coordinates[8], coordinates[27] = first, second, third
    return coordinates


def _operator(coordinates: sp.MatrixBase) -> sp.Matrix:
    return sp.Matrix(
        DIMENSION,
        DIMENSION,
        lambda row, column: cd_sign(DIMENSION, row ^ column, column) * coordinates[row ^ column],
    )


def _block(representative: int, coordinates: sp.MatrixBase) -> sp.Matrix:
    rows, columns = _indices(representative)
    return sp.Matrix(
        8,
        8,
        lambda row, column: (
            cd_sign(DIMENSION, rows[row] ^ columns[column], columns[column]) * coordinates[rows[row] ^ columns[column]]
        ),
    )


def _lift(representative: int, local: sp.MatrixBase) -> sp.Matrix:
    _, columns = _indices(representative)
    lifted = sp.zeros(DIMENSION, local.cols)
    for row, column in enumerate(columns):
        lifted[column, :] = local[row, :]
    return lifted


def _circle_coordinates(amplitude: Any, slope: Any, chart: str) -> sp.Matrix:
    _chart(chart)
    first = amplitude * (1 - slope**2) if chart == "first" else amplitude * (slope**2 - 1)
    return _symbolic_coordinates(first, 2 * amplitude * slope, amplitude * (1 + slope**2))


def _local_internal_frame(block: sp.Matrix) -> sp.Matrix:
    pivot = block.extract(PIVOT_POSITIONS, PIVOT_POSITIONS)
    solved = -(pivot.inv(method="DM") * block.extract(PIVOT_POSITIONS, FREE_POSITIONS)).applyfunc(sp.cancel)
    frame = sp.zeros(8, 2)
    for column, free_row in enumerate(FREE_POSITIONS):
        frame[free_row, column] = 1
    for row, pivot_row in enumerate(PIVOT_POSITIONS):
        frame[pivot_row, :] = solved[row, :]
    return frame


@lru_cache(maxsize=2)
def _internal_frame(chart: str) -> sp.ImmutableMatrix:
    coordinates = _circle_coordinates(AMPLITUDE, SLOPE, chart)
    frames = [
        _lift(representative, _local_internal_frame(_block(representative, coordinates))) for representative in (0, 1)
    ]
    return sp.ImmutableMatrix(sp.Matrix.hstack(*frames))


def _local_external_frame(representative: int, slope: Any) -> sp.Matrix:
    sign = 1 if representative == 4 else -1
    first = sp.Matrix([slope + 1, 0, 0, sign * (slope - 1), 0, -sign * (slope + 1), slope - 1, 0])
    second = sp.Matrix([0, slope + 1, sign * (slope - 1), 0, -sign * (slope + 1), 0, 0, slope - 1])
    return first.row_join(second)


@lru_cache(maxsize=1)
def _endpoint_frames() -> tuple[sp.ImmutableMatrix, sp.ImmutableMatrix, sp.ImmutableMatrix, sp.ImmutableMatrix]:
    center_coordinates = _symbolic_coordinates(0, 0, 0)
    fixed = sp.Matrix.hstack(
        *[
            _lift(representative, _local_internal_frame(_block(representative, center_coordinates)))
            for representative in INTERNAL_REPRESENTATIVES
        ]
    )
    external = sp.Matrix.hstack(
        *[_lift(representative, _local_external_frame(representative, SLOPE)) for representative in (4, 5)]
    )
    first = external.subs(SLOPE, 0)
    second = external.diff(SLOPE)
    fixed_projector = fixed * (fixed.T * fixed).inv() * fixed.T
    return tuple(sp.ImmutableMatrix(matrix) for matrix in (fixed, first, second, fixed_projector))


def _quaternion_complex_structure() -> sp.Matrix:
    return sp.Matrix(4, 4, lambda row, column: cd_sign(4, 1, column) if row == (1 ^ column) else 0)


def _global_external_frame(first: Any, second: Any) -> sp.Matrix:
    _, at_zero, at_infinity, _ = _endpoint_frames()
    complex_structure = _quaternion_complex_structure()
    return sp.Matrix(
        (
            at_zero * ((1 + first) * sp.eye(4) + second * complex_structure)
            + at_infinity * (second * sp.eye(4) + (1 - first) * complex_structure)
        )
        / 4
    ).applyfunc(sp.cancel)


def _circle_projector(slope: Any, chart: str) -> sp.Matrix:
    _chart(chart)
    _, at_zero, at_infinity, fixed_projector = _endpoint_frames()
    external = at_zero + slope * at_infinity if chart == "first" else slope * at_zero + at_infinity
    return sp.Matrix(fixed_projector + external * external.T / (4 * (1 + slope**2))).applyfunc(sp.cancel)


@dataclass(frozen=True)
class SliceClassification:
    coefficients: tuple[Fraction, Fraction, Fraction]
    delta: Fraction
    norm_squared: Fraction
    rank: int

    @property
    def nullity(self) -> int:
        return DIMENSION - self.rank


def slice_coordinates(coefficients: Sequence[int | Fraction]) -> tuple[Fraction, ...]:
    """Embed three exact rational coefficients into the named affine slice."""
    first, second, third = _coefficients(coefficients)
    values = {1: Fraction(1), 18: Fraction(1), 3: first, 8: second, 27: third}
    return tuple(values.get(index, Fraction(0)) for index in range(DIMENSION))


def classify_slice(coefficients: Sequence[int | Fraction]) -> SliceClassification:
    """Evaluate the complete real-locus formula at exact rational coefficients."""
    first, second, third = values = _coefficients(coefficients)
    delta = first**2 + second**2 - third**2
    rank = 32 if delta else 24 if any(values) else 20
    return SliceClassification(values, delta, Fraction(2) + first**2 + second**2 + third**2, rank)


def cone_kernel_frame(coefficients: Sequence[int | Fraction]) -> sp.ImmutableMatrix:
    """Return a full rational kernel frame on every nonzero rational cone point.

    The first chart covers C+A != 0; the second covers C-A != 0. Global internal
    pivots and the orthonormal external frame establish bundle triviality over
    both sheets of the punctured cone. The origin carries a larger kernel.
    """
    first, second, third = values = _coefficients(coefficients)
    if classify_slice(values).rank != 24:
        raise ValueError("the cone kernel frame requires a nonzero point with A^2+B^2=C^2")
    if third + first:
        chart, amplitude, slope = "first", (third + first) / 2, second / (third + first)
    else:
        chart, amplitude, slope = "second", (third - first) / 2, second / (third - first)
    internal = _internal_frame(chart).subs({AMPLITUDE: sp.Rational(amplitude), SLOPE: sp.Rational(slope)})
    external = _global_external_frame(sp.Rational(first / third), sp.Rational(second / third))
    frame = sp.Matrix(internal.row_join(external))
    matrix = _operator(sp.Matrix(slice_coordinates(values)))
    _equal(matrix * frame, sp.zeros(DIMENSION, 8), "rational cone frame action")
    _equal(external.T * external, sp.eye(4), "rational external orthonormal frame")
    _require(frame.rank() == 8, "rational cone frame independence")
    return sp.ImmutableMatrix(frame)


def circle_projector(slope: int | Fraction, chart: str = "first") -> sp.ImmutableMatrix:
    """Evaluate an endpoint rank-eight projector, including infinity at second/0."""
    _chart(chart)
    return sp.ImmutableMatrix(_circle_projector(sp.Rational(_rational(slope)), chart))


def attachment_image_contains(partner: Sequence[int | Fraction], require_unit: bool = False) -> bool:
    """Check endpoint containment and the six collinearity equations for limits.

    Unit partners belong to the attachment image exactly when their external
    coordinates alpha,beta form a rank-at-most-one 4-by-2 matrix. The optional
    unit condition restricts the homogeneous image to the endpoint sphere.
    """
    if type(require_unit) is not bool:
        raise ValueError("require_unit must be a boolean")
    if isinstance(partner, (str, bytes)) or not isinstance(partner, Sequence) or len(partner) != DIMENSION:
        raise ValueError("partners require exactly 32 rational coordinates")
    vector = sp.Matrix([sp.Rational(_rational(value)) for value in partner])
    center = _operator(_symbolic_coordinates(0, 0, 0))
    if center * vector != sp.zeros(DIMENSION, 1) or (require_unit and vector.dot(vector) != 1):
        return False
    _, at_zero, at_infinity, _ = _endpoint_frames()
    alpha, beta = at_zero.T * vector / 2, at_infinity.T * vector / 2
    return all(
        alpha[first] * beta[second] - alpha[second] * beta[first] == 0 for first, second in combinations(range(4), 2)
    )


def _sparse_matrix(matrix: sp.MatrixBase) -> dict[str, object]:
    return {
        "shape": [matrix.rows, matrix.cols],
        "nonzero_entries": [
            [row, column, str(sp.cancel(matrix[row, column]))]
            for row in range(matrix.rows)
            for column in range(matrix.cols)
            if matrix[row, column] != 0
        ],
    }


def _coordinates_record(coordinates: sp.MatrixBase) -> list[list[object]]:
    return [[index, str(sp.expand(value))] for index, value in enumerate(coordinates) if value != 0]


def _chart_certificate(chart: str) -> dict[str, object]:
    coordinates = _circle_coordinates(AMPLITUDE, SLOPE, chart)
    matrix = _operator(coordinates)
    records = []
    for representative in REPRESENTATIVES:
        block = _block(representative, coordinates)
        coefficients = (block.T * block).charpoly().all_coeffs()
        _equal(coefficients[-1], 0, "cone Gram constant coefficient")
        _equal(coefficients[-2], 0, "cone Gram linear coefficient")
        rank_witness = (
            256 * (1 + AMPLITUDE**2 * (1 + SLOPE**2) ** 2) ** 6
            if representative in INTERNAL_REPRESENTATIVES
            else 4096 * AMPLITUDE**8 * (1 + SLOPE**2) ** 8
        )
        _equal(coefficients[-3], rank_witness, "positive cone Gram rank-six witness")
        record: dict[str, object] = {
            "representative": representative,
            "gram_coefficient_z0": "0",
            "gram_coefficient_z1": "0",
            "gram_coefficient_z2": str(sp.factor(rank_witness)),
        }
        if representative in INTERNAL_REPRESENTATIVES:
            local = _local_internal_frame(block)
            determinant = block.extract(PIVOT_POSITIONS, PIVOT_POSITIONS).det(method="domain-ge")
            _equal(determinant, -4 * (1 + AMPLITUDE**2 * (1 + SLOPE**2) ** 2) ** 2, "global internal pivot")
            _equal(block * local, sp.zeros(8, 2), "global internal kernel action")
            _equal(local.extract(FREE_POSITIONS, (0, 1)), sp.eye(2), "global internal kernel independence")
            record.update(
                pivot_local_positions=PIVOT_POSITIONS,
                free_local_positions=FREE_POSITIONS,
                pivot_determinant=str(sp.factor(determinant)),
                local_kernel_frame=_sparse_matrix(local),
            )
        else:
            local = _local_external_frame(representative, SLOPE)
            if chart == "second":
                local = (SLOPE * local.subs(SLOPE, 1 / SLOPE)).applyfunc(sp.cancel)
            _equal(block * local, sp.zeros(8, 2), "global external kernel action")
            _equal(local.T * local, 4 * (1 + SLOPE**2) * sp.eye(2), "positive external Gram")
            record["local_kernel_frame"] = _sparse_matrix(local)
        records.append(record)
    internal = _internal_frame(chart)
    _, at_zero, at_infinity, _ = _endpoint_frames()
    external = at_zero + SLOPE * at_infinity if chart == "first" else SLOPE * at_zero + at_infinity
    _equal(matrix * internal, sp.zeros(32, 4), "global internal lifted action")
    _equal(matrix * external, sp.zeros(32, 4), "global external lifted action")
    _equal(internal.T * external, sp.zeros(4), "internal external orthogonality")
    internal_free_rows = tuple(
        _indices(representative)[1][position]
        for representative in INTERNAL_REPRESENTATIVES
        for position in FREE_POSITIONS
    )
    residual_rows = tuple(index for index in range(32) if index not in internal_free_rows)
    residual_frame = internal.extract(residual_rows, range(4))
    _equal(internal.extract(internal_free_rows, range(4)), sp.eye(4), "global internal free-row identity")
    _equal(
        internal.T * internal - sp.eye(4),
        residual_frame.T * residual_frame,
        "global internal Gram positivity certificate",
    )
    return {
        "chart": chart,
        "coordinates": _coordinates_record(coordinates),
        "domain": "u != 0; slope is any real number",
        "blocks": records,
        "internal_frame": _sparse_matrix(internal),
        "internal_free_rows": internal_free_rows,
        "internal_gram": _sparse_matrix((internal.T * internal).applyfunc(sp.cancel)),
        "internal_gram_positive_certificate": "F.T*F=I+R.T*R with R the complement of the recorded free rows",
        "external_frame": _sparse_matrix(external),
    }


def _slice_rank_certificate() -> dict[str, object]:
    coordinates = _symbolic_coordinates(FIRST, SECOND, THIRD)
    matrix = _operator(coordinates)
    delta = FIRST**2 + SECOND**2 - THIRD**2
    norm = 2 + FIRST**2 + SECOND**2 + THIRD**2
    covered_rows: list[int] = []
    covered_columns: list[int] = []
    records = []
    for representative in REPRESENTATIVES:
        rows, columns = _indices(representative)
        covered_rows.extend(rows)
        covered_columns.extend(columns)
        outside_columns = tuple(column for column in range(32) if column not in columns)
        _equal(matrix.extract(rows, outside_columns), sp.zeros(8, 24), "unrestricted off-sector action")
        block = matrix.extract(rows, columns)
        expected = -(delta**2) * norm**2 if representative in INTERNAL_REPRESENTATIVES else delta**4
        _equal(block.det(method="domain-ge"), expected, "unrestricted slice determinant identity")
        center_rank = _block(representative, _symbolic_coordinates(0, 0, 0)).rank()
        _require(center_rank == (6 if representative in INTERNAL_REPRESENTATIVES else 4), "endpoint sector rank")
        records.append(
            {
                "representative": representative,
                "input_columns": columns,
                "output_rows": rows,
                "determinant": str(sp.factor(expected)),
                "center_rank": center_rank,
            }
        )
    _require(sorted(covered_rows) == sorted(covered_columns) == list(range(32)), "full input/output sector partitions")
    first_inverse_amplitude, first_inverse_slope = (THIRD + FIRST) / 2, SECOND / (THIRD + FIRST)
    second_inverse_amplitude, second_inverse_slope = (THIRD - FIRST) / 2, SECOND / (THIRD - FIRST)
    first_residual = _circle_coordinates(first_inverse_amplitude, first_inverse_slope, "first") - coordinates
    second_residual = _circle_coordinates(second_inverse_amplitude, second_inverse_slope, "second") - coordinates
    expected_first, expected_second = sp.zeros(32, 1), sp.zeros(32, 1)
    expected_first[3], expected_first[27] = -delta / 2, delta / 2
    expected_second[3] = expected_second[27] = delta / 2
    _equal((THIRD + FIRST) * first_residual, expected_first, "first circle inverse modulo cone")
    _equal((THIRD - FIRST) * second_residual, expected_second, "second circle inverse modulo cone")
    return {
        "slice": "e1+e18+A*e3+B*e8+C*e27",
        "delta": "A**2+B**2-C**2",
        "norm_squared": "2+A**2+B**2+C**2",
        "full_rank_loci": {"delta_nonzero": 32, "punctured_cone": 24, "coefficient_origin": 20},
        "blocks": records,
        "first_chart_inverse": {"domain": "C+A != 0", "u": "(C+A)/2", "v": "B/(C+A)"},
        "second_chart_inverse": {"domain": "C-A != 0", "u": "(C-A)/2", "w": "B/(C-A)"},
        "real_cover_reason": "C+A=C-A=0 implies A=C=0; the real cone equation then forces B=0.",
    }


def _bundle_and_attachment_certificate() -> dict[str, object]:
    fixed, at_zero, at_infinity, fixed_projector = _endpoint_frames()
    center = _operator(_symbolic_coordinates(0, 0, 0))
    _equal(center * fixed, sp.zeros(32, 4), "fixed endpoint kernel")
    _equal(center * at_zero, sp.zeros(32, 4), "zero-circle endpoint kernel")
    _equal(center * at_infinity, sp.zeros(32, 4), "infinity-circle endpoint kernel")
    _equal(at_zero.T * at_zero, 4 * sp.eye(4), "zero-circle Gram")
    _equal(at_infinity.T * at_infinity, 4 * sp.eye(4), "infinity-circle Gram")
    _equal(at_zero.T * at_infinity, sp.zeros(4), "circle endpoint orthogonality")
    _equal(fixed.T * at_zero, sp.zeros(4), "fixed zero-circle orthogonality")
    _equal(fixed.T * at_infinity, sp.zeros(4), "fixed infinity-circle orthogonality")
    _require(fixed.row_join(at_zero).row_join(at_infinity).rank() == 12, "endpoint kernel decomposition")
    _require(center.rank() == 20, "endpoint kernel dimension")
    for chart in ("first", "second"):
        internal = _internal_frame(chart)
        _equal(internal.subs(AMPLITUDE, 0), fixed, "internal amplitude-zero limit")
    first_internal = _internal_frame("first")
    second_internal = _internal_frame("second").subs(
        {AMPLITUDE: AMPLITUDE * SLOPE**2, SLOPE: 1 / SLOPE}, simultaneous=True
    )
    _equal(first_internal, second_internal, "internal reciprocal chart transition")
    projector = _circle_projector(SLOPE, "first")
    second_projector = _circle_projector(SECOND_SLOPE, "second")
    _equal(projector.subs(SLOPE, 1 / SECOND_SLOPE), second_projector, "projector reciprocal chart transition")
    _equal(projector * projector, projector, "circle projector idempotence")
    _equal(projector.T, projector, "circle projector symmetry")
    _equal(projector.trace(), 8, "circle projector rank")
    _equal(center * projector, sp.zeros(32), "circle projector endpoint inclusion")
    cross_gram = 4 * (1 + SLOPE * SECOND_SLOPE) * sp.eye(4)
    first_external, other_external = at_zero + SLOPE * at_infinity, at_zero + SECOND_SLOPE * at_infinity
    _equal(first_external.T * other_external, cross_gram, "circle external cross Gram")
    joined_coefficients = sp.eye(4).row_join(sp.eye(4)).col_join((SLOPE * sp.eye(4)).row_join(SECOND_SLOPE * sp.eye(4)))
    _equal(joined_coefficients.det(), (SECOND_SLOPE - SLOPE) ** 4, "distinct external planes span eight dimensions")
    _equal(
        first_external.row_join(other_external),
        at_zero.row_join(at_infinity) * joined_coefficients,
        "distinct external planes endpoint-coordinate certificate",
    )
    overlap_trace = 4 + 4 * (1 + SLOPE * SECOND_SLOPE) ** 2 / ((1 + SLOPE**2) * (1 + SECOND_SLOPE**2))
    _equal(sp.trace(projector * projector.subs(SLOPE, SECOND_SLOPE)), overlap_trace, "circle projector overlap")
    derivative = projector.diff(SLOPE)
    _equal(sp.trace(derivative * derivative), 8 / (1 + SLOPE**2) ** 2, "circle projector derivative Gram")
    complex_structure = _quaternion_complex_structure()
    _equal(complex_structure.T, -complex_structure, "quaternion complex-structure skew symmetry")
    _equal(complex_structure.T * complex_structure, sp.eye(4), "quaternion complex-structure orthogonality")
    _equal(complex_structure**2, -sp.eye(4), "quaternion complex-structure square")
    external = _global_external_frame(CIRCLE_FIRST, CIRCLE_SECOND)
    _equal(
        external.T * external - sp.eye(4),
        (CIRCLE_FIRST**2 + CIRCLE_SECOND**2 - 1) * sp.eye(4) / 2,
        "global circle external orthonormality modulo circle",
    )
    _equal(fixed.T * external, sp.zeros(4), "global external fixed-kernel orthogonality")
    global_records = []
    for chart in ("first", "second"):
        circle_first = (1 - SLOPE**2) / (1 + SLOPE**2) if chart == "first" else (SLOPE**2 - 1) / (1 + SLOPE**2)
        circle_second = 2 * SLOPE / (1 + SLOPE**2)
        global_frame = external.subs({CIRCLE_FIRST: circle_first, CIRCLE_SECOND: circle_second}).applyfunc(sp.cancel)
        local_frame = at_zero + SLOPE * at_infinity if chart == "first" else SLOPE * at_zero + at_infinity
        transition = (
            (sp.eye(4) + SLOPE * complex_structure) if chart == "first" else (SLOPE * sp.eye(4) + complex_structure)
        )
        _equal(global_frame, local_frame * transition / (2 * (1 + SLOPE**2)), "global external chart transition")
        _equal(local_frame.T * global_frame, 2 * transition, "external chart transition Gram")
        _equal(global_frame.T * global_frame, sp.eye(4), "global external frame Gram")
        _equal(
            _operator(_circle_coordinates(AMPLITUDE, SLOPE, chart)) * global_frame,
            sp.zeros(32, 4),
            "global external action",
        )
        _equal(transition.det(), (1 + SLOPE**2) ** 2, "every real chart transition is invertible")
        global_records.append({"chart": chart, "transition": _sparse_matrix(transition / (2 * (1 + SLOPE**2)))})
    return {
        "fixed_internal_kernel_frame": _sparse_matrix(fixed),
        "fixed_internal_projector": _sparse_matrix(fixed_projector),
        "external_frame_at_zero": _sparse_matrix(at_zero),
        "external_frame_at_infinity": _sparse_matrix(at_infinity),
        "quaternion_complex_structure": _sparse_matrix(complex_structure),
        "global_external_orthonormal_frame": _sparse_matrix(external),
        "global_external_chart_transitions": global_records,
        "internal_transition": "identity, with u_second=u_first*v**2 and w=1/v on v!=0",
        "external_polynomial_transition": "W_first(v)=v*W_second(1/v), v!=0",
        "circle_projector": _sparse_matrix(projector),
        "second_circle_projector": _sparse_matrix(second_projector),
        "distinct_plane_intersection_dimension": 4,
        "external_direct_sum_determinant": "(w-v)**4 for distinct finite slopes",
        "pairwise_projector_trace": str(overlap_trace),
        "projector_derivative_gram": "8/(1+v**2)**2",
        "limiting_plane_dimension": 8,
        "endpoint_kernel_dimension": 12,
        "attachment_equations": "alpha_i*beta_j-alpha_j*beta_i=0 for all 0<=i<j<4",
        "attachment_coordinates": "alpha=W0.T*y/2, beta=Winfinity.T*y/2",
        "bundle_scope": "complete kernel bundle on the punctured cone of the named affine slice",
    }


def _invalid(value: Any) -> Any:
    return value


def _rejection(operation: Callable[[], object], label: str) -> str:
    try:
        operation()
    except ValueError:
        return label
    raise RuntimeError(f"invalid input accepted: {label}")


def _public_contracts() -> dict[str, object]:
    point_records = []
    points = ((0, 0, 0), (1, 0, 0), (1, 0, 1), (-1, 0, 1), (3, 4, 5), (3, 4, -5), (0, 1, 1))
    for point in points:
        classification = classify_slice(point)
        matrix = _operator(sp.Matrix(slice_coordinates(point)))
        _require(matrix.rank() == classification.rank, "rational public rank classification")
        record: dict[str, object] = {
            "coefficients": list(point),
            "rank": classification.rank,
            "nullity": classification.nullity,
            "delta": str(classification.delta),
            "norm_squared": str(classification.norm_squared),
        }
        if classification.rank == 24:
            record["kernel_frame"] = _sparse_matrix(cone_kernel_frame(point))
        point_records.append(record)
    _equal(circle_projector(0, "second"), _circle_projector(0, "second"), "public infinity chart")
    _equal(circle_projector(Fraction(2, 3)), circle_projector(Fraction(3, 2), "second"), "public reciprocal charts")
    _, at_zero, at_infinity, _ = _endpoint_frames()
    unit_inside = at_zero[:, 0] / 2
    unit_outside = 3 * at_zero[:, 0] / 10 + 2 * at_infinity[:, 1] / 5
    _require(unit_inside.dot(unit_inside) == unit_outside.dot(unit_outside) == 1, "unit attachment fixtures")
    inside = tuple(Fraction(value) for value in unit_inside)
    outside = tuple(Fraction(value) for value in unit_outside)
    _require(attachment_image_contains(inside, require_unit=True), "unit attachment membership")
    _require(not attachment_image_contains(outside, require_unit=True), "endpoint unit vector outside attachment image")
    _require(attachment_image_contains((0,) * 32), "homogeneous zero attachment membership")
    _require(not attachment_image_contains((0,) * 32, require_unit=True), "zero vector outside unit attachment sphere")
    outside_endpoint = tuple(int(index == 0) for index in range(32))
    _require(not attachment_image_contains(outside_endpoint), "ambient vector outside endpoint kernel")
    rejections = [
        _rejection(lambda: slice_coordinates((1, 2)), "slice_dimension"),
        _rejection(lambda: classify_slice(_invalid((1.0, 0, 1))), "approximate_coefficients"),
        _rejection(lambda: classify_slice((True, 0, 1)), "boolean_coefficients"),
        _rejection(lambda: classify_slice(_invalid("101")), "string_coefficients"),
        _rejection(lambda: cone_kernel_frame((0, 0, 0)), "origin_cone_frame"),
        _rejection(lambda: cone_kernel_frame((1, 0, 0)), "off_cone_frame"),
        _rejection(lambda: circle_projector(_invalid(0.1)), "approximate_slope"),
        _rejection(lambda: circle_projector(0, "third"), "invalid_circle_chart"),
        _rejection(lambda: attachment_image_contains((0,) * 31), "partner_dimension"),
        _rejection(lambda: attachment_image_contains(_invalid((0.0,) * 32)), "approximate_partner"),
        _rejection(lambda: attachment_image_contains((0,) * 32, _invalid(1)), "unit_flag_type"),
    ]
    return {
        "rational_points": point_records,
        "unit_partner_inside_image": _coordinates_record(unit_inside),
        "unit_endpoint_partner_outside_image": _coordinates_record(unit_outside),
        "invalid_inputs_rejected": sorted(rejections),
    }


def audit_circle_kernel_attachments() -> dict[str, object]:
    """Replay unrestricted slice ranks, kernel charts and endpoint attachments."""
    return {
        "schema": "dimension32-circle-kernel-attachments-v1",
        "real_rank_certificate": _slice_rank_certificate(),
        "circle_charts": [_chart_certificate(chart) for chart in ("first", "second")],
        "kernel_bundle_and_attachments": _bundle_and_attachment_certificate(),
        "public_api_contracts": _public_contracts(),
        "scope": (
            "complete arbitrary-real affine-slice ranks, punctured-cone kernel bundle and endpoint attachment image"
        ),
        "remaining_obligations": [
            "Establish ambient rank-stratum coverage and neighborhood attachments beyond the named slice.",
            "Calculate the unrestricted pair space's global invariants and homotopy type.",
            "Prove an unrestricted all-dimensional classification.",
            "Translate retained exact identities into Rocq after the authorized run-result milestone.",
        ],
    }


def main() -> int:
    print(json.dumps(audit_circle_kernel_attachments(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
