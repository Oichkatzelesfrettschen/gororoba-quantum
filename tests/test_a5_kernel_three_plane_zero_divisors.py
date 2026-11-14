"""Higher zero divisors of the kernel three-plane: the line certificate, the point rows and the record rules."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles-residuals"))

import kernel_three_plane_zero_divisors as locus  # noqa: E402
from nullity4_gauss_image import Points, _block, _flint, _twist  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _fixture(number: int) -> tuple[int, list[int]]:
    for fixture, _, split in locus._fixture_splits():
        if fixture == number:
            return fixture, split
    raise AssertionError(f"no fixture {number}")


def _kernel_quartic(split: list[int]) -> list[int]:
    reduced = [value % locus.PRIME for value in split]
    _, split_basis = locus.kernel_three_plane(reduced)
    return locus.restrict_to_kernel(locus._hypersurfaces()["G"], split_basis, 4)


def test_pfaffian_squares_to_the_determinant() -> None:
    points = Points("test:pfaffian")
    size = 8
    matrix = [[0] * size for _ in range(size)]
    for row in range(size):
        for column in range(row + 1, size):
            matrix[row][column] = points.value()
            matrix[column][row] = -matrix[row][column] % locus.PRIME
    _same(locus._pfaffian(matrix) ** 2 % locus.PRIME, int(_flint(matrix).det()) % locus.PRIME)


def test_principal_pfaffian_of_the_block_is_the_product_of_the_hypersurfaces() -> None:
    # Deleting row and column j of M(t) leaves a 14 x 14 skew matrix with Pfaffian (-1)^j Q(t') G(t') t_j.
    polynomials = locus._hypersurfaces()
    for number in range(3):
        split = Points(f"test:identity:{number}").vector()
        frame = _twist(split, locus.ROOT_OF_MINUS_ONE)
        block = _block(frame)
        product = locus._value(polynomials["Q"], split) * locus._value(polynomials["G"], split) % locus.PRIME
        for removed in range(locus.IMAGINARY):
            keep = [index for index in range(locus.IMAGINARY) if index != removed]
            pfaffian = locus._pfaffian([[block[a][b] for b in keep] for a in keep])
            _same(pfaffian, (-1) ** removed * product * frame[removed] % locus.PRIME)


def test_interpolated_restriction_reproduces_the_hypersurfaces_on_the_three_plane() -> None:
    polynomials = locus._hypersurfaces()
    _, split = _fixture(13)
    reduced = [value % locus.PRIME for value in split]
    basis, split_basis = locus.kernel_three_plane(reduced)
    quartic = locus.restrict_to_kernel(polynomials["G"], split_basis, 4)
    _same(any(locus.restrict_to_kernel(polynomials["Q"], split_basis, 2)), False)
    for coefficients in ((2, 3, 5), (1, 0, 7), (11, 13, 17)):
        value = locus._value(polynomials["G"], locus._combination(split_basis, coefficients))
        found = sum(c * m for c, m in zip(quartic, locus._monomial_values(coefficients, 4), strict=True)) % locus.PRIME
        _same(found, value)
        _same(locus.nullity(locus._combination(basis, coefficients)) >= 3, True)


def test_certificate_passes_quartics_without_a_line_and_rejects_quartics_with_one() -> None:
    found = locus.calibration()
    _same(found, locus.CALIBRATION)
    _same(
        {name: locus.line_free(certificate) for name, certificate in found.items()},
        {
            "three_nodal_quartic": True,
            "conic_times_conic": True,
            "tangent_conics": True,
            "line_times_cubic": False,
            "two_lines_times_conic": False,
            "double_line_times_conic": False,
        },
    )


def test_certificate_on_the_quartic_of_a_fixture_and_on_that_quartic_with_a_line_attached() -> None:
    _, split = _fixture(13)
    quartic = _kernel_quartic(split)
    _same([locus.hilbert_function(quartic, degree) for degree in range(3, 9)], [7, 6, 3, 3, 3, 3])
    _same(locus.quartic_line_certificate(quartic), {"singular_scheme_length": 3, "trisecant_hilbert_value": 0})
    # A partial derivative of the quartic is a cubic; the line a + 3 b + 5 c times it is a quartic with a line.
    cubic = [0] * len(locus._monomials(3))
    for monomial, coefficient in locus._jacobian_ideal(quartic)[0].items():
        cubic[locus._monomials(3).index(monomial)] = coefficient
    linear = locus._form({(1, 0, 0): 1, (0, 1, 0): 3, (0, 0, 1): 5}, 1)
    certificate = locus.quartic_line_certificate(locus._form_product(linear, 1, cubic, 3))
    _same(locus.line_free(certificate), False)


def _exchange(rows: list[dict[str, object]], first: int, second: int) -> None:
    """Exchange every field but the fixture number between two rows."""
    numbers = rows[first]["fixture"], rows[second]["fixture"]
    rows[first], rows[second] = dict(rows[second]), dict(rows[first])
    rows[first]["fixture"], rows[second]["fixture"] = numbers


def test_rows_at_exact_fixtures_of_the_two_strata() -> None:
    number, split = _fixture(13)
    row = locus.quadric_fixture((number, split))
    _same(
        row,
        {
            "fixture": 13,
            "quadric_gram_rank": 0,
            "quartic_nonzero": True,
            "singular_scheme_length": 3,
            "trisecant_hilbert_value": 0,
            "pfaffian_forms": 91,
            "pfaffian_span_rank": 6,
            "quartic_multiples_rank": 6,
            "union_rank": 6,
        },
    )
    found = {}
    for fixture in (0, 1, 29):
        row = locus.quartic_fixture(_fixture(fixture))
        exact = row["exact_polar_line"]
        found[fixture] = (
            row["quadric_gram_rank"],
            row["quartic_zero_probes"],
            row["polar_line_dimension"],
            sorted(set(row["line_nullities"])),
            row["off_line_nullity"],
            row["plane_equals_line"],
            row["fiber_dimension"],
            row["exact_fiber_dimension"],
            sorted(set(exact["line_ranks"])),
            exact["off_line_rank"],
        )
    _same(
        found,
        {
            0: (1, 16, 2, [7], 3, True, 6, 6, [8], 12),
            1: (1, 16, 2, [9], 3, True, 12, 12, [6], 12),
            29: (1, 16, 2, [9], 3, False, 2, 2, [6], 12),
        },
    )


def test_rows_at_grid_points_with_a_long_singular_scheme_and_a_plane_on_the_line() -> None:
    # The quartic G|_K at this point has a singular scheme of length 5, and the trisecant ideal is the whole ring.
    long_scheme = locus.quadric_point([1, 1, 2, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0, 0])
    _same(
        long_scheme,
        {
            "quadric_gram_rank": 0,
            "quartic_nonzero": True,
            "singular_scheme_length": 5,
            "trisecant_hilbert_value": 0,
        },
    )
    # P = l_z with dim L = 2 and nullity 7 on the polar line.
    row = locus.quartic_point(locus.PLANE_ON_LINE_POINTS[0])
    _same(
        (row["line_nullities"], row["plane_equals_line"], row["fiber_dimension"], row["off_line_nullity"]),
        ([7] * 6, True, 2, 3),
    )


def test_grid_block_of_both_strata_carries_its_classes() -> None:
    block = locus.grid_block((1, 0, 0))
    _same(
        (block["candidates"], block["excluded"], block["quartic_classes"], block["quadric_classes"]),
        (1156, 24, {(9, True, 12): 12, (9, False, 2): 72}, {(0, True, 3, 0): 46}),
    )


def test_grid_block_with_the_singular_schemes_of_length_five() -> None:
    block = locus.grid_block((1, 2, 1))
    _same(block["quadric_classes"].get((0, True, 5, 0)), 32)
    _same(len(block["long_scheme_points"]), 32)


def test_grid_block_with_the_kernel_planes_on_the_polar_line() -> None:
    block = locus.grid_block((0, 1, 1))
    _same([tuple(row["split_point"]) for row in block["plane_on_line"]], list(locus.PLANE_ON_LINE_POINTS))


def test_retained_record_passes_its_rules_and_each_mutation_fails_them(monkeypatch: pytest.MonkeyPatch) -> None:
    record = json.loads(locus.RECORD.read_text(encoding="utf-8"))
    # The digests of the live source files are compared by the on-demand replay gate; here the rule that compares
    # them is exercised against a fixed copy, so an edit of an input file leaves the required test lane green.
    retained_inputs = dict(record["inputs"])
    monkeypatch.setattr(locus, "_inputs", lambda: dict(retained_inputs))
    _same((record["pass"], locus.verdict(record)), (True, []))
    _same(
        (len(record["fixtures"]["quadric_stratum"]), len(record["fixtures"]["quartic_stratum"])),
        (12, 52),
    )
    quadric, quartic = "quadric_stratum", "quartic_stratum"
    quadric_name, quartic_name = locus.QUADRIC, locus.QUARTIC
    changes: dict[str, Callable[[dict[str, Any]], Any]] = {
        "field": lambda r: r.update(field="GF(2)"),
        "inputs": lambda r: r.update(inputs={}),
        "one input digest": lambda r: r["inputs"].update({next(iter(r["inputs"])): "0" * 64}),
        "stated failure": lambda r: r.update({"pass": False}),
        "probe rank": lambda r: r["quartic_probes"].update(monomial_rank=14),
        "probe points": lambda r: r["quartic_probes"].update(points=15),
        "calibration entry": lambda r: r["calibration"]["line_times_cubic"].update(trisecant_hilbert_value=0),
        "calibration of a quartic without a line": lambda r: r["calibration"]["three_nodal_quartic"].update(
            trisecant_hilbert_value=1
        ),
        "calibration of a quartic with a line passes": lambda r: r["calibration"]["two_lines_times_conic"].update(
            trisecant_hilbert_value=0
        ),
        "stratum counts": lambda r: r["fixtures"]["stratum_counts"].update({locus.QUADRIC: 11}),
        "quadric fixture": lambda r: r["fixtures"][quadric][0].update(fixture=0),
        "quadric gram": lambda r: r["fixtures"][quadric][1].update(quadric_gram_rank=1),
        "quartic vanishes": lambda r: r["fixtures"][quadric][2].update(quartic_nonzero=False),
        "no certificate": lambda r: r["fixtures"][quadric][3].update(singular_scheme_length=None),
        "other length": lambda r: r["fixtures"][quadric][4].update(singular_scheme_length=4),
        "trisecant ideal": lambda r: r["fixtures"][quadric][5].update(trisecant_hilbert_value=1),
        "pfaffian count": lambda r: r["fixtures"][quadric][6].update(pfaffian_forms=90),
        "pfaffian span": lambda r: r["fixtures"][quadric][7].update(pfaffian_span_rank=5),
        "pfaffian multiples": lambda r: r["fixtures"][quadric][8].update(quartic_multiples_rank=7),
        "pfaffian union": lambda r: r["fixtures"][quadric][9].update(union_rank=7),
        "sampled class": lambda r: r["sampled_points"][quartic_name][0].__setitem__(0, 2),
        "sampled count": lambda r: r["sampled_points"][quadric_name][0].__setitem__(4, 39),
        "sampled line": lambda r: r["sampled_points"][quadric_name][0].__setitem__(3, 1),
        "quartic pfaffian span": lambda r: r["fixtures"][quartic][1].update(pfaffian_span_rank=5),
        "quartic pfaffian union": lambda r: r["fixtures"][quartic][2].update(union_rank=7),
        "exchanged fixture classes": lambda r: _exchange(r["fixtures"][quartic], 0, 23),
        "calibration of tangent conics": lambda r: r["calibration"]["tangent_conics"].update(trisecant_hilbert_value=1),
        "quartic fixture": lambda r: r["fixtures"][quartic][0].update(fixture=1),
        "quartic gram": lambda r: r["fixtures"][quartic][3].update(quadric_gram_rank=2),
        "probe zeros": lambda r: r["fixtures"][quartic][4].update(quartic_zero_probes=15),
        "polar line": lambda r: r["fixtures"][quartic][5].update(polar_line_dimension=3),
        "mixed nullities": lambda r: r["fixtures"][quartic][6].update(line_nullities=[7, 7, 7, 7, 7, 9]),
        "nullity 5": lambda r: r["fixtures"][quartic][7].update(line_nullities=[5] * 6),
        "short nullities": lambda r: r["fixtures"][quartic][8].update(line_nullities=[7] * 5),
        "off-line nullity": lambda r: r["fixtures"][quartic][9].update(off_line_nullity=5),
        "exact line rank": lambda r: r["fixtures"][quartic][10]["exact_polar_line"]["line_ranks"].__setitem__(0, 7),
        "exact off-line rank": lambda r: r["fixtures"][quartic][11]["exact_polar_line"].update(off_line_rank=10),
        "exact kernel": lambda r: r["fixtures"][quartic][12]["exact_polar_line"].update(kernel_dimension=4),
        "exact lower block": lambda r: r["fixtures"][quartic][13]["exact_polar_line"].update(rank_lower_block=13),
        "modular dim L": lambda r: r["fixtures"][quartic][14].update(fiber_dimension=3),
        "exact dim L": lambda r: r["fixtures"][quartic][0].update(exact_fiber_dimension=3, fiber_dimension=3),
        "plane on the line": lambda r: r["fixtures"][quartic][15].update(
            plane_equals_line=not r["fixtures"][quartic][15]["plane_equals_line"]
        ),
        "candidates": lambda r: r["grid"].update(candidates=41615),
        "excluded points": lambda r: r["grid"].update(excluded_stratum_points=387),
        "quartic class count": lambda r: r["grid"]["quartic_classes"][0].__setitem__(3, 363),
        "quartic class dropped": lambda r: r["grid"].update(quartic_classes=r["grid"]["quartic_classes"][1:]),
        "dim L above 2 off the line": lambda r: r["grid"]["quartic_classes"].append([7, False, 6, 1]),
        "quartic invariants": lambda r: r["grid"]["quartic_invariants"][0].__setitem__(4, 1202),
        "quartic invariants split": lambda r: r["grid"]["quartic_invariants"].append([1, 15, 2, 3, 1]),
        "quadric class count": lambda r: r["grid"]["quadric_classes"][0].__setitem__(4, 2063),
        "quadric trisecant ideal": lambda r: r["grid"]["quadric_classes"][0].__setitem__(3, 1),
        "quadric without certificate": lambda r: r["grid"]["quadric_classes"][1].__setitem__(2, None),
        "quadric gram on the grid": lambda r: r["grid"]["quadric_classes"][0].__setitem__(0, 1),
        "long scheme point": lambda r: r["grid"]["long_scheme_points"][0].__setitem__(0, 2),
        "long scheme dropped": lambda r: r["grid"]["long_scheme_points"].pop(),
        "plane on the line nullity": lambda r: r["grid"]["plane_on_line"][0].update(line_nullity=9),
        "plane on the line point": lambda r: r["grid"]["plane_on_line"][1].update(split_point=[0] * 15),
        "plane on the line repeated": lambda r: r["grid"]["plane_on_line"][2].update(
            split_point=r["grid"]["plane_on_line"][0]["split_point"]
        ),
        "plane on the line dropped": lambda r: r["grid"].update(plane_on_line=r["grid"]["plane_on_line"][1:]),
    }
    for name, change in changes.items():
        mutated = json.loads(json.dumps(record))
        change(mutated)
        if locus.verdict(mutated) == []:
            raise AssertionError(f"a record mutated at {name} passes")


def test_replay_comparison_separates_a_boolean_from_an_integer() -> None:
    # True == 1 in Python, so a comparison of parsed records accepts either; the replay compares the retained text.
    _same({"plane_equals_line": True} == {"plane_equals_line": 1}, True)
    _same(locus._serialized({"plane_equals_line": True}) == locus._serialized({"plane_equals_line": 1}), False)
