"""Focused contracts for the aligned nullity-twelve compact-orbit decomposition."""

from __future__ import annotations

import unittest
from typing import Any

import aligned_orbit_moduli


class AlignedOrbitModuliTests(unittest.TestCase):
    """Catch collapse of the principal interval to its special representative."""

    baseline: dict[str, Any]

    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = aligned_orbit_moduli.orbit_moduli_checks()

    def test_normalized_gram_discriminant_classifies_the_orbit_interval(self) -> None:
        self.assertTrue(self.baseline["pass"])
        self.assertEqual(self.baseline["orbit_space"], "0<rho<=1")
        self.assertEqual(
            self.baseline["original_coordinate_parameterization"],
            "z=(u,0,+/- i u), u dot u != 0",
        )
        self.assertTrue(self.baseline["gram_invariant"]["pass"])
        self.assertTrue(self.baseline["component_results_identical"])

    def test_principal_endpoint_and_boundary_stabilizers_are_distinct(self) -> None:
        positive_rows = [row for row in self.baseline["rows"] if row["sign"] == 1]
        self.assertEqual(
            [
                (
                    row["orbit_type"],
                    row["rho_squared"],
                    row["compact_tangent_rank"],
                    row["stabilizer_lie_algebra"],
                    row["left_nullity"],
                )
                for row in positive_rows
            ],
            [
                ("collinear_endpoint", "1", 7, "su(3)", 12),
                ("principal", "9/25", 12, "su(2)", 12),
                ("null_boundary", "0", 11, "su(2)+u(1)", 16),
            ],
        )
        self.assertEqual(
            self.baseline["earlier_rank_scope"],
            "the rank-seven V^a representative is the rho=1 endpoint, not the principal orbit",
        )

    def test_quadratic_link_complement_has_the_claimed_topology(self) -> None:
        topology = self.baseline["topology"]
        self.assertTrue(topology["pass"])
        self.assertEqual(topology["unit_section"], "S^13 minus V_2(R^7), independently for V^a_+ and V^a_-")
        self.assertEqual(topology["monodromy_degree_on_h6"], -1)
        self.assertEqual(topology["fundamental_group"], "Z")
        self.assertEqual(topology["integral_cohomology"], {"0": "Z", "1": "Z", "7": "Z/2"})

    def test_phase_and_monodromy_mutations_are_rejected(self) -> None:
        phase_mutation = aligned_orbit_moduli.orbit_moduli_checks("delete_phase_generator")
        monodromy_mutation = aligned_orbit_moduli.orbit_moduli_checks("trivialize_monodromy")

        self.assertFalse(phase_mutation["pass"])
        self.assertEqual(
            [row["compact_tangent_rank"] for row in phase_mutation["rows"] if row["orbit_type"] == "principal"],
            [11, 11],
        )
        self.assertFalse(monodromy_mutation["pass"])
        self.assertEqual(monodromy_mutation["topology"]["monodromy_degree_on_h6"], 1)
        self.assertNotEqual(monodromy_mutation["topology"]["integral_cohomology"].get("7"), "Z/2")


if __name__ == "__main__":
    unittest.main()
