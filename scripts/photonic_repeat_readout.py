"""Replay conditional mode frequencies and matched-request differences from Quandela raw evidence.

Every run passes the provider's raw-result and receipt validator first. Vacuum
and multi-click outcomes keep their counts outside the one-click denominator.
The readout supplies descriptive differences, rather than calibrated coverage
or a causal assignment to optical drift.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import qd_platform as qd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

from parallel import ordered_map  # noqa: E402


def observation(setting: dict[str, Any], entry: dict[str, Any], logical_modes: int) -> dict[str, Any]:
    if entry.get("iteration", {}).get("circuit_params") != setting["circuit_params"]:
        raise ValueError("service parameter echo differs from the submitted setting")
    operator = setting["operator"]
    matrix = np.asarray(operator["real"]) + 1j * np.asarray(operator["imaginary"])
    expected = np.abs(matrix[:, 0]) ** 2
    modes = len(expected)
    counts = [0] * modes
    vacuum = multiple = 0
    for state, count in entry["counts"].items():
        occupations = [int(value) for value in state.split(",")]
        if len(occupations) != modes or any(value < 0 for value in occupations) or count < 0:
            raise ValueError("counted output differs from the declared mode and count domain")
        photons = sum(occupations)
        if photons == 1:
            counts[occupations.index(1)] += count
        elif photons == 0:
            vacuum += count
        else:
            multiple += count
    eligible = sum(counts)
    if eligible == 0:
        raise ValueError("the acquisition carries zero eligible one-click samples")
    if eligible + vacuum + multiple != entry["samples"]:
        raise ValueError("the declared sample count differs from its eligible and excluded counts")
    probabilities = np.asarray(counts) / eligible
    fields = entry["result_fields"]
    compiled = fields.get("computed_circuit")
    return {
        "name": setting["name"],
        "setting": setting["setting"]["name"],
        "repeat_index": setting["repeat_index"],
        "eligible_samples": eligible,
        "excluded_samples": vacuum + multiple,
        "vacuum_samples": vacuum,
        "multiple_click_samples": multiple,
        "mode_counts": counts,
        "mode_probabilities": probabilities.tolist(),
        "expected_mode_probabilities": expected.tolist(),
        "logical_pair_probabilities": [
            float(sum(probabilities[index : index + 2])) for index in range(0, logical_modes, 2)
        ],
        "outside_logical_support_probability": float(sum(probabilities[logical_modes:])),
        "total_variation_from_ideal": float(np.abs(probabilities - expected).sum() / 2),
        "computed_circuit_sha256": hashlib.sha256(compiled.encode()).hexdigest() if isinstance(compiled, str) else None,
        "reported_shots": fields.get("nb_shots_used"),
        "reported_physical_perf": fields.get("physical_perf"),
        "reported_logical_perf": fields.get("logical_perf"),
        "reported_global_perf": fields.get("global_perf"),
    }


def _observation(arguments: tuple[dict[str, Any], dict[str, Any], int]) -> dict[str, Any]:
    return observation(*arguments)


def analyze(directories: list[Path]) -> dict[str, Any]:
    rows = []
    acquisitions = []
    sources = {}
    for directory in directories:
        directory = directory.resolve()
        facts = qd.run_facts(directory)
        if facts["statuses"] != {"completed": 1}:
            raise ValueError(f"{directory.name}: the repeated-operator analysis requires a completed job")
        manifest, _, _ = qd.load_case(directory)
        if manifest["schema"] != "qd-hypercomplex-cases-v1" or "logical_modes" not in manifest:
            raise ValueError("the repeated-operator readout requires a full-output successor case")
        result = json.loads((directory / "results.json").read_text())
        if result.get("partial"):
            raise ValueError("a partial result cannot enter a complete repeat comparison")
        settings, entries = manifest["settings"], result["iterations"]
        if len(settings) != len(entries):
            raise ValueError("the setting and result denominators differ")
        for setting, entry in zip(settings, entries, strict=True):
            if entry["iteration"].get("compilation_seed") != setting["compilation_seed"]:
                raise ValueError("the returned compilation seed differs from the case")
        arguments = [
            (setting, entry, manifest["logical_modes"]) for setting, entry in zip(settings, entries, strict=True)
        ]
        observations = ordered_map(_observation, arguments, min_items=1)
        for index, row in enumerate(observations):
            rows.append({**row, "job_id": result["job_id"], "observation_index": index, "run": directory.name})
        acquisitions.append({"run": directory.name, "job_id": result["job_id"], **facts})
        for name in (
            "cases.json",
            "circuit.json",
            "submission.json",
            "job-body.json",
            "results.json",
            "raw/result.json",
        ):
            path = directory / name
            sources[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["setting"], []).append(row)
    differences = []
    for name, group in grouped.items():
        repeats = [row["repeat_index"] for row in group]
        if len(set(repeats)) != len(repeats):
            raise ValueError(f"{name}: an acquisition repeat appears more than once")
        for first, second in itertools.combinations(group, 2):
            distance = np.abs(np.asarray(first["mode_probabilities"]) - second["mode_probabilities"])
            differences.append(
                {
                    "setting": name,
                    "first": {key: first[key] for key in ("job_id", "repeat_index", "observation_index")},
                    "second": {key: second[key] for key in ("job_id", "repeat_index", "observation_index")},
                    "conditional_total_variation": float(distance.sum() / 2),
                    "same_compiled_circuit_bytes": first["computed_circuit_sha256"] is not None
                    and first["computed_circuit_sha256"] == second["computed_circuit_sha256"],
                }
            )
    return {
        "schema": "photonic-repeat-descriptive-readout-v1",
        "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "sources_sha256": sources,
        "acquisitions": acquisitions,
        "observations": rows,
        "repeat_differences": differences,
        "boundary": (
            "conditional one-click frequencies; acceptance and absolute efficiency remain distinct; "
            "matched-request changes do not isolate temporal drift, source response, mesh or processing"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directories", type=Path, nargs="+")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    record = analyze(arguments.directories)
    if arguments.check:
        from bdsc_certificate import close

        close(json.loads(arguments.check.read_text()), record, "photonic repeat readout")
        print("replayed photonic repeat readout and every raw source digest")
    elif arguments.out:
        qd.write_json(arguments.out, record, exclusive=True)
        print(f"retained {len(record['observations'])} descriptive photonic observations")
    else:
        print(json.dumps(record, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
