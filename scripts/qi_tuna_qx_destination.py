"""Build the reduced, unapproved QX destination-conformance manifest."""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from qi_platform import Client, _check_submission_manifest
from qi_tuna_readout_mapping_cases import measurement_map, physical_stream

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "results/quantum_inspire/proposals/tuna-destination-qx-conformance"
CASE = ROOT / "docs/design/tuna-destination-qx-conformance.md"
SOURCES = (
    ("baseline", "004667f94872f372eab01eb75dfbc6e5fb25e0b16534d3c20da6b1c7f5dc91af", "000"),
    ("rotated", "39454ac0e32f0bebfd687d5def41666ee7e35b3af5d61430c2f0b084d355e584", "000"),
    ("asymmetric", "dc9de0253a6d544bf76ba215a3fca2cf253dda549364f899064f927c1d7f0ecd", "001"),
)


def digest(path: Path) -> str:
    """Hash exact bytes without modifying the source."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def observed_time(value: object) -> datetime.datetime:
    """Parse an explicitly timezone-aware timestamp for the receipt chronology."""
    if not isinstance(value, str):
        raise ValueError("receipt chronology requires timezone-aware timestamps")
    try:
        parsed = datetime.datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("receipt chronology requires timezone-aware timestamps") from error
    if parsed.utcoffset() is None:
        raise ValueError("receipt chronology requires timezone-aware timestamps")
    return parsed.astimezone(datetime.UTC)


def provider_job_times(job: dict[str, Any]) -> tuple[datetime.datetime, datetime.datetime, datetime.datetime]:
    """Check provider-reported job order without equating provider and local clocks."""
    created = observed_time(job.get("created_on"))
    queued = observed_time(job.get("queued_at"))
    finished = observed_time(job.get("finished_at"))
    if not created <= queued <= finished:
        raise ValueError("provider job chronology is inconsistent")
    return created, queued, finished


def validate_result_creation(result: dict[str, Any]) -> None:
    """Require the API Result object's timezone-aware creation timestamp."""
    try:
        observed_time(result.get("created_on"))
    except ValueError as error:
        raise ValueError("result creation timestamp is missing or invalid") from error


def execution_seconds(value: object) -> Decimal:
    """Validate a provider execution duration against the per-job bound."""
    if type(value) not in (int, float):
        raise ValueError("execution time must be a finite decimal")
    try:
        seconds = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError("execution time must be a finite decimal") from error
    if not seconds.is_finite() or not 0 <= seconds <= 3600:
        raise ValueError("execution time exceeds the case bound")
    return seconds


def result_digest(value: dict[str, Any]) -> str:
    """Hash a provider result including its ordered raw shot list."""
    content = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
    return hashlib.sha256(content).hexdigest()


