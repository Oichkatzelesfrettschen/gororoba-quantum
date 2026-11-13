"""Quadric scheme of E8bar->VB along the boost: the Hilbert function helper and the record rules."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-attachments"))

import boost_e8_vb_quadrics as boost  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def test_hilbert_function_from_the_first_numerator() -> None:
    # The polynomial ring in 10 variables, then the quadric ring of the record: 1, 10, 55 - 21, 220 - 210 + 70.
    _same([boost.quadric_ring_hilbert([1], 10, degree) for degree in range(4)], [1, 10, 55, 220])
    found = [boost.quadric_ring_hilbert(boost.FIRST_NUMERATOR, boost.GENERATORS, degree) for degree in range(4)]
    _same(found, [1, 10, 34, 80])


def test_the_four_boosts_lie_on_the_hyperbola_and_start_at_the_identity() -> None:
    _same([cosh * cosh - sinh * sinh for cosh, sinh in boost.BOOSTS], [1, 1, 1, 1])
    _same((boost.BOOSTS[0], boost.DEGREE_THREE_BOOST != boost.BOOSTS[0]), ((1, 0), True))


def test_normal_form_follows_a_linear_change_of_the_generators() -> None:
    # y1 y2 under the swap of the first two generators is itself; under y1 = w1 + w2, y2 = w2 it is w1 w2 + w2^2.
    identity = [[int(i == j) for j in range(boost.GENERATORS)] for i in range(boost.GENERATORS)]
    shear = [list(row) for row in identity]
    shear[0][1] = 1
    quadric = [{(0, 1): 1}]
    plain, sheared = boost.normal_form(quadric, identity), boost.normal_form(quadric, shear)
    _same([(index, value) for index, value in enumerate(plain[0]) if value], [(1, 1)])
    _same([(index, value) for index, value in enumerate(sheared[0]) if value], [(1, 1), (boost.GENERATORS, 1)])


def test_adapted_frame_reads_its_scalars_and_is_invertible() -> None:
    quadrics = [{(6, 9): 1, (0, 6): 5}, {(6, 8): 1, (4, 6): 7}, {(5, 6): 1, (0, 6): 14}]
    scalars, matrix = boost.adapted_frame(quadrics)
    _same(scalars, {"a": 5, "b": 7, "d": 14})
    _same((len(matrix), matrix[0][7], matrix[9][3], matrix[9][7]), (10, 1, 1, boost.PRIME - 5))


def test_retained_record_passes_its_rules_and_each_mutation_fails_them() -> None:
    record = json.loads(boost.RECORD.read_text(encoding="utf-8"))
    _same((record["pass"], boost.verdict(record), len(record["basepoints"])), (True, [], 4))
    changes: dict[str, Callable[[dict[str, Any]], Any]] = {
        "generators": lambda r: r["basepoints"][1].update(generators=9),
        "relations": lambda r: r["basepoints"][2].update(relations=20),
        "numerator": lambda r: r["basepoints"][3].update(first_numerator=[1, 0, -20]),
        "primes": lambda r: r["basepoints"][1].update(minimal_primes=[[4, 7]]),
        "radical": lambda r: r["basepoints"][2].update(radical=False),
        "symmetry": lambda r: r["basepoints"][3].update(symmetry_algebra_dimension=14),
        "orbit": lambda r: r["basepoints"][1]["transversality"].update(orbit_dimension=6),
        "slice": lambda r: r["basepoints"][1]["transversality"].update(rank_of_orbit_tangent_with_slice=14),
        "retained": lambda r: r["basepoints"][0].update(equals_retained_k2=False),
        "dimension": lambda r: r["basepoints"][1].update(affine_dimension=3),
        "multiplicity": lambda r: r["basepoints"][2].update(multiplicity=6),
        "saturated": lambda r: r["basepoints"][3].update(saturated=False),
        "products": lambda r: r["basepoints"][1].update(products=54),
        "slice dimension": lambda r: r["basepoints"][1]["transversality"].update(slice_dimension=7),
        "closure": lambda r: r["basepoints"][2]["transversality"].update(closure_membership="000000000000"),
        "field": lambda r: r.update(field="GF(2)"),
        "incidence": lambda r: r.update(incidence="E8->VB"),
        "same input": lambda r: r["basepoints"][1].update(moved_input_sha256=r["basepoints"][0]["moved_input_sha256"]),
        "normal form": lambda r: r["basepoints"][2].update(normal_form_sha256="0" * 64),
        "void control": lambda r: r["basepoints"][3].update(
            normal_form_in_retained_frame_sha256=r["basepoints"][0]["normal_form_sha256"]
        ),
        "retained frame": lambda r: r["basepoints"][0].update(normal_form_in_retained_frame_sha256="0" * 64),
        "degree three relations": lambda r: r["degree_three"].update(relations=139),
        "degree three products": lambda r: r["degree_three"].update(products=219),
        "coherent degree three": lambda r: r["degree_three"].update(relations=139, h_3=81, quadric_ring_h_3=81),
        "missing basepoint": lambda r: r.update(basepoints=r["basepoints"][:3]),
        "degree three": lambda r: r["degree_three"].update(h_3=79),
        "degree three boost": lambda r: r["degree_three"].update(boost=["1", "0"]),
    }
    for name, change in changes.items():
        mutated = json.loads(json.dumps(record))
        change(mutated)
        if boost.verdict(mutated) == []:
            raise AssertionError(f"a record mutated at {name} passes")
