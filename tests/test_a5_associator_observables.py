"""The associator observables on A_5 strata: arithmetic at the W8 representative, a moved W8 point and a compact
rotation of it, each decided in exact arithmetic."""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/a5-associator-observables"
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(EVIDENCE))

import associator_observables as probe  # noqa: E402


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def _w8(program: probe.Program = ()) -> list[Fraction]:
    return probe.y_from_split(probe.apply_program(probe.REPRESENTATIVES["W8"], program))


def test_w8_representative_has_associator_rank_16_and_nullity_8() -> None:
    obs = probe.observables(_w8())
    _check(obs["nullity_left"] == 8 and obs["nullity_right"] == 8)
    _check(obs["rank_left"] == 16 and obs["rank_right"] == 16)
    _check(obs["consistent"])
    _check(probe.certified_stratum(_w8()) == "W8")


def test_a_unipotent_moved_w8_point_stays_in_w8_with_associator_rank_24() -> None:
    moved = _w8((("u", 0, Fraction(1)),))
    obs = probe.observables(moved)
    _check(probe.certified_stratum(moved) == "W8" and obs["nullity_left"] == 8)
    _check(obs["rank_left"] == 24 and obs["rank_right"] == 24)
    _check(obs["spectrum_id"] != probe.observables(_w8())["spectrum_id"])


def test_a_compact_rotation_and_the_reflection_leave_every_observable_unchanged() -> None:
    moved = _w8((("u", 0, Fraction(1)),))
    base = probe.observables(moved)
    for name in ("rot-a", "reflect"):
        matrix = probe.automorphism_matrix(name)
        _check(probe.automorphism_failures(matrix) == 0)
        image = probe._apply(matrix, moved)
        _check(image != moved)
        _check(probe.observables(image) == base)
        _check(probe.certified_stratum(image) == "W8")


def test_the_unipotent_realization_and_a_mutated_rotation_are_not_automorphisms() -> None:
    unipotent = probe.induced_real_map(
        lambda z: probe.independent.act_g2(probe.unipotent(0, Fraction(1)), z),
    )
    _check(probe.automorphism_failures(unipotent) > 0)
    _check(probe.automorphism_failures(probe._mutated_matrix()) > 0)


def test_b9_representative_attains_the_maximal_associator_rank_28() -> None:
    obs = probe.observables(probe.y_from_split(probe.REPRESENTATIVES["B9"]))
    _check(obs["rank_left"] == 28 and obs["nullity_left"] == 12 and obs["consistent"])


def test_summary_counts_exact_coordinates_and_refuses_inconsistent_duplicates(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(probe, "STRATA", {"W8": probe.STRATA["W8"]})
    representative = probe.REPRESENTATIVES["W8"]
    moved = probe.apply_program(representative, (("u", 0, Fraction(1)),))
    specs = [
        probe.PointSpec("W8", "representative", "rep", representative),
        probe.PointSpec("W8", "unipotent", "stabilized", representative),
        probe.PointSpec("W8", "unipotent", "moved", moved),
    ]
    rows = [probe.evaluate_point(spec) for spec in specs]
    summary = probe._summaries(rows, specs)["W8"]
    _check(summary["evaluations"] == 3 and summary["points"] == 2 and summary["certified"] == 2)
    _check(summary["rank_values"] == {"16": 1, "24": 1})
    _check(summary["points_by_family"]["unipotent"] == 2)
    rows[1]["obs"] = {**rows[1]["obs"], "rank_left": 24}
    with pytest.raises(RuntimeError, match="duplicate coordinates"):
        probe._summaries(rows, specs)
