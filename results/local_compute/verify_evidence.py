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


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify(bundle: Path) -> None:
    manifest = json.loads((bundle / "manifest.json").read_text())
    entries = manifest["files"]
    _require(len({entry["path"] for entry in entries}) == len(entries), "duplicate manifest path")
    for entry in entries:
        relative = Path(entry["path"])
        _require(relative.name == entry["path"], "manifest paths must be sibling files")
        payload = (bundle / relative).read_bytes()
        _require(digest(payload) == entry["sha256"], f"retained digest: {relative}")
        _require(len(payload) == entry["bytes"], f"retained length: {relative}")
        if relative.suffix == ".gz":
            raw = gzip.decompress(payload)
            _require(digest(raw) == entry["source_sha256"], f"source digest: {relative}")
            _require(len(raw) == entry["source_bytes"], f"source length: {relative}")

    initial = read_json(bundle, "cpu_branching_results.json")
    qualification = read_json(bundle, "cpu_branching_qualification.json")
    _require(initial["state"] == "running", "initial evidence must retain its interrupted checkpoint")
    _require(qualification["state"] == "failed", "completed failure must remain explicit")
    initial_bytes = gzip.decompress((bundle / "cpu_branching_results.json.gz").read_bytes())
    _require(
        digest(initial_bytes) == qualification["input_report_sha256"], "qualification input-report digest mismatch"
    )
    qpy_bytes = gzip.decompress((bundle / "cpu_branching_inputs.qpy.gz").read_bytes())
    _require(
        digest(qpy_bytes) == initial["qpy_sha256"] == qualification["qpy_sha256"],
        "initial and qualification QPY digest mismatch",
    )
    noise_bytes = gzip.decompress((bundle / "cpu_branching_noise_semantic.json.gz").read_bytes())
    _require(
        digest(noise_bytes.removesuffix(b"\n")) == qualification["noise_semantic_sha256"],
        "qualification serialized-noise digest mismatch",
    )
    json.loads(noise_bytes)

    pairs = []
    for comparison in qualification["comparisons"]:
        rows = {
            case["shot_branching_enable"]: case
            for case in qualification["cases"]
            if case["family"] == comparison["family"] and case["shots"] == comparison["shots"]
        }
        _require(set(rows) == {False, True}, "paired counts must survive retention")
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
        _require(
            differences == comparison["bin_differences"],
            "qualification bin differences disagree with retained distributions",
        )
        maximum = max(value for values in differences.values() for value in values)
        radius = math.sqrt(2 * math.log(8 * bin_count / qualification["familywise_alpha"]) / comparison["shots"])
        _require(
            maximum == comparison["max_absolute_bin_difference"],
            "qualification maximum bin difference disagrees with recomputation",
        )
        _require(
            math.isclose(radius, comparison["simultaneous_radius"], rel_tol=1e-14),
            "qualification simultaneous radius disagrees with recomputation",
        )
        _require(
            (maximum <= radius) == comparison["compatible"],
            "qualification compatibility verdict disagrees with recomputation",
        )
        observed_failure |= maximum > radius
    _require(observed_failure, "retained qualification must reproduce its sampled incompatibility")
    _require(len(qualification["circuits"]) == 18, "qualification must retain eighteen circuits")
    _require(
        qualification["noiseless_oracle_check"]["compatible_with_exact_laws"],
        "noiseless oracle must remain compatible with exact laws",
    )
    _require(
        qualification["noiseless_oracle_check"]["swapped_n21_label_oracle_rejected"],
        "noiseless oracle must reject swapped N21 labels",
    )

    summary = json.loads((bundle / "summary.json").read_text())
    _require(summary["state"] == qualification["state"], "summary state differs from qualification")
    _require(summary["versions"] == qualification["versions"], "summary versions differ from qualification")
    _require(summary["qpy_sha256"] == qualification["qpy_sha256"], "summary QPY digest differs from qualification")
    _require(
        summary["circuit_count"] == len(qualification["circuits"]), "summary circuit count differs from qualification"
    )
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
    _require(
        summary["failed_bins"] == expected_failures, "summary failed bins differ from recomputed qualification failures"
    )
    replay = read_json(bundle, "cpu_branching_rca.json")
    _require(replay["state"] == "completed", "fresh-instance replay must remain completed")
    _require(
        replay["qpy_sha256"] == qualification["qpy_sha256"],
        "fresh-instance replay QPY digest differs from qualification",
    )
    _require(
        replay["noise_semantic_sha256"] == qualification["noise_semantic_sha256"],
        "fresh-instance replay serialized-noise digest differs from qualification",
    )
    channel_document = json.loads(noise_bytes)
    for channel in channel_document["errors"]:
        if channel.get("type") == "qerror":
            channel.pop("id", None)
    channel_document["errors"].sort(key=lambda channel: json.dumps(channel, sort_keys=True))
    _require(
        digest(json.dumps(channel_document, sort_keys=True).encode()) == replay["noise_channel_multiset_sha256"],
        "fresh-instance replay canonical noise-channel digest mismatch",
    )
    _require(
        summary["fresh_instance_replay"]["case_count"] == len(replay["cases"]) == 10,
        "fresh-instance replay and summary must retain ten cases",
    )
    _require(
        summary["fresh_instance_replay"]["cases"]
        == [
            {key: case[key] for key in ("options", "selection", "target_index", "wall_seconds", "distribution")}
            for case in replay["cases"]
        ],
        "summary fresh-instance cases differ from replay evidence",
    )
    for case in replay["cases"]:
        _require(len(case["distribution"]) == 4, "fresh-instance distribution must retain four outcomes")
        _require(
            all(0 <= probability <= 1 for probability in case["distribution"]),
            "fresh-instance probabilities must lie between zero and one",
        )
        _require(math.isclose(sum(case["distribution"]), 1.0), "fresh-instance probabilities must sum to one")
        _require(case["metadata"]["device"] == "CPU", "fresh-instance replay device must remain CPU")
        _require(
            case["metadata"]["method"] == "density_matrix", "fresh-instance replay method must remain density_matrix"
        )
    full_probe = read_json(bundle, "cpu_branching_reuse_probe.json")
    full_analysis = read_json(bundle, "cpu_branching_reuse_analysis.json")
    _require(full_probe["state"] == "completed", "full-family replay must remain completed")
    _require(len(full_probe["cases"]) == 15, "full-family replay must retain fifteen cases")
    _require(
        full_analysis["state"] == "failed_fresh_instance_repair_falsified",
        "full-family analysis must retain its failed-repair verdict",
    )
    _require(
        full_analysis["production_shot_branching_qualified"] is False,
        "full-family analysis must leave production shot branching unqualified",
    )
    for filename, expected in full_analysis["source_input_sha256"].items():
        _require(
            digest(gzip.decompress((bundle / (filename + ".gz")).read_bytes())) == expected,
            "full-family analysis source-input digest mismatch",
        )
    _require(
        full_analysis["qpy_sha256"] == qualification["qpy_sha256"] == full_probe["qpy_sha256"],
        "full-family analysis, qualification, and replay QPY digests differ",
    )
    _require(full_analysis["all_count_totals_complete"], "full-family analysis must retain complete count totals")
    _require(
        full_analysis["all_qpy_before_after_identical"], "full-family analysis must retain unchanged QPY identities"
    )
    _require(full_analysis["all_execution_modes_match"], "full-family analysis must retain matching execution modes")
    for comparison in full_analysis["comparisons"]:
        maximum = max(value for values in comparison["bin_differences"].values() for value in values)
        radius = sum(
            math.sqrt(
                math.log(8 * full_analysis["total_bin_comparisons"] / full_analysis["familywise_alpha"]) / (2 * shots)
            )
            for shots in (comparison["left_shots"], comparison["right_shots"])
        )
        _require(
            maximum == comparison["max_absolute_bin_difference"],
            "full-family maximum bin difference disagrees with recomputation",
        )
        _require(
            math.isclose(radius, comparison["simultaneous_radius"], rel_tol=1e-14),
            "full-family simultaneous radius disagrees with recomputation",
        )
        _require(
            (maximum <= radius) == comparison["compatible"],
            "full-family compatibility verdict disagrees with recomputation",
        )
    _require(
        summary["full_family_replay"]["state"] == full_analysis["state"],
        "summary full-family state differs from analysis",
    )
    _require(
        summary["full_family_replay"]["case_count"] == len(full_probe["cases"]),
        "summary full-family case count differs from replay",
    )
    print(
        "Local evidence digests, decompression, circuit/noise bindings, and sampled incompatibility pass verification"
    )


if __name__ == "__main__":
    verify(Path(__file__).resolve().parent)
