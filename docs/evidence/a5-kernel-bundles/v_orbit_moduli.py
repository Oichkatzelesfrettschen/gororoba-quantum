"""Exact compact-orbit classification of the open nullity-twelve piece ``V``.

In original complex coordinates, ``V`` consists of collinear seven-vector
blocks ``v=lambda*u`` satisfying the quadric equation.  This replay checks the
projective ratio and normalized Gram discriminant, the compact tangent ranks,
and the stabilizer Lie algebras at principal and collinear points.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import aligned_orbit_moduli as aligned  # noqa: E402
import kernel_symmetry as symmetry  # noqa: E402
import stabilizer_representation as stabilizer  # noqa: E402

DIMENSION = 32
KERNEL_SYMMETRY_RESULT = HERE / "result.json"
KERNEL_SYMMETRY_SCRIPT = HERE / "kernel_symmetry.py"
ALIGNED_MODULI_RESULT = HERE / "aligned-orbit-moduli-result.json"
ALIGNED_MODULI_SCRIPT = HERE / "aligned_orbit_moduli.py"

RationalMatrix = symmetry.RationalMatrix
ComplexRational = tuple[Fraction, Fraction]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _complex_add(first: ComplexRational, second: ComplexRational) -> ComplexRational:
    return first[0] + second[0], first[1] + second[1]


def _complex_multiply(first: ComplexRational, second: ComplexRational) -> ComplexRational:
    return first[0] * second[0] - first[1] * second[1], first[0] * second[1] + first[1] * second[0]


def _complex_conjugate(value: ComplexRational) -> ComplexRational:
    return value[0], -value[1]


def _complex_scale(value: ComplexRational, scalar: Fraction) -> ComplexRational:
    return scalar * value[0], scalar * value[1]


def _complex_scale_by_i(value: ComplexRational, sign: int) -> ComplexRational:
    if sign not in (-1, 1):
        raise ValueError("complex i multiplier must have sign +1 or -1")
    return -sign * value[1], sign * value[0]


def _complex_divide(numerator: ComplexRational, denominator: ComplexRational) -> ComplexRational:
    norm_squared = _complex_norm_squared(denominator)
    if norm_squared == 0:
        raise ZeroDivisionError("complex denominator is zero")
    product = _complex_multiply(numerator, _complex_conjugate(denominator))
    return product[0] / norm_squared, product[1] / norm_squared


def _complex_norm_squared(value: ComplexRational) -> Fraction:
    return value[0] * value[0] + value[1] * value[1]


def _complex_sum(values: Sequence[ComplexRational]) -> ComplexRational:
    return sum((value[0] for value in values), Fraction(0)), sum((value[1] for value in values), Fraction(0))


def _complex_dot(first: Sequence[ComplexRational], second: Sequence[ComplexRational]) -> ComplexRational:
    return _complex_sum([_complex_multiply(left, right) for left, right in zip(first, second, strict=True)])


def _hermitian_norm(values: Sequence[ComplexRational]) -> Fraction:
    return sum((_complex_norm_squared(value) for value in values), Fraction(0))


def _rational_square_root(value: Fraction) -> Fraction:
    if value < 0:
        raise ValueError("rational square root needs a nonnegative value")
    numerator_root = math.isqrt(value.numerator)
    denominator_root = math.isqrt(value.denominator)
    _require(
        numerator_root * numerator_root == value.numerator and denominator_root * denominator_root == value.denominator,
        f"{value} is not a rational square",
    )
    return Fraction(numerator_root, denominator_root)


def _complex_coordinates(point: Sequence[Fraction]) -> tuple[ComplexRational, ...]:
    _require(len(point) == DIMENSION, "A_5 point must have 32 real coordinates")
    return tuple((Fraction(point[index]), Fraction(point[16 + index])) for index in range(1, 16))


def _v_point(
    alpha: int,
    beta: int,
    split_mu: int,
    real_length: Fraction,
    imaginary_length: Fraction,
    mutation: str = "",
) -> tuple[Fraction, ...]:
    """Build ``z=(alpha*a,i*m,i*beta*a)`` with ``a=x e_1+i y e_2``."""
    if mutation not in ("", "drop_i_on_v"):
        raise ValueError(f"unknown point mutation {mutation!r}")
    common = [(Fraction(0), Fraction(0)) for _ in range(7)]
    common[0] = (real_length, Fraction(0))
    common[1] = (Fraction(0), imaginary_length)
    lower = [_complex_scale(value, Fraction(alpha)) for value in common]
    if mutation == "drop_i_on_v":
        upper = [_complex_scale(value, Fraction(beta)) for value in common]
    else:
        upper = [_complex_scale_by_i(_complex_scale(value, Fraction(beta)), 1) for value in common]
    coordinates = [*lower, (Fraction(0), Fraction(split_mu)), *upper]
    point = [Fraction(0)] * DIMENSION
    for index, value in enumerate(coordinates, start=1):
        point[index] = value[0]
        point[16 + index] = value[1]
    return tuple(point)


def _format_complex(value: ComplexRational) -> str:
    return f"{value[0]}+({value[1]})i"


def _extract_invariants(point: Sequence[Fraction]) -> dict[str, Any]:
    coordinates = _complex_coordinates(point)
    lower = coordinates[:7]
    middle = coordinates[7]
    upper = coordinates[8:]
    rotated_upper = [_complex_scale_by_i(value, -1) for value in upper]
    lower_nonzero = any(value != (Fraction(0), Fraction(0)) for value in lower)
    if lower_nonzero:
        pivot = next(index for index, value in enumerate(lower) if value != (Fraction(0), Fraction(0)))
        split_ratio = _complex_divide(rotated_upper[pivot], lower[pivot])
        collinear = all(rotated_upper[index] == _complex_multiply(split_ratio, lower[index]) for index in range(7))
        common = list(lower)
        original_lambda: ComplexRational | None = _complex_scale_by_i(split_ratio, 1)
        projective_ratio = _format_complex(split_ratio)
        affine_chart = "v=lambda*u"
    else:
        collinear = any(value != (Fraction(0), Fraction(0)) for value in rotated_upper)
        common = rotated_upper
        original_lambda = None
        projective_ratio = "infinity"
        affine_chart = "u=kappa*v at kappa=0"
    bilinear_square = _complex_dot(common, common)
    hermitian_norm = _hermitian_norm(common)
    _require(hermitian_norm > 0, "the common complex line vector must be nonzero")
    bilinear_norm_squared = _complex_norm_squared(bilinear_square)
    rho_squared = bilinear_norm_squared / (hermitian_norm * hermitian_norm)
    lower_square = _complex_dot(lower, lower)
    upper_square = _complex_dot(upper, upper)
    quadric = _complex_add(_complex_add(lower_square, _complex_multiply(middle, middle)), upper_square)
    excluded_ratio = original_lambda in ((Fraction(0), Fraction(1)), (Fraction(0), Fraction(-1)))
    inside_open_v = (
        collinear
        and bilinear_square != (Fraction(0), Fraction(0))
        and middle != (Fraction(0), Fraction(0))
        and quadric == (Fraction(0), Fraction(0))
        and not excluded_ratio
    )

    rho = _rational_square_root(rho_squared)
    total_norm = _hermitian_norm(coordinates)
    if original_lambda is None:
        affine_parameter: ComplexRational = (Fraction(0), Fraction(0))
    else:
        affine_parameter = original_lambda
    one_plus_square = _complex_add((Fraction(1), Fraction(0)), _complex_multiply(affine_parameter, affine_parameter))
    normalization_factor = (
        Fraction(1)
        + _complex_norm_squared(affine_parameter)
        + rho * _rational_square_root(_complex_norm_squared(one_plus_square))
    )
    normalization_identity = total_norm == hermitian_norm * normalization_factor
    return {
        "affine_chart": affine_chart,
        "split_projective_ratio_beta_over_alpha": projective_ratio,
        "original_lambda": "infinity" if original_lambda is None else _format_complex(original_lambda),
        "collinear_blocks": collinear,
        "quadric_value": [str(value) for value in quadric],
        "common_bilinear_square": [str(value) for value in bilinear_square],
        "common_hermitian_norm": str(hermitian_norm),
        "rho_squared": str(rho_squared),
        "mu_nonzero": middle != (Fraction(0), Fraction(0)),
        "lambda_avoids_plus_minus_i": not excluded_ratio,
        "inside_open_V": inside_open_v,
        "unit_normalization_identity_before_rescaling": normalization_identity,
    }


def _rho_stationary(
    common: Sequence[ComplexRational],
    common_derivative: Sequence[ComplexRational],
) -> bool:
    bilinear = _complex_dot(common, common)
    bilinear_derivative = _complex_scale(_complex_dot(common, common_derivative), Fraction(2))
    hermitian = _hermitian_norm(common)
    hermitian_derivative = Fraction(2) * sum(
        (
            _complex_multiply(_complex_conjugate(value), derivative)[0]
            for value, derivative in zip(common, common_derivative, strict=True)
        ),
        Fraction(0),
    )
    numerator = _complex_norm_squared(bilinear)
    numerator_derivative = Fraction(2) * _complex_multiply(_complex_conjugate(bilinear), bilinear_derivative)[0]
    return numerator_derivative * hermitian - Fraction(2) * numerator * hermitian_derivative == 0


def _invariants_stationary(point: Sequence[Fraction]) -> bool:
    invariants = _extract_invariants(point)
    coordinates = _complex_coordinates(point)
    lower = coordinates[:7]
    upper = coordinates[8:]
    original_lambda = invariants["original_lambda"]
    compact = stabilizer._compact_triples()
    for _name, triple in compact:
        tangent = stabilizer._matrix_vector(triple[0], point)
        tangent_coordinates = _complex_coordinates(tangent)
        lower_derivative = tangent_coordinates[:7]
        upper_derivative = tangent_coordinates[8:]
        if original_lambda == "infinity":
            if any(value != (Fraction(0), Fraction(0)) for value in lower_derivative):
                return False
            common = upper
            common_derivative = upper_derivative
        else:
            pivot = next(index for index, value in enumerate(lower) if value != (Fraction(0), Fraction(0)))
            lambda_value = _complex_divide(upper[pivot], lower[pivot])
            if any(
                upper_derivative[index] != _complex_multiply(lambda_value, lower_derivative[index])
                for index in range(7)
            ):
                return False
            common = lower
            common_derivative = lower_derivative
        if not _rho_stationary(common, common_derivative):
            return False
    return True


def _fixture_task(task: tuple[int, int, int, Fraction, Fraction, str, str]) -> dict[str, Any]:
    alpha, beta, split_mu, real_length, imaginary_length, orbit_type, mutation = task
    point_mutation = mutation if mutation == "drop_i_on_v" else ""
    point = _v_point(alpha, beta, split_mu, real_length, imaginary_length, point_mutation)
    invariants = _extract_invariants(point)
    if mutation == "drop_i_on_v":
        return {
            "mutation": mutation,
            "inside_open_V": invariants["inside_open_V"],
            "quadric_value": invariants["quadric_value"],
            "pass": invariants["inside_open_V"],
        }

    stabilizer_mutation = mutation if mutation == "delete_phase_generator" else ""
    tangent_rank, stabilizer_bases, coefficient_rows = aligned._stabilizer_data(point, stabilizer_mutation)
    derived_bases = aligned._derived_basis(stabilizer_bases)
    center_dimension = aligned._center_dimension(stabilizer_bases)
    killing = stabilizer._killing_matrix(derived_bases)
    compact_semisimple = aligned._negative_definite(killing)
    stabilizer_dimension = len(coefficient_rows)
    lie_algebra = aligned._lie_algebra_label(
        stabilizer_dimension,
        center_dimension,
        len(derived_bases),
        compact_semisimple,
    )
    nullity = symmetry.equations.nullity(point)
    expected_tangent_rank = 7 if orbit_type == "collinear_endpoint" else 12
    expected_stabilizer = "su(3)" if orbit_type == "collinear_endpoint" else "su(2)"
    row_pass = (
        mutation == ""
        and invariants["inside_open_V"]
        and invariants["unit_normalization_identity_before_rescaling"]
        and _invariants_stationary(point)
        and tangent_rank == expected_tangent_rank
        and lie_algebra == expected_stabilizer
        and nullity == 12
    )
    return {
        "mutation": mutation,
        "orbit_type": orbit_type,
        "split_projective_coefficients": [alpha, beta],
        "split_mu": split_mu,
        "canonical_common_vector": f"({real_length})e_1+i*({imaginary_length})e_2",
        **invariants,
        "compact_generator_count": 14 if mutation == "delete_phase_generator" else 15,
        "compact_invariants_stationary": _invariants_stationary(point),
        "compact_tangent_rank": tangent_rank,
        "stabilizer_dimension": stabilizer_dimension,
        "stabilizer_center_dimension": center_dimension,
        "stabilizer_derived_dimension": len(derived_bases),
        "derived_killing_negative_definite": compact_semisimple,
        "stabilizer_lie_algebra": lie_algebra,
        "left_nullity": nullity,
        "pass": row_pass,
    }


def _load_inputs() -> dict[str, str]:
    bindings = (
        ("kernel_symmetry", KERNEL_SYMMETRY_RESULT, KERNEL_SYMMETRY_SCRIPT, "a5-kernel-symmetry-v3"),
        (
            "aligned_orbit_moduli",
            ALIGNED_MODULI_RESULT,
            ALIGNED_MODULI_SCRIPT,
            "a5-aligned-nullity-twelve-orbit-moduli-v1",
        ),
    )
    digests: dict[str, str] = {}
    for label, result_path, script_path, schema in bindings:
        result = json.loads(result_path.read_text(encoding="utf-8"))
        script_digest = hashlib.sha256(script_path.read_bytes()).hexdigest()
        _require(result.get("schema") == schema, f"{result_path.name} has an unexpected schema")
        _require(result.get("pass") is True, f"{result_path.name} does not pass")
        _require(result.get("script_sha256") == script_digest, f"{result_path.name} is stale against its producer")
        digests[f"{label}_result_sha256"] = hashlib.sha256(result_path.read_bytes()).hexdigest()
        digests[f"{label}_script_sha256"] = script_digest
    return digests


def orbit_moduli_checks(mutation: str = "") -> dict[str, Any]:
    if mutation not in ("", "delete_phase_generator", "drop_i_on_v"):
        raise ValueError(f"unknown mutation {mutation!r}")
    input_digests = _load_inputs()
    if mutation:
        rows = [_fixture_task((3, 5, 4, Fraction(3, 4), Fraction(5, 4), "principal", mutation))]
        return {
            "mutation": mutation,
            "input_digests": input_digests,
            "rows": rows,
            "pass": all(row["pass"] for row in rows),
        }

    coefficient_fixtures = ((3, 5, 4), (5, 13, 12), (0, 1, 1))
    gram_fixtures = (
        (Fraction(0), Fraction(1), "collinear_endpoint"),
        (Fraction(3, 4), Fraction(5, 4), "principal"),
        (Fraction(4, 3), Fraction(5, 3), "principal"),
    )
    tasks = [
        (alpha, beta, split_mu, real_length, imaginary_length, orbit_type, "")
        for alpha, beta, split_mu in coefficient_fixtures
        for real_length, imaginary_length, orbit_type in gram_fixtures
    ]
    rows = symmetry.parallel.ordered_map(_fixture_task, tasks, min_items=1)
    principal_rows = [row for row in rows if row["orbit_type"] == "principal"]
    endpoint_rows = [row for row in rows if row["orbit_type"] == "collinear_endpoint"]
    projective_independence = all(
        row["compact_tangent_rank"] == 12 and row["stabilizer_lie_algebra"] == "su(2)" for row in principal_rows
    ) and all(row["compact_tangent_rank"] == 7 and row["stabilizer_lie_algebra"] == "su(3)" for row in endpoint_rows)
    return {
        "mutation": mutation,
        "input_digests": input_digests,
        "original_coordinate_parameterization": ("v=lambda*u, mu^2=-(1+lambda^2)(u dot u), u dot u!=0, mu!=0"),
        "complete_compact_invariants": [
            "lambda in CP^1 minus {+i,-i}",
            "rho=abs(u dot u)/(u^* dot u) in (0,1]",
        ],
        "compact_orbit_space": "(CP^1 minus {+i,-i}) x (0,1]",
        "compact_orbit_space_topology": {
            "homotopy_type": "C^*",
            "fundamental_group": "Z",
            "integral_cohomology": {"0": "Z", "1": "Z"},
        },
        "completeness_argument": (
            "the unit norm and quadric determine the common-line Hermitian norm from (lambda,rho); after matching mu "
            "by the global phase, the common vectors have identical real Gram matrices and G_2 transitivity on ordered "
            "two-frames (or unit vectors at rho=1) maps one point to the other"
        ),
        "principal_orbits": "0<rho<1, dimension 12, stabilizer SU(2)",
        "collinear_endpoint_orbits": "rho=1, dimension 7, stabilizer Lie algebra su(3)",
        "recorded_representative_scope": (
            "the repository V representative has lambda=(5/3)i and rho=1, so its rank-seven orbit is an endpoint"
        ),
        "rows": rows,
        "stabilizer_type_independent_of_lambda": projective_independence,
        "pass": all(row["pass"] for row in rows) and projective_independence,
    }


def build_result() -> dict[str, Any]:
    result = orbit_moduli_checks()
    return {
        "schema": "a5-v-compact-orbit-moduli-v1",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "v_orbit_moduli": result,
        "pass": result["pass"],
    }


def self_test() -> None:
    baseline = orbit_moduli_checks()
    if not baseline["pass"]:
        raise RuntimeError("baseline V compact-orbit moduli check failed")
    phase_mutation = orbit_moduli_checks("delete_phase_generator")
    if phase_mutation["pass"] or phase_mutation["rows"][0]["compact_tangent_rank"] == 12:
        raise RuntimeError("phase-generator deletion survived the V orbit-rank check")
    coordinate_mutation = orbit_moduli_checks("drop_i_on_v")
    if coordinate_mutation["pass"] or coordinate_mutation["rows"][0]["inside_open_V"]:
        raise RuntimeError("missing-i mutation survived the V coordinate check")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        self_test()
        print("PASS: V compact-orbit moduli self-test")
    if arguments.out is not None:
        result = build_result()
        arguments.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {arguments.out}")
    if not arguments.self_test and arguments.out is None:
        parser.error("choose --self-test or --out")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
