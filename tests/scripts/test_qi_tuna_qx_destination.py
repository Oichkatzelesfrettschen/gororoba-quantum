"""Verify the source-bound reduced QX destination conformance proposal."""

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/qi_tuna_qx_destination.py"


def test_manifest_binds_exact_sources_and_qx_predictions(tmp_path: Path) -> None:
    """Catch wrong backend, shot count, source identity or asymmetric terminal prediction."""
    output = tmp_path / "cases.json"
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--manifest-out", str(output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if process.returncode != 0:
        raise AssertionError(f"QX proposal generation failed: {process.stderr}")
    manifest = json.loads(output.read_bytes())
    if (manifest["backend"], manifest["backend_type_id"], manifest["nqubits"], manifest["shots"]) != (
        "QXsinglenodesimulator",
        1,
        3,
        2048,
    ):
        raise AssertionError("QX manifest backend, width or shot count differs")
    if [(row["file"], row["expected_output"]) for row in manifest["circuits"]] != [
        ("baseline.cq", "000"),
        ("rotated.cq", "000"),
        ("asymmetric.cq", "001"),
    ]:
        raise AssertionError("QX manifest circuit identities or expected outputs differ")
    if manifest["provider_execution_authorized"] is not False:
        raise AssertionError("a locally generated proposal cannot authorize a provider job")
    if not any(path.endswith("local-replay.json") for path in manifest["evidence"]):
        raise AssertionError("the manifest must bind the independently replayable local observation")


def test_manifest_refuses_inconsistent_local_output_observation(tmp_path: Path, monkeypatch: object) -> None:
    """Catch a bound local QX observation that contradicts the expected output."""
    import shutil

    import pytest
    import qi_tuna_qx_destination as proposal

    for name in (
        "baseline.cq",
        "rotated.cq",
        "asymmetric.cq",
        "local-parse-observation.json",
        "local-qx-output-observation.json",
        "local-replay.json",
    ):
        shutil.copyfile(proposal.PROPOSAL / name, tmp_path / name)
    path = tmp_path / "local-qx-output-observation.json"
    observation = json.loads(path.read_bytes())
    observation["sources"][2]["counts"] = {"000": 1}
    path.write_text(json.dumps(observation), encoding="utf-8")
    monkeypatch.setattr(proposal, "PROPOSAL", tmp_path)  # type: ignore[attr-defined]
    with pytest.raises(ValueError, match="local QX observation"):
        proposal.build_manifest()


def test_manifest_rejects_invalid_local_observation_provenance(tmp_path: Path, monkeypatch: object) -> None:
    """Require typed interpreter identities and ordered timezone-aware observation times."""
    import shutil

    import pytest
    import qi_tuna_qx_destination as proposal

    names = (
        "baseline.cq",
        "rotated.cq",
        "asymmetric.cq",
        "local-parse-observation.json",
        "local-qx-output-observation.json",
        "local-replay.json",
    )
    for name in names:
        shutil.copyfile(proposal.PROPOSAL / name, tmp_path / name)
    monkeypatch.setattr(proposal, "PROPOSAL", tmp_path)  # type: ignore[attr-defined]
    for filename, field, value in (
        ("local-parse-observation.json", "observed_utc", "2026-01-01T00:00:00"),
        ("local-parse-observation.json", "python_version", None),
        ("local-qx-output-observation.json", "started_utc", "2026-01-01T00:00:00"),
        ("local-qx-output-observation.json", "finished_utc", "1900-01-01T00:00:00+00:00"),
        ("local-qx-output-observation.json", "python_version", False),
    ):
        path = tmp_path / filename
        original = path.read_bytes()
        observation = json.loads(original)
        observation[field] = value
        path.write_text(json.dumps(observation), encoding="utf-8")
        with pytest.raises(ValueError, match="local observation provenance"):
            proposal.build_manifest()
        path.write_bytes(original)


