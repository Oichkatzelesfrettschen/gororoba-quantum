"""The two minimal primes of the W8 quadric ideal over Q(i) as linear images of two parametrized models."""

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

import w8_component_models as models  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _record() -> dict[str, Any]:
    record: dict[str, Any] = json.loads(models.RECORD.read_text(encoding="utf-8"))
    return record


def test_the_retained_record_passes_and_agrees_with_the_weight_slice_record() -> None:
    record = _record()
    _same(models.problems(record), [])
    _same(models.slice_problems(record), [])
    _same(record["pass"], True)
    _same([cell["orbit"] for cell in record["cells"]], ["N-", "N+"])


def test_the_degrees_of_the_two_images_sum_to_the_degree_of_the_quadric_ideal() -> None:
    expected = models.EXPECTED
    _same(expected["image20"][1] + expected["image30"][1], expected["ideal"][1])
    _same({expected["image20"][0], expected["image30"][0]}, {expected["ideal"][0]})


def test_each_change_of_coordinates_names_every_generator() -> None:
    """The model coordinates and the linear forms of each component involve all 24 generators between them."""
    for table, linear in ((models.MAP20, models.LINEAR20), (models.MAP30, models.LINEAR30)):
        indices = {index for form in (*table, *linear) for _, index in form}
        _same(indices <= set(range(1, models.GENERATORS + 1)), True)
    _same(len(models.MAP20), len(models.MODEL20_COORDINATES))
    _same(len(models.MAP30), len(models.MODEL30_COORDINATES))
    # The degree-20 map sends w12 and w34 to opposite forms, the section w12 + w34 = 0.
    w12 = models.MAP20[models.MODEL20_COORDINATES.index("w12")]
    w34 = models.MAP20[models.MODEL20_COORDINATES.index("w34")]
    _same(tuple(((-real, -imaginary), index) for (real, imaginary), index in w12), w34)
    _same(len(models.MAP20) - 1 + len(models.LINEAR20), models.GENERATORS)
    _same(len(models.MAP30) + len(models.LINEAR30), models.GENERATORS)


def test_the_maps_at_the_two_basepoints_are_complex_conjugates() -> None:
    for table in (models.MAP20, models.LINEAR20, models.MAP30, models.LINEAR30):
        plus = models.forms_at("N+", table)
        _same(tuple(models.conjugate(form) for form in plus), table)
        _same(models.forms_at("N-", table), table)
    _same(models.render((((0, -2), 18),)), "(0-2*i)*y(18)")
    _same(models.render(models.conjugate((((1, 0), 8), ((0, 1), 17)))), "(1+0*i)*y(8)+(0-1*i)*y(17)")
    with pytest.raises(ValueError):
        models.forms_at("N", models.MAP20)


def test_each_control_alters_exactly_one_form() -> None:
    tables = {20: models.MAP20, 30: models.MAP30}
    for degree, position, replacement in models.CONTROLS.values():
        if tables[degree][position] == replacement:
            raise AssertionError((degree, position))
    script = models.control_script("N-")
    _same(script.count("RESULT control"), len(models.CONTROLS))


def _set(orbit: str, key: str, value: object) -> Callable[[dict[str, Any]], None]:
    def mutate(record: dict[str, Any]) -> None:
        next(cell for cell in record["cells"] if cell["orbit"] == orbit)[key] = value

    return mutate


def _conjugated_map(record: dict[str, Any]) -> None:
    record["cells"][1]["map30"] = record["cells"][0]["map30"]


MUTATIONS: dict[str, tuple[Callable[[dict[str, Any]], None], str]] = {
    "quadric ideal not in the intersection": (_set("N-", "ideal_in_intersection", False), "ideal_in_intersection"),
    "intersection larger than the quadric ideal": (_set("N+", "intersection_in_ideal", False), "intersection_in"),
    "one image inside the other": (_set("N-", "image20_in_image30", True), "image20_in_image30"),
    "degree of an image changed": (_set("N+", "image30", [6, 31]), "image30 differs"),
    "dimension of a model changed": (_set("N-", "model20", [5, 20, 37]), "model20 differs"),
    "rank of the coordinates dropped": (_set("N-", "coordinate_rank30", 23), "coordinate_rank30"),
    "a control accepted": (_set("N+", "controls_rejected", sorted(models.CONTROLS)[1:]), "controls_rejected"),
    "the N- map recorded at N+": (_conjugated_map, "map30 differs"),
    "a linear form dropped": (_set("N-", "linear_forms20", ["(1+0*i)*y(24)"]), "linear_forms20 differs"),
    "a cell removed": (lambda record: record["cells"].pop(), "N- and N+"),
    "pass flag cleared": (lambda record: record.update({"pass": False}), "pass flag"),
    "schema changed": (lambda record: record.update(schema="gororoba.a5.w8-component-models/0"), "schema"),
    "field changed": (lambda record: record.update(field="Q"), "field"),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_the_checker_rejects_each_mutation_of_the_retained_record(name: str) -> None:
    mutate, fragment = MUTATIONS[name]
    record = copy.deepcopy(_record())
    mutate(record)
    found = models.problems(record)
    if not any(fragment in problem for problem in found):
        raise AssertionError((name, found))


def test_the_slice_comparison_rejects_other_relations() -> None:
    record = copy.deepcopy(_record())
    record["cells"][0]["relations_sha256"] = "0" * 64
    _same(models.slice_problems(record), ["N-: the relations differ from those of the weight-slice record"])


def test_the_retained_record_binds_the_current_input_digests() -> None:
    record = _record()
    _same(sorted(record["inputs"]), sorted(models.INPUTS))
    for name in models.INPUTS:
        _same(record["inputs"][name], hashlib.sha256((ATTACH / name).read_bytes()).hexdigest())
    _same(record["weight_slice_record_sha256"], hashlib.sha256(models.WEIGHT_SLICE.read_bytes()).hexdigest())
