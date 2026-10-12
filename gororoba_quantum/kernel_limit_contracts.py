"""Exact replay contracts for polynomial kernel limits and pair-space attachments.

Polynomial rank witnesses and full projector identities cover the declared real
path domains. Distinct endpoint subspaces certify distinct attachment spheres
at a shared center and tangent; they leave neighborhood coverage unproved.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from dataclasses import replace
from fractions import Fraction
from functools import partial
from itertools import combinations
from typing import Any

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from cd_core import cd_sign
from four_support_rank import SUPPORT
from kernel_limits import (
    KernelLimitCertificate,
    cd_polynomial_matrix,
    certify_kernel_limit,
    extend_limiting_partner,
    verify_kernel_limit,
)

PARAMETER = sp.Symbol("t", real=True)
CENTER = sp.zeros(32, 1)
CENTER[1] = CENTER[18] = 1
EIGHT_NULLITY_DIRECTIONS = ((3, 27), (4, 11), (8, 27), (11, 24))
EIGHT_NULLITY_LABELS = ("e3+e27", "e4+e11", "e8+e27", "e11+e24")


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


def _rank(matrix: sp.MatrixBase) -> int:
    return int(DomainMatrix.from_Matrix(sp.Matrix(matrix)).to_field().rank())


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


def _certificate_record(certificate: KernelLimitCertificate) -> dict[str, object]:
    return {
        "parameter": str(certificate.parameter),
        "endpoint": str(certificate.endpoint),
        "generic_rank": certificate.generic_rank,
        "generic_nullity": certificate.generic_nullity,
        "endpoint_nullity": certificate.endpoint_nullity,
        "pivot_rows": certificate.pivot_rows,
        "pivot_columns": certificate.pivot_columns,
        "pivot_determinant": str(sp.factor(certificate.pivot_determinant)),
        "kernel_free_rows": certificate.kernel_free_rows,
        "kernel_frame": _sparse_matrix(certificate.kernel_frame),
        "exceptional_polynomial": str(sp.factor(certificate.exceptional_polynomial)),
        "punctured_radius": str(certificate.punctured_radius),
        "transport_frame": _sparse_matrix(certificate.transport_frame),
        "transport_gram": _sparse_matrix(certificate.transport_gram),
        "transport_determinant": str(sp.factor(certificate.transport_determinant)),
        "projector": _sparse_matrix(certificate.projector),
        "limit_projector": _sparse_matrix(certificate.limit_projector),
        "limiting_frame": _sparse_matrix(certificate.limiting_frame),
        "limiting_columns": certificate.limiting_columns,
        "endpoint_pivot_rows": certificate.endpoint_pivot_rows,
        "endpoint_pivot_columns": certificate.endpoint_pivot_columns,
        "endpoint_pivot_determinant": str(certificate.endpoint_pivot_determinant),
        "endpoint_free_rows": certificate.endpoint_free_rows,
        "endpoint_frame": _sparse_matrix(certificate.endpoint_frame),
        "attachment": _sparse_matrix(certificate.attachment),
    }


def _rank_domain_roots(determinant: sp.Expr) -> list[dict[str, object]]:
    intervals = sp.Poly(determinant, PARAMETER, domain=sp.QQ).intervals(eps=sp.Rational(1, 16))
    records = []
    for (lower, upper), multiplicity in intervals:
        _require(
            (lower == upper == 0) or upper <= -1 or lower >= 1,
            "rank witness vanishes inside the declared punctured real path domain",
        )
        records.append({"interval": [str(lower), str(upper)], "multiplicity": int(multiplicity)})
    return records


def _coordinates_record(coordinates: sp.MatrixBase) -> list[list[object]]:
    return [[index, str(sp.expand(value))] for index, value in enumerate(coordinates) if value != 0]


def _invalid(value: Any) -> Any:
    return value


def _alter_matrix(matrix: sp.MatrixBase) -> sp.ImmutableMatrix:
    changed = sp.Matrix(matrix)
    changed[0, 0] += 1
    return sp.ImmutableMatrix(changed)


def _reject_value_error(operation: Callable[[], object], label: str) -> str:
    try:
        operation()
    except ValueError:
        return label
    raise RuntimeError(f"invalid input accepted: {label}")


def _mutation_contracts(matrix: sp.Matrix, certificate: KernelLimitCertificate) -> list[str]:
    mutations = {
        "generic_rank": replace(certificate, generic_rank=certificate.generic_rank + 1),
        "punctured_radius": replace(certificate, punctured_radius=certificate.punctured_radius + 1),
        "transport_frame": replace(certificate, transport_frame=_alter_matrix(certificate.transport_frame)),
        "transport_gram": replace(certificate, transport_gram=_alter_matrix(certificate.transport_gram)),
        "transport_determinant": replace(certificate, transport_determinant=certificate.transport_determinant + 1),
        "pivot_determinant": replace(certificate, pivot_determinant=certificate.pivot_determinant + 1),
        "kernel_frame": replace(certificate, kernel_frame=_alter_matrix(certificate.kernel_frame)),
        "projector": replace(certificate, projector=_alter_matrix(certificate.projector)),
        "limit_projector": replace(certificate, limit_projector=_alter_matrix(certificate.limit_projector)),
        "limiting_frame": replace(certificate, limiting_frame=_alter_matrix(certificate.limiting_frame)),
        "attachment": replace(certificate, attachment=_alter_matrix(certificate.attachment)),
        "exceptional_polynomial": replace(certificate, exceptional_polynomial=certificate.exceptional_polynomial + 1),
        "endpoint_frame": replace(certificate, endpoint_frame=_alter_matrix(certificate.endpoint_frame)),
        "endpoint_pivot_determinant": replace(
            certificate, endpoint_pivot_determinant=certificate.endpoint_pivot_determinant + 1
        ),
    }
    for label, mutation in mutations.items():
        _require(not verify_kernel_limit(matrix, mutation), f"certificate mutation accepted: {label}")
    return sorted(mutations)


def _toy_contracts() -> dict[str, object]:
    parameter = PARAMETER
    fixtures = {
        "rectangular_pole_frame": (sp.Matrix([[parameter, 1, 0], [0, 0, parameter]]), 2, 2),
        "zero_rectangular_operator": (sp.zeros(2, 3), 0, 3),
        "constant_full_rank": (sp.eye(2), 2, 0),
        "full_rank_endpoint_jump": (sp.diag(parameter, parameter**2), 2, 2),
    }
    records = {}
    for label, (matrix, generic_rank, endpoint_nullity) in fixtures.items():
        certificate = certify_kernel_limit(matrix, parameter)
        _require(verify_kernel_limit(matrix, certificate), f"toy certificate fails: {label}")
        _require(
            certificate.generic_rank == generic_rank and certificate.endpoint_nullity == endpoint_nullity,
            f"toy rank differs: {label}",
        )
        records[label] = {"operator": _sparse_matrix(matrix), "certificate": _certificate_record(certificate)}
    matrix = fixtures["rectangular_pole_frame"][0]
    certificate = certify_kernel_limit(matrix, parameter)
    _require(
        any(sp.denom(value).subs(parameter, 0) == 0 for value in certificate.kernel_frame), "pole fixture loses pole"
    )
    _equal(certificate.limit_projector, sp.diag(1, 0, 0), "pole-frame projector limit")
    partner = extend_limiting_partner(certificate, (1, 0, 0))
    _equal(matrix * partner, sp.zeros(2, 1), "extended partner satisfies operator")
    _equal(partner.subs(parameter, 0), sp.Matrix([1, 0, 0]), "extended partner endpoint")
    _require(partner.dot(partner).subs(parameter, 0) == 1, "positive normalization near endpoint")
    _equal(extend_limiting_partner(certificate, (0, 0, 0)), sp.zeros(3, 1), "zero partner extension")
    rejected = [
        _reject_value_error(lambda: extend_limiting_partner(certificate, (0, 0, 1)), "endpoint_kernel_outside_limit"),
        _reject_value_error(lambda: extend_limiting_partner(certificate, _invalid((1.0, 0, 0))), "approximate_partner"),
        _reject_value_error(lambda: extend_limiting_partner(certificate, (1, 0)), "partner_dimension"),
        _reject_value_error(lambda: extend_limiting_partner(certificate, _invalid("100")), "string_partner"),
    ]
    extra_symbol = sp.Symbol("s", real=True)
    invalid_entries = (
        (sp.Float("0.1"), "approximate_operator"),
        (1 / parameter, "nonpolynomial_operator"),
        (parameter + extra_symbol, "multiple_symbols"),
        (sp.sqrt(2), "irrational_coefficient"),
    )
    for entry, label in invalid_entries:
        rejected.append(_reject_value_error(partial(certify_kernel_limit, sp.Matrix([[entry]]), parameter), label))
    rejected.extend(
        [
            _reject_value_error(lambda: certify_kernel_limit(matrix, sp.Symbol("z")), "parameter_real_assumption"),
            _reject_value_error(lambda: certify_kernel_limit(matrix, parameter, _invalid(0.0)), "approximate_endpoint"),
            _reject_value_error(lambda: certify_kernel_limit(sp.zeros(0, 3), parameter), "empty_operator"),
            _reject_value_error(lambda: cd_polynomial_matrix((1, 0, 0), parameter), "non_power_two_dimension"),
            _reject_value_error(lambda: cd_polynomial_matrix((1, 0), parameter, "middle"), "multiplication_side"),
            _reject_value_error(lambda: cd_polynomial_matrix((1, True), parameter), "boolean_coefficient"),
        ]
    )
    return {
        "fixtures": records,
        "mutations_rejected": _mutation_contracts(matrix, certificate),
        "invalid_inputs_rejected": sorted(rejected),
        "extended_partner": _sparse_matrix(partner),
    }


def _quaternion_rotation() -> tuple[sp.Matrix, dict[str, object]]:
    parameter = PARAMETER
    denominator = 1 + parameter**2
    cosine, sine = (1 - parameter**2) / denominator, 2 * parameter / denominator
    quaternion = sp.Matrix([[1, 0, 0, 0], [0, cosine, -sine, 0], [0, sine, cosine, 0], [0, 0, 0, 1]])
    conjugation = sp.diag(1, -1, -1, -1)
    _equal(quaternion.T * quaternion, sp.eye(4), "quaternion rotation is orthogonal")
    _equal(quaternion * conjugation, conjugation * quaternion, "quaternion rotation preserves conjugation")
    _equal(quaternion.det(), 1, "quaternion rotation determinant")
    _equal(quaternion[:, 0], sp.eye(4)[:, 0], "quaternion rotation fixes scalar")
    verified_products = []
    for first in range(4):
        for second in range(4):
            product = sp.Matrix(
                [
                    sum(
                        quaternion[left, first] * quaternion[right, second] * cd_sign(4, left, right)
                        for left in range(4)
                        for right in range(4)
                        if left ^ right == output
                    )
                    for output in range(4)
                ]
            )
            _equal(product, cd_sign(4, first, second) * quaternion[:, first ^ second], "quaternion product covariance")
            verified_products.append([first, second])
    transform = sp.diag(*(quaternion for _ in range(8)))
    _equal(transform.T * transform, sp.eye(32), "dimension-32 rotation is orthogonal")
    _equal(transform.det(), 1, "dimension-32 rotation determinant")
    return transform, {
        "quaternion_transform": _sparse_matrix(quaternion),
        "quaternion_basis_products": verified_products,
        "norm_preserved": True,
        "conjugation_preserved": True,
        "scalar_fixed": True,
        "dimension32_transform": "diag(B,B,B,B,B,B,B,B)",
        "extension_justification": (
            "componentwise Cayley-Dickson doubling of a unital conjugation-preserving automorphism"
        ),
    }


def _eight_nullity_paths() -> tuple[list[KernelLimitCertificate], dict[str, object]]:
    parameter = PARAMETER
    witnesses = (
        (tuple(range(24)), 256 * parameter**8 * (parameter**2 + 1) ** 4),
        ((*range(23), 24), 256 * parameter**12 * (parameter**2 + 1) ** 2),
        ((*range(20), *range(28, 32)), 4096 * parameter**8 * (parameter**2 + 1) ** 4),
        (tuple(range(24)), 4096 * parameter**8 * (parameter - 1) ** 2 * (parameter + 1) ** 2 * (parameter**2 + 1) ** 2),
    )
    certificates = []
    records = []
    transform, automorphism_record = _quaternion_rotation()
    common_derivative = sp.zeros(32, 1)
    common_derivative[2], common_derivative[17] = 2, -2
    for label, direction, (indices, determinant) in zip(
        EIGHT_NULLITY_LABELS, EIGHT_NULLITY_DIRECTIONS, witnesses, strict=True
    ):
        coordinates = CENTER.copy()
        for index in direction:
            coordinates[index] = parameter
        matrix = cd_polynomial_matrix(tuple(coordinates), parameter)
        certificate = certify_kernel_limit(matrix, parameter)
        certificates.append(certificate)
        _require(certificate.generic_nullity == 8 and certificate.endpoint_nullity == 12, "eight-nullity path ranks")
        _equal(matrix.extract(indices, indices).det(method="domain-ge"), determinant, "declared real-domain rank minor")
        denominator = 1 + parameter**2
        rotated_coordinates = (denominator * transform * coordinates.subs(parameter, parameter**2)).applyfunc(sp.cancel)
        rotated_matrix = cd_polynomial_matrix(tuple(rotated_coordinates), parameter)
        _equal(
            rotated_matrix,
            denominator * transform * matrix.subs(parameter, parameter**2) * transform.T,
            "direct dimension-32 operator covariance",
        )
        _equal(rotated_coordinates.subs(parameter, 0), CENTER, "rotated endpoint")
        _equal(rotated_coordinates.diff(parameter).subs(parameter, 0), common_derivative, "shared nonzero derivative")
        projector = (transform * certificate.projector.subs(parameter, parameter**2) * transform.T).applyfunc(sp.cancel)
        _equal(rotated_matrix * projector, sp.zeros(32), "rotated projector annihilation")
        _equal(projector.T, projector, "rotated projector symmetry")
        _equal(projector * projector, projector, "rotated projector idempotence")
        _equal(projector.trace(), 8, "rotated projector dimension")
        _equal(projector.subs(parameter, 0), certificate.limit_projector, "rotated projector limit")
        norm_squared = sp.factor(rotated_coordinates.dot(rotated_coordinates))
        _equal(norm_squared, 2 * (1 + parameter**2) ** 2 * (1 + parameter**4), "rotated positive norm polynomial")
        _equal(sp.diff(norm_squared, parameter).subs(parameter, 0), 0, "normalization preserves derivative")
        records.append(
            {
                "direction": label,
                "coordinates": _coordinates_record(coordinates),
                "domain": "0 < abs(t) < 1",
                "certificate": _certificate_record(certificate),
                "independent_real_rank_minor": {
                    "rows_and_columns": indices,
                    "determinant": str(sp.factor(determinant)),
                    "complete_real_root_isolation": _rank_domain_roots(determinant),
                },
                "same_derivative_path": {
                    "polynomial_coordinates": _coordinates_record(rotated_coordinates),
                    "norm_squared": str(norm_squared),
                    "sphere_normalization": "sqrt(2 / norm_squared)",
                    "derivative": _coordinates_record(common_derivative),
                    "rank_transport_factor": str(denominator),
                    "rank_transport_transform_determinant": "1",
                    "projector": _sparse_matrix(projector),
                    "limit_equals_base_path": True,
                },
            }
        )
    intersections = []
    for first, second in combinations(range(4), 2):
        first_frame, second_frame = certificates[first].limiting_frame, certificates[second].limiting_frame
        intersection = 16 - _rank(first_frame.row_join(second_frame))
        _require(intersection == 4, "eight-nullity pair intersection dimension")
        _require(certificates[first].limit_projector != certificates[second].limit_projector, "distinct limit planes")
        intersections.append(
            {"first": EIGHT_NULLITY_LABELS[first], "second": EIGHT_NULLITY_LABELS[second], "dimension": intersection}
        )
    overlap_trace = sp.trace(certificates[0].limit_projector * certificates[1].limit_projector)
    _equal(overlap_trace, sp.Rational(9, 2), "A/B principal-angle overlap trace")
    return certificates, {
        "paths": records,
        "pairwise_intersections": intersections,
        "first_second_projector_product_trace": str(overlap_trace),
        "automorphism": automorphism_record,
        "attachment_sphere_dimension": 7,
        "endpoint_sphere_dimension": 11,
        "shared_normalized_derivative": _coordinates_record(common_derivative),
    }


def _four_support_paths() -> dict[str, object]:
    parameter = PARAMETER
    half_square, half_cube = parameter**2 / 2, parameter**3 / 2
    fixtures = (
        (
            "first_linear_component",
            (1 + half_square, parameter + half_square, 1 - half_square, -parameter + half_square),
        ),
        (
            "second_linear_component",
            (1 - half_square, parameter + half_square, 1 + half_square, -parameter + half_square),
        ),
        ("quadratic_component", (1 - half_cube, parameter + half_square, 1 + half_cube, -parameter + half_square)),
    )
    certificates = []
    records = []
    derivative = sp.zeros(32, 1)
    derivative[10], derivative[25] = 1, -1
    for label, values in fixtures:
        coordinates = sp.zeros(32, 1)
        for index, value in zip(SUPPORT, values, strict=True):
            coordinates[index] = value
        matrix = cd_polynomial_matrix(tuple(coordinates), parameter)
        certificate = certify_kernel_limit(matrix, parameter)
        _require(certificate.generic_nullity == 4 and certificate.endpoint_nullity == 12, "four-support path ranks")
        _equal(coordinates.subs(parameter, 0), CENTER, "four-support endpoint")
        _equal(coordinates.diff(parameter).subs(parameter, 0), derivative, "four-support shared derivative")
        norm_squared = sp.factor(coordinates.dot(coordinates))
        _equal(sp.diff(norm_squared, parameter).subs(parameter, 0), 0, "four-support normalized derivative")
        _require(norm_squared.subs(parameter, 0) == 2, "four-support endpoint norm")
        certificates.append(certificate)
        a, b, c, d = values
        forms = (a - b - c - d, a - b + c + d, a + b - c + d, a + b + c - d)
        quadric = a * a + b * b - c * c - d * d
        records.append(
            {
                "family": label,
                "coordinates": _coordinates_record(coordinates),
                "domain": "0 < abs(t) < 1",
                "complete_real_rank_minor_root_isolation": _rank_domain_roots(certificate.pivot_determinant),
                "linear_forms": [str(sp.factor(value)) for value in forms],
                "quadric": str(sp.factor(quadric)),
                "norm_squared": str(norm_squared),
                "sphere_normalization": "sqrt(2 / norm_squared)",
                "certificate": _certificate_record(certificate),
            }
        )
    intersections = []
    for first, second in combinations(range(3), 2):
        _equal(
            certificates[first].limit_projector * certificates[second].limit_projector,
            sp.zeros(32),
            "orthogonal limit planes",
        )
        intersection = 8 - _rank(certificates[first].limiting_frame.row_join(certificates[second].limiting_frame))
        _require(intersection == 0, "four-support limit-plane intersection")
        intersections.append({"first": fixtures[first][0], "second": fixtures[second][0], "dimension": intersection})
    endpoint_frame = sp.Matrix(certificates[0].endpoint_frame)
    endpoint_projector = (endpoint_frame * (endpoint_frame.T * endpoint_frame).inv() * endpoint_frame.T).applyfunc(
        sp.cancel
    )
    _equal(
        sum((certificate.limit_projector for certificate in certificates), sp.zeros(32)),
        endpoint_projector,
        "endpoint kernel orthogonal decomposition",
    )
    return {
        "paths": records,
        "pairwise_intersections": intersections,
        "sum_equals_endpoint_kernel_projector": True,
        "shared_normalized_derivative": _coordinates_record(derivative),
        "attachment_sphere_dimension": 3,
        "endpoint_sphere_dimension": 11,
    }


def _cd_side_contracts() -> dict[str, object]:
    values: Sequence[int | Fraction | sp.Expr] = (1, PARAMETER, Fraction(1, 2), -(PARAMETER**2))
    left = cd_polynomial_matrix(values, PARAMETER, "left")
    right = cd_polynomial_matrix(values, PARAMETER, "right")
    for first in range(4):
        for second in range(4):
            _equal(
                left[first ^ second, second],
                values[first] * cd_sign(4, first, second),
                "left multiplication orientation",
            )
            _equal(
                right[first ^ second, second],
                values[first] * cd_sign(4, second, first),
                "right multiplication orientation",
            )
    return {"dimension": 4, "basis_product_checks_per_side": 16}


def audit_kernel_limits() -> dict[str, object]:
    """Replay exact rank, projector, real-domain and attachment witnesses."""
    toy_records = _toy_contracts()
    _, eight_nullity_records = _eight_nullity_paths()
    return {
        "parameter_field": "Q(t)",
        "endpoint": "0",
        "arbitrary_polynomial_path_algorithm": "generic rank and removable orthogonal projector limit",
        "arbitrary_path_scope": "finite polynomial matrices of arbitrary rectangular size over Q[t]",
        "cayley_dickson_sides": _cd_side_contracts(),
        "toy_contracts": toy_records,
        "dimension32_eight_nullity_attachments": eight_nullity_records,
        "dimension32_four_support_attachments": _four_support_paths(),
        "proved_attachment_interpretation": (
            "The closure fiber along each punctured path equals its limiting-kernel unit sphere."
        ),
        "remaining_obligations": [
            "Cover arbitrary real-coefficient rank loci and their local smooth strata.",
            "Classify all path limits and neighborhood incidence at every singular center.",
            "Construct a global topological model and calculate its integral invariants.",
            "Prove an unrestricted all-dimensional classification.",
            "Translate retained exact identities into Rocq after the authorized run-result milestone.",
        ],
    }


def main() -> int:
    print(json.dumps(audit_kernel_limits(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
