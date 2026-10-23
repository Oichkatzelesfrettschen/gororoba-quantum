"""Build offline algebra/instrument cases and check every measurement branch.

The bank contains logical circuits, not backend-qualified submissions. Exact
finite certificates and retained hardware analyses live in the conjecture
synthesis. This module checks circuit conformance without sampled jobs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, qasm3, transpile
from qiskit.quantum_info import Statevector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from cd_core import cd_sign  # noqa: E402
from designs import design_c_associator_spectrum, lcu_witness  # noqa: E402
from parallel import ordered_map  # noqa: E402


def _build_case(task: tuple[str, Any]) -> dict[str, Any]:
    """Construct one independent logical instrument before its conformance check."""
    kind, parameter = task
    if kind == "sector":
        name, phase, probability = parameter
        return {
            "name": f"sector-{name}",
            "family": "sector",
            "circuit": lcu_witness((1, 10), (4, 15), phase),
            "expected": {"0": probability, "1": 1 - probability},
        }
    if kind == "order":
        commuting = parameter
        circuit = QuantumCircuit(2, 1)
        circuit.h(0)
        circuit.x(0)
        circuit.cx(0, 1)
        (circuit.cx if commuting else circuit.cz)(0, 1)
        circuit.x(0)
        (circuit.cx if commuting else circuit.cz)(0, 1)
        circuit.cx(0, 1)
        circuit.h(0)
        circuit.measure(0, 0)
        return {
            "name": "order-commuting" if commuting else "order-anticommuting",
            "family": "order",
            "circuit": circuit,
            "expected": {"0": float(commuting), "1": float(not commuting)},
        }
    if kind == "dephased":
        dephased = QuantumCircuit(2, 2)
        dephased.h(0)
        dephased.measure(0, 1)
        dephased.x(0)
        dephased.cx(0, 1)
        dephased.cz(0, 1)
        dephased.x(0)
        dephased.cz(0, 1)
        dephased.cx(0, 1)
        dephased.h(0)
        dephased.measure(0, 0)
        return {
            "name": "order-dephased",
            "family": "order",
            "circuit": dephased,
            "expected": {"00": 0.25, "01": 0.25, "10": 0.25, "11": 0.25},
        }
    if kind == "fixed":
        sequence = parameter
        fixed = QuantumCircuit(1, 1)
        for gate in sequence:
            getattr(fixed, gate)(0)
        fixed.measure(0, 0)
        return {
            "name": f"order-fixed-{sequence}",
            "family": "order",
            "circuit": fixed,
            "expected": {"0": 0.0, "1": 1.0},
        }
    if kind == "measurement":
        steps = parameter
        circuit = QuantumCircuit(1, steps)
        for step in range(steps):
            circuit.ry(math.pi / (2 * steps), 0)
            circuit.measure(0, step)
        expected = {}
        for bits in range(2**steps):
            previous, probability = 0, 1.0
            for step in range(steps):
                value = (bits >> step) & 1
                probability *= (math.cos if previous == value else math.sin)(math.pi / (4 * steps)) ** 2
                previous = value
            expected[format(bits, f"0{steps}b")] = probability
        return {
            "name": f"measurement-fixed-evolution-{steps}",
            "family": "measurement",
            "circuit": circuit,
            "expected": expected,
        }
    if kind in ("unmeasured", "reset"):
        circuit = QuantumCircuit(1, 4 if kind == "reset" else 1)
        for step in range(4):
            circuit.ry(math.pi / 8, 0)
            if kind == "reset":
                circuit.measure(0, step)
                circuit.reset(0)
        if kind == "unmeasured":
            circuit.measure(0, 0)
            expected = {"0": 0.5, "1": 0.5}
        else:
            expected = {
                format(bits, "04b"): math.sin(math.pi / 16) ** (2 * bits.bit_count())
                * math.cos(math.pi / 16) ** (2 * (4 - bits.bit_count()))
                for bits in range(16)
            }
        return {"name": f"measurement-{kind}-4", "family": "measurement", "circuit": circuit, "expected": expected}
    if kind == "contraction":
        circuit = QuantumCircuit(2, 2)
        circuit.h(0)
        circuit.cry(2 * math.pi / 3, 0, 1)
        circuit.measure([0, 1], [0, 1])
        return {
            "name": "contraction-success-failure",
            "family": "instrument",
            "circuit": circuit,
            "expected": {"00": 0.5, "01": 0.125, "10": 0.0, "11": 0.375},
        }
    if kind == "dimension":
        dimension = parameter
        signs = [
            cd_sign(dimension, 1, 2)
            * cd_sign(dimension, 3, index)
            * cd_sign(dimension, 2, index)
            * cd_sign(dimension, 1, 2 ^ index)
            for index in range(dimension)
        ]
        expected = {
            format(index, f"0{dimension.bit_length() - 1}b"): (
                sum(sign * (-1) ** ((index & source).bit_count()) for source, sign in enumerate(signs)) / dimension
            )
            ** 2
            for index in range(dimension)
        }
        return {
            "name": f"dimension-{dimension}-associator",
            "family": "dimension",
            "circuit": design_c_associator_spectrum(dimension, 1, 2),
            "expected": expected,
        }
    raise ValueError(f"unknown logical instrument family: {kind}")


def bank() -> list[dict[str, Any]]:
    tasks: list[tuple[str, Any]] = [
        ("sector", ("dark", math.pi, 0.0)),
        ("sector", ("bright", 0.0, 1.0)),
        ("sector", ("quadrature", math.pi / 2, 0.5)),
        ("order", True),
        ("order", False),
        ("dephased", None),
        ("fixed", "xz"),
        ("fixed", "zx"),
        ("measurement", 1),
        ("measurement", 2),
        ("measurement", 4),
        ("unmeasured", None),
        ("reset", None),
        ("contraction", None),
        ("dimension", 8),
        ("dimension", 16),
        ("dimension", 32),
    ]
    return ordered_map(_build_case, tasks, min_items=1)


def probabilities(circuit: QuantumCircuit) -> dict[str, float]:
    """Enumerate unnormalized measurement branches; retain classical overwrite semantics."""
    branches = [(Statevector.from_int(0, 2**circuit.num_qubits), 0)]
    for instruction in circuit.data:
        operation = instruction.operation
        qubits = [circuit.find_bit(bit).index for bit in instruction.qubits]
        if operation.name == "barrier":
            continue
        if operation.name not in ("measure", "reset"):
            branches = [(state.evolve(operation, qargs=qubits), classical) for state, classical in branches]
            continue
        clbit = circuit.find_bit(instruction.clbits[0]).index if operation.name == "measure" else None
        divided = []
        for state, classical in branches:
            for value in (0, 1):
                data = state.data.copy()
                mask = ((np.arange(len(data)) >> qubits[0]) & 1) != value
                data[mask] = 0
                if clbit is None:
                    if value:
                        data = data[np.arange(len(data)) ^ (1 << qubits[0])]
                    divided.append((Statevector(data), classical))
                else:
                    divided.append((Statevector(data), (classical & ~(1 << clbit)) | (value << clbit)))
        branches = divided
    result: dict[str, float] = {}
    for state, classical in branches:
        key = format(classical, f"0{circuit.num_clbits}b")
        result[key] = result.get(key, 0.0) + float(np.vdot(state.data, state.data).real)
    return result


def check_case(row: dict[str, Any]) -> dict[str, Any]:
    circuit = transpile(
        row["circuit"], basis_gates=["cx", "rz", "sx", "x"], optimization_level=0, seed_transpiler=0, num_processes=1
    )
    measured = probabilities(circuit)
    expected = row["expected"]
    if any(not math.isfinite(value) for value in (*measured.values(), *expected.values())):
        raise ValueError(f"{row['name']}: probability laws must be finite")
    if any(value < 0 or value > 1 for value in expected.values()) or abs(sum(expected.values()) - 1) > 1e-10:
        raise ValueError(f"{row['name']}: expected law must be a normalized probability distribution")
    if abs(sum(measured.values()) - 1) > 1e-10 or any(
        abs(measured.get(key, 0) - expected.get(key, 0)) > 1e-10 for key in measured.keys() | expected.keys()
    ):
        raise ValueError(f"{row['name']}: compiled instrument differs from its declared probability law")
    return {
        "name": row["name"],
        "family": row["family"],
        "qubits": circuit.num_qubits,
        "classical_bits": circuit.num_clbits,
        "probabilities": measured,
        "expected": expected,
        "logical_depth": circuit.depth(),
        "gate_counts": dict(circuit.count_ops()),
        "qasm": qasm3.dumps(circuit),
        "hardware_admitted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write logical QASM and conformance record; default checks only")
    args = parser.parse_args()
    checked = ordered_map(check_case, bank(), min_items=1)
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        for row in checked:
            qasm = row.pop("qasm")
            name = row["name"] + ".qasm"
            (args.out / name).write_text(qasm)
            row["qasm_path"], row["qasm_sha256"] = name, hashlib.sha256(qasm.encode()).hexdigest()
        (args.out / "circuits.json").write_text(
            json.dumps(
                {
                    "schema": "algebra-conjecture-circuits-v1",
                    "evidence_class": "circuit-conformance check",
                    "versions": {
                        "python": platform.python_version(),
                        "qiskit": version("qiskit"),
                        "numpy": version("numpy"),
                    },
                    "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    "cases": checked,
                    "boundary": (
                        "Logical basis compilation; fresh physical routing, timing, costs "
                        "and approval precede execution."
                    ),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
    print(f"{len(checked)} complete logical instruments match their probability laws within 1e-10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
