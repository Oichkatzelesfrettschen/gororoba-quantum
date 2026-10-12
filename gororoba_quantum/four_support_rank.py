"""Exact real rank loci on the dimension-32 support {1, 10, 18, 25}.

Polynomial identities certify every real coefficient point on this support.
The executable evaluator accepts integers and Fractions, and constructs complete
kernel frames without numerical rank thresholds. The all-real certificate uses
positive sums of squares; rational examples alone would establish less.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, replace
from fractions import Fraction
from itertools import combinations
from typing import Any

import sympy as sp

import parallel
from cd_core import cd_sign
from rank_charts import (
    ConstantRankChart,
    RationalMatrix,
    chart_transition,
    multiplication_matrix,
    rank_certificate,
    verify_rank_certificate,
)

DIMENSION = 32
SUPPORT = (1, 10, 18, 25)
SUBGROUP = tuple(sorted(index ^ SUPPORT[0] for index in SUPPORT))
COEFFICIENTS = sp.symbols("a b c d", real=True)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _equal(actual: Any, expected: Any, label: str) -> None:
    difference = actual - expected
    if isinstance(difference, sp.MatrixBase):
        valid = difference.applyfunc(sp.expand) == sp.zeros(*difference.shape)
    else:
        valid = sp.expand(difference) == 0
    _require(bool(valid), label)


def _rational_coefficients(coefficients: Sequence[int | Fraction]) -> tuple[Fraction, ...]:
    if (
        not isinstance(coefficients, Sequence)
        or isinstance(coefficients, (str, bytes))
        or len(coefficients) != len(SUPPORT)
    ):
        raise ValueError("the fixed support requires exactly four coefficients")
    if any(isinstance(value, bool) or not isinstance(value, (int, Fraction)) for value in coefficients):
        raise ValueError("coefficients must be exact integers or Fractions")
    return tuple(Fraction(value) for value in coefficients)


def _fraction_matrix(matrix: sp.Matrix) -> RationalMatrix:
    return tuple(tuple(Fraction(value) for value in row) for row in matrix.tolist())


def support_coordinates(coefficients: Sequence[int | Fraction]) -> tuple[Fraction, ...]:
    """Embed four exact coefficients into the fixed dimension-32 basis support."""
    values = dict(zip(SUPPORT, _rational_coefficients(coefficients), strict=True))
    return tuple(values.get(index, Fraction(0)) for index in range(DIMENSION))


def symbolic_matrix() -> sp.Matrix:
    """Derive the complete polynomial left action from the CD sign recursion."""
    sparse = dict(zip(SUPPORT, COEFFICIENTS, strict=True))
    return sp.Matrix(
        DIMENSION,
        DIMENSION,
        lambda row, column: sparse.get(row ^ column, 0) * cd_sign(DIMENSION, row ^ column, column),
    )


def sector_indices(representative: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return output rows and input columns of one four-dimensional XOR sector."""
    if isinstance(representative, bool) or not isinstance(representative, int) or representative not in range(8):
        raise ValueError("sector representative must be an integer in [0,7]")
    columns = tuple(representative ^ offset for offset in SUBGROUP)
    return tuple(SUPPORT[0] ^ column for column in columns), columns


def _linear_forms(values: Sequence[Any]) -> tuple[Any, ...]:
    a, b, c, d = values
    return a - b - c - d, a - b + c + d, a + b - c + d, a + b + c - d


def _norm_and_quadric(values: Sequence[Any]) -> tuple[Any, Any]:
    a, b, c, d = values
    return a * a + b * b + c * c + d * d, a * a + b * b - c * c - d * d


def _linear_frames(representative: int) -> tuple[sp.Matrix, sp.Matrix]:
    transform = sp.Matrix(_linear_forms(COEFFICIENTS)).jacobian(COEFFICIENTS)
    frame = transform.T
    signs = sp.diag(1, -1, -1, 1)
    right = frame if representative in (4, 6) else signs * frame
    left = {4: signs * frame, 5: -frame, 6: -signs * frame, 7: frame}[representative]
    return left, right


