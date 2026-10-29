"""Freeze bounded Tuna register qualification; retain failed screens as evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

MANIFEST_SHA256 = "d9a41a677a2a4bff4e2d3f4e10c4db2017d41ba1ee910da67960333d151dcfb2"
FILES = ("readout-zero.cq", "readout-one.cq", "geometry.cq")
TRIPLES = ((1, 4, 8), (13, 11, 14), (3, 6, 9))
SHOTS = 4096


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_metadata(metadata: dict[str, Any]) -> None:
    if metadata.get("width") != 20 or metadata.get("bit_order") != "classical bit zero is the rightmost character":
        raise ValueError("qualification requires width 20 and rightmost classical bit zero")
    if metadata.get("index_convention") != "zero-based string offsets from the left":
        raise ValueError("qualification requires left-based string offsets")
    replicas = metadata.get("replicas", [])
    if len(replicas) != 3:
        raise ValueError("qualification requires three replicas")
    for index, (replica, triple, angle) in enumerate(zip(replicas, TRIPLES, (0, 45, 90), strict=True)):
        expected = {
            "data": 19 - triple[0],
            "herald": 2 - index,
            "final_herald": 19 - triple[1],
            "physical_triple_a_c_b": list(triple),
            "angle_degrees": angle,
            "endpoint": "z",
        }
        if any(replica.get(key) != value for key, value in expected.items()):
            raise ValueError("qualification metadata differs from the frozen physical bit map")


def shot_counts(arguments: tuple[str, list[str]]) -> dict[str, Any]:
    filename, shots = arguments
    if len(shots) != SHOTS or any(type(shot) is not str or len(shot) != 20 or set(shot) - {"0", "1"} for shot in shots):
        raise ValueError("qualification requires 4096 width-20 binary shot strings")
    bits = np.array([list(shot) for shot in shots], dtype=np.int8)
    return {
        "file": filename,
        "ones": bits.sum(axis=0).tolist(),
        "disagreements": (bits[:, [2, 1, 0]] != bits[:, [15, 8, 13]]).sum(axis=0).tolist(),
    }


def screen(counts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Use exact integer boundaries: contrast >= 1/2; disagreement <= 1/10."""
    if set(counts) != set(FILES):
        raise ValueError("qualification requires exactly the three frozen circuits")
    active = {qubit for triple in TRIPLES for qubit in triple}
    contrasts = []
    for bit in range(20):
        difference = counts[FILES[1]]["ones"][19 - bit] - counts[FILES[0]]["ones"][19 - bit]
        contrasts.append(
            {
                "classical_bit": bit,
                "difference_count": difference,
                "shots_per_arm": SHOTS,
                "required": bit in active or bit >= 17,
                "passed": difference * 2 >= SHOTS,
            }
        )
    disagreements = [
        {"file": filename, "ancilla_qubit": triple[1], "count": count, "shots": SHOTS, "passed": count * 10 <= SHOTS}
        for filename in FILES
        for triple, count in zip(TRIPLES, counts[filename]["disagreements"], strict=True)
    ]
    return {
        "assignment_contrasts": contrasts,
        "early_final_disagreements": disagreements,
        "passed": all(row["passed"] for row in contrasts if row["required"])
        and all(row["passed"] for row in disagreements),
    }