def build_manifest() -> dict[str, Any]:
    """Bind three frozen sources and their documented deterministic QX outputs."""
    rows = []
    streams = {}
    for name, expected_hash, expected_output in SOURCES:
        path = PROPOSAL / f"{name}.cq"
        if digest(path) != expected_hash:
            raise ValueError(f"{name} source differs from the frozen case")
        source = path.read_text(encoding="utf-8")
        streams[name] = physical_stream(source)
        rows.append(
            {
                "name": name,
                "file": path.name,
                "sha256": expected_hash,
                "expected_output": expected_output,
                "measurement_to_bit_map": measurement_map(source),
            }
        )
    if streams["baseline"] != streams["rotated"]:
        raise ValueError("baseline and rotated physical instruction streams differ")
    asymmetric = list(streams["baseline"]["instructions"])
    asymmetric.insert(3, ["X", [0], None])
    if streams["asymmetric"] != {**streams["baseline"], "instructions": asymmetric}:
        raise ValueError("asymmetric control must add only X on q0")
    backend_path = ROOT / "docs/evidence/tuna-projector-geometry/approved-qx-backend.json"
    backend = json.loads(backend_path.read_bytes())
    if (
        type(backend.get("id")) is not int
        or backend["id"] != 1
        or backend.get("identifier") != "QXsinglenodesimulator"
        or type(backend.get("nqubits")) is not int
        or backend["nqubits"] < 3
        or type(backend.get("max_number_of_shots")) is not int
        or backend["max_number_of_shots"] != 2048
        or type(backend.get("job_execution_time_limit")) is not int
        or backend["job_execution_time_limit"] != 3600
        or backend.get("supports_raw_data") is not True
        or backend.get("is_hardware") is not False
        or type(backend.get("max_jobs_per_batch_job")) is not int
        or backend["max_jobs_per_batch_job"] < 3
        or type(backend.get("batchjobs_per_queue_limit")) is not int
        or backend["batchjobs_per_queue_limit"] < 1
        or not isinstance(backend.get("gateset"), list)
        or not {"X", "init", "measure", "barrier"}.issubset(backend["gateset"])
    ):
        raise ValueError("backend snapshot differs from the historical case limits")
    parse = json.loads((PROPOSAL / "local-parse-observation.json").read_bytes())
    local_qx = json.loads((PROPOSAL / "local-qx-output-observation.json").read_bytes())
    replay_path = PROPOSAL / "local-replay.json"
    replay = json.loads(replay_path.read_bytes())
    try:
        observed_time(parse.get("observed_utc"))
        started = observed_time(local_qx.get("started_utc"))
        finished = observed_time(local_qx.get("finished_utc"))
        if started > finished or not all(
            isinstance(observation.get("python_version"), str) and observation["python_version"]
            for observation in (parse, local_qx)
        ):
            raise ValueError("invalid observation order or interpreter identity")
    except ValueError as error:
        raise ValueError("local observation provenance is invalid") from error
    source_prefix = "results/quantum_inspire/proposals/tuna-destination-qx-conformance"
    if (
        parse.get("schema") != "qi-qx-reduced-destination-local-parse-v1"
        or parse.get("libqasm_version") != "1.2.1"
        or parse.get("baseline_rotated_physical_stream_equal") is not True
        or parse.get("asymmetric_only_adds_x_q0") is not True
        or parse.get("physical_stream_producer_sha256") != digest(ROOT / "scripts/qi_tuna_readout_mapping_cases.py")
        or not isinstance(parse.get("sources"), list)
        or len(parse["sources"]) != len(rows)
    ):
        raise ValueError("local parser observation differs from the source contract")
    if (
        local_qx.get("schema") != "qi-qx-reduced-destination-local-output-v1"
        or local_qx.get("qxelarator_version") != "0.10.0"
        or not isinstance(local_qx.get("sources"), list)
        or len(local_qx["sources"]) != len(rows)
    ):
        raise ValueError("local QX observation differs from the source contract")
    for row, parsed, observed in zip(rows, parse["sources"], local_qx["sources"], strict=True):
        source = f"{source_prefix}/{row['file']}"
        if (
            parsed.get("name") != row["name"]
            or parsed.get("source") != source
            or parsed.get("sha256") != row["sha256"]
            or parsed.get("parser_errors") != []
            or parsed.get("measurement_map") != row["measurement_to_bit_map"]
        ):
            raise ValueError("local parser observation differs from the source contract")
        if (
            observed.get("source") != source
            or observed.get("sha256") != row["sha256"]
            or observed.get("shots") != 1
            or observed.get("counts") != {row["expected_output"]: 1}
        ):
            raise ValueError("local QX observation differs from the source contract")
    try:
        replay_started = observed_time(replay.get("started_utc"))
        replay_finished = observed_time(replay.get("finished_utc"))
    except ValueError as error:
        raise ValueError("local replay provenance is invalid") from error
    expected_replay_rows = [
        {"name": name, "source_sha256": source_hash, "parser_errors": [], "shots": 1, "counts": {output: 1}}
        for name, source_hash, output in SOURCES
    ]
    if (
        replay.get("schema") != "qi-qx-destination-local-replay-v1"
        or replay_started > replay_finished
        or replay_finished > datetime.datetime.now(datetime.UTC)
        or not isinstance(replay.get("python_version"), str)
        or re.fullmatch(r"3\.13\.\d+", replay["python_version"]) is None
        or replay.get("versions") != {"libqasm": "1.2.1", "qxelarator": "0.10.0"}
        or replay.get("boundary")
        != "Local parser and one-shot simulator replay; no provider execution or Tuna measurement."
        or replay.get("producer_sha256") != digest(ROOT / "scripts/qi_tuna_qx_local_replay.py")
        or replay.get("command") != '"$QI_PYTHON" scripts/qi_tuna_qx_local_replay.py --out OUTPUT'
        or replay.get("rows") != expected_replay_rows
        or any(
            type(row.get("shots")) is not int or any(type(count) is not int for count in row.get("counts", {}).values())
            for row in replay["rows"]
        )
    ):
        raise ValueError("local replay provenance or results differ from the source contract")
    evidence = (
        PROPOSAL / "local-parse-observation.json",
        PROPOSAL / "local-qx-output-observation.json",
        replay_path,
        ROOT / "scripts/qi_tuna_qx_local_replay.py",
        backend_path,
        ROOT / "scripts/qi_platform.py",
        ROOT / "scripts/qi_tuna_readout_mapping_cases.py",
        ROOT / "scripts/qi_projector_compiler_admission.py",
        CASE,
        Path(__file__),
    )
    return {
        "schema": "qi-qx-destination-conformance-case-v1",
        "status": "working-unapproved",
        "provider_execution_authorized": False,
        "backend": "QXsinglenodesimulator",
        "backend_type_id": 1,
        "nqubits": 3,
        "shots": 2048,
        "circuits": rows,
        "job_execution_ceiling_seconds": 3600,
        "total_execution_ceiling_seconds": 10800,
        "allowed_credit_change": 0,
        "evidence": {path.relative_to(ROOT).as_posix(): digest(path) for path in evidence},
        "boundary": (
            "Reduced QX terminal-output conformance only; the 17-qubit Tuna source and intermediate "
            "classical-bit history cannot be validated by QX. Fresh admission and exact approval are required."
        ),
    }


