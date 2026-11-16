"""Components of the centralizer of G_2 in the kernel-pencil symmetry group: lattices, eigen-classes, the record."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles-residuals"))
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles"))

import centralizer_components as cc  # noqa: E402
import kernel_symmetry as ks  # noqa: E402
import sympy as sp  # noqa: E402

import parallel  # noqa: E402


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
        "eleven components": lambda r: (
            r.update(complex_components=11),
            r["counts"].update(points=11, reduced_points=11),
        ),
        "a third pattern": lambda r: (
            r.update(complex_components=18),
            r["counts"].update(points=18, reduced_points=18),
            r["counts"]["patterns_with_points"].append(
                {
                    "pattern": [[1, 0, 3, 2], 0, [1, 0, 3, 2], 0, 0],
                    "points": 6,
                    "reduced_points": 6,
                    "equations_over_all_indices_not_reduced": 0,
                }
            ),
        ),
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


def _visible(outer: int, epsilon: int, psi: int) -> sp.Matrix:
    """A visible automorphism outer^o epsilon^a psi^b of A_5 on eigen-coordinates."""
    _, frame, inverse = cc.eigen_frame("")
    exact = ks._finite_matrix(32, epsilon, psi, outer, "")
    matrix = sp.Matrix(
        32, 32, lambda r, c: sp.Rational(exact[r][c].rational) + sp.Rational(exact[r][c].radical) * sp.sqrt(3)
    )
    return sp.simplify(inverse * matrix * frame)


def _pattern_and_values(matrix: sp.Matrix) -> tuple[cc.Pattern, dict[str, Any]]:
    """The pattern of a triple (T on U, T, T) read from T on eigen-coordinates, and the values of its unknowns."""
    labels, _, _ = cc.eigen_frame("")
    position = {label: k for k, label in enumerate(labels)}
    classes = cc.UNIT_CLASSES
    unit = []
    for source in classes:
        column = position[(0, *source, 0, 0)]
        hits = [k for k, target in enumerate(classes) if matrix[position[(0, *target, 0, 0)], column] != 0]
        _same(len(hits), 1)
        unit.append(hits[0])
    swap = int(any(matrix[position[(1, -1, 1, image, 1)], position[(1, 1, -1, 0, 1)]] != 0 for image in range(2)))
    swap_g = int(matrix[position[(0, -1, 1, 0, 0)], position[(0, 1, -1, 0, 0)]] != 0)
    pattern: cc.Pattern = (tuple(unit), swap, tuple(unit), swap, swap_g)
    values: dict[str, Any] = {}
    for k, source in enumerate(classes):
        entry = matrix[position[(0, *classes[unit[k]], 0, 0)], position[(0, *source, 0, 0)]]
        values[f"p{k}"] = values[f"q{k}"] = entry
    for sign in cc.SIGNS:
        image_sign = -sign if swap else sign
        base_sign = -sign if swap_g else sign
        tag = (1 - sign) // 2
        for row in range(2):
            for column in range(2):
                block = matrix[position[(1, image_sign, -image_sign, row, 1)], position[(1, sign, -sign, column, 1)]]
                values[f"a{tag}{row}{column}"] = values[f"b{tag}{row}{column}"] = block
                values[f"c{tag}{row}{column}"] = matrix[
                    position[(1, base_sign, -base_sign, row, 1)], position[(1, sign, -sign, column, 1)]
                ]
        values[f"g{tag}"] = matrix[position[(0, base_sign, -base_sign, 0, 0)], position[(0, sign, -sign, 0, 0)]]
    return pattern, values


def _visible_case(item: tuple[int, int, int]) -> tuple[cc.Pattern, tuple[int, int, int], int]:
    """The pattern of one visible automorphism and the number of transport equations of that pattern it fails."""
    outer, epsilon, psi = item
    pattern, values = _pattern_and_values(_visible(outer, epsilon, psi))
    names, generators = cc.pattern_ideal(pattern, "")
    # The last 16 generators are the inverses and the 4 before them the gauge; the rest are the equations.
    equations = generators[: len(generators) - 20]
    symbols = {name: sp.Symbol(name) for name in names} | {"i": sp.I}
    table = {sp.Symbol(name): value for name, value in values.items()}
    failed = sum(
        sp.simplify(sp.sympify(text.replace("^", "**"), locals=symbols).subs(table)) != 0 for text in equations
    )
    return pattern, item, int(failed)


def test_the_twelve_visible_automorphisms_solve_the_two_patterns_six_each() -> None:
    """The lower S_3 lies in the identity pattern and its products with the outer reflection in the sign-negating
    one; each satisfies every transport equation of its pattern. Six distinct solutions modulo T in an ideal with
    six points also show that the ideal is radical, with no call to `radical`."""
    items = [(outer, epsilon, psi) for outer in range(2) for epsilon in range(2) for psi in range(3)]
    members: dict[cc.Pattern, list[tuple[int, int, int]]] = {}
    for pattern, item, failed in parallel.ordered_map(_visible_case, items, min_items=1):
        _same(failed, 0)
        members.setdefault(pattern, []).append(item)
    identity: cc.Pattern = ((0, 1, 2, 3), 0, (0, 1, 2, 3), 0, 0)
    negating: cc.Pattern = ((3, 2, 1, 0), 1, (3, 2, 1, 0), 1, 1)
    _same(sorted(members), sorted([identity, negating]))
    _same([sorted({outer for outer, _, _ in members[pattern]}) for pattern in (identity, negating)], [[0], [1]])
    _same([len(members[pattern]) for pattern in (identity, negating)], [6, 6])