def replay(run: Path) -> dict[str, Any]:
    manifest_path = run / "cases.json"
    if digest(manifest_path) != MANIFEST_SHA256:
        raise ValueError("manifest differs from the frozen Tuna qualification")
    manifest = json.loads(manifest_path.read_text())
    submission = json.loads((run / "submission.json").read_text())
    collection = json.loads((run / "results.json").read_text())
    if (
        submission.get("state") != "enqueued"
        or submission.get("backend_type_id") != 7
        or submission.get("backend") != "tuna_17"
        or submission.get("shots") != SHOTS
        or submission.get("cases_sha256") != MANIFEST_SHA256
    ):
        raise ValueError("submission identity differs from the frozen qualification")
    submitted = submission["jobs"]
    collected = collection["jobs"]
    if (
        len(submitted) != 3
        or len(collected) != 3
        or {row["file"] for row in submitted} != set(FILES)
        or {row["file"] for row in collected} != set(FILES)
    ):
        raise ValueError("submission and collection require exactly three distinct named jobs")
    job_ids = [row["job"] for row in submitted]
    if any(type(job) is not int or job <= 0 for job in job_ids) or len(set(job_ids)) != 3:
        raise ValueError("submission requires three distinct positive job identifiers")
    inputs = [manifest_path, run / "submission.json", run / "results.json"]
    sources = {row["file"]: row for row in manifest["circuits"]}
    collected_by_file = {row["file"]: row for row in collected}
    shot_arguments = []
    executions = []
    identities = []
    for row in submitted:
        filename = row["file"]
        source = sources[filename]
        validate_metadata(source["analysis_metadata"])
        source_path = run / filename
        if digest(source_path) != source["sha256"] or row["sha256"] != source["sha256"]:
            raise ValueError("submitted circuit differs from the manifest digest")
        retained = collected_by_file[filename]
        job = retained["job"]
        if (
            job["id"] != row["job"]
            or job["batch_job_id"] != submission["batch_job"]
            or job["status"] != "completed"
            or job["number_of_shots"] != SHOTS
            or job["raw_data_enabled"] is not True
            or len(retained["results"]) != 1
        ):
            raise ValueError("collection requires matching completed full-shot raw-enabled jobs")
        result = retained["results"][0]
        if result["job_id"] != row["job"] or result["shots_requested"] != SHOTS or result["shots_done"] != SHOTS:
            raise ValueError("result identity or shot count differs from submission")
        raw_path = run / "raw" / f"{filename}.json"
        shots = json.loads(raw_path.read_text())
        if not isinstance(shots, list) or any(type(shot) is not str for shot in shots):
            raise ValueError("raw outcomes must be an ordered string list")
        histogram = result["results"]
        if (
            any(type(value) is not int or value <= 0 for value in histogram.values())
            or dict(Counter(shots)) != histogram
        ):
            raise ValueError("raw histogram differs from result histogram")
        execution = Decimal(str(result["execution_time_in_seconds"]))
        if not execution.is_finite() or execution < 0 or execution > 300:
            raise ValueError("execution time exceeds the finite nonnegative 300-second per-job boundary")
        executions.append(execution)
        identities.append({"file": filename, "job": row["job"], "execution_seconds_decimal": str(execution)})
        shot_arguments.append((filename, shots))
        inputs.extend((source_path, raw_path))
    transactions = collection["transactions"]
    transaction_ids = [row["id"] for row in transactions]
    if len(set(transaction_ids)) != len(transaction_ids) or any(row["job"] not in job_ids for row in transactions):
        raise ValueError("transaction identity differs from the submitted jobs")
    charges = [Decimal(str(row["change"])) for row in transactions]
    if any(not change.is_finite() for change in charges):
        raise ValueError("transaction changes must be finite")
    counts = {row["file"]: row for row in ordered_map(shot_counts, shot_arguments)}
    report = screen(counts)
    report.update(
        {
            "schema": "qi-tuna-register-qualification-v1",
            "jobs": identities,
            "execution_seconds_decimal": str(sum(executions, Decimal(0))),
            "expected_execution_seconds_decimal": "14.31264",
            "transaction_change_decimal": str(sum(charges, Decimal(0))),
            "zero_recorded_charge": all(change == 0 for change in charges),
            "shots_total": 3 * SHOTS,
            "boundary": "Bounded register/readout screen; excludes causal mechanism, stationarity, QND and IID claims.",
            "order_boundary": (
                "Raw byte digests bind retained shot order; histogram agreement alone cannot establish provider order."
            ),
            "inputs": {path.relative_to(run).as_posix(): digest(path) for path in inputs},
            "analyzer_sha256": digest(Path(__file__)),
        }
    )
    report["passed"] = report["passed"] and report["zero_recorded_charge"]
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--out", type=Path)
    operation.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    report = replay(arguments.run)
    content = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if arguments.check:
        if arguments.check.read_text() != content:
            raise SystemExit("retained qualification differs from replay")
    else:
        with arguments.out.open("x") as destination:
            destination.write(content)
    if not report["passed"]:
        raise SystemExit("Tuna qualification refused; retained raw data and failed screen remain evidence")


if __name__ == "__main__":
    main()