def _cone_vectors(values: Sequence[Any]) -> tuple[tuple[sp.Matrix, sp.Matrix], ...]:
    a, b, c, d = values
    norm, _ = _norm_and_quadric(values)
    mixed_difference, mixed_sum = a * d - b * c, a * c + b * d
    return (
        (sp.Matrix([0, norm, 2 * mixed_difference, 2 * mixed_sum]), sp.Matrix([-b, a, d, -c])),
        (sp.Matrix([b, -a, -d, c]), sp.Matrix([0, 1, 0, 0])),
        (sp.Matrix([d, -c, b, -a]), sp.Matrix([0, 0, 0, -1])),
        (sp.Matrix([-2 * mixed_difference, -2 * mixed_sum, 0, norm]), sp.Matrix([d, -c, b, -a])),
    )


@dataclass(frozen=True)
class FourSupportEvaluation:
    coefficients: tuple[Fraction, ...]
    linear_forms: tuple[Fraction, ...]
    norm_squared: Fraction
    quadric: Fraction
    kernel_frame: RationalMatrix

    @property
    def nullity(self) -> int:
        return len(self.kernel_frame[0])

    @property
    def rank(self) -> int:
        return DIMENSION - self.nullity


def evaluate_four_support(coefficients: Sequence[int | Fraction]) -> FourSupportEvaluation:
    """Classify an exact rational point and lift a full orthogonal kernel frame.

    The nonzero formula follows from the polynomial sector certificate. At the
    origin the identity frame supplies the entire 32-dimensional kernel.
    """
    values = _rational_coefficients(coefficients)
    norm, quadric = _norm_and_quadric(values)
    forms = _linear_forms(values)
    lifted_columns: list[sp.Matrix] = []
    if norm == 0:
        frame = sp.eye(DIMENSION)
    else:
        cone_vectors = _cone_vectors(values)
        for representative in range(8):
            _, columns = sector_indices(representative)
            local_columns = []
            if representative < 4 and quadric == 0:
                local_columns.append(cone_vectors[representative][0])
            elif representative >= 4:
                _, right = _linear_frames(representative)
                local_columns.extend(right[:, index] for index, value in enumerate(forms) if value == 0)
            for local in local_columns:
                lifted = sp.zeros(DIMENSION, 1)
                for index, column in enumerate(columns):
                    lifted[column, 0] = local[index]
                lifted_columns.append(lifted)
        frame = sp.Matrix.hstack(*lifted_columns) if lifted_columns else sp.zeros(DIMENSION, 0)
        expected_nullity = 4 * (sum(value == 0 for value in forms) + int(quadric == 0))
        _require(frame.cols == expected_nullity, "kernel frame dimension disagrees with the certified formula")
    matrix = sp.Matrix(multiplication_matrix(support_coordinates(values)))
    _require(matrix * frame == sp.zeros(DIMENSION, frame.cols), "lifted frame fails the kernel identity")
    gram = frame.T * frame
    _require(
        gram == sp.diag(*(gram[index, index] for index in range(frame.cols)))
        and all(gram[index, index] > 0 for index in range(frame.cols)),
        "kernel independence",
    )
    return FourSupportEvaluation(values, forms, norm, quadric, _fraction_matrix(frame))


