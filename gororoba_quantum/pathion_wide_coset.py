"""Whole-operand nullity of two-term operands of the 64- and 128-dimensional Cayley-Dickson algebras on IBM Heron r2.

pathion_coset_block tiles the kernel map of e_i + t e_j into D / 8 four-qubit blocks, one per coset of a 3-dimensional
subspace V that contains m = i XOR j, for every power-of-two dimension D. The aligned XOR pairs of block b number N_b,
the blocks of one operand sum to its nullity, and the nullity is the rank defect of L_(e_i + t e_j) that cd_core
certifies (python-flint fmpz_mat rank). The group reads every block of six operands, each with both orientation arms:

* ``o64`` and ``o128`` are two-term operands of maximal nullity, 28 of 64 and 60 of 128, 8 and 16 blocks;
* ``n64`` and ``n128`` are null operands (nullity 0) of the same shape as e1 + e17 of A_5, the in-run control whose
  summed estimate reads the population offset of the estimator at 8 and 16 blocks;
* ``m64`` and ``m128`` tile the operands ``o64`` and ``o128`` with the cocycle-free SELECT (every L_m replaced by its
  unsigned XOR permutation), the mutation test: the ideal sum of N_b is -2 where the true tiling sums to 28 and 60.

Every member is one four-qubit circuit that compiles onto one layout, so each fused PUB reads one block arm on every
replica of the placement search, as in pathion_parallel_coset. Each block keeps its own ideal marginal; there is no
cross-block entanglement, and the blocks of an operand never share a shot. A shot reads one replica of one block arm
on each placement, so a PUB of S shots reads 16 or 17 copies of that block arm, and an operand's whole nullity is the
sum over its blocks of the per-block estimators. The estimator of pathion_parallel_coset (``estimate``) applies
unchanged: N_hat of a block is the half-sum of its output contrasts divided by their signed visibility, and the
readout-corrected summary of live_run applies it to readout-inverted replica laws.

The first member is the minus arm of block k0 of ``n64``; it fixes the placement and takes live_run's isolated
reference, the same circuit alone on replica 0, against which the packed replica is compared.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass

import numpy as np
from qiskit import QuantumCircuit

import pathion_coset_block as pcb
import pathion_kernel_map as pkm
from experiments import Group, Member
from pathion_parallel_coset import estimate
from select_lcu import joint_select_signs

ZERO = pkm.ZERO


@dataclass(frozen=True)
class WideOperand:
    """One operand e_i + t e_j of the algebra of dimension ``dim`` tiled by its coset blocks."""

    key: str
    role: str
    dim: int
    operand: tuple[int, int, int]
    cocycle_free: bool = False

    @property
    def basis(self) -> tuple[int, ...]:
        return pcb.default_basis(self.operand, self.dim)

    def blocks(self) -> list[pcb.Block]:
        return [pcb.Block(f"k{k0}", self.operand, self.basis, k0, self.dim) for k0 in pcb.cosets(self.basis, self.dim)]

    @property
    def nullity(self) -> int:
        """The rank defect of the true operand, from the cd_core integer rank; a mutated tiling keeps its operand's."""
        return certified_nullity(self.dim, self.operand)


# Order fixes the member order: the first member of the group is the minus arm of block k0 of n64.
WIDE_OPERANDS: tuple[WideOperand, ...] = (
    WideOperand("n64", "null", 64, (1, 33, 1)),
    WideOperand("o64", "target", 64, (1, 36, 1)),
    WideOperand("m64", "mutation", 64, (1, 36, 1), cocycle_free=True),
    WideOperand("n128", "null", 128, (1, 65, 1)),
    WideOperand("o128", "target", 128, (4, 72, 1)),
    WideOperand("m128", "mutation", 128, (4, 72, 1), cocycle_free=True),
)
BY_KEY = {op.key: op for op in WIDE_OPERANDS}


@functools.cache
def certified_nullity(dim: int, operand: tuple[int, int, int]) -> int:
    return pkm.nullity(operand, dim=dim)


def block_prefix(op: WideOperand, block: pcb.Block) -> str:
    return f"wide_{op.key}_{block.name}"


def wide_members() -> tuple[Member, ...]:
    members: list[Member] = []
    for op in WIDE_OPERANDS:
        for block in op.blocks():
            template = pcb.block_template(block, cocycle_free=op.cocycle_free)
            prefix = block_prefix(op, block)
            template.name = prefix
            for plus in (False, True):
                phase = np.pi if plus else 0.0
                ideal = pcb.block_law_closed_form(block, plus, cocycle_free=op.cocycle_free)
                members.append(
                    Member(f"{prefix}_{'plus' if plus else 'minus'}", template, ideal, {pcb.ORIENTATION: phase})
                )
    return tuple(members)


