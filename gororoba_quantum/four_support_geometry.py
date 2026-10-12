"""Smooth sign strata and partner incidence on one fixed CD coefficient support.

The real geometry follows the log-coordinate and constructive closure proofs
in docs/notes/four_support_incidence_geometry.md. Exact identities and finite
closure checks retain the executable evidence. The APIs use rational rays and
weighted fiber coordinates; positive frame normalization gives the all-real
unit-sphere model without numerical square roots.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Any

import sympy as sp

import parallel
from four_support_rank import (
    COEFFICIENTS,
    DIMENSION,
    evaluate_four_support,
    sector_indices,
    support_coordinates,
    symbolic_matrix,
)
from rank_charts import RationalMatrix, multiplication_matrix

LINEAR_TRANSFORM = sp.ImmutableMatrix([[1, -1, -1, -1], [1, -1, 1, 1], [1, 1, -1, 1], [1, 1, 1, -1]])
BLOCK_NAMES = ("cone", "p", "q", "r", "s")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _equal(actual: Any, expected: Any, label: str) -> None:
    difference = actual - expected
    valid = (
        difference.applyfunc(sp.expand) == sp.zeros(*difference.shape)
        if isinstance(difference, sp.MatrixBase)
        else sp.expand(difference) == 0
    )
    _require(bool(valid), label)


def _rationals(values: Sequence[int | Fraction], length: int) -> tuple[Fraction, ...]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)) or len(values) != length:
        raise ValueError(f"expected exactly {length} exact rational entries")
    if any(isinstance(value, bool) or not isinstance(value, (int, Fraction)) for value in values):
        raise ValueError("entries must be exact integers or Fractions")
    return tuple(Fraction(value) for value in values)


def _fractions(matrix: sp.Matrix) -> RationalMatrix:
    return tuple(tuple(Fraction(value) for value in row) for row in matrix.tolist())


def _sign(value: Fraction) -> int:
    return int(value > 0) - int(value < 0)


def _validate_signs(signs: tuple[int, ...]) -> None:
    if (
        not isinstance(signs, tuple)
        or len(signs) != 4
        or any(type(value) is not int or value not in (-1, 0, 1) for value in signs)
    ):
        raise ValueError("coordinate signs must be a tuple of four integers in {-1,0,1}")
    if not any(signs):
        raise ValueError("the origin lies outside the nonzero support geometry")


def allowed_cone_signs(signs: tuple[int, ...]) -> tuple[int, ...]:
    """Derive the feasible signs of Q=pq+rs on a nonempty orthant face."""
    _validate_signs(signs)
    first, second = signs[0] * signs[1], signs[2] * signs[3]
    if first == 0:
        return (second,)
    if second == 0 or first == second:
        return (first,)
    return (-1, 0, 1)


@dataclass(frozen=True)
class Stratum:
    signs: tuple[int, ...]
    cone_sign: int

    def __post_init__(self) -> None:
        feasible = allowed_cone_signs(self.signs)
        if type(self.cone_sign) is not int or self.cone_sign not in feasible:
            raise ValueError("cone sign is incompatible with the coordinate signs")

    @property
    def dimension(self) -> int:
        active = sum(value != 0 for value in self.signs)
        return active - 1 - int(active == 4 and self.cone_sign == 0)

    @property
    def kernel_slots(self) -> tuple[int, ...]:
        mask = (self.cone_sign == 0,) + tuple(value == 0 for value in self.signs)
        return tuple(4 * block + offset for block, active in enumerate(mask) if active for offset in range(4))

    @property
    def nullity(self) -> int:
        return len(self.kernel_slots)


def enumerate_strata() -> tuple[Stratum, ...]:
    """Generate every feasible label from coordinate-product signs."""
    return tuple(
        Stratum(signs, cone)
        for signs in product((-1, 0, 1), repeat=4)
        if any(signs)
        for cone in allowed_cone_signs(signs)
    )


def classify_linear_coordinates(values: Sequence[int | Fraction]) -> Stratum:
    """Classify a nonzero rational ray in the (p,q,r,s) coordinates."""
    p, q, r, s = _rationals(values, 4)
    return Stratum(tuple(_sign(value) for value in (p, q, r, s)), _sign(p * q + r * s))


def classify_coefficients(coefficients: Sequence[int | Fraction]) -> Stratum:
    """Classify x=a e1+b e10+c e18+d e25 without normalizing its ray."""
    values = _rationals(coefficients, 4)
    return classify_linear_coordinates(tuple(Fraction(value) for value in LINEAR_TRANSFORM * sp.Matrix(values)))


def stratum_witness(stratum: Stratum) -> tuple[Fraction, ...]:
    """Construct an exact rational ray witness for a feasible stratum."""
    values = [Fraction(value) for value in stratum.signs]
    if (
        all(stratum.signs)
        and stratum.signs[0] * stratum.signs[1] != stratum.signs[2] * stratum.signs[3]
        and stratum.cone_sign
    ):
        values[0] *= 2 if stratum.cone_sign == stratum.signs[0] * stratum.signs[1] else Fraction(1, 2)
    result = tuple(values)
    _require(classify_linear_coordinates(result) == stratum, "constructed ray has the wrong stratum label")
    return result


def closure_contains(source: Stratum, target: Stratum) -> bool:
    """Whether the entire target stratum lies in the closure of the source."""
    if not isinstance(source, Stratum) or not isinstance(target, Stratum):
        raise ValueError("closure arguments must be validated strata")
    return all(
        target_sign in (0, source_sign) for source_sign, target_sign in zip(source.signs, target.signs, strict=True)
    ) and target.cone_sign in (0, source.cone_sign)


def coordinate_inclusion(source: Stratum, target: Stratum) -> RationalMatrix:
    """Insert zero coordinates in newly available kernel slots along a closure."""
    if not closure_contains(source, target):
        raise ValueError("target lies outside the source closure")
    source_slots, target_slots = source.kernel_slots, target.kernel_slots
    _require(set(source_slots) <= set(target_slots), "source kernel slots fail to persist at the boundary")
    return tuple(
        tuple(Fraction(target_slot == source_slot) for source_slot in source_slots) for target_slot in target_slots
    )


def approach_ray(source: Stratum, target: Sequence[int | Fraction], parameter: int | Fraction) -> tuple[Fraction, ...]:
    """Approach a target ray through the source with any positive rational t.

    Radial normalization sends these rays to the support sphere. The explicit
    formulas converge to the given target as t decreases to zero.
    """
    values = _rationals(target, 4)
    value = _rationals((parameter,), 1)[0]
    if value <= 0:
        raise ValueError("approach parameter must be strictly positive")
    target_stratum = classify_linear_coordinates(values)
    if not closure_contains(source, target_stratum):
        raise ValueError("target lies outside the source closure")
    first_sign = source.signs[0] * source.signs[1]
    opposing = first_sign != 0 and first_sign == -source.signs[2] * source.signs[3]
    if opposing and target_stratum.cone_sign == 0:
        p, q, r, s = (abs(entry) for entry in values)
        matrix = sp.Matrix([[p, r], [s, q]])
        row, column = next((row, column) for row in range(2) for column in range(2) if matrix[row, column] > 0)
        first = matrix[:, column]
        second = matrix[row, :] / matrix[row, column]
        _require(first * second == matrix, "nonnegative cone factorization fails")
        regularized = (first + value * sp.ones(2, 1)) * (second + value * sp.ones(1, 2))
        determinant_sign = first_sign * source.cone_sign
        if determinant_sign > 0:
            regularized[0, 0] += value
        elif determinant_sign < 0:
            regularized[0, 1] += value
        magnitudes = (regularized[0, 0], regularized[1, 1], regularized[0, 1], regularized[1, 0])
        result = tuple(Fraction(magnitude) * sign for magnitude, sign in zip(magnitudes, source.signs, strict=True))
    else:
        step = value / (1 + value)
        if opposing:
            quadric = abs(values[0] * values[1] + values[2] * values[3])
            step *= quadric / (2 * (sum(abs(entry) for entry in values) + 2 + quadric))
        result = tuple(entry if entry else step * sign for entry, sign in zip(values, source.signs, strict=True))
    _require(classify_linear_coordinates(result) == source, "approach leaves the source stratum")
    return result


def _lift(representative: int, local: sp.Matrix, output: bool = False) -> sp.Matrix:
    rows, columns = sector_indices(representative)
    indices = rows if output else columns
    result = sp.zeros(DIMENSION, 1)
    for index, value in zip(indices, local, strict=True):
        result[index] = value
    return result


def _frame_matrices(values: Sequence[Any]) -> tuple[sp.Matrix, sp.Matrix, tuple[Any, ...], tuple[Any, ...]]:
    a, b, c, d = values
    first_pair, second_pair = a * a + b * b, c * c + d * d
    norm, quadric = first_pair + second_pair, first_pair - second_pair
    forms = LINEAR_TRANSFORM * sp.Matrix(values)
    mixed_difference, mixed_sum = a * d - b * c, a * c + b * d
    cone_vectors = (
        sp.Matrix([0, norm, 2 * mixed_difference, 2 * mixed_sum]),
        sp.Matrix([b, -a, -d, c]),
        sp.Matrix([d, -c, b, -a]),
        sp.Matrix([-2 * mixed_difference, -2 * mixed_sum, 0, norm]),
    )
    cone_residuals = (
        sp.Matrix([-b, a, d, -c]),
        sp.Matrix([0, 1, 0, 0]),
        sp.Matrix([0, 0, 0, -1]),
        sp.Matrix([d, -c, b, -a]),
    )
    columns = [_lift(index, vector) for index, vector in enumerate(cone_vectors)]
    residuals = [_lift(index, vector, output=True) for index, vector in enumerate(cone_residuals)]
    factors = [quadric] * 4
    constant, signs = LINEAR_TRANSFORM.T, sp.diag(1, -1, -1, 1)
    for form_index in range(4):
        for representative in range(4, 8):
            right = constant if representative in (4, 6) else signs * constant
            left = {4: signs * constant, 5: -constant, 6: -signs * constant, 7: constant}[representative]
            columns.append(_lift(representative, right[:, form_index] / 2))
            residuals.append(_lift(representative, left[:, form_index] / 2, output=True))
            factors.append(forms[form_index])
    quadratic_norm = norm**2 + 4 * first_pair * second_pair
    diagonal = (quadratic_norm, norm, norm, quadratic_norm) + (sp.Integer(1),) * 16
    return sp.Matrix.hstack(*columns), sp.Matrix.hstack(*residuals), diagonal, tuple(factors)


@dataclass(frozen=True)
class IncidenceFrame:
    coefficients: tuple[Fraction, ...]
    matrix: RationalMatrix
    gram_diagonal: tuple[Fraction, ...]
    factors: tuple[Fraction, ...]


def incidence_frame(coefficients: Sequence[int | Fraction]) -> IncidenceFrame:
    """Evaluate the global 20-column frame at a nonzero exact rational point."""
    values = _rationals(coefficients, 4)
    if not any(values):
        raise ValueError("global frame requires a nonzero coefficient tuple")
    frame, _, diagonal, factors = _frame_matrices(values)
    _require(all(value > 0 for value in diagonal), "global frame Gram diagonal must be positive")
    return IncidenceFrame(
        values,
        _fractions(frame),
        tuple(Fraction(value) for value in diagonal),
        tuple(Fraction(value) for value in factors),
    )


def lift_kernel_coordinates(
    coefficients: Sequence[int | Fraction], coordinates: Sequence[int | Fraction]
) -> tuple[Fraction, ...]:
    """Lift weighted 20-coordinates satisfying their factor equations to ker L_x."""
    point = incidence_frame(coefficients)
    values = _rationals(coordinates, 20)
    if any(factor * value for factor, value in zip(point.factors, values, strict=True)):
        raise ValueError("fiber coordinates violate the factor equations")
    return tuple(Fraction(value) for value in sp.Matrix(point.matrix) * sp.Matrix(values))


def kernel_coordinates(
    coefficients: Sequence[int | Fraction], partner: Sequence[int | Fraction]
) -> tuple[Fraction, ...]:
    """Recover weighted kernel coordinates with D^-1 G^T and check membership."""
    point = incidence_frame(coefficients)
    values = sp.Matrix(_rationals(partner, DIMENSION))
    matrix = sp.Matrix(multiplication_matrix(support_coordinates(point.coefficients)))
    if matrix * values != sp.zeros(DIMENSION, 1):
        raise ValueError("partner lies outside the left-multiplication kernel")
    frame = sp.Matrix(point.matrix)
    recovered = sp.diag(*(1 / value for value in point.gram_diagonal)) * frame.T * values
    result = tuple(Fraction(value) for value in recovered)
    _require(
        lift_kernel_coordinates(point.coefficients, result) == tuple(Fraction(value) for value in values),
        "global kernel inverse fails",
    )
    return result


def _audit_polynomial_frames() -> dict[str, Any]:
    frame, residual, diagonal, factors = _frame_matrices(COEFFICIENTS)
    norm = sum(value**2 for value in COEFFICIENTS)
    _equal(LINEAR_TRANSFORM * LINEAR_TRANSFORM.T, 4 * sp.eye(4), "invertible coefficient coordinates")
    _equal(frame.T * frame, sp.diag(*diagonal), "global positive diagonal Gram identity")
    _equal(residual.T * residual, sp.diag(norm, 1, 1, norm, *([1] * 16)), "residual frame independence")
    _equal(symbolic_matrix() * frame, residual * sp.diag(*factors), "global factor action")
    damaged = frame.copy()
    damaged[:, 4] = damaged[:, 0]
    try:
        _equal(damaged.T * damaged, sp.diag(*diagonal), "duplicated frame column")
    except RuntimeError:
        pass
    else:
        raise RuntimeError("duplicated global frame column accepted")
    damaged = frame.copy()
    row = next(index for index in range(DIMENSION) if damaged[index, 4] != 0)
    damaged[row, 4] *= -1
    try:
        _equal(symbolic_matrix() * damaged, residual * sp.diag(*factors), "sign-damaged frame action")
    except RuntimeError:
        pass
    else:
        raise RuntimeError("sign-damaged global frame accepted")
    return {
        "frame_shape": list(frame.shape),
        "frame_gram_diagonal": [str(value) for value in diagonal],
        "action_factors": [str(value) for value in factors],
        "residual_gram_diagonal": [str(value) for value in (norm, 1, 1, norm) + (1,) * 16],
        "polynomial_action": "L_x*G=R*diag(Delta I4,p I4,q I4,r I4,s I4)",
        "normalization": "F=G*D^(-1/2), using positive square roots; F^T F=I20",
        "weighted_inverse": "D^(-1)*G^T on ker L_x",
    }


def _audit_closure_polynomials() -> dict[str, Any]:
    u0, u1, v0, v1, parameter = sp.symbols("u0 u1 v0 v1 t", nonnegative=True)
    regularized = sp.Matrix([u0 + parameter, u1 + parameter]) * sp.Matrix([[v0 + parameter, v1 + parameter]])
    _equal(regularized.det(), 0, "positive rank-one regularization")
    _equal(
        (regularized + sp.Matrix([[parameter, 0], [0, 0]])).det(),
        parameter * regularized[1, 1],
        "positive determinant approach",
    )
    _equal(
        (regularized + sp.Matrix([[0, parameter], [0, 0]])).det(),
        -parameter * regularized[1, 0],
        "negative determinant approach",
    )
    entries = sp.symbols("m00 m01 m10 m11", real=True)
    matrix = sp.Matrix(2, 2, entries)
    for row in range(2):
        for column in range(2):
            numerator = matrix[row, column] * matrix - matrix[:, column] * matrix[row, :]
            expected = sp.zeros(2)
            expected[1 - row, 1 - column] = (-1) ** (row + column) * matrix.det()
            _equal(numerator, expected, "rank-one factorization on a nonzero pivot")
    first, second = sp.symbols("u v", real=True)
    square = sp.Matrix([[first * second, first * (1 - second)], [(1 - first) * second, (1 - first) * (1 - second)]])
    _equal(sum(square), 1, "cone square normalization")
    _equal(square.det(), 0, "cone square determinant")
    _equal(square[0, 0] + square[0, 1], first, "square inverse row margin")
    _equal(square[0, 0] + square[1, 0], second, "square inverse column margin")
    return {
        "rank_one_pivots": 4,
        "approach_determinants": ["0", "+t*M_t[1,1]", "-t*M_t[1,0]"],
        "cone_closure_square": "[[uv,u(1-v)],[(1-u)v,(1-u)(1-v)]]; inverse uses first row and column sums",
    }


def _audit_stratum(stratum: Stratum) -> dict[str, Any]:
    ray = stratum_witness(stratum)
    coefficients = tuple(Fraction(value) for value in LINEAR_TRANSFORM.T * sp.Matrix(ray) / 4)
    point = incidence_frame(coefficients)
    evaluated = evaluate_four_support(coefficients)
    _require(
        classify_coefficients(coefficients) == stratum and evaluated.nullity == stratum.nullity,
        "stratum rank disagrees with the exact rank evaluator",
    )
    _require(
        tuple(index for index, value in enumerate(point.factors) if value == 0) == stratum.kernel_slots,
        "global factor slots disagree with stratum slots",
    )
    frame = sp.Matrix(point.matrix)
    rank_frame = sp.Matrix(evaluated.kernel_frame)
    inverse = sp.diag(*(1 / value for value in point.gram_diagonal)) * frame.T
    recovered = inverse * rank_frame
    _require(frame * recovered == rank_frame, "global frame fails to span the independently evaluated kernel")
    _require(
        sp.diag(*point.factors) * recovered == sp.zeros(20, rank_frame.cols),
        "kernel coordinates violate factor equations",
    )
    coordinates = tuple(Fraction(index + 1) if index in stratum.kernel_slots else Fraction(0) for index in range(20))
    partner = lift_kernel_coordinates(coefficients, coordinates)
    _require(kernel_coordinates(coefficients, partner) == coordinates, "rational forward/inverse round trip")
    _require(
        sum(value * value for value in partner)
        == sum(weight * value * value for weight, value in zip(point.gram_diagonal, coordinates, strict=True)),
        "weighted partner norm identity",
    )
    return {
        "signs": stratum.signs,
        "cone_sign": stratum.cone_sign,
        "dimension": stratum.dimension,
        "nullity": stratum.nullity,
        "ray_witness": [str(value) for value in ray],
        "kernel_slots": stratum.kernel_slots,
    }


def _audit_extreme_approaches() -> list[dict[str, Any]]:
    large, small = Fraction(10**40), Fraction(1, 10**40)
    signs = (1, 1, 1, -1)
    cases = (
        (Stratum(signs, -1), (Fraction(0), large, Fraction(1), Fraction(-1))),
        (Stratum(signs, 1), (small, Fraction(1), Fraction(0), Fraction(0))),
        (Stratum(signs, 0), (small, Fraction(0), large, Fraction(0))),
        (Stratum(signs, -1), (small, Fraction(0), large, Fraction(0))),
        (Stratum(signs, 1), (small, Fraction(0), large, Fraction(0))),
    )
    records = []
    for source, target in cases:
        for parameter in (small, Fraction(1), large):
            actual = approach_ray(source, target, parameter)
            _require(classify_linear_coordinates(actual) == source, "extreme-scale approach leaves its source")
            records.append(
                {
                    "source_signs": source.signs,
                    "source_cone_sign": source.cone_sign,
                    "target_ray": [str(value) for value in target],
                    "parameter": str(parameter),
                }
            )
    unscaled = tuple(value if value else Fraction(1, 2) * sign for value, sign in zip(cases[0][1], signs, strict=True))
    _require(classify_linear_coordinates(unscaled) != cases[0][0], "missing scale-dependent step bound escapes control")
    return records


def _audit_invalid_inputs() -> int:
    invalid_calls = [
        lambda: Stratum((0, 0, 0, 0), 0),
        lambda: Stratum((1, 1, 1, 1), 0),
        lambda: Stratum((0, 1, 1, 1), 0),
        lambda: Stratum((True, 1, 1, 1), 1),
        lambda: Stratum((1, 1, 1, 1), True),
        lambda: Stratum((1, 1, 1), 1),
        lambda: incidence_frame((0, 0, 0, 0)),
        lambda: incidence_frame((1.0, 0, 0, 0)),  # type: ignore[arg-type]
        lambda: incidence_frame((sp.I, 0, 0, 0)),
        lambda: incidence_frame((sp.Symbol("a", real=True), 0, 0, 0)),
        lambda: lift_kernel_coordinates((1, 0, 0, 0), (1,) + (0,) * 19),
        lambda: kernel_coordinates((1, 0, 0, 0), (1,) + (0,) * 31),
        lambda: kernel_coordinates((1, 0, 0, 0), (0,) * 31),
        lambda: approach_ray(Stratum((1, 1, 1, 1), 1), (1, 1, 1, 1), 0),
        lambda: approach_ray(Stratum((1, 1, 1, 1), 1), (1, 1, 1, 1), 0.5),  # type: ignore[arg-type]
    ]
    positive, cone = Stratum((1, 1, 1, -1), 1), Stratum((1, 1, 1, -1), 0)
    invalid_calls.extend((lambda: coordinate_inclusion(cone, positive), lambda: approach_ray(cone, (2, 1, 1, -1), 1)))
    for call in invalid_calls:
        try:
            call()
        except ValueError:
            pass
        else:
            raise RuntimeError("invalid geometric domain or impossible incidence accepted")
    return len(invalid_calls)


def audit_four_support_geometry() -> dict[str, Any]:
    """Check finite incidence and exact frame/closure identities with falsifiers."""
    strata = enumerate_strata()
    records = parallel.ordered_map(_audit_stratum, strata, min_items=2)
    relation = {
        (source, target)
        for source in range(len(strata))
        for target in range(len(strata))
        if closure_contains(strata[source], strata[target])
    }
    approach_checks = 0
    for source_index, source in enumerate(strata):
        _require((source_index, source_index) in relation, "closure reflexivity")
        for target_index, target in enumerate(strata):
            if (source_index, target_index) not in relation:
                continue
            inclusion = sp.Matrix(coordinate_inclusion(source, target))
            _require(inclusion.shape == (target.nullity, source.nullity), "kernel inclusion shape")
            _require(
                inclusion.T * inclusion == sp.eye(source.nullity), "kernel inclusion preserves orthonormal coordinates"
            )
            if source_index != target_index:
                _require((target_index, source_index) not in relation, "closure antisymmetry")
                _require(
                    target.dimension < source.dimension and target.nullity > source.nullity,
                    "strict frontier and rank gain",
                )
            for later in range(len(strata)):
                if (target_index, later) in relation:
                    _require((source_index, later) in relation, "closure transitivity")
            ray = stratum_witness(target)
            for parameter in (Fraction(1), Fraction(1, 3), Fraction(1, 100)):
                _require(
                    classify_linear_coordinates(approach_ray(source, ray, parameter)) == source,
                    "rational closure approach",
                )
                approach_checks += 1
        records[source_index]["id"] = source_index
        records[source_index]["closure_targets"] = [
            target for target in range(len(strata)) if (source_index, target) in relation
        ]
    _require(
        Counter(stratum.dimension for stratum in strata) == {0: 8, 1: 24, 2: 40, 3: 24},
        "smooth-stratum dimension census",
    )
    _require(
        Counter(stratum.nullity for stratum in strata) == {0: 24, 4: 40, 8: 8, 12: 16, 16: 8},
        "rank-locus component census",
    )
    _require(len(relation) == 704, "closure incidence census")
    sign_flip = Stratum((-1, 1, 1, -1), -1)
    _require(not closure_contains(Stratum((1, 1, 1, -1), 1), sign_flip), "coordinate sign flip must leave the closure")
    return {
        "schema": "cayley-dickson-four-support-incidence-geometry-v1",
        "domain": "nonzero support {1,10,18,25}; normalized base uses N=1 or norm(p,q,r,s)=2",
        "qpu_executed": False,
        "sympy_version": sp.__version__,
        "stratum_count": len(strata),
        "dimension_counts": dict(sorted(Counter(stratum.dimension for stratum in strata).items())),
        "rank_locus_component_counts": dict(sorted(Counter(stratum.nullity for stratum in strata).items())),
        "closure_pairs_including_reflexive": len(relation),
        "strict_closure_pairs": len(relation) - len(strata),
        "rational_approach_checks": approach_checks,
        "extreme_scale_approaches": _audit_extreme_approaches(),
        "strata": records,
        "closure_polynomials": _audit_closure_polynomials(),
        "global_frame": _audit_polynomial_frames(),
        "global_block_order": BLOCK_NAMES,
        "global_unit_model": "Y={(x,z) in S3 x S19: Delta*z_cone=0; ell_i*z_i=0 for i=1..4}",
        "homeomorphism": "(x,z)->(x,F(x)z); inverse (x,y)->(x,F(x)^T y), for F=G*D^(-1/2)",
        "kernel_completeness_dependency": "eight-sector all-real rank theorem on the fixed support",
        "negative_controls": [
            "duplicated frame column rejected",
            "sign-damaged frame rejected",
            "reversed incidence rejected",
            "coordinate sign flip excluded",
            "origin and malformed domains rejected",
            "unscaled approach step fails its extreme target",
        ],
        "invalid_inputs_rejected": _audit_invalid_inputs(),
        "proof_scope": (
            "Analytic log-coordinate and constructive density proofs establish smoothness, connectedness and exact "
            "closure; polynomial identities certify the global incidence homeomorphism using the prior rank theorem."
        ),
        "remaining_scope": (
            "Whitney conditions, finite triangulation, homology, all 32 coefficient directions "
            "and all-dimensional classification require separate proofs."
        ),
    }


def main() -> int:
    print(json.dumps(audit_four_support_geometry(), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
