"""Real points of V(G) minus V(Q): the orbit rank 13 locus, the polar line at mu = 0 and the record rules."""

from __future__ import annotations

import copy
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles-residuals"))

import nullity4_real_polar_line as module  # noqa: E402
import sympy as sp  # noqa: E402

Mutation = tuple[str, Callable[[dict[str, Any]], Any]]


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


@pytest.mark.parametrize("name", module.IDENTITIES)
def test_exact_identity_holds(name: str) -> None:
    _same(module.identity(name), True)


def _unit(index: int) -> list[int]:
    return [1 if column == index else 0 for column in range(7)]


def test_orbit_rank_is_13_on_an_associative_plane_and_16_off_it() -> None:
    first, second = [1, 2, 0, 1, 0, 0, 0], [0, 1, 3, 0, 1, 0, 0]
    third = module.cross(first, second)
    inside = [first, second, third, [a + b for a, b in zip(first, third, strict=True)]]
    _same(module.quaternion_position(inside), True)
    _same(module.orbit_rank(module.point_from_parts(inside, (2, -1))), 13)
    # A cross product with its sign reversed still lies in the plane; a vector outside it leaves the position.
    outside = [first, second, third, [0, 0, 0, 0, 0, 1, 0]]
    _same(module.quaternion_position(outside), False)
    _same(module.orbit_rank(module.point_from_parts(outside, (2, -1))), 16)


def test_orbit_rank_hypothesis_is_nonzero_gram_determinant() -> None:
    # u = e_1 + i e_2 is null: Delta = 0, W is a plane, and the phase is absorbed by a rotation, so the rank is 12.
    parts = [_unit(0), _unit(1), [0] * 7, [0] * 7]
    _same(module.gram_determinant(parts), 0)
    _same(module.orbit_rank(module.point_from_parts(parts, (0, 0))), 12)
    parts = [_unit(0), [0] * 7, _unit(1), [0] * 7]
    _same(module.gram_determinant(parts) != 0, True)
    _same(module.orbit_rank(module.point_from_parts(parts, (0, 0))), 13)


def test_a_sample_of_each_kind_has_the_predicted_rank() -> None:
    for kind in module.SAMPLE_KINDS:
        parts = module.sample_parts(kind, f"test:{kind}")
        if module.gram_determinant(parts) == 0:
            continue
        rank = module.orbit_rank(module.point_from_parts(parts, (1, 1)))
        _same(rank, 13 if module.quaternion_position(parts) else 16)


@pytest.mark.parametrize("line", module.ZERO_LINES)
def test_the_polar_line_at_mu_zero_lies_in_one_eigenline(line: tuple[int, int]) -> None:
    sigma, sign = line
    eps = -sigma * sign
    _same(module.mu_zero_line((sigma, sign, 1)), [6, eps, True, 0, 5 if eps == -1 else 1, 1 if eps == -1 else 5])


def test_a_flipped_sign_in_a_derivation_leaves_the_frame_stabilizer(monkeypatch: pytest.MonkeyPatch) -> None:
    entries = [list(rows) for rows in module.polar.DERIVATION_ENTRIES]
    entries[1][0] = (entries[1][0][0], entries[1][0][1], -entries[1][0][2])
    monkeypatch.setattr(module.polar, "DERIVATION_ENTRIES", tuple(tuple(rows) for rows in entries))
    _same(module.frame_stabilizer_is_su2_acting_freely_on_the_complement(), False)


def test_the_polar_line_eigenline_decides_the_containment() -> None:
    # sigma = 1, s = i: the polar line lies in E_-, so C(l_z) lies in C z_0 + E_+ and not in C z_0 + E_-.
    z0, line, kernel = module.polar_data(1, sp.I, 1, 0)
    e8: list[Any] = [0] * 15
    e8[7] = 1
    _same(module._rank(line + module.eigenline(-1)), 7)
    for sign, contained in ((1, True), (-1, False)):
        lines = module.eigenline(sign)
        _same(module._rank([*lines, z0, e8, *kernel]) == module._rank([*lines, z0, e8]), contained)


def test_first_order_pairing_at_mu_nonzero_is_definite() -> None:
    _same(module.first_order_pairing((1, 0)), module.FIRST_ORDER)


