"""The checks of the germ, quadric and plane-image records of the A_5 fiber track, on fixtures built here.

A fixture is a record as the scripts write it, assembled from each module's tables and constants; check() accepts
it and reports every copy that drops, relabels or alters a row. The retained records replay on demand through the
gates core-a5-quadric-and-germ-probes and core-a5-embedded-plane-images of ci/gates.json.
"""

import copy
import importlib.util
from fractions import Fraction
from math import comb
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

HERE = Path(__file__).resolve().parents[1] / "docs/evidence/a5-exceptional-fibers/structure"
# The first Hilbert numerator of the 148 quadrics of E8-bar -> N+- over (1 - t)^21.
NUM_K_E8 = [
    1,
    0,
    -148,
    1562,
    -8745,
    32753,
    -89936,
    190224,
    -319606,
    435500,
    -488280,
    454948,
    -354354,
    231126,
    -125840,
    56672,
    -20763,
    6028,
    -1332,
    210,
    -21,
    1,
]


def load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"a5_{name}", HERE / f"{name}.py")
    if spec is None or spec.loader is None:
        raise ImportError(name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sections(mod: ModuleType, degree: int) -> dict[str, Any]:
    point = {"projdim": 0, "degree": degree, "reduced": True, "orbits": [1, degree - 1]}
    return {str(base): dict(point) for base in mod.BASES}


def probe_fixture(mod: ModuleType) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [mod.expected_germ(item) for item in mod.GERMS]
    closed = {
        str(d): [7 * comb(d + 2, 3) + comb(d + 2, 2), 3 * comb(d + 2, 3) + comb(d + 2, 2),
                 4 * comb(d + 2, 3) + comb(d + 2, 2), comb(d + 2, 2)]
        for d in range(1, 8)
    }  # fmt: skip
    for p, rel in mod.VB:
        parts = [{"projdim": 3, "degree": e, "sections": sections(mod, e)} for e in (3, 4)]
        rows.append({"check": "vb-components", "fiber": "E8-bar -> VB", "prime": p, "relations": rel, "primes": 2,
                     "components": parts, "hf": copy.deepcopy(closed), "meet": dict(mod.MEET)})  # fmt: skip
    for fiber, p, rel in mod.XS:
        sign = "-" if fiber == "X- -> N-" else "+"
        rows.append({"check": "x-colon", "fiber": fiber, "prime": p, "relations": rel, "primes": [1],
                     "prime_ideal": [4, 12, 1], "colon": [3, 1, 12, 12, 1], "bicolon": [1],
                     "forms": [f.replace("SIGN", sign) for f in mod.PLANE_FORMS], "sections": sections(mod, 12),
                     "numK": list(mod.NUM_K), "numP": list(mod.NUM_P), "numA": list(mod.NUM_A)})  # fmt: skip
    unit = [(-1) ** i * comb(21, i) for i in range(22)]
    num_a = mod.NUM_A_E8 + [0] * (22 - len(mod.NUM_A_E8))
    num_r = [k - a + u for k, a, u in zip(NUM_K_E8, num_a, unit, strict=True)]
    for fiber, p, rel in mod.E8S:
        rows.append({"check": "e8-colon", "fiber": fiber, "prime": p, "relations": rel, "radical": [5, 1, 5, 11],
                     "square": [1], "colon": [4, 2, 17, 16, 1, 1], "bicolon": [1], "numK": list(NUM_K_E8),
                     "numR": list(num_r), "numA": list(mod.NUM_A_E8)})  # fmt: skip
    return rows


def row(rows: list[dict[str, Any]], kind: str, index: int = 0) -> dict[str, Any]:
    return [r for r in rows if r["check"] == kind][index]


def test_the_fixture_record_passes() -> None:
    mod = load("quadric_and_germ_probes")
    rows = probe_fixture(mod)
    if len(rows) != 21 or mod.check(rows):
        raise AssertionError(mod.check(rows))


def drop_pivot(rows: list[dict[str, Any]]) -> None:
    germ = row(rows, "germ-prime")
    germ["pivot"] = None
    del germ["pivot_in_J"]


def duplicate_a_germ(rows: list[dict[str, Any]]) -> None:
    rows[5] = dict(rows[4])


def drop_sections(rows: list[dict[str, Any]]) -> None:
    kept = row(rows, "vb-components")["components"][0]["sections"]
    for base in ("3", "4", "5"):
        del kept[base]


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
    rows = probe_fixture(mod)
    MUTATIONS[name](rows)
    if not mod.check(rows):
        raise AssertionError(f"{name}: the changed record passes")


def test_the_hilbert_function_of_a_numerator_expands_exactly() -> None:
    mod = load("quadric_and_germ_probes")
    if mod.hilbert_function([1, 0, -1], 3, range(5)) != [1, 3, 5, 7, 9]:
        raise AssertionError("the plane conic k[x, y, z]/(q) has Hilbert function 2d + 1")
    if mod.hilbert_function(NUM_K_E8, 21, range(1, 8)) != mod.HF_E8:
        raise AssertionError("the fixture numerator misses the retained Hilbert function")


def test_changed_plane_images_are_reported() -> None:
    mod = load("embedded_plane_images")
    if mod.check(copy.deepcopy(mod.EXPECTED)):
        raise AssertionError(mod.check(mod.EXPECTED))
    meeting = copy.deepcopy(mod.EXPECTED)
    meeting[0]["ranks"] = [15, 3, 17]
    outside = copy.deepcopy(mod.EXPECTED)
    outside[2]["Va"]["with_forms"] = 13
    shared = copy.deepcopy(mod.EXPECTED)
    shared[3]["Va"]["on_opposite"] = 2
    if not all(mod.check(rows) for rows in (meeting, outside, shared, outside[:-1])):
        raise AssertionError("a changed plane record passes")


def test_exact_ranks_and_kernels_on_small_matrices() -> None:
    mod = load("embedded_plane_images")
    one, zero, i = (Fraction(1), Fraction(0)), (Fraction(0), Fraction(0)), (Fraction(0), Fraction(1))
    minus = (Fraction(-1), Fraction(0))
    if mod.rank_gauss([[one, i], [i, minus]]) != 1 or mod.rank_gauss([[one, i], [i, one]]) != 2:
        raise AssertionError("(1, i) and (i, -1) are proportional over Q(i); (1, i) and (i, 1) are independent")
    if mod.rank_gauss([[zero, zero]]) != 0 or mod.rank_mod([[1, 2, 3], [2, 4, 6], [0, 1, 1]], 7) != 2:
        raise AssertionError("rank")
    kernel = mod.kernel_mod([[1, 0, 6], [0, 1, 6]], 3, 7)
    if kernel != [[1, 1, 1]]:
        raise AssertionError(kernel)


def test_a_form_that_is_not_a_sum_of_signed_variables_is_rejected() -> None:
    mod = load("embedded_plane_images")
    if mod.form_row("y(3)-y(10)", 15, 7)[2:10] != [1, 0, 0, 0, 0, 0, 0, 6]:
        raise AssertionError(mod.form_row("y(3)-y(10)", 15, 7))
    with pytest.raises(ValueError, match="not a sum"):
        mod.form_row("2*y(3)", 15, 7)
