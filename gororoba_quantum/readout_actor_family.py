"""Bounded full-PUB actor acquisition with descriptive, shot-preserving analysis.

The family owns the complete measured register and its synchronization barrier.
Its ideal is a prepared-bit vector. Generic dense Group prediction and packing
never interpret that vector as a probability distribution. Explicit operational
cases can be approved; statistical confirmation remains a separate contract.
"""

from __future__ import annotations

import copy
import hashlib
import io
import json
import math
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit, qpy, transpile

import parallel
import qpu_planning

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from readout_information_circuits import padded_actor_alternatives  # noqa: E402
from readout_sparse_receipt import validate_collection_sources, verify_and_project  # noqa: E402

FAMILY = "readout-actor"
SCHEMA = "readout-actor-run-v1"
DESCRIPTIVE_INFERENCE = {
    "status": "descriptive",
    "hardware_verdict": None,
    "physical_alignment": "unverified",
    "predecessor_order": "unverified",
}
SOURCE_PATHS = (
    "gororoba_quantum/readout_actor_family.py",
    "gororoba_quantum/live_run.py",
    "gororoba_quantum/adjudicate.py",
    "scripts/readout_information_circuits.py",
    "scripts/readout_sparse_projection.py",
    "scripts/readout_sparse_receipt.py",
    "scripts/readout_information_controls.py",
    "scripts/readout_actor_cost_model.py",
    "gororoba_quantum/qpu_planning.py",
    "gororoba_quantum/qpu_cases.py",
    "gororoba_quantum/parallel.py",
)


def encode(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=1, allow_nan=False) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


_SOURCE_CACHE: dict[str, str] = {}


def sources() -> dict[str, str]:
    """Rehash the closure on every call and rediscover imports when its bytes change."""
    global _SOURCE_CACHE
    if _SOURCE_CACHE:
        refreshed = {name: digest((ROOT / name).read_bytes()) for name in _SOURCE_CACHE}
        if refreshed == _SOURCE_CACHE:
            return dict(refreshed)
    directories = (ROOT / "gororoba_quantum", ROOT / "scripts")
    paths: set[Path] = set()
    for name in SOURCE_PATHS:
        entry = ROOT / name
        if entry not in paths:
            paths.update(qpu_planning.scripts_closure(entry, directories))
    _SOURCE_CACHE = {path.relative_to(ROOT).as_posix(): digest(path.read_bytes()) for path in sorted(paths)}
    return dict(_SOURCE_CACHE)


def _integer(value: Any, minimum: int, maximum: int, label: str) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{label} must be an integer in [{minimum}, {maximum}]")
    return value


def _number(value: Any, minimum: float, label: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or value < minimum:
        raise ValueError(f"{label} must be finite and at least {minimum}")
    return float(value)


def _approval_registry() -> Path:
    """Use one digest-keyed approval registry shared by this repository's worktrees."""
    result = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"], cwd=ROOT, check=True, capture_output=True, text=True
    )
    common = Path(result.stdout.strip())
    if not common.is_absolute():
        common = ROOT / common
    return common.resolve() / "gororoba-actor-approvals"


def validate_case(case: dict[str, Any]) -> None:
    fields = {
        "schema",
        "backend",
        "width",
        "reporters",
        "actors",
        "pairs",
        "groups",
        "allocations",
        "purpose",
        "reference_rule",
        "carryover_rule",
        "selection_rule",
        "inference",
        "max_execution_seconds",
        "max_total_execution_seconds",
        "reserve_seconds",
        "max_pending",
        "initialization_seconds",
        "job_overhead_seconds",
    }
    if type(case) is not dict or set(case) != fields or case["schema"] != "readout-actor-case-v1":
        raise ValueError("a complete readout-actor-case-v1 operational case is required")
    if case["inference"] != "descriptive":
        raise ValueError("the full-PUB family admits descriptive acquisition only")
    for field in ("backend", "purpose", "reference_rule", "carryover_rule", "selection_rule"):
        if type(case[field]) is not str or not case[field].strip() or len(case[field]) > 4096:
            raise ValueError(f"{field} requires a bounded explicit statement")
    width = _integer(case["width"], 3, 4096, "width")
    for field in ("reporters", "actors"):
        if type(case[field]) is not list or not case[field]:
            raise ValueError(f"{field} requires explicit physical qubits")
        for bit in case[field]:
            _integer(bit, 0, width - 1, field)
    if len(case["reporters"]) != 2 or len(set(case["reporters"] + case["actors"])) != len(
        case["reporters"] + case["actors"]
    ):
        raise ValueError("two reporters and the actors must occupy distinct qubits")
    for field, minimum, maximum in (("pairs", 2, 2), ("groups", 1, width)):
        rows = case[field]
        if type(rows) is not list or len(rows) > 10_000:
            raise ValueError(f"{field} must be a bounded projection list")
        seen: set[tuple[int, ...]] = set()
        for row in rows:
            if type(row) is not list or not minimum <= len(row) <= maximum or len(set(row)) != len(row):
                raise ValueError(f"{field} has invalid projection width")
            for bit in row:
                _integer(bit, 0, width - 1, field)
            if set(row).intersection(case["actors"]):
                raise ValueError(f"{field} cannot include an actor in a reporter projection")
            if tuple(row) in seen:
                raise ValueError(f"{field} repeats a projection")
            seen.add(tuple(row))
    if not case["pairs"] and not case["groups"]:
        raise ValueError("declare at least one projection")
    _integer(case["max_execution_seconds"], 1, 10_000, "per-job ceiling")
    _number(case["max_total_execution_seconds"], 0.000001, "total ceiling")
    _integer(case["max_pending"], 0, 1_000_000, "queue ceiling")
    for field in ("reserve_seconds", "initialization_seconds", "job_overhead_seconds"):
        _number(case[field], 0, field)
    allocations = case["allocations"]
    if type(allocations) is not list or not 1 <= len(allocations) <= 1024:
        raise ValueError("declare between one and 1024 acquisition allocations")
    names = set()
    for allocation in allocations:
        if type(allocation) is not dict or set(allocation) != {
            "name",
            "arm",
            "input",
            "stage",
            "shots",
            "rep_delay_seconds",
        }:
            raise ValueError("each allocation requires its identity, arm, input, stage, shots and delay")
        name = allocation["name"]
        if type(name) is not str or not name or len(name) > 128 or name in names:
            raise ValueError("allocation names must be unique bounded strings")
        names.add(name)
        if allocation["arm"] not in ("idle", "active") or allocation["stage"] not in (
            "pilot",
            "references",
            "discovery",
            "confirmation",
        ):
            raise ValueError("unknown actor arm or acquisition stage")
        _integer(allocation["input"], 0, 3, "reporter preparation")
        _integer(allocation["shots"], 1, 1_000_000, "shots")
        _number(allocation["rep_delay_seconds"], 0, "repetition delay")
        work = allocation["shots"] * (width + 2 * len(case["pairs"]) + sum(map(len, case["groups"])))
        if work > 250_000_000:
            raise ValueError("allocation exceeds the bounded projection-work limit")


