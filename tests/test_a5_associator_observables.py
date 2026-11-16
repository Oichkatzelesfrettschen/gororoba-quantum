"""The associator observables on A_5 strata: arithmetic at the W8 representative, a moved W8 point and a compact
rotation of it, each decided in exact arithmetic."""

from __future__ import annotations

import sys
from collections.abc import Callable, Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

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


@pytest.mark.parametrize(
    "bounds,expected",
    [
        ((0, 27), [1, 3, 13, 23, 25]),
        ((27, 54), [27, 37, 39, 47, 51]),
        (
            ((3**15 - 1) // 2 - 13, (3**15 - 1) // 2 + 14),
            [(3**15 - 1) // 2 - 13 + offset for offset in (1, 3, 5, 7, 19, 21, 23, 25)],
        ),
        ((54, 54), []),
    ],
)
def test_grid_candidate_chunk_matches_bounded_scalar_equations(bounds: tuple[int, int], expected: list[int]) -> None:
    """The eight nonzero isotropic triples near the origin satisfy -u1^2-u2^2+u3^2=0.

    The first two intervals fix the remaining base-three digits at zero, hence the remaining coordinates at -1.
    Their literal indices also catch a missing interval endpoint, coordinate reversal or reordered results.
    """
    _check(probe._grid_candidate_chunk(bounds) == expected)


def test_grid_candidate_dispatch_preserves_serial_parallel_order_and_stride(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A serial candidate loop, an unordered flattening or applying the stride inside chunks breaks the contract."""
    monkeypatch.setattr(probe, "GRID_SIZE", 54)
    monkeypatch.setattr(probe, "GRID_CANDIDATE_CHUNK", 17)
    monkeypatch.setattr(probe, "GRID_STRIDE", 3)
    actual_map = probe.parallel.ordered_map
    dispatched: list[tuple[Callable[[Any], Any], int]] = []

    def record_dispatch(function: Callable[[Any], Any], items: Sequence[Any], min_items: int = 64) -> list[Any]:
        dispatched.append((function, min_items))
        return actual_map(function, items, min_items=min_items)

    monkeypatch.setattr(probe.parallel, "ordered_map", record_dispatch)
    monkeypatch.setenv("GOROROBA_WORKERS", "1")
    serial = probe._grid_candidates()
    serial_selection = probe.grid_selection()
    monkeypatch.setenv("GOROROBA_WORKERS", "2")
    pooled = probe._grid_candidates()
    pooled_selection = probe.grid_selection()
    expected = [1, 3, 13, 23, 25, 27, 37, 39, 47, 51]
    _check(serial == pooled == expected)
    _check(serial[::3] == [1, 23, 37, 51])
    selected = {name: [37] if name == "Ehat" else [] for name in probe.STRATA}
    counts = {name: int(name == "Ehat") for name in probe.STRATA}
    _check(serial_selection == pooled_selection == (selected, counts))
    candidate_dispatches = [minimum for function, minimum in dispatched if function is probe._grid_candidate_chunk]
    _check(candidate_dispatches == [1, 1, 1, 1])


def test_point_construction_dispatches_strata_and_preserves_serial_parallel_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    representatives = {name: probe.REPRESENTATIVES[name] for name in ("W8", "Ehat")}
    monkeypatch.setattr(probe, "REPRESENTATIVES", representatives)
    actual_map = probe.parallel.ordered_map
    dispatches: list[tuple[Callable[[Any], Any], int]] = []

    def record_dispatch(function: Callable[[Any], Any], items: Sequence[Any], min_items: int = 64) -> list[Any]:
        dispatches.append((function, min_items))
        return actual_map(function, items, min_items=min_items)

    monkeypatch.setattr(probe.parallel, "ordered_map", record_dispatch)
    monkeypatch.setenv("GOROROBA_WORKERS", "1")
    serial = probe.point_specs({name: [] for name in representatives})
    monkeypatch.setenv("GOROROBA_WORKERS", "2")
    pooled = probe.point_specs({name: [] for name in representatives})
    _check(serial == pooled)
    movement = probe.programs()
    per_stratum = len(movement) + 3 * len(probe.AUTOMORPHISM_NAMES) + len(probe.PHASE_BASES) * len(probe.PHASES)
    _check([spec.stratum for spec in pooled] == ["W8"] * per_stratum + ["Ehat"] * per_stratum)
    _check([spec.label for spec in pooled[: len(movement)]] == [probe.program_label(item[1]) for item in movement])
    _check(dispatches == [(probe.stratum_point_specs, 1), (probe.stratum_point_specs, 1)])


def test_doubling_basis_pairs_dispatch_and_detect_a_product_mutation(monkeypatch: pytest.MonkeyPatch) -> None:
    actual_map = probe.parallel.ordered_map
    dispatches: list[tuple[Callable[[Any], Any], list[Any], int]] = []

    def record_dispatch(function: Callable[[Any], Any], items: Sequence[Any], min_items: int = 64) -> list[Any]:
        dispatches.append((function, list(items), min_items))
        return actual_map(function, items, min_items=min_items)

    monkeypatch.setattr(probe.parallel, "ordered_map", record_dispatch)
    monkeypatch.setenv("GOROROBA_WORKERS", "2")
    _check(probe.doubling_failures() == 0)
    function, pairs, minimum = dispatches[0]
    _check(function is probe.doubling_pair_failure and minimum == 1)
    _check(pairs == [(first, second) for first in range(32) for second in range(32)])
    actual_product = probe.cd_multiply_exact

    def altered_product(dimension: int, first: Sequence[Fraction], second: Sequence[Fraction]) -> tuple[Fraction, ...]:
        result = list(actual_product(dimension, first, second))
        if dimension == probe.DIM:
            result[0] += 1
        return tuple(result)

    monkeypatch.setattr(probe, "cd_multiply_exact", altered_product)
    _check(probe.doubling_pair_failure((0, 0)) == 1)


def test_real_scaling_preserves_normalized_observables_and_changes_raw_spectrum() -> None:
    operand = _w8()
    base = probe.observables(operand)
    scaled = probe.observables([2 * coefficient for coefficient in operand])
    for field in ("rank_left", "rank_right", "nullity_left", "nullity_right", "spectrum", "spectrum_id"):
        _check(scaled[field] == base[field])
    _check(Fraction(scaled["norm"]) == 4 * Fraction(base["norm"]))
    _check(scaled["charpoly"] != base["charpoly"])
    _check(
        all(
            Fraction(changed) == Fraction(original) * 4 ** (probe.DIM - degree)
            for degree, (original, changed) in enumerate(zip(base["charpoly"], scaled["charpoly"], strict=True))
        )
    )
