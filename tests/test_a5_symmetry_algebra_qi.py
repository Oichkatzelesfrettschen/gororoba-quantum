"""Exact symmetry algebras of quadrics over Q(i): known algebras, the scalar and echelon layer, and the record."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATTACHMENTS = ROOT / "docs" / "evidence" / "a5-kernel-attachments"
sys.path.insert(0, str(ATTACHMENTS))
sys.path.insert(0, str(ROOT / "tests"))

import symmetry_algebra_qi as qi  # noqa: E402
from test_a5_symmetry_algebra import CHECKS, GL3, HEISENBERG, PARABOLIC, SO4, TRIPLE  # noqa: E402

ONE, IMAGINARY = qi.Gauss(1, 0), qi.Gauss(0, 1)


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _numbers(quadrics: list[dict[tuple[int, int], qi.Gauss]], n: int, label: str) -> dict[str, object]:
    return qi.decompose(qi.stabilizer(quadrics, n)[0], label)[0]


def _matrix(rows: list[list[int]]) -> qi.CMat:
    return qi.CMat.from_rows([[qi.Gauss(value, 0) for value in row] for row in rows], len(rows[0]))


def test_stabilizer_of_a_nondegenerate_quadric_is_so4_with_scalars() -> None:
    _same(_numbers([{(i, i): ONE for i in range(4)}], 4, "so4"), SO4 | CHECKS)


def test_a_gaussian_change_of_coordinates_keeps_the_structure_numbers() -> None:
    # y0^2 + y1^2 + y2^2 + y3^2 = (y0 + i y1)(y0 - i y1) + (y2 + i y3)(y2 - i y3): the same quadric as a sum of
    # two products, written on coordinates that need i.
    quadric = {(0, 1): IMAGINARY, (2, 3): qi.Gauss(0, -2)}
    _same(_numbers([quadric], 4, "so4 split"), SO4 | CHECKS)


def test_stabilizer_of_a_squared_coordinate_is_a_parabolic_with_a_nilpotent_ideal() -> None:
    _same(_numbers([{(0, 0): ONE}], 3, "parabolic"), PARABOLIC | CHECKS | TRIPLE)


def test_stabilizer_of_no_quadric_is_gl3() -> None:
    _same(_numbers([], 3, "gl3"), GL3 | CHECKS)


def test_heisenberg_algebra_has_a_cartan_subalgebra_that_is_not_toral() -> None:
    units = [(0, 1), (1, 2), (0, 2)]
    algebra = [_matrix([[int((i, j) == unit) for j in range(3)] for i in range(3)]) for unit in units]
    _same(qi.decompose(algebra, "heisenberg")[0], HEISENBERG | CHECKS | {"cartan_is_toral": False})


def test_semisimplicity_separates_a_jordan_block_from_diagonal_and_rotation_matrices() -> None:
    found = [qi.is_semisimple(_matrix(m)) for m in ([[1, 1], [0, 1]], [[1, 0], [0, 2]], [[0, 1], [-1, 0]])]
    _same(found, [False, True, True])
    _same(qi.is_semisimple(qi.CMat.from_rows([[IMAGINARY, ONE], [qi.ZERO, IMAGINARY]], 2)), False)


def test_square_roots_in_the_gaussian_field() -> None:
    squares = [qi.Gauss(4, 0), qi.Gauss(-9, 0), qi.Gauss(0, 2), qi.Gauss(3, 4), qi.Gauss(-5, 12)]
    for value in squares:
        root = qi.gauss_sqrt(value)
        if root is None or root * root != value:
            raise AssertionError(str((value.re, value.im)))
    _same([qi.gauss_sqrt(value) for value in (qi.Gauss(2, 0), qi.Gauss(0, 1), qi.Gauss(1, 1))], [None, None, None])


def test_echelon_form_over_the_gaussian_field() -> None:
    # (1, i) and (i, -1) are dependent over Q(i) and independent over Q.
    basis, pivots = qi.rref([[ONE, IMAGINARY], [IMAGINARY, qi.Gauss(-1, 0)]], 2)
    _same((basis, pivots), ([[ONE, IMAGINARY]], [0]))
    # x0 + i x1 = 0 holds on the line of (-i, 1), whose echelon generator is (1, i).
    _same(qi.null_space([[ONE, IMAGINARY]], 2), [[ONE, IMAGINARY]])
    _same(qi.rank([[ONE, IMAGINARY], [ONE, qi.Gauss(0, -1)]], 2), 2)


def test_a_matrix_outside_the_stabilizer_fails_the_exact_test() -> None:
    quadrics = [{(0, 0): ONE, (1, 1): ONE}]
    basis, pivots = qi.quadric_basis(quadrics, 2)
    sparse = [{k: entry for k, entry in enumerate(row) if entry} for row in basis]
    found = [
        qi.stabilizes(_matrix(rows), sparse, basis, pivots, 2)
        for rows in ([[0, 1], [-1, 0]], [[1, 0], [0, 1]], [[0, 1], [1, 0]])
    ]
    _same(found, [True, True, False])


def test_retained_record_passes_its_rules_and_a_changed_number_fails_them() -> None:
    record = json.loads(qi.RECORD.read_text(encoding="utf-8"))
    _same((record["pass"], qi.verdict(record), len(record["rows"])), (True, [], 8))
    expected = {"X": (23, 20, 16, 5), "Iso": (17, 14, 11, 4), "E8bar": (34, 31, 26, 6), "W8": (26, 23, 19, 5)}
    for row in record["rows"]:
        algebra = row["algebra"]
        found = (algebra["dimension"], algebra["radical"], algebra["trace_form_nil_ideal"], algebra["torus_rank"])
        _same(found, expected[row["incidence"].split("->")[0].rstrip("+-")])
        _same((algebra["levi_type"], algebra["cartan_dimension"]), ("sl2", found[3]))
    for change in (
        lambda row: row["algebra"].update(quotient_by_radical_has_sl2_triple=False),
        lambda row: row["reduction"].update(stabilizer_dimension_of_reduced_quadrics=1),
        lambda row: row.update(control_stabilizer_dimension_modulo_prime=2),
        lambda row: row.update(weight_derivation_stabilizes=False),
    ):
        mutated = json.loads(json.dumps(record))
        change(mutated["rows"][0])
        if qi.verdict(mutated) == []:
            raise AssertionError("a mutated record passes")
