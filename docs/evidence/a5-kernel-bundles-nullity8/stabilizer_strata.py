"""Exact invariant criteria and canonical checks for all connected nullity-eight stabilizer strata."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any, TypeAlias

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KERNEL_BUNDLES = HERE.parent / "a5-kernel-bundles"
REGULARITY = HERE.parent / "a5-strata-regularity"
EQUATIONS = HERE.parent / "a5-rank-strata-equations"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(KERNEL_BUNDLES))
sys.path.insert(0, str(REGULARITY))
sys.path.insert(0, str(EQUATIONS))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import aligned_stabilizer_representation as aligned_representation  # noqa: E402
import kernel_symmetry as symmetry  # noqa: E402
import remaining_orbit_moduli as remaining_moduli  # noqa: E402
import stabilizer_fiber_samples as samples  # noqa: E402
import stabilizer_representation as stabilizer  # noqa: E402
import verify_regularity_independent as independent  # noqa: E402
import w8_orbit_moduli as frame_invariants  # noqa: E402

import parallel  # noqa: E402
from cd_core import left_mult_matrix_exact  # noqa: E402

SCHEMA = "a5-kernel-bundles-nullity8-stabilizer-strata-v1"
MUTATIONS = ("", "ignore_three_forms", "drop_phase_projection")
SAMPLE_RESULT = HERE / "stabilizer-fiber-samples-result.json"
SAMPLE_SCRIPT = HERE / "stabilizer_fiber_samples.py"
W8_MODULI_RESULT = HERE / "w8-orbit-moduli-result.json"
W8_MODULI_SCRIPT = HERE / "w8_orbit_moduli.py"
REMAINING_MODULI_RESULT = HERE / "remaining-orbit-moduli-result.json"
REMAINING_MODULI_SCRIPT = HERE / "remaining_orbit_moduli.py"
SOURCE_PATHS = (
    HERE / "stabilizer_strata.py",
    SAMPLE_RESULT,
    SAMPLE_SCRIPT,
    W8_MODULI_RESULT,
    W8_MODULI_SCRIPT,
    REMAINING_MODULI_RESULT,
    REMAINING_MODULI_SCRIPT,
    KERNEL_BUNDLES / "kernel_symmetry.py",
    KERNEL_BUNDLES / "stabilizer_representation.py",
    KERNEL_BUNDLES / "aligned_orbit_moduli.py",
    KERNEL_BUNDLES / "aligned_stabilizer_representation.py",
    REGULARITY / "verify_regularity_independent.py",
)

Vector = tuple[Fraction, ...]
Frame = tuple[Vector, Vector, Vector, Vector]
RationalMatrix: TypeAlias = tuple[tuple[Fraction, ...], ...]
GaussianPoint: TypeAlias = tuple[independent.Gq, ...]
Candidate = tuple[dict[str, Any], Vector, GaussianPoint]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_bound_result(path: Path, script: Path, schema: str) -> dict[str, Any]:
    record: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    _require(record.get("schema") == schema, f"{path.name} has an unexpected schema")
    _require(record.get("pass") is True, f"{path.name} does not pass")
    script_key = str(script.relative_to(ROOT))
    recorded_digest = record.get("inputs", {}).get(script_key)
    _require(recorded_digest == _sha256(script), f"{path.name} is stale against {script.name}")
    return record


def _fraction(value: Any) -> Fraction:
    return Fraction(str(value))


def _gram_from_invariants(invariants: dict[str, Any]) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(_fraction(invariants[f"gram_{min(row, column) + 1}{max(row, column) + 1}"]) for column in range(4))
        for row in range(4)
    )


def _determinant(matrix: Sequence[Sequence[Fraction]]) -> Fraction:
    return frame_invariants._determinant(matrix)


def _principal_submatrix(
    matrix: Sequence[Sequence[Fraction]], indices: Sequence[int]
) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(tuple(matrix[row][column] for column in indices) for row in indices)


def _three_form_value(invariants: dict[str, Any], indices: tuple[int, int, int]) -> Fraction:
    return _fraction(invariants["phi_" + "".join(str(index + 1) for index in indices)])


def _associative_rank_three(invariants: dict[str, Any], mutation: str) -> bool:
    gram = _gram_from_invariants(invariants)
    comparisons = []
    for indices in itertools.combinations(range(4), 3):
        determinant = _determinant(_principal_submatrix(gram, indices))
        if determinant:
            three_form = Fraction(0) if mutation == "ignore_three_forms" else _three_form_value(invariants, indices)
            comparisons.append(three_form * three_form == determinant)
    return bool(comparisons) and all(comparisons)


def _three_forms_zero(invariants: dict[str, Any], mutation: str) -> bool:
    if mutation == "ignore_three_forms":
        return True
    return all(_three_form_value(invariants, indices) == 0 for indices in itertools.combinations(range(4), 3))


def _predicted_connected_group(orbit_name: str, real_frame_rank: int, invariants: dict[str, Any], mutation: str) -> str:
    if orbit_name == "Iso":
        return "U(1)" if _three_forms_zero(invariants, mutation) else "trivial"
    if real_frame_rank == 2 or (real_frame_rank == 3 and _associative_rank_three(invariants, mutation)):
        return "SU(2)"
    return "trivial"


def _sample_classification_row(
    task: tuple[dict[str, Any], dict[tuple[str, str], dict[str, Any]], str],
) -> dict[str, Any]:
    sample_row, invariant_rows, mutation = task
    orbit_name = str(sample_row["orbit"])
    move_name = str(sample_row["move"])
    invariant_row = invariant_rows[(orbit_name, move_name)]
    predicted_group = _predicted_connected_group(
        orbit_name,
        int(invariant_row["real_frame_rank"]),
        invariant_row["raw_invariants"],
        mutation,
    )
    observed_group = str(sample_row["representation"]["connected_group"])
    return {
        "orbit": orbit_name,
        "move": move_name,
        "real_frame_rank": invariant_row["real_frame_rank"],
        "associative_rank_three": _associative_rank_three(invariant_row["raw_invariants"], mutation),
        "three_forms_zero": _three_forms_zero(invariant_row["raw_invariants"], mutation),
        "predicted_connected_group": predicted_group,
        "observed_connected_group": observed_group,
        "matches": predicted_group == observed_group,
    }


def _standard_basis(index: int) -> Vector:
    return tuple(Fraction(coordinate == index) for coordinate in range(7))


def _state_from_frame(frame: Frame) -> Vector:
    return tuple([*(coordinate for vector in frame for coordinate in vector), Fraction(0), Fraction(0)])


def _real_point_from_state(state: Vector) -> Vector:
    _require(len(state) == 30, "a frame state must have thirty coordinates")
    point = [Fraction(0)] * 32
    point[1:8] = state[0:7]
    point[17:24] = state[7:14]
    point[9:16] = state[14:21]
    point[25:32] = state[21:28]
    point[8] = state[28]
    point[24] = state[29]
    return tuple(point)


def _split_from_real_point(point: Sequence[Fraction]) -> GaussianPoint:
    split = []
    for index in range(1, 16):
        original = independent.Gq(point[index], point[16 + index])
        split.append(independent.i_pow(-independent.popcount(index)) * original)
    return tuple(split)


def _format_gaussian(value: independent.Gq) -> list[str]:
    return [str(value.re), str(value.im)]


def _invariant_values(state: Vector) -> dict[str, Fraction]:
    frame = remaining_moduli._frame(state)
    return {name: function(frame) for name, function in frame_invariants._invariant_functions("")}


def _coassociative_quartets() -> tuple[tuple[int, int, int, int], ...]:
    quartets = []
    for indices in itertools.combinations(range(7), 4):
        vectors = tuple(_standard_basis(index) for index in indices)
        if all(
            frame_invariants._three_form(vectors[first], vectors[second], vectors[third]) == 0
            for first, second, third in itertools.combinations(range(4), 3)
        ):
            quartets.append(indices)
    return tuple(quartets)


def _coassociative_candidate(task: tuple[tuple[int, int, int, int], int]) -> Candidate:
    indices, sign = task
    frame: Frame = (
        _standard_basis(indices[0]),
        _standard_basis(indices[1]),
        _standard_basis(indices[2]),
        tuple(sign * value for value in _standard_basis(indices[3])),
    )
    state = _state_from_frame(frame)
    point = _real_point_from_state(state)
    split_point = _split_from_real_point(point)
    membership = independent.membership(split_point)
    summary = {
        "basis_indices": [index + 1 for index in indices],
        "fourth_vector_sign": sign,
        "nullity_Ly": independent.nullity_ly(split_point),
        "closure_membership_pattern": independent.pattern(split_point),
        "is_open_Iso": independent.pattern(split_point) == independent.pattern(independent.REPS["Iso"]),
        "is_B9": membership["B9"],
        "split_point": [_format_gaussian(value) for value in split_point],
    }
    return summary, point, split_point


def _w8_associative_point() -> Candidate:
    frame: Frame = (
        _standard_basis(0),
        tuple(Fraction(3, 5) * value for value in _standard_basis(2)),
        tuple(Fraction(4, 5) * value for value in _standard_basis(1)),
        (Fraction(0),) * 7,
    )
    state = _state_from_frame(frame)
    point = _real_point_from_state(state)
    split_point = _split_from_real_point(point)
    summary = {
        "canonical_frame": "(e_1,(3/5)e_3,(4/5)e_2,0)",
        "nullity_Ly": independent.nullity_ly(split_point),
        "closure_membership_pattern": independent.pattern(split_point),
        "is_open_W8": independent.pattern(split_point) == independent.pattern(independent.REPS["W8"]),
        "split_point": [_format_gaussian(value) for value in split_point],
    }
    return summary, point, split_point


def _kernel_preserved_task(
    task: tuple[RationalMatrix, RationalMatrix, tuple[tuple[Fraction, ...], ...]],
) -> bool:
    left_matrix, domain, adapted_basis = task
    return all(
        not any(stabilizer._matrix_vector(left_matrix, stabilizer._matrix_vector(domain, vector)))
        for vector in adapted_basis
    )


def _fiber_matrix_task(
    task: tuple[RationalMatrix, tuple[tuple[Fraction, ...], ...], RationalMatrix],
) -> sp.Matrix:
    domain, adapted_basis, complex_structure = task
    return aligned_representation._fiber_matrix(domain, adapted_basis, complex_structure)


def _circle_representation(
    coefficient_rows: Sequence[Sequence[Fraction]], fiber_matrices: Sequence[sp.Matrix]
) -> dict[str, Any]:
    _require(len(coefficient_rows) == 1 and len(fiber_matrices) == 1, "circle representation requires one generator")
    phase_coefficient = coefficient_rows[0][-1]
    _require(phase_coefficient != 0, "circle stabilizer has zero phase projection")
    primitive_fiber = sp.simplify(
        fiber_matrices[0] / sp.Rational(phase_coefficient.numerator, phase_coefficient.denominator)
    )
    weights = []
    total_dimension = 0
    all_integral = True
    for eigenvalue, multiplicity in sorted(
        primitive_fiber.eigenvals().items(), key=lambda item: sp.default_sort_key(item[0])
    ):
        weight = sp.simplify(eigenvalue / sp.I)
        all_integral &= weight.is_integer is True
        total_dimension += multiplicity
        weights.append({"weight": sp.sstr(weight), "multiplicity": multiplicity})
    return {
        "phase_normalization": "the base phase coefficient is one",
        "weight_multiplicities": weights,
        "complex_dimension": total_dimension,
        "pass": all_integral and total_dimension == samples.COMPLEX_FIBER_DIMENSION,
    }


def _analyze_canonical_point(label: str, candidate: Candidate, mutation: str) -> dict[str, Any]:
    summary, point, split_point = candidate
    tangent_rank, coefficient_rows, base_stabilizers, domain_stabilizers = samples._compact_data(point, "")
    point_fixed = [not any(stabilizer._matrix_vector(matrix, point)) for matrix in base_stabilizers]
    left_matrix = tuple(tuple(row) for row in left_mult_matrix_exact(32, point))
    complex_structure = aligned_representation._complex_structure()
    adapted_basis = aligned_representation._adapted_kernel_basis(
        left_matrix,
        complex_structure,
        samples.REAL_FIBER_DIMENSION,
    )
    kernel_preserved = parallel.ordered_map(
        _kernel_preserved_task,
        [(left_matrix, domain, adapted_basis) for domain in domain_stabilizers],
        min_items=1,
    )
    fiber_matrices = parallel.ordered_map(
        _fiber_matrix_task,
        [(domain, adapted_basis, complex_structure) for domain in domain_stabilizers],
        min_items=1,
    )
    commutators_match = aligned_representation._representation_commutators_match(
        domain_stabilizers,
        fiber_matrices,
        adapted_basis,
        complex_structure,
    )
    stabilizer_dimension = len(coefficient_rows)
    phase_projection_dimension = int(any(row[-1] for row in coefficient_rows))
    reported_phase_projection = 0 if mutation == "drop_phase_projection" else phase_projection_dimension
    if stabilizer_dimension == 1:
        representation = _circle_representation(coefficient_rows, fiber_matrices)
        connected_group = "U(1)" if reported_phase_projection == 1 else "unclassified"
    else:
        representation = samples._representation_data(
            domain_stabilizers,
            fiber_matrices,
            adapted_basis,
            complex_structure,
        )
        connected_group = str(representation["connected_group"])
    state = remaining_moduli._state_from_real_coordinates(point)
    invariants = _invariant_values(state)
    real_frame_rank = symmetry.equations.qrank(list(remaining_moduli._frame(state)))
    predicted_group = _predicted_connected_group(
        "Iso" if label == "Iso coassociative" else "W8",
        real_frame_rank,
        {name: str(value) for name, value in invariants.items()},
        mutation,
    )
    expected_pattern = independent.pattern(independent.REPS["Iso" if label == "Iso coassociative" else "W8"])
    row_pass = (
        independent.pattern(split_point) == expected_pattern
        and independent.nullity_ly(split_point) == 8
        and stabilizer_dimension == samples.COMPACT_GENERATOR_COUNT - tangent_rank
        and all(point_fixed)
        and all(kernel_preserved)
        and commutators_match
        and connected_group == predicted_group
        and representation["pass"]
    )
    return {
        "label": label,
        **summary,
        "real_frame_rank": real_frame_rank,
        "associative_rank_three": _associative_rank_three(
            {name: str(value) for name, value in invariants.items()}, mutation
        ),
        "three_forms_zero": _three_forms_zero({name: str(value) for name, value in invariants.items()}, mutation),
        "compact_tangent_rank": tangent_rank,
        "stabilizer_dimension": stabilizer_dimension,
        "phase_projection_dimension": phase_projection_dimension,
        "reported_phase_projection_dimension": reported_phase_projection,
        "predicted_connected_group": predicted_group,
        "computed_connected_group": connected_group,
        "point_fixed": point_fixed,
        "kernel_preserved": kernel_preserved,
        "representation_commutators_match": commutators_match,
        "representation": representation,
        "pass": row_pass,
    }


def _analyze_canonical_task(task: tuple[str, Candidate, str]) -> dict[str, Any]:
    label, candidate, mutation = task
    return _analyze_canonical_point(label, candidate, mutation)


def _load_sample_and_invariant_rows() -> tuple[dict[str, Any], dict[tuple[str, str], dict[str, Any]]]:
    sample_record = _load_bound_result(SAMPLE_RESULT, SAMPLE_SCRIPT, samples.SCHEMA)
    w8_record = _load_bound_result(
        W8_MODULI_RESULT,
        W8_MODULI_SCRIPT,
        frame_invariants.SCHEMA,
    )
    remaining_record = _load_bound_result(
        REMAINING_MODULI_RESULT,
        REMAINING_MODULI_SCRIPT,
        remaining_moduli.SCHEMA,
    )
    invariant_rows: dict[tuple[str, str], dict[str, Any]] = {("W8", str(row["move"])): row for row in w8_record["rows"]}
    invariant_rows.update({(str(row["orbit"]), str(row["move"])): row for row in remaining_record["rows"]})
    return sample_record, invariant_rows


def build_record(mutation: str = "") -> dict[str, Any]:
    if mutation not in MUTATIONS:
        raise ValueError(f"unknown mutation {mutation!r}")
    sample_record, invariant_rows = _load_sample_and_invariant_rows()
    sample_tasks = [(row, invariant_rows, mutation) for row in sample_record["rows"]]
    sample_classification = parallel.ordered_map(_sample_classification_row, sample_tasks, min_items=1)

    quartets = _coassociative_quartets()
    candidate_tasks = [(quartet, sign) for quartet in quartets for sign in (1, -1)]
    coassociative_candidates = parallel.ordered_map(_coassociative_candidate, candidate_tasks, min_items=1)
    open_iso_candidates = [candidate for candidate in coassociative_candidates if candidate[0]["is_open_Iso"]]
    _require(bool(open_iso_candidates), "the coassociative enumeration found no open Iso point")
    canonical_rows = parallel.ordered_map(
        _analyze_canonical_task,
        [
            ("W8 associative rank three", _w8_associative_point(), mutation),
            *(("Iso coassociative", candidate, mutation) for candidate in open_iso_candidates),
        ],
        min_items=1,
    )
    iso_rows = canonical_rows[1:]
    iso_weight_signatures = {
        tuple((entry["weight"], entry["multiplicity"]) for entry in row["representation"]["weight_multiplicities"])
        for row in iso_rows
    }
    candidate_summary = [candidate[0] for candidate in coassociative_candidates]
    return {
        "schema": SCHEMA,
        "mutation": mutation or None,
        "inputs": {str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS},
        "sample_classification": sample_classification,
        "canonical_rows": canonical_rows,
        "coassociative_enumeration": {
            "coassociative_coordinate_four_planes": len(quartets),
            "signed_null_two_plane_candidates": len(coassociative_candidates),
            "open_Iso_candidates": len(open_iso_candidates),
            "B9_candidates": sum(bool(candidate[0]["is_B9"]) for candidate in coassociative_candidates),
            "open_Iso_weight_signatures": [list(signature) for signature in sorted(iso_weight_signatures)],
            "open_Iso_weights_constant": len(iso_weight_signatures) == 1,
            "rows": candidate_summary,
        },
        "rank_minima_argument": {
            "W8": (
                "the nonzero common bilinear square and orthogonality force two independent real directions, so the "
                "real frame has rank at least two"
            ),
            "E8bar_X": (
                "rank at most two makes the split cross product leave the real two-plane unless it vanishes; the "
                "E8-bar equations then place the point in a lower orbit, so the open E8-bar and X branches have "
                "rank at least three"
            ),
            "Iso": (
                "two independent complex-isotropic vectors cannot lie in the complexification of a positive real "
                "three-plane, so the open Iso frame has rank four"
            ),
        },
        "classification_argument": {
            "phase_projection": (
                "W8 has a nonzero complex bilinear square, E8-bar has nonzero mu, and each open X branch lies "
                "outside Iso, so a nonzero quadratic scalar kills the infinitesimal phase projection there. On "
                "Iso the Gram and four-form data are circle-fixed, while the third-exterior-power action fixes the "
                "associative three-form vector exactly when that vector vanishes."
            ),
            "pointwise_g2": (
                "the pointwise compact G_2 stabilizer is SU(2) for a real two-frame or an associative real "
                "three-frame, and is trivial for a nonassociative real three-frame or a real frame of rank at least "
                "four"
            ),
            "strata": {
                "W8": "SU(2) at rank two and associative rank three; trivial otherwise",
                "E8bar": "SU(2) at associative rank three; trivial at rank four",
                "Iso": "U(1) where all four associative three-form values vanish; trivial otherwise",
                "X+": "SU(2) at associative rank three; trivial at rank four",
                "X-": "SU(2) at associative rank three; trivial at rank four",
            },
        },
        "pass": (
            mutation == ""
            and all(row["matches"] for row in sample_classification)
            and all(row["pass"] for row in canonical_rows)
            and len(iso_weight_signatures) == 1
        ),
    }


def _build_record_task(mutation: str) -> dict[str, Any]:
    return build_record(mutation)


def self_test() -> None:
    normal, form_mutation, phase_mutation = parallel.ordered_map(
        _build_record_task,
        list(MUTATIONS),
        min_items=1,
    )
    _require(normal["pass"], "normal stabilizer-stratum record failed")
    _require(not form_mutation["pass"], "three-form mutation survived")
    _require(
        any(not row["matches"] for row in form_mutation["sample_classification"]),
        "three-form mutation changed no downstream sample classification",
    )
    _require(not phase_mutation["pass"], "phase-projection mutation survived")
    _require(
        any(not row["pass"] for row in phase_mutation["canonical_rows"]),
        "phase-projection mutation changed no downstream canonical stratum",
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
        expected = arguments.check.read_bytes()
        actual = _record_bytes(build_record())
        _require(actual == expected, f"record differs from {arguments.check}")
    if not arguments.self_test and arguments.out is None and arguments.check is None:
        parser.error("select --out, --check, or --self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
