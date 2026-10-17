"""Mock-only checks of one-batch submission recovery and immutable shot retention.

Every service constructor is replaced before use. These fixtures create no
remote resources, read no credentials and simulate no quantum circuit.
"""

from __future__ import annotations

import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import patch

import qi_platform as platform


class FakeToolError(RuntimeError):
    """SDK-free stand-in for the MCP tool error envelope."""


class FakeServer:
    def __init__(self, name: str) -> None:
        self.tools: dict[str, Any] = {}

    def tool(self, **kwargs: Any) -> Any:
        def register(function: Any) -> Any:
            self.tools[function.__name__] = function
            return function

        return register


def mcp_with_stubs() -> Any:
    """Import the actual tool functions without installing or contacting the SDK."""
    names = (
        "mcp",
        "mcp.server",
        "mcp.server.mcpserver",
        "mcp.server.mcpserver.exceptions",
        "mcp.types",
    )
    modules = {name: ModuleType(name) for name in names}
    modules["mcp.server.mcpserver"].MCPServer = FakeServer  # type: ignore[attr-defined]
    modules["mcp.server.mcpserver.exceptions"].ToolError = FakeToolError  # type: ignore[attr-defined]
    modules["mcp.types"].ToolAnnotations = dict  # type: ignore[attr-defined]
    spec = importlib.util.spec_from_file_location(
        "qi_mcp_retention_fixture", Path(__file__).with_name("qi_mcp_server.py")
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the MCP server fixture")
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module


class FakeClient:
    """A recording transport whose only remote state is this Python object."""

    member_id = 1

    def __init__(self, case_dir: Path, *, enqueue_timeout: bool = False, fail_create: bool = False) -> None:
        self.case_dir = case_dir
        cases = json.loads((case_dir / "cases.json").read_text())
        self.backend_type_id = cases["backend_type_id"]
        self.enqueue_timeout = enqueue_timeout
        self.fail_create = fail_create
        self.calls: list[tuple[str, str]] = []
        self.next_id = 100
        self.jobs: dict[int, dict[str, Any]] = {}
        self.batch: dict[str, Any] = {
            "id": 100,
            "status": "planned",
            "backend_type_id": self.backend_type_id,
            "job_ids": [],
        }
        self.results: dict[int, dict[str, Any]] = {}
        self.fail_queue = False
        self.queue_count = 0
        self.backend = {
            "identifier": cases["backend"],
            "nqubits": 17,
            "status": "idle",
            "is_hardware": True,
            "max_jobs_per_batch_job": 5,
            "max_number_of_shots": 16384,
            "batchjobs_per_queue_limit": 5,
        }
        self.uploaded_sources: list[str] = []

    def get(self, path: str, **params: Any) -> Any:
        self.calls.append(("GET", path))
        if path == f"/backend_types/{self.backend_type_id}":
            return self.backend
        if path == f"/backend_types/{self.backend_type_id}/queue":
            if params != {"user_only": True}:
                raise AssertionError("submission queue preflight did not select the current user")
            if self.fail_queue:
                raise TimeoutError("synthetic queue timeout")
            return {"number_of_jobs_in_queue": self.queue_count}
        if path.startswith("/results/job/"):
            return {"items": [copy.deepcopy(self.results[int(path.rsplit("/", 1)[1])])]}
        if path.startswith("/jobs/"):
            return copy.deepcopy(self.jobs[int(path.rsplit("/", 1)[1])])
        raise AssertionError(f"unexpected mock GET {path}")

    def pages(self, path: str, **params: Any) -> list[dict[str, Any]]:
        self.calls.append(("GET", path))
        if path == "/languages":
            return [{"id": 1, "name": "cQASM", "version": "3.0"}]
        if path == "/transactions/":
            return []
        if path == "/batch_jobs" and params == {"id": self.batch["id"]}:
            return [copy.deepcopy(self.batch)]
        raise AssertionError(f"unexpected mock paginated GET {path} {params}")

    def post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        if not (self.case_dir / "submission-state.json").is_file():
            raise AssertionError("remote creation happened without a retained submission guard")
        self.calls.append(("POST", path))
        if self.fail_create:
            raise TimeoutError("synthetic creation response lost")
        self.next_id += 1
        if path == "/batch_jobs":
            self.batch["id"] = self.next_id
        if path == "/files":
            self.uploaded_sources.append(body["content"])
        if path == "/jobs":
            self.jobs[self.next_id] = {"id": self.next_id, "status": "planned", **body}
            self.batch["job_ids"].append(self.next_id)
        return {"id": self.next_id}

    def patch(self, path: str) -> None:
        state = json.loads((self.case_dir / "submission-state.json").read_text())
        if state["phase"] != "enqueue_outcome_unknown" or "submission" not in state:
            raise AssertionError("enqueue intent was not durably checkpointed")
        candidate = state["submission"]
        if candidate["state"] != "created" or "submitted_utc" in candidate:
            raise AssertionError("receipt claimed enqueue before the service accepted it")
        for row in candidate["jobs"]:
            if row["sha256"] != hashlib.sha256((self.case_dir / row["file"]).read_bytes()).hexdigest():
                raise AssertionError("candidate did not bind the uploaded circuit bytes")
        self.calls.append(("PATCH", path))
        self.batch["status"] = "queued"
        if self.enqueue_timeout:
            raise TimeoutError("synthetic lost enqueue response after acceptance")


ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "results/quantum_inspire/cases"


class PreflightReached(Exception):
    """Raised at submit's first request after every manifest and queue check passed."""


class PreflightClient:
    """A hardware backend that accepts the manifest's backend and shots and stops at the language lookup."""

    member_id = 1

    def __init__(self, cases: dict[str, Any]) -> None:
        self.cases = cases
        catalogue = json.loads((ROOT / "docs/evidence/quantum_inspire/catalogue.json").read_text())
        self.backend = next(row for row in catalogue["backend_types"] if row["id"] == cases["backend_type_id"])

    def get(self, path: str, **params: Any) -> Any:
        if path == f"/backend_types/{self.cases['backend_type_id']}":
            return {
                "identifier": self.cases["backend"],
                "name": self.cases["backend"],
                "status": "idle",
                "is_hardware": True,
                "nqubits": self.backend["nqubits"],
                "max_jobs_per_batch_job": 5,
                "max_number_of_shots": self.cases["shots"],
                "batchjobs_per_queue_limit": 5,
            }
        if path == f"/backend_types/{self.cases['backend_type_id']}/queue":
            return {"number_of_jobs_in_queue": 0}
        raise AssertionError(f"unexpected preflight GET {path}")

    def pages(self, path: str, **params: Any) -> list[dict[str, Any]]:
        raise PreflightReached(path)

    def post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        raise AssertionError("a preflight check created a remote resource")


class GeneratedCaseChecks(unittest.TestCase):
    def test_every_generated_batch_passes_hardware_submission_checks(self) -> None:
        manifests = [
            path
            for path in sorted(CASES.rglob("cases.json"))
            if isinstance(json.loads(path.read_text(encoding="utf-8")).get("circuits"), list)
        ]
        self.assertTrue(manifests)
        for manifest in manifests:
            with self.subTest(case=manifest.parent.relative_to(CASES).as_posix()):
                cases = json.loads(manifest.read_text(encoding="utf-8"))
                self.assertLessEqual(len(cases["circuits"]), platform.HARDWARE_BATCH_CIRCUITS)
                with tempfile.TemporaryDirectory() as scratch:
                    case_dir = Path(scratch) / manifest.parent.name
                    case_dir.mkdir()
                    for name in ["cases.json", *(row["file"] for row in cases["circuits"])]:
                        (case_dir / name).write_bytes((manifest.parent / name).read_bytes())
                    with patch.object(platform, "Client", return_value=PreflightClient(cases)):
                        with self.assertRaises(PreflightReached):
                            platform.submit(case_dir, cases["backend_type_id"], "preflight fixture")
                    self.assertFalse((case_dir / "submission-state.json").exists())

    def test_zero_divisor_routing_constants_follow_the_catalogue(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        import qi_zero_divisor_cases as zero_divisor

        zero_divisor.catalogue_check()
        for name, value in (("TUNA17", zero_divisor.TUNA17[1:]), ("NQUBITS", 18), ("BACKEND_TYPE_ID", 6)):
            with self.subTest(constant=name), patch.object(zero_divisor, name, value):
                with self.assertRaises(SystemExit):
                    zero_divisor.catalogue_check()

    def test_retained_zero_divisor_runs_reproduce_through_their_batched_series(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        import qi_zero_divisor_cases as zero_divisor

        for name in ("zero_divisor_tuna_17", "zero_divisor_qx"):
            with self.subTest(series=name), tempfile.TemporaryDirectory() as scratch:
                retained = ROOT / f"results/quantum_inspire/runs/2026-10-16T221133Z-{name}"
                # The retained record keeps the placement it executed; its batches
                # come from the recorded manifest split by finish(), whatever
                # regions the current generator places.
                recorded = json.loads((retained / "cases.json").read_text(encoding="utf-8"))
                sources = {
                    row["file"]: (retained / row["file"]).read_text(encoding="utf-8") for row in recorded["circuits"]
                }
                manifests = {
                    path: text
                    for path, text in zero_divisor.finish(recorded, sources).items()
                    if path.endswith("/cases.json")
                }
                runs = []
                for path, text in sorted(manifests.items()):
                    run = Path(scratch) / Path(path).parent.name
                    (run / "raw").mkdir(parents=True)
                    (run / "cases.json").write_text(text, encoding="utf-8")
                    for row in json.loads(text)["circuits"]:
                        raw = f"raw/{row['file']}.json"
                        (run / raw).write_bytes((retained / raw).read_bytes())
                    runs.append(run)
                self.assertGreater(len(runs), 1)
                record = zero_divisor.analyze(runs)
                text = json.dumps(record, indent=1) + "\n"
                if name == "zero_divisor_qx":
                    self.assertEqual(text, (retained / "analysis.json").read_text(encoding="utf-8"))
                else:
                    # Every batch resamples its own copy of the retained readout
                    # pair, so only the corrected bootstrap block departs from
                    # the single-batch record; every point estimate is equal.
                    expected = json.loads((retained / "analysis.json").read_text(encoding="utf-8"))
                    for analysis_record in (record, expected):
                        analysis_record["secondary"].pop("readout_corrected_bootstrap")
                    self.assertEqual(record, expected)
                    with self.assertRaisesRegex(SystemExit, "analyze every batch together"):
                        zero_divisor.analyze(runs[:1])
                    manifest_path = runs[1] / "cases.json"
                    original = manifest_path.read_bytes()
                    manifest = json.loads(original)
                    manifest["circuits"] = [row for row in manifest["circuits"] if row["file"] != "readout-1.cq"]
                    manifest_path.write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
                    with self.assertRaisesRegex(SystemExit, "readout"):
                        zero_divisor.analyze(runs)
                    manifest_path.write_bytes(original)
                analysis = Path(scratch) / "analysis.json"
                analysis.write_text(text, encoding="utf-8")
                command = [sys.executable, "-B", str(ROOT / "scripts/qi_zero_divisor_cases.py"), "--replay-series"]
                replay = subprocess.run([*command, str(analysis), *map(str, runs)], capture_output=True, text=True)
                self.assertEqual(replay.returncode, 0, replay.stderr)
                analysis.write_text(text.replace('"shots": ', '"shots":  ', 1), encoding="utf-8")
                replay = subprocess.run([*command, str(analysis), *map(str, runs)], capture_output=True, text=True)
                self.assertIn("differs from the recomputation", replay.stderr)


class RegisterWidthChecks(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.case_dir = Path(self.directory.name)

    def fixture(
        self,
        programs: list[str],
        batch_width: Any,
        *,
        row_widths: list[Any] | None = None,
        backend_width: Any = 17,
        backend: tuple[str, int] = ("tuna_17", 7),
    ) -> FakeClient:
        rows = []
        for index, source in enumerate(programs):
            name = f"width-{index}.cq"
            (self.case_dir / name).write_bytes(source.encode())
            row: dict[str, Any] = {"file": name, "sha256": hashlib.sha256(source.encode()).hexdigest()}
            if row_widths is not None:
                row["nqubits"] = row_widths[index]
            rows.append(row)
        cases = {
            "backend": backend[0],
            "backend_type_id": backend[1],
            "nqubits": batch_width,
            "shots": 4,
            "circuits": rows,
        }
        (self.case_dir / "cases.json").write_text(json.dumps(cases))
        client = FakeClient(self.case_dir)
        client.backend.update(nqubits=backend_width, is_hardware=backend[1] != 1)
        return client

    def submit(self, client: FakeClient) -> None:
        with patch.object(platform, "Client", return_value=client):
            platform.submit(self.case_dir, client.backend_type_id, "width fixture approval")

    def refused(self, client: FakeClient, pattern: str, error: type[BaseException] = SystemExit) -> None:
        with self.assertRaisesRegex(error, pattern):
            self.submit(client)
        self.assertTrue(all(method == "GET" for method, _ in client.calls))
        self.assertEqual(client.uploaded_sources, [])
        self.assertFalse((self.case_dir / "submission-state.json").exists())
        self.assertFalse((self.case_dir / "submission.json").exists())

    def test_eighteen_qubits_cannot_reach_tuna17(self) -> None:
        client = self.fixture(["version 3.0\nqubit[18] q\ninit q\n"], 18)
        self.refused(client, "declared width 18 exceeds backend nqubits 17")
        self.assertEqual(client.calls, [("GET", "/backend_types/7")])

    def test_individual_registers_are_summed_against_capacity(self) -> None:
        client = self.fixture(["version 3.0\nqubit[9] a\nqubit[9] b\n"], 18)
        self.refused(client, "declared width 18 exceeds backend nqubits 17")

    def test_backend_capacity_is_not_inferred_from_case_metadata(self) -> None:
        client = self.fixture(["version 3.0\nqubit[17] q\n"], 17, backend_width=9)
        self.refused(client, "declared width 17 exceeds backend nqubits 9")

    def test_understated_overstated_and_invalid_manifest_widths_refuse_locally(self) -> None:
        source = "version 3.0\nqubit[17] q\n"
        for width in (16, 18, 0, -1, True, "17", None):
            with self.subTest(nqubits=width):
                client = self.fixture([source], width)
                self.refused(client, "nqubits")
                self.assertEqual(client.calls, [])

    def test_mixed_qx_batch_retains_exact_widths_and_source_bytes(self) -> None:
        sources = ["version 3.0\r\nqubit[2] q\r\n", "version 3.0\nqubit[8] q\n"]
        client = self.fixture(sources, 8, row_widths=[2, 8], backend_width=10, backend=("QXsinglenodesimulator", 1))
        self.submit(client)
        self.assertEqual(client.uploaded_sources, sources)
        self.assertEqual(sum(method == "PATCH" for method, _ in client.calls), 1)

    def test_mixed_batch_rejects_missing_or_inexact_per_circuit_widths(self) -> None:
        sources = ["version 3.0\nqubit[2] q\n", "version 3.0\nqubit[8] q\n"]
        for row_widths, batch_width in ((None, 8), ([8, 8], 8), ([2, 7], 8), ([2, 8], 9), ([True, 8], 8)):
            with self.subTest(row_widths=row_widths, batch_width=batch_width):
                client = self.fixture(sources, batch_width, row_widths=row_widths)
                self.refused(client, "nqubits")
                self.assertEqual(client.calls, [])

    def test_scalar_and_multiple_registers_ignore_commented_declarations(self) -> None:
        source = (
            "version 3.0\n// qubit[999] omitted\n/* qubit[99] omitted */\n"
            "qubit[16] data; qubit ancilla // qubit[100] omitted\n"
            '@name("qubit[999] text")\n'
        )
        client = self.fixture([source], 17)
        self.submit(client)
        self.assertEqual(client.uploaded_sources, [source])

    def test_legacy_ry_qubits_declaration_remains_admissible(self) -> None:
        source = "version 1.0\n# qubits 999\nQUBITS 9\nx q[0]\n"
        client = self.fixture([source], 9, backend_width=9, backend=("Rydberg", 5))
        self.submit(client)
        self.assertEqual(client.uploaded_sources, [source])

    def test_missing_malformed_and_ambiguous_declarations_refuse_locally(self) -> None:
        declarations = (
            "// qubit[2] q\nX q[0]",
            "qubit[0] q",
            "qubit[-2] q",
            "qubit[1+1] q",
            "qubit[N] q",
            "qubit[2] q\nqubit[2] q",
            "qubits 2\nqubit q",
            "qubits 2\nqubits 2",
            "qubit[2] q, other",
            "qubit[2] q /* unterminated",
            'qubit[2] q\n@name("unterminated)',
        )
        for declaration in declarations:
            with self.subTest(declaration=declaration):
                client = self.fixture([f"version 3.0\n{declaration}\n"], 2)
                self.refused(client, "cQASM")
                self.assertEqual(client.calls, [])

    def test_invalid_backend_capacity_refuses_before_remote_mutation(self) -> None:
        for capacity in (None, 0, -1, True, "17"):
            with self.subTest(nqubits=capacity):
                client = self.fixture(["version 3.0\nqubit[2] q\n"], 2, backend_width=capacity)
                self.refused(client, "backend nqubits capacity", platform.PlatformError)
                self.assertEqual(client.calls, [("GET", "/backend_types/7")])


class RetentionChecks(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.case_dir = Path(self.directory.name)
        source = "version 3.0\nqubit[2] q\nX q[0]\n"
        (self.case_dir / "one.cq").write_text(source)
        self.cases: dict[str, Any] = {
            "backend": "tuna_17",
            "backend_type_id": 7,
            "nqubits": 2,
            "shots": 4,
            "circuits": [{"file": "one.cq", "sha256": hashlib.sha256(source.encode()).hexdigest()}],
        }
        (self.case_dir / "cases.json").write_text(json.dumps(self.cases))
        self.output = io.StringIO()
        self.addCleanup(self.output.close)

    def submit(self, client: FakeClient) -> None:
        with patch.object(platform, "Client", return_value=client), contextlib.redirect_stdout(self.output):
            platform.submit(self.case_dir, 7, "fixture approval for one batch")

    def reconcile(self, client: FakeClient) -> None:
        with patch.object(platform, "Client", return_value=client), contextlib.redirect_stdout(self.output):
            platform.reconcile(self.case_dir)

    def assert_retry_blocked(self) -> None:
        with patch.object(platform, "Client", side_effect=AssertionError("retry reached the service")):
            with self.assertRaisesRegex(SystemExit, "exists"):
                platform.submit(self.case_dir, 7, "fixture approval for one batch")

    def test_success_and_historical_receipts_block_repeats(self) -> None:
        client = FakeClient(self.case_dir)
        self.submit(client)
        path = self.case_dir / "submission.json"
        record = json.loads(path.read_text())
        self.assertEqual(record["schema"], "qi-submission-v2")
        self.assertEqual(record["state"], "enqueued")
        self.assertIn("created_utc", record)
        self.assertIn("submitted_utc", record)
        self.assertEqual(record["jobs"][0]["sha256"], self.cases["circuits"][0]["sha256"])
        self.assertEqual(
            record["cases_sha256"], hashlib.sha256((self.case_dir / "cases.json").read_bytes()).hexdigest()
        )
        self.assertTrue(record["queue_user_only"])
        self.assertEqual(record["queue_limit_at_submit"], 1)
        self.assertEqual(sum(method == "PATCH" for method, _ in client.calls), 1)
        self.assert_retry_blocked()
        record["schema"] = "qi-submission-v1"
        del record["cases_sha256"]
        path.write_text(json.dumps(record))
        (self.case_dir / "submission-state.json").unlink()
        self.assert_retry_blocked()

    def test_queue_failure_happens_before_remote_creation(self) -> None:
        client = FakeClient(self.case_dir)
        client.fail_queue = True
        with self.assertRaises(TimeoutError):
            self.submit(client)
        self.assertFalse(any(method != "GET" for method, _ in client.calls))
        self.assertFalse((self.case_dir / "submission-state.json").exists())

    def test_queue_limits_refuse_before_remote_creation(self) -> None:
        # Hardware admits one queued batch of the account at a time; emulators use the API capacity.
        for hardware, limit, queued in ((True, 5, 1), (True, 2, 1), (False, 5, 5)):
            with self.subTest(hardware=hardware, limit=limit, queued=queued):
                client = FakeClient(self.case_dir)
                client.backend.update(is_hardware=hardware, batchjobs_per_queue_limit=limit)
                client.queue_count = queued
                with self.assertRaisesRegex(SystemExit, "current-user queue"):
                    self.submit(client)
                self.assertFalse(any(method != "GET" for method, _ in client.calls))
                self.assertFalse((self.case_dir / "submission-state.json").exists())

    def test_emulator_queue_uses_api_capacity(self) -> None:
        client = FakeClient(self.case_dir)
        client.backend["is_hardware"] = False
        client.queue_count = 4
        self.submit(client)
        record = json.loads((self.case_dir / "submission.json").read_text())
        self.assertEqual(record["queue_limit_at_submit"], 5)
        self.assertEqual(record["queue_at_submit"]["number_of_jobs_in_queue"], 4)

    def test_hardware_batch_holds_at_most_three_circuits(self) -> None:
        source = (self.case_dir / "one.cq").read_bytes()
        circuit_digest = hashlib.sha256(source).hexdigest()
        # Six breaks the API batch limit, four and five the hardware cap of three
        # circuits per batch; three submits.
        for count, refusal in ((6, "max_jobs_per_batch_job"), (5, "hardware batch"), (4, "hardware batch"), (3, None)):
            with self.subTest(circuits=count):
                self.cases["circuits"] = []
                for index in range(count):
                    filename = f"queue-{index}.cq"
                    (self.case_dir / filename).write_bytes(source)
                    self.cases["circuits"].append({"file": filename, "sha256": circuit_digest})
                (self.case_dir / "cases.json").write_text(json.dumps(self.cases))
                client = FakeClient(self.case_dir)
                if refusal:
                    with self.assertRaisesRegex(SystemExit, refusal):
                        self.submit(client)
                    self.assertTrue(all(method == "GET" for method, _ in client.calls))
                    self.assertFalse((self.case_dir / "submission-state.json").exists())
                else:
                    self.submit(client)
                    record = json.loads((self.case_dir / "submission.json").read_text())
                    self.assertEqual(len(record["jobs"]), 3)
                    self.assertEqual(sum(method == "PATCH" for method, _ in client.calls), 1)

    def test_circuit_wider_than_backend_is_refused_before_remote_creation(self) -> None:
        source = "version 3.0\nqubit[17] q\nqubit r\nX q[0]\n"
        (self.case_dir / "one.cq").write_text(source)
        self.cases["nqubits"] = 18
        self.cases["circuits"][0]["sha256"] = hashlib.sha256(source.encode()).hexdigest()
        (self.case_dir / "cases.json").write_text(json.dumps(self.cases))
        client = FakeClient(self.case_dir)
        with self.assertRaisesRegex(SystemExit, "declared width 18"):
            self.submit(client)
        self.assertTrue(all(method == "GET" for method, _ in client.calls))
        self.assertFalse((self.case_dir / "submission-state.json").exists())

    def test_source_bytes_are_the_uploaded_program(self) -> None:
        source = (self.case_dir / "one.cq").read_bytes().replace(b"\n", b"\r\n")
        (self.case_dir / "one.cq").write_bytes(source)
        self.cases["circuits"][0]["sha256"] = hashlib.sha256(source).hexdigest()
        (self.case_dir / "cases.json").write_text(json.dumps(self.cases))
        client = FakeClient(self.case_dir)
        self.submit(client)
        self.assertEqual([text.encode("utf-8") for text in client.uploaded_sources], [source])

    def test_directory_sync_failure_precedes_remote_creation(self) -> None:
        client = FakeClient(self.case_dir)
        fsync = os.fsync

        def fail_directory(descriptor: int) -> None:
            if stat.S_ISDIR(os.fstat(descriptor).st_mode):
                raise OSError("synthetic directory sync failure")
            fsync(descriptor)

        with patch.object(platform.os, "fsync", side_effect=fail_directory):
            with self.assertRaisesRegex(OSError, "directory sync failure"):
                self.submit(client)
        self.assertFalse(any(method != "GET" for method, _ in client.calls))
        self.assertTrue((self.case_dir / "submission-state.json").exists())
        self.assert_retry_blocked()

    def test_lost_creation_response_blocks_repeat(self) -> None:
        client = FakeClient(self.case_dir, fail_create=True)
        with self.assertRaises(TimeoutError):
            self.submit(client)
        self.assert_retry_blocked()
        self.assertEqual(sum(method == "POST" for method, _ in client.calls), 1)

    def test_lost_enqueue_response_recovers_without_resubmission(self) -> None:
        client = FakeClient(self.case_dir, enqueue_timeout=True)
        with self.assertRaises(TimeoutError):
            self.submit(client)
        self.assertFalse((self.case_dir / "submission.json").exists())
        self.assertEqual(
            json.loads((self.case_dir / "submission-state.json").read_text())["phase"], "enqueue_outcome_unknown"
        )
        self.assertEqual(
            json.loads((self.case_dir / "submission-state.json").read_text())["submission"]["state"], "created"
        )
        self.assert_retry_blocked()
        prior_mutations = [call for call in client.calls if call[0] != "GET"]
        self.reconcile(client)
        self.assertTrue((self.case_dir / "submission.json").is_file())
        receipt_path = self.case_dir / "submission.json"
        self.assertEqual(json.loads(receipt_path.read_text())["state"], "enqueued")
        before = receipt_path.read_bytes()
        with patch.object(platform, "now", return_value="later reconciliation"):
            self.reconcile(client)
        self.assertEqual(receipt_path.read_bytes(), before)
        self.assertEqual([call for call in client.calls if call[0] != "GET"], prior_mutations)

    def test_receipt_write_failure_recovers_from_enqueued_checkpoint(self) -> None:
        client = FakeClient(self.case_dir)
        with patch.object(platform, "_retain_json", side_effect=OSError("synthetic receipt publication failure")):
            with self.assertRaises(OSError):
                self.submit(client)
        self.assert_retry_blocked()
        self.reconcile(client)
        self.assertTrue((self.case_dir / "submission.json").is_file())
        self.assertEqual(sum(method == "PATCH" for method, _ in client.calls), 1)

    def test_planned_batch_is_never_automatically_enqueued(self) -> None:
        client = FakeClient(self.case_dir, enqueue_timeout=True)
        with self.assertRaises(TimeoutError):
            self.submit(client)
        client.batch["status"] = "planned"
        with self.assertRaisesRegex(platform.PlatformError, "enqueue is unconfirmed"):
            self.reconcile(client)
        self.assertFalse((self.case_dir / "submission.json").exists())
        self.assert_retry_blocked()
        self.assertEqual(sum(method == "PATCH" for method, _ in client.calls), 1)

    def test_reconcile_statuses_match_captured_openapi(self) -> None:
        path = Path(__file__).resolve().parents[1] / "docs/notes/quantum_inspire/api/openapi.json"
        spec = json.loads(path.read_text())
        states = set(spec["components"]["schemas"]["BatchJobStatus"]["enum"])
        self.assertEqual(platform.ENQUEUED_BATCH_STATUSES, states - {"planned"})
        self.assertIn("get", spec["paths"]["/batch_jobs"])
        self.assertIn("id", {item["name"] for item in spec["paths"]["/batch_jobs"]["get"]["parameters"]})
        queue_parameters = spec["paths"]["/backend_types/{id}/queue"]["get"]["parameters"]
        user_only = next(item for item in queue_parameters if item["name"] == "user_only")
        self.assertEqual(user_only["schema"]["type"], "boolean")

    def test_reconcile_rejects_changed_candidate_digest_before_service(self) -> None:
        client = FakeClient(self.case_dir, enqueue_timeout=True)
        with self.assertRaises(TimeoutError):
            self.submit(client)
        state_path = self.case_dir / "submission-state.json"
        state = json.loads(state_path.read_text())
        state["submission"]["cases_sha256"] = "0" * 64
        state_path.write_text(json.dumps(state))
        with patch.object(platform, "Client", side_effect=AssertionError("changed receipt reached the service")):
            with self.assertRaisesRegex(platform.PlatformError, "receipt digest"):
                platform.reconcile(self.case_dir)
        self.assertFalse((self.case_dir / "submission.json").exists())

    def test_foreign_batch_job_cannot_recover_a_receipt(self) -> None:
        client = FakeClient(self.case_dir, enqueue_timeout=True)
        with self.assertRaises(TimeoutError):
            self.submit(client)
        client.batch["job_ids"].append(999)
        with self.assertRaisesRegex(platform.PlatformError, "checkpointed backend or jobs"):
            self.reconcile(client)
        self.assertFalse((self.case_dir / "submission.json").exists())

    def collection_client(self, *, two_jobs: bool = False) -> FakeClient:
        client = FakeClient(self.case_dir)
        files = ["one.cq", "two.cq"] if two_jobs else ["one.cq"]
        jobs: list[dict[str, Any]] = [{"file": file, "job": 10 + i} for i, file in enumerate(files)]
        (self.case_dir / "submission.json").write_text(
            json.dumps({"schema": "qi-submission-v1", "shots": 4, "batch_job": 20, "jobs": jobs})
        )
        for row in jobs:
            client.jobs[row["job"]] = {
                "id": row["job"],
                "status": "completed",
                "batch_job_id": 20,
                "number_of_shots": 4,
            }
            client.results[row["job"]] = {
                "job_id": row["job"],
                "shots_requested": 4,
                "shots_done": 4,
                "results": {"00": 2, "01": 2},
                "raw_data": ["00", "01", "00", "01"],
            }
        return client

    def collect(self, client: FakeClient) -> None:
        with patch.object(platform, "Client", return_value=client), contextlib.redirect_stdout(self.output):
            platform.collect(self.case_dir, poll=0, timeout=1)

    def bind_collection_receipt(self) -> dict[str, Any]:
        path = self.case_dir / "submission.json"
        record = json.loads(path.read_text())
        record.update(
            schema="qi-submission-v2",
            state="enqueued",
            backend=self.cases["backend"],
            backend_type_id=self.cases["backend_type_id"],
            cases_sha256=hashlib.sha256((self.case_dir / "cases.json").read_bytes()).hexdigest(),
        )
        digests = {row["file"]: row["sha256"] for row in self.cases["circuits"]}
        for row in record["jobs"]:
            row["sha256"] = digests[row["file"]]
        path.write_text(json.dumps(record))
        return record

    def test_collection_accepts_bound_v2_receipt(self) -> None:
        client = self.collection_client()
        self.bind_collection_receipt()
        self.collect(client)
        self.assertTrue((self.case_dir / "results.json").is_file())

    def test_collection_rejects_joint_source_and_manifest_edit_before_service(self) -> None:
        self.collection_client()
        self.bind_collection_receipt()
        source = b"version 3.0\nqubit[2] q\nX q[1]\n"
        (self.case_dir / "one.cq").write_bytes(source)
        self.cases["circuits"][0]["sha256"] = hashlib.sha256(source).hexdigest()
        (self.case_dir / "cases.json").write_text(json.dumps(self.cases))
        with patch.object(platform, "Client", side_effect=AssertionError("changed manifest reached the service")):
            with self.assertRaisesRegex(platform.PlatformError, "receipt digest"):
                platform.collect(self.case_dir, poll=0, timeout=1)
        self.assertFalse((self.case_dir / "raw").exists())

    def test_collection_rejects_missing_or_changed_receipt_digest(self) -> None:
        self.collection_client()
        record = self.bind_collection_receipt()
        for schema, digest in (
            ("qi-submission-v2", None),
            ("qi-submission-v2", "0" * 64),
            ("qi-submission-v1", "0" * 64),
        ):
            with self.subTest(schema=schema, digest=digest):
                mutated = {**record, "schema": schema}
                if digest is None:
                    del mutated["cases_sha256"]
                else:
                    mutated["cases_sha256"] = digest
                (self.case_dir / "submission.json").write_text(json.dumps(mutated))
                with patch.object(
                    platform, "Client", side_effect=AssertionError("invalid receipt reached the service")
                ):
                    with self.assertRaisesRegex(platform.PlatformError, "receipt digest"):
                        platform.collect(self.case_dir, poll=0, timeout=1)

    def test_collection_rejects_missing_or_changed_job_digest(self) -> None:
        self.collection_client()
        record = self.bind_collection_receipt()
        for digest in (None, "0" * 64):
            with self.subTest(digest=digest):
                mutated = copy.deepcopy(record)
                if digest is None:
                    del mutated["jobs"][0]["sha256"]
                else:
                    mutated["jobs"][0]["sha256"] = digest
                (self.case_dir / "submission.json").write_text(json.dumps(mutated))
                with patch.object(platform, "Client", side_effect=AssertionError("changed job digest reached service")):
                    with self.assertRaisesRegex(platform.PlatformError, "submission receipt sha256"):
                        platform.collect(self.case_dir, poll=0, timeout=1)

    def test_collection_requires_confirmed_v2_receipt(self) -> None:
        self.collection_client()
        record = self.bind_collection_receipt()
        for state in (None, "created"):
            with self.subTest(state=state):
                mutated = {**record, "state": state}
                (self.case_dir / "submission.json").write_text(json.dumps(mutated))
                with patch.object(
                    platform, "Client", side_effect=AssertionError("unconfirmed receipt reached service")
                ):
                    with self.assertRaisesRegex(platform.PlatformError, "receipt state|receipt is not enqueued"):
                        platform.collect(self.case_dir, poll=0, timeout=1)

    def test_identical_recollection_preserves_original_bytes(self) -> None:
        client = self.collection_client()
        self.collect(client)
        raw_path = self.case_dir / "raw/one.cq.json"
        raw_path.write_text('["00", "01", "00", "01"]\n\n')
        original = raw_path.read_bytes()
        original_stat = raw_path.stat().st_mtime_ns
        metadata = (self.case_dir / "results.json").read_bytes()
        with patch.object(platform, "now", return_value="later collection"):
            self.collect(client)
        self.assertEqual(raw_path.read_bytes(), original)
        self.assertEqual(raw_path.stat().st_mtime_ns, original_stat)
        self.assertEqual((self.case_dir / "results.json").read_bytes(), metadata)

    def test_same_histogram_different_order_is_rejected(self) -> None:
        client = self.collection_client()
        self.collect(client)
        before = (self.case_dir / "raw/one.cq.json").read_bytes()
        client.results[10]["raw_data"] = ["01", "00", "00", "01"]
        with self.assertRaisesRegex(platform.PlatformError, "conflicts with retained data"):
            self.collect(client)
        self.assertEqual((self.case_dir / "raw/one.cq.json").read_bytes(), before)

    def test_late_conflict_publishes_no_earlier_new_raw_file(self) -> None:
        client = self.collection_client(two_jobs=True)
        (self.case_dir / "raw").mkdir()
        conflict = self.case_dir / "raw/two.cq.json"
        conflict.write_text('["01", "00", "00", "01"]\n')
        before = conflict.read_bytes()
        with self.assertRaisesRegex(platform.PlatformError, "conflicts with retained data"):
            self.collect(client)
        self.assertFalse((self.case_dir / "raw/one.cq.json").exists())
        self.assertFalse((self.case_dir / "results.json").exists())
        self.assertEqual(conflict.read_bytes(), before)

    def test_invalid_provider_histogram_is_rejected_before_publication(self) -> None:
        client = self.collection_client()
        client.results[10]["results"] = {"00": 1, "01": 3}
        with self.assertRaisesRegex(platform.PlatformError, "raw shots or result metadata disagree"):
            self.collect(client)
        self.assertFalse((self.case_dir / "raw").exists())
        self.assertFalse((self.case_dir / "results.json").exists())

    def test_empty_approval_does_not_reach_service(self) -> None:
        with patch.object(platform, "Client", side_effect=AssertionError("empty approval reached the service")):
            with self.assertRaisesRegex(SystemExit, "nonempty approval"):
                platform.submit(self.case_dir, 7, "  ")

    def test_snapshot_rejects_every_form_of_account_identifier(self) -> None:
        evidence = ROOT / "docs/evidence/quantum_inspire"
        for name, key, value in (
            ("catalogue.json", "team", "61cec6179092"),
            ("catalogue.json", "member", 4321),
            ("usage.json", "member", None),
        ):
            with self.subTest(file=name, key=key), tempfile.TemporaryDirectory() as scratch:
                directory = Path(scratch)
                for source in ("catalogue.json", "usage.json"):
                    (directory / source).write_bytes((evidence / source).read_bytes())
                snapshot = json.loads((directory / name).read_text(encoding="utf-8"))
                if name == "usage.json":
                    snapshot["transactions"].append({key: value})
                else:
                    snapshot["account"]["members"][0][key] = value
                (directory / name).write_text(json.dumps(snapshot))
                with self.assertRaisesRegex(SystemExit, f"snapshot carries {key}"):
                    platform.check(directory)

    def test_snapshot_rejects_inconsistent_completed_shots(self) -> None:
        retained = Path(__file__).resolve().parents[1] / "docs/evidence/quantum_inspire"
        for name in ("catalogue.json", "usage.json"):
            (self.case_dir / name).write_bytes((retained / name).read_bytes())
        with contextlib.redirect_stdout(self.output):
            platform.check(self.case_dir)
        path = self.case_dir / "usage.json"
        usage = json.loads(path.read_text())
        usage["totals"]["shots_done"] += 1
        path.write_text(json.dumps(usage))
        with self.assertRaisesRegex(SystemExit, "completed shots differ"):
            platform.check(self.case_dir)

    def test_mcp_legacy_submit_refuses_without_service_access(self) -> None:
        module = mcp_with_stubs()
        with patch.object(module, "client", side_effect=AssertionError("legacy tool reached the service")):
            with self.assertRaisesRegex(FakeToolError, "qi_submit_case"):
                module.qi_submit("version 3.0", 7, 4, "fixture approval")

    def test_mcp_shared_width_parser_reports_malformed_source_without_execution(self) -> None:
        module = mcp_with_stubs()
        emulator = ModuleType("qxelarator")

        def unexpected_execution(*args: Any, **kwargs: Any) -> None:
            raise AssertionError("malformed source reached the emulator")

        emulator.execute_string = unexpected_execution  # type: ignore[attr-defined]
        self.assertEqual(module.declared_qubits("version 3.0\nqubit[2] q\nqubit r\n"), 3)
        for source in ("version 3.0\n", "version 3.0\nqubit[N] q\n", "version 3.0\nqubit[2] q /*"):
            with self.subTest(source=source), patch.dict(sys.modules, {"qxelarator": emulator}):
                with self.assertRaises(ValueError):
                    module.declared_qubits(source)
                with self.assertRaisesRegex(FakeToolError, "cQASM"):
                    module.qi_run_local(source)

    def test_mcp_case_tool_uses_guard_and_does_not_print_to_stdio(self) -> None:
        module = mcp_with_stubs()
        client = FakeClient(self.case_dir)
        with patch.object(platform, "Client", return_value=client), contextlib.redirect_stdout(self.output):
            record = module.qi_submit_case(str(self.case_dir), 7, "fixture approval")
            self.assertEqual(record["schema"], "qi-submission-v2")
            before = list(client.calls)
            with self.assertRaisesRegex(FakeToolError, "exists"):
                module.qi_submit_case(str(self.case_dir), 7, "fixture approval")
            self.assertEqual(client.calls, before)
        self.assertEqual(self.output.getvalue(), "")
        self.assertEqual(len(module.server.tools), 11)

    def test_mcp_compile_rejects_unknown_backend_before_remote_creation(self) -> None:
        module = mcp_with_stubs()
        client = FakeClient(self.case_dir)
        with patch.object(module, "client", return_value=client):
            with self.assertRaises(AssertionError):
                module.qi_compile("version 3.0", 999)
        self.assertEqual(client.calls, [("GET", "/backend_types/999")])

    def test_mcp_readonly_results_keep_their_interface(self) -> None:
        module = mcp_with_stubs()
        client = self.collection_client()
        with patch.object(module, "client", return_value=client):
            results = module.qi_results(10)
        self.assertEqual(results[0]["results"], {"00": 2, "01": 2})
        self.assertNotIn("raw_data", results[0])
        self.assertTrue(all(method == "GET" for method, _ in client.calls))


if __name__ == "__main__":
    unittest.main()
