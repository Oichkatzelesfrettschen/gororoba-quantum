"""Cross-check frozen optical and cQASM circuits on local noiseless simulators."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import sys
import time
import warnings
from importlib.metadata import version
from pathlib import Path
from typing import Any

from parallel import ordered_map

ROOT = Path(__file__).resolve().parents[1]
SEED = 20261022
SHOTS = 1024
DEFAULT_WRITER_RESIDUALS = {
    f"results/quantum_inspire/runs/tuna17-quaternion-order-noise/order-batch-{batch:02d}/{name}.cq"
    for batch, name in (
        (2, "order-i0-j1-representative0"),
        (3, "order-i0-j1-representative1"),
        (6, "order-i1-j1-representative0"),
        (7, "order-i1-j1-representative1"),
    )
}


def qi_warning_policy() -> None:
    """Fail warnings except the pinned libqasm/qxelarator SWIG type diagnostic."""
    warnings.simplefilter("error")
    warnings.filterwarnings("ignore", r"builtin type \w+ has no __module__ attribute", DeprecationWarning)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def terminal_unitary(text: str) -> str:
    """Remove only terminal whole-line measurements; reject later operations."""
    kept = []
    measured = False
    for line in text.splitlines():
        statement = line.partition("//")[0].strip()
        if re.fullmatch(r"b(?:\[[0-9:, ]+\])?\s*=\s*measure\s+q(?:\[[0-9:, ]+\])?", statement):
            measured = True
            continue
        if re.search(r"\bmeasure\b", statement):
            raise ValueError("unitary probe requires supported terminal measurements")
        if measured and statement:
            raise ValueError("unitary probe requires terminal measurements")
        kept.append(line)
    if not measured:
        raise ValueError("unitary probe requires terminal measurements")
    return "\n".join(kept) + "\n"


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
    qi_warning_policy()
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
        if case.get("_full_precision"):
            from opensquirrel_fullprecision import compile_circuit as precise_compile

            compiled = precise_compile(text, compiler_configs()["tuna_17"])
        else:
            compiled = compile_circuit(text, compiler_configs()["tuna_17"])
        compiled_errors = json.loads(v3.Analyzer().analyze_string_to_json(compiled), strict=False).get("errors", [])
        simulations = {}
        for name, code in (("source", text), ("compiled", compiled)):
            simulation = qxelarator.execute_string(code, iterations=SHOTS, seed=SEED)
            probe_code = terminal_unitary(code)
            probe_result = qxelarator.execute_string(probe_code, iterations=1, seed=SEED)
            simulations[name] = {
                "counts": simulation.results,
                "shots_done": simulation.shots_done,
                "unitary_probe": probe_code,
                "unitary_probe_sha256": hashlib.sha256(probe_code.encode()).hexdigest(),
                "state": {key: [value.real, value.imag] for key, value in probe_result.state.items()},
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
    parser.add_argument("--full-precision", action="store_true")
    arguments = parser.parse_args()
    destination = arguments.out / ("qi.json" if arguments.qi_worker else "photonic.json")
    if destination.exists():
        raise FileExistsError(
            f"retain the existing simulation record and choose a fresh output directory: {destination}"
        )
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
                (str(manifest_path.parent.relative_to(ROOT)), case | {"_full_precision": arguments.full_precision})
                for case in json.loads(manifest_path.read_text())["circuits"]
            )
        rows = ordered_map(qi_case, inputs, min_items=1)
        record = {"versions": {name: version(name) for name in ("opensquirrel", "libqasm", "qxelarator")}, "rows": rows}
        if arguments.full_precision:
            record["exporter"] = {
                "path": "scripts/opensquirrel_fullprecision.py",
                "sha256": digest(ROOT / "scripts/opensquirrel_fullprecision.py"),
                "precision": "17 significant decimal digits, public IRVisitor, finite native pilot contract",
            }
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
        record = {
            "rows": rows,
            "source_sha256": identities,
            "versions": {name: version(name) for name in ("perceval-quandela", "exqalibur", "numpy")},
        }
        stack = probe()
        if not stack.available:
            print(stack.reason, file=sys.stderr)
            record["qi_worker_error"] = "pinned QI stack unavailable"
        else:
            try:
                run(
                    [
                        "-B",
                        "-W",
                        "error",
                        str(Path(__file__).relative_to(ROOT)),
                        "--qi-worker",
                        "--out",
                        str(arguments.out),
                    ]
                )
            except SystemExit as error:
                print(str(error), file=sys.stderr)
                record["qi_worker_error"] = "QI subprocess failed"
                record["qi_worker_record_present"] = (arguments.out / "qi.json").is_file()
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
    destination.write_text(json.dumps(record, indent=2) + "\n")
    print(
        json.dumps({"record": destination.name, "rows": len(rows), "passed": sum(row["passed"] for row in rows)}),
        flush=True,
    )
    execution_errors = any(row.get("error") or row.get("source_errors") or row.get("compiled_errors") for row in rows)
    failed_cases = {row.get("case", "") for row in rows if not row["passed"]}
    expected_residuals = (
        arguments.qi_worker and not arguments.full_precision and failed_cases == DEFAULT_WRITER_RESIDUALS
    )
    if record.get("qi_worker_error") or execution_errors or (failed_cases and not expected_residuals):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