def prepared(case: dict[str, Any], allocation: dict[str, Any]) -> list[int]:
    values = [0] * case["width"]
    for position, bit in enumerate(case["reporters"]):
        values[bit] = (allocation["input"] >> position) & 1
    if allocation["arm"] == "active":
        for bit in case["actors"]:
            values[bit] = 1
    return values


def pub_manifest(case: dict[str, Any], allocation: dict[str, Any]) -> dict[str, Any]:
    """Describe the single full-register component of one actor PUB."""
    return {
        "name": allocation["name"],
        "backend": case["backend"],
        "kind": "static",
        "components": [
            {
                "member": allocation["name"],
                "register_prefix": "c",
                "registers_by_replica": [["c"]],
                "physical_qubits": list(range(case["width"])),
            }
        ],
        "prepared_bits": prepared(case, allocation),
    }


def verify_circuit(circuit: QuantumCircuit, case: dict[str, Any], allocation: dict[str, Any]) -> None:
    """Prove the restricted circuit's preparation, full barrier and measurement map."""
    width = case["width"]
    if circuit.name != allocation["name"] or circuit.num_qubits != width or circuit.num_clbits != width:
        raise ValueError("actor circuit identity or width differs from its allocation")
    if [(register.name, len(register)) for register in circuit.cregs] != [("c", width)]:
        raise ValueError("actor acquisition requires one complete classical register c")
    x_qubits: list[int] = []
    measured: list[tuple[int, int]] = []
    barriers = 0
    for item in circuit.data:
        operation = item.operation
        qubits = [circuit.find_bit(bit).index for bit in item.qubits]
        clbits = [circuit.find_bit(bit).index for bit in item.clbits]
        if operation.name == "barrier":
            if measured or qubits != list(range(width)) or clbits:
                raise ValueError("the actor synchronization barrier must cover the full PUB before measurement")
            barriers += 1
        elif operation.name == "x":
            if barriers or measured or len(qubits) != 1 or clbits:
                raise ValueError("actor X must precede the synchronization barrier")
            x_qubits.extend(qubits)
        elif operation.name == "delay":
            if measured or len(qubits) != 1 or clbits or operation.unit != "dt":
                raise ValueError("actor delays must be single-wire dt instructions before measurement")
            _integer(operation.duration, 0, 10**12, "delay duration")
        elif operation.name == "measure":
            if barriers != 1 or len(qubits) != 1 or len(clbits) != 1:
                raise ValueError("actor measurements require the complete synchronization barrier")
            measured.append((qubits[0], clbits[0]))
        else:
            raise ValueError(f"unsupported actor instruction {operation.name}")
    expected_x = [index for index, value in enumerate(prepared(case, allocation)) if value]
    if sorted(x_qubits) != expected_x or measured != [(index, index) for index in range(width)]:
        raise ValueError("actor preparation or measurement wiring differs from the frozen case")


def _compile(task: tuple[dict[str, Any], dict[str, Any], Any, tuple[int, ...]]) -> QuantumCircuit:
    case, allocation, target, ticks = task
    circuit = padded_actor_alternatives(case["width"], tuple(case["reporters"]), tuple(case["actors"]), ticks)[
        allocation["arm"], allocation["input"]
    ]
    circuit.name = allocation["name"]
    compiled = transpile(
        circuit,
        target=target,
        initial_layout=list(range(case["width"])),
        optimization_level=0,
        scheduling_method="asap",
    )
    verify_circuit(compiled, case, allocation)
    return compiled


