"""Composed-limit sections: the containment equations, a section on a small fiber and the pass rule of a chain."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ATTACHMENTS = ROOT / "docs" / "evidence" / "a5-kernel-attachments"
sys.path.insert(0, str(ATTACHMENTS))

import composed_limit_sections as cl  # noqa: E402

RECORD = ATTACHMENTS / "composed-limit-sections-result.json"


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def test_the_containment_equations_vanish_on_a_contained_plane_and_on_no_other() -> None:
    control = cl.convention_control()
    _same(control["contained_plane_nonzero_coefficients"], 0)
    _same(control["plane_sharing_one_covector_nonzero_coefficients"] > 0, True)
    _same(control["transverse_plane_nonzero_coefficients"] > 0, True)
    _same(control["detected"], True)


def test_gaussian_reduction_sends_i_to_the_root() -> None:
    _same(cl.reduce_gaussian(["0", "1"], 32009, 10754), 10754)
    _same(cl.reduce_gaussian(["-1", "0"], 32009, 10754), 32008)
    _same(cl.reduce_gaussian(["1/2", "-1"], 32009, 10754), (16005 - 10754) % 32009)
    _same(cl.reduce_gaussian(["0", "1"], 32009, 10754) ** 2 % 32009, 32008)


def test_flag_equations_of_a_coordinate_form_select_the_pfaffians_through_its_two_indices() -> None:
    # S_0 = f^0 ^ f^1 and pi = y1 f^0^f^1^f^2^f^3 + y2 f^2^f^3^f^4^f^5: only the second lies outside {f^0, f^1}.
    form = [0] * len(cl.PAIRS)
    form[cl.PAIRS.index((0, 1))] = 1
    embedding = [[0, 0] for _ in cl.QUADS]
    embedding[cl.QUAD_INDEX[(0, 1, 2, 3)]] = [1, 0]
    embedding[cl.QUAD_INDEX[(2, 3, 4, 5)]] = [0, 1]
    equations = cl.flag_equations(form, embedding, ("y1", "y2"))
    _same(equations != [], True)
    _same(any("y1" in equation for equation in equations), False)
    _same(all("y2" in equation for equation in equations), True)


def test_the_pass_rule_compares_reduced_components_and_the_section_degree() -> None:
    section = {
        "linear_conditions": 9,
        "section_projective_dimension": 2,
        "section_degree": 2,
        "reduced_degree": 1,
        "components_projective_dimension_degree": [[2, 1]],
    }
    expected = {"reduced_components": [[2, 1]], "section_degree": 2}
    chain = {"expected_through_one_point_stratum": expected, "points": [{"section": section}]}
    _same(cl.chain_passes(chain), True)
    _same(cl.chain_passes({**chain, "points": [{"section": {**section, "section_degree": 1}}]}), False)
    two = {**section, "components_projective_dimension_degree": [[2, 1], [2, 1]]}
    _same(cl.chain_passes({**chain, "points": [{"section": two}]}), False)
    empty = {**section, "section_projective_dimension": -1}
    _same(cl.chain_passes({"expected_through_one_point_stratum": None, "points": [{"section": empty}]}), False)


def test_the_retained_record_reproduces_each_fiber_over_vb_and_one_double_plane_over_va() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    _same((record["pass"], record["summary"]["sections_agree_between_the_primes"]), (True, True))
    _same((record["summary"]["chain_count"], record["summary"]["section_count"]), (41, 136))
    through_vb = {
        (chain["prime"], chain["source"]): chain["points"][0]["section"]["components_projective_dimension_degree"]
        for chain in record["chains"]
        if chain["through"].startswith("VB->")
    }
    _same(through_vb[(32009, "Iso->N+")], [[3, 1]])
    _same(through_vb[(32009, "W8->N-")], [[4, 1]])
    _same(through_vb[(32029, "X+->N+")], [[2, 1]])
    _same(through_vb[(32009, "E8bar->N+")], [[3, 3], [3, 4]])
    _same(through_vb[(32029, "E8bar->N-")], [[3, 3], [3, 4]])
    for chain in record["chains"]:
        _same(cl.chain_passes(chain), True)
        if chain["through"].startswith("Va"):
            section = chain["points"][0]["section"]
            _same((section["section_degree"], section["reduced_degree"]), (2, 1))


def test_self_test_rejects_a_failed_record_and_a_surviving_mutation() -> None:
    with pytest.raises(RuntimeError, match="failed"):
        cl._self_test({"pass": False, "mutation_control": {"detected": True}})
    with pytest.raises(RuntimeError, match="outside"):
        cl._self_test({"pass": True, "mutation_control": {"detected": False}})


@pytest.mark.audit
def test_the_retained_record_regenerates_byte_for_byte() -> None:
    _same(cl._record_bytes(cl.build_record()), RECORD.read_bytes())
