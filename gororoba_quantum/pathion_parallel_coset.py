"""Wide parallel coset-block campaign on IBM Heron r2: the retained coset map, readout-flip twins, within-arm repeats
and four-term blocks, one fused PUB per circuit over every placement the replica search admits.

The group extends pathion_coset_map (pathion_coset_block) with three control families and one new object, all
four-qubit circuits that compile onto one layout, so each fused PUB reads one block (or arm) on every replica at once.

``cflip`` twins carry X on every qubit just before the measurement. The ideal law of a twin is the base law with every
outcome index complemented, and the summary complements the observed distribution back before it applies the base
estimator. A population bias that acts after the X, the asymmetry of the readout channel, changes sign under the flip,
so half the difference of the base and twin half-sums (the odd part) holds it. Everything that acts before the X reaches
the complemented twin exactly as it reaches the base, so half their sum (the even part) holds relaxation during the
gates, state-preparation excitation, a compile-dependent coherent error and crosstalk.

``crep`` repeats run a block's two arms a second time on the same template and binding. The group lists them in mirror
order, so the arms of the null block read +, -, ..., -, + in the member list. Within one arm the repeat difference has
ideal zero in every bin and sees an identical coherent-error frame in both copies (no virtual Z separates them), so
its half-sum measures the contrast estimator's response to position, drift and sampling alone; the arm contrast pairs
the two copies of each arm.

The first member is the null block's minus arm: it fixes the placement and takes live_run's isolated reference, the
same circuit alone on replica 0, against which the packed replica is compared (crosstalk at the full replica density).

Four-term blocks come from pathion_four_term_block.
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit

import pathion_coset_block as pcb
import pathion_four_term_block as pft
import pathion_kernel_map as pkm
from experiments import Group, Member

# Operands whose four cosets gain a readout-flip twin and a within-arm repeat: the null operand, whose positive
# nullity estimate is the open question, and the nullity-12 operand, whose blocks all have aligned pairs.
CONTROL_OPERANDS: tuple[tuple[int, int, int], ...] = ((1, 17, 1), (1, 18, 1))
FLIP_MASK = 0b1111
ZERO = pkm.ZERO


def block_prefix(operand: tuple[int, int, int], k0: int) -> str:
    return f"cmap_{pkm.operand_tag(operand)}_k{k0}"


def control_blocks() -> list[tuple[tuple[int, int, int], int, pcb.Block]]:
    """(operand, coset, block) for every coset of every control operand, in the retained map's order."""
    out = []
    for operand in CONTROL_OPERANDS:
        basis = pcb.default_basis(operand)
        for k0 in pcb.cosets(basis):
            out.append((operand, k0, pcb.Block(f"k{k0}", operand, basis, k0)))
    return out


def flipped_template(block: pcb.Block) -> QuantumCircuit:
    """The block circuit with X on all four qubits ahead of the measurement."""
    base = pcb.block_template(block, measure=False)
    qc = QuantumCircuit(base.num_qubits, base.num_qubits)
    qc.compose(base, range(base.num_qubits), inplace=True)
    qc.x(range(base.num_qubits))
    qc.measure(range(base.num_qubits), range(base.num_qubits))
    return qc


def deflip(distribution: np.ndarray) -> np.ndarray:
    """The distribution with every outcome index complemented."""
    return np.asarray(distribution)[np.arange(distribution.size) ^ FLIP_MASK]


def apply_readout_clbit(distribution: np.ndarray, clbit: int, e01: float, e10: float) -> np.ndarray:
    """The law after clbit reads 1 with probability e01 when prepared 0 and 0 with probability e10 when prepared 1."""
    qubits = distribution.size.bit_length() - 1
    axis = qubits - 1 - clbit
    confusion = np.array([[1.0 - e01, e10], [e01, 1.0 - e10]])
    tensor = np.asarray(distribution, dtype=float).reshape((2,) * qubits)
    return np.moveaxis(np.tensordot(confusion, tensor, axes=([1], [axis])), 0, axis).reshape(-1)


def apply_readout(distribution: np.ndarray, e01: float, e10: float) -> np.ndarray:
    """The law after every measured qubit takes one asymmetric channel, the readout asymmetry the twins test."""
    out = np.asarray(distribution, dtype=float)
    for clbit in range(distribution.size.bit_length() - 1):
        out = apply_readout_clbit(out, clbit, e01, e10)
    return out


