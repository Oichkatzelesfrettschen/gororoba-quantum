"""Replay the failed simulator reuse sequence, then repeat fresh full-family batches."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import io
import json
import platform
import sys
from pathlib import Path
from time import perf_counter
from typing import Any
from unittest.mock import patch

from cpu_branching_rca import canonical_channels, forbidden_service


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.repo / "gororoba_quantum"))
    from qiskit import qpy

    import live_run
    from qpu_planning_contracts import _fixture

    qualification_path = args.out / "cpu_branching_qualification.json"
    qualification = json.loads(qualification_path.read_text())
    if platform.python_version() != qualification["python"]:
        raise RuntimeError("Reuse probe Python version differs from retained qualification")
    for package, version in qualification["versions"].items():
        if importlib.metadata.version(package) != version:
            raise RuntimeError(f"{package}: installed version differs from the retained qualification")
    archive = args.out / "cpu_branching_inputs.qpy"
    if hashlib.sha256(archive.read_bytes()).hexdigest() != qualification["qpy_sha256"]:
        raise RuntimeError("Reuse probe received different circuit bytes")
    with archive.open("rb") as stream:
        circuits = qpy.load(stream)
    members = list(zip(qualification["circuits"], circuits, strict=True))
    families = {
        family: [(member, circuit) for member, circuit in members if member["family"] == family]
        for family in ("folded-qpe", "n21-feedback")
    }
    reference_channels = canonical_channels((args.out / "cpu_branching_noise_semantic.json").read_text())
    report: dict[str, Any] = {
        "state": "running",
        "execution_limit_seconds": 360,
        "qpy_sha256": qualification["qpy_sha256"],
        "qualification_input_sha256": hashlib.sha256(qualification_path.read_bytes()).hexdigest(),
        "noise_channel_multiset_sha256": hashlib.sha256(reference_channels.encode()).hexdigest(),
        "options": qualification["options"],
        "cases": [],
        "scope": "Exact original reuse prefix through failed folded2048 call; three fresh32768 trials per family",
    }
    output = args.out / "cpu_branching_reuse_probe.json"

    def checkpoint() -> None:
        temporary = output.with_suffix(".tmp")
        temporary.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
        temporary.replace(output)

    def circuit_digest() -> str:
        stream = io.BytesIO()
        qpy.dump(circuits, stream)
        return hashlib.sha256(stream.getvalue()).hexdigest()

    checkpoint()
    with (
        patch.object(live_run, "QiskitRuntimeService", forbidden_service),
        patch.object(live_run, "configure_sampler", forbidden_service),
    ):
        _service, snapshot = _fixture()
        for filename, expected_digest in qualification["fixture_sha256"].items():
            observed_digest = hashlib.sha256((Path(snapshot.backend.dirname) / filename).read_bytes()).hexdigest()
            if observed_digest != expected_digest:
                raise RuntimeError(f"{filename}: FakeFez fixture differs from the retained qualification")

        def make_simulator(enabled: bool) -> Any:
            simulator = live_run.noise_simulator(snapshot.name, snapshot.backend.target, snapshot.properties)
            channels = canonical_channels(json.dumps(simulator.options.noise_model.to_dict(serializable=True)))
            if channels != reference_channels:
                raise RuntimeError("Reuse probe changed a retained noise channel")
            simulator.set_options(**report["options"], shot_branching_enable=enabled)
            expected = {**report["options"], "shot_branching_enable": enabled}
            if any(getattr(simulator.options, name) != value for name, value in expected.items()):
                raise RuntimeError("Reuse probe simulator options differ from their declared values")
            return simulator

        def run_case(simulator: Any, family: str, enabled: bool, shots: int, seed: int, mode: str) -> None:
            selected = families[family]
            before = circuit_digest()
            print(f"mode={mode} family={family} branching={enabled} shots={shots}", flush=True)
            started = perf_counter()
            result = simulator.run(
                [circuit for _member, circuit in selected], shots=shots, seed_simulator=seed
            ).result()
            elapsed = perf_counter() - started
            if not result.success:
                raise RuntimeError(result.to_dict())
            distributions = {}
            counts_total = {}
            for index, (member, circuit) in enumerate(selected):
                counts = result.get_counts(index)
                counts_total[member["name"]] = sum(counts.values())
                if counts_total[member["name"]] != shots:
                    raise RuntimeError("Reuse probe received an incomplete shot count")
                probabilities = [0.0] * (1 << circuit.num_clbits)
                for label, count in counts.items():
                    probabilities[int(label.replace(" ", ""), 2)] = count / shots
                distributions[member["name"]] = probabilities
            after = circuit_digest()
            row = {
                "mode": mode,
                "family": family,
                "shot_branching_enable": enabled,
                "shots": shots,
                "seed": seed,
                "wall_seconds": elapsed,
                "distributions": distributions,
                "counts_total": counts_total,
                "qpy_before": before,
                "qpy_after": after,
                "qpy_identical": before == after,
                "metadata": [entry.metadata for entry in result.results],
            }
            report["cases"].append(row)
            checkpoint()
            print(
                json.dumps(
                    {
                        "seconds": elapsed,
                        "qpy_identical": before == after,
                        "target": distributions.get("qpe_archived_s1", distributions.get("n21_feedback")),
                    }
                ),
                flush=True,
            )

        reused = {enabled: make_simulator(enabled) for enabled in (False, True)}
        original_sequence = [
            ("folded-qpe", False, 16, 2026101200),
            ("folded-qpe", True, 16, 2026101201),
            ("n21-feedback", False, 16, 2026101200),
            ("n21-feedback", True, 16, 2026101201),
            ("folded-qpe", False, 256, 2026101300),
            ("folded-qpe", True, 256, 2026101301),
            ("n21-feedback", False, 256, 2026101302),
            ("n21-feedback", True, 256, 2026101303),
            ("folded-qpe", True, 2048, 2026101311),
        ]
        for family, enabled, shots, seed in original_sequence:
            run_case(reused[enabled], family, enabled, shots, seed, "original_reused_sequence")
        for repeat in range(3):
            for family_index, family in enumerate(families):
                run_case(
                    make_simulator(True),
                    family,
                    True,
                    32768,
                    2026101600 + 2 * repeat + family_index,
                    f"fresh_trial_{repeat}",
                )
        report["state"] = "completed"
        checkpoint()


if __name__ == "__main__":
    main()
