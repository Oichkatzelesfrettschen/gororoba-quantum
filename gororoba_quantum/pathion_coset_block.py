"""Coset blocks of the pair-resolved kernel map of A_n, as circuits on d data qubits and the selector.

pathion_kernel_map runs the map on all 32 basis states. The SELECT of the operand e_i + t e_j sends k to
k XOR i XOR (s m), m = i XOR j, so for any subspace V of (Z/2)^5 that contains m it maps the coset k0 + V onto
the coset (k0 XOR i) + V, and the uniform input with the orientation oracle splits into 32 / |V| independent blocks.
A block with the basis (m, b_1, ..., b_(d-1)) of V takes the 2^d inputs k0 XOR (sum of x_c b_c), numbers them by the
bits x of that sum, and reads the output coset (k0 XOR i) XOR (sum of y_c b_c) by the bits y. In these coordinates
the permutation is one CNOT from the selector onto data bit 0, because m is the first basis vector, so a block is
H on the d data qubits, a diagonal on them (the orientation oracle times the s = 0 SELECT sign), H on the selector, a
diagonal on d + 1 qubits (the ratio of the two SELECT sign tables, with the Z of t = -1 folded in), the CNOT, and H on
the selector. The block law is the six-qubit law of pathion_kernel_map restricted to the output coset and divided by
the number of cosets, ``restriction_error`` measures the departure, and the cosets of one V tile the full map.

The two orientations differ by -1 on every upper member of an XOR pair, the k with bit h of m set. In block
coordinates that indicator is c_0 XOR (sum of x_c h_c) with h_c the bit h of b_c, so the plus arm is the minus arm with
a phase pi on each data qubit c with h_c = 1, up to a global phase; data qubit 0 always qualifies because b_0 = m.
Both arms are one parametrized circuit, ``ORIENTATION`` binds 0 or pi, and they route to identical CZ sequences.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import DiagonalGate
from qiskit.quantum_info import Statevector

import pathion_kernel_map as pkm
from experiments import Group, Member
from select_lcu import joint_select_signs

# Orientation phase on the data qubits that carry the upper-member bit: 0 binds the minus arm, pi the plus arm.
ORIENTATION = pkm.ORIENTATION


@dataclass(frozen=True)
class Block:
    """One coset of the subspace V = span(basis) for the operand e_i + t e_j; basis[0] is m = i XOR j."""

    name: str
    operand: tuple[int, int, int]
    basis: tuple[int, ...]
    coset: int
    dim: int = pkm.DIM

    def __post_init__(self) -> None:
        i, j, _ = self.operand
        pkm.data_qubits(self.dim)
        if not all(0 <= index < self.dim for index in (i, j, self.coset, *self.basis)):
            raise ValueError(f"{self.name}: an index lies outside the algebra of dimension {self.dim}")
        if self.basis[0] != i ^ j:
            raise ValueError(f"{self.name}: the first basis vector {self.basis[0]} is not m = {i ^ j}")
        if len(set(span(self.basis))) != 1 << len(self.basis):
            raise ValueError(f"{self.name}: the basis {self.basis} is linearly dependent")

    @property
    def d(self) -> int:
        return len(self.basis)

    @property
    def tag(self) -> str:
        prefix = "" if self.dim == pkm.DIM else f"d{self.dim}_"
        return f"{prefix}{pkm.operand_tag(self.operand)}_v{'-'.join(map(str, self.basis))}_k{self.coset}"


def span(basis: tuple[int, ...]) -> list[int]:
    """Element x of the list is the XOR of the basis vectors named by the set bits of x."""
    out = [0]
    for vector in basis:
        out += [member ^ vector for member in out]
    return out


def input_labels(block: Block) -> list[int]:
    """Algebra index of the block's input x."""
    members = span(block.basis)
    return [block.coset ^ members[x] for x in range(1 << block.d)]


def output_labels(block: Block) -> list[int]:
    """Algebra index of the block's output bin y: the output coset (k0 XOR i) + V."""
    members = span(block.basis)
    return [block.coset ^ block.operand[0] ^ members[y] for y in range(1 << block.d)]


