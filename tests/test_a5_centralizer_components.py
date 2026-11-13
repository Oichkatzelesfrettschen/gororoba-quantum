"""Components of the centralizer of G_2 in the kernel-pencil symmetry group: lattices, eigen-classes, the record."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles-residuals"))

import centralizer_components as cc  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def test_lattice_basis_kernel_and_coordinates() -> None:
    _same(cc.lattice_basis([[2, 0], [0, 2], [1, 1]]), [[1, 1], [0, 2]])
    _same(cc.integer_kernel([[1, 1, 0], [0, 0, 0]]), [[1, -1, 0], [0, 0, 1]])
    # (1, 1) and (1, -1) span a sublattice of index 2: (1, 0) has half-integer coordinates there.
    _same(cc.lattice_coordinates([[1, 1], [1, -1]], [2, 0]), [1, 1])
    _same(cc.lattice_coordinates([[1, 1], [1, -1]], [1, 0]), None)
    _same(cc.lattice_coordinates([[1, 0, 0]], [0, 1, 0]), None)


def test_joint_eigenspaces_are_four_unit_lines_and_two_vector_planes() -> None:
    expected = {"unit": {"1,1": 1, "1,-1": 1, "-1,1": 1, "-1,-1": 1}, "vector": {"1,-1": 2, "-1,1": 2}}
    _same(cc.eigen_classes(""), expected)


def test_gauge_characters_generate_the_character_lattice_and_the_real_torus_is_connected() -> None:
    summary = cc.torus_summary("")
    found = (
        summary["character_lattice_rank"],
        summary["gauge_index_in_character_lattice"],
        summary["norm_elementary_divisors"],
        summary["real_torus_components"],
    )
    _same(found, (4, 1, [1, 1], 1))


def test_the_pattern_enumeration_and_the_identity_triple() -> None:
    patterns = cc.all_patterns()
    _same((len(patterns), len(set(patterns))), (4608, 4608))
    _same(cc.identity_solves(""), True)
    names, generators = cc.pattern_ideal(patterns[0], "")
    _same((len(names), len(set(names))), (50, 50))
    if not any(text == "p0 - 1" for text in generators):
        raise AssertionError("the gauge is missing from the ideal")


def test_retained_record_passes_its_rules_and_each_mutation_fails_them() -> None:
    record = json.loads(cc.RECORD.read_text(encoding="utf-8"))
    _same((record["pass"], cc.verdict(record), record["complex_components"]), (True, [], 12))
    changes: dict[str, Callable[[dict[str, Any]], Any]] = {
        "enumeration": lambda r: r["counts"].update(patterns=4607),
        "positive dimension": lambda r: r["counts"].update(patterns_of_positive_dimension=1),
        "radical": lambda r: r["counts"].update(points=r["counts"]["points"] + 1),
        "other octonion index": lambda r: r["counts"]["patterns_with_points"][0].update(
            equations_over_all_indices_not_reduced=1
        ),
        "gauge": lambda r: r["torus"].update(gauge_index_in_character_lattice=2),
        "rank": lambda r: r["torus"].update(character_lattice_rank=3),
        "real torus": lambda r: r["torus"].update(real_torus_components=2),
        "count": lambda r: r.update(complex_components=11),
        "identity": lambda r: r["controls"].update(identity_triple_solves_identity_pattern=False),
        "mutation control": lambda r: r["controls"].update(
            identity_pattern_points_with_flipped_sign=6, identity_pattern_dimension_positive_with_flipped_sign=0
        ),
    }
    for name, change in changes.items():
        mutated = json.loads(json.dumps(record))
        change(mutated)
        if cc.verdict(mutated) == []:
            raise AssertionError(f"a record mutated at {name} passes")
