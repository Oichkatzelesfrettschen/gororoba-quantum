"""Exact symmetry algebras of quadrics over Q(i): known algebras, the scalar and echelon layer, and the record."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

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
    changes = {
        "quotient_by_radical_has_sl2_triple": lambda row: row["algebra"].update(
            quotient_by_radical_has_sl2_triple=False
        ),
        "radical_is_solvable_ideal": lambda row: row["algebra"].update(radical_is_solvable_ideal=False),
        "quotient_by_radical_is_perfect": lambda row: row["algebra"].update(quotient_by_radical_is_perfect=False),
        "nil_ideal_is_nilpotent_ideal": lambda row: row["algebra"].update(nil_ideal_is_nilpotent_ideal=False),
        "cartan_is_toral": lambda row: row["algebra"].update(cartan_is_toral=False),
        "reduced dimension": lambda row: row["reduction"].update(stabilizer_dimension_of_reduced_quadrics=1),
        "reduced numbers": lambda row: row["reduction"].update(numbers_of_reduced_basis_equal=False),
        "control": lambda row: row.update(control_stabilizer_dimension_modulo_prime=2),
        "weight derivation": lambda row: row.update(weight_derivation_stabilizes=False),
        "euler field": lambda row: row.update(euler_field_stabilizes=False),
    }
    _same(sorted(set(qi.CHECKS) - set(changes)), [])
    for name, change in changes.items():
        mutated = json.loads(json.dumps(record))
        change(mutated["rows"][0])
        if qi.verdict(mutated) == []:
            raise AssertionError(f"a record mutated at {name} passes")


def test_exact_predicates_reject_a_subspace_that_is_no_ideal_and_a_series_that_stops_above_zero() -> None:
    # gl2 on the basis E11, E12, E21, E22: the span of E12 is no ideal, sl2 is perfect, and the upper triangular
    # matrices are solvable and not nilpotent.
    units = [[[int((i, j) == unit) for j in range(2)] for i in range(2)] for unit in ((0, 0), (0, 1), (1, 0), (1, 1))]
    _, ad = qi.adjoint([_matrix(rows) for rows in units], "gl2")
    structure = qi.Structure(ad)
    e11, e12, e21, e22 = structure.whole
    sl2 = [[a - b for a, b in zip(e11, e22, strict=True)], e12, e21]
    borel = [e11, e12, e22]

    def derived(space: qi.Rows) -> qi.Rows:
        return structure.bracket_span(space, space)

    _same([structure.is_ideal([e12]), structure.is_ideal(sl2)], [False, True])
    _same([structure.reaches_zero(sl2, derived), structure.reaches_zero(borel, derived)], [False, True])
    _same(structure.reaches_zero(borel, lambda space: structure.bracket_span(borel, space)), False)
    _same([structure.sums_to_whole(sl2, [e12]), structure.sums_to_whole(sl2, [e11])], [False, True])
    _same(qi.quotient_has_sl2_triple(structure, [[a + b for a, b in zip(e11, e22, strict=True)]]), True)
    _same(qi.quotient_has_sl2_triple(structure, [e12]), False)


def test_check_ignores_the_singular_banner_and_compares_the_version() -> None:
    record = {"tools": {"singular": "banner A", "singular_version": "4.4.1"}, "rows": []}
    banner = {"tools": {"singular": "banner B", "singular_version": "4.4.1"}, "rows": []}
    version = {"tools": {"singular": "banner A", "singular_version": "4.4.0"}, "rows": []}
    _same(
        [qi.comparable(record) == qi.comparable(banner), qi.comparable(record) == qi.comparable(version)], [True, False]
    )


def _gauss_rows(rows: list[list[int]]) -> qi.Rows:
    return [[qi.Gauss(value, 0) for value in row] for row in rows]


def test_levi_lift_of_the_parabolic_restores_the_sl2_relations_and_reads_its_strings() -> None:
    # The stabilizer of y0^2 in gl3 is a parabolic with Levi factor gl1 x gl2; its sl2 acts on (y1, y2).
    matrices, _ = qi.stabilizer([{(0, 0): ONE}], 3)
    basis, ad = qi.adjoint(matrices, "parabolic")
    structure = qi.Structure(ad)
    radical = qi.killing_radical(structure)
    triple = qi.quotient_sl2_triple(structure, radical)
    if triple is None:
        raise AssertionError("no triple in the quotient of the parabolic")
    lift = qi.levi_lift(structure, radical, triple)
    if lift is None:
        raise AssertionError("no Levi lift of the parabolic")
    _same([any(defect) for defect in qi.sl2_defects(structure, lift)], [False, False, False])
    spectrum = qi.integer_spectrum(qi.combine(lift[0], basis))
    _same((spectrum, qi.sl2_strings(spectrum)), ({-1: 1, 0: 1, 1: 1}, {0: 1, 1: 1}))
    # A triple moved by an element of the radical keeps its classes and loses the relations.
    moved = ([a + b for a, b in zip(lift[0], radical[0], strict=True)], lift[1], lift[2])
    _same(any(any(defect) for defect in qi.sl2_defects(structure, moved)), True)


def test_strings_of_the_weights_of_a_cubic_and_a_trivial_summand() -> None:
    _same(qi.sl2_strings({-3: 1, -1: 1, 0: 1, 1: 1, 3: 1}), {0: 1, 3: 1})
    _same(qi.integer_spectrum(_matrix([[2, 0, 0], [0, 0, 0], [0, 0, -2]])), {-2: 1, 0: 1, 2: 1})
    # A Jordan block has an eigenspace smaller than its size: the spectrum does not fill the space.
    _same(sum(qi.integer_spectrum(_matrix([[1, 1], [0, 1]])).values()), 1)


def test_an_inconsistent_system_has_no_solution_and_a_consistent_one_is_solved() -> None:
    _same(qi.solve(_gauss_rows([[1, 1], [1, 1]]), [ONE, qi.Gauss(2, 0)], 2), None)
    _same(qi.solve(_gauss_rows([[1, 0], [0, 2]]), [ONE, IMAGINARY], 2), [ONE, qi.Gauss(0, qi.fmpq(1, 2))])


def test_eigenvalues_inside_and_outside_the_gaussian_field() -> None:
    _same(qi.eigenvalues(_matrix([[0, 1], [-1, 0]])), [qi.Gauss(0, -1), qi.Gauss(0, 1)])
    _same(qi.eigenvalues(_matrix([[2, 0], [0, -3]])), [qi.Gauss(-3, 0), qi.Gauss(2, 0)])
    # x^2 - 2 has no root in Q(i); x^4 + 1 splits only over the eighth roots of unity.
    _same(qi.eigenvalues(_matrix([[0, 2], [1, 0]])), None)
    _same(qi.eigenvalues(qi.CMat.from_rows([[qi.ZERO, IMAGINARY], [ONE, qi.ZERO]], 2)), None)
    # A matrix over Q(i) with eigenvalue i alone: the conjugate root of the rational polynomial is rejected.
    _same(qi.eigenvalues(qi.CMat.from_rows([[IMAGINARY, ONE], [qi.ZERO, IMAGINARY]], 2)), [IMAGINARY])


def test_joint_eigenspaces_fill_the_space_only_for_diagonalizable_matrices() -> None:
    first, second = _matrix([[1, 0, 0], [0, 1, 0], [0, 0, 2]]), _matrix([[0, 1, 0], [1, 0, 0], [0, 0, 5]])
    spaces = qi.joint_eigenspaces([first, second], 3)
    if spaces is None:
        raise AssertionError("commuting diagonalizable matrices have no joint eigenspaces")
    _same(
        sorted((len(vectors), [str(value.re) for value in weight]) for vectors, weight in spaces),
        [(1, ["1", "-1"]), (1, ["1", "1"]), (1, ["2", "5"])],
    )
    jordan = qi.joint_eigenspaces([_matrix([[1, 1], [0, 1]])], 2)
    _same(None if jordan is None else sum(len(vectors) for vectors, _ in jordan), 1)
    _same(qi.joint_eigenspaces([_matrix([[0, 2], [1, 0]])], 2), None)


def test_integer_weights_need_a_rational_lattice_of_full_rank() -> None:
    half = qi.Gauss(qi.fmpq(1, 2), 0)
    weights = [[ONE, qi.ZERO], [half, half], [qi.ZERO, ONE]]
    integral = qi.integer_weights(weights, 2)
    if integral is None:
        raise AssertionError("a rational lattice of rank 2 was refused")
    # The three weights generate a lattice in which (1/2, 1/2) is primitive: its coordinates have gcd 1.
    _same(all(isinstance(value, int) for row in integral for value in row), True)
    _same(qi.cocharacter(integral, [qi.Gauss(2, 0), ONE, qi.ZERO]) is not None, True)
    _same(qi.cocharacter(integral, [ONE, ONE, qi.ZERO]), None)
    _same(qi.integer_weights([[ONE, qi.ZERO], [qi.Gauss(2, 0), qi.ZERO]], 2), None)
    _same(qi.integer_weights([[ONE], [IMAGINARY]], 1), None)


def test_quadrics_split_by_weight_exactly_when_the_torus_preserves_them() -> None:
    eigenvectors = qi.CMat.identity(3).rows()
    weights = [[1, 0], [0, 1], [1, 1]]
    stable, _ = qi.quadric_basis([{(0, 1): ONE, (2, 2): IMAGINARY}, {(0, 0): ONE}], 3)
    mixed, _ = qi.quadric_basis([{(0, 1): ONE, (2, 2): ONE}], 3)
    _same(qi.quadric_weight_spaces(stable, eigenvectors, weights, 3)["sum_of_weight_space_dimensions"], 3)
    # y0 y1 has weight (1, 1) and y2^2 has weight (2, 2): the sum is no weight vector and the dimensions exceed 1.
    _same(qi.quadric_weight_spaces(mixed, eigenvectors, weights, 3)["sum_of_weight_space_dimensions"], 2)


def test_each_refinement_rule_fails_on_a_mutated_row() -> None:
    record = json.loads(qi.RECORD.read_text(encoding="utf-8"))
    row = record["rows"][0]
    _same(qi.refinement_problems(row), [])

    def clear(flag: str) -> Callable[[dict[str, Any]], Any]:
        return lambda r: r["refinement"].update({flag: False})

    changes: dict[str, Callable[[dict[str, Any]], Any]] = {flag: clear(flag) for flag in qi.REFINEMENT_FLAGS}
    changes |= {
        "h spectrum": lambda r: r["refinement"]["h_spectrum"].update({"3": 2}),
        "strings": lambda r: r["refinement"].update(sl2_strings_total=0),
        "weights": lambda r: r["refinement"]["weights"][0].__setitem__(-1, 5),
        "rank": lambda r: r["algebra"].update(cartan_dimension=1),
        "euler": lambda r: r["refinement"].update(cocharacter_of_euler_field=None),
        "h": lambda r: r["refinement"].update(cocharacter_of_h=None),
        "derivation": lambda r: r["refinement"].update(cocharacter_of_weight_derivation=None),
        "quadrics": lambda r: r["refinement"]["quadrics_by_weight"].update(sum_of_weight_space_dimensions=0),
    }
    for name, change in changes.items():
        mutated = json.loads(json.dumps(row))
        change(mutated)
        if qi.refinement_problems(mutated) == []:
            raise AssertionError(f"a row mutated at {name} passes")