def screen_shots(shots: object, expected: str) -> dict[str, Any]:
    """Screen complete QX terminal shots against one frozen deterministic output."""
    if expected not in {"000", "001"}:
        raise ValueError("expected QX output is outside the frozen case")
    if (
        not isinstance(shots, list)
        or len(shots) != 2048
        or any(type(shot) is not str or len(shot) != 3 or set(shot) - {"0", "1"} for shot in shots)
    ):
        raise ValueError("screen requires 2048 width-3 binary shots")
    mismatches = sum(shot != expected for shot in shots)
    return {"shots": len(shots), "expected": expected, "mismatches": mismatches, "passed": mismatches == 0}


def capture_readback(run: Path, client: Any | None = None) -> dict[str, Any]:
    """Read and validate provider batch, job and stored-source identities without submitting."""
    manifest = build_manifest()
    expected_manifest = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    if (run / "cases.json").read_bytes() != expected_manifest:
        raise ValueError("readback manifest differs from the frozen proposal")
    submission = json.loads((run / "submission.json").read_bytes())
    if submission.get("schema") != "qi-submission-v2":
        raise ValueError("readback requires a v2 submission receipt")
    _check_submission_manifest(run, submission, require_enqueued=True)
    batch_id = submission.get("batch_job")
    submitted = submission.get("jobs")
    if (
        type(batch_id) is not int
        or batch_id <= 0
        or not isinstance(submitted, list)
        or len(submitted) != 3
        or any(type(row.get("job")) is not int or row["job"] <= 0 for row in submitted)
        or len({row["job"] for row in submitted}) != 3
    ):
        raise ValueError("backend readback submission identities are invalid")
    collected = json.loads((run / "results.json").read_bytes())
    submitted_time = observed_time(submission.get("submitted_utc"))
    collected_time = observed_time(collected.get("collected_utc"))
    started = datetime.datetime.now(datetime.UTC)
    if collected.get("schema") != "qi-collection-v1" or not submitted_time <= collected_time <= started:
        raise ValueError("readback chronology differs from submission and collection")
    if client is None:
        client = Client()
    response = client.get("/batch_jobs", id=batch_id, page=1, size=100)
    if (
        not isinstance(response, dict)
        or not isinstance(response.get("items"), list)
        or len(response["items"]) != 1
        or not isinstance(response["items"][0], dict)
        or type(response.get("page")) is not int
        or response["page"] != 1
        or type(response.get("pages")) is not int
        or response["pages"] != 1
        or type(response.get("total")) is not int
        or response["total"] != 1
        or type(response.get("size")) is not int
        or response["size"] < 1
    ):
        raise ValueError("backend readback must resolve exactly one batch")
    batch = response["items"][0]
    if (
        type(batch.get("id")) is not int
        or batch["id"] != batch_id
        or type(batch.get("backend_type_id")) is not int
        or batch["backend_type_id"] != 1
        or not isinstance(batch.get("job_ids"), list)
        or any(type(job_id) is not int for job_id in batch["job_ids"])
        or sorted(batch["job_ids"]) != sorted(row["job"] for row in submitted)
    ):
        raise ValueError("backend readback differs from the submitted QX batch")
    sources = {row["file"]: row["sha256"] for row in manifest["circuits"]}
    jobs = []
    file_ids: set[int] = set()
    result_ids: set[int] = set()
    for submitted_job in submitted:
        job_id = submitted_job["job"]
        job = client.get(f"/jobs/{job_id}")
        file_id = job.get("file_id")
        if (
            type(job.get("id")) is not int
            or job["id"] != job_id
            or type(job.get("batch_job_id")) is not int
            or job["batch_job_id"] != batch_id
            or job.get("status") != "completed"
            or type(job.get("number_of_shots")) is not int
            or job["number_of_shots"] != 2048
            or job.get("raw_data_enabled") is not True
            or type(file_id) is not int
            or file_id <= 0
            or file_id in file_ids
        ):
            raise ValueError("source readback job or file identity differs")
        provider_job_times(job)
        file_ids.add(file_id)
        stored = client.get(f"/files/{file_id}")
        text = stored.get("content")
        if (
            type(stored.get("id")) is not int
            or stored["id"] != file_id
            or not isinstance(text, str)
            or stored.get("compile_stage") != "none"
            or stored.get("compile_properties") != {}
            or hashlib.sha256(text.encode("utf-8")).hexdigest() != sources[submitted_job["file"]]
        ):
            raise ValueError("source readback differs from the approved source bytes")
        response = client.get(f"/results/job/{job_id}", page=1, size=100)
        results = response.get("items")
        if (
            not isinstance(results, list)
            or len(results) != 1
            or not isinstance(results[0], dict)
            or type(response.get("page")) is not int
            or response["page"] != 1
            or type(response.get("pages")) is not int
            or response["pages"] != 1
            or type(response.get("total")) is not int
            or response["total"] != 1
            or type(response.get("size")) is not int
            or response["size"] < 1
        ):
            raise ValueError("provider result readback requires exactly one result and one page")
        result = results[0]
        validate_result_creation(result)
        result_id = result.get("id")
        if type(result_id) is not int or result_id <= 0 or result_id in result_ids:
            raise ValueError("result identity must be positive and unique")
        result_ids.add(result_id)
        execution_seconds(result.get("execution_time_in_seconds"))
        try:
            screen_shots(result.get("raw_data"), "000")
        except ValueError as error:
            raise ValueError("provider result readback has invalid shots") from error
        if (
            type(result.get("job_id")) is not int
            or result["job_id"] != job_id
            or type(result.get("shots_requested")) is not int
            or result["shots_requested"] != 2048
            or type(result.get("shots_done")) is not int
            or result["shots_done"] != 2048
            or not isinstance(result.get("raw_data"), list)
            or len(result["raw_data"]) != 2048
            or not isinstance(result.get("results"), dict)
            or any(type(count) is not int or count <= 0 for count in result["results"].values())
            or Counter(result["raw_data"]) != Counter(result["results"])
        ):
            raise ValueError("provider result readback differs from the requested job")
        jobs.append(
            {
                "job_id": job_id,
                "file_id": file_id,
                "created_on": job["created_on"],
                "queued_at": job["queued_at"],
                "finished_at": job["finished_at"],
                "number_of_shots": job["number_of_shots"],
                "raw_data_enabled": job["raw_data_enabled"],
                "compile_stage": stored["compile_stage"],
                "compile_properties": stored["compile_properties"],
                "stored_source_sha256": sources[submitted_job["file"]],
                "provider_result_sha256": result_digest(result),
            }
        )
    return {
        "schema": "qi-qx-destination-readback-v1",
        "started_utc": started.isoformat(),
        "observed_utc": datetime.datetime.now(datetime.UTC).isoformat(),
        "batch": {"id": batch_id, "backend_type_id": 1, "job_ids": [row["job"] for row in submitted]},
        "jobs": jobs,
        "boundary": (
            "Authenticated readback of batch, job, stored source and result through the supplied client; "
            "stored source does not establish served analog execution, approval or account-wide billing."
        ),
    }


