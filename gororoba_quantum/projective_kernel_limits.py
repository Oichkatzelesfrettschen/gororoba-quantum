"""Polynomial kernel-frame saturation and leading projective Pfaffian limits.

Exact division by the endpoint parameter removes a common exterior factor.
The endpoint frame and one complementary Pfaffian then determine every leading
Plucker coordinate. Real graph-closure coverage remains a separate obligation.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations

import sympy as sp

from complex_skew import pfaffian
from kernel_limits import cd_polynomial_matrix


def _endpoint(value: int | Fraction) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise ValueError("endpoint must be an integer or Fraction")
    return Fraction(value)


def _poly(value: sp.Expr, parameter: sp.Symbol) -> sp.Poly:
    expression = sp.sympify(value)
    if expression.has(sp.Float) or expression.free_symbols - {parameter}:
        raise ValueError("entries must belong to Q(i)[parameter]")
    try:
        return sp.Poly(expression, parameter, domain=sp.QQ_I)
    except sp.polys.polyerrors.BasePolynomialError as error:
        raise ValueError("entries must belong to Q(i)[parameter]") from error


def _operator(matrix: sp.MatrixBase, parameter: sp.Symbol) -> sp.ImmutableMatrix:
    if not isinstance(parameter, sp.Symbol) or parameter.is_real is not True:
        raise ValueError("parameter must be a real SymPy symbol")
    if not isinstance(matrix, sp.MatrixBase) or matrix.rows < 1 or matrix.rows != matrix.cols:
        raise ValueError("operator must be a nonempty square polynomial skew matrix")
    result = sp.ImmutableMatrix(matrix.applyfunc(lambda value: _poly(value, parameter).as_expr()))
    if (result + result.T).applyfunc(sp.expand) != sp.zeros(result.rows):
        raise ValueError("operator must be skew under transpose")
    return result


def _kernel(matrix: sp.MatrixBase) -> sp.Matrix:
    reduced, pivots = matrix.to_DM().to_field().rref()
    reduced_matrix = reduced.to_Matrix()
    free = tuple(index for index in range(matrix.cols) if index not in pivots)
    result = sp.eye(matrix.cols)[:, list(free)]
    for column, index in enumerate(free):
        for row, pivot in enumerate(pivots):
            result[pivot, column] = -reduced_matrix[row, index]
    return result


def _independent_rows(matrix: sp.MatrixBase) -> tuple[int, ...]:
    return tuple(int(index) for index in matrix.T.to_DM().to_field().rref()[1]) if matrix.cols else ()


def _clear_columns(matrix: sp.MatrixBase, parameter: sp.Symbol) -> sp.ImmutableMatrix:
    result = sp.Matrix(matrix)
    for column in range(result.cols):
        denominator = _poly(sp.Integer(1), parameter)
        for value in result[:, column]:
            denominator = denominator.lcm(_poly(sp.fraction(sp.cancel(value))[1], parameter))
        result[:, column] = (result[:, column] * denominator.as_expr()).applyfunc(sp.cancel)
    return sp.ImmutableMatrix(result)


def _order(value: sp.Expr, parameter: sp.Symbol, endpoint: Fraction) -> tuple[int, sp.Expr]:
    shifted = _poly(sp.expand(value.subs(parameter, parameter + sp.Rational(endpoint))), parameter)
    if shifted.is_zero:
        raise ValueError("vanishing order requires a nonzero polynomial")
    order = min(monomial[0] for monomial in shifted.monoms())
    return order, shifted.nth(order)


def _radius(polynomial: sp.Expr, parameter: sp.Symbol, endpoint: Fraction) -> Fraction:
    order, leading = _order(polynomial, parameter, endpoint)
    shifted = sp.Poly(polynomial.subs(parameter, parameter + sp.Rational(endpoint)), parameter, domain=sp.QQ)
    remainder = sum(
        (abs(Fraction(shifted.nth(index))) for index in range(order + 1, shifted.degree() + 1)), Fraction(0)
    )
    return min(Fraction(1), abs(Fraction(leading)) / (2 * remainder)) if remainder else Fraction(1)


def _equal(first: sp.MatrixBase, second: sp.MatrixBase) -> bool:
    return first.shape == second.shape and (first - second).applyfunc(sp.cancel).is_zero_matrix is True


@dataclass(frozen=True)
class KernelDivision:
    column: int
    coefficients: tuple[sp.Expr, ...]


def _divide(
    frame: sp.MatrixBase, division: KernelDivision, parameter: sp.Symbol, endpoint: Fraction
) -> sp.ImmutableMatrix:
    if (
        not isinstance(division, KernelDivision)
        or type(division.column) is not int
        or not 0 <= division.column < frame.cols
    ):
        raise ValueError("invalid division column")
    coefficients = division.coefficients
    if type(coefficients) is not tuple or len(coefficients) != frame.cols:
        raise ValueError("division coefficients have the wrong shape")
    if any(_poly(value, parameter).degree() > 0 for value in coefficients) or coefficients[division.column] != 1:
        raise ValueError("division requires constant coefficients with selected coefficient one")
    numerator = frame * sp.Matrix(coefficients)
    divisor = _poly(parameter - sp.Rational(endpoint), parameter)
    quotient = []
    for value in numerator:
        divided, remainder = _poly(value, parameter).div(divisor)
        if not remainder.is_zero:
            raise ValueError("kernel column combination lacks the endpoint factor")
        quotient.append(divided.as_expr())
    result = sp.Matrix(frame)
    result[:, division.column] = sp.Matrix(quotient)
    return sp.ImmutableMatrix(result)


@dataclass(frozen=True)
class ProjectiveKernelLimit:
    parameter: sp.Symbol
    endpoint: Fraction
    generic_rank: int
    seed_frame: sp.ImmutableMatrix
    initial_rows: tuple[int, ...]
    initial_minor_order: int
    divisions: tuple[KernelDivision, ...]
    regular_frame: sp.ImmutableMatrix
    free_rows: tuple[int, ...]
    limit_frame: sp.ImmutableMatrix
    pivot_pfaffian: sp.Expr
    vanishing_order: int
    leading_factor: sp.Expr
    admission_polynomial: sp.Expr
    punctured_radius: Fraction


def _admission(pivot: sp.Expr, minor: sp.Expr, parameter: sp.Symbol) -> sp.Expr:
    product = sp.expand(pivot * minor)
    squared_norm = sp.expand(product * sp.conjugate(product))
    return sp.Poly(squared_norm, parameter, domain=sp.QQ).sqf_part().monic().as_expr()


def certify_projective_limit(
    matrix: sp.MatrixBase, parameter: sp.Symbol, endpoint: int | Fraction = 0
) -> ProjectiveKernelLimit:
    """Recover a complete limiting kernel and its leading Pfaffian volume.

    The algorithm removes at most the recorded initial minor's vanishing order
    of common exterior factors. It uses polynomial identities over Q(i), not
    numerical ranks or a sampled direction census.
    """
    operator = _operator(matrix, parameter)
    endpoint_value = _endpoint(endpoint)
    seed = _clear_columns(_kernel(operator), parameter)
    rows = _independent_rows(seed)
    initial_minor = seed.extract(rows, range(seed.cols)).det(method="domain-ge")
    bound = _order(initial_minor, parameter, endpoint_value)[0]
    frame = seed
    divisions: list[KernelDivision] = []
    while True:
        endpoint_frame = frame.subs(parameter, sp.Rational(endpoint_value))
        relations = _kernel(endpoint_frame)
        if relations.cols == 0:
            break
        if len(divisions) >= bound:
            raise RuntimeError("kernel saturation exceeds its nonzero-minor termination bound")
        relation = relations[:, 0]
        column = next(index for index, value in enumerate(relation) if value != 0)
        coefficients = tuple(sp.cancel(value / relation[column]) for value in relation)
        division = KernelDivision(column, coefficients)
        frame = _divide(frame, division, parameter, endpoint_value)
        divisions.append(division)
    free = _independent_rows(endpoint_frame)
    minor = frame.extract(free, range(frame.cols)).det(method="domain-ge")
    limit = endpoint_frame * endpoint_frame.extract(free, range(frame.cols)).inv()
    pivot = tuple(index for index in range(operator.rows) if index not in free)
    pivot_value = pfaffian(operator.extract(pivot, pivot))
    order, leading = _order(pivot_value, parameter, endpoint_value)
    sign = (-1) ** sum(index - position for position, index in enumerate(pivot))
    admission = _admission(pivot_value, minor, parameter)
    certificate = ProjectiveKernelLimit(
        parameter,
        endpoint_value,
        operator.rows - frame.cols,
        seed,
        rows,
        bound,
        tuple(divisions),
        frame,
        free,
        sp.ImmutableMatrix(limit.applyfunc(sp.cancel)),
        pivot_value,
        order,
        sp.expand(sign * leading),
        admission,
        _radius(admission, parameter, endpoint_value),
    )
    if not verify_projective_limit(operator, certificate):
        raise RuntimeError("constructed projective kernel-limit certificate fails verification")
    return certificate


def _indices(indices: tuple[int, ...], size: int, count: int) -> bool:
    return (
        type(indices) is tuple
        and len(indices) == count
        and all(type(index) is int and 0 <= index < size for index in indices)
        and tuple(sorted(set(indices))) == indices
    )


def verify_projective_limit(matrix: sp.MatrixBase, certificate: ProjectiveKernelLimit) -> bool:
    """Verify division witnesses, independent rank bounds and endpoint minors."""
    try:
        if not isinstance(certificate, ProjectiveKernelLimit):
            return False
        parameter = certificate.parameter
        endpoint = _endpoint(certificate.endpoint)
        operator = _operator(matrix, parameter)
        dimension = operator.rows
        rank = certificate.generic_rank
        if type(rank) is not int or rank % 2 or not 0 <= rank <= dimension:
            return False
        nullity = dimension - rank
        if any(
            type(value) is not sp.ImmutableMatrix
            for value in (certificate.seed_frame, certificate.regular_frame, certificate.limit_frame)
        ):
            return False
        seed = certificate.seed_frame
        if seed.shape != (dimension, nullity) or not _indices(certificate.initial_rows, dimension, nullity):
            return False
        for value in seed:
            _poly(value, parameter)
        initial_minor = seed.extract(certificate.initial_rows, range(nullity)).det(method="domain-ge")
        initial_order = _order(initial_minor, parameter, endpoint)[0]
        if type(certificate.initial_minor_order) is not int or certificate.initial_minor_order != initial_order:
            return False
        if type(certificate.divisions) is not tuple or len(certificate.divisions) > initial_order:
            return False
        if not _equal(operator * seed, sp.zeros(dimension, nullity)):
            return False
        frame = seed
        for division in certificate.divisions:
            frame = _divide(frame, division, parameter, endpoint)
        if not _equal(frame, certificate.regular_frame) or not _indices(certificate.free_rows, dimension, nullity):
            return False
        free = certificate.free_rows
        minor = sp.cancel(frame.extract(free, range(nullity)).det(method="domain-ge"))
        if minor.subs(parameter, sp.Rational(endpoint)) == 0:
            return False
        endpoint_frame = frame.subs(parameter, sp.Rational(endpoint))
        limit = endpoint_frame * endpoint_frame.extract(free, range(nullity)).inv()
        if not _equal(limit, certificate.limit_frame) or not _equal(
            operator.subs(parameter, sp.Rational(endpoint)) * limit, sp.zeros(dimension, nullity)
        ):
            return False
        pivot = tuple(index for index in range(dimension) if index not in free)
        pivot_value = pfaffian(operator.extract(pivot, pivot))
        if sp.cancel(pivot_value - certificate.pivot_pfaffian) != 0:
            return False
        order, leading = _order(pivot_value, parameter, endpoint)
        sign = (-1) ** sum(index - position for position, index in enumerate(pivot))
        if (
            type(certificate.vanishing_order) is not int
            or order != certificate.vanishing_order
            or sp.cancel(sign * leading - certificate.leading_factor) != 0
        ):
            return False
        admission = _admission(pivot_value, minor, parameter)
        return sp.expand(admission - certificate.admission_polynomial) == 0 and _endpoint(
            certificate.punctured_radius
        ) == _radius(admission, parameter, endpoint)
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


def leading_plucker_coordinates(
    matrix: sp.MatrixBase, certificate: ProjectiveKernelLimit
) -> Iterator[tuple[tuple[int, ...], sp.Expr]]:
    """Yield the complete leading exterior vector lazily after verification."""
    if not verify_projective_limit(matrix, certificate):
        raise ValueError("leading coordinates require an intact projective-limit certificate")
    frame = certificate.limit_frame
    for free in combinations(range(frame.rows), frame.cols):
        minor = frame.extract(free, range(frame.cols)).det(method="domain-ge")
        yield free, sp.expand(certificate.leading_factor * minor)


def cd_skew_path(coefficients: Sequence[int | Fraction | sp.Expr], parameter: sp.Symbol) -> sp.ImmutableMatrix:
    """Construct L_a-i*R_b for a doubly-pure polynomial CD path."""
    if not isinstance(coefficients, Sequence) or isinstance(coefficients, (str, bytes)):
        raise ValueError("coefficients must be a sequence")
    dimension = len(coefficients)
    if dimension < 4 or dimension & (dimension - 1):
        raise ValueError("dimension must be a power of two at least four")
    half = dimension // 2
    left = cd_polynomial_matrix(coefficients[:half], parameter, "left")
    right = cd_polynomial_matrix(coefficients[half:], parameter, "right")
    if (
        not _poly(sp.sympify(coefficients[0]), parameter).is_zero
        or not _poly(sp.sympify(coefficients[half]), parameter).is_zero
    ):
        raise ValueError("both scalar coefficients must vanish")
    return _operator(left - sp.I * right, parameter)