def upper_qubits(block: Block) -> list[int]:
    """Data qubits whose basis vector carries bit h of m, the orientation phase's targets."""
    h = pkm.upper_bit(block.operand)
    return [c for c, vector in enumerate(block.basis) if vector >> h & 1]


def block_template(
    block: Block, *, cocycle_free: bool = False, direct_plus: bool = False, measure: bool = True
) -> QuantumCircuit:
    """The block circuit with ORIENTATION unbound; ``direct_plus`` builds the plus oracle diagonal explicitly with
    no phase gates, the reference the parametrized form is checked against."""
    i, j, t = block.operand
    d = block.d
    labels = input_labels(block)
    orientation = pkm.orientation_signs(block.operand, direct_plus, dim=block.dim)
    signs = joint_select_signs(block.dim, i, j)
    f0 = np.array([signs[k] for k in labels])
    f1 = np.array([signs[k + block.dim] for k in labels]) * (-1.0 if t < 0 else 1.0)
    if cocycle_free:
        f0 = np.ones(1 << d)
        f1 = np.full(1 << d, -1.0 if t < 0 else 1.0)
    qc = QuantumCircuit(d + 1, d + 1 if measure else 0)
    qc.h(range(d))
    qc.append(DiagonalGate(list(np.array([orientation[k] for k in labels]) * f0)), range(d))
    if not direct_plus:
        for c in upper_qubits(block):
            qc.p(ORIENTATION, c)
    qc.h(d)
    qc.append(DiagonalGate([1.0] * (1 << d) + list(f0 * f1)), range(d + 1))
    qc.cx(d, 0)
    qc.h(d)
    if measure:
        qc.measure(range(d + 1), range(d + 1))
    return qc


def block_circuit(block: Block, plus: bool, **options: bool) -> QuantumCircuit:
    template = block_template(block, **options)
    return template.assign_parameters({ORIENTATION: np.pi if plus else 0.0})


def block_law(circuit: QuantumCircuit) -> np.ndarray:
    """Outcome law indexed y + 2^d s (data clbits first, selector last)."""
    return np.asarray(Statevector(circuit.remove_final_measurements(inplace=False)).probabilities())


def block_law_closed_form(block: Block, plus: bool, *, cocycle_free: bool = False) -> np.ndarray:
    """``block_law`` of the same circuit from its amplitudes, with no state-vector evolution.

    After H on the data qubits and the oracle diagonal the data amplitudes are psi = orientation * f0 / sqrt(2^d); the
    selector H splits them into low = psi / sqrt 2 on s = 0 and high = f0 f1 psi / sqrt 2 on s = 1, the CNOT moves the
    selector-1 amplitudes from x to x XOR 1, and the final selector H returns (low +- high) / sqrt 2 on s = 0, 1."""
    i, j, t = block.operand
    labels = input_labels(block)
    orientation = pkm.orientation_signs(block.operand, plus, dim=block.dim)
    signs = joint_select_signs(block.dim, i, j)
    f0 = np.array([signs[k] for k in labels])
    f1 = np.array([signs[k + block.dim] for k in labels]) * (-1.0 if t < 0 else 1.0)
    if cocycle_free:
        f0 = np.ones(1 << block.d)
        f1 = np.full(1 << block.d, -1.0 if t < 0 else 1.0)
    psi = np.array([orientation[k] for k in labels]) * f0 / np.sqrt(float(1 << block.d))
    low = psi / np.sqrt(2.0)
    high = (psi * f0 * f1 / np.sqrt(2.0))[np.arange(1 << block.d) ^ 1]
    return np.concatenate([(low + high) / np.sqrt(2.0), (low - high) / np.sqrt(2.0)]) ** 2


def selector_contrast(plus_law: np.ndarray, minus_law: np.ndarray) -> float:
    half = plus_law.size // 2
    return float(plus_law[:half].sum() - minus_law[:half].sum())


def output_contrast(plus_law: np.ndarray, minus_law: np.ndarray) -> np.ndarray:
    """c(y) = P_plus(s = 0 | y) - P_minus(s = 0 | y); a bin with no weight in an arm reads 0."""
    half = plus_law.size // 2

    def conditional(law: np.ndarray) -> np.ndarray:
        total = law[:half] + law[half:]
        return np.divide(law[:half], total, out=np.zeros(half), where=total > pkm.ZERO)

    return conditional(plus_law) - conditional(minus_law)


