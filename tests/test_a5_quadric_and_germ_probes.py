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
    num_r = [k - a + u for k, a, u in zip(mod.NUM_K_E8, num_a, unit, strict=True)]
    for fiber, p, rel in mod.E8S:
        rows.append({"check": "e8-colon", "fiber": fiber, "prime": p, "relations": rel, "radical": [5, 1, 5, 11],
                     "square": [1], "colon": [4, 2, 17, 16, 1, 1], "bicolon": [1], "numK": list(mod.NUM_K_E8),
                     "numR": list(num_r), "numA": list(mod.NUM_A_E8)})  # fmt: skip
    rows += [mod.expected_map(item) for item in mod.MAPS]
    for fiber, p, rel in mod.E8S:
        parts = [
            {"projdim": dim, "degree": e, "linear": linear, "sections": sections(mod, e)}
            for dim, e, linear in ((4, 11, 9), (3, 4, 14))
        ]
        rows.append(
            {"check": "e8-primes", "fiber": fiber, "prime": p, "relations": rel, "primes": 2, "components": parts}
        )
    rows += [mod.expected_receipt(item) for item in mod.RECEIPTS]
    return rows


def row(rows: list[dict[str, Any]], kind: str, index: int = 0) -> dict[str, Any]:
    return [r for r in rows if r["check"] == kind][index]


def test_the_fixture_record_passes() -> None:
    mod = load("quadric_and_germ_probes")
    rows = probe_fixture(mod)
    if len(rows) != 38 or mod.check(rows):
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
    "a receipt of another rank": lambda rows: row(rows, "receipt").update(rank_h_d=52),
    "a receipt whose input is not the canonical header": lambda rows: row(rows, "receipt").update(input_matches=False),
    "a receipt with a membership failure": lambda rows: row(rows, "receipt")["membership"].update(failures=1),
    "a third-prime map with the coefficient of 32009": lambda rows: row(rows, "module-map", 8)["images"][1].__setitem__(
        1, "-10501*y(5)"
    ),
    "a module map with a two-dimensional solution space": lambda rows: row(rows, "module-map").update(solutions=[2]),
    "a control system with a solution": lambda rows: row(rows, "module-map", 5).update(control_solutions=[1]),
    "a singular module map": lambda rows: row(rows, "module-map").update(det_nonzero=[0]),
    "a changed image of the module map": lambda rows: row(rows, "module-map", 7)["images"][0].__setitem__(1, "y(7)"),
    "a radical not generated by its linear forms": lambda rows: row(rows, "module-map", 3).update(generation=[5, 0]),
    "an E8-bar prime without an F_p-point": lambda rows: [
        s.update(orbits=[11]) for s in row(rows, "e8-primes")["components"][0]["sections"].values()
    ],
    "an E8-bar prime of another degree": lambda rows: row(rows, "e8-primes", 2)["components"][1].update(degree=5),
    "a colon ideal with two minimal primes": lambda rows: row(rows, "e8-colon")["colon"].__setitem__(5, 2),
    "a radical with a sixth linear form": lambda rows: row(rows, "e8-colon")["radical"].__setitem__(0, 6),
    "a changed radical numerator": lambda rows: row(rows, "e8-colon", 3)["numR"].__setitem__(1, -4),
    "a quadric numerator replaced by a plane": lambda rows: row(rows, "e8-colon").update(numA=[1, -18, 153]),
    "numerators of K2 and its radical raised together in degree 8": lambda rows: [
        row(rows, "e8-colon")[k].__setitem__(8, row(rows, "e8-colon")[k][8] + 1) for k in ("numK", "numR")
    ],
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_a_changed_probe_record_is_reported(name: str) -> None:
    mod = load("quadric_and_germ_probes")
    rows = probe_fixture(mod)
    MUTATIONS[name](rows)
    if not mod.check(rows):
        raise AssertionError(f"{name}: the changed record passes")


