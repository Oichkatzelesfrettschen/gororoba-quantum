"""Exact complete compact-orbit invariants for the four non-W8 nullity-eight orbits."""

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
import verify_regularity_independent as independent  # noqa: E402
import w8_orbit_moduli as frame_invariants  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-bundles-nullity8-remaining-orbit-moduli-v1"
ORBIT_NAMES = ("E8bar", "Iso", "X+", "X-")
MUTATIONS = ("", "drop_four_form_correction", "one_block_phase")
SOURCE_PATHS = (
    HERE / "remaining_orbit_moduli.py",
    HERE / "compact_orbit_ranks.py",
    HERE / "w8_orbit_moduli.py",
    KERNEL_BUNDLES / "kernel_symmetry.py",
    REGULARITY / "verify_regularity_independent.py",
)

Vector = tuple[Fraction, ...]
Frame = tuple[Vector, Vector, Vector, Vector]
StateFunction = Callable[[Vector], Fraction]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dot(first: Sequence[Fraction], second: Sequence[Fraction]) -> Fraction:
    return sum((left * right for left, right in zip(first, second, strict=True)), Fraction(0))


def _frame(state: Sequence[Fraction]) -> Frame:
    _require(len(state) == 30, "an invariant state must have thirty real coordinates")
    return (
        tuple(state[0:7]),
        tuple(state[7:14]),
        tuple(state[14:21]),
        tuple(state[21:28]),
    )


def _state_from_real_coordinates(real_coordinates: Sequence[Fraction]) -> Vector:
    _require(len(real_coordinates) == 32, "an A_5 real coordinate vector must have thirty-two entries")
    return tuple(
        [
            *real_coordinates[1:8],
            *real_coordinates[17:24],
            *real_coordinates[9:16],
            *real_coordinates[25:32],
            real_coordinates[8],
            real_coordinates[24],
        ]
    )


def _state(split_point: Sequence[Fraction]) -> Vector:
    return _state_from_real_coordinates(symmetry.equations.y_from_split(split_point))


def _replace_coordinate(state: Vector, coordinate: int, delta: Fraction) -> Vector:
    changed = list(state)
    changed[coordinate] += delta
    return tuple(changed)


def _gradient_task(task: tuple[StateFunction, Vector]) -> Vector:
    function, state = task
    gradient = []
    for coordinate in range(len(state)):
        positive = function(_replace_coordinate(state, coordinate, Fraction(1)))
        negative = function(_replace_coordinate(state, coordinate, Fraction(-1)))
        gradient.append((positive - negative) / 2)
    return tuple(gradient)


def _lift_frame_function(function: frame_invariants.ScalarFunction) -> StateFunction:
    def lifted(state: Vector) -> Fraction:
        return function(_frame(state))

    return lifted


def _middle_real(state: Vector) -> Fraction:
    return state[28]


def _middle_imaginary(state: Vector) -> Fraction:
    return state[29]


def _invariant_functions(orbit_name: str, mutation: str) -> tuple[tuple[str, StateFunction], ...]:
    frame_functions = frame_invariants._invariant_functions(mutation)
    lifted = tuple((name, _lift_frame_function(function)) for name, function in frame_functions)
    if orbit_name == "E8bar":
        return (*lifted, ("mu_real", _middle_real), ("mu_imaginary", _middle_imaginary))
    return lifted


def _realify_complex_tangent(complex_tangent: Sequence[Fraction]) -> tuple[Vector, Vector]:
    real_tangent = tuple(symmetry.equations.y_from_split(complex_tangent))
    imaginary_multiple = tuple([-coordinate for coordinate in real_tangent[16:32]] + list(real_tangent[0:16]))
    return (
        _state_from_real_coordinates(real_tangent),
        _state_from_real_coordinates(imaginary_multiple),
    )


def _independent_basis(vectors: Sequence[Vector]) -> tuple[Vector, ...]:
    basis: list[Vector] = []
    rank = 0
    for vector in vectors:
        candidate_rank = symmetry.equations.qrank([*basis, vector])
        if candidate_rank > rank:
            basis.append(vector)
            rank = candidate_rank
    return tuple(basis)


def _combine_tangent_task(task: tuple[Sequence[Fraction], tuple[Vector, ...]]) -> Vector:
    coefficients, tangent_basis = task
    return tuple(
        sum(
            (
                coefficient * tangent_basis[basis_index][coordinate]
                for basis_index, coefficient in enumerate(coefficients)
            ),
            Fraction(0),
        )
        for coordinate in range(30)
    )


