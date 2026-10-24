"""Mock-only checks of one-batch submission recovery and immutable shot retention.

Every service constructor is replaced before use. These fixtures create no
remote resources, read no credentials and simulate no quantum circuit.
"""

from __future__ import annotations

import contextlib
import copy
import datetime
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
from unittest.mock import Mock, patch

import qi_platform as platform

# submit() takes the account submit lock; the fixtures lock a private file.
platform.SUBMIT_LOCK = Path(tempfile.mkdtemp(prefix="qi-submit-lock-")) / "submit.lock"


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
        # The account's other jobs and batches, read by the hardware pause check.
        self.account_types: list[dict[str, Any]] = [
            {"id": 1, "is_hardware": False},
            {"id": 6, "is_hardware": True},
            {"id": 7, "is_hardware": True},
        ]
        self.account_batches: list[dict[str, Any]] = []
        self.account_jobs: list[dict[str, Any]] = []

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
        if path == "/backend_types/":
            return copy.deepcopy(self.account_types)
        if path == "/batch_jobs" and not params:
            return copy.deepcopy(self.account_batches)
        if path == "/jobs":
            return copy.deepcopy(self.account_jobs)
        if path == "/batch_jobs" and params == {"id": self.batch["id"]}:
            return [copy.deepcopy(self.batch)]
        raise AssertionError(f"unexpected mock paginated GET {path} {params}")

    def post(self, path: str, body: dict[str, Any], *, execution_deadline: float | None = None) -> dict[str, Any]:
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
        if path in {"/backend_types/", "/batch_jobs", "/jobs"}:
            return []
        raise PreflightReached(path)

    def post(self, path: str, body: dict[str, Any], *, execution_deadline: float | None = None) -> dict[str, Any]:
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

    def test_preflight_refusal_blocks_direct_submission_before_service_access(self) -> None:
        (self.case_dir / "preflight-refusal.json").write_text("{}")
        with patch.object(platform, "Client", side_effect=AssertionError("refused case reached the service")):
            with self.assertRaisesRegex(SystemExit, "preflight-refusal"):
                platform.submit(self.case_dir, 7, "approved")
        self.assertFalse((self.case_dir / "submission-state.json").exists())
        self.assertFalse((self.case_dir / "submission.json").exists())

    def test_submission_deadline_covers_lock_wait_provider_preflight_and_state_sync(self) -> None:
        for times, state_expected in (((11.0,), False), ((1.0, 11.0), False), ((1.0, 2.0, 11.0), True)):
            with self.subTest(times=times):
                client = FakeClient(self.case_dir)
                with (
                    patch.object(platform, "Client", return_value=client),
                    patch.object(platform.time, "monotonic", side_effect=times),
                ):
                    with self.assertRaisesRegex(TimeoutError, "deadline"):
                        platform.submit(self.case_dir, 7, "fixture approval", execution_deadline=10.0)
                self.assertTrue(all(method == "GET" for method, _ in client.calls))
                self.assertEqual((self.case_dir / "submission-state.json").exists(), state_expected)
                (self.case_dir / "submission-state.json").unlink(missing_ok=True)

    def test_expiry_after_checkpoint_retains_proof_of_zero_resource_dispatch(self) -> None:
        client = FakeClient(self.case_dir)
        with (
            patch.object(platform, "Client", return_value=client),
            patch.object(platform.time, "monotonic", side_effect=(1.0, 2.0, 11.0)),
        ):
            with self.assertRaisesRegex(TimeoutError, "deadline"):
                platform.submit(self.case_dir, 7, "fixture approval", execution_deadline=10.0)
        state = json.loads((self.case_dir / "submission-state.json").read_text())
        self.assertEqual(state["phase"], "pre-dispatch-refused")
        self.assertEqual(state["resource_requests_dispatched"], 0)
        self.assertTrue(all(method == "GET" for method, _ in client.calls))
        self.assert_retry_blocked()
        with self.assertRaisesRegex(platform.PlatformError, "zero resource requests.*separately approved"):
            self.reconcile(client)

    def test_collection_deadline_blocks_terminal_result_and_ledger_dispatch(self) -> None:
        for expired_path in ("/jobs/10", "/results/job/10", "/transactions/"):
            with self.subTest(expired_path=expired_path):
                client = self.collection_client()
                self.bind_collection_receipt()
                original_get = client.get
                original_pages = client.pages
                clock = [1.0]
                dispatched: list[str] = []

                def get(
                    path: str,
                    *,
                    expired_path: str = expired_path,
                    clock: list[float] = clock,
                    dispatched: list[str] = dispatched,
                    original_get: Any = original_get,
                    **params: Any,
                ) -> Any:
                    if path == expired_path:
                        clock[0] = 11.0
                    platform._check_execution_deadline(params.pop("execution_deadline", None))
                    dispatched.append(path)
                    return original_get(path, **params)

                def pages(
                    path: str,
                    *,
                    expired_path: str = expired_path,
                    clock: list[float] = clock,
                    dispatched: list[str] = dispatched,
                    original_pages: Any = original_pages,
                    **params: Any,
                ) -> Any:
                    if path == expired_path:
                        clock[0] = 11.0
                    platform._check_execution_deadline(params.pop("execution_deadline", None))
                    dispatched.append(path)
                    return original_pages(path, **params)

                with (
                    patch.object(platform, "Client", return_value=client),
                    patch.object(platform.time, "monotonic", side_effect=lambda clock=clock: clock[0]),
                    patch.object(client, "get", side_effect=get),
                    patch.object(client, "pages", side_effect=pages),
                ):
                    with self.assertRaisesRegex(TimeoutError, "deadline"):
                        platform.collect(self.case_dir, poll=0, timeout=100, execution_deadline=10.0)
                self.assertNotIn(expired_path, dispatched)
                self.assertFalse((self.case_dir / "results.json").exists())

    def test_collection_transport_checks_each_page_after_refresh(self) -> None:
        client = platform.Client.__new__(platform.Client)
        client.expires = 10000
        client.session = Mock()
        clock = [1.0]
        response = client.session.request.return_value
        response.status_code = 200
        response.content = b"fixture"

        def page() -> dict[str, Any]:
            clock[0] = 11.0
            return {"items": [], "pages": 2}

        response.json.side_effect = page
        with (
            patch.object(platform.time, "time", return_value=100.0),
            patch.object(platform.time, "monotonic", side_effect=lambda: clock[0]),
        ):
            with self.assertRaisesRegex(TimeoutError, "deadline"):
                client.pages("/transactions/", execution_deadline=10.0)
        self.assertEqual(client.session.request.call_count, 1)

    def test_initial_token_refresh_expiry_retains_local_refusal_checkpoint(self) -> None:
        client = FakeClient(self.case_dir)
        transport = platform.Client.__new__(platform.Client)
        transport.expires = 0
        transport.session = Mock()
        clock = [1.0]

        def refresh() -> None:
            clock[0] = 11.0

        with (
            patch.object(platform, "Client", return_value=client),
            patch.object(platform.time, "time", return_value=100.0),
            patch.object(platform.time, "monotonic", side_effect=lambda: clock[0]),
            patch.object(transport, "refresh", side_effect=refresh),
            patch.object(client, "post", side_effect=transport.post),
        ):
            with self.assertRaisesRegex(TimeoutError, "deadline"):
                platform.submit(self.case_dir, 7, "fixture approval", execution_deadline=10.0)
        transport.session.request.assert_not_called()
        digest = hashlib.sha256((self.case_dir / "cases.json").read_bytes()).hexdigest()
        self.assertTrue(platform.pre_dispatch_refused(self.case_dir, digest))
        state_path = self.case_dir / "submission-state.json"
        state = json.loads(state_path.read_text())
        for change in ({"phase": "creating"}, {"resource_requests_dispatched": True}, {"project": 1}):
            state_path.write_text(json.dumps({**state, **change}))
            self.assertFalse(platform.pre_dispatch_refused(self.case_dir, digest))

    def test_submission_deadline_requires_a_finite_value(self) -> None:
        for deadline in (float("nan"), float("inf"), -float("inf")):
            with (
                self.subTest(deadline=deadline),
                patch.object(platform, "Client", side_effect=AssertionError("invalid deadline reached service")),
            ):
                with self.assertRaisesRegex(ValueError, "finite"):
                    platform.submit(self.case_dir, 7, "fixture approval", execution_deadline=deadline)

    def test_unauthorized_project_expiry_retains_proven_rejection_and_attempt(self) -> None:
        expired = {"detail": platform.EXPIRED_SIGNATURE}
        for status, body, receipt in (
            (401, {}, {"method": "POST", "path": "/projects", "status_code": 401}),
            (403, expired, {"method": "POST", "path": "/projects", "status_code": 403, **expired}),
        ):
            with self.subTest(status=status):
                client = FakeClient(self.case_dir)
                transport = platform.Client.__new__(platform.Client)
                transport.expires = 10000
                transport.session = Mock()
                transport.session.request.return_value.status_code = status
                transport.session.request.return_value.json.return_value = body
                clock = [1.0]

                def refresh(clock: list[float] = clock) -> None:
                    clock[0] = 11.0

                with (
                    patch.object(platform, "Client", return_value=client),
                    patch.object(platform.time, "time", return_value=100.0),
                    patch.object(platform.time, "monotonic", side_effect=lambda clock=clock: clock[0]),
                    patch.object(transport, "refresh", side_effect=refresh),
                    patch.object(client, "post", side_effect=transport.post),
                ):
                    with self.assertRaisesRegex(TimeoutError, f"HTTP {status} rejected"):
                        platform.submit(self.case_dir, 7, "fixture approval", execution_deadline=10.0)
                self.assertEqual(transport.session.request.call_count, 1)
                state_path = self.case_dir / "submission-state.json"
                state = json.loads(state_path.read_text())
                self.assertEqual(state["phase"], "resource-request-rejected")
                self.assertEqual(state["resource_requests_dispatched"], 1)
                self.assertEqual(state["resource_requests_applied"], 0)
                self.assertEqual(state["rejected_request"], receipt)
                self.assertFalse(platform.pre_dispatch_refused(self.case_dir, state["cases_sha256"]))
                self.assertTrue(platform.creation_refused(self.case_dir, state["cases_sha256"]))
                self.assert_retry_blocked()
                with self.assertRaisesRegex(platform.PlatformError, f"HTTP {status} and was not.*separately approved"):
                    self.reconcile(client)
                for forged in ({**receipt, "status_code": 500}, {**receipt, "detail": "other"}):
                    state_path.write_text(json.dumps({**state, "rejected_request": forged}))
                    self.assertFalse(platform.creation_refused(self.case_dir, state["cases_sha256"]))
                state_path.unlink()

    def test_rejection_after_project_creation_keeps_partial_resource_boundary(self) -> None:
        for rejected_path in ("/batch_jobs", "/algorithms", "/jobs"):
            with self.subTest(rejected_path=rejected_path):
                client = FakeClient(self.case_dir)
                original_post = client.post

                def post(
                    path: str,
                    body: dict[str, Any],
                    *,
                    execution_deadline: float | None = None,
                    rejected_path: str = rejected_path,
                    original_post: Any = original_post,
                ) -> Any:
                    if path == rejected_path:
                        raise platform.RequestRejectedBeforeRetry("POST", path)
                    return original_post(path, body, execution_deadline=execution_deadline)

                with patch.object(client, "post", side_effect=post):
                    with self.assertRaises(platform.RequestRejectedBeforeRetry):
                        self.submit(client)
                state_path = self.case_dir / "submission-state.json"
                state = json.loads(state_path.read_text())
                self.assertEqual(state["phase"], "creating")
                self.assertIn("project", state)
                if rejected_path != "/batch_jobs":
                    self.assertIn("batch_job", state)
                self.assertFalse(platform.creation_refused(self.case_dir, state["cases_sha256"]))
                self.assert_retry_blocked()
                state_path.unlink()

    def test_refresh_expiry_blocks_initial_dispatch_and_unauthorized_retry(self) -> None:
        for retry in (False, True):
            with self.subTest(retry=retry):
                client = platform.Client.__new__(platform.Client)
                client.expires = 10000 if retry else 0
                session = Mock()
                session.request.return_value.status_code = 401
                client.session = session
                clock = [1.0]

                def refresh(clock: list[float] = clock) -> None:
                    clock[0] = 11.0

                def current_time(clock: list[float] = clock) -> float:
                    return clock[0]

                with (
                    patch.object(platform.time, "time", return_value=100.0),
                    patch.object(platform.time, "monotonic", side_effect=current_time),
                    patch.object(client, "refresh", side_effect=refresh),
                ):
                    with self.assertRaisesRegex(TimeoutError, "deadline"):
                        client.post("/projects", {}, execution_deadline=10.0)
                self.assertEqual(session.request.call_count, int(retry))

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

    def paused_client(self, jobs: list[tuple[int, str, int | None]], *, now: datetime.datetime) -> FakeClient:
        """A client whose account holds one job per (backend type, status, seconds since it finished) row."""
        client = FakeClient(self.case_dir)
        for index, (type_id, status, age) in enumerate(jobs):
            client.account_batches.append(
                {
                    "id": 900 + index,
                    "backend_type_id": type_id,
                    "status": "finished" if status in platform.TERMINAL else "queued",
                    "created_on": (now - datetime.timedelta(seconds=3600)).isoformat(),
                }
            )
            finished = None if age is None else (now - datetime.timedelta(seconds=age)).isoformat()
            client.account_jobs.append(
                {"id": 800 + index, "batch_job_id": 900 + index, "status": status, "finished_at": finished}
            )
        return client

    def test_hardware_batch_waits_for_the_account_pause(self) -> None:
        now = datetime.datetime(2026, 10, 17, 12, 0, 0, tzinfo=datetime.UTC)
        pause = platform.HARDWARE_PAUSE_SECONDS
        self.assertEqual(pause, platform.HARDWARE_PAUSE_LADDER[0])
        self.assertEqual(platform.HARDWARE_PAUSE_LADDER, (30, 60, 90, 120))
        with patch.object(platform, "utc_now", return_value=now):
            # Jobs of every hardware backend type count, whichever session submitted them.
            for type_id in (6, 7):
                for age, wait in ((pause - 1, "wait 1 more seconds"), (5, f"wait {pause - 5} more seconds")):
                    with self.subTest(backend_type=type_id, age=age):
                        client = self.paused_client([(type_id, "completed", age)], now=now)
                        with self.assertRaisesRegex(SystemExit, wait):
                            self.submit(client)
                        self.assertTrue(all(method == "GET" for method, _ in client.calls))
                        self.assertFalse((self.case_dir / "submission-state.json").exists())
            for age in (pause, pause + 1, 3600):
                with self.subTest(accepted_after=age):
                    client = self.paused_client([(6, "completed", age), (7, "failed", age + 50)], now=now)
                    self.submit(client)
                    self.assertEqual(sum(method == "PATCH" for method, _ in client.calls), 1)
                    for name in ("submission.json", "submission-state.json"):
                        (self.case_dir / name).unlink()
            with self.subTest(latest_of_several=True):
                client = self.paused_client(
                    [(7, "completed", 20 * pause), (6, "completed", 10), (7, "failed", 10 * pause)], now=now
                )
                with self.assertRaisesRegex(SystemExit, f"wait {pause - 10} more seconds"):
                    self.submit(client)

    def test_hardware_pause_takes_only_a_ladder_step(self) -> None:
        for value, want in (("", 30), ("60", 60), ("90", 90), ("120", 120)):
            with self.subTest(value=value), patch.dict(os.environ, {"QI_HARDWARE_PAUSE_SECONDS": value}):
                self.assertEqual(platform._hardware_pause(), want)
        for value in ("45", "0", "-30", "30s", "600"):
            with self.subTest(value=value), patch.dict(os.environ, {"QI_HARDWARE_PAUSE_SECONDS": value}):
                with self.assertRaisesRegex(SystemExit, "is not a step of"):
                    platform._hardware_pause()

    def test_hardware_batch_refuses_while_an_account_hardware_job_is_unfinished(self) -> None:
        now = datetime.datetime(2026, 10, 17, 12, 0, 0, tzinfo=datetime.UTC)
        with patch.object(platform, "utc_now", return_value=now):
            for status in ("planned", "queued", "running"):
                with self.subTest(status=status):
                    client = self.paused_client([(6, "completed", 3600), (6, status, None)], now=now)
                    with self.assertRaisesRegex(SystemExit, f"hardware job 801 is {status}"):
                        self.submit(client)
                    self.assertTrue(all(method == "GET" for method, _ in client.calls))
                    self.assertFalse((self.case_dir / "submission-state.json").exists())

    def test_un_enqueued_hardware_batch_blocks_only_while_recent(self) -> None:
        now = datetime.datetime(2026, 10, 17, 12, 0, 0, tzinfo=datetime.UTC)
        limit = platform.ABANDONED_PLANNING_SECONDS
        with patch.object(platform, "utc_now", return_value=now):
            for age, refused in ((30, True), (limit - 1, True), (limit, False), (86400, False)):
                with self.subTest(age=age):
                    client = self.paused_client([(7, "completed", 3600), (7, "planned", None)], now=now)
                    batch = client.account_batches[1]
                    batch["status"] = "planned"
                    batch["created_on"] = (now - datetime.timedelta(seconds=age)).isoformat()
                    if refused:
                        with self.assertRaisesRegex(SystemExit, "hardware batch 901 is being planned"):
                            self.submit(client)
                        self.assertTrue(all(method == "GET" for method, _ in client.calls))
                    else:
                        # An interrupted submit's planned jobs never run, so they hold no device time.
                        self.submit(client)
                        self.assertEqual(sum(method == "PATCH" for method, _ in client.calls), 1)
                        for name in ("submission.json", "submission-state.json"):
                            (self.case_dir / name).unlink()

    def test_terminal_hardware_job_without_finish_time_refuses(self) -> None:
        now = datetime.datetime(2026, 10, 17, 12, 0, 0, tzinfo=datetime.UTC)
        with patch.object(platform, "utc_now", return_value=now):
            for status in sorted(platform.TERMINAL):
                with self.subTest(status=status):
                    client = self.paused_client([(7, status, None)], now=now)
                    with self.assertRaisesRegex(SystemExit, "without a finish time"):
                        self.submit(client)
                    self.assertFalse((self.case_dir / "submission-state.json").exists())

    def test_submit_waits_for_the_account_submit_lock(self) -> None:
        import threading

        client = self.paused_client([], now=datetime.datetime(2026, 10, 17, 12, 0, 0, tzinfo=datetime.UTC))
        done = threading.Event()

        def run() -> None:
            self.submit(client)
            done.set()

        with platform.token_lock(platform.SUBMIT_LOCK):
            worker = threading.Thread(target=run)
            worker.start()
            self.assertFalse(done.wait(0.5))
            self.assertEqual(client.calls, [])
        worker.join(30)
        self.assertTrue(done.is_set())
        self.assertEqual(sum(method == "PATCH" for method, _ in client.calls), 1)

    def test_emulator_jobs_and_emulator_batches_ignore_the_pause(self) -> None:
        now = datetime.datetime(2026, 10, 17, 12, 0, 0, tzinfo=datetime.UTC)
        with patch.object(platform, "utc_now", return_value=now):
            # An emulator job that finished a second ago or is still running does not delay a hardware batch.
            client = self.paused_client([(1, "completed", 1), (1, "running", None)], now=now)
            self.submit(client)
            self.assertEqual(sum(method == "PATCH" for method, _ in client.calls), 1)
            for name in ("submission.json", "submission-state.json"):
                (self.case_dir / name).unlink()
            # An emulator batch skips the pause and never reads the account's jobs.
            client = self.paused_client([(6, "completed", 1), (6, "running", None)], now=now)
            client.backend["is_hardware"] = False
            self.submit(client)
            self.assertEqual(sum(method == "PATCH" for method, _ in client.calls), 1)
            self.assertNotIn(("GET", "/jobs"), client.calls)

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

    def test_ledger_declares_the_jobs_no_run_directory_retains(self) -> None:
        class LedgerClient:
            jobs = [
                {
                    "id": job,
                    "batch_job_id": 5,
                    "status": "completed",
                    "created_on": "",
                    "number_of_shots": 2,
                    "queued_at": "",
                    "finished_at": "",
                }
                for job in (40, 10, 30, 20)
            ]

            def pages(self, path: str, **params: Any) -> list[dict[str, Any]]:
                tables: dict[str, list[dict[str, Any]]] = {
                    "/jobs": self.jobs,
                    "/batch_jobs": [{"id": 5, "backend_type_id": 1}],
                    "/transactions/": [],
                }
                return tables[path]

            def get(self, path: str, **params: Any) -> Any:
                return {"items": [{"shots_done": 2, "execution_time_in_seconds": 0.5, "change": 0}]}

        runs = self.case_dir / "runs"
        for name, jobs in (("a", [10, 20]), ("b", [30])):
            (runs / name).mkdir(parents=True)
            (runs / name / "submission.json").write_text(json.dumps({"jobs": [{"job": job} for job in jobs]}))
        (runs / "interrupted").mkdir()
        (runs / "interrupted" / "submission-state.json").write_text("{}")
        self.assertEqual(platform.run_directories(runs), [runs / "a", runs / "b", runs / "interrupted"])
        self.assertEqual(platform.retained_job_ids(runs), {10, 20, 30})
        record = platform.ledger(LedgerClient(), runs)  # type: ignore[arg-type]
        self.assertEqual((record["schema"], record["unretained"]), ("qi-usage-v2", [40]))
        self.assertEqual([row["job"] for row in record["jobs"]], [10, 20, 30, 40])
        self.assertEqual(platform.retained_job_ids(runs / "absent"), set())

    def test_marked_campaign_enumerates_bound_batches_beside_legacy_runs(self) -> None:
        runs = self.case_dir / "runs"
        legacy = runs / "legacy"
        legacy.mkdir(parents=True)
        campaign = runs / "campaign"
        batches = {}
        for index, name in enumerate(("batch-b", "batch-a")):
            directory = campaign / name
            directory.mkdir(parents=True)
            source = b'{"circuits": []}'
            (directory / "cases.json").write_bytes(source)
            (directory / "submission.json").write_text(json.dumps({"jobs": [{"job": index + 1}]}))
            batches[name] = hashlib.sha256(source).hexdigest()
        marker = {"schema": "qi-campaign-v1", "plan_sha256": "a" * 64, "batches": batches}
        (campaign / "campaign.json").write_text(json.dumps(marker))
        for name, digest in batches.items():
            (campaign / name / "execution-intent.json").write_text(
                json.dumps({"schema": "qi-campaign-intent-v1", "plan_sha256": "a" * 64, "cases_sha256": digest})
            )
        expected = [campaign / "batch-a", campaign / "batch-b"]
        self.assertEqual(platform.run_directories(campaign), expected)
        self.assertEqual(platform.run_directories(runs), [*expected, legacy])
        self.assertEqual(platform.retained_job_ids(runs), {1, 2})

    def test_marked_campaign_refuses_omitted_extra_and_changed_batches(self) -> None:
        campaign = self.case_dir / "campaign"
        batch = campaign / "batch"
        batch.mkdir(parents=True)
        source = b"{}"
        (batch / "cases.json").write_bytes(source)
        marker: dict[str, Any] = {
            "schema": "qi-campaign-v1",
            "plan_sha256": "a" * 64,
            "batches": {"batch": hashlib.sha256(source).hexdigest()},
        }
        invalid = [
            {**marker, "schema": "unknown"},
            {**marker, "plan_sha256": "x" * 64},
            {**marker, "batches": {}},
            {**marker, "batches": {"omitted": "a" * 64}},
            {**marker, "batches": {**marker["batches"], "extra": "a" * 64}},
            {**marker, "batches": {"../batch": "a" * 64}},
            {**marker, "batches": {"batch": "a" * 64}},
        ]
        for record in invalid:
            with self.subTest(record=record):
                (campaign / "campaign.json").write_text(json.dumps(record))
                with self.assertRaises(platform.PlatformError):
                    platform.run_directories(self.case_dir)
        (campaign / "campaign.json").write_text(json.dumps(marker))
        (batch / "cases.json").write_text("changed")
        with self.assertRaisesRegex(platform.PlatformError, "bound digest"):
            platform.run_directories(campaign)

    def test_campaign_journal_distinguishes_planned_intended_and_refused_batches(self) -> None:
        campaign = self.case_dir / "campaign"
        batch = campaign / "batch"
        batch.mkdir(parents=True)
        source = b"{}"
        (batch / "cases.json").write_bytes(source)
        binding = {"plan_sha256": "a" * 64, "cases_sha256": hashlib.sha256(source).hexdigest()}
        (campaign / "campaign.json").write_text(
            json.dumps(
                {
                    "schema": "qi-campaign-v1",
                    "plan_sha256": binding["plan_sha256"],
                    "batches": {"batch": binding["cases_sha256"]},
                }
            )
        )
        self.assertEqual(platform.run_directories(campaign), [])
        intent_path = batch / "execution-intent.json"
        intent = {"schema": "qi-campaign-intent-v1", **binding}
        refusal_path = batch / "preflight-refusal.json"
        refusal = {"schema": "qi-campaign-refusal-v1", "phase": "preflight-refused", **binding}
        for artifact in ("submission.json", "submission-state.json", "results.json", "raw"):
            path = batch / artifact
            path.write_text("{}")
            with self.subTest(artifact=artifact), self.assertRaisesRegex(platform.PlatformError, "intent"):
                platform.run_directories(campaign)
            path.unlink()
        refusal_path.write_text(json.dumps(refusal))
        with self.assertRaisesRegex(platform.PlatformError, "intent"):
            platform.run_directories(campaign)
        refusal_path.unlink()
        for invalid in ({**intent, "cases_sha256": "0" * 64}, {**intent, "extra": True}):
            intent_path.write_text(json.dumps(invalid))
            with self.assertRaisesRegex(platform.PlatformError, "intent"):
                platform.run_directories(campaign)
        intent_path.write_text(json.dumps(intent))
        self.assertEqual(platform.run_directories(campaign), [batch])
        for invalid in (
            {**refusal, "phase": "completed"},
            {**refusal, "plan_sha256": "0" * 64},
            {**refusal, "extra": True},
        ):
            refusal_path.write_text(json.dumps(invalid))
            with self.assertRaisesRegex(platform.PlatformError, "refusal"):
                platform.run_directories(campaign)
        refusal_path.write_text(json.dumps(refusal))
        self.assertEqual(platform.run_directories(campaign), [])
        for artifact in ("submission.json", "submission-state.json", "results.json", "raw"):
            path = batch / artifact
            path.write_text("{}")
            with self.subTest(artifact=artifact), self.assertRaisesRegex(platform.PlatformError, "conflicts"):
                platform.run_directories(campaign)
            path.unlink()

    def test_snapshot_check_validates_the_unretained_list(self) -> None:
        retained = Path(__file__).resolve().parents[1] / "docs/evidence/quantum_inspire"
        for name in ("catalogue.json", "usage.json"):
            (self.case_dir / name).write_bytes((retained / name).read_bytes())
        path = self.case_dir / "usage.json"
        usage = json.loads(path.read_text())
        ids = [row["job"] for row in usage["jobs"]]
        for schema, unretained, refusal in (
            ("qi-usage-v2", [ids[0], ids[1]], None),
            ("qi-usage-v2", [], None),
            ("qi-usage-v2", [ids[1], ids[0]], "sorted list of distinct"),
            ("qi-usage-v2", [ids[0], ids[0]], "sorted list of distinct"),
            ("qi-usage-v2", [max(ids) + 1], "sorted list of distinct"),
            ("qi-usage-v1", [], "carries no unretained list"),
        ):
            with self.subTest(schema=schema, unretained=unretained):
                path.write_text(json.dumps({**usage, "schema": schema, "unretained": unretained}))
                if refusal is None:
                    with contextlib.redirect_stdout(self.output):
                        platform.check(self.case_dir)
                else:
                    with self.assertRaisesRegex(SystemExit, refusal):
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
        self.assertEqual(len(module.server.tools), 13)

    def test_mcp_performance_outage_is_a_tool_error(self) -> None:
        module = mcp_with_stubs()
        failing = Mock(side_effect=module.monitoring_query.__globals__["MonitoringError"]("every query failed"))
        with patch.object(module, "monitoring_query", failing), self.assertRaisesRegex(FakeToolError, "every query"):
            module.qi_performance_query("tuna-17", 3)
        failing.assert_called_once_with("tuna-17", 3, 6.0)

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

    def test_mcp_backend_uses_account_queue_and_reports_distinct_live_statuses(self) -> None:
        module = mcp_with_stubs()
        client = Mock()
        client.get.side_effect = [
            {"id": 7, "identifier": "tuna_17", "enabled": True, "status": "offline"},
            {"number_of_jobs_in_queue": 0},
            {"id": 7, "identifier": "tuna_17", "enabled": True, "status": "idle"},
            {"number_of_jobs_in_queue": 12},
        ]
        client.pages.return_value = [
            {"id": 7, "backend_type_id": 7, "status": "calibrating", "last_heartbeat": "2026-10-22T16:43:34Z"},
            {"id": 6, "backend_type_id": 6, "status": "offline"},
        ]
        with patch.object(module, "client", return_value=client):
            account = module.qi_backend(7)
            self.assertIn("queue_user_only", account)
            global_queue = module.qi_backend(7, user_only=False)
        self.assertEqual(account["status"], "offline")
        self.assertTrue(account["enabled"])
        self.assertEqual(account["queue"]["number_of_jobs_in_queue"], 0)
        self.assertIs(account["queue_user_only"], True)
        self.assertEqual(account["backend_instances"], [client.pages.return_value[0]])
        self.assertEqual(global_queue["status"], "idle")
        self.assertEqual(global_queue["queue"]["number_of_jobs_in_queue"], 12)
        self.assertIs(global_queue["queue_user_only"], False)
        for record in (account, global_queue):
            started = datetime.datetime.fromisoformat(record["request_started_utc"])
            finished = datetime.datetime.fromisoformat(record["retrieved_utc"])
            self.assertEqual(started.utcoffset(), datetime.timedelta(0))
            self.assertEqual(finished.utcoffset(), datetime.timedelta(0))
            self.assertLessEqual(started, finished)
        self.assertEqual(
            client.get.call_args_list,
            [
                unittest.mock.call("/backend_types/7"),
                unittest.mock.call("/backend_types/7/queue", user_only=True),
                unittest.mock.call("/backend_types/7"),
                unittest.mock.call("/backend_types/7/queue", user_only=False),
            ],
        )

    def test_mcp_backend_catalogue_exposes_queue_scope_and_freshness(self) -> None:
        module = mcp_with_stubs()
        client = Mock()
        backend: dict[str, Any] = {key: None for key in module.LIMIT_FIELDS}
        backend.update(id=7, identifier="tuna_17", status="offline", enabled=True)
        client.pages.return_value = [backend]
        client.get.side_effect = [{"number_of_jobs_in_queue": 0}, {"number_of_jobs_in_queue": 12}]
        with patch.object(module, "client", return_value=client):
            account = module.qi_backends()[0]
            self.assertIn("queue_user_only", account)
            global_queue = module.qi_backends(user_only=False)[0]
        self.assertIs(account["queue_user_only"], True)
        self.assertEqual(account["queue"]["number_of_jobs_in_queue"], 0)
        self.assertIs(global_queue["queue_user_only"], False)
        self.assertEqual(global_queue["queue"]["number_of_jobs_in_queue"], 12)
        self.assertEqual(account["status"], "offline")
        self.assertIn("request_started_utc", account)
        self.assertIn("retrieved_utc", account)
        self.assertEqual(
            client.get.call_args_list,
            [
                unittest.mock.call("/backend_types/7/queue", user_only=True),
                unittest.mock.call("/backend_types/7/queue", user_only=False),
            ],
        )

    def test_mcp_hardware_status_reads_again_without_rewriting_backend_state(self) -> None:
        module = mcp_with_stubs()
        client = Mock()
        client.pages.side_effect = [
            [{"id": 7, "backend_type_id": 7, "status": "offline", "last_heartbeat": "2026-10-22T16:43:34Z"}],
            [{"id": 7, "backend_type_id": 7, "status": "idle", "last_heartbeat": "2026-10-22T16:44:34Z"}],
        ]
        with patch.object(module, "client", return_value=client):
            first = module.qi_hardware_status()[0]
            second = module.qi_hardware_status()[0]
        self.assertEqual(first["status"], "offline")
        self.assertEqual(second["status"], "idle")
        self.assertEqual(second["last_heartbeat"], "2026-10-22T16:44:34Z")
        self.assertIn("request_started_utc", first)
        self.assertIn("retrieved_utc", second)
        self.assertEqual(
            client.pages.call_args_list, [unittest.mock.call("/backends"), unittest.mock.call("/backends")]
        )

    def test_mcp_observation_intervals_preserve_subsecond_completion(self) -> None:
        started = datetime.datetime(2026, 10, 22, 17, 3, 1, 123456, tzinfo=datetime.UTC)
        finished = datetime.datetime(2026, 10, 22, 17, 3, 1, 823456, tzinfo=datetime.UTC)
        parse = datetime.datetime.fromisoformat
        for name in ("qi_backend", "qi_backends", "qi_hardware_status"):
            with (
                self.subTest(tool=name),
                patch.object(platform.datetime, "datetime", wraps=datetime.datetime) as clock,
            ):
                clock.now.side_effect = [started, finished]
                module = mcp_with_stubs()
                client = Mock()
                backend: dict[str, Any] = {key: None for key in module.LIMIT_FIELDS}
                backend.update(id=7, backend_type_id=7, status="offline")
                client.pages.return_value = [backend]
                client.get.side_effect = lambda path, observed_backend=backend, **params: (
                    {"number_of_jobs_in_queue": 0} if path.endswith("/queue") else observed_backend
                )
                with patch.object(module, "client", return_value=client):
                    result = getattr(module, name)(7) if name == "qi_backend" else getattr(module, name)()
                record = result if name == "qi_backend" else result[0]
                self.assertEqual(parse(record["request_started_utc"]), started)
                self.assertEqual(parse(record["retrieved_utc"]), finished)


