"""Credential-free contracts for allocated PUB submission and lossless collection.

Fake services exercise approval and ledger paths. Two real executor Sampler
jobs run on the local fake backend at uniform 64 and 128 shots; those jobs
establish client decoding and ordered registers, rather than QPU behavior.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import tempfile
from collections.abc import Callable
from contextlib import redirect_stdout
from datetime import UTC, datetime, timedelta
from functools import partial
from pathlib import Path
from typing import Any
from unittest.mock import patch

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, qpy, transpile
from qiskit_ibm_runtime.executor_sampler import Sampler
from qiskit_ibm_runtime.fake_provider import FakeFez
from qiskit_ibm_runtime.results.quantum_program import ChunkPart, ChunkSpan

import live_run as runtime
import packing
import qpu_planning
import run_archive
from experiments import experiment_groups
from runtime_contracts import (
    _collect_with_zero_simulation,
    _CollectionProbeService,
    _executor_result,
    _fake_snapshot,
    _fixture_args,
    _ProbeBackend,
    _ProbeJob,
    _ProbeResultJob,
    _ProbeSampler,
    _ProbeService,
    _synthetic_fusion_choice,
    _zero_replica_distributions,
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _reject(call: Callable[[], Any], message: str, fragment: str | None = None) -> None:
    try:
        call()
    except runtime.LiveRunError as error:
        if fragment is not None and fragment not in str(error):
            raise RuntimeError(f"{message}: unexpected rejection {error}") from error
    else:
        raise RuntimeError(message)


def _fake_sampler(
    backend: Any,
    kind: str,
    twirl: bool,
    dd: str | None,
    tags: list[str],
    shots: int = 4096,
    max_execution_seconds: int | None = None,
) -> _ProbeSampler:
    del backend, twirl, dd
    return _ProbeSampler(kind, tags, shots, lambda circuits: None, None, max_execution_seconds)


def _fixture() -> tuple[_ProbeBackend, _ProbeService, argparse.Namespace, list[runtime.Choice], dict[str, Any]]:
    backend = _ProbeBackend("allocated-fixture", FakeFez())
    service = _ProbeService([backend])
    args = _fixture_args(
        groups=["design_a", "zero_divisor_fringe"], shots=128, max_replicas=1, isolated_reference=False
    )
    choices, record = runtime.plan(service, args)
    pubs = runtime.execution_pubs(choices)
    _require(len(pubs) >= 4, "allocated fixture needs interleaved rows in both tiers")
    _require(any(len(pub.components) > 1 for pub in pubs), "allocated fixture needs a fused PUB")
    args.pub_shots = {pub.name: 64 if index % 2 == 0 else 128 for index, pub in enumerate(pubs)}
    record["pub_shots"] = dict(args.pub_shots)
    record["execution_contract"] = qpu_planning.execution_contract(choices, record)
    record["groups"] = [
        runtime._choice_record(
            choice,
            {entry.name: _zero_replica_distributions(entry) for entry in choice.entries},
            choice.snap.calibration,
            args.shots,
        )
        for choice in choices
    ]
    return backend, service, args, choices, record


def _verify_batches(choices: list[runtime.Choice], args: argparse.Namespace) -> None:
    pubs = runtime.execution_pubs(choices)
    batches = runtime.submission_batches(choices, "static", args.shots, args.pub_shots)
    expected = [[pub.name for pub in pubs if args.pub_shots[pub.name] == tier] for tier in (64, 128)]
    _require([[pub.name for pub in batch] for batch in batches] == expected, "tier grouping changed PUB row order")
    _require([runtime.batch_shots(batch, args.shots, args.pub_shots) for batch in batches] == [64, 128], "wrong tiers")
    _require(runtime.submission_batches(choices, "static", 128) == [pubs], "uniform batching changed")
    _require(runtime.submission_batches(choices, "dynamic", 128, args.pub_shots) == [], "static PUB became dynamic")
    missing = dict(args.pub_shots)
    missing.pop(pubs[0].name)
    extra = dict(args.pub_shots, unknown_pub=64)
    invalid_maps: list[dict[str, Any]] = [missing, extra, {}]
    for value in (True, 0, -1, 64.0, "64", runtime.MAX_JOB_EXECUTIONS + 1):
        invalid_maps.append(dict(args.pub_shots) | {pubs[0].name: value})
    for allocation in invalid_maps:
        _reject(
            partial(runtime.submission_batches, choices, "static", 128, allocation),
            f"invalid PUB shot allocation accepted: {allocation}",
        )
    _reject(lambda: runtime.batch_shots([], 128, args.pub_shots), "empty batch accepted")
    _reject(lambda: runtime.batch_shots(pubs, 128, args.pub_shots), "mixed-tier job accepted")
    _reject(lambda: runtime.batch_shots([pubs[0]], 128, missing), "unallocated batch PUB accepted")
    with patch.object(runtime, "MAX_JOB_EXECUTIONS", 128):
        _reject(
            lambda: runtime.submission_batches(choices, "static", 128, args.pub_shots),
            "tier aggregate execution limit ignored",
            "Sampler job limit",
        )


def _verify_multiple_backends() -> None:
    groups = {group.name: group for group in experiment_groups()}
    choices = [
        _synthetic_fusion_choice(groups[name], _fake_snapshot(_ProbeBackend(f"backend-{index}", FakeFez())), 0, False)
        for index, name in enumerate(("design_a", "zero_divisor_fringe"))
    ]
    pubs = runtime.execution_pubs(choices)
    allocation = {pub.name: (64 if index % 2 == 0 else 128) for index, pub in enumerate(pubs)}
    args = _fixture_args(shots=128, pub_shots=allocation)
    with patch.object(runtime, "configure_sampler", _fake_sampler):
        submission, batches = runtime.build_submission_plan(choices, args, "0" * 64)
    _require(set(submission["planned_backends"]) == {"backend-0", "backend-1"}, "backend partition disappeared")
    planned_names = [pub["name"] for job in submission["planned_jobs"] for pub in job["pubs"]]
    _require(
        len(planned_names) == len(set(planned_names)) and set(planned_names) == set(allocation), "PUB coverage lost"
    )
    for index, _unused_backend, _unused_kind, batch in batches:
        planned = submission["planned_jobs"][index]
        _require(all(allocation[pub.name] == planned["shots"] for pub in batch), "backend partition lost shot tier")
    budget = qpu_planning.budget_plan(runtime, choices, args, {"usage_remaining_seconds": 600})
    budget_jobs = {
        (job["backend"], job["kind"], job["batch_index"]): (job["shots"], job["pub_names"]) for job in budget["jobs"]
    }
    planned_jobs = {
        (job["backend"], job["kind"], job["batch_index"]): (job["shots"], [pub["name"] for pub in job["pubs"]])
        for job in submission["planned_jobs"]
    }
    _require(budget_jobs == planned_jobs, "budget and submission tier partitions differ across backends")
    _require(
        budget["combined_ceiling_seconds"] == len(planned_jobs) * args.max_execution_seconds,
        "backend-tier job ceiling aggregation differs from the actual plan",
    )
    extra_args = copy.copy(args)
    extra_args.pub_shots = allocation | {"outside_manifest": 64}
    with patch.object(runtime, "configure_sampler", _fake_sampler):
        _reject(
            lambda: runtime.build_submission_plan(choices, extra_args, "0" * 64),
            "backend subsetting silently removed an extra global PUB key",
        )


def _verify_approval(run_dir: Path, record: dict[str, Any], choices: list[runtime.Choice]) -> None:
    digest = runtime.write_archive(run_dir, choices)
    runtime.write_json(run_dir, record)
    record_digest = hashlib.sha256((run_dir / "record.json").read_bytes()).hexdigest()
    _require(
        runtime.approved_record_mismatches(run_dir, record, digest, record_digest) == [],
        "identical allocated approval rejected",
    )
    first = next(iter(record["pub_shots"]))
    for mutation in ("value", "missing", "extra", "removed"):
        changed = copy.deepcopy(record)
        if mutation == "value":
            changed["pub_shots"][first] *= 2
        elif mutation == "missing":
            changed["pub_shots"].pop(first)
        elif mutation == "extra":
            changed["pub_shots"]["extra"] = 64
        else:
            changed.pop("pub_shots")
        mismatches = runtime.approved_record_mismatches(run_dir, changed, digest, record_digest)
        _require(
            any("pub_shots" in reason for reason in mismatches), f"{mutation} allocation tampering passed approval"
        )


def _submit_fixture(
    run_dir: Path,
    approved_dir: Path,
    service: _ProbeService,
    args: argparse.Namespace,
    choices: list[runtime.Choice],
    record: dict[str, Any],
) -> dict[str, Any]:
    submitted = copy.deepcopy(record)
    submit_args = copy.copy(args)
    submit_args.approved_record = approved_dir
    submit_args.approved_record_sha256 = hashlib.sha256((approved_dir / "record.json").read_bytes()).hexdigest()
    calls: list[tuple[int, list[str]]] = []

    class FixtureSampler(_ProbeSampler):
        def run(self, circuits: list[QuantumCircuit]) -> _ProbeJob:
            tier = self.options.model_dump(mode="json")["default_shots"]
            planned = submitted["submission"]["planned_jobs"][len(calls)]
            _require(planned["state"] == "attempted", "run precedes attempted-job checkpoint")
            _require(planned["shots"] == tier, "Sampler option differs from planned shots")
            _require(
                [circuit.name for circuit in circuits] == [pub["name"] for pub in planned["pubs"]], "run reordered PUBs"
            )
            disk_record = json.loads((run_dir / "record.json").read_text())
            _require(
                disk_record["submission"]["planned_jobs"][len(calls)]["state"] == "attempted",
                "attempted-job ledger reaches disk after run",
            )
            calls.append((tier, [circuit.name for circuit in circuits]))
            return _ProbeJob(f"allocated-local-fixture-{len(calls)}")

    def configure(
        backend: Any,
        kind: str,
        twirl: bool,
        dd: str | None,
        tags: list[str],
        shots: int = 4096,
        max_execution_seconds: int | None = None,
    ) -> FixtureSampler:
        del backend, twirl, dd
        return FixtureSampler(kind, tags, shots, lambda circuits: None, None, max_execution_seconds)

    with patch.object(runtime, "configure_sampler", configure), redirect_stdout(io.StringIO()):
        with tempfile.TemporaryDirectory(prefix="allocated-tampered-approval-") as directory:
            tampered_dir = Path(directory)
            tampered_record = copy.deepcopy(record)
            first_pub = next(iter(tampered_record["pub_shots"]))
            tampered_record["pub_shots"][first_pub] *= 2
            _reject(
                lambda: runtime.submit(
                    service,
                    list(choices),
                    submit_args,
                    tampered_record,
                    lambda: runtime.write_archive(tampered_dir, choices),
                    lambda: runtime.write_json(tampered_dir, tampered_record),
                ),
                "allocation tampering reached submission",
                "pub_shots",
            )
            _require(tampered_record["state"] == "approval_required", "tampered allocation lost renewal state")
            _require(calls == [], "tampered allocation invoked a Sampler")
            _require((approved_dir / "approval-consumed.json").exists() is False, "failed approval was consumed")
        runtime.submit(
            service,
            list(choices),
            submit_args,
            submitted,
            lambda: runtime.write_archive(run_dir, choices),
            lambda: runtime.write_json(run_dir, submitted),
        )
    _require([tier for tier, unused_names in calls] == [64, 128], "submission failed to send one job per tier")
    _require(submitted["state"] == "submitted" and submitted["submission"]["complete"], "submission stayed incomplete")
    _require(runtime.submission_gaps(submitted["submission"]) == ([], [], []), "submitted allocation left ledger gaps")
    _require((approved_dir / "approval-consumed.json").is_file(), "approved allocated run left approval reusable")
    for entry in submitted["submission"]["jobs"]:
        _require(entry["shots"] == entry["options"]["default_shots"], "submitted ledger lost shot count")
    changed = copy.deepcopy(submitted["submission"])
    changed["jobs"][0]["shots"] *= 2
    _reject(lambda: runtime.submission_gaps(changed), "submitted shot ledger tampering accepted", "shots")
    return submitted


def _result_jobs(
    run_dir: Path, record: dict[str, Any], wrong_count: bool = False, missing_windows: bool = False
) -> dict[str, _ProbeResultJob]:
    archived = {circuit.name: circuit for circuit in qpy.load(run_archive.open_archive(run_dir))}
    jobs: dict[str, _ProbeResultJob] = {}
    base = datetime(2026, 10, 10, 12, 0, tzinfo=UTC)
    for job_index, job in enumerate(record["submission"]["jobs"]):
        circuits = [archived[pub["name"]] for pub in job["pubs"]]
        chunks = [
            ChunkSpan(base + timedelta(seconds=index), base + timedelta(seconds=index + 1), [ChunkPart(index, 1)])
            for index in range(len(circuits))
        ]
        durations = [pub["target_gate_lower_bound_dt"] for pub in job["pubs"]]
        shots = job["shots"] - int(wrong_count and job_index == 0)
        result = _executor_result(FakeFez(), circuits, shots, [] if missing_windows else chunks, durations)
        jobs[job["job_id"]] = _ProbeResultJob(result, usage={"status": "completed"}, charge=1.0)
    return jobs


def _verify_raw(raw_dir: Path, expected_shots: int) -> None:
    index = json.loads((raw_dir / "index.json").read_text())
    pub_files = []
    for filename, digest in index["files"].items():
        _require(hashlib.sha256((raw_dir / filename).read_bytes()).hexdigest() == digest, "raw checksum mismatch")
        if filename.startswith("pub_"):
            pub_files.append(filename)
            payload = json.loads((raw_dir / filename).read_text())
            _require(
                all(len(register["bitstrings"]) == expected_shots for register in payload["registers"].values()),
                "raw shot-ordered register count changed",
            )
    _require(bool(pub_files), "raw index contains no PUB files")


def _verify_collection(backend: _ProbeBackend, run_dir: Path, record: dict[str, Any]) -> None:
    jobs = _result_jobs(run_dir, record)
    with redirect_stdout(io.StringIO()):
        _collect_with_zero_simulation(_CollectionProbeService(backend, jobs), run_dir)
    output = json.loads((run_dir / "collect.json").read_text())
    members = {component["member"] for pub in record["execution_pubs"] for component in pub["components"]}
    family = output[0]["family_measurements"]
    _require(set(family) == members, "cross-job family header lost a logical member")
    for member, evidence in family.items():
        allocation = record["pub_shots"][evidence["execution"]["pub"]]
        _require(evidence["execution"]["shots"] == allocation, f"{member}: wrong measured denominator")
        _require(evidence["replay_status"] == "calibration_bound", f"{member}: calibration replay unavailable")
        _require(
            evidence["replica_probabilities"] == evidence["replayed_replica_probabilities"], "zero-law replay differs"
        )
    _require(
        any(group.get("summary_unavailable") for group in output[1:]),
        "fixture failed to exercise groups split across tier jobs",
    )
    for job in record["submission"]["jobs"]:
        _verify_raw(run_dir / runtime.RAW_DIRECTORY / job["job_id"], job["shots"])
        measured_usage = output[0]["jobs"][job["job_id"]]["usage"]["submitted_pub_shots"]
        _require(measured_usage == len(job["pubs"]) * job["shots"], "billing ledger used the global shot maximum")

    with tempfile.TemporaryDirectory(prefix="allocated-missing-windows-") as directory:
        missing_dir = Path(directory)
        (missing_dir / "record.json").write_bytes((run_dir / "record.json").read_bytes())
        (missing_dir / "isa.qpy").write_bytes(run_archive.read_archive(run_dir))
        missing_jobs = _result_jobs(missing_dir, record, missing_windows=True)
        with redirect_stdout(io.StringIO()):
            _collect_with_zero_simulation(_CollectionProbeService(backend, missing_jobs), missing_dir)
        missing = json.loads((missing_dir / "collect.json").read_text())[0]["family_measurements"]
        _require(set(missing) == members, "missing windows erased measured family members")
        _require(
            all(
                evidence["replayed_replica_probabilities"] is None
                and evidence["replay_status"] == "execution_window_unavailable"
                for evidence in missing.values()
            ),
            "absent execution windows fabricated calibration replay",
        )

    with tempfile.TemporaryDirectory(prefix="allocated-straddled-calibration-") as directory:
        straddled_dir = Path(directory)
        (straddled_dir / "record.json").write_bytes((run_dir / "record.json").read_bytes())
        (straddled_dir / "isa.qpy").write_bytes(run_archive.read_archive(run_dir))
        original_execution = runtime.component_execution_records

        def straddled_execution(
            pub_manifest: dict[str, Any],
            window: tuple[datetime, datetime] | None,
            calibration: datetime | None,
            calibration_changed: bool | None,
            window_reason: str | None = None,
        ) -> dict[str, dict[str, Any]]:
            del calibration_changed
            return original_execution(pub_manifest, window, calibration, True, window_reason)

        with patch.object(runtime, "component_execution_records", straddled_execution), redirect_stdout(io.StringIO()):
            _collect_with_zero_simulation(_CollectionProbeService(backend, jobs), straddled_dir)
        straddled = json.loads((straddled_dir / "collect.json").read_text())[0]["family_measurements"]
        _require(set(straddled) == members, "straddled calibrations erased measured family members")
        _require(
            all(
                evidence["replayed_replica_probabilities"] is None
                and evidence["replay_status"] == "calibration_changed_during_shots"
                for evidence in straddled.values()
            ),
            "a straddled calibration fabricated a single-calibration replay",
        )

    with tempfile.TemporaryDirectory(prefix="allocated-wrong-count-") as directory:
        invalid_dir = Path(directory)
        (invalid_dir / "record.json").write_bytes((run_dir / "record.json").read_bytes())
        (invalid_dir / "isa.qpy").write_bytes(run_archive.read_archive(run_dir))
        invalid_jobs = _result_jobs(invalid_dir, record, wrong_count=True)
        with redirect_stdout(io.StringIO()):
            _reject(
                lambda: _collect_with_zero_simulation(_CollectionProbeService(backend, invalid_jobs), invalid_dir),
                "actual returned count escaped validation",
                "returned shot count",
            )
        job = record["submission"]["jobs"][0]
        _verify_raw(invalid_dir / runtime.RAW_DIRECTORY / job["job_id"], job["shots"] - 1)
        _require((invalid_dir / "collect.partial.json").is_file(), "count mismatch lost the partial billing checkpoint")
        _require((invalid_dir / "collect.json").exists() is False, "count mismatch published complete analysis")


def _verify_recorded_shots(record: dict[str, Any]) -> None:
    job = record["submission"]["jobs"][0]
    _require(runtime._recorded_job_shots(record, job) == job["shots"], "valid allocated job rejected")
    for value in (True, 64.0, "64", 0, -1):
        changed_job = copy.deepcopy(job)
        changed_job["shots"] = value
        _reject(
            partial(runtime._recorded_job_shots, record, changed_job),
            f"invalid job shots accepted: {value!r}",
        )
    absent_job_shots = copy.deepcopy(job)
    absent_job_shots.pop("shots")
    _reject(lambda: runtime._recorded_job_shots(record, absent_job_shots), "allocated job used legacy shot fallback")
    first = job["pubs"][0]["name"]
    for mutation in ("missing", "extra", "stale", "bool", "string"):
        changed_record = copy.deepcopy(record)
        if mutation == "missing":
            changed_record["pub_shots"].pop(first)
        elif mutation == "extra":
            changed_record["pub_shots"]["extra"] = 64
        elif mutation == "stale":
            changed_record["pub_shots"][first] *= 2
        else:
            changed_record["pub_shots"][first] = True if mutation == "bool" else "64"
        _reject(
            partial(runtime._recorded_job_shots, changed_record, job),
            f"{mutation} record allocation accepted",
        )
    null_map = copy.deepcopy(record)
    null_map["pub_shots"] = None
    _reject(lambda: runtime._recorded_job_shots(null_map, job), "explicitly null allocation used legacy fallback")
    mismatched_option = copy.deepcopy(job)
    mismatched_option["options"]["default_shots"] *= 2
    _reject(lambda: runtime._recorded_job_shots(record, mismatched_option), "effective Sampler shots mismatch accepted")
    legacy = copy.deepcopy(record)
    legacy.pop("pub_shots")
    legacy_job = copy.deepcopy(job)
    legacy_job.pop("shots")
    legacy_job["options"]["default_shots"] = legacy["shots"]
    _require(runtime._recorded_job_shots(legacy, legacy_job) == legacy["shots"], "legacy uniform fallback rejected")


def _verify_local_executor() -> list[dict[str, Any]]:
    backend = FakeFez()
    circuits = []
    for row_index in range(2):
        components = []
        for member_index in range(2):
            circuit = QuantumCircuit(QuantumRegister(2, "q"), ClassicalRegister(1, "r0_result"))
            if member_index == row_index:
                circuit.x(member_index)
            circuit.measure(member_index, 0)
            components.append(transpile(circuit, backend=backend, optimization_level=0, initial_layout=[0, 1]))
        circuits.append(packing.fuse(components, ["g0_", "g1_"], f"local_ordered_row_{row_index}"))
    receipts = []
    for shots in (64, 128):
        sampler = Sampler(mode=backend)
        sampler.options.simulator.seed_simulator = 20261012
        result = sampler.run(circuits, shots=shots).result()
        _require(len(result) == len(circuits), "local executor changed PUB count")
        for row_index, pub in enumerate(result):
            for member_index in range(2):
                name = f"g{member_index}_r0_result"
                register = getattr(pub.data, name)
                _require(register.num_shots == shots, "local executor returned the wrong tier")
                counts = register.get_counts()
                expected = "1" if row_index == member_index else "0"
                _require(counts.get(expected, 0) >= 0.75 * shots, "local executor lost PUB/member order")
        receipts.append({"shots": shots, "pubs": len(result), "registers_per_pub": 2, "mode": "local_fake_backend"})
    return receipts


def main() -> None:
    backend, service, args, choices, record = _fixture()
    _verify_batches(choices, args)
    _verify_multiple_backends()
    with tempfile.TemporaryDirectory(prefix="allocated-runtime-contracts-") as directory:
        root = Path(directory)
        approved_dir, run_dir = root / "approved", root / "submitted"
        approved_dir.mkdir()
        run_dir.mkdir()
        _verify_approval(approved_dir, record, choices)
        submitted = _submit_fixture(run_dir, approved_dir, service, args, choices, record)
        _verify_recorded_shots(submitted)
        _verify_collection(backend, run_dir, submitted)
    local_jobs = _verify_local_executor()
    print(json.dumps({"status": "pass", "local_executor_jobs": local_jobs, "physical_qpu_jobs": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