def _sector_certificate(representative: int, supplied_block: sp.Matrix | None = None) -> dict[str, Any]:
    matrix = symbolic_matrix()
    rows, columns = sector_indices(representative)
    outside = tuple(column for column in range(DIMENSION) if column not in columns)
    _equal(matrix.extract(rows, outside), sp.zeros(4, 28), "off-sector entries must vanish identically")
    block = matrix.extract(rows, columns) if supplied_block is None else supplied_block
    norm, quadric = _norm_and_quadric(COEFFICIENTS)
    forms = _linear_forms(COEFFICIENTS)
    record: dict[str, Any] = {"representative": representative, "input_columns": columns, "output_rows": rows}
    if representative < 4:
        sign = -1 if representative in (0, 1) else 1
        _equal(block.det(), sign * norm * quadric, "quadratic sector determinant identity")
        squared_minors = sum(
            block.extract(minor_rows, minor_columns).det() ** 2
            for minor_rows in combinations(range(4), 3)
            for minor_columns in combinations(range(4), 3)
        )
        _equal(squared_minors, 2 * norm * (norm**2 + quadric**2), "positive rank-three minor certificate")
        vector, residual = _cone_vectors(COEFFICIENTS)[representative]
        _equal(block * vector, quadric * residual, "polynomial cone kernel identity")
        a, b, c, d = COEFFICIENTS
        vector_norm = norm if representative in (1, 2) else norm**2 + 4 * (a * a + b * b) * (c * c + d * d)
        _equal((vector.T * vector)[0], vector_norm, "strictly positive cone-frame norm")
        spectral_variable = sp.Symbol("z")
        _equal(
            (block.T * block).charpoly(spectral_variable).as_expr(),
            (spectral_variable - norm) ** 2 * (spectral_variable**2 - 2 * norm * spectral_variable + quadric**2),
            "quadratic sector Gram characteristic polynomial",
        )
        record.update(
            determinant=str(sp.factor(sign * norm * quadric)),
            sum_squared_three_minors="2*N*(N**2+Delta**2)",
            rank_nonzero="3 if Delta=0, otherwise 4",
            cone_kernel_vector=[str(value) for value in vector],
            kernel_residual_divided_by_delta=[str(value) for value in residual],
            cone_vector_norm_squared=str(vector_norm),
        )
    else:
        left, right = _linear_frames(representative)
        _equal(left.T * left, 4 * sp.eye(4), "invertible left constant frame")
        _equal(right.T * right, 4 * sp.eye(4), "invertible right constant frame")
        _equal(block * right, left * sp.diag(*forms), "linear sector two-sided diagonalization")
        _equal(block.det(), sp.prod(forms), "linear sector determinant")
        _equal(block.T * block * right, right * sp.diag(*(form**2 for form in forms)), "linear sector Gram spectrum")
        record.update(
            left_frame=left.tolist(),
            right_frame=right.tolist(),
            rank="number of nonzero linear forms",
        )
        record["left_frame"] = [[int(value) for value in row] for row in record["left_frame"]]
        record["right_frame"] = [[int(value) for value in row] for row in record["right_frame"]]
    return record


def _check_sector_cover(records: Sequence[dict[str, Any]]) -> None:
    _require(
        sorted(row for record in records for row in record["output_rows"]) == list(range(DIMENSION)),
        "sector output rows fail to partition the full matrix",
    )
    _require(
        sorted(column for record in records for column in record["input_columns"]) == list(range(DIMENSION)),
        "sector input columns fail to partition the full matrix",
    )


def _audit_rational_point(linear_coordinates: tuple[Fraction, ...]) -> dict[str, Any]:
    transform = sp.Matrix(_linear_forms(COEFFICIENTS)).jacobian(COEFFICIENTS)
    values = tuple(Fraction(value) for value in transform.T * sp.Matrix(linear_coordinates) / 4)
    evaluated = evaluate_four_support(values)
    certificate = rank_certificate(support_coordinates(values))
    _require(certificate.nullity == evaluated.nullity, "independent rational rank certificate disagrees")
    _require(
        verify_rank_certificate(certificate.coordinates, replace(certificate, kernel_basis=evaluated.kernel_frame)),
        "lifted frame fails the independent rank-certificate verifier",
    )
    if evaluated.nullity:
        damaged = replace(certificate, kernel_basis=tuple(row[:-1] for row in evaluated.kernel_frame))
        _require(not verify_rank_certificate(certificate.coordinates, damaged), "missing kernel column is accepted")
    return {
        "coefficients": [str(value) for value in values],
        "linear_coordinates": [str(value) for value in linear_coordinates],
        "quadric": str(evaluated.quadric),
        "rank": evaluated.rank,
        "nullity": evaluated.nullity,
        "kernel_gram_diagonal": [
            str(sum(row[index] ** 2 for row in evaluated.kernel_frame)) for index in range(evaluated.nullity)
        ],
    }


def _audit_overlap() -> dict[str, Any]:
    values = support_coordinates((1, 1, 1, 1))
    first = ConstantRankChart.from_certificate(rank_certificate(values)).certify(values)
    second = ConstantRankChart.from_certificate(
        rank_certificate(values, column_order=tuple(reversed(range(32))))
    ).certify(values)
    transition = chart_transition(first, second)
    lifted = sp.Matrix(evaluate_four_support((1, 1, 1, 1)).kernel_frame)
    first_frame = sp.Matrix(first.kernel_frame)
    to_chart = lifted.extract(first.free_columns, range(lifted.cols))
    _require(to_chart.det() != 0 and first_frame * to_chart == lifted, "support frame to pivot-chart transition")
    return {
        "coefficients": ["1", "1", "1", "1"],
        "nullity": lifted.cols,
        "pivot_chart_transition": [[str(value) for value in row] for row in transition],
        "support_frame_to_first_chart": [[str(value) for value in row] for row in to_chart.tolist()],
        "scope": "rational overlap verification; the symbolic pivot-chart contract defines all real overlaps",
    }


