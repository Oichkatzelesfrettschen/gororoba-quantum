"""Pair-resolved kernel map of two-term operands of the 32-dimensional Cayley-Dickson algebra A_5.

For the operand e_i + t e_j, write L for its left multiplication, m = i XOR j and
K = L_i^T (t L_j), a signed permutation k -> k XOR m that pairs the 32 basis
states into 16 XOR pairs {k, k XOR m}. A pair is aligned when K carries the same
sign on both members. On an aligned pair e_k - s e_(k XOR m) spans a kernel
direction of L (Gram eigenvalue 0) and e_k + s e_(k XOR m) a Gram eigenvalue 4;
on a misaligned pair both combinations sit at eigenvalue 2. The nullity of L is
the number N of aligned pairs, 0, 4, 8 or 12 for two-term operands (the classes
of Biss, Dugger and Isaksen, math/0511691, Theorem 14.6; Skiouris, Aphanics at
the Pathion Level, Proposition 2.2), checked by ``nullity`` against the cd_core
matrix rank.

Circuit, six qubits (algebra index bit b on qubit b, selector on qubit 5):
H on every data qubit, a diagonal orientation oracle, then the fixed-operand
linear combination of unitaries (H on the selector, Z on it for t = -1,
select_lcu.select_circuit(32, i, j), H on the selector), and a measurement of
all six qubits. The oracle is +1 on the lower member k of every pair and -s_k
(arm ``minus``) or +s_k (arm ``plus``) on the upper member, with s_k the sign K
puts on k, so the upper-member signs enter only through the compiled SELECT.
The ideal selector marginals are P(s = 0) = (16 - N)/32 and (16 + N)/32, so the
selector contrast plus - minus is N/16, and the per-output contrast
c(y) = P_plus(s = 0 | y) - P_minus(s = 0 | y) is +1 at both outputs of an aligned
pair and +1 at one, -1 at the other output of a misaligned pair; half the sum of
c(y) is N. A device whose error contracts every outcome toward a fixed state
scales both contrasts by one visibility, so the ratio of selector contrasts
between operands equals the ratio of their nullities.

Controls: the N = 0 operand (ideal contrast 0); the quarter-turn twins, operands
with disjoint support and the same Gram operator as a primary operand (Moreno,
math/0512517, Corollary 2.4), which read the primary's values through a
different compiled sign network; the cocycle-free SELECT (every L_m replaced by
its unsigned XOR permutation), whose contrast departs from N/16; a single SELECT
sign flipped at one input, which moves N by one; and the selector-disconnected
skeleton, whose selector reads s = 0 with certainty.
"""

from __future__ import annotations

import flint
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import DiagonalGate
from qiskit.quantum_info import Statevector

import cd_core
from experiments import Group, Member
from select_lcu import select_circuit

DIM = 32
DATA = 5
WIDTH = DATA + 1
# (i, j, t) names the operand e_i + t e_j; nullities 0, 4, 4, 8, 12, 12. e2 + e27 and e1 + e24 share the strut
# constant 9 with nullities 4 and 12; e1 + e10 lies in the sedenions.
OPERANDS: tuple[tuple[int, int, int], ...] = ((1, 17, 1), (1, 26, 1), (2, 27, 1), (1, 10, 1), (1, 18, 1), (1, 24, 1))
# Quarter-turn twins: e17 - e10 has the Gram operator of e1 + e26, and e17 - e2 that of e1 + e18.
TWINS: tuple[tuple[tuple[int, int, int], tuple[int, int, int]], ...] = (
    ((17, 10, -1), (1, 26, 1)),
    ((17, 2, -1), (1, 18, 1)),
)
COCYCLE_FREE: tuple[tuple[int, int, int], ...] = ((1, 10, 1), (1, 18, 1))
# One SELECT sign negated at (selector 1, data input FLIP_INPUT) of this operand.
FLIP_OPERAND, FLIP_INPUT = (1, 18, 1), 3
SKELETON_OPERAND = (1, 18, 1)
# Ideal contrasts are multiples of 1/32; a Statevector value below this is zero.
ZERO = 1e-9


def operand_tag(operand: tuple[int, int, int]) -> str:
    i, j, t = operand
    return f"e{i}{'p' if t > 0 else 'm'}e{j}"


def _left(m: int) -> np.ndarray:
    return np.array(cd_core.left_mult_matrix(DIM, cd_core.basis(DIM, m)))


