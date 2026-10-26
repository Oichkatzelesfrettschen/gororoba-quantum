"""Focused contracts for the A_5 kernel transport and complex structure."""

from __future__ import annotations

import unittest

import kernel_symmetry


class KernelTransportTests(unittest.TestCase):
    """Catch loss of the input conjugation or the kernel's J action."""

    def test_transport_and_complex_structure_hold_at_every_high_nullity_representative(self) -> None:
        result = kernel_symmetry.representative_kernel_checks()

        self.assertTrue(result["pass"])
        self.assertEqual(
            [(row["orbit"], row["real_nullity"], row["complex_nullity"]) for row in result["rows"]],
            [
                ("B9", 12, 6),
                ("V", 12, 6),
                ("VB", 12, 6),
                ("Vap", 12, 6),
                ("Vam", 12, 6),
                ("Np", 16, 8),
                ("Nm", 16, 8),
            ],
        )
        self.assertTrue(all(row["transport_with_input_conjugation"] for row in result["rows"]))
        self.assertTrue(all(row["j_preserves_kernel"] for row in result["rows"]))
        self.assertTrue(all(row["phi_j_equals_i_phi"] for row in result["rows"]))
        self.assertTrue(all(row["conjugate_phi_j_equals_minus_i_conjugate_phi"] for row in result["rows"]))

    def test_omitting_input_conjugation_is_detected(self) -> None:
        result = kernel_symmetry.representative_kernel_checks(mutation="omit_input_conjugation")

        self.assertFalse(result["pass"])
        self.assertGreater(sum(row["transport_failures"] for row in result["rows"]), 0)

    def test_wrong_j_phase_is_detected(self) -> None:
        result = kernel_symmetry.representative_kernel_checks(mutation="wrong_j_phase")

        self.assertFalse(result["pass"])
        self.assertTrue(any(not row["conjugate_phi_j_equals_minus_i_conjugate_phi"] for row in result["rows"]))


class KernelSymmetryLieAlgebraTests(unittest.TestCase):
    """Catch missing constraints, missing lifts, and accidental boost admission."""

    def test_lie_algebra_is_g2_plus_four_commuting_directions(self) -> None:
        result = kernel_symmetry.lie_algebra_checks()

        self.assertTrue(result["pass"])
        self.assertEqual(result["dimension"], 18)
        self.assertEqual(result["base_projection_dimension"], 16)
        self.assertEqual(result["vertical_dimension"], 2)
        self.assertEqual(result["expected_span_dimension"], 18)
        self.assertEqual(result["center_dimension"], 4)
        self.assertEqual(result["derived_algebra_dimension"], 14)
        self.assertEqual(
            result["decomposition"],
            {
                "compact_g2": 14,
                "base_scaling": 1,
                "domain_scaling": 1,
                "vertical_j_phase": 1,
                "base_phase_lift": 1,
            },
        )
        self.assertTrue(result["all_solution_basis_triples_verified"])
        self.assertTrue(result["all_expected_triples_verified"])
        self.assertTrue(result["expected_span_equals_solution"])
        self.assertFalse(result["boost_lifts"])
        self.assertEqual(result["orbit_dimensions"], kernel_symmetry.EXPECTED_ORBIT_DIMENSIONS)

    def test_lie_algebra_rejects_a_mutated_multiplication_sign(self) -> None:
        result = kernel_symmetry.lie_algebra_checks(mutation="flip_structure_sign")

        self.assertFalse(result["pass"])
        self.assertFalse(result["all_expected_triples_verified"])


class KernelSymmetryFiniteSubgroupTests(unittest.TestCase):
    """Catch loss of the visible sedenion S3 or outer reflection."""

    def test_visible_component_subgroup_is_s3_times_z2(self) -> None:
        result = kernel_symmetry.finite_symmetry_checks()

        self.assertTrue(result["pass"])
        self.assertEqual(result["lower_s3_order"], 6)
        self.assertEqual(result["visible_component_cosets"], 12)
        self.assertTrue(result["all_lower_s3_automorphisms"])
        self.assertTrue(result["all_a5_extensions_verified"])
        self.assertTrue(result["s3_relations"])
        self.assertTrue(result["outer_reflection_relation"])
        self.assertTrue(result["factors_commute"])
        self.assertTrue(result["nonidentity_lower_s3_outside_identity_component"])
        self.assertEqual(result["lower_s3_base_determinants"], [1, 1, 1, 1, 1, 1])
        self.assertEqual(result["outer_reflection_base_determinant"], -1)
        self.assertEqual(result["classification_status"], "visible subgroup, not an exhaustive component census")

    def test_mutated_order_three_map_is_rejected(self) -> None:
        result = kernel_symmetry.finite_symmetry_checks(mutation="break_lower_psi")

        self.assertFalse(result["pass"])
        self.assertFalse(result["all_lower_s3_automorphisms"])


if __name__ == "__main__":
    unittest.main()