def _audit_spectral_coefficients() -> dict[str, Any]:
    from rank_polynomials import evaluate_rank_polynomials

    norm, quadric = _norm_and_quadric(COEFFICIENTS)
    forms = _linear_forms(COEFFICIENTS)
    variable = sp.Symbol("z")
    elementary = [sp.Integer(1)] + [
        sum(sp.prod(forms[index] ** 2 for index in indices) for indices in combinations(range(4), degree))
        for degree in range(1, 5)
    ]
    coefficients = [
        sum(
            multiplier * elementary[degree - offset]
            for offset, multiplier in enumerate((1, 3 * norm, 2 * norm**2 + quadric**2, norm * quadric**2))
            if 0 <= degree - offset <= 4
        )
        for degree in range(8)
    ]
    reduced_polynomial = (
        (variable - norm)
        * (variable**2 - 2 * norm * variable + quadric**2)
        * sp.prod(variable - form**2 for form in forms)
    )
    _equal(
        reduced_polynomial,
        sum((-1) ** degree * value * variable ** (7 - degree) for degree, value in enumerate(coefficients)),
        "restricted spectral coefficient expansion",
    )
    _equal(coefficients[7], norm * quadric**2 * sp.prod(forms) ** 2, "restricted degree-fourteen factor")
    point = (1, 2, 3, 5)
    general = evaluate_rank_polynomials(support_coordinates(point))
    substitution = dict(zip(COEFFICIENTS, point, strict=True))
    restricted = tuple(Fraction(value.subs(substitution)) for value in coefficients)
    _require(restricted == general.elementary, "restricted coefficients disagree with the general Newton evaluator")
    return {
        "reduced_polynomial": "(z-N)*(z**2-2*N*z+Delta**2)*product_i(z-ell_i**2)",
        "coefficient_formula": "E_j=e_j+3*N*e_(j-1)+(2*N**2+Delta**2)*e_(j-2)+N*Delta**2*e_(j-3)",
        "elementary_definition": "e_j is elementary in ell_i**2; e_0=1, e_j=0 outside 0..4",
        "degree_fourteen_factor": "E_7=N*Delta**2*product_i(ell_i)**2",
        "general_evaluator_point": point,
        "general_evaluator_coefficients": [str(value) for value in restricted],
    }


def _audit_path() -> dict[str, Any]:
    from rank_attachments import path_coefficients

    parameter = sp.Symbol("t", real=True)
    coordinates = path_coefficients(parameter)
    substitution = dict(zip(COEFFICIENTS, (coordinates[index] for index in SUPPORT), strict=True))
    forms = [sp.factor(form.subs(substitution)) for form in _linear_forms(COEFFICIENTS)]
    expected = [0, 2 * parameter * (2 - parameter), (parameter - 1) * (parameter - 2), parameter**2 - parameter + 2]
    _equal(sp.Matrix(forms), sp.Matrix(expected), "existing polynomial path linear forms")
    _, quadric = _norm_and_quadric(COEFFICIENTS)
    specialized = sp.factor(quadric.subs(substitution))
    _equal(specialized, (parameter - 2) * (parameter - 1) * (parameter**2 - parameter + 2) / 2, "path quadric")
    endpoint_nullities = []
    for endpoint in (0, 1, 2):
        values = tuple(Fraction(coordinates[index].subs(parameter, endpoint)) for index in SUPPORT)
        endpoint_nullities.append(evaluate_four_support(values).nullity)
    _require(endpoint_nullities == [8, 12, 16], "existing path endpoint kernel dimensions")
    return {
        "linear_forms": [str(value) for value in forms],
        "quadric": str(specialized),
        "endpoint_nullities": endpoint_nullities,
    }


