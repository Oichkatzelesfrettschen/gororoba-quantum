"""Reconstruct retained Quantum Inspire final-result responses and verify their observed object hashes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

from qi_tuna_destination_one_analysis import (
    ROOT,
    digest,
    json_bytes,
    timestamp,
    validate_execution_seconds,
    validate_positive_integer,
)

from parallel import ordered_map

RESPONSE_FIELDS = sorted(("id", "job_id", "created_on", "final_result"))
FINAL_FIELDS = sorted(("execution_time_in_seconds", "shots_requested", "shots_done", "results", "raw_data"))
CHECK_FIELDS = {
    "execution_seconds_match",
    "field_set",
    "histogram_matches",
    "job_identity",
    "ordered_raw_matches",
    "shot_counts_match",
}


def object_digest(value: Any) -> str:
    """Match the original read-only probe's compact sorted-key JSON digest."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def relative_path(root: Path, name: Any) -> Path:
    if (
        not isinstance(name, str)
        or not name
        or not PurePosixPath(name).parts
        or "\\" in name
        or PurePosixPath(name).is_absolute()
        or any(part in (".", "..") for part in PurePosixPath(name).parts)
        or PurePosixPath(name).as_posix() != name
    ):
        raise ValueError("evidence paths must be normalized repository-relative POSIX paths")
    path = root / name
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("evidence path escapes the repository")
    return path


def require_hash(value: Any) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("an observed object or evidence digest is malformed")
    return value


def bound_record(root: Path, name: Any, expected: Any) -> tuple[Path, dict[str, Any]]:
    path = relative_path(root, name)
    if digest(path) != require_hash(expected):
        raise ValueError("linked evidence bytes differ from the projection binding")
    record = json.loads(path.read_bytes())
    if not isinstance(record, dict):
        raise ValueError("linked evidence must be a JSON object")
    return path, record


def index_jobs(rows: Any, label: str) -> dict[int, dict[str, Any]]:
    if not isinstance(rows, list) or len(rows) != 6 or any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"{label} must contain six job objects")
    index = {}
    for row in rows:
        job = validate_positive_integer(row.get("job"), f"{label} job")
        if job in index:
            raise ValueError(f"{label} repeats a job identity")
        index[job] = row
    return index


