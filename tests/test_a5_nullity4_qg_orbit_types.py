"""The orbit types of the nullity-4 points of V(Q) n V(G): the type s = +-1, the point (i, 0), dim C(P) = 5."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles-residuals"))

import nullity4_qg_intersection as qg  # noqa: E402
import nullity4_qg_orbit_types as ot  # noqa: E402
import sympy as sp  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


@pytest.mark.parametrize("name", ot.IDENTITIES)
def test_exact_identity_holds(name: str) -> None:
    _same(ot.identity(name), True)


@pytest.mark.parametrize("s", [1, -1])
def test_type_s_plus_minus_one_has_its_plane_in_an_eigenline(s: int) -> None:
    _same(ot.eigenline_facts(s), ot.EIGENLINE_FACTS[str(s)])


def test_the_plane_x_is_in_no_eigenline_at_s_two() -> None:
    # At s = 2 the plane P_x is not inside E_+ or E_-, so the invariant of the type s = +-1 is absent.
    k0, k1, k2 = qg.kernel_vectors(sp.Integer(2))
    _same([ot._in_eigenline(k1, eps) or ot._in_eigenline(k2, eps) for eps in (1, -1)], [False, False])


def test_a_skew_matrix_that_mixes_the_blocks_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    # A skew coupling between u and v added to the first derivation leaves the matrix skew; it is no longer
    # equivariant and no longer maps E_eps into itself, so the check rejects it for those reasons alone.
    matrices = list(ot.derivation_matrices())
    bad = matrices[0].copy()
    bad[0, 9] += 1
    bad[9, 0] -= 1
    _same(bad + bad.T, sp.zeros(15, 15))
    monkeypatch.setattr(ot, "derivation_matrices", lambda: tuple([bad, *matrices[1:]]))
    _same(ot.derivations_preserve_the_eigenlines(), False)


def test_sigma_zero_facts() -> None:
    _same(ot.sigma_facts(), ot.SIGMA_FACTS)
    _same(ot.sigma_pfaffian(), ot.SIGMA_PFAFFIAN)
    _same(ot.sigma_orbit_ranks(), ot.SIGMA_ORBIT_RANKS)


@pytest.mark.parametrize("plane", ["x", "y", "z"])
def test_sigma_witness_has_the_pinned_facts(plane: str) -> None:
    found_plane, row, point = ot.sigma_witness(plane)
    _same(found_plane, plane)
    _same(row, ot.SIGMA_WITNESSES[plane])
    _same(point, ot.SIGMA_POINTS[plane])


def test_sigma_zero_has_the_computed_facts_of_the_chart_point_s_zero() -> None:
    # The docstring argues that s and 1 / s are one orbit type. This compares the two computations, not the two
    # pinned tables: dim C of the three planes at sigma = 0 and at s = 0, and the fiber dimension at each witness.
    _same(ot.sigma_facts()[2], qg.special_facts(0)[:3])
    _same([ot.sigma_witness(p)[1][4] for p in "xyz"], [qg.witness_facts((0, p))[1][4] for p in "xyz"])


def test_dimension_table_is_derived_from_the_minors() -> None:
    minors = {plane: dict(ot.STACK_MINORS[plane]) for plane in "xyz"}
    sigma: Any = ot.SIGMA_FACTS[2]
    table = ot.dimension_table(minors, ot.SPECIAL_DIMENSIONS, sigma, True)
    _same(table, ot.DIMENSION_TABLE)
    minors["x"]["factors"] = [*minors["x"]["factors"], ["s - 2", 1]]
    _same(ot.dimension_table(minors, ot.SPECIAL_DIMENSIONS, sigma, True), {"inconsistent": []})


@pytest.mark.audit
def test_pencil_on_the_plane_x_has_nullity_seven() -> None:
    _same(ot.sigma_line_x(), ot.SIGMA_LINE_X)


def test_stack_minor_of_the_plane_x_vanishes_only_at_zero_and_plus_minus_one() -> None:
    _same(ot.stack_minor("x"), ot.STACK_MINORS["x"])


@pytest.mark.audit
@pytest.mark.parametrize("plane", ["y", "z"])
def test_stack_minor_of_the_planes_y_and_z(plane: str) -> None:
    _same(ot.stack_minor(plane), ot.STACK_MINORS[plane])


def test_special_dimensions() -> None:
    _same(ot.special_dimensions(), ot.SPECIAL_DIMENSIONS)


def _record() -> dict[str, Any]:
    return json.loads(ot.RECORD.read_text(encoding="utf-8"))


def test_pinned_record_passes_its_rules(monkeypatch: pytest.MonkeyPatch) -> None:
    record = _record()
    retained_inputs = dict(record["inputs"])
    monkeypatch.setattr(ot, "_inputs", lambda: dict(retained_inputs))
    _same(ot.verdict(record), [])
    _same(record["pass"], True)
    _same(ot._serialized(record), ot.RECORD.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("label", "mutate"),
    [
        ("an eigenline fact", lambda r: r["eigenlines"]["1"].__setitem__(4, 9)),
        ("a sigma witness", lambda r: r["sigma_witnesses"]["x"].__setitem__(4, 4)),
        ("a witness point", lambda r: r["sigma_points"]["y"].__setitem__(0, "0")),
        ("a minor factor", lambda r: r["stack_minors"]["x"]["factors"][1].__setitem__(1, 2)),
        ("an identity", lambda r: r["identities"].__setitem__("plane_coincidence", False)),
        ("the pencil", lambda r: r["sigma_line_x"].__setitem__("rank", 9)),
        ("the dimension table", lambda r: r["dimension_table"].__setitem__("sigma = 0", [5, 4, 5])),
        ("the verdict flag", lambda r: r.__setitem__("pass", False)),
    ],
)
def test_record_rules_reject_a_planted_mutant(label: str, mutate: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    record = _record()
    retained_inputs = dict(record["inputs"])
    monkeypatch.setattr(ot, "_inputs", lambda: dict(retained_inputs))
    mutate(record)
    if not ot.verdict(record):
        raise AssertionError(label)
