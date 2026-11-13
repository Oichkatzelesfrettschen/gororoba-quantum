"""Fibers into VB at boosted basepoints: the moved point, slice complementarity and the pass rule of a sample."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
ATTACHMENTS = ROOT / "docs" / "evidence" / "a5-kernel-attachments"
sys.path.insert(0, str(ATTACHMENTS))

import boost_fiber_variation as bf  # noqa: E402

RECORD = ATTACHMENTS / "boost-fiber-variation-result.json"


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _rows() -> dict[str, dict[str, Any]]:
    first_order = bf.nakayama._load_json(bf.nakayama.FIRST_ORDER_RESULT)
    return {str(entry["incidence"]): entry for entry in first_order["incidences"]}


def test_every_sampled_pair_is_a_boost_and_the_identity_keeps_the_basepoint() -> None:
    _same([cosh * cosh - sinh * sinh for cosh, sinh in bf.BOOSTS], [Fraction(1)] * len(bf.BOOSTS))
    row = _rows()["W8->VB"]
    _same(bf.moved_row(row, bf.BOOSTS[0])["boundary_point"], [str(Fraction(v)) for v in row["boundary_point"]])
    with pytest.raises(RuntimeError, match="not a boost"):
        bf.moved_row(row, (Fraction(5, 4), Fraction(1)))


def test_a_boosted_basepoint_stays_on_the_orbit_with_a_complementary_slice_and_a_short_slice_does_not() -> None:
    row = _rows()["W8->VB"]
    retained = bf.transversality(row)
    moved = bf.moved_row(row, bf.BOOSTS[1])
    _same(moved["boundary_point"] != row["boundary_point"], True)
    geometry = bf.transversality(moved)
    _same(geometry, retained)
    _same((geometry["orbit_dimension"], geometry["slice_dimension"]), (7, 8))
    _same(geometry["rank_of_orbit_tangent_with_slice"], 15)
    short = {**moved, "slice_columns_zero_based": list(moved["slice_columns_zero_based"])[:-1]}
    _same(bf.transversality(short)["rank_of_orbit_tangent_with_slice"], 14)


def test_the_pass_rule_rejects_each_changed_field_of_a_sampled_point() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    entry = next(row for row in record["incidences"] if row["incidence"] == "W8->VB")
    expected = tuple(entry["expected_fiber_projective_dimension_degree_components"])
    point = entry["points"][1]
    _same(bf.point_passes(point, expected), True)
    rational, modular = point["fibers"]
    conic = {**modular, "fiber_projective_dimension_degree_components": [4, 2, 1]}
    _same(bf.point_passes({**point, "fibers": [rational, conic]}, expected), False)
    other = {**modular, "selected_indices_one_based": [8, 12, 16, 17, 18]}
    _same(bf.point_passes({**point, "fibers": [rational, other]}, expected), False)
    low = {**modular, "embedding_rank": 4}
    _same(bf.point_passes({**point, "fibers": [rational, low]}, expected), False)
    _same(bf.point_passes({**point, "fibers": [modular, rational]}, expected), False)
    _same(bf.point_passes({**point, "fibers": [modular]}, expected), False)
    off = {**point["transversality"], "orbit_dimension": 6}
    _same(bf.point_passes({**point, "transversality": off}, expected), False)
    short = {**point["transversality"], "rank_of_orbit_tangent_with_slice": 14}
    _same(bf.point_passes({**point, "transversality": short}, expected), False)


def test_the_retained_record_passes_at_sixteen_points_and_the_selection_moves_only_for_w8() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    _same((record["pass"], record["mutation_control"]["detected"]), (True, True))
    _same([entry["incidence"] for entry in record["incidences"]], list(bf.INCIDENCES))
    _same(sum(len(entry["points"]) for entry in record["incidences"]), 16)
    moving = [e["incidence"] for e in record["incidences"] if e["selected_coordinates_change_along_the_boost"]]
    _same(moving, ["W8->VB"])
    for entry in record["incidences"]:
        expected = tuple(entry["expected_fiber_projective_dimension_degree_components"])
        _same([bf.point_passes(point, expected) for point in entry["points"]], [True] * len(bf.BOOSTS))


def test_self_test_rejects_a_failed_record_and_a_surviving_mutation() -> None:
    with pytest.raises(RuntimeError, match="failed"):
        bf._self_test({"pass": False, "mutation_control": {"detected": True}})
    with pytest.raises(RuntimeError, match="shortened slice"):
        bf._self_test({"pass": True, "mutation_control": {"detected": False}})


@pytest.mark.audit
def test_the_retained_record_regenerates_byte_for_byte() -> None:
    _same(bf._record_bytes(bf.build_record()), RECORD.read_bytes())
