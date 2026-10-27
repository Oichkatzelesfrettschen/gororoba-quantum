"""Exact Pfaffian-chart transitions on every high-nullity A_5 piece.

Every rank-r bordered skew matrix has a nonzero principal order-r Pfaffian.
The corresponding Schur frames therefore give a finite atlas.  On an overlap,
the target frame restricted to the source free rows is the transition matrix.
This replay verifies reconstruction, inverses, triple cocycles, Hermitian Gram
transport, and real complex-linearity on three simultaneous charts per piece.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import kernel_frames as frames  # noqa: E402
import kernel_symmetry as symmetry  # noqa: E402

FRAMES_RESULT = HERE / "frames-result.json"
FRAMES_SCRIPT = HERE / "kernel_frames.py"
SYMMETRY_RESULT = HERE / "result.json"
SYMMETRY_SCRIPT = HERE / "kernel_symmetry.py"
NULLITY_SIXTEEN_RESULT = HERE / "nullity-sixteen-bundle-result.json"
NULLITY_SIXTEEN_SCRIPT = HERE / "nullity_sixteen_bundle.py"

NULLITY_TWELVE_PIECES = tuple(frames.NULLITY_TWELVE_ORBITS)
NULLITY_SIXTEEN_PIECES = tuple(frames.ORBIT_SIGNS)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _matrix_text(matrix: sp.Matrix) -> list[list[str]]:
    return [[sp.sstr(matrix[row, column]) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _find_three_pivots(matrix: sp.Matrix, matrix_rank: int) -> tuple[tuple[int, ...], ...]:
    pivots: list[tuple[int, ...]] = []
    for candidate in itertools.combinations(range(frames.BORDERED_DIMENSION), matrix_rank):
        if matrix.extract(candidate, candidate).det() != 0:
            pivots.append(candidate)
            if len(pivots) == 3:
                break
    _require(len(pivots) == 3, "fixture has fewer than three simultaneous principal-Pfaffian charts")
    return tuple(pivots)


def _transition(source_frame: sp.Matrix, source_pivot: Sequence[int], target_frame: sp.Matrix) -> sp.Matrix:
    source_free = tuple(index for index in range(frames.BORDERED_DIMENSION) if index not in source_pivot)
    return target_frame.extract(source_free, range(target_frame.cols))


def _realify_transition(transition: sp.Matrix) -> sp.Matrix:
    realified = sp.zeros(2 * transition.rows, 2 * transition.cols)
    for row in range(transition.rows):
        for column in range(transition.cols):
            real_part, imaginary_part = sp.expand_complex(transition[row, column]).as_real_imag()
            real_part = sp.expand(real_part)
            imaginary_part = sp.expand(imaginary_part)
            realified[2 * row, 2 * column] = real_part
            realified[2 * row, 2 * column + 1] = -imaginary_part
            realified[2 * row + 1, 2 * column] = imaginary_part
            realified[2 * row + 1, 2 * column + 1] = real_part
    return realified


def _fiber_complex_structure(complex_dimension: int) -> sp.Matrix:
    complex_structure = sp.zeros(2 * complex_dimension)
    for coordinate in range(complex_dimension):
        complex_structure[2 * coordinate, 2 * coordinate + 1] = 1
        complex_structure[2 * coordinate + 1, 2 * coordinate] = -1
    return complex_structure


def _piece_matrix(piece: str, parameter: str | int) -> tuple[sp.Matrix, int]:
    if isinstance(parameter, str):
        split_point = frames.regularity.REPS[parameter]
        z = frames._original_z_from_split(split_point)
        return frames._bordered_matrix(z), frames.NULLITY_TWELVE_MATRIX_RANK
    z = frames._nullity_sixteen_z(0, 1, parameter)
    return frames._bordered_matrix(z), frames.FRAME_RANK


def _fixture_task(task: tuple[str, str | int, str]) -> dict[str, Any]:
    piece, parameter, mutation = task
    matrix, matrix_rank = _piece_matrix(piece, parameter)
    complex_dimension = frames.BORDERED_DIMENSION - matrix_rank
    pivots = _find_three_pivots(matrix, matrix_rank)
    frame_rows = [frames._principal_frame(matrix, pivot) for pivot in pivots]
    local_frames = [row[0] for row in frame_rows]
    determinants = [sp.factor(row[1]) for row in frame_rows]
    pfaffians = [sp.factor(row[2]) for row in frame_rows]
    transitions: dict[tuple[int, int], sp.Matrix] = {}
    for source in range(3):
        for target in range(3):
            transition = _transition(local_frames[source], pivots[source], local_frames[target])
            if mutation == "perturb_transition" and (source, target) == (0, 1):
                transition = transition.copy()
                transition[0, 0] += 1
            transitions[source, target] = transition
    if mutation not in ("", "perturb_transition", "transpose_metric"):
        raise ValueError(f"unknown transition mutation {mutation!r}")

    identity = sp.eye(complex_dimension)
    zero = sp.zeros(frames.BORDERED_DIMENSION, complex_dimension)
    frame_identities = [matrix * local_frame == zero for local_frame in local_frames]
    reconstruction = all(
        local_frames[source] * transitions[source, target] == local_frames[target]
        for source in range(3)
        for target in range(3)
    )
    inverses = all(
        sp.simplify(transitions[source, target] * transitions[target, source]) == identity
        for source in range(3)
        for target in range(3)
    )
    cocycles = all(
        sp.simplify(transitions[first, middle] * transitions[middle, last] - transitions[first, last])
        == sp.zeros(complex_dimension)
        for first in range(3)
        for middle in range(3)
        for last in range(3)
    )
    transition_determinants = {
        f"{source}->{target}": sp.factor(transitions[source, target].det())
        for source in range(3)
        for target in range(3)
    }
    invertible = all(value != 0 for value in transition_determinants.values())

    gram_matrices = [sp.simplify(local_frame.conjugate().T * local_frame) for local_frame in local_frames]
    metric_transport_checks: list[bool] = []
    for source in range(3):
        for target in range(3):
            transition = transitions[source, target]
            adjoint = transition.T if mutation == "transpose_metric" else transition.conjugate().T
            metric_transport_checks.append(
                sp.simplify(adjoint * gram_matrices[source] * transition - gram_matrices[target])
                == sp.zeros(complex_dimension)
            )
    metric_transport = all(metric_transport_checks)
    raw_transition_unitary = all(
        sp.simplify(transition.conjugate().T * transition) == identity for transition in transitions.values()
    )

    fiber_complex_structure = _fiber_complex_structure(complex_dimension)
    real_complex_linearity = all(
        sp.simplify(_realify_transition(transition) * fiber_complex_structure)
        == sp.simplify(fiber_complex_structure * _realify_transition(transition))
        for transition in transitions.values()
    )
    pass_value = (
        mutation == ""
        and all(frame_identities)
        and all(value != 0 for value in determinants)
        and all(value != 0 for value in pfaffians)
        and all(
            sp.expand(determinant - pfaffian * pfaffian) == 0
            for determinant, pfaffian in zip(determinants, pfaffians, strict=True)
        )
        and reconstruction
        and inverses
        and cocycles
        and invertible
        and metric_transport
        and real_complex_linearity
    )
    return {
        "piece": piece,
        "matrix_rank": matrix_rank,
        "complex_kernel_rank": complex_dimension,
        "chart_count": math.comb(frames.BORDERED_DIMENSION, matrix_rank),
        "triple_overlap_pivots": [list(pivot) for pivot in pivots],
        "triple_overlap_pfaffians": [sp.sstr(value) for value in pfaffians],
        "triple_overlap_determinants": [sp.sstr(value) for value in determinants],
        "frame_identities": frame_identities,
        "transition_reconstruction": reconstruction,
        "transition_inverse": inverses,
        "transition_cocycle": cocycles,
        "transition_determinants": {key: sp.sstr(value) for key, value in transition_determinants.items()},
        "transitions_invertible": invertible,
        "hermitian_gram_transport": metric_transport,
        "raw_transitions_all_unitary": raw_transition_unitary,
        "realified_transitions_commute_with_J": real_complex_linearity,
        "sample_transition_0_to_1": _matrix_text(transitions[0, 1]),
        "mutation": mutation,
        "pass": pass_value,
    }


def _load_inputs() -> tuple[dict[str, str], dict[str, Any]]:
    bindings = (
        ("frames", FRAMES_RESULT, FRAMES_SCRIPT, "a5-high-nullity-kernel-frames-v2", "source_sha256"),
        ("symmetry", SYMMETRY_RESULT, SYMMETRY_SCRIPT, "a5-kernel-symmetry-v3", "script_sha256"),
        (
            "nullity_sixteen_bundle",
            NULLITY_SIXTEEN_RESULT,
            NULLITY_SIXTEEN_SCRIPT,
            "a5-nullity-sixteen-bundle-invariants-v2",
            "script_sha256",
        ),
    )
    digests: dict[str, str] = {}
    loaded: dict[str, Any] = {}
    for label, result_path, script_path, schema, digest_key in bindings:
        result = json.loads(result_path.read_text(encoding="utf-8"))
        script_digest = hashlib.sha256(script_path.read_bytes()).hexdigest()
        _require(result.get("schema") == schema, f"{result_path.name} has an unexpected schema")
        _require(result.get("pass") is True, f"{result_path.name} does not pass")
        _require(result.get(digest_key) == script_digest, f"{result_path.name} is stale against its producer")
        digests[f"{label}_result_sha256"] = hashlib.sha256(result_path.read_bytes()).hexdigest()
        digests[f"{label}_script_sha256"] = script_digest
        loaded[label] = result
    return digests, loaded


def transition_atlas_checks(mutation: str = "") -> dict[str, Any]:
    if mutation not in ("", "perturb_transition", "transpose_metric"):
        raise ValueError(f"unknown mutation {mutation!r}")
    input_digests, inputs = _load_inputs()
    if mutation:
        rows = [_fixture_task(("B9", "B9", mutation))]
        return {
            "mutation": mutation,
            "input_digests": input_digests,
            "rows": rows,
            "pass": all(row["pass"] for row in rows),
        }

    tasks = [
        *((piece_label, piece_key, "") for piece_key, piece_label in NULLITY_TWELVE_PIECES),
        *((piece_label, sign, "") for piece_label, sign in NULLITY_SIXTEEN_PIECES),
    ]
    rows = symmetry.parallel.ordered_map(_fixture_task, tasks, min_items=1)
    nullity_sixteen_transition = inputs["nullity_sixteen_bundle"]["bundle"]["transition"]
    nullity_sixteen_reduction_matches = (
        nullity_sixteen_transition["pass"] is True
        and nullity_sixteen_transition["representation"] == "diag(I_2,Q,Q,Q)"
        and nullity_sixteen_transition["structure_group"] == "diagonal SU(2)=Sp(1) inside Sp(4) and SU(8)"
    )
    vertical_decomposition = inputs["symmetry"]["lie_algebra"]["decomposition"]
    constant_vertical_complex_only = (
        inputs["symmetry"]["lie_algebra"]["vertical_dimension"] == 2
        and vertical_decomposition["domain_scaling"] == 1
        and vertical_decomposition["vertical_j_phase"] == 1
    )
    return {
        "mutation": mutation,
        "input_digests": input_digests,
        "atlas": {
            "nullity_twelve_pieces": [piece_label for _piece_key, piece_label in NULLITY_TWELVE_PIECES],
            "nullity_twelve_charts_per_piece": frames.NULLITY_TWELVE_CHART_COUNT,
            "nullity_sixteen_pieces": [piece_label for piece_label, _sign in NULLITY_SIXTEEN_PIECES],
            "nullity_sixteen_charts_per_piece": frames.CHART_COUNT,
            "chart_domain": "U_I={y:pf(A(z,conjugate(z))_I,I)!=0}",
            "coverage": (
                "on a rank-r skew matrix, the principal-rank theorem supplies a nonzero principal order-r Pfaffian"
            ),
            "frame": "F_I=[-B_I^(-1) C_I;I] in pivot/free rows",
            "transition": "g_IJ=(F_J)_(I-complement), so F_J=F_I g_IJ",
            "inverse": "g_IJ g_JI=I",
            "cocycle": "g_IJ g_JK=g_IK",
            "metric": "G_J=g_IJ^* G_I g_IJ for G_I=F_I^* F_I",
        },
        "structure_groups": {
            "nullity_twelve_raw": "GL(6,C)",
            "nullity_twelve_metric_reduction": "U(6)",
            "nullity_sixteen_raw": "GL(8,C)",
            "nullity_sixteen_metric_reduction": "U(8)",
            "nullity_sixteen_further_reduction": "diagonal SU(2)=Sp(1) inside Sp(4) and SU(8)",
            "realification": "GL(k,C) embeds in GL(2k,R) as the centralizer of J",
            "quaternionic_scope": (
                "the constant vertical symmetry algebra is span_R{I,J}; it supplies no constant second complex "
                "structure on the nullity-twelve family, so no canonical Sp(3) reduction is asserted"
            ),
        },
        "constant_vertical_complex_only": constant_vertical_complex_only,
        "nullity_sixteen_reduction_matches_committed_result": nullity_sixteen_reduction_matches,
        "rows": rows,
        "pass": all(row["pass"] for row in rows)
        and constant_vertical_complex_only
        and nullity_sixteen_reduction_matches,
    }


def build_result() -> dict[str, Any]:
    result = transition_atlas_checks()
    return {
        "schema": "a5-high-nullity-transition-atlas-v1",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "transition_atlas": result,
        "pass": result["pass"],
    }


def _self_test_mutation_task(mutation: str) -> tuple[str, dict[str, Any]]:
    """Build one independent atlas mutation for the parent self-test."""
    return mutation, transition_atlas_checks(mutation)


def self_test() -> None:
    baseline = transition_atlas_checks()
    if not baseline["pass"]:
        raise RuntimeError("baseline high-nullity transition-atlas check failed")
    mutations = dict(
        symmetry.parallel.ordered_map(
            _self_test_mutation_task,
            ["perturb_transition", "transpose_metric"],
            min_items=1,
        )
    )
    transition_mutation = mutations["perturb_transition"]
    transition_row = transition_mutation["rows"][0]
    if (
        transition_mutation["pass"]
        or transition_row["transition_reconstruction"]
        or transition_row["transition_inverse"]
        or transition_row["transition_cocycle"]
    ):
        raise RuntimeError("transition-entry mutation survived reconstruction, inverse, or cocycle checks")
    metric_mutation = mutations["transpose_metric"]
    if metric_mutation["pass"] or metric_mutation["rows"][0]["hermitian_gram_transport"]:
        raise RuntimeError("transpose-instead-of-adjoint mutation survived Hermitian Gram transport")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.check is not None and (arguments.self_test or arguments.out is not None):
        parser.error("--check cannot be combined with --self-test or --out")
    if arguments.self_test:
        self_test()
        print("PASS: high-nullity transition-atlas self-test")
    if arguments.out is not None or arguments.check is not None:
        result = build_result()
        payload = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
        if arguments.check is not None:
            if payload != arguments.check.read_bytes():
                raise SystemExit(f"transition_atlas.py: fresh JSON differs byte-for-byte from {arguments.check}")
            print(f"transition_atlas.py: fresh JSON matches {arguments.check}")
        else:
            arguments.out.write_bytes(payload)
            print(f"wrote {arguments.out}")
    if not arguments.self_test and arguments.out is None and arguments.check is None:
        parser.error("choose --self-test, --out, or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
