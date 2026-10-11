"""Exact polynomial rank changes along a nonzero dimension-32 zero-divisor path.

Eight four-by-four polynomial blocks certify all real parameter values. Their
minor identities identify the exceptional parameters 0, 1, 2. A constant
four-dimensional kernel extends to the larger endpoint kernels. The restricted
incidence-space topology is derived separately in rank_path_topology.py.
"""

from __future__ import annotations

import json
from dataclasses import replace
from fractions import Fraction
from itertools import permutations

import sympy as sp

import parallel
from cd_core import cd_sign
from rank_charts import rank_certificate, verify_rank_certificate

DIMENSION = 32
COSET_SUBGROUP = (0, 11, 19, 24)
ENDPOINTS = (0, 1, 2)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _parameter(value: object) -> sp.Expr:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction, sp.Expr)):
        raise ValueError("path parameter must be an exact real rational or a real SymPy expression")
    expression = sp.sympify(value)
    if expression.is_real is not True or expression.has(sp.Float):
        raise ValueError("path parameter must be exact and real")
    return expression


def path_coefficients(parameter: object) -> tuple[sp.Expr, ...]:
    """Return the exact polynomial path, whose e1 coefficient is always one."""
    value = _parameter(parameter)
    sparse = {1: sp.Integer(1), 10: (value - 1) ** 2, 18: value * (3 - value) / 2, 25: -value * (value - 1) / 2}
    return tuple(sparse.get(index, sp.Integer(0)) for index in range(DIMENSION))


def path_matrix(parameter: object) -> sp.Matrix:
    """Return the exact left multiplication matrix along the dimension-32 path."""
    coordinates = path_coefficients(parameter)
    return sp.Matrix(
        DIMENSION,
        DIMENSION,
        lambda row, column: coordinates[row ^ column] * cd_sign(DIMENSION, row ^ column, column),
    )


def common_kernel_basis() -> sp.Matrix:
    """Return four constant integer kernel columns; division by two is orthonormal."""
    supports = (
        {4: -1, 15: 1, 23: 1, 28: 1},
        {5: -1, 14: -1, 22: -1, 29: 1},
        {6: -1, 13: 1, 21: 1, 30: 1},
        {7: -1, 12: -1, 20: -1, 31: 1},
    )
    return sp.Matrix(DIMENSION, len(supports), lambda row, column: supports[column].get(row, 0))


def _endpoint_coordinates(endpoint: int) -> tuple[Fraction, ...]:
    if isinstance(endpoint, bool) or not isinstance(endpoint, int) or endpoint not in ENDPOINTS:
        raise ValueError("endpoint must be the integer 0, 1, or 2")
    return tuple(Fraction(int(value.p), int(value.q)) for value in path_coefficients(endpoint))


def endpoint_kernel_basis(endpoint: int) -> sp.Matrix:
    """Return an independently certified complete rational endpoint kernel."""
    return sp.Matrix(rank_certificate(_endpoint_coordinates(endpoint)).kernel_basis)


def _polynomial_determinant(matrix: sp.Matrix, parameter: sp.Symbol) -> sp.Expr:
    """Expand only a block minor of size at most four by its permutation formula."""
    if matrix.rows != matrix.cols or matrix.rows > 4:
        raise ValueError("polynomial block determinant requires a square matrix of size at most four")
    determinant = sp.Integer(0)
    for permutation in permutations(range(matrix.rows)):
        inversion_count = sum(
            permutation[first] > permutation[second]
            for first in range(matrix.rows)
            for second in range(first + 1, matrix.rows)
        )
        term = sp.Integer(-1 if inversion_count % 2 else 1)
        for row, column in enumerate(permutation):
            term *= matrix[row, column]
        determinant += term
    return sp.Poly(determinant, parameter).as_expr()


def _zero_polynomial(expression: sp.Expr, parameter: sp.Symbol) -> bool:
    return bool(sp.Poly(expression, parameter).is_zero)


