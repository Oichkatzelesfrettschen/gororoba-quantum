"""Exact trace/Newton evaluations of Cayley-Dickson rank-locus polynomials.

For D=2^n with n>=2, put N=||x||^2, B=L_x^T L_x, and m=D/4-1.
The recurrence q_i=tr(B^i)/4-N^i and j E_j=sum((-1)^(i-1) E_(j-i) q_i)
defines polynomials on every real input. The cited fourfold-multiplicity
theorem makes E_j nonnegative elementary symmetric functions of the reduced
spectrum. The evaluator accepts integers and Fraction values only; finite
audits validate the implementation independently of the all-real theorem.

Every E_j has zero gradient on its zero locus because E_j is globally
nonnegative. A scalar E_j Jacobian therefore cannot certify a smooth rank
stratum. Exact rank predicates alone supply neither a triangulation nor a
description of attachments between strata.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import cast

import sympy as sp
from sympy.polys.matrices import DomainMatrix

import parallel
from cd_core import cd_sign

ExactScalar = int | Fraction
AUDIT_DIMENSIONS = (4, 8, 16, 32, 64)
DENSE_SEED = 20261011
SOURCES = (
    {
        "url": "https://arxiv.org/html/0905.2987v1",
        "source_read_sha256": "68e52e0c408e8bbfd663c921188acb6f6f01cbd53bce99ac441ea5bfc5ac66d0",
        "claims": "Propositions 3.9, 3.13 and 3.20: positivity, norm eigenvalue and fourfold eigenspaces",
    },
    {
        "url": "https://arxiv.org/html/2608.08232v1",
        "source_read_sha256": "e7cb0aace6a034943a1ee99ece0796d3f05fc777ac1ecf4803b4e722bcc507c9",
        "claims": "Definitions 3.1 and 3.3, Proposition 4.3 and Section 9: trace/Newton construction",
    },
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _exact_scalar(value: ExactScalar) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, int | Fraction):
        raise ValueError("exact coordinates must be int or Fraction; binary floats are outside the contract")
    return Fraction(value)


def _exact_vector(coordinates: Sequence[ExactScalar]) -> tuple[Fraction, ...]:
    dimension = len(coordinates)
    if dimension < 4 or dimension & (dimension - 1):
        raise ValueError("coordinate dimension must be a power of two at least four")
    return tuple(_exact_scalar(value) for value in coordinates)


def _fraction(value: sp.Rational) -> Fraction:
    numerator, denominator = value.as_numer_denom()
    return Fraction(int(numerator), int(denominator))


def _integer_left_matrix(coordinates: tuple[Fraction, ...]) -> tuple[sp.Matrix, int]:
    denominator = math.lcm(*(value.denominator for value in coordinates))
    coefficients = [int(value * denominator) for value in coordinates]
    dimension = len(coordinates)
    matrix = sp.zeros(dimension)
    for basis_index, coefficient in enumerate(coefficients):
        if coefficient:
            for column in range(dimension):
                matrix[basis_index ^ column, column] = coefficient * cd_sign(dimension, basis_index, column)
    return matrix, denominator


def newton_elementary(power_sums: Sequence[ExactScalar]) -> tuple[Fraction, ...]:
    """Return E_0=1 followed by the exact Newton elementary coefficients."""
    sums = tuple(_exact_scalar(value) for value in power_sums)
    elementary = [Fraction(1)]
    for degree in range(1, len(sums) + 1):
        numerator = sum(
            ((-1) ** (index - 1) * elementary[degree - index] * sums[index - 1] for index in range(1, degree + 1)),
            start=Fraction(0),
        )
        elementary.append(numerator / degree)
    return tuple(elementary)


@dataclass(frozen=True)
class RankPolynomialEvaluation:
    dimension: int
    norm_squared: Fraction
    gram_power_traces: tuple[Fraction, ...]
    reduced_power_sums: tuple[Fraction, ...]
    elementary: tuple[Fraction, ...]
    predicted_nullity: int


@dataclass(frozen=True)
class IncidencePresentation:
    dimension: int
    base_variables: tuple[sp.Symbol, ...]
    partner_variables: tuple[sp.Symbol, ...]
    product_equations: tuple[sp.Expr, ...]
    unit_equations: tuple[sp.Expr, sp.Expr]


def incidence_presentation(dimension: int) -> IncidencePresentation:
    """Present all real unit pairs (x,y) satisfying x*y=0 as polynomial zeros.

    F_l=sum_i cd_sign(D,i,i XOR l) x_i y_(i XOR l). The two additional
    equations impose sum x_i^2=sum y_i^2=1. The generator describes the
    complete incidence set in every supported algebraic dimension; it does
    not compute its components, triangulation, homology or attachment maps.
    """
    if isinstance(dimension, bool) or not isinstance(dimension, int) or dimension < 4 or dimension & (dimension - 1):
        raise ValueError("incidence dimension must be a power of two at least four")
    base_variables = sp.symbols(f"base_0:{dimension}", real=True)
    partner_variables = sp.symbols(f"partner_0:{dimension}", real=True)
    equations = tuple(
        sum(
            (
                cd_sign(dimension, index, index ^ output) * base_variables[index] * partner_variables[index ^ output]
                for index in range(dimension)
            ),
            start=sp.Integer(0),
        )
        for output in range(dimension)
    )
    return IncidencePresentation(
        dimension,
        base_variables,
        partner_variables,
        equations,
        (sum(value**2 for value in base_variables) - 1, sum(value**2 for value in partner_variables) - 1),
    )


def evaluate_rank_polynomials(coordinates: Sequence[ExactScalar]) -> RankPolynomialEvaluation:
    """Evaluate all reduced coefficients exactly, for any rational D=2^n input.

    The all-real rank predicate follows from the cited spectral theorem;
    rational arithmetic is the computational input boundary, not a restriction
    on the polynomial identity. The zero vector receives nullity D separately.
    """
    vector = _exact_vector(coordinates)
    dimension = len(vector)
    reduced_degree = dimension // 4 - 1
    norm_squared = sum((value * value for value in vector), start=Fraction(0))
    matrix, denominator = _integer_left_matrix(vector)
    gram = matrix.T * matrix
    power = sp.eye(dimension)
    traces = []
    for exponent in range(1, reduced_degree + 1):
        power = power * gram
        traces.append(Fraction(int(sp.trace(power)), denominator ** (2 * exponent)))
    reduced = tuple(trace / 4 - norm_squared**index for index, trace in enumerate(traces, start=1))
    elementary = newton_elementary(reduced)
    _require(all(value >= 0 for value in elementary), "reduced spectral coefficient became negative")
    positive_degree = max(index for index, value in enumerate(elementary) if value > 0)
    _require(all(value > 0 for value in elementary[: positive_degree + 1]), "spectral positivity has an interior gap")
    nullity = dimension if norm_squared == 0 else 4 * (reduced_degree - positive_degree)
    return RankPolynomialEvaluation(dimension, norm_squared, tuple(traces), reduced, elementary, nullity)


def rank_locus(evaluation: RankPolynomialEvaluation, nullity: int) -> bool:
    """Evaluate the all-real E-polynomial rank predicate on an exact evaluation.

    For nonzero x and 1<=k<=m, nullity 4k means E_(m-k)>0 and
    E_(m-k+1)=0; invertibility means E_m>0. The zero vector is separate.
    """
    dimension = evaluation.dimension
    if isinstance(nullity, bool) or not isinstance(nullity, int) or not 0 <= nullity <= dimension or nullity % 4:
        raise ValueError("nullity must be a multiple of four between zero and the coordinate dimension")
    if evaluation.norm_squared == 0:
        return nullity == dimension
    if nullity == dimension:
        return False
    reduced_degree = dimension // 4 - 1
    positive_degree = reduced_degree - nullity // 4
    if nullity == 0:
        return evaluation.elementary[reduced_degree] > 0
    return evaluation.elementary[positive_degree] > 0 and evaluation.elementary[positive_degree + 1] == 0


def directional_derivatives(
    coordinates: Sequence[ExactScalar], direction: Sequence[ExactScalar]
) -> tuple[Fraction, ...]:
    """Differentiate the trace/Newton recurrence exactly in one rational direction.

    d tr(B^i)=i tr(B^(i-1) dB), dB=L_h^T L_x+L_x^T L_h.
    Return dE_0=0 followed by dE_1 through dE_m.
    """
    vector = _exact_vector(coordinates)
    tangent = _exact_vector(direction)
    if len(vector) != len(tangent):
        raise ValueError("direction and coordinates must have equal dimensions")
    evaluation = evaluate_rank_polynomials(vector)
    integer_matrix, denominator = _integer_left_matrix(vector)
    integer_tangent, tangent_denominator = _integer_left_matrix(tangent)
    matrix = integer_matrix / denominator
    tangent_matrix = integer_tangent / tangent_denominator
    gram = matrix.T * matrix
    gram_derivative = tangent_matrix.T * matrix + matrix.T * tangent_matrix
    norm_derivative = 2 * sum((left * right for left, right in zip(vector, tangent, strict=True)), start=Fraction(0))
    power = sp.eye(len(vector))
    sum_derivatives = []
    for exponent in range(1, len(evaluation.elementary)):
        trace_derivative = exponent * _fraction(sp.trace(power * gram_derivative))
        sum_derivatives.append(
            trace_derivative / 4 - exponent * evaluation.norm_squared ** (exponent - 1) * norm_derivative
        )
        power = power * gram
    derivatives = [Fraction(0)]
    for degree in range(1, len(evaluation.elementary)):
        derivative = sum(
            (
                (-1) ** (index - 1)
                * (
                    derivatives[degree - index] * evaluation.reduced_power_sums[index - 1]
                    + evaluation.elementary[degree - index] * sum_derivatives[index - 1]
                )
                for index in range(1, degree + 1)
            ),
            start=Fraction(0),
        )
        derivatives.append(derivative / degree)
    return tuple(derivatives)


def _evaluation_record(evaluation: RankPolynomialEvaluation) -> dict[str, object]:
    return {
        "dimension": evaluation.dimension,
        "norm_squared": str(evaluation.norm_squared),
        "gram_power_traces": [str(value) for value in evaluation.gram_power_traces],
        "reduced_power_sums": [str(value) for value in evaluation.reduced_power_sums],
        "elementary_E0_through_Em": [str(value) for value in evaluation.elementary],
        "predicted_nullity": evaluation.predicted_nullity,
    }


def _audit_fixture(case: tuple[str, tuple[Fraction, ...]]) -> dict[str, object]:
    name, coordinates = case
    evaluation = evaluate_rank_polynomials(coordinates)
    integer_matrix, denominator = _integer_left_matrix(coordinates)
    matrix = integer_matrix / denominator
    dimension = len(coordinates)
    independent_rank = int(DomainMatrix.from_Matrix(integer_matrix).rank())
    _require(dimension - independent_rank == evaluation.predicted_nullity, "Newton predicate disagrees with exact rank")
    _require(
        [nullity for nullity in range(0, dimension + 1, 4) if rank_locus(evaluation, nullity)]
        == [evaluation.predicted_nullity],
        "rank-locus predicates fail unique admission",
    )
    variable = sp.Symbol("spectral_parameter")
    reduced_degree = dimension // 4 - 1
    reduced_polynomial = sum(
        (
            (-1) ** index * sp.Rational(value.numerator, value.denominator) * variable ** (reduced_degree - index)
            for index, value in enumerate(evaluation.elementary)
        ),
        start=sp.Integer(0),
    )
    norm = sp.Rational(evaluation.norm_squared.numerator, evaluation.norm_squared.denominator)
    expected_characteristic = sp.Poly(((variable - norm) * reduced_polynomial) ** 4, variable)
    actual_characteristic = sp.Poly((matrix.T * matrix).charpoly(variable).as_expr(), variable)
    _require(expected_characteristic == actual_characteristic, "fourfold characteristic identity failed")
    determinant = _fraction(matrix.det(method="domain-ge"))
    _require(
        determinant == evaluation.norm_squared**2 * evaluation.elementary[-1] ** 2,
        "left determinant factorization failed",
    )
    return {
        "fixture": name,
        "coordinates": [str(value) for value in coordinates],
        "evaluation": _evaluation_record(evaluation),
        "independent_exact_rank": independent_rank,
        "exact_determinant": str(determinant),
        "characteristic_identity": True,
        "unique_rank_locus": True,
    }


def _fixture_cases(maximum_dimension: int) -> list[tuple[str, tuple[Fraction, ...]]]:
    generator = random.Random(DENSE_SEED)
    cases = []
    for dimension in AUDIT_DIMENSIONS:
        if dimension > maximum_dimension:
            continue
        cases.append((f"zero_dimension_{dimension}", (Fraction(0),) * dimension))
        cases.append((f"scalar_dimension_{dimension}", (Fraction(3, 2),) + (Fraction(0),) * (dimension - 1)))
        for dense_index in range(2 if dimension <= 32 else 1):
            dense = tuple(Fraction(generator.randint(-5, 5), generator.randint(1, 5)) for _ in range(dimension))
            cases.append((f"dense_rational_dimension_{dimension}_case_{dense_index}", dense))
        if dimension >= 16:
            for second_index in sorted({2, dimension // 4 + 2, dimension // 2 + 2, dimension - dimension // 4 + 2}):
                vector = tuple(Fraction(int(index in (1, second_index))) for index in range(dimension))
                cases.append((f"sparse_dimension_{dimension}_e1_plus_e{second_index}", vector))
                if dimension == 32:
                    unit_vector = list(value / 2 for value in vector)
                    for index, value in enumerate(vector):
                        unit_vector[16 ^ index] += value * cd_sign(dimension, 16, index) / 2
                    cases.append((f"unit_complex_rotation_e1_plus_e{second_index}", tuple(unit_vector)))
            if dimension == 32:
                maximal = tuple(
                    Fraction(1, 2) if index in (1, 10, 18) else Fraction(-1, 2) if index == 25 else Fraction(0)
                    for index in range(dimension)
                )
                cases.append(("unit_maximal_lift_e1_e10_e18_minus_e25", maximal))
    return cases


def _audit_scaling_and_derivatives() -> dict[str, object]:
    dimension = 32
    coordinates = tuple(Fraction(int(index in (1, 18))) for index in range(dimension))
    evaluation = evaluate_rank_polynomials(coordinates)
    for scale in (Fraction(0), Fraction(-3, 2), Fraction(5, 3)):
        scaled = evaluate_rank_polynomials(tuple(scale * value for value in coordinates))
        _require(
            scaled.elementary
            == tuple(scale ** (2 * degree) * value for degree, value in enumerate(evaluation.elementary)),
            "homogeneous coefficient scaling failed",
        )
        _require(scaled.norm_squared == scale**2 * evaluation.norm_squared, "norm scaling failed")
        _require(
            scaled.predicted_nullity == (dimension if scale == 0 else evaluation.predicted_nullity),
            "rank scaling failed",
        )
    direction = tuple(Fraction((index % 7) - 3, (index % 3) + 1) for index in range(dimension))
    derivatives = directional_derivatives(coordinates, direction)
    vanishing = [degree for degree, value in enumerate(evaluation.elementary) if value == 0]
    _require(bool(vanishing), "gradient fixture must lie on a polynomial zero locus")
    _require(all(derivatives[degree] == 0 for degree in vanishing), "nonnegative zero-locus derivative failed")
    radial = directional_derivatives(coordinates, coordinates)
    _require(
        radial == tuple(2 * degree * value for degree, value in enumerate(evaluation.elementary)),
        "Euler homogeneous directional derivative identity failed",
    )
    return {
        "dimension": dimension,
        "scales": ["0", "-3/2", "5/3"],
        "coordinates": [str(value) for value in coordinates],
        "direction": [str(value) for value in direction],
        "directional_derivatives": [str(value) for value in derivatives],
        "vanishing_coefficients_with_zero_directional_derivative": vanishing,
        "euler_identity": True,
        "scope": "Finite derivative checks support the recurrence; global nonnegativity proves zero gradient at zeros.",
    }


def _audit_falsifiers() -> dict[str, object]:
    coordinates = tuple(Fraction(int(index in (1, 10))) for index in range(32))
    evaluation = evaluate_rank_polynomials(coordinates)
    missing_norm = newton_elementary(tuple(trace / 4 for trace in evaluation.gram_power_traces))
    wrong_multiplicity = newton_elementary(
        tuple(
            trace / 2 - evaluation.norm_squared**degree for degree, trace in enumerate(evaluation.gram_power_traces, 1)
        )
    )
    _require(missing_norm != evaluation.elementary, "omitted norm-eigenvalue subtraction mutation escaped")
    _require(wrong_multiplicity != evaluation.elementary, "wrong spectral multiplicity mutation escaped")
    wrong_signs = [Fraction(1)]
    for degree in range(1, len(evaluation.elementary)):
        wrong_signs.append(
            sum(
                (
                    wrong_signs[degree - index] * evaluation.reduced_power_sums[index - 1]
                    for index in range(1, degree + 1)
                ),
                start=Fraction(0),
            )
            / degree
        )
    _require(wrong_signs[-1] > 0 and evaluation.elementary[-1] == 0, "Newton alternating-sign mutation escaped")
    rejected = 0
    invalid_inputs = ([0, 0], [0] * 6, [1.0, 0, 0, 0], [float("nan"), 0, 0, 0], [True, 0, 0, 0], [1j, 0, 0, 0])
    for invalid in invalid_inputs:
        try:
            evaluate_rank_polynomials(invalid)  # type: ignore[arg-type]
        except ValueError:
            rejected += 1
        else:
            raise RuntimeError("input outside exact rational dimension contract accepted")
    return {
        "omitted_norm_subtraction_detected": True,
        "wrong_fourfold_multiplicity_detected": True,
        "newton_alternating_sign_mutation_detected": True,
        "rejected_inputs": rejected,
    }


def _audit_incidence_presentation() -> dict[str, object]:
    dimension = 32
    presentation = incidence_presentation(dimension)
    coordinates = tuple(Fraction(index - 3, index % 5 + 2) for index in range(dimension))
    partner = tuple(Fraction(index + 1, index % 7 + 3) for index in range(dimension))
    values = coordinates + partner
    variables = presentation.base_variables + presentation.partner_variables
    substitution = {
        variable: sp.Rational(value.numerator, value.denominator)
        for variable, value in zip(variables, values, strict=True)
    }
    matrix, denominator = _integer_left_matrix(coordinates)
    expected_product = matrix * sp.Matrix([sp.Rational(value.numerator, value.denominator) for value in partner])
    evaluated_product = tuple(expression.xreplace(substitution) for expression in presentation.product_equations)
    _require(
        all(value == expected_product[index] / denominator for index, value in enumerate(evaluated_product)),
        "incidence equations disagree with exact left multiplication",
    )
    unit_values = tuple(expression.xreplace(substitution) for expression in presentation.unit_equations)
    _require(
        tuple(_fraction(value) for value in unit_values)
        == (sum(value * value for value in coordinates) - 1, sum(value * value for value in partner) - 1),
        "incidence normalization equations changed",
    )
    unit_base = tuple(sp.sqrt(2) / 2 if index in (1, 10) else sp.Integer(0) for index in range(dimension))
    unit_partner = tuple(
        sp.sqrt(2) / 2 if index == 4 else -sp.sqrt(2) / 2 if index == 15 else sp.Integer(0)
        for index in range(dimension)
    )
    witness_substitution = dict(zip(variables, unit_base + unit_partner, strict=True))
    _require(
        all(
            expression.xreplace(witness_substitution) == 0
            for expression in presentation.product_equations + presentation.unit_equations
        ),
        "exact normalized incidence witness failed",
    )
    corrupted = (
        presentation.product_equations[0] - 2 * presentation.base_variables[0] * presentation.partner_variables[0]
    )
    _require(
        corrupted.xreplace(substitution) != evaluated_product[0],
        "incidence coefficient-sign mutation escaped",
    )
    return {
        "construction_domain": "all real unit pairs in dimension D=2^n, n>=2",
        "product_formula": "F_l(x,y)=sum_i cd_sign(D,i,i XOR l)*x_i*y_(i XOR l)",
        "normalization_equations": ["sum_i x_i^2-1", "sum_i y_i^2-1"],
        "finite_checked_dimension": dimension,
        "product_equations_checked": len(presentation.product_equations),
        "bilinear_terms_per_equation": dimension,
        "unit_equations_checked": 2,
        "unit_base_witness": [str(value) for value in unit_base],
        "unit_partner_witness": [str(value) for value in unit_partner],
        "witness_arithmetic": "exact algebraic sqrt(2), without numerical approximations",
        "coefficient_sign_mutation_detected": True,
        "scope": "Complete real algebraic set presentation; finite substitution checks validate the generator.",
    }


def audit_rank_polynomials(maximum_dimension: int = 32) -> dict[str, object]:
    """Check the generic recurrence on a finite exact-rational corpus."""
    if maximum_dimension not in AUDIT_DIMENSIONS:
        raise ValueError(f"maximum_dimension must be one of {AUDIT_DIMENSIONS}")
    cases = _fixture_cases(maximum_dimension)
    fixtures = parallel.ordered_map(_audit_fixture, cases, min_items=2)
    unit_nullities = sorted(
        {
            32 - cast(int, record["independent_exact_rank"])
            for record in fixtures
            if cast(str, record["fixture"]).startswith("unit_")
        }
    )
    if maximum_dimension >= 32:
        _require(unit_nullities == [0, 4, 8, 12, 16], "dimension-32 unit rank-locus regression coverage changed")
        _require(
            all(
                sum(value * value for value in coordinates) == 1
                for name, coordinates in cases
                if name.startswith("unit_")
            ),
            "unit rank-locus witness normalization failed",
        )
    return {
        "schema": "cayley-dickson-rank-polynomials-v1",
        "qpu_executed": False,
        "execution": "local exact integer and rational arithmetic",
        "versions": {"python": platform.python_version(), "sympy": sp.__version__},
        "source_provenance": list(SOURCES),
        "multiplication_source_sha256": hashlib.sha256(Path(__file__).with_name("cd_core.py").read_bytes()).hexdigest(),
        "computational_domain": "int and Fraction coordinates; binary floats rejected",
        "construction_domain": "all real x in dimension 2^n for every n>=2, by the cited spectral theorem",
        "recurrence": "m=D/4-1; N=sum(x_i^2); q_i=tr((L_x^T L_x)^i)/4-N^i; E_0=1; j E_j=sum_i(-1)^(i-1)E_(j-i)q_i",
        "degrees": "E_j is homogeneous of degree 2j",
        "rank_predicate": "x!=0: nullity4k iff E_(m-k)>0 and E_(m-k+1)=0; k=0 iff E_m>0; x=0 has nullity D",
        "characteristic_identity": "chi_(L_x^T L_x)(z)=[(z-N) sum_j(-1)^j E_j z^(m-j)]^4",
        "smoothness_boundary": (
            "E_j>=0 on all real inputs, so grad(E_j)=0 at every zero; scalar Jacobians cannot certify smoothness"
        ),
        "topology_boundary": (
            "Rank loci are described as sets; finite evaluations supply neither global triangulations "
            "nor attachment maps."
        ),
        "maximum_corpus_dimension": maximum_dimension,
        "fixed_regression_dimension": 32,
        "dense_seed": DENSE_SEED,
        "fixtures": fixtures,
        "dimension32_unit_nullities_checked": unit_nullities,
        "unit_incidence_presentation": _audit_incidence_presentation(),
        "scaling_and_directional_derivatives": _audit_scaling_and_derivatives(),
        "falsifiers": _audit_falsifiers(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-dimension", type=int, choices=AUDIT_DIMENSIONS, default=32)
    arguments = parser.parse_args()
    print(json.dumps(audit_rank_polynomials(arguments.max_dimension), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
