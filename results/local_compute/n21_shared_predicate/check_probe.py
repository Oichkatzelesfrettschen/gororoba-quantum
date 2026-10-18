"""Check N21 probe provenance with real native-Qiskit computations."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import math
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

PRODUCER_COST_FIELDS = frozenset(("source_operations_before", "source_operations_after", "unrouted"))
ERROR_FIELDS = frozenset(("clean_subspace_operator_error", "scratch_leakage", "full_controlled_permutation_error"))
STRUCTURAL_FIELDS = frozenset(("multiplier", "shared_boundaries", "pivots"))


def _operation_counts(value: Any) -> None:
    if (
        not isinstance(value, dict)
        or not value
        or any(
            not isinstance(name, str) or not name or type(count) is not int or count < 0
            for name, count in value.items()
        )
    ):
        raise RuntimeError("Producer operation counts must map gate names to nonnegative integers")


def _semantic_results(results: Any, tolerance: float) -> list[dict[str, Any]]:
    if not isinstance(results, list) or len(results) != 2:
        raise RuntimeError("Native probe must report both multiplier results")
    projected = []
    for result in results:
        if not isinstance(result, dict) or result.keys() != PRODUCER_COST_FIELDS | ERROR_FIELDS | STRUCTURAL_FIELDS:
            raise RuntimeError("Native result fields differ from the declared semantic/cost boundary")
        for key in ERROR_FIELDS:
            error = result[key]
            if type(error) not in (int, float) or not math.isfinite(error) or not 0 <= error <= tolerance:
                raise RuntimeError(f"Native scientific check {key} violates the retained tolerance")
        for key in ("source_operations_before", "source_operations_after"):
            _operation_counts(result[key])
        if not isinstance(result["unrouted"], dict) or result["unrouted"].keys() != {"baseline", "shared"}:
            raise RuntimeError("Unrouted costs must report exactly baseline and shared circuits")
        for cost in result["unrouted"].values():
            if not isinstance(cost, dict) or cost.keys() != {"cx", "depth", "operations"}:
                raise RuntimeError("Unrouted cost dimensions differ from the producer contract")
            _operation_counts(cost["operations"])
            if (
                any(type(cost[key]) is not int or cost[key] < 0 for key in ("cx", "depth"))
                or cost["cx"] != cost["operations"].get("cx", 0)
                or cost["depth"] > sum(cost["operations"].values())
                or not set(cost["operations"]) <= {"cx", "rz", "sx", "x"}
            ):
                raise RuntimeError("Unrouted costs violate their declared basis or count dimensions")
        projected.append({key: result[key] for key in STRUCTURAL_FIELDS})
    return projected


def _results_agree(historical: Any, successful: Any, *, current_sdk: bool, tolerance: float) -> bool:
    if not current_sdk:
        return bool(historical == successful)
    old = _semantic_results(historical, tolerance)
    new = _semantic_results(successful, tolerance)
    return json.dumps(old, sort_keys=True, allow_nan=False) == json.dumps(new, sort_keys=True, allow_nan=False)


def _check_comparison_contract(historical: dict[str, Any]) -> None:
    retained = historical["results"]
    tolerance = historical["operator_check"]["tolerance"]
    changed = json.loads(json.dumps(retained))
    changed[0]["unrouted"]["baseline"]["depth"] -= 1
    if _results_agree(retained, changed, current_sdk=False, tolerance=tolerance):
        raise RuntimeError("Historical replay accepts changed producer costs")
    if not _results_agree(retained, changed, current_sdk=True, tolerance=tolerance):
        raise RuntimeError("Current SDK replay requires historical compiler costs")
    changed[0]["clean_subspace_operator_error"] = tolerance / 2
    if not _results_agree(retained, changed, current_sdk=True, tolerance=tolerance):
        raise RuntimeError("Current SDK replay rejects an error within the original scientific tolerance")
    for field in ("multiplier", "shared_boundaries"):
        changed = json.loads(json.dumps(retained))
        changed[0][field] += 1
        if _results_agree(retained, changed, current_sdk=True, tolerance=tolerance):
            raise RuntimeError(f"Current SDK replay accepts changed {field}")
    changed = json.loads(json.dumps(retained))
    changed[0]["pivots"][0][1] = not changed[0]["pivots"][0][1]
    if _results_agree(retained, changed, current_sdk=True, tolerance=tolerance):
        raise RuntimeError("Current SDK replay accepts a changed predicate pivot")
    mutations = [
        ("extra", "unknown", 1),
        ("error", "scratch_leakage", 2 * tolerance),
        ("error", "full_controlled_permutation_error", math.nan),
        ("error", "clean_subspace_operator_error", -tolerance),
        ("cost", "width", 7),
        ("cost", "cx", -1),
        ("cost", "operations", {"cx": 1.0}),
    ]
    for category, key, value in mutations:
        changed = json.loads(json.dumps(retained))
        target = changed[0]["unrouted"]["baseline"] if category == "cost" else changed[0]
        target[key] = value
        try:
            _results_agree(retained, changed, current_sdk=True, tolerance=tolerance)
        except RuntimeError:
            continue
        raise RuntimeError(f"Current SDK replay accepts an invalid {category} field {key}")


def _check_endpoint_contract(probe: Any) -> None:
    import numpy as np
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator
    from qiskit.synthesis import synth_mcx_1_clean_kg24

    for controls in (3, 4, 5):
        native = synth_mcx_1_clean_kg24(controls)
        body, _representation = probe.kg24_body(native, controls)
        restored = QuantumCircuit(native.num_qubits)
        restored.rccx(0, 1, controls + 1)
        for instruction in body:
            restored.append(instruction.operation, [native.find_bit(qubit).index for qubit in instruction.qubits])
        restored.rccx(0, 1, controls + 1)
        if float(np.max(np.abs(Operator(native).data - Operator(restored).data))) > 1e-12:
            raise RuntimeError("Endpoint recovery changes the complete native operator")
        broken = QuantumCircuit(native.num_qubits)
        broken.x(0)
        broken.compose(native, inplace=True)
        try:
            probe.kg24_body(broken, controls)
        except RuntimeError:
            continue
        raise RuntimeError("Endpoint recovery accepts a changed native predicate prefix")


def _run_probe(probe_path: Path, source_root: Path, output_path: Path, *, mutate: bool = False) -> None:
    import qiskit

    specification = importlib.util.spec_from_file_location("n21_probe_fixture", probe_path)
    if specification is None or specification.loader is None:
        raise RuntimeError("Cannot load temporary probe")
    probe = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(probe)
    _check_endpoint_contract(probe)
    real_transpile = qiskit.transpile
    source_changed = False

    def transpile(*arguments: Any, **keywords: Any) -> Any:
        nonlocal source_changed
        if mutate and not source_changed:
            with probe_path.open("a", encoding="utf-8") as destination:
                destination.write("\n# Temporary regression mutation during native transpilation.\n")
            source_changed = True
        return real_transpile(*arguments, **keywords)

    arguments = [str(probe_path), "--source-root", str(source_root), "--output", str(output_path)]
    with (
        patch.object(sys, "argv", arguments),
        patch.object(qiskit, "transpile", transpile),
        redirect_stdout(io.StringIO()),
    ):
        probe.main()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument(
        "--current-sdk", action="store_true", help="check semantic contracts while recording current producer costs"
    )
    arguments = parser.parse_args()
    source_root = arguments.source_root.resolve(strict=True)
    bundle = Path(__file__).resolve().parent
    historical_bytes = (bundle / "result.json").read_bytes()
    historical = json.loads(historical_bytes)
    _check_comparison_contract(historical)
    archive = (bundle / "historical_probe.py.gz").read_bytes()
    if hashlib.sha256(gzip.decompress(archive)).hexdigest() != historical["probe_sha256"]:
        raise RuntimeError("Archived probe differs from the historical result's recorded source digest")
    if archive[4:8] != bytes(4):
        raise RuntimeError("Historical probe gzip timestamp must be zero")
    source_bytes = (bundle / "probe.py").read_bytes()

    with tempfile.TemporaryDirectory(prefix="n21-probe-provenance-") as temporary_directory:
        temporary = Path(temporary_directory)
        probe_path = temporary / "probe.py"
        probe_path.write_bytes(source_bytes)
        output_path = temporary / "unchanged.json"
        _run_probe(probe_path, source_root, output_path)
        successful_bytes = output_path.read_bytes()
        successful = json.loads(successful_bytes)
        if successful["probe_sha256"] != hashlib.sha256(source_bytes).hexdigest():
            raise RuntimeError("Unchanged probe output carries the wrong executed-source digest")
        if arguments.current_sdk:
            if successful.keys() != historical.keys() | {"native_kg24_endpoint_representations"}:
                raise RuntimeError("Current SDK output fields differ from the declared probe schema")
            for key in ("schema", "operator_check", "compile_options", "limitations", "checkout_label"):
                if successful[key] != historical[key]:
                    raise RuntimeError(f"Current SDK probe changes the retained {key} contract")
            if successful["native_kg24_endpoint_representations"] not in (["opaque-rccx"], ["elementary-rccx"]):
                raise RuntimeError("Current SDK reports an unrecognized native endpoint representation")
        if not _results_agree(
            historical["results"],
            successful["results"],
            current_sdk=arguments.current_sdk,
            tolerance=historical["operator_check"]["tolerance"],
        ):
            raise RuntimeError("Native probe results differ from the retained multiplier checks")

        try:
            _run_probe(probe_path, source_root, output_path)
        except FileExistsError:
            pass
        else:
            raise RuntimeError("Probe accepted an existing output path")
        if output_path.read_bytes() != successful_bytes:
            raise RuntimeError("Probe changed the existing output")

        changed_output = temporary / "changed-source.json"
        try:
            _run_probe(probe_path, source_root, changed_output, mutate=True)
        except RuntimeError as error:
            if str(error) != "probe source changes during the probe":
                raise RuntimeError("Mutation failed outside the probe-source guard") from error
        else:
            raise RuntimeError("Probe accepted a source mutation during native computation")
        if probe_path.read_bytes() == source_bytes:
            raise RuntimeError("Source mutation fixture did not edit the executed probe")
        if changed_output.exists():
            raise RuntimeError("Changed-source probe created an output")
        if output_path.read_bytes() != successful_bytes:
            raise RuntimeError("Source mutation changed the existing output")

    if (bundle / "result.json").read_bytes() != historical_bytes:
        raise RuntimeError("Historical result bytes changed during regression")
    if (bundle / "historical_probe.py.gz").read_bytes() != archive:
        raise RuntimeError("Historical probe archive bytes changed during regression")
    if arguments.current_sdk:
        print(
            json.dumps(
                {
                    "producer_versions": successful["versions"],
                    "probe_sha256": successful["probe_sha256"],
                    "native_kg24_endpoint_representations": successful["native_kg24_endpoint_representations"],
                    "current_results": successful["results"],
                },
                sort_keys=True,
                allow_nan=False,
            )
        )
    print("N21 probe: native results, source mutation rejection, exclusive output, and historical source archive pass")


if __name__ == "__main__":
    main()