def summarize_operand(op: WideOperand, dist: dict[str, np.ndarray], ideal: dict[str, np.ndarray]) -> dict[str, float]:
    """Per-block and whole-operand values of one operand from the laws of its member names."""
    summary: dict[str, float] = {}
    n_hat = n_ideal = selector = agreement = 0.0
    visibilities: list[float] = []
    for block in op.blocks():
        prefix = block_prefix(op, block)
        plus, minus = dist[f"{prefix}_plus"], dist[f"{prefix}_minus"]
        ideal_plus, ideal_minus = ideal[f"{prefix}_plus"], ideal[f"{prefix}_minus"]
        est = estimate(plus, minus, ideal_plus, ideal_minus)
        c_obs = pcb.output_contrast(plus, minus)
        c_ideal = pcb.output_contrast(ideal_plus, ideal_minus)
        decided = np.abs(c_ideal) > ZERO
        block_ideal = float(c_ideal.sum() / 2.0)
        block_agreement = float(np.sum(np.sign(c_obs[decided]) == np.sign(c_ideal[decided])))
        block_selector = pcb.selector_contrast(plus, minus)
        summary[f"{prefix}_visibility"] = est["visibility"]
        summary[f"{prefix}_half_sum"] = est["half_sum"]
        summary[f"{prefix}_nullity_estimate"] = est["nullity_estimate"]
        summary[f"{prefix}_nullity_ideal"] = block_ideal
        summary[f"{prefix}_sign_agreement"] = block_agreement
        summary[f"{prefix}_selector_contrast"] = block_selector
        n_hat += est["nullity_estimate"]
        n_ideal += block_ideal
        selector += block_selector
        agreement += block_agreement
        visibilities.append(est["visibility"])
    tag = f"wide_{op.key}"
    summary[f"{tag}_nullity_estimate"] = n_hat
    summary[f"{tag}_nullity_ideal"] = n_ideal
    summary[f"{tag}_certified_nullity"] = float(op.nullity)
    summary[f"{tag}_selector_contrast_sum"] = selector
    summary[f"{tag}_sign_agreement"] = agreement
    summary[f"{tag}_bins"] = float(sum(1 << block.d for block in op.blocks()))
    summary[f"{tag}_visibility_mean"] = float(np.mean(visibilities))
    summary[f"{tag}_visibility_min"] = float(np.min(visibilities))
    return summary


def pathion_wide_coset_group() -> Group:
    members = wide_members()
    if len({member.name for member in members}) != len(members):
        raise ValueError("pathion_wide_coset: member names must be unique")
    ideal = {member.name: member.ideal for member in members}

    def summarize(dist: dict[str, np.ndarray]) -> dict[str, float]:
        summary: dict[str, float] = {}
        for op in WIDE_OPERANDS:
            summary |= summarize_operand(op, dist, ideal)
        for dim in (64, 128):
            target, null, mutation = (summary[f"wide_{role}{dim}_nullity_estimate"] for role in "onm")
            summary[f"wide_d{dim}_target_minus_null"] = target - null
            summary[f"wide_d{dim}_target_minus_mutation"] = target - mutation
        summary["wide_ratio_o128_over_o64_nullity_estimate"] = (
            summary["wide_o128_nullity_estimate"] / summary["wide_o64_nullity_estimate"]
            if abs(summary["wide_o64_nullity_estimate"]) > ZERO
            else float("nan")
        )
        return summary

    return Group("pathion_wide_coset", members, summarize)


def full_width_circuit(op: WideOperand, plus: bool, blocks: list[pcb.Block] | None = None) -> QuantumCircuit:
    """The operand's blocks side by side on disjoint four-qubit slices, block i on qubits and clbits 4i to 4i + 3.

    The blocks share no gate, so the circuit has no cross-block entanglement and each slice keeps its own ideal
    marginal. The campaign runs the slices one block per PUB; this circuit is the one-shot reading the simulations
    check (a matrix-product state of bond dimension at most 8 for any number of blocks)."""
    chosen = op.blocks() if blocks is None else blocks
    qc = QuantumCircuit(4 * len(chosen), 4 * len(chosen))
    for index, block in enumerate(chosen):
        window = range(4 * index, 4 * index + 4)
        qc.compose(
            pcb.block_circuit(block, plus, cocycle_free=op.cocycle_free), qubits=window, clbits=window, inplace=True
        )
    return qc


