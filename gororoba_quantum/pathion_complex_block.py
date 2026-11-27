"""Complex coset blocks of the pathion kernel map of A_5: the operand e_i + t e_j for t in {1, i, -i}.

pathion_coset_block builds the real blocks (t = +-1) of the pair-resolved kernel map. A block of the operand
e_i + t e_j differs from the block of e_i + e_j by the factor t on the selector-one branch and on every upper member of
an XOR pair (the k with bit h of m set, h the highest set bit of m). With a basis whose only vector carrying bit h is
b_0 = m (``normalized_basis``), the upper indicator of block input x is the parity c_0 XOR x_0, so the factor is one
phase gate on data qubit 0, RZ(PHASE) for c_0 = 0 and RZ(-PHASE) for c_0 = 1 up to a global phase, and one RZ(PHASE) on
the selector. The block circuit is the real block circuit with those two gates: one gate skeleton serves t = 1, i and -i
(PHASE = 0, pi/2, -pi/2) and both orientations (ORIENTATION = 0, pi), so the transpiled skeletons are identical.

The selector marginal of a block, P_plus(s = 0) - P_minus(s = 0), is the mean of its output contrasts c(y), and
2^(d-1) times it is the block's share N_b of the nullity of L_(e_i + t e_j) over C. The strata of the 465 pairs of
imaginary units fix N in {0, 4, 8, 12, 16}, so N / 16 has the denominator 2^(d-1) with d = 1, 3, 2, 3 at N = 0 or 16,
4 or 12, 8 and the complement; the tests check that every coset of the chosen subspaces reads N exactly.
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.circuit.library import DiagonalGate

import pathion_coset_block as pcb
import pathion_kernel_map as pkm
from select_lcu import joint_select_signs

ORIENTATION = pcb.ORIENTATION
PHASE = Parameter("phase")
PHASES: dict[str, complex] = {"1": 1, "i": 1j, "-i": -1j}
ANGLES: dict[str, float] = {"1": 0.0, "i": float(np.pi / 2), "-i": float(-np.pi / 2)}


def normalized_basis(operand: tuple[int, int, int], basis: tuple[int, ...]) -> tuple[int, ...]:
    """The basis with bit h of m cleared from every vector after b_0 = m, spanning the same subspace."""
    h = pkm.upper_bit(operand)
    return (basis[0], *(vector ^ basis[0] if vector >> h & 1 else vector for vector in basis[1:]))


def _parts(block: pcb.Block, *, plain: bool) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(real first diagonal of the minus arm, real second diagonal's upper half, upper indicator) over inputs x.

    Plain replaces the pair sign s_k of the oracle by 1 (mutation control)."""
    i, j, _ = block.operand
    labels = pcb.input_labels(block)
    h = pkm.upper_bit(block.operand)
    upper = np.array([(k >> h) & 1 for k in labels])
    base = np.array([pkm.orientation_signs((i, j, 1), False, dim=block.dim)[k] for k in labels])
    orientation = np.where(upper == 1, -1.0, 1.0) if plain else base
    signs = joint_select_signs(block.dim, i, j)
    f0 = np.array([signs[k] for k in labels])
    f1 = np.array([signs[k + block.dim] for k in labels])
    return orientation * f0, f0 * f1, upper


def block_law(block: pcb.Block, t: complex, plus: bool, *, plain: bool = False) -> np.ndarray:
    """Outcome law indexed y + 2^d s from the amplitudes with the factor t folded into the diagonals (the reference
    of the gate form)."""
    first, second, upper = _parts(block, plain=plain)
    first = np.where(upper == 1, first * t, first)
    psi = first * (np.where(upper == 1, -1.0, 1.0) if plus else 1.0) / np.sqrt(float(1 << block.d))
    low = psi / np.sqrt(2.0)
    high = (psi * second * t / np.sqrt(2.0))[np.arange(1 << block.d) ^ 1]
    return np.concatenate([np.abs(low + high) ** 2 / 2.0, np.abs(low - high) ** 2 / 2.0])


def block_template(block: pcb.Block, *, plain: bool = False, measure: bool = True) -> QuantumCircuit:
    """The block circuit with ORIENTATION and PHASE unbound."""
    if pcb.upper_qubits(block) != [0]:
        raise ValueError(f"{block.tag}: bit h of m must sit on basis vector 0 alone (use normalized_basis)")
    first, second, _ = _parts(block, plain=plain)
    d = block.d
    sign = -1.0 if block.coset >> pkm.upper_bit(block.operand) & 1 else 1.0
    qc = QuantumCircuit(d + 1, d + 1 if measure else 0)
    qc.h(range(d))
    qc.append(DiagonalGate(list(first)), range(d))
    # The two phase gates stay Z rotations behind barriers, so a compile keeps them apart from the neighboring
    # rotations and a Z rotation moves to the end of the circuit as a shift of the phase of every later PRX.
    qc.barrier(0)
    qc.rz(ORIENTATION + sign * PHASE, 0)
    qc.barrier(0)
    qc.h(d)
    qc.barrier(d)
    qc.rz(PHASE, d)
    qc.barrier(d)
    qc.append(DiagonalGate([1.0] * (1 << d) + list(second)), range(d + 1))
    qc.cx(d, 0)
    qc.h(d)
    if measure:
        qc.measure(range(d + 1), range(d + 1))
    return qc


def block_circuit(block: pcb.Block, label: str, plus: bool, **options: bool) -> QuantumCircuit:
    """The bound circuit for t = PHASES[label] (label 1, i or -i) and the arm."""
    return block_template(block, **options).assign_parameters(
        {ORIENTATION: np.pi if plus else 0.0, PHASE: ANGLES[label]}
    )


def selector_marginal(block: pcb.Block, t: complex, *, plain: bool = False) -> float:
    """P_plus(s = 0) - P_minus(s = 0) of the block."""
    half = 1 << block.d
    plus = block_law(block, t, True, plain=plain)
    minus = block_law(block, t, False, plain=plain)
    return float(plus[:half].sum() - minus[:half].sum())
