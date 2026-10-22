"""Validate retained local simulator evidence and optionally replay the pinned QI stack."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "ci"))
from pins import read_pins  # noqa: E402

from parallel import ordered_map  # noqa: E402

BUNDLE = ROOT / "results/local-simulation"
QI_BUNDLES = (
    ("photonic-compiler-crosscheck", False, False),
    ("physical-photonic-compiler-crosscheck", False, False),
    ("terminal-unitary-compiler-crosscheck", False, True),
    ("validated-terminal-unitary-compiler-crosscheck", False, True),
    ("fullprecision-compiler-crosscheck", True, True),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory() -> dict[str, str]:
    visible = subprocess.check_output(
        ["git", "ls-files", "--cached", "-z", "--", "results/local-simulation"],
        cwd=ROOT,
    )
    return {
        path.relative_to(BUNDLE).as_posix(): sha(path)
        for path in sorted({ROOT / name.decode() for name in visible.split(b"\0") if name})
        if path.name != "artifacts.json"
    }


def load(name: str) -> dict[str, Any]:
    return json.loads((BUNDLE / name).read_text())


def check_probabilities(values: list[float]) -> None:
    if any(not math.isfinite(value) or value < 0 or value > 1 + 1e-12 for value in values):
        raise ValueError("probabilities must be finite and bounded")
    if abs(sum(values) - 1) > 1e-12:
        raise ValueError("probabilities must retain unit normalization")


def check_qi(arguments: tuple[dict[str, Any], bool, bool]) -> None:
    row, precise, terminal = arguments
    source = ROOT / row["case"]
    manifest = json.loads(source.with_name("cases.json").read_text())
    case = next(case for case in manifest["circuits"] if case["file"] == source.name)
    if sha(source) != row["sha256"] or row["sha256"] != case["sha256"]:
        raise ValueError("QI frozen source identity changed")
    expected = case.get("native_probabilities")
    if expected is None:
        expected = [0.0] * 4
        expected[3 if case["prepared"] else 0] = 1.0
    if row["source_errors"] or row["compiled_errors"]:
        raise ValueError("retained cQASM parser errors")
    errors = {}
    if set(row["simulations"]) != {"source", "compiled"} or set(row["native_probability_errors"]) != {
        "source",
        "compiled",
    }:
        raise ValueError("QI comparison requires source and compiled simulations")
    for kind, simulation in row["simulations"].items():
        counts = simulation["counts"]
        if simulation["shots_done"] != 1024 or sum(counts.values()) != 1024:
            raise ValueError("simulated sample denominator differs")
        if any(
            len(bits) != 2 or set(bits) - {"0", "1"} or type(count) is not int or count < 0
            for bits, count in counts.items()
        ):
            raise ValueError("simulated measurement-register histogram malformed")
        probabilities = [0.0] * len(expected)
        for bits, amplitude in simulation["state"].items():
            if len(bits) != 2 or set(bits) - {"0", "1"}:
                raise ValueError("state-vector basis labels must contain exactly two binary digits")
            probabilities[int(bits, 2)] = amplitude[0] ** 2 + amplitude[1] ** 2
        check_probabilities(probabilities)
        if any(count and expected[int(bits, 2)] == 0 for bits, count in counts.items()):
            raise ValueError("simulated histogram contradicts the frozen native support")
        errors[kind] = max(abs(actual - wanted) for actual, wanted in zip(probabilities, expected, strict=True))
        if terminal:
            from local_photonic_compiler_crosscheck import terminal_unitary

            original = source.read_text() if kind == "source" else row["compiled"]
            probe = terminal_unitary(original)
            if (
                probe != simulation["unitary_probe"]
                or hashlib.sha256(probe.encode()).hexdigest() != simulation["unitary_probe_sha256"]
            ):
                raise ValueError("derived terminal-unitary identity changed")
        retained_error = row["native_probability_errors"][kind]
        if (
            not math.isfinite(retained_error)
            or retained_error < 0
            or abs(errors[kind] - retained_error) > max(math.ulp(errors[kind]), math.ulp(retained_error))
        ):
            raise ValueError("stored probability error differs from amplitudes")
    if row["passed"] != (max(errors.values()) < 1e-9):
        raise ValueError("retained QI verdict differs from numerical criterion")
    if precise and (not row["passed"] or errors["compiled"] >= 1e-9):
        raise ValueError("full-precision export failed the numerical criterion")


def check_photonic(row: dict[str, Any]) -> None:
    import numpy as np

    manifest = json.loads((ROOT / row["case"] / "cases.json").read_text())
    circuit = json.loads((ROOT / row["case"] / manifest["circuit"]["file"]).read_text())
    input_state = circuit["input_state"]
    if (
        len(input_state) != row["modes"]
        or input_state.count(1) != 1
        or any(type(value) is not int or value not in {0, 1} for value in input_state)
        or type(row["source"]) is not int
        or row["source"] != input_state.index(1)
    ):
        raise ValueError("physical source mode differs from the registered one-photon input")
    setting = manifest["settings"][row["index"]]
    if setting["name"] != row["name"] or row["modes"] not in {12, 24}:
        raise ValueError("physical setting identity differs")
    expected = [pair[0] ** 2 + pair[1] ** 2 for pair in setting["column"]]
    if len(expected) != row["modes"] or len(row["simulated_counts"]) != row["modes"]:
        raise ValueError("physical output coverage differs")
    if sum(row["simulated_counts"]) != 1024:
        raise ValueError("synthetic photonic count denominator differs")
    if any(type(count) is not int or count < 0 for count in row["simulated_counts"]):
        raise ValueError("synthetic photonic counts must be nonnegative integers")
    for actual, wanted in zip(row["ideal"], expected, strict=True):
        if not math.isfinite(actual) or abs(actual - wanted) > 1e-12:
            raise ValueError("ideal probabilities differ from the frozen optical column")
    check_probabilities(row["ideal"])
    ideal = np.asarray(row["ideal"])
    seeded_counts = np.random.default_rng(20261022 + row["index"]).multinomial(1024, ideal / ideal.sum()).tolist()
    if row["simulated_counts"] != seeded_counts:
        raise ValueError("synthetic photonic counts differ from the frozen-ideal seeded sampler")
    if set(row["probabilities"]) != {"SLOS", "Naive"}:
        raise ValueError("optical comparison requires both SLOS and Naive")
    for kind, values in row["probabilities"].items():
        check_probabilities(values)
        error = max(abs(actual - wanted) for actual, wanted in zip(values, row["ideal"], strict=True))
        retained_error = row["max_probability_errors"][kind]
        if (
            not math.isfinite(retained_error)
            or retained_error < 0
            or abs(error - retained_error) > max(math.ulp(error), math.ulp(retained_error))
            or error >= 1e-9
        ):
            raise ValueError("optical backend probability criterion differs")
    operator_error = row["full_operator_max_error"]
    if not row["passed"] or not math.isfinite(operator_error) or not 0 <= operator_error < 1e-9:
        raise ValueError("optical full-operator criterion differs")


def check_optical_sources(record: dict[str, Any]) -> None:
    manifests = sorted((ROOT / "results/hypercomplex/photonic-successors").glob("*/*/cases.json"))
    expected = {
        path.relative_to(ROOT).as_posix(): sha(path)
        for manifest in manifests
        for path in (manifest, manifest.parent / json.loads(manifest.read_text())["circuit"]["file"])
    }
    if record["source_sha256"] != expected:
        raise ValueError("frozen optical source-hash denominator or digest differs")


def check_optical_operator(arguments: tuple[dict[str, Any], dict[str, Any]]) -> None:
    import numpy as np

    retained, output = arguments
    manifest = json.loads((ROOT / retained["case"] / "cases.json").read_text())
    setting = manifest["settings"][retained["index"]]
    expected = np.asarray(setting["operator"]["real"]) + 1j * np.asarray(setting["operator"]["imaginary"])
    actual = np.asarray(output["actual_operator"]["real"]) + 1j * np.asarray(output["actual_operator"]["imaginary"])
    if actual.shape != expected.shape or not np.isfinite(actual).all() or not np.isfinite(expected).all():
        raise ValueError("retained complete optical operator has invalid shape or entries")
    error = float(np.max(np.abs(actual - expected)))
    recorded = retained["full_operator_max_error"]
    if (
        not math.isfinite(error)
        or not math.isfinite(recorded)
        or not 0 <= error < 1e-9
        or abs(error - recorded) > max(math.ulp(error), math.ulp(recorded))
    ):
        raise ValueError("retained full-operator maximum differs from its complete optical output")


def check() -> None:
    from local_photonic_compiler_crosscheck import QI_CASE_PATHS, qi_inputs

    from qi_stack import pins

    if load("artifacts.json")["sha256"] != inventory():
        raise ValueError("local simulation file set or bytes differ from artifact inventory")
    initial = load("photonic-compiler-crosscheck/photonic.json")["rows"]
    if len(initial) != 40 or any(
        row["passed"] or "Experiment' object has no attribute 'circuit" not in row["error"] for row in initial
    ):
        raise ValueError("initial Perceval harness failure diagnosis differs")
    optical = load("physical-photonic-compiler-crosscheck/photonic.json")
    if optical["seed"] != 20261022 or optical["shots"] != 1024:
        raise ValueError("optical synthetic sampling seed or denominator differs")
    rows = optical["rows"]
    expected = {
        (str(path.parent.relative_to(ROOT)), index)
        for path in (ROOT / "results/hypercomplex/photonic-successors").glob("*/*/cases.json")
        for index in range(len(json.loads(path.read_text())["settings"]))
    }
    if len(rows) != 128 or {(row["case"], row["index"]) for row in rows} != expected:
        raise ValueError("physical photonic setting denominator differs")
    ordered_map(check_photonic, rows, min_items=1)
    check_optical_sources(optical)
    operators = load("optical-operator-replay.json")
    requirements = read_pins(ROOT / "requirements.txt") | read_pins(ROOT / "ci/requirements-ci.txt")
    optical_versions = {name: requirements[name] for name in ("perceval-quandela", "exqalibur", "numpy")}
    if optical["versions"] != optical_versions or operators["versions"] != optical_versions:
        raise ValueError("retained optical toolchain versions differ from the requirement pins")
    outputs = {(row["case"], row["index"]): row for row in operators["rows"]}
    if len(operators["rows"]) != 128 or set(outputs) != expected:
        raise ValueError("complete optical operator denominator differs")
    if operators["source_sha256"] != optical["source_sha256"] or operators["retained_photonic_sha256"] != sha(
        BUNDLE / "physical-photonic-compiler-crosscheck/photonic.json"
    ):
        raise ValueError("complete optical operators differ from their retained source identities")
    if operators["producer_sha256"] != sha(BUNDLE / "optical-operator-replay-producer.py"):
        raise ValueError("complete optical operator producer identity differs")
    ordered_map(check_optical_operator, [(row, outputs[(row["case"], row["index"])]) for row in rows], min_items=1)
    for directory, precise, terminal in QI_BUNDLES:
        record = load(directory + "/qi.json")
        if record["versions"] != pins():
            raise ValueError("retained QI toolchain versions differ from the lock")
        if record["seed"] != 20261022 or record["shots"] != 1024:
            raise ValueError("QI seeded sampling metadata differs")
        rows = record["rows"]
        qi_inputs(precise)
        if len(rows) != 24 or {row["case"] for row in rows} != QI_CASE_PATHS:
            raise ValueError("QI case denominator differs")
        ordered_map(check_qi, [(row, precise, terminal) for row in rows], min_items=1)
        if sum(row["passed"] for row in rows) != (24 if precise else 20):
            raise ValueError("default-writer residual or full-precision verdict changed")
    for directory, record_file in (
        ("physical-photonic-compiler-crosscheck", "photonic.json"),
        ("validated-terminal-unitary-compiler-crosscheck", "qi.json"),
        ("fullprecision-compiler-crosscheck", "qi.json"),
    ):
        record = load(directory + "/" + record_file)
        if sha(BUNDLE / directory / "producer.py") != record["runner_sha256"]:
            raise ValueError("retained producer identity differs")
        if (
            directory.startswith("fullprecision")
            and sha(BUNDLE / directory / "exporter.py") != record["exporter"]["sha256"]
        ):
            raise ValueError("retained full-precision exporter identity differs")


def qi_simulation(arguments: tuple[str, str | None]) -> dict[str, Any]:
    from local_photonic_compiler_crosscheck import qi_warning_policy

    qi_warning_policy()
    import qxelarator

    code, unitary_probe = arguments
    result = qxelarator.execute_string(code, iterations=1024, seed=20261022)
    state_result = (
        result if unitary_probe is None else qxelarator.execute_string(unitary_probe, iterations=1, seed=20261022)
    )
    return {
        "counts": {str(bits): int(count) for bits, count in result.results.items()},
        "state": {bits: [value.real, value.imag] for bits, value in state_result.state.items()},
    }


def qi_default_compile(case: str) -> str:
    from local_photonic_compiler_crosscheck import qi_warning_policy

    qi_warning_policy()
    from qi_toolchain_check import compile_circuit, compiler_configs

    return compile_circuit((ROOT / case).read_text(), compiler_configs()["tuna_17"])


def live_qi() -> None:
    from qi_stack import live, pins, run

    if not live("local QI compiler simulation", "retained numerical and identity replay"):
        return
    code = """
