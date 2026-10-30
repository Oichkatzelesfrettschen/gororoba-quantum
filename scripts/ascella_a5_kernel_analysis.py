"""Describe the retained Ascella A5 slice observations and their provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import qd_platform
from experiment_analysis import decode_photonic_counts

FILES = ("cases.json", "circuit.json", "job-body.json", "submission.json", "results.json", "raw/result.json")


def describe(directory: Path) -> dict[str, Any]:
    """Validate the submitted request and report conditional single-photon branch fractions."""
    facts = qd_platform.run_facts(directory)
    manifest = json.loads((directory / "cases.json").read_bytes())
    results = json.loads((directory / "results.json").read_bytes())
    if manifest.get("family") != "ascella_a5_kernel_slice" or results["status"]["status"] != "completed":
        raise ValueError("a completed Ascella A5 kernel-slice run is required")
    settings = manifest["settings"]
    entries = results["iterations"]
    if len(settings) != 6 or len(entries) != len(settings):
        raise ValueError("the result must contain all six settings")
    observations = []
    for setting, entry in zip(settings, entries, strict=True):
        iteration = entry["iteration"]
        if any(iteration[key] != setting[key] for key in ("compilation_seed", "circuit_params")):
            raise ValueError(f"{setting['name']}: returned iteration differs from its request")
        ports, invalid = decode_photonic_counts(entry["counts"], 12)
        events = sum(ports) + sum(invalid.values())
        shots = entry["result_fields"]["nb_shots_used"]
        if events != entry["samples"] or events != 10000 or type(shots) is not int or not events <= shots <= 100000:
            raise ValueError(f"{setting['name']}: returned sample or shot count differs from the case")
        success, failure = sum(ports[:4]), sum(ports[4:8])
        denominator = success + failure
        if denominator == 0:
            raise ValueError(f"{setting['name']}: no eligible branch events")
        observations.append(
            {
                "name": setting["name"],
                "ideal_success": setting["ideal_success"],
                "port_counts": ports,
                "invalid_events": invalid,
                "returned_events": events,
                "shots_used": shots,
                "success": success,
                "failure": failure,
                "sentinel": sum(ports[8:]),
                "conditional_success": success / denominator,
            }
        )
    return {
        "schema": "ascella-a5-kernel-slice-analysis-v1",
        "job_id": results["job_id"],
        "platform": facts["backends"][0],
        "charge": facts["charge"],
        "artifact_sha256": {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in FILES},
        "observations": observations,
        "interpretation": (
            "Descriptive conditional branch fractions; full A5 nullity and physical nonassociativity remain untested."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    print(json.dumps(describe(args.run), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
