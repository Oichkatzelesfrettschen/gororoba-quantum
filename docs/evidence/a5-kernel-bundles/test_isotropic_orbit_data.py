"""Focused contracts for the compact moduli and fibers on ``B9`` and ``VB``."""

from __future__ import annotations

import unittest
from fractions import Fraction
from typing import Any

import isotropic_orbit_data


class IsotropicOrbitDataTests(unittest.TestCase):
    """Catch incomplete Gram quotients and representation jumps."""

    baseline: dict[str, Any]

    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = isotropic_orbit_data.orbit_data_checks()

    def test_b9_quotient_is_the_open_hermitian_gram_ball(self) -> None:
        self.assertTrue(self.baseline["pass"])
        b9 = self.baseline["B9"]
        self.assertIn("open 3-ball", b9["compact_orbit_space"])
        self.assertEqual(b9["unit_section_homotopy_type"], "G_2")
        self.assertTrue(b9["representations_constant"])
        rows = [row for row in self.baseline["rows"] if row["orbit"] == "B9"]
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(row["inside_B9"] and row["compact_gram_stationary"] for row in rows))
        self.assertTrue(all(Fraction(row["normalized_ball_radius_squared"]) < 1 for row in rows))
        self.assertEqual(
            {row["stabilizer_representation"]["compact_tangent_rank"] for row in rows},
            {14},
        )
        self.assertEqual(
            {row["stabilizer_representation"]["stabilizer_lie_algebra"] for row in rows},
            {"u(1)"},
        )

    def test_b9_circle_representation_is_constant(self) -> None:
        rows = [row for row in self.baseline["rows"] if row["orbit"] == "B9"]
        representations = [row["stabilizer_representation"]["representation"] for row in rows]
        self.assertEqual({row["decomposition"] for row in representations}, {"3 C_(-1) + 3 C_(-2)"})
        self.assertEqual(
            {tuple(sorted(row["weight_multiplicities"].items())) for row in representations},
            {(("-2*I", 3), ("-I", 3))},
        )
        self.assertTrue(all(row["pass"] for row in representations))

    def test_vb_is_the_punctured_rank_one_boundary(self) -> None:
        vb = self.baseline["VB"]
        self.assertEqual(vb["compact_orbit_space"], "CP^1 minus {+i,-i}, homotopy equivalent to C^*")
        self.assertEqual(vb["unit_section_fundamental_group"], "Z")
        self.assertTrue(vb["representations_constant"])
        self.assertTrue(vb["boundary_restriction_matches"])
        rows = [row for row in self.baseline["rows"] if row["orbit"] == "VB"]
        self.assertEqual(len(rows), 4)
        self.assertEqual(
            {row["original_projective_ratio_lambda"] for row in rows},
            {"0+(0)i", "0+(2)i", "-2+(0)i", "infinity"},
        )
        self.assertTrue(all(row["inside_VB"] and row["compact_gram_stationary"] for row in rows))
        self.assertEqual(
            {row["stabilizer_representation"]["compact_tangent_rank"] for row in rows},
            {11},
        )
        self.assertEqual(
            {row["stabilizer_representation"]["stabilizer_lie_algebra"] for row in rows},
            {"su(2)+u(1)"},
        )

    def test_vb_kernel_drops_the_boundary_doublet(self) -> None:
        rows = [row for row in self.baseline["rows"] if row["orbit"] == "VB"]
        representations = [row["stabilizer_representation"]["representation"] for row in rows]
        self.assertEqual(
            {row["decomposition"] for row in representations},
            {"V_(0,-4) + 2 V_(1,-3) + V_(0,-2)"},
        )
        self.assertEqual(
            {tuple(row["projectors"]["projector_ranks"]) for row in representations},
            {(1, 2, 2, 1)},
        )
        self.assertEqual({row["projectors"]["commutant_dimension"] for row in representations}, {6})
        self.assertTrue(all(row["pass"] for row in representations))

    def test_all_four_mutations_are_rejected(self) -> None:
        phase = isotropic_orbit_data.orbit_data_checks("drop_common_phase")
        rank = isotropic_orbit_data.orbit_data_checks("force_rank_one")
        moving = isotropic_orbit_data.orbit_data_checks("include_moving_direction")
        fiber = isotropic_orbit_data.orbit_data_checks("perturb_fiber_action")
        self.assertFalse(phase["pass"])
        self.assertFalse(phase["rows"][0]["compact_gram_stationary"])
        self.assertFalse(rank["pass"])
        self.assertFalse(rank["rows"][0]["inside_B9"])
        self.assertFalse(moving["pass"])
        self.assertFalse(all(moving["rows"][0]["stabilizer_representation"]["point_fixed"]))
        self.assertFalse(fiber["pass"])
        self.assertFalse(fiber["rows"][0]["stabilizer_representation"]["representation_commutators_match"])


if __name__ == "__main__":
    unittest.main()
