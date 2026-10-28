"""Contracts of the exact checks behind docs/notes/topics/reference-corpus-falsification.md."""

from __future__ import annotations

import pytest
import reference_corpus_checks as checks


def test_albert_algebra_derivations_are_f4_and_structure_algebra_is_e6() -> None:
    result = checks.albert_algebra(cross_check=True)
    if result["der_dimension"] != 52 or result["reduced_structure_dimension"] != 78:
        raise AssertionError(f"Albert algebra symmetry dimensions {result}")
    if result["pairs_cross_checked_with_albert_algebra_py"] != 729:
        raise AssertionError("the Jordan table was not compared with albert_algebra.py on every basis pair")


def test_e8_roots_are_the_eight_dimensional_gosset_vertices() -> None:
    result = checks.e8_structure()
    if result["span_rank"] != 8 or result["gosset_421_edges"] != 6720:
        raise AssertionError(f"E8 structure {result}")


def test_su5_grouping_of_the_corpus_fails_dimension_count() -> None:
    result = checks.su5_assignments()
    if result["corpus"] != {"10": 8, "5bar": 7} or not result["same_state_set"]:
        raise AssertionError(f"SU(5) grouping {result}")


def test_octonion_left_multiplication_generates_cl8_and_sedenions_fail_on_42_pairs() -> None:
    if checks.clifford_from_left_multiplication(8)["pairs_failing_clifford"] != 0:
        raise AssertionError("octonion gammas fail Cl(8)")
    if checks.clifford_from_left_multiplication(16)["pairs_failing_clifford"] != 42:
        raise AssertionError("sedenion Clifford failures differ from the 42 zero-divisor index pairs")
    if checks.d4_diagram_symmetries() != 6:
        raise AssertionError("D4 diagram symmetry group is not S3")


def test_sugawara_central_charge_and_pairing_sign() -> None:
    result = checks.sugawara_su2()
    if result["central_charge"] != "3*K/(K + 1)":
        raise AssertionError(f"Sugawara central charge {result['central_charge']}")
    pairing = result["bilinear_pairing_word_vs_state"]
    if not isinstance(pairing, list) or pairing[0] == pairing[1]:
        raise AssertionError("the bilinear pairing no longer shows its sign contradiction")


def test_coulomb_gas_reproduces_the_kac_table() -> None:
    if checks.coulomb_gas()["c"] != "1 - 12 Q^2":
        raise AssertionError("Feigin-Fuchs central charge")


@pytest.mark.parametrize("level", [1, 2, 3, 4])
def test_kac_determinant_and_constant(level: int) -> None:
    result = checks.kac_determinant(level)
    if level == 2 and result["K_N"] != 32:
        raise AssertionError(f"K_2 = {result['K_N']}")


@pytest.mark.audit
def test_kac_determinant_level_five() -> None:
    if checks.kac_determinant(5)["K_N"] != 8697308774400:
        raise AssertionError("K_5 changed")


def test_small_identities_and_physical_orders() -> None:
    checks.sl2_brackets()
    checks.e8_branchings()
    checks.level_two_ising()
    if checks.linfinity_counterexample()["jacobiator_e0_e1_e2"] != [1, 0, 0]:
        raise AssertionError("L-infinity counterexample Jacobiator")
    if checks.virasoro_cocycle(window=4) != 9**3:
        raise AssertionError("Virasoro cocycle window")
    physics = checks.physics()
    if not 6e34 < physics["zpe_higgs_over_corpus"] < 7e34:
        raise AssertionError(f"Higgs-cutoff zero-point ratio {physics['zpe_higgs_over_corpus']}")
