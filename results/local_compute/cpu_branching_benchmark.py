"""Compare CPU branch sharing on real diagnostic replicas with FakeFez noise.

Run with PYTHONDONTWRITEBYTECODE=1, PYTHONWARNINGS=error, and
GOROROBA_WORKERS=1. This program constructs only a FakeFez-backed service
fixture and replaces credential service and Sampler constructors with guards.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import platform
import subprocess
import sys
from pathlib import Path
from time import perf_counter
from typing import Any
from unittest.mock import patch


def forbidden_service(*args: Any, **kwargs: Any) -> Any:
    del args, kwargs
    raise RuntimeError("The CPU benchmark reached a credential or submission constructor")


def semantic_noise_json(model: Any) -> str:
    """Exclude generated error UUIDs while retaining channel parameters and qubit maps."""
    document = model.to_dict(serializable=True)
    for error in document["errors"]:
        if error.get("type") == "qerror":
            error.pop("id", None)
    return json.dumps(document, sort_keys=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--shots", type=int, nargs="+", default=[256, 2048])
    arguments = parser.parse_args()
    arguments.out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(arguments.repo / "gororoba_quantum"))

    from qiskit import qpy

    import live_run
    import qpu_planning
    from qpe_diagnostics import ideal_compiled_probabilities
    from qpu_planning_contracts import _args, _fixture

    output_path = arguments.out / "cpu_branching_results.json"
    report: dict[str, Any] = {
        "state": "running",
        "python": platform.python_version(),
        "versions": {
            name: importlib.metadata.version(name) for name in ("qiskit", "qiskit-aer", "qiskit-ibm-runtime", "numpy")
        },
        "source_commit": subprocess.check_output(
            ["git", "-C", str(arguments.repo), "rev-parse", "HEAD"], text=True
        ).strip(),
        "options": {
            "device": "CPU",
            "method": "density_matrix",
            "precision": "double",
            "max_parallel_threads": 2,
            "max_parallel_experiments": 1,
            "max_parallel_shots": 2,
            "shot_branching_sampling_enable": False,
        },
        "shots": arguments.shots,
        "familywise_alpha": 1e-6,
        "timing_boundary": "Aer run through result retrieval; compilation and simulator creation excluded",
        "timing_limitation": "single observation per configuration; concurrent host work is uncontrolled",
        "cases": [],
        "warmups": [],
    }

    def checkpoint() -> None:
        temporary = output_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
        temporary.replace(output_path)

    checkpoint()
    with (
        patch.object(live_run, "QiskitRuntimeService", forbidden_service),
        patch.object(live_run, "configure_sampler", forbidden_service),
    ):
        _service, snapshot = _fixture()
        families: dict[str, list[Any]] = {}
        preparation_start = perf_counter()
        for family in ("folded-qpe", "n21-feedback"):
            trace: dict[str, Any] = {}
            candidates = qpu_planning.family_candidates(live_run, [snapshot], _args(family), trace)
            if not candidates:
                raise RuntimeError(trace)
            choices, _configuration = candidates[0]
            families[family] = [entry for choice in choices for entry in choice.entries]
        report["compile_seconds"] = perf_counter() - preparation_start
        all_circuits = [replica for entries in families.values() for entry in entries for replica in entry.replicas]
        archive_path = arguments.out / "cpu_branching_inputs.qpy"
        with archive_path.open("wb") as stream:
            qpy.dump(all_circuits, stream)
        report["qpy_sha256"] = hashlib.sha256(archive_path.read_bytes()).hexdigest()
        report["circuits"] = []
        for family, entries in families.items():
            for entry in entries:
                if len(entry.replicas) != 1:
                    raise RuntimeError("The bounded benchmark requires one calibrated replica per member")
                circuit = entry.replicas[0]
                exact = ideal_compiled_probabilities(circuit)
                if any(abs(observed - expected) > 1e-10 for observed, expected in zip(exact, entry.ideal, strict=True)):
                    raise RuntimeError(f"{entry.name}: compiled ideal differs from its labeled law")
                active = {
                    qubit
                    for instruction in circuit.data
                    if instruction.operation.name != "barrier"
                    for qubit in instruction.qubits
                }
                report["circuits"].append(
                    {
                        "family": family,
                        "name": entry.name,
                        "declared_qubits": circuit.num_qubits,
                        "active_qubits": len(active),
                        "clbits": circuit.num_clbits,
                        "top_level_operations": len(circuit.data),
                        "ideal_law": exact,
                    }
                )

        simulators = {}
        for enabled in (False, True):
            simulator = live_run.noise_simulator(snapshot.name, snapshot.backend.target, snapshot.properties)
            simulator.set_options(**report["options"], shot_branching_enable=enabled)
            simulators[enabled] = simulator
        noise_json = json.dumps(simulators[False].options.noise_model.to_dict(serializable=True), sort_keys=True)
        report["noise_sha256"] = hashlib.sha256(noise_json.encode()).hexdigest()
        semantic_json = semantic_noise_json(simulators[False].options.noise_model)
        report["noise_semantic_sha256"] = hashlib.sha256(semantic_json.encode()).hexdigest()
        (arguments.out / "cpu_branching_noise_semantic.json").write_text(semantic_json + "\n")
        checkpoint()

        def run_case(family: str, enabled: bool, shots: int, seed: int) -> dict[str, Any]:
            entries = families[family]
            circuits = [entry.replicas[0] for entry in entries]
            started = perf_counter()
            result = simulators[enabled].run(circuits, shots=shots, seed_simulator=seed).result()
            elapsed = perf_counter() - started
            if not result.success:
                raise RuntimeError(result.to_dict())
            distributions = {}
            for index, entry in enumerate(entries):
                counts = result.get_counts(index)
                if sum(counts.values()) != shots:
                    raise RuntimeError(f"{entry.name}: simulator returned an incomplete shot count")
                probabilities = [0.0] * (1 << circuits[index].num_clbits)
                for label, count in counts.items():
                    probabilities[int(label.replace(" ", ""), 2)] = count / shots
                distributions[entry.name] = probabilities
                metadata = result.results[index].metadata
                if metadata.get("method") != "density_matrix" or metadata.get("device") != "CPU":
                    raise RuntimeError(f"{entry.name}: unexpected execution method or device {metadata}")
            return {
                "family": family,
                "shot_branching_enable": enabled,
                "shots": shots,
                "seed": seed,
                "wall_seconds": elapsed,
                "distributions": distributions,
                "metadata": [entry.metadata for entry in result.results],
            }

        for family in families:
            for enabled in (False, True):
                print(f"warmup family={family} branching={enabled} shots=16", flush=True)
                report["warmups"].append(run_case(family, enabled, 16, 2026101200 + int(enabled)))
                checkpoint()
        for tier_index, shots in enumerate(arguments.shots):
            order = (False, True) if tier_index % 2 == 0 else (True, False)
            for family_index, family in enumerate(families):
                for enabled in order:
                    print(f"run family={family} branching={enabled} shots={shots}", flush=True)
                    case = run_case(
                        family, enabled, shots, 2026101300 + 10 * tier_index + 2 * family_index + int(enabled)
                    )
                    report["cases"].append(case)
                    checkpoint()
                    print(f"completed seconds={case['wall_seconds']:.6f}", flush=True)

        comparison_count = len(arguments.shots) * sum(1 << circuit.num_clbits for circuit in all_circuits)
        report["comparison_count"] = comparison_count
        report["comparisons"] = []
        for shots in arguments.shots:
            radius = math.sqrt(2 * math.log(4 * comparison_count / report["familywise_alpha"]) / shots)
            for family in families:
                rows = {
                    row["shot_branching_enable"]: row
                    for row in report["cases"]
                    if row["family"] == family and row["shots"] == shots
                }
                maximum = max(
                    abs(reference - observed)
                    for name in rows[False]["distributions"]
                    for reference, observed in zip(
                        rows[False]["distributions"][name], rows[True]["distributions"][name], strict=True
                    )
                )
                report["comparisons"].append(
                    {
                        "family": family,
                        "shots": shots,
                        "max_absolute_bin_difference": maximum,
                        "simultaneous_radius": radius,
                        "passed": maximum <= radius,
                        "speedup": rows[False]["wall_seconds"] / rows[True]["wall_seconds"],
                    }
                )
        report["state"] = "passed" if all(row["passed"] for row in report["comparisons"]) else "failed"
        checkpoint()
        print(json.dumps(report["comparisons"], indent=2), flush=True)
        if report["state"] != "passed":
            raise RuntimeError("Labeled distributions exceed the simultaneous sampling bound")


if __name__ == "__main__":
    main()