def test_the_map_coefficient_is_two_over_the_root_of_minus_one_in_the_symmetric_range() -> None:
    mod = load("quadric_and_germ_probes")
    values = {p: 2 * pow(root, -1, p) % p for p, root in mod.ROOT_OF_MINUS_ONE.items()}
    if values != {32009: 10501, 32029: 13799, 32057: 15939}:
        raise AssertionError(values)
    if [mod.term(-3, 2, 7, True), mod.term(4, 5, 7), mod.term(1, 1, 7), mod.term(6, 3, 7, True)] != [
        "-3*y(2)",
        "-3*y(5)",
        "+y(1)",
        "-y(3)",
    ]:
        raise AssertionError("terms print in the symmetric range with a unit coefficient omitted")


def test_the_hilbert_function_of_a_numerator_expands_exactly() -> None:
    mod = load("quadric_and_germ_probes")
    if mod.hilbert_function([1, 0, -1], 3, range(5)) != [1, 3, 5, 7, 9]:
        raise AssertionError("the plane conic k[x, y, z]/(q) has Hilbert function 2d + 1")
    if mod.hilbert_function(mod.NUM_K_E8, 21, range(1, 8)) != mod.HF_E8:
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


def skew_form(mod: ModuleType, wedges: list[tuple[list[int], list[int]]]) -> list[list[int]]:
    """The 9 x 9 matrix of a sum of wedges u ^ v of covectors."""
    n = mod.cls.KERNEL_DIMENSION
    return [[sum(u[a] * v[b] - u[b] * v[a] for u, v in wedges) for b in range(n)] for a in range(n)]


def test_containment_conditions_vanish_on_a_contained_kernel_and_not_on_a_transverse_one() -> None:
    """ker T lies in ker S exactly when S is a two-form on the row space of T.

    T = u1 ^ u2 + u3 ^ u4 has rank four with mixed-sign principal Pfaffians; S = (u1 + u3) ^ (u2 - u4) lives on its
    row space and S' = u1 ^ e5 does not. flag_rows must return zero rows for S, nonzero rows for S', and as many
    nonzero rows as wedge_residual of composed_limit_sections.py counts.
    """
    mod = load("embedded_plane_images")
    p, cls = 32009, mod.cls
    u1, u2 = [1, 0, 0, 0, 1, 0, 0, 0, 0], [0, 1, 0, 0, 0, 1, 1, 0, 0]
    u3, u4 = [0, 0, 1, 0, 0, 0, 0, -1, 0], [0, 0, 0, 1, 0, 0, 0, 0, 2]
    e5 = [0, 0, 0, 0, 1, 0, 0, 0, 0]
    t = skew_form(mod, [(u1, u2), (u3, u4)])
    pfaffians = [t[a][b] * t[c][d] - t[a][c] * t[b][d] + t[a][d] * t[b][c] for a, b, c, d in cls.QUADS]
    if len({x for x in pfaffians if x}) < 3 or min(pfaffians) >= 0:
        raise AssertionError("the fixture needs Pfaffians of both signs")
    embedding = [[x % p] for x in pfaffians]
    plus = [x + y for x, y in zip(u1, u3, strict=True)]
    minus = [x - y for x, y in zip(u2, u4, strict=True)]
    for wedges, contained in (([(plus, minus)], True), ([(u1, e5)], False)):
        form = skew_form(mod, wedges)
        entries = [form[a][b] for a, b in cls.PAIRS]
        nonzero = sum(any(row) for row in mod.flag_rows(entries, embedding, p))
        if (nonzero == 0) != contained or nonzero != cls.wedge_residual(form, pfaffians):
            raise AssertionError((contained, nonzero, cls.wedge_residual(form, pfaffians)))


def test_a_form_that_is_not_a_sum_of_signed_variables_is_rejected() -> None:
    mod = load("embedded_plane_images")
    if mod.form_row("y(3)-y(10)", 15, 7)[2:10] != [1, 0, 0, 0, 0, 0, 0, 6]:
        raise AssertionError(mod.form_row("y(3)-y(10)", 15, 7))
    with pytest.raises(ValueError, match="not a sum"):
        mod.form_row("2*y(3)", 15, 7)
