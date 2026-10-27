"""Execution-start calibration of a collected PUB, stored once per PUB.

The header entry of collect.json (its first element) holds `pub_calibration[pub_name]`: the calibration in force
at the PUB's execution start over every qubit the PUB ran (`placed_qubit_calibration`, and
`placed_gate_calibration` for the measurement-sequence families). Each member's `executed` entry keeps the same
two mappings restricted to its own physical qubits, and `pub` names its row in `pub_calibration`. A record
collected before the map exists holds the full-PUB values on every member; a reader that needs only a member's
own qubits reads both forms through the member entry, and a reader that needs the whole PUB takes the union over
the PUB's members, which is the PUB's qubit set.
"""

from __future__ import annotations


def split_pub_calibration(
    full: dict[str, dict[str, dict[str, float]]], member_qubits: list[int]
) -> dict[str, dict[str, dict[str, float]]]:
    """Each calibration mapping of a PUB restricted to the member's own qubits."""
    keys = {str(qubit) for qubit in member_qubits}
    return {field: {q: values for q, values in table.items() if q in keys} for field, table in full.items()}
