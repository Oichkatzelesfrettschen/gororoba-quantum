"""Current Ascella request and analysis source bindings."""

from __future__ import annotations

import json
from pathlib import Path

import ascella_predecessor_case as original
import ascella_predecessor_current_analysis as analysis
import ascella_predecessor_current_case as current
import pytest
import qd_platform as qd


def test_current_case_admits_running_job_only_with_an_available_queue_slot() -> None:
    current_case = {"family": "ascella_predecessor", "job": current.JOB}
    counters = {"max_concurrent_jobs": 1, "max_jobs_in_queue": 1, "num_concurrent_jobs": 1, "num_jobs_in_queue": 0}
    qd.require_token_capacity(current_case, counters)
    with pytest.raises(qd.PlatformError, match="running or queued"):
        qd.require_token_capacity({"family": "ascella_predecessor", "job": original.JOB}, counters)
    with pytest.raises(qd.PlatformError, match="no available queue slot"):
        qd.require_token_capacity(current_case, {**counters, "num_jobs_in_queue": 1})
    with pytest.raises(qd.PlatformError, match="integer"):
        qd.require_token_capacity(current_case, {**counters, "max_jobs_in_queue": None})


def test_current_request_preserves_scientific_fields_and_binds_current_sources(tmp_path: Path) -> None:
    prior = original.documents()
    newer = current.documents()
    old = json.loads(prior["cases.json"])
    new = json.loads(newer["cases.json"])
    registered = new["preregistered"].pop("current_case_sources")
    old["job"] = current.JOB
    if new != old or newer["circuit.json"] != prior["circuit.json"]:
        raise AssertionError("the current request changed the target-slot experiment")
    manifest = json.loads(newer["cases.json"])
    sources = qd.acquisition_sources(manifest)
    if not set(registered).issubset(sources):
        raise AssertionError("review packet omits current producer sources")
    original.publish_case(tmp_path, newer)
    if current.check(tmp_path) != manifest:
        raise AssertionError("the current request does not reproduce")
    manifest["preregistered"]["current_case_sources"][current.ANALYZER] = "0" * 64
    with pytest.raises(qd.PlatformError, match="reviewed source changed"):
        qd.acquisition_sources(manifest)


def test_current_analysis_rejects_changed_case(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(current, "check", lambda _directory: {"job": current.JOB})
    (tmp_path / "cases.json").write_text("{}\n")
    with pytest.raises(ValueError, match="differs from the current case"):
        analysis.analyze(tmp_path, submission_sha256="0" * 64, results_sha256="0" * 64)


def test_current_analyzer_validates_serialized_result_end_to_end(tmp_path: Path) -> None:
    import copy

    import ascella_predecessor_analysis as prior
    import perceval as pcvl
    from perceval.serialization import OutputArchive, Serialization, deserialize, serialize

    request = tmp_path / "request"
    original.publish_case(request, current.documents())
    manifest = current.check(request)
    source = original.ROOT / original.MESH_RUNS["job-00"]
    source_results = json.loads((source / "results.json").read_bytes())
    body = json.loads((source / "job-body.json").read_bytes())
    computation = deserialize(body["payload"]["computation"])
    observed = []
    for setting in manifest["settings"]:
        previous = source_results["iterations"][setting["source_observation_index"]]
        params = {
            "circuit_params": setting["circuit_params"],
            "compilation_seed": setting["compilation_seed"],
            "max_samples": 32768,
            "max_shots": 32768,
        }
        counts = pcvl.BSCount({pcvl.BasicState("|1,0,0,0,0,0,0,0,0,0,0,0>"): 32768})
        fields = {**previous["result_fields"], "nb_shots_used": 32768}
        observed.append({**fields, "iteration": params, "results": serialize(counts)})
    computation.iterations[:] = [copy.deepcopy(row["iteration"]) for row in observed]
    archive = OutputArchive()
    Serialization.serialize(computation, archive)
    body["payload"].update(computation=archive.to_text(), max_samples=32768, max_shots=32768)
    body["max_duration"] = 300
    job_id = "offline-current-fixture"
    raw = {"job_id": job_id, "shots": 32768, "results": json.dumps({"results_list": observed})}
    raw_bytes = json.dumps(raw).encode()
    status = {"status": "completed", "duration": 40, "shots": 32768}
    submission = json.loads((source / "submission.json").read_bytes())
    submission.update(
        job_id=raw["job_id"],
        cases_sha256=prior.digest(request / "cases.json"),
        body_sha256=original.sha256_bytes(json.dumps(body, sort_keys=True).encode()),
        approval="synthetic offline fixture",
        submitted_utc="2026-10-28T00:00:00Z",
        credit_ceiling=original.charge(32768),
    )
    result = {
        "schema": qd.COLLECTION_SCHEMA,
        "job_id": raw["job_id"],
        "status": status,
        "data": {"payload": body["payload"]},
        "result_sha256": original.sha256_bytes(raw_bytes),
        **qd.result_summary(raw_bytes, job_id, status, True, 8),
    }
    run = tmp_path / "run"
    (run / "raw").mkdir(parents=True)
    (run / "raw/result.json").write_bytes(raw_bytes)
    for name in ("cases.json", "circuit.json"):
        (run / name).write_bytes((request / name).read_bytes())
    for name, value in (("job-body.json", body), ("submission.json", submission), ("results.json", result)):
        (run / name).write_text(json.dumps(value))
    submission_sha = prior.digest(run / "submission.json")
    results_sha = prior.digest(run / "results.json")
    report = analysis.analyze(run, submission_sha256=submission_sha, results_sha256=results_sha)
    if report["verdict"] != "descriptive-only" or report["physical_predecessor_attribution"] != "unavailable":
        raise AssertionError("analysis promoted a descriptive slot response")
    (run / "results.json").write_text("{}")
    with pytest.raises(ValueError, match="anchor"):
        analysis.analyze(run, submission_sha256=submission_sha, results_sha256=results_sha)