def compile_case(case: dict[str, Any], target: Any) -> tuple[list[QuantumCircuit], list[dict[str, Any]]]:
    validate_case(case)
    if target.num_qubits != case["width"] or target.dt is None or not math.isfinite(target.dt) or target.dt <= 0:
        raise ValueError("the case must measure the complete Target with a positive dt")
    durations = [target["x"][(index,)].duration for index in range(case["width"])]
    if any(value is None or not math.isfinite(value) or value <= 0 for value in durations):
        raise ValueError("every measured qubit requires a finite X duration")
    ticks = tuple(round(value / target.dt) for value in durations)
    if any(abs(value / target.dt - tick) > 1e-7 for value, tick in zip(durations, ticks, strict=True)):
        raise ValueError("X durations must align with Target dt")
    circuits = parallel.ordered_map(_compile, [(case, allocation, target, ticks) for allocation in case["allocations"]])
    schedules = []
    for circuit in circuits:
        starts = [
            int(circuit.op_start_times[index])
            for index, item in enumerate(circuit.data)
            if item.operation.name == "measure"
        ]
        if len(set(starts)) != 1:
            raise ValueError("the compiled full-PUB measurements require one start tick")
        schedules.append(
            {
                "name": circuit.name,
                "measurement_start_dt": starts[0],
                "duration_seconds": float(circuit.estimate_duration(target, unit="s")),
            }
        )
    if len({row["measurement_start_dt"] for row in schedules}) != 1:
        raise ValueError("actor arms have unequal compiled measurement start times")
    return circuits, schedules


def projection_manifest(case: dict[str, Any], allocation: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "schema": "readout-sparse-projection-v1",
        "condition": allocation["name"],
        "pub_name": allocation["name"],
        "pub_index": index,
        "registers": {"c": case["width"]},
        "bits": [
            {"register": "c", "index": bit, "logical": bit, "physical": bit, "prepared": value}
            for bit, value in enumerate(prepared(case, allocation))
        ],
        "pairs": case["pairs"],
        "groups": case["groups"],
    }


def _batches(case: dict[str, Any]) -> list[list[dict[str, Any]]]:
    batches: list[list[dict[str, Any]]] = []
    for allocation in case["allocations"]:
        if (
            not batches
            or (batches[-1][0]["shots"], batches[-1][0]["rep_delay_seconds"])
            != (allocation["shots"], allocation["rep_delay_seconds"])
            or (len(batches[-1]) + 1) * allocation["shots"] > 10_000_000
        ):
            batches.append([])
        batches[-1].append(allocation)
    return batches


def configure(runtime: Any, backend: Any, tags: list[str], shots: int, ceiling: int, delay: float) -> Any:
    """Bind physical preparation and measurement options explicitly for actor comparisons."""
    sampler = runtime.configure_sampler(backend, "static", False, None, tags, shots, ceiling, rep_delay=delay)
    sampler.options.twirling.enable_gates = False
    sampler.options.twirling.enable_measure = False
    sampler.options.dynamical_decoupling.enable = False
    sampler.options.execution.init_qubits = True
    return sampler


