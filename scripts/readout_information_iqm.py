"""Construct unassigned IQM readout-context source alternatives.

Inputs require fresh validation against the selected calibration architecture.
The catalogue does not choose order, compile, authorize or submit a job.
"""

import math
from typing import Any


def alternatives(qubits: tuple[str, ...], target_qubits: tuple[str, str]) -> dict[tuple[str, int], dict[str, Any]]:
    """Build four input preparations in each context with a fixed readout set."""
    if (
        type(qubits) is not tuple
        or len(qubits) < 2
        or any(type(qubit) is not str or not qubit for qubit in qubits)
        or len(set(qubits)) != len(qubits)
        or type(target_qubits) is not tuple
        or len(target_qubits) != 2
        or any(type(qubit) is not str or qubit not in qubits for qubit in target_qubits)
        or target_qubits[0] == target_qubits[1]
    ):
        raise ValueError("two distinct target qubits must belong to a unique measured set")
    circuits: dict[tuple[str, int], dict[str, Any]] = {}
    for context in ("sparse", "dense"):
        for input_bits in range(4):
            selected = [qubit for position, qubit in enumerate(target_qubits) if (input_bits >> position) & 1]
            if context == "dense":
                selected.extend(qubit for qubit in qubits if qubit not in target_qubits)
            instructions = [
                {"name": "prx", "locus": [qubit], "args": {"angle": math.pi, "phase": 0.0}} for qubit in selected
            ]
            instructions.append({"name": "measure", "locus": list(qubits), "args": {"key": "c"}})
            circuits[(context, input_bits)] = {
                "name": f"{context}-input-{input_bits:02b}",
                "instructions": instructions,
            }
    return circuits