def block_marginals(counts: dict[str, int], blocks: int) -> list[np.ndarray]:
    """Per-block outcome laws (index y + 8 s) from full-width counts, clbit 4i + c carrying block i's clbit c."""
    totals = sum(counts.values())
    laws = [np.zeros(16) for _ in range(blocks)]
    for bits, count in counts.items():
        value = int(bits.replace(" ", ""), 2)
        for index in range(blocks):
            laws[index][(value >> (4 * index)) & 0xF] += count / totals
    return laws


def simulate_full_width(
    op: WideOperand, shots: int, seed: int, blocks: list[pcb.Block] | None = None
) -> dict[str, np.ndarray]:
    """Noise-free matrix-product-state samples of the full-width circuit, as laws under the group's member names."""
    from qiskit import transpile
    from qiskit_aer import AerSimulator

    chosen = op.blocks() if blocks is None else blocks
    simulator = AerSimulator(method="matrix_product_state")
    laws: dict[str, np.ndarray] = {}
    for plus in (False, True):
        circuit = transpile(full_width_circuit(op, plus, chosen), basis_gates=["cx", "u"], optimization_level=0)
        counts = simulator.run(circuit, shots=shots, seed_simulator=seed).result().get_counts()
        for block, law in zip(chosen, block_marginals(counts, len(chosen)), strict=True):
            laws[f"{block_prefix(op, block)}_{'plus' if plus else 'minus'}"] = law
    return laws


def _diagonal_terms(signs: list[float]) -> list[int]:
    """Nonzero monomials x >= 1 of the algebraic normal form over GF(2) of f, signs[x] = (-1)^f(x); bit q of x
    names qubit q."""
    n = len(signs).bit_length() - 1
    anf = [0 if sign > 0 else 1 for sign in signs]
    for bit in range(n):
        for x in range(1 << n):
            if x >> bit & 1:
                anf[x] ^= anf[x ^ (1 << bit)]
    return [x for x in range(1, 1 << n) if anf[x]]


def phase_degree(signs: list[float]) -> int:
    """Degree over GF(2) of the Boolean function f with signs[x] = (-1)^f(x)."""
    return max((term.bit_count() for term in _diagonal_terms(signs)), default=0)


def clifford_block_circuit(block: pcb.Block, plus: bool, *, cocycle_free: bool = False) -> QuantumCircuit | None:
    """The block circuit with each diagonal written as Z and CZ gates, or None when a diagonal has degree above 2.

    A +-1 diagonal is Clifford exactly when its sign function is quadratic over GF(2); such a block runs on a
    stabilizer simulator at any width. The circuit equals ``pcb.block_circuit`` up to a global phase."""
    i, j, t = block.operand
    d = block.d
    labels = pcb.input_labels(block)
    orientation = pkm.orientation_signs(block.operand, plus, dim=block.dim)
    signs = joint_select_signs(block.dim, i, j)
    f0 = np.array([signs[k] for k in labels])
    f1 = np.array([signs[k + block.dim] for k in labels]) * (-1.0 if t < 0 else 1.0)
    if cocycle_free:
        f0, f1 = np.ones(1 << d), np.full(1 << d, -1.0 if t < 0 else 1.0)
    first = list(np.array([orientation[k] for k in labels]) * f0)
    second = [1.0] * (1 << d) + list(f0 * f1)
    if phase_degree(first) > 2 or phase_degree(second) > 2:
        return None
    qc = QuantumCircuit(d + 1, d + 1)
    qc.h(range(d))
    for diagonal in (first, second):
        if diagonal is second:
            qc.h(d)
        for term in _diagonal_terms(diagonal):
            qubits = [q for q in range(d + 1) if term >> q & 1]
            if len(qubits) == 1:
                qc.z(qubits[0])
            else:
                qc.cz(*qubits)
    qc.cx(d, 0)
    qc.h(d)
    qc.measure(range(d + 1), range(d + 1))
    return qc


if __name__ == "__main__":
    group = pathion_wide_coset_group()
    out = group.summarize({member.name: member.ideal for member in group.members})
    print(
        f"pathion wide coset: {len(group.members)} members;",
        {k: round(v, 6) for k, v in out.items() if k.startswith("wide_") and k.count("_k") == 0},
    )
