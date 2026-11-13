"""Fibers into VB at boosted basepoints: the moved point, slice complementarity and the pass rule of a sample."""

from __future__ import annotations

import copy
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


@pytest.mark.parametrize("name", bf.INCIDENCES)
def test_the_boost_acts_as_a_group_on_every_incidence_and_keeps_the_complementary_slice(name: str) -> None:
    row = _rows()[name]
    retained = bf.transversality(row)
    for boost in bf.BOOSTS[1:]:
        moved = bf.moved_row(row, boost)
        _same(moved["boundary_point"] != row["boundary_point"], True)
        _same(bf.transversality(moved), retained)
        cosh, sinh = boost
        back = bf.moved_row(moved, (cosh, -sinh))
        _same(back["boundary_point"], [str(Fraction(value)) for value in row["boundary_point"]])
        short = {**moved, "slice_columns_zero_based": list(moved["slice_columns_zero_based"])[:-1]}
        _same(bf.transversality(short)["rank_of_orbit_tangent_with_slice"], 14)
    _same(retained["closure_membership"], bf.source_expectation(row)["closure_membership"])


def test_the_pass_rule_rejects_each_changed_field_of_a_sampled_point() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    entry = next(row for row in record["incidences"] if row["incidence"] == "W8->VB")
    expected = tuple(entry["expected_fiber_projective_dimension_degree_components"])
    point = entry["points"][1]
    source = bf.source_expectation(_rows()["W8->VB"])
    _same(source, {"closure_membership": "111111110000", "germ_dimension": 5})
    _same(bf.point_passes(point, expected, source), True)
    rational, modular = point["fibers"]
    conic = {**modular, "fiber_projective_dimension_degree_components": [4, 2, 1]}
    _same(bf.point_passes({**point, "fibers": [rational, conic]}, expected, source), False)
    other = {**modular, "selected_indices_one_based": [8, 12, 16, 17, 18]}
    _same(bf.point_passes({**point, "fibers": [rational, other]}, expected, source), False)
    low = {**modular, "embedding_rank": 4}
    _same(bf.point_passes({**point, "fibers": [rational, low]}, expected, source), False)
    _same(bf.point_passes({**point, "fibers": [modular, rational]}, expected, source), False)
    _same(bf.point_passes({**point, "fibers": [modular]}, expected, source), False)
    off = {**point["transversality"], "orbit_dimension": 6}
    _same(bf.point_passes({**point, "transversality": off}, expected, source), False)
    short = {**point["transversality"], "rank_of_orbit_tangent_with_slice": 14}
    _same(bf.point_passes({**point, "transversality": short}, expected, source), False)
    # An off-orbit pattern or a changed germ dimension fails although every other field is the retained value.
    pattern = {**point["transversality"], "closure_membership": "111111111000"}
    _same(bf.point_passes({**point, "transversality": pattern}, expected, source), False)
    germ = {**modular, "germ_dimension": modular["germ_dimension"] + 1}
    _same(bf.point_passes({**point, "fibers": [rational, germ]}, expected, source), False)
    germ_first = {**rational, "germ_dimension": rational["germ_dimension"] - 1}
    _same(bf.point_passes({**point, "fibers": [germ_first, modular]}, expected, source), False)


def test_the_retained_record_passes_at_sixteen_points_and_the_selection_moves_only_for_w8() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    _same((record["pass"], record["mutation_control"]["detected"]), (True, True))
    _same([entry["incidence"] for entry in record["incidences"]], list(bf.INCIDENCES))
    _same(sum(len(entry["points"]) for entry in record["incidences"]), 16)
    moving = [e["incidence"] for e in record["incidences"] if e["selected_coordinates_change_along_the_boost"]]
    _same(moving, ["W8->VB"])
    rows = _rows()
    for entry in record["incidences"]:
        expected = tuple(entry["expected_fiber_projective_dimension_degree_components"])
        source = bf.source_expectation(rows[entry["incidence"]])
        _same(
            [bf.point_passes(point, expected, source) for point in entry["points"]],
            [True] * len(bf.BOOSTS),
        )
        _same([point["fibers"][0]["germ_dimension"] for point in entry["points"]], [source["germ_dimension"]] * 4)


def test_self_test_rejects_a_failed_record_and_a_surviving_mutation() -> None:
    with pytest.raises(RuntimeError, match="failed"):
        bf._self_test({"pass": False, "mutation_control": {"detected": True}})
    with pytest.raises(RuntimeError, match="shortened slice"):
        bf._self_test({"pass": True, "mutation_control": {"detected": False}})


def test_self_test_rejects_a_field_outside_the_pass_and_mutation_flags() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    bf._self_test(record)
    for mutate in (
        lambda r: r["incidences"][0]["points"][0]["fibers"][0].update(germ_dimension=9),
        lambda r: r["incidences"][1]["points"][2]["transversality"].update(closure_membership="0" * 12),
        lambda r: r["incidences"][2]["points"][3]["fibers"][1].update(embedding_rank=1),
        lambda r: r["incidences"][3].update(expected_fiber_projective_dimension_degree_components=[1, 1, 1]),
        lambda r: r["incidences"][0]["points"].pop(),
        lambda r: r.update(identity_boost_reproduces_the_retained_selection=False),
    ):
        broken = copy.deepcopy(record)
        mutate(broken)
        with pytest.raises(RuntimeError, match="disagrees|failed"):
            bf._self_test(broken)


@pytest.mark.audit
def test_the_retained_record_binds_the_current_producer_and_input_digests() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    own = Path(bf.__file__).resolve().relative_to(ROOT).as_posix()
    _same(own in record["inputs"], True)
    _same([path for path, digest in record["inputs"].items() if bf.nakayama._sha256(ROOT / path) != digest], [])


@pytest.mark.audit
def test_the_retained_record_regenerates_byte_for_byte() -> None:
    _same(bf._record_bytes(bf.build_record()), RECORD.read_bytes())
