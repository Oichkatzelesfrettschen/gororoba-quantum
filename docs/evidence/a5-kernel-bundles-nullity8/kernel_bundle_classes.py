"""Producer-bound inputs for the nullity-eight kernel-bundle classes.

The producer derives representation multiplicities, external-circle
projections, exact phase periodicity, K-class residues, and boundary-sheet
comparisons from retained exact records.  Associated-bundle identifications,
Kunneth arguments, and ordinary bundle conclusions remain explicitly inferred.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import sys
from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any, TypeAlias

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KERNEL_BUNDLES = HERE.parent / "a5-kernel-bundles"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(KERNEL_BUNDLES))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import kernel_symmetry as symmetry  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-bundles-nullity8-classes-v1"
ORBIT_NAMES = ("W8", "E8bar", "Iso", "X+", "X-")
DISPLAY_NAMES = {"W8": "W8", "E8bar": "E8-bar", "Iso": "Iso", "X+": "X_+", "X-": "X_-"}
MUTATIONS = ("", "add_e8_doublet", "kill_stiefel_torsion", "break_phase_period", "remove_e8_path_dependence")

INPUT_SPECS = {
    "topology": (
        HERE / "unit-section-topology-result.json",
        HERE / "unit_section_topology.py",
        "a5-kernel-bundles-nullity8-unit-section-topology-v1",
    ),
    "fiber_samples": (
        HERE / "stabilizer-fiber-samples-result.json",
        HERE / "stabilizer_fiber_samples.py",
        "a5-kernel-bundles-nullity8-stabilizer-fiber-samples-v1",
    ),
    "stabilizer_strata": (
        HERE / "stabilizer-strata-result.json",
        HERE / "stabilizer_strata.py",
        "a5-kernel-bundles-nullity8-stabilizer-strata-v1",
    ),
    "transition_atlas": (
        HERE / "kernel-transition-atlas-result.json",
        HERE / "kernel_transition_atlas.py",
        "a5-kernel-bundles-nullity8-transition-atlas-v1",
    ),
    "boundary": (
        HERE / "boundary-specializations-result.json",
        HERE / "boundary_specializations.py",
        "a5-kernel-bundles-nullity8-boundary-specializations-v1",
    ),
    "nullity_sixteen": (
        KERNEL_BUNDLES / "nullity-sixteen-bundle-result.json",
        KERNEL_BUNDLES / "nullity_sixteen_bundle.py",
        "a5-nullity-sixteen-bundle-invariants-v2",
    ),
    "kernel_symmetry": (
        KERNEL_BUNDLES / "result.json",
        KERNEL_BUNDLES / "kernel_symmetry.py",
        "a5-kernel-symmetry-v3",
    ),
}

RationalMatrix: TypeAlias = symmetry.RationalMatrix


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_inputs(mutation: str) -> tuple[dict[str, dict[str, Any]], dict[str, str], dict[str, Any]]:
    if mutation not in MUTATIONS:
        raise ValueError(f"unknown bundle-class mutation {mutation!r}")
    loaded: dict[str, dict[str, Any]] = {}
    digests: dict[str, str] = {}
    for name, (result_path, script_path, schema) in INPUT_SPECS.items():
        result = json.loads(result_path.read_text(encoding="utf-8"))
        script_digest = _sha256(script_path)
        _require(result.get("schema") == schema, f"{result_path.name} has an unexpected schema")
        _require(result.get("pass") is True, f"{result_path.name} does not pass")
        relative_script = str(script_path.relative_to(ROOT))
        recorded_digest = result.get("script_sha256")
        if recorded_digest is None:
            recorded_digest = result.get("source_sha256")
        if recorded_digest is None:
            recorded_digest = result.get("inputs", {}).get(relative_script)
        _require(recorded_digest == script_digest, f"{result_path.name} is stale against {script_path.name}")
        loaded[name] = result
        digests[f"{name}_result_sha256"] = _sha256(result_path)
        digests[f"{name}_script_sha256"] = script_digest

    mutated = copy.deepcopy(loaded)
    mutation_record: dict[str, Any] = {"name": mutation or None, "target": None}
    if mutation == "add_e8_doublet":
        row = next(
            value
            for value in mutated["fiber_samples"]["rows"]
            if value["orbit"] == "E8bar" and value["move"] == "representative"
        )
        doublet = next(
            value for value in row["representation"]["irreducible_decomposition"] if value["highest_weight"] == 1
        )
        doublet["multiplicity"] += 1
        doublet["joint_dimension"] += doublet["irreducible_dimension"]
        mutation_record["target"] = "E8-bar standard-doublet multiplicity"
    elif mutation == "kill_stiefel_torsion":
        mutated["nullity_sixteen"]["bundle"]["representation_ring_k_theory"]["generator_order"] = 1
        mutation_record["target"] = "Stiefel reduced K-generator order"
    elif mutation == "break_phase_period":
        mutated["kernel_symmetry"]["lie_algebra"]["decomposition"]["base_phase_lift"] = 0
        mutation_record["target"] = "constant base-phase lift multiplicity"
    elif mutation == "remove_e8_path_dependence":
        incidence = next(value for value in mutated["boundary"]["incidences"] if value["incidence"] == "E8bar->B9")
        reference_plane = copy.deepcopy(incidence["approaches"][0]["kernel_limit"]["limiting_plane_rref"])
        for approach in incidence["approaches"]:
            approach["kernel_limit"]["limiting_plane_rref"] = copy.deepcopy(reference_plane)
        mutation_record["target"] = incidence["incidence"]
    return mutated, digests, mutation_record


def _identity_matrix(dimension: int, sign: int = 1) -> RationalMatrix:
    return tuple(
        tuple(Fraction(sign if row == column else 0) for column in range(dimension)) for row in range(dimension)
    )


def _phase_certificate(kernel_symmetry: dict[str, Any], mutation: str) -> dict[str, Any]:
    right_j = symmetry._basis_right_matrix(symmetry.HALF_DIMENSION)
    if mutation == "break_phase_period":
        mutable = [list(row) for row in right_j]
        changed = False
        for row in range(symmetry.DIMENSION):
            for column in range(symmetry.DIMENSION):
                if mutable[row][column] and not changed:
                    mutable[row][column] = -mutable[row][column]
                    changed = True
        _require(changed, "phase mutation found no nonzero right-multiplication entry")
        right_j = tuple(tuple(row) for row in mutable)
    square = symmetry._matrix_product(right_j, right_j)
    negative_identity = _identity_matrix(symmetry.DIMENSION, -1)
    phase_lift_multiplicity = int(kernel_symmetry["lie_algebra"]["decomposition"]["base_phase_lift"])
    return {
        "right_phase_square_is_negative_identity": square == negative_identity,
        "base_phase_lift_multiplicity": phase_lift_multiplicity,
        "period": "2 pi" if square == negative_identity else "mutation broke the complex structure",
        "pass": square == negative_identity and phase_lift_multiplicity == 1,
    }


def _representation_counts(fiber_samples: dict[str, Any]) -> dict[str, dict[str, Any]]:
    representative_rows = [row for row in fiber_samples["rows"] if row["move"] == "representative"]
    core_rows = fiber_samples["mostow_adapted_core_rows"]
    output: dict[str, dict[str, Any]] = {}
    for orbit in ("W8", "E8bar", "X+", "X-"):
        source_rows = core_rows if orbit in ("X+", "X-") else representative_rows
        row = next(value for value in source_rows if value["orbit"] == orbit)
        decomposition = row["representation"]["irreducible_decomposition"]
        trivial_lines = sum(int(value["multiplicity"]) for value in decomposition if int(value["highest_weight"]) == 0)
        standard_doublets = sum(
            int(value["multiplicity"]) for value in decomposition if int(value["highest_weight"]) == 1
        )
        unsupported = [value for value in decomposition if int(value["highest_weight"]) not in (0, 1)]
        commutant_dimension = sum(int(value["multiplicity"]) ** 2 for value in decomposition)
        output[orbit] = {
            "trivial_lines": trivial_lines,
            "standard_doublets": standard_doublets,
            "complex_dimension": trivial_lines + 2 * standard_doublets,
            "commutant_dimension": commutant_dimension,
            "equivariant_automorphism_group": " x ".join(
                f"GL({int(value['multiplicity'])},C)" for value in decomposition
            ),
            "equivariant_automorphism_group_connected": not unsupported,
            "source_decomposition": row["representation"]["decomposition"],
            "source_point": row["move"],
            "unsupported_irreducibles": unsupported,
        }
    return output


def _integer_pair(row: Sequence[str]) -> tuple[int, int]:
    values = tuple(Fraction(value) for value in row)
    _require(all(value.denominator == 1 for value in values), "external projection row is not integral")
    return int(values[0]), int(values[1])


def _external_circle_data(topology: dict[str, Any]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    component_rows = {row["orbit"]: row for row in topology["compact_stabilizer_components"]}
    for row in topology["complex_stabilizers"]:
        orbit = str(row["orbit"])
        nonzero_rows = [
            _integer_pair(value) for value in row["external_torus_projection_rows"] if any(_integer_pair(value))
        ]
        primitive_rows = []
        for first, second in nonzero_rows:
            divisor = math.gcd(abs(first), abs(second))
            primitive_rows.append((first // divisor, second // divisor))
        phase_supplies_quotient = False
        if len(primitive_rows) == 1:
            first, second = primitive_rows[0]
            phase_supplies_quotient = abs(-second) == 1
        output[orbit] = {
            "external_projection_rank": int(row["external_torus_projection_rank"]),
            "nonzero_projection_rows": [list(value) for value in nonzero_rows],
            "primitive_projection_rows": [list(value) for value in primitive_rows],
            "phase_circle_supplies_primitive_quotient": phase_supplies_quotient,
            "full_compact_external_image": component_rows[orbit]["external_image"],
            "compact_stabilizer_component_group": component_rows[orbit]["component_group"],
            "full_compact_component_certificate_passes": component_rows[orbit]["pass"],
        }
    return output


def _limiting_plane_from_approach(approach: dict[str, Any]) -> sp.Matrix:
    return sp.Matrix(
        [
            [sp.sympify(value, locals={"I": sp.I}) for value in row]
            for row in approach["kernel_limit"]["limiting_plane_rref"]
        ]
    )


def _planes_equal(first: sp.Matrix, second: sp.Matrix) -> bool:
    return first.rank() == 4 and second.rank() == 4 and sp.Matrix.vstack(first, second).rank() == 4


def _sheet_data(boundary: dict[str, Any]) -> dict[str, Any]:
    incidences = [value for value in boundary["incidences"] if value["high_orbit"] == "E8bar"]
    recomputed_rows = []
    for incidence in incidences:
        approaches = incidence["approaches"]
        planes = [_limiting_plane_from_approach(approach) for approach in approaches]
        path_dependent = any(
            not _planes_equal(planes[left_index], planes[right_index])
            for left_index in range(len(planes))
            for right_index in range(left_index + 1, len(planes))
        )
        sheet_indices = [
            index
            for index, approach in enumerate(approaches)
            if str(approach["approach"]).startswith("middle-coordinate-sheet")
        ]
        sheet_limits_equal = None
        if len(sheet_indices) == 2:
            sheet_limits_equal = _planes_equal(planes[sheet_indices[0]], planes[sheet_indices[1]])
        recomputed_rows.append(
            {
                "incidence": incidence["incidence"],
                "path_dependent": path_dependent,
                "recorded_path_dependent": incidence["comparison"]["path_dependent"],
                "recorded_comparison_matches": path_dependent == incidence["comparison"]["path_dependent"],
                "sheet_limits_equal": sheet_limits_equal,
            }
        )
    sheet_rows = [row for row in recomputed_rows if row["sheet_limits_equal"] is not None]
    return {
        "incidence_count": len(incidences),
        "path_dependent_incidence_count": sum(bool(row["path_dependent"]) for row in recomputed_rows),
        "recorded_comparisons_match_recomputed_planes": all(
            row["recorded_comparison_matches"] for row in recomputed_rows
        ),
        "explicit_middle_coordinate_sheet_comparisons": len(sheet_rows),
        "explicit_middle_coordinate_sheet_limits_equal": all(row["sheet_limits_equal"] for row in sheet_rows),
        "incidences": recomputed_rows,
    }


def _zero_characteristic_classes(complex_rank: int, reason: str) -> dict[str, Any]:
    return {
        "status": "inferred",
        "reason": reason,
        "total_chern_class": "1",
        "chern_coefficients_c0_through_c4": [1, *([0] * complex_rank)],
        "underlying_real_total_stiefel_whitney_class": "1",
        "underlying_real_total_pontryagin_class": "1",
    }


def _classification_row(task: tuple[str, dict[str, dict[str, Any]], int]) -> dict[str, Any]:
    orbit, representations, generator_order = task
    display_name = DISPLAY_NAMES[orbit]
    if orbit == "Iso":
        return {
            "orbit": display_name,
            "row_status": "inferred from the graph-torus section and standard topology inputs",
            "compact_core": "G_2",
            "ordinary_complex_bundle": "C^4",
            "ordinary_classification": "trivial",
            "ordinary_classification_status": "inferred from the graph-torus section",
            "reduced_K0": "Z",
            "reduced_K0_status": "inferred from the Hodgkin K-group input",
            "reduced_K_class": {"status": "inferred", "free": [0], "torsion": []},
            "structure_group_reduction": "identity after the graph-section trivialization",
            "structure_group_reduction_status": "inferred",
            "underlying_real_bundle": "R^8",
            "underlying_real_bundle_status": "inferred",
            "underlying_real_bundle_reason": "the graph-section trivializes the complex rank-four bundle",
            "characteristic_classes": _zero_characteristic_classes(4, "the graph-section trivialization"),
        }

    representation = representations[orbit]
    trivial_lines = int(representation["trivial_lines"])
    doublets = int(representation["standard_doublets"])
    residue = doublets % generator_order
    if orbit == "E8bar":
        compact_core = "V_2(R^7) x T^2"
        reduced_group = "Z^3 + (Z/2)^2"
        class_coordinates = {"status": "inferred", "free": [0, 0, 0], "torsion": [residue, 0]}
    else:
        compact_core = "V_2(R^7) x S^1"
        reduced_group = "Z + Z/2"
        class_coordinates = {"status": "inferred", "free": [0], "torsion": [residue]}
    doublet_term = "xi" if doublets == 1 else f"{doublets} xi"
    ordinary_bundle = doublet_term if trivial_lines == 0 else f"C^{trivial_lines} + {doublet_term}"
    if residue:
        ordinary_type = "complex nontrivial because its reduced K-class is nonzero"
    else:
        ordinary_type = "ordinary class retained as 2 xi; stable triviality does not cancel in rank four"
    real_bundle = "2 xi_R; stably trivial, with actual triviality not inferred"
    real_bundle_reason = "realification of the associated bundle; stable K-theory does not prove actual triviality"
    if trivial_lines == 2 and doublets == 1:
        real_bundle = "R^4 + xi_R = R^8"
        real_bundle_reason = (
            "xi_R is the orthogonal complement of the associative plane span(x_1,x_2,x_1 x_2), so "
            "xi_R + span(x_1,x_2,x_1 x_2)=R^7 and one further trivial line gives R^4+xi_R=R^8"
        )
    reduction = (
        "diagonal SU(2)=Sp(1) inside Sp(2) and SU(4)"
        if trivial_lines == 0
        else "SU(2) as diag(I_2,Q) inside Sp(2) and SU(4) after pairing the two trivial lines"
    )
    return {
        "orbit": display_name,
        "row_status": "inferred from observed representation multiplicities and standard topology inputs",
        "compact_core": compact_core,
        "fiber_representation": representation["source_decomposition"],
        "ordinary_complex_bundle": ordinary_bundle,
        "ordinary_classification": ordinary_type,
        "ordinary_classification_status": "inferred from the compact-core associated bundle and circle pullback",
        "reduced_K0": reduced_group,
        "reduced_K0_status": "inferred from Kunneth and the committed Stiefel K-groups",
        "reduced_K_class": class_coordinates,
        "stiefel_torsion_generator_order": generator_order,
        "stiefel_torsion_residue": residue,
        "structure_group_reduction": reduction,
        "structure_group_reduction_status": "inferred from the associated representation",
        "underlying_real_bundle": real_bundle,
        "underlying_real_bundle_status": "inferred",
        "underlying_real_bundle_reason": real_bundle_reason,
        "characteristic_classes": _zero_characteristic_classes(
            4,
            "xi has SU(2) structure, its c2 pulls back from H^4(V_2(R^7))=0, and the external multiplicity bundles "
            "are trivial",
        ),
    }


def class_checks(mutation: str = "") -> dict[str, Any]:
    inputs, input_digests, mutation_record = _load_inputs(mutation)
    phase = _phase_certificate(inputs["kernel_symmetry"], mutation)
    representations = _representation_counts(inputs["fiber_samples"])
    external = _external_circle_data(inputs["topology"])
    sheets = _sheet_data(inputs["boundary"])
    generator_order = int(inputs["nullity_sixteen"]["bundle"]["representation_ring_k_theory"]["generator_order"])
    rows = parallel.ordered_map(
        _classification_row,
        [(orbit, representations, generator_order) for orbit in ORBIT_NAMES],
        min_items=1,
    )
    rows_by_orbit = {row["orbit"]: row for row in rows}
    topology_models = {row["orbit"]: row["maximal_compact_core"] for row in inputs["topology"]["orbit_models"]}
    transition_rows = inputs["transition_atlas"]["rows"]
    observed_checks = {
        "all_transition_rows_have_rank_four": all(
            row["matrix_rank"] == 12 and row["complex_kernel_rank"] == 4 and row["pass"] for row in transition_rows
        ),
        "transition_metric_reduction_is_U4": inputs["transition_atlas"]["structure_group"]["metric_reduction"]
        == "U(4)",
        "topology_models_match": topology_models
        == {
            "W8": "V_2(R^7) x S^1",
            "E8bar": "V_2(R^7) x T^2",
            "Iso": "G_2",
            "X+": "V_2(R^7) x S^1",
            "X-": "V_2(R^7) x S^1",
        },
        "fiber_dimensions_are_four": all(row["complex_dimension"] == 4 for row in representations.values()),
        "W8_has_two_doublets": representations["W8"]["standard_doublets"] == 2
        and representations["W8"]["trivial_lines"] == 0,
        "E8_and_X_have_two_lines_plus_one_doublet": all(
            representations[orbit]["standard_doublets"] == 1 and representations[orbit]["trivial_lines"] == 2
            for orbit in ("E8bar", "X+", "X-")
        ),
        "equivariant_automorphism_groups_connected": all(
            row["equivariant_automorphism_group_connected"] for row in representations.values()
        ),
        "phase_lift_is_periodic": phase["pass"],
        "full_compact_component_certificates_pass": all(
            row["full_compact_component_certificate_passes"] for row in external.values()
        ),
        "W8_has_two_phase_components": external["W8"]["full_compact_external_image"]
        == "{phase=+1,phase=-1} x S^1_boost"
        and external["W8"]["compact_stabilizer_component_group"] == "Z/2",
        "E8_external_image_is_identity": external["E8bar"]["full_compact_external_image"] == "identity"
        and external["E8bar"]["compact_stabilizer_component_group"] == "0",
        "Iso_external_image_is_connected_two_torus": external["Iso"]["full_compact_external_image"]
        == "S^1_phase x S^1_boost"
        and external["Iso"]["compact_stabilizer_component_group"] == "0",
        "X_external_images_are_connected_graph_circles": external["X+"]["compact_stabilizer_component_group"] == "0"
        and external["X-"]["compact_stabilizer_component_group"] == "0"
        and external["X+"]["full_compact_external_image"] == "phase+boost=0 graph circle"
        and external["X-"]["full_compact_external_image"] == "boost-phase=0 graph circle",
        "stiefel_generator_has_order_two": generator_order == 2,
        "stable_residues_match": rows_by_orbit["W8"]["stiefel_torsion_residue"] == 0
        and rows_by_orbit["E8-bar"]["stiefel_torsion_residue"] == 1
        and rows_by_orbit["X_+"]["stiefel_torsion_residue"] == 1
        and rows_by_orbit["X_-"]["stiefel_torsion_residue"] == 1,
        "all_E8_boundary_incidences_are_path_dependent": sheets["incidence_count"] == 5
        and sheets["path_dependent_incidence_count"] == 5,
        "recorded_E8_comparisons_match_recomputed_planes": sheets["recorded_comparisons_match_recomputed_planes"],
        "aligned_sheet_normal_limits_agree": sheets["explicit_middle_coordinate_sheet_comparisons"] == 2
        and sheets["explicit_middle_coordinate_sheet_limits_equal"],
    }
    return {
        "mutation": mutation_record,
        "input_digests": input_digests,
        "phase_certificate": phase,
        "representation_inputs": representations,
        "external_circle_inputs": external,
        "sheet_inputs": sheets,
        "stiefel_generator_order": generator_order,
        "pieces": rows,
        "torsion_propagation": {
            "status": "inferred",
            "statement": (
                "the order-two Stiefel class occurs on E8-bar, X_+, and X_-; W8 contains two copies and has zero "
                "reduced complex K-class, while Iso is trivial"
            ),
        },
        "E8_sheet_behavior": {
            "status": "inferred",
            "abstract_bundle_class": (
                "both local sheets restrict the single global pullback class C^2+xi; external torus directions add "
                "no Kunneth cross-term"
            ),
            "attaching_data_status": (
                "not computed: path dependence proves the datum is not one inclusion, but the full limit set in "
                "Gr(4,K_0) remains unknown"
            ),
        },
        "inference_scope": (
            "The pass flag covers producer bindings, ranks, representation multiplicities, phase periodicity, "
            "external projections, K-residue arithmetic, and boundary comparisons. Associated-bundle "
            "identifications, graph-section triviality, Kunneth pullbacks, and ordinary equivalence statements are "
            "written mathematical arguments."
        ),
        "observed_checks": observed_checks,
        "pass": all(observed_checks.values()),
    }


def _mutation_task(mutation: str) -> tuple[str, dict[str, Any]]:
    return mutation, class_checks(mutation)


def build_record() -> dict[str, Any]:
    records = dict(parallel.ordered_map(_mutation_task, list(MUTATIONS), min_items=1))
    baseline = records[""]
    mutations = {mutation: records[mutation] for mutation in MUTATIONS if mutation}
    mutation_control = {
        "add_e8_doublet": {
            "detected": not mutations["add_e8_doublet"]["pass"],
            "fiber_dimension_changed": not mutations["add_e8_doublet"]["observed_checks"]["fiber_dimensions_are_four"],
        },
        "kill_stiefel_torsion": {
            "detected": not mutations["kill_stiefel_torsion"]["pass"],
            "E8_residue_changed": next(
                row for row in mutations["kill_stiefel_torsion"]["pieces"] if row["orbit"] == "E8-bar"
            )["stiefel_torsion_residue"]
            == 0,
        },
        "break_phase_period": {
            "detected": not mutations["break_phase_period"]["pass"],
            "phase_square_changed": not mutations["break_phase_period"]["phase_certificate"][
                "right_phase_square_is_negative_identity"
            ],
        },
        "remove_e8_path_dependence": {
            "detected": not mutations["remove_e8_path_dependence"]["pass"],
            "path_count_changed": mutations["remove_e8_path_dependence"]["sheet_inputs"][
                "path_dependent_incidence_count"
            ]
            == 4,
        },
    }
    return {
        "schema": SCHEMA,
        "script_sha256": _sha256(Path(__file__)),
        **baseline,
        "mutation_control": mutation_control,
        "pass": baseline["pass"]
        and all(value["detected"] for value in mutation_control.values())
        and all(
            value[key]
            for value, key in (
                (mutation_control["add_e8_doublet"], "fiber_dimension_changed"),
                (mutation_control["kill_stiefel_torsion"], "E8_residue_changed"),
                (mutation_control["break_phase_period"], "phase_square_changed"),
                (mutation_control["remove_e8_path_dependence"], "path_count_changed"),
            )
        ),
    }


def self_test() -> None:
    record = build_record()
    _require(record["pass"], "baseline bundle classes or a mutation control failed")
    _require(
        record["mutation_control"]["add_e8_doublet"]["fiber_dimension_changed"],
        "E8-bar representation mutation left the fiber dimension unchanged",
    )
    _require(
        record["mutation_control"]["kill_stiefel_torsion"]["E8_residue_changed"],
        "Stiefel torsion mutation left the E8-bar residue unchanged",
    )
    _require(
        record["mutation_control"]["break_phase_period"]["phase_square_changed"],
        "phase mutation left the exact square unchanged",
    )
    _require(
        record["mutation_control"]["remove_e8_path_dependence"]["path_count_changed"],
        "boundary mutation left the E8-bar path-dependence count unchanged",
    )


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--out", type=Path)
    output.add_argument("--check", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        self_test()
    if arguments.out is not None:
        arguments.out.write_bytes(_record_bytes(build_record()))
    if arguments.check is not None:
        fresh = _record_bytes(build_record())
        if fresh != arguments.check.read_bytes():
            raise SystemExit(f"{Path(__file__).name}: fresh JSON differs byte-for-byte from {arguments.check}")
    if arguments.out is None and arguments.check is None and not arguments.self_test:
        parser.error("choose --out, --check, or --self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
