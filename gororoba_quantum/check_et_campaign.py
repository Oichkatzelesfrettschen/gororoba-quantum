"""Acquisition completeness, null rejection, mapping and runner adapter regressions."""

import unittest

import numpy as np
from scipy.stats import binom

from et_campaign import configuration, et_group
from et_statistics import _union_pvalue, analyze, bounded_pvalue, holm


class ETCampaignTests(unittest.TestCase):
    def test_declared_block_independence_prices_the_complete_raw_law(self) -> None:
        from dataclasses import replace

        from et_campaign import contracts
        from experiment_optimizer import BudgetContract, CandidatePlan, JobCandidate, PubPrediction, evaluate_candidate

        config = configuration()
        group = et_group(config)
        pubs = {
            member.name: PubPrediction(
                member.name,
                {member.name: (tuple(member.ideal),)},
                1e-6,
                0.00025,
                "ideal fixture",
                simulation_shots=65536,
            )
            for member in group.members
        }
        jobs = tuple(
            JobCandidate(
                f"tier-{shots}",
                tuple(pubs[name] for name, item in config["members"].items() if item["shots"] == shots),
                shots,
                2.3,
                90,
                "fixture",
            )
            for shots in (32, 64, 128, 2048)
        )
        plan = CandidatePlan("fixture", jobs)
        budget = BudgetContract(600, 10, 600)
        endpoints = contracts(0.08, 0.05, 0.8)
        self.assertFalse(evaluate_candidate(plan, endpoints, budget).feasible)
        blocks = tuple(
            tuple(name for name, item in config["members"].items() if item["block"] == block)
            for block in range(config["blocks"])
        )
        declared = replace(
            plan, independent_pub_blocks=blocks, pub_independence_assumption=config["sampling_assumption"]
        )
        result = evaluate_candidate(declared, endpoints, budget)
        self.assertTrue(result.feasible, result.rejection_reasons)
        self.assertTrue(
            all(config["sampling_assumption"] in endpoint.covariance_assumptions for endpoint in result.observables)
        )
        self.assertFalse(
            evaluate_candidate(replace(declared, pub_independence_assumption=None), endpoints, budget).feasible
        )

    def test_calibrated_filter_preserves_search_wide_admission(self) -> None:
        from experiment_optimizer import CandidateResult, OptimizationResult, restrict_candidates

        def candidate(name: str, feasible: bool, charge: float) -> CandidateResult:
            return CandidateResult(name, feasible, charge, 90, (), (), (), {}, worst_case_charge_seconds=charge)

        near_boundary = candidate("raw_infeasible", False, 1)
        cheapest = candidate("calibration_infeasible", True, 2)
        retained = candidate("retained", True, 3)
        original = OptimizationResult(
            cheapest.name,
            (near_boundary, cheapest, retained),
            (cheapest.name, retained.name),
            (),
            0.01,
            99,
            (),
            selected_objective_value=2,
        )
        result = restrict_candidates(original, {near_boundary.name, retained.name}, "calibrated screen")
        self.assertEqual(result.selected, retained.name)
        self.assertEqual(result.simulation_comparisons, 99)
        self.assertFalse(result.candidates[0].feasible)
        self.assertFalse(result.candidates[1].feasible)
        self.assertIs(result.candidates[2], retained)
        self.assertEqual(result.selected_objective_value, 3)

    def test_calibrated_filter_preserves_raw_failure_reasons(self) -> None:
        from experiment_optimizer import CandidateResult, OptimizationResult, restrict_candidates

        candidate = CandidateResult("raw_infeasible", False, 1, 90, (), (), ("budget",), {})
        original = OptimizationResult(None, (candidate,), (), ("raw budget failure",), 0.01, 1, ())
        self.assertIs(restrict_candidates(original, {candidate.name}, "calibrated screen"), original)
        rejected = restrict_candidates(original, set(), "calibrated screen")
        self.assertEqual(rejected.rejection_reasons, original.rejection_reasons)
        self.assertIn("calibrated screen", rejected.candidates[0].rejection_reasons)

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
        import math

        from experiment_optimizer import CandidatePlan, _plan_radius, _PubObservable

        for shots in (32, 128, 2048):
            blocks = tuple((f"block_{block}",) for block in range(4))
            plan = CandidatePlan(
                "null-fixture",
                (),
                independent_pub_blocks=blocks,
                pub_independence_assumption="independent shots within a block",
            )
            streams = tuple(_PubObservable(block[0], shots, 0.25, None, None) for block in blocks)
            self.assertAlmostEqual(
                _plan_radius(plan, streams, 0.025, False), math.sqrt(math.log(4 / 0.025) / (2 * shots))
            )
            rejection = [
                successes
                for successes in range(shots + 1)
                if _union_pvalue(successes / shots - 0.5, [0.25] * 4, [shots] * 4, list(range(4))) <= 0.025
            ]
            probability = float(binom.sf(min(rejection) - 1, shots, 0.5)) if rejection else 0.0
            self.assertLessEqual(probability, 0.025)


if __name__ == "__main__":
    unittest.main()
