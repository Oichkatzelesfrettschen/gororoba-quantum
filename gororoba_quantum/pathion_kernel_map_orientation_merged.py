"""Merged-diagonal members of the orientation-bit kernel map: one six-qubit diagonal per member.

Successor of pathion_kernel_map_orientation, which keeps its bytes (the approved case and its dry runs bind it).

The retained member applies a five-qubit oracle DiagonalGate on the data qubits, a phase on the orientation qubit, H on
the selector, and the six-qubit SELECT DiagonalGate. The oracle, the orientation phase and the Z of a negative operand
are diagonal in the computational basis, and the H on the selector acts on another wire, so the oracle commutes past
it into the SELECT diagonal. The member here applies one six-qubit DiagonalGate with signs oracle(x) * select(x, a):
the operator equals the retained member's on both arms, the logical CZ count falls from 96 and 95 to 64 and 63, and
every role keeps the retained role options (orientation bit, bit-4 exchange, wire exchange of data qubits 1 and 4).
Member names, ideal laws and the pair summary are the retained ones, so the retained analysis reads the records.

Group pathion_kernel_map_orientation_merged holds the sixteen members of pathion_kernel_map_orientation in the same
order. The routed CZ count depends on the six-qubit tile shape and the assignment of logical qubits to it
(docs/design/pathion-kernel-map-orientation-architecture.md, section 3(b)).
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import DiagonalGate

import pathion_kernel_map as pkm
import pathion_kernel_map_orientation as pko
from experiments import Group, Member
from select_lcu import joint_select_signs

GROUP_NAME = "pathion_kernel_map_orientation_merged"


def merged_signs(operand: tuple[int, int, int], orientation_bit: int, *, dim: int = pkm.DIM) -> list[float]:
    """Diagonal of the six-qubit gate at index x + dim * a: select sign at (x, a) times the minus-arm oracle at x."""
    i, j, _ = operand
    oracle = pko.orientation_signs(operand, False, orientation_bit, dim=dim)
    select = joint_select_signs(dim, i, j)
    return [select[z] * oracle[z % dim] for z in range(2 * dim)]


def merged_template(
    role: str, operand: tuple[int, int, int], *, measure: bool = True, dim: int = pkm.DIM
) -> QuantumCircuit:
    """pko.role_template with the oracle folded into the SELECT diagonal."""
    i, j, t = operand
    orientation_bit, exchange_bit = pko.role_options(role, operand)
    data = pkm.data_qubits(dim)
    qc = QuantumCircuit(data + 1, data + 1 if measure else 0)
    qc.h(range(data))
    qc.p(pkm.ORIENTATION, orientation_bit)
    qc.h(data)
    if t < 0:
        qc.z(data)
    qc.append(DiagonalGate(merged_signs(operand, orientation_bit, dim=dim)), range(data + 1))
    for b in range(data):
        if i >> b & 1:
            qc.x(b)
    for b in range(data):
        if (i ^ j) >> b & 1:
            qc.cx(data, b)
    if exchange_bit is not None:
        qc.x(exchange_bit)
    qc.h(data)
    if role == "swap":
        perm = list(range(data + 1))
        a, b = pko.SWAP_WIRES
        perm[a], perm[b] = b, a
        swapped = QuantumCircuit(data + 1, data + 1 if measure else 0)
        swapped.compose(qc, qubits=perm, inplace=True)
        qc = swapped
        if measure:
            for q in range(data + 1):
                qc.measure(perm[q], q)
        return qc
    if measure:
        qc.measure(range(data + 1), range(data + 1))
    return qc


def merged_members() -> tuple[Member, ...]:
    members: list[Member] = []
    templates: dict[str, QuantumCircuit] = {}
    for role, operand, plus in pko.member_order():
        name = pko.unit_name(role, operand)
        if name not in templates:
            templates[name] = merged_template(role, operand)
            templates[name].name = name
        phase = np.pi if plus else 0.0
        template = templates[name]
        ideal = pko.outcome_law(template.assign_parameters({pkm.ORIENTATION: phase}))
        members.append(Member(f"{name}_{'plus' if plus else 'minus'}", template, ideal, {pkm.ORIENTATION: phase}))
    return tuple(members)


def pathion_kernel_map_orientation_merged_group() -> Group:
    members = merged_members()
    ideal = {member.name: member.ideal for member in members}
    prefixes = sorted({member.name.rsplit("_", 1)[0] for member in members})

    def summarize(dist: dict[str, np.ndarray]) -> dict[str, float]:
        summary: dict[str, float] = {}
        for prefix in prefixes:
            summary |= pkm._pair_summary(prefix, dist, ideal)
        return summary

    return Group(GROUP_NAME, members, summarize)


if __name__ == "__main__":
    group = pathion_kernel_map_orientation_merged_group()
    print(f"{len(group.members)} circuits on {pkm.WIDTH} qubits")
