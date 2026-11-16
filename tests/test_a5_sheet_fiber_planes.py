"""The sheet decomposition, special-fiber planes and exact arcs of the E8bar->Va slice germs."""

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


def _arc(lower_containing: list[str]) -> dict[str, object]:
    return {
        "closure_generators_nonzero_on_arc": 0,
        "germ_generators_nonzero_on_arc": 0,
        "sheet_generators_nonzero_on_arc": 0,
        "lower_closures_containing_the_arc": lower_containing,
        "schur_lowest_order_in_u": 1,
        "schur_leading_vector_equals_embedded_rees_leading_vector": True,
        "leading_vector_is_nonzero_and_on_plane": True,
        "rank_C_z_at_parameter": {"0": 8, "1": 10, "2": 10, "3": 10},
    }


def test_an_arc_passes_only_with_vanishing_generators_the_named_lower_closures_and_the_rank_jump() -> None:
    arc = _arc([])
    _same(sfp._arc_passes(arc, []), True)
    _same(sfp._arc_passes({**arc, "sheet_generators_nonzero_on_arc": 1}, []), False)
    _same(sfp._arc_passes({**arc, "closure_generators_nonzero_on_arc": 1}, []), False)
    _same(sfp._arc_passes({**arc, "rank_C_z_at_parameter": {"0": 8, "1": 10, "2": 9, "3": 10}}, []), False)


def test_rank_10_with_the_arc_inside_a_lower_closure_does_not_pass_as_an_open_orbit_arc() -> None:
    in_x_plus = _arc(["Xp"])
    _same(sfp._arc_passes(in_x_plus, []), False)
    _same(sfp._arc_passes(in_x_plus, ["Xp"]), True)
    _same(sfp._arc_passes(in_x_plus, ["Xm"]), False)


def test_the_conic_arc_point_satisfies_the_sheet_conic_and_the_line_keeps_t2_and_t8_zero() -> None:
    coefficients = sfp.ARCS["E8bar->Va+"]
    for parameter in (1, 2, 3):
        point = sfp._arc_point(coefficients, True, parameter)
        _same(point[1] ** 2 + point[7] ** 2 + 2 * point[1], Fraction(0))
        _same(point[0], Fraction(coefficients[0] * parameter))
        line = sfp._arc_point(coefficients, False, parameter)
        _same((line[1], line[7]), (Fraction(0), Fraction(0)))
    _same(sfp._arc_point(coefficients, True, 2)[1], Fraction(-8, 5))
    _same(sfp._arc_image(coefficients, True)[7], "-2*u*d")
    _same(sfp._arc_image(coefficients, False)[7], "(0)*u")


def test_rank_of_c_z_along_each_arc_jumps_from_8_at_the_basepoint_to_10() -> None:
    first_order = sfp.nakayama._load_json(sfp.nakayama.FIRST_ORDER_RESULT)
    for entry in first_order["incidences"]:
        if entry["incidence"] in sfp.INCIDENCES:
            for conic in (True, False):
                _same(
                    sfp._rank_along_arc(entry, sfp.ARCS[str(entry["incidence"])], conic),
                    {"0": 8, "1": 10, "2": 10, "3": 10},
                )


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