def contract(distribution: np.ndarray, visibility: float) -> np.ndarray:
    """The law contracted toward uniform, the symmetric depolarizing response of the routed circuit."""
    return visibility * np.asarray(distribution) + (1.0 - visibility) / distribution.size


def invert_readout(distribution: np.ndarray, e01: list[float], e10: list[float]) -> np.ndarray:
    """The law with each clbit's asymmetric confusion matrix inverted, e01[i] and e10[i] belonging to clbit i.

    A placement's readout correction takes the calibration of the physical qubits that carry its clbits, so the
    corrected N_hat of every placement follows from its own two lists; the result is a quasi-probability vector."""
    qubits = distribution.size.bit_length() - 1
    tensor = np.asarray(distribution, dtype=float).reshape((2,) * qubits)
    for clbit in range(qubits):
        axis = qubits - 1 - clbit
        inverse = np.linalg.inv(np.array([[1.0 - e01[clbit], e10[clbit]], [e01[clbit], 1.0 - e10[clbit]]]))
        tensor = np.moveaxis(np.tensordot(inverse, tensor, axes=([1], [axis])), 0, axis)
    return tensor.reshape(-1)


def estimate(plus: np.ndarray, minus: np.ndarray, ideal_plus: np.ndarray, ideal_minus: np.ndarray) -> dict[str, float]:
    """The per-block estimator of pathion_coset_map: signed visibility, half-sum of c(y) and their ratio."""
    c_obs = pcb.output_contrast(plus, minus)
    c_ideal = pcb.output_contrast(ideal_plus, ideal_minus)
    decided = np.abs(c_ideal) > ZERO
    visibility = float(np.mean(c_obs[decided] * np.sign(c_ideal[decided]))) if decided.any() else float("nan")
    half_sum = float(c_obs.sum() / 2.0)
    return {
        "visibility": visibility,
        "half_sum": half_sum,
        "nullity_estimate": half_sum / visibility if abs(visibility) > ZERO else float("nan"),
    }


def within_arm_half_sum(first: np.ndarray, second: np.ndarray) -> float:
    """Half the sum over output bins of P_first(s = 0 | y) - P_second(s = 0 | y) for two copies of one arm."""
    half = first.size // 2

    def conditional(law: np.ndarray) -> np.ndarray:
        total = law[:half] + law[half:]
        return np.divide(law[:half], total, out=np.zeros(half), where=total > ZERO)

    return float((conditional(first) - conditional(second)).sum() / 2.0)


def parallel_members() -> tuple[Member, ...]:
    """Retained coset map, four-term blocks, flip twins and mirrored repeats, in that member order."""
    retained = pcb.coset_map_members()
    members: list[Member] = list(retained)
    members.extend(pft.four_term_members())
    by_name = {member.name: member for member in retained}
    controls = control_blocks()
    for operand, k0, block in controls:
        prefix = block_prefix(operand, k0)
        template = flipped_template(block)
        template.name = prefix.replace("cmap_", "cflip_", 1)
        for plus in (False, True):
            phase = np.pi if plus else 0.0
            ideal = pcb.block_law(template.assign_parameters({pcb.ORIENTATION: phase}))
            arm = "plus" if plus else "minus"
            members.append(Member(f"{template.name}_{arm}", template, ideal, {pcb.ORIENTATION: phase}))
    repeats: list[Member] = []
    for operand, k0, _block in controls:
        prefix = block_prefix(operand, k0)
        for arm in ("minus", "plus"):
            source = by_name[f"{prefix}_{arm}"]
            repeats.append(
                Member(f"{prefix.replace('cmap_', 'crep_', 1)}_{arm}", source.circuit, source.ideal, source.binding)
            )
    members.extend(reversed(repeats))
    return tuple(members)


