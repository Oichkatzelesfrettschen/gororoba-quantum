"""Focused contracts for the aligned nullity-twelve stabilizer representations."""

from __future__ import annotations

import unittest
from typing import Any

import aligned_stabilizer_representation


class AlignedStabilizerRepresentationTests(unittest.TestCase):
    """Catch representation jumps missed by the complex orbit labels."""

    baseline: dict[str, Any]

    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = aligned_stabilizer_representation.representation_checks()

    def test_principal_representation_is_constant_across_signs_and_moduli(self) -> None:
        self.assertTrue(self.baseline["pass"])
        self.assertTrue(self.baseline["principal_rows_equivalent"])
        principal_rows = [row for row in self.baseline["rows"] if row["orbit_type"] == "principal"]
        self.assertEqual(len(principal_rows), 6)
        self.assertEqual({row["rho_squared"] for row in principal_rows}, {"9/25", "16/25", "25/169"})
        self.assertEqual({row["representation"]["decomposition"] for row in principal_rows}, {"2 V_0 + 2 V_1"})
        self.assertEqual({tuple(row["representation"]["isotypic_projector_ranks"]) for row in principal_rows}, {(2, 4)})

    def test_endpoint_is_a_faithful_fundamental_plus_dual(self) -> None:
        endpoint_rows = [row for row in self.baseline["rows"] if row["orbit_type"] == "collinear_endpoint"]
        self.assertEqual(len(endpoint_rows), 2)
        self.assertTrue(self.baseline["endpoint_components_equivalent"])
        for row in endpoint_rows:
            certificate = row["representation"]
            self.assertEqual(certificate["decomposition"], "3 + conjugate(3)")
            self.assertEqual(certificate["commutant_dimension"], 2)
            self.assertEqual(certificate["irreducible_projector_ranks"], [3, 3])
            self.assertEqual(certificate["invariant_symmetric_pairing_rank"], 6)
            self.assertTrue(certificate["summands_are_pairwise_dual"])

    def test_boundary_adds_one_standard_doublet(self) -> None:
        comparison = self.baseline["boundary_comparison"]
        self.assertTrue(comparison["pass"])
        self.assertEqual(comparison["principal_restriction"], {"trivial_lines": 2, "standard_doublets": 2})
        self.assertEqual(comparison["nullity_sixteen_restriction"], {"trivial_lines": 2, "standard_doublets": 3})

    def test_moving_and_fiber_action_mutations_are_rejected(self) -> None:
        moving = aligned_stabilizer_representation.representation_checks("include_moving_direction")
        fiber = aligned_stabilizer_representation.representation_checks("perturb_fiber_action")
        self.assertFalse(moving["pass"])
        self.assertFalse(all(moving["rows"][0]["point_fixed"]))
        self.assertFalse(fiber["pass"])
        self.assertFalse(fiber["rows"][0]["representation_commutators_match"])


if __name__ == "__main__":
    unittest.main()
