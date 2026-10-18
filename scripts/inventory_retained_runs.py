"""Separate retained runner, mock, local and physical evidence and bind every job identity.

Every job id a runner record's submission names, and every job a retention.json
recovers, belongs to the retained service inventory
(results/live/qpu-job-inventory.json); the two sets are disjoint and together
equal it. Native mock reports declare a mock or dry-run boundary, and local
compute, native preparation and compile artifacts declare no QPU execution.
The printed counts describe retained evidence objects; they establish no
physical job beyond the service inventory.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path: Path) -> Any:
    payload = path.read_bytes()
    if path.suffix == ".gz":
        payload = gzip.decompress(payload)
    return json.loads(payload)


def descriptor(path: Path) -> dict[str, Any]:
    data = read(path)
    require(isinstance(data, dict), "Evidence descriptor requires a JSON object")
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": digest(path),
        "schema": data.get("schema", data.get("schema_version")),
        "retained_state": data.get("state", data.get("status", "unspecified")),
        "evidence_kind": data.get("evidence_kind", data.get("evidence_surface")),
        "declared_qpu_execution": data.get("qpu_execution", data.get("qpu_executed")),
    }


def record_descriptor(path: Path) -> dict[str, Any]:
    data = read(path)
    result = descriptor(path)
    submission = data.get("submission") or {}
    require(isinstance(submission, dict), "Submission metadata requires an object")
    jobs = submission.get("jobs", [])
    require(isinstance(jobs, list), "Submission job metadata requires a list")
    identities = [entry.get("job_id") for entry in jobs if entry.get("job_id")]
    result.update(
        {
            "submission_field_present": "submission" in data,
            "submission_complete": submission.get("complete"),
            "recorded_job_ids": identities,
            "local_batch_metadata_entries": {
                name: len(data[name])
                for name in ("local_simulation_batches", "evaluation_simulation_batches")
                if name in data
            },
            "qpy_present": (path.parent / "isa.qpy").is_file(),
            "collection_present": (path.parent / "collect.json").is_file(),
        }
    )
    return result


def inventory() -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "gororoba_quantum"))
    import parallel

    service_path = ROOT / "results/live/qpu-job-inventory.json"
    service = read(service_path)
    # Each further IBM Cloud instance observes into qpu-job-inventory.<instance_crn_hash>.json.
    additional_paths = sorted((ROOT / "results/live").glob("qpu-job-inventory.*.json"))
    snapshots = [service, *(read(path) for path in additional_paths)]
    physical_ids = {entry["job_id"] for snapshot in snapshots for entry in snapshot["jobs"]}
    require(
        len(physical_ids) == sum(len(snapshot["jobs"]) for snapshot in snapshots),
        "A physical job appears in two instance inventories",
    )
    record_paths = sorted((ROOT / "results/live").glob("*/record.json"))
    records = parallel.ordered_map(record_descriptor, record_paths, min_items=16)
    registered_ids = {identity for record in records for identity in record["recorded_job_ids"]}
    require(registered_ids <= physical_ids, "Runner records reference a job absent from the service observation")
    retrospective_paths = sorted((ROOT / "results/live").glob("*/retention.json"))
    retrospective = [descriptor(path) for path in retrospective_paths]
    retrospective_ids = {read(path)["job_id"] for path in retrospective_paths}
    require(registered_ids.isdisjoint(retrospective_ids), "Physical acquisition provenance is duplicated")
    require(registered_ids | retrospective_ids == physical_ids, "Physical service inventory lacks a retention channel")

    mock_paths = sorted((ROOT / "results/live").glob("*/native-dry-run/*/report.json"))
    mock_paths.extend(sorted((ROOT / "results/live").glob("*/native-validation.json")))
    mocks = []
    for path in mock_paths:
        data = read(path)
        require(
            data.get("evidence_kind") in {"server_mock_timing", "server_dry_run_randomized_mock_data"},
            "Native mock report evidence kind differs",
        )
        require(data.get("dry_run") is True or data.get("qpu_execution") is False, "Mock execution boundary missing")
        mocks.append(descriptor(path))
    diagnostics = [descriptor(path) for path in sorted((ROOT / "results/ripple").glob("*-mock-diagnosis.json"))]
    local_paths = sorted(
        set((ROOT / "results/local_compute").rglob("*.json")) | set((ROOT / "results/local_compute").rglob("*.json.gz"))
    )
    local = [descriptor(path) for path in local_paths]
    native_local = []
    for path in sorted((ROOT / "results/live").glob("*/native-preparation.json")):
        data = read(path)
        require(data.get("audit_contract") == "native-aer-n21-dry-run-v1", "Local preparation contract differs")
        require(
            data["artifact_checks"]["recorded_runtime_jobs"] == 0
            and data["artifact_checks"]["submission_field_present"] is False,
            "Local preparation carries a submission and needs separate reconciliation",
        )
        native_local.append(descriptor(path))
    compiled = [descriptor(path) for path in sorted((ROOT / "results/hw_estimate").glob("*.json"))]
    require(
        all(entry["declared_qpu_execution"] is not True for entry in local + compiled),
        "Local/compile evidence declares a physical execution and needs separate reconciliation",
    )
    states = Counter(str(entry["retained_state"]) for entry in records)
    return {
        "schema": "retained-run-channel-inventory-v1",
        "scope": "Repository runner records, named native mock reports, local-compute JSON archives and top-level "
        "compile/algebra/simulation JSON artifacts. Counts describe retained evidence objects; neither "
        "directory names nor planned/local/mock records establish additional physical QPU jobs.",
        "physical_service_observed_at": service["observed_at"],
        "physical_inventory_sha256": digest(service_path),
        **(
            {"additional_physical_inventory_sha256": {path.name: digest(path) for path in additional_paths}}
            if additional_paths
            else {}
        ),
        "replay_source_sha256": digest(Path(__file__)),
        "counts": {
            "runner_records": len(records),
            "runner_record_states": dict(sorted(states.items())),
            "physical_jobs": len(physical_ids),
            "registered_physical_jobs": len(registered_ids),
            "retrospective_physical_jobs": len(retrospective_ids),
            "native_mock_reports": len(mocks),
            "mock_diagnostics": len(diagnostics),
            "local_compute_json_artifacts": len(local),
            "native_local_preparation_reports": len(native_local),
            "compile_algebra_simulation_json_artifacts": len(compiled),
        },
        "runner_records": records,
        "retrospective_physical_retention": retrospective,
        "native_mock_reports": mocks,
        "mock_diagnostics": diagnostics,
        "local_compute_json_artifacts": local,
        "native_local_preparation_reports": native_local,
        "compile_algebra_simulation_json_artifacts": compiled,
        "interpretation": "States are retained artifact fields; a running checkpoint does not establish a live "
        "process. Legacy unspecified states and missing batch metadata remain unknown. Software tests and failed "
        f"native mocks inform implementation qualification. Measured physics comes from {len(physical_ids)} "
        "hash-bound physical-job archives.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="also write the full channel inventory as JSON, outside results/")
    arguments = parser.parse_args()
    try:
        data = inventory()
        if arguments.out is not None:
            destination = arguments.out.resolve()
            require(not destination.is_relative_to(ROOT / "results"), "the inventory stays outside results/")
            destination.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n")
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"retained run channels: {error}\n")
    print(json.dumps(data["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