def test_manifest_rejects_changed_local_replay(tmp_path: Path, monkeypatch: object) -> None:
    """Reject a locally replayed result that differs from the source-bound prediction."""
    import shutil

    import pytest
    import qi_tuna_qx_destination as proposal

    for name in (
        "baseline.cq",
        "rotated.cq",
        "asymmetric.cq",
        "local-parse-observation.json",
        "local-qx-output-observation.json",
        "local-replay.json",
    ):
        shutil.copyfile(proposal.PROPOSAL / name, tmp_path / name)
    monkeypatch.setattr(proposal, "PROPOSAL", tmp_path)  # type: ignore[attr-defined]
    path = tmp_path / "local-replay.json"
    replay = json.loads(path.read_bytes())
    replay["rows"][2]["counts"] = {"000": 1}
    path.write_text(json.dumps(replay), encoding="utf-8")
    with pytest.raises(ValueError, match="local replay provenance or results"):
        proposal.build_manifest()


def test_manifest_rejects_contradictory_backend_and_replay_metadata(monkeypatch: object) -> None:
    """Reject contradictory backend limits and impossible or misleading replay metadata."""
    import pytest
    import qi_tuna_qx_destination as proposal

    original_read_bytes = Path.read_bytes
    for filename, changes, expected in (
        ("approved-qx-backend.json", {"id": 7}, "backend snapshot"),
        ("approved-qx-backend.json", {"id": True}, "backend snapshot"),
        ("approved-qx-backend.json", {"nqubits": 2}, "backend snapshot"),
        ("approved-qx-backend.json", {"nqubits": 3.0}, "backend snapshot"),
        ("approved-qx-backend.json", {"identifier": "different_backend"}, "backend snapshot"),
        ("approved-qx-backend.json", {"max_number_of_shots": 1}, "backend snapshot"),
        ("approved-qx-backend.json", {"max_number_of_shots": 2048.0}, "backend snapshot"),
        ("approved-qx-backend.json", {"job_execution_time_limit": 1}, "backend snapshot"),
        ("approved-qx-backend.json", {"job_execution_time_limit": 3600.0}, "backend snapshot"),
        ("approved-qx-backend.json", {"supports_raw_data": False}, "backend snapshot"),
        ("approved-qx-backend.json", {"is_hardware": True}, "backend snapshot"),
        ("approved-qx-backend.json", {"max_jobs_per_batch_job": 1}, "backend snapshot"),
        ("approved-qx-backend.json", {"max_jobs_per_batch_job": 3.0}, "backend snapshot"),
        ("approved-qx-backend.json", {"batchjobs_per_queue_limit": 0}, "backend snapshot"),
        ("approved-qx-backend.json", {"batchjobs_per_queue_limit": True}, "backend snapshot"),
        ("approved-qx-backend.json", {"gateset": ["init", "measure", "barrier"]}, "backend snapshot"),
        ("approved-qx-backend.json", {"gateset": ["X", "measure", "barrier"]}, "backend snapshot"),
        ("approved-qx-backend.json", {"gateset": ["X", "init", "barrier"]}, "backend snapshot"),
        ("approved-qx-backend.json", {"gateset": ["X", "init", "measure"]}, "backend snapshot"),
        ("approved-qx-backend.json", {"gateset": {"X": 1, "init": 1, "measure": 1, "barrier": 1}}, "backend snapshot"),
        ("local-replay.json", {"python_version": "3.13.fabricated"}, "local replay"),
        ("local-replay.json", {"boundary": "provider authenticated"}, "local replay"),
        (
            "local-replay.json",
            {"started_utc": "9999-01-01T00:00:00+00:00", "finished_utc": "9999-01-01T00:00:01+00:00"},
            "local replay",
        ),
    ):

        def altered_read_bytes(path: Path, target: str = filename, mutations: Mapping[str, object] = changes) -> bytes:
            content = original_read_bytes(path)
            if path.name == target:
                data = json.loads(content)
                data.update(mutations)
                return json.dumps(data).encode()
            return content

        with monkeypatch.context() as context:  # type: ignore[attr-defined]
            context.setattr(Path, "read_bytes", altered_read_bytes)
            with pytest.raises(ValueError, match=expected):
                proposal.build_manifest()


