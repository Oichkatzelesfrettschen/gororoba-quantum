"""Bounded behavioral fixtures; no retained acquisitions or services are read."""

from __future__ import annotations

import copy
import importlib.util
import math
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import evidence_workbench as ew  # noqa: E402


def seal(value: dict[str, Any]) -> dict[str, Any]:
    value.pop("payload_sha256", None)
    value["payload_sha256"] = ew.sha256(ew.canonical(value))
    return value


def fixture(family: str = "ripple") -> tuple[dict[str, Any], bytes]:
    """Eight synthetic shared positions with an anticorrelated pair and a constant."""
    values = {"alpha": [0, 0, 1, 1, 0, 0, 1, 1], "beta": [1, 1, 0, 0, 1, 1, 0, 0], "constant": [0] * 8}
    members: dict[str, Any] = {}
    for i, (name, sequence) in enumerate(values.items()):
        p = sequence.count(0) / 8
        metadata: dict[str, Any] = {"kind": "atlas", "role": "atlas", "kite": 1, "edge_index": i}
        if family == "rank-sector":
            metadata = {
                "kind": "rank-sector",
                "role": "packed",
                "execution_row": i,
                "sector": 0,
                "probe": name,
                "parameter_exact": "0",
                "alpha_exact": "2",
                "unit_probe_norm_factor_exact": "4",
                "unnormalized_probe_norm_factor_exact": "8",
                "ideal_success_exact": "1",
                "probe_coordinates": [1, 1, 0, 0],
            }
        members[name] = {
            "job_id": "synthetic-job",
            "pub": "synthetic-pub",
            "pub_index": 0,
            "shots": 8,
            "registers": [name],
            "physical_qubits": [i],
            "counts": [sequence.count(0), sequence.count(1)],
            "probabilities": [p, 1 - p],
            "ideal_probabilities": [1.0, 0.0],
            "metadata": metadata,
            "preparation_model": {"probabilities": [0.9, 0.1], "calibration": "synthetic"},
            "execution_replay": {"status": "calibration_bound", "probabilities": [0.8, 0.2]},
            "shot_order_blocks": [
                {
                    "start_shot": start,
                    "stop_shot_exclusive": start + 4,
                    "shots": 4,
                    "event_zero_probability": sequence[start : start + 4].count(0) / 4,
                }
                for start in (0, 4)
            ],
        }

    def moments(error: bool) -> dict[str, Any]:
        sequences = [[int(v != 0) if error else int(v == 0) for v in sequence] for sequence in values.values()]
        means = [sum(s) / 8 for s in sequences]
        joint = [
            [sum(a * b for a, b in zip(left, right, strict=True)) / 8 for right in sequences] for left in sequences
        ]
        return {
            "members": list(values),
            "joint_probabilities": joint,
            "covariance": [[joint[i][j] - means[i] * means[j] for j in range(3)] for i in range(3)],
        }

    raw = ew.canonical(
        {
            "pub_name": "synthetic-pub",
            "pub_index": 0,
            "registers": {
                name: {"num_bits": 1, "num_shots": 8, "bitstrings": list(map(str, sequence))}
                for name, sequence in values.items()
            },
        }
    )
    relative = "raw/synthetic-job/pub_00.json"
    value = {
        "schema": ew.EXTRACTION_SCHEMA,
        "family": family,
        "evidence_kind": "synthetic_fixture",
        "source_commit": "synthetic",
        "experiment_digest": "0" * 64,
        "source_files": {relative: ew.sha256(raw)},
        "members": members,
        "pubs": [
            {
                "job_id": "synthetic-job",
                "name": "synthetic-pub",
                "shots": 8,
                "raw_sha256": ew.sha256(raw),
                "event_zero": moments(False),
                "deterministic_error": moments(True),
            }
        ],
        "endpoint_analysis": {"withheld": "synthetic behavioral fixture"},
    }
    return seal(value), raw


