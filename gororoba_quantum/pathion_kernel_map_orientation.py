"""Orientation-bit variants of the pair-resolved kernel map of two-term operands of A_5.

Successor of pathion_kernel_map, which is digest-pinned and keeps its bytes.

pathion_kernel_map fixes the orientation phase on the highest bit h of m = i XOR j, so the lower member of every XOR
pair {k, k XOR m} clears bit h and the plus arm is the minus arm with a phase pi on data qubit h. Any set bit b of m
splits the pairs the same way: the member with bit b clear is the lower one, the oracle is +1 on it and -s on the upper
member, with s = K[upper, lower] the sign of K = L_i^T (t L_j) that carries the lower member to the upper, and the
plus arm differs by a phase pi on data qubit b. The split changes only which member of a misaligned pair carries the
-1 of the ideal per-output contrast, so every contrast stays +-1 and the nullity N is unchanged. The signature
character of the Walsh support moves from 2^h to 2^b; each support holds eight characters, three of the other seven
are shared by the retained and the moved map, no statistic of the case reads a shared character, and the (0, signature)
weight pair is identical between them (tests/gororoba_quantum/test_pathion_kernel_map_orientation.py, SUPPORTS).

Two orientation-bit options extend the circuit, with the retained circuit as their default (orientation_bit = h,
no exchange):

- orientation_bit b: the oracle, the phase P(ORIENTATION) and the plus/minus pair move to data qubit b.
- exchange_bit q: one X on data qubit q after the SELECT and before measurement. The sign relation of the quarter-turn
  twin, s_twin(x) = -s_primary(x XOR 16), makes the twin's ideal outcome law equal to the primary's with data bit 4
  exchanged, which is this X; the equality holds on all 64 outcomes of both arms
  (tests/gororoba_quantum/test_pathion_kernel_map_orientation.py). The member with the exchange compiles to the
  control's cz, sx and x sequence plus a changed rz angle on the wire measured into data bit 4, so the statistic D
  (control minus exchange) is zero under every error that acts before that frame and responds only to asymmetric readout
  of that qubit or a coherent angle error on its final single-qubit tail.

The role "swap" is the retained circuit with data wires 1 and 4 exchanged (swap_wires): every gate acts on the other
wire and each wire still measures into its own classical bit, so the ideal outcome law is the control's. All members of
a group run on one layout, so the swap member puts data bit 4 on the physical qubit that carries data bit 1 in the other
members and data bit 1 on the one that carries bit 4. Its gap lambda_16 - lambda_0 and the moved member's gap
lambda_2 - lambda_0 are then read on the same physical qubit, which removes the T1, T2 and readout difference between
the two qubits from their difference (the statistic diff_sm of the analysis).

Group pathion_kernel_map_orientation holds, for the nullity-4 operand e1 + e26 (m = 27) and the nullity-12 operand
e1 + e18 (m = 19), four members each with plus and minus arms on one layout: the retained placement (orientation on
bit 4), the orientation moved to bit 1 (a set bit of both m, with character 2 in the ideal support), the retained
placement with the bit-4 exchange, and the retained circuit with data wires 1 and 4 exchanged. The experiment question
is whether the character gap lambda_16 - lambda_0 of the retained map follows the orientation qubit
(docs/design/pathion-kernel-map-orientation-bit.md).
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import DiagonalGate
from qiskit.quantum_info import Statevector

import pathion_kernel_map as pkm
from experiments import Group, Member

DIM = pkm.DIM
OPERANDS: tuple[tuple[int, int, int], ...] = ((1, 26, 1), (1, 18, 1))
# Bit 1 is set in m = 27 and m = 19, and is the lowest common set bit other than the retained bit 4 and bit 0.
MOVED_BIT = 1
EXCHANGE_BIT = 4
ROLES = ("ctrl", "move", "xtwin", "swap")
SWAP_WIRES = (MOVED_BIT, EXCHANGE_BIT)


def orientation_signs(operand: tuple[int, int, int], plus: bool, bit: int, *, dim: int = DIM) -> list[float]:
    """Oracle signs of one arm with the XOR pairs split by data bit `bit`: +1 on the member that clears the bit and
    -s (minus arm) or +s (plus arm) on the member that sets it, s = K[upper, lower]."""
    i, j, _ = operand
    m = i ^ j
    if not m >> bit & 1:
        raise ValueError(f"bit {bit} is clear in m = {m}: it does not split the pairs of {operand}")
    k_matrix = pkm._k_matrix(operand, dim)
    signs = [1.0] * dim
    for lower in range(dim):
        upper = lower ^ m
        if not lower >> bit & 1:
            s = float(k_matrix[upper, lower])
            signs[upper] = s if plus else -s
    return signs


def kernel_map_template(
    operand: tuple[int, int, int],
    *,
    orientation_bit: int | None = None,
    exchange_bit: int | None = None,
    swap_wires: tuple[int, int] | None = None,
    cocycle_free: bool = False,
    flip_input: int | None = None,
    measure: bool = True,
    dim: int = DIM,
) -> QuantumCircuit:
    """pathion_kernel_map.kernel_map_template with the orientation on `orientation_bit` (default the highest bit of
    m), an optional X on data qubit `exchange_bit` between the SELECT and the readout, and the SELECT mutations of
    the retained map (cocycle-free layers, one negated joint sign) for the mutation test. With swap_wires (a, b) every
    gate acts on the other of the two data wires while each wire measures into its own classical bit."""
    i, j, t = operand
    data = pkm.data_qubits(dim)
    bit = pkm.upper_bit(operand) if orientation_bit is None else orientation_bit
    qc = QuantumCircuit(data + 1, data + 1 if measure else 0)
    qc.h(range(data))
    qc.append(DiagonalGate(orientation_signs(operand, False, bit, dim=dim)), range(data))
    qc.p(pkm.ORIENTATION, bit)
    qc.h(data)
    if t < 0:
        qc.z(data)
    select = pkm._cocycle_free_select(i, j, dim) if cocycle_free else pkm._select(i, j, flip_input, dim)
    qc.compose(select, range(data + 1), inplace=True)
    if exchange_bit is not None:
        qc.x(exchange_bit)
    qc.h(data)
    if swap_wires is not None:
        perm = list(range(data + 1))
        a, b = swap_wires
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


def role_options(role: str, operand: tuple[int, int, int]) -> tuple[int, int | None]:
    """(orientation bit, exchange bit) of one role: ctrl is the retained circuit, move the orientation on MOVED_BIT,
    xtwin the retained circuit with the bit-4 exchange, swap the retained circuit (role_template swaps wires)."""
    if role in ("ctrl", "swap"):
        return pkm.upper_bit(operand), None
    if role == "move":
        return MOVED_BIT, None
    if role == "xtwin":
        return pkm.upper_bit(operand), EXCHANGE_BIT
    raise ValueError(f"unknown role {role!r}")


def role_template(role: str, operand: tuple[int, int, int]) -> QuantumCircuit:
    orientation_bit, exchange_bit = role_options(role, operand)
    return kernel_map_template(
        operand,
        orientation_bit=orientation_bit,
        exchange_bit=exchange_bit,
        swap_wires=SWAP_WIRES if role == "swap" else None,
    )


def outcome_law(circuit: QuantumCircuit) -> np.ndarray:
    """Ideal outcome law indexed by the classical bits (bit j of the index is classical bit j), for a circuit whose
    wires measure into any classical bits; equals pathion_kernel_map.ideal_law when wire j measures into bit j."""
    measured: dict[int, int] = {}
    core = QuantumCircuit(circuit.num_qubits)
    for instruction in circuit.data:
        if instruction.operation.name == "measure":
            measured[circuit.find_bit(instruction.clbits[0]).index] = circuit.find_bit(instruction.qubits[0]).index
        else:
            core.append(instruction.operation, [circuit.find_bit(q).index for q in instruction.qubits])
    order = [measured[j] for j in range(len(measured))]
    return np.asarray(Statevector(core).probabilities(order))


def unit_name(role: str, operand: tuple[int, int, int]) -> str:
    return f"kmo_{role}_{pkm.operand_tag(operand)}"


# Arms alternate their order unit by unit (plus first, minus first, ...), so each arm holds early and late positions
# in the job while every unit keeps its two arms adjacent.
def member_order() -> list[tuple[str, tuple[int, int, int], bool]]:
    order: list[tuple[str, tuple[int, int, int], bool]] = []
    flip = False
    for operand in OPERANDS:
        for role in ROLES:
            arms = (True, False) if not flip else (False, True)
            order.extend((role, operand, plus) for plus in arms)
            flip = not flip
    return order


def orientation_members() -> tuple[Member, ...]:
    members: list[Member] = []
    templates: dict[str, QuantumCircuit] = {}
    for role, operand, plus in member_order():
        name = unit_name(role, operand)
        if name not in templates:
            templates[name] = role_template(role, operand)
            templates[name].name = name
        phase = np.pi if plus else 0.0
        template = templates[name]
        ideal = outcome_law(template.assign_parameters({pkm.ORIENTATION: phase}))
        members.append(Member(f"{name}_{'plus' if plus else 'minus'}", template, ideal, {pkm.ORIENTATION: phase}))
    return tuple(members)


def pathion_kernel_map_orientation_group() -> Group:
    members = orientation_members()
    ideal = {member.name: member.ideal for member in members}
    prefixes = sorted({member.name.rsplit("_", 1)[0] for member in members})

    def summarize(dist: dict[str, np.ndarray]) -> dict[str, float]:
        summary: dict[str, float] = {}
        for prefix in prefixes:
            summary |= pkm._pair_summary(prefix, dist, ideal)
        return summary

    return Group("pathion_kernel_map_orientation", members, summarize)


if __name__ == "__main__":
    group = pathion_kernel_map_orientation_group()
    print(f"{len(group.members)} circuits on {pkm.WIDTH} qubits")
