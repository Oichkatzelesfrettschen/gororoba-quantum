"""Observed API hashes turn final-result equivalence flags into independently checked retention evidence."""

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import pytest
import qi_tuna_final_result_receipt as verifier


def save(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def api_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def refresh_projection_links(root: Path, projection_path: Path) -> None:
    projection = json.loads(projection_path.read_text())
    for stem in ("observations", "equivalence"):
        projection[f"{stem}_sha256"] = verifier.digest(root / projection[f"{stem}_file"])
    save(projection_path, projection)


@pytest.fixture
def retained(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    monkeypatch.setenv("GOROROBA_WORKERS", "1")
    root = tmp_path / "repository"
    projection_path = root / "docs/evidence/final-result-projections.json"
    observed_jobs, requests, equivalent_jobs, responses = [], [], [], []
    for index in range(6):
        job_id = 100 + index
        case_name = f"results/quantum_inspire/runs/synthetic-case-{index}"
        case = root / case_name
        source = "version 3.0\nqubit[17] q\nbit[20] b\ninit q\n"
        source_hash = hashlib.sha256(source.encode()).hexdigest()
        save(
            case / "cases.json",
            {"shots": 4096, "backend_type_id": 7, "circuits": [{"file": "control.cq", "sha256": source_hash}]},
        )
        (case / "control.cq").write_text(source)
        save(
            case / "submission.json",
            {
                "schema": "qi-submission-v2",
                "state": "enqueued",
                "backend": "tuna_17",
                "backend_type_id": 7,
                "shots": 4096,
                "cases_sha256": verifier.digest(case / "cases.json"),
                "batch_job": 200 + index,
                "jobs": [{"file": "control.cq", "job": job_id, "sha256": source_hash}],
            },
        )
        shots = ["0" * 20, "1" * 20] * 2048
        raw_path = case / "raw/control.cq.json"
        save(raw_path, shots)
        job = {
            "id": job_id,
            "batch_job_id": 200 + index,
            "status": "completed",
            "raw_data_enabled": True,
            "number_of_shots": 4096,
        }
        result = {
            "id": 2000 + index,
            "created_on": "2026-10-27T19:00:00Z",
            "job_id": job_id,
            "execution_time_in_seconds": 5.0,
            "shots_requested": 4096,
            "shots_done": 4096,
            "results": dict(Counter(shots)),
        }
        save(
            case / "results.json",
            {"schema": "qi-collection-v1", "jobs": [{"file": "control.cq", "job": job, "results": [result]}]},
        )
        metadata = {"id": 1000 + index, "job_id": job_id, "created_on": "2026-10-27T19:00:01.500000Z"}
        payload = {key: result[key] for key in verifier.FINAL_FIELDS if key != "raw_data"} | {"raw_data": shots}
        response_hash = api_hash(metadata | {"final_result": payload})
        path = f"/final_results/job/{job_id}"
        observed_jobs.append({"case": case_name, "job": job_id, "job_fields": job})
        requests.append(
            {
                "path": path,
                "parameters": {},
                "status": "returned",
                "returned_type": "object",
                "returned_fields": verifier.RESPONSE_FIELDS,
                "final_result_fields": verifier.FINAL_FIELDS,
                "raw_shots_returned": 4096,
                "redacted_fields": 0,
                "object_sha256": response_hash,
            }
        )
        equivalent_jobs.append(
            {
                "job": job_id,
                "raw_file": raw_path.relative_to(root).as_posix(),
                "raw_file_sha256": verifier.digest(raw_path),
                "final_result_fields": verifier.FINAL_FIELDS,
                "checks": {name: True for name in verifier.CHECK_FIELDS},
            }
        )
        responses.append(
            {
                "case": case_name,
                "job": job_id,
                "path": path,
                "object_sha256": response_hash,
                "response_fields": verifier.RESPONSE_FIELDS,
                "response_metadata": metadata,
                "final_result_fields": verifier.FINAL_FIELDS,
            }
        )
    observations = root / "docs/evidence/observations.json"
    equivalence = root / "docs/evidence/equivalence.json"
    save(
        observations, {"schema": "qi-destination-job-artifact-readback-v1", "jobs": observed_jobs, "requests": requests}
    )
    save(equivalence, {"schema": "qi-final-result-retention-equivalence-v1", "jobs": equivalent_jobs})
    save(
        projection_path,
        {
            "schema": "qi-final-result-projections-v1",
            "captured_utc": "2026-10-27T20:00:00+00:00",
            "observations_file": observations.relative_to(root).as_posix(),
            "observations_sha256": verifier.digest(observations),
            "equivalence_file": equivalence.relative_to(root).as_posix(),
            "equivalence_sha256": verifier.digest(equivalence),
            "responses": responses,
        },
    )
    return root, projection_path


def observations(root: Path) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): verifier.digest(path) for path in root.rglob("*") if path.is_file()}