def test_terminal_screen_rejects_wrong_or_incomplete_shots() -> None:
    """Catch changed terminal labels, malformed shot widths and partial collections."""
    import pytest
    import qi_tuna_qx_destination as proposal

    good = ["001"] * 2048
    if proposal.screen_shots(good, "001") != {"shots": 2048, "expected": "001", "mismatches": 0, "passed": True}:
        raise AssertionError("the deterministic asymmetric control must pass")
    wrong = good.copy()
    wrong[100] = "000"
    result = proposal.screen_shots(wrong, "001")
    if result["passed"] is not False or result["mismatches"] != 1:
        raise AssertionError("one valid but incorrect label must fail the deterministic screen")
    for malformed in (good[:-1], ["01"] * 2048, ["00x"] * 2048):
        with pytest.raises(ValueError, match="2048 width-3 binary shots"):
            proposal.screen_shots(malformed, "001")


def write_synthetic_collection(directory: Path) -> None:
    """Create a local fixture that exercises receipt bindings without a provider call."""
    import hashlib
    import shutil

    import qi_tuna_qx_destination as proposal

    directory.mkdir()
    raw_dir = directory / "raw"
    raw_dir.mkdir()
    manifest = proposal.build_manifest()
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    (directory / "cases.json").write_bytes(manifest_bytes)
    submission_jobs = []
    result_jobs = []
    for index, row in enumerate(manifest["circuits"]):
        job_id = 1000 + index
        shutil.copyfile(proposal.PROPOSAL / row["file"], directory / row["file"])
        raw = [row["expected_output"]] * 2048
        (raw_dir / f"{row['file']}.json").write_text(json.dumps(raw), encoding="utf-8")
        submission_jobs.append({"file": row["file"], "job": job_id, "sha256": row["sha256"]})
        result_jobs.append(
            {
                "file": row["file"],
                "job": {
                    "id": job_id,
                    "file_id": 3000 + index,
                    "batch_job_id": 100,
                    "status": "completed",
                    "created_on": "2026-10-28T01:58:50+00:00",
                    "queued_at": "2026-10-28T01:58:55+00:00",
                    "finished_at": "2026-10-28T01:59:00+00:00",
                    "number_of_shots": 2048,
                    "raw_data_enabled": True,
                },
                "results": [
                    {
                        "id": 2000 + index,
                        "created_on": "2026-10-28T01:58:59+00:00",
                        "job_id": job_id,
                        "shots_requested": 2048,
                        "shots_done": 2048,
                        "execution_time_in_seconds": 1,
                        "results": {row["expected_output"]: 2048},
                    }
                ],
                "logs": None,
            }
        )
    submission = {
        "schema": "qi-submission-v2",
        "state": "enqueued",
        "backend": manifest["backend"],
        "backend_type_id": 1,
        "shots": 2048,
        "cases_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "batch_job": 100,
        "submitted_utc": "2026-10-28T01:55:00+00:00",
        "jobs": submission_jobs,
    }
    (directory / "submission.json").write_text(json.dumps(submission), encoding="utf-8")
    (directory / "results.json").write_text(
        json.dumps(
            {
                "schema": "qi-collection-v1",
                "collected_utc": "2026-10-28T01:59:30+00:00",
                "jobs": result_jobs,
                "transactions": [],
            }
        ),
        encoding="utf-8",
    )
    readback = {
        "schema": "qi-qx-destination-readback-v1",
        "started_utc": "2026-10-28T02:00:00+00:00",
        "observed_utc": "2026-10-28T02:00:01+00:00",
        "batch": {"id": 100, "backend_type_id": 1, "job_ids": [1000, 1001, 1002]},
        "jobs": [
            {
                "job_id": 1000 + index,
                "file_id": 3000 + index,
                "created_on": "2026-10-28T01:58:50+00:00",
                "queued_at": "2026-10-28T01:58:55+00:00",
                "finished_at": "2026-10-28T01:59:00+00:00",
                "number_of_shots": 2048,
                "raw_data_enabled": True,
                "compile_stage": "none",
                "compile_properties": {},
                "stored_source_sha256": row["sha256"],
                "provider_result_sha256": hashlib.sha256(
                    json.dumps(
                        {**result_jobs[index]["results"][0], "raw_data": [row["expected_output"]] * 2048},
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=False,
                        allow_nan=False,
                    ).encode()
                ).hexdigest(),
            }
            for index, row in enumerate(manifest["circuits"])
        ],
    }
    (directory / "source-readback.json").write_text(json.dumps(readback), encoding="utf-8")


