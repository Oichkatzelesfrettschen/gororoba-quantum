"""Describe the sim:ascella qualification of the frozen Ascella predecessor case.

The qualification copies the frozen case and replaces only its job name and admitted platform, so its retained
cases.json is the builder's manifest with those two fields substituted in place. The frozen analyzer's source digest
is bound by the case, so this reader reuses its per-iteration functions unchanged and reports the descriptive
statistics only; a sampling contract and its conditional envelopes bind the QPU case alone.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import ascella_predecessor_analysis as analysis
import ascella_predecessor_case as case
import qd_platform as qd

from parallel import ordered_map

SIMULATOR_VARIANT: dict[str, Any] = {"job": "source-compatible-simulator", "platforms": ["sim:ascella"]}
FILES = ("cases.json", "circuit.json", "submission.json", "job-body.json", "results.json", "raw/result.json")


def _entry(arguments: tuple[dict[str, Any], dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    """The frozen analyzer's iteration checks, with the returned compilation identity reported instead of required:
    the preregistered identity is the QPU's compilation, which sim:ascella need not reproduce."""
    setting, entry, identities = arguments
    expected = (
        identities["target"] if setting["role"] == "target" else identities["predecessors"][setting["source_name"]]
    )
    fields = entry.get("result_fields", {})
    matches = {
        name: isinstance(fields.get(name), str) and case.sha256_text(fields[name]) == expected[f"{name}_sha256"]
        for name in ("computed_circuit", "computed_input")
    }
    analysis.attribute_iteration({**setting, "setting_id": setting["name"]}, entry, analysis.PROFILE)
    ports, invalid = analysis.decode_photonic_counts(entry["counts"], case.MODES)
    total = sum(ports) + sum(invalid.values())
    if entry.get("samples") != total or total != case.SAMPLES_PER_ITERATION:
        raise ValueError(f"{setting['name']}: every iteration must reach the fixed returned-event count")
    detected = fields.get("nb_shots_used")
    if type(detected) is not int or not total <= detected <= case.SHOTS_PER_ITERATION:
        raise ValueError(f"{setting['name']}: detected shots differ from the frozen budget")
    return {
        "name": setting["name"],
        "eligible_port_counts": ports,
        "invalid_event_counts": invalid,
        "returned_events": total,
        "detected_shots": detected,
        "identity_matches_preregistration": matches,
    }


def simulator_manifest() -> dict[str, Any]:
    """The frozen manifest with the qualification's two fields replaced in place."""
    return {**case.check(), **SIMULATOR_VARIANT}


def describe_run(directory: Path) -> dict[str, Any]:
    """Check a simulator run against the substituted manifest and describe its eight iterations."""
    manifest = simulator_manifest()
    artifacts = {name: (directory / name).read_bytes() for name in FILES}
    if artifacts["cases.json"] != (json.dumps(manifest, indent=1) + "\n").encode():
        raise ValueError("the run is not the simulator qualification of the frozen case")
    qd.run_facts(directory)
    results = analysis._parse_json(artifacts["results.json"], "results.json")
    status = results.get("status", {})
    if not isinstance(status, dict) or status.get("status") != "completed":
        raise ValueError("a completed acquisition is required")
    body = analysis._parse_json(artifacts["job-body.json"], "job-body.json")
    if body.get("platform_name") != "sim:ascella":
        raise ValueError("the simulator qualification sends its body to sim:ascella")
    # validate_sent_body admits the QPU platform name only; every other field is checked as sent.
    analysis.validate_sent_body(body | {"platform_name": "qpu:ascella"}, manifest, analysis.PROFILE)
    entries = results.get("iterations")
    if not isinstance(entries, list) or len(entries) != len(case.ORDER):
        raise ValueError("the result requires all eight iterations")
    identities = manifest["preregistered"]["compilation_identity"]
    observations = ordered_map(
        _entry,
        [(setting, entry, identities) for setting, entry in zip(manifest["settings"], entries, strict=True)],
    )
    return {
        "schema": "ascella-predecessor-simulator-v1",
        "case_variant": SIMULATOR_VARIANT,
        "job_id": results["job_id"],
        "source_sha256": manifest["analysis_sources"],
        "run_bindings": {name: hashlib.sha256(data).hexdigest() for name, data in artifacts.items()},
        "observations": observations,
        **analysis.describe([row["eligible_port_counts"] for row in observations]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    print(json.dumps(describe_run(args.run), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
