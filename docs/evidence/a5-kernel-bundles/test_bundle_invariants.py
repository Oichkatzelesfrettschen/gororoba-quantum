"""Focused contracts for the high-nullity bundle classification."""

from __future__ import annotations

import unittest
from typing import Any

import bundle_invariants


class BundleInvariantTests(unittest.TestCase):
    """Catch denominator gaps, hidden torsion, and false clutching claims."""

    baseline: dict[str, Any]

    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = bundle_invariants.bundle_checks()

    def _pieces(self) -> dict[str, dict[str, Any]]:
        return {row["piece"]: row for row in self.baseline["pieces"]}

    def test_all_seven_pieces_have_exactly_one_classification(self) -> None:
        self.assertTrue(self.baseline["pass"])
        self.assertTrue(self.baseline["denominator_exact"])
        self.assertEqual(tuple(self.baseline["declared_denominator"]), bundle_invariants.PIECES)
        self.assertEqual(self.baseline["declared_denominator"], self.baseline["classified_keys"])
        self.assertEqual(self.baseline["residual_open_keys"], [])
        residuals = self.baseline["out_of_denominator_residuals"]
        self.assertEqual(
            {row["key"] for row in residuals},
            {"full_component_group", "individual_xi_real_type", "smaller_nullity_twelve_reductions"},
        )
        self.assertTrue(all(row["next_action"] for row in residuals))

    def test_nullity_twelve_complex_bundles_are_actually_trivial(self) -> None:
        pieces = self._pieces()
        for piece in ("B9", "V", "VB", "V^a_+", "V^a_-"):
            with self.subTest(piece=piece):
                self.assertEqual(pieces[piece]["complex_rank"], 6)
                self.assertTrue(pieces[piece]["complex_stably_trivial"])
                self.assertTrue(pieces[piece]["complex_actually_trivial"])
                self.assertEqual(pieces[piece]["ordinary_complex_bundle"], "C^6")
                self.assertEqual(pieces[piece]["characteristic_classes"]["total_chern_class"], "1")
                self.assertEqual(
                    pieces[piece]["characteristic_classes"]["total_stiefel_whitney_class"],
                    "1",
                )

    def test_vb_torsion_cancels_before_the_moduli_circle_is_attached(self) -> None:
        vb = self._pieces()["VB"]
        self.assertEqual(vb["ordinary_bundle_on_stiefel_factor"], "C^2 + 2 xi")
        self.assertEqual(vb["reduced_complex_k_class"], "2x=0 in Z/2")
        self.assertTrue(vb["stable_cancellation_on_stiefel_factor"]["pass"])
        self.assertEqual(vb["equivariant_automorphism_group"], "GL(1,C) x GL(2,C) x GL(1,C)")
        self.assertEqual(vb["irreducible_multiplicities"], [1, 2, 1])
        self.assertEqual(vb["commutant_dimension"], 6)
        self.assertTrue(vb["equivariant_automorphism_group_connected"])
        self.assertEqual(vb["natural_clutching"]["moduli_generator"], "I_6")

    def test_open_v_phase_lift_kills_both_available_reduced_classes(self) -> None:
        open_v = self._pieces()["V"]
        phase = open_v["phase_pullback_certificate"]
        self.assertTrue(phase["pass"])
        self.assertEqual(phase["right_phase_square"], "-I_32")
        self.assertEqual(phase["ambient_period"], "2 pi")
        self.assertEqual(phase["fiber_clutching_after_one_period"], "I_6")
        self.assertTrue(open_v["pulled_back_from_mapping_torus_factor"])
        self.assertEqual(open_v["reduced_complex_k_class_coordinates"], {"free": 0, "order_two": 0})

    def test_antipodal_clutching_is_null_homotopic_inside_su6(self) -> None:
        clutching = self.baseline["antipodal_clutching"]
        self.assertEqual(clutching["natural_clutching"], "-I_6")
        self.assertEqual(clutching["determinant"], 1)
        self.assertEqual(clutching["path_integer_weights"], [1, 1, 1, 1, 1, -5])
        self.assertEqual(clutching["weight_sum"], 0)
        self.assertTrue(all(isinstance(sign, int) for sign in clutching["endpoint_signs"]))
        self.assertTrue(clutching["null_homotopic_in_SU"])

    def test_nullity_sixteen_complex_class_remains_nonzero(self) -> None:
        pieces = self._pieces()
        for piece in ("N_+", "N_-"):
            with self.subTest(piece=piece):
                self.assertFalse(pieces[piece]["complex_stably_trivial"])
                self.assertFalse(pieces[piece]["complex_actually_trivial"])
                self.assertEqual(pieces[piece]["ordinary_complex_bundle"], "E_C=C^2+3 xi")
                self.assertEqual(pieces[piece]["reduced_complex_k_class"], "3x=x != 0")
                self.assertEqual(pieces[piece]["characteristic_classes"]["total_chern_class"], "1")
                self.assertEqual(
                    pieces[piece]["underlying_real_bundle"], "trivial rank 16 by stable-range cancellation"
                )
                self.assertFalse(pieces[piece]["quaternionic_actually_trivial"])

    def test_adjacent_rank_jumps_add_exactly_one_standard_doublet(self) -> None:
        comparisons = self.baseline["adjacent_strata"]["comparisons"]
        rank_jumps = [row for row in comparisons if row["rank_change"] == 2]
        self.assertEqual(len(rank_jumps), 2)
        self.assertTrue(all(row["added_bundle"] == "xi" for row in rank_jumps))
        self.assertTrue(all(row["standard_doublet_change"] == 1 for row in rank_jumps))
        self.assertTrue(self.baseline["adjacent_strata"]["pass"])

    def test_all_three_mutations_are_rejected_for_the_intended_reason(self) -> None:
        missing_doublet = bundle_invariants.bundle_checks("drop_vb_standard_doublet")
        torsion_twist = bundle_invariants.bundle_checks("inject_v_torsion")
        odd_rank = bundle_invariants.bundle_checks("odd_rank_antipodal_clutching")

        self.assertFalse(missing_doublet["pass"])
        mutated_vb = next(row for row in missing_doublet["pieces"] if row["piece"] == "VB")
        self.assertEqual(mutated_vb["reduced_complex_k_class"], "1x=1 in Z/2")

        self.assertFalse(torsion_twist["pass"])
        mutated_v = next(row for row in torsion_twist["pieces"] if row["piece"] == "V")
        self.assertEqual(mutated_v["reduced_complex_k_class_coordinates"]["order_two"], 1)

        self.assertFalse(odd_rank["pass"])
        self.assertEqual(odd_rank["antipodal_clutching"]["determinant"], -1)
        self.assertFalse(odd_rank["antipodal_clutching"]["lies_in_SU"])


if __name__ == "__main__":
    unittest.main()
