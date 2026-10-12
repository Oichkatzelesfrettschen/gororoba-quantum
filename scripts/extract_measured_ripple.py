"""Extract hash-bound, portable observations from collected static algebra runs.

Raw shot order defines joint observations only inside a single PUB. Preparation
predictions and execution-calibration replay remain separate model views. The
extractor reads retained files only; it never creates a service or changes raw
records. New output files are installed atomically without replacing a path.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import re
import sys
import tempfile
from datetime import datetime
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import qpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import live_run as runtime  # noqa: E402
import qpu_planning  # noqa: E402
from cd_core import cd_sign  # noqa: E402
from rank_sector_experiments import reference_probes, sector_probes  # noqa: E402

SCHEMA = "measured-static-algebra-extraction-v1"
FIXTURE_MARKER = "synthetic_fixture"
BLOCK_SHOTS = 512


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def decode(contents: bytes) -> Any:
    return json.loads(contents, object_pairs_hook=_object_pairs)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def digest(contents: bytes) -> str:
    return hashlib.sha256(contents).hexdigest()


def _sha(value: Any) -> str:
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None, "invalid SHA-256")
    return str(value)


def _integer(value: Any, label: str, minimum: int = 1) -> int:
    require(type(value) is int and value >= minimum, f"{label} must be an integer >= {minimum}")
    return int(value)


def probabilities(value: Any, width: int, label: str, tolerance: float = 1e-9) -> list[float]:
    require(isinstance(value, list) and len(value) == width, f"{label}: probability width differs")
    require(
        all(type(item) in (int, float) and math.isfinite(item) and 0 <= item <= 1 for item in value),
        f"{label}: invalid probability",
    )
    require(abs(math.fsum(value) - 1) <= tolerance, f"{label}: probability mass differs")
    return list(map(float, value))


class Inputs:
    """Retain relative identities and reject movement during extraction."""

    def __init__(self, root: Path):
        self.root = root.resolve(strict=True)
        require(self.root.is_dir(), "run input must be a directory")
        self.hashes: dict[str, str] = {}

    def read(self, relative: str, expected: str | None = None) -> bytes:
        path = self.root / relative
        require(path.resolve().is_relative_to(self.root), "input link leaves the run directory")
        require(path.is_file(), f"missing input file {relative}")
        contents = path.read_bytes()
        identity = digest(contents)
        require(expected is None or identity == _sha(expected), f"input hash mismatch: {relative}")
        require(relative not in self.hashes or self.hashes[relative] == identity, f"input changed: {relative}")
        self.hashes[relative] = identity
        return contents

    def json(self, relative: str, expected: str | None = None) -> Any:
        return decode(self.read(relative, expected))

    def verify_unchanged(self) -> None:
        for relative, expected in list(self.hashes.items()):
            self.read(relative, expected)


def validate_output(run_dir: Path, output: Path, *, check: bool = False) -> None:
    """Reject directory, symbolic, and hard-link input aliases before parsing."""
    root = run_dir.resolve()
    destination = output.resolve()
    require(not destination.is_relative_to(root), "output must remain outside the input run directory")
    require(not output.is_dir(), "output must be a file outside the input directory")
    if output.exists():
        for source in run_dir.rglob("*"):
            if source.is_file():
                require(not output.samefile(source), "output aliases an input file")
        require(check, "output already exists; use --check or choose a new output")
    elif output.is_symlink():
        raise ValueError("output must be a new regular path")


def _acquisition_marker(value: Any, synthetic: bool) -> None:
    """Keep explicit fixture and server-mock markers outside hardware evidence."""
    if isinstance(value, dict):
        require(value.get("dry_run") is not True, "server mock data is excluded")
        marker = value.get("evidence_kind")
        if marker is not None:
            require(marker in ("collected_hardware", FIXTURE_MARKER), "unsupported acquisition marker")
            require((marker == FIXTURE_MARKER) == synthetic, "acquisition marker differs from evidence kind")
        for child in value.values():
            _acquisition_marker(child, synthetic)
    elif isinstance(value, list):
        for child in value:
            _acquisition_marker(child, synthetic)


def _metadata(record: dict[str, Any], members: dict[str, Any]) -> dict[str, dict[str, Any]]:
    config = record["family_configuration"]
    family = config["name"]
    if family == "ripple":
        result = config["members"]
        require(set(result) == set(members), "ripple metadata member coverage differs")
        canonical_atlas = set()
        for name, item in result.items():
            require(item["group"] == members[name]["group"], "metadata group differs")
            if item["kind"] == "atlas" and item["role"] != "readout":
                kite = _integer(item["kite"], "kite")
                require(kite <= 7 and type(item["sign"]) is int and item["sign"] in (-1, 1), "invalid kite sign")
                low = [index for index in range(1, 8) if index != kite]
                edges = [(left, right) for left, right in combinations(low, 2) if left ^ right != kite]
                edge = _integer(item["edge_index"], "edge index", 0)
                require(edge < len(edges) and (item["source"], item["target"]) == edges[edge], "kite edge differs")
                left, right = edges[edge]
                sign = -cd_sign(16, left, right) * cd_sign(16, left ^ (8 ^ kite), right ^ (8 ^ kite))
                require(item["sign"] == sign, "certified box-kite sign differs")
                phase = _integer(item["phase_index"], "phase index", 0)
                require(phase < 8, "phase index outside eight-point sweep")
                ideal = (1 - sign * math.cos(phase * math.pi / 4)) / 2
                require(abs(members[name]["ideal"][0] - ideal) < 1e-10, "atlas ideal differs from signed fringe")
                if item["role"] == "atlas":
                    require((kite, edge, phase) not in canonical_atlas, "duplicate canonical atlas point")
                    canonical_atlas.add((kite, edge, phase))
        require(len(canonical_atlas) == 672, "canonical atlas requires all 672 phase points")
        rows = config["rows"]
        require([row["row"] for row in rows] == list(range(len(rows))), "execution row indices differ")
        flat = [name for row in rows for name in row["members"]]
        require(len(flat) == len(set(flat)) and set(flat) == set(result), "execution row member coverage differs")
        for row in rows:
            require(all(result[name]["execution_row"] == row["row"] for name in row["members"]), "member row differs")
        return result
    require(family == "rank-sector", "extractor requires a ripple or rank-sector family")
    require(config["schema"] == "rank-sector-four-qubit-lcu-v1", "unsupported rank-sector schema")
    parameters = [Fraction(value) for value in config["parameters"]]
    require(
        parameters == [Fraction(0), Fraction(1, 2), Fraction(1), Fraction(3, 2), Fraction(2)], "rank parameters differ"
    )
    result = {}
    require([sector["sector"] for sector in config["sectors"]] == list(range(8)), "rank sector coverage differs")
    for sector in config["sectors"]:
        index = sector["sector"]
        require(
            sector["probes"]
            == [{"name": probe.name, "coordinates": list(probe.coordinates)} for probe in sector_probes(index)],
            "rank probe coordinates differ from the certified frame",
        )
        require(
            sector["reference_probes_at_one"] == list(reference_probes(index)), "rank isolated probe identities differ"
        )
        exact = {row["member"]: row["probability"] for row in sector["exact_probabilities"]}
        require(len(exact) == len(sector["exact_probabilities"]) == 20, "rank exact probability coverage differs")
        require(len(sector["probes"]) == 4, "rank sector requires four probes")
        for probe_index, probe in enumerate(sector["probes"]):
            coordinates = probe["coordinates"]
            require(
                len(coordinates) == 4 and all(type(value) is int for value in coordinates), "invalid probe coordinates"
            )
            probe_norm = sum(value * value for value in coordinates)
            require(probe_norm > 0, "zero probe")
            for parameter_index, parameter in enumerate(parameters):
                name = f"rank_sector_{index}_{probe['name']}_t{parameter.numerator}d{parameter.denominator}"
                require(name in members and name in exact, "rank member identity differs")
                probability = Fraction(exact[name])
                require(0 <= probability <= 1, "rank exact probability outside [0,1]")
                require(abs(members[name]["ideal"][0] - float(probability)) < 1e-10, "rank exact ideal differs")
                alpha = Fraction(2) if parameter <= 1 else parameter * parameter - parameter + 2
                metadata = {
                    "kind": "rank-sector",
                    "role": "packed",
                    "sector": index,
                    "probe": probe["name"],
                    "parameter_exact": str(parameter),
                    "probe_coordinates": coordinates,
                    "execution_row": probe_index * 5 + parameter_index,
                    "ideal_success_exact": str(probability),
                    "alpha_exact": str(alpha),
                    "unit_probe_norm_factor_exact": str(alpha * alpha),
                    "unnormalized_probe_norm_factor_exact": str(alpha * alpha * probe_norm),
                }
                result[name] = metadata
                if parameter == 1 and probe["name"] in sector["reference_probes_at_one"]:
                    reference = name + "_reference"
                    require(reference in members, "rank isolated reference is absent")
                    result[reference] = metadata | {
                        "role": "isolated",
                        "packed_member": name,
                        "execution_row": 20 + 2 * index + sector["reference_probes_at_one"].index(probe["name"]),
                    }
    require(set(result) == set(members), "rank metadata member coverage differs")
    return result


def _execution(entry: dict[str, Any] | None, pub: str, shots: int) -> dict[str, Any]:
    if entry is None:
        return {
            "pub": pub,
            "shots": shots,
            "start": None,
            "stop": None,
            "calibration": None,
            "calibration_changed_during_shots": None,
            "window_unavailable_reason": "collector execution absent",
        }
    require(entry["pub"] == pub and entry.get("shots", shots) == shots, "collector execution identity or shots differ")
    changed = entry["calibration_changed_during_shots"]
    require(changed is None or type(changed) is bool, "invalid calibration change flag")
    if entry["calibration"] is not None:
        start, stop = datetime.fromisoformat(entry["start"]), datetime.fromisoformat(entry["stop"])
        calibration = datetime.fromisoformat(entry["calibration"])
        require(start.tzinfo is not None and stop.tzinfo is not None and stop >= start, "invalid execution window")
        require(calibration.tzinfo is not None and type(changed) is bool, "invalid calibration evidence")
    else:
        require(entry.get("start") is None and entry.get("stop") is None, "unknown calibration has an execution window")
    return {
        key: entry.get(key)
        for key in (
            "pub",
            "start",
            "stop",
            "calibration",
            "calibration_changed_during_shots",
            "window_unavailable_reason",
        )
    } | {"shots": shots}


def _vectors(raw: dict[str, Any], component: dict[str, Any], circuit: Any, shots: int) -> np.ndarray:
    registers = component["registers_by_replica"]
    require(len(registers) == 1, "static algebra requires one replica per lane")
    widths = {register.name: register.size for register in circuit.cregs}
    value = np.zeros(shots, dtype=np.int64)
    offset = 0
    for name in registers[0]:
        register = raw["registers"][name]
        width = _integer(register["num_bits"], "raw register width")
        require(width == widths[name] and width + offset <= 16, "raw register width differs from supported QPY")
        require(type(register["num_shots"]) is int and register["num_shots"] == shots, "raw shot count differs")
        bits = register["bitstrings"]
        require(isinstance(bits, list) and len(bits) == shots, "raw shot vector length differs")
        require(
            all(isinstance(item, str) and re.fullmatch(rf"[01]{{{width}}}", item) for item in bits), "invalid raw bits"
        )
        value |= np.fromiter((int(item, 2) for item in bits), dtype=np.int64, count=shots) << offset
        offset += width
    return value


def _dependence(events: list[np.ndarray], names: list[str]) -> dict[str, Any]:
    if not events:
        return {"members": [], "joint_probabilities": [], "covariance": []}
    matrix = np.asarray(events, dtype=float)
    means = matrix.mean(axis=1)
    joint = matrix @ matrix.T / matrix.shape[1]
    return {
        "members": names,
        "joint_probabilities": joint.tolist(),
        "covariance": (joint - np.outer(means, means)).tolist(),
    }


def _check_analysis(
    record: dict[str, Any], header: dict[str, Any], measured: dict[str, Any], executed: dict[str, Any]
) -> Any:
    retained = header.get("family_analysis")
    if retained is None:
        return {"withheld": "collector family analysis is absent"}
    expected = qpu_planning.measured_family(record, measured, executed, runtime)
    require(canonical(retained) == canonical(expected), "retained endpoint intervals or calibration withholding differ")
    return retained


def extract_run(run_dir: Path, *, fixture_mode: bool = False) -> dict[str, Any]:
    """Validate an admitted collection; fixture mode remains a private test surface."""
    inputs = Inputs(run_dir)
    record = inputs.json("record.json")
    require(record.get("evidence_kind") in (None, "collected_hardware", FIXTURE_MARKER), "unsupported acquisition kind")
    synthetic = record.get("evidence_kind") == FIXTURE_MARKER
    require(fixture_mode == synthetic, "synthetic fixture requires explicit private fixture mode")
    _acquisition_marker(record, synthetic)
    require(
        record.get("dry_run") is not True and record.get("evidence_kind") != "server_mock_timing", "mock acquisition"
    )
    require(
        record["state"] == "submitted" and record["budget_plan"]["admitted"] is True,
        "run is not an admitted submission",
    )
    require(record["code_commit"]["sources_modified"] is False, "submission source is modified")
    _sha(record["experiment_digest"])
    require(record["schema_version"] == runtime.RECORD_SCHEMA_VERSION, "unsupported record schema")
    require(record["schema_contract"] == runtime.RECORD_SCHEMA_CONTRACT, "unsupported record contract")
    require(record["approved_record"]["mismatches"] == [], "approved record has mismatches")
    _sha(record["approved_record"]["record_sha256"])
    require(record["approval_consumed"]["run"] == record["started"], "approval consumption belongs to another run")
    submission = record["submission"]
    require(submission["complete"] is True and bool(submission["jobs"]), "submission is incomplete")
    require(runtime.submission_gaps(submission) == ([], [], []), "submission ledger has gaps")
    qpy_digest = _sha(submission["qpy_archive_sha256"])
    require(record["approved_record"]["qpy_archive_sha256"] == qpy_digest, "approved QPY identity differs")
    circuits = list(qpy.load(io.BytesIO(inputs.read("isa.qpy", qpy_digest))))
    by_circuit = {circuit.name: circuit for circuit in circuits}
    require(len(by_circuit) == len(circuits), "duplicate QPY circuit name")
    pubs = {pub["name"]: pub for pub in record["execution_pubs"]}
    require(
        len(pubs) == len(record["execution_pubs"]) and set(pubs) == set(by_circuit), "record/QPY PUB coverage differs"
    )
    planned = {pub["name"]: pub for job in submission["planned_jobs"] for pub in job["pubs"]}
    require(planned == pubs, "planned PUB manifests differ from the record")
    collection = inputs.json("collect.json")
    require(isinstance(collection, list) and bool(collection), "collection header absent")
    _acquisition_marker(collection, synthetic)
    header = collection[0]
    require(header["submission_complete"] is True, "collection is incomplete")
    jobs = submission["jobs"]
    require(set(header["jobs"]) == {job["job_id"] for job in jobs}, "collected job coverage differs")
    members = {}
    for group in record["groups"]:
        for member in group["members"]:
            require(member["name"] not in members, "duplicate record member")
            members[member["name"]] = member | {
                "group": group["group"],
                "model_calibration": group["noise_model_calibration"],
            }
    metadata = _metadata(record, members)
    require(len(pubs) == record["family_configuration"]["execution_row_count"], "family execution row count differs")
    family_header = header.get("family_measurements")
    if family_header is not None:
        require(set(family_header) == set(members), "family header member coverage differs")
    old_measured, old_executed = {}, {}
    for group in collection[1:]:
        for name, value in group.get("executed", {}).items():
            require(name not in old_executed, "collection repeats an executed member")
            old_executed[name] = value
        old_measured.update(group.get("measured", {}))
    output_members: dict[str, Any] = {}
    measured: dict[str, Any] = {}
    executed: dict[str, Any] = {}
    output_pubs = []
    used_rows: set[int] = set()
    charges: list[float | None] = []
    pub_shots = member_shots = active_qubit_shots = reserved_qubit_shots = 0
    for job in jobs:
        job_id = job["job_id"]
        require(isinstance(job_id, str) and re.fullmatch(r"[A-Za-z0-9_-]+", job_id) is not None, "invalid job identity")
        require(job["kind"] == "static", "static algebra job has another execution kind")
        shots = runtime._recorded_job_shots(record, job)
        job_collection = header["jobs"][job_id]
        require(
            job_collection["backend"] == job["backend"] and job_collection["kind"] == "static", "job identity differs"
        )
        usage = job_collection["usage"]
        require(
            usage["job_status"] == "DONE" and usage["submitted_pub_shots"] == len(job["pubs"]) * shots,
            "job usage differs",
        )
        charge = usage.get("qpu_charge_time_seconds") if usage.get("usage_status") == "final" else None
        if charge is not None:
            require(type(charge) in (str, float, int), "invalid retained charge")
            charge = float(charge)
            require(math.isfinite(charge) and charge >= 0, "invalid retained charge")
        raw_prefix = f"raw/{job_id}"
        index = inputs.json(raw_prefix + "/index.json")
        require(index["job_id"] == job_id, "raw index job identity differs")
        files = index["files"]
        expected_files = {f"pub_{position:02d}.json" for position in range(len(job["pubs"]))} | {"result_metadata.json"}
        require(set(files) == expected_files, "raw indexed file coverage differs")
        require(job_collection["raw"] == {"directory": raw_prefix, "files": files}, "collector raw identities differ")
        result_metadata = inputs.json(raw_prefix + "/result_metadata.json", files["result_metadata.json"])
        _acquisition_marker(result_metadata, synthetic)
        snapshots, snapshot_hashes = index.get("metrics", []), index.get("metrics_sha256", [])
        require(
            len(snapshots) == len(snapshot_hashes) and len(set(snapshots)) == len(snapshots), "metrics index differs"
        )
        metrics_by_name = {}
        for filename, expected in zip(snapshots, snapshot_hashes, strict=True):
            require(re.fullmatch(r"job_metrics(?:\.[0-9]+)?\.json", filename) is not None, "invalid metrics filename")
            metrics_by_name[filename] = inputs.json(raw_prefix + "/" + filename, expected)
        latest_name = index.get("metrics_latest", snapshots[-1] if snapshots else None)
        require(latest_name is None or latest_name in metrics_by_name, "latest metrics identity differs")
        settled = metrics_by_name.get(latest_name, {}).get("usage", {})
        if settled.get("status") in ("complete", "completed") and settled.get("qpu_charge_time_seconds") is not None:
            raw_charge = settled["qpu_charge_time_seconds"]
            require(
                type(raw_charge) in (int, float) and math.isfinite(raw_charge) and raw_charge >= 0, "invalid raw charge"
            )
            if charge is not None:
                require(charge == raw_charge, "collector charge differs from settled raw usage")
        else:
            charge = None
        charges.append(charge)
        for position, pub in enumerate(job["pubs"]):
            require(pub == pubs[pub["name"]], "submitted manifest differs")
            circuit = by_circuit[pub["name"]]
            runtime._validate_archived_pub(pub, circuit, job["backend"], "static")
            filename = f"pub_{position:02d}.json"
            raw = inputs.json(raw_prefix + "/" + filename, files[filename])
            _acquisition_marker(raw["metadata"], synthetic)
            require(raw["pub_name"] == pub["name"] and raw["pub_index"] == position, "raw PUB identity differs")
            require(
                set(raw["registers"]) == {register.name for register in circuit.cregs}, "raw register coverage differs"
            )
            components = pub["components"]
            rows = {metadata[component["member"]]["execution_row"] for component in components}
            require(len(rows) == 1 and not used_rows.intersection(rows), "PUB row identity differs")
            row = rows.pop()
            expected_members = {name for name, item in metadata.items() if item["execution_row"] == row}
            require(
                {component["member"] for component in components} == expected_members, "PUB row member coverage differs"
            )
            used_rows.add(row)
            event_vectors, event_names, error_vectors, error_names = [], [], [], []
            for component in components:
                name = component["member"]
                require(name not in output_members and name in members, "duplicate or unknown submitted member")
                source = members[name]
                require(component["group"] == source["group"], "component group differs")
                require(
                    len(source["replicas"]) == len(source["replica_qubits"]) == 1, "static member replica count differs"
                )
                require(
                    sorted(source["replica_qubits"][0]) == component["physical_qubits"],
                    "member physical footprint differs",
                )
                values = _vectors(raw, component, circuit, shots)
                width = 1 << sum(
                    raw["registers"][register]["num_bits"] for register in component["registers_by_replica"][0]
                )
                counts = np.bincount(values, minlength=width)
                distribution = counts / shots
                ideal = probabilities(source["ideal"], width, "ideal", 1e-10)
                model = probabilities(source["replicas"][0]["noisy"], width, "preparation model", 1e-5)
                item = family_header[name] if family_header is not None else None
                witness = item["execution"] if item is not None else old_executed.get(name)
                execution = _execution(witness, pub["name"], shots)
                executed[name] = execution
                if name in old_executed:
                    require(
                        _execution(old_executed[name], pub["name"], shots) == execution,
                        "collector execution views differ",
                    )
                observed = item["replica_probabilities"] if item is not None else old_measured.get(name)
                require(observed is not None and len(observed) == 1, "collector marginal absent")
                retained = probabilities(list(observed or [])[0], width, "collected marginal", 1e-5)
                tolerance = 1e-12 if item is not None else 5.1e-7
                require(
                    np.max(np.abs(distribution - retained)) <= tolerance, "collected marginal differs from raw counts"
                )
                replay, replay_status = None, "collector_replay_vector_absent"
                if item is not None:
                    replay_status = item["replay_status"]
                    replay = item["replayed_replica_probabilities"]
                    expected_status = (
                        "calibration_changed_during_shots"
                        if execution["calibration_changed_during_shots"]
                        else (
                            "calibration_bound"
                            if execution["calibration"] is not None
                            else "execution_window_unavailable"
                        )
                    )
                    require(replay_status == expected_status, "replay status differs from execution calibration")
                    if replay_status == "calibration_bound":
                        require(isinstance(replay, list) and len(replay) == 1, "calibration replay vector absent")
                        replay = probabilities(replay[0], width, "execution replay")
                    else:
                        require(replay is None, "unavailable calibration carries replay probabilities")
                measured[name] = [distribution]
                events = (values == 0).astype(float)
                event_vectors.append(events)
                event_names.append(name)
                deterministic = next((index for index, probability in enumerate(ideal) if probability == 1.0), None)
                if deterministic is not None:
                    error_vectors.append((values != deterministic).astype(float))
                    error_names.append(name)
                blocks = [
                    {
                        "start_shot": start,
                        "stop_shot_exclusive": min(start + BLOCK_SHOTS, shots),
                        "shots": len(values[start : start + BLOCK_SHOTS]),
                        "event_zero_probability": float(events[start : start + BLOCK_SHOTS].mean()),
                    }
                    for start in range(0, shots, BLOCK_SHOTS)
                ]
                output_members[name] = {
                    "metadata": metadata[name],
                    "group": source["group"],
                    "job_id": job_id,
                    "pub": pub["name"],
                    "pub_index": position,
                    "shots": shots,
                    "registers": component["registers_by_replica"][0],
                    "physical_qubits": component["physical_qubits"],
                    "counts": counts.tolist(),
                    "probabilities": distribution.tolist(),
                    "ideal_probabilities": ideal,
                    "preparation_model": {"probabilities": model, "calibration": source["model_calibration"]},
                    "execution": execution,
                    "execution_replay": {"status": replay_status, "probabilities": replay},
                    "hardware_minus_ideal": (distribution - ideal).tolist(),
                    "hardware_minus_preparation_model": (distribution - model).tolist(),
                    "hardware_minus_execution_replay": (distribution - replay).tolist() if replay is not None else None,
                    "shot_order_blocks": blocks,
                }
            active = sorted(
                {circuit.find_bit(qubit).index for instruction in circuit.data for qubit in instruction.qubits}
            )
            reserved = sorted({qubit for component in components for qubit in component["physical_qubits"]})
            output_pubs.append(
                {
                    "job_id": job_id,
                    "name": pub["name"],
                    "row": row,
                    "shots": shots,
                    "active_physical_qubits": active,
                    "replica_stream_count": sum(len(component["registers_by_replica"]) for component in components),
                    "reserved_physical_qubits": reserved,
                    "event_zero": _dependence(event_vectors, event_names),
                    "deterministic_error": _dependence(error_vectors, error_names),
                    "raw_sha256": files[filename],
                }
            )
            pub_shots += shots
            member_shots += shots * len(components)
            active_qubit_shots += shots * len(active)
            reserved_qubit_shots += shots * len(reserved)
    require(set(output_members) == set(members), "submitted member coverage differs")
    require(used_rows == set(range(len(pubs))), "submitted execution row coverage differs")
    endpoints = _check_analysis(record, header, measured, executed)
    complete_charge = all(charge is not None for charge in charges)
    total_charge = math.fsum(charge for charge in charges if charge is not None) if complete_charge else None
    totals = {
        "physical_pub_shots": pub_shots,
        "logical_member_shots": member_shots,
        "unique_active_qubit_shots": active_qubit_shots,
        "unique_reserved_qubit_shots": reserved_qubit_shots,
    }
    inputs.verify_unchanged()
    result = {
        "schema": SCHEMA,
        "evidence_kind": FIXTURE_MARKER if synthetic else "collected_hardware",
        "family": record["family_configuration"]["name"],
        "source_files": inputs.hashes,
        "experiment_digest": record["experiment_digest"],
        "source_commit": record["code_commit"]["head"],
        "analysis_sources": {
            "extractor_sha256": digest(Path(__file__).read_bytes()),
            "runtime_experiment_digest": runtime.experiment_digest(),
        },
        "members": output_members,
        "pubs": output_pubs,
        "endpoint_analysis": endpoints,
        "observable_contracts": record.get("observable_contracts", []),
        "throughput": totals
        | {
            "scope": "occupancy and sampling throughput; physical PUB-shots remain the vendor sampling unit",
            "replica_stream_shots": member_shots,
            "fidelity_goodput": None,
            "covariance_adjusted_goodput": None,
            "goodput_withheld": "a scientifically justified independent-evidence or fidelity unit is undefined",
            "retained_collector_charge_seconds": total_charge,
            "rates_per_charged_second": {key: value / total_charge for key, value in totals.items()}
            if total_charge is not None and total_charge > 0
            else None,
            "rates_withheld": None
            if total_charge is not None and total_charge > 0
            else "complete positive final charge is unavailable",
        },
        "interpretation": [
            "Joint event covariance uses same-PUB shot positions; different PUBs and jobs have no paired observations.",
            "Deterministic errors exist only when the declared ideal outcome has probability one.",
            "Shot-order blocks are descriptive index windows, not per-shot wall-clock timestamps or drift tests.",
            "Residuals are descriptive; hardware alone does not identify model error or finite simulation uncertainty.",
            "Basis probabilities do not establish state fidelity, amplitude phases, or crosstalk causality.",
            "Qubit-shot totals count each distinct active or reserved physical qubit once per PUB shot.",
        ],
    }
    result["payload_sha256"] = digest(canonical(result))
    return result


def read_artifact(path: Path) -> dict[str, Any]:
    result = decode(path.read_bytes())
    require(isinstance(result, dict) and result.get("schema") == SCHEMA, "unsupported extraction schema")
    expected = _sha(result.get("payload_sha256"))
    require(
        digest(canonical({key: value for key, value in result.items() if key != "payload_sha256"})) == expected,
        "extraction payload hash differs",
    )
    require(result["evidence_kind"] in ("collected_hardware", FIXTURE_MARKER), "unsupported evidence kind")
    return result


def write_new(output: Path, payload: bytes) -> None:
    """Install a complete file by link without replacing an existing destination."""
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".measured-algebra-", dir=output.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, output)
    finally:
        Path(temporary).unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--run", type=Path)
    source.add_argument("--read", type=Path, help="Validate and print a portable extraction without reading run inputs")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", action="store_true", help="Recompute and compare an existing output without writing")
    args = parser.parse_args()
    try:
        if args.read is not None:
            require(args.out is None and not args.check, "--read excludes --out and --check")
            sys.stdout.buffer.write(canonical(read_artifact(args.read)))
            return 0
        require(args.out is not None, "--run requires --out")
        validate_output(args.run, args.out, check=args.check)
        result = extract_run(args.run)
        payload = canonical(result)
        if args.check:
            require(args.out.is_file() and args.out.read_bytes() == payload, "output differs from validated extraction")
        else:
            validate_output(args.run, args.out)
            write_new(args.out, payload)
    except (ValueError, KeyError, TypeError, IndexError, OSError, runtime.LiveRunError) as error:
        print(f"measured extraction: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
