"""The associated primes of the E8-bar quadric ideal over Q(i): their intersections and the singular locus of each."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
ATTACH = ROOT / "docs" / "evidence" / "a5-kernel-attachments"
sys.path.insert(0, str(ATTACH))

import e8_component_geometry as geometry  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _record() -> dict[str, Any]:
    record: dict[str, Any] = json.loads(geometry.RECORD.read_text(encoding="utf-8"))
    return record


def _cell(record: dict[str, Any], orbit: str) -> dict[str, Any]:
    cell: dict[str, Any] = next(cell for cell in record["cells"] if cell["orbit"] == orbit)
    return cell


def test_the_retained_record_passes_and_agrees_with_the_weight_slice_record() -> None:
    record = _record()
    _same(geometry.problems(record), [])
    _same(geometry.slice_problems(record), [])
    _same(record["pass"], True)
    _same([cell["orbit"] for cell in record["cells"]], ["N-", "N+"])


def test_the_singular_locus_is_a_plane_and_a_line_inside_the_meeting_of_the_two_minimal_primes() -> None:
    for cell in _record()["cells"]:
        line, plane = cell["singular_components"]
        _same(line[:2], [1, 1])
        _same(plane[:2], [2, 1])
        # The Jacobian has rank 7 at a smooth point of the main prime: rank 4 along the line, 6 along the plane.
        _same([line[2:4], plane[2:4], cell["smooth_rank"]], [[4, 4], [6, 6], [7, 7]])
        # Both lie in the main prime, in the sum of the two minimal primes and in the embedded prime.
        _same([line[4:7], plane[4:7]], [[True, True, True], [True, True, True]])
        # The line is the vertex of the embedded quadric cone; the plane is not.
        _same([line[7], plane[7]], [True, False])
        _same(cell["singular_locus"], [2, 1])


def test_the_two_basepoints_carry_conjugate_singular_components() -> None:
    record = _record()
    minus = _cell(record, "N-")["singular_generators"]
    plus = _cell(record, "N+")["singular_generators"]
    _same([text.replace("(-i)", "(i)") for text in plus], minus)
    _same(minus, list(geometry.SINGULAR_GENERATORS["N-"]))
    _same(plus, list(geometry.SINGULAR_GENERATORS["N+"]))


def test_the_derived_properties_follow_the_betti_table_and_the_singular_locus() -> None:
    cell = copy.deepcopy(_cell(_record(), "N-"))
    _same(
        geometry.derived(cell),
        {"main_is_cohen_macaulay": True, "main_is_gorenstein": False, "main_is_normal": True},
    )
    # A singular locus of codimension one would end normality and leave the depth statement alone.
    cell["singular_locus"] = [4, 1]
    _same(geometry.derived(cell)["main_is_normal"], False)
    _same(geometry.derived(cell)["main_is_cohen_macaulay"], True)
    # A longer resolution ends the Cohen-Macaulay property and with it the other two.
    cell = copy.deepcopy(_cell(_record(), "N-"))
    cell["main_betti"] = [[*row, 0] for row in cell["main_betti"]]
    cell["main_betti"][2][-1] = 1
    _same(
        geometry.derived(cell),
        {"main_is_cohen_macaulay": False, "main_is_gorenstein": False, "main_is_normal": False},
    )
    # A last module of rank one would make a Cohen-Macaulay quotient Gorenstein.
    cell = copy.deepcopy(_cell(_record(), "N-"))
    cell["main_betti"][2][-1] = 1
    _same(geometry.derived(cell)["main_is_gorenstein"], True)


def test_every_component_of_the_outer_bound_holds_a_smooth_point() -> None:
    for cell in _record()["cells"]:
        parts = cell["bound_component_dimensions"]
        _same(len(parts), cell["bound_components"])
        _same(all(singular < dimension for dimension, _degree, singular in parts), True)
        _same(max(singular for _dimension, _degree, singular in parts), cell["singular_locus"][0])
        _same([row[0] for row in cell["walk"]], [1, 2])


Mutation = Callable[[dict[str, Any]], Any]


def _set(orbit: str, key: str, value: object) -> Mutation:
    def mutate(record: dict[str, Any]) -> None:
        _cell(record, orbit)[key] = value

    return mutate


def _component(orbit: str, index: int, position: int, value: object) -> Mutation:
    def mutate(record: dict[str, Any]) -> None:
        _cell(record, orbit)["singular_components"][index][position] = value

    return mutate


def _bound(orbit: str, index: int, value: list[int]) -> Mutation:
    def mutate(record: dict[str, Any]) -> None:
        _cell(record, orbit)["bound_component_dimensions"][index] = value

    return mutate


def _swap_generators(record: dict[str, Any]) -> None:
    cell = _cell(record, "N-")
    cell["singular_generators"] = cell["singular_generators"][::-1]


def _repeat_generator(record: dict[str, Any]) -> None:
    cell = _cell(record, "N+")
    cell["singular_generators"] = [cell["singular_generators"][0]] * 2


MUTATIONS: dict[str, tuple[Mutation, str]] = {
    "main prime degree changed": (_set("N-", "main_prime", [5, 12]), "main_prime"),
    "scroll prime dimension changed": (_set("N+", "scroll_prime", [5, 4]), "scroll_prime"),
    "embedded prime contains the scroll": (_set("N-", "embedded_contains_scroll", True), "embedded_contains_scroll"),
    "embedded prime leaves the main prime": (_set("N+", "embedded_contains_main", False), "embedded_contains_main"),
    "meeting of the minimal primes not linear": (
        _set("N-", "scroll_meets_main_is_linear", False),
        "scroll_meets_main_is_linear",
    ),
    "meeting of the minimal primes enlarged": (_set("N-", "scroll_meets_main", [4, 1]), "scroll_meets_main"),
    "embedded quadric of full rank": (_set("N-", "embedded_quadric_rank", 5), "embedded_quadric_rank"),
    "embedded vertex a point": (_set("N+", "embedded_vertex", [0, 1]), "embedded_vertex"),
    "scroll with a singular line": (_set("N-", "scroll_singular_locus", 1), "scroll_singular_locus"),
    "scroll betti entry changed": (_set("N-", "scroll_betti", [[1, 0, 0, 0], [0, 6, 8, 2]]), "scroll_betti"),
    "main hilbert numerator changed": (_set("N+", "main_hilbert_second", [1, 7, 4]), "main_hilbert_second"),
    "main betti table lengthened": (
        _set("N-", "main_betti", [[1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 25, 91, 147, 119, 35, 6, 0, 0], [0] * 8 + [1]]),
        "main_betti",
    ),
    "main codimension changed": (_set("N-", "main_codimension", 8), "main_codimension"),
    "smooth rank lowered": (_set("N-", "smooth_rank", [6, 7]), "smooth_rank"),
    "singular locus of codimension one": (_set("N-", "singular_locus", [4, 1]), "singular_locus"),
    "singular plane dropped": (
        lambda record: _cell(record, "N-")["singular_components"].pop(),
        "singular_components",
    ),
    "rank on the plane raised to the smooth rank": (_component("N-", 1, 2, 7), "singular_components"),
    "rank bounds on the line apart": (_component("N+", 0, 3, 5), "singular_components"),
    "line outside the embedded prime": (_component("N-", 0, 6, False), "singular_components"),
    "plane named the vertex": (_component("N-", 1, 7, True), "singular_components"),
    "flag written as an integer": (_component("N-", 0, 4, 1), "singular_components"),
    "generators of the two components swapped": (_swap_generators, "generators of the singular components"),
    "one generator list repeated": (_repeat_generator, "generators of the singular components"),
    "conjugate generators at the other basepoint": (
        _set("N-", "singular_generators", list(geometry.SINGULAR_GENERATORS["N+"])),
        "generators of the singular components",
    ),
    "a bound component inside the singular locus": (_bound("N-", 0, [2, 1, 2]), "inside the singular locus"),
    "bound component count changed": (_set("N-", "bound_components", 1), "differs from its count"),
    "smooth-point count changed": (
        _set("N+", "bound_components_with_smooth_points", 0),
        "bound components with smooth points",
    ),
    "bound components removed": (
        lambda record: _cell(record, "N-").pop("bound_component_dimensions"),
        "outer bound are missing",
    ),
    "second walk removed": (lambda record: _cell(record, "N-")["walk"].pop(), "minor walks"),
    "normal flag cleared": (_set("N-", "main_is_normal", False), "main_is_normal"),
    "gorenstein flag set": (_set("N+", "main_is_gorenstein", True), "main_is_gorenstein"),
    "cohen-macaulay flag cleared": (_set("N-", "main_is_cohen_macaulay", False), "main_is_cohen_macaulay"),
    "a cell removed": (lambda record: record["cells"].pop(), "N- and N+"),
    "pass flag cleared": (lambda record: record.update({"pass": False}), "pass flag"),
    "schema changed": (lambda record: record.update(schema="gororoba.a5.e8-component-geometry/0"), "schema"),
    "field changed": (lambda record: record.update(field="Q"), "field"),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_the_checker_rejects_each_mutation_of_the_retained_record(name: str) -> None:
    mutate, fragment = MUTATIONS[name]
    record = copy.deepcopy(_record())
    mutate(record)
    found = geometry.problems(record)
    if not any(fragment in problem for problem in found):
        raise AssertionError((name, found))


def test_the_slice_comparison_rejects_other_relations() -> None:
    record = copy.deepcopy(_record())
    record["cells"][0]["relations_sha256"] = "0" * 64
    _same(geometry.slice_problems(record), ["N-: the relations differ from those of the weight-slice record"])


def test_the_stored_record_check_rejects_a_missing_input_table() -> None:
    record = copy.deepcopy(_record())
    record["inputs"] = None
    found = geometry.check_problems(record)
    _same(sum("input digest" in problem for problem in found), len(geometry.INPUTS))


@pytest.mark.audit
def test_the_retained_record_binds_the_current_input_digests() -> None:
    record = _record()
    _same(geometry.check_problems(record), [])
    _same(sorted(record["inputs"]), sorted(geometry.INPUTS))
    for name in geometry.INPUTS:
        _same(record["inputs"][name], hashlib.sha256((ATTACH / name).read_bytes()).hexdigest())
    _same(record["weight_slice_record_sha256"], hashlib.sha256(geometry.WEIGHT_SLICE.read_bytes()).hexdigest())
