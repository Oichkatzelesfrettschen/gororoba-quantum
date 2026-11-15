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


def test_the_retained_record_passes_its_checker() -> None:
    record = _record()
    _same(geometry.problems(record), [])
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


def test_the_main_prime_is_no_cone_and_its_tangent_cones_have_multiplicity_four_two_and_one() -> None:
    for cell in _record()["cells"]:
        _same(cell["main_vertex_space"], 0)
        # At a point of the singular line, of the singular plane and of the meeting of the components.
        _same(cell["tangent_cones"], [[1, 5, 4], [2, 5, 2], [3, 5, 1]])


def test_the_meeting_of_the_components_is_a_ruling_plane_of_the_scroll() -> None:
    record = _record()
    for cell in record["cells"]:
        _same(cell["scroll_is_linear_forms_plus_matrix_minors"], True)
        _same(cell["scroll_rows_proportional_on_meeting"], True)
    _same(_cell(record, "N-")["scroll_row_ratio_on_meeting"], "(-i)")
    _same(_cell(record, "N+")["scroll_row_ratio_on_meeting"], "(i)")


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


def _walk(orbit: str, index: int, value: list[int]) -> Mutation:
    def mutate(record: dict[str, Any]) -> None:
        _cell(record, orbit)["walk"][index] = value

    return mutate


def _one_bound_component(record: dict[str, Any]) -> None:
    """One component in place of eight, with every aggregate count adjusted to agree with it."""
    cell = _cell(record, "N-")
    cell["bound_component_dimensions"] = [[3, 1, 2]]
    cell["bound_components"] = 1
    cell["bound_components_with_smooth_points"] = 1


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
    "a bound component of degree two": (_bound("N-", 7, [3, 2, 2]), "bound_component_dimensions"),
    "all bound components replaced consistently": (_one_bound_component, "bound_component_dimensions"),
    "kept-minor count of a walk changed": (_walk("N-", 1, [2, 435600, 1600, 3, 4]), "walk differs"),
    "tried-minor count of a walk changed": (_walk("N+", 0, [1, 0, 1394, 3, 13]), "walk differs"),
    "terminal bound of a walk changed": (_walk("N-", 1, [2, 435600, 1657, 4, 2]), "walk differs"),
    "bound components removed": (
        lambda record: _cell(record, "N-").pop("bound_component_dimensions"),
        "outer bound are missing",
    ),
    "second walk removed": (lambda record: _cell(record, "N-")["walk"].pop(), "minor walks"),
    "a vertex line on the main prime": (_set("N-", "main_vertex_space", 1), "main_vertex_space"),
    "scroll matrix lost": (
        _set("N+", "scroll_is_linear_forms_plus_matrix_minors", False),
        "scroll_is_linear_forms_plus_matrix_minors",
    ),
    "scroll rows independent on the meeting": (
        _set("N-", "scroll_rows_proportional_on_meeting", False),
        "scroll_rows_proportional_on_meeting",
    ),
    "conjugate row ratio": (_set("N-", "scroll_row_ratio_on_meeting", "(i)"), "ratio of the scroll matrix rows"),
    "multiplicity at the isolated point changed": (
        _set("N-", "tangent_cones", [[1, 5, 3], [2, 5, 2], [3, 5, 1]]),
        "tangent_cones",
    ),
    "a singular point of the meeting": (
        _set("N+", "tangent_cones", [[1, 5, 4], [2, 5, 2], [3, 5, 2]]),
        "tangent_cones",
    ),
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


