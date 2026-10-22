"""Generate submit-free quaternion experiments for the existing guarded providers.

The photonic mesh reconstructs the entire requested operator, rather than a
single prepared column. Tuna cases retain the operator after angle quantization
so native approximation cannot be mistaken for a device anomaly.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from qi_zero_divisor_cases import CATALOGUE, catalogue_check  # noqa: E402

from hypercomplex_operators import (  # noqa: E402
    ComplexMatrix,
    left_fourier,
    order_interferometer,
    periodic_generator,
)
from parallel import ordered_map  # noqa: E402


def encoded(matrix: ComplexMatrix) -> dict[str, Any]:
    return {"real": matrix.real.tolist(), "imaginary": matrix.imag.tolist()}


def photonic_template(matrix: ComplexMatrix) -> tuple[dict[str, Any], dict[str, float]]:
    """Fixed triangular nearest-neighbor Rx/phase mesh for an arbitrary unitary."""
    size = matrix.shape[0]
    if matrix.shape != (size, size) or not np.isfinite(matrix).all():
        raise ValueError("the photonic operator must be a finite square matrix")
    if not np.allclose(matrix.conj().T @ matrix, np.eye(size), atol=1e-12, rtol=0):
        raise ValueError("the photonic operator must be unitary")
    remaining = matrix.copy()
    eliminations: list[tuple[int, ComplexMatrix]] = []
    for column in range(size - 1):
        for bottom in range(size - 1, column, -1):
            top = bottom - 1
            first, second = remaining[top, column], remaining[bottom, column]
            radius = math.hypot(abs(first), abs(second))
            givens = (
                np.array([[first.conjugate(), second.conjugate()], [-second, first]]) / radius
                if radius > 1e-15
                else np.eye(2, dtype=complex)
            )
            remaining[top : bottom + 1] = givens @ remaining[top : bottom + 1]
            eliminations.append((top, np.asarray(givens, dtype=np.complex128)))
    operations: list[list[Any]] = []
    parameters: dict[str, float] = {}

    def add(kind: str, mode: int, value: float) -> None:
        index = len(parameters)
        operations.append([kind, mode, index])
        parameters[f"x{index}"] = float(value)

    for mode in range(size):
        add("PS", mode, float(np.angle(remaining[mode, mode])))
    for mode, givens in reversed(eliminations):
        inverse = givens.conj().T
        diagonal_phase = float(np.angle(inverse[0, 0]))
        off_phase = float(np.angle(inverse[0, 1])) - math.pi / 2
        alpha, beta = (diagonal_phase + off_phase) / 2, (diagonal_phase - off_phase) / 2
        theta = 2 * math.atan2(abs(inverse[0, 1]), abs(inverse[0, 0]))
        add("PS", mode, beta)
        add("PS", mode + 1, -beta)
        add("BS", mode, theta)
        add("PS", mode, alpha)
        add("PS", mode + 1, -alpha)
    return {
        "schema": "qd-template-circuit-v1",
        "modes": size,
        "input_state": [1] + [0] * (size - 1),
        "parameters": len(parameters),
        "ops": operations,
    }, parameters


def order_settings() -> list[dict[str, Any]]:
    return [
        {
            "name": f"order-i{first}-j{second}-representative{representative}",
            "theta": first * math.pi / 4,
            "phi": second * math.pi / 4,
            "representative": representative,
        }
        for first in (0, 1)
        for second in (0, 1)
        for representative in (0, 1)
    ]


def wave_settings() -> list[dict[str, Any]]:
    return (
        [
            {"name": f"wave-frame-{index:02d}", "time": index / 8, "coupling": 1.0, "representative": 0}
            for index in range(17)
        ]
        + [
            {"name": f"free-reference-{index}", "time": index / 2, "coupling": 0.0, "representative": 0}
            for index in range(5)
        ]
        + [
            {"name": f"wave-ray-check-{index}", "time": index / 2, "coupling": 1.0, "representative": 1}
            for index in (1, 2)
        ]
    )


def setting_operator(setting: dict[str, Any]) -> ComplexMatrix:
    if "theta" in setting:
        matrix = order_interferometer(setting["theta"], setting["phi"])
    elif "time" in setting:
        matrix = expm(setting["time"] * periodic_generator(4, setting["coupling"]))
    else:
        transform = left_fourier(4)
        operation = setting["operation"]
        if operation == "identity-reference":
            matrix = np.eye(8, dtype=complex)
        elif operation == "forward":
            matrix = transform
        elif operation in {"forward-real-superposition", "forward-imaginary-superposition"}:
            preparation = np.eye(8, dtype=complex)
            phase = 1 if operation == "forward-real-superposition" else 1j
            block = np.array([[1, -phase.conjugate()], [phase, 1]], dtype=complex) / math.sqrt(2)
            preparation[np.ix_([0, 2], [0, 2])] = block
            preparation[np.ix_([1, 3], [1, 3])] = block.conj()
            matrix = transform @ preparation
        else:
            raise ValueError("unknown transform control")
    if setting.get("representative", 0):
        permutation = np.eye(matrix.shape[0], dtype=complex)
        permutation[:, [0, 1]] = permutation[:, [1, 0]]
        matrix = matrix @ permutation
    return matrix


def qi_native(matrix: ComplexMatrix, name: str) -> dict[str, Any]:
    """Compile to coupled Rx/Ry/Rz/CZ, round to Tuna's pi/36 grid, retain both laws."""
    from qiskit import QuantumCircuit, transpile
    from qiskit.quantum_info import Operator

    qubits = int(round(math.log2(len(matrix))))
    if qubits not in (2, 3) or matrix.shape != (2**qubits, 2**qubits):
        raise ValueError("the admitted native compiler supports two or three qubits")
    backend, _ = catalogue_check()
    circuit = QuantumCircuit(qubits)
    circuit.unitary(matrix, range(qubits))
    edges = [edge for edge in backend["topology"] if max(edge) < qubits]
    compiled = transpile(
        circuit,
        basis_gates=["rx", "ry", "rz", "cz"],
        coupling_map=edges,
        initial_layout=list(range(qubits)),
        optimization_level=1,
        seed_transpiler=7,
        num_processes=1,
    )
    native = QuantumCircuit(qubits)
    text = ["version 3.0", f"qubit[{qubits}] q", f"bit[{qubits}] b"]
    for instruction in compiled.data:
        operation = instruction.operation
        operands = [compiled.find_bit(qubit).index for qubit in instruction.qubits]
        if operation.name == "cz":
            native.cz(*operands)
            text.append(f"CZ q[{operands[0]}], q[{operands[1]}]")
        else:
            angle = round(float(operation.params[0]) / (math.pi / 36)) * math.pi / 36
            getattr(native, operation.name)(angle, operands[0])
            text.append(f"{operation.name.capitalize()}({angle:.17g}) q[{operands[0]}]")
    final_layout = compiled.layout.final_index_layout() if compiled.layout is not None else list(range(qubits))
    row_order = [
        sum(((basis >> logical) & 1) << physical for logical, physical in enumerate(final_layout))
        for basis in range(2**qubits)
    ]
    native_matrix = np.asarray(Operator(native).data)[row_order]
    compiled_matrix = np.asarray(Operator(compiled).data)[row_order]
    # Layout permutations are part of the comparison, not an inferred device error.
    if compiled.layout is not None:
        requested = np.asarray(Operator.from_circuit(compiled).data)
        if not np.allclose(np.abs(requested[:, 0]) ** 2, np.abs(matrix[:, 0]) ** 2, atol=1e-10):
            raise ValueError("transpiler layout changes the promised initial-state law")
    overlap = np.vdot(compiled_matrix.reshape(-1), native_matrix.reshape(-1))
    alignment = overlap / abs(overlap) if abs(overlap) else 1
    error = float(np.linalg.norm(native_matrix - alignment * compiled_matrix, ord=2))
    text.append("barrier q")
    text.extend(f"b[{logical}] = measure q[{physical}]" for logical, physical in enumerate(final_layout))
    text.append("")
    return {
        "file": f"{name}.cq",
        "source": "\n".join(text),
        "kind": "hypercomplex-operator",
        "nqubits": qubits,
        "operator_error": error,
        "requested_probabilities": (np.abs(matrix[:, 0]) ** 2).tolist(),
        "native_probabilities": (np.abs(native_matrix[:, 0]) ** 2).tolist(),
        "native_operator": encoded(native_matrix),
        "measurement_mapping": final_layout,
        "observable_partition": [[index, index + 1] for index in range(0, len(matrix), 2)],
    }