def aligned_in_block(block: Block) -> int:
    """Aligned XOR pairs inside the block, N_b = (sum of c(y)) / 2 of the ideal law."""
    plus = block_law(block_circuit(block, True))
    minus = block_law(block_circuit(block, False))
    return int(round(float(output_contrast(plus, minus).sum()) / 2.0))


def restriction_error(block: Block, plus: bool, *, cocycle_free: bool = False) -> float:
    """Largest probability difference between the block law and the module's six-qubit law on the output coset.

    The six-qubit input is uniform, so each of the 32 / |V| cosets carries weight |V| / 32 and the module's law on
    the output coset equals |V| / 32 times the block law."""
    full = pkm.ideal_law(pkm.kernel_map_circuit(block.operand, plus, cocycle_free=cocycle_free, dim=block.dim))
    reduced = block_law(block_circuit(block, plus, cocycle_free=cocycle_free))
    weight = (1 << block.d) / block.dim
    labels = output_labels(block)
    size = 1 << block.d
    return max(
        abs(full[labels[y] + block.dim * s] - weight * reduced[y + size * s]) for y in range(size) for s in (0, 1)
    )


def contrast_restriction_error(block: Block, *, cocycle_free: bool = False) -> float:
    """Largest difference between the block's c(y) and the module's c(k) on the output coset."""
    full = pkm.output_contrast(
        pkm.ideal_law(pkm.kernel_map_circuit(block.operand, True, cocycle_free=cocycle_free, dim=block.dim)),
        pkm.ideal_law(pkm.kernel_map_circuit(block.operand, False, cocycle_free=cocycle_free, dim=block.dim)),
    )
    reduced = output_contrast(
        block_law(block_circuit(block, True, cocycle_free=cocycle_free)),
        block_law(block_circuit(block, False, cocycle_free=cocycle_free)),
    )
    labels = output_labels(block)
    return float(max(abs(full[labels[y]] - reduced[y]) for y in range(1 << block.d)))


def orientation_error(block: Block) -> float:
    """Largest departure of the parametrized plus arm from the explicit plus construction, as states up to a
    global phase: 1 - |<a|b>| of the two final states."""
    bound = Statevector(block_circuit(block, True, measure=False))
    direct = Statevector(block_template(block, direct_plus=True, measure=False))
    return float(1.0 - abs(np.vdot(bound.data, direct.data)))


def cosets(basis: tuple[int, ...], dim: int = pkm.DIM) -> list[int]:
    """One representative of every coset of span(basis) in (Z/2)^n, dim = 2^n, ascending."""
    members = set(span(basis))
    reps: list[int] = []
    covered: set[int] = set()
    for k in range(dim):
        if k not in covered:
            reps.append(k)
            covered |= {k ^ v for v in members}
    return reps


def tile(operand: tuple[int, int, int], basis: tuple[int, ...], dim: int = pkm.DIM) -> dict[str, object]:
    """The blocks of one subspace over every coset: their output bins cover all dim algebra indices once, their
    aligned counts N_b sum to the nullity of L_(e_i + t e_j), and the concatenated c(y) equals the module's c(k)."""
    blocks = [Block(f"coset{k0}", operand, basis, k0, dim) for k0 in cosets(basis, dim)]
    covered = sorted(label for b in blocks for label in output_labels(b))
    full = pkm.output_contrast(
        pkm.ideal_law(pkm.kernel_map_circuit(operand, True, dim=dim)),
        pkm.ideal_law(pkm.kernel_map_circuit(operand, False, dim=dim)),
    )
    gap = 0.0
    for b in blocks:
        reduced = output_contrast(block_law(block_circuit(b, True)), block_law(block_circuit(b, False)))
        gap = max(gap, max(abs(full[label] - reduced[y]) for y, label in enumerate(output_labels(b))))
    return {
        "covers_once": covered == list(range(dim)),
        "aligned": [aligned_in_block(b) for b in blocks],
        "nullity": pkm.nullity(operand, dim=dim),
        "contrast_gap": gap,
    }


