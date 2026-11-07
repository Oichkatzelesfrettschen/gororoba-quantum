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

One fused PUB carries one arm of one operand, and its placements run different blocks: placement p of a
``PLACEMENTS``-placement layout holds block p mod (the operand's block count) of every operand, so a 128-dimensional
operand's 16 blocks fill the 16 placements at once and a 64-dimensional operand's 8 blocks run twice. The blocks of an
operand are four-qubit circuits that share no gate, so there is no cross-block entanglement and each placement keeps
the ideal marginal of its own block (``Group.per_placement_laws``). The plus and minus arms of block b sit on the same
placement in their two PUBs, so the contrast of a placement pairs its own arms, and block b of an operand, of its null
control and of its mutation share one placement. The estimator of pathion_parallel_coset (``estimate``) applies to
each placement's block: N_hat of a block is the half-sum of its output contrasts divided by their signed visibility.
The whole-operand nullity is the sum over the blocks of one shot, which the pooled mean over placements gives when each
placement scales its contribution by the operand's block count (``placed_summary``).

``pathion_wide_coset_d32`` adds placement 16 for an ibm_fez layout of 17: its bodies are the two arms of block k0 of the
32-dimensional null operand e1 + e17 of the drain case, read in all twelve PUBs at the same time as the wide blocks.

The first member is the minus arm of ``n64``; its first body, block k0 of ``n64``, fixes the placement and takes
live_run's isolated reference, the same circuit alone on replica 0, against which the packed replica is compared.
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
# Placements that carry operand blocks: the largest block count of an operand, so one PUB reads a whole operand.
PLACEMENTS = 16
# The 32-dimensional reference block of pathion_wide_coset_d32: block k0 of the null operand e1 + e17 of the drain case.
REFERENCE_OPERAND = (1, 17, 1)
REFERENCE_TAG = "wide_ref32"


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

    def block_at(self, placement: int) -> pcb.Block:
        """The block that placement runs: blocks repeat in order when the operand has fewer than PLACEMENTS."""
        blocks = self.blocks()
        if not 0 <= placement < PLACEMENTS:
            raise ValueError(f"{self.key}: placement {placement} carries no operand block")
        return blocks[placement % len(blocks)]

    @property
    def nullity(self) -> int:
        """The rank defect of the true operand, from the cd_core integer rank; a mutated tiling keeps its operand's."""
        return certified_nullity(self.dim, self.operand)


# Order fixes the member order: the first member of the group is the minus arm of n64.
WIDE_OPERANDS: tuple[WideOperand, ...] = (
    WideOperand("n64", "null", 64, (1, 33, 1)),
    WideOperand("o64", "target", 64, (1, 36, 1)),
    WideOperand("m64", "mutation", 64, (1, 36, 1), cocycle_free=True),
    WideOperand("n128", "null", 128, (1, 65, 1)),
    WideOperand("o128", "target", 128, (4, 72, 1)),
    WideOperand("m128", "mutation", 128, (4, 72, 1), cocycle_free=True),
)
BY_KEY = {op.key: op for op in WIDE_OPERANDS}
ARMS = ("minus", "plus")


@functools.cache
def certified_nullity(dim: int, operand: tuple[int, int, int]) -> int:
    return pkm.nullity(operand, dim=dim)


def block_prefix(op: WideOperand, block: pcb.Block) -> str:
    return f"wide_{op.key}_{block.name}"


def member_name(op: WideOperand, arm: str) -> str:
    return f"wide_{op.key}_{arm}"


def reference_block() -> pcb.Block:
    basis = pcb.default_basis(REFERENCE_OPERAND)
    return pcb.Block("k0", REFERENCE_OPERAND, basis, 0)


def _arm_binding(arm: str) -> dict:
    return {pcb.ORIENTATION: np.pi if arm == "plus" else 0.0}


@dataclass(frozen=True)
class _Body:
    """One block arm: the body name, its template, its ideal law and its orientation binding."""

    name: str
    template: QuantumCircuit
    ideal: np.ndarray
    binding: dict


def _bodies(block: pcb.Block, prefix: str, cocycle_free: bool) -> dict[str, _Body]:
    template = pcb.block_template(block, cocycle_free=cocycle_free)
    template.name = prefix
    return {
        arm: _Body(
            f"{prefix}_{arm}",
            template,
            pcb.block_law_closed_form(block, arm == "plus", cocycle_free=cocycle_free),
            _arm_binding(arm),
        )
        for arm in ARMS
    }


def wide_layout(reference: bool = False) -> tuple[dict[str, list[_Body]], list[str]]:
    """The body of each member at each placement, by member name, and the member names in group order."""
    chosen: dict[str, list[_Body]] = {member_name(op, arm): [] for op in WIDE_OPERANDS for arm in ARMS}
    cache: dict[str, dict[str, _Body]] = {}
    for op in WIDE_OPERANDS:
        for placement in range(PLACEMENTS):
            block = op.block_at(placement)
            prefix = block_prefix(op, block)
            if prefix not in cache:
                cache[prefix] = _bodies(block, prefix, op.cocycle_free)
            for arm in ARMS:
                chosen[member_name(op, arm)].append(cache[prefix][arm])
    if reference:
        ref = _bodies(reference_block(), f"{REFERENCE_TAG}_k0", False)
        for op in WIDE_OPERANDS:
            for arm in ARMS:
                chosen[member_name(op, arm)].append(ref[arm])
    return chosen, list(chosen)


def wide_members(
    reference: bool = False, layout: tuple[dict[str, list[_Body]], list[str]] | None = None
) -> tuple[Member, ...]:
    """One member per operand arm; its replica bodies are that arm's block at each placement.

    The member's circuit is its first body's template, the same object the group's body templates hold, so a caller
    that builds both passes one layout."""
    chosen, names = wide_layout(reference) if layout is None else layout
    return tuple(
        Member(
            name,
            chosen[name][0].template,
            chosen[name][0].ideal,
            chosen[name][0].binding,
            replica_bodies=tuple(body.name for body in chosen[name]),
        )
        for name in names
    )


def block_values(
    plus: np.ndarray, minus: np.ndarray, ideal_plus: np.ndarray, ideal_minus: np.ndarray
) -> dict[str, float]:
    """The per-block quantities of one placement: estimate, ideal, signs, visibility, selector contrast."""
    est = estimate(plus, minus, ideal_plus, ideal_minus)
    c_obs = pcb.output_contrast(plus, minus)
    c_ideal = pcb.output_contrast(ideal_plus, ideal_minus)
    decided = np.abs(c_ideal) > ZERO
    return {
        "visibility": est["visibility"],
        "half_sum": est["half_sum"],
        "nullity_estimate": est["nullity_estimate"],
        "nullity_ideal": float(c_ideal.sum() / 2.0),
        "sign_agreement": float(np.sum(np.sign(c_obs[decided]) == np.sign(c_ideal[decided]))),
        "selector_contrast": pcb.selector_contrast(plus, minus),
    }


def placed_operand_values(
    op: WideOperand, placement: int, dist: dict[str, np.ndarray], ideal: dict[str, np.ndarray]
) -> dict[str, float]:
    """The values one placement reports for one operand: its own block's, and the operand sum's contribution.

    The block's quantities carry the block's name. The operand-level keys are that block's quantity times the
    operand's block count, so their mean over the placements, in which each block appears equally often, is the sum
    over the operand's blocks (the mean over copies for a 64-dimensional operand that runs twice)."""
    block = op.block_at(placement)
    prefix = block_prefix(op, block)
    plus, minus = member_name(op, "plus"), member_name(op, "minus")
    values = block_values(dist[plus], dist[minus], ideal[plus], ideal[minus])
    count = len(op.blocks())
    summary = {f"{prefix}_{key}": value for key, value in values.items()}
    tag = f"wide_{op.key}"
    summary[f"{tag}_nullity_estimate"] = values["nullity_estimate"] * count
    summary[f"{tag}_nullity_ideal"] = values["nullity_ideal"] * count
    summary[f"{tag}_certified_nullity"] = float(op.nullity)
    summary[f"{tag}_selector_contrast_sum"] = values["selector_contrast"] * count
    summary[f"{tag}_sign_agreement"] = values["sign_agreement"] * count
    summary[f"{tag}_bins"] = float(sum(1 << b.d for b in op.blocks()))
    summary[f"{tag}_visibility_mean"] = values["visibility"]
    return summary


def placed_reference_values(dist: dict[str, np.ndarray], ideal: dict[str, np.ndarray]) -> dict[str, float]:
    """The 32-dimensional reference block's values at the reference placement, once per operand's PUB pair.

    Each operand's two PUBs carry the same reference block on that placement, so the six pairs read it at six
    moments of the job; the keys name the operand whose PUBs read it."""
    summary: dict[str, float] = {}
    for op in WIDE_OPERANDS:
        plus, minus = member_name(op, "plus"), member_name(op, "minus")
        values = block_values(dist[plus], dist[minus], ideal[plus], ideal[minus])
        summary |= {f"{REFERENCE_TAG}_{op.key}_{key}": value for key, value in values.items()}
    return summary


def operand_sum(op: WideOperand, dist: dict[str, np.ndarray], ideal: dict[str, np.ndarray]) -> dict[str, float]:
    """The whole-operand values of one shot: the blocks' quantities summed, from laws under their body names.

    A shot that reads every block of the operand at once (the side-by-side circuit, or one PUB's placements) gives
    the nullity as the sum of the block estimates."""
    n_hat = n_ideal = selector = agreement = 0.0
    visibilities: list[float] = []
    for block in op.blocks():
        prefix = block_prefix(op, block)
        values = block_values(
            dist[f"{prefix}_plus"], dist[f"{prefix}_minus"], ideal[f"{prefix}_plus"], ideal[f"{prefix}_minus"]
        )
        n_hat += values["nullity_estimate"]
        n_ideal += values["nullity_ideal"]
        selector += values["selector_contrast"]
        agreement += values["sign_agreement"]
        visibilities.append(values["visibility"])
    tag = f"wide_{op.key}"
    return {
        f"{tag}_nullity_estimate": n_hat,
        f"{tag}_nullity_ideal": n_ideal,
        f"{tag}_certified_nullity": float(op.nullity),
        f"{tag}_selector_contrast_sum": selector,
        f"{tag}_sign_agreement": agreement,
        f"{tag}_bins": float(sum(1 << block.d for block in op.blocks())),
        f"{tag}_visibility_mean": float(np.mean(visibilities)),
        f"{tag}_visibility_min": float(np.min(visibilities)),
    }


def pathion_wide_coset_group(reference: bool = False) -> Group:
    """The wide group of PLACEMENTS operand placements, or of PLACEMENTS + 1 with the 32-dimensional reference block."""
    layout = wide_layout(reference)
    chosen, names = layout
    members = wide_members(reference, layout)
    if len({member.name for member in members}) != len(members):
        raise ValueError("pathion_wide_coset: member names must be unique")
    templates: list[tuple[str, QuantumCircuit, np.ndarray]] = []
    bindings: list[tuple[str, dict]] = []
    seen: set[str] = set()
    for name in names:
        for body in chosen[name]:
            if body.name not in seen:
                seen.add(body.name)
                templates.append((body.name, body.template, body.ideal))
                bindings.append((body.name, body.binding))
    first = {member.name: member.ideal for member in members}

    def placed(placement: int, dist: dict[str, np.ndarray], ideal: dict[str, np.ndarray]) -> dict[str, float]:
        if placement >= PLACEMENTS:
            return placed_reference_values(dist, ideal)
        summary: dict[str, float] = {}
        for op in WIDE_OPERANDS:
            summary |= placed_operand_values(op, placement, dist, ideal)
        for dim in (64, 128):
            target, null, mutation = (summary[f"wide_{role}{dim}_nullity_estimate"] for role in "onm")
            summary[f"wide_d{dim}_target_minus_null"] = target - null
            summary[f"wide_d{dim}_target_minus_mutation"] = target - mutation
        return summary

    return Group(
        "pathion_wide_coset_d32" if reference else "pathion_wide_coset",
        members,
        lambda dist: placed(0, dist, first),
        body_templates=tuple(templates),
        body_bindings=tuple(bindings),
        per_placement_laws=True,
        placed_summary=placed,
    )


def pathion_wide_coset_d32_group() -> Group:
    return pathion_wide_coset_group(reference=True)


def placed_ideal_summary(group: Group) -> dict[str, float]:
    """The pooled summary of the ideal laws: each key's mean over the placements that report it."""
    if group.placed_summary is None:
        raise ValueError(f"{group.name} has no placed summary")
    bodies = {member.name: member.replica_bodies or () for member in group.members}
    ideals = {name: ideal for name, _, ideal in group.body_templates}
    count = len(next(iter(bodies.values())))
    per_placement = [
        group.placed_summary(
            k, {n: ideals[b[k]] for n, b in bodies.items()}, {n: ideals[b[k]] for n, b in bodies.items()}
        )
        for k in range(count)
    ]
    keys = list(dict.fromkeys(key for row in per_placement for key in row))
    return {key: float(np.mean([row[key] for row in per_placement if key in row])) for key in keys}


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
    out = placed_ideal_summary(group)
    print(
        f"pathion wide coset: {len(group.members)} members;",
        {k: round(v, 6) for k, v in out.items() if k.startswith("wide_") and k.count("_k") == 0},
    )