def plan(runtime: Any, service: Any, case: dict[str, Any]) -> tuple[dict[str, Any], bytes, Any]:
    validate_case(case)
    names = {backend.name for backend in service.backends()}
    if case["backend"] not in names:
        raise ValueError("the selected actor backend is absent from live discovery")
    snapshot = runtime.take_snapshot(service, case["backend"])
    reason = snapshot.ineligible_reason(case["max_pending"])
    if reason:
        raise ValueError(reason)
    circuits, schedules = compile_case(case, snapshot.backend.target)
    measurement_durations = [snapshot.backend.target["measure"][(index,)].duration for index in range(case["width"])]
    if any(value is None or not math.isfinite(value) or value <= 0 for value in measurement_durations):
        raise ValueError("every measured qubit requires a finite measurement duration")
    initialization_floor = max(measurement_durations)
    if "reset" in snapshot.backend.target.operation_names:
        reset_properties = [snapshot.backend.target["reset"].get((index,)) for index in range(case["width"])]
        if any(
            item is None or item.duration is None or not math.isfinite(item.duration) or item.duration <= 0
            for item in reset_properties
        ):
            raise ValueError("every measured qubit requires a finite positive Target reset duration")
        reset_durations = [item.duration for item in reset_properties]
        initialization_floor = max(initialization_floor, max(reset_durations))
    if case["initialization_seconds"] < initialization_floor or case["job_overhead_seconds"] < 2.0:
        raise ValueError(
            "cost scenario requires at least the Target reset/measurement proxy and documented two-second overhead"
        )
    for circuit in circuits:
        violations = runtime.target_violations(circuit, snapshot.backend.target)
        if violations:
            raise ValueError("; ".join(violations))
    for allocation in case["allocations"]:
        qpu_planning.repetition_delay(snapshot.backend, allocation["rep_delay_seconds"])
        violations = qpu_planning.shot_ceiling_violations(snapshot.backend, allocation["shots"])
        if violations:
            raise ValueError("; ".join(violations))
    buffer = io.BytesIO()
    qpy.dump(circuits, buffer)
    archive = buffer.getvalue()
    batches = _batches(case)
    combined = len(batches) * case["max_execution_seconds"]
    if combined > case["max_total_execution_seconds"]:
        raise ValueError("summed per-job ceilings exceed the case total ceiling")
    durations = {row["name"]: row["duration_seconds"] for row in schedules}
    estimates = [
        case["job_overhead_seconds"]
        + sum(
            row["shots"] * (durations[row["name"]] + row["rep_delay_seconds"] + case["initialization_seconds"])
            for row in batch
        )
        for batch in batches
    ]
    if any(value > case["max_execution_seconds"] for value in estimates):
        raise ValueError("an estimated batch exceeds its execution ceiling")
    options = [
        configure(
            runtime,
            snapshot.backend,
            [],
            batch[0]["shots"],
            case["max_execution_seconds"],
            batch[0]["rep_delay_seconds"],
        ).options.model_dump(mode="json")
        for batch in batches
    ]
    calibration = runtime.calibration_values(circuits, snapshot.backend.target, snapshot.properties)
    source_hashes = sources()
    identity = runtime.reported_identity(snapshot.backend)
    summary = snapshot.summary() | identity
    record = {
        "schema_version": SCHEMA,
        "schema_contract": "full-PUB prepared-bit ideals and descriptive sparse projection",
        "state": "planned",
        "started": datetime.now(UTC).isoformat(timespec="microseconds"),
        "family_configuration": {"name": FAMILY, "case": case, "source_sha256": source_hashes},
        "experiment_digest": digest(encode(source_hashes)),
        "versions": runtime.dependency_versions(),
        "instance_sha256_12": runtime._instance_hash(service),
        "shots": None,
        "pub_shots": {row["name"]: row["shots"] for row in case["allocations"]},
        "policy": {
            key: case[key]
            for key in ("max_execution_seconds", "max_total_execution_seconds", "reserve_seconds", "max_pending")
        },
        "execution_contract": {
            "schedules": schedules,
            "runtime_options": options,
            "batch_estimate_seconds": estimates,
            "combined_ceiling_seconds": combined,
            "initialization_proxy_seconds": initialization_floor,
            "cost_boundary": (
                "Scenario estimate; runtime initialization and provider sub-job splits remain unverified. "
                "Execution ceilings bound submission."
            ),
            "repetition_delay_range": qpu_planning.repetition_delay_range(snapshot.backend),
        },
        "groups": [
            {
                "group": FAMILY,
                "backend": case["backend"],
                "initial_layout": list(range(case["width"])),
                "calibration": snapshot.calibration,
                "calibration_fingerprint": calibration,
                "replicas": [{"physical_qubits": list(range(case["width"]))}],
                **identity,
            }
        ],
        "execution_pubs": [pub_manifest(case, row) for row in case["allocations"]],
        "qpy_sha256": digest(archive),
        "backends": {case["backend"]: summary},
        "system_inventory": {case["backend"]: {"eligibility": "eligible", **summary}},
        "inference": dict(DESCRIPTIVE_INFERENCE),
    }
    return record, archive, snapshot


def _verify_archive_circuit(task: tuple[QuantumCircuit, dict[str, Any], dict[str, Any], dict[str, Any]]) -> None:
    circuit, case, allocation, manifest = task
    verify_circuit(circuit, case, allocation)
    if manifest["prepared_bits"] != prepared(case, allocation) or manifest["name"] != circuit.name:
        raise ValueError("actor prepared-bit ideal differs from its constructor")


def verify_archive(
    record: dict[str, Any], archive: bytes, *, require_current_sources: bool = True
) -> dict[str, QuantumCircuit]:
    family = record.get("family_configuration", {})
    if record.get("schema_version") != SCHEMA or family.get("name") != FAMILY:
        raise ValueError("unsupported full-PUB actor record")
    case = family["case"]
    validate_case(case)
    if record.get("inference") != DESCRIPTIVE_INFERENCE:
        raise ValueError("actor inference must remain descriptive and unverified")
    recorded_sources = family.get("source_sha256")
    if (
        not isinstance(recorded_sources, dict)
        or not recorded_sources
        or any(
            type(name) is not str
            or type(value) is not str
            or len(value) != 64
            or any(character not in "0123456789abcdef" for character in value)
            for name, value in recorded_sources.items()
        )
        or record.get("experiment_digest") != digest(encode(recorded_sources))
        or (require_current_sources and recorded_sources != sources())
    ):
        raise ValueError("actor source closure differs from the retained record")
    if digest(archive) != record.get("qpy_sha256"):
        raise ValueError("actor QPY differs from its retained digest")
    if record.get("execution_pubs") != [pub_manifest(case, row) for row in case["allocations"]]:
        raise ValueError("actor PUB manifest differs from the frozen roles and mapping")
    if record.get("pub_shots") != {row["name"]: row["shots"] for row in case["allocations"]}:
        raise ValueError("actor shot allocation differs from the frozen case")
    decoded = qpy.load(io.BytesIO(archive))
    if len(decoded) != len(case["allocations"]):
        raise ValueError("actor QPY allocation count differs")
    tasks = [
        (circuit, case, allocation, manifest)
        for circuit, allocation, manifest in zip(decoded, case["allocations"], record["execution_pubs"], strict=True)
    ]
    parallel.ordered_map(_verify_archive_circuit, tasks, min_items=1)
    return {circuit.name: circuit for circuit in decoded}


