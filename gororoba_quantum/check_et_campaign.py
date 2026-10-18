"""Acquisition completeness, null rejection, mapping and runner adapter regressions."""

import unittest

import numpy as np
from scipy.stats import binom

from et_campaign import configuration, et_group
from et_statistics import _union_pvalue, analyze, bounded_pvalue, holm


class ETCampaignTests(unittest.TestCase):
    def test_complete_budget_and_reconstruction(self) -> None:
        config = configuration()
        group = et_group(config)
        metadata = config["members"]
        self.assertEqual(set(metadata), {member.name for member in group.members})
        self.assertEqual(sum(row["shots"] for row in metadata.values() if row["kind"] == "signal"), 98304)
        self.assertEqual(sum(row["shots"] for row in metadata.values() if row["kind"] == "dephased"), 49152)
        self.assertEqual(len(set(group.execution_rows or ())), len(group.members))
        from diagnostic_experiments import record_groups

        rebuilt = record_groups({"family_configuration": config})
        self.assertEqual([member.name for member in rebuilt[0].members], list(metadata))
        self.assertNotEqual(group.execution_rows, tuple(range(len(group.members))))
        self.assertEqual(et_group(configuration()).execution_rows, group.execution_rows)

    def test_declared_budget_ideal_admission(self) -> None:
        config = configuration()
        members = et_group(config).members
        observations = {}
        for member in members:
            shots = config["members"][member.name]["shots"]
            expected = member.ideal * shots
            counts = np.floor(expected).astype(int)
            remainder = shots - int(counts.sum())
            counts[np.argsort(-(expected - counts), kind="stable")[:remainder]] += 1
            self.assertEqual(int(counts.sum()), shots)
            observations[member.name] = {"counts": counts.tolist(), "shots": shots}
        contexts = {member.name: {"validated": True} for member in members}
        report = analyze(config, observations, contexts)
        self.assertTrue(report["admitted"], report["endpoints"])

    def test_admission_and_identical_marker_counterexample(self) -> None:
        config = configuration()
        members = et_group(config).members
        observations = {
            member.name: {
                "counts": np.rint(member.ideal * 1000000).astype(int).tolist(),
                "shots": int(np.rint(member.ideal * 1000000).sum()),
            }
            for member in members
        }
        report = analyze(config, observations)
        self.assertEqual(len(report["endpoints"]), 6)
        # Primary evidence alone never establishes valid physical controls.
        self.assertFalse(report["admitted"])
        self.assertIn("control", report["withheld"])
        for member in members:
            metadata = config["members"][member.name]
            if metadata["basis"] == "X" and metadata["kind"] == "signal":
                uniform = np.full(64, 15625)
                observations[member.name] = {"counts": uniform.tolist(), "shots": 1000000}
        report = analyze(config, observations)
        self.assertTrue(
            all(endpoint["p_value"] == 1 for endpoint in report["endpoints"] if endpoint["kind"] == "coherence")
        )

    def test_bounded_probabilities(self) -> None:
        self.assertEqual(bounded_pvalue(0, 0.001), 1)
        self.assertLess(bounded_pvalue(0.5, 0.001), 1e-10)
        self.assertEqual(holm([0.001, 0.04, 0.5], 0.05), [True, False, False])
        with self.assertRaises(ValueError):
            bounded_pvalue(float("nan"), 1)

    def test_null_bound_with_identical_dependent_blocks(self) -> None:
        for shots in (32, 128, 2048):
            rejection = [
                successes
                for successes in range(shots + 1)
                if _union_pvalue(successes / shots - 0.5, [0.25] * 4, [shots] * 4, list(range(4))) <= 0.025
            ]
            probability = float(binom.sf(min(rejection) - 1, shots, 0.5)) if rejection else 0.0
            self.assertLessEqual(probability, 0.025)


if __name__ == "__main__":
    unittest.main()
