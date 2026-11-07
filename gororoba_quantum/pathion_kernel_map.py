"""Pair-resolved kernel map of two-term operands of the 32-dimensional Cayley-Dickson algebra A_5.

For the operand e_i + t e_j, write L for its left multiplication, m = i XOR j and
K = L_i^T (t L_j), a signed permutation k -> k XOR m that pairs the 32 basis
states into 16 XOR pairs {k, k XOR m}. A pair is aligned when K carries the same
sign on both members. On an aligned pair e_k - s e_(k XOR m) spans a kernel
direction of L (Gram eigenvalue 0) and e_k + s e_(k XOR m) a Gram eigenvalue 4;
on a misaligned pair both combinations sit at eigenvalue 2. The nullity of L is
the number N of aligned pairs, 0, 4, 8 or 12 for two-term operands, among the
annihilator dimensions 0, 4, 8, 12, 16 of A_5 (Biss, Dugger and Isaksen,
math/0511691, Theorem 1.2; Skiouris, Aphanics at the Pathion Level,
Proposition 2.2, gives 12 and 4 for the pairs with i < 16 < j), checked by
``nullity`` against the cd_core matrix rank.

Circuit, six qubits (algebra index bit b on qubit b, selector on qubit 5):
H on every data qubit, a diagonal orientation oracle, then the fixed-operand
linear combination of unitaries (H on the selector, Z on it for t = -1,
select_lcu.select_circuit(32, i, j), H on the selector), and a measurement of
all six qubits. The oracle is +1 on the lower member k of every pair and -s_k
(arm ``minus``) or +s_k (arm ``plus``) on the upper member, with s_k the sign K
puts on k, so the upper-member signs enter only through the compiled SELECT.
Every upper member has the highest bit h of m set and every lower member clears
it, so the plus arm is the minus arm with a phase pi on data qubit h: both arms
are one parametrized circuit and compile to the same routed gates.
The ideal selector marginals are P(s = 0) = (16 - N)/32 and (16 + N)/32, so the
selector contrast plus - minus is N/16, and the per-output contrast
c(y) = P_plus(s = 0 | y) - P_minus(s = 0 | y) is +1 at both outputs of an aligned
pair and +1 at one, -1 at the other output of a misaligned pair; half the sum of
c(y) is N. A device whose error contracts every outcome toward a fixed state
scales both contrasts by one visibility, so the ratio of selector contrasts
between operands equals the ratio of their nullities, and within one circuit the
signed mean of c(y) against the ideal signs estimates that visibility, so half
the sum of c(y) over it estimates N whatever visibility the circuit has
(``nullity_estimate``; hypothesis-level when the contraction depends on the
output bin, for instance through readout asymmetry).

Controls: the N = 0 operand (ideal contrast 0); the quarter-turn twins, operands
with disjoint support and the same Gram operator as a primary operand (Moreno,
math/0512517, Corollary 2.4: L^2 = -G is invariant under the O(2) rotation of
pure operands), which read the primary's values through a
different compiled sign network; the cocycle-free SELECT (every L_m replaced by
its unsigned XOR permutation), whose contrast departs from N/16; a single SELECT
sign flipped at one input, which moves N by one; and the selector-disconnected
skeleton, whose selector reads s = 0 with certainty.
"""

from __future__ import annotations

import functools

import flint
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.circuit.library import DiagonalGate
from qiskit.quantum_info import Statevector

import cd_core
from experiments import Group, Member
from select_lcu import joint_select_signs, select_circuit

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
# Orientation phase: 0 binds the minus arm, pi the plus arm, so both arms compile once and share routing.
ORIENTATION = Parameter("orientation")


def operand_tag(operand: tuple[int, int, int]) -> str:
    i, j, t = operand
    return f"e{i}{'p' if t > 0 else 'm'}e{j}"


def data_qubits(dim: int) -> int:
    """Number of data qubits of the map on the algebra of dimension dim, a power of two; the selector follows them.

    Every function that builds the map or its operand data takes ``dim`` as a keyword, 32 by default."""
    if dim < 2 or dim & (dim - 1):
        raise ValueError(f"dimension {dim} is not a power of two")
    return dim.bit_length() - 1


