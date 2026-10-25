from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
from bdsc_certificate import close  # noqa: E402

from parallel import ordered_map  # noqa: E402

RUN = ROOT / "results/quandela/runs/ascella-approved-order-pilot-retry"
SUCCESS = ROOT / "results/quandela/runs/ascella-mosaiq-update-order-retry"


def compare_requests(failed: dict[str, Any], successful: dict[str, Any]) -> None:
    """Require identical submissions apart from the per-process routing identifier."""
    if any(not isinstance(body.get("process_id"), str) for body in (failed, successful)):
        raise ValueError("Both requests must retain their process identifiers")
    failed_computation = {key: value for key, value in failed.items() if key != "process_id"}
    successful_computation = {key: value for key, value in successful.items() if key != "process_id"}
    if json.dumps(failed_computation, sort_keys=True) != json.dumps(successful_computation, sort_keys=True):
        raise ValueError("Failed and successful requests differ outside process_id")


def deny_connection(event: str, arguments: tuple[Any, ...]) -> None:
    if event in {"socket.connect", "socket.sendto", "socket.getaddrinfo"}:
        raise RuntimeError("Local replay forbids network connections")


def probability_row(task: tuple[str, int]) -> dict[str, Any]:
    import numpy as np
    import perceval as pcvl
    from perceval.serialization import deserialize

    sys.addaudithook(deny_connection)
    backend, index = task
    manifest = json.loads((RUN / "cases.json").read_text())
    body = json.loads((RUN / "job-body.json").read_text())
    computation = list(deserialize(body["payload"]["computation"]))[index]
    simulator = pcvl.SimulatedComputer(backend)
    result = simulator.probs(computation.experiment, precision=1e-14)
    expected = [real * real + imaginary * imaginary for real, imaginary in manifest["settings"][index]["column"]]
    measured = [0.0] * len(expected)
    for state, probability in result["results"].items():
        occupations = list(state)
        if sum(occupations) != 1:
            raise ValueError("Unexpected non-single-photon local output")
        measured[occupations.index(1)] += float(probability)
    residual = float(np.max(np.abs(np.array(expected) - measured)))
    if residual > 1e-12 or abs(sum(measured) - 1.0) > 1e-12:
        raise ValueError(f"Probability mismatch: {backend}, {index}, {residual}")
    return {
        "backend": backend,
        "setting": index,
        "name": manifest["settings"][index]["name"],
        "probabilities": measured,
        "max_absolute_error": residual,
    }


def sample_iterator(backend: str) -> dict[str, Any]:
    import perceval as pcvl
    from perceval.serialization import deserialize

    sys.addaudithook(deny_connection)
    pcvl.random_seed(20261023)
    body = json.loads((RUN / "job-body.json").read_text())
    computation = deserialize(body["payload"]["computation"])
    result = pcvl.SimulatedComputer(backend).execute(computation)
    counts = [sum(row["results"].values()) for row in result["results_list"]]
    if counts != [8192] * 8:
        raise ValueError(f"Local iterator sample mismatch: {backend}: {counts}")
    return {"backend": backend, "samples_per_setting": counts, "samples_total": sum(counts)}


def analyze() -> dict[str, Any]:
    sys.addaudithook(deny_connection)
    compare_requests(
        json.loads((RUN / "job-body.json").read_text()), json.loads((SUCCESS / "job-body.json").read_text())
    )
    probabilities = ordered_map(
        probability_row, [(backend, index) for backend in ("SLOS", "Naive") for index in range(8)], min_items=1
    )
    samples = ordered_map(sample_iterator, ["SLOS", "Naive"], min_items=1)
    report = {
        "schema": "ascella-local-serialized-replay-v1",
        "boundary": (
            "Ideal local Perceval simulation of the retained sent computation; "
            "hardware instruments and their configuration are absent."
        ),
        "manifest_sha256": hashlib.sha256((RUN / "cases.json").read_bytes()).hexdigest(),
        "job_body_sha256": hashlib.sha256((RUN / "job-body.json").read_bytes()).hexdigest(),
        "request_comparison": {"equal_except": ["process_id"], "matched": True},
        "seed": 20261023,
        "versions": {name: importlib.metadata.version(name) for name in ("perceval-quandela", "exqalibur")},
        "probability_checks": probabilities,
        "iterator_checks": samples,
    }
    paths = [
        Path(__file__).resolve(),
        ROOT / "gororoba_quantum/parallel.py",
        ROOT / "scripts/bdsc_certificate.py",
        RUN / "cases.json",
        RUN / "job-body.json",
        SUCCESS / "job-body.json",
    ]
    report["source_sha256"] = {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Replay the retained Ascella request locally with network connections forbidden."
    )
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("replay-ordered-map-cancel.json"))
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    report = analyze()
    if arguments.check:
        close(json.loads(arguments.out.read_text()), report, "Ascella local serialized request replay")
    else:
        arguments.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"Validated {len(report['probability_checks'])} probability checks and two sample iterators")


if __name__ == "__main__":
    main()
