"""Contracts of the checks behind the persona-corpus verified results, their run designs and the earlier notes."""

from __future__ import annotations

import persona_corpus_checks as claims
import pytest


def test_e8_root_system_and_4_21_are_eight_dimensional() -> None:
    result = claims.e8_structure()
    if result["inner_product_with_negative"] != -2 or result["affine_dimension_4_21"] != 8:
        raise AssertionError("E8 root facts changed")
    if result["d4xd4_root_split"] != [24, 24, 64, 64, 64]:
        raise AssertionError("the triality-symmetric root split changed")


@pytest.mark.parametrize(("dim", "expected"), [(1, (3, 8)), (2, (8, 16)), (4, (21, 35))])
def test_magic_square_rows_on_small_jordan_algebras(dim: int, expected: tuple[int, int]) -> None:
    row = claims.jordan_symmetry_dimensions(dim)
    if (row["derivation_dimension"], row["norm_preserving_dimension"]) != expected:
        raise AssertionError(f"H3 over dimension {dim}: {row}")


@pytest.mark.audit
def test_albert_algebra_has_f4_derivations_and_e6_norm_symmetry() -> None:
    row = claims.jordan_symmetry_dimensions(8)
    if (row["derivation_dimension"], row["norm_preserving_dimension"]) != (52, 78):
        raise AssertionError(f"H3(O): {row}")


def test_moufang_holds_on_octonions_and_fails_on_sedenions() -> None:
    result = claims.moufang_split()
    counts = {name: entry["failures"] for name, entry in result.items() if isinstance(entry, dict)}
    if counts != {"octonions": 0, "sedenions": 10752}:
        raise AssertionError(f"Moufang counts {result}")


def test_kac_determinant_through_level_four() -> None:
    constants = {level: claims.kac_level(level)["constant"] for level in range(1, 5)}
    if constants != {1: 2, 2: 32, 3: 2304, 4: 37748736}:
        raise AssertionError(f"Kac constants {constants}")


@pytest.mark.audit
def test_kac_determinant_at_level_five() -> None:
    if claims.kac_level(5)["h_degree"] != 20:
        raise AssertionError("level-5 degree")


def test_coulomb_gas_and_sugawara() -> None:
    if claims.coulomb_gas()["ising_m3"] != {"2,1": "1/2", "1,2": "1/16", "1,1": "0"}:
        raise AssertionError("Ising weights")
    if claims.sugawara_sl2()["nonzero_L2_terms_p"] != [1]:
        raise AssertionError("Sugawara central-charge terms")


def test_corpus_counterexamples_and_physics_bounds() -> None:
    claims.l_infinity_and_affine()
    claims.scalar_equation_of_motion()
    shortfall = claims.casimir()["shortfall_factor"]
    if not isinstance(shortfall, float) or shortfall < 1e3:
        raise AssertionError("passive dielectric reached the claimed enhancement")
    if claims.zero_point()["higgs_cutoff_over_corpus"] < 1e30:
        raise AssertionError("zero-point cutoff arithmetic")
    if claims.su5_assignments()["corpus_ten_dimension"] == 10:
        raise AssertionError("corpus 10 has ten states")


def test_only_the_known_slip_disagrees_in_the_existing_notes() -> None:
    bad = [row["statement"] for row in claims.existing_note_rechecks() if not row["agrees"]]
    if bad != ["electron Schrodinger step over c^4/(2G), the sentence's referent"]:
        raise AssertionError(f"disagreeing rows {bad}")
    claims.algebra_rechecks()
    if claims.spin_up_profiles()["sin2_ramp_peak_W"] < 10 * claims.spin_up_profiles()["scale_estimate_W"]:
        raise AssertionError("profile factor")


def test_ascella_associator_shows_only_through_two_photon_interference() -> None:
    result = claims.ascella_two_photon_associator()
    if result["route_difference_ideal"] != 2.0 or result["route_difference_control"] != 0.0:
        raise AssertionError(f"route differences {result}")


def test_corpus_linear_pairing_contradicts_itself_and_the_hermitian_one_agrees() -> None:
    result = claims.corpus_pairing_sign()
    if (result["linear_word"], result["linear_state"]) != ("-2*k", "2*k"):
        raise AssertionError(f"pairing {result}")


def test_quaternion_encoding_carries_the_sl2_bracket_into_the_order_interferometer() -> None:
    if claims.quaternion_order_bridge()["angle_pairs_checked"] != 3:
        raise AssertionError("order-interferometer bridge")


def test_octonion_gammas_generate_cl8_and_sedenions_fail_on_zero_divisor_pairs() -> None:
    result = claims.octonion_clifford()
    if result["failing_pairs_by_dimension"] != {"8": 0, "16": 42}:
        raise AssertionError(f"Clifford failures {result}")


def test_associator_columns_are_characters_with_trivial_mutations() -> None:
    result = claims.associator_characters()
    if result != {"octonion_pairs_nontrivial": 21, "cl03_trivial": True, "a_equals_b_trivial": True}:
        raise AssertionError(f"associator characters {result}")


@pytest.mark.audit
def test_jordan_table_matches_the_sage_checked_albert_product() -> None:
    if claims.albert_table_cross_check()["pairs_checked"] != 729:
        raise AssertionError("Albert cross-check")


def test_two_decompositions_reconcile_to_derived_values() -> None:
    result = claims.decomposition_reconciliation()
    estimates, derived = result["field_gravity_estimates_over_1m"], result["field_gravity_derived_over_1m"]
    if not (isinstance(estimates, list) and isinstance(derived, float) and estimates[0] < derived < estimates[1]):
        raise AssertionError(f"gravity coefficient {result}")
    peak, average = result["peak_power_instantaneous_W"], result["peak_power_cycle_average_W"]
    if not (isinstance(peak, float) and isinstance(average, float)) or abs(peak / (2 * average) - 1) > 1e-12:
        raise AssertionError("instantaneous and averaged power")
