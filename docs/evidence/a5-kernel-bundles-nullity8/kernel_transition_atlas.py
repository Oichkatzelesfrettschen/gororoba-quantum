"""Exact Pfaffian-frame transitions on the five nullity-eight A_5 orbits.

A rank-twelve bordered skew matrix has a nonzero principal order-twelve
Pfaffian.  The corresponding Schur frame has four columns, and the 1,820
principal charts therefore cover each nullity-eight orbit.  This producer
checks the frame construction and all overlap identities on three exact
simultaneous charts at one point of every orbit.
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
KERNEL_BUNDLES = HERE.parent / "a5-kernel-bundles"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(KERNEL_BUNDLES))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import kernel_frames as frames  # noqa: E402

import parallel  # noqa: E402
from cd_core import left_mult_matrix_exact  # noqa: E402

SCHEMA = "a5-kernel-bundles-nullity8-transition-atlas-v1"
MATRIX_RANK = 12
COMPLEX_KERNEL_RANK = frames.BORDERED_DIMENSION - MATRIX_RANK
CHART_COUNT = math.comb(frames.BORDERED_DIMENSION, MATRIX_RANK)
ORBIT_KEYS = (
    ("W8", "W8"),
    ("Ehat", "E8-bar"),
    ("Iso", "Iso"),
    ("Xp", "X_+"),
    ("Xm", "X_-"),
)
SOURCE_PATHS = (
    HERE / "kernel_transition_atlas.py",
    HERE / "compact_orbit_ranks.py",
    KERNEL_BUNDLES / "kernel_frames.py",
    KERNEL_BUNDLES / "frames-result.json",
)
MUTATIONS = ("", "drop_matrix_entry", "perturb_transition", "transpose_metric")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_text(matrix: sp.Matrix) -> list[list[str]]:
    return [[sp.sstr(matrix[row, column]) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _find_three_pivots(matrix: sp.Matrix) -> tuple[tuple[int, ...], ...]:
    pivots: list[tuple[int, ...]] = []
    for candidate in itertools.combinations(range(frames.BORDERED_DIMENSION), MATRIX_RANK):
        if matrix.extract(candidate, candidate).det() != 0:
            pivots.append(candidate)
            if len(pivots) == 3:
                break
    _require(len(pivots) == 3, "fixture has fewer than three simultaneous principal-Pfaffian charts")
    return tuple(pivots)


def _transition(source_pivot: Sequence[int], target_frame: sp.Matrix) -> sp.Matrix:
    source_free = tuple(index for index in range(frames.BORDERED_DIMENSION) if index not in source_pivot)
    return target_frame.extract(source_free, range(target_frame.cols))


def _realify_transition(transition: sp.Matrix) -> sp.Matrix:
    realified = sp.zeros(2 * transition.rows, 2 * transition.cols)
    for row in range(transition.rows):
        for column in range(transition.cols):
            real_part, imaginary_part = sp.expand_complex(transition[row, column]).as_real_imag()
            realified[2 * row, 2 * column] = sp.expand(real_part)
            realified[2 * row, 2 * column + 1] = -sp.expand(imaginary_part)
            realified[2 * row + 1, 2 * column] = sp.expand(imaginary_part)
            realified[2 * row + 1, 2 * column + 1] = sp.expand(real_part)
    return realified


def _fiber_complex_structure() -> sp.Matrix:
    complex_structure = sp.zeros(2 * COMPLEX_KERNEL_RANK)
    for coordinate in range(COMPLEX_KERNEL_RANK):
        complex_structure[2 * coordinate, 2 * coordinate + 1] = 1
        complex_structure[2 * coordinate + 1, 2 * coordinate] = -1
    return complex_structure


def _matrix_for_orbit(orbit_key: str) -> tuple[tuple[sp.Expr, ...], sp.Matrix]:
    split_point = frames.regularity.REPS[orbit_key]
    original_point = frames._original_z_from_split(split_point)
    matrix = frames._bordered_matrix(original_point)
    _require(matrix.T == -matrix, f"{orbit_key} bordered matrix is not skew")
    _require(matrix.rank() == MATRIX_RANK, f"{orbit_key} bordered matrix does not have rank twelve")
    return original_point, matrix


def _drop_effective_matrix_entry(matrix: sp.Matrix, frame: sp.Matrix) -> tuple[sp.Matrix, tuple[int, int]]:
    zero = sp.zeros(frames.BORDERED_DIMENSION, COMPLEX_KERNEL_RANK)
    for row in range(frames.BORDERED_DIMENSION):
        for column in range(row + 1, frames.BORDERED_DIMENSION):
            if matrix[row, column] == 0:
                continue
            mutated = matrix.copy()
            mutated[row, column] = 0
            mutated[column, row] = 0
            if mutated * frame != zero:
                return mutated, (row, column)
    raise RuntimeError("every nonzero matrix-entry deletion left the kernel frame unchanged")


def _fixture_task(task: tuple[str, str, str]) -> dict[str, Any]:
    orbit_key, orbit_label, mutation = task
    if mutation not in MUTATIONS:
        raise ValueError(f"unknown transition-atlas mutation {mutation!r}")
    original_point, matrix = _matrix_for_orbit(orbit_key)
    pivots = _find_three_pivots(matrix)
    frame_rows = [frames._principal_frame(matrix, pivot) for pivot in pivots]
    local_frames = [row[0] for row in frame_rows]
    determinants = [sp.factor(row[1]) for row in frame_rows]
    pfaffians = [sp.factor(row[2]) for row in frame_rows]

    tested_matrix = matrix
    dropped_entry: tuple[int, int] | None = None
    if mutation == "drop_matrix_entry":
        tested_matrix, dropped_entry = _drop_effective_matrix_entry(matrix, local_frames[0])

    transitions: dict[tuple[int, int], sp.Matrix] = {}
    for source in range(3):
        for target in range(3):
            transition = _transition(pivots[source], local_frames[target])
            if mutation == "perturb_transition" and (source, target) == (0, 1):
                transition = transition.copy()
                transition[0, 0] += 1
            transitions[source, target] = transition

    identity = sp.eye(COMPLEX_KERNEL_RANK)
    zero = sp.zeros(frames.BORDERED_DIMENSION, COMPLEX_KERNEL_RANK)
    frame_identities = [tested_matrix * local_frame == zero for local_frame in local_frames]
    free_row_identities = [
        local_frame.extract(
            tuple(index for index in range(frames.BORDERED_DIMENSION) if index not in pivot),
            range(COMPLEX_KERNEL_RANK),
        )
        == identity
        for pivot, local_frame in zip(pivots, local_frames, strict=True)
    ]
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
        == sp.zeros(COMPLEX_KERNEL_RANK)
        for first in range(3)
        for middle in range(3)
        for last in range(3)
    )
    transition_determinants = {
        f"{source}->{target}": sp.factor(transitions[source, target].det())
        for source in range(3)
        for target in range(3)
    }
    transitions_invertible = all(value != 0 for value in transition_determinants.values())

    gram_matrices = [sp.simplify(local_frame.conjugate().T * local_frame) for local_frame in local_frames]
    metric_transport_checks: list[bool] = []
    for source in range(3):
        for target in range(3):
            transition = transitions[source, target]
            adjoint = transition.T if mutation == "transpose_metric" else transition.conjugate().T
            metric_transport_checks.append(
                sp.simplify(adjoint * gram_matrices[source] * transition - gram_matrices[target])
                == sp.zeros(COMPLEX_KERNEL_RANK)
            )
    metric_transport = all(metric_transport_checks)

    complex_structure = _fiber_complex_structure()
    real_complex_linearity = all(
        sp.simplify(_realify_transition(transition) * complex_structure)
        == sp.simplify(complex_structure * _realify_transition(transition))
        for transition in transitions.values()
    )

    real_point = frames._real_coordinates_from_z(original_point)
    left_matrix = sp.Matrix(left_mult_matrix_exact(32, real_point))
    real_frames = [frames._real_kernel_frame(local_frame) for local_frame in local_frames]
    real_kernel_identities = [
        left_matrix * real_frame == sp.zeros(32, 2 * COMPLEX_KERNEL_RANK) for real_frame in real_frames
    ]
    real_frame_ranks = [real_frame.rank() for real_frame in real_frames]

    pass_value = (
        all(frame_identities)
        and all(free_row_identities)
        and all(value != 0 for value in determinants)
        and all(value != 0 for value in pfaffians)
        and all(
            sp.expand(determinant - pfaffian * pfaffian) == 0
            for determinant, pfaffian in zip(determinants, pfaffians, strict=True)
        )
        and reconstruction
        and inverses
        and cocycles
        and transitions_invertible
        and metric_transport
        and real_complex_linearity
        and all(real_kernel_identities)
        and all(rank == 2 * COMPLEX_KERNEL_RANK for rank in real_frame_ranks)
    )
    return {
        "orbit": orbit_label,
        "representative_key": orbit_key,
        "matrix_rank": matrix.rank(),
        "complex_kernel_rank": COMPLEX_KERNEL_RANK,
        "chart_count": CHART_COUNT,
        "triple_overlap_pivots": [list(pivot) for pivot in pivots],
        "triple_overlap_pfaffians": [sp.sstr(value) for value in pfaffians],
        "triple_overlap_determinants": [sp.sstr(value) for value in determinants],
        "frame_identities": frame_identities,
        "free_row_identities": free_row_identities,
        "real_kernel_identities": real_kernel_identities,
        "real_frame_ranks": real_frame_ranks,
        "transition_reconstruction": reconstruction,
        "transition_inverse": inverses,
        "transition_cocycle": cocycles,
        "transition_determinants": {key: sp.sstr(value) for key, value in transition_determinants.items()},
        "transitions_invertible": transitions_invertible,
        "hermitian_gram_transport": metric_transport,
        "realified_transitions_commute_with_J": real_complex_linearity,
        "sample_transition_0_to_1": _matrix_text(transitions[0, 1]),
        "mutation": mutation or None,
        "dropped_matrix_entry": list(dropped_entry) if dropped_entry is not None else None,
        "pass": pass_value,
    }


def transition_atlas_checks(mutation: str = "") -> dict[str, Any]:
    if mutation not in MUTATIONS:
        raise ValueError(f"unknown transition-atlas mutation {mutation!r}")
    tasks = [(orbit_key, orbit_label, mutation) for orbit_key, orbit_label in ORBIT_KEYS]
    rows = parallel.ordered_map(_fixture_task, tasks, min_items=1)
    return {
        "mutation": mutation or None,
        "atlas": {
            "orbits": [orbit_label for _orbit_key, orbit_label in ORBIT_KEYS],
            "bordered_rank": MATRIX_RANK,
            "complex_kernel_rank": COMPLEX_KERNEL_RANK,
            "charts_per_orbit": CHART_COUNT,
            "chart_indexing": "all 12-subsets I of {0,...,15}",
            "chart_domain": "U_I={y:pf(A(z,conjugate(z))_(I,I))!=0}",
            "coverage": (
                "a rank-twelve skew matrix has a nonzero principal order-twelve Pfaffian by the principal-rank theorem"
            ),
            "frame": "F_I=[-B_I^(-1) C_I;I_4] in pivot/free rows",
            "transition": "g_IJ=P_I F_J, so F_J=F_I g_IJ",
            "inverse": "g_IJ g_JI=I_4",
            "cocycle": "g_IJ g_JK=g_IK",
            "metric": "G_J=g_IJ^* G_I g_IJ for G_I=F_I^* F_I",
        },
        "structure_group": {
            "raw": "GL(4,C)",
            "metric_reduction": "U(4)",
            "realification": "GL(4,C) embeds in GL(8,R) as the centralizer of J",
            "scope": (
                "the Pfaffian atlas and ambient Hermitian metric establish U(4); orbit-specific smaller reductions "
                "require the bundle-class calculation"
            ),
        },
        "rows": rows,
        "pass": all(row["pass"] for row in rows),
    }


def _mutation_task(mutation: str) -> tuple[str, dict[str, Any]]:
    return mutation, transition_atlas_checks(mutation)


def build_record() -> dict[str, Any]:
    baseline = transition_atlas_checks()
    mutations = dict(
        parallel.ordered_map(
            _mutation_task,
            ["drop_matrix_entry", "perturb_transition", "transpose_metric"],
            min_items=1,
        )
    )
    matrix_mutation = mutations["drop_matrix_entry"]
    transition_mutation = mutations["perturb_transition"]
    metric_mutation = mutations["transpose_metric"]
    mutation_control = {
        "drop_matrix_entry": {
            "detected": not matrix_mutation["pass"],
            "frame_identity_changed": any(not all(row["frame_identities"]) for row in matrix_mutation["rows"]),
        },
        "perturb_transition": {
            "detected": not transition_mutation["pass"],
            "reconstruction_inverse_and_cocycle_changed": any(
                not row["transition_reconstruction"] and not row["transition_inverse"] and not row["transition_cocycle"]
                for row in transition_mutation["rows"]
            ),
        },
        "transpose_metric": {
            "detected": not metric_mutation["pass"],
            "hermitian_transport_changed": any(not row["hermitian_gram_transport"] for row in metric_mutation["rows"]),
        },
    }
    return {
        "schema": SCHEMA,
        "inputs": {str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS},
        **baseline,
        "mutation_control": mutation_control,
        "pass": baseline["pass"]
        and all(control["detected"] for control in mutation_control.values())
        and mutation_control["drop_matrix_entry"]["frame_identity_changed"]
        and mutation_control["perturb_transition"]["reconstruction_inverse_and_cocycle_changed"]
        and mutation_control["transpose_metric"]["hermitian_transport_changed"],
    }


def self_test() -> None:
    record = build_record()
    _require(record["pass"], "baseline transition atlas or a mutation control failed")
    _require(
        record["mutation_control"]["drop_matrix_entry"]["frame_identity_changed"],
        "matrix-entry deletion left every frame identity unchanged",
    )
    _require(
        record["mutation_control"]["perturb_transition"]["reconstruction_inverse_and_cocycle_changed"],
        "transition-entry mutation survived an overlap identity",
    )
    _require(
        record["mutation_control"]["transpose_metric"]["hermitian_transport_changed"],
        "transpose-instead-of-adjoint mutation survived Hermitian transport",
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