def pathion_parallel_coset_group() -> Group:
    members = parallel_members()
    names = {member.name for member in members}
    if len(names) != len(members):
        raise ValueError("pathion_parallel_coset: member names must be unique")
    ideal = {member.name: member.ideal for member in members}
    retained_group = pcb.pathion_coset_map_group()
    four_term = pft.four_term_group()
    controls = control_blocks()

    def summarize(dist: dict[str, np.ndarray]) -> dict[str, float]:
        summary = dict(retained_group.summarize({k: v for k, v in dist.items() if k.startswith("cmap_")}))
        summary |= four_term.summarize({k: v for k, v in dist.items() if k.startswith("ftb_")})
        for name in dist:
            if name.startswith("cmap_") and name.endswith("_minus") and f"{name[:-6]}_plus" in dist:
                summary[f"{name[:-6]}_selector_contrast"] = pcb.selector_contrast(dist[f"{name[:-6]}_plus"], dist[name])
        per_operand: dict[str, dict[str, float]] = {}
        for operand, k0, _block in controls:
            prefix = block_prefix(operand, k0)
            flip_prefix = prefix.replace("cmap_", "cflip_", 1)
            rep_prefix = prefix.replace("cmap_", "crep_", 1)
            tag = pkm.operand_tag(operand)
            base = estimate(
                dist[f"{prefix}_plus"], dist[f"{prefix}_minus"], ideal[f"{prefix}_plus"], ideal[f"{prefix}_minus"]
            )
            flip = estimate(
                deflip(dist[f"{flip_prefix}_plus"]),
                deflip(dist[f"{flip_prefix}_minus"]),
                deflip(ideal[f"{flip_prefix}_plus"]),
                deflip(ideal[f"{flip_prefix}_minus"]),
            )
            plus_pool = 0.5 * (dist[f"{prefix}_plus"] + dist[f"{rep_prefix}_plus"])
            minus_pool = 0.5 * (dist[f"{prefix}_minus"] + dist[f"{rep_prefix}_minus"])
            quad = estimate(plus_pool, minus_pool, ideal[f"{prefix}_plus"], ideal[f"{prefix}_minus"])
            repeat = estimate(
                dist[f"{rep_prefix}_plus"],
                dist[f"{rep_prefix}_minus"],
                ideal[f"{prefix}_plus"],
                ideal[f"{prefix}_minus"],
            )
            values = {
                "flip_selector_contrast": pcb.selector_contrast(
                    deflip(dist[f"{flip_prefix}_plus"]), deflip(dist[f"{flip_prefix}_minus"])
                ),
                "flip_visibility": flip["visibility"],
                "flip_half_sum": flip["half_sum"],
                "flip_nullity_estimate": flip["nullity_estimate"],
                "odd_half_sum": 0.5 * (base["half_sum"] - flip["half_sum"]),
                "even_half_sum": 0.5 * (base["half_sum"] + flip["half_sum"]),
                "odd_nullity": 0.5 * (base["nullity_estimate"] - flip["nullity_estimate"]),
                "even_nullity": 0.5 * (base["nullity_estimate"] + flip["nullity_estimate"]),
                "repeat_nullity_estimate": repeat["nullity_estimate"],
                "repeat_half_sum": repeat["half_sum"],
                "quad_half_sum": quad["half_sum"],
                "quad_nullity_estimate": quad["nullity_estimate"],
                "pair_half_sum_gap": base["half_sum"] - repeat["half_sum"],
                "within_minus_half_sum": within_arm_half_sum(dist[f"{prefix}_minus"], dist[f"{rep_prefix}_minus"]),
                "within_plus_half_sum": within_arm_half_sum(dist[f"{prefix}_plus"], dist[f"{rep_prefix}_plus"]),
            }
            for key, value in values.items():
                summary[f"{prefix}_{key}"] = value
                if "visibility" in key:
                    continue
                per_operand.setdefault(tag, {}).setdefault(key, 0.0)
                per_operand[tag][key] += value
        for tag, sums in per_operand.items():
            for key, value in sums.items():
                summary[f"cmap_{tag}_{key}"] = value
        return summary

    return Group("pathion_parallel_coset", members, summarize)


if __name__ == "__main__":
    group = pathion_parallel_coset_group()
    ideal = {member.name: member.ideal for member in group.members}
    out = group.summarize(ideal)
    print(
        f"pathion parallel coset: {len(group.members)} members;",
        {k: round(v, 6) for k, v in out.items() if k.startswith("cmap_e1pe17_") and k.count("_k") == 0},
    )
