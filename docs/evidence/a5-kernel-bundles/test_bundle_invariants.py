"""Focused contracts for producer-bound high-nullity bundle inputs."""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any

import bundle_invariants


class BundleInvariantTests(unittest.TestCase):
    """Separate computed prerequisites from written classification arguments."""

    baseline: dict[str, Any]

    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = bundle_invariants.bundle_checks()

    def _pieces(self) -> dict[str, dict[str, Any]]:
        return {row["piece"]: row for row in self.baseline["pieces"]}

    def test_producers_cover_each_declared_piece(self) -> None:
        self.assertTrue(self.baseline["pass"])
        self.assertEqual(tuple(self.baseline["declared_denominator"]), bundle_invariants.PIECES)
        self.assertEqual(tuple(self.baseline["producer_piece_keys"]), bundle_invariants.PIECES)
        self.assertTrue(self.baseline["observed_checks"]["producer_denominator_exact"])
        self.assertEqual(self.baseline["residual_open_keys"], [])
        residuals = self.baseline["out_of_denominator_residuals"]
        self.assertEqual(
            {row["key"] for row in residuals},
            {"full_component_group", "individual_xi_real_type", "smaller_nullity_twelve_reductions"},
        )
        self.assertTrue(all(row["next_action"] for row in residuals))

    def test_every_piece_classification_is_explicitly_inferred(self) -> None:
        pieces = self._pieces()
        self.assertEqual(tuple(pieces), bundle_invariants.PIECES)
        for piece in bundle_invariants.PIECES:
            with self.subTest(piece=piece):
                self.assertEqual(pieces[piece]["classification_status"], "inferred")
                self.assertTrue(pieces[piece]["classification_argument"])

    def test_nullity_twelve_ranks_are_producer_derived(self) -> None:
        pieces = self._pieces()
        for piece in ("B9", "V", "VB", "V^a_+", "V^a_-"):
            with self.subTest(piece=piece):
                self.assertEqual(pieces[piece]["complex_rank"], 6)
                self.assertEqual(pieces[piece]["ordinary_complex_bundle"], "C^6")

    def test_vb_multiplicities_give_zero_order_two_residue(self) -> None:
        derived = self.baseline["derived_inputs"]["VB"]
        vb = self._pieces()["VB"]
        self.assertEqual(derived["trivial_lines"], 2)
        self.assertEqual(derived["standard_doublets"], 2)
        self.assertEqual(derived["irreducible_multiplicities"], [1, 2, 1])
        self.assertEqual(derived["commutant_dimension"], 6)
        self.assertEqual(vb["ordinary_bundle_on_stiefel_factor"], "C^2 + 2 xi")
        self.assertEqual(vb["k_generator_order"], 2)
        self.assertEqual(vb["reduced_k_residue"], 0)
        self.assertTrue(vb["equivariant_automorphism_group_connected"])
        self.assertEqual(vb["cancellation"]["inequality"], "11<=12")
        self.assertTrue(vb["cancellation"]["inequality_verified"])

    def test_complex_cancellation_uses_the_closed_stable_range(self) -> None:
        boundary = bundle_invariants._complex_cancellation(6, 12)
        outside = bundle_invariants._complex_cancellation(6, 13)
        self.assertEqual(boundary["range_condition"], "d<=2k")
        self.assertEqual(boundary["inequality"], "12<=12")
        self.assertTrue(boundary["inequality_verified"])
        self.assertEqual(outside["inequality"], "13<=12")
        self.assertFalse(outside["inequality_verified"])

    def test_open_v_uses_exact_phase_and_mapping_torus_inputs(self) -> None:
        derived = self.baseline["derived_inputs"]
        open_v = self._pieces()["V"]
        self.assertEqual(derived["phase"]["right_phase_square"], "-I_32")
        self.assertEqual(derived["phase"]["ambient_period"], "2 pi")
        self.assertEqual(derived["phase"]["fiber_return_after_one_period"], "identity")
        self.assertEqual(derived["mapping_torus_reduced_k0"], {"free_rank": 0, "torsion_orders": []})
        self.assertEqual(open_v["pulled_back_class_coordinates"], {"free": [0], "torsion": [0]})
        self.assertTrue(open_v["phase_pullback_input"])

    def test_nullity_sixteen_multiplicities_retain_nonzero_residue(self) -> None:
        derived = self.baseline["derived_inputs"]["N"]
        self.assertEqual(derived["trivial_lines"], 2)
        self.assertEqual(derived["standard_doublets"], 3)
        self.assertEqual(derived["complex_rank"], 8)
        for piece in ("N_+", "N_-"):
            with self.subTest(piece=piece):
                row = self._pieces()[piece]
                self.assertEqual(row["ordinary_complex_bundle"], "C^2 + 3 xi")
                self.assertEqual(row["reduced_k_residue"], 1)

    def test_adjacent_boundaries_add_one_doublet_and_two_complex_dimensions(self) -> None:
        adjacency = self.baseline["adjacent_strata"]
        self.assertEqual(adjacency["VB_to_N_standard_doublet_change"], 1)
        self.assertEqual(adjacency["aligned_to_N_standard_doublet_change"], 1)
        self.assertEqual(adjacency["VB_to_N_complex_rank_change"], 2)
        self.assertEqual(adjacency["aligned_to_N_complex_rank_change"], 2)

    def test_characteristic_arrays_are_inferred_and_rank_sized(self) -> None:
        for row in self.baseline["pieces"]:
            with self.subTest(piece=row["piece"]):
                rank = int(row["complex_rank"])
                characteristics = row["characteristic_classes"]
                self.assertEqual(characteristics["status"], "inferred")
                self.assertEqual(len(characteristics["chern_coefficients_c0_through_c_rank"]), rank + 1)
                self.assertEqual(
                    len(characteristics["stiefel_whitney_coefficients_w0_through_w_real_rank"]),
                    2 * rank + 1,
                )
                self.assertEqual(
                    len(characteristics["pontryagin_coefficients_p0_through_p_floor_real_rank_over_4"]),
                    rank // 2 + 1,
                )

    def test_mutations_change_bound_inputs_and_fail_downstream_checks(self) -> None:
        extra_doublet = bundle_invariants.bundle_checks("add_vb_standard_doublet")
        self.assertFalse(extra_doublet["pass"])
        self.assertGreater(extra_doublet["mutation"]["rows_changed"], 0)
        self.assertEqual(extra_doublet["derived_inputs"]["VB"]["standard_doublets"], 3)
        self.assertFalse(extra_doublet["observed_checks"]["VB_fiber_dimension_is_six"])

        mapping_generator = bundle_invariants.bundle_checks("add_mapping_torus_k0_generator")
        self.assertFalse(mapping_generator["pass"])
        self.assertEqual(mapping_generator["derived_inputs"]["mapping_torus_reduced_k0"]["free_rank"], 1)
        self.assertFalse(mapping_generator["observed_checks"]["mapping_torus_reduced_K0_is_zero"])

        killed_generator = bundle_invariants.bundle_checks("kill_k_generator")
        self.assertFalse(killed_generator["pass"])
        self.assertEqual(killed_generator["derived_inputs"]["k_generator_order"], 1)
        self.assertFalse(killed_generator["observed_checks"]["nullity_sixteen_stable_class_is_nonzero"])

    def test_false_antipodal_clutching_criterion_is_absent(self) -> None:
        self.assertNotIn("antipodal_clutching", self.baseline)
        for row in self.baseline["pieces"]:
            self.assertNotIn("natural_clutching", row)

    def test_readme_uses_source_grounded_obstruction_arguments(self) -> None:
        readme = Path(__file__).with_name("README.md").read_text(encoding="utf-8")
        for required_text in (
            "is a special triple",
            "unit section is connected",
            "d<=2k",
            "pi_6(U(6))=pi_6(U)=0",
            "Dale Husemoller",
            "Luke Hodgkin",
            "Raoul Bott",
        ):
            with self.subTest(required_text=required_text):
                self.assertIn(required_text, readme)
        for rejected_text in (
            "2*6>11",
            "natural geometric clutching",
            "only natural nonidentity clutching",
            "joins `I_6` to `-I_6`",
        ):
            with self.subTest(rejected_text=rejected_text):
                self.assertNotIn(rejected_text, readme)


if __name__ == "__main__":
    unittest.main()