def _qi_science(setting: dict[str, Any]) -> dict[str, Any]:
    return {**qi_native(setting_operator(setting), setting["name"]), "setting": setting}


def qi_cases(shots: int, family: str = "order") -> dict[str, str]:
    if type(shots) is not int or not 1 <= shots <= 131072:
        raise ValueError("Tuna shots must lie in [1,131072]")
    settings = order_settings() if family == "order" else wave_settings() if family == "wave" else transform_settings()
    sciences = ordered_map(_qi_science, settings, min_items=1)
    files: dict[str, str] = {}
    for index, science in enumerate(sciences):
        directory = f"{family}-batch-{index:02d}"
        qubits = science["nqubits"]
        rows = []
        for prepared in (0, 1):
            source = f"version 3.0\nqubit[{qubits}] q\nbit[{qubits}] b\n"
            if prepared:
                source += "\n".join(f"X q[{qubit}]" for qubit in range(qubits)) + "\n"
            source += "barrier q\nb = measure q\n"
            filename = f"readout-{prepared}.cq"
            files[f"{directory}/{filename}"] = source
            rows.append(
                {
                    "file": filename,
                    "sha256": hashlib.sha256(source.encode()).hexdigest(),
                    "kind": "readout-reference",
                    "prepared": prepared,
                }
            )
        source = science.pop("source")
        files[f"{directory}/{science['file']}"] = source
        science["sha256"] = hashlib.sha256(source.encode()).hexdigest()
        rows.append(science)
        manifest = {
            "schema": "qi-hypercomplex-cases-v1",
            "backend": "tuna_17",
            "backend_type_id": 7,
            "nqubits": qubits,
            "shots": shots,
            "hardware_pause_seconds": 120,
            "job_execution_time_limit": 300,
            "circuits": rows,
            "evidence_kind": "complex encoding and device conformance",
            "preregistered": {
                "primary": "raw grouped probabilities",
                "mitigation": "sensitivity only",
                "shot_order": "retain; test temporal dependence before IID intervals",
                "minimum_output_readout_contrast": 0.2,
            },
            "compiler": {
                "qiskit": importlib.metadata.version("qiskit"),
                "seed": 7,
                "angle_step_radians": math.pi / 36,
                "catalogue_sha256": hashlib.sha256(CATALOGUE.read_bytes()).hexdigest(),
            },
        }
        files[f"{directory}/cases.json"] = json.dumps(manifest, indent=1) + "\n"
    return files


