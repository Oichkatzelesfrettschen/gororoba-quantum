"""The two arc families that place one family of limits in each component of the W8 quadric locus over Q(i)."""

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
TRANSFER = ROOT / "docs" / "evidence" / "a5-char0-transfer"
WEIGHT_SLICE = ROOT / "docs" / "evidence" / "a5-kernel-attachments" / "weight-slice-fiber-relations-result.json"
sys.path.insert(0, str(TRANSFER))

import w8_component_arcs_qi as arcs  # noqa: E402

VARIABLES = [f"t{index}" for index in range(1, 10)]


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _record() -> dict[str, Any]:
    record: dict[str, Any] = json.loads(arcs.RECORD.read_text(encoding="utf-8"))
    return record


def _row(record: dict[str, Any], slug: str, family: str, control: bool = False) -> dict[str, Any]:
    row: dict[str, Any] = next(
        r for r in record["rows"] if (r["slug"], r["family"], r["control"]) == (slug, family, control)
    )
    return row


def test_the_retained_record_passes_and_holds_order_rank_and_span_of_each_family() -> None:
    record = _record()
    _same(arcs.problems(record), [])
    _same(record["pass"], True)
    for slug in ("w8-nm", "w8-np"):
        linear, series = _row(record, slug, "linear"), _row(record, slug, "series")
        _same((linear["order_of_G"], linear["ranks"], linear["span_of_limits"]), (2, [6, 6], 15))
        _same((series["order_of_G"], series["ranks"], series["span_of_limits"]), (4, [6, 6], 20))
        _same((linear["j_nonzero"], linear["j_is_identity"], series["j_nonzero"]), (0, True, 0))
        _same(_row(record, slug, "linear", True)["j_is_identity"], False)


def test_the_component_table_is_the_minimal_primes_of_every_w8_cell_of_the_weight_slice_record() -> None:
    cells = [cell for cell in json.loads(WEIGHT_SLICE.read_text(encoding="utf-8"))["cells"] if cell["source"] == "w8"]
    _same(len(cells), 3)
    for cell in cells:
        _same(tuple(tuple(prime) for prime in cell["hilbert"]["minimal_primes"]), arcs.COMPONENTS)
        _same(cell["generator_count"], arcs.GENERATORS)


def test_the_spans_separate_the_two_components() -> None:
    """Span 15 fits the 15-dimensional span of the degree-20 component only; span 20 exceeds it."""
    small, large = (arcs.GENERATORS - linear_forms for _, _, linear_forms in arcs.COMPONENTS)
    _same((small, large), (15, 20))
    _same((arcs.EXPECTED["linear"][2], arcs.EXPECTED["series"][2]), (small, large))
    _same(arcs.EXPECTED["linear"][1], arcs.COMPONENTS[0][0])
    _same(arcs.EXPECTED["series"][1], arcs.COMPONENTS[1][0])


def test_the_linear_arc_maps_seven_slice_coordinates_and_carries_the_sign_on_the_last() -> None:
    names, text = arcs._arc("w8-nm", "linear", 1, VARIABLES)
    _same(names, arcs.LINEAR_PARAMETERS)
    images = text.split("map phi=R0,")[1].rstrip(";").split(",")
    _same(len(images), 9)
    _same([VARIABLES[index] for index, image in enumerate(images) if image == "0"], ["t3", "t8"])
    _same(images[8], "(1)*V*x")
    _same(arcs._arc("w8-np", "linear", -1, VARIABLES)[1].split(",")[-1], "(-1)*V*x;")


def test_the_series_family_refuses_a_sign_other_than_that_of_the_modular_certificate() -> None:
    with pytest.raises(RuntimeError, match="sign"):
        arcs._arc("w8-nm", "series", -arcs.arcs_qi.CASES["w8-nm"][2], VARIABLES)


def _set(slug: str, family: str, key: str, value: object) -> Callable[[dict[str, Any]], None]:
    def mutate(record: dict[str, Any]) -> None:
        _row(record, slug, family)[key] = value

    return mutate


def _control_stays(record: dict[str, Any]) -> None:
    row = _row(record, "w8-nm", "linear", True)
    row["j_nonzero"], row["j_is_identity"] = 0, True


def _drop_row(record: dict[str, Any]) -> None:
    del record["rows"][1]


def _swap_components(record: dict[str, Any]) -> None:
    record["components"].reverse()


def _clear_pass(record: dict[str, Any]) -> None:
    record["pass"] = False


def _schema(record: dict[str, Any]) -> None:
    record["schema"] = "gororoba.a5.w8-component-arcs-qi/0"


MUTATIONS: dict[str, tuple[Callable[[dict[str, Any]], None], str]] = {
    "linear span 20": (_set("w8-nm", "linear", "span_of_limits", 20), "span"),
    "series span 15": (_set("w8-np", "series", "span_of_limits", 15), "degree-20 component"),
    "linear rank 5": (_set("w8-np", "linear", "ranks", [6, 5]), "rank"),
    "series rank 5": (_set("w8-nm", "series", "ranks", [5, 6]), "rank"),
    "linear order 3": (_set("w8-nm", "linear", "order_of_G", 3), "order"),
    "series off the germ": (_set("w8-nm", "series", "j_nonzero", 1), "J does not vanish"),
    "linear J through the jet only": (_set("w8-np", "linear", "j_is_identity", False), "identically"),
    "generator count 23": (_set("w8-nm", "series", "generators", 23), "generator count"),
    "control on the germ": (_control_stays, "reversed sign"),
    "a row removed": (_drop_row, "six cases"),
    "components swapped": (_swap_components, "component table"),
    "pass flag cleared": (_clear_pass, "pass flag"),
    "schema changed": (_schema, "schema"),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_the_checker_rejects_each_mutation_of_the_retained_record(name: str) -> None:
    mutate, fragment = MUTATIONS[name]
    record = copy.deepcopy(_record())
    mutate(record)
    found = arcs.problems(record)
    if not any(fragment in problem for problem in found):
        raise AssertionError((name, found))


def test_the_retained_record_binds_the_current_input_digests() -> None:
    record = _record()
    _same(sorted(record["inputs"]), sorted(arcs.INPUTS))
    for name in arcs.INPUTS:
        _same(record["inputs"][name], hashlib.sha256((TRANSFER / name).read_bytes()).hexdigest())
    _same(record["order"], arcs.arcs_qi.ORDER)
    _same(record["points"], [list(point) for point in arcs.arcs_qi.POINTS])
