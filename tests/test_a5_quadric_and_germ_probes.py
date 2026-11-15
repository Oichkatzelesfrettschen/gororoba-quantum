"""The retained germ and quadric probes of the A_5 fiber track hold their findings, and a changed record is reported."""

import copy
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

HERE = Path(__file__).resolve().parents[1] / "docs/evidence/a5-exceptional-fibers/structure"


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("a5_quadric_and_germ_probes", HERE / "quadric_and_germ_probes.py")
    if spec is None or spec.loader is None:
        raise ImportError(HERE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def record() -> list[dict[str, Any]]:
    return [json.loads(ln) for ln in (HERE / "quadric-and-germ-probes.jsonl").read_text().splitlines()]


def first(rows: list[dict[str, Any]], kind: str) -> dict[str, Any]:
    return next(r for r in rows if r["check"] == kind)


def test_the_retained_record_passes_and_names_tracked_inputs() -> None:
    mod = load()
    rows = record()
    if mod.check(rows):
        raise AssertionError(mod.check(rows))
    for r in rows:
        if not (mod.W / r.get("input", r.get("relations", ""))).is_file():
            raise AssertionError(r)


def test_a_germ_with_two_primes_or_a_pivot_inside_it_is_reported() -> None:
    mod = load()
    rows = record()
    first(rows, "germ-prime")["minimal_primes"] = 2
    pivoted = copy.deepcopy(record())
    next(r for r in pivoted if r["check"] == "germ-prime" and r["pivot"] is not None)["pivot_in_J"] = 1
    if not mod.check(rows) or not mod.check(pivoted):
        raise AssertionError("a changed germ row passes")


def test_a_component_without_a_rational_point_or_a_changed_meet_is_reported() -> None:
    mod = load()
    rows = record()
    for section in first(rows, "vb-components")["components"][0]["sections"].values():
        section["orbits"] = [3]
    moved = record()
    first(moved, "vb-components")["meet"]["degree"] = 2
    if not mod.check(rows) or not mod.check(moved):
        raise AssertionError("a changed component row passes")


def test_a_broken_numerator_identity_or_a_thirteenth_form_is_reported() -> None:
    mod = load()
    rows = record()
    first(rows, "x-colon")["numP"][2] += 1
    longer = record()
    first(longer, "x-colon")["forms"].append("y(4)")
    if not mod.check(rows) or not mod.check(longer):
        raise AssertionError("a changed colon row passes")
