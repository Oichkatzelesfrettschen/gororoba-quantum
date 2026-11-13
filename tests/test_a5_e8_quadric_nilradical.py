"""The nilradical of the E8-bar quadric ideal over Q(i): five linear forms of square zero and one embedded component."""

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

import e8_quadric_nilradical as nil  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _record() -> dict[str, Any]:
    record: dict[str, Any] = json.loads(nil.RECORD.read_text(encoding="utf-8"))
    return record


def test_the_retained_record_passes_and_agrees_with_the_weight_slice_record() -> None:
    record = _record()
    _same(nil.problems(record), [])
    _same(nil.slice_problems(record), [])
    _same(record["pass"], True)
    _same([cell["orbit"] for cell in record["cells"]], ["N-", "N+"])


def test_the_degrees_of_the_primary_components_sum_to_the_multiplicity_in_top_dimension() -> None:
    """Only the 5-dimensional component enters the multiplicity 11; the embedded one doubles a prime of degree 2."""
    components = nil.EXPECTED["primary_components"]
    top = max(component[0] for component in components)
    _same(sum(component[2] for component in components if component[0] == top), nil.EXPECTED["ideal"][1])
    embedded = [component for component in components if not component[3]]
    _same(embedded, [[4, 2, 4, False]])
    _same(sorted(component[:2] for component in components if component[3]), nil.EXPECTED["minimal_primes"])


def test_the_linear_forms_at_the_two_basepoints_are_conjugate() -> None:
    minus, plus = (cell["linear_forms"] for cell in _record()["cells"])
    _same(sorted(form.replace("(-i)", "(i)") for form in plus), sorted(minus))
    _same(sum("i" in form for form in minus), 1)


def _set(orbit: str, key: str, value: object) -> Callable[[dict[str, Any]], None]:
    def mutate(record: dict[str, Any]) -> None:
        next(cell for cell in record["cells"] if cell["orbit"] == orbit)[key] = value

    return mutate


MUTATIONS: dict[str, tuple[Callable[[dict[str, Any]], None], str]] = {
    "four linear forms": (_set("N-", "radical_linear_forms", 4), "radical_linear_forms"),
    "a linear form dropped": (_set("N+", "linear_forms", ["y(3)"]), "differ in number"),
    "radical larger": (_set("N-", "radical_is_ideal_plus_linear_forms", False), "radical_is_ideal_plus"),
    "square not zero": (_set("N+", "radical_square_in_ideal", False), "radical_square_in_ideal"),
    "annihilator changed": (_set("N-", "annihilator", [5, 2]), "annihilator differs"),
    "embedded component radical": (
        _set("N+", "primary_components", [[4, 2, 2, True], [4, 4, 4, True], [5, 11, 11, True]]),
        "primary_components",
    ),
    "minimal primes changed": (_set("N-", "minimal_primes", [[5, 11]]), "minimal_primes"),
    "a cell removed": (lambda record: record["cells"].pop(), "N- and N+"),
    "pass flag cleared": (lambda record: record.update({"pass": False}), "pass flag"),
    "schema changed": (lambda record: record.update(schema="gororoba.a5.e8-quadric-nilradical/0"), "schema"),
    "field changed": (lambda record: record.update(field="Q"), "field"),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_the_checker_rejects_each_mutation_of_the_retained_record(name: str) -> None:
    mutate, fragment = MUTATIONS[name]
    record = copy.deepcopy(_record())
    mutate(record)
    found = nil.problems(record)
    if not any(fragment in problem for problem in found):
        raise AssertionError((name, found))


def test_the_slice_comparison_rejects_other_relations() -> None:
    record = copy.deepcopy(_record())
    record["cells"][0]["relations_sha256"] = "0" * 64
    _same(nil.slice_problems(record), ["N-: the relations differ from those of the weight-slice record"])


def test_the_retained_record_binds_the_current_input_digests() -> None:
    record = _record()
    _same(sorted(record["inputs"]), sorted(nil.INPUTS))
    for name in nil.INPUTS:
        _same(record["inputs"][name], hashlib.sha256((ATTACH / name).read_bytes()).hexdigest())
    _same(record["weight_slice_record_sha256"], hashlib.sha256(nil.WEIGHT_SLICE.read_bytes()).hexdigest())
