"""Verify local-compute evidence bytes and the retained compatibility failure.

The verifier uses the standard library, reads local archives, and performs
zero service, simulator, credential, or network operations.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
from pathlib import Path
from typing import Any


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def read_json(bundle: Path, name: str) -> Any:
    return json.loads(gzip.decompress((bundle / f"{name}.gz").read_bytes()))


def verify(bundle: Path) -> None:
    manifest = json.loads((bundle / "manifest.json").read_text())
    entries = manifest["files"]
    assert len({entry["path"] for entry in entries}) == len(entries), "duplicate manifest path"
    for entry in entries:
        relative = Path(entry["path"])
        assert relative.name == entry["path"], "manifest paths must be sibling files"
        payload = (bundle / relative).read_bytes()
        assert digest(payload) == entry["sha256"], f"retained digest: {relative}"
        assert len(payload) == entry["bytes"], f"retained length: {relative}"
        if relative.suffix == ".gz":
            raw = gzip.decompress(payload)
            assert digest(raw) == entry["source_sha256"], f"source digest: {relative}"
            assert len(raw) == entry["source_bytes"], f"source length: {relative}"

    initial = read_json(bundle, "cpu_branching_results.json")
    qualification = read_json(bundle, "cpu_branching_qualification.json")
    assert initial["state"] == "running", "initial evidence must retain its interrupted checkpoint"
    assert qualification["state"] == "failed", "completed failure must remain explicit"
    initial_bytes = gzip.decompress((bundle / "cpu_branching_results.json.gz").read_bytes())
    assert digest(initial_bytes) == qualification["input_report_sha256"]
    qpy_bytes = gzip.decompress((bundle / "cpu_branching_inputs.qpy.gz").read_bytes())
    assert digest(qpy_bytes) == initial["qpy_sha256"] == qualification["qpy_sha256"]
    noise_bytes = gzip.decompress((bundle / "cpu_branching_noise_semantic.json.gz").read_bytes())
    assert digest(noise_bytes.removesuffix(b"\n")) == qualification["noise_semantic_sha256"]
    json.loads(noise_bytes)

    pairs = []
    for comparison in qualification["comparisons"]:
        rows = {
            case["shot_branching_enable"]: case
            for case in qualification["cases"]
            if case["family"] == comparison["family"] and case["shots"] == comparison["shots"]
        }
        assert set(rows) == {False, True}, "paired counts must survive retention"
        pairs.append((comparison, rows))
    bin_count = sum(len(values) for _, rows in pairs for values in rows[False]["distributions"].values())
    observed_failure = False
    for comparison, rows in pairs:
        differences = {
            member: [
                abs(first - second) for first, second in zip(values, rows[True]["distributions"][member], strict=True)
            ]
            for member, values in rows[False]["distributions"].items()
        }
        assert differences == comparison["bin_differences"]
        maximum = max(value for values in differences.values() for value in values)
        radius = math.sqrt(2 * math.log(8 * bin_count / qualification["familywise_alpha"]) / comparison["shots"])
        assert maximum == comparison["max_absolute_bin_difference"]
        assert math.isclose(radius, comparison["simultaneous_radius"], rel_tol=1e-14)
        assert (maximum <= radius) == comparison["compatible"]
        observed_failure |= maximum > radius
    assert observed_failure, "retained qualification must reproduce its sampled incompatibility"
    assert len(qualification["circuits"]) == 18
    assert qualification["noiseless_oracle_check"]["compatible_with_exact_laws"]
    assert qualification["noiseless_oracle_check"]["swapped_n21_label_oracle_rejected"]

    summary = json.loads((bundle / "summary.json").read_text())
    assert summary["state"] == qualification["state"]
    assert summary["versions"] == qualification["versions"]
    assert summary["qpy_sha256"] == qualification["qpy_sha256"]
    assert summary["circuit_count"] == len(qualification["circuits"])
    expected_failures = [
        {
            "family": row["family"],
            "shots": row["shots"],
            "member": member,
            "outcome": index,
            "absolute_difference": value,
            "simultaneous_radius": row["simultaneous_radius"],
        }
        for row in qualification["comparisons"]
        for member, values in row["bin_differences"].items()
        for index, value in enumerate(values)
        if value > row["simultaneous_radius"]
    ]
    assert summary["failed_bins"] == expected_failures
    replay = read_json(bundle, "cpu_branching_rca.json")
    assert replay["state"] == "completed"
    assert replay["qpy_sha256"] == qualification["qpy_sha256"]
    assert replay["noise_semantic_sha256"] == qualification["noise_semantic_sha256"]
    channel_document = json.loads(noise_bytes)
    for channel in channel_document["errors"]:
        if channel.get("type") == "qerror":
            channel.pop("id", None)
    channel_document["errors"].sort(key=lambda channel: json.dumps(channel, sort_keys=True))
    assert digest(json.dumps(channel_document, sort_keys=True).encode()) == replay["noise_channel_multiset_sha256"]
    assert summary["fresh_instance_replay"]["case_count"] == len(replay["cases"]) == 10
    assert summary["fresh_instance_replay"]["cases"] == [
        {key: case[key] for key in ("options", "selection", "target_index", "wall_seconds", "distribution")}
        for case in replay["cases"]
    ]
    for case in replay["cases"]:
        assert len(case["distribution"]) == 4
        assert all(0 <= probability <= 1 for probability in case["distribution"])
        assert math.isclose(sum(case["distribution"]), 1.0)
        assert case["metadata"]["device"] == "CPU"
        assert case["metadata"]["method"] == "density_matrix"
    full_probe = read_json(bundle, "cpu_branching_reuse_probe.json")
    full_analysis = read_json(bundle, "cpu_branching_reuse_analysis.json")
    assert full_probe["state"] == "completed"
    assert len(full_probe["cases"]) == 15
    assert full_analysis["state"] == "failed_fresh_instance_repair_falsified"
    assert full_analysis["production_shot_branching_qualified"] is False
    for filename, expected in full_analysis["source_input_sha256"].items():
        assert digest(gzip.decompress((bundle / (filename + ".gz")).read_bytes())) == expected
    assert full_analysis["qpy_sha256"] == qualification["qpy_sha256"] == full_probe["qpy_sha256"]
    assert full_analysis["all_count_totals_complete"]
    assert full_analysis["all_qpy_before_after_identical"]
    assert full_analysis["all_execution_modes_match"]
    for comparison in full_analysis["comparisons"]:
        maximum = max(value for values in comparison["bin_differences"].values() for value in values)
        radius = sum(
            math.sqrt(
                math.log(8 * full_analysis["total_bin_comparisons"] / full_analysis["familywise_alpha"]) / (2 * shots)
            )
            for shots in (comparison["left_shots"], comparison["right_shots"])
        )
        assert maximum == comparison["max_absolute_bin_difference"]
        assert math.isclose(radius, comparison["simultaneous_radius"], rel_tol=1e-14)
        assert (maximum <= radius) == comparison["compatible"]
    assert summary["full_family_replay"]["state"] == full_analysis["state"]
    assert summary["full_family_replay"]["case_count"] == len(full_probe["cases"])
    print(
        "Local evidence digests, decompression, circuit/noise bindings, and sampled incompatibility pass verification"
    )


if __name__ == "__main__":
    verify(Path(__file__).resolve().parent)