def _unit_tangent(split_point: Sequence[Fraction], state: Vector) -> tuple[Vector, ...]:
    complex_tangents = independent.h_tangent(split_point)
    realified_pairs = parallel.ordered_map(_realify_complex_tangent, complex_tangents, min_items=1)
    real_orbit_tangent = _independent_basis(tuple(itertools.chain.from_iterable(realified_pairs)))
    sphere_derivatives = parallel.ordered_map(
        _dot_pair,
        [(state, tangent) for tangent in real_orbit_tangent],
        min_items=1,
    )
    coefficient_basis = symmetry.equations.nullspace([sphere_derivatives])
    return tuple(
        parallel.ordered_map(
            _combine_tangent_task,
            [(coefficients, real_orbit_tangent) for coefficients in coefficient_basis],
            min_items=1,
        )
    )


def _dot_pair(task: tuple[Sequence[Fraction], Sequence[Fraction]]) -> Fraction:
    return _dot(task[0], task[1])


def _directional_derivative_row(task: tuple[Vector, tuple[Vector, ...]]) -> list[Fraction]:
    tangent, gradients = task
    return parallel.ordered_map(_dot_pair, [(tangent, gradient) for gradient in gradients], min_items=1)


def _append_middle_zeros(tangent: Sequence[Fraction]) -> Vector:
    return tuple([*tangent, Fraction(0), Fraction(0)])


def _g2_tangents(state: Vector) -> tuple[Vector, ...]:
    return tuple(
        parallel.ordered_map(
            _append_middle_zeros,
            frame_invariants._g2_tangents(_frame(state)),
            min_items=1,
        )
    )


def _phase_tangent(state: Vector, mutation: str) -> Vector:
    first_real, first_imaginary, second_real, second_imaginary = _frame(state)
    if mutation == "one_block_phase":
        zeros = (Fraction(0),) * 7
        return tuple(
            [
                *(-coordinate for coordinate in first_imaginary),
                *first_real,
                *zeros,
                *zeros,
                Fraction(0),
                Fraction(0),
            ]
        )
    return tuple(
        [
            *(-coordinate for coordinate in first_imaginary),
            *first_real,
            *(-coordinate for coordinate in second_imaginary),
            *second_real,
            -state[29],
            state[28],
        ]
    )


def _vector_lies_in_span(vector: Vector, basis: Sequence[Vector]) -> bool:
    return symmetry.equations.qrank(list(basis)) == symmetry.equations.qrank([*basis, vector])


def _permutation_sign(values: Sequence[int]) -> int:
    inversions = sum(
        1 for first in range(len(values)) for second in range(first + 1, len(values)) if values[first] > values[second]
    )
    return -1 if inversions % 2 else 1


def _alternating_three_value(values: dict[tuple[int, int, int], Fraction], indices: tuple[int, int, int]) -> Fraction:
    if len(set(indices)) < 3:
        return Fraction(0)
    ordered = tuple(sorted(indices))
    ordered_indices = (ordered[0], ordered[1], ordered[2])
    return Fraction(_permutation_sign(indices)) * values[ordered_indices]


def _quarter_turn_predictions(state: Vector, invariant_values: dict[str, Fraction]) -> dict[str, Fraction]:
    transformation = (
        (Fraction(0), Fraction(-1), Fraction(0), Fraction(0)),
        (Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(0), Fraction(-1)),
        (Fraction(0), Fraction(0), Fraction(1), Fraction(0)),
    )
    predictions: dict[str, Fraction] = {}
    for first in range(4):
        for second in range(first, 4):
            predictions[f"gram_{first + 1}{second + 1}"] = sum(
                (
                    transformation[first][source_first]
                    * transformation[second][source_second]
                    * invariant_values[
                        f"gram_{min(source_first, source_second) + 1}{max(source_first, source_second) + 1}"
                    ]
                    for source_first in range(4)
                    for source_second in range(4)
                ),
                Fraction(0),
            )
    three_values = {
        indices: invariant_values["phi_" + "".join(str(index + 1) for index in indices)]
        for indices in itertools.combinations(range(4), 3)
    }
    for target_indices in itertools.combinations(range(4), 3):
        predictions["phi_" + "".join(str(index + 1) for index in target_indices)] = sum(
            (
                transformation[target_indices[0]][source_first]
                * transformation[target_indices[1]][source_second]
                * transformation[target_indices[2]][source_third]
                * _alternating_three_value(three_values, (source_first, source_second, source_third))
                for source_first in range(4)
                for source_second in range(4)
                for source_third in range(4)
            ),
            Fraction(0),
        )
    predictions["psi_1234"] = invariant_values["psi_1234"]
    if "mu_real" in invariant_values:
        predictions["mu_real"] = -state[29]
        predictions["mu_imaginary"] = state[28]
    return predictions


