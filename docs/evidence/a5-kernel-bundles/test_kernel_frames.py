"""Focused contracts for the parameterized A_5 kernel frames."""

from __future__ import annotations

import unittest

import kernel_frames


class NullitySixteenFrameTests(unittest.TestCase):
    """Catch incomplete coverage and invalid bordered-kernel frames on N_+ and N_-."""

    def test_principal_pfaffian_charts_cover_both_nullity_sixteen_cones(self) -> None:
        result = kernel_frames.nullity_sixteen_frame_checks()

        self.assertTrue(result["pass"])
        self.assertEqual(result["chart_count"], 12_870)
        self.assertEqual(
            [(row["orbit"], row["bordered_rank"], row["frame_columns"]) for row in result["orbits"]],
            [("N_+", 8, 8), ("N_-", 8, 8)],
        )
        self.assertTrue(all(row["parameterization_verified"] for row in result["orbits"]))
        self.assertTrue(all(row["frame_identity_verified"] for row in result["orbits"]))
        self.assertTrue(all(row["left_kernel_verified"] for row in result["orbits"]))
        self.assertTrue(all(row["real_frame_rank_verified"] for row in result["orbits"]))
        self.assertTrue(all(row["coverage_witness"] for row in result["orbits"]))

    def test_bordered_sign_mutation_is_rejected(self) -> None:
        result = kernel_frames.nullity_sixteen_frame_checks(mutation="flip_border_sign")

        self.assertFalse(result["pass"])
        self.assertTrue(any(not row["frame_identity_verified"] for row in result["orbits"]))
        self.assertGreater(sum(row["frame_identity_failure_count"] for row in result["orbits"]), 0)


if __name__ == "__main__":
    unittest.main()
