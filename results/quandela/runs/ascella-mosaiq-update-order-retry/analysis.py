"""Replay the four-returned-mode Ascella order acquisition and compiled metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qd_belenos_mesh as mesh  # noqa: E402
import qd_platform as qd  # noqa: E402
from bdsc_certificate import close  # noqa: E402
from photonic_compilation_audit import _elements  # noqa: E402

from parallel import ordered_map  # noqa: E402


def observation(task: tuple[dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    setting, entry = task
    counts = [0] * 4
    vacuum = multiple = 0
    for state, count in entry["counts"].items():
        if not re.fullmatch(r"\d+,\d+,\d+,\d+", state) or type(count) is not int or count < 0:
            raise ValueError("Counts require four nonnegative integer occupations and integer frequencies")
        occupation = [int(value) for value in state.split(",")]
        total = sum(occupation)
        if total == 1:
            counts[occupation.index(1)] += count
        elif total == 0:
            vacuum += count
        else:
            multiple += count
    accepted = sum(counts)
    if accepted == 0:
        raise ValueError("The conditional distribution requires accepted samples")
    measured = np.asarray(counts) / accepted
    requested = np.asarray([real * real + imaginary * imaginary for real, imaginary in setting["column"]])
    if requested.shape != (4,) or not np.isfinite(requested).all() or abs(float(requested.sum()) - 1) > 1e-12:
        raise ValueError("Requested probabilities require four normalized finite entries")
    fields = entry["result_fields"]
    match = re.fullmatch(r":PCVL:BasicState:\|([01](?:,[01])*)>", fields["computed_input"])
    occupations = [int(value) for value in match[1].split(",")] if match else []
    if len(occupations) != 12 or sum(occupations) != 1:
        raise ValueError("Compiled input requires twelve modes and one photon")
    elements = _elements(fields["computed_circuit"])
    experiment_elements = _elements(fields["computed_experiment"])
    for kind, mode, _ in elements + experiment_elements:
        if kind not in {"bs", "ps"} or not 0 <= mode < (11 if kind == "bs" else 12):
            raise ValueError("Compiled components exceed the twelve-mode Ascella domain")
    unitary = mesh.unitary(elements, [value for kind, _, value in elements if kind == "ps"])
    probabilities = np.abs(unitary[:, occupations.index(1)]) ** 2
    if not np.isfinite(probabilities).all() or abs(float(probabilities.sum()) - 1) > 1e-9:
        raise ValueError("Compiled probabilities fail normalization")
    if np.any(probabilities[12:] != 0) or float(probabilities[:4].sum()) <= 0:
        raise ValueError("Compiled probabilities exceed the physical domain or lack returned support")
    compiled = probabilities[:4] / probabilities[:4].sum()
    return {
        "name": setting["name"],
        "accepted_samples": accepted,
        "vacuum_exclusions": vacuum,
        "multiple_occupation_exclusions": multiple,
        "counts": counts,
        "requested_probabilities": requested.tolist(),
        "measured_conditional_probabilities": measured.tolist(),
        "compiled_conditional_probabilities": compiled.tolist(),
        "measured_vs_requested_tvd": float(np.abs(measured - requested).sum() / 2),
        "compiled_vs_requested_tvd": float(np.abs(compiled - requested).sum() / 2),
        "measured_vs_compiled_tvd": float(np.abs(measured - compiled).sum() / 2),
        "compiled_metadata_probability_outside_returned_modes": float(probabilities[4:12].sum()),
        "experiment_mesh_matches_circuit": elements == experiment_elements,
        "provider_metadata": {key: fields[key] for key in ("physical_perf", "global_perf", "nb_shots_used")},
    }


def advertised_deployment(snapshot: dict[str, Any]) -> str:
    specs = snapshot["processor"]["specs"]
    version = specs["software_versions"]["mosaiq-arcturus"]
    if specs["processor_name"] != "qpu:ascella" or version != "2.1.5.2.post4":
        raise ValueError("The recovery acquisition requires the retained Ascella deployment advertisement")
    return str(version)


def analyze(directory: Path) -> dict[str, Any]:
    qd.run_facts(directory)
    deployment = advertised_deployment(json.loads((directory / "platform-before-submission.json").read_text()))
    manifest = json.loads((directory / "cases.json").read_text())
    results = json.loads((directory / "results.json").read_text())
    submission = json.loads((directory / "submission.json").read_text())
    if submission["platform"] != "qpu:ascella" or results["status"]["status"] != "completed":
        raise ValueError("Analysis requires a completed Ascella acquisition")
    if len(manifest["settings"]) != 8 or len(results["iterations"]) != 8:
        raise ValueError("Analysis requires the eight-setting order pilot")
    if any(entry["result_fields"]["final_mode_number"] != 4 for entry in results["iterations"]):
        raise ValueError("Analysis requires four returned modes")
    rows = ordered_map(observation, list(zip(manifest["settings"], results["iterations"], strict=True)), min_items=1)
    dependencies = [
        "scripts/bdsc_certificate.py",
        "scripts/qd_platform.py",
        "scripts/qd_belenos_mesh.py",
        "scripts/photonic_compilation_audit.py",
        "gororoba_quantum/parallel.py",
    ]
    paths = [
        directory / name
        for name in (
            "platform-before-submission.json",
            "cases.json",
            "circuit.json",
            "job-body.json",
            "submission.json",
            "results.json",
            "raw/result.json",
        )
    ]
    paths += [Path(__file__).resolve(), *(ROOT / name for name in dependencies)]
    return {
        "schema": "ascella-four-output-order-analysis-v1",
        "job_id": results["job_id"],
        "advertised_mosaiq_arcturus": deployment,
        "deployment_boundary": "Pre-submission provider advertisement; the snapshot does not establish "
        "the executing instrument version or the cause of recovery.",
        "conditioning": "Occupation sum one within the four returned modes of twelve-mode Ascella.",
        "boundary": "Compiled meshes and performance fields are provider metadata. Four-output counts cannot "
        "measure full-output leakage, absolute calibrated loss, drift, or physical phase reconstruction.",
        "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
        "observations": rows,
    }


def check_report_types(retained: Any, fresh: Any) -> None:
    """Preserve JSON scalar domains before the shared numerical comparison."""
    if type(retained) is not type(fresh):
        raise ValueError("Retained analysis changes a JSON value type")
    if isinstance(fresh, dict):
        if retained.keys() != fresh.keys():
            raise ValueError("Retained analysis changes object keys")
        for key in fresh:
            check_report_types(retained[key], fresh[key])
    elif isinstance(fresh, list):
        if len(retained) != len(fresh):
            raise ValueError("Retained analysis changes list length")
        for recorded, computed in zip(retained, fresh, strict=True):
            check_report_types(recorded, computed)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    directory = Path(__file__).resolve().parent
    report = analyze(directory)
    output = directory / "analysis.json"
    if arguments.check:
        # Match the repository photonic replays: floats tolerate libm rounding;
        # counts, labels and source digests retain exact comparison.
        retained = json.loads(output.read_text())
        check_report_types(retained, report)
        close(retained, report, "Ascella four-output order analysis")
    else:
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"Validated {len(report['observations'])} Ascella observations")


if __name__ == "__main__":
    main()