def test_the_slice_comparison_reads_the_e8_cells_over_qi_and_rejects_other_relations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A constructed weight-slice record: the comparison reads only the E8-bar cells of characteristic 0.
    cells = [
        {"orbit": "N-", "characteristic": 0, "source": "e8", "relations_sha256": "a" * 64},
        {"orbit": "N+", "characteristic": 0, "source": "e8", "relations_sha256": "b" * 64},
        {"orbit": "N-", "characteristic": 32009, "source": "e8", "relations_sha256": "c" * 64},
        {"orbit": "N-", "characteristic": 0, "source": "iso", "relations_sha256": "d" * 64},
    ]
    fixture = tmp_path / "weight-slice.json"
    fixture.write_text(json.dumps({"cells": cells}), encoding="utf-8")
    monkeypatch.setattr(geometry, "WEIGHT_SLICE", fixture)
    record = {"cells": [{"orbit": "N-", "relations_sha256": "a" * 64}, {"orbit": "N+", "relations_sha256": "b" * 64}]}
    _same(geometry.slice_problems(record), [])
    record["cells"][0]["relations_sha256"] = "c" * 64
    _same(geometry.slice_problems(record), ["N-: the relations differ from those of the weight-slice record"])
    record["cells"].append({"orbit": "W8", "relations_sha256": "a" * 64})
    _same(len(geometry.slice_problems(record)), 2)


def test_the_stored_record_check_rejects_a_missing_input_table() -> None:
    record = copy.deepcopy(_record())
    record["inputs"] = None
    found = geometry.check_problems(record)
    _same(sum("input digest" in problem for problem in found), len(geometry.INPUTS))


def _join(numbers: list[int]) -> str:
    return ",".join(str(int(number)) for number in numbers)


def _singular_values(orbit: str) -> dict[str, list[str]]:
    """The RESULT lines of a run that finds the expected cell, in an order and form the producer must normalize."""
    expected = geometry.EXPECTED
    line, plane = geometry.SINGULAR_GENERATORS[orbit]
    values = {key: [str(expected[key])] for key in ("minimal_primes", "embedded_linear_forms", "bound_components")}
    for key in (
        "embedded_quadric_rank",
        "scroll_singular_locus",
        "main_linear_forms",
        "main_free_variables",
        "main_codimension",
        "bound_components_with_smooth_points",
        "main_vertex_space",
    ):
        values[key] = [str(expected[key])]
    for key in (
        "scroll_prime",
        "main_prime",
        "embedded_prime",
        "scroll_meets_main",
        "scroll_meets_embedded",
        "embedded_vertex",
        "smooth_rank",
        "singular_locus",
        "main_residual_generator_degrees",
    ):
        values[key] = [_join(expected[key])]
    for key in (
        "embedded_contains_main",
        "embedded_contains_scroll",
        "scroll_meets_main_is_linear",
        "scroll_meets_main_contains_embedded",
        "scroll_meets_embedded_equals_scroll_meets_main",
        "scroll_is_linear_forms_plus_matrix_minors",
        "scroll_rows_proportional_on_meeting",
    ):
        values[key] = [str(int(expected[key]))]
    # Singular prints the degrees in generator order, the Hilbert numerator with a trailing marker entry, and the
    # components, walks excepted, in the order its decomposition returns them: here the reverse of the sorted one.
    values["scroll_generator_degrees"] = [_join(list(reversed(expected["scroll_generator_degrees"])))]
    values["main_hilbert_second"] = [_join([*expected["main_hilbert_second"], 1])]
    values["scroll_betti"] = [";".join(_join(row) for row in expected["scroll_betti"])]
    values["main_betti"] = [";".join(_join(row) for row in expected["main_betti"])]
    values["walk"] = [_join(row) for row in expected["walk"]]
    values["bound_component"] = [_join(row) for row in reversed(expected["bound_component_dimensions"])]
    values["singular_component"] = [_join(row) for row in reversed(expected["singular_components"])]
    values["singular_generators"] = [f"2 {plane}", f"1 {line}"]
    values["tangent_cone"] = [_join(row) for row in reversed(expected["tangent_cones"])]
    values["scroll_row_ratio_on_meeting"] = [geometry.SCROLL_ROW_RATIO[orbit]]
    values["done"] = ["1"]
    return values


