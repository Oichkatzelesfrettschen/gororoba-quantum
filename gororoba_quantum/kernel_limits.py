"""Exact limiting kernels and attachment coordinates along polynomial operators.

The generic kernel projector has a removable limit at every real endpoint.
Rank witnesses and rational identities certify the subspace that persists into
the endpoint kernel. The proof and incidence interpretation live in
docs/notes/annihilator_kernel_limits.md.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from cd_core import cd_sign


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _parameter(parameter: sp.Symbol) -> None:
    if not isinstance(parameter, sp.Symbol) or parameter.is_real is not True:
        raise ValueError("the polynomial parameter must be a real SymPy symbol")


def _endpoint(value: int | Fraction) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise ValueError("the endpoint must be an integer or Fraction")
    return Fraction(value)


def _polynomial(value: object, parameter: sp.Symbol) -> sp.Expr:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction, sp.Expr)):
        raise ValueError("operator entries must be exact rational polynomials")
    expression = sp.sympify(value)
    if expression.has(sp.Float) or expression.free_symbols - {parameter}:
        raise ValueError("operator entries must lie in Q[parameter]")
    try:
        return sp.Poly(expression, parameter, domain=sp.QQ).as_expr()
    except (sp.PolynomialError, sp.polys.polyerrors.CoercionFailed) as error:
        raise ValueError("operator entries must lie in Q[parameter]") from error


def _operator(matrix: sp.MatrixBase, parameter: sp.Symbol) -> sp.Matrix:
    _parameter(parameter)
    if not isinstance(matrix, sp.MatrixBase) or matrix.rows < 1 or matrix.cols < 1:
        raise ValueError("the operator must be a nonempty exact polynomial matrix")
    return sp.Matrix(matrix.rows, matrix.cols, lambda row, column: _polynomial(matrix[row, column], parameter))


def _cancel(matrix: sp.MatrixBase) -> sp.Matrix:
    return sp.Matrix(matrix).applyfunc(sp.cancel)


def _equal(first: sp.MatrixBase, second: sp.MatrixBase) -> bool:
    return first.shape == second.shape and _cancel(first - second) == sp.zeros(*first.shape)


def _rref(matrix: sp.Matrix) -> tuple[sp.Matrix, tuple[int, ...]]:
    if matrix.rows == 0 or matrix.cols == 0:
        return matrix.copy(), ()
    reduced, pivots = DomainMatrix.from_Matrix(matrix).to_field().rref()
    return reduced.to_Matrix(), tuple(int(index) for index in pivots)


def _kernel(matrix: sp.Matrix) -> tuple[sp.Matrix, tuple[int, ...], tuple[int, ...]]:
    reduced, pivots = _rref(matrix)
    free = tuple(index for index in range(matrix.cols) if index not in pivots)
    frame = sp.zeros(matrix.cols, len(free))
    for column, index in enumerate(free):
        frame[index, column] = 1
        for row, pivot in enumerate(pivots):
            frame[pivot, column] = -reduced[row, index]
    return frame, pivots, free


def _minor(matrix: sp.Matrix, columns: tuple[int, ...]) -> tuple[tuple[int, ...], sp.Expr]:
    rows = _rref(matrix[:, list(columns)].T)[1] if columns else ()
    return rows, sp.cancel(matrix.extract(rows, columns).det(method="domain-ge"))


def _exceptional(
    matrix: sp.Matrix,
    frame: sp.Matrix,
    projector: sp.Matrix,
    minor: sp.Expr,
    transport_determinant: sp.Expr,
    parameter: sp.Symbol,
) -> sp.Expr:
    polynomials = {
        sp.fraction(sp.cancel(minor))[0],
        sp.fraction(sp.cancel(transport_determinant))[0],
    }
    for value in (*matrix, *frame, *projector):
        polynomials.add(sp.fraction(sp.cancel(value))[1])
    product = sp.Integer(1)
    for polynomial in sorted(polynomials, key=str):
        product = sp.lcm(product, polynomial)
    return sp.Poly(product, parameter, domain=sp.QQ).sqf_part().monic().as_expr()


def _radius(exceptional: sp.Expr, parameter: sp.Symbol, endpoint: Fraction) -> Fraction:
    shifted = sp.Poly(exceptional.subs(parameter, parameter + sp.Rational(endpoint)), parameter, domain=sp.QQ)
    order = min(index for index in range(shifted.degree() + 1) if shifted.nth(index) != 0)
    constant = abs(Fraction(shifted.nth(order)))
    remainder = sum(
        (abs(Fraction(shifted.nth(index))) for index in range(order + 1, shifted.degree() + 1)), Fraction(0)
    )
    return min(Fraction(1), constant / (2 * remainder)) if remainder else Fraction(1)


@dataclass(frozen=True)
class KernelLimitCertificate:
    parameter: sp.Symbol
    endpoint: Fraction
    generic_rank: int
    pivot_rows: tuple[int, ...]
    pivot_columns: tuple[int, ...]
    pivot_determinant: sp.Expr
    kernel_free_rows: tuple[int, ...]
    kernel_frame: sp.ImmutableMatrix
    exceptional_polynomial: sp.Expr
    punctured_radius: Fraction
    projector: sp.ImmutableMatrix
    limit_projector: sp.ImmutableMatrix
    limiting_frame: sp.ImmutableMatrix
    limiting_columns: tuple[int, ...]
    transport_frame: sp.ImmutableMatrix
    transport_gram: sp.ImmutableMatrix
    transport_determinant: sp.Expr
    endpoint_pivot_rows: tuple[int, ...]
    endpoint_pivot_columns: tuple[int, ...]
    endpoint_pivot_determinant: sp.Expr
    endpoint_free_rows: tuple[int, ...]
    endpoint_frame: sp.ImmutableMatrix
    attachment: sp.ImmutableMatrix

    @property
    def generic_nullity(self) -> int:
        return self.kernel_frame.cols

    @property
    def endpoint_nullity(self) -> int:
        return self.endpoint_frame.cols


def certify_kernel_limit(
    matrix: sp.MatrixBase, parameter: sp.Symbol, endpoint: int | Fraction = 0
) -> KernelLimitCertificate:
    """Certify the two-sided generic kernel limit at a rational real endpoint.

    Every real parameter outside the recorded finite exceptional set has the
    certified generic rank and projector. A punctured endpoint neighborhood
    excludes all other exceptional parameters. Matrix size and polynomial
    degree determine the cost; the algorithm imposes no support restriction.
    """
    operator = _operator(matrix, parameter)
    endpoint_value = _endpoint(endpoint)
    kernel, columns, free = _kernel(operator)
    rows, determinant = _minor(operator, columns)
    projector = (
        _cancel(kernel * (kernel.T * kernel).inv(method="DM") * kernel.T) if kernel.cols else sp.zeros(operator.cols)
    )
    limit = projector.subs(parameter, sp.Rational(endpoint_value))
    _require(not limit.has(sp.zoo, sp.nan, sp.oo, -sp.oo), "projector contains an unremoved real-endpoint pole")
    limiting_columns = _rref(limit)[1]
    limiting_frame = limit[:, list(limiting_columns)]
    transport_frame = _cancel(projector * limiting_frame)
    transport_gram = _cancel(transport_frame.T * transport_frame)
    transport_determinant = sp.cancel(transport_gram.det(method="domain-ge"))
    exceptional = _exceptional(operator, kernel, projector, determinant, transport_determinant, parameter)
    endpoint_operator = operator.subs(parameter, sp.Rational(endpoint_value))
    endpoint_kernel, endpoint_columns, endpoint_free = _kernel(endpoint_operator)
    endpoint_rows, endpoint_determinant = _minor(endpoint_operator, endpoint_columns)
    attachment = limiting_frame[list(endpoint_free), :]
    certificate = KernelLimitCertificate(
        parameter,
        endpoint_value,
        len(columns),
        rows,
        columns,
        determinant,
        free,
        sp.ImmutableMatrix(kernel),
        exceptional,
        _radius(exceptional, parameter, endpoint_value),
        sp.ImmutableMatrix(projector),
        sp.ImmutableMatrix(limit),
        sp.ImmutableMatrix(limiting_frame),
        limiting_columns,
        sp.ImmutableMatrix(transport_frame),
        sp.ImmutableMatrix(transport_gram),
        transport_determinant,
        endpoint_rows,
        endpoint_columns,
        endpoint_determinant,
        endpoint_free,
        sp.ImmutableMatrix(endpoint_kernel),
        sp.ImmutableMatrix(attachment),
    )
    _require(verify_kernel_limit(operator, certificate), "constructed kernel-limit certificate fails verification")
    return certificate


def _indices(indices: tuple[int, ...], size: int, count: int) -> bool:
    return (
        isinstance(indices, tuple)
        and len(indices) == count
        and len(set(indices)) == count
        and all(type(index) is int and 0 <= index < size for index in indices)
    )


def verify_kernel_limit(matrix: sp.MatrixBase, certificate: KernelLimitCertificate) -> bool:
    """Check independent rank bounds, projector identities and endpoint inclusion."""
    try:
        operator = _operator(matrix, certificate.parameter)
        endpoint = _endpoint(certificate.endpoint)
        parameter = certificate.parameter
        rank = certificate.generic_rank
        dimension = operator.cols
        if type(rank) is not int or not 0 <= rank <= min(operator.shape):
            return False
        nullity = dimension - rank
        if not _indices(certificate.pivot_rows, operator.rows, rank) or not _indices(
            certificate.pivot_columns, dimension, rank
        ):
            return False
        determinant = operator.extract(certificate.pivot_rows, certificate.pivot_columns).det(method="domain-ge")
        if sp.cancel(determinant) == 0 or sp.cancel(determinant - certificate.pivot_determinant) != 0:
            return False
        frame = sp.Matrix(certificate.kernel_frame)
        if frame.shape != (dimension, nullity) or not _indices(certificate.kernel_free_rows, dimension, nullity):
            return False
        if not _equal(operator * frame, sp.zeros(operator.rows, nullity)) or not _equal(
            frame[list(certificate.kernel_free_rows), :], sp.eye(nullity)
        ):
            return False
        projector = sp.Matrix(certificate.projector)
        if projector.shape != (dimension, dimension):
            return False
        if not all(
            (
                _equal(projector, projector.T),
                _equal(projector * projector, projector),
                _equal(operator * projector, sp.zeros(operator.rows, dimension)),
                _equal(projector * frame, frame),
                sp.cancel(projector.trace() - nullity) == 0,
            )
        ):
            return False
        transport_frame = _cancel(projector * certificate.limiting_frame)
        transport_gram = _cancel(transport_frame.T * transport_frame)
        transport_determinant = sp.cancel(transport_gram.det(method="domain-ge"))
        if not _equal(transport_frame, certificate.transport_frame) or not _equal(
            transport_gram, certificate.transport_gram
        ):
            return False
        if transport_determinant == 0 or sp.cancel(transport_determinant - certificate.transport_determinant) != 0:
            return False
        exceptional = _exceptional(operator, frame, projector, determinant, transport_determinant, parameter)
        if sp.expand(exceptional - certificate.exceptional_polynomial) != 0:
            return False
        if _endpoint(certificate.punctured_radius) != _radius(exceptional, parameter, endpoint):
            return False
        limit = _cancel(projector).subs(parameter, sp.Rational(endpoint))
        if limit.has(sp.zoo, sp.nan, sp.oo, -sp.oo) or not _equal(limit, certificate.limit_projector):
            return False
        if not _equal(limit, limit.T) or not _equal(limit * limit, limit) or limit.trace() != nullity:
            return False
        endpoint_operator = operator.subs(parameter, sp.Rational(endpoint))
        endpoint_rank = len(certificate.endpoint_pivot_columns)
        endpoint_nullity = dimension - endpoint_rank
        if not _indices(certificate.endpoint_pivot_rows, operator.rows, endpoint_rank) or not _indices(
            certificate.endpoint_pivot_columns, dimension, endpoint_rank
        ):
            return False
        endpoint_determinant = endpoint_operator.extract(
            certificate.endpoint_pivot_rows, certificate.endpoint_pivot_columns
        ).det(method="domain-ge")
        if endpoint_determinant == 0 or endpoint_determinant != certificate.endpoint_pivot_determinant:
            return False
        endpoint_frame = sp.Matrix(certificate.endpoint_frame)
        if endpoint_frame.shape != (dimension, endpoint_nullity) or not _indices(
            certificate.endpoint_free_rows, dimension, endpoint_nullity
        ):
            return False
        if not _equal(endpoint_operator * endpoint_frame, sp.zeros(operator.rows, endpoint_nullity)) or not _equal(
            endpoint_frame[list(certificate.endpoint_free_rows), :], sp.eye(endpoint_nullity)
        ):
            return False
        if not _indices(certificate.limiting_columns, dimension, nullity):
            return False
        limiting_frame = sp.Matrix(certificate.limiting_frame)
        if not _equal(limiting_frame, limit[:, list(certificate.limiting_columns)]):
            return False
        if _rref(limiting_frame)[1] != tuple(range(nullity)):
            return False
        return _equal(endpoint_frame * certificate.attachment, limiting_frame) and _equal(
            endpoint_operator * limit, sp.zeros(operator.rows, dimension)
        )
    except (
        ValueError,
        TypeError,
        AttributeError,
        IndexError,
        ZeroDivisionError,
        sp.polys.polyerrors.BasePolynomialError,
        sp.matrices.exceptions.MatrixError,
    ):
        return False


def extend_limiting_partner(
    certificate: KernelLimitCertificate, partner: Sequence[int | Fraction]
) -> sp.ImmutableMatrix:
    """Return P(t)y0 for an exact vector in the limiting kernel.

    Positive norm normalization yields the unit-partner extension in the proof.
    The exact API retains the unnormalized rational vector and accepts zero.
    """
    dimension = certificate.projector.rows
    if (
        not isinstance(partner, Sequence)
        or isinstance(partner, (str, bytes))
        or len(partner) != dimension
        or any(isinstance(value, bool) or not isinstance(value, (int, Fraction)) for value in partner)
    ):
        raise ValueError("partner must contain exactly the ambient number of integers or Fractions")
    vector = sp.Matrix([sp.Rational(value) for value in partner])
    if certificate.limit_projector * vector != vector:
        raise ValueError("partner lies outside the limiting kernel subspace")
    return sp.ImmutableMatrix(_cancel(certificate.projector * vector))


def cd_polynomial_matrix(
    coefficients: Sequence[int | Fraction | sp.Expr], parameter: sp.Symbol, side: str = "left"
) -> sp.Matrix:
    """Construct the exact CD operator with arbitrary polynomial coefficients."""
    _parameter(parameter)
    if not isinstance(coefficients, Sequence) or isinstance(coefficients, (str, bytes)):
        raise ValueError("coefficients must be a nonempty sequence")
    dimension = len(coefficients)
    if dimension < 1 or dimension & (dimension - 1):
        raise ValueError("the Cayley-Dickson dimension must be a positive power of two")
    if side not in ("left", "right"):
        raise ValueError("multiplication side must be left or right")
    values = tuple(_polynomial(value, parameter) for value in coefficients)
    return sp.Matrix(
        dimension,
        dimension,
        lambda row, column: values[row ^ column]
        * (cd_sign(dimension, row ^ column, column) if side == "left" else cd_sign(dimension, column, row ^ column)),
    )
