"""Exact invariant and normal-form data for the nullity-eight orbit ``W8``."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections.abc import Callable, Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

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

import compact_orbit_ranks as ranks  # noqa: E402
import kernel_symmetry as symmetry  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "a5-kernel-bundles-nullity8-w8-orbit-moduli-v1"
MUTATIONS = ("", "drop_four_form_correction", "one_block_phase")
SOURCE_PATHS = (
    HERE / "w8_orbit_moduli.py",
    HERE / "compact_orbit_ranks.py",
    KERNEL_BUNDLES / "kernel_symmetry.py",
    REGULARITY / "verify_regularity_independent.py",
)

Vector = tuple[Fraction, ...]
Frame = tuple[Vector, Vector, Vector, Vector]
ScalarFunction = Callable[[Frame], Fraction]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dot(first: Sequence[Fraction], second: Sequence[Fraction]) -> Fraction:
    return sum((left * right for left, right in zip(first, second, strict=True)), Fraction(0))


def _cross(first: Sequence[Fraction], second: Sequence[Fraction]) -> Vector:
    output = [Fraction(0)] * 7
    for left_index, left in enumerate(first, start=1):
        for right_index, right in enumerate(second, start=1):
            result_index = left_index ^ right_index
            if result_index:
                output[result_index - 1] += left * right * cd_sign(8, left_index, right_index)
    return tuple(output)


def _three_form(first: Sequence[Fraction], second: Sequence[Fraction], third: Sequence[Fraction]) -> Fraction:
    return _dot(_cross(first, second), third)


def _four_form(frame: Frame, mutation: str) -> Fraction:
    first, second, third, fourth = frame
    cross_pairing = _dot(_cross(first, second), _cross(third, fourth))
    if mutation == "drop_four_form_correction":
        return cross_pairing
    return cross_pairing - _dot(first, third) * _dot(second, fourth) + _dot(first, fourth) * _dot(second, third)


def _frame(split_point: Sequence[Fraction]) -> Frame:
    real_point = symmetry.equations.y_from_split(split_point)
    return (
        tuple(real_point[1:8]),
        tuple(real_point[17:24]),
        tuple(real_point[9:16]),
        tuple(real_point[25:32]),
    )


def _flatten(frame: Frame) -> Vector:
    return tuple(coordinate for vector in frame for coordinate in vector)


def _replace_coordinate(frame: Frame, coordinate: int, delta: Fraction) -> Frame:
    vectors = [list(vector) for vector in frame]
    vectors[coordinate // 7][coordinate % 7] += delta
    return tuple(tuple(vector) for vector in vectors)  # type: ignore[return-value]


def _gradient(function: ScalarFunction, frame: Frame) -> Vector:
    gradient = []
    for coordinate in range(28):
        positive = function(_replace_coordinate(frame, coordinate, Fraction(1)))
        negative = function(_replace_coordinate(frame, coordinate, Fraction(-1)))
        gradient.append((positive - negative) / 2)
    return tuple(gradient)


def _constraint_functions() -> tuple[ScalarFunction, ...]:
    return (
        lambda frame: (
            _dot(frame[0], frame[0]) - _dot(frame[1], frame[1]) - _dot(frame[2], frame[2]) + _dot(frame[3], frame[3])
        ),
        lambda frame: 2 * (_dot(frame[0], frame[1]) - _dot(frame[2], frame[3])),
        lambda frame: _dot(frame[0], frame[2]) - _dot(frame[1], frame[3]),
        lambda frame: _dot(frame[0], frame[3]) + _dot(frame[1], frame[2]),
        lambda frame: sum((_dot(vector, vector) for vector in frame), Fraction(0)),
    )


def _gram_function(first: int, second: int) -> ScalarFunction:
    def gram_entry(frame: Frame) -> Fraction:
        return _dot(frame[first], frame[second])

    return gram_entry


def _three_form_function(indices: tuple[int, int, int]) -> ScalarFunction:
    def three_form_entry(frame: Frame) -> Fraction:
        return _three_form(frame[indices[0]], frame[indices[1]], frame[indices[2]])

    return three_form_entry


def _invariant_functions(mutation: str) -> tuple[tuple[str, ScalarFunction], ...]:
    functions: list[tuple[str, ScalarFunction]] = []
    for first in range(4):
        for second in range(first, 4):
            functions.append(
                (
                    f"gram_{first + 1}{second + 1}",
                    _gram_function(first, second),
                )
            )
    for indices in itertools.combinations(range(4), 3):
        functions.append(
            (
                "phi_" + "".join(str(index + 1) for index in indices),
                _three_form_function(indices),
            )
        )
    functions.append(("psi_1234", lambda frame: _four_form(frame, mutation)))
    return tuple(functions)


def _matrix_rank(rows: Sequence[Sequence[Fraction]]) -> int:
    return symmetry.equations.qrank(rows) if rows else 0


def _determinant(matrix: Sequence[Sequence[Fraction]]) -> Fraction:
    total = Fraction(0)
    for permutation in itertools.permutations(range(len(matrix))):
        inversions = sum(
            1
            for first in range(len(permutation))
            for second in range(first + 1, len(permutation))
            if permutation[first] > permutation[second]
        )
        term = Fraction(-1 if inversions % 2 else 1)
        for row, column in enumerate(permutation):
            term *= matrix[row][column]
        total += term
    return total


def _gram(frame: Frame) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(tuple(_dot(first, second) for second in frame) for first in frame)


def _form_identity(frame: Frame, mutation: str) -> dict[str, Any]:
    gram = _gram(frame)
    triple_dual = []
    for omitted in range(4):
        indices = [index for index in range(4) if index != omitted]
        triple_dual.append(
            Fraction(-1 if omitted % 2 else 1) * _three_form(frame[indices[0]], frame[indices[1]], frame[indices[2]])
        )
    triple_norm_numerator = sum(
        (triple_dual[row] * gram[row][column] * triple_dual[column] for row in range(4) for column in range(4)),
        Fraction(0),
    )
    four_form = _four_form(frame, mutation)
    gram_determinant = _determinant(gram)
    identity_left = triple_norm_numerator + four_form * four_form
    return {
        "gram_determinant": str(gram_determinant),
        "triple_dual": [str(value) for value in triple_dual],
        "triple_norm_numerator": str(triple_norm_numerator),
        "four_form": str(four_form),
        "identity_left": str(identity_left),
        "identity_holds": identity_left == gram_determinant,
    }


def _g2_tangents(frame: Frame) -> tuple[Vector, ...]:
    tangents = []
    for derivation in ranks.COMPACT_DERIVATIONS:
        vectors = []
        for vector in frame:
            vectors.append(
                tuple(
                    sum((derivation[output + 1][source + 1] * vector[source] for source in range(7)), Fraction(0))
                    for output in range(7)
                )
            )
        tangents.append(_flatten(tuple(vectors)))  # type: ignore[arg-type]
    return tuple(tangents)


def _phase_tangent(frame: Frame, mutation: str) -> Vector:
    first_real, first_imaginary, second_real, second_imaginary = frame
    if mutation == "one_block_phase":
        zero = (Fraction(0),) * 7
        return _flatten(
            (
                tuple(-value for value in first_imaginary),
                first_real,
                zero,
                zero,
            )
        )
    return _flatten(
        (
            tuple(-value for value in first_imaginary),
            first_real,
            tuple(-value for value in second_imaginary),
            second_real,
        )
    )


def _canonical_phase_frame(frame: Frame) -> tuple[Frame, Fraction]:
    bilinear_real = _dot(frame[0], frame[0]) - _dot(frame[1], frame[1])
    bilinear_imaginary = 2 * _dot(frame[0], frame[1])
    _require(bilinear_imaginary == 0, "the exact W8 fixtures need a real bilinear square for rational phase fixing")
    _require(bilinear_real != 0, "the open W8 orbit requires a nonzero bilinear square")
    if bilinear_real > 0:
        return frame, bilinear_real
    return (
        (
            tuple(-value for value in frame[1]),
            frame[0],
            tuple(-value for value in frame[3]),
            frame[2],
        ),
        -bilinear_real,
    )


def _canonical_gram_data(frame: Frame) -> dict[str, Any]:
    canonical, bilinear_magnitude = _canonical_phase_frame(frame)
    first_real, first_imaginary, second_real, second_imaginary = canonical
    norm_squared = sum((_dot(vector, vector) for vector in canonical), Fraction(0))
    first_norm = _dot(first_real, first_real)
    mixed_real = _dot(first_real, second_real)
    mixed_imaginary = _dot(first_real, second_imaginary)
    second_norm = norm_squared / 2 + bilinear_magnitude - first_norm
    reconstructed = (
        (first_norm, Fraction(0), mixed_real, mixed_imaginary),
        (Fraction(0), first_norm - bilinear_magnitude, -mixed_imaginary, mixed_real),
        (mixed_real, -mixed_imaginary, second_norm, Fraction(0)),
        (mixed_imaginary, mixed_real, Fraction(0), second_norm - bilinear_magnitude),
    )
    actual = _gram(canonical)
    return {
        "bilinear_square_magnitude": str(bilinear_magnitude),
        "norm_squared": str(norm_squared),
        "four_gram_parameters": [
            str(bilinear_magnitude),
            str(first_norm),
            str(mixed_real),
            str(mixed_imaginary),
        ],
        "canonical_gram": [[str(value) for value in row] for row in actual],
        "reconstructed_gram": [[str(value) for value in row] for row in reconstructed],
        "reconstruction_holds": actual == reconstructed,
    }


def _row(task: tuple[str, tuple[Fraction, ...], str]) -> dict[str, Any]:
    move_name, split_point, mutation = task
    frame = _frame(split_point)
    constraint_functions = _constraint_functions()
    constraint_gradients = tuple(_gradient(function, frame) for function in constraint_functions)
    constraint_rank = _matrix_rank(constraint_gradients)
    tangent_basis = tuple(tuple(row) for row in symmetry.equations.nullspace(constraint_gradients))
    invariant_functions = _invariant_functions(mutation)
    invariant_values = {name: str(function(frame)) for name, function in invariant_functions}
    invariant_gradients = tuple(_gradient(function, frame) for _name, function in invariant_functions)
    restricted_differential = [
        [_dot(tangent, gradient) for gradient in invariant_gradients] for tangent in tangent_basis
    ]
    invariant_differential_rank = _matrix_rank(restricted_differential)
    g2_tangents = _g2_tangents(frame)
    phase_tangent = _phase_tangent(frame, mutation)
    g2_rank = _matrix_rank(g2_tangents)
    compact_rank = _matrix_rank([*g2_tangents, phase_tangent])
    g2_stationary = all(_dot(tangent, gradient) == 0 for tangent in g2_tangents for gradient in invariant_gradients)
    phase_constraint_derivatives = [_dot(phase_tangent, gradient) for gradient in constraint_gradients]
    phase_invariant_derivatives = [_dot(phase_tangent, gradient) for gradient in invariant_gradients]
    generic_level_set_match = (
        compact_rank < len(ranks.COMPACT_DERIVATIONS) + 1 or len(tangent_basis) - invariant_differential_rank == g2_rank
    )
    return {
        "move": move_name,
        "real_frame_rank": _matrix_rank(frame),
        "constraint_rank": constraint_rank,
        "unit_section_tangent_dimension": len(tangent_basis),
        "g2_tangent_rank": g2_rank,
        "compact_tangent_rank": compact_rank,
        "raw_invariants": invariant_values,
        "raw_invariant_differential_rank": invariant_differential_rank,
        "raw_invariant_level_set_tangent_dimension": len(tangent_basis) - invariant_differential_rank,
        "g2_tangents_are_invariant_stationary": g2_stationary,
        "phase_preserves_w8_unit_constraints": all(value == 0 for value in phase_constraint_derivatives),
        "phase_moves_raw_g2_invariants": any(value != 0 for value in phase_invariant_derivatives),
        "generic_level_set_kernel_matches_g2_tangent": generic_level_set_match,
        "form_identity": _form_identity(frame, mutation),
        "canonical_gram_data": _canonical_gram_data(frame),
    }


def build_record(mutation: str = "") -> dict[str, Any]:
    if mutation not in MUTATIONS:
        raise ValueError(f"unknown mutation {mutation!r}")
    fixtures = ranks._move_fixtures("W8")
    tasks = [(move_name, point, mutation) for _orbit, move_name, point, _unused in fixtures]
    rows = parallel.ordered_map(_row, tasks, min_items=1)
    baseline_checks = all(
        row["constraint_rank"] == 5
        and row["unit_section_tangent_dimension"] == 23
        and row["g2_tangents_are_invariant_stationary"]
        and row["phase_preserves_w8_unit_constraints"]
        and row["phase_moves_raw_g2_invariants"]
        and row["generic_level_set_kernel_matches_g2_tangent"]
        and row["form_identity"]["identity_holds"]
        and row["canonical_gram_data"]["reconstruction_holds"]
        for row in rows
    )
    full_rank_rows = [row for row in rows if row["compact_tangent_rank"] == len(ranks.COMPACT_DERIVATIONS) + 1]
    return {
        "schema": SCHEMA,
        "mutation": mutation or None,
        "inputs": {str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS},
        "rows": rows,
        "observed_real_frame_ranks": sorted({row["real_frame_rank"] for row in rows}),
        "full_compact_rank_rows": len(full_rank_rows),
        "full_rank_raw_invariant_differential_ranks": sorted(
            {row["raw_invariant_differential_rank"] for row in full_rank_rows}
        ),
        "moduli_description": {
            "before_phase_quotient": (
                "real Gram matrix, four associative three-form values, and one coassociative four-form value"
            ),
            "phase_slice": (
                "make the nonzero common bilinear square positive real; the residual phase is simultaneous sign"
            ),
            "gram_slice_parameters": [
                "bilinear magnitude",
                "first real norm",
                "real mixed product",
                "imaginary mixed product",
            ],
            "rank_stratified_completeness": (
                "Gram data classifies frames of rank at most two; after Gram-Schmidt, one three-form value classifies "
                "rank three, while the four three-form values and the four-form value obey the recorded quadratic "
                "identity and give the residual rank-four sphere coordinates"
            ),
            "residual_identification": (
                "simultaneous sign reverses all four three-form values and fixes the four-form value"
            ),
        },
        "pass": mutation == "" and baseline_checks and bool(full_rank_rows),
    }


def _build_record_task(mutation: str) -> dict[str, Any]:
    return build_record(mutation)


def self_test() -> None:
    normal, four_form_mutation, phase_mutation = parallel.ordered_map(
        _build_record_task,
        list(MUTATIONS),
        min_items=1,
    )
    _require(normal["pass"], "normal W8 invariant record failed")
    _require(not four_form_mutation["pass"], "four-form correction mutation survived")
    _require(
        any(not row["form_identity"]["identity_holds"] for row in four_form_mutation["rows"]),
        "four-form mutation changed no downstream identity",
    )
    _require(not phase_mutation["pass"], "one-block phase mutation survived")
    _require(
        any(not row["phase_preserves_w8_unit_constraints"] for row in phase_mutation["rows"]),
        "one-block phase mutation changed no downstream constraint derivative",
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
