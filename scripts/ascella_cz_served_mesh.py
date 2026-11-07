"""Served-against-designed two-photon law of every setting of the Ascella CZ process tomography case.

Each of the 144 settings of scripts/ascella_cz_tomography_case.py ran on its own compiled mesh, which the service
returns as the iteration's computed_circuit. This script decodes every retained mesh (photonic_compilation_audit and
qd_belenos_mesh, which agree with Perceval's deserializer) into its twelve-mode unitary and compares it with the
designed unitary of the setting, setting_unitary embedded at chip modes 0..5.

Photons enter chip modes 0 and 2 only, so a setting fixes two columns of the unitary and leaves the other ten free to
the transpiler. The eligible amplitudes are the four permanents of one photon on each rail pair, (0, 2), (0, 3),
(1, 2) and (1, 3), with modes 4..11 empty. The readout rotation is part of every setting's unitary, so for
indistinguishable photons the click statistics of a setting depend on the moduli of those amplitudes alone; the
transpiler fits a phase on each output mode freely, and a phase-sensitive overlap of the amplitudes measures that
freedom rather than an error. Distinguishable photons follow the sum of the squared moduli of the two products of
each permanent instead; tests/scripts/test_ascella_cz_served_mesh.py holds that law to the same tolerance.

Per setting the record keeps the total variation distance between the served and designed distributions over the
four eligible outcomes (nominal_tvd), the ratio of served to designed eligible probability (success_ratio) and the
largest deviation of the moduli of the two input columns (column_modulus_deviation). The summary gives their range
over all 144 settings and per job. These are nominal quantities: the mesh as returned, without the chip's physical
phase errors, loss or source imperfection.

The measured side of the same settings is the eligible events of the retained analysis per nb_shots_used of the
iteration, as a ratio to its mean over the 144 settings (eligible_per_shot_ratio), with the mean ratio of each of the
16 inputs over its nine readouts. The ensemble design's input-independence condition is a rule on this ratio.

--write retains the record; --check recomputes it and requires every key, name and count to match and every float to
agree within TOLERANCE, the comparison of ascella_cz_tomography_case.first_difference.

Usage:
  "$PYTHON" scripts/ascella_cz_served_mesh.py --check | --write
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_cz_tomography_case as case  # noqa: E402
import photonic_compilation_audit as audit  # noqa: E402
import qd_belenos_mesh as mesh  # noqa: E402

RECORD = ROOT / "results/quandela/ascella-cz-served-mesh.json"
RUNS = (
    "results/quandela/runs/2026-10-31T050944Z-qpu_ascella-ascella_cz_tomography-job-00",
    "results/quandela/runs/2026-10-31T050944Z-qpu_ascella-ascella_cz_tomography-job-01",
)
ANALYSIS = "results/quandela/ascella-cz-tomography-analysis.json"
SCHEMA = "ascella-cz-served-mesh-v1"
SOURCES = (case.C0, case.T0)
ELIGIBLE = ((case.C0, case.T0), (case.C0, case.T1), (case.C1, case.T0), (case.C1, case.T1))
METRICS = ("nominal_tvd", "success_ratio", "column_modulus_deviation")


def eligible_amplitudes(unitary: np.ndarray) -> np.ndarray:
    """Amplitudes of the four eligible outcomes, outcome order 2 * control rail + target rail."""
    a, b = SOURCES
    return np.array([unitary[c, a] * unitary[t, b] + unitary[c, b] * unitary[t, a] for c, t in ELIGIBLE])


def served_unitary(blob: str) -> np.ndarray:
    elements = audit._elements(blob)
    full = mesh.unitary(elements, [value for kind, _, value in elements if kind == "ps"])
    return np.asarray(full[: case.MODES, : case.MODES], dtype=complex)


def compare(setting: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    iteration = entry["iteration"]
    case.require(
        iteration["compilation_seed"] == setting["compilation_seed"]
        and iteration["circuit_params"] == setting["circuit_params"],
        f"{setting['name']}: the result entry echoes another setting",
    )
    served = served_unitary(entry["computed_circuit"])
    designed = case.embed(case.setting_unitary(setting))
    served_p = np.abs(eligible_amplitudes(served)) ** 2
    designed_p = np.abs(eligible_amplitudes(designed)) ** 2
    columns = list(SOURCES)
    return {
        "name": setting["name"],
        "observation_index": setting["observation_index"],
        "nominal_tvd": float(np.abs(served_p / served_p.sum() - designed_p / designed_p.sum()).sum() / 2),
        "success_ratio": float(served_p.sum() / designed_p.sum()),
        "column_modulus_deviation": float(np.abs(np.abs(served[:, columns]) - np.abs(designed[:, columns])).max()),
    }


def summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {"settings": len(rows)}
    for key in METRICS:
        values = np.array([row[key] for row in rows])
        out[key] = {"min": float(values.min()), "median": float(np.median(values)), "max": float(values.max())}
    return out


def record() -> dict[str, Any]:
    jobs: dict[str, Any] = {}
    every: list[dict[str, Any]] = []
    eligible = json.loads((ROOT / ANALYSIS).read_text(encoding="utf-8"))["eligible_events_by_setting"]
    for job, run in zip(case.JOBS, RUNS, strict=True):
        settings = json.loads((ROOT / run / "cases.json").read_text(encoding="utf-8"))["settings"]
        raw = json.loads((ROOT / run / "raw/result.json").read_text(encoding="utf-8"))
        entries = json.loads(raw["results"])["results_list"]
        case.require(len(settings) == len(entries), f"{run}: {len(entries)} results for {len(settings)} settings")
        rows = [compare(setting, entry) for setting, entry in zip(settings, entries, strict=True)]
        for row, entry in zip(rows, entries, strict=True):
            row["shots"] = int(entry["nb_shots_used"])
            row["eligible_events"] = int(eligible[row["name"]])
        jobs[job] = {"run": run, "summary": summary(rows), "settings": rows}
        every += rows
    mean_rate = sum(row["eligible_events"] / row["shots"] for row in every) / len(every)
    by_input: dict[str, list[float]] = {}
    for row in every:
        row["eligible_per_shot_ratio"] = row["eligible_events"] / row["shots"] / mean_rate
        by_input.setdefault(row["name"].split("-")[1], []).append(row["eligible_per_shot_ratio"])
    ratios = [row["eligible_per_shot_ratio"] for row in every]
    return {
        "schema": SCHEMA,
        "case": case.DESIGN,
        "metrics": {
            "nominal_tvd": "total variation distance between served and designed eligible-outcome distributions",
            "success_ratio": "served over designed probability of one photon on each rail pair, modes 4..11 empty",
            "column_modulus_deviation": "largest |abs(served) - abs(designed)| over the two photon-input columns",
        },
        "summary": summary(every),
        "eligible_per_shot": {
            "analysis": ANALYSIS,
            "mean": mean_rate,
            "setting_ratio": {"min": min(ratios), "max": max(ratios)},
            "input_mean_ratio": {label: sum(values) / len(values) for label, values in sorted(by_input.items())},
        },
        "jobs": jobs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    built = record()
    if args.write:
        RECORD.write_text(json.dumps(built, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    else:
        retained = json.loads(RECORD.read_text(encoding="utf-8"))
        difference = case.first_difference(retained, built)
        case.require(difference is None, f"{RECORD.name} differs from the recomputed record at {difference}")
    s = built["summary"]
    print(
        f"{s['settings']} settings: nominal TVD max {s['nominal_tvd']['max']:.2e}, success ratio "
        f"{s['success_ratio']['min']:.5f} to {s['success_ratio']['max']:.5f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