class TokenRefreshChecks(unittest.TestCase):
    """Client.refresh against a stand-in SDK whose authorization server rotates refresh tokens.

    The stand-in mirrors quantuminspire 4.1: ConfigManager reads the token file,
    AuthManager.refresh_tokens exchanges only near expiry and keeps the rotated
    tokens in memory, and the server revokes the login when a spent refresh
    token is presented again.
    """

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.file = Path(self.tmp.name) / "config.json"
        self.server: dict[str, Any] = {"live": "r0", "revoked": False, "exchanges": 0}
        self.clock = [1000.0]
        tokens = {"access_token": "a0", "refresh_token": "r0", "generated_at": 1000.0 - 3600, "expires_in": 3600}
        auths = {platform.HOST: {"tokens": tokens, "team_member_id": 1}}
        self.file.write_text(json.dumps({"default_host": platform.HOST, "auths": auths}), encoding="utf-8")

    def sdk(self) -> dict[str, ModuleType]:
        test = self

        class Tokens:
            def __init__(self, data: dict[str, Any]) -> None:
                self.access_token: str = data["access_token"]
                self.refresh_token: str = data["refresh_token"]
                self.generated_at: float = data["generated_at"]
                self.expires_in: int = data["expires_in"]

        class Auth:
            def __init__(self, data: dict[str, Any]) -> None:
                self.tokens = Tokens(data["tokens"])
                self.team_member_id = data["team_member_id"]

        class Settings:
            def __init__(self) -> None:
                data = json.loads(test.file.read_text(encoding="utf-8"))
                self.auths = {host: Auth(value) for host, value in data["auths"].items()}

            @classmethod
            def json_file(cls) -> Path:
                return test.file

            def model_dump_json(self, indent: int = 4) -> str:
                auths = {
                    h: {"tokens": vars(a.tokens), "team_member_id": a.team_member_id} for h, a in self.auths.items()
                }
                return json.dumps({"default_host": platform.HOST, "auths": auths}, indent=indent)

        class ConfigManager:
            def __init__(self) -> None:
                self.user_settings = Settings()

            def get(self, key: str) -> str:
                return platform.HOST

        class AuthManager:
            def __init__(self, user_settings: Settings) -> None:
                self.settings = user_settings

            def login_required(self, host: str) -> bool:
                return False

            def refresh_tokens(self, host: str) -> None:
                tokens = self.settings.auths[host].tokens
                if tokens.generated_at + tokens.expires_in > test.clock[0] + 5:
                    return
                if tokens.refresh_token != test.server["live"]:
                    test.server["revoked"] = True
                    raise RuntimeError("invalid_grant: Unknown or invalid refresh token")
                test.server["exchanges"] += 1
                n = test.server["exchanges"]
                test.server["live"] = f"r{n}"
                fresh = {
                    "access_token": f"a{n}",
                    "refresh_token": f"r{n}",
                    "generated_at": test.clock[0],
                    "expires_in": 3600,
                }
                self.settings.auths[host].tokens = Tokens(fresh)

        auth_module = ModuleType("quantuminspire.managers.auth_manager")
        auth_module.AuthManager = AuthManager  # type: ignore[attr-defined]
        config_module = ModuleType("quantuminspire.managers.config_manager")
        config_module.ConfigManager = ConfigManager  # type: ignore[attr-defined]
        requests = ModuleType("requests")
        requests.Session = lambda: type("Session", (), {"headers": {}})()  # type: ignore[attr-defined]
        return {
            "quantuminspire": ModuleType("quantuminspire"),
            "quantuminspire.managers": ModuleType("quantuminspire.managers"),
            "quantuminspire.managers.auth_manager": auth_module,
            "quantuminspire.managers.config_manager": config_module,
            "requests": requests,
        }

    def stored_refresh_token(self) -> str:
        return str(json.loads(self.file.read_text(encoding="utf-8"))["auths"][platform.HOST]["tokens"]["refresh_token"])

    def test_rotated_tokens_reach_disk_and_a_second_process_adopts_them(self) -> None:
        with (
            patch.dict(sys.modules, self.sdk()),
            patch.object(platform, "TOKEN_FILE", self.file),
            patch.object(platform, "TOKEN_LOCK", self.file.with_name("config.json.lock")),
            patch.object(platform.time, "time", side_effect=lambda: self.clock[0]),
        ):
            first = platform.Client()
            self.assertEqual((self.server["exchanges"], self.stored_refresh_token()), (1, "r1"))
            self.assertEqual(stat.S_IMODE(self.file.stat().st_mode), 0o600)
            second = platform.Client()
            self.assertEqual(self.server["exchanges"], 1)
            self.assertEqual(second.session.headers["Authorization"], "Bearer a1")
            self.clock[0] += 3600
            first.refresh()
            second.refresh()
            self.assertEqual((self.server["exchanges"], self.stored_refresh_token()), (2, "r2"))
            self.assertFalse(self.server["revoked"])
            self.assertEqual(second.session.headers["Authorization"], "Bearer a2")

    def refresh_records(self) -> list[dict[str, Any]]:
        log = self.file.with_name("refresh-log.jsonl")
        self.assertEqual(stat.S_IMODE(log.stat().st_mode), 0o600)
        text = log.read_text(encoding="utf-8")
        for token in ("a0", "r0", "a1", "r1", "a2", "r2"):
            self.assertNotIn(f'"{token}"', text)
        return [json.loads(line) for line in text.splitlines()]

    def test_each_exchange_is_logged_without_token_bytes(self) -> None:
        with (
            patch.dict(sys.modules, self.sdk()),
            patch.object(platform, "TOKEN_FILE", self.file),
            patch.object(platform, "TOKEN_LOCK", self.file.with_name("config.json.lock")),
            patch.object(platform.time, "time", side_effect=lambda: self.clock[0]),
        ):
            client = platform.Client()
            client.refresh()
            self.clock[0] += 3600
            client.refresh()
        records = self.refresh_records()
        self.assertEqual([record["outcome"] for record in records], ["exchanged", "exchanged"])
        self.assertEqual({record["pid"] for record in records}, {os.getpid()})

    def test_a_dead_refresh_token_names_the_forced_login(self) -> None:
        self.server["live"] = "r9"
        with (
            patch.dict(sys.modules, self.sdk()),
            patch.object(platform, "TOKEN_FILE", self.file),
            patch.object(platform, "TOKEN_LOCK", self.file.with_name("config.json.lock")),
            patch.object(platform.time, "time", side_effect=lambda: self.clock[0]),
        ):
            with self.assertRaises(platform.PlatformError) as caught:
                platform.Client()
        self.assertIn('qi" login --force', str(caught.exception))
        self.assertIn("plain `qi login` cannot recover it", str(caught.exception))
        self.assertEqual([record["outcome"] for record in self.refresh_records()], ["rejected"])
        self.assertEqual(self.stored_refresh_token(), "r0")

    def test_an_expired_signature_refreshes_once_and_another_403_refuses(self) -> None:
        for detail, calls in ((platform.EXPIRED_SIGNATURE, 2), ("Not authorized for this backend", 1)):
            with self.subTest(detail=detail):
                client = platform.Client.__new__(platform.Client)
                client.expires = float("inf")
                refused = Mock(status_code=403, text=json.dumps({"detail": detail}))
                refused.json.return_value = {"detail": detail}
                served = Mock(status_code=200, content=b"{}")
                served.json.return_value = {}
                client.session = Mock()
                client.session.request.side_effect = [refused, served]
                with patch.object(client, "refresh") as refresh:
                    if calls == 2:
                        self.assertEqual(client.get("/backend_types/7"), {})
                    else:
                        with self.assertRaisesRegex(platform.PlatformError, "403"):
                            client.get("/backend_types/7")
                self.assertEqual(client.session.request.call_count, calls)
                self.assertEqual(refresh.call_count, calls - 1)


if __name__ == "__main__":
    unittest.main()