def _quarter_turn_state(state: Vector) -> Vector:
    first_real, first_imaginary, second_real, second_imaginary = _frame(state)
    return tuple(
        [
            *(-coordinate for coordinate in first_imaginary),
            *first_real,
            *(-coordinate for coordinate in second_imaginary),
            *second_real,
            -state[29],
            state[28],
        ]
    )


def _evaluate_invariants(functions: Sequence[tuple[str, StateFunction]], state: Vector) -> dict[str, Fraction]:
    return {name: function(state) for name, function in functions}


def _row(task: tuple[str, str, tuple[Fraction, ...], str]) -> dict[str, Any]:
    orbit_name, move_name, split_point, mutation = task
    state = _state(split_point)
    frame = _frame(state)
    unit_tangent = _unit_tangent(split_point, state)
    invariant_functions = _invariant_functions(orbit_name, mutation)
    invariant_values = _evaluate_invariants(invariant_functions, state)
    gradient_tasks = [(function, state) for _name, function in invariant_functions]
    invariant_gradients = tuple(parallel.ordered_map(_gradient_task, gradient_tasks, min_items=1))
    differential_tasks = [(tangent, invariant_gradients) for tangent in unit_tangent]
    restricted_differential = parallel.ordered_map(_directional_derivative_row, differential_tasks, min_items=1)
    invariant_differential_rank = symmetry.equations.qrank(restricted_differential)
    g2_tangents = _g2_tangents(state)
    phase_tangent = _phase_tangent(state, mutation)
    g2_rank = symmetry.equations.qrank(list(g2_tangents))
    compact_rank = symmetry.equations.qrank([*g2_tangents, phase_tangent])
    g2_stationary = all(
        derivative == 0
        for derivative in parallel.ordered_map(
            _dot_pair,
            [(tangent, gradient) for tangent in g2_tangents for gradient in invariant_gradients],
            min_items=1,
        )
    )
    phase_derivatives = parallel.ordered_map(
        _dot_pair,
        [(phase_tangent, gradient) for gradient in invariant_gradients],
        min_items=1,
    )
    full_compact_rank = compact_rank == len(ranks.COMPACT_DERIVATIONS) + 1
    level_set_dimension = len(unit_tangent) - invariant_differential_rank
    raw_quotient_dimension = invariant_differential_rank
    compact_quotient_dimension = len(unit_tangent) - compact_rank
    quarter_state = _quarter_turn_state(state)
    quarter_values = _evaluate_invariants(invariant_functions, quarter_state)
    quarter_predictions = _quarter_turn_predictions(state, invariant_values)
    form_identity = frame_invariants._form_identity(frame, mutation)
    expected_unit_dimension = ranks.UNIT_SECTION_DIMENSIONS[orbit_name]
    return {
        "orbit": orbit_name,
        "move": move_name,
        "nullity_Ly": independent.nullity_ly(split_point),
        "same_open_orbit": independent.pattern(split_point) == independent.pattern(independent.REPS[orbit_name]),
        "squared_radius": str(_dot(state, state)),
        "middle_coordinate": [str(state[28]), str(state[29])],
        "real_frame_rank": symmetry.equations.qrank(list(frame)),
        "unit_section_tangent_dimension": len(unit_tangent),
        "expected_unit_section_tangent_dimension": expected_unit_dimension,
        "g2_tangent_rank": g2_rank,
        "compact_tangent_rank": compact_rank,
        "g2_tangents_lie_in_unit_section": all(_vector_lies_in_span(tangent, unit_tangent) for tangent in g2_tangents),
        "phase_tangent_lies_in_unit_section": _vector_lies_in_span(phase_tangent, unit_tangent),
        "g2_tangents_are_invariant_stationary": g2_stationary,
        "phase_moves_raw_g2_invariants": any(derivative != 0 for derivative in phase_derivatives),
        "raw_invariants": {name: str(value) for name, value in invariant_values.items()},
        "raw_invariant_differential_rank": invariant_differential_rank,
        "raw_invariant_level_set_tangent_dimension": level_set_dimension,
        "full_compact_rank": full_compact_rank,
        "generic_level_set_kernel_matches_g2_tangent": (not full_compact_rank or level_set_dimension == g2_rank),
        "raw_g2_quotient_dimension": raw_quotient_dimension,
        "compact_quotient_dimension": compact_quotient_dimension,
        "phase_removes_one_raw_quotient_dimension": (
            not full_compact_rank or raw_quotient_dimension - compact_quotient_dimension == 1
        ),
        "quarter_turn_action_matches_exterior_power_formula": quarter_values == quarter_predictions,
        "form_identity": form_identity,
    }


