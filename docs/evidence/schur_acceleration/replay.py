"""Replay exact Schur acceleration systems and complete quadratic coefficients."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from dataclasses import dataclass, replace
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp

SOURCE_FILES = (
    "docs/evidence/schur_acceleration/replay.py",
    "docs/notes/schur_acceleration_certificates.md",
    "gororoba_quantum/schur_acceleration.py",
    "gororoba_quantum/skew_schur_charts.py",
    "gororoba_quantum/rank_charts.py",
    "gororoba_quantum/cd_core.py",
)
DIMENSION = 32
INDICES = tuple(index for index in range(DIMENSION) if index not in (0, 16))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def zero(matrix: sp.Matrix) -> bool:
    return bool(matrix.applyfunc(sp.factor) == sp.zeros(matrix.rows, matrix.cols))


def sparse_record(matrix: sp.Matrix) -> dict[str, Any]:
    return {
        "shape": [matrix.rows, matrix.cols],
        "nonzero_entries": [
            [row, column, str(matrix[row, column])]
            for row in range(matrix.rows)
            for column in range(matrix.cols)
            if matrix[row, column] != 0
        ],
    }


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def coordinates(entries: dict[int, int | Fraction]) -> tuple[Fraction, ...]:
    return tuple(Fraction(entries.get(index, 0)) for index in range(DIMENSION))


def as_matrix(rows: Any, row_count: int, column_count: int) -> sp.Matrix:
    require(len(rows) == row_count and all(len(row) == column_count for row in rows), "retained shape differs")
    return sp.Matrix(row_count, column_count, lambda row, column: sp.Rational(rows[row][column]))


def fraction_rows(matrix: sp.Matrix) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(tuple(Fraction(value) for value in matrix.row(row)) for row in range(matrix.rows))


def full_vector(vector: sp.Matrix) -> sp.Matrix:
    require(vector.shape == (30, 1), "free-coordinate vector has the wrong shape")
    return sp.Matrix([vector[INDICES.index(index)] if index in INDICES else 0 for index in range(DIMENSION)])


def multiplication(values: Any) -> sp.Matrix:
    from cd_core import cd_sign

    require(len(values) == DIMENSION, "full coordinate vector has the wrong length")
    return sp.Matrix(
        DIMENSION,
        DIMENSION,
        lambda row, column: cd_sign(DIMENSION, row ^ column, column) * sp.sympify(values[row ^ column]),
    )


def complete_kernel(matrix: sp.Matrix) -> sp.Matrix:
    columns = matrix.nullspace()
    kernel = sp.Matrix.hstack(*columns) if columns else sp.zeros(matrix.cols, 0)
    require(zero(matrix * kernel), "independent nullspace residual fails")
    require(kernel.rank() == matrix.cols - matrix.rank(), "independent nullspace completeness fails")
    return kernel


@dataclass
class Context:
    chart: Any
    derivative: Any
    center: sp.Matrix
    complement: sp.Matrix
    kernel: sp.Matrix
    inverse: sp.Matrix
    coefficient: sp.Matrix
    system: sp.Matrix
    tangent: sp.Matrix
    left_kernel: sp.Matrix
    entries: tuple[tuple[int, int], ...]

    def cross(self, direction: sp.Matrix) -> sp.Matrix:
        return self.complement.T * multiplication(direction) * self.kernel

    def quadratic(self, direction: sp.Matrix) -> sp.Matrix:
        cross = self.cross(direction)
        return cross.T * self.inverse * cross

    def residual(self, values: sp.Matrix) -> sp.Matrix:
        matrix = multiplication(values)
        pivot = self.complement.T * matrix * self.complement
        cross = self.complement.T * matrix * self.kernel
        diagonal = self.kernel.T * matrix * self.kernel
        return (diagonal + cross.T * pivot.inv() * cross).applyfunc(sp.factor)


def context(entries: dict[int, int | Fraction]) -> Context:
    from rank_charts import rank_certificate
    from skew_schur_charts import SkewSchurChart, verify_linearized_schur_constraint

    center = sp.Matrix(coordinates(entries))
    chart = SkewSchurChart.from_certificate(rank_certificate(tuple(Fraction(value) for value in center)))
    derivative = chart.derivative_at_center()
    require(verify_linearized_schur_constraint(chart, derivative), "production derivative fails verification")
    require(derivative.coordinate_indices == INDICES, "derivative coordinate denominator differs")
    matrix = multiplication(center)
    require(matrix == sp.Matrix(chart.center_certificate.matrix), "independent center multiplication differs")
    complement, kernel = sp.Matrix(chart.complement), sp.Matrix(chart.kernel)
    nullity = kernel.cols
    require(zero(matrix + matrix.T), "center multiplication is not skew")
    require(matrix.rank() == DIMENSION - nullity and kernel.rank() == nullity, "center kernel rank differs")
    require(zero(matrix * kernel), "center kernel residual differs")
    require(complement.row_join(kernel).det() != 0, "center complement is incomplete")
    pivot = complement.T * matrix * complement
    require(pivot.det() != 0, "center pivot is singular")
    require(zero(complement.T * matrix * kernel), "center cross block differs")
    upper = tuple((row, column) for row in range(nullity) for column in range(row + 1, nullity))
    diagonal_blocks = [kernel.T * multiplication(coordinates({index: 1})) * kernel for index in INDICES]
    coefficient = sp.Matrix(
        len(upper), len(INDICES), lambda row, column: diagonal_blocks[column][upper[row][0], upper[row][1]]
    )
    require(coefficient == sp.Matrix(derivative.coefficient_matrix), "independent derivative columns differ")
    require(upper == derivative.upper_triangle_indices, "upper-triangle denominator differs")
    radial = sp.Matrix([center[index] for index in INDICES])
    system = coefficient.col_join(radial.T)
    tangent = complete_kernel(system)
    left = complete_kernel(coefficient.T)
    require(zero(coefficient * radial), "radial direction leaves the derivative kernel")
    require(system.rank() == coefficient.rank() + 1, "radial row independence fails")
    published_tangent = sp.Matrix(derivative.unit_base_nullspace_basis)
    require(zero(system * published_tangent), "production tangent residual differs")
    require(published_tangent.rank() == tangent.cols, "production tangent completeness differs")
    return Context(
        chart, derivative, center, complement, kernel, pivot.inv(), coefficient, system, tangent, left, upper
    )


def changed(rows: Any) -> Any:
    return tuple(
        tuple(value + int(row == 0 and column == 0) for column, value in enumerate(values))
        for row, values in enumerate(rows)
    )


def certificate_case(case: tuple[str, dict[int, int | Fraction], dict[int, int | Fraction], str]) -> dict[str, Any]:
    from schur_acceleration import (
        certify_schur_acceleration,
        verify_acceleration_member,
        verify_schur_acceleration_certificate,
    )

    label, center_entries, direction_entries, expected_status = case
    setup = context(center_entries)
    direction_values = coordinates(direction_entries)
    direction = sp.Matrix(direction_values)
    certificate = certify_schur_acceleration(setup.chart, direction_values, linearized=setup.derivative)
    require(verify_schur_acceleration_certificate(setup.chart, certificate), "production certificate fails")
    require(certificate.status == expected_status, "certificate state differs")
    quadratic = setup.quadratic(direction)
    first = setup.kernel.T * multiplication(direction) * setup.kernel
    rhs = sp.Matrix([-2 * quadratic[row, column] for row, column in setup.entries] + [-direction.dot(direction)])
    first_order = setup.system * sp.Matrix([direction[index] for index in INDICES])
    require(zero(quadratic + quadratic.T), "quadratic term is not skew")
    require(sp.Matrix(certificate.direction_cross) == setup.cross(direction), "direction cross differs")
    require(sp.Matrix(certificate.first_schur_derivative) == first, "first Schur derivative differs")
    require(sp.Matrix(certificate.quadratic_term) == quadratic, "quadratic term differs")
    require(sp.Matrix(certificate.system_matrix) == setup.system, "acceleration system differs")
    require(sp.Matrix(certificate.system_rhs) == rhs, "acceleration right-hand side differs")
    require(sp.Matrix(certificate.first_order_residual) == first_order, "first-order residual differs")
    record: dict[str, Any] = {
        "label": label,
        "center": sparse_record(setup.center),
        "direction": sparse_record(direction),
        "status": certificate.status,
        "center_nullity": setup.kernel.cols,
        "derivative_rank": int(setup.coefficient.rank()),
        "system": sparse_record(setup.system),
        "rhs": sparse_record(rhs),
        "quadratic": sparse_record(quadratic),
        "first_order_residual": sparse_record(first_order),
    }
    mutations = {
        "system_matrix": replace(certificate, system_matrix=changed(certificate.system_matrix)),
        "system_rhs": replace(certificate, system_rhs=(certificate.system_rhs[0] + 1, *certificate.system_rhs[1:])),
        "direction_cross": replace(certificate, direction_cross=changed(certificate.direction_cross)),
        "quadratic_term": replace(certificate, quadratic_term=changed(certificate.quadratic_term)),
        "first_schur_derivative": replace(
            certificate, first_schur_derivative=changed(certificate.first_schur_derivative)
        ),
        "first_order_residual": replace(
            certificate,
            first_order_residual=(certificate.first_order_residual[0] + 1, *certificate.first_order_residual[1:]),
        ),
        "direction": replace(certificate, direction=(Fraction(1), *certificate.direction[1:])),
        "linearized_rank": replace(certificate, linearized=replace(certificate.linearized, rank=30)),
        "chart": replace(certificate, chart=replace(setup.chart, complement=changed(setup.chart.complement))),
        "status": replace(
            certificate,
            status="second_order_obstructed"
            if expected_status == "second_order_compatible"
            else "second_order_compatible",
        ),
    }
    if expected_status == "second_order_compatible":
        affine = certificate.affine_space
        if affine is None:
            raise RuntimeError("compatible certificate omits its affine space")
        require(
            affine is not None and certificate.obstruction is None and zero(first_order), "compatible state differs"
        )
        particular = sp.Matrix(affine.particular)
        kernel = as_matrix(affine.kernel_basis, 30, 30 - affine.rank)
        schur_particular = sp.Matrix(affine.schur_particular)
        radial = sp.Matrix([setup.center[index] for index in INDICES])
        require(zero(setup.system * particular - rhs), "particular residual differs")
        require(zero(setup.coefficient * schur_particular - rhs[:-1, :]), "Schur particular residual differs")
        require(zero(setup.system * kernel), "homogeneous acceleration residual differs")
        require(kernel.rank() == 30 - setup.system.rank(), "homogeneous acceleration basis is incomplete")
        require(affine.rank == setup.system.rank(), "affine rank differs")
        require(
            setup.system.extract(affine.pivot_rows, affine.pivot_columns).det() == affine.pivot_determinant
            and affine.pivot_determinant != 0,
            "rank-minor witness differs",
        )
        correction = (-direction.dot(direction) - radial.dot(schur_particular)) / radial.dot(radial)
        require(correction == affine.radial_correction, "radial correction differs")
        require(particular == schur_particular + correction * radial, "corrected particular differs")
        parameters = tuple(Fraction(index + 1, index + 2) for index in range(kernel.cols))
        expected = full_vector(particular + kernel * sp.Matrix(parameters))
        generated = certificate.acceleration(parameters)
        require(sp.Matrix(generated) == expected, "complete affine parameterization differs")
        require(verify_acceleration_member(certificate, generated), "affine member verifier rejects valid member")
        second = setup.kernel.T * multiplication(expected) * setup.kernel + 2 * quadratic
        require(zero(second) and setup.center.dot(expected) == -direction.dot(direction), "direct acceleration fails")
        wrong = list(generated)
        wrong[1] += 1
        require(not verify_acceleration_member(certificate, tuple(wrong)), "damaged acceleration passes")
        for name, value in {
            "particular": (affine.particular[0] + 1, *affine.particular[1:]),
            "schur_particular": (affine.schur_particular[0] + 1, *affine.schur_particular[1:]),
            "radial_correction": affine.radial_correction + 1,
            "kernel_basis": changed(affine.kernel_basis),
            "rank": affine.rank + 1,
            "pivot_determinant": affine.pivot_determinant + 1,
            "pivot_rows": (affine.pivot_rows[0],) * len(affine.pivot_rows),
            "pivot_columns": (affine.pivot_columns[0],) * len(affine.pivot_columns),
        }.items():
            mutations[f"affine_{name}"] = replace(certificate, affine_space=replace(affine, **{name: value}))
        mutations["affine_incomplete_kernel"] = replace(
            certificate,
            affine_space=replace(affine, kernel_basis=tuple(row[:-1] for row in affine.kernel_basis)),
        )
        record["affine_solution"] = {
            "particular": sparse_record(particular),
            "schur_particular": sparse_record(schur_particular),
            "radial_correction": str(correction),
            "complete_kernel": sparse_record(kernel),
            "dimension": kernel.cols,
            "rank": affine.rank,
            "pivot_rows": list(affine.pivot_rows),
            "pivot_columns": list(affine.pivot_columns),
            "pivot_determinant": str(affine.pivot_determinant),
            "parameterized_member_sha256": digest(sparse_record(expected)),
            "direct_second_order_and_norm_checks": True,
        }
    elif expected_status == "second_order_obstructed":
        obstruction = certificate.obstruction
        if obstruction is None:
            raise RuntimeError("obstructed certificate omits its separator")
        require(
            obstruction is not None and certificate.affine_space is None and zero(first_order),
            "obstruction state differs",
        )
        covector = sp.Matrix(obstruction.covector)
        require(zero(covector.T * setup.system), "separator left-kernel residual differs")
        pairing = (covector.T * rhs)[0]
        require(pairing == obstruction.pairing and pairing != 0 and covector[-1] == 0, "separator pairing differs")
        mutations["zero_separator"] = replace(
            certificate, obstruction=replace(obstruction, covector=tuple(Fraction(0) for _ in obstruction.covector))
        )
        mutations["zero_pairing"] = replace(certificate, obstruction=replace(obstruction, pairing=Fraction(0)))
        mutations["damaged_separator"] = replace(
            certificate,
            obstruction=replace(obstruction, covector=(obstruction.covector[0] + 1, *obstruction.covector[1:])),
        )
        record["separator"] = {"covector": sparse_record(covector), "pairing": str(pairing)}
    else:
        require(
            not zero(first_order) and certificate.affine_space is None and certificate.obstruction is None,
            "first-order state differs",
        )
    for name, damaged in mutations.items():
        require(not verify_schur_acceleration_certificate(setup.chart, damaged), f"mutation passes: {label}/{name}")
    record["damaged_certificate_fields_rejected"] = sorted(mutations)
    return record


def symbolic_curvature() -> dict[str, Any]:
    setup = context({1: 1, 10: 1})
    parameter = sp.Symbol("t", real=True)
    direction = sp.Matrix(coordinates({3: 1}))
    acceleration = sp.Matrix(coordinates({1: -1}))
    quadratic = setup.quadratic(direction)
    curved = sp.Matrix(coordinates({10: 1}))
    curved[1] = (4 - parameter**2) / (4 + parameter**2)
    curved[3] = 4 * parameter / (4 + parameter**2)
    straight = setup.center + parameter * direction
    require(sp.factor(curved.dot(curved)) == 2, "curved norm differs")
    require(curved.diff(parameter).subs(parameter, 0) == direction, "curved velocity differs")
    require(curved.diff(parameter, 2).subs(parameter, 0) == acceleration, "curved acceleration differs")
    curved_residual, straight_residual = setup.residual(curved), setup.residual(straight)
    require(zero(curved_residual), "curved exact Schur residual differs")
    require(zero(straight_residual.diff(parameter).subs(parameter, 0)), "straight first derivative differs")
    require(
        zero(straight_residual.diff(parameter, 2).subs(parameter, 0) - 2 * quadratic), "factor-two derivative differs"
    )
    require(sp.factor(straight_residual.det()) == parameter**16, "straight determinant differs")
    require((2 * quadratic).rank() == 8, "straight quadratic rank differs")
    normalized = sp.sqrt(2 / (2 + parameter**2)) * straight
    normalized_acceleration = normalized.diff(parameter, 2).subs(parameter, 0)
    require(normalized_acceleration == -setup.center / 2, "radial normalized acceleration differs")
    diagonal = setup.kernel.T * multiplication(acceleration) * setup.kernel
    radial_diagonal = setup.kernel.T * multiplication(normalized_acceleration) * setup.kernel
    require(zero(diagonal + 2 * quadratic), "known curved cancellation differs")
    require(not zero(diagonal + quadratic) and not zero(diagonal - 2 * quadratic), "factor/sign controls fail")
    require(zero(radial_diagonal) and normalized_acceleration.dot(setup.center) == -1, "radial identity differs")
    return {
        "center_norm_squared": "2",
        "curved_coordinates": sparse_record(curved),
        "velocity": sparse_record(direction),
        "curved_acceleration": sparse_record(acceleration),
        "curved_schur_identically_zero": True,
        "straight_schur_determinant": str(sp.factor(straight_residual.det())),
        "straight_second_derivative": sparse_record(2 * quadratic),
        "straight_second_derivative_rank": 8,
        "normalized_straight_acceleration": sparse_record(normalized_acceleration),
        "normalization_preserves_schur_obstruction": True,
        "missing_factor_two_and_wrong_sign_rejected": True,
    }


def explicit_separator() -> dict[str, Any]:
    setup = context({1: 1, 18: 1})
    direction = sp.Matrix(coordinates({11: 1}))
    quadratic = setup.quadratic(direction)
    rows = [setup.entries.index(pair) for pair in ((0, 1), (4, 5))]
    expected = sp.zeros(1, 30)
    expected[0, INDICES.index(1)], expected[0, INDICES.index(18)] = 2, -2
    require(
        setup.coefficient[rows[0], :] == setup.coefficient[rows[1], :] == expected, "explicit derivative rows differ"
    )
    covector = sp.zeros(setup.system.rows, 1)
    covector[rows[0]], covector[rows[1]] = -1, 1
    rhs = sp.Matrix([-2 * quadratic[row, column] for row, column in setup.entries] + [-1])
    require(zero(setup.system * sp.Matrix([direction[index] for index in INDICES])), "e11 first order fails")
    require(rhs[rows[0]] == 2 and rhs[rows[1]] == -2, "explicit right-hand sides differ")
    require(zero(covector.T * setup.system) and (covector.T * rhs)[0] == -4, "explicit separator fails")
    require(quadratic[4, 5] - quadratic[0, 1] == 2, "tangent necessary-condition witness differs")
    return {
        "center": sparse_record(setup.center),
        "direction": sparse_record(direction),
        "derivative_rank": int(setup.coefficient.rank()),
        "linearized_sphere_dimension": setup.tangent.cols,
        "residual_entries": [[0, 1], [4, 5]],
        "common_derivative_row": sparse_record(expected),
        "right_hand_side_values": ["2", "-2"],
        "separating_covector": sparse_record(covector),
        "rhs_pairing": "-4",
        "quadratic_pairing": "2",
        "scope": "excludes same-nullity constant-norm Bouligand direction by the written exact-identity proof",
    }


def polarization_case(case: tuple[str, dict[int, int | Fraction], int]) -> dict[str, Any]:
    label, center_entries, expected_dimension = case
    setup = context(center_entries)
    tangent = setup.tangent
    require(tangent.cols == expected_dimension, "polarization dimension differs")
    directions = [full_vector(tangent[:, index]) for index in range(tangent.cols)]
    crosses = [setup.cross(direction) for direction in directions]
    solved = [setup.inverse * cross for cross in crosses]
    quadratics = [cross.T * solution for cross, solution in zip(crosses, solved, strict=True)]
    exponent_pairs = [(index, index) for index in range(tangent.cols)]
    exponent_pairs.extend((left, right) for left in range(tangent.cols) for right in range(left + 1, tangent.cols))
    coefficient_columns = []
    for left, right in exponent_pairs:
        if left == right:
            coefficient = quadratics[left]
            evaluation = coefficient
        else:
            coefficient = crosses[left].T * solved[right] + crosses[right].T * solved[left]
            evaluation = setup.quadratic(directions[left] + directions[right])
            require(evaluation == quadratics[left] + quadratics[right] + coefficient, "polarization identity fails")
        values = sp.Matrix([coefficient[row, column] for row, column in setup.entries])
        projected = setup.left_kernel.T * values
        require(zero(projected), "projected quadratic coefficient differs from zero")
        require(
            zero(setup.left_kernel.T * sp.Matrix([evaluation[row, column] for row, column in setup.entries])),
            "basis/pair evaluation is obstructed",
        )
        coefficient_columns.append(projected)
    coefficient_matrix = sp.Matrix.hstack(*coefficient_columns)
    require(
        len(exponent_pairs) == expected_dimension * (expected_dimension + 1) // 2, "coefficient denominator differs"
    )
    return {
        "label": label,
        "center": sparse_record(setup.center),
        "center_nullity": setup.kernel.cols,
        "tangent_basis": sparse_record(tangent),
        "complete_derivative_left_kernel": sparse_record(setup.left_kernel),
        "derivative_matrix_sha256": digest(sparse_record(setup.coefficient)),
        "monomial_pairs": [list(pair) for pair in exponent_pairs],
        "coefficient_count": len(exponent_pairs),
        "projected_coefficient_matrix": sparse_record(coefficient_matrix),
        "scope": "all real linearized sphere directions admit second-order accelerations; curve existence is separate",
    }


def invalid_inputs() -> list[str]:
    from schur_acceleration import certify_schur_acceleration

    setup = context({1: 1, 10: 1})
    valid = coordinates({3: 1})
    cases: dict[str, Any] = {
        "wrong_length": valid[:-1],
        "forbidden_real_coordinate": (Fraction(1), *valid[1:]),
        "forbidden_distinguished_coordinate": coordinates({3: 1, 16: 1}),
        "float_coordinate": tuple(0.5 if index == 3 else value for index, value in enumerate(valid)),
        "boolean_coordinate": tuple(True if index == 3 else value for index, value in enumerate(valid)),
        "string_input": "invalid",
    }
    for label, values in cases.items():
        try:
            certify_schur_acceleration(setup.chart, values)
        except (ValueError, TypeError):
            continue
        raise RuntimeError(f"invalid direction passes: {label}")
    damaged_chart = replace(setup.chart, complement=changed(setup.chart.complement))
    try:
        certify_schur_acceleration(damaged_chart, valid)
    except (ValueError, TypeError):
        pass
    else:
        raise RuntimeError("invalid center chart passes")
    return [*sorted(cases), "invalid_center_chart"]


def source_digests(root: Path) -> dict[str, str]:
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in SOURCE_FILES}


def audit(root: Path) -> dict[str, Any]:
    before = source_digests(root)
    sys.path.insert(0, str(root / "gororoba_quantum"))
    from parallel import ordered_map

    cases = [
        ("curvature", {1: 1, 10: 1}, {3: 1}, "second_order_compatible"),
        ("separator", {1: 1, 18: 1}, {11: 1}, "second_order_obstructed"),
        ("nullity4_zero_velocity", {1: 1, 10: 2, 18: 3, 25: -4}, {}, "second_order_compatible"),
        ("nullity16_zero_velocity", {1: 1, 10: 1, 18: 1, 25: -1}, {}, "second_order_compatible"),
        ("radial_first_order_rejection", {1: 1, 10: 1}, {1: 1, 10: 1}, "first_order_inadmissible"),
    ]
    certificates = ordered_map(certificate_case, cases, min_items=2)
    polarized = ordered_map(
        polarization_case,
        [("nullity8", {1: 1, 10: 1}, 23), ("nullity16", {1: 1, 10: 1, 18: 1, 25: -1}, 11)],
        min_items=2,
    )
    result = {
        "schema": "schur-acceleration-evidence-v1",
        "versions": {"python": platform.python_version(), "sympy": sp.__version__},
        "certificates": certificates,
        "symbolic_curvature": symbolic_curvature(),
        "explicit_separator": explicit_separator(),
        "invalid_inputs_rejected": invalid_inputs(),
        "complete_quadratic_coefficients": polarized,
        "qpu_executed": False,
    }
    for source in SOURCE_FILES[2:]:
        loaded = Path(str(sys.modules[Path(source).stem].__file__)).resolve()
        require(loaded == (root / source).resolve(), "loaded module differs from declared checkout")
    require(source_digests(root) == before, "source or proof note changes during replay")
    return result


def adopt_recorded_interpreter(record: dict[str, Any], retained: dict[str, Any]) -> None:
    """Carry the retained interpreter release into a replay under the same Python major.minor.

    The patch release names the interpreter that wrote result.json and is
    provenance; every certificate field still compares byte for byte, and a
    replay under another major.minor keeps its own version and differs.
    """
    for holder, key, kept in (
        (record, "python_version", retained),
        (record.get("versions"), "python", retained.get("versions")),
    ):
        if isinstance(holder, dict) and isinstance(kept, dict) and key in holder and isinstance(kept.get(key), str):
            if kept[key].split(".")[:2] == str(holder[key]).split(".")[:2]:
                holder[key] = kept[key]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare rebuilt evidence with retained result.json")
    arguments = parser.parse_args()
    bundle = Path(__file__).resolve().parent
    record = audit(bundle.parents[2])
    if arguments.check:
        adopt_recorded_interpreter(record, json.loads((bundle / "result.json").read_bytes()))
    result = json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if arguments.check:
        require(result.encode() == (bundle / "result.json").read_bytes(), "Schur acceleration evidence differs")
        print("Schur acceleration systems, complete kernels, separators, polynomial coefficients, and hashes pass")
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
