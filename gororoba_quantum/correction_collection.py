"""Gate correction decisions on retained integer shots and archived schedule pairs.

Collection binds the emitted scheduler table to each submitted physical circuit.
The statistical rule runs after the complete four-PUB order, single replicas,
8192-shot histograms and common unchanged execution calibration are established.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit

import correction_circuits
import correction_schedule
from correction_statistics import MEMBERS, analyze_counts

SHOTS = 8192


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def integer_counts(histogram: dict[str, int]) -> list[int]:
    """Decode the raw two-bit histogram without floating normalization or rounding."""
    _require(isinstance(histogram, dict) and bool(histogram), "raw histogram is missing")
    vector = [0, 0, 0, 0]
    for bits, count in histogram.items():
        _require(isinstance(bits, str) and re.fullmatch(r"[01]{2}", bits) is not None, "invalid two-bit outcome")
        _require(type(count) is int and count >= 0, "raw counts must be nonnegative Python integers")
        vector[int(bits, 2)] += count
    _require(sum(vector) == SHOTS, "correction member requires exactly 8192 raw shots")
    return vector


def retained_member(
    run_dir: Path,
    raw_record: dict[str, Any],
    *,
    job_id: str,
    pub_index: int,
    pub_manifest: dict[str, Any],
    member: str,
    circuit: QuantumCircuit,
    histogram: dict[str, int],
    dt_seconds: float | None,
) -> dict[str, Any]:
    """Read hashed raw PUB bytes and reconcile their shot-ordered bits with counts."""
    vector = integer_counts(histogram)
    _require(re.fullmatch(r"[A-Za-z0-9_-]+", job_id) is not None, "invalid retained job identity")
    _require(type(pub_index) is int and 0 <= pub_index < 4, "invalid correction PUB index")
    directory = f"raw/{job_id}"
    _require(raw_record["directory"] == directory, "retained raw directory differs from job identity")
    filename = f"pub_{pub_index:02d}.json"
    raw_bytes = (run_dir / directory / filename).read_bytes()
    digest = hashlib.sha256(raw_bytes).hexdigest()
    _require(raw_record["files"][filename] == digest, "retained raw PUB digest changed")
    raw = json.loads(raw_bytes)
    _require(raw["pub_index"] == pub_index and raw["pub_name"] == pub_manifest["name"], "raw PUB identity changed")
    components = pub_manifest["components"]
    _require(len(components) == 1 and components[0]["member"] == member, "correction PUB must contain one member")
    registers = components[0]["registers_by_replica"]
    _require(len(registers) == 1 and len(registers[0]) == 1, "correction member requires one replica and register")
    register_name = registers[0][0]
    _require(set(raw["registers"]) == {register_name}, "raw result register set differs from single replica")
    register = raw["registers"][register_name]
    _require(
        type(register["num_bits"]) is int
        and register["num_bits"] == 2
        and type(register["num_shots"]) is int
        and register["num_shots"] == SHOTS,
        "raw result register requires two bits and 8192 shots",
    )
    bits = register["bitstrings"]
    _require(isinstance(bits, list) and len(bits) == SHOTS, "raw shot-ordered register length changed")
    raw_histogram: dict[str, int] = {}
    for outcome in bits:
        _require(
            isinstance(outcome, str) and re.fullmatch(r"[01]{2}", outcome) is not None,
            "raw shot-ordered outcome must contain two bits",
        )
        raw_histogram[outcome] = raw_histogram.get(outcome, 0) + 1
    _require(integer_counts(raw_histogram) == vector, "integer histogram differs from retained shot-ordered bits")
    return {
        "name": member,
        "counts": vector,
        "circuit": circuit,
        "pub_manifest": pub_manifest,
        "pub_index": pub_index,
        "job_id": job_id,
        "backend": pub_manifest["backend"],
        "dt_seconds": dt_seconds,
        "timing": raw["metadata"].get("compilation", {}).get("scheduler_timing"),
        "raw_pub_sha256": digest,
    }


def analyze(
    record: dict[str, Any],
    evidence: list[dict[str, Any]] | None,
    executed: dict[str, Any],
    runtime: Any,
) -> dict[str, Any]:
    """Withhold the optimizer decision whenever its acquisition or timing gate fails."""
    result: dict[str, Any] = {
        "schema": "folded-correction-collected-decision-v1",
        "family": "folded-correction",
        "decision_available": False,
        "scientific_scope": "supplied odd-label witnesses; recorded-bit dependence with dispatch retained",
    }
    try:
        _require(record["family_configuration"]["name"] == "folded-correction", "incorrect correction family")
        _require(type(record["shots"]) is int and record["shots"] == SHOTS, "protocol requires 8192 shots per PUB")
        _require(
            isinstance(evidence, list) and len(evidence) == 4, "exactly four retained correction PUBs are required"
        )
        rows = list(evidence or [])
        _require([row["name"] for row in rows] == list(MEMBERS), "correction member order differs from protocol")
        errors = {row["name"]: row["error"] for row in rows if "error" in row}
        if errors:
            result["evidence_errors"] = errors
            raise ValueError("retained correction PUB evidence failed validation")
        submission = record["submission"]
        _require(submission.get("complete") is True, "correction acquisition is incomplete")
        jobs = submission["jobs"]
        planned = submission["planned_jobs"]
        _require(len(jobs) == len(planned) == 1, "correction acquisition requires exactly one job")
        job = jobs[0]
        _require(job["kind"] == planned[0]["kind"] == "dynamic", "correction job must retain dynamic dispatch")
        _require(job["members"] == planned[0]["members"] == list(MEMBERS), "job member order differs from protocol")
        _require(job["pubs"] == planned[0]["pubs"], "submitted PUB manifests differ from plan")
        _require([row["pub_index"] for row in rows] == list(range(4)), "retained PUB indices differ from order")
        _require([row["pub_manifest"] for row in rows] == job["pubs"], "retained PUB manifests differ from submission")
        _require(all(row["job_id"] == job["job_id"] for row in rows), "retained PUBs came from different jobs")
        _require(
            all(row["backend"] == job["backend"] == planned[0]["backend"] for row in rows),
            "retained PUB backend differs from submission",
        )
        _require(set(executed) == set(MEMBERS), "execution calibration evidence requires exactly four members")
        reason = runtime._comparisons_withheld(list(MEMBERS), executed)
        _require(reason is None, str(reason))
        _require(
            all(executed[name].get("calibration_changed_during_shots") is False for name in MEMBERS),
            "unchanged calibration is unestablished for a correction member",
        )
        for row in rows:
            manifest = row["pub_manifest"]
            circuit = row["circuit"]
            _require(executed[row["name"]]["pub"] == manifest["name"], "execution evidence names another PUB")
            runtime._validate_archived_pub(manifest, circuit, job["backend"], "dynamic")
            _require(len(manifest["components"]) == 1, "correction PUB has multiple components")
            component = manifest["components"][0]
            _require(
                component["member"] == row["name"] and component["reference"] is False, "invalid correction component"
            )
            _require(len(component["registers_by_replica"]) == 1, "correction member has multiple replicas")
            _require(circuit.num_clbits == 2, "archived correction circuit must retain two measured bits")
            _require(re.fullmatch(r"[0-9a-f]{64}", row["raw_pub_sha256"]) is not None, "raw PUB digest is unavailable")
        dt_seconds = rows[0]["dt_seconds"]
        _require(
            type(dt_seconds) in (int, float) and math.isfinite(dt_seconds) and dt_seconds > 0,
            "execution-time backend dt is unavailable",
        )
        _require(all(row["dt_seconds"] == dt_seconds for row in rows), "execution-time backend dt changed")
        pairs = {}
        for label, feedback, independent in ((1, 0, 1), (3, 3, 2)):
            circuit_report = correction_circuits.validate_bound_correction_pair(
                rows[feedback]["circuit"], rows[independent]["circuit"], label
            )
            pairs[str(label)] = correction_schedule.qualify_pair(
                rows[feedback]["timing"],
                rows[independent]["timing"],
                dt_seconds=dt_seconds,
                circuit_pair_report=circuit_report,
            )
            _require(pairs[str(label)]["qualified"] is True, "correction pair schedule is unqualified")
        counts = {row["name"]: row["counts"] for row in rows}
        decision = analyze_counts(counts, expected_shots=SHOTS, alpha=0.05, minimum_gain=0.01)
        result.update(
            decision_available=True,
            integer_counts=counts,
            schedule_pairs=pairs,
            statistical_decision=decision,
            raw_pub_sha256={row["name"]: row["raw_pub_sha256"] for row in rows},
            calibration=executed[MEMBERS[0]]["calibration"],
            job_id=job["job_id"],
            backend=job["backend"],
        )
    except (ValueError, KeyError, TypeError, IndexError, AttributeError, RuntimeError) as error:
        result["withheld"] = f"correction acquisition or schedule evidence: {error}"
    return result