# The IBM coset-block campaign: every operand of pathion_kernel_map tiled by the four cosets of a 3-dimensional V.
COSET_MAP_CONTROLS: tuple[tuple[str, tuple[int, int, int]], ...] = (("xor", (1, 18, 1)), ("twin", (17, 2, -1)))


def default_basis(operand: tuple[int, int, int], dim: int = pkm.DIM) -> tuple[int, ...]:
    """m followed by the two lowest vectors that extend it to a 3-dimensional subspace."""
    i, j, _ = operand
    basis: list[int] = [i ^ j]
    for vector in range(1, dim):
        if len(basis) == 3:
            break
        if vector not in span(tuple(basis)):
            basis.append(vector)
    return tuple(basis)


def coset_map_members() -> tuple[Member, ...]:
    members: list[Member] = []

    def tiles(prefix: str, operand: tuple[int, int, int], cocycle_free: bool = False) -> None:
        basis = default_basis(operand)
        for k0 in cosets(basis):
            block = Block(f"k{k0}", operand, basis, k0)
            template = block_template(block, cocycle_free=cocycle_free)
            name = f"{prefix}_k{k0}"
            template.name = name
            for plus in (False, True):
                phase = np.pi if plus else 0.0
                ideal = block_law(template.assign_parameters({ORIENTATION: phase}))
                members.append(Member(f"{name}_{'plus' if plus else 'minus'}", template, ideal, {ORIENTATION: phase}))

    for operand in pkm.OPERANDS:
        tiles(f"cmap_{pkm.operand_tag(operand)}", operand)
    for kind, operand in COSET_MAP_CONTROLS:
        tiles(f"cmap_{kind}_{pkm.operand_tag(operand)}", operand, cocycle_free=kind == "xor")
    return tuple(members)


def pathion_coset_map_group() -> Group:
    members = coset_map_members()
    ideal = {member.name: member.ideal for member in members}
    blocks = sorted({member.name.rsplit("_", 1)[0] for member in members})
    operands = sorted({block.rsplit("_k", 1)[0] for block in blocks})

    def summarize(dist: dict[str, np.ndarray]) -> dict[str, float]:
        summary: dict[str, float] = {}
        for block in blocks:
            plus, minus = dist[f"{block}_plus"], dist[f"{block}_minus"]
            c_obs = output_contrast(plus, minus)
            c_ideal = output_contrast(ideal[f"{block}_plus"], ideal[f"{block}_minus"])
            decided = np.abs(c_ideal) > pkm.ZERO
            visibility = float(np.mean(c_obs[decided] * np.sign(c_ideal[decided]))) if decided.any() else float("nan")
            half_sum = float(c_obs.sum() / 2.0)
            summary[f"{block}_visibility"] = visibility
            summary[f"{block}_half_sum"] = half_sum
            summary[f"{block}_nullity_estimate"] = half_sum / visibility if abs(visibility) > pkm.ZERO else float("nan")
            summary[f"{block}_nullity_ideal"] = float(c_ideal.sum() / 2.0)
            summary[f"{block}_sign_agreement"] = float(np.sum(np.sign(c_obs[decided]) == np.sign(c_ideal[decided])))
        for operand in operands:
            parts = [b for b in blocks if b.rsplit("_k", 1)[0] == operand]
            summary[f"{operand}_nullity_estimate"] = float(sum(summary[f"{b}_nullity_estimate"] for b in parts))
            summary[f"{operand}_nullity_ideal"] = float(sum(summary[f"{b}_nullity_ideal"] for b in parts))
            summary[f"{operand}_visibility_mean"] = float(np.mean([summary[f"{b}_visibility"] for b in parts]))
            summary[f"{operand}_sign_agreement"] = float(sum(summary[f"{b}_sign_agreement"] for b in parts))
        summary["twin_nullity_difference"] = (
            summary["cmap_twin_e17me2_nullity_estimate"] - summary["cmap_e1pe18_nullity_estimate"]
        )
        return summary

    return Group("pathion_coset_map", members, summarize)