class WorkbenchTests(unittest.TestCase):
    def reject(self, mutate: Any, pattern: str) -> None:
        value, _ = fixture()
        mutate(value)
        seal(value)
        with self.assertRaisesRegex((ValueError, KeyError, TypeError), pattern):
            ew.validate_acquisition(value)

    def test_valid_moments_and_constant(self) -> None:
        value, _ = fixture()
        checked = ew.validate_acquisition(value)
        corr = checked["dependence"][0]["event_zero"]["correlation"]
        self.assertEqual(corr[0][:2], [1.0, -1.0])
        self.assertIsNone(corr[2][2])
        self.assertEqual(value["evidence_kind"], "synthetic_fixture")

    def test_payload_mutation(self) -> None:
        value, _ = fixture()
        value["members"]["alpha"]["counts"][0] += 1
        with self.assertRaisesRegex(ValueError, "payload hash"):
            ew.validate_acquisition(value)

    def test_internal_mass(self) -> None:
        self.reject(lambda v: v["members"]["alpha"].update(counts=[3, 4]), "histogram mass")

    def test_boolean_count(self) -> None:
        self.reject(lambda v: v["members"]["alpha"].update(counts=[True, 7]), "invalid integer")

    def test_blocks_gap(self) -> None:
        self.reject(lambda v: v["members"]["alpha"]["shot_order_blocks"][1].update(start_shot=5), "block gap")

    def test_blocks_integer(self) -> None:
        self.reject(
            lambda v: v["members"]["alpha"]["shot_order_blocks"][0].update(event_zero_probability=0.3), "integer count"
        )

    def test_blocks_totals(self) -> None:
        self.reject(
            lambda v: v["members"]["alpha"]["shot_order_blocks"][0].update(event_zero_probability=0.25), "block totals"
        )

    def test_cross_pub_pairing(self) -> None:
        self.reject(lambda v: v["members"]["alpha"].update(pub="another-pub"), "cross-PUB")

    def test_covariance_identity(self) -> None:
        self.reject(lambda v: v["pubs"][0]["event_zero"]["covariance"][0].__setitem__(1, 0), "covariance identity")

    def test_noninteger_joint(self) -> None:
        self.reject(
            lambda v: v["pubs"][0]["event_zero"]["joint_probabilities"][0].__setitem__(1, 0.01), "integer count"
        )

    def test_unqualified_replay(self) -> None:
        self.reject(
            lambda v: v["members"]["alpha"]["execution_replay"].update(status="unavailable"), "unqualified replay"
        )

    def test_exact_psd(self) -> None:
        self.assertTrue(ew.positive_semidefinite([[1, -1, 0], [-1, 1, 0], [0, 0, 0]]))
        self.assertFalse(ew.positive_semidefinite([[1, -1, -1], [-1, 1, -1], [-1, -1, 1]]))
        self.assertFalse(ew.positive_semidefinite([[0, 1], [1, 1]]))

    def test_rank_factor_validation(self) -> None:
        value, _ = fixture("rank-sector")
        ew.validate_acquisition(value)
        value["members"]["alpha"]["metadata"]["unit_probe_norm_factor_exact"] = "3"
        seal(value)
        with self.assertRaisesRegex(ValueError, "unit-probe factor"):
            ew.validate_acquisition(value)

    def test_rank_identity_required(self) -> None:
        for field in ("kind", "role", "sector", "probe", "execution_row"):
            value, _ = fixture("rank-sector")
            del value["members"]["alpha"]["metadata"][field]
            seal(value)
            with self.assertRaises(ValueError, msg=field):
                ew.validate_acquisition(value)
        for field, bad in (("role", "other"), ("sector", 8), ("parameter_exact", "1/3")):
            value, _ = fixture("rank-sector")
            value["members"]["alpha"]["metadata"][field] = bad
            seal(value)
            with self.assertRaises(ValueError, msg=field):
                ew.validate_acquisition(value)

    def test_rank_exact_metadata_uses_the_page_grammar(self) -> None:
        for field in ("parameter_exact", "alpha_exact", "unit_probe_norm_factor_exact"):
            value, _ = fixture("rank-sector")
            metadata = value["members"]["alpha"]["metadata"]
            metadata[field] = str(float(Fraction(metadata[field])))
            seal(value)
            with self.assertRaisesRegex(ValueError, "not an integer or a/b", msg=field):
                ew.validate_acquisition(value)

    def test_wide_mass_rejected(self) -> None:
        width = 65536
        with self.assertRaisesRegex(ValueError, "mass exceeds"):
            ew._probabilities([1.03 / width] * width, width, "wide")
        ew._probabilities([1.0 / width] * width, width, "wide")
        rounded = [1 / 32] * 32
        rounded[0] += 3e-6
        ew._probabilities(rounded, 32, "retained-scale rounding")
        rounded[0] += 2e-5
        with self.assertRaisesRegex(ValueError, "mass exceeds"):
            ew._probabilities(rounded, 32, "excess")

    def test_strict_decode(self) -> None:
        for text in (b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}'):
            with self.assertRaises(ValueError):
                ew.decode(text)

    def test_raw_replay(self) -> None:
        value, raw = fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "raw/synthetic-job/pub_00.json"
            target.parent.mkdir(parents=True)
            target.write_bytes(raw)
            report = ew.verify_sources(ew.validate_acquisition(value), root)
            self.assertEqual(report["verification"], "source_files_and_raw_statistics")
            self.assertEqual(report["raw_replays"][0]["members"], 3)
            target.write_bytes(raw + b" ")
            with self.assertRaisesRegex(ValueError, "source hash"):
                ew.verify_sources(ew.validate_acquisition(value), root)

    def test_raw_replay_detects_consistent_marginal_false_joint(self) -> None:
        value, raw = fixture()
        changed = ew.decode(raw)
        changed["registers"]["beta"]["bitstrings"] = changed["registers"]["alpha"]["bitstrings"]
        changed_raw = ew.canonical(changed)
        value["source_files"]["raw/synthetic-job/pub_00.json"] = ew.sha256(changed_raw)
        value["pubs"][0]["raw_sha256"] = ew.sha256(changed_raw)
        seal(value)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "raw/synthetic-job/pub_00.json"
            target.parent.mkdir(parents=True)
            target.write_bytes(changed_raw)
            with self.assertRaisesRegex(ValueError, "raw joint"):
                ew.verify_sources(ew.validate_acquisition(value), root)

    def test_no_input_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = root / "original.json"
            original.write_bytes(b"source")
            with self.assertRaises(ValueError):
                ew.write_new(original, b"changed", [original])
            self.assertEqual(original.read_bytes(), b"source")
            target = root / "fresh.html"
            ew.write_new(target, b"result", [original])
            self.assertEqual(target.read_bytes(), b"result")

    def test_source_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ValueError):
                ew.source_path(root, "../elsewhere")
            with self.assertRaises(ValueError):
                ew.source_path(root, "/etc/passwd")

    def test_bloch_set(self) -> None:
        self.assertEqual(ew.bloch_region([0, 0], [0, 0])["z"], [-1, 1])
        self.assertEqual(ew.bloch_region([1, 1], [0, 0])["z"], [-0.0, 0.0])
        self.assertTrue(ew.bloch_region([0.9, 1], [0.9, 1])["empty"])
        result = ew.bloch_region([0.3, 0.8], [0.4, 0.9])
        self.assertAlmostEqual(result["z"][1], math.sqrt(0.75))

    def test_bloch_invalid(self) -> None:
        for x in ([math.nan, 1], [-2, 0], [0.5, 0.4]):
            with self.assertRaises(ValueError):
                ew.bloch_region(x, [0, 0])

    def test_optical_cohorts(self) -> None:
        for schema in (
            "ascella-fixed-mesh-confirmation-v1",
            "ascella-new-mesh-score-v1",
            "ascella-replication-score-v1",
        ):
            value = {
                "schema": schema,
                "primary": {"reading": "not carried"},
                "rows": [{"observed": 0.8, "predicted": 0.85, "counting_variance": 0.001}],
            }
            result = ew.load_ascella(value, schema)
            self.assertEqual(result["payload"]["primary"], value["primary"])
            self.assertEqual(result["prediction_fields"], ["predicted"])

    def test_optical_missing_prediction(self) -> None:
        with self.assertRaises(ValueError):
            ew.load_ascella({"schema": "ascella-fixed-mesh-confirmation-v1", "rows": [{"observed": 0.5}]}, "bad")

    def test_static_build_escapes_labels(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "workbench_builder", ROOT / "scripts/render_evidence_workbench.py"
        )
        if spec is None or spec.loader is None:
            self.fail("builder module unavailable")
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        bundle = {
            "schema": ew.SCHEMA,
            "sources": [],
            "ramsey": None,
            "acquisitions": [],
            "optical": [],
            "boundaries": ["</script><img src=x onerror=alert(1)>"],
        }
        rendered = builder.render(bundle).decode()
        self.assertNotIn("</script><img", rendered)
        self.assertIn("\\u003c/script\\u003e", rendered)
        self.assertIn("script-src 'sha256-", rendered)
        self.assertEqual(rendered, builder.render(copy.deepcopy(bundle)).decode())


if __name__ == "__main__":
    unittest.main()