def validate_response(
    task: tuple[Path, dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]],
) -> dict[str, Any]:
    root, projection, observed, request, equivalence = task
    job_id = validate_positive_integer(projection["job"], "projection job")
    case_name = projection["case"]
    case = relative_path(root, case_name)
    expected_path = f"/final_results/job/{job_id}"
    if projection["path"] != expected_path or observed["case"] != case_name or request["path"] != expected_path:
        raise ValueError("case or final-result route differs from the original observation")
    if (
        projection["response_fields"] != RESPONSE_FIELDS
        or projection["final_result_fields"] != FINAL_FIELDS
        or request.get("returned_fields") != RESPONSE_FIELDS
        or request.get("final_result_fields") != FINAL_FIELDS
        or request.get("status") != "returned"
        or request.get("returned_type") != "object"
        or type(request.get("redacted_fields")) is not int
        or request["redacted_fields"] != 0
        or request.get("parameters") != {}
        or validate_positive_integer(request.get("raw_shots_returned"), "observed raw shots") != 4096
    ):
        raise ValueError("observed response and final-result field contracts differ")
    metadata = projection["response_metadata"]
    if not isinstance(metadata, dict) or set(metadata) != {"id", "job_id", "created_on"}:
        raise ValueError("response metadata must contain exactly id, job_id and created_on")
    validate_positive_integer(metadata["id"], "final-result response ID")
    if validate_positive_integer(metadata["job_id"], "final-result response job") != job_id:
        raise ValueError("response metadata names a different job")
    timestamp(metadata["created_on"])
    manifest_path = case / "cases.json"
    submission_path = case / "submission.json"
    results_path = case / "results.json"
    manifest = json.loads(manifest_path.read_bytes())
    submission = json.loads(submission_path.read_bytes())
    collection = json.loads(results_path.read_bytes())
    if (
        validate_positive_integer(manifest["shots"], "manifest shots") != 4096
        or validate_positive_integer(manifest["backend_type_id"], "manifest backend") != 7
        or len(manifest["circuits"]) != 1
        or submission.get("schema") != "qi-submission-v2"
        or submission.get("state") != "enqueued"
        or submission.get("backend") != "tuna_17"
        or validate_positive_integer(submission["backend_type_id"], "submission backend") != 7
        or validate_positive_integer(submission["shots"], "submission shots") != 4096
        or submission["cases_sha256"] != digest(manifest_path)
        or len(submission["jobs"]) != 1
        or collection.get("schema") != "qi-collection-v1"
        or len(collection["jobs"]) != 1
    ):
        raise ValueError("retained submission or collection scope differs from the single completed Tuna job")
    source = manifest["circuits"][0]
    filename = source["file"]
    if not isinstance(filename, str) or PurePosixPath(filename).name != filename or "\\" in filename:
        raise ValueError("retained circuit file must be a basename")
    source_path = relative_path(root, f"{case_name}/{filename}")
    if digest(source_path) != require_hash(source["sha256"]):
        raise ValueError("retained circuit bytes differ from the manifest")
    submitted = submission["jobs"][0]
    collected = collection["jobs"][0]
    job = collected["job"]
    if (
        submitted["file"] != filename
        or submitted["sha256"] != source["sha256"]
        or collected["file"] != filename
        or validate_positive_integer(submitted["job"], "submitted job") != job_id
        or validate_positive_integer(job["id"], "collected job") != job_id
        or validate_positive_integer(job["batch_job_id"], "collected batch")
        != validate_positive_integer(submission["batch_job"], "submitted batch")
        or job["status"] != "completed"
        or job["raw_data_enabled"] is not True
        or validate_positive_integer(job["number_of_shots"], "job shots") != 4096
        or len(collected["results"]) != 1
    ):
        raise ValueError("retained completed job identities or raw-data contract differ")
    observed_job = observed["job_fields"]
    for field in ("id", "batch_job_id", "status", "number_of_shots", "raw_data_enabled"):
        if object_digest(observed_job[field]) != object_digest(job[field]):
            raise ValueError("retained job metadata differs from the original API observation")
    result = collected["results"][0]
    if (
        validate_positive_integer(result["job_id"], "retained result job") != job_id
        or validate_positive_integer(result["shots_requested"], "retained requested shots") != 4096
        or validate_positive_integer(result["shots_done"], "retained completed shots") != 4096
    ):
        raise ValueError("retained result job or complete shot counts differ")
    execution = validate_execution_seconds(result["execution_time_in_seconds"])
    raw_name = f"{case_name}/raw/{filename}.json"
    raw_path = relative_path(root, raw_name)
    shots = json.loads(raw_path.read_bytes())
    histogram = result["results"]
    if (
        not isinstance(shots, list)
        or len(shots) != 4096
        or any(type(shot) is not str or len(shot) != 20 or set(shot) - {"0", "1"} for shot in shots)
        or not isinstance(histogram, dict)
        or any(type(count) is not int or count <= 0 for count in histogram.values())
        or dict(Counter(shots)) != histogram
    ):
        raise ValueError("retained raw ordering, width, shot count or histogram contract failed")
    payload = {field: result[field] for field in FINAL_FIELDS if field != "raw_data"}
    payload["raw_data"] = shots
    response = dict(metadata) | {"final_result": payload}
    reconstructed = object_digest(response)
    if reconstructed != require_hash(projection["object_sha256"]) or reconstructed != require_hash(
        request["object_sha256"]
    ):
        raise ValueError("reconstructed full response differs from the projection or original observed API hash")
    derived_checks = {
        "execution_seconds_match": validate_execution_seconds(payload["execution_time_in_seconds"]) == execution,
        "field_set": sorted(payload) == FINAL_FIELDS and sorted(response) == RESPONSE_FIELDS,
        "histogram_matches": payload["results"] == dict(Counter(shots)),
        "job_identity": type(response["job_id"]) is int and response["job_id"] == job_id,
        "ordered_raw_matches": object_digest(payload["raw_data"]) == object_digest(shots),
        "shot_counts_match": type(payload["shots_requested"]) is int
        and type(payload["shots_done"]) is int
        and payload["shots_requested"] == payload["shots_done"] == len(shots) == 4096,
    }
    if (
        equivalence.get("final_result_fields") != FINAL_FIELDS
        or equivalence.get("raw_file") != raw_name
        or digest(raw_path) != require_hash(equivalence.get("raw_file_sha256"))
        or not isinstance(equivalence.get("checks"), dict)
        or set(equivalence["checks"]) != CHECK_FIELDS
        or any(equivalence["checks"][field] is not value for field, value in derived_checks.items())
        or not all(derived_checks.values())
    ):
        raise ValueError("equivalence claims differ from the reconstructed observed response and retained raw bytes")
    return {
        "case": case_name,
        "job": job_id,
        "path": expected_path,
        "response_id": metadata["id"],
        "response_created_on": metadata["created_on"],
        "reconstructed_object_sha256": reconstructed,
        "original_observed_object_sha256": request["object_sha256"],
        "projection_object_sha256": projection["object_sha256"],
        "checks": derived_checks,
        "shots": len(shots),
        "width": 20,
        "execution_seconds_decimal": str(execution),
        "inputs": {
            path.relative_to(root).as_posix(): digest(path)
            for path in (manifest_path, source_path, submission_path, results_path, raw_path)
        },
    }


