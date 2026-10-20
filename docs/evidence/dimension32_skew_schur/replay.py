"""Replay local dimension-32 skew-Schur charts and exact curved rank changes."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp

SOURCE_FILES = (
    "docs/evidence/dimension32_skew_schur/replay.py",
    "gororoba_quantum/skew_schur_charts.py",
    "gororoba_quantum/rank_charts.py",
    "gororoba_quantum/cd_core.py",
)
PROOF_NOTE = "docs/notes/dimension32_skew_schur_charts.md"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def source_digests(root: Path) -> dict[str, str]:
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in (*SOURCE_FILES, PROOF_NOTE)}


def _zero(matrix: sp.Matrix) -> bool:
    return bool(matrix.applyfunc(sp.factor) == sp.zeros(matrix.rows, matrix.cols))


def _matrix_record(matrix: sp.Matrix) -> dict[str, Any]:
    return {
        "shape": [matrix.rows, matrix.cols],
        "entries": [
            [str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)
        ],
    }


def _digest(record: object) -> str:
    return hashlib.sha256(json.dumps(record, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def rational_direction_point(coordinate: int) -> dict[str, Any]:
    from rank_charts import multiplication_matrix, rank_certificate
    from skew_schur_charts import SkewSchurChart, verify_skew_schur_point

    center = [Fraction(0)] * 32
    center[1] = center[10] = Fraction(1)
    chart = SkewSchurChart.from_certificate(rank_certificate(center))
    coordinates = center.copy()
    coordinates[coordinate] += Fraction(1, 7)
    point = chart.reduce(coordinates)
    full = rank_certificate(coordinates)
    _require(verify_skew_schur_point(chart, point), "coordinate perturbation fails point verification")
    _require(point.rank == full.rank, "coordinate perturbation disagrees with full rank certificate")
    frame = sp.Matrix(point.full_kernel)
    lift = sp.Matrix(point.lift)
    reduced_frame = sp.Matrix(point.reduced_certificate.kernel_basis)
    metric = sp.Matrix(point.gram_metric)
    projection = sp.Matrix(chart.projection)
    matrix = sp.Matrix(multiplication_matrix(coordinates))
    _require(_zero(matrix * frame), "coordinate perturbation kernel residual differs")
    _require(frame.rank() == point.nullity, "coordinate perturbation kernel independence differs")
    _require(_zero(projection * frame - reduced_frame), "coordinate perturbation kernel inverse differs")
    _require(_zero(frame.T * frame - reduced_frame.T * metric * reduced_frame), "kernel metric transport differs")
    _require(_zero(metric - lift.T * lift), "coordinate perturbation ambient metric differs")
    _require(point.nullity in (0, 4, 8), "nullity leaves this center's admissible rank values")
    output = {
        "schur": _matrix_record(sp.Matrix(point.schur_complement)),
        "full_kernel": _matrix_record(frame),
        "gram_metric": _matrix_record(metric),
        "full_certificate_kernel": _matrix_record(sp.Matrix(full.kernel_basis)),
    }
    inputs = [str(value) for value in coordinates]
    return {
        "coordinate": coordinate,
        "perturbation": "1/7",
        "coordinates": inputs,
        "input_sha256": _digest(inputs),
        "output_sha256": _digest(output),
        "nullity": point.nullity,
        "full_pivot_rows": list(full.pivot_rows),
        "full_pivot_columns": list(full.pivot_columns),
        "full_pivot_determinant": str(full.pivot_determinant),
        "chart_pivot_determinant": str(point.pivot_determinant),
        "reduced_rank": point.reduced_certificate.rank,
        "full_and_reduced_rank_agree": True,
        "kernel_metric_and_inverse_verified": True,
    }


def derivative_certificates() -> list[dict[str, Any]]:
    from rank_charts import multiplication_matrix, rank_certificate
    from skew_schur_charts import COORDINATE_INDICES, SkewSchurChart, verify_linearized_schur_constraint

    records = []
    for expected_nullity, entries in (
        (4, {1: Fraction(1), 10: Fraction(1, 4), 18: Fraction(5, 8), 25: Fraction(1, 8)}),
        (8, {1: Fraction(1), 10: Fraction(1)}),
        (12, {1: Fraction(1), 18: Fraction(1)}),
        (16, {1: Fraction(1), 10: Fraction(1), 18: Fraction(1), 25: Fraction(-1)}),
    ):
        center = [entries.get(index, Fraction(0)) for index in range(32)]
        chart = SkewSchurChart.from_certificate(rank_certificate(center))
        center_point = chart.reduce(center)
        center_frame = sp.Matrix(center_point.full_kernel)
        center_reduced_frame = sp.Matrix(center_point.reduced_certificate.kernel_basis)
        center_metric = sp.Matrix(center_point.gram_metric)
        _require(center_frame.rank() == expected_nullity, "center kernel independence differs")
        _require(_zero(sp.Matrix(center_point.matrix) * center_frame), "center full kernel residual differs")
        _require(
            _zero(sp.Matrix(chart.projection) * center_frame - center_reduced_frame), "center kernel inverse differs"
        )
        _require(
            _zero(center_frame.T * center_frame - center_reduced_frame.T * center_metric * center_reduced_frame),
            "center kernel metric transport differs",
        )
        derivative = chart.derivative_at_center()
        _require(verify_linearized_schur_constraint(chart, derivative), "derivative certificate fails verification")
        _require(chart.reduced_dimension == expected_nullity, "derivative center nullity differs")
        _require(derivative.coordinate_indices == COORDINATE_INDICES, "derivative direction denominator differs")
        kernel = sp.Matrix(chart.kernel)
        independent_columns = []
        for position, coordinate in enumerate(COORDINATE_INDICES):
            direction = [int(index == coordinate) for index in range(32)]
            matrix = kernel.T * sp.Matrix(multiplication_matrix(direction)) * kernel
            _require(
                matrix == sp.Matrix(derivative.direction_matrices[position]), "derivative direction matrix differs"
            )
            independent_columns.append(
                sp.Matrix([matrix[row, column] for row, column in derivative.upper_triangle_indices])
            )
        independent = sp.Matrix.hstack(*independent_columns)
        _require(independent == sp.Matrix(derivative.coefficient_matrix), "derivative coefficient matrix differs")
        _require(independent.rank() == derivative.rank, "derivative rank differs")
        sphere_map = independent.col_join(sp.Matrix(1, 30, derivative.unit_base_constraint))
        unit_kernel = sp.Matrix(derivative.unit_base_nullspace_basis)
        _require(_zero(sphere_map * unit_kernel), "unit-base tangent kernel residual differs")
        _require(unit_kernel.rank() == 29 - derivative.rank, "unit-base linearized bound differs")
        damaged = tuple(
            tuple(value + int(row == 0 and column == 0) for column, value in enumerate(entries))
            for row, entries in enumerate(derivative.coefficient_matrix)
        )
        _require(
            not verify_linearized_schur_constraint(chart, replace(derivative, coefficient_matrix=damaged)),
            "altered derivative coefficient escapes verification",
        )
        inputs = [str(value) for value in center]
        output = {
            "coefficient_matrix": _matrix_record(independent),
            "unit_base_nullspace_basis": _matrix_record(unit_kernel),
            "unit_base_constraint": [str(value) for value in derivative.unit_base_constraint],
            "center_kernel": _matrix_record(center_frame),
            "center_metric": _matrix_record(center_metric),
        }
        records.append(
            {
                "center_coordinates": inputs,
                "input_sha256": _digest(inputs),
                "output_sha256": _digest(output),
                "nullity": expected_nullity,
                "coordinate_indices": list(COORDINATE_INDICES),
                "upper_triangle_indices": [list(entry) for entry in derivative.upper_triangle_indices],
                "derivative_rank": derivative.rank,
                "unit_base_linearized_dimension": derivative.unit_base_linearized_dimension,
                "altered_derivative_coefficient_rejected": True,
                "center_kernel_metric_and_inverse_verified": True,
                **output,
            }
        )
    return records


def symbolic_same_tangent_fixture() -> dict[str, Any]:
    from rank_charts import multiplication_matrix, rank_certificate
    from skew_schur_charts import SkewSchurChart, verify_skew_schur_point

    def basis(coordinate: int) -> sp.Matrix:
        values = [0] * 32
        values[coordinate] = 1
        return sp.Matrix(multiplication_matrix(values))

    parameter = sp.Symbol("t", real=True)
    first, third, tenth = (basis(coordinate) for coordinate in (1, 3, 10))
    coordinates = [0] * 32
    coordinates[1] = coordinates[10] = 1
    chart = SkewSchurChart.from_certificate(rank_certificate(coordinates))
    complement = sp.Matrix(chart.complement)
    kernel = sp.Matrix(chart.kernel)
    transform = complement.row_join(kernel)
    projection = sp.Matrix(chart.projection)
    center = first + tenth
    _require(kernel.cols == 8, "same-tangent center must have nullity eight")
    _require(_zero(center * kernel), "center kernel residual differs")
    _require(_zero(kernel.T * third * kernel), "same-tangent direction derivative differs")
    _require(transform.det() != 0, "symbolic chart transformation is singular")
    records = []
    matrices: dict[str, sp.Matrix] = {}
    lifts: dict[str, sp.Matrix] = {}
    for name, matrix in (
        ("straight", first + parameter * third + tenth),
        (
            "curved",
            ((4 - parameter**2) * first + 4 * parameter * third) / (4 + parameter**2) + tenth,
        ),
    ):
        pivot = complement.T * matrix * complement
        cross = complement.T * matrix * kernel
        diagonal = kernel.T * matrix * kernel
        determinant = sp.factor(pivot.det())
        inverse_cross = pivot.inv() * cross
        schur = (diagonal + cross.T * inverse_cross).applyfunc(sp.factor)
        lift = (kernel - complement * inverse_cross).applyfunc(sp.factor)
        metric = (lift.T * lift).applyfunc(sp.factor)
        _require(_zero(metric - (parameter**2 + 4) * sp.eye(8) / 2), f"{name}: scalar metric differs")
        elimination = sp.eye(32)
        elimination[: complement.cols, complement.cols :] = -inverse_cross
        _require(_zero(schur + schur.T), f"{name}: skew identity differs")
        _require(
            _zero(elimination.T * transform.T * matrix * transform * elimination - sp.diag(pivot, schur)),
            f"{name}: congruence identity differs",
        )
        residual = sp.Matrix.vstack(sp.zeros(complement.cols, kernel.cols), schur)
        _require(
            _zero(transform.T * matrix * lift - residual),
            f"{name}: lift residual differs",
        )
        _require(_zero(projection * lift - sp.eye(kernel.cols)), f"{name}: inverse differs")
        _require(_zero(matrix.subs(parameter, 0) - center), f"{name}: center differs")
        _require(
            _zero(matrix.diff(parameter).subs(parameter, 0) - third),
            f"{name}: derivative differs",
        )
        _require(
            _zero(schur.diff(parameter).subs(parameter, 0)),
            f"{name}: reduced derivative differs",
        )
        schur_determinant = sp.factor(schur.det())
        second_rank = int(schur.diff(parameter, 2).subs(parameter, 0).rank())
        if name == "straight":
            _require(
                determinant == 2**32 * (parameter**2 + 2) ** 8,
                "straight pivot polynomial differs",
            )
            _require(schur_determinant == parameter**16, "straight Schur determinant differs")
            _require(
                second_rank == 8,
                "straight second derivative must have full reduced rank",
            )
            _require(
                set(schur) == {sp.Integer(0), parameter**2, -(parameter**2)},
                "straight residual entries differ",
            )
        else:
            _require(
                determinant == 2**56 / (parameter**2 + 4) ** 8,
                "curved pivot expression differs",
            )
            _require(_zero(schur), "curved path must preserve the center nullity")
            norm = ((4 - parameter**2) ** 2 + (4 * parameter) ** 2) / (4 + parameter**2) ** 2 + 1
            _require(sp.factor(norm - 2) == 0, "curved input norm differs")
            _require(_zero(matrix * lift), "curved full kernel differs")
        matrices[name] = schur
        lifts[name] = lift
        retained = {
            "pivot_determinant": str(determinant),
            "schur": _matrix_record(schur),
            "lift": _matrix_record(lift),
            "gram_metric": _matrix_record(metric),
            "schur_determinant": str(schur_determinant),
            "second_derivative_rank": second_rank,
        }
        records.append(
            {
                "path": name,
                "same_center_and_tangent": True,
                "congruence_identity": True,
                "lift_residual_identity": True,
                "projection_identity": True,
                "symbolic_record_sha256": _digest(retained),
                **retained,
            }
        )

    point_records = []
    for name, entries, expected_nullity in (
        ("straight_at_one", {1: 1, 3: 1, 10: 1}, 0),
        ("curved_at_one_scaled", {1: 3, 3: 4, 10: 5}, 8),
        ("curved_at_two", {3: 1, 10: 1}, 8),
    ):
        point_coordinates = [0] * 32
        for coordinate, value in entries.items():
            point_coordinates[coordinate] = value
        full = rank_certificate(point_coordinates)
        reduced = chart.reduce(point_coordinates)
        _require(
            full.nullity == expected_nullity == reduced.nullity,
            f"{name}: full and reduced ranks disagree",
        )
        _require(
            verify_skew_schur_point(chart, reduced),
            f"{name}: point verifier rejects its certificate",
        )
        frame = sp.Matrix(reduced.full_kernel)
        matrix = sp.Matrix(full.matrix)
        _require(frame.shape == (32, expected_nullity), f"{name}: full kernel shape differs")
        _require(_zero(matrix * frame), f"{name}: full kernel residual differs")
        _require(
            frame.rank() == expected_nullity,
            f"{name}: full kernel independence differs",
        )
        point_records.append(
            {
                "name": name,
                "coordinates": point_coordinates,
                "full_rank": full.rank,
                "nullity": full.nullity,
                "full_pivot_rows": list(full.pivot_rows),
                "full_pivot_columns": list(full.pivot_columns),
                "full_pivot_determinant": str(full.pivot_determinant),
                "chart_pivot_determinant": str(reduced.pivot_determinant),
                "full_kernel_sha256": _digest(_matrix_record(frame)),
                "full_and_reduced_rank_agree": True,
            }
        )

    _require(_zero(lifts["straight"] - lifts["curved"]), "same-tangent paths must share the retained lift")
    # An omitted quadratic term identifies the two paths incorrectly.
    _require(
        matrices["straight"] != matrices["curved"],
        "same-tangent paths must have distinct reduced matrices",
    )
    _require(
        matrices["straight"].subs(parameter, 1) != sp.zeros(8),
        "dropping the quadratic term escapes detection",
    )
    _require((parameter**16).subs(parameter, 1) != 0, "straight invertibility control fails")
    return {
        "center": {"1": "1", "10": "1"},
        "direction": {"3": "1"},
        "chart_transform": _matrix_record(transform),
        "chart_projection": _matrix_record(projection),
        "center_nullity": 8,
        "derivative_zero": True,
        "paths": records,
        "independent_rational_points": point_records,
        "quadratic_term_omission_rejected": True,
        "shared_lift_and_metric_verified": True,
        "shared_metric": "(t^2+4)/2 * I_8",
        "all_real_domain_argument": "t^2+2>0 and t^2+4>0 for every real t",
        "scope": "same first derivative permits different nearby ranks; smoothness and global coverage remain separate",
    }


def audit(root: Path) -> dict[str, Any]:
    before = source_digests(root)
    sys.path.insert(0, str(root / "gororoba_quantum"))
    from parallel import ordered_map
    from skew_schur_charts import audit_skew_schur_charts

    production = audit_skew_schur_charts()
    coordinates = tuple(index for index in range(32) if index not in (0, 16))
    direction_records = ordered_map(rational_direction_point, coordinates, min_items=2)
    _require(
        tuple(record["coordinate"] for record in direction_records) == coordinates,
        "rational direction denominator differs",
    )
    derivatives = derivative_certificates()
    symbolic = symbolic_same_tangent_fixture()
    for source in SOURCE_FILES[1:]:
        loaded = Path(str(sys.modules[Path(source).stem].__file__)).resolve()
        _require(
            loaded == (root / source).resolve(),
            "loaded module differs from the declared checkout",
        )
    _require(
        source_digests(root) == before,
        "source or proof-note bytes change during the replay",
    )
    return {
        "schema": "dimension32-skew-schur-evidence-v1",
        "versions": {"python": platform.python_version(), "sympy": sp.__version__},
        "qpu_executed": False,
        "rational_certificate": production,
        "rational_coordinate_directions": direction_records,
        "derivative_certificates": derivatives,
        "symbolic_same_tangent_fixture": symbolic,
    }


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
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare recomputed JSON with retained result.json",
    )
    arguments = parser.parse_args()
    bundle = Path(__file__).resolve().parent
    record = audit(bundle.parents[2])
    if arguments.check:
        adopt_recorded_interpreter(record, json.loads((bundle / "result.json").read_bytes()))
    result = json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if arguments.check:
        _require(
            result.encode() == (bundle / "result.json").read_bytes(),
            "skew-Schur replay differs from retained bytes",
        )
        print("Skew-Schur congruence, rank, metric transport, nonlinear fixture, mutations, and source stability pass")
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
