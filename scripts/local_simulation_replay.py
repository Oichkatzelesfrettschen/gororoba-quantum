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
from parallel import ordered_map  # noqa: E402

BUNDLE = ROOT / "results/local-simulation"


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
    if sha(source) != row["sha256"]:
        raise ValueError("QI frozen source identity changed")
    manifest = json.loads(source.with_name("cases.json").read_text())
    case = next(case for case in manifest["circuits"] if case["file"] == source.name)
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
            probabilities[int(bits, 2)] = amplitude[0] ** 2 + amplitude[1] ** 2
        check_probabilities(probabilities)
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
        if not math.isfinite(retained_error) or retained_error < 0 or abs(errors[kind] - retained_error) > 1e-15:
            raise ValueError("stored probability error differs from amplitudes")
    if row["passed"] != (max(errors.values()) < 1e-9):
        raise ValueError("retained QI verdict differs from numerical criterion")
    if precise and (not row["passed"] or errors["compiled"] >= 1e-9):
        raise ValueError("full-precision export failed the numerical criterion")


def check_photonic(row: dict[str, Any]) -> None:
    manifest = json.loads((ROOT / row["case"] / "cases.json").read_text())
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
    if set(row["probabilities"]) != {"SLOS", "Naive"}:
        raise ValueError("optical comparison requires both SLOS and Naive")
    for kind, values in row["probabilities"].items():
        check_probabilities(values)
        error = max(abs(actual - wanted) for actual, wanted in zip(values, row["ideal"], strict=True))
        retained_error = row["max_probability_errors"][kind]
        if (
            not math.isfinite(retained_error)
            or retained_error < 0
            or abs(error - retained_error) > 1e-15
            or error >= 1e-9
        ):
            raise ValueError("optical backend probability criterion differs")
    operator_error = row["full_operator_max_error"]
    if not row["passed"] or not math.isfinite(operator_error) or not 0 <= operator_error < 1e-9:
        raise ValueError("optical full-operator criterion differs")


def check() -> None:
    if load("artifacts.json")["sha256"] != inventory():
        raise ValueError("local simulation file set or bytes differ from artifact inventory")
    initial = load("photonic-compiler-crosscheck/photonic.json")["rows"]
    if len(initial) != 40 or any(
        row["passed"] or "Experiment' object has no attribute 'circuit" not in row["error"] for row in initial
    ):
        raise ValueError("initial Perceval harness failure diagnosis differs")
    optical = load("physical-photonic-compiler-crosscheck/photonic.json")
    rows = optical["rows"]
    expected = {
        (str(path.parent.relative_to(ROOT)), index)
        for path in (ROOT / "results/hypercomplex/photonic-successors").glob("*/*/cases.json")
        for index in range(len(json.loads(path.read_text())["settings"]))
    }
    if len(rows) != 128 or {(row["case"], row["index"]) for row in rows} != expected:
        raise ValueError("physical photonic setting denominator differs")
    ordered_map(check_photonic, rows, min_items=1)
    for relative, wanted in optical["source_sha256"].items():
        if sha(ROOT / relative) != wanted:
            raise ValueError("frozen optical source changed")
    for directory, precise, terminal in (
        ("photonic-compiler-crosscheck", False, False),
        ("physical-photonic-compiler-crosscheck", False, False),
        ("terminal-unitary-compiler-crosscheck", False, True),
        ("validated-terminal-unitary-compiler-crosscheck", False, True),
        ("fullprecision-compiler-crosscheck", True, True),
    ):
        record = load(directory + "/qi.json")
        rows = record["rows"]
        expected_qi = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "results/quantum_inspire/runs/tuna17-quaternion-order-noise").glob("order-batch-*/*.cq")
        }
        if len(rows) != 24 or {row["case"] for row in rows} != expected_qi:
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


def live_qi() -> None:
    from qi_stack import live, run

    if not live("local QI compiler simulation", "retained numerical and identity replay"):
        return
    code = """
import json,sys
sys.path[:0] = ['scripts', 'gororoba_quantum']
from pathlib import Path
from local_photonic_compiler_crosscheck import qi_case
from parallel import ordered_map
inputs = []
root = Path('results/quantum_inspire/runs/tuna17-quaternion-order-noise')
for manifest in sorted(root.glob('order-batch-*/cases.json')):
    cases = json.loads(manifest.read_text())['circuits']
    inputs.extend((str(manifest.parent), case | {'_full_precision': True}) for case in cases)
print(json.dumps(ordered_map(qi_case, inputs, min_items=1)))
"""
    actual = json.loads(run(["-c", code]))
    if actual != load("fullprecision-compiler-crosscheck/qi.json")["rows"]:
        raise ValueError("live pinned QI replay differs from retained full-precision evidence")


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
