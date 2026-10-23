"""Retain complete Perceval operators that reproduce the physical simulation residuals."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402


def operators_for_case(arguments: tuple[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    import numpy as np
    import qd_platform

    directory, retained = arguments
    manifest, specification, _ = qd_platform.load_case(ROOT / directory)
    built, _ = qd_platform.template_experiment(manifest, specification)
    chip = built.unitary_circuit()
    parameters = chip.get_parameters()
    rows = []
    for row in retained:
        setting = manifest["settings"][row["index"]]
        for parameter in parameters:
            parameter.set_value(setting["circuit_params"][parameter.name])
        actual = np.asarray(chip.compute_unitary())
        expected = np.asarray(setting["operator"]["real"]) + 1j * np.asarray(setting["operator"]["imaginary"])
        error = float(np.max(np.abs(actual - expected)))
        if not math.isfinite(error) or error >= 1e-9 or error != row["full_operator_max_error"]:
            raise ValueError(
                f"{directory}/{row['index']}: reconstructed operator residual differs from retained observation"
            )
        rows.append(
            {
                "case": directory,
                "index": row["index"],
                "actual_operator": {"real": actual.real.tolist(), "imaginary": actual.imag.tolist()},
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()
    if arguments.out.exists():
        raise FileExistsError("choose a fresh output path and retain existing operator evidence")
    retained_path = ROOT / "results/local-simulation/physical-photonic-compiler-crosscheck/photonic.json"
    retained = json.loads(retained_path.read_text())
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in retained["rows"]:
        groups.setdefault(row["case"], []).append(row)
    rows = [row for group in ordered_map(operators_for_case, list(groups.items()), min_items=1) for row in group]
    record = {
        "schema": "local-optical-operator-replay-v1",
        "evidence_class": "complete operators from local noiseless Perceval reconstruction",
        "versions": {name: version(name) for name in ("perceval-quandela", "exqalibur", "numpy")},
        "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "retained_photonic_sha256": hashlib.sha256(retained_path.read_bytes()).hexdigest(),
        "source_sha256": retained["source_sha256"],
        "rows": rows,
    }
    arguments.out.write_text(json.dumps(record, indent=1) + "\n")
    print(f"retained {len(rows)} complete operators with exactly reproduced residuals")


if __name__ == "__main__":
    main()