def _block_certificate(representative: int) -> dict[str, object]:
    parameter = sp.Symbol("t", real=True)
    matrix = path_matrix(parameter)
    columns = tuple(representative ^ offset for offset in COSET_SUBGROUP)
    rows = tuple(1 ^ column for column in columns)
    outside_columns = tuple(column for column in range(DIMENSION) if column not in columns)
    _require(matrix.extract(rows, outside_columns) == sp.zeros(4, 28), "coset block has an off-block entry")
    block = matrix.extract(rows, columns)
    full_determinant = _polynomial_determinant(block, parameter)
    norm_squared = sum((value**2 for value in path_coefficients(parameter)), sp.Integer(0))
    positive_quadratic = parameter**2 - parameter + 2
    minor_rows: tuple[int, ...]
    minor_columns: tuple[int, ...]
    if representative < 4:
        generic_rank = 4
        factor_sign = -1 if representative in (0, 1) else 1
        expected = factor_sign * (parameter - 2) * (parameter - 1) * positive_quadratic * norm_squared / 2
        minor_rows = minor_columns = (0, 1, 2, 3)
        chosen_minor = full_determinant
    else:
        generic_rank = 3
        factor_sign = -1 if representative in (4, 7) else 1
        expected = factor_sign * parameter * (parameter - 2) ** 2 * (parameter - 1) * positive_quadratic / 2
        minor_rows = minor_columns = (0, 1, 2)
        chosen_minor = _polynomial_determinant(block.extract(minor_rows, minor_columns), parameter)
        _require(_zero_polynomial(full_determinant, parameter), "rank-three block determinant fails identically")
    _require(_zero_polynomial(chosen_minor - expected, parameter), "exact polynomial minor factorization failed")
    endpoint_records = []
    for endpoint in ENDPOINTS:
        endpoint_block = block.subs(parameter, endpoint)
        _, pivot_columns = endpoint_block.rref()
        _, pivot_rows = endpoint_block[:, list(pivot_columns)].T.rref()
        pivot_determinant = endpoint_block.extract(pivot_rows, pivot_columns).det()
        kernel_columns = endpoint_block.nullspace()
        kernel = sp.Matrix.hstack(*kernel_columns) if kernel_columns else sp.zeros(4, 0)
        rank = len(pivot_columns)
        _require(pivot_determinant != 0, "endpoint block lower-rank certificate failed")
        _require(
            kernel.rank() == 4 - rank and endpoint_block * kernel == sp.zeros(4, 4 - rank), "endpoint block upper bound"
        )
        endpoint_records.append(
            {
                "parameter": endpoint,
                "rank": rank,
                "pivot_rows": list(pivot_rows),
                "pivot_columns": list(pivot_columns),
                "pivot_determinant": str(pivot_determinant),
            }
        )
    return {
        "coset_representative": representative,
        "input_columns": list(columns),
        "output_rows": list(rows),
        "generic_rank": generic_rank,
        "minor_rows_in_block": list(minor_rows),
        "minor_columns_in_block": list(minor_columns),
        "minor_expanded": str(chosen_minor),
        "minor_factored": str(expected),
        "full_determinant_zero_identity": representative >= 4,
        "endpoints": endpoint_records,
    }


