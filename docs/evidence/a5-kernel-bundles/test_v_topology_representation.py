"""Focused contracts for the topology and compact representations of ``V``."""

from __future__ import annotations

import unittest
from typing import Any

import v_topology_representation


class VTopologyRepresentationTests(unittest.TestCase):
    """Catch incorrect square-root monodromy and orbitwise fiber actions."""

    baseline: dict[str, Any]

    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = v_topology_representation.topology_representation_checks()

    def test_unit_section_is_the_phase_circle_times_an_antipodal_mapping_torus(self) -> None:
        topology = self.baseline["topology"]
        self.assertTrue(topology["pass"])
        self.assertEqual(topology["square_root_monodromy"], -1)
        self.assertEqual(topology["homotopy_type"], "S^1 x mapping_torus(-id:S^6->S^6)")
        self.assertEqual(topology["fundamental_group"], "Z^2")
        self.assertEqual(
            topology["unit_section_cohomology"],
            {"0": "Z", "1": "Z^2", "2": "Z", "7": "Z/2", "8": "Z/2"},
        )

    def test_wang_maps_determine_the_complex_k_groups(self) -> None:
        topology = self.baseline["topology"]
        self.assertEqual(topology["wang_map_on_H6"], 2)
        self.assertEqual(topology["wang_map_on_reduced_K0_of_S6"], 2)
        self.assertEqual(topology["mapping_torus_K0"], "Z")
        self.assertEqual(topology["mapping_torus_K1"], "Z + Z/2")
        self.assertEqual(topology["unit_section_K0"], "Z^2 + Z/2")
        self.assertEqual(topology["unit_section_reduced_K0"], "Z + Z/2")
        self.assertEqual(topology["unit_section_K1"], "Z^2 + Z/2")

    def test_principal_and_endpoint_representations_are_constant(self) -> None:
        self.assertTrue(self.baseline["pass"])
        self.assertTrue(self.baseline["principal_rows_equivalent"])
        self.assertTrue(self.baseline["endpoint_rows_equivalent"])
        principal_rows = [row for row in self.baseline["rows"] if row["orbit_type"] == "principal"]
        endpoint_rows = [row for row in self.baseline["rows"] if row["orbit_type"] == "collinear_endpoint"]
        self.assertEqual(len(principal_rows), 6)
        self.assertEqual(len(endpoint_rows), 3)
        self.assertEqual({row["representation"]["decomposition"] for row in principal_rows}, {"2 V_0 + 2 V_1"})
        self.assertEqual(
            {row["representation"]["decomposition"] for row in endpoint_rows},
            {"3 + conjugate(3)"},
        )

    def test_vb_boundary_recovers_the_committed_u2_module(self) -> None:
        self.assertTrue(self.baseline["boundary_rows_equivalent"])
        self.assertTrue(self.baseline["boundary_matches_committed_VB_result"])
        boundary_rows = [row for row in self.baseline["rows"] if row["orbit_type"] == "VB_boundary"]
        self.assertEqual(len(boundary_rows), 3)
        self.assertEqual(
            {row["representation"]["decomposition"] for row in boundary_rows},
            {"V_(0,-4) + 2 V_(1,-3) + V_(0,-2)"},
        )

    def test_topology_and_representation_mutations_are_rejected(self) -> None:
        topology = v_topology_representation.topology_representation_checks("trivialize_monodromy")
        moving = v_topology_representation.topology_representation_checks("include_moving_direction")
        fiber = v_topology_representation.topology_representation_checks("perturb_fiber_action")
        self.assertFalse(topology["pass"])
        self.assertNotEqual(topology["topology"]["unit_section_cohomology"].get("8"), "Z/2")
        self.assertFalse(moving["pass"])
        self.assertFalse(all(moving["rows"][0]["point_fixed"]))
        self.assertFalse(fiber["pass"])
        self.assertFalse(fiber["rows"][0]["representation_commutators_match"])


if __name__ == "__main__":
    unittest.main()
