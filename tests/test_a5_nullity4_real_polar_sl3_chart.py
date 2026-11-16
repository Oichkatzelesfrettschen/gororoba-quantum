"""The SL(3, C) chart at the polar normal form: structure, equations, Krawczyk boxes and the eliminant factor."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles-residuals"))

import nullity4_real_polar_sl3_chart as sc  # noqa: E402
import sympy as sp  # noqa: E402
from flint import arb, fmpq  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def test_chart_is_hermitian_equivariant_and_carries_the_row_relation() -> None:
    _same(sc.chart_facts(), sc.CHART)


def test_a_matrix_outside_g2_fails_equivariance_alone(monkeypatch: pytest.MonkeyPatch) -> None:
    # g with 1 added to its real diagonal entry (1, 1): still Hermitian, no longer equivariant.
    chart = sc.chart()
    broken = chart.copy()
    broken[0, 0] += 1
    monkeypatch.setattr(sc, "chart", lambda: broken)
    sc._pairings.cache_clear()
    try:
        facts = sc.chart_facts()
        _same((facts["hermitian"], facts["equivariant"]), (True, False))
    finally:
        monkeypatch.undo()
        sc._pairings.cache_clear()


def test_equations_are_real_with_the_pinned_shape() -> None:
    _same(sc.equation_facts(), sc.EQUATIONS)


def test_polynomials_vanish_with_the_pairings_at_a_rational_point() -> None:
    # p_k is the numerator of the real part: at a rational point p_0 / (32 d2^2) is the entry F_0 itself.
    point = {sc.D2: sp.Rational(3, 2), sc.X21: sp.Rational(1, 3), sc.Y31: sp.Rational(-2, 5)}
    f, _ = sc._pairings()
    p0 = sc.polynomials()[0].as_expr().subs(point)
    _same(sp.simplify(f[0, 0].subs(point) - p0 / (32 * sp.Rational(3, 2) ** 2)), 0)


@pytest.mark.parametrize("job", sc.BOX_JOBS)
def test_krawczyk_test_holds_on_the_box(job: tuple[str, int]) -> None:
    _same(sc.krawczyk(job), sc.BOXES[job[0]][str(job[1])])
    _same(sc.ctx.prec, job[1])


def test_a_void_certificate_is_refused_and_a_wide_box_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(RuntimeError, match="below 64 bits"):
        sc.krawczyk(("coarse", 32))
    with pytest.raises(RuntimeError, match="unknown box"):
        sc.krawczyk(("wide", 200))
    monkeypatch.setattr(sc, "RADIUS_BITS", 0)
    with pytest.raises(RuntimeError, match="point evaluation"):
        sc.krawczyk(("coarse", 200))
    monkeypatch.setattr(sc, "RADIUS_BITS", 2)
    _same(sc.krawczyk(("coarse", 200))["interior"], False)


def test_a_box_away_from_the_zero_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    shifted = (sc.MIDPOINT[0] + (1 << 20), sc.MIDPOINT[1], sc.MIDPOINT[2])
    monkeypatch.setattr(sc, "MIDPOINT", shifted)
    _same(sc.krawczyk(("coarse", 200))["interior"], False)


def test_fine_box_is_a_refinement_of_the_coarse_midpoint() -> None:
    fine = sc.fine_midpoint()
    for coarse_numerator, fine_numerator in zip(sc.MIDPOINT, fine, strict=True):
        distance = abs(fmpq(fine_numerator, 1 << sc.FINE_GRID_BITS) - fmpq(coarse_numerator, 1 << sc.GRID_BITS))
        _same(bool(distance < fmpq(1, 1 << sc.GRID_BITS)), True)
    _same(sc._nested(), True)


def test_largest_power_reads_both_directions() -> None:
    _same(sc._largest_power(arb(fmpq(1, 9)), True, 10), 3)
    _same(sc._largest_power(arb(17), False, 10), 4)
    _same(sc._largest_power(arb(2), True, 10), -1)
    _same(sc._largest_power(arb(fmpq(1, 2)), False, 10), -1)


def test_degree_facts_name_the_factor_of_degree_88() -> None:
    _same(sc.degree_facts(), sc.DEGREE)


def test_an_eliminant_with_a_planted_factor_changes_the_degrees(monkeypatch: pytest.MonkeyPatch) -> None:
    # The retained polynomial times (t - 1): one more factor, whose ball excludes 0, and the same factor at the point.
    data = dict(sc._eliminant())
    coefficients = [int(text) for text in data["eliminant"]]
    shifted = [0, *coefficients]
    product = [a - b for a, b in zip(shifted, [*coefficients, 0], strict=True)]
    data["eliminant"] = [str(c) for c in product]
    monkeypatch.setattr(sc, "_eliminant", lambda: data)
    facts = sc.degree_facts()
    _same(facts["eliminant_degree"], sc.DEGREE["eliminant_degree"] + 1)
    _same(facts["factor_degrees"][0], [1, 1])
    _same(facts["degrees_of_the_factors_whose_ball_holds_zero"], [88])


def test_an_eliminant_of_another_form_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sc, "FORM", (1, 2, 3, 5))
    sc._eliminant.cache_clear()
    try:
        with pytest.raises(RuntimeError, match="another linear form"):
            sc._eliminant()
    finally:
        monkeypatch.undo()
        sc._eliminant.cache_clear()


def test_an_unknown_fact_is_refused() -> None:
    with pytest.raises(RuntimeError, match="unknown fact"):
        sc.fact("rank")


def test_msolve_input_names_the_saturation() -> None:
    text = sc.msolve_input()
    _same(text.splitlines()[:2], ["w,x21,y31,d2", "0"])
    _same(text.rstrip().endswith("w*d2-1"), True)
    _same(text.count(",\n"), 3)


def _record() -> dict[str, Any]:
    record: dict[str, Any] = json.loads(sc.RECORD.read_text(encoding="utf-8"))
    return record


def test_pinned_record_passes_its_rules(monkeypatch: pytest.MonkeyPatch) -> None:
    record = _record()
    retained_inputs = dict(record["inputs"])
    monkeypatch.setattr(sc, "_inputs", lambda: dict(retained_inputs))
    _same(sc.verdict(record), [])
    _same(record["pass"], True)
    _same(sc._serialized(record), sc.RECORD.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("label", "mutate"),
    [
        ("equivariance", lambda r: r["chart"].__setitem__("equivariant", False)),
        ("a degree", lambda r: r["equations"]["degrees"].__setitem__(2, 15)),
        ("the midpoint", lambda r: r["midpoint"]["numerators"].__setitem__(0, 1)),
        ("a Krawczyk test", lambda r: r["boxes"]["coarse"]["400"].__setitem__("interior", False)),
        ("the nesting", lambda r: r["boxes"]["fine"]["1500"].__setitem__("inside_the_coarse_box", False)),
        (
            "the factor at the point",
            lambda r: r["degree"].__setitem__("degrees_of_the_factors_whose_ball_holds_zero", [36]),
        ),
        ("the verdict flag", lambda r: r.__setitem__("pass", False)),
    ],
)
def test_record_rules_reject_a_planted_mutant(label: str, mutate: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    record = _record()
    retained_inputs = dict(record["inputs"])
    monkeypatch.setattr(sc, "_inputs", lambda: dict(retained_inputs))
    mutate(record)
    if not sc.verdict(record):
        raise AssertionError(label)
