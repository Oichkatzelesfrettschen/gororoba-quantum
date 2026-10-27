"""Exact compact tangent ranks on the five nullity-eight strata.

The recorded complex-orbit representatives can be special for the compact
group. This producer moves each representative by exact noncompact
``G_2(C)`` unipotents and ``SO(2,C)`` boosts, then computes the
``G_2 x U(1)`` tangent rank in two coordinate realizations.
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
KERNEL_BUNDLES = HERE.parent / "a5-kernel-bundles"
REGULARITY = HERE.parent / "a5-strata-regularity"
EQUATIONS = HERE.parent / "a5-rank-strata-equations"
sys.path.insert(0, str(KERNEL_BUNDLES))
sys.path.insert(0, str(REGULARITY))
sys.path.insert(0, str(EQUATIONS))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import kernel_symmetry as symmetry  # noqa: E402
import stabilizer_representation as stabilizer  # noqa: E402
import verify_regularity_independent as independent  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "a5-kernel-bundles-nullity8-compact-orbit-ranks-v1"
ORBIT_NAMES = ("W8", "E8bar", "Iso", "X+", "X-")
UNIT_SECTION_DIMENSIONS = {"W8": 23, "E8bar": 21, "Iso": 21, "X+": 19, "X-": 19}
SOURCE_PATHS = (
    HERE / "compact_orbit_ranks.py",
    KERNEL_BUNDLES / "kernel_symmetry.py",
    KERNEL_BUNDLES / "stabilizer_representation.py",
    REGULARITY / "verify_regularity_independent.py",
)

RationalMatrix = tuple[tuple[Fraction, ...], ...]
PointTask = tuple[str, str, tuple[Fraction, ...], str]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _compact_triples(mutation: str) -> tuple[tuple[str, symmetry.LieTriple], ...]:
    if mutation not in ("", "delete_phase_generator"):
        raise ValueError(f"unknown mutation {mutation!r}")
    compact = stabilizer._compact_triples()
    if mutation == "delete_phase_generator":
        compact = compact[:-1]
    return compact


def _compact_derivations() -> tuple[RationalMatrix, ...]:
    table = [[cd_sign(8, left, right) for right in range(8)] for left in range(8)]
    derivations = symmetry.equations.derivations(table)
    return tuple(tuple(tuple(Fraction(entry) for entry in row) for row in derivation) for derivation in derivations)


COMPACT_DERIVATIONS = _compact_derivations()


def _move_fixtures(orbit_name: str) -> list[PointTask]:
    nilpotents = independent.nilpotent_derivations()
    _require(len(nilpotents) >= 3, "the regularity helper supplied fewer than three nilpotent derivations")
    first = independent.expm_nilpotent(nilpotents[0])
    middle = independent.expm_nilpotent(nilpotents[len(nilpotents) // 2])
    last = independent.expm_nilpotent(nilpotents[-1])
    representative = independent.REPS[orbit_name]
    moved_first = independent.act_g2(first, representative)
    moved_middle_boost = independent.act_boost(
        Fraction(13, 12), Fraction(5, 12), independent.act_g2(middle, representative)
    )
    moved_composite = independent.act_g2(
        last,
        independent.act_boost(independent.BOOST[0], independent.BOOST[1], independent.act_g2(first, representative)),
    )
    return [
        (orbit_name, "representative", tuple(representative), ""),
        (orbit_name, "unipotent", tuple(moved_first), ""),
        (orbit_name, "unipotent_boost", tuple(moved_middle_boost), ""),
        (orbit_name, "composite", tuple(moved_composite), ""),
    ]


def _point_tasks(mutation: str) -> list[PointTask]:
    orbit_tasks = parallel.ordered_map(_move_fixtures, list(ORBIT_NAMES), min_items=1)
    tasks: list[PointTask] = []
    for fixtures in orbit_tasks:
        for orbit_name, move_name, point, _unused in fixtures:
            tasks.append((orbit_name, move_name, point, mutation))
    return tasks


def _matrix_tangent_rank(point: Sequence[Fraction], mutation: str) -> int:
    real_point = tuple(symmetry.equations.y_from_split(point))
    tangent_vectors = [stabilizer._matrix_vector(triple[0], real_point) for _name, triple in _compact_triples(mutation)]
    return symmetry._rank(tangent_vectors)


def _direct_derivation_tangent(
    derivation: Sequence[Sequence[Fraction]], real_point: Sequence[Fraction]
) -> tuple[Fraction, ...]:
    tangent_real = [Fraction(0)] * 15
    tangent_imaginary = [Fraction(0)] * 15
    for block_offset in (0, 8):
        for output_index in range(1, 8):
            for input_index in range(1, 8):
                coefficient = derivation[output_index][input_index]
                tangent_real[block_offset + output_index - 1] += coefficient * real_point[block_offset + input_index]
                tangent_imaginary[block_offset + output_index - 1] += (
                    coefficient * real_point[16 + block_offset + input_index]
                )
    return tuple([*tangent_real, *tangent_imaginary])


def _phase_tangent(real_point: Sequence[Fraction]) -> tuple[Fraction, ...]:
    tangent_real = [-real_point[16 + index] for index in range(1, 16)]
    tangent_imaginary = [real_point[index] for index in range(1, 16)]
    return tuple([*tangent_real, *tangent_imaginary])


def _direct_tangent_rank(point: Sequence[Fraction], mutation: str) -> int:
    real_point = tuple(symmetry.equations.y_from_split(point))
    tangent_vectors = [_direct_derivation_tangent(derivation, real_point) for derivation in COMPACT_DERIVATIONS]
    if mutation != "delete_phase_generator":
        tangent_vectors.append(_phase_tangent(real_point))
    return symmetry.equations.qrank(tangent_vectors)


def _point_row(task: PointTask) -> dict[str, Any]:
    orbit_name, move_name, point, mutation = task
    representative_pattern = independent.pattern(independent.REPS[orbit_name])
    point_pattern = independent.pattern(point)
    nullity = independent.nullity_ly(point)
    matrix_rank = _matrix_tangent_rank(point, mutation)
    direct_rank = _direct_tangent_rank(point, mutation)
    unit_section_dimension = UNIT_SECTION_DIMENSIONS[orbit_name]
    return {
        "orbit": orbit_name,
        "move": move_name,
        "nullity_Ly": nullity,
        "closure_membership_pattern": point_pattern,
        "representative_membership_pattern": representative_pattern,
        "same_open_orbit": point_pattern == representative_pattern,
        "matrix_tangent_rank": matrix_rank,
        "direct_complex_block_tangent_rank": direct_rank,
        "ranks_agree": matrix_rank == direct_rank,
        "unit_section_dimension": unit_section_dimension,
        "local_quotient_dimension": unit_section_dimension - matrix_rank,
    }


def _orbit_summary(task: tuple[str, tuple[dict[str, Any], ...], int]) -> dict[str, Any]:
    orbit_name, rows, compact_algebra_dimension = task
    orbit_rows = [row for row in rows if row["orbit"] == orbit_name]
    representative = next(row for row in orbit_rows if row["move"] == "representative")
    ranks = [int(row["matrix_tangent_rank"]) for row in orbit_rows]
    maximum_rank = max(ranks)
    return {
        "orbit": orbit_name,
        "representative_rank": representative["matrix_tangent_rank"],
        "moved_ranks": {row["move"]: row["matrix_tangent_rank"] for row in orbit_rows if row is not representative},
        "minimum_observed_rank": min(ranks),
        "maximum_observed_rank": maximum_rank,
        "full_compact_rank_observed": maximum_rank == compact_algebra_dimension,
        "generic_local_quotient_dimension_if_maximal_rank_is_open": UNIT_SECTION_DIMENSIONS[orbit_name] - maximum_rank,
    }


def build_record(mutation: str = "") -> dict[str, Any]:
    compact_triples = _compact_triples(mutation)
    rows = tuple(parallel.ordered_map(_point_row, _point_tasks(mutation), min_items=1))
    summary_tasks = [(orbit_name, rows, len(compact_triples)) for orbit_name in ORBIT_NAMES]
    summaries = parallel.ordered_map(_orbit_summary, summary_tasks, min_items=1)
    nilpotents = independent.nilpotent_derivations()
    selected_nilpotents = (nilpotents[0], nilpotents[len(nilpotents) // 2], nilpotents[-1])
    selected_unipotents = parallel.ordered_map(
        independent.expm_nilpotent,
        list(selected_nilpotents),
        min_items=1,
    )
    automorphism_checks = parallel.ordered_map(independent.is_automorphism, selected_unipotents, min_items=1)
    group_dimensions = {
        "compact_derivation_dimension": len(COMPACT_DERIVATIONS),
        "compact_generator_dimension": len(compact_triples),
    }
    expected_phase_count = 0 if mutation == "delete_phase_generator" else 1
    group_checks = {
        "generator_dimension_matches_derivations_plus_phase": (
            len(compact_triples) == len(COMPACT_DERIVATIONS) + expected_phase_count
        ),
        "selected_unipotents_are_automorphisms": all(automorphism_checks),
        "boost_hyperbola_identity": independent.BOOST[0] ** 2 - independent.BOOST[1] ** 2 == 1,
        "second_boost_hyperbola_identity": Fraction(13, 12) ** 2 - Fraction(5, 12) ** 2 == 1,
    }
    rows_pass = all(row["nullity_Ly"] == 8 and row["same_open_orbit"] and row["ranks_agree"] for row in rows)
    full_rank_reached = all(summary["full_compact_rank_observed"] for summary in summaries)
    return {
        "schema": SCHEMA,
        "mutation": mutation or None,
        "inputs": {str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS},
        "group_dimensions": group_dimensions,
        "group_checks": group_checks,
        "rows": list(rows),
        "orbit_summaries": summaries,
        "all_points_keep_nullity_and_open_orbit": all(
            row["nullity_Ly"] == 8 and row["same_open_orbit"] for row in rows
        ),
        "independent_rank_implementations_agree": all(row["ranks_agree"] for row in rows),
        "every_orbit_reaches_full_compact_rank": full_rank_reached,
        "pass": all(group_checks.values()) and rows_pass and full_rank_reached,
    }


def _build_record_task(mutation: str) -> dict[str, Any]:
    return build_record(mutation)


def self_test() -> None:
    normal, mutation = parallel.ordered_map(
        _build_record_task,
        ["", "delete_phase_generator"],
        min_items=1,
    )
    _require(normal["pass"], "normal compact-rank record failed")
    normal_ranks = [row["matrix_tangent_rank"] for row in normal["rows"]]
    mutation_ranks = [row["matrix_tangent_rank"] for row in mutation["rows"]]
    _require(normal_ranks != mutation_ranks, "phase-generator deletion left every downstream tangent rank unchanged")
    _require(
        mutation["group_dimensions"]["compact_generator_dimension"]
        < normal["group_dimensions"]["compact_generator_dimension"],
        "phase-generator mutation did not shrink the compact generator family",
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
