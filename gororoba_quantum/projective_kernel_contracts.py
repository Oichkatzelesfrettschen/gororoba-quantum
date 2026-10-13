"""Exact projective-limit controls independent of kernel-frame saturation."""

from __future__ import annotations

import json
from dataclasses import replace
from fractions import Fraction
from typing import Any

import sympy as sp

from complex_skew import kernel_to_real, pfaffian
from kernel_limits import cd_polynomial_matrix, certify_kernel_limit
from projective_kernel_limits import (
    KernelDivision,
    cd_skew_path,
    certify_projective_limit,
    leading_plucker_coordinates,
    verify_projective_limit,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def equal(first: sp.MatrixBase, second: sp.MatrixBase) -> bool:
    return first.shape == second.shape and (first - second).applyfunc(sp.cancel).is_zero_matrix is True


def projector(frame: sp.MatrixBase) -> sp.Matrix:
    return (frame * (frame.H * frame).inv() * frame.H).applyfunc(sp.cancel) if frame.cols else sp.zeros(frame.rows)


def changing_chart(parameter: sp.Symbol) -> sp.Matrix:
    pivot = sp.Matrix([[0, parameter**3], [-(parameter**3), 0]])
    cross = sp.Matrix([[1, 1], [0, parameter**3]])
    return pivot.row_join(cross).col_join((-cross.T).row_join(-cross.T * pivot.inv() * cross))


def coordinate_control(matrix: sp.Matrix, parameter: sp.Symbol, endpoint: Fraction = Fraction(0)) -> dict[str, Any]:
    certificate = certify_projective_limit(matrix, parameter, endpoint)
    require(verify_projective_limit(matrix, certificate), "projective certificate fails")
    coordinates = dict(leading_plucker_coordinates(matrix, certificate))
    shifted = sp.Symbol("u", real=True)
    for free, coefficient in coordinates.items():
        pivot = tuple(index for index in range(matrix.rows) if index not in free)
        sign = (-1) ** sum(index - position for position, index in enumerate(pivot))
        polynomial = sp.Poly(sign * pfaffian(matrix.extract(pivot, pivot)).subs(parameter, shifted + endpoint), shifted)
        require(all(polynomial.nth(order) == 0 for order in range(certificate.vanishing_order)), "missed earlier term")
        require(sp.cancel(polynomial.nth(certificate.vanishing_order) - coefficient) == 0, "leading minor differs")
    require(any(value != 0 for value in coordinates.values()), "projective endpoint vanishes")
    return {
        "complex_size": matrix.rows,
        "generic_rank": certificate.generic_rank,
        "divisions": len(certificate.divisions),
        "initial_minor_order": certificate.initial_minor_order,
        "pfaffian_order": certificate.vanishing_order,
        "punctured_radius": str(certificate.punctured_radius),
        "leading_coordinates": [[list(key), str(value)] for key, value in coordinates.items()],
    }


def audit() -> dict[str, Any]:
    parameter = sp.Symbol("t", real=True)
    matrix = changing_chart(parameter)
    certificate = certify_projective_limit(matrix, parameter)
    require(len(certificate.divisions) == 3, "three-order chart singularity loses its division controls")
    require(certificate.vanishing_order == 0, "chart singularity becomes an operator rank drop")
    fixtures = {
        "singular_chart_constant_rank": coordinate_control(matrix, parameter),
        "complex_rank_drop": coordinate_control((1 + sp.I) * parameter**2 * matrix, parameter),
        "shifted_endpoint": coordinate_control(
            matrix.subs(parameter, parameter - sp.Rational(3, 2)), parameter, Fraction(3, 2)
        ),
        "zero_operator": coordinate_control(sp.zeros(4), parameter),
        "empty_kernel": coordinate_control(sp.Matrix([[0, parameter], [-parameter, 0]]), parameter),
        "odd_ambient": coordinate_control(sp.Matrix([[0, parameter, 1], [-parameter, 0, 0], [-1, 0, 0]]), parameter),
    }
    mutations = {
        "rank": replace(certificate, generic_rank=certificate.generic_rank + 1),
        "initial_rows": replace(certificate, initial_rows=(0, 0)),
        "initial_order": replace(certificate, initial_minor_order=certificate.initial_minor_order + 1),
        "division_pivot": replace(
            certificate,
            divisions=(KernelDivision(-1, certificate.divisions[0].coefficients), *certificate.divisions[1:]),
        ),
        "division_coefficients": replace(
            certificate, divisions=(KernelDivision(0, (sp.Integer(1), sp.Integer(0))), *certificate.divisions[1:])
        ),
        "regular_frame": replace(
            certificate, regular_frame=sp.ImmutableMatrix(sp.zeros(*certificate.regular_frame.shape))
        ),
        "free_rows": replace(certificate, free_rows=(0, 0)),
        "pivot_pfaffian": replace(certificate, pivot_pfaffian=certificate.pivot_pfaffian + 1),
        "admission": replace(certificate, admission_polynomial=certificate.admission_polynomial + 1),
        "endpoint": replace(certificate, endpoint=Fraction(1)),
        "seed": replace(certificate, seed_frame=sp.ImmutableMatrix(sp.zeros(*certificate.seed_frame.shape))),
        "divisions": replace(certificate, divisions=certificate.divisions[:-1]),
        "order": replace(certificate, vanishing_order=certificate.vanishing_order + 1),
        "factor": replace(certificate, leading_factor=certificate.leading_factor + 1),
        "limit": replace(certificate, limit_frame=sp.ImmutableMatrix(sp.zeros(*certificate.limit_frame.shape))),
        "radius": replace(certificate, punctured_radius=certificate.punctured_radius * 2),
    }
    for label, mutation in mutations.items():
        require(not verify_projective_limit(matrix, mutation), f"certificate mutation accepted: {label}")
    invalid = [
        sp.zeros(0),
        sp.zeros(2, 3),
        sp.Matrix([[0, sp.sqrt(2)], [-sp.sqrt(2), 0]]),
        sp.Matrix([[0, sp.Symbol("s")], [-sp.Symbol("s"), 0]]),
        sp.eye(2),
        sp.Matrix([[0, 1 / parameter], [-1 / parameter, 0]]),
        sp.Matrix([[0, sp.Float(1)], [-sp.Float(1), 0]]),
    ]
    for value in invalid:
        try:
            certify_projective_limit(value, parameter)
        except ValueError:
            continue
        raise RuntimeError("invalid polynomial skew input accepted")
    symbolic_zero = (parameter + 1) ** 2 - parameter**2 - 2 * parameter - 1
    require(
        equal(cd_skew_path((symbolic_zero, 1, 0, parameter), parameter), cd_skew_path((0, 1, 0, parameter), parameter)),
        "equivalent zero scalar coefficients differ",
    )
    change = sp.eye(4)
    change[0, 3] = 1 + sp.I + parameter
    congruent = change.T * matrix * change
    transported = certify_projective_limit(congruent, parameter)
    expected_frame = change.subs(parameter, 0).inv() * certificate.limit_frame
    require(equal(projector(transported.limit_frame), projector(expected_frame)), "complex congruence transport fails")
    repeated = certify_projective_limit((parameter**2 * matrix).subs(parameter, parameter**2), parameter)
    require(repeated.vanishing_order == 4 and len(repeated.divisions) == 6, "reparametrization loses orders")
    require(
        equal(projector(repeated.limit_frame), projector(certificate.limit_frame)),
        "reparametrization changes limit plane",
    )
    dimension32 = []
    for direction in ((3, 27), (4, 11), (8, 27), (11, 24)):
        coefficients: list[sp.Expr] = [sp.Integer(0)] * 32
        coefficients[1] = coefficients[18] = sp.Integer(1)
        for index in direction:
            coefficients[index] = parameter
        skew = cd_skew_path(coefficients, parameter)
        projective = certify_projective_limit(skew, parameter)
        real_frame = kernel_to_real(projective.limit_frame)
        baseline = certify_kernel_limit(cd_polynomial_matrix(coefficients, parameter), parameter)
        require(equal(projector(real_frame), baseline.limit_projector), "independent real limit differs")
        require(real_frame.cols == 8 and baseline.endpoint_nullity == 12, "dimension-32 ranks differ")
        dimension32.append(
            {
                "direction": list(direction),
                "real_nullity": real_frame.cols,
                "endpoint_nullity": baseline.endpoint_nullity,
                "pfaffian_order": projective.vanishing_order,
                "divisions": len(projective.divisions),
                "projector_equal": True,
            }
        )
    orthogonal_limits = []
    support = (1, 10, 18, 25)
    half_square, half_cube = parameter**2 / 2, parameter**3 / 2
    for values in (
        (1 + half_square, parameter + half_square, 1 - half_square, -parameter + half_square),
        (1 - half_square, parameter + half_square, 1 + half_square, -parameter + half_square),
        (1 - half_cube, parameter + half_square, 1 + half_cube, -parameter + half_square),
    ):
        coefficients = [sp.Integer(0)] * 32
        for index, value in zip(support, values, strict=True):
            coefficients[index] = value
        skew = cd_skew_path(coefficients, parameter)
        projective = certify_projective_limit(skew, parameter)
        real_limit = projector(kernel_to_real(projective.limit_frame))
        baseline = certify_kernel_limit(cd_polynomial_matrix(coefficients, parameter), parameter)
        require(equal(real_limit, baseline.limit_projector), "nullity-four projective limit differs")
        orthogonal_limits.append(real_limit)
    for first in range(3):
        for second in range(first):
            require(
                equal(orthogonal_limits[first] * orthogonal_limits[second], sp.zeros(32)),
                "distinct limit planes overlap",
            )
    endpoint_coefficients = [sp.Integer(0)] * 32
    endpoint_coefficients[1] = endpoint_coefficients[18] = sp.Integer(1)
    endpoint_certificate = certify_projective_limit(cd_skew_path(endpoint_coefficients, parameter), parameter)
    require(
        equal(sum(orthogonal_limits, sp.zeros(32)), projector(kernel_to_real(endpoint_certificate.limit_frame))),
        "three projective limits fail to exhaust the endpoint kernel",
    )
    doubled_coefficients = [sp.Integer(0)] * 64
    doubled_coefficients[1] = doubled_coefficients[18] = sp.Integer(1)
    doubled_coefficients[3] = doubled_coefficients[27] = parameter
    doubled = certify_projective_limit(cd_skew_path(doubled_coefficients, parameter), parameter)
    doubled_baseline = certify_kernel_limit(cd_polynomial_matrix(doubled_coefficients, parameter), parameter)
    require(
        equal(projector(kernel_to_real(doubled.limit_frame)), doubled_baseline.limit_projector),
        "dimension-64 ordinary embedding limit differs",
    )
    return {
        "schema": "projective-kernel-limits-v1",
        "congruence_and_reparametrization": {
            "complex_congruence": True,
            "reparametrized_pfaffian_order": repeated.vanishing_order,
            "reparametrized_divisions": len(repeated.divisions),
        },
        "nullity_four_limits": {"orthogonal_planes": 3, "sum_equals_endpoint_kernel": True},
        "dimension64": {
            "real_nullity": 2 * doubled.limit_frame.cols,
            "endpoint_nullity": doubled_baseline.endpoint_nullity,
            "projector_equal": True,
        },
        "fixtures": fixtures,
        "dimension32": dimension32,
        "rejected_certificates": sorted(mutations),
        "rejected_inputs": len(invalid),
        "physical_qpu_jobs": 0,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