def test_witness_has_a_two_dimensional_fiber_and_a_moved_point_does_not() -> None:
    coordinates = module.WITNESSES[0]
    _same(module.witness_facts(coordinates), module.WITNESS_FACTS)
    moved = (str(float(coordinates[0]) + 0.5), *coordinates[1:])
    _same(module.witness_facts(moved) != module.WITNESS_FACTS, True)


@pytest.mark.parametrize("index", [0, 1])
def test_witness_singular_values_show_the_gaps(index: int) -> None:
    found = module.witness_singular_values(module.WITNESSES[index])
    _same(found, module.WITNESS_SINGULAR_VALUES[index])
    _same(found["M(z)"].count("0"), 3)
    _same(found["fiber system"].count("0"), 2)
    coordinates = module.WITNESSES[index]
    moved = (str(float(coordinates[0]) + 0.5), *coordinates[1:])
    _same(module.witness_singular_values(moved) != found, True)


@pytest.mark.parametrize("index", [0, 1])
def test_normal_form_calibration_has_the_whole_common_kernel_as_fiber(index: int) -> None:
    _same(module.witness_facts(module.CALIBRATIONS[index]), module.CALIBRATION_FACTS[index])


def test_retained_kernel_vector_nullities_are_twice_the_plane_nullity_less_one() -> None:
    _same(module.fixture_kernel_nullities(), {"fixtures": 66, "agree": 66})


def test_the_kernel_at_mu_zero_does_not_depend_on_v_1() -> None:
    _same(module.kernel_independence((1, 1)), True)


MUTATIONS: list[Mutation] = [
    ("identity", lambda record: record["identities"].__setitem__("eigenlines_are_hermitian_orthogonal", False)),
    ("orbit rank", lambda record: record["orbit_rank_samples"]["quaternion position"].__setitem__(0, 12)),
    ("gram zero", lambda record: record["orbit_rank_samples"]["gram zero calibration"].__setitem__(0, 13)),
    ("fixtures", lambda record: record["fixture_agreement"].__setitem__("agreeing", 63)),
    ("line", lambda record: record["mu_zero_lines"][2].__setitem__(1, -1)),
    ("projection", lambda record: record["mu_zero_lines"][0].__setitem__(4, 6)),
    ("pairing", lambda record: record["first_order_pairings"][1].__setitem__("imaginary_part_is_definite", False)),
    ("witness", lambda record: record["witnesses"][0].__setitem__("fiber_dimension_of_L_z", 1)),
    ("singular values", lambda record: record["witness_singular_values"][0]["M(z)"].__setitem__(0, "9")),
    ("calibration", lambda record: record["calibrations"][0].__setitem__("fiber_dimension_of_L_z", 2)),
    ("nullities", lambda record: record["fixture_kernel_nullities"].__setitem__("agree", 65)),
    ("independence", lambda record: record["mu_zero_kernels_independent_of_v_1"].__setitem__(0, False)),
    ("claim", lambda record: record["claims"]["fiber"].__setitem__("dim_L_4_exact", True)),
    ("digest", lambda record: record["inputs"].__setitem__(next(iter(record["inputs"])), "0" * 64)),
    ("pass", lambda record: record.__setitem__("pass", False)),
    ("true as one", lambda record: record["identities"].__setitem__("real_nullity_of_a_kernel_vector", 1)),
]


def test_record_rules_accept_the_pinned_record(monkeypatch: pytest.MonkeyPatch) -> None:
    _same(module.verdict(module.expected_record()), [])
    retained = json.loads(module.RECORD.read_text(encoding="utf-8"))
    retained_inputs = dict(retained["inputs"])
    monkeypatch.setattr(module, "_inputs", lambda: dict(retained_inputs))
    _same(module.verdict(retained), [])
    _same(module.RECORD.read_text(encoding="utf-8"), module._serialized(module.expected_record()))


@pytest.mark.parametrize("mutation", MUTATIONS, ids=[name for name, _ in MUTATIONS])
def test_record_rules_reject_a_mutated_record(mutation: Mutation) -> None:
    record = copy.deepcopy(module.expected_record())
    mutation[1](record)
    _same(module.verdict(record) != [], True)


@pytest.mark.audit
def test_the_record_replays() -> None:
    _same(module.verdict(module.compute()), [])
