"""Finish bounded branch-sharing qualification from retained CPU benchmark inputs.

Replay cpu_branching_benchmark.py with --shots 256 first. This runner reuses
its hash-bound QPY inputs, completes folded 2048-shot pairs, runs noisy N21
with 32768 shots, and checks all 18 noiseless laws against the exact oracle.
Use GOROROBA_WORKERS=1 QISKIT_NUM_PROCS=2 PYTHONWARNINGS=error
PYTHONDONTWRITEBYTECODE=1. All credential/service constructors are guarded.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import json
import math
import sys
from pathlib import Path
from time import perf_counter
from typing import Any
from unittest.mock import patch

from cpu_branching_benchmark import forbidden_service, semantic_noise_json


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()
    sys.path.insert(0, str(arguments.repo / "gororoba_quantum"))

    from qiskit import qpy
    from qiskit_aer import AerSimulator

    import live_run
    from diagnostic_experiments import family_contracts
    from qpu_planning_contracts import _fixture

    source_path = arguments.out / "cpu_branching_results.json"
    source_bytes = source_path.read_bytes()
    report: dict[str, Any] = json.loads(source_bytes)
    report["state"] = "running_followup"
    report["input_report_sha256"] = hashlib.sha256(source_bytes).hexdigest()
    report["schedule_revision"] = (
        "Paired N21 at 256 and folded at 2048 have priority; N21 branch-enabled at 32768 establishes scaling. "
        "The initial process was deliberately stopped during optional N21 baseline at 2048; its partial "
        "run has no measured result. Replay the initial script with --shots 256 to avoid that optional run."
    )
    report["followup_execution_limit_seconds"] = 180
    report["qualification_boundary"] = (
        "Noisy finite-shot compatibility checks; numerical equivalence at a scientific margin stays unclaimed. "
        "Noiseless labeled laws are checked independently against the recorded exact oracle."
    )
    output_path = arguments.out / "cpu_branching_qualification.json"

    def checkpoint() -> None:
        temporary = output_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
        temporary.replace(output_path)

    checkpoint()
    for package, version in report["versions"].items():
        if importlib.metadata.version(package) != version:
            raise RuntimeError(f"{package}: dependency version changed after input compilation")
    archive = arguments.out / "cpu_branching_inputs.qpy"
    if hashlib.sha256(archive.read_bytes()).hexdigest() != report["qpy_sha256"]:
        raise RuntimeError("Retained compiled input digest changed")
    with archive.open("rb") as stream:
        circuits = qpy.load(stream)
    members = list(zip(report["circuits"], circuits, strict=True))
    alpha = report["familywise_alpha"]
    with (
        patch.object(live_run, "QiskitRuntimeService", forbidden_service),
        patch.object(live_run, "configure_sampler", forbidden_service),
    ):
        _service, snapshot = _fixture()
        simulators = {}
        for enabled in (False, True):
            simulator = live_run.noise_simulator(snapshot.name, snapshot.backend.target, snapshot.properties)
            simulator.set_options(**report["options"], shot_branching_enable=enabled)
            simulators[enabled] = simulator
        semantic_json = semantic_noise_json(simulators[False].options.noise_model)
        if semantic_json != semantic_noise_json(simulators[True].options.noise_model):
            raise RuntimeError("Independent FakeFez constructions produced different noise channels")
        semantic_digest = hashlib.sha256(semantic_json.encode()).hexdigest()
        recorded_semantic_digest = report.get("noise_semantic_sha256")
        if recorded_semantic_digest is not None and recorded_semantic_digest != semantic_digest:
            raise RuntimeError("FakeFez semantic noise channels changed after the paired benchmark")
        report["noise_semantic_sha256"] = semantic_digest
        report["noise_replay_boundary"] = (
            "Initial raw noise digest includes generated error UUIDs. The initial semantic digest was omitted; "
            "the followup reconstructs the same pinned FakeFez fixture and verifies two independent semantic models. "
            "The corrected initial runner records the semantic digest on future replays."
            if recorded_semantic_digest is None
            else "The retained semantic noise digest matches both independently constructed models."
        )
        (arguments.out / "cpu_branching_noise_semantic.json").write_text(semantic_json + "\n")
        report["fixture_sha256"] = {
            filename: hashlib.sha256((Path(snapshot.backend.dirname) / filename).read_bytes()).hexdigest()
            for filename in (snapshot.backend.conf_filename, snapshot.backend.props_filename)
        }
        checkpoint()

        def sample(simulator: Any, selected: list[Any], shots: int, seed: int) -> dict[str, Any]:
            started = perf_counter()
            result = simulator.run(
                [circuit for _member, circuit in selected], shots=shots, seed_simulator=seed
            ).result()
            wall_seconds = perf_counter() - started
            if not result.success:
                raise RuntimeError(result.to_dict())
            distributions = {}
            total_counts = {}
            for index, (member, circuit) in enumerate(selected):
                counts = result.get_counts(index)
                total_counts[member["name"]] = sum(counts.values())
                if total_counts[member["name"]] != shots:
                    raise RuntimeError(f"{member['name']}: incomplete result shot count")
                probabilities = [0.0] * (1 << circuit.num_clbits)
                for label, count in counts.items():
                    probabilities[int(label.replace(" ", ""), 2)] = count / shots
                distributions[member["name"]] = probabilities
                metadata = result.results[index].metadata
                if metadata.get("method") != "density_matrix" or metadata.get("device") != "CPU":
                    raise RuntimeError("Simulation method or device departed from the qualification contract")
            return {
                "shots": shots,
                "seed": seed,
                "wall_seconds": wall_seconds,
                "distributions": distributions,
                "total_counts": total_counts,
                "metadata": [entry.metadata for entry in result.results],
            }

        schedule = [("folded-qpe", 2048, True), ("folded-qpe", 2048, False), ("n21-feedback", 32768, True)]
        for index, (family, shots, enabled) in enumerate(schedule):
            if any(
                row["family"] == family and row["shots"] == shots and row["shot_branching_enable"] == enabled
                for row in report["cases"]
            ):
                continue
            selected = [(member, circuit) for member, circuit in members if member["family"] == family]
            print(f"run family={family} branching={enabled} shots={shots}", flush=True)
            case = sample(simulators[enabled], selected, shots, 2026101400 + index)
            case.update(family=family, shot_branching_enable=enabled)
            report["cases"].append(case)
            checkpoint()
            print(f"completed seconds={case['wall_seconds']:.6f}", flush=True)

        paired = []
        for family, shots in (("folded-qpe", 256), ("n21-feedback", 256), ("folded-qpe", 2048)):
            rows = {
                row["shot_branching_enable"]: row
                for row in report["cases"]
                if row["family"] == family and row["shots"] == shots
            }
            if set(rows) != {False, True}:
                raise RuntimeError(f"{family}: missing paired {shots}-shot result")
            paired.append((family, shots, rows))
        bin_count = sum(
            len(values) for _family, _shots, rows in paired for values in rows[False]["distributions"].values()
        )
        term_estimates = sum(
            2 * sum(len(contract.terms) for contract in family_contracts(family, 0.08, 0.05, 0.8))
            for family, _shots, _rows in paired
        )
        report["comparisons"] = []
        report["contrast_comparisons"] = []
        for family, shots, rows in paired:
            radius = math.sqrt(2 * math.log(8 * bin_count / alpha) / shots)
            differences = {
                name: [abs(left - right) for left, right in zip(values, rows[True]["distributions"][name], strict=True)]
                for name, values in rows[False]["distributions"].items()
            }
            maximum = max(value for values in differences.values() for value in values)
            report["comparisons"].append(
                {
                    "family": family,
                    "shots": shots,
                    "bin_differences": differences,
                    "max_absolute_bin_difference": maximum,
                    "simultaneous_radius": radius,
                    "compatible": maximum <= radius,
                    "speedup": rows[False]["wall_seconds"] / rows[True]["wall_seconds"],
                }
            )
            score_radius = math.sqrt(math.log(4 * term_estimates / alpha) / (2 * shots))
            for contract in family_contracts(family, 0.08, 0.05, 0.8):
                estimates = {
                    str(enabled): sum(
                        term.sign
                        * sum(
                            value * probability
                            for value, probability in zip(term.values, row["distributions"][term.member], strict=True)
                        )
                        for term in contract.terms
                    )
                    for enabled, row in rows.items()
                }
                contrast_radius = 2 * score_radius * sum(max(term.values) - min(term.values) for term in contract.terms)
                difference = abs(estimates["False"] - estimates["True"])
                report["contrast_comparisons"].append(
                    {
                        "family": family,
                        "shots": shots,
                        "name": contract.name,
                        "estimates": estimates,
                        "absolute_difference": difference,
                        "simultaneous_radius": contrast_radius,
                        "compatible": difference <= contrast_radius,
                    }
                )
        checkpoint()

        ideal_options = copy.deepcopy(report["options"])
        ideal = AerSimulator(**ideal_options, shot_branching_enable=True)
        print("run all 18 noiseless compiled laws with branching=True shots=32768", flush=True)
        ideal_result = sample(ideal, members, 32768, 2026101500)
        exact_radius = math.sqrt(
            math.log(2 * sum(1 << circuit.num_clbits for _member, circuit in members) / alpha) / (2 * 32768)
        )
        exact_differences = {
            member["name"]: max(
                abs(observed - expected)
                for observed, expected in zip(
                    ideal_result["distributions"][member["name"]], member["ideal_law"], strict=True
                )
            )
            for member, _circuit in members
        }
        ideal_result.update(max_bin_differences=exact_differences, simultaneous_radius=exact_radius)
        ideal_result["compatible_with_exact_laws"] = all(value <= exact_radius for value in exact_differences.values())
        feedback = ideal_result["distributions"]["n21_feedback"]
        swapped_oracle = [0.375, 0.125, 0.25, 0.25]
        ideal_result["swapped_n21_label_oracle_rejected"] = (
            max(abs(left - right) for left, right in zip(feedback, swapped_oracle, strict=True)) > exact_radius
        )
        report["noiseless_oracle_check"] = ideal_result
        large = next(
            row
            for row in report["cases"]
            if row["family"] == "n21-feedback" and row["shots"] == 32768 and row["shot_branching_enable"]
        )
        report["large_noisy_run_valid"] = all(
            metadata.get("shot_branching_enabled") is True for metadata in large["metadata"]
        ) and all(count == 32768 for count in large["total_counts"].values())
        checks = [row["compatible"] for row in report["comparisons"] + report["contrast_comparisons"]]
        checks += [
            ideal_result["compatible_with_exact_laws"],
            ideal_result["swapped_n21_label_oracle_rejected"],
            report["large_noisy_run_valid"],
        ]
        report["state"] = "sampled_compatibility_passed" if all(checks) else "failed"
        checkpoint()
        print(
            json.dumps(
                {
                    "state": report["state"],
                    "paired": report["comparisons"],
                    "large_seconds": large["wall_seconds"],
                    "ideal_max_difference": max(exact_differences.values()),
                    "ideal_radius": exact_radius,
                },
                indent=2,
            ),
            flush=True,
        )
        if not all(checks):
            raise RuntimeError("CPU branch-sharing qualification failed")


if __name__ == "__main__":
    main()
