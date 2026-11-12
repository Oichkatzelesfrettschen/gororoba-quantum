"""Levi structure of the linear symmetry algebras of the retained quadric ideals: known algebras and the record."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CENSUS = ROOT / "docs" / "evidence" / "a5-exceptional-fibers" / "quadric-census"
sys.path.insert(0, str(CENSUS))

import symmetry_algebra as sa  # noqa: E402

PRIME = 32009


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


# fiber: (dim g, radical, nilpotent ideal, torus rank)
EXPECTED = {
    "X-": (23, 20, 16, 5),
    "X+": (23, 20, 16, 5),
    "E8-bar -> VB": (15, 12, 8, 5),
    "Iso": (17, 14, 11, 4),
    "E8-bar -> N-": (34, 31, 26, 6),
    "E8-bar -> N+": (34, 31, 26, 6),
    "W8 -> N-": (26, 23, 19, 5),
}


CHECKS = {
    "radical_is_solvable_ideal": True,
    "quotient_by_radical_is_perfect": True,
    "nil_ideal_is_nilpotent_ideal": True,
    "cartan_is_toral": True,
}
SO4 = {
    "dimension": 7,
    "derived_series": [7, 6],
    "center": 1,
    "radical": 1,
    "trace_form_nil_ideal": 0,
    "central_torus": 1,
    "levi_dimension": 6,
    "levi_rank": 2,
    "levi_type": "sl2 + sl2",
    "generic_centralizer": 3,
    "cartan_dimension": 3,
    "cartan_derived_dimension": 0,
    "torus_rank": 3,
}
PARABOLIC = SO4 | {
    "derived_series": [7, 5],
    "radical": 4,
    "trace_form_nil_ideal": 2,
    "central_torus": 2,
    "levi_dimension": 3,
    "levi_rank": 1,
    "levi_type": "sl2",
}
GL3 = SO4 | {"dimension": 9, "derived_series": [9, 8], "levi_dimension": 8, "levi_type": "sl3"}
HEISENBERG = {
    "dimension": 3,
    "derived_series": [3, 1, 0],
    "center": 1,
    "radical": 3,
    "trace_form_nil_ideal": 3,
    "central_torus": 0,
    "levi_dimension": 0,
    "levi_rank": 0,
    "levi_type": "0",
    "generic_centralizer": 2,
    "cartan_dimension": 3,
    "cartan_derived_dimension": 1,
    "torus_rank": 0,
}


def test_stabilizer_of_a_nondegenerate_quadric_is_so4_with_scalars() -> None:
    algebra = sa.stabilizer([{(i, i): 1 for i in range(4)}], 4, PRIME)
    _same(sa.analyze(algebra, PRIME, "so4"), SO4 | CHECKS)


def test_stabilizer_of_a_squared_coordinate_is_a_parabolic_with_a_nilpotent_ideal() -> None:
    _same(sa.analyze(sa.stabilizer([{(0, 0): 1}], 3, PRIME), PRIME, "parabolic"), PARABOLIC | CHECKS)


def test_stabilizer_of_no_quadric_is_gl3() -> None:
    _same(sa.analyze(sa.stabilizer([], 3, PRIME), PRIME, "gl3"), GL3 | CHECKS)


def test_heisenberg_algebra_has_a_cartan_subalgebra_that_is_not_toral() -> None:
    units = [(0, 1), (1, 2), (0, 2)]
    algebra = sa.np.array([[[int((i, j) == unit) for j in range(3)] for i in range(3)] for unit in units])
    _same(sa.analyze(algebra, PRIME, "heisenberg"), HEISENBERG | CHECKS | {"cartan_is_toral": False})


def test_semisimplicity_separates_a_jordan_block_from_diagonal_and_rotation_matrices() -> None:
    found = [sa.is_semisimple(sa.np.array(m), PRIME) for m in ([[1, 1], [0, 1]], [[1, 0], [0, 2]], [[0, 1], [-1, 0]])]
    _same(found, [False, True, True])


def test_a_span_that_is_not_a_lie_algebra_is_rejected() -> None:
    algebra = sa.stabilizer([], 2, PRIME)[:3]
    with pytest.raises(ValueError, match="not closed"):
        sa.analyze(algebra[[1, 2]], PRIME, "open")


def test_retained_record_gives_sl2_and_an_abelian_cartan_torus_on_every_file() -> None:
    rows = json.loads((CENSUS / "symmetry-algebra.json").read_text(encoding="utf-8"))["rows"]
    _same((len(rows), len(sa.SOURCES)), (14, 14))
    for row in rows:
        numbers = row["algebra"]
        _same(row["control_stabilizer_dimension"], 1)
        _same({key: numbers[key] for key in CHECKS}, CHECKS)
        _same((numbers["levi_type"], numbers["center"], numbers["cartan_derived_dimension"]), ("sl2", 1, 0))
        _same((numbers["cartan_dimension"], numbers["generic_centralizer"]), (numbers["torus_rank"],) * 2)
        found = (numbers["dimension"], numbers["radical"], numbers["trace_form_nil_ideal"], numbers["torus_rank"])
        _same(found, EXPECTED[row["fiber"]])


def test_linear_forms_keep_the_degree_one_generators_only() -> None:
    forms = sa.linear_forms("y(1)+3*y(2),y(1)*y(2)+y(3)*y(4),-y(3),y(2)^2,2*y(4)-y(1),5", 4, PRIME)
    _same(forms.tolist(), [[1, 0, 0, PRIME - 2], [0, 1, 0, 2 * pow(3, -1, PRIME) % PRIME], [0, 0, 1, 0]])


def test_restricted_torus_loses_the_directions_that_fix_the_subspace() -> None:
    """The diagonal torus of gl(3) on the plane y(3) = 0 has rank 2 and preserves it; a shear does not preserve it."""
    diagonal = sa.np.array([sa.np.diag([1 if i == k else 0 for i in range(3)]) for k in range(3)])
    plane = sa.linear_forms("y(3)", 3, PRIME)
    row = sa.restricted_torus(diagonal, plane, PRIME)
    _same((row["span_dimension"], row["span_preserved"], row["torus_rank_on_span"]), (2, True, 2))
    shear = sa.np.array([[[0, 0, 0], [0, 0, 0], [1, 0, 0]]])
    _same(sa.restricted_torus(shear, plane, PRIME)["span_preserved"], False)


def test_retained_record_gives_the_torus_rank_on_each_w8_component() -> None:
    rows = json.loads((CENSUS / "symmetry-algebra.json").read_text(encoding="utf-8"))["rows"]
    with_components = [row for row in rows if row["components"]]
    _same([(row["fiber"], row["prime"]) for row in with_components], [("W8 -> N-", 32009)])
    found = {
        name: (c["linear_forms"], c["span_dimension"], c["span_preserved"], c["torus_rank_on_span"], c["complexity"])
        for name, c in with_components[0]["components"].items()
    }
    _same(found, {"C20": (9, 15, True, 4, 2), "C30": (4, 20, True, 5, 1)})
