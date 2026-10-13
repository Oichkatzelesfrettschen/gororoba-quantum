"""Replay the small principal cover and kernel-restricted overlap certificates."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp

SOURCE_FILES = (
    "docs/evidence/principal_skew_atlas/replay.py",
    "gororoba_quantum/principal_skew_atlas.py",
    "gororoba_quantum/skew_schur_charts.py",
    "gororoba_quantum/rank_charts.py",
    "gororoba_quantum/cd_core.py",
)
PROOF_NOTE = "docs/notes/principal_skew_atlas.md"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def source_digests(root: Path) -> dict[str, str]:
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in (*SOURCE_FILES, PROOF_NOTE)}


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _matrix(rows: Sequence[Sequence[Fraction]], row_count: int, column_count: int) -> sp.Matrix:
    _require(len(rows) == row_count, "retained matrix row count differs")
    _require(all(len(row) == column_count for row in rows), "retained matrix column count differs")
    return sp.Matrix(row_count, column_count, lambda row, column: sp.Rational(rows[row][column]))


def _matrix_record(matrix: sp.Matrix) -> dict[str, Any]:
    return {
        "shape": [matrix.rows, matrix.cols],
        "entries": [[str(value) for value in matrix.row(row)] for row in range(matrix.rows)],
    }


def symbolic_cover() -> dict[str, Any]:
    from cd_core import cd_sign
    from principal_skew_atlas import principal_cover

    records = []
    for stage in range(2, 9):
        dimension = 2**stage
        half = dimension // 2
        symbols = list(sp.symbols(f"x0:{dimension}", real=True))
        symbols[0] = symbols[half] = sp.Integer(0)
        charts = principal_cover(dimension)
        expected_indices = tuple((0, half, index, half + index) for index in range(1, half))
        _require(tuple(chart.pivot_indices for chart in charts) == expected_indices, "cover index denominator differs")
        pivot_records = []
        for chart in charts:
            indices = chart.pivot_indices
            first = symbols[indices[2]]
            second = symbols[indices[3]]
            actual = sp.Matrix(
                [
                    [cd_sign(dimension, row ^ column, column) * symbols[row ^ column] for column in indices]
                    for row in indices
                ]
            )
            expected = sp.Matrix(
                [[0, 0, -first, -second], [0, 0, second, -first], [first, -second, 0, 0], [second, first, 0, 0]]
            )
            norm_squared = first**2 + second**2
            _require(actual == expected, "symbolic principal block differs from the quaternion formula")
            _require(actual**2 == -norm_squared * sp.eye(4), "symbolic square differs")
            _require(sp.factor(actual.det() - norm_squared**2) == 0, "symbolic determinant differs")
            pivot_records.append(
                {
                    "indices": list(indices),
                    "coefficient_indices": [indices[2], indices[3]],
                    "pivot": _matrix_record(actual),
                    "determinant": str(norm_squared**2),
                }
            )
        _require(
            sum(symbols[index] ** 2 for index in range(dimension))
            == sum(symbols[index] ** 2 + symbols[half + index] ** 2 for index in range(1, half)),
            "pair norms do not cover the full norm",
        )
        records.append(
            {
                "stage": stage,
                "dimension": dimension,
                "chart_count": len(charts),
                "all_coefficient_symbols": [str(symbol) for symbol in symbols],
                "pivots": pivot_records,
                "coverage_norm_identity": True,
                "initial_inverse_norm_bound": f"sqrt({half - 1})/norm(x)",
            }
        )
    return {
        "expanded_stage_range": [2, 8],
        "total_symbolic_pivots": sum(record["chart_count"] for record in records),
        "records": records,
        "unbounded_scope": (
            "the written doubling proof covers every stage n>=2; finite expansion checks the implementation"
        ),
    }


def independent_point(task: tuple[str, dict[int, Fraction], int]) -> dict[str, Any]:
    from principal_skew_atlas import (
        PrincipalSkewChart,
        principal_cover,
        select_cover_chart,
        select_maximal_principal_pivot,
    )
    from rank_charts import rank_certificate

    label, entries, expected_nullity = task
    dimension = 32
    coordinates = tuple(entries.get(index, Fraction(0)) for index in range(dimension))
    independent = rank_certificate(coordinates)
    _require(independent.nullity == expected_nullity, "fixture full-rank certificate differs")
    full_matrix = sp.Matrix(independent.matrix)
    selected = select_cover_chart(coordinates)
    pair_norms = tuple(coordinates[index] ** 2 + coordinates[16 + index] ** 2 for index in range(1, 16))
    chosen_index = min(index for index, value in enumerate(pair_norms, start=1) if value == max(pair_norms))
    _require(selected.pivot_indices == (0, 16, chosen_index, chosen_index + 16), "conditioning selector differs")
    chosen_point = selected.reduce(coordinates)
    input_norm_squared = sum(value * value for value in coordinates)
    _require(chosen_point.pivot_determinant >= input_norm_squared**2 / 225, "initial pivot determinant bound fails")

    charts = [
        chart
        for chart in principal_cover(dimension)
        if coordinates[chart.pivot_indices[2]] or coordinates[chart.pivot_indices[3]]
    ]
    admitted_cover_count = len(charts)
    if len(charts) > 4:
        charts = [charts[0], charts[len(charts) // 2], charts[-1]]
    refinement = select_maximal_principal_pivot(coordinates, initial_indices=selected.pivot_indices)
    _require(len(refinement.pivot_indices) == independent.rank, "principal refinement rank differs")
    chain_indices = selected.pivot_indices
    chain_records = []
    for step in refinement.steps:
        chain_free = tuple(index for index in range(dimension) if index not in chain_indices)
        chain_pivot = full_matrix.extract(chain_indices, chain_indices)
        chain_cross = full_matrix.extract(chain_indices, chain_free)
        chain_residual = full_matrix.extract(chain_free, chain_free) + chain_cross.T * chain_pivot.inv() * chain_cross
        first_position, second_position = (chain_free.index(index) for index in step.pair_indices)
        _require(
            chain_residual[first_position, second_position] == sp.Rational(step.pivot_entry),
            "retained refinement entry differs",
        )
        next_indices = chain_indices + step.pair_indices
        next_determinant = full_matrix.extract(next_indices, next_indices).det()
        _require(
            next_determinant == chain_pivot.det() * sp.Rational(step.pivot_entry) ** 2,
            "principal refinement determinant product differs",
        )
        chain_records.append(
            {
                "selected_pair": list(step.pair_indices),
                "entry": str(step.pivot_entry),
                "principal_determinant": str(next_determinant),
            }
        )
        chain_indices = next_indices
    _require(chain_indices == refinement.pivot_indices, "refinement pair sequence differs")
    charts.append(refinement.chart)
    # Full independent columns of a skew matrix form a rank-sized principal pivot.
    maximal_indices = tuple(int(index) for index in full_matrix.rref()[1])
    _require(
        full_matrix.extract(maximal_indices, maximal_indices).det() != 0, "independent principal pivot is singular"
    )
    charts.append(PrincipalSkewChart(dimension, maximal_indices))
    points = [chart.reduce(coordinates) for chart in charts]
    point_records = []
    matrices = []
    pivot_inverses = []
    for point in points:
        pivot_size = len(point.chart.pivot_indices)
        residual_size = dimension - pivot_size
        lift = _matrix(point.lift, dimension, residual_size)
        projection = _matrix(point.chart.projection, residual_size, dimension)
        free_frame = _matrix(point.chart.free_frame, dimension, residual_size)
        complement = _matrix(point.chart.complement, dimension, pivot_size)
        pivot = _matrix(point.pivot, pivot_size, pivot_size)
        residual = _matrix(point.schur_complement, residual_size, residual_size)
        metric = _matrix(point.gram_metric, residual_size, residual_size)
        full_kernel = _matrix(point.full_kernel, dimension, expected_nullity)
        reduced_kernel = projection * full_kernel
        _require(point.nullity == expected_nullity, "principal reduced nullity differs")
        _require(full_matrix * lift == free_frame * residual, "principal lift residual differs")
        _require(projection * lift == sp.eye(residual_size), "principal inverse differs")
        _require(metric == lift.T * lift, "principal metric differs")
        _require(full_matrix * full_kernel == sp.zeros(dimension, expected_nullity), "full kernel residual differs")
        _require(full_kernel.rank() == expected_nullity, "full kernel independence differs")
        _require(lift * reduced_kernel == full_kernel, "principal kernel reconstruction differs")
        _require(reduced_kernel.rank() == expected_nullity, "reduced kernel independence differs")
        if pivot_size == independent.rank:
            constant = point.constant_rank_chart()
            _require(sp.Matrix(constant.kernel_frame) == full_kernel, "constant-rank interface frame differs")
        output = {
            "pivot_indices": list(point.chart.pivot_indices),
            "pivot_determinant": str(point.pivot_determinant),
            "schur": _matrix_record(residual),
            "lift": _matrix_record(lift),
            "metric": _matrix_record(metric),
            "full_kernel": _matrix_record(full_kernel),
        }
        point_records.append(
            {
                "output_sha256": _digest(output),
                "pivot_indices": list(point.chart.pivot_indices),
                "pivot_determinant": str(point.pivot_determinant),
                "residual_dimension": residual_size,
                "full_kernel_shape": [dimension, expected_nullity],
            }
        )
        matrices.append((lift, projection, free_frame, complement, pivot, residual, metric, reduced_kernel))
        pivot_inverses.append(pivot.inv())
    pair_count = 0
    triple_count = 0
    unequal_count = 0
    for source in matrices:
        source_lift, source_projection, source_free, _, _, source_residual, source_metric, source_kernel = source
        for target_index, target in enumerate(matrices):
            target_lift, target_projection, _, target_complement, target_pivot, target_residual, target_metric, _ = (
                target
            )
            transport = target_projection * source_lift
            reverse = source_projection * target_lift
            correction = target_complement * pivot_inverses[target_index] * target_complement.T * source_free
            _require(
                target_lift * transport - source_lift == -correction * source_residual, "overlap lift defect differs"
            )
            _require(
                target_residual * transport == target_lift.T * source_free * source_residual,
                "overlap intertwiner differs",
            )
            _require(
                reverse * transport - sp.eye(source_residual.rows) == -source_projection * correction * source_residual,
                "overlap inverse defect differs",
            )
            _require(
                source_kernel.T * (transport.T * target_metric * transport - source_metric) * source_kernel
                == sp.zeros(expected_nullity),
                "overlap restricted metric differs",
            )
            _require(
                (target_lift * transport - source_lift) * source_kernel == sp.zeros(dimension, expected_nullity),
                "overlap kernel reconstruction differs",
            )
            pair_count += 1
            unequal_count += int(source_residual.rows != target_residual.rows)
            for last in matrices:
                last_projection = last[1]
                composed = last_projection * target_lift * transport
                direct = last_projection * source_lift
                _require(
                    composed - direct == -last_projection * correction * source_residual,
                    "overlap cocycle defect differs",
                )
                _require(
                    (composed - direct) * source_kernel == sp.zeros(last_projection.rows, expected_nullity),
                    "overlap kernel cocycle differs",
                )
                triple_count += 1
    inputs = [str(value) for value in coordinates]
    return {
        "label": label,
        "coordinates": inputs,
        "input_sha256": _digest(inputs),
        "nullity": expected_nullity,
        "selected_pivot_indices": list(selected.pivot_indices),
        "initial_pivot_bound_verified": True,
        "admitted_cover_count": admitted_cover_count,
        "principal_refinement": chain_records,
        "maximal_principal_indices": list(refinement.pivot_indices),
        "charts": point_records,
        "overlap_pairs": pair_count,
        "unequal_residual_size_pairs": unequal_count,
        "overlap_triples": triple_count,
        "all_residual_factor_and_kernel_metric_identities_verified": True,
    }


def audit(root: Path) -> dict[str, Any]:
    before = source_digests(root)
    sys.path.insert(0, str(root / "gororoba_quantum"))
    from parallel import ordered_map
    from principal_skew_atlas import audit_principal_skew_atlas

    production = audit_principal_skew_atlas()
    symbolic = symbolic_cover()
    tasks = [
        ("nullity4", {1: Fraction(1), 10: Fraction(1, 4), 18: Fraction(5, 8), 25: Fraction(1, 8)}, 4),
        ("nullity8", {1: Fraction(1), 10: Fraction(1)}, 8),
        ("nullity12", {1: Fraction(1), 18: Fraction(1)}, 12),
        ("nullity16", {1: Fraction(1), 10: Fraction(1), 18: Fraction(1), 25: Fraction(-1)}, 16),
        ("dense_invertible", {index: Fraction(index + 1, 31) for index in range(32) if index not in (0, 16)}, 0),
    ]
    rational = ordered_map(independent_point, tasks, min_items=2)
    for source in SOURCE_FILES[1:]:
        loaded = Path(str(sys.modules[Path(source).stem].__file__)).resolve()
        _require(loaded == (root / source).resolve(), "loaded module differs from the declared checkout")
    _require(source_digests(root) == before, "source or proof-note bytes change during replay")
    return {
        "schema": "principal-skew-atlas-evidence-v1",
        "versions": {"python": platform.python_version(), "sympy": sp.__version__},
        "qpu_executed": False,
        "production_certificate": production,
        "symbolic_cover": symbolic,
        "independent_rational_points": rational,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare recomputed JSON with retained result.json")
    arguments = parser.parse_args()
    bundle = Path(__file__).resolve().parent
    result = json.dumps(audit(bundle.parents[2]), indent=2, sort_keys=True, allow_nan=False) + "\n"
    if arguments.check:
        _require(
            result.encode() == (bundle / "result.json").read_bytes(),
            "principal-atlas replay differs from retained bytes",
        )
        print("Principal cover, rank refinement, restricted overlap identities, mutations, and source stability pass")
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
