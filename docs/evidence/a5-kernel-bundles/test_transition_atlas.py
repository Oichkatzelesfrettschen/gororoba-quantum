"""Focused contracts for the high-nullity Pfaffian transition atlas."""

from __future__ import annotations

import unittest
from typing import Any

import transition_atlas


class TransitionAtlasTests(unittest.TestCase):
    """Catch broken overlap maps and unjustified structure-group reductions."""

    baseline: dict[str, Any]

    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = transition_atlas.transition_atlas_checks()

    def test_finite_atlas_covers_every_high_nullity_piece(self) -> None:
        atlas = self.baseline["atlas"]
        self.assertTrue(self.baseline["pass"])
        self.assertEqual(atlas["nullity_twelve_charts_per_piece"], 8008)
        self.assertEqual(atlas["nullity_sixteen_charts_per_piece"], 12870)
        self.assertEqual(len(atlas["nullity_twelve_pieces"]), 5)
        self.assertEqual(len(atlas["nullity_sixteen_pieces"]), 2)
        self.assertEqual(len(self.baseline["rows"]), 7)
        self.assertTrue(all(len(row["triple_overlap_pivots"]) == 3 for row in self.baseline["rows"]))

    def test_transitions_reconstruct_invert_and_satisfy_the_cocycle(self) -> None:
        for row in self.baseline["rows"]:
            self.assertTrue(row["transition_reconstruction"])
            self.assertTrue(row["transition_inverse"])
            self.assertTrue(row["transition_cocycle"])
            self.assertTrue(row["transitions_invertible"])

    def test_hermitian_metric_reduces_the_complex_structure_group(self) -> None:
        groups = self.baseline["structure_groups"]
        self.assertEqual(groups["nullity_twelve_raw"], "GL(6,C)")
        self.assertEqual(groups["nullity_twelve_metric_reduction"], "U(6)")
        self.assertEqual(groups["nullity_sixteen_raw"], "GL(8,C)")
        self.assertEqual(groups["nullity_sixteen_metric_reduction"], "U(8)")
        self.assertTrue(all(row["hermitian_gram_transport"] for row in self.baseline["rows"]))
        self.assertTrue(all(row["realified_transitions_commute_with_J"] for row in self.baseline["rows"]))

    def test_nullity_sixteen_keeps_the_committed_sp1_reduction(self) -> None:
        self.assertTrue(self.baseline["nullity_sixteen_reduction_matches_committed_result"])
        self.assertEqual(
            self.baseline["structure_groups"]["nullity_sixteen_further_reduction"],
            "diagonal SU(2)=Sp(1) inside Sp(4) and SU(8)",
        )
        self.assertTrue(self.baseline["constant_vertical_complex_only"])

    def test_transition_and_metric_mutations_are_rejected(self) -> None:
        transition = transition_atlas.transition_atlas_checks("perturb_transition")
        metric = transition_atlas.transition_atlas_checks("transpose_metric")
        self.assertFalse(transition["pass"])
        self.assertFalse(transition["rows"][0]["transition_reconstruction"])
        self.assertFalse(transition["rows"][0]["transition_inverse"])
        self.assertFalse(transition["rows"][0]["transition_cocycle"])
        self.assertFalse(metric["pass"])
        self.assertFalse(metric["rows"][0]["hermitian_gram_transport"])


if __name__ == "__main__":
    unittest.main()
