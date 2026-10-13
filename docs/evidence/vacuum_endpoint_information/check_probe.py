"""Reject malformed endpoint evidence, coverage and binding under normal Python and -O."""

from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import probe


class EndpointEvidenceTests(unittest.TestCase):
    def test_comparator_rejections(self) -> None:
        fixtures = [
            ({"value": 1.0}, {"value": 1.01}),
            ({"status": "passed"}, {"status": "failed"}),
            ({"count": 8}, {"count": 9}),
            ({"value": 1.0}, {"value": 1}),
            ({"value": 1.0}, {"value": True}),
            ({"value": float("nan")}, {"value": float("nan")}),
            ({"value": float("inf")}, {"value": float("inf")}),
            ({"value": 1.0}, {"value": 1.0, "extra": 2}),
            ([1.0], [1.0, 2.0]),
        ]
        for observed, retained in fixtures:
            with self.subTest(observed=observed):
                with self.assertRaises(RuntimeError):
                    probe.compare_records(observed, retained)

    def test_numeric_tolerance(self) -> None:
        probe.compare_records({"value": 1.0}, {"value": 1.0 + 1e-13})

    def test_version_scope(self) -> None:
        observed = {"python": "3.14", "numpy": "2.5", "scipy": "1.18", "value": 1.0}
        retained = {**observed, "python": "3.15"}
        probe.compare_version_aware(observed, retained)
        for key in probe.VERSION_KEYS:
            mutated = {**retained, key: ""}
            with self.assertRaises(RuntimeError):
                probe.compare_version_aware(observed, mutated)
        with self.assertRaises(RuntimeError):
            probe.compare_version_aware(observed, {**retained, "value": 2.0})

    def test_json_duplicate_nonfinite_and_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "fixture.json"
            for text in ('{"x": 1, "x": 2}', '{"x": NaN}', '{"x": Infinity}', '{"x": 1e999}', "[]"):
                path.write_text(text)
                with self.assertRaises(RuntimeError):
                    probe.load_json_object(path)

    def test_provenance_rejections(self) -> None:
        provenance = probe.load_json_object(probe.BUNDLE / "provenance.json")
        invalid_schema = copy.deepcopy(provenance)
        invalid_schema["schema_version"] = True
        with self.assertRaises(RuntimeError):
            probe.validate_provenance(invalid_schema, probe.EXPECTED_INPUTS)
        for name in probe.EXPECTED_INPUTS:
            mutated = copy.deepcopy(probe.EXPECTED_INPUTS)
            mutated[name]["sha256"] = "0" * 64
            with self.assertRaises(RuntimeError):
                probe.validate_provenance(provenance, mutated)
        mutated_provenance = copy.deepcopy(provenance)
        mutated_provenance["inputs"].pop(next(iter(probe.EXPECTED_INPUTS)))
        with self.assertRaises(RuntimeError):
            probe.validate_provenance(mutated_provenance, probe.EXPECTED_INPUTS)

    def test_source_change_rejection(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "changed during computation"):
            probe.verify_unchanged_sources({"probe.py": "before"}, {"probe.py": "after"})
        actual = probe.source_hashes()
        mutated = {**actual, "probe.py": "changed"}
        with patch("probe.source_hashes", side_effect=[actual, mutated]):
            with self.assertRaisesRegex(RuntimeError, "changed during computation"):
                probe.build_record()

    def test_bound_source_rejections(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            (base / "probe.py").symlink_to(probe.BUNDLE / "probe.py")
            with patch("probe.BUNDLE", base), patch("probe.SOURCE_FILES", ("probe.py",)):
                with self.assertRaisesRegex(RuntimeError, "regular file"):
                    probe.source_hashes()
            (base / "inputs").mkdir()
            (base / "inputs/reviewed_probe.py.txt").write_text("changed")
            with patch("probe.BUNDLE", base), patch("probe.SOURCE_FILES", ("inputs/reviewed_probe.py.txt",)):
                with self.assertRaisesRegex(RuntimeError, "input size differs"):
                    probe.source_hashes()

    def test_coverage_rejections(self) -> None:
        reviewed = probe.load_json_object(probe.BUNDLE / "inputs/reviewed_result.json")
        probe.validate_coverage(reviewed)
        missing_arm = copy.deepcopy(reviewed)
        missing_arm["arms"].pop()
        duplicate_arm = copy.deepcopy(reviewed)
        duplicate_arm["arms"][1] = copy.deepcopy(duplicate_arm["arms"][0])
        missing_law = copy.deepcopy(reviewed)
        missing_law["arms"][0]["setting_moments"].pop("XX")
        wrong_shots = copy.deepcopy(reviewed)
        wrong_shots["workload"]["whole_workload_shots_each_design"] = 144000
        for mutated in (missing_arm, duplicate_arm, missing_law, wrong_shots):
            with self.assertRaises(RuntimeError):
                probe.validate_coverage(mutated)

    def test_endpoint_cover_and_witness(self) -> None:
        result = probe.supplementary_checks()
        self.assertEqual(result["minimum_setting_count"], 7)
        self.assertEqual(len(result["unique_minimum_cover"]), 1)
        for witness in result["hidden_after_XY_counterexamples"]:
            self.assertGreater(witness["minimum_eigenvalue"], 0)
            self.assertGreater(abs(witness["Im_ab"]), 1e-8)
            self.assertLess(witness["five_setting_probability_residual"], 1e-12)


if __name__ == "__main__":
    unittest.main()