@functools.cache
def _left_matrix(dim: int, m: int) -> np.ndarray:
    matrix = np.array(cd_core.left_mult_matrix(dim, cd_core.basis(dim, m)))
    matrix.flags.writeable = False
    return matrix


def _left(m: int, dim: int = DIM) -> np.ndarray:
    return _left_matrix(dim, m)


@functools.cache
def _k_matrix(operand: tuple[int, int, int], dim: int) -> np.ndarray:
    """K = L_i^T (t L_j), the signed XOR permutation of the operand's pairs, read-only."""
    i, j, t = operand
    matrix = _left(i, dim).T @ (t * _left(j, dim))
    matrix.flags.writeable = False
    return matrix


def nullity(operand: tuple[int, int, int], *, dim: int = DIM) -> int:
    """Exact nullity of L_(e_i + t e_j) from the integer rank of its cd_core matrix (python-flint fmpz_mat)."""
    i, j, t = operand
    matrix = (_left(i, dim) + t * _left(j, dim)).astype(int).tolist()
    return dim - int(flint.fmpz_mat(matrix).rank())


def aligned_pairs(operand: tuple[int, int, int], *, dim: int = DIM) -> int:
    i, j, _ = operand
    k_matrix = _k_matrix(operand, dim)
    m = i ^ j
    return sum(1 for k in range(dim) if k < k ^ m and k_matrix[k ^ m, k] == k_matrix[k, k ^ m])


def orientation_signs(operand: tuple[int, int, int], plus: bool, *, dim: int = DIM) -> list[float]:
    i, j, _ = operand
    k_matrix = _k_matrix(operand, dim)
    m = i ^ j
    signs = [1.0] * dim
    for k in range(dim):
        if k < k ^ m:
            s_k = float(k_matrix[k ^ m, k])
            signs[k ^ m] = s_k if plus else -s_k
    return signs


def upper_bit(operand: tuple[int, int, int]) -> int:
    """The highest set bit h of m = i XOR j: the upper member of every XOR pair has bit h set and the lower clears it,
    so Z on data qubit h turns the minus orientation into the plus orientation."""
    i, j, _ = operand
    return (i ^ j).bit_length() - 1


def _select(i: int, j: int, flip_input: int | None, dim: int = DIM) -> QuantumCircuit:
    """select_lcu.select_circuit, or the same layers with the joint sign at (selector 1, data flip_input) negated
    inside its one diagonal, so the mutation adds no gate."""
    if flip_input is None:
        return select_circuit(dim, i, j)
    data = data_qubits(dim)
    signs = joint_select_signs(dim, i, j)
    signs[dim + flip_input] = -signs[dim + flip_input]
    qc = QuantumCircuit(data + 1, name=f"select_{i}_{j}_flip{flip_input}")
    qc.append(DiagonalGate(signs), range(data + 1))
    for b in range(data):
        if i >> b & 1:
            qc.x(b)
    for b in range(data):
        if (i ^ j) >> b & 1:
            qc.cx(data, b)
    return qc


def _cocycle_free_select(i: int, j: int, dim: int = DIM) -> QuantumCircuit:
    data = data_qubits(dim)
    qc = QuantumCircuit(data + 1, name=f"xor_select_{i}_{j}")
    for b in range(data):
        if i >> b & 1:
            qc.x(b)
    for b in range(data):
        if (i ^ j) >> b & 1:
            qc.cx(data, b)
    return qc


