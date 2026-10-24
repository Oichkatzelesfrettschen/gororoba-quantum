"""Archive a matched correction pilot and qualify mock schedules without QPU execution.

Preparation has a separate record format because backend schedule evidence must
close before the pilot receives a production submission interface. The only
remote primitive call sets dry_run=True; randomized mock outcomes are unread.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any, cast

import numpy as np
from qiskit import qpy
from qiskit_ibm_runtime import QiskitRuntimeService

import correction_circuits
import correction_schedule
import correction_statistics
import ibm_account
import live_run
import local_compute
import qrng_seeds
from qpe_diagnostics import ideal_compiled_probabilities
from qpu_planning import repetition_delay

MEMBERS = correction_statistics.MEMBERS
ARMS = ("measured_feedback", "recorded_bit_independent", "recorded_bit_independent", "measured_feedback")
LABELS = (1, 1, 3, 3)
EXTRA_SOURCES = (
    "correction_circuits.py",
    "correction_schedule.py",
    "correction_statistics.py",
    "correction_preparation.py",
)
PACKAGES = ("numpy", "qiskit", "qiskit-aer", "qiskit-ibm-runtime", "scipy", "rustworkx", "sympy")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_hashes() -> dict[str, str]:
    root = Path(__file__).resolve().parent
    return {
        name: _hash((root / name).read_bytes())
        for name in sorted(set(live_run.EXPERIMENT_SOURCE_MANIFEST + EXTRA_SOURCES))
    }


def _qpy(circuits: list[Any]) -> bytes:
    stream = io.BytesIO()
    qpy.dump(circuits, stream)
    return stream.getvalue()


def _write(path: Path, value: dict[str, Any]) -> None:
    live_run._replace_atomically(
        path,
        lambda handle: handle.write(
            json.dumps(live_run._scrub_instances(value), indent=2, sort_keys=True, allow_nan=False) + "\n"
        ),
        "w",
    )


def build(
    snapshot: Any, *, seed: int = 20261010, shots: int = 8192, model_shots: int = 32768
) -> tuple[dict[str, Any], dict[str, bytes]]:
    """Compile once, bind four arms, validate ideal laws, and freeze model predictions."""
    _require(type(seed) is int and seed >= 0, "seed must be a nonnegative integer")
    _require(type(model_shots) is int and model_shots > 0, "model_shots must be a positive integer")
    power = correction_statistics.planning_certificate(shots)
    captured_sources = source_hashes()
    template = correction_circuits.correction_template()
    routed = live_run._compile(template, snapshot, seed)
    circuits = []
    members = []
    for name, label, arm in zip(MEMBERS, LABELS, ARMS, strict=True):
        circuit = correction_circuits.bind_correction_template(routed, label, arm)
        circuit.name = name
        violations = live_run.compiled_violations(circuit, snapshot)
        _require(not violations, f"{name}: compiled operation rejection: {violations}")
        ideal = np.zeros(4)
        ideal[label] = 1.0
        probabilities = ideal_compiled_probabilities(circuit)
        _require(bool(np.allclose(probabilities, ideal, rtol=0, atol=1e-10)), f"{name}: compiled ideal law mismatch")
        circuits.append(circuit)
        members.append(
            {
                "name": name,
                "label": label,
                "arm": arm,
                "ideal_probabilities": ideal.tolist(),
                "compiled_probabilities": list(map(float, probabilities)),
                "target_gate_lower_bound_seconds": live_run.duration_s(circuit, snapshot.backend.target),
                "cz_count": sum(operation == "cz" for operation, _qubits in live_run._ops(circuit)),
                "active_physical_qubits": sorted(live_run._physical(circuit)),
            }
        )
    pairs = {
        "1": correction_circuits.validate_correction_pair(routed, circuits[0], circuits[1], 1),
        "3": correction_circuits.validate_correction_pair(routed, circuits[3], circuits[2], 3),
    }
    live_run.check_target_matches_properties(circuits, snapshot.backend.target, snapshot.properties, snapshot.name)
    simulator = live_run.noise_simulator(snapshot.name, snapshot.backend.target, snapshot.properties)
    simulated = local_compute.run(simulator, circuits, model_shots, live_run.SEED_SIMULATOR)
    for index, member in enumerate(members):
        counts = simulated.get_counts(index)
        vector = [0] * 4
        for bits, count in counts.items():
            outcome = int(bits.replace(" ", ""), 2)
            _require(0 <= outcome < 4 and type(count) is int and count >= 0, "invalid simulation count")
            vector[outcome] += count
        _require(sum(vector) == model_shots, "simulation shot count differs from requested shots")
        member["noise_model_counts"] = vector
        member["noise_model_probabilities"] = [count / model_shots for count in vector]
    archive = _qpy(circuits)
    template_archive = _qpy([routed])
    # The archive is the exact future scheduling input, so validate its round trip.
    restored = list(qpy.load(io.BytesIO(archive)))
    restored_template = list(qpy.load(io.BytesIO(template_archive)))[0]
    correction_circuits.validate_correction_pair(restored_template, restored[0], restored[1], 1)
    correction_circuits.validate_correction_pair(restored_template, restored[3], restored[2], 3)
    delay = repetition_delay(snapshot.backend)
    lower_seconds = 2.3 + shots * sum(
        (delay + cast(float, member["target_gate_lower_bound_seconds"]) for member in members), 0.0
    )
    historical_seconds = 2.3 + 4 * shots * (250e-6 + 22.904e-6)
    _require(captured_sources == source_hashes(), "preparation sources changed during compilation or simulation")
    report = {
        "schema": "known-label-correction-preparation-v1",
        "state": "prepared_schedule_unqualified",
        "physical_execution_authorized": False,
        "production_submission_interface": "unavailable pending schedule qualification and approval-bound integration",
        "prepared_at": datetime.now(UTC).isoformat(),
        "backend": snapshot.name,
        "backend_snapshot": snapshot.summary(),
        "versions": {package: version(package) for package in PACKAGES},
        "sources": captured_sources,
        "source_commit": live_run._code_commit(),
        "files": {"isa.qpy": _hash(archive), "template.qpy": _hash(template_archive)},
        "seed_transpiler": seed,
        "shots_per_pub": shots,
        "pub_count": 4,
        "replicas_per_pub": 1,
        "member_order": list(MEMBERS),
        "members": members,
        "circuit_pairs": pairs,
        "calibration_fingerprint": live_run.fingerprint(circuits, snapshot.backend.target, snapshot.properties),
        "decision_contract": {
            "alpha": 0.05,
            "per_bound_tail": 0.0125,
            "minimum_gain": 0.01,
            "rule": "CP_lower_U - CP_upper_F > 0.01 for both s1 and s3",
            "observation": "terminal correctness using every integer-count shot; y=first_bit+2*terminal_bit",
            "policy_scope": "supplied odd-label witnesses; U retains dispatch and removes recorded-value dependence",
            "coverage_assumption": "independent stationary shots within each PUB; cross-PUB dependence allowed",
            "comparison_assumption": "stable comparison context; four PUBs cannot identify arbitrary drift",
            "sampling": "fixed sample; entire future acquisition is prospective; cross-PUB shot indices are unpaired",
        },
        "hypothetical_power": power,
        "model_prediction": {
            "evidence_class": "finite-shot calibration noise simulation; controller/instrument errors are incomplete",
            "shots_per_member": model_shots,
            "seed": live_run.SEED_SIMULATOR,
            "batches": local_compute.batches(simulator),
            "prediction_frozen_before_hardware": True,
        },
        "timing": {
            "repetition_delay_seconds": delay,
            "assumed_overhead_seconds": 2.3,
            "target_gate_cost_lower_scenario_seconds": lower_seconds,
            "target_scope": "gate-duration lower bound excludes dynamic controller latency; overhead is historical",
            "historical_schedule_scenario_seconds": historical_seconds,
            "historical_schedule_seconds": 22.904e-6,
            "fresh_native_estimate_seconds": None,
            "service_ceiling_seconds": None,
        },
        "native_schedule_qualified": False,
        "remaining_gates": [
            "native mock event schedules for the exact QPY/options/calibration",
            "production family, raw-count collector and approval/submission binding after schedule qualification",
            "fresh written execution case and explicit owner approval",
        ],
    }
    return report, {"isa.qpy": archive, "template.qpy": template_archive}


def _preserved(directory: Path, report: dict[str, Any], record_hash: str) -> None:
    _require(_hash((directory / "preparation.json").read_bytes()) == record_hash, "preparation record changed")
    _require(source_hashes() == report["sources"], "preparation source changed")
    _require(set(report["versions"]) == set(PACKAGES), "dependency manifest is incomplete")
    _require(set(report["files"]) == {"isa.qpy", "template.qpy"}, "archive manifest is incomplete")
    for package, expected in report["versions"].items():
        _require(version(package) == expected, f"dependency changed: {package}")
    for name, expected in report["files"].items():
        _require(_hash((directory / name).read_bytes()) == expected, f"archive changed: {name}")


def native_qualification(
    service: Any, directory: Path, *, expected_preparation_sha256: str, runtime: Any = live_run
) -> dict[str, Any]:
    """Schedule exactly four archived PUBs on the mock service and retain metadata only."""
    record_bytes = (directory / "preparation.json").read_bytes()
    report = json.loads(record_bytes)
    record_hash = _hash(record_bytes)
    _require(record_hash == expected_preparation_sha256, "preparation digest differs from expected bytes")
    destination = directory / "native-qualification.json"
    _require(not destination.exists(), "native qualification already exists; prepare a fresh directory")
    result: dict[str, Any] = {
        "schema": "known-label-correction-native-qualification-v1",
        "status": "preparing",
        "qualified": False,
        "dry_run": True,
        "physical_execution_authorized": False,
        "preparation_sha256": record_hash,
        "files": report["files"],
        "job_id": None,
        "measurement_data": "mock values are unread and excluded from scientific evidence",
    }
    _write(destination, result)
    try:
        _preserved(directory, report, record_hash)
        _require(report["schema"] == "known-label-correction-preparation-v1", "unsupported preparation schema")
        _require(report["member_order"] == list(MEMBERS), "member order differs from protocol")
        _require(type(report["shots_per_pub"]) is int and report["shots_per_pub"] > 0, "invalid shot count")
        _require(
            type(report["pub_count"]) is int
            and report["pub_count"] == 4
            and type(report["replicas_per_pub"]) is int
            and report["replicas_per_pub"] == 1,
            "invalid PUB or replica count",
        )
        _require(report["physical_execution_authorized"] is False, "preparation has an invalid execution state")
        _require(runtime._instance_hash(service) == report["instance_sha256_12"], "service instance changed")
        fresh = runtime.take_snapshot(service, report["backend"])
        _require(fresh.ineligible_reason(None) is None, "backend is ineligible")
        _require(fresh.calibration == report["backend_snapshot"]["calibration"], "calibration changed")
        circuits = list(qpy.load(io.BytesIO((directory / "isa.qpy").read_bytes())))
        _require([circuit.name for circuit in circuits] == list(MEMBERS), "QPY member order changed")
        templates = list(qpy.load(io.BytesIO((directory / "template.qpy").read_bytes())))
        _require(len(templates) == 1, "exactly one common template is required")
        for label, feedback, known in ((1, 0, 1), (3, 3, 2)):
            restored_pair = correction_circuits.validate_correction_pair(
                templates[0], circuits[feedback], circuits[known], label
            )

            # Retained archive bytes carry identity; QPY reserialization is not canonical.
            def stable(pair: dict[str, Any]) -> dict[str, Any]:
                return {key: value for key, value in pair.items() if not key.endswith("_qpy_sha256")}

            _require(
                stable(restored_pair) == stable(report["circuit_pairs"][str(label)]), "archived pair report changed"
            )
        _require(
            runtime.fingerprint(circuits, fresh.backend.target, fresh.properties) == report["calibration_fingerprint"],
            "compiled calibration changed",
        )
        _require(
            repetition_delay(fresh.backend) == report["timing"]["repetition_delay_seconds"], "repetition delay changed"
        )
        # The 30 s value limits the mock request only; a physical case has no ceiling yet.
        sampler = runtime.configure_sampler(
            fresh.backend,
            "dynamic",
            False,
            None,
            ["gororoba-correction-native-preparation"],
            report["shots_per_pub"],
            30,
        )
        result["options"] = sampler.options.model_dump(mode="json")
        result["backend_dt_seconds"] = float(fresh.backend.dt)
        result["status"] = "attempted"
        _write(destination, result)
        _preserved(directory, report, record_hash)
        job = sampler.run(circuits, shots=report["shots_per_pub"], dry_run=True)
        result["job_id"] = job.job_id()
        result["status"] = "accepted"
        _write(destination, result)
        received = job.result()
        _require(len(received) == 4, "native result requires exactly four PUBs")
        timing = [pub.metadata["compilation"]["scheduler_timing"] for pub in received]
        result["timing"] = {name: entry for name, entry in zip(MEMBERS, timing, strict=True)}
        result["pairs"] = {
            str(label): correction_schedule.qualify_pair(
                timing[feedback],
                timing[known],
                dt_seconds=float(fresh.backend.dt),
                circuit_pair_report=report["circuit_pairs"][str(label)],
            )
            for label, feedback, known in ((1, 0, 1), (3, 3, 2))
        }
        _require(all(pair["qualified"] is True for pair in result["pairs"].values()), "pair schedule is unqualified")
        estimate = job.usage_estimation.get("quantum_seconds")
        _require(
            type(estimate) in (int, float) and math.isfinite(estimate) and estimate > 0,
            "native usage estimate is unavailable",
        )
        result["estimated_quantum_seconds"] = estimate
        result["estimate_semantics"] = "mock service estimate; actual charge and execution approval remain separate"
        _preserved(directory, report, record_hash)
        result.update(status="schedule_qualified_preparation_only", qualified=True)
    except Exception as error:
        result.update(status="unqualified", qualified=False, error_type=type(error).__name__)
        if isinstance(error, ValueError):
            result["reason"] = str(error)
    _write(destination, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True)
    parser.add_argument("--out", type=Path, required=True)
    qrng_seeds.add_seed_argument(parser, "--seed", default=20261010)
    parser.add_argument("--shots", type=int, default=8192)
    parser.add_argument("--model-shots", type=int, default=32768)
    parser.add_argument("--native-dry-run", action="store_true")
    args = parser.parse_args()
    correction_statistics.planning_certificate(args.shots)
    _require(args.seed >= 0 and args.model_shots > 0, "invalid seed or model shot count")
    service = ibm_account.open_service(QiskitRuntimeService)
    snapshot = live_run.take_snapshot(service, args.backend)
    _require(snapshot.ineligible_reason(None) is None, "backend is ineligible")
    directory = args.out / datetime.now(UTC).strftime("%Y-%m-%dT%H%M%S.%fZ")
    directory.mkdir(parents=True, exist_ok=False)
    try:
        report, files = build(snapshot, seed=args.seed, shots=args.shots, model_shots=args.model_shots)
        report["instance_sha256_12"] = live_run._instance_hash(service)
        if args.seed_source != "default":
            report["seed_source"] = qrng_seeds.seed_record(
                "gororoba_quantum/correction_preparation.py",
                "--seed",
                qrng_seeds.repo_relative(args.out),
                args.seed_source,
            )
        for name, data in files.items():
            (directory / name).write_bytes(data)
        _write(directory / "preparation.json", report)
        if args.native_dry_run:
            native = native_qualification(
                service, directory, expected_preparation_sha256=_hash((directory / "preparation.json").read_bytes())
            )
            print(f"native schedule: {native['status']}")
        print(f"preparation: {directory}")
    except Exception as error:
        _write(
            directory / "failure.json",
            {"state": "preparation_failed", "error_type": type(error).__name__, "physical_execution_authorized": False},
        )
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