def analyze_collection(run: Path) -> dict[str, Any]:
    """Validate a collected QX batch and screen its bound ordered terminal shots."""
    manifest = build_manifest()
    expected_manifest = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    if (run / "cases.json").read_bytes() != expected_manifest:
        raise ValueError("collection manifest differs from the frozen proposal")
    submission = json.loads((run / "submission.json").read_bytes())
    if submission.get("schema") != "qi-submission-v2":
        raise ValueError("collection requires a v2 submission receipt")
    _check_submission_manifest(run, submission, require_enqueued=True)
    if type(submission.get("batch_job")) is not int or submission["batch_job"] <= 0:
        raise ValueError("submission batch identity must be a positive integer")
    submitted = submission.get("jobs")
    if (
        not isinstance(submitted, list)
        or len(submitted) != 3
        or any(type(row.get("job")) is not int or row["job"] <= 0 for row in submitted)
        or len({row["job"] for row in submitted}) != 3
    ):
        raise ValueError("submission job identity set is invalid")
    submitted_by_file = {row["file"]: row["job"] for row in submitted}
    readback = json.loads((run / "source-readback.json").read_bytes())
    readback_started = observed_time(readback.get("started_utc"))
    readback_finished = observed_time(readback.get("observed_utc"))
    batch = readback.get("batch")
    if (
        readback.get("schema") != "qi-qx-destination-readback-v1"
        or not isinstance(batch, dict)
        or type(batch.get("id")) is not int
        or batch["id"] != submission["batch_job"]
        or type(batch.get("backend_type_id")) is not int
        or batch["backend_type_id"] != 1
        or not isinstance(batch.get("job_ids"), list)
        or any(type(job_id) is not int for job_id in batch["job_ids"])
        or sorted(batch["job_ids"]) != sorted(submitted_by_file.values())
    ):
        raise ValueError("backend readback differs from the submitted QX batch")
    source_jobs = readback.get("jobs")
    if (
        not isinstance(source_jobs, list)
        or len(source_jobs) != 3
        or any(not isinstance(row, dict) or type(row.get("job_id")) is not int for row in source_jobs)
        or {row["job_id"] for row in source_jobs} != set(submitted_by_file.values())
        or any(type(row.get("file_id")) is not int or row["file_id"] <= 0 for row in source_jobs)
        or len({row["file_id"] for row in source_jobs}) != 3
    ):
        raise ValueError("source readback job identity set differs from submission")
    source_by_job = {row["job_id"]: row for row in source_jobs}
    collected = json.loads((run / "results.json").read_bytes())
    submitted_time = observed_time(submission.get("submitted_utc"))
    collected_time = observed_time(collected.get("collected_utc"))
    if (
        not submitted_time
        <= collected_time
        <= readback_started
        <= readback_finished
        <= datetime.datetime.now(datetime.UTC)
    ):
        raise ValueError("receipt chronology differs from submission, collection or readback time")
    if collected.get("schema") != "qi-collection-v1" or collected.get("transactions") != []:
        raise ValueError("collection schema or transaction list is invalid")
    jobs = collected.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != 3 or {row.get("file") for row in jobs} != set(submitted_by_file):
        raise ValueError("collection file identity set differs from the submission")
    jobs_by_file = {row["file"]: row for row in jobs}
    expected_raw = {f"{row['file']}.json" for row in manifest["circuits"]}
    if {path.name for path in (run / "raw").iterdir()} != expected_raw:
        raise ValueError("raw shot identity set differs from the manifest")
    total_seconds = Decimal(0)
    checks = []
    result_ids: set[int] = set()
    input_paths = [run / "cases.json", run / "submission.json", run / "results.json", run / "source-readback.json"]
    for case in manifest["circuits"]:
        row = jobs_by_file[case["file"]]
        job = row.get("job")
        results = row.get("results")
        job_id = submitted_by_file[case["file"]]
        if (
            not isinstance(job, dict)
            or type(job.get("id")) is not int
            or job.get("id") != job_id
            or type(job.get("batch_job_id")) is not int
            or job.get("batch_job_id") != submission["batch_job"]
            or job.get("status") != "completed"
            or type(job.get("number_of_shots")) is not int
            or job.get("number_of_shots") != 2048
            or job.get("raw_data_enabled") is not True
            or not isinstance(results, list)
            or len(results) != 1
        ):
            raise ValueError("collection job identity, status or shot count differs")
        source_readback = source_by_job[job_id]
        if provider_job_times(source_readback) != provider_job_times(job):
            raise ValueError("provider job chronology differs between collection and readback")
        if (
            type(job.get("file_id")) is not int
            or job["file_id"] <= 0
            or type(source_readback.get("file_id")) is not int
            or source_readback["file_id"] != job["file_id"]
            or type(source_readback.get("number_of_shots")) is not int
            or source_readback["number_of_shots"] != job["number_of_shots"]
            or source_readback.get("raw_data_enabled") is not True
            or source_readback.get("compile_stage") != "none"
            or source_readback.get("compile_properties") != {}
            or source_readback.get("stored_source_sha256") != case["sha256"]
        ):
            raise ValueError("source readback differs from the job file or approved source")
        result = results[0]
        if not isinstance(result, dict):
            raise ValueError("result identity record must be an object")
        validate_result_creation(result)
        result_id = result.get("id")
        if type(result_id) is not int or result_id <= 0 or result_id in result_ids:
            raise ValueError("result identity must be positive and unique")
        result_ids.add(result_id)
        raw_path = run / "raw" / f"{case['file']}.json"
        shots = json.loads(raw_path.read_bytes())
        check = screen_shots(shots, case["expected_output"])
        if (
            type(result.get("job_id")) is not int
            or result.get("job_id") != job_id
            or type(result.get("shots_requested")) is not int
            or result.get("shots_requested") != 2048
            or type(result.get("shots_done")) is not int
            or result.get("shots_done") != 2048
            or not isinstance(result.get("results"), dict)
            or any(type(count) is not int or count <= 0 for count in result["results"].values())
            or Counter(shots) != Counter(result["results"])
        ):
            raise ValueError("result identity, shot counts or histogram differ from raw shots")
        if "raw_data" in result or source_readback.get("provider_result_sha256") != result_digest(
            {**result, "raw_data": shots}
        ):
            raise ValueError("provider result readback differs from retained metadata or ordered shots")
        total_seconds += execution_seconds(result.get("execution_time_in_seconds"))
        checks.append({"file": case["file"], "job": job_id, **check})
        input_paths.append(raw_path)
    return {
        "schema": "qi-qx-destination-conformance-analysis-v1",
        "checks": checks,
        "terminal_screen_passed": all(check["passed"] for check in checks),
        "provider_conformance_admitted": False,
        "total_shots": sum(check["shots"] for check in checks),
        "execution_seconds_decimal": str(total_seconds),
        "inputs": {path.relative_to(run).as_posix(): digest(path) for path in input_paths},
        "producer_sha256": digest(Path(__file__)),
        "boundary": (
            "QX terminal-output and retained readback consistency only; local records alone do not establish "
            "provider authenticity, actual user approval, fresh admission, account-wide billing reconciliation, "
            "Tuna early-history reconstruction or physical behavior."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--manifest-out", type=Path)
    operation.add_argument("--manifest-check", type=Path)
    operation.add_argument("--collection", type=Path)
    operation.add_argument("--capture-readback", type=Path)
    operation.add_argument("--local-replay-check", action="store_true")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--analysis-out", type=Path)
    output.add_argument("--analysis-check", type=Path)
    output.add_argument("--readback-out", type=Path)
    arguments = parser.parse_args()
    if arguments.local_replay_check:
        if arguments.analysis_out or arguments.analysis_check or arguments.readback_out:
            parser.error("--local-replay-check does not accept output options")
        build_manifest()
        sys.path.insert(0, str(ROOT / "gororoba_quantum"))
        import qi_stack

        if qi_stack.live("QX local replay", "source-bound observation check"):
            print(
                qi_stack.run(
                    [
                        "-B",
                        "-W",
                        "error",
                        "scripts/qi_tuna_qx_local_replay.py",
                        "--check",
                        str(PROPOSAL / "local-replay.json"),
                    ]
                ).strip()
            )
        return
    if arguments.capture_readback:
        if not arguments.readback_out:
            parser.error("--capture-readback requires --readback-out")
        with arguments.readback_out.open("xb") as destination:
            incomplete = b'{"schema":"qi-qx-destination-readback-incomplete-v1"}\n'
            destination.write(incomplete)
            destination.flush()
            os.fsync(destination.fileno())
            report = capture_readback(arguments.capture_readback)
            content = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
            destination.seek(0)
            destination.truncate()
            destination.write(content)
            destination.flush()
            os.fsync(destination.fileno())
        print("QX stored-source and backend readback retained; provider execution was not submitted.")
        return
    if arguments.readback_out:
        parser.error("--readback-out requires --capture-readback")
    if arguments.collection:
        if not (arguments.analysis_out or arguments.analysis_check):
            parser.error("--collection requires --analysis-out or --analysis-check")
        report = analyze_collection(arguments.collection)
        content = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
        if arguments.analysis_check:
            if arguments.analysis_check.read_bytes() != content:
                raise SystemExit("QX destination analysis differs from exact collection replay")
        else:
            with arguments.analysis_out.open("xb") as destination:
                destination.write(content)
        if not report["terminal_screen_passed"]:
            raise SystemExit("QX terminal conformance failed; retained analysis must not admit hardware")
        print("QX terminal screen passed; provider conformance and hardware approval remain unadmitted.")
        return
    if arguments.analysis_out or arguments.analysis_check:
        parser.error("analysis output options require --collection")
    content = (json.dumps(build_manifest(), indent=2, sort_keys=True) + "\n").encode()
    if arguments.manifest_check:
        if arguments.manifest_check.read_bytes() != content:
            raise SystemExit("QX destination proposal differs from exact source-bound replay")
    else:
        with arguments.manifest_out.open("xb") as destination:
            destination.write(content)
    print("Reduced QX proposal binds three sources; provider execution remains unapproved.")


if __name__ == "__main__":
    main()
