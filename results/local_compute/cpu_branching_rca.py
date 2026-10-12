"""Isolate the retained folded-QPE noisy branch-sharing discrepancy."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import sys
from pathlib import Path
from time import perf_counter
from typing import Any
from unittest.mock import patch


def forbidden_service(*args: Any, **kwargs: Any) -> Any:
    del args, kwargs
    raise RuntimeError("RCA reached a credential or submission constructor")


def canonical_channels(document: str) -> str:
    """Canonicalize process-dependent channel-list order after generated IDs are removed."""
    decoded = json.loads(document)
    for error in decoded["errors"]:
        if error.get("type") == "qerror":
            error.pop("id", None)
    decoded["errors"].sort(key=lambda error: json.dumps(error, sort_keys=True))
    return json.dumps(decoded, sort_keys=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.repo / "gororoba_quantum"))
    from qiskit import qpy

    import live_run
    from qpu_planning_contracts import _fixture

    qualification = json.loads((args.out / "cpu_branching_qualification.json").read_text())
    if platform.python_version() != qualification["python"]:
        raise RuntimeError("RCA Python version differs from the retained qualification")
    for package, version in qualification["versions"].items():
        if importlib.metadata.version(package) != version:
            raise RuntimeError(f"{package}: RCA dependency version differs from retained qualification")
    if hashlib.sha256((args.out / "cpu_branching_inputs.qpy").read_bytes()).hexdigest() != qualification["qpy_sha256"]:
        raise RuntimeError("RCA circuit archive differs from the retained qualification inputs")
    with (args.out / "cpu_branching_inputs.qpy").open("rb") as stream:
        circuits = qpy.load(stream)
    members = list(zip(qualification["circuits"], circuits, strict=True))
    folded = [(member, circuit) for member, circuit in members if member["family"] == "folded-qpe"]
    isolated = [next(pair for pair in folded if pair[0]["name"] == "qpe_archived_s1")]
    selections = {"isolated": isolated, "mixed": folded, "reversed": list(reversed(folded))}
    report: dict[str, Any] = {
        "state": "running",
        "shots": 2048,
        "seed": 2026101311,
        "qpy_sha256": qualification["qpy_sha256"],
        "qualification_input_sha256": hashlib.sha256(
            (args.out / "cpu_branching_qualification.json").read_bytes()
        ).hexdigest(),
        "noise_semantic_sha256": qualification["noise_semantic_sha256"],
        "options": qualification["options"],
        "cases": [],
    }
    output = args.out / "cpu_branching_rca.json"
    recorded_channels = canonical_channels((args.out / "cpu_branching_noise_semantic.json").read_text())
    report["noise_channel_multiset_sha256"] = hashlib.sha256(recorded_channels.encode()).hexdigest()
    report["noise_hash_boundary"] = (
        "The previous semantic digest retained process-dependent error-list order. "
        "RCA compares every saved channel after canonical ordering, with identical numeric parameters."
    )

    def checkpoint() -> None:
        temporary = output.with_suffix(".tmp")
        temporary.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
        temporary.replace(output)

    checkpoint()
    with (
        patch.object(live_run, "QiskitRuntimeService", forbidden_service),
        patch.object(live_run, "configure_sampler", forbidden_service),
    ):
        _service, snapshot = _fixture()
        fixture_hashes = {
            filename: hashlib.sha256((Path(snapshot.backend.dirname) / filename).read_bytes()).hexdigest()
            for filename in (snapshot.backend.conf_filename, snapshot.backend.props_filename)
        }
        if fixture_hashes != qualification["fixture_sha256"]:
            raise RuntimeError("RCA FakeFez fixture differs from the retained delay/calibration inputs")
        report["python"] = platform.python_version()
        report["versions"] = dict(qualification["versions"])
        report["fixture_sha256"] = fixture_hashes
        report["replay_source_sha256"] = {
            source.name: hashlib.sha256(source.read_bytes()).hexdigest()
            for source in sorted((args.repo / "gororoba_quantum").glob("*.py"))
        }
        report["replay_source_boundary"] = (
            "Source-file hashes are captured after import; concurrent source edits remain outside the replay contract."
        )
        checkpoint()
        schedule = [
            (False, 2, 2, "isolated"),
            (True, 2, 2, "isolated"),
            (True, 2, 2, "mixed"),
            (True, 2, 2, "reversed"),
            (True, 1, 1, "isolated"),
            (True, 1, 1, "mixed"),
            (True, 1, 1, "reversed"),
            (True, 2, 1, "mixed"),
            (True, 1, 2, "mixed"),
            (True, 2, 2, "mixed"),
        ]
        for enabled, threads, parallel_shots, selection in schedule:
            simulator = live_run.noise_simulator(snapshot.name, snapshot.backend.target, snapshot.properties)
            semantic_digest = hashlib.sha256(
                canonical_channels(json.dumps(simulator.options.noise_model.to_dict(serializable=True))).encode()
            ).hexdigest()
            if semantic_digest != report["noise_channel_multiset_sha256"]:
                raise RuntimeError("RCA changed its semantic noise model")
            options = {
                **report["options"],
                "max_parallel_threads": threads,
                "max_parallel_shots": parallel_shots,
                "shot_branching_enable": enabled,
            }
            simulator.set_options(**options)
            if any(getattr(simulator.options, name) != value for name, value in options.items()):
                raise RuntimeError("RCA simulator options differ from their recorded configuration")
            selected = selections[selection]
            target_index = next(index for index, pair in enumerate(selected) if pair[0]["name"] == "qpe_archived_s1")
            print(
                f"branching={enabled} threads={threads} parallel_shots={parallel_shots} batch={selection}", flush=True
            )
            start = perf_counter()
            result = simulator.run(
                [circuit for _member, circuit in selected], shots=2048, seed_simulator=report["seed"]
            ).result()
            if not result.success:
                raise RuntimeError(result.to_dict())
            counts = result.get_counts(target_index)
            if sum(counts.values()) != 2048:
                raise RuntimeError("RCA received an incomplete shot count")
            distribution = [0.0] * 4
            for label, count in counts.items():
                distribution[int(label.replace(" ", ""), 2)] = count / 2048
            row = {
                "options": options,
                "selection": selection,
                "target_index": target_index,
                "wall_seconds": perf_counter() - start,
                "distribution": distribution,
                "metadata": result.results[target_index].metadata,
            }
            report["cases"].append(row)
            checkpoint()
            print(json.dumps({key: row[key] for key in ("selection", "wall_seconds", "distribution")}), flush=True)
        report["state"] = "completed"
        checkpoint()


if __name__ == "__main__":
    main()