def validate_submission(record: dict[str, Any], archive: bytes) -> None:
    """Bind the planned ledger to the verified full-PUB archive and case order."""
    reviewed = record.get("reviewed_record_sha256")
    if (
        type(reviewed) is not str
        or len(reviewed) != 64
        or any(character not in "0123456789abcdef" for character in reviewed)
    ):
        raise ValueError("actor submission requires the independently reviewed record digest")
    submission = record.get("submission")
    case = record["family_configuration"]["case"]
    batches = _batches(case)
    pubs = {pub["name"]: pub for pub in record["execution_pubs"]}
    if not isinstance(submission, dict) or submission.get("qpy_archive_sha256") != digest(archive):
        raise ValueError("actor submission QPY differs from the verified archive")
    jobs = submission.get("planned_jobs")
    if not isinstance(jobs, list) or len(jobs) != len(batches):
        raise ValueError("actor submission job count differs from the approved allocation")
    for index, (job, batch) in enumerate(zip(jobs, batches, strict=True), 1):
        names = [row["name"] for row in batch]
        if (
            not isinstance(job, dict)
            or job.get("backend") != case["backend"]
            or job.get("kind") != "static"
            or job.get("batch_index") != index
            or job.get("batch_count") != len(batches)
            or job.get("shots") != batch[0]["shots"]
            or job.get("members") != names
            or job.get("pubs") != [pubs[name] for name in names]
            or job.get("qpy_archive_sha256") != digest(archive)
        ):
            raise ValueError("actor submission PUB order or allocation differs from the approved case")


