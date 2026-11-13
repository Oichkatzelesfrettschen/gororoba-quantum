"""The exact Q(i) arcs behind the characteristic-0 arc-jet bounds: series arithmetic, reduction, valuation drops."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TRANSFER = ROOT / "docs" / "evidence" / "a5-char0-transfer"
sys.path.insert(0, str(TRANSFER))

import arc_jets_qi as qi  # noqa: E402

jr = qi.jr
PRECISION = 8
RANKS = {"1": 21, "2": 83, "3": 225, "4": 495, "5": 952, "6": 1666, "7": 2718}


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def test_inverse_of_a_unit_series_is_exact() -> None:
    series = qi.Series([2, 3, 0, 5], [], PRECISION)
    product = series * series.inv()
    _same([product.coefficient(k) for k in range(PRECISION)], [(1, 0)] + [(0, 0)] * (PRECISION - 1))


def test_inverse_refuses_a_series_without_a_rational_unit_constant_term() -> None:
    with pytest.raises(ZeroDivisionError):
        qi.Series([0, 1], [], PRECISION).inv()
    with pytest.raises(ZeroDivisionError):
        qi.Series([1], [1], PRECISION).inv()


def test_multiplication_uses_i_squared_equal_to_minus_one() -> None:
    i = qi.Series.const(0, 1, PRECISION)
    _same((i * i).coefficient(0), (-1, 0))


def test_reduction_sends_i_to_the_root_and_rejects_a_denominator_divisible_by_p() -> None:
    _same(qi.reduce_gauss((Fraction(1, 2), Fraction(3)), 32009, 10754), (pow(2, -1, 32009) + 3 * 10754) % 32009)
    _same(qi.reduce_gauss((Fraction(1, 32009), Fraction(0)), 32009, 10754), None)
    _same(qi.reduce_gauss((Fraction(32009), Fraction(0)), 32009, 10754), 0)


@pytest.mark.parametrize("name", ["e8nm-p32009", "e8np-p32029"])
@pytest.mark.parametrize("idx", [0, 1, 2])
def test_exact_arc_reduces_to_the_modular_arc_with_the_same_valuations(name: str, idx: int) -> None:
    target = jr.TARGETS[name]
    modular = [t.to_series(PRECISION) for t in jr.arc(target, idx)]
    exact = qi.arc(target.prime, target.sign9, idx, PRECISION)
    for series, reference in zip(exact, modular, strict=True):
        coefficients = [int(c) for c in reference.c.coeffs()] + [0] * PRECISION
        images = [qi.reduce_gauss(series.coefficient(k), target.prime, target.root) for k in range(PRECISION)]
        _same(images, coefficients[:PRECISION])
        _same(series.valuation(), next((k for k in range(PRECISION) if coefficients[k]), None))


def test_sign_of_t9_separates_the_two_headers() -> None:
    minus = qi.arc(32009, 1, 0, PRECISION)[8]
    plus = qi.arc(32009, -1, 0, PRECISION)[8]
    _same((minus + plus).valuation(), None)
    if minus.valuation() is None:
        raise AssertionError("t9 vanishes on the arc")


def test_a_coefficient_divisible_by_p_lowers_the_exact_valuation_only() -> None:
    """The failure the certificate excludes: p t3 vanishes modulo p and has the valuation of t3 over Q(i)."""
    target = jr.TARGETS["e8nm-p32009"]
    arc = qi.arc(target.prime, target.sign9, 0, PRECISION)
    poly: qi.Coefficients = {(0, 0, 1, 0, 0, 0, 0, 0, 0): (Fraction(target.prime), Fraction(0))}
    series = qi.evaluate(poly, arc)
    _same(series.valuation(), arc[2].valuation())
    images = [qi.reduce_gauss(series.coefficient(k), target.prime, target.root) for k in range(PRECISION)]
    _same(images, [0] * PRECISION)


@pytest.mark.parametrize("slug", sorted(qi.TARGETS))
def test_retained_record_states_the_bounds_for_every_degree(slug: str) -> None:
    record = json.loads((TRANSFER / f"arc-jets-qi-{slug}.json").read_text(encoding="utf-8"))
    _same(record["verdict"], "lower_bounds_hold_over_qi")
    _same(record["j_on_phi"]["phi"], {"generators": 16, "nonzero": 0})
    if not record["j_on_phi"]["mutated"]["nonzero"]:
        raise AssertionError("the mutated arc family passes the J identity")
    _same(sorted({degree for cell in record["cells"] for degree in cell["lower_bounds"]}), sorted(RANKS))
    for cell in record["cells"]:
        _same((cell["arcs_checked"], cell["arcs_with_problems"], cell["arcs_differing_from_record"]), (3000, [], []))
        for degree, bound in cell["lower_bounds"].items():
            _same((bound["rank"], bound["arcs_within_checked"]), (RANKS[degree], True))


@pytest.mark.audit
@pytest.mark.parametrize("slug", sorted(qi.TARGETS))
def test_retained_record_binds_its_sources_and_modular_records(slug: str) -> None:
    """On demand: a change to a bound source needs the records regenerated, which costs 8,800 CPU seconds."""
    record = json.loads((TRANSFER / f"arc-jets-qi-{slug}.json").read_text(encoding="utf-8"))
    _same(record["sha256"]["arc_jets_qi"], qi._sha256(TRANSFER / "arc_jets_qi.py"))
    _same(record["sha256"]["jet_rank"], qi._sha256(qi.ARC_JETS / "jet_rank.py"))
    _same(record["sha256"]["reduction_check"], qi._sha256(TRANSFER / "reduction_check.py"))
    for cell in record["cells"]:
        for bound in cell["lower_bounds"].values():
            _same(bound["sha256"], qi._sha256(ROOT / bound["record"]))


def test_a_missing_degree_record_stops_the_run(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(qi, "DEGREES", (*qi.DEGREES, 8))
    with pytest.raises(SystemExit, match="degrees"):
        qi.compute("e8-nm")


def test_the_coordinate_valuation_drop_at_32009_leaves_e_and_v_in_place() -> None:
    """Arc 2996 of E8-bar -> N- at 32009: t2 has valuation 3 over Q(i) and 4 modulo p, and the arc has no problem."""
    record = json.loads((TRANSFER / "arc-jets-qi-e8-nm.json").read_text(encoding="utf-8"))
    cell = next(c for c in record["cells"] if c["target"] == "e8nm-p32009")
    drops = {row["index"]: row["drops"] for row in cell["coordinate_valuation_drops"]}
    _same(drops.get(2996), ["t2: valuation 3 over Q(i), 4 modulo p"])
