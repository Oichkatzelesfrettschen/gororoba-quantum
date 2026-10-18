"""Behavioral contracts for changed-input replay selection and timing records."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

import run_gates


class SelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.write("ci/full_gate_inputs.json", json.dumps({"gates": {"long": ["data/**"]}}))
        self.write("entry.py", "def run():\n import helper\n")
        self.write("helper.py", "import leaf\n")
        self.write("leaf.py", "")
        self.gates: list[dict[str, Any]] = [
            {"name": "fast", "cwd": ".", "cmd": "true"},
            {"name": "long", "cwd": ".", "cmd": '"$PYTHON" entry.py', "tier": "full"},
        ]
        self.write("ci/gates.json", json.dumps({"gates": self.gates}))

    def write(self, name: str, text: str) -> None:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def chosen(self, *paths: str) -> list[str]:
        return [gate["name"] for gate in run_gates.select(self.root, "pr", changed=list(paths))]

    def test_transitive_and_function_local_sources(self) -> None:
        for path in ("entry.py", "helper.py", "leaf.py", "data/new/record.json", "requirements.txt"):
            with self.subTest(path=path):
                self.assertEqual(self.chosen(path), ["fast", "long"])
        self.assertEqual(self.chosen("unrelated.md"), ["fast"])
        self.assertEqual(self.chosen(), ["fast"])

    def test_deleted_import_still_selects(self) -> None:
        self.write("helper.py", "import deleted\n")
        self.assertEqual(self.chosen("deleted.py"), ["fast", "long"])

    def test_source_digest_literal(self) -> None:
        self.write("entry.py", "SOURCES = ('helper.py',)\n")
        self.assertEqual(self.chosen("leaf.py"), ["fast", "long"])

    def test_deleted_source_digest_literal(self) -> None:
        self.write("entry.py", "SOURCES = ('deleted.py',)\n")
        self.assertEqual(self.chosen("deleted.py"), ["fast", "long"])

    def test_timing_analysis_denominators(self) -> None:
        import analyze_timings

        job = {
            "name": "gates 0/1",
            "conclusion": "success",
            "created_at": "2026-01-01T00:00:00Z",
            "started_at": "2026-01-01T00:00:02Z",
            "completed_at": "2026-01-01T00:00:12Z",
            "steps": [
                {"name": "Run shard", "started_at": "2026-01-01T00:00:04Z", "completed_at": "2026-01-01T00:00:12Z"}
            ],
        }
        report = analyze_timings.analyze(
            [job],
            "gates 0/1\tRun shard\tPASS fast 7.0s  command\ngates 0/1\tRun shard\tPASS long 8.0s  command\n",
            {"gates": [dict(gate, seconds=1) for gate in self.gates]},
        )
        self.assertEqual(report["workflow_seconds"], 12)
        delayed = analyze_timings.analyze(
            [job],
            "",
            {"gates": []},
            {
                "id": 1,
                "event": "push",
                "head_sha": "abc",
                "created_at": "2025-12-31T23:59:00Z",
                "run_started_at": job["created_at"],
            },
        )
        self.assertEqual(delayed["created_to_first_job_seconds"], 60)
        self.assertEqual(delayed["workflow_seconds"], 72)
        self.assertEqual(report["runner_seconds"], 10)
        self.assertEqual(report["gate_elapsed_seconds"], 15)
        self.assertEqual(report["stage_runner_seconds"]["Run shard"], 8)
        manifest = {"gates": [{"name": "fast", "seconds": 1}]}
        analyze_timings.refresh(manifest, [report])
        self.assertEqual(manifest["gates"][0]["seconds"], 7)

    def test_manifest_coverage_and_scope_validation(self) -> None:
        for manifest in ({}, {"long": ["../outside"]}, {"long": "data/**"}):
            self.write("ci/full_gate_inputs.json", json.dumps({"gates": manifest}))
            with self.assertRaises(ValueError):
                self.chosen("unrelated.md")

    def test_toolchain_filter_preserves_full_manifest_validation(self) -> None:
        self.gates[1]["requires"] = ["qi"]
        self.write("ci/gates.json", json.dumps({"gates": self.gates}))
        selected = run_gates.select(self.root, "pr", requires="qi", changed=["helper.py"])
        self.assertEqual([gate["name"] for gate in selected], ["long"])

    def test_timing_record_and_failure_keep_going(self) -> None:
        import contextlib
        import io

        self.gates[0]["cmd"] = "exit 1"
        self.gates[1]["cmd"] = "true"
        self.write("ci/gates.json", json.dumps({"gates": self.gates}))
        record = self.root / "timings.json"
        with patch.object(run_gates, "ROOT", self.root), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run_gates.main(["--timings", str(record)]), 1)
        result = json.loads(record.read_text())
        self.assertEqual([(row["name"], row["status"]) for row in result["gates"]], [("fast", 1), ("long", 0)])
        self.assertGreater(result["wall_seconds"], 0)

    def test_workflow_diff_failure_selects_exhaustive_checks(self) -> None:
        import subprocess

        import changed_paths

        destination = self.root / "changed.bin"
        for base in ("", "0" * 40):
            with patch.object(changed_paths.subprocess, "run") as run:
                flags = changed_paths.select(self.root, "pull_request", base, destination)
                self.assertFalse(flags["limited"])
                self.assertTrue(flags["rocq"])
                run.assert_not_called()
        passed = subprocess.CompletedProcess([], 0, stdout=b"")
        failed = subprocess.CompletedProcess([], 128, stdout=b"")
        for responses in ([failed], [passed, failed]):
            with patch.object(changed_paths.subprocess, "run", side_effect=responses):
                flags = changed_paths.select(self.root, "push", "missing", destination)
                self.assertEqual(flags, {"rocq": True, "full": True, "limited": False})
        paths = b"old.py\0new name.py\0"
        difference = subprocess.CompletedProcess([], 0, stdout=paths)
        predicate = subprocess.CompletedProcess([], 1, stdout=b"")
        with patch.object(changed_paths.subprocess, "run", side_effect=[passed, difference, predicate]):
            flags = changed_paths.select(self.root, "pull_request", "base", destination)
            self.assertEqual(flags, {"rocq": False, "full": False, "limited": True})
            self.assertEqual(destination.read_bytes(), paths)

    def test_thread_defaults_and_explicit_override(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            environment = run_gates.environment_for(None)
            self.assertEqual(environment["OMP_NUM_THREADS"], "1")
            self.assertEqual(environment["OPENBLAS_NUM_THREADS"], "1")
        with patch.dict("os.environ", {"OMP_NUM_THREADS": "2"}, clear=True):
            self.assertEqual(run_gates.environment_for(None)["OMP_NUM_THREADS"], "2")


if __name__ == "__main__":
    unittest.main()
