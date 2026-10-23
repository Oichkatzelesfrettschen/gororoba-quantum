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
import sys
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


def bank() -> list[dict[str, Any]]:
    cases = []
    for name, phase, probability in (("dark", math.pi, 0.0), ("bright", 0.0, 1.0), ("quadrature", math.pi / 2, 0.5)):
        cases.append(
            {
                "name": f"sector-{name}",
                "family": "sector",
                "circuit": lcu_witness((1, 10), (4, 15), phase),
                "expected": {"0": probability, "1": 1 - probability},
            }
        )
    for commuting in (True, False):
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
        cases.append(
            {
                "name": "order-commuting" if commuting else "order-anticommuting",
                "family": "order",
                "circuit": circuit,
                "expected": {"0": float(commuting), "1": float(not commuting)},
            }
        )
    for steps in (1, 2, 4):
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
        cases.append(
            {
                "name": f"measurement-fixed-evolution-{steps}",
                "family": "measurement",
                "circuit": circuit,
                "expected": expected,
            }
        )
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cry(2 * math.pi / 3, 0, 1)
    circuit.measure([0, 1], [0, 1])
    cases.append(
        {
            "name": "contraction-success-failure",
            "family": "instrument",
            "circuit": circuit,
            "expected": {"00": 0.5, "01": 0.125, "10": 0.0, "11": 0.375},
        }
    )
    for dimension in (8, 16, 32):
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
        cases.append(
            {
                "name": f"dimension-{dimension}-associator",
                "family": "dimension",
                "circuit": design_c_associator_spectrum(dimension, 1, 2),
                "expected": expected,
            }
        )
    return cases


def probabilities(circuit: QuantumCircuit) -> dict[str, float]:
    """Enumerate unnormalized measurement branches; retain classical overwrite semantics."""
    branches = [(Statevector.from_int(0, 2**circuit.num_qubits), 0)]
    for instruction in circuit.data:
        operation = instruction.operation
        qubits = [circuit.find_bit(bit).index for bit in instruction.qubits]
        if operation.name == "barrier":
            continue
        if operation.name != "measure":
            branches = [(state.evolve(operation, qargs=qubits), classical) for state, classical in branches]
            continue
        clbit = circuit.find_bit(instruction.clbits[0]).index
        divided = []
        for state, classical in branches:
            for value in (0, 1):
                data = state.data.copy()
                mask = ((np.arange(len(data)) >> qubits[0]) & 1) != value
                data[mask] = 0
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