def nullity(operand: tuple[int, int, int]) -> int:
    """Exact nullity of L_(e_i + t e_j) from the integer rank of its cd_core matrix (python-flint fmpz_mat)."""
    i, j, t = operand
    matrix = (_left(i) + t * _left(j)).astype(int).tolist()
    return DIM - int(flint.fmpz_mat(matrix).rank())


def aligned_pairs(operand: tuple[int, int, int]) -> int:
    i, j, t = operand
    k_matrix = _left(i).T @ (t * _left(j))
    m = i ^ j
    return sum(1 for k in range(DIM) if k < k ^ m and k_matrix[k ^ m, k] == k_matrix[k, k ^ m])


def orientation_signs(operand: tuple[int, int, int], plus: bool) -> list[float]:
    i, j, t = operand
    k_matrix = _left(i).T @ (t * _left(j))
    m = i ^ j
    signs = [1.0] * DIM
    for k in range(DIM):
        if k < k ^ m:
            s_k = float(k_matrix[k ^ m, k])
            signs[k ^ m] = s_k if plus else -s_k
    return signs


def _cocycle_free_select(i: int, j: int) -> QuantumCircuit:
    qc = QuantumCircuit(WIDTH, name=f"xor_select_{i}_{j}")
    for b in range(DATA):
        if i >> b & 1:
            qc.x(b)
    for b in range(DATA):
        if (i ^ j) >> b & 1:
            qc.cx(DATA, b)
    return qc


def kernel_map_circuit(
    operand: tuple[int, int, int],
    plus: bool,
    *,
    oracle_operand: tuple[int, int, int] | None = None,
    cocycle_free: bool = False,
    flip_input: int | None = None,
    skeleton: bool = False,
    measure: bool = True,
) -> QuantumCircuit:
    i, j, t = operand
    qc = QuantumCircuit(WIDTH, WIDTH if measure else 0)
    qc.h(range(DATA))
    qc.append(DiagonalGate(orientation_signs(oracle_operand or operand, plus)), range(DATA))
    qc.h(DATA)
    if not skeleton:
        if t < 0:
            qc.z(DATA)
        if flip_input is not None:
            flips = [1.0] * (2 * DIM)
            flips[DIM + flip_input] = -1.0
            qc.append(DiagonalGate(flips), range(WIDTH))
        qc.compose(
            _cocycle_free_select(i, j) if cocycle_free else select_circuit(DIM, i, j), range(WIDTH), inplace=True
        )
    qc.h(DATA)
    if measure:
        qc.measure(range(WIDTH), range(WIDTH))
    return qc


def ideal_law(circuit: QuantumCircuit) -> np.ndarray:
    """Outcome law indexed y + 32 s (data clbits 0-4, selector clbit 5)."""
    return np.asarray(Statevector(circuit.remove_final_measurements(inplace=False)).probabilities())


def selector_zero(law: np.ndarray) -> float:
    return float(law[:DIM].sum())


def output_contrast(plus_law: np.ndarray, minus_law: np.ndarray) -> np.ndarray:
    """c(y) = P_plus(s = 0 | y) - P_minus(s = 0 | y); an output with no weight in an arm reads 0."""

    def conditional(law: np.ndarray) -> np.ndarray:
        total = law[:DIM] + law[DIM:]
        return np.divide(law[:DIM], total, out=np.zeros(DIM), where=total > 0)

    return conditional(plus_law) - conditional(minus_law)


def kernel_map_members() -> tuple[Member, ...]:
    members: list[Member] = []

    def arms(prefix: str, operand: tuple[int, int, int], **options: object) -> None:
        for plus in (False, True):
            circuit = kernel_map_circuit(operand, plus, **options)  # type: ignore[arg-type]
            name = f"{prefix}_{'plus' if plus else 'minus'}"
            circuit.name = name
            members.append(Member(name, circuit, ideal_law(circuit)))

    for operand in OPERANDS:
        arms(f"kmap_{operand_tag(operand)}", operand)
    for twin, _primary in TWINS:
        arms(f"kmap_twin_{operand_tag(twin)}", twin)
    for operand in COCYCLE_FREE:
        arms(f"kmap_xor_{operand_tag(operand)}", operand, cocycle_free=True)
    arms(f"kmap_flip{FLIP_INPUT}_{operand_tag(FLIP_OPERAND)}", FLIP_OPERAND, flip_input=FLIP_INPUT)
    skeleton = kernel_map_circuit(SKELETON_OPERAND, False, skeleton=True)
    skeleton.name = "kmap_skeleton"
    members.append(Member("kmap_skeleton", skeleton, ideal_law(skeleton)))
    return tuple(members)


