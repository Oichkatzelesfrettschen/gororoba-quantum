"""Exploratory pinching analysis over every layout qubit of a collected measurement-sequence envelope run.

The preregistered envelope analysis (msq_envelope_analysis.collected) runs the pinching analysis only over the qubits
its screens keep. This script runs measurement_sequence_analysis.collected over every layout qubit with the screens
ignored, as a second, non-preregistered reading of the same counts; no device verdict it prints is a result of the
envelope case.

Counts come from collect.json: each stored law, times its member's shots, rounds to whole shots. Before analysing,
the script recomputes msq_envelope_analysis.screens from those counts and requires every reset statistic, pattern
p-value and keep decision to equal the collected envelope screens exactly, so the counts are the ones collect read.

``--out FILE`` writes the result; ``--check FILE`` recomputes it and requires the retained bytes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import law_encoding  # noqa: E402
import measurement_sequence_analysis as msa  # noqa: E402
import msq_envelope_analysis as ea  # noqa: E402

SCHEMA = "msq-envelope-exploratory-v1"


def counts(run: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, list[np.ndarray]], dict[str, Any]]:
    record = json.loads((run / "record.json").read_text())
    collected = json.loads((run / "collect.json").read_text())
    distributions: dict[str, list[np.ndarray]] = {}
    executed: dict[str, Any] = {}
    for entry in collected[1:]:
        executed.update(entry["executed"])
        for name, laws in entry["measured"].items():
            shots = int(entry["executed"][name]["shots"])
            rows = []
            for law in laws:
                whole = np.rint(np.asarray(law_encoding.dense(law), dtype=float) * shots)
                if whole.sum() != shots:
                    raise SystemExit(f"{name}: {whole.sum()} rounded shots, {shots} executed")
                rows.append(whole / shots)
            distributions[name] = rows
    return record, collected, distributions, executed


def require_screens(record: dict[str, Any], collected: list[dict[str, Any]], distributions, executed) -> None:
    recomputed = ea.screens(record, distributions, executed)
    retained = collected[0]["family_analysis"]["envelope"]["screens"]
    if recomputed.keys() != retained.keys():
        raise SystemExit("screened qubits differ from collect.json")
    for qubit, screen in retained.items():
        mine = recomputed[qubit]
        same = mine["kept"] == screen["kept"] and all(
            mine["reset"].get(key) == screen["reset"].get(key) for key in ("difference", "se", "upper_bound")
        )
        same = same and all(
            mine["patterns"]["states"][state]["p_value"] == screen["patterns"]["states"][state]["p_value"]
            for state in ("0", "1")
        )
        if not same:
            raise SystemExit(f"q{qubit}: recomputed screens differ from collect.json")


def run(path: Path) -> dict[str, Any]:
    record, collected, distributions, executed = counts(path)
    require_screens(record, collected, distributions, executed)
    width = int(record["family_configuration"]["layout_width"])
    analysis = msa.collected(record, distributions, executed, None, ea.count_rule(width))
    return {
        "schema": SCHEMA,
        "run": path.name,
        "preregistered": False,
        "screens_reproduced": True,
        "count_rule": ea.count_rule(width),
        "analysis": analysis,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    args = parser.parse_args(argv)
    text = json.dumps(run(args.run), indent=1, sort_keys=True, default=float) + "\n"
    if args.out:
        args.out.write_text(text)
        return 0
    if args.check.read_text() != text:
        raise SystemExit(f"{args.check} differs from the recomputed analysis")
    print(f"{args.check}: reproduced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
