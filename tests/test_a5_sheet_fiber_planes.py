"""The sheet decomposition, special-fiber planes and exact line arc of the E8bar->Va slice germs."""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ATTACHMENTS = ROOT / "docs" / "evidence" / "a5-kernel-attachments"
sys.path.insert(0, str(ATTACHMENTS))

import sheet_fiber_planes as sfp  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _gaussian(real: int, imaginary: int = 0) -> tuple[Fraction, Fraction]:
    return Fraction(real), Fraction(imaginary)


def test_lowest_order_and_leading_coefficients_of_series_with_a_zero_series() -> None:
    series = [[_gaussian(0)], [_gaussian(0), _gaussian(2, 1), _gaussian(5)], [_gaussian(0), _gaussian(0), _gaussian(3)]]
    _same(sfp._lowest_order(series), 1)
    _same(sfp._coefficient_at(series, 1), (_gaussian(0), _gaussian(2, 1), _gaussian(0)))
    _same(sfp._coefficient_at(series, 2), (_gaussian(0), _gaussian(5), _gaussian(3)))
    with pytest.raises(RuntimeError, match="zero"):
        sfp._lowest_order([[_gaussian(0)], [_gaussian(0)]])


def test_a_special_fiber_must_be_cut_out_by_coordinate_hyperplanes() -> None:
    _same(sfp._plane_coordinates({"generators": ["y6", "y1", "y2"]}), ["y1", "y2", "y6"])
    with pytest.raises(RuntimeError, match="coordinate hyperplanes"):
        sfp._plane_coordinates({"generators": ["y1", "y2+y3"]})


def test_an_arc_passes_only_with_vanishing_generators_and_the_rank_jump_from_8_to_10() -> None:
    arc = {
        "closure_generators_nonzero_on_arc": 0,
        "germ_generators_nonzero_on_arc": 0,
        "sheet_generators_nonzero_on_arc": 0,
        "schur_lowest_order_in_u": 1,
        "schur_leading_vector_equals_embedded_rees_leading_vector": True,
        "leading_vector_is_nonzero_and_on_plane": True,
    }
    ranks = {"0": 8, "1": 10, "2": 10, "3": 10}
    _same(sfp._arc_passes(arc, ranks), True)
    _same(sfp._arc_passes({**arc, "sheet_generators_nonzero_on_arc": 1}, ranks), False)
    _same(sfp._arc_passes(arc, {**ranks, "2": 9}), False)


def test_rank_of_c_z_along_each_line_arc_jumps_from_8_at_the_basepoint_to_10() -> None:
    first_order = sfp.nakayama._load_json(sfp.nakayama.FIRST_ORDER_RESULT)
    for entry in first_order["incidences"]:
        if entry["incidence"] in sfp.INCIDENCES:
            _same(sfp._rank_along_arc(entry, sfp.ARCS[str(entry["incidence"])]), {"0": 8, "1": 10, "2": 10, "3": 10})


def test_self_test_rejects_a_failed_record_and_a_surviving_mutation() -> None:
    with pytest.raises(RuntimeError, match="failed"):
        sfp._self_test({"pass": False, "mutation_control": {"detected": True}})
    with pytest.raises(RuntimeError, match="survived"):
        sfp._self_test({"pass": True, "mutation_control": {"detected": False}})


@pytest.mark.audit
def test_retained_record_is_the_regenerated_record() -> None:
    record = sfp.build_record()
    _same(record["pass"], True)
    _same(sfp._record_bytes(record), (ATTACHMENTS / "sheet-fiber-planes-result.json").read_bytes())
