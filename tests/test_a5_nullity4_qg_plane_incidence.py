"""Real points of V(Q) n V(G) with an exceptional kernel plane: the incidence Jacobian and the type s = +-1."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles-residuals"))

import nullity4_qg_intersection as qg  # noqa: E402
import nullity4_qg_plane_incidence as pi  # noqa: E402
import sympy as sp  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


@pytest.mark.parametrize("job", pi.WITNESS_JOBS)
def test_incidence_jacobian_has_rank_four_at_the_witness(job: tuple[int, str]) -> None:
    _same(pi.incidence_facts(job), pi.INCIDENCE_ROW)


def test_real_rank_separates_real_and_imaginary_parts() -> None:
    # Two columns that are complex multiples of each other are independent over R; a repeated column is not.
    one = [sp.Integer(1), sp.Integer(0)]
    _same(pi._real_rank([one, [sp.I, sp.Integer(0)]]), 2)
    _same(pi._real_rank([one, one]), 1)


def test_unipotent_element_is_equivariant_and_not_unitary() -> None:
    _same(pi.unipotent_facts(), pi.UNIPOTENT_FACTS)


def test_a_sum_of_two_derivations_is_not_nilpotent(monkeypatch: pytest.MonkeyPatch) -> None:
    # Without the factor i the matrix D_a - D_b is real and skew, so no power of it vanishes.
    pi.unipotent_element.cache_clear()
    monkeypatch.setattr(pi, "IU", sp.Integer(-1))
    with pytest.raises(RuntimeError, match="not nilpotent"):
        pi.unipotent_element()
    pi.unipotent_element.cache_clear()


@pytest.mark.parametrize("job", [(s, name) for s in (1, -1) for name in pi.ELEMENTS])
def test_complements_at_s_plus_minus_one_lie_in_the_plane_x(job: tuple[int, str]) -> None:
    _same(pi.complement_facts(job), pi.COMPLEMENTS[f"s = {job[0]}, {job[1]}"])


def test_an_unknown_element_or_fact_is_refused() -> None:
    with pytest.raises(RuntimeError, match="unknown element"):
        pi.complement_fact((1, "rotation", "x"))
    with pytest.raises(RuntimeError, match="unknown fact"):
        pi.complement_fact((1, "identity", "w"))


@pytest.mark.parametrize("plane", ["y", "z"])
def test_complement_at_s_two_is_the_witness_outside_the_plane_x(plane: str) -> None:
    # At s = 2 the complement is the retained witness of qg, a point of nullity 3 outside P_x: the containment of
    # item 3 belongs to the type s = +-1.
    _same(pi.generic_complement(plane), pi.GENERIC_COMPLEMENTS[plane])
    kernel = qg.kernel_vectors(sp.Integer(2))
    w = pi._complement(kernel, list(qg.plane_vectors(sp.Integer(2))[plane]))
    _same(qg._rank([w, qg.witness_point(sp.Integer(2), plane)]), 1)


def _record() -> dict[str, Any]:
    return json.loads(pi.RECORD.read_text(encoding="utf-8"))


def test_pinned_record_passes_its_rules(monkeypatch: pytest.MonkeyPatch) -> None:
    record = _record()
    retained_inputs = dict(record["inputs"])
    monkeypatch.setattr(pi, "_inputs", lambda: dict(retained_inputs))
    _same(pi.verdict(record), [])
    _same(record["pass"], True)
    _same(pi._serialized(record), pi.RECORD.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("label", "mutate"),
    [
        ("a Jacobian rank", lambda r: r["incidence"]["s = 2, y"].__setitem__(7, 3)),
        ("a tangent dimension", lambda r: r["incidence"]["s = 0, x"].__setitem__(2, 12)),
        ("the unipotent element", lambda r: r["unipotent"].__setitem__("unitary", True)),
        ("a complement nullity", lambda r: r["complements"]["s = 1, unipotent"]["y"].__setitem__(0, 3)),
        ("a complement containment", lambda r: r["complements"]["s = -1, identity"]["z"].__setitem__(1, False)),
        ("the generic complement", lambda r: r["generic_complements"]["y"].__setitem__(1, True)),
        ("the verdict flag", lambda r: r.__setitem__("pass", False)),
    ],
)
def test_record_rules_reject_a_planted_mutant(label: str, mutate: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    record = _record()
    retained_inputs = dict(record["inputs"])
    monkeypatch.setattr(pi, "_inputs", lambda: dict(retained_inputs))
    mutate(record)
    if not pi.verdict(record):
        raise AssertionError(label)
