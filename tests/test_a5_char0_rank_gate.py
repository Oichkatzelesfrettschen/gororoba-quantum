"""Regression tests for exact characteristic-zero rank-transfer gate."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "a5_char0_rank_gate.py"
SPEC = importlib.util.spec_from_file_location("a5_char0_rank_gate", SOURCE)
assert SPEC and SPEC.loader
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class RankGateTests(unittest.TestCase):
    def test_two_split_primes_refute_naive_difference_transfer(self) -> None:
        # W vanishes at both primes, but not in characteristic zero.
        for prime, root in ((32009, 10754), (32029, 9115)):
            result = gate.check({
                "prime": prime, "i_root": root,
                "W": [[32009 * 32029]], "P": [[1]],
            })
            self.assertEqual(result["truncated_difference_Qi"], 0)
            self.assertEqual(result["truncated_difference_Fp"], 1)
            self.assertFalse(result["lower_bound_transfer_admissible"])

    def test_stable_subtracted_rank_allows_transfer(self) -> None:
        result = gate.check({
            "prime": 32009, "i_root": 10754,
            "W": [[1], [0]], "P": [[0], [1]],
        })
        self.assertTrue(result["subtracted_rank_stable"])
        self.assertEqual(result["truncated_difference_Qi"], 1)
        self.assertEqual(result["truncated_difference_Fp"], 1)

    def test_gaussian_rational_exact_arithmetic(self) -> None:
        result = gate.check({
            "prime": 32009, "i_root": 10754,
            "W": [[[1, 1]], [[2, 2]]],
            "P": [[[0, 1]], [[0, 0]]],
        })
        self.assertEqual(result["rank_W_Qi"], 1)
        self.assertEqual(result["rank_joined_Qi"], 2)
        self.assertTrue(result["subtracted_rank_stable"])

    def test_reject_bad_denominator(self) -> None:
        with self.assertRaisesRegex(ValueError, "Denominator"):
            gate.check({
                "prime": 32009, "i_root": 10754,
                "W": [["1/32009"]], "P": [[1]],
            })

    def test_reject_bad_root(self) -> None:
        with self.assertRaisesRegex(ValueError, "i_root"):
            gate.check({"prime": 32009, "i_root": 1, "W": [[1]], "P": [[1]]})

    def test_reject_nonrectangular_input(self) -> None:
        with self.assertRaisesRegex(ValueError, "rectangular"):
            gate.check({
                "prime": 32009, "i_root": 10754,
                "W": [[1], [1, 2]], "P": [[1], [2]],
            })


if __name__ == "__main__":
    unittest.main()