def transform_settings() -> list[dict[str, Any]]:
    return [
        {
            "name": f"transform-{operation}-representative{representative}",
            "operation": operation,
            "representative": representative,
        }
        for operation in (
            "forward",
            "identity-reference",
            "forward-real-superposition",
            "forward-imaginary-superposition",
        )
        for representative in (0, 1)
    ]


def _qd_setting(setting: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    matrix = setting_operator(setting)
    circuit, parameters = photonic_template(matrix)
    return circuit, {
        "name": setting["name"],
        "circuit_params": parameters,
        "column": [[float(value.real), float(value.imag)] for value in matrix[:, 0]],
        "operator": encoded(matrix),
        "setting": setting,
        "compilation_seed": 0,
    }


def qd_cases(settings: list[dict[str, Any]], label: str) -> dict[str, str]:
    compiled = ordered_map(_qd_setting, settings, min_items=1)
    circuit = compiled[0][0]
    iterations = []
    for candidate, iteration in compiled:
        if candidate != circuit:
            raise ValueError("photonic iterations need the same fixed mesh")
        iterations.append(iteration)
    text = json.dumps(circuit, indent=1) + "\n"
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": label,
        "job": label,
        "platforms": ["qpu:ascella", "qpu:belenos", "sim:ascella", "sim:belenos"],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": len(iterations),
        "settings": iterations,
        "min_detected_photons": 1,
        "max_samples": 8192 * len(iterations),
        "max_shots": 16384 * len(iterations),
        "max_duration": 180,
        "circuit": {"file": "circuit.json", "sha256": hashlib.sha256(text.encode()).hexdigest()},
        "preregistered": {
            "primary": "paired mode probabilities",
            "phase": "unmeasured unless reconstructed",
            "interpretation": "complex encoding device test",
        },
    }
    return {"circuit.json": text, "cases.json": json.dumps(manifest, indent=1) + "\n"}


def write_files(directory: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        path = directory / name
        if path.exists() and path.read_text() != text:
            raise ValueError(f"refusing to overwrite different case bytes: {path.name}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--shots", type=int, default=16384)
    arguments = parser.parse_args()
    for family, settings in (
        ("order", order_settings()),
        ("wave", wave_settings()),
        ("transform", transform_settings()),
    ):
        write_files(arguments.out / "quantum_inspire" / family, qi_cases(arguments.shots, family))
        write_files(arguments.out / "quandela" / family, qd_cases(settings, family))
    print("generated submit-free Quantum Inspire and Quandela operator cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
