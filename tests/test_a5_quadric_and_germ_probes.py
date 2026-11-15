"""The retained germ, quadric and plane-image records of the A_5 fiber track hold their findings.

Each test applies a record's check() to the retained record and to copies that drop, relabel or alter a row.
"""

import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

HERE = Path(__file__).resolve().parents[1] / "docs/evidence/a5-exceptional-fibers/structure"


def load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"a5_{name}", HERE / f"{name}.py")
    if spec is None or spec.loader is None:
        raise ImportError(name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def record(name: str = "quadric-and-germ-probes") -> list[dict[str, Any]]:
    return [json.loads(ln) for ln in (HERE / f"{name}.jsonl").read_text().splitlines()]


def row(rows: list[dict[str, Any]], kind: str, index: int = 0) -> dict[str, Any]:
    return [r for r in rows if r["check"] == kind][index]


def test_the_retained_probe_record_passes_and_names_existing_inputs() -> None:
    mod = load("quadric_and_germ_probes")
    rows = record()
    if mod.check(rows):
        raise AssertionError(mod.check(rows))
    for r in rows:
        if not (mod.W / r.get("input", r.get("relations", ""))).is_file():
            raise AssertionError(r)


def drop_pivot(rows: list[dict[str, Any]]) -> None:
    germ = row(rows, "germ-prime")
    germ["pivot"] = None
    del germ["pivot_in_J"]


def duplicate_a_germ(rows: list[dict[str, Any]]) -> None:
    rows[5] = dict(rows[4])


def drop_sections(rows: list[dict[str, Any]]) -> None:
    sections = row(rows, "vb-components")["components"][0]["sections"]
    for base in ("3", "4", "5"):
        del sections[base]


MUTATIONS = {
    "two minimal primes": lambda rows: row(rows, "germ-prime").update(minimal_primes=2),
    "a pivot inside J": lambda rows: row(rows, "germ-prime").update(pivot_in_J=1),
    "a pivot test removed": drop_pivot,
    "a germ replaced by a copy of another": duplicate_a_germ,
    "a 32029 comparison removed": lambda rows: row(rows, "germ-prime", 6).pop("equals_32009_text"),
    "a changed generator count": lambda rows: row(rows, "germ-prime").update(gens=13),
    "a relabeled prime": lambda rows: row(rows, "vb-components", 1).update(prime=32009),
    "a component without an F_p-point": lambda rows: [
        s.update(orbits=[3]) for s in row(rows, "vb-components")["components"][0]["sections"].values()
    ],
    "a negative orbit": lambda rows: row(rows, "vb-components")["components"][1]["sections"]["2"].update(
        orbits=[-1, 1, 4]
    ),
    "sections of three bases removed": drop_sections,
    "a meet of degree two": lambda rows: row(rows, "vb-components")["meet"].update(degree=2),
    "a Hilbert value in degree eight": lambda rows: row(rows, "vb-components")["hf"].update({"8": [0, 0, 0, 0]}),
    "a nonlinear colon form": lambda rows: row(rows, "x-colon")["forms"].__setitem__(0, "y(14)^2"),
    "a thirteenth colon form": lambda rows: row(rows, "x-colon")["forms"].append("y(4)"),
    "a shifted numerator pair": lambda rows: [row(rows, "x-colon")[k].__setitem__(0, 101) for k in ("numK", "numP")],
    "a changed numerator": lambda rows: row(rows, "x-colon")["numP"].__setitem__(2, -29),
    "a row removed": lambda rows: rows.pop(),
    "a colon ideal with two minimal primes": lambda rows: row(rows, "e8-colon")["colon"].__setitem__(5, 2),
    "a radical with a sixth linear form": lambda rows: row(rows, "e8-colon")["radical"].__setitem__(0, 6),
    "a changed radical numerator": lambda rows: row(rows, "e8-colon", 3)["numR"].__setitem__(1, -4),
    "a quadric numerator replaced by a plane": lambda rows: row(rows, "e8-colon").update(numA=[1, -18, 153]),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_a_changed_probe_record_is_reported(name: str) -> None:
    mod = load("quadric_and_germ_probes")
    rows = record()
    MUTATIONS[name](rows)
    if not mod.check(rows):
        raise AssertionError(f"{name}: the changed record passes")


def test_the_retained_plane_images_pass_and_recompute() -> None:
    mod = load("embedded_plane_images")
    rows = record("embedded-plane-images")
    if mod.check(rows) or mod.build() != rows:
        raise AssertionError(mod.check(rows))


def test_meeting_spans_or_a_plane_outside_the_section_are_reported() -> None:
    mod = load("embedded_plane_images")
    meeting = record("embedded-plane-images")
    meeting[0]["ranks"] = [15, 3, 17]
    outside = record("embedded-plane-images")
    outside[2]["Va"]["with_forms"] = 13
    shared = record("embedded-plane-images")
    shared[3]["Va"]["on_opposite"] = 2
    if not all(mod.check(rows) for rows in (meeting, outside, shared, outside[:-1])):
        raise AssertionError("a changed plane record passes")


def test_a_form_that_is_not_a_sum_of_signed_variables_is_rejected() -> None:
    mod = load("embedded_plane_images")
    if mod.form_row("y(3)-y(10)", 15, 7)[2:10] != [1, 0, 0, 0, 0, 0, 0, 6]:
        raise AssertionError(mod.form_row("y(3)-y(10)", 15, 7))
    with pytest.raises(ValueError, match="not a sum"):
        mod.form_row("2*y(3)", 15, 7)
