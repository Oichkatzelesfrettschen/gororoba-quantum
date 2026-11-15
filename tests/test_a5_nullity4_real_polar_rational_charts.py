"""Rational charts of G_2(C) at the polar normal form: stabilizers, root subgroups, boost families, precisions."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles-residuals"))

import nullity4_real_polar_fiber_four as ff  # noqa: E402
import nullity4_real_polar_rational_charts as rc  # noqa: E402
import sympy as sp  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def test_normal_form_has_zero_incidence_and_zero_pairing() -> None:
    # Pi = 1: z_0 is Hermitian-orthogonal to l and so is all of C(l), the point with dim L = 6 the charts start from.
    z0, line, kernel = rc.polar()
    _same(any(z0.H * line), False)
    _same(any(kernel.H * line), False)


def test_stabilizers_are_one_subalgebra() -> None:
    _same(rc.stabilizer_facts(), rc.STABILIZERS)


def test_an_unknown_stabilizer_is_refused() -> None:
    with pytest.raises(RuntimeError, match="unknown stabilizer"):
        rc._stabilizer_job("line")


@pytest.mark.parametrize(
    ("job", "expected"),
    [
        ((0, 1, 1), [False, False]),  # nilpotent of order 2 that moves z_0 off the incidence
        ((2, 6, 1), [True, True]),  # nilpotent of order 3 that keeps the incidence and the zero pairing
        ((0, 3, 1), None),  # not nilpotent
    ],
)
def test_root_subgroup_classes(job: tuple[int, int, int], expected: list[bool] | None) -> None:
    _same(rc.root_subgroup(job), expected)


@pytest.mark.audit
def test_root_subgroup_tally() -> None:
    _same(rc.root_subgroup_tally(), rc.ROOT_SUBGROUPS)


@pytest.mark.parametrize("job", rc.FAMILY_JOBS)
def test_boost_family_fact(job: tuple[str, str]) -> None:
    _same(rc.family_fact(job), rc.FAMILY_FACTS[job[0]][job[1]])


def test_a_generator_outside_g2_fails_the_structure(monkeypatch: pytest.MonkeyPatch) -> None:
    # The single rotation of the plane (e_1, e_4) is skew and not a derivation of the octonions.
    families = {name: dict(data) for name, data in rc.FAMILIES.items()}
    families["4, 7"]["L"] = [[(1, 4, 1)], families["4, 7"]["L"][1]]
    monkeypatch.setattr(rc, "FAMILIES", families)
    rc._family.cache_clear()
    rc._hermitian_element.cache_clear()
    try:
        _same(rc.family_structure("4, 7")["in_g2"], False)
    finally:
        monkeypatch.undo()
        rc._family.cache_clear()
        rc._hermitian_element.cache_clear()


def test_generators_that_do_not_commute_fail_that_clause_alone(monkeypatch: pytest.MonkeyPatch) -> None:
    # R_1 of the family (5, 6) in place of R_1 of (4, 7): a derivation, so membership holds, and it does not
    # commute with L_1.
    families = {name: dict(data) for name, data in rc.FAMILIES.items()}
    families["4, 7"]["R"] = [rc.FAMILIES["5, 6"]["R"][0], families["4, 7"]["R"][1]]
    monkeypatch.setattr(rc, "FAMILIES", families)
    rc._family.cache_clear()
    rc._hermitian_element.cache_clear()
    try:
        facts = rc.family_structure("4, 7")
        _same((facts["in_g2"], facts["commute"]), (True, False))
    finally:
        monkeypatch.undo()
        rc._family.cache_clear()
        rc._hermitian_element.cache_clear()


def test_reduction_uses_both_relations() -> None:
    _same(rc._reduced(rc.SL**2 + rc.CL**2), 1)
    _same(rc._reduced(rc.CHR**2 - rc.SHR**2), 1)
    _same(rc._reduced(rc.SL * rc.CHL) == 0, False)


def test_an_unknown_family_or_fact_is_refused() -> None:
    with pytest.raises(RuntimeError, match="unknown family"):
        rc.family_fact(("4, 5", "structure"))
    with pytest.raises(RuntimeError, match="unknown fact"):
        rc.family_fact(("4, 7", "rank"))


@pytest.mark.parametrize("precision", rc.PRECISIONS)
def test_krawczyk_test_holds_at_the_precision(precision: int) -> None:
    _same(rc.krawczyk_at(precision), rc.KRAWCZYK)


@pytest.mark.parametrize("precision", rc.PRECISIONS)
def test_evaluation_keeps_its_precision_on_a_cold_cache(precision: int) -> None:
    # ff._pairing_factors sets the context to 200 bits on its first call; the evaluation must end at its own.
    ff._pairing_factors.cache_clear()
    rc.ctx.prec = 53
    rc.evaluation_at((precision, ff.RADIUS_BITS, ff.SLICE_FREE[0]))
    _same(rc.ctx.prec, precision)


def test_evaluation_at_200_bits_is_the_evaluation_of_the_certificate() -> None:
    # The same job through both modules: the serialized balls agree, so krawczyk_at repeats the test of ff.
    k = ff.SLICE_FREE[0]
    _same(rc.evaluation_at((ff.PRECISION, ff.RADIUS_BITS, k)), ff.evaluation((ff.RADIUS_BITS, ff.MIDPOINT, k)))


def test_a_low_precision_is_refused_and_a_wide_box_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(RuntimeError, match="below 64 bits"):
        rc.evaluation_at((32, ff.RADIUS_BITS, ff.SLICE_FREE[0]))
    monkeypatch.setattr(ff, "RADIUS_BITS", 2)
    _same(rc.krawczyk_at(131)["interior"], False)


def _record() -> dict[str, Any]:
    return json.loads(rc.RECORD.read_text(encoding="utf-8"))


def test_pinned_record_passes_its_rules(monkeypatch: pytest.MonkeyPatch) -> None:
    record = _record()
    retained_inputs = dict(record["inputs"])
    monkeypatch.setattr(rc, "_inputs", lambda: dict(retained_inputs))
    _same(rc.verdict(record), [])
    _same(record["pass"], True)
    _same(rc._serialized(record), rc.RECORD.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("label", "mutate"),
    [
        ("a stabilizer dimension", lambda r: r["stabilizers"].__setitem__("span", 4)),
        ("the root subgroup tally", lambda r: r["root_subgroups"].__setitem__("pairing_zero_among_them", 23)),
        ("a minor", lambda r: r["families"]["4, 7"].__setitem__("minor", "0")),
        ("an instance rank", lambda r: r["families"]["5, 6"]["instance"].__setitem__(3, 1)),
        ("a precision", lambda r: r["precisions"]["400"].__setitem__("interior", False)),
        ("the verdict flag", lambda r: r.__setitem__("pass", False)),
    ],
)
def test_record_rules_reject_a_planted_mutant(label: str, mutate: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    record = _record()
    retained_inputs = dict(record["inputs"])
    monkeypatch.setattr(rc, "_inputs", lambda: dict(retained_inputs))
    mutate(record)
    if not rc.verdict(record):
        raise AssertionError(label)


def test_sympy_is_exact_here() -> None:
    _same(sp.Rational(rc.INSTANCE["C"]) ** 2 - sp.Rational(rc.INSTANCE["S"]) ** 2, 1)
    _same(sp.Rational(rc.INSTANCE["c"]) ** 2 + sp.Rational(rc.INSTANCE["s"]) ** 2, 1)