def audit_rank_attachments() -> dict[str, object]:
    """Verify the complete real-parameter rank stratification and kernel limits."""
    parameter = sp.Symbol("t", real=True)
    coordinates = path_coefficients(parameter)
    matrix = path_matrix(parameter)
    common = common_kernel_basis()
    _require(common.T * common == 4 * sp.eye(4), "constant kernel Gram certificate changed")
    _require((matrix * common).applyfunc(sp.expand) == sp.zeros(32, 4), "constant kernel polynomial identity failed")
    norm_squared = sum((value**2 for value in coordinates), sp.Integer(0))
    _require(coordinates[1] == 1, "path nonvanishing certificate changed")
    _require(
        sp.expand(coordinates[18] - coordinates[25] - parameter) == 0, "normalized-path injectivity identity changed"
    )
    quadratic = parameter**2 - parameter + 2
    # The recorded sum-of-squares identities prove positivity on every real
    # parameter; evaluating a finite collection of roots would be insufficient.
    _require(
        _zero_polynomial(quadratic - ((parameter - sp.Rational(1, 2)) ** 2 + sp.Rational(7, 4)), parameter),
        "positive quadratic",
    )
    blocks = parallel.ordered_map(_block_certificate, list(range(8)), min_items=2)
    covered_columns = [
        column for representative in range(8) for column in (representative ^ offset for offset in COSET_SUBGROUP)
    ]
    _require(sorted(covered_columns) == list(range(32)), "coset decomposition fails to partition all columns")
    generic_rank = sum(int(record["generic_rank"]) for record in blocks)
    _require(generic_rank + common.cols == 32, "generic rank lower and upper bounds disagree")
    endpoint_records = []
    stacked = sp.Matrix.vstack(*(path_matrix(endpoint) for endpoint in ENDPOINTS))
    _require(stacked.rank() == 28, "common endpoint intersection has a different dimension")
    for endpoint in ENDPOINTS:
        values = _endpoint_coordinates(endpoint)
        certificate = rank_certificate(values)
        kernel = sp.Matrix(certificate.kernel_basis)
        endpoint_matrix = path_matrix(endpoint)
        _require(endpoint_matrix == sp.Matrix(certificate.matrix), "endpoint matrix disagrees with rational CD action")
        _require(endpoint_matrix * common == sp.zeros(32, 4), "endpoint rejects common limiting kernel")
        _require(kernel.row_join(common).rank() == kernel.cols, "limiting kernel inclusion failed")
        damaged = replace(certificate, kernel_basis=tuple(row[:-1] for row in certificate.kernel_basis))
        _require(not verify_rank_certificate(values, damaged), "incomplete endpoint kernel accepted")
        endpoint_records.append(
            {
                "parameter": endpoint,
                "rank": certificate.rank,
                "nullity": certificate.nullity,
                "pivot_rows": list(certificate.pivot_rows),
                "pivot_columns": list(certificate.pivot_columns),
                "pivot_determinant": str(certificate.pivot_determinant),
                "kernel_basis": [[str(value) for value in row] for row in certificate.kernel_basis],
                "limiting_common_kernel_dimension": common.cols,
            }
        )
    wrong_path = matrix.copy()
    wrong_path[5, 4] *= -1
    _require(
        (wrong_path * common).applyfunc(sp.expand) != sp.zeros(32, 4),
        "path sign mutation escaped common-kernel identity",
    )
    for invalid in (0.5, True, sp.I, sp.Symbol("z")):
        try:
            path_matrix(invalid)
        except ValueError:
            pass
        else:
            raise RuntimeError("inexact or nonreal path parameter admitted")
    return {
        "schema": "cayley-dickson-polynomial-rank-attachments-v1",
        "qpu_executed": False,
        "arithmetic": "SymPy polynomial identities over Q[t] and exact rational rank certificates",
        "sympy_version": sp.__version__,
        "dimension": DIMENSION,
        "path": "e1+(t-1)^2 e10+t(3-t)/2 e18-t(t-1)/2 e25",
        "parameter_domain": "all real t",
        "nonvanishing": "a1(t)=1, hence N(t)=sum_i a_i(t)^2 >= 1",
        "norm_squared_polynomial": str(sp.expand(norm_squared)),
        "positive_quadratic_identity": "t^2-t+2=(t-1/2)^2+7/4 > 0",
        "generic_parameter_domain": "R excluding {0,1,2}",
        "generic_rank": generic_rank,
        "generic_nullity": common.cols,
        "polynomial_blocks": blocks,
        "constant_kernel_basis": [[str(value) for value in row] for row in common.tolist()],
        "constant_kernel_gram": "4I; division by 2 gives a constant orthonormal frame",
        "endpoints": endpoint_records,
        "normalized_path_inverse": "t=(x18-x25)/x1 for x=a(t)/sqrt(N(t)); x1>0",
        "limiting_frames": "The same constant orthonormal frame extends from each open interval to both endpoints.",
        "scope": (
            "This certificate classifies the selected polynomial path; "
            "it does not classify the full dimension-32 zero-divisor locus."
        ),
    }


def main() -> int:
    print(json.dumps(audit_rank_attachments(), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
