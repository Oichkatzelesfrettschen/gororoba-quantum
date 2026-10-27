"""Focused contracts for the compact-orbit quotient of the open piece ``V``."""

from __future__ import annotations

import unittest
from typing import Any

import v_orbit_moduli


class VOrbitModuliTests(unittest.TestCase):
    """Catch collapse of the three-dimensional quotient to the recorded endpoint."""

    baseline: dict[str, Any]

    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = v_orbit_moduli.orbit_moduli_checks()

    def test_projective_ratio_and_gram_discriminant_give_the_quotient(self) -> None:
        self.assertTrue(self.baseline["pass"])
        self.assertEqual(
            self.baseline["compact_orbit_space"],
            "(CP^1 minus {+i,-i}) x (0,1]",
        )
        self.assertEqual(self.baseline["compact_orbit_space_topology"]["fundamental_group"], "Z")
        self.assertEqual(self.baseline["compact_orbit_space_topology"]["integral_cohomology"], {"0": "Z", "1": "Z"})
        self.assertTrue(all(row["compact_invariants_stationary"] for row in self.baseline["rows"]))

    def test_principal_orbits_have_su2_stabilizer_for_every_ratio(self) -> None:
        principal_rows = [row for row in self.baseline["rows"] if row["orbit_type"] == "principal"]
        self.assertEqual(len(principal_rows), 6)
        self.assertEqual({row["rho_squared"] for row in principal_rows}, {"64/289", "81/1681"})
        self.assertEqual(
            {row["split_projective_ratio_beta_over_alpha"] for row in principal_rows},
            {"5/3+(0)i", "13/5+(0)i", "infinity"},
        )
        self.assertEqual({row["compact_tangent_rank"] for row in principal_rows}, {12})
        self.assertEqual({row["stabilizer_lie_algebra"] for row in principal_rows}, {"su(2)"})

    def test_collinear_endpoint_explains_the_recorded_rank(self) -> None:
        endpoint_rows = [row for row in self.baseline["rows"] if row["orbit_type"] == "collinear_endpoint"]
        self.assertEqual(len(endpoint_rows), 3)
        self.assertEqual({row["rho_squared"] for row in endpoint_rows}, {"1"})
        self.assertEqual({row["compact_tangent_rank"] for row in endpoint_rows}, {7})
        self.assertEqual({row["stabilizer_lie_algebra"] for row in endpoint_rows}, {"su(3)"})
        self.assertIn("endpoint", self.baseline["recorded_representative_scope"])

    def test_phase_and_coordinate_mutations_are_rejected(self) -> None:
        phase = v_orbit_moduli.orbit_moduli_checks("delete_phase_generator")
        coordinate = v_orbit_moduli.orbit_moduli_checks("drop_i_on_v")
        self.assertFalse(phase["pass"])
        self.assertEqual(phase["rows"][0]["compact_tangent_rank"], 11)
        self.assertFalse(coordinate["pass"])
        self.assertFalse(coordinate["rows"][0]["inside_open_V"])


if __name__ == "__main__":
    unittest.main()