def _orbit_summary(task: tuple[str, tuple[dict[str, Any], ...]]) -> dict[str, Any]:
    orbit_name, rows = task
    orbit_rows = [row for row in rows if row["orbit"] == orbit_name]
    full_rank_rows = [row for row in orbit_rows if row["full_compact_rank"]]
    return {
        "orbit": orbit_name,
        "fixtures": len(orbit_rows),
        "observed_real_frame_ranks": sorted({row["real_frame_rank"] for row in orbit_rows}),
        "full_compact_rank_fixtures": len(full_rank_rows),
        "full_rank_raw_invariant_differential_ranks": sorted(
            {row["raw_invariant_differential_rank"] for row in full_rank_rows}
        ),
        "full_rank_level_set_dimensions": sorted(
            {row["raw_invariant_level_set_tangent_dimension"] for row in full_rank_rows}
        ),
        "generic_compact_quotient_dimensions": sorted({row["compact_quotient_dimension"] for row in full_rank_rows}),
    }


def _row_passes(row: dict[str, Any]) -> bool:
    return bool(
        row["nullity_Ly"] == 8
        and row["same_open_orbit"]
        and row["unit_section_tangent_dimension"] == row["expected_unit_section_tangent_dimension"]
        and row["g2_tangents_lie_in_unit_section"]
        and row["phase_tangent_lies_in_unit_section"]
        and row["g2_tangents_are_invariant_stationary"]
        and row["phase_moves_raw_g2_invariants"]
        and row["generic_level_set_kernel_matches_g2_tangent"]
        and row["phase_removes_one_raw_quotient_dimension"]
        and row["quarter_turn_action_matches_exterior_power_formula"]
        and row["form_identity"]["identity_holds"]
    )


def build_record(mutation: str = "") -> dict[str, Any]:
    if mutation not in MUTATIONS:
        raise ValueError(f"unknown mutation {mutation!r}")
    orbit_fixtures = parallel.ordered_map(ranks._move_fixtures, list(ORBIT_NAMES), min_items=1)
    tasks = [
        (orbit_name, move_name, split_point, mutation)
        for fixtures in orbit_fixtures
        for orbit_name, move_name, split_point, _unused in fixtures
    ]
    rows = tuple(parallel.ordered_map(_row, tasks, min_items=1))
    summary_tasks = [(orbit_name, rows) for orbit_name in ORBIT_NAMES]
    summaries = parallel.ordered_map(_orbit_summary, summary_tasks, min_items=1)
    return {
        "schema": SCHEMA,
        "mutation": mutation or None,
        "inputs": {str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS},
        "rows": list(rows),
        "orbit_summaries": summaries,
        "complete_g2_invariant_argument": (
            "The real Gram matrix, four associative three-form values, and coassociative four-form value classify "
            "ordered real four-frames under compact G_2 by the rank-stratified Gram-Schmidt normal form. E8-bar "
            "also records the middle complex coordinate, which compact G_2 fixes. Restriction to each orbit "
            "therefore remains complete."
        ),
        "phase_action": {
            "frame": "(a,b,c,d) maps to (cos(t)a-sin(t)b, sin(t)a+cos(t)b, cos(t)c-sin(t)d, sin(t)c+cos(t)d)",
            "gram": "G maps to T(t) G T(t)^transpose for T(t)=diag(R(t),R(t))",
            "three_forms": "the four associative values transform by the third exterior power of T(t)",
            "four_form": "the coassociative four-form is fixed because det(T(t))=1",
            "middle_coordinate": "(mu_real,mu_imaginary) maps by R(t)",
        },
        "moduli_spaces": {
            "E8bar": (
                "the complete invariant image of the unit E8-bar orbit in the unique gauge with its nonzero middle "
                "coordinate positive real"
            ),
            "Iso": "the complete invariant image of the unit Iso orbit modulo the displayed circle action",
            "X+": "the complete invariant image of the unit X_+ orbit modulo the displayed circle action",
            "X-": "the complete invariant image of the unit X_- orbit modulo the displayed circle action",
        },
        "pass": mutation == "" and all(_row_passes(row) for row in rows),
    }


def _build_record_task(mutation: str) -> dict[str, Any]:
    return build_record(mutation)


def self_test() -> None:
    normal, form_mutation, phase_mutation = parallel.ordered_map(
        _build_record_task,
        list(MUTATIONS),
        min_items=1,
    )
    _require(normal["pass"], "normal remaining-orbit invariant record failed")
    _require(not form_mutation["pass"], "four-form correction mutation survived")
    _require(
        any(not row["form_identity"]["identity_holds"] for row in form_mutation["rows"]),
        "four-form mutation changed no downstream identity",
    )
    _require(not phase_mutation["pass"], "one-block phase mutation survived")
    _require(
        any(not row["phase_tangent_lies_in_unit_section"] for row in phase_mutation["rows"]),
        "one-block phase mutation changed no downstream tangent membership",
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
