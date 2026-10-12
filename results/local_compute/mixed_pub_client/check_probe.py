"""Exercise mixed-PUB rejection without launching a simulator or service."""

from __future__ import annotations

import unittest

from probe import validate_counts
from qiskit_ibm_runtime.executor_estimator import Estimator, EstimatorV2
from qiskit_ibm_runtime.executor_sampler import Sampler, SamplerV2


class CountValidationTests(unittest.TestCase):
    def test_expected_counts_pass(self) -> None:
        validate_counts([{"11": 64}, {"01": 64}])

    def test_wrong_counts_fail(self) -> None:
        for counts in ([{"11": 63}, {"01": 64}], [{"10": 64}, {"01": 64}]):
            with self.subTest(counts=counts), self.assertRaisesRegex(RuntimeError, "counts or order differ"):
                validate_counts(counts)

    def test_wrong_order_and_cardinality_fail(self) -> None:
        for counts in ([{"01": 64}, {"11": 64}], [{"11": 64}], [{"11": 64}, {"01": 64}, {"00": 64}]):
            with self.subTest(counts=counts), self.assertRaisesRegex(RuntimeError, "counts or order differ"):
                validate_counts(counts)

    def test_client_aliases_resolve(self) -> None:
        self.assertIs(Sampler, SamplerV2)
        self.assertIs(Estimator, EstimatorV2)


if __name__ == "__main__":
    unittest.main()