def _pair_summary(prefix: str, dist: dict[str, np.ndarray], ideal: dict[str, np.ndarray]) -> dict[str, float]:
    plus, minus = dist[f"{prefix}_plus"], dist[f"{prefix}_minus"]
    contrast = selector_zero(plus) - selector_zero(minus)
    ideal_contrast = selector_zero(ideal[f"{prefix}_plus"]) - selector_zero(ideal[f"{prefix}_minus"])
    c_obs = output_contrast(plus, minus)
    c_ideal = output_contrast(ideal[f"{prefix}_plus"], ideal[f"{prefix}_minus"])
    decided = c_ideal != 0
    return {
        f"{prefix}_p0_minus": selector_zero(minus),
        f"{prefix}_p0_plus": selector_zero(plus),
        f"{prefix}_contrast": contrast,
        f"{prefix}_contrast_ideal": ideal_contrast,
        f"{prefix}_contrast_ratio": contrast / ideal_contrast if abs(ideal_contrast) > ZERO else float("nan"),
        f"{prefix}_sign_agreement": float(np.sum(np.sign(c_obs[decided]) == np.sign(c_ideal[decided]))),
        f"{prefix}_mean_abs_output_contrast": float(np.mean(np.abs(c_obs[decided]))) if decided.any() else float("nan"),
        f"{prefix}_half_sum_output_contrast": float(c_obs.sum() / 2.0),
    }


def pathion_kernel_map_group() -> Group:
    members = kernel_map_members()
    ideal = {member.name: member.ideal for member in members}
    prefixes = sorted({member.name.rsplit("_", 1)[0] for member in members if member.name != "kmap_skeleton"})

    def summarize(dist: dict[str, np.ndarray]) -> dict[str, float]:
        summary: dict[str, float] = {}
        for prefix in prefixes:
            summary |= _pair_summary(prefix, dist, ideal)
        contrast = {operand: summary[f"kmap_{operand_tag(operand)}_contrast"] for operand in OPERANDS}
        n12 = (contrast[(1, 18, 1)] + contrast[(1, 24, 1)]) / 2.0
        n4 = (contrast[(1, 26, 1)] + contrast[(2, 27, 1)]) / 2.0
        summary["nullity_ratio_12_over_4"] = n12 / n4 if n4 else float("nan")
        summary["nullity_ratio_8_over_4"] = contrast[(1, 10, 1)] / n4 if n4 else float("nan")
        summary["strut9_ratio_e1e24_over_e2e27"] = (
            contrast[(1, 24, 1)] / contrast[(2, 27, 1)] if contrast[(2, 27, 1)] else float("nan")
        )
        for twin, primary in TWINS:
            summary[f"twin_difference_{operand_tag(twin)}"] = (
                summary[f"kmap_twin_{operand_tag(twin)}_contrast"] - summary[f"kmap_{operand_tag(primary)}_contrast"]
            )
        summary["skeleton_p0"] = selector_zero(dist["kmap_skeleton"])
        return summary

    return Group("pathion_kernel_map", members, summarize)


if __name__ == "__main__":
    for operand in (*OPERANDS, *(twin for twin, _ in TWINS)):
        n = nullity(operand)
        if aligned_pairs(operand) != n:
            raise SystemExit(f"{operand_tag(operand)}: aligned pairs differ from the nullity {n}")
        minus = ideal_law(kernel_map_circuit(operand, False))
        plus = ideal_law(kernel_map_circuit(operand, True))
        if abs(selector_zero(minus) - (16 - n) / 32) > 1e-12 or abs(selector_zero(plus) - (16 + n) / 32) > 1e-12:
            raise SystemExit(f"{operand_tag(operand)}: selector marginals differ from (16 -+ N)/32")
        c = output_contrast(plus, minus)
        if not np.allclose(np.abs(c), 1.0) or abs(c.sum() / 2 - n) > 1e-9:
            raise SystemExit(f"{operand_tag(operand)}: output contrasts are not +-1 with half-sum N")
    group = pathion_kernel_map_group()
    ideal_summary = group.summarize({member.name: member.ideal for member in group.members})
    print(
        f"pathion kernel map: {len(group.members)} circuits on {WIDTH} qubits;",
        {
            key: round(value, 6)
            for key, value in ideal_summary.items()
            if "ratio" in key or "twin" in key or "skeleton" in key
        },
    )
