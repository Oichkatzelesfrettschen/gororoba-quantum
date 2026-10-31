"""Qualify archived workloads through Runtime's server-side mock execution.

Runtime 0.50's client-side Sampler.run(dry_run=True) validates and schedules
against a mock backend. Randomized measurement data has no scientific meaning;
the adapter reads metadata only and stores it outside hardware result paths.
https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/executor-sampler-sampler
https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/runtime-job-v2
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any
from uuid import uuid4

from qiskit import qpy

import run_archive


class PreflightError(ValueError):
    """The retained workload or native metadata failed qualification."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PreflightError(message)


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_digest(value: Any) -> str:
    return _digest(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())


def _preserved_files(run_dir: Path) -> dict[str, str | None]:
    files = {
        name: _digest((run_dir / name).read_bytes()) if (run_dir / name).is_file() else None
        for name in ("record.json", "approval-consumed.json")
    }
    files["isa.qpy"] = _digest(run_archive.read_archive(run_dir)) if run_archive.has_archive(run_dir) else None
    return files


def _binding(runtime: Any, service: Any, choices: list[Any], record: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    _require(record.get("state") == "planned", "native qualification requires a planned record")
    _require(record.get("budget_plan", {}).get("admitted") is True, "native qualification requires admitted budget")
    _require(bool(choices), "native qualification requires executable choices")
    retained = json.loads((run_dir / "record.json").read_text())
    serialized_record = json.loads(json.dumps(record, default=str))
    _require(retained == serialized_record, "record argument differs from retained record.json")
    _require(record["experiment_digest"] == runtime.experiment_digest(), "experiment source digest changed")
    _require(record["instance_sha256_12"] == runtime._instance_hash(service), "service instance changed")
    for choice in choices:
        _require(
            record["backends"][choice.snap.name]["calibration"] == choice.snap.calibration,
            f"{choice.snap.name}: calibration differs from retained record",
        )
    for package, expected in record["versions"].items():
        _require(version(package) == expected, f"dependency version changed: {package}")
    shots = record["shots"]
    _require(isinstance(shots, int) and not isinstance(shots, bool) and shots > 0, "shots must be positive integers")
    pubs = runtime.execution_pubs(choices)
    _require([pub.manifest() for pub in pubs] == record["execution_pubs"], "execution PUB manifest changed")
    named_circuits = []
    for pub in pubs:
        circuit = copy.copy(pub.circuit)
        circuit.name = pub.name
        named_circuits.append(circuit)
    archive_bytes = run_archive.read_archive(run_dir)
    _require(
        runtime._qpy_digest(named_circuits) == _digest(archive_bytes), "QPY archive differs from execution choices"
    )
    _require(
        runtime.qpu_planning.execution_contract(choices, record) == record["execution_contract"],
        "execution contract changed",
    )
    return {
        "files": _preserved_files(run_dir),
        "experiment_digest": record["experiment_digest"],
        "preflight_source_sha256": _digest(Path(__file__).read_bytes()),
        "instance_sha256_12": record["instance_sha256_12"],
        "versions": copy.deepcopy(record["versions"]),
        "shots": shots,
        "execution_contract_sha256": _json_digest(record["execution_contract"]),
        "execution_pubs_sha256": _json_digest(record["execution_pubs"]),
    }


def _positive_seconds(value: Any, label: str) -> float:
    _require(
        isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0,
        f"{label} must be a finite positive number",
    )
    return float(value)


def _timing(pub_result: Any, dt: float, name: str) -> dict[str, Any]:
    metadata = pub_result.metadata
    compilation = metadata.get("compilation") if isinstance(metadata, dict) else None
    timing = compilation.get("scheduler_timing") if isinstance(compilation, dict) else None
    if not isinstance(timing, dict):
        raise PreflightError(f"{name}: scheduler timing unavailable")
    duration = timing.get("circuit_duration")
    if not (
        isinstance(duration, (int, float))
        and not isinstance(duration, bool)
        and math.isfinite(duration)
        and duration >= 0
        and duration == int(duration)
    ):
        raise PreflightError(f"{name}: scheduler circuit_duration must be a nonnegative integer count of dt")
    timing_csv = timing.get("timing")
    if not isinstance(timing_csv, str) or not timing_csv.strip():
        raise PreflightError(f"{name}: scheduler timing CSV unavailable")
    return {
        "name": name,
        "circuit_duration_dt": int(duration),
        "backend_dt_seconds": dt,
        "circuit_duration_seconds": int(duration) * dt,
        "timing_csv": timing_csv,
        "timing_csv_sha256": _digest(timing_csv.encode()),
    }


def _check_preservation(runtime: Any, run_dir: Path, binding: dict[str, Any]) -> None:
    _require(_preserved_files(run_dir) == binding["files"], "retained record, QPY, or approval marker changed")
    _require(runtime.experiment_digest() == binding["experiment_digest"], "experiment source digest changed")
    _require(_digest(Path(__file__).read_bytes()) == binding["preflight_source_sha256"], "preflight source changed")


def _options_without_tags(options: dict[str, Any]) -> dict[str, Any]:
    copied = copy.deepcopy(options)
    copied.get("environment", {}).pop("job_tags", None)
    return copied


def _estimate_budget(record: dict[str, Any], jobs: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare server estimates with the retained per-job and invocation limits."""
    for job in jobs:
        ceiling = _positive_seconds(job["options"].get("max_execution_time"), "job execution ceiling")
        job["execution_ceiling_seconds"] = ceiling
        job["within_execution_ceiling"] = job["estimated_quantum_seconds"] <= ceiling
    estimated_total = sum(job["estimated_quantum_seconds"] for job in jobs)
    budget = record["budget_plan"]
    combined_ceiling = _positive_seconds(budget.get("combined_ceiling_seconds"), "combined execution ceiling")
    invocation_cap = _positive_seconds(budget.get("max_total_execution_seconds"), "invocation execution cap")
    return {
        "estimated_quantum_seconds": estimated_total,
        "combined_execution_ceiling_seconds": combined_ceiling,
        "invocation_execution_cap_seconds": invocation_cap,
        "per_job_estimates_within_ceilings": all(job["within_execution_ceiling"] for job in jobs),
        "estimated_total_within_combined_ceiling": estimated_total <= combined_ceiling,
        "estimated_total_within_invocation_cap": estimated_total <= invocation_cap,
        "combined_ceiling_matches_job_options": combined_ceiling
        == sum(job["execution_ceiling_seconds"] for job in jobs),
        "combined_ceiling_within_invocation_cap": combined_ceiling <= invocation_cap,
    }


def qualify(runtime: Any, service: Any, choices: list[Any], record: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    """Retain a distinct mock-only report; preserve record.json and isa.qpy.

    Every primitive invocation explicitly binds dry_run=True. The runtime module
    supplies production policy, grouping, and calibration guards; tests inject
    recording primitives and services. Remote acceptance is checkpointed before
    any result wait. An unavailable mock service leaves an unqualified report.
    """
    run_dir = Path(run_dir)
    identifier = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ") + "-" + uuid4().hex[:8]
    directory = run_dir / "native-dry-run" / identifier
    directory.mkdir(parents=True, exist_ok=False)
    report: dict[str, Any] = {
        "schema_version": 1,
        "evidence_kind": "server_mock_timing",
        "status": "preparing",
        "qualified": False,
        "timing_qualified": False,
        "within_execution_ceilings": False,
        "report_path": str(directory.relative_to(run_dir) / "report.json"),
        "dry_run": True,
        "measurement_data": "randomized mock data omitted; excluded from scientific analysis and visuals",
        "estimate_semantics": "server system-time estimate, distinct from executed QPU usage and final billing",
        "component_accounting": "initialization, repetition delay, circuit time, and overhead remain unseparated",
        "jobs": [],
        "reasons": [],
    }

    def checkpoint() -> None:
        safe = runtime._scrub_instances(runtime._jsonable(report))
        runtime._replace_atomically(
            directory / "report.json",
            lambda handle: handle.write(json.dumps(safe, indent=2, sort_keys=True, allow_nan=False) + "\n"),
            "w",
        )

    checkpoint()
    accepted: list[tuple[Any, dict[str, Any]]] = []
    binding: dict[str, Any] | None = None
    try:
        binding = _binding(runtime, service, choices, record, run_dir)
        report["binding"] = binding
        policy = record["policy"]
        args = argparse.Namespace(
            started=record["started"],
            shots=record["shots"],
            pub_shots=record.get("pub_shots"),
            twirl=policy["twirl"],
            dd=policy["dd"],
            max_execution_seconds=policy["max_execution_seconds"],
            rep_delay=policy.get("rep_delay_seconds"),
        )
        plan, batches = runtime.build_submission_plan(choices, args, binding["files"]["isa.qpy"])
        _require(bool(batches), "native qualification requires at least one batch")
        archive = list(qpy.load(run_archive.open_archive(run_dir)))
        circuits_by_name = {circuit.name: circuit for circuit in archive}
        _require(len(circuits_by_name) == len(archive), "QPY archive contains duplicate circuit names")
        report["planned_jobs"] = len(batches)
        checkpoint()
        for plan_index, name, kind, batch in batches:
            _check_preservation(runtime, run_dir, binding)
            fresh = runtime.take_snapshot(service, name, policy.get("operator_excluded_qubits", {}).get(name, ()))
            reason = fresh.ineligible_reason(policy["max_pending"])
            _require(reason is None, f"{name}: backend is ineligible: {reason}")
            owners = {id(component.choice): component.choice for pub in batch for component in pub.components}
            for owner in owners.values():
                _require(owner.snap.calibration == fresh.calibration, f"{name}: calibration timestamp changed")
                reasons = runtime.choice_change_reasons(owner, fresh)
                _require(not reasons, f"{name}: compiled calibration changed: {reasons}")
            planned = plan["planned_jobs"][plan_index]
            selected_shots = planned.get("shots", args.shots)
            tags = ["gororoba-native-dry-run", f"native-{identifier}", f"native-batch-{plan_index}"]
            sampler = runtime.configure_sampler(
                fresh.backend,
                kind,
                args.twirl,
                args.dd,
                tags,
                selected_shots,
                args.max_execution_seconds,
                **runtime.sampler_rep_delay(args),
            )
            options = sampler.options.model_dump(mode="json")
            _require(
                _options_without_tags(options) == _options_without_tags(planned["options"]),
                f"{name}: effective sampler options changed",
            )
            dt = _positive_seconds(fresh.backend.dt, f"{name}: backend dt")
            job_record = {
                "backend": name,
                "kind": kind,
                "calibration": fresh.calibration,
                "fetched_at": fresh.fetched_at,
                "backend_dt_seconds": dt,
                "shots": selected_shots,
                "pub_names": [pub.name for pub in batch],
                "pub_manifests_sha256": _json_digest([pub.manifest() for pub in batch]),
                "options": options,
                "options_sha256": _json_digest(options),
                "modeled_options_sha256": _json_digest(planned["options"]),
                "options_difference": "environment.job_tags only; native tags isolate mock recovery identity",
                "state": "attempted",
            }
            report["jobs"].append(job_record)
            checkpoint()
            _check_preservation(runtime, run_dir, binding)
            _require(runtime._instance_hash(service) == binding["instance_sha256_12"], "service instance changed")
            # The archive supplies the exact circuits whose bytes the binding names.
            job = sampler.run([circuits_by_name[pub.name] for pub in batch], shots=selected_shots, dry_run=True)
            job_record["job_id"] = job.job_id()
            job_record["state"] = "accepted"
            accepted.append((job, job_record))
            checkpoint()
    except Exception as error:
        report["status"] = "failed" if accepted or isinstance(error, PreflightError) else "unavailable"
        report["reasons"].append(str(error) if isinstance(error, PreflightError) else type(error).__name__)
        if report["jobs"] and report["jobs"][-1]["state"] == "attempted":
            report["jobs"][-1]["state"] = "unavailable"
            report["jobs"][-1]["reason"] = report["reasons"][-1]
        checkpoint()

    for job, job_record in accepted:
        try:
            result = job.result()
            estimate = job.usage_estimation
            _require(isinstance(estimate, dict), "job.usage_estimation must be a dictionary")
            job_record["estimated_quantum_seconds"] = _positive_seconds(
                estimate.get("quantum_seconds"), "job.usage_estimation quantum_seconds"
            )
            _require(len(result) == len(job_record["pub_names"]), "native result PUB count differs from request")
            job_record["pub_timing"] = [
                _timing(pub_result, job_record["backend_dt_seconds"], name)
                for name, pub_result in zip(job_record["pub_names"], result, strict=True)
            ]
            job_record["metrics"] = runtime._scrub_instances(runtime._jsonable(job.metrics()))
            # Sampler result metadata holds effective options; data registers are deliberately unread.
            result_metadata = result.metadata
            job_record["result_options"] = runtime._scrub_instances(runtime._jsonable(result_metadata.get("options")))
            job_record["state"] = "complete"
        except Exception as error:
            job_record["state"] = "failed"
            job_record["reason"] = str(error) if isinstance(error, PreflightError) else type(error).__name__
            report["reasons"].append(f"native result {job_record['job_id']}: {job_record['reason']}")
            report["status"] = "failed"
        checkpoint()

    if binding is not None:
        try:
            _check_preservation(runtime, run_dir, binding)
            report["preserved_files"] = _preserved_files(run_dir)
        except Exception as error:
            report["status"] = "failed"
            report["reasons"].append(str(error) if isinstance(error, PreflightError) else type(error).__name__)
    if (
        accepted
        and len(accepted) == report.get("planned_jobs")
        and all(entry["state"] == "complete" for _, entry in accepted)
    ):
        report["timing_qualified"] = True
        report["estimated_quantum_seconds"] = sum(entry["estimated_quantum_seconds"] for _, entry in accepted)
        try:
            budget_check = _estimate_budget(record, [entry for _, entry in accepted])
            report["server_estimate_budget"] = budget_check
            violations = [key for key, value in budget_check.items() if isinstance(value, bool) and not value]
            _require(not violations, "server estimate fails execution limits: " + ", ".join(violations))
            report["within_execution_ceilings"] = True
        except PreflightError as error:
            report["status"] = "failed"
            report["reasons"].append(str(error))
    if report["status"] == "preparing" and report["timing_qualified"] and report["within_execution_ceilings"]:
        report["status"] = "complete"
        report["qualified"] = True
    report["finished_at"] = datetime.now(UTC).isoformat()
    checkpoint()
    return dict(runtime._scrub_instances(runtime._jsonable(report)))
