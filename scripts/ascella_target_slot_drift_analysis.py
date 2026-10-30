"""Describe the Ascella eight-target requested-slot contrast without causal attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import qd_platform
from ascella_target_slot_drift import LABELS, WEIGHTS
from experiment_analysis import decode_photonic_counts

FILES = ("cases.json", "circuit.json", "job-body.json", "submission.json", "results.json", "raw/result.json")


def analyze(directory: Path) -> dict[str, Any]:
    """Validate provider records and attribute all sixteen returned iterations."""
    facts = qd_platform.run_facts(directory)
    manifest = json.loads((directory / "cases.json").read_bytes())
    results = json.loads((directory / "results.json").read_bytes())
    if manifest.get("family") != "ascella_target_slot_drift" or results["status"]["status"] != "completed":
        raise ValueError("a complete Ascella target-slot diagnostic is required")
    settings = manifest["settings"]
    entries = results["iterations"]
    if len(settings) != 16 or len(entries) != 16:
        raise ValueError("all sixteen iterations are required")
    identities = manifest["preregistered"]["compilation_identity"]
    rows = []
    laws = []
    for index, (setting, entry) in enumerate(zip(settings, entries, strict=True)):
        if (
            setting["order"] != LABELS[index // 2]
            or setting["slot"] != index % 2
            or setting["role"] != ("target" if index % 2 else "predecessor")
        ):
            raise ValueError("the requested setting order differs")
        iteration = entry["iteration"]
        if any(iteration[key] != setting[key] for key in ("compilation_seed", "circuit_params")):
            raise ValueError(f"{setting['name']}: returned iteration differs from the request")
        ports, invalid = decode_photonic_counts(entry["counts"], 12)
        samples = sum(ports) + sum(invalid.values())
        if samples != 32768 or entry["samples"] != samples or sum(ports) == 0:
            raise ValueError(f"{setting['name']}: sample count or eligible denominator differs")
        fields = entry["result_fields"]
        if type(fields.get("nb_shots_used")) is not int or fields["nb_shots_used"] != 32768:
            raise ValueError(f"{setting['name']}: shot count differs from the request")
        expected = (
            identities["target"] if setting["role"] == "target" else identities["predecessors"][setting["source_name"]]
        )
        identity = {}
        for name in ("computed_circuit", "computed_input"):
            blob = fields.get(name)
            identity[name] = (
                isinstance(blob, str) and hashlib.sha256(blob.encode()).hexdigest() == expected[f"{name}_sha256"]
            )
        rows.append(
            {
                "name": setting["name"],
                "ports": ports,
                "invalid": invalid,
                "eligible": sum(ports),
                "shots_used": fields.get("nb_shots_used"),
                "reference_identity_matches": identity,
            }
        )
        if index % 2:
            laws.append([count / sum(ports) for count in ports])
    contrast = [math.fsum(WEIGHTS[index] * law[mode] / 4 for index, law in enumerate(laws)) for mode in range(12)]
    qpu_identity_valid = all(all(row["reference_identity_matches"].values()) for row in rows)
    return {
        "schema": "ascella-target-slot-drift-analysis-v1",
        "analyzer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "job_id": results["job_id"],
        "platform": facts["backends"][0],
        "charge": facts["charge"],
        "observations": rows,
        "requested_index_contrast": contrast,
        "contrast_total_variation_norm": sum(abs(x) for x in contrast) / 2,
        "reference_compilation_matches_all": qpu_identity_valid,
        "physical_predecessor_attribution": "unavailable",
        "boundary": "Descriptive only; requested order does not establish physical chronology or causal history.",
        "artifact_sha256": {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in FILES},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    print(json.dumps(analyze(args.run), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
