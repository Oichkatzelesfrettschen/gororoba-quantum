"""Exact quadratic Schur-form witnesses on the seven first-order degeneracy loci."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from dataclasses import dataclass
from fractions import Fraction
from functools import partial
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KERNEL_BUNDLES = HERE.parent / "a5-kernel-bundles"
NULLITY_EIGHT = HERE.parent / "a5-kernel-bundles-nullity8"
REGULARITY = HERE.parent / "a5-strata-regularity"
EQUATIONS = HERE.parent / "a5-rank-strata-equations"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(KERNEL_BUNDLES))
sys.path.insert(0, str(NULLITY_EIGHT))
sys.path.insert(0, str(REGULARITY))
sys.path.insert(0, str(EQUATIONS))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import boundary_specializations as boundary  # noqa: E402
import first_order_normal_cones as first_order  # noqa: E402
import path_supported_basepoints as basepoints  # noqa: E402
import strata_regularity as regularity  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-attachments-schur-degeneracy-witnesses-v1"
MATRIX_DIMENSION = 16
SPLIT_DIMENSION = MATRIX_DIMENSION - 1
BOUNDARY_MATRIX_RANK = 10
BOUNDARY_KERNEL_DIMENSION = 6
LIMITING_KERNEL_DIMENSION = 4
SOURCE_PATHS = (
    HERE / "schur_degeneracy_witnesses.py",
    HERE / "first_order_normal_cones.py",
    HERE / "first-order-normal-cones-result.json",
    HERE / "path_supported_basepoints.py",
    HERE / "path-supported-basepoints-result.json",
    ROOT / "docs" / "design" / "a5-kernel-attachments-program.md",
    NULLITY_EIGHT / "boundary_specializations.py",
    NULLITY_EIGHT / "boundary-specializations-result.json",
    KERNEL_BUNDLES / "kernel_frames.py",
    REGULARITY / "strata_regularity.py",
    EQUATIONS / "rederive_strata_equations.py",
    ROOT / "gororoba_quantum" / "cd_core.py",
)
FIRST_ORDER_RESULT = HERE / "first-order-normal-cones-result.json"
PRIOR_RESULT = NULLITY_EIGHT / "boundary-specializations-result.json"


@dataclass(frozen=True)
class SchurCase:
    record: dict[str, Any]
    limiting_plane: sp.Matrix


@dataclass(frozen=True)
class WitnessAnalysis:
    path: boundary.PathSpec
    record: dict[str, Any]
    limiting_plane: sp.Matrix


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_path(path: Path) -> tuple[str, str]:
    return str(path.relative_to(ROOT)), _sha256(path)


def _fraction_vector(*coordinates: int | Fraction) -> tuple[Fraction, ...]:
    _require(len(coordinates) == SPLIT_DIMENSION, "a split vector needs 15 coordinates")
    return tuple(map(Fraction, coordinates))


def _iso_witnesses() -> tuple[boundary.PathSpec, boundary.PathSpec]:
    point, _paths = basepoints.selected_path_group(basepoints.Incidence("Iso", "VB"))
    first_order = _fraction_vector(1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    second_orders = (
        _fraction_vector(Fraction(1, 2), 1, Fraction(3, 2), 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        _fraction_vector(1, 1, 2, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0),
    )
    return (
        boundary.PathSpec("Iso", "VB", "fixed-degeneracy-second-jet-1", (point, first_order, second_orders[0])),
        boundary.PathSpec("Iso", "VB", "fixed-degeneracy-second-jet-2", (point, first_order, second_orders[1])),
    )


def _w8_witnesses() -> tuple[boundary.PathSpec, boundary.PathSpec]:
    point, _paths = basepoints.selected_path_group(basepoints.Incidence("W8", "VB"))
    first_order = _fraction_vector(0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0)
    second_orders = (
        _fraction_vector(0, 0, Fraction(1, 2), 0, 0, 0, 0, 0, 0, 0, 0, Fraction(1, 2), 0, 0, 0),
        _fraction_vector(0, 0, Fraction(1, 2), 0, 0, 0, 0, 0, 0, 0, 0, Fraction(-1, 2), 0, 0, 0),
    )
    return (
        boundary.PathSpec("W8", "VB", "fixed-degeneracy-second-jet-plus", (point, first_order, second_orders[0])),
        boundary.PathSpec("W8", "VB", "fixed-degeneracy-second-jet-minus", (point, first_order, second_orders[1])),
    )


def _witness_group(incidence: str) -> tuple[boundary.PathSpec, boundary.PathSpec]:
    if incidence == "E8bar->VB":
        paths = boundary._e8_slice_paths()
        return paths[2], paths[3]
    if incidence == "E8bar->Va+":
        paths = boundary._e8_aligned_paths("Va+")
        return paths[0], paths[1]
    if incidence == "E8bar->Va-":
        paths = boundary._e8_aligned_paths("Va-")
        return paths[0], paths[1]
    if incidence == "Iso->VB":
        return _iso_witnesses()
    if incidence == "W8->VB":
        return _w8_witnesses()
    if incidence == "X+->VB":
        paths = boundary._x_vb_paths("X+")
        return paths[0], paths[1]
    if incidence == "X-->VB":
        paths = boundary._x_vb_paths("X-")
        return paths[0], paths[1]
    raise ValueError(f"unknown exceptional incidence {incidence!r}")


def _exceptional_incidence(row: dict[str, Any]) -> str | None:
    if bool(row["degeneracy_locus"]["one_blowup_resolves_first_order_map"]):
        return None
    return str(row["incidence"])


def _schur_case(path: boundary.PathSpec, drop_schur_correction: bool) -> SchurCase:
    first_matrix = boundary._matrix_for_split(path.coefficients[1])
    second_matrix = boundary._matrix_for_split(path.coefficients[2])
    (
        boundary_matrix,
        pivot,
        boundary_frame,
        pivot_determinant,
        pivot_pfaffian,
        pivot_columns,
        pivot_block,
    ) = boundary._boundary_frame_data(path.coefficients[0])
    first_restriction = sp.simplify(boundary_frame.T * first_matrix * boundary_frame)
    first_coupling = first_matrix.extract(pivot, range(MATRIX_DIMENSION)) * boundary_frame
    second_restriction = sp.simplify(boundary_frame.T * second_matrix * boundary_frame)
    schur_correction = sp.simplify(first_coupling.T * pivot_block.inv() * first_coupling)
    effective_form = second_restriction if drop_schur_correction else sp.simplify(second_restriction + schur_correction)
    effective_rank = int(effective_form.rank())
    nullspace = effective_form.nullspace()
    limit_coordinates = sp.Matrix.hstack(*nullspace) if nullspace else sp.zeros(BOUNDARY_KERNEL_DIMENSION, 0)
    limiting_plane = boundary_frame * limit_coordinates
    first_residual_verified = False
    second_residual_verified = False
    if effective_rank == 2:
        first_correction = -pivot_columns * pivot_block.inv() * first_coupling * limit_coordinates
        first_residual = sp.simplify(boundary_matrix * first_correction + first_matrix * limiting_plane)
        second_residual = sp.simplify(first_matrix * first_correction + second_matrix * limiting_plane)
        first_residual_verified = first_residual == sp.zeros(MATRIX_DIMENSION, LIMITING_KERNEL_DIMENSION)
        second_residual_verified = sp.simplify(boundary_frame.T * second_residual) == sp.zeros(
            BOUNDARY_KERNEL_DIMENSION, LIMITING_KERNEL_DIMENSION
        )
    limiting_plane_dimension = int(limiting_plane.rank())
    limiting_plane_inside_boundary_kernel = (
        limiting_plane_dimension == LIMITING_KERNEL_DIMENSION
        and boundary_matrix * limiting_plane == sp.zeros(MATRIX_DIMENSION, LIMITING_KERNEL_DIMENSION)
    )
    passed = (
        int(boundary_matrix.rank()) == BOUNDARY_MATRIX_RANK
        and pivot_determinant == pivot_pfaffian * pivot_pfaffian
        and first_restriction == sp.zeros(BOUNDARY_KERNEL_DIMENSION)
        and effective_form.T == -effective_form
        and effective_rank == 2
        and limiting_plane_dimension == LIMITING_KERNEL_DIMENSION
        and limiting_plane_inside_boundary_kernel
        and first_residual_verified
        and second_residual_verified
    )
    return SchurCase(
        {
            "drop_schur_correction": drop_schur_correction,
            "boundary_bordered_rank": int(boundary_matrix.rank()),
            "boundary_pivot_indices": list(pivot),
            "boundary_pivot_pfaffian": str(pivot_pfaffian),
            "boundary_pivot_determinant": str(pivot_determinant),
            "first_restricted_rank": int(first_restriction.rank()),
            "first_restriction": boundary._matrix_rows(first_restriction),
            "second_restriction": boundary._matrix_rows(second_restriction),
            "schur_correction": boundary._matrix_rows(schur_correction),
            "effective_form": boundary._matrix_rows(effective_form),
            "effective_form_skew": effective_form.T == -effective_form,
            "effective_restricted_rank": effective_rank,
            "limiting_plane_dimension": limiting_plane_dimension,
            "limiting_plane_inside_boundary_kernel": limiting_plane_inside_boundary_kernel,
            "formal_first_residual_verified": first_residual_verified,
            "formal_second_residual_verified": second_residual_verified,
            "limiting_plane_rref": boundary._matrix_rows(limiting_plane.T.rref()[0]),
            "pass": passed,
        },
        limiting_plane,
    )


def _prior_path_row(path: boundary.PathSpec) -> dict[str, Any] | None:
    prior_record = json.loads(PRIOR_RESULT.read_text(encoding="utf-8"))
    for incidence in prior_record["incidences"]:
        if incidence["incidence"] != path.incidence:
            continue
        for approach in incidence["approaches"]:
            if approach["approach"] == path.approach:
                return approach
    return None


def _first_order_row(incidence: str) -> dict[str, Any]:
    first_order_record = json.loads(FIRST_ORDER_RESULT.read_text(encoding="utf-8"))
    return next(row for row in first_order_record["incidences"] if row["incidence"] == incidence)


def _analyze_path(path: boundary.PathSpec) -> WitnessAnalysis:
    source_orbit, boundary_orbit = path.incidence.split("->", maxsplit=1)
    selected_point, _selected_paths = basepoints.selected_path_group(basepoints.Incidence(source_orbit, boundary_orbit))
    boundary_key = basepoints.ORBIT_KEYS.get(boundary_orbit, boundary_orbit)
    slice_columns = tuple(
        regularity.transverse_columns(
            selected_point,
            regularity.COLUMN_ORDER.get(boundary_key, range(SPLIT_DIMENSION)),
        )
    )
    outside_columns = tuple(sorted(set(range(SPLIT_DIMENSION)) - set(slice_columns)))
    path_coefficients = sp.Matrix.hstack(sp.Matrix(path.coefficients[1]), sp.Matrix(path.coefficients[2]))
    path_lies_in_coordinate_slice = path_coefficients.extract(outside_columns, (0, 1)) == sp.zeros(
        len(outside_columns), 2
    )
    slice_symbols = tuple(sp.symbols(f"t1:{len(slice_columns) + 1}"))
    first_order_row = _first_order_row(path.incidence)
    tangent_generators = tuple(
        first_order._sympy_polynomial(text, slice_symbols) for text in first_order_row["tangent_cone"]["generators"]
    )
    boundary_matrix = boundary._matrix_for_split(selected_point)
    pivot = first_order.kernel_frames._find_principal_pivot(boundary_matrix, BOUNDARY_MATRIX_RANK)
    boundary_frame, _pivot_determinant, _pivot_pfaffian = first_order.kernel_frames._principal_frame(
        boundary_matrix, pivot
    )
    effective_form = first_order._effective_form(boundary_frame, slice_columns, slice_symbols)
    first_order_context = first_order.AnalysisContext(
        first_order.Incidence(source_orbit, boundary_orbit),
        selected_point,
        slice_columns,
        slice_symbols,
        boundary_frame,
        effective_form,
        tangent_generators,
    )
    first_order_comparison = first_order._path_comparison(path, first_order_context)
    curve = boundary._curve_certificate(path)
    schur = _schur_case(path, False)
    prior_kernel, prior_plane, _prior_quotient, _prior_boundary = boundary._kernel_limit(path)
    plane_union_dimension = int(sp.Matrix.hstack(schur.limiting_plane, prior_plane).rank())
    prior_path_row = _prior_path_row(path)
    retained_plane_matches = None
    if prior_path_row is not None:
        retained_plane_matches = (
            schur.record["limiting_plane_rref"] == prior_path_row["kernel_limit"]["limiting_plane_rref"]
        )
    passed = (
        path.coefficients[0] == selected_point
        and bool(curve["pass"])
        and bool(first_order_comparison["pass"])
        and bool(first_order_comparison["direction_in_tangent_cone"])
        and first_order_comparison["first_order_effective_rank"] == 0
        and any(coordinate != "0" for coordinate in first_order_comparison["normal_coordinates"])
        and bool(schur.record["pass"])
        and bool(prior_kernel["pass"])
        and plane_union_dimension == LIMITING_KERNEL_DIMENSION
        and retained_plane_matches is not False
    )
    row = {
        "incidence": path.incidence,
        "approach": path.approach,
        "boundary_point_matches_path_supported_certificate": path.coefficients[0] == selected_point,
        "slice_columns_zero_based": list(slice_columns),
        "path_lies_in_coordinate_slice": path_lies_in_coordinate_slice,
        "normal_projection": {
            "coordinates": first_order_comparison["normal_coordinates"],
            "direction_in_tangent_cone": first_order_comparison["direction_in_tangent_cone"],
            "first_order_effective_rank": first_order_comparison["first_order_effective_rank"],
            "projectively_nonzero": any(
                coordinate != "0" for coordinate in first_order_comparison["normal_coordinates"]
            ),
        },
        "first_order_split_coefficients": list(map(str, path.coefficients[1])),
        "second_order_split_coefficients": list(map(str, path.coefficients[2])),
        "curve": curve,
        "schur": schur.record,
        "recomputed_prior_limit_pass": prior_kernel["pass"],
        "recomputed_prior_plane_union_dimension": plane_union_dimension,
        "retained_record_contains_approach": prior_path_row is not None,
        "retained_record_plane_matches": retained_plane_matches,
        "pass": passed,
    }
    return WitnessAnalysis(path, row, schur.limiting_plane)


def _compare_pair(pair: tuple[WitnessAnalysis, WitnessAnalysis]) -> dict[str, Any]:
    first, second = pair
    _require(first.path.incidence == second.path.incidence, "comparison paths belong to different incidences")
    first_directions = sp.Matrix.hstack(sp.Matrix(first.path.coefficients[1]), sp.Matrix(second.path.coefficients[1]))
    plane_union_dimension = int(sp.Matrix.hstack(first.limiting_plane, second.limiting_plane).rank())
    plane_intersection_dimension = 2 * LIMITING_KERNEL_DIMENSION - plane_union_dimension
    return {
        "incidence": first.path.incidence,
        "first_approach": first.path.approach,
        "second_approach": second.path.approach,
        "same_projective_first_direction": int(first_directions.rank()) == 1,
        "same_second_order_coefficient": first.path.coefficients[2] == second.path.coefficients[2],
        "limiting_plane_union_dimension": plane_union_dimension,
        "limiting_plane_intersection_dimension": plane_intersection_dimension,
        "limiting_planes_equal": plane_union_dimension == LIMITING_KERNEL_DIMENSION,
        "pass": bool(first.record["pass"])
        and bool(second.record["pass"])
        and LIMITING_KERNEL_DIMENSION <= plane_union_dimension <= 2 * LIMITING_KERNEL_DIMENSION,
    }


def build_record() -> dict[str, Any]:
    first_order_record = json.loads(FIRST_ORDER_RESULT.read_text(encoding="utf-8"))
    exceptional_candidates = parallel.ordered_map(
        _exceptional_incidence, tuple(first_order_record["incidences"]), min_items=1
    )
    exceptional_incidences = tuple(filter(None, exceptional_candidates))
    witness_groups = parallel.ordered_map(_witness_group, exceptional_incidences, min_items=1)
    witness_paths = tuple(itertools.chain.from_iterable(witness_groups))
    witness_analyses = parallel.ordered_map(_analyze_path, witness_paths, min_items=1)
    comparison_tasks = tuple(zip(witness_analyses[::2], witness_analyses[1::2], strict=True))
    comparisons = parallel.ordered_map(_compare_pair, comparison_tasks, min_items=1)
    mutation_target = next(
        analysis.path
        for analysis in witness_analyses
        if analysis.path.incidence == "E8bar->Va+" and analysis.path.approach == "middle-coordinate-sheet-+1"
    )
    mutation_cases = parallel.ordered_map(partial(_schur_case, mutation_target), (False, True), min_items=1)
    mutation_baseline, mutation_dropped = mutation_cases
    mutation_detected = (
        bool(mutation_baseline.record["pass"])
        and not bool(mutation_dropped.record["pass"])
        and mutation_baseline.record["effective_restricted_rank"]
        != mutation_dropped.record["effective_restricted_rank"]
    )
    input_rows = parallel.ordered_map(_hash_path, SOURCE_PATHS, min_items=1)
    passed = (
        len(exceptional_incidences) == len(witness_groups)
        and all(bool(analysis.record["pass"]) for analysis in witness_analyses)
        and all(bool(comparison["pass"]) for comparison in comparisons)
        and mutation_detected
    )
    return {
        "schema": SCHEMA,
        "inputs": dict(input_rows),
        "tools": {"sympy": sp.__version__},
        "scope": {
            "passage": "the seven exceptional nullity-8 to nullity-12 first-order rows",
            "claim_boundary": (
                "The record supplies two exact degree-at-most-two arcs per incidence, proves that each normal "
                "projection lies on the coordinate-slice first-order degeneracy locus, and computes the actual "
                "arc's Schur-corrected limit. It is a lower-bound witness family, not a classification of the full "
                "formal slice image or a two-sided curve-selection certificate."
            ),
        },
        "summary": {
            "exceptional_incidence_count": len(exceptional_incidences),
            "quadratic_witness_count": len(witness_analyses),
            "equal_plane_pair_count": sum(bool(comparison["limiting_planes_equal"]) for comparison in comparisons),
            "unequal_plane_pair_count": sum(
                not bool(comparison["limiting_planes_equal"]) for comparison in comparisons
            ),
            "same_first_direction_unequal_plane_count": sum(
                bool(comparison["same_projective_first_direction"]) and not bool(comparison["limiting_planes_equal"])
                for comparison in comparisons
            ),
        },
        "exceptional_incidences": list(exceptional_incidences),
        "witnesses": [analysis.record for analysis in witness_analyses],
        "pair_comparisons": comparisons,
        "mutation_control": {
            "name": "drop_second_order_schur_correction",
            "target": f"{mutation_target.incidence}:{mutation_target.approach}",
            "input_change": "replace D_2+C_1^T*B_0^-1*C_1 by D_2",
            "baseline": mutation_baseline.record,
            "mutated": mutation_dropped.record,
            "detected": mutation_detected,
        },
        "falsifier": (
            "An exceptional row lacks a projectively nonzero degenerate direction; an admitted quadratic arc leaves "
            "the source closure; a Schur form is non-skew or has rank outside zero or two; a retained second-order "
            "limit disagrees; a pairwise plane equality disagrees with its exact union rank; the witness family is "
            "misrepresented as a full curve-selection image; or the Schur-block mutation survives."
        ),
        "pass": passed,
    }


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _self_test(record: dict[str, Any]) -> None:
    _require(bool(record["pass"]), "the Schur-degeneracy witness record failed")
    _require(bool(record["mutation_control"]["detected"]), "the Schur-block mutation survived")
    w8_comparison = next(comparison for comparison in record["pair_comparisons"] if comparison["incidence"] == "W8->VB")
    _require(bool(w8_comparison["same_projective_first_direction"]), "the W8 witness directions differ")
    _require(not bool(w8_comparison["limiting_planes_equal"]), "the W8 second jets gave the same plane")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write the deterministic JSON record")
    parser.add_argument("--check", type=Path, help="compare a deterministic record byte for byte")
    parser.add_argument("--self-test", action="store_true", help="run the baseline and mutation checks")
    arguments = parser.parse_args()
    selected_modes = sum((arguments.out is not None, arguments.check is not None, arguments.self_test))
    if selected_modes != 1:
        parser.error("select exactly one of --out, --check, or --self-test")
    record = build_record()
    _self_test(record)
    rendered = _record_bytes(record)
    if arguments.out is not None:
        arguments.out.write_bytes(rendered)
    elif arguments.check is not None:
        retained = arguments.check.read_bytes()
        _require(
            retained == rendered,
            f"record mismatch: retained={hashlib.sha256(retained).hexdigest()} "
            f"fresh={hashlib.sha256(rendered).hexdigest()}",
        )


if __name__ == "__main__":
    main()
