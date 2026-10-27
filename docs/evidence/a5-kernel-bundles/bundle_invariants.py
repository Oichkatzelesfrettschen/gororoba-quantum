"""Producer-bound inputs for the high-nullity A_5 bundle classification.

The script recomputes the discrete inputs to the written bundle arguments:
fiber multiplicities, K-class residues, CW dimensions, cancellation
inequalities, phase periodicity, and adjacent-stratum rank jumps. Topological
classification steps that use a theorem or a geometric argument remain marked
``inferred`` and do not masquerade as machine-verified pass-flag literals.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from collections.abc import Iterable, Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import kernel_symmetry as symmetry  # noqa: E402

DIMENSION = 32
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
        "a5-v-topology-stabilizer-representation-v2",
    ),
    "isotropic_orbit_data": (
        "isotropic-orbit-data-result.json",
        "isotropic_orbit_data.py",
        "a5-isotropic-orbit-data-v1",
    ),
    "nullity_sixteen_stabilizer": (
        "stabilizer-result.json",
        "stabilizer_representation.py",
        "a5-nullity-sixteen-stabilizer-representation-v1",
    ),
    "nullity_sixteen_bundle": (
        "nullity-sixteen-bundle-result.json",
        "nullity_sixteen_bundle.py",
        "a5-nullity-sixteen-bundle-invariants-v2",
    ),
    "transition_atlas": (
        "transition-atlas-result.json",
        "transition_atlas.py",
        "a5-high-nullity-transition-atlas-v1",
    ),
}

MUTATIONS = (
    "",
    "add_vb_standard_doublet",
    "add_mapping_torus_k0_generator",
    "kill_k_generator",
)

RationalMatrix = symmetry.RationalMatrix


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _apply_input_mutation(inputs: dict[str, dict[str, Any]], mutation: str) -> dict[str, Any]:
    if mutation == "":
        return {"name": "", "target": None}
    if mutation == "add_vb_standard_doublet":
        rows = inputs["isotropic_orbit_data"]["isotropic_orbit_data"]["rows"]
        changed = 0
        for row in rows:
            if row["orbit"] != "VB":
                continue
            irreducibles = row["stabilizer_representation"]["representation"]["irreducible_decomposition"]
            doublet = next(item for item in irreducibles if int(item["sl2_highest_weight"]) == 1)
            doublet["multiplicity"] = int(doublet["multiplicity"]) + 1
            doublet["joint_dimension"] = int(doublet["joint_dimension"]) + int(doublet["irreducible_dimension"])
            changed += 1
        _require(changed > 0, "VB input mutation found no producer row")
        return {"name": mutation, "target": "isotropic VB irreducible multiplicity", "rows_changed": changed}
    if mutation == "add_mapping_torus_k0_generator":
        topology = inputs["open_v_topology"]["v_topology_stabilizer_representation"]["topology"]
        topology["mapping_torus_K0"] = "Z^2"
        return {"name": mutation, "target": "open-V producer mapping_torus_K0"}
    if mutation == "kill_k_generator":
        k_theory = inputs["nullity_sixteen_bundle"]["bundle"]["representation_ring_k_theory"]
        k_theory["generator_order"] = 1
        return {"name": mutation, "target": "nullity-sixteen producer generator_order"}
    raise ValueError(f"unknown mutation {mutation!r}")


def _load_inputs(mutation: str) -> tuple[dict[str, dict[str, Any]], dict[str, str], dict[str, Any]]:
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
    mutated = copy.deepcopy(loaded)
    mutation_record = _apply_input_mutation(mutated, mutation)
    return mutated, digests, mutation_record


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
    return {
        "committed_constant_triple": "base_phase_lift has domain action R_(e_16)",
        "base_phase_lift_verified": base_phase_lift_verified,
        "right_phase_is_skew_symmetric": skew_symmetric,
        "right_phase_square": "-I_32" if square_is_negative_identity else "not -I_32",
        "exact_exponential": "exp(theta R)=cos(theta) I+sin(theta) R",
        "ambient_period": "2 pi" if square_is_negative_identity else "undetermined",
        "fiber_return_after_one_period": "identity" if square_is_negative_identity else "undetermined",
        "pass": base_phase_lift_verified and skew_symmetric and square_is_negative_identity,
    }


def _parse_abelian_group(group: str) -> tuple[int, tuple[int, ...]]:
    if group == "0":
        return 0, ()
    free_rank = 0
    torsion: list[int] = []
    for term in group.split(" + "):
        if term == "Z":
            free_rank += 1
        elif term.startswith("Z^"):
            free_rank += int(term.removeprefix("Z^"))
        elif term.startswith("Z/"):
            torsion.append(int(term.removeprefix("Z/")))
        else:
            raise ValueError(f"unsupported abelian-group term {term!r}")
    return free_rank, tuple(torsion)


def _uniform(values: Iterable[int], label: str) -> int:
    distinct = set(values)
    _require(len(distinct) == 1, f"{label} is not constant: {sorted(distinct)}")
    return distinct.pop()


def _u2_counts(rows: Sequence[dict[str, Any]]) -> tuple[int, int, tuple[int, ...], int]:
    doublet_counts: list[int] = []
    trivial_counts: list[int] = []
    multiplicity_signatures: list[tuple[int, ...]] = []
    commutant_dimensions: list[int] = []
    for row in rows:
        representation = row["stabilizer_representation"]["representation"]
        irreducibles = representation["irreducible_decomposition"]
        doublet_counts.append(
            sum(int(item["multiplicity"]) for item in irreducibles if int(item["sl2_highest_weight"]) == 1)
        )
        trivial_counts.append(
            sum(int(item["multiplicity"]) for item in irreducibles if int(item["sl2_highest_weight"]) == 0)
        )
        multiplicity_signatures.append(tuple(int(item["multiplicity"]) for item in irreducibles))
        commutant_dimensions.append(int(representation["projectors"]["commutant_dimension"]))
    signatures = set(multiplicity_signatures)
    _require(len(signatures) == 1, "U(2) irreducible multiplicities vary between producer rows")
    return (
        _uniform(trivial_counts, "U(2) trivial-line count"),
        _uniform(doublet_counts, "U(2) standard-doublet count"),
        signatures.pop(),
        _uniform(commutant_dimensions, "U(2) commutant dimension"),
    )


def _nullity_u2_counts(rows: Sequence[dict[str, Any]]) -> tuple[int, int, tuple[int, ...], int]:
    doublets: list[int] = []
    trivials: list[int] = []
    signatures: list[tuple[int, ...]] = []
    commutants: list[int] = []
    for row in rows:
        irreducibles = row["irreducible_decomposition"]
        doublets.append(sum(int(item["multiplicity"]) for item in irreducibles if int(item["sl2_highest_weight"]) == 1))
        trivials.append(sum(int(item["multiplicity"]) for item in irreducibles if int(item["sl2_highest_weight"]) == 0))
        signatures.append(tuple(int(item["multiplicity"]) for item in irreducibles))
        commutants.append(int(row["invariant_projectors"]["commutant_dimension"]))
    signature_set = set(signatures)
    _require(len(signature_set) == 1, "nullity-sixteen irreducible multiplicities vary")
    return (
        _uniform(trivials, "nullity-sixteen trivial-line count"),
        _uniform(doublets, "nullity-sixteen doublet count"),
        signature_set.pop(),
        _uniform(commutants, "nullity-sixteen commutant dimension"),
    )


def _su2_counts(rows: Sequence[dict[str, Any]]) -> tuple[int, int]:
    return (
        _uniform((int(row["representation"]["trivial_lines"]) for row in rows), "SU(2) trivial-line count"),
        _uniform((int(row["representation"]["standard_doublets"]) for row in rows), "SU(2) doublet count"),
    )


def _complex_cancellation(complex_rank: int, cw_dimension: int) -> dict[str, Any]:
    inequality_verified = cw_dimension <= 2 * complex_rank
    return {
        "status": "inferred",
        "lemma": "a stably trivial complex rank-k bundle on a CW complex of dimension d<=2k is trivial",
        "range_condition": "d<=2k",
        "complex_rank": complex_rank,
        "cw_dimension": cw_dimension,
        "inequality": f"{cw_dimension}<={2 * complex_rank}",
        "inequality_verified": inequality_verified,
    }


def _inferred_zero_characteristics(complex_rank: int, reason: str) -> dict[str, Any]:
    real_rank = 2 * complex_rank
    return {
        "status": "inferred",
        "reason": reason,
        "chern_coefficients_c0_through_c_rank": [1, *([0] * complex_rank)],
        "stiefel_whitney_coefficients_w0_through_w_real_rank": [1, *([0] * real_rank)],
        "pontryagin_coefficients_p0_through_p_floor_real_rank_over_4": [1, *([0] * (real_rank // 4))],
    }


def _producer_piece_keys(inputs: dict[str, dict[str, Any]]) -> tuple[str, ...]:
    isotropic_rows = inputs["isotropic_orbit_data"]["isotropic_orbit_data"]["rows"]
    aligned_rows = inputs["aligned_stabilizer"]["aligned_stabilizer_representation"]["rows"]
    nullity_rows = inputs["nullity_sixteen_stabilizer"]["stabilizer_representation"]["rows"]
    observed = {str(row["orbit"]) for row in isotropic_rows}
    observed.add("V")
    observed.update(str(row["component"]) for row in aligned_rows)
    observed.update({"Np": "N_+", "Nm": "N_-"}[str(row["orbit"])] for row in nullity_rows)
    return tuple(piece for piece in PIECES if piece in observed)


def _derive_inputs(inputs: dict[str, dict[str, Any]], phase: dict[str, Any]) -> dict[str, Any]:
    isotropic_rows = inputs["isotropic_orbit_data"]["isotropic_orbit_data"]["rows"]
    b9_rows = [row for row in isotropic_rows if row["orbit"] == "B9"]
    vb_rows = [row for row in isotropic_rows if row["orbit"] == "VB"]
    b9_rank = _uniform(
        (int(row["stabilizer_representation"]["complex_kernel_dimension"]) for row in b9_rows),
        "B9 complex rank",
    )
    vb_rank = _uniform(
        (int(row["stabilizer_representation"]["complex_kernel_dimension"]) for row in vb_rows),
        "VB complex rank",
    )
    vb_trivials, vb_doublets, vb_multiplicities, vb_commutant = _u2_counts(vb_rows)

    aligned_rows = inputs["aligned_stabilizer"]["aligned_stabilizer_representation"]["rows"]
    aligned_principal = [row for row in aligned_rows if row["orbit_type"] == "principal"]
    aligned_boundary = [row for row in aligned_rows if row["orbit_type"] == "null_boundary"]
    aligned_rank = _uniform((int(row["complex_kernel_dimension"]) for row in aligned_principal), "aligned rank")
    aligned_trivials, aligned_doublets = _su2_counts(aligned_principal)
    boundary_trivials, boundary_doublets = _su2_counts(aligned_boundary)

    open_v_result = inputs["open_v_topology"]["v_topology_stabilizer_representation"]
    open_v_principal = [row for row in open_v_result["rows"] if row["orbit_type"] == "principal"]
    open_v_rank = _uniform((int(row["complex_kernel_dimension"]) for row in open_v_principal), "open-V rank")
    open_v_trivials, open_v_doublets = _su2_counts(open_v_principal)

    nullity_rows = inputs["nullity_sixteen_stabilizer"]["stabilizer_representation"]["rows"]
    nullity_rank = _uniform((int(row["complex_fiber_dimension"]) for row in nullity_rows), "nullity-sixteen rank")
    nullity_trivials, nullity_doublets, nullity_multiplicities, nullity_commutant = _nullity_u2_counts(nullity_rows)

    topology = open_v_result["topology"]
    mapping_k0_free, mapping_k0_torsion = _parse_abelian_group(str(topology["mapping_torus_K0"]))
    unit_reduced_free, unit_reduced_torsion = _parse_abelian_group(str(topology["unit_section_reduced_K0"]))
    aligned_cohomology = inputs["aligned_orbit_moduli"]["aligned_orbit_moduli"]["topology"]["integral_cohomology"]
    aligned_cw_dimension = max(int(degree) for degree in aligned_cohomology)
    stiefel_cells = inputs["nullity_sixteen_bundle"]["bundle"]["base_topology"]["cell_degrees"]
    stiefel_cw_dimension = max(int(degree) for degree in stiefel_cells)
    k_theory = inputs["nullity_sixteen_bundle"]["bundle"]["representation_ring_k_theory"]
    generator_order = int(k_theory["generator_order"])
    _require(generator_order > 0, "K-theory generator order must be positive")

    return {
        "piece_keys": list(_producer_piece_keys(inputs)),
        "phase": phase,
        "B9": {"complex_rank": b9_rank},
        "VB": {
            "complex_rank": vb_rank,
            "trivial_lines": vb_trivials,
            "standard_doublets": vb_doublets,
            "irreducible_multiplicities": list(vb_multiplicities),
            "commutant_dimension": vb_commutant,
        },
        "aligned": {
            "complex_rank": aligned_rank,
            "trivial_lines": aligned_trivials,
            "standard_doublets": aligned_doublets,
            "boundary_trivial_lines": boundary_trivials,
            "boundary_standard_doublets": boundary_doublets,
            "cw_dimension": aligned_cw_dimension,
        },
        "V": {
            "complex_rank": open_v_rank,
            "trivial_lines": open_v_trivials,
            "standard_doublets": open_v_doublets,
            "unit_reduced_k0": {"free_rank": unit_reduced_free, "torsion_orders": list(unit_reduced_torsion)},
        },
        "N": {
            "complex_rank": nullity_rank,
            "trivial_lines": nullity_trivials,
            "standard_doublets": nullity_doublets,
            "irreducible_multiplicities": list(nullity_multiplicities),
            "commutant_dimension": nullity_commutant,
        },
        "mapping_torus_reduced_k0": {
            "free_rank": mapping_k0_free - 1,
            "torsion_orders": list(mapping_k0_torsion),
        },
        "stiefel_cw_dimension": stiefel_cw_dimension,
        "k_generator_order": generator_order,
    }


def _classification(derived: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    generator_order = int(derived["k_generator_order"])
    mapping_group = derived["mapping_torus_reduced_k0"]
    mapping_group_zero = mapping_group == {"free_rank": 0, "torsion_orders": []}

    b9_rank = int(derived["B9"]["complex_rank"])
    vb_rank = int(derived["VB"]["complex_rank"])
    aligned_rank = int(derived["aligned"]["complex_rank"])
    open_v_rank = int(derived["V"]["complex_rank"])
    nullity_rank = int(derived["N"]["complex_rank"])
    vb_doublets = int(derived["VB"]["standard_doublets"])
    aligned_doublets = int(derived["aligned"]["standard_doublets"])
    nullity_doublets = int(derived["N"]["standard_doublets"])
    vb_residue = vb_doublets % generator_order
    nullity_residue = nullity_doublets % generator_order

    vb_cancellation = _complex_cancellation(vb_rank, int(derived["stiefel_cw_dimension"]))
    aligned_cancellation = _complex_cancellation(aligned_rank, int(derived["aligned"]["cw_dimension"]))
    open_v_cancellation = _complex_cancellation(open_v_rank, int(derived["aligned"]["cw_dimension"]))
    vb_automorphism_connected = int(derived["VB"]["commutant_dimension"]) == sum(
        int(multiplicity) * int(multiplicity) for multiplicity in derived["VB"]["irreducible_multiplicities"]
    )
    phase_pullback_input = bool(derived["phase"]["pass"])

    rows = [
        {
            "piece": "B9",
            "complex_rank": b9_rank,
            "ordinary_complex_bundle": f"C^{b9_rank}",
            "classification_status": "inferred",
            "classification_argument": "the graph-circle principal bundle has a section over each G_2 orbit",
            "characteristic_classes": _inferred_zero_characteristics(
                b9_rank, "the inferred complex trivialization also trivializes the underlying real bundle"
            ),
        },
        {
            "piece": "V",
            "complex_rank": open_v_rank,
            "ordinary_complex_bundle": f"C^{open_v_rank}" if mapping_group_zero else "not inferred trivial",
            "classification_status": "inferred",
            "classification_argument": "the exact periodic phase lift makes the bundle a pullback from M_-",
            "phase_pullback_input": phase_pullback_input,
            "mapping_torus_reduced_k0": mapping_group,
            "unit_reduced_k0": derived["V"]["unit_reduced_k0"],
            "pulled_back_class_coordinates": {
                "free": [0] * int(derived["V"]["unit_reduced_k0"]["free_rank"]),
                "torsion": [0] * len(derived["V"]["unit_reduced_k0"]["torsion_orders"]),
            },
            "cancellation": open_v_cancellation,
            "characteristic_classes": _inferred_zero_characteristics(
                open_v_rank, "pullback from reduced K-class zero plus stable-range cancellation"
            ),
        },
        {
            "piece": "VB",
            "complex_rank": vb_rank,
            "ordinary_bundle_on_stiefel_factor": (f"C^{int(derived['VB']['trivial_lines'])} + {vb_doublets} xi"),
            "k_generator_order": generator_order,
            "reduced_k_residue": vb_residue,
            "irreducible_multiplicities": derived["VB"]["irreducible_multiplicities"],
            "commutant_dimension": derived["VB"]["commutant_dimension"],
            "equivariant_automorphism_group_connected": vb_automorphism_connected,
            "cancellation": vb_cancellation,
            "ordinary_complex_bundle": f"C^{vb_rank}" if vb_residue == 0 else "not inferred trivial",
            "classification_status": "inferred",
            "classification_argument": "zero stable class, cancellation on V_2(R^7), and trivial multiplicity bundles",
            "characteristic_classes": _inferred_zero_characteristics(
                vb_rank, "the inferred complex trivialization also trivializes the underlying real bundle"
            ),
        },
        *[
            {
                "piece": piece,
                "complex_rank": aligned_rank,
                "mapping_torus_reduced_k0": mapping_group,
                "cancellation": aligned_cancellation,
                "ordinary_complex_bundle": f"C^{aligned_rank}" if mapping_group_zero else "not inferred trivial",
                "classification_status": "inferred",
                "classification_argument": "reduced K^0(M_-)=0 plus stable-range cancellation",
                "characteristic_classes": _inferred_zero_characteristics(
                    aligned_rank, "zero reduced K-class plus stable-range cancellation"
                ),
            }
            for piece in ("V^a_+", "V^a_-")
        ],
        *[
            {
                "piece": piece,
                "complex_rank": nullity_rank,
                "ordinary_complex_bundle": f"C^{int(derived['N']['trivial_lines'])} + {nullity_doublets} xi",
                "k_generator_order": generator_order,
                "reduced_k_residue": nullity_residue,
                "classification_status": "inferred",
                "classification_argument": "Hodgkin edge map sends x to [xi]-2",
                "underlying_real_bundle": f"R^{2 * nullity_rank}",
                "real_classification_status": "inferred",
                "characteristic_classes": _inferred_zero_characteristics(
                    nullity_rank, "the complex summands have zero Chern classes and the total real bundle is trivial"
                ),
                "quaternionic_bundle": f"H + {nullity_doublets} xi_H",
                "quaternionic_classification_status": "inferred",
            }
            for piece in ("N_+", "N_-")
        ],
    ]

    rows_by_piece = {row["piece"]: row for row in rows}
    adjacency = {
        "VB_to_N_standard_doublet_change": nullity_doublets - vb_doublets,
        "aligned_to_N_standard_doublet_change": nullity_doublets - aligned_doublets,
        "VB_to_N_complex_rank_change": nullity_rank - vb_rank,
        "aligned_to_N_complex_rank_change": nullity_rank - aligned_rank,
    }
    observed_checks = {
        "producer_denominator_exact": tuple(derived["piece_keys"]) == PIECES,
        "phase_period_verified": phase_pullback_input,
        "B9_complex_rank_is_six": b9_rank == 6,
        "VB_fiber_dimension_is_six": int(derived["VB"]["trivial_lines"]) + 2 * vb_doublets == vb_rank == 6,
        "VB_stable_class_is_zero": vb_residue == 0,
        "VB_commutant_matches_multiplicities": vb_automorphism_connected,
        "mapping_torus_reduced_K0_is_zero": mapping_group_zero,
        "aligned_fiber_dimension_is_six": (
            int(derived["aligned"]["trivial_lines"]) + 2 * aligned_doublets == aligned_rank == 6
        ),
        "open_V_fiber_dimension_is_six": (
            int(derived["V"]["trivial_lines"]) + 2 * int(derived["V"]["standard_doublets"]) == open_v_rank == 6
        ),
        "nullity_sixteen_fiber_dimension_is_eight": (
            int(derived["N"]["trivial_lines"]) + 2 * nullity_doublets == nullity_rank == 8
        ),
        "nullity_sixteen_stable_class_is_nonzero": nullity_residue != 0,
        "VB_cancellation_inequality": bool(vb_cancellation["inequality_verified"]),
        "aligned_cancellation_inequality": bool(aligned_cancellation["inequality_verified"]),
        "open_V_cancellation_inequality": bool(open_v_cancellation["inequality_verified"]),
        "VB_boundary_adds_one_doublet": adjacency["VB_to_N_standard_doublet_change"] == 1,
        "aligned_boundary_adds_one_doublet": adjacency["aligned_to_N_standard_doublet_change"] == 1,
    }
    _require(set(rows_by_piece) == set(PIECES), "classification rows do not cover the declared pieces")
    return rows, {"observed_checks": observed_checks, "adjacent_strata": adjacency}


def bundle_checks(mutation: str = "") -> dict[str, Any]:
    if mutation not in MUTATIONS:
        raise ValueError(f"unknown mutation {mutation!r}")
    inputs, input_digests, mutation_record = _load_inputs(mutation)
    phase = _right_phase_certificate(inputs["kernel_symmetry"])
    derived = _derive_inputs(inputs, phase)
    rows, classification = _classification(derived)
    observed_checks = classification["observed_checks"]
    return {
        "mutation": mutation_record,
        "declared_denominator": list(PIECES),
        "producer_piece_keys": derived["piece_keys"],
        "residual_open_keys": [],
        "out_of_denominator_residuals": list(OUT_OF_DENOMINATOR_RESIDUALS),
        "input_digests": input_digests,
        "derived_inputs": derived,
        "pieces": rows,
        "adjacent_strata": classification["adjacent_strata"],
        "observed_checks": observed_checks,
        "inference_scope": (
            "Piece triviality, Hodgkin's edge map, stable-range cancellation, and the graph-circle section are "
            "written mathematical arguments. The pass flag covers their producer-derived numeric prerequisites, "
            "not those theorems themselves."
        ),
        "pass": all(observed_checks.values()),
    }


def build_result() -> dict[str, Any]:
    result = bundle_checks()
    return {
        "schema": "a5-high-nullity-bundle-invariants-v2",
        "script_sha256": _sha256(Path(__file__)),
        "bundle_invariants": result,
        "pass": result["pass"],
    }


def _self_test_mutation_task(mutation: str) -> tuple[str, dict[str, Any]]:
    """Build one independent producer-input mutation for the parent self-test."""
    return mutation, bundle_checks(mutation)


def self_test() -> None:
    baseline = bundle_checks()
    if not baseline["pass"]:
        raise RuntimeError("baseline producer-bound invariant inputs failed")

    mutations = dict(
        symmetry.parallel.ordered_map(
            _self_test_mutation_task,
            ["add_vb_standard_doublet", "add_mapping_torus_k0_generator", "kill_k_generator"],
            min_items=1,
        )
    )
    extra_doublet = mutations["add_vb_standard_doublet"]
    if extra_doublet["pass"] or extra_doublet["derived_inputs"]["VB"]["standard_doublets"] != 3:
        raise RuntimeError("mutated VB producer multiplicity survived")
    if extra_doublet["observed_checks"]["VB_fiber_dimension_is_six"]:
        raise RuntimeError("mutated VB producer multiplicity left the fiber dimension unchanged")

    mapping_generator = mutations["add_mapping_torus_k0_generator"]
    if mapping_generator["pass"]:
        raise RuntimeError("mutated mapping-torus K^0 input survived")
    if mapping_generator["derived_inputs"]["mapping_torus_reduced_k0"]["free_rank"] != 1:
        raise RuntimeError("mapping-torus input mutation did not reach the reduced K-group")

    killed_generator = mutations["kill_k_generator"]
    if killed_generator["pass"]:
        raise RuntimeError("mutated K-theory relation survived")
    nullity_row = next(row for row in killed_generator["pieces"] if row["piece"] == "N_+")
    if nullity_row["reduced_k_residue"] != 0:
        raise RuntimeError("K-theory relation mutation did not change the nullity-sixteen class")


def main(arguments: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parsed = parser.parse_args(arguments)
    if parsed.check is not None and (parsed.self_test or parsed.out is not None):
        parser.error("--check cannot be combined with --self-test or --out")
    if parsed.self_test:
        self_test()
        print("PASS: producer-bound bundle-invariant input self-test")
    if parsed.out is not None or parsed.check is not None:
        result = build_result()
        payload = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
        if parsed.check is not None:
            if payload != parsed.check.read_bytes():
                raise SystemExit(f"bundle_invariants.py: fresh JSON differs byte-for-byte from {parsed.check}")
            print(f"bundle_invariants.py: fresh JSON matches {parsed.check}")
        else:
            parsed.out.write_bytes(payload)
            print(f"wrote {parsed.out}")
    if not parsed.self_test and parsed.out is None and parsed.check is None:
        parser.error("choose --self-test, --out, or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
