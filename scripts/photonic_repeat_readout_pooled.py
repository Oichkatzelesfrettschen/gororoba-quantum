"""Replay photonic acquisitions through an order-preserving directory pool.

The serial producer and its hash-bound output remain historical evidence.
Each worker validates one acquisition before deriving its observations.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np
import qd_platform as qd
from photonic_repeat_readout import ROOT, _observation

from parallel import ordered_map


def _directory(name: str) -> dict[str, Any]:
    directory = Path(name)
    facts = qd.run_facts(directory)
    if facts["statuses"] != {"completed": 1}:
        raise ValueError(f"{directory.name}: repeat analysis requires a completed job")
    manifest, _, _ = qd.load_case(directory)
    if manifest["schema"] != "qd-hypercomplex-cases-v1" or "logical_modes" not in manifest:
        raise ValueError("repeat readout requires a full-output successor case")
    result = json.loads((directory / "results.json").read_text())
    if result.get("partial"):
        raise ValueError("a partial result cannot enter a complete repeat comparison")
    settings, entries = manifest["settings"], result["iterations"]
    if len(settings) != len(entries):
        raise ValueError("the setting and result denominators differ")
    if any(
        entry["iteration"].get("compilation_seed") != setting["compilation_seed"]
        for setting, entry in zip(settings, entries, strict=True)
    ):
        raise ValueError("the returned compilation seed differs from the case")
    arguments = [(setting, entry, manifest["logical_modes"]) for setting, entry in zip(settings, entries, strict=True)]
    observations = ordered_map(_observation, arguments, min_items=1)
    rows = [
        {**row, "job_id": result["job_id"], "observation_index": index, "run": directory.name}
        for index, row in enumerate(observations)
    ]
    sources = {
        (directory / relative).relative_to(ROOT).as_posix(): hashlib.sha256(
            (directory / relative).read_bytes()
        ).hexdigest()
        for relative in (
            "cases.json",
            "circuit.json",
            "submission.json",
            "job-body.json",
            "results.json",
            "raw/result.json",
        )
    }
    return {
        "rows": rows,
        "acquisition": {"run": directory.name, "job_id": result["job_id"], **facts},
        "sources": sources,
    }


def _difference(arguments: tuple[str, dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    name, first, second = arguments
    distance = np.abs(np.asarray(first["mode_probabilities"]) - np.asarray(second["mode_probabilities"]))
    return {
        "setting": name,
        "first": {key: first[key] for key in ("job_id", "repeat_index", "observation_index")},
        "second": {key: second[key] for key in ("job_id", "repeat_index", "observation_index")},
        "conditional_total_variation": float(distance.sum() / 2),
        "same_compiled_circuit_bytes": first["computed_circuit_sha256"] is not None
        and first["computed_circuit_sha256"] == second["computed_circuit_sha256"],
    }


def analyze(directories: list[Path]) -> dict[str, Any]:
    parts = ordered_map(_directory, [str(path.resolve()) for path in directories], min_items=1)
    rows = [row for part in parts for row in part["rows"]]
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["setting"], []).append(row)
    arguments: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
    for name, group in grouped.items():
        repeats = [row["repeat_index"] for row in group]
        if len(set(repeats)) != len(repeats):
            raise ValueError(f"{name}: an acquisition repeat appears more than once")
        arguments.extend((name, first, second) for first, second in itertools.combinations(group, 2))
    return {
        "schema": "photonic-repeat-descriptive-readout-v1",
        "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "dependency_sha256": {
            "scripts/photonic_repeat_readout.py": hashlib.sha256(
                (ROOT / "scripts/photonic_repeat_readout.py").read_bytes()
            ).hexdigest()
        },
        "sources_sha256": {name: digest for part in parts for name, digest in part["sources"].items()},
        "acquisitions": [part["acquisition"] for part in parts],
        "observations": rows,
        "repeat_differences": ordered_map(_difference, arguments, min_items=1),
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

        close(json.loads(arguments.check.read_text()), record, "pooled photonic readout")
        print("replayed pooled acquisition validation and photonic readout")
    elif arguments.out:
        qd.write_json(arguments.out, record, exclusive=True)
    else:
        print(json.dumps(record, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