def test_collection_replay_rejects_misbound_identity_and_charges(tmp_path: Path) -> None:
    """Catch a wrong job-to-file association or any nonempty transaction list."""
    import pytest
    import qi_tuna_qx_destination as proposal

    run = tmp_path / "run"
    write_synthetic_collection(run)
    report = proposal.analyze_collection(run)
    if report["terminal_screen_passed"] is not True or report["total_shots"] != 6144:
        raise AssertionError("the complete source-bound local fixture should pass the QX screen")
    path = run / "results.json"
    collection = json.loads(path.read_bytes())
    collection["jobs"][0]["job"]["id"] = 1001
    path.write_text(json.dumps(collection), encoding="utf-8")
    with pytest.raises(ValueError, match="identity"):
        proposal.analyze_collection(run)
    collection["jobs"][0]["job"]["id"] = 1000
    collection["transactions"] = [{"change": -1}, {"change": 1}]
    path.write_text(json.dumps(collection), encoding="utf-8")
    with pytest.raises(ValueError, match="transaction"):
        proposal.analyze_collection(run)


def test_collection_cli_preserves_a_failed_screen(tmp_path: Path) -> None:
    """Catch a CLI that reports success for a bound but incorrect deterministic output."""
    run = tmp_path / "run"
    write_synthetic_collection(run)
    output = tmp_path / "analysis.json"
    valid = subprocess.run(
        [sys.executable, str(SCRIPT), "--collection", str(run), "--analysis-out", str(output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if valid.returncode != 0 or json.loads(output.read_bytes())["terminal_screen_passed"] is not True:
        raise AssertionError(f"valid collected fixture did not pass: {valid.stderr}")
    collected_path = run / "results.json"
    collected = json.loads(collected_path.read_bytes())
    raw_path = run / "raw" / "baseline.cq.json"
    raw = json.loads(raw_path.read_bytes())
    raw[0] = "001"
    raw_path.write_text(json.dumps(raw), encoding="utf-8")
    collected["jobs"][0]["results"][0]["results"] = {"000": 2047, "001": 1}
    collected_path.write_text(json.dumps(collected), encoding="utf-8")
    import hashlib

    readback_path = run / "source-readback.json"
    readback = json.loads(readback_path.read_bytes())
    provider_result = {**collected["jobs"][0]["results"][0], "raw_data": raw}
    readback["jobs"][0]["provider_result_sha256"] = hashlib.sha256(
        json.dumps(provider_result, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
    ).hexdigest()
    readback_path.write_text(json.dumps(readback), encoding="utf-8")
    failed_output = tmp_path / "failed.json"
    invalid = subprocess.run(
        [sys.executable, str(SCRIPT), "--collection", str(run), "--analysis-out", str(failed_output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if invalid.returncode == 0 or json.loads(failed_output.read_bytes())["terminal_screen_passed"] is not False:
        raise AssertionError("the failed screen must be retained and return a nonzero status")


def test_collection_rejects_boolean_histogram_counts(tmp_path: Path) -> None:
    """Catch JSON booleans masquerading as integer histogram counts."""
    import pytest
    import qi_tuna_qx_destination as proposal

    run = tmp_path / "run"
    write_synthetic_collection(run)
    path = run / "results.json"
    collected = json.loads(path.read_bytes())
    raw_path = run / "raw" / "baseline.cq.json"
    raw = json.loads(raw_path.read_bytes())
    raw[0] = "001"
    raw_path.write_text(json.dumps(raw), encoding="utf-8")
    collected["jobs"][0]["results"][0]["results"] = {"000": 2047, "001": True}
    path.write_text(json.dumps(collected), encoding="utf-8")
    with pytest.raises(ValueError, match="histogram"):
        proposal.analyze_collection(run)


def test_collection_rejects_float_counts_and_duplicate_result_ids(tmp_path: Path) -> None:
    """Catch non-integer provider shot counts and duplicated result identities."""
    import pytest
    import qi_tuna_qx_destination as proposal

    run = tmp_path / "run"
    write_synthetic_collection(run)
    path = run / "results.json"
    original = json.loads(path.read_bytes())
    malformed = json.loads(json.dumps(original))
    malformed["jobs"][0]["job"]["number_of_shots"] = 2048.0
    malformed["jobs"][0]["results"][0]["shots_requested"] = 2048.0
    malformed["jobs"][0]["results"][0]["shots_done"] = 2048.0
    path.write_text(json.dumps(malformed), encoding="utf-8")
    with pytest.raises(ValueError, match="shot count"):
        proposal.analyze_collection(run)
    malformed = json.loads(json.dumps(original))
    malformed["jobs"][1]["results"][0]["id"] = malformed["jobs"][0]["results"][0]["id"]
    path.write_text(json.dumps(malformed), encoding="utf-8")
    with pytest.raises(ValueError, match="result identity"):
        proposal.analyze_collection(run)


def test_collection_rejects_backend_or_stored_source_mismatch(tmp_path: Path) -> None:
    """Catch swapped provider sources and a batch recorded under another backend."""
    import pytest
    import qi_tuna_qx_destination as proposal

    run = tmp_path / "run"
    write_synthetic_collection(run)
    path = run / "source-readback.json"
    original = json.loads(path.read_bytes())
    changed = json.loads(json.dumps(original))
    changed["batch"]["backend_type_id"] = 7
    path.write_text(json.dumps(changed), encoding="utf-8")
    with pytest.raises(ValueError, match="backend readback"):
        proposal.analyze_collection(run)
    changed = json.loads(json.dumps(original))
    changed["jobs"][0]["stored_source_sha256"] = changed["jobs"][1]["stored_source_sha256"]
    path.write_text(json.dumps(changed), encoding="utf-8")
    with pytest.raises(ValueError, match="source readback"):
        proposal.analyze_collection(run)


def test_collection_rejects_one_file_identity_for_distinct_sources(tmp_path: Path) -> None:
    """Catch incompatible source hashes attributed to the same provider file ID."""
    import pytest
    import qi_tuna_qx_destination as proposal

    run = tmp_path / "run"
    write_synthetic_collection(run)
    source_path = run / "source-readback.json"
    source = json.loads(source_path.read_bytes())
    source["jobs"][1]["file_id"] = source["jobs"][0]["file_id"]
    source_path.write_text(json.dumps(source), encoding="utf-8")
    result_path = run / "results.json"
    results = json.loads(result_path.read_bytes())
    results["jobs"][1]["job"]["file_id"] = results["jobs"][0]["job"]["file_id"]
    result_path.write_text(json.dumps(results), encoding="utf-8")
    with pytest.raises(ValueError, match="source readback"):
        proposal.analyze_collection(run)


def test_readback_capture_checks_provider_batch_and_source_bytes(tmp_path: Path) -> None:
    """Catch provider readbacks that swap source files or report another backend."""
    import pytest
    import qi_tuna_qx_destination as proposal

    run = tmp_path / "run"
    write_synthetic_collection(run)
    manifest = proposal.build_manifest()

    class ReadOnlyClient:
        def __init__(self) -> None:
            self.backend_id = 1
            self.swap_sources = False
            self.multiple_results = False
            self.bad_shot_count = False
            self.bad_raw_flag = False
            self.bad_compile_stage = False
            self.bad_compile_properties = False
            self.missing_result_created = False
            self.bad_result_time = False
            self.bad_result_width = False
            self.duplicate_result_id = False
            self.bad_batch_total = False
            self.paths: list[str] = []

        def get(self, path: str, **params: object) -> dict[str, object]:
            if path == "/batch_jobs":
                if params != {"id": 100, "page": 1, "size": 100}:
                    raise ValueError("unexpected provider batch page")
                self.paths.append("/batch_jobs?id=100")
                return {
                    "items": [{"id": 100, "backend_type_id": self.backend_id, "job_ids": [1000, 1001, 1002]}],
                    "page": 1,
                    "pages": 1,
                    "total": 2 if self.bad_batch_total else 1,
                    "size": 100,
                }
            self.paths.append(path)
            for index, row in enumerate(manifest["circuits"]):
                if path == f"/jobs/{1000 + index}":
                    return {
                        "id": 1000 + index,
                        "batch_job_id": 100,
                        "file_id": 3000 + index,
                        "status": "completed",
                        "number_of_shots": 1 if self.bad_shot_count else 2048,
                        "raw_data_enabled": not self.bad_raw_flag,
                        "created_on": "2026-10-28T01:58:50+00:00",
                        "queued_at": "2026-10-28T01:58:55+00:00",
                        "finished_at": "2026-10-28T01:59:00+00:00",
                    }
                if path == f"/files/{3000 + index}":
                    actual = (index + 1) % 3 if self.swap_sources else index
                    return {
                        "id": 3000 + index,
                        "content": (run / manifest["circuits"][actual]["file"]).read_text(),
                        "compile_stage": "other" if self.bad_compile_stage else "none",
                        "compile_properties": {"unexpected": True} if self.bad_compile_properties else {},
                    }
                if path == f"/results/job/{1000 + index}":
                    if params != {"page": 1, "size": 100}:
                        raise ValueError("unexpected provider result page")
                    collected = json.loads((run / "results.json").read_bytes())
                    result = dict(collected["jobs"][index]["results"][0])
                    if self.missing_result_created:
                        result.pop("created_on")
                    if self.bad_result_time:
                        result.pop("execution_time_in_seconds")
                    if self.duplicate_result_id:
                        result["id"] = 2000
                    result["raw_data"] = json.loads((run / "raw" / f"{row['file']}.json").read_bytes())
                    if self.bad_result_width:
                        result["raw_data"][0] = "01"
                        result["results"] = {row["expected_output"]: 2047, "01": 1}
                    return {
                        "items": [result],
                        "page": 1,
                        "pages": 2 if self.multiple_results else 1,
                        "size": 100,
                        "total": 2 if self.multiple_results else 1,
                    }
            raise ValueError(f"unexpected provider path: {path}")

    client = ReadOnlyClient()
    readback = proposal.capture_readback(run, client)
    if readback["batch"]["backend_type_id"] != 1 or len(readback["jobs"]) != 3:
        raise AssertionError("QX batch and all source readbacks must be retained")
    if client.paths != [
        "/batch_jobs?id=100",
        "/jobs/1000",
        "/files/3000",
        "/results/job/1000",
        "/jobs/1001",
        "/files/3001",
        "/results/job/1001",
        "/jobs/1002",
        "/files/3002",
        "/results/job/1002",
    ]:
        raise AssertionError("readback must visit the exact batch, jobs and attached file identities")
    client.bad_batch_total = True
    with pytest.raises(ValueError, match="exactly one batch"):
        proposal.capture_readback(run, client)
    client.bad_batch_total = False
    client.bad_shot_count = True
    with pytest.raises(ValueError, match="source readback"):
        proposal.capture_readback(run, client)
    client.bad_shot_count = False
    client.bad_raw_flag = True
    with pytest.raises(ValueError, match="source readback"):
        proposal.capture_readback(run, client)
    client.bad_raw_flag = False
    client.bad_compile_stage = True
    with pytest.raises(ValueError, match="source readback"):
        proposal.capture_readback(run, client)
    client.bad_compile_stage = False
    client.bad_compile_properties = True
    with pytest.raises(ValueError, match="source readback"):
        proposal.capture_readback(run, client)
    client.bad_compile_properties = False
    client.missing_result_created = True
    with pytest.raises(ValueError, match="result creation"):
        proposal.capture_readback(run, client)
    client.missing_result_created = False
    client.bad_result_time = True
    with pytest.raises(ValueError, match="execution time"):
        proposal.capture_readback(run, client)
    client.bad_result_time = False
    client.bad_result_width = True
    with pytest.raises(ValueError, match="provider result readback"):
        proposal.capture_readback(run, client)
    client.bad_result_width = False
    client.duplicate_result_id = True
    with pytest.raises(ValueError, match="result identity"):
        proposal.capture_readback(run, client)
    client.duplicate_result_id = False
    client.multiple_results = True
    with pytest.raises(ValueError, match="provider result readback"):
        proposal.capture_readback(run, client)
    client.multiple_results = False
    client.backend_id = 7
    with pytest.raises(ValueError, match="backend readback"):
        proposal.capture_readback(run, client)
    client.backend_id = 1
    client.swap_sources = True
    with pytest.raises(ValueError, match="source readback"):
        proposal.capture_readback(run, client)


def test_readback_refuses_invalid_manifest_before_loading_credentials(tmp_path: Path, monkeypatch: object) -> None:
    """Catch token refresh or provider access before local case validation."""
    import pytest
    import qi_tuna_qx_destination as proposal

    run = tmp_path / "run"
    write_synthetic_collection(run)
    manifest = run / "cases.json"
    manifest.write_bytes(manifest.read_bytes() + b" ")

    def forbidden_client() -> None:
        raise AssertionError("credentials must not be loaded for an invalid manifest")

    monkeypatch.setattr(proposal, "Client", forbidden_client)  # type: ignore[attr-defined]
    with pytest.raises(ValueError, match="readback manifest"):
        proposal.capture_readback(run)


def test_collection_rejects_coherent_replacement_of_raw_and_histogram(tmp_path: Path) -> None:
    """Catch retained results changed after the provider result readback was captured."""
    import pytest
    import qi_tuna_qx_destination as proposal

    run = tmp_path / "run"
    write_synthetic_collection(run)
    raw_path = run / "raw" / "baseline.cq.json"
    shots = json.loads(raw_path.read_bytes())
    shots[0] = "001"
    raw_path.write_text(json.dumps(shots), encoding="utf-8")
    result_path = run / "results.json"
    result = json.loads(result_path.read_bytes())
    result["jobs"][0]["results"][0]["results"] = {"000": 2047, "001": 1}
    result_path.write_text(json.dumps(result), encoding="utf-8")
    with pytest.raises(ValueError, match="provider result readback"):
        proposal.analyze_collection(run)


def test_collection_rejects_incoherent_readback_chronology(tmp_path: Path) -> None:
    """Catch readback timestamps that predate collection or provider completion."""
    import pytest
    import qi_tuna_qx_destination as proposal

    run = tmp_path / "run"
    write_synthetic_collection(run)
    path = run / "source-readback.json"
    readback = json.loads(path.read_bytes())
    readback["observed_utc"] = "1900-01-01T00:00:00+00:00"
    path.write_text(json.dumps(readback), encoding="utf-8")
    with pytest.raises(ValueError, match="chronology"):
        proposal.analyze_collection(run)


def test_capture_output_is_reserved_before_client_access(tmp_path: Path, monkeypatch: object) -> None:
    """Catch read requests before a missing parent or dangling symlink is rejected."""
    import pytest
    import qi_tuna_qx_destination as proposal

    run = tmp_path / "run"
    write_synthetic_collection(run)

    def forbidden_client() -> None:
        raise AssertionError("invalid output must fail before credential loading")

    monkeypatch.setattr(proposal, "Client", forbidden_client)  # type: ignore[attr-defined]
    missing = tmp_path / "missing" / "readback.json"
    dangling = tmp_path / "dangling.json"
    dangling.symlink_to(tmp_path / "target-not-created.json")
    for output in (missing, dangling):
        monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--capture-readback", str(run), "--readback-out", str(output)])  # type: ignore[attr-defined]
        with pytest.raises((FileNotFoundError, FileExistsError)):
            proposal.main()


def test_failed_capture_retains_explicit_incomplete_receipt(tmp_path: Path, monkeypatch: object) -> None:
    """Catch partial or misleading readback output after a capture error."""
    import pytest
    import qi_tuna_qx_destination as proposal

    run = tmp_path / "run"
    write_synthetic_collection(run)
    output = tmp_path / "readback.json"

    def failed_capture(_run: Path) -> dict[str, object]:
        raise ValueError("synthetic provider failure")

    monkeypatch.setattr(proposal, "capture_readback", failed_capture)  # type: ignore[attr-defined]
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--capture-readback", str(run), "--readback-out", str(output)])  # type: ignore[attr-defined]
    with pytest.raises(ValueError, match="synthetic provider failure"):
        proposal.main()
    record = json.loads(output.read_bytes())
    if record != {"schema": "qi-qx-destination-readback-incomplete-v1"}:
        raise AssertionError("a failed capture must leave an explicitly incomplete receipt")


def test_provider_and_local_clocks_are_not_falsely_ordered(tmp_path: Path) -> None:
    """Allow a fast job or subsecond completion without assuming synchronized clocks."""
    import qi_tuna_qx_destination as proposal

    run = tmp_path / "run"
    write_synthetic_collection(run)
    result_path = run / "results.json"
    readback_path = run / "source-readback.json"
    result = json.loads(result_path.read_bytes())
    readback = json.loads(readback_path.read_bytes())
    for created, queued, finished in (
        ("2026-10-28T01:54:58+00:00", "2026-10-28T01:54:59+00:00", "2026-10-28T01:54:59.900000+00:00"),
        ("2026-10-28T01:59:29+00:00", "2026-10-28T01:59:30+00:00", "2026-10-28T01:59:30.900000+00:00"),
    ):
        for row in result["jobs"]:
            row["job"].update(created_on=created, queued_at=queued, finished_at=finished)
        for row in readback["jobs"]:
            row.update(created_on=created, queued_at=queued, finished_at=finished)
        result_path.write_text(json.dumps(result), encoding="utf-8")
        readback_path.write_text(json.dumps(readback), encoding="utf-8")
        if proposal.analyze_collection(run)["terminal_screen_passed"] is not True:
            raise AssertionError("provider and local timestamps have separate clock domains")


def test_local_collection_screen_cannot_admit_provider_conformance(tmp_path: Path) -> None:
    """Catch promotion of fabricated local receipts into a provider-execution verdict."""
    import qi_tuna_qx_destination as proposal

    run = tmp_path / "run"
    write_synthetic_collection(run)
    report = proposal.analyze_collection(run)
    if report["terminal_screen_passed"] is not True or report["provider_conformance_admitted"] is not False:
        raise AssertionError("local receipt consistency cannot admit a provider execution")


def test_collection_rejects_missing_result_creation_time(tmp_path: Path) -> None:
    """Catch a coherently rehashed provider result missing its required creation timestamp."""
    import hashlib

    import pytest
    import qi_tuna_qx_destination as proposal

    run = tmp_path / "run"
    write_synthetic_collection(run)
    results_path = run / "results.json"
    results = json.loads(results_path.read_bytes())
    result = results["jobs"][0]["results"][0]
    result.pop("created_on")
    results_path.write_text(json.dumps(results), encoding="utf-8")
    raw = json.loads((run / "raw" / "baseline.cq.json").read_bytes())
    readback_path = run / "source-readback.json"
    readback = json.loads(readback_path.read_bytes())
    readback["jobs"][0]["provider_result_sha256"] = hashlib.sha256(
        json.dumps(
            {**result, "raw_data": raw}, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode()
    ).hexdigest()
    readback_path.write_text(json.dumps(readback), encoding="utf-8")
    with pytest.raises(ValueError, match="result creation"):
        proposal.analyze_collection(run)
