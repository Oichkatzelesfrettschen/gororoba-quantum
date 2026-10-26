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


if __name__ == "__main__":
    unittest.main()
