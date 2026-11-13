"""Equivariance of ker C_z under the census product of unipotent G_2 automorphisms; its failure for the boost."""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ATTACHMENTS = ROOT / "docs" / "evidence" / "a5-kernel-attachments"
sys.path.insert(0, str(ATTACHMENTS))

import kernel_equivariance as ke  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def test_original_coordinate_matrix_of_the_g2_element_is_complex_orthogonal() -> None:
    _, original = ke.g2_matrices()
    _same(ke.multiply_matrices(ke.kernel_lemma._transpose(original), original), ke.identity_matrix())


def test_the_census_g2_element_has_trace_12_and_is_therefore_not_unipotent() -> None:
    _, original = ke.g2_matrices()
    _same(sum((original[index][index][0] for index in range(ke.DIMENSION)), Fraction(0)), Fraction(12))
    _same(all(original[index][index][1] == 0 for index in range(ke.DIMENSION)), True)


def test_kernel_transport_holds_for_the_g2_element_and_fails_for_the_boost_at_vb() -> None:
    split_point = ke.regularity.REPS["VB"]
    _, g2_element = ke.g2_matrices()
    _, boost, _, _ = ke.boost_matrices()
    _same(ke.kernel_transport(split_point, g2_element), (7, 7, True, 7))
    _same(ke.kernel_transport(split_point, boost), (7, 7, False, 6))


def test_the_split_coordinate_matrix_moves_the_kernel_at_a_point_where_the_original_one_does_not() -> None:
    split_point = ke.regularity.REPS["Va+"]
    split, original = ke.g2_matrices()
    _same(ke.kernel_transport(split_point, original)[2], True)
    _same(ke.kernel_transport(split_point, split)[2], False)


def test_boost_matrix_has_the_prescribed_blocks_and_its_generator_swaps_the_halves() -> None:
    split, _, inverse, _ = ke.boost_matrices()
    cosh, sinh = ke.regularity.BOOST
    _same((split[0][0][0], split[0][8][0], split[7][7]), (cosh, sinh, ke.ONE))
    _same(inverse[0][8][0], -sinh)
    _same(ke.split_matrix_of_boost_generator()[3][11], ke.ONE)


def test_complex_span_membership_separates_a_member_from_a_nonmember() -> None:
    basis = [ke.identity_matrix(), ke.split_matrix_of_boost_generator()]
    scaled = tuple(tuple((Fraction(2) * a, Fraction(3) * b) for a, b in row) for row in ke.identity_matrix())
    _same(ke.in_complex_span(basis, scaled), True)
    _same(ke.in_complex_span([ke.identity_matrix()], ke.split_matrix_of_boost_generator()), False)


def test_self_test_rejects_a_failed_record_and_a_surviving_mutation() -> None:
    with pytest.raises(RuntimeError, match="failed"):
        ke._self_test({"pass": False, "mutation_control": {"detected": True}})
    with pytest.raises(RuntimeError, match="zero residual"):
        ke._self_test({"pass": True, "mutation_control": {"detected": False}})


@pytest.mark.audit
def test_retained_record_is_the_regenerated_record() -> None:
    record = ke.build_record()
    _same(record["pass"], True)
    _same(ke._record_bytes(record), (ATTACHMENTS / "kernel-equivariance-result.json").read_bytes())