import json,sys
sys.path[:0] = ['scripts', 'gororoba_quantum']
from pathlib import Path
from importlib.metadata import version
from local_photonic_compiler_crosscheck import qi_case, qi_inputs
from local_simulation_replay import QI_BUNDLES, load, qi_default_compile, qi_simulation
from parallel import ordered_map
inputs = qi_inputs(True)
case_paths = [row['case'] for row in load('fullprecision-compiler-crosscheck/qi.json')['rows']]
default_compiled = dict(zip(case_paths, ordered_map(qi_default_compile, case_paths, min_items=1), strict=True))
simulation_inputs = []
for directory, precise, terminal in QI_BUNDLES:
    for row in load(directory + '/qi.json')['rows']:
        if not precise and default_compiled[row['case']] != row['compiled']:
            raise ValueError('default compiler differs from retained code: ' + row['case'])
        for kind, code in [('source', Path(row['case']).read_text()), ('compiled', row['compiled'])]:
            probe = row['simulations'][kind]['unitary_probe'] if terminal else None
            simulation_inputs.append((code, probe))
print(json.dumps({'versions': {name: version(name) for name in ('opensquirrel', 'libqasm', 'qxelarator')},
                 'rows': ordered_map(qi_case, inputs, min_items=1),
                 'default_compiled': default_compiled,
                 'simulations': ordered_map(qi_simulation, simulation_inputs, min_items=1)}))
