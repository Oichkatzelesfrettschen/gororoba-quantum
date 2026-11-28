"""Cell scripts of the weight-slice unit-replacement route: two substitutions of the retained template."""

from __future__ import annotations

import a5_weight_slice_unit_cells as record


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


def test_only_the_j_line_and_the_root_change() -> None:
    template = record.TEMPLATE.read_text(encoding="utf-8").split("\n")
    cell = record.cell_script("xp", 21255).split("\n")
    require(len(cell) == len(template))
    changed = [k for k, (a, b) in enumerate(zip(template, cell, strict=True)) if a != b]
    require(all(cell[k].startswith("ideal J=") or "number i=21255" in cell[k] for k in changed))
    require(sum("number i=21255" in line for line in cell) == 2)


def test_the_mutant_drops_one_generator() -> None:
    full = record.equations("iso")
    dropped = record.equations("iso", True)
    require(dropped.count(",") == full.count(",") - 1 and full.endswith(dropped))