def receipt(projections: Path, root: Path | None = None) -> dict[str, Any]:
    root = ROOT if root is None else root
    projections_name = projections.resolve().relative_to(root.resolve()).as_posix()
    projections = relative_path(root, projections_name)
    projection = json.loads(projections.read_bytes())
    if not isinstance(projection, dict) or projection.get("schema") != "qi-final-result-projections-v1":
        raise ValueError("final-result projection schema differs")
    timestamp(projection["captured_utc"])
    observations_path, observations = bound_record(
        root, projection["observations_file"], projection["observations_sha256"]
    )
    equivalence_path, equivalence = bound_record(root, projection["equivalence_file"], projection["equivalence_sha256"])
    if (
        observations.get("schema") != "qi-destination-job-artifact-readback-v1"
        or equivalence.get("schema") != "qi-final-result-retention-equivalence-v1"
    ):
        raise ValueError("original API observation or equivalence schema differs")
    projected_jobs = index_jobs(projection["responses"], "response projections")
    observed_jobs = index_jobs(observations["jobs"], "original API observations")
    equivalence_jobs = index_jobs(equivalence["jobs"], "retained equivalence")
    if projected_jobs.keys() != observed_jobs.keys() or projected_jobs.keys() != equivalence_jobs.keys():
        raise ValueError("projection, original observation and equivalence job sets differ")
    cases = [row["case"] for row in projected_jobs.values()]
    if any(not isinstance(name, str) for name in cases) or len(set(cases)) != 6:
        raise ValueError("projections require six distinct retained cases")
    observed_cases = [row["case"] for row in observed_jobs.values()]
    if len(set(observed_cases)) != 6 or set(cases) != set(observed_cases):
        raise ValueError("projection and original observation case sets differ")
    requests = observations["requests"]
    if not isinstance(requests, list) or any(
        not isinstance(row, dict) or not isinstance(row.get("path"), str) for row in requests
    ):
        raise ValueError("original API requests require objects with route strings")
    final_requests = [row for row in requests if row["path"].startswith("/final_results/job/")]
    expected_paths = {f"/final_results/job/{job}" for job in projected_jobs}
    if len(final_requests) != 6 or {row["path"] for row in final_requests} != expected_paths:
        raise ValueError("original observation must contain exactly one final-result response per job")
    request_index = {row["path"]: row for row in final_requests}
    rows = ordered_map(
        validate_response,
        [
            (root, row, observed_jobs[job], request_index[f"/final_results/job/{job}"], equivalence_jobs[job])
            for job, row in projected_jobs.items()
        ],
    )
    inputs = {
        path.relative_to(root).as_posix(): digest(path) for path in (projections, observations_path, equivalence_path)
    }
    for row in rows:
        inputs.update(row["inputs"])
    return {
        "schema": "qi-final-result-retention-checked-receipt-v1",
        "jobs": rows,
        "inputs": inputs,
        "response_fields": RESPONSE_FIELDS,
        "final_result_fields": FINAL_FIELDS,
        "all_six_observed_response_hashes_match": all(
            row["reconstructed_object_sha256"] == row["original_observed_object_sha256"] for row in rows
        ),
        "boundary": (
            "Offline reconstruction binds six observed response objects to retained binary shots and result fields. "
            "The comparison retains the API capture's trust boundary and leaves analog acquisition data and physical "
            "causality unresolved."
        ),
        "producer_sha256": digest(Path(__file__)),
        "validator_sources": {
            name: digest(Path(__file__).resolve().parents[1] / name)
            for name in ("scripts/qi_tuna_destination_one_analysis.py", "gororoba_quantum/parallel.py")
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("projections", type=Path)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--out", type=Path)
    operation.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    content = json_bytes(receipt(arguments.projections))
    if arguments.check:
        if arguments.check.read_bytes() != content:
            raise SystemExit("retained final-result receipt differs from exact offline replay")
    else:
        with arguments.out.open("xb") as output:
            output.write(content)
    print("Six final-result responses reconstruct exactly against their original observed API object hashes.")


if __name__ == "__main__":
    main()
