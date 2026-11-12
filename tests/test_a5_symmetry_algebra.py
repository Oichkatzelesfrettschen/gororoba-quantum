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


def test_stabilizer_of_a_nondegenerate_quadric_is_so4_with_scalars() -> None:
    algebra = sa.stabilizer([{(i, i): 1 for i in range(4)}], 4, PRIME)
    numbers = sa.analyze(algebra, PRIME, "so4")
    _same((numbers["dimension"], numbers["radical"], numbers["trace_form_nil_ideal"]), (7, 1, 0))
    _same((numbers["levi_type"], numbers["torus_rank"], numbers["center"]), ("sl2 + sl2", 3, 1))


def test_stabilizer_of_a_squared_coordinate_is_a_parabolic_with_a_nilpotent_ideal() -> None:
    numbers = sa.analyze(sa.stabilizer([{(0, 0): 1}], 3, PRIME), PRIME, "parabolic")
    _same((numbers["dimension"], numbers["radical"], numbers["trace_form_nil_ideal"]), (7, 4, 2))
    _same((numbers["levi_type"], numbers["central_torus"], numbers["torus_rank"]), ("sl2", 2, 3))


def test_stabilizer_of_no_quadric_is_gl3() -> None:
    numbers = sa.analyze(sa.stabilizer([], 3, PRIME), PRIME, "gl3")
    _same((numbers["dimension"], numbers["levi_type"], numbers["torus_rank"]), (9, "sl3", 3))


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
