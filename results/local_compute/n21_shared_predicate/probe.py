"""Replay bounded native-Qiskit shared-predicate multiplier checks."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import itertools
import json
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

SOURCE_FILES = (
    "gororoba_quantum/target_flip.py",
    "gororoba_quantum/modular_arithmetic.py",
    "gororoba_quantum/affine_residual.py",
    "gororoba_quantum/boolean_anf.py",
    "gororoba_quantum/parallel.py",
    "gororoba_quantum/order_finding.py",
    "gororoba_quantum/qpe_diagnostics.py",
    "requirements.txt",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_snapshot(root: Path) -> dict[str, Any]:
    def git(*arguments: str) -> str:
        return subprocess.check_output(
            ["git", "-c", "core.fsmonitor=false", "-C", str(root), *arguments], text=True
        ).strip()

    return {
        "head": git("rev-parse", "HEAD"),
        "status": git("status", "--porcelain=v1", "--untracked-files=all"),
        "source_sha256": {name: digest(root / name) for name in SOURCE_FILES},
    }


def main() -> None:
    probe_path = Path(__file__).resolve(strict=True)
    probe_sha256 = digest(probe_path)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    root = arguments.source_root.resolve(strict=True)
    before = source_snapshot(root)
    sys.path.insert(0, str(root / "gororoba_quantum"))

    import numpy as np
    import qiskit
    from qiskit import QuantumCircuit, transpile
    from qiskit.quantum_info import Operator
    from qiskit.synthesis import synth_mcx_1_clean_kg24

    from modular_arithmetic import _append_controlled_target_flips, modular_permutation
    from target_flip import target_flip_network

    started = time.monotonic()
    results: list[dict[str, Any]] = []
    for multiplier in (4, 16):
        network = target_flip_network(modular_permutation(21, multiplier))
        choices: list[list[tuple[int, bool] | None]] = [
            [(bit, bool(cube.control_state & (1 << bit))) for bit in range(5) if cube.control_mask & (1 << bit)]
            if cube.control_mask.bit_count() >= 2
            else [None]
            for cube in network
        ]
        paths = {choice: (0, [choice]) for choice in choices[0]}
        for options in choices[1:]:
            paths = {
                choice: max(
                    (
                        (count + int(choice is not None and choice == previous), path + [choice])
                        for previous, (count, path) in paths.items()
                    ),
                    key=lambda entry: (entry[0], tuple((-1, False) if pivot is None else pivot for pivot in entry[1])),
                )
                for choice in options
            }
        count, pivots = max(
            paths.values(),
            key=lambda entry: (entry[0], tuple((-1, False) if pivot is None else pivot for pivot in entry[1])),
        )
        baseline = QuantumCircuit(7)
        _append_controlled_target_flips(baseline, 0, list(range(1, 6)), [6], network)
        candidate = QuantumCircuit(7)
        for pivot, group_iterator in itertools.groupby(zip(pivots, network, strict=True), key=lambda entry: entry[0]):
            group = [entry[1] for entry in group_iterator]
            if pivot is None:
                _append_controlled_target_flips(candidate, 0, list(range(1, 6)), [6], tuple(group))
                continue
            pivot_bit, pivot_positive = pivot
            if not pivot_positive:
                candidate.x(pivot_bit + 1)
            candidate.rccx(0, pivot_bit + 1, 6)
            for cube in group:
                other_bits = [bit for bit in range(5) if bit != pivot_bit and cube.control_mask & (1 << bit)]
                open_bits = [bit for bit in other_bits if not cube.control_state & (1 << bit)]
                for bit in open_bits:
                    candidate.x(bit + 1)
                controls = [0, pivot_bit + 1] + [bit + 1 for bit in other_bits]
                synthesized = synth_mcx_1_clean_kg24(len(controls))
                mapping = controls + [cube.target + 1, 6]
                for endpoint in (synthesized.data[0], synthesized.data[-1]):
                    indices = [synthesized.find_bit(qubit).index for qubit in endpoint.qubits]
                    if endpoint.operation.name != "rccx" or indices != [0, 1, len(controls) + 1]:
                        raise RuntimeError("KG24 outer-predicate structure differs from the audited native circuit")
                for instruction in synthesized.data[1:-1]:
                    candidate.append(
                        instruction.operation,
                        [mapping[synthesized.find_bit(qubit).index] for qubit in instruction.qubits],
                    )
                for bit in reversed(open_bits):
                    candidate.x(bit + 1)
            candidate.rccx(0, pivot_bit + 1, 6)
            if not pivot_positive:
                candidate.x(pivot_bit + 1)

        matrix = Operator(candidate).data
        discrepancy = float(np.max(np.abs(matrix[:, :64] - Operator(baseline).data[:, :64])))
        leakage = float(np.max(np.abs(matrix[64:, :64])))
        expected = np.zeros((128, 64), dtype=complex)
        for packed in range(64):
            data_value = packed >> 1
            output_value = multiplier * data_value % 21 if data_value < 21 else data_value
            destination = (output_value << 1 | 1) if packed & 1 else packed
            expected[destination, packed] = 1
        permutation_error = float(np.max(np.abs(matrix[:, :64] - expected)))
        if max(discrepancy, leakage, permutation_error) > 1e-12:
            raise RuntimeError("phase-sensitive controlled-permutation or scratch-restoration check fails")
        result: dict[str, Any] = {
            "multiplier": multiplier,
            "shared_boundaries": count,
            "pivots": pivots,
            "source_operations_before": dict(baseline.count_ops()),
            "source_operations_after": dict(candidate.count_ops()),
            "clean_subspace_operator_error": discrepancy,
            "scratch_leakage": leakage,
            "full_controlled_permutation_error": permutation_error,
            "unrouted": {},
        }
        for name, circuit in (("baseline", baseline), ("shared", candidate)):
            compiled = transpile(
                circuit,
                basis_gates=["cx", "rz", "sx", "x"],
                optimization_level=3,
                seed_transpiler=20261010,
            )
            result["unrouted"][name] = {
                "cx": compiled.count_ops().get("cx", 0),
                "depth": compiled.depth(),
                "operations": dict(compiled.count_ops()),
            }
        results.append(result)

    after = source_snapshot(root)
    if before != after:
        raise RuntimeError("source hashes, HEAD, or checkout status change during the probe")
    output = {
        "schema": "n21-native-qiskit-shared-predicate-audit-v1",
        "elapsed_seconds": time.monotonic() - started,
        "probe_sha256": probe_sha256,
        "checkout_label": "source checkout",
        "snapshot_before": before,
        "snapshot_after": after,
        "versions": {
            "python": platform.python_version(),
            "qiskit": importlib.metadata.version("qiskit"),
            "numpy": importlib.metadata.version("numpy"),
            "qiskit_aer_distribution": importlib.metadata.version("qiskit-aer"),
        },
        "loaded_qiskit": {"module": "qiskit.__init__", "sha256": digest(Path(qiskit.__file__))},
        "operator_check": {
            "matrix_shape": [128, 64],
            "input_domain": "all 32 data states and both phase-control values, scratch initially zero",
            "tolerance": 1e-12,
            "comparison": "complex amplitudes including relative phases, against independently constructed permutation",
        },
        "compile_options": {
            "basis_gates": ["cx", "rz", "sx", "x"],
            "optimization_level": 3,
            "seed_transpiler": 20261010,
            "coupling_map": None,
            "backend_target": None,
        },
        "limitations": [
            "Exploratory in-memory construction; the probe preserves production source modules.",
            "The bounded floating-point matrix check supplies numerical evidence, not a formal proof.",
            "The check covers all data states with clean scratch; dirty scratch lies outside the contract.",
            "Native KG24 endpoint structure is checked at replay and may change with upstream versions.",
            "Reported costs precede physical connectivity, routing, scheduling, and calibrated noise.",
            "The probe does not establish N21 statistical admission, hardware accuracy, or QPU readiness.",
            "The probe performs no Aer shot simulation, IBM service construction, package build, or QPU submission.",
        ],
        "results": results,
    }
    serialized_output = json.dumps(output, indent=2, sort_keys=True) + "\n"
    if digest(probe_path) != probe_sha256:
        raise RuntimeError("probe source changes during the probe")
    with arguments.output.open("x", encoding="utf-8") as destination:
        destination.write(serialized_output)
    print(json.dumps({"output": str(arguments.output), "results": results}, indent=2))


if __name__ == "__main__":
    main()
