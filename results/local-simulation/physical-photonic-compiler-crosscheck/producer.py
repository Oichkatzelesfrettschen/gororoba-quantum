"""Cross-check frozen optical and cQASM circuits on local noiseless simulators."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from importlib.metadata import version
from pathlib import Path
from typing import Any

from parallel import ordered_map

ROOT = Path(__file__).resolve().parents[1]
SEED = 20261022
SHOTS = 1024


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def photonic(item: tuple[str, int]) -> dict[str, Any]:
    import numpy as np
    import perceval as pcvl
    import qd_platform

    directory, index = item
    manifest, specification, _ = qd_platform.load_case(ROOT / directory)
    setting = manifest["settings"][index]
    started = time.monotonic()
    result: dict[str, Any] = {"case": directory, "index": index, "name": setting["name"]}
    try:
        built, _ = qd_platform.template_experiment(manifest, specification)
        chip = built.unitary_circuit()
        for parameter in chip.get_parameters():
            parameter.set_value(setting["circuit_params"][parameter.name])
        operator = np.asarray(setting["operator"]["real"]) + 1j * np.asarray(setting["operator"]["imaginary"])
        actual = np.asarray(chip.compute_unitary())
        source = specification["input_state"].index(1)
        ideal = np.abs(operator[:, source]) ** 2
        distributions = {}
        for name in ("SLOS", "Naive"):
            backend = pcvl.BackendFactory.get_backend(name)
            backend.set_circuit(chip)
            backend.set_input_state(pcvl.BasicState(specification["input_state"]))
            distribution = backend.prob_distribution()
            probabilities = [0.0] * specification["modes"]
            for state, probability in distribution.items():
                probabilities[list(state).index(1)] = float(probability)
            distributions[name] = probabilities
        errors = {name: float(np.max(np.abs(np.asarray(values) - ideal))) for name, values in distributions.items()}
        operator_error = float(np.max(np.abs(actual - operator)))
        result |= {
            "modes": specification["modes"],
            "source": source,
            "ideal": ideal.tolist(),
            "probabilities": distributions,
            "max_probability_errors": errors,
            "full_operator_max_error": operator_error,
            "simulated_counts": np.random.default_rng(SEED + index).multinomial(SHOTS, ideal / ideal.sum()).tolist(),
            "passed": operator_error < 1e-9 and max(errors.values()) < 1e-9,
        }
    except Exception as error:
        result |= {"passed": False, "error": f"{type(error).__name__}: {error}"}
    result["seconds"] = time.monotonic() - started
    print(json.dumps({"progress": result["name"], "passed": result["passed"]}), flush=True)
    return result


def qi_case(item: tuple[str, dict[str, Any]]) -> dict[str, Any]:
    import cqasm.v3x as v3
    import qxelarator
    from qi_toolchain_check import compile_circuit, compiler_configs

    directory, case = item
    path = ROOT / directory / case["file"]
    text = path.read_text()
    result: dict[str, Any] = {"case": str(path.relative_to(ROOT)), "sha256": digest(path)}
    try:
        if result["sha256"] != case["sha256"]:
            raise ValueError("source hash differs from frozen manifest")
        source_errors = json.loads(v3.Analyzer().analyze_string_to_json(text), strict=False).get("errors", [])
        compiled = compile_circuit(text, compiler_configs()["tuna_17"])
        compiled_errors = json.loads(v3.Analyzer().analyze_string_to_json(compiled), strict=False).get("errors", [])
        simulations = {}
        for name, code in (("source", text), ("compiled", compiled)):
            simulation = qxelarator.execute_string(code, iterations=SHOTS, seed=SEED)
            simulations[name] = {
                "counts": simulation.results,
                "shots_done": simulation.shots_done,
                "state": {key: [value.real, value.imag] for key, value in simulation.state.items()},
            }
        expected = case.get("native_probabilities")
        if expected is None:
            expected = [0.0] * 4
            expected[3 if case["prepared"] else 0] = 1.0
        errors = {}
        for name, simulation in simulations.items():
            probabilities = [0.0] * len(expected)
            for state, amplitude in simulation["state"].items():
                probabilities[int(state, 2)] = amplitude[0] ** 2 + amplitude[1] ** 2
            errors[name] = max(abs(actual - wanted) for actual, wanted in zip(probabilities, expected, strict=True))
        result |= {
            "source_errors": source_errors,
            "compiled_errors": compiled_errors,
            "compiled": compiled,
            "simulations": simulations,
            "native_probability_errors": errors,
            "passed": not source_errors and not compiled_errors and max(errors.values()) < 1e-9,
        }
    except Exception as error:
        result |= {"passed": False, "error": f"{type(error).__name__}: {error}"}
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--qi-worker", action="store_true")
    arguments = parser.parse_args()
    arguments.out.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    record: dict[str, Any]
    inputs: list[Any]
    if arguments.qi_worker:
        inputs = []
        for manifest_path in sorted(
            (ROOT / "results/quantum_inspire/runs/tuna17-quaternion-order-noise").glob("order-batch-*/cases.json")
        ):
            inputs.extend(
                (str(manifest_path.parent.relative_to(ROOT)), case)
                for case in json.loads(manifest_path.read_text())["circuits"]
            )
        rows = ordered_map(qi_case, inputs, min_items=1)
        record = {"versions": {name: version(name) for name in ("opensquirrel", "libqasm", "qxelarator")}, "rows": rows}
    else:
        from qi_stack import probe, run

        inputs = []
        identities = {}
        for manifest_path in sorted((ROOT / "results/hypercomplex/photonic-successors").glob("*/*/cases.json")):
            manifest = json.loads(manifest_path.read_text())
            identities[str(manifest_path.relative_to(ROOT))] = digest(manifest_path)
            circuit_path = manifest_path.parent / manifest["circuit"]["file"]
            identities[str(circuit_path.relative_to(ROOT))] = digest(circuit_path)
            inputs.extend(
                (str(manifest_path.parent.relative_to(ROOT)), index) for index in range(len(manifest["settings"]))
            )
        rows = ordered_map(photonic, inputs, min_items=1)
        stack = probe()
        if not stack.available:
            raise RuntimeError(stack.reason)
        run([str(Path(__file__).relative_to(ROOT)), "--qi-worker", "--out", str(arguments.out)])
        record = {
            "rows": rows,
            "source_sha256": identities,
            "versions": {name: version(name) for name in ("perceval-quandela", "exqalibur", "numpy")},
        }
    record |= {
        "schema": "local-photonic-compiler-simulation-v1",
        "python": platform.python_version(),
        "runner_sha256": digest(Path(__file__)),
        "seed": SEED,
        "shots": SHOTS,
        "elapsed_seconds": time.monotonic() - started,
        "evidence_class": "local noiseless simulation; sampled counts are simulated",
        "authorization": "User approved additive background simulation on this machine while Ascella waits",
        "boundary": "Mathematical and compiler checks; hardware loss, drift and device conformance remain unmeasured",
        "dialects": {
            "cQASM": "3.0 through libqasm and OpenSquirrel",
            "OpenQASM": "absent from the selected frozen cases",
        },
    }
    destination = arguments.out / ("qi.json" if arguments.qi_worker else "photonic.json")
    destination.write_text(json.dumps(record, indent=2) + "\n")
    print(
        json.dumps({"record": destination.name, "rows": len(rows), "passed": sum(row["passed"] for row in rows)}),
        flush=True,
    )


if __name__ == "__main__":
    main()
