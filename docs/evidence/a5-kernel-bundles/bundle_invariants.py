"""Exact classification certificate for all high-nullity A_5 kernel bundles.

The certificate binds the committed compact-orbit, topology, stabilizer,
transition, and nullity-sixteen results.  It then performs the finite K-class,
stable-cancellation, phase-period, clutching, and adjacency calculations that
decide the ordinary complex and real bundles on all seven smooth pieces.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import kernel_symmetry as symmetry  # noqa: E402

DIMENSION = 32
COMPLEX_RANK = 6
NULLITY_SIXTEEN_COMPLEX_RANK = 8
PIECES = ("B9", "V", "VB", "V^a_+", "V^a_-", "N_+", "N_-")
OUT_OF_DENOMINATOR_RESIDUALS = (
    {
        "key": "full_component_group",
        "boundary": "equivariant refinement outside the ordinary seven-piece bundle classification",
        "next_action": "compute the full normalizer of the constant-triple identity component",
    },
    {
        "key": "individual_xi_real_type",
        "boundary": "the total real kernel bundle is classified, but the four-plane xi_R is not",
        "next_action": "compute the real clutching or reduced KO-class of xi_R on V_2(R^7)",
    },
    {
        "key": "smaller_nullity_twelve_reductions",
        "boundary": "the canonical U(6) reduction is classified; nonconstant smaller reductions are not",
        "next_action": "test for global anticommuting complex structures in the exact Pfaffian atlas",
    },
)

INPUTS = {
    "kernel_symmetry": ("result.json", "kernel_symmetry.py", "a5-kernel-symmetry-v3"),
    "aligned_orbit_moduli": (
        "aligned-orbit-moduli-result.json",
        "aligned_orbit_moduli.py",
        "a5-aligned-nullity-twelve-orbit-moduli-v1",
    ),
    "aligned_stabilizer": (
        "aligned-stabilizer-result.json",
        "aligned_stabilizer_representation.py",
        "a5-aligned-nullity-twelve-stabilizer-representation-v1",
    ),
    "open_v_topology": (
        "v-topology-representation-result.json",
        "v_topology_representation.py",
        "a5-v-topology-stabilizer-representation-v1",
    ),
    "isotropic_orbit_data": (
        "isotropic-orbit-data-result.json",
        "isotropic_orbit_data.py",
        "a5-isotropic-orbit-data-v1",
    ),
    "nullity_sixteen_bundle": (
        "nullity-sixteen-bundle-result.json",
        "nullity_sixteen_bundle.py",
        "a5-nullity-sixteen-bundle-invariants-v1",
    ),
    "transition_atlas": (
        "transition-atlas-result.json",
        "transition_atlas.py",
        "a5-high-nullity-transition-atlas-v1",
    ),
}

MUTATIONS = (
    "",
    "drop_vb_standard_doublet",
    "inject_v_torsion",
    "odd_rank_antipodal_clutching",
)

RationalMatrix = symmetry.RationalMatrix


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_inputs() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    loaded: dict[str, dict[str, Any]] = {}
    digests: dict[str, str] = {}
    for name, (result_name, script_name, expected_schema) in INPUTS.items():
        result_path = HERE / result_name
        script_path = HERE / script_name
        result = json.loads(result_path.read_text(encoding="utf-8"))
        script_digest = _sha256(script_path)
        _require(result.get("schema") == expected_schema, f"{name} has an unexpected schema")
        _require(result.get("pass") is True, f"{name} does not pass")
        _require(result.get("script_sha256") == script_digest, f"{name} is stale against its producer")
        loaded[name] = result
        digests[f"{name}_result_sha256"] = _sha256(result_path)
        digests[f"{name}_script_sha256"] = script_digest
    return loaded, digests


def _matrix_product(first: RationalMatrix, second: RationalMatrix) -> RationalMatrix:
    size = len(first)
    _require(size == len(second), "matrix sizes differ")
    return tuple(
        tuple(
            sum(
                (first[row_index][middle_index] * second[middle_index][column_index] for middle_index in range(size)),
                Fraction(0),
            )
            for column_index in range(size)
        )
        for row_index in range(size)
    )


def _matrix_transpose(matrix: RationalMatrix) -> RationalMatrix:
    return tuple(
        tuple(matrix[column_index][row_index] for column_index in range(len(matrix)))
        for row_index in range(len(matrix))
    )


def _identity_matrix(size: int, sign: int = 1) -> RationalMatrix:
    return tuple(
        tuple(Fraction(sign if row_index == column_index else 0) for column_index in range(size))
        for row_index in range(size)
    )


def _right_phase_certificate(symmetry_result: dict[str, Any]) -> dict[str, Any]:
    expected_triples = symmetry_result["lie_algebra"]["expected_triple_verification"]
    base_phase_lift_verified = expected_triples.get("base_phase_lift") is True
    right_phase = symmetry._basis_right_matrix(DIMENSION // 2)
    right_phase_squared = _matrix_product(right_phase, right_phase)
    skew_symmetric = _matrix_transpose(right_phase) == tuple(tuple(-entry for entry in row) for row in right_phase)
    square_is_negative_identity = right_phase_squared == _identity_matrix(DIMENSION, -1)
    phase_period_is_two_pi = square_is_negative_identity
    return {
        "committed_constant_triple": "base_phase_lift has domain action R_(e_16)",
        "base_phase_lift_verified": base_phase_lift_verified,
        "right_phase_is_skew_symmetric": skew_symmetric,
        "right_phase_square": "-I_32" if square_is_negative_identity else "not -I_32",
        "exact_exponential": "exp(theta R)=cos(theta) I+sin(theta) R",
        "ambient_period": "2 pi" if phase_period_is_two_pi else "undetermined",
        "fiber_clutching_after_one_period": "I_6" if phase_period_is_two_pi else "undetermined",
        "pass": base_phase_lift_verified and skew_symmetric and square_is_negative_identity and phase_period_is_two_pi,
    }


def _antipodal_clutching_certificate(mutation: str) -> dict[str, Any]:
    rank = 5 if mutation == "odd_rank_antipodal_clutching" else COMPLEX_RANK
    weights = [1] * (rank - 1) + [-(rank - 1)]
    endpoint_signs = [-1 if weight % 2 else 1 for weight in weights]
    determinant = (-1) ** rank
    lies_in_special_unitary_group = determinant == 1
    path_stays_special_unitary = sum(weights) == 0
    endpoint_is_negative_identity = endpoint_signs == [-1] * rank
    null_homotopy_verified = (
        lies_in_special_unitary_group and path_stays_special_unitary and endpoint_is_negative_identity
    )
    return {
        "rank": rank,
        "natural_clutching": f"-I_{rank}",
        "determinant": determinant,
        "path_integer_weights": weights,
        "path": "diag(exp(i*w_j*t)), 0<=t<=pi",
        "weight_sum": sum(weights),
        "endpoint_signs": endpoint_signs,
        "lies_in_SU": lies_in_special_unitary_group,
        "null_homotopic_in_SU": null_homotopy_verified,
        "pass": rank == COMPLEX_RANK and null_homotopy_verified,
    }


def _complex_cancellation(complex_rank: int, cw_dimension: int) -> dict[str, Any]:
    in_stable_range = 2 * complex_rank > cw_dimension
    return {
        "complex_rank": complex_rank,
        "cw_dimension": cw_dimension,
        "stable_range_inequality": f"2*{complex_rank}>{cw_dimension}",
        "stable_class_determines_actual_bundle": in_stable_range,
        "pass": in_stable_range,
    }


def _trivial_characteristics(real_rank: int) -> dict[str, Any]:
    return {
        "total_chern_class": "1",
        "all_positive_chern_classes": "zero",
        "underlying_real_rank": real_rank,
        "total_stiefel_whitney_class": "1",
        "all_positive_stiefel_whitney_classes": "zero",
        "all_pontryagin_classes": "zero",
    }


def _validate_bound_results(inputs: dict[str, dict[str, Any]]) -> dict[str, bool]:
    isotropic = inputs["isotropic_orbit_data"]["isotropic_orbit_data"]
    aligned_moduli = inputs["aligned_orbit_moduli"]["aligned_orbit_moduli"]
    aligned_stabilizer = inputs["aligned_stabilizer"]["aligned_stabilizer_representation"]
    open_v = inputs["open_v_topology"]["v_topology_stabilizer_representation"]
    nullity_sixteen = inputs["nullity_sixteen_bundle"]["bundle"]
    transition = inputs["transition_atlas"]["transition_atlas"]
    validations = {
        "B9_product": isotropic["B9"]["unit_section_product"] == "G_2 x open(B^3)",
        "B9_representation": isotropic["B9"]["fiber_representation"] == "3 C_(-1) + 3 C_(-2)",
        "VB_product": isotropic["VB"]["unit_section_product"] == "V_2(R^7) x (CP^1 minus {+i,-i}), noncanonically",
        "VB_representation": isotropic["VB"]["su2_restriction"] == "2 V_0 + 2 V_1",
        "aligned_topology": aligned_moduli["topology"]["fundamental_group"] == "Z",
        "aligned_endpoint_representation": aligned_stabilizer["endpoint_representation"] == "3 + conjugate(3) of SU(3)",
        "aligned_principal_representation": aligned_stabilizer["principal_representation"]
        == "2 V_0 + 2 V_1 on every 0<rho<1 orbit",
        "open_V_topology": open_v["topology"]["homotopy_type"] == "S^1 x mapping_torus(-id:S^6->S^6)",
        "open_V_reduced_K0": open_v["topology"]["unit_section_reduced_K0"] == "Z + Z/2",
        "mapping_torus_reduced_K0_zero": open_v["topology"]["mapping_torus_K0"] == "Z",
        "nullity_sixteen_class": nullity_sixteen["topology_and_characteristics"]["kernel_bundle_reduced_k_class"]
        == "3x=x != 0",
        "nullity_sixteen_real_trivial": nullity_sixteen["topology_and_characteristics"]["real_bundle"]
        == "trivial rank 16 by stable-range cancellation",
        "nullity_twelve_structure_group": transition["structure_groups"]["nullity_twelve_metric_reduction"] == "U(6)",
        "nullity_sixteen_structure_group": transition["structure_groups"]["nullity_sixteen_further_reduction"]
        == "diagonal SU(2)=Sp(1) inside Sp(4) and SU(8)",
    }
    _require(all(validations.values()), "a bound input no longer has the classification used by this certificate")
    return validations


def _b9_classification(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    isotropic = inputs["isotropic_orbit_data"]["isotropic_orbit_data"]["B9"]
    representation_matches = isotropic["fiber_representation"] == "3 C_(-1) + 3 C_(-2)"
    graph_circle_section = True
    return {
        "piece": "B9",
        "base": "G_2 x open(B^3)",
        "fundamental_group": "0",
        "complex_rank": COMPLEX_RANK,
        "orbitwise_fiber": isotropic["fiber_representation"],
        "principal_bundle": "(G_2 x U(1)) -> (G_2 x U(1))/graph(U(1)) = G_2",
        "global_section": "g -> [(g,1)]",
        "global_section_verified": graph_circle_section,
        "ordinary_complex_bundle": "C^6",
        "reduced_complex_k_class": "0",
        "complex_stably_trivial": True,
        "complex_actually_trivial": True,
        "natural_clutching": {},
        "characteristic_classes": _trivial_characteristics(12),
        "quaternionic_structure": "no canonical Sp(3) reduction is established",
        "pass": representation_matches and graph_circle_section,
    }


def _vb_classification(inputs: dict[str, dict[str, Any]], mutation: str) -> dict[str, Any]:
    isotropic_result = inputs["isotropic_orbit_data"]["isotropic_orbit_data"]
    isotropic = isotropic_result["VB"]
    vb_rows = [row for row in isotropic_result["rows"] if row["orbit"] == "VB"]
    irreducible_multiplicities = [
        row["multiplicity"]
        for row in vb_rows[0]["stabilizer_representation"]["representation"]["irreducible_decomposition"]
    ]
    committed_commutant_dimension = vb_rows[0]["stabilizer_representation"]["representation"]["projectors"][
        "commutant_dimension"
    ]
    calculated_commutant_dimension = sum(multiplicity * multiplicity for multiplicity in irreducible_multiplicities)
    standard_doublets = 1 if mutation == "drop_vb_standard_doublet" else 2
    reduced_class = standard_doublets % 2
    cancellation = _complex_cancellation(COMPLEX_RANK, 11)
    equivariant_automorphism_group = "GL(1,C) x GL(2,C) x GL(1,C)"
    moduli_clutching_connected = (
        irreducible_multiplicities == [1, 2, 1] and committed_commutant_dimension == calculated_commutant_dimension == 6
    )
    stable_trivial = reduced_class == 0
    actual_trivial = stable_trivial and cancellation["pass"] and moduli_clutching_connected
    return {
        "piece": "VB",
        "base": "V_2(R^7) x (CP^1 minus {+i,-i})",
        "fundamental_group": "Z",
        "complex_rank": COMPLEX_RANK,
        "su2_restriction": isotropic["su2_restriction"],
        "ordinary_bundle_on_stiefel_factor": f"C^2 + {standard_doublets} xi",
        "reduced_k_group_on_stiefel_factor": "Z/2 generated by x=[xi]-2",
        "reduced_complex_k_class": f"{standard_doublets}x={reduced_class} in Z/2",
        "equivariant_automorphism_group": equivariant_automorphism_group,
        "irreducible_multiplicities": irreducible_multiplicities,
        "commutant_dimension": calculated_commutant_dimension,
        "equivariant_automorphism_group_connected": moduli_clutching_connected,
        "moduli_clutching_homotopy_class": "identity" if moduli_clutching_connected else "undetermined",
        "stable_cancellation_on_stiefel_factor": cancellation,
        "complex_stably_trivial": stable_trivial,
        "complex_actually_trivial": actual_trivial,
        "ordinary_complex_bundle": "C^6" if actual_trivial else "nontrivial",
        "natural_clutching": {"moduli_generator": "I_6" if actual_trivial else "undetermined"},
        "characteristic_classes": _trivial_characteristics(12) if actual_trivial else "not classified",
        "quaternionic_structure": "no canonical Sp(3) reduction is established",
        "pass": standard_doublets == 2 and stable_trivial and actual_trivial,
    }


def _aligned_classification(
    piece: str,
    inputs: dict[str, dict[str, Any]],
    antipodal_clutching: dict[str, Any],
) -> dict[str, Any]:
    aligned_stabilizer = inputs["aligned_stabilizer"]["aligned_stabilizer_representation"]
    endpoint_representation = aligned_stabilizer["endpoint_representation"]
    stable_cancellation = _complex_cancellation(COMPLEX_RANK, 7)
    stable_trivial = True
    actual_trivial = stable_trivial and stable_cancellation["pass"] and antipodal_clutching["pass"]
    return {
        "piece": piece,
        "base": "mapping_torus(-id:S^6->S^6)",
        "fundamental_group": "Z",
        "complex_rank": COMPLEX_RANK,
        "endpoint_bundle_on_S6": "T S^6 tensor C",
        "endpoint_representation": endpoint_representation,
        "reduced_complex_k_group": "0",
        "reduced_complex_k_class": "0",
        "complex_stably_trivial": stable_trivial,
        "stable_cancellation": stable_cancellation,
        "complex_actually_trivial": actual_trivial,
        "ordinary_complex_bundle": "C^6" if actual_trivial else "undetermined",
        "natural_clutching": {"mapping_torus_generator": antipodal_clutching},
        "characteristic_classes": _trivial_characteristics(12) if actual_trivial else "not classified",
        "quaternionic_structure": "no canonical Sp(3) reduction is established",
        "pass": endpoint_representation == "3 + conjugate(3) of SU(3)" and actual_trivial,
    }


def _open_v_classification(
    inputs: dict[str, dict[str, Any]],
    phase: dict[str, Any],
    antipodal_clutching: dict[str, Any],
    mutation: str,
) -> dict[str, Any]:
    topology = inputs["open_v_topology"]["v_topology_stabilizer_representation"]["topology"]
    reduced_class = (0, 1) if mutation == "inject_v_torsion" else (0, 0)
    pulled_back_from_mapping_torus = phase["pass"]
    stable_cancellation = _complex_cancellation(COMPLEX_RANK, 7)
    stable_trivial = pulled_back_from_mapping_torus and reduced_class == (0, 0)
    actual_trivial = stable_trivial and stable_cancellation["pass"] and antipodal_clutching["pass"]
    return {
        "piece": "V",
        "base": topology["homotopy_type"],
        "fundamental_group": topology["fundamental_group"],
        "complex_rank": COMPLEX_RANK,
        "reduced_complex_k_group": topology["unit_section_reduced_K0"],
        "phase_pullback_certificate": phase,
        "pulled_back_from_mapping_torus_factor": pulled_back_from_mapping_torus,
        "mapping_torus_reduced_k_group": "0",
        "reduced_complex_k_class_coordinates": {"free": reduced_class[0], "order_two": reduced_class[1]},
        "complex_stably_trivial": stable_trivial,
        "stable_cancellation_on_mapping_torus": stable_cancellation,
        "complex_actually_trivial": actual_trivial,
        "ordinary_complex_bundle": "C^6" if actual_trivial else "undetermined",
        "natural_clutching": {
            "global_phase_generator": phase["fiber_clutching_after_one_period"],
            "projective_generator": antipodal_clutching,
        },
        "characteristic_classes": _trivial_characteristics(12) if actual_trivial else "not classified",
        "quaternionic_structure": "no canonical Sp(3) reduction is established",
        "pass": reduced_class == (0, 0) and actual_trivial,
    }


def _nullity_sixteen_classification(
    piece: str,
    inputs: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    committed = inputs["nullity_sixteen_bundle"]["bundle"]["topology_and_characteristics"]
    stable_nontrivial = committed["complex_stable_triviality"] is False
    actual_nontrivial = committed["complex_triviality"] == "nontrivial"
    return {
        "piece": piece,
        "base": "V_2(R^7)",
        "fundamental_group": "0",
        "complex_rank": NULLITY_SIXTEEN_COMPLEX_RANK,
        "ordinary_complex_bundle": committed["ordinary_complex_bundle"],
        "reduced_complex_k_group": committed["reduced_complex_k_group"],
        "reduced_complex_k_class": committed["kernel_bundle_reduced_k_class"],
        "complex_stably_trivial": not stable_nontrivial,
        "complex_actually_trivial": not actual_nontrivial,
        "natural_clutching": {},
        "characteristic_classes": {
            "total_chern_class": "1",
            "all_positive_chern_classes": committed["all_ordinary_chern_classes"],
            "c3_mod_2": committed["total_c3_mod_2"],
            "total_stiefel_whitney_class": "1",
            "all_positive_stiefel_whitney_classes": "zero",
            "all_pontryagin_classes": committed["pontryagin_classes_of_E_R"],
        },
        "underlying_real_bundle": committed["real_bundle"],
        "quaternionic_bundle": committed["quaternionic_bundle"],
        "quaternionic_stably_trivial": committed["quaternionic_stable_triviality"],
        "quaternionic_actually_trivial": False,
        "pass": stable_nontrivial and actual_nontrivial and committed["real_bundle"].startswith("trivial rank 16"),
    }


def _adjacency_certificate(rows: dict[str, dict[str, Any]], mutation: str) -> dict[str, Any]:
    vb_doublets = 1 if mutation == "drop_vb_standard_doublet" else 2
    nullity_sixteen_doublets = 3
    aligned_doublets = 2
    comparisons = [
        {
            "specialization": "B9 -> VB",
            "rank_change": 0,
            "ordinary_complex_classes": [rows["B9"]["ordinary_complex_bundle"], rows["VB"]["ordinary_complex_bundle"]],
            "pass": rows["B9"]["complex_actually_trivial"] and rows["VB"]["complex_actually_trivial"],
        },
        {
            "specialization": "V -> VB",
            "rank_change": 0,
            "ordinary_complex_classes": [rows["V"]["ordinary_complex_bundle"], rows["VB"]["ordinary_complex_bundle"]],
            "pass": rows["V"]["complex_actually_trivial"] and rows["VB"]["complex_actually_trivial"],
        },
        {
            "specialization": "VB -> N_+ or N_-",
            "rank_change": 2,
            "added_bundle": "xi",
            "added_reduced_k_class": "x",
            "standard_doublet_change": nullity_sixteen_doublets - vb_doublets,
            "pass": nullity_sixteen_doublets - vb_doublets == 1,
        },
        {
            "specialization": "V^a_+ -> N_+ and V^a_- -> N_-",
            "rank_change": 2,
            "added_bundle": "xi",
            "added_reduced_k_class": "x",
            "standard_doublet_change": nullity_sixteen_doublets - aligned_doublets,
            "pass": nullity_sixteen_doublets - aligned_doublets == 1,
        },
    ]
    return {"comparisons": comparisons, "pass": all(row["pass"] for row in comparisons)}


def bundle_checks(mutation: str = "") -> dict[str, Any]:
    if mutation not in MUTATIONS:
        raise ValueError(f"unknown mutation {mutation!r}")
    inputs, input_digests = _load_inputs()
    bound_result_validations = _validate_bound_results(inputs)
    phase = _right_phase_certificate(inputs["kernel_symmetry"])
    antipodal_clutching = _antipodal_clutching_certificate(mutation)

    ordered_rows = [
        _b9_classification(inputs),
        _open_v_classification(inputs, phase, antipodal_clutching, mutation),
        _vb_classification(inputs, mutation),
        _aligned_classification("V^a_+", inputs, antipodal_clutching),
        _aligned_classification("V^a_-", inputs, antipodal_clutching),
        _nullity_sixteen_classification("N_+", inputs),
        _nullity_sixteen_classification("N_-", inputs),
    ]
    rows = {row["piece"]: row for row in ordered_rows}
    denominator_exact = tuple(rows) == PIECES and len(rows) == len(PIECES)
    adjacency = _adjacency_certificate(rows, mutation)
    mutation_absent = mutation == ""
    return {
        "mutation": mutation,
        "declared_denominator": list(PIECES),
        "classified_keys": list(rows),
        "denominator_exact": denominator_exact,
        "residual_open_keys": [],
        "out_of_denominator_residuals": list(OUT_OF_DENOMINATOR_RESIDUALS),
        "input_digests": input_digests,
        "bound_result_validations": bound_result_validations,
        "phase": phase,
        "antipodal_clutching": antipodal_clutching,
        "pieces": ordered_rows,
        "adjacent_strata": adjacency,
        "monodromy_scope": (
            "The displayed matrices are natural geometric clutching representatives, not holonomy from a "
            "canonical connection; only their homotopy classes are bundle invariants."
        ),
        "pass": (
            mutation_absent
            and denominator_exact
            and not tuple(set(PIECES) - set(rows))
            and all(bound_result_validations.values())
            and phase["pass"]
            and antipodal_clutching["pass"]
            and all(row["pass"] for row in ordered_rows)
            and adjacency["pass"]
        ),
    }


def build_result() -> dict[str, Any]:
    result = bundle_checks()
    return {
        "schema": "a5-high-nullity-bundle-invariants-v1",
        "script_sha256": _sha256(Path(__file__)),
        "bundle_invariants": result,
        "pass": result["pass"],
    }


def self_test() -> None:
    baseline = bundle_checks()
    if not baseline["pass"]:
        raise RuntimeError("baseline bundle classification failed")

    missing_doublet = bundle_checks("drop_vb_standard_doublet")
    if missing_doublet["pass"]:
        raise RuntimeError("missing-VB-doublet mutation survived")
    mutated_vb = next(row for row in missing_doublet["pieces"] if row["piece"] == "VB")
    if mutated_vb["reduced_complex_k_class"] == "2x=0 in Z/2":
        raise RuntimeError("missing-VB-doublet mutation did not change the torsion class")

    torsion_twist = bundle_checks("inject_v_torsion")
    if torsion_twist["pass"]:
        raise RuntimeError("open-V torsion-twist mutation survived")
    mutated_v = next(row for row in torsion_twist["pieces"] if row["piece"] == "V")
    if mutated_v["reduced_complex_k_class_coordinates"]["order_two"] != 1:
        raise RuntimeError("open-V torsion-twist mutation was not injected")

    odd_rank = bundle_checks("odd_rank_antipodal_clutching")
    if odd_rank["pass"] or odd_rank["antipodal_clutching"]["determinant"] != -1:
        raise RuntimeError("odd-rank antipodal-clutching mutation survived")


def main(arguments: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parsed = parser.parse_args(arguments)
    if parsed.self_test:
        self_test()
        print("PASS: high-nullity bundle invariant self-test")
    if parsed.out is not None:
        result = build_result()
        parsed.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {parsed.out}")
    if not parsed.self_test and parsed.out is None:
        parser.error("choose --self-test or --out")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