def _audit_invalid_inputs() -> int:
    rejected = 0
    for coefficients in (
        (1, 2, 3),
        (1, 2, 3, 4, 5),
        (True, 0, 0, 0),
        (0.1, 0, 0, 0),
        (sp.I, 0, 0, 0),
        (sp.Symbol("a", real=True), 0, 0, 0),
        "1234",
    ):
        try:
            evaluate_four_support(coefficients)  # type: ignore[arg-type]
        except ValueError:
            rejected += 1
        else:
            raise RuntimeError("invalid exact evaluator input accepted")
    for representative in (True, -1, 8, 0.5):
        try:
            sector_indices(representative)  # type: ignore[arg-type]
        except ValueError:
            rejected += 1
        else:
            raise RuntimeError("invalid sector representative accepted")
    return rejected


def audit_four_support_rank() -> dict[str, Any]:
    """Replay polynomial identities, exact rank examples, frames, and falsifiers."""
    norm, quadric = _norm_and_quadric(COEFFICIENTS)
    forms = _linear_forms(COEFFICIENTS)
    transform = sp.Matrix(forms).jacobian(COEFFICIENTS)
    _equal(transform * transform.T, 4 * sp.eye(4), "linear coefficient transform is invertible")
    _equal(2 * quadric, forms[0] * forms[1] + forms[2] * forms[3], "cone in linear coordinates")
    _require({first ^ second for first in SUBGROUP for second in SUBGROUP} == set(SUBGROUP), "XOR subgroup closure")
    sectors = parallel.ordered_map(_sector_certificate, list(range(8)), min_items=2)
    _check_sector_cover(sectors)
    damaged_sectors = [dict(record) for record in sectors]
    damaged_sectors[-1]["input_columns"] = sectors[0]["input_columns"]
    try:
        _check_sector_cover(damaged_sectors)
    except RuntimeError:
        pass
    else:
        raise RuntimeError("duplicate sector passes the partition check")
    rows, columns = sector_indices(4)
    damaged_block = symbolic_matrix().extract(rows, columns)
    damaged_block[0, 1] *= -1
    try:
        _sector_certificate(4, damaged_block)
    except RuntimeError:
        pass
    else:
        raise RuntimeError("sign mutation passes the polynomial sector check")
    examples = (
        (1, 1, 1, 1),
        (1, 1, 1, -1),
        (0, 1, 1, 1),
        (0, 0, 1, 1),
        (0, 1, 0, 1),
        (0, 0, 0, 1),
        (0, 0, 0, 0),
        (Fraction(1, 10**40), 1, 1, 1),
    )
    points = parallel.ordered_map(
        _audit_rational_point, [tuple(Fraction(value) for value in example) for example in examples], min_items=2
    )
    return {
        "schema": "cayley-dickson-four-support-real-rank-v1",
        "arithmetic": "polynomial identities over Q[a,b,c,d] and exact rational point evaluations",
        "sympy_version": sp.__version__,
        "dimension": DIMENSION,
        "support": SUPPORT,
        "qpu_executed": False,
        "norm_squared": str(norm),
        "quadric": str(quadric),
        "linear_forms": [str(form) for form in forms],
        "linear_coordinate_transform": [[int(value) for value in row] for row in transform.tolist()],
        "quadric_in_linear_coordinates": "2*Delta=ell1*ell2+ell3*ell4",
        "sector_subgroup": SUBGROUP,
        "sectors": sectors,
        "nonzero_nullity": "4*(number of vanishing linear forms + indicator(Delta=0))",
        "origin_nullity": DIMENSION,
        "real_sufficiency": "N>0 off the origin; 2*N*(N**2+Delta**2)>0 proves quadratic-sector rank at least3",
        "kernel_trivialization_scope": (
            "Each fixed vanishing pattern of Delta and all four linear forms away from the origin has "
            "the retained polynomial orthogonal frame; "
            "smoothness and attachments require separate analysis."
        ),
        "rational_points": points,
        "pivot_overlap": _audit_overlap(),
        "spectral_coefficients": _audit_spectral_coefficients(),
        "path_specialization": _audit_path(),
        "negative_controls": [
            "duplicate input sector rejected",
            "CD sign mutation rejected",
            "missing kernel columns rejected",
            "origin evaluated separately",
            "positive rational 1/10^40 retains nonzero rank contribution",
        ],
        "invalid_inputs_rejected": _audit_invalid_inputs(),
        "scope": (
            "Every real coefficient point on support {1,10,18,25}; global dimension-32 loci, attachments, "
            "topology and other supports remain outside this certificate."
        ),
    }


def main() -> int:
    print(json.dumps(audit_four_support_rank(), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
