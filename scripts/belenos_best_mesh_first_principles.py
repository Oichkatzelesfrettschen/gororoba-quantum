#!/usr/bin/env python3
"""First-principles checks behind the Belenos best-mesh teleportation replay.

The script reads the retained teleportation rehearsal runs (job-02, its exact replay and job-03) and computes, per
served mesh, the quantities that decide how a winner-and-loser replay of the job-02 and job-03 compilation seeds
reads:

- compiled: the noiseless three-photon propagation through each returned ``computed_circuit`` unitary, scored by the
  rehearsal classifier, against the target operator of its setting. A compiled-mesh shortfall that differs by seed
  places the per-seed error in the compiler; equal unit scores place it on the chip.

Usage: belenos_best_mesh_first_principles.py --out PATH
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import qd_belenos_mesh as mesh  # noqa: E402
import qd_teleportation_rehearsal as tr  # noqa: E402
from qd_network_protocol import propagate  # noqa: E402

from parallel import ordered_map  # noqa: E402

RUNS = ROOT / "results/quandela/runs"
RUN_NAMES = {
    "job-02": "2026-10-31T035736Z-qpu_belenos-teleportation_rehearsal-job-02",
    "job-02-replay": "2026-10-31T042633Z-qpu_belenos-teleportation_rehearsal-job-02-replay",
    "job-03": "2026-10-31T040337Z-qpu_belenos-teleportation_rehearsal-job-03",
}


def clicks_of(unitary: np.ndarray, source: Sequence[int]) -> dict[tuple[int, ...], float]:
    """Threshold-click distribution of the noiseless three-photon propagation through ``unitary``."""
    output = propagate(unitary, {tuple(source): 1.0 + 0.0j})
    clicks: dict[tuple[int, ...], float] = {}
    for occupation, amplitude in output.items():
        key = tuple(1 if count else 0 for count in occupation)
        clicks[key] = clicks.get(key, 0.0) + abs(amplitude) ** 2
    return clicks


def total_variation(left: Mapping[tuple[int, ...], float], right: Mapping[tuple[int, ...], float]) -> float:
    """Total variation distance of two click distributions: the complete observable of threshold detection, blind to
    the input-photon and output-mode phases that a column comparison would count."""
    return 0.5 * sum(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in set(left) | set(right))


def compiled_row(item: tuple[str, int, Mapping[str, Any], str, Sequence[int]]) -> dict[str, Any]:
    run, index, setting, circuit_text, layout = item
    elements = mesh.decode(circuit_text)
    arch = mesh.run_architecture(elements)
    phases = mesh.mesh_phases(arch, elements)
    compiled = mesh.unitary(arch, phases)
    target = tr.operator_of(dict(setting))
    source = tr.source_state(layout)
    occupied = [mode for mode, count in enumerate(source) if count]
    label = setting["label"]
    target_clicks, compiled_clicks = clicks_of(target, source), clicks_of(compiled, source)
    ideal_acc, ideal_cor = tr.scored(label, target_clicks, layout)
    comp_acc, comp_cor = tr.scored(label, compiled_clicks, layout)
    power = np.abs(compiled[:, occupied]) ** 2 - np.abs(target[:, occupied]) ** 2
    return {
        "run": run,
        "index": index,
        "label": label,
        "compilation_seed": setting["compilation_seed"],
        "mesh_sha": hashlib.sha256(mesh.unzip(circuit_text).encode()).hexdigest()[:8],
        "heater_phase_rad": float(sum(phases)),
        "click_total_variation": total_variation(compiled_clicks, target_clicks),
        "max_column_power_difference": float(np.max(np.abs(power))),
        "target_accepted_probability": ideal_acc,
        "target_conditional_fidelity": ideal_cor / ideal_acc,
        "compiled_accepted_probability": comp_acc,
        "compiled_conditional_fidelity": comp_cor / comp_acc,
    }


def compiled_section() -> list[dict[str, Any]]:
    items = []
    for run, name in RUN_NAMES.items():
        cases = json.loads((RUNS / name / "cases.json").read_text(encoding="utf-8"))
        layout = tuple(cases["layout"]["chip_modes"])
        circuits = mesh.computed_circuits(RUNS / name)
        if len(circuits) != len(cases["settings"]):
            raise ValueError(f"{run}: {len(circuits)} computed circuits for {len(cases['settings'])} settings")
        for index, (setting, text) in enumerate(zip(cases["settings"], circuits, strict=True)):
            items.append((run, index, setting, text, layout))
    return ordered_map(compiled_row, items, min_items=1)


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    record = {"schema": "belenos-best-mesh-first-principles-v1", "compiled": compiled_section()}
    args.out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
