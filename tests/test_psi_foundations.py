import math
import unittest
from fractions import Fraction

from gororoba_quantum.psi_foundations import (
    classical_chsh_bound,
    independent_common_overlap,
    overlap,
    product_probability,
    quantum_chsh,
)


class PsiFoundationsTests(unittest.TestCase):
    def test_local_vertices(self):
        self.assertEqual(classical_chsh_bound(), [-2, 2])

    def test_singlet_violation(self):
        self.assertAlmostEqual(abs(quantum_chsh()), 2 * math.sqrt(2), places=12)
        self.assertGreater(abs(quantum_chsh()), 2)

    def test_independent_distribution(self):
        p = {"x": Fraction(1, 4), "y": Fraction(3, 4)}
        joint = product_probability(p, p)
        self.assertEqual(sum(joint.values()), 1)
        self.assertEqual(joint[("x", "y")], Fraction(3, 16))

    def test_overlap(self):
        p = {"x": Fraction(1, 4), "y": Fraction(3, 4)}
        q = {"x": Fraction(3, 4), "y": Fraction(1, 4)}
        self.assertEqual(overlap(p, q), Fraction(1, 2))
        self.assertEqual(independent_common_overlap(p, q), Fraction(1, 4))

    def test_invalid_distribution_fails_closed(self):
        with self.assertRaises(ValueError):
            overlap({"x": Fraction(-1), "y": Fraction(2)}, {"x": Fraction(1, 2), "y": Fraction(1, 2)})


if __name__ == "__main__":
    unittest.main()