def submit(
    runtime: Any,
    service: Any,
    record: dict[str, Any],
    archive: bytes,
    run_dir: Path,
    approved_dir: Path,
    approved_sha256: str,
    *,
    reviewed_dir: Path | None = None,
    reviewed_sha256: str | None = None,
) -> None:
    """Submit the exact approved descriptive case using the shared Runtime guards."""
    if (
        reviewed_dir is None
        or type(reviewed_sha256) is not str
        or len(reviewed_sha256) != 64
        or any(character not in "0123456789abcdef" for character in reviewed_sha256)
    ):
        raise runtime.LiveRunError("the reviewed actor record and its digest are required")
    owner = reviewed_dir
    if (owner / runtime.APPROVAL_CONSUMED_FILE).exists():
        raise runtime.LiveRunError("the reviewed actor approval is already consumed")
    if (approved_dir / runtime.APPROVAL_CONSUMED_FILE).exists():
        raise runtime.LiveRunError("actor approval is already consumed")
    existing = run_dir / "record.json"
    if existing.exists() and "submission" in json.loads(existing.read_bytes()):
        raise runtime.LiveRunError("actor run directory already retains a submission ledger")
    circuits = verify_archive(record, archive)
    runtime._require_record_instance(service, record, "actor submit")
    binding: dict[str, Any] = {}
    mismatches = runtime.approved_record_mismatches(approved_dir, record, digest(archive), approved_sha256, binding)
    if mismatches:
        record["state"] = "approval_required"
        runtime.write_json(run_dir, record)
        raise runtime.LiveRunError("; ".join(mismatches))
    reviewed_mismatches = runtime.approved_record_mismatches(reviewed_dir, record, digest(archive), reviewed_sha256)
    if reviewed_mismatches:
        raise runtime.LiveRunError("reviewed actor case differs: " + "; ".join(reviewed_mismatches))
    case = record["family_configuration"]["case"]
    batches = _batches(case)
    pubs = {row["name"]: row for row in record["execution_pubs"]}
    entries = []
    for index, batch in enumerate(batches, 1):
        manifests = [pubs[row["name"]] for row in batch]
        tags = runtime._recovery_tags(
            record["started"], case["backend"], "static", index, len(batches), manifests, digest(archive)
        )
        entries.append(
            {
                "backend": case["backend"],
                "kind": "static",
                "batch_index": index,
                "batch_count": len(batches),
                "shots": batch[0]["shots"],
                "members": [row["name"] for row in batch],
                "pubs": manifests,
                "qpy_archive_sha256": digest(archive),
                "calibrations": [record["groups"][0]["calibration"]],
                "recovery_tags": tags,
                "state": "planned",
            }
        )
    record["submission"] = {
        "started": record["started"],
        "qpy_archive_sha256": digest(archive),
        "planned_backends": [case["backend"]],
        "planned_jobs": entries,
        "jobs": [],
        "complete": False,
    }
    record["approved_record"] = {"record_sha256": approved_sha256, "calibration_values": binding}
    record["reviewed_record_sha256"] = reviewed_sha256
    runtime.write_json(run_dir, record)
    for index, (entry, batch) in enumerate(zip(entries, batches, strict=True)):
        fresh, fresh_archive, snapshot = plan(runtime, service, case)
        mismatches = runtime.approved_record_mismatches(approved_dir, fresh, digest(fresh_archive), approved_sha256)
        if mismatches:
            raise runtime.LiveRunError("pre-submit actor refresh: " + "; ".join(mismatches))
        usage = service.usage()
        required = record["execution_contract"]["combined_ceiling_seconds"] + case["reserve_seconds"]
        runtime.check_budget(case["backend"], usage, required)
        remaining = usage.get("usage_remaining_seconds")
        if type(remaining) not in (int, float) or not math.isfinite(remaining) or remaining < required:
            raise runtime.LiveRunError(
                "actor acquisition requires a finite quota covering all unsettled ceilings and reserve"
            )
        sampler = configure(
            runtime,
            snapshot.backend,
            entry["recovery_tags"],
            entry["shots"],
            case["max_execution_seconds"],
            batch[0]["rep_delay_seconds"],
        )
        entry["options"] = sampler.options.model_dump(mode="json")
        expected_options = copy.deepcopy(record["execution_contract"]["runtime_options"][index])
        expected_options.setdefault("environment", {})["job_tags"] = entry["recovery_tags"]
        if entry["options"] != expected_options:
            raise runtime.LiveRunError("effective actor Sampler options differ from the approved plan")
        entry["budget_before"] = runtime._budget(service, usage)
        if index == 0:
            registry = _approval_registry()
            registry.mkdir(parents=True, exist_ok=True)
            common_fd = os.open(registry.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(common_fd)
            finally:
                os.close(common_fd)
            record["reviewed_digest_consumed"] = runtime.consume_approval(
                registry,
                record["started"],
                marker_name=f"{reviewed_sha256}.json",
                detail={"reviewed_record_sha256": reviewed_sha256},
            )
            if owner.resolve() != approved_dir.resolve():
                record["reviewed_approval_consumed"] = runtime.consume_approval(
                    owner, record["started"], detail={"reviewed_record_sha256": reviewed_sha256}
                )
            record["approval_consumed"] = runtime.consume_approval(approved_dir, record["started"])
        entry["state"] = "attempted"
        runtime.write_json(run_dir, record)
        job = sampler.run([circuits[row["name"]] for row in batch])
        record["submission"]["jobs"].append(runtime._job_record(entry, job.job_id()))
        entry["state"] = "accepted"
        record["state"] = "partially_submitted"
        runtime.write_json(run_dir, record)
    record["submission"]["complete"] = True
    record["state"] = "submitted"
    runtime.write_json(run_dir, record)


def _read_anchored(path: Path, expected: str | None) -> bytes:
    if type(expected) is not str or len(expected) != 64:
        raise ValueError(f"{path.name} requires its independently retained SHA-256 anchor")
    try:
        data = path.read_bytes()
    except OSError as error:
        raise ValueError(f"{path.name} cannot be read for anchored verification") from error
    if digest(data) != expected:
        raise ValueError(f"{path.name} requires its independently retained SHA-256 anchor")
    return data


def _verify_indexed_files(directory: Path, index_bytes: bytes, job_id: str, pub_count: int) -> None:
    """Verify every raw file in the anchored acquisition index with bounded reads."""
    index = json.loads(index_bytes)
    expected = {"result_metadata.json", *(f"pub_{position:02d}.json" for position in range(pub_count))}
    if not isinstance(index, dict) or index.get("job_id") != job_id or not isinstance(index.get("files"), dict):
        raise ValueError("indexed acquisition identity is invalid")
    files = index["files"]
    if set(files) != expected:
        raise ValueError("indexed acquisition file set differs from the submitted PUBs")
    for name, expected_digest in files.items():
        if type(expected_digest) is not str or len(expected_digest) != 64:
            raise ValueError("indexed acquisition digest is invalid")
        checksum = hashlib.sha256()
        with (directory / name).open("rb") as handle:
            while block := handle.read(1024 * 1024):
                checksum.update(block)
        if checksum.hexdigest() != expected_digest:
            raise ValueError(f"indexed acquisition file {name} differs from its retained digest")


def collect_pub(task: tuple[Any, ...]) -> tuple[dict[str, Any], bytes, bytes]:
    """Build one sparse receipt and projection without mutating shared evidence."""
    directory, job_id, pub_index, name, case, allocation, index_bytes, index_name, archive = task
    manifest_bytes = encode(projection_manifest(case, allocation, pub_index))
    raw_name = f"pub_{pub_index:02d}.json"
    raw_bytes = (directory / raw_name).read_bytes()
    receipt = {
        "schema": "readout-sparse-receipt-v1",
        "family": "actor-reporter",
        "job_id": job_id,
        "pub_index": pub_index,
        "pub_name": name,
        "circuit_name": name,
        "raw_pub_filename": raw_name,
        "raw_pub_sha256": digest(raw_bytes),
        "raw_index_sha256": digest(index_bytes),
        "qpy_sha256": digest(archive),
        "manifest_sha256": digest(manifest_bytes),
    }
    receipt_bytes = encode(receipt)
    projection = verify_and_project(
        raw_bytes, index_bytes, archive, manifest_bytes, receipt_bytes, digest(receipt_bytes)
    )
    if projection["projection"]["num_shots"] != allocation["shots"]:
        raise ValueError("provider shots differ from the approved allocation")
    row = {
        "name": name,
        "pub_index": pub_index,
        "index_file": index_name,
        "receipt_file": f"receipt-{digest(receipt_bytes)}.json",
        "receipt_sha256": digest(receipt_bytes),
        "manifest_file": f"projection-{digest(manifest_bytes)}.json",
        "result": projection,
    }
    return row, manifest_bytes, receipt_bytes


def collect_pub_outcome(task: tuple[Any, ...]) -> tuple[tuple[dict[str, Any], bytes, bytes] | None, str | None]:
    """Keep valid PUB results when a different PUB fails validation."""
    try:
        return collect_pub(task), None
    except Exception as error:  # noqa: BLE001 - a malformed PUB remains a recorded partial acquisition
        return None, type(error).__name__


def collect(runtime: Any, service: Any, run_dir: Path, record_sha256: str | None) -> dict[str, Any]:
    """Retain full raw PUBs and immutable index snapshots before sparse projection."""
    record_bytes = _read_anchored(run_dir / "record.json", record_sha256)
    record = json.loads(record_bytes)
    runtime._require_record_instance(service, record, "actor collection")
    archive = (run_dir / "isa.qpy").read_bytes()
    verify_archive(record, archive, require_current_sources=False)
    submission = record.get("submission")
    if not isinstance(submission, dict):
        raise ValueError("actor collection requires a submitted ledger")
    validate_submission(record, archive)
    runtime.submission_gaps(submission)
    before_recovery = encode(record)
    try:
        recovered = runtime.reconcile_attempted_jobs(service, submission)
    finally:
        if encode(record) != before_recovery:
            runtime.write_json(run_dir, record)
    if recovered:
        raise ValueError("recovered job identities update record.json; retain its new digest before collection")
    missing, missing_backends, missing_members = runtime.submission_gaps(submission)
    case = record["family_configuration"]["case"]
    allocations = {row["name"]: row for row in case["allocations"]}
    collection_sources = sources()
    output: dict[str, Any] = {
        "schema": "readout-actor-collection-v1",
        "record_sha256": record_sha256,
        "reviewed_record_sha256": record["reviewed_record_sha256"],
        "qpy_sha256": digest(archive),
        "jobs": {},
        "inference": record["inference"],
        "collection_source_sha256": collection_sources,
        "collection_digest": digest(encode(collection_sources)),
        "submission_complete": bool(submission.get("complete", False)) and not missing,
        "jobs_without_recorded_id": missing,
        "backends_without_recorded_job_id": missing_backends,
        "members_without_recorded_job_id": missing_members,
        "all_allocations_retained": False,
    }
    for entry in submission["jobs"]:
        job_id = entry["job_id"]
        if type(job_id) is not str or not job_id or Path(job_id).name != job_id or job_id in (".", ".."):
            raise ValueError("invalid job identity")
        output["jobs"][job_id] = {"pubs": [], "status": "unavailable"}
        try:
            job = service.job(job_id)
            output["jobs"][job_id] = {
                "usage": runtime.job_usage_record(job, len(entry["pubs"]), entry["shots"]),
                "pubs": [],
            }
            runtime._write_text_atomically(run_dir / "actor-collect.partial.json", encode(output).decode())
            if job.job_id() != job_id or job.backend().name != entry["backend"]:
                raise ValueError("provider job or backend identity differs from the actor ledger")
            try:
                backend = service.backend(entry["backend"])
            except Exception:  # noqa: BLE001 - backend discovery failures leave identity unknown
                backend = None
            output["jobs"][job_id]["backend_identity"] = runtime.execution_identity(backend, {})
            output["jobs"][job_id]["status"] = str(job.status())
            if output["jobs"][job_id]["status"] != "DONE":
                runtime._write_text_atomically(run_dir / "actor-collect.partial.json", encode(output).decode())
                continue
            result = job.result()
            if len(result) != len(entry["pubs"]):
                raise ValueError("provider PUB count differs from the actor ledger")
            windows = runtime.pub_windows(result, len(entry["pubs"]))
            properties_at = {}
            for window in windows.windows:
                if window is None or window[0] in properties_at:
                    continue
                try:
                    properties_at[window[0]] = backend.properties(datetime=window[0])
                except Exception:  # noqa: BLE001 - unavailable historical properties remain explicit nulls
                    properties_at[window[0]] = None
            output["jobs"][job_id]["backend_identity"] = runtime.execution_identity(backend, properties_at)
            names = [row["name"] for row in entry["pubs"]]
            runtime.write_raw_result(run_dir, job_id, job, result, names)
            directory = run_dir / "raw" / job_id
            index_bytes = (directory / "acquisition-index.json").read_bytes()
            index_name = f"index-{digest(index_bytes)}.json"
            runtime._write_once_atomically(directory / index_name, index_bytes.decode())
            tasks = [
                (directory, job_id, pub_index, name, case, allocations[name], index_bytes, index_name, archive)
                for pub_index, name in enumerate(names)
            ]
            for outcome, error_type in parallel.ordered_map(collect_pub_outcome, tasks, min_items=1):
                if outcome is None:
                    output["jobs"][job_id]["collection_error_type"] = error_type
                    continue
                row, manifest_bytes, receipt_bytes = outcome
                runtime._write_once_atomically(directory / row["receipt_file"], receipt_bytes.decode())
                runtime._write_once_atomically(directory / row["manifest_file"], manifest_bytes.decode())
                output["jobs"][job_id]["pubs"].append(row)
            output["jobs"][job_id]["usage"] = runtime.job_usage_record(job, len(entry["pubs"]), entry["shots"])
            runtime.snapshot_metrics(run_dir, job_id, job)
        except Exception as error:
            output["jobs"][job_id]["collection_error_type"] = type(error).__name__
            runtime._write_text_atomically(run_dir / "actor-collect.partial.json", encode(output).decode())
    observed = {pub["name"] for job in output["jobs"].values() for pub in job["pubs"]}
    output["allocations_without_results"] = sorted(set(allocations) - observed)
    output["all_allocations_retained"] = (
        output["submission_complete"]
        and observed == set(allocations)
        and all("collection_error_type" not in job for job in output["jobs"].values())
    )
    output["acquisition_status"] = "complete" if output["all_allocations_retained"] else "incomplete"
    data = encode(output)
    path = run_dir / f"actor-collection-{digest(data)}.json"
    runtime._write_once_atomically(path, data.decode())
    print(f"actor collection: {path} sha256={digest(data)}")
    return output | {"path": str(path)}


def adjudicate_pub(task: tuple[Path, dict[str, Any], bytes]) -> tuple[dict[str, Any], bytes]:
    """Replay one indexed PUB without mutating the retained acquisition."""
    directory, pub, archive = task
    for field in ("receipt_file", "manifest_file", "index_file"):
        if Path(pub[field]).name != pub[field] or pub[field] in (".", ".."):
            raise ValueError("collection artifact must name one local file")
    index_bytes = (directory / pub["index_file"]).read_bytes()
    result = verify_and_project(
        (directory / f"pub_{pub['pub_index']:02d}.json").read_bytes(),
        index_bytes,
        archive,
        (directory / pub["manifest_file"]).read_bytes(),
        (directory / pub["receipt_file"]).read_bytes(),
        pub["receipt_sha256"],
    )
    if result != pub["result"]:
        raise ValueError("replayed projection differs from the anchored collection")
    return result, index_bytes


def adjudicate(runtime: Any, run_dir: Path, collection_sha256: str | None) -> dict[str, Any]:
    """Replay an externally anchored collection without provider calls or integer narrowing."""
    if (
        type(collection_sha256) is not str
        or len(collection_sha256) != 64
        or any(character not in "0123456789abcdef" for character in collection_sha256)
    ):
        raise ValueError("actor adjudication requires an independently retained collection SHA-256")
    collection_path = run_dir / f"actor-collection-{collection_sha256}.json"
    collection = json.loads(_read_anchored(collection_path, collection_sha256))
    validate_collection_sources(collection)
    record = json.loads(_read_anchored(run_dir / "record.json", collection["record_sha256"]))
    if collection.get("reviewed_record_sha256") != record.get("reviewed_record_sha256"):
        raise ValueError("actor collection reviewed-record binding differs from the submitted record")
    archive = (run_dir / "isa.qpy").read_bytes()
    verify_archive(record, archive, require_current_sources=False)
    validate_submission(record, archive)
    analysis_sources = sources()
    output = {
        "schema": "readout-actor-adjudication-v1",
        "collection_sha256": collection_sha256,
        "reviewed_record_sha256": collection["reviewed_record_sha256"],
        "all_allocations_retained": collection["all_allocations_retained"],
        "acquisition_status": collection["acquisition_status"],
        "allocations_without_results": collection["allocations_without_results"],
        "jobs": {},
        "inference": record["inference"],
        "analysis_source_sha256": analysis_sources,
        "analysis_digest": digest(encode(analysis_sources)),
    }
    jobs_by_id = {entry["job_id"]: entry for entry in record["submission"]["jobs"]}
    for job_id, job in collection["jobs"].items():
        if Path(job_id).name != job_id or job_id in (".", ".."):
            raise ValueError("invalid collection job identity")
        directory = run_dir / "raw" / job_id
        rows = []
        checked_index: str | None = None
        tasks = [(directory, pub, archive) for pub in job["pubs"]]
        for result, index_bytes in parallel.ordered_map(adjudicate_pub, tasks, min_items=1):
            index_digest = digest(index_bytes)
            if checked_index is None:
                if job_id not in jobs_by_id:
                    raise ValueError("indexed acquisition job is absent from the submitted ledger")
                _verify_indexed_files(directory, index_bytes, job_id, len(jobs_by_id[job_id]["pubs"]))
                checked_index = index_digest
            elif checked_index != index_digest:
                raise ValueError("one job cannot mix indexed acquisition snapshots")
            rows.append(result)
        output["jobs"][job_id] = {"pubs": rows}
    data = encode(output)
    path = run_dir / f"actor-adjudication-{digest(data)}.json"
    runtime._write_once_atomically(path, data.decode())
    return output | {"path": str(path)}


def run_cli(runtime: Any, service: Any, args: Any) -> int:
    case_bytes = args.actor_case.read_bytes()
    case = json.loads(case_bytes)
    validate_case(case)
    if (
        args.max_execution_seconds != case["max_execution_seconds"]
        or args.max_total_execution_seconds != case["max_total_execution_seconds"]
    ):
        raise ValueError("CLI execution ceilings must equal the frozen actor case")
    if args.backends is not None and args.backends != [case["backend"]]:
        raise ValueError("CLI backends differ from the actor case")
    record, archive, _snapshot = plan(runtime, service, case)
    if args.actor_reviewed_record is not None:
        mismatches = runtime.approved_record_mismatches(
            args.actor_reviewed_record, record, digest(archive), args.actor_reviewed_sha256
        )
        if mismatches:
            raise ValueError("reviewed actor case differs from the fresh plan: " + "; ".join(mismatches))
    run_dir = args.out / datetime.now(UTC).strftime("%Y-%m-%dT%H%M%S.%fZ")
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "isa.qpy").write_bytes(archive)
    runtime.write_json(run_dir, record)
    runtime._write_once_atomically(run_dir / "actor-case.json", encode(case).decode())
    import qpu_cases

    case_path = qpu_cases.write_case(run_dir, record)
    if case_path is None:
        raise ValueError("the actor plan does not qualify for an unapproved written case")
    print(f"audit record: {run_dir}")
    if args.submit:
        submit(
            runtime,
            service,
            record,
            archive,
            run_dir,
            args.approved_record,
            args.approved_record_sha256,
            reviewed_dir=args.actor_reviewed_record,
            reviewed_sha256=args.actor_reviewed_sha256,
        )
    return 0