def _mock_singular(monkeypatch: pytest.MonkeyPatch, values: dict[str, dict[str, list[str]]]) -> list[str]:
    """Replace both Singular stages of `certify`; the returned list receives the second script of every call."""
    scripts: list[str] = []

    def run_singular(script: str) -> dict[str, Any]:
        if script.startswith("relations of "):
            return {"values": {"orbit": [script.removeprefix("relations of ")]}, "relations": [RELATION_LINE]}
        scripts.append(script)
        orbit = "N-" if len(scripts) % 2 == 1 else "N+"
        return {"values": values[orbit], "relations": []}

    monkeypatch.setattr(geometry.ws, "orbit_task", lambda orbit: orbit)
    monkeypatch.setattr(geometry.ws, "fiber_script", lambda task, source, prime, root: f"relations of {task}")
    monkeypatch.setattr(geometry.ws, "run_singular", run_singular)
    monkeypatch.setattr(
        geometry.ws, "summarize_fiber_run", lambda run: {"relations_sha256": run["values"]["orbit"][0] * 32}
    )
    return scripts


RELATION_LINE = "RELATION 1,2:1 3,3:(i)"


def test_certify_normalizes_the_order_and_form_of_the_singular_output(monkeypatch: pytest.MonkeyPatch) -> None:
    scripts = _mock_singular(monkeypatch, {orbit: _singular_values(orbit) for orbit in geometry.ORBITS})
    cells = [geometry.certify(orbit) for orbit in geometry.ORBITS]
    for orbit, cell in zip(geometry.ORBITS, cells, strict=True):
        for key, expected in geometry.EXPECTED.items():
            _same(json.dumps(cell[key]), json.dumps(expected))
        _same(cell["singular_generators"], list(geometry.SINGULAR_GENERATORS[orbit]))
        _same(cell["relations_sha256"], orbit * 32)
    _same(geometry.problems({"schema": geometry.SCHEMA, "field": "Q(i)", "cells": cells, "pass": True}), [])
    # The second stage holds the relation as a polynomial over Q(i) and computes in global orderings only.
    for script in scripts:
        _same(script.startswith("ring r=(0,i),(y(1..21)),(dp); minpoly=i^2+1;"), True)
        _same("ideal K=(1)*y(1)*y(2)+((i))*y(3)*y(3);" in script, True)
        _same([ordering for ordering in ("),ds;", ",(ds);", "tangentcone(") if ordering in script], [])
        _same("sat(tr(P11),h)" in script, True)


@pytest.mark.parametrize(
    ("key", "lines", "problem"),
    [
        ("scroll_meets_main_is_linear", ["0"], "scroll_meets_main_is_linear differs"),
        ("embedded_contains_scroll", ["1"], "embedded_contains_scroll differs"),
        ("main_hilbert_second", ["1,7,3"], "main_hilbert_second differs"),
        ("tangent_cone", ["1,5,4", "2,5,2", "3,5,2"], "tangent_cones differs"),
        ("singular_component", ["1,1,4,4,1,1,1,0", "2,1,6,6,1,1,1,0"], "singular_components differs"),
        ("singular_generators", ["1 y(1)", "2 y(2)"], "the generators of the singular components differ"),
    ],
)
def test_certify_carries_a_changed_singular_result_into_a_cell_the_checker_rejects(
    monkeypatch: pytest.MonkeyPatch, key: str, lines: list[str], problem: str
) -> None:
    values = {orbit: _singular_values(orbit) for orbit in geometry.ORBITS}
    values["N-"][key] = lines
    _mock_singular(monkeypatch, values)
    cells = [geometry.certify(orbit) for orbit in geometry.ORBITS]
    found = geometry.problems({"schema": geometry.SCHEMA, "field": "Q(i)", "cells": cells, "pass": True})
    _same([text for text in found if problem in text and text.startswith("N-")] != [], True)
    _same([text for text in found if text.startswith("N+")], [])


@pytest.mark.audit
def test_the_retained_record_binds_the_current_input_digests() -> None:
    record = _record()
    _same(geometry.check_problems(record), [])
    _same(sorted(record["inputs"]), sorted(geometry.INPUTS))
    for name in geometry.INPUTS:
        _same(record["inputs"][name], hashlib.sha256((ATTACH / name).read_bytes()).hexdigest())
    _same(record["weight_slice_record_sha256"], hashlib.sha256(geometry.WEIGHT_SLICE.read_bytes()).hexdigest())