def test_six_lossless_responses_replay_and_preserve(retained: tuple[Path, Path]) -> None:
    root, projection = retained
    before = observations(root)
    report = verifier.receipt(projection, root)
    if report != verifier.receipt(projection, root) or len(report["jobs"]) != 6 or len(report["inputs"]) != 33:
        raise AssertionError("six-job receipt must replay deterministically with complete file bindings")
    if report["all_six_observed_response_hashes_match"] is not True:
        raise AssertionError("every reconstructed response must match its original API hash")
    if any(not all(row["checks"].values()) for row in report["jobs"]):
        raise AssertionError("all equivalence flags require derived passing checks")
    if report["jobs"][0]["response_id"] != 1000:
        raise AssertionError("final-result response ID must retain its distinct metadata identity")
    if observations(root) != before:
        raise AssertionError("offline response validation changed retained files")


@pytest.mark.parametrize(
    "defect",
    [
        "schema",
        "metadata-id",
        "metadata-job",
        "metadata-time",
        "metadata-extra",
        "hash",
        "route",
        "response-fields",
        "payload-fields",
        "duplicate-job",
        "duplicate-case",
    ],
)
def test_projection_mutations_refuse(retained: tuple[Path, Path], defect: str) -> None:
    root, path = retained
    projection = json.loads(path.read_text())
    row = projection["responses"][0]
    if defect == "schema":
        projection["schema"] = "unknown"
    elif defect == "metadata-id":
        row["response_metadata"]["id"] = False
    elif defect == "metadata-job":
        row["response_metadata"]["job_id"] += 1
    elif defect == "metadata-time":
        row["response_metadata"]["created_on"] = "2026-10-27T19:00:00"
    elif defect == "metadata-extra":
        row["response_metadata"]["extra"] = "unobserved"
    elif defect == "hash":
        row["object_sha256"] = "0" * 64
    elif defect == "route":
        row["path"] = "/final_results/job/999"
    elif defect == "response-fields":
        row["response_fields"] = ["id", "job_id", "final_result"]
    elif defect == "payload-fields":
        row["final_result_fields"] = sorted(verifier.FINAL_FIELDS + ["iq"])
    elif defect == "duplicate-job":
        projection["responses"][1]["job"] = row["job"]
    else:
        projection["responses"][1]["case"] = row["case"]
    save(path, projection)
    with pytest.raises(ValueError):
        verifier.receipt(path, root)


@pytest.mark.parametrize("defect", ["hash", "fields", "count", "duplicate-route", "wrong-job-set", "job-metadata"])
def test_original_observation_constraints_refuse_after_rebinding(retained: tuple[Path, Path], defect: str) -> None:
    root, projection_path = retained
    projection = json.loads(projection_path.read_text())
    path = root / projection["observations_file"]
    value = json.loads(path.read_text())
    if defect == "hash":
        value["requests"][0]["object_sha256"] = "0" * 64
    elif defect == "fields":
        value["requests"][0]["returned_fields"] = ["id", "final_result"]
    elif defect == "count":
        value["requests"][0]["raw_shots_returned"] = 4095
    elif defect == "duplicate-route":
        value["requests"].append(value["requests"][0])
    elif defect == "wrong-job-set":
        value["jobs"][0]["job"] += 1000
    else:
        value["jobs"][0]["job_fields"]["batch_job_id"] += 1
    save(path, value)
    refresh_projection_links(root, projection_path)
    with pytest.raises(ValueError):
        verifier.receipt(projection_path, root)


@pytest.mark.parametrize("defect", ["false-check", "numeric-check", "wrong-raw-hash", "wrong-raw-file", "wrong-fields"])
def test_equivalence_flags_are_recomputed(retained: tuple[Path, Path], defect: str) -> None:
    root, projection_path = retained
    projection = json.loads(projection_path.read_text())
    path = root / projection["equivalence_file"]
    value = json.loads(path.read_text())
    row = value["jobs"][0]
    if defect == "false-check":
        row["checks"]["ordered_raw_matches"] = False
    elif defect == "numeric-check":
        row["checks"]["ordered_raw_matches"] = 1
    elif defect == "wrong-raw-hash":
        row["raw_file_sha256"] = "0" * 64
    elif defect == "wrong-raw-file":
        row["raw_file"] = "../outside.json"
    else:
        row["final_result_fields"] = []
    save(path, value)
    refresh_projection_links(root, projection_path)
    with pytest.raises(ValueError, match="equivalence claims differ"):
        verifier.receipt(projection_path, root)


