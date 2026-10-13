"""Synthetic fixtures exercise decoder identities and raw evidence rejection."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from folded_raw_analysis import (
    RUNGS,
    SCHEMA_CONTRACT,
    AnalysisError,
    analyze,
    decode_member,
    lag_one,
    sha256,
)


def register_for(rung: str, label: int, scores: list[int]) -> dict[str, object]:
    width = 1 if rung == "delay" else 2
    bitstrings = []
    for score in scores:
        terminal = label // 2 if score else 1 - label // 2
        # The first bit opposes the terminal bit to expose swapped bit indices.
        outcome = terminal if width == 1 else 2 * terminal + (1 - terminal)
        bitstrings.append(format(outcome, f"0{width}b"))
    return {"num_bits": width, "num_shots": len(scores), "bitstrings": bitstrings}


def save_json(path: Path, value: object) -> bytes:
    data = (json.dumps(value, sort_keys=True) + "\n").encode()
    path.write_bytes(data)
    return data


def make_fixture(folder: Path, scores: list[int]) -> None:
    archive_bytes = b"Synthetic archive bytes test digest binding, not QPY interpretation.\n"
    (folder / "isa.qpy").write_bytes(archive_bytes)
    archive_digest = sha256(archive_bytes)
    manifests = []
    jobs = []
    for kind, rungs in (("dynamic", RUNGS[:3]), ("static", RUNGS[3:])):
        job_id = f"synthetic_{kind}"
        raw = folder / "raw" / job_id
        raw.mkdir(parents=True)
        pubs = []
        file_digests = {}
        for rung in rungs:
            for label in range(4):
                pub_index = len(pubs)
                pub_name = f"synthetic_{kind}_pub_{pub_index:02d}"
                register_name = f"distinct_mapping_{label}_{rung}"
                pub = {
                    "name": pub_name,
                    "kind": kind,
                    "components": [
                        {
                            "member": f"qpe_{rung}_s{label}",
                            "reference": False,
                            "registers_by_replica": [[register_name]],
                        }
                    ],
                }
                pubs.append(pub)
                manifests.append(pub)
                payload = {
                    "pub_index": pub_index,
                    "pub_name": pub_name,
                    "registers": {register_name: register_for(rung, label, scores)},
                    "metadata": {},
                }
                name = f"pub_{pub_index:02d}.json"
                file_digests[name] = sha256(save_json(raw / name, payload))
        file_digests["result_metadata.json"] = sha256(save_json(raw / "result_metadata.json", {}))
        metric_digest = sha256(save_json(raw / "job_metrics.json", {"usage": {"status": "pending"}}))
        save_json(
            raw / "index.json",
            {
                "job_id": job_id,
                "files": file_digests,
                "metrics": ["job_metrics.json"],
                "metrics_sha256": [metric_digest],
                "metrics_latest": "job_metrics.json",
            },
        )
        jobs.append(
            {
                "job_id": job_id,
                "pubs": pubs,
                "backend": "synthetic",
                "kind": kind,
                "batch_index": 1,
                "batch_count": 1,
                "members": [pub["components"][0]["member"] for pub in pubs],
                "qpy_archive_sha256": archive_digest,
                "calibrations": ["synthetic"],
                "recovery_tags": [f"synthetic-{kind}"],
                "options": {},
            }
        )
    save_json(
        folder / "record.json",
        {
            "schema_version": 7,
            "schema_contract": SCHEMA_CONTRACT,
            "family_configuration": {"name": "folded-qpe"},
            "shots": len(scores),
            "experiment_digest": sha256(b"synthetic-only"),
            "execution_pubs": manifests,
            "submission": {
                "complete": True,
                "jobs": jobs,
                "qpy_archive_sha256": archive_digest,
                "planned_jobs": copy.deepcopy(jobs),
            },
        },
    )


class DecoderTests(unittest.TestCase):
    def test_all_labels_and_widths_use_terminal_bit(self) -> None:
        for rung in RUNGS:
            for label in range(4):
                with self.subTest(rung=rung, label=label):
                    result = decode_member(f"qpe_{rung}_s{label}", register_for(rung, label, [1, 1, 1, 0]), 4)
                    self.assertEqual(result["terminal_correct_mean"], 0.75)
                    self.assertEqual(result["expected_terminal_bit"], label // 2)
                    self.assertEqual(sum(result["outcome_counts_by_integer_index"]), 4)

    def test_blocks_and_early_late_direction(self) -> None:
        for scores, expected in (([0] * 512 + [1] * 512, 1.0), ([1] * 512 + [0] * 512, -1.0)):
            result = decode_member("qpe_archived_s2", register_for("archived", 2, scores), 1024)
            self.assertEqual(result["half_comparison"]["late_minus_early"], expected)
            self.assertEqual(
                [block["terminal_correct_mean"] for block in result["blocks"]],
                [float(scores[0]), float(scores[-1])],
            )

    def test_odd_shot_and_partial_block_partition(self) -> None:
        scores = [0] * 512 + [1] * 513
        result = decode_member("qpe_delay_s1", register_for("delay", 1, scores), 1025)
        self.assertEqual([block["shots"] for block in result["blocks"]], [512, 512, 1])
        self.assertEqual(result["half_comparison"]["early_shots"], 512)
        self.assertEqual(result["half_comparison"]["late_shots"], 513)
        self.assertEqual(result["half_comparison"]["late_minus_early"], 1.0)

    def test_correlation_uses_two_lagged_vectors(self) -> None:
        self.assertAlmostEqual(lag_one([0, 1, 0, 1])[0], -1.0)
        self.assertAlmostEqual(lag_one([0, 1, 1, 0])[0], -0.5)
        for scores in ([0] * 4, [1] * 4, [0, 0, 0, 1], [1, 0]):
            with self.subTest(scores=scores):
                correlation, reason = lag_one(scores)
                self.assertIsNone(correlation)
                self.assertIn("zero variance", reason)

    def test_malformed_register_rejected(self) -> None:
        valid = register_for("archived", 0, [0, 1, 0, 1])
        for mutation in (
            {"num_bits": 1},
            {"num_bits": True},
            {"num_shots": 3},
            {"bitstrings": ["00"]},
            {"bitstrings": ["00", "10", "0x", "11"]},
            {"bitstrings": ["0", "1", "0", "1"]},
            {"bitstrings": [0, 1, 0, 1]},
        ):
            with self.subTest(mutation=mutation), self.assertRaises(AnalysisError):
                decode_member("qpe_archived_s0", valid | mutation, 4)
        for name in ("qpe_delay_s4", "folded_qpe_s0", "qpe_archived_s0_suffix"):
            with self.subTest(name=name), self.assertRaises(AnalysisError):
                decode_member(name, valid, 4)


class EvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="synthetic-", dir=Path(__file__).parent)
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        make_fixture(self.folder, [0] * 512 + [1] * 512)
        self.raw = self.folder / "raw" / "synthetic_dynamic"

    def read(self, path: Path) -> dict:
        return json.loads(path.read_text())

    def mutate_indexed_pub(self, update) -> None:
        path = self.raw / "pub_00.json"
        payload = self.read(path)
        update(payload)
        digest = sha256(save_json(path, payload))
        index = self.read(self.raw / "index.json")
        index["files"][path.name] = digest
        save_json(self.raw / "index.json", index)

    def mutate_record(self, update, sync_ledger=True) -> None:
        record = self.read(self.folder / "record.json")
        update(record)
        if sync_ledger:
            record["submission"]["planned_jobs"] = copy.deepcopy(record["submission"]["jobs"])
        save_json(self.folder / "record.json", record)

    def test_complete_fixture_uses_manifest_register_mapping(self) -> None:
        result = analyze(self.folder)
        self.assertEqual(len(result["members"]), 16)
        self.assertEqual(len(result["jobs"]), 2)
        self.assertTrue(all(row["terminal_correct_mean"] == 0.5 for row in result["members"]))
        self.assertTrue(all(row["half_comparison"]["late_minus_early"] == 1 for row in result["members"]))
        self.assertIn("supplemental exploratory", result["analysis_kind"])
        self.assertNotIn("p_value", json.dumps(result))

    def test_raw_byte_corruption_rejected(self) -> None:
        with (self.raw / "pub_00.json").open("ab") as stream:
            stream.write(b" ")
        with self.assertRaisesRegex(AnalysisError, "sha256 mismatch"):
            analyze(self.folder)

    def test_metric_byte_corruption_rejected(self) -> None:
        (self.raw / "job_metrics.json").write_text("{}")
        with self.assertRaisesRegex(AnalysisError, "sha256 mismatch"):
            analyze(self.folder)

    def test_missing_indexed_pub_rejected(self) -> None:
        index = self.read(self.raw / "index.json")
        del index["files"]["pub_00.json"]
        save_json(self.raw / "index.json", index)
        with self.assertRaisesRegex(AnalysisError, "indexed PUB/result files"):
            analyze(self.folder)

    def test_metric_digest_cardinality_rejected(self) -> None:
        index = self.read(self.raw / "index.json")
        index["metrics_sha256"] = []
        save_json(self.raw / "index.json", index)
        with self.assertRaisesRegex(AnalysisError, "metric digest cardinality"):
            analyze(self.folder)

    def test_raw_pub_identity_rejected(self) -> None:
        self.mutate_indexed_pub(lambda payload: payload.update(pub_name="wrong_identity"))
        with self.assertRaisesRegex(AnalysisError, "raw PUB identity"):
            analyze(self.folder)

    def test_raw_pub_index_rejected(self) -> None:
        self.mutate_indexed_pub(lambda payload: payload.update(pub_index=True))
        with self.assertRaisesRegex(AnalysisError, "raw PUB identity"):
            analyze(self.folder)

    def test_extra_raw_register_rejected(self) -> None:
        self.mutate_indexed_pub(
            lambda payload: payload["registers"].update(extra=copy.deepcopy(next(iter(payload["registers"].values()))))
        )
        with self.assertRaisesRegex(AnalysisError, "raw registers differ"):
            analyze(self.folder)

    def test_second_replica_rejected(self) -> None:
        def update(record):
            pub = record["execution_pubs"][0]
            pub["components"][0]["registers_by_replica"].append(["another_replica"])
            record["submission"]["jobs"][0]["pubs"][0] = copy.deepcopy(pub)

        self.mutate_record(update)
        with self.assertRaisesRegex(AnalysisError, "exactly one replica"):
            analyze(self.folder)

    def test_duplicate_member_rejected(self) -> None:
        def update(record):
            pub = record["execution_pubs"][1]
            pub["components"][0]["member"] = "qpe_archived_s0"
            record["submission"]["jobs"][0]["pubs"][1] = copy.deepcopy(pub)

        self.mutate_record(update)
        with self.assertRaisesRegex(AnalysisError, "repeated folded member"):
            analyze(self.folder)

    def test_incomplete_submission_rejected(self) -> None:
        self.mutate_record(lambda record: record["submission"].update(complete=False))
        with self.assertRaisesRegex(AnalysisError, "submission must be complete"):
            analyze(self.folder)

    def test_path_escape_rejected(self) -> None:
        index = self.read(self.raw / "index.json")
        index["metrics"] = ["../outside.json"]
        index["metrics_latest"] = "../outside.json"
        save_json(self.raw / "index.json", index)
        with self.assertRaisesRegex(AnalysisError, "unsafe file name"):
            analyze(self.folder)

    def test_duplicate_json_key_rejected(self) -> None:
        (self.folder / "record.json").write_text('{"shots": 1, "shots": 2}')
        with self.assertRaisesRegex(AnalysisError, "duplicate key"):
            analyze(self.folder)

    def test_archive_digest_mismatch_rejected(self) -> None:
        (self.folder / "isa.qpy").write_bytes(b"changed archive")
        with self.assertRaisesRegex(AnalysisError, "submission archive digest"):
            analyze(self.folder)

    def test_immutable_ledger_difference_rejected(self) -> None:
        self.mutate_record(
            lambda record: record["submission"]["planned_jobs"][0]["options"].update(changed=True),
            sync_ledger=False,
        )
        with self.assertRaisesRegex(AnalysisError, "immutable planned ledger"):
            analyze(self.folder)

    def test_record_schema_rejected(self) -> None:
        self.mutate_record(lambda record: record.update(schema_version=True))
        with self.assertRaisesRegex(AnalysisError, "record schema"):
            analyze(self.folder)

    def test_experiment_digest_rejected(self) -> None:
        self.mutate_record(lambda record: record.update(experiment_digest="synthetic"))
        with self.assertRaisesRegex(AnalysisError, "experiment digest"):
            analyze(self.folder)


if __name__ == "__main__":
    unittest.main()
