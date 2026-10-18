"""Exact ET fixtures and arbitrary-input circuit contracts, including doubling."""

import unittest

import numpy as np
from qiskit.quantum_info import Operator, Statevector

from et_reference import ETSpec, child_box, table_census
from et_rows import direct_state, row_circuit


class ETRowTests(unittest.TestCase):
    def test_census_and_exclusions(self) -> None:
        for strut, degree in ((1, 12), (9, 4)):
            spec = ETSpec(32, strut, 2)
            self.assertEqual(spec.degree, degree)
            self.assertEqual(spec.spectrum, {0: degree, 2: 32 - 2 * degree, 4: degree})
            for column in (0, strut, 2, 2 ^ strut):
                self.assertFalse(spec.cell(column).valid)
        self.assertEqual(table_census(32, 9)["filled"], 72)
        self.assertEqual(ETSpec(32, 9, 8).degree, 12)
        with self.assertRaises(ValueError):
            ETSpec(32, 9, 9)

    def test_shifted_child_box(self) -> None:
        self.assertEqual(child_box(32, 15)["counts"], {"interior": 72, "border": 56, "box": 128})
        self.assertEqual(ETSpec(32, 15, 1).cell(6).value, -7)
        self.assertEqual(ETSpec(64, 15, 17).cell(22).value, -7)
        self.assertEqual(ETSpec(64, 15, 1).cell(22).value, -23)

    def test_direct_states_and_complete_dephasing(self) -> None:
        for dimension in (32, 64, 128):
            spec = ETSpec(dimension, 9, 2)
            for basis in ("Z", "X"):
                for sign in (-1, 1):
                    for mask in (0, 1):
                        actual = Statevector.from_instruction(row_circuit(spec, sign, basis, mask, measured=False)).data
                        np.testing.assert_allclose(actual, direct_state(spec, sign, basis, mask), atol=3e-14)
            law = np.mean([abs(direct_state(spec, 1, "X", mask)) ** 2 for mask in range(spec.generator)], axis=0)
            np.testing.assert_allclose(law.reshape(4, spec.generator).sum(axis=0), 1 / spec.generator, atol=1e-14)

    def test_coherence_and_instrument(self) -> None:
        spec = ETSpec(32, 9, 2)
        circuit = row_circuit(spec, 1, "X")
        self.assertEqual(circuit.num_clbits, 6)
        self.assertEqual(circuit.count_ops()["measure"], 6)
        law = abs(direct_state(spec, 1, "X")) ** 2
        expected = np.array([1, 9, 11, 3, 1, 25, 11, 3, 1, 1, 3, 3, 1, 1, 51, 3]) / 128
        np.testing.assert_allclose(law.reshape(4, 16).sum(axis=0), expected, atol=1e-14)
        self.assertAlmostEqual(float(abs(expected - 1 / 16).sum() / 2), 67 / 128)
        self.assertEqual(Operator(circuit.remove_final_measurements(inplace=False)).dim, (64, 64))

    def test_partial_dephasing_preserves_only_marker_bit(self) -> None:
        spec = ETSpec(32, 9, 2)
        partial = np.mean([abs(direct_state(spec, 1, "X", mask)) ** 2 for mask in range(0, 16, 2)], axis=0)
        np.testing.assert_allclose(partial.reshape(4, 16).sum(axis=0), np.tile([5 / 64, 3 / 64], 8), atol=1e-14)
        marked = np.mean([abs(direct_state(spec, 1, "X", mask ^ 1)) ** 2 for mask in range(0, 16, 2)], axis=0)
        np.testing.assert_allclose(
            marked.reshape(4, 16).sum(axis=0), partial.reshape(4, 16).sum(axis=0)[np.arange(16) ^ 1], atol=1e-14
        )


if __name__ == "__main__":
    unittest.main()
