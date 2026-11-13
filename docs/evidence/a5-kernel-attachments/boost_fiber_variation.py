"""Special fibers of the four whole-projective-space incidences into VB at basepoints moved along the boost.

G_2(C) x C^* acts on the holomorphic kernel and its orbit of a basepoint on VB has dimension 6 in the 7-dimensional
boundary orbit (`kernel_equivariance.py`); the missing direction is the boost u -> c u + s v, v -> s u + c v with
c^2 - s^2 = 1, which preserves every stratum and has no lift to the kernel. This producer moves the retained VB
basepoint of Iso->VB, W8->VB, X+->VB and X-->VB by three rational boosts, keeps the retained slice columns, checks
that the slice stays complementary to the boundary orbit, and recomputes the Nakayama-reduced Rees special fiber
over Q(i) and modulo 32003 with the scripts of `nakayama_rees_fibers.py`. The record states the fiber at each
sampled basepoint; it samples the boost orbit and proves nothing about an unsampled point.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(HERE.parent / "a5-strata-regularity"))

import nakayama_rees_fibers as nakayama  # noqa: E402
import verify_regularity_independent as independent  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-attachments-boost-fiber-variation-v1"
INCIDENCES = ("Iso->VB", "W8->VB", "X+->VB", "X-->VB")
# (cosh, sinh) with cosh^2 - sinh^2 = 1; the first is the identity and reproduces the retained basepoint.
BOOSTS = (
    (Fraction(1), Fraction(0)),
    (Fraction(5, 4), Fraction(3, 4)),
    (Fraction(5, 3), Fraction(4, 3)),
    (Fraction(13, 12), Fraction(-5, 12)),
)
COMPLEX_DIMENSION = 15
VB_ORBIT_DIMENSION = 7
CHARACTERISTICS = (0, nakayama.MODULAR_PRIME)
SOURCE_PATHS = (
    HERE / "boost_fiber_variation.py",
    HERE / "nakayama_rees_fibers.py",
    HERE / "holomorphic_gauss_fibers.py",
    HERE / "first-order-normal-cones-result.json",
    HERE.parent / "a5-strata-regularity" / "verify_regularity_independent.py",
    HERE.parent / "a5-strata-regularity" / "strata_regularity.py",
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def moved_row(row: dict[str, Any], boost: tuple[Fraction, Fraction]) -> dict[str, Any]:
    """The committed first-order row with its boundary point moved by the boost; the slice columns stay."""
    cosh, sinh = boost
    _require(cosh * cosh - sinh * sinh == 1, f"({cosh}, {sinh}) is not a boost")
    point = [Fraction(value) for value in row["boundary_point"]]
    return {**row, "boundary_point": [str(value) for value in independent.act_boost(cosh, sinh, point)]}


def transversality(row: dict[str, Any]) -> dict[str, Any]:
    """Orbit dimension, closure membership and the rank of the orbit tangent space together with the slice."""
    point = [Fraction(value) for value in row["boundary_point"]]
    columns = [int(value) for value in row["slice_columns_zero_based"]]
    slice_basis = [[Fraction(int(index == column)) for index in range(COMPLEX_DIMENSION)] for column in columns]
    return {
        "orbit_dimension": independent.orbit_dim(point),
        "closure_membership": independent.pattern(point),
        "slice_dimension": len(columns),
        "rank_of_orbit_tangent_with_slice": independent.c_rank(independent.h_tangent(point) + slice_basis),
    }


def fiber_task(item: tuple[dict[str, Any], tuple[str, ...], int]) -> dict[str, Any]:
    """Nakayama selection and Rees special fiber of one moved row in one characteristic."""
    row, closure, characteristic = item
    task = nakayama.RowTask(row, (), closure)
    data = nakayama.resolved._schur_polynomials(nakayama.resolved.IncidenceTask(row))
    phase_one = nakayama._phase_one_summary(
        nakayama._run_singular(nakayama._phase_one_script(characteristic, task, data))
    )
    fiber = nakayama._phase_two_summary(
        nakayama._run_singular(nakayama._phase_two_script(characteristic, phase_one, ())), 0
    )
    dimension, degree, count, components = nakayama._fiber_tuple(fiber)
    return {
        "characteristic": characteristic,
        "germ_dimension": phase_one["germ_dimension"],
        "selected_count": phase_one["selected_count"],
        "selected_indices_one_based": phase_one["selected_indices_one_based"],
        "embedding_rank": phase_one["embedding_rank"],
        "fiber_projective_dimension_degree_components": [dimension, degree, count],
        "components_projective_dimension_degree": [list(pair) for pair in components],
    }


def point_passes(point: dict[str, Any], expected: tuple[int, int, int]) -> bool:
    """A sampled basepoint passes when its slice is complementary and both characteristics give the whole space."""
    geometry = point["transversality"]
    fibers = point["fibers"]
    count = expected[0] + 1
    return (
        geometry["orbit_dimension"] == VB_ORBIT_DIMENSION
        and geometry["orbit_dimension"] + geometry["slice_dimension"] == COMPLEX_DIMENSION
        and geometry["rank_of_orbit_tangent_with_slice"] == COMPLEX_DIMENSION
        and [fiber["characteristic"] for fiber in fibers] == list(CHARACTERISTICS)
        and all(tuple(fiber["fiber_projective_dimension_degree_components"]) == expected for fiber in fibers)
        and all(fiber["selected_count"] == count == fiber["embedding_rank"] for fiber in fibers)
        and len({tuple(fiber["selected_indices_one_based"]) for fiber in fibers}) == 1
    )


def build_record() -> dict[str, Any]:
    first_order = nakayama._load_json(nakayama.FIRST_ORDER_RESULT)
    rows = {str(entry["incidence"]): entry for entry in first_order["incidences"]}
    closures = {name: nakayama._closure_row(name, rows=rows)[1] for name in INCIDENCES}
    moved = [(name, boost, moved_row(rows[name], boost)) for name in INCIDENCES for boost in BOOSTS]
    items = [(row, closures[name], characteristic) for name, _, row in moved for characteristic in CHARACTERISTICS]
    fibers = parallel.ordered_map(fiber_task, items, min_items=1)
    incidences: list[dict[str, Any]] = []
    for index, name in enumerate(INCIDENCES):
        expected = nakayama.EXPECTED_FIBERS[name]
        points = []
        for offset, boost in enumerate(BOOSTS):
            position = index * len(BOOSTS) + offset
            point: dict[str, Any] = {
                "boost_cosh_sinh": [str(boost[0]), str(boost[1])],
                "boundary_point": moved[position][2]["boundary_point"],
                "transversality": transversality(moved[position][2]),
                "fibers": fibers[len(CHARACTERISTICS) * position : len(CHARACTERISTICS) * (position + 1)],
            }
            point["pass"] = point_passes(point, expected)
            points.append(point)
        selections = [point["fibers"][0]["selected_indices_one_based"] for point in points]
        incidences.append(
            {
                "incidence": name,
                "expected_fiber_projective_dimension_degree_components": list(expected),
                "points": points,
                "selected_coordinates_change_along_the_boost": any(entry != selections[0] for entry in selections),
                "pass": all(bool(point["pass"]) for point in points),
            }
        )
    retained = nakayama._load_json(nakayama.RESULT_PATH)
    retained_rows = {str(entry["incidence"]): entry for entry in retained["incidences"]}
    identity_matches = all(
        entry["points"][0]["fibers"][0]["selected_indices_one_based"]
        == retained_rows[str(entry["incidence"])]["chosen_coordinate_indices_one_based"]
        for entry in incidences
    )
    # The control removes one slice column at a boosted basepoint: the slice then misses one normal direction.
    boosted = moved[1][2]
    short = {**boosted, "slice_columns_zero_based": list(boosted["slice_columns_zero_based"])[:-1]}
    mutated_point = {**incidences[0]["points"][1], "transversality": transversality(short)}
    control: dict[str, Any] = {
        "name": "slice_with_one_column_removed",
        "input_change": "drop the last slice column of Iso->VB at the boost (5/4, 3/4)",
        "transversality": mutated_point["transversality"],
        "detected": not point_passes(mutated_point, nakayama.EXPECTED_FIBERS[INCIDENCES[0]]),
    }
    return {
        "schema": SCHEMA,
        "inputs": dict(parallel.ordered_map(nakayama._hash_path, SOURCE_PATHS, min_items=1)),
        "scope": {
            "statement": (
                "At the retained VB basepoint and at its images under three rational boosts, the retained slice is "
                "complementary to the boundary orbit and the Nakayama-reduced Rees special fiber of Iso->VB, "
                "W8->VB, X+->VB and X-->VB is the whole projective space of its generators over Q(i) and modulo "
                f"{nakayama.MODULAR_PRIME}."
            ),
            "claim_boundary": (
                "Four points of a one-parameter orbit per incidence. The record compares no limiting plane "
                "between basepoints, covers neither E8bar->VB nor E8bar->V, and proves nothing at an unsampled "
                "boost."
            ),
        },
        "incidences": incidences,
        "identity_boost_reproduces_the_retained_selection": identity_matches,
        "mutation_control": control,
        "falsifier": (
            "A sampled basepoint off the VB orbit or with a slice that is not complementary; a fiber other than "
            "the whole projective space in either characteristic; a selection that differs between the "
            "characteristics; or a slice with one column removed passing the complementarity check."
        ),
        "pass": all(bool(entry["pass"]) for entry in incidences) and identity_matches and bool(control["detected"]),
    }


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _self_test(record: dict[str, Any]) -> None:
    _require(bool(record["pass"]), "the boost fiber variation record failed")
    _require(bool(record["mutation_control"]["detected"]), "the shortened slice passed the complementarity check")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write the deterministic JSON record")
    parser.add_argument("--check", type=Path, help="compare a deterministic record byte for byte")
    parser.add_argument("--self-test", action="store_true", help="run the baseline and mutation checks")
    arguments = parser.parse_args()
    if sum((arguments.out is not None, arguments.check is not None, arguments.self_test)) != 1:
        parser.error("select exactly one of --out, --check, or --self-test")
    record = build_record()
    _self_test(record)
    rendered = _record_bytes(record)
    if arguments.out is not None:
        arguments.out.write_bytes(rendered)
    elif arguments.check is not None:
        _require(arguments.check.read_bytes() == rendered, f"{arguments.check} differs from the regenerated record")


if __name__ == "__main__":
    main()
