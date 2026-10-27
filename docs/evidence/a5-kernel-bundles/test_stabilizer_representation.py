"""Focused contracts for the nullity-sixteen stabilizer representations."""

from __future__ import annotations

import unittest

import stabilizer_representation


class NullitySixteenStabilizerTests(unittest.TestCase):
    """Catch a wrong stabilizer, fiber action, or irreducible split."""

    def test_both_components_have_the_same_su2_plus_u1_representation(self) -> None:
        result = stabilizer_representation.stabilizer_checks()

        self.assertTrue(result["pass"])
        self.assertTrue(result["equivalent_decompositions"])
        self.assertEqual([row["orbit"] for row in result["rows"]], ["Np", "Nm"])
        expected_decomposition = [
            {
                "central_weight": "-4*I",
                "sl2_highest_weight": 0,
                "irreducible_dimension": 1,
                "multiplicity": 1,
                "joint_dimension": 1,
                "casimir_eigenvalue": "0",
            },
            {
                "central_weight": "-3*I",
                "sl2_highest_weight": 1,
                "irreducible_dimension": 2,
                "multiplicity": 2,
                "joint_dimension": 4,
                "casimir_eigenvalue": "3/8",
            },
            {
                "central_weight": "-2*I",
                "sl2_highest_weight": 0,
                "irreducible_dimension": 1,
                "multiplicity": 1,
                "joint_dimension": 1,
                "casimir_eigenvalue": "0",
            },
            {
                "central_weight": "-I",
                "sl2_highest_weight": 1,
                "irreducible_dimension": 2,
                "multiplicity": 1,
                "joint_dimension": 2,
                "casimir_eigenvalue": "3/8",
            },
        ]
        for row in result["rows"]:
            self.assertEqual(row["stabilizer_dimension"], 4)
            self.assertEqual(row["compact_orbit_dimension"], 11)
            self.assertEqual(row["stabilizer_center_dimension"], 1)
            self.assertEqual(row["stabilizer_derived_dimension"], 3)
            self.assertEqual(row["stabilizer_lie_algebra"], "su(2) + u(1)")
            self.assertEqual(
                row["connected_stabilizer_group"]["connected_stabilizer_group"],
                "U(2) = (SU(2) x U(1))/diagonal Z_2",
            )
            self.assertTrue(row["connected_stabilizer_group"]["pass"])
            self.assertEqual(row["complex_fiber_dimension"], 8)
            self.assertEqual(row["su2_restriction"], {"trivial_lines": 2, "standard_doublets": 3})
            self.assertEqual(
                row["primitive_center_named_coefficients"],
                {"compact_g2_7": 1, "compact_g2_13": 1, "base_phase_lift": 2},
            )
            self.assertTrue(row["weights_descend_to_su2_times_u1_mod_diagonal_z2"])
            self.assertEqual(row["irreducible_decomposition"], expected_decomposition)
            self.assertTrue(row["representation_commutators_match"])
            self.assertTrue(row["compact_domain_matrices_skew_symmetric"])
            self.assertEqual(row["invariant_projectors"]["commutant_dimension"], 7)
            self.assertEqual(row["invariant_projectors"]["projector_ranks"], [1, 2, 2, 1, 2])
            self.assertTrue(row["invariant_projectors"]["pass"])

    def test_a_moving_compact_direction_is_rejected_from_the_stabilizer(self) -> None:
        result = stabilizer_representation.stabilizer_checks("include_moving_direction")

        self.assertFalse(result["pass"])
        self.assertTrue(any(not all(row["point_fixed"]) for row in result["rows"]))


if __name__ == "__main__":
    unittest.main()