@pytest.mark.parametrize("value", ["5", True, None, float("nan"), float("inf"), -1, 301])
def test_execution_numbers_are_strict(retained: tuple[Path, Path], value: Any) -> None:
    root, projection_path = retained
    projection = json.loads(projection_path.read_text())
    path = root / projection["responses"][0]["case"] / "results.json"
    result = json.loads(path.read_text())
    result["jobs"][0]["results"][0]["execution_time_in_seconds"] = value
    save(path, result)
    with pytest.raises(ValueError):
        verifier.receipt(projection_path, root)


@pytest.mark.parametrize(
    "defect",
    [
        "integer-representation",
        "float-shots",
        "float-histogram",
        "wrong-job",
        "failed-status",
        "partial-count",
        "raw-width",
    ],
)
def test_retained_result_representation_and_identity_refuse(retained: tuple[Path, Path], defect: str) -> None:
    root, projection_path = retained
    projection = json.loads(projection_path.read_text())
    case = root / projection["responses"][0]["case"]
    path = case / "results.json"
    collection = json.loads(path.read_text())
    result = collection["jobs"][0]["results"][0]
    if defect == "integer-representation":
        result["execution_time_in_seconds"] = 5
    elif defect == "float-shots":
        result["shots_requested"] = 4096.0
    elif defect == "float-histogram":
        result["results"]["0" * 20] = 2048.0
    elif defect == "wrong-job":
        result["job_id"] += 1
    elif defect == "failed-status":
        collection["jobs"][0]["job"]["status"] = "failed"
    elif defect == "partial-count":
        result["shots_done"] = 4095
    else:
        save(case / "raw/control.cq.json", ["0" * 19] * 4096)
        result["results"] = {"0" * 19: 4096}
    save(path, collection)
    with pytest.raises(ValueError):
        verifier.receipt(projection_path, root)


def test_raw_order_mutation_refuses_despite_coherent_local_hash_updates(retained: tuple[Path, Path]) -> None:
    root, projection_path = retained
    projection = json.loads(projection_path.read_text())
    row = projection["responses"][0]
    case = root / row["case"]
    raw_path = case / "raw/control.cq.json"
    shots = json.loads(raw_path.read_text())
    save(raw_path, list(reversed(shots)))
    equivalence_path = root / projection["equivalence_file"]
    equivalence = json.loads(equivalence_path.read_text())
    equivalence["jobs"][0]["raw_file_sha256"] = verifier.digest(raw_path)
    save(equivalence_path, equivalence)
    metadata = row["response_metadata"]
    result = json.loads((case / "results.json").read_text())["jobs"][0]["results"][0]
    payload = {key: result[key] for key in verifier.FINAL_FIELDS if key != "raw_data"} | {
        "raw_data": list(reversed(shots))
    }
    row["object_sha256"] = api_hash(metadata | {"final_result": payload})
    save(projection_path, projection)
    refresh_projection_links(root, projection_path)
    before = observations(root)
    with pytest.raises(ValueError, match="original observed API hash"):
        verifier.receipt(projection_path, root)
    if observations(root) != before:
        raise AssertionError("hash-chain refusal changed retained evidence")


@pytest.mark.parametrize(
    "name", ["../outside.json", "/tmp/outside.json", "docs/../outside.json", "docs//outside.json", "docs\\outside.json"]
)
def test_invalid_repository_paths_refuse(retained: tuple[Path, Path], name: str) -> None:
    root, projection_path = retained
    value = json.loads(projection_path.read_text())
    value["observations_file"] = name
    save(projection_path, value)
    with pytest.raises(ValueError, match="repository-relative"):
        verifier.receipt(projection_path, root)


def test_symlink_escape_refuses(retained: tuple[Path, Path], tmp_path: Path) -> None:
    root, projection_path = retained
    outside = tmp_path / "outside.json"
    outside.write_text("{}")
    (root / "escape.json").symlink_to(outside)
    value = json.loads(projection_path.read_text())
    value["observations_file"] = "escape.json"
    save(projection_path, value)
    with pytest.raises(ValueError, match="escapes"):
        verifier.receipt(projection_path, root)


def test_cli_exclusive_output_and_exact_check(
    retained: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, projection_path = retained
    monkeypatch.setattr(verifier, "ROOT", root)
    output = tmp_path / "checked-response-receipt.json"
    arguments = ["final-result-receipt", str(projection_path)]
    before = observations(root)
    monkeypatch.setattr(sys, "argv", [*arguments, "--out", str(output)])
    verifier.main()
    original = output.read_bytes()
    with pytest.raises(FileExistsError):
        verifier.main()
    if output.read_bytes() != original:
        raise AssertionError("exclusive receipt output replaced existing bytes")
    monkeypatch.setattr(sys, "argv", [*arguments, "--check", str(output)])
    verifier.main()
    output.write_bytes(original + b"\n")
    with pytest.raises(SystemExit, match="differs from exact offline replay"):
        verifier.main()
    if observations(root) != before:
        raise AssertionError("receipt publication or verification changed evidence files")