"""
    actual = json.loads(run(["-B", "-W", "error", "-c", code]))
    if actual["versions"] != pins() or any(
        load(directory + "/qi.json")["versions"] != actual["versions"] for directory, _, _ in QI_BUNDLES
    ):
        raise ValueError("live QI toolchain versions differ from the lock or retained provenance")
    if actual["rows"] != load("fullprecision-compiler-crosscheck/qi.json")["rows"]:
        raise ValueError("live pinned QI replay differs from retained full-precision evidence")
    for directory, precise, _ in QI_BUNDLES:
        if not precise and any(
            actual["default_compiled"][row["case"]] != row["compiled"] for row in load(directory + "/qi.json")["rows"]
        ):
            raise ValueError("live default-compiler output differs from retained compiled programs")
    expected_simulations = [
        {field: row["simulations"][kind][field] for field in ("counts", "state")}
        for directory, _, _ in QI_BUNDLES
        for row in load(directory + "/qi.json")["rows"]
        for kind in ("source", "compiled")
    ]
    if actual["simulations"] != expected_simulations:
        raise ValueError("live pinned QI seeded counts or states differ from retained source or compiled evidence")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-inventory", action="store_true")
    parser.add_argument("--live-qi", action="store_true")
    arguments = parser.parse_args()
    if arguments.write_inventory:
        (BUNDLE / "artifacts.json").write_text(
            json.dumps({"schema": "local-simulation-artifacts-v1", "sha256": inventory()}, indent=2) + "\n"
        )
    check()
    if arguments.live_qi:
        live_qi()
    print("validated local simulation identities, complete denominators and numerical residuals")


if __name__ == "__main__":
    main()