def kernel_map_template(
    operand: tuple[int, int, int],
    *,
    cocycle_free: bool = False,
    flip_input: int | None = None,
    skeleton: bool = False,
    measure: bool = True,
    dim: int = DIM,
) -> QuantumCircuit:
    """Both orientations of one operand as one circuit: the minus oracle, then P(ORIENTATION) on qubit upper_bit."""
    i, j, t = operand
    data = data_qubits(dim)
    width = data + 1
    qc = QuantumCircuit(width, width if measure else 0)
    qc.h(range(data))
    qc.append(DiagonalGate(orientation_signs(operand, False, dim=dim)), range(data))
    qc.p(ORIENTATION, upper_bit(operand))
    qc.h(data)
    if not skeleton:
        if t < 0:
            qc.z(data)
        qc.compose(
            _cocycle_free_select(i, j, dim) if cocycle_free else _select(i, j, flip_input, dim),
            range(width),
            inplace=True,
        )
    qc.h(data)
    if measure:
        qc.measure(range(width), range(width))
    return qc


def kernel_map_circuit(operand: tuple[int, int, int], plus: bool, **options: bool | int | None) -> QuantumCircuit:
    template = kernel_map_template(operand, **options)  # type: ignore[arg-type]
    return template.assign_parameters({ORIENTATION: np.pi if plus else 0.0})


def ideal_law(circuit: QuantumCircuit) -> np.ndarray:
    """Outcome law indexed y + dim s (data clbits first, selector clbit last; dim 32 has data clbits 0-4)."""
    return np.asarray(Statevector(circuit.remove_final_measurements(inplace=False)).probabilities())


def selector_zero(law: np.ndarray) -> float:
    return float(law[: law.size // 2].sum())


def output_contrast(plus_law: np.ndarray, minus_law: np.ndarray) -> np.ndarray:
    """c(y) = P_plus(s = 0 | y) - P_minus(s = 0 | y); an output with no weight in an arm reads 0."""
    half = plus_law.size // 2

    def conditional(law: np.ndarray) -> np.ndarray:
        total = law[:half] + law[half:]
        return np.divide(law[:half], total, out=np.zeros(half), where=total > 0)

    return conditional(plus_law) - conditional(minus_law)


def kernel_map_members() -> tuple[Member, ...]:
    members: list[Member] = []

    def arms(prefix: str, operand: tuple[int, int, int], **options: bool | int | None) -> None:
        template = kernel_map_template(operand, **options)  # type: ignore[arg-type]
        template.name = prefix
        for plus in (False, True):
            phase = np.pi if plus else 0.0
            name = f"{prefix}_{'plus' if plus else 'minus'}"
            ideal = ideal_law(template.assign_parameters({ORIENTATION: phase}))
            members.append(Member(name, template, ideal, {ORIENTATION: phase}))

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
    decided = np.abs(c_ideal) > ZERO
    # Signed visibility: under a contraction of both arms toward the uniform law, c_obs = V c_ideal on every bin, so
    # V_hat = V and the half-sum over V_hat returns the ideal half-sum (N for a true SELECT) whatever V the circuit has.
    visibility = float(np.mean(c_obs[decided] * np.sign(c_ideal[decided]))) if decided.any() else float("nan")
    half_sum = float(c_obs.sum() / 2.0)
    return {
        f"{prefix}_p0_minus": selector_zero(minus),
        f"{prefix}_p0_plus": selector_zero(plus),
        f"{prefix}_contrast": contrast,
        f"{prefix}_contrast_ideal": ideal_contrast,
        f"{prefix}_contrast_ratio": contrast / ideal_contrast if abs(ideal_contrast) > ZERO else float("nan"),
        f"{prefix}_sign_agreement": float(np.sum(np.sign(c_obs[decided]) == np.sign(c_ideal[decided]))),
        f"{prefix}_mean_abs_output_contrast": float(np.mean(np.abs(c_obs[decided]))) if decided.any() else float("nan"),
        f"{prefix}_half_sum_output_contrast": half_sum,
        f"{prefix}_visibility": visibility,
        f"{prefix}_nullity_estimate": half_sum / visibility if abs(visibility) > ZERO else float("nan"),
        f"{prefix}_nullity_ideal": float(c_ideal.sum() / 2.0),
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
            summary[f"twin_nullity_difference_{operand_tag(twin)}"] = (
                summary[f"kmap_twin_{operand_tag(twin)}_nullity_estimate"]
                - summary[f"kmap_{operand_tag(primary)}_nullity_estimate"]
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
